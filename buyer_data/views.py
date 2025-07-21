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
def affordability_calculator(r):
    try:
        down_payment = float(r.query_params.get('down_payment'))
        interest_rate = float(r.query_params.get('interest_rate')) / (12 * 100)
        tenure = int(r.query_params.get('tenure_in_years')) * 12
        remaining_capacity = (float(r.query_params.get('income')) / 2) - float(r.query_params.get('existing_debt'))
        if remaining_capacity <= 0: return Response({'message': 'You are already above the mandated DTI.'}, status=HTTP_422_UNPROCESSABLE_ENTITY)
        elif interest_rate == 0: principal_amount = remaining_capacity * tenure
        else:
            powered_rate = calculate_interest_power(interest_rate, tenure)
            principal_amount = remaining_capacity * ((powered_rate - 1) / (interest_rate * powered_rate))
        return Response({'principal_amount': round(principal_amount, 2), 'total_available_cost': round(principal_amount + down_payment, 2)}, status=HTTP_200_OK)
    except (TypeError, AttributeError): return Response({'error': 'Invalid input. Please check your query parameters.'}, status=HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@parser_classes([AllowAny])
def emi_calculator(request):
    try:
        P = float(request.GET.get('P'))
        r = float(request.GET.get('r'))
        n = int(request.GET.get('n'))
        k = int(request.GET.get('k'))
        A = float(request.GET.get('A'))
        emi = request.GET.get('emi')
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
