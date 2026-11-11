# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 045
- 選んだ候補(backlog.mdのタイトルかURL): Deletion Tuning(Bit-Mask Tuning)論文 — https://huggingface.co/papers/2611.10866
- 補足メモ(あれば):
  - 出典: https://huggingface.co/papers/2611.10866 (Hugging Face Daily Papersで本日トレンド上位。arXiv: 2611.10866。コード: https://github.com/agentic-learning-ai-lab/deleting-weights 〈MIT〉、プロジェクトページ: https://agenticlearning.ai/deleting-weights/ 、学習済みマスク: https://huggingface.co/Jacklu0831/deletion-tuning-masks 。著者: Jack Lu, Zhenbang Yang, Mike Lasby, Tejas Pote, Yani Ioannou, Mengye Ren。NeurIPS/ICML 2026にも掲載)。本エントリはbacklog.md側では2026-11-11付研究PR(#152、本記事作成時点で未マージ)に記載されている。backlog.mdへの反映が先にマージされていなくても、本todayエントリの情報だけで検証に着手できるよう以下に詳細を再掲する。
  - 概要: 事前学習済みLLMにどれだけ変更を加えれば新しい能力を獲得できるかを問う論文。Transformerブロックのgate projection上にバイナリマスクを学習し、全体の0.05%未満の重みを0にするだけ(他の変更なし)で、強化学習(RLVR)・SFT・on-policy distillationにおいてフルファインチューニング(FFT)と同等の性能になることを示した。学習後のマスクはFFT済みチェックポイントより数百〜数千倍小さく、継続学習で重要な「忘却の少なさ」でもLoRAやランダムスパースファインチューニングより優れる(RLでは旧タスク精度がベースモデル付近を維持する一方、FFT/LoRA/ランダムスパースFTは最大5.4ポイント低下)と報告している。
  - 導入方法の選択肢・検証範囲の絞り方: リポジトリは学習(GRPO/SFT/SDFT)用の重い環境構築(flash-attention・vLLM・verl等、CUDA前提)を要求するが、`src/apply_mask.py`で公開済みの学習済みマスクをベースモデルに適用するだけなら、学習用の重い依存関係は不要でTransformers+PyTorchのみで足りる見込み。本検証はフルSFT/RLVR学習の再現ではなく、**公開済みマスクの適用と評価**に絞る。
    - 第一候補: `sft/llama-3.2-1b-instruct-mmlu-pro`(ベースモデル`meta-llama/Llama-3.2-1B-Instruct`)。パラメータ数が最小(1B)でCPUでも推論が現実的。ただしLlamaはHugging Face上でゲート付き(利用規約への同意が必要)のため、Routine実行環境のHFアカウントで即座にアクセス許可が下りない可能性がある。
    - 第二候補(ゲート回避用フォールバック): `sdft/qwen2.5-7b-instruct-toolalpaca` または `grpo/qwen2.5-7b-simplerl-zoo`(ベースモデル`Qwen/Qwen2.5-7B`系、ゲート無し・オープンに取得可能)。7Bのため推論速度はLlama-3.2-1Bより遅いが、少数プロンプトでの比較であればCPUでも許容範囲の見込み。
  - APIキー・前提条件についての方針: 追加の有料APIキーは不要(ベースモデル・マスクともにHugging Faceから無料で取得可能。Qwen2.5系はゲート無し、Llama-3.2系はHF利用規約への同意のみで無料)。GPUは必須ではない(`apply_mask.py`によるマスク適用と少数プロンプトでの推論比較はCPUでも可能と見込むが、7Bモデルの場合は低速になる想定)。リポジトリ自体はMITライセンス、ベースモデルのライセンス(Llama Community License、またはQwenのライセンス)は記事内で明記する。
  - 検証スコープ・手順:
    1. `agentic-learning-ai-lab/deleting-weights` をclone。READMEを読み、`src/apply_mask.py`の使い方・学習に使った重い依存関係(flash-attention/vLLM/verl)なしで単純適用できるか確認する。
    2. まず`meta-llama/Llama-3.2-1B-Instruct`へのHugging Faceアクセスを試す。即座に許可が下りない・ゲートで止まる場合は`Qwen/Qwen2.5-7B`系(ゲート無し)にフォールバックする。
    3. 対応する学習済みマスク(`Jacklu0831/deletion-tuning-masks`の該当フォルダ)を取得し、`python src/apply_mask.py --base_model <モデル> --mask_dir <マスクのパス> --output_dir outputs/masked/<名前>` でマスク適用済みモデルを生成する。
    4. ベースモデル(マスク適用前)とマスク適用後のモデルに同じプロンプト(当該マスクが対象とするタスク、例: MMLU-Pro/ToolAlpaca系の問題)を与え、応答・正答率をBefore/Afterで比較する。リポジトリ付属の評価スクリプト(`evaluate_sft.sh`等)が使えればそれも実行する。
    5. マスクファイル(圧縮ビットマップ)の実際のファイルサイズと、フルファインチューニング相当チェックポイントの想定サイズ(パラメータ数×ベースのbit幅から算出)を比較し、論文の「数百〜数千倍小さい」という主張を実際の数値で検証する。
    6. もし(a)Llama系へのアクセスがRoutine実行環境のアカウント状態により認可されず、かつ(b)Qwen7Bでの推論がRoutine実行環境のコンピュート制約(タイムアウト・メモリ不足等)で完結しない場合は、CLAUDE.mdの「書かない(Routine環境の制約)」に該当する範囲は記事等に書かず、PRの説明文冒頭に「ローカル検証が必要」と明記し再現手順(上記clone/apply_mask.py/評価コマンド)を添えてローカル検証にエスカレーションする。results.mdには「Routine環境の制約により未検証、ローカル検証待ち」と1〜2行だけ残す。一方、フルSFT/RLVR学習自体の再現可否(GPUクラスタ前提)は今回のスコープ外であり、これは「検証に直接関係する失敗」ではなく当初からスコープ外とした設計判断として記事に書く。
    7. 実行コマンド・出力・エラー・所要時間・ファイルサイズの実測値はすべてそのままresults.mdに記録する。失敗した場合も、それがツール自体(マスクが想定タスク以外では効果が薄い等)に起因する失敗なのかRoutine環境固有の制約なのかを区別した上で正直に書く。
  - 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(2026-11-11時点、backlog.md参照。関連手法〈ShortGPT等〉やpruning全般の記事はあるが本論文〈Deletion Tuning/Bit-Mask Tuning〉自体の日本語紹介記事は検索範囲では未検出)。
  - 記事化の切り口: 「フルファインチューニング後のモデル」vs「0.05%未満の重みを0にしただけのDeletion Tuningモデル」の応答・正答率比較と、チェックポイントサイズの実測比較というBefore/After構成にする。公開済み学習済みマスクの適用・評価に絞ったこと(フル学習の再現ではないこと)を正直に明記し、過大な一般化をしない。

注意:
  - backlog.mdへの反映元であるPR #152はまだマージされていない。順序としては先にPR #152をマージすることを推奨するが、today.mdの内容はPR #152の有無に関わらず実装Routineが参照できる。

状態: 設定済み
