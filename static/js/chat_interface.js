
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
    projectScope.innerHTML = marked.parse(scope);
    
    updateButtonColors(scope);
}

function updateButtonColors(scope, hld, lld_db, lld_ux, lld_code) {
    const scopeButton = document.querySelector('.action-button[onclick="performAction(\'Scope\')"]');
    const hldButton = document.querySelector('.action-button[onclick="performAction(\'HLD\')"]');
    const lldDbButton = document.querySelector('.action-button[onclick="performAction(\'LLD-DB\')"]');
    const lldUxButton = document.querySelector('.action-button[onclick="performAction(\'LLD-UX\')"]');
    const lldCodeButton = document.querySelector('.action-button[onclick="performAction(\'LLD-Code\')"]');

    if (scopeButton && !scope.includes("Unanswered items:")) {
        scopeButton.classList.add('complete');
        hldButton.classList.add('amber');
    } else if (scopeButton) {
        scopeButton.classList.remove('complete');
        hldButton.classList.remove('amber');
    }

    if (hldButton && hld) {
        hldButton.classList.add('complete');
        lldDbButton.classList.add('amber');
        lldUxButton.classList.add('amber');
        lldCodeButton.classList.add('amber');
    }

    if (lldDbButton && lld_db) lldDbButton.classList.add('complete');
    if (lldUxButton && lld_ux) lldUxButton.classList.add('complete');
    if (lldCodeButton && lld_code) lldCodeButton.classList.add('complete');
}

function updateButtonColors(scope, hld, lld_db, lld_ux, lld_code) {
    const scopeButton = document.querySelector('.action-button[onclick="performAction(\'Scope\')"]');
    const hldButton = document.querySelector('.action-button[onclick="performAction(\'HLD\')"]');
    const lldDbButton = document.querySelector('.action-button[onclick="performAction(\'LLD-DB\')"]');
    const lldUxButton = document.querySelector('.action-button[onclick="performAction(\'LLD-UX\')"]');
    const lldCodeButton = document.querySelector('.action-button[onclick="performAction(\'LLD-Code\')"]');

    if (scopeButton && !scope.includes("Unanswered items:")) {
        scopeButton.classList.add('complete');
        hldButton.classList.add('amber');
    } else if (scopeButton) {
        scopeButton.classList.remove('complete');
        hldButton.classList.remove('amber');
    }

    if (hldButton && hld) {
        hldButton.classList.add('complete');
        lldDbButton.classList.add('amber');
        lldUxButton.classList.add('amber');
        lldCodeButton.classList.add('amber');
    }

    if (lldDbButton && lld_db) lldDbButton.classList.add('complete');
    if (lldUxButton && lld_ux) lldUxButton.classList.add('complete');
    if (lldCodeButton && lld_code) lldCodeButton.classList.add('complete');
}

function renderMarkdownContent(elementId, content) {
    const element = document.getElementById(elementId);
    if (element) {
        if (content && content.trim() !== '') {
            try {
                element.innerHTML = marked.parse(content);
            } catch (error) {
                console.error('Error parsing markdown:', error);
                element.innerHTML = '<p>Error rendering content. Please try again.</p>';
            }
        } else {
            element.innerHTML = '<p>No content available yet.</p>';
        }
    } else {
        console.error(`Element with id '${elementId}' not found`);
    }
}

// Add this to your existing window.onload function or create one if it doesn't exist
window.onload = function() {
    console.log('Chat interface initialized');
    document.getElementById('clearJournalBtn').addEventListener('click', clearJournal);
    
    // Get initial content for all tabs
    const initialScope = document.getElementById('projectScope').innerHTML;
    const initialHld = document.getElementById('hldContent').dataset.content;
    const initialLldDb = document.getElementById('lldDbContent').innerHTML;
    const initialLldUx = document.getElementById('lldUxContent').innerHTML;
    const initialLldCode = document.getElementById('lldCodeContent').innerHTML;

    // Update button colors based on initial content
    updateButtonColors(initialScope, initialHld, initialLldDb, initialLldUx, initialLldCode);

    // Render initial content for all tabs
    const projectScopeContent = document.getElementById('projectScope').dataset.content;
    console.log('Project Scope content:', projectScopeContent); // Debug log
    renderMarkdownContent('projectScope', projectScopeContent);
    
    // Render HLD content
    const hldContent = document.getElementById('hldContent').dataset.content;
    console.log('HLD content:', hldContent); // Debug log
    renderMarkdownContent('hldContent', hldContent);

    // Ensure project scope is visible
    const scopeTab = document.getElementById('Scope');
    if (scopeTab) {
        scopeTab.style.display = 'block';
    }

    // Ensure HLD tab is properly initialized
    const hldTab = document.getElementById('HLD');
    if (hldTab) {
        hldTab.style.display = 'none'; // Initially hide the HLD tab
    }
    renderMarkdownContent('lldDbContent', initialLldDb);
    renderMarkdownContent('lldUxContent', initialLldUx);
    renderMarkdownContent('lldCodeContent', initialLldCode);
    renderMarkdownContent('codingPlanContent', document.getElementById('codingPlanContent').innerHTML);
    renderMarkdownContent('vfsContent', document.getElementById('vfsContent').innerHTML);

    // Ensure HLD content is rendered
    const hldContent = document.getElementById('hldContent').dataset.content;
    console.log('HLD content:', hldContent); // Debug log
    renderMarkdownContent('hldContent', hldContent);
};

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
        // ... (existing download code)
    } else if (action === 'HLD' || action.startsWith('LLD-') || action === 'Plan') {
        const button = document.querySelector(`.action-button[onclick="performAction('${action}')"]`);
        if (button && (button.classList.contains('amber') || action === 'Plan')) {
            console.log(`Initiating ${action} creation process...`);
            const endpoint = action === 'Plan' ? '/create_coding_plan' : `/create_${action.toLowerCase()}`;
            fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    project_id: currentProjectId
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(`${action} created successfully!`);
                    // Update the content in the UI
                    const contentElement = action === 'Plan' ? document.getElementById('codingPlanContent') : document.getElementById(`${action.toLowerCase()}Content`);
                    if (contentElement) {
                        contentElement.innerHTML = marked.parse(data[action.toLowerCase()]);
                    }
                    // Change the button color to green
                    button.classList.remove('amber');
                    button.classList.add('complete');
                    // If HLD was created, make LLD buttons amber
                    if (action === 'HLD') {
                        document.querySelectorAll('.action-button[onclick^="performAction(\'LLD-"]').forEach(btn => {
                            btn.classList.add('amber');
                        });
                    }
                    // If all LLDs are complete, make Plan button amber
                    if (action.startsWith('LLD-')) {
                        const allLLDsComplete = ['LLD-DB', 'LLD-UX', 'LLD-Code'].every(lld => 
                            document.querySelector(`.action-button[onclick="performAction('${lld}')"]`).classList.contains('complete')
                        );
                        if (allLLDsComplete) {
                            document.querySelector('.action-button[onclick="performAction(\'Plan\')"]').classList.add('amber');
                        }
                    }
                } else {
                    alert(`Failed to create ${action}: ` + data.error);
                }
            })
            .catch((error) => {
                console.error('Error:', error);
                alert(`An error occurred while creating ${action}: ${error.message}`);
            });
        } else {
            alert(`${action} creation is not available at this time. Please complete the previous steps first.`);
        }
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
