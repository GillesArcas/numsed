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
            if line.startswith('---'):
                yield lines
                lines = []
            else:
                lines.append(line)


def run_test(test):
    # save script
    with open('tmp.py', 'w') as f:
        f.writelines(test)

    # run script and store results
    ref = subprocess.check_output('python tmp.py')
    print ref

    mode = 2
    if mode == 1:
        # transform
        transformer.transform('tmp.py', 'tmp_transformed.py', do_assert=True)

        # run transformed script and store results
        res = subprocess.check_output('python tmp.py')
        print res
    if mode == 2:
        #numsed.make_opcode_and_run('tmp.py', trace=False)
        res = subprocess.check_output('python numsed.py -opsrun tmp.py')

    # compare
    status, diff = list_compare('ref', 'res', ref.splitlines(), res.splitlines())
    if not status:
        print diff

    return status


def list_compare(tag1, tag2, list1, list2):
    # make sure both lists have same length
    maxlen = max(len(list1), len(list2))
    list1.extend([''] * (maxlen - len(list1)))
    list2.extend([''] * (maxlen - len(list2)))

    diff = list()
    res = True
    for i, (x, y) in enumerate(zip(list1, list2)):
        if x != y:
            diff.append('line %s %d: %s' % (tag1, i + 1, x))
            diff.append('line %s %d: %s' % (tag2, i + 1, y))
            res = False
    return res, diff


def main():
    status = True
    for test in testlines(sys.argv[1]):
        print test
        status = status and run_test(test)
    if status:
        print 'ALL TESTS OK'
    else:
        print 'One TEST failure'


if __name__ == '__main__':
    main()