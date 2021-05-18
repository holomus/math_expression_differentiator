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
    class Expr:
        def __init__(self, head) -> None:
            self.head = head
            self.dot = Digraph()
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



    class Func(UnOp):
        def __init__(self, func, expr):
            super().__init__(func, expr)

    class BinOp(Expr):
        def __init__(self, op, left, right):
            super().__init__(op)

            self.left = left
            self.right = right

            self.dot.subgraph(self.left.dot)
            self.dot.subgraph(self.right.dot)

            self.dot.edge(self.head, self.left.head)
            self.dot.edge(self.head, self.right.head)

        
    class ID(Expr):
        def __init__(self, id):
            super().__init__(id)



    class Number(ID):
        def __init__(self, value):
            super().__init__(str(value))
            
            self.value = value


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

