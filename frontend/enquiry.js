document.addEventListener("DOMContentLoaded", function () {

    const btn = document.getElementById("enquireBtn");
    const popup = document.getElementById("enquiryPopup");
    const close = document.getElementById("closePopup");

    btn.onclick = function () {
        popup.style.display = "flex";
    };

    close.onclick = function () {
        popup.style.display = "none";
    };

    window.onclick = function (e) {
        if (e.target == popup) {
            popup.style.display = "none";
        }
    };

});
