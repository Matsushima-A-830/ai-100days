"""Quick look at the chat-tuned querylm-wiki-360m-sft-search on the same 8 questions,
using the same fixed reference passages as 02_qa_compare.py (not a live retrieval call)."""
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

REPO = "models/querylm-wiki-360m-sft-search"

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


def main():
    tok = AutoTokenizer.from_pretrained(REPO)
    model = AutoModelForCausalLM.from_pretrained(REPO, dtype=torch.bfloat16).eval()
    Q_OPEN = tok.convert_tokens_to_ids("<WEB_QUERY>")
    Q_CLOSE = tok.convert_tokens_to_ids("</WEB_QUERY>")

    @torch.no_grad()
    def gen(text, max_new_tokens, stop_id=None, block_ids=None):
        x = tok(text, add_special_tokens=False, return_tensors="pt")
        kw = {} if not block_ids else {"bad_words_ids": [[i] for i in block_ids]}
        out = model.generate(**x, max_new_tokens=max_new_tokens, do_sample=False,
                              eos_token_id=stop_id, pad_token_id=tok.eos_token_id, **kw)
        return tok.decode(out[0, x.input_ids.shape[1]:], skip_special_tokens=True)

    results = []
    for q in REFERENCE_PASSAGES:
        prompt = f"User: {q}\n\nAssistant: "
        query = gen(prompt + "<WEB_QUERY>", 24, stop_id=Q_CLOSE).strip()
        passage = REFERENCE_PASSAGES[q]
        block = f"<WEB_QUERY>{query}</WEB_QUERY> <WEB_RESPONSE>{passage}</WEB_RESPONSE>"
        answer = gen(prompt + block, 64, block_ids=[Q_OPEN])
        answer = answer.split("\n\nUser:")[0].strip()
        row = {"question": q, "query": query, "answer": answer}
        results.append(row)
        print(json.dumps(row, ensure_ascii=False, indent=2))

    with open("sft_results.json", "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
