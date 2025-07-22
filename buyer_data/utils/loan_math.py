def get_query_params(request, key, type_cast=float, required=True):
    value = request.query_params.get(key)
    if required and value is None: raise ValueError(f"Missing required query parameter: {key}")
    try: return type_cast(value)
    except (TypeError, ValueError): raise ValueError(f"Invalid value for '{key}': Expected {type_cast.__name__}")
