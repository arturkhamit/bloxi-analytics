### Example 1 — Total spent yesterday (calendar day)
**Question:** How much money did I spend yesterday?

```json
{
  "sql": "SELECT COALESCE(SUM(i.price), 0) AS total_spent_in_1_day FROM item i JOIN transaction t ON i.transaction_id = t.id WHERE t.issue_date::date = DATE $1 - INTERVAL '1 day'",
  "explanation": "Total amount spent yesterday (calendar day) by summing i.price, using t.issue_date::date = (DATE $1 - INTERVAL '1 day'); $1 is the anchor date (e.g., CURRENT_DATE).",
  "params": {
    "$1": "specified_date"
  }
}
```

---

### Example 2 — How many carrots did I buy last month?
**Question:** How many carrots did I buy last month?

```json
{
  "sql": "SELECT COALESCE(SUM(i.quantity), 0) AS total_items_in_1_month FROM item i JOIN transaction t ON i.transaction_id = t.id WHERE i.ai_name_in_english_without_brand_and_quantity ILIKE $2 AND t.issue_date >= date_trunc('month', DATE $1 - INTERVAL '1 month') AND t.issue_date < date_trunc('month', DATE $1)",
  "explanation": "Total quantity of items matching $2 bought in the previous calendar month relative to $1, using a month range from date_trunc('month', DATE $1 - INTERVAL '1 month') to before date_trunc('month', DATE $1).",
  "params": {
    "$1": "specified_date",
    "$2": "%carrot%"
  }
}
```

---

### Example 3 — Compare how much money I spent today and last Tuesday on carrots.
**Question:** Compare how much money I spent today and last Tuesday on carrots.

```json
{
  "sql": "SELECT SUM(CASE WHEN t.issue_date::date = DATE $1 THEN i.price END) AS today_spent_on_item, SUM(CASE WHEN t.issue_date::date = date_trunc('week', DATE $1) - INTERVAL '6 days' THEN i.price END) AS last_tuesday_spent_on_item FROM item i JOIN transaction t ON i.transaction_id = t.id WHERE i.ai_name_in_english_without_brand_and_quantity ILIKE $2",
  "explanation": "Compares spending on the item today vs. last Tuesday using conditional sums over i.price, with $1 as the anchor date for 'today' and $2 as the item pattern.",
  "params": {
    "$1": "specified_date",
    "$2": "%carrot%"
  }
}
```

---

### Example 4 — In which shop and when did I last buy sausage?
**Question:** In which shop and when did I last buy sausage?

```json
{
  "sql": "SELECT u.name AS shop_name, t.issue_date FROM item i JOIN transaction t ON i.transaction_id = t.id JOIN unit u ON t.unit_id = u.id WHERE i.ai_name_in_english_without_brand_and_quantity ILIKE $1 ORDER BY t.issue_date DESC LIMIT 1",
  "explanation": "Returns the most recent purchase of the item with the shop (unit) name and timestamp by ordering t.issue_date descending and taking the latest row.",
  "params": {
    "$1": "%sausage%"
  }
}
```

---

### Example 5 — Have I ever bought orange juice?
**Question:** Have I ever bought orange juice?

```json
{
  "sql": "SELECT EXISTS (SELECT 1 FROM item i JOIN transaction t ON i.transaction_id = t.id WHERE i.ai_name_in_english_without_brand_and_quantity ILIKE $1) AS has_bought",
  "explanation": "Boolean check indicating whether any purchase exists for the given item name pattern.",
  "params": {
    "$1": "%orange juice%"
  }
}
```

---

### Example 6 — When did I go to the shop yesterday?
**Question:** When did I go to the shop yesterday?

```json
{
  "sql": "SELECT t.issue_date FROM transaction t WHERE t.issue_date::date = DATE $1 - INTERVAL '1 day' ORDER BY t.issue_date",
  "explanation": "Lists all visit timestamps (receipt times) from yesterday (calendar day) ordered chronologically, using $1 as the anchor date.",
  "params": {
    "$1": "specified_date"
  }
}
```

---

### Example 7 — In which shops did I buy groceries yesterday?
**Question:** In which shops did I buy groceries yesterday?

```json
{
  "sql": "SELECT DISTINCT u.name AS shop_name FROM item i JOIN transaction t ON i.transaction_id = t.id JOIN unit u ON t.unit_id = u.id WHERE t.issue_date::date = DATE $1 - INTERVAL '1 day' AND i.ai_category ILIKE $2",
  "explanation": "Returns the distinct shop (unit) names where items in the given category were purchased yesterday (calendar day), using $1 as the anchor date and $2 as the category pattern.",
  "params": {
    "$1": "specified_date",
    "$2": "Groceries%"
  }
}
```
