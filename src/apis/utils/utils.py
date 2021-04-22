def has_any_uppercase_character(s):
    return any(x.isupper() for x in s)


def add_update_fields_to_save_kwargs(save_kwargs: dict, fields: list):
    update_fields = save_kwargs.get("update_fields", [])
    if update_fields:
        update_fields.extend(fields)
        # remove duplicates fields and set again
        save_kwargs["update_fields"] = list(set(update_fields))
    return save_kwargs


def bytes_to_mb(bytes_):
    return float(bytes_) / (1024 * 1024)