from unittests.mips_vm import MIPSVM


def test_input():
    program = """
while True:
    out = load(d1, P1) + load(d1, P2) + load(d1, P3)
    yield
"""

    vm = MIPSVM(program)
    vm.execute({('d1', 'P1'): 1, ('d1', 'P2'): 10, ('d1', 'P3'): 100})
    assert vm.get_variable('o') == 111
    vm.execute({('d1', 'P2'): 5})
    assert vm.get_variable('o') == 106


def test_input_if_and_true_true():
    program = """
if load(d1, P1) and load(d1, P2):
    out = 1
    yield
"""

    vm = MIPSVM(program)
    vm.execute({('d1', 'P1'): 1, ('d1', 'P2'): 1})
    assert vm.get_variable('o') == 1


def test_input_if_and_false_true():
    program = """
if load(d1, P1) and load(d1, P2):
    out = 1
    yield
"""

    vm = MIPSVM(program)
    vm.execute({('d1', 'P1'): 0, ('d1', 'P2'): 1})
    assert vm.get_variable('o') == 0


def test_input_if_and_true_false():
    program = """
if load(d1, P1) and load(d1, P2):
    out = 1
    yield
"""

    vm = MIPSVM(program)
    vm.execute({('d1', 'P1'): 1, ('d1', 'P2'): 0})
    assert vm.get_variable('o') == 0


def test_input_if_and_false_false():
    program = """
if load(d1, P1) and load(d1, P2):
    out = 1
    yield
"""

    vm = MIPSVM(program)
    vm.execute({('d1', 'P1'): 0, ('d1', 'P2'): 0})
    assert vm.get_variable('o') == 0


def test_input_while():
    program = """
while load(d1, P1) and load(d1, P2):
    out = 1
    yield
yield
"""

    vm = MIPSVM(program)
    vm.execute({('d1', 'P1'): 1, ('d1', 'P2'): 1})
    assert vm.get_variable('o') == 1
