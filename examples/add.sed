# This sed script is the result of the compilation of the following python script by numsed.py
# https://github.com/GillesArcas/numsed

# # assign add
# m = 42
# n = 5
# p = m + n
# print(p)

                                        # STARTUP

    x
    s/.*/end_of_script;@/
    x
    bL71
:end_of_script
    q
:NameError
    s/.*/NameError: name & is not defined/
    p
    q
:UnknownLabel
    s/.*/UnknownLabel: label & is not defined/
    p
    q
:NotPositiveInteger
    s/^([^;]+;[^;]+).*/NotPositiveInteger: an operand is not a positive integer: \1/
    p
    q
:NotImplemented
    s/.*/NotImplemented: not available with --literal, use --unsigned or --signed: &/
    p
    q
:L71
                                        # STARTUP/

                                        # LOAD_CONST print.func
                                        # PS: ?         HS: X
    g                                   # PS: X         HS: X
    s/^/print.func;/                    # PS: print.func;X   HS: X
    h                                   # PS: print.func;X   HS: print.func;X
                                        # LOAD_CONST/

                                        # MAKE_FUNCTION 0
                                        # MAKE_FUNCTION/

                                        # STORE_NAME print
                                        # PS: ?         HS: x;X
    g
    s/(@[^|]*);print;[^;|]*/\1/         # PS: x;X'      HS: ? (del ;var;val in PS)
    s/^([^;]*);([^@]*@)/\2;print;\1/    # PS: X;v;x     HS: ?
    h                                   # PS: ?         HS: X;v;x
                                        # STORE_NAME/

                                        # LOAD_CONST signed_add.func
                                        # PS: ?         HS: X
    g                                   # PS: X         HS: X
    s/^/signed_add.func;/               # PS: signed_add.func;X   HS: X
    h                                   # PS: signed_add.func;X   HS: signed_add.func;X
                                        # LOAD_CONST/

                                        # MAKE_FUNCTION 0
                                        # MAKE_FUNCTION/

                                        # STORE_NAME signed_add
                                        # PS: ?         HS: x;X
    g
    s/(@[^|]*);signed_add;[^;|]*/\1/    # PS: x;X'      HS: ? (del ;var;val in PS)
    s/^([^;]*);([^@]*@)/\2;signed_add;\1/# PS: X;v;x     HS: ?
    h                                   # PS: ?         HS: X;v;x
                                        # STORE_NAME/

                                        # LOAD_CONST 42
                                        # PS: ?         HS: X
    g                                   # PS: X         HS: X
    s/^/42;/                            # PS: 42;X   HS: X
    h                                   # PS: 42;X   HS: 42;X
                                        # LOAD_CONST/

                                        # STORE_NAME m
                                        # PS: ?         HS: x;X
    g
    s/(@[^|]*);m;[^;|]*/\1/             # PS: x;X'      HS: ? (del ;var;val in PS)
    s/^([^;]*);([^@]*@)/\2;m;\1/        # PS: X;v;x     HS: ?
    h                                   # PS: ?         HS: X;v;x
                                        # STORE_NAME/

                                        # LOAD_CONST 5
                                        # PS: ?         HS: X
    g                                   # PS: X         HS: X
    s/^/5;/                             # PS: 5;X   HS: X
    h                                   # PS: 5;X   HS: 5;X
                                        # LOAD_CONST/

                                        # STORE_NAME n
                                        # PS: ?         HS: x;X
    g
    s/(@[^|]*);n;[^;|]*/\1/             # PS: x;X'      HS: ? (del ;var;val in PS)
    s/^([^;]*);([^@]*@)/\2;n;\1/        # PS: X;v;x     HS: ?
    h                                   # PS: ?         HS: X;v;x
                                        # STORE_NAME/

                                        # LOAD_NAME signed_add
                                        # PS: ?         HS: ?;v;x?
    g                                   # PS: ?;v;x?    HS: ?;v;x?
    /@[^|]*;signed_add;/! { s/.*/signed_add/; b NameError }
                                        # branch to error if var undefined
    s/[^@]*@[^|]*;signed_add;([^;|]*).*/\1;&/
                                        # PS: x;?;v;x?  HS: ?;v;x?
    h                                   # PS: x;?;v;x?  HS: x;?;v;x?
                                        # LOAD_NAME/

                                        # LOAD_NAME m
                                        # PS: ?         HS: ?;v;x?
    g                                   # PS: ?;v;x?    HS: ?;v;x?
    /@[^|]*;m;/! { s/.*/m/; b NameError }
                                        # branch to error if var undefined
    s/[^@]*@[^|]*;m;([^;|]*).*/\1;&/
                                        # PS: x;?;v;x?  HS: ?;v;x?
    h                                   # PS: x;?;v;x?  HS: x;?;v;x?
                                        # LOAD_NAME/

                                        # LOAD_NAME n
                                        # PS: ?         HS: ?;v;x?
    g                                   # PS: ?;v;x?    HS: ?;v;x?
    /@[^|]*;n;/! { s/.*/n/; b NameError }
                                        # branch to error if var undefined
    s/[^@]*@[^|]*;n;([^;|]*).*/\1;&/
                                        # PS: x;?;v;x?  HS: ?;v;x?
    h                                   # PS: x;?;v;x?  HS: x;?;v;x?
                                        # LOAD_NAME/

                                        # CALL_FUNCTION 2

    x
    s/^(([^;]*;){2})([^;]+;)/\3\1R0;/
    s/^print.func;/print.func;~~;/
    x
                                        # POP
                                        # PS: ?         HS: N;X
    g                                   # PS: N;X       HS: N;X
    s/^[^;]*;//                         # PS: X         HS: N;X
    x                                   # PS: N;X       HS: X
    s/;.*//                             # PS: N         HS: X
                                        # POP/

    b call_function
:R0
                                        # CALL_FUNCTION/

                                        # STORE_NAME p
                                        # PS: ?         HS: x;X
    g
    s/(@[^|]*);p;[^;|]*/\1/             # PS: x;X'      HS: ? (del ;var;val in PS)
    s/^([^;]*);([^@]*@)/\2;p;\1/        # PS: X;v;x     HS: ?
    h                                   # PS: ?         HS: X;v;x
                                        # STORE_NAME/

                                        # LOAD_NAME print
                                        # PS: ?         HS: ?;v;x?
    g                                   # PS: ?;v;x?    HS: ?;v;x?
    /@[^|]*;print;/! { s/.*/print/; b NameError }
                                        # branch to error if var undefined
    s/[^@]*@[^|]*;print;([^;|]*).*/\1;&/
                                        # PS: x;?;v;x?  HS: ?;v;x?
    h                                   # PS: x;?;v;x?  HS: x;?;v;x?
                                        # LOAD_NAME/

                                        # LOAD_NAME p
                                        # PS: ?         HS: ?;v;x?
    g                                   # PS: ?;v;x?    HS: ?;v;x?
    /@[^|]*;p;/! { s/.*/p/; b NameError }
                                        # branch to error if var undefined
    s/[^@]*@[^|]*;p;([^;|]*).*/\1;&/
                                        # PS: x;?;v;x?  HS: ?;v;x?
    h                                   # PS: x;?;v;x?  HS: x;?;v;x?
                                        # LOAD_NAME/

                                        # CALL_FUNCTION 1

    x
    s/^(([^;]*;){1})([^;]+;)/\3\1R1;/
    s/^print.func;/print.func;~;/
    x
                                        # POP
                                        # PS: ?         HS: N;X
    g                                   # PS: N;X       HS: N;X
    s/^[^;]*;//                         # PS: X         HS: N;X
    x                                   # PS: N;X       HS: X
    s/;.*//                             # PS: N         HS: X
                                        # POP/

    b call_function
