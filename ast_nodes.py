from graphviz import Digraph

# Syntax tree node kinds


class Base:
    def __init__(self) -> None:
        self.dot = Digraph()


class Program(Base):
    def __init__(self, funcs, diffarg, exprs) -> None:
        super().__init__()
        self.funcs = funcs
        self.diffarg = diffarg
        self.exprs = exprs


class Funcs(Base):
    def __init__(self, func, funcs) -> None:
        super().__init__()
        self.func = func
        self.funcs = funcs


class Func(Base):
    def __init__(self, name, arg, expr) -> None:
        super().__init__()
        self.name = name
        self.arg = arg
        self.expr = expr

        self.dot.node(self.name + "(" + self.arg + ")")
        self.dot.subgraph(self.expr.dot)
        self.dot.edge(self.name + "(" + self.arg + ")", self.expr.head)


class DIFFARG(Base):
    def __init__(self, diffby) -> None:
        super().__init__()
        self.diffby = diffby

        self.dot.node("diff by " + self.diffby)


class Exprs(Base):
    def __init__(self, expr, exprs) -> None:
        super().__init__()
        self.expr = expr
        self.exprs = exprs


class Expr(Base):
    def __init__(self, head, funcs) -> None:
        super().__init__()
        self.head = head
        self.dot.node(self.head)
        self.funcs = funcs

    def to_python_expr(self):
        pass

    def differentiate_expr(self):
        pass


class UnOp(Expr):
    def __init__(self, op, expr, funcs):
        super().__init__(op, funcs)

        self.expr = expr

        self.dot.subgraph(self.expr.dot)
        self.dot.edge(self.head, self.expr.head)

    def to_python_expr(self):
        return "(" + self.head + self.expr.to_python_expr() + ")"

    def differentiate_expr(self):
        return "(" + self.head + self.expr.differentiate_expr() + ")"


class FuncOp(UnOp):
    def __init__(self, func, expr, funcs):
        super().__init__(func, expr, funcs)

    def differentiate_expr(self):
        expr_diff = self.expr.differentiate_expr()
        if expr_diff == "0":
            return "0"

        if self.head == "sin":
            if expr_diff == "1":
                return "cos" + self.expr.to_python_expr()
            return "cos" + self.expr.to_python_expr() + "*" + expr_diff

        if self.head == "cos":
            if expr_diff == "1":
                return "(-sin" + self.expr.to_python_expr() + ")"
            return "(-sin" + self.expr.to_python_expr() + ")*" + expr_diff

        if self.head == "log":
            if expr_diff == "1":
                return "1/(" + self.expr.to_python_expr() + "*ln(10))"
            return "1/(" + self.expr.to_python_expr() + "*ln(10))*" + expr_diff

        if self.head == "ln":
            if expr_diff == "1":
                return "1/" + self.expr.to_python_expr()
            return "1/" + self.expr.to_python_expr() + "*" + expr_diff

        if self.head == "tan":
            if expr_diff == "1":
                return "1/(cos" + self.expr.to_python_expr() + ")**2"
            return "1/(cos" + self.expr.to_python_expr() + ")**2*" + expr_diff

        if self.head == "exp":
            if expr_diff == "1":
                return "exp" + self.expr.to_python_expr()
            return "exp" + self.expr.to_python_expr() + "*" + expr_diff

        if self.head == "sqrt":
            if expr_diff == "1":
                return "1/(2*sqrt" + self.expr.to_python_expr() + ")"
            return "1/(2*sqrt" + self.expr.to_python_expr() + ")*" + expr_diff


