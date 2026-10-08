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

### [2026-10-04] Janus — 単一Goバイナリで.ggufモデルをVulkan/CPUで動かすOpenAI互換ローカル推論サーバー

- 出典: https://github.com/Vibra-Ingenn/Janus (Show HN)
- 概要: Python/Docker/Ollama不要、単一のGoバイナリだけでAMD/Intel/NVIDIA GPUのVulkanまたはCPUフォールバックで.ggufモデルをロードし、/v1/chat/completions等のOpenAI互換APIを提供するローカルLLM推論サーバー。モデル無停止でのホットスワップやGGUFメタデータからのチャットテンプレート自動検出にも対応。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(llama.cpp/GGUF全般の解説記事は多数あるが、本リポジトリ(Janus)自体を紹介する日本語記事は未検出)
- 検証難易度: 低(MITライセンス。Go 1.22+のみで導入可能、APIキー不要。Vulkan対応GPUが無くてもCPUフォールバックで動作するため、クラウド実行環境でも6時間以内に検証可能)
- 見栄え: 「Python/Docker無しで1バイナリだけでOpenAI互換ローカルLLMサーバーが立つ」という手軽さを、起動コマンドと応答のBefore/Afterで見せやすい。
- 状態: 未選択

### [2026-10-04] K-Dense BYOK — ハッシュチェーンで改竄不可能な実験ノートを残すローカル完結AI co-scientist

- 出典: https://github.com/K-Dense-AI/k-dense-byok (論文: https://arxiv.org/abs/2610.00074)
- 概要: 研究者が自分のPC上で動かすOSSのAI co-scientist。科学的手順のスキルライブラリ・ワークフロー雛形・レビュワー/ライター役を備え、エージェントの行動を監視して書き込むLiving Lab Notebook(エージェント自身は書き換え不可)を記録することで「本当に実行したことの証跡」を残すのが特徴。BYOK(Bring Your Own Key)方式でOllama等のローカルモデルも使用可能。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では本リポジトリ自体を紹介する日本語記事は未検出)
- 検証難易度: 低〜中(MITライセンス。Node.js+Gitでクローンして起動まで数分。LLMバックエンドにOllama等のローカル/無料モデルを選べば追加の有料APIキーなしで検証可能。簡単な調査タスクを1件流し、Living Lab Notebookに何が記録されるかを確認するデモなら6時間以内で可能)
- 見栄え: 「エージェントが"やった"と主張する内容と、改竄不可能なログに実際に記録された内容」を並べて見せるBefore/After的な検証がしやすく、本リポジトリの絶対ルール「動かしていないものを動いたと書かない」と直接共鳴するテーマ。
- 状態: 採用済み(day-007)

### [2026-10-04] JevSpawn — 追加学習なしでエージェントの行動探索を並列化する「構成的アクション空間」手法(論文)

- 出典: https://arxiv.org/abs/2610.00437 (コード: https://github.com/Hoyant-Su/JevSpawn)
- 概要: LLMエージェントがトークン単位で逐次生成する従来方式に対し、自然言語の指示から導出した有限のアクション空間を構成的に組み立て、共有アクション構造とモデルprefixにより重複生成・コンテキスト計算を追加学習なしで削減する手法。Maze/Grid/2048等8つのベンチマークタスクと7つのエージェントベースラインで評価し性能・速度の向上を報告。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では本論文・本リポジトリを紹介する日本語記事は未検出)
- 検証難易度: 低〜中(リポジトリにGPU・APIキー不要で8つのケーススタディの実行ログをブラウザで再生できるデモ(`bash demo/run.sh`→`http://127.0.0.1:8765`)が用意されており、これなら1時間未満で確認可能。フルのベンチマーク再現はQwen3.8-27B+4GPU構成が前提で6時間では非現実的。ライセンス表記は要確認)
- 見栄え: 再生デモで「エージェントが複数の行動を並列探索する様子」を可視化でき、既存のトークン逐次生成方式との対比を記事内で語りやすい。
- 状態: 未選択

### [2026-10-04] ds4(DwarfStar) — Redis作者antirez発、284B MoEモデルをMacでローカル推論する専用エンジン(要注意・日本語記事多数)

