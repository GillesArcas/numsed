# pass
pass
# ---
# print constant
print(42)
# ---
# print long int constant
print(10000000000000000000)
# ---
# constant error
n = 42.0
# ===
numsed error: line 2 col 5: not an integer
n = 42.0
    ^
# ---
# constant error
n = 'foo'
# ===
numsed error: line 2 col 5: strings not handled (unless as print argument)
n = 'foo'
    ^
# ---
# variable names
_ = 1
print(_)
n = 42
print(n)
nn = 13
print(nn)
nnnnnnnnnnnnnnnnn = 5
print(nnnnnnnnnnnnnnnnn)
n1 = 543
print(n1)
n123456789000 = 64
print(n123456789000)
a_very_long_variable_name = 17
print(a_very_long_variable_name)
# ---
# assign variable
m = 42
n = m
print(n)
# ---
# can't assign
1 = 2
# ===
SyntaxError: can't assign to literal
line 2: 1 = 2
# ---
# cannot assign to
x[0] = 1
# ===
numsed error: line 2 col 1: cannot assign to
x[0] = 1
^
# ---
# chained assignment
m = n = 42
print(m, n)
m = n = p = 42
print(m, n, p)
m = n = p = q = 42
print(m, n, p, q)
# ---
# assign add
m = 42
n = 5
p = m + n
print(p)
# ---
# assign sub
m = 42
n = 5
p = m - n
print(p)
# ---
# assign mul
m = 42
n = 5
p = m * n
print(p)
# ---
# assign div
m = 42234683543
n = 557
p = m // n
print(p)
# ---
# assign mod
m = 42
n = 5
p = m % n
print(p)
# ---
# assign pow
m = 42
n = 5
p = m ** n
print(p)
# ---
# assign expression
m = 42
n = 5
p = (m * n + m // n) - 3 * (m - n)
print(p)
# ---
# binary operator not handled
x = 5 & 7
# ===
numsed error: line 2 col 5: operator not handled
x = 5 & 7
    ^
# ---
# unary arithmetical operators
if +5 == 5:
    print(1)
else:
    print(0)
if -5 == 0 - 5:
    print(1)
else:
    print(0)
# ---
# unary operator operator not handled
x = ~5
# ===
numsed error: line 2 col 5: operator not handled
x = ~5
    ^
# ---
# augmented assign add
m = 42
n = 5
m += n
print(m)
# ---
# augmented assign sub
m = 42
n = 5
m -= n
print(m)
# ---
# augmented assign mul
m = 42
n = 5
m *= n
print(m)
# ---
# augmented assign div
m = 42
n = 5
m //= n
print(m)
# ---
# augmented assign mod
m = 42
n = 5
m %= n
print(m)
# ---
# augmented assign pow
m = 42
n = 5
m **= n
print(m)
# ---
# augmented assign expression
m = 42
n = 5
m += (m * n + m // n) - 3 * (m - n)
print(m)
# ---
# add negative values (+-)
m = 42
n = -5
p = m + n
print(p)
# ---
# add negative values (-+)
m = -42
n = 5
p = m + n
print(p)
# ---
# add negative values (--)
m = -42
n = -5
p = m + n
print(p)
# ---
# sub negative values (+-)
m = 42
n = -5
p = m - n
print(p)
# ---
# sub negative values (-+)
m = -42
n = 5
p = m - n
print(p)
# ---
# sub negative values (--)
m = -42
n = -5
p = m - n
print(p)
# ---
# mul negative values (+-)
m = 42
n = -5
p = m * n
print(p)
# ---
# mul negative values (-+)
m = -42
n = 5
p = m * n
print(p)
# ---
# mul negative values (--)
m = -42
n = -5
p = m * n
print(p)
# ---
# div negative values (+-)
m = 42
n = -5
p = m // n
print(p)
# ---
# div negative values (-+)
m = -42
n = 5
p = m // n
print(p)
# ---
# div negative values (--)
m = -42
n = -5
p = m // n
print(p)
# ---
# mod negative values (+-)
m = 42
n = -5
p = m % n
print(p)
# ---
# mod negative values (-+)
m = -42
n = 5
p = m % n
print(p)
# ---
# mod negative values (--)
m = -42
n = -5
p = m % n
print(p)
# ---
# loop increasing
n = -10
while n <= 10:
    print(n)
    n += 1
# ---
# loop decreasing
n = 10
while n >= -10:
    print(n)
    n -= 1
# ---
# loop
n = -10
while n <= -5:
    print(n)
    n += 1
# ---
# loop
n = -5
while n >= -10:
    print(n)
    n -= 1
# ---
# while else
n = 0
while n < 10:
    if n == 5:
        break
    n += 1
else:
    print(n)
n = 0
while n < 10:
    if n == 15:
        break
    n += 1
else:
    print(n)
# ---
# while else
def foo(x):
    n = 0
    while n < 10:
        if n == x:
            print(x)
            break
        n += 1
    else:
        print(0)
    print(1)

foo(5)
foo(15)
# ---
# while else
def foo(x):
    n = 0
    while n < 10:
        if n == x:
            return x
        n += 1
    else:
        return 0
    return 1

print(foo(5))
print(foo(15))
# ---
# if elif else
n = -10
while n <= 10:
    if n <= -5:
        print(-1)
    elif n >= 5:
        print(+1)
    else:
        print(0)
    n += 1
# ---
# if operator
n = -10
while n <= 10:
    print(-1 if n <= -5 else +1 if n >= 5 else 0)
    n += 1
# ---
# double loop
m = -10
while m <= 10:
    n = -10
    while n <= m:
        print(m, n)
        n += 1
    m += 1
# ---
# double loop
m = 10
while m >= -10:
    n = 10
    while n >= m:
        print(m, n)
        n -= 1
    m -= 1
# ---
# break statement
n = 0
while n <= 10:
    n += 1
    if n == 8:
        break
    print(n)
# ---
# break statement
m = -10
while m <= 10:
    n = -10
    while n <= 10:
        print(m)
        if m + n == 13:
            break
        n += 1
    m += 1
# ---
# break statement
m = -10
while m <= 10:
    n = -10
    while n <= 10:
        print(m)
        n += 1
    if m + n == 13:
        break
    m += 1
# ---
# continue statement
n = 0
while n <= 10:
    n += 1
    if n == 8:
        continue
    print(n)
# ---
# continue statement
m = -10
while m <= 10:
    n = -10
    while n <= 10:
        print(m)
        n += 1
        if m + n == 13:
            continue
    m += 1
# ---
# continue statement
m = -10
while m <= 10:
    n = -10
    while n <= 10:
        print(m)
        n += 1
    m += 1
    if m + n == 13:
        continue
# ---
# loop on unary positive
n = -10
while n <= 10:
    p = +n
    print(p)
    n += 1
# ---
# loop on unary negative
n = -10
while n <= 10:
    p = -n
    print(p)
    n += 1
# ---
# loop on adding values
m = -10
while m <= 10:
    n = -10
    while n <= 10:
        p = m + n
        print(p)
        n += 1
    m += 1
# ---
# loop on subtracting values
m = -10
while m <= 10:
    n = -10
    while n <= 10:
        p = m - n
        print(p)
        n += 1
    m += 1
# ---
# loop on multiplying values
m = -10
while m <= 10:
    n = -10
    while n <= 10:
        p = m * n
        print(p)
        n += 1
    m += 1
# ---
# loop on dividing values
m = -10
while m <= 10:
    n = -10
    while n <= 10:
        if n != 0:
            p = m // n
            print(p)
        n += 1
    m += 1
# ---
# loop on modulo
m = -10
while m <= 10:
    n = -10
    while n <= 10:
        if n != 0:
            p = m % n
            print(p)
        n += 1
    m += 1
# ---
# loop on divmod
m = -10
while m <= 10:
    n = -10
    while n <= 10:
        if n != 0:
            q, r = divmod(m, n)
            print(q, r)
        n += 1
    m += 1
# ---
# loop on power
m = -10
while m <= 10:
    n = 0
    while n <= 10:
        p = m ** n
        print(p)
        n += 1
    m += 1
# ---
# comparison operators
m = -2
while m <= 2:
    n = -2
    while n <= 2:
        print(1 if m == n else 0,
              1 if m != n else 0,
              1 if m <  n else 0,
              1 if m <= n else 0,
              1 if m >  n else 0,
              1 if m >= n else 0)
        n += 1
    m += 1
# ---
# comparison concatenation
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
            print(x)
            p += 1
        n += 1
    m += 1
# ---
# comparator not handled
x = 1 is 2
# ===
numsed error: line 2 col 5: comparator not handled
x = 1 is 2
    ^
# ---
# not
print(not 0)
print(not 1)
print(not 2)
# ===
1
0
0
# ---
# and
m = -2
while m <= 2:
    n = -2
    while n <= 2:
        print(1 if m and n else 0)
        n += 1
    m += 1
# ---
# or
m = -2
while m <= 2:
    n = -2
    while n <= 2:
        print(1 if m or n else 0)
        n += 1
    m += 1
# ---
# test not
m = -2
while m <= 2:
    n = -2
    while n <= 2:
        print(1 if not(m == n) else 0,
              1 if not(m != n) else 0,
              1 if not(m <  n) else 0,
              1 if not(m <= n) else 0,
              1 if not(m >  n) else 0,
              1 if not(m >= n) else 0)
        n += 1
    m += 1
# ---
# and
m = -2
while m <= 2:
    n = -2
    while n <= 2:
        print(m and n)
        n += 1
    m += 1
# ---
# or
m = -2
while m <= 2:
    n = -2
    while n <= 2:
        print(m or n)
        n += 1
    m += 1
# ---
# construct is not handled
x = []
# ===
numsed error: line 2 col 5: construct is not handled
x = []
    ^
# ---
# function
def foo(n):
    return n + 10

n = 42
print(foo(n))
# ---
# function
def foo(n):
    return n + 10

def bar(n):
    return n * 2

n = 42
print(foo(bar(n)))
# ---
# function definitions allowed only at module level - 1
if 1:
    def foo():
        return 42
# ===
numsed error: line 3 col 5: function definitions allowed only at module level
    def foo():
    ^
# ---
# function definitions allowed only at module level - 2
def spam():
    def foo():
        return 42
# ===
numsed error: line 3 col 5: function definitions allowed only at module level
    def foo():
    ^
# ---
# callable not handled
foo(x)(y)
# ===
numsed error: line 2 col 1: callable not handled
foo(x)(y)
^
# ---
# not allowed to redefine numsed_lib functions
def udivmod(x, y):
    return 0
# ===
numsed error: line 2 col 1: not allowed to redefine numsed_lib functions
def udivmod(x, y):
^
# ---
# no vararg arguments
def foo(*args):
    print(args)
# ===
numsed error: line 2 col 1: no vararg arguments
def foo(*args):
^
# ---
# no kwarg arguments
def foo(**kwargs):
    print(kwargs)
# ===
numsed error: line 2 col 1: no kwarg arguments
def foo(**kwargs):
^
# ---
# no default arguments
def spam(x=42):
    return x
# ===
numsed error: line 2 col 1: no default arguments
def spam(x=42):
^
# ---
# recursion: fac
def fac(n):
    if n == 1:
        return 1
    else:
        return n * fac(n - 1)

n = 10
r = fac(n)
print(r)
# ---
# recursion: fib
def fib(n):
    if n <= 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)

print(fib(10))
# ---
# recursion: Hofstadter G sequence
def G(n):
    if n == 0:
        return 0
    else:
        return n - G(G(n - 1))

print(G(10))
# ---
# recursion: Hofstadter H sequence
def H(n):
    if n == 0:
        return 0
    else:
        return n - H(H(H(n - 1)))

print(H(10))
# ---
# recursion: Hofstadter Q sequence
def Q(n):
    if n <= 2:
        return 1
    else:
        return Q(n - Q(n - 1)) + Q(n - Q(n - 2))

print(Q(10))
# ---
# recursion: binomial coefficient
def binomial(n, k):
    if k == 0 or k == n:
        return 1
    else:
        return binomial(n - 1, k - 1) + binomial(n - 1, k)

n = 8
k = 0
while k <= n:
    print(binomial(n, k))
    k += 1
# ---
# mutual recursion: odd/even
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
print(even(10))
print(odd(10))
# ---
# mutual recursion: Hofstadter
def F(n):
    if n == 0:
        return 1
    else:
        return n - M(F(n - 1))

def M(n):
    if n == 0:
        return 0
    else:
        return n - F(M(n - 1))

print(F(15))
print(M(15))
# ---
# mutual recursion: Kurkiewicz
def R(k):
    if k == 1:
        return 1
    else:
        return R(k-1) + M(k-1) + C(k-1)

def M(k):
    if k == 1:
        return 1
    else:
        return R(k-1) + M(k-1)

def C(k):
    if k == 1:
        return 1
    else:
        return R(k-1) + C(k-1)

print(R(6) + M(6) + C(6))
# ---
# global
x = 0
def foo():
    global x
    x = x + 1
    return x

print(foo())
print(x)
# ---
# print strings
print('Hello word!')
print("Hello word!")
print('Hello "word"!')
print("Hello 'word'!")
# ---
# print several arguments
print()
print(1)
print(1, 2)
print(1, 2, 3)
print('foo')
print('foo', 'bar')
print('foo', 'bar', 'baz')
print('')
print(' ')
print('  ')
print('   ')
print('    ')
x = 1
print(1 + x, 'foo', 2 + x)
print(1, ' ', 2, '  ', 3, '   ', 4)
print(1, '', 2, '', 3, '', 4)
# ---
# print: forbidden characters
print('foo;bar')
# ===
numsed error: line 2 col 7: character not handled (@|;~)
print('foo;bar')
      ^
# ---
# Multiple assignment (constants)
a, = 1,
x, = a,
print(x)
a, b = 1, 2
x, y = a, b
print(x, y)
a, b, c = 1, 2, 3
x, y, z = a, b, c
print(x, y, z)
a, b, c, d = 1, 2, 3, 4
x, y, z, t = a, b, c, d
print(x, y, z, t)
# ---
# Multiple assignment (expressions)
a, b = 1, 2
x, y = a + b, a - b
print(x, y)
a, b, c = 1, 2, 3
x, y, z = a + b, b + c, c + a
print(x, y, z)
a, b, c, d = 1, 2, 3, 4
x, y, z, t = a, a - b, a - b + c, a - b + c - d
print(x, y, z, t)
# ---
# Swap and permutation
x, y = 1, 2
x, y = y, x
print(x, y)
x, y, z = 1, 2, 3
x, y, z = z, x, y
print(x, y, z)
x, y, z, t = 1, 2, 3, 4
x, y, z, t = t, z, y, x
print(x, y, z, t)
# ---
# target and value must have same length
a, b, c = 1, 2
# ===
numsed error: line 2 col 1: targets and values must have same length
a, b, c = 1, 2
^
# ---
# multiple assignment must have same number of variables
a, b, c = e, f = 1, 2
# ===
numsed error: line 2 col 1: multiple assignment must have same number of variables
a, b, c = e, f = 1, 2
^
# ---
# elements of tuples may not be tuples
x, y = 1, (2, 3)
# ===
numsed error: line 2 col 12: elements of tuples may not be tuples
x, y = 1, (2, 3)
           ^
# ---
# Multiple assignment with function results
def foo(n):
    return 2 * n + 1

x, y, z = foo(13), foo(17), foo(19)
print(x, y, z)
# ---
# function result must be an integer (tuple)
def foo(x, y):
    return x + y, x - y
# ===
numsed error: line 3 col 12: function result must be an integer
    return x + y, x - y
           ^
# ---
# function result must be an integer (divmod)
def foo(x, y):
    return divmod(x, y)
# ===
numsed error: line 3 col 12: divmod results must be assigned immediately
    return divmod(x, y)
           ^
# ---
