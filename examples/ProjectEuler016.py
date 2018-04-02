# Project Euler #16: Power digit sum


n = 2 ** 1000 # project euler
n = 2 ** 100  # numsed testing
s = 0

while n:
    print(n)
    s += n % 10
    n //= 10
    
print(s)