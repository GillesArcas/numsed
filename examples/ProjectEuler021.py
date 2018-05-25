# Project Euler #21: Amicable numbers


def sum_of_divisors(n):
    sd = 1  # 1 is a divisors1
    i = 2
    i2 = i * i
    while i2 <= n:
        if n % i == 0:
            sd += i + n // i
        if i2 == n:
            sd -= i
        i += 1
        i2 = i * i
    return sd
    

print(sum_of_divisors(220))
print(sum_of_divisors(284))


def main():
    N = 10000  # project euler
    N = 300    # numsed testing
    i = 2
    s = 0
    while i <= N:
        j = sum_of_divisors(i)
        if j < i:
            pass
        elif j == i:
            pass
        else:
            k = sum_of_divisors(j)
            if i == k:
                s += i + j
        i += 1
    print(s)
    
    
main()