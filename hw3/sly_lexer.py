from sly import Lexer

class MyLexer(Lexer):
    tokens = {NUMBER, LEFT_PAR, RIGHT_PAR, IDENTIFIER, STRING}
    ignore = ' \t'
    ignore_comment = r'\#.*'
    ignore_newline = r'\n+'

    LEFT_PAR = r'\('
    RIGHT_PAR = r'\)'
    NUMBER  = r'\d+'
    STRING = r'".*?"'
    IDENTIFIER = r'[a-zA-Z_][a-zA-Z0-9_]*'

    def error(self, t):
        print('Line %d: Bad character %r' % (self.lineno, t.value[0]))
        self.index += 1