import sys
import dis
import subprocess

# https://docs.python.org/2/library/dis.html
# http://www.goldsborough.me/python/low-level/2016/10/04/00-31-30-disassembling_python_bytecode/


def normalize(snippet, labels=None, macros=None):
    if labels:
        for label in labels:
            snippet = snippet.replace(label, new_label())

    if macros:
        for macro in macros:
            snippet = snippet.replace(macro, globals()[macro]())

    snippet = snippet.replace('\\d', '[0-9]')
    return snippet

label_counter = 0
def new_label():
    global label_counter
    r = 'label%d' % label_counter
    label_counter += 1
    return r


def LOAD_CONST(const):
    snippet = r'''                      # PS: ?         HS: X
        s/.*/const/                     # PS: const     HS: X
        G                               # PS: const\nX  HS: X
        s/\n/;/                         # PS: const;X   HS: X
        h                               # PS: ?         HS: const;X
    '''
    return replace('const', const, snippet)


def LOAD_NAME(name):
    snippet = r'''                      # PS: ?         HS: ?;v;x?
        g                               # PS: ?;v;x?    HS: ?;v;x?
        /;name;/! s/.*/0/               # PS: 0 if var undefined
        s/(^.*;name;([^;]*).*)/\2;\1/   # PS: x;?;v;x?  HS: ?;v;x?
        h                               # PS: ?         HS: x;?;v;x?
    '''
    return replace('name', name, snippet)


def STORE_NAME(name):
    # name = TOS
    snippet = r'''                      # PS: ?         HS: x;X
        g                               # PS: x;X       HS: ?
        s/;name;[^;]*//                 # PS: x;X'      HS: ? (del ;var;val in PS)
        s/([^;]*).*/&;name;\1/          # PS: x;X';v;x  HS: ?
        h                               # PS: ?         HS: x;X';v;x
    '''
    return replace('name', name, snippet)



def CMP():
    snippet = r'''                      # PS: X;Y;
        s/;/!;/g                        # PS: X!;Y!;
        :loop                           # PS: Xx!X';Yy!Y';
        s/(\d)!(\d*;\d*)(\d)!/!\1\2!\3/ # PS: X!xX';Y!yY';
        tloop
        /^!/!bgt
        /;!/!blt
                                        # PS: !X;!Y;
        s/^!(\d*)(\d*);!\1(\d*);/\2;\3;/# strip identical leading digits
        /^;;$/ { s/.*/=/; bend }        # PS: 1 if all digits are equal

        s/$/9876543210/
        /^(.)\d*;(.)\d*;.*\1.*\2/bgt
        :lt
        s/.*/</                         # PS: 0 if x < y
        bend
        :gt
        s/.*/>/                         # PS: 2 if x > y
        :end                            # PS: 0|1|2
    '''
    return normalize(snippet, labels=('loop', 'gt', 'lt', 'end'))

def COMPARE_OP(opname):
    if opname == 'EQ':
        snippet = 'LOAD_TOP2; CMP; y/<=>/010/; PUSH'
    elif opname == 'NE':
        snippet = 'LOAD_TOP2; CMP; y/<=>/101/; PUSH'
    elif opname == 'LT':
        snippet = 'LOAD_TOP2; CMP; y/<=>/100/; PUSH'
    elif opname == 'LE':
        snippet = 'LOAD_TOP2; CMP; y/<=>/110/; PUSH'
    elif opname == 'GT':
        snippet = 'LOAD_TOP2; CMP; y/<=>/001/; PUSH'
    elif opname == 'GE':
        snippet = 'LOAD_TOP2; CMP; y/<=>/011/; PUSH'
    return snippet


def POP_JUMP_IF_TRUE(target):
    snippet = 'LOAD_TOP; /^1$/b ' + target
    return snippet

def POP_JUMP_IF_FALSE(target):
    snippet = 'LOAD_TOP; /^0$/b ' + target
    return snippet


