from unittests.mips_vm import MIPSVM


def test_slot_number():
    program = """
Hydroponic = label(d0, 'Hydroponic')
out = Hydroponic.Growth[1]
yield_tick
"""

    vm = MIPSVM(program)
    vm.execute({('d0', 'Growth', 1): 1})
    assert vm.get_variable('o') == 1


def test_slot_var():
    program = """
Hydroponic = label(d0, 'Hydroponic')
a = 1
out = Hydroponic.Growth[a]
yield_tick
"""

    vm = MIPSVM(program)
    vm.execute({('d0', 'Growth', 1): 1})
    assert vm.get_variable('o') == 1


def test_slot_expr():
    program = """
Hydroponic = label(d0, 'Hydroponic')
a = 1
out = Hydroponic.Growth[a + 1]
yield_tick
"""

    vm = MIPSVM(program)
    vm.execute({('d0', 'Growth', 2): 1})
    assert vm.get_variable('o') == 1


def test_slot_test_ternary_true():
    program = """
Hydroponic = label(d0, 'Hydroponic')
out = Hydroponic.Growth[1 if 1 else 0]
yield_tick
"""

    vm = MIPSVM(program)
    vm.execute({('d0', 'Growth', 1): 1})
    assert vm.get_variable('o') == 1


def test_slot_test_ternary_false():
        program = """
Hydroponic = label(d0, 'Hydroponic')
out = Hydroponic.Growth[1 if 0 else 0]
yield_tick
    """

        vm = MIPSVM(program)
        vm.execute({('d0', 'Growth', 0): 1})
        assert vm.get_variable('o') == 1
