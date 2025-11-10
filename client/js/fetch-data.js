async function fetchData(filter = {}) {
  //192.168.137.224
  const localhost = "http://192.168.2.3:8001";
  if (filter.dateFrom && filter.dateTo) {
    console.log("Fetching data with filter:", filter.dateFrom, filter.dateTo);
    var qr = `/receipts/?start_date=${filter.dateFrom}&end_date=${filter.dateTo}`;
  }
  if (filter.filter) {
    console.log("Fetching data with filter:", filter.filter);
    var qr = `/receipts/last-${filter.filter}`;
  }
  if (filter.query) {
    console.log("Fetching data with query:", filter.query);
    var qr = `/similar_receipts/5?query=${filter.query}`;
  }
  if (filter.default) {
    console.log("Fetching default data");
    var qr = `/receipts/10`;
  }
  const apiUrl = `${localhost}${qr}`;

  try {
    const response = await fetch(apiUrl);
    if (!response.ok) {
      throw new Error("Network response was not ok: " + response.statusText);
    }
    const data = await response.json();
    console.log("Fetched data:", data);
    const stats = data[data.length-1];
    console.log("Extracted stats:", stats);
    
    return data;
  } catch (error) {
    console.error("There has been a problem with your fetch operation:", error);
    throw error;
  }
}

export { fetchData };
