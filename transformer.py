import sys
import ast
#import codegen
import unparser


class NumsedAstVisitor(ast.NodeVisitor):
    def generic_visit(self, node):
        print type(node).__name__
        ast.NodeVisitor.generic_visit(self, node)

    #def visit_BinOp(self, node):
    #    print ast.dump(node)



class NumsedAstTransformer(ast.NodeTransformer):

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
                comparators= comparators[1:]
            return ast.BoolOp(op=ast.And(), values=list_compare)


tree = ast.parse(open('compare.py').read())

numsed_ast_transformer = NumsedAstTransformer()
numsed_ast_transformer.visit(tree)
print ast.dump(tree)
#print codegen.to_source(tree)

unparser.Unparser(tree, sys.stdout)
print numsed_ast_transformer.required_func
