from sly import Parser
from diff_calc import mathLexer
import ast_nodes as ast


class mathParser(Parser):
    tokens = mathLexer.tokens
    debugfile = "parser.out"

    # Operator predence taken from
    # Python operator precedence list
    # https://docs.python.org/3/reference/expressions.html#operator-precedence
    precedence = (
        ('left', PLUS, MINUS),
        ('left', DIVIDE, TIMES),
        ('right', UMINUS, UPLUS),
        ('left', POW),
        ('right', SIN, COS, LOG, LN,
         TAN, EXP, SQRT, FUNC),
    )

    def __init__(self) -> None:
        super().__init__()
        self.funcs = {}

    def parse(self, tokens):
        self.funcs = {}
        return super().parse(tokens)

    # Grammar rules and actions

    @_('optfuncs optdiffarg optexprs')
    def program(self, p):
        return ast.Program(p.optfuncs, p.optdiffarg, p.optexprs)

    @_('')
    def empty(self, p):
        pass

    @_('funcs')
    def optfuncs(self, p):
        return p.funcs

    @_('empty')
    def optfuncs(self, p):
        pass

    @_('diffarg')
    def optdiffarg(self, p):
        return p.diffarg

    @_('empty')
    def optdiffarg(self, p):
        pass

    @_('exprs')
    def optexprs(self, p):
        return p.exprs

    @_('empty')
    def optexprs(self, p):
        pass

    @_('func funcs')
    def funcs(self, p):
        return ast.Funcs(p.func, p.funcs)

    @_('func')
    def funcs(self, p):
        return ast.Funcs(p.func, None)

    @_('DEF ID "(" ID ")" "{" expr "}"')
    def func(self, p):
        if p.ID0 in self.funcs:
            print("Function " + p.ID0 + " already defined")
        else:
            self.funcs[p.ID0] = ast.Func(p.ID0, p.ID1, p.expr)
            return self.funcs[p.ID0]

    @_('"{" DIFF ID "}"')
    def diffarg(self, p):
        return ast.DIFFARG(p.ID)

    @_('"{" expr "}" exprs')
    def exprs(self, p):
        return ast.Exprs(p.expr, p.exprs)

    @_('expr')
    def exprs(self, p):
        return ast.Exprs(p.expr, None)

    @_('expr PLUS expr',
       'expr MINUS expr',
       'expr TIMES expr',
       'expr DIVIDE expr',
       'expr POW expr')
    def expr(self, p):
        return ast.BinOp(p[1], p.expr0, p.expr1, self.funcs)

    @_('MINUS expr %prec UMINUS',
       'PLUS  expr %prec UPLUS')
    def expr(self, p):
        return ast.UnOp(p[0], p.expr, self.funcs)

    @_('SIN  expr',
       'COS  expr',
       'LOG  expr',
       'LN   expr',
       'TAN  expr',
       'EXP  expr',
       'SQRT expr')
    def expr(self, p):
        return ast.FuncOp(p[0], p.expr, self.funcs)

    @_('ID "(" expr ")" %prec FUNC')
    def expr(self, p):
        if p.ID not in self.funcs:
            print("Function " + p.ID0 + " not defined")
        else:
            return ast.FuncOp(p.ID, p.expr, self.funcs)

    @_('"(" expr ")"')
    def expr(self, p):
        return p.expr

    @_('ID')
    def expr(self, p):
        return ast.ID(p.ID, self.funcs)

    @_('NUMBER')
    def expr(self, p):
        return ast.Number(p.NUMBER, self.funcs)
