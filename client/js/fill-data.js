import { fetchData } from "./fetch-data.js";
import { renderStatistics } from "./fill-statisticts.js";

document.addEventListener("DOMContentLoaded", async () => {
  const statsData = {
    shops: [
      { name: "ATB", value: 550 },
      { name: "Silpo", value: 545 },
      { name: "Kaufland", value: 542 },
      { name: "Lidl", value: 436 },
      { name: "Fresh", value: 433 },
      { name: "Billa", value: 425 },
      { name: "Tesco", value: 324 },
      { name: "Epicentr", value: 313 },
      { name: "Spar", value: 307 },
      { name: "Hornbach", value: 304 },
    ],
    products: [
      { name: "Coca‑Cola", value: 2536 },
      { name: "Nutella ", value: 2021 },
      { name: "Ben & Jerry's Chocolate ", value: 1987 },
      { name: "Heinz Tomato Ketchup ", value: 1789 },
      { name: "Lay's Classic ", value: 1675 },
      { name: "Nescafé Gold ", value: 1450 },
      { name: "Espresso", value: 1320 },
      { name: "Philadelphia ", value: 1250 },
      { name: "Danone Activia ", value: 1150 },
      { name: "Persil Universal Gel 1.", value: 1100 },
    ],
    categories: [
      { name: "Fruits & Vegetables", value: 955 },
      { name: "Dairy & Eggs", value: 876 },
      { name: "Bakery & Bread", value: 845 },
      { name: "Meat & Seafood", value: 789 },
      { name: "Frozen Foods", value: 756 },
      { name: "Beverages", value: 700 },
      { name: "Snacks & Confectionery", value: 650 },
      { name: "Household & Cleaning", value: 600 },
      { name: "Personal Care & Hygiene", value: 550 },
      { name: "Baby & Childcare", value: 500 },
    ],
  };

  const receiptsData = [
    {
      organization: {
        organization_name: "Lidl",
        organization_address: "123 Main St, City",
      },
      items: [
        { item_name: "Apples", item_quantity: 2, item_price: 3.5 },
        { item_name: "Bread", item_quantity: 1, item_price: 2.0 },
        { item_name: "Milk", item_quantity: 3, item_price: 1.5 },
      ],
      total_price: 12.0,
    },
    {
      organization: {
        organization_name: "Kaufland",
        organization_address: "456 Market St, City",
      },
      items: [
        { item_name: "Bananas", item_quantity: 5, item_price: 1.2 },
        { item_name: "Eggs", item_quantity: 1, item_price: 2.5 },
        { item_name: "Cheese", item_quantity: 2, item_price: 4.0 },
      ],
      total_price: 17.5,
    },
    {
      organization: {
        organization_name: "Billa",
        organization_address: "789 Broadway Ave, City",
      },
      items: [
        { item_name: "Chicken", item_quantity: 1, item_price: 7.5 },
        { item_name: "Rice", item_quantity: 2, item_price: 3.0 },
        { item_name: "Vegetables", item_quantity: 4, item_price: 2.5 },
      ],
      total_price: 26.5,
    },
    {
      organization: {
        organization_name: "Tesco",
        organization_address: "101 Center Rd, City",
      },
      items: [
        { item_name: "Fish", item_quantity: 2, item_price: 6.0 },
        { item_name: "Pasta", item_quantity: 3, item_price: 2.0 },
        { item_name: "Sauce", item_quantity: 1, item_price: 3.5 },
      ],
      total_price: 27.5,
    },
    {
      organization: {
        organization_name: "Fresh",
        organization_address: "202 Green St, City",
      },
      items: [
        { item_name: "Yogurt", item_quantity: 4, item_price: 1.0 },
        { item_name: "Granola", item_quantity: 1, item_price: 4.5 },
        { item_name: "Fruit Juice", item_quantity: 2, item_price: 3.0 },
        { item_name: "Yogurt", item_quantity: 4, item_price: 1.0 },
        { item_name: "Granola", item_quantity: 1, item_price: 4.5 },
        { item_name: "Fruit Juice", item_quantity: 2, item_price: 3.0 },
        { item_name: "Yogurt", item_quantity: 4, item_price: 1.0 },
        { item_name: "Granola", item_quantity: 1, item_price: 4.5 },
        { item_name: "Fruit Juice", item_quantity: 2, item_price: 3.0 },
      ],
      total_price: 34.5,
    },
    {
      organization: {
        organization_name: "Fresh",
        organization_address: "202 Green St, City",
      },
      items: [
        { item_name: "Yogurt", item_quantity: 4, item_price: 1.0 },
        { item_name: "Granola", item_quantity: 1, item_price: 4.5 },
        { item_name: "Fruit Juice", item_quantity: 2, item_price: 3.0 },
        { item_name: "Yogurt", item_quantity: 4, item_price: 1.0 },
        { item_name: "Granola", item_quantity: 1, item_price: 4.5 },
        { item_name: "Fruit Juice", item_quantity: 2, item_price: 3.0 },
        { item_name: "Yogurt", item_quantity: 4, item_price: 1.0 },
        { item_name: "Granola", item_quantity: 1, item_price: 4.5 },
        { item_name: "Fruit Juice", item_quantity: 2, item_price: 3.0 },
      ],
      total_price: 34.5,
    },
        {
      organization: {
        organization_name: "Fresh",
        organization_address: "202 Green St, City",
      },
      items: [
        { item_name: "Yogurt", item_quantity: 4, item_price: 1.0 },
        { item_name: "Granola", item_quantity: 1, item_price: 4.5 },
        { item_name: "Fruit Juice", item_quantity: 2, item_price: 3.0 },
        { item_name: "Yogurt", item_quantity: 4, item_price: 1.0 },
        { item_name: "Granola", item_quantity: 1, item_price: 4.5 },
        { item_name: "Fruit Juice", item_quantity: 2, item_price: 3.0 },
        { item_name: "Yogurt", item_quantity: 4, item_price: 1.0 },
        { item_name: "Granola", item_quantity: 1, item_price: 4.5 },
        { item_name: "Fruit Juice", item_quantity: 2, item_price: 3.0 },
      ],
      total_price: 34.5,
    },
        {
      organization: {
        organization_name: "Fresh",
        organization_address: "202 Green St, City",
      },
      items: [
        { item_name: "Yogurt", item_quantity: 4, item_price: 1.0 },
        { item_name: "Granola", item_quantity: 1, item_price: 4.5 },
        { item_name: "Fruit Juice", item_quantity: 2, item_price: 3.0 },
        { item_name: "Yogurt", item_quantity: 4, item_price: 1.0 },
        { item_name: "Granola", item_quantity: 1, item_price: 4.5 },
        { item_name: "Fruit Juice", item_quantity: 2, item_price: 3.0 },
        { item_name: "Yogurt", item_quantity: 4, item_price: 1.0 },
        { item_name: "Granola", item_quantity: 1, item_price: 4.5 },
        { item_name: "Fruit Juice", item_quantity: 2, item_price: 3.0 },
      ],
      total_price: 34.5,
    }
  ];

  const data = await fetchData({ filter: "month" });
  const stats = data[data.length-1];

  console.log("Using fetched data:");
  console.log(stats);
  

  renderStatistics(stats, data);

  // const data = fetchData({ default: true});
});
