# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 051
- 選んだ候補(backlog.mdのタイトルかURL): jingyaogong/minimind — https://github.com/jingyaogong/minimind
- 補足メモ(あれば):
  - 出典: https://github.com/jingyaogong/minimind (2026-11-17付研究PR〈#174〉でbacklog.mdに追記。Apache-2.0。当日GitHub Trending Pythonで+188star/日、スター数65,881)。
  - 概要: Tokenizer→Pretrain→SFT→LoRA/DPO/PPO/GRPO/CISPO→エージェント的RL→蒸留まで、LLM学習パイプライン全体を高レベルラッパーに頼らずPyTorchネイティブで実装したプロジェクト。「Train a 64M-parameter LLM from scratch in just 2h!」を掲げ、最小構成の「minimind-3(64M)」は公式リファレンス環境(RTX3090 1枚)でPretrain約1.21時間+SFT約1.10時間、合計2.3時間程度で学習できると主張している。
  - 検証スコープの絞り方と選定理由: 公式のリファレンス環境はRTX3090 1枚だが、CUDA必須ではなくCPU/Apple MPSでも学習できると明記されている。クラウドRoutine実行環境にGPUが無い前提で、データセット規模・ステップ数を縮小したミニ構成(例: サンプル数・epoch数を絞ったpretrain+SFT)をCPU上で6時間以内に収まるように調整して実行する。フルスケールの「2時間でLLM」という主張そのものの再現はGPU前提のため今回のスコープ外とし、その旨を正直に記事に明記する(ツール自体のGPU前提は検証対象の性質なので「書く」失敗として扱ってよい)。
  - APIキー・前提条件についての方針: 追加の有料APIキーは不要。モデル・データセットはHugging Face/ModelScopeから取得する(ネットワーク制限でダウンロードできない場合はRoutine環境の制約として扱い、ローカル検証にエスカレーションする)。実験管理用のwandb/SwanLabは任意・未使用で進める。
  - 検証スコープ・手順:
    1. リポジトリをcloneし、Python仮想環境でrequirementsを導入する。導入ログをそのまま記録する。
    2. 学習データセット(ミニ構成)をHugging Face/ModelScopeから取得する。取得できない場合はRoutine環境の制約として記録し、ローカル検証へエスカレーションする。
    3. CPU上でpretrainを縮小構成(サンプル数・ステップ数を絞る)で実行し、loss推移をログに記録する。
    4. 同様に縮小構成でSFTを実行し、学習前後で簡単な質問に対する生成結果がどう変わるかをBefore/Afterで比較する。
    5. 実行時間・loss推移・生成サンプルをすべて`results.md`にそのまま記録する(動かなかった場合も失敗として正直に書く)。
    6. GPU前提のフルスケール「2時間」主張を今回CPU縮小版では再現していない旨を記事・シェアカードに明記する。
  - 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(2026-11-17時点、backlog.md参照。検索範囲ではZenn/Qiita/noteでの紹介・検証記事は未検出)。
  - 記事化の切り口: 「ゼロから自分で書いたわけではないが、公式スクリプトを使って実際に自作LLMを一から学習させ、学習曲線と生成結果がどう変化するかを手元で確認する」というBefore/After型の切り口。GPUが無い環境でどこまで縮小すれば現実的な時間で動くか、という制約込みの試行録にする。

状態: 設定済み
