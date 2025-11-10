from pathlib import Path
import json
import re
import sys
from typing import Dict, List, Any
from .llm_client import OllamaClient
from .validator import validate_payload

ROOT = Path(__file__).resolve().parents[1]

SYSTEM_PROMPT = (ROOT / "prompts" / "system.md").read_text(encoding="utf-8")
SCHEMA_PROMPT = (ROOT / "prompts" / "schema.md").read_text(encoding="utf-8")
EXAMPLES_PROMPT = (ROOT / "prompts" / "examples.md").read_text(encoding="utf-8")
client = OllamaClient(model="llama3.1")

def extract_json_object(text: str) -> dict:
    """
    Пытається дістати JSON-об'єкт з довільного тексту:
    - якщо текст уже починається з { — парсимо напряму
    - якщо є ``` ``` або ```json ``` — беремо те, що між ними
    - fallback: шукаємо першу { і останню }, парсимо шматок між ними
    """
    text = text.strip()

    # 1) якщо відповідь вже чистий JSON
    if text.startswith("{") and text.endswith("}"):
        return json.loads(text)

    # 2) шукаємо ```json ...``` або ``` ...``` з об'єктом всередині
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if fence_match:
        json_str = fence_match.group(1)
        return json.loads(json_str)

    # 3) fallback: перша { і остання }
    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last != -1 and first < last:
        json_str = text[first:last+1]
        return json.loads(json_str)

    # якщо так і не знайшли — кидаємо помилку
    raise ValueError("Cannot find a valid JSON object in LLM response.")





def infer_locale(question: str) -> str:
    """
    Very small SK vs EN heuristic from the user's question.
    Returns "sk" for Slovak/Czech-ish queries, otherwise "en".
    """
    q = (question or "").lower()
    sk_markers = [
        "koľko", "kolko", "kedy", "ktoré", "ktore", "posledných", "poslednych",
    "najviac", "najmenej", "porovnaj", "porovnať", "spolu", "suma",

    # time / date
    "včera", "vcera", "dnes", "zajtra", "minulý", "minuly", "budúci", "buduci",
    "týždeň", "tyzden", "mesiac", "rok", "v roku", "za mesiac", "za týždeň",

    # shopping / receipts
    "nákup", "nakup", "nákupy", "nakupy", "pokladňa", "pokladna",
    "bloček", "blocek", "účtenka", "uctenka", "paragon",

    # stores / places
    "obchod", "predajňa", "predajna", "supermarket", "potraviny",
    "predaj", "prevádzka", "prevadzka", "pobočka", "pobocka",

    # slovak chains (proper nouns still useful as SK hint)
    "lidl", "tesco", "kaufland", "billa", "coop", "terno", "jednota",

    # cities
    "bratislava", "košice", "kosice", "žilina", "zilina", "prešov", "presov",
    "nitra", "trnava", "trenčín", "trencin", "banská bystrica", "banska bystrica",

    # categories / items (common SK words)
    "pivo", "víno", "vino", "syry", "syr", "klobása", "klobasa",
    "pečivo", "pecivo", "mlieko", "džús"
    ]
    return "sk" if any(w in q for w in sk_markers) else "en"






def build_user_prompt(question: str) -> str:
     """ Формуємо промпт для моделі: правила + few-shot приклади + схема + питання. 
     ПІД 4 ТАБЛИЦІ: item, transaction, unit, organization. """ 
     return f""" 
You are given a relational schema with FOUR tables: item, transaction, unit, organization. 
TASK: - Generate ONE PostgreSQL SELECT query that answers the user question. 
- Use ONLY the tables/columns from the schema below.
- Use positional placeholders $1, $2, ... for all dynamic values. 
- Use transaction.issue_date for ALL date filters (year/month/range/last N days). 
- Prefer ILIKE for text search (multi-language). 
- Join tables via: - item.transaction_id = transaction.id - transaction.unit_id = unit.id - transaction.org_id = organization.id 
- Return ONLY a JSON object with keys: sql, explanation, params. No markdown.

EXAMPLES (few-shot):
{EXAMPLES_PROMPT}

SCHEMA (documentation):
{SCHEMA_PROMPT}

QUESTION: 
{question} 
""".strip()






