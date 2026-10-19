# Day 021: mcp-for-blender を日本語指示でBlenderに繋ぐ

対象: https://github.com/ahujasid/mcp-for-blender (MIT License)

詳しい実行ログ・結果は `results.md` を参照。ここでは再現手順のみまとめる。

## 再現手順(Linux / GUIなしサーバー環境向け)

### 1. Blender と Xvfb を用意する

```bash
apt-get install -y blender xvfb
blender --background --version   # Blender 4.0.2 で確認
```

### 2. アドオンを配置して有効化する

```bash
mkdir -p ~/.config/blender/4.0/scripts/addons
cp mcp-for-blender/addon.py ~/.config/blender/4.0/scripts/addons/mcp_for_blender.py

# Blender配布パッケージにrequestsが無い場合は、addonのmodulesパスへ直接インストール
mkdir -p ~/.config/blender/4.0/scripts/addons/modules
python3.12 -m pip install --target ~/.config/blender/4.0/scripts/addons/modules requests

xvfb-run -a blender --background --python-expr "
import bpy
bpy.ops.preferences.addon_enable(module='mcp_for_blender')
bpy.ops.wm.save_userpref()
"
```

### 3. Blenderを(仮想ディスプレイ付きで)起動したままにする

**`blender --background`ではアドオンのソケットサーバーが起動しない**(ツール側の仕様、
`results.md`参照)。`xvfb-run -a blender`でGUIモードのまま起動する。

```bash
nohup xvfb-run -a blender > blender_gui.log 2>&1 &
sleep 8
cat blender_gui.log
# => BlenderMCP server started on localhost:9876
```

### 4. MCPサーバーを用意し、MCPクライアントから接続する

```bash
cd mcp-for-blender
uv sync
```

Python製の簡易MCPクライアント(`mcp`パッケージの`stdio_client`/`ClientSession`)で
`uv run mcp-for-blender`をstdio経由で起動し、`execute_blender_code`等のツールを呼ぶ。
実際に使ったクライアントスクリプトの要点:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(command="uv", args=["run", "mcp-for-blender"], cwd="mcp-for-blender")
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        result = await session.call_tool("execute_blender_code", {"code": "...", "user_prompt": "..."})
```

### 5. レンダリング画像を保存する

`execute_blender_code`に渡すコード内で`bpy.ops.render.render(write_still=True)`を呼べば、
MCP経由でBlenderのレンダリング画像をファイルとして保存できる(`before.png` / `after.png`)。

実際に使ったスクリプト:

- `mcp_client_scene_info.py` — ツール一覧取得・Before/Afterの`get_scene_info`確認
- `mcp_client_build_room.py` — 日本語指示に基づく部屋生成コードを`execute_blender_code`で実行
- `mcp_client_fix_camera_and_render.py` — カメラ位置を部屋全体が見える構図に調整して`after.png`を再レンダリング

## 前提条件・制約

- Claude Desktop等の実際のAIクライアントGUIはこの実行環境に無いため、MCPクライアントの役割は
  上記の自作Pythonスクリプトで代替した。実際のAIクライアントからの接続体験そのものは未検証。
- Poly Haven等のアセットインポート、Hyper3D/Sketchfab/Meshy/Tripo等の有料3D生成連携は未検証
  (後者はCLAUDE.mdの方針により対象外)。