- 出典: https://github.com/antirez/ds4 (Hacker News: 208pt/56コメント)
- 概要: Redis作者のSalvatore Sanfilippo(antirez)が開発した、DeepSeek V4 Flash(284B MoE)などモデル固有に最適化したローカル推論エンジン。汎用GGUFランナーではなく専用の選択的量子化(「Dwarf Star量子化」)とディスクKVキャッシュにより、大型MoEモデルをMac上で実用速度で動かすことを狙う。OpenAI/Anthropic互換APIを公開しコーディングエージェントからも利用可能。MITライセンス、公開2週間で23.4k star。
- 日本語記事件数: Zenn 数件(DeepSeekローカル実行の文脈で言及) / Qiita 5件以上(「ds4.cを読み解く」連載、GitHub日報系記事など既に実践的な解説記事が複数公開済み) / note 1件以上
- 検証難易度: 高(Metal/CUDA/ROCm前提でCPUのみの実行パスが無く、最小構成でも64GB以上のMac(Qwen3.8 Flash Q2)、284Bモデル本体の検証には128GB以上のMacまたは複数GPUが必要。一般的なクラウド実行環境やノートPCでは当日中の再現は難しい)
- 見栄え: 著名開発者発という知名度と「ローカルで284Bモデルが動く」という驚きは大きいが、日本語記事が既に多数あり差別化が難しい上、必要ハードウェアのハードルも高い。取り上げる場合は「手元で動かせないので設計(選択的量子化・ディスクKVキャッシュ)をコード読解する」という限定スコープに絞る必要がある。
- 状態: 未選択

### [2026-10-05] Magnitude — YC S25発、起動時に自分のハードウェア向けGPUカーネルを自動チューニングするローカル推論エンジン

- 出典: https://github.com/magnitudedev/magnitude (Launch HN: https://news.ycombinator.com/item?id=49911995)
- 概要: Rust製OSSのローカル推論エンジン。起動時にApple Silicon/NVIDIA/AMD/CPUのみといった自分のハードウェア向けにGPUカーネルを自動コンパイル・チューニングし、開発元ベンチマークではllama.cpp比でMetal最大92%・CUDA19%高速と主張(Apache-2.0)。GitHub 6.4k star、Launch HNは194点・97コメントまで伸びている。
- 日本語記事件数: Zenn 0〜1件(Local LLM記事中で名前のみ言及) / Qiita 0件 / note 1件(「推論エンジンがローカル内蔵、APIキー不要」という紹介記事)
- 検証難易度: 低〜中(Apache-2.0。APIキー不要、GPUが無くてもCPUのみで動作するため、小型.ggufモデルをダウンロードして生成速度を手元/クラウド実行環境で実測できる)
- 見栄え: 自分の環境でのtok/s実測値を他の推論エンジン(llama.cpp等)と比較するBefore/After・数値推移グラフが作りやすい。
- 状態: 未選択

### [2026-10-05] Mem++ — 書き込み時に要約・圧縮しない「非破壊メモリ」で組織向けLLMエージェントの記憶欠落を防ぐ(論文)

- 出典: https://arxiv.org/abs/2610.02002 (コード: https://github.com/AIDAChip-Inc/mem-plus-plus)
- 概要: 文書を日付・著者付きでそのまま全保存し、要約・圧縮を行わず、質問時にのみ語彙的・意味的ランキングで関連文書を選択する非破壊メモリフレームワーク。組織内ベンチマークOrgMemBenchで既存のメモリ手法を8.0〜13.1ポイント上回ると報告(Apache-2.0)。
- 日本語記事件数: Zenn 0件(Mem0/Zep等の一般的なエージェントメモリ記事はあるがMem++固有の記事は見当たらない) / Qiita 0件 / note 0件
- 検証難易度: 低〜中(デフォルトはローカルONNX MiniLM埋め込みで動作し有料APIキー不要。PostgreSQL16+pgvectorの準備は必要、GPU不要)。注意: GitHubスター3個と非常に新しく実績の薄いリポジトリのため、挙動の個体差に留意すること。
- 見栄え: 従来の要約型メモリとMem++の非破壊取得を同じ質問にぶつけ、回答精度・情報欠落の有無を比較するBefore/Afterデモが作りやすい。

### [2026-10-08] diagram-design — 指示文だけでエディトリアル調の図解を自動生成するClaude Code向けagent skill

