import constants

def price_crossed(old, new, target):
    if (old <= target <= new) or (new <= target < old):
        return True
    else:
        return False


def price_increased(old, new):
    if new > old: 
        return True
    else:
        return False


def format_token(token):
    token = token.upper()
    for key, value in supported_tokens.items():
        if token == key:
            return supported_tokens[token]
        elif token == value:
            return token
    return None