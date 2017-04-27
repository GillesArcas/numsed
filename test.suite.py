# print constant
print 42
---
# assign constant
n = 42
print n
---
# assign add
m = 42
n = 5
p = m + n
print p
---
# assign sub
m = 42
n = 5
p = m - n
print p
---
# assign mul
m = 42
n = 5
p = m * n
print p
---
# assign div
m = 42
n = 5
p = m // n
print p
---
# assign mod
m = 42
n = 5
p = m % n
print p
---
# assign expression
m = 42
n = 5
p = (m * n + m // n) - 3 * (m - n)
print p
---
# augmented assign add
m = 42
n = 5
m += n
print m
---
# augmented assign sub
m = 42
n = 5
m -= n
print m
---
# augmented assign mul
m = 42
n = 5
m *= n
print m
---
# augmented assign div
m = 42
n = 5
m //= n
print m
---
# augmented assign mod
m = 42
n = 5
m %= n
print m
---
# augmented assign expression
m = 42
n = 5
m += (m * n + m // n) - 3 * (m - n)
print m
---
# add negative values (+-)
m = 42
n = -5
p = m + n
print p
---
# add negative values (-+)
m = -42
n = 5
p = m + n
print p
---
# add negative values (--)
m = -42
n = -5
p = m + n
print p
---
# sub negative values (+-)
m = 42
n = -5
p = m - n
print p
---
# sub negative values (-+)
m = -42
n = 5
p = m - n
print p
---
# sub negative values (--)
m = -42
n = -5
p = m - n
print p
---
# mul negative values (+-)
m = 42
n = -5
p = m * n
print p
---
# mul negative values (-+)
m = -42
n = 5
p = m * n
print p
---
# mul negative values (--)
m = -42
n = -5
p = m * n
print p
---
# div negative values (+-)
m = 42
n = -5
p = m // n
print p
---
# div negative values (-+)
m = -42
n = 5
p = m // n
print p
---
# div negative values (--)
m = -42
n = -5
p = m // n
print p
---
# mod negative values (+-)
m = 42
n = -5
p = m % n
print p
---
# mod negative values (-+)
m = -42
n = 5
p = m % n
print p
---
# mod negative values (--)
m = -42
n = -5
p = m % n
print p
---
# loop
n = -10
while n <= 10:
    print n
    n += 1
---
# loop
n = 10
while n >= -10:
    print n
    n -= 1
---
# loop
n = -10
while n <= -5:
    print n
    n += 1
---
# loop
n = -5
while n >= -10:
    print n
    n -= 1
---
# loop on adding values
m = -10
while m <= 10:
    n = -10
    while n <= 10:
        p = m + n
        print p
        n += 1
    m += 1
---
# loop on subtracting values
m = -10
while m <= 10:
    n = -10
    while n <= 10:
        p = m - n
        print p
        n += 1
    m += 1
---
# loop on multiplying values
m = -10
while m <= 10:
    n = -10
    while n <= 10:
        p = m * n
        print p
        n += 1
    m += 1
---
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
---
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
---
