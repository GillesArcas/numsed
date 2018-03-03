import subprocess
import random
from sedcode import (normalize,
                 STARTUP, MAKE_CONTEXT, POP_CONTEXT, PUSH, POP,
                 LOAD_GLOBAL, STORE_GLOBAL, DELETE_GLOBAL, LOAD_FAST,
                 STORE_FAST, CMP, FULLADD, FULLSUB, UADD, USUB, FULLMUL,
                 MULBYDIGIT, UMUL, DIVBY2, ODD)


def random_ndigits(p):
    return random.randint(10 ** (p-1), 10 ** p)

def random_varname():
    return ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', random.randint(1, 10)))

def random_content():
    x = [str(random.randint(0, 10 ** random.randint(0, 10))) for _ in range(random.randint(0, 10))]
    return ';'.join(x)


def func_context_0():
    nvars = 10
    lvars = [random_varname() for n in range(nvars)]
    snippet_begin = '1 {' + STARTUP() + '}\n'
    snippet_end = ''
    def pattern_store(n, s):
        snippet = '''
            n { PUSH
                STORE_GLOBAL s
                LOAD_GLOBAL s
                POP
              }
        '''
        return normalize(snippet, replace=(('n', str(n)), ('s', s)))
    def pattern_load(n, s):
        x = ('%d {' % n, LOAD_GLOBAL(s), POP(), '}\n')
        return '\n'.join(x)
    snippet = '\n'.join([snippet_begin] +
                        [pattern_store(n, s) for s, n in zip(lvars, range(1, nvars+1))] +
                        [pattern_load(n, s)  for s, n in zip(lvars, range(nvars+01, nvars+11))] +
                        [pattern_store(n, s) for s, n in zip(lvars, range(nvars+11, nvars+21))] +
                        [pattern_load(n, s)  for s, n in zip(lvars, range(nvars+21, nvars+31))] +
                        [snippet_end])
    return snippet


def test_context_0():
    # Input  PS:
    # Output PS:
    nvars = 10
    inplist = list()
    outlist = list()
    numlist1 = [random_ndigits(10) for n in range(1, nvars+1)]
    numlist2 = [random_ndigits(10) for n in range(1, nvars+1)]
    for numlist in (numlist1, numlist2):
        for x in numlist:
            inplist.append('%d' % x)
            outlist.append('%d' % x)
        for x in numlist:
            inplist.append('pop')
            outlist.append('%d' % x)
    test_gen('func_context_0', func_context_0, inplist, outlist)


def func_context_1():
    snippet =\
        '''/^push/ {
        s/^push// ''' +\
        MAKE_CONTEXT() +\
        PUSH() +\
        STORE_FAST('x') +\
        LOAD_FAST('x') +\
        POP() +\
        '}\n' +\
        '/^pop/ { s/^pop// ' +\
        LOAD_FAST('x') +\
        POP() +\
        POP_CONTEXT() +\
        '}'
    return snippet

def test_context_1():
    # Input  PS:
    # Output PS:
    inplist = list()
    outlist = list()
    numlist = [random_ndigits(n) for n in range(1, 11)]
    for x in numlist:
        inplist.append('push%d' % x)
        outlist.append('%d' % x)
    for x in reversed(numlist):
        inplist.append('pop')
        outlist.append('%d' % x)
    test_gen('func_context_1', func_context_1, inplist, outlist)


def func_context_2():
    nvars = 10
    lvars = [random_varname() for n in range(nvars)]
    snippet_begin = '1 {' + MAKE_CONTEXT() + '}\n'
    snippet_end =  '$ {' +  POP_CONTEXT() + '}\n'
    pattern_store = \
        '%d {' +\
        PUSH() +\
        STORE_FAST('%s') +\
        LOAD_FAST('%s') +\
        POP() +\
        '}\n'
    pattern_load = \
        '%d {' +\
        LOAD_FAST('%s') +\
        POP() +\
        '}\n'
    snippet = '\n'.join([snippet_begin] +
                        [pattern_store % (n, s, s, s, s) for n,s in zip(range(1, nvars+1), lvars)] +
                        [pattern_load % (n, s, s) for n,s in zip(range(nvars+1, nvars+11), lvars)] +
                        [snippet_end])
    return snippet

def test_context_2():
    # Input  PS:
    # Output PS:
    nvars = 10
    inplist = list()
    outlist = list()
    numlist = [random_ndigits(10) for n in range(1, nvars+1)]
    for x in numlist:
        inplist.append('%d' % x)
        outlist.append('%d' % x)
    for x in numlist:
        inplist.append('pop')
        outlist.append('%d' % x)
    test_gen('func_context_2', func_context_2, inplist, outlist)


def func_context_3():
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
    return normalize(snippet)

def test_context_3():
    inplist = ['0']
    outlist = ['@;z;3;y;2;x;1']
    test_gen('func_context_3', func_context_3, inplist, outlist)


