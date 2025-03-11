"""
7字取りルール実装モジュール

このモジュールは、7字取りルールに従って日本語氏名を整形する機能を提供します。
効率よりも確実性を重視し、各条件を明示的に処理します。
"""

def format_name_7chars_rule(surname, given_name):
    """
    7字取りルールに従って氏名を整形する関数
    
    苗字と名前の文字数に応じて、7字取りルールに沿った整形を行います。
    「処理しない」場合は、苗字と名前をそのまま連結して返します。
    
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
    # 入力値の検証と準備
    if not surname or not given_name:
        return surname + given_name
    
    surname_len = len(surname)
    given_name_len = len(given_name)
    
    # 名前が6文字以上の時は処理しない
    if given_name_len >= 6:
        return surname + given_name
    
    # 名前が5文字の場合
    if given_name_len == 5:
        if surname_len == 1:
            return f"{surname}　{given_name}"  # 「苗　名名名名名」に
        else:  # 名前5文字で苗字2文字以上の時は処理しない
            return surname + given_name
    
    # 名前が4文字の場合
    if given_name_len == 4:
        if surname_len == 1:
            return f"{surname}　　{given_name}"  # 「苗　　名名名名」に
        elif surname_len == 2:
            return f"{surname}　{given_name}"  # 「苗　名名名名名」に
        else:  # 名前4文字で苗字3文字以上の時は処理しない
            return surname + given_name
    
    # 名前が3文字の場合
    if given_name_len == 3:
        if surname_len == 1:
            return f"{surname}　　　{given_name}"  # 「苗　　　名名名」に
        elif surname_len == 2:
            return f"{surname[0]}　{surname[1]}　{given_name}"  # 「苗　苗　名名名」に
        elif surname_len == 3:
            return f"{surname}　{given_name}"  # 「苗苗苗　名名名」に
        else:  # 名前3文字で苗字4文字以上の時は処理しない
            return surname + given_name
    
    # 名前が2文字の場合
    if given_name_len == 2:
        if surname_len == 1:
            return f"{surname}　　　{given_name[0]}　{given_name[1]}"  # 「苗　　　名　名」に
        elif surname_len == 2:
            return f"{surname[0]}　{surname[1]}　{given_name[0]}　{given_name[1]}"  # 「苗　苗　名　名」に
        elif surname_len == 3:
            return f"{surname}　{given_name[0]}　{given_name[1]}"  # 「苗苗苗　名　名」に
        elif surname_len == 4:
            return f"{surname}　{given_name}"  # 「苗苗苗苗　名名」に
        else:  # 名前2文字で苗字5文字以上の時は処理しない
            return surname + given_name
    
    # 名前が1文字の場合
    if given_name_len == 1:
        if surname_len == 1:
            return f"{surname}　　　　　{given_name}"  # 「苗　　　　　名」に
        elif surname_len == 2:
            return f"{surname[0]}　{surname[1]}　　　{given_name}"  # 「苗　苗　　　名」に
        elif surname_len == 3:
            return f"{surname}　　　{given_name}"  # 「苗苗苗　　　名」に
        elif surname_len == 4:
            return f"{surname}　　{given_name}"  # 「苗苗苗苗　　名」に
        elif surname_len == 5:
            return f"{surname}　{given_name}"  # 「苗苗苗苗苗　名」に
        else:  # 名前1文字で苗字6文字以上の時は処理しない
            return surname + given_name
    
    # 上記のルールに当てはまらない場合は処理しない
    return surname + given_name 