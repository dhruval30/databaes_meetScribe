// Function to handle CSV upload and create a new chat session
function uploadTranscription() {
    const fileInput = document.getElementById('transcriptionFile');
    const file = fileInput.files[0];

    // Check if the selected file is a CSV
    if (file && file.name.endsWith('.csv')) {
        const formData = new FormData();
        formData.append('transcription', file);

        // Send the CSV file to the backend
        fetch(`http://localhost:5001/upload-transcription?session_id=${Date.now()}`, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log('Upload Response:', data);
            if (data.message) {
                const fileName = file.name.split('.').slice(0, -1).join('.'); // Get file name without extension
                startNewChat(fileName);  // Start a new chat session with the file name
                alert(data.message); // Show success message
            } else if (data.error) {
                alert('Error: ' + data.error); // Show error message if present
            }
        })
        .catch(error => {
            console.error('Error uploading file:', error);
            alert('Failed to upload transcription.');
        });
    } else {
        alert('Please select a valid CSV file.');
    }
}

// Ensure file input accepts only CSV files
document.getElementById('transcriptionFile').setAttribute('accept', '.csv');


// Function to initialize a new chat session
function startNewChat(sessionName) {
    const chatSessionId = Date.now();  // Use timestamp as a unique session ID
    const chatSessionName = sessionName || `Chat ${chatSessionId}`;  // Use provided name or default

    let chatSessions = JSON.parse(localStorage.getItem('chatSessions')) || {};

    if (!chatSessions[chatSessionId]) {
        chatSessions[chatSessionId] = {
            sessionName: chatSessionName,
            messages: []  // Initialize with no messages
        };
    }

    localStorage.setItem('chatSessions', JSON.stringify(chatSessions));  // Store updated sessions
    localStorage.setItem('currentChatSession', chatSessionId);  // Set current session in localStorage

    clearChatWindow();  // Clear the chat window for the new session
    loadCurrentChat();  // Load current chat after clearing (without moving it to history)
    updateChatSessions();  // Refresh the chat session list
}

// Function to send a message
function sendMessage() {
    const message = document.getElementById('messageInput').value;
    const currentChatSession = localStorage.getItem('currentChatSession');

    if (message && currentChatSession) {
        const chatBody = document.getElementById('chatBody');
        const newMessage = `
            <div class="message sent">
                <div class="bubble">${message}</div>
                <div class="timestamp">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
            </div>
        `;
        chatBody.insertAdjacentHTML('beforeend', newMessage);
        document.getElementById('messageInput').value = '';  // Clear input field
        chatBody.scrollTop = chatBody.scrollHeight;  // Scroll to the bottom

        // Send message to backend
        fetch('http://localhost:5001/ask-question', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question: message, session_id: currentChatSession })
        })
        .then(response => response.json())
        .then(data => {
            displayResponse(data);  // Use the new displayResponse function to handle markdown
            saveChatMessage(currentChatSession, message, data.response);  // Save messages in the session
        })
        .catch(error => {
            console.error('Error sending message:', error);
            alert('Failed to get response from the assistant.');
        });
    }
}

// Function to process and display the response with markdown formatting
function displayResponse(responseData) {
    const chatBody = document.getElementById('chatBody');

    // Convert markdown to HTML using marked.js
    const formattedResponse = marked.parse(responseData.response); // Convert markdown to HTML

    const responseMessage = `
        <div class="message received">
            <div class="bubble">${formattedResponse}</div>
            <div class="timestamp">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
        </div>
    `;

    chatBody.insertAdjacentHTML('beforeend', responseMessage);
    chatBody.scrollTop = chatBody.scrollHeight;  // Scroll to the bottom
}

// Function to save chat messages to localStorage
function saveChatMessage(sessionId, userMessage, botResponse) {
    let chatSessions = JSON.parse(localStorage.getItem('chatSessions')) || {};

    if (!chatSessions[sessionId]) {
        chatSessions[sessionId] = {
            sessionName: `Chat ${sessionId}`,
            messages: []  // Initialize an empty messages array if not already present
        };
    }

    chatSessions[sessionId].messages.push({
        userMessage,
        botResponse,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    });

    localStorage.setItem('chatSessions', JSON.stringify(chatSessions));
}

// Function to load current chat and display messages without clearing
function loadCurrentChat() {
    const currentChatSession = localStorage.getItem('currentChatSession');
    const chatSessions = JSON.parse(localStorage.getItem('chatSessions')) || {};
    const chatBody = document.getElementById('chatBody');

    if (!chatSessions[currentChatSession]) {
        alert('Chat session not found.');
        return;
    }

    chatBody.innerHTML = '';  // Clear the chat body

    // Populate the chat window with the messages from the current session
    chatSessions[currentChatSession].messages.forEach(chat => {
        const userMessage = `
            <div class="message sent">
                <div class="bubble">${chat.userMessage}</div>
                <div class="timestamp">${chat.timestamp}</div>
            </div>
        `;
        const botResponse = `
            <div class="message received">
                <div class="bubble">${marked.parse(chat.botResponse)}</div>
                <div class="timestamp">${chat.timestamp}</div>
            </div>
        `;
        chatBody.insertAdjacentHTML('beforeend', userMessage + botResponse);
    });

    chatBody.scrollTop = chatBody.scrollHeight;  // Scroll to the bottom
}

