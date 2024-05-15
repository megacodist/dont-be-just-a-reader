#
# 
#

def StrPow(base: int, power: int) -> str:
    from string_mega import GetSuperNum
    if power == 1:
        return str(base)
    else:
        powStr = GetSuperNum(str(power))
        return f'{base}{powStr}'


def GetPrimeFactors(n: int) -> dict[int, int]:
    """
    """
    from collections import defaultdict
    import math
    from prime_nums import GetPrimeNums
    primes = list(GetPrimeNums(math.isqrt(n)))
    divisors: dict[int, int] = defaultdict(lambda: 0)
    for prime in primes:
        while True:
            quotient, remainder = divmod(n, prime)
            if remainder == 0:
                divisors[prime] += 1
                n = quotient
            else:
                break
        if n == 1:
            break
    if n > 1:
        divisors[n] += 1
    return divisors
