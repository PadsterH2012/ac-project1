
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
            body: JSON.stringify({ 
                message: messageText,
                project_id: currentProjectId  // Assume this variable is set when loading the chat interface
            }),
        });

        console.log('Response status:', response.status);  // Debug log

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        console.log('Received data:', data);  // Debug log

        // Display AI response
        displayMessage('AI Agent Project Planner', data.planner_response, data.planner_name, data.planner_role, data.planner_avatar);
        
        // Update project journal
        updateProjectJournal(data.journal_entry);
        
        // Always update project scope
        updateProjectScope(data.project_scope);

    } catch (error) {
        console.error('Error:', error);
        let errorMessage = 'An error occurred while processing your message.';
        if (error.response && error.response.data && error.response.data.error) {
            errorMessage = error.response.data.error;
        } else if (error.message) {
            errorMessage = error.message;
        }
        displayMessage('System', errorMessage);
        alert(errorMessage); // Add an alert for immediate visibility
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
    const entryHtml = marked.parse(journalEntry);
    projectJournal.innerHTML += `<hr>${entryHtml}`;
    projectJournal.scrollTop = projectJournal.scrollHeight;
}

function updateProjectScope(scope) {
    const projectScope = document.getElementById('projectScope');
    projectScope.innerHTML = scope;
    
    // Check if all questions are answered
    const scopeButton = document.querySelector('.action-button[onclick="performAction(\'Scope\')"]');
    if (scopeButton) {
        if (!scope.includes("Unanswered items:")) {
            scopeButton.classList.add('complete');
        } else {
            scopeButton.classList.remove('complete');
        }
    }
}

// Add event listeners when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    const sendButton = document.querySelector('.message-input button');
    const messageInput = document.getElementById('messageInput');
    const clearJournalBtn = document.getElementById('clearJournalBtn');
    const projectJournal = document.getElementById('projectJournal');

    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }

    if (messageInput) {
        messageInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                sendMessage();
            }
        });
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
