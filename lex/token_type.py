from enum import StrEnum


class TokenType(StrEnum):
    # Single-character tokens.
    LEFT_PAREN = "LEFT_PAREN"
    RIGHT_PAREN = "RIGHT_PAREN"
    LEFT_BRACE = "LEFT_BRACE"
    RIGHT_BRACE = "RIGHT_BRACE"
    LEFT_BRACKET = "LEFT_BRACKET"
    RIGHT_BRACKET = "RIGHT_BRACKET"
    COMMA = "COMMA"
    DOT = "DOT"
    MINUS = "MINUS"
    PLUS = "PLUS"
    COLON = "COLON"
    SEMICOLON = "SEMICOLON"
    SLASH = "SLASH"
    DOUBLE_SLASH = "DOUBLE_SLASH"
    STAR = "STAR"
    NEWLINE = "NEWLINE"
    
    # One or two character tokens.
    BANG = "BANG"
    BANG_EQUAL = "BANG_EQUAL"
    EQUAL = "EQUAL"
    EQUAL_EQUAL = "EQUAL_EQUAL"
    GREATER = "GREATER"
    GREATER_EQUAL = "GREATER_EQUAL"
    LESS = "LESS"
    LESS_EQUAL = "LESS_EQUAL"
    RIGHT_ARROW = "RIGHT_ARROW"
    
    # Literals
    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    INT = "INT"
    FLOAT = "FLOAT"
    
    # Keywords
    AND = "AND"
    CLASS = "CLASS"
    ELSE = "ELSE"
    FALSE = "FALSE"
    FOR = "FOR"
    IF = "IF"
    IN = "IN"
    LAMBDA = "LAMBDA"
    NULL = "NULL"
    OR = "OR"
    RETURN = "RETURN"
    SELF = "SELF"
    SUPER = "SUPER"
    TRUE = "TRUE"
    VAR = "VAR"
    WHILE = "WHILE"
    
    EOF = "EOF"
