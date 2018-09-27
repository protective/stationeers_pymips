from unittests.mips_vm import MIPSVM


def test_getattr_test():
    program = """
Switch = label(d0, "Analyzer")
if Switch.Pressure:
    out = 1
    yield
"""

    vm = MIPSVM(program)
    vm.execute({('d0', 'Pressure'): 1})
    assert vm.get_variable('o') == 1


def test_getattr_expr():
    program = """
Switch = label(d0, "Analyzer")
out = Switch.Pressure
yield
"""

    vm = MIPSVM(program)
    vm.execute({('d0', 'Pressure'): 1})
    assert vm.get_variable('o') == 1


def test_setattr_expr():
    program = """
Switch = label(d0, "Analyzer")
a = 41
Switch.Pressure = a + 1
yield
"""

    vm = MIPSVM(program)
    vm.execute({('d0', 'Pressure'): 1})
    assert vm.get_variable(('d0', 'Pressure')) == 42


def test_setattr_test():
    program = """
Switch = label(d0, "Analyzer")
a = 41
Switch.Pressure = a if a else 0 
yield
"""

    vm = MIPSVM(program)
    vm.execute({('d0', 'Pressure'): 1})
    assert vm.get_variable(('d0', 'Pressure')) == 41


def test_setgetattr_expr_1():
    program = """
Switch = label(d0, "Analyzer")
Switch.Pressure = Switch.ExternalPressure
yield
"""

    vm = MIPSVM(program)
    vm.execute({('d0', 'Pressure'): 1, ('d0', 'ExternalPressure'): 42})
    assert vm.get_variable(('d0', 'Pressure')) == 42


def test_setgetattr_expr_2():
    program = """
Switch = label(d0, "Analyzer")
Switch.Pressure = 2 + Switch.ExternalPressure
yield
"""

    vm = MIPSVM(program)
    vm.execute({('d0', 'Pressure'): 1, ('d0', 'ExternalPressure'): 40})
    assert vm.get_variable(('d0', 'Pressure')) == 42


def test_setgetattr_expr_3():
    program = """
Switch = label(d0, "Analyzer")
Switch.Pressure = Switch.ExternalPressure + 2
yield
"""

    vm = MIPSVM(program)
    vm.execute({('d0', 'Pressure'): 1, ('d0', 'ExternalPressure'): 40})
    assert vm.get_variable(('d0', 'Pressure')) == 42


def test_setgetattr_expr_4():
    program = """
Switch = label(d0, "Analyzer")
Switch.Pressure = Switch.Pressure + 2
yield
"""

    vm = MIPSVM(program)
    vm.execute({('d0', 'Pressure'): 1})
    assert vm.get_variable(('d0', 'Pressure')) == 3
