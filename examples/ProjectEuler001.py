# Project Euler #1: Multiples of 3 and 5

s = 0
n = 3
while n < 1000:
    if n % 3 == 0 or n % 5 == 0:
        s += n
    n += 1
print(s)
