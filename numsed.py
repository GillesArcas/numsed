import argparse
import sys
import os
import re
import dis
import subprocess
import inspect
from StringIO import StringIO  # Python2
#from io import StringIO  # Python3
import transformer


# AST
# https://greentreesnakes.readthedocs.io/en/latest/

# DST
# https://docs.python.org/2/library/dis.html
# http://unpyc.sourceforge.net/Opcodes.html
# http://www.goldsborough.me/python/low-level/2016/10/04/00-31-30-disassembling_python_bytecode/
# http://stackoverflow.com/questions/31989893/how-to-fully-disassemble-python-source
# http://www.aosabook.org/en/500L/a-python-interpreter-written-in-python.html
# https://github.com/python/cpython/blob/2bdba08bd0eb6f1b2a20d14558a4ea2009b46438/Python/ceval.c

# http://faster-cpython-zh.readthedocs.io/en/latest/registervm.html


def normalize(snippet, labels=None, replace=None, macros=None, functions=None):
    if labels:
        for label in labels:
            snippet = snippet.replace(label, new_label())

    if replace:
        for sfrom,sto in replace:
            snippet = snippet.replace(sfrom, sto)

    if macros:
        for macro in macros:
            #snippet = snippet.replace(macro, globals()[macro]())

            def repl(m):
                #print '(%s)' % m.group(1)
                if not m.group(1):
                    return globals()[macro]()
                else:
                    return globals()[macro](m.group(1))

            snippet = re.sub(r'%s *([^; #\n]*)' % macro, repl, snippet)

    if functions:
        # TODO
        pass

    snippet = snippet.replace('\\d', '[0-9]')
    return snippet


label_counter = 0
def new_label():
    global label_counter
    r = 'label%d' % label_counter
    label_counter += 1
    return r


# -- push/pop ---------------------------------------------------------------


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

def ROT_THREE():
    # TODO
    snippet = '''
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


# -- Constants --------------------------------------------------------------


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
        s/.*/-/
        x
        b start
        :NameError
        s/.*/NameError: name & is not defined/
        q
        :start
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
        /-[^|]*;name;/! { s/.*/name/; b NameError }
                                        # branch to error if var undefined
        s/-[^|]*;name;([^;]*).*/\1;&/   # PS: x;?;v;x?  HS: ?;v;x?
        h                               # PS: ?         HS: x;?;v;x?
    '''
    return snippet.replace('name', name)

def STORE_GLOBAL(name):
    # TODO: remove
    # name = POP() (cf cpython/ceval.c)
    snippet = r'''                      # PS: ?         HS: x;X
        g                               # PS: x;X       HS: ?
        s/([^;]*;)([^-]*-)/\2;name;\1/  # PS: X;v;x     HS: ?
        h                               # PS: ?         HS: X;v;x
    '''
    return DELETE_GLOBAL(name) + snippet.replace('name', name)

def STORE_GLOBAL(name):
    # name = POP() (cf cpython/ceval.c)
    snippet = r'''                      # PS: ?         HS: x;X
        g                               # PS: x;X       HS: ?
        t reset_t
        :reset_t
        s/^([^;]*);([^-]*-[^|]*;name;)[^;]*/\2\1/
                                        # PS: X;v;x     HS: ?
        t next
        s/^([^;]*);([^-]*-)/\2;name;\1/ # PS: X;v;x     HS: ?
        :next
        h                               # PS: ?         HS: X;v;x
    '''
    return normalize(snippet, labels=('reset_t', 'next'), replace=(('name', name),))

def DELETE_GLOBAL(name):
    snippet = r'''                      # PS: ?         HS: x;X
        g                               # PS: x;X       HS: ?
        s/(-[^|]*);name;[^;|]*(.*)/\1\2/
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
        s/.*[|][^|]*;name;([^;]*)[^|]*$/\1;&/
                                        # PS: x;?;v;x?  HS: ?;v;x?
        h                               # PS: ?         HS: x;?;v;x?
    '''
    return snippet.replace('name', name)

def STORE_FAST(name):
    # TODO: code without DELETE, see STORE_GLOBAL
    # name = POP() (cf cpython/ceval.c)
    snippet = r'''                      # PS: ?         HS: x;X
        g                               # PS: x;X       HS: ?
        s/([^;]*);(.*)/\2;name;\1/      # PS: X';v;x    HS: ?
        h                               # PS: ?         HS: X';v;x
    '''
    return DELETE_FAST(name) + snippet.replace('name', name)

