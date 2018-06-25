# Project Euler #24: Lexicographic permutations


# https://www.quora.com/How-would-you-explain-an-algorithm-that-generates-permutations-using-lexicographic-ordering
# https://www.geeksforgeeks.org/lexicographic-permutations-of-string/


def reverse(n, i):
    # Reverse digits in n from index i to index 0 (least significant).
    k1 = i
    k2 = 0
    while k1 > k2:
        n = swap(n, k1, k2)
        k1 -= 1
        k2 += 1
    return n


def swap(n, i, j):
    di = get_digit(n, i)
    dj = get_digit(n, j)
    n = set_digit(n, i, dj)
    n = set_digit(n, j, di)
    return n


def get_digit(n, i):
    return (n // (10 ** i)) % 10


def set_digit(n, i, d):
    pow10i = (10 ** i)
    pow10ip1 = pow10i * 10
    return (n // pow10ip1) * pow10ip1 + d * pow10i + n % pow10i


def findfirst(n, len):
    # Find the rightmost digit which is smaller than its next digit
    # xxxx67xxxx
    d0 = get_digit(n, 0)
    i = 1
    while i < len:
        di = get_digit(n, i)
        if di < d0:
            return i
        d0 = di
        i += 1
    # not found
    return 0


def findsecond(n, i):
    # Find the smallest digit bigger than i-th digit at the right of i.
    di = get_digit(n, i)
    djmin = 10
    j = i - 1
    while 1:
        dj = get_digit(n, j)
        if dj > di and dj < djmin:
            djmin = dj
            jmin = j
        if j == 0:
            # finished
            break
        else:
            j -= 1
    return jmin


def nextperm(n, len):
    i = findfirst(n, len)
    if i == 0:
        return 0
    j = findsecond(n, i)
    n = swap(n, i, j)
    n = reverse(n, i - 1)
    return n


def nthperm(first, len, nth):
    i = 1
    n = first
    while i != nth:
        i += 1
        n = nextperm(n, len)
        print(i, n)


n = 1000000  # project euler
n = 100      # numsed testing
nthperm(123456789, 10, n)
