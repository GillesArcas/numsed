"""
Generating and interpreting numsed opcodes.
"""


import sys
import re
import dis
from StringIO import StringIO  # Python2
#from io import StringIO  # Python3
import transformer


# -- Disassemble -------------------------------------------------------------


def disassemble(source, trace=False):

     # compile
    with open(source) as f:
        script = f.read()

    code = compile(script, source, "exec")

    # disassemble
    old_stdout = sys.stdout
    result = StringIO()
    sys.stdout = result
    dis.dis(code)
    sys.stdout = old_stdout
    code = result.getvalue().splitlines()

    # trace if requested
    if trace:
        for instr in code:
            print instr

    # return list of instructions
    return code


# -- Disassemble to numsed opcodes -------------------------------------------


def make_opcode_module(source, trace=False):

    if 1 == 1:
        global BINARY_ADD, BINARY_MULTIPLY
        def BINARY_ADD(): return 'BINARY_ADD'
        def BINARY_MULTIPLY(): return 'BINARY_MULTIPLY'

    # transform to positive form
    transformer.transform(source, '~.py')

    # disassemble
    dis_code = disassemble('~.py', trace=False)

    # simplify dis code
    dis_code = prepared_dis_code(dis_code)

    # convert dis codes to numsed codes
    newcode3 = opcodes(dis_code, trace)

    # return list of instructions
    return newcode3


def opcodes(dis_code, trace=False):
    newcode = []
    newcode.append('STARTUP')

    # add dummy context to be removed by final RETURN_VALUE
    newcode.append('MAKE_CONTEXT')
    # add dummy pointer address to be taken by final RETURN_VALUE
    newcode.append('LOAD_CONST end_of_script')

    # normalize disassembly labels and opcode arguments
    newcode.extend(dis_code)

    # inline helper functions (is_positive, negative, divide_by_ten)
    newcode = inline_helper_opcodes(newcode)

    # handle function arguments and context
    tmp = []
    for instr in newcode:
        if instr.startswith('FUNCTION'):
            x = instr.split()
            name = x[1]
            args = x[2:]
            tmp.append(':%s' % name)
            tmp.append('MAKE_CONTEXT')
            # arguments are pushed first one first by native python compiler,
            # and they have to be popped in reverse order
            for arg in reversed(args):
                tmp.append('STORE_FAST %s' % arg)
        elif instr.startswith('RETURN_VALUE'):
            tmp.append('POP_CONTEXT')
            tmp.append(instr)
        else:
            tmp.append(instr)
    newcode = tmp

    # rename jump opcodes as all are absolute
    tmp = []
    for instr in newcode:
        if re.match('^JUMP_ABSOLUTE|JUMP_FORWARD', instr):
            x = instr.split()
            label = x[1]
            tmp.append('JUMP ' + label)
        else:
            tmp.append(instr)
    newcode = tmp

    # replace INPLACE_* with BINARY_ equivalent
    tmp = []
    for instr in newcode:
        instr = re.sub('^INPLACE_', 'BINARY_', instr)
        tmp.append(instr)
    newcode = tmp

    # clean long int representation (python2)
    tmp = []
    for instr in newcode:
        if re.match('LOAD_CONST +\d+L', instr):
            tmp.append(instr[:-1])
        else:
            tmp.append(instr)
    newcode = tmp

    # handle break: find associated start of loop, retrieve label of end of loop
    # and replace break with jump to end of loop
    for instr_pointer, instr in enumerate(newcode):
        if instr == 'BREAK_LOOP':
            setup_loop = newcode[current_loop(newcode, instr_pointer)]
            endblock_label = setup_loop.split(None, 1)[1]
            newcode[instr_pointer] = 'JUMP ' + endblock_label

    # # TODO: ici ?
    # list_macros = ('BINARY_ADD', 'BINARY_SUBTRACT', 'BINARY_MULTIPLY')
    # newcode3 = normalize('\n'.join(newcode3), macros=list_macros)
    # newcode3 = newcode3.splitlines()

    # trace if requested
    if trace:
        for instr in newcode:
            print instr

    # return list of instructions
    return newcode


def current_loop(opcode, instr_pointer):
    pointer = instr_pointer
    depth = 1
    while depth > 0:
        pointer -= 1
        if opcode[pointer] == 'POP_BLOCK':
            depth += 1
        elif opcode[pointer].startswith('SETUP_LOOP'):
            depth -= 1
        else:
            pass
    assert opcode[pointer].startswith('SETUP_LOOP')
    return pointer


# -- Reading opcode ----------------------------------------------------------


def read_opcode_module(source, trace=False):
    with open(source) as f:
        return f.readlines()


# -- Preparing dis code ------------------------------------------------------


