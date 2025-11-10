from db.models import Item
from django.core.management.base import BaseCommand
from embeddings.models import ItemEmbedding
from sentence_transformers import SentenceTransformer


class Command(BaseCommand):
    """Generates and saves embeddings for all items with detailed context"""

    def add_arguments(self, parser):
        parser.add_argument(
            "--rebuild",
            action="store_true",
            help="Force re-generation of embeddings for ALL items, deleting old ones.",
        )

    def handle(self, *args, **options):
        self.stdout.write("Loading embedding model...")
        try:
            EMBEDDING_MODEL = SentenceTransformer(
                "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            )
            self.stdout.write(self.style.SUCCESS("Embedding model loaded."))
        except Exception as e:
            self.stderr.write(f"Failed to load SentenceTransformer model: {e}")
            return
        rebuild_all = options["rebuild"]

        if rebuild_all:
            self.stdout.write(
                self.style.WARNING(
                    "--- REBUILD FLAG DETECTED: Deleting all existing embeddings... ---"
                )
            )
            count, _ = ItemEmbedding.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f"Successfully deleted {count} old embeddings.")
            )

        self.stdout.write("Querying database for items to index...")

        items_to_process = Item.objects.select_related(
            "transaction",
            "transaction__unit",
            "transaction__org",
        ).filter(embedding__isnull=True)

        count = items_to_process.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS("No new items to embed. Exiting."))
            return

        self.stdout.write(f"Found {count} items to textualize and embed...")

        embeddings_to_create = []
        texts_to_encode = []
        items_to_process_list = []

        for item in items_to_process:
            try:
                transaction = item.transaction
                # unit = transaction.unit
                # org = transaction.org

                item_text = (
                    f"Item purchased: {item.name} (ID: {item.id}). "
                    f"Price: {item.price} euros for {item.quantity} units. "
                    # f"AI analysis: [Product Name: {item.ai_name_without_brand_and_quantity}, "
                    f"Brand: {item.ai_brand}, Category: {item.ai_category}, "
                    f"Quantity Value: {item.ai_quantity_value}, Unit: {item.ai_quantity_unit}]."
                )

                trans_text = (
                    f"Receipt (Transaction) ID: {transaction.id}. "
                    f"Date: {transaction.issue_date.strftime('%Y-%m-%d %H:%M:%S')}."
                )

                # unit_text = (
                #     f"Store (Unit) Details: {unit.name} (ID: {unit.id}). "
                #     f"Address: {unit.street_name} {unit.building_number} (Reg Num: {unit.property_registration_number}), "
                #     f"{unit.postal_code} {unit.municipality}, {unit.country}. "
                #     f"Coordinates: (Lat: {unit.latitude}, Lon: {unit.longitude})."
                # )

                # org_text = (
                #     f"Company (Organization) Details: {org.name} (ID: {org.id}). "
                #     f"Company Identifiers: [ICO: {org.ico}, DIC: {org.dic}, IC DPH: {org.ic_dph}]. "
                #     f"Address: {org.street_name} {org.building_number}, {org.postal_code} {org.municipality}, {org.country}."
                # )

                text_content = f"{item_text} Part of: {trans_text}"  #  Purchased at: {unit_text} Owned by: {org_text}

                texts_to_encode.append(text_content)
                items_to_process_list.append(item)
            except Exception as e:
                self.stderr.write(f"Error processing item {item.id}: {e}")

        self.stdout.write("Generating all embeddings in a single batch...")
        all_vectors = EMBEDDING_MODEL.encode(texts_to_encode, show_progress_bar=True)

        self.stdout.write("Creating objects for database...")

        embeddings_to_create = []

        for item, text, vector in zip(
            items_to_process_list, texts_to_encode, all_vectors
        ):
            embeddings_to_create.append(
                ItemEmbedding(item=item, text_content=text, embedding=vector)
            )
        self.stdout.write(
            f"Saving {len(embeddings_to_create)} new embeddings to the database..."
        )
        ItemEmbedding.objects.bulk_create(embeddings_to_create, ignore_conflicts=True)
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {len(embeddings_to_create)} new embeddings."
            )
        )
