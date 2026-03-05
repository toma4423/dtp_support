"""
日本語DTP字取りツール

このアプリケーションは、テキストフィールドまたはファイルから入力された日本語氏名を、
指定された文字数（5字または7字）で整形し、DTP処理に適した形式で出力します。
"""

import os
from typing import List, Optional, Set, Tuple

import pandas as pd
import streamlit as st

# 自作モジュールのインポート
from pattern5 import format_name_5chars_rule
from pattern7 import format_name_7chars_rule

# --- 定数 ---
DEFAULT_SURNAME_FILE = "surnames.txt"
BACKUP_SURNAME_FILE = "苗字リスト.txt"


def init_page():
    """ページ初期設定"""
    st.set_page_config(
        page_title="日本語DTP字取りツール",
        page_icon="📝",
        layout="centered",  # 1カラムのシンプルなレイアウト
    )

    # CSSスタイルの追加
    st.markdown(
        """
    <style>
        /* メイン背景とフォント */
        .stApp {
            background-color: var(--background-color);
        }
        
        /* ヘッダー */
        .main-header {
            font-size: 2.8rem;
            font-weight: 800;
            color: var(--text-color);
            text-align: center;
            margin-bottom: 0.5rem;
            letter-spacing: -0.025em;
        }
        .main-subheader {
            font-size: 1.1rem;
            color: var(--text-color);
            opacity: 0.7;
            text-align: center;
            margin-bottom: 3rem;
        }
        
        /* セクション見出し */
        .sub-header {
            font-size: 1.4rem;
            font-weight: 700;
            color: var(--text-color);
            margin-top: 2.5rem;
            margin-bottom: 1.2rem;
            padding-left: 0.8rem;
            border-left: 5px solid #3b82f6;
        }
        
        /* カード風のボックス */
        .custom-card {
            background-color: var(--secondary-background-color);
            padding: 1.5rem;
            border-radius: 0.8rem;
            border: 1px solid rgba(128, 128, 128, 0.2);
            box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
            margin-bottom: 1.5rem;
        }
        
        /* 成功・エラーボックスのカスタマイズ */
        .stAlert {
            border-radius: 0.8rem;
        }
        
        /* 結果エリア */
        .result-label {
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: var(--text-color);
        }
        
        /* フッター */
        .footer {
            text-align: center;
            margin-top: 5rem;
            padding: 2rem;
            color: var(--text-color);
            opacity: 0.5;
            font-size: 0.9rem;
            border-top: 1px solid rgba(128, 128, 128, 0.2);
        }

        /* アニメーション用JSのトリガー（ダミー） */
        #scroll-target {
            height: 0px;
        }
    </style>
    
    <script>
        // 処理完了時に結果までスクロールさせる簡単なJS
        function scrollToResult() {
            const el = window.parent.document.querySelector('[data-testid="stTextArea"]');
            if (el) {
                el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    </script>
    """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_default_surname_list() -> List[str]:
    """デフォルトの苗字リストを読み込む"""
    filename = (
        DEFAULT_SURNAME_FILE
        if os.path.exists(DEFAULT_SURNAME_FILE)
        else BACKUP_SURNAME_FILE
    )

    if not os.path.exists(filename):
        return []

    try:
        # UTF-8, Shift-JIS, CP932を順に試す
        for enc in ["utf-8", "shift-jis", "cp932"]:
            try:
                with open(filename, encoding=enc) as f:
                    surnames = [line.strip() for line in f if line.strip()]
                if surnames:
                    # 長い順にソートして最長一致を実現
                    surnames.sort(key=len, reverse=True)
                    return surnames
            except UnicodeDecodeError:
                continue
    except Exception:
        pass
    return []


def load_custom_surname_list(uploaded_file) -> List[str]:
    """アップロードされた苗字リストを読み込む"""
    try:
        content = uploaded_file.getvalue()
        for enc in ["utf-8", "shift-jis", "cp932"]:
            try:
                text = content.decode(enc)
                surnames = [line.strip() for line in text.splitlines() if line.strip()]
                if surnames:
                    surnames.sort(key=len, reverse=True)
                    return surnames
            except UnicodeDecodeError:
                continue
    except Exception as e:
        st.error(f"苗字リストの読み取りに失敗しました: {e}")
    return []


def split_name_smart(
    full_name: str, surname_set: Set[str], max_surname_len: int
) -> Tuple[Optional[str], Optional[str]]:
    """最長一致で苗字と名前に分割する"""
    for length in range(min(len(full_name), max_surname_len), 0, -1):
        potential_surname = full_name[:length]
        if potential_surname in surname_set:
            return potential_surname, full_name[length:]
    return None, None


def process_names(names: List[str], surname_list: List[str], target_length: int):
    """名前リストを処理する"""
    surname_set = set(surname_list)
    max_surname_len = max(len(s) for s in surname_list) if surname_list else 0

    formatted_names = []
    skipped_names = []

    progress_bar = st.progress(0)
    total = len(names)

    for i, full_name in enumerate(names):
        full_name = str(full_name).strip()
        if not full_name:
            continue

        surname, given_name = split_name_smart(full_name, surname_set, max_surname_len)

        if surname is None:
            skipped_names.append((i + 1, full_name))
            formatted_names.append(full_name)
        else:
            fmt_func = (
                format_name_5chars_rule
                if target_length == 5
                else format_name_7chars_rule
            )
            formatted_names.append(fmt_func(surname, given_name))

        if (i + 1) % 10 == 0 or (i + 1) == total:
            progress_bar.progress((i + 1) / total)

    return formatted_names, skipped_names


def main():
    init_page()

    # タイトル
    st.markdown('<h1 class="main-header">日本語DTP字取りツール</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="main-subheader">名簿リストを指定された文字数（5字・7字）に自動整形します</p>',
        unsafe_allow_html=True,
    )

    # サイドバー
    with st.sidebar:
        st.header("⚙️ 設定")
        char_option = st.radio("目標文字数を選択:", ["5字取り", "7字取り"], index=0)
        target_len = 5 if char_option == "5字取り" else 7

        st.divider()
        st.subheader("💡 使い方")
        st.info("1. 名前を入力またはアップロード\n2. 目標文字数を選択\n3. 処理実行をクリック")

    # メインコンテンツ
    st.markdown('<h2 class="sub-header">1. 名前リストの入力</h2>', unsafe_allow_html=True)

    input_method = st.radio(
        "入力方法:", ["テキストエリア", "ファイルアップロード (CSV/Excel)"], horizontal=True
    )

    name_list = []
    if input_method == "テキストエリア":
        name_input = st.text_area(
            "氏名を一行に一つずつ入力してください:",
            height=200,
            placeholder="田中太郎\n佐藤二朗",
        )
        if name_input:
            name_list = [line.strip() for line in name_input.splitlines() if line.strip()]
    else:
        uploaded_data = st.file_uploader(
            "ファイルをアップロード", type=["csv", "xlsx", "xls"]
        )
        if uploaded_data:
            try:
                if uploaded_data.name.endswith(".csv"):
                    # 文字コード判定
                    content = uploaded_data.read()
                    df = None
                    for enc in ["utf-8", "shift-jis", "cp932"]:
                        try:
                            df = pd.read_csv(pd.io.common.BytesIO(content), encoding=enc)
                            break
                        except Exception:
                            continue
                else:
                    df = pd.read_excel(uploaded_data)

                if df is not None:
                    st.dataframe(df.head(3), use_container_width=True)
                    target_col = st.selectbox("氏名が含まれる列を選択:", df.columns)
                    if target_col:
                        name_list = df[target_col].dropna().astype(str).tolist()
                else:
                    st.error("ファイルの読み込みに失敗しました。")
            except Exception as e:
                st.error(f"エラー: {e}")

    st.markdown('<h2 class="sub-header">2. 苗字リストの設定</h2>', unsafe_allow_html=True)
    st.write("デフォルトで約2.5万件のリストを使用します。独自のリストが必要な場合のみアップロードしてください。")
    custom_surname_file = st.file_uploader(
        "カスタム苗字リスト (任意)", type=["txt"], key="custom_surnames"
    )

    st.markdown('<div id="scroll-target"></div>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">3. 実行と結果</h2>', unsafe_allow_html=True)

    if not name_list:
        st.warning("名前リストが空です。")
    else:
        if st.button("🚀 処理を実行する", use_container_width=True, type="primary"):
            # 苗字リスト準備
            with st.spinner("準備中..."):
                if custom_surname_file:
                    surname_list = load_custom_surname_list(custom_surname_file)
                else:
                    surname_list = load_default_surname_list()

            if not surname_list:
                st.error("苗字リストを読み込めませんでした。")
            else:
                # 処理
                with st.spinner("変換中..."):
                    formatted, skipped = process_names(
                        name_list, surname_list, target_len
                    )

                st.success(f"完了! (全 {len(formatted)} 件)")

                # 結果表示
                res_text = "\n".join(formatted)
                st.markdown('<p class="result-label">整形結果:</p>', unsafe_allow_html=True)
                st.text_area("result", value=res_text, height=300, label_visibility="collapsed")

                st.download_button(
                    "📥 結果をダウンロード (.txt)",
                    data=res_text,
                    file_name="formatted_names.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

                if skipped:
                    with st.expander(f"⚠️ 判定できなかった名前 ({len(skipped)}件)"):
                        for line_no, name in skipped:
                            st.write(f"- {line_no}行目: {name}")

    # フッター
    st.markdown(
        '<div class="footer">© 2025 日本語DTP字取りツール | Modernized DTP Utility</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
