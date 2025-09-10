class ASTNode:
    def __init__(self, location):
        self.location = location

class Number(ASTNode):
    def __init__(self, value, location):
        super().__init__(location)
        self.value = int(value)
    def __repr__(self):
        return f"Number({self.value})"

class Float(ASTNode):
    def __init__(self, value, location):
        super().__init__(location)
        self.value = float(value)
    def __repr__(self):
        return f"Float({self.value})"

class String(ASTNode):
    def __init__(self, value, location):
        super().__init__(location)
        self.value = value
    def __repr__(self):
        return f"String({self.value})"

class Array(ASTNode):
    def __init__(self, array, location):
        super().__init__(location)
        self.value = tuple([val.value for val in array])

    def get(self, index): return self.value[index]

    def __repr__(self):
        return f"Array({[val for val in self.value]})"

class BooleanLiteral(ASTNode):
    def __init__(self, value, location):
        super().__init__(location)
        self.value = value
    def __repr__(self):
        return f"Boolean({self.value})"

class NullLiteral(ASTNode):
    def __init__(self, location):
        super().__init__(location)
    def __repr__(self):
        return "Null"

class VarReference(ASTNode):
    def __init__(self, name, location):
        super().__init__(location)
        self.name = name
    def __repr__(self):
        return f"VarRef({self.name})"

class BinaryOp(ASTNode):
    def __init__(self, op, left, right, location):
        super().__init__(location)
        self.op = op
        self.left = left
        self.right = right
    def __repr__(self):
        return f"BinaryOp({self.op}, {self.left}, {self.right})"

class VarDeclaration(ASTNode):
    def __init__(self, name, value, location):
        super().__init__(location)
        self.name = name
        self.value = value
    def __repr__(self):
        return f"VarDecl({self.name}, {self.value})"

class ConstDeclaration(ASTNode):
    def __init__(self, name, value, location):
        super().__init__(location)
        self.name = name
        self.value = value
    def __repr__(self):
        return f"ConstDecl({self.name}, {self.value})"

class Assignment(ASTNode):
    def __init__(self, name, value, location):
        super().__init__(location)
        self.name = name
        self.value = value
    def __repr__(self):
        return f"Assign({self.name}, {self.value})"

class ReturnStatement(ASTNode):
    def __init__(self, value, location):
        super().__init__(location)
        self.value = value
    def __repr__(self):
        return f"Return({self.value})"

class Block(ASTNode):
    def __init__(self, statements, location):
        super().__init__(location)
        self.statements = statements
    def __repr__(self):
        return f"Block({self.statements})"

class IfStatement(ASTNode):
    def __init__(self, condition, then_block, else_block, location):
        super().__init__(location)
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block
    def __repr__(self):
        return f"If({self.condition}, {self.then_block}, {self.else_block})"

class WhileStatement(ASTNode):
    def __init__(self, condition, block, location):
        super().__init__(location)
        self.condition = condition
        self.block = block
    def __repr__(self):
        return f"While({self.condition}, {self.block})"

class ForStatement(ASTNode):
    def __init__(self, init, condition, update, block, location):
        super().__init__(location)
        self.init = init
        self.condition = condition
        self.update = update
        self.block = block
    def __repr__(self):
        return f"For({self.init}, {self.condition}, {self.update}, {self.block})"

class FunctionDeclaration(ASTNode):
    def __init__(self, block, params, name, location):
        super().__init__(location)
        self.block = block
        self.params = params
        self.name = name
    def __repr__(self):
        return f"FunctionDeclaration({self.name} {self.params} {self.block})"

class Parameters(ASTNode):
    def __init__(self, params):
        super().__init__(None)
        self.params = params
    def __repr__(self):
        return f"Parameters({self.params})"

class FunctionCall(ASTNode):
    def __init__(self, name, args, location):
        super().__init__(location)
        self.name = name
        self.args = args
    def __repr__(self):
        return f"FunctionCall({self.name}, args={self.args})"

