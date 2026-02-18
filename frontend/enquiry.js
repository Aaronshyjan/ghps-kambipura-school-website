document.addEventListener("DOMContentLoaded", function () {

    const btn = document.getElementById("enquireBtn");
    const popup = document.getElementById("enquiryPopup");
    const close = document.getElementById("closePopup");
    const form = document.getElementById("enquiryForm");

    // Open popup
    btn.onclick = function () {
        popup.style.display = "flex";
    };

    // Close popup
    close.onclick = function () {
        popup.style.display = "none";
    };

    window.onclick = function (e) {
        if (e.target == popup) {
            popup.style.display = "none";
        }
    };

    // 🚀 Submit enquiry to Flask backend
    form.addEventListener("submit", async function(e) {
        e.preventDefault();

        const name = document.getElementById("name").value;
        const email = document.getElementById("email").value;
        const message = document.getElementById("message").value;

        try {
            const response = await fetch("https://ghpskambipura.onrender.com", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    name: name,
                    email: email,
                    message: message
                })
            });

            const data = await response.json();

            if (response.ok) {
                alert("Enquiry sent successfully ✅");
                form.reset();
                popup.style.display = "none";
            } else {
                alert("Failed to send enquiry ❌");
            }

        } catch (error) {
            alert("Server not responding ❌");
            console.error(error);
        }
    });

});
