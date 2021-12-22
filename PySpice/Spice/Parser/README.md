# Input file structure

The circuit to be analyzed is described to ngspice by a set of element instance lines, which
define the circuit topology and element instance values, and a set of control lines, which
define the model parameters and the run controls.

All lines are assembled in an input file to be read by ngspice.

The input file will be scanned for valid utf-8 characters.

Two lines are essential:
* The first line in the input file must be the title, which is the only comment line that
does not need any special character in the first place.
* The last line must be .end, plus a newline delimiter.

The order of the remaining lines is alomost arbitrary (except, of course, that continuation
lines must immediately follow the line being continued, .subckt ... .ends, .if ... .endif,
or .control ... .endc have to enclose their specific lines).

Leading white spaces in a line are ignored, as well as empty lines.

The lines described in sections 2.1 to 2.12 are typically used in the core of the input file,
outside of a `.control` section.

The `.include includefile` line may be placed anywhere in the input file. The contents of includefile
will be inserted exactly in place of the .include line.

# Continuation lines

General Form:

```
< any command >
+ < continuation of any command > ; some comment
+ < further continuation of any command >
```

If input lines get overly long, they may be split into two or more lines (e.g. for better
readability). Internally they will be merged into a single line.

* Each follow-up line starts with charachter `+ ` plus additional space.
* Follw-up lines have to follow immediately after each other.
* End-of-line comments will be ignored.
* The following lines do not allow using continuation lines: .title, .lib, and .include.

# Naming conventions

Fields on a line are separated by one or more blanks, a comma, an equal (=) sign, or a left
or right parenthesis; extra spaces are ignored.

A line may be continued by entering a ‘+’ (plus) in column 1 of the following line; ngspice
continues reading beginning with column 2.

A name field must begin with a letter (A through Z) and cannot contain any delimiters.

A number field may be an integer field (12, -44), a floating point field (3.14159), either
an integer or floating point number followed by an integer exponent (1e-14, 2.65e3), or
either an integer or a floating point number followed by one of the following scale factors:

| Suffix | Name  | Factor       |
|--------|-------|--------------|
|  T     | Tera  | 10**12       |
|  G     | Giga  | 10**9        |
|  Meg   | Mega  | 10**6        |
|  K     | Kilo  | 10**3        |
|  mil   | Mil   | 25.4 ×10**−6 |
|  m     | milli | 10**−3       |
|  u     | micro | 10**−6       |
|  n     | nano  | 10**−9       |
|  p     | pico  | 10**−12      |
|  f     | femto | 10**−15      |

Letters immediately following a number that are not scale factors are ignored, and letters
immediately following a scale factor are ignored. Hence, 10, 10V, 10Volts, and 10Hz all represent
the same number, and M, MA, MSec, and MMhos all represent the same scale factor.

Note that 1000, 1000.0, 1000Hz, 1e3, 1.0e3, 1kHz, and 1k all represent the same number.

Note that ‘M’ or ‘m’ denote ‘milli’, i.e. 10−3. Suffix meg has to be used for 106.

If compatibility mode LT is set, ngspice will accept the RKM notation for entering
resistance or capacitance values, e.g. 2K7 or 100R.

Nodes names may be arbitrary character strings and are case insensitive, if ngspice is used in
batch mode. If in interactive or control mode, node names may either be plain numbers or arbitrary
character strings, not starting with a number.

# Syntax of expressions

| Operator | Alias | Precedence | Description      |
|----------|-------|------------|------------------|
|   -      |       |   1        | unary -          |
|   !      |       |   1        | unary not        |
|   **     |   ^   |   2        | power, like pwr  |
|   *      |       |   3        | multiply         |
|   /      |       |   3        | divide           |
|   %      |       |   3        | modulo           |
|   \      |       |   3        | integer divide   |
|   +      |       |   4        | add              |
|   -      |       |   4        | subtract         |
|   ==     |       |   5        | equality         |
|   !=     |   <>  |   5        | non-equal        |
|   <=     |       |   5        | less or equal    |
|   >=     |       |   5        | greater or equal |
|   <      |       |   5        | less than        |
|   >      |       |   5        | greater than     |
|   &&     |       |   6        | boolean and      |
|   ||     |       |   7        | boolean or       |
|   c?x:y  |       |   8        | ternary operator |

