"""
Tests if a script is compliant with numsed python syntax.
The following is tested:
- the script respects python syntax
- the only scalar type is integer
- strings are allowed only as print arguments
- tuples are allowed as multiple assignments and function results. A tuple
  may not contain tuples. A tuple must be assigned to a tuple of the same
  length.
- unary operators are - and +
- binary operators are -, +, *, //, % and **
- comparison operators are ==, !=, <, <=, >, and >=
- boolean operators are or, and and not
- functions are defined at module level
- functions from numsed_lib may not be redefined
- functions accept only positional arguments with no default value
- names are the only callables accepted
- print admits only one argument
- control flow statements are if-elif-else, while-else, break, continue,
  return, pass
"""
from __future__ import division, print_function

import inspect
import types
import ast
import codegen
import common
import numsed_lib
from numsed_lib import *


FUTURE_FUNCTION = 'from __future__ import print_function\n'


def check(source):
    try:
        with open(source) as f:
            script = f.read()
            code = compile(script, source, "exec")
    except SyntaxError as e:
        msg = 'SyntaxError: %s\nline %d: %s'% (e.args[0], e.args[1][1], e.args[1][3])
        return False, msg

    # list of functions defined in source
    source_functions = {x.co_name for x in code.co_consts if isinstance(x, types.CodeType)}

    tree = ast.parse(FUTURE_FUNCTION + script)
    numsed_check_ast_visitor = NumsedCheckAstVisitor(source_functions)
    try:
        numsed_check_ast_visitor.visit(tree)
        return True, ''
    except CheckException as e:
        return False, e.args[0]


BINOP = (ast.Add, ast.Sub, ast.Mult, ast.FloorDiv, ast.Mod, ast.Pow,
         ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE)


