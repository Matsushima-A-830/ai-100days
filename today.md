# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 041
- 選んだ候補(backlog.mdのタイトルかURL): milind-soni/OpenMausBot — https://github.com/milind-soni/OpenMausBot
- 補足メモ(あれば):
  - 出典: https://github.com/milind-soni/OpenMausBot (Apache-2.0。`enterprise/`配下のみ別のsource-availableライセンス。2026-11-07付でGitHub Trending TypeScriptの中で最多の+1,986star/日)。本エントリはbacklog.md側では2026-11-07付研究PR(#138、本記事作成時点で未マージ)に記載されている。backlog.mdへの反映が先にマージされていなくても、本todayエントリの情報だけで検証に着手できるよう以下に詳細を再掲する。
  - 概要: xAIのGrok Botのクローズドソース・xAIモデル縛りを批判し、手元の`claude`/`codex`/`grok` CLI(既存ログイン・サブスクリプションを利用)を各ボットの実行基盤とするOSS版チャットアプリ。サイドバーの各ボットはローカルで動くエージェントCLIを裏側に持ち、シェル実行やファイル編集などの危険な操作は許可/拒否カードで確認を求める。モデルピッカーで会話途中でもボットごとにモデル・CLIを切り替えられ、Composio経由で500以上の外部アプリにも接続できる。
  - 導入方法の選択肢: (1) GitHubリリースのデスクトップアプリ(macOS/Windows/Ubuntu 24.04 x64のElectron GUI)、(2) `npm install -g openmausbot` または `npx openmausbot`(Node 24+、初回は対話式セットアップ後にブラウザでUIが開く。`--no-open`で無効化可)、(3) `npx openmausbot serve` によるサーバー運用、(4) ソースから`pnpm install`+`pnpm dev:server`等。本Routineではまず(3)のサーバー運用または(2)の`--no-open`付きCLI起動でヘッドレスに動かせるか確認する。
  - APIキー・前提条件についての方針: `claude`/`codex`/`grok`のいずれか1つ以上がインストール・ログイン済みであることが前提(本Routine環境には既にClaude Code CLIが入っているため、これをエンジンとして使えるか確認する)。Composio・Boat・ElevenLabs・Fish Audioの外部連携キーはすべて任意で、無くてもローカルチャットは動く設計。CLAUDE.mdの「有料APIキー必須の候補は選ばない」方針には抵触しない見込みだが、ログイン済みCLIの検出がうまくいかない場合でも、新たに有料APIキーを取得・設定することはしない。
  - 検証スコープ・手順:
    1. まず本Routine実行環境でNode 24+/pnpm/npxが使えるか、また`claude` CLI(このRoutine自身が使っているもの)がOpenMausBotから認識されるかを確認する。
    2. `npx openmausbot serve`(または`npx openmausbot --no-open`)でヘッドレスに起動できるか試す。デスクトップアプリ(Electron GUI)の起動はこのRoutine実行環境では前提から外し、試さない。
    3. 起動できた場合、ボットを1つ作成し、`claude` CLIをエンジンに指定した簡単な対話(例: ファイル作成やシェル実行を伴うタスク)を実行し、許可/拒否カードの挙動を含めて動作確認する。
    4. もし(a)GUI/ブラウザUIが必須でヘッドレスに操作できない、または(b)エージェントCLIのログイン検出がこのRoutine実行環境固有の制約(ブラウザ不在・認証フロー不一致等)で失敗する場合は、CLAUDE.mdの「書かない(Routine環境の制約)」に該当するため記事等には書かず、PRの説明文冒頭に「ローカル検証が必要」と明記し、再現手順(上記npx/pnpmコマンド)を添えてローカル検証にエスカレーションする。results.mdには「Routine環境の制約により未検証、ローカル検証待ち」と1〜2行だけ残す。
    5. 実行コマンド・出力・エラー・所要時間はすべてそのままresults.mdに記録する。失敗した場合も、それがツール自体に起因する失敗なのかRoutine環境固有の制約なのかを区別した上で正直に書く。
  - 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(2026-11-07時点、backlog.md参照。中国語解説記事〈aitoolly.com〉は複数日分あるが日本語の一次検証記事は検索した範囲では未検出)。
  - 記事化の切り口: 「このRoutine自身が使っているClaude Code CLIを、別のOSSチャットアプリ(Grok Botの代替)のバックエンドとして動かす」という自己言及的な検証。Grok Bot的な閉じたUI/モデル縛りと、手元のCLIエージェントを自由に組み込める構成とのBefore/After的な対比を作る。ヘッドレス実行で詰まった部分は記事には書かず、ローカル検証の結果が出てから反映する。

状態: 設定済み
