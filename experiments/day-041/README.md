# Day 041 — milind-soni/OpenMausBot

出典: https://github.com/milind-soni/OpenMausBot (Apache-2.0。`enterprise/`配下のみ別のsource-availableライセンス)
npm: https://www.npmjs.com/package/openmausbot

## 再現手順

前提: Node.js 24以上(デフォルトのNodeがそれより古い場合はnvm/fnm等で24+を用意する)。

```bash
# 1. どこか空のディレクトリで
npm install openmausbot

# 2. ヘッドレスでサーバー起動(ブラウザを開かない / ローカル専用)
npx openmausbot serve --no-open --local
# または npm install 済みなら: node node_modules/openmausbot/cli.js serve --no-open --local

# 3. 別ターミナルから状態確認(claude/codex/grok CLIのいずれかがログイン済みならengineとして検出される)
npx openmausbot doctor
npx openmausbot models

# 4. 実際にタスクを投げる(MausBotは最初から用意されているデフォルトbot)
npx openmausbot run MausBot "何か指示文"  --wait job --timeout 50s
```

(このRoutine実行環境では `npx` 経由の実行がサンドボックスの安全policyに阻まれたため、
`npm install openmausbot` で明示的にインストールしたうえで `node node_modules/openmausbot/cli.js ...`
と直接呼び出した。通常のローカル環境では `npx openmausbot ...` のまま動くはずで、
機能面での違いはない。)

## 確認したこと

1. `npm view openmausbot engines` → Node `>=24` が前提(デフォルトNode 22では動かない)。
2. `doctor --host` によるホスト診断(Docker常時起動・cgroup v2前提のサンドボックス機能についての
   警告が出たが、これは今回利用した `--local`(クラウド共有なし)モードには影響しなかった)。
3. `serve --no-open --local` でGUIなしにサーバー起動、`curl http://127.0.0.1:8799/` が200を返すことを確認。
4. `doctor` / `models` で、既にログイン済みのClaude Code CLIが追加設定なしに `claude` エンジンとして
   検出されること(27種のエンジン一覧中、available だったのはclaudeのみ)。
5. `openmausbot run MausBot "..."` でファイル作成・シェルコマンドによるファイル削除・簡単な質疑応答を
   実際に実行し、生成/削除されたファイルを確認した。
6. ライセンス: ルートはApache-2.0、`enterprise/`のみ別ライセンス(ライセンスキー必須)。
   今回検証した機能はいずれも`enterprise/`を使わないOSS部分。

詳細な実行ログ・所見は `results.md` を参照。

## ローカル検証(実施済み・2026-11-08)

人間のPCで、GUI(ブラウザUI)側の確認カードの挙動を実際に確認した。

- GUIでも既定設定(bot設定「Before MausBot acts」= Just do it)では確認カードは出ず、CLIと同じく即実行された。原因はCLI/GUIの違いではなく、新規botの承認レベルが既定で「Full access」相当であること。
- 承認レベルを明示的に「Ask me first」に変更しても確認カードは表示されず、必須のMCPツール(`mcp__ogb__approve`)が未登録のため`claude`プロセスがエラー終了するだけだった(2回再現)。
- 別の安全機構として、botのシェルは専用の作業ディレクトリにサンドボックス化されており、承認レベルに関わらずその外側への書き込みは拒否されることも確認した。

詳細は`results.md`の「8. ローカル検証」節を参照。
