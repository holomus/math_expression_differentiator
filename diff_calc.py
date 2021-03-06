from sly import Lexer
from sly.lex import LexError


class mathLexer(Lexer):
    # Set of token names.
    tokens = {NUMBER, ID,
              SIN, COS, LOG, LN, TAN, EXP, SQRT,
              PLUS, MINUS, TIMES, DIVIDE, POW,
              DIFF, DEF}

    literals = {'(', ')', '{', '}'}

    # String containing ignored characters
    ignore = ' \t'

    # Regular expression rules for tokens
    PLUS = r'\+'
    MINUS = r'-'
    TIMES = r'\*'
    DIVIDE = r'/'
    POW = r'\^'

    @_(r'\d+(\.\d+)?')
    def NUMBER(self, t):
        if t.value.isdigit():
            t.value = int(t.value)
        else:
            t.value = float(t.value)
        return t

    # Identifiers and keywords
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    ID['sin'] = SIN
    ID['cos'] = COS
    ID['log'] = LOG
    ID['tan'] = TAN
    ID['exp'] = EXP
    ID['ln'] = LN
    ID['sqrt'] = SQRT
    ID['diff'] = DIFF
    ID['def'] = DEF
