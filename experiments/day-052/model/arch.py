import torch
import torch.nn.functional as nnf

TOPK = 8
SCALE = 6.0


def forward(w, q, o):
    idf = w["idf"]
    facts = w["facts"]
    bias = w["bias"]
    v = idf.shape[0]
    n = q.shape[0]
    q_bow = nnf.one_hot(q, v).sum(dim=1).float() * idf
    logits = torch.zeros(n, 4)
    for k in range(4):
        o_bow = nnf.one_hot(o[:, k, :], v).sum(dim=1).float() * idf
        cand = q_bow + o_bow
        cand = cand / (cand.norm(dim=1, keepdim=True) + 1e-6)
        sims = cand.matmul(facts.t())
        top_vals, top_idx = sims.topk(TOPK, dim=1)
        weights = torch.softmax(top_vals * SCALE, dim=1)
        score = (weights * top_vals).sum(dim=1) * SCALE
        logits[:, k] = score + bias[0]
    return logits
