import unittest
from PySpice.Spice.EBNFExpressionParser import ExpressionParser
from PySpice.Tools.StringTools import str_spice
from PySpice.Spice.Expressions import Expression
import os

data = {
    "1": "1",
    "+1": "1",
    "-1": "-1",
    "1.": "1",
    "+1.": "1",
    "-1.": "-1",
    ".1": "0.1",
    "-.1": "-0.1",
    "+.1": "0.1",
    ".1E0": "0.1",
    "-.1E1": "-1",
    "+.1E1": "1",
    "1.E0": "1",
    "-1.E-1": "-0.1",
    "+1.E-1": "0.1",
    "1.23": "1.23",
    "-1.23": "-1.23",
    "+1.23": "1.23",
    "1.23E1": "12.3",
    "1.23E-1": "0.123",
    "1Hz": "1hz",
    "2.0kohm": "2kohm",
    "1.0Meg": "1meg",
    "1.0MegOhm": "1megohm",
    "1.0µOhm": "1uohm",
    "True?1:0": "if(true, 1, 0)",
    "False?1:0": "if(false, 1, 0)",
    "a + b": "a + b",
    "a - b": "a - b",
    "(a + b)": "a + b",
    "(a - b)": "a - b",
    "a * b": "a * b",
    "a / b": "a / b",
    "{(a * b)}": "a * b",
    "{(a / b)}": "a / b",
    "{(a / b) * c}": "(a / b) * c",
    "{if(1<2,1,0)}": "if(1 < 2, 1, 0)",
    "{if((1<2),(1),(0))}": "if(1 < 2, 1, 0)",
    "{2<=1?1:0}": "if(2 <= 1, 1, 0)",
    "{a + (b + c)}": "a + (b + c)",
    "{(a + b) + c}": "(a + b) + c",
    "{1}": "1",
    "{1+2}": "1 + 2",
    "{(1+2)}": "1 + 2",
    "{(1+2) + 3}": "(1 + 2) + 3",
    "{(1+2) * 3}": "(1 + 2) * 3",
    "{(1+2) * (3 + 7)}": "(1 + 2) * (3 + 7)",
    "{(1+2) * -(3 + 7)}": "(1 + 2) * -(3 + 7)",
    "{(1+a) * -(b + 7)}": "(1 + a) * -(b + 7)",
    "{(1+sin(3.14)) * -(3 + 7)}": "(1 + sin(3.14)) * -(3 + 7)",
    "{(1+v(a)) * -(3 + 7)}": "(1 + v(a)) * -(3 + 7)",
    "{atan2(asin(b), ln(c))}": "atan2(asin(b), ln(c))",
    "{atan2(asin(b) - 7, ln(c) + 5)}": "atan2(asin(b) - 7, ln(c) + 5)",
    "{ddx(asin, ln(c) + 5)}": "ddx(asin, ln(c) + 5)",
    "{if(True, 1, 2)}": "if(true, 1, 2)",
    "{if(2 < 3, 1, 2)}": "if(2 < 3, 1, 2)",
    "{if((2 < 3) | False , 1, 2)}": "if((2 < 3) | false, 1, 2)",
    "{(2 < 3) | False ? True ? 3: 4: 2}": "if((2 < 3) | false, if(true, 3, 4), 2)",
    "{(2 < 3) | False ? True ? 3: sin(4): 2}": "if((2 < 3) | false, if(true, 3, sin(4)), 2)",
    "{(2 < 3) | False ? (True ? 3: sin(4)): 2}": "if((2 < 3) | false, if(true, 3, sin(4)), 2)",
    "{(2 < 3) & ( False | True) ? (True ? 3: sin(4)): 2}": "if((2 < 3) & (false | true), if(true, 3, sin(4)), 2)",
    "{~(2 < 3) & ~( False | True) ? (True ? 3: sin(4)): 2}": "if(~(2 < 3) & ~(false | true), if(true, 3, sin(4)), 2)",
    "{limit(3, 2, a)}": "limit(3, 2, a)",
    "{limit(3, 2, a)}": "limit(3, 2, a)"
}

class TestExpressionParser(unittest.TestCase):
    def test_parser(self):
        # ExpressionParser._regenerate()
        for case, expr in data.items():
            expr_i = ExpressionParser.parse(source=case)
            case_i = str_spice(expr_i)
            if expr != case_i:
                expr_i = ExpressionParser.parse(source=case)
                case_i = str_spice(expr_i)
            self.assertEqual(expr, case_i)

if __name__ == '__main__':
    unittest.main()
