import logging
from django.shortcuts import get_object_or_404
from rest_framework.status import HTTP_200_OK, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_400_BAD_REQUEST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from buyer_data.models import Buyer
from buyer_data.serializer import BuyerSerializer
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
    Retrieve serialized data for a buyer identified by username.
    
    Parameters:
        buyer_username (str): The username of the buyer whose data is requested.
    
    Returns:
        Response: A REST framework response containing the serialized buyer data, or a 404 error if not found.
    """
    return Response(BuyerSerializer(get_object_or_404(Buyer, user__username=buyer_username)).data, status=HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def eligibility_calculator(r):
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
    try:
        tenure = loan_math.get_query_params(r, 'n', int) * 12
        interest_rate = loan_math.get_query_params(r, 'r') / 1200
        affordable_emi = loan_math.get_query_params(r, 'inc') - loan_math.get_query_params(r, 'exp') - loan_math.get_query_params(r, 'd') - loan_math.get_query_params(r, 's')
        if affordable_emi <= 0: return Response({'error': 'DTI limit exceeded.'}, status=HTTP_422_UNPROCESSABLE_ENTITY)
        if interest_rate == 0: return Response({'max loan': round((affordable_emi * tenure), 2)}, status=HTTP_200_OK)
        max_loan = loan_math.calculate_max_loan(affordable_emi, interest_rate, tenure)
        return Response({'max_loan': round(max_loan, 2)}, status=HTTP_200_OK)
    except (TypeError, AttributeError, ValueError): return Response({'error': 'Invalid input. Check query parameters.'}, status=HTTP_400_BAD_REQUEST)
