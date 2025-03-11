"""
5字取りルール実装モジュール

このモジュールは、5字取りルールに従って日本語氏名を整形する機能を提供します。
"""

def format_name_5chars_rule(surname, given_name):
    """
    5字取りルールに従って氏名を整形する関数
    
    Parameters:
    -----------
    surname : str
        苗字
    given_name : str
        名前
    
    Returns:
    --------
    str
        整形された氏名
    """
    surname_len = len(surname)
    given_name_len = len(given_name)
    
    # 苗字と名前を合わせて5文字以上であれば処理しない
    if surname_len + given_name_len >= 5:
        return surname + given_name
    
    # 苗字が4文字以上の場合は処理しない
    if surname_len >= 4:
        return surname + given_name
    
    # 名前が4文字以上の場合は処理しない
    if given_name_len >= 4:
        return surname + given_name
    
    # 名前が1文字の場合
    if given_name_len == 1:
        if surname_len == 1:
            return f"{surname}　　　{given_name}"  # 「苗　　　名」に
        elif surname_len == 2:
            return f"{surname}　　{given_name}"    # 「苗苗　　名」に
        elif surname_len == 3:
            return f"{surname}　{given_name}"      # 「苗苗苗　名」に
        else:  # 苗字が4文字以上の場合はスペースなし
            return surname + given_name
    
    # 名前が2文字の場合
    if given_name_len == 2:
        if surname_len == 1:
            return f"{surname}　　{given_name}"    # 「苗　　名名」に
        elif surname_len == 2:
            return f"{surname}　{given_name}"      # 「苗苗　名名」に
        else:  # 苗字が3文字以上の場合はスペースなし
            return surname + given_name
    
    # 名前が3文字の場合
    if given_name_len == 3:
        if surname_len == 1:
            return f"{surname}　{given_name}"      # 「苗　名名名」に
        elif surname_len == 2:
            return f"{surname}　{given_name}"      # 「苗苗　名名名」に - 実際のルールには記載がないが、ドキュメントに従う
        elif surname_len == 3:
            # 苗字が3文字の場合は、苗字の最初の1文字だけを使用
            return f"{surname[0]}　{given_name}"   # 「苗　名名名」に
        else:  # 苗字が4文字以上の場合はスペースなし
            return surname + given_name
    
    # 上記のルールに当てはまらない場合は単純に連結
    return surname + given_name 