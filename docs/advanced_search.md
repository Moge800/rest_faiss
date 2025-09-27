# 高度な検索機能

このAPIでは基本的な類似度検索に加えて、より柔軟な検索を可能にする高度な機能を提供しています。

## モデル情報

現在使用しているモデル: **intfloat/multilingual-e5-large**

- **特徴**: 多言語対応で日本語の性能が高く、検索タスクに最適化
- **ベクトル次元**: 1024次元
- **サイズ**: 約2.5GB
- **利点**: 高精度な意味検索と日本語での優れたパフォーマンス

## 類似度スコア閾値フィルタリング

### `threshold` パラメータ

指定した類似度スコア以上の結果のみを返却します。

- **範囲**: 0.0〜1.0
- **デフォルト**: 0.5
- **使用例**:
  ```bash
  curl "http://localhost:8000/get_knowledge?text=検索語&threshold=0.7"
  ```

### 効果

- **高い値（0.8〜1.0）**: 非常に関連性の高い結果のみ
- **中間値（0.5〜0.7）**: バランスの取れた結果
- **低い値（0.1〜0.4）**: より広範囲の結果

## フォールバック機能

### `fallback` パラメータ

閾値を満たす結果が少ない場合に、自動的に閾値を下げて再検索を行います。

- **デフォルト**: false
- **使用例**:
  ```bash
  curl "http://localhost:8000/get_knowledge?text=検索語&threshold=0.8&fallback=true&min_k=3"
  ```

### `min_k` パラメータ

フォールバック機能で保証する最小結果数を指定します。

- **範囲**: 1〜100
- **デフォルト**: 3
- **動作**: 結果数が`min_k`に満たない場合、閾値を半分にして再検索

### フォールバックのログ例

```
INFO:rest_faiss.faiss_serch:resultがmin_k[3]に満たないため、thresholdを[0.4]に下げて再検索します。
INFO:rest_faiss.faiss_serch:resultがmin_k[3]に満たないため、thresholdを[0.2]に下げて再検索します。
```

## 実用的な使用パターン

### パターン1: 高品質な結果のみ取得

```bash
curl "http://localhost:8000/get_knowledge?text=FastAPI&top_k=5&threshold=0.8"
```

- 類似度スコア0.8以上の結果のみ
- 最大5件まで取得
- 該当なしの場合は空の結果

### パターン2: 高品質優先、最低数保証

```bash
curl "http://localhost:8000/get_knowledge?text=FastAPI&top_k=5&threshold=0.8&fallback=true&min_k=3"
```

- 可能な限り類似度スコア0.8以上を優先
- 0.8以上が3件未満の場合、閾値を下げて最低3件確保
- 最終的には最大5件まで返却

### パターン3: バランス型検索

```bash
curl "http://localhost:8000/get_knowledge?text=FastAPI&top_k=10&threshold=0.6"
```

- 中程度の閾値で幅広い結果を取得
- 最大10件まで取得

## レスポンス形式の拡張

新しい機能を使用した場合のレスポンス例：

```json
{
  "query": "FastAPI",
  "normalized_query": "FastAPI",
  "requested_count": 5,
  "total_data_count": 20,
  "actual_returned_count": 3,
  "results": [
    {
      "rank": 1,
      "similarity_score": 0.8542,
      "id": 1,
      "title": "FastAPIの基本",
      "content": "FastAPIの詳細説明...",
      "category": "API開発"
    }
  ]
}
```

## 注意事項

1. **閾値の設定**: 高すぎる閾値は結果が0件になる可能性があります
2. **フォールバックの制限**: 閾値が0.01未満になると自動的に再検索を停止します
3. **パフォーマンス**: フォールバック機能は複数回検索を実行するため、若干の処理時間増加があります
4. **結果の順序**: フォールバック検索でも類似度スコアの高い順で結果を返却します