import re


def sedcode(opcode, function_labels_, return_labels_):
    global function_labels, return_labels

    function_labels = function_labels_
    return_labels = return_labels_ + ['EndOfScript']

    return normalize('\n'.join(opcode))


def normalize(snippet, replace=None, macros=None, functions=None):

    labels = []
    for line in snippet.splitlines():
        m = re.match(r' *:(\.\S+)', line)
        if m:
            labels.append(m.group(1))

    for label in labels:
        snippet = snippet.replace(label, new_label())

    if replace:
        for sfrom, sto in replace:
            # TODO: had to remove stating \b cf CALL_FUNCTION
            snippet = re.sub(r'%s\b' % sfrom, sto, snippet)

    macros = ('STARTUP', 'MAKE_FUNCTION', 'CALL_FUNCTION', 'BRANCH_ON_NAME',
              'MAKE_CONTEXT', 'POP_CONTEXT',
              'LOAD_CONST', 'LOAD_GLOBAL', 'STORE_GLOBAL', 'LOAD_NAME', 'STORE_NAME',
              'LOAD_FAST', 'STORE_FAST',
              'BINARY_ADD', 'BINARY_SUBTRACT', 'BINARY_MULTIPLY',
              'INPLACE_ADD', 'INPLACE_SUBTRACT',
              'COMPARE_OP', 'UNARY_NOT',
              'JUMP', 'POP_JUMP_IF_TRUE', 'POP_JUMP_IF_FALSE',
              'SETUP_LOOP', 'POP_BLOCK',
              'RETURN_VALUE',
              'PRINT_ITEM', 'PRINT_NEWLINE',
              'IS_POSITIVE', 'NEGATIVE', 'DIVIDE_BY_TEN', 'TRACE')

    macros += ('PUSH', 'POP', 'POP2', 'SWAP', 'CMP', 'UADD', 'USUB', 'UMUL',
               'FULLADD', 'FULLSUB', 'FULLMUL', 'MULBYDIGIT')

    for macro in macros:

        def repl(m):
            if not m.group(1):
                return globals()[macro]()
            else:
                args = m.group(1).split()
                return globals()[macro](*args)

        snippet = re.sub(r'\b%s\b *([^;#\n]*)' % macro, repl, snippet)

    if functions:
        # TODO
        pass

    snippet = snippet.replace('\\d', '[0-9]')
    return snippet


label_counter = 0
def new_label():
    global label_counter
    r = 'labelX%d' % label_counter
    label_counter += 1
    return r


# -- push/pop ---------------------------------------------------------------


PUSH = r'''                             # PS: N         HS: X
    G                                   # PS: N\nX      HS: X
    s/\n/;/                             # PS: N;X       HS: X
    h                                   # PS: N;X       HS: N;X
    s/;.*//                             # PS: N         HS: N;X
'''

def PUSH():
    return r'''                         # PS: N         HS: X
        G                               # PS: N\nX      HS: X
        s/\n/;/                         # PS: N;X       HS: X
        h                               # PS: N;X       HS: N;X
        s/;.*//                         # PS: N         HS: N;X
    '''

def PUSH():
    snippet = r'''                      # PS: N         HS: X
        G                               # PS: N\nX      HS: X
        s/\n/;/                         # PS: N;X       HS: X
        h                               # PS: N;X       HS: N;X
        s/;.*//                         # PS: N         HS: N;X
        '''
    return snippet

def POP():
    snippet = r'''                      # PS: ?         HS: N;X
        g                               # PS: N;X       HS: N;X
        s/^[^;]*;//                     # PS: X         HS: N;X
        x                               # PS: N;X       HS: X
        s/;.*//                         # PS: N         HS: X
        '''
    return snippet

def PUSH2():
    snippet = r'''                      # PS: M;N       HS: X
        G                               # PS: M;N\nX    HS: X
        s/\n/;/                         # PS: M;N;X     HS: X
        h                               # PS: M;N;X     HS: M;N;X
        s/^([^;]*;[^;]*);.*/\1/         # PS: M;N       HS: M;N;X
        '''
    return snippet