:R1
                                        # CALL_FUNCTION/

                                        # POP_TOP

    g
    s/^[^;]+;//
    h
                                        # POP_TOP/

                                        # EXIT

    q
                                        # EXIT/


:signed_add.func
                                        # MAKE_CONTEXT

    x
    s/$/|/
    x
                                        # MAKE_CONTEXT/

                                        # STORE_FAST y
                                        # PS: ?         HS: x;X
    g                                   # PS: x;X       HS: ?
    s/;y;[^;|]*([^|]*)$/\1/             # PS: x;X'      HS: ? (del ;var;val in PS)
    s/^([^;]*);(.*)/\2;y;\1/            # PS: X';v;x    HS: ?
    h                                   # PS: ?         HS: X';v;x
                                        # STORE_FAST/

                                        # STORE_FAST x
                                        # PS: ?         HS: x;X
    g                                   # PS: x;X       HS: ?
    s/;x;[^;|]*([^|]*)$/\1/             # PS: x;X'      HS: ? (del ;var;val in PS)
    s/^([^;]*);(.*)/\2;x;\1/            # PS: X';v;x    HS: ?
    h                                   # PS: ?         HS: X';v;x
                                        # STORE_FAST/

                                        # LOAD_FAST x
                                        # PS: ?         HS: ?;v;x?
    g                                   # PS: ?;v;x?    HS: ?;v;x?
    tL0                                 # reset t flag
:L0
    s/.*;x;([^;]*)[^|]*$/\1;&/          # PS: x;?;v;x?  HS: ?;v;x?
    tL1
    s/.*/x/; b NameError                # branch to error if var undefined
:L1
    h                                   # PS: ?         HS: x;?;v;x?
                                        # LOAD_FAST/

                                        # IS_POSITIVE
                                        # PS: ?         HS: N;X
    g                                   # PS: N;X       HS: N;X
    s/^[0-9+][^;]*/1/                   # PS: 1;X       HS: N;X  if pos
    s/^-[^;]+/0/                        # PS: 0;X       HS: N;X  if neg
    h                                   # PS: r;X       HS: r;X  r = 0 or 1
                                        # IS_POSITIVE/

                                        # POP_JUMP_IF_FALSE 85

                                        # POP
                                        # PS: ?         HS: N;X
    g                                   # PS: N;X       HS: N;X
    s/^[^;]*;//                         # PS: X         HS: N;X
    x                                   # PS: N;X       HS: X
    s/;.*//                             # PS: N         HS: X
                                        # POP/

    /^0$/b 85
                                        # POP_JUMP_IF_FALSE/

                                        # LOAD_FAST y
                                        # PS: ?         HS: ?;v;x?
    g                                   # PS: ?;v;x?    HS: ?;v;x?
    tL2                                 # reset t flag
:L2
    s/.*;y;([^;]*)[^|]*$/\1;&/          # PS: x;?;v;x?  HS: ?;v;x?
    tL3
    s/.*/y/; b NameError                # branch to error if var undefined
:L3
    h                                   # PS: ?         HS: x;?;v;x?
                                        # LOAD_FAST/

                                        # IS_POSITIVE
                                        # PS: ?         HS: N;X
    g                                   # PS: N;X       HS: N;X
    s/^[0-9+][^;]*/1/                   # PS: 1;X       HS: N;X  if pos
    s/^-[^;]+/0/                        # PS: 0;X       HS: N;X  if neg
    h                                   # PS: r;X       HS: r;X  r = 0 or 1
                                        # IS_POSITIVE/

                                        # POP_JUMP_IF_FALSE 39

                                        # POP
                                        # PS: ?         HS: N;X
    g                                   # PS: N;X       HS: N;X
    s/^[^;]*;//                         # PS: X         HS: N;X
    x                                   # PS: N;X       HS: X
    s/;.*//                             # PS: N         HS: X
                                        # POP/

    /^0$/b 39
                                        # POP_JUMP_IF_FALSE/

                                        # LOAD_FAST x
                                        # PS: ?         HS: ?;v;x?
    g                                   # PS: ?;v;x?    HS: ?;v;x?
    tL4                                 # reset t flag
:L4
    s/.*;x;([^;]*)[^|]*$/\1;&/          # PS: x;?;v;x?  HS: ?;v;x?
    tL5
    s/.*/x/; b NameError                # branch to error if var undefined
:L5
    h                                   # PS: ?         HS: x;?;v;x?
                                        # LOAD_FAST/

                                        # LOAD_FAST y
                                        # PS: ?         HS: ?;v;x?
    g                                   # PS: ?;v;x?    HS: ?;v;x?
    tL6                                 # reset t flag
:L6
    s/.*;y;([^;]*)[^|]*$/\1;&/          # PS: x;?;v;x?  HS: ?;v;x?
    tL7
    s/.*/y/; b NameError                # branch to error if var undefined
:L7
    h                                   # PS: ?         HS: x;?;v;x?
                                        # LOAD_FAST/

                                        # BINARY_ADD
                                        # PS: ?         HS: M;N;X
                                        # POP2
                                        # PS: ?         HS: M;N;X
    g                                   # PS: M;N;X     HS: M;N;X
    s/^[^;]*;[^;]*;//                   # PS: X         HS: M;N;X
    x                                   # PS: M;N;X     HS: X
    s/(^[^;]*;[^;]*).*/\1/              # PS: M;N       HS: X
                                        # POP2/
                                        # PS: M;N       HS: X
                                        # CHECKINT2
                                        # PS: X;Y       HS: X;Y;Z
    /^[0-9]+;[0-9]+/!b NotPositiveInteger
                                        # CHECKINT2/

                                        # UADD

                                        # PS: M;N*
    s/[0-9]*;[0-9]*/0;&;/               # PS; 0;M;N;*
