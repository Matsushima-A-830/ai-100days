# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 026
- 選んだ候補(backlog.mdのタイトルかURL): NVIDIA/OpenShell — https://github.com/NVIDIA/OpenShell
- 補足メモ(あれば):
  - 人間(matsu)から直接指定された候補(research: 2026-10-23分のネタ候補PR〈#88、backlog.md追記〉内の候補の1つ)。
  - 出典: https://github.com/NVIDIA/OpenShell (本日〈2026-10-23〉GitHub Trending全言語で+1,240star/日・累計約18.7k star。同日のHacker Newsフロントページにも掲載。初出は2026年9月28日発表の「NVIDIA Open Agent Safety Platform」の一部で、今回のトレンド自体は新規リリースというより再拡散と見られる)
  - 概要: 自律AIエージェントをDockerコンテナ単位のサンドボックスで隔離実行するランタイム(Apache-2.0)。宣言的なYAMLポリシーで、ファイルアクセス(Landlock LSM)・システムコール(seccomp)・ネットワーク接続・推論呼び出しをエージェントプロセスの外側からカーネルレベルで強制し、エージェントは実際の認証情報を直接見ることなく承認済みエンドポイント宛の通信にのみ認証情報が付与される。リスクの高いポリシー変更は人間のレビューに回される。Claude Code/Codex/OpenCode/GitHub Copilot等複数のコーディングエージェントに対応。
  - 検証範囲: `curl -LsSf https://raw.githubusercontent.com/NVIDIA/OpenShell/main/install.sh | sh` でCLIを導入し、`openshell sandbox create` でサンドボックスを作成。YAMLポリシーでファイル/ネットワークアクセスを制限した状態と制限なしの状態で、同じエージェント操作(例: 許可外のファイル読み取りや外部ホストへの通信)を試し、実際にブロック/許可が切り替わる様子をBefore/Afterで記録する。モデルバックエンドはOpenRouterの無料枠モデルを使うチュートリアルに従う想定。
  - 追加の有料APIキーは不要(OpenRouter無料枠モデルで検証可能)。GPU不要。Docker/Podmanまたはホスト仮想化が前提のため、**実装Routineの実行環境でDockerが使えるか最初に確認すること**。使えない場合はCLAUDE.mdの方針に従い、推測で埋めず「ローカル検証が必要」と明記してPR冒頭でエスカレーションする(Routine環境固有の制約は記事・X投稿案・noteには書かない)。
  - 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(2026-10-23時点、backlog.md参照。ビジネス系ニュース記事〈Business Insider Japan等〉による発表紹介はあるが、技術者による一次検証記事は未検出)。
  - 記事化の切り口: 「エージェントに認証情報を直接見せずに、承認済み先への通信にだけ後から認証情報を付与する」というカーネルレベルの隔離の仕組みを、実際にポリシーを設定してアクセス許可/拒否が切り替わる様子で示すBefore/After実証。NVIDIA公式発のエージェント安全実行環境という切り口を明記する。

状態: 設定済み
