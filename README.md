# numsed
Computing with sed: compiling python into sed

# [![Build Status](https://travis-ci.org/GillesArcas/numsed.svg?branch=master)](https://travis-ci.org/GillesArcas/numsed)[![Coverage Status](https://coveralls.io/repos/github/GillesArcas/numsed/badge.svg?branch=master)](https://coveralls.io/github/GillesArcas/numsed?branch=master)

# Table of Contents
* [Description](#description)
* [Language](#language)
* [Getting started](#getting-started)
* [Compilation process](#compilation-process)
* [ Command line](#command-line)
  * [Filename parameter](#filename-parameter)
  * [Action parameter](#action-parameter)
  * [Transformation parameter](#transformation-parameter)
  * [Format parameter](#format-parameter)
* [ Testing](#testing)
* [Opcodes](#opcodes)
* [ numsed virtual machine](#numsed-virtual-machine)
* [Calls and returns](#calls-and-returns)
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
* comparison operators and boolean operators are limited to test position (if, while, ternary if),
* characters in strings are limited to ASCII-32 (space) to ASCII-125 ("}")
  less the characters "@", "|" and ";" which are used in sed snippets.

These features and limitations are designed to guarantee that the initial python script and the resulting sed script give always the same results.

Note also that recursion is handled with no limitations (except memory) on depth. 

Examples of this dialect are given in the test suite and in the example folder. This includes 20 examples from Project Euler. 

## Getting started

To install, just clone or download the depository zip file and run the setup.

Use the following command to compile and run a numsed python script:

`numsed.py filename`

The resulting sed script is obtained with:

`numsed.py --trace filename`

## Compilation process

Compiling a python script into sed is made in four passes:

- the python script is transformed into another python script where all operators are replaced with functions. These functions are defined in the numsed_lib module. These definitions used the standard operators assuming they work on positive operands. Let's call the resulting script the positive form.
- The positive form is then compiled and disassembled with the dis module into opcodes.
- The disassembly is simplified and completed to obtain an opcode program which can be interpreted independently. The interpretation of opcodes is used for testing.
- Finally, the sed script is obtained by replacing each opcode by a sed snippet.

The example directory contains an exemple of a simple python script (add.py) and the resulting opcode and sed scripts (add.opc and add.sed). The opcode script can be interpreted with the --opcode option. The sed script can be interpreted with any sed utility.

## Command line

The command line enables to specify several output formats, several transformations to apply to the original script, and several actions.

`numsed.py <action> <transformation> <format> filename`

Compiling a python script into sed and running it, is done with:

`numsed.py --run --signed --sed filename`

As all these options are defaults, this can be abbreviated into:

`numsed.py filename`

The other parameters are used for development, testing or optimization.

###### Filename parameter

`filename` can be a python script with `.py` extension.

`filename` can be file containing opcodes with `.opc` extension. In that case, the transformation argument may be `--opcodes` or `--sed`. The opcodes contained in the file are executed, or used to generate sed instructions depending on the action.

`filename` is a collection of scripts if ended with `.suite.py`. Several python scripts are contained in the same file, separated by a comment with at least two dashes (`# ---`). In that case, the action is applied separately to each script in the collection.

`filename` can be the name of a directory. In that case, the action is applied to each python script in this directory. 

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

* runs several sets of command line parameters. See test.batch file in tests directory.

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

## Opcodes

numsed transforms sed scripts to opcodes then replace each opcode by a sed snippet. These opcodes are derived from the result of disassembling with dis utility. They are then simplified and completed to obtain an autonomous script which can be interpreted.

The transformation process goes as follow:

* labels and bytecode numbers are removed,
* bytecodes requested for branching (indicated with ">>") insert a label opcode prefixed with a column (":18"),
* the name of arguments in parentheses is kept but the index to one of the name spaces are ignored,
* in the case of relative jumps, the parentheses contain the absolute address. Therefore, all relative jumps are transformed into absolute jumps.

Here is an example:

    1    0 LOAD_CONST         0 (42)                         LOAD_CONST        42
         2 STORE_NAME         0 (n)                          STORE_NAME        n
    2    4 LOAD_NAME          0 (n)                          LOAD_NAME         n
         6 LOAD_CONST         1 (0)                          LOAD_CONST        0
         8 COMPARE_OP         0 (<)                          COMPARE_OP        <
        10 POP_JUMP_IF_FALSE 18               gives          POP_JUMP_IF_FALSE 18
        12 LOAD_NAME          0 (n)                          LOAD_NAME         n
        14 UNARY_NEGATIVE                                    UNARY_NEGATIVE
        16 JUMP_FORWARD       2 (to 20)                      JUMP              20
                                                             :18
     >> 18 LOAD_NAME          0 (n)                          LOAD_NAME         n
                                                             :20
     >> 20 STORE_NAME         1 (r)                          STORE_NAME        r  
Functions are disassembled apart. The code of functions is prefixed with the FUNCTION keyword, a label reminding the name of the function, and the names of the parameters (-1 being a dummy bytecode number). 

    1    0 LOAD_CONST         0 (<code object foo at 0x0336D0D0, file "<ast>", line 1>)
           ...
        -1 FUNCTION           foo.func n
           ... 
         6 RETURN_VALUE 
When converting disassembly to opcodes, the reference to the function object is replaced with the label of the function. This label is used as the entry point of the function.

    LOAD_CONST        print.func
    ...
    :foo.func
    ...
    RETURN_VALUE
The local context of the function is created and deleted with two additional opcodes, `MAKE_CONTEXT` and `POP_CONTEXT`, added at the beginning and at the end of the function. Once the context is created, the parameters are popped and store locally.

    :foo.func
    MAKE_CONTEXT
    STORE_FAST        n
    ...
    POP_CONTEXT
    RETURN_VALUE

Finally, some more transformations are applied to opcodes to make easier the conversion to sed. For instance, INPLACE_ opcodes are replaced with their binary equivalents, BREAK_LOOP are transformed into a JUMP, and some other. Hopefully, this is enough documented in the code.

## numsed virtual machine

Using the same opcodes as python, numsed uses a machine model close to the one of python:

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

## Calls and returns

The call and return instructions are missing in sed. Additionally, we need a way to branch on names as call addresses come from the stack and are stored as strings. The two available instructions are `b`, the unconditional branching, and `t`, the conditional branching which tests if a previous substitution has been successful. Both require labels which live in the sed command space but not in the sed pattern or hold spaces.

We have therefore the following problems to solve:

* simulate calls by using numsed stack,
* make the conversion between string labels and sed labels. This enables to implement calls with strings as argument, but also to implement returns as branching to string labels stored in some way,

### Calls

Assume we have a POP_GOTO instruction taking a string at the top of stack as argument and branching to the corresponding sed label. Calls are implemented by creating and pushing an explicit return label. Ignoring function arguments to simplify the example, we have:

    # TOS == "myfunc"              		# TOS == "myfunc"
    CALL_FUNCTION                  		PUSH "myreturn"
    ...                            		ROT_TWO
    :myfunc            implemented as   POP_GOTO  # branch to popped value
    ...                            		:myreturn
    RETURN                         		...
                                   		:myfunc
                                   		...             
                                   		POP_GOTO  # branch to popped value


###Branching on string labels

We have now to find a way to branch on strings. The problem is that labels for sed branching and strings are in different spaces and a conversion is required. To do this, we gather all possible values of branching labels during conversion. and test these values to branch conditionally to the corresponding sed label.

This list of labels can be:

* either the list of all function labels (these values will be found in the stack when executing CALL_FUNCTION),

* or the list of all return labels  (these values will be found in the stack when executing RETURN).

For instance, let L1, L2, ..., Ln be the possible function labels. The pseudocode to implement `GOTO "L"` where L can be in L1,  L2, ..., Ln is something like:

    if string_label == "L1" goto L1
    if string_label == "L2" goto L2
    ...

The conversion to sed is straightforward:

    s/^L1$//t L1
    s/^L2$//t L2
    ...

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


