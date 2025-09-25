import faiss
from typing import List, Dict, Any
import pandas as pd
from sentence_transformers import SentenceTransformer
import logging

# ロガーの設定
logger = logging.getLogger(__name__)


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
            except Exception as e:
                logger.error(f"モデルの初期化に失敗しました: {e}")
                raise e
            logger.info("モデル初期化完了")
        return self._model


class FaissSearch:
    def __init__(self, csv_path: str):
        # シングルトンのモデルマネージャーを使用
        self.model_manager = ModelManager()
        self.model = self.model_manager.get_model()
        self.data = None
        self.index = None
        self.text_columns = []  # ベクトル化に使用するテキストカラム
        self.make_index(csv_path)

    def detect_text_columns(self, df: pd.DataFrame) -> List[str]:
        """テキストカラムを自動検出"""
        text_columns = []

        # 優先順位でテキストカラムを検出
        priority_columns = ["title", "content", "name", "description", "text", "summary", "body"]

        for col in priority_columns:
            if col in df.columns:
                text_columns.append(col)

        # 優先カラムが見つからない場合、文字列型のカラムを自動検出
        if not text_columns:
            for col in df.columns:
                if df[col].dtype == "object" and col.lower() not in ["id", "category", "tag", "url", "author"]:
                    text_columns.append(col)

        # 最低限1つのテキストカラムが必要
        if not text_columns:
            # 'id'以外の最初のカラムを使用
            available_cols = [col for col in df.columns if col.lower() != "id"]
            if available_cols:
                text_columns = [available_cols[0]]
            else:
                raise ValueError("テキスト化可能なカラムが見つかりません")

        return text_columns

    def make_index(self, csv_path: str):
        # CSVデータを読み込み
        self.data = pd.read_csv(csv_path)

        # テキストカラムを自動検出
        self.text_columns = self.detect_text_columns(self.data)
        logger.info(f"検出されたテキストカラム: {self.text_columns}")

        # テキストカラムを結合してベクトル化
        texts = []
        for _, row in self.data.iterrows():
            combined_text = " ".join([str(row[col]) for col in self.text_columns if pd.notna(row[col])])
            texts.append(combined_text)

        vectors = self.model.encode(texts, show_progress_bar=False)

        # FAISSインデックスを構築
        dimension = vectors.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(vectors.astype("float32"))

        logger.info(f"FAISSインデックスが作成されました。データ数: {self.index.ntotal}, 次元数: {dimension}")

    def search(self, query_text: str, top_k: int) -> List[Dict[str, Any]]:
        # クエリテキストをベクトル化
        query_vector = self.model.encode([query_text], show_progress_bar=False)

        # FAISS検索実行
        distances, indices = self.index.search(query_vector.astype("float32"), top_k)

        # 結果を構造化して返す
        results = []
        for i, (idx, distance) in enumerate(zip(indices[0], distances[0])):
            if idx != -1:  # 有効なインデックスの場合
                row = self.data.iloc[idx]

                # 距離を類似度スコアに変換
                similarity_score = 1 / (1 + distance)

                # しきい値未満であればスキップ
                if similarity_score < threshold:
                    continue

                # 基本的な結果構造
                result = {"rank": i + 1, "similarity_score": float(similarity_score)}

                # 各カラムを動的に追加
                for col in self.data.columns:
                    try:
                        value = row[col]
                        # 数値型の場合は適切に変換
                        if pd.api.types.is_integer_dtype(self.data[col]):
                            result[col] = int(value)
                        elif pd.api.types.is_float_dtype(self.data[col]):
                            result[col] = float(value)
                        else:
                            result[col] = str(value) if pd.notna(value) else ""
                    except Exception as e:
                        logger.error(f"カラム '{col}' の処理でエラー: {e}")
                        result[col] = ""

                results.append(result)

        return results