def POP2():
    snippet = r'''                      # PS: ?         HS: M;N;X
        g                               # PS: M;N;X     HS: M;N;X
        s/^[^;]*;[^;]*;//               # PS: X         HS: M;N;X
        x                               # PS: M;N;X     HS: X
        s/(^[^;]*;[^;]*).*/\1/          # PS: M;N       HS: X
        '''
    return snippet

def SWAP():
    snippet = r'''                      # PS: ?         HS: M;N;X
        x                               # PS: M;N;X     HS: ?
        s/^([^;]*;)([^;]*;)/\2\1/       # PS: N;M;X     HS: ?
        x                               # PS: ?         HS: N;M;X
    '''
    return snippet


# -- Constants --------------------------------------------------------------


LOAD_CONST = r'''                       # PS: ?         HS: X
    g                                   # PS: X         HS: X
    s/^/{const};/                       # PS: const;X   HS: X
    h                                   # PS: const;X   HS: const;X
'''

def LOAD_CONST(const):
    snippet = r'''                      # PS: ?         HS: X
        g                               # PS: X         HS: X
        s/^/const;/                     # PS: const;X   HS: X
        h                               # PS: const;X   HS: const;X
    '''
    return snippet.replace('const', const)


# -- Name spaces -------------------------------------------------------------


def STARTUP():
    snippet = '''
        x
        s/.*/@/
        x
        b.start
        :EndOfScript
        q
        :NameError
        s/.*/NameError: name & is not defined/
        p
        q
        :UnknownLabel
        s/.*/UnknownLabel: label & is not defined/
        p
        q
        :.start
    '''
    return snippet

def MAKE_CONTEXT():
    snippet = '''
        x
        s/$/|/
        x
    '''
    return snippet

def POP_CONTEXT():
    snippet = '''
        x
        s/[|][^|]*$//
        x
    '''
    return snippet


def LOAD_GLOBAL(name):
    # TOS = val(name)
    snippet = r'''                      # PS: ?         HS: ?;v;x?
        g                               # PS: ?;v;x?    HS: ?;v;x?
        /@[^|]*;name;/! { s/.*/name/; b NameError }
                                        # branch to error if var undefined
        s/[^@]*@[^|]*;name;([^;|]*).*/\1;&/   # PS: x;?;v;x?  HS: ?;v;x?
        h                               # PS: x;?;v;x?  HS: x;?;v;x?
    '''
    return snippet.replace('name', name)


def STORE_GLOBAL(name):
    # name = POP() (cf cpython/ceval.c)
    snippet = r'''                      # PS: ?         HS: x;X
        g                               # PS: x;X       HS: ?
        t.reset_t
        :.reset_t
        s/^([^;]*);([^@]*@[^|]*;name;)[^;]*/\2\1/
                                        # PS: X;v;x     HS: ?
        t.next
        s/^([^;]*);([^@]*@)/\2;name;\1/ # PS: X;v;x     HS: ?
        :.next
        h                               # PS: ?         HS: X;v;x
    '''
    return normalize(snippet, replace=(('name', name),))

def DELETE_GLOBAL(name):
    snippet = r'''                      # PS: ?         HS: x;X
        g                               # PS: x;X       HS: ?
        s/(@[^|]*);name;[^;|]*(.*)/\1\2/
                                        # PS: x;X'      HS: ? (del ;var;val in PS)
        h                               # PS: ?         HS: x;X';v;x
    '''
    return snippet.replace('name', name)


STORE_NAME = STORE_GLOBAL
LOAD_NAME = LOAD_GLOBAL


