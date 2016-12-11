from cws import CMP, FULLADD, FULLSUB, UADD, USUB, FULLMUL, MULBYDIGIT, UMUL
import subprocess
import random


def random_content():
    x = [str(random.randint(0, 10 ** 10)) for n in range(random.randint(0, 10))]
    return ';'.join(x)


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
        if out != res:
            print '%-8s %-8s %-8s' % (inp, out, res)


def main():
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

main()
