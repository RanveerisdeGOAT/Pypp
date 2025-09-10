import sys
from tkinter import filedialog
import AST
from ASTNodes import *
from Runtime import interpret

def interpret_file(file):
    with open(file, 'r') as f:
        try:
            code = f.read()
            ast = AST.to_ast(code)
            interpreter = interpret(ast)
            return interpreter
        except SyntaxException as e:
            if e.location is not None:
                print('\033[31m'+code.split('\n')[e.location[1]-1])
                print('\033[31m' + f'{" " * (e.location[2]-1)}{len(e.token.value)*"^"}')
            print(e)
            sys.exit(1)
        except RuntimeException as e:
            if e.location is not None:
                print('\033[31m'+code.split('\n')[e.location[1]-1])
                print('\033[31m' + f'{" " * (e.location[2]-1)}{len(e.token.value)*"^"}')
            print(e)
            sys.exit(1)

if __name__ == '__main__':
    interpret_file('program.py++')
