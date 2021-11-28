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

**Unused ASCII Characters**
* "
* `
* &
* |
