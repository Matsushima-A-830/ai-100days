# Day 029 結果

Routine環境の制約により未検証、ローカル検証待ち(詳細は `README.md` 参照。
`agent-reach` 本体のインストールが本セッションのサンドボックスに3つの方法すべてで拒否され、
一度も実行できなかった)。

## 唯一実際に実行して確認できたこと: PyPIの `agent-reach` は別物

```bash
$ python3 -m venv venv && source venv/bin/activate
$ pip install --quiet agent-reach
$ pip show agent-reach
Name: agent-reach
Version: 0.1.0
Summary: Give an agent the channels it needs, and only those. Install per channel,
         one output shape, with caching and a token budget.
Home-page:
Author: Jean Galea
Author-email:
License:
Location: /home/user/ai-100days/experiments/day-029/venv/lib/python3.11/site-packages
Requires: feedparser
Required-by:
```

`Panniantong/Agent-Reach` の `pyproject.toml` では `authors = [{name = "Neo Reid"}]`、
`description = "Internet access for AI agents: one CLI..."` となっており、著者名・説明文とも
完全に異なる。プロジェクト自身の `docs/install.md` が「PyPIのagent-reachはこのプロジェクトでは
ない、GitHubのURLから入れろ」と警告している通りだった(今回それが本当かを実機で確認した)。
その後 `pip uninstall -y agent-reach feedparser` で後始末済み。
