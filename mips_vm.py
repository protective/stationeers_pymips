import traceback

from compiler import Compiler

a = """
j 16                 //  0: Jump to 16
bgtz 1 3             //  1: Jump to 3 if 1
j 17                 //  2: Jump to 17
add r1 i1 273.15     //  3: i1 + 273.15 -> r1
move r0 r1           //  4: r1 -> r0
add r2 i2 r0         //  5: i2 + r0 -> r2
move r1 r2           //  6: r2 -> r1
slt r2 r1 i0         //  7: i0 > r1 -> r2
bgtz r2 14           //  8: Jump to 14 if r2
slt r2 i0 r0         //  9: i0 < r0 -> r2
bgtz r2 12           // 10: Jump to 12 if r2
j 15                 // 11: Jump to 15
move o 0             // 12: 0 -> o
j 15                 // 13: Jump to 15
move o 1             // 14: 1 -> o
yield                // 15: yield
j 1                  // 16: Jump to 1
yield                // 17: EOF yield 
j 0                  // 18: EOF loop
"""



class MIPSVM:

    MAX_INST = 128
    def __init__(self, program=None):
        self._indput = {}
        self._output = {f'o': 0 for k in range(1)}
        self._registers = {f'r{k}': 0 for k in range(15)}
        self._pc = 0
        self._no_inst = 0
        self._program = []
        if program:
            mips = Compiler().compile(program)
            self.parse(mips)
            print()
            print(mips)
            print()
            pass

    def __str__(self):
        ret = []

        ret.append(f'pc: {self._pc}')
        ret.append('Indput')
        for k, v in self._indput.items():
            ret.append(f'{k}: {v}')

        ret.append('Output')
        for k, v in self._output.items():
            ret.append(f'{k}: {v}')

        ret.append('Registers')
        for k, v in self._registers.items():
            ret.append(f'{k}: {v}')

        return "\n".join(ret)

    def _next_inst(self):
        if self._pc >= len(self._program):
            return None
        ret = self._program[self._pc]
        self._pc += 1
        return ret

    def parse(self, program):
        for line in program.strip().split('\n'):
            args = line.split(' ')
            self._program.append(args)

    def get_variable(self, variable):
        return float(self._get_variable(variable))

    def _get_variable(self, variable):
        if variable in self._registers:
            return self._registers[variable]
        elif variable in self._indput:
            return self._indput[variable]
        elif variable in self._output:
            return self._output[variable]
        try:
            float(variable)
        except Exception as exc:
            print(f"unable to find variable {variable}")
            raise
        return variable

    def _set_variable(self, variable, value):
        if variable in self._registers:
            self._registers[variable] = value
        elif variable in self._indput:
            self._indput[variable] = value
        elif variable in self._output:
            self._output[variable] = value
        else:
            raise Exception(f"Unknown variable {variable}")

    def _execute_inst(self, args):
        inst = args[0]

        if inst == 'yield':
            return False
        elif inst == 'j':
            self._pc = int(args[1])
        elif inst == 'l':
            self._set_variable(args[1], self._get_variable((args[2], args[3])))
        elif inst == 's':
            self._set_variable((args[1], args[2]), self._get_variable(args[3]))
        elif inst == 'move':
            self._set_variable(args[1], self._get_variable(args[2]))
        elif inst == 'and':
            self._set_variable(args[1], str(float(self._get_variable(args[2])) and float(self._get_variable(args[3]))))
        elif inst == 'or':
            self._set_variable(args[1], str(float(self._get_variable(args[2])) or float(self._get_variable(args[3]))))
        elif inst == 'add':
            self._set_variable(args[1], str(float(self._get_variable(args[2])) + float(self._get_variable(args[3]))))
        elif inst == 'sub':
            self._set_variable(args[1], str(float(self._get_variable(args[2])) - float(self._get_variable(args[3]))))
        elif inst == 'mul':
            self._set_variable(args[1], str(float(self._get_variable(args[2])) * float(self._get_variable(args[3]))))
        elif inst == 'div':
            self._set_variable(args[1], str(float(self._get_variable(args[2])) / float(self._get_variable(args[3]))))
        elif inst == 'mod':
            self._set_variable(args[1], str(float(self._get_variable(args[2])) % float(self._get_variable(args[3]))))
        elif inst == 'slt':
            self._set_variable(args[1], str(1 if float(self._get_variable(args[2])) < float(self._get_variable(args[3])) else 0))
        elif inst == 'bgtz':
            if float(self._get_variable(args[1])) > 0:
                self._pc = int(args[2])
        elif inst == 'beq':
            if float(self._get_variable(args[1])) == float(self._get_variable(args[2])):
                self._pc = int(args[3])
        elif inst == 'bne':
            if float(self._get_variable(args[1])) != float(self._get_variable(args[2])):
                self._pc = int(args[3])
        return True

    def execute(self, indput=None):
        try:
            if indput:
                for k, v in indput.items():
                    self._indput[k] = v

            while self._no_inst < self.MAX_INST:
                inst = self._next_inst()
                if not inst:
                    break
                ret = self._execute_inst(inst)
                if not ret:
                    self._no_inst = 0
                    break
                self._no_inst += 1
        except Exception as exc:
            print(exc)
            traceback.print_exc()
            raise