- 出典: https://github.com/cathrynlavery/diagram-design
- 概要: Claude Code/Codex/GitHub Copilot等向けのagent skillで、自然言語の指示だけで自己完結HTML+インラインSVGのエディトリアル調図解(アーキテクチャ図・シーケンス図・ER図・タイムライン等)を生成する。Mermaid風の素朴な見た目を避け、対象Webサイトの配色・フォントを読み取ってブランドに合わせる機能もある(MITライセンス)。本日GitHub Trending(全言語)で2位に急伸中。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(海外メディアの解説記事は複数あるが日本語での一次紹介は未検出)
- 検証難易度: 低(MIT。Claude Code自身にスキルとして追加するだけで追加の有料APIキー不要、GPUも不要。PNG書き出しにはPlaywright+Chromiumが必要だが、SVG/HTMLでの確認だけなら不要)
- 見栄え: 本リポジトリ自身の構成図やexperiments/day-NNNの処理フローをこのスキルで自動生成し、手書き/Mermaidとの見た目をBefore/After比較できる。本チャレンジのX投稿用シェアカード(HTML+SVG)との相性も良い。
- 状態: 未選択

### [2026-10-08] plannotator — エージェントの計画・コード差分をブラウザでアノテーションして戻すローカル完結レビューツール

- 出典: https://github.com/backnotprop/plannotator
- 概要: Claude Code/Codex/Gemini CLI等のエージェントが提示した「計画(プラン)」やコード差分・HTML出力をブラウザ上で開き、削除・置換・挿入・コメントで直接アノテーションしてエージェントにフィードバックを返すローカル完結のレビューツール。GitHub/GitLabのPR/MRレビューにも対応。GitHub Trending(TypeScript)で急伸中。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(日本語ドキュメントのミラーはあるが一次解説記事は未検出)
- 検証難易度: 低(公式READMEはApache-2.0/MITデュアルライセンスと明記。ただし日本語ドキュメントの付録にはクラウド共有機能について「BSL-1.1」という記載もあり要確認。コアのローカルレビュー機能自体には追加のLLM APIキーは不要、GPUも不要)
- 見栄え: 本リポジトリのRoutine運用(朝リサーチ→通勤中レビュー→昼実装→夜レビュー)にこのツールを組み込み、実際にPRの差分をブラウザでアノテーションして戻す様子をBefore/After的に見せられる。「人間が確認・仕上げを行う」という本チャレンジの運用そのものを強化する自己言及的なネタとして語りやすい。
- 状態: 未選択

### [2026-10-08] freellmapi — 複数プロバイダの無料枠を1つのOpenAI互換エンドポイントに集約するセルフホスト型ルーター

- 出典: https://github.com/tashfeenahmed/freellmapi
- 概要: 複数のLLMプロバイダの無料枠を1つのOpenAI互換`/v1`エンドポイントに集約し、レート制限(429)やサーバーエラー時には自動で次のプロバイダへフェイルオーバーするセルフホスト型ルーター。登録したAPIキーはSQLiteにAES-256-GCMで暗号化保存される(MITライセンス、「個人の実験用」と明記)。GitHub Trending(TypeScript)で急伸中。
- 日本語記事件数: Zenn 0件(無関係なllama.cpp記事のみ検出) / Qiita 0件 / note 0件
- 検証難易度: 中(ルーター本体はMITでAPIキー・GPU不要だが、実際に使うには複数プロバイダの無料枠キーを自分で取得・登録する必要がある。Dockerでの一発導入は可能)
- 見栄え: 本チャレンジの方針「有料APIキー不要」に正面から合致するツールで、複数の無料LLMプロバイダを1つの窓口で切り替えながら応答品質・速度をBefore/After的に比較する表が作りやすい。
- 状態: 未選択

### [2026-10-08] OpenSRE — ログ・メトリクス・トレースを集めて根拠付きで根本原因を返すAI SREエージェント構築OSS

