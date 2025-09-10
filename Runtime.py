from ASTNodes import *
from types import FunctionType

class ReturnValue(Exception):
    def __init__(self, value): self.value = value

class Environment:
    def __init__(self, parent=None):
        self.vars, self.parent = {}, parent
    def declare(self, name, value, node, is_constant=False):
        if name in self.vars: raise NameException(f"Variable '{name}' already declared.", node.location)
        self.vars[name] = (value, is_constant); return value

    def assign(self, name, value, node):
        if name in self.vars:
            _, is_const = self.vars[name]
            if is_const: raise TypeException(f"Cannot assign to constant '{name.value}'.", node.location)
            self.vars[name] = (value, is_const); return value
        if self.parent: return self.parent.assign(name, value)
        raise NameException(f"Variable '{name}' is not defined.", node.location)

    def lookup(self, name, node):
        if name in self.vars: return self.vars[name][0]
        if self.parent: return self.parent.lookup(name, node)
        raise NameException(f"Variable '{name}' is not defined.", node.location)

    def __add__(self, other):
        merged = Environment()
        merged.vars = {**self.vars, **other.vars}
        return merged

class UserDefinedFunction:
    def __init__(self, declaration, closure): self.declaration, self.closure = declaration, closure
    def __repr__(self): return f"<function {self.declaration.name}>"

class ClassObject:
    def __init__(self, name, methods):
        self.name = name; self.methods = {m.name: m for m in methods}

    def instantiate(self, interpreter, args, node):
        instance = InstanceObject(self, interpreter.environment, node)
        constructor = self.methods.get("$struct")
        if constructor:
            # Bind the constructor method to the new instance and execute it
            bound_constructor = UserDefinedFunction(constructor, instance.env)
            interpreter.execute_function(bound_constructor, args, node, self_env=instance.env)
        return instance

    def __repr__(self): return f"<class {self.name}>"

class InstanceObject:
    def __init__(self, klass, parent_env, node):
        self.klass = klass; self.env = Environment(parent=parent_env)
        self.env.declare("this", self, node.location, is_constant=True)

    def get_method(self, name, node):
        method = self.klass.methods.get(name)
        if not method: raise AttrException(f"'{self.klass.name}' has no method '{name}'", node.location)
        # Return a function bound to this instance's environment
        return UserDefinedFunction(method, self.env)
    def __repr__(self): return f"<{self.klass.name} instance>"

