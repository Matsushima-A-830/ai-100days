# ネタ候補バックログ

リサーチRoutineが毎朝追記する。人間はここから選んで `today.md` に書く。
採用したら「状態」を `採用済み(day-NNN)` に、見送ったら `見送り` に変更する。

## テンプレート(Routineはこの形式で追記すること)

```
### [YYYY-MM-DD] タイトル

- 出典: URL
- 概要: 1-2文
- 日本語記事件数: Zenn n件 / Qiita n件 / note n件
- 検証難易度: 低/中/高(APIキー・GPU要否も書く)
- 見栄え: デモ映えするか一言
- 状態: 未選択
```

---

(ここに候補が積まれていきます)

### [2026-09-28] Shorthand for Thought — エントロピー誘導supertokenでLLMの思考トークンを平均8.1%圧縮(COLM 2026採択)

- 出典: https://arxiv.org/abs/2604.26355 (コード: https://github.com/Writer/shorthand-for-thought)
- 概要: 推論トレース中の低エントロピーな「構造トークン」をBPEでsupertoken化し、SFTでモデルに採用させることで、精度を落とさず思考の長さを平均8.1%短縮する手法。3モデルファミリー×5つの数学ベンチマークで検証済みでモデル非依存。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(類似テーマの記事はあるが本論文自体の紹介は未検出)
- 検証難易度: 中(コード公開・手法はモデル非依存。フルSFTには小型モデル+GPUが必要だが、既存の推論トレースへの後処理・トークン数比較のみなら手元のAPIキーやローカル小型モデルでも概念実証は可能)
- 見栄え: 「推論トークンを削ってコストを下げつつ精度維持」という定量的なBefore/Afterのグラフが作りやすい。
- 状態: 検証済み(day-001, PR作成)。公式データセット/トークナイザーはhuggingface.coブロックのため未使用。自作コーパス+自前BPEトークナイザーで公式アルゴリズム(n-gram集計→BPEマージ→supertoken適用)を実行し、held-outで10.75%のトークン削減を確認。詳細はexperiments/day-001/。

### [2026-09-28] VoiceStudio — ローカル完結のElevenLabs代替OSS(音声クローン/読み上げ/字幕)

- 出典: https://github.com/debpalash/VoiceStudio (GitHub Trending 2026-09-28)
- 概要: 完全ローカルで音声クローン・音声デザイン・動画吹替・書き起こしを646言語でこなすOSSデスクトップアプリ。AGPL-3.0ライセンス。3〜15秒の参照音声からクローン可能とされる。
- 日本語記事件数: Zenn ほぼなし(本リポジトリ名では未検出) / Qiita ほぼなし(類似OSSの記事はあるが本リポジトリ名では未検出) / note 1件(類似名の紹介記事)
- 検証難易度: 中(GPU推奨だがCPUでも小規模なら動作可能との報告あり、APIキー不要)
- 見栄え: 自分の声を日本語でクローンして読み上げさせる比較デモは映える。注意: 同一READMEを持つfork/コピーリポジトリ(shuv1337/VoiceStudio, dabelstech-creator/voicestudio等)が多数存在するため、検証はオリジナル(debpalash/VoiceStudio)で行い、ライセンス実体を確認すること。
- 状態: 未選択

### [2026-09-28] Quail — AI-SQL向け「クエリプランナー×推論エンジン」でLLM推論を高速化

- 出典: https://github.com/fsdatalab/quail (CMU Full Stack Data Lab + Modal共同OSS, Modal Blog: https://modal.com/blog/quail-billion-tpm)
- 概要: LLMをSQLのfilter/joinに埋め込む「AI-SQL」ワークロード向けに、クエリプランナーとKVキャッシュ再利用型の推論エンジンを組み合わせ、vLLM比で高速化を狙うOSS(MITライセンス)。Modal社ブログでは「H100 1基あたり10億トークン/分」を主張。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した限り日本語紹介記事は未検出)
- 検証難易度: 中〜高(公式にはCUDA GPU必須。フル再現にはH100等のレンタルGPUが必要だが、小規模モデルでのミニベンチマーク再現なら6時間以内も狙える範囲)
- 見栄え: 「AI-SQLクエリでLLM推論を高速化」という切り口は技術者向けにインパクトがあり、ベンチマーク結果を数字とグラフで見せやすい。
- 状態: 未選択

### [2026-09-27] Stanford×Caltech「HomeBody」— VLMを直結したヒューマノイドが未知のキッチンを自律的に片付け

- 出典: https://tml.stanford.edu/homebody/ (解説: https://the-decoder.com/researchers-plug-gpt-6-astra-directly-into-a-robot-and-let-it-clean-up-an-unfamiliar-kitchen/)
- 概要: 学習済み制御ポリシーを介さず、フロンティアVLMが直接モーションスキルライブラリ(歩行・引き出しを開ける等)を呼び出し、探索で構築した3D空間記憶を使って初見のキッチンを片付けるヒューマノイド(Unitree G1)システム。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(発表から日が浅く未検出)
- 検証難易度: 高(Unitree G1実機やIsaac Sim/Omniverse環境が前提。個人が6時間以内に手元で再現するのは非現実的)
- 見栄え: 映像的インパクトは非常に高いが、そのまま「動かしてみた」記事にはできない。扱うなら「ニュース解説+関連するVLMタスク分解プロンプトだけを手元で疑似実験」という限定スコープに絞る必要あり。
- 状態: 未選択