- 出典: https://github.com/Tracer-Cloud/opensre
- 概要: ログ・メトリクス・トレース・直近のデプロイ情報を集めて仮説を検証し、根拠付きの回答を返す「AI SREエージェント」を構築するOSSフレームワーク(Apache-2.0)。60以上のツールに接続でき、Slack/PagerDuty/Telegramへの要約投稿にも対応。Public alpha。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(agentpedia.codesの日本語ガイドはあるが著者自身による一次検証ではない)
- 検証難易度: 中〜高(Apache-2.0。`opensre`実行時のサインインでホスト型モデルが有効化される仕組みで、無料枠の範囲かは要確認。セルフホスト・コンテナ構成では`LLM_PROVIDER`と対応するAPIキーが必須。Public alphaのため挙動が変わりやすい点にも注意)
- 見栄え: 意図的に軽微な障害(ログにエラーを仕込む等)を用意し、根本原因レポートが返ってくる様子をBefore/After的に見せられる。既に扱ったエージェント安全性・信頼性系(HexStrike AI・OpenShell・Uber ADR等)の実務応用編として語れる。
- 状態: 未選択

### [2026-10-08] Codex Security — 脆弱性の発見・検証・修正パッチ生成までを担うOpenAI公式CLI/SDK(要注意・有料APIキー前提)

- 出典: https://github.com/openai/codex-security
- 概要: リポジトリやGit差分をスキャンして脆弱性を発見・検証し、修正パッチやSECURITY.mdドラフトまで生成するOpenAI公式のCLI/TypeScript SDK(Apache-2.0)。2026年3月に研究プレビュー、7月にOSS版CLIが公開された。GitHub Trending(Python)で急伸中。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(Gigazine等のニュース解説記事はあるが一次検証記事は未検出)
- 検証難易度: 高(**スキャン実行には`OPENAI_API_KEY`または`CODEX_API_KEY`が必須**で、代替のAmazon Bedrock/OpenRouter/Fireworks AIもいずれも有料API前提。本リポジトリの方針「有料APIキー必須候補は選ばない」に抵触するため、無料枠だけで完結できない限りtoday.mdでは選ばないこと)
- 見栄え: 意図的に脆弱なサンプルコード(例: SQLインジェクション可能な簡単なアプリ)を用意し、検出→検証→修正パッチ提案までの流れをBefore/Afterで見せられ、インパクトは大きい。ただし有料キー制約のため、扱う場合は無料クレジット枠内での限定実行に留める必要がある。
- 状態: 未選択
- 状態: 未選択

### [2026-10-05] ICoA — 「ユーザーに気づかれるか」で間接プロンプトインジェクションの成功率を分解する指標CSR/OSR(EMNLP 2026採択論文、要注意・有料APIキー前提)

- 出典: https://arxiv.org/abs/2608.30362 (コード: https://github.com/yslmoment/ICoA)
- 概要: 「Will the User Ever Know?」論文。ツール利用LLMエージェント向け間接プロンプトインジェクション攻撃の成功率を、ユーザーが気づけるか否かでCovert Success Rate(CSR)/Overt Success Rate(OSR)に分解する指標を提案し、提案攻撃ICoAがAgentDojo上の864ベンチマーク(4モデル×9攻撃×6防御×4タスクスイート)で既存手法より3.79〜12.01ポイント高いCSRを達成したと報告(MITライセンス)。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(プロンプトインジェクション全般の記事は多数あるが本論文固有の内容は未発信)
- 検証難易度: 中〜高(**デフォルト審査官にOPENAI_API_KEYまたはGOOGLE_API_KEYが必須**。ローカルOllama経由のLLaMA-3.3-70B/Qwen3-235B等も使えるが大型でDay内実行には重い。**本リポジトリの「有料APIキー必須候補は選ばない」方針に抵触するため、無料枠や軽量ローカル審査官への差し替えができない限りtoday.mdでは選ばないこと**)
- 見栄え: 防御あり/なしでの隠蔽成功率の違いを棒グラフ化でき、既に扱ったエージェント安全性系(HexStrike AI・OpenShell・SkillSpector)の続編として語りやすい。
- 状態: 未選択

### [2026-10-05] PageIndex — ベクトルDB不要、文書の目次ツリーをLLMに推論させる「推論ベースRAG」(日本語記事多数・要有料APIキー)