:L46                                    # PS: cR;Mm;Nn;*
    s/^([0-9]*);([0-9]*)([0-9]);([0-9]*)([0-9])/\3\5\1;\2;\4/
                                        # PS: mncR;M;N;*
                                        # FULLADD

    s/^(...)/\1;9876543210;9876543210;/
    s/^(..)0/\1/
    s/(.)(.)([0-9])*;([0-9]*\1([0-9]*));[0-9]*(\2[0-9]*);/\3\5\6\4;/
    s/.{10}(.)[0-9]{0,9}([0-9]{0,1})[0-9]*;/0\2\1;/
    /^0[0-9]([0-9]);/s//1\1;/
    s/;//
                                        # FULLADD/
                                        # PS: abR;M;N;*
    /^[0-9]*;[0-9]*[0-9];[0-9]/bL46     # more digits in M and N
    /^[0-9]*;;;/{                       # no more digits in M and N
    s/;;;//
    s/^0//
    bL47
    }
    /^1/{
    s/;;/;0;/
    bL46
    }
    s/^0([0-9]*);([0-9]*);([0-9]*);/\2\3\1/
:L47                                    # PS: R*
                                        # UADD/
                                        # PS: R         HS: X
                                        # PUSH
                                        # PS: N         HS: X
    G                                   # PS: N\nX      HS: X
    s/\n/;/                             # PS: N;X       HS: X
    h                                   # PS: N;X       HS: N;X
    s/;.*//                             # PS: N         HS: N;X
                                        # PUSH/
                                        # PS: R         HS: R;X
                                        # BINARY_ADD/

                                        # STORE_FAST r
                                        # PS: ?         HS: x;X
    g                                   # PS: x;X       HS: ?
    s/;r;[^;|]*([^|]*)$/\1/             # PS: x;X'      HS: ? (del ;var;val in PS)
    s/^([^;]*);(.*)/\2;r;\1/            # PS: X';v;x    HS: ?
    h                                   # PS: ?         HS: X';v;x
                                        # STORE_FAST/

                                        # JUMP 161
    b 161                               # JUMP/


:39
                                        # LOAD_FAST y
                                        # PS: ?         HS: ?;v;x?
    g                                   # PS: ?;v;x?    HS: ?;v;x?
    tL8                                 # reset t flag
:L8
    s/.*;y;([^;]*)[^|]*$/\1;&/          # PS: x;?;v;x?  HS: ?;v;x?
    tL9
    s/.*/y/; b NameError                # branch to error if var undefined
:L9
    h                                   # PS: ?         HS: x;?;v;x?
                                        # LOAD_FAST/

                                        # UNARY_NEGATIVE
                                        # PS: ?         HS: N;X
    g                                   # PS: N;X       HS: N;X
    s/^-/!/                             # use marker to avoid another substitution
    s/^\+/-/                            #
    s/^[0-9]/-&/                        #
    s/^-0;/0;/                          # handle N = -0
    s/^!//                              # remove marker
    h                                   # PS: R;X       HS: R;X  R = -N
                                        # UNARY_NEGATIVE/

                                        # STORE_FAST y
                                        # PS: ?         HS: x;X
    g                                   # PS: x;X       HS: ?
    s/;y;[^;|]*([^|]*)$/\1/             # PS: x;X'      HS: ? (del ;var;val in PS)
    s/^([^;]*);(.*)/\2;y;\1/            # PS: X';v;x    HS: ?
    h                                   # PS: ?         HS: X';v;x
                                        # STORE_FAST/

                                        # LOAD_FAST x
                                        # PS: ?         HS: ?;v;x?
    g                                   # PS: ?;v;x?    HS: ?;v;x?
    tL10                                # reset t flag
:L10
    s/.*;x;([^;]*)[^|]*$/\1;&/          # PS: x;?;v;x?  HS: ?;v;x?
    tL11
    s/.*/x/; b NameError                # branch to error if var undefined
:L11
    h                                   # PS: ?         HS: x;?;v;x?
                                        # LOAD_FAST/

                                        # LOAD_FAST y
                                        # PS: ?         HS: ?;v;x?
    g                                   # PS: ?;v;x?    HS: ?;v;x?
    tL12                                # reset t flag
:L12
    s/.*;y;([^;]*)[^|]*$/\1;&/          # PS: x;?;v;x?  HS: ?;v;x?
    tL13
    s/.*/y/; b NameError                # branch to error if var undefined
:L13
    h                                   # PS: ?         HS: x;?;v;x?
                                        # LOAD_FAST/

                                        # COMPARE_OP >

                                        # SWAP
                                        # PS: ?         HS: M;N;X
    x                                   # PS: M;N;X     HS: ?
    s/^([^;]*;)([^;]*;)/\2\1/           # PS: N;M;X     HS: ?
    x                                   # PS: ?         HS: N;M;X
                                        # SWAP/

                                        # POP2
                                        # PS: ?         HS: M;N;X
    g                                   # PS: M;N;X     HS: M;N;X
    s/^[^;]*;[^;]*;//                   # PS: X         HS: M;N;X
    x                                   # PS: M;N;X     HS: X
    s/(^[^;]*;[^;]*).*/\1/              # PS: M;N       HS: X
                                        # POP2/

                                        # CHECKINT2
                                        # PS: X;Y       HS: X;Y;Z
    /^[0-9]+;[0-9]+/!b NotPositiveInteger
                                        # CHECKINT2/

    s/$/;/
                                        # CMP
                                        # PS: X;Y;
    s/;/!;/g                            # PS: X!;Y!;
:L62                                    # PS: Xx!X';Yy!Y';
    s/([0-9])!([0-9]*;[0-9]*)([0-9])!/!\1\2!\3/# PS: X!xX';Y!yY';
    tL62
    /^!/!bL64
    /;!/!bL63
                                        # PS: !X;!Y;
    s/^!([0-9]*)([0-9]*);!\1([0-9]*);/\2;\3;/# strip identical leading digits
    /^;;$/ { s/.*/=/; bL65 }            # PS: = if all digits are equal

    s/$/9876543210/
    /^(.)[0-9]*;(.)[0-9]*;.*\1.*\2/bL64
:L63
    s/.*/</                             # PS: < if x < y
    bL65
:L64
    s/.*/>/                             # PS: > if x > y
:L65                                    # PS: <|=|>
                                        # CMP/

    y/<=>/001/
                                        # PUSH
                                        # PS: N         HS: X
    G                                   # PS: N\nX      HS: X
    s/\n/;/                             # PS: N;X       HS: X
    h                                   # PS: N;X       HS: N;X
    s/;.*//                             # PS: N         HS: N;X
                                        # PUSH/

                                        # COMPARE_OP/

                                        # POP_JUMP_IF_FALSE 71

                                        # POP
                                        # PS: ?         HS: N;X
    g                                   # PS: N;X       HS: N;X
    s/^[^;]*;//                         # PS: X         HS: N;X
    x                                   # PS: N;X       HS: X
    s/;.*//                             # PS: N         HS: X
                                        # POP/

    /^0$/b 71
                                        # POP_JUMP_IF_FALSE/

                                        # LOAD_FAST x
                                        # PS: ?         HS: ?;v;x?
    g                                   # PS: ?;v;x?    HS: ?;v;x?
    tL14                                # reset t flag
:L14
    s/.*;x;([^;]*)[^|]*$/\1;&/          # PS: x;?;v;x?  HS: ?;v;x?
    tL15
    s/.*/x/; b NameError                # branch to error if var undefined
