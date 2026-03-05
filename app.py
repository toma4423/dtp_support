"""
日本語DTP字取りツール

このアプリケーションは、テキストフィールドまたはファイルから入力された日本語氏名を、
指定された文字数（5字または7字）で整形し、DTP処理に適した形式で出力します。
"""

import streamlit as st
import pandas as pd
import io
import os

# 自作モジュールのインポート
from pattern5 import format_name_5chars_rule
from pattern7 import format_name_7chars_rule

# アプリケーションのタイトルとスタイル設定
st.set_page_config(
    page_title="日本語DTP字取りツール",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSSスタイルの追加
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #1E88E5;
        padding-bottom: 0.5rem;
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
    footer {
        text-align: center;
        margin-top: 3rem;
        color: #666;
        font-size: 0.8rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# メインヘッダー
st.markdown(
    "<h1 class='main-header'>日本語DTP字取りツール</h1>", unsafe_allow_html=True
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

def process_names(names, surname_list, char_count_option):
    """
    名前リストを処理する
    """
    # 効率化のためにset化
    surname_set = set(surname_list)
    max_surname_len = max(len(s) for s in surname_list) if surname_list else 0
    
    formatted_names = []
    skipped_names = []
    
    target_length = 5 if char_count_option == "5字取り" else 7
    
    progress_bar = st.progress(0)
    total_names = len(names)
    
    for i, full_name in enumerate(names):
        full_name = str(full_name).strip()
        if not full_name:
            continue
            
        # 苗字と名前の分割
        surname, given_name = split_name_smart(full_name, surname_set, max_surname_len)
        
        if surname is None:
            skipped_names.append((i + 1, full_name))
            formatted_names.append(full_name)
        else:
            formatted_name = format_name(surname, given_name, target_length)
            formatted_names.append(formatted_name)
            
        if (i + 1) % 10 == 0 or (i + 1) == total_names:
            progress_bar.progress((i + 1) / total_names)
            
    return formatted_names, skipped_names

# --- サイドバー ---
with st.sidebar:
    st.header("⚙️ 設定")

    # 文字数整形オプション
    st.subheader("文字数整形")
    char_count = st.radio("目標文字数を選択:", ["5字取り", "7字取り"], index=0)

    st.markdown("---")
    
    # 苗字リストのカスタマイズ
    st.subheader("📂 苗字リスト")
    st.write("デフォルトで内蔵リスト（約2.5万件）を使用します。")
    custom_surname_file = st.file_uploader(
        "カスタム苗字リストをアップロード (任意)",
        type=["txt"],
        help="1行に1つの苗字を記載したテキストファイルをアップロードしてください。"
    )

    st.markdown("---")
    
    st.subheader("❓ ヘルプ")
    with st.expander("使い方"):
        st.write("""
        1. 変換したい氏名を入力またはファイルをアップロードします。
        2. サイドバーで文字数（5字または7字）を選択します。
        3. 「処理実行」ボタンをクリックします。
        4. 結果をコピーまたはダウンロードします。
        """)

# --- メインエリア ---

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("<h2 class='sub-header'>1. 名前入力</h2>", unsafe_allow_html=True)
    
    input_method = st.radio("入力方法を選択:", ["テキストエリア", "ファイルアップロード (CSV/Excel)"])
    
    name_list = []
    
    if input_method == "テキストエリア":
        name_input = st.text_area(
            "変換したい氏名を入力してください（一行に一つ）:",
            height=300,
            placeholder="田中太郎\n佐藤二朗\n...",
            help="一行に一つの氏名を入力してください。"
        )
        if name_input:
            name_list = [line.strip() for line in name_input.split("\n") if line.strip()]
            
    else:
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
                    st.success(f"{len(name_list)} 件の氏名を読み込みました。")
                    
            except Exception as e:
                st.error(f"ファイルの読み込みに失敗しました: {e}")

with col2:
    st.markdown("<h2 class='sub-header'>2. 処理と結果</h2>", unsafe_allow_html=True)
    
    if not name_list:
        st.info("左側のパネルで氏名を入力してください。")
    else:
        if st.button("🚀 処理実行", use_container_width=True):
            with st.spinner("苗字リストを準備中..."):
                if custom_surname_file is not None:
                    surname_list = load_custom_surname_list(custom_surname_file)
                else:
                    surname_list = load_default_surname_list()
            
            if not surname_list:
                st.error("苗字リストが読み込めませんでした。")
            else:
                with st.spinner("整形処理を実行中..."):
                    formatted_names, skipped_names = process_names(
                        name_list, surname_list, char_count
                    )
                
                st.success("処理が完了しました！")
                
                result_text = "\n".join(formatted_names)
                st.text_area("整形結果 (コピー用):", value=result_text, height=300)
                
                st.download_button(
                    label="📥 結果をダウンロード (.txt)",
                    data=result_text,
                    file_name="formatted_names.txt",
                    mime="text/plain",
                    use_container_width=True
                )
                
                if skipped_names:
                    with st.expander(f"⚠️ 処理されなかった名前 ({len(skipped_names)}件)"):
                        st.write("苗字リストに存在しなかったため分割できなかった氏名です。")
                        for line_no, name in skipped_names:
                            st.write(f"- {line_no}行目: {name}")

# フッター
st.markdown(
    "<footer>© 2025 日本語DTP字取りツール | Created with Streamlit</footer>",
    unsafe_allow_html=True
)