class NumsedCheckAstVisitor(ast.NodeVisitor):
    """
    two problems remain to handle multiple results n functions. First, it is not
    always possible to determine the number of results. for instance:

    def foo():
        while x:
            return x

    does this return 1 result (in the loop) or none (after the loop). Second,
    at least the dimension should be tested for any argument of print
    """

    def __init__(self, source_functions):
        # list of functions defined in lib
        self.lib_functions = {x[0] for x in inspect.getmembers(numsed_lib, inspect.isfunction)}
        self.lib_functions.add('print')

    def visit_Module(self, node):
        self.modulebody = node.body
        self.numvalout = nvalout_functions(node)
        self.numvalout['divmod'] = 2
        self.visit_child_nodes(node)

    def visit_ImportFrom(self, node):
        # allow for print_function
        pass

    def visit_Assign(self, node):
        def len_of_target(elt):
            if isinstance(elt, ast.Name):
                return 1
            elif isinstance(elt, ast.Tuple):
                return len(elt.elts)
            else:
                check_error('cannot assign to', codegen.to_source(elt), node)

        num = len_of_target(node.targets[0])
        for elt in node.targets[1:]:
            if len_of_target(elt) != num:
                check_error('multiple assignment must have same number of variables',
                            codegen.to_source(node), node)

        if isinstance(node.value, ast.Tuple):
            numv = len(node.value.elts)
        elif isinstance(node.value, ast.Call):
            numv = self.numvalout[node.value.func.id]
        else:
            numv = 1
        if numv != num:
            check_error('targets and values must have same length',
                        codegen.to_source(node), node)

        self.visit_child_nodes(node)

    def visit_AugAssign(self, node):
        self.visit(node.target)
        self.visit(node.value)

    def visit_Expr(self, node):
        self.visit_child_nodes(node)

    def visit_Name(self, node):
        pass

    def visit_Num(self, node):
        if not isinstance(node.n, int) and not (common.PY2 and isinstance(node.n, long)):
            check_error('not an integer', node.n, node)

    def visit_Str(self, node):
        check_error('strings not handled (less as print argument)',
                    codegen.to_source(node), node)

    def visit_Tuple(self, node):
        for elt in node.elts:
            if isinstance(elt, ast.Tuple):
                check_error('elements of tuples may not be tuples',
                            codegen.to_source(node), node)
            elif isinstance(elt, ast.Call):
                if self.numvalout[elt.func.id] > 1:
                    check_error('call in tuples should return a single result',
                                codegen.to_source(node), node)
        self.visit_child_nodes(node)

    def visit_Store(self, node):
        pass

    def visit_Load(self, node):
        pass

    def visit_UnaryOp(self, node):
        if not isinstance(node.op, (ast.UAdd, ast.USub, ast.Not)):
            check_error('operator not handled', codegen.to_source(node), node)
        self.visit(node.operand)

    def visit_BinOp(self, node):
        if not isinstance(node.op, BINOP):
            check_error('operator not handled', codegen.to_source(node), node)
        self.visit(node.left)
        self.visit(node.right)

    def visit_Compare(self, node):
        for op in node.ops:
            if not isinstance(op, (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE)):
                check_error('comparator not handled', codegen.to_source(node), node)
            else:
                self.visit(node.left)
                for _ in node.comparators: self.visit(_)

    def visit_BoolOp(self, node):
        for _ in node.values: self.visit(_)

    def visit_IfExp(self, node):
        self.visit_child_nodes(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id == 'print':
                self.visit_CallPrint(node)
            else:
                self.visit_child_nodes(node)
        else:
            check_error('callable not handled', codegen.to_source(node.func), node)

    def visit_CallPrint(self, node):
        if len(node.args) != 1:
            check_error('print admits one and only one argument', codegen.to_source(node), node)
        elif isinstance(node.args[0], ast.Str):
            pass
        else:
            self.visit_child_nodes(node)

    def visit_If(self, node):
        self.visit_child_nodes(node)

    def visit_While(self, node):
        self.visit_child_nodes(node)

    def visit_Break(self, node):
        pass

    def visit_Continue(self, node):
        pass

    def visit_Pass(self, node):
        pass

    def visit_Return(self, node):
        self.visit_child_nodes(node)

    def visit_Global(self, node):
        pass

    def visit_FunctionDef(self, node):
        if node not in self.modulebody:
            check_error('function definitions allowed only at module level', node.name, node)

        if node.name in self.lib_functions:
            check_error('not allowed to redefine numsed_lib functions', node.name, node)
        if node.args.vararg is not None:
            check_error('no vararg', node.args.vararg, node)
        if node.args.kwarg is not None:
            check_error('no kwarg', node.args.kwarg, node)
        if len(node.args.defaults) > 0:
            check_error('no defaults', node.args.defaults, node)
        for _ in node.body: self.visit(_)

    def visit_child_nodes(self, node):
        for _ in ast.iter_child_nodes(node):
            self.visit(_)

    def generic_visit(self, node):
        check_error('construct is not handled', codegen.to_source(node), node)


def nvalout_functions(tree):
    """
    Returns a dictionary giving the number of results for each function.
    """
    nvalout = dict()
    calls = dict()

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            func_nval, func_calls = nvalout_funcdef(node)
            if True or func_nval is not None:
                nvalout[node.name] = func_nval
            calls[node.name] = func_calls

    for func in nvalout:
        nval = set()
        nval.add(nvalout[func])
        for f in call_closure(func, calls):
            if f in nvalout:
                nval.add(nvalout[f])
            else:
                # TODO: not defined or lib
                pass
        if None in nval:
            nval.discard(None)
        if len(nval) == 1:
            nvalout[func] = next(iter(nval))
        else:
            check_error('different numbers of return values', func, None)

    return nvalout


def nvalout_funcdef(node):
    """
    Return the number of result values and the set of static calls in
    return position.
    """
    nval = set()
    calls = set()
    nvalout_body(node.body, nval, calls, terminal=True)
    print(nval)
    if len(nval) == 0:
        return None, calls
    elif len(nval) == 1:
        return next(iter(nval)), calls
    else:
        check_error('various numbers of result values', node.name, node)


def nvalout_body(body, nval, calls, terminal):
    for node in body:
        last = node == body[-1]
        if isinstance(node, ast.Return):
            nvalout_return(node.value, nval, calls)
        elif isinstance(node, (ast.If, ast.While)):
            nvalout_body(node.body, nval, calls, terminal and last)
            nvalout_body(node.orelse, nval, calls, terminal and last)
        elif terminal and last:
            nval.add(0)
        else:
            pass


def nvalout_return(value, nval, calls):
    if value is None:
        nval.add(0)
    elif isinstance(value, (ast.Num, ast.Name, ast.UnaryOp, ast.BinOp, ast.BoolOp, ast.Compare)):
        nval.add(1)
    elif isinstance(value, ast.Tuple):
        nval.add(len(value.elts))
    elif isinstance(value, ast.IfExp):
        nvalout_return(value.body, nval, calls)
        nvalout_return(value.orelse, nval, calls)
    elif isinstance(value, ast.Call):
        calls.add(value.func.id)
    else:
        check_error('unexpected return value', codegen.to_source(value), value)


def call_closure(func, calls_dict):
    """
    calls_dict contains the functions called in function definitions
    returns the set of functions transitively called from func
    """
    heap = calls_dict[func]
    calls = set()
    while heap:
        call = next(iter(heap))
        heap.discard(call)
        if call not in calls:
            calls.add(call)
            for f in calls_dict[call]:
                heap.add(f)
    return calls


class CheckException(Exception):
    pass


def check_error(msg, arg, node):
    # has to remove the line added for from future
    lineno = node.lineno - 1

    msg = 'numsed error: %s\nline %d col %d: %s' % (msg, lineno, node.col_offset, arg)
    raise CheckException(msg)
