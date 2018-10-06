from unittests.mips_vm import MIPSVM


def test_condition_or_scope_false_true():
    program = """
p = label(d0, "Sensor")
if p.false or p.true:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute({('d0', 'true'): 1, ('d0', 'false'): 0})
    assert vm.get_variable('o') == 1


def test_condition_or_scope_true_false():
    program = """
p = label(d0, "Sensor")
if p.true or p.false:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute({('d0', 'true'): 1, ('d0', 'false'): 0})
    assert vm.get_variable('o') == 1


def test_condition_and_scope_false_true():
    program = """
p = label(d0, "Sensor")
if p.false and p.true:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute({('d0', 'true'): 1, ('d0', 'false'): 0})
    assert vm.get_variable('o') == 0


def test_condition_and_scope_true_false():
    program = """
p = label(d0, "Sensor")
if p.true and p.false:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute({('d0', 'true'): 1, ('d0', 'false'): 0})
    assert vm.get_variable('o') == 0




def test_condition_or_false_true():
    program = """
if 0 or 1:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 1


def test_condition_or_false_true():
    program = """
if 1 or 0:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 1


def test_condition_or_true_true():
    program = """
if 1 or 1:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 1


def test_condition_or_false_false():
    program = """
if 0 or 0:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 0


def test_condition_and_false_true():
    program = """
if 0 and 1:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 0


def test_condition_and_false_true():
    program = """
if 1 and 0:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 0


def test_condition_and_true_true():
    program = """
if 1 and 1:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 1

def test_condition_and_false_false():
    program = """
if 0 and 0:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 0


def test_condition_and_and_false_false_true():
    program = """
if 0 and 0 and 1:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 0


def test_condition_or_or_false_false_true():
    program = """
if 0 or 0 or 1:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 1



def test_condition_and_or_true_false_true():
    program = """
if 1 and 0 or 1:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 1


def test_condition_and_or_false_true_true():
    program = """
if 0 and 1 or 1:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 1


def test_condition_and_or_false_true_false():
    program = """
if 1 and 1 or 0:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 1


def test_condition_and_or_true_false_false():
    program = """
if 1 and 0 or 0:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 0


def test_condition_or_and_false_true_true():
    program = """
if 0 or 1 and 1:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 1


def test_condition_or_and_true_false_false():
    program = """
if 1 or 0 and 0:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 1


def test_condition_or_and_false_false_true():
    program = """
if 0 or 0 and 1:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 0


def test_condition_or_and_false_true_false():
    program = """
if 0 or 1 and 0:
    out = 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 0


def test_condition_assignment_and_true():
    program = """
out = 1 and 1
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 1


def test_condition_assignment_and_false():
    program = """
out = 1 and 0
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 0


def test_condition_assignment_ternary_true():
    program = """
out = 1 if 1 and 1 else 0
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 1


def test_condition_assignment_ternary_false():
    program = """
out = 1 if 1 and 0 else 0
"""
    vm = MIPSVM(program)
    vm.execute()
    assert vm.get_variable('o') == 0

