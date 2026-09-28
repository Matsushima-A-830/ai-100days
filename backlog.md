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
- 状態: 採用済み(day-001)

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
