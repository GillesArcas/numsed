# print constant
print 42
# --
# print long int constant
print 10000000000000000000
# --
# assign constant
n = 42
print n
# --
# assign add
m = 42
n = 5
p = m + n
print p
# --
# assign sub
m = 42
n = 5
p = m - n
print p
# --
# assign mul
m = 42
n = 5
p = m * n
print p
# --
# assign div
m = 42234683543
n = 557
p = m // n
print p
# --
# assign mod
m = 42
n = 5
p = m % n
print p
# --
# assign expression
m = 42
n = 5
p = (m * n + m // n) - 3 * (m - n)
print p
# --
# augmented assign add
m = 42
n = 5
m += n
print m
# --
# augmented assign sub
m = 42
n = 5
m -= n
print m
# --
# augmented assign mul
m = 42
n = 5
m *= n
print m
# --
# augmented assign div
m = 42
n = 5
m //= n
print m
# --
# augmented assign mod
m = 42
n = 5
m %= n
print m
# --
# augmented assign expression
m = 42
n = 5
m += (m * n + m // n) - 3 * (m - n)
print m
# --
# add negative values (+-)
m = 42
n = -5
p = m + n
print p
# --
# add negative values (-+)
m = -42
n = 5
p = m + n
print p
# --
# add negative values (--)
m = -42
n = -5
p = m + n
print p
# --
# sub negative values (+-)
m = 42
n = -5
p = m - n
print p
# --
# sub negative values (-+)
m = -42
n = 5
p = m - n
print p
# --
# sub negative values (--)
m = -42
n = -5
p = m - n
print p
# --
# mul negative values (+-)
m = 42
n = -5
p = m * n
print p
# --
# mul negative values (-+)
m = -42
n = 5
p = m * n
print p
# --
# mul negative values (--)
m = -42
n = -5
p = m * n
print p
# --
# div negative values (+-)
m = 42
n = -5
p = m // n
print p
# --
# div negative values (-+)
m = -42
n = 5
p = m // n
print p
# --
# div negative values (--)
m = -42
n = -5
p = m // n
print p
# --
# mod negative values (+-)
m = 42
n = -5
p = m % n
print p
# --
# mod negative values (-+)
m = -42
n = 5
p = m % n
print p
# --
# mod negative values (--)
m = -42
n = -5
p = m % n
print p
# --
# loop
n = -10
while n <= 10:
    print n
    n += 1
# --
# loop
n = 10
while n >= -10:
    print n
    n -= 1
# --
# loop
n = -10
while n <= -5:
    print n
    n += 1
# --
# loop
n = -5
while n >= -10:
    print n
    n -= 1
# --
# if elif else
n = -10
while n <= 10:
    if n <= -5:
        print -1
    elif n >= 5:
        print +1
    else:
        print 0
    n += 1
# --
# if operator
n = -10
while n <= 10:
    print -1 if n <= -5 else +1 if n >= 5 else 0
    n += 1
# --
# double loop
m = -10
while m <= 10:
    n = -10
    while n <= m:
        print m
        print n
        n += 1
    m += 1
# --
# double loop
m = 10
while m >= -10:
    n = 10
    while n >= m:
        print m
        print n
        n -= 1
    m -= 1
# --
# break statement
n = 0
while n <= 10:
    n += 1
    if n == 8:
        break
    print n
# --
# break statement
m = -10
while m <= 10:
    n = -10
    while n <= 10:
        print m
        if m + n == 13:
            break
        n += 1
    m += 1
# --
# break statement
m = -10
while m <= 10:
    n = -10
    while n <= 10:
        print m
        n += 1
    if m + n == 13:
        break
    m += 1
# --
# continue statement
n = 0
while n <= 10:
    n += 1
    if n == 8:
        continue
    print n
# --
# continue statement
m = -10
while m <= 10:
    n = -10
    while n <= 10:
        print m
        n += 1
        if m + n == 13:
            continue
    m += 1
# --
# continue statement
m = -10
while m <= 10:
    n = -10
    while n <= 10:
        print m
        n += 1
    m += 1
    if m + n == 13:
        continue
# --
# loop on unary positive
n = -10
while n <= 10:
    p = +n
    print p
    n += 1
# --
# loop on unary negative
n = -10
while n <= 10:
    p = -n
    print p
    n += 1
# --
# loop on adding values
m = -10
while m <= 10:
    n = -10
    while n <= 10:
        p = m + n
        print p
        n += 1
    m += 1
# --
# loop on subtracting values
m = -10
while m <= 10:
    n = -10
    while n <= 10:
        p = m - n
        print p
        n += 1
    m += 1
# --
# loop on multiplying values
m = -10
while m <= 10:
    n = -10
    while n <= 10:
        p = m * n
        print p
        n += 1
    m += 1
# --
# loop on dividing values
m = -10
while m <= 10:
    n = -10
    while n <= 10:
        if n != 0:
            p = m // n
            print p
        n += 1
    m += 1
# --
# loop on modulo
m = -10
while m <= 10:
    n = -10
    while n <= 10:
        if n != 0:
            p = m % n
            print p
        n += 1
    m += 1
# --
# test all comparison operators
m = -5
while m <= 5:
    n = -5
    while n <= 5:
        print 1 if m == n else 0
        print 1 if m != n else 0
        print 1 if m <  n else 0
        print 1 if m <= n else 0
        print 1 if m >  n else 0
        print 1 if m >= n else 0
        n += 1
    m += 1
# --    
# test comparison operator concatenation
m = -2
while m <= 2:
    n = -2
    while n <= 2:
        p = -2
        while p <= 2:
            x = 0
            k = 1
            x += k if m == n == p else 0; k *= 2
            x += k if m == n != p else 0; k *= 2
            x += k if m == n <  p else 0; k *= 2
            x += k if m == n <= p else 0; k *= 2
            x += k if m == n >  p else 0; k *= 2
            x += k if m == n >= p else 0; k *= 2
            x += k if m != n == p else 0; k *= 2
            x += k if m != n != p else 0; k *= 2
            x += k if m != n <  p else 0; k *= 2
            x += k if m != n <= p else 0; k *= 2
            x += k if m != n >  p else 0; k *= 2
            x += k if m != n >= p else 0; k *= 2
            x += k if m <= n == p else 0; k *= 2
            x += k if m <= n != p else 0; k *= 2
            x += k if m <= n <  p else 0; k *= 2
            x += k if m <= n <= p else 0; k *= 2
            x += k if m <= n >  p else 0; k *= 2
            x += k if m <= n >= p else 0; k *= 2
            x += k if m <  n == p else 0; k *= 2
            x += k if m <  n != p else 0; k *= 2
            x += k if m <  n <  p else 0; k *= 2
            x += k if m <  n <= p else 0; k *= 2
            x += k if m <  n >  p else 0; k *= 2
            x += k if m <  n >= p else 0; k *= 2
            x += k if m >= n == p else 0; k *= 2
            x += k if m >= n != p else 0; k *= 2
            x += k if m >= n <  p else 0; k *= 2
            x += k if m >= n <= p else 0; k *= 2
            x += k if m >= n >  p else 0; k *= 2
            x += k if m >= n >= p else 0; k *= 2
            x += k if m >  n == p else 0; k *= 2
            x += k if m >  n != p else 0; k *= 2
            x += k if m >  n <  p else 0; k *= 2
            x += k if m >  n <= p else 0; k *= 2
            x += k if m >  n >  p else 0; k *= 2
            x += k if m >  n >= p else 0; k *= 2
            print x
            p += 1
        n += 1
    m += 1
# --    
# and
m = -2
while m <= 2:
    n = -2
    while n <= 2:
        print 1 if m and n else 0
        n += 1
    m += 1
# --
# or
m = -2
while m <= 2:
    n = -2
    while n <= 2:
        print 1 if m or n else 0
        n += 1
    m += 1
# --
# and
m = -2
while m <= 2:
    n = -2
    while n <= 2:
        print m and n
        n += 1
    m += 1
# --
# or
m = -2
while m <= 2:
    n = -2
    while n <= 2:
        print m or n
        n += 1
    m += 1
# --
# function
def foo(n):
    return n + 10
    
n = 42
p = foo(n)
print p
# --
# function
def foo(n):
    return n + 10
    
def bar(n):
    return n * 2
    
n = 42
p = foo(bar(n))
print p
# --
# recursive function
def fac(n):
    if n == 1:
        return 1
    else:
        return n * fac(n - 1)
    
n = 10
p = fac(n)
print p
# --
# recursive function
def fib(n):
    if n <= 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)
    
print fib(10)
# --
# mutual recursive functions
def even(n):
    if n == 0:
        return 1
    else:
        return odd(n - 1)
    
def odd(n):
    if n == 0:
        return 0
    else:
        return even(n - 1)
    
n = 10
print even(10)
print odd(10)
# --
