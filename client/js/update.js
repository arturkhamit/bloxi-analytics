 (function () {
    const addBtn = document.querySelector('.ai-add-btn');
    const uploadModal = document.getElementById('uploadModal');
    if (!uploadModal) return;

    const backdrop = uploadModal.querySelector('.upload-modal__backdrop');
    const closeBtn = document.getElementById('uploadCloseBtn');
    const localBtn = document.getElementById('uploadLocalBtn');
    const fileInput = document.getElementById('uploadInput');

    function openUpload() {
      uploadModal.classList.add('open');
      document.body.classList.add('upload-open');
    }

    function closeUpload() {
      uploadModal.classList.remove('open');
      document.body.classList.remove('upload-open');
    }

    addBtn && addBtn.addEventListener('click', (e) => {
      e.stopPropagation(); // щоб не клікалась кнопка чату
      openUpload();
    });

    backdrop && backdrop.addEventListener('click', closeUpload);
    closeBtn && closeBtn.addEventListener('click', closeUpload);

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        closeUpload();
      }
    });

    localBtn && localBtn.addEventListener('click', () => {
      fileInput && fileInput.click();
    });
  })();