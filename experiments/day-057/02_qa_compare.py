"""Compare QueryLM (search-native) vs Standard (no-search) 360M baselines on the same
knowledge-QA questions, under three conditions:
  (A) QueryLM, search disabled (bad_words_ids blocks <WEB_QUERY>) -- same information as Standard.
  (B) QueryLM, search enabled -- the model writes its own query, then is handed a short reference
      passage (written by the author, Wikipedia-sourced facts, one per question -- the same
      "fixed-string retriever" approach the model card itself demonstrates, since this script
      intentionally never calls a live retrieval API), and continues from there.
  (C) Standard baseline, no search (it never saw the search tokens in training).
All runs use greedy decoding (do_sample=False) for reproducibility.
"""
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

QUERYLM_REPO = "models/querylm-wiki-360m"
STANDARD_REPO = "models/standard-wiki-360m"

QUESTIONS = [
    "Who wrote the novel Pride and Prejudice?",
    "What is the chemical symbol for gold?",
    "What is the capital of Australia?",
    "What is the capital of Mongolia?",
    "Who painted the Mona Lisa?",
    "In which year did the Berlin Wall fall?",
    "What is the tallest mountain in the world?",
    "Who was the first person to walk on the Moon?",
]

FEWSHOT = (
    "Question: Who wrote the novel Pride and Prejudice?\nAnswer: Jane Austen\n\n"
    "Question: What is the chemical symbol for gold?\nAnswer: Au\n\n"
)

FEWSHOT_SEARCH = (
    "Question: Who wrote the novel Pride and Prejudice?\n"
    "<WEB_QUERY>Pride and Prejudice author</WEB_QUERY> "
    "<WEB_RESPONSE>Pride and Prejudice is an 1813 novel of manners written by Jane Austen.</WEB_RESPONSE>\n"
    "Answer: Jane Austen\n\n"
    "Question: What is the chemical symbol for gold?\n"
    "<WEB_QUERY>gold chemical symbol</WEB_QUERY> "
    "<WEB_RESPONSE>Gold is a chemical element with the symbol Au and atomic number 79.</WEB_RESPONSE>\n"
    "Answer: Au\n\n"
)


# Fixed reference passages, one per question (author-written, Wikipedia-sourced facts).
# Keyed by question text; used as the <WEB_RESPONSE> payload instead of a live retrieval call.
REFERENCE_PASSAGES = {
    "Who wrote the novel Pride and Prejudice?":
        "Pride and Prejudice is an 1813 novel of manners written by Jane Austen.",
    "What is the chemical symbol for gold?":
        "Gold is a chemical element with the symbol Au and atomic number 79.",
    "What is the capital of Australia?":
        "Canberra is the capital city of Australia. It was founded in 1913 and is the country's largest inland city.",
    "What is the capital of Mongolia?":
        "Ulaanbaatar is the capital and largest city of Mongolia.",
    "Who painted the Mona Lisa?":
        "The Mona Lisa is a half-length portrait painting by the Italian artist Leonardo da Vinci.",
    "In which year did the Berlin Wall fall?":
        "The Berlin Wall fell on 9 November 1989, when East Germany announced that its citizens could cross the border freely.",
    "What is the tallest mountain in the world?":
        "Mount Everest, known in Nepali as Sagarmatha, is Earth's highest mountain above sea level, located in the Himalayas.",
    "Who was the first person to walk on the Moon?":
        "Neil Armstrong was an American astronaut who became the first person to walk on the Moon, on July 20, 1969, during the Apollo 11 mission.",
}


def reference_passage(question: str) -> str:
    return REFERENCE_PASSAGES.get(question, "No reference passage available for this question.")


def main():
    print("Loading QueryLM...")
    tok_q = AutoTokenizer.from_pretrained(QUERYLM_REPO)
    model_q = AutoModelForCausalLM.from_pretrained(QUERYLM_REPO, dtype=torch.bfloat16).eval()
    Q_OPEN = tok_q.convert_tokens_to_ids("<WEB_QUERY>")
    Q_CLOSE = tok_q.convert_tokens_to_ids("</WEB_QUERY>")

    print("Loading Standard...")
    tok_s = AutoTokenizer.from_pretrained(STANDARD_REPO)
    model_s = AutoModelForCausalLM.from_pretrained(STANDARD_REPO, dtype=torch.bfloat16).eval()

    @torch.no_grad()
    def gen(model, tok, text, max_new_tokens, stop_id=None, block_ids=None):
        x = tok(text, add_special_tokens=False, return_tensors="pt")
        kw = {} if not block_ids else {"bad_words_ids": [[i] for i in block_ids]}
        out = model.generate(**x, max_new_tokens=max_new_tokens, do_sample=False,
                              eos_token_id=stop_id, pad_token_id=tok.eos_token_id, **kw)
        return tok.decode(out[0, x.input_ids.shape[1]:], skip_special_tokens=True)

    results = []
    for q in QUESTIONS:
        row = {"question": q}

        # (A) QueryLM, search disabled
        prompt_a = FEWSHOT + f"Question: {q}\nAnswer:"
        ans_a = gen(model_q, tok_q, prompt_a, 16, block_ids=[Q_OPEN])
        row["querylm_no_search"] = ans_a.split("\n")[0].strip()

        # (B) QueryLM, search enabled (model writes query, real Wikipedia lookup, model continues)
        prompt_b = FEWSHOT_SEARCH + f"Question: {q}\n"
        query = gen(model_q, tok_q, prompt_b + "<WEB_QUERY>", 24, stop_id=Q_CLOSE).strip()
        passage = reference_passage(q)
        block = f"<WEB_QUERY>{query}</WEB_QUERY> <WEB_RESPONSE>{passage}</WEB_RESPONSE>"
        ans_b = gen(model_q, tok_q, prompt_b + block + "\nAnswer:", 16, block_ids=[Q_OPEN])
        row["querylm_query"] = query
        row["querylm_retrieved"] = passage
        row["querylm_with_search"] = ans_b.split("\n")[0].strip()

        # (C) Standard baseline, no search
        prompt_c = FEWSHOT + f"Question: {q}\nAnswer:"
        ans_c = gen(model_s, tok_s, prompt_c, 16)
        row["standard"] = ans_c.split("\n")[0].strip()

        results.append(row)
        print(json.dumps(row, ensure_ascii=False, indent=2))

    with open("qa_results.json", "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
