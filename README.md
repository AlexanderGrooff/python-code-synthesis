[![PyPI version](https://badge.fury.io/py/evalo.svg)](https://pypi.org/project/evalo/)
# Python code synthesis

This project is used to interpret Python code and generate Python code based on given values.

This project is heavily influenced by [Barliman](https://github.com/webyrd/Barliman), which implemented
this exact idea for Scheme. While Barliman works wonders, I don't think Scheme is a programming
language that is widely used in production environments. This is the reason I created this
project, so that the principle of Barliman could be applied to Python.


## Examples
This project can do both interpreting from Python code to values and vica versa. For example, AST
values will be converted to the correct interpreted values:

```
> from evalo import *
> x = var()
> run(1, x, eval_expro(ast.BinOp(left=ast.Num(n=1), op=ast.Add(), right=ast.Num(n=1)), [], x))

(2,)
```

Interpreting from values to Python code will generate AST objects, which can be directly translated
to Python code using external libraries. For example, if we want 5 different versions of Python code
that are interpreted to the value `2`, we can do the following:

```
> from evalo import *
> x = var()
> run(5, x, eval_expro(x, [], 2))

(<_ast.Num at 0x7fdf44aabe48>,
 <_ast.BinOp at 0x7fdf44a87fd0>,
 <_ast.BinOp at 0x7fdf44a1d320>,
 <_ast.BinOp at 0x7fdf44a444e0>,
 <_ast.BinOp at 0x7fdf46ee36a0>)
```

To translate this to human-readable values, we can use `ast_dump_if_possible`:
```
> [ast_dump_if_possible(y) for y in run(5, x, eval_expro(x, [], 2, maxdepth=3))]

['Num(n=2)',
 'BinOp(left=Num(n=0), op=Add(), right=Num(n=2))',
 'BinOp(left=Num(n=0), op=Sub(), right=BinOp(left=Num(n=0), op=Sub(), right=Num(n=2)))',
 'BinOp(left=Num(n=1), op=Mult(), right=Num(n=2))',
 'BinOp(left=BinOp(left=Num(n=0), op=Add(), right=Num(n=0)), op=Add(), right=Num(n=2))']
```

Using the [astunparse](https://github.com/simonpercivall/astunparse) library we can directly translate this output to Python source code:

```
> [astunparse.unparse(y).strip() for y in run(10, x, eval_expro(x, [], 2, maxdepth=3))]

['2',
 '(0 + 2)',
 '(0 - (0 - 2))',
 '(1 * 2)',
 '((0 + 0) + 2)',
 '((0 + 0) - (0 - 2))',
 '((1 + 0) * 2)',
 '((0 - 0) + 2)',
 '((0 - 0) - (0 - 2))',
 '((1 - 0) * 2)']
```

## Development
If you want to help develop on this project, you can install it like so using Python 3.7:
```
mkvirtualenv -a $(pwd) $(basename $(pwd)) -p python3
pip install -r requirements/development.txt
pre-commit install
```

This project uses `tox` with `pytest` for testing, so just run `tox` to run all tests.
