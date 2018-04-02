# Project Euler #10: Summation of primes

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
    
N = 1000 # 1000 rather than 2000000 for numsed testing
s = 0
n = 2
while n < N:
    if is_prime(n):
        print(n)
        s += n
    n += 1
print(s)
