from graphviz import Digraph
import re


# Syntax tree node kinds

class Base:
    def __init__(self) -> None:
        self.dot = Digraph()
        self.name = str(id(self))


class Program(Base):
    def __init__(self, funcs, diffarg, exprs) -> None:
        super().__init__()
        self.funcs = funcs
        self.diffarg = diffarg
        self.exprs = exprs

        self.dot.node(self.name, label="Program")
        if self.funcs is not None:
            self.dot.subgraph(self.funcs.dot)
            self.dot.edge(self.name, self.funcs.name)
        if self.diffarg is not None:
            self.dot.subgraph(self.diffarg.dot)
            self.dot.edge(self.name, self.diffarg.name)
        if self.exprs is not None:
            self.dot.subgraph(self.exprs.dot)
            self.dot.edge(self.name, self.exprs.name)

    def exec(self):
        if self.funcs is not None:
            self.funcs.compute(self.diffarg is not None)
        if self.exprs is None:
            print("No expressions were provided for execution")
        result = {}
        result["python_exprs"] = self.exprs.to_python_exprs()
        if self.diffarg is not None:
            result["diff_exprs"] = self.exprs.differentiate_exprs(
                self.diffarg())
        return result


class Funcs(Base):
    def __init__(self, func, funcs) -> None:
        super().__init__()
        self.func = func
        self.funcs = funcs

        self.dot.node(self.name, label="Funcs")
        if self.funcs is not None:
            self.dot.subgraph(self.funcs.dot)
            self.dot.edge(self.name, self.funcs.name)

        self.dot.subgraph(self.func.dot)
        self.dot.edge(self.name, self.func.name)

    def compute(self, differentiate):
        self.func.compute(differentiate)
        if self.funcs is not None:
            self.funcs.compute(differentiate)


class Func(Base):
    def __init__(self, funcname, arg, expr) -> None:
        super().__init__()
        self.funcname = funcname
        self.arg = arg
        self.expr = expr

        self.diff_expr = None
        self.python_expr = None

        self.dot.node(self.name, label=self.funcname + "(" + self.arg + ")")
        self.dot.subgraph(self.expr.dot)
        self.dot.edge(self.name, self.expr.name)

    def __call__(self, expr, diffarg=None, diff=False):
        if diff:
            return re.sub(r'(\W?)self.arg(\W?)', expr.to_python_expr(), self.diff_expr) + "*" + expr.differentiate_expr(
                diffarg)
        return re.sub(r'(\W?)self.arg(\W?)', expr.to_python_expr(), self.python_expr)

    def compute(self, differentiate):
        if differentiate:
            self.diff_expr = self.expr.differentiate_expr(self.arg)
        self.python_expr = self.expr.to_python_expr()


class Diffarg(Base):
    def __init__(self, diffby) -> None:
        super().__init__()
        self.diffby = diffby

        self.dot.node(self.name, label="diff by " + self.diffby)

    def __call__(self):
        return self.diffby


class Exprs(Base):
    def __init__(self, expr, exprs) -> None:
        super().__init__()
        self.expr = expr
        self.exprs = exprs

        self.dot.node(self.name, label="Exprs")

        if self.exprs is not None:
            self.dot.subgraph(self.exprs.dot)
            self.dot.edge(self.name, self.exprs.name)

        self.dot.subgraph(self.expr.dot)
        self.dot.edge(self.name, self.expr.name)

    def to_python_exprs(self):
        python_exprs = []
        if self.exprs is not None:
            python_exprs = self.exprs.to_python_exprs()
        python_exprs.append(self.expr.to_python_expr())
        return python_exprs

    def differentiate_exprs(self, diffarg):
        diff_exprs = []
        if self.exprs is not None:
            diff_exprs = self.exprs.differentiate_exprs(diffarg)
        diff_exprs.append(self.expr.differentiate_expr(diffarg))
        return diff_exprs


class Expr(Base):
    def __init__(self, head, funcs) -> None:
        super().__init__()
        self.head = head
        self.dot.node(self.name, label=self.head)
        self.funcs = funcs

    def to_python_expr(self):
        pass

    def differentiate_expr(self, diffarg):
        pass


class UnOp(Expr):
    def __init__(self, op, expr, funcs):
        super().__init__(op, funcs)

        self.expr = expr

        self.dot.subgraph(self.expr.dot)
        self.dot.edge(self.name, self.expr.name)

    def to_python_expr(self):
        head = self.head
        if head == "ln":
            head = "log"
        else:
            if head == "log":
                head = "log10"

        expr = self.expr.to_python_expr()

        if expr[0] == "(" and expr[len(expr) - 1] == ")":
            for i in range(1, len(expr) - 1):
                if expr[i] == "(" or expr[i] == ")":
                    expr = "(" + expr + ")"

        return "(" + head + expr + ")"

    def differentiate_expr(self, diffarg):
        return "(" + self.head + self.expr.differentiate_expr(diffarg) + ")"