:L15
    h                                   # PS: ?         HS: x;?;v;x?
                                        # LOAD_FAST/

                                        # LOAD_FAST y
                                        # PS: ?         HS: ?;v;x?
    g                                   # PS: ?;v;x?    HS: ?;v;x?
    tL16                                # reset t flag
:L16
    s/.*;y;([^;]*)[^|]*$/\1;&/          # PS: x;?;v;x?  HS: ?;v;x?
    tL17
    s/.*/y/; b NameError                # branch to error if var undefined
:L17
    h                                   # PS: ?         HS: x;?;v;x?
                                        # LOAD_FAST/

                                        # BINARY_SUBTRACT
                                        # PS: ?         HS: M;N;X
                                        # SWAP
                                        # PS: ?         HS: M;N;X
    x                                   # PS: M;N;X     HS: ?
    s/^([^;]*;)([^;]*;)/\2\1/           # PS: N;M;X     HS: ?
    x                                   # PS: ?         HS: N;M;X
                                        # SWAP/

                                        # POP2
                                        # PS: ?         HS: M;N;X
    g                                   # PS: M;N;X     HS: M;N;X
    s/^[^;]*;[^;]*;//                   # PS: X         HS: M;N;X
    x                                   # PS: M;N;X     HS: X
    s/(^[^;]*;[^;]*).*/\1/              # PS: M;N       HS: X
                                        # POP2/
                                        # PS: M;N       HS: X
                                        # CHECKINT2
                                        # PS: X;Y       HS: X;Y;Z
    /^[0-9]+;[0-9]+/!b NotPositiveInteger
                                        # CHECKINT2/

                                        # USUB

                                        # PS: M;N*
    s/[0-9]*;[0-9]*/0;&;/               # PS; 0;M;N;*
:L50                                    # PS: cR;Mm;Nn;*
    s/([0-9]*);([0-9]*)([0-9]);([0-9]*)([0-9]);/\3\5\1;\2;\4;/
                                        # PS: mncR;M;N;*
                                        # FULLSUB

    s/^(...)/\1;9876543210;0123456789;/
    s/^(..)0/\1/
    s/(.)(.)([0-9]*);[0-9]*\2([0-9]*);([0-9]*(\1[0-9]*));/\3\4\6\5;/
    s/.{10}(.)[0-9]{0,9}([0-9]{0,1})[0-9]*;/0\2\1;/
    /^0[0-9]([0-9]);/s//1\1;/
    s/;//
                                        # FULLSUB/
                                        # PS: c'rR;M;N;*
    /^[0-9]*;[0-9]*[0-9];[0-9]/ bL50    # more digits in M and N
    /^[0-9]*;;[0-9]/bL51                # more digits in N
    /^1[0-9]*;;;/bL51                   # same number of digits, but borrow
    /^1/{                               # if borrow,
    s/^1([0-9]*;[0-9]*);;/0\1;1;/       # move borrow to second operand
    bL50                                # and loop
    }
    s/^0([0-9]*);([0-9]*);;/\2\1/       # add remaining part of first operand
    s/^0*([0-9])/\1/                    # del leading 0
    bL52
:L51                                    # if invalid subtraction
    s/^[0-9]*;[0-9]*;[0-9]*;/NAN/       # PS: NAN*
:L52                                    # PS: M-N|NAN
                                        # USUB/
                                        # PS: R         HS: X
                                        # PUSH
                                        # PS: N         HS: X
    G                                   # PS: N\nX      HS: X
    s/\n/;/                             # PS: N;X       HS: X
    h                                   # PS: N;X       HS: N;X
    s/;.*//                             # PS: N         HS: N;X
                                        # PUSH/
                                        # PS: R         HS: R;X
                                        # BINARY_SUBTRACT/

                                        # STORE_FAST r
                                        # PS: ?         HS: x;X
    g                                   # PS: x;X       HS: ?
    s/;r;[^;|]*([^|]*)$/\1/             # PS: x;X'      HS: ? (del ;var;val in PS)
    s/^([^;]*);(.*)/\2;r;\1/            # PS: X';v;x    HS: ?
    h                                   # PS: ?         HS: X';v;x
                                        # STORE_FAST/

                                        # JUMP 161
    b 161                               # JUMP/


:71
                                        # LOAD_FAST y
                                        # PS: ?         HS: ?;v;x?
    g                                   # PS: ?;v;x?    HS: ?;v;x?
    tL18                                # reset t flag
:L18
    s/.*;y;([^;]*)[^|]*$/\1;&/          # PS: x;?;v;x?  HS: ?;v;x?
    tL19
    s/.*/y/; b NameError                # branch to error if var undefined
:L19
    h                                   # PS: ?         HS: x;?;v;x?
                                        # LOAD_FAST/

                                        # LOAD_FAST x
                                        # PS: ?         HS: ?;v;x?
    g                                   # PS: ?;v;x?    HS: ?;v;x?
    tL20                                # reset t flag
:L20
    s/.*;x;([^;]*)[^|]*$/\1;&/          # PS: x;?;v;x?  HS: ?;v;x?
    tL21
    s/.*/x/; b NameError                # branch to error if var undefined
:L21
    h                                   # PS: ?         HS: x;?;v;x?
                                        # LOAD_FAST/

                                        # BINARY_SUBTRACT
                                        # PS: ?         HS: M;N;X
                                        # SWAP
                                        # PS: ?         HS: M;N;X
    x                                   # PS: M;N;X     HS: ?
    s/^([^;]*;)([^;]*;)/\2\1/           # PS: N;M;X     HS: ?
    x                                   # PS: ?         HS: N;M;X
                                        # SWAP/

                                        # POP2
                                        # PS: ?         HS: M;N;X
    g                                   # PS: M;N;X     HS: M;N;X
    s/^[^;]*;[^;]*;//                   # PS: X         HS: M;N;X
    x                                   # PS: M;N;X     HS: X
    s/(^[^;]*;[^;]*).*/\1/              # PS: M;N       HS: X
                                        # POP2/
                                        # PS: M;N       HS: X
                                        # CHECKINT2
                                        # PS: X;Y       HS: X;Y;Z
    /^[0-9]+;[0-9]+/!b NotPositiveInteger
                                        # CHECKINT2/

                                        # USUB

                                        # PS: M;N*
    s/[0-9]*;[0-9]*/0;&;/               # PS; 0;M;N;*
