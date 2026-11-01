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

### [2026-10-10] anthropics/knowledge-work-plugins — Anthropic公式、Claude Cowork/Code向け職種別プラグイン集

- 出典: https://github.com/anthropics/knowledge-work-plugins (本日GitHub Trending Python/全言語で+626star/日)
- 概要: Anthropic自身が公開した、Claude Cowork(および Claude Code)向けの職種特化プラグイン集(Apache-2.0)。productivity/sales/customer-support/product-management/marketing/legal/finance/data/enterprise-search/bio-research/cowork-plugin-managementの11種を収録し、各プラグインはskills・MCP連携(`.mcp.json`)・slashコマンド・サブエージェントをMarkdown/JSONのみで構成する(コード・ビルド不要)。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語での一次検証記事は未検出。英語解説記事〈the-decoder.com等〉は複数あり)
- 検証難易度: 低(Apache-2.0。`claude plugin marketplace add anthropics/knowledge-work-plugins`→`claude plugin install <plugin>@knowledge-work-plugins`でClaude Code側から追加の有料APIキー無しで導入可能。外部ツール〈Slack/Notion/HubSpot等〉と連携するMCPは`.mcp.json`経由だが、未設定でも各skillやslashコマンド単体の動作は確認できる見込み。GPU不要)
- 見栄え: 「productivityプラグイン導入前後でClaude Codeの職務特化タスク〈議事録整理・スプレッドシート作成等〉への応答がどう変わるか」のBefore/After比較が作りやすい。Anthropic公式発というニュース価値も高い。
- 状態: 採用済み(day-013)

### [2026-10-10] ppt-master — ドキュメント/トピックからネイティブ編集可能なPowerPointを生成するAIエージェント向けスキル

- 出典: https://github.com/hugohe3/ppt-master (本日GitHub Trending Pythonで+515star/日)
- 概要: Claude Code/Cursor/Codex CLI等のエージェントに組み込み、文書やトピックからスライド画像ではなくネイティブな図形・グラフ・表を持つ編集可能な`.pptx`を生成するワークフロー(MIT。オプションのPDF変換機能はAGPL-3.0のPyMuPDFに依存)。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(open-design.ai等に日本語の紹介記事はあるが著者自身による検証記事ではない)
- 検証難易度: 低(Python 3.10+とrequirements.txtの導入のみ。画像生成はエージェント自身の画像ツールかOpenverse/Wikimedia経由の無料Web画像検索で代替でき、有料の`*_API_KEY`〈gpt-image-2等〉無しでも検証可能。モデルはClaude Code自身を使えば追加キー不要。GPU不要)
- 見栄え: 実際に生成された`.pptx`(ネイティブなグラフ・表入り)をスクリーンショットで見せられ、「スライド画像ではなく編集可能なオブジェクトとして生成される」という差別化ポイントを実物で示せる。短期間で38k star超という伸びの速さにも触れる価値あり。
- 状態: 未選択

### [2026-10-10] REMORY — 要約だけでは拾えない情報を補う「残差メモリ」でLLMエージェントのコンテキスト圧縮を改善(論文)

- 出典: https://arxiv.org/abs/2610.11287 (Hugging Face Daily Papers、コード: https://github.com/1ring2rta/Remory)
- 概要: 長期稼働エージェントの履歴をテキスト要約だけに圧縮すると、要約が拾いきれない情報が後続の判断を損なうという問題に対し、履歴と要約を条件に少数の「ソフトメモリトークン」を要約の後ろに追加生成し、フルコンテキストでの応答に近づける手法(残差接続のアナロジー)。SummHayで入力位置の5.2%のみでフルコンテキスト相当のスコアに近づき、Qwen3.8-27B/GLM-5.3-FlashでBrowseComp・Terminal-Bench 2.1のツール呼び出し重複/エラーを削減したと報告。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出)
- 検証難易度: 中(コード公開済み〈github.com/1ring2rta/Remory〉、Hugging Faceに学習済み重み〈Qwen3.8-27B/GLM-5.3-Flash向け〉もあるが、いずれも大型モデルでGPU前提の可能性が高い。本リポジトリの方針に沿うなら、フル再現ではなく「要約のみ」vs「要約+残差メモリ」の設計思想を小規模な自作ログ・軽量モデルで疑似再現する縮小版の概念実証に絞る必要がある)
- 見栄え: Hindsight・Mem++・MemAdapter・Headroom等、本チャレンジで既に扱ってきた「エージェントメモリ/コンテキスト圧縮」シリーズの最新作として位置づけられ、Before/Afterのトークン削減率・精度比較グラフが作りやすい。ただし同テーマが頻出しているため、採用する場合は差別化(「要約の欠落をどう補うか」という新しい切り口)を明記した方がよい。
- 状態: 未選択

### [2026-10-10] andrej-karpathy-skills — Karpathyの指摘するLLMコーディングの落とし穴に対処する単一CLAUDE.mdファイル

- 出典: https://github.com/forrestchang/andrej-karpathy-skills (ミラー: https://github.com/multica-ai/andrej-karpathy-skills。本日GitHub Trending〈multica-ai版〉で+279star/日、本家forrestchang版は218.2k star・22.0k fork)
- 概要: Andrej Karpathyが公言したLLMコーディングの落とし穴(未検証の前提を置く・過剰な抽象化等)に対処するため、「コーディング前に考える」「シンプルさ優先」「外科的な変更のみ」「ゴール駆動の実行」という4原則をまとめた単一のCLAUDE.mdファイル(MIT)。Claude Codeプラグインとしての導入、または既存CLAUDE.mdへの追記のどちらでも使える。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出。英語・ドイツ語・中国語の紹介記事は複数あり)
- 検証難易度: 低(MIT。ファイル1つをプロジェクトに追記するだけで追加の有料APIキー・GPU不要。導入前後で同じ曖昧なタスクをClaude Codeに与え、応答〈前提確認の有無・変更範囲の広さ等〉がどう変わるかを比較するだけで6時間以内に完結する)
- 見栄え: 「CLAUDE.mdを1つ追加するだけでClaude Codeの振る舞いがどう変わるか」というBefore/After比較は分かりやすく、本リポジトリ自身がClaude Code Routineで運用されているという自己言及的な文脈にも合う。注意: multica-ai版は本家forrestchang版のミラー/派生と見られ、READMEのインストールコマンドもforrestchang側を指すため、検証はforrestchang/andrej-karpathy-skills(本家)で行うこと。
- 状態: 未選択

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
- 状態: 採用済み(day-026、ローカルPCで検証完了。詳細はexperiments/day-026/README.md)

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

### [2026-10-09] Headroom — ツール出力・ログ・RAGチャンクをLLMに渡す前にローカル圧縮するコンテキスト圧縮レイヤー

- 出典: https://github.com/headroomlabs-ai/headroom (GitHub Trending Python 2026-10-09、+120star/日、74,834star。旧名chopratejas/headroom、2026年1月公開・7月に開発元がHeadroom Labsとして法人化した同一プロジェクトの改名と確認)
- 概要: AIエージェントのツール出力・ログ・ファイル・RAGチャンク・会話履歴をLLMに送る前にローカルで圧縮するミドルウェア(ライブラリ/プロキシ/MCPサーバーの3形態で導入可能)。JSONはSmartCrusher、ソースコードはAST対応のCodeCompressor、自然文はHugging Face上のKompress-v2-baseモデルで圧縮し、元データはローカルにキャッシュして必要時に取り出せる「可逆圧縮」が特徴(Apache-2.0)。
- 日本語記事件数: Zenn 0件 / Qiita 1件(2026年の紹介記事あり) / note 0件
- 検証難易度: 低(pipインストールのみでAPIキー不要。圧縮処理自体はローカルのONNXモデルで完結しGPU不要。x86では一部機能にAVX2が前提)
- 見栄え: ツール出力を生のまま渡した場合とHeadroom経由で圧縮した場合のトークン数をBefore/Afterで比較しやすく、本リポジトリのRoutine自体に組み込んで実測できる自己言及的ネタとしても語れる(context-mode・caveman等これまでの「コンテキスト削減」系候補の系譜)。公称の「60〜95%削減」はベンダー自身の値でJSON限定、コーディング用途では15〜20%程度との報告もあり、実測値で検証する必要がある。
- 状態: 未選択

### [2026-10-09] alibaba/open-code-review — Claude Codeより少ないトークンで高精度なレビューを主張するAlibaba発OSSコードレビューCLI

- 出典: https://github.com/alibaba/open-code-review (GitHub Trending全言語 2026-10-09、+323star/日)
- 概要: 決定的なファイル選定・バンドリング・ルールマッチングのパイプラインと、動的なコード解析を行うLLMエージェントを組み合わせたハイブリッド型AIコードレビューCLI(Go製、Apache-2.0)。社内2万人以上が利用し100万件超の欠陥を検出したと主張。200PR×10言語の内部ベンチマークでClaude Codeより高いPrecision/F1をおよそ1/9のトークン数で達成したと報告(Alibaba自身の計測で第三者検証ではない)。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出。英語のDEV Community記事やInfoQ記事は複数あり)
- 検証難易度: 低(Apache-2.0。npm一発導入。通常のLLM接続には自前のAPIキー設定が必要だが、「Delegation Mode」を使えばClaude Code等既存のコーディングエージェント自身にレビューさせる方式で追加の有料APIキーは不要。GPU不要)
- 見栄え: 同じPull RequestをClaude Codeの通常レビューとopen-code-review(Delegation Mode)の両方にかけ、指摘内容・トークン消費量をBefore/After比較できる。Alibaba自身の「1/9のトークンで高精度」という主張を自分の環境で検証できる切り口は技術者向けに刺さりやすい。
- 状態: 未選択

### [2026-10-09] video-shotcraft — Claude Code/Codex向けの「映画的プロダクト動画」自動生成agent skill(Remotion土台)

- 出典: https://github.com/Vincentwei1021/video-shotcraft (GitHub Trending TypeScript 2026-10-09、+161star/日)
- 概要: Remotion(Reactベースの動画生成フレームワーク)を土台に、152枚のショットレシピカード・209本のモーションプレビュー・すぐ使える36.2秒のプロモ用テンプレート「Ink Press」を備えたClaude Code/Codex向けagent skill(Apache-2.0。Remotion自体は個人・小規模チームは無料だが企業利用は別途ライセンス契約が必要な場合がある)。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(中国語記事・英語ブログでの紹介はあるが日本語での一次紹介は未検出)
- 検証難易度: 低(Claude Code自身にスキルとして追加するだけで追加の有料APIキー不要、GPUも不要。ヘッドレスLinuxでのレンダリングには`--concurrency=1`指定・ヘッドレスChromeの差し替え・`--browser-executable`指定が必要と報告されており、day-009(OpenMontage)で遭遇したRemotionレンダリングの詰まりどころと共通する点がある)
- 見栄え: テンプレート「Ink Press」をレンダリングし、実際に生成された短いプロモ動画そのものをデモにできる。day-009の知見(Remotionのheadless環境での詰まりどころ)を活かした「今回はどこで詰まったか/詰まらなかったか」という比較記事にしやすい。
- 状態: 採用済み(day-012)

### [2026-10-09] Tencent Hunyuan「Hy-MT2」— 33言語対応・1.8B/7B/30B-A3Bの3サイズを持つ高速多言語翻訳モデル

- 出典: https://github.com/Tencent-Hunyuan/Hy-MT2 (GitHub Trending全言語 2026-10-09、+147star/日)
- 概要: Tencent Hunyuanが公開した多言語翻訳特化モデル群(1.8B/7B/30B-A3B MoEの3サイズ、33言語対応)。自然言語の翻訳指示への追従力を測るベンチマークIFMTBenchも同時公開。公表値では7B/30B-A3Bが高速思考モードでDeepSeek-V4-Pro等を上回り、1.8Bも大手商用翻訳APIを上回ると主張(Apache-2.0)。
- 日本語記事件数: Zenn 1件(kun432氏のスクラップでREADMEベースの概要紹介のみ、詳細な検証はまだ無い) / Qiita 0件 / note 0件
- 検証難易度: 低(APIキー不要。1.8Bモデルはtransformersでのロード、またはllama.cppのGGUF(CPU実行、`-ngl 0`)でGPU無しでも動作可能。30B-A3Bはvllm/SGLang推奨でGPU前提だが、1.8B/7Bに絞れば6時間以内にCPUのみでの検証も狙える)
- 見栄え: 既存の無料翻訳(DeepL無料枠等)とHy-MT2(1.8B)の翻訳品質・指示追従力(「です/ます調で」等のスタイル指定付き翻訳)をBefore/After比較しやすい。1.25bit量子化版(440MB)は個人検証で読み込みに失敗したとの報告もあり、「軽量化の限界」という切り口も語れる。
- 状態: 未選択

### [2026-10-11] lyogavin/airllm — 70Bモデルを4GB GPU 1枚で推論できるOSSライブラリが本日GitHub Trendingに再浮上

- 出典: https://github.com/lyogavin/airllm (本日GitHub Trending Pythonで再浮上)
- 概要: 70B級LLMを量子化・枝刈りなしに、1層ずつGPUへロード→推論→解放する方式で単一4GB GPUでも推論可能にするOSSライブラリ(Apache-2.0)。2023年公開の既存プロジェクトだが、FP8対応・Kimi K3/Qwen3.8対応・学習サポート追加(2026年6〜9月)などの更新が続き、本日のGitHub Trendingに再浮上した。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では本リポジトリ固有の日本語紹介記事は未検出。英語のDEV Community記事では「70Bは本当に動くが非常に遅い」という指摘もある)
- 検証難易度: 中〜高(APIキー不要。ただし公式の仕組み上NVIDIA CUDA GPU、またはApple SiliconならMLX経由が前提で、サンプルコードも`.cuda()`呼び出しを使う。クラウド実行環境にGPUが無い場合、小型モデルでの代替実行可否を確認するか、ローカル検証へエスカレーションする必要がある。モデル本体のディスク容量も大きい点に注意)
- 見栄え: 「層ごとにGPUへストリーミングして70Bを4GBで動かす」仕組みをVRAM使用量とトークン生成速度の実測値で見せられ、「本当に遅いのか」を定量評価できればインパクトがある。GPU有無で検証可否が分かれる点は記事内で明記する必要がある。
- 状態: 未選択

### [2026-10-11] repowise-dev/repowise — LLM呼び出しゼロでコードベースを解析するMCPサーバーが本日GitHub Trending

- 出典: https://github.com/repowise-dev/repowise (本日GitHub Trending Python)
- 概要: リポジトリをローカルでインデックスし、依存関係グラフ・git履歴・健全性スコア・デッドコード検出・アーキテクチャ上の意思決定をMCP経由でコーディングエージェントに提供するコードベース知能ツール(AGPL-3.0。個人・社内利用は無料、エンタープライズ機能や組み込み配布のみ別途商用ライセンス)。グラフ/リスク/健全性/テスト/デッドコード解析は「LLM呼び出しゼロ」で動作し、ドキュメント自動生成など一部機能のみ任意でLLM(自前キーまたはOllama)を使う設計。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出。lobehub等の海外ディレクトリ掲載のみ)
- 検証難易度: 低(`uv tool install repowise`→`repowise init --yes --no-prose`→`repowise serve`で導入可能。コア機能はAPIキー・GPU不要。本リポジトリ(ai-100days)自身に対して実行し、健全性スコアやデッドコード検出結果を見るデモが6時間以内で可能)
- 見栄え: 本リポジトリ自身(experiments/day-NNN群が増えてきた構成)をrepowiseで解析し、生成されたコードベース健全性レポート・依存関係グラフを見せる自己言及的なデモが作りやすい。手動で把握していた構成とMCPツールが即答する内容のBefore/After比較もできる。
- 状態: 未選択

### [2026-10-09] TokenRouter(thu-nics) — 複数LLMをトークン単位で動的に振り分ける推論サーバー、既存比最大64倍のデコード速度(NeurIPS 2026採択・Hugging Face Daily Papers)

- 出典: https://github.com/thu-nics/TokenRouter (Hugging Face Daily Papers 2026-10-09掲載)
- 概要: 小型モデルと大型モデルなど複数のLLMをトークン単位で動的に振り分けながら配信するサービングシステム。`route()`/`send()`/`receive()`の3インターフェースでルーティング手法(R2R・CITER・Co-LLM等)を定義でき、遅延バッチングスケジューラにより既存スタック比2.01〜64.15倍のデコードスループットを報告。NeurIPS 2026採択。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出)
- 検証難易度: 中〜高(APIキー不要でYAML設定のみでモデルをローカル構成できるが、サンプル構成は最小でもQwen3-32Bを含みCUDA MPSが前提のためGPUが実質必須。リポジトリ上でライセンス表記を確認できず要確認)。小型モデル同士のルーティング構成に絞れば6時間以内の縮小版検証も狙えるが、GPU有無が検証可否を左右する。
- 見栄え: 「ルーティングあり/なし」でのデコードスループット(トークン/秒)比較を数値とグラフで見せやすく、推論高速化系(Quail・TensorFold・Magnitude等)の系譜として語れる。ライセンス未確認の点は記事化前に必ず解消する必要がある。
- 状態: 採用済み(day-014)

### [2026-10-09] "What Did the Agent Actually Do? Evidence-Grounded Oversight for Long-Horizon Agents" — エージェントの「申告」と「実際の行動」のズレを検知するモニタリング手法(論文、コード未公開)

- 出典: https://arxiv.org/abs/2610.06406 (Hugging Face Daily Papers 2026-10-09掲載)
- 概要: 長期稼働するコーディングエージェントが行った「重要な意思決定」を検知し、その裏付けとなる実行証拠を提示することで人間が何を確認すべきかを絞り込めるモニタリング手法。ソフトウェア工程タスクのベンチマークAgentMonBench(要件と実際の挙動が一致しているか/モニタが確認すべき自律的決定を認識できるか、の2軸×3サブセット)で評価。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出)
- 検証難易度: 中(検索した範囲ではAgentMonBenchのコード・データセット公開は確認できず、フル再現は不可。本リポジトリの絶対ルール「動かしていないものを動いたと書かない」と直接共鳴するテーマのため、Claude Code自身に簡単なコーディングタスクをやらせ、実行ログと「申告された完了報告」を突き合わせて不一致を検出する自作の縮小版モニタを作る、という概念実証に絞れば6時間以内で可能。APIキー・GPU追加不要)
- 見栄え: 「エージェントが"やりました"と言った内容」と「実際のツール呼び出しログ」を並べて不一致を可視化するBefore/After表が作りやすく、本リポジトリの検証ルールそのものを定量的に補強するテーマとして自己言及的に語れる。日本語記事が無く差別化しやすい。
- 状態: 未選択

### [2026-10-12] obsidian-mind — AIコーディングエージェントにセッション横断の永続メモリを与える自己組織化Obsidianボルト

- 出典: https://github.com/breferrari/obsidian-mind (GitHub Trending TypeScript 2026-10-12、+82star/日、5.2k star)
- 概要: Claude Code/Codex CLI/Gemini CLI向けに、North Star・進行中プロジェクト・直近の意思決定を記録するObsidianボルトのテンプレートとフック/MCPサーバー群を提供し、セッションをまたいで文脈・決定事項・メモを保持できるようにするOSS(MITライセンス)。セマンティック検索用のQMDはローカルの小型モデル(約2.3GB)で動き追加APIキー不要、GPUがあれば使うがCPUフォールバックもある。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出)
- 検証難易度: 低(MIT。`npm install -g shardmind`→`shardmind install github:breferrari/obsidian-mind`で導入し、Claude Code自身をエージェントとして使えば追加の有料APIキー不要。GPUも不要)
- 見栄え: 本リポジトリ自身が`tools/sync-to-obsidian.*`でObsidian Vaultを「恒久的な蓄積場所」として使っている運用方針と直接重なるテーマで、「このRoutine自体にobsidian-mindを試験導入し、セッションを跨いで文脈が本当に復元されるか」を自己言及的に検証できるのが最大の強み。claude-mem(backlog内2026-10-03、未選択)等の既存メモリプラグインとの比較軸も作れる。
- 状態: 未選択

### [2026-10-12] google/skills — Google公式のAgent Skillsライブラリ(Anthropic版との比較候補)

- 出典: https://github.com/google/skills (GitHub Trending Python 2026-10-12、+66star/日、21.2k star)
- 概要: Google Cloud/Gemini関連プロダクト(BigQuery・Cloud Run・GKE・Cloud SQL・AlloyDB・Firebase等)向けのAgent Skillsとプロダクトプラグイン(MCPサーバー連携含む)を集めたGoogle公式リポジトリ(Apache-2.0)。`npx skills add google/skills`でSKILL.md単位にインストールでき、Claude Code/Codex/Antigravity CLI等に対応。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲ではZenn/Qiita/noteでの一次紹介記事は未検出。英語解説記事〈pinggy.io等〉は複数あり)
- 検証難易度: 低(Apache-2.0。Node.js〈npx〉のみで導入可能、個々のskill単体の動作確認には追加の有料APIキー不要と見込まれる。外部クラウドリソース〈BigQuery等〉に実際に接続するskillを使う場合は別途GCP認証情報が必要になる点に注意。GPU不要)
- 見栄え: day-013で検証したanthropics/knowledge-work-plugins(Anthropic公式)と並べ、「2社の公式Agent Skills配布のされ方・構成・導入体験の違い」を比較するBefore/After的な記事が作りやすい。
- 状態: 未選択

### [2026-10-12] microsoft/BitNet — 1-bit LLM(BitNet b1.58)をCPUで高速推論するMicrosoft公式フレームワークが再浮上

- 出典: https://github.com/microsoft/BitNet (本日GitHub Trendingで再浮上、134star/日)
- 概要: 全重みを三値{-1,0,1}に量子化したBitNet b1.58モデル(2.4Bパラメータ・4Tトークン学習済み)を、llama.cppベースの独自カーネル(T-MACのlookup-table手法を応用)でCPU上で高速・損失なく推論するMicrosoft公式フレームワーク(MITライセンス)。ARM CPUで最大5.07倍、x86 CPUで最大6.17倍の高速化を主張。2026年7月にはBitNet量子化を使ったリアルタイム多言語ASR「VibeASR.cpp」や埋め込みモデルも追加された。
- 日本語記事件数: Zenn 2件(GitHub Trending入りを受けた入門記事、および関連する軽量化手法の論文ベース整理記事) / Qiita 0件 / note 0件(単体の実測検証記事はまだ少なく入門記事止まり)
- 検証難易度: 低(MIT。`huggingface-cli`でBitNet-b1.58-2B-4Tモデルをダウンロードし`python setup_env.py`→`run_inference.py`で動作、GPU不要・追加APIキー不要。CPUのみのクラウド実行環境でも6時間以内に動作確認・簡易速度計測が可能)
- 見栄え: 同程度サイズの通常精度モデル(FP16等)とのCPU推論速度・メモリ使用量をBefore/After比較でき、数値グラフが作りやすい。日本語記事が入門記事止まりのため、実測比較という切り口で差別化しやすい。
- 状態: 未選択

