# Project Euler #14: Longest Collatz sequence


def nb_iter(n):
    k = 0
    while n != 1:
        if n % 2 == 0:
            n = n // 2
        else:
            n = n * 3 + 1
        k += 1
    return k


a = 1000000 # project euler
a = 100     # numsed testing
n = 1
max = 0

while n < a:
    k = nb_iter(n)
    if k > max:
        print(n)
        print(k)
        max = k
    n += 1
