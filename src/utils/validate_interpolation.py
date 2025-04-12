import string


def validate_interpolation(template: str, values: dict):
    """Validate that all keys in the values dict are present in the template string"""
    formatter = string.Formatter()
    template_keys = {
        field_name for _, field_name, _, _ in formatter.parse(template) if field_name
    }

    dict_keys = set(values.keys())

    missing_in_dict = template_keys - dict_keys
    extra_in_dict = dict_keys - template_keys

    if missing_in_dict or extra_in_dict:
        msg = []
        if missing_in_dict:
            msg.append(f"Missing keys in dict: {sorted(missing_in_dict)}")
        if extra_in_dict:
            msg.append(f"Extra keys in dict: {sorted(extra_in_dict)}")
        raise ValueError("Strict interpolation mismatch:\n" + "\n".join(msg))
