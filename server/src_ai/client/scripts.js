// // script.js

// const container = document.querySelector(".logos-container");
// const speed = 0.5; // Швидкість прокрутки в пікселях за кадр

// function scrollAnimation() {
//   let currentX = parseFloat(
//     container.style.transform.replace("translateX(", "").replace("px)", "") || 0
//   );

//   currentX -= speed;

//   container.style.transform = `translateX(${currentX}px)`;

//   const totalWidth = container.scrollWidth;
//   const halfWidth = totalWidth / 2;

//   if (Math.abs(currentX) >= halfWidth) {
//     container.style.transform = `translateX(0)`;
//   }

//   requestAnimationFrame(scrollAnimation);
// }

// scrollAnimation();

const container = document.querySelector(".logos-container");
let logos = document.querySelectorAll(".logos-container img");

for (let i = 0; i < 10; i++) {
  for (let i = 0; i < logos.length; i++) {
    let clone = logos[i].cloneNode(true);
    container.appendChild(clone);
  }
}

const receiptContainer = document.querySelector(".receipts-container");
let receipts = document.querySelectorAll(".receipts-container .receipt");

for (let i = 0; i < 51; i++) {
  for (let i = 0; i < receipts.length; i++) {
    let clone = receipts[i].cloneNode(true);
    receiptContainer.appendChild(clone);
  }
}
