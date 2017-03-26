"""
Transform a python program into positive form:
- all operators and binary comparisons are replaced with call to functions
  x + y --> signed_add(x, y), idem -, *, /, ==, !=, <, <=, >, >=
- all operands of operators and binary comparisons must be positive integers.
  This is tested by transformer_test.py
"""

import sys
import inspect
import ast
import codegen


# -- Transformer --------------------------------------------------------------


class NumsedAstTransformer(ast.NodeTransformer):
    # TODO: +=, ...

    def __init__(self):
        self.required_func = set()

    def make_call(self, func, args):
        self.required_func.add(func)
        return ast.Call(func=ast.Name(id=func, ctx=ast.Load()),
                        args=args,
                        keywords=[], starargs=None, kwargs=None)

    def visit_BinOp(self, node):
        self.generic_visit(node)
        func = {ast.Add: 'signed_add',
                ast.Sub: 'signed_sub',
                ast.Mult: 'signed_mult',
                ast.Div: 'signed_div',
                ast.FloorDiv: 'signed_div'}
        return self.make_call(func[type(node.op)], [node.left, node.right])

    def visit_Compare(self, node):
        self.generic_visit(node)
        func = {ast.Eq: 'signed_eq',
                ast.NotEq: 'signed_noteq',
                ast.Lt: 'signed_lt',
                ast.LtE: 'signed_lte',
                ast.Gt: 'signed_gt',
                ast.GtE: 'signed_gte'}
        left = node.left
        ops = node.ops
        comparators = node.comparators
        if len(ops) == 1:
            return self.make_call(func[type(node.ops[0])], [node.left, comparators[0]])
        else:
            list_compare = []
            while ops:
                #compare = ast.Compare(left, ops[:1], comparators[:1])
                compare = self.make_call(func[type(ops[0])], [left, comparators[0]])
                list_compare.append(compare)
                left = comparators[0]
                ops = ops[1:]
                comparators = comparators[1:]
            return ast.BoolOp(op=ast.And(), values=list_compare)


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
            return abs(x) == abs(y)

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
            return abs(x) < abs(y)

def signed_gte(x, y):
    return not signed_lt(x, y)


def signed_add(x, y):
    if is_positive(x):
        if is_positive(y):
            r = x + y
        else:
            y = -y
            if x > y:
                r = x - y
            else:
                r = -(y - x)
    else:
        x = -x
        if is_positive(y):
            if x > y:
                r = -(x - y)
            else:
                r = y - x
        else:
            y = -y
            r = -(x + y)
    return r

def signed_sub(x, y):
    abs_x = absolute(x)
    abs_y = absolute(y)
    if is_positive(x):
        if is_positive(y):
            if unsigned_gte(abs_x, abs_y):
                return unsigned_sub(abs_x, abs_y)
            else:
                return negative(unsigned_sub(abs_y, abs_x))
        else:
            return unsigned_add(abs_x, abs_y)
    else:
        if is_positive(y):
            return negative(unsigned_add(abs_x, abs_y))
        else:
            if unsigned_gte(abs_x, abs_y):
                return negative(unsigned_sub(abs_x, abs_y))
            else:
                return unsigned_sub(abs_y, abs_x)


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
        aux /= 10
        n -= 1
        q = q * 2
        if r >= aux:
            r -= aux
            q += 1

    return q

def modulo(a, b):
    q = euclide(a, b)
    return a - b * q

def signed_divide(a, b):
    if (a >= 0 and b >= 0) or (a <= 0 and b <= 0):
        return euclide(a, b)
    else:
        return -euclide(a, b)

def signed_modulo(a, b):
    q = signed_divide(a, b)
    return a - b * q


# -- Primitives --------------------------------------------------------------


def is_positive(x):
    return x >= 0

def absolute(x):
    return abs(x)

def negative(x):
    return -x

def unsigned_gte(x, y):
    assert(x >= 0)
    assert(y >= 0)
    return x > y

def unsigned_add(x, y):
    assert(x >= 0)
    assert(y >= 0)
    return x + y

def unsigned_sub(x, y):
    assert(x >= 0)
    assert(y >= 0)
    return x - y


# -- Tests -------------------------------------------------------------------


class NumsedAstVisitor(ast.NodeVisitor):
    def generic_visit(self, node):
        print type(node).__name__
        ast.NodeVisitor.generic_visit(self, node)

    #def visit_BinOp(self, node):
    #    print ast.dump(node)


# -- Main --------------------------------------------------------------------


def main():
    tree = ast.parse(open('ast\\sub.py').read())
    print ast.dump(tree)

    numsed_ast_transformer = NumsedAstTransformer()
    numsed_ast_transformer.visit(tree)
    builtin = numsed_ast_transformer.required_func
    builtin = [globals()[x] for x in builtin]
    builtin += [is_positive, absolute, negative, unsigned_gte, unsigned_add, unsigned_sub]
    #print builtin

    # add builtin functions to code to compile
    script = ''
    for func in builtin:
        script += '\n'
        script += '\n'.join(inspect.getsourcelines(func)[0])
    script += codegen.to_source(tree)

    print script


if __name__ == "__main__":
    main()
