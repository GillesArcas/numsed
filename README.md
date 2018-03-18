# numsed
Computing with sed: compiling python scripts into sed scripts

[TOC]

## Description

numsed compiles a tiny subset of python into sed scripts. This subset is sufficient to make any calculation using integer numbers. The compilation to sed uses python opcodes as intermediate format. These opcodes can be interpreted as independent programs and are replaced by sed snippets to obtain the final the script.

numsed is compatible with python 2 and 3.

## Language

numsed uses a small subset of python, a minimal subset to make non trivial integer calculus.

This subset includes:

* signed integer constants and variables, with no limitation in size,
* arithmetic operators (+, -, *, //, %, **)
* comparison operators (==, !=, <, <=, >, >=)
* logical if
* logical operators (and , or, not)
* assignments, including augmented assignments and chained assignments,
* control flow statements (if-elif-else, while-else, break, continue, pass)
* function definitions and calls
* print function
* global statement
* first citizen functions. Functions can be assigned to variables, returned by functions and compared. However, arithmetical and comparison operators do not apply to functions and the assumption is made in the current version that arithmetical and comparison operator operands are always integers.

The grammar of numsed python is given in the file grammar/grammar. 

A numsed script is a python script and can be executed as any python script. When executed by numsed, a verification is done to check that the script uses only numsed python subset.

There are some limitations to note:

* there is no list and as a consequence no parallel assignments nor multiple return results
* functions have only positional arguments with no default values
* it is not possible to define a function inside a function
* print has always a single argument

More limitations:

* there is no control on using arithmetical and comparison operators with functions
* not always return 0 or 1, and the result cannot be compared with python which returns True or False
* the value printed for functions cannot be compared with the function values printed by python.

Note also that there is no limitations (less memory) on recursion.

## Compilation process

Compiling a python script sed is made in four passes:

* the python script is transformed into another python script where all operators are replaced with functions. These functions are defined in the module numsed_lib. These definitions used the standard operators but with positive operands. Let's call the resulting script the positive form.
* The positive form is then compiled and disassembled with the dis module into opcodes including the function definitions.
* The disassembly is simplified and completed to obtain an opcode program which can be interpreted. The interpretation of opcodes is used for testing.
* Finally, the sed script is obtained by replacing each opcode by a sed snippet.


## Command line

The command line enables to specify several output formats, several transformations to apply to the original script, and several actions.

`numsed.py <action> <transformation> <format> filename`

To focus on the goal of the project, compiling a python script  into sed and running it, is done with:

`numsed.py --run --signed --sed filename`

The other parameters are used for development and testing.

###### Filename parameter

`filename` can be a python script with `.py` extension.

`filename` can be file containing opcodes with `.opc` extension. In that case, the transformation argument may be `--opcodes` or `--sed`. The opcodes contained in the file are executed, or used to generate sed instructions depending on the action.

`filename` is a collection of scripts if ended with `.suite.py`. Several python scripts are contained in the same file, separated by a comment with at least two dashes (`# --`). In that case, the action is applied separately to each script in the collection.

###### Action parameter

`--trace`

- trace the result of the conversion. Available for all formats and transformations.

`--run`

- execute the result of the conversion. Available for all formats (except disassembly)  and transformations.

`--coverage`

- available only for opcode format. Execute the opcodes and counts the number of calls for each opcode.

`--test` 

- compare the result of the original python script with the execution of the conversion. Available for all formats (except disassembly)  and transformations.

###### Transformation parameter

 `--literal` 

* no transformation is applied to the python script. When compiling into sed, this assumes that the script  does not handle signed integers, and does not use division, modulo or power operators.

`--unsigned` 

* the python script is assumed to handle only unsigned integers, and the transformation replaces the division, modulo and power operators by functions implementing these operators.

`--signed`

* the python script handles signed integers and the transformation replaces all operators with function implementing the signed operators.

Notes: 

* It must be kept in mind that using the literal or unsigned transformation on scripts using negative integers or all operators can lead to unexpected behaviour (crash, infinite loops).
* When running or testing the signed transformation with AST or script format, an additional transformation is applied to check that all operands are positive.

###### Format parameter

`--ast`

* generate the abstract syntax tree (AST) after transformation

`--script` 

* generates the python script after transformation

`--dis` 

* generates the disassembly after transformation

`--opcode`

* generates opcodes

`--sed`

* generates the sed script


## Testing

Testing is done with the `--test` action with a test suite:

`numsed.py --test --sed --signed test.suite.py`

This displays a message describing the result when terminated.

To test all the possible formats and transformations, use the `--all` parameter.

`numsed_test.py --all test.suite.py`

Finally, the `snippet_test.py` script enables to test some opcodes with hardcoded inputs.