- 出典: https://github.com/VectifyAI/PageIndex (MCP版: https://github.com/vectifyai/pageindex-mcp)
- 概要: ベクトル埋め込み・チャンキングを使わず、文書の階層構造(目次ツリー)をLLMに推論させて該当箇所を探索する「ベクトルなし・推論ベースRAG」。FinanceBenchで98.7%の精度、1ページあたり約$0.001のインデックス構築コストを報告(MITライセンス)。
- 日本語記事件数: **Zenn 5件以上 / Qiita 4件以上 / note 4件以上**(既に複数の深掘り解説記事が公開済み)
- 検証難易度: 低(pip install一発で使えるが、公式クイックスタートはOpenAI APIキー〈gpt-5.6系モデル〉が前提。GPU不要)。本リポジトリの「有料APIキー必須候補は選ばない」方針上、代替の無料バックエンドに差し替えられない限りそのままは選びにくい。
- 見栄え: 精度・コストの数値比較は作りやすいが、日本語記事が既に多数あり差別化が最大の課題。
- 状態: 未選択

### [2026-10-05] SE-GoS — 数千件規模のスキルライブラリ向け学習不要の自己進化型Graph-of-Skills(論文、要有料APIキー)

- 出典: https://arxiv.org/abs/2609.08228 (コード: https://github.com/PKUfudawei/SEGoS, データ: https://huggingface.co/datasets/PKUfudawei/SEGoS-data)
- 概要: LLMエージェントのスキルライブラリが数千件規模に膨らんだ際の検索ボトルネックを、学習不要(training-free)のグラフ進化で解消する手法。実行トレースからスキル間の関係・重み・説明文を更新し、SkillsBenchで平均報酬を52.4%→59.4%に改善、全スキルロードより少ないトークンで済むと報告。Claude Codeのスキルエコシステムと文脈的に相性が良いテーマ(Apache-2.0、evaluation/skillsbench配下はSkillsBench本体のライセンスを継承)。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(完全に未発信)
- 検証難易度: 中(`./scripts/download_data.sh`で再現環境を構築でき主要実験は単一コマンドで実行可能。ただしL3ノード更新〈LLMベースの進化機能〉にOpenAI Chat Completions APIキーが必須)。本リポジトリの方針上、代替の無料バックエンドに差し替えられない限りそのままは選びにくい。注意: GitHubスター0個の非常にニッチな新規リポジトリ。
- 見栄え: 進化前後でのタスク成功率・トークン消費量の比較グラフが作りやすい。
- 状態: 未選択

### [2026-10-06] heretic — TPEベースの自動パラメータ探索で任意のLLMから安全アラインメントを自動除去するabliterationツール

- 出典: https://github.com/p-e-w/heretic (GitHub Trending Python 2026-10-05、+331star/日、33.7k star)
- 概要: transformer系言語モデルの「拒否方向」を検出し、方向性アブレーション(abliteration)によって安全アラインメント(検閲・拒否挙動)を自動的に除去するCLIツール。TPEベースのOptunaパラメータ最適化により、拒否率の低減とKLダイバージェンス(元モデルからの劣化)を co-minimize し、人手でのハイパーパラメータ調整なしに「検閲除去済みモデル」を生成できるのが特徴。Llama/Qwen/Gemma/GPT-OSS等の主要モデルに対応。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(zenn.dev/qiita.com/note.com上での本リポジトリ固有の紹介記事は検索した範囲では未検出。ただしgigazine、weel.co.jp、korben.info/ja、apidog.com/jp等の日本語テックメディアでは既に紹介記事が複数出ている点に注意。Zenn/Qiita/note固有ではないため0件としたが完全な独自ネタとは言いにくい)
- 検証難易度: 低〜中(ライセンスはAGPL-3.0。`pip install heretic-llm`で導入可能、APIキー不要。README記載ではRTX 3090でQwen3-4B-Instructの処理に20〜30分、4bit量子化でVRAM削減可能なためGPU付き環境なら6時間以内の検証が狙えるが、CPUのみでの実行速度・可否は未確認)
- 見栄え: 「同じプロンプトに対し元モデルは拒否するが、処理後のモデルは応答する」というBefore/After比較が直感的でデモ映えしやすい。一方で「検閲除去」という題材自体はセンシティブなため、紹介する場合は目的・ライセンス・悪用可能性への言及など慎重な書き方が必要。
- 状態: 未選択

### [2026-10-06] text-to-cad — Claude Code等のコーディングエージェントに「CAD/CAE/CAM」能力を与えるagent skillライブラリ

