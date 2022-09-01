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