### [2026-09-28] Hindsight — 「学習するエージェントメモリ」がGitHubトレンド急上昇

- 出典: https://github.com/vectorize-io/hindsight (論文: https://arxiv.org/pdf/2512.12818)
- 概要: 会話ログをWorld/Experience/Opinion/Observationの4種に分類し、ベクトル類似度・BM25・グラフ探索・時間フィルタを組み合わせて長期記憶を検索するセルフホスト型エージェントメモリ基盤(MITライセンス)。LongMemEvalでSOTAを主張。Dockerで起動可能。
- 日本語記事件数: Zenn 数件〜10件超(既にローカル運用・高速化の実践記事が複数公開) / Qiita 数件 / note 未確認
- 検証難易度: 低〜中(Docker一発で起動、LLM APIキー(OpenAI/Anthropic等)が必要)
- 見栄え: エージェントに「覚えさせる」デモは分かりやすいが、既に日本語の実践記事がかなり出回っており差別化が必要。
- 状態: 未選択

### [2026-09-28] HexStrike AI — Claude Codeに150以上のセキュリティツールを自律実行させるMCPサーバー

- 出典: https://github.com/0x4m4/hexstrike-ai (GitHub Trending 2026-09-28)
- 概要: Nmap/Gobuster/Nuclei/SQLMapなど150以上のペネトレーションテストツールをMCP経由でClaude Code/Claude Desktop等のAIエージェントから自律的に呼び出せるようにするOSS(MITライセンス)。脆弱性診断やバグバウンティ自動化を想定した攻防両用ツール。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出)
- 検証難易度: 低〜中(外部LLM APIキー不要。Claude Code自身がMCPクライアントとして直結できるため追加の有料キーなしで検証可能。GPUも不要。ただし検証は必ず自分が管理するローカルの意図的脆弱環境(例: DVWA等のDockerコンテナ)のみを対象にし、第三者システムには絶対に向けないこと)
- 見栄え: 「AIエージェントに自律的にペネトレーションテストをやらせてみた」は技術者向けに非常にインパクトがある。記事化時は防御的・教育目的であることと検証環境の限定を明記する必要あり。
- 状態: 未選択

### [2026-09-28] Paperclip — AIエージェントを「社員」として組織運用するOSSオーケストレーション基盤が急伸

- 出典: https://github.com/paperclipai/paperclip (GitHub Trending 2026-09-28、本日+3,185star)
- 概要: Claude Code/Codex/OpenClaw等の複数AIエージェントを組織図・予算・ガバナンス付きで「チームメンバー」として管理し、"zero-human company"的な業務自動化を狙うOSS(MITライセンス)。Node.js+React製、Tailscale連携でスマホからの管理にも対応。
- 日本語記事件数: Zenn 数件(関連文脈での言及あり) / Qiita 1件以上(2026-09-26付GitHub日報系記事で紹介済み) / note 1件確認
- 検証難易度: 中〜高(Node.js/pnpm/PostgreSQLのセットアップ自体はローカルで完結するが、実際にエージェントを稼働させるにはANTHROPIC_API_KEYまたはOPENAI_API_KEYが必要な可能性が高い。既存のClaude Code連携(サブスクリプション認証)だけで有料キーなしに動くかは要検証)
- 見栄え: 「AIエージェントを社員のように管理するダッシュボード」の画面は見せやすいが、日本語記事が既に出始めているため切り口の差別化が必要。
- 状態: 未選択

### [2026-09-28] Microsoft SkillOpt — モデルの重みではなく「skill.md」を訓練対象にする自己進化型エージェントスキル最適化

- 出典: https://github.com/microsoft/SkillOpt (論文: arXiv:2605.23904)
- 概要: LLM本体の重みを凍結したまま、自然言語のスキル文書(best_skill.md、300〜2000トークン)を試行錯誤ログとホールドアウト検証に基づいて反復編集し性能を上げるMicrosoft Research発のOSS(MITライセンス)。GPT-5.5で+23.5ptの精度向上を主張。2026年6月にはオフライン自己進化機能「SkillOpt-Sleep」も追加。
- 日本語記事件数: Zenn 2件以上 / Qiita 3件以上(SkillOpt-Sleepや評価ツール比較など既に複数の実践記事が公開済み) / note 未確認
- 検証難易度: 中(pip installのみで導入できるが、最適化ループの実行にOpenAI/Azure/Claude/Qwen等のLLMバックエンドAPIキーが必要。無料枠や既存のClaude Code環境だけで完結できるかは要確認)
- 見栄え: skill.mdのBefore/Afterと精度差を並べて見せられるので技術者向けに刺さりやすいが、日本語記事が既に複数あるため差別化が課題(優先度は下げつつ候補として残す)。
- 状態: 未選択

