# 動的カラム対応について

このFAISS検索APIは、CSVファイルのカラム構造が変化しても自動的に対応できるように設計されています。

## カラム自動検出の仕組み

### 1. テキストカラムの優先順位検出

以下の順序でテキストカラムを検出し、ログに出力されます：

```
1. title (タイトル)
2. content (内容)
3. name (名前)
4. description (説明)
5. text (テキスト)
6. summary (要約)
7. body (本文)
```

### 2. 自動フォールバック

優先カラムが見つからない場合：

- 文字列型（object）のカラムを自動検出
- 除外対象：id, category, tag, url, author

### 3. 最小構成対応

どのカラムも見つからない場合：

- 'id'以外の最初のカラムを使用

## ログ出力例

検出されたテキストカラムはログに出力されます：

```
INFO:src.faiss_serch:検出されたテキストカラム: ['title', 'content']
```

## 対応例

### 標準構造
```csv
id,title,content,category
1,タイトル1,内容1,カテゴリ1
```
→ 使用カラム: `['title', 'content']`

### 拡張構造
```csv
id,name,description,url,author,tags
1,名前1,説明1,URL1,著者1,タグ1
```
→ 使用カラム: `['name', 'description']`

### 最小構造
```csv
item,info
製品A,高品質な製品です
```
→ 使用カラム: `['item', 'info']`

## 検索結果の動的対応

検索結果では、CSVのすべてのカラムが自動的に含まれます：

```json
{
  "rank": 1,
  "similarity_score": 0.8542,
  "id": 1,
  "title": "FastAPIの基本的な使い方",
  "content": "FastAPIはPython...",
  "category": "API開発"
}
```

## 注意点

1. **CSVフォーマット**: カンマを含むフィールドは引用符で囲む
   ```csv
   id,name,tags
   1,Python講座,"Python,入門,プログラミング"
   ```

2. **データ型の自動変換**:
   - 整数型 → `int()`
   - 浮動小数点型 → `float()`
   - その他 → `str()`

3. **エラーハンドリング**: カラム処理エラーは空文字列で補完

## テスト方法

```bash
# 仮想環境をアクティベート
.\.venv\Scripts\Activate.ps1

# 動的カラムテストを実行
python tests/test_dynamic_columns.py
```

この機能により、様々なCSV構造に対して柔軟に対応できます。