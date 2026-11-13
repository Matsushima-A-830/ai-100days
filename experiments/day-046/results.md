# Day 046 results — PurpleDoubleD/locally-uncensored

Routine環境の制約により未検証だった部分は、2026-11-13にローカルPCで検証済み(末尾の「ローカル検証」節を参照)。

検証に着手する前段階(リポジトリの取得・ライセンス確認・依存インストールの可否・Ollama導入元への
ネットワーク到達性)を確認したところ、下記2点が重なりコア機能(ローカルチャット・コーディング
エージェント)を一切実行できなかった。詳細は [`README.md`](./README.md) を参照。

1. クローンしたリポジトリ自身のコード実行(`npm install`)が、本Routine実行環境の権限自動分類器により
   `[Code from External]` として拒否された(cwdをclone先の内側/外側のどちらにしても拒否された)。
2. Ollamaのインストール元ホスト(`ollama.com`)が本Routine実行環境のネットワークポリシーで
   ブロックされていた(`CONNECT` 403)。

1はDay 024・Day 032・Day 043で遭遇した「本Routineの無人自動実行モードが外部コードの実行を拒否する」
制約と同種、2は過去のCLAUDE.md「書かない(Routine環境の制約)」の既存例(ネットワーク制限による
自動ダウンロードのブロック)と同種の、本Routine実行環境固有の制約と判断した。いずれも対象ツール
自体の欠陥ではないため、記事等には書かない。

`npm install` が通らないため、ブラウザ向け開発モード(`npm run dev`)・デスクトップビルド
(`npm run tauri:build`)のいずれも後続作業として実行できず、チャット機能・コーディングエージェント
機能の動作確認(今回の検証の核心)には到達できなかった。

静的に確認できた事実(読んだだけで、動かして確認したわけではない内容):

- ライセンス: `LICENSE`ファイル全文がAGPL-3.0(GNU AFFERO GENERAL PUBLIC LICENSE Version 3)。
  `package.json`の`"license": "AGPL-3.0-only"`とも一致。
- アーキテクチャ: Tauri(Rust+React/Vite)デスクトップアプリ本体 + `dev-server/`配下のNodeサーバーが
  ブラウザ向け開発モードでOllama連携・ファイルアクセス・シェル実行等をプロキシする構成。
- 「Bring your own engine」としてOllama/LM Studio/Jan/GPT4All/KoboldCpp/llama.cpp/vLLM/LocalAI/
  text-generation-webui/TabbyAPI/Aphrodite/SGLangの12種類を自動検出すると明記。
- CLI専用モード・`--host`フラグ・ヘッドレスサーバー専用モードはREADME上存在しない
  (リモートアクセスはLocal API〈OpenAI互換、ポート8129〉かRemoteタブ〈LAN、ポート11435〉経由)。

---

## ローカル検証(2026-11-13, 人間のPC)

### 環境

- OS: Windows + WSL2(Linux 6.6.87.2-microsoft-standard-WSL2)
- CPU: AMD Ryzen 7 7700(8コア16スレッド)/ RAM 30GiB
- GPU: NVIDIA GeForce RTX 5060 Ti 16GB(ドライバ 610.88)
- Node v26.8.2 / npm 11.19.1 / Ollama 0.35.1(インストール済み、モデルも既存のものを利用)
- 対象: `PurpleDoubleD/locally-uncensored` HEAD `3dff4291`(2026-11-09)、package.jsonのversion 3.0.10
- 操作: ブラウザ向け開発モード(`npm run dev`)を起動し、Playwright同梱のChromiumでUIを操作した。
  スクリーンショットは `screenshots/`、エージェントのツール呼び出しログは `logs/` に保存。

### 1. 依存インストールと起動

```
$ npm ci --ignore-scripts --loglevel=error
added 625 packages, and audited 626 packages in 43s
14 vulnerabilities (4 low, 9 moderate, 1 high)
elapsed 43.04 s
```

(`--ignore-scripts` でpostinstall等のライフサイクルスクリプトは実行していない。その状態でも `npm run dev` は問題なく起動した。)

```
$ npm run dev
[Python] Resolved: python3
[Ollama] Already running
[Whisper] faster-whisper not installed — STT disabled
[WebSearch] SearXNG not available (connection refused or timeout)
  VITE v8.1.6  ready in 403 ms
  ➜  Local:   http://localhost:5273/
[ComfyUI] Not found. Set COMFYUI_PATH in .env or install ComfyUI.
```

- 開発サーバーのポートは **5273**(`vite.config.ts` の `DEV_PORT` 既定値。`LU_DEV_PORT` で変更可)。
  Routine側READMEに書いていた5173は推測で誤りだったので修正した。
- 起動時に既に動いているOllamaを自動検出した。ComfyUI・faster-whisper・SearXNGは未導入のため無効化されるだけで起動は妨げない。

### 2. オンボーディング(4ステップ)

1. Engine: 既定は「LU Engine(同梱エンジン)」。「Use another engine (Ollama, LM Studio…)」を押すと
   `1 backend detected — Ollama is running. localhost:11434` と表示され、Ollamaを選択できた。
2. Image & Video: ComfyUIのインストール提案 → Skip。
3. Model: 「Models you already have」にOllamaの既存モデル5つが列挙された。`qwen2.5-coder:3b-instruct-q4_K_M` を選択。
   (同画面のおすすめは「Qwen 2.5 7B Abliterated (Starter)」4.4GiB と「Qwen 3.5 9B Abliterated — Agent-ready」5.2GiB。)
4. Documents: 埋め込みモデル nomic-embed-text(84MB)の導入提案 → Skip。

完了画面の文言は「The LU Engine is ready.」で、Ollamaを選んだ場合でも同梱エンジン前提の文言のままだった(軽微な表示上の不整合)。

### 3. チャット(qwen2.5-coder:3b-instruct-q4_K_M)

質問: `日本の首都はどこですか?理由を1文で添えて、日本語で答えてください。`

```
日本の首都は東京です。理由は、日本の経済、政治、文化の中心地であるためです。
126 in · 27 out
Context window 162/16K
```

- 送信から表示が増え始めるまで約0.55秒、応答が止まるまで約5.6秒(Playwrightで画面テキストの変化を監視して計測。
  モデルのロード時間を含む初回応答)。
- `ollama ps` → `qwen2.5-coder:3b-instruct-q4_K_M  2.7 GB  100% GPU  16384`(GPUで実行)。
- スクリーンショット: `screenshots/chat-3b.png`

参考: GPU無し(CPUのみ)の速度。アプリ経由ではなく、同じ質問をOllama APIに直接 `num_gpu` を指定して送って計測した。

```
num_gpu=0   日本の首都は東京です。 | total 3.67s load 3.07s eval 8 tok 25.8 tok/s
num_gpu=99  日本の首都は東京です。理由は、日本の歴史的と文化的な中心地で、大都市であります。 | total 1.81s load 1.51s eval 28 tok 141.6 tok/s
```

3BモデルはCPUのみ(Ryzen 7 7700)でも約26 tok/sで、チャット用途なら実用的な速度。

### 4. コーディングエージェント(Codeタブ)

#### 課題

意図的にバグを入れた小さなPythonプロジェクト(`git init`済み)を用意した。

```
$ cat calc.py
def add(a, b):
    return a - b  # bug: should be a + b


def mul(a, b):
    return a * b

$ cat test_calc.py
from calc import add, mul

assert add(2, 3) == 5, f"add(2, 3) returned {add(2, 3)}"
assert mul(2, 3) == 6
print("all tests passed")

$ python3 test_calc.py
AssertionError: add(2, 3) returned -1
```

指示(全モデル共通):
`test_calc.py fails. Read calc.py and test_calc.py, fix the bug in calc.py, then run `python3 test_calc.py` to confirm it passes.`

- 作業フォルダの指定: ブラウザ版では右パネルの「Select folder...」を押すと `window.prompt('Enter folder path:')` でパスを入力する方式
  (デスクトップ版はネイティブのフォルダ選択ダイアログ)。
- 権限モードは既定の「Ask」。`shell_execute` は「needs your ok」と表示され Run / No / Accept without asking の承認待ちになる。
  ファイル編集は即時反映されず「Pending (n)」としてdiff付きでステージされ、Apply all / Reject all で反映する。
- 安全のため、承認は `python3 test_calc.py` の実行と `calc.py` への編集だけに限定するスクリプトで行った。
- ヘッダーに「Small-Model」バッジが表示される(小型モデル向けのモードとみられる。今回は既定のまま)。

#### 結果

| モデル | 試行 | 結果 | 所要時間 |
|---|---|---|---|
| qwen2.5-coder:3b-instruct-q4_K_M | 2回(クリーンな状態で) | 2回とも ❌ calc.py と test_calc.py を読み、テストを実行して失敗を確認した後、**修正もメッセージも出さずに終了** | 約11秒 |
| qwen2.5:7b-instruct | 2回 | 2回とも ❌ 存在しない `src/` ディレクトリを探して `file_list src` → `file_read src/calc.py` → `file_read src/test_calc.py` を繰り返し、アプリの **Loop guard が停止** | 約10秒 |
| qwen2.5:14b-instruct | 1回(承認スクリプトの不具合を直した後の1回) | ✅ `file_edit` で `return a - b` → `return a + b` を提案、Apply後にテスト通過、変更内容を要約して終了 | 約15秒 |

3Bのログ(`logs/code-3b-steps.txt`、抜粋):

```
file_read  calc.py
file_read  test_calc.py
shell_execute  python3 test_calc.py
Error (1): AssertionError: add(2, 3) returned -1
4,733 in · 177 out
(ここで終了。file_editも最終メッセージも無し)
```

7Bのログ(`logs/code-7b-steps.txt`、抜粋):

```
⛔ Loop guard halted the run: same tool sequence repeated 3× in a row.
file_list  /home/matsu/work-day046/code-sandbox/src      → The folder is empty.
file_read  /home/matsu/work-day046/code-sandbox/src/calc.py
file_read  /home/matsu/work-day046/code-sandbox/src/test_calc.py
(同じ3手をもう一度)
(halted: same tool sequence repeated 3× in a row. The model is looping. Try a stronger model for multi-step code tasks, or rephrase the instruction.)
7,059 in · 182 out
```

14Bのログ(`logs/code-14b-steps.txt`、要約):

```
file_read  calc.py
file_read  test_calc.py
file_edit  calc.py  {"old_string": "return a - b  # bug: should be a + b", "new_string": "return a + b  # fixed"}
           → Pending(ステージのみ、未反映)
shell_execute  python3 test_calc.py → Error (1): AssertionError: add(2, 3) returned -1
           (ステージ済みの編集がまだ反映されていない状態でテストが走った。この直後に Apply all を押した)
"The assertion error indicates that the add function is still returning -1 ... Let's confirm the fix in calc.py and re-run the test."
file_edit  calc.py  → file_edit: old_string not found in .../calc.py. (反映済みのため)
shell_execute  python3 test_calc.py → all tests passed
"The test now passes, confirming the fix in calc.py was applied correctly. ..."
10,051 in · 385 out
Applied staged change: /home/matsu/work-day046/code-sandbox/calc.py
```

```
$ git diff
-    return a - b  # bug: should be a + b
+    return a + b  # fixed
$ python3 test_calc.py
all tests passed
```

観察:

- エージェントのツール基盤(ファイル読み込み・diff付きステージング・承認付きシェル実行・ループ検出)は3モデルとも正常に動いた。
  成否を分けたのはモデル側の能力で、今回の単純なバグ修正では3B・7Bは失敗、14Bで成功した。
  アプリ自身もオンボーディングでエージェント用途には9Bの「Agent-ready」モデルを勧めており、7Bの停止時にも
  「Try a stronger model for multi-step code tasks」と案内を出した。
- Askモードでは、ファイル編集がステージされたままでもエージェントは次のツール(テスト実行)に進むため、
  承認前のテストは必ず失敗する。14Bはそれを見て再編集→再テストで回復したが、承認のタイミング次第で余分な往復が発生する。
- Loop guardは7B(同じツール列の3回繰り返し)と、別試行の14B(同じ計画文の3回繰り返し、後述)の両方で作動し、無限ループを防いだ。

#### 補足: 検証手順上の不備で無効とした試行(記事には使わない)

- 14Bの初回試行は、承認スクリプトがPendingのパスを相対パス `calc.py` とだけ比較していたため、
  正しい修正(絶対パス表示)を10回Rejectしてしまった。モデルは同じ修正を提案し続け、最終的に
  「the model wrote the same plan 4 times ... and kept starting over」としてLoop guardが停止した。スクリプトを直して再実行したものが上表の結果。
- 3Bで作業フォルダ未指定(既定の `~/agent-workspace`、存在しない)のまま走らせた試行が1回あった(`python3 test_calc.py` を5回実行し、
  誤った内容の test_calc.py 新規作成を3件ステージ → 未適用)。フォルダ指定漏れは筆者側のミスなので結果から除外。
- 14Bを動かした直後(14Bが約15GBのVRAMを占有したまま)に3B・7Bを再試行した2回は、どちらも「Responding / Working」のまま9分以上進まなかった。
  Ollama単体は直後に正常応答(2.3秒)しており、VRAMの空きが無い状態でのモデル切り替えが原因とみられるが確証は無い。
  その後、同条件(クリーンなプロファイル)で再試行した3B・7Bは上表どおり約10秒で終了し、再現しなかった。

### 5. スコープ外

- 画像・動画生成(ComfyUI必須、VRAM 6〜12GB以上)は今回試していない。
- デスクトップ版(Tauri)のビルド・起動は試していない。ブラウザ向け開発モードのみ。
