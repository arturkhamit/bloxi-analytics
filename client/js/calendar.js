import { fetchData } from "./fetch-data.js";
import { renderStatistics } from "./fill-statisticts.js";

document.addEventListener("DOMContentLoaded", () => {
  const dateInput = document.getElementById("datepicker-input");
  const calendarTrigger = document.getElementById("calendar-trigger");

  const picker = new Litepicker({
    element: dateInput,
    singleMode: false,
    autoApply: false,
    format: "YYYY.MM.DD",

    dropdowns: {
      months: true,
      years: true,
      maxYear: 2024,
    },

    parentEl: ".filter-group",
  });

  calendarTrigger.addEventListener("click", (event) => {
    event.stopPropagation();
    picker.show();
  });

  picker.on("selected", async (date1, date2) => {
    console.log("Selected dates:");
    console.log(
      "From:",
      date1.format("YYYY.MM.DD"),
      "To:",
      date2.format("YYYY.MM.DD")
    );
    const data = await fetchData({
      dateFrom: date1.format("YYYY-MM-DD"),
      dateTo: date2.format("YYYY-MM-DD"),
    });

    const stats = data[data.length-1];

    // wtf why twice 
    renderStatistics(stats, data);
  });
});