:L53                                    # PS: cR;Mm;Nn;*
    s/([0-9]*);([0-9]*)([0-9]);([0-9]*)([0-9]);/\3\5\1;\2;\4;/
                                        # PS: mncR;M;N;*
                                        # FULLSUB

    s/^(...)/\1;9876543210;0123456789;/
    s/^(..)0/\1/
    s/(.)(.)([0-9]*);[0-9]*\2([0-9]*);([0-9]*(\1[0-9]*));/\3\4\6\5;/
    s/.{10}(.)[0-9]{0,9}([0-9]{0,1})[0-9]*;/0\2\1;/
    /^0[0-9]([0-9]);/s//1\1;/
    s/;//
                                        # FULLSUB/
                                        # PS: c'rR;M;N;*
    /^[0-9]*;[0-9]*[0-9];[0-9]/ bL53    # more digits in M and N
    /^[0-9]*;;[0-9]/bL54                # more digits in N
    /^1[0-9]*;;;/bL54                   # same number of digits, but borrow
    /^1/{                               # if borrow,
    s/^1([0-9]*;[0-9]*);;/0\1;1;/       # move borrow to second operand
    bL53                                # and loop
    }
    s/^0([0-9]*);([0-9]*);;/\2\1/       # add remaining part of first operand
    s/^0*([0-9])/\1/                    # del leading 0
    bL55
:L54                                    # if invalid subtraction
    s/^[0-9]*;[0-9]*;[0-9]*;/NAN/       # PS: NAN*
:L55                                    # PS: M-N|NAN
                                        # USUB/
                                        # PS: R         HS: X
                                        # PUSH
                                        # PS: N         HS: X
    G                                   # PS: N\nX      HS: X
    s/\n/;/                             # PS: N;X       HS: X
    h                                   # PS: N;X       HS: N;X
    s/;.*//                             # PS: N         HS: N;X
                                        # PUSH/
                                        # PS: R         HS: R;X
                                        # BINARY_SUBTRACT/

                                        # UNARY_NEGATIVE
                                        # PS: ?         HS: N;X
    g                                   # PS: N;X       HS: N;X
    s/^-/!/                             # use marker to avoid another substitution
    s/^\+/-/                            #
    s/^[0-9]/-&/                        #
    s/^-0;/0;/                          # handle N = -0
    s/^!//                              # remove marker
    h                                   # PS: R;X       HS: R;X  R = -N
                                        # UNARY_NEGATIVE/

                                        # STORE_FAST r
                                        # PS: ?         HS: x;X
    g                                   # PS: x;X       HS: ?
    s/;r;[^;|]*([^|]*)$/\1/             # PS: x;X'      HS: ? (del ;var;val in PS)
    s/^([^;]*);(.*)/\2;r;\1/            # PS: X';v;x    HS: ?
    h                                   # PS: ?         HS: X';v;x
                                        # STORE_FAST/

                                        # JUMP 161
    b 161                               # JUMP/


:85
                                        # LOAD_FAST x
                                        # PS: ?         HS: ?;v;x?
    g                                   # PS: ?;v;x?    HS: ?;v;x?
    tL22                                # reset t flag
:L22
    s/.*;x;([^;]*)[^|]*$/\1;&/          # PS: x;?;v;x?  HS: ?;v;x?
    tL23
    s/.*/x/; b NameError                # branch to error if var undefined
:L23
    h                                   # PS: ?         HS: x;?;v;x?
                                        # LOAD_FAST/

                                        # UNARY_NEGATIVE
                                        # PS: ?         HS: N;X
    g                                   # PS: N;X       HS: N;X
    s/^-/!/                             # use marker to avoid another substitution
    s/^\+/-/                            #
    s/^[0-9]/-&/                        #
    s/^-0;/0;/                          # handle N = -0
    s/^!//                              # remove marker
    h                                   # PS: R;X       HS: R;X  R = -N
                                        # UNARY_NEGATIVE/

                                        # STORE_FAST x
                                        # PS: ?         HS: x;X
    g                                   # PS: x;X       HS: ?
    s/;x;[^;|]*([^|]*)$/\1/             # PS: x;X'      HS: ? (del ;var;val in PS)
    s/^([^;]*);(.*)/\2;x;\1/            # PS: X';v;x    HS: ?
    h                                   # PS: ?         HS: X';v;x
                                        # STORE_FAST/

                                        # LOAD_FAST y
                                        # PS: ?         HS: ?;v;x?
    g                                   # PS: ?;v;x?    HS: ?;v;x?
    tL24                                # reset t flag
:L24
    s/.*;y;([^;]*)[^|]*$/\1;&/          # PS: x;?;v;x?  HS: ?;v;x?
    tL25
    s/.*/y/; b NameError                # branch to error if var undefined
:L25
    h                                   # PS: ?         HS: x;?;v;x?
                                        # LOAD_FAST/

                                        # IS_POSITIVE
                                        # PS: ?         HS: N;X
    g                                   # PS: N;X       HS: N;X
    s/^[0-9+][^;]*/1/                   # PS: 1;X       HS: N;X  if pos
    s/^-[^;]+/0/                        # PS: 0;X       HS: N;X  if neg
    h                                   # PS: r;X       HS: r;X  r = 0 or 1
                                        # IS_POSITIVE/

                                        # POP_JUMP_IF_FALSE 143

                                        # POP
                                        # PS: ?         HS: N;X
    g                                   # PS: N;X       HS: N;X
    s/^[^;]*;//                         # PS: X         HS: N;X
    x                                   # PS: N;X       HS: X
    s/;.*//                             # PS: N         HS: X
                                        # POP/

    /^0$/b 143
                                        # POP_JUMP_IF_FALSE/

                                        # LOAD_FAST x
                                        # PS: ?         HS: ?;v;x?
    g                                   # PS: ?;v;x?    HS: ?;v;x?
    tL26                                # reset t flag
:L26
    s/.*;x;([^;]*)[^|]*$/\1;&/          # PS: x;?;v;x?  HS: ?;v;x?
    tL27
    s/.*/x/; b NameError                # branch to error if var undefined
:L27
    h                                   # PS: ?         HS: x;?;v;x?
                                        # LOAD_FAST/

                                        # LOAD_FAST y
                                        # PS: ?         HS: ?;v;x?
    g                                   # PS: ?;v;x?    HS: ?;v;x?
    tL28                                # reset t flag
:L28
    s/.*;y;([^;]*)[^|]*$/\1;&/          # PS: x;?;v;x?  HS: ?;v;x?
    tL29
    s/.*/y/; b NameError                # branch to error if var undefined
:L29
    h                                   # PS: ?         HS: x;?;v;x?
                                        # LOAD_FAST/

                                        # COMPARE_OP >

                                        # SWAP
                                        # PS: ?         HS: M;N;X
    x                                   # PS: M;N;X     HS: ?
    s/^([^;]*;)([^;]*;)/\2\1/           # PS: N;M;X     HS: ?
    x                                   # PS: ?         HS: N;M;X
                                        # SWAP/

                                        # POP2
                                        # PS: ?         HS: M;N;X
    g                                   # PS: M;N;X     HS: M;N;X
    s/^[^;]*;[^;]*;//                   # PS: X         HS: M;N;X
    x                                   # PS: M;N;X     HS: X
    s/(^[^;]*;[^;]*).*/\1/              # PS: M;N       HS: X
                                        # POP2/

                                        # CHECKINT2
                                        # PS: X;Y       HS: X;Y;Z
    /^[0-9]+;[0-9]+/!b NotPositiveInteger
                                        # CHECKINT2/

    s/$/;/
                                        # CMP
                                        # PS: X;Y;
    s/;/!;/g                            # PS: X!;Y!;
