# Intermediate Code Generator

A Python-based Compiler Design project that converts arithmetic
expressions into **Three Address Code (TAC)** and displays their
corresponding **Quadruple** and **Triple** representations.

## Project Overview

The Intermediate Code Generator demonstrates the intermediate code
generation phase of a compiler. It accepts an arithmetic expression as
input, analyzes its structure, and generates a sequence of intermediate
instructions using temporary variables.

The project uses **Syntax Directed Translation** to generate
intermediate code while preserving the correct order of arithmetic
operations.

## Objectives

-   Convert high-level arithmetic expressions into an intermediate
    representation.
-   Generate Three Address Code (TAC) using temporary variables.
-   Represent generated instructions using Quadruples and Triples.
-   Demonstrate the role of syntax-directed translation in compiler
    design.
-   Help users understand how source expressions are transformed into
    structured intermediate code.

## Features

-   **Expression Input:** Accepts arithmetic expressions from the user.
-   **Lexical Analysis:** Breaks the input into tokens such as
    identifiers, operators, and operands.
-   **Syntax Analysis:** Analyzes the expression structure and builds a
    parse tree or Abstract Syntax Tree (AST).
-   **Syntax Directed Translation:** Applies semantic rules to generate
    intermediate instructions.
-   **TAC Generation:** Produces Three Address Code using temporary
    variables.
-   **Quadruple Representation:** Displays instructions in a table
    containing the operator, arguments, and result.
-   **Triple Representation:** Displays instructions using indexed
    intermediate results.
-   **Structured Output:** Presents the generated representations in an
    easy-to-understand format.

## Technology Stack

-   **Programming Language:** Python
-   **Core Concepts:** Compiler Design, Lexical Analysis, Syntax
    Analysis, Syntax Directed Translation, Intermediate Code Generation

## Project Workflow

1.  **Input Expression** -- The user enters an arithmetic expression.
2.  **Lexical Analysis** -- The expression is converted into tokens.
3.  **Syntax Analysis** -- Tokens are analyzed and a parse tree / AST is
    constructed.
4.  **Syntax Directed Translation** -- Translation rules are applied to
    the expression.
5.  **Three Address Code Generation** -- Intermediate instructions are
    generated using temporary variables.
6.  **Quadruple Generation** -- TAC instructions are represented as
    quadruples.
7.  **Triple Generation** -- TAC instructions are represented as
    triples.
8.  **Output Display** -- TAC, Quadruple, and Triple representations are
    displayed.

## Example

For the arithmetic expression:

``` text
a + b * c
```

Multiplication is performed before addition.

### Three Address Code (TAC)

``` text
t1 = b * c
t2 = a + t1
```

### Quadruple Representation

    No.  Operator   Arg1   Arg2   Result
  ----- ---------- ------ ------ --------
      1    `*`      `b`    `c`     `t1`
      2    `+`      `a`    `t1`    `t2`

### Triple Representation

    No.  Operator   Arg1   Arg2
  ----- ---------- ------ -------
      0    `*`      `b`     `c`
      1    `+`      `a`    `(0)`

*The example illustrates the intended output format.*

## Expected Outcome

The completed system will allow users to enter an arithmetic expression
and automatically generate its corresponding TAC, Quadruple
representation, and Triple representation. It provides a practical
demonstration of how high-level expressions are transformed into a
structured intermediate form during compiler design.

## Future Enhancements

-   Support for more complex arithmetic expressions.
-   Support for additional operators.
-   Support for other intermediate-code representations.

## Project Team

  Name                    University ID
  --------------------- ---------------
  B. Chetna Chaudhary        2420030098
  Aashna Begum               2420030647
  M. Asleshitha              2420030740
  K. Vasavi                  2420030785

**Project Guide:** E. Uma Shankari

## Academic Details

-   **Course:** Project Evaluation (24CS2235F)
-   **Academic Year:** 2026--2027
-   **Department:** Computer Science and Engineering
-   **Institution:** Koneru Lakshmaiah Education Foundation (KL
    University)

------------------------------------------------------------------------

*This project is developed for academic learning as part of the Compiler
Design domain.*
