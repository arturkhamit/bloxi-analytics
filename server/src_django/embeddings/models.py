from db.models import Item
from django.db import models
from pgvector.django import HnswIndex, VectorField


class ItemEmbedding(models.Model):
    item = models.OneToOneField(
        Item, on_delete=models.CASCADE, related_name="embedding"
    )

    text_content = models.TextField()

    embedding = VectorField(dimensions=384, null=True, blank=True)

    class Meta:
        indexes = [
            HnswIndex(
                name="embedding_hnsw_idx",
                fields=["embedding"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            )
        ]
