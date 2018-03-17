"""
numsed: compiling python to sed
"""

from __future__ import print_function

import argparse
import sys
import os
import webbrowser

import common
import transformer
import opcoder
import sedcode


VERSION = '0.01'


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


def do_helphtml():
    if os.path.isfile('README.md'):
        helpfile = 'README.md'
    else:
        helpfile = r'https://github.com/GillesArcas/numsed/blob/master/README.md'

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
    xgroup.add_argument("--test", help="run conversion and compare with original python script", action="store_true")

    parser.add_argument("--all", help="test", action="store_true")
    parser.add_argument("source", nargs='?', help=argparse.SUPPRESS)

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
    elif args.signed:
        return transformer.SIGNED
    else:
        # default to --signed
        return transformer.SIGNED


def numsed_maker(args):
    if args.ast:
        return transformer.AstConversion
    elif args.script:
        return transformer.ScriptConversion
    elif args.disassembly:
        return opcoder.DisassemblyConversion
    elif args.opcode:
        return opcoder.OpcodeConversion
    elif args.sed:
        return sedcode.SedConversion
    else:
        # default to --sed
        return sedcode.SedConversion


def proceed(args, source):
    maker = numsed_maker(args)
    target = maker(source, transformation(args))
    if args.run:
        x = target.run()
    elif args.coverage:
        x = target.coverage()
    elif args.test:
        x = target.test()
    elif args.trace:
        x = target.trace()
    else:
        # default to --run
        x = target.run()
    print(x)
    return x


def numsed(argstring=None):
    parser, args = parse_command_line(argstring)

    if args.version:
        print(__doc__)
        print(VERSION)

    elif args.do_help:
        parser.print_help()

    elif args.do_helphtml:
        do_helphtml()

    elif args.all:
        # use --trace when -test is not relevant. This may catch some errors
        # and complete coverage.
        test_args = ('--ast    --literal  --test ',
                     '--ast    --unsigned --trace',
                     '--ast    --signed   --test ',
                     '--script --literal  --test ',
                     '--script --unsigned --trace',
                     '--script --signed   --test ',
                     '--dis    --literal  --trace',
                     '--dis    --unsigned --trace',
                     '--dis    --signed   --trace',
                     '--opcode --literal  --test ',
                     '--opcode --unsigned --trace',
                     '--opcode --signed   --test ',
                     '--sed    --literal  --trace',
                     '--sed    --unsigned --trace',
                     '--sed    --signed   --test ')
        status = all(numsed('%s %s' % (x, args.source)) for x in test_args)
        print('ALL TESTS OK' if status else 'ONE TEST FAILURE')

    else:
        if not args.source.endswith('.suite.py'):
            return proceed(args, args.source)
        else:
            status = True
            for test in common.testlines(args.source):
                print(test)
                with open('tmp.py', 'w') as f:
                    f.writelines(test)
                status = status and proceed(args, 'tmp.py')
            print('ALL TESTS OK' if status else 'ONE TEST FAILURE')
            return status


if __name__ == "__main__":
    numsed()
