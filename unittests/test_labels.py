from unittests.mips_vm import MIPSVM

def test_labels():
    program = """
room_sensor = label(d0, "Sensor")
exit_pump = label(d1, "VolumePump")
pipe_sensor = label(d2, "PipeAnalyzer")

while True:
    room_tmp = room_sensor.Temperature
    if room_tmp > 25 or pipe_sensor.Pressure > 4000:
        exit_pump.On = 1
    elif room_tmp < 24:
        exit_pump.On = 0
    yield_tick
"""

    vm = MIPSVM(program)

    vm.execute({('d0', 'Temperature'): 1, ('d1', 'On'): 0,  ('d2', 'Pressure'): 100})
    assert vm.get_variable(('d1', 'On')) == 0

    vm.execute({('d0', 'Temperature'): 1, ('d1', 'On'): 0,  ('d2', 'Pressure'): 5700})
    assert vm.get_variable(('d1', 'On')) == 1

    vm.execute({('d0', 'Temperature'): 1, ('d1', 'On'): 0,  ('d2', 'Pressure'): 100})
    assert vm.get_variable(('d1', 'On')) == 0

    vm.execute({('d0', 'Temperature'): 26, ('d1', 'On'): 0,  ('d2', 'Pressure'): 100})
    assert vm.get_variable(('d1', 'On')) == 1

    vm.execute({('d0', 'Temperature'): 10, ('d1', 'On'): 0,  ('d2', 'Pressure'): 100})
    assert vm.get_variable(('d1', 'On')) == 0



