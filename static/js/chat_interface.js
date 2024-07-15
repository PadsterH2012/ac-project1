
async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const chatMessages = document.getElementById('chatMessages');
    let messageText = messageInput.value;

    if (messageText.trim() === '') {
        return;
    }

    console.log('Sending message:', messageText);  // Debug log

    // Display user message
    displayMessage('You', messageText);

    // Clear input
    messageInput.value = '';

    try {
        // Send message to AI agent
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: messageText }),
        });

        console.log('Response status:', response.status);  // Debug log

        if (response.status === 202) {
            const data = await response.json();
            displayMessage('System', data.response);
            setTimeout(() => sendMessage(), 5000); // Retry after 5 seconds
        } else if (!response.ok) {
            throw new Error('Network response was not ok');
        } else {
            const data = await response.json();
            console.log('Received data:', data);  // Debug log
            // Display AI response
            displayMessage('AI Agent', data.response, data.agent_name, data.agent_role, data.agent_avatar);
            
            // Update project journal
            updateProjectJournal(data.journal_entry);
        }

        // User message is already displayed before the API call
    } catch (error) {
        console.error('Error:', error);
        displayMessage('System', 'An error occurred while processing your message.');
    }
}

function updateProjectJournal(journalEntry) {
    const projectJournal = document.getElementById('projectJournal');
    const entryElement = document.createElement('p');
    entryElement.textContent = journalEntry;
    projectJournal.appendChild(entryElement);
    projectJournal.scrollTop = projectJournal.scrollHeight;
}

// Add event listener for the send button
document.addEventListener('DOMContentLoaded', function() {
    const sendButton = document.querySelector('.message-input button');
    sendButton.addEventListener('click', sendMessage);

    // Add event listener for the Enter key in the input field
    const messageInput = document.getElementById('messageInput');
    messageInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            sendMessage();
        }
    });
});

function displayMessage(sender, text, agentName = '', agentRole = '', agentAvatar = '') {
    console.log('Displaying message:', { sender, text, agentName, agentRole, agentAvatar });  // Debug log

    const chatMessages = document.getElementById('chatMessages');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender === 'You' ? 'user' : 'other');

    const avatarElement = document.createElement('img');
    if (sender === 'You') {
        avatarElement.src = 'https://websim.ai/avatar4.jpg';
    } else if (agentAvatar) {
        avatarElement.src = agentAvatar;
    } else {
        avatarElement.src = '/static/avatars/default_agent.jpg';
    }
    avatarElement.onerror = function() {
        this.src = '/static/avatars/default_agent.jpg';
    };
    avatarElement.alt = sender;
    avatarElement.classList.add('avatar');

    const bubbleElement = document.createElement('div');
    bubbleElement.classList.add('bubble');
    
    const senderNameElement = document.createElement('span');
    senderNameElement.classList.add('sender-name');
    senderNameElement.textContent = sender === 'You' ? sender : `${agentName} - ${agentRole}`;

    const messageTextElement = document.createElement('p');
    messageTextElement.textContent = text;

    const timestampElement = document.createElement('span');
    timestampElement.classList.add('timestamp');
    timestampElement.textContent = new Date().toLocaleTimeString();

    bubbleElement.appendChild(senderNameElement);
    bubbleElement.appendChild(messageTextElement);
    bubbleElement.appendChild(timestampElement);

    messageElement.appendChild(avatarElement);
    messageElement.appendChild(bubbleElement);
    chatMessages.appendChild(messageElement);

    chatMessages.scrollTop = chatMessages.scrollHeight;

    console.log('Message displayed');  // Debug log
}

function openTab(event, tabName) {
    const tabContents = document.getElementsByClassName('tab-content');
    for (let i = 0; i < tabContents.length; i++) {
        tabContents[i].style.display = 'none';
    }

    const tabs = document.getElementsByClassName('tab');
    for (let i = 0; i < tabs.length; i++) {
        tabs[i].classList.remove('active');
    }

    document.getElementById(tabName).style.display = 'block';
    event.currentTarget.classList.add('active');
}

function performAction(action) {
    if (action === 'Download') {
        console.log('Initiating backup process...');
        // Trigger the backup process
        fetch('/backup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                backup_projects: true,
                backup_agents: true,
                backup_providers: true
            })
        })
        .then(response => {
            console.log('Response received:', response);
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(`HTTP error! status: ${response.status}, message: ${errorData.error || 'Unknown error'}`);
                });
            }
            return response.blob();
        })
        .then(blob => {
            console.log('Blob received:', blob);
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            // Get the filename from the Content-Disposition header if available
            const filename = response.headers.get('Content-Disposition')
                ? response.headers.get('Content-Disposition').split('filename=')[1].replace(/"/g, '')
                : 'backup.json';
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            console.log('Download initiated');
        })
        .catch((error) => {
            console.error('Error:', error);
            alert(`An error occurred while creating the backup: ${error.message}`);
        });
    } else {
        alert(`Performing action: ${action}`);
    }
}

function navigateVFS(path) {
    alert(`Navigating to: ${path}`);
}

// Initialize the chat
window.onload = function() {
    console.log('Chat interface initialized');
};

function navigateVFS(path) {
    alert(`Navigating to: ${path}`);
}
