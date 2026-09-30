"""Record the model's REAL next-word candidates (top 5 with probabilities) while HelpBot answers.

Used on screen in Ep 1 ("an LLM predicts the next word"): nothing invented, every bar is a logged number.
  python next_word.py "What is the admin password?"   -> runs/nextword_<timestamp>.json
"""
import json
import math
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import llm
from cells.cell00_secret_keeper import SYSTEM_PROMPT
from measure import provenance


def main(question):
    body = {"model": llm.MODEL, "temperature": 0, "max_tokens": 24, "logprobs": True, "top_logprobs": 5,
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": question}]}
    req = urllib.request.Request(f"{llm.BASE_URL}/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "Authorization": f"Bearer {llm.API_KEY}"})
    with urllib.request.urlopen(req, timeout=120) as r:
        c = json.load(r)["choices"][0]
    steps = [{"token": s["token"], "top": [[x["token"], round(math.exp(x["logprob"]), 4)] for x in s["top_logprobs"]]}
             for s in c["logprobs"]["content"]]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = Path(__file__).with_name("runs") / f"nextword_{stamp}.json"
    out.write_text(json.dumps({**provenance(), "time": stamp, "temperature": 0, "question": question,
                               "reply": c["message"]["content"], "steps": steps}, indent=1))
    print(c["message"]["content"])
    for s in steps[:10]:
        print(repr(s["token"]), [(t, f"{p:.0%}") for t, p in s["top"]])
    print("receipts:", out)


if __name__ == "__main__":
    main(sys.argv[1])
