function navigateToPage(url) {
    window.location.href = url;
}

function showLogoutConfirmation() {
    document.getElementById('logoutModal').style.display = 'block';
}

function hideLogoutConfirmation() {
    document.getElementById('logoutModal').style.display = 'none';
}


document.addEventListener('DOMContentLoaded', function() {
const addButton = document.querySelector('.add-button');
const clearButton = document.querySelector('.clear-button');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');

addButton.addEventListener('click', function() {
    const email = emailInput.value;
    const password = passwordInput.value;

    fetch('http://localhost:5050//add_admin', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: email, password: password }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 200) {
            alert('Admin added successfully');
            // Optionally clear the form or redirect
            emailInput.value = '';
            passwordInput.value = '';
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to add admin');
    });
});

clearButton.addEventListener('click', function() {
    emailInput.value = '';
    passwordInput.value = '';
});
});



//display admins 

document.addEventListener('DOMContentLoaded', function() {
fetchAdmins();
});

function fetchAdmins() {
fetch('http://localhost:5050/get_admin')
.then(response => {
if (!response.ok) {
    throw new Error('Network response was not ok');
}
return response.json();
})
.then(data => {
if (!Array.isArray(data.data)) {  // Ensure that data.data is an array
    console.error('Expected an array of admins, received:', data);
    throw new TypeError('Received data is not an array');
}
const container = document.getElementById('admin-container');
data.data.forEach(admin => {
    const adminCard = createAdminCard(admin); // Use createAdminCard to generate the card
    container.appendChild(adminCard); // Append the created card to the container
});
})
.catch(error => console.error('Error loading admin data:', error));
}

function createAdminCard(admin) {
const card = document.createElement('div');
card.className = 'admin-card';

const image = document.createElement('img');
image.className = 'admin-image';
image.src = '../assets/images/admin1.png';  // Adjust if you have different images per admin
image.alt = 'Admin Image';

const infoDiv = document.createElement('div');
const email = document.createElement('h5');
email.textContent = admin.email;  // Display the email

infoDiv.appendChild(email);
card.appendChild(image);
card.appendChild(infoDiv);

return card;
}









//logout 
function logout() {
fetch('http://localhost:5050/logout', {
method: 'POST',  // Change this to POST if the server expects POST
})
.then(response => {
if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
}
return response.json();
})
.then(data => {
if (data.status === 200) {
    window.location.href = '../Login.html';
} else {
    throw new Error(data.message || 'Logout failed');
}
})
.catch(error => {
console.error('Error:', error);
alert('Logout failed: ' + error.message); // Optionally show error to the user
});
}
