"""
日本語DTP名寄せツール

このアプリケーションは、名簿リスト（CSV, Excel, テキスト）に含まれる日本語氏名を、
指定された文字数（5字または7字）で整形し、DTP処理に適した形式で出力します。
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import tempfile
import re
from io import BytesIO
import base64
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
st.markdown("""
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
</style>
""", unsafe_allow_html=True)

# メインヘッダー
st.markdown("<h1 class='main-header'>日本語DTP名寄せツール</h1>", unsafe_allow_html=True)

# サイドバーの設定
with st.sidebar:
    st.header("設定")
    
    # 文字数整形オプション
    st.subheader("文字数整形オプション")
    char_count = st.radio(
        "文字数を選択してください:",
        ["5字取り", "7字取り"],
        index=0
    )
    
    # ヘルプ情報
    st.subheader("ヘルプ")
    with st.expander("使い方"):
        st.write("""
        1. 名簿リスト（CSV、Excel、またはテキスト）をアップロードします。
        2. 苗字リスト（テキストファイル）をアップロードします。
        3. サイドバーで文字数整形オプション（5字取りまたは7字取り）を選択します。
        4. 「処理実行」ボタンをクリックします。
        5. 処理結果をダウンロードします。
        """)
    
    with st.expander("注意事項"):
        st.write("""
        - アップロード可能なファイルサイズは10MBまでです。
        - 名簿リスト：
          - CSVまたはExcelの場合は氏名列が必要です。
          - テキストファイルの場合は1行に1つの氏名を記載してください。
        - 苗字リストは1行に1つの苗字が記載されたテキストファイルです。
        """)

# メイン処理関数
def process_name_list(df, surname_list, char_count_option):
    """
    名簿リストの処理を行う関数
    
    Parameters:
    -----------
    df : pandas.DataFrame
        処理対象の名簿データフレーム
    surname_list : list
        苗字リスト
    char_count_option : str
        文字数整形オプション（"5字取り" or "7字取り"）
    
    Returns:
    --------
    pandas.DataFrame
        処理後のデータフレーム
    list
        エラーメッセージのリスト
    """
    # 進捗バーの初期化
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # エラーメッセージを格納するリスト
    errors = []
    
    # 氏名列の特定
    name_columns = []
    for col in df.columns:
        if '氏名' in col or '名前' in col or '姓名' in col or 'name' in col.lower():
            name_columns.append(col)
    
    if not name_columns:
        errors.append("氏名列が見つかりませんでした。列名に「氏名」「名前」「姓名」「name」のいずれかを含む列が必要です。")
        return df, errors
    
    # 最初の氏名列を使用
    name_column = name_columns[0]
    status_text.text(f"氏名列として「{name_column}」を使用します。")
    
    # 文字数の設定
    if char_count_option == "5字取り":
        target_length = 5
    else:  # "7字取り"
        target_length = 7
    
    # 結果列の追加
    result_column = f"{name_column}_整形済み"
    df[result_column] = ""
    
    # 苗字リストをセットに変換して検索を高速化
    surname_set = set(surname_list)
    
    # 各行の処理
    total_rows = len(df)
    for i, (index, row) in enumerate(df.iterrows()):
        # 進捗状況の更新
        progress = (i + 1) / total_rows
        progress_bar.progress(progress)
        status_text.text(f"処理中... {i+1}/{total_rows} 行 ({progress:.1%})")
        
        # 氏名の取得
        full_name = str(row[name_column]).strip()
        
        if pd.isna(full_name) or full_name == "":
            errors.append(f"行 {i+1}: 氏名が空です。")
            continue
        
        # 苗字と名前の分割（リストの順序を考慮して1行目から検索）
        surname = None
        for potential_surname in surname_list:
            if full_name.startswith(potential_surname):
                surname = potential_surname
                given_name = full_name[len(potential_surname):]
                break
        
        if surname is None:
            # 苗字が見つからない場合、単純に半分で分割
            mid = len(full_name) // 2
            surname = full_name[:mid]
            given_name = full_name[mid:]
            errors.append(f"行 {i+1}: 「{full_name}」の苗字がリストにありません。自動分割しました: {surname} {given_name}")
        
        # 整形処理
        formatted_name = format_name(surname, given_name, target_length)
        
        # 結果の格納
        df.at[index, result_column] = formatted_name
        
        # 処理の遅延をシミュレート（実際の処理では削除可能）
        time.sleep(0.01)
    
    # 進捗バーを完了状態に
    progress_bar.progress(1.0)
    status_text.text("処理完了！")
    
    return df, errors

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
    content = file.read().decode('utf-8')
    surnames = [line.strip() for line in content.split('\n') if line.strip()]
    return surnames

def get_download_link(df, file_format, filename):
    """
    ダウンロードリンクを生成する関数
    
    Parameters:
    -----------
    df : pandas.DataFrame
        ダウンロード対象のデータフレーム
    file_format : str
        ファイル形式（"csv" or "excel"）
    filename : str
        ダウンロードファイル名
    
    Returns:
    --------
    str
        ダウンロードリンクのHTML
    """
    if file_format == "csv":
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">ダウンロード（CSV）</a>'
    else:  # excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        b64 = base64.b64encode(output.getvalue()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}.xlsx">ダウンロード（Excel）</a>'
    
    return href

# メイン処理部分
st.markdown("<h2 class='sub-header'>ファイルアップロード</h2>", unsafe_allow_html=True)

# 名簿リストのアップロード
uploaded_file = st.file_uploader("名簿リスト（CSV、Excel、またはテキスト）をアップロードしてください", type=["csv", "xlsx", "txt"])

# 苗字リストのアップロード
surname_file = st.file_uploader("苗字リスト（テキストファイル）をアップロードしてください", type=["txt"])

# 処理実行ボタン
if uploaded_file is not None and surname_file is not None:
    st.markdown("<h2 class='sub-header'>処理実行</h2>", unsafe_allow_html=True)
    
    if st.button("処理実行", key="process_button"):
        try:
            # ファイル形式の判定
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            # データフレームの読み込み
            if file_extension == 'csv':
                df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
                file_format = "csv"
            elif file_extension == 'xlsx':
                df = pd.read_excel(uploaded_file)
                file_format = "excel"
            else:  # txt
                # テキストファイルを読み込む
                content = uploaded_file.read().decode('utf-8')
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                
                # 各行を氏名として扱い、DataFrameに変換
                df = pd.DataFrame({'氏名': lines})
                file_format = "csv"  # 出力形式はCSVとする
            
            # 苗字リストの読み込み
            surname_list = load_surname_list(surname_file)
            
            # 名簿リストの処理
            with st.spinner('処理中...'):
                result_df, errors = process_name_list(
                    df, 
                    surname_list, 
                    char_count
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
            st.write(f"処理が完了しました。合計 {len(df)} 行を処理しました。")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # 結果のプレビュー
            st.subheader("結果プレビュー")
            st.dataframe(result_df.head(10))
            
            # ダウンロードリンク
            st.subheader("結果のダウンロード")
            download_filename = f"整形済み_{uploaded_file.name.split('.')[0]}"
            st.markdown(get_download_link(result_df, file_format, download_filename), unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")
else:
    st.markdown("<div class='info-box'>", unsafe_allow_html=True)
    st.write("名簿リストと苗字リストをアップロードしてください。")
    st.markdown("</div>", unsafe_allow_html=True)

# フッター
st.markdown("---")
st.markdown("© 2023 日本語DTP名寄せツール") 