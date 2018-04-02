# Project Euler #7: nth prime

def is_prime(n):
    # https://en.wikipedia.org/wiki/Primality_test
    if n <= 1:
        return 0
    elif n <= 3:
       return 1
    elif n % 2 == 0 or n % 3 == 0:
        return 0
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return 0
        i += 6
    return 1
    
N = 101 # search 101st with sed rather than 10001st
n = 0
i = 2
while n < N:
    if is_prime(i):
        print(i)
        n += 1
    i += 1