def DELETE_FAST(name):
    snippet = r'''                      # PS: ?         HS: x;X
        g                               # PS: x;X       HS: ?
        s/([|][^|]*);name;[^;|]*;([^|]*)/\1\2/
                                        # PS: x;X'      HS: ? (del ;var;val in PS)
        h                               # PS: ?         HS: x;X';v;x
    '''
    return snippet.replace('name', name)


# -- Functions ---------------------------------------------------------------


def CALL_FUNCTION(argc):
    # TODO: return address to be handled
    if int(argc) >= 256:
        # do not handle keyword parameters
        print '[%s]' % argc
        raise Exception('numsed: keyword parameters not handled')
    # argc parameters on top of stack above name of function
    # first, swap parameters and name
    snippet = '''
        s/(([^;];){argc})([^;];)/\3\2/
        BRANCH_ON_NAME(function_labels)
        '''
    return normalize(snippet, replace=(('argc', argc),))


def RETURN():
    # TODO: remove
    # HS: label;X
    return_labels = X
    snippet = '''
        s/^//                           # force a substitution to enable t
        t test_return                   # t to next line to reset t flag
        :test_return
        s/^label1;//
        t label1
        s/^label2;//
        t label2
    '''
    return snippet


def RETURN_VALUE():
    return BRANCH_ON_NAME(return_labels)
    #return 's/.*//'


def BRANCH_ON_NAME(labels):
    snippet = '''                       # HS: label;X
        s/^//                           # force a substitution to enable t
        t test_return                   # t to next line to reset t flag
        :test_return
    '''
    snippet = normalize(snippet, labels=('test_return',))

    snippet += '\n'.join(('s/^%s;//;t %s' % (label, label) for label in labels))

    return snippet


# -- Printing ----------------------------------------------------------------


def PRINT_ITEM():
    snippet = r'''
                                        # PS: ?         HS: N;X
        POP                             # PS: N         HS: X
        p
     '''
    return normalize(snippet, macros=('POP',))

def PRINT_NEWLINE():
    return ''


# -- Compare operators -------------------------------------------------------


def CMP():
    snippet = r'''                      # PS: X;Y;
        s/;/!;/g                        # PS: X!;Y!;
        :loop                           # PS: Xx!X';Yy!Y';
        s/(\d)!(\d*;\d*)(\d)!/!\1\2!\3/ # PS: X!xX';Y!yY';
        t loop
        /^!/!b gt
        /;!/!b lt
                                        # PS: !X;!Y;
        s/^!(\d*)(\d*);!\1(\d*);/\2;\3;/# strip identical leading digits
        /^;;$/ { s/.*/=/; b end }       # PS: = if all digits are equal

        s/$/9876543210/
        /^(.)\d*;(.)\d*;.*\1.*\2/b gt
        :lt
        s/.*/</                         # PS: < if x < y
        b end
        :gt
        s/.*/>/                         # PS: > if x > y
        :end                            # PS: <|=|>
    '''
    return normalize(snippet, labels=('loop', 'gt', 'lt', 'end'))

def COMPARE_OP(opname):
    if opname == 'EQ':
        snippet = 'POP2; CMP; y/<=>/010/; PUSH'
    elif opname == 'NE':
        snippet = 'POP2; CMP; y/<=>/101/; PUSH'
    elif opname == 'LT':
        snippet = 'POP2; CMP; y/<=>/100/; PUSH'
    elif opname == 'LE':
        snippet = 'POP2; CMP; y/<=>/110/; PUSH'
    elif opname == 'GT':
        snippet = 'POP2; CMP; y/<=>/001/; PUSH'
    elif opname == 'GE':
        snippet = 'POP2; CMP; y/<=>/011/; PUSH'
    return snippet

def POP_JUMP_IF_TRUE(target):
    snippet = 'LOAD_TOP; /^1$/b ' + target
    return snippet

def POP_JUMP_IF_FALSE(target):
    snippet = 'LOAD_TOP; /^0$/b ' + target
    return snippet


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
        s/\d*;\d*/0;&;/                 # PS; 0;M;N;*
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


def BINARY_ADD():
    """
    Implements TOS = TOS1 + TOS on unsigned integers (R = N + M).
    """
    snippet = r'''                      # PS: ?         HS: M;N;X
        POP2                            # PS: M;N;      HS: X
        UADD                            # PS: R         HS: X
        PUSH                            # PS: R         HS: R;X
     '''
    return normalize(snippet, macros=('POP2', 'UADD', 'PUSH'))

