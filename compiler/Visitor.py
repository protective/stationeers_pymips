class Visitor:
    def visit(self, node, **kwargs):
        f = getattr(self, node.data)
        return f(node, **kwargs)