- 出典: https://github.com/earthtojake/text-to-cad (GitHub Trending Python 2026-10-05、+620star/日、17.9k star)
- 概要: 見た目だけの text-to-3D ではなく、Open CASCADE(OCP)/build123dをバックエンドに、自然言語の指示から寸法・制約を持つ本格的なCADモデルを生成・検証できるagent skillライブラリ。Claude Code/Codex/Cursor/Gemini/Grok等、既存のコーディングエージェントに「スキル」として追加するだけで使え、STEP/STL/3MF/GLB出力やURDF/SRDF/SDFのロボット記述ファイル生成、ブラウザでのローカルプレビューにも対応。
- 日本語記事件数: Zenn 0件(Zoo社の別のtext-to-CAD技術を紹介する記事はあるが本リポジトリ固有の記事ではない) / Qiita 0件 / note 0件(検索した範囲では本リポジトリ自体を紹介する日本語記事は未検出)
- 検証難易度: 低(MITライセンス。`uv`とPython 3.11+で導入、コーディングエージェント自身〈本リポジトリの実装RoutineであるClaude Code自身でも可〉に「text-to-cadをインストールして」と頼むだけで使えるため追加の有料APIキー不要。6時間以内の検証は十分可能)
- 見栄え: 「自然言語の指示から実際に寸法のあるCADモデルが生成され、ブラウザでプレビューできる」という工学的な見栄えがあり、ソフトウェア専用エージェントが物理世界の設計に踏み出す例としても語りやすい。
- 状態: 未選択

### [2026-10-06] OpenMontage — コーディングエージェントを「動画制作スタジオ」化するOSSのagentic動画生産システム(要注意・大規模フレームワーク)

- 出典: https://github.com/calesthio/OpenMontage (GitHub Trending Python 2026-10-05、+973star/日、64.6k star、GitHub Trending全体1位)
- 概要: Claude Code/Cursor/GitHub Copilot等のコーディングエージェントに、12本のパイプライン・52個のツール・500以上のagent skill(Markdown)を与え、リサーチ→台本→ナレーション→編集→レンダリングまでの動画制作を自動化するOSSシステム(AGPLv3)。Kling/Runway/Veo等20以上の有料動画生成APIにも対応する一方、公式ドキュメントは「有料APIキー無しでも実際の動画が作れる」とし、オフラインTTS(Piper)・FFmpeg・Remotionのみで完結する構成も用意している。
- 日本語記事件数: Zenn 0件(「AIエージェントで動画を全自動生成」等、関連テーマの別記事はあるが本リポジトリ固有の記事ではない) / Qiita 要確認(検索結果に「OpenMontageをText-to-Videoツールとして紹介した記事が1件ある」という言及があったが、本リポジトリ〈calesthio/OpenMontage〉への言及かURLは未確認) / note 0件
- 検証難易度: 中(AGPLv3。有料APIキーを使わずPiper/FFmpeg/Remotionのオフライン構成に絞れば本リポジトリの方針〈有料APIキー不要〉を満たせるが、「12パイプライン・52ツール・500 skill」という規模が大きいため、6時間でどこまで動かせるか〈1本の短い動画を最小構成で生成する、等〉スコープを事前に絞り込む必要がある)
- 見栄え: 実際に生成された短い動画ファイルそのものがデモになり、インパクトは大きい。ただし記事内での動画の共有方法(埋め込み/リンク/静止画抜粋)の検討が必要。
- 状態: 検証済み(day-009, PR作成)。紹介文の「52ツール・500以上skill」は実測と不一致(ツールレジストリ登録137個・skill数157個)。Piper TTS・Remotion・FFmpegのみ(有料APIキー0件)でナレーション付き動画を実際にレンダリング。Remotion初回レンダリングはネットワーク制限でブロックされ`--browser-executable`等の回避策が必要、Piperも公式インストール手順が現行バージョンと食い違うなど複数のつまずきあり。詳細はexperiments/day-009/。

### [2026-10-06] MemAdapter — 長期記憶によってLLMエージェントがユーザーの誤った信念に追従してしまう「記憶誘発性おもねり」への対処(論文、一部有料API)

