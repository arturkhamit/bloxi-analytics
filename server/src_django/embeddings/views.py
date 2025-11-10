import json
import ollama
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pgvector.django import CosineDistance
from sentence_transformers import SentenceTransformer

from .models import ItemEmbedding

# INITIALIZATION
try:
    EMBEDDING_MODEL = SentenceTransformer(
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    LLM_CLIENT = ollama.Client(host="http://localhost:11434")
    LLM_CLIENT.list()  # checking for a connection
    print("Models and Ollama client loaded successfully.")
except Exception as e:
    print(f"Failed to load models or connect to Ollama: {e}")
    EMBEDDING_MODEL = None
    LLM_CLIENT = None


@csrf_exempt
def ask_rag_question(request):
    if request.method == "POST":
        if not EMBEDDING_MODEL or not LLM_CLIENT:
            return JsonResponse(
                {"error": "Models or Ollama are not initialized."}, status=500
            )

        try:
            data = json.loads(request.body)
            query = data.get("query")
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON."}, status=400)

        if not query:
            return JsonResponse({"error": "No query provided."}, status=400)

        try:
            query_embedding = EMBEDDING_MODEL.encode(query)

            similar_items = (
                ItemEmbedding.objects.annotate(
                    distance=CosineDistance("embedding", query_embedding)
                )
                .order_by("distance")[:5]
            )

            if not similar_items:
                return JsonResponse(
                    {
                        "answer": "I could not find any relevant items in the database.",
                        "similar_items": similar_items,
                    }
                )

            context_items = [item_emb.text_content for item_emb in similar_items]
            context = "\n\n".join(context_items)


            prompt = (
                "You are an assistant who answers questions based ONLY on the context provided. "
                "If the information is not in the context, say 'I do not have that information in the context.'\n\n"
                f"Context:\n{context}\n\n"
                f"Question:\n{query}\n\n"
                "Answer:"
            )

            response = LLM_CLIENT.chat(  # MAKE CONNECTION WITH LM
                model="llama3.1", messages=[{"role": "user", "content": prompt}]
            )
            answer = response["message"]["content"]

            return JsonResponse({"answer": answer, "context": context})

        except Exception as e:
            print(f"Error during RAG execution: {e}")
            return JsonResponse(
                {"error": f"An internal error occurred: {e}"}, status=500
            )

    return JsonResponse({"error": "Only POST method is allowed."}, status=405)
