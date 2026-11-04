---
title: "7倍速の動画生成Wave Forcingは、GPU8基の前に依存パッケージが足りず動かなかった"
emoji: "🌊"
type: "tech"
topics: ["ai", "llm", "videogeneration", "diffusionmodel", "gpu"]
published: false
---

## これは何の記事か

海外AIネタ100日チャレンジ、Day 037。今回取り上げるのは、上海交通大学のDENG Labが出した動画拡散モデルの高速化手法「Wave Forcing」。論文・推論コード・学習済みモデル重みがすべて公開されており、執筆時点(2026年11月)でZenn・Qiita・noteを検索した範囲では日本語の言及は0件だった。

- 論文: https://huggingface.co/papers/2611.00859 (arXiv:2611.00859)
- コード: https://github.com/SJTU-DENG-Lab/WaveForcing (Apache License 2.0)
- 学習済み重み: https://huggingface.co/SJTU-DENG-Lab/WaveForcing-1.3B
- プロジェクトページ: https://sjtu-deng-lab.github.io/WaveForcing/

筆者が実際にリポジトリをcloneし、`LICENSE`・`README.md`・推論ランタイムのコード(`wave_rt/config.py`など)を読んで確認した内容と、実際にインストール・実行を試みてわかったことを書く。
結論を先に書くと、GPUを8基用意できたとしても、現状このツールは動かせない。
READMEのクイックスタートが依存している推論ランタイムの中核クラスが、公開されているパッケージのどこにも存在しないという、GPU基数とは無関係の依存関係の不備が見つかったためである。

## 背景: ストリーミング動画生成とパイプライン化の難しさ

動画拡散モデルは、通常チャンク(数フレームのまとまり)単位でノイズ除去を繰り返して動画を生成する。
リアルタイム・ストリーミング的に生成を続けるには、複数のGPUにチャンクの処理を分担させてパイプライン化したいところだが、素朴な拡散モデルの設計では「新しいチャンクのノイズ除去には、直前のチャンクが完全にノイズ除去し終わっている必要がある」という逆方向の依存関係が生じやすく、これがGPU間のパイプライン化を妨げる。

## Wave Forcingの仕組み

Wave Forcingは、Wan2.1-T2V-1.3Bをベースに、新しいチャンクが「ノイズ除去済みの直前チャンク」だけでなく「ノイズ除去が進行中の、混在したノイズレベルを持つ先行チャンク(mixed-noise frontier)」も条件として参照できるよう、チャンク単位の因果アテンションを設計し直した手法。
これにより、各チャンクの処理が前のチャンクの完了を待たずに進められるようになり、複数GPUのレプリカにチャンクの各ステージを割り振ってパイプライン的に流す「Wave Parallelism」が可能になる。

この並列化を実際に動かすための専用ランタイムが「WaveRT」で、GPU間でチャンクごとのK/V(キー・バリュー)状態を一方向にやり取りしながら、通信をより長いアテンション計算の裏に隠す(プリフェッチ)ことでオーバーヘッドを抑える設計になっている。
リポジトリの`wave_rt/denoiser/exchange/`には、この通信方式のバリエーション(sync・overlap・one-sided・staggered・relay・pagedなど)が複数実装されており、README上の結果表でもこの`exchange-mode`による比較が載っている。

## ライセンスと構成を実際に確認した

```
$ git clone --depth 1 https://github.com/SJTU-DENG-Lab/WaveForcing.git
$ cat LICENSE | head -5
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/
```

推論コード本体(`wave_rt/`・`naive_rt/`)はApache License 2.0。
一方`training/`配下の参考学習コード(RollingForcingベースのトレーナー)だけは別のacademic-use licenseが適用される、とREADMEに明記されている。
推論して使う分にはApache-2.0の範囲で問題ない。

## ハードウェア要件を読んで気づいたこと

READMEのQuick Startは、8基のGPUを使う「5+2」構成(5段のdenoisingステージ+1段のclean-KV store rank+2段のstreaming VAEステージ)がそのまま最小単位として示されている。
`wave_rt/config.py`を読むと、WaveRTの並列度`wp_size`には`rf_step + 1 == wp_size`という制約が課されていて、値としては`wp_size`を1まで下げること自体は可能に見える。
しかし`wp_size=1`は`rf_step=0`、つまりチャンク単位のパイプライン化ステージが実質ゼロになる退化的な設定になり、Wave Forcingが提案する「チャンク単位の因果アテンションによるパイプライン化」という手法の中身そのものが機能しなくなる。
つまりこの手法は、設計上そもそも複数GPUでの運用を前提にしていると読める。