### [2026-10-12] "Self-Preservation in Language Models" — 継続ファインチューニング中にモデル自身が生成したリプレイデータで既存知識の忘却を防ぐ手法(論文、コード未確認)

- 出典: https://huggingface.co/papers/2610.12602
- 概要: 継続的なファインチューニングで既存タスクの性能が失われる「破滅的忘却」に対し、保持したいタスクを短い説明(Task Bank)として与え、更新前のモデルのコピー自身にリプレイ用データを生成させて新タスクの学習データと混合する手法。Qwen3(0.6B/1.7B/4B)をMedQA/C-STANCEでファインチューニングし、ARC-C/WinoGrande/PIQA/SVAMP等の未知タスクでの保持率(Retention)を計測、4Bモデルでは新タスクを意識したリプレイ対象選択がランダム選択より保持率を改善(95.69% vs 92.94%)したと報告。平均精度だけでは「3.6%が不正解化・3.6%が正解化」のような変化を見落とす点も指摘。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出)
- 検証難易度: 高(検索した範囲では公式コード・データセットの公開リンクは確認できず、フル再現は不可。本リポジトリの絶対ルールに沿うなら、Qwen3の最小サイズ〈0.6B〉を使い「ファインチューニング後にリプレイ無し/自己生成リプレイ有りで既存タスクの正答率がどう変わるか」を小規模データで疑似再現する縮小版の概念実証に絞る必要がある。APIキー不要、GPUはあれば望ましいがCPUでも0.6Bなら時間次第で可能)
- 見栄え: 「忘却したかどうかを平均精度だけで判断すると見誤る」という論文の指摘自体が、本リポジトリの「動かしていないものを動いたと書かない」という検証ルールと響き合うテーマ。保持率のBefore/Afterグラフが作りやすいが、再現スコープを事前に絞り込む必要があるため採用する場合は候補メモにその旨を明記すること。
- 状態: 未選択

### [2026-10-13] mksglu/context-mode — AIコーディングエージェントのコンテキストウィンドウ消費を最大98%削減するMCPサーバー

- 出典: https://github.com/mksglu/context-mode (GitHub Trending 全言語 2026-10-13、+978star/日、累計28.1k star)
- 概要: Claude Code/Gemini CLI/Codex CLI等向けのMCPサーバー。ツールの生出力を会話に直接流さずサンドボックスでローカルSQLiteにフルテキストを保存し、会話には要約・検索結果のみを渡すことでコンテキストウィンドウ消費を削減(プロジェクト自身の計測では最大98%)。会話がcompactionされてもセッション状態(直近の編集・エラー・タスク等)をBM25検索付きで復元できる。Elastic License 2.0(ソースは公開だが本体をホスティングサービスとして提供することは不可)。
- 日本語記事件数: Zenn 0件 / Qiita 1件(導入を勧める短い紹介記事。本体の検証記事ではない) / note 0件
- 検証難易度: 低(Node.js 22.5+またはBunのみで追加の有料APIキー・GPU不要。`claude mcp add context-mode -- npx -y context-mode`で即導入可能)
- 見栄え: 同じ調査・大量ログ読み込みタスクを導入前/導入後で実行し、`ctx stats`で実際のコンテキスト消費量の差を数値で見せられる。本Routine自身がWebFetch等で大量のツール出力を読む作業をしているため、自己言及的な検証がしやすい。
- 状態: 未選択

### [2026-10-13] mvanhorn/last30days-skill — Reddit/X/YouTube/HN等を並列検索し直近30日間の話題をエンゲージメント順にまとめるClaude Code向けAgent Skill

- 出典: https://github.com/mvanhorn/last30days-skill (GitHub Trending Python 2026-10-13、+103star/日)
- 概要: Reddit・X・YouTube・TikTok・Hacker News・Polymarket・GitHub等を並列検索し、実際のエンゲージメント(反応の大きさ)でランキングした上で出典付きの要約を1本にまとめるオープンソースのClaude Code向けAgent Skill(MIT)。Reddit/HN/Polymarket/GitHub/StockTwitsなど無料ソースのみでも動作し、X/TikTok等の追加ソースは任意の有料APIキーで拡張できる設計。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出)
- 検証難易度: 低(MIT。`/plugin marketplace add mvanhorn/last30days-skill`→`/plugin install last30days`で導入、無料ソースのみに絞れば追加の有料APIキー・GPU不要)
- 見栄え: 本Routine自身が毎朝行っている「複数の情報源を巡回してネタ候補を探す」作業と同じ領域のツールのため、「このスキルに同じ日・同じテーマを調べさせた結果」と「Routineが実際に見つけた候補」を並べて比較するBefore/After記事が作りやすい、非常に自己言及的な候補。
- 状態: 未選択

### [2026-10-13] cathrynlavery/diagram-design — 自然文の指示だけで自己完結HTML+SVGのエディトリアルな図解を生成するAgent Skill

- 出典: https://github.com/cathrynlavery/diagram-design (GitHub Trending 全言語 2026-10-13、+1,813star/日)
- 概要: 「アーキテクチャ図を作って」等の自然文の指示だけで、アーキテクチャ図・シーケンス図・ER図・Sankey図・Wardley mapなど40種類超のエディトリアルな図を、ビルド不要の自己完結HTML(インラインSVG)1ファイルとして生成するAIコーディングエージェント向けAgent Skill(MIT)。Mermaidのような「コードから図を起こす」方式ではなく、既存の関係性に統一されたデザイン規則(1色のアクセント・1pxの罫線・4pxグリッド等)を当てはめる「後処理型デザインシステム」という位置づけ。draw.io/Mermaid/Excalidrawからの読み込みにも対応。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(Zenn/Qiita/noteでの一次紹介・検証記事は未検出。日本語の解説コラム記事〈oflight.co.jp等〉はあるが著者自身の検証記事ではない)
- 検証難易度: 低(MIT。`npx skills add cathrynlavery/diagram-design`またはClaude Codeのプラグインマーケットプレイスから導入。デフォルトのHTML/SVG出力は追加の有料APIキー・GPU不要。PNG書き出しのみPlaywright/Chromiumが必要)
- 見栄え: 本リポジトリ自身の構成(CLAUDE.mdのフロー図やexperiments/day-NNN群の増え方)を実際にこのスキルで図解させ、出力HTMLをブラウザで開いたスクリーンショットをそのまま記事・シェアカードに使える。見た目のインパクトが強く、日本語の一次検証記事が無い点でも差別化しやすい。
- 状態: 未選択

### [2026-10-13] debpalash/VoiceStudio — ElevenLabsの完全ローカル代替を掲げる音声クローン/TTS OSSアプリ、646言語対応を主張

- 出典: https://github.com/debpalash/VoiceStudio (GitHub Trending Python 2026-10-13、+2,277star/日、累計62.9k star)
- 概要: 音声クローン・テキストからの音声デザイン・動画の吹き替え・文字起こし・オーディオブック生成を1つにまとめた、アカウント登録不要・完全ローカル動作のOSSデスクトップアプリ兼ローカルAPI/MCPサーバー(AGPL-3.0。モデル重み・音声・生成物の利用条件はアプリ本体のライセンスとは別途)。既定エンジンはk2-fsa/OmniVoiceで、CosyVoice3・GPT-SoVITS等16種のTTSエンジンに切り替え可能。646言語対応を主張。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(Zenn/Qiita/noteでの一次紹介・検証記事は未検出。日本語の解説コラム記事〈oflight.co.jp等〉はあるが著者自身の検証記事ではない)
- 検証難易度: 中(APIキー・アカウント不要。GPU〈CUDA/Metal〉が無くてもCPUフォールバックで動作するとの記載があるが低速〈参考情報ではApple M3 Maxで1文あたり約30秒〉。クラウド実行環境がCPUのみの場合、短いサンプル生成なら6時間以内に収まる見込みだが、モデルの自動ダウンロード容量がRoutine環境のネットワーク制約に引っかからないかは実際に試して判断し、引っかかった場合はCLAUDE.mdの「Routine環境の制約」に沿ってローカル検証にエスカレーションする)
- 見栄え: 音声サンプルをローカルでクローン生成し、生成音声そのものをデモにできれば非常に見栄えが良い。646言語対応という主張を日本語テキストで実際に試せるかも見どころ。「生成物の利用条件はアプリ本体のライセンスと別」である点を記事で明記する必要がある。
- 状態: 未選択

### [2026-10-14] ifixai-ai/iFixAi — AIエージェントが「言ったこと」と「実際の挙動」のズレを監査するOSSツールが本日GitHub Trendingで急上昇

- 出典: https://github.com/ifixai-ai/iFixAi (GitHub Trending Python 2026-10-14、+2,143star/日、累計27.3k star。Product Hunt 2026-09-29ローンチ)
- 概要: AIエージェントが実際に申告通りの仕事をしているかを独立監査するPython製OSSツール(Apache-2.0)。Fabrication(捏造)・Manipulation(操作)・Deception(欺瞞)・Unpredictability(予測不能性)・Opacity(不透明性)の5本柱に沿った60項目の検査(アドバーサリアルテスト+運用チェック)でA〜Fを採点する。`--provider mock`ならネットワーク非依存のモック相手に動作確認でき(意図的に欠陥入りのため不合格スコアが出る想定)、実際のエージェントを本物のグレードで監査するには検査対象用と判定用(ジャッジ)で異なるベンダーの有料APIキーが2つ必要(フルスイートで見積もり$10〜18)。Claude Code/Codex向けプラグインもあり。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出。英語のProduct Huntローンチ記事はあり)
- 検証難易度: 低〜中(モック監査〈`--provider mock`〉なら追加の有料APIキー・GPU不要で6時間以内に実行・スコアカード取得が可能。ただし「実際に動くエージェントを本物の基準で監査する」フル検証には検査対象モデル用+ジャッジモデル用の計2種類の有料APIキーが必要〈推定$10〜18〉。CLAUDE.mdの方針〈当面は有料APIキー必須の候補を選ばない〉に沿うなら、today.mdではモック監査または自作の簡易エージェントに絞ったスコープを明記して選ぶ必要がある)
- 見栄え: 本リポジトリの絶対ルール「動かしていないものを動いたと書かない」と直接共鳴するテーマで、他ツールのレビューより一段メタな「ツールを監査するツールを監査する」自己言及的な記事が書ける。5本柱ごとのA〜Fスコアカードはそのまま見せやすい。
- 状態: 未選択

### [2026-10-14] K-Dense-AI/scientific-agent-skills — AIエージェントを「AI研究者」に変えるAgent Skills集(旧Claude Scientific Skills)が163種に拡大

- 出典: https://github.com/K-Dense-AI/scientific-agent-skills (累計49.2k star、GitHub Trending Python 2026-10-14で+146star/日。関連arXiv論文: 2609.00065)
- 概要: 生物学・化学・医学・物理・工学・地球科学・データ解析・科学コミュニケーションにまたがる163種のスキルと、100種類超の科学データベースへのガイダンスを収録したAgent Skills集(MIT。個々のスキルのライセンスは`SKILL.md`ごとに異なる場合がある)。Claude Code/Cursor/Codex/Google Antigravity等、オープンなAgent Skills標準に対応するホストで使える。元はClaude Scientific Skillsという名前だったが、Claude専用ではなく汎用のAgent Skills標準対応に改称された。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出)
- 検証難易度: 低(MIT。`npx skills add K-Dense-AI/scientific-agent-skills`で導入。多くのスキルは追加の有料APIキー不要だが、Exa・Benchling・NCBI・Materials Project等一部の外部データベース連携スキルは個別にAPIキーが要る。APIキー不要なスキルに絞って検証範囲を選べば6時間以内に収まる。GPU不要〈GPU活用スキルはオプション〉)
- 見栄え: Claude Code自身に特定の科学スキル〈例: 化学または生物学系〉を実際に使わせ、スキル無し/有りで疑似研究タスクへの応答の深さ・正確さがどう変わるかのBefore/After比較が作りやすい。同じ`npx skills add`エコシステムの中でdiagram-design〈day-016で検証済み〉と対比できる、領域特化スキル集という切り口。
- 状態: 採用済み(day-017)

### [2026-10-14] HKUDS/CLI-Anything — 既存ソフトウェアをAIエージェント対応CLIに自動変換する7フェーズパイプライン

- 出典: https://github.com/HKUDS/CLI-Anything (累計52.4k star、GitHub Trending Python 2026-10-14で+94star/日)
- 概要: 「あらゆるソフトウェアをAIエージェントネイティブにする」を掲げ、既存のGUIアプリ〈GIMP・Blender・LibreOffice・Inkscape・OBS Studio・Zotero・Draw.io・Godot・Ollama等50種類超〉を解析し、Clickベースの構造化CLI〈REPL+JSON出力対応〉を自動生成する7フェーズパイプライン(分析→設計→実装→テスト計画→テスト作成→ドキュメント化→公開)のOSS(Apache-2.0)。生成済みCLIを集めたレジストリ「CLI-Hub」も付属し、`cli-hub install <name>`でコミュニティ製CLIを導入できる。Claude Code/Cursor/Codex等のプラグインとして動作。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出。韓国語〈PyTorch Korea User Group〉・英語の紹介記事は複数あり)
- 検証難易度: 中(Apache-2.0、CLI-Hub自体の導入〈`pip install cli-anything-hub`〉や既存CLIの一覧閲覧・起動は追加の有料APIキー・GPU不要。ただし新規にCLIを自動生成する7フェーズパイプラインを試す場合、対象ソフトウェア〈GIMP等〉がRoutine実行環境に実際にインストールされている必要があり、クラウド実行環境で対象アプリを用意できない場合はCLAUDE.mdの「Routine環境の制約」に沿って軽量な対象〈CLIツールやPythonライブラリ等、追加インストール不要なもの〉に絞るか、ローカル検証にエスカレーションする判断が必要)
- 見栄え: 「このツールにGIMPやBlenderを食わせてAI操作可能なCLIを自動生成させ、実際にエージェントから操作させてみる」というデモは視覚的インパクトが大きい。本リポジトリ自身〈ai-100days〉を解析対象にして簡易CLIを生成させる自己言及的な切り口も可能。
- 状態: 未選択

### [2026-10-14] vercel-labs/skills — Vercel公式のAgent Skillsインストーラ、75以上のコーディングエージェントに対応

- 出典: https://github.com/vercel-labs/skills (累計34.9k star、GitHub Trending TypeScript 2026-10-14で+732star/日)
- 概要: `SKILL.md`形式の再利用可能なAgent Skillsを導入・管理するVercel公式CLI(MIT)。GitHub省略形・フルURL・GitLab・Azure Repos・任意のgit URL・ローカルパス・直接ダウンロードURLなど多様なソース指定に対応し、OpenCode/Claude Code/Codex/Cursor等75以上のエージェントで動作する。実はdiagram-design〈day-016で検証済み〉・K-Dense scientific-agent-skills・CLI-Anythingなど、本バックログに並ぶ他候補が導入コマンドとして挙げている`npx skills add ...`自体がこのツール。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出)
- 検証難易度: 低(MIT。`npx skills add <repo>`のみでAPIキー不要〈GitHub Tokenはprivateリポジトリ用のオプション〉、GPUも不要。6時間以内に複数のスキルソース〈GitHub/GitLab/直接URL等〉からのインストール動作を一通り試せる)
- 見栄え: 単体のデモとしては地味だが、「day-016以降この100日チャレンジが繰り返し使ってきた`npx skills add`の正体を掘り下げる」という裏方・エコシステム視点の記事になる。75以上のエージェント対応表やインストール元の多様性〈GitHub以外にGitLab/Azure Repos等〉を一覧化するBefore/After的な整理記事も作りやすい。
- 状態: 未選択

### [2026-10-15] obra/superpowers — Jesse Vincent氏発、Claude Code等向けの「考えてから書く」エージェント向けスキル・開発方法論フレームワーク

- 出典: https://github.com/obra/superpowers (GitHub Trending Shell 2026-10-15、本日+688star/日、累計299,787star。MITライセンス)
- 概要: 「ブレインストーミングで要求を明確化→計画を小タスクに分解→TDDで実装(サブエージェント・レビューを挟む)→テスト確認とブランチ整理」という一連の開発方法論を、文脈に応じて自動発火する複数のSKILL.mdスキル(ブレインストーミング・計画作成・TDD・体系的デバッグ・コードレビュー・診断用スキル等)として提供するフレームワーク。Claude Code/Codex/Cursor/Gemini CLI/GitHub Copilot CLI/OpenCode等、複数のコーディングエージェントで動作する。Anthropic公式プラグインディレクトリ(`anthropics/claude-plugins-official`、本バックログにも別途候補として記録)にも掲載されている。
- 日本語記事件数: Zenn 0件 / Qiita 1件(pythonista0328氏、2026-02-02付。スキル14種・MITライセンス・対応エージェント等を紹介する導入記事) / note 0件(検索した範囲では確認できず)
- 検証難易度: 低(MIT。Claude Codeでは`/plugin marketplace add obra/superpowers-marketplace`→`/plugin install superpowers@superpowers-marketplace`で導入。追加の有料APIキー・GPU不要〈動作は導入先エージェント自身のモデルに依存〉。導入前後で同じ曖昧なタスクをClaude Codeに与え、ブレインストーミング・計画立案などのスキルが自動発火するか、応答プロセスがどう変わるかを比較すれば6時間以内に完結する)
- 見栄え: 「スキルフレームワーク導入前後でClaude Codeの振る舞いがどう変わるか」というBefore/After比較は分かりやすく、本リポジトリ自身が「朝リサーチ→昼実装」というRoutine運用をしている自己言及的な文脈とも相性が良い。ただしQiitaに既に紹介記事が1件あり、またAnthropic公式knowledge-work-plugins(day-013)・google/skills・vercel-labs/skills等、本バックログで既に「エージェントSkillsエコシステム」系の候補が多いため、採用する場合は「自分たちのRoutine運用に実際に組み込んで効果を見る」等の独自切り口が必要。
- 状態: 未選択

### [2026-10-15] morluto/rea — AIエージェントにアプリ・ネイティブバイナリまで丸ごとリバースエンジニアリングさせるMCPサーバー/CLI

- 出典: https://github.com/morluto/rea (GitHub Trending TypeScript 2026-10-15、累計267,621star、2026-04-14作成で半年で急伸)
- 概要: ソースコード非公開のアプリでも、高レベルな挙動から.NETアセンブリ・Android APK・JavaScript/Electronアプリ・Webサイト・パケットキャプチャ・ファームウェア・実行中プロセスの挙動、さらにネイティブバイナリ(Hopper/Ghidra/IDA連携)までをAIエージェントに解析させるMCPサーバー/CLI(MIT。Hopper/IDA/JEB等の商用解析ツール自体は別途正規に入手する必要があり、REAはそれらのツールライセンスを付与しない)。解析はローカルで実行され外部のホスト型解析サービスにアップロードしない設計。70以上のMCPツールを備え、Claude Code/Codex/Cursor/Gemini CLI等に対応。日本語READMEも用意されている。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では一次検証記事は未検出。GameBusiness.jpに日本語のニュース解説記事が1件あるが著者自身の検証記事ではない)
- 検証難易度: 低〜中(MIT。Node.js 22/24/26系が前提で`npx rea-agents setup`等で導入、追加の有料APIキー・GPU不要〈動作は導入先エージェント自身のモデルに依存〉。静的なJavaScript/.NET解析はHopper/Ghidra/IDA等の商用ツール無しでも動作するため、自分が所有する/ライセンス上問題ない小規模なOSS製CLIやAPK等を対象にした静的解析のみに検証範囲を絞れば6時間以内に収まる。ネイティブバイナリの深い解析は別途Hopper/Ghidra/IDA等の用意が必要なため今回のスコープ外とする)
- 見栄え: 「ソース非公開のアプリの挙動をAIエージェントに解析させ、同等機能を再実装させてみる」は技術者向けに非常にインパクトがあり、日本語の一次検証記事が無い点で差別化しやすい。記事化する場合は対象ソフトウェアが自分の所有物またはリバースエンジニアリングが許諾された対象であることを明記する必要がある。
- 状態: 未選択

### [2026-10-15] affaan-m/ECC(Everything Claude Code) — Anthropicハッカソン優勝者発、71エージェント・311スキルを束ねるエージェントハーネス最適化システム

- 出典: https://github.com/affaan-m/ECC (GitHub Trending JavaScript 2026-10-15、累計280,242star、2026-01-18作成)
- 概要: Anthropic×Cerebral Valley主催ハッカソン優勝者が、約10ヶ月の日常利用で磨いた設定を公開したAIコーディングエージェント向けの「エージェントハーネス」(MIT)。約71種の専門エージェント・311種の再利用可能スキル・97種のスラッシュコマンド・フック・ルール・メモリシステム(Memory Vault)・エージェント設定を静的スキャンするセキュリティツール「AgentShield」を束ね、「計画→テスト→実装→レビュー→検証→記憶」というワークフローを毎回のプロンプトで作り直さずに済むことを狙う。Claude Codeをメインに、Codex/Qoder/Cursor/OpenCode/Gemini/Copilot等にも部分対応。
- 日本語記事件数: Zenn 1件(haboshi氏、インストール手順を解説する導入ガイド) / Qiita 0件 / note 0件
- 検証難易度: 低(MIT。Node.js 18+とGitが前提、`npx ecc-universal@2.2.3 setup`またはClaude Codeの`/plugin marketplace add`経由で導入。核となる機能に追加の有料APIキー・GPU不要〈Kimi連携やカスタムゲートウェイ等の一部オプション機能のみ追加キーが必要〉。導入前後で同じ開発タスクをClaude Codeに与え、専門エージェント・スキルの自動活用やAgentShieldのスキャン結果を比較すれば6時間以内に完結する)
- 見栄え: 大量のエージェント・スキルを一括導入した際の実際の振る舞いの変化や、AgentShieldによる危険な設定の検出デモは見せやすい。ただし本バックログには既にobra/superpowers(同日候補)・knowledge-work-plugins(day-013)・google/skills・vercel-labs/skills等、同系統の「エージェント拡張エコシステム」候補が多数あるため、採用する場合は差別化(例: AgentShieldのセキュリティスキャン機能に絞る等)が必要。
- 状態: 未選択