class BinOp(Expr):
    def __init__(self, op, left, right, funcs):
        super().__init__(op, funcs)

        self.left = left
        self.right = right

        self.dot.subgraph(self.left.dot)
        self.dot.subgraph(self.right.dot)

        self.dot.edge(self.head, self.left.head)
        self.dot.edge(self.head, self.right.head)

    def to_python_expr(self):
        head = self.head
        if self.head == "^":
            head = "**"

        left_expr = self.left.to_python_expr()
        right_expr = self.right.to_python_expr()

        if head == "+" or head == "-":
            if right_expr == "0":
                return left_expr
            if left_expr == "0":
                if head == "-":
                    return "(-" + right_expr + ")"
                return right_expr
            if left_expr == right_expr:
                if head == "-":
                    return "0"
                return "2*" + left_expr
        else:
            if head == "*":
                if right_expr == "0" or left_expr == "0":
                    return "0"
                if right_expr == "1":
                    return left_expr
                if left_expr == "1":
                    return right_expr

            else:
                if head == "/":
                    if right_expr != "0" and left_expr == "0":
                        return "0"
                    if left_expr == right_expr:
                        return "1"
                else:
                    if right_expr == "0" or left_expr == "1":
                        return "1"
        return "(" + self.left.to_python_expr() + head + self.right.to_python_expr() + ")"

    def differentiate_expr(self):

        left_diff = self.left.differentiate_expr()
        right_diff = self.right.differentiate_expr()

        if left_diff == "0" and right_diff == "0":
            return "0"

        if self.head == "+" or self.head == "-":
            if left_diff == "0":
                if self.head == "-":
                    return "(-" + right_diff + ")"
                return right_diff

            if right_diff == "0":
                return left_diff

            if left_diff == right_diff:
                if self.head == "-":
                    return "0"
                return "2*" + left_diff

            return "(" + left_diff + self.head + right_diff + ")"

        left_to_python = self.left.to_python_expr()
        right_to_python = self.right.to_python_expr()

        if self.head == "*":
            if left_to_python == "0" or right_to_python == "0":
                return "0"
            if right_to_python == "1":
                return left_diff
            if left_to_python == "1":
                return right_diff

            new_left_expr = left_diff + "*" + right_to_python
            new_right_expr = right_diff + "*" + left_to_python

            if right_diff == "1":
                new_right_expr = left_to_python
            if left_diff == "1":
                new_left_expr = right_to_python

            if right_diff == "0":
                return new_left_expr
            if left_diff == "0":
                return new_right_expr

            if new_left_expr == new_right_expr:
                return "2*" + new_left_expr

            return "(" + new_left_expr + "+" + new_right_expr + ")"

        if self.head == "/":
            if left_to_python == "0" or left_to_python == right_to_python:
                return "0"
            if right_to_python == "1":
                return left_diff
            if left_to_python == "1":
                return "(-" + right_diff + ")/(" + right_to_python + ")**2"

            new_left_expr = left_diff + "*" + right_to_python
            new_right_expr = left_to_python + "*" + right_diff
            if right_diff == "1":
                new_right_expr = left_to_python
            if left_diff == "1":
                new_left_expr = right_to_python

            if right_diff == "0":
                return new_left_expr + "/(" + right_to_python + ")**2"
            if left_diff == "0":
                return "(-" + new_right_expr + ")/(" + right_to_python + ")**2"

            return "(" + new_left_expr + "-" + new_right_expr + ")/(" + right_to_python + ")**2"

        if self.head == "^":
            if left_to_python == "0" or right_to_python == "0" or left_to_python == "1":
                return "0"
            if right_to_python == "1":
                return left_diff

            new_left_expr = right_to_python + "*" + left_to_python + \
                "**(" + right_to_python + "-1)*" + left_diff
            new_right_expr = left_to_python + "**" + right_to_python + \
                "*ln" + left_to_python + "*" + right_diff

            if right_diff == "1":
                new_right_expr = left_to_python + "**" + \
                    right_to_python + "*ln" + left_to_python
            if left_diff == "1":
                new_left_expr = right_to_python + "*" + \
                    left_to_python + "**(" + right_to_python + "-1)"

            if right_diff == "0":
                return new_left_expr
            if left_diff == "0":
                return new_right_expr

            return "(" + new_left_expr + "+" + new_right_expr + ")"


class ID(Expr):
    def __init__(self, id, funcs):
        super().__init__(id, funcs)

    # self.diff_arg = diff_arg

    def to_python_expr(self):
        return self.head

    def differentiate_expr(self):
        # if self.head == self.diff_arg:
        #     return "1"
        return "1"


class Number(Expr):
    def __init__(self, value, funcs):
        super().__init__(str(value), funcs)
        self.value = value

    def to_python_expr(self):
        return self.head

    def differentiate_expr(self):
        return "0"
