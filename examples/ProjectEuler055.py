# Project Euler #55: Lychrel numbers

def palindrome(n):
    p = 0
    while n > 0:
        r = n % 10
        n = n // 10
        p = p * 10 + r
    return p
    
def find_palindrome(n):
    k = 0
    p = palindrome(n)
    while k < 50:
        k += 1
        n = n + p
        p = palindrome(n)
        if n == p:
            print(n)
            return k
    else:
        print(n)
        return -1
        
k = 1
n = 0
while k < 1000: # 1000 for sed rather than original 10000
    print(k)
    r = find_palindrome(k)
    if r == -1:
        print(r)
        n += 1
    else:
        print(r)
    k += 1
print(n)
