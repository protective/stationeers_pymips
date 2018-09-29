from unittests.mips_vm import MIPSVM


def test_var_assign():
    program = """
a = 1
out = a
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 1


def test_var_access_1():
    program = """
a = 1
b = 2
out = b
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 2


def test_var_access_2():
    program = """
a = 1
b = 2
out = a
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 1


def test_var_access_expr_1():
    program = """
a = 1
b = 2
out = a + b
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 3


def test_var_access_expr_2():
    program = """
a = 1
b = 2
out = a + b + a
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 4


def test_var_access_scope_1():
    program = """
a = 1
b = 2
c = a + b
out = c
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 3


def test_var_access_scope_2():
    program = """
a = 1
b = 2
a = a + b + a
out = a
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 4


def test_var_access_scope_3():
    program = """
a = 1
b = 2
a = b + a
out = a
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 3


def test_var_negative():
    program = """
a = -1
out = a
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == -1
