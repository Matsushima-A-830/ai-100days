# Day 054: higurashi-ai/Haru-4B を自前ホストでCPUだけで動かす

出典: https://huggingface.co/higurashi-ai/Haru-4B (Apache-2.0)
Code: https://github.com/higurashi-ai/Haru (Apache-2.0)

全二重(同時聞き取り・発話)の音声対話モデル。公開Hugging Face Spaces(`hugging-apps/haru-4b`)の
オフラインデュプレックスデモはこのRoutine実行環境のネットワークポリシーで`*.hf.space`への接続が
ブロックされていたため、GitHubのコードを自前でインストールし、CPUのみで推論を実行した。
詳細・実測値は `results.md` を参照。

## 再現手順

```bash
# 1. コードとモデルを取得(GPUなしでも実行可能)
git clone https://github.com/higurashi-ai/Haru
python3 -m venv .venv
.venv/bin/pip install torch          # PyPIのデフォルトwheel(CPU/CUDA同梱)で十分
.venv/bin/pip install -e ./Haru/haru

# 2. 公式サンプル音声を取得(hugging-apps/haru-4b Spaceの gr.Examples から)
mkdir -p assets
for f in en_seg.wav en_ref.wav ja_seg.wav ja_ref.wav; do
  curl -sL -o "assets/$f" \
    "https://huggingface.co/spaces/hugging-apps/haru-4b/resolve/main/assets/$f"
done

# 3. 公式の英語/日本語キャラクターカード(persona)をレンダリング
.venv/bin/python make_cards.py   # card_en.txt / card_ja.txt を生成

# 4. CPUで推論(初回はmodel.safetensors ~10.5GBをHugging Face Hubから自動取得)
.venv/bin/haru-inference assets/en_seg.wav out_en_cpu_card.wav \
  --reference assets/en_ref.wav --device cpu \
  --transcript transcript_en_cpu_card.jsonl \
  --system-prompt-file card_en.txt
```

初回実行時に `higurashi-ai/Haru-4B` の `model.safetensors`(約10.5GB)・`config.json`・`tokenizer.json`が
`~/.cache/huggingface/` に自動ダウンロードされる(認証不要、公開モデル)。

## ファイル

- `make_cards.py` — `haru.prompt.render_card` を使い、リポジトリ内蔵の英語/日本語キャラクターカード
  (`haru/assets/cards/{en,ja}.json`)をシステムプロンプトのテキストに変換するスクリプト。
- `card_en.txt` / `card_ja.txt` — 上記で生成した実際のシステムプロンプト。
- `assets/*.wav` — `hugging-apps/haru-4b` Spaceの公式サンプル音声(そのまま使用)。
  `*_padded.wav` は末尾に5秒の無音を追加したもの(Space側の `app.py` が行っている処理を再現)。
- `out_*.wav` / `transcript_*.jsonl` — 各条件(英語/日本語、プロンプトの違い、seed固定)での実際の出力音声と
  フレーム単位の文字起こし。
- `logs/` — 各実行の標準出力ログ(モデルのダウンロード、warning、フレーム数・1フレームあたりの時間、
  最終的な文字起こし)。
- `test_haru.py` / `raw_results.json` — 公開Spaces(`hugging-apps/haru-4b`)のGradio API(`/converse`)を
  直接呼ぶ試み。このRoutine実行環境のネットワークポリシーで`*.hf.space`への接続がブロックされたログ
  (`403 Forbidden: no rule or network setting allows this host`)。Routine環境固有の制約のため記事には
  反映していない。

## 人間が確認・再現すべき点

- GPU搭載PCで `python -m haru.server --hf-repo higurashi-ai/Haru-4B` を起動し、
  `http://localhost:8998` でマイクを使った実際のリアルタイム全二重会話を試す
  (このRoutine実行環境にはGPUが無く、マイクも無いため未検証)。
- 公開Spaces(`hugging-apps/haru-4b` / `akhaliq/haru-4b-studio`)にブラウザからアクセスし、
  同じ公式サンプル音声・カードで応答が再現するか比較する。
