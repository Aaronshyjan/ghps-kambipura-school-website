// Open chat
document.getElementById("chat-logo").onclick = function () {
    document.getElementById("chat-container").style.display = "flex";
};

// Close chat
document.getElementById("chat-close").onclick = function () {
    document.getElementById("chat-container").style.display = "none";
};

// Send message on click
document.getElementById("chat-send").onclick = function (e) {
    e.preventDefault();   // prevent form submit
    sendMessage();
};

// Send message on Enter
document.getElementById("chat-input").addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
        e.preventDefault();   // prevent page reload
        sendMessage();
    }
});

// ================= MAIN FUNCTION =================
async function sendMessage() {

    let inputField = document.getElementById("chat-input");
    let message = inputField.value.trim();

    if (message === "") return;

    addUserMessage(message);
    inputField.value = "";

    addTyping();

    try {

        const response = await fetch("https://ghpskambipura.onrender.com/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();

        removeTyping();
        addBotMessage(data.reply);

    } catch (error) {
        removeTyping();
        addBotMessage("⚠️ AI not available right now.");
        console.error(error);
    }
}

// ================= USER MESSAGE =================
function addUserMessage(message) {
    let chat = document.getElementById("chat-messages");
    chat.innerHTML += `<div class="user-message">${message}</div>`;
    chat.scrollTop = chat.scrollHeight;
}

// ================= BOT MESSAGE =================
function addBotMessage(message) {
    let chat = document.getElementById("chat-messages");
    chat.innerHTML += `<div class="bot-message">${message}</div>`;
    chat.scrollTop = chat.scrollHeight;
}

// ================= TYPING =================
function addTyping() {
    let chat = document.getElementById("chat-messages");
    chat.innerHTML += `<div class="bot-message typing">Typing...</div>`;
    chat.scrollTop = chat.scrollHeight;
}

function removeTyping() {
    let typing = document.querySelector(".typing");
    if (typing) typing.remove();
}
