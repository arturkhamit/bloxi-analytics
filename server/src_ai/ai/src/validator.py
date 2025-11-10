import re
import json
from pathlib import Path
from typing import Set

from jsonschema import validate, ValidationError

# Корінь проєкту /ai
ROOT = Path(__file__).resolve().parents[1]

# JSON Schema для відповіді від LLM (sql, explanation, params)
SCHEMA_PATH = ROOT / "config" / "json_schema.sqlgen.json"
JSON_SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

# Які таблиці дозволено використовувати в SQL
ALLOWED_TABLES: Set[str] = {"item", "transaction", "unit", "organization"}

# Заборонені токени / ключові слова (безпека)
DENY = re.compile(
    r"(;|--|/\*|\b(INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|GRANT|REVOKE|SET|SHOW|COPY|CALL|DO|TRUNCATE|SECURITY|POLICY)\b)",
    re.I,
)

# Шукаємо посилання на таблиці в FROM / JOIN
# Приклади, які матчаться:
#   FROM item i
#   from transaction t
#   JOIN unit u ON ...
#   join organization o on ...
TABLE_REF_RE = re.compile(
    r"\b(from|join)\s+([a-zA-Z_][a-zA-Z0-9_\.]*)",
    re.I,
)


def _basic_sql_safety(sql: str) -> None:
    """
    Базова перевірка безпеки SQL:
    - тільки SELECT
    - немає заборонених ключових слів та символів
    """
    stripped = sql.strip().lower()
    if not stripped.startswith("select"):
        raise ValueError("Only SELECT queries are allowed")

    if DENY.search(sql):
        raise ValueError(f"Forbidden SQL token found in SQL: {sql}")


def _extract_tables(sql: str) -> Set[str]:
    """
    Дістає імена таблиць з виразів FROM / JOIN.

    Повертає сет нижньорегістрових імен таблиць без схеми:
    - 'public.item' -> 'item'
    - 'item'        -> 'item'
    """
    tables: Set[str] = set()
    for _kw, raw_name in TABLE_REF_RE.findall(sql):
        # Розбиваємо schema.table або просто table
        base = raw_name.split(".")[-1].lower()
        tables.add(base)
    return tables


def _validate_allowed_tables(sql: str) -> None:
    """
    Перевіряє, що в FROM / JOIN використовуються тільки дозволені таблиці.
    """
    tables = _extract_tables(sql)

    if not tables:
        raise ValueError("No table references (FROM/JOIN) found in SQL.")

    illegal = tables - ALLOWED_TABLES
    if illegal:
        raise ValueError(
            f"Query uses disallowed tables: {', '.join(sorted(illegal))}. "
            f"Allowed tables are: {', '.join(sorted(ALLOWED_TABLES))}."
        )


def validate_payload(payload: dict) -> None:
    """
    1) Перевіряє JSON-схему (структура відповіді LLM).
    2) Перевіряє, що SQL:
       - починається з SELECT
       - не містить заборонених токенів (INSERT, DROP, ;, коментарі тощо)
       - використовує тільки таблиці item, transaction, unit, organization
    """
    # 1) Валідація структури JSON
    try:
        validate(instance=payload, schema=JSON_SCHEMA)
    except ValidationError as e:
        raise ValueError(f"Invalid JSON structure from LLM: {e.message}") from e

    sql = payload["sql"]

    # 2) Базові перевірки безпеки
    _basic_sql_safety(sql)

    # 3) Перевірка таблиць
    _validate_allowed_tables(sql)