def LOAD_FAST(name):
    # TOS = val(name)
    snippet = r'''                      # PS: ?         HS: ?;v;x?
        g                               # PS: ?;v;x?    HS: ?;v;x?
        /[|][^|]*;name;[^|]*/! s/.*/0;&/
                                        # PS: 0 if var undefined
                                        # TODO: should be error
        s/.*[|][^|]*;name;([^;]*)[^|]*$/\1;&/
                                        # PS: x;?;v;x?  HS: ?;v;x?
        h                               # PS: ?         HS: x;?;v;x?
    '''
    return snippet.replace('name', name)

def STORE_FAST(name):
    # TODO: code without DELETE, see STORE_GLOBAL
    # name = POP() (cf cpython/ceval.c)
    # TODO: make sure there is a test with var in last position
    snippet = r'''                      # PS: ?         HS: x;X
        g                               # PS: x;X       HS: ?
        s/([^;]*);(.*)/\2;name;\1/      # PS: X';v;x    HS: ?
        h                               # PS: ?         HS: X';v;x
    '''
    return DELETE_FAST(name) + snippet.replace('name', name)

def DELETE_FAST(name):
    snippet = r'''                      # PS: ?         HS: x;X
        g                               # PS: x;X       HS: ?
        s/([|][^|]*);name;[^;|]*([^|]*)/\1\2/
                                        # PS: x;X'      HS: ? (del ;var;val in PS)
        h                               # PS: ?         HS: x;X';v;x
    '''
    return snippet.replace('name', name)


# -- Functions ---------------------------------------------------------------


def MAKE_FUNCTION(x):
    return ''


def CALL_FUNCTION(argc, return_label):
    if int(argc) >= 256:
        # do not handle keyword parameters
        print('[%s]' % argc)
        raise Exception('numsed: keyword parameters not handled')
    # argc parameters on top of stack above name of function
    # first, swap parameters and name
    snippet = r'''
        x
        s/^(([^;]+;){argc})([^;]+;)/\3\1return_label;/
        x
        POP
        ''' + BRANCH_ON_NAME(function_labels)
    snippet2 = normalize(snippet, replace=(('argc', argc),('return_label', return_label)))
    return snippet2


def RETURN_VALUE():
    snippet = 'SWAP\n' + 'POP\n' + BRANCH_ON_NAME(return_labels)
    return normalize(snippet)


def BRANCH_ON_NAME(labels):
    snippet = '''                       # HS: label;X
        s/^//                           # force a substitution to reset t flag
        t.test_return                   # t to next line to reset t flag
        :.test_return
    '''
    snippet = normalize(snippet)
    snippet += '\n'.join(('s/^%s$//;t %s' % (label, label) for label in labels))
    snippet += '\nb UnknownLabel'

    return snippet


# -- Compare operators and jumps ---------------------------------------------


def CMP():
    snippet = r'''                      # PS: X;Y;
        s/;/!;/g                        # PS: X!;Y!;
        :.loop                          # PS: Xx!X';Yy!Y';
        s/(\d)!(\d*;\d*)(\d)!/!\1\2!\3/ # PS: X!xX';Y!yY';
        t.loop
        /^!/!b.gt
        /;!/!b.lt
                                        # PS: !X;!Y;
        s/^!(\d*)(\d*);!\1(\d*);/\2;\3;/# strip identical leading digits
        /^;;$/ { s/.*/=/; b.end }       # PS: = if all digits are equal

        s/$/9876543210/
        /^(.)\d*;(.)\d*;.*\1.*\2/b.gt
        :.lt
        s/.*/</                         # PS: < if x < y
        b.end
        :.gt
        s/.*/>/                         # PS: > if x > y
        :.end                            # PS: <|=|>
    '''
    return normalize(snippet)


def COMPARE_OP(opname):
    snippet = '''
        SWAP
        POP2
        s/$/;/
        CMP
        y/<=>/xyz/
        PUSH
    '''
    conv = {'==': '010', '!=': '101', '<': '100', '<=': '110', '>': '001', '>=': '011'}
    snippet = snippet.replace('xyz', conv[opname])
    return normalize(snippet)