def BINARY_SUBTRACT():
    """
    Implements TOS = TOS1 - TOS on unsigned integers (R = N - M).
    """
    snippet = r'''                      # PS: ?         HS: M;N;X
        POP2                            # PS: M;N;      HS: X
       #SWAP                            # PS: N;M;      HS: X (swap required ?) ou en 1ere ligne
        USUB                            # PS: R         HS: X
        PUSH                            # PS: R         HS: R;X
     '''
    return normalize(snippet, macros=('POP2', 'USUB', 'PUSH'))


# -- Multiplication ----------------------------------------------------------


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


def BINARY_MULTIPLY():
    snippet = r'''
                                        # PS: ?         HS: M;N;X
        POP2                            # PS: M;N;      HS: X
        s/$/;/
        UMUL                            # PS: R         HS: X
        PUSH                            # PS: R         HS: R;X
     '''
    return normalize(snippet, macros=('POP2', 'UMUL', 'PUSH'))


# -- Division ----------------------------------------------------------------


def UDIV():
    print euclide.func_code.co_varnames
    print euclide.func_code.co_varnames[:euclide.func_code.co_argcount]
    old_stdout = sys.stdout
    result = StringIO()
    sys.stdout = result
    dis.dis(euclide)
    sys.stdout = old_stdout
    return result.getvalue()


# -- Helper opcodes ----------------------------------------------------------


def IS_POSITIVE():
    snippet = r'''                      # PS: ?         HS: N;X
        g                               # PS: N;X       HS: N;X
        s/^[0-9+][^;]+/1/               # PS: 1;X       HS: N;X  if pos
        s/^-[^;]+/0/                    # PS: 0;X       HS: N;X  if neg
        h                               # PS: r;X       HS: r;X  r = 0 or 1
        '''
    return snippet


def NEGATIVE():
    # TODO : sed implementation
    pass


def DIVIDE_BY_TEN():
    # TODO : sed implementation
    pass


# -- Opcode interpreter ------------------------------------------------------


def interpreter(code):

    stack = list()
    names = dict()
    varnames = list()
    opcodes = list()
    labels = dict()

    for index, x in enumerate(code):
        y = x.split() + [None]
        opc, arg = y[:2]
        if opc[0] == ':':
            opc, arg = opc[0], opc[1:]
            labels[arg] = index
        opcodes.append((opc, arg))

    instr_pointer = 0
    while instr_pointer < len(opcodes):
        opc, arg = opcodes[instr_pointer]
        #print instr_pointer, opc, arg
        instr_pointer += 1
        if False:
            pass
        elif opc == ':':
            pass
        elif opc == 'LOAD_CONST':
            try:
                x = int(arg)
            except:
                x = arg
            stack.append(x)
        elif opc == 'LOAD_NAME' or opc == 'LOAD_GLOBAL':
            stack.append(names[arg])
        elif opc == 'STORE_NAME' or opc == 'STORE_GLOBAL':
            names[arg] = stack.pop()
            #print names
        elif opc == 'LOAD_FAST':
            stack.append(varnames[-1][arg])
        elif opc == 'STORE_FAST':
            varnames[-1][arg] = stack.pop()
        elif opc == 'ROT_THREE':
            # stack in  = [... z y x]
            # stack out = [... x z y]
            x = stack.pop()
            y = stack.pop()
            z = stack.pop()
            stack.extend([x, z, y])
        elif opc == 'UNARY_NEGATIVE':
            # TODO: optimize
            tos = stack.pop()
            stack.append(-tos)
        elif opc == 'UNARY_POSITIVE':
            # TODO: NOP like
            tos = stack.pop()
            stack.append(+tos)
        elif opc == 'BINARY_ADD' or opc == 'INPLACE_ADD':
            tos = stack.pop()
            tos1 = stack.pop()
            stack.append(tos1 + tos)
        elif opc == 'BINARY_SUBTRACT':
            tos = stack.pop()
            tos1 = stack.pop()
            stack.append(tos1 - tos)
        elif opc == 'BINARY_MULTIPLY':
            tos = stack.pop()
            tos1 = stack.pop()
            stack.append(tos1 * tos)
        elif opc == 'COMPARE_OP':
            tos = stack.pop()
            tos1 = stack.pop()
            if arg == '==':
                stack.append(tos1 == tos)
            elif arg == '!=':
                stack.append(tos1 != tos)
            elif arg == '<':
                stack.append(tos1 < tos)
            elif arg == '>':
                stack.append(tos1 > tos)
            elif arg == '<=':
                stack.append(tos1 <= tos)
            elif arg == '>=':
                stack.append(tos1 >= tos)
            else:
                raise Exception('numsed: unknown compare operator: %s' % arg)
        elif opc == 'JUMP_ABSOLUTE':
            instr_pointer = labels[arg]
        elif opc == 'POP_JUMP_IF_TRUE':
            tos = stack.pop()
            if tos:
                instr_pointer = labels[arg]
        elif opc == 'POP_JUMP_IF_FALSE':
            tos = stack.pop()
            if not tos:
                instr_pointer = labels[arg]
        elif opc == 'JUMP_FORWARD':
            # TODO: should be JUMP
            instr_pointer = labels[arg]
        elif opc == 'PRINT_ITEM':
            tos = stack.pop()
            print tos,
        elif opc == 'PRINT_NEWLINE':
            print
        elif opc == 'MAKE_FUNCTION':
            if int(arg) >= 256:
                raise Exception('numsed: keyword parameters not handled')
            else:
                pass
        elif opc == 'CALL_FUNCTION':
            # argc parameters on top of stack above name of function
            # first, add return address and swap parameters and name
            args = list()
            for i in range(int(arg)):
                args.append(stack.pop())
            func = stack.pop()
            stack.append(instr_pointer)
            for i in range(int(arg)):
                stack.append(args.pop())
            instr_pointer = labels[func]
        elif opc == 'RETURN_VALUE':
            ret_value = stack.pop()
            ret_pointer = stack.pop()
            instr_pointer = ret_pointer
            stack.append(ret_value)
        elif opc == 'SETUP_LOOP':
            pass
        elif opc == 'POP_BLOCK':
            pass
        elif opc == 'STARTUP':
            pass
        elif opc == 'MAKE_CONTEXT':
            varnames.append(dict())
        elif opc == 'POP_CONTEXT':
            varnames.pop()
        elif opc == 'IS_POSITIVE':
            tos = stack.pop()
            stack.append(tos >= 0)
        else:
            raise Exception('numsed: Unknown opcode: %s' % opc)


