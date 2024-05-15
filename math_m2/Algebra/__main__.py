#
# 
#


def main_factors() -> None:
    # Declaring variables ---------------------------------
    from divisors import GetPrimeFactors, StrPow
    # Functioning -----------------------------------------
    from pathlib import Path
    import sys
    projRoot = Path(__file__).resolve().parent.parent.parent
    sys.path.append(str(projRoot))
    # Getting the number....
    while True:
        try:
            n = int(input('Prime factors of (ctrl+C to exit): '))
        except ValueError:
            print('Invalid input')
            continue
        except KeyboardInterrupt:
            break
        # Getting divisors...
        divisors = GetPrimeFactors(n)
        # Outputting...
        text = ' X '.join(
            StrPow(base, power)
            for base, power in divisors.items())
        print(text)


def main() -> None:
    while True:
        try:
            print('1. Decomposition to prime factors')
            try:
                n = int(input('Select which one to run (ctrl+C to exit): '))
            except ValueError:
                print('Invalid input.')
                continue
            match n:
                case 1:
                    main_factors()
                case _:
                    print('Invalid number')
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    main()