### [2026-09-28] TensorFold — Apple Silicon/NVIDIA向けのOpenAI互換ローカルLLM推論エンジン

- 出典: https://github.com/ashhart/TensorFold (GitHub Trending 2026-09-28、本日+160star)
- 概要: Apple Silicon(MLX)またはNVIDIA GPU上でOpenAI互換エンドポイントを立て、プロンプトキャッシュや投機的デコーディングにより高速・正確なLLM推論を行うOSS(MITライセンス)。Qwen3.8-27BやGLM-5.3-Flash等をローカルでサーブ可能。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語記事未検出)
- 検証難易度: 中〜高(APIキーは不要だが、Apple Silicon Mac(十分なメモリ)かNVIDIA GPUが前提。クラウド実行環境では要件を満たさない可能性が高く、手元にMac/GPUがあるかがボトルネック)。注意: 同一READMEを持つ大量のフォーク/コピーリポジトリ(jasontitus, taussoe, quigles1977, CerebralCoding, vcruz305, machinegenieorg等)がGitHub上に多数存在するため、検証前に公式実体(ashhart/TensorFold、公式サイトtensorfold.dev)を確認すること。
- 見栄え: 「手元のMacでLLMをどれだけ高速に動かせるか」のBefore/After速度比較は分かりやすいが、対応ハードウェアがないと着手できない点に注意。
- 状態: 未選択

### [2026-09-29] OpenRig — Claude CodeとCodexを1つのチームとして動かすマルチエージェント・ハーネス(Show HN話題)

- 出典: https://github.com/mvschwarz/openrig (Show HN: https://news.ycombinator.com/item?id=47772935)
- 概要: Claude CodeとCodexをtmuxベースの「リグ」に同居させ、YAMLで定義したチーム(pod/seat)としてエージェント同士に直接メッセージを送り合わせる、Apache-2.0のマルチエージェント・オーケストレーションCLI/デーモン/MCPサーバー。GitHub Trending(TypeScript)で本日+733starと急伸中。
- 日本語記事件数: Zenn 0件 / Qiita 0件(Claude Code×Codex連携自体の記事は複数あるが、OpenRig自体の紹介は未検出) / note 0件
- 検証難易度: 低(追加のAPIキー不要。既存のClaude Code/Codexサブスクリプション認証をそのまま再利用する設計と説明されている。Node.js 22/24とtmuxが必要、GPU不要)
- 見栄え: 「Claude CodeとCodexが会話しながら共同作業する」様子をターミナルUIで見せられ、本リポジトリのRoutine運用(朝リサーチ→昼実装の分業)との類似性も語れるので技術者に刺さりやすい。
- 状態: 未選択

### [2026-09-29] Octop — セルフホスト型マルチユーザー・マルチエージェントAIアシスタント(Ollamaでキー不要運用可)

- 出典: https://github.com/TencentCloud/Octop
- 概要: Web/CLI/IM(Discord・Telegram・Slack系含む)から使えるセルフホスト型のマルチユーザー・マルチエージェントAIアシスタント(MITライセンス)。16種のMBTIペルソナテンプレートや複数エージェントを協調させるAgentTeams機能が特徴。GitHub Trending(Python)で本日+234star。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲で本リポジトリ名での紹介記事は未検出)
- 検証難易度: 低〜中(LLMプロバイダとしてOllamaのローカルモデルを設定でき、外部APIキーなしで動作可能。Python 3.12+、GPUは任意)
- 見栄え: 複数のペルソナを持つエージェントがWebダッシュボードやIM経由で応答し分業する様子はデモ映えする。
- 状態: 未選択

### [2026-09-29] Ouroboros — 「曖昧な要求をインタビューで明確化してから実装する」自己改善型Agent OS

- 出典: https://github.com/Q00/ouroboros
- 概要: 曖昧な要求をSocratic Interviewで明確化し、評価ゲート(曖昧さスコア閾値)を通過してから実装、さらに多段評価と進化ループで改善し続けるAgent OS(MITライセンス)。Claude Code CLI/Codex CLI/Gemini CLIなど14種のランタイムに対応。GitHub Trendingで6,000star超。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件
- 検証難易度: 中(Python 3.12+、Git、uvで導入可能でGPU不要。LiteLLM経由の外部LLM API利用が基本だが、ランタイムとしてClaude Code CLIを選べば追加の有料APIキーなしで検証できる可能性がある。要事前確認)
- 見栄え: 「要件があいまいなまま突っ走らず、質問で明確化してから実装する」プロセスを実演できれば説得力のあるBefore/Afterデモになる。
- 状態: 未選択

### [2026-09-29] Google、GeminiでgiflibをAI支援でRustに書き換え差分ファジングで検証(企業ブログ)

