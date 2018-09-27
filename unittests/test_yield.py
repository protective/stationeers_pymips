from unittests.mips_vm import MIPSVM


def test_yield_1():
    program = """
while True:
    a = load(d1, P1)
    if a > 10:
        out = 1
    elif a < 5:
        out = 0
    yield
"""
    vm = MIPSVM(program)
    vm.execute({('d1', 'P1'): 0})
    assert vm.get_variable('o') == 0
    vm.execute({('d1', 'P1'): 6})
    assert vm.get_variable('o') == 0
    vm.execute({('d1', 'P1'): 11})
    assert vm.get_variable('o') == 1
    vm.execute({('d1', 'P1'): 6})
    assert vm.get_variable('o') == 1
    vm.execute({('d1', 'P1'): 0})
    assert vm.get_variable('o') == 0
    vm.execute({('d1', 'P1'): 6})
    assert vm.get_variable('o') == 0
