"""
素朴な「naive RAG」役の検索スクリプト。

日本語の会話ログに対してMeCab等の形態素解析器を使わず、文字bigram(2文字ずつの
スライディングウィンドウ)をトークン代わりにしたTF-IDFで類似度を計算する、素朴な
キーワード検索(論文中の "IDF-keyword" ベースラインに近い簡易実装)。

外部ライブラリは使わず標準ライブラリのみで実装している。密検索(埋め込みベクトル)や
クロスエンコーダ再ランキングは実装していない — これは意図的な簡略化であり、
results.mdの「限界」節に明記する。
"""
import math
import re
import sys
from pathlib import Path

TURN_RE = re.compile(r"^\[(\d+-\d+)\]\s*([^:]+):\s*(.+)$")


def parse_transcript(path: Path):
    turns = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = TURN_RE.match(line.strip())
        if m:
            turn_id, speaker, text = m.groups()
            turns.append({"id": turn_id, "speaker": speaker.strip(), "text": text.strip()})
    return turns


def bigrams(text: str):
    # 句読点・記号は落とし、文字bigramのみを特徴として使う
    cleaned = re.sub(r"[\s、。「」『』・()（）\[\]\-]", "", text)
    if len(cleaned) < 2:
        return [cleaned] if cleaned else []
    return [cleaned[i:i + 2] for i in range(len(cleaned) - 1)]


def build_idf(turns):
    df = {}
    for t in turns:
        seen = set(bigrams(t["text"]))
        for bg in seen:
            df[bg] = df.get(bg, 0) + 1
    n = len(turns)
    return {bg: math.log((n + 1) / (c + 1)) + 1.0 for bg, c in df.items()}


def score(text, turn_text, idf):
    q_bgs = bigrams(text)
    d_bgs = bigrams(turn_text)
    d_counts = {}
    for bg in d_bgs:
        d_counts[bg] = d_counts.get(bg, 0) + 1
    s = 0.0
    for bg in q_bgs:
        if bg in d_counts:
            s += d_counts[bg] * idf.get(bg, 0.0)
    return s


def retrieve(question: str, transcript_path: Path, top_k: int = 5):
    turns = parse_transcript(transcript_path)
    idf = build_idf(turns)
    scored = [(score(question, t["text"], idf), t) for t in turns]
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:top_k]


if __name__ == "__main__":
    base = Path(__file__).parent
    cases = [
        ("project_nova", "PN1", "最終的な技術スタックは何か?"),
        ("project_nova", "PN2", "最終的なチーム人数は何人か?"),
        ("project_nova", "PN3", "Kestrel Roboticsとのデモはいつ・どこで行われる予定か?"),
        ("project_nova", "PN4", "技術スタックは最初(セッション1)何だったか?"),
        ("project_nova", "PN5", "ステージング環境はAWSに移行する前は何を使っていたか?"),
        ("project_nova", "PN6", "最終的に確定した締め切りの日付はいつか?"),
        ("project_nova", "PN7", "予算はセッション1からセッション2、セッション3でどのように変化したか、3つの値を順番に答えよ"),
        ("project_nova", "PN8", "セッション2で新たにチームに加わったが、最終的なチームには残っていない人物は誰か?"),
        ("trip_planning", "TP1", "最終的なホテルはどこか?"),
        ("trip_planning", "TP2", "最終的な人数は何人か?"),
        ("trip_planning", "TP3", "最終的な行き先(都市/国)はどこか?"),
        ("trip_planning", "TP4", "最初に計画していた行き先はどこだったか?"),
        ("trip_planning", "TP5", "最初に候補として挙がっていたホテルはどこだったか?"),
        ("trip_planning", "TP6", "予算はセッション1からセッション2、セッション3でどのように変化したか、3つの値を順番に答えよ"),
        ("trip_planning", "TP7", "記念日のディナーのレストランに伝えるべき食事の注意事項は何か?"),
        ("trip_planning", "TP8", "レンタカーの確認番号は何か?"),
    ]
    for conv, qid, question in cases:
        path = base / "transcripts" / f"{conv}.md"
        results = retrieve(question, path, top_k=5)
        print(f"=== {qid} ({conv}) ===")
        print(f"Q: {question}")
        for rank, (s, t) in enumerate(results, 1):
            print(f"  [{rank}] score={s:.2f} turn={t['id']} {t['speaker']}: {t['text']}")
        print()
