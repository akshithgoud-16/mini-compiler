# FlowLang Mini Compiler

This project demonstrates a simple compiler pipeline for the FlowLang DSL:

1. Lexical analysis
2. Recursive descent parsing
3. Semantic analysis
4. Three-address code generation
5. Constant folding optimization
6. Pseudo assembly and Python code generation

## Example

```text
x -> 10
y -> 20
folded -> 10 + 20
z -> x + y
when z > 15:
say z
```

## Run

```bash
python main.py
```

You can also provide a file path or inline source:

```bash
python main.py program.flow
python main.py --source "x -> 10\nsay x\n"
```
