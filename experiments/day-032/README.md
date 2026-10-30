# Day 032 — KeygraphHQ/shannon(Shannon Lite)

出典: https://github.com/KeygraphHQ/shannon (AGPL-3.0)

**状態: ローカル検証実施済み(2026-10-30)。詳細は [results.md](./results.md) を参照。**
reconフェーズの再現性あるバグにより、実際の脆弱性スキャン結果までは到達できなかったが、
その過程で得られたツールの挙動(ドキュメント不備・Docker構成依存のバグ・ローカルモデルでの
破綻パターン)を検証結果として記録した。

## 要約

today.mdの指示どおり、検証対象はローカルに自分で立てたOWASP Juice Shop(意図的に脆弱なデモアプリ)
のみとし、第三者が運用するサイトには一切向けていない。

- Routineのクラウド実行環境: Docker・Juice Shopのローカル起動・Juice Shopソースの取得までは確認できたが、
  Shannon自体のコマンドはクラウド実行環境の自動実行(auto mode)に組み込まれている安全装置
  (「外部パッケージを人間不在のまま実行しようとした」ことに対するブロック)により実行がブロックされ、
  試せなかった。これはRoutine実行環境固有の制約であり、ローカル検証にエスカレーションした。
- ローカル検証(人間のWindows + WSL2環境): Docker Desktopへの切り替え、READMEの誤り修正(後述)を経て
  Shannonの起動自体には成功し、pre-reconフェーズは完全に成功したが、reconフェーズで再現性のある
  バグに遭遇し、実際の脆弱性スキャン・エクスプロイトまでは到達できなかった。無料のOllama
  (ローカルモデル)への切替も試したが、小型モデルでは構造化出力が破綻することを確認した。
  詳細は [results.md](./results.md) の「3. ローカル検証」を参照。

## ローカル検証の記録(matsu氏による実施)

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
# 注意: localhost ではなく host.docker.internal を使うこと。
# Shannon自体がDockerコンテナ内で動くため、localhost はコンテナ自身を指してしまい
# InvalidTargetError になる(README初版はこれで一度失敗した。results.md 3-2(a)参照)。
npx @keygraph/shannon@latest start \
  -u http://host.docker.internal:3000 \
  -r ./juice-shop

# 5. 終了したらJuice Shopを止める
docker stop juice-shop
```

README記載では1回のフルスキャンは1〜1.5時間程度。

**重要な注意点(results.mdに詳細記録)**:
- WSL2環境でDockerをsnapパッケージ版のまま使うと、Shannon起動時にread-onlyマウントエラーで
  失敗する可能性がある。Docker Desktop(WSL2バックエンド)への切り替えで解消した。
- reconフェーズの終盤で`AGENT_EXECUTION_FAILED`になる再現性のあるバグに遭遇した。
  `-w <workspace名>`で同じworkspace名を指定すればresumeでき、完了済みフェーズ
  (pre-recon等)の再実行・再課金は避けられる。
- Ollama等の無料ローカルモデルに切り替える場合、`host.docker.internal`がWSL2側と
  Windowsネイティブ側のどちらのOllamaを指すか(Docker Desktopの構成による)を事前に
  確認すること。また小型モデル(7B程度)では脆弱性検証エージェントの構造化出力が
  破綻し、スキャンが完走しない可能性が高い。

結果(検出された脆弱性・PoCの有無・実行ログ)はすべて `experiments/day-032/results.md` に
記録した。
