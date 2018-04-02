# Project Euler #5: Smallest multiple

def gcd(a, b):
    while b != 0:
        r = a % b
        a = b
        b = r
    return a

def lcm(a, b):
    return a * b // gcd(a, b)

n = 2
d = 1
while n <= 20:
    d = lcm(n, d)
    print(d)
    n += 1
print(d)
 