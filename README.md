rfmt
====

The file `rfmt.py` and its associated package, `formatter` comprise a
stand-alone code formatter for the [R](http://www.r-project.org/) programming
language, in the same mold as [**gofmt**](https://golang.org/cmd/gofmt/) tool
for Go, and [**clang-format**](http://clang.llvm.org/docs/ClangFormat.html) for
C/C++.

To use the formatter, you'll need Python 2.7 or later, and you'll need to
ensure that David Beazley's [`ply` package](http://www.dabeaz.com/ply/) is
[accessible to Python](https://docs.python.org/2/using/cmdline.html#envvar-PYTHONPATH).
Help for command line usage is available by running `python rfmt.py --help`.