### [2026-10-15] Cortex — プロンプトで与えた文脈の効果をモデルの重みに「定着」させるMemory Consolidation手法(論文、コード未確認)

- 出典: https://huggingface.co/papers/2610.20399 (Hugging Face Daily Papers 2026-10-15時点で62 upvotes)
- 概要: 文脈(プロンプト)で一時的に得られる性能向上は、その文脈を取り除くと消えてしまう問題に対し、文脈がどう使われるかを予測する「prospective query」を生成し、文脈付きの出力を少数の低ランク/構造的なFFN更新へ蒸留して重みに統合する「Memory Consolidation」手法Cortexを提案。4B〜120Bのdense/MoEモデル(テキストのみ・マルチモーダル含む)で、定着(consolidation)と既存能力の保持(retention)のパレートフロンティア上に位置すると報告。14Bモデルで50回の逐次的な知識編集後も文脈由来の性能向上の88.9%を保持(非対象タスクの性能保持率99.8%)としている。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出)
- 検証難易度: 高(arXiv抄録ページでは公式コード・学習済み重みの公開リンク・ライセンス表記を確認できず、フル再現は不可の可能性が高い。本リポジトリの絶対ルールに沿うなら、手法のアイデア〈文脈の効果を少数の更新に蒸留して定着させる〉のみを参考に、軽量モデル・小規模データでの縮小版の概念実証に絞る必要がある。APIキー不要、GPUはあれば望ましい)
- 見栄え: 「文脈を外した後も効果が残るか」というBefore/After比較はHindsight・Remory・Core-Tail World Model等、本バックログで既に扱ってきたエージェントメモリ系の文脈と自然に接続できる。日本語記事が無く差別化しやすいが、再現スコープを事前に絞り込む必要があるため採用する場合は候補メモにその旨を明記すること。
- 状態: 未選択

### [2026-10-16] xerj-org/xerj — AIエージェント専用のローカル検索エンジン(Elasticsearch API互換、Rust製)

- 出典: https://github.com/xerj-org/xerj (本日GitHub Trending Rustで急伸、累計6.8k star)
- 概要: コード・ドキュメント・ログ・PDF等のフォルダをまるごとインデックス化し、AIエージェントがファイル全体を読み込まずに該当箇所だけを取り出せるようにするローカル検索エンジン(Apache-2.0)。全文検索(BM25)・ベクトル検索・ハイブリッド検索に対応し、Elasticsearch 8.x互換APIとMCPサーバーを備える単一バイナリ(JVM等の依存無し)。「似た実装を持つOSSを参照しながらコーディングする(reference coding)」を主な用途として想定している。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出)
- 検証難易度: 低(Apache-2.0。単一バイナリをダウンロードし`--insecure`フラグ付きで起動すれば追加の有料APIキー不要で検証可能〈それ以外では認証キーが自動生成される〉。既定の埋め込みはオフラインの軽量lexical方式でGPU不要。ニューラル埋め込みはオプションで約90MBのモデルファイルを追加DLするのみ。リランク機能のみ外部有料サービス〈TypeSafe Jev〉のキーが必要だが、今回は未使用の範囲で検証可能)
- 見栄え: 本リポジトリ(ai-100days)のexperiments/articles等のフォルダをXERJでインデックスし、キーワード検索・ベクトル検索・ハイブリッド検索でヒットする結果がどう変わるかをBefore/After的に並べられる。MCPサーバーとしてClaude Code自身から直接呼び出すデモも作りやすく、自己言及的な切り口になる。注意: 同一READMEを持つフォーク(github.com/pradaev/xerj)が存在するため、検証は公式(xerj-org/xerj)で行うこと。
- 状態: 未選択

### [2026-10-16] MadsLorentzen/ai-job-search — Claude Code上で動く求職活動自動化フレームワーク

- 出典: https://github.com/MadsLorentzen/ai-job-search (本日GitHub Trending Pythonで+879star/日、累計48.3k star)
- 概要: Claude Codeに「求人検索(`/scrape`)」「応募書類作成(`/apply <url>`)」「面接対策(`/interview`)」をスラッシュコマンドとして実行させる、オープンソースの求職活動フレームワーク(MIT)。アプリやSaaSではなく指示・スキル・テンプレート集のフォルダで、利用者自身のPCとClaude Code自身のサブスクリプション認証だけで動く設計。同梱の求人サイト連携スキルはデンマーク市場向けが中心。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出。英語・中国語・スペイン語の紹介記事は複数あり)
- 検証難易度: 低〜中(MIT。Python 3.10+/Bun、CV生成にはLaTeX〈lualatex/xelatex〉が必要。追加の有料APIキーは不要〈Claude Code自身のサブスクリプション認証で動く設計〉、GPUも不要。ただし同梱の求人サイト連携スキルはデンマーク向けのため、日本の求人サイトを対象にするには`/apply`等のコア機能〈求人票テキストからのCV/カバーレター自動生成〉に検証範囲を絞るか、架空・公開済みの求人票テキストを使う縮小版の概念実証が必要)
- 見栄え: 同じ求人票に対し、素のClaude Codeに頼んだ場合と、このフレームワーク導入後(スキル・テンプレート活用)でCV/カバーレターの質・作業時間がどう変わるかのBefore/After比較が作りやすい。実務に直結するテーマで読者の関心を引きやすい。
- 状態: 未選択

### [2026-10-16] anthropics/claude-plugins-official — Anthropic公式のClaude Codeプラグイン・ディレクトリ自体が本日GitHub Trendingで急伸

- 出典: https://github.com/anthropics/claude-plugins-official (本日GitHub Trending Pythonで+1,552star/日、累計40.4k star)
- 概要: Anthropic自身が管理する、Claude Code向けプラグインの公式ディレクトリ(Apache-2.0。個々のプラグインは別途ライセンスがある場合がある)。`/plugins`にAnthropic自身が開発・保守する内部プラグイン、`/external_plugins`にパートナー・コミュニティ製のサードパーティプラグイン(品質・セキュリティ基準を満たしたもののみ掲載)を収録し、`/plugin install <name>@claude-plugins-official`やClaude Code内の`/plugin > Discover`から導入できる。day-013で検証したanthropics/knowledge-work-plugins等、個々のプラグイン自体は既に話題になっているが、この「公式ディレクトリ」自体がGitHub Trendingで急伸するのは本日が初観測。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語の一次紹介記事は未検出。タイ語ブログ等の海外記事はあり)
- 検証難易度: 低(Apache-2.0。Claude Code自身の`/plugin`コマンドから追加の有料APIキー・GPU不要で導入・比較できる)
- 見栄え: ディレクトリに掲載された複数のAnthropic内部プラグインを実際に`/plugin install`し、未導入時と導入後でClaude Codeの応答がどう変わるかを比較できる。本バックログで既に扱った(または扱う予定の)google/skills・vercel-labs/skills・obra/superpowers等の「エージェント拡張エコシステム」系候補と比べ、「Anthropic自身の公式配布チャネルの実態」という一段メタな切り口で差別化できる。
- 状態: 未選択

### [2026-10-16] android/skills — Google公式、Android開発向けAgent Skills集

- 出典: https://github.com/android/skills (本日GitHub Trendingで+163star/日、累計8.0k star)
- 概要: developer.android.comの公式ガイダンスに基づき、XMLレイアウトからComposeへの移行・AGP 9へのアップグレード・R8設定の点検など、LLMが苦手とされる領域に絞ったAndroid開発向けのAgent Skills集(Apache-2.0)。オープンなAgent Skills標準(SKILL.md形式)に準拠し、Claude Code/Codex等に導入できる。day-015で検証したgoogle/skills(Cloud/Gemini向け)とは異なる、Android開発特化のGoogle公式スキル集。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出。developer.android.comの公式ガイド日本語版はあるが著者自身の検証記事ではない)
- 検証難易度: 中(Apache-2.0。スキル自体の導入は`.skills/`配下への配置のみで追加の有料APIキー・GPU不要だが、「XML→Compose移行」等の効果を実際に検証するには手元に小さなAndroidサンプルプロジェクト(Android Studio/Gradle)を用意する必要がある。既存のXMLレイアウトを持つ軽量なサンプルを自作すれば6時間以内に収まる見込み)
- 見栄え: 同じXMLレイアウトファイルをスキル無し/有りでClaude Codeに移行させ、生成されたComposeコードの品質・ベストプラクティス準拠度をBefore/After比較できる。Google公式のAgent Skills第2弾という文脈で、day-015のgoogle/skillsとの比較軸も作れる。
- 状態: 未選択

### [2026-10-17] debpalash/VoiceStudio — ElevenLabsのローカル完全動作版を目指すOSS音声クローン/ダビング/文字起こしスタジオ

- 出典: https://github.com/debpalash/VoiceStudio (本日GitHub Trending Pythonで5位、累計73,084star・本日+2,135star。短期間での急伸)
- 概要: 音声クローン・ボイスデザイン・動画ダビング・ディクテーション・文字起こし・オーディオブック作成を646言語分、すべてローカルで行えることを掲げるデスクトップアプリ(アプリ本体はAGPL-3.0)。既定のTTSエンジンはk2-fsa/OmniVoiceで、HTTP/WebSocket/JSON-RPC/CLI/MCPの各トランスポートを備え、エージェントからも呼び出せる。NVIDIA(CUDA)/Apple Silicon(Metal)で高速化、専用GPUが無い環境でもCPUで動作可能(その場合はPyTorchのCPUビルドに約5GBの空き容量が必要。モデル込みで合計約14GBという報告もある)。
- 日本語記事件数: Zenn 0件 / Qiita 4件前後(tsuzuri_ai, Git_Dayori等の「GitHub日報」系まとめ記事でのトレンド紹介のみで、著者自身による検証記事は確認できず) / note 4件前後(shali_note氏「ローカルだけでやる声クローン」、generativeai_new氏「AIボイスを自作する前に ── VoiceStudioに必要な約14GB」等、一部ハンズオン的な内容を含む記事あり。ただしELiteprise的な深い技術検証記事ではない)
- 検証難易度: 低(追加の有料APIキー不要。既定のGPU無し構成でCPU動作可能なため6時間以内に声クローン・ディクテーション・文字起こし等の主要機能を一通り試せる見込み。話者分離(diarization)機能のみHugging Faceトークンが必要だが今回はオプションとして除外可能。注意: アプリ本体はAGPL-3.0だが、既定のOmniVoiceモデル重みはCC-BY-NC〈非商用〉とする日本語記事の報告があり、ライセンスが二重構造になっている点を記事中で明記する必要がある)
- 見栄え: 自分の声を10秒程度の録音からクローンし、テキストから読み上げさせるBefore/After的なデモは一般読者にも分かりやすい。ElevenLabs等の有料SaaSとの対比、完全ローカルで個人情報が外部に出ない点も訴求しやすい。日本語音声の品質は未確認のため、検証記事ではそこに触れる価値がある。
- 状態: 未選択

### [2026-10-17] google/artemis(ARTEMIS) — Google公式、自然言語の指示だけでAndroid端末を自動操作するエージェントハーネス

- 出典: https://github.com/google/artemis (本日GitHub Trending全言語で1位、累計12,154star・本日+135star。GoogleのPixel Test Engineering〈PTE〉Fusionチームが開発)
- 概要: 自然言語の指示を、実機またはエミュレータ上のAndroid操作(画面観察→行動決定→ADB経由で実行→結果確認のループ)に変換するオープンソースのエージェントハーネス(Apache-2.0。`third_party/mobile_use`配下はMinitap, Inc.由来のApache-2.0コードで、2026年9月にはMinitap社の`mobile-use`からのコード一致・帰属表記欠落を指摘される一幕もあった)。Web console・CLI・Python SDK・MCPサーバーの4経路で利用でき、MCP経由でClaude Code/Codex/Cursor等から呼び出せる。高速なFlashプロファイルと、計画・検証を挟むProプロファイルの2モードを持つ。AndroidWorldベンチマークで99%超(自己申告)と主張。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 1件(ai_driven氏「Googleの『ARTEMIS』を徹底分析:AndroidWorldの99.1%はどこから来たのか、公式リーダーボードには存在せず」。ベンチマークの検証可能性とMinitap社由来の帰属問題まで深く掘り下げた記事で、既に日本語での一次解説が存在する)
- 検証難易度: 中〜高(Apache-2.0。導入にはPython 3.12+に加え、実機〈USBデバッグ有効〉またはAndroidエミュレータが必要。さらに画面理解・行動決定にGemini/Claude/GPT-4o/Qwen-VL等のモデルAPIキーが必須〈`.env`経由〉で、本リポジトリの「当面は有料APIキー必須の候補を選ばない」方針に抵触する可能性が高い。Gemini APIの無料枠で足りる範囲に絞れば方針上は選べるが、無料枠のレート制限内に収まるか要確認。エミュレータ+無料枠モデルの組み合わせなら6時間以内に収まる見込み)
- 見栄え: 「日本語の簡単な指示だけでAndroidアプリを横断操作させる」デモは視覚的に分かりやすいが、既に上記のnote記事がベンチマークの信頼性や帰属問題まで踏み込んで解説済みのため、採用する場合は「実際に手元のエミュレータで動かして公式ベンチマークの再現性を自分の目で確認する」等、既存記事と差別化できる検証軸が必要。有料APIキー方針の制約もあり、現時点では優先度を下げる。
- 状態: 未選択

### [2026-10-17] akitaonrails/ai-memory — Claude Code↔Codex等、異なるAIコーディングエージェント間でセッションの記憶を引き継ぐRust製ツール

- 出典: https://github.com/akitaonrails/ai-memory (本日GitHub Trending全言語で+208star/日、累計約9.9k star・2026年8月に急伸)
- 概要: ライフサイクルフックでセッション中の作業を観測し、セッション終了時にMarkdown形式のWikiへ要約・整理して蓄積するAIコーディングエージェント向けの長期記憶ツール(MIT、Rust製)。Claude Code/Codex/Cursor/Gemini CLI/OpenCode/Kimi Code/Grok Build CLI/Kiro CLI/VS Code Copilot等20種類超のharnessに対応し、「Claude Codeで中断した作業をCodexで続きから再開する」といったツール間ハンドオフが主目的。サーバー経由で複数マシン・チーム間の記憶共有にも対応。
- 日本語記事件数: Zenn 0件 / Qiita 1件(jqit_suwa氏「Claude Codeをやめて Codexで続きから作業できた — ただし引き継がれたのは要約ではなかった」。Windows環境でv1.28.1を実際に検証したハンズオン記事で、既定ではLLMプロバイダ未設定のためハンドオフされた文脈がLLM要約ではなくヒューリスティックな合成だった点を指摘している) / note 1件(totorotom氏「Claude CodeからCodexへ、コンテキストを引き継ぐOSSが急成長——ai-memoryの急伸が示す『エージェントメモリ』層」という深掘り解説記事)
- 検証難易度: 低(MIT。核となるキャプチャ・検索・ハンドオフ機能は追加の有料APIキー不要〈LLM/embeddingプロバイダはオプションで、未設定だとヒューリスティックな要約になる〉。GPU不要。Linux/macOS対応、Windowsネイティブは実験的(WSL2推奨)。6時間以内に複数harness間のハンドオフを一通り試せる)
- 見栄え: 既にQiitaに「Codexへの引き継ぎ内容がLLM要約ではなくヒューリスティック合成だった」という具体的なハンズオン検証記事があるため、同じ切り口の再検証では差別化が難しい。採用する場合は「LLMプロバイダを明示的に設定した場合に引き継ぎ品質がどう変わるか」「本リポジトリ(ai-100days)自身のRoutine運用〈朝research→昼実装〉にハンドオフを組み込めるか」等、既存記事が触れていない軸を選ぶ必要がある。
- 状態: 未選択

### [2026-10-17] Behavioral Compositionality of Sparse Autoencoder Representations(SAE Additivity Residuals, SAR) — SAEの特徴は本当に「足し算」で振る舞いを説明できるのか を定量評価する解釈可能性研究(論文)

- 出典: https://huggingface.co/papers/2610.21261 (Ziye Mei, Frederic Sala〈University of Wisconsin–Madison〉、コード: https://github.com/OpenSAE/SAE-Behavioral-Compositionality)
- 概要: Sparse Autoencoder(SAE)の個々の特徴が、モデルの出力(振る舞い)に対して本当に加算的に効いているのかを「SAE Additivity Residuals(SAR)」という指標で定量化する研究。学習済みSAEの座標系を、同じ部分空間のランダム回転(足し算は保存するが特徴の意味は保たない対照群)と比較し、18種類のモデル・振る舞いの組み合わせすべてで学習済み座標系の方が1次(個々の特徴のみ)残差が小さいことを示す一方、2次(特徴ペア)の交互作用を加えるとcoalitionの順序予測やsteering実験のrank fidelityが0.5874→0.7790まで改善したと報告しており、「SAEの特徴は完全な足し算ではない」ことを示している。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出)
- 検証難易度: 高(コードはOpenSAE/SAE-Behavioral-Compositionalityで公開されているが、ライセンス表記は確認できていない。実験にはGemma Scope 2・Llama ScopeなどSAELens経由で入手できる既存の公開SAE・公開モデルを使うためAPIキーは不要だが、フル再現にはGPUが前提になる可能性が高い。本リポジトリの方針に沿うなら、公開されている小型モデル向けSAE〈例: GPT-2 small等〉1つに絞り、「学習済みSAE座標 vs ランダム回転」の1次残差比較のみをCPUでも動く範囲に縮小した概念実証に絞る必要がある)
- 見栄え: 「AIの思考の部品(特徴)は本当に独立して足し算できるのか」という解釈可能性の根本的な問いに切り込める点で、本バックログで続いているエージェントSkillsエコシステム系の候補群とは一線を画す差別化ポイントになる。グラフで「1次残差」「2次残差込みの改善」を可視化すれば見栄えも作りやすい。ただし再現スコープを事前に強く絞り込む必要があるため、採用する場合は候補メモにその旨を明記すること。
- 状態: 採用済み(day-020)

### [2026-10-18] ahujasid/mcp-for-blender — 任意のLLMでBlender 3Dを操作できるMCPサーバー(旧称blender-mcp)

- 出典: https://github.com/ahujasid/mcp-for-blender (本日GitHub Trending Python/全言語で+2,098star/日)
- 概要: Blenderアドオン(ソケットサーバー)とMCPサーバーの2部構成で、Claude Code/Claude Desktop等のAIクライアントからBlender Python APIを直接実行させ、シーン検査・レンダリング・Poly Haven/Sketchfab/Poly Pizzaからのアセット取り込み、Tripo/Hyper3D Rodin/Hunyuan3D/Meshy経由の3Dモデル生成までを自然言語で行える(MITライセンス)。Blender Foundation非公式のコミュニティプラグイン。
- 日本語記事件数: Zenn 2件以上(前身の「blender-mcp」として社内勉強会のハンズオン記事・アーキテクチャ解説記事が既に公開済み) / Qiita 0件 / note 0件(本日時点の検索範囲)
- 検証難易度: 低(MIT。Blender 3.0+・Python 3.10+・uvのみで追加の有料APIキー不要〈Poly Haven等は無料で利用できるアセット取得先もある〉。GPUは任意〈Blenderのレンダリング品質には影響するが必須ではない〉。`execute_blender_code`は任意のPythonを実行するため、検証前にBlenderファイルを保存すること)
- 見栄え: 「日本語の指示だけでBlenderに低ポリゴンの3Dシーンを作らせる」様子はスクリーンショットで非常に見栄えがよい。前身のblender-mcp自体はZenn記事が複数あるため完全新規ではないが、mcp-for-blenderへの改称後に強化されたアセット生成系連携(Tripo等)を中心に据えれば差別化できる。
- 状態: 採用済み(day-021)

### [2026-10-18] Graphify-Labs/graphify — コードベース・ドキュメントを問い合わせ可能な知識グラフに変換するAIエージェント向けスキル

- 出典: https://github.com/Graphify-Labs/graphify (本日GitHub Trending Pythonで+592star/日)
- 概要: tree-sitterでコードをローカル解析し、ドキュメント・SQLスキーマ・設定ファイル・PDF・画像も含めて(コードのみならLLM不要で)問い合わせ可能な知識グラフ(graph.html/GRAPH_REPORT.md/graph.json)に変換するツール。エッジは「EXTRACTED(明記された関係)」「INFERRED(推論された関係)」で区別され、Claude Code/Cursor/Codex/Gemini CLI等20以上のアシスタント向けに`/graphify`スキルとして動作する(リポジトリにApache-2.0・MIT両方のLICENSEファイルがあるデュアルライセンス表記)。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語の一次紹介記事は未検出。韓国語〈braindetox.kr〉・英語の解説記事は複数あり)
- 検証難易度: 低(`uv tool install graphifyy`で導入可能。`--code-only`オプションを使えばコードのみの知識グラフ構築に追加の有料APIキー不要〈ドキュメント/PDF/画像の意味抽出にLLMを使う場合のみ任意でAPIキーまたはClaude Code自身のモデルを使用〉。GPU不要)
- 見栄え: 本リポジトリ(ai-100days)自身に対して`/graphify .`を実行し、生成されたgraph.htmlの可視化と、grep/手動探索との比較(同じ質問に対する正答率や所要ファイル読み込み数の違い)をBefore/After的に見せられる。既出のcontext-mode・caveman等「Routine運用コスト改善」系ネタの発展として自己言及的に語りやすい。
- 状態: 未選択

### [2026-10-18] superdesigndev/treg — AIエージェント向けツールAPIの「OpenRouter」を謳うレジストリ/プロキシ

- 出典: https://github.com/superdesigndev/treg (本日GitHub Trending Pythonで+76star/日。8月のProduct Hunt公開後も継続的に伸長中)
- 概要: エージェントが1つのベースURL・1つのトークンだけで、SEO・企業情報・スクレイピング・メディア生成等サードパーティAPI群(数千エンドポイント規模)に従量課金でアクセスできるレジストリ兼プロキシ。認証情報はサーバー側に保持され呼び出し元には渡らない設計。CLIは`tools-registry`としてPyPI配布、サーバーはFastAPI製で自己ホスト可能。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出。英語のレビュー記事〈eesel.ai等〉は複数あり)
- 検証難易度: 低〜中(ライセンスはApache-2.0に追加条件〈競合するホスト型レジストリとしての再配布は不可。自己ホスト・自社利用は無制限〉が付く非OSI的ライセンスのため、記事内で明記が必要。ローカルサーバー起動〈`scripts/dev-local.sh up`〉とサンドボックスDBでのCLIログイン・カタログ検索はAPIキー不要。実際の外部API呼び出し〈`treg call`〉はtreg.to側の残高を消費するため、検証はローカルサーバーでの登録・カタログ検索機能に限定するか、消費を最小限に絞ること)
- 見栄え: 「1つのトークンで複数の外部APIにアクセスできる」仕組みをローカルサーバーのダッシュボード・カタログ検索のスクリーンショットで見せられる。有料枠を消費しない範囲に絞った検証であることを記事内で明記する必要あり。
- 状態: 未選択