def HALFADD():
    snippet = r'''
        s/^(..)/&;9876543210;9876543210;/
        s/(.)(.);\d*\1(\d*);\d*(\2\d*);/\3\49876543210;/
        s/.{10}(.)\d{0,9}(\d{0,1})\d*;/0\2\1;/
        /^0\d(\d);/s//1\1;/
        s/;//
    '''
    return normalize(snippet)

def FULLADD():
    # Add two left digits with carry
    #
    # Input  PS: abcX with c = 0 or 1
    # Output PS: rX   with r = a + b + c padded on two digits
    snippet = r'''
        s/^(...)/\1;9876543210;9876543210;/
        s/^(..)0/\1/
        s/(.)(.)(\d)*;(\d*\1(\d*));\d*(\2\d*);/\3\5\6\4;/
        s/.{10}(.)\d{0,9}(\d{0,1})\d*;/0\2\1;/
        /^0\d(\d);/s//1\1;/
        s/;//
    '''
    return normalize(snippet)

def FULLSUB():
    # Subtract two left digits with borrow
    #
    # Input  PS: abcX with c = 0 or 1
    # Output PS: xyX  with if b+c <= a, x = 0, y = a-(b+c)
    #                      if b+c >  a, x = 1, y = 10+a-(b+c)
    snippet = r'''
        s/^(...)/\1;9876543210;0123456789;/
        s/^(..)0/\1/
        s/(.)(.)(\d*);\d*\2(\d*);(\d*(\1\d*));/\3\4\6\5;/
        s/.{10}(.)\d{0,9}(\d{0,1})\d*;/0\2\1;/
        /^0\d(\d);/s//1\1;/
        s/;//
    '''
    return normalize(snippet)


def FULLADD2():
    snippet = r'''
        s/^(...)/\19876543210aaaaaaaaa;9876543210aaaaaaaaa;10a;/
        s/(.)(.)(.)\d*\1.{9}(a*);\d*\2.{9}(a*);\d*\3.(a*);/\4\5\6/
        s/a{10}/b/
        s/(b*)(a*)/\19876543210;\29876543210;/
        s/.{9}(.)\d*;.{9}(.)\d*;/\1\2/
        '''
    return snippet


def UADD():
    snippet = r'''
                                        # PS: M;N*
        s/\d*;\d*/0;&;/                 # PS; 0;M;N;*
        :loop                           # PS: cR;Mm;Nn;*
        s/^(\d*);(\d*)(\d);(\d*)(\d)/\3\5\1;\2;\4/
                                        # PS: mncR;M;N;*
        FULLADD                         # PS: abR;M;N;*
        /^\d*;\d*\d;\d/b loop           # more digits in M and N
        /^\d*;;;/{                      # no more digits in M and N
            s/;;;//
            s/^0//
            b exit
        }
        /^1/{
            s/;;/;0;/
            b loop
        }
        s/^0(\d*);(\d*);(\d*);/\2\3\1/
        :exit                           # PS: R*
    '''
    return normalize(snippet, labels=('loop', 'exit'), macros=('FULLADD',))


def USUB():
    snippet = r'''
                                        # PS: M;N*
        s/(\d*;\d*)/0;&;/               # PS; 0;M;N;*
        :loop                           # PS: cR;Mm;Nn;*
        s/(\d*);(\d*)(\d);(\d*)(\d);/\3\5\1;\2;\4;/
                                        # PS: mncR;M;N;*
        FULLSUB                         # PS: c'rR;M;N;*
        /^\d*;\d*\d;\d/ b loop          # more digits in M and N
        /^\d*;;\d/b nan                 # more digits in N
        /^1\d*;;;/b nan                 # same number of digits, but borrow
        /^1/{                           # if borrow,
            s/^1(\d*;\d*);;/0\1;1;/     # move borrow to second operand
            b loop                      # and loop
        }
        s/^0(\d*);(\d*);;/\2\1/         # add remaining part of first operand
        s/^0*(\d)/\1/                   # del leading 0
        b end
        :nan                            # if invalid subtraction
        s/^\d*;\d*;\d*;/NAN/            # PS: NAN*
        :end                            # PS: M-N|NAN
     '''
    return normalize(snippet, labels=('loop', 'nan', 'end'), macros=('FULLSUB',))


