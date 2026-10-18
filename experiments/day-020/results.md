# Day 020 検証結果: SAE Additivity Residuals (SAR) を GPT-2 Small で再現する

対象の論文: "Behavioral Compositionality of Sparse Autoencoder Representations"
(Ziye Mei, Frederic Sala, University of Wisconsin–Madison)
https://huggingface.co/papers/2610.21261

コード: https://github.com/OpenSAE/SAE-Behavioral-Compositionality (Apache-2.0)

## 検証の範囲

論文本体は Gemma Scope 2・Llama Scope 等、GPU前提の大型モデル×SAEの組み合わせ
18種類で評価しているが、今回はtoday.mdで事前に決めた通り、公開リポジトリに
同梱されている `demo/demo.py`(GPT-2 Small + 公開SAE `gpt2-small-res-jb` を使う
縮小デモ)をCPUのみでそのまま実行し、「学習済みSAE座標 vs 同一部分空間の
ランダム回転」で1次残差(SAR_1)を比較する部分を再現することに絞った。
2次(特徴ペア)の交互作用やsteering実験のrank fidelity(論文本体の0.5874→0.7790
という数値)は論文側の主張であり、今回のGPT-2 Small限定の再現では別の数値になる
点に注意(後述)。

## 1. 環境構築

Python 3.11.17 の venv を作成し、リポジトリの `requirements_demo.txt` が指定する
バージョン(`numpy==2.5.0`, `matplotlib==3.11.0`, `torch==2.11.0`,
`transformer-lens==3.5.0`, `sae-lens==6.44.4`、コメントに「Python 3.12.10で動作確認」
とある)をまず試した。

```
$ pip install numpy==2.5.0 matplotlib==3.11.0
ERROR: Ignored the following versions that require a different python version:
  ... 2.5.0 Requires-Python >=3.12 ...
ERROR: Could not find a version that satisfies the requirement numpy==2.5.0
```

**これは検証に直接関係する失敗として記録する。** `requirements_demo.txt` のコメントに
「Python 3.12.10で動作確認」と明記されている通り、`numpy==2.5.0` はPython 3.12以降が
前提で、Python 3.11環境(今回の実行環境のデフォルト)ではこの固定バージョンのまま
インストールできない。公式手順通りのバージョン指定では動かなかったケースにあたる。
対処として、バージョンを固定せず `pip install numpy matplotlib` で最新の互換版
(numpy 2.4.6, matplotlib 3.11.2)を入れ直したところ問題なくインストールできた。

続けて `transformer-lens==3.5.0 sae-lens==6.44.4` をデフォルトのPyPIからインストール。
このとき依存関係の解決で `torch` が2.14.1(CUDA同梱ビルド)に引き上げられた
(`torch==2.11.0` 固定でのインストールは、実行環境のネットワークポリシーにより
PyTorch公式のCPU専用wheel配布元への接続がブロックされたため断念し、デフォルトの
PyPI経由にフォールバックした。これは検証対象ツール自体の問題ではなく、今回の
Routine実行環境のネットワーク制約によるものなので記事では触れない)。
本機にGPUは無いため `torch.cuda.is_available()` は `False` で、実行は素のCPUで行われる。

最終的な実行環境:

```
Python 3.11.17
numpy 2.4.6
matplotlib 3.11.2
torch 2.14.1 (CUDA同梱ビルドだがGPU無し環境のためCPU実行)
transformer-lens 3.5.0
sae-lens 6.44.4
```

## 2. 実行: `demo/demo.py --layers 4 10`