# -- Disassemble -------------------------------------------------------------


def disassemble(source, trace=False):

     # compile
    with open(source) as f:
        script = f.read()

    code = compile(script, source, "exec")

    # disassemble
    old_stdout = sys.stdout
    result = StringIO()
    sys.stdout = result
    dis.dis(code)
    sys.stdout = old_stdout
    code = result.getvalue().splitlines()

    # trace if requested
    if trace:
        for instr in code:
            print instr

    # return list of instructions
    return code


# -- Disassemble to numsed opcodes -------------------------------------------


def make_opcode_module(source, trace=False):

    if 1 == 1:
        global BINARY_ADD, BINARY_MULTIPLY
        def BINARY_ADD(): return 'BINARY_ADD'
        def BINARY_MULTIPLY(): return 'BINARY_MULTIPLY'

    # transform to positive form
    transformer.transform(source, '~.py')

    # disassemble
    code = disassemble('~.py', trace=False)

    # normalize disassembly labels and opcode arguments
    newcode = []
    newcode.append('STARTUP')

    # add dummy context to be removed by final RETURN_VALUE
    newcode.append('MAKE_CONTEXT')
    # add dummy pointer address to be taken by final RETURN_VALUE
    newcode.append('LOAD_CONST 1000000')

    for line in code:
        if line.strip():
            label, instr, arg = parse_dis_instruction(line)
            if label:
                newcode.append(':%s' % label)
            if arg:
                newcode.append('%s %s' % (instr, arg))
            else:
                newcode.append(instr)

    # create list of function labels and list of return labels
    function_labels = []
    return_labels = []
    newcode2 = []
    for instr in newcode:
        if instr.startswith('FUNCTION'):
            name = instr.split()[1]
            function_labels.append(name)
            newcode2.append(instr)
        elif instr.startswith('CALL_FUNCTION'):
            label = new_label()
            return_labels.append(label)
            newcode2.append('%s %s' % (instr, label))
            newcode2.append(':%s' % label)
        else:
            newcode2.append(instr)

    # handle function arguments and context
    newcode3 = []
    for instr in newcode2:
        if instr.startswith('FUNCTION'):
            x = instr.split()
            name = x[1]
            args = x[2:]
            newcode3.append(':%s' % name)
            newcode3.append('MAKE_CONTEXT')
            for arg in args:
                newcode3.append('STORE_FAST %s' % arg)
        elif instr.startswith('RETURN_VALUE'):
            newcode3.append('POP_CONTEXT')
            newcode3.append(instr)
        else:
            newcode3.append(instr)

    # print '[', '-' * 40
    # for instr in newcode3:
    #     print instr
    # print ']', '-' * 40

    # # TODO: ici ?
    # list_macros = ('BINARY_ADD', 'BINARY_SUBTRACT', 'BINARY_MULTIPLY')
    # newcode3 = normalize('\n'.join(newcode3), macros=list_macros)
    # newcode3 = newcode3.splitlines()

    # inline helper functions (is_positive, negative, divide_by_ten)
    newcode3 = inline_helper_opcodes(newcode3)

    # trace if requested
    if trace:
        for instr in newcode3:
            print instr

    # return list of instructions
    return newcode3, function_labels, return_labels


def parse_dis_instruction(s):
    #  45 BINARY_MULTIPLY
    #  59 JUMP_ABSOLUTE           27
    #  46 STORE_FAST               5 (aux)
    m = re.search('(\d+) (\w+) +(.*)', s)
    label, instr, arg = m.group(1), m.group(2), m.group(3)

    if '>>' not in s:
        label = None

    if not arg:
        arg = None
    elif 'code object' in arg:
        # <code object foo at 030E7EC0, file "exemple01.py", line 1>
        m = re.search('code object ([^ ]+) at ([^ ]+),', arg)
        arg = '%s_%s' % (m.group(1), m.group(2))
    elif '(' in arg:
        m = re.search('\((.*)\)', arg)
        arg = m.group(1)
        if arg.startswith('to '):
            arg = arg[3:]
    else:
        arg = arg.strip()

    return label, instr, arg


def inline_helper_opcodes(code):
    """
    Detect following opcode sequences :

    LOAD_GLOBAL is_positive|negative|divide_by_ten
    XXX
    CALL_FUNCTION 1 labelname
    :labelname

    and replace with

    XXX
    IS_POSITIVE|NEGATIVE|DIVIDE_BY_TEN

    This assumee the helper functions are called with arguments made of
    variables, consts and operators, i:e. no call functions inside the XXX
    sequence of opcodes.
    """

    # TODO: check in and out

    code2 = []
    i = 0
    while i < len(code):
        opcode = code[i]
        i += 1
        if not opcode.startswith('LOAD_GLOBAL'):
            code2.append(opcode)
        else:
            func = opcode.split()[1]
            if func not in ('is_positive', 'negative', 'divide_by_ten'):
                code2.append(opcode)
            else:
                argseq = []
                while not code[i].startswith('CALL_FUNCTION'):
                    argseq.append(code[i])
                    i += 1
                # skip call and label
                i += 2
                # append sequence
                code2.extend(argseq)
                # append opcode
                code2.append(func.upper())
    return code2


# -- Generate opcodes and run ------------------------------------------------


def make_opcode_and_run(source, trace=False):

    opcodes, function_labels, return_labels = make_opcode_module(source, trace=True)
    interpreter(opcodes)


# -- Generate sed code -------------------------------------------------------


def make_sed_module(source, trace=False):

    x, function_labels_, return_labels_ = make_opcode_module(source, trace=False)

    global function_labels, return_labels

    function_labels = function_labels_
    return_labels = return_labels_

    list_macros = ('STARTUP',
                   'MAKE_CONTEXT', 'POP_CONTEXT',
                   'LOAD_CONST', 'LOAD_NAME', 'STORE_NAME',
                   'LOAD_FAST', 'STORE_FAST',
                   'BINARY_ADD', 'BINARY_SUBTRACT', 'BINARY_MULTIPLY',
                   'RETURN_VALUE',
                   'PRINT_ITEM', 'PRINT_NEWLINE')

    y = normalize('\n'.join(x), macros=list_macros)
    # trace if requested
    if trace:
        print y

    # return string
    return y


# -- Generate sed script and run ---------------------------------------------


def make_sed_and_run(source):

    sed = make_sed_module(source, trace=False)

    name_script = 'test.sed'
    name_input = 'test.input'

    with open(name_script, 'w') as f:
        print>>f, sed

    with open(name_input, 'w') as f:
        print>>f, '0'

    com = 'sed -r -f %s %s' % (name_script, name_input)

    # TODO: check sed in path
    res = subprocess.check_output(com).splitlines()
    for line in res:
        print line


# -- Tests -------------------------------------------------------------------


def tmp():
    snippet = r'''
        LOAD_NAME foo
        STORE_NAME bar
    '''
    return normalize(snippet, macros=('LOAD_NAME', 'STORE_NAME'))

def numsed_compile(fname):
    __import__(fname)
    #functions_list = [obj for name,obj in inspect.getmembers(sys.modules[fname])
    #                 if inspect.isfunction(obj)]

def test():
    #import exemple01
    #dis.dis(exemple01)
    #numsed_compile('exemple01')
    #print make_opcode_module(sys.argv[1])
    #import inspect
    #functions_list = [obj for name,obj in inspect.getmembers(sys.modules[__name__])
    #                 if inspect.isfunction(obj)]
    #print functions_list
    #print dis.dis(euclide)
    #print CMP()
    #print euclide(17,3)
    #print MULBYDIGIT()
    #print 123456 * 567, UMUL(123456, 567)
    #x = UDIV()
    #print tmp()
    #print dis.dis(signed_add)
    #print inspect.getsourcelines(signed_add)
    pass


# -- Main --------------------------------------------------------------------


def do_helphtml():
    if os.path.isfile('numsed.html'):
        helpfile = 'numsed.html'
    else:
        helpfile = r'http://numsed.godrago.net/numsed.html'

    webbrowser.open(helpfile, new=2)

USAGE = '''
numsed.py -h | -H | -v
       -dis | -ops | -sed python-script
'''

def parse_command_line():
    parser = argparse.ArgumentParser(usage=USAGE, add_help=False)

    parser.add_argument('-h', help='show this help message', action='store_true', dest='do_help')
    parser.add_argument('-H', help='open html help page', action='store_true', dest='do_helphtml')
    parser.add_argument("-v", help="version", action="store_true", dest="version")
    parser.add_argument("-dis", help="disassemble", action="store_true", dest="disassemble")
    parser.add_argument("-ops", help="numsed intermediate opcodes", action="store_true", dest="opcodes")
    parser.add_argument("-opsrun", help="run numsed intermediate opcodes", action="store_true", dest="runopcodes")
    parser.add_argument("-sed", help="generate sed script", action="store_true", dest="sed")
    parser.add_argument("-run", help="generate sed script and run", action="store_true", dest="run")
    parser.add_argument("-test", help="test", action="store_true", dest="test")
    parser.add_argument("source", nargs='?', help=argparse.SUPPRESS, default=sys.stdin)

    args = parser.parse_args()
    return parser, args


def main():
    parser, args = parse_command_line()

    if args.version:
        print(BRIEF)
        print(VERSION)
        return
    elif args.do_help:
        parser.print_help()
        return
    elif args.do_helphtml:
        do_helphtml()
        return
    elif args.disassemble:
        disassemble(args.source, trace=True)
    elif args.opcodes:
        make_opcode_module(args.source, trace=True)
    elif args.runopcodes:
        make_opcode_and_run(args.source, trace=True)
    elif args.sed:
        make_sed_module(args.source, trace=True)
    elif args.run:
        make_sed_and_run(args.source)
    elif args.test:
        test()
    else:
        raise Exception()


if __name__ == "__main__":
    main()


# -- useless now


def BINARY_ADD():
    snippet = r'''
                                        # PS: ?         HS: M;N;X
        POP2                            # PS: M;N;      HS: X
        LOAD_GLOBAL signed_add          # PS: M;N;      HS: signed_add;X
        PUSH2                           # PS: ?         HS: M;N;signed_add;X
        CALL_FUNCTION 2                 # PS: ?         HS: R;X
     '''
    return normalize(snippet, macros=('POP2', 'PUSH2', 'LOAD_GLOBAL', 'CALL_FUNCTION'), functions=('signed_add',))

def BINARY_ADD():
    snippet = r'''                      ## interpreted in opcodes, perhaps should not be described in sed
                                        ##  # PS: ?         HS: M;N;X
        LOAD_GLOBAL signed_add          ##  # PS: ?         HS: signed_add;M;N;X
        ROT_THREE                       ##  # PS: ?         HS: M;N;signed_add;X
        CALL_FUNCTION 2                 ##  # PS: ?         HS: R;X
     '''
    return snippet
