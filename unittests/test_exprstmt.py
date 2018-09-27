from unittests.mips_vm import MIPSVM


def test_exprstmt_add():
    program = """
out = 1 + 2
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 3


def test_exprstmt_add_2():
    program = """
out = 1 + 2 + 3
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 6


def test_exprstmt_sub():
    program = """
out = 1 - 2
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == -1


def test_exprstmt_mul():
    program = """
out = 1 * 2
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 2


def test_exprstmt_mul_2():
    program = """
out = 1 * 2 * 3
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 6


def test_exprstmt_div():
    program = """
out = 1 / 2
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 0.5


def test_exprstmt_mod():
    program = """
out = 5 % 2
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 1


def test_exprstmt_add_mul():
    program = """
out = 1 + 2 * 10
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 21


def test_exprstmt_add_mul_par():
    program = """
out = (1 + 2) * 10
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 30


def test_exprstmt_add_div_par():
    program = """
out = (10 + 20) / 2
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 15
