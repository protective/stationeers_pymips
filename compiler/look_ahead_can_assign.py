from compiler.expr_look_ahead import ExprLookAhead


class LACanAssign(ExprLookAhead):

    def __init__(self, node):

        ret = self.visit(node)
        self.result = False if ret is None else True

    def dot_access(self, expr):
        return True

    def attr_get(self, expr):
        return True

    def loc(self, loc):
        return True

    def test(self, stmt):
        return True

    def arith_expr(self, expr):
        return True

    def expr(self, expr):
        return True

    def term(self, expr):
        return True

    def and_test(self, stmt):
        return True

    def or_test(self, stmt):
        return True

    def not_test(self, stmt):
        return True

    def comparison(self, expr):
        return True
