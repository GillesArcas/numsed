"""
Generating and interpreting numsed opcodes.
"""

from __future__ import print_function

import sys
import re
import dis
import types
import shutil

import common
import transformer
import numsed_lib


# -- Disassembly -------------------------------------------------------------


class DisassemblyConversion(common.NumsedConversion):
    def __init__(self, source, transformation):
        common.NumsedConversion.__init__(self, source, transformation)
        script_trans = transformer.ScriptConversion(source, transformation)
        with open('~.py', 'wt') as f:
            f.write(script_trans.trace())
        self.code = disassemble('~.py')
    def trace(self):
        return '\n'.join(self.code)


IS64BITS = sys.maxsize > 2**32


def disassemble(source):

    # compile
    with open(source) as f:
        script = f.read()
        code = compile(script, source, "exec")

    with common.ListStream() as x:
        dis.dis(code)
        for oparg in code.co_consts:
            if isinstance(oparg, types.CodeType):
                func_code = oparg
                padded_id = ('%016X' if IS64BITS else '%08X') % id(func_code)
                print('\n', ' ' * 11, '%-29s %s_%s %s' % ('-1 FUNCTION',
                                                    func_code.co_name,
                                                    padded_id,
                                                    ' '.join(func_code.co_varnames[:func_code.co_argcount])))
                dis.disassemble(func_code)

    code = x.stringlist()

    # return list of instructions
    return code


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
    for line in dis_code.splitlines():
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
        m = re.search('code object ([^ ]+) at (?:0x)?([^ ]+),', arg)
        arg = '%s_%s' % (m.group(1), m.group(2))
    elif '(' in arg:
        m = re.search(r'\((.*)\)', arg)
        arg = m.group(1)
        if arg.startswith('to '):
            arg = arg[3:]
    else:
        arg = arg.strip()

    return label, instr, arg


# -- Disassemble to numsed opcodes -------------------------------------------


class OpcodeConversion(common.NumsedConversion):
    def __init__(self, source, transformation):
        common.NumsedConversion.__init__(self, source, transformation)
        if source.endswith('.py'):
            x = DisassemblyConversion(source, transformation)
            dis_code = x.trace()
            self.opcode = opcodes(dis_code)
        elif source.endswith('.opc'):
            with open(source) as f:
                self.opcode = [_.rstrip() for _ in f.readlines()]
        else:
            raise Exception('Invalid file type')

    def trace(self):
        return '\n'.join(self.opcode)

    def run(self):
        with common.ListStream() as x:
            interpreter(self.opcode, coverage=False)
        return x.singlestring()

    def coverage(self):
        return'\n'.join(interpreter(self.opcode, coverage=True))


def opcodes(dis_code):
    # simplify dis code
    dis_code = prepared_dis_code(dis_code)

    newcode = []
    newcode.append('STARTUP')

    # add dummy context to be removed by final RETURN_VALUE
    newcode.append('MAKE_CONTEXT')

    # add print declaration
    newcode.extend(PRINT_DECL())

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

    # rename jump opcodes
    tmp = []
    for instr in newcode:
        if re.match('^JUMP_ABSOLUTE|JUMP_FORWARD', instr):
            x = instr.split()
            label = x[1]
            tmp.append('JUMP ' + label)
        else:
            tmp.append(instr)
    newcode = tmp

    # link
    link_opcode(newcode)

    # replace INPLACE_* with BINARY_ equivalent
    tmp = []
    for instr in newcode:
        instr = re.sub('^INPLACE_', 'BINARY_', instr)
        tmp.append(instr)
    newcode = tmp

    # clean long int representation (python2)
    tmp = []
    for instr in newcode:
        if re.match(r'LOAD_CONST +\d+L', instr):
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

    # ignore some opcodes
    tmp = []
    for instr in newcode:
        x = instr.split()
        opc = x[0]
        arg = x[1] if len(x) > 1 else None
        if opc == 'EXTENDED_ARG':
            pass # used in py3 for comparison operators, useless here, operators
                 # have been written in argument position
        elif opc == 'LOAD_CONST' and re.match(r"^'.*'$", arg):
            pass # use in py3, the name of a function is pushed before MAKE_FUNCTION
                 # there is no other string hanfled in numsed
        elif opc == 'STORE_NAME' and arg in numsed_lib.PRIMITIVES:
            pass # use in py3
        else:
            tmp.append(instr)
    newcode = tmp

    # add print definition
    newcode.extend(PRINT())

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


# -- Other code transformations ----------------------------------------------


def primitive_opcode(func):
    return func.upper()