- 出典: https://arxiv.org/abs/2610.05162 (コード: https://github.com/DEEP-JLU/MemAdapter)
- 概要: LLMエージェントの長期記憶が、ユーザーの過去の(誤った)発言や信念とエージェントを過剰に整合させてしまう「記憶誘発性sycophancy(おもねり)」を、反事実推論(counterfactual reasoning)・文脈認識リフレクション・証拠に基づく推論によって緩和するフレームワーク。MemSyco-Bench/MemTrapBench/PersistBenchの3ベンチマーク・5種のメモリシステムで評価。day-008で検証したMem++(非破壊メモリ)の続編的なテーマとして、「記憶をどう保持するか」ではなく「記憶にどう追従しすぎないか」を扱える。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では本論文・本リポジトリを紹介する日本語記事は未検出)
- 検証難易度: 中〜高(ライセンス記載なし・要確認。論文の主評価はDeepSeek-V4-Flash/GPT-5.6-sol等のAPIモデルを使うが、Qwen3-8Bを4bit NF4量子化でローカル実行する構成も使われているため、有料APIキーを使わずQwen3-8Bのみに絞った縮小版の概念実証は可能と見込まれる。本家ベンチマークのフル再現は非現実的)
- 見栄え: day-008のMem++と対比させ、「何を憶えておくか」→「憶えたことにどう追従しすぎないようにするか」という記憶シリーズの続きとして語れる。誤った信念に追従する前後の回答をBefore/After的に見せやすい。
- 状態: 未選択

### [2026-10-06] SearchJev — 自己回帰生成を回避し検索エージェントの行動判断を5倍高速化する「System-1」モデル(論文、GPU必須)

- 出典: https://arxiv.org/abs/2610.05107 (コード/重み: https://github.com/EvoScientist/SearchJev, https://huggingface.co/SearchJev)
- 概要: Huawei Technologies等による、検索エージェントの「検索する/しない」等の短い行動判断を、自己回帰的なトークン生成を介さずスキーマ条件付きの確率予測として直接出力するSystem-1モデル。0.8B/4Bの2バリアントをQwen3.5バックボーンで構築し、従来の自己回帰生成方式より5.2〜5.3倍高速な判断を報告(Apache-2.0、学習コード・データセット・重みを公開)。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では本論文・本リポジトリを紹介する日本語記事は未検出)
- 検証難易度: 高(**flash-linear-attentionカーネルがGPU専用のためCUDA対応GPUが必須、CPUのみでの実行は不可**と公式に明記。論文の学習には6xH200を使用しているが、公開済み重みを使った推論のみであればより小さいGPUでも可能な見込み。クラウド実行環境にGPUが無い場合は検証不可能であり、採用する場合はGPU付き環境の確保が前提)
- 見栄え: 「自己回帰生成 vs 直接確率予測」の速度比較(tok/s、レイテンシ)を数値とグラフで見せやすく、検索エージェントの実行速度という実用的な切り口が技術者向けに刺さりやすい。
- 状態: 未選択

### [2026-10-07] i-have-adhd — 「結論を埋没させない」出力整形スキルがClaude Code向けに急拡大

- 出典: https://github.com/ayghri/i-have-adhd (GitHub Trending Python 2026-10-07、本日+620star、55,020star)
- 概要: コーディングエージェントの応答を、次の一手を先頭に出し・複数ステップを番号付けし・前置きを削り・末尾に具体的な次の一手を1つだけ残す形式に変換するスキル+プラグイン(MITライセンス)。Claude Code/Codex等に`claude plugin`経由で追加できる。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では本リポジトリ固有の日本語紹介記事は未検出。Android Authority・Medium等の英語メディアでは既に複数紹介されている)
- 検証難易度: 低(MIT。`claude plugin marketplace add`で導入するだけで動作確認できる。追加のAPIキー・GPU不要)
- 見栄え: スキル導入前後で同じ質問をしてClaude Codeの応答フォーマットがどう変わるかをBefore/Afterで見せやすい。中身は1枚のSKILL.mdなので、検証に深さを出すには応答の行数・結論までの文字数などの定量評価を自分で設計する必要がある。
- 状態: 未選択

### [2026-10-07] REA(morluto/rea) — ネイティブバイナリ/アプリをエージェントにリバースエンジニアリングさせるMCPサーバーが急伸

