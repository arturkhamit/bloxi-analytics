const cards = document.querySelectorAll('.flip-card');

cards.forEach(card => {
    card.addEventListener('click', () => {
        card.classList.toggle('is-flipped');
    });
});