// Function to clear chat window
function clearChatWindow() {
    const chatBody = document.getElementById('chatBody');
    chatBody.innerHTML = '';  // Clear all messages in the chat body
}

// Function to populate previous chats (history)
function populatePreviousChats() {
    const previousChatsList = document.getElementById('previousChatsList');
    previousChatsList.innerHTML = '';  // Clear current list
    const chatSessions = JSON.parse(localStorage.getItem('chatSessions')) || {};

    Object.keys(chatSessions).forEach(sessionId => {
        const lastChat = (chatSessions[sessionId].messages || []).slice(-1)[0] || { userMessage: '', timestamp: '' };  // Handle empty session
        const chatSessionName = chatSessions[sessionId].sessionName || `Chat ${sessionId}`;

        const chatElement = `
            <div class="recent-chat" onclick="openChat('${sessionId}')">
                <div class="chat-info">
                    <h5>${chatSessionName}</h5>
                    <p>${lastChat.userMessage.substring(0, 30) || 'No messages yet'}...</p>
                </div>
                <span class="chat-timestamp">${lastChat.timestamp || ''}</span>
            </div>
        `;
        previousChatsList.insertAdjacentHTML('beforeend', chatElement);
    });
}

// Function to open a previous chat session
function openChat(sessionId) {
    const chatSessions = JSON.parse(localStorage.getItem('chatSessions')) || {};
    const chatBody = document.getElementById('chatBody');

    if (!chatSessions[sessionId]) {
        alert('Chat session not found.');
        return;
    }

    localStorage.setItem('currentChatSession', sessionId);  // Set the clicked session as the current one
    chatBody.innerHTML = '';  // Clear the chat body

    // Populate the chat window with the messages from the selected session
    chatSessions[sessionId].messages.forEach(chat => {
        const userMessage = `
            <div class="message sent">
                <div class="bubble">${chat.userMessage}</div>
                <div class="timestamp">${chat.timestamp}</div>
            </div>
        `;
        const botResponse = `
            <div class="message received">
                <div class="bubble">${marked.parse(chat.botResponse)}</div>
                <div class="timestamp">${chat.timestamp}</div>
            </div>
        `;
        chatBody.insertAdjacentHTML('beforeend', userMessage + botResponse);
    });

    chatBody.scrollTop = chatBody.scrollHeight;  // Scroll to the bottom
}

// Function to update chat session list
function updateChatSessions() {
    populatePreviousChats();
}

// Call this function on page load to populate previous chats
window.onload = () => {
    populatePreviousChats();

    // Check if there's an active chat session, if not, start a new chat session
    if (!localStorage.getItem('currentChatSession')) {
        startNewChat();
    } else {
        loadCurrentChat();  // Load the current chat session if available
    }
};

// Function to clear all chat history
function clearChatHistory() {
    const confirmClear = confirm("Are you sure you want to clear all chat history?");
    
    if (confirmClear) {
        localStorage.removeItem('chatSessions');
        localStorage.removeItem('currentChatSession');
        
        clearChatWindow();
        populatePreviousChats();

        alert("Chat history cleared.");
    }
}

// Function to handle predefined prompt clicks
function sendPrompt(promptText) {
    const currentChatSession = localStorage.getItem('currentChatSession');

    if (currentChatSession) {
        const chatBody = document.getElementById('chatBody');
        const newMessage = `
            <div class="message sent">
                <div class="bubble">${promptText}</div>
                <div class="timestamp">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
            </div>
        `;
        chatBody.insertAdjacentHTML('beforeend', newMessage);
        chatBody.scrollTop = chatBody.scrollHeight;  // Scroll to the bottom

        // Send the predefined prompt to backend
        fetch('http://localhost:5001/ask-question', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question: promptText, session_id: currentChatSession })
        })
        .then(response => response.json())
        .then(data => {
            // Convert markdown response to HTML using marked.js
            const formattedResponse = marked.parse(data.response);

            const responseMessage = `
                <div class="message received">
                    <div class="bubble">${formattedResponse}</div>
                    <div class="timestamp">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                </div>
            `;
            chatBody.insertAdjacentHTML('beforeend', responseMessage);
            chatBody.scrollTop = chatBody.scrollHeight;

            saveChatMessage(currentChatSession, promptText, data.response);  // Save messages in the session
        })
        .catch(error => {
            console.error('Error sending prompt:', error);
            alert('Failed to get response from the assistant.');
        });
    }
}

