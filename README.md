# FAISS Knowledge Search API

LLMのRAG（Retrieval-Augmented Generation）のためのFAISS検索APIです。

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.117.1-009639.svg)

## ✨ 特徴

- 🚀 **高速検索**: FAISSによる高速な近似最近傍探索
- 🌐 **多言語対応**: sentence-transformersの多言語モデルを使用
- 🔧 **動的カラム対応**: CSVのカラム構造が変わっても自動対応
- 📊 **詳細な検索結果**: データ件数情報を含む充実したレスポンス
- 💾 **モデルキャッシュ**: シングルトンパターンによる効率的なメモリ使用
- ⚡ **型安全**: Pydanticによる型検証
- 🛠️ **テスト完備**: 包括的なテストスイート

## 機能

- CSV形式の知識データベースからの高速類似度検索
- 固有名詞の正規化機能（略称や文字のゆらぎ対応）
- RESTful API設計
- JSON形式でのレスポンス

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

**注意**: `requirements.txt`には全ての依存関係（`pip freeze`の結果）が含まれています。
主要なパッケージのみをインストールする場合は以下を使用してください：

```bash
pip install fastapi uvicorn faiss-cpu pandas sentence-transformers
```

### 2. データ準備

`DATA/` フォルダに以下のCSVファイルを配置してください：

#### knowledge_data.csv
知識データベースファイル（必須）
```csv
id,title,content,category
1,FastAPIの基本的な使い方,FastAPIはPythonで高速なAPIを構築するためのフレームワークです。,API開発
```

#### noun_base.csv  
固有名詞正規化辞書（任意）
```csv
original,normalized
API,API
api,API
えーぴーあい,API
```

### 3. サーバー起動

```bash
python start_server.py
```

サーバーは `http://localhost:8000` で起動します。

### 4. テスト実行

```bash
# API基本テスト
python tests/test_api.py

# n=100件検索テスト
python tests/test_n100.py

# 動的カラム対応テスト
python tests/test_dynamic_columns.py
```

## API使用方法

### エンドポイント

#### GET /get_knowledge

知識ベースから類似したコンテンツを検索します。

**パラメータ:**
- `text` (string, 必須): 検索対象のテキスト
- `n` (integer, 任意): 返却する上位結果の数（デフォルト：3、最大：100）

**重要な注意事項:**

- `n`で指定した件数よりもデータベース内のレコード数が少ない場合、実際のデータ件数分のみ返却されます
- レスポンスには要求件数、データベース総件数、実際の返却件数の情報が含まれます

**使用例:**
```bash
curl "http://localhost:8000/get_knowledge?text=FastAPIの使い方&n=3"
```

**レスポンス例:**

```json
{
  "query": "FastAPIの使い方",
  "normalized_query": "FastAPIの使い方",
  "requested_count": 3,
  "total_data_count": 20,
  "actual_returned_count": 2,
  "results": [
    {
      "rank": 1,
      "id": 1,
      "title": "FastAPIの基本的な使い方",
      "content": "FastAPIはPythonで高速なAPIを構築するためのフレームワークです。Pydanticベースの型検証と自動ドキュメント生成が特徴です。",
      "category": "API開発",
      "similarity_score": 0.8542
    }
  ]
}
```

#### GET /health

ヘルスチェックエンドポイント

**レスポンス例:**

```json
{
  "status": "healthy",
  "faiss_ready": true,
  "noun_normalizer_loaded": true,
  "total_data_count": 20
}
```

#### GET /

API情報とエンドポイント一覧

## 自動ドキュメント

サーバー起動後、以下のURLでSwagger UIが利用できます：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## アーキテクチャ

```text
├── start_server.py         # サーバー起動スクリプト
├── rest_faiss/
│   ├── __init__.py
│   ├── main_app.py        # FastAPI アプリケーション
│   └── faiss_serch.py     # FAISS検索クラス
├── DATA/
│   ├── knowledge_data.csv  # 知識データベース（20件のサンプルデータ）
│   ├── noun_base.csv      # 固有名詞正規化辞書
│   └── test_knowledge.csv # テスト用データ
├── tests/
│   ├── test_api.py        # API テストスクリプト
│   ├── test_n100.py       # n=100 検索テストスクリプト
│   └── test_dynamic_columns.py # 動的カラムテストスクリプト
├── docs/
│   ├── dynamic_columns.md  # 動的カラム対応の説明
│   └── model_cache.md     # モデルキャッシュの説明
├── requirements.txt       # Python依存関係（詳細版）
├── LICENSE               # MITライセンス
└── README.md            # このファイル
```

## 使用技術

- **FastAPI**: RESTful API フレームワーク
- **FAISS**: Facebook製高速類似度検索ライブラリ
- **sentence-transformers**: 多言語対応文章埋め込みモデル
- **pandas**: データ処理
- **uvicorn**: ASGI サーバー

## 特徴

1. **高速検索**: FAISSによる高速な近似最近傍探索
2. **多言語対応**: sentence-transformersの多言語モデルを使用
3. **固有名詞正規化**: 略称や表記ゆれに対応
4. **スケーラブル**: 大規模データセットに対応可能
5. **型安全**: Pydanticによる型検証
6. **動的カラム対応**: CSVのカラム構造が変わっても自動対応
7. **モデル最適化**: シングルトンパターンによる効率的なメモリ使用

## パフォーマンス最適化

### モデルキャッシュ

- **初回のみダウンロード**: Hugging Faceキャッシュシステムを利用
- **メモリ効率**: 複数インスタンス間でモデルを共有
- **高速起動**: シングルトンパターンによる初期化コスト削減

### キャッシュ場所

- Windows: `C:\Users\[ユーザー名]\.cache\huggingface\`
- Linux/macOS: `~/.cache/huggingface/`

## ライセンス

MIT License
