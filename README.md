# 自然言語入力によるGPUサーバー予約とAI優先度判定アプリ

プロジェクトの詳細は、所定のドキュメントを確認すること。

## 技術スタック

- **Backend**: Python (FastAPI)
- **Frontend**: React.js
- **Database**: SQLite
- **AI**: Google Gemini API
- **認証**: JWT

## プロジェクト構成

```
.
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   └── utils/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.js
│   ├── package.json
│   └── .env.example
├── docker-compose.yml
└── README.md
```

## セットアップ手順

### 前提条件

- Python 3.9+
- Node.js 16+
- Google Cloud Platform アカウント（Gemini API用）

### バックエンド

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# .envファイルにGemini APIキーを設定
python -m app.main
```

### フロントエンド

```bash
cd frontend
npm install
cp .env.example .env
npm start
```

## 環境変数

### Backend (.env)

```
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///./gpu_reservation.db
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend (.env)

```
REACT_APP_API_URL=http://localhost:8000
```

## API エンドポイント

- `POST /api/auth/register` - ユーザー登録
- `POST /api/auth/login` - ログイン
- `GET /api/reservations` - 予約一覧取得
- `POST /api/reservations` - 新規予約作成（自然言語入力）
- `PUT /api/reservations/{id}` - 予約更新
- `DELETE /api/reservations/{id}` - 予約キャンセル
- `POST /api/reservations/{id}/confirm-rejection` - 拒否確認
- `GET /api/servers` - サーバー一覧取得

## 実装
⏺ Update Todos
  ⎿  ☐ プロジェクトのディレクトリ構造を作成
     ☐ バックエンドの基本設定とモデル作成
     ☐ 認証機能の実装
     ☐ 予約管理APIの実装
     ☐ Gemini APIを使った自然言語処理と優先度判定機能の実装
     ☐ フロントエンドの基本設定
     ☐ フロントエンドのコンポーネント実装
     ☐ Docker設定の作成

## バックエンド（FastAPI）
  - 認証機能（JWT）
  - 予約管理API
  - Gemini APIを使った自然言語処理と優先度判定
  - SQLiteデータベース

## フロントエンド（React + TypeScript）
  - ログイン/登録画面
  - ダッシュボード
  - 自然言語での予約作成
  - 予約一覧表示
  - 拒否確認待ち予約の処理

## 使用方法
  1. バックエンドの.envファイルを作成し、Gemini APIキーを設定
  2. cd backend && pip install -r requirements.txt && python -m app.main
  3. cd frontend && npm install && npm start

  またはDockerを使用：docker-compose up