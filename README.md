# ai-100days

海外AIネタ100日チャレンジ — 毎日、海外で話題のAI関連ニュース/OSS/論文を見つけて実際に検証し、
Zenn/X/noteで日本語発信するための作業リポジトリ。

運用ルールは [CLAUDE.md](./CLAUDE.md) を参照。

## 進め方

1. 朝: リサーチRoutine(自動)が `backlog.md` にネタ候補を追加
2. 通勤中: `today.md` にその日のネタを書いてコミット
3. 昼: 実装Routine(自動)が検証・記事下書き・PR作成
4. 夜: PRを確認・再現・マージ、Zenn公開、X投稿、`tools/sync-to-obsidian.ps1` でローカルVaultに蓄積

## ローカルへの蓄積(Obsidian)

PRをマージしたあと、PowerShellで以下を実行すると、その日の検証ログ・記事下書き・投稿案が
ローカルのObsidian Vault(`C:\Users\matsu\Documents\ObsidianVaults\ai-100days`)に
1ノートとしてまとめて取り込まれ、`00-Index.md` にも一覧行が追記される。

```powershell
powershell -File tools\sync-to-obsidian.ps1
```

このリポジトリの最新化(`git pull`)もスクリプトが自動で行う。既に取り込み済みの日はスキップされる
(再取り込みしたい場合は `-Force` を付ける)。