- 出典: https://bughunters.google.com/blog/scaling-memory-safety (解説記事: https://www.infoq.com/news/2026/09/c-rust-rewrite/)
- 概要: GoogleがGeminiを使い、giflib(約3,000行のC製GIF画像処理ライブラリ)をABI互換のRust実装にAI支援で書き換え、差分ファジングで検証した事例。移行後、公開前だったヒープ書き込みゼロデイ(CVE-2026-26740)の影響を受けなかったと報告している。
- 日本語記事件数: Zenn 0件(「C++→Rust移行」など関連テーマの記事はあるが本件そのものの紹介は未検出) / Qiita 0件 / note 0件
- 検証難易度: 低(GPU・外部APIキー不要。Claude Code自身の機能だけで、小規模なCコード片をAI支援でRustに書き換え→テストで差分検証する縮小版のミニ実験が可能)
- 見栄え: Before(C)/After(Rust)のコードと検証結果を並べて見せやすく、「AIエージェントによるレガシーコードのメモリ安全化」という切り口はセキュリティ文脈でも刺さる。
- 状態: 検証済み(day-002, PR作成)。giflib本体ではなく、同種のバグ(サイズチェック漏れによるヒープ書き込み)を再現した独自ミニRLEデコーダで、C版(意図的にバグを残す)とRust版(Claude Codeで安全に書き換え)を実装し、正常系1000件の差分ファジングで完全一致・異常系でC版のASan検出とRust版の安全なエラー返却を確認。詳細はexperiments/day-002/。

### [2026-09-30] NVIDIA OpenShell — 自律AIエージェント向けサンドボックス型実行ランタイム(Open Agent Safety Platform)

- 出典: https://github.com/NVIDIA/OpenShell (発表: Open Agent Safety Platform, 2026-09-28。GitHub Trending急伸、+990star/日)
- 概要: AIエージェントにファイルアクセス・パッケージインストール・API利用を許しつつ、宣言的YAMLポリシーでファイルシステム/ネットワーク/プロセス/推論の4領域をdeny-by-default制御するサンドボックス型ランタイム(Apache-2.0)。Docker/Podman/MicroVM/Kubernetes上で動作し、NVIDIA BlueField-4上で動くハードウェア監視「Sentry」と組み合わせた「Open Agent Safety Platform」の中核として発表された。
- 日本語記事件数: Zenn 2件以上 / Qiita 1件以上(「NVIDIA OpenShell入門」記事あり) / note 未確認(発表直後から解説記事が複数出ており既に話題)
- 検証難易度: 低〜中(Apache-2.0。Docker/Podmanで起動可能、クイックスタートは無料のOpenRouterモデルを使う例があり必須の有料APIキーはなし。「エージェントに危険な操作をさせてポリシーでブロックされる」デモなら6時間以内に再現できそう)
- 見栄え: 「ポリシー無し/ありでエージェントの危険操作がブロックされるか」のBefore/Afterは分かりやすいが、日本語記事が既に複数出ているため切り口の差別化が必要。
- 状態: 未選択

### [2026-09-30] TokenCast — LLMエージェント実行中のトークン消費量を逐次予測する手法(論文)

- 出典: https://arxiv.org/abs/2609.35760 (コード: https://github.com/DEFENSE-SEU/TokenCast)
- 概要: LLMエージェントの累積コンテキストが後続呼び出しのコストを押し上げる構造を、実行セグメント単位のコスト表現として学習し合成することで、タスク完了までのトークン消費量を事前予測・実行中に逐次更新する手法。4タスクスイート×6エージェントモデル・96通りの評価で既存手法比MAEを平均14.5%改善し、予算制御リプレイでは同じ完了率のまま平均21.3%のトークン削減を報告。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(bot集計記事以外の日本語紹介記事は未検出)
- 検証難易度: 高(公式コードのREADMEに「近日公開予定、現在整理中」とあり本日時点では未公開でフル再現は不可。手法のアイデア(セグメント単位のコスト分解+累積予測)のみを参考に、自分のエージェント実行ログに対する簡易予測モデルを自作して概念実証する、という限定スコープなら6時間以内も可能)
- 見栄え: トークン消費の実測値と予測値をグラフで比較でき、コスト最適化の文脈で刺さりやすい。ただし公式コード非公開という制約を記事内で明記する必要がある。
- 状態: 未選択

### [2026-09-30] Univer — AIエージェント向け「オフィスハーネス」を謳うOSS Office SDK(スプレッドシート/ドキュメント/スライド)

- 出典: https://github.com/dream-num/univer (GitHub Trending 2026-09-30、+696star/日)
- 概要: スプレッドシート・ドキュメント・スライド・PDF等を1つのランタイムで扱えるOSS Office SDK(Apache-2.0)。AIエージェントがFacade API経由でワークブックを生成・編集でき、Worktree機能で人間レビュー前の下書きを分離できる「AIエージェント向けオフィスハーネス」を標榜。
- 日本語記事件数: Zenn 0件(Univer自体を扱う記事は未検出) / Qiita 1件(「Univer入門」記事あり) / note 未確認
- 検証難易度: 低(Apache-2.0。Node.js 18.17+のみでAPIキー・GPU不要。headlessモードでローカル完結のデモが作れる)
- 見栄え: 「AIエージェントに指示してスプレッドシートのダッシュボードを自動生成させる」Before/Afterは見せやすく、外部キー不要で完結する点が本チャレンジの運用方針とも相性が良い。
- 状態: 採用済み(day-003)

