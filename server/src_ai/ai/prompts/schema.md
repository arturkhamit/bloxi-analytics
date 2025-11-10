Receipts & Shopping Analytics – Database Schema

We have four PostgreSQL tables used for receipts and shopping analytics:

organization — legal entity / company

unit — store / branch / physical location

transaction — receipt / purchase event

item — line item on a receipt (includes AI-enriched fields)

LLM must use only these tables and their relationships.

1) organization (legal entity / company)

Table name: organization

Columns

id (bigint, PRIMARY KEY) — organization identifier

ico (text) — organization identification number (ICO)

dic (text) — tax identification number (DIC)

ic_dph (text) — VAT ID

name (text) — company name, e.g., “Leder & Schuh SK spol. s r.o.”

country (text) — registered country (e.g., “Slovensko”)

municipality (text) — city/town

postal_code (text) — postal code

street_name (text) — street name

building_number (text) — building number

Notes / usage

Use organization.name when questions mention “organization/company” at legal-entity level.

Organization-level geography: organization.country, organization.municipality, organization.postal_code.

2) unit (store / branch / location)

Table name: unit

Columns

id (bigint, PRIMARY KEY) — store/branch identifier

org_id (bigint, FK → organization.id) — owning organization

name (text) — store/branch name (e.g., “CCC Avion”)

country (text) — store country

municipality (text) — store city/town (e.g., “Bratislava”)

postal_code (text) — store postal code

street_name (text) — store street name

building_number (text) — store building number

property_registration_number (text) — property reg. number

latitude (double precision) — store latitude

longitude (double precision) — store longitude

Notes / usage

City/store questions: use unit.municipality and/or unit.name.

Each unit belongs to exactly one organization: unit.org_id = organization.id.

3) transaction (receipt / purchase event)

Table name: transaction

Columns

id (bigint, PRIMARY KEY) — receipt identifier

issue_date (timestamptz) — when the receipt was issued

org_id (bigint, FK → organization.id) — issuing organization

unit_id (bigint, FK → unit.id) — store where issued

Notes / usage

All time filtering must use transaction.issue_date.

Year example:

issue_date >= '2024-01-01' AND issue_date < '2025-01-01'

“Last 30 days”:

issue_date >= NOW() - INTERVAL '30 days'

Join to items: item.transaction_id = transaction.id.

4) item (line item with AI fields)

Table name: item

Columns

id (bigint, PRIMARY KEY) — line item identifier

transaction_id (bigint, FK → transaction.id) — parent receipt

quantity (double precision) — quantity on the receipt

name (text) — raw product name from the receipt

price (numeric(12,6)) — total line price in EUR

AI-enriched fields

ai_name_without_brand_and_quantity (text) — normalized name (original language)

ai_name_in_english_without_brand_and_quantity (text) — normalized English name

ai_brand (text) — detected brand (e.g., “CCC”, “Bakalář”)

ai_category (text) — category (e.g., “Footwear”, “Beer”)

ai_quantity_value (double precision) — normalized numeric quantity

ai_quantity_unit (text) — normalized quantity unit (e.g., “kg”, “L”, “pcs”)

Notes / usage

Spending questions: sum item.price.

Item count: SUM(item.quantity) or COUNT(*) (context-dependent).

Category/brand analytics: ai_category, ai_brand.

Name search: ai_name_* fields.

5) Typical joins and patterns

You may need to join tables depending on the question.

Base pattern: item + transaction

When you need product-level analytics over time:

FROM item i
JOIN transaction t ON i.transaction_id = t.id


Use t.issue_date for all date/time filters.

Add store (unit)

When the question mentions city, store, or branch:

FROM item i
JOIN transaction t ON i.transaction_id = t.id
JOIN unit u        ON t.unit_id = u.id


Use u.municipality for city filters (e.g., Bratislava).

Use u.name for a specific store.

Add organization

When the question mentions organization/company:

FROM item i
JOIN transaction t ON i.transaction_id = t.id
JOIN organization o ON t.org_id = o.id


Use o.name for organization-level filtering or grouping.

Use o.country / o.municipality for organization geography.

Full join (all four tables)

When you need product + time + store + organization:

FROM item i
JOIN transaction t ON i.transaction_id = t.id
JOIN unit u        ON t.unit_id = u.id
JOIN organization o ON t.org_id = o.id

6) Semantic guidelines

Spending / “How much did I spend” → SUM(i.price) (not quantity).

How many items/products → SUM(i.quantity) or COUNT(*) (context-dependent).

How many times did I shop → COUNT(DISTINCT t.id) (distinct receipts).

Time filters → always on t.issue_date.

Lifetime / “za celý život” → no date filters.

Top-K (categories/brands/stores/cities):

Choose grouping field: i.ai_category / i.ai_brand / u.name / u.municipality

Metric: default SUM(i.price); or COUNT(*) / SUM(i.quantity) if asked

GROUP BY <field> → ORDER BY <metric> DESC → LIMIT K

Existence (“Have I ever bought X?”) → SELECT EXISTS ( … ) AS has_bought

Last N purchases:

Return individual rows (no GROUP BY)

ORDER BY t.issue_date DESC + LIMIT N (literal integer)

Comparisons (one row): conditional aggregation

SELECT
  SUM(i.price) FILTER (WHERE <cond A>) AS a_spent,
  SUM(i.price) FILTER (WHERE <cond B>) AS b_spent
FROM item i
JOIN transaction t ON i.transaction_id = t.id
WHERE <shared filters>;


Placeholders: all dynamic values must use $1, $2, …; LIMIT must be a literal integer.

7) Quick reference: common filters

Year 2024

t.issue_date >= DATE '2024-01-01' AND t.issue_date < DATE '2025-01-01'


Last 30 days

t.issue_date >= NOW() - INTERVAL '30 days'


City filter (Bratislava)

u.municipality ILIKE $1  -- e.g., '%Bratislava%'


Category contains beer

i.ai_category ILIKE $1   -- e.g., 'Beer%'


Brand present

i.ai_brand IS NOT NULL


Use only these tables and relationships. Do not invent new tables or columns.