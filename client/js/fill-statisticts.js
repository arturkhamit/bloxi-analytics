import { expandReceipt } from "./receipts.js";

function createStatRow(containerId, leftText, rightText) {
  const container = document.getElementById(containerId);

  const statGroup = document.createElement("div");
  statGroup.classList.add("stat-group");

  const leftElem = document.createElement("span");
  leftElem.classList.add("stat", "text-semimedium");
  leftElem.textContent = leftText;

  const rightElem = document.createElement("span");
  rightElem.classList.add("stat", "text-semibold");
  rightElem.textContent = rightText;

  statGroup.appendChild(leftElem);
  statGroup.appendChild(rightElem);

  container.appendChild(statGroup);
}

function clearStatistics() {
  document.getElementById("shops-stats").innerHTML = "";
  document.getElementById("products-stats").innerHTML = "";
  document.getElementById("categories-stats").innerHTML = "";
}

function clearReceiptsStats() {
  const receiptsContainer = document.querySelectorAll(".receipt-main");
  receiptsContainer.forEach(element => {
    element.remove();
  });;
}

function drawShopChart(labels, data) {
  const ctx = document.getElementById("shopsChart");

  const existingChart = Chart.getChart(ctx);
  if (existingChart) {
    existingChart.destroy();
  }

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Visits",
          data: data,
          backgroundColor: "rgba(38, 111, 237, 0.7)",
          borderColor: "rgba(54, 162, 235, 1)",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false,
        },
      },
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });
}

function drawProductChart(labels, data) {
  const ctx = document.getElementById("productsChart");

  const existingChart = Chart.getChart(ctx);
  if (existingChart) {
    existingChart.destroy();
  }

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Times",
          data: data,
          backgroundColor: "rgba(38, 111, 237, 0.7)",
          borderColor: "rgba(54, 162, 235, 1)",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false,
        },
      },
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });
}

function drawCategoryChart(labels, data) {
  const ctx = document.getElementById("categoriesChart");

  const existingChart = Chart.getChart(ctx);
  if (existingChart) {
    existingChart.destroy();
  }

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Times",
          data: data,
          backgroundColor: "rgba(38, 111, 237, 0.7)",
          borderColor: "rgba(54, 162, 235, 1)",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false,
        },
      },
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });
}

function fillReceiptsStats(storeName, storeAddress, productInfo, totalPrice) {
  const receiptTemplate = document.querySelector(".receipt-main-template");
  const receiptClone = receiptTemplate.cloneNode(true);
  receiptClone.style = "";
  receiptClone.classList.remove("receipt-main-template");
  receiptClone.classList.add("receipt-main");

  receiptClone.querySelector("#store-name").textContent = storeName;
  receiptClone.querySelector("#store-address").textContent = storeAddress;

  const itemsTableBody = receiptClone.querySelector(
    ".items-table #receipt-items"
  );
  productInfo.forEach((item) => {
    const row = document.createElement("tr");

    const nameCell = document.createElement("td");
    nameCell.textContent = item.name;
    row.appendChild(nameCell);

    const quantityCell = document.createElement("td");
    quantityCell.textContent = parseFloat(item.quantity).toFixed(0);
    row.appendChild(quantityCell);

    const priceCell = document.createElement("td");
    priceCell.textContent = (item.price * item.quantity).toFixed(2);
    row.appendChild(priceCell);

    itemsTableBody.appendChild(row);
  });

  totalPrice = parseFloat(totalPrice).toFixed(2);
  receiptClone.querySelector("#receipt-total").textContent = totalPrice;
  receiptClone.querySelector("#receipt-tax").textContent =
    (totalPrice * 20) / 100;
  receiptClone.querySelector("#receipt-subtotal").textContent =
    totalPrice - (totalPrice * 20) / 100;
  receiptClone.addEventListener("click", () => {
    expandReceipt(receiptClone);
  });

  const receiptsContainer = document.querySelector(".receipts-group-main");
  receiptsContainer.appendChild(receiptClone);
}

function renderStatistics(statsData, receiptsData) {
  clearStatistics();
  clearReceiptsStats();

  if (statsData !== undefined) {
    const org = Object.entries(statsData.organizations);
    const prod = Object.entries(statsData.products);
    const cat = Object.entries(statsData.categories);

    org.forEach(([name, value], index) => {
      createStatRow("shops-stats", `${index + 1}. ${name}`, `${value}x`);
    });

    prod.forEach(([name, value], index) => {
      createStatRow("products-stats", `${index + 1}. ${name}`, `${value}x`);
    });

    cat.forEach(([name, value], index) => {
      createStatRow("categories-stats", `${index + 1}. ${name}`, `${value}x`);
    });
    const shopLabels = org.map(([name, value]) => name);
    const shopValues = org.map(([name, value]) => value);

    drawShopChart(shopLabels, shopValues);

    const productLabels = prod.map(([name, value]) => name);
    const productValues = prod.map(([name, value]) => value);

    drawProductChart(productLabels, productValues);

    const categoryLabels = cat.map(([name, value]) => name);
    const categoryValues = cat.map(([name, value]) => value);

    drawCategoryChart(categoryLabels, categoryValues);
  }

  receiptsData.forEach((receipt) => {
    if (receipt.total_price === undefined) return;
    fillReceiptsStats(
      receipt.organization.organization_name,
      receipt.organization.organization_address ?? "No address",
      receipt.products,
      receipt.total_price
    );
  });
}

export { renderStatistics };
