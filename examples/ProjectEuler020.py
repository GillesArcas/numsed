# Project Euler #20: Factorial digit sum

def fac(n):
    i = 1
    r = 1
    while i <= n:
        r *= i
        i += 1
    return r
    

n = fac(100)
s = 0
while n:
    d = n % 10
    n //= 10
    s += d
    
print(s)
