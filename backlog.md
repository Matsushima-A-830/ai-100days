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
- 状態: 未選択

### [2026-09-30] OpenAI dots — GPT-6 Astra搭載の常時稼働AIエージェント(DevDay 2026発表、ニュース扱いのみ)

- 出典: OpenAI DevDay 2026発表 (解説: https://www.itmedia.co.jp/aiplus/article/2609/30/2000001864/ , https://www.macrumors.com/2026/09/29/openai-launches-dots/)
- 概要: GPT-6 Astraを搭載し、専用クラウドマシン・ブラウザ・記憶を持って、ChatGPTを閉じていてもタスクを継続して進める「常時稼働」型AIエージェント。ChatGPT/SMS/Slack/Teams経由でメッセージを送って作業を進められる。
- 日本語記事件数: Zenn 2件以上 / Qiita 未確認 / note 3件以上(DevDay直後から多数の解説記事が出ており日本語での一次紹介は既に飽和状態)
- 検証難易度: 高(ChatGPT Pro/Business Premium/Enterpriseプラン限定のクローズドな有料機能で、コード・APIは公開されていない。本リポジトリの方針「当面は有料APIキー/有料プラン必須の候補を選ばない」に抵触するため、今回は選定不可)
- 見栄え: ニュース価値は高いが「動かして検証する」ネタにはできない。取り上げる場合はニュース解説のみの扱いに留める必要あり。
- 状態: 未選択