class MethodCall(ASTNode):
    def __init__(self, obj, method, args, location):
        super().__init__(location)
        self.obj = obj
        self.method = method
        self.args = args
    def __repr__(self):
        return f"MethodCall(obj={self.obj}, method={self.method}, args={self.args})"

class ClassDeclaration(ASTNode):
    def __init__(self, name, methods, location):
        super().__init__(location)
        self.name = name
        self.methods = methods
    def __repr__(self):
        return f"ClassDeclaration(name={self.name}, methods={self.methods})"

class ClassInstance(ASTNode):
    def __init__(self, class_name, args, location):
        super().__init__(location)
        self.class_name = class_name
        self.args = args
    def __repr__(self):
        return f"ClassInstance(class_name={self.class_name} args={self.args})"

class PropertyAccess(ASTNode):
    def __init__(self, obj, prop, location):
        super().__init__(location)
        self.obj = obj
        self.prop = prop
    def __repr__(self):
        return f"PropertyAccess(obj={self.obj}, prop={self.prop})"

class PropertyAssignment(ASTNode):
    def __init__(self, obj, prop, value, location):
        super().__init__(location)
        self.obj = obj
        self.prop = prop
        self.value = value
    def __repr__(self):
        return f"PropertyAssignment(obj={self.obj}, prop={self.prop}, value={self.value})"

class PropertyDeclaration(ASTNode):
    def __init__(self, obj, prop, value, location):
        super().__init__(location)
        self.obj = obj
        self.prop = prop
        self.value = value
    def __repr__(self):
        return f"PropertyDecl(obj={self.obj}, prop={self.prop}, value={self.value})"

class Include(ASTNode):
    def __init__(self, path, location):
        super().__init__(location)
        self.path = path
    def __repr__(self):
        return f'Include(name={self.path})'

class SelectiveInclude(ASTNode):
    def __init__(self, names, path, location):
        super().__init__(location)
        self.names = names
        self.path = path
    def __repr__(self):
        return f'SelectiveInclude(names={self.names}, path={self.path})'

class StructFlag(ASTNode):
    def __init__(self, constructor_name, location):
        super().__init__(location)
        self.constructor_name = constructor_name
    def __repr__(self):
        return f'StructFlag({self.constructor_name})'

class MetadataFlag(ASTNode):
    def __init__(self, key, value, location):
        super().__init__(location)
        self.key = key
        self.value = value
    def __repr__(self):
        return f'MetadataFlag({self.key} = {self.value})'

class PyPlusPlusException(Exception):
    def __init__(self, message, location=None, token=None):
        self.token = token
        self.location = location
        self.message = message
        super().__init__(f'{message}{f"; at char {location[0]}, line {location[1]}, col {location[2]}" if location is not None else ""}')


class SyntaxException(PyPlusPlusException):
    def __init__(self, message, token=None):
        location = (token.position, token.line, token.column) if token is not None else None
        super().__init__('SyntaxError: '+message, location, token)

class RuntimeException(PyPlusPlusException):
    def __init__(self, message, token=None):
        location = (token.position, token.line, token.column) if token is not None else None
        super().__init__('RuntimeError: '+message, location, token)

class NameException(RuntimeException):
    def __init__(self, message, token=None):
        super().__init__('NameError: '+message, token)

class TypeException(RuntimeException):
    def __init__(self, message, token=None):
        super().__init__('TypeError: '+message, token)

class AttrException(RuntimeException):
    def __init__(self, message, token=None):
        super().__init__('AttributeError: '+message, token)

class FileNotFoundException(RuntimeException):
    def __init__(self, message, token=None):
        super().__init__('FileNotFoundError: '+message, token)

class ImportException(RuntimeException):
    def __init__(self, message, token=None):
        super().__init__('ImportError: '+message, token)

class ValueException(RuntimeException):
    def __init__(self, message, token=None):
        super().__init__('ValueError: '+message, token)

class ZeroDivisionException(RuntimeException):
    def __init__(self, message, token=None):
        super().__init__('ZeroDivisionError: '+message, token)





