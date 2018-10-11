from unittests.mips_vm import MIPSVM

def test_device_1():
    program = """
Device = label(d1, 'Sensor')
Device.Pressure = 1
a = Device.Pressure
out = Device.Pressure + a
"""

    vm = MIPSVM(program)
    vm.execute({('d1', 'Pressure'): 1})
    assert vm.get_variable('o') == 2

