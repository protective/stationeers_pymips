

class MipsException(Exception):
    pass


class MipsSyntaxError(MipsException):
    pass


class MipsCodeError(MipsException):
    pass


class MipsUnboundLocalError(MipsCodeError):
    """"""
    def __init__(self, name):
        self.name = name
        super().__init__(f"local variable '{name}' referenced before assignment")


class MipsAttributeError(MipsCodeError):
    """"""
    def __init__(self, attrib, obj_type):
        super().__init__(f"AttributeError: '{obj_type}' object has no attribute '{attrib}'")


class MipsNameError(MipsCodeError):
    def __init__(self, attrib):
        super().__init__(f"NameError: name '{attrib}' is not defined")


class MipsTypeError(MipsCodeError):
    """TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'"""
    pass


class MipsAttributeCantSetError(MipsCodeError):
    def __init__(self, attrib):
        super().__init__(f"AttributeError: can't set attribute '{attrib}'")
