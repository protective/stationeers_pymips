from contextlib import contextmanager

from compiler.Visitor import Visitor
from compiler.exceptions import MipsCodeError, MipsUnboundLocalError, MipsAttributeError, MipsNameError, \
    MipsAttributeCantSetError
from compiler.look_ahead_can_assign import LACanAssign
from compiler.look_ahead_expr_rearrange import LAExprRearrange
from compiler.look_ahead_return_type import LAReturnType
from compiler.types import Device, Function, Variable

from lark import Tree
from lark.lexer import Token


class InstBuilder(Visitor):

    def __init__(self):
        self._free_register_counter = 0
        self.idtable = {'out': 'o'}
        self.device_table = {'db': Device('db', 'Socket')}
        self.vtable = {'label': Function(self._label, Device()), 'device': Function(self._label, Device())}
        self.labels = {}
        self.label = 0
        self.program = []

    @contextmanager
    def free_register(self, can_direct_access=None, store_dst=None):
        """
        :param check_direct_access: Node to check if it can put it result directly into a register
        :param store_dst: if we already know the register to store the result we dont need a free register
        :return: Destination register
        """
        # We know where to store the result so we dont need a free register
        if store_dst:
            yield store_dst
            return

        if can_direct_access:
            if self._free_register_counter < 0 or self._free_register_counter > 15:
                raise MipsCodeError(f'Invalid register r{self._free_register_counter}')
            yield f'r{self._free_register_counter}'
            return

        self._free_register_counter += 1
        if self._free_register_counter < 0 or self._free_register_counter > 15:
            raise MipsCodeError(f'Invalid register r{self._free_register_counter}')
        yield f'r{self._free_register_counter}'
        self._free_register_counter -= 1

    @property
    def cur_register(self):
        if self._free_register_counter < 0 or self._free_register_counter > 15:
            raise MipsCodeError(f'Invalid register r{self._free_register_counter}')
        return f'r{self._free_register_counter}'

    def cur_stack_dst(self, store_dst=None):
        if store_dst:
            return store_dst
        return self.cur_register

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

    def root(self, stmts):
        for stmt in stmts.children:
            self.visit(stmt)

    def var(self, var, assignment=False, store_dst=None):
        name: str = var.children[0].value

        if name in self.idtable:
            return f'{self.idtable[name]}'
        elif name in self.device_table:
            return self.device_table[name]
        elif assignment:
            self.idtable[name] = self.cur_register
            self._free_register_counter += 1
            return self.idtable[name]
        else:
            raise MipsUnboundLocalError(name)

    def const_true(self, token, store_dst=None):
        return '1'

    def const_false(self, token, store_dst=None):
        return '0'

    def loc(self, loc, store_dst=None):
        return loc.children[0].value

    def factor(self, number, store_dst=None):
        if number.children[0].value == '-':
            return f'-{self.visit(number.children[1])}'
        raise Exception(f'Unknown factor "{number.children[0].value}"')

    def number(self, number, store_dst=None):
        value = number.children[0].value
        return value

    def _label(self, _, args):
        device = args[0].children[0].value
        if args[1].data == 'string':
            prop = args[1].children[0].value[1:-1]
        else:
            prop = args[1].children[0].value

        self._add_instruction(f'alias {prop} {device}', f'alias {prop} {device}')
        return Device(device, prop)

    def if_stmt(self, stmt):
        exit_jump = self._create_label()
        self._recursive_if_stmt(stmt.children.copy(), exit_jump)
        self._insert_label(exit_jump)

    def and_test(self, stmt, store_dst=None):
        lst = stmt.children.copy()
        with self.free_register(store_dst=store_dst) as t0:
            while len(lst) >= 2:
                ret = self.operator(lst[0], 'and', lst[1], store_dst=t0)
                lst = lst[2:]
                lst.insert(0, Tree('loc', [Token('loc', t0)]))
            return t0

    def or_test(self, stmt, store_dst=None):
        lst = stmt.children.copy()
        with self.free_register(store_dst=store_dst) as t0:
            while len(lst) >= 2:
                ret = self.operator(lst[0], 'or', lst[1], store_dst=t0)
                lst = lst[2:]
                lst.insert(0, Tree('loc', [Token('loc', t0)]))
            return t0

    def not_test(self, stmt, store_dst=None):
        lst = stmt.children.copy()
        with self.free_register(store_dst=store_dst) as t0:
            while len(lst) >= 1:
                ret = self.unary_operator('not', lst[0], store_dst=t0)
                lst = lst[1:]
            return t0

    def test(self, stmt, store_dst=None):
        lst = stmt.children.copy()

        n_lst = [lst[1], lst[0], lst[2]]
        self._recursive_if_stmt(n_lst, exit_jump=None, is_expr=True, store_dst=store_dst)
        return store_dst

    def assignment_stmt(self, stmt):

        id = stmt.children[0]
        expr = stmt.children[1]
        expr_return_type = LAReturnType(self, expr).return_type

        if isinstance(expr_return_type, Device):
            r0 = self.visit(expr, assignment=True)
            self.device_table[stmt.children[0].children[0].value] = r0
            return
        else:
            # Get the destination by visit the id.
            dst = self.visit(id, assignment=True)

        expr_can_assign = LACanAssign(expr).result
        store_dst = dst if dst in self.idtable.values() else None
        with self.free_register(can_direct_access=expr_can_assign,
                                store_dst=store_dst) as t0:
            t0 = self.visit(expr, store_dst=t0)

        if isinstance(dst, Device):
            self._save_attr(t0, dst, dst.property_access[0])
        elif not expr_can_assign:
            self._push_copy_inst(src=t0, dst=dst)

    def _recursive_if_stmt(self, stmt_lst, exit_jump, is_expr=False, store_dst=None):
        if len(stmt_lst) >= 2:
            test = stmt_lst[0]
            if_suite = stmt_lst[1]

            with self.free_register(can_direct_access=LACanAssign(test).result) as t0:
                t0 = self.visit(test, store_dst=t0)
            con_jump_label = self._push_conditional_jump_inst(t0, None)
            # Else stmt
            self._recursive_if_stmt(stmt_lst[2:], exit_jump, is_expr=is_expr, store_dst=store_dst)

            jump_label = self._push_jump_inst(exit_jump)
            self._insert_label(con_jump_label)
            # True

            if is_expr:
                with self.free_register( can_direct_access=LACanAssign(if_suite).result, store_dst=store_dst):
                    t0 = self.visit(if_suite, store_dst=store_dst)
                self._stmt_lookahead_copy = True
                self._push_copy_inst(src=t0, dst=self.cur_stack_dst(store_dst))
            else:
                self.visit(if_suite)

            self._insert_label(jump_label)
        elif len(stmt_lst) == 1:
            else_suite = stmt_lst[0]

            if is_expr:
                with self.free_register(else_suite):
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
        with self.free_register(test, store_dst=store_dst) as s0:
            r0 = self.visit(test, store_dst=s0)

        con_jump_label = self._push_conditional_jump_inst(r0, None)
        end_jump = self._push_jump_inst()

        self._insert_label(con_jump_label)
        self.visit(suite)
        self._insert_label(init_jump)
        self._push_jump_inst(jump_label)
        self._insert_label(end_jump)

    def stmt(self, stmt):
        for s in stmt.children:
            self.visit(s)

    def suite(self, stmt):
        for s_stmt in stmt.children:
            self.visit(s_stmt)

    def compound_stmt(self, stmt):
        self.visit(stmt.children[0])

    def yield_stmt(self, stmt):
        self._add_instruction('yield', 'yield')

    def reduce_expr(self, tree, store_dst=None):
        lst = tree.children.copy()
        expr_eval_dst = store_dst

        if LAExprRearrange(store_dst, tree).tree is None:
            # store_dst is an id hence check if it can be used directly else
            # use a tmp register
            expr_eval_dst = None
        with self.free_register(store_dst=expr_eval_dst) as t0:
            eval_store = t0
            while len(lst) >= 3:
                eval_store = t0 if len(lst) >= 5 else store_dst  # use store_dst if final eval
                eval_store = self.operator(*lst[0:3], store_dst=eval_store)
                lst = lst[3:]
                lst.insert(0, Tree('loc', [Token('loc', t0)]))
            return eval_store

    def unary_operator(self, op, right, store_dst=None):
        with self.free_register(right, store_dst=store_dst) as s0:
            r0 = self.visit(right, store_dst=s0)

        dst = self.cur_stack_dst(store_dst)
        if op == 'not':
            self._add_instruction(f'xor {dst} {r0} 1', f'not {r0} -> {dst}')

        return dst

    def operator(self, left, op: Token, right, store_dst=None):

        with self.free_register(LACanAssign(left).result, store_dst=store_dst) as s0:
            r0 = self.visit(left, store_dst=s0)
            with self.free_register() as s1:
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

    def subscriptlist(self, expr, store_dst=None):
        return self.visit(expr.children[0], store_dst=store_dst)

    def subscript(self, expr, store_dst=None):
        return self.visit(expr.children[0],  store_dst=store_dst)

    def term(self, expr, store_dst=None):
        return self.reduce_expr(expr, store_dst=store_dst)

    def arith_expr(self, expr, store_dst=None):
        return self.reduce_expr(expr, store_dst=store_dst)

    def comparison(self, expr, store_dst=None):
        return self.reduce_expr(expr, store_dst=store_dst)

    def atom_expr(self, expr, store_dst=None):
        dst = self.cur_stack_dst(store_dst=store_dst)
        return dst

    def call(self, expr, store_dst=None, **kwargs):
        with self.free_register(store_dst=store_dst) as dst:
            ret = None
            if isinstance(expr.children[0], Tree):
                tree = expr.children[0]
                if len(expr.children) > 1 and isinstance(expr.children[1], Tree) and expr.children[1].data == 'arguments':
                    if tree.children[0].value in self.vtable:
                        arguments = expr.children[1]
                        ret = self.vtable[tree.children[0].value].var(
                            dst,
                            arguments.children)
            if ret:
                return ret
            return dst

    def attr_get(self, expr, store_dst=None):
        if store_dst:

            index_expr = expr.children[1]
            dot_access_expr = expr.children[0]
            with self.free_register() as r0:
                r0 = self.visit(index_expr, store_dst=r0)
            dst = self.cur_stack_dst(store_dst=store_dst)

            device = self.visit(dot_access_expr)
            self._load_attr_slot(dst=dst, device=device, prop=device.property_access[0], slot=r0)
            return dst
        else:
            raise Exception("Slot access read only")

    def dot_access(self, expr, store_dst=None, assignment=None, **kwargs):
        if store_dst:
            dst = self.cur_stack_dst(store_dst=store_dst)
            prop = expr.children[1]
            device = self.visit(expr.children[0], store_dst=store_dst)
            if device not in self.device_table.values():
                if device in self.idtable.values():
                    raise MipsAttributeError(device, prop)
                if assignment:
                    raise MipsNameError(device)
                raise MipsUnboundLocalError(device)
            if prop.startswith("Reagent"):
                # Handle Reagents as a special case property
                args = prop.split('_')
                self._load_reagent(dst=dst, device=device, mode_str=args[1], reagent_str=args[2])
            else:
                self._load_attr(dst=dst, device=device, prop=prop)
            return dst
        else:
            prop = expr.children[1].value
            try:
                device = self.visit(expr.children[0], store_dst=store_dst)
            except MipsUnboundLocalError as exc:
                raise MipsNameError(exc.name)
            ret = device.access_prop(device, property_access=prop)
            return ret

    def _load_attr(self, dst, device: Device, prop: Token):
        prop_str = prop.value
        if device not in self.device_table.values():
            raise MipsAttributeError(device, prop_str)
        self._add_instruction(f'l {dst} {device.device} {prop_str}', f'load {device.device} {prop_str} to {dst}')

    def _load_reagent(self, dst, device: Device, mode_str: str, reagent_str: str):
        if device not in self.device_table.values():
            raise MipsAttributeError(device, mode_str)
        self._add_instruction(f'lr {dst} {device.device} {mode_str} {reagent_str}', f'load reagent {device.device} {mode_str} {reagent_str} to {dst}')

    def _load_attr_slot(self, dst, device: Device, prop: str, slot):
        self._add_instruction(f'ls {dst} {device.device} {slot} {prop}', f'load {device.device} {prop}[{slot}] to {dst}')

    def _save_attr(self, var, device: Device, prop: str):
        if prop.startswith("Reagent"):
            # Special case for Reagent where we cant assign
            raise MipsAttributeCantSetError(prop)
        self._add_instruction(f's {device.device} {prop} {var}', f'save {var} to {device.device} {prop}')
