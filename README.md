# 日本語DTP字取りツール

## 概要

このアプリケーションは、名簿リスト（テキスト、CSV, Excel）に含まれる日本語氏名を、指定された文字数（5字または7字）で整形し、DTP処理に適した形式で出力するStreamlitアプリケーションです。

## アクセス

以下のURLからアプリケーションにアクセスできます。
[https://toma4423-dtp-support-app-y69c0d.streamlit.app/](https://toma4423-dtp-support-app-y69c0d.streamlit.app/)

## 機能

- **多彩な入力方式**: テキストエリアへの直接入力、またはCSV/Excelファイルのアップロードに対応。
- **自動苗字判定**: 約2.5万件の苗字リスト（surnames.txt）を内蔵。氏名から苗字と名前を自動的に分割します。
- **カスタム苗字リスト（surnames.txt）**: 独自の苗字リスト（surnames.txt）（テキストファイル）をアップロードして使用することも可能です。
- **5字取り・7字取り**: 日本語DTPの慣習に基づいた文字数整形ルールを適用。
- **一括処理とダウンロード**: 処理結果をワンクリックでテキストファイルとしてダウンロード可能。

## インストール方法（ローカル実行）

1. リポジトリをクローン
```bash
git clone https://github.com/toma4423/dtp_support.git
cd dtp_support
```

2. 仮想環境を作成し、アクティベート
```bash
python -m venv venv
source venv/bin/activate  # Linux/Macの場合
venv\Scripts\activate     # Windowsの場合
```

3. 必要なパッケージをインストール
```bash
pip install -r requirements.txt
```

## 使用方法

1. アプリケーションを起動
```bash
streamlit run app.py
```

2. ブラウザで表示されたURL（通常は http://localhost:8501 ）にアクセス

3. **名前の入力**:
   - テキストエリアに直接入力するか、CSV/Excelファイルをアップロードします。
   - ファイルの場合は、氏名が含まれる列を選択してください。

4. **設定**:
   - サイドバーで「5字取り」または「7字取り」を選択します。
   - 必要に応じてカスタムの苗字リスト（surnames.txt）をアップロードします。

5. **処理実行**:
   - 「処理実行」ボタンをクリックすると、右側に結果が表示されます。

6. **結果の保存**:
   - 結果をコピーするか、「結果をダウンロード」ボタンで保存します。

## 注意事項

- アップロード可能なファイルサイズはStreamlit Cloudの制限（通常200MB）に準じます。
- 苗字リスト（surnames.txt）にない氏名は自動分割ができず、そのまま出力されます（「処理されなかった名前」として表示されます）。

## ライセンス

MIT License 