def sign_add(x, y):
    if x > 0:
        if y > 0:
            r = x + y
        else:
            y = -y
            if x > y:
                r = x - y
            else:
                r = -(y - x)
    else:
        x = -x
        if y > 0:
            if x > y:
                r = -(x - y)
            else:
                r = y - x
        else:
            y = -y
            r = -(x + y)
    return r


def FULLMUL(): # dc.sed version
    # Multiply two digits with carry
    #
    # Input  PS: abcX with a, b and c = 0 to 9
    # Output PS: rX   with r = a * b + c padded on two digits
    snippet = r'''
        /^(0.|.0)/ {
            s/^../0/
            b exit
        }
        s/(...)/\1;9876543210aaaaaaaaa;9876543210aaaaaaaaa;/
        s/(.)(.)(.);\d*\2.{9}(a*);\d*\3.{9}(a*);/\19\48\47\46\45\44\43\42\41\40\5;/
        s/(.)[^;]*\1(.*);/\2;/
        s/a\d/a/g
        s/a{10}/b/g
        s/(b*)(a*)/\19876543210;\29876543210/
        s/.{9}(.)\d*;.{9}(.)\d*;/\1\2/
        :exit
    '''
    return normalize(snippet, labels=('exit',))


def MULBYDIGIT():
    # Input  PS: aN;X with a = 0 to 9
    # Output PS: R;X
    snippet = r'''                      # PS: aNX
        s/(.)(\d*)/0;\1;\2;/
        :loop
        s/(\d*);(\d);(\d*)(\d)/\2\4\1;\2;\3/
        FULLMUL
        /^\d*;\d;\d/b loop
        s/;\d;;//                       # PS: RX
        s/^0*(\d)/\1/
    '''
    return normalize(snippet, labels=('loop',), macros=('FULLMUL',))


def UMUL(a, b):
    r = 0
    m = 1
    while b > 0:
        digit = b % 10
        b = b / 10
        r += m * digit * a
        m *= 10
    return r

def UMUL():
    snippet = r'''                      # PS: A;M;
        s/^/0;;/                        # PS: 0;;A;M;
        :loop                           # PS: P;S;A;Mm;
                                        # P partial result to add, S last digits
        s/(\d*;\d*;(\d*;)\d*)(\d)/\3\2\1/
                                        # PS: mA;P;S;A;M;
        MULBYDIGIT                      # PS: B;P;S;A;M; (B = m * A)
        UADD                            # PS: R;S;A;M    (R = B + P)
                                        # PS: Rr;S;A;M;
        s/(\d);/;\1/                    # PS: R;rS;A;M;
        s/^;/0;/                        # R is the partial result to add, if empty put 0
        /\d; *$/b loop                  # Loop if still digits in M
                                        # PS: R;S;A;;
        s/(\d*);(\d*).*/\1\2/           # PS: RS
        s/^0*(.)/\1/                    # Normalize leading zeros
    '''
    return normalize(snippet, labels=('loop',), macros=('UADD', 'MULBYDIGIT',))


def euclide(a, b):
    # http://compoasso.free.fr/primelistweb/page/prime/euclide.php
    r = a
    q = 0
    n = 0
    aux = b

    while aux <= a:
        aux = aux * 2
        n += 1

    while n > 0:
        aux = aux / 2
        n -= 1
        q = q * 2
        if r >= aux:
            r -= aux
            q += 1

    return q, r


def decompfile(filename):
    with open(filename) as f:
        source = f.read()
    code = compile(source, filename, "exec")
    print dis.dis(code)

def test():
    #decompfile(sys.argv[1])
    #print dis.dis(euclide)
    #print CMP()
    #print euclide(17,3)
    #print MULBYDIGIT()
    #print 123456 * 567, UMUL(123456, 567)
    #print UMUL()
    pass


test()
