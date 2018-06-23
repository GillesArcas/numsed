"""
numsed: compiling python to sed
"""

from __future__ import print_function

import argparse
import os
import sys
import webbrowser
import glob
import time

try:
    import common
    import checker
    import transformer
    import opcoder
    import sedcode
    import snippet_test
except:
    from . import common
    from . import checker
    from . import transformer
    from . import opcoder
    from . import sedcode
    from . import snippet_test


VERSION = '0.21'

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
    xgroup.add_argument("--snippets", help="test snippets", action="store_true")
    xgroup.add_argument("--batch", help="batch test", action="store_true")

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

    # do not use, it is intended to pass batch directory ni batch mode
    parser.add_argument("--batchdir", help=argparse.SUPPRESS, action="store")

    parser.add_argument("source", nargs='?', help=argparse.SUPPRESS)

    if argstring is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(argstring.split())

    information = (args.help, args.fullhelp)

    actions = (args.trace, args.run, args.coverage, args.test, args.batch, args.snippets)
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
    if not any(information) and args.source is None and not args.snippets:
        print('numsed.py: error: filename required')
        parser.exit(1)

    if args.coverage and not args.opcode:
        print('numsed.py: error: argument --coverage requires argument --opcode')
        parser.exit(1)

    if args.batch:
        # if batch, tests are looked for in batch directory
        args.batchdir = os.path.dirname(args.source)
    else:
        # look for test file in argument test directory
        # args.source may be None (cf --snippets)
        if args.batchdir and args.source and not os.path.isabs(args.source):
            args.source = os.path.join(args.batchdir, args.source)

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
    else:
        return None


def numsed_conversion(args):
    if args.ast:
        return transformer.AstAssertConversion
    elif args.script:
        return transformer.ScriptConversion
    elif args.disassembly:
        return opcoder.DisassemblyConversion
    elif args.opcode:
        return opcoder.OpcodeConversion
    elif args.sed:
        return sedcode.SedConversion
    else:
        return None


def process_script(args, source, title, expected_result=None):

    checked, msg = checker.check(source)

    if args.test:
        return test_script(args, source, title, expected_result, checked, msg)
    elif checked is False:
        print(msg)
        return ''
    else:
        print(title)
        conversion = numsed_conversion(args)
        target = conversion(source, transformation(args))
        if args.run:
            x = target.run()
        elif args.coverage:
            x = target.coverage()
        elif args.trace:
            x = target.trace()

        if args.run and args.sed:
            # already printed
            pass
        else:
            print(x)
        return x


def expected_result(args, source, result, checked, msg):

    def result_from_script(source):
        source_lines = open(source).read()
        code = compile(source_lines, '<string>', 'exec')
        try:
            with common.ListStream() as x:
                exec(code, {})
        except SystemExit:
            pass
        return x.singlestring()

    def result_from_suite():
        return ''.join(result)

    if result is None:
        # no result in test suite, run script
        return result_from_script(source)
    else:
        # result in test suite
        if result[0].startswith('numsed error') or result[0].startswith('SyntaxError:'):
            return result_from_suite()
        elif args.opcode or args.sed:
            return result_from_suite()
        else:
            return result_from_script(source)


def test_script(args, source, title, result, checked, msg):
    """
    if result is None, the test has to be compared with the python script
    if result is not None, the test has to be compared with this result
    checked and msg are the results of syntax checking
    """
    if not source.endswith('.py'):
        return False

    print('%-50s' % title, end='')

    # make reference by running original script or using result lines in suite
    ref = expected_result(args, source, result, checked, msg)

    # run conversion or use result of syntax checking
    if checked is False:
        res = msg #+ '\n'
        time_sed = 0
    else:
        conversion = numsed_conversion(args)
        target = conversion(source, transformation(args))

        # run conversion
        t0 = time.time()
        res = target.run(verbose=False)
        time_sed = time.time() - t0

    # compare
    status, diff = common.list_compare('ref', 'res', ref.splitlines(), res.splitlines())
    if status:
        print(' OK %6.2f' % time_sed)
    else:
        print(' FAIL')
        for _ in diff:
            print(_)

    return status, time_sed


def tests_from_dir(source):
    for test in glob.glob(os.path.join(source, '*.py')):
        yield test, test, None


def tests_from_suite(source):
    for test, result in common.testlines(source):
        with open(common.TMP_PY, 'w') as f:
            f.writelines(test)
        yield common.TMP_PY, test[0].rstrip(), result


def process_testset(args, tests_from_source):
    if not args.test:
        for test, title, result in tests_from_source(args.source):
            process_script(args, test, title, result)
        return True
    else:
        status = True
        timing = 0
        for test, title, result in tests_from_source(args.source):
            sta, tim = process_script(args, test, title, result)
            status = status and sta
            timing += tim
            if not status:
                break
        print('%-50s    %6.2f' % ('total', timing))
        print('ALL TESTS OK' if status else 'ONE TEST FAILURE')
        return status


def process_batch(args):
    status = True
    with open(args.source) as batch:
        for line in batch:
            if line.strip() and line[0] != ';':
                testargs = line.strip()

                # propagate parameter test directory
                if args.batchdir:
                    testargs += ' --batchdir %s' % args.batchdir

                status = numsed(testargs)
                if not status:
                    break
    print('BATCH OK' if status else 'ONE TEST FAILURE in ' + line.strip())
    return status


def numsed(argstring=None):

    parser, args = parse_command_line(argstring)
    if args.help:
        parser.print_help()

    elif args.fullhelp:
        do_fullhelp()

    elif args.batch:
        return process_batch(args)

    elif args.snippets:
        return snippet_test.main()

    else:
        if os.path.isdir(args.source):
            result = process_testset(args, tests_from_dir)
        elif os.path.isfile(args.source):
            if args.source.endswith('.suite.py'):
                result = process_testset(args, tests_from_suite)
            elif args.source.endswith('.py'):
                result = process_script(args, args.source, args.source)
            elif args.source.endswith('.opc'):
                if args.run:
                    opcode = open(args.source).readlines()
                    opcode = [_.rstrip() for _ in opcode]
                    result = opcoder.interpreter(opcode)
                else:
                    pass
            else:
                print('numsed error: file type not handled:', args.source)
                return ''
        else:
            print('numsed error: file not found:', args.source)
            return ''

        if args.coverage:
            opcoder.display_coverage()

        return result


def numsed_main():
    if numsed():
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    numsed_main()
