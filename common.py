#coding: latin_1

from __future__ import print_function

import sys
import subprocess
try:
    from StringIO import StringIO  # Python2
except ImportError:
    from io import StringIO  # Python3

PY2 = sys.version_info < (3,)


class NumsedConversion:
    def __init__(self, source, transformation):
        self.source = source
        self.transformation = transformation

    def trace(self):
        return ''

    def run(self):
        return ''

    def coverage(self):
        return 'Coverage not implemented for current conversion.'

    def print_run_result(self):
        return True

    def test(self):
        if not self.source.endswith('.py'):
            return False

        # run original script and store results
        ref = subprocess.check_output('python ' + self.source)
        ref = ref.decode('Latin-1') # py3
        print(ref)

        # run conversion
        res = self.run()
        if self.print_run_result():
            print(res)

        # compare
        status, diff = list_compare('ref', 'res', ref.splitlines(), res.splitlines())
        if not status:
            for _ in diff:
                print(_)

        return status


class ListStream:
    def __enter__(self):
        self.result = StringIO()
        sys.stdout = self.result
        return self
    def __exit__(self, ext_type, exc_value, traceback):
        sys.stdout = sys.__stdout__
    def stringlist(self):
        return self.result.getvalue().splitlines()
    def singlestring(self):
        return self.result.getvalue()


def run(cmd):
    try:
        p = subprocess.Popen(cmd.split(),
                            #shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    except:
        print('Unable to start', cmd)
        exit(1)

    res = []
    while True:
        line = p.stdout.readline()
        line = line.decode('Latin-1') # py3
        if line == '':
            break
        else:
            line = line.rstrip('\n\r')
            res.append(line)
            print(line)
    return '\n'.join(res)


def testlines(name):
    '''
    yield each test in a test suite
    '''
    with open(name) as f:
        lines = []
        for line in f:
            if line.startswith('#') and '---' in line:
                yield lines
                lines = []
            else:
                lines.append(line)


def list_compare(tag1, tag2, list1, list2):
    # make sure both lists have same length
    maxlen = max(len(list1), len(list2))
    list1.extend([''] * (maxlen - len(list1)))
    list2.extend([''] * (maxlen - len(list2)))

    # with open('list1.txt', 'w') as f:
    #     for line in list1:
    #         print>>f, line
    # with open('list2.txt', 'w') as f:
    #     for line in list2:
    #         print>>f, line

    diff = list()
    res = True
    for i, (x, y) in enumerate(zip(list1, list2)):
        if x != y:
            diff.append('line %s %d: %s' % (tag1, i + 1, x))
            diff.append('line %s %d: %s' % (tag2, i + 1, y))
            res = False
    return res, diff


