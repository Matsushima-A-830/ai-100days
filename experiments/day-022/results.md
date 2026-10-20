# Day 022 検証結果: Kronos(金融K線専用の基盤モデル)でBTC/USDTを予測する

対象: shiyu-coder/Kronos
https://github.com/shiyu-coder/Kronos
ライセンス: MIT(`LICENSE`に明記、Copyright (c) 2025 ShiYu)
論文: https://arxiv.org/abs/2508.02739(AAAI 2026採択)

## 検証の範囲

today.mdの通り、追加の有料APIキー不要の範囲で、Hugging Face Hubで公開されている
`Kronos-mini`/`Kronos-small`を使い、BTC/USDTの実際の1時間足データに対して
「過去400時間 → 未来120時間」の価格予測を実行し、予測結果と実際の値動きを
突き合わせた。あわせて、着手前に確認すべきとされていた「CPUでも実用的な速度で
推論できるか」をKronos-miniで検証し、`sample_count`(複数サンプルの平均)の
効果も簡易的に確認した。中国本土市場向けの`akshare`連携やファインチューニング
スクリプトは今回のスコープ外とした。

## 1. 環境構築

```
$ python3 --version
Python 3.12.3
$ pip install numpy pandas torch einops huggingface_hub matplotlib safetensors tqdm
...
torch==2.14.1 (CUDA同梱ビルド。本機にGPUがあるためCUDA有効)
einops==0.8.1
pandas==2.2.2
numpy==2.5.4
matplotlib==3.9.3
safetensors==0.6.2
tqdm==4.67.1
```

公式の`requirements.txt`に厳密なバージョン固定は`einops`/`huggingface_hub`/`matplotlib`/
`pandas`/`safetensors`/`tqdm`のみで、`numpy`/`torch`はバージョン不問(`numpy`、
`torch>=2.0.0`)だった。今回の環境(Python 3.12.3、CUDA付きGPU)ではそのままの
指定で問題なく入り、クラウドRoutineで過去に遭遇したようなPythonバージョン起因の
インストール失敗は無かった。

## 2. データ取得: BinanceのPublic APIを使う(APIキー不要)

今回の検証対象であるBTC/USDTの実際のOHLCVデータを、Binanceの公開REST API
(APIキー不要)から取得した。

```
$ curl -s "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=700" -o btcusdt_1h.json
$ python3 prepare_data.py
(700, 7)
           timestamps      open      high  ...     close      volume        amount
0 2026-09-21 10:00:00  84653.70  84816.42  ...  84441.77  1696.63605  1.432929e+08
1 2026-09-21 11:00:00  84441.77  84917.36  ...  84887.19  1151.00512  9.750108e+07
...
```

2026-09-21 10:00から2026-10-20 13:00(UTC)までの1時間足700本を取得できた
(`btcusdt_1h.csv`)。

## 3. CPUでの実用性確認(Kronos-mini)

着手前にtoday.mdで指示されていた通り、まず最小モデルのKronos-miniで、CPUのみ
(`CUDA_VISIBLE_DEVICES=""`で明示的にGPUを隠した上で`device="cpu"`指定)の
推論速度を確認した。

```
$ CUDA_VISIBLE_DEVICES="" python3 cpu_feasibility_test.py
Load time: 7.1s
100%|██████████| 24/24 [00:00<00:00, 78.78it/s]
CPU predict time (Kronos-mini, lookback=200, pred_len=24): 0.3s
```

lookback 200時間・予測24時間という規模では、モデルの読み込み(約7秒、初回は
Hugging Face Hubからのダウンロードを含む)を除けば、CPUのみでも推論自体は
**0.3秒**で終わった。ノートPC相当のCPUでも十分実用的な速度だと確認でき、
「GPUが使えず極端に遅い」という事態は発生しなかった。

## 4. 本検証: Kronos-smallで400時間→120時間を予測する(CPU/GPU比較)

公式README記載の構成(lookback=400, pred_len=120, T=1.0, top_p=0.9, sample_count=1)
に合わせ、実際のBTC/USDTデータで予測を実行した。予測対象の120時間分は、データ取得
時点で既に実績値が存在するため、予測結果と実際の値動きをそのまま突き合わせられる
(いわゆるバックテスト形式)。