:L66                                    # PS: Xx!X';Yy!Y';
    s/([0-9])!([0-9]*;[0-9]*)([0-9])!/!\1\2!\3/# PS: X!xX';Y!yY';
    tL66
    /^!/!bL68
    /;!/!bL67
                                        # PS: !X;!Y;
    s/^!([0-9]*)([0-9]*);!\1([0-9]*);/\2;\3;/# strip identical leading digits
    /^;;$/ { s/.*/=/; bL69 }            # PS: = if all digits are equal

    s/$/9876543210/
    /^(.)[0-9]*;(.)[0-9]*;.*\1.*\2/bL68
:L67
    s/.*/</                             # PS: < if x < y
    bL69
:L68
    s/.*/>/                             # PS: > if x > y
:L69                                    # PS: <|=|>
                                        # CMP/

    y/<=>/001/
                                        # PUSH
                                        # PS: N         HS: X
    G                                   # PS: N\nX      HS: X
    s/\n/;/                             # PS: N;X       HS: X
    h                                   # PS: N;X       HS: N;X
    s/;.*//                             # PS: N         HS: N;X
                                        # PUSH/

                                        # COMPARE_OP/

                                        # POP_JUMP_IF_FALSE 130

                                        # POP
                                        # PS: ?         HS: N;X
    g                                   # PS: N;X       HS: N;X
    s/^[^;]*;//                         # PS: X         HS: N;X
    x                                   # PS: N;X       HS: X
    s/;.*//                             # PS: N         HS: X
                                        # POP/

    /^0$/b 130
                                        # POP_JUMP_IF_FALSE/

                                        # LOAD_FAST x
                                        # PS: ?         HS: ?;v;x?
    g                                   # PS: ?;v;x?    HS: ?;v;x?
    tL30                                # reset t flag
:L30
    s/.*;x;([^;]*)[^|]*$/\1;&/          # PS: x;?;v;x?  HS: ?;v;x?
    tL31
    s/.*/x/; b NameError                # branch to error if var undefined
:L31
    h                                   # PS: ?         HS: x;?;v;x?
                                        # LOAD_FAST/

                                        # LOAD_FAST y
                                        # PS: ?         HS: ?;v;x?
    g                                   # PS: ?;v;x?    HS: ?;v;x?
    tL32                                # reset t flag
:L32
    s/.*;y;([^;]*)[^|]*$/\1;&/          # PS: x;?;v;x?  HS: ?;v;x?
    tL33
    s/.*/y/; b NameError                # branch to error if var undefined
:L33
    h                                   # PS: ?         HS: x;?;v;x?
                                        # LOAD_FAST/

                                        # BINARY_SUBTRACT
                                        # PS: ?         HS: M;N;X
                                        # SWAP
                                        # PS: ?         HS: M;N;X
    x                                   # PS: M;N;X     HS: ?
    s/^([^;]*;)([^;]*;)/\2\1/           # PS: N;M;X     HS: ?
    x                                   # PS: ?         HS: N;M;X
                                        # SWAP/

                                        # POP2
                                        # PS: ?         HS: M;N;X
    g                                   # PS: M;N;X     HS: M;N;X
    s/^[^;]*;[^;]*;//                   # PS: X         HS: M;N;X
    x                                   # PS: M;N;X     HS: X
    s/(^[^;]*;[^;]*).*/\1/              # PS: M;N       HS: X
                                        # POP2/
                                        # PS: M;N       HS: X
                                        # CHECKINT2
                                        # PS: X;Y       HS: X;Y;Z
    /^[0-9]+;[0-9]+/!b NotPositiveInteger
                                        # CHECKINT2/

                                        # USUB

                                        # PS: M;N*
    s/[0-9]*;[0-9]*/0;&;/               # PS; 0;M;N;*
:L56                                    # PS: cR;Mm;Nn;*
    s/([0-9]*);([0-9]*)([0-9]);([0-9]*)([0-9]);/\3\5\1;\2;\4;/
                                        # PS: mncR;M;N;*
                                        # FULLSUB

    s/^(...)/\1;9876543210;0123456789;/
    s/^(..)0/\1/
    s/(.)(.)([0-9]*);[0-9]*\2([0-9]*);([0-9]*(\1[0-9]*));/\3\4\6\5;/
    s/.{10}(.)[0-9]{0,9}([0-9]{0,1})[0-9]*;/0\2\1;/
    /^0[0-9]([0-9]);/s//1\1;/
    s/;//
                                        # FULLSUB/
                                        # PS: c'rR;M;N;*
    /^[0-9]*;[0-9]*[0-9];[0-9]/ bL56    # more digits in M and N
    /^[0-9]*;;[0-9]/bL57                # more digits in N
    /^1[0-9]*;;;/bL57                   # same number of digits, but borrow
    /^1/{                               # if borrow,
    s/^1([0-9]*;[0-9]*);;/0\1;1;/       # move borrow to second operand
    bL56                                # and loop
    }
    s/^0([0-9]*);([0-9]*);;/\2\1/       # add remaining part of first operand
    s/^0*([0-9])/\1/                    # del leading 0
    bL58
:L57                                    # if invalid subtraction
    s/^[0-9]*;[0-9]*;[0-9]*;/NAN/       # PS: NAN*
:L58                                    # PS: M-N|NAN
                                        # USUB/
                                        # PS: R         HS: X
                                        # PUSH
                                        # PS: N         HS: X
    G                                   # PS: N\nX      HS: X
    s/\n/;/                             # PS: N;X       HS: X
    h                                   # PS: N;X       HS: N;X
    s/;.*//                             # PS: N         HS: N;X
                                        # PUSH/
                                        # PS: R         HS: R;X
                                        # BINARY_SUBTRACT/

                                        # UNARY_NEGATIVE
                                        # PS: ?         HS: N;X
    g                                   # PS: N;X       HS: N;X
    s/^-/!/                             # use marker to avoid another substitution
    s/^\+/-/                            #
    s/^[0-9]/-&/                        #
    s/^-0;/0;/                          # handle N = -0
    s/^!//                              # remove marker
    h                                   # PS: R;X       HS: R;X  R = -N
                                        # UNARY_NEGATIVE/

                                        # STORE_FAST r
                                        # PS: ?         HS: x;X
    g                                   # PS: x;X       HS: ?
    s/;r;[^;|]*([^|]*)$/\1/             # PS: x;X'      HS: ? (del ;var;val in PS)
    s/^([^;]*);(.*)/\2;r;\1/            # PS: X';v;x    HS: ?
    h                                   # PS: ?         HS: X';v;x
                                        # STORE_FAST/

                                        # JUMP 161
    b 161                               # JUMP/


:130
                                        # LOAD_FAST y
                                        # PS: ?         HS: ?;v;x?
    g                                   # PS: ?;v;x?    HS: ?;v;x?
    tL34                                # reset t flag
