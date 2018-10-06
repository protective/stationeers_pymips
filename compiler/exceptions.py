

class MipsException(Exception):
    pass


class MipsSyntaxError(MipsException):
    pass


class MipsCodeError(MipsException):
    pass


class MipsUndeclaredVariable(MipsCodeError):
    pass


class MipsTypeError(MipsCodeError):
    pass
