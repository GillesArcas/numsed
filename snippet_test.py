from __future__ import print_function

import subprocess
import random

import common
from sedcode import (normalize,
                 STARTUP, MAKE_CONTEXT, POP_CONTEXT, PUSH, POP,
                 LOAD_GLOBAL, STORE_GLOBAL, LOAD_FAST, STORE_FAST,
                 CMP, FULLADD, FULLSUB, UADD, USUB, FULLMUL,
                 MULBYDIGIT, UMUL, DIVBY2, ODD, EQU)


def random_ndigits(n):
    return random.randint(10 ** (n - 1), 10 ** n)

def random_varname():
    return ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', random.randint(1, 10)))

def random_content():
    x = [str(random.randint(0, 10 ** random.randint(0, 10))) for _ in range(random.randint(0, 10))]
    return ';'.join(x)


def test_context_0():
    """
    store and load 10 global variables, load the 10 variables again
    """
    nvars = 10
    inplist = list()
    outlist = list()
    numlist1 = [random_ndigits(10) for _ in range(1, nvars+1)]
    numlist2 = [random_ndigits(10) for _ in range(1, nvars+1)]
    for numlist in (numlist1, numlist2):
        for x in numlist:
            inplist.append('%d' % x)
            outlist.append('%d' % x)
        for x in numlist:
            inplist.append('pop')
            outlist.append('%d' % x)

    return test_gen('context_0', snippet_context_0, inplist, outlist)


def snippet_context_0():
    nvars = 10
    lvars = [random_varname() for n in range(nvars)]
    snippet_begin = '''
        1 {
            STARTUP
        }
        '''
    pattern_store = '''
        %d {
            PUSH
            STORE_GLOBAL %s
            LOAD_GLOBAL %s
            POP
        }
    '''
    pattern_load = '''
        %d {
            LOAD_GLOBAL %s
                POP
              }
        '''
    snippet_end = ''
    snippet = '\n'.join([snippet_begin] +
                        [pattern_store % (n, s, s) for s, n in zip(lvars, range(1, nvars+1))] +
                        [pattern_load  % (n, s) for s, n in zip(lvars, range(nvars+ 1, nvars+11))] +
                        [pattern_store % (n, s, s) for s, n in zip(lvars, range(nvars+11, nvars+21))] +
                        [pattern_load  % (n, s) for s, n in zip(lvars, range(nvars+21, nvars+31))] +
                        [snippet_end])
    return snippet


def test_context_1():
    '''
    store and load the same variable in 10 different local name spaces, load
    again the variables and pop contexts
    '''
    inplist = list()
    outlist = list()
    numlist = [random_ndigits(n) for n in range(1, 11)]
    for x in numlist:
        inplist.append('push%d' % x)
        outlist.append('%d' % x)
    for x in reversed(numlist):
        inplist.append('pop')
        outlist.append('%d' % x)

    return test_gen('context_1', snippet_context_1, inplist, outlist)


def snippet_context_1():
    snippet = '''
        1 {
            STARTUP
        }
        /^push/ {
            s/^push//
            MAKE_CONTEXT
            PUSH
            STORE_FAST x
            LOAD_FAST x
            POP
        }
        /^pop/ {
            s/^pop//
            LOAD_FAST x
            POP
            POP_CONTEXT
        }
    '''
    return snippet


def test_context_2():
    """
    store and load 10 local variables, load the 10 variables again
    """
    nvars = 10
    inplist = list()
    outlist = list()
    numlist = [random_ndigits(10) for _ in range(1, nvars+1)]
    for x in numlist:
        inplist.append('%d' % x)
        outlist.append('%d' % x)
    for x in numlist:
        inplist.append('pop')
        outlist.append('%d' % x)

    return test_gen('context_2', snippet_context_2, inplist, outlist)


def snippet_context_2():
    nvars = 10
    lvars = [random_varname() for n in range(nvars)]
    snippet_begin = '''
        1 {
            STARTUP
            MAKE_CONTEXT
        }
    '''
    pattern_store = '''
        %d {
            PUSH
            STORE_FAST %s
            LOAD_FAST %s
            POP
        }
        '''
    pattern_load = '''
        %d {
            LOAD_FAST %s
            POP
        }
        '''
    snippet_end = '''
        $ {
            POP_CONTEXT
        }
        '''
    snippet = '\n'.join([snippet_begin] +
                        [pattern_store % (n, s, s) for n, s in zip(range(1, nvars+1), lvars)] +
                        [pattern_load % (n, s) for n, s in zip(range(nvars+1, nvars+11), lvars)] +
                        [snippet_end])
    return snippet