:L34
    s/.*;y;([^;]*)[^|]*$/\1;&/          # PS: x;?;v;x?  HS: ?;v;x?
    tL35
    s/.*/y/; b NameError                # branch to error if var undefined
:L35
    h                                   # PS: ?         HS: x;?;v;x?
                                        # LOAD_FAST/

                                        # LOAD_FAST x
                                        # PS: ?         HS: ?;v;x?
    g                                   # PS: ?;v;x?    HS: ?;v;x?
    tL36                                # reset t flag
:L36
    s/.*;x;([^;]*)[^|]*$/\1;&/          # PS: x;?;v;x?  HS: ?;v;x?
    tL37
    s/.*/x/; b NameError                # branch to error if var undefined
:L37
    h                                   # PS: ?         HS: x;?;v;x?
                                        # LOAD_FAST/

                                        # BINARY_SUBTRACT
                                        # PS: ?         HS: M;N;X
                                        # SWAP
                                        # PS: ?         HS: M;N;X
    x                                   # PS: M;N;X     HS: ?
    s/^([^;]*;)([^;]*;)/\2\1/           # PS: N;M;X     HS: ?
    x                                   # PS: ?         HS: N;M;X
                                        # SWAP/

                                        # POP2
                                        # PS: ?         HS: M;N;X
    g                                   # PS: M;N;X     HS: M;N;X
    s/^[^;]*;[^;]*;//                   # PS: X         HS: M;N;X
    x                                   # PS: M;N;X     HS: X
    s/(^[^;]*;[^;]*).*/\1/              # PS: M;N       HS: X
                                        # POP2/
                                        # PS: M;N       HS: X
                                        # CHECKINT2
                                        # PS: X;Y       HS: X;Y;Z
    /^[0-9]+;[0-9]+/!b NotPositiveInteger
                                        # CHECKINT2/

                                        # USUB

                                        # PS: M;N*
    s/[0-9]*;[0-9]*/0;&;/               # PS; 0;M;N;*
:L59                                    # PS: cR;Mm;Nn;*
    s/([0-9]*);([0-9]*)([0-9]);([0-9]*)([0-9]);/\3\5\1;\2;\4;/
                                        # PS: mncR;M;N;*
                                        # FULLSUB

    s/^(...)/\1;9876543210;0123456789;/
    s/^(..)0/\1/
    s/(.)(.)([0-9]*);[0-9]*\2([0-9]*);([0-9]*(\1[0-9]*));/\3\4\6\5;/
    s/.{10}(.)[0-9]{0,9}([0-9]{0,1})[0-9]*;/0\2\1;/
    /^0[0-9]([0-9]);/s//1\1;/
    s/;//
                                        # FULLSUB/
                                        # PS: c'rR;M;N;*
    /^[0-9]*;[0-9]*[0-9];[0-9]/ bL59    # more digits in M and N
    /^[0-9]*;;[0-9]/bL60                # more digits in N
    /^1[0-9]*;;;/bL60                   # same number of digits, but borrow
    /^1/{                               # if borrow,
    s/^1([0-9]*;[0-9]*);;/0\1;1;/       # move borrow to second operand
    bL59                                # and loop
    }
    s/^0([0-9]*);([0-9]*);;/\2\1/       # add remaining part of first operand
    s/^0*([0-9])/\1/                    # del leading 0
    bL61
:L60                                    # if invalid subtraction
    s/^[0-9]*;[0-9]*;[0-9]*;/NAN/       # PS: NAN*
:L61                                    # PS: M-N|NAN
                                        # USUB/
                                        # PS: R         HS: X
                                        # PUSH
                                        # PS: N         HS: X
    G                                   # PS: N\nX      HS: X
    s/\n/;/                             # PS: N;X       HS: X
    h                                   # PS: N;X       HS: N;X
    s/;.*//                             # PS: N         HS: N;X
                                        # PUSH/
                                        # PS: R         HS: R;X
                                        # BINARY_SUBTRACT/

                                        # STORE_FAST r
                                        # PS: ?         HS: x;X
    g                                   # PS: x;X       HS: ?
    s/;r;[^;|]*([^|]*)$/\1/             # PS: x;X'      HS: ? (del ;var;val in PS)
    s/^([^;]*);(.*)/\2;r;\1/            # PS: X';v;x    HS: ?
    h                                   # PS: ?         HS: X';v;x
                                        # STORE_FAST/

                                        # JUMP 161
    b 161                               # JUMP/


:143
                                        # LOAD_FAST y
                                        # PS: ?         HS: ?;v;x?
    g                                   # PS: ?;v;x?    HS: ?;v;x?
    tL38                                # reset t flag
:L38
    s/.*;y;([^;]*)[^|]*$/\1;&/          # PS: x;?;v;x?  HS: ?;v;x?
    tL39
    s/.*/y/; b NameError                # branch to error if var undefined
:L39
    h                                   # PS: ?         HS: x;?;v;x?
                                        # LOAD_FAST/

                                        # UNARY_NEGATIVE
                                        # PS: ?         HS: N;X
    g                                   # PS: N;X       HS: N;X
    s/^-/!/                             # use marker to avoid another substitution
    s/^\+/-/                            #
    s/^[0-9]/-&/                        #
    s/^-0;/0;/                          # handle N = -0
    s/^!//                              # remove marker
    h                                   # PS: R;X       HS: R;X  R = -N
                                        # UNARY_NEGATIVE/

                                        # STORE_FAST y
                                        # PS: ?         HS: x;X
    g                                   # PS: x;X       HS: ?
    s/;y;[^;|]*([^|]*)$/\1/             # PS: x;X'      HS: ? (del ;var;val in PS)
    s/^([^;]*);(.*)/\2;y;\1/            # PS: X';v;x    HS: ?
    h                                   # PS: ?         HS: X';v;x
                                        # STORE_FAST/

                                        # LOAD_FAST x
                                        # PS: ?         HS: ?;v;x?
    g                                   # PS: ?;v;x?    HS: ?;v;x?
    tL40                                # reset t flag
:L40
    s/.*;x;([^;]*)[^|]*$/\1;&/          # PS: x;?;v;x?  HS: ?;v;x?
    tL41
    s/.*/x/; b NameError                # branch to error if var undefined
:L41
    h                                   # PS: ?         HS: x;?;v;x?
                                        # LOAD_FAST/

                                        # LOAD_FAST y
                                        # PS: ?         HS: ?;v;x?
    g                                   # PS: ?;v;x?    HS: ?;v;x?
    tL42                                # reset t flag
:L42
    s/.*;y;([^;]*)[^|]*$/\1;&/          # PS: x;?;v;x?  HS: ?;v;x?
    tL43
    s/.*/y/; b NameError                # branch to error if var undefined
