// Authentication utility functions
class AuthManager {
    static TOKEN_KEY = 'access_token';
    static USERNAME_KEY = 'username';
    static LOGIN_STATUS_KEY = 'isLoggedIn';
    
    // Store authentication data
    static login(token, username) {
        sessionStorage.setItem(this.TOKEN_KEY, token);
        sessionStorage.setItem(this.USERNAME_KEY, username);
        sessionStorage.setItem(this.LOGIN_STATUS_KEY, 'true');
    }
    
    // Clear authentication data
    static logout() {
        sessionStorage.removeItem(this.TOKEN_KEY);
        sessionStorage.removeItem(this.USERNAME_KEY);
        sessionStorage.removeItem(this.LOGIN_STATUS_KEY);
        window.location.href = '/login';
    }
    
    // Check if user is logged in
    static isLoggedIn() {
        return sessionStorage.getItem(this.LOGIN_STATUS_KEY) === 'true' && 
               sessionStorage.getItem(this.TOKEN_KEY) !== null;
    }
    
    // Get stored token
    static getToken() {
        return sessionStorage.getItem(this.TOKEN_KEY);
    }
    
    // Get stored username
    static getUsername() {
        return sessionStorage.getItem(this.USERNAME_KEY);
    }
    
    // Make authenticated API requests
    static async apiRequest(url, options = {}) {
        const token = this.getToken();
        
        if (!token) {
            throw new Error('No authentication token found');
        }
        
        const defaultOptions = {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        };
        
        const mergedOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...(options.headers || {})
            }
        };
        
        try {
            const response = await fetch(url, mergedOptions);
            
            // If unauthorized, logout and redirect
            if (response.status === 401) {
                this.logout();
                return;
            }
            
            return response;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }
    
    // Protect pages that require authentication
    static requireAuth() {
        if (!this.isLoggedIn()) {
            window.location.href = '/login';
            return false;
        }
        return true;
    }
    
    // Redirect if already logged in (for login/signup pages)
    static redirectIfLoggedIn() {
        if (this.isLoggedIn()) {
            window.location.href = '/dashboard';
            return true;
        }
        return false;
    }
}

// Global utility functions
window.AuthManager = AuthManager;