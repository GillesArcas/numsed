"""
numsed: compiling python to sed
"""

from __future__ import print_function

import argparse
import os
import webbrowser
import glob

import common
import transformer
import opcoder
import sedcode
import snippet_test


VERSION = '0.01'

USAGE = '''
%s
Version          %s
Usage            numsed.py -h | -H
                 numsed.py <action> <format> <transformation> python-script
''' % (__doc__, VERSION)


def parse_command_line(argstring=None):
    parser = argparse.ArgumentParser(description=USAGE, usage=argparse.SUPPRESS, add_help=False, formatter_class=argparse.RawTextHelpFormatter)

    agroup = parser.add_argument_group('Information')
    xgroup = agroup.add_mutually_exclusive_group()
    xgroup.add_argument('-h', help='show this help message', action='store_true', dest='help')
    xgroup.add_argument('-H', help='open full help page', action='store_true', dest='fullhelp')

    agroup = parser.add_argument_group('Actions')
    xgroup = agroup.add_mutually_exclusive_group()
    xgroup.add_argument("--run", help="run generated script (default)", action="store_true")
    xgroup.add_argument("--trace", help="trace generated script", action="store_true")
    xgroup.add_argument("--coverage", help="run intermediate opcode and display opcode coverage (--opcode only)", action="store_true")
    xgroup.add_argument("--test", help="run conversion and compare with original python script", action="store_true")
    xgroup.add_argument("--all", help="complete test", action="store_true")

    agroup = parser.add_argument_group('Formats')
    xgroup = agroup.add_mutually_exclusive_group()
    xgroup.add_argument("--ast", help="generate abstract syntax tree", action="store_true")
    xgroup.add_argument("--script", help="generate python script", action="store_true")
    xgroup.add_argument("--disassembly", help="generate disassembly", action="store_true")
    xgroup.add_argument("--opcode", help="generate numsed intermediate opcode", action="store_true")
    xgroup.add_argument("--sed", help="generate sed script (default)", action="store_true")

    agroup = parser.add_argument_group('Transformations')
    xgroup = agroup.add_mutually_exclusive_group()
    xgroup.add_argument("--literal", help="no program transformation", action="store_true")
    xgroup.add_argument("--unsigned", help="replace division, modulo and power by functions", action="store_true")
    xgroup.add_argument("--signed", help="replace all operators by functions (default)", action="store_true")

    parser.add_argument("source", nargs='?', help=argparse.SUPPRESS)

    if argstring is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(argstring.split())

    information = (args.help, args.fullhelp)

    actions = (args.trace, args.run, args.coverage, args.test, args.all)
    if not any(actions):
        args.run = True

    formats = (args.ast, args.script, args.disassembly, args.opcode, args.sed)
    if not any(formats):
        args.sed = True

    transformations = (args.literal, args.unsigned, args.signed)
    if not any(transformations):
        args.signed = True

    # no action specified nor filename
    if not any(information) and not any(actions) and args.source is None:
        parser.print_help()
        parser.exit(1)

    # some action but no filename
    if not any(information) and args.source is None:
        print('numsed.py: error: filename required')
        parser.exit(1)

    if args.coverage and not args.opcode:
        print('numsed.py: error: argument --coverage requires argument --opcode')
        parser.exit(1)

    return parser, args


def do_fullhelp():
    if os.path.isfile('README.md'):
        helpfile = 'README.md'
    else:
        helpfile = r'https://github.com/GillesArcas/numsed/blob/master/README.md'

    webbrowser.open(helpfile, new=2)


def transformation(args):
    if args.literal:
        return transformer.LITERAL
    elif args.unsigned:
        return transformer.UNSIGNED
    elif args.signed:
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


def process_test(args, source, result):
    maker = numsed_maker(args)
    target = maker(source, transformation(args))
    if args.run:
        x = target.run()
    elif args.coverage:
        x = target.coverage()
    elif args.test:
        x = target.test(result)
    elif args.trace:
        x = target.trace()

    if args.run and args.sed:
        # already printed
        pass
    else:
        print(x)
    return x


def tests_from_dir(source):
    for test in glob.glob(os.path.join(source, '*.py')):
        print(test)
        yield test, test, None


def tests_from_suite(source):
    for test, result in common.testlines(source):
        print(test[0].rstrip())
        with open('tmp.py', 'w') as f:
            f.writelines(test)
        yield 'tmp.py', test[0].rstrip(), result


def process_tests(args, tests_from_source):
    timing = []
    status = True
    for test, title, result in tests_from_source(args.source):
        r = process_test(args, test, result)
        status = status and (not args.test or r)
        if args.test:
            timing.append((title, status[1]))
            status = status[0]
        if not status:
            break
    if args.test:
        s = 0
        for (test, timing) in timing:
            print('%-30s %6.2f' % (test, timing))
            s += timing
        print('%-30s %6.2f' % ('total', s))
        print('ALL TESTS OK' if status else 'ONE TEST FAILURE')
    return status


def process_all(args):
    # use --trace when -test is not relevant. This completes coverage and may
    # catch some errors
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
    status = status and snippet_test.main()
    print('ALL TESTS OK' if status else 'ONE TEST FAILURE')


def numsed(argstring=None):
    parser, args = parse_command_line(argstring)

    if args.help:
        parser.print_help()

    elif args.fullhelp:
        do_fullhelp()

    elif args.all:
        process_all(args)

    else:
        if os.path.isdir(args.source):
            result = process_tests(args, tests_from_dir)
        elif args.source.endswith('.suite.py'):
            result = process_tests(args, tests_from_suite)
        else:
            result = process_test(args, args.source)
        if args.coverage:
            opcoder.display_coverage()
        return result


if __name__ == "__main__":
    numsed()
