# -*- coding: utf-8 -*-
"""
Quick local demo for the LLM → SQL → (mock DB) → final text flow.

How to run (Windows / venv activated):
  (venv) C:\...\Erste_hack\ai\src> python test_sqlgen_flow.py

What it does:
- Reads a question from stdin.
- Calls ask_sql(question) from sqlgen.py
- SIMULATES DB rows (no real DB!) based on the question/SQL shape.
- Calls build_final_text(...) to produce ONE final text for the frontend.
- Prints the SQL, params, mock rows, and the final text.

Exit by pressing Enter on an empty line.
"""

from __future__ import annotations
import json
import re

# Import your existing functions from sqlgen.py
from src.sqlgen import ask_sql, build_final_text, infer_locale


import os
import psycopg

USE_REAL_DB = True  # постав False, якщо хочеш повернутись на моки

def _ordered_params(params: dict) -> tuple:
    """
    Перетворює {"$1": v1, "$2": v2, ...} -> (v1, v2, ...)
    Важливо: LLM завжди дає $1, $2 ... — сортуємо за числом.
    """
    if not params:
        return tuple()
    items = sorted(params.items(), key=lambda kv: int(kv[0].lstrip("$")))
    return tuple(v for _, v in items)

def _connect_dsn() -> str:
    # будуємо DSN з env, або можна прямо os.getenv(...) у connect(**kwargs)
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    user = os.getenv("PGUSER", "receipts_user")
    password = os.getenv("PGPASSWORD", "mypassword")
    dbname = os.getenv("PGDATABASE", "receiptsdb")
    return f"host={host} port={port} user={user} password={password} dbname={dbname}"

def execute_on_postgres(sql: str, params: dict):
    """
    Виконує SELECT і повертає список dict-ів: [{col: val, ...}, ...]
    - Плейсхолдери у твоєму SQL: $1, $2, ...
    - psycopg приймає позиційні параметри як %s, але ПСГ 3 вміє напряму з $1?..
      Тому ми просто передаємо позиційний tuple, і psycopg підставить значення.
    """
    dsn = _connect_dsn()
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, _ordered_params(params))
            rows = cur.fetchall() if cur.description else []
            cols = [c.name for c in cur.description] if cur.description else []
    out = []
    for r in rows:
        obj = {}
        for k, v in zip(cols, r):
            if hasattr(v, "isoformat"):
                obj[k] = v.isoformat()
            else:
                obj[k] = v
        out.append(obj)
    return out



# -----------------------------
# Mock "DB execution" section
# -----------------------------

def _looks_like_top(sql: str, question: str) -> bool:
    s = (sql or "").lower()
    q = (question or "").lower()
    # Heuristic: GROUP BY + ORDER BY + LIMIT 10, or the question says "top"
    return ("group by" in s and "order by" in s and "limit" in s) or ("top" in q or "top " in q)

def _looks_like_sum(sql: str, question: str) -> bool:
    s = (sql or "").lower()
    q = (question or "").lower()
    return "sum(" in s or "how much" in q or "koľko som minul" in q or "kolko som minul" in q

def _looks_like_count(sql: str, question: str) -> bool:
    s = (sql or "").lower()
    q = (question or "").lower()
    return "count(" in s or "how many" in q or "koľko" in q or "kolko" in q

def simulate_db_execute(sql: str, params: dict, question: str):
    """
    Produce fake rows that look like real DB results.
    You can tweak this to mirror your actual SELECT shapes.
    """
    # Top-K style (brands/categories with totals)
    if _looks_like_top(sql, question):
        # Return 10 rows for "Top 10 ..." feel
        return [
            {"ai_brand": f"Brand {chr(65+i)}", "total_spent": round(100 - i * 7.3, 2)}
            for i in range(10)
        ]

    # SUM money → single KPI row
    if _looks_like_sum(sql, question) and not _looks_like_top(sql, question):
        return [{"total_spent": 87.9}]

    # COUNT → single KPI row
    if _looks_like_count(sql, question) and not _looks_like_top(sql, question):
        return [{"count": 12}]

    # Fallback: a small table of purchases (for “last purchases”, generic lists)
    return [
        {"name": "Orange Juice", "price": 1.80},
        {"name": "Non-Alcoholic Beer", "price": 1.50},
        {"name": "Ribs in BBQ", "price": 9.90},
        {"name": "Rice Noodles with Duck Breast", "price": 10.90},
        {"name": "Paper Bag", "price": 0.30},
    ]

# -----------------------------
# Pretty printers
# -----------------------------

def _print_header(title: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

def _print_rows(rows):
    if not rows:
        print("(no rows)")
        return
    # print as a mini-table (keys from first row)
    keys = list(rows[0].keys())
    print("Columns:", ", ".join(keys))
    for i, r in enumerate(rows, 1):
        vals = [str(r.get(k)) for k in keys]
        print(f"{i:02d}. " + " | ".join(vals))

# -----------------------------
# Main demo loop
# -----------------------------

def main():
    print("LLM → SQL → (mock DB) → final text")
    print("Type a question (SK/EN/UKR). Empty line to exit.")
    while True:
        try:
            q = input("\nOtázka / Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not q:
            break

        # 1) First call: LLM → SQL
        _print_header("1) Generating SQL via LLM")
        payload = ask_sql(q) # format sql-request
        print("SQL:", payload["sql"])
        print("Params:", json.dumps(payload.get("params", {}), ensure_ascii=False))
        print("Explanation:", payload.get("explanation", ""))

        # 2) Execute DB
        _print_header("2) DB rows (real)" if USE_REAL_DB else "2) Simulated DB rows (mock)")
        if USE_REAL_DB:
            rows = execute_on_postgres(payload["sql"], payload.get("params", {}))
        else:
            rows = simulate_db_execute(payload["sql"], payload.get("params", {}), q)
        _print_rows(rows)

        # 3) Build the final user-facing text (headline from LLM + optional list from rows)
        _print_header("3) Final text (to frontend)")
        locale = infer_locale(q)  # or hardcode "sk"/"en"
        final_text = build_final_text(q, payload, rows, locale=locale)
        print(final_text)

        print("\n(locale:", locale, ")")

    print("\nBye.")

if __name__ == "__main__":
    main()
