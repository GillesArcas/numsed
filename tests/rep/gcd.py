# greatest common divisor
def gcd(a, b): 
    c = 1
    while c != 0:
        c = a % b
        if c == 0:
            return b
        else:
            a = b
            b = c

a = 8136
b = 492
print(gcd(a, b))
