from typing import Type, Callable


class BaseType:
    pass


class VarType(BaseType):
    pass


class Device(BaseType):
    def __init__(self, device: str, prop: str):
        self.device = device
        self.prop = prop


class Variable:
    def __init__(self, var: str, var_type: Type[BaseType]):
        self.var = var
        self.var_type: Type[BaseType] = var_type


class Function:
    def __init__(self, var: Callable, var_type: Type[BaseType]):
        self.var = var
        self.var_type: Type[BaseType] = var_type

