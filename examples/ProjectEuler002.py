# Project Euler #2: Even Fibonacci numbers

m = 1
n = 2
s = 0
while n < 4000000:
    print(n)
    if n % 2 == 0:
        s += n
    x = m
    m = n
    n = x + m
print(s)
