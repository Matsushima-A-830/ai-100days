# Day 042 — ranxianglei/billion-context を検証する

対象: https://github.com/ranxianglei/billion-context (MIT License + 製品組み込み時のクレジット表記条項)

「既存のコーディングエージェント(Claude Code/Codex/OpenCode等)とモデルAPIの間に挟まる
プロキシとして、会話を可逆的に圧縮しプロンプトキャッシュを保ったまま小さいコンテキスト窓で
長時間セッションを扱えるようにする」というツール。本Routine自身が使っているClaude Code CLIを
`bili claude` でそのままラップできるかを自己言及的に検証した。

詳細な実行ログ・結果は [`results.md`](./results.md) を参照。

## 再現手順

前提: Node.js 20以上(確認環境はv22.23.4)、`claude` CLIがログイン済みであること。

```bash
# 1. 依存をプロジェクトローカルに入れる(グローバルインストールは環境によって
#    承認ポリシーでブロックされる場合があるため、プロジェクトローカル推奨)
mkdir sandbox && cd sandbox
npm init -y
npm install billion-context

# 2. Claude Code CLIをbili経由でラップして単発の質問を投げる
cd scratch-run_or_anywhere
../node_modules/.bin/bili claude -- -p "2+2? Answer with just the number."
# => プロキシ起動ログの後、"4" が返れば成功

# 3. biliが注入したMCPツール(acp_status)を呼んでみる
#    (非対話 -p モードでは事前に --allowedTools での許可が必要)
../node_modules/.bin/bili claude -- \
  -p "Call the acp_status tool and report its raw output verbatim." \
  --output-format json --allowedTools "mcp__bili__acp_status"
```

## Before/After比較の再現

`scripts/` 配下に同梱した4本のスクリプトで、本記事中の表を再現できる
(実行には `npm install billion-context` 済みの `node_modules/.bin/bili` へのパスが必要。
各スクリプト冒頭の `BILI_BIN` / `CHUNK_DIR` 相対パスは実行時のディレクトリ構成に合わせて調整すること)。

```bash
mkdir scratch-run && cd scratch-run
python3 ../scripts/generate_chunks.py   # chunk_part_aa..af を生成
cd ..
python3 scripts/driver.py direct direct-run     # 直接 claude -p (4ターン) + 累計usage記録
python3 scripts/driver.py bili bili-run         # bili claude -p (4ターン) + acp_status 確認
python3 scripts/continue_direct.py <direct-runのsession_id>   # 直接系をさらに2ターン追加
python3 scripts/continue_bili.py <bili-runのsession_id>       # bili系をさらに2ターン追加(圧縮が発動する)
```

各スクリプトは `claude --output-format json` の `usage` と `total_cost_usd` をそのまま
`summary.json` / `summary2.json` に保存する。実際に得られた生の出力は
[`logs/`](./logs/)(`direct-run-turns1-4.json` 等)と、biliのプロキシログから圧縮発動部分を
抜粋した [`logs/bili-compression-log-excerpt.txt`](./logs/bili-compression-log-excerpt.txt) に残した。

## 制約・注意

- `npm install -g billion-context` はこのクラウドRoutine実行環境のコマンド承認ポリシーで
  ブロックされた。プロジェクトローカルインストール(`npm install billion-context` → 生成される
  `node_modules/.bin/bili` を直接呼ぶ)で代替でき、動作上の差はない。これは検証対象ツール自体の
  制約ではなくこの実行環境固有の事情のため、記事本文では詳述していない。
- 今回の圧縮発動は「モデルが`compress`ツールを明示的に呼んだ」のではなく、biliが文脈窓の
  上限に迫ったと判断して自動で行う「preflight overflow compress」だった。モデル主導の
  `compress`呼び出しそのものを明示的に誘発する再現は今回は行っていない。
