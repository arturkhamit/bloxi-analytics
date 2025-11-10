import { fetchData } from "./fetch-data.js";
import { renderStatistics } from "./fill-statisticts.js";

document.addEventListener("DOMContentLoaded", () => {
  const filterTrigger = document.querySelector(".filter-static");
  const filterCalendar = document.querySelector(".filter-calendar");
  const dropdownMenu = document.querySelector(".dropdown-menu");
  const dropdownItems = dropdownMenu.querySelectorAll(".dropdown-item");

  dropdownItems.forEach((item) => {
    item.addEventListener("click", async () => {
      const data = await fetchData({
        filter: item.getAttribute("filter-data"),
      });
      const stats = data[data.length-1];
      
      renderStatistics(stats, data);
      dropdownMenu.classList.remove("show");
    });
  });

  filterTrigger.addEventListener("click", (event) => {
    event.stopPropagation();
    dropdownMenu.classList.toggle("show");
  });

  window.addEventListener("click", (event) => {
    if (dropdownMenu.classList.contains("show")) {
      if (!dropdownMenu.contains(event.target)) {
        dropdownMenu.classList.remove("show");
      }
    }
  });

  filterCalendar.addEventListener("click", (event) => {
    if (dropdownMenu.classList.contains("show")) {
      if (!dropdownMenu.contains(event.target)) {
        dropdownMenu.classList.remove("show");
      }
    }
  });
});
