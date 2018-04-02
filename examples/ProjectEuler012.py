# Project Euler #12: Highly divisible triangular number


def number_of_divisors1(n):
    nd = 2 # 1 and n are divisors
    i = 2
    while i * 2 <= n:
        if n % i == 0:
            nd += 1
        i += 1
    return nd
    

def number_of_divisors(n):
    nd = 2 # 1 and n are divisors
    i = 2
    i2 = i * i
    while i2 <= n:
        if n % i == 0:
            nd += 2
        if i2 == n:
            nd -= 1
        i += 1
        i2 = i * i
    return nd
    

def search1(nb_divisors):
    i = 1
    n = 1
    nd = 1
    ndmax = 1
    while 1:
        nd = number_of_divisors(n)
        if nd > ndmax:
            ndmax = nd
            print(i)
            print(n)
            print(nd)
        if nd > 500:
            break
        i += 1
        n += i
        
        
def search(nb_divisors):
    n1 = 1
    n = 2
    n2 = n // 2
    t = n1 * n2
    nd1 = 1
    nd2 = 1
    nd = nd1 * nd2
    ndmax = nd
    while nd <= nb_divisors:
        n1 = n2
        n += 1
        n2 = n // 2 if n % 2 == 0 else n
        t = n1 * n2
        nd1 = nd2
        nd2 = number_of_divisors(n2)
        nd = nd1 * nd2
        if nd > ndmax:
            print(t)
            print(nd)
            ndmax = nd
            
search(100) # 100 rather than 500 for numsed testing        