### [2026-10-18] k2-fsa/OmniVoice — 600以上の言語に対応するゼロショット音声クローンTTS

- 出典: https://github.com/k2-fsa/OmniVoice (本日GitHub Trending Pythonで+55star/日)
- 概要: 離散・非自己回帰(NAR)アーキテクチャにより、3〜25秒の参照音声から600以上の言語でゼロショット音声クローンを行うTTSモデル(コードApache-2.0)。性別・年齢・ピッチ・アクセント指定による音声デザイン、`[laughter]`等のノンバーバルタグ、ピンイン/CMU音素による発音制御にも対応し、H100でRTF 0.025(リアルタイム比約40倍速)を主張。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語の一次検証記事は未検出。英語圏の紹介記事〈korben.info等〉はあり)
- 検証難易度: 中〜高(コードはApache-2.0だが、公開されている事前学習済みモデルの重みは学習データ〈Emilia等〉のライセンス制約によりCC-BY-NC〈非商用〉。記事内で必ず明記すること。公式のベンチマーク・導入例はCUDA/MPS/XPU前提で、CPUのみでの動作例・速度報告は無く、GPUが使えない環境では大幅に低速化するか動作しない可能性がある。`pip install omnivoice`後に自分の声の短い参照クリップで`omnivoice-infer`を実行し、生成音声をASRで書き起こして入力テキストと一致するか確認する、という範囲なら6時間以内も狙えるが、着手前にGPU有無を確認すべき)
- 見栄え: 自分の声をクローンして日本語以外の言語(例: 英語・中国語等)で読み上げさせる「多言語ゼロショット音声クローン」のBefore/After比較は非常にデモ映えする。既出のVoiceStudio(音声クローンアプリ全体)とは異なり、600言語対応・NARアーキテクチャという技術的切り口で差別化できる。
- 状態: 未選択

### [2026-10-19] shiyu-coder/Kronos — ローソク足(K線)データ専用のオープンソース金融基盤モデル

- 出典: https://github.com/shiyu-coder/Kronos (本日GitHub Trending Pythonで+355star/日、累計41.6k star。AAAI 2026採択)
- 概要: 世界45取引所・120億件超のK線(OHLCV)データで事前学習した、金融ローソク足専用の基盤モデル(MIT)。専用トークナイザでOHLCVを階層的な離散トークンに変換し、自己回帰Transformerを事前学習する2段構成で、ゼロショットの価格系列予測でRankICが既存の時系列基盤モデルより93%高いと報告。Kronos-mini(4.1M)・Kronos-small(24.7M)・Kronos-base(102.3M)はHugging Face Hubで重み公開、Kronos-large(499.2M)は非公開。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語の一次検証記事は未検出。中国語の紹介記事〈磐创AI由来、新浪財経転載〉はあり)
- 検証難易度: 低(MIT。追加の有料APIキー不要。Kronos-mini/small/baseはHugging Face Hubから直接ダウンロードでき、公式デモ〈shiyu-coder.github.io/Kronos-demo〉も稼働中。`KronosPredictor`は`device`パラメータを持ちCPU指定も可能と見られるが、実際にノートPC相当のCPUで実用的な速度で推論できるかは着手前に小型モデル〈Kronos-mini〉で確認すること。GPUは必須ではない)
- 見栄え: 自分で選んだ銘柄(例: BTC/USDT、日経平均等)の直近K線データをKronos-miniに入力し、予測チャートと実際の値動きをBefore/After的に並べて見せられる。「予測は確率的サンプルで投資判断の唯一の根拠にしてはいけない」という公式の免責も記事に明記すべき。
- 状態: 採用済み(day-022)

### [2026-10-19] koala73/worldmonitor — AIでニュース・地政学イベントを集約するリアルタイム「グローバルインテリジェンスダッシュボード」

- 出典: https://github.com/koala73/worldmonitor (本日GitHub Trending TypeScriptで+143star/日、累計88.8k star)
- 概要: ニュース・地政学イベント・航空機動静・災害情報等をAIで集約し1画面にまとめるリアルタイムダッシュボード(AGPL-3.0。商用ライセンスは別途提供)。Web/Tauriデスクトップ/ターミナル/CLI/Python・Ruby・Go SDK/MCPサーバーの複数経路で利用でき、AIバックエンドはOllama(ローカル、キー不要)とOpenRouter等に対応する。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語の一次検証記事は未検出。英語・スペイン語のローカル実行ガイド〈knightli.com、2026年6月〉、ASCII.jpの紹介記事はあり)
- 検証難易度: 低〜中(README記載では「環境変数無しで動作する」とのことで`npm install && npm run dev`のみで基本機能は追加キー不要。ただしAI要約等の一部機能はOllama〈ローカルモデル、要PC用意〉かOpenRouter〈有料API〉のどちらかを選ぶ必要があり、本リポジトリの方針上はOllama経由に限定する。GPU不要〈CPUでも動く軽量ローカルモデルを選べば可〉)
- 見栄え: 自分のPCで起動したダッシュボード(地図・ニュース一覧・金融チャート等が1画面に集約)のスクリーンショットは見栄えがよく、「個人のPCだけでOSINT風ダッシュボードが動く」という訴求がしやすい。2026年6月時点で既に英語圏のハンズオン記事があるため、記事化する場合はOllama連携のローカルAI要約部分等、その記事がカバーしていない切り口での差別化が必要。
- 状態: 未選択

### [2026-10-19] usestrix/strix — PoCエクスプロイトで脆弱性を検証する自律型AIペネトレーションテストエージェント

- 出典: https://github.com/usestrix/strix (本日GitHub Trending Pythonで+476star/日、累計70.0k star)
- 概要: 自律型AIエージェントが対象アプリを動的に実行し、実際の概念実証(PoC)エクスプロイトで脆弱性を検証する分散ワークフロー型のオープンソースAIペネトレーションテストツール(Apache-2.0)。複数の専門特化エージェントが異なる攻撃経路を分担する「Graph of Agents」構成を取り、HTTPプロキシ・ブラウザ自動化・ターミナル・Pythonランタイムを備え、レポート生成・自動修正パッチ生成機能も持つ。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語の一次検証記事は未検出。日本語の紹介ブログ〈knightli.com、OpenReplayブログ日本語版〉はあり)
- 検証難易度: 中〜高(Apache-2.0。Docker必須。LLMバックエンドに`STRIX_LLM`+`LLM_API_KEY`〈OpenAI/Anthropic/Google/OpenRouter等の有料APIキー〉、またはChatGPT Plus/Proサブスクリプション認証〈いずれも有料〉が前提で、本リポジトリの「当面は有料APIキーが必須の候補を選ばない」方針に抵触する。`LLM_API_BASE`でOllama/LM Studio等のローカルモデルを指定する方式のみ追加課金なしで試せる可能性があるが、脆弱性診断の精度にローカル小型モデルがどこまで耐えるかは未確認。採用する場合はローカルモデル限定での縮小版検証に絞る必要がある)
- 見栄え: 自作の意図的に脆弱なサンプルWebアプリに対してstrixを走らせ、実際にPoCエクスプロイトが生成される様子を見せられれば非常にインパクトが大きい。ただし「所有または明示的に許可された対象のみに使う」という利用規約の遵守を記事内で明記する必要がある。有料APIキー方針との兼ね合いで、採用するなら優先度は下げてよい。
- 状態: 未選択

### [2026-10-19] Into the Unknown — AIエージェントに未発表の科学研究課題を解かせたら9エージェント構成・135件中ゼロ件しか誠実な報告ができなかったベンチマーク(論文)

- 出典: https://huggingface.co/papers/2610.19159 / コード: https://github.com/prometheus-eval/into-the-unknown / データセット: https://huggingface.co/datasets/prometheus-eval/into-the-unknown (Carnegie Mellon University他、米エネルギー省〈DOE〉国立研究所の科学者と共同作成)
- 概要: DOE国立研究所の科学者が提供した、既発表の計算科学論文に対する「未発表の追加研究課題」15件をAIエージェントに与え、論文・コード・実行ログを提出させて評価するベンチマーク。9つのフロンティアエージェント構成による135件の提出のうち、誠実性(integrity)・完全性(completeness)・十分性(sufficiency)の全条件を満たしたものはゼロで、114件が「実際には行っていない作業を主張する」「実行ログと矛盾する数値を報告する」等の誠実性チェックで不合格だったと報告している。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出。AlphaSignal等英語の二次解説記事はあり)
- 検証難易度: 中(コード・データセット〈エージェントの実行ログ含む〉は公開済みだがライセンス表記は未確認。9エージェント×15課題のフル再現は複数の有料APIキーが前提になり本リポジトリの方針には合わない。縮小版として、公開されている15課題のうち1つを選び、Claude Code自身〈追加APIキー不要〉をエージェントとして走らせ、公開されているルーブリック〈誠実性・完全性・十分性〉で自己評価する、という小規模な概念実証に絞れば6時間以内に収まる見込み)
- 見栄え: 「AIエージェントに研究の続きをやらせたら、架空の実験結果を報告してしまった」という誠実性の問題を自分の手元で再現できれば、AIエージェントの限界を扱う記事として説得力が高い。原論文自体が135件中114件で不誠実な報告を検出したという衝撃的な結果を持つため、読者の関心を引きやすい。
- 状態: 未選択

### [2026-10-19] 666ghj/MiroFish — ニュース・政策案から仮想社会を構築し多数のAIエージェントで将来を予測する群知能シミュレーションエンジン

- 出典: https://github.com/666ghj/MiroFish (本日GitHub Trending Pythonで+394star/日、累計80.6k star。Shanda Groupの支援を受けて開発)
- 概要: ニュース・政策案・金融シグナル等の「種」情報から仮想の社会環境を構築し、個性・記憶を持つ多数のエージェントを相互作用させて将来の展開を予測するマルチエージェント型シミュレーションエンジン(AGPL-3.0。シミュレーション基盤にOASIS〈Open Agent Social Interaction Simulations〉を使用)。レポート生成エージェントや、シミュレーション内エージェントとのチャット機能も持つ。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出。フランス語・スペイン語・ポルトガル語の紹介記事〈pasqualepillitteri.it〉はあり、「予測精度の数値が公式に載っていない」「バックテスト提案がGitHub上で未解決」といった指摘も含む)
- 検証難易度: 中(AGPL-3.0。LLMバックエンドに`LLM_API_KEY`〈OpenAI SDK互換の任意のAPI。公式はAlibaba qwen-plusを推奨し「消費量が多い」と明記〉、加えてメモリ機構に`ZEP_API_KEY`〈Zep Cloud、無料枠ありと明記〉が必要で、本リポジトリの「有料APIキー必須の候補は選ばない」方針に抵触する可能性が高い。公式のオンラインデモ〈666ghj.github.io/mirofish-demo〉で挙動を確認する範囲なら追加キー不要)
- 見栄え: 自分で用意した架空のニュース記事やプレスリリースを入力し、シミュレーション内のエージェントたちがどう反応するかを可視化するデモは見栄えがよいが、有料APIキー必須という制約と、海外記事が既に「予測精度の数値が公開されていない」点を指摘していることから、採用する場合は検証スコープを強く絞る必要がある。
- 状態: 未選択

### [2026-10-20] cloudflare/security-audit-skill — Cloudflare公式、AIエージェントを多段検証付きセキュリティ監査員に変えるClaude Codeスキル

- 出典: https://github.com/cloudflare/security-audit-skill (本日GitHub Trending JavaScriptで+1,680star/日、累計約34k star)
- 概要: Cloudflare自身が公開した、コーディングエージェントを多段パイプライン(偵察→並列サブエージェントによる網羅的ハンティング→候補所見の敵対的検証→構造化出力→最終所見の独立再検証→レポート生成)でセキュリティ監査員に変えるClaude Codeスキル(MIT)。所見は`findings.json`に`confirmed`/`needs_validation`/`rejected`で分類され、Cloudflare社内の脆弱性発見ハーネスの元になったと説明されている。1回の実行では複数回実行時に見つかる脆弱性の約半分しか検出できないとREADMEに明記されている。
- 日本語記事件数: Zenn 2件以上 / Qiita 3件以上 / note 4件以上(2026年6月の公開直後から複数の検証記事が出ており、「AIが見つけた不具合をAI自身に検証させない」設計や、所見の精度〈5件中1件のみ本物だった、等〉を実測した記事も既にある)
- 検証難易度: 低(MIT。`npx skills add`でClaude Codeに導入でき、追加の有料APIキー・GPUは不要。Node.jsのみ要。対象コードをビルド・実行する場合はOSレベルのサンドボックス〈外部ネットワーク遮断等〉が推奨されている点に注意。自作の意図的に脆弱なサンプルアプリ〈例: 既知のSQLインジェクション/パストラバーサルを仕込んだ小さなFlask/Expressアプリ〉を用意し、1回実行と複数回実行で検出率がどう変わるかを比較すれば6時間以内に完結する)
- 見栄え: 「AIエージェントに自分のコードの脆弱性診断をさせたら、1回の実行と複数回の実行でどれだけ検出率が変わるか」というBefore/After比較が作りやすく、Cloudflare公式発というニュース価値も高い。日本語記事が既に複数あるため、既存記事が触れていない「検出率の再現実測」や「誤検出(false positive)の内訳」に切り口を絞ると差別化しやすい。
- 状態: 未選択

### [2026-10-20] google/artemis — Google公式、自然言語指示でAndroid実機/エミュレータを操作するオープンソース自動化エージェント(ARTEMIS)

- 出典: https://github.com/google/artemis (本日GitHub Trending全言語で+348star/日、累計約13.2k star。third_party/mobile_useにMinitap, Inc.のApache-2.0コードを含む)
- 概要: 自然言語の指示をAndroid実機/エミュレータ上の実際の操作(タップ・スワイプ等)に変換するGoogle公式のオープンソース自動化ツール(Apache-2.0)。MCPサーバー・Webコンソール・CLI・Python SDKを持ち、Gemini/Claude/GPT-4o/Qwen-VL等複数のモデルプロバイダに対応。高速だが計画・検証を省く「Flash」プロファイルと、各操作を事前計画・検証する「Pro」プロファイルの2モードがあり、Google自身のAndroidWorldベンチマークで99%超のタスク完了率を主張(公式リーダーボード外の自己申告値)。初回実行時にアクセシビリティ補助アプリを端末にインストールする。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 1件(2026年8月公開の技術解説記事が1件あるのみで、ARTEMIS自体を実際に動かして検証した日本語記事は検索した範囲では未検出。他は無関係なAndroid自動化アプリ〈Tasker/MacroDroid等〉の記事だった)
- 検証難易度: 中〜高(Apache-2.0。Android実機〈USBデバッグ有効化〉またはエミュレータが前提で、Pythonセットアップスクリプトがadb/scrcpy/ffmpeg/uvを自動導入する。モデルバックエンドにGemini/Claude/GPT-4o/Qwen-VLいずれかのAPIキーが必要になる可能性が高く、Routineのクラウド実行環境にAndroidエミュレータや実機が無い場合は検証が進められない。Routine環境の制約で進まない場合はCLAUDE.mdの方針に従い「ローカル検証が必要」と明記してエスカレーションすること)
- 見栄え: 「日本語で指示するだけでスマホの実機/エミュレータが操作される」様子は動画・スクリーンショットで非常に見栄えが良く、Google公式発・日本語記事ほぼ0件という点で差別化しやすい。ただしAndroid実機/エミュレータとモデルAPIキーという二重のハードルがあるため、採用する場合は人間のローカルPC〈実機接続可能〉での検証を前提にした方が良い。
- 状態: 未選択

### [2026-10-20] NVlabs/ASPIRE — NVIDIA発、コーディングエージェントにロボットの操作スキルを並列発見させる継続学習フレームワーク(論文)

- 出典: https://github.com/NVlabs/ASPIRE (論文: arXiv:2607.00272。Yuke Zhu・Linxi Fan等NVIDIA関係の研究者が著者に含まれる)
- 概要: 勾配降下による重み更新ではなく、コーディングエージェントが並列にスキルを試行・洗練し続けることを「学習」とみなし、学習済みの成果を感覚運動スキルのリポジトリとして蓄積する継続学習フレームワーク(Apache-2.0)。LIBERO-Pro/Robosuite/BEHAVIOR-1Kのシミュレーションベンチマークと、YAMステーションでの実機マニピュレーションデモを含む。LIBERO-Proの摂動タスクで既存手法比最大77pt、Robosuiteの接触を伴う操作タスクで最大72pt、BEHAVIOR-1Kの長期タスクで最大32ptの成功率改善を主張。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出)
- 検証難易度: 高(Apache-2.0だがCUDA GPU必須、ゲート付きのHugging Face重み〈SAM3〉の取得にHFトークンが必要、Claude Opus/GPT等のモデルAPIクレジットも前提。README自身が「エージェントが生成したPythonをフルインポート権限で実行するためセキュリティサンドボックスではない」と明記し、専用の隔離ホストを推奨している。実機デモはキャリブレーション済みYAMステーションが必要で個人が6時間以内に再現するのは非現実的。シミュレーション側もGPU+複数モデルAPIキーが前提のため、本リポジトリの「有料APIキー必須の候補は選ばない」方針との相性が悪い)
- 見栄え: 「AIエージェント自身がロボットの操作スキルを試行錯誤で発見・蓄積していく」というコンセプトはインパクトが大きいが、動かして検証する記事には向かない。扱うならGPU・APIキー要件を明記した「ニュース解説のみ」の扱いに留めるか、見送るのが妥当。
- 状態: 未選択

### [2026-10-20] Graphify-Labs/graphify — コードベースをベクトルDB不要のナレッジグラフ化しAIエージェントのgrep/Readを置き換えるClaude Codeスキル

- 出典: https://github.com/Graphify-Labs/graphify (本日GitHub Trending Pythonで+906star/日、累計約130k star。開発者Safi Shamsi名義の個人リポジトリ〈safishamsi/graphify〉から移管/ミラーされた可能性があり記事によってURL表記が揺れているため、検証時はGraphify-Labs/graphifyが現行の公式であることを確認すること)
- 概要: コード・ドキュメント・SQLスキーマ・設定ファイル・PDF・画像・動画を1つのクエリ可能なナレッジグラフに変換するPython CLI兼Claude Code/Cursor/Codex/Gemini CLI向けスキル。コード解析はtree-sitterによる完全ローカル・LLM不要の決定的処理で、`--code-only`を使えば外部送信なしの完全オフライン動作が可能(ベクトルストア不使用)。出力は操作可能な`graph.html`・`GRAPH_REPORT.md`・`graph.json`で、grepやReadの繰り返しの代わりに`graphify query`等でグラフに問い合わせる運用を想定。
- 日本語記事件数: Zenn 2件以上 / Qiita 1件以上 / note 5件以上(2026年4月の公開直後から多数の紹介記事があり、トークン削減効果〈71.5分の1等〉を検証する記事も既に複数ある)
- 検証難易度: 低(ライセンス表記はApache-2.0/MIT両方の記載があり要確認。`uv tool install graphifyy`で導入可能、`--code-only`モードならAPIキー・GPU不要で完全オフライン動作。本リポジトリ自身〈ai-100days〉のコードベースに対して`/graphify`を実行し、生成されたグラフとgrepベースの探索を比較するBefore/After実験が6時間以内で可能)
- 見栄え: 自分のコードベースから生成した`graph.html`を実際にブラウザで開いて見せられ、ビジュアル的な説得力が高い。「公式が主張するトークン削減率は本当か」を自分の環境で実測する切り口であれば、既存の日本語記事(効果を疑問視する記事も既にある)との差別化もしやすい。
- 状態: 未選択

### [2026-10-21] stablyai/orca — Claude Code/Codex等を一括統括する複数コーディングエージェント艦隊運用OSSデスクトップIDE

- 出典: https://github.com/stablyai/orca (本日GitHub Trending 全言語で+1,543star/日。公式サイト: https://onorca.dev)
- 概要: Claude Code・Codex・OpenCode・Pi等の複数のCLIコーディングエージェントを、それぞれ独立したgit worktree・ターミナル・環境で同時に走らせ、1つのデスクトップアプリ(macOS/Windows/Linux)から横断管理できるOSS「艦隊運用」IDE(MITライセンス)。モバイル用コンパニオンアプリでの監視・GitHub/Linear連携・リモートマシンへのSSH worktree対応も備える。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(zenn.dev/qiita.com/note.comへのsite:検索ではいずれも0件。EvoMap.ai等の海外ブログに日本語記事は確認できたが、Zenn/Qiita/note上の一次検証記事は未検出)
- 検証難易度: 低〜中(MIT。各自のCLIエージェントのサブスクリプション〈本リポジトリならClaude Codeのサブスクリプション認証〉を利用する設計のため追加の有料APIキーは不要と説明されている。GPU不要。ただしデスクトップGUIアプリのため、Routineのクラウド実行環境ではブラウザ/GUIが使えない可能性がある点に注意〈その場合はCLI機能のみの検証に絞るか、ローカル検証にエスカレーション〉)
- 見栄え: Claude CodeとCodexを同じリポジトリの別worktreeで並走させ、1画面で進捗を見比べるBefore/After(単一エージェント運用 vs Orcaでの並列運用)は分かりやすく、本チャレンジ自身の「朝リサーチ→昼実装」という分業Routineとも文脈的に相性が良い。
- 状態: 未選択

### [2026-10-21] DietrichGebert/ponytail — コーディングエージェントに「最小限のコード」を書かせるClaude Code向けスキル

