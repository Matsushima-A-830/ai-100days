import torch


def bag(w, stems, weights, n_concepts):
    """(rows, L) concept ids and weights -> (rows, C) max weight of each concept"""
    out = torch.zeros(stems.shape[0], n_concepts)
    out = out.scatter_reduce(1, stems, weights, reduce="amax", include_self=True)
    return out * w["keep"]


def phrases(w, ids):
    """(rows, L) word-concept ids (0 = skipped) -> (rows, L-1) phrase-concept ids of adjacent content words
    (0 where the pair is not a known phrase), and the position of the second word of each pair"""
    L = ids.shape[1]
    key = torch.arange(L).unsqueeze(0) + L * (ids == 0).long()
    order = torch.argsort(key, dim=1)
    c = torch.gather(ids, 1, order)
    a, b = c[:, :-1], c[:, 1:]
    k = a * w["n_words"] + b
    idx = torch.searchsorted(w["phrase_keys"], k)
    idx = idx.clamp(max=w["phrase_keys"].shape[0] - 1)
    hit = ((w["phrase_keys"][idx] == k) & (a > 0) & (b > 0) & (a != b)).long()
    return (w["phrase_base"] + idx) * hit, order[:, 1:]


def forward(w, q, o):
    hp = w["hp"]
    n = q.shape[0]
    C = w["idf"].shape[0]
    idf = w["idf"]
    sent = torch.sparse_coo_tensor(w["sent_idx"], w["sent_val"], (w["sent_neg"].shape[0], C))
    assoc = torch.sparse_coo_tensor(w["assoc_idx"], w["assoc_val"], (C, C))

    # ---- question concepts, the last words of the question weigh more (that is where the actual ask is)
    qs = w["stem_of"][q]
    valid = (q > 0).float()
    length = valid.sum(1, keepdim=True)
    pos = torch.arange(q.shape[1]).float().unsqueeze(0)
    dist = (length - 1.0 - pos).clamp(min=0.0)
    pw = (1.0 + hp[0] * torch.exp(-dist / hp[1])) * (qs > 0).float()
    qph, qorder = phrases(w, qs)
    qpw = torch.gather(pw, 1, qorder) * (qph > 0).float()
    qpos = bag(w, torch.cat([qs, qph], 1), torch.cat([pw, qpw], 1), C)
    qpresent = (qpos > 0).float()
    qw = qpos * idf
    qnorm = qw.sum(1, keepdim=True).clamp(min=1e-6)

    # ---- option concepts that are not already in the question
    os_ = w["stem_of"][o].reshape(n * 4, o.shape[2])
    oph, _ = phrases(w, os_)
    oall = torch.cat([os_, oph], 1)
    ob = bag(w, oall, (oall > 0).float(), C)
    ob = ob * (1.0 - hp[10] * qpresent.repeat_interleave(4, dim=0))
    ow = ob * idf
    onorm = ow.sum(1, keepdim=True).clamp(min=1e-6) ** hp[8]

    # ---- negative questions (EXCEPT, NOT, LEAST): prefer the option the knowledge supports least
    neg1 = w["neg_word"][q].sum(1)
    # "not" counts when it closely follows "which"/"what" ("Which of these is NOT ...")
    neg2 = torch.zeros(n)
    for k in range(1, 7):
        neg2 = neg2 + (w["which_word"][q[:, :-k]] * w["not_word"][q[:, k:]]).sum(1)
    # "least likely", "not true", "not an example" ...
    neg3 = (w["least_word"][q[:, :-1]] * w["likely_word"][q[:, 1:]]).sum(1)
    neg = (neg1 + neg2 + neg3).clamp(max=1.0).unsqueeze(1)
    sign = 1.0 - 2.0 * hp[5] * neg

    # ---- retrieval: best knowledge-base sentence that covers both question and option
    hq = torch.sparse.mm(sent, (qw / qnorm).t())            # (N, n)
    ho = torch.sparse.mm(sent, (ow / onorm).t())            # (N, 4n)
    joint = ho.reshape(-1, n, 4) * (hq ** hp[9]).unsqueeze(2)    # (N, n, 4)
    # polarity: an option that says "not"/"no" is supported by negated sentences, a plain option by plain ones
    oneg = (w["neg_option_word"][o].sum(2) > 0).float()           # (n, 4)
    # a question that itself says "no"/"not" (and is not a NOT-question) makes the whole statement negative
    qneg = (w["neg_option_word"][q].sum(1, keepdim=True) > 0).float() * (1.0 - neg)   # (n, 1)
    oneg = oneg + qneg - 2.0 * oneg * qneg                        # exclusive or
    sneg = w["sent_neg"].reshape(-1, 1, 1)                        # (N, 1, 1)
    same = sneg * oneg.unsqueeze(0) + (1.0 - sneg) * (1.0 - oneg.unsqueeze(0))
    joint = joint * (same + hp[7] * (1.0 - same))
    top = torch.topk(joint, 5, dim=0).values                     # (5, n, 4)
    decay = hp[6] ** torch.arange(5).float()                     # weight of the k-th best sentence
    ir = (top * decay.reshape(5, 1, 1)).sum(0)

    # ---- association: question concepts x option concepts, PPMI from sentence co-occurrence
    pq = torch.sparse.mm(assoc, (qw / qnorm).t())           # (C, n)
    pq = pq.t().repeat_interleave(4, dim=0)                      # (4n, C)
    assoc = ((ow / ow.sum(1, keepdim=True).clamp(min=1e-6)) * pq).sum(1).reshape(n, 4)


    olen = (o > 0).float().sum(2)
    return sign * (hp[2] * ir + hp[3] * assoc) + hp[4] * olen
