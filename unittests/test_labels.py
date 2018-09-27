from unittests.mips_vm import MIPSVM

def test_labels():
    program = """
room_sensor = label(d0, "Sensor")
exit_pump = label(d1, "VolumePump")
pipe_sensor = label(d2, "PipeAnalyzer")

while True:
    room_tmp = load(room_sensor, Temperature)
    if room_tmp > 25 or load(pipe_sensor, Pressure) > 4000:
        save(1, exit_pump, On)
    elif room_tmp < 24:
        save(0, exit_pump, On)
    yield
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



