document.addEventListener('DOMContentLoaded', function() {
    // Redirect if already logged in
    AuthManager.redirectIfLoggedIn();

    const loginForm = document.getElementById('loginForm');
    const loginResult = document.getElementById('loginResult');
    const signInBtn = loginForm.querySelector('.sign-in-btn');

    console.log('Login form loaded');
    
    // Add loading state to button
    function setLoading(loading) {
        if (loading) {
            signInBtn.textContent = 'Signing in...';
            signInBtn.disabled = true;
            signInBtn.style.opacity = '0.7';
        } else {
            signInBtn.textContent = 'Sign in';
            signInBtn.disabled = false;
            signInBtn.style.opacity = '1';
        }
    }
    
    // Show result message
    function showResult(message, isSuccess) {
        loginResult.textContent = message;
        loginResult.className = `login-result show ${isSuccess ? 'success' : 'error'}`;
        
        // Hide message after 5 seconds
        setTimeout(() => {
            loginResult.classList.remove('show');
        }, 5000);
    }

    // Store authentication data
    function storeAuthData(token, username) {
        sessionStorage.setItem('access_token', token);
        sessionStorage.setItem('username', username);
        sessionStorage.setItem('isLoggedIn', 'true');
    }
    
    // Form submission handler
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        setLoading(true);
        
        try {
            console.log('Submitting login form...');
            // const formData = new FormData(e.target);
            const formData = new URLSearchParams(new FormData(e.target));
            const loginData = {
                username: formData.get('username').trim(),
                password: formData.get('password')
            };
            console.log('Login data:', loginData);

            // Validate input
            if (!loginData.username || !loginData.password) {
                showResult('Please enter both username and password', false);
                return;
            }

            console.log('Making API request to login with data:', JSON.stringify(loginData));
            console.log(loginData);
            // Use the ApiClient for consistent API calls
            const response = await ApiClient.login(loginData);
            
            // const response = await fetch('/api/v1/auth/login', {
            //     method: 'POST',
            //     headers: {
            //         'Content-Type': 'application/json'
            //     },
            //     body: JSON.stringify(loginData)
            // });

            // console.log('Response status:', response.status);
            // console.log('Response headers:', response.headers);

            const result = await response.json();
            
            if (response.ok && result.access_token) {
                showResult('Login successful! Redirecting...', true);
                
                // Store authentication data using AuthManager
                AuthManager.login(result.access_token, loginData.username);
                
                // Redirect after successful login (optional)
                setTimeout(() => {
                    window.location.href = '/dashboard';
                    console.log('Redirect to dashboard or main page');
                }, 1500);
                
            } else {
                // Handle error response
                const errorMessage = result.detail || result.message || 'Login failed. Please try again.';
                showResult(errorMessage, false);
            }
            
        } catch (error) {
            console.error('Login error:', error);
            showResult('Network error. Please check your connection and try again.', false);
        } finally {
            setLoading(false);
        }
    });
    
    // Add input focus effects
    const inputs = document.querySelectorAll('input[type="text"], input[type="password"]');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });
    
    // Forgot password handler
    const forgotPasswordLink = document.querySelector('.forgot-password');
    if (forgotPasswordLink) {
        forgotPasswordLink.addEventListener('click', function(e) {
            e.preventDefault();
            showResult('Forgot password functionality coming soon!', false);
        });
    }
    
    // Enter key support for better UX
    loginForm.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            loginForm.dispatchEvent(new Event('submit'));
        }
    });
    
    // Clear any previous error messages when user starts typing
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    
    [usernameInput, passwordInput].forEach(input => {
        if (input) {
            input.addEventListener('input', function() {
                if (loginResult.classList.contains('show') && loginResult.classList.contains('error')) {
                    loginResult.classList.remove('show');
                }
            });
        }
    });
});