"""
Prepare a python program (tiny subset) for compilation into sed.
Transform into positive form:
- all operators and binary comparisons are replaced with call to functions
  x + y --> signed_add(x, y), idem -, *, //, ==, !=, <, <=, >, >=
- all operands of operators and binary comparisons inside signed_xxx functions
  must be positive integers.
- two functions handling negative values remain: is_positive and negative. They
  are treated separately when testing python positive form or compiling into sed.
- augmented assignments are replaced with simple assignments.

A testing mode of the transformer program generates code testing that arguments
of operators and comparisons are positive.
"""

from __future__ import division, print_function

import sys
import inspect
import operator
import ast
import codegen
from numsed_lib import *


# -- Transformer --------------------------------------------------------------


signed_func = {
    ast.Add: 'signed_add',
    ast.Sub: 'signed_sub',
    ast.Mult: 'signed_mult',
    ast.FloorDiv: 'signed_div',
    ast.Mod: 'signed_mod',
    ast.Eq: 'signed_eq',
    ast.NotEq: 'signed_noteq',
    ast.Lt: 'signed_lt',
    ast.LtE: 'signed_lte',
    ast.Gt: 'signed_gt',
    ast.GtE: 'signed_gte'}

unsigned_func = {  # assert_unsigned_func
    ast.Add: 'unsigned_add',
    ast.Sub: 'unsigned_sub',
    ast.Mult: 'unsigned_mult',
    ast.FloorDiv: 'unsigned_div',
    ast.Mod: 'unsigned_mod',
    ast.Eq: 'unsigned_eq',
    ast.NotEq: 'unsigned_noteq',
    ast.Lt: 'unsigned_lt',
    ast.LtE: 'unsigned_lte',
    ast.Gt: 'unsigned_gt',
    ast.GtE: 'unsigned_gte'}


class NumsedAstTransformer(ast.NodeTransformer):

    def __init__(self, func):
        self.func = func
        self.required_func = set()

    def make_call(self, func, args):
        self.required_func.add(func)
        return ast.Call(func=ast.Name(id=func, ctx=ast.Load()),
                        args=args,
                        keywords=[], starargs=None, kwargs=None)

    def visit_BinOp(self, node):
        self.generic_visit(node)
        if type(node.op) in self.func:
            return self.make_call(self.func[type(node.op)], [node.left, node.right])
        else:
            raise Exception('Operator not handled: ' + str(type(node.op)))

    def visit_Compare(self, node):
        self.generic_visit(node)
        left = node.left
        ops = node.ops
        comparators = node.comparators
        if len(ops) == 1:
            return self.make_call(self.func[type(node.ops[0])], [node.left, comparators[0]])
        else:
            list_compare = []
            while ops:
                compare = self.make_call(self.func[type(ops[0])], [left, comparators[0]])
                list_compare.append(compare)
                left = comparators[0]
                ops = ops[1:]
                comparators = comparators[1:]
            return ast.BoolOp(op=ast.And(), values=list_compare)

    def visit_AugAssign(self, node):
        # AugAssign(target=Name(id='x', ctx=Store()), op=Add(), value=Num(n=1)),
        # Assign(targets=[Name(id='x', ctx=Store())], value=BinOp(left=Name(id='x', ctx=Load()), op=Add(), right=Num(n=1)))])
        #self.generic_visit(node)
        target = node.target
        source = ast.Name(id=target.id, ctx=ast.Load())
        return ast.Assign(targets=[target], value=self.visit_BinOp(ast.BinOp(left=source, op=node.op, right=node.value)))

    def visit_FunctionDef(self, node):
        if node.name in PRIMITIVES:
            return node
        else:
            self.generic_visit(node)
            return node


# -- Testing transformation --------------------------------------------------


unsigned_func_pattern = """
def %s(x, y):
    assert x >= 0, 'x < 0'
    assert y >= 0, 'y < 0'
    return x %s y
"""

unsigned_op = {
    'unsigned_add': '+',
    'unsigned_sub': '-',
    'unsigned_mult': '*',
    'unsigned_div': '//',
    'unsigned_mod': '%',
    'unsigned_eq': '==',
    'unsigned_noteq': '!=',
    'unsigned_lt': '<',
    'unsigned_lte': '<=',
    'unsigned_gt': '>',
    'unsigned_gte': '>='}


def make_unsigned_func(name):
    return unsigned_func_pattern % (name, unsigned_op[name])


# -- List of library functions -----------------------------------------------


class NumsedAstVisitor(ast.NodeVisitor):

    def __init__(self):
        self.required_func = set()

    def visit_Call(self, node):
        self.generic_visit(node)
        if type(node.func) is ast.Name:
            self.required_func.add(node.func.id)


def function_calls(libfuncs):
    """
    Argument is the list of library functions called in script
    Output is the list of all library functions required in script
    """
    libfuncs2 = set()
    while libfuncs:
        func = libfuncs.pop()
        libfuncs2.add(func)
        textfunc = '\n'.join(inspect.getsourcelines(globals()[func])[0])
        tree = ast.parse(textfunc)
        numsed_ast_visitor = NumsedAstVisitor()
        numsed_ast_visitor.visit(tree)
        for func in numsed_ast_visitor.required_func:
            if func not in libfuncs and func not in libfuncs2:
                libfuncs.add(func)
    return libfuncs2


# -- Main --------------------------------------------------------------------


def save_new_script(tree, libfuncs, script_out):
    # add builtins functions to code to compile
    script = ''
    # script += 'import operator\n\n'
    for func in libfuncs:
        script += '\n'
        script += ''.join(inspect.getsourcelines(func)[0])
    script += '\n'
    script += codegen.to_source(tree)

    with open(script_out, 'w') as f:
        f.writelines(script)

    return script


def transform_positive(script_in, script_out, do_exec):
    tree = ast.parse(open(script_in).read())
    numsed_ast_transformer = NumsedAstTransformer(signed_func)
    numsed_ast_transformer.visit(tree)

    libfuncs = numsed_ast_transformer.required_func
    libfuncs2 = function_calls(libfuncs)
    libfuncs = [globals()[x] for x in libfuncs2]

    return save_new_script(tree, libfuncs, script_out)


def transform_assert(script_in, script_out, do_exec):
    tree = ast.parse(open(script_in).read())
    test_exec(tree, do_exec)
    numsed_ast_transformer = NumsedAstTransformer(unsigned_func)
    numsed_ast_transformer.visit(tree)
    test_exec(tree, do_exec)

    # add builtins functions to code to compile
    builtins = numsed_ast_transformer.required_func
    script = ''
    for func in builtins:
        script += '\n'
        script += make_unsigned_func(func)
    script += '\n'
    # script += 'import operator\n\n'
    script += codegen.to_source(tree)

    with open(script_out, 'w') as f:
        f.writelines(script)


def test_exec(tree, do_exec):
    if do_exec:
        ast.fix_missing_locations(tree)
        print(ast.dump(tree))
        exec(compile(tree, filename="<ast>", mode="exec"))


def transform(script_in, script_out, do_assert=False, do_exec=False):
    code = transform_positive(script_in, script_out, do_exec)
    if do_assert:
        code = transform_assert(script_out, script_out, do_exec)
    return code


# -- Main --------------------------------------------------------------------


def main():
    script_in = sys.argv[1]
    script_out = sys.argv[2]
    do_assert = False
    do_exec = True
    transform(script_in, script_out, do_assert, do_exec)


if __name__ == "__main__":
    main()