### [2026-09-30] OpenAI dots — GPT-6 Astra搭載の常時稼働AIエージェント(DevDay 2026発表、ニュース扱いのみ)

- 出典: OpenAI DevDay 2026発表 (解説: https://www.itmedia.co.jp/aiplus/article/2609/30/2000001864/ , https://www.macrumors.com/2026/09/29/openai-launches-dots/)
- 概要: GPT-6 Astraを搭載し、専用クラウドマシン・ブラウザ・記憶を持って、ChatGPTを閉じていてもタスクを継続して進める「常時稼働」型AIエージェント。ChatGPT/SMS/Slack/Teams経由でメッセージを送って作業を進められる。
- 日本語記事件数: Zenn 2件以上 / Qiita 未確認 / note 3件以上(DevDay直後から多数の解説記事が出ており日本語での一次紹介は既に飽和状態)
- 検証難易度: 高(ChatGPT Pro/Business Premium/Enterpriseプラン限定のクローズドな有料機能で、コード・APIは公開されていない。本リポジトリの方針「当面は有料APIキー/有料プラン必須の候補を選ばない」に抵触するため、今回は選定不可)
- 見栄え: ニュース価値は高いが「動かして検証する」ネタにはできない。取り上げる場合はニュース解説のみの扱いに留める必要あり。
- 状態: 未選択

### [2026-10-01] context-mode — Claude Code等17プラットフォーム向けのコンテキストウィンドウ最適化MCPプラグイン

- 出典: https://github.com/mksglu/context-mode (GitHub Trending TypeScript, 2026-10-01、+357star/日)
- 概要: Claude Code/Codex/Cursor/Gemini CLI等17プラットフォームにMCP+hooksで差し込み、ツール出力をサンドボックス化して98%圧縮しつつ、SQLite+FTS5でセッション記憶(ファイル編集・git操作・タスク・エラー・判断)を永続化し、compact後も必要な情報だけをBM25検索で取り戻すプラグイン。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出)
- 検証難易度: 低(ライセンスはElastic License v2 = ソースは公開されているがマネージドサービスとしての再提供は制限される、いわゆる非OSIライセンス。Node.js 22.5+/Bunのみで`claude mcp add`一発導入、外部APIキー・GPU不要。本リポジトリのRoutine自体に組み込んで「圧縮前後のコンテキスト消費量」を実測できる)
- 見栄え: 生のツール出力をそのまま食わせた場合と、context-mode経由で圧縮した場合の「コンテキスト消費量」「会話が長持ちする時間」をBefore/Afterのグラフで見せやすく、本チャレンジ自身の運用改善ネタとしても語れる。
- 状態: 未選択

### [2026-10-01] Corral — AIエージェントが起動した子プロセスを確実に全停止させる軽量セーフティユーティリティ

- 出典: https://github.com/Cardinal44/corral (Show HN: https://news.ycombinator.com/item?id=49886422)
- 概要: コマンドをプロセスグループごと(cgroup v2)管理し、`tail -f`やデーモン化・二重フォークした子プロセスを含めて、コマンド終了時に起動した全プロセスが確実に死んでいることを保証するAIエージェント向けセーフティツール(MITライセンス)。「AIエージェントが放置したバックグラウンドプロセスが残り続ける」問題への対処を謳う。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出)
- 検証難易度: 低〜中(MIT。Linux 5.11以降・x86-64/glibc 2.36+が前提でCMake/Ninja/GCCからビルド。APIキー・GPU不要。クラウド実行環境がLinuxであれば6時間以内に検証可能)
- 見栄え: 「エージェントに`tail -f`やデーモンを起動させ、Corralあり/なしでプロセスが残り続けるか」をps確認付きのBefore/Afterで見せられ、HexStrike AI等で既に触れたエージェント安全性というテーマの続編として語りやすい。
- 状態: 未選択

### [2026-10-01] Jeff — Qwen3.5/Gemma4をファインチューンした22msの軽量ゼロショット分類モデル

- 出典: https://github.com/firelex/jeff (Release v1.1/v1.2, 2026-09-29。GitHub Trending Pythonで+1,213star/日)
- 概要: Qwen3.5(0.8B/2B)とGemma4-E2Bをファインチューンし、ユーザーが定義した最大254個の選択肢に対し1回のフォワードパスで較正済み確率を返す「ミリ秒で意思決定する」ゼロショット分類モデル群。RTX PRO 6000で22〜29ms、Apple Silicon(MLX)で28〜60msと主張(コードMIT、重みApache-2.0)。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(GIGAZINE等の海外ニュース翻訳記事はあるが、日本語での一次検証記事は未検出)
- 検証難易度: 低(uvで導入可能。0.8Bモデルは1.7GBでCPU推論も可能(GPUなしでも動作確認でき、速度は劣るが検証は可能)。外部APIキー不要)
- 見栄え: 自作の簡単な分類タスク(例: 問い合わせ文の振り分け)で、キーワードルールベースの分類とJeffのゼロショット分類を精度・速度の両面でBefore/After比較でき、数値グラフが作りやすい。
- 状態: 未選択

