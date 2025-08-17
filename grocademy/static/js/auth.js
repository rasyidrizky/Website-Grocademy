// static/js/auth.js

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
});

function showAlert(message, type = 'danger') {
    const alertContainer = document.getElementById('alert-container');
    const alert = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    alertContainer.innerHTML = alert;
}

async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('/api/auth/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });

        const data = await response.json();

        if (response.ok) {
            // Simpan token di localStorage
            localStorage.setItem('accessToken', data.access);
            localStorage.setItem('refreshToken', data.refresh);
            // Arahkan ke halaman utama
            window.location.href = '/'; 
        } else {
            // Tampilkan pesan error
            const errorMessage = Object.values(data).join('\n');
            showAlert(errorMessage);
        }
    } catch (error) {
        showAlert('An unexpected error occurred. Please try again.');
        console.error('Login Error:', error);
    }
}

async function handleRegister(event) {
    event.preventDefault();
    const firstName = document.getElementById('firstName').value;
    const lastName = document.getElementById('lastName').value;
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const password2 = document.getElementById('password2').value;

    try {
        const response = await fetch('/api/auth/register/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                first_name: firstName, 
                last_name: lastName, 
                username, 
                email, 
                password, 
                password2 
            }),
        });

        const data = await response.json();

        if (response.status === 201) {
            showAlert('Registration successful! Please login.', 'success');
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000); // Tunggu 2 detik sebelum redirect
        } else {
            const errorMessage = Object.entries(data).map(([key, value]) => `${key}: ${value}`).join('<br>');
            showAlert(errorMessage);
        }
    } catch (error) {
        showAlert('An unexpected error occurred. Please try again.');
        console.error('Register Error:', error);
    }
}