def test_context_3():
    '''
    store and load several times 3 global variables
    '''
    inplist = ['0']
    outlist = ['end_of_script;@;z;3;y;2;x;1']
    return test_gen('context_3', snippet_context_3, inplist, outlist)


def snippet_context_3():
    snippet = '''
        STARTUP
        LOAD_CONST 1
        STORE_NAME x
        LOAD_CONST 2
        STORE_NAME y
        LOAD_CONST 3
        STORE_NAME z
        LOAD_CONST 4
        STORE_NAME x
        LOAD_CONST 5
        STORE_NAME y
        LOAD_CONST 6
        STORE_NAME z
        LOAD_CONST 1
        STORE_NAME x
        LOAD_CONST 2
        STORE_NAME y
        LOAD_CONST 3
        STORE_NAME z
        x
        '''
    return snippet


def test_context_4():
    '''
    store and load several times 3 local variables
    '''
    inplist = ['0']
    outlist = ['end_of_script;@|;x;1;y;2;z;3']
    return test_gen('context_4', snippet_context_4, inplist, outlist)


def snippet_context_4():
    snippet = '''
        STARTUP
        MAKE_CONTEXT
        LOAD_CONST 1
        STORE_FAST x
        LOAD_CONST 2
        STORE_FAST y
        LOAD_CONST 3
        STORE_FAST z
        LOAD_CONST 4
        STORE_FAST x
        LOAD_CONST 5
        STORE_FAST y
        LOAD_CONST 6
        STORE_FAST z
        LOAD_CONST 1
        STORE_FAST x
        LOAD_CONST 2
        STORE_FAST y
        LOAD_CONST 3
        STORE_FAST z
        x
        '''
    return snippet


def test_cmp_1():
    '''
    Input  PS: M;N;
    Output PS: < or = or >
    all values from 0 to 99
    '''
    inplist = list()
    outlist = list()
    for a in range(100):
        for b in range(100):
            inplist.append('%d;%d;' % (a, b))
            outlist.append('%s' % '<' if a < b else '=' if a == b else '>')

    return test_gen('CMP_1', CMP, inplist, outlist)


def test_cmp_2():
    '''
    Input  PS: M;N;
    Output PS: < or = or >
    100 x 100 values with 1 to 99 digits
    '''
    inplist = list()
    outlist = list()
    for p in range(1, 100):
        for q in range(1, 100):
            a = random_ndigits(p)
            b = random_ndigits(q)
            inplist.append('%d;%d;' % (a, b))
            outlist.append('%s' % '<' if a < b else '=' if a == b else '>')

    return test_gen('CMP_2', CMP, inplist, outlist)


def test_equ():
    '''
    Input  HS: M;N;
    Output PS: 0 or 1
    100 equalities and 100 differences with 1 to 99 digits
    '''
    inplist = list()
    outlist = list()
    for p in range(1, 100):
        a = random_ndigits(p)
        b = random_ndigits(p)
        while b == a:
            b = random_ndigits(p)
        inplist.append('%d;%d;' % (a, a))
        outlist.append('%s' % '1')
        inplist.append('%d;%d;' % (a, b))
        outlist.append('%s' % '0')

    return test_gen('EQU', lambda: 'x\n' + EQU(), inplist, outlist)


def test_fulladd():
    '''
    test full adder for all values
    Input  PS: abcX with a and b = 0 to 9, c = 0 or 1
    Output PS: rX   with r = a + b + c padded on two digits
    '''
    inplist = list()
    outlist = list()
    for a in range(10):
        for b in range(10):
            for c in range(2):
                rest = random_content()
                inplist.append('%d%d%d%s' % (a, b, c, rest))
                outlist.append('%02d%s' % (a + b + c, rest))

    return test_gen('FULLADD', FULLADD, inplist, outlist)


def test_fullsub():
    '''
    test full subtractor with all values
    Input  PS: abcX with c = 0 or 1
    Output PS: xyX  with if b+c <= a, x = 0, y = a-(b+c)
                         if b+c >  a, x = 1, y = 10+a-(b+c)
    '''
    inplist = list()
    outlist = list()
    for a in range(10):
        for b in range(10):
            for c in range(2):
                rest = random_content()
                inplist.append('%d%d%d%s' % (a, b, c, rest))
                if (b + c) <= a:
                    x, y = 0, a - (b + c)
                else:
                    x, y = 1, 10 + a - (b + c)
                outlist.append('%d%d%s' % (x, y, rest))

    return test_gen('FULLSUB', FULLSUB, inplist, outlist)


