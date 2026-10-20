# Day 022: Kronos (金融K線専用の基盤モデル) で BTC/USDT を予測する

対象: https://github.com/shiyu-coder/Kronos (MIT License)

詳しい実行ログ・結果・考察は [`results.md`](./results.md) を参照。ここでは再現手順のみまとめる。

## 事前準備

- Python 3.10以上(本検証はPython 3.12.3で実施)。
- 追加の有料APIキーは不要。GPUは必須ではない(後述の通りCPUのみでも実用的な速度で動く)。
- モデル(`NeoQuasar/Kronos-small`等)とトークナイザはHugging Face Hubから自動ダウンロードされる(認証不要)。
- 価格データはBinanceの公開REST API(`api.binance.com/api/v3/klines`、APIキー不要)からBTC/USDTの1時間足を取得する。

## 再現手順

```bash
cd experiments/day-022
python3 -m venv venv
source venv/bin/activate
pip install numpy pandas torch einops huggingface_hub matplotlib safetensors tqdm

# 1. BTC/USDTの1時間足700本をBinance公開APIから取得してCSV化
curl -s "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=700" -o btcusdt_1h.json
python3 prepare_data.py   # -> btcusdt_1h.csv

# 2. CPUでの実用性を小型モデル(Kronos-mini)で確認
python3 cpu_feasibility_test.py

# 3. 本検証: Kronos-small で400時間分の実績から120時間先を予測(CPU/GPU両方)
python3 main_run.py --device cpu --out cpu
python3 main_run.py --device cuda:0 --out gpu   # GPUが無ければ省略可

# 4. 複数サンプルの平均(sample_count=10)を試す
python3 sample_count_test.py

# 5. 予測 vs 実績のグラフを生成(gpu_*.csvを使用)
python3 plot_result.py   # -> before.png, after.png
```

## このディレクトリの内容

- `model/` — Kronosのモデル実装(`kronos.py`, `module.py`)。上流リポジトリから無改変で取得。
- `LICENSE-upstream` — 上記モデル実装の出典元リポジトリのライセンス全文(MIT)。
- `prepare_data.py` — Binance公開APIで取得したJSONをCSVに整形するスクリプト。
- `cpu_feasibility_test.py` — Kronos-miniでCPU推論の実用性(所要時間)を確認するスクリプト。
- `main_run.py` — Kronos-smallで400時間→120時間予測を実行するメインスクリプト(CPU/GPU両対応)。
- `sample_count_test.py` — `sample_count=10`で複数パスを平均した場合の挙動を確認するスクリプト。
- `plot_result.py` — 予測結果と実績を重ねたグラフ(`before.png`/`after.png`)を生成するスクリプト。
- `btcusdt_1h.csv` — 実際に使用したBTC/USDT 1時間足データ(2026-09-21〜2026-10-20、700本)。
- `before.png` / `after.png` — 実際に生成した図。
- `cpu_metrics.json` / `gpu_metrics.json` — 各デバイスでの実行結果の指標。
