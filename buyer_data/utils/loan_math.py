from math import pow

def get_query_params(request, key, type_cast=float, required=True):
    value = request.query_params.get(key)
    if required and value is None: raise ValueError(f"Missing required query parameter: {key}")
    try: return type_cast(value)
    except (TypeError, ValueError): raise ValueError(f"Invalid value for '{key}': Expected {type_cast.__name__}")

def calculate_interest_power(rate, tenure_months):
    if rate == 0: return 1
    return pow(1 + rate, tenure_months)

def calculate_emi(principal, rate, tenure_months):
    if rate == 0: return principal / tenure_months
    power_n = calculate_interest_power(rate, tenure_months)
    return (principal * rate * power_n) / (power_n - 1)

def calculate_max_loan(emi, rate, tenure_months):
    if rate == 0: return emi * tenure_months
    power_n = calculate_interest_power(rate, tenure_months)
    return emi * (power_n - 1) / (rate * power_n)
