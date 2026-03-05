"""
7字取りルール実装モジュール

このモジュールは、7字取りルールに従って日本語氏名を整形する機能を提供します。
"""

from typing import Dict, Tuple


def format_name_7chars_rule(surname: str, given_name: str) -> str:
    """
    7字取りルールに従って氏名を整形する関数
    """
    if not surname or not given_name:
        return f"{surname}{given_name}"

    s_len = len(surname)
    g_len = len(given_name)

    # ルール定義: (苗字長, 名前長) -> フォーマット
    # s: 苗字, g: 名前, s0: 苗字[0], s1: 苗字[1], g0: 名前[0], g1: 名前[1]
    rules: Dict[Tuple[int, int], str] = {
        # 名前5文字
        (1, 5): "{s}　{g}",
        
        # 名前4文字
        (1, 4): "{s}　　{g}",
        (2, 4): "{s}　{g}",
        
        # 名前3文字
        (1, 3): "{s}　　　{g}",
        (2, 3): "{s0}　{s1}　{g}",
        (3, 3): "{s}　{g}",
        
        # 名前2文字
        (1, 2): "{s}　　　{g0}　{g1}",
        (2, 2): "{s0}　{s1}　{g0}　{g1}",
        (3, 2): "{s}　{g0}　{g1}",
        (4, 2): "{s}　{g}",
        
        # 名前1文字
        (1, 1): "{s}　　　　　{g}",
        (2, 1): "{s0}　{s1}　　　{g}",
        (3, 1): "{s}　　　{g}",
        (4, 1): "{s}　　{g}",
        (5, 1): "{s}　{g}",
    }

    rule_key = (s_len, g_len)
    if rule_key in rules:
        fmt = rules[rule_key]
        return fmt.format(
            s=surname, 
            g=given_name,
            s0=surname[0] if s_len > 0 else "",
            s1=surname[1] if s_len > 1 else "",
            g0=given_name[0] if g_len > 0 else "",
            g1=given_name[1] if g_len > 1 else ""
        )

    return f"{surname}{given_name}"
