# Project Euler #9: Special Pythagorean triplet

def find():
    a = 1   # euler prject
    a = 350 # numsed testing
    while a <= 998:
        print(a)
        b = 1
        while b <= a:
            c = 1000 - a - b
            if a * a + b * b == c * c:
                print(a, b, c, 'sum:', a + b + c, 'sqr1:', a * a + b * b, 'sqr2:', c * c, 'product:', a * b * c)
                return
            b += 1
        a += 1

find()
