"""
Prepare a numsed python program for compilation into sed.
Transform into positive form:
- all operators and binary comparisons are replaced with call to functions
  x + y --> signed_add(x, y), idem -, *, //, %, **, ==, !=, <, <=, >, >=
- all operands of operators and binary comparisons inside signed_xxx functions
  must be positive integers.
- two functions handling negative values remain: is_positive and abs. They are
  treated separately when testing python positive form or compiling into sed.
- augmented assignments are replaced with simple assignments.

A testing mode of the transformer program generates code testing that arguments
of operators and comparisons are positive.
"""

from __future__ import print_function

import sys
import inspect
import ast
import codegen
import common
from numsed_lib import *


LITERAL, UNSIGNED, SIGNED = range(3)
FUTURE_FUNCTION = 'from __future__ import print_function\n'


# -- Basic transformer --------------------------------------------------------


class PrepareTransformer(ast.NodeTransformer):
    """
    - replace augmented assignments with standard assignments
    - replace chained comparisons with and of comparisons
    """

    def visit_AugAssign(self, node):
        self.generic_visit(node)
        target = node.target
        source = ast.Name(id=target.id, ctx=ast.Load())
        return ast.Assign(targets=[target],
                          value=ast.BinOp(left=source, op=node.op, right=node.value))

    def visit_Compare(self, node):
        self.generic_visit(node)
        if len(node.ops) == 1:
            return node
        else:
            list_compare = []
            left = node.left
            for op, comparator in zip(node.ops, node.comparators):
                compare = ast.Compare(left=left, ops=[op], comparators=[comparator])
                list_compare.append(compare)
                left = comparator
            return ast.BoolOp(op=ast.And(), values=list_compare)


# -- Generic transformer ------------------------------------------------------


class NumsedTransformer(ast.NodeTransformer):

    def transform(self, tree):
        self.visit(tree)
        if common.PY2:
            tree.body = tree.body[1:]

        libfuncs = self.required_func
        libfuncs = function_calls(libfuncs)
        libfuncs = [globals()[x] for x in libfuncs]

        for func in libfuncs:
            treefunc = ast.parse(getsourcetext(func))
            tree.body.insert(0, treefunc.body[0])

        ast.fix_missing_locations(tree)

    def make_call(self, operator, *args):
        func = self.func[type(operator)]
        self.required_func.add(func)
        return ast.Call(func=ast.Name(id=func, ctx=ast.Load()),
                        args=list(args),
                        keywords=[], starargs=None, kwargs=None)


def getsourcetext(func):
    return ''.join(inspect.getsourcelines(func)[0])


# -- List of library functions ------------------------------------------------


def called_functions(func):
    """
    func is the name of a function. Returns the names of all functions called
    in func.
    """
    functext = '\n'.join(inspect.getsourcelines(globals()[func])[0])
    tree = ast.parse(functext)
    called = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # it is tested in checker.check that node.func is an ast.Name
            called.add(node.func.id)
    return called


def function_calls(libfuncs):
    """
    libfuncs is the list of library functions called in script. Returns ths
    list of all library functions required in script
    """
    libfuncs2 = set()
    while libfuncs:
        func = libfuncs.pop()
        libfuncs2.add(func)
        for func in called_functions(func):
            if func not in libfuncs and func not in libfuncs2:
                libfuncs.add(func)
    return sorted(list(libfuncs2))


# -- Unsigned transformer -----------------------------------------------------


UNSIGNED_FUNC = {
    ast.FloorDiv: 'udiv',
    ast.Mod: 'umod',
    ast.Pow: 'upow'}


class UnsignedTransformer(NumsedTransformer):

    def __init__(self):
        self.func = UNSIGNED_FUNC
        self.required_func = set()

    def visit_BinOp(self, node):
        self.generic_visit(node)
        if type(node.op) in self.func:
            return self.make_call(node.op, node.left, node.right)
        else:
            return node

    def visit_FunctionDef(self, node):
        if node.name in PRIMITIVES:
            return node
        else:
            self.generic_visit(node)
            return node

    def visit_Call(self, node):
        if node.func.id == 'divmod':
            node.func.id = 'udivmod'
            self.required_func.add('udivmod')
        self.generic_visit(node)
        return node


# -- Signed transformer -------------------------------------------------------


