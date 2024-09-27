// Function to handle transcription upload
function uploadTranscription() {
    const fileInput = document.getElementById('transcriptionFile');
    const file = fileInput.files[0];

    if (file) {
        const formData = new FormData();
        formData.append('transcription', file);

        // Send the file to the backend on port 5000
        fetch('http://localhost:5001/upload-transcription', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log('Upload Response:', data);
            if (data.message) {
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
        alert('Please select a file before uploading.');
    }
}

// Function to send a message
function sendMessage() {
    const message = document.getElementById('messageInput').value;
    if (message) {
        const chatBody = document.getElementById('chatBody');
        const newMessage = `
            <div class="message sent">
                <div class="bubble">${message}</div>
                <div class="timestamp">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
            </div>
        `;
        chatBody.insertAdjacentHTML('beforeend', newMessage);
        document.getElementById('messageInput').value = ''; // Clear input field
        chatBody.scrollTop = chatBody.scrollHeight; // Scroll to the bottom

        // Send message to backend for LLM response on port 5000
        fetch('http://localhost:5001/ask-question', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question: message })
        })
        .then(response => response.json())
        .then(data => {
            const responseMessage = `
                <div class="message received">
                    <div class="bubble">${data.response}</div>
                    <div class="timestamp">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                </div>
            `;
            chatBody.insertAdjacentHTML('beforeend', responseMessage);
            chatBody.scrollTop = chatBody.scrollHeight; // Scroll to the bottom
        })
        .catch(error => {
            console.error('Error sending message:', error);
            alert('Failed to get response from the assistant.');
        });
    }
}

// Dummy function to populate previous chats (to be replaced with actual chat history)
function populatePreviousChats() {
    const previousChatsList = document.getElementById('previousChatsList');
    const chatHistory = [
        { name: "Dinesh Bro (Repute)", lastMessage: "Mm okay bro", timestamp: "2:47 pm" },
        { name: "Antony", lastMessage: "Project, skill...", timestamp: "1:57 pm" },
    ];

    chatHistory.forEach(chat => {
        const chatElement = `
            <div class="recent-chat" onclick="openChat('${chat.name}')">
                <img src="https://via.placeholder.com/45" alt="Profile">
                <div class="chat-info">
                    <h5>${chat.name}</h5>
                    <p>${chat.lastMessage}</p>
                </div>
                <span class="chat-timestamp">${chat.timestamp}</span>
            </div>
        `;
        previousChatsList.insertAdjacentHTML('beforeend', chatElement);
    });
}

// Call this function on page load to populate previous chats
window.onload = populatePreviousChats;
