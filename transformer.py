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
import types
import operator
import ast
import codegen
import numsed_lib
from numsed_lib import *


# -- Syntax checking Transformer ---------------------------------------------


class NumsedCheckAstVisitor(ast.NodeVisitor):

    def __init__(self, source_functions):
        # list of functions defined in lib
        self.lib_functions = {x[0] for x in inspect.getmembers(numsed_lib, inspect.isfunction)}
        self.lib_functions.add('print')

        self.defined_functions = source_functions.union(self.lib_functions)

        self.inside_funcdef = False

    def visit_Module(self, node):
        for _ in node.body: self.visit(_)

    def visit_Assign(self, node):
        for _ in node.targets: self.visit(_)
        self.visit(node.value)

    def visit_AugAssign(self, node):
        self.visit(node.target)
        self.visit(node.value)

    def visit_Expr(self, node):
        self.visit(node.value)

    def visit_Name(self, node):
        pass

    def visit_Num(self, node):
        if not isinstance(node.n, int) and not isinstance(node.n, long):
            check_error('not an integer', node.n, node)

    def visit_UnaryOp(self, node):
        if type(node.op) not in [ast.UAdd, ast.USub, ast.Not]:
            check_error('unknown operator', node.op, node)
        self.visit(node.operand)

    def visit_BinOp(self, node):
        if type(node.op) not in signed_func:
            check_error('unknown operator', type(node.op), node)
        self.visit(node.left)
        self.visit(node.right)

    def visit_Print(self, node):
        if len(node.values) != 1 or node.dest is not None or  node.nl is False:
            check_error('incorrect print', node.func.id, node)
        else:
            self.visit(node.values[0])

    def visit_Call(self, node):
        if type(node.func) is ast.Name:
            if node.func.id not in self.defined_functions:
                check_error('function is not defined', node.func.id, node)
            elif node.func.id == 'print' and len(node.args) != 1:
                check_error('print admits only one argument', node.func.id, node)
            else:
                for _ in node.args: self.visit(_)
        else:
            check_error('callable not handled', node.func, node)

    def visit_Compare(self, node):
        for op in node.ops:
            if type(op) not in (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE):
                check_error('comparator not handled', type(op), node)
            else:
                self.visit(node.left)
                for _ in node.comparators: self.visit(_)

    def visit_BoolOp(self, node):
        for _ in node.values: self.visit(_)

    def visit_IfExp(self, node):
        self.visit(node.test)
        self.visit(node.body)
        self.visit(node.orelse)

    def visit_If(self, node):
        self.visit(node.test)
        for _ in node.body: self.visit(_)
        for _ in node.orelse: self.visit(_)

    def visit_While(self, node):
        self.visit(node.test)
        for _ in node.body: self.visit(_)
        for _ in node.orelse: self.visit(_)

    def visit_Break(self, node):
        pass

    def visit_Continue(self, node):
        pass

    def visit_Return(self, node):
        self.visit(node.value)

    def visit_Global(self, node):
        pass

    def visit_FunctionDef(self, node):
        if self.inside_funcdef:
            check_error('no nested function definitions', node.name, node)
        if node.name in self.lib_functions:
            check_error('not allowed to redefine functions', node.name, node)
        if node.args.vararg is not None:
            check_error('no vararg', node.args.vararg, node)
        if node.args.kwarg is not None:
            check_error('no kwarg', node.args.kwarg, node)
        if len(node.args.defaults) > 0:
            check_error('no defaults', node.args.defaults, node)
        self.inside_funcdef = True
        for _ in node.body: self.visit(_)
        self.inside_funcdef = False

    def generic_visit(self, node):
        # print(node)
        # print(dir(node))
        # print(ast.dump(node))
        check_error('construct is not handled', type(node), node)


def check(source):
    # compile for syntax verification
    with open(source) as f:
        script = f.read()
        code = compile(script, source, "exec")

    # list of functions defined in source
    source_functions = {x.co_name for x in code.co_consts if isinstance(x, types.CodeType)}

    tree = ast.parse(script)
    #print(ast.dump(tree))
    numsed_check_ast_visitor = NumsedCheckAstVisitor(source_functions)
    numsed_check_ast_visitor.visit(tree)


def check_error(msg, arg, node):
    print('numsed: line %d col %d: %s : %s' % (node.lineno, node.col_offset, msg, arg))
    exit(1)


