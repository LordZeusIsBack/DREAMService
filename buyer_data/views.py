import logging
from django.shortcuts import get_object_or_404
from rest_framework.status import HTTP_200_OK, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_400_BAD_REQUEST
from rest_framework.decorators import api_view, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from buyer_data.models import Buyer
from buyer_data.serializer import BuyerSerializer
from rest_framework.response import Response
from common.views import create_user_views
from common.models import CustomUser
from math import pow, log

logger = logging.getLogger('buyer_data')

def calculate_interest_power(r, n):
    return pow(1 + r, n)

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
@parser_classes([IsAuthenticated])
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
@parser_classes([AllowAny])
def eligibility_calculator(r):
    try:
        dp = float(r.query_params.get('dp')) # Down-Payment
        p = float(r.query_params.get('r')) / (12 * 100) # Interest Rate
        n = int(r.query_params.get('n')) * 12 # Tenure
        inc = float(r.query_params.get('inc')) # Income
        d = float(r.query_params.get('d')) #Existing Debt
        emi = (inc / 2) - d
        if emi <= 0: return Response({'message': 'DTI limit exceeded.'}, status=HTTP_422_UNPROCESSABLE_ENTITY)
        if p == 0: L = emi * n
        else:
            r_power_n = calculate_interest_power(p, n)
            L = emi * ((r_power_n - 1) / (p * r_power_n))
        return Response({'L': round(L, 2), 'C': round((L + dp), 2)}, status=HTTP_200_OK) # L: Maximum Loan Amount, C: Maximum Cost of Property
    except (TypeError, AttributeError, ValueError): return Response({'error': 'Invalid input. Check query parameters.'}, status=HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@parser_classes([AllowAny])
def emi_calculator(request):
    try:
        P = float(request.GET.get('P')) # Principal Loan Amount
        r = float(request.GET.get('r')) # Interest Rate
        n = int(request.GET.get('n')) # Tenure in months
        k = int(request.GET.get('k')) # Number of months for which EMI has been paid
        A = float(request.GET.get('A')) # Prepayment Amount
        emi = request.GET.get('emi') # EMI Amount, optional
        if emi: EMI = float(emi)
        else:
            power_n = calculate_interest_power(r, n)
            EMI = (P * r * power_n) / (power_n - 1)
        power_k = calculate_interest_power(r, k)
        balance_k = (P * power_k) - (EMI * (power_k - 1) / r)
        new_principal = balance_k - A
        numerator = EMI
        denominator = EMI - (r * new_principal)
        if denominator <= 0:
            return Response({"error": "Prepayment too high, loan can be closed immediately."},
                            status=HTTP_400_BAD_REQUEST)
        tenure_ratio = numerator / denominator
        power_n_prime = log(tenure_ratio) / log(1 + r)
        new_total_tenure = round(k + power_n_prime, 2)
        months_saved = n - new_total_tenure
        return Response({
            "original_emi": round(EMI, 2),
            "outstanding_balance_after_k_emis": round(balance_k, 2),
            "new_principal_after_prepayment": round(new_principal, 2),
            "remaining_months_after_prepayment": round(power_n_prime, 2),
            "new_total_tenure": round(new_total_tenure, 2),
            "months_saved": round(months_saved, 2)
        }, status=HTTP_200_OK)
    except (TypeError, ValueError):
        return Response({"error": "Invalid or missing query parameters."}, status=HTTP_400_BAD_REQUEST)
