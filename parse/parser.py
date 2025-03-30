from typing import Callable

from lex import Token
from lex import TokenType
from .expressions import Expression, Binary, Unary, Literal, Grouping, Variable, Assignment, Logical, Call, Lambda, Get, Set, Self, Super, Parameter, Pair
from .statements import Statement, Print, ExpressionStatement, VariableStatement, Block, IfStatement, WhileStatement, Function, ReturnStatement, Class, ForStatement
from errors import ParserError


class ParserControl:
    def __init__(self, tokens: list[Token], error_callback: Callable[[Token, str], None]):
        self.tokens = tokens
        self.error_callback = error_callback

        self.current = 0
    
    def match(self, *token_types: TokenType) -> bool:
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
            
        return False
    
    def check(self, token_type: TokenType) -> bool:
        if self.is_at_end():
            return False
        
        return self.peek().type_ == token_type
    
    def check_next(self, token_type: TokenType) -> bool:
        if self.is_at_end() or self.peek_next().type_ == TokenType.EOF:
            return False
        
        return self.peek_next().type_ == token_type
    
    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def is_at_end(self) -> bool:
        return self.peek().type_ == TokenType.EOF
    
    def peek(self) -> Token:
        return self.tokens[self.current]
    
    def peek_next(self) -> Token:
        return self.tokens[self.current+1]

    def previous(self) -> Token:
        return self.tokens[self.current-1]
    
    def consume(self, token_type: TokenType, message: str) -> Token:
        if self.check(token_type):
            return self.advance()
        
        raise self.error(self.peek(), message)
    
    def error(self, token: Token, message: str):
        self.error_callback(token, message)
        return ParserError(message)
    
    def synchronize(self):
        self.advance()

        while not self.is_at_end():
            if self.previous().type_ == TokenType.SEMICOLON:
                return
            
            if self.peek().type_ in (
                TokenType.CLASS,
                TokenType.LAMBDA,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN,
            ):
                return
            
            self.advance()


class ExpressionsParser(ParserControl):
    def expression(self) -> Expression:
        return self.assignment()
    
    def assignment(self) -> Expression:
        expression = self.or_expression()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expression, Variable):
                name = expression.name
                return Assignment(name, value)
            elif isinstance(expression, Get):
                return Set(expression.obj, expression.name, value)
            
            self.error(equals, "Invalid assignment target.")

        return expression
    
    def or_expression(self) -> Expression:
        expression = self.and_expression()

        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.and_expression()
            expression = Logical(expression, operator, right)

        return expression
    
    def and_expression(self) -> Expression:
        expression = self.equality()

        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expression = Logical(expression, operator, right)

        return expression
    
    def equality(self) -> Expression:
        expression = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expression = Binary(expression, operator, right)

        return expression
    
    def comparison(self) -> Expression:
        expression = self.pair()

        while self.match(
            TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL
        ):
            operator = self.previous()
            right = self.pair()
            expression = Binary(expression, operator, right)

        return expression
    
    def pair(self) -> Expression:
        expression = self.term()
        
        while self.match(TokenType.RIGHT_ARROW):
            operator = self.previous()
            right = self.term()
            expression = Pair(expression, operator, right)

        return expression
    
    def term(self) -> Expression:
        expression = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expression = Binary(expression, operator, right)

        return expression
    
    def factor(self) -> Expression:
        expression = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expression = Binary(expression, operator, right)

        return expression
    
    def unary(self) -> Expression:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        
        return self.call()
    
    def call(self) -> Expression:
        expression = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expression = self.finish_call(expression)
            elif self.match(TokenType.DOT):
                name = self.consume(TokenType.IDENTIFIER, "EXpect property name after '.'.")
                expression = Get(expression, name)
            else:
                break

        return expression
    
    def primary(self) -> Expression:
        if self.match(TokenType.FALSE):
            return Literal(False)
        if self.match(TokenType.TRUE):
            return Literal(True)
        if self.match(TokenType.NIL):
            return Literal(None)
        
        if self.match(TokenType.SUPER):
            keyword = self.previous()
            method = None
            if self.match(TokenType.DOT):
                method = self.consume(TokenType.IDENTIFIER, "Expect superclass method name.")
            return Super(keyword, method)
        
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)
        
        if self.match(TokenType.SELF):
            return Self(self.previous())
        
        if self.match(TokenType.LAMBDA):
            return self.function_body("lambda")
        
        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())
        
        if self.match(TokenType.LEFT_PAREN):
            expression = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expression)
        
        raise self.error(self.peek(), "Expect expression.")
    
    def finish_call(self, expression: Expression):
        arguments: list[Expression] = []

        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                arguments.append(self.expression())
                if not self.match(TokenType.COMMA):
                    break

        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        return Call(expression, paren, arguments)
    
    def function_body(self, kind: str):
        parameters: list[Parameter] = []
        if self.match(TokenType.COLON):
            has_had_default = False
            while True:
                type_ = self.consume(TokenType.IDENTIFIER, "Expect type.")
                name = self.consume(TokenType.IDENTIFIER, "Expect parameter name.")
                default = None
                if self.match(TokenType.EQUAL):
                    default = self.expression()
                    has_had_default = True

                if has_had_default and default is None:
                    raise self.error(name, "Cannot set a parameter without a default value after a parameter with a default value.")

                parameters.append(Parameter(type_, name, default))
                if not self.match(TokenType.COMMA):
                    break

        self.consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body = self.block()
        return Lambda(parameters, body)
    