* Node voltages may be saved by giving the `nodename` or `v(nodename)`.
* Currents through an independent voltage source are given by `i(sourcename)` or `sourcename#branch`.
* Internal device data are accepted as `@dev[param]`

# Spice Tokens

| Token |                                                   |
|-------|---------------------------------------------------|
| -     | unary - and subtract                              |
| !     | unary not                                         |
| **    | power                                             |
| ^     | ** alias                                          |
| /     | divide                                            |
| %     | modulo                                            |
| \     | integer divide                                    |
| +     | add                                               |
| ==    | equality                                          |
| !=    | non-equal                                         |
| <=    | less or equal                                     |
| >=    | greater or equal                                  |
| <     | less than                                         |
| >     | greater than                                      |
| &&    | boolean and                                       |
| ||    | boolean or                                        |
| ?     | ternary operator                                  |
| :     | ternary operator                                  |
| ;     | end-of-line comment                               |
| $     | end-of-line comment                               |
| ()    | math ()                                           |
| {}    | brass expression                                  |
| []    | array                                             |
| '     | expression delimiter                              |
| ,     | math function parameter delimiter                 |
| =     | to set parameter by name                          |
| #     | branch current `sourcename#branch`                |
| @     | internal parameter `@dev[param]`                  |
| ~     | XSpice invert signal                              |
| "     | string                                            |

**Unused ASCII Characters**
* `
* &
* |

# Title

The title line must be the first in the input file. Its contents are printed verbatim as the
heading for each section of output.

As an alternative, you may place a `.TITLE <any title>` line anywhere in your input deck. The first
line of your input deck will be overridden by the contents of this line following the `.TITLE`
statement.

# XSpice

Square brackets `[]` are used to enclose vector input nodes. In addition, these brackets
are used to delineate vectors of parameters.

The literal string `null`, when included in a node list, is interpreted as no connection at
that input to the model. `Null` is not allowed as the name of a model’s input or output if
the model only has one input or one output. Also, `null` should only be used to indicate a
missing connection for a code model; use on other XSPICE component is not interpreted
as a missing connection, but will be interpreted as an actual node name.

The tilde, `~`, when prepended to a digital node name, specifies that the logical value of
that node be inverted prior to being passed to the code model. This allows for simple
inversion of input and output polarities of a digital model in order to handle logically
equivalent cases and others that frequently arise in digital system design.

**Port Type Modifiers**

The specification `%v` preceding the input and output node numbers indicate that the inputs to the model should be single-ended voltage
values, e.g. `a1 %v(1) %v(2) amp`.

| Modifier | Interpretation |
|----------|----------------|
| %v       | represents a single-ended voltage port - one node name or number is expected for each port. |
| %i       | represents a single-ended current port - one node name or number is expected for each port. |
| %g       | represents a single-ended voltage-input, current-output (VCCS) port - one node name or number is expected for each port. |
|          | This type of port is automatically an input/output. |
| %h       | represents a single-ended current-input, voltage-output (CCVS) port - one node name or number is expected for each port. |
|          | This type of port is automatically an input/output. |
| %d       | represents a digital port - one node name or number is expected for each port. This type of port may be either an input or an output. |
| %vnam    | represents the name of a voltage source, the current through which is taken as an input. |
|          | This notation is provided primarily in order to allow models defined using SPICE2G6 syntax to operate properly in XSPICE. |
| %vd      | represents a differential voltage port - two node names or numbers are expected for each port. |
| %id      | represents a differential current port - two node names or numbers are expected for each port. |
| %gd      | represents a differential VCCS port - two node names or numbers are expected for each port. |
| %hd      | represents a differential CCVS port - two node names or numbers are expected for each port. |
