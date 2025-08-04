document.addEventListener('DOMContentLoaded', function() {
    // Redirect if already logged in
    AuthManager.redirectIfLoggedIn();
    
    const signupForm = document.getElementById('signupForm');
    const signupResult = document.getElementById('signupResult');
    const signUpBtn = signupForm.querySelector('.sign-up-btn');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const strengthFill = document.getElementById('strengthFill');
    const strengthText = document.getElementById('strengthText');
    const passwordMatch = document.getElementById('passwordMatch');

    console.log('Signup form loaded');
    
    // Add loading state to button
    function setLoading(loading) {
        if (loading) {
            signUpBtn.textContent = 'Creating account...';
            signUpBtn.disabled = true;
            signUpBtn.style.opacity = '0.7';
        } else {
            signUpBtn.textContent = 'Create Account';
            signUpBtn.disabled = false;
            signUpBtn.style.opacity = '1';
        }
    }
    
    // Show result message
    function showResult(message, isSuccess) {
        signupResult.textContent = message;
        signupResult.className = `signup-result show ${isSuccess ? 'success' : 'error'}`;
        
        // Hide message after 5 seconds
        setTimeout(() => {
            signupResult.classList.remove('show');
        }, 5000);
    }
    
    // Password strength checker
    function getPasswordStrength(password) {
        let strength = 0;
        let feedback = [];
        
        if (password.length >= 6) strength++;
        else feedback.push('at least 6 characters');
        
        if (password.length >= 10) strength++;
        
        if (/[a-z]/.test(password)) strength++;
        else feedback.push('lowercase letter');
        
        if (/[A-Z]/.test(password)) strength++;
        else feedback.push('uppercase letter');
        
        if (/[0-9]/.test(password)) strength++;
        else feedback.push('number');
        
        if (/[^A-Za-z0-9]/.test(password)) strength++;
        else feedback.push('special character');
        
        return { strength, feedback };
    }
    
    function updatePasswordStrength(password) {
        const { strength, feedback } = getPasswordStrength(password);
        
        // Update strength meter
        strengthFill.className = 'strength-fill';
        strengthText.textContent = 'Password strength: ';
        
        if (strength === 0) {
            strengthText.textContent += 'Very weak';
        } else if (strength <= 2) {
            strengthFill.classList.add('weak');
            strengthText.textContent += 'Weak';
        } else if (strength <= 4) {
            strengthFill.classList.add('fair');
            strengthText.textContent += 'Fair';
        } else if (strength <= 5) {
            strengthFill.classList.add('good');
            strengthText.textContent += 'Good';
        } else {
            strengthFill.classList.add('strong');
            strengthText.textContent += 'Strong';
        }
        
        // Show feedback for improvement
        if (feedback.length > 0 && password.length > 0) {
            strengthText.textContent += ` (Add: ${feedback.slice(0, 2).join(', ')})`;
        }
    }
    
    function updatePasswordMatch() {
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        
        if (confirmPassword.length === 0) {
            passwordMatch.textContent = '';
            passwordMatch.className = 'password-match';
            return;
        }
        
        if (password === confirmPassword) {
            passwordMatch.textContent = '✓ Passwords match';
            passwordMatch.className = 'password-match match';
            confirmPasswordInput.setCustomValidity('');
        } else {
            passwordMatch.textContent = '✗ Passwords do not match';
            passwordMatch.className = 'password-match no-match';
            confirmPasswordInput.setCustomValidity('Passwords do not match');
        }
    }
    
    // Validate form
    function validateForm(formData) {
        const username = formData.get('username').trim();
        const email = formData.get('email').trim();
        const password = formData.get('password');
        const confirmPassword = formData.get('confirmPassword');
        // const terms = formData.get('terms');
        
        if (username.length < 3) {
            showResult('Username must be at least 3 characters long', false);
            return false;
        }
        
        if (!/^[a-zA-Z0-9_]+$/.test(username)) {
            showResult('Username can only contain letters, numbers, and underscores', false);
            return false;
        }
        
        if (password.length < 6) {
            showResult('Password must be at least 6 characters long', false);
            return false;
        }
        
        if (password !== confirmPassword) {
            showResult('Passwords do not match', false);
            return false;
        }
        
        // if (!terms) {
        //     showResult('Please agree to the Terms of Service and Privacy Policy', false);
        //     return false;
        // }
        
        return true;
    }
    
    // Event listeners
    passwordInput.addEventListener('input', function() {
        updatePasswordStrength(this.value);
        updatePasswordMatch();
    });
    
    confirmPasswordInput.addEventListener('input', updatePasswordMatch);
    
    // Form submission handler
    signupForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        
        // Validate form
        if (!validateForm(formData)) {
            return;
        }
        
        setLoading(true);
        
        try {
            console.log('Submitting signup form...');
            
            const signupData = {
                username: formData.get('username').trim(),
                email: formData.get('email').trim(),
                password: formData.get('password')
            };
            
            const response = await ApiClient.register(signupData);
            const result = await response.json();
            
            if (response.ok) {
                showResult('Account created successfully! Redirecting to login...', true);
                
                // Clear form
                signupForm.reset();
                updatePasswordStrength('');
                updatePasswordMatch();
                
                // Redirect to login page after successful signup
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
                
            } else {
                // Handle error response
                const errorMessage = result.detail || result.message || 'Registration failed. Please try again.';
                showResult(errorMessage, false);
            }
            
        } catch (error) {
            console.error('Signup error:', error);
            showResult('Network error. Please check your connection and try again.', false);
        } finally {
            setLoading(false);
        }
    });
    
    // Add input focus effects
    const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"]');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });
    
    // Real-time username validation
    const usernameInput = document.getElementById('username');
    usernameInput.addEventListener('input', function() {
        const username = this.value;
        if (username.length > 0 && !/^[a-zA-Z0-9_]+$/.test(username)) {
            this.setCustomValidity('Username can only contain letters, numbers, and underscores');
        } else if (username.length > 0 && username.length < 3) {
            this.setCustomValidity('Username must be at least 3 characters long');
        } else {
            this.setCustomValidity('');
        }
    });
    
    // Terms and privacy links (placeholder functionality)
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('terms-link')) {
            e.preventDefault();
            showResult('Terms of Service page coming soon!', false);
        }
        
        if (e.target.classList.contains('privacy-link')) {
            e.preventDefault();
            showResult('Privacy Policy page coming soon!', false);
        }
    });
});