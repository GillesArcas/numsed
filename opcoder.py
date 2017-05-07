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
    newcode3, function_labels, return_labels = opcodes(dis_code, trace)

    # return list of instructions
    return newcode3, function_labels, return_labels


def opcodes(dis_code, trace=False):
    newcode = []
    newcode.append('STARTUP')

    # add dummy context to be removed by final RETURN_VALUE
    newcode.append('MAKE_CONTEXT')
    # add dummy pointer address to be taken by final RETURN_VALUE
    newcode.append('LOAD_CONST EndOfScript')

    # normalize disassembly labels and opcode arguments
    newcode.extend(dis_code)

    # inline helper functions (is_positive, negative, divide_by_ten)
    newcode = inline_helper_opcodes(newcode)

    # create list of function labels and list of return labels
    function_labels = []
    return_labels = []
    newcode2 = []
    for instr in newcode:
        if instr.startswith('FUNCTION'):
            name = instr.split()[1]
            function_labels.append(name)
            newcode2.append(instr)
        elif instr.startswith('CALL_FUNCTION'):
            label = new_label()
            return_labels.append(label)
            newcode2.append('%s %s' % (instr, label))
            newcode2.append(':%s' % label)
        else:
            newcode2.append(instr)

    # handle function arguments and context
    newcode3 = []
    for instr in newcode2:
        if instr.startswith('FUNCTION'):
            x = instr.split()
            name = x[1]
            args = x[2:]
            newcode3.append(':%s' % name)
            newcode3.append('MAKE_CONTEXT')
            # arguments are pushed first one first by native python compiler,
            # and they have to be popped in reverse order
            for arg in reversed(args):
                newcode3.append('STORE_FAST %s' % arg)
        elif instr.startswith('RETURN_VALUE'):
            newcode3.append('POP_CONTEXT')
            newcode3.append(instr)
        else:
            newcode3.append(instr)

    # rename jump opcodes as all are absolute
    tmp = []
    for instr in newcode3:
        if instr.startswith('JUMP_'):
            x = instr.split()
            label = x[1]
            tmp.append('JUMP ' + label)
        else:
            tmp.append(instr)
    newcode3 = tmp

    # replace INPLACE_* with BINARY_ equivalent
    tmp = []
    for instr in newcode3:
        instr = re.sub('^INPLACE_', 'BINARY_', instr)
        tmp.append(instr)
    newcode3 = tmp

    # clean long int representation (python2)
    tmp = []
    for instr in newcode3:
        if re.match('LOAD_CONST +\d+L', instr):
            tmp.append(instr[:-1])
        else:
            tmp.append(instr)
    newcode3 = tmp

    # # TODO: ici ?
    # list_macros = ('BINARY_ADD', 'BINARY_SUBTRACT', 'BINARY_MULTIPLY')
    # newcode3 = normalize('\n'.join(newcode3), macros=list_macros)
    # newcode3 = newcode3.splitlines()

    # trace if requested
    if trace:
        for instr in newcode3:
            print instr

    # return list of instructions
    return newcode3, function_labels, return_labels


label_counter = 0
def new_label():
    global label_counter
    r = 'return%d' % label_counter
    label_counter += 1
    return r


# -- Reading opcode ----------------------------------------------------------


def read_opcode_module(source, trace=False):
    with open(source) as f:
        opcode = f.readlines()

    function_labels = []
    return_labels = []

    for instr in opcode:
        if re.match(r':\w+_[0-9A-Z]{8}', instr):
            function_labels.append(instr[1:].strip())
        elif re.match(r':return\d+', instr):
            return_labels.append(instr[1:].strip())
        else:
            pass

    return opcode, function_labels, return_labels


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


def interpreter(code):

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

    instr_pointer = 0
    while instr_pointer < len(opcodes):
        opc, arg = opcodes[instr_pointer]
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
            #print names
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
            # TODO: optimize
            tos = stack.pop()
            stack.append(-tos)
        elif opc == 'UNARY_POSITIVE':
            # TODO: NOP like
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
            assert tos in (0, 1)
            stack.append(1 - tos)
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
