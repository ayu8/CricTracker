// Global API utilities
class ApiClient {
    static BASE_URL = '/api/v1';
    
    // Generic API request method
    static async request(endpoint, options = {}) {
        const url = `${this.BASE_URL}${endpoint}`;
        
        const defaultOptions = {
            headers: {
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
            return response;
        } catch (error) {
            console.error(`API request failed for ${endpoint}:`, error);
            throw error;
        }
    }
    
    // Authenticated API request
    static async authenticatedRequest(endpoint, options = {}) {
        const token = AuthManager.getToken();
        
        if (!token) {
            throw new Error('No authentication token found');
        }
        
        const authOptions = {
            ...options,
            headers: {
                ...options.headers,
                'Authorization': `Bearer ${token}`
            }
        };
        
        const response = await this.request(endpoint, authOptions);
        
        // Handle unauthorized responses
        if (response.status === 401) {
            AuthManager.logout();
            throw new Error('Session expired. Please login again.');
        }
        
        return response;
    }
    
    // Specific API methods
    static async login(loginData) {
        console.log('Logging in with data {api.js}:', JSON.stringify(loginData));
        return this.request('/auth/login', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/x-www-form-urlencoded' 
            },
            body: new URLSearchParams(loginData).toString()
        });
    }
    
    static async register(userData) {
        console.log('Registering with data {api.js}:', JSON.stringify(userData));
        return this.request('/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });
    }
    
    static async getCurrentUser() {
        return this.authenticatedRequest('/auth/me');
    }
    
    static async getMatches() {
        return this.authenticatedRequest('/matches');
    }
    
    static async createMatch(matchData) {
        return this.authenticatedRequest('/matches', {
            method: 'POST',
            body: JSON.stringify(matchData)
        });
    }
    
    static async getBattingStats() {
        return this.authenticatedRequest('/bat_stats/summary');
    }
    
    static async getBattingDetailedStats() {
        return this.authenticatedRequest('/bat_stats/detailed');
    }
}

// Make ApiClient globally available
window.ApiClient = ApiClient;