## 著者らが報告している数値(筆者自身の実測ではない点に注意)

以下はREADMEの「Current results」表に記載されている、著者ら自身の実測値で、8×NVIDIA H200・832×480・399 latent frames(1593 decoded frames)という条件での計測。

| モデル | ステップ数 | 構成 | Steady FPS (p50) | E2E FPS |
|---|---:|---|---:|---:|
| WaveForcing-1.3B | 4 | 4+3・BF16/FA3 | 152.1 | **134.8** |
| WaveForcing-1.3B | 5 | 5+2・BF16/FA3 | 99.6 | 96.5 |

比較対象として示されている単一GPUベースラインは19.06 FPSで、8×H200構成の134.8 FPSは**7.07倍**に相当すると著者らは報告している。
1593フレームのデコードが約11.8秒で終わる計算になる。

これらはあくまで論文・README内の著者らによる報告値であり、筆者自身がこの環境を再現して確認した数値ではない。
そのため本記事では「動かしてみた」ではなく「読んでみた」というトーンにとどめている。

## 実際にインストール・実行を試みてわかったこと

GPUを用意できた段階で、READMEのクイックスタート通りに手を動かしてみた。
最初の一歩である`uv sync`の時点で、想定と違う結果になった。

```
$ git clone https://github.com/SJTU-DENG-Lab/WaveForcing.git && cd WaveForcing
$ uv sync
# torch==2.11.0+cu128 などは入るが、sglangは一切インストールされない
$ .venv/bin/python -c "import sglang"
ModuleNotFoundError: No module named 'sglang'
```

`pyproject.toml`のコメントには「`sgl-dlab`という編集可能パッケージをインストールする」という記述があるが、`sgl-dlab`というディレクトリやパッケージはこのリポジトリのどこにも存在せず、READMEにも入手方法の説明がない。
公開されているPyPI版の`sglang`を自分で追加インストールしてみたところ、`import`自体は通ったが、`wave_rt`が既定で要求する`WanRollingForcingPipeline`というパイプラインクラスを実際にロードしようとすると、次のように失敗した。

```
[rank0]: ValueError: Pipeline class 'WanRollingForcingPipeline' not found in registry.
Available pipelines: ['ComfyUIFluxPipeline', ..., 'WanCausalDMDPipeline', 'WanDMDPipeline',
'WanImageToVideoDmdPipeline', 'WanImageToVideoPipeline', 'WanPipeline', 'ZImagePipeline']
```

リポジトリ全体と、公開版`sglang`のソース全体の両方を検索しても、`RollingForcing`という文字列は`wave_rt/config.py`の既定値の文字列以外に一度も出てこない。
つまり`WanRollingForcingPipeline`は、著者らが社内で使っている非公開フォーク(`sgl-dlab`)にしか存在しないクラスで、公開されている材料だけでは原理的に組み立てられない。

README記載の「単一GPUベースライン(19.06 FPS)」に対応する比較スクリプト`scripts/wrt_ref_single.py`も試したが、こちらは別のAPIの食い違いにも遭遇した。

```
$ .venv/bin/python scripts/wrt_ref_single.py --num-frames 6 --out /tmp/wf-out
TypeError: maybe_init_distributed_environment_and_model_parallel() got an
unexpected keyword argument 'cfg_degree'
```

実際の関数には`cfg_degree`という引数は存在せず、`enable_cfg_parallel`という名前に変わっていた。
これを直して再実行すると、今度は先ほどと同じ`WanRollingForcingPipeline not found in registry`で止まった。
つまりAPIのズレを一つ直しても、根本原因である依存パイプラインの不在は変わらず、この比較スクリプトも完走しない。

## まとめ

Wave Forcingは、ストリーミング動画生成のパイプライン並列化を妨げていた「チャンク間の逆方向依存」を、チャンク単位の因果アテンションという形で設計から取り除き、複数GPUへの分散を実際に機能させる、という方向性の提案だった。
コード・重みともに公開されApache-2.0で使えることも確認できた一方、実際に手を動かしてみると、GPUを8基用意する以前の段階で止まることがわかった。
`wave_rt`が要求する核心のパイプラインクラスが、著者らの非公開フォークにしか存在せず、公開されているREADME・`pyproject.toml`の指示だけでは原理的に再現できない。
これはGPU環境を持たない実行環境固有の制約ではなく、リポジトリと依存関係の公開範囲が食い違っているという、ツール自体に直接関係する不具合として記録しておく。
