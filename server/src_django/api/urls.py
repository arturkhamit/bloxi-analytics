from django.urls import path

# 1. Импортируйте все ваши views
from .views import (
    ask_rag_question,
    get_receipts_last_day,
    get_receipts_last_week,
    get_receipts_last_month,
    get_receipts_from_day_to_day
)

urlpatterns = [
    path('rag/', ask_rag_question, name='ask-rag-question'),

    path('get_receipts_from_day_to_day/', get_receipts_from_day_to_day, name='get_receipts_from_day_to_day'),
    path('get_receipts_last_day/', get_receipts_last_day, name='get_receipts_last_day'),
    path('get_receipts_last_week/', get_receipts_last_week, name='get_receipts_last_week'),
    path('get_receipts_last_month/', get_receipts_last_month, name='get_receipts_last_month'),
]
