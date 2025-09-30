#!/usr/bin/env python3
"""
FAISS Knowledge Search API 起動スクリプト
"""

import os


def check_data_files():
    """必要なデータファイルが存在するかチェック"""
    required_files = ["DATA/knowledge_data.csv", "DATA/noun_base.csv"]

    missing_files = []

    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"✗ {file_path} (ファイルが見つかりません)")

    return missing_files


def start_server():
    """APIサーバーを起動"""
    print("\n=== APIサーバーを起動中 ===")
    try:
        import uvicorn
        from rest_faiss.main_app import app

        print(f"サーバーは http://{HOST}:{PORT} で起動します")
        print(f"Swagger UI: http://{HOST}:{PORT}/docs")
        print("停止するには Ctrl+C を押してください\n")

        uvicorn.run(app, host=HOST, port=PORT, log_level="info")

    except ImportError as e:
        print(f"エラー: 必要なパッケージが見つかりません - {e}")
        return False
    except Exception as e:
        print(f"エラー: サーバーの起動に失敗しました - {e}")
        return False

    return True


def main():

    missing_files = check_data_files()

    if missing_files:
        print("\n⚠️  以下のファイルを作成してください:")
        for file_path in missing_files:
            print(f"   {file_path}")
        return

    start_server()


if __name__ == "__main__":
    PORT = 8000
    HOST = "0.0.0.0"
    main()
