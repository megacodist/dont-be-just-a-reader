#
# 
#


superscript: dict[str, str] = {
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


def main() -> None:
    while True:
        n = input('Enter a number: ')
        table = n.maketrans(superscript)
        m = n.translate(table)
        print(f'{n}{m}')


if __name__ == '__main__':
    main()
