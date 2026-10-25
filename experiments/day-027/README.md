# Day 027: IQuestLab/IQuest-Q1 のライセンス・トークナイザ実機確認

検証対象: https://huggingface.co/IQuestLab/IQuest-Q1
論文: https://huggingface.co/papers/2610.30949
コード: https://github.com/IQuestLab/IQuest-Q1
ライセンス: Modified MIT License(`experiments/day-027/LICENSE`に全文を保存、商用利用可・
UI上に"IQuest-Q1"と表示する義務のみ)

## この日の検証スコープ

本体は総パラメータ320B・BF16で約650GB、公式デプロイ手順は8GPU構成(`--tp-size 8`)前提で、
Hosted Inference ProviderもHugging Face Spacesの無料デモも存在しない。個人が6時間以内に
用意できる構成ではないため、**本体の実機推論は行っていない。**

一方で、以下はダウンロードサイズが小さく(数十KB〜十数MB)GPUも不要なため、実際に取得して動かした。

- `LICENSE` ファイル全文の取得・確認
- `config.json` のアーキテクチャ設定値の確認
- `tokenizer.json` / `tokenizer_config.json` を実際にロードし、日本語・英語・Pythonコードの
  トークナイズ結果を取得

詳細な実行ログは `results.md` を参照。

## 再現手順

```bash
pip install huggingface_hub tokenizers

python3 - <<'EOF'
from huggingface_hub import hf_hub_download, list_repo_files

repo = "IQuestLab/IQuest-Q1"
print("num files:", len(list_repo_files(repo)))

for f in ["config.json", "tokenizer.json", "tokenizer_config.json",
          "chat_template.jinja", "generation_config.json", "LICENSE"]:
    print(f, "->", hf_hub_download(repo, f, local_dir="."))
EOF

python3 tokenizer_test.py
```

`tokenizer_test.py` はこのディレクトリに同梱。GPT-2トークナイザ(`tokenizers`ライブラリが
Hugging Face Hubから自動取得)を比較対象として使う。

## 含まれているファイル

- `results.md`: 実行ログと結果(実際に動かしたものと、動かしていないもの〈ベンチマーク数値の引用〉を明確に分けて記録)
- `config.json`: Hugging Faceから取得した実際のモデル設定ファイル
- `LICENSE`: Hugging Faceから取得した実際のライセンス全文
- `tokenizer_test.py`: トークナイザ比較に使った実行スクリプト

`tokenizer.json`(12.5MB)・`tokenizer_config.json`(92.7KB)はサイズの都合でこのリポジトリには
含めていない。再現手順のコマンドで取得できる。

## 人間のローカルPCでの独立検証(results.md 5節)

人間のローカルPC(GPU搭載)で、本PRのLICENSE・config.json・トークナイザ比較・ベンチマーク表を
独立に取得・再実行し、すべてバイト単位・数値単位で完全に一致することを確認した。また、PR記載時点
では「見つからなかった」としていたGGUF量子化版が、後日のHugging Face Hub検索で新たに2件見つかった
(`Baekpica/IQuest-Q1-Mixed-Quant-GGUF` 約88GB、`xhxlb/IQuest-Q1-GGUF` 約844GB)。最小構成の
IQ2_XXS(約88GB)でもこのPCのVRAM(16GB)・RAM(30GB)には収まらないためフル推論は見送ったが、
HTTPレンジリクエストでGGUFファイル先頭200MBのみ取得し、メタデータ(層数・エキスパート数・
コンテキスト長等)が`config.json`と完全に一致することを確認した。詳細はresults.md 5節参照。
