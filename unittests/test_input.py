from unittests.mips_vm import MIPSVM


def test_input_1():
    program = """
d1 = label(d1, 'd1')
while True:
    out = d1.P1 + d1.P2 + d1.P3
    yield_tick
"""

    vm = MIPSVM(program)
    vm.execute({('d1', 'P1'): 1, ('d1', 'P2'): 10, ('d1', 'P3'): 100})
    assert vm.get_variable('o') == 111
    vm.execute({('d1', 'P2'): 5})
    assert vm.get_variable('o') == 106


def test_input_if_and_true_true():
    program = """
d1 = label(d1, 'd1')
if d1.P1 and d1.P2:
    out = 1
"""

    vm = MIPSVM(program)
    vm.execute({('d1', 'P1'): 1, ('d1', 'P2'): 1})
    assert vm.get_variable('o') == 1


def test_input_if_and_false_true():
    program = """
d1 = label(d1, 'd1')
if d1.P1 and d1.P2:
    out = 1
"""

    vm = MIPSVM(program)
    vm.execute({('d1', 'P1'): 0, ('d1', 'P2'): 1})
    assert vm.get_variable('o') == 0


def test_input_if_and_true_false():
    program = """
d1 = label(d1, 'd1')
if d1.P1 and d1.P2:
    out = 1
"""

    vm = MIPSVM(program)
    vm.execute({('d1', 'P1'): 1, ('d1', 'P2'): 0})
    assert vm.get_variable('o') == 0


def test_input_if_and_false_false():
    program = """
d1 = label(d1, 'd1')
if d1.P1 and d1.P2:
    out = 1
"""

    vm = MIPSVM(program)
    vm.execute({('d1', 'P1'): 0, ('d1', 'P2'): 0})
    assert vm.get_variable('o') == 0


def test_input_while():
    program = """
d1 = label(d1, 'd1')
while d1.P1 and d1.P2:
    out = 1
    yield_tick
yield_tick
"""

    vm = MIPSVM(program)
    vm.execute({('d1', 'P1'): 1, ('d1', 'P2'): 1})
    assert vm.get_variable('o') == 1
