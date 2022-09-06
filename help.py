from config import supported_tokens

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


def token_supported(token):
    token = token.upper()
    for item in supported_tokens.items():
        if token == item[0]:
            return supported_tokens[token]
        elif token == item[1]:
            return token
    return None