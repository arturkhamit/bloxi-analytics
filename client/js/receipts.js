function expandReceipt(receipt) {
  const modalBackground = document.querySelector('.modal-background');
  const modal = document.querySelector('.modal');

  modal.classList.toggle('expanded');
  modal.innerHTML = receipt.innerHTML;
  modalBackground.classList.toggle('show');
  modalBackground.addEventListener('click', () => {
      modal.classList.remove('expanded');
      modalBackground.classList.remove('show');
      modal.innerHTML = '';
  });
} 

export { expandReceipt };