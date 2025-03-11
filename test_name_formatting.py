"""
日本語名前整形テストスクリプト

このスクリプトは、様々な長さの苗字と名前の組み合わせを生成し、
5字取りルールと7字取りルールによる整形結果を表形式で出力します。
また、苗字判別が難しいケースについても検証します。
"""

import random
from pattern5 import format_name_5chars_rule
from pattern7 import format_name_7chars_rule

def main():
    # 苗字リストから一部をランダムに選択
    surnames = []
    with open('苗字リスト.txt', 'r', encoding='utf-8') as f:
        all_surnames = [line.strip() for line in f if line.strip()]
        # 長さごとに分類
        surnames_by_length = {i: [] for i in range(1, 6)}
        for surname in all_surnames:
            if 1 <= len(surname) <= 5:
                surnames_by_length[len(surname)].append(surname)
        
        # 各長さから最大5個ずつ選択
        for length, names in surnames_by_length.items():
            if names:
                sample_size = min(5, len(names))
                surnames.extend(random.sample(names, sample_size))

    # 仮の名前リスト（長さごとに分類）
    given_names = {
        1: ['太', '花', '一', '実', '愛', '心', '光', '翔', '蓮', '陽'],
        2: ['太郎', '花子', '一郎', '実子', '愛子', '真実', '光一', '翔太', '蓮司', '陽子'],
        3: ['太郎丸', '花子美', '一郎太', '実子奈', '愛子美', '真実子', '光一郎', '翔太郎', '蓮司郎', '陽子美'],
        4: ['太郎丸子', '花子美咲', '一郎太郎', '実子奈美', '愛子美波', '真実子奈', '光一郎丸', '翔太郎介', '蓮司郎太', '陽子美香'],
        5: ['太郎丸子奈', '花子美咲奈', '一郎太郎介', '実子奈美子', '愛子美波音', '真実子奈美', '光一郎丸太', '翔太郎介二', '蓮司郎太助', '陽子美香子']
    }

    # テストケースを作成
    test_cases = []
    for surname_len in range(1, 6):
        available_surnames = [s for s in surnames if len(s) == surname_len]
        if not available_surnames:
            continue
        
        for given_name_len in range(1, 6):
            if not given_names.get(given_name_len):
                continue
                
            # 各パターンから1つのケースを選択
            surname = random.choice(available_surnames)
            given_name = random.choice(given_names[given_name_len])
            test_cases.append((surname, given_name))

    # 特別なテストケース（既存のサンプル）も追加
    test_cases.extend([
        ('伊藤', 'さくら'),
        ('中村', '真由美'),
        ('山田', '太'),
        ('佐藤', '太'),
        ('小比類巻', 'あい'),
        ('小比類巻', 'いいこと')
    ])
    
    # 苗字判別が難しいケースを追加
    problematic_cases = [
        ('小', '太郎'),         # 「小」は「小比類巻」の一部
        ('小比類巻', '太郎'),    # 「小比類巻」には「小」が含まれる
        ('中', '一郎'),         # 「中」は「中村」の一部
        ('中村', '一郎'),       # 「中村」には「中」が含まれる
        ('佐', '花子'),         # 「佐」は「佐藤」の一部
        ('佐藤', '花子'),       # 「佐藤」には「佐」が含まれる
        ('鈴', '太郎'),         # 「鈴」は「鈴木」の一部
        ('鈴木', '太郎')        # 「鈴木」には「鈴」が含まれる
    ]
    
    # 説明を追加
    print('\n【苗字判別が難しいケースのテスト】')
    print('以下は、一方の苗字が他方の先頭部分になっているケース（例：「小」と「小比類巻」）のテストです。')
    print('これらは苗字リストの順序に依存して結果が変わる可能性があります。\n')
    
    # 苗字判別テスト結果を表示
    print(f'{"苗字":^10}{"名前":^10}{"合計文字数":^10}{"5字取り":^20}{"7字取り":^20}')
    print('-' * 70)
    
    for surname, given_name in problematic_cases:
        total_len = len(surname) + len(given_name)
        formatted_5 = format_name_5chars_rule(surname, given_name)
        formatted_7 = format_name_7chars_rule(surname, given_name)
        print(f'{surname:<10}{given_name:<10}{total_len:^10}{formatted_5:<20}{formatted_7:<20}')
        
    # 通常のテスト結果を表示
    print('\n【一般的なテストケース結果】')
    print(f'{"苗字":^10}{"名前":^10}{"合計文字数":^10}{"5字取り":^20}{"7字取り":^20}')
    print('-' * 70)

    for surname, given_name in test_cases:
        total_len = len(surname) + len(given_name)
        formatted_5 = format_name_5chars_rule(surname, given_name)
        formatted_7 = format_name_7chars_rule(surname, given_name)
        print(f'{surname:<10}{given_name:<10}{total_len:^10}{formatted_5:<20}{formatted_7:<20}')

if __name__ == "__main__":
    main() 