def UNARY_NOT():
    snippet = '''
        g
        s/^0;/!;/                       # use marker to avoid another substitution
        s/^\d+/0/
        s/^!/1/
        h
    '''
    return snippet


def POP_JUMP_IF_TRUE(target):
    snippet = 'POP; /^1$/b ' + target
    return normalize(snippet, macros=('POP',))


def POP_JUMP_IF_FALSE(target):
    snippet = 'POP; /^0$/b ' + target
    return normalize(snippet)


def JUMP(target):
    return 'b ' + target


def SETUP_LOOP(_):
    return ''


def POP_BLOCK():
    return ''


# -- Printing ----------------------------------------------------------------


def PRINT_ITEM():
    snippet = r'''
                                        # PS: ?         HS: N;X
        POP                             # PS: N         HS: X
        p
     '''
    return normalize(snippet)

def PRINT_NEWLINE():
    return ''


# - Addition and subtraction -------------------------------------------------


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
        :.loop                           # PS: cR;Mm;Nn;*
        s/^(\d*);(\d*)(\d);(\d*)(\d)/\3\5\1;\2;\4/
                                        # PS: mncR;M;N;*
        FULLADD                         # PS: abR;M;N;*
        /^\d*;\d*\d;\d/b.loop           # more digits in M and N
        /^\d*;;;/{                      # no more digits in M and N
            s/;;;//
            s/^0//
            b.exit
        }
        /^1/{
            s/;;/;0;/
            b.loop
        }
        s/^0(\d*);(\d*);(\d*);/\2\3\1/
        :.exit                           # PS: R*
    '''
    return normalize(snippet)


def USUB():
    snippet = r'''
                                        # PS: M;N*
        s/\d*;\d*/0;&;/                 # PS; 0;M;N;*
        :.loop                           # PS: cR;Mm;Nn;*
        s/(\d*);(\d*)(\d);(\d*)(\d);/\3\5\1;\2;\4;/
                                        # PS: mncR;M;N;*
        FULLSUB                         # PS: c'rR;M;N;*
        /^\d*;\d*\d;\d/ b.loop          # more digits in M and N
        /^\d*;;\d/b.nan                 # more digits in N
        /^1\d*;;;/b.nan                 # same number of digits, but borrow
        /^1/{                           # if borrow,
            s/^1(\d*;\d*);;/0\1;1;/     # move borrow to second operand
            b.loop                      # and loop
        }
        s/^0(\d*);(\d*);;/\2\1/         # add remaining part of first operand
        s/^0*(\d)/\1/                   # del leading 0
        b.end
        :.nan                            # if invalid subtraction
        s/^\d*;\d*;\d*;/NAN/            # PS: NAN*
        :.end                            # PS: M-N|NAN
     '''
    return normalize(snippet)


def BINARY_ADD():
    """
    Implements TOS = TOS1 + TOS on unsigned integers (R = N + M).
    """
    snippet = r'''                      # PS: ?         HS: M;N;X
        POP2                            # PS: M;N;      HS: X
        UADD                            # PS: R         HS: X
        PUSH                            # PS: R         HS: R;X
     '''
    return normalize(snippet)

def BINARY_SUBTRACT():
    """
    Implements TOS = TOS1 - TOS on unsigned integers (R = N - M).
    """
    snippet = r'''                      # PS: ?         HS: M;N;X
        SWAP
        POP2                            # PS: M;N;      HS: X
        USUB                            # PS: R         HS: X
        PUSH                            # PS: R         HS: R;X
     '''
    return normalize(snippet)


INPLACE_ADD = BINARY_ADD
INPLACE_SUBTRACT = BINARY_SUBTRACT


# -- Multiplication ----------------------------------------------------------


def FULLMUL(): # dc.sed version
    # Multiply two digits with carry
    #
    # Input  PS: abcX with a, b and c = 0 to 9
    # Output PS: rX   with r = a * b + c padded on two digits
    snippet = r'''
        /^(0.|.0)/ {
            s/^../0/
            b.exit
        }
        s/(...)/\1;9876543210aaaaaaaaa;9876543210aaaaaaaaa;/
        s/(.)(.)(.);\d*\2.{9}(a*);\d*\3.{9}(a*);/\19\48\47\46\45\44\43\42\41\40\5;/
        s/(.)[^;]*\1(.*);/\2;/
        s/a\d/a/g
        s/a{10}/b/g
        s/(b*)(a*)/\19876543210;\29876543210/
        s/.{9}(.)\d*;.{9}(.)\d*;/\1\2/
        :.exit
    '''
    return normalize(snippet)


def MULBYDIGIT():
    # Input  PS: aN;X with a = 0 to 9
    # Output PS: R;X
    snippet = r'''                      # PS: aNX
        s/(.)(\d*)/0;\1;\2;/
        :.loop
        s/(\d*);(\d);(\d*)(\d)/\2\4\1;\2;\3/
        FULLMUL
        /^\d*;\d;\d/b.loop
        s/;\d;;//                       # PS: RX
        s/^0*(\d)/\1/
    '''
    return normalize(snippet)


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
        :.loop                           # PS: P;S;A;Mm;
                                        # P partial result to add, S last digits
        s/(\d*;\d*;(\d*;)\d*)(\d)/\3\2\1/
                                        # PS: mA;P;S;A;M;
        MULBYDIGIT                      # PS: B;P;S;A;M; (B = m * A)
        UADD                            # PS: R;S;A;M    (R = B + P)
                                        # PS: Rr;S;A;M;
        s/(\d);/;\1/                    # PS: R;rS;A;M;
        s/^;/0;/                        # R is the partial result to add, if empty put 0
        /\d; *$/b.loop                  # Loop if still digits in M
                                        # PS: R;S;A;;
        s/(\d*);(\d*).*/\1\2/           # PS: RS
        s/^0*(.)/\1/                    # Normalize leading zeros
    '''
    return normalize(snippet)