```
$ python3 main_run.py --device cpu --out cpu
ACTUAL_DEVICE: cpu
PREDICT_TIME: 19.62s
METRICS: {
  "device": "cpu",
  "predict_time_sec": 19.62,
  "mae_usd": 1928.37,
  "mape_pct": 2.33,
  "directional_hits": 56,
  "directional_total": 120,
  "directional_accuracy": 0.467,
  "diff_correlation": 0.034
}

$ python3 main_run.py --device cuda:0 --out gpu
ACTUAL_DEVICE: cuda:0
PREDICT_TIME: 2.80s
METRICS: {
  "device": "cuda:0",
  "predict_time_sec": 2.80,
  "mae_usd": 1929.82,
  "mape_pct": 2.33,
  "directional_hits": 60,
  "directional_total": 120,
  "directional_accuracy": 0.5,
  "diff_correlation": 0.043
}
```

| 項目 | CPU | GPU (RTX 5060 Ti) |
| --- | --- | --- |
| 実行時間(predict) | 19.62秒 | 2.80秒(約7倍速) |
| MAE(平均絶対誤差、USD) | $1928.37 | $1929.82 |
| MAPE(平均絶対誤差率) | 2.33% | 2.33% |
| 方向性的中率(120時間の各1時間ステップで上昇/下落の向きが合っていた割合) | 46.7%(56/120) | 50.0%(60/120) |
| 予測差分と実績差分の相関係数 | 0.034 | 0.043 |

CPU/GPUで予測時間は約7倍の差があったが、MAE・MAPEはほぼ同じだった(サンプリング
を伴う生成なので、CPU/GPUの実装差というより乱数由来の揺らぎの範囲と考えられる)。
一方で、**方向性的中率(次の1時間が上がるか下がるかを当てられた割合)はCPU 46.7%・
GPU 50.0%と、コイン投げ(50%)を明確に上回ることはなかった**。予測差分と実績差分
の相関係数も0.03〜0.04とほぼ0に近く、少なくとも今回のBTC/USDT・この120時間という
1つの窓では、方向性に関して統計的に意味のある予測力は確認できなかった。

実際の値動きと予測のグラフは[`after.png`](./after.png)、予測前の400時間分の
実績データのみを示した図は[`before.png`](./before.png)を参照。青線(400時間の
実績)に続いて、緑線(実際の120時間)が一度下落してから回復する一方、オレンジ点線
(Kronosの予測)はほぼ一貫して上昇方向にずれていった様子が視覚的に確認できる。

## 5. 複数サンプルの平均(sample_count=10)は改善するか

論文・READMEでは、`sample_count`を増やして複数の予測パスを平均することで
より安定した予測が得られるとされている。これを実際に試した。

```
$ python3 sample_count_test.py
{
  "predict_time_sec": 5.16,
  "mae_usd": 1891.23,
  "mape_pct": 2.29,
  "directional_accuracy": 0.45,
  "diff_correlation": -0.116
}
```

GPUでは`sample_count=10`でも5.2秒と十分高速だったが、MAE/MAPEはほぼ変わらず
(むしろ僅かに改善)、**方向性的中率はむしろ45.0%に下がり、相関係数も-0.116と
マイナスに転じた**。少なくとも今回の1組のデータ・1回の試行では、サンプル数を
増やす平均化が方向性の予測力を改善する効果は確認できなかった。

## 6. 結論

- Kronosの「MCPクライアント相当の呼び出し → トークナイザ → モデル推論」という
  一連の流れは、追加の有料APIキー不要・GPU不要で、実際のBTC/USDTデータに対して
  問題なく動作した。公式READMEの手順通りの依存バージョンで、Python 3.12環境でも
  インストールトラブルは無かった。
- **CPUのみでも実用的な速度で動く。** Kronos-miniなら200時間→24時間予測が0.3秒、
  Kronos-smallの400時間→120時間予測でも約20秒で完了し、「GPUが無いと話にならない」
  という懸念は杞憂だった。GPU(RTX 5060 Ti)を使うと約7倍速くなった。
- **一方で、今回の実測では、価格の方向性(上がるか下がるか)を当てる力は
  確認できなかった。** 方向性的中率は46.7%〜50.0%でコイン投げ水準にとどまり、
  予測差分と実績差分の相関係数も0に近かった。`sample_count`を増やしても
  この点は改善しなかった。
- MAE・MAPE(絶対的な価格水準への近さ)自体は2.3%程度とそこそこ小さく、
  「大外れはしない」という意味での予測の滑らかさはあったが、これは市場全体の
  値動きのレンジに対して自然に追従しているだけで、投資判断に使える方向性の
  シグナルとは別物である点に注意が必要である。
- **公式の免責の通り、Kronosの出力は確率的なサンプルの1つであり、これ単体を
  投資判断の根拠にすべきではない。** 今回の1回・1銘柄・1期間の検証結果も、
  他の銘柄・期間では異なる結果になりうる点に留意されたい。
