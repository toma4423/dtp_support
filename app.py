"""
日本語DTP名寄せツール

このアプリケーションは、名簿リスト（CSV, Excel）に含まれる日本語氏名を、
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
    
    # 字取り方法
    st.subheader("字取り方法")
    alignment = st.radio(
        "揃え方を選択してください:",
        ["中央揃え", "左揃え", "右揃え"],
        index=0
    )
    
    # 文字間設定
    st.subheader("文字間設定")
    spacing = st.radio(
        "文字間を選択してください:",
        ["通常", "空ける", "詰める"],
        index=0
    )
    
    # ヘルプ情報
    st.subheader("ヘルプ")
    with st.expander("使い方"):
        st.write("""
        1. 名簿リスト（CSVまたはExcel）をアップロードします。
        2. 苗字リスト（テキストファイル）をアップロードします。
        3. サイドバーで文字数整形オプションを選択します。
        4. 「処理実行」ボタンをクリックします。
        5. 処理結果をダウンロードします。
        """)
    
    with st.expander("注意事項"):
        st.write("""
        - アップロード可能なファイルサイズは10MBまでです。
        - 名簿リストには氏名列が必要です。
        - 苗字リストは1行に1つの苗字が記載されたテキストファイルです。
        """)

# メイン処理関数
def process_name_list(df, surname_list, char_count_option, alignment_option, spacing_option):
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
    alignment_option : str
        揃え方オプション（"中央揃え", "左揃え", "右揃え"）
    spacing_option : str
        文字間設定（"通常", "空ける", "詰める"）
    
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
        
        # 苗字と名前の分割
        surname = None
        for length in range(min(3, len(full_name)), 0, -1):
            if full_name[:length] in surname_set:
                surname = full_name[:length]
                given_name = full_name[length:]
                break
        
        if surname is None:
            # 苗字が見つからない場合、単純に半分で分割
            mid = len(full_name) // 2
            surname = full_name[:mid]
            given_name = full_name[mid:]
            errors.append(f"行 {i+1}: 「{full_name}」の苗字がリストにありません。自動分割しました: {surname} {given_name}")
        
        # 文字間の調整
        spacing_char = ""
        if spacing_option == "空ける":
            spacing_char = "　"  # 全角スペースに変更
        elif spacing_option == "詰める":
            spacing_char = ""  # 通常より詰める場合は特殊な処理が必要かもしれません
        
        # 整形処理
        formatted_name = format_name(surname, given_name, target_length, alignment_option, spacing_char)
        
        # 結果の格納
        df.at[index, result_column] = formatted_name
        
        # 処理の遅延をシミュレート（実際の処理では削除可能）
        time.sleep(0.01)
    
    # 進捗バーを完了状態に
    progress_bar.progress(1.0)
    status_text.text("処理完了！")
    
    return df, errors

def format_name(surname, given_name, target_length, alignment, spacing_char=""):
    """
    氏名を指定された文字数と揃え方で整形する関数
    
    Parameters:
    -----------
    surname : str
        苗字
    given_name : str
        名前
    target_length : int
        目標の文字数
    alignment : str
        揃え方（"中央揃え", "左揃え", "右揃え"）
    spacing_char : str
        文字間に挿入する文字（"空ける"オプションの場合は全角スペース）
    
    Returns:
    --------
    str
        整形された氏名
    """
    # 7字取りの特別ルールを適用
    if target_length == 7 and spacing_char == "　":
        return format_name_7chars_rule(surname, given_name)
    
    # 通常の整形処理
    # 苗字と名前の間にスペースを入れる
    full_name = surname + spacing_char + given_name
    
    # 現在の文字数
    current_length = len(full_name)
    
    # 文字数が目標より少ない場合、空白を追加
    if current_length < target_length:
        padding = target_length - current_length
        
        if alignment == "中央揃え":
            left_padding = padding // 2
            right_padding = padding - left_padding
            formatted_name = " " * left_padding + full_name + " " * right_padding
        elif alignment == "左揃え":
            formatted_name = full_name + " " * padding
        else:  # "右揃え"
            formatted_name = " " * padding + full_name
    
    # 文字数が目標と同じ場合、そのまま返す
    elif current_length == target_length:
        formatted_name = full_name
    
    # 文字数が目標より多い場合、切り詰める（警告を出すべき）
    else:
        formatted_name = full_name[:target_length]
    
    return formatted_name

def format_name_7chars_rule(surname, given_name):
    """
    7字取りルールに従って氏名を整形する関数
    
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
    
    # 名前が6文字以上の場合はスペースなし
    if given_name_len >= 6:
        return surname + given_name
    
    # 名前が5文字の場合
    if given_name_len == 5:
        if surname_len == 1:
            return f"{surname}　{given_name}"
        else:  # 苗字が2文字以上の場合はスペースなし
            return surname + given_name
    
    # 名前が4文字の場合
    if given_name_len == 4:
        if surname_len == 1:
            return f"{surname}　　{given_name}"
        elif surname_len == 2:
            return f"{surname}　{given_name}"
        else:  # 苗字が3文字以上の場合はスペースなし
            return surname + given_name
    
    # 名前が3文字の場合
    if given_name_len == 3:
        if surname_len == 1:
            return f"{surname}　　　{given_name}"
        elif surname_len == 2:
            return f"{surname}　{given_name}"
        elif surname_len == 3:
            return f"{surname}　{given_name}"
        else:  # 苗字が4文字以上の場合はスペースなし
            return surname + given_name
    
    # 名前が2文字の場合
    if given_name_len == 2:
        if surname_len == 1:
            return f"{surname}　　　{given_name[0]}　{given_name[1]}"
        elif surname_len == 2:
            return f"{surname[0]}　{surname[1]}　{given_name[0]}　{given_name[1]}"
        elif surname_len == 3:
            return f"{surname}　{given_name[0]}　{given_name[1]}"
        elif surname_len == 4:
            return f"{surname}　{given_name}"
        else:  # 苗字が5文字以上の場合はスペースなし
            return surname + given_name
    
    # 名前が1文字の場合
    if given_name_len == 1:
        if surname_len == 1:
            return f"{surname}　　　　　{given_name}"
        elif surname_len == 2:
            return f"{surname[0]}　{surname[1]}　　　{given_name}"
        elif surname_len == 3:
            return f"{surname}　　　{given_name}"
        elif surname_len == 4:
            return f"{surname}　　{given_name}"
        elif surname_len == 5:
            return f"{surname}　{given_name}"
        else:  # 苗字が6文字以上の場合はスペースなし
            return surname + given_name
    
    # 上記のルールに当てはまらない場合は単純に連結
    return surname + given_name

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
uploaded_file = st.file_uploader("名簿リスト（CSVまたはExcel）をアップロードしてください", type=["csv", "xlsx"])

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
            else:  # xlsx
                df = pd.read_excel(uploaded_file)
                file_format = "excel"
            
            # 苗字リストの読み込み
            surname_list = load_surname_list(surname_file)
            
            # 名簿リストの処理
            with st.spinner('処理中...'):
                result_df, errors = process_name_list(
                    df, 
                    surname_list, 
                    char_count, 
                    alignment, 
                    spacing
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