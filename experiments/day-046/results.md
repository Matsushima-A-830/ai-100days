# Day 046 results — PurpleDoubleD/locally-uncensored

Routine環境の制約により未検証、ローカル検証待ち。

検証に着手する前段階(リポジトリの取得・ライセンス確認・依存インストールの可否・Ollama導入元への
ネットワーク到達性)を確認したところ、下記2点が重なりコア機能(ローカルチャット・コーディング
エージェント)を一切実行できなかった。詳細は [`README.md`](./README.md) を参照。

1. クローンしたリポジトリ自身のコード実行(`npm install`)が、本Routine実行環境の権限自動分類器により
   `[Code from External]` として拒否された(cwdをclone先の内側/外側のどちらにしても拒否された)。
2. Ollamaのインストール元ホスト(`ollama.com`)が本Routine実行環境のネットワークポリシーで
   ブロックされていた(`CONNECT` 403)。

1はDay 024・Day 032・Day 043で遭遇した「本Routineの無人自動実行モードが外部コードの実行を拒否する」
制約と同種、2は過去のCLAUDE.md「書かない(Routine環境の制約)」の既存例(ネットワーク制限による
自動ダウンロードのブロック)と同種の、本Routine実行環境固有の制約と判断した。いずれも対象ツール
自体の欠陥ではないため、記事等には書かない。

`npm install` が通らないため、ブラウザ向け開発モード(`npm run dev`)・デスクトップビルド
(`npm run tauri:build`)のいずれも後続作業として実行できず、チャット機能・コーディングエージェント
機能の動作確認(今回の検証の核心)には到達できなかった。

静的に確認できた事実(読んだだけで、動かして確認したわけではない内容):

- ライセンス: `LICENSE`ファイル全文がAGPL-3.0(GNU AFFERO GENERAL PUBLIC LICENSE Version 3)。
  `package.json`の`"license": "AGPL-3.0-only"`とも一致。
- アーキテクチャ: Tauri(Rust+React/Vite)デスクトップアプリ本体 + `dev-server/`配下のNodeサーバーが
  ブラウザ向け開発モードでOllama連携・ファイルアクセス・シェル実行等をプロキシする構成。
- 「Bring your own engine」としてOllama/LM Studio/Jan/GPT4All/KoboldCpp/llama.cpp/vLLM/LocalAI/
  text-generation-webui/TabbyAPI/Aphrodite/SGLangの12種類を自動検出すると明記。
- CLI専用モード・`--host`フラグ・ヘッドレスサーバー専用モードはREADME上存在しない
  (リモートアクセスはLocal API〈OpenAI互換、ポート8129〉かRemoteタブ〈LAN、ポート11435〉経由)。
