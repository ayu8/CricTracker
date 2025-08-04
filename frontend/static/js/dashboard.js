document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard
    initializeDashboard();
    
    // Set up navigation
    setupNavigation();
    
    // Set up logout
    setupLogout();
    
    // Load initial data
    loadDashboardData();
});

function initializeDashboard() {
    // Display username in welcome message
    const username = AuthManager.getUsername();
    const welcomeElement = document.getElementById('welcomeUser');
    if (welcomeElement && username) {
        welcomeElement.textContent = `Welcome, ${username}!`;
    }
}

function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const contentSections = document.querySelectorAll('.content-section');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links and sections
            navLinks.forEach(l => l.classList.remove('active'));
            contentSections.forEach(s => s.classList.remove('active'));
            
            // Add active class to clicked link
            this.classList.add('active');
            
            // Show corresponding content section
            const targetPage = this.getAttribute('data-page');
            const targetSection = document.getElementById(targetPage);
            if (targetSection) {
                targetSection.classList.add('active');
                
                // Load data for specific sections
                loadSectionData(targetPage);
            }
        });
    });
}

function setupLogout() {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            if (confirm('Are you sure you want to logout?')) {
                AuthManager.logout();
            }
        });
    }
}

async function loadDashboardData() {
    try {
        // Load overview stats
        await loadOverviewStats();
        
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
        showError('Failed to load dashboard data. Please refresh the page.');
    }
}

async function loadOverviewStats() {
    try {
        // Example API calls - adjust based on your actual endpoints
        const statsResponse = await AuthManager.apiRequest('/api/v1/bat_stats/summary');
        
        if (statsResponse.ok) {
            const stats = await statsResponse.json();
            
            // Update overview cards
            updateStatCard('totalMatches', stats.total_matches || 0);
            updateStatCard('totalRuns', stats.total_runs || 0);
            updateStatCard('battingAverage', (stats.batting_average || 0).toFixed(2));
            updateStatCard('strikeRate', (stats.strike_rate || 0).toFixed(2));
        }
        
    } catch (error) {
        console.error('Failed to load overview stats:', error);
        // Set default values on error
        updateStatCard('totalMatches', 0);
        updateStatCard('totalRuns', 0);
        updateStatCard('battingAverage', '0.00');
        updateStatCard('strikeRate', '0.00');
    }
}

function updateStatCard(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = value;
    }
}

async function loadSectionData(section) {
    switch (section) {
        case 'matches':
            await loadMatches();
            break;
        case 'batting':
            await loadBattingStats();
            break;
        case 'bowling':
            await loadBowlingStats();
            break;
        case 'analytics':
            await loadAnalytics();
            break;
        default:
            // Overview is already loaded
            break;
    }
}

async function loadMatches() {
    try {
        const response = await AuthManager.apiRequest('/api/v1/matches');
        
        if (response.ok) {
            const matches = await response.json();
            displayMatches(matches);
        } else {
            showError('Failed to load matches');
        }
        
    } catch (error) {
        console.error('Failed to load matches:', error);
        showError('Failed to load matches. Please try again.');
    }
}

function displayMatches(matches) {
    const matchesList = document.getElementById('matchesList');
    if (!matchesList) return;
    
    if (matches.length === 0) {
        matchesList.innerHTML = '<p>No matches found. Add your first match!</p>';
        return;
    }
    
    const matchesHTML = matches.map(match => `
        <div class="match-card">
            <h3>${match.date} - ${match.ground}</h3>
            <p>Runs: ${match.runs_scored || 'N/A'} | Balls: ${match.balls_faced || 'N/A'}</p>
            <p>Result: ${match.match_result}</p>
        </div>
    `).join('');
    
    matchesList.innerHTML = matchesHTML;
}

async function loadBattingStats() {
    try {
        const response = await AuthManager.apiRequest('/api/v1/bat_stats/detailed');
        
        if (response.ok) {
            const stats = await response.json();
            displayBattingStats(stats);
        } else {
            showError('Failed to load batting stats');
        }
        
    } catch (error) {
        console.error('Failed to load batting stats:', error);
        showError('Failed to load batting stats. Please try again.');
    }
}

function displayBattingStats(stats) {
    const battingStats = document.getElementById('battingStats');
    if (!battingStats) return;
    
    battingStats.innerHTML = `
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Innings</h3>
                <p class="stat-number">${stats.innings || 0}</p>
            </div>
            <div class="stat-card">
                <h3>Highest Score</h3>
                <p class="stat-number">${stats.highest_score || 0}</p>
            </div>
            <div class="stat-card">
                <h3>Fifties</h3>
                <p class="stat-number">${stats.fifties || 0}</p>
            </div>
            <div class="stat-card">
                <h3>Hundreds</h3>
                <p class="stat-number">${stats.hundreds || 0}</p>
            </div>
        </div>
    `;
}

async function loadBowlingStats() {
    // Similar implementation for bowling stats
    const bowlingStats = document.getElementById('bowlingStats');
    if (bowlingStats) {
        bowlingStats.innerHTML = '<p>Bowling stats will be implemented soon!</p>';
    }
}

async function loadAnalytics() {
    // Implementation for charts and analytics
    const chartsContainer = document.getElementById('chartsContainer');
    if (chartsContainer) {
        chartsContainer.innerHTML = '<p>Analytics and charts will be implemented soon!</p>';
    }
}

function showError(message) {
    // You can implement a more sophisticated error display
    alert(message);
}

// Add match functionality
document.addEventListener('click', function(e) {
    if (e.target.id === 'addMatchBtn') {
        // Redirect to add match page or open modal
        window.location.href = '/add-match';
    }
});