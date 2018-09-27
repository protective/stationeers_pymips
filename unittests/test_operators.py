from unittests.mips_vm import MIPSVM


def test_condition_eq_true():
    program = """
a = 1
if a == 1:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 1


def test_condition_eq_false():
    program = """
a = 1
if a == 0:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 0


def test_condition_neq_true():
    program = """
a = 1
if a != 1:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 0


def test_condition_neq_false():
    program = """
a = 1
if a != 0:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 1


def test_condition_lt_true():
    program = """
a = 0
if a < 1:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 1


def test_condition_lt_false():
    program = """
a = 0
if a < 0:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 0


def test_condition_gt_true():
    program = """
a = 1
if a > 0:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 1


def test_condition_gt_false():
    program = """
a = 1
if a > 1:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 0
