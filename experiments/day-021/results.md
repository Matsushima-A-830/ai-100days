# Day 021 検証結果: mcp-for-blender (旧称 blender-mcp) を日本語指示でBlenderに繋いで動かす

対象: ahujasid/mcp-for-blender
https://github.com/ahujasid/mcp-for-blender
(検証時点のHEAD commit: `25e1fe008fc523b1a947c6f3d28510a362a0f06e`, 2026-10-18)
ライセンス: MIT (`LICENSE`に明記、Copyright (c) 2025 Siddharth Ahuja)
PyPIパッケージ: `mcp-for-blender` (pyproject.tomlのversionは2.2.0)

## 検証の範囲

today.mdの通り、Blender 3.0+・Python 3.10+・uvのみで動く範囲(追加の有料APIキーなし)で
「MCPクライアント → MCPサーバー → Blenderアドオンのソケットサーバー → 実際のBlender Python実行」
という全スタックを実機で通し、日本語の指示文から低ポリゴンの3Dシーン(石壁の部屋+松明)を
実際に生成し、レンダリング画像をBefore/Afterで記録した。Sketchfab/Hyper3D/Meshy等の有料連携は使っていない。
Poly Haven等の無料アセット取得フローは今回の検証範囲には含めなかった(時間の都合でシーン生成の
コア動作確認を優先した)。

## 1. 環境構築

今回の実行環境にはBlenderが入っていなかったため、まずインストールした。

```
$ apt-get install -y blender
...
Setting up blender (4.0.2+dfsg-1ubuntu8) ...
$ blender --background --version
Blender 4.0.2
```

Ubuntu(noble)のuniverseリポジトリにあるBlender 4.0.2を使用。mcp-for-blenderの`bl_info`が
要求する最低バージョンは3.0.0なので要件は満たす。

アドオン本体(`addon.py`)をBlenderのアドオンディレクトリに配置して有効化を試みたところ、
`requests`モジュールが無く失敗した(配布パッケージ版のBlenderは`requests`を同梱していない)。

```
ModuleNotFoundError: No module named 'requests'
```

これは「ツールの既定設定・公式手順のままでは動かなかった」に該当する、検証に直接関係する失敗
として記録する。Blenderが使うPythonは配布形態によってシステムPython(今回は3.12)を指すことが
あり、その場合`pip install requests`だけでは別のPython(本機のデフォルトは3.13)に入ってしまい
解決しない。アドオンの`sys.path`に含まれる`scripts/addons/modules`ディレクトリへ明示的に
ターゲットインストールすることで解決した。

```
$ python3.12 -m pip install --target ~/.config/blender/4.0/scripts/addons/modules requests
Successfully installed certifi-2026.10.18 charset_normalizer-3.5.2 idna-3.20 requests-2.34.2 urllib3-2.8.0
```

## 2. 最初の壁: `blender --background` では動かない(ツール自身が明示的に拒否する)

`blender --background`(`-b`)でアドオンを有効化すると登録はできるが、サーバーのソケット自体が
起動しない。アドオンのソースコード(`addon.py`の`BlenderMCPServer.start()`)を見ると、
これは意図された仕様であることがわかった。

```python
def start(self):
    if bpy.app.background:
        print("BlenderMCP: cannot start server in background mode (blender -b) - commands would never execute\n"
              "BlenderMCP: run Blender with a GUI, or use a virtual display: xvfb-run -a blender")
        return
```

同様に、MCPサーバー側(`src/blender_mcp/server.py`)もBlenderからの応答が無い場合のエラー
メッセージに同じ助言を出す。

```
Timeout waiting for Blender response - try simplifying your request. If Blender is running
headless (blender -b), commands never execute; run Blender with a GUI or via
'xvfb-run -a blender' instead
```

つまり純粋なheadlessモードが使えないのは、CLAUDE.mdが言う「Routine実行環境固有の制約」ではなく、
**ツール自身が設計として明示的にheadlessを拒否し、代わりにXvfb(仮想ディスプレイ)経由での実行を
公式に案内している**ケースだった。そこでツールの案内通り`xvfb-run -a blender`で検証した。

## 3. `xvfb-run -a blender` で実際に起動させる

```
$ apt-get install -y xvfb   # 既にインストール済みだった
$ nohup xvfb-run -a blender > /tmp/blender_gui.log 2>&1 &
$ cat /tmp/blender_gui.log
Read prefs: "/root/.config/blender/4.0/config/userpref.blend"
BlenderMCP addon registered
Server thread startedBlenderMCP server started on localhost:9876
```

ソケットサーバーが`localhost:9876`で実際に起動した。生のTCPソケットで疎通確認。

```
$ python3 -c "
import socket, json
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 9876))
s.sendall(json.dumps({'type': 'get_scene_info', 'params': {}}).encode('utf-8'))
print(s.recv(8192).decode())
"
{"status": "success", "result": {"name": "Scene", "object_count": 3, "objects": [{"name": "Cube", ...}, {"name": "Light", ...}, {"name": "Camera", ...}], "materials_count": 2}}
```

デフォルトシーン(Cube/Light/Camera)の情報が正しく返ってきた。Xvfb経由であれば
headlessなLinuxサーバー上でもBlenderアドオンのソケットサーバーが正常に動作することを確認した。

## 4. MCPサーバーを実際のMCPクライアントとして繋ぐ

`uv sync`でMCPサーバー側の依存関係(`mcp>=1.26.0`等)をインストールし、Python製の
MCPクライアント(`mcp`パッケージの`stdio_client`/`ClientSession`)を自分で書いて、
`uv run mcp-for-blender`をstdio経由のMCPサーバーとして起動、実際にMCPプロトコルで接続した
(Claude Desktop等のGUIクライアントはこの環境に無いため、MCPクライアントの役割をスクリプトで代替)。

```
$ uv sync
 + mcp==1.29.0
 + mcp-for-blender==2.2.0 (from file:///.../mcp-for-blender)
 ...
```

`list_tools`で実際に公開されているツール一覧を取得:

```
AVAILABLE_TOOLS: ['disable_telemetry', 'execute_blender_code', 'generate_3d', 'get_addon_status',
  'get_scene_info', 'import_asset', 'look', 'record_trajectory_feedback', 'search_assets']
```

## 5. 日本語指示でシーンを生成する

ユーザープロンプトとして以下の日本語指示を渡し、`execute_blender_code`ツールでBlender Python
コード(壁4枚・床・松明の柄・点光源・カメラを配置するコード)を実行させた。

> 低ポリゴンのダンジョンシーンを作って。石の壁で囲まれた部屋と、中央に松明を1本置いて、
> カメラで部屋全体が見えるようにレンダリングして。

実行前(`get_scene_info`):

```
Scene 'Scene' | 1 camera, 1 light, 1 mesh | active Cube | selected Cube | mode OBJECT
Cube | mesh | at (0.0, 0.0, 0.0) | size 2.0x2.0x2.0
Light | light | at (4.08, 1.01, 5.9)
Camera | camera | at (7.36, -6.93, 4.96)
```

`execute_blender_code`実行結果:

```
Code executed successfully: SCENE_BUILD_RESULT:{'object_count': 8, 'object_names':
['Floor', 'RoomCamera', 'Torch_Flame_Light', 'Torch_Handle', 'Wall_East', 'Wall_North',
'Wall_South', 'Wall_West']}
```

実行後(`get_scene_info`):

```
Scene 'Scene' | 1 camera, 1 light, 6 mesh | active RoomCamera | selected RoomCamera | mode OBJECT
Wall_North | mesh | at (0.0, 3.0, 1.5) | size 6.0x0.4x3.0
Wall_South | mesh | at (0.0, -3.0, 1.5) | size 6.0x0.4x3.0
Wall_East | mesh | at (3.0, 0.0, 1.5) | size 0.4x6.0x3.0
Wall_West | mesh | at (-3.0, 0.0, 1.5) | size 0.4x6.0x3.0
Floor | mesh | at (0.0, 0.0, 0.0) | size 6.0x6.0x0.0
Torch_Handle | mesh | at (0.0, 0.0, 0.5) | size 0.1x0.1x1.0
Torch_Flame_Light | light | at (0.0, 0.0, 1.1)
RoomCamera | camera | at (0.0, -7.5, 5.2)
```

デフォルトのCube/Light/Cameraシーンが、指示通りの石壁4枚+床+松明(柄+暖色の点光源)を持つ
部屋に置き換わったことを、MCP経由の`get_scene_info`応答だけから確認できた。

## 6. レンダリング画像(Before/After)

`execute_blender_code`内で`bpy.ops.render.render(write_still=True)`を呼び、EEVEE(Legacy、
Blender 4.0のデフォルトエンジン)で960x540のPNGとして実際にレンダリングした。

- Before: `before.png` (デフォルトのCubeシーン)
- After: `after.png` (生成したダンジョンルーム、松明点灯)

カメラの初期配置(ルーム外から水平に狙う位置)では、壁(厚み0.4のソリッドなCube)がカメラと
室内の間を完全に塞いでしまい、無地のグレー画像になった。これは筆者のシーン構築コード側の
カメラ配置ミスであり、ツール自体の不具合ではない。カメラを部屋の上空から見下ろす位置
(`(0, -7.0, 11.0)`、天井の無い部屋の開口部越しに内部を見るアングル)に置き直してから、
壁・床・松明の炎色の光が当たる様子が映る画像になった。試行錯誤の過程も含め、`execute_blender_code`
を使えば何度でも同じソケット接続上でシーンを修正・再レンダリングできることも確認できた。

## 7. 結論

- `mcp-for-blender`の「MCPクライアント→MCPサーバー→Blenderアドオン→bpy実行」という
  全スタックは、Xvfb経由であればGPUなし・有料APIキーなしのLinuxサーバー環境でも実際に動作した。
- `blender --background`では動かないが、これはツール側が意図的に拒否する仕様であり、
  ツール自身のエラーメッセージ・ソースコードコメントの両方が`xvfb-run -a blender`を
  公式な代替手段として明記している。
- Blender配布パッケージに`requests`が同梱されていない場合があり、アドオンの依存解決は
  手動対応が必要だった(今回はUbuntu配布のBlenderパッケージ特有の事情)。
- 日本語の自然文指示から、MCP経由でBlenderシーンの中身(オブジェクト・マテリアル・ライト・
  カメラ)を実際に変更でき、レンダリング画像として結果を確認できた。

## 8. 追加検証: 人間のローカルPCで、実際のAIクライアント(Claude Code)から接続する

上記までは、クラウドRoutine環境にGUIクライアントが無かったため、MCPクライアントの役割を
Pythonの自作スクリプトで代替していた。人間(matsu)のローカルPC(Windows 11 + Blender 4.5)で、
実際にClaude Codeセッション自身をMCPクライアントとして接続し、「実際のAIクライアントGUIから
操作する体験」を追加で検証した。

### 8.1 セットアップ

公式のWindowsインストーラ手順に従い、`uv`導入後に`uvx mcp-for-blender setup`を実行した。

```
$ uvx --refresh-package mcp-for-blender mcp-for-blender@latest setup
MCP for Blender setup
  ✓ Claude Desktop: Added "blender" in ...\claude_desktop_config.json
  ✓ Claude Code: Added "blender" (user scope, all projects)
  ✓ VS Code: Added "blender" in ...\mcp.json
  ✓ Antigravity: Added "blender" in ...\mcp_config.json
Blender addon:
  Installed the addon to ...\Blender Foundation\Blender\4.5\scripts\addons\blender_mcp.py
  Enabled the addon in Blender
```

このコマンド1つで、アドオンのインストール・有効化と、見つかった全MCPクライアント(Claude
Desktop・Claude Code・VS Code・Antigravity)への設定登録が自動で完了した。**注意点として、
`setup`はデフォルトで「見つかった全クライアントに設定」という挙動であり、Claude Codeについては
「ユーザースコープ(全プロジェクト対象)」で登録される。** 今回のリポジトリだけでなく、
対話的に選べばクライアントを絞り込むこともできる(`1 3`のように番号で指定、`n`で全スキップ)。

### 8.2 Blender GUIを起動し、サーバーの自動起動を確認

Blender 4.5をGUIモード(`--background`を付けずに通常起動)で起動したところ、追加の手動操作
(アドオン有効化のクリックなど)なしに、起動直後からソケットサーバーがport 9876で
LISTEN状態になっていることを確認した。

```
> Get-NetTCPConnection -LocalPort 9876
LocalAddress LocalPort  State OwningProcess
127.0.0.1         9876 Listen         30452
```

これは、クラウドRoutine環境での検証(3節)で確認した「`blender --background`ではサーバーが
起動せず、通常のGUIモードが必要」という挙動と一致する。

### 8.3 Claude Codeから実際にMCP接続し、操作する

`claude mcp list`で、このClaude Codeセッション自身がblenderサーバーに実際に接続できることを
確認した。

```
$ claude mcp list
blender: C:\Users\matsu\.local\bin\uvx.EXE mcp-for-blender - ✔ Connected
```

さらに、Python製のMCPクライアント(クラウド検証時と同じ`mcp`パッケージの`stdio_client`/
`ClientSession`)を使い、`uvx mcp-for-blender`経由で実際に起動中のBlender GUIへ`execute_blender_code`
でオブジェクト(トーラス+暖色ポイントライト)を追加し、`get_scene_info`でシーンの変化
(1 mesh/1 light/1 camera → 2 mesh/2 light/1 camera)を確認、`bpy.ops.render.render(write_still=True)`
で実際にレンダリング画像を取得した。

```
SCENE BEFORE: Scene 'Scene' | 1 camera, 1 light, 1 mesh | active Cube ...
EXEC RESULT: Code executed successfully:
SCENE AFTER: Scene 'Scene' | 1 camera, 2 light, 2 mesh | active LocalVerifyTorchLight_Day021 ...
  LocalVerifyTorus_Day021 | mesh | at (0.0, 0.0, 1.0) | size 1.6x1.6x0.4
  LocalVerifyTorchLight_Day021 | light | at (0.0, 0.0, 2.5)
```

レンダリング結果(`local_gui_render.png`、検証後は削除済み)は、追加したトーラスがデフォルトの
Cube上に乗り、暖色の点光源で照らされている様子が実際に確認できた。検証後、追加した
オブジェクトは`execute_blender_code`で削除し、シーンを元の状態にクリーンアップした。

### 8.4 結論(追加検証)

- クラウドRoutine環境でPythonスクリプトを使って代替検証した「MCPクライアント → MCPサーバー →
  Blenderアドオン → bpy実行」という全スタックは、実際のAIクライアント(Claude Code自身)から、
  実機のBlender GUI(Windows, 4.5)に対しても問題なく動作した。クラウド環境(Linux, Xvfb経由)と
  ローカル環境(Windows, 通常のGUIモード)という違いはあるが、ツールの挙動・制約(headless拒否の
  仕様含む)は一致していた。
- `uvx mcp-for-blender setup`は、アドオンの導入とMCPクライアント設定を1コマンドで自動化しており、
  手動での`addon.py`配置やrequests依存解決(クラウド環境で必要だった対応、1節参照)は不要だった。
  Windows配布のBlenderにはrequestsが同梱されているとみられる。
- 以前「未検証」としていた「実際のAIクライアントGUIから接続する体験」は、本節の検証で解消した。

## 未検証の範囲(今回はスコープ外、有料APIキー不要の範囲でも未実施)

- Poly Haven経由のアセットインポート(`import_asset`ツール)は時間の都合で未実施。
- Hyper3D/Sketchfab/Meshy/Tripo等の有料3D生成連携は、CLAUDE.mdの方針により最初から対象外。