def ask_sql(question: str) -> dict:
    prompt = build_user_prompt(question)
    response_text = client.generate(
        prompt=prompt,
        system=SYSTEM_PROMPT,
        temperature=0.1, 
    )

    print("\n=== Raw model response ===")
    print(response_text)
    print("=== End raw ===\n")

    data = extract_json_object(response_text)

    # легка перевірка
    for key in ("sql", "explanation", "params"):
        if key not in data:
            raise ValueError(f"Missing key '{key}' in LLM response: {data}")
    validate_payload(data)
    return data



# -------------------------------
# NLG (second call): DB rows -> one sentence in user's language (locale inferred in backend)
# -------------------------------

NLG_SYSTEM = """You are a careful assistant that writes ONE short sentence
summarizing the provided shopping analytics ROWS in the requested LOCALE.

Return ONLY a JSON object with EXACTLY this key:
- text (string)  -- one sentence in the requested locale

Rules:
- Do NOT invent numbers, dates, shops, cities, or categories.
- Use ONLY values present in ROWS (already aggregated).
- Keep the sentence short (max ~20 words).
- If there is no data (ROWS is empty), say so politely in the locale.
- No markdown, no code fences, no extra keys.
"""




def _nlg_preview_rows(rows: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
    """Keep payload small; pass only a few rows to NLG."""
    if not rows:
        return []
    return rows[:limit]



def build_nlg_prompt(question: str, sql_payload: Dict[str, Any], rows: List[Dict[str, Any]], locale: str = "en") -> str:
    """
    Compose a compact prompt:
      - LOCALE ("sk" or "en")
      - QUESTION (raw)
      - INTENT_HINT: only 'explanation' and first ~200 chars of SQL (no need to leak full query)
      - ROWS: tiny JSON array with up to 5 rows
    """
    expl = (sql_payload or {}).get("explanation", "")
    sql_head = (sql_payload or {}).get("sql", "")[:200]
    rows_preview = _nlg_preview_rows(rows)

    return (
        f"LOCALE: {locale}\n\n"
        f"QUESTION:\n{question}\n\n"
        "INTENT_HINT:\n"
        f"{json.dumps({'explanation': expl, 'sql_head': sql_head}, ensure_ascii=False)}\n\n"
        "ROWS:\n"
        f"{json.dumps(rows_preview, ensure_ascii=False)}"
    )

# You can reuse the same model as SQL gen (llama3.1) for NLG:
nlg_client = OllamaClient(model="llama3.1")



def summarize_result(question: str, sql_payload: Dict[str, Any], rows: List[Dict[str, Any]], locale: str = "en") -> Dict[str, str]:
    """
    Second LLM call: produce ONE natural-language sentence in 'locale'.

    Inputs:
      - question: user's original question (string)
      - sql_payload: {"sql","explanation","params"} from the first call
      - rows: DB result rows (already aggregated), small list[dict]
      - locale: "sk" or "en"

    Returns:
      { "text": "<one short sentence in the requested locale>" }
    """
    prompt = build_nlg_prompt(question, sql_payload, rows or [], locale=locale)
    raw = nlg_client.generate(prompt=prompt, system=NLG_SYSTEM, temperature=0.1)

    # Expect a tiny JSON with {"text": "..."}
    try:
        candidate = raw.strip()
        if candidate.startswith("{") and candidate.endswith("}"):
            obj = json.loads(candidate)
        else:
            obj = extract_json_object(candidate)

        if isinstance(obj, dict) and isinstance(obj.get("text"), str):
            return {"text": obj["text"]}
    except Exception:
        pass

    # Fallbacks
    if not rows:
        return {"text": "Nenašli sme žiadne zodpovedajúce údaje." if locale == "sk" else "No matching data was found."}
    return {"text": "Zhrnutie je pripravené." if locale == "sk" else "Summary is ready."}




def render_rows_as_list(rows: List[Dict[str, Any]], limit: int = 10) -> str:
    """
    Build a numbered plain-text list from DB rows (1..N).
    We pick a readable label (string) and a value (number) heuristically.
    """
    rows = (rows or [])[:limit]
    if not rows:
        return ""

    # Choose label + value keys from the first row
    sample = rows[0]
    label_pref = [
        "ai_brand",
        "ai_name_in_english_without_brand_and_quantity",
        "ai_category",
        "name",
        "org_name",
        "unit_name",
    ]
    label_key = next((k for k in label_pref if k in sample and isinstance(sample[k], str)), None)
    if label_key is None:
        label_key = next((k for k, v in sample.items() if isinstance(v, str)), None)

    value_pref = ["total_spent", "sum", "total", "amount", "price", "count", "cnt"]
    value_key = next((k for k in value_pref if k in sample and isinstance(sample[k], (int, float))), None)
    if value_key is None:
        value_key = next((k for k, v in sample.items() if isinstance(v, (int, float))), None)

    lines = []
    for i, r in enumerate(rows, start=1):
        label = str(r.get(label_key)) if label_key else None
        val = r.get(value_key)

        if isinstance(val, (int, float)):
            # Money-ish keys → 2 decimals; else just str(val)
            if any(t in (value_key or "").lower() for t in ["price", "spent", "total", "sum", "amount"]):
                val_str = f"€{float(val):,.2f}"
            else:
                val_str = str(val)
        else:
            val_str = str(val) if val is not None else None

        if label and val_str:
            lines.append(f"{i}) {label} — {val_str}")
        elif label:
            lines.append(f"{i}) {label}")
        else:
            # fallback: show full row safely
            lines.append(f"{i}) " + ", ".join(f"{k}={r[k]}" for k in r.keys()))

    return "\n".join(lines)


def build_final_text_from_model_and_rows(headline_text: str, rows: List[Dict[str, Any]]) -> str:
    """
    Combine model’s one-liner with a deterministic DB list when there are multiple rows.
    - If 0/1 row: return the headline only.
    - If >1 row: append a numbered list rendered from the DB rows.
    """
    if not rows or len(rows) <= 1:
        return (headline_text or "").strip()

    list_text = render_rows_as_list(rows, limit=10)
    if not list_text:
        return (headline_text or "").strip()

    # Keep the headline from summarize_result(); list comes from DB (truth source).
    return (headline_text or "").strip() + "\n" + list_text


# ---------------------------------------------------------
# ONE FINAL OUTPUT FUNCTION (use this from backend)
# ---------------------------------------------------------

def build_final_text(question: str, sql_payload: Dict[str, Any], rows: List[Dict[str, Any]], locale: str = None) -> str:
    """
    Orchestrator:
      1) Call summarize_result() to get the model's one-sentence headline (in locale).
      2) If there are multiple DB rows, append a deterministic numbered list from the rows.
      3) Return one final text string for the frontend to display as-is.
    """
    # Decide language (or override via argument)
    if locale is None:
        locale = infer_locale(question)

    # 1) one-liner from the model
    nl = summarize_result(question, sql_payload, rows, locale=locale)
    headline = nl.get("text", "").strip()

    # 2) attach deterministic list if needed
    final_text = build_final_text_from_model_and_rows(headline, rows)

    # Fallbacks for empty headline
    if not final_text:
        if not rows:
            return "Nenašli sme žiadne zodpovedajúce údaje." if locale == "sk" else "No matching data was found."
        # at least show the list
        return render_rows_as_list(rows, limit=10)

    return final_text

