# Project Euler #6: Sum square difference

n = 1
s = 0
s2 = 0
while n <= 100:
    s += n
    s2 += n * n
    n += 1
print(s * s - s2)
