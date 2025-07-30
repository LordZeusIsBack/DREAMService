import logging
from django.shortcuts import get_object_or_404
from rest_framework.status import HTTP_200_OK, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, \
    HTTP_201_CREATED
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from buyer_data.models import Buyer, WishlistItem
from estate_data.models import Estate
from buyer_data.serializer import BuyerSerializer, WishlistItemSerializer
from rest_framework.response import Response
from common.views import create_user_views
from common.models import CustomUser
from .utils import loan_math

logger = logging.getLogger('buyer_data')

# Create your views here.
buyer_views = create_user_views(CustomUser, BuyerSerializer, 'buyer')

delete_buyer = buyer_views['delete_user']
update_buyer_data = buyer_views['update_user']
add_buyer = buyer_views['add_user']
buyer_forgot_password = buyer_views['forgot_password']
buyer_reset_password = buyer_views['reset_password']
buyer_login = buyer_views['login']
buyer_logout = buyer_views['logout']
buyer_verify_email = buyer_views['verify']
buyer_resend_otp = buyer_views['resend_otp']

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def buyer_data(r, buyer_username):
    """
    Retrieve buyer details for a given username.
    
    Returns:
        Response: Serialized buyer data with HTTP 200 if found, or 404 if the buyer does not exist.
    """
    return Response(BuyerSerializer(get_object_or_404(Buyer, user__username=buyer_username)).data, status=HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bookmarked_estates(r, buyer_username):
    """
    Retrieve all wishlist items for a buyer, including related estate details.
    
    Returns:
        Response: A serialized list of the buyer's wishlist items with HTTP 200 status.
    """
    return Response(WishlistItemSerializer(WishlistItem.objects.filter(buyer=get_object_or_404(Buyer, user__username=buyer_username)).select_related('estate'), many=True).data, status=HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def eligibility_calculator(r):
    """
    Calculates the maximum eligible loan amount and property cost based on down payment, annual interest rate, tenure, monthly income, and existing debt.
    
    Accepts query parameters: down payment (`dp`), annual interest rate (`r`), tenure in years (`n`), monthly income (`inc`), and existing debt (`d`). Returns a JSON response with the maximum loan amount (`L`) and property cost (`C`), both rounded to two decimals. Returns HTTP 422 if the calculated EMI is non-positive, indicating the debt-to-income limit is exceeded. Returns HTTP 400 for invalid or missing parameters.
    """
    try:
        dp = loan_math.get_query_params(r, 'dp') # Down-Payment
        rate = loan_math.get_query_params(r, 'r') / 1200 # Interest Rate
        n = loan_math.get_query_params(r, 'n', int) * 12 # Tenure
        inc = loan_math.get_query_params(r, 'inc') # Income
        d = loan_math.get_query_params(r, 'd') #Existing Debt
        emi = (inc / 2) - d
        if emi <= 0: return Response({'message': 'DTI limit exceeded.'}, status=HTTP_422_UNPROCESSABLE_ENTITY)
        loan_amount = loan_math.calculate_max_loan(emi, rate, n)
        return Response({'L': round(loan_amount, 2), 'C': round((loan_amount + dp), 2)}, status=HTTP_200_OK) # L: Maximum Loan Amount, C: Maximum Cost of Property
    except (TypeError, AttributeError, ValueError): return Response({'error': 'Invalid input. Check query parameters.'}, status=HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def emi_calculator(r):
    """
    Calculates the EMI for a loan and provides detailed amortization information, including the impact of prepayment if specified.
    
    Accepts query parameters for principal amount (`P`), annual interest rate (`r`), tenure in months (`n`), optional months paid (`k`), optional prepayment amount (`A`), and optional EMI override (`emi`).  
    If only principal, rate, and tenure are provided, returns the calculated EMI.  
    If both `k` and `A` are provided, returns outstanding balance after `k` EMIs, new principal after prepayment, remaining months, new total tenure, and months saved due to prepayment.  
    Returns an error if required parameters are missing or if prepayment is excessive.
    """
    try:
        principal = loan_math.get_query_params(r, 'P') # Principal Loan Amount
        rate = loan_math.get_query_params(r, 'r') / 1200 # Interest Rate
        tenure = loan_math.get_query_params(r, 'n', int) # Tenure in months
        k = loan_math.get_query_params(r, 'k', int, required=False) # Number of months for which EMI has been paid, optional
        prepayment_amount = loan_math.get_query_params(r, 'A', required=False) # Prepayment Amount
        emi = loan_math.get_query_params(r, 'emi', required=False) # EMI Amount, optional
        if not emi: emi = loan_math.calculate_emi(principal, rate, tenure)
        if k is None and prepayment_amount is None: return Response({'emi': round(emi, 2)}, status=HTTP_200_OK)
        if k is None or prepayment_amount is None: return Response({'error': 'Both k (months paid) and A (prepayment) must be provided for prepayment calculation.'}, status=HTTP_400_BAD_REQUEST)
        balance_k, new_principal, power_n_prime, months_saved = loan_math.calculate_new_tenure_after_prepayment(principal, rate, tenure, k, prepayment_amount, emi)
        if months_saved == 0: return Response({'error': 'Prepayment too high, loan can be closed immediately.'}, status=HTTP_422_UNPROCESSABLE_ENTITY)
        return Response({
            'original_emi': round(emi, 2),
            'outstanding_balance_after_k_emis': round(balance_k, 2),
            'new_principal_after_prepayment': round(new_principal, 2),
            'remaining_months_after_prepayment': round(power_n_prime, 2),
            'new_total_tenure': round(k + power_n_prime, 2),
            'months_saved': round(months_saved, 2)
        }, status=HTTP_200_OK)
    except (TypeError, ValueError): return Response({'error': 'Invalid or missing query parameters.'}, status=HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def affordability_calculator(r):
    """
    Calculates the maximum loan amount a user can afford based on income, expenses, debts, savings, tenure, and interest rate.
    
    Accepts query parameters for tenure in years (`n`), annual interest rate (`r`), income (`inc`), expenses (`exp`), existing debt (`d`), and savings (`s`). Returns the maximum affordable loan amount rounded to two decimals, or an error if debt-to-income constraints are exceeded or input is invalid.
    
    Returns:
        Response: JSON with the maximum affordable loan amount and HTTP 200 status, or an error message with an appropriate HTTP status code.
    """
    try:
        tenure = loan_math.get_query_params(r, 'n', int) * 12
        interest_rate = loan_math.get_query_params(r, 'r') / 1200
        affordable_emi = loan_math.get_query_params(r, 'inc') - loan_math.get_query_params(r, 'exp') - loan_math.get_query_params(r, 'd') - loan_math.get_query_params(r, 's')
        if affordable_emi <= 0: return Response({'error': 'DTI limit exceeded.'}, status=HTTP_422_UNPROCESSABLE_ENTITY)
        if interest_rate == 0: return Response({'max loan': round((affordable_emi * tenure), 2)}, status=HTTP_200_OK)
        max_loan = loan_math.calculate_max_loan(affordable_emi, interest_rate, tenure)
        return Response({'max_loan': round(max_loan, 2)}, status=HTTP_200_OK)
    except (TypeError, AttributeError, ValueError): return Response({'error': 'Invalid input. Check query parameters.'}, status=HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_bookmarks(r, buyer_username):
    """
    Add an estate to a buyer's wishlist.
    
    Adds the specified estate to the wishlist for the given buyer if the estate exists, is available, and is not already bookmarked. Returns a success message with estate details if added, or an error if the estate is unavailable, missing, or already in the wishlist.
    """
    slug = r.data.get('slug')
    if not slug: return Response({'error': 'Estate Data has not been provided.'}, status=HTTP_400_BAD_REQUEST)
    estate = get_object_or_404(Estate, slug=slug)
    buyer = get_object_or_404(Buyer, user__username=buyer_username)
    if estate.status != 'available': return Response({'error': 'Cannot add unavailable properties to wishlist'}, status=HTTP_400_BAD_REQUEST)
    wishlist_item, created = WishlistItem.objects.get_or_create(buyer=buyer, estate=estate)
    if created: return Response({'message': 'Estate added to wishlist successfully', 'estate_name': estate.estate_name, 'estate_type': estate.estate_type, 'added_on': wishlist_item.added_on}, status=HTTP_201_CREATED)
    return Response({'error': 'Estate already in wishlist', 'estate_name': estate.estate_name}, status=HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_bookmarks(r, buyer_username):
    """
    Remove an estate from a buyer's wishlist.
    
    Deletes the specified estate from the buyer's wishlist based on the provided estate slug and buyer username.
    
    Returns:
        Response: JSON message confirming removal with estate name and buyer username, HTTP 200 on success, or HTTP 400/404 for errors.
    """
    slug = r.data.get('slug')
    if not slug: return Response({'error': 'Estate Data has not been provided.'}, status=HTTP_400_BAD_REQUEST)
    estate = get_object_or_404(Estate, slug=slug)
    buyer = get_object_or_404(Buyer, user__username=buyer_username)
    wishlist_item = get_object_or_404(WishlistItem, buyer=buyer, estate=estate)
    wishlist_item.delete()
    return Response({'message': 'Bookmark removed successfully.', 'estate_name': estate.estate_name, 'buyer': buyer_username}, status=HTTP_200_OK)