:L43
    h                                   # PS: ?         HS: x;?;v;x?
                                        # LOAD_FAST/

                                        # BINARY_ADD
                                        # PS: ?         HS: M;N;X
                                        # POP2
                                        # PS: ?         HS: M;N;X
    g                                   # PS: M;N;X     HS: M;N;X
    s/^[^;]*;[^;]*;//                   # PS: X         HS: M;N;X
    x                                   # PS: M;N;X     HS: X
    s/(^[^;]*;[^;]*).*/\1/              # PS: M;N       HS: X
                                        # POP2/
                                        # PS: M;N       HS: X
                                        # CHECKINT2
                                        # PS: X;Y       HS: X;Y;Z
    /^[0-9]+;[0-9]+/!b NotPositiveInteger
                                        # CHECKINT2/

                                        # UADD

                                        # PS: M;N*
    s/[0-9]*;[0-9]*/0;&;/               # PS; 0;M;N;*
:L48                                    # PS: cR;Mm;Nn;*
    s/^([0-9]*);([0-9]*)([0-9]);([0-9]*)([0-9])/\3\5\1;\2;\4/
                                        # PS: mncR;M;N;*
                                        # FULLADD

    s/^(...)/\1;9876543210;9876543210;/
    s/^(..)0/\1/
    s/(.)(.)([0-9])*;([0-9]*\1([0-9]*));[0-9]*(\2[0-9]*);/\3\5\6\4;/
    s/.{10}(.)[0-9]{0,9}([0-9]{0,1})[0-9]*;/0\2\1;/
    /^0[0-9]([0-9]);/s//1\1;/
    s/;//
                                        # FULLADD/
                                        # PS: abR;M;N;*
    /^[0-9]*;[0-9]*[0-9];[0-9]/bL48     # more digits in M and N
    /^[0-9]*;;;/{                       # no more digits in M and N
    s/;;;//
    s/^0//
    bL49
    }
    /^1/{
    s/;;/;0;/
    bL48
    }
    s/^0([0-9]*);([0-9]*);([0-9]*);/\2\3\1/
:L49                                    # PS: R*
                                        # UADD/
                                        # PS: R         HS: X
                                        # PUSH
                                        # PS: N         HS: X
    G                                   # PS: N\nX      HS: X
    s/\n/;/                             # PS: N;X       HS: X
    h                                   # PS: N;X       HS: N;X
    s/;.*//                             # PS: N         HS: N;X
                                        # PUSH/
                                        # PS: R         HS: R;X
                                        # BINARY_ADD/

                                        # UNARY_NEGATIVE
                                        # PS: ?         HS: N;X
    g                                   # PS: N;X       HS: N;X
    s/^-/!/                             # use marker to avoid another substitution
    s/^\+/-/                            #
    s/^[0-9]/-&/                        #
    s/^-0;/0;/                          # handle N = -0
    s/^!//                              # remove marker
    h                                   # PS: R;X       HS: R;X  R = -N
                                        # UNARY_NEGATIVE/

                                        # STORE_FAST r
                                        # PS: ?         HS: x;X
    g                                   # PS: x;X       HS: ?
    s/;r;[^;|]*([^|]*)$/\1/             # PS: x;X'      HS: ? (del ;var;val in PS)
    s/^([^;]*);(.*)/\2;r;\1/            # PS: X';v;x    HS: ?
    h                                   # PS: ?         HS: X';v;x
                                        # STORE_FAST/


:161
                                        # LOAD_FAST r
                                        # PS: ?         HS: ?;v;x?
    g                                   # PS: ?;v;x?    HS: ?;v;x?
    tL44                                # reset t flag
:L44
    s/.*;r;([^;]*)[^|]*$/\1;&/          # PS: x;?;v;x?  HS: ?;v;x?
    tL45
    s/.*/r/; b NameError                # branch to error if var undefined
:L45
    h                                   # PS: ?         HS: x;?;v;x?
                                        # LOAD_FAST/

                                        # POP_CONTEXT

    x
    s/[|][^|]*$//
    x
                                        # POP_CONTEXT/

                                        # RETURN_VALUE
                                        # PS: ?         HS: R;label;X
                                        # SWAP
                                        # PS: ?         HS: M;N;X
    x                                   # PS: M;N;X     HS: ?
    s/^([^;]*;)([^;]*;)/\2\1/           # PS: N;M;X     HS: ?
    x                                   # PS: ?         HS: N;M;X
                                        # SWAP/
                                        # PS: ?         HS: label;R;X
                                        # POP
                                        # PS: ?         HS: N;X
    g                                   # PS: N;X       HS: N;X
    s/^[^;]*;//                         # PS: X         HS: N;X
    x                                   # PS: N;X       HS: X
    s/;.*//                             # PS: N         HS: X
                                        # POP/
                                        # PS: label     HS: R;X
    b return
                                        # RETURN_VALUE/


:print.func
                                        # PRINT_ITEMS
                                        # PS: ?         HS: ~~~;C;B;A;X
    g
:L70                                    # PS: C ~~;B;A;X
    s/([^~]*)~(~*);([^;]*);/\3 \1\2;/
                                        # PS: A B ~;C;X
    tL70
    s/ ;/;/                             # remove extra space
                                        # PS: A B C ;X
    h                                   # PS: A B C ;X  HS: A B C ;X
                                        # POP
                                        # PS: ?         HS: N;X
    g                                   # PS: N;X       HS: N;X
    s/^[^;]*;//                         # PS: X         HS: N;X
    x                                   # PS: N;X       HS: X
    s/;.*//                             # PS: N         HS: X
                                        # POP/
                                        # PS: A B C     HS: X
    p
                                        # PRINT_ITEMS/

                                        # PRINT_NEWLINE
                                        # PRINT_NEWLINE/

                                        # LOAD_CONST 0
                                        # PS: ?         HS: X
    g                                   # PS: X         HS: X
    s/^/0;/                             # PS: 0;X   HS: X
    h                                   # PS: 0;X   HS: 0;X
                                        # LOAD_CONST/

                                        # RETURN_VALUE
                                        # PS: ?         HS: R;label;X
                                        # SWAP
                                        # PS: ?         HS: M;N;X
    x                                   # PS: M;N;X     HS: ?
    s/^([^;]*;)([^;]*;)/\2\1/           # PS: N;M;X     HS: ?
    x                                   # PS: ?         HS: N;M;X
                                        # SWAP/
                                        # PS: ?         HS: label;R;X
                                        # POP
                                        # PS: ?         HS: N;X
    g                                   # PS: N;X       HS: N;X
    s/^[^;]*;//                         # PS: X         HS: N;X
    x                                   # PS: N;X       HS: X
    s/;.*//                             # PS: N         HS: X
                                        # POP/
                                        # PS: label     HS: R;X
    b return
                                        # RETURN_VALUE/

:call_function
                                        # PS: label
    t.L72                               # t to next line to reset t flag
:.L72                                   # PS: label
    s/^print.func$//;t print.func
    s/^signed_add.func$//;t signed_add.func
    s/^print.func$//;t print.func
    b UnknownLabel
:return
                                        # PS: label
    t.L73                               # t to next line to reset t flag
:.L73                                   # PS: label
    s/^R0$//;t R0
    s/^R1$//;t R1
    s/^end_of_script$//;t end_of_script
    b UnknownLabel
