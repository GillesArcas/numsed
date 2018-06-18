# numsed
Computing with sed: compiling python into sed

# [![Build Status](https://travis-ci.org/GillesArcas/numsed.svg?branch=master)](https://travis-ci.org/GillesArcas/numsed)


# Table of Contents
* [Description](#description)
* [Language](#language)
* [Compilation process](#compilation-process)
* [Getting started](#getting-started)
* [ Command line](#command-line)
  * [Filename parameter](#filename-parameter)
  * [Action parameter](#action-parameter)
  * [Transformation parameter](#transformation-parameter)
  * [Format parameter](#format-parameter)
* [ Testing](#testing)
* [ numsed virtual machine](#numsed-virtual-machine)
* [ Links](#links)
  * [Abstract syntax tree](#abstract-syntax-trees)
  * [Opcodes](#dis-and-opcodes)
  * [Sed](#sed)

## Description

numsed compiles a small subset of python into sed scripts. This subset is sufficient to make any calculation using integer numbers. The compilation to sed uses python opcodes as intermediate format. Opcodes are replaced by sed snippets to obtain the final script.

numsed is compatible with python 2 and 3.

## Language

The subset of Python used by numsed is made of:

* signed integer constants and variables, with no limitation in size,
* arithmetic operators (+, -, *, //, %, **) and divmod function,
* comparison operators (==, !=, <, <=, >, >=),
* logical if,
* logical operators (and, or, not),
* assignments, including multiple assignments, augmented assignments and chained assignments,
* control flow statements (if-elif-else, while-else, break, continue, pass, exit),
* function definitions and calls,
* print function, 
* string constants only allowed as print arguments,
* global statement.

The following limitations are checked during conversion:

* functions must be defined as module level instructions,
* functions have only positional arguments with no default values,
* functions must return an integer (with the exception of the predefined function divmod),
* characters in strings are limited to ASCII-32 (space) to ASCII-125 ("}")
  less the characters "@", "|" and ";" which are used in sed snippets.

Note also that there is no limitations (less memory) on recursion.

## Compilation process

Compiling a python script into sed is made in four passes:

* the python script is transformed into another python script where all operators are replaced with functions. These functions are defined in the numsed_lib module. These definitions used the standard operators assuming they work on positive operands. Let's call the resulting script the positive form.
* The positive form is then compiled and disassembled with the dis module into opcodes.
* The disassembly is simplified and completed to obtain an opcode program which can be interpreted independently. The interpretation of opcodes is used for testing.
* Finally, the sed script is obtained by replacing each opcode by a sed snippet.

## Getting started

To install, just clone or download the depository zip file. There is no dependency.

Use the following command to compile and run a numsed python script:

`numsed.py filename`

The resulting sed script is obtained with:

`numsed.py --trace filename`

## Command line

The command line enables to specify several output formats, several transformations to apply to the original script, and several actions.

`numsed.py <action> <transformation> <format> filename`

Compiling a python script into sed and running it, is done with:

`numsed.py --run --signed --sed filename`

As all these options are defaults, this can be abbreviated into:

`numsed.py filename`

The other parameters are mainly used for development, testing or optimization.

###### Filename parameter

`filename` can be a python script with `.py` extension.

`filename` can be file containing opcodes with `.opc` extension. In that case, the transformation argument may be `--opcodes` or `--sed`. The opcodes contained in the file are executed, or used to generate sed instructions depending on the action.

`filename` is a collection of scripts if ended with `.suite.py`. Several python scripts are contained in the same file, separated by a comment with at least two dashes (`# ---`). In that case, the action is applied separately to each script in the collection.

`filename` can be the name of directory. In that case, the action is applied to each python script in this directory. 

###### Action parameter

`--trace`

* traces the result of the conversion. Available for all formats and transformations.

`--run (default)`

* executes the result of the conversion. Available for all formats (except disassembly)  and transformations.

`--coverage`

* available only for opcode format. Executes the opcodes and counts the number of calls for each opcode.

`--test` 

* compares the result of the original python script with the execution of the conversion. Available for all formats (except disassembly)  and transformations.

`--batch`

* runs several sets of command line parameters. See test.batch.

###### Transformation parameter

 `--literal` 

* no transformation is applied to the python script. When compiling into sed, this assumes that the script does not handle signed integers, and does not use division, modulo or power operators.

`--unsigned` 

* the python script is assumed to handle only unsigned integers, and the transformation replaces the division, modulo and power operators by functions implementing these operators.

`--signed (default)`

* the python script handles signed integers and the transformation replaces all operators with function implementing the signed operators.

Notes: 

* Using the literal or unsigned transformations on scripts using negative integers or all operators can lead to unexpected behaviour (crash, infinite loops).
* When running or testing the signed transformation with AST or script format, an additional transformation is applied to check that all operands are positive.

###### Format parameter

`--ast`

* generate the abstract syntax tree (AST)

`--script` 

* generates the python script

`--dis` 

* generates the disassembly

`--opcode`

* generates opcodes

`--sed (default)`

* generates the sed script


## Testing

Testing is done with the `--test` action with a test suite:

`numsed.py --test --sed --signed test.suite.py`

This displays a message describing the result when terminated.

## numsed virtual machine

Using the same opcodes as python, numsed uses machine model close to the one of python:

* all operators take their argument in the stack and put the result in the stack,
* there is a global namespace,
* there is local namespace for each function call.

In numsed, stack and namespaces are implemented in sed hold space (HS). HS is organized with the stack on the left and namespaces on the right separated by a "@":

                           HS: <stack>@<namespaces>

The stack grows at the beginning and contains integer values and addresses. Items are separated by semicolons. For instance:

                           HS: x;y;z;@<namespaces>
    LOAD_CONST  42         HS: 42;x;y;z;@<namespaces>
    LOAD_CONST  13         HS: 13;42;x;y;z;@<namespaces>
    BINARY_ADD             HS: 55;x;y;z;@<namespaces>

Name spaces grow at the end of HS and are separated by a vertical bar character "|". First name space is the global name space. Other name spaces are local and created for each function call. Name spaces contain pairs of names and values separated by semicolons. 

                           HS: x;y;z;@
    LOAD_CONST  42         HS: 42;x;y;z;@
    STORE_GLOBAL x         HS: x;y;z;@x;42;
    MAKE_CONTEXT           HS: x;y;z;@x;42;|
    LOAD_CONST  13         HS: 13;x;y;z;@x;42;|
    STORE_FAST x           HS: 55;x;y;z;@x;42;|x;13;
    POP_CONTEXT            HS: 55;x;y;z;@x;42;

## Links

#### Abstract syntax trees

The official documentation:

* https://docs.python.org/3/library/ast.html

A more detailed description:

* https://greentreesnakes.readthedocs.io/en/latest/

#### dis and opcodes

The official documentation:

* https://docs.python.org/3/library/dis.html

The implementation gives all details of opcode working:

* [cpython/ceval.c](https://github.com/python/cpython/blob/2bdba08bd0eb6f1b2a20d14558a4ea2009b46438/Python/ceval.c) 

#### Sed

The original documentation:

* http://sed.sourceforge.net/grabbag/tutorials/sed_mcmahon.txt

Description of using lookup tables with sed by Greg Ubben:

* [Using lookup tables with s///](http://sed.sourceforge.net/grabbag/tutorials/lookup_tables.txt)
* [A lookup-table counter](http://sed.sourceforge.net/grabbag/tutorials/lookup_table_counter.txt)

The inspiring sed implementation of dc by Greg Ubben:

* [dc.sed](http://sed.sourceforge.net/grabbag/scripts/dc.sed)