SIGNED_FUNC = {
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


class SignedTransformer(NumsedTransformer):

    def __init__(self):
        self.func = SIGNED_FUNC
        self.required_func = set()

    def visit_BinOp(self, node):
        # node.op in self.func ensured by checker.check()
        self.generic_visit(node)
            return self.make_call(node.op, node.left, node.right)

    def visit_Compare(self, node):
        self.generic_visit(node)
        return self.make_call(node.ops[0], node.left, node.comparators[0])

    def visit_FunctionDef(self, node):
        if node.name in PRIMITIVES:
            return node
        else:
            self.generic_visit(node)
            return node

    def visit_Call(self, node):
        if node.func.id == 'divmod':
            node.func.id = 'signed_divmod'
            self.required_func.add('signed_divmod')
        self.generic_visit(node)
        return node


# -- Assert transformer -------------------------------------------------------


ASSERT_POSITIVE_FUNC = {
    ast.Add: 'assert_positive_add',
    ast.Sub: 'assert_positive_sub',
    ast.Mult: 'assert_positive_mult',
    ast.FloorDiv: 'assert_positive_div',
    ast.Mod: 'assert_positive_mod',
    ast.Pow: 'assert_positive_pow',
    ast.Eq: 'assert_positive_eq',
    ast.NotEq: 'assert_positive_noteq',
    ast.Lt: 'assert_positive_lt',
    ast.LtE: 'assert_positive_lte',
    ast.Gt: 'assert_positive_gt',
    ast.GtE: 'assert_positive_gte'}


ASSERT_POSITIVE_FUNC_PATTERN = """
def %s(x, y):
    assert x >= 0, 'x < 0'
    assert y >= 0, 'y < 0'
    return x %s y
"""


def make_assert_positive_func(name):

    unsigned_op = {
        'assert_positive_add': '+',
        'assert_positive_sub': '-',
        'assert_positive_mult': '*',
        'assert_positive_div': '//',
        'assert_positive_mod': '%',
        'assert_positive_pow': '**',
        'assert_positive_eq': '==',
        'assert_positive_noteq': '!=',
        'assert_positive_lt': '<',
        'assert_positive_lte': '<=',
        'assert_positive_gt': '>',
        'assert_positive_gte': '>='}

    return ASSERT_POSITIVE_FUNC_PATTERN % (name, unsigned_op[name])


class AssertTransformer(NumsedTransformer):

    def __init__(self):
        self.func = ASSERT_POSITIVE_FUNC
        self.required_func = set()

    def visit_BinOp(self, node):
        self.generic_visit(node)
        if type(node.op) in self.func:
            return self.make_call(node.op, node.left, node.right)
        else:
            return node

    def visit_Compare(self, node):
        # len(node.ops) == 1 ensured by PrepareTransformer
        self.generic_visit(node)
        return self.make_call(node.ops[0], node.left, node.comparators[0])

    def visit_FunctionDef(self, node):
        if node.name in ('is_positive', 'abs'):
            return node
        else:
            self.generic_visit(node)
            return node

    def transform(self, tree):
        self.visit(tree)
        for func in self.required_func:
            treefunc = ast.parse(make_assert_positive_func(func))
            tree.body.insert(0, treefunc.body[0])


# -- AST pretty print ---------------------------------------------------------
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


# -- Ast conversion -----------------------------------------------------------


class AstConversion(common.NumsedConversion):
    def __init__(self, source, transformation):
        common.NumsedConversion.__init__(self, source, transformation)
        sourcelines = open(source).read()
        if common.PY2:
            sourcelines = FUTURE_FUNCTION + sourcelines
        self.tree = ast.parse(sourcelines)
        if transformation == LITERAL:
            pass
        elif transformation == UNSIGNED:
            PrepareTransformer().visit(self.tree)
            transformer = UnsignedTransformer()
            transformer.transform(self.tree)
        elif transformation == SIGNED:
            PrepareTransformer().visit(self.tree)
            transformer = SignedTransformer()
            transformer.transform(self.tree)
        else:
            pass

    def trace(self):
        print(ast.dump(self.tree))
        with common.ListStream() as x:
            pprint_ast(self.tree)
        return x.singlestring()

    def run(self):
        with common.ListStream() as x:
            code = compile(self.tree, filename="<ast>", mode="exec")
            # giving a new namespace is necessary to avoid exec interfering
            # with current context (x variable from with construct)
            # giving global and local namespace (or equivalently only global
            # namespace) is necessary to handle recursive function definitions
            # see https://stackoverflow.com/questions/871887/using-exec-with-recursive-functions
            exec(code, {})
        return x.singlestring()


# -- Script conversion --------------------------------------------------------


class ScriptConversion(AstConversion):
    def __init__(self, source, transformation):
        AstConversion.__init__(self, source, transformation)

        if self.transformation in (UNSIGNED, SIGNED):
            transformer = AssertTransformer()
            transformer.transform(self.tree)

        self.code = codegen.to_source(self.tree)

    def trace(self):
        return self.code

    def run(self):
        with common.ListStream() as x:
            code = compile(self.code, filename="<script>", mode="exec")
            exec(code, {})
        return x.singlestring()


# -- Main ---------------------------------------------------------------------


if __name__ == "__main__":
    pass
