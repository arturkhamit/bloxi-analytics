from django.test import TestCase

from .models import User, Receipt, Product


class ModelQueryTests(TestCase):
    def test_model_queries(self):
        print("--- Все User ---")
        all_data = User.objects.all()
        print(f"Найдено: {all_data.count()}")
        print(all_data)

        print("--- Все Receipt ---")
        all_data = Receipt.objects.all()
        print(f"Найдено: {all_data.count()}")
        print(all_data)

        print("--- Все Product ---")
        all_data = Product.objects.all()
        print(f"Найдено: {all_data.count()}")
        print(all_data)
