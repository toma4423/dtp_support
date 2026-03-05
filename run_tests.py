import unittest
from pattern5 import format_name_5chars_rule
from pattern7 import format_name_7chars_rule

class TestDTPLogic(unittest.TestCase):
    def test_pattern5(self):
        cases = [
            ("佐藤", "健", "佐藤　　健"),      # 2+2+1=5
            ("田中", "二朗", "田中　二朗"),    # 2+1+2=5
            ("森", "健太", "森　　健太"),      # 1+2+2=5
            ("林", "愛", "林　　　愛"),        # 1+3+1=5
            ("高橋", "浩一郎", "高橋浩一郎"),  # 5以上はそのまま
            ("小比類巻", "健", "小比類巻健"),  # 4文字以上はそのまま
        ]
        for s, g, expected in cases:
            with self.subTest(s=s, g=g):
                self.assertEqual(format_name_5chars_rule(s, g), expected)

    def test_pattern7(self):
        cases = [
            ("佐藤", "健", "佐　藤　　　健"),      # (2, 1) -> 7字
            ("佐藤", "二朗", "佐　藤　二　朗"),    # (2, 2) -> 7字
            ("高橋", "健二郎", "高　橋　健二郎"),  # (2, 3) -> 7字
            ("森", "二朗", "森　　　二　朗"),      # (1, 2) -> 7字
            ("勅使河原", "健", "勅使河原　　健"),  # (4, 1) -> 7字
            ("天王寺谷", "二", "天王寺谷　　二"),  # (4, 1) -> 4+2+1=7字 (天王寺谷は4文字)
            ("上久木田", "二", "上久木田　　二"),  # (4, 1) -> 4+2+1=7字
            ("林", "一郎太", "林　　　一郎太"),    # (1, 3) -> 7字
        ]
        for s, g, expected in cases:
            with self.subTest(s=s, g=g):
                self.assertEqual(format_name_7chars_rule(s, g), expected)

if __name__ == "__main__":
    unittest.main()