class StatementsParser(ExpressionsParser):
    def declaration(self) -> Statement:
        try:
            if self.match(TokenType.CLASS):
                return self.class_declaration()
            if self.check(TokenType.IDENTIFIER) and (
                self.check_next(TokenType.LEFT_BRACE) or self.check_next(TokenType.COLON)
            ):
                return self.function("function")
            
            return self.statement()
        except ParserError:
            self.synchronize()

    def class_declaration(self) -> Class:
        name = self.consume(TokenType.IDENTIFIER, "Expect class name.")

        superclasses: list[Variable] = []
        if self.match(TokenType.COLON):
            while True:
                self.consume(TokenType.IDENTIFIER, "Expect superclass name.")
                superclasses.append(
                    Variable(self.previous())
                )
                if not self.match(TokenType.COMMA):
                    break

        self.consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")

        methods: list[Function] = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            methods.append(self.function("method"))

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")

        return Class(name, superclasses, methods)

    def function(self, kind: str) -> Function:
        name = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        return Function(name, self.function_body(kind))

    def var_declaration(self) -> Statement:
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        
        initializer: Expression | None = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaraction.")
        return VariableStatement(name, initializer)

    def statement(self) -> Statement:
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.RETURN):
            return self.return_statement()
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.LEFT_BRACE):
            return Block(self.block())
        if self.match(TokenType.IF):
            return self.if_statement()
        
        return self.expression_statement()
    
    def print_statement(self) -> Statement:
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)
    
    def return_statement(self) -> Statement:
        keyword = self.previous()
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return ReturnStatement(keyword, value)
    
    def for_statement(self) -> Statement:
        for_name = self.inline_var_declaration()
        self.consume(TokenType.IN, "Expect 'in' after variable name in for-loop.")
        in_name = self.expression()
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before for-loop body.")
        body = self.block()

        return ForStatement(for_name, in_name, body)
    
    def inline_var_declaration(self) -> Statement:
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        return VariableStatement(name, None)

    def while_statement(self) -> Statement:
        condition = self.expression()
        body = self.statement()

        return WhileStatement(condition, body)
    
    def block(self) -> list[Statement]:
        statements: list[Statement] = []

        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements
    
    def if_statement(self) -> Statement:
        condition = self.expression()

        then_branch = self.statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()

        return IfStatement(
            condition, then_branch, else_branch
        )
    
    def expression_statement(self) -> Statement:
        expression = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return ExpressionStatement(expression)
    

class Parser(StatementsParser):
    def parse(self) -> list[Statement]:
        statements: list[Statement] = []
        while not self.is_at_end():
            statements.append(self.declaration())
            
        return statements
        