def test_uadd():
    '''
    test addition of all integers less or equal 100, and 100 pairs of integers
    with at most 9 digits
    Input  PS: M;N;
    Output PS: R;   with R = M+N
    '''
    inplist = list()
    outlist = list()
    for a in range(101):
        for b in range(101):
            inplist.append('%d;%d;' % (a, b))
            outlist.append('%d;' % (a + b,))
    for _ in range(100):
        a = random.randint(0, 10 ** 10)
        b = random.randint(0, 10 ** 10)
        inplist.append('%d;%d;' % (a, b))
        outlist.append('%d;' % (a + b,))

    return test_gen('UADD', UADD, inplist, outlist)


def test_usub_1():
    '''
    test subtraction of all integers less or equal 100, and 100 pairs of integers
    with at most 9 digits, result is always positive
    Input  PS: M;N;
    Output PS: R;   with R = M-N
    '''
    inplist = list()
    outlist = list()
    for a in range(101):
        for b in range(a + 1):
            inplist.append('%d;%d;' % (a, b))
            outlist.append('%d;' % (a - b,))
    for _ in range(100):
        a = random.randint(0, 10 ** 10)
        b = random.randint(0, a + 1)
        inplist.append('%d;%d;' % (a, b))
        outlist.append('%d;' % (a - b,))

    return test_gen('USUB_1', USUB, inplist, outlist)


def test_usub_2():
    '''
    test subtraction x - x
    Input  PS: M;N;
    Output PS: R;   with R = M-N
    '''
    inplist = list()
    outlist = list()
    for n in range(100):
        a = random.randint(0, 10 ** n)
        b = a
        inplist.append('%d;%d;' % (a, b))
        outlist.append('%d;' % (a - b,))

    return test_gen('USUB_2', USUB, inplist, outlist)


def test_fullmul():
    '''
    test full multiplier with all values
    Input  PS: abcX with a, b and c = 0 to 9
    Output PS: rX   with r = a * b + c padded on two digits
    '''
    inplist = list()
    outlist = list()
    for a in range(10):
        for b in range(10):
            for c in range(10):
                rest = random_content()
                inplist.append('%d%d%d%s' % (a, b, c, rest))
                outlist.append('%02d%s' % (a * b + c, rest))

    return test_gen('FULLMUL', FULLMUL, inplist, outlist)


def test_mulbydigit():
    '''
    test digit multiplier with random numbers
    Input  PS: aN;X with a = 0 to 9
    Output PS: R;X  with R = a*N
    '''
    inplist = list()
    outlist = list()
    for d in range(10):
        for _ in range(100):
            a = random.randint(0, 10 ** 10)
            rest = random_content()
            inplist.append('%d%d;%s' % (d, a, rest))
            outlist.append('%d;%s' % (d * a, rest))

    return test_gen('MULBYDIGIT', MULBYDIGIT, inplist, outlist)


def test_umul_1():
    '''
    test multiplication of all integers less or equal 100
    Input  PS: M;N;
    Output PS: R   with R = M*N
    '''
    inplist = list()
    outlist = list()
    for a in range(101):
        for b in range(101):
            inplist.append('%d;%d;' % (a, b))
            outlist.append('%d' % (a * b,))

    return test_gen('UMUL_1', UMUL, inplist, outlist)


def test_umul_2():
    '''
    test multiplication of single digits with random numbers (d*n and n*d)
    Input  PS: M;N;
    Output PS: R   with R = M*N
    '''
    inplist = list()
    outlist = list()
    for a in range(10):
        for b in range(1, 101):
            x = random_ndigits(b)
            inplist.append('%d;%d;' % (a, x))
            outlist.append('%d' % (a * x,))
            inplist.append('%d;%d;' % (x, a))
            outlist.append('%d' % (x * a,))

    return test_gen('UMUL_2', UMUL, inplist, outlist)


def test_umul_3():
    '''
    test multiplication of 100 pairs of integers with at most 9 digits
    Input  PS: M;N;
    Output PS: R   with R = M*N
    '''
    inplist = list()
    outlist = list()
    for _ in range(100):
        a = random.randint(0, 10 ** 10)
        b = random.randint(0, 10 ** 10)
        inplist.append('%d;%d;' % (a, b))
        outlist.append('%d' % (a * b,))

    return test_gen('UMUL_3', UMUL, inplist, outlist)


def test_umul_4():
    '''
    test multiplication of 100 pairs of integers with at most 99 digits
    Input  PS: M;N;
    Output PS: R   with R = M*N
    '''
    inplist = list()
    outlist = list()
    for _ in range(10):
        a = random.randint(0, 10 ** 100)
        b = random.randint(0, 10 ** 100)
        inplist.append('%d;%d;' % (a, b))
        outlist.append('%d' % (a * b,))

    return test_gen('UMUL_4', UMUL, inplist, outlist)


