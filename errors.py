from lex import Token


class ParserError(Exception):
    pass


class InterpreterError(Exception):
    def __init__(self, token: Token, message: str):
        super().__init__(message)
        self.token = token
        self.message = message


class InternalError(Exception):
    pass