### [2026-10-01] MicroLLM Lab — WebGPUでブラウザ内完結、7種の小型LLMを体験できる実験ラボ

- 出典: https://github.com/robss2020/microllm-lab (Show HN: https://news.ycombinator.com/item?id=49882781、デモ: https://stateofutopia.com/experiments/microllmlab/)
- 概要: PetitGPT(124.6M)・SmolLM系・MiniMind2・GPT-2など25M〜360Mパラメータの7種の小型LLMをQ4量子化してWebGPU経由でブラウザ内に直接ロードし、サーバーもPython/CUDA環境も使わずにチャット・ベンチマークできる実験ラボ(ラボ本体はApache-2.0、各重みは由来元のライセンスに従う。GPT-2のみMIT)。重みはIndexedDBにキャッシュされる。
- 日本語記事件数: Zenn 0件 / Qiita 1件(海外テック動向まとめ記事内で他2トピックと合わせて紹介済み) / note 0件(単体の検証記事はまだ無い)
- 検証難易度: 低(APIキー・サーバー・CUDA不要。WebGPU対応ブラウザ(Chrome/Edge/Safari)さえあれば動作するため、クラウド実行環境でもブラウザのスクリーンショット確認を含め6時間以内に検証可能)
- 見栄え: 7種の小型モデルの応答速度(トークン/秒)・出力品質をブラウザ上で横並び比較でき、Before/After表やグラフにまとめやすい。日本語記事がまだ単体では無く差別化しやすい。
- 状態: 未選択

### [2026-10-02] "Do LLM Agents Execute the Plans They Declare?" — 宣言した計画モードと実際の実行の乖離を検証する論文(Planning-as-Routing)

- 出典: https://arxiv.org/abs/2609.38108 (2026-09-29投稿)
- 概要: LLMエージェントが4種の計画モード(Predefined/Sequential/Hierarchical/Search)のいずれかを自己宣言しても、汎用的なPlan+ReActでは特に長い計画ほど宣言した構造を実行時に守れず(3ベンチマークで構造保持率22〜45%)、モード別の専用executorに振り分ける「Planning-as-Routing」の方が構造を守り成功率も上がる(ALFWorldで0.48→0.92、SWE-bench Verifiedで0.36→0.44)と報告する論文。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(GitHub上の自動翻訳botによる要約issueが1件あるのみで、一次的な日本語解説記事は未検出)
- 検証難易度: 低(論文自体の公式コード公開は未確認。追加の有料APIキーやGPUは不要で、Claude Code自身に簡単なマルチステップタスクをやらせ「どの計画モードを使うか」を事前宣言させた上で、実際の実行ログ(ツール呼び出し順序)が宣言と一致するかを自作スクリプトで突き合わせる、という縮小版の概念実証なら6時間以内で可能)
- 見栄え: 「宣言した計画」と「実際の実行ログ」を並べて一致/不一致を可視化するBefore/After表が作りやすく、エージェントの信頼性という切り口で技術者に刺さりやすい。日本語記事が無く差別化しやすい。
- 状態: 未選択

### [2026-10-02] NVIDIA SkillSpector — AIエージェントのSkillを導入前に静的スキャンするセキュリティツール

- 出典: https://github.com/NVIDIA/SkillSpector
- 概要: Claude Code/Codex/MCP向けのAgent Skillsをインストール前にスキャンし、隠し指示・プロンプトインジェクション・サプライチェーンリスクなど71パターン×17カテゴリの脆弱性を検出するOSS(Apache-2.0)。リスクスコア(0-100)と「SAFE/DO NOT INSTALL」等の判定を返す。GitHub Trendingで本日+167star。
- 日本語記事件数: Zenn 2件以上 / Qiita 1件以上 / note 数件(2026年5月の発表直後から解説記事が複数公開されており、ある程度認知は進んでいる)
- 検証難易度: 低(Apache-2.0。`--no-llm`フラグで静的解析のみに限定すればAPIキー不要、GPUも不要。Python 3.12+で導入可能)
- 見栄え: 意図的に危険な指示(プロンプトインジェクション等)を仕込んだ自作のダミーSkillファイルを用意し、SkillSpectorでスキャンしてリスクスコアや検出項目を見せるBefore/Afterデモが作りやすい。既に扱ったHexStrike AI・OpenShellと同じ「AIエージェント安全性」系の関連作として語れるが、日本語記事が複数あるため切り口の差別化が必要。
- 状態: 未選択

### [2026-10-02] Soup — 単一YAMLでLLMファインチューニングを完結させるCLI(Layer Streamingで4GB GPUでも8Bモデル学習)

