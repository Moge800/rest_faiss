# モデルのキャッシュとパフォーマンス最適化

## モデルのダウンロードとキャッシュ

### 初回実行時のログ出力
```
INFO:rest_faiss.faiss_serch:モデルを初期化中: paraphrase-multilingual-MiniLM-L12-v2
Downloading (…)_Pooling/config.json: 100%|██| 190/190 [00:00<?, ?B/s]
Downloading (…)7e55ad/.gitattributes: 100%|██| 1.18k/1.18k [00:00<?, ?B/s]
...
INFO:rest_faiss.faiss_serch:モデル初期化完了
```

### 2回目以降のログ出力
```
INFO:rest_faiss.faiss_serch:モデルを初期化中: paraphrase-multilingual-MiniLM-L12-v2
INFO:rest_faiss.faiss_serch:モデル初期化完了  # ダウンロードなし、キャッシュから読み込み
```

## キャッシュ場所

### Windows
```
C:\Users\[ユーザー名]\.cache\huggingface\hub\models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2\
```

### Linux/macOS
```
~/.cache/huggingface/hub/models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2/
```

## パフォーマンス最適化

### 1. シングルトンパターンによるモデル共有

```python
class ModelManager:
    """モデルのシングルトン管理クラス"""
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_model(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        """モデルをキャッシュから取得、初回のみダウンロード"""
        if self._model is None:
            logger.info(f"モデルを初期化中: {model_name}")
            try:
                self._model = SentenceTransformer(model_name)
                logger.info("モデル初期化完了")
            except Exception as e:
                logger.error(f"モデルの初期化に失敗しました: {e}")
                raise e
        return self._model
```

### 2. 利点

- **初回のみダウンロード**: Hugging Faceのキャッシュシステムを利用
- **メモリ効率**: 複数のFaissSearchインスタンス間でモデルを共有
- **高速起動**: 2回目以降のインスタンス作成が高速

### 3. 使用例

```python
# 1つ目のインスタンス（モデル初期化）
search1 = FaissSearch("data1.csv")  # モデルダウンロード＋初期化

# 2つ目のインスタンス（モデル再利用）
search2 = FaissSearch("data2.csv")  # モデル再利用、初期化なし

# 3つ目のインスタンス（モデル再利用）
search3 = FaissSearch("data3.csv")  # モデル再利用、初期化なし
```

## モデルサイズと性能

### paraphrase-multilingual-MiniLM-L12-v2
- **サイズ**: 約471MB
- **対応言語**: 多言語（日本語含む）
- **ベクトル次元**: 384次元
- **特徴**: 軽量で高性能

### 他のモデルオプション

```python
# より軽量なモデル
model_manager.get_model("paraphrase-multilingual-mpnet-base-v2")

# 日本語特化モデル
model_manager.get_model("sonoisa/sentence-bert-base-ja-mean-tokens-v2")
```

## キャッシュ管理

### キャッシュクリア（必要に応じて）
```python
from huggingface_hub import HfApi
HfApi().delete_cache()
```

### 環境変数でキャッシュディレクトリを変更
```bash
export HF_HOME=/path/to/your/cache
```

この最適化により、APIサーバーの起動時間が大幅に短縮され、メモリ使用量も削減されます。