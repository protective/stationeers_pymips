import pytest

from compiler.exceptions import MipsUnboundLocalError, MipsAttributeError, MipsNameError, MipsSyntaxError
from unittests.mips_vm import MIPSVM


def test_exception_expr_undeclared_access_1():
    program = """
out = a + 1
"""
    with pytest.raises(MipsUnboundLocalError):
        vm = MIPSVM(program)


def test_exception_expr_undeclared_access_2():
    program = """
out = 1 + a
"""
    with pytest.raises(MipsUnboundLocalError):
        vm = MIPSVM(program)


def test_exception_while_undeclared_access():
    program = """
while true:
    out = 1
"""
    with pytest.raises(MipsUnboundLocalError):
        vm = MIPSVM(program)


def test_exception_if_undeclared_access():
    program = """
if true:
    out = 1
"""
    with pytest.raises(MipsUnboundLocalError):
        vm = MIPSVM(program)


def test_exception_elif_undeclared_access():
    program = """
if 1:
    out = 1
elif true:
    out = 1
"""
    with pytest.raises(MipsUnboundLocalError):
        vm = MIPSVM(program)


def test_exception_attr_get_undeclared_access():
    program = """
out = a.Pressure
"""
    with pytest.raises(MipsUnboundLocalError):
        vm = MIPSVM(program)


def test_exception_attr_set_name_error():
    program = """
a.Pressure = 1
"""
    with pytest.raises(MipsNameError):
        vm = MIPSVM(program)


def test_exception_var_attribute_error_1():
    program = """
a = 1
out = a.Pressure
"""
    with pytest.raises(MipsAttributeError):
        vm = MIPSVM(program)


def test_exception_syntaxError_error_1():
    program = """
out = 1.Pressure
"""
    with pytest.raises(MipsSyntaxError):
        vm = MIPSVM(program)

