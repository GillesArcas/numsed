"""
Prepare a python program (tiny subset) for compliation into sed.
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

from __future__ import division

import sys
import inspect
import operator
import ast
import codegen


# -- Transformer --------------------------------------------------------------


signed_func = {
    ast.Add: 'signed_add',
    ast.Sub: 'signed_sub',
    ast.Mult: 'signed_mult',
    ast.Div: None,
    ast.FloorDiv: 'signed_div',
    ast.Mod: 'signed_mod',
    ast.Eq: 'signed_eq',
    ast.NotEq: 'signed_noteq',
    ast.Lt: 'signed_lt',
    ast.LtE: 'signed_lte',
    ast.Gt: 'signed_gt',
    ast.GtE: 'signed_gte'}

unsigned_func = {
    ast.Add: 'unsigned_add',
    ast.Sub: 'unsigned_sub',
    ast.Mult: 'unsigned_mult',
    ast.Div: None,
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
        return self.make_call(self.func[type(node.op)], [node.left, node.right])

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


# -- Builtin functions -------------------------------------------------------


def signed_eq(x, y):
    if is_positive(x):
        if is_positive(y):
            return x == y
        else:
            return False
    else:
        if is_positive(y):
            return False
        else:
            return negative(x) == negative(y)

def signed_noteq(x, y):
    return not signed_eq(x, y)

def signed_lt(x, y):
    if is_positive(x):
        if is_positive(y):
            return x < y
        else:
            return True
    else:
        if is_positive(y):
            return True
        else:
            return negative(x) < negative(y)

def signed_gte(x, y):
    return not signed_lt(x, y)


def signed_add(x, y):
    if is_positive(x):
        if is_positive(y):
            r = x + y
        else:
            y = negative(y)
            if x > y:
                r = x - y
            else:
                r = negative(y - x)
    else:
        x = negative(x)
        if is_positive(y):
            if x > y:
                r = negative(x - y)
            else:
                r = y - x
        else:
            y = negative(y)
            r = negative(x + y)
    return r


def signed_sub(x, y):
    if is_positive(x):
        if is_positive(y):
            if x > y:
                return x - y
            else:
                return negative(y - x)
        else:
            return x + negative(y)
    else:
        abs_x = negative(x)
        if is_positive(y):
            return negative(abs_x + y)
        else:
            abs_y = negative(y)
            if abs_x > abs_y:
                return negative(abs_x - abs_y)
            else:
                return abs_y - abs_x


def signed_pos(x):
    return x


def signed_neg(x):
    return negative(x)


def euclide(a, b):
    # http://compoasso.free.fr/primelistweb/page/prime/euclide.php
    r = a
    q = 0
    n = 0
    aux = b

    while aux <= a:
        aux = aux * 2
        n += 1

    while n > 0:
        #aux = aux / 2
        aux *= 5
        aux //= 10 # TODO: //10 should be a primitive divide_by_10()
        n -= 1
        q = q * 2
        if r >= aux:
            r -= aux
            q += 1

    return q

def modulo(a, b):
    q = euclide(a, b)
    return a - b * q


def signed_mult(a, b):
    if (a >= 0 and b >= 0) or (a <= 0 and b <= 0):
        return a * b
    else:
        return negative(a * b)


def signed_div(a, b):
    if (a >= 0 and b >= 0) or (a <= 0 and b <= 0):
        return euclide(a, b)
    else:
        # TODO: pas d'appel dans negative()
        return negative(euclide(a, b))


def signed_mod(a, b):
    q = signed_divide(a, b)
    return a - b * q


# -- Primitives --------------------------------------------------------------


def is_positive(x):
    return operator.ge(x, 0)

def negative(x):
    return operator.neg(x)


# -- Testing transformation --------------------------------------------------


unsigned_func_pattern = """
def %s(x, y):
    assert x >= 0
    assert y >= 0
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


# -- Tests -------------------------------------------------------------------


class NumsedAstVisitor(ast.NodeVisitor):
    def generic_visit(self, node):
        print type(node).__name__
        ast.NodeVisitor.generic_visit(self, node)

    #def visit_BinOp(self, node):
    #    print ast.dump(node)


# -- Main --------------------------------------------------------------------


def transform_positive(script_in, script_out, do_exec):
    tree = ast.parse(open(script_in).read())
    test_exec(tree, do_exec)
    numsed_ast_transformer = NumsedAstTransformer(signed_func)
    numsed_ast_transformer.visit(tree)
    test_exec(tree, do_exec)

    builtin = numsed_ast_transformer.required_func
    builtin = [globals()[x] for x in builtin]
    if signed_div in builtin or signed_mod in builtin:
        builtin.append(euclide)
    builtin += [is_positive, negative]

    # add builtin functions to code to compile
    script = ''
    for func in builtin:
        script += '\n'
        script += ''.join(inspect.getsourcelines(func)[0])
    script += '\n'
    script += codegen.to_source(tree)

    with open(script_out, 'w') as f:
        f.writelines(script)


def transform_assert(script_in, script_out, do_exec):
    tree = ast.parse(open(script_in).read())
    test_exec(tree, do_exec)
    numsed_ast_transformer = NumsedAstTransformer(unsigned_func)
    numsed_ast_transformer.visit(tree)
    test_exec(tree, do_exec)

    # add builtin functions to code to compile
    builtin = numsed_ast_transformer.required_func
    script = ''
    for func in builtin:
        script += '\n'
        script += make_unsigned_func(func)
    script += '\n'
    script += 'import operator\n\n'
    script += codegen.to_source(tree)

    with open(script_out, 'w') as f:
        f.writelines(script)


def test_exec(tree, do_exec):
    if do_exec:
        ast.fix_missing_locations(tree)
        print ast.dump(tree)
        exec(compile(tree, filename="<ast>", mode="exec"))


def transform(script_in, script_out, do_assert=False, do_exec=False):
    transform_positive(script_in, script_out, do_exec)
    if do_assert:
        transform_assert(script_out, script_out, do_exec)


# -- Main --------------------------------------------------------------------


def main():
    script_in = sys.argv[1]
    script_out = sys.argv[2]
    do_assert = False
    do_exec = True
    transform(script_in, script_out, do_assert, do_exec)


if __name__ == "__main__":
    main()
