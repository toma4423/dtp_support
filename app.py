"""
日本語DTP字取りツール

このアプリケーションは、テキストフィールドまたはファイルから入力された日本語氏名を、
指定された文字数（5字または7字）で整形し、DTP処理に適した形式で出力します。
"""

import streamlit as st
import pandas as pd
import time
import os

# 自作モジュールのインポート
from pattern5 import format_name_5chars_rule
from pattern7 import format_name_7chars_rule

# アプリケーションのタイトルとスタイル設定
st.set_page_config(
    page_title="日本語DTP字取りツール",
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
    "<h1 class='main-header'>日本語DTP字取りツール</h1>", unsafe_allow_html=True
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
        1. テキストフィールドに変換したい氏名を入力、またはCSV/Excelファイルをアップロードします。
        2. （任意）カスタムの苗字リストをアップロードします。
        3. サイドバーで文字数整形オプション（5字取りまたは7字取り）を選択します。
        4. 「処理実行」ボタンをクリックします。
        5. 処理結果が下部のテキストエリアに表示されます。
        """
        )

    with st.expander("注意事項"):
        st.write(
            """
        - 空白行は処理されません。
        - 苗字リストに存在しない氏名は処理されず、スキップされます。
        - デフォルトで約2.5万件の苗字リストが内蔵されています。
        """
        )


# --- 共通関数 ---

@st.cache_data
def load_default_surname_list():
    """
    デフォルトの苗字リストを読み込む
    """
    filename = "surnames.txt"
    if not os.path.exists(filename):
        # バックアップとして元のファイル名も確認
        if os.path.exists("苗字リスト.txt"):
            filename = "苗字リスト.txt"
        else:
            return []
            
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(filename, "r", encoding="shift-jis") as f:
                content = f.read()
        except:
            return []
    except:
        return []
        
    surnames = [line.strip() for line in content.split("\n") if line.strip()]
    surnames.sort(key=len, reverse=True)
    return surnames

def load_custom_surname_list(uploaded_file):
    """
    アップロードされた苗字リストを読み込む
    """
    try:
        content = uploaded_file.getvalue().decode("utf-8")
    except UnicodeDecodeError:
        try:
            content = uploaded_file.getvalue().decode("shift-jis")
        except Exception as e:
            st.error(f"苗字リストの読み込みに失敗しました: {e}")
            return []
            
    surnames = [line.strip() for line in content.split("\n") if line.strip()]
    surnames.sort(key=len, reverse=True)
    return surnames

def format_name(surname, given_name, target_length):
    """
    氏名を指定された文字数でルールに従って整形する関数
    """
    if target_length == 5:
        return format_name_5chars_rule(surname, given_name)
    else:  # target_length == 7
        return format_name_7chars_rule(surname, given_name)

def split_name_smart(full_name, surname_set, max_surname_len):
    """
    苗字リスト（set）を使って賢く分割する
    """
    # 最長一致で分割
    for length in range(min(len(full_name), max_surname_len), 0, -1):
        potential_surname = full_name[:length]
        if potential_surname in surname_set:
            return potential_surname, full_name[length:]
    return None, None


# メイン処理関数
def process_name_list(names, surname_list, char_count_option):
    """
    名前リストの処理を行う関数
    """
    # 進捗バーの初期化
    progress_bar = st.progress(0)
    status_text = st.empty()

    surname_set = set(surname_list)
    max_surname_len = max(len(s) for s in surname_list) if surname_list else 0

    # 処理されなかった名前のリスト（行番号付き）
    skipped_names = []

    # 整形された名前を格納するリスト
    formatted_names = []

    # 文字数の設定
    if char_count_option == "5字取り":
        target_length = 5
    else:  # "7字取り"
        target_length = 7

    # 各行の処理
    total_names = len(names)
    for i, full_name in enumerate(names):
        full_name = str(full_name).strip()
        if not full_name:
            continue  # 空白行はスキップ
            
        progress = (i + 1) / total_names
        # 進捗状況の更新 (負荷軽減のため一定間隔で更新)
        if (i + 1) % 10 == 0 or (i + 1) == total_names:
            progress_bar.progress(progress)
            status_text.text(f"処理中... {i+1}/{total_names} 行 ({progress:.1%})")

        # 苗字と名前の分割
        surname, given_name = split_name_smart(full_name, surname_set, max_surname_len)

        if surname is None:
            # 苗字が見つからない場合は行番号と共に記録
            skipped_names.append((i + 1, full_name))
            # 元のデータをそのまま出力に加える
            formatted_names.append(full_name)
            continue  # 次の名前に進む

        # 整形処理
        formatted_name = format_name(surname, given_name, target_length)

        # 結果の格納
        formatted_names.append(formatted_name)

    # 進捗バーを完了状態に
    progress_bar.progress(1.0)
    status_text.text("処理完了！")

    return formatted_names, skipped_names


# メイン処理部分
st.markdown("<h2 class='sub-header'>名前入力</h2>", unsafe_allow_html=True)

input_method = st.radio("入力方法を選択:", ["テキストエリア", "ファイルアップロード (CSV/Excel)"])

name_list = []

if input_method == "テキストエリア":
    # 名前リストのテキストエリア
    name_input = st.text_area(
        "変換したい氏名を入力してください（一行に一つ）:",
        height=200,
        help="一行に一つの氏名を入力してください。",
    )
    if name_input:
        name_list = [line.strip() for line in name_input.split("\n") if line.strip()]
else:
    # CSV/Excelのアップロード
    uploaded_data = st.file_uploader(
        "CSVまたはExcelファイルをアップロード",
        type=["csv", "xlsx", "xls"],
        help="氏名が含まれる列を持つファイルをアップロードしてください。"
    )
    if uploaded_data:
        try:
            if uploaded_data.name.endswith(".csv"):
                try:
                    df = pd.read_csv(uploaded_data, encoding="utf-8")
                except UnicodeDecodeError:
                    df = pd.read_csv(uploaded_data, encoding="shift-jis")
            else:
                df = pd.read_excel(uploaded_data)
            
            st.write("読み込まれたデータ (プレビュー):")
            st.dataframe(df.head(), use_container_width=True)
            
            target_col = st.selectbox("氏名が含まれる列を選択してください:", df.columns)
            if target_col:
                name_list = df[target_col].dropna().astype(str).tolist()
        except Exception as e:
            st.error(f"ファイルの読み込みに失敗しました: {e}")

st.markdown("<h2 class='sub-header'>苗字リスト（任意）</h2>", unsafe_allow_html=True)
st.write("※デフォルトで約2.5万件の苗字リストを使用します。独自のリストを使用したい場合のみアップロードしてください。")

# 苗字リストのアップロード
surname_file = st.file_uploader(
    "苗字リスト（テキストファイル）をアップロードしてください",
    type=["txt"],
    help="一行に一つの苗字が記載されたテキストファイルをアップロードしてください。",
)


# 処理実行ボタン
if name_list:
    st.markdown("<h2 class='sub-header'>処理実行</h2>", unsafe_allow_html=True)

    if st.button("処理実行", key="process_button"):
        try:
            # 苗字リストの読み込み
            with st.spinner("苗字リストを準備中..."):
                if surname_file is not None:
                    surname_list = load_custom_surname_list(surname_file)
                else:
                    surname_list = load_default_surname_list()

            if not surname_list:
                st.error("苗字リストが読み込めませんでした。")
            else:
                # 名前リストの処理
                formatted_names, skipped_names = process_name_list(
                    name_list, surname_list, char_count
                )

                # 処理結果の表示
                st.markdown("<h2 class='sub-header'>処理結果</h2>", unsafe_allow_html=True)
                st.markdown("<div class='success-box'>", unsafe_allow_html=True)
                st.write(
                    f"処理が完了しました。合計 {len(formatted_names)} 行を処理しました。"
                )
                if skipped_names:
                    st.write(f"処理されなかった名前: {len(skipped_names)} 行")
                st.markdown("</div>", unsafe_allow_html=True)

                # 結果の表示（コピー可能なテキストエリアのみ残す）
                result_text = "\n".join(formatted_names)
                st.subheader("結果")
                st.text_area("結果（コピー可能）:", value=result_text, height=300)
                
                # ダウンロードボタン
                st.download_button(
                    label="📥 結果をダウンロード (.txt)",
                    data=result_text,
                    file_name="formatted_names.txt",
                    mime="text/plain",
                )

                # 処理されなかった名前の表示
                if skipped_names:
                    # 処理できなかった名前の行番号と名前を「n行目：名前」の形式で表示
                    skipped_info = ", ".join([f"{i}行目：{name}" for i, name in skipped_names])
                    st.markdown("<h3>処理されなかった名前</h3>", unsafe_allow_html=True)
                    st.markdown("<div class='error-box'>", unsafe_allow_html=True)
                    st.write(skipped_info)
                    st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")
else:
    st.markdown("<div class='info-box'>", unsafe_allow_html=True)
    st.write("名前リストを入力し、必要に応じて苗字リストをアップロードしてください。")
    st.markdown("</div>", unsafe_allow_html=True)

# フッター
st.markdown("---")
st.markdown("© 2025 日本語DTP字取りツール")
