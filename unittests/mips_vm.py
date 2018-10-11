import traceback

from compiler.compiler import Compiler


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
            print("================================================")
            print(program)
            print("------------------------------------------------")
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
        elif inst == 'ls':
            self._set_variable(args[1], self._get_variable((args[2], args[4], int(float(self._get_variable(args[3]))))))
        elif inst == 'lr':
            self._set_variable(args[1], self._get_variable((args[2], 'Reagent', args[3], args[4])))
        elif inst == 's':
            self._set_variable((args[1], args[2]), self._get_variable(args[3]))
        elif inst == 'move':
            self._set_variable(args[1], self._get_variable(args[2]))
        elif inst == 'and':
            self._set_variable(args[1], str(float(self._get_variable(args[2])) and float(self._get_variable(args[3]))))
        elif inst == 'or':
            self._set_variable(args[1], str(float(self._get_variable(args[2])) or float(self._get_variable(args[3]))))
        elif inst == 'xor':
            self._set_variable(args[1], str(int(bool(float(self._get_variable(args[2]))) != bool(float(self._get_variable(args[3]))))))
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
        elif inst == 'sgt':
            self._set_variable(args[1], str(1 if float(self._get_variable(args[2])) > float(self._get_variable(args[3])) else 0))
        elif inst == 'sle':
            self._set_variable(args[1], str(1 if float(self._get_variable(args[2])) <= float(self._get_variable(args[3])) else 0))
        elif inst == 'sge':
            self._set_variable(args[1], str(1 if float(self._get_variable(args[2])) >= float(self._get_variable(args[3])) else 0))
        elif inst == 'seq':
            self._set_variable(args[1], str(1 if float(self._get_variable(args[2])) == float(self._get_variable(args[3])) else 0))
        elif inst == 'sne':
            self._set_variable(args[1], str(1 if float(self._get_variable(args[2])) != float(self._get_variable(args[3])) else 0))
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
