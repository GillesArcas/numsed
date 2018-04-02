# Project Euler #9: Special Pythagorean triplet

def find():
    a = 300 # start at 300 for numsed testing rather than 1
    while a <= 998:
        print(a)
        b = 1
        while b <= a:
            c = 1000 - a - b
            if a * a + b * b == c * c:
                print(a)
                print(b)
                print(c)
                print(a + b + c)
                print(a * a + b * b)
                print(c * c)
                print(a * b * c)
                return
            b += 1
        a += 1

find()