def prepared_dis_code(dis_code):
    """
    Keep only required labels.
    Put labels on their own lines.
    Remove relative jumps and keep explicit labels.
    Keep only explicit arguments.
    Replace reference to function objects by labels.
    """
    newcode = []
    for line in dis_code:
        if line.strip():
            label, instr, arg = parse_dis_instruction(line)
            if label:
                newcode.append(':%s' % label)
            if arg:
                newcode.append('%s %s' % (instr, arg))
            else:
                newcode.append(instr)
    return newcode


def parse_dis_instruction(s):
    #  45 BINARY_MULTIPLY
    #  59 JUMP_ABSOLUTE           27
    #  46 STORE_FAST               5 (aux)
    m = re.search(r'(\d+) (\w+) *(.*)', s)
    label, instr, arg = m.group(1), m.group(2), m.group(3)

    if '>>' not in s:
        label = None

    if not arg:
        arg = None
    elif 'code object' in arg:
        # <code object foo at 030E7EC0, file "exemple01.py", line 1>
        m = re.search('code object ([^ ]+) at ([^ ]+),', arg)
        arg = '%s_%s' % (m.group(1), m.group(2))
    elif '(' in arg:
        m = re.search(r'\((.*)\)', arg)
        arg = m.group(1)
        if arg.startswith('to '):
            arg = arg[3:]
    else:
        arg = arg.strip()

    return label, instr, arg


# -- Other code transformations ----------------------------------------------


def inline_helper_opcodes(code):
    """
    Detect following opcode sequences :

    LOAD_GLOBAL is_positive|negative|divide_by_ten
    XXX
    CALL_FUNCTION 1 labelname
    :labelname

    and replace with

    XXX
    IS_POSITIVE|NEGATIVE|DIVIDE_BY_TEN

    This assumes the helper functions are called with arguments made of
    variables, consts and operators, i.e. no call functions inside the XXX
    sequence of opcodes.
    """

    code2 = []
    i = 0
    while i < len(code):
        opcode = code[i]
        i += 1
        if opcode.startswith('LOAD_CONST'):
            func = opcode.split()[1]
            if (func.startswith('is_positive_') or
                func.startswith('negative_') or
                func.startswith('divide_by_ten_')):
                i += 2
            else:
                code2.append(opcode)
        elif opcode.startswith('LOAD_GLOBAL'):
            func = opcode.split()[1]
            if func not in ('is_positive', 'negative', 'divide_by_ten'):
                code2.append(opcode)
            else:
                argseq = []
                while not code[i].startswith('CALL_FUNCTION'):
                    argseq.append(code[i])
                    i += 1
                i += 1                      # skip call and return label
                code2.extend(argseq)        # append sequence
                code2.append(func.upper())  # append opcode
        elif (opcode.startswith('FUNCTION is_positive_') or
              opcode.startswith('FUNCTION negative_') or
              opcode.startswith('FUNCTION divide_by_ten_')):
            while not code[i].startswith('RETURN_VALUE'):
                i += 1
            i += 1
        else:
            code2.append(opcode)
    return code2


# -- Opcode interpreter ------------------------------------------------------


OPCODES = ('LOAD_CONST', 'LOAD_NAME', 'LOAD_GLOBAL', 'STORE_NAME', 'STORE_GLOBAL',
           'LOAD_FAST', 'STORE_FAST', 'UNARY_NEGATIVE', 'UNARY_POSITIVE',
           'BINARY_ADD', 'BINARY_SUBTRACT', 'BINARY_MULTIPLY', 'BINARY_FLOOR_DIVIDE',
           'COMPARE_OP', 'UNARY_NOT', 'JUMP', 'POP_JUMP_IF_TRUE', 'POP_JUMP_IF_FALSE',
           'JUMP_IF_TRUE_OR_POP', 'JUMP_IF_FALSE_OR_POP', 'PRINT_ITEM', 'PRINT_NEWLINE',
           'MAKE_FUNCTION', 'CALL_FUNCTION', 'RETURN_VALUE', 'SETUP_LOOP', 'POP_BLOCK',
           'STARTUP', 'MAKE_CONTEXT', 'POP_CONTEXT', 'IS_POSITIVE', 'NEGATIVE', 'DIVIDE_BY_TEN')

