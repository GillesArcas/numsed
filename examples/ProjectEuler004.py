# Project Euler #4: Largest palindrome product

def palindrome(n):
    p = 0
    while n > 0:
        r = n % 10
        n = n // 10
        p = p * 10 + r
    return p

def find_largest():
    max = 850000 # make a guess to save time
    m = 999
    while m >= 100:
        n = m
        while n >= 100:
            print(m)
            print(n)
            p = m * n
            if p < max:
                break
            if p == palindrome(p):
                if p > max:
                    print(0)
                    print(m)
                    print(n)
                    print(p)
                    max = p
            n -= 1
        m -= 1
    print(max)
        
find_largest()
