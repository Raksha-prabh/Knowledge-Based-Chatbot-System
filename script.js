// Get DOM elements
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const chatContainer = document.getElementById('chatContainer');

// Event listeners
sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

async function sendMessage() {
    const message = userInput.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    userInput.value = '';
    
    // Disable send button while waiting
    sendBtn.disabled = true;
    
    // Add loading indicator
    const loadingMsg = addMessageToChat('Thinking...', 'bot');
    
    try {
        // Send message to backend
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        // Remove loading message
        if (loadingMsg) loadingMsg.remove();
        
        if (!response.ok) {
            throw new Error(data.message || 'Network response was not ok');
        }
        
        // Add bot response to chat
        const sourceText = data.source ? ` [${data.source.toUpperCase()}]` : '';
        addMessageToChat(data.message + sourceText, 'bot');
        
    } catch (error) {
        console.error('Error:', error);
        if (loadingMsg) loadingMsg.remove();
        addMessageToChat(`Error: ${error.message}`, 'bot');
    } finally {
        sendBtn.disabled = false;
        userInput.focus();
    }
}

function addMessageToChat(message, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    messageDiv.innerHTML = `<p>${escapeHtml(message)}</p>`;
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    return messageDiv;
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Focus input on page load
window.addEventListener('load', () => {
    userInput.focus();
});