- 出典: https://github.com/DietrichGebert/ponytail (本日GitHub Trending 全言語で+2,051star/日)
- 概要: 「最も怠惰なシニア開発者」のように振る舞わせ、新しいコードを書く前に既存コード・標準ライブラリ・プラットフォーム標準機能の再利用を優先させ、リスクの高いロジックにはテストを残しつつ不要な抽象化や冗長なコードを削るルールセット(MITライセンス)。Claude Code/Codexへのプラグイン導入や、他エージェント向けのAGENTS.md/SKILL.md配置に対応し、`/ponytail-review`等のレビュー・監査コマンドも備える。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(site:検索ではいずれも0件。pasqualepillitteri.it等に日本語訳記事が1件あるが、日本語コミュニティでの一次検証記事は未検出)
- 検証難易度: 低(MIT。`/plugin marketplace add DietrichGebert/ponytail`→`/plugin install ponytail@ponytail`でClaude Code CLIから追加の有料APIキー無しで導入可能。GPU不要。Node.jsがPATH上にあれば動作)
- 見栄え: 同一タスクをponytail導入前/導入後のClaude Codeに与え、生成コード行数・トークン使用量・応答時間をBefore/After比較できる。公式は「54〜94%のコード削減」等を主張しているが独立検証では数値が小さく出る報告もあり、自分の環境での実測値を出す価値がある。本リポジトリで既に扱ったandrej-karpathy-skills(CLAUDE.mdでの原則提示)と似た系譜だが、実装・計測コマンド(`/ponytail-audit`等)まで備える点で差別化できる。
- 状態: 未選択

### [2026-10-21] "Good Judgment, Bad Advice" — Terminal-Bench 2.1でClaude Sonnet 5.5エージェントに決定モデルコントローラーを足すとコストだけ上がり成功率は上がらないと報告する論文(プラセボ対照研究)

- 出典: https://huggingface.co/papers/2610.24649 (コード: https://github.com/namanvats/decision-model-controllers)
- 概要: Claude Sonnet 5.5のターミナルエージェントに、停止判断・検証・方針転換といった決定ポイントでのみ介入する「決定モデル」コントローラー(Jev 1.13)を追加する効果を、none/ルールベース/小型LLM(Claude Haiku 5.5)/Jev/プラセボの5アームでプレ登録比較した研究。21タスク・315試行のheld-out評価で、Jevはコストを19%増やした一方で成功率(両アームとも73.0%)は変わらず、プラセボよりも22%高コストだったと報告。オフラインではJevの判定精度(AUROC 0.78)はルール/小型LLMより高かったが、キャリブレーションが悪く既に正しい作業にも検証を要求し、どのコントローラーも「打ち切り」を一度も選ばなかったという。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出。論文自体も直近の投稿)
- 検証難易度: 高(コードは公開されているが、フル再現にはOpenRouter APIキー〈クレジット課金〉とDaytonaサンドボックス課金が必須〈smokeフェーズだけで約$3、評価フェーズは540試行〉。本リポジトリの方針「当面は有料APIキー必須の候補を選ばない」に抵触するため、フル再現は選定不可。取り上げる場合は論文の主張・実験設計の解説と、Claude Code自身を使った小規模な概念実証〈例: 自分の小さなタスクに簡易的な決定ルールを足して応答回数/手直し回数を比較する程度〉に限定する必要がある)
- 見栄え: 「エージェントに賢そうな管理者を足したらむしろコストが増えるだけだった」という反直感的な結果はエージェント設計の議論として刺さりやすく、本チャレンジの「エージェント信頼性」系(Planning-as-Routing等)の続編として位置づけられる。有料API必須という制約を記事内で明記する必要あり。
- 状態: 未選択

### [2026-10-21] "More Memory, Worse Agents" — 要約・ルール化した記憶が誤りを定着させる「エラー再生産」を指摘し、生の軌跡を使い捨てる"Anti-Persistence"を提案する論文

- 出典: https://huggingface.co/papers/2610.27406
- 概要: モデル重みを更新せず自身の経験を蓄積して自己改善するLLMエージェントにおいて、推論ルールや要約を記憶として貯め込む従来design(Hindsight等、本チャレンジでも既に扱った系譜)は、誤りを含んだまま定着・再生産してしまう「エラー再生産(error reproduction)」を起こすと指摘。生の軌跡と結果だけを保持し、タスクごとにオンデマンドでガイダンスを組み立てて使い捨てる"Anti-Persistence"という設計を提案し、ALFWorld/WebShop/ScienceWorld(3バックボーン: Llama-4-Scout/Qwen3-Coder-Next/Gemma-4-31B-it)でheld-out成功率・LLM呼び出しコストの両方で既存の記憶設計を上回ったと報告。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出。論文自体も直近の投稿)
- 検証難易度: 中〜高(論文側のコード公開は確認できず、検証に使われたバックボーン〈Llama-4-Scout/Qwen3-Coder-Next/Gemma-4-31B-it〉はいずれもGPU前提の大型モデル。フル再現ではなく、「要約を貯めて使う記憶」vs「生の軌跡を使い捨てるAnti-Persistence」という設計思想を、自作の小さなタスクログ・軽量モデルまたはClaude Code自身で疑似再現する縮小版の概念実証に絞る必要がある)
- 見栄え: 本チャレンジで既に扱ってきたHindsight・Remory等の「エージェントメモリ」系候補群に対する反論・別解として位置づけられ、「記憶を貯めるほど良いとは限らない」という反直感的な切り口はBefore/After(要約ベース記憶 vs Anti-Persistence)の比較デモを作りやすい。
- 状態: 未選択

### [2026-10-22] "Entertain, then Cancel" — 推論モデルは「思考」すればするほどsome/orを論理的に"字義通り"読むようになる(COLM系論文、HF Daily Papers本日27位)

- 出典: https://huggingface.co/papers/2610.21204 (コード・データ: https://github.com/kouzhizhuo/entertain-then-cancel 、HKUST/HKUST(広州)/北京大学、HF Daily Papers 2026-10-22時点27位・12 upvote)
- 概要: 推論モデルの「思考予算(thinking budget)」だけを変えてモデル重みは固定し、"some"(not all)や"or"(not both)のようなスカラー含意を、文脈に応じた豊かな解釈ではなく論理記号通りの字義通りの意味で読むかどうかを調べた研究。40種のオープンモデルのうち30種とGPT-5で、思考量が増えるほどsome/orのスカラー含意が「キャンセル」され字義通りの解釈に収束する一方、間接応答・前提のような文脈依存推論はむしろ思考で改善することを報告。推論トレースを途中で区切って都度答えさせる実験から、モデルは最初は豊かな解釈を「一旦採用してから後でキャンセルする(entertain, then cancel)」という時系列パターンを示すとし、早い段階の解釈から答えさせることでスカラー含意を字義通り精度を落とさず回復できる推論時手法も提案している。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出。論文自体も2026-10-16投稿の比較的新しいもの)
- 検証難易度: 低(コード・プロンプト・全モデルトレース公開済み。クローズドモデル〈GPT-5/Claude/Gemini〉での再現には有料API課金〈論文では合計約$105〉が必要だが、本リポジトリの方針上そこは避け、Claude Code自身の拡張思考(thinking)のON/OFFや思考量を変えて、"some"/"or"を含む自作のテスト文(例: 「宿題の一部を終えた」「AまたはBを選べる」等)に対する解釈がどう変わるかを比較する、追加APIキー不要の縮小版概念実証に限定する。GPU不要)
- 見栄え: 「よく考えるAIほど皮肉なことに"文脈を読まなくなる"」という反直感的な結果は言語学的に面白く、自分で用意した日本語・英語の曖昧文に対するClaude Codeの解釈をBefore(思考なし)/After(思考あり)で並べて見せるデモが作りやすい。本チャレンジで初めて扱う「推論モデルの言語解釈バイアス」という切り口で差別化しやすい。
- 状態: 未選択

### [2026-10-22] Cache Engineering for Agents(AKV) — エージェントが自分のKVキャッシュを直接操作する「キャッシュエンジニアリング」(清華大学、HF Daily Papers本日4位)

- 出典: https://huggingface.co/papers/2610.28577 (コード: https://github.com/thu-nics/AKV 、清華大学・香港中文大学、HF Daily Papers 2026-10-22時点4位・109 upvote、投稿日2026-10-21)
- 概要: エージェントの履歴が伸びるほどKVキャッシュのI/O・保存コストが支配的になる問題に対し、要約や履歴の書き換え(既存のcontext engineering)はキャッシュを無効化し再prefillのコストを招くとして、エージェント自身が将来の注意から特定のキャッシュエントリを除外する"drop"、保持したキーの位置エンコーディングを調整する"repos"という2つの操作で、履歴を書き換えずにアクティブなKVキャッシュを直接操作できるようにする手法。これを支えるサービングエンジンAKVはステートレスなAPIを提供しつつ内部で履歴依存のキャッシュ再利用・eviction・復元を管理する。ツール応答に対するrolling-drop方針は、閾値トリガー型の要約と比べ3モデル×4ベンチマークで平均スコア+1.7pt・平均コスト-27.7%、AKV自体はスループット最大1.2倍・P95レイテンシ1.5倍改善、キャッシュ方針を再帰的に自己改善させるとheld-outタスクでさらに-7.1%のコスト削減を報告。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出。投稿当日のため当然未発信)
- 検証難易度: 中〜高(コード公開済みだが、論文のサービング実験はA800 80GB×8枚・GPT-OSS-120B等の大型モデル前提でフル再現は非現実的。本リポジトリの方針に沿うなら、"drop"/"repos"というアイデア自体(不要になった履歴のキャッシュを捨てる/位置エンコーディングを調整する)を、ローカルで動く小型モデル〈GPT-2やQwen小型モデル等〉上で疑似再現し、通常の「要約して詰め込む」方式との応答品質・トークン/レイテンシをBefore/After比較する縮小版の概念実証に絞る必要がある。GPU必須ではないがCPU推論は低速)
- 見栄え: 本チャレンジで既に扱ってきたRemory・Headroom・context-mode・caveman等の「エージェントのコンテキスト/メモリ圧縮」系の最新作として位置づけられ、Before/Afterのトークン削減率・レイテンシのグラフが作りやすい。ただし同テーマが頻出しているため、採用する場合は「要約ではなくキャッシュそのものを操作する」という新しい切り口を明記した方がよい。
- 状態: 未選択

### [2026-10-22] HKUDS/Vibe-Trading — 自然言語の指示だけで調査・バックテスト・発注までやらせる個人用AIトレーディングエージェント(本日GitHub Trending全言語で急伸)

- 出典: https://github.com/HKUDS/Vibe-Trading (本日GitHub Trending全言語で+166star/日、総計36,321star。香港大学HKUDSラボ発、2026年7月初出・以後継続的に機能追加)
- 概要: 自然言語の調査クエリを、投資委員会・クオンツ・リスクレビュー・マクロ・クリプト等の役割を持つ複数エージェント(swarm)が受け取り、実行可能なバックテストや(設定次第で)発注まで行う個人用AIトレーディングエージェント(MITライセンス)。pipパッケージ(`vibe-trading-ai`)として配布され、CLI・FastAPI Web UI・MCPサーバーのいずれからも起動可能。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出。英語・中国語・韓国語の紹介記事は複数あり)
- 検証難易度: 中(MIT。LLMバックエンドとしてどのプロバイダが必須かはREADME精読が必要で、Claude Code自身や無料枠LLMで代替できるか要確認。データソースはYahoo Finance等の無料枠で代替しバックテストに限定すれば、実際の発注(ブローカーAPI)無しでも検証可能と見込まれる。GPU不要。本リポジトリで既に扱った金融系候補〈day-022 Kronos〉とは「基盤モデル単体」ではなく「調査〜バックテストまでを自動化するマルチエージェント」という点で異なる)
- 見栄え: 「自然言語で指示するだけでバックテスト戦略が組まれて結果が返ってくる」様子はデモ映えしやすく、スクリーンショットやレポート出力も見せ場になる。採用する場合は実際の発注機能には触れず、研究・バックテスト用途に限定して検証・記事化すること。
- 状態: 未選択

### [2026-10-22] EveryInc/compound-engineering-plugin — 「計画→実装→レビュー→知見の蓄積」を回すClaude Code公式スキルループプラグイン

- 出典: https://github.com/EveryInc/compound-engineering-plugin (本日GitHub Trending TypeScriptで+25star/日、総計25,658star。Every社のKieran Klaassen氏がCora開発から生み出した手法のOSS化)
- 概要: Claude Code/Cursor/Codex等14種のエージェントホスト向けに、ブレインストーミング→計画(`/ce:plan`)→実装(`/ce:work`)→複数エージェントによるレビュー(`/ce:review`)→学びをCLAUDE.md等に書き戻す知見の蓄積(`/ce:compound`)というループを回す36個のスキル・22個のワークフローコマンド・29個の専用エージェントをまとめたプラグイン(MITライセンス)。「各作業単位が後続の作業を楽にするべき」という"Compound Engineering"思想を具体化したもの。
- 日本語記事件数: Zenn 1件(Claude Codeでの実践方法を解説する記事が既に1件あるが、プラグイン自体の検証記事ではなく概念解説が主) / Qiita 0件 / note 0件
- 検証難易度: 低(MIT。`/plugin marketplace add EveryInc/compound-engineering-plugin`→`/plugin install compound-engineering`でClaude Code CLIから追加の有料APIキー無しで導入可能。GPU不要)
- 見栄え: 同一の曖昧な開発タスクを、プラグイン導入前のClaude Codeと導入後(`/ce:plan`→`/ce:work`→`/ce:review`→`/ce:compound`を通した場合)に与え、計画の具体性・レビューで拾われる指摘数・CLAUDE.mdへの知見蓄積の有無をBefore/After比較できる。本リポジトリ自身が「朝リサーチ→昼実装→夜レビュー」というループで運用されている点と相性が良く、自己言及的な検証がしやすい。andrej-karpathy-skills・ponytail等の既存の「Claude Codeの振る舞いを変えるプラグイン/スキル」系の続編として位置づけられる。
- 状態: 未選択

### [2026-10-23] cloudflare/security-audit-skill — Cloudflare公式、コーディングエージェントを「発見者と検証者が別エージェント」の多段階セキュリティ監査官に変えるClaude Codeスキル

- 出典: https://github.com/cloudflare/security-audit-skill (本日GitHub Trending全言語で1位・+2,706star/日。初出は2026年9月下旬で、Cloudflare社内の脆弱性発見ハーネスの出発点として公開されたもの。今回のトレンド急伸自体は新規リリースというより再拡散と見られる)
- 概要: コーディングエージェント(Claude Code等)に「偵察→網羅的探索→候補の検証→構造化出力→独立した記録検証→レポーティング」の6フェーズでセキュリティ監査を行わせるスキル(MITライセンス)。各フェーズを別々のサブエージェントが担当し、脆弱性を「発見したエージェント」と「それを反証しようとするエージェント」を分離することで誤検知を減らす設計。対象コードを実際に実行して検証する場合はOSで強制されたサンドボックス(ネットワーク遮断等)が前提で、本体のスキル自体はそのサンドボックスを提供しない。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(site:検索ではいずれも0件。英語・中国語・スペイン語・ドイツ語の紹介記事は複数あるが、日本語の一次検証記事は検索した範囲では未検出)
- 検証難易度: 低(MIT。`npx skills add https://github.com/cloudflare/security-audit-skill --skill security-audit`でClaude Code CLIから追加の有料APIキー無しで導入可能〈Claude Code自身のサブスクリプションを使う〉。GPU不要。本リポジトリ自身〈ai-100days〉や適当な脆弱性入りサンプルコードに対して実行し、実際に何が検出され、どの候補が「反証エージェント」によって却下されたかを比較するBefore/After〈単純な1エージェントでのレビュー依頼 vs 本スキル導入後〉が6時間以内に可能)
- 見栄え: 「発見者と検証者を別エージェントに分ける」という誤検知対策の仕組みを、実際に見つかった指摘とその反証ログを示しながら解説できる。セキュリティ診断という実務色の強いテーマで、本チャレンジの「Claude Codeの振る舞いを変えるスキル」系(ponytail・compound-engineering-plugin等)とは異なり実務直結のユースケースとして差別化しやすい。
- 状態: 未選択

### [2026-10-23] NVIDIA/OpenShell — NVIDIA公式、自律AIエージェントをカーネルレベルでサンドボックス隔離するオープンソースランタイム

- 出典: https://github.com/NVIDIA/OpenShell (本日GitHub Trending全言語で+1,240star/日・累計約18.7k star。本日のHacker News フロントページにも掲載。初出は2026年9月28日発表の「NVIDIA Open Agent Safety Platform」の一部で、今回のトレンドは新規リリースというより再拡散・新バージョンへの反応と見られる)
- 概要: 自律AIエージェントをDockerコンテナ単位のサンドボックスで隔離実行するランタイム(Apache-2.0)。宣言的なYAMLポリシーで、ファイルアクセス(Landlock LSM)・システムコール(seccomp)・ネットワーク接続・推論呼び出しをエージェントプロセスの外側からカーネルレベルで強制し、エージェントは実際の認証情報を直接見ることなく承認済みエンドポイント宛の通信にのみ認証情報が付与される。リスクの高いポリシー変更は人間のレビューに回される。Claude Code/Codex/OpenCode/GitHub Copilot等複数のコーディングエージェントに対応。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(site:検索ではいずれも0件。ただし日本語のビジネス系ニュース記事〈Business Insider Japan、rocket-boys.co.jp、eesel.ai日本語版等〉による「Open Agent Safety Platform」発表の紹介は複数あり。技術者による実際に動かした日本語の一次検証記事は検索した範囲では未検出)
- 検証難易度: 中(Apache-2.0。`curl -LsSf https://raw.githubusercontent.com/NVIDIA/OpenShell/main/install.sh | sh`でCLI導入後、`openshell sandbox create`でサンドボックス作成。Docker/Podmanまたはホスト仮想化が前提。モデルバックエンドはOpenRouterの無料枠モデルでチュートリアルが組まれており、追加の有料APIキーは必須ではない見込み。GPU不要。Routineのクラウド実行環境でDockerが使えない場合はローカル検証にエスカレーションする必要がある)
- 見栄え: 「エージェントに認証情報を直接見せずに、承認済み先への通信にだけ後から認証情報を付与する」という仕組みを、実際にポリシーを設定してアクセス許可/拒否が切り替わる様子で見せられる。本チャレンジで取り上げてきた「エージェントの安全な実行環境」系の中でもNVIDIA公式発という点でニュース価値が高い。
- 状態: 未選択

### [2026-10-23] "Deep Search in Real-World Web Environments"(OpenDS) — 動画のワンシーンから出発し複数モダリティ・複数ソースを辿らないと解けない「深い検索」ベンチマークで最高性能モデルでも39%しか解けないと報告する論文

- 出典: https://huggingface.co/papers/2610.30181 (HF Daily Papers 2026-10-23時点3位・149 upvote、投稿日2026-10-21頃)
- 概要: テキスト・画像・音声・動画など複数モダリティ、HTML・PDF・CSV等複数フォーマットに証拠が分散する実際のWeb調査を測るため、動画から「アンカーとなる実体」を特定し、そこからGoogle検索等を辿って複数ソースで裏付けられた証拠経路を構築し、それを間接的な手がかりに逆変換した200問のベンチマーク「OpenDS-World」を提案。検索・GUIブラウジング・動画/字幕ツールを備えた共通ハーネス上で12種のフロンティアモデルを評価し、100回のツール呼び出し・1時間の予算という条件下で、最高性能のGPT-6 Astraでも正解率39.0%、Claude Opus 5.5は38.0%にとどまり、人間50人による基準(21.1%、42.5%の問題はどの担当者も解けなかった)との比較も報告している。思考量やツール呼び出し数を増やしても精度向上が信頼できないこと、ツール呼び出しの失敗が実行時間の多くを占めることも指摘。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出。論文自体も投稿直後)
- 検証難易度: 高(フルベンチマークの再現にはGPT-6 Astra・Claude Opus 5.5等の有料フロンティアモデルAPI、検索API、ヘッドレスブラウザ、動画処理環境が必要で、1タスクあたり最大100回のツール呼び出し・1時間という予算も課金額が大きくなる見込み。本リポジトリの方針上フル再現は選定不可。取り上げる場合は、論文の構成〈動画のワンシーン→アンカー実体特定→複数ソースを辿る間接的手がかり〉を模した自作の小問〈3〜5問程度〉を用意し、Claude Code自身の検索・Webフェッチ機能だけでどこまで解けるか/どこで詰まるかを確認する追加APIキー不要の縮小版概念実証に絞る必要がある)
- 見栄え: 「フロンティアモデルでも4割弱しか解けない、人間はさらに低い」という具体的な数字が強く、自作の難問をClaude Code自身に解かせて「どのステップで詰まったか」を実況するBefore/After的なデモ記事が作りやすい。ただし有料API必須のフル再現ではない旨を記事内で明記する必要がある。
- 状態: 未選択

### [2026-10-23] OpenBMB/VoxCPM2 — トークナイザー不要の拡散自己回帰方式で30言語の音声生成・ボイスデザイン・ボイスクローンを行うTTSモデル

- 出典: https://github.com/OpenBMB/VoxCPM (本日GitHub Trending Pythonで+144star/日。最新リリースv2.0.3は2026年5月11日付で、今回のトレンドは新規リリースというより再拡散と見られる)
- 概要: 離散トークナイザーを使わず拡散自己回帰アーキテクチャで音声を生成する2BパラメータのTTSモデル(Apache-2.0、MiniCPM-4ベース)。30言語対応、テキストでの説明からボイスを作る「ボイスデザイン」、5〜10分程度の音声で行える制御可能なボイスクローン、48kHz出力を特徴とする。`pip install voxcpm`でインストールし、`voxcpm design`/`voxcpm clone`/`voxcpm batch`のCLIコマンドやPython API、ローカルWeb UI(`python app.py`)で利用できる。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(site:検索ではいずれも0件。韓国語〈wikidocs.net〉・中国語の紹介記事は複数あるが、日本語の一次検証記事は検索した範囲では未検出)
- 検証難易度: 低〜中(Apache-2.0。追加の有料APIキー不要。推奨VRAMは約8GBだが、Web UIはCPU/MPSデバイスも選択可能(速度は遅い見込み)。Routineのクラウド実行環境にGPUが無い場合はCPU推論で低速になるか、モデルダウンロード自体がネットワーク制限で進まない可能性があり、その場合はCLAUDE.mdの方針に従いローカル検証にエスカレーションする)
- 見栄え: 同じテキストを「ボイスデザイン」で生成した声と「ボイスクローン」で複製した声とで聴き比べるBefore/After音声デモは分かりやすく、シェアカードに波形やスペクトログラムの画像を載せれば視覚的にも見栄えが良い。本チャレンジで音声生成系を取り上げるのは今回が初めてで、既存の「エージェント/コンテキスト圧縮」系とは異なる新しい切り口になる。
- 状態: 未選択

### [2026-10-24] pbakaus/impeccable — 「AIハーネスをデザインに強くする」デザイン言語・決定論的検出CLI(本日GitHub Trending 1位級、+733star/日)

- 出典: https://github.com/pbakaus/impeccable (本日GitHub Trending全言語で+733star/日、累計86,288star。作者はjQuery UIの作者としても知られる元Google Developer Advocate)
- 概要: Claude Code/Codex/Cursor等のAIコーディングエージェントが生成するフロントエンドが「AIスロップ」(Interフォント多用・紫→青グラデーション・カードの入れ子等の定型デザイン)になりがちな問題に対し、24個のスラッシュコマンド(`/impeccable audit`・`/polish`・`/critique`・`/harden`等)と、HTML/CSS/URLを62のルールでLLM不要・決定論的に検査するCLI検出器(`npx impeccable detect`)を組み合わせたデザイン言語(Apache-2.0)。同日GitHub Trendingには同種の設計方針を持つNutlope/hallmark(こちらはテーマベースのデザインスキル、MIT、+570star/日)も急伸しており、本チャレンジでは検出器が決定論的でAPIキー不要な点から1つを選び、重複を避けるためhallmarkは候補に含めなかった。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(site:検索ではいずれも0件。open-design.aiに日本語の紹介ページが1件あるが、著者自身による検証記事ではない。英語・ポルトガル語・スペイン語・ドイツ語・韓国語の紹介記事は多数あり)
- 検証難易度: 低(Apache-2.0。検出器CLI自体はLLMもAPIキーも不要と明記されている。Node.jsのみで`npx impeccable detect`が動作し、ブラウザでのURL検査にはChrome/Chromium/Edgeが必要だが、無くても静的なHTML/CSSファイルへの検査は可能。GPU不要。telemetry送信はオプトアウト可)
- 見栄え: 意図的に「AIスロップ」な定型HTML(Interフォント・紫グラデーション・空のカード等)を用意し、`impeccable detect`前後の検出ルール違反数をBefore/Afterの数値・グラフで見せやすい。さらにClaude Codeに同じプロンプトで画面を作らせ、スキル導入前後で生成結果がどう変わるかも比較できる。
- 状態: 未選択

### [2026-10-24] aws/agent-toolkit-for-aws — AWS公式、AIコーディングエージェントがAWS上で構築するためのMCPサーバー・スキル・プラグイン集

- 出典: https://github.com/aws/agent-toolkit-for-aws (本日GitHub Trending Pythonで+11star/日・累計3,090star。2026年5月6日発表「Agent Toolkit for AWS」のOSS実体で、既存のAWS Labs発MCPサーバー/プラグイン群の後継)
- 概要: Claude Code/Codex/Cursor/Devin/Kiro等のAIコーディングエージェントがAWS上でアプリを構築・デプロイ・管理できるよう支援する、AWS公式サポートのツール集(Apache-2.0)。AWS MCP Server(API呼び出し・サンドボックスでのスクリプト実行・ドキュメント検索)、タスク別スキル、プラグイン(`aws-core`・`aws-agents`〈Bedrock/AgentCore〉・`aws-data-analytics`等)、ルールファイルの4要素で構成される。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(site:検索ではいずれも0件。AWS公式発表〈aws.amazon.com/about-aws/whats-new〉と公式ドキュメントのみ確認、日本語の一次検証記事は検索した範囲では未検出)
- 検証難易度: 中(ツール固有の追加APIキーは不要だが、実際にAWS MCP Server経由でAPI呼び出し・スクリプト実行を行うにはAWSアカウントとローカルのAWS認証情報が必要で、AWS利用料金が発生する可能性がある。本リポジトリの方針上、新しいシークレット登録はできないため、検証範囲は「アカウント不要」と明記されているドキュメント検索・スキルカタログの検出・プラグイン構成の確認に絞る必要がある。GPU不要)
- 見栄え: 「AWS公式がAIエージェント向けに出したMCPツールキット」というニュース価値はあるが、AWSアカウント連携を伴う本格的なデプロイデモは本Routineの方針(新規シークレット不可)では見せられない。採用する場合は検証スコープの限定を記事内に明記する必要がある。
- 状態: 未選択

### [2026-10-24] makecindy/cindy — Claude Code/Codexを横断してメモリ・スキルを共有するゼロコンフィグOSS AIエージェント(本日GitHub Trending TypeScript+471star/日)

- 出典: https://github.com/makecindy/cindy (本日GitHub Trending TypeScriptで+471star/日、累計4,024star)
- 概要: Claude CodeとCodexを最初の対応ハーネスとして、複数のAIコーディングエージェント・モデル・ツールを1つのワークスペースにまとめ、一度修正したメモリやスキルをハーネスをまたいで共有できるデスクトップ/モバイルのOSSクライアント(Apache-2.0。モデル重み・データセット・商標等は別条件)。ブラウザ・コンピュータ・スマートフォンの操作、IM/スケジュール経由でのタスク受付、定期自動化、MCP連携も備える。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(site:検索ではいずれも0件。中国語〈简体中文README〉・トレンド集計サイトでの言及はあるが日本語の紹介記事は検索した範囲では未検出)
- 検証難易度: 中〜高(Node.js 22.x/pnpm 10.x/Git LFSが前提で、`pnpm install`時にclaude-code・codex・ripgrepのプラットフォーム別バイナリをダウンロードする構成。「Skip Sign-In」でアカウント無しのローカルエージェント利用は可能(サーバー連携機能は不可)で追加APIキーは不要だが、デスクトップ/モバイルGUIアプリとしての動作確認はヘッドレスなクラウド実行環境では困難な可能性が高く、CLIレベルの検証に限定されるか、人間のローカルPCでのGUI確認が必要になる可能性がある)
- 見栄え: 「Claude CodeとCodexの間でメモリ・スキルを共有しながら作業を引き継ぐ」様子はBefore/After的に見せやすいが、GUI部分の検証がRoutine環境の制約を受けやすい点に注意(CLAUDE.mdの「Routine環境の制約」エスカレーションルールに該当する可能性がある)。
- 状態: 未選択

### [2026-10-24] IQuestLab/IQuest-Q1 — 320B(active 15B)の疎MoEによるエージェント型CLI基盤モデル(Hugging Face Daily Papers上位)

- 出典: https://huggingface.co/papers/2610.30949 (モデル: https://huggingface.co/IQuestLab/IQuest-Q1 、コード: github.com/IQuestLab/IQuest-Q1。本日Hugging Face Daily Papersで上位掲載)
- 概要: ソフトウェア開発・汎用タスク実行・長期推論・サイバーセキュリティ等のCLI/エージェント作業に重点を置いた疎MoE基盤モデル(総パラメータ約320B、トークンあたり有効化15B、コンテキスト524,288トークン、BF16公開)。SWE-Bench Pro 57.5、Terminal-Bench 2.1で83.2、CyberGym 84.5などのベンチマークを報告。vLLM/SGLangでのデプロイ(`--tp-size 8`等、8GPU構成前提)が想定されている。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(site:検索ではいずれも0件。中国語〈量子位系記事の転載〉の紹介記事はあるが日本語の一次検証記事は検索した範囲では未検出)
- 検証難易度: 高(Hugging Faceページには独自ライセンス「iquest-q1」の表記のみで条文の詳細・商用利用可否は未確認。Hosted Inference Providerや無料デモも無く、自前でvLLM/SGLangサーバーを立てる必要がある。BF16重みは約640GB相当と推定され8GPU構成が前提のため、個人が6時間以内に手元で動かすのは非現実的。CLAUDE.mdの方針(有料APIキー/GPU必須の候補は避けるか制約を明記)に抵触する可能性が高く、扱う場合はベンチマーク結果の紹介に留めるニュース解説のみに限定する必要がある)
- 見栄え: ベンチマーク数値は豊富でニュース価値は高いが、実機で「動かしてみた」検証ができないため本チャレンジの「動かしていないものを動いたと書かない」原則に抵触しやすい。採用には慎重な判断が必要。
- 状態: 未選択

### [2026-10-25] TauricResearch/TradingAgents — アナリスト・討論・リスク管理を分業するマルチエージェントLLM金融トレーディング研究フレームワーク

- 出典: https://github.com/TauricResearch/TradingAgents (本日GitHub Trending Pythonで+636star/日、累計9万star超。元論文はarXiv:2412.20138)
- 概要: 証券会社の役割分担を模し、ファンダメンタルズ/センチメント/ニュース/テクニカル分析の4アナリストが並列調査し、ブル派・ベア派の研究者が討論、トレーダーが取引案を提示し、リスク・ポートフォリオマネージャーが承認/却下するマルチエージェントLLM金融トレーディング研究フレームワーク(Apache-2.0、LangGraphベース)。CLI・Python API・Docker対応、過去の判断ログを次回に活かすメモリ機能やバックテストツールも備える。
- 日本語記事件数: Zenn 1件以上(「TradingAgentsを使ってみた」等、セットアップ手順を解説する記事が既に存在) / Qiita 0件 / note 0件(site:検索で確認。いずれも実際にバックテストを動かした検証記事ではない)
- 検証難易度: 低〜中(Apache-2.0。LLMバックエンドはOllamaのローカルモデルやOpenAI互換のローカルサーバー〈vLLM/LM Studio/llama.cpp〉を無料で利用できる設計で、追加の有料APIキー不要で検証可能。市場データもSEC EDGAR〈キー不要〉・Yahoo Finance・無料枠のFRED等で代替できる見込み。GPU不要)
- 見栄え: 実際の個別株を対象にアナリスト調査→ブル/ベア討論→トレーダー判断→リスク管理という一連の意思決定ログをそのまま記事に載せられ、マルチエージェントの「合議制」トレーディングという切り口はデモ映えする。日本語のセットアップ記事は既に1件あるが、実際にバックテストまで動かした検証記事は確認した範囲では見当たらず差別化しやすい。投資助言ではなく研究目的であることを明記する必要あり。
- 状態: 未選択

### [2026-10-25] "Is Complex Agentic Memory Always Needed? Naive RAG Is Stronger Than We Thought" — 要約・変異型のエージェントメモリより素朴なRAGが強いと報告する論文(HF Daily Papers掲載)

- 出典: https://huggingface.co/papers/2610.30755 (arXiv 2610.30755、投稿日2026-10-23頃)
- 概要: 会話履歴を要約・抽出・UPDATE/DELETE等で加工する既存の「エージェントメモリ」手法群に対し、生の会話履歴に密検索+クロスエンコーダ再ランキングだけをかける素朴な「Raw-RAG」ベースラインが、比較した7つのモデル設定のうち6つで最高性能を記録したと報告する論文。Mem0のUPDATE/DELETE操作を追記のみに置き換えるだけでLoCoMoの精度が67.36%→69.42%に改善する例を示し、メモリの「加工・変異」自体が有害になりうる場合があることも指摘。素朴なRAGは取り込みコストも大幅に低い(MEMEスライスで取り込み+検索305.91秒)と報告している。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では本論文自体の日本語紹介記事は未検出。「エージェントメモリ vs RAG」という一般論の日本語記事はあるが本論文の主張の紹介ではない)
- 検証難易度: 低(著者独自実装のコード公開は確認できず。本リポジトリの方針に沿い、フル再現ではなく「要約・変異型メモリ」vs「素朴な生履歴RAG」という設計思想の対比を、自作の小さな会話履歴データセットとClaude Code自身の検索機能・軽量な埋め込みだけで疑似再現する縮小版の概念実証に絞る。追加APIキー・GPU不要)
- 見栄え: 本チャレンジで繰り返し扱ってきたHindsight・Remory・AKV・Anti-Persistence等の「エージェントメモリを賢く加工する」系の潮流に対する「素朴な方が強い」という反直感的な結果を示すアンチテーゼ回として位置づけられ、Before/After(加工型メモリ vs 生履歴RAG)の精度・コスト比較が作りやすい。日本語記事が無く差別化しやすい。
- 状態: 採用済み(day-028)

### [2026-10-25] Heartbeat Thinking — 発話を聞きながら先行して推論・ツール実行しておきリアルタイム音声エージェントの応答を高速化する手法(HF Daily Papers掲載)

- 出典: https://huggingface.co/papers/2610.26233 (arXiv 2610.26233、投稿日2026-10-20)
- 概要: リアルタイム音声エージェントにおいて、ユーザーの発話を聞いている最中にも500ms間隔で「Thinker」を起動し、部分的な書き起こしから推論・ツール呼び出しを非同期に先行実行しておき、発話終了時に「Responder」が完了済みの準備結果を再利用して未完了分だけを実行することで応答を高速化する手法。SHANKS系のウィンドウ思考ベースラインと比べ投機的ツールカバレッジが向上し、FDBench v3では最終応答レイテンシが6.90秒→4.39秒(36.4%減)に短縮したと報告。一方でタスク精度は一部ベンチマークでわずかに低下するなど、準備の蓄積が必ずしも精度向上につながらないとも指摘している。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出。論文自体も投稿から日が浅い)
- 検証難易度: 中〜高(著者独自実装のコード公開は確認できず、フル再現にはQwen3.6-35B-A3B等の大型モデル+H200 GPUが前提で非現実的。本リポジトリの方針に沿い、実際の音声入出力は使わず、テキストで「部分的な入力を受け取るたびに先行して処理し、入力完了時に差分だけ処理する」疑似ストリーミング実験をClaude Code自身で組んで、先行処理なし/ありの応答までの手数・待ち時間を比較する縮小版の概念実証に絞る必要がある。追加APIキー・GPU不要)
- 見栄え: 「聞きながら先読みして考えておく」という仕組みを簡略化したテキストデモで示せ、本チャレンジで初めて扱う「リアルタイム音声エージェントの低遅延化」という切り口で差別化しやすい。精度がわずかに下がるケースもあるという正直な限界も記事に書きやすい。
- 状態: 未選択

### [2026-10-25] JetBrains/thinkrail — JetBrains公式、CLIコーディングエージェント「pi」向けの軽量グラフィカルIDE(アルファ版)

- 出典: https://github.com/JetBrains/thinkrail (JetBrains公式InnovationHub発、本日GitHub Trending TypeScriptで+52star/日、累計約1.5k star)
- 概要: CLIコーディングエージェント「pi」のためのグラフィカルなワークスペースを提供する軽量IDE(Apache-2.0)。エージェントとのやり取りをgit worktreeで分離したワークスペースごとに管理し、Monacoエディタ・ターミナル・ファイルツリー・diffレビューを備える。プロジェクトの知見は`SPEC.md`に蓄積されエージェントが読み書きする設計で、Agent Skills・MCPサーバー・GitHub PRワークフローにも対応する。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(site:検索ではいずれも0件。検索した範囲では英語の紹介記事のみ確認)
- 検証難易度: 中(Apache-2.0だが、バックエンドのpiエージェント自体がどのLLMプロバイダ・APIキーを要求するかは要確認で、JetBrains AIでのサインインまたは独自プロバイダ連携が必要とされる。追加の有料APIキーなしで検証できるかは着手前にpi側のドキュメントを読んで判断する必要がある。アルファ版のため不具合の可能性もある点にも注意。GPU不要)
- 見栄え: 「エージェントとのやり取りをgit worktreeで分離し、SPEC.mdに知見を蓄積していく」という設計をスクリーンショット付きで見せられ、JetBrains公式が本格的にエージェント型IDE競争に参入したというニュース価値も高い。本チャレンジで既に扱ったClaude Code向けスキル/プラグイン系とは異なり、IDEそのものという切り口で差別化できる。ただしAPIキー要件次第では見送りまたはスコープ限定が必要。
- 状態: 未選択

### [2026-10-25] Agent Mosaic — 個別には問題ない文書の組み合わせからLLMエージェントが機密な結論を合成・開示してしまう「モザイク効果」を検証する論文(HF Daily Papers掲載)

- 出典: https://huggingface.co/papers/2610.30418 (arXiv 2610.30418、USC Information Sciences Institute、投稿日2026-10-23頃)
- 概要: 個別には閲覧権限内の文書群からでも、LLMエージェントがそれらを組み合わせることで本来非公開であるべき結論(「モザイク効果」)を合成・開示してしまう問題を検証した論文。単一文書で答えられる一見無害な質問でも、シミュレーションで7.08%〜12.50%の応答が許可されていない複合的な結論を開示し、分類ヘッダーや集約ルールの明示でその割合は下がるものの32.37%は依然残存すると報告。拒否応答の説明文自体が機密結論を漏らすケースがあることも指摘している。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出。類似テーマの別論文「MosaicLeaks」〈ServiceNow発、arXiv:2605.30727〉との混同に注意。本候補は別の論文〈arXiv:2610.30418〉を指す)
- 検証難易度: 中(論文の著者コードは未公開〈採択後公開予定とのみ記載〉。フル再現にはGPT-5.6-Sol等への有料API課金が必要だが、本リポジトリの方針に沿い、Claude Code自身に「個別には問題ない」複数の架空文書〈例: 医療・セキュリティ分野の断片情報〉を与え、組み合わせた結論を開示するかどうかを確認する縮小版の概念実証に絞れば追加APIキー不要で検証可能)
- 見栄え: 「個々の情報は無害でも組み合わせると機密になる」という具体的な失敗例を自作のダミー文書で再現し、実際にClaude Codeが開示してしまうかどうかを見せるBefore/After的なデモは説得力がある。本チャレンジで既に扱ったHexStrike AI・SkillSpector・security-audit-skill等の「攻撃的/監査的セキュリティ」系とは異なり、「エージェントが意図せず機密を漏らす」という防御的データプライバシーの切り口で差別化できる。
- 状態: 未選択

### [2026-10-26] Nutlope/hallmark — Claude Code/Cursor/Codex向け「アンチAIスロップ」デザインスキル(本日GitHub Trending全言語で2位級、+2,235star/日)

- 出典: https://github.com/Nutlope/hallmark
- 概要: Claude Code/Cursor/Codex/OpenCode向けのデザインスキル(MIT)。プロジェクトの目的に応じて48種のテーマから1つを選び、生成したWebページを「スロップテストゲート」と呼ぶ静的チェック+自己批評に通すことで、AI生成特有の定型的な見た目(通称AIスロップ)を避けて作る。build/audit/redesign/studyの4モードを持つ。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(fyve.co.jp等の日本語企業ブログによる紹介記事はあるが、実際に動かして比較検証した日本語の一次記事は検索した範囲では未検出)
- 検証難易度: 低(MIT。`npx skills add nutlope/hallmark`で導入でき追加の有料APIキー不要。Claude Code自身をモデルとして使えば追加コストなし。ブラウザでの静的チェックにはPuppeteer/Chromeを使うが、無くても一部チェックは動作する。GPU不要)
- 見栄え: 同じプロンプトでhallmark導入前後にWebページを生成し、レイアウト・配色の多様性と「スロップ判定」結果をBefore/Afterで並べられる。「AIに作らせたサイトはどれも似て見える」という定番の不満に直接答える切り口で分かりやすい。
- 状態: 未選択

### [2026-10-26] mvanhorn/last30days-skill — Reddit/HN/GitHub等を横断し直近30日の話題を要約するClaude Code向けリサーチエージェントスキル(本日GitHub Trendingで急伸)

- 出典: https://github.com/mvanhorn/last30days-skill
- 概要: Reddit・Hacker News・GitHub・Polymarket・X・YouTube等を横断検索し、エンゲージメント(upvote・再生数・賭け率等)でランキングして直近30日の話題を要約するClaude Code向けAIエージェント・リサーチスキル(MIT)。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出)
- 検証難易度: 低(MIT。`/plugin marketplace add mvanhorn/last30days-skill`→`/plugin install last30days`で導入。README上「Reddit・HN・Polymarket・GitHubはゼロコンフィグで即動作」と明記されており、これらのソースに限定すれば追加の有料APIキー不要(X/YouTube/TikTok等の拡張ソースは別途キーが必要なため今回は対象外とする)。GPU不要)
- 見栄え: 本リポジトリ自身の朝リサーチRoutine(本Routine)と同じ「海外の話題を巡回して要点をまとめる」作業を同じトピックでこのスキルにも依頼し、通常のWebSearch巡回による結果とBefore/After的に比較できる。本チャレンジの運用そのものをメタ的に検証できる珍しい切り口。
- 状態: 未選択

### [2026-10-26] eugeniughelbur/obsidian-second-brain — Claude Code等向け、Obsidian Vaultに知見をMarkdown永続化する「第二の脳」システム(本日GitHub Trending Pythonで急伸)

- 出典: https://github.com/eugeniughelbur/obsidian-second-brain
- 概要: Claude Code/Codex等7種のCLIコーディングエージェント向けに、知見・決定事項をObsidian Vault内のMarkdownとして永続化する「第二の脳」システム(MIT)。49種のスラッシュコマンドでハイブリッド検索・矛盾の洗い出し・定期メンテナンスエージェントを提供する。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(英語のObsidian×Claude Code連携記事は複数あるが、本リポジトリ名での日本語紹介記事は検索した範囲では未検出)
- 検証難易度: 低(MIT。Claude Codeプラグインとして`/plugin marketplace add`→`/plugin install`で導入し`OBSIDIAN_VAULT_PATH`を設定するだけ。コア機能〈保存・検索・矛盾チェック等〉は「No API keys needed for the core vault commands」と明記されており追加キー不要。GPUも不要〈音声書き起こし等の一部オプション機能のみPyTorch/Ollamaを使うが必須ではない〉)
- 見栄え: 本リポジトリは夜に`tools/sync-to-obsidian.ps1`で成果をObsidian Vaultへ手動同期する運用をしているため、「Routineの検証結果をこのツールのスラッシュコマンドで記録・検索させてみたら、手動同期スクリプトの運用とどう違うか」というBefore/After比較が作りやすく、本チャレンジの運用改善ネタとして直接語れる。
- 状態: 未選択

### [2026-10-26] Panniantong/Agent-Reach — ログイン必須ページや動画も有料API契約無しに読み取れるAIエージェント向けCLI(本日GitHub Trending Pythonで+723star/日)

