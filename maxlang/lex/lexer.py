from dataclasses import dataclass

from .token_type import TokenType


@dataclass
class Token:
    type_: TokenType
    lexeme: str
    literal: object
    line: int


@dataclass
class Error:
    line: int
    message: str


KEYWORDS = {
    "and": TokenType.AND,
    "class": TokenType.CLASS,
    "else": TokenType.ELSE,
    "false": TokenType.FALSE,
    "for": TokenType.FOR,
    "if": TokenType.IF,
    "in": TokenType.IN,
    "lambda": TokenType.LAMBDA,
    "null": TokenType.NULL,
    "or": TokenType.OR,
    "return": TokenType.RETURN,
    "self": TokenType.SELF,
    "super": TokenType.SUPER,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE,
}


class Lexer:
    def __init__(self, source: str):
        self.source = source

        self.tokens: list[Token] = []
        self.errors: list[Error] = []
        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self) -> list[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(
            Token(
                TokenType.EOF, "", None, self.line
            )
        )
        return self.tokens
    
    def scan_token(self):
        c = self.advance()
        match c:
            case '(':
                self.add_token(TokenType.LEFT_PAREN)
            case ')': 
                self.add_token(TokenType.RIGHT_PAREN)
            case '{': 
                self.add_token(TokenType.LEFT_BRACE)
            case '}': 
                self.add_token(TokenType.RIGHT_BRACE)
            case '[':
                self.add_token(TokenType.LEFT_BRACKET)
            case ']':
                self.add_token(TokenType.RIGHT_BRACKET)
            case ',': 
                self.add_token(TokenType.COMMA)
            case '.': 
                self.add_token(TokenType.DOT)
            case '+':
                if self.match('='):
                    self.add_token(TokenType.PLUS_EQUALS)
                else:
                    self.add_token(TokenType.PLUS)
            case ':': 
                self.add_token(TokenType.COLON)
            case ';': 
                self.add_token(TokenType.SEMICOLON)
            case '*':
                if self.match('='):
                    self.add_token(TokenType.STAR_EQUALS)
                elif self.match('-'):
                    self.errors.append(
                        Error(
                            self.line, "Comment ending without a comment start."
                        )
                    )
                else:
                    self.add_token(TokenType.STAR)

            case '!':
                self.add_token(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
            case '=':
                self.add_token(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
            case '<':
                self.add_token(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)
            case '>':
                self.add_token(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)

            case '-':
                if self.match('='):
                    self.add_token(TokenType.MINUS_EQUALS)
                elif self.match('-'):
                    while self.peek() != '\n' and not self.is_at_end():
                        self.advance()
                elif self.match('*'):
                    while not (self.peek() == '*' and self.peek_next() == '-') and not self.is_at_end():
                        if self.peek() == '\n':
                            self.line += 1
                        self.advance()
                    self.advance()
                    self.advance()
                elif self.match('>'):
                    self.add_token(TokenType.RIGHT_ARROW)
                else:
                    self.add_token(TokenType.MINUS)
            case '/': 
                if self.match('/'):
                    self.add_token(TokenType.DOUBLE_SLASH)
                elif self.match('='):
                    self.add_token(TokenType.SLASH_EQUALS)
                else:
                    self.add_token(TokenType.SLASH)

            case '"' | "'" | "`":
                self.string(c)

            case ' ' | '\r' | '\t':
                pass
            case '\n':
                self.add_token(TokenType.NEWLINE)
                self.line += 1

            case _:
                if c.isdigit():
                    self.number()
                elif c.isalpha():
                    self.identifier()
                else:
                    self.errors.append(
                        Error(
                            self.line, f"Unexpected character '{c}'."
                        )
                    )

    def string(self, delimiter: str):
        while self.peek() != delimiter and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()

        if self.is_at_end():
            self.errors.append(
                Error(
                    self.line, "Unterminated string."
                )
            )

        self.advance()

        value = self.source[self.start+1:self.current-1]
        self.add_token(TokenType.STRING, value)

    def number(self):
        while self.peek().isdigit():
            self.advance()

        token_type = TokenType.INT
        if self.peek() == '.' and self.peek_next().isdigit():
            token_type = TokenType.FLOAT
            self.advance()
            while self.peek().isdigit():
                self.advance()
            value = float(self.source[self.start:self.current])
        else:
            value = int(self.source[self.start:self.current])

        self.add_token(token_type, value)

    def identifier(self):
        while self.peek().isalnum() or self.peek() in "_":
            self.advance()

        value = self.source[self.start:self.current]
        token_type = KEYWORDS.get(value)
        if token_type is None:
            token_type = TokenType.IDENTIFIER

        self.add_token(token_type)


    def match(self, expected: str) -> bool:
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        
        self.current += 1
        return True
            

    def advance(self) -> str:
        char = self.peek()
        self.current += 1
        return char
    
    def peek(self) -> str:
        if self.is_at_end():
            return '\0'
        return self.source[self.current]
    
    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current+1]
    
    def add_token(self, token_type: TokenType, literal: object | None = None):
        lexeme = self.source[self.start:self.current]
        self.tokens.append(
            Token(
                token_type, lexeme, literal, self.line
            )
        )
    
    def is_at_end(self) -> bool:
        return self.current >= len(self.source)