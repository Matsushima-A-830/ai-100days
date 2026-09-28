<#
.SYNOPSIS
    ai-100days の成果物(experiments/articles/posts)を Obsidian Vault に取り込む。

.DESCRIPTION
    夜の確認・マージ作業のあとに手動で実行する想定。
    1. リポジトリを最新化(git pull)
    2. experiments/day-N が存在し、まだ Vault に取り込んでいない日を探す
    3. README / results / 記事下書き / 投稿案をまとめて1つのノートにする
    4. Vault の Days/day-N.md を作成し、00-Index.md に行を追記する

.PARAMETER RepoPath
    ai-100days リポジトリのローカルパス。

.PARAMETER VaultPath
    Obsidian Vault のパス。

.PARAMETER Force
    既にノートが存在する日も上書きして再取り込みする。

.EXAMPLE
    powershell -File tools\sync-to-obsidian.ps1
#>

param(
    [string]$RepoPath = "\\wsl.localhost\Ubuntu\home\matsu\workspace\ai-100days",
    [string]$VaultPath = "$env:USERPROFILE\Documents\ObsidianVaults\ai-100days",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

function Get-FileTextOrEmpty {
    param([string]$Path)
    if (Test-Path $Path) {
        return (Get-Content -Path $Path -Raw -Encoding UTF8)
    }
    return ""
}

Write-Host "=== ai-100days -> Obsidian sync ===" -ForegroundColor Cyan

if (-not (Test-Path $RepoPath)) {
    throw "RepoPath not found: $RepoPath"
}
if (-not (Test-Path $VaultPath)) {
    throw "VaultPath not found: $VaultPath (先に Vault を作成してください)"
}

$daysDir = Join-Path $VaultPath "Days"
if (-not (Test-Path $daysDir)) {
    New-Item -ItemType Directory -Force -Path $daysDir | Out-Null
}

Push-Location $RepoPath
try {
    Write-Host "Pulling latest main..." -ForegroundColor Yellow
    git pull origin main
} finally {
    Pop-Location
}

$expRoot = Join-Path $RepoPath "experiments"
if (-not (Test-Path $expRoot)) {
    Write-Host "experiments/ ディレクトリがまだありません。同期対象なし。" -ForegroundColor Yellow
    exit 0
}

$dayDirs = Get-ChildItem -Path $expRoot -Directory -Filter "day-*" | Sort-Object Name
if (-not $dayDirs) {
    Write-Host "experiments/day-* がまだありません。同期対象なし。" -ForegroundColor Yellow
    exit 0
}

$syncedAny = $false

foreach ($dir in $dayDirs) {
    if ($dir.Name -match '^day-(\d+)$') {
        $n = $matches[1]
    } else {
        continue
    }

    $noteName = "day-{0}.md" -f $n
    $notePath = Join-Path $daysDir $noteName

    if ((Test-Path $notePath) -and (-not $Force)) {
        continue
    }

    $readme = Get-FileTextOrEmpty (Join-Path $dir.FullName "README.md")
    $results = Get-FileTextOrEmpty (Join-Path $dir.FullName "results.md")
    $article = Get-FileTextOrEmpty (Join-Path $RepoPath ("articles\day-{0}.md" -f $n))
    $posts = Get-FileTextOrEmpty (Join-Path $RepoPath ("posts\day-{0}.md" -f $n))

    $status = "unknown"
    if ($article -match 'published:\s*true') {
        $status = "published"
    } elseif ($article -match 'published:\s*false') {
        $status = "draft"
    }

    $syncDate = Get-Date -Format "yyyy-MM-dd"

    $noteBody = @"
---
day: $n
sync_date: $syncDate
status: $status
tags: [ai100days, day]
source_repo: https://github.com/Matsushima-A-830/ai-100days/tree/main/experiments/day-$n
---

# Day $n

## 検証ログ (experiments/day-$n/README.md)

$readme

## 検証結果 (experiments/day-$n/results.md)

$results

## Zenn記事下書き (articles/day-$n.md)

$article

## X投稿案 / note原稿 (posts/day-$n.md)

$posts

## リンク

- [GitHub: experiments/day-$n](https://github.com/Matsushima-A-830/ai-100days/tree/main/experiments/day-$n)
- [GitHub: articles/day-$n.md](https://github.com/Matsushima-A-830/ai-100days/blob/main/articles/day-$n.md)
- [GitHub: posts/day-$n.md](https://github.com/Matsushima-A-830/ai-100days/blob/main/posts/day-$n.md)
"@

    Set-Content -Path $notePath -Value $noteBody -Encoding UTF8
    Write-Host "Synced day-$n -> $notePath" -ForegroundColor Green
    $syncedAny = $true

    # Index.md に行を追記(まだ無ければ)
    $indexPath = Join-Path $VaultPath "00-Index.md"
    $indexContent = Get-Content -Path $indexPath -Raw -Encoding UTF8
    $rowMarker = "| $n |"
    if ($indexContent -notmatch [regex]::Escape($rowMarker)) {
        $row = "| $n | $syncDate | $status | [[Days/day-$n]] |"
        Add-Content -Path $indexPath -Value $row -Encoding UTF8
    }
}

if (-not $syncedAny) {
    Write-Host "新規に同期する日はありませんでした(既に全て取り込み済み)。" -ForegroundColor Yellow
} else {
    Write-Host "同期完了。" -ForegroundColor Cyan
}