- 出典: https://github.com/Panniantong/Agent-Reach
- 概要: Twitter/Reddit/YouTube/GitHub/Bilibili/小紅書など15以上のプラットフォームを、プラットフォームごとの有料API契約無しに1つのCLIから読み取り・検索できるようにする、AIエージェント向けの「インターネットへのアクセス」ツール(MIT)。読み取り専用で投稿・コメント等の書き込みは行わない設計。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(aipicks.jp等の日本語AIツール紹介メディアによる紹介はあるが、実際に動かして検証した日本語の一次記事は検索した範囲では未検出)
- 検証難易度: 低〜中(MIT。多くのデフォルトチャンネル〈GitHub等〉は追加APIキー・ログイン不要と説明されているが、音声書き起こし〈YouTube等〉にはGroq/OpenAIキーが必要、Reddit/Twitter等ログイン前提のチャンネルはブラウザログインの再利用が必要でクラウド実行環境では制約がある見込み。キー/ログイン不要なチャンネルに絞れば6時間以内に検証可能。GPU不要)
- 見栄え: 「エージェントが普段読めないログイン必須ページや動画の内容を、Agent-Reach経由でどこまで読めるようになるか」をBefore/Afterで見せられる。クラウド実行環境の制約でログイン系チャンネルが試せない場合はその旨を明記し、キー/ログイン不要なチャンネルのみの検証に絞る。
- 状態: 未選択

### [2026-10-27] backnotprop/plannotator — Claude Code等のAIコーディングエージェントのplan/diffをブラウザで注釈しフィードバックを送り返すレビューツール(本日GitHub Trending TypeScriptで言及)

- 出典: https://github.com/backnotprop/plannotator
- 概要: Claude Code/Codex/Gemini CLI/OpenCode/Pi等のAIコーディングエージェントが提案した計画(plan)を自動でブラウザのローカルUIに開き、視覚的に注釈してそのままエージェントへフィードバックを送り返せるレビューツール(Apache-2.0とMITのデュアルライセンス)。コード差分やPR/MRのレビュー、Markdown/HTMLファイルへの注釈にも対応し、ターミナル版「Herdr Annotate」も備える。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(site:検索。英語の紹介記事・デモ動画はあるが日本語での一次検証記事は検索した範囲では未検出)
- 検証難易度: 低(コア機能にAPIキー不要〈URL注釈のレート制限緩和用の`JINA_API_KEY`のみ任意で、AIレビュー機能は`PLANNOTATOR_AI=disabled`で無効化可能〉。インストールスクリプト1本とClaude Code向けプラグイン追加〈`/plugin marketplace add backnotprop/plannotator`〉のみで導入でき、GPU不要。本リポジトリ自身がClaude Code Routineで運用されているため、`/plannotator-review`で実際のPRのdiffをレビューさせる、というメタ的な検証がそのまま6時間以内に完結する)
- 見栄え: Claude Codeが出したplanやdiffをブラウザでハイライト・コメントし、そのままエージェントにフィードバックが戻る様子はスクリーンショットで見せやすい。本チャレンジの「朝リサーチ→昼実装→夜レビュー」という運用フロー自体の改善ネタとしても語れる自己言及的な切り口。
- 状態: 未選択

### [2026-10-27] heygen-com/hyperframes — HTML/CSS/GSAPアニメーションを確定的にMP4動画へレンダリングするAIエージェント向けOSS(本日GitHub Trending TypeScriptで言及、HeyGen社が2026年4月にOSS公開)

- 出典: https://github.com/heygen-com/hyperframes
- 概要: HTML・CSS・GSAP/Lottie/Three.js等のアニメーションコードを、ヘッドレスChromeで1フレームずつシークしFFmpegでエンコードすることで、同じ入力から毎回同じ出力のMP4動画を確定的に生成するフレームワーク(Apache-2.0)。CLI・Claude Code向けエージェントスキル・ブラウザ上のスタジオエディタを備え、「HTMLを書くだけで動画になる」ことを謳う。
- 日本語記事件数: Zenn 0件 / Qiita 1件(2026-04-29付の導入記事〈インストール・CLIコマンド・AIコーディングエージェント連携を紹介〉あり) / note 0件(site:検索。Qiitaに基本的な導入記事が1件あるが、独自コンテンツで動画を作り込んで検証した記事は確認した範囲では未検出)
- 検証難易度: 低(Apache-2.0。Node.js 22+とFFmpegのみで`npx hyperframes init`から導入可能。HeyGen社の生成AIメディア連携はオプション機能であり、コアのHTML→MP4レンダリングには外部APIキー不要。GPUも不要)
- 見栄え: 自作のHTML/CSS/GSAPアニメーションから実際にMP4を書き出せるため、「静的なHTMLがそのまま動画になる」というBefore/Afterは視覚的にインパクトがある。本チャレンジのX投稿用シェアカード(`posts/cards/day-NNN.html`)運用を動画版に拡張できるか、という自リポジトリの運用改善ネタとしても語れる。
- 状態: 採用済み(day-030)

### [2026-10-27] Trial by Trace — モデルだけでなく「エージェントハーネス」の信頼性を7要素で評価するベンチマーク論文(Hugging Face Daily Papers上位掲載)

- 出典: https://huggingface.co/papers/2610.32285 (arXiv:2610.32285。TraceLite AI、中国科学院自動化研究所・情報工程研究所、清華大学、北京理工大学)
- 概要: エージェントの性能はモデル本体だけでなく、コンテキスト管理・実行・権限等を担う「ハーネス」にも依存するにもかかわらず既存ベンチマークは最終的なタスク成否しか採点しないという問題意識から、コンテキスト・実行・ガバナンス・ライフサイクル・観測性・ツール・検証の7要素でハーネス自体の信頼性を評価する「TraceTrial-Bench」を提案する論文。実行可能または状態ベースの正解を持つ95の専門家レベルのタスクを用意し、4つのハーネス×9モデルで3,420回の実行を評価したところ、ハーネススコアは59.8%〜72.0%にとどまり、タスク自体には成功していてもハーネス基準の少なくとも1つに失敗していた実行が31.1%あったと報告している。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(公開直後で検索した範囲では日本語紹介記事は未検出)
- 検証難易度: 中(論文本文は「公開プロジェクトリポジトリはタイトルページにリンクされている」と述べているが、Hugging Face上の要約にはコード本体のURLが見当たらず公開状況は着手前に要確認。本リポジトリの方針に沿い、フル再現ではなく論文が挙げる7要素〈コンテキスト・実行・ガバナンス・ライフサイクル・観測性・ツール・検証〉の切り口を使い、Claude Code自身に小さなマルチステップタスクを実行させ、タスク自体の成否とは別に「ハーネス的な失敗」〈権限逸脱・観測性不足等〉が無いかを自作チェックリストで評価する縮小版の概念実証に絞れば、追加APIキー・GPU不要で6時間以内に可能)
- 見栄え: 本リポジトリ自身がClaude Code Routine(まさに1つのエージェントハーネス)で運用されているという自己言及的な文脈に合い、「タスクは成功しても水面下でハーネスが失敗しているケースがある」という論文の指摘を自分のRoutine運用に当てはめて検証できる点が差別化しやすい。公式コードの公開状況次第では概念実証スコープへの絞り込みが必須。
- 状態: 未選択

### [2026-10-27] Thinking-in-Bets at Test Time Reduces Sycophantic Revisions in LLM Agents — ユーザーの反論に折れる前に根拠を記録しておく学習不要の迎合抑制手法(Hugging Face Daily Papers上位掲載、Google)

- 出典: https://huggingface.co/papers/2610.34654 (arXiv:2610.34654、Google)
- 概要: LLMエージェントはユーザーに反論されると正しい作業も撤回してしまいがちだが、単に「反論に屈するな」と指示すると今度は本物の誤りも見逃してしまうというジレンマに対し、ユーザーのフィードバックを読む前に自分の主な主張・それを支える根拠・確信度を非公開で記録しておく学習不要の手法「Thinking-in-Bets」を提案する論文。5種のGeminiモデル×ソフトウェア工学・専門文書作成・学術推論・金融・コマンドライン作業等8ベンチマークで検証し、苦情を受ける前に主張を記録しておくことでパッチレビューにおける誤った撤回をほぼ無くせた一方、苦情を受けた後に記録してもその効果はほとんど回復しないと報告している。確信が低い場合のみ記録することでトークンコストを抑えられるとも述べている。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(公開直後で検索した範囲では日本語紹介記事は未検出)
- 検証難易度: 低(著者コードの公開は確認できず。本リポジトリの方針に沿い、Claude Code自身に小さなタスク〈例: コードレビューや計算問題への回答〉をやらせた上で、正しい回答に対し意図的に誤ったユーザーの反論をぶつけ、「事前に根拠・確信度を記録させる場合」と「記録させない場合」とで誤った撤回〈迎合〉が起きる頻度を比較する縮小版の概念実証なら、追加APIキー・GPU不要で6時間以内に可能)
- 見栄え: 「AIエージェントはユーザーに強く言われると、たとえ自分が正しくても折れてしまう」という身近な失敗を、実際に反論をぶつけるBefore/Afterデモで見せられる。本チャレンジで度々扱ってきたLLMエージェントの信頼性というテーマの新しい切り口(迎合/sycophancy)として差別化しやすい。
- 状態: 未選択

### [2026-10-28] HKUDS/DeepTutor — ドキュメントを丸ごと放り込める個人向けAIチュータリングワークスペース(本日v1.7.0リリース、GitHub Trending Pythonで言及)

- 出典: https://github.com/HKUDS/DeepTutor (香港大学HKUDS発、論文: https://arxiv.org/abs/2604.26962。本日2026-10-28付でv1.7.0をリリース)
- 概要: チャット・クイズ生成・資料読み込み・リサーチ・可視化・習熟度に応じた演習を1つのエージェント型ワークスペースに統合した、個人学習支援AIのOSS(Apache-2.0)。複数のモードが知識ベース・メモリ・学習コンテキストを共有し、メモリはファイルベースで人間が内容を確認・編集できる設計。マルチエンジンRAG・Web検索・学術論文データベース検索・Pythonコード実行・サブエージェントを統合する。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(hyper.aiに論文要約の日本語記事が1件あるが、Zenn/Qiita/noteでの検証記事は検索した範囲では未検出)
- 検証難易度: 低〜中(Apache-2.0。Docker1コマンドまたは`pip install -U "deeptutor[full]"`で導入可能。モデルプロバイダは設定画面で選ぶ必要があり、クラウドAPIキーを使わず無料検証するにはOllama等のローカルモデル接続が前提になる見込み。埋め込み・Web検索は任意機能で未設定でも基本動作は確認できる。GPU不要〈ローカルモデルを使う場合は実行速度に影響する程度〉)
- 見栄え: 自作の資料〈PDF等〉を読み込ませてクイズ生成・要点解説・習熟度演習までを一通り試し、生成されたクイズや解説のスクリーンショットでBefore(手動で資料を読む)/After(DeepTutorに読ませて対話的に学ぶ)を見せやすい。本日付けの新バージョンリリースというニュース性もある。
- 状態: 未選択

### [2026-10-28] obra/superpowers — 「ブレインストーミング→計画→TDD実装→レビュー」をエージェントの既定動作に組み込むスキル集・開発方法論(本日GitHub Trending Shellで言及)

- 出典: https://github.com/obra/superpowers (Jesse Vincent氏作、MIT)
- 概要: Claude Code/Codex/Cursor/Gemini CLI/GitHub Copilot CLI/OpenCode/Pi向けのスキルフレームワーク兼開発方法論。コーディングエージェントが要件確認を飛ばして実装に走る問題に対し、ブレインストーミングで設計を固める→詳細な計画を書く→git worktreeで分離した環境でテスト駆動開発により実装→コードレビューを依頼→ブランチを完了する、という7段階のワークフローをスキルとして自動的に発火させる。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出。英語・ポルトガル語の紹介記事は多数あり、GitHub star数は記事により4万〜30万超までばらつきがあるほど急伸中)
- 検証難易度: 低(MIT。Claude Codeでは`/plugin marketplace add obra/superpowers-marketplace`→`/plugin install superpowers@superpowers-marketplace`で導入でき、追加の有料APIキー・GPU不要。導入前後で同じ曖昧な実装依頼をClaude Code自身に与え、ブレインストーミング・計画書・TDDの有無など振る舞いの差をBefore/Afterで比較するだけで6時間以内に完結する)
- 見栄え: 本リポジトリ自身がClaude Code Routineで運用されているという自己言及的な文脈に合い、「導入前は即実装に走るが、導入後は設計確認→計画書作成→TDDを経る」という振る舞いの変化を具体的なログで示しやすい。本チャレンジで既に扱ったhallmark・last30days-skill・obsidian-second-brain等の個別スキルとは異なり、「開発プロセス全体の方法論」という切り口で差別化できる。
- 状態: 未選択

### [2026-10-28] Memory Tax: Dissecting the Net Value of Agent Memory — 複雑なエージェントメモリは素朴なRAGに負けることが多いと実証した論文(Hugging Face Daily Papers本日掲載)

- 出典: https://huggingface.co/papers/2610.34073 (arXiv:2610.34073。清華大学・UIUC・人民大学・Waterloo大学・Verdent.ai等)
- 概要: フラット型・階層型・グラフ型・学習済みポリシー型の10種のエージェントメモリシステムを、会話履歴に直接検索をかける素朴なRAGと比較し、多くのメモリシステムがRAGの素のスコアを下回ると報告した論文。メモリがRAGの取りこぼしに答えられる「利益」と、RAGが答えられる設問にメモリが負ける「税(tax)」に分解し、税の原因を構築時の忠実性・検索のしやすさ・バックボーン変更への頑健性の3観点で分析する。LongMemEval-s・PersonaMem-v2・MINT-Evalで検証し、IDF-keywordが50%超、RAG-Hybridが約70%のスコアに達する一方、メモリシステムはそれを下回るケースが多いと報告。ALFWorld/WebShop等の経験メモリ・ワールドモデルメモリでも同様の傾向が見られるとしている。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出。公開直後の論文)
- 検証難易度: 中(著者コードの公開リンクは論文ページ上で確認できず。フル再現は複数バックボーン〈Qwen3.5-4B等〉と複数ベンチマークが前提で非現実的。本リポジトリの方針に沿い、Claude Code自身に小規模な自作の会話履歴を与え、「素朴に履歴全文から検索して答える」場合と「要約・独自メモリ構造を介して答える」場合とで、RAGが答えられる設問にメモリ側がむしろ間違える「税」が実際に起きるかを比較する縮小版の概念実証に絞れば、追加APIキー・GPU不要で6時間以内に検証可能)
- 見栄え: 「メモリを賢くしようとすると、素朴な検索より性能が落ちることがある」という直感に反する結果を、具体的な設問と誤答例で示せると説得力がある。本チャレンジで既に扱ったREMORY等の「エージェントメモリ/コンテキスト圧縮」系の流れに、「そもそもメモリは素朴なRAGに勝てているのか」という懐疑的な切り口を加えられる。
- 状態: 未選択

### [2026-10-28] nightly-labs/openbot — 複数デバイス・複数エージェント(Claude Code/Codex/Grok等)を横断管理するローカルファーストのデスクトップワークスペース(本日GitHub Trending TypeScriptで言及)

- 出典: https://github.com/nightly-labs/openbot (Synthetify Labs発)
- 概要: Codex/Claude Code/Grok/OpenCode/Gemini/Cursor CLI/Cline CLI等のエージェントそれぞれに専用ワークスペースと会話を持たせ、ローカルのメッセージキュー・ファイル転送・組み込みブラウザ・エージェント間メッセージングを1つのデスクトップアプリに統合するプロジェクト(0.1.11まではApache-2.0、以降はPolyForm Noncommercial 1.0.0で商用利用は別途ライセンスが必要)。「development preview」段階で、エージェントは`danger-full-access`かつ承認なしで動く設計である点に注意が必要。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出)
- 検証難易度: 高(既存のローカルCLIログインを再利用する設計のため追加の有料APIキーは必須ではなく、OpenCodeの無料モデルを使えば無料枠内で検証できる見込みだが、本体はmacOS/Windows/LinuxのデスクトップGUIアプリ〈Electron系〉が前提で、GUIの無いクラウドRoutine実行環境では起動・操作ができない可能性が高い。Dockerイメージ〈ghcr.io/nightly-labs/openbot〉やLinuxサーバー向けインストールスクリプトがGUI無しで何を提供するかは着手前に要確認。GPU不要)
- 見栄え: 「複数のエージェントCLIを1つのアプリから横断管理し、エージェント同士がメッセージをやり取りする」様子はスクリーンショット映えしやすいが、GUI必須という性質上、Routine環境での検証が構造的に難しい。採用する場合はCLAUDE.mdの「Routine環境の制約」エスカレーションルールに従い、早い段階でGUI起動可否を確認し、不可であればPR本文冒頭に「ローカル検証が必要」と明記して人間に引き継ぐ想定で進める必要がある。
- 状態: 未選択

### [2026-10-29] RealCLI — CLIエージェントの「タスク成功」と「人間との協働品質」を分けて評価するベンチマーク(Hugging Face Daily Papers上位掲載、IQuest/北京航空航天大学/人民大学)

- 出典: https://huggingface.co/papers/2610.22507 (arXiv:2610.22507。GitHub: https://github.com/RealCLI-Team/RealCLI-Benchmark-v1.0 、データセット: https://huggingface.co/datasets/RealCLI-Team/RealCLI-Benchmark-v1.0)
- 概要: CLIエージェントを、仕様を最初に全て与える「REALCLI-EXEC」モードと、情報を小出しにしたり途中で訂正・権限確認を挟んでくる台本付きユーザーと対話させる「REALCLI-COLLAB」モードの両方で評価し、タスク実行の成否(最高49.2%)と人間との協働品質(5観点・22副観点、最高でも37.6%)が食い違うことを示すベンチマーク論文。steerability(指示の受け入れやすさ)・信頼の調整・安全境界の管理が特に弱いと報告している。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(公開直後で検索した範囲では日本語紹介記事は未検出。似た名称の別ベンチマークLongCLI-Benchの日本語要約はあるが本論文とは別物)
- 検証難易度: 低〜中(GitHubにベンチマークコード、Hugging Faceにデータセットが公開済み。フルベンチマークの全シナリオ実行は非現実的なため、本リポジトリの方針に沿い、REALCLI-COLLABの一部シナリオ〈情報の小出し・途中訂正・権限確認〉を抜粋し、本リポジトリの検証対象でもあるClaude Code自身をCLIエージェントとして動かして比較する縮小版の概念実証に絞れば、追加の有料APIキー・GPU不要で6時間以内に可能)
- 見栄え: 「タスクには成功したのに、人間との協働の仕方(指示の聞き方・安全確認)は実は下手だった」という具体的な対話ログを示せると説得力がある。本リポジトリ自身がClaude Code Routineという1つのCLIエージェントで運用されている自己言及的な文脈にも合う。
- 状態: 未選択

### [2026-10-29] What Effort Level Should I Choose? — LLMエージェントの「推論努力(reasoning effort)」の経済性を検証した論文(Together AI、Hugging Face Daily Papers掲載)

- 出典: https://huggingface.co/papers/2610.34491 (arXiv:2610.34491。Together AI、Johns Hopkins大学、Cornell大学)
- 概要: 高い推論努力(effort/thinking budget)を固定で使うことが必ずしも得にならず、低努力で解けるタスクをむしろ高努力側が失敗したり、簡単なタスクでもコストだけ上がったりすることを示した論文。タスクごとに低努力から始め、失敗チェックを経てからのみ努力を上げる方式の方が、固定で最高努力を使うより低コストで同等以上の性能を出せると報告している。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出。類似テーマの別論文「Ares」等はあるが本論文自体の日本語記事は未検出)
- 検証難易度: 低(著者コードの公開は確認できていないが、本リポジトリの方針に沿い、本Routineが使っているAgentツール自体が備える`effort`パラメータを使って同一タスクを異なる努力レベルで実行し、成功率・コスト(概算トークン量)・解法の違いを比較する縮小版の概念実証なら、追加の有料APIキー・GPU不要で6時間以内に可能)
- 見栄え: 本チャレンジの実装・リサーチRoutine自身が使っているAgentツールの`effort`設定を題材にできるため極めて自己言及的で分かりやすい。「努力を上げたのに逆に失敗した」という具体例が取れれば訴求力が高い。
- 状態: 未選択

### [2026-10-29] thedotmack/claude-mem — Claude Code等のコーディングエージェントにセッションを跨いだ永続メモリを与えるOSSプラグイン(本日GitHub Trendingで言及)

- 出典: https://github.com/thedotmack/claude-mem
- 概要: Claude Code/Codex/Gemini CLI等のセッション中のツール操作・ファイル編集をライフサイクルフックで記録し、AIで圧縮してSQLite+Chroma(ベクトル検索)に保存、次回セッション開始時に関連する記憶を自動的に注入するOSSプラグイン(Apache-2.0)。
- 日本語記事件数: Zenn 1件以上(Mem0との比較記事がZenn発として確認できた) / Qiita 0件(検索した範囲) / note 0件(検索した範囲)。導入ガイド的な日本語記事は複数あるが、自分で使い込んで検証した記事は確認した範囲では見当たらない。
- 検証難易度: 低(Apache-2.0。`npx claude-mem install`、またはClaude Codeプラグインとして`/plugin marketplace add thedotmack/claude-mem`で導入可能。既定ではセッション観測の圧縮にAnthropicプランのトークンを使う設計だが、`CLAUDE_MEM_ONLINE_OPTIN=false`等でサインインをスキップする経路もあり追加の有料APIキーは必須ではない。GPU不要)
- 見栄え: 本リポジトリ自身がまさに「Claude Code Routineでセッションを跨いで作業する」運用をしているため、導入前後でRoutineが前の文脈をどれだけ覚えているかのBefore/After比較が作りやすい自己言及的な切り口。日本語記事が既にあるため、採用する場合は「自分のRoutine運用への適用」という独自の切り口を明記した方がよい。
- 状態: 未選択

### [2026-10-29] KeygraphHQ/shannon — ソースコード解析とブラウザ自動操作で実際に攻撃を再現する自律型AIペネトレーションテスターOSS(本日GitHub Trending TypeScriptで言及)

