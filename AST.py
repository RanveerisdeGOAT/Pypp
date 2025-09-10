import re
from ASTNodes import *

class Token:
    def __init__(self, type_, value, position, line, column):
        self.type, self.value, self.position, self.line, self.column = type_, value, position, line, column

    def __repr__(self):
        return f"Token({self.type}, '{self.value}', pos={self.position}, line={self.line}, col={self.column})"

class Lexer:
    TOKEN_SPEC = [
        ('STRING', r'"([^"\\]|\\.)*"|\'([^\'\\]|\\.)*\''),
        ('FLOAT', '[\+-]?(\d+\.\d+)'),
        ('NUMBER', r'[\+-]?\d+'),
        ('ID', r'[A-Za-z_$]\w*'),
        ('OP', r'==|!=|<=|>=|\+\+|--|\+=|-=|\*=|/=|\+|-|\*|/|%|=|<|>|\||&|!|,'),
        ('SEMI', r';'),
        ('COLON', r':'),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('LBRACE', r'\{'),
        ('RBRACE', r'\}'),
        ('LSQUARE', r'\['),
        ('RSQUARE', r'\]'),
        ('DOT', r'\.'),
        ('NEWLINE', r'\n'),
        ('WHITESPACE', r'[ \t]+'),
        ('COMMENT', r'//[^\n]*'),
    ]
    KEYWORDS = {'return', 'let', 'const', 'true', 'false', 'define', 'null', 'if', 'else', 'while', 'for', 'class', 'new', 'include'}

    def __init__(self, code):
        self.code = code

    def tokenize(self):
        tokens, line, line_start, last_pos = [], 1, 0, 0
        pattern = '|'.join(f'(?P<{name}>{regex})' for name, regex in self.TOKEN_SPEC)
        for match in re.finditer(pattern, self.code):
            kind, value, position = match.lastgroup, match.group(), match.start()
            last_pos = position
            column = position - line_start + 1
            if kind == 'NEWLINE':
                line += 1
                line_start = match.end()
                continue
            elif kind in ('WHITESPACE', 'COMMENT'):
                continue
            if kind == 'STRING':
                value = value[1:-1]
            token_type = value.upper() if kind == 'ID' and value in self.KEYWORDS else kind
            tokens.append(Token(token_type, value, position, line, column))
        tokens.append(Token('EOF', 'EOF', last_pos, line, 1))
        return tokens


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, type_=None, value=None):
        token = self.current()
        if token and (type_ is None or token.type == type_) and (value is None or token.value == value):
            self.pos += 1
            return token
        raise SyntaxException(f"Expected {type_}, got '{token.value}'", token)

    def last(self):
        return self.tokens[self.pos-1] if self.pos > 0 else None

    def parse(self):
        statements = []
        while self.current() and self.current().type != 'EOF':
            stmt = self.statement()
            if stmt is not None:
                statements.append(stmt)
            if __name__ == '__main__':
                print(stmt)
        return statements

    def statement(self):
        tok = self.current()
        if tok.type == 'LET': return self.var_declaration()
        if tok.type == 'CONST': return self.const_declaration()
        if tok.type == 'RETURN': return self.return_statement()
        if tok.type == 'DEFINE': return self.function_declaration()
        if tok.type == 'IF': return self.if_statement()
        if tok.type == 'WHILE': return self.while_statement()
        if tok.type == 'FOR': return self.for_statement()
        if tok.type == 'CLASS': return self.class_declaration()
        if tok.type == 'INCLUDE': return self.include()
        if tok.type == 'ID' and tok.value.startswith('$'): return self.handle_flag()
        if tok.type == 'EOF': self.eat('EOF'); return
        stmt = self.expr()
        if self.current() and self.current().type == 'SEMI': self.eat('SEMI')
        return stmt

    def if_statement(self):
        self.eat('IF'); self.eat('LPAREN'); condition = self.expr(); self.eat('RPAREN')
        then_block = self.block()
        else_block = None
        if self.current() and self.current().type == 'ELSE':
            self.eat('ELSE'); else_block = self.block()
        return IfStatement(condition, then_block, else_block, self.last())

    def var_declaration(self):
        self.eat('LET')
        target = self.member_expression()
        self.eat('OP', '=')
        value = self.expr()
        if isinstance(target, VarReference):
            return VarDeclaration(target.name, value, self.last())
        if isinstance(target, PropertyAccess):
            return PropertyDeclaration(target.obj, target.prop, value, self.last())
        raise SyntaxException("Invalid target for variable declaration.", self.last())

    def const_declaration(self):
        self.eat('CONST')
        name = self.eat('ID').value
        self.eat('OP', '=')
        value = self.expr()
        return ConstDeclaration(name, value, self.last())

    def function_declaration(self):
        self.eat('DEFINE')
        name = self.eat('ID').value
        params = Parameters(self.collection())
        block = self.block()
        return FunctionDeclaration(block, params, name, self.last())

    def return_statement(self):
        self.eat('RETURN')
        return ReturnStatement(self.expr(), self.last())

    def while_statement(self):
        self.eat('WHILE')
        self.eat('LPAREN')
        condition = self.expr()
        self.eat('RPAREN')
        return WhileStatement(condition, self.block(), self.last())

    def for_statement(self):
        self.eat('FOR')
        self.eat('LPAREN')
        init = self.statement() if self.current().type != 'COLON' else None
        self.eat('COLON')
        condition = self.expr() if self.current().type != 'COLON' else None
        self.eat('COLON')
        update = self.expr() if self.current().type != 'RPAREN' else None
        self.eat('RPAREN')
        return ForStatement(init, condition, update, self.block(), self.last())

    def class_declaration(self):
        self.eat('CLASS')
        name = self.eat('ID').value
        self.eat('LBRACE')
        methods = []
        while self.current().type != 'RBRACE':
            self.eat('DEFINE')
            method_name = self.eat('ID').value
            params = Parameters(self.collection())
            body = self.block()
            methods.append(FunctionDeclaration(body, params, method_name, self.last()))
        self.eat('RBRACE')
        return ClassDeclaration(name, methods, self.last())

    def include(self):
        self.eat('INCLUDE')
        path = self.eat('STRING').value
        return Include(path, self.last())

    def handle_flag(self):
        flag_name = self.eat('ID').value
        self.eat('OP', '=')
        if flag_name == '$include':
            self.eat('LPAREN')
            names = []
            while self.current().type == 'STRING':
                names.append(self.eat('STRING').value)
                if self.current() and self.current().value == ',':
                    self.eat('OP', ',')
            self.eat('RPAREN')
            return MetadataFlag('include', names, self.last())
        elif flag_name == '$name':
            return MetadataFlag('filename', self.eat('STRING').value, self.last())
        else:
            return MetadataFlag(flag_name[1:], self.expr(), self.last())

    def block(self):
        self.eat('LBRACE')
        statements = []
        while self.current().type != 'RBRACE':
            statements.append(self.statement())
        self.eat('RBRACE')
        return Block(statements, self.last())

    def collection(self, type='PAREN'):
        self.eat('L'+type)
        items = []
        if self.current().type != 'R'+type:
            items.append(self.expr())
            while self.current().type == 'OP' and self.current().value == ',':
                self.eat('OP', ',')
                items.append(self.expr())
        self.eat('R'+type)
        return items

    def expr(self):
        node = self.member_expression()

        if self.current() and self.current().type == 'OP':
            while self.current() and self.current().type == 'OP':
                op = self.current().value

                if op in ('+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>='):
                    self.eat('OP')
                    right = self.expr()
                    node = BinaryOp(op, node, right, self.last())

                elif op == '=':
                    self.eat('OP')
                    right = self.expr()
                    node = self.assignment(node, right)

                elif op == '++':
                    self.eat('OP')
                    node = self.assignment(node, BinaryOp('+', node, Number(1, self.last()), self.last()))

                elif op == '--':
                    self.eat('OP')
                    node = self.assignment(node, BinaryOp('-', node, Number(1, self.last()), self.last()))

                elif op == '+=':
                    self.eat('OP')
                    right = self.expr()
                    node = self.assignment(node, BinaryOp('+', node, right, self.last()))
                elif op == '-=':
                    self.eat('OP')
                    right = self.expr()
                    node = self.assignment(node, BinaryOp('-', node, right, self.last()))
                elif op == '*=':
                    self.eat('OP')
                    right = self.expr()
                    node = self.assignment(node, BinaryOp('*', node, right, self.last()))
                elif op == '/=':
                    self.eat('OP')
                    right = self.expr()
                    node = self.assignment(node, BinaryOp('/', node, right, self.last()))

                else:
                    break
        elif self.current() and self.current().type == 'LPAREN':
            return self.call_expression(node)

        return node

    def assignment(self, node, value):
        if isinstance(node, VarReference):
            return Assignment(node.name, value, self.last())

        elif isinstance(node, PropertyAccess):
            return PropertyAssignment(node.obj, node.prop, value, self.last())

        else:
            raise SyntaxException("Assignments can only be use on variables or properties", self.last())

    def call_expression(self, node):
        node = node
        while self.current() and self.current().type == 'LPAREN':
            args = self.collection()
            if isinstance(node, PropertyAccess):
                node = MethodCall(node.obj, node.prop, args, self.last())
            elif isinstance(node, VarReference):
                node = FunctionCall(node.name, args, self.last())
            else:
                raise SyntaxException("Expression is not callable.", self.last())
        return node

    def member_expression(self):
        node = self.primary_expression()
        while self.current() and self.current().type == 'DOT':
            self.eat('DOT')
            prop = self.eat('ID').value
            node = PropertyAccess(node, prop, self.last())
        return node

    def primary_expression(self):
        tok = self.current()
        if tok.type == 'NUMBER':
            return Number(self.eat('NUMBER').value, self.last())
        if tok.type == 'FLOAT':
            return Float(self.eat('FLOAT').value, self.last())
        if tok.type == 'STRING':
            return String(self.eat('STRING').value, self.last())
        if tok.type == 'LSQUARE':
            return Array(tuple(self.collection('SQUARE')), self.last())
        if tok.type == 'TRUE':
            self.eat('TRUE')
            return BooleanLiteral(True, self.last())
        if tok.type == 'FALSE':
            self.eat('FALSE')
            return BooleanLiteral(False, self.last())
        if tok.type == 'NULL':
            self.eat('NULL')
            return NullLiteral(self.last())
        if tok.type == 'ID':
            return VarReference(self.eat('ID').value, self.last())
        if tok.type == 'NEW':
            self.eat('NEW')
            name = self.eat('ID').value
            return ClassInstance(name, self.collection(), self.last())
        if tok.type == 'LPAREN':
            self.eat('LPAREN')
            expr = self.expr()
            self.eat('RPAREN')
            return expr
        raise SyntaxException(f"Unexpected literal: {tok.value}", tok)

def to_ast(code):
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()



# Example usage:
if __name__ == "__main__":
    code = open('program.py++', 'r').read()
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    print(tokens)
    parser = Parser(tokens)
    ast = parser.parse()
    a = 1.1

