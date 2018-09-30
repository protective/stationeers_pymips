from unittests.mips_vm import MIPSVM


def test_not_test_true():
    program = """
if not 0:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 1


def test_not_test_false():
    program = """
if not 1:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 0


def test_not_test_neg_false():
    program = """
if not -1:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 0


def test_not_expr_false():
    program = """
out = not 0
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 1


def test_not_expr_true():
    program = """
out = not 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 0


def test_not_expr_neg_true():
    program = """
out = not -1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 0


def test_not_test_ternary_true():
    program = """
if not 0:
    out = 1 if not 1 else 0
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 0


def test_not_test_ternary_false():
    program = """
out = 1 if not 0 else 0
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 1


def test_not_test_ternary_true():
    program = """
out = 1 if not 1 else 0
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 0


def test_not_test_and_true():
    program = """
if 1 and not 0:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 1


def test_not_test_and_false():
    program = """
if 0 and not 0:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 0


def test_not_test_or_true():
    program = """
if 1 or not 0:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 1


def test_not_test_or_false():
    program = """
if 0 or not 0:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 1


def test_not_test_paran_and_true():
    program = """
if not(1 and 1):
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 0


def test_not_test_paran_and_false():
    program = """
if not(1 and 0):
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 1