# -- Transformer -------------------------------------------------------------


class NumsedAstTransformer(ast.NodeTransformer):

    def __init__(self, func):
        """
        func is a dict giving the functions replacing operators. Can be
        the functions from library, or testing functions checking all
        operands are positive.
        """
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


# -- Positive transformation -------------------------------------------------


def transform_positive(script_in, script_out, do_exec):
    tree = ast.parse(open(script_in).read())
    numsed_ast_transformer = NumsedAstTransformer(signed_func)
    numsed_ast_transformer.visit(tree)

    libfuncs = numsed_ast_transformer.required_func
    libfuncs2 = function_calls(libfuncs)
    libfuncs = [globals()[x] for x in libfuncs2]

    return save_new_script(tree, libfuncs, getsourcetext, script_out)


signed_func = {
    ast.Add: 'signed_add',
    ast.Sub: 'signed_sub',
    ast.Mult: 'signed_mult',
    ast.FloorDiv: 'signed_div',
    ast.Mod: 'signed_mod',
    ast.Pow: 'signed_pow',
    ast.Eq: 'signed_eq',
    ast.NotEq: 'signed_noteq',
    ast.Lt: 'signed_lt',
    ast.LtE: 'signed_lte',
    ast.Gt: 'signed_gt',
    ast.GtE: 'signed_gte'}


def getsourcetext(func):
    return ''.join(inspect.getsourcelines(func)[0])


def save_new_script(tree, libfuncs, func_text, script_out):
    # add library functions to code to compile
    script = ''
    for func in libfuncs:
        script += '\n'
        script += func_text(func)
    script += '\n'
    script += codegen.to_source(tree)

    with open(script_out, 'w') as f:
        f.writelines(script)

    return script


# -- Testing transformation --------------------------------------------------


def transform_assert(script_in, script_out, do_exec):
    tree = ast.parse(open(script_in).read())
    numsed_ast_transformer = NumsedAstTransformer(unsigned_func)
    numsed_ast_transformer.visit(tree)
    test_exec(tree, do_exec)

    libfuncs = numsed_ast_transformer.required_func

    return save_new_script(tree, libfuncs, make_unsigned_func, script_out)


unsigned_func = {  # assert_unsigned_func
    ast.Add: 'unsigned_add',
    ast.Sub: 'unsigned_sub',
    ast.Mult: 'unsigned_mult',
    ast.FloorDiv: 'unsigned_div',
    ast.Mod: 'unsigned_mod',
    ast.Mod: 'unsigned_pow',
    ast.Eq: 'unsigned_eq',
    ast.NotEq: 'unsigned_noteq',
    ast.Lt: 'unsigned_lt',
    ast.LtE: 'unsigned_lte',
    ast.Gt: 'unsigned_gt',
    ast.GtE: 'unsigned_gte'}


unsigned_func_pattern = """
def %s(x, y):
    assert x >= 0, 'x < 0'
    assert y >= 0, 'y < 0'
    return x %s y
"""


def make_unsigned_func(name):

    unsigned_op = {
        'unsigned_add': '+',
        'unsigned_sub': '-',
        'unsigned_mult': '*',
        'unsigned_div': '//',
        'unsigned_mod': '%',
        'unsigned_pow': '**',
        'unsigned_eq': '==',
        'unsigned_noteq': '!=',
        'unsigned_lt': '<',
        'unsigned_lte': '<=',
        'unsigned_gt': '>',
        'unsigned_gte': '>='}

    return unsigned_func_pattern % (name, unsigned_op[name])


# -- Main --------------------------------------------------------------------


def test_exec(tree, do_exec):
    if do_exec:
        ast.fix_missing_locations(tree)
        print(ast.dump(tree))
        exec(compile(tree, filename="<ast>", mode="exec"))


def transform(script_in, script_out, do_assert=False, do_exec=False):
    check(script_in)
    code = transform_positive(script_in, script_out, do_exec)
    if do_assert:
        code = transform_assert(script_out, script_out, do_exec)
    return code


def main():
    script_in = sys.argv[1]
    script_out = sys.argv[2]
    do_assert = False
    do_exec = True
    transform(script_in, script_out, do_assert, do_exec)


if __name__ == "__main__":
    main()