- 出典: https://github.com/morluto/rea (GitHub Trending TypeScript 2026-10-07、本日+4,666star、14,340star。npm: rea-agents)
- 概要: コーディングエージェントにネイティブバイナリ(Mach-O/ELF/PE)・Electron/JSアプリ・.NETアセンブリ・Android APK等を解析させ、「元のソースコードは復元しない」前提で機能の挙動を調査し自分のプロジェクトへの再実装の参考にするためのCLI/MCPサーバー(MITライセンス)。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出)
- 検証難易度: 中(MIT。静的なJS解析だけならNode.js/npmのみで追加ツール不要だが、ネイティブバイナリ解析には解析エンジン(Hopper/Ghidra/IDA Pro)が別途必要。無料OSSのGhidra〈JDK21+〉を使えば有料ソフトなしで検証可能。APIキーはエージェント側の既存契約で足りる見込み、GPU不要)
- 見栄え: 「自分で作った/公開されている小さなバイナリやアプリを渡し、エージェントが機能をどこまで正確に説明できるか」のBefore/After的なデモが作れる。リバースエンジニアリング系ツールのため、検証対象は自分が用意した・ライセンス上問題のないサンプルに限定し、教育・防御目的である旨を記事で明記する必要がある。
- 状態: 未選択

### [2026-10-07] Uber ADR — AIエージェント専用の検知・対応システム(社内10ヶ月運用実績のEDR相当)がオープンソース化

- 出典: https://github.com/uber/ADR (MLSys 2026採択論文。解説: https://techstrong.ai/articles/uber-open-sources-tool-to-catch-agentic-blunders-legacy-security-misses/)
- 概要: Uberが社内のAIエージェント(Claude Code/Cursor等の従業員向けツールや顧客対応チャットボット)を10ヶ月以上監視してきた、プロンプト・推論・ツール呼び出し・結果の因果チェーンを記録するエージェント専用の検知システム「Agentic AI Detection and Response(ADR)」。302タスク×17攻撃手法×133MCPサーバーのベンチマークADR-Benchで既存手法比2〜4倍のF1スコアを主張(Apache-2.0)。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出。英語では複数のテック系メディア記事あり)
- 検証難易度: 中(Apache-2.0。デフォルトの`adr`検知器はAnthropic/OpenAI両方のAPIキーが必須だが、`--detector llamafirewall`を使えばAPIキー不要のkeylessスモークテストが可能と公式に明記されている。本リポジトリの方針上、llamafirewall検知器に限定して検証する必要がある。GPU不要)
- 見栄え: 意図的に不審な振る舞い(権限外アクセス等)を含むセッションをADR-Bench収録タスクの一部で流し、検知される/されないをBefore/After的に見せられる。既に扱ったエージェント安全性系(HexStrike AI・OpenShell・SkillSpector)の続編として語りやすい。
- 状態: 未選択

### [2026-10-07] treg — 「モデルのOpenRouter」ではなく「ツールのOpenRouter」を自称するAIエージェント向けAPIゲートウェイ

- 出典: https://github.com/superdesigndev/treg (GitHub Trending Python 2026-10-07、本日+407star、4,734star。PyPI: tools-registry)
- 概要: SEO・ソーシャル分析・スクレイピング等2,600以上の外部APIを1つのトークンでまとめて呼び出せる、認証情報注入型のプロキシ+レジストリ。チームの鍵・スキル・CLIを共有しエージェント同士で使い回せる(Apache-2.0+再配布制限条項)。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲ではZenn/Qiita/noteへの固有紹介記事は未検出。海外メディアの日本語翻訳記事〈eesel.ai等〉はあるが一次検証記事ではない)
- 検証難易度: 低(treg.toへの無料アカウント登録とtregトークン取得が必要だが、有料APIキーなしでも「検証済み公開ルート」経由でカタログの一部ツールを無料で呼び出せると説明されている。GPU不要。セルフホスト版〈`pip install "tools-registry[server]"`〉ならSQLiteで単体起動も可能)
- 見栄え: 「1つのトークンでエージェントが複数の外部APIを横断的に呼び出す」様子を実際のレスポンスとともに見せやすい。無料ルートの範囲でどこまで使えるかを正直に書く必要がある。アカウント登録が前提になる点は記事内で明記する。
- 状態: 未選択
