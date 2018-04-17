# A version of the towers of hanoi using a single integer to represent the state
# of the three stacks.
# Example       : hanoi(4)
# Initial state : 1000000004321
# Final state   : 1432100000000


def hanoi(size):
    stacks = prepare(size)
    print(stacks)
    stacks = move_stack(size, size, stacks, 0, 1, 2)


def move_stack(n, size, stacks, source, helper, target):
    if n > 0:
        stacks = move_stack(n - 1, size, stacks, source, target, helper)
        stacks = move_disk(size, stacks, source, target, helper)
        stacks = move_stack(n - 1, size, stacks, helper, source, target)
    return stacks


def prepare(n):
    i = 0
    s = 0
    while i < n:
        s = s + (i + 1) * 10 ** i
        i += 1
    s = 10 ** (3 * n) + s
    return s


def get_stack(size, stacks, index):
    stk = stacks // 10 ** (index * size)
    stk = stk % 10 ** size
    return stk


def move_disk(size, stacks, source, target, other):
    src = get_stack(size, stacks, source)
    tgt = get_stack(size, stacks, target)
    oth = get_stack(size, stacks, other)
    src, disk = divmod(src, 10)
    tgt = tgt * 10 + disk
    stacks = 10 ** (3 * size) + src * 10 ** (source * size) + tgt * 10 ** (target * size) + oth * 10 ** (other * size)
    print(stacks)
    return stacks


hanoi(6)
