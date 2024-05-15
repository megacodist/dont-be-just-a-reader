#
# 
#


from typing import Generator


def GetPrimeNums(n: int) -> Generator[int, None, None]:
    """Yields all prime numbers less than or equal to `n`.

    #### Exceptions:
    * `TypeError`: the argument is not a whole number.
    * `ValueError`: the number is not greater than one.
    """
    # Checking the argument...
    badType = False
    try:
        n_ = int(n)
    except TypeError:
        badType = True
    else:
        if n != n_:
            badType = True
    if badType:
        raise TypeError('a whole number is required for computing prime '
            f'numbers not a {n.__class__.__qualname__}')
    if n_ <= 1:
        raise ValueError('for computing prime numbers an integer greater '
            f'than one is required not {n_}')
    # Computing primes...
    import math
    primes = [2,]
    yield 2
    if n_ >= 3:
        primes.append(3)
        yield 3
    if n_ <= 4:
        return
    m = 5
    while m <= n_:
        sqrt = math.isqrt(m)
        isPrime = True
        for p in primes:
            if p > sqrt:
                break
            if m % p == 0:
                isPrime = False
                break
        if isPrime:
            primes.append(m)
            yield m
        m += 1


def main() -> None:
    import math
    from math_m2.Algebra.prime_nums import GetPrimeNums
    while True:
        try:
            n = int(input('Prime numbers up to (ctrl+C to exit): '))
        except ValueError:
            print('Invalid input')
            continue
        except KeyboardInterrupt:
            return
        try:
            primes = list(GetPrimeNums(n))
            nPrimes = len(primes)
            nDigits = math.floor(math.log10(nPrimes) + 1)
            for idx in range(nPrimes):
                print(f'{(idx + 1):>{nDigits}}: {primes[idx]}')
        except KeyboardInterrupt:
            return


if __name__ == '__main__':
    main()
