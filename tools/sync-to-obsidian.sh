#!/usr/bin/env bash
# ai-100days の成果物(experiments/articles/posts)を Obsidian Vault に取り込む(WSL用)。
#
# 夜の確認・マージ作業のあとに WSL のターミナルから手動で実行する想定。
#   1. リポジトリを最新化(git pull)
#   2. experiments/day-N が存在し、まだ Vault に取り込んでいない日を探す
#   3. README / results / 記事下書き / 投稿案をまとめて1つのノートにする
#   4. Vault の Days/day-N.md を作成し、00-Index.md に行を追記する
#
# 使い方:
#   bash tools/sync-to-obsidian.sh [--force]
#
# 環境変数で上書き可能:
#   REPO_PATH  デフォルト: このスクリプトの1つ上のディレクトリ
#   VAULT_PATH デフォルト: /mnt/c/Users/matsu/Documents/ObsidianVaults/ai-100days

set -euo pipefail

REPO_PATH="${REPO_PATH:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
VAULT_PATH="${VAULT_PATH:-/mnt/c/Users/matsu/Documents/ObsidianVaults/ai-100days}"
FORCE=0
[[ "${1:-}" == "--force" ]] && FORCE=1

echo "=== ai-100days -> Obsidian sync (WSL) ==="

if [[ ! -d "$REPO_PATH" ]]; then
  echo "RepoPath not found: $REPO_PATH" >&2
  exit 1
fi
if [[ ! -d "$VAULT_PATH" ]]; then
  echo "VaultPath not found: $VAULT_PATH (先に Vault を作成してください)" >&2
  exit 1
fi

DAYS_DIR="$VAULT_PATH/Days"
mkdir -p "$DAYS_DIR"

echo "Pulling latest main..."
git -C "$REPO_PATH" pull origin main

EXP_ROOT="$REPO_PATH/experiments"
if [[ ! -d "$EXP_ROOT" ]]; then
  echo "experiments/ ディレクトリがまだありません。同期対象なし。"
  exit 0
fi

shopt -s nullglob
day_dirs=("$EXP_ROOT"/day-*)
shopt -u nullglob

if [[ ${#day_dirs[@]} -eq 0 ]]; then
  echo "experiments/day-* がまだありません。同期対象なし。"
  exit 0
fi

synced_any=0
INDEX_PATH="$VAULT_PATH/00-Index.md"

for dir in "${day_dirs[@]}"; do
  base="$(basename "$dir")"
  [[ "$base" =~ ^day-([0-9]+)$ ]] || continue
  n="${BASH_REMATCH[1]}"

  note_path="$DAYS_DIR/day-$n.md"
  if [[ -f "$note_path" && "$FORCE" -eq 0 ]]; then
    continue
  fi

  readme=""
  [[ -f "$dir/README.md" ]] && readme="$(cat "$dir/README.md")"
  results=""
  [[ -f "$dir/results.md" ]] && results="$(cat "$dir/results.md")"
  article=""
  article_link_path="articles/day-$n.md"
  article_file="$(ls "$REPO_PATH"/articles/day-"$n"-*.md 2>/dev/null | head -1)"
  if [[ -z "$article_file" && -f "$REPO_PATH/articles/day-$n.md" ]]; then
    article_file="$REPO_PATH/articles/day-$n.md"
  fi
  if [[ -n "$article_file" ]]; then
    article="$(cat "$article_file")"
    article_link_path="articles/$(basename "$article_file")"
  fi
  posts=""
  [[ -f "$REPO_PATH/posts/day-$n.md" ]] && posts="$(cat "$REPO_PATH/posts/day-$n.md")"

  status="unknown"
  if grep -qE 'published:\s*true' <<<"$article"; then
    status="published"
  elif grep -qE 'published:\s*false' <<<"$article"; then
    status="draft"
  fi

  sync_date="$(date +%Y-%m-%d)"

  cat > "$note_path" <<EOF
---
day: $n
sync_date: $sync_date
status: $status
tags: [ai100days, day]
source_repo: https://github.com/Matsushima-A-830/ai-100days/tree/main/experiments/day-$n
---

# Day $n

## 検証ログ (experiments/day-$n/README.md)

$readme

## 検証結果 (experiments/day-$n/results.md)

$results

## Zenn記事下書き ($article_link_path)

$article

## X投稿案 / note原稿 (posts/day-$n.md)

$posts

## リンク

- [GitHub: experiments/day-$n](https://github.com/Matsushima-A-830/ai-100days/tree/main/experiments/day-$n)
- [GitHub: $article_link_path](https://github.com/Matsushima-A-830/ai-100days/blob/main/$article_link_path)
- [GitHub: posts/day-$n.md](https://github.com/Matsushima-A-830/ai-100days/blob/main/posts/day-$n.md)
EOF

  echo "Synced day-$n -> $note_path"
  synced_any=1

  if ! grep -qF "| $n |" "$INDEX_PATH"; then
    echo "| $n | $sync_date | $status | [[Days/day-$n]] |" >> "$INDEX_PATH"
  fi
done

if [[ "$synced_any" -eq 0 ]]; then
  echo "新規に同期する日はありませんでした(既に全て取り込み済み)。"
else
  echo "同期完了。"
fi
