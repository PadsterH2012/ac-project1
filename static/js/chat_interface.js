const users = [
    { name: 'Alice', avatar: 'https://websim.ai/avatar1.jpg' },
    { name: 'Bob', avatar: 'https://websim.ai/avatar2.jpg' },
    { name: 'Charlie', avatar: 'https://websim.ai/avatar3.jpg' },
    { name: 'You', avatar: 'https://websim.ai/avatar4.jpg' }
];

const messages = [
    { sender: 'Alice', text: 'Hey team! I\'ve adjusted the action buttons to make them more readable.' },
    { sender: 'Bob', text: 'Nice work, Alice! The centered text and smaller font size look much better.' },
    { sender: 'Charlie', text: 'I agree, it\'s easier to read now. The buttons also look more uniform.' },
    { sender: 'You', text: 'This is great! The new layout is both functional and visually appealing.' },
    { sender: 'Alice', text: 'Thanks! I adjusted the CSS to center the text and made the buttons a bit taller to accommodate longer names.' },
    { sender: 'Bob', text: 'It\'s a smart design choice. Now all the buttons look consistent, even with varying text lengths.' },
    { sender: 'Charlie', text: 'This small change really improves the overall user experience. Good job!' },
    { sender: 'You', text: 'Absolutely! Let\'s keep refining our UI like this to make it as user-friendly as possible.' }
];

function getRandomUser() {
    return users[Math.floor(Math.random() * users.length)];
}

function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const chatMessages = document.getElementById('chatMessages');
    const messageText = messageInput.value;

    if (messageText.trim() === '') return;

    const user = getRandomUser();
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', user.name === 'You' ? 'user' : 'other');

    const avatarElement = document.createElement('img');
    avatarElement.src = user.avatar;
    avatarElement.alt = user.name;
    avatarElement.classList.add('avatar');

    const bubbleElement = document.createElement('div');
    bubbleElement.classList.add('bubble');
    
    const senderNameElement = document.createElement('span');
    senderNameElement.classList.add('sender-name');
    senderNameElement.textContent = user.name;

    const messageTextElement = document.createElement('p');
    messageTextElement.textContent = messageText;

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
    messageInput.value = '';
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
    alert(`Performing action: ${action}`);
}

function navigateVFS(path) {
    alert(`Navigating to: ${path}`);
}

// Initialize the chat with some messages
window.onload = function() {
    const chatMessages = document.getElementById('chatMessages');
    messages.forEach(msg => {
        const user = users.find(u => u.name === msg.sender);
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', user.name === 'You' ? 'user' : 'other');

        const avatarElement = document.createElement('img');
        avatarElement.src = user.avatar;
        avatarElement.alt = user.name;
        avatarElement.classList.add('avatar');

        const bubbleElement = document.createElement('div');
        bubbleElement.classList.add('bubble');
        
        const senderNameElement = document.createElement('span');
        senderNameElement.classList.add('sender-name');
        senderNameElement.textContent = user.name;

        const messageTextElement = document.createElement('p');
        messageTextElement.textContent = msg.text;

        bubbleElement.appendChild(senderNameElement);
        bubbleElement.appendChild(messageTextElement);

        messageElement.appendChild(avatarElement);
        messageElement.appendChild(bubbleElement);
        chatMessages.appendChild(messageElement);
    });
    chatMessages.scrollTop = chatMessages.scrollHeight;
};

function navigateVFS(path) {
    alert(`Navigating to: ${path}`);
}