def test_cmp_1():
    # Input  PS: M;N;
    # Output PS: < or = or >
    inplist = list()
    outlist = list()
    for a in range(100):
        for b in range(100):
            inplist.append('%d;%d;' % (a, b))
            outlist.append('%s' % '<' if a < b else '=' if a == b else '>')
    test_gen('CMP_1', CMP, inplist, outlist)

def test_cmp_2():
    # Input  PS: M;N;
    # Output PS: < or = or >
    inplist = list()
    outlist = list()
    for p in range(1, 100):
        for q in range(1, 100):
            a = random.randint(10 ** (p-1), 10 ** p)
            b = random.randint(10 ** (q-1), 10 ** q)
            inplist.append('%d;%d;' % (a, b))
            outlist.append('%s' % '<' if a < b else '=' if a == b else '>')
    test_gen('CMP_2', CMP, inplist, outlist)


def test_fulladd():
    # Input  PS: abcX with c = 0 or 1
    # Output PS: rX   with r = a + b + c padded on two digits
    inplist = list()
    outlist = list()
    for a in range(10):
        for b in range(10):
            for c in range(2):
                rest = random_content()
                inplist.append('%d%d%d%s' % (a, b, c, rest))
                outlist.append('%02d%s' % (a + b + c, rest))
    test_gen('FULLADD', FULLADD, inplist, outlist)


def test_fullsub():
    # Input  PS: abcX with c = 0 or 1
    # Output PS: xyX  with if b+c <= a, x = 0, y = a-(b+c)
    #                      if b+c >  a, x = 1, y = 10+a-(b+c)
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
    test_gen('FULLSUB', FULLSUB, inplist, outlist)


def test_uadd():
    # Input  PS: M;N;
    # Output PS: R;   with R = M+N
    inplist = list()
    outlist = list()
    for a in range(101):
        for b in range(101):
            inplist.append('%d;%d;' % (a, b))
            outlist.append('%d;' % (a + b,))
    for n in range(100):
        a = random.randint(0, 10 ** 10)
        b = random.randint(0, 10 ** 10)
        inplist.append('%d;%d;' % (a, b))
        outlist.append('%d;' % (a + b,))

    test_gen('UADD', UADD, inplist, outlist)


def test_usub_1():
    # Input  PS: M;N;
    # Output PS: R;   with R = M-N
    inplist = list()
    outlist = list()
    for a in range(101):
        for b in range(a + 1):
            inplist.append('%d;%d;' % (a, b))
            outlist.append('%d;' % (a - b,))
    test_gen('USUB_1', USUB, inplist, outlist)

def test_usub_2():
    # Input  PS: M;N;
    # Output PS: R;   with R = M-N
    inplist = list()
    outlist = list()
    for n in range(100):
        a = random.randint(0, 10 ** 10)
        b = random.randint(0, a + 1)
        inplist.append('%d;%d;' % (a, b))
        outlist.append('%d;' % (a - b,))
    test_gen('USUB_2', USUB, inplist, outlist)

def test_usub_3():
    # Input  PS: M;N;
    # Output PS: R;   with R = M-N
    inplist = list()
    outlist = list()
    for n in range(100):
        a = random.randint(0, 10 ** n)
        b = a
        inplist.append('%d;%d;' % (a, b))
        outlist.append('%d;' % (a - b,))
    test_gen('USUB_3', USUB, inplist, outlist)


def test_fullmul():
    # Input  PS: abcX with a, b and c = 0 to 9
    # Output PS: rX   with r = a * b + c padded on two digits
    inplist = list()
    outlist = list()
    for a in range(10):
        for b in range(10):
            for c in range(10):
                rest = random_content()
                inplist.append('%d%d%d%s' % (a, b, c, rest))
                outlist.append('%02d%s' % (a * b + c, rest))
    test_gen('FULLMUL', FULLMUL, inplist, outlist)


def test_mulbydigit():
    # Input  PS: aN;X with a = 0 to 9
    # Output PS: R;X
    inplist = list()
    outlist = list()
    for d in range(10):
        for n in range(100):
            a = random.randint(0, 10 ** 10)
            rest = random_content()
            inplist.append('%d%d;%s' % (d, a, rest))
            outlist.append('%d;%s' % (d * a, rest))

    test_gen('MULBYDIGIT', MULBYDIGIT, inplist, outlist)


def test_umul_1():
    # Input  PS: M;N;
    # Output PS: R   with R = M*N
    inplist = list()
    outlist = list()
    for a in range(101):
        for b in range(101):
            inplist.append('%d;%d;' % (a, b))
            outlist.append('%d' % (a * b,))
    test_gen('UMUL_1', UMUL, inplist, outlist)

