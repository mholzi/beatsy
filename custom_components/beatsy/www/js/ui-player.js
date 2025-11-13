/**
 * Beatsy Player UI - JavaScript Initialization
 * ES6 module for player interface
 * Mobile-first, vanilla JavaScript (no frameworks)
 *
 * TODO: Story 4.1 - Full player registration implementation
 * Story 3.6 STUB: Admin key detection and "Next Song" button functionality
 */

/**
 * Initialize player UI on DOM ready
 */
function initPlayerUI() {
    console.log('Beatsy Player UI initialized');
    console.log('Version: 1.0.0 (Story 3.6 STUB)');
    console.log('Environment:', {
        userAgent: navigator.userAgent,
        viewportWidth: window.innerWidth,
        viewportHeight: window.innerHeight,
        devicePixelRatio: window.devicePixelRatio
    });

    // Extract game_id from URL query params
    const urlParams = new URLSearchParams(window.location.search);
    const gameId = urlParams.get('game_id');

    if (!gameId) {
        console.error('No game_id in URL');
        showError('Invalid game link. Please get a new link from the game admin.');
        return;
    }

    console.log('Game ID:', gameId);

    // Story 3.6 Task 4: Check for admin_key in localStorage
    checkAdminStatus();

    // Setup event listeners
    setupEventListeners();

    console.log('Player UI ready - awaiting Story 4.1 full implementation');
}

/**
 * Story 3.6 Task 4: Check if admin key exists in localStorage
 * This function detects if the current user is the admin
 */
function checkAdminStatus() {
    const adminKey = localStorage.getItem('beatsy_admin_key');
    const adminKeyExpiry = localStorage.getItem('beatsy_admin_key_expiry');

    if (adminKey && adminKeyExpiry) {
        const now = Date.now();
        const expiry = parseInt(adminKeyExpiry);

        if (now < expiry) {
            console.log('✅ Admin key detected (valid, not expired)');
            console.log('Admin key:', adminKey.substring(0, 8) + '...');
            console.log('Expires:', new Date(expiry).toISOString());
            return true;
        } else {
            console.warn('⚠️ Admin key expired');
            // Don't remove - let server handle expiry validation
            return false;
        }
    } else {
        console.log('Regular player (no admin key)');
        return false;
    }
}

/**
 * Setup event listeners for player UI
 */
function setupEventListeners() {
    // Story 4.1: Player registration form submit
    const registrationForm = document.getElementById('player-registration-form');
    if (registrationForm) {
        registrationForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await joinGame();
        });
    }

    // Story 3.6 Task 9: "Next Song" button click handler
    const nextSongBtn = document.getElementById('next-song-btn');
    if (nextSongBtn) {
        nextSongBtn.addEventListener('click', async (e) => {
            await nextSong();
        });
    }

    console.log('✓ Event listeners registered');
}

/**
 * Story 4.1 + Story 3.6 Task 4: Join game with player name
 * TODO: Story 4.1 - Full implementation
 * Story 3.6 Extension: Include admin_key in request if present
 */
async function joinGame() {
    console.log('Join game requested');

    const playerNameInput = document.getElementById('player-name');
    const joinBtn = document.getElementById('join-game-btn');
    const spinnerElement = document.getElementById('join-spinner');
    const buttonTextElement = document.getElementById('join-text');

    const playerName = playerNameInput.value.trim();

    if (!playerName || playerName.length < 2) {
        showError('Please enter a valid name (at least 2 characters)');
        return;
    }

    try {
        // Show loading state
        joinBtn.disabled = true;
        spinnerElement.classList.remove('hidden');
        buttonTextElement.textContent = 'Joining...';

        // Get game_id from URL
        const urlParams = new URLSearchParams(window.location.search);
        const gameId = urlParams.get('game_id');

        // Story 3.6 Task 4: Include admin_key if present in localStorage
        const requestBody = {
            name: playerName,
            game_id: gameId
        };

        // Check for admin key (Story 3.6 extension)
        const adminKey = localStorage.getItem('beatsy_admin_key');
        if (adminKey) {
            requestBody.admin_key = adminKey;
            console.log('Including admin_key in join request (first 8 chars):', adminKey.substring(0, 8) + '...');
        }

        console.log('Sending join_game request:', {
            name: playerName,
            game_id: gameId,
            has_admin_key: !!adminKey
        });

        // TODO: Story 4.1 - Implement actual /api/beatsy/api/join_game endpoint
        // For now, simulate response for Story 3.6 testing
        const response = await fetch('/api/beatsy/api/join_game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            throw new Error(`Registration failed: ${response.status}`);
        }

        const data = await response.json();

        console.log('Join game successful:', data);

        // Story 3.6 Task 8: Show "Next Song" button if is_admin=true
        if (data.is_admin === true) {
            console.log('✅ Admin player confirmed by server');
            localStorage.setItem('beatsy_is_admin', 'true');
            showAdminControls();
        } else {
            console.log('Regular player registered');
            localStorage.setItem('beatsy_is_admin', 'false');
        }

        // TODO: Story 4.1 - Navigate to game lobby or active round view
        showSuccess(`Welcome, ${playerName}! (Story 4.1: Implement game view navigation)`);

    } catch (error) {
        console.error('Error joining game:', error);
        showError('Failed to join game. TODO: Story 4.1 - Implement join_game endpoint');

        // Re-enable button for retry
        joinBtn.disabled = false;
        spinnerElement.classList.add('hidden');
        buttonTextElement.textContent = 'Join Game';
    }
}

/**
 * Story 3.6 Task 8: Show admin controls ("Next Song" button)
 */
function showAdminControls() {
    const nextSongBtn = document.getElementById('next-song-btn');
    if (nextSongBtn) {
        nextSongBtn.classList.remove('hidden');
        console.log('✓ Admin controls visible (Next Song button)');
    }
}

/**
 * Story 3.6 Task 9: Trigger next song (admin only)
 * TODO: Story 5.2 - Round initialization logic
 */
async function nextSong() {
    console.log('Next Song requested (admin only)');

    const nextSongBtn = document.getElementById('next-song-btn');

    try {
        // Verify admin status
        const isAdmin = localStorage.getItem('beatsy_is_admin') === 'true';
        if (!isAdmin) {
            console.error('Next Song button clicked by non-admin');
            showError('Unauthorized: Only admins can start the next song');
            return;
        }

        // Disable button during request
        nextSongBtn.disabled = true;
        nextSongBtn.textContent = 'Starting...';

        // Get game session info
        const gameId = new URLSearchParams(window.location.search).get('game_id');

        // TODO: Story 3.6 Task 10 - Implement /api/beatsy/api/next_song endpoint
        const response = await fetch('/api/beatsy/api/next_song', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                game_id: gameId,
                // Add session_id when Story 4.1 provides it
            })
        });

        if (!response.ok) {
            throw new Error(`Next song failed: ${response.status}`);
        }

        const data = await response.json();

        console.log('Next song started:', data);
        showSuccess('Next song started! Round ' + (data.round_number || 'N'));

        // Re-enable button
        nextSongBtn.disabled = false;
        nextSongBtn.textContent = 'Next Song ▶';

    } catch (error) {
        console.error('Error starting next song:', error);
        showError('Failed to start next song. TODO: Story 3.6 Task 10 - Implement next_song endpoint');

        // Re-enable button
        nextSongBtn.disabled = false;
        nextSongBtn.textContent = 'Next Song ▶';
    }
}

/**
 * Show error message
 */
function showError(message) {
    console.error('[ERROR]', message);

    const statusSection = document.getElementById('status-section');
    const statusMessage = document.getElementById('status-message');

    if (statusSection && statusMessage) {
        statusSection.classList.remove('hidden', 'bg-blue-50', 'border-blue-200');
        statusSection.classList.add('bg-red-50', 'border-red-200');
        statusMessage.textContent = '❌ ' + message;
    }

    // Also show as toast for visibility
    showToast(message, 'error');
}

/**
 * Show success message
 */
function showSuccess(message) {
    console.log('[SUCCESS]', message);

    const statusSection = document.getElementById('status-section');
    const statusMessage = document.getElementById('status-message');

    if (statusSection && statusMessage) {
        statusSection.classList.remove('hidden', 'bg-red-50', 'border-red-200');
        statusSection.classList.add('bg-blue-50', 'border-blue-200');
        statusMessage.textContent = '✅ ' + message;
    }

    // Also show as toast for visibility
    showToast(message, 'success');
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    console.log(`[TOAST ${type.toUpperCase()}]`, message);

    // Create toast element
    const toast = document.createElement('div');
    toast.className = `fixed bottom-4 right-4 p-4 rounded-lg shadow-lg z-50 max-w-md ${
        type === 'success' ? 'bg-green-500' :
        type === 'error' ? 'bg-red-500' :
        'bg-blue-500'
    } text-white`;
    toast.textContent = message;

    document.body.appendChild(toast);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

/**
 * Main initialization - runs when DOM is fully loaded
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('=== Beatsy Player UI Starting ===');
    console.log('TODO: Story 4.1 - Full player registration and game view');
    console.log('Story 3.6 STUB: Admin key detection and "Next Song" functionality');

    initPlayerUI();

    console.log('=== Beatsy Player UI Ready ===');
});

/**
 * Story 3.6 Task 13: Show admin indicator in player list
 * TODO: Story 4.3 - Implement player list UI
 *
 * When player list is rendered, check each player for is_admin flag:
 * - If is_admin === true: Add badge/icon next to name (e.g., "👑 Admin" or "🎮 Admin")
 * - Visual distinction: purple/gold color, distinctive icon
 *
 * Example implementation (for Story 4.3):
 * ```javascript
 * function renderPlayerList(players) {
 *   players.forEach(player => {
 *     const adminBadge = player.is_admin ? '<span class="admin-badge">👑</span>' : '';
 *     const playerHtml = `<li>${player.name} ${adminBadge}</li>`;
 *     // ... append to player list
 *   });
 * }
 * ```
 */

/**
 * Export functions for testing (optional - for future test suite)
 */
export {
    initPlayerUI,
    checkAdminStatus,
    joinGame,
    showAdminControls,
    nextSong,
    showError,
    showSuccess,
    showToast
};
