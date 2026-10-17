# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 020
- 選んだ候補(backlog.mdのタイトルかURL): Behavioral Compositionality of Sparse Autoencoder Representations(SAE Additivity Residuals, SAR) — https://huggingface.co/papers/2610.21261
- 補足メモ(あれば):
  - 人間(matsu)から直接指定された候補(research: 2026-10-17分のネタ候補PR内の候補の1つ)。
  - 出典: https://huggingface.co/papers/2610.21261 (Ziye Mei, Frederic Sala〈University of Wisconsin–Madison〉)。コード公開: https://github.com/OpenSAE/SAE-Behavioral-Compositionality (ライセンス表記は要確認)。
  - 概要: Sparse Autoencoder(SAE)の個々の特徴が、モデルの出力(振る舞い)に対して本当に加算的に効いているのかを「SAE Additivity Residuals(SAR)」という指標で定量化する解釈可能性研究。学習済みSAEの座標系を、同じ部分空間のランダム回転(足し算は保存するが特徴の意味は保たない対照群)と比較し、18種類のモデル・振る舞いの組み合わせすべてで学習済み座標系の方が1次(個々の特徴のみ)残差が小さいことを示す一方、2次(特徴ペア)の交互作用を加えるとcoalitionの順序予測やsteering実験のrank fidelityが0.5874→0.7790まで改善したと報告しており、「SAEの特徴は完全な足し算ではない」ことを示している。
  - 検証範囲(縮小版の概念実証に絞る): フル再現(Gemma Scope 2・Llama Scope等の大型モデル向けSAE)はGPU前提になる可能性が高いため、CPUでも扱える公開済みの小型モデル向けSAE(例: GPT-2 small向けにSAELens等で配布されている既存の学習済みSAE)1つに絞り、「学習済みSAE座標 vs 同一部分空間のランダム回転」で1次残差を比較する部分のみを再現する。2次(特徴ペア)の交互作用やsteering実験のrank fidelity再現はスコープ外としてよい。
  - 追加の有料APIキーは不要(公開済みの既存モデル・SAEを使用)。Routineのクラウド実行環境でGPUが使えない場合は、CLAUDE.mdの「Routine環境の制約」ではなく元から「縮小版の概念実証」に絞る方針のため、CPUで完結する範囲に収める。どうしても歯が立たない場合は、ローカル検証にエスカレーションする旨をPR冒頭に明記する。
  - 日本語記事件数: Zenn 0件 / Qiita 0件 / note 0件(2026-10-17時点、backlog.md参照。日本語での一次紹介記事は未検出のため差別化しやすい)。
  - 記事化の切り口: 「AIの思考の部品(特徴)は本当に独立して足し算できるのか」という解釈可能性の根本的な問いを、1次残差の比較グラフ(学習済み座標 vs ランダム回転)で可視化する。本リポジトリで続いていたエージェントSkillsエコシステム系の候補群とは一線を画す回なので、その旨も記事の導入で触れるとよい。

状態: 設定済み
