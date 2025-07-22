from math import pow

def get_query_params(request, key, type_cast=float, required=True):
    value = request.query_params.get(key)
    if required and value is None: raise ValueError(f"Missing required query parameter: {key}")
    try: return type_cast(value)
    except (TypeError, ValueError): raise ValueError(f"Invalid value for '{key}': Expected {type_cast.__name__}")

def calculate_interest_power(rate, tenure_months):
    if rate == 0: return 1
    return pow(1 + rate, tenure_months)