def BINARY_MULTIPLY():
    snippet = r'''
                                        # PS: ?         HS: M;N;X
        POP2                            # PS: M;N;      HS: X
        s/$/;/
        UMUL                            # PS: R         HS: X
        PUSH                            # PS: R         HS: R;X
     '''
    return normalize(snippet)


def BINARY_FLOOR_DIVIDE():
    # not implemented in sed, implemented in python
    return ''


# -- Helper opcodes ----------------------------------------------------------


def IS_POSITIVE():
    snippet = r'''                      # PS: ?         HS: N;X
        g                               # PS: N;X       HS: N;X
        s/^[0-9+][^;]*/1/               # PS: 1;X       HS: N;X  if pos
        s/^-[^;]+/0/                    # PS: 0;X       HS: N;X  if neg
        h                               # PS: r;X       HS: r;X  r = 0 or 1
        '''
    return snippet


def NEGATIVE():
    snippet = r'''                      # PS: ?         HS: N;X
        g                               # PS: N;X       HS: N;X
        s/^-/!/                         # use marker to avoid another substitution
        s/^\+/-/                        #
        s/^[0-9]/-&/                    #
        s/^-0;/0;/
        s/^!//                          # remove marker
        h                               # PS: R;X       HS: R;X  R = -N
        '''
    return snippet


def DIVIDE_BY_TEN():
    snippet = r'''                      # PS: ?         HS: N;X
        g                               # PS: N;X       HS: N;X
        s/[0-9];/;/                     # remove last digit
        s/^;/0;/                        # R = 0 if single digit input
        h                               # PS: R;X       HS: R;X  R = N // 10
        '''
    return snippet


# -- Debug -------------------------------------------------------------------


def TRACE(msg):
    snippet = '''
        i msg
        p
        x
        p
        x
    '''
    #return ''
    return snippet.replace('msg', msg)
