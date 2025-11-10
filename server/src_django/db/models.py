from django.db import models

# -- ======================================
# -- ORGANIZATION
# -- ======================================
# CREATE TABLE organization (
#     id BIGINT PRIMARY KEY,
#     ico TEXT,
#     dic TEXT,
#     ic_dph TEXT,
#     name TEXT,
#     building_number TEXT,
#     country TEXT,
#     municipality TEXT,
#     postal_code TEXT,
#     street_name TEXT
# );


class Organization(models.Model):
    id = models.BigAutoField(
        primary_key=True, unique=True, verbose_name="id of an organization"
    )
    ico = models.TextField(
        verbose_name="ICO (indetifikacne cislo organizacie) of an organization"
    )
    dic = models.TextField(
        verbose_name="DIC (danove identifikacne cislo) of an organization"
    )
    ic_dph = models.TextField(verbose_name="organization's identificator for taxes")
    name = models.TextField(verbose_name="organization name")
    building_number = models.TextField(
        verbose_name="building number of an organization"
    )
    country = models.TextField(verbose_name="country, where an organization is located")
    municipality = models.TextField(
        verbose_name="town, where an organization is located"
    )
    postal_code = models.TextField(verbose_name="organization's local postal code")
    street_name = models.TextField(verbose_name="organization's location street name")

    class Meta:
        db_table = "organization"
        verbose_name = "organization"
        verbose_name_plural = "organizations"
        ordering = ["id"]

    def __str__(self):
        return "organization model"


# -- ======================================
# -- UNIT (store branch)
# -- ======================================
# CREATE TABLE unit (
#     id BIGINT PRIMARY KEY,
#     org_id BIGINT REFERENCES organization(id) ON DELETE CASCADE,
#     name TEXT,
#     country TEXT,
#     municipality TEXT,
#     postal_code TEXT,
#     building_number TEXT,
#     property_registration_number TEXT,
#     street_name TEXT,
#     latitude DOUBLE PRECISION,
#     longitude DOUBLE PRECISION
# );
class Unit(models.Model):
    id = models.BigAutoField(
        primary_key=True, unique=True, verbose_name="id of an unit"
    )
    org = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
    )
    name = models.TextField(verbose_name="local street name of unit")
    country = models.TextField(verbose_name="country of unit")
    municipality = models.TextField(verbose_name="unit's name of town")
    postal_code = models.TextField(verbose_name="unit's local postal code")
    building_number = models.TextField(verbose_name="building number of unit")
    property_registration_number = models.TextField(
        verbose_name="unit's property registration number"
    )
    street_name = models.TextField(verbose_name="unit's local street name")
    latitude = models.FloatField(verbose_name="unit's latitude on world map")
    longitude = models.FloatField(verbose_name="unit's longitude on world map")

    class Meta:
        db_table = "unit"
        verbose_name = "unit"
        verbose_name_plural = "units"
        ordering = ["id"]

    def __str__(self):
        return "unit model"


# -- ======================================
# -- TRANSACTION (receipt)
# -- ======================================
# CREATE TABLE transaction (
#     id BIGINT PRIMARY KEY,  -- formerly fs_receipt_id
#     issue_date TIMESTAMPTZ,
#     org_id BIGINT REFERENCES organization(id) ON DELETE CASCADE,
#     unit_id BIGINT REFERENCES unit(id) ON DELETE CASCADE
# );
class Transaction(models.Model):
    id = models.BigAutoField(
        primary_key=True, unique=True, verbose_name="id of a transaction"
    )

    issue_date = models.DateTimeField("transaction's date and time of creating")
    org = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = "transaction"
        verbose_name = "transaction"
        verbose_name_plural = "transactions"
        ordering = ["id"]

    def __str__(self):
        return "transaction model"


# -- ======================================
# -- ITEM (line item with AI fields)
# -- ======================================
# CREATE TABLE item (
#     id BIGINT PRIMARY KEY,
#     transaction_id BIGINT REFERENCES transaction(id) ON DELETE CASCADE,
#     quantity DOUBLE PRECISION,
#     name TEXT,
#     price NUMERIC(12,6),


#     -- AI fields (prefixed by ai_)
#     ai_name_without_brand_and_quantity TEXT,
#     ai_name_in_english_without_brand_and_quantity TEXT,
#     ai_brand TEXT,
#     ai_category TEXT,
#     ai_quantity_value DOUBLE PRECISION,
#     ai_quantity_unit TEXT
# );
class Item(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True, verbose_name="item's id")
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
    )
    quantity = models.FloatField(verbose_name="item quantity")
    name = models.TextField(verbose_name="item's name")
    price = models.DecimalField(
        max_digits=12, decimal_places=6, verbose_name="total price of an item"
    )
    ai_name_without_brand_and_quantity = models.TextField(
        verbose_name="name without brand and quantity"
    )
    ai_name_in_english_without_brand_and_quantity = models.TextField(
        verbose_name="name in english without brand and quantity"
    )
    ai_brand = models.TextField(verbose_name="brand of an item")
    ai_category = models.TextField(verbose_name="category of an item")
    ai_quantity_value = models.FloatField(
        verbose_name="quantity value"  # Rewrite verbose_name
    )
    ai_quantity_unit = models.TextField(verbose_name="quantity unit")

    class Meta:
        db_table = "item"
        verbose_name = "item"
        verbose_name_plural = "items"
        ordering = ["id"]

    def __str__(self):
        return "item model"
