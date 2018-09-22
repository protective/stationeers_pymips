import pytest

from mips_vm import MIPSVM


def test_while_true():
    program = """
while True:
    out = out + 1 
    yield
out = 0
"""
    vm = MIPSVM(program)
    vm.execute()
    vm.execute()
    assert vm.get_variable('o') == 2


def test_while_false():
    program = """
while False:
    out = out + 1 
    yield
out = 1
yield
yield
"""
    vm = MIPSVM(program)
    vm.execute()
    vm.execute()
    assert vm.get_variable('o') == 1


def test_while_true():
    program = """
while out < 10:
    out = out + 1
yield
"""
    vm = MIPSVM(program)
    vm.execute()
    vm.execute()
    assert vm.get_variable('o') == 10
