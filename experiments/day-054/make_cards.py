from importlib import resources
import json
from haru.prompt import card_templates, render_card

templates = card_templates()
TEMPLATES = templates["templates"]
for code in ["en", "ja"]:
    path = resources.files("haru") / "assets" / "cards" / f"{code}.json"
    card = json.loads(path.read_text(encoding="utf-8")).get("chat", {})
    prompt = render_card(card, TEMPLATES[code])
    with open(f"card_{code}.txt", "w", encoding="utf-8") as f:
        f.write(prompt)
