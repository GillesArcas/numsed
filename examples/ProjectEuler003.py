# Project Euler #3: Largest prime factor

def largest_prime_factor(n):
    # https://en.wikipedia.org/wiki/Trial_division
    while n % 2 == 0:
        print(2)
        n //= 2
    f = 3
    while n > 1:
        if n % f == 0:
            print(f)
            n //= f
        else:
            f += 2
    return f


n = 600851475143
p = largest_prime_factor(n)
print(p)