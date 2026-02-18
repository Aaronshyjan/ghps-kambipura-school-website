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

    // 🔥 Handle Form Submit
    form.addEventListener("submit", async function (e) {

        e.preventDefault();   // stop page reload

        const parent_name = document.getElementById("parent_name").value;
        const student_name = document.getElementById("student_name").value;
        const phone = document.getElementById("phone").value;
        const class_interest = document.getElementById("class_interest").value;
        const message = document.getElementById("message").value;

        try {

            const response = await fetch("https://ghpskambipura.onrender.com/submit-enquiry", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    parent_name,
                    student_name,
                    phone,
                    class_interest,
                    message
                })
            });

            const data = await response.json();

            if (data.status === "success") {
                alert("Enquiry submitted successfully ✅");
                form.reset();
                popup.style.display = "none";
            } else {
                alert("Submission failed ❌");
            }

        } catch (err) {
            alert("Server not responding ❌");
            console.error(err);
        }

    });

});