`sar.py`・`demo/demo.py` は [OpenSAE/SAE-Behavioral-Compositionality](https://github.com/OpenSAE/SAE-Behavioral-Compositionality)
(Apache-2.0) から無改変のまま `experiments/day-020/` に取り込んだ
(`sar.py`, `demo/demo.py`, `LICENSE-upstream`)。

```
$ python3 demo/demo.py --layers 4 10
Loaded pretrained model gpt2 into HookedTransformer
layer  4 done
layer 10 done

GPT-2 Small, 24 copying prompts, K = 16, 384 coalitions (256 fit, 128 held out)

Layer  SAR_1 SAE  SAR_1 rotated  SAE lower   rho_2  affine SAR_1
    4     0.3232         0.5652     24 / 24   0.383       2.3e-27
   10     0.0148         0.0481     24 / 24   0.945       5.3e-26

         Rank fidelity     Ordering error       Sign error      Selection regret
Layer     first pairwise     first pairwise     first pairwise     first pairwise
    4    0.7955   0.8519    0.0391   0.0187    0.2614   0.2002    0.1520   0.0632
   10    0.9847   0.9967    0.0018   0.0002    0.0472   0.0254    0.0139   0.0017

Example: "Alice Emma Alice", layer 4: SAR_1 = 0.4113, rho_2 = 0.518
  strongest pair: features 2788 and 23180, interaction -1.558, main effects +3.070 and +1.194
  https://www.neuronpedia.org/gpt2-small/4-res-jb/2788
  https://www.neuronpedia.org/gpt2-small/4-res-jb/23180

Saved demo_layers4_10.png

real    4m12.682s
user    13m25.396s
sys     1m50.443s
```

実行時間は約4分13秒(CPUのみ、GPT-2 Small・2層分・24プロンプト×384コアリション)。
追加の有料APIキーは不要、GPUも不要だった。生成された図は
[`demo_layers4_10.png`](./demo_layers4_10.png)。

モデル(`gpt2`)はTransformerLens経由、SAE(`gpt2-small-res-jb`)はSAELens経由で
HuggingFace Hubから自動ダウンロードされた(いずれも追加の認証・APIキー不要の
公開モデル)。

## 3. 結果の読み方

- **SAR_1(1次残差)**: SAEが選んだ上位16特徴の活性化×デコーダ方向を単純に
  足し合わせるモデルだけで、実際のモデルの振る舞い(`logit(B) - logit(C)`)を
  どれだけ説明できないかを表す指標。0に近いほど「完全に足し算で説明できる」。
- **rotated(ランダム回転)**: 同じ16次元部分空間を保ったまま、学習済みSAEの
  座標系の代わりにランダムな直交回転を適用した対照群。足し算という操作自体は
  保存されるが、各座標が「意味のある特徴」である保証は失われる。
- 今回の再現で、layer 4では SAE座標のSAR_1 = 0.3232、ランダム回転のSAR_1(8回の
  中央値) = 0.5652 で、**24プロンプト全てでSAE座標の方が残差が小さかった**
  (`SAE lower: 24/24`)。layer 10でも同様にSAE座標 0.0148 < 回転 0.0481、
  24/24でSAE座標が下回った。
- layerが深くなるほど(4→10)SAR_1自体が小さくなっている(0.32→0.015)ことから、
  後段の層では振る舞いがより「足し算的」に説明しやすくなっている、という
  傾向も今回のCPU限定の再現で確認できた。
- `affine SAR_1`(アフィン制御: 線形写像 `psi(h) = W_U[:, B] . h` を使った
  サニティチェックで、理論上SAR_1は丸め誤差程度まで0になるはず)は
  layer 4で2.3e-27、layer 10で5.3e-26と、いずれも事実上0になっており、
  `sar.py` の実装・今回の実行パイプラインが数値的に健全であることを確認できた。
- ρ₂(2次=特徴ペアの交互作用を足すとSAR_1のうちどれだけ追加で説明できるか)は
  layer 4で0.383、layer 10で0.945。**1次だけでも「ランダム回転よりは」良いが、
  2次の交互作用を加えるとさらに説明力が上がる**、という論文の主張(「SAEの特徴は
  完全な足し算ではない」)の方向性も、GPT-2 Small・2層限定ながら確認できた。

**注意: 今回の数値は論文本体(18種類のモデル・振る舞いの組み合わせ、
rank fidelity 0.5874→0.7790)とは異なる。** 論文の集計値はGemma Scope 2・
Llama Scope等の大型モデルを含む全体の結果であり、今回はリポジトリ同梱の
GPT-2 Small限定デモをそのまま動かした結果である。上記のrank fidelity
(layer 4: 0.7955→0.8519、layer 10: 0.9847→0.9967)も今回のGPT-2 Small・
24プロンプト限定の値であり、論文の集計値と単純比較できない。

## 4. 結論

- `OpenSAE/SAE-Behavioral-Compositionality` のAapche-2.0公開コードは、
  GPU・有料APIキーなしでも、CPUのみ・Python 3.11環境で(固定バージョンから
  numpy/matplotlib/torchを現行の互換バージョンに読み替えれば)問題なく
  動作し、「学習済みSAE座標の方がランダム回転よりも振る舞いを足し算的に
  説明できる」という論文の中心的な主張を、GPT-2 Small・2層・24プロンプトという
  縮小スケールで実際に再現できた。
- 公式の`requirements_demo.txt`はPython 3.12を前提にしており、Python 3.11
  環境ではバージョン固定のままでは `numpy==2.5.0` のインストールに失敗する。
  バージョンを緩めれば動作する。

## 5. 追加検証: 人間のローカルPC(GPU)での再実行

上記まではRoutineのクラウド実行環境(CPUのみ、Python 3.11、ネットワーク制約で
PyTorch公式配布元に接続できずtorchは2.14.1にフォールバック)での結果だった。
人間(matsu)のローカルPC(Windows 11 + WSL2 Ubuntu、NVIDIA GeForce RTX 5060 Ti、
16GB VRAM)で、同じ`sar.py`・`demo/demo.py`(無改変)を**GPU・公式の固定バージョン
そのまま**で再実行し、結果の再現性と環境差の影響を追加で確認した。

### 5.1 環境構築(ローカル、Python 3.12.3)

ローカルのWSL Ubuntuには Python 3.12.3 が入っており、クラウド環境で失敗した
`numpy==2.5.0` を含む公式の固定バージョンがそのままインストールできた。

```
$ python3 -m venv venv_gpu && source venv_gpu/bin/activate
$ pip install numpy==2.5.0 matplotlib==3.11.0
Successfully installed ... matplotlib-3.11.0 numpy-2.5.0 ...
$ pip install torch==2.11.0
Successfully installed ... torch-2.11.0 ...
$ pip install transformer-lens==3.5.0 sae-lens==6.44.4
Successfully installed ... sae-lens-6.44.4 ... transformer-lens-3.5.0 ... transformers-5.20.1 ...
$ python3 -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
2.11.0+cu130 True NVIDIA GeForce RTX 5060 Ti
```

クラウド環境ではPyTorch公式配布元への接続がネットワークポリシーでブロックされ
torchが2.14.1に引き上げられたが、ローカルではそのような制約がなく、公式が
固定した`torch==2.11.0`をそのままCUDA付きでインストールできた
(環境制約の差であり、ツール自体の問題ではない)。

### 5.2 実行: `demo/demo.py --layers 4 10` (GPU)

`demo/demo.py`は`torch.cuda.is_available()`で自動的にGPUへ切り替わる実装
(無改変)のため、コード側の変更は不要だった。

```
$ time python3 demo/demo.py --layers 4 10
Loaded pretrained model gpt2 into HookedTransformer
layer  4 done
layer 10 done

GPT-2 Small, 24 copying prompts, K = 16, 384 coalitions (256 fit, 128 held out)

Layer  SAR_1 SAE  SAR_1 rotated  SAE lower   rho_2  affine SAR_1
    4     0.3232         0.5652     24 / 24   0.383       2.6e-27
   10     0.0148         0.0481     24 / 24   0.945       7.1e-26

         Rank fidelity     Ordering error       Sign error      Selection regret
Layer     first pairwise     first pairwise     first pairwise     first pairwise
    4    0.7955   0.8519    0.0391   0.0187    0.2614   0.2002    0.1520   0.0632
   10    0.9847   0.9967    0.0018   0.0002    0.0472   0.0254    0.0139   0.0017

Saved demo_layers4_10.png

real    1m0.801s
user    3m43.072s
sys     0m11.081s
```

生成された図は[`demo_layers4_10_gpu_local.png`](./demo_layers4_10_gpu_local.png)
(クラウドCPU版の[`demo_layers4_10.png`](./demo_layers4_10.png)と比較可能)。

### 5.3 CPU(クラウド)とGPU(ローカル)の比較

| 項目 | CPU(クラウドRoutine, Python 3.11) | GPU(ローカルPC, Python 3.12) |
| --- | --- | --- |
| 実行時間(real) | 4m12.682s | 1m0.801s(約4.2倍速) |
| SAR_1 SAE(layer 4 / 10) | 0.3232 / 0.0148 | 0.3232 / 0.0148(完全一致) |
| SAR_1 rotated(layer 4 / 10) | 0.5652 / 0.0481 | 0.5652 / 0.0481(完全一致) |
| SAE lower | 24/24, 24/24 | 24/24, 24/24(完全一致) |
| rho_2(layer 4 / 10) | 0.383 / 0.945 | 0.383 / 0.945(完全一致) |
| rank fidelity first/pairwise(layer 4) | 0.7955 / 0.8519 | 0.7955 / 0.8519(完全一致) |
| rank fidelity first/pairwise(layer 10) | 0.9847 / 0.9967 | 0.9847 / 0.9967(完全一致) |
| affine SAR_1(layer 4 / 10) | 2.3e-27 / 5.3e-26 | 2.6e-27 / 7.1e-26(いずれも丸め誤差レベルで実質0) |

- **主要な指標はCPU/GPU・クラウド/ローカル・Python 3.11/3.12という環境差を
  横断して完全に一致した。** 乱数シードが固定されている(あるいはランダム回転の
  中央値を複数回評価して報告している)ため、浮動小数演算の経路がCPUとGPUで
  変わっても、報告される桁数では差が出なかった。
  `affine SAR_1`のような理論上ゼロになるはずの量にのみ、GPU固有の浮動小数誤差
  (e-27〜e-26オーダー)が見えるが、これは実質的な差ではない。
- **GPUにより実行時間は約4.2倍短縮された**(4m13s → 1m1s)。GPT-2 Small・2層・
  24プロンプトという縮小デモではCPUでも6時間ルールの範囲内で十分完走できる
  規模だったが、論文本体のようにGemma Scope 2・Llama Scope等の大型モデル×
  18種類の組み合わせへスケールする場合は、GPUによる高速化が実質的に必要に
  なると考えられる。
- ローカル環境ではPython 3.12かつ公式のネットワーク配布元に制約がないため、
  `requirements_demo.txt`の固定バージョンをそのまま使えた。CPU実行時に必要
  だった「バージョンを緩める」対処(1節参照)は、環境(Python 3.12・ネットワーク
  制約なし)さえ揃えば不要だったことも確認できた。

## 6. 結論(更新)

- クラウドCPU環境とローカルGPU環境の両方で、「学習済みSAE座標の方がランダム
  回転よりも振る舞いを足し算的に説明できる」という論文の中心的な主張を同一の
  数値で再現できた。環境(CPU/GPU、Python 3.11/3.12)が変わっても結果は変わらず、
  再現性の高さを追加で確認できた。
- GPUを使うことで実行時間を約4.2倍短縮できた。今回の縮小デモの規模では
  CPUでも十分だったが、論文本体のフルスケール実験(大型モデル×18組み合わせ)
  ではGPUの恩恵がより大きくなると考えられる。
