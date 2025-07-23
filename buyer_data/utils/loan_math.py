from math import pow, log

def get_query_params(request, key, type_cast=float, required=True):
    """
    Extracts and type-casts a query parameter from a request object.
    
    Raises:
        ValueError: If the required parameter is missing or cannot be cast to the specified type.
    """
    value = request.query_params.get(key)
    if required and value is None: raise ValueError(f'Missing required query parameter: {key}')
    try: return type_cast(value)
    except (TypeError, ValueError): raise ValueError(f"Invalid value for '{key}': Expected {type_cast.__name__}")

def calculate_interest_power(rate, tenure_months):
    """
    Compute (1 + rate) raised to the power of tenure_months.
    
    Parameters:
        rate (float): The periodic interest rate.
        tenure_months (int): The number of periods (months).
    
    Returns:
        float: The computed power value.
    
    Raises:
        ValueError: If tenure_months is less than or equal to zero.
    """
    if tenure_months <= 0: raise ValueError(f'Invalid tenure months: {tenure_months}')
    if rate == 0: return 1
    return pow(1 + rate, tenure_months)

def calculate_emi(principal, rate, tenure_months):
    """
    Calculate the Equated Monthly Installment (EMI) for a loan based on principal, monthly interest rate, and tenure.
    
    Parameters:
        principal (float): The loan amount.
        rate (float): The monthly interest rate as a decimal (e.g., 0.01 for 1%).
        tenure_months (int): The loan tenure in months.
    
    Returns:
        float: The calculated EMI amount.
    
    Raises:
        ValueError: If principal is negative, tenure_months is not positive, or rate is not between 0 and 1.
    """
    if principal < 0: raise ValueError('Principle must be positive.')
    if tenure_months <= 0: raise ValueError('Tenure months must be positive')
    if rate < 0 or rate > 1: raise ValueError('Rate must be between 0 and 1')
    if rate == 0: return principal / tenure_months
    power_n = calculate_interest_power(rate, tenure_months)
    return (principal * rate * power_n) / (power_n - 1)

def calculate_max_loan(emi, rate, tenure_months):
    """
    Calculate the maximum loan principal that can be serviced for a given EMI, interest rate, and tenure.
    
    If the interest rate is zero, returns the product of EMI and tenure in months. Otherwise, uses the standard loan formula to compute the principal based on the provided EMI, monthly interest rate, and tenure.
     
    Parameters:
        emi (float): The fixed monthly payment amount.
        rate (float): The monthly interest rate as a decimal (e.g., 0.01 for 1%).
        tenure_months (int): The total number of monthly payments.
    
    Returns:
        float: The maximum principal amount that can be borrowed.
    """
    if rate == 0: return emi * tenure_months
    power_n = calculate_interest_power(rate, tenure_months)
    return emi * (power_n - 1) / (rate * power_n)

def calculate_outstanding_balance(principal, rate, emi, months_paid):
    """
    Calculate the outstanding loan balance after a specified number of EMI payments.
    
    Parameters:
        principal (float): The original loan amount.
        rate (float): The monthly interest rate as a decimal (e.g., 0.01 for 1%).
        emi (float): The fixed monthly payment amount.
        months_paid (int): The number of monthly payments made.
    
    Returns:
        float: The remaining loan balance after the given number of payments.
    """
    if rate == 0: return principal - (emi * months_paid)
    power_k = calculate_interest_power(rate, months_paid)
    return (principal * power_k) - (emi * (power_k - 1) / rate)

def calculate_new_tenure_after_prepayment(principal, rate, tenure_months, months_paid, prepayment_amount, emi):
    """
    Calculate the new outstanding balance, principal, tenure, and months saved after making a prepayment on a loan.
    
    Handles both zero and non-zero interest rate scenarios. If the prepayment fully repays the loan, returns zeros for all outputs. Raises a ValueError if the EMI is insufficient to cover the interest on the new principal.
    
    Parameters:
        principal (float): The original loan amount.
        rate (float): The monthly interest rate (as a decimal).
        tenure_months (int): The original loan tenure in months.
        months_paid (int): The number of months for which EMI has already been paid.
        prepayment_amount (float): The lump sum amount paid towards the principal.
        emi (float): The fixed monthly EMI amount.
    
    Returns:
        balance_k (float): Outstanding balance before prepayment.
        new_principal (float): Principal remaining after prepayment.
        new_tenure_months (float): New tenure required to repay the remaining principal at the same EMI (rounded to 2 decimals for non-zero rate).
        months_saved (float): Number of months saved compared to the original tenure.
    """
    if rate == 0:
        balance_k = principal - (emi * months_paid)
        new_principal = balance_k - prepayment_amount
        if new_principal <= 0: return 0, 0, 0, 0
        remaining_months = new_principal / emi
        months_saved = tenure_months - months_paid - remaining_months
        return balance_k, new_principal, remaining_months, months_saved
    balance_k = calculate_outstanding_balance(principal, rate, emi, months_paid)
    new_principal = balance_k - prepayment_amount
    if new_principal <= 0: return 0, 0, 0, 0
    numerator = emi
    denominator = emi - (rate * new_principal)
    if denominator <= 0: raise ValueError('EMI too low for the remaining principal and interest rate')
    tenure_ratio = numerator / denominator
    power_n_prime = log(tenure_ratio) / log(1 + rate)
    new_total_tenure = round(months_paid + power_n_prime, 2)
    month_saved = tenure_months - new_total_tenure
    return balance_k, new_principal, power_n_prime, month_saved
