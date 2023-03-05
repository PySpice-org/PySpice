import unittest
from PySpice.Spice.EBNFExpressionParser import ExpressionParser
import os

data = [
    "{True?1:0}",
    "{False?1:0}",
    "{a + b}",
    "{a - b}",
    "{(a + b)}",
    "{(a - b)}",
    "{a * b}",
    "{a / b}",
    "{(a * b)}",
    "{(a / b)}",
    "{(a / b) * c}",
    "{if(1<2,1,0)}",
    "{if((1<2),(1),(0))}",
    "{2<=1?1:0}",
    "{a + (b + c)}",
    "{(a + b) + c}",
    "1",
    "{1}",
    "{1+2}",
    "{(1+2)}",
    "{(1+2) + 3}",
    "{(1+2) * 3}",
    "{(1+2) * (3 + 7)}",
    "{(1+2) * -(3 + 7)}",
    "{(1+a) * -(b + 7)}",
    "{(1+sin(3.14)) * -(3 + 7)}",
    "{(1+v(a)) * -(3 + 7)}",
    "{atan2(asin(b), ln(c))}",
    "{atan2(asin(b) - 7, ln(c) + 5)}",
    "{ddx(asin, ln(c) + 5)}",
    "{if(True, 1, 2)}",
    "{if(2 < 3, 1, 2)}",
    "{if((2 < 3) | False , 1, 2)}",
    "{(2 < 3) | False ? True ? 3: 4: 2}",
    "{(2 < 3) | False ? True ? 3: sin(4): 2}",
    "{(2 < 3) | False ? (True ? 3: sin(4)): 2}",
    "{(2 < 3) & ( False | True) ? (True ? 3: sin(4)): 2}",
    "{~(2 < 3) & ~( False | True) ? (True ? 3: sin(4)): 2}",
    "{limit(3, 2, a)}",
    "{limit(3, 2, a)}"
]

class TestExpressionParser(unittest.TestCase):
    def test_parser(self):
        #ExpressionParser._regenerate()
        for case in data:
            expr_i = ExpressionParser.parse(source=case)
            case_i = "{%s}" % expr_i
            expr_f = ExpressionParser.parse(source=case_i)
            self.assertEqual("{%s}" % expr_f, case_i)

if __name__ == '__main__':
    unittest.main()
