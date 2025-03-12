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
        2. 苗字リスト（テキストファイル）をアップロードします（一行に一つの苗字）。
        3. サイドバーで文字数整形オプション（5字取りまたは7字取り）を選択します。
        4. 「処理実行」ボタンをクリックします。
        5. 処理結果が下部のテキストエリアに表示されます。
        """
        )

    with st.expander("注意事項"):
        st.write(
            """
        - 氏名は一行に一つずつ入力してください。
        - 空白行は処理されません。
        - 苗字リストは1行に1つの苗字が記載されたテキストファイルです。
        - 苗字リストに存在しない氏名は、自動的に半分で分割されます。
        """
        )


def load_surname_list(file):
    """
    苗字リストを読み込む関数

    Parameters:
    -----------
    file : UploadedFile
        アップロードされた苗字リストファイル

    Returns:
    --------
    list
        苗字のリスト
    """
    content = file.read().decode("utf-8")
    surnames = [line.strip() for line in content.split("\n") if line.strip()]
    return surnames


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
        処理されなかった名前のリスト
    list
        エラーメッセージのリスト
    """
    # 進捗バーの初期化
    progress_bar = st.progress(0)
    status_text = st.empty()

    # エラーメッセージを格納するリスト
    errors = []

    # 処理されなかった名前のリスト
    skipped_names = []

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
            # 苗字が見つからない場合は処理しない
            skipped_names.append(full_name)
            errors.append(
                f"行 {i+1}: 「{full_name}」の苗字がリストにありません。処理をスキップします。"
            )
            continue  # 次の名前に進む

        # 整形処理
        formatted_name = format_name(surname, given_name, target_length)

        # 結果の格納
        formatted_names.append(formatted_name)

        # 処理の遅延をシミュレート（実際の処理では削除可能）
        time.sleep(0.01)

    # 進捗バーを完了状態に
    progress_bar.progress(1.0)
    status_text.text("処理完了！")

    return formatted_names, skipped_names, errors


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

# 名前リストのテキストエリア
name_input = st.text_area(
    "変換したい氏名を入力してください（一行に一つ）:",
    height=200,
    help="一行に一つの氏名を入力してください。",
)

# 苗字リストのアップロード
surname_file = st.file_uploader(
    "苗字リスト（テキストファイル）をアップロードしてください",
    type=["txt"],
    help="一行に一つの苗字が記載されたテキストファイルをアップロードしてください。",
)

# 処理実行ボタン
if name_input and surname_file is not None:
    st.markdown("<h2 class='sub-header'>処理実行</h2>", unsafe_allow_html=True)

    if st.button("処理実行", key="process_button"):
        try:
            # 入力を行ごとにリスト化
            names = [line.strip() for line in name_input.split("\n") if line.strip()]

            # 苗字リストの読み込み
            surname_list = load_surname_list(surname_file)

            # 名前リストの処理
            with st.spinner("処理中..."):
                formatted_names, skipped_names, errors = process_name_list(
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
            if skipped_names:
                st.write(f"処理されなかった名前: {len(skipped_names)} 行")
            st.markdown("</div>", unsafe_allow_html=True)

            # 結果の表示
            result_text = "\n".join(formatted_names)
            st.markdown("<h3>結果出力</h3>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='result-area'>{result_text}</div>", unsafe_allow_html=True
            )

            # コピー可能なテキストエリアとしても表示
            st.text_area("結果（コピー可能）:", value=result_text, height=300)

            # 処理されなかった名前の表示
            if skipped_names:
                skipped_text = "\n".join(skipped_names)
                st.markdown("<h3>処理されなかった名前</h3>", unsafe_allow_html=True)
                st.text_area("処理されなかった名前:", value=skipped_text, height=100)

        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")
else:
    st.markdown("<div class='info-box'>", unsafe_allow_html=True)
    st.write("名前リストを入力し、苗字リストをアップロードしてください。")
    st.markdown("</div>", unsafe_allow_html=True)

# フッター
st.markdown("---")
st.markdown("© 2023 日本語DTP名寄せツール")