class FuncOp(UnOp):
    def __init__(self, func, expr, funcs):
        super().__init__(func, expr, funcs)

    def to_python_expr(self):
        if self.head in self.funcs:
            return self.funcs[self.head](self.expr)
        else:
            return super().to_python_expr()

    def differentiate_expr(self, diffarg):
        if self.head in self.funcs:
            return self.funcs[self.head](self.expr, diffarg, diff=True)

        expr_diff = self.expr.differentiate_expr(diffarg)
        expr = self.expr.to_python_expr()

        if expr_diff == "0":
            return "0"

        if expr[0] == "(" and expr[len(expr) - 1] == ")":
            for i in range(1, len(expr) - 1):
                if expr[i] == "(" or expr[i] == ")":
                    expr = "(" + expr + ")"

        if self.head == "sin":
            if expr_diff == "1":
                return "cos" + expr
            return "cos" + expr + "*" + expr_diff

        if self.head == "cos":
            if expr_diff == "1":
                return "(-sin" + expr + ")"
            return "(-sin" + expr + ")*" + expr_diff

        if self.head == "log":
            if expr_diff == "1":
                return "1/(" + expr + "*log(10))"
            return "1/(" + expr + "*log(10))*" + expr_diff

        if self.head == "ln":
            if expr_diff == "1":
                return "1/" + expr + ""
            return "1/" + expr + "*" + expr_diff

        if self.head == "tan":
            if expr_diff == "1":
                return "1/(cos" + expr + ")**2"
            return "1/(cos" + expr + ")**2*" + expr_diff

        if self.head == "exp":
            if expr_diff == "1":
                return "exp" + expr
            return "exp" + expr + "*" + expr_diff

        if self.head == "sqrt":
            if expr_diff == "1":
                return "1/(2*sqrt" + expr + ")"
            return "1/(2*sqrt" + expr + ")*" + expr_diff


def is_digit(string):
    if string.isdigit():
        return 1
    try:
        float(string)
        return 2
    except ValueError:
        return 0


