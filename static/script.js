document.addEventListener("DOMContentLoaded", () => {
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const chatBox = document.getElementById("chat-box");

    // Function to append messages to the chat UI
    function appendMessage(text, sender) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", `${sender}-message`);
        messageDiv.textContent = text;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to bottom
    }

    // Function to send message to Flask backend
    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        // Display user message instantly
        appendMessage(message, "user");
        userInput.value = "";

        // Display a temporary loading placeholder
        const loadingDiv = document.createElement("div");
        loadingDiv.classList.add("message", "bot-message", "loading");
        loadingDiv.textContent = "...";
        chatBox.appendChild(loadingDiv);

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();
            
            // Remove loading placeholder
            chatBox.removeChild(loadingDiv);

            if (response.ok) {
                appendMessage(data.reply, "bot");
            } else {
                appendMessage(`Error: ${data.reply}`, "bot");
            }
        } catch (error) {
            chatBox.removeChild(loadingDiv);
            appendMessage("Failed to connect to the server.", "bot");
            console.error("Error:", error);
        }
    }

    // Event listeners for button click and 'Enter' key press
    sendBtn.addEventListener("click", sendMessage);
    userInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });
});