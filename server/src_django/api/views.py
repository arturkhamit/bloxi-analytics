# from rest_framework import viewsets
# from db.models import Item, Transaction
# from .serializers import ItemSerializer, TransactionSerializer

# class ItemViewSet(viewsets.ModelViewSet):
#     queryset = Item.objects.all()
#     serializer_class = ItemSerializer

# class TransactionViewSet(viewsets.ModelViewSet):
#     queryset = Transaction.objects.all()
#     serializer_class = TransactionSerializer

import json
from datetime import datetime, time, timedelta

from db.models import Transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from embeddings.models import ItemEmbedding
from pgvector.django import CosineDistance
from sentence_transformers import SentenceTransformer

print("Loading Embedding model...")
EMBEDDING_MODEL = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)


def get_organization_info(org):
    org_street_name = ""
    org_building_number = ""
    org_postal_code = ""
    org_municipality = ""
    org_country = ""
    if org.street_name:
        org_street_name = org.street_name
    if org.building_number:
        org_building_number = org.building_number
    if org.postal_code:
        org_postal_code = org.postal_code
    if org.municipality:
        org_municipality = org.municipality
    if org.country:
        org_country = org.country

    org_address = (
        f"{org_street_name} {org_building_number}, "
        f"{org_postal_code} {org_municipality}, {org_country}"
    )
    return org_address


def get_receipts_in_range(start_date, end_date):
    try:
        receipts = (
            Transaction.objects.filter(
                issue_date__gte=start_date, issue_date__lte=end_date
            )
            .select_related("org", "unit")
            .prefetch_related("item_set")
            .order_by("-issue_date")
        )

        data = []
        statistics = {"organizations": {}, "products": {}, "categories": {}}
        for receipt in receipts:
            org = receipt.org

            org_address = get_organization_info(org)

            statistics["organizations"][org.name] = (
                statistics["organizations"].get(org.name, 0) + 1
            )
            items_list = []
            receipt_total_price = 0

            for item in receipt.item_set.all():
                category = item.ai_category
                quantity = float(item.quantity or 0)
                price = float(item.price or 0)
                total_line_price = quantity * price

                receipt_total_price += total_line_price

                items_list.append(
                    {
                        "name": item.name,
                        "quantity": quantity,
                        "price": price,
                        "category": category,
                    }
                )
                statistics["products"][item.name] = (
                    statistics["products"].get(item.name, 0) + 1
                )
                statistics["categories"][category] = (
                    statistics["categories"].get(category, 0) + 1
                )

            receipt_data = {
                "receipt_id": receipt.id,
                "issue_date": receipt.issue_date,
                "organization": {
                    "organization_name": org.name,
                    "organization_address": org_address,
                },
                "products": items_list,
                "total_price": receipt_total_price,
            }
            data.append(receipt_data)
        # print(data)
        # renderStatistics({
        #   shops: [],
        #   products: [],
        #   categories: []
        # }, [receiptData]);
        data.append(statistics)
        return JsonResponse(data, safe=False)

    except Exception as e:
        print(f"Error in get_receipts_in_range: {e}")
        return JsonResponse({"error": f"An internal error occurred: {e}"}, status=500)


@csrf_exempt
def get_receipts_from_day_to_day(request):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET method is allowed."}, status=405)

    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")

    if not start_date_str or not end_date_str:
        return JsonResponse(
            {
                "error": "Missing parameters. Both 'start_date' and 'end_date' are required (YYYY-MM-DD)."
            },
            status=400,
        )

    try:
        start_date_obj = datetime.fromisoformat(start_date_str).date()
        end_date_obj = datetime.fromisoformat(end_date_str).date()

        start_date = timezone.make_aware(datetime.combine(start_date_obj, time.min))
        end_date = timezone.make_aware(datetime.combine(end_date_obj, time.max))

    except ValueError:
        return JsonResponse(
            {"error": "Invalid date format. Please use YYYY-MM-DD."}, status=400
        )

    return get_receipts_in_range(start_date, end_date)


@csrf_exempt
def get_receipts_last_day(request):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET method is allowed."}, status=405)

    end_date = timezone.now()
    start_date = end_date - timedelta(days=1)

    return get_receipts_in_range(start_date, end_date)


@csrf_exempt
def get_receipts_last_week(request):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET method is allowed."}, status=405)

    end_date = timezone.now()
    start_date = end_date - timedelta(weeks=1)

    return get_receipts_in_range(start_date, end_date)


@csrf_exempt
def get_receipts_last_month(request):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET method is allowed."}, status=405)

    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)

    return get_receipts_in_range(start_date, end_date)


@csrf_exempt
def ask_rag_question(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method is allowed."}, status=405)

    if not EMBEDDING_MODEL:
        return JsonResponse({"error": "Backend models is not initialized."}, status=503)

    try:
        data = json.loads(request.body)
        query = data.get("query")
        number_of_similar_receipts = data.get("receipts_count")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    if not query:
        return JsonResponse({"error": "No 'query' provided in JSON body."}, status=400)
    if not number_of_similar_receipts:
        return JsonResponse(
            {"error": "No 'receipts_count' provided in JSON body."}, status=400
        )

    try:
        query_embedding = EMBEDDING_MODEL.encode(query)

        similar_items = ItemEmbedding.objects.annotate(
            distance=CosineDistance("embedding", query_embedding)
        ).order_by("distance")[:number_of_similar_receipts]

        if not similar_items:
            return JsonResponse(
                {
                    "answer": "I could not find any relevant items in the database for your query.",
                    "context": "",
                }
            )
        context = "Similar items: \n\n"
        for item in similar_items:
            context += item.text_content + "\n\n"
        return JsonResponse(context, safe=False)
    #     context_items = [item.text_content for item in similar_items]
    #     context = "\n\n".join(context_items)

    #     prompt = (
    #         "You are an assistant who answers questions based ONLY on the context provided. "
    #         "If the information is not in the context, say 'I do not have that information.'\n\n"
    #         f"Context:\n{context}\n\n"
    #         f"Question: {query}\n\n"
    #         "Answer:"
    #     )

    #     print("-------------------------Prompt-------------------------\n\n")
    #     print(prompt)
    #     print("\n\n---------------------------------------------------------------")
    #     response = LLM_CLIENT.chat(
    #         model="llama3.1",
    #         messages=[{"role": "user", "content": prompt}]
    #     )

    #     answer = response["message"]["content"]

    #     return JsonResponse({"answer": answer, "context": context})

    except Exception as e:
        print(f"Error during RAG execution: {e}")
        return JsonResponse({"error": f"An internal error occurred: {e}"}, status=500)
