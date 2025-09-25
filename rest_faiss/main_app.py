from fastapi import FastAPI, HTTPException, Query
from contextlib import asynccontextmanager
from typing import Dict, Any
import pandas as pd
import logging
import os
from .faiss_serch import FaissSearch

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 固有名詞正規化辞書
noun_normalizer = {}


def load_noun_normalizer():
    """noun_base.csvから固有名詞の正規化辞書を作成"""
    global noun_normalizer
    try:
        noun_df = pd.read_csv("DATA/noun_base.csv")
        noun_normalizer = dict(zip(noun_df["original"], noun_df["normalized"]))
        logger.info(f"固有名詞辞書を読み込みました: {len(noun_normalizer)}件")
    except Exception as e:
        logger.warning(f"固有名詞辞書の読み込みに失敗: {e}")


def normalize_query(text: str) -> str:
    """検索クエリの固有名詞を正規化"""
    normalized_text = text
    for original, normalized in noun_normalizer.items():
        normalized_text = normalized_text.replace(original, normalized)
    return normalized_text


# FAISSインデックスを初期化
faiss_search = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    # アプリケーション起動時の初期化処理
    global faiss_search

    # 固有名詞辞書をロード
    load_noun_normalizer()

    # FAISSインデックスを構築
    try:
        knowledge_path = "DATA/knowledge_data.csv"
        if os.path.exists(knowledge_path):
            faiss_search = FaissSearch(knowledge_path)
            logger.info("FAISSインデックスの構築が完了しました")
        else:
            logger.error(f"知識データファイルが見つかりません: {knowledge_path}")
    except Exception as e:
        logger.error(f"FAISSインデックスの構築に失敗: {e}")

    yield  # アプリケーションの実行

    # アプリケーション終了時のクリーンアップ処理（必要に応じて）
    logger.info("アプリケーションを終了します")


app = FastAPI(
    title="FAISS Knowledge Search API", description="LLMのRAGのためのFAISS検索API", version="1.0.0", lifespan=lifespan
)


@app.get("/")
async def root():
    """APIの基本情報を返す"""
    return {
        "message": "FAISS Knowledge Search API",
        "version": "1.0.0",
        "endpoints": ["/get_knowledge?text=検索文字列&n=3"],
    }


@app.get("/get_knowledge")
async def get_knowledge(
    text: str = Query(..., description="検索対象のテキスト"),
    n: int = Query(
        3, description="返却する上位結果の数（デフォルト3、最大100。ただし実際のデータ件数が上限）", ge=1, le=100
    ),
) -> Dict[str, Any]:
    """
    知識ベースから類似したコンテンツを検索する

    Args:
        text: 検索クエリ
        n: 返却する結果数（デフォルト3、最大100。実際のデータ件数を超える場合は全件返却）

    Returns:
        検索結果のJSON（要求件数、データ総件数、実際の返却件数を含む）
    """

    if faiss_search is None:
        raise HTTPException(status_code=500, detail="FAISSインデックスが初期化されていません")

    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="検索テキストが空です")

    try:
        # クエリを正規化
        normalized_query = normalize_query(text.strip())
        logger.info(f"検索クエリ: '{text}' -> 正規化後: '{normalized_query}'")

        # データベース内の総件数を取得
        total_data_count = len(faiss_search.data)

        # FAISS検索実行（データ件数以上は要求できない）
        actual_n = min(n, total_data_count)
        results = faiss_search.search(normalized_query, actual_n)

        response = {
            "query": text,
            "normalized_query": normalized_query,
            "requested_count": n,
            "total_data_count": total_data_count,
            "actual_returned_count": len(results),
            "results": results,
        }

        if n > total_data_count:
            logger.info(
                f"検索完了: 要求件数{n}件に対してデータベース内の総件数{total_data_count}件のため、{len(results)}件を返却"
            )
        else:
            logger.info(f"検索完了: {len(results)}件の結果を返却")

        return response

    except Exception as e:
        logger.error(f"検索エラー: {e}")
        raise HTTPException(status_code=500, detail=f"検索処理でエラーが発生しました: {str(e)}")


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {
        "status": "healthy",
        "faiss_ready": faiss_search is not None,
        "noun_normalizer_loaded": len(noun_normalizer) > 0,
        "total_data_count": len(faiss_search.data) if faiss_search else 0,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
