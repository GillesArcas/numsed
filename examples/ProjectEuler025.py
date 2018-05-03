# Project Euler #25: 1000-digit Fibonacci number

m = 1
n = 1
i = 2
num = 1000 # project euler
num = 100  # numsed testing
lim = 10 ** (num - 1)
while n < lim:
    m, n = n, m + n
    i += 1
    print(i, n)
