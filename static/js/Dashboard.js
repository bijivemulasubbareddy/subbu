const container = document.querySelector(".container");
const nav = document.querySelector(".sidebar");
const main = document.querySelector(".main__content");

container.addEventListener("click", (e) => {
    const toggleBtn = document.querySelector(".nav__toggle--input");
    if (e.target.closest(".sidebar") || e.target.contains(toggleBtn)) {
        return;
    }
    toggleBtn.checked = false;
});