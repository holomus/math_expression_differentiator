from sly import Lexer


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

    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value)
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
