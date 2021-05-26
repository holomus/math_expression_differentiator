from sly import Lexer, Parser
from graphviz import Digraph

class mathLexer(Lexer):
    # Set of token names.
    tokens = { NUMBER, ID,
               SIN, COS, LOG, LN, TAN, EXP, SQRT, FUNC,
               PLUS, MINUS, TIMES, DIVIDE, POW, }


    literals = { '(', ')' }

    # String containing ignored characters
    ignore = ' \t'

    # Regular expression rules for tokens
    PLUS    = r'\+'
    MINUS   = r'-'
    TIMES   = r'\*'
    DIVIDE  = r'/'
    POW     = r'\^'

    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    # Identifiers and keywords
    ID          = r'[a-zA-Z_][a-zA-Z0-9_]*'
    ID['sin']   = SIN
    ID['cos']   = COS
    ID['log']   = LOG
    ID['tan']   = TAN
    ID['exp']   = EXP
    ID['LN']    = LN
    ID['sqrt']  = SQRT
    ID['func']  = FUNC
    

class mathParser(Parser):
    tokens = mathLexer.tokens

    # Operator predence taken from 
    # Python operator precedence list
    # https://docs.python.org/3/reference/expressions.html#operator-precedence
    precedence = (
        ('left', PLUS, MINUS),
        ('left', DIVIDE, TIMES),
        ('left', POW),        
        ('right', UMINUS, UPLUS),
        ('right', SIN, COS, LOG, LN,
                  TAN, EXP, SQRT, FUNC)
    )

    def __init__(self) -> None:
        super().__init__()
        self.names = { }

    # Syntax tree node kinds
    class Program:
        def __init__(self) -> None:
            self.dot = Digraph()
    
    class Funcs(Program):
        def __init__(self, func, funcs) -> None:
            super().__init__()
            self.func = func
            self.funcs = funcs
    
    class Func(Program):
        def __init__(self, name, arg, expr) -> None:
            super().__init__()
            self.name = name
            self.arg = arg
            self.expr = expr
            
            self.dot.node(self.name + "(" + self.arg + ")")
            self.dot.subgraph(self.expr.dot)
            self.dot.edge(self.name + "(" + self.arg + ")", self.expr.head)
            
    
    class DIFFARG(Program):
        def __init(self, diffby) -> None:
            super().__init__()
            self.diffby = diffby
            
            self.dot.node("diif by " + self.diffby)
    
    class Exprs(Program):
        def __init__(self, expr, exprs) -> None:
            super().__init__()
            self.expr = expr
            self.exprs = exprs
            
    
    class Expr:
        def __init__(self, head) -> None:
            self.head = head
            self.dot.node(self.head)
        
        def to_python_expr(self):
            pass

        def differentiate_expr(self):
            pass

    class UnOp(Expr):
        def __init__(self, op, expr):
            super().__init__(op)

            self.expr = expr

            self.dot.subgraph(self.expr.dot)
            self.dot.edge(self.head, self.expr.head)

        def to_python_expr(self):
            return self.head + "(" + self.expr.to_python_expr() + ")" 


    class FuncOp(UnOp):
        def __init__(self, func, expr):
            super().__init__(func, expr)

        def differentiate_expr(self):
            pass

    class BinOp(Expr):
        def __init__(self, op, left, right):
            super().__init__(op)

            self.left = left
            self.right = right

            self.dot.subgraph(self.left.dot)
            self.dot.subgraph(self.right.dot)

            self.dot.edge(self.head, self.left.head)
            self.dot.edge(self.head, self.right.head)

        def to_python_expr(self):
            head = self.head
            if (self.head == "^"):
                head = "**"
            return "(" + self.left.to_python_expr() + head + self.right.to_python_expr() + ")"

        def differentiate_expr(self):
            pass
        
    class ID(Expr):
        def __init__(self, id):
            super().__init__(id)

        def to_python_expr(self):
            return "x"

        def differentiate_expr(self):
            return "1"


    class Number(ID):
        def __init__(self, value):
            super().__init__(str(value))
            
            self.value = value

        def differentiate_expr(self):
            return "0"

    # Grammar rules and actions
    @_('expr PLUS expr',
    'expr MINUS expr',
    'expr TIMES expr',
    'expr DIVIDE expr',
    'expr POW expr')
    def expr(self, p):
        return self.BinOp(p[1], p.expr0, p.expr1)

    @_('MINUS expr %prec UMINUS',
       'PLUS  expr %prec UPLUS')
    def expr(self, p):
        return self.UnOp(p[0], p.expr)

    @_('SIN  expr',
       'COS  expr',
       'LOG  expr',
       'LN   expr',
       'TAN  expr',
       'EXP  expr',
       'SQRT expr',
       'FUNC expr')
    def expr(self, p):
        return self.Func(p[0], p.expr)


    @_('"(" expr ")"')
    def expr(self, p):
        return p.expr

    @_('ID')
    def expr(self, p):
        self.names[p.ID] = p.ID
        return self.ID(p.ID)

    @_('NUMBER')
    def expr(self, p):
        return self.Number(p.NUMBER)

