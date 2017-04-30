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


def run_test(test, mode):
    # save script
    with open('tmp.py', 'w') as f:
        f.writelines(test)

    # run script and store results
    ref = subprocess.check_output('python tmp.py')
    print ref

    if mode == 'transform':
        # transform
        transformer.transform('tmp.py', 'tmp_transformed.py', do_assert=True)

        # run transformed script and store results
        res = subprocess.check_output('python tmp_transformed.py')
        print res

    if mode == 'opcode':
        #numsed.make_opcode_and_run('tmp.py', trace=False)
        res = subprocess.check_output('python numsed.py --oprun tmp.py')
        print res

    if mode == 'sed':
        res = subprocess.check_output('python numsed.py --run tmp.py')
        print res

    # compare
    status, diff = list_compare('ref', 'res', ref.splitlines(), res.splitlines())
    if not status:
        for _ in diff:
            print _

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


def main():
    mode = 'sed'
    status = True
    for test in testlines(sys.argv[1]):
        print test
        status = status and run_test(test, mode)
    if status:
        print 'ALL TESTS OK'
    else:
        print 'One TEST failure'


if __name__ == '__main__':
    main()