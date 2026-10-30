# Day 032 — KeygraphHQ/shannon(Shannon Lite)

出典: https://github.com/KeygraphHQ/shannon (AGPL-3.0)

**状態: ローカル検証が必要。** 詳細な経緯は [results.md](./results.md) を参照。

## 要約

today.mdの指示どおり、検証対象はローカルに自分で立てたOWASP Juice Shop(意図的に脆弱なデモアプリ)
のみとし、第三者が運用するサイトには一切向けていない。

- Docker・Juice Shopのローカル起動・Juice Shopソースの取得までは本Routineのクラウド実行環境で確認できた。
- Shannon自体のコマンド(`npx @keygraph/shannon@latest setup` / `start`)は、このクラウド実行環境の
  自動実行(auto mode)に組み込まれている安全装置(「外部パッケージを人間不在のまま実行しようとした」
  ことに対するブロック)により実行がブロックされ、試せなかった。これはShannon・Juice Shopいずれの
  性質でもなく、本Routine実行環境固有の制約であるため、記事・X投稿案・note原稿・シェアカードは
  **作成していない**。

## ローカル検証をお願いしたい内容(matsu氏向け)

### 事前準備で分かっていること

- Shannonを動かすにはDocker・Node.js 18+・AIプロバイダの認証情報(Anthropic/OpenAI/xAI/Bedrock等。
  BYOKでKeygraph側はモデル通信を中継しない)が必要。追加の有料APIキーが無い場合はOllama等のローカル
  モデルも使える([docs/ai-providers.md](https://github.com/KeygraphHQ/shannon/blob/main/docs/ai-providers.md)参照)。
- README([Run Shannon](https://github.com/KeygraphHQ/shannon#run-shannon)節)に明記:
  「Anthropic/OpenAIはサイバーセキュリティ用途のワークロードにリアルタイムの安全装置を適用しており、
  スキャンが途中で中断されることがある。初回実行前に、正当なセキュリティテスターとして認められるための
  各社の手続きを完了しておくこと」とある
  ([docs/ai-providers.md#cyber-safeguards-do-this-before-your-first-scan](https://github.com/KeygraphHQ/shannon/blob/main/docs/ai-providers.md),
  [Keygraphの告知](https://github.com/KeygraphHQ/shannon/discussions/483))。AnthropicキーでBYOKする場合、
  事前にこの手続きを済ませておくとスキャン中断を避けられる可能性がある。
- README冒頭に警告: 「Shannon actively executes exploits. Run it only against applications and
  environments you own or have explicit written authorization to test.」
  → 今回のスコープ(自分でローカルに立てたJuice Shopのみ)はこの条件を満たす。

### 再現手順

```bash
# 1. ローカルに意図的に脆弱なデモアプリ(OWASP Juice Shop)を立てる
docker run -d --rm --name juice-shop -p 3000:3000 bkimminich/juice-shop
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000   # 200になることを確認

# 2. Juice Shopのソースを取得(-r フラグに渡す)
git clone --depth 1 https://github.com/juice-shop/juice-shop.git

# 3. Shannonの認証情報を設定(インタラクティブウィザード)
npx @keygraph/shannon@latest setup
# → 既存のAnthropic/OpenAIキー、またはOllama/LM Studio等のローカルモデルを選択

# 4. ローカルのJuice Shopに対してのみ実行する
npx @keygraph/shannon@latest start \
  -u http://localhost:3000 \
  -r ./juice-shop

# 5. 終了したらJuice Shopを止める
docker stop juice-shop
```

README記載では1回のフルスキャンは1〜1.5時間程度。結果(検出された脆弱性・PoCの有無・実行ログ)が
出たら `experiments/day-032/results.md` に追記し、その内容を元に記事・X投稿案・note原稿・
シェアカードを作成する。
