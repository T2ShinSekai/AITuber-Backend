# AITuber FastAPI プロジェクト

## 概要
このレポジトリは、視聴者とインタラクティブにコミュニケーションするAI Vtuberを開発するためのバックエンドAPIを提供します。このAPIは、[「視聴者とコミュニケーションするAITuberをゼロから開発する本」](https://techbookfest.org/product/gq3Rq6rpmpx6TRSW3A4XbR)で紹介されている実装をベースにしています。リアルタイムの視聴者のコメントに対してAIが反応し、YouTube APIを通じて動画コンテンツを管理する機能を提供します。

### 機能
- AIによるコメントのリアルタイム応答
- YouTube APIを使用した動画の管理
- ニュースAPIを介した最新情報の取得と配信

### 始め方

#### 必要条件
- Python 3.8 以上
- FastAPI
- Uvicorn
- miniconda

#### インストール手順

プロジェクトのルートディレクトリに移動し、以下のコマンドを実行して依存関係をインストールします。

```bash
conda create --name aituber python=3.8
conda activate aituber
pip install -r requirements.txt
```


#### 実行方法

以下のコマンドでAPIサーバーを起動します。
```bash
uvicorn main:app --reload
```

#### .env の設定について
プロジェクトに必要なAPIキーを.envファイルに設定します。以下の形式でファイルを作成し、各APIキーを入力してください。
```bash
OPENAI_API_KEY=your_openai_api_key
OPENSSL_SECRET_KEY=your_openssl_secret_key
YOUTUBE_API_KEY=your_youtube_api_key
YOUTUBE_VIDEO_ID=your_youtube_video_id
NEWS_API_KEY=your_news_api_key
```

#### API ドキュメント
APIのエンドポイントと使用方法については、サーバーを起動した後にhttp://localhost:8000/docs# でアクセスすることで確認できるSwagger UIを参照してください。

