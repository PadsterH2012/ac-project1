function openNav() {
    document.getElementById("mySidenav").style.width = "250px";
    document.getElementById("main").style.marginLeft = "250px";
}

function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
    document.getElementById("main").style.marginLeft = "0";
}

// Simulating user authentication state
let isLoggedIn = false;

function updateAuthButtons() {
    const loginBtn = document.getElementById('loginBtn');
    const registerBtn = document.getElementById('registerBtn');
    const logoutBtn = document.getElementById('logoutBtn');

    if (isLoggedIn) {
        loginBtn.style.display = 'none';
        registerBtn.style.display = 'none';
        logoutBtn.style.display = 'block';
    } else {
        loginBtn.style.display = 'block';
        registerBtn.style.display = 'block';
        logoutBtn.style.display = 'none';
    }
}

// Initial update
updateAuthButtons();

// Simulating login/logout actions
document.getElementById('loginBtn').addEventListener('click', function(e) {
    e.preventDefault();
    isLoggedIn = true;
    updateAuthButtons();
    alert('You are now logged in!');
});

document.getElementById('logoutBtn').addEventListener('click', function(e) {
    e.preventDefault();
    isLoggedIn = false;
    updateAuthButtons();
    alert('You have been logged out.');
});
