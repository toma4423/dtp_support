import pytest
from pattern5 import format_name_5chars_rule
from pattern7 import format_name_7chars_rule

# --- 5字取りのテスト ---
@pytest.mark.parametrize("surname, given_name, expected", [
    ("佐藤", "健", "佐藤　　健"),      # (2, 1) -> 2+2+1=5
    ("田中", "二朗", "田中　二朗"),    # (2, 2) -> 2+1+2=5
    ("木村", "一郎", "木村　一郎"),    # (2, 2) -> 2+1+2=5
    ("森", "健太", "森　　健太"),      # (1, 2) -> 1+2+2=5
    ("高橋", "愛", "高橋　　愛"),      # (2, 1) -> 2+2+1=5
    ("林", "愛", "林　　　愛"),        # (1, 1) -> 1+3+1=5
    ("高橋", "浩一郎", "高橋浩一郎"),  # (2, 3) -> 合計5なのでそのまま
    ("小比類巻", "健", "小比類巻健"),  # (4, 1) -> 苗字4以上なのでそのまま
    ("田中", "慎一郎", "田中慎一郎"),  # (2, 3) -> 合計5なのでそのまま
])
def test_format_5chars(surname, given_name, expected):
    assert format_name_5chars_rule(surname, given_name) == expected


# --- 7字取りのテスト ---
@pytest.mark.parametrize("surname, given_name, expected", [
    ("佐藤", "健", "佐　藤　　　健"),      # (2, 1) -> 1+1+1+3+1=7
    ("佐藤", "二朗", "佐　藤　二　朗"),    # (2, 2) -> 1+1+1+1+1+1+1=7
    ("高橋", "健二郎", "高橋　健二郎"),    # (2, 3) -> 1+1+1+1+3=7 (佐藤の場合: 佐　藤　健二郎?)
    ("森", "二朗", "森　　　二　朗"),      # (1, 2) -> 1+3+1+1+1=7
    ("勅使河原", "健", "勅使河原　　健"),  # (4, 1) -> 4+2+1=7
    ("天王寺谷", "二", "天王寺谷　二"),    # (5, 1) -> 5+1+1=7
    ("林", "一郎太", "林　　　一郎太"),    # (1, 3) -> 1+3+3=7
    ("高橋", "美智子", "高橋　美智子"),    # (2, 3) -> 2+1+3=6? いえ、(2, 3)は 佐　藤　名名名 だったので 高　橋　美智子?
])
def test_format_7chars(surname, given_name, expected):
    # (2, 3) の期待値を再確認: 佐　藤　名名名
    if len(surname) == 2 and len(given_name) == 3:
        expected = f"{surname[0]}　{surname[1]}　{given_name}"
    assert format_name_7chars_rule(surname, given_name) == expected
