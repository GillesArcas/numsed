from __future__ import print_function

import argparse
import sys
import os

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


# -- Tests -------------------------------------------------------------------


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
numsed.py <format> <transformation> <action> python-script
'''

def parse_command_line(argstring=None):
    parser = argparse.ArgumentParser(usage=USAGE, add_help=False)

    parser.add_argument('-h', help='show this help message', action='store_true', dest='do_help')
    parser.add_argument('-H', help='open html help page', action='store_true', dest='do_helphtml')
    parser.add_argument("-v", help="version", action="store_true", dest="version")

    agroup = parser.add_argument_group('Formats')
    xgroup = agroup.add_mutually_exclusive_group()
    xgroup.add_argument("--ast", help="generate abstract syntax tree", action="store_true")
    xgroup.add_argument("--script", help="generate python script", action="store_true")
    xgroup.add_argument("--disassembly", help="generate disassembly", action="store_true")
    xgroup.add_argument("--opcode", help="generate numsed intermediate opcode", action="store_true")
    xgroup.add_argument("--sed", help="generate sed script", action="store_true")

    agroup = parser.add_argument_group('Transformations')
    xgroup = agroup.add_mutually_exclusive_group()
    xgroup.add_argument("--literal", help="no program transformation", action="store_true")
    xgroup.add_argument("--unsigned", help="replace division, modulo and power by functions", action="store_true")
    xgroup.add_argument("--signed", help="replace all operators by functions", action="store_true")

    agroup = parser.add_argument_group('Actions')
    xgroup = agroup.add_mutually_exclusive_group()
    xgroup.add_argument("--run", help="run generated script", action="store_true")
    xgroup.add_argument("--trace", help="trace generated script", action="store_true")
    xgroup.add_argument("--coverage", help="run numsed intermediate opcode and display opcode coverage", action="store_true")
    xgroup.add_argument("--testing", help="run conversion and compare with original python script", action="store_true")

    parser.add_argument("--test", help="test", action="store_true", dest="test")
    parser.add_argument("source", nargs='?', help=argparse.SUPPRESS, default=sys.stdin)

    if argstring is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(argstring.split())
    return parser, args


def transformation(args):
    if args.literal:
        return transformer.LITERAL
    elif args.unsigned:
        return transformer.UNSIGNED
    else:
        return transformer.SIGNED


def numsed_maker(args):
    if args.ast:
        return transformer.AstConversion
    if args.script:
        return transformer.ScriptConversion
    if args.disassembly:
        return opcoder.DisassemblyConversion
    if args.opcode:
        return opcoder.OpcodeConversion
    if args.sed:
        return sedcode.SedConversion
    return None


def numsed(argstring=None):
    parser, args = parse_command_line(argstring)

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

    elif args.test:
        test()

    else:
        maker = numsed_maker(args)
        target = maker(args.source, transformation(args))
        if args.run:
            x = target.run()
        elif args.coverage:
            x = target.coverage()
        elif args.testing:
            x = target.test()
        else:
            x = target.trace()
        print(x)
        return x


if __name__ == "__main__":
    numsed()
