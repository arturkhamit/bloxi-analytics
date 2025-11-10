# -*- coding: utf-8 -*-
"""
FastAPI endpoint для LLM → SQL → DB → final text flow.
"""

import os
import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from fastapi.middleware.cors import CORSMiddleware


# Импортируем ваши существующие функции из sqlgen.py
# Убедитесь, что main.py лежит так, что src.sqlgen доступен
from src.sqlgen import ask_sql, build_final_text, infer_locale

# ---
# Копируем логику для работы с БД из вашего test_sqlgen_flow.py
# ---

def _ordered_params(params: dict) -> tuple:
    """
    Превращает {"$1": v1, "$2": v2, ...} -> (v1, v2, ...)
    """
    if not params:
        return tuple()
    items = sorted(params.items(), key=lambda kv: int(kv[0].lstrip("$")))
    return tuple(v for _, v in items)

def _connect_dsn() -> str:
    # строим DSN из env
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    user = os.getenv("PGUSER", "receipts_user")
    password = os.getenv("PGPASSWORD", "mypassword")
    dbname = os.getenv("PGDATABASE", "receiptsdb")
    return f"host={host} port={port} user={user} password={password} dbname={dbname}"

import re # Не забудьте добавить import re вверху файла

def execute_on_postgres(sql: str, params: dict):
    """
    Выполняет SELECT и возвращает список dict-ов: [{col: val, ...}, ...]
    """
    if not sql:
        return []

    dsn = _connect_dsn()
    param_tuple = _ordered_params(params)

    # --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---

    # 1. Сначала проверяем, не вставила ли LLM значения прямо в SQL
    # (Это исправление из нашего предыдущего шага, оно все еще нужно)
    # Ищем $1 ИЛИ %s (на всякий случай)
    has_placeholders = "$1" in sql or "%s" in sql

    if param_tuple and not has_placeholders:
        print("Warning: Params detected, but no placeholders found in SQL. Executing as-is.")
        param_tuple = tuple() # Игнорируем параметры

    # 2. НОВОЕ: Конвертируем $1, $2... в %s для psycopg2
    # Делаем это, только если параметры есть и синтаксис $1 используется
    elif param_tuple and "$1" in sql:
        print("Info: Converting $N placeholders to %s for psycopg2.")
        # Заменяем все $1, $2, $10 и т.д. на %s
        sql = re.sub(r'\$\d+', '%s', sql)

    # --- КОНЕЦ ИСПРАВЛЕНИЯ ---

    try:
        with psycopg.connect(dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                # 'sql' теперь либо оригинальный (если был %s),
                # либо исправленный (если был $1),
                # а 'param_tuple' либо полный, либо пустой
                cur.execute(sql, param_tuple)

                rows = cur.fetchall() if cur.description else []
                cols = [c.name for c in cur.description] if cur.description else []
    except Exception as e:
        # ... (остальная часть вашей обработки ошибок)
        print(f"Error executing SQL: {e}")
        raise HTTPException(status_code=500, detail=f"Database execution error: {str(e)}")

    # ... (остальная часть функции)
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

# ---
# Логика FastAPI
# ---

# 1. Определяем модели Pydantic для запроса и ответа
class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str       # Финальный текстовый ответ
    sql: str          # SQL, который был сгенерирован
    params: dict      # Параметры для SQL
    locale: str       # Определенный язык
    rows_count: int   # Количество строк из БД

# 2. Создаем приложение FastAPI
app = FastAPI(
    title="LLM SQL Bot API",
    description="API для преобразования вопросов на естественном языке в SQL и получения ответа из БД."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
import datetime
# 3. Создаем эндпоинт
@app.post("/ask", response_model=AnswerResponse)
def handle_ask(request: QuestionRequest):
    """
    Принимает вопрос, выполняет весь пайплайн (LLM->SQL, DB->Rows, LLM->Text)
    и возвращает готовый ответ.
    """
    q = request.question
    if not q:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        # 1) Определяем язык
        print(1)
        locale = infer_locale(q)
        print(q)
        # 2) Первый вызов: LLM → SQL
        print(2)
        payload = ask_sql(q)
        sql = payload.get("sql")
        params = payload.get("params", {})

        # --- ИСПРАВЛЕНИЕ ДЛЯ "specified_date" ---
        # Ищем все значения-заполнители и меняем их на сегодняшнюю дату
        today_str = datetime.date.today().isoformat()
        for key, value in params.items():
            if value == "specified_date":
                print(f"Info: Replacing '{value}' with today's date: {today_str}")
                params[key] = today_str
        # --- КОНЕЦ ИСПРАВЛЕНИЯ ---

        # 3) Выполняем запрос к БД (реальной)
        rows = execute_on_postgres(sql, params)

        # 4) Строим финальный ответ для пользователя
        print(4)
        print(payload)
        final_text = build_final_text(q, payload, rows, locale=locale)
        print(5)
        # 5) Возвращаем структурированный ответ
        return AnswerResponse(
            answer=final_text,
            sql=sql,
            params=params,
            locale=locale,
            rows_count=len(rows)
        )

    except HTTPException as e:
        # Перехватываем ошибки, которые мы сами сгенерировали (напр. ошибка БД)
        raise e
    except Exception as e:
        # Ловим все остальные непредвиденные ошибки
        print(f"Unhandled error processing request: {e}")
        # Важно! В production не стоит показывать `str(e)` пользователю
        raise HTTPException(status_code=500, detail="An internal server error occurred.")
