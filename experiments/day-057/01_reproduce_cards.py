"""Reproduce the exact usage snippets from the QueryLM / Standard model cards, verbatim, to confirm they run as documented."""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

print("=== QueryLM (search-native) ===")
repo = "models/querylm-wiki-360m"
tok = AutoTokenizer.from_pretrained(repo)
model = AutoModelForCausalLM.from_pretrained(repo, torch_dtype=torch.bfloat16).eval()

Q_OPEN, Q_CLOSE = tok.convert_tokens_to_ids("<WEB_QUERY>"), tok.convert_tokens_to_ids("</WEB_QUERY>")
print("WEB_QUERY ids:", Q_OPEN, Q_CLOSE)

def my_search(query: str) -> str:
    return "Canberra is the capital city of Australia. It was founded in 1913 and is the country's largest inland city."

@torch.no_grad()
def generate(text, max_new_tokens, stop_id=None, allow_search=True):
    x = tok(text, add_special_tokens=False, return_tensors="pt")
    kw = {} if allow_search else {"bad_words_ids": [[Q_OPEN]]}
    out = model.generate(**x, max_new_tokens=max_new_tokens, do_sample=False,
                         eos_token_id=stop_id, pad_token_id=tok.eos_token_id, **kw)
    return tok.decode(out[0, x.input_ids.shape[1]:], skip_special_tokens=True)

def shot(q, query, passage, a):
    return f"Question: {q}\n<WEB_QUERY>{query}</WEB_QUERY> <WEB_RESPONSE>{passage}</WEB_RESPONSE>\nAnswer: {a}\n\n"

shots = (shot("Who wrote the novel Pride and Prejudice?", "Pride and Prejudice author",
              "Pride and Prejudice is an 1813 novel of manners written by Jane Austen.", "Jane Austen")
         + shot("What is the chemical symbol for gold?", "gold chemical symbol",
                "Gold is a chemical element with the symbol Au and atomic number 79.", "Au"))
prompt = shots + "Question: What is the capital of Australia?\n"

query = generate(prompt + "<WEB_QUERY>", max_new_tokens=24, stop_id=Q_CLOSE).strip()
block = f"<WEB_QUERY>{query}</WEB_QUERY> <WEB_RESPONSE>{my_search(query)}</WEB_RESPONSE>"
answer = generate(prompt + block + "\nAnswer:", max_new_tokens=16, allow_search=False)
print("query :", query)
print("answer:", answer.split("\n")[0].strip())

print()
print("=== Standard (no-search baseline) ===")
repo2 = "models/standard-wiki-360m"
tok2 = AutoTokenizer.from_pretrained(repo2)
model2 = AutoModelForCausalLM.from_pretrained(repo2, torch_dtype=torch.bfloat16).eval()

prompt2 = ("Question: Who wrote the novel Pride and Prejudice?\nAnswer: Jane Austen\n\n"
          "Question: What is the chemical symbol for gold?\nAnswer: Au\n\n"
          "Question: What is the capital of Australia?\nAnswer:")
x2 = tok2(prompt2, add_special_tokens=False, return_tensors="pt")
with torch.no_grad():
    out2 = model2.generate(**x2, max_new_tokens=16, do_sample=False, pad_token_id=tok2.eos_token_id)
print("answer:", tok2.decode(out2[0, x2.input_ids.shape[1]:], skip_special_tokens=True).split("\n")[0].strip())
