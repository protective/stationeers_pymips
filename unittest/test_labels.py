import pytest

from mips_vm import MIPSVM

def test_input():
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
    vm.execute({('d1', 'P1'): 1, ('d1', 'P2'): 10, ('d1', 'P3'): 100})
    assert vm.get_variable('o') == 111
    vm.execute({('d1', 'P2'): 5})
    assert vm.get_variable('o') == 106




