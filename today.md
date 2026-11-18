# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 052
- 選んだ候補(backlog.mdのタイトルかURL): Weight-Space Programming Doesn't Need Transformers — https://huggingface.co/papers/2611.22055
- 補足メモ(あれば):
  - 出典: https://huggingface.co/papers/2611.22055 (arXiv 2611.22055。2026-11-18付研究PR〈#178〉でbacklog.mdに追記。著者: Hyunjong Ok, Jaeho Lee〈POSTECH〉。コード: https://github.com/effl-lab/Weight-Space-Programming, MIT)。
  - 概要: 勾配降下法を使わず、LLMに他モデルの重みを直接「書かせる」Weight-Space Programmingという手法を検証した論文。3つのフロンティアLLM(Claude Opus 5.5・GPT-6.1 Sol・GPT-6 Astra)にARCの多肢選択科学問題10例とサンドボックスを与え、固定アーキテクチャへの重み書き込みと、LLM自身にアーキテクチャ設計させる場合を比較した。設計を自由にすると3モデルともプレーンテキストの事実を疎なテーブルにコンパイルし固定の検索手順で読む構造に行き着き、最大54.4%のテスト精度を達成、あるモデルは同じLLMが書いた最も精度の高いTransformerを約1,800分の1のパラメータ数で上回った。勾配が無いためLLMは各エントリの意味を説明でき、誤答を1行に追跡・修正できる点を特徴としている。
  - 検証スコープの絞り方と選定理由: 公開コードの`harness.run`はClaude Code CLIをサンドボックス(bubblewrap)内の「writer」として直接呼び出す設計になっている。これにより追加の有料APIキーを使わず、Claude Code自身をwriterとして動かして再現できる。公開済み言語モデルへのファインチューニング・速度比較の一部(`baselines.arc_released`等)はCUDA GPUが必須のため今回のスコープ外とし、CPU上で完結する「ARCタスク1〜2問に対してClaude Code自身にwriterとして重みを書かせ、スコアリングする」という中心的な実験に絞る。
  - APIキー・前提条件についての方針: 追加の有料APIキーは不要(導入済みのClaude Code CLI自身をwriterとして使う)。ARCデータセット(`allenai/ai2_arc`)はHugging Face Hubから取得する(ネットワーク制限で取得できない場合はRoutine環境の制約として扱い、ローカル検証にエスカレーションする)。Linux環境でのbubblewrapによるサンドボックス実行が前提のため、Routine実行環境で動かない場合もRoutine環境の制約として扱う。
  - 検証スコープ・手順:
    1. リポジトリをcloneし、`requirements.txt`を導入する。導入ログをそのまま記録する。
    2. オフラインの単体テスト(`pytest tests -q`)をCPU上で実行する。
    3. ARCデータセット(`allenai/ai2_arc`)をHugging Face Hubから取得する。取得できない場合はRoutine環境の制約として記録し、ローカル検証へエスカレーションする。
    4. 環境変数(`WSP_DATA_ROOT`・`HF_HOME`・`WSP_VENV`・`WSP_CLAUDE_BIN`・`WSP_CLAUDE_PROFILES`)を設定し、`WSP_CLAUDE_BIN`を導入済みのClaude Code CLIに向ける。
    5. `python -m harness.run`で1つのARCタスクに対しClaude Code自身をwriterとして動かし、固定アーキテクチャへの重み書き込みと、可能であればLLM自身にアーキテクチャ設計させる場合の両方を試す。
    6. 生成された重み(疎なテーブル等)の中身を実際に読み、どの事実がどう格納・解釈されているかを確認する。
    7. スコアリング結果・ログ・生成された重みの中身をすべて`results.md`にそのまま記録する(動かなかった場合も失敗として正直に書く)。
    8. GPU前提のファインチューニング・速度比較(`baselines.arc_released`等)は今回スコープ外とした旨を記事・シェアカードに明記する。
  - 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(2026-11-18時点、backlog.md参照。検索範囲ではこの論文・公開コード自体の日本語紹介・検証記事は未検出。元になったMIT CSAILの先行ブログ「Weight-space programming」自体を紹介する日本語記事〈企業メディア経由〉はある)。
  - 記事化の切り口: 「LLMが勾配降下なしで他モデルの重みを直接書き換えて正解させる」という直感に反する現象を、実際にClaude Code自身をwriterとして動かし、生成された重み(疎なテーブル)の中身を覗いて見せる切り口。本チャレンジを運用しているClaude Code自身が検証対象の「writer」役を担うという自己言及的な構成にもできる。

状態: 設定済み