- 出典: https://github.com/MakazhanAlpamys/Soup
- 概要: YAML1ファイルの設定だけでSFT/DPO/GRPO等のLLMファインチューニングを実行できるCLI(Apache-2.0)。「Layer Streaming」により凍結したベースモデルの各デコーダ層をVRAMに置かずGPUへ1層ずつ流し込むことで、Llama-3.1-8B-InstructのNF4量子化ファインチューニングをRTX 3050 Laptop(4GB)で119.6 tok/sで実行できたと主張。無料のColabノートブックでも動作実証済み。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 1件(他ツールと並べた短い言及のみで単体の検証記事は未検出)
- 検証難易度: 中〜高(APIキーは不要だが、見出し機能の検証にはCUDA GPU(できれば実機)が前提。クラウド実行環境にGPUが無い場合はColabノートブックでの代替実行が必要で、当日中に完結できるかは環境依存)
- 見栄え: 「GPUメモリ使用量」と「学習速度(tok/s)」のBefore/After(通常のファインチューニング vs Layer Streaming)を数値とグラフで見せやすい。日本語記事がほぼ無く差別化しやすい。
- 状態: 未選択

### [2026-10-02] caveman — コーディングエージェントを「原始人口調」にしてトークンを60〜75%削減するスキル+プロキシ

- 出典: https://github.com/JuliusBrussee/caveman (公式ドキュメント: https://docs.caveman.so/)
- 概要: エージェントの出力・入力スタイルを「技術的内容は保ったまま簡潔な原始人口調」に変えることで、トークンを平均65%(JetBrainsラボ実測では出力トークン8.5%減、公式プロキシの54実行ベンチマークでは入力トークン33.2%減)削減するスキル+ローカルプロキシ(Apache-2.0/一部MIT)。2026年4月に公開され1週間で4,000star、7月にGitHub Trending 1位に到達、Claude Code/Codex/Cursor等30+エージェントに対応。
- 日本語記事件数: Zenn 9件以上 / Qiita 8件以上 / note 6件以上(「原始人プロンプト」として既に日本語でも非常に多数の実践記事が公開済み、日本語特化の派生プラグイン「genshijin」も存在)
- 検証難易度: 低(`npx skills add JuliusBrussee/caveman -g`等で導入可能。APIキー・GPU不要。本リポジトリ自身のRoutine実行時のトークン消費量をBefore/Afterで比較する自己言及的な検証がしやすい)
- 見栄え: 自分の実行環境(Claude Code)への導入前後でトークン消費量を実測してグラフ化できるが、日本語記事が極めて多く差別化が最大の課題。扱うなら「本チャレンジ自身のRoutine運用コストにどう効くか」という独自切り口に絞る必要あり。
- 状態: 未選択

### [2026-10-03] Chandra OCR 2 — 手書き・複雑な表に強いOSS OCRモデル(Datalab)

- 出典: https://github.com/datalab-to/chandra (モデル: https://huggingface.co/datalab-to/chandra-ocr-2)
- 概要: スキャン文書・手書き・複雑な表組み・数式・90言語以上のレイアウトを保持したままHTML/Markdown/JSONに変換するOCRモデル。2026年3月にChandra 2としてメジャーアップデートし、DeepSeek-OCR等と比較する海外レビューが相次いでいる。コードはApache-2.0だが、モデル本体は改変OpenRAIL-M(研究・個人利用および年間売上/資金調達$2M未満のスタートアップは無料、それ以上の商用利用は別途ライセンス契約が必要)。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(Medium等の英語記事は複数あるが日本語での検証記事は検索した範囲で未検出)
- 検証難易度: 低〜中(`pip install chandra-ocr`で導入可能、APIキー不要。GPUは任意でCPU推論も可能だが低速。手元の手書きメモや複雑な表組みPDFを用意してBefore/After的に既存OCR(Tesseract等)と精度を比較するデモが6時間以内で狙える)
- 見栄え: 手書き・表組みの認識結果を画像と並べて見せられ、精度比較の数値表も作りやすい。ライセンス(改変OpenRAIL-M)の条件を記事内で明記する必要あり。
- 状態: 未選択

### [2026-10-03] Heavy-Tailed Memory Traces in Long-Horizon Language Agents — エージェント記憶のロングテール問題とCore-Tail World Model(論文)

- 出典: https://arxiv.org/abs/2610.00010 (コード: https://github.com/Hik289/world-model-self-organized-criticality)
- 概要: 長期稼働するLLMエージェントが外部メモリを「凍結した世界モデル」として使う際、記憶が少数の「コア」状態に集中し、稀な状態が「テール」に押し込まれて予測誤差が蓄積する現象を定式化。ランク依存の単一指数τでプロンプト予算を配分しつつテールを要約として保持するCore-Tail World Model(CTWM)を提案し、合成グラフ世界でプロンプトトークン5.9%削減・テール予測誤差13.6%改善、LongMemEvalでトークン24.48%削減を報告。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出)
- 検証難易度: 中(コードはMITで公開済み、GPU不要)。ただしLLMポリシーを使う本家の実験は外部LLM API(OpenAI互換エンドポイント)のAPIキーが前提の実装になっている。本リポジトリの方針(有料APIキー不要)に沿うなら、ランダムウォークのスケーリング実験(API不要・CPUのみ)の再現、またはLLM呼び出し部分をClaude Code自身に代替させる縮小版の概念実証に絞る必要がある。
- 見栄え: 「記憶のコア/テール」構造とトークン削減率をBefore/Afterのグラフで見せやすく、エージェントメモリ系の話題(Hindsight等)の発展形として語れる。日本語記事が無く差別化しやすい。
- 状態: 未選択

