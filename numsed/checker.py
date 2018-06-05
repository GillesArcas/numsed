"""
Tests if a script is compliant with numsed python syntax.
The following is tested:
- the script respects python syntax
- the only scalar type is integer
- strings are allowed only as print arguments
- characters in strings are limited to ASCII-32 (space) to ASCII-125 ("}")
  less the characters "@", "|" and ";" which are used by sed snippets
- tuples are allowed as multiple assignments but tuples must be assigned to
  tuples of the same length.
- tuples are not allowed as function results less for builtin divmod, but
  divmod results must be assigned immediately.
- unary operators are - and +
- binary operators are -, +, *, //, % and **, divmod function is available
- comparison operators are ==, !=, <, <=, >, and >=
- boolean operators are or, and and not
- functions are defined at module level
- functions from numsed_lib may not be redefined
- functions accept only positional arguments with no default value
- names are the only callables accepted
- control flow statements are if-elif-else, while-else, break, continue,
  return, pass
- all other constructs are not allowed
"""
from __future__ import print_function

import inspect
import ast
import re
from . import common
from . import numsed_lib


FUTURE_FUNCTION = 'from __future__ import print_function\n'


def check(source):
    try:
        with open(source) as f:
            # compile to catch syntax errors
            script = f.read()
            code = compile(script, source, "exec")
    except SyntaxError as e:
        msg = 'SyntaxError: %s\nline %d: %s' % (e.args[0], e.args[1][1], e.args[1][3])
        return False, msg

    tree = ast.parse(FUTURE_FUNCTION + script)
    numsed_check_ast_visitor = NumsedCheckAstVisitor()
    try:
        numsed_check_ast_visitor.visit(tree)
        return True, ''
    except CheckException as e:
        msg, node = e.args
        return False, error_message(msg, node, script)


def error_message(msg, node, script):
    script = script.splitlines()

    # remove the line added for from future
    lineno = node.lineno - 1
    # count column from 1
    col_offset = node.col_offset + 1

    msg = 'numsed error: line %d col %d: %s\n' % (lineno, col_offset, msg)
    msg += script[lineno - 1] + '\n'
    msg += ' ' * (col_offset - 1) + '^'
    return msg


BINOP = (ast.Add, ast.Sub, ast.Mult, ast.FloorDiv, ast.Mod, ast.Pow,
         ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE)


class NumsedCheckAstVisitor(ast.NodeVisitor):

    def __init__(self):
        # list of functions defined in lib
        # used to check there is no redefinition
        self.lib_functions = {x[0] for x in inspect.getmembers(numsed_lib, inspect.isfunction)}

    def visit_Module(self, node):
        self.tree = node
        self.modulebody = node.body
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
                raise CheckException('cannot assign to', node)

        num = len_of_target(node.targets[0])
        for elt in node.targets[1:]:
            if len_of_target(elt) != num:
                raise CheckException('multiple assignment must have same number of variables', node)

        if isinstance(node.value, ast.Tuple):
            numv = len(node.value.elts)
        elif isinstance(node.value, ast.Call):
            if node.value.func.id == 'divmod':
                numv = 2
            else:
                numv = 1
        else:
            numv = 1
        if numv != num:
            raise CheckException('targets and values must have same length', node)

        self.visit_child_nodes(node)

    def visit_AugAssign(self, node):
        self.visit(node.target)
        self.visit(node.value)

    def visit_Expr(self, node):
        self.visit_child_nodes(node)

    def visit_Name(self, node):
        if node.id in self.lib_functions and isinstance(node.ctx, ast.Store):
            raise CheckException('reserved word', node)

    def visit_Num(self, node):
        if not isinstance(node.n, int) and not (common.PY2 and isinstance(node.n, long)):
            raise CheckException('not an integer', node)

    def visit_Str(self, node):
        raise CheckException('strings not handled (unless as print argument)', node)

    def visit_Tuple(self, node):
        for elt in node.elts:
            if isinstance(elt, ast.Tuple):
                raise CheckException('elements of tuples may not be tuples', elt)
        self.visit_child_nodes(node)

    def visit_Store(self, node):
        pass

    def visit_Load(self, node):
        pass

    def visit_UnaryOp(self, node):
        if not isinstance(node.op, (ast.UAdd, ast.USub, ast.Not)):
            raise CheckException('operator not handled', node)
        self.visit(node.operand)

    def visit_BinOp(self, node):
        if not isinstance(node.op, BINOP):
            raise CheckException('operator not handled', node)
        self.visit(node.left)
        self.visit(node.right)

    def visit_Compare(self, node):
        for op in node.ops:
            if not isinstance(op, (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE)):
                raise CheckException('comparator not handled', node)
            else:
                self.visit(node.left)
                for _ in node.comparators:
                    self.visit(_)

    def visit_BoolOp(self, node):
        for _ in node.values:
            self.visit(_)

    def visit_IfExp(self, node):
        self.visit_child_nodes(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id == 'print':
                self.visit_CallPrint(node)
            elif node.func.id == 'divmod':
                self.visit_CallDivmod(node)
            elif node.func.id == 'exit':
                self.visit_CallExit(node)
            else:
                self.visit_child_nodes(node)
        else:
            raise CheckException('callable not handled', node)

    def visit_CallPrint(self, node):
        for arg in node.args:
            if isinstance(arg, ast.Str):
                if re.match('^[ -~]*$', arg.s) and re.search('[@|;~]', arg.s) is None:
                    pass
                else:
                    raise CheckException('character not handled (@|;~)', arg)
            else:
                self.visit(arg)

    def visit_CallDivmod(self, node):
        parent = parent_node(self.tree, node)
        if isinstance(parent, ast.Assign):
            pass
        else:
            raise CheckException('divmod results must be assigned immediately', node)
        self.visit_child_nodes(node)

    def visit_CallExit(self, node):
        if len(node.args) > 0:
           raise CheckException('arguments are not allowed', node)

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
        if isinstance(node.value, ast.Tuple):
            raise CheckException('function result must be an integer', node.value)
        self.visit_child_nodes(node)

    def visit_Global(self, node):
        pass

    def visit_FunctionDef(self, node):
        if node not in self.modulebody:
            raise CheckException('function definitions allowed only at module level', node)

        if node.name in self.lib_functions:
            raise CheckException('not allowed to redefine numsed_lib functions', node)
        if node.args.vararg is not None:
            raise CheckException('no vararg arguments', node)
        if node.args.kwarg is not None:
            raise CheckException('no kwarg arguments', node)
        if len(node.args.defaults) > 0:
            raise CheckException('no default arguments', node)
        for _ in node.body:
            self.visit(_)

    def visit_child_nodes(self, node):
        for _ in ast.iter_child_nodes(node):
            self.visit(_)

    def generic_visit(self, node):
        raise CheckException('construct is not handled', node)


def parent_node(tree, node):
    for nod in ast.walk(tree):
        for _ in ast.iter_child_nodes(nod):
            if _ == node:
                return nod


class CheckException(Exception):
    pass