def test_umul_2():
    # Input  PS: M;N;
    # Output PS: R   with R = M*N
    inplist = list()
    outlist = list()
    for a in range(10):
        for b in range(101):
            x = random.randint(10 ** b, 10 ** (b + 1))
            inplist.append('%d;%d;' % (a, x))
            outlist.append('%d' % (a * x,))
            inplist.append('%d;%d;' % (x, a))
            outlist.append('%d' % (x * a,))
    test_gen('UMUL_2', UMUL, inplist, outlist)

def test_umul_3():
    # Input  PS: M;N;
    # Output PS: R   with R = M*N
    inplist = list()
    outlist = list()
    for n in range(100):
        a = random.randint(0, 10 ** 10)
        b = random.randint(0, 10 ** 10)
        inplist.append('%d;%d;' % (a, b))
        outlist.append('%d' % (a * b,))
    test_gen('UMUL_3', UMUL, inplist, outlist)

def test_umul_4():
    # Input  PS: M;N;
    # Output PS: R   with R = M*N
    inplist = list()
    outlist = list()
    for n in range(10):
        a = random.randint(0, 10 ** 100)
        b = random.randint(0, 10 ** 100)
        inplist.append('%d;%d;' % (a, b))
        outlist.append('%d' % (a * b,))
    test_gen('UMUL_4', UMUL, inplist, outlist)

def test_umul_5():
    # Input  PS: M;N;
    # Output PS: R   with R = M*N
    inplist = list()
    outlist = list()
    r = 1
    for n in range(100):
        inplist.append('%d;%d;' % (n, r))
        outlist.append('%d' % (n * r,))
        r *= n
    test_gen('UMUL_5', UMUL, inplist, outlist)

def test_umul_6():
    # Input  PS: M;N;
    # Output PS: R   with R = M*N
    inplist = list()
    outlist = list()
    r = 1
    for n in range(100):
        inplist.append('%d;%d;' % (r, 2))
        outlist.append('%d' % (r * 2,))
        r *= 2
    test_gen('UMUL_6', UMUL, inplist, outlist)

def test_umul_7():
    # Input  PS: M;N;
    # Output PS: R   with R = M*N
    inplist = list()
    outlist = list()
    for a in range(1, 10):
        for b in range(1, 10):
            for n in range(1, 10):
                x = int(str(a) * n)
                y = int(str(b) * n)
                inplist.append('%d;%d;' % (x, y))
                outlist.append('%d' % (x * y,))
    test_gen('UMUL_7', UMUL, inplist, outlist)


def test_divby2_1():
    # Input  PS: N;X
    # Output PS: R;X  with R = N // 2
    # N takes all values in [0, 99]
    inplist = list()
    outlist = list()
    for n in range(0, 100):
        s = random_content()
        inplist.append('%d;%s' % (n, s))
        outlist.append('%d;%s' % (n // 2, s))
    test_gen('DIVBY2_1', DIVBY2, inplist, outlist)

def test_divby2_2():
    # Input  PS: N;X
    # Output PS: R;X  with R = N // 2
    # N takes 100 big integer values
    inplist = list()
    outlist = list()
    for _ in range(0, 100):
        n = random_ndigits(random.randint(100, 200))
        s = random_content()
        inplist.append('%d;%s' % (n, s))
        outlist.append('%d;%s' % (n // 2, s))
    test_gen('DIVBY2_2', DIVBY2, inplist, outlist)


def test_odd():
    # Input  PS: N;X
    # Output PS: R;X  with R = N // 2
    # N takes all values in [0, 99]
    inplist = list()
    outlist = list()
    for n in range(0, 100):
        s = random_content()
        inplist.append('%d;%s' % (n, s))
        outlist.append('%d;%s' % (n % 2, s))
    test_gen('ODD_1', ODD, inplist, outlist)


def test_gen(descr, func, inplist, outlist):
    with open('test.sed', 'w') as f:
        print>>f, func()

    with open('test.input', 'w') as f:
        for line in inplist:
            print>>f, line

    with open('test.output', 'w') as f:
        for line in outlist:
            print>>f, line

    com = 'sed -r -f %s %s' % ('test.sed', 'test.input')

    # TODO: check sed in path
    res = subprocess.check_output(com).splitlines()

    print descr
    for inp, out, res in zip(inplist, outlist, res):
        # attention, ne compare pas si des lignes en plus
        if out != res:
            print '%-8s %-8s %-8s' % (inp, out, res)


def main():
    test_divby2_1()
    test_divby2_2()
    test_odd()
    test_context_0()
    test_context_1()
    test_context_2()
    test_context_3()
    test_cmp_1()
    test_cmp_2()
    test_fulladd()
    test_fullsub()
    test_uadd()
    test_usub_1()
    test_usub_2()
    test_usub_3()
    test_fullmul()
    test_mulbydigit()
    test_umul_1()
    test_umul_2()
    test_umul_3()
    test_umul_4()
    test_umul_5()
    test_umul_6()
    test_umul_7()
    test_divby2_1()
    test_divby2_2()
    test_odd()


if __name__ == "__main__":
    main()
