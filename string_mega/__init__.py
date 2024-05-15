#
# 
#

_SUPER: dict[str, str] = {
    '0': '\u2070',
    '1': '\u00b9',
    '2': '\u00b2',
    '3': '\u00b3',
    '4': '\u2074',
    '5': '\u2075',
    '6': '\u2076',
    '7': '\u2077',
    '8': '\u2078',
    '9': '\u2079',}
"""A mapping from unicode character of regular decimal digits to
unicode character of their superscript representations.
"""


def GetSuperNum(num: str) -> str:
    """This function receives a string of a decimal number and
    returns the superscript representation of the number.
    """
    table = num.maketrans(_SUPER)
    return num.translate(table)


def main() -> None:
    while True:
        n = input('Enter a number: ')
        table = n.maketrans(_SUPER)
        m = n.translate(table)
        print(f'{n}{m}')


if __name__ == '__main__':
    main()