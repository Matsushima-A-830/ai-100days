# 今日のネタ

人間が通勤中などにここを書き換えてコミットする。実装Routineはこのファイルを読んで作業する。

- Day: 021
- 選んだ候補(backlog.mdのタイトルかURL): ahujasid/mcp-for-blender — https://github.com/ahujasid/mcp-for-blender
- 補足メモ(あれば):
  - 人間(matsu)から直接指定された候補(research: 2026-10-18分のネタ候補PR内の候補の1つ)。
  - 出典: https://github.com/ahujasid/mcp-for-blender (本日GitHub Trending Python/全言語で+2,098star/日。旧称blender-mcp)。MITライセンス、Blender Foundation非公式のコミュニティプラグイン。
  - 概要: Blenderアドオン(ソケットサーバー)とMCPサーバーの2部構成で、Claude Code/Claude Desktop等のAIクライアントからBlender Python APIを直接実行させ、シーン検査・レンダリング・Poly Haven/Sketchfab/Poly Pizzaからのアセット取り込み、Tripo/Hyper3D Rodin/Hunyuan3D/Meshy経由の3Dモデル生成までを自然言語で行える。
  - 検証範囲: Blender 3.0+・Python 3.10+・uvを導入してmcp-for-blenderアドオンとMCPサーバーをセットアップし、Claude Code自身をMCPクライアントとして接続する。日本語の指示(例:「低ポリゴンのダンジョンシーンを作って」)でBlenderシーンを生成させ、生成前後のスクリーンショットをBefore/Afterで記録する。アセット取得はPoly Haven等キー不要のものに限定し、Sketchfab/Hyper3D/Meshy等の有料連携は使わない。
  - 追加の有料APIキーは不要(Poly Havenはキー不要。有料の3D生成連携は使わない)。GPUは任意(Blenderのレンダリング品質には影響するが必須ではない)。`execute_blender_code`は任意のPythonを実行するため、検証前にBlenderファイルを保存すること。
  - 日本語記事件数: Zenn 2件以上(前身の「blender-mcp」名義でのハンズオン記事・アーキテクチャ解説記事) / Qiita 0件 / note 0件(2026-10-18時点、backlog.md参照)。前身名義での記事があるため完全新規ではなく、mcp-for-blenderへの改称後に強化されたアセット生成系連携(Tripo等)への言及や、独自の3Dシーン生成デモを中心に据えて差別化すること。
  - 記事化の切り口: 「日本語の指示だけでBlenderに3Dシーンを作らせてみた」というBefore/After比較を軸に、生成過程で実行されたBlender Pythonコードと結果画像をセットで見せる。

状態: 設定済み
