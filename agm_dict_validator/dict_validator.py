def validate_dict(original_dict: dict, scheme: dict) -> (dict, dict, bool):
    """
    Validate and slice (get part of, optional) original dict by scheme.
    Also, it can return dict with converted values of keys of original dict.

    :param original_dict:
        Dictionary that needs to be validated.
    :param scheme:
        Dictionary with an established schema:
        {
            'key_name_1': (is_necessary_1, value_type_1, conversion_1),
            'key_name_2': (is_necessary_2, value_type_2, conversion_2),
            ...
            'key_name_N': (is_necessary_N, value_type_N, conversion_N)
        }, where:
            [str] key_name_*              - name of key in original dict,  # TODO: add support for other types
            [bool] is_necessary_*         - if set to True and key_name_* is not in original dict,
                                            add this key to errors['converting_errors_keys'],
                                            else ignore key
            [any, type] value_type_*     - expected type of value in original dict,
                                            if type of value in original dict is not as in scheme
                                            and conversion_8 is set to False,
                                            add key of value to errors['value_type_errors_keys'],
                                            else try to convert
            [bool] conversion_*           - if set to True and type of value is not as in scheme,
                                            func will try to convert value to type in scheme,
                                            else add key of value to errors['converting_errors_keys']
        Example:
        {
            'customer_name': (str, True),
            'amount': (str, True),
            'days': (int, True),
        }
        If 'need_to_convert' parameter is set to True, func returns dict with converted values.
    :return:
        [dict] result_dict  - validated, sliced with [if conversion=True] converted values
        [dict] errors       - dict, contains 3 types of errors:
            Example:
                errors = {
                    'missing_keys': ['key_1', 'key_4'],
                    'value_type_errors_keys': ['key_7', 'key_5'],
                    'converting_errors_keys': ['key_6', 'key_11']
                }
        [bool] has_errors   - True if any errors, else False
    """

    result_dict = {}
    errors = {
        'missing_keys': [],
        'value_type_errors_keys': [],
        'converting_errors_keys': []
    }

    # Check types of original_dict and scheme
    if type(original_dict) is not dict:
        raise TypeError(f"'original_dict' must be {dict}, not {type(original_dict)}.")
    if type(scheme) is not dict:
        raise TypeError(f"'scheme' must be {dict}, not {type(scheme)}.")

    for scheme_key, value_rules in scheme.items():
        if not isinstance(scheme_key, str):
            raise TypeError(f"'scheme_key' parameter type must be {str}, not {type(scheme_key)}.")
        if not isinstance(value_rules, tuple):
            raise TypeError(f"Value rules must be {tuple}, not {type(value_rules)}.")
        if len(value_rules) != 3:
            raise SyntaxError(f"Value rules must have only 2 arguments, not {len(value_rules)}.")
        is_key_necessary = value_rules[0]
        scheme_value_type = value_rules[1]
        conversion = value_rules[2]
        if not isinstance(is_key_necessary, bool):
            raise TypeError(f"'is_necessary' parameter type must be {bool}, not {type(is_key_necessary)}.")
        if not isinstance(scheme_value_type, type):  # If scheme_value_type is instance of class (not class)
            raise TypeError(f"'value_type' parameter type must be {type}, not instance of {type(scheme_value_type)}.")
        if not isinstance(conversion, bool):
            raise TypeError(f"'conversion' parameter type must be {bool}, not {type(conversion)}.")

        # Check if key exists in original dict
        if scheme_key not in original_dict.keys() and is_key_necessary:
            errors['missing_keys'].append(scheme_key)
            continue

        # Check if value has same type as in scheme and add it to result dict
        original_dict_value = original_dict.get(scheme_key)
        if isinstance(original_dict_value, scheme_value_type):
            result_dict[scheme_key] = original_dict_value
        else:
            if conversion:
                try:
                    converted_value = scheme_value_type(original_dict_value)
                    result_dict[scheme_key] = converted_value
                except Exception:
                    errors['converting_errors_keys'].append(scheme_key)  # Can't convert value
                    errors['value_type_errors_keys'].append(scheme_key)
            else:
                errors['value_type_errors_keys'].append(scheme_key)  # Value has wrong type

    if len(errors['missing_keys'] + errors['converting_errors_keys'] + errors['value_type_errors_keys']) > 0:
        has_errors = True
    else:
        has_errors = False

    return result_dict, errors, has_errors
