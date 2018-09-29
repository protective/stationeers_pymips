from contextlib import contextmanager

import sys
from pathlib import Path

try:
    from lark import Lark, Tree
    from lark.lexer import Token
    from lark.indenter import Indenter

except ImportError:
    print('Missing Module lark install with pip \"pip install lark-parser\"')
    sys.exit(1)

grammar = None
with open('compiler/gramma', 'r') as fd:
    grammar = fd.read()


class TreeIndenter(Indenter):
    NL_type = '_NEWLINE'
    OPEN_PAREN_types = ['LPAR', 'LSQB', 'LBRACE']
    CLOSE_PAREN_types = ['RPAR', 'RSQB', 'RBRACE']
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 4


class Device:
    def __init__(self, device: str, prop: str):
        self.device = device
        self.prop = prop


class Compiler:
    def __init__(self, debug=False):
        self.debug = debug
        self.stack_counter = -1
        self.idtable = {'out': 'o'}
        self.device_table = {}
        self.vtable = {'load': self._load, 'save': self._save, 'label': self._label}
        self.labels = {}
        self.label = 0
        self.program = []
        self.final_program = []
        self._stmt_lookahead = False
        self._stmt_lookahead_fail = False
        self._stmt_lookahead_copy = False
        self._stmt_lookahead_ban = []

    def compile(self, program):
        parser = Lark(grammar, start='root', parser='lalr', postlex=TreeIndenter())

        tree = parser.parse(program)
        if self.debug:
            print(tree)
        self.visit(tree)
        self.resolve_labels()
        self.validate()
        return "\n".join([f'{line:20} // {i:2}: {desc}' for i, (line, desc) in enumerate(self.final_program)])

    def resolve_labels(self):

        for line, desc in self.program:
            line = line.format(**self.labels)
            desc = desc.format(**self.labels)
            self.final_program.append((line, desc))

    def validate(self):
        if len(self.final_program) > 127:
            raise Exception(f"program to large {len(self.final_program)} > 127")

    @contextmanager
    def stack(self, check_direct_access=None, store_dst=None):
        # Lockahead for increase in stack
        if store_dst:
            yield store_dst
            return

        if check_direct_access:
            r = self.visit(check_direct_access, check_direct_access=True)
            if r:
                yield f'r{self.stack_counter}'
                # if check_direct_access and check_direct_access.data == 'loc':
                #    yield f'r{self.stack_counter}'
                return

        self.stack_counter += 1
        yield f'r{self.stack_counter}'
        self.stack_counter -= 1

    @property
    def cur_stack(self):
        return f'r{self.stack_counter}'

    def cur_stack_dst(self, store_dst=None):
        if store_dst:
            return store_dst
        return self.cur_stack

    def _insert_label(self, label=None):
        if label is None:
            self.label += 1
            label = f'L{self.label}'
        self.labels[label] = len(self.program)
        return label

    def _create_label(self, label=None):
        if label is None:
            self.label += 1
            label = f'L{self.label}'
        return label

    def _add_instruction(self, inst, desc):
        self.program.append((inst, desc))

    def _push_copy_inst(self, src, dst):
        self._add_instruction(f'move {dst} {src}', f'{src} -> {dst}')

    def _push_conditional_jump_inst(self, condition, label):
        if label is None:
            self.label += 1
            label = f'L{self.label}'
        self.labels[label] = None
        label_str = '{' + str(label) + '}'
        self._add_instruction(f'bne {condition} 0 {label_str}', f'Jump to {label_str} if {condition}')
        return label

    def _push_conditional_eq_jump_inst(self, r0, r1, label, eq=True):
        if label is None:
            self.label += 1
            label = f'L{self.label}'
        self.labels[label] = None
        label_str = '{' + str(label) + '}'

        op = 'beq' if eq else 'bne'

        self._add_instruction(f'{op} {r0} {r1} {label_str}', f'Jump to {label_str} if {r0} == {r1}')
        return label

    def _push_jump_inst(self, label=None):
        if label is None:
            self.label += 1
            label = f'L{self.label}'
        if label not in self.labels:
            self.labels[label] = None
        label_str = '{' + str(label) + '}'
        self._add_instruction(f'j {label_str}', f'Jump to {label_str}')
        return label

    def visit(self, node, **kwargs):
        f = getattr(self, node.data)
        return f(node, **kwargs)

    def root(self, stmts):

        """"""
        for stmt in stmts.children:
            self.visit(stmt)

    def stmt(self, stmt):

        for s in stmt.children:
            self.visit(s)

    def if_stmt(self, stmt):
        exit_jump = self._create_label()
        self._recursive_if_stmt(stmt.children.copy(), exit_jump)
        self._insert_label(exit_jump)

    def and_test(self, stmt, check_direct_access=None, store_dst=None):
        if check_direct_access:
            return False
        lst = stmt.children.copy()
        retloc = self.cur_stack
        while len(lst) >= 2:
            ret = self.operator(lst[0], 'and', lst[1], store_dst=store_dst)
            lst = lst[2:]
            lst.insert(0, Tree('loc', [Token('loc', retloc)]))
        return retloc

    def or_test(self, stmt, check_direct_access=None, store_dst=None):
        if check_direct_access:
            return False
        lst = stmt.children.copy()
        retloc = self.cur_stack
        while len(lst) >= 2:
            ret = self.operator(lst[0], 'or', lst[1], store_dst=store_dst)
            lst = lst[2:]
            lst.insert(0, Tree('loc', [Token('loc', retloc)]))
        return retloc

    def test(self, stmt, check_direct_access=None, store_dst=None):
        if check_direct_access:
            return False
        if self._stmt_lookahead:
            return
        lst = stmt.children.copy()

        n_lst = [lst[1], lst[0], lst[2]]
        self._recursive_if_stmt(n_lst, exit_jump=None, is_expr=True, store_dst=store_dst)
        retloc = self.cur_stack_dst(store_dst)
        return retloc

    def _recursive_if_stmt(self, stmt_lst, exit_jump, is_expr=False, store_dst=None):
        if len(stmt_lst) >= 2:
            test = stmt_lst[0]
            if_suite = stmt_lst[1]

            with self.stack(test, store_dst=store_dst) as s0:
                r0 = self.visit(test, store_dst=s0)
            con_jump_label = self._push_conditional_jump_inst(r0, None)
            # Else stmt
            self._recursive_if_stmt(stmt_lst[2:], exit_jump, is_expr=is_expr, store_dst=store_dst)

            jump_label = self._push_jump_inst(exit_jump)
            self._insert_label(con_jump_label)
            # True

            if is_expr:
                with self.stack(if_suite):
                    r0 = self.visit(if_suite)
                self._stmt_lookahead_copy = True
                self._push_copy_inst(src=r0, dst=self.cur_stack_dst(store_dst))
            else:
                self.visit(if_suite)

            self._insert_label(jump_label)
        elif len(stmt_lst) == 1:
            else_suite = stmt_lst[0]

            if is_expr:
                with self.stack(else_suite):
                    r0 = self.visit(else_suite)
                self._stmt_lookahead_copy = True
                self._push_copy_inst(src=r0, dst=self.cur_stack_dst(store_dst))
            else:
                self.visit(else_suite)

    def while_stmt(self, stmt, store_dst=None):
        test = stmt.children[0]

        suite = stmt.children[1]

        init_jump = self._push_jump_inst()
        jump_label = self._insert_label()
        with self.stack(test, store_dst=store_dst) as s0:
            r0 = self.visit(test, store_dst=s0)

        con_jump_label = self._push_conditional_jump_inst(r0, None)
        end_jump = self._push_jump_inst()

        self._insert_label(con_jump_label)
        self.visit(suite)
        self._insert_label(init_jump)
        self._push_jump_inst(jump_label)
        self._insert_label(end_jump)

    def suite(self, stmt):
        for s_stmt in stmt.children:
            self.visit(s_stmt)

    def compound_stmt(self, stmt):
        self.visit(stmt.children[0])

    def reduce_expr(self, tree, store_dst=None):
        lst = tree.children.copy()
        retloc = self.cur_stack_dst(store_dst)
        while len(lst) >= 3:
            ret = self.operator(*lst[0:3], store_dst=store_dst)
            lst = lst[3:]
            lst.insert(0, Tree('loc', [Token('loc', retloc)]))
        return retloc

    def operator(self, left, op, right, store_dst=None):
        if self._stmt_lookahead:
            r0 = self.visit(left)
            r1 = self.visit(right)
            self._stmt_lookahead_copy = True
            return
        with self.stack(left, store_dst=store_dst) as s0:
            r0 = self.visit(left, store_dst=s0)
            with self.stack(right) as s1:
                r1 = self.visit(right, store_dst=s1)
                pass

        opper = None
        if op == 'and':
            opper = 'and'
        elif op == 'or':
            opper = 'or'
        elif op.value == '+':
            opper = 'add'
        elif op.value == '-':
            opper = 'sub'
        elif op.value == '*':
            opper = 'mul'
        elif op.value == '/':
            opper = 'div'
        elif op.value == '%':
            opper = 'mod'

        dst = self.cur_stack_dst(store_dst)
        if opper:
            self._add_instruction(f'{opper} {dst} {r0} {r1}', f'{r0} {opper} {r1} -> {dst}')
        else:
            if op.value == '<':
                self._add_instruction(f'slt {dst} {r0} {r1}', f'{r0} < {r1} -> {dst}')
            elif op.value == '>':
                self._add_instruction(f'sgt {dst} {r0} {r1}', f'{r0} < {r1} -> {dst}')
            elif op.value == '<=':
                self._add_instruction(f'sle {dst} {r0} {r1}', f'{r0} <= {r1} -> {dst}')
            elif op.value == '>=':
                self._add_instruction(f'sge {dst} {r0} {r1}', f'{r0} <= {r1} -> {dst}')
            elif op.value == '==':
                self._add_instruction(f'seq {dst} {r0} {r1}', f'{r0} == {r1} -> {dst}')
            elif op.value == '!=':
                self._add_instruction(f'sne {dst} {r0} {r1}', f'{r0} != {r1} -> {dst}')
        return dst

    def term(self, expr, check_direct_access=None, store_dst=None):
        if check_direct_access:
            return False
        return self.reduce_expr(expr, store_dst=store_dst)

    def arith_expr(self, expr, check_direct_access=None, store_dst=None):
        if check_direct_access:
            return False
        return self.reduce_expr(expr, store_dst=store_dst)

    def comparison(self, expr, check_direct_access=None, store_dst=None):
        if check_direct_access:
            return False
        return self.reduce_expr(expr, store_dst=store_dst)

    def atom_expr(self, expr, left_type=None, check_direct_access=None, store_dst=None):
        if check_direct_access:
            return False
        dst = self.cur_stack_dst(store_dst=store_dst)
        return dst

    def call(self, expr, left_type=None, check_direct_access=None, store_dst=None):
        if check_direct_access:
            return False
        dst = self.cur_stack_dst(store_dst=store_dst)
        ret = None
        if isinstance(expr.children[0], Tree):
            tree = expr.children[0]
            if len(expr.children) > 1 and isinstance(expr.children[1], Tree) and expr.children[1].data == 'arguments':
                if tree.children[0].value in self.vtable:
                    arguments = expr.children[1]
                    ret = self.vtable[tree.children[0].value](
                        dst,
                        arguments.children)
        if ret:
            return ret
        return dst

    def attr_get(self, expr, left_type=None, check_direct_access=None, store_dst=None):
        if check_direct_access:
            return False

    def dotaccess(self, expr, left_type=None, check_direct_access=None, store_dst=None):
        if check_direct_access or self._stmt_lookahead:
            return False
        if store_dst:
            dst = self.cur_stack_dst(store_dst=store_dst)
            prop = expr.children[1]
            device = expr.children[0].children[0]
            self._load_attr(dst=dst, device=device, prop=prop)
            return dst
        else:

            prop = expr.children[1]
            device = expr.children[0].children[0]

            return Device(device, prop)

    def assignmentstmt(self, stmt):
        """"""
        self._stmt_lookahead = True
        expr = stmt.children[1]
        r0 = self.visit(expr)
        self._stmt_lookahead = False
        if isinstance(r0, Device):
            self.device_table[stmt.children[0].children[0].value] = r0
            self.visit(expr, left_type=Device)
            return
        else:
            id = self.visit(stmt.children[0])
            dst = id
            if not id:
                dst = self.idtable[id]

        with self.stack(expr) as r1:

            self._stmt_lookahead_fail = False

            if isinstance(dst, Device):
                self._stmt_lookahead_ban = []
            else:
                self._stmt_lookahead_ban = [stmt.children[0].children[0].value]
            self._stmt_lookahead_copy = False

            if not isinstance(dst, Device):
                self._stmt_lookahead = True
                r0 = self.visit(expr)
                self._stmt_lookahead = False
            else:
                self._stmt_lookahead_fail = True

            if self._stmt_lookahead_fail:
                r0 = self.visit(expr, store_dst=r1)
        if not self._stmt_lookahead_fail:
            r0 = self.visit(expr, store_dst=dst)

        if isinstance(dst, Device):
            self._save_attr(r0, dst.device, dst.prop)
        elif self._stmt_lookahead_fail or self._stmt_lookahead_copy == False:
            self._push_copy_inst(src=r0, dst=dst)

    def var(self, var, **kwargs):
        name: str = var.children[0].value

        if name in self._stmt_lookahead_ban:
            self._stmt_lookahead_fail = True
        if name in self.idtable:
            return f'{self.idtable[name]}'
        else:
            self.stack_counter += 1
            self.idtable[name] = self.cur_stack
            return self.idtable[name]

    def yield_stmt(self, stmt):
        self._add_instruction('yield', 'yield')

    def const_true(self, token, check_direct_access=None, store_dst=None):
        if check_direct_access:
            return True
        return '1'

    def const_false(self, token, check_direct_access=None, store_dst=None):
        if check_direct_access:
            return True
        return '0'

    def loc(self, loc, check_direct_access=None, store_dst=None):
        if check_direct_access:
            return True
        return loc.children[0].value

    def factor(self, number, check_direct_access=None, store_dst=None):
        if check_direct_access:
            return True
        if number.children[0].value == '-':
            return f'-{self.visit(number.children[1])}'
        raise Exception(f'Unknown factor "{number.children[0].value}"')

    def number(self, number, check_direct_access=None, store_dst=None):
        if check_direct_access:
            return True
        value = number.children[0].value
        return value

    def _load_attr(self, dst, device: Token, prop: Token):
        self._stmt_lookahead_copy = True
        if self._stmt_lookahead:
            return
        if device in self.device_table:
            device = self.device_table[device].device

        prop_str= prop.value
        self._add_instruction(f'l {dst} {device} {prop_str}', f'load {device} {prop_str} to {dst}')

    def _save_attr(self, var, device: Token, prop: Token):
        self._stmt_lookahead_copy = True
        if self._stmt_lookahead:
            return
        if device in self.device_table:
            device = self.device_table[device].device

        prop_str = prop.value
        self._add_instruction(f's {device} {prop} {var}', f'save {var} to {device} {prop}')

    def _load(self, dst, args):
        self._stmt_lookahead_copy = True
        if self._stmt_lookahead:
            return
        device = args[0].children[0].value
        if device in self.device_table:
            device = self.device_table[device].device
        prop = args[1].children[0].value
        slot = args[2].children[0].value if len(args) == 3 else None
        self._add_instruction(f'l {dst} {device} {prop}', f'load {device} {prop} to {dst}')

    def _save(self, _, args):
        if self._stmt_lookahead:
            return
        with self.stack():
            r0 = self.visit(args[0])
        device = args[1].children[0].value
        if device in self.device_table:
            device = self.device_table[device].device
        prop = args[2].children[0].value
        slot = args[3].children[0].value if len(args) == 4 else None
        self._add_instruction(f's {device} {prop} {r0}', f'save {r0} to {device} {prop}')

    def _label(self, _, args):

        device = args[0].children[0].value
        if args[1].data == 'string':
            prop = args[1].children[0].value[1:-1]
        else:
            prop = args[1].children[0].value

        if not self._stmt_lookahead:
            self._add_instruction(f'alias {prop} {device}', f'alias {prop} {device}')
        return Device(device, prop)


def compile_file(file: Path, debug=False):
    file_o = Path(f'{file}.mips')
    with file.open('r') as fd_r, file_o.open('w') as fd_w:
        output = compile_src(fd_r.read(), debug)
        fd_w.write(output)
        print(output)


def compile_src(src: str, debug=False):
    compiler = Compiler(debug=debug)
    compiler.compile(src)

    output = ""
    if debug:
        output = src.strip() + '\n'

        output += "Begin Python**************************\n"
        output += src.strip(src) + '\n'
        output += "End Python*****************************\n"

        output += "MIPS***********************************\n"
        for i, (line, desc) in enumerate(compiler.final_program):
            output += f'{line:35} {i:2}: {desc}\n'

        output += "MIPS***********************************\n"
    for i, (line, desc) in enumerate(compiler.final_program):
        output += f'{line}\n'
    return output
