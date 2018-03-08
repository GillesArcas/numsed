from __future__ import print_function

import sys
import os
import subprocess
import transformer
import numsed


def testlines(name):
    '''
    yield each test in a test suite
    '''
    with open(name) as f:
        lines = []
        for line in f:
            if line.startswith('# --'):
                yield lines
                lines = []
            else:
                lines.append(line)


def run_test(test, mode):
    # save script
    with open('tmp.py', 'w') as f:
        f.writelines(test)

    # run script and store results
    ref = subprocess.check_output('python tmp.py')
    ref = ref.decode('ascii') # py3
    print(ref)

    if mode == 'transform':
        # transform
        transformer.transform('tmp.py', 'tmp_transformed.py', do_assert=True)

        # run transformed script and store results
        res = subprocess.check_output('python tmp_transformed.py')
        res = res.decode('ascii') # py3
        ###print(res)

    if mode == 'opsigned':
        #res = numsed.make_opcode_and_run('tmp.py', trace=False)
        #res = numsed.run_opcode('tmp.py', transform=False)
        #res = subprocess.check_output('python numsed.py --opsigned --run tmp.py')
        res = numsed.numsed('--opsigned --run tmp.py')
        #res = subprocess.check_output('python numsed.py --opsigned --run tmp.py')
        print(res)

    if mode == 'opcode':
        #numsed.make_opcode_and_run('tmp.py', trace=False)
        #res = subprocess.check_output('python numsed.py --opcode --run tmp.py')
        res = numsed.numsed('--opcode --run tmp.py')
        print(res)

    if mode == 'sed':
        res = subprocess.check_output('python numsed.py --sed --run tmp.py')
        res = res.decode('ascii') # py3
        print(res)

    # compare
    status, diff = list_compare('ref', 'res', ref.splitlines(), res.splitlines())
    if not status:
        for _ in diff:
            print(_)

    return status


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


def main(mode, testsuite):
    if mode in ('transform', 'opsigned', 'opcode', 'sed'):
        status = True
        for test in testlines(testsuite):
            print(test)
            status = status and run_test(test, mode)
        print('ALL TESTS OK' if status else 'One TEST failure')
    else:
        status = all(main(mode, testsuite) for mode in ('transform', 'opsigned', 'opcode', 'sed'))
        print('ALL MODES OK' if status else 'ONE MODE FAILURE')
    return status


if __name__ == '__main__':
    if len(sys.argv) != 3 or sys.argv[1] not in ('transform', 'opsigned', 'opcode', 'sed') + ('all',):
        print('numsed_test.py transform|opsigned|opcode|sed|all testsuite')
    else:
        mode = sys.argv[1]
        testsuite = sys.argv[2]
        main(mode, testsuite)
