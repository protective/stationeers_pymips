from typing import Optional

from lark import Tree
from lark.lexer import Token

from compiler.expr_look_ahead import ExprLookAhead


class LAExprRearrange(ExprLookAhead):

    def __init__(self, id, node):
        self.loc_used = []
        self.tree = None
        # TODO implement possible to save register use
