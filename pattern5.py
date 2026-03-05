"""
5字取りルール実装モジュール

このモジュールは、5字取りルールに従って日本語氏名を整形する機能を提供します。
"""

from typing import Dict, Tuple


def format_name_5chars_rule(surname: str, given_name: str) -> str:
    """
    5字取りルールに従って氏名を整形する関数
    """
    surname_len = len(surname)
    given_name_len = len(given_name)
    total_len = surname_len + given_name_len

    # 基本ルール：合計5文字以上、または苗字/名前が4文字以上の場合は処理しない
    if total_len >= 5 or surname_len >= 4 or given_name_len >= 4:
        return f"{surname}{given_name}"

    # 整形ルール定義: (苗字長, 名前長) -> フォーマット文字列
    # {} は苗字、 [] は名前（後で置換）
    rules: Dict[Tuple[int, int], str] = {
        # 名前が1文字の場合
        (1, 1): "{s}　　　{g}",  # 「苗　　　名」
        (2, 1): "{s}　　{g}",    # 「苗苗　　名」
        (3, 1): "{s}　{g}",      # 「苗苗苗　名」
        
        # 名前が2文字の場合
        (1, 2): "{s}　　{g}",    # 「苗　　名名」
        (2, 2): "{s}　{g}",      # 「苗苗　名名」
        
        # 名前が3文字の場合
        (1, 3): "{s}　{g}",      # 「苗　名名名」
        (2, 3): "{s}　{g}",      # 「苗苗　名名名」
        (3, 3): "{s0}　{g}",     # 「苗　名名名」 (苗字の先頭1文字のみ)
    }

    rule_key = (surname_len, given_name_len)
    if rule_key in rules:
        fmt = rules[rule_key]
        return fmt.format(s=surname, g=given_name, s0=surname[0] if surname else "")

    return f"{surname}{given_name}"
