from math import pow, log

def get_query_params(request, key, type_cast=float, required=True):
    value = request.query_params.get(key)
    if required and value is None: raise ValueError(f'Missing required query parameter: {key}')
    try: return type_cast(value)
    except (TypeError, ValueError): raise ValueError(f"Invalid value for '{key}': Expected {type_cast.__name__}")

def calculate_interest_power(rate, tenure_months):
    if tenure_months <= 0: raise ValueError(f'Invalid tenure months: {tenure_months}')
    if rate == 0: return 1
    return pow(1 + rate, tenure_months)

def calculate_emi(principal, rate, tenure_months):
    if principal < 0: raise ValueError('Principle must be positive.')
    if tenure_months <= 0: raise ValueError('Tenure months must be positive')
    if rate < 0 or rate > 1: raise ValueError('Rate must be between 0 and 1')
    if rate == 0: return principal / tenure_months
    power_n = calculate_interest_power(rate, tenure_months)
    return (principal * rate * power_n) / (power_n - 1)

def calculate_max_loan(emi, rate, tenure_months):
    if rate == 0: return emi * tenure_months
    power_n = calculate_interest_power(rate, tenure_months)
    return emi * (power_n - 1) / (rate * power_n)

def calculate_outstanding_balance(principal, rate, emi, months_paid):
    if rate == 0: return principal - (emi * months_paid)
    power_k = calculate_interest_power(rate, months_paid)
    return (principal * power_k) - (emi * (power_k - 1) / rate)

def calculate_new_tenure_after_prepayment(principal, rate, tenure_months, months_paid, prepayment_amount, emi):
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
    if rate == 0: raise ValueError('Cannot calculate logarithm for zero interest rate')
    power_n_prime = log(tenure_ratio) / log(1 + rate)
    new_total_tenure = round(months_paid + power_n_prime, 2)
    month_saved = tenure_months - new_total_tenure
    return balance_k, new_principal, power_n_prime, month_saved
