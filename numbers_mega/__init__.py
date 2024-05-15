#
# 
#


from typing import Any


def AssertInt(val: Any) -> None:
    """Asserts that the argument is an integer or a numeric whole number,
    otherwise it raises a `TypeError`.
    """
    badType = False
    try:
        n = int(val)
    except TypeError:
        badType = True
    if n != val:
        badType = True
    if badType:
        raise TypeError(f"'{val}' is not an integer or a whole number.")