class Interpreter:
    def __init__(self):
        self.environment = Environment()

    def interpret(self, ast_nodes):
        result = None
        for node in ast_nodes: result = self.visit(node)
        return result, self.environment

    def visit(self, node, **kwargs):
        method_name = f"visit_{type(node).__name__}"; visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node, **kwargs)

    def generic_visit(self, node, **kwargs): raise NotImplementedError(f"No visitor for {type(node).__name__}")

    def visit_NoneType(self, node, **kwargs): return

    def visit_Number(self, node, **kwargs): return node.value

    def visit_String(self, node, **kwargs): return node.value

    def visit_Float(self, node, **kwargs): return node.value

    def visit_Array(self, node, **kwargs): return node.value

    def visit_BooleanLiteral(self, node, **kwargs): return node.value

    def visit_NullLiteral(self, node, **kwargs): return None

    def visit_VarReference(self, node, **kwargs): return self.environment.lookup(node.name, node)

    def visit_BinaryOp(self, node, **kwargs):
        a, b = self.visit(node.left), self.visit(node.right)
        op = node.op
        location = node.location

        def safe_op(func):
            try:
                if func(a, b) == 'undefined': raise ZeroDivisionError
                return func(a, b)
            except Exception:
                raise TypeException(f"The expression '{a.__repr__()} {op} {b.__repr__()}' is not possible", location)

        ops = {
            "+": lambda x, y: x + y,
            "-": lambda x, y: x - y,
            "*": lambda x, y: x * y,
            "/": lambda x, y: (x / y if y != 0 else float('inf')) if y != 0 and x != 0 else 'undefined',
            ">": lambda x, y: x > y,
            "<": lambda x, y: x < y,
            "==": lambda x, y: x == y,
            "!=": lambda x, y: x != y,
            "<=": lambda x, y: x <= y,
            ">=": lambda x, y: x >= y,
        }

        if op not in ops:
            raise TypeException(f"Unknown operator '{op}'", location)

        return safe_op(ops[op])

    def visit_Include(self, node, **kwargs):
        import os

        if node.path.endswith('.py++'):
            # Handle custom py++ file
            from interpreter import interpret_file  # You must define this
            file = node.path
            if not os.path.exists(file):
                raise FileNotFoundException(f"Included file '{file}' not found.", node.location)
            _, env = interpret_file(file)
            self.environment += env  # merge included env
            return


        elif node.path.endswith('.py'):
            import importlib

            module_path = node.path.replace('.py', '').replace('/', '.').replace('\\', '.')
            try:
                mod = importlib.import_module(module_path)
            except ImportError as e:
                raise ImportException(f"Could not import Python module '{module_path}': {e}", node.location)
            if hasattr(mod, '__include__') and isinstance(mod.__include__, dict):

                for name, value in mod.__include__.items():
                    self.environment.declare(name, value, node, is_constant=True)
            else:
                for name in dir(mod):
                    if not name.startswith('_'):
                        value = getattr(mod, name)
                        self.environment.declare(name, value, node, is_constant=True)

        else:
            try:
                return self.visit_Include(Include(node.path+'.py++', node.location), **kwargs)
            except:
                try:
                    return self.visit_Include(Include(node.path+'.py', node.location), **kwargs)
                except:
                    try:
                        return self.visit_Include(Include(node.path, node.location), **kwargs)
                    except:
                        raise ValueException(f"Unsupported include path: {node.path}", node.location)

    def visit_VarDeclaration(self, node, **kwargs):
        return self.environment.declare(node.name, self.visit(node.value), node,False)

    def visit_ConstDeclaration(self, node, **kwargs):
        return self.environment.declare(node.name, self.visit(node.value), node,True)

    def visit_Assignment(self, node, **kwargs):
        return self.environment.assign(node.name, self.visit(node.value), node)

    def visit_Block(self, node, create_new_scope=True, **kwargs):
        if create_new_scope: self.environment = Environment(parent=self.environment)
        try:
            for stmt in node.statements: self.visit(stmt)
        finally:
            if create_new_scope: self.environment = self.environment.parent
    def visit_IfStatement(self, node, **kwargs):
        if self.visit(node.condition): return self.visit(node.then_block)
        elif node.else_block: return self.visit(node.else_block)

    def visit_WhileStatement(self, node, **kwargs):
        while self.visit(node.condition): self.visit(node.block)

    def visit_ForStatement(self, node, **kwargs):
        if node.init: self.visit(node.init)
        while True:
            if node.condition and not self.visit(node.condition): break
            self.visit(node.block)
            if node.update: self.visit(node.update)
    def visit_FunctionDeclaration(self, node, **kwargs):
        return self.environment.declare(node.name, UserDefinedFunction(node, self.environment), True)

    def visit_FunctionCall(self, node, **kwargs):
        callee = self.environment.lookup(node.name, node); args = [self.visit(arg) for arg in node.args]
        if isinstance(callee, UserDefinedFunction): return self.execute_function(callee, args, node)
        if isinstance(callee, ClassObject): return callee.instantiate(self, args, node)
        if isinstance(callee, FunctionType): return callee(*args)
        if callable(callee): return callee(*args)
        raise TypeException(f"'{node.name}' is not callable", node.location)

    def execute_function(self, user_func, args, node, self_env=None):
        func_decl, func_env = user_func.declaration, Environment(parent=self_env or user_func.closure)
        if self_env: func_env.declare("this", self_env.lookup("this", node), node, is_constant=True)
        for param, arg in zip(func_decl.params.params, args): func_env.declare(param.name, node, arg)
        prev_env = self.environment; self.environment = func_env
        try:
            self.visit(func_decl.block, create_new_scope=False)
        except ReturnValue as rv: return rv.value
        finally: self.environment = prev_env

    def visit_ReturnStatement(self, node, **kwargs): raise ReturnValue(self.visit(node.value))

    def visit_ClassDeclaration(self, node, **kwargs):
        self.environment.declare(node.name, ClassObject(node.name, node.methods), True)

    def visit_ClassInstance(self, node, **kwargs):
        klass = self.environment.lookup(node.class_name, node)
        args = [self.visit(arg) for arg in node.args]

        if isinstance(klass, ClassObject):
            return klass.instantiate(self, args, node)

        elif isinstance(klass, type):  # native Python class
            return klass(*args)

        raise TypeError(f"'{node.class_name}' is not a class")

    def visit_MethodCall(self, node, **kwargs):
        instance = self.visit(node.obj)
        if not isinstance(instance, InstanceObject):
            method = getattr(instance, node.method, None)
            args = [self.visit(arg) for arg in node.args]
            if node.method == '$get':
                try:
                    return instance[args[0]]
                except:
                    raise TypeException(f"'{node.method}' is not a method of {type(instance).__name__}", node.location)

            if not callable(method):
                raise TypeException(f"'{node.method}' is not a method of {type(instance).__name__}", node.location)
            return method(*args)

        method = instance.get_method(node.method, node)
        args = [self.visit(arg) for arg in node.args]
        return self.execute_function(method, args, node, self_env=instance.env)

    def visit_PropertyAccess(self, node, **kwargs):
        instance = self.visit(node.obj)
        if not isinstance(instance, InstanceObject):
            prop = getattr(instance, node.prop, None)
            if prop is None:
                raise TypeException(f"'{node.prop}' is not a property of {type(instance).__name__}", node.location)
            return prop
        return instance.env.lookup(node.prop, node)

    def visit_PropertyAssignment(self, node, **kwargs):
        instance = self.visit(node.obj)
        if not isinstance(instance, InstanceObject): raise TypeException(f"Cannot set property on a non-object.", node.location)
        return instance.env.assign(node.prop, self.visit(node.value), node)

    def visit_PropertyDeclaration(self, node, **kwargs):
        instance = self.visit(node.obj)
        if not isinstance(instance, InstanceObject): raise TypeException(f"Cannot declare property on a non-object.", node.location)
        return instance.env.declare(node.prop, self.visit(node.value), node)


def interpret(ast):
    return Interpreter().interpret(ast)