def inline_helper_opcodes(code):
    """
    Detect following opcode sequences:

        LOAD_GLOBAL is_positive|negative|is_odd|divide_by_two
        XXX
        CALL_FUNCTION 1 labelname
        :labelname

    and replace with:

        XXX
        IS_POSITIVE|NEGATIVE|IS_ODD|DIVIDE_BY_TWO

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
            if any(func.startswith(_) for _ in numsed_lib.PRIMITIVES):
                i += 2
            else:
                code2.append(opcode)
        elif opcode.startswith('LOAD_GLOBAL'):
            func = opcode.split()[1]
            if func not in numsed_lib.PRIMITIVES:
                code2.append(opcode)
            else:
                argseq = []
                while not code[i].startswith('CALL_FUNCTION'):
                    argseq.append(code[i])
                    i += 1
                i += 1                                      # skip call and return label
                code2.extend(argseq)                        # append sequence
                code2.append(primitive_opcode(func))        # append opcode
        elif any(opcode.startswith('FUNCTION ' + _) for _ in numsed_lib.PRIMITIVES):
            while not code[i].startswith('RETURN_VALUE'):
                i += 1
            i += 1
        else:
            code2.append(opcode)
    return code2


# print() is also a primitive but is handled as a function. Its opcode
# snippets are inserted directly into opcodes in opcodes() function.


def PRINT_DECL():
    return (
        'LOAD_CONST               print',
        'MAKE_FUNCTION            0',
        'STORE_NAME               print'
    )


def PRINT():
    return (                            # PS: ?         HS: N;label;X
        ':print',
        'PRINT_ITEM',                   # PS: N         HS: label;X
        'PRINT_NEWLINE',
        'LOAD_CONST 0',                 # PS: N         HS: 0;label;X
        'RETURN_VALUE'
    )


def link_opcode(code):
    # after disassembly of functions by dis-ing on module, labels in each
    # function starts from 0. Update labels to have separate name spaces.

    offset = 0
    maxlabel = 0
    for index, instr in enumerate(code):
        if instr.strip() == '':
            continue
        if re.match(r':\w+_[0-9A-Z]{8}', instr):        # attention !!! c'est la syntaxe dis patche !!!
            offset = maxlabel + 2
            continue
        if instr.startswith(':'):
            label = offset + int(instr[1:])
            code[index] = ':%d' % label
            if label > maxlabel:
                maxlabel = label

        if instr_with_label(instr):
            opc, arg = instr.split()
            label = offset + int(arg)
            code[index] = '%s %d' % (opc, label)


def instr_with_label(instr):
    return 'JUMP' in instr or instr.startswith('SETUP_LOOP')


# -- Opcode interpreter ------------------------------------------------------


OPCODES = ('LOAD_CONST', 'LOAD_NAME', 'LOAD_GLOBAL', 'STORE_NAME', 'STORE_GLOBAL',
           'LOAD_FAST', 'STORE_FAST',
           'POP_TOP', 'DUP_TOP', 'ROT_TWO', 'ROT_THREE',
           'UNARY_NEGATIVE', 'UNARY_POSITIVE',
           'BINARY_ADD', 'BINARY_SUBTRACT', 'BINARY_MULTIPLY',
           'BINARY_FLOOR_DIVIDE', 'BINARY_MODULO', 'BINARY_POWER',
           'COMPARE_OP', 'UNARY_NOT', 'JUMP', 'POP_JUMP_IF_TRUE', 'POP_JUMP_IF_FALSE',
           'JUMP_IF_TRUE_OR_POP', 'JUMP_IF_FALSE_OR_POP', 'PRINT_ITEM', 'PRINT_NEWLINE',
           'MAKE_FUNCTION', 'CALL_FUNCTION', 'RETURN_VALUE', 'SETUP_LOOP', 'POP_BLOCK',
           'STARTUP', 'MAKE_CONTEXT', 'POP_CONTEXT',
           'IS_POSITIVE', 'NEGATIVE', 'IS_ODD', 'DIVIDE_BY_TWO')

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

    # add label for final RETURN_VALUE
    stack.append(1000000000)

    counter = dict()
    for x in OPCODES:
        counter[x] = 0

    result = []

    instr_pointer = 0
    while instr_pointer < len(opcodes):
        opc, arg = opcodes[instr_pointer]
        if opc != ':':
            if opc in OPCODES:
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
        elif opc == 'POP_TOP':
            _ = stack.pop()
        elif opc == 'DUP_TOP':
            stack.append(stack[-1])
        elif opc == 'ROT_TWO':
            # stack in  = [... y x]
            # stack out = [... x y]
            x = stack.pop()
            y = stack.pop()
            stack.extend([x, y])
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
        elif opc == 'BINARY_MODULO':
            tos = stack.pop()
            tos1 = stack.pop()
            stack.append(tos1 % tos)
        elif opc == 'BINARY_POWER':
            tos = stack.pop()
            tos1 = stack.pop()
            stack.append(tos1 ** tos)
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
            print(tos, end='')
            if not result:
                result.append('')
            result[-1] += '%s' % tos
        elif opc == 'PRINT_NEWLINE':
            print()
            result.append('')
        elif opc == 'MAKE_FUNCTION':
            if int(arg) >= 256:
                raise Exception('numsed: keyword parameters not handled')
            else:
                pass
        elif opc == 'CALL_FUNCTION':
            # argc parameters on top of stack above name of function
            # first, add return address and swap parameters and name
            args = list()
            for _ in range(int(arg)):
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
        elif opc == 'IS_ODD':
            tos = stack.pop()
            stack.append(tos % 2)
        elif opc == 'DIVIDE_BY_TWO':
            tos = stack.pop()
            stack.append(tos // 2)
        elif opc == 'TRACE':
            pass
        else:
            raise Exception('numsed: Unknown opcode: %s' % opc)

    if coverage:
        for x in OPCODES:
            print('%-20s %10d' % (x, counter[x]))
        return ''
    else:
        return result


if __name__ == "__main__":
    pass
