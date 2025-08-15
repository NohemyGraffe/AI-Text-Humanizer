# app.py
# pip install fastapi uvicorn openai==1.* regex python-dotenv
import os, re, json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # lock this down to your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------- STYLE RULES ----------
BUZZWORDS = [
    r"\bsynergy\b", r"\bleverage\b", r"\bparadigm\b", r"\bcutting-edge\b",
    r"\bholistic\b", r"\bseamless\b", r"\bactionable insights?\b",
    r"\brobust\b", r"\boptimi[sz]e\b", r"\bscalable\b", r"\bunlock value\b",
    r"\bmission[- ]critical\b", r"\bgame[- ]changer\b", r"\bnorth star\b"
]
PATTERNS = [
    (re.compile(r"[—–]"), "Em-dash found"),
    (re.compile(r"\bHonestly\b|\bhonestly\b|\bbut honestly\b"), "Uses 'honestly'"),
    (re.compile(r"\bIt'?s not just[^.?!]+, it'?s[^.?!]+", re.I), "Template: It's not just..., it's..."),
    (re.compile(r"\bNot only[^.?!]+,? but also[^.?!]+", re.I), "Template: Not only..., but also..."),
    (re.compile(r"\?\s*$", re.M), "Ends with a question (likely rhetorical)"),
    (re.compile(r"(?:^|\s)-\s*because", re.I), "Dash '— because' style"),
]
ADJ_TRIPLE = re.compile(
    r"\b(\w{3,})\b(?:\s*,\s*|\s+)(\w{3,})\b(?:\s*,\s*|\s+)(\w{3,})\b", re.I
)

SYSTEM_GUIDE = """You rewrite text to sound like a concise human.
Hard DO NOTs:
- No rhetorical questions. Never end with a question unless the original explicitly asks one you must keep.
- No em-dashes. Use commas or periods instead.
- Avoid templates: "It’s not just __, it’s __" and "Not only __, but also __".
- No “Honestly” or “but honestly”.
- No dramatic “— because” constructions.
- Avoid buzzwords (corporate-speak). Prefer plain words.
- Prefer 1 clear paragraph. Split only if meaning suffers.
- Prefer 1 precise adjective instead of strings of 3.
Preserve meaning; don’t add claims. Keep tone natural and direct.
Output ONLY the rewritten text.
"""

def lint(text: str):
    issues = []
    for rx, msg in PATTERNS:
        if rx.search(text):
            issues.append(msg)
    if ADJ_TRIPLE.search(text):
        issues.append("Three stacked adjectives in a row")
    for buzz in BUZZWORDS:
        if re.search(buzz, text, re.I):
            issues.append("Buzzword detected")
            break
    if text.count("\n\n") >= 4:
        issues.append("Too many paragraphs (prefer 1)")
    return sorted(set(issues))

def rewrite_once(text: str, language_hint: str = "auto") -> str:
    prompt = f"""Language: {language_hint}.
Rewrite the text under <<< >>> to follow the guide.
<<<
{text}
>>>"""
    resp = client.responses.create(
        model="gpt-4o-mini",
        input=[{"role": "system", "content": SYSTEM_GUIDE},
               {"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return resp.output_text.strip()

def humanize_core(text: str, language_hint: str = "auto", max_fixes: int = 1):
    out = rewrite_once(text, language_hint)
    issues = lint(out)
    if issues and max_fixes > 0:
        fix_prompt = f"""You violated these rules: {issues}.
Fix the text. Return only the corrected text.
TEXT:
{out}"""
        resp = client.responses.create(
            model="gpt-4o-mini",
            input=[{"role": "system", "content": SYSTEM_GUIDE},
                   {"role": "user", "content": fix_prompt}],
            temperature=0.2,
        )
        out = resp.output_text.strip()
        issues = lint(out)
    return out, issues

class HumanizeIn(BaseModel):
    text: str
    language_hint: str | None = "auto"

class HumanizeOut(BaseModel):
    rewritten: str
    remaining_issues: list[str]

@app.post("/api/humanize", response_model=HumanizeOut)
def humanize_endpoint(payload: HumanizeIn):
    rewritten, issues = humanize_core(
        payload.text, payload.language_hint or "auto", max_fixes=1
    )
    return {"rewritten": rewritten, "remaining_issues": issues}
