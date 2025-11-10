from fastapi import FastAPI
import requests
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/similar_receipts/{receipt_count}")
def get_receipt(receipt_count: int, query: str):
    payload = {
        "query": query,
        "receipts_count" : receipt_count
    }
    URL = "http://127.0.0.1:8000/api/rag/"
    try:
        response = requests.post(URL, json=payload)

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Error contacting RAG service: {e}")

@app.get("/receipts/")
def get_receipts_from_day_to_day(start_date: str, end_date: str):
    URL = "http://127.0.0.1:8000/api/get_receipts_from_day_to_day/"
    try:
        response = requests.get(URL, params={"start_date": start_date, "end_date": end_date})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Error contacting Django service: {e}")


@app.get("/receipts/last-day")
def get_receipts_last_day():
    URL = "http://127.0.0.1:8000/api/get_receipts_last_day"
    try:
        response = requests.get(URL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Error contacting Django service: {e}")


@app.get("/receipts/last-week")
def get_receipts_last_week():
    URL = "http://127.0.0.1:8000/api/get_receipts_last_week"
    try:
        response = requests.get(URL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Error contacting Django service: {e}")


@app.get("/receipts/last-month")
def get_receipts_last_month():
    URL = "http://127.0.0.1:8000/api/get_receipts_last_month"
    try:
        response = requests.get(URL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Error contacting Django service: {e}")
