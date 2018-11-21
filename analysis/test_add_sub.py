"""
This script is used to construct, test and analyze the various variants
for digit addition and subtraction.
"""
import re
import sys
import subprocess
import colorama


# snippet construction


def define_all():
    global ADD_09_09, ADD_09_90, ADD_90_09, ADD_90_90
    global SUB_09_09, SUB_90_09, SUB_09_90, SUB_90_90

    ADD_09_09 = r'''
        s/(..)/\1;0123456789;0123456789/
        s/(.)(.);\d*(\1\d*);(\d*(\2\d*))/\3\5\4/
        s/.{10}(.)\d{0,9}(\d{0,1})\d*/1\1\2/
        s/1\d(\d)/0\1/
    '''

    ADD_09_90 = r'''
        s/(..)/\1;0123456789;9876543210/
        s/(.)(.);(\d*)\1\d*;(\d*(\2\d*))/\3\5\4/
        s/.{10}(.)\d{0,9}(\d{0,1})\d*/0\1\2/
        s/0\d(\d)/1\1/
    '''

    ADD_90_09 = reverse1(ADD_09_09)
    ADD_90_90 = reverse1(ADD_09_90)
    SUB_09_09 = reverse2(permute(ADD_09_90))
    SUB_90_09 = reverse2(permute(ADD_90_90))
    SUB_09_90 = reverse2(permute(ADD_09_09))
    SUB_90_90 = reverse2(permute(ADD_90_09))


def permute(snippet):
    """Permute snippet arguments:
    a + b --> b + a
    a - b --> b - a
    Exchange \1 and \2 in s/(.)(.);\d*(\1\d*);(\d*(\2\d*))/\3\5\4/
    """
    lines = snippet.splitlines()
    lines[2] = re.sub(r'(\\[12])(.*)(\\[12])', r'\3\2\1', lines[2])
    return '\n'.join(lines)


def reverse1(snippet):
    """Reverse first sequence.
    This does not change the calculated value.
    """
    text = snippet
    if '0123456789;' in text:
        text = text.replace('0123456789;', '9876543210;')
        text = text.replace(r';\d*(\1\d*);', r';(\d*\1)\d*;')   # [a9] to [9a]  len = 10 - a
        text = text.replace(r';(\d*)\1\d*;', r';\d*\1(\d*);')   # [0a[ to ]a0]  len = a
    else:
        text = text.replace('9876543210;', '0123456789;')
        text = text.replace(r';(\d*\1)\d*;', r';\d*(\1\d*);')   # [9a] to [a9]  len = 10 - a
        text = text.replace(r';\d*\1(\d*);', r';(\d*)\1\d*;')   # ]a0] to [0a[  len = a
    return text


def reverse2(snippet):
    """Reverse second sequence.
    Change a + b to b - a and a - b or b - a to a + b.
    """
    text = snippet
    if '0123456789/' in text:
        text = text.replace('0123456789/', '9876543210/')
    else:
        text = text.replace('9876543210/', '0123456789/')
    return text


# testing


def testdeck_add():
    inplist = list()
    outlist = list()
    for a in range(10):
        for b in range(10):
            inplist.append('%d%d' % (a, b))
            outlist.append('%02d' % (a + b))
    return inplist, outlist


def testdeck_sub():
    inplist = list()
    outlist = list()
    for a in range(10):
        for b in range(10):
            inplist.append('%d%d' % (a, b))
            if b <= a:
                x, y = 0, a - b
            else:
                x, y = 1, 10 + a - b
            outlist.append('%d%d' % (x, y))
    return inplist, outlist


def runtest(descr, snippet, inplist, outlist):
    """ Run a test.

    snippet is the snippet to test
    inplist is the input of the snippet
    outlist is the expected result
    """
    snippet = snippet.replace(r'\d', '[0-9]')
    with open('tmp.sed', 'w') as f:
        print(snippet, file=f)

    with open('tmp.input', 'w') as f:
        for line in inplist:
            print(line, file=f)

    com = 'sed -r -f %s %s' % ('tmp.sed', 'tmp.input')
    res = subprocess.check_output(com).decode('ascii').splitlines()

    if res == outlist:
        print('%-15s %s' % (descr, 'OK'))
    else:
        print('%-15s %s' % (descr, 'fail'))
        for inp, out, resline in zip(inplist, outlist, res):
            if out != resline:
                print('%-8s %-8s %-8s' % (inp, out, resline))


def test_all():
    runtest('ADD_09_09', ADD_09_09, *testdeck_add())
    runtest('ADD_90_09', ADD_90_09, *testdeck_add())
    runtest('ADD_09_90', ADD_09_90, *testdeck_add())
    runtest('ADD_90_90', ADD_90_90, *testdeck_add())
    runtest('SUB_09_09', SUB_09_09, *testdeck_sub())
    runtest('SUB_90_09', SUB_90_09, *testdeck_sub())
    runtest('SUB_09_90', SUB_09_90, *testdeck_sub())
    runtest('SUB_90_90', SUB_90_90, *testdeck_sub())


# colors


def colorize(snippet):
    snippet = snippet.splitlines()
    line1 = snippet[1]          #  s/(..)/\1;0123456789;0123456789/
    line2 = snippet[2]          #  s/(.)(.);\d*(\2\d*);(\d*(\1\d*))/\3\5\4/
    line3 = snippet[3]          #  s/.{10}(.)\d{0,9}(\d{0,1})\d*/1\2\1/

    line1pat, line1sub = line1.split(r'/')[1:3]
    line2pat, line2sub = line2.split(r'/')[1:3]
    line3pat, line3sub = line3.split(r'/')[1:3]

    for i in range(10):
        for j in range(10):
            s = '%d%d' % (i, j)
            s = re.sub(line1pat, line1sub, s)
            m = re.match(line2pat, s)
            colors = 'A' * (m.end(3) - m.start(3)) + 'B' * (m.end(5) - m.start(5)) + 'C' * (m.end(4) - m.start(4))
            s = re.sub(line2pat, line2sub, s)
            m = re.match(line3pat, s)
            index1 = m.start(1)
            index2 = m.start(2)
            print('%d%d' % (i, j), colored_string(s, colors, index1, index2))


def colored_string(s, color, index1, index2):
    colors = {
        'A': colorama.Fore.BLUE,
        'B': colorama.Fore.GREEN,
        'C': colorama.Fore.MAGENTA
    }
    colored = ''
    for index, (dig, col) in enumerate(zip(s, color)):
        colored_digit = colors[col] + dig + colorama.Fore.RESET
        if index in (index1, index2):
            colored_digit = colorama.Back.YELLOW + colored_digit + colorama.Back.RESET
        colored += colored_digit
    return colored


# main


def main():
    colorama.init()
    define_all()
    nargs = len(sys.argv) - 1
    if nargs == 2 and sys.argv[1] == 'trace':
        snippet = globals()[sys.argv[2]]
        print(snippet)
    elif nargs == 1 and sys.argv[1] == 'test':
        test_all()
    elif nargs == 2 and sys.argv[1] == 'colorize':
        snippet = globals()[sys.argv[2]]
        colorize(snippet)
    else:
        s = 'ADD_09_09|ADD_09_90|ADD_90_09|ADD_90_90|SUB_09_09|SUB_90_09|SUB_09_90|SUB_90_90'
        print('$ test-add-sub.py trace', s)
        print('$ test-add-sub.py test')
        print('$ test-add-sub.py colorize', s)


main()
