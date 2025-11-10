const outerContainer = document.querySelector(".logos-container");
const container = document.querySelector(".logos-group");

for (let i = 0; i < 4; i++) {
  let clone = container.cloneNode(true);
  clone.ariaHidden = "true";
  outerContainer.appendChild(clone);
}

const receiptOuterContainer = document.querySelector(".receipts-container");
const receiptContainer = document.querySelector(".receipts-group");

for (let i = 0; i < 3; i++) {
  let clone = receiptContainer.cloneNode(true);
  clone.ariaHidden = "true";
  receiptOuterContainer.appendChild(clone);
}

function test() {
  console.log("test");
}