### [2026-10-03] claude-mem — Claude Codeにセッション横断の永続メモリを追加するプラグイン

- 出典: https://github.com/thedotmack/claude-mem
- 概要: Claude Codeのセッション中の操作をフックで捕捉し、AIで要約・圧縮してSQLite+ベクトル検索(Chroma)に保存、次回以降のセッションにCLAUDE.mdへの差し込み等で関連文脈を復元するメモリプラグイン(Apache-2.0)。GitHub Trending(TypeScript)で本日急伸中。
- 日本語記事件数: Zenn 1件以上(「claude-mem: Claude Codeに永続メモリを追加する」という紹介記事を確認) / Qiita 数件(ツールまとめ記事内での言及あり) / note 未確認
- 検証難易度: 低(`/plugin marketplace add thedotmack/claude-mem`等で導入可能。Node.js 20+とBun/uv(自動導入)のみで、基本機能は外部APIキー不要・GPU不要)
- 見栄え: 本リポジトリ自身のClaude Code Routine運用(朝リサーチ→昼実装)にインストールし、セッションを跨いだ文脈復元が実際に効くかを自己言及的に検証できるのが強み。日本語記事が既に1件以上あるため、「自分たちの運用への適用」という独自切り口が必要。
- 状態: 未選択

### [2026-10-03] Agent-Reach — AIエージェントにSNS/Web横断の「検索・閲覧」能力を与えるCLI(要注意・出典確認必須)

- 出典: https://github.com/vinay121314/Agent-Reach (GitHub Trending Python 2026-10-02、+1,683star/日)
- 概要: Twitter/Reddit/YouTube/GitHub/Bilibili/XiaoHongShu等を「ゼロAPI費用」で横断的に読み書き・検索できるとするAIエージェント向けCLI。Cookie認証で各プラットフォームの公式APIを介さずアクセスする設計だと説明されている。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出)
- 検証難易度: 低(APIキー・GPU不要でCLIのみで動作)。**ただし要注意**: 同一READMEを持つほぼ同名のフォーク/コピーリポジトリが極めて多数(binawoh, Yverr0y, rdriaz, 0xfudman, zhudao, iqjiy, 899ms, silently0801 等)存在し、スター数の急伸パターンもVoiceStudio/TensorFoldで過去に見られた疑わしいフォーム群に類似。さらに「Cookie認証で公式APIを回避して各SNSにアクセスする」という設計自体が各プラットフォームの利用規約に抵触する可能性が高く、検証・紹介するかどうかは慎重な判断が必要。
- 見栄え: 「CLIから複数SNSを横断検索」はデモ映えしそうだが、上記のライセンス/ToS/出所の懸念から今回は見送り、または深く掘らずにニュース解説のみに留めるのが無難。
- 状態: 未選択

### [2026-10-03] OpenDLSS-NR — NVIDIA DLSS 5ニューラルレンダリングのOSS(Vulkan/WebGPU)再実装(要ライセンス確認)

- 出典: https://github.com/spydrful/OpenDLSS-NR-AMD (関連: https://github.com/aloshdenny/open-dlss , https://github.com/bhouston/three-dlss-nr) (解説: https://wccftech.com/nvidia-dlss-5-gets-open-source-vulkan-reimplementation-runs-on-rtx-40-gpus-and-even-in-web-browsers/)
- 概要: NVIDIA DLSS 5のニューラルレンダリングネットワーク(71ブロック構成)を、Vulkanおよびブラウザ上のWebGPU/WGSLで「bit-exact」に再実装したというOSS。RTX 4070で1080p 7.8msを主張し、AMD GPU向けポートやThree.js(WebGPURenderer)向けポートも派生している。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出)
- 検証難易度: 高(クラウド実行環境にGPU・ディスプレイが無い場合、Vulkan/WebGPUでの実レンダリング検証は困難。WebGPU対応ブラウザでの代替実行ができるかは要確認。加えて、NVIDIAの非公開ネットワークを「bit-exact」でリバースエンジニアリングしたと称する点は著作権・知的財産の観点でグレーゾーンの可能性があり、紹介する場合はその経緯・ライセンス表記を慎重に確認する必要がある)
- 見栄え: 映像的な見栄えは良いが、法的・環境的な制約が大きいニュース解説向きの候補。動かして検証するには環境がネックになる可能性が高い。
- 状態: 未選択
