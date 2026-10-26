"""
Day 028 追加検証(ローカルGPU): 論文が実際に使う構成に近い「密検索(埋め込みモデル)+
クロスエンコーダ再ランキング」でRawRAGを実装し直す。

元のRawRAGMemory(TF-IDFのみ)がresults.mdで「クロスエンコーダ再ランキングを実装して
いないことが、Raw-RAGの正答率が低かった一因」と考察していたため、その仮説を実際に
検証する。埋め込みモデル・クロスエンコーダともに公開の無料モデル(APIキー不要)で、
ローカルGPUで実行する。
"""
import time

import torch
from sentence_transformers import SentenceTransformer, CrossEncoder, util

EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
RERANK_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

_device = "cuda" if torch.cuda.is_available() else "cpu"
_embedder = None
_reranker = None


def _get_models():
    global _embedder, _reranker
    if _embedder is None:
        _embedder = SentenceTransformer(EMBED_MODEL_NAME, device=_device)
    if _reranker is None:
        _reranker = CrossEncoder(RERANK_MODEL_NAME, device=_device)
    return _embedder, _reranker


class DenseRAGMemory:
    """生ログをそのまま保持し、質問時に埋め込みモデルで候補を絞り込んでから
    クロスエンコーダで再ランキングする(論文の密検索+再ランキング構成に近い)。"""

    def __init__(self, turns, top_k=5, candidate_k=10, use_reranker=True, include_speaker=True):
        embedder, reranker = _get_models()
        self.embedder = embedder
        self.reranker = reranker if use_reranker else None
        self.turns = turns
        self.top_k = top_k
        self.candidate_k = candidate_k

        t0 = time.perf_counter()
        self.doc_texts = [
            f"{speaker}: {text}" if include_speaker else text
            for (_, speaker, text) in turns
        ]
        self.storage_chars = sum(len(text) for (_, _, text) in turns)
        self.doc_embeddings = self.embedder.encode(
            self.doc_texts, convert_to_tensor=True, show_progress_bar=False,
            device=_device,
        )
        self.build_time = time.perf_counter() - t0

    def retrieve(self, query_text):
        t0 = time.perf_counter()
        q_emb = self.embedder.encode(
            query_text, convert_to_tensor=True, show_progress_bar=False, device=_device,
        )
        sims = util.cos_sim(q_emb, self.doc_embeddings)[0]
        cand_k = min(self.candidate_k, len(self.turns))
        cand_idx = torch.topk(sims, k=cand_k).indices.tolist()

        if self.reranker is not None:
            pairs = [(query_text, self.doc_texts[i]) for i in cand_idx]
            rerank_scores = self.reranker.predict(pairs)
            order = sorted(range(len(cand_idx)), key=lambda j: rerank_scores[j], reverse=True)
            final_idx = [cand_idx[j] for j in order[: self.top_k]]
        else:
            final_idx = cand_idx[: self.top_k]

        top = [self.turns[i] for i in final_idx]
        query_time = time.perf_counter() - t0
        return top, query_time

    def answer(self, category, question_type, query_text):
        top, query_time = self.retrieve(query_text)
        combined_text = " ".join(text for (_, _, text) in top)
        return combined_text, query_time, top
