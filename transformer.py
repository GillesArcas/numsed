"""
Prepare a numsed python program for compilation into sed.
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
import ast
import subprocess
import codegen
import common
import numsed_lib
from numsed_lib import *


LITERAL, UNSIGNED, SIGNED = range(3)
FUTURE_FUNCTION = 'from __future__ import print_function\n'


# -- Unsigned transformer ----------------------------------------------------


class UnsignedTransformer(ast.NodeTransformer):

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
            return node

    def visit_AugAssign(self, node):
        # AugAssign(target=Name(id='x', ctx=Store()), op=Add(), value=Num(n=1)),
        # Assign(targets=[Name(id='x', ctx=Store())], value=BinOp(left=Name(id='x', ctx=Load()), op=Add(), right=Num(n=1)))])
        # self.generic_visit(node)
        if type(node.op) in self.func:
            target = node.target
            source = ast.Name(id=target.id, ctx=ast.Load())
            return ast.Assign(targets=[target], value=self.visit_BinOp(ast.BinOp(left=source, op=node.op, right=node.value)))
        else:
            self.generic_visit(node)
            return node

    def visit_FunctionDef(self, node):
        if node.name in PRIMITIVES:
            return node
        else:
            self.generic_visit(node)
            return node

    def visit_Call(self, node):
        self.generic_visit(node)
        return node


# -- Signed transformer ------------------------------------------------------


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

    def visit_Call(self, node):
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
    return sorted(list(libfuncs2))


# -- Unsigned transformation -------------------------------------------------


def transform_unsigned(script_in, script_out, include_prim_def=True):
    tree = ast.parse(open(script_in).read())
    numsed_ast_transformer = UnsignedTransformer(Unsigned_func)
    numsed_ast_transformer.visit(tree)

    libfuncs = numsed_ast_transformer.required_func
    libfuncs2 = function_calls(libfuncs)
    if include_prim_def is False:
        for func in numsed_lib.PRIMITIVES:
            if func in libfuncs2:
                libfuncs2.remove(func)
    libfuncs = [globals()[x] for x in libfuncs2]
    return save_new_script(tree, libfuncs, getsourcetext, script_out)


Unsigned_func = {
    ast.FloorDiv: 'udiv',
    ast.Mod: 'umod',
    ast.Pow: 'upow'}


# -- Positive transformation -------------------------------------------------


def transform_positive(script_in, script_out, include_prim_def=True):
    tree = ast.parse(open(script_in).read())
    numsed_ast_transformer = NumsedAstTransformer(signed_func)
    numsed_ast_transformer.visit(tree)

    libfuncs = numsed_ast_transformer.required_func
    libfuncs2 = function_calls(libfuncs)
    if include_prim_def is False:
        for func in numsed_lib.PRIMITIVES:
            if func in libfuncs2:
                libfuncs2.remove(func)
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


def transform_assert(script_in, script_out):
    tree = ast.parse(open(script_in).read())
    numsed_ast_transformer = NumsedAstTransformer(unsigned_func)
    numsed_ast_transformer.visit(tree)

    libfuncs = numsed_ast_transformer.required_func
    for func in numsed_lib.PRIMITIVES:
        if func in libfuncs:
            libfuncs.remove(func)

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


# -- AST pretty print --------------------------------------------------------
#
# adapted from http://code.activestate.com/recipes/533146-ast-pretty-printer/


def pprint_ast(astree, indent='  ', stream=sys.stdout):
    rec_node(astree, 0, indent, stream.write)
    stream.write('\n')


def rec_node(node, level, indent, write):
    pfx = indent * level
    if (common.PY2 and isinstance(node, (ast.Name, ast.Num)) or
        common.PY3 and isinstance(node, (ast.Name, ast.Num, ast.arg))):
        print(pfx, ast.dump(node), sep='', end='')

    elif isinstance(node, ast.AST):
        print(pfx, node.__class__.__name__, '(', sep='', end='')

        if any(isinstance(child, ast.AST) for child in ast.iter_child_nodes(node)):
            for i, child in enumerate(ast.iter_child_nodes(node)):
                if i != 0:
                    print(',', end='')
                print()
                rec_node(child, level+1, indent, write)
            print()
            print(pfx, sep='', end='')
        else:
            # None of the children as nodes, simply join their repr on a single line.
            print(', '.join(repr(child) for child in ast.iter_child_nodes(node)), sep='', end='')

        print(')', sep='', end='')
    else:
        print(pfx, repr(node), sep='', end='')


# -- Main --------------------------------------------------------------------


class AstConversion(common.NumsedConversion):
    def __init__(self, source, transformation):
        common.NumsedConversion.__init__(self, source, transformation)
        self.tree = ast.parse(open(source).read())
        if transformation == LITERAL:
            pass
        elif transformation == UNSIGNED:
            numsed_ast_transformer = UnsignedTransformer(Unsigned_func)
            numsed_ast_transformer.visit(self.tree)
        elif transformation == SIGNED:
            numsed_ast_transformer = NumsedAstTransformer(signed_func)
            numsed_ast_transformer.visit(self.tree)
        else:
            pass

    def trace(self):
        print(ast.dump(self.tree))
        with common.ListStream() as x:
            pprint_ast(self.tree)
        return x.singlestring()

    def run(self):
        with common.ListStream() as x:
            ast.fix_missing_locations(self.tree)
            code = compile(self.tree, filename="<ast>", mode="exec")
            # giving a new namespace is necessary to avoid exec interfering
            # with current context (x variable from with construct)
            # giving global and local namespace (or equivalently only global
            # namespace) is necessary to handle recursive function definitions
            # see https://stackoverflow.com/questions/871887/using-exec-with-recursive-functions
            exec(code, globals())
        return x.singlestring()


class ScriptConversion(common.NumsedConversion):
    def __init__(self, source, transformation):
        common.NumsedConversion.__init__(self, source, transformation)
        if transformation == LITERAL or transformation == LITERAL + 10:
            self.code = open(source).read()
            open('~.py', 'wt').write(self.code)
        elif transformation == UNSIGNED:
            self.code = transform_unsigned(source, '~.py')
        elif transformation == SIGNED:
            self.code = transform_positive(source, '~.py')
        elif transformation == UNSIGNED + 10:
            self.code = transform_unsigned(source, '~.py', include_prim_def=False)
        elif transformation == SIGNED + 10:
            self.code = transform_positive(source, '~.py', include_prim_def=False)
        else:
            self.code = ''
    def trace(self):
        return self.code
    def run(self):
        if self.transformation == SIGNED:
            code = transform_assert('~.py', '~.py')
        res = subprocess.check_output('python ~.py')
        res = res.decode('ascii') # py3
        return res


if __name__ == "__main__":
    pass
