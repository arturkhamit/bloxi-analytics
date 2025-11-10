const langButtons = document.querySelectorAll(".lang-btn");
langButtons.forEach(button => {
    button.addEventListener("click", () => {
        langButtons.forEach(btn => btn.classList.remove("active"));
        button.classList.add("active");
    });
});