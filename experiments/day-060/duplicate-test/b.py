def check_email_format(address: str) -> bool:
    if "@" not in address:
        return False
    local, _, domain = address.partition("@")
    return bool(local) and "." in domain
