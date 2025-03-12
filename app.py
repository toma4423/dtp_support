"""
日本語DTP名寄せツール

このアプリケーションは、テキストフィールドに入力された日本語氏名を、
指定された文字数（5字または7字）で整形し、DTP処理に適した形式で出力します。
"""

import streamlit as st
import pandas as pd
import numpy as np
import re
import time

# 自作モジュールのインポート
from pattern5 import format_name_5chars_rule
from pattern7 import format_name_7chars_rule

# サンプルデータ
SAMPLE_NAMES = """佐藤太郎
鈴木花子
高橋一郎
田中美咲
渡辺健太
伊藤さくら
山本雄大
中村真由美
小林誠
加藤裕子"""

SAMPLE_SURNAMES = """佐藤
鈴木
高橋
田中
渡辺
伊藤
山本
中村
小林
加藤
吉田
山田
佐々木
山口
松本"""

# アプリケーションのタイトルとスタイル設定
st.set_page_config(
    page_title="日本語DTP名寄せツール",
    page_icon="📝",
    layout="wide",
)

# CSSスタイルの追加
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .error-box {
        background-color: #FFEBEE;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .result-area {
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 0.5rem;
        font-family: monospace;
        white-space: pre;
        margin-top: 1rem;
    }
    .button-container {
        display: flex;
        gap: 1rem;
        margin-bottom: 1rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# メインヘッダー
st.markdown(
    "<h1 class='main-header'>日本語DTP名寄せツール</h1>", unsafe_allow_html=True
)

# サイドバーの設定
with st.sidebar:
    st.header("設定")

    # 文字数整形オプション
    st.subheader("文字数整形オプション")
    char_count = st.radio("文字数を選択してください:", ["5字取り", "7字取り"], index=0)

    # ヘルプ情報
    st.subheader("ヘルプ")
    with st.expander("使い方"):
        st.write(
            """
        1. テキストフィールドに変換したい氏名を入力します（一行に一つの氏名）。
        2. 苗字リストをテキストフィールドに入力します（一行に一つの苗字）。
        3. サイドバーで文字数整形オプション（5字取りまたは7字取り）を選択します。
        4. 「処理実行」ボタンをクリックします。
        5. 処理結果が下部のテキストエリアに表示されます。
        """
        )

    with st.expander("注意事項"):
        st.write(
            """
        - 氏名と苗字は一行に一つずつ入力してください。
        - 空白行は処理されません。
        - 苗字リストに存在しない氏名は、自動的に半分で分割されます。
        """
        )


# メイン処理関数
def process_name_list(names, surname_list, char_count_option):
    """
    名前リストの処理を行う関数

    Parameters:
    -----------
    names : list
        処理対象の名前リスト
    surname_list : list
        苗字リスト
    char_count_option : str
        文字数整形オプション（"5字取り" or "7字取り"）

    Returns:
    --------
    list
        処理後の名前リスト
    list
        エラーメッセージのリスト
    """
    # 進捗バーの初期化
    progress_bar = st.progress(0)
    status_text = st.empty()

    # エラーメッセージを格納するリスト
    errors = []

    # 整形された名前を格納するリスト
    formatted_names = []

    # 文字数の設定
    if char_count_option == "5字取り":
        target_length = 5
    else:  # "7字取り"
        target_length = 7

    # 苗字リストをセットに変換して検索を高速化
    surname_set = set(surname_list)

    # 各行の処理
    total_names = len(names)
    for i, full_name in enumerate(names):
        # 進捗状況の更新
        progress = (i + 1) / total_names
        progress_bar.progress(progress)
        status_text.text(f"処理中... {i+1}/{total_names} 行 ({progress:.1%})")

        full_name = full_name.strip()
        if not full_name:
            continue  # 空白行はスキップ

        # 苗字と名前の分割（リストの順序を考慮して検索）
        surname = None
        for potential_surname in surname_list:
            if full_name.startswith(potential_surname):
                surname = potential_surname
                given_name = full_name[len(potential_surname) :]
                break

        if surname is None:
            # 苗字が見つからない場合、単純に半分で分割
            mid = len(full_name) // 2
            surname = full_name[:mid]
            given_name = full_name[mid:]
            errors.append(
                f"行 {i+1}: 「{full_name}」の苗字がリストにありません。自動分割しました: {surname} {given_name}"
            )

        # 整形処理
        formatted_name = format_name(surname, given_name, target_length)

        # 結果の格納
        formatted_names.append(formatted_name)

        # 処理の遅延をシミュレート（実際の処理では削除可能）
        time.sleep(0.01)

    # 進捗バーを完了状態に
    progress_bar.progress(1.0)
    status_text.text("処理完了！")

    return formatted_names, errors


def format_name(surname, given_name, target_length):
    """
    氏名を指定された文字数でルールに従って整形する関数

    Parameters:
    -----------
    surname : str
        苗字
    given_name : str
        名前
    target_length : int
        目標の文字数（5または7）

    Returns:
    --------
    str
        整形された氏名
    """
    # 5字取りか7字取りのルールを適用
    if target_length == 5:
        return format_name_5chars_rule(surname, given_name)
    else:  # target_length == 7
        return format_name_7chars_rule(surname, given_name)


# メイン処理部分
st.markdown("<h2 class='sub-header'>名前入力</h2>", unsafe_allow_html=True)

# サンプルデータ使用ボタン
st.markdown("<div class='button-container'>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 3])
with col1:
    use_sample_names = st.button("サンプル氏名を使用", key="sample_names")
with col2:
    use_sample_surnames = st.button("サンプル苗字を使用", key="sample_surnames")
st.markdown("</div>", unsafe_allow_html=True)

# 名前リストのテキストエリア
name_input = st.text_area(
    "変換したい氏名を入力してください（一行に一つ）:",
    value=SAMPLE_NAMES if use_sample_names else "",
    height=200,
    help="一行に一つの氏名を入力してください。",
    key="name_input",
)

# 苗字リストのテキストエリア
surname_input = st.text_area(
    "苗字リストを入力してください（一行に一つ）:",
    value=SAMPLE_SURNAMES if use_sample_surnames else "",
    height=200,
    help="一行に一つの苗字を入力してください。",
    key="surname_input",
)

# 処理実行ボタン
if name_input and surname_input:
    st.markdown("<h2 class='sub-header'>処理実行</h2>", unsafe_allow_html=True)

    if st.button("処理実行", key="process_button"):
        try:
            # 入力を行ごとにリスト化
            names = [line.strip() for line in name_input.split("\n") if line.strip()]
            surname_list = [
                line.strip() for line in surname_input.split("\n") if line.strip()
            ]

            # 名前リストの処理
            with st.spinner("処理中..."):
                formatted_names, errors = process_name_list(
                    names, surname_list, char_count
                )

            # エラーメッセージの表示
            if errors:
                st.markdown("<div class='error-box'>", unsafe_allow_html=True)
                st.subheader("処理中に以下のエラーが発生しました:")
                for error in errors:
                    st.write(f"- {error}")
                st.markdown("</div>", unsafe_allow_html=True)

            # 処理結果の表示
            st.markdown("<h2 class='sub-header'>処理結果</h2>", unsafe_allow_html=True)
            st.markdown("<div class='success-box'>", unsafe_allow_html=True)
            st.write(
                f"処理が完了しました。合計 {len(formatted_names)} 行を処理しました。"
            )
            st.markdown("</div>", unsafe_allow_html=True)

            # 結果の表示
            result_text = "\n".join(formatted_names)
            st.markdown("<h3>結果出力</h3>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='result-area'>{result_text}</div>", unsafe_allow_html=True
            )

            # コピー可能なテキストエリアとしても表示
            st.text_area("結果（コピー可能）:", value=result_text, height=300)

        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")
else:
    st.markdown("<div class='info-box'>", unsafe_allow_html=True)
    st.write("名前リストと苗字リストを入力してください。")
    st.markdown("</div>", unsafe_allow_html=True)

# フッター
st.markdown("---")
st.markdown("© 2023 日本語DTP名寄せツール")