def test_umul_5():
    '''
    test multiplication of integers from 1 to 99 (factorial 99)
    Input  PS: (n-1)!;Nn;
    Output PS: R   with R = n!
    '''
    inplist = list()
    outlist = list()
    r = 1
    for n in range(100):
        inplist.append('%d;%d;' % (n, r))
        outlist.append('%d' % (n * r,))
        r *= n

    return test_gen('UMUL_5', UMUL, inplist, outlist)


def test_umul_6():
    '''
    test multiplication of 2 * 2 * ... * 2
    Input  PS: 2**(n-1);2;
    Output PS: R   with R = 2**n
    '''
    inplist = list()
    outlist = list()
    r = 1
    for _ in range(100):
        inplist.append('%d;%d;' % (r, 2))
        outlist.append('%d' % (r * 2,))
        r *= 2

    return test_gen('UMUL_6', UMUL, inplist, outlist)


def test_umul_7():
    '''
    test multiplication of integers will all digits identical (1111 * 1111)
    Input  PS: M;N;
    Output PS: R   with R = M*N
    '''
    inplist = list()
    outlist = list()
    for a in range(1, 10):
        for b in range(1, 10):
            for n in range(1, 10):
                x = int(str(a) * n)
                y = int(str(b) * n)
                inplist.append('%d;%d;' % (x, y))
                outlist.append('%d' % (x * y,))

    return test_gen('UMUL_7', UMUL, inplist, outlist)


def test_divby2_1():
    '''
    test division by 2 for all integers below 100
    Input  PS: N;X
    Output PS: R;X  with R = N // 2
    '''
    inplist = list()
    outlist = list()
    for n in range(0, 100):
        s = random_content()
        inplist.append('%d;%s' % (n, s))
        outlist.append('%d;%s' % (n // 2, s))

    return test_gen('DIVBY2_1', DIVBY2, inplist, outlist)


def test_divby2_2():
    '''
    test division by 2 for 100 big integers
    Input  PS: N;X
    Output PS: R;X  with R = N // 2
    '''
    inplist = list()
    outlist = list()
    for _ in range(0, 100):
        n = random_ndigits(random.randint(100, 200))
        s = random_content()
        inplist.append('%d;%s' % (n, s))
        outlist.append('%d;%s' % (n // 2, s))

    return test_gen('DIVBY2_2', DIVBY2, inplist, outlist)


def test_odd():
    '''
    test odd predicate for all integers below 100
    Input  PS: N;X
    Output PS: R;X  with R = N % 2
    '''
    inplist = list()
    outlist = list()
    for n in range(0, 100):
        s = random_content()
        inplist.append('%d;%s' % (n, s))
        outlist.append('%d;%s' % (n % 2, s))

    return test_gen('ODD', ODD, inplist, outlist)


def test_gen(descr, func, inplist, outlist):
    with open(common.TMP_SED, 'w') as f:
        print(normalize(func()), file=f)

    with open(common.TMP_INPUT, 'w') as f:
        for line in inplist:
            print(line, file=f)

    com = 'sed -r -f %s %s' % (common.TMP_SED, common.TMP_INPUT)

    #res = subprocess.check_output(com).decode('ascii').splitlines()
    res = common.run(com, echo=False).splitlines()

    if res == outlist:
        print('%-15s %s' % (descr, 'OK'))
        return True
    else:
        print('%-15s %s' % (descr, 'fail'))
        for inp, out, res in zip(inplist, outlist, res):
            if out != res:
                print('%-8s %-8s %-8s' % (inp, out, res))
        return False


def main():
    try:
        subprocess.check_output(['sed', '--version'])
    except Exception as e:
        print('Fail to start sed:', str(e))
        exit(1)

    result = all((test_context_0(),
                  test_context_1(),
                  test_context_2(),
                  test_context_3(),
                  test_context_4(),
                  test_cmp_1(),
                  test_cmp_2(),
                  test_equ(),
                  test_fulladd(),
                  test_fullsub(),
                  test_uadd(),
                  test_usub_1(),
                  test_usub_2(),
                  test_fullmul(),
                  test_mulbydigit(),
                  test_umul_1(),
                  test_umul_2(),
                  test_umul_3(),
                  test_umul_4(),
                  test_umul_5(),
                  test_umul_6(),
                  test_umul_7(),
                  test_divby2_1(),
                  test_divby2_2(),
                  test_odd(),))

    print('OK' if result else 'FAIL')
    return result


if __name__ == "__main__":
    main()