def interpreter(code, coverage=False):

    stack = list()
    names = dict()
    varnames = list()
    opcodes = list()
    labels = dict()

    for index, x in enumerate(code):
        y = x.split() + [None]
        opc, arg = y[:2]
        if opc[0] == ':':
            opc, arg = opc[0], opc[1:]
            labels[arg] = index
        opcodes.append((opc, arg))

    counter = dict()
    for x in OPCODES:
        counter[x] = 0

    instr_pointer = 0
    while instr_pointer < len(opcodes):
        opc, arg = opcodes[instr_pointer]
        if opc != ':':
            counter[opc] += 1
        #print instr_pointer, opc, arg, stack
        instr_pointer += 1
        if False:
            pass
        elif opc == ':':
            pass
        elif opc == 'LOAD_CONST':
            try:
                x = int(arg)
            except:
                x = arg
            stack.append(x)
        elif opc == 'LOAD_NAME' or opc == 'LOAD_GLOBAL':
            stack.append(names[arg])
        elif opc == 'STORE_NAME' or opc == 'STORE_GLOBAL':
            names[arg] = stack.pop()
        elif opc == 'LOAD_FAST':
            stack.append(varnames[-1][arg])
        elif opc == 'STORE_FAST':
            varnames[-1][arg] = stack.pop()
        elif opc == 'ROT_THREE':
            # stack in  = [... z y x]
            # stack out = [... x z y]
            x = stack.pop()
            y = stack.pop()
            z = stack.pop()
            stack.extend([x, z, y])
        elif opc == 'UNARY_NEGATIVE':
            tos = stack.pop()
            stack.append(-tos)
        elif opc == 'UNARY_POSITIVE':
            tos = stack.pop()
            stack.append(+tos)
        elif opc == 'BINARY_ADD':
            tos = stack.pop()
            tos1 = stack.pop()
            stack.append(tos1 + tos)
        elif opc == 'BINARY_SUBTRACT':
            tos = stack.pop()
            tos1 = stack.pop()
            stack.append(tos1 - tos)
        elif opc == 'BINARY_MULTIPLY':
            tos = stack.pop()
            tos1 = stack.pop()
            stack.append(tos1 * tos)
        elif opc == 'BINARY_FLOOR_DIVIDE':
            tos = stack.pop()
            tos1 = stack.pop()
            stack.append(tos1 // tos)
        elif opc == 'UNARY_NOT':
            tos = stack.pop()
            stack.append(1 if tos == 0 else 0)
        elif opc == 'COMPARE_OP':
            tos = stack.pop()
            tos1 = stack.pop()
            if arg == '==':
                stack.append(tos1 == tos)
            elif arg == '!=':
                stack.append(tos1 != tos)
            elif arg == '<':
                stack.append(tos1 < tos)
            elif arg == '>':
                stack.append(tos1 > tos)
            elif arg == '<=':
                stack.append(tos1 <= tos)
            elif arg == '>=':
                stack.append(tos1 >= tos)
            else:
                raise Exception('numsed: unknown compare operator: %s' % arg)
        elif opc == 'JUMP':
            instr_pointer = labels[arg]
        elif opc == 'POP_JUMP_IF_TRUE':
            tos = stack.pop()
            if tos:
                instr_pointer = labels[arg]
        elif opc == 'POP_JUMP_IF_FALSE':
            tos = stack.pop()
            if not tos:
                instr_pointer = labels[arg]
        elif opc == 'JUMP_IF_TRUE_OR_POP':
            if stack[-1]:
                instr_pointer = labels[arg]
            else:
                tos = stack.pop()
        elif opc == 'JUMP_IF_FALSE_OR_POP':
            if not stack[-1]:
                instr_pointer = labels[arg]
            else:
                tos = stack.pop()
        elif opc == 'PRINT_ITEM':
            tos = stack.pop()
            print tos,
        elif opc == 'PRINT_NEWLINE':
            print
        elif opc == 'MAKE_FUNCTION':
            if int(arg) >= 256:
                raise Exception('numsed: keyword parameters not handled')
            else:
                pass
        elif opc == 'CALL_FUNCTION':
            # argc parameters on top of stack above name of function
            # first, add return address and swap parameters and name
            args = list()
            for i in range(int(arg)):
                args.append(stack.pop())
            func = stack.pop()
            stack.append(instr_pointer)
            for i in range(int(arg)):
                stack.append(args.pop())
            instr_pointer = labels[func]
        elif opc == 'RETURN_VALUE':
            ret_value = stack.pop()
            ret_pointer = stack.pop()
            instr_pointer = ret_pointer
            stack.append(ret_value)
        elif opc == 'SETUP_LOOP':
            pass
        elif opc == 'POP_BLOCK':
            pass
        elif opc == 'STARTUP':
            pass
        elif opc == 'MAKE_CONTEXT':
            varnames.append(dict())
        elif opc == 'POP_CONTEXT':
            varnames.pop()
        elif opc == 'IS_POSITIVE':
            tos = stack.pop()
            stack.append(tos >= 0)
        elif opc == 'NEGATIVE':
            tos = stack.pop()
            stack.append(-tos)
        elif opc == 'DIVIDE_BY_TEN':
            tos = stack.pop()
            stack.append(tos // 10)
        elif opc == 'TRACE':
            pass
        else:
            raise Exception('numsed: Unknown opcode: %s' % opc)

    if coverage:
        for x in OPCODES:
            print '%-20s %10d' % (x, counter[x])
