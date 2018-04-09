# Project Euler #15: Lattice paths

def fac(n):
    i = 1
    r = 1
    while i <= n:
        r *= i
        i += 1
    return r
    
def bin(a, b):
    return fac(a) // fac(b) // fac(a - b)
    
def numpaths(i, j, m, n):
    return bin(m + n, m)

print(numpaths(0, 0, 20, 20))
