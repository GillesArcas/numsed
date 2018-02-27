"""
numsed library

numsed opcodes include unsigned operators (+, -, *) and unsigned
comparisons. This library provides functions implementing all
arithmetic and comparison signed operators using only numsed
operators.
"""


# signed comparison operators


def signed_eq(x, y):
    if is_positive(x):
        if is_positive(y):
            return x == y
        else:
            return 0
    else:
        if is_positive(y):
            return 0
        else:
            return negative(x) == negative(y)

def signed_noteq(x, y):
    return not signed_eq(x, y)

def signed_lt(x, y):
    if is_positive(x):
        if is_positive(y):
            return x < y
        else:
            return 0
    else:
        if is_positive(y):
            return 1
        else:
            return negative(x) > negative(y)

def signed_lte(x, y):
    if is_positive(x):
        if is_positive(y):
            return x <= y
        else:
            return 0
    else:
        if is_positive(y):
            return 1
        else:
            return negative(x) >= negative(y)

def signed_gt(x, y):
    return not signed_lte(x, y)

def signed_gte(x, y):
    return not signed_lt(x, y)


# unsigned arithmetic operators


def udiv(a, b):
    # http://compoasso.free.fr/primelistweb/page/prime/euclide.php
    r = a
    q = 0
    n = 0
    aux = b

    while aux <= a:
        aux *= 2
        n += 1

    while n > 0:
        aux = divide_by_two(aux)
        n -= 1
        q *= 2
        if r >= aux:
            r -= aux
            q += 1

    return q


def upow(base, exp):
    result = 1
    while exp:
        if exp & 1: # odd primitive ?
            result *= base
        exp = divide_by_two(exp)
        base *= base
    return result


# signed arithmetic operators


def signed_add(x, y):
    if is_positive(x):
        if is_positive(y):
            r = x + y
        else:
            y = negative(y)
            if x > y:
                r = x - y
            else:
                r = negative(y - x)
    else:
        x = negative(x)
        if is_positive(y):
            if x > y:
                r = negative(x - y)
            else:
                r = y - x
        else:
            y = negative(y)
            r = negative(x + y)
    return r


def signed_sub(x, y):
    if is_positive(x):
        if is_positive(y):
            if x > y:
                return x - y
            else:
                return negative(y - x)
        else:
            return x + negative(y)
    else:
        abs_x = negative(x)
        if is_positive(y):
            return negative(abs_x + y)
        else:
            abs_y = negative(y)
            if abs_x > abs_y:
                return negative(abs_x - abs_y)
            else:
                return abs_y - abs_x


def signed_mult(x, y):
    if is_positive(x):
        if is_positive(y):
            return x * y
        else:
            abs_y = negative(y)
            return negative(x * abs_y)
    else:
        abs_x = negative(x)
        if is_positive(y):
            return negative(abs_x * y)
        else:
            abs_y = negative(y)
            return abs_x * abs_y


def signed_div(x, y):
    if is_positive(x):
        if is_positive(y):
            q = udiv(x, y)
            return q
        else:
            abs_y = negative(y)
            q = udiv(x, abs_y)
            r = x - abs_y * q
            if r == 0:
                return negative(q)
            else:
                return negative(q + 1)
    else:
        abs_x = negative(x)
        if is_positive(y):
            q = udiv(abs_x, y)
            r = abs_x - y * q
            if r == 0:
                return negative(q)
            else:
                return negative(q + 1)
        else:
            abs_y = negative(y)
            q = udiv(abs_x, abs_y)
            return q


def signed_mod(x, y):
    q = signed_div(x, y)
    return signed_sub(x, signed_mult(y, q))


def signed_pow(base, exp):
    if exp < 0:
        raise Exception('Exponent should be positive')

    if is_positive(base):
        return upow(base, exp)
    else:
        return negative(upow(negative(base), exp))


def divide_by_two(x):
    return divide_by_ten(x * 5)


# -- Primitives --------------------------------------------------------------

"""
Primitive functions are used in the definition of the library functions.
However, they are handled separately:
- they are not transformed,
- they are added to positive forms. This enables to test the transformation,
- they are removed when generating opcodes and replaced with dedicated
  opcodes.
"""


PRIMITIVES = ('is_positive', 'negative', 'divide_by_ten')


def is_positive(x):
    return x > 0

def negative(x):
    return -x

def divide_by_ten(x):
    return x // 10