class BinOp(Expr):
    def __init__(self, op, left, right, funcs):
        super().__init__(op, funcs)

        self.left = left
        self.right = right

        self.dot.subgraph(self.left.dot)
        self.dot.subgraph(self.right.dot)

        self.dot.edge(self.name, self.left.name)
        self.dot.edge(self.name, self.right.name)

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

                if is_digit(left_expr) == 1:
                    number = int(left_expr)
                    return str(number * 2)
                if is_digit(left_expr) == 2:
                    number = float(left_expr)
                    return str(number * 2)
                return "2*" + left_expr

            if is_digit(left_expr) != 0 and is_digit(right_expr) != 0:
                if is_digit(left_expr) == 1 and is_digit(right_expr) == 1:
                    num_1 = int(left_expr)
                    num_2 = int(right_expr)
                else:
                    num_1 = float(left_expr)
                    num_2 = float(right_expr)
                if head == "+":
                    return str(num_1 + num_2)
                return str(num_1 - num_2)


        else:
            if head == "*":
                if right_expr == "0" or left_expr == "0":
                    return "0"
                if right_expr == "1":
                    return left_expr
                if left_expr == "1":
                    return right_expr

                if is_digit(left_expr) != 0 and is_digit(right_expr) != 0:
                    if is_digit(left_expr) == 1 and is_digit(right_expr) == 1:
                        num_1 = int(left_expr)
                        num_2 = int(right_expr)
                    else:
                        num_1 = float(left_expr)
                        num_2 = float(right_expr)
                    return str(num_1 * num_2)

            else:
                if head == "/":
                    if right_expr == "0":
                        raise Exception('You cannot divide by zero')
                    if right_expr != "0" and left_expr == "0":
                        return "0"
                    if left_expr == right_expr:
                        return "1"

                    if is_digit(left_expr) != 0 and is_digit(right_expr) != 0:
                        num_1 = float(left_expr)
                        num_2 = float(right_expr)
                        return str(num_1 / num_2)
                else:
                    if right_expr == "0" or left_expr == "1":
                        return "1"
                    if is_digit(left_expr) != 0 and is_digit(right_expr) != 0:
                        if is_digit(left_expr) == 1 and is_digit(right_expr) == 1:
                            num_1 = int(left_expr)
                            num_2 = int(right_expr)
                        else:
                            num_1 = float(left_expr)
                            num_2 = float(right_expr)
                        return str(num_1 ** num_2)

        return "(" + self.left.to_python_expr() + head + self.right.to_python_expr() + ")"

    def differentiate_expr(self, diffarg):

        left_diff = self.left.differentiate_expr(diffarg)
        right_diff = self.right.differentiate_expr(diffarg)

        if left_diff == "0" and right_diff == "0" and self.head != '/':
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

                if is_digit(left_diff) == 1:
                    num = int(left_diff)
                    return str(num * 2)
                if is_digit(left_diff) == 2:
                    num = float(left_diff)
                    return str(num * 2)
                return "2*" + left_diff

            if is_digit(left_diff) != 0 and is_digit(right_diff) != 0:
                if is_digit(left_diff) == 1 and is_digit(right_diff) == 1:
                    num1 = int(left_diff)
                    num2 = int(right_diff)
                else:
                    num1 = float(left_diff)
                    num2 = float(right_diff)
                if self.head == '+':
                    return str(num1 + num2)
                return str(num1 - num2)

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

            if is_digit(left_diff) != 0 and is_digit(right_to_python) != 0:
                if is_digit(left_diff) == 1 and is_digit(right_to_python) == 1:
                    num1 = int(left_diff)
                    num2 = int(right_to_python)
                else:
                    num1 = float(left_diff)
                    num2 = float(right_to_python)
                return str(num1 * num2)

            if is_digit(left_to_python) != 0 and is_digit(right_diff) != 0:
                if is_digit(left_to_python) == 1 and is_digit(right_diff) == 1:
                    num1 = int(right_diff)
                    num2 = int(left_to_python)
                else:
                    num1 = float(right_diff)
                    num2 = float(left_to_python)
                return str(num1 * num2)

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

            if right_to_python == "0":
                raise Exception('You cannot divide by zero')
            if left_diff == "0" and right_diff == "0":
                return "0"
            if left_to_python == "0" or left_to_python == right_to_python:
                return "0"
            if right_to_python == "1":
                return left_diff
            if left_to_python == "1":
                if right_to_python[0] == "(" and right_to_python[len(right_to_python) - 1] == ")":
                    for i in range(1, len(right_to_python) - 1):
                        if right_to_python[i] == "(" or right_to_python[i] == ")":
                            right_to_python = "(" + right_to_python + ")"
                return "(-" + right_diff + ")/" + right_to_python + "**2"

            new_left_expr = left_diff + "*" + right_to_python
            new_right_expr = left_to_python + "*" + right_diff

            if is_digit(left_diff) != 0 and is_digit(right_to_python) != 0:
                num1 = float(left_diff)
                num2 = float(right_to_python)
                return str(num1 / num2)

            if is_digit(left_to_python) != 0 and is_digit(right_diff) != 0:
                num1 = float(right_diff)
                num2 = float(left_to_python)
                num = -num1 * num2

                if right_to_python[0] == "(" and right_to_python[len(right_to_python) - 1] == ")":
                    for i in range(1, len(right_to_python) - 1):
                        if right_to_python[i] == "(" or right_to_python[i] == ")":
                            right_to_python = "(" + right_to_python + ")"

                if num > 0:
                    return str(num) + "/" + right_to_python + "**2"
                return "(" + str(num) + ")/" + right_to_python + "**2"

            if right_diff == "1":
                new_right_expr = left_to_python
            if left_diff == "1":
                new_left_expr = right_to_python

            if right_to_python[0] == "(" and right_to_python[len(right_to_python) - 1] == ")":
                for i in range(1, len(right_to_python) - 1):
                    if right_to_python[i] == "(" or right_to_python[i] == ")":
                        right_to_python = "(" + right_to_python + ")"

            if right_diff == "0":
                return new_left_expr + "/" + right_to_python + "**2"
            if left_diff == "0":
                return "(-" + new_right_expr + ")/" + right_to_python + "**2"

            return "(" + new_left_expr + "-" + new_right_expr + ")/" + right_to_python + "**2"

        if self.head == "^":
            if left_to_python == "0" or right_to_python == "0" or left_to_python == "1":
                return "0"
            if right_to_python == "1":
                return left_diff

            new_left_expr = right_to_python + "*" + left_to_python + "**(" + right_to_python + "-1)*" + left_diff
            new_right_expr = left_to_python + "**" + right_to_python + "*log(" + left_to_python + ")*" + right_diff

            if left_to_python[0] == "(" and left_to_python[len(left_to_python) - 1] == ")":
                flag = True
                for i in range(1, len(left_to_python) - 1):
                    if left_to_python[i] == "(" or left_to_python[i] == ")":
                        flag = False
                        break
                if flag:
                    new_right_expr = left_to_python + "**" + right_to_python + "*log" + left_to_python + "*" + right_diff

            if is_digit(left_diff) != 0 and is_digit(right_to_python) != 0:
                if is_digit(left_diff) == 1 and is_digit(right_to_python) == 1:
                    num1 = int(left_diff)
                    num2 = int(right_to_python)
                else:
                    num1 = float(left_diff)
                    num2 = float(right_to_python)
                return str(num1 * num2) + "*" + left_to_python + "**" + str(num2 - 1)

            if right_diff == "1":
                new_right_expr = left_to_python + "**" + right_to_python + "*log(" + left_to_python + ")"
            if left_diff == "1":
                new_left_expr = right_to_python + "*" + left_to_python + "**(" + right_to_python + "-1)"

            if right_diff == "0":
                return new_left_expr
            if left_diff == "0":
                return new_right_expr

            return "(" + new_left_expr + "+" + new_right_expr + ")"


class ID(Expr):
    def __init__(self, id, funcs):
        super().__init__(id, funcs)

    def to_python_expr(self):
        return self.head

    def differentiate_expr(self, diffarg):
        if self.head == diffarg:
            return "1"
        return "0"


class Number(Expr):
    def __init__(self, value, funcs):
        super().__init__(str(value), funcs)
        self.value = value

    def to_python_expr(self):
        return self.head

    def differentiate_expr(self, diffarg):
        return "0"
