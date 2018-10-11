import pytest

from compiler.exceptions import MipsAttributeCantSetError
from unittests.mips_vm import MIPSVM


def test_reagent_expr():
    program = """
autolate = label(d0, 'Autolate')
out = autolate.Reagent_Required_Gold
yield_tick
"""

    vm = MIPSVM(program)
    vm.execute({('d0', 'Reagent', 'Required', 'Gold'): 1})
    assert vm.get_variable('o') == 1


def test_reagent_expr_add():
    program = """
autolate = label(d0, 'Autolate')
out = autolate.Reagent_Required_Gold + 42
yield_tick
"""

    vm = MIPSVM(program)
    vm.execute({('d0', 'Reagent', 'Required', 'Gold'): 1})
    assert vm.get_variable('o') == 43


def test_reagent_test():
    program = """
autolate = label(d0, 'Autolate')
if autolate.Reagent_Required_Gold == 1:
   out = 2
yield_tick
"""

    vm = MIPSVM(program)
    vm.execute({('d0', 'Reagent', 'Required', 'Gold'): 1})
    assert vm.get_variable('o') == 2


def test_reagent_assign_error():
    program = """
autolate = label(d0, 'Autolate')
autolate.Reagent_Required_Gold = 1
yield_tick
"""

    with pytest.raises(MipsAttributeCantSetError):
        vm = MIPSVM(program)
