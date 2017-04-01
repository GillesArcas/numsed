import sys
import os
import subprocess


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

    # run script and store results

    # transform

    # run transformed script and store results

    # compare
    pass


def main():
    for test in testlines(sys.argv[1]):
        print test


if __name__ == '__main__':
    main()