from __future__ import print_function

import argparse
import sys
import os
import re
import subprocess
from StringIO import StringIO  # Python2
#from io import StringIO  # Python3

import transformer
import opcoder
import sedcode


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


# -- Generate opcodes and run ------------------------------------------------


def make_opcode_and_run(source, trace=False):

    opcodes, function_labels, return_labels = opcoder.make_opcode_module(source, trace=trace)
    opcoder.interpreter(opcodes)


# -- Generate sed code -------------------------------------------------------


def make_sed_module(source, trace=False):

    if source.endswith('.py'):
        opcodes, function_labels, return_labels = opcoder.make_opcode_module(source, trace=False)
    elif source.endswith('.opc'):
        opcodes, function_labels, return_labels = opcoder.read_opcode_module(source, trace=False)
    else:
        raise Exception('Invalid file type')

    sed = sedcode.sedcode(opcodes, function_labels, return_labels)

    # trace if requested
    if trace:
        print(sed)

    # return string
    return sed


# -- Generate sed script and run ---------------------------------------------


def make_sed_and_run(source, trace=False):

    sed = make_sed_module(source, trace=False)

    name_script = 'tmp.sed'
    name_input = 'tmp.input'

    with open(name_script, 'w') as f:
        print(sed, file=f)

    with open(name_input, 'w') as f:
        print('0', file=f)

    com = 'sed -n -r -f %s %s' % (name_script, name_input)

    # TODO: check sed in path
    res = subprocess.check_output(com).splitlines()
    for line in res:
        print(line)


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
    parser.add_argument("--dis", help="disassemble", action="store_true", dest="disassemble")
    parser.add_argument("--opcode", help="numsed intermediate opcode", action="store_true", dest="opcode")
    parser.add_argument("--oprun", help="run numsed intermediate opcode", action="store_true", dest="runopcode")
    parser.add_argument("--sed", help="generate sed script", action="store_true", dest="sed")
    parser.add_argument("--run", help="generate sed script and run", action="store_true", dest="run")
    parser.add_argument("--test", help="test", action="store_true", dest="test")
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
        opcoder.disassemble(args.source, trace=True)
    elif args.opcode:
        opcoder.make_opcode_module(args.source, trace=True)
    elif args.runopcode:
        make_opcode_and_run(args.source, trace=False)
    elif args.sed:
        make_sed_module(args.source, trace=True)
    elif args.run:
        make_sed_and_run(args.source, trace=False)
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