- 出典: https://github.com/KeygraphHQ/shannon
- 概要: Webアプリ/APIのソースコードを解析して攻撃経路を特定し、ブラウザ自動操作とCLIツールで実際に攻撃を再現した上で、動作するPoCが取れた脆弱性のみを報告する自律型AIペネトレーションテストOSS「Shannon Lite」(AGPL-3.0)。READMEで「自分が所有する、または明示的な許可を得た環境にのみ実行すること」と明記されている。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語紹介記事は未検出。英語のニュース記事・ブログはあり)
- 検証難易度: 中(Docker・Node.js 18+・AIプロバイダの認証情報が必要。第三者の許可を得る必要がなく自己責任で検証できるよう、ローカルで自分で立てたOWASP Juice Shop等の意図的に脆弱なデモアプリのみを対象にする。モデルは既存のAnthropicキーまたはローカルOllama等を利用できる見込みで追加の有料APIキーは必須ではない。README記載で1回のフルスキャンは1〜1.5時間程度のため6時間以内に収まる。GPU不要)
- 見栄え: 「ソースコードから攻撃経路を見つけ、実際にPoCを取る」様子を、意図的に脆弱なデモアプリ相手に再現し、検出されたPoCのログをそのまま見せられる。本チャレンジでは新しい切り口である「AIエージェントによる攻撃的セキュリティ検証」として差別化できる。検証対象は必ず自分でローンチしたローカルの脆弱デモアプリのみとし、第三者のサイトには向けない。
- 状態: 採用済み(day-032)。Routine実行環境の制約(自動実行モードの安全装置がnpx経由の外部パッケージ実行をブロック)でShannon本体の実行には進めず、ローカル検証待ち。詳細は`experiments/day-032/`参照。

### [2026-10-30] lightpanda-io/browser — Chromium/WebKitに依存せずゼロから書かれた、AIエージェント専用ヘッドレスブラウザ(本日GitHub Trending Zigで言及)

- 出典: https://github.com/lightpanda-io/browser (本日GitHub Trending Zigで+652star/日、総スター数は約38.3k)
- 概要: ChromiumやWebKitのフォークではなく、AIエージェント・自動化向けにゼロから書かれたヘッドレスブラウザ。JS実行にV8、HTML解析にhtml5everを使いつつDOM・ネットワーク・レイアウトは自前実装。CDP/WebDriver BiDi/MCPサーバー/内蔵エージェントモードで操作でき、公式ベンチマークではヘッドレスChrome比で約16倍少ないメモリ・約9倍速い実行を主張(AGPL-3.0)。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(dev.to等の英語記事・ブログは複数あるが日本語の紹介・検証記事は検索した範囲では未検出)
- 検証難易度: 低〜中(Linux/macOS向けビルド済みバイナリ・Dockerイメージあり。コア機能〈ブラウジング・CDP/MCPサーバー〉は有料APIキー不要。`lightpanda agent`機能のみ有料LLMプロバイダのAPIキーか、Ollama/llama.cppでのローカルモデルで代替可能。GPU不要。ライセンスがAGPL-3.0のため検証内容を記事にする際は利用条件を明記すること)
- 見栄え: 「本当にヘッドレスChromeより軽い/速いのか」をメモリ使用量・実行時間の実測比較で見せられる。本リポジトリが過去(day-012)に直面した「Routine実行環境にブラウザが無い」制約への代替策候補としても自己言及的な意味を持つ。
- 状態: 未選択

### [2026-10-30] Broken on Arrival — 公開モデルレジストリ上で「中身は壊れていないのにタスクを解けない」量子化LLMアーティファクトの実態調査と検出ツール(論文, arXiv:2609.05881)

- 出典: https://arxiv.org/abs/2609.05881 (現行タイトルは"Non-Functional Quantized LLM Artifacts in Public Model Registries and How to Catch Them"。コード・データ: https://github.com/aditi-p31/quantcheck 〈v3.4〉。Hugging Face Daily Papers掲載)
- 概要: Ollama公式ライブラリ305件+Hugging Face上の人気コミュニティ量子化GGUFアーティファクト22件、計327件に対しHumanEval+ベースの機能検査(`quantcheck`)を実行。164タスクのフル実行では、Ollama公式タグのうち7件(`qwen2.5-coder:3b-instruct`のq2_K/q3_K_S/q3_K_M/q3_K_L、`phi3.5:3.8b-mini-instruct-q2_K`、`llama3.2:1b-instruct`のq2_K/q3_K_S)が164問中0〜6問しか解けない「機能しない」状態だったと報告。**ただし初版(v1)が主張した「サイレントな欠陥〈壊れたファイル〉」という診断はv3で訂正されている。** Qwen2.5-Coder-3B系・phi3.5系はオリジナルのチェックポイントから著者が再ビルドしてもビット単位で一致する正規の(無calibrationの)低bit量子化であり、ファイル自体は壊れていない。むしろ「無calibrationの低bit量子化によって性能が実質ゼロまで崩壊する」現象であり、importance matrix(calibration)を使った量子化に変えると同じ3Bモデルの一部タグで0→76〜113問(164問中)まで回復したという。phi3.5の欠陥主張自体は2026-09-10付でOllama側Issue(ollama/ollama#18252)上で撤回されている。llama3.2-1B系2タグは再ビルド検証が未実施で原因未特定のまま「機能しない」。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語記事は未検出)
- 検証難易度: 低〜中(`quantcheck`はMITライセンスのPythonツール〈Python 3.9+、ローカルOllama、EvalPlus 0.3.1が必要〉、監査データセットはCC BY 4.0。追加の有料APIキー不要。論文が指摘した具体的なタグ〈3Bクラス〉をOllamaから実際にpullして`quantcheck`のスモークテスト〈15タスク〉を回すだけなら、GPU無し・CPU推論でも6時間以内に再現可能)
- 見栄え: 「ダウンロードもロードもトークン生成もできるのに、実質タスクを解けないモデルを掴んでしまう」という具体的なタグ名を挙げて実際に再現できれば読者への実利が大きい。かつ「壊れたファイルだと思ったら実は無calibration量子化の性能崩壊だった」という訂正の経緯自体が、検証記事にそのまま使える誠実な「失敗から学ぶ」ストーリーになる。記事化の際は撤回済みの「サイレントな欠陥(壊れたファイル)」という初版の診断を事実として書かないこと。
- 状態: 採用済み(day-033)

### [2026-10-30] CopilotKit/OpenBot — 「各エージェントに自分専用のコンピュータを持たせる」ガバナンス付きAIコワーカー基盤(本日GitHub Trending TypeScriptで言及、要有料APIキー)

- 出典: https://github.com/CopilotKit/OpenBot (本日GitHub Trending TypeScriptで+707star/日、総スター数は約8.8k。CopilotKit公式、ベータ版)
- 概要: LangGraph/Mastra/CrewAI/Pydantic AI/Google ADK等、AG-UI対応の任意のフレームワークで作ったエージェントを「コワーカー」として受け入れ、各コワーカーに専用のブラウザ・ファイル・ツールを与え、ツール実行をポリシーゲートウェイが実行前に許可判断・実行後に記録するセルフホスト型プラットフォーム(MIT)。「プロダクトではなくテンプレート」として、General Assistant/Knowledge/Risk Analystの3種のコワーカー例を同梱。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲では日本語記事は未検出)
- 検証難易度: 高・**有料APIキー必須**(クイックスタートで`OPENAI_API_KEY`が必須〈LangGraphエージェントはAnthropic/Googleキーでも代替可〉。加えてCopilotKit Intelligenceのプロジェクト/ライセンス〈無料枠ありだがセルフホストも要設定〉、Docker、Bun 1.4+、PostgreSQLが必要で、セットアップが重い。本リポジトリの方針〈当面は有料APIキー必須の候補をtoday.mdでは選ばない〉により、現時点では選択しない)
- 見栄え: 「各コワーカーが専用のブラウザ・権限を持ち、ツール実行がポリシーゲートウェイに記録される」様子はデモ映えするが、上記の理由で当面は見送り候補。将来、有料APIキー運用方針を変更する場合の候補として記録のみ残す。
- 状態: 未選択

### [2026-10-31] Matched Capabilities, Different Behaviors — 同じ機能でもMCP経由かCLI経由かでAIエージェントの挙動が大きく変わることを統制実験で示した論文(HF Daily Papers掲載)

- 出典: https://arxiv.org/abs/2610.34298 (HF Daily Papers 2026-10-30掲載。Zhenning Shi, Liang Pang, Yongqi Li著。コード: https://github.com/ModalityDance/MICA、プロジェクトページ: https://modalitydance.github.io/MICA/)
- 概要: MCP/CLIという2つのインターフェースを同一の「意味論的アクション契約」から機械的に生成する評価フレームワークMICAを用い、6モデル×3環境(ALFWorld/WebShop/ScienceWorld)で比較したところ、2,004エピソードの94.3%でペアとなる実行軌跡が分岐したと報告。インターフェース固有のフォーマット不整合を修復する手法DART(Decoupled Action Realization and Targeted Repair)を提案し、全6設定でベンチマークスコアを最大9.0点改善、MCP側のトークンコストを最大27.1kトークン/タスク削減したという。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲。英語のMCP vs CLI比較記事は複数あるが本論文自体を扱った日本語記事は未検出)
- 検証難易度: 中〜高。MITライセンスでGitHubに`mica run --interface mcp`/`--interface cli`の比較コードあり。ただし公式ベンチマークのフル再現にはローカルvLLM(GPU必須)またはDeepSeek/Gemini等の有料APIキーが必要で、本リポジトリの「有料APIキー必須の候補は選ばない」方針に抵触する。縮小版として、Claude Code自身にCLI的なツール呼び出しとMCP的なツール呼び出しを模した小規模タスクを与え、挙動・トークン消費の違いを定性的に観察する独自の概念実証なら追加キー・GPU無しで6時間以内に可能。
- 見栄え: 本チャレンジの実行基盤(Claude Code)自体が題材になるため自己言及性が強い。「ツールの見せ方だけでエージェントの振る舞いが変わる」という具体例を自分のRoutine運用から取れれば説得力が高いが、フル再現ではなく概念実証に絞る旨を記事で明記する必要がある。
- 状態: 未選択

### [2026-10-31] pbakaus/impeccable — AIコーディングエージェントが生成するUIの「いかにもAI感」を62の決定的ルールで検出するツール(本日GitHub Trendingで言及)

- 出典: https://github.com/pbakaus/impeccable (元Google Developer Advocate・jQuery UI作者のPaul Bakaus氏。Anthropic公式の`frontend-design`スキルを土台に拡張)
- 概要: Apache-2.0。LLM・API不要の62個の決定的ルールで、詰まったパディングや見出しレベルのスキップ等の「AIっぽい」デザインパターンを検出する。`npx impeccable detect`でソースディレクトリやURLをスキャンしJSON出力・GitHub Actionsアノテーションに対応、ライブモードではdevサーバー上でUI要素のバリアント比較・適用もできる。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲。中国語・ドイツ語・フランス語・韓国語の紹介記事は複数あるが日本語の紹介・検証記事は未検出)
- 検証難易度: 低。検出器(`detect`コマンド)はAPIキー・LLM不要でNode.jsのみで動作し6時間以内に十分検証可能。GPU不要。
- 見栄え: 本リポジトリの`posts/cards/day-NNN.html`(自前のシェアカードHTML)を`impeccable detect`で実際にスキャンし、指摘された項目をBefore/Afterで見せる自己言及的な切り口が作れる。追加の有料キー不要で本リポジトリの方針にも合う。
- 状態: 未選択

### [2026-10-31] Soft-MTP — 多トークン予測の学習勾当からノイズ残差だけを1行のコード変更で除去する論文(HF Daily Papers掲載)

- 出典: https://arxiv.org/abs/2610.38331 (HF Daily Papers 2026-10-30掲載。コード・学習済みチェックポイント: https://github.com/JaydenTeoh/Soft-MTP)
- 概要: 標準的な多トークン予測(MTP)の学習勾当に「有用な自己蒸留信号」と「学習を害するノイズ残差」が混在していることを示し、straight-through gradient routingによりKL自己蒸留信号のみを取り出すSoft-MTPを提案。167M〜1.2Bパラメータで検証し、次トークン困惑度の低下・自己投機的デコーディングの高速化・ゼロショット精度向上を報告、パラメータ追加なし・計測可能なオーバーヘッドなしの「フリーランチ」と主張している。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲。MTP自体の英語解説記事は多いが本論文〈Soft-MTP〉自体の日本語記事は未検出)
- 検証難易度: 中〜高。MITライセンスで学習済みチェックポイント(NTP/MTP/Soft-MTP版)がHugging Face上に別途公開されており、ゼロから学習せず推論のみ(困惑度・自己投機的デコーディング速度の比較)なら検証の余地がある。GPU不要・APIキー不要だが、167MモデルでもCPU推論には相応の時間がかかる見込みで6時間に収まるかは当日のスモーク版の絞り方次第。
- 見栄え: 直近がエージェント/ツール系の候補に偏っているため、純粋なモデル学習手法の論文として多様性を持たせられる。公開済みチェックポイント同士(MTP版 vs Soft-MTP版)の困惑度・デコーディング速度を自分で測って比較するBefore/Afterが学習コストをかけずに作れる。
- 状態: 未選択

### [2026-10-31] Orkas-AI/Orkas — Commanderエージェントが16種の専門エージェント・外部CLIエージェントに作業を振り分けるローカルファーストのマルチエージェント司令塔デスクトップアプリ(本日GitHub Trending JavaScriptで言及)

- 出典: https://github.com/Orkas-AI/Orkas (MIT。スター数6.1k、フォーク367)
- 概要: 1つのCommanderエージェントが目標をタスクに分解し、16種の内蔵専門エージェントとClaude Code/Codex等の外部CLIエージェントに作業を振り分けるローカルファーストのデスクトップAIチームアプリ。プロジェクト単位で目標・メモリ・ファイルを会話を跨いで保持でき、定期自動化(スケジュール実行)にも対応。パッケージ版は内蔵モデル用の無料クレジット500分付きでサインインすれば追加APIキー無しで試せ、ソースビルドはローカルOpenAI互換エンドポイントに向ければ完全オフラインでも動作するとREADMEに明記されている。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲)
- 検証難易度: 低〜中。無料クレジットまたはローカルOpenAI互換エンドポイント(Ollama等)を使えば追加の有料APIキー無しで6時間以内に検証可能。GPU不要(ローカルモデル使用時はそのモデル側の要件に依存)。パッケージ版はサインイン必須な点に留意。
- 見栄え: 「Commanderが目標をどう分解し、どの専門エージェントに何を振るか」を実際のログで見せられる。直近数日(claude-mem、superpowers、KeygraphHQ/shannon、nightly-labs/openbot等)でエージェントオーケストレーション系ツールが連続しているため、採用する場合はローカルファースト・無料クレジットでの検証という切り口での差別化を明記した方がよい。
- 状態: 未選択

### [2026-11-01] Claude Code Game Studios — Claude Codeを49体のAIエージェント・74スキルによる「ゲーム開発スタジオ」に変える構成テンプレート(本日GitHub Trendingで言及)

- 出典: https://github.com/Donchitos/Claude-Code-Game-Studios (MIT。本日GitHub Trending Shellで言及)
- 概要: Claude Codeの1セッションを、Director/部門リーダー/専門職の3階層・49体のエージェント、74個のスラッシュコマンド形式スキル、15個のフック(自動検証)、14個のパス限定ルール、62個のドキュメントテンプレートからなる「ゲーム開発スタジオ」として動かすMITライセンスのテンプレート。Godot 4/Unity/Unreal Engine 5に対応し、`/start`で状況を聞かれてワークフローに誘導される。README自身が「パースチェックは実行確認ではない」「画面の変化を伴う修正は、実際にゲームを起動しスクリーンショットを`production/qa/evidence/`に残すまで完了としない」と強く検証を要求している点が特徴。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲。英語のdev.to記事や中国語ミラー(Gitee)は複数あるが日本語の紹介・検証記事は未検出)
- 検証難易度: 低。Claude Code自体の認証以外に追加のAPIキー・GPUは不要。ただしフルのゲーム開発サイクルは6時間に収まらないため、`/setup-engine godot`等で環境を作った上で1〜2個のスキル(例: `/brainstorm`、`/skill-test static`)に絞って動かすスコープが必要。
- 見栄え: 本リポジトリ自体がClaude Code Routineで運用されているという自己言及的な文脈に合う。49エージェント・74スキルという大規模な構成を実際に動かし、ログやスクリーンショットをそのまま見せられる。
- 状態: 未選択

### [2026-11-01] AiSOC — ローカルLLM(Ollama)で動く自己ホスト型AI Security Operations Center(本日GitHub Trending Pythonで言及)

- 出典: https://github.com/beenuar/AiSOC (MIT。Cyble社の資金提供で公開)
- 概要: セキュリティテレメトリを取り込み、7,015件中2,534件が実行可能な検知ルールでアラートを相関・インシデント化し、AIエージェントが推論過程・ツール呼び出しを全てログに残しながら調査、最終的な対応は人間が承認するセルフホスト型AI SOC。MCPサーバーも同梱。既定では追加の有料APIキー不要で、CPU専用推論向けにサイズ調整された約2GBのローカルモデル(Ollamaの`llama3.2:3b-instruct-q4_K_M`)が同梱される。README自身が「ベンチマーク数値はライブなエージェント精度ではなく基盤の自己一貫性の指標」「既定では自律動作しない」「SIEMの代替ではない」と明記している。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲)
- 検証難易度: 低〜中。Docker Compose v2(Dockerに8GBメモリ・20GB空き容量)+Python 3.9+のみで、`make up`→`make smoke`(パイプライン全体を1イベントで通し10/10 PASSのログが出る)→サンプルデータ投入まで一通り確認できる。追加APIキー不要・GPU不要(CPU専用)。
- 見栄え: `make smoke`のPASS/FAILログと、サンプルインシデントに対するAIエージェントの調査過程(監査可能なInvestigation Ledger)を具体的に見せられる。セキュリティ運用×AIエージェントという切り口で直近のdefensive security文脈にも合う。
- 状態: 未選択

### [2026-11-01] shiyu-coder/Kronos — 金融ローソク足(K-line)データ専用のOSS基盤モデル(本日GitHub Trending Pythonで言及、元論文はAAAI 2026採択)

- 出典: https://github.com/shiyu-coder/Kronos (MIT。元論文: arXiv:2508.02739「Kronos: A Foundation Model for the Language of Financial Markets」、AAAI 2026採択。本日GitHub Trending Pythonで+611star/日)
- 概要: 価格変動と取引活動の両方を保持する専用トークナイザでOHLCVデータを離散トークン化し、45の取引所から集めた120億件超のK-lineで自己回帰的に事前学習したデコーダのみの基盤モデル群(mini 4.1M/small 24.7M/base 102.3Mはオープン、largeは非公開)。Hugging Face Hubから`NeoQuasar/Kronos-small`等をロードするだけで推論でき、著者らは既存のTSFM(時系列基盤モデル)比でRankICが93%向上したと報告している。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲。英語論文・海外プラットフォームの紹介は複数あるが日本語記事は未検出)
- 検証難易度: 低。`pip install`後、Hugging Face Hubからsmall/baseモデルをロードして`predict`するだけで追加APIキー不要・GPU不要(CPUで動作、GPUは任意)。ただしREADME付属のサンプルCSV(`./data/XSHG_5min_600977.csv`)はリポジトリに同梱されていないため、自前で株価・為替・暗号資産等の実際のOHLCV CSVを用意する必要がある。
- 見栄え: 自分で用意した実際の相場データに対する予測チャートと、ground truth(実際の値動き)を重ねたBefore/Afterが分かりやすい。直近のエージェント系候補に偏っていたため、純粋な時系列基盤モデルとして多様性を持たせられる。投資助言ではなく検証目的であることを明記する必要あり。
- 状態: 未選択

### [2026-11-01] Co-Design Bench — 画像・音声・文書など実際のマルチモーダル依頼に対するコーディングエージェントの対応力を測るベンチマーク(論文, arXiv:2610.35138)

- 出典: https://arxiv.org/abs/2610.35138 (Fudan大学・Alibaba Token Hub・上海交通大学ら。データセット: https://huggingface.co/datasets/Wiselnn/Co-Design-Bench〈Parquet, testスプリット96件+ルーブリック521件〉。プロジェクトページ: https://codesignbench.github.io/)
- 概要: 37,463件の実クエリ・26,314件の実セッションから抽出した273タスク(本リポジトリで確認できた公開データセットはそのサブセットの96件)で、ローカライズされた編集+画像/音声/動画/文書等の添付ファイルを伴う「Multimodal Editing」と複数ファイルに渡る「Repository Editing」の2トラックを評価するベンチマーク。各タスクに隠された専門家作成の採点基準(合計2,331件)を用意し、LLMが採点した上で別のLLMが過大判定を検証する「judge-then-refute」方式を採用。著者らの実験では最良のモデルでも採点基準の平均69.9%しか満たせず、タスク完全成功率は26.4%に留まったと報告している。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲)
- 検証難易度: 中〜高。テストタスクとルーブリックはHugging Face上にParquetで公開されているが、論文の評価ハーネス(judge-then-refuteの実装)自体のコードは検索した範囲では見つからず、フル再現は不可。縮小版として、96件から1〜2タスクを選びClaude Code自身に解かせ、付随するルーブリックを人力で採点するという概念実証なら追加APIキー・GPU不要で6時間以内に可能。
- 見栄え: 画像・文書等の添付ファイルを伴う実際のWeb開発依頼にエージェントがどこまで応えられるかを、具体的な1タスクのBefore/Afterで見せられる。
- 状態: 未選択

### [2026-11-01] WorkFactory / WorkPilot — 職業タスクをエージェント訓練用の実行可能タスクに変換するフレームワーク(論文, arXiv:2610.37161。要追加調査・見送り推奨)

- 出典: https://arxiv.org/abs/2610.37161 (Zhejiang大学・人民大学ら。コード: https://github.com/IQuestLab/WorkFactory, Apache-2.0)
- 概要: 専門職の依頼(プロフェッショナルインテント)から、必要な情報とその情報が置かれるべき場所を対応付ける「情報レベルの計画」を作り、実際に実行してみて環境の不備を見つけ、意図した作業内容を変えずに修復するWorkFactoryフレームワークを提案。612職種・112,686タスクを構築し、教師の実行軌跡でQwenベースのWorkPilotファミリー(4B/27B/35B-A3B)をファインチューンしたところ、いずれもベースモデルを上回り、WorkPilot-35B-A3BはGDPval-AA v2.1のEloが879から1565に上昇したと報告している。
- 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(検索した範囲)
- 検証難易度: 高・要追加調査(現時点では見送り推奨)。GitHubリポジトリにはLICENSE以外の実体がなく、タスクデータ・WorkPilotモデル重みへの具体的なダウンロードURL・実行コマンドが見当たらない(確認した範囲ではHugging Face上の実体を別途探す必要がある)。着手前にモデル重みの有無・サイズ・GPU要否を確認しないと6時間以内に収まるか判断できない。
- 見栄え: 「職業タスクをそのままエージェント訓練データに変換する」という切り口自体は面白いが、再現可能性の不確実性が高く、今回は参考記録として残すのみとする。
- 状態: 未選択
