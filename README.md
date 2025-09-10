# Pypp 🐍➕➕

A **toy programming language & interpreter** written in **Python**, inspired by high-level language concepts.  
The name **Py++** is just a fun play on “C++”, but under the hood everything is pure Python.

This project is a learning experiment in building interpreters from scratch. It currently supports a minimal but growing set of language features such as expressions, runtime evaluation, and AST (Abstract Syntax Tree) parsing.

---

## ✨ Features

- 🧩 **AST (Abstract Syntax Tree)** implementation (`AST.py`, `ASTNodes.py`)  
- ⚡ **Interpreter** for evaluating custom `.py++` programs  
- 🛠️ **Runtime system** with basic execution logic (`Runtime.py`)  
- 📦 **Standard library functions** (`standard.py`)  
- 📝 Example program file (`program.py++`)  

---

## 🚀 Getting Started

### 1. Clone the repo
```
git clone https://github.com/RanveerisdeGOAT/Pypp.git
cd Pypp
```

### 2. Create a program
Eg.
`stdout("Hello from Py++!")`

### 3. Run the program
`python interpreter.py program.py++`

## Example
```car.py++
include 'standard'

class Car{
    define $struct(name, price, brand){
        let this.name = name
        let this.price = price
        let this.brand = brand
    }

    define start(){
        stdout('VROOM!', this.name)
    }

}
```

## Contributing

Contributions are welcome!  Please feel free to submit pull requests or open issues.

---

<br>
MyDE 2025<br>
Author: @RanveerisdeGOAT,<br>
Co-Authors: Deepseek, Gemini, ChatGPT ;)<br>
Open source: Free to use, modify and improve: https://github.com/RanveerisdeGOAT?tab=repositories


