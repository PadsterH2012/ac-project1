
async function sendMessage() {
    console.log('sendMessage function called');
    console.log('Current project ID:', currentProjectId);
    const messageInput = document.getElementById('messageInput');
    const chatMessages = document.getElementById('chatMessages');
    let messageText = messageInput.value;

    if (messageText.trim() === '') {
        console.log('Message is empty, not sending');
        return;
    }

    console.log('Sending message:', messageText);

    // Display user message
    displayMessage('You', messageText);

    // Clear input
    messageInput.value = '';

    try {
        console.log('Preparing to send POST request');
        console.log('Message:', message);
        console.log('Request body:', JSON.stringify({
            message: message,
            project_id: currentProjectId
        }));
        // Send message to AI agent
        console.log('Sending fetch request to /chat');
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                message: messageText,
                project_id: currentProjectId
            }),
        });

        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Network response was not ok');
        }

        const data = await response.json();
        console.log('Received data:', data);
        console.log('AI response:', data.planner_response);

        // Display AI response
        displayMessage('AI Agent Project Planner', data.planner_response, data.planner_name, data.planner_role, data.planner_avatar);
        
        // Update project journal
        updateProjectJournal(data.journal_entry);

        // Update project scope
        if (data.scope) {
            updateScopeContent(data.scope);
        }

    } catch (error) {
        console.error('Error:', error);
        let errorMessage = 'An error occurred while processing your message.';
        if (error.message) {
            errorMessage = error.message;
        }
        displayMessage('System', errorMessage);
        alert(errorMessage);
    }
}

// Add this new function to handle clearing the journal
async function clearJournal() {
    try {
        const response = await fetch('/clear_journal', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                project_id: currentProjectId
            }),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        if (data.success) {
            const projectJournal = document.getElementById('projectJournal');
            if (projectJournal) {
                projectJournal.innerHTML = '';
                console.log('Journal cleared successfully');
            } else {
                console.error('Project journal element not found');
            }
        } else {
            console.error('Failed to clear journal:', data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while clearing the journal');
    }
}

// Add this to your existing window.onload function or create one if it doesn't exist
window.onload = function() {
    console.log('Chat interface initialized');
    document.getElementById('clearJournalBtn').addEventListener('click', clearJournal);
};

function updateProjectJournal(journalEntry) {
    const projectJournal = document.getElementById('projectJournal');
    const entryElement = document.createElement('p');
    entryElement.textContent = journalEntry;
    projectJournal.appendChild(entryElement);
    projectJournal.scrollTop = projectJournal.scrollHeight;
}

// Add event listeners when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded');
    const sendButton = document.querySelector('.message-input button');
    const messageInput = document.getElementById('messageInput');
    const clearJournalBtn = document.getElementById('clearJournalBtn');
    const projectJournal = document.getElementById('projectJournal');

    if (sendButton) {
        console.log('Send button found, adding event listener');
        sendButton.addEventListener('click', function(event) {
            console.log('Send button clicked');
            sendMessage();
        });
    } else {
        console.error('Send button not found');
    }

    if (messageInput) {
        console.log('Message input found, adding event listener');
        messageInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                console.log('Enter key pressed in message input');
                event.preventDefault();
                sendMessage();
            }
        });
    } else {
        console.error('Message input not found');
    }

    if (clearJournalBtn) {
        clearJournalBtn.addEventListener('click', clearJournal);
    }

    // Load journal entries
    if (projectJournal) {
        const journalEntries = projectJournal.dataset.entries;
        if (journalEntries) {
            const entries = journalEntries.split('\n\n');
            entries.forEach(entry => {
                const entryElement = document.createElement('p');
                entryElement.textContent = entry;
                projectJournal.appendChild(entryElement);
            });
        }
    }
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

async function createProjectScope() {
    try {
        const response = await fetch('/create_scope', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                project_id: currentProjectId
            }),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        if (data.success) {
            updateScopeContent(data.scope);
            console.log('Project scope created successfully');
        } else {
            console.error('Failed to create project scope:', data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while creating the project scope');
    }
}

function updateScopeContent(scope) {
    const scopeContent = document.getElementById('Scope');
    if (scopeContent) {
        scopeContent.innerHTML = `<h3>Project Scope</h3><p>${scope}</p>`;
    } else {
        console.error('Scope content element not found');
    }
}

// Add this to your existing window.onload function or create one if it doesn't exist
window.onload = function() {
    console.log('Chat interface initialized');
    document.getElementById('clearJournalBtn').addEventListener('click', clearJournal);
    document.getElementById('createScopeBtn').addEventListener('click', createProjectScope);
};

// Modify the existing sendMessage function
async function sendMessage() {
    // ... (existing code)

    try {
        // ... (existing code)

        const data = await response.json();
        console.log('Received data:', data);  // Debug log

        // Display AI response
        displayMessage('AI Agent Project Planner', data.planner_response, data.planner_name, data.planner_role, data.planner_avatar);
        
        // Update project journal
        updateProjectJournal(data.journal_entry);

        // Update project scope
        if (data.scope) {
            updateScopeContent(data.scope);
        }

    } catch (error) {
        // ... (existing error handling code)
    }
}

let currentProjectId;

// Initialize the chat
window.onload = function() {
    console.log('Chat interface initialized');
    currentProjectId = document.getElementById('projectId').value;
    console.log('Current project ID:', currentProjectId);
};

function navigateVFS(path) {
    alert(`Navigating to: ${path}`);
}
