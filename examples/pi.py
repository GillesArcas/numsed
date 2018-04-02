# Compute pi with a Ramanujan serie ------------------------------------------ 
#                                                                            
# pi = SIGMA n from 0 of [Bin(2n,n) (42n + 5) / 2^(12n + 4)]                 
# with Bin(a,b) binomial coefficients                                       
#                                                                            
# ---------------------------------------------------------------------------- 

# X is Bin(2N,N)
# Y is 42N + 5
# Z is 2^(12N + 4)
# P is numerator of sum
# Q is denominator of sum
# S is scale factor

n = 0
x = 1
y = 5
z = 16
p = x ** 3 * y
q = z
s = 10000000000000000000

while n < 10:
    n = n + 1
    print(n)

    x = x * (4 * n - 2) // n
    y = y + 42
    z = z * 4096
    p = p * z + q * x ** 3 * y
    q = q * z
   
pi = (q * s) // p

print(pi)
