/**
 * Beatsy Player UI - WebSocket-Based Registration
 * Story 4.1: Player Registration Form
 *
 * Implements:
 * - WebSocket connection (Task 3)
 * - Client-side form validation (Task 4)
 * - Join game request handler (Task 5)
 * - WebSocket response handler (Task 6)
 * - Lobby transition stub (Task 7)
 * - Mobile keyboard optimizations (Task 9)
 */


// Story 9.1-9.3: Import results view rendering functions
import { renderResultsView } from './ui-results.js';
// Global WebSocket connection
let ws = null;
let connectionAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;

// Global timer interval for active round
let timerInterval = null;

// Story 8.6: Guess submission state
const gameState = {
    locked: false,
    playerName: null,
    yearGuess: null,
    betActive: false
};

/**
 * Story 4.5 Task 10: Pre-load year dropdown during page load
 * AC-6: Year dropdown pre-populated with range (1950-2024)
 * Populates dropdown in descending order (2024 → 1950)
 */
function preloadYearDropdown() {
    const yearSelector = document.getElementById('year-selector');
    if (!yearSelector) {
        console.warn('Year selector not found, skipping pre-load');
        return;
    }

    // Default year range: 1950 to current year
    const currentYear = new Date().getFullYear();
    const minYear = 1950;
    const maxYear = currentYear;

    // Clear existing options
    yearSelector.innerHTML = '';

    // Add placeholder option
    const placeholder = document.createElement('option');
    placeholder.value = '';
    placeholder.textContent = 'Select a year...';
    placeholder.disabled = true;
    placeholder.selected = true;
    yearSelector.appendChild(placeholder);

    // Generate options in descending order (2024 → 1950)
    for (let year = maxYear; year >= minYear; year--) {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        yearSelector.appendChild(option);
    }

    console.log(`✓ Year dropdown pre-loaded (${minYear}-${maxYear}, ${maxYear - minYear + 1} years)`);
}

/**
 * Initialize player UI on DOM ready
 * Story 4.4: Check for reconnection BEFORE showing registration
 * Story 4.5: Pre-load year dropdown for active round view
 */
function initPlayerUI() {
    console.log('Beatsy Player UI initialized (Story 4.5)');
    console.log('Version: 4.5.0 - Active round transition support');

    // Story 4.5 Task 10: Pre-load year dropdown during page load
    preloadYearDropdown();

    // Story 4.4 AC-1: Check for existing session BEFORE showing registration
    const sessionId = localStorage.getItem('beatsy_session_id');
    const playerName = localStorage.getItem('beatsy_player_name');

    if (sessionId && playerName) {
        console.log('Existing session found, attempting reconnection:', {
            session: sessionId.substring(0, 8) + '...',
            player: playerName
        });

        // Show reconnection loader
        showReconnectionLoader();

        // Connect to WebSocket and attempt reconnection
        connectWebSocket();
    } else {
        // No session found, show registration form
        console.log('No existing session, showing registration form');
        document.getElementById('registration-view').classList.remove('hidden');

        // Connect to WebSocket for registration
        connectWebSocket();

        // Setup form validation
        setupFormValidation();

        // Setup event listeners
        setupEventListeners();
    }

    console.log('Player UI ready');
}

/**
 * Story 4.3 Task 12: Check if player has existing session in localStorage
 * Returns session info if valid, null otherwise
 */
function checkExistingSession() {
    const sessionId = localStorage.getItem('beatsy_session_id');
    const playerName = localStorage.getItem('beatsy_player_name');

    if (sessionId && playerName) {
        console.log(`Found existing session: ${playerName} (${sessionId})`);
        return { sessionId, playerName };
    }

    return null;
}

/**
 * Story 11.4: Restore lobby view for existing session with horizontal ticker
 * Shows lobby with "Reconnecting..." state until WebSocket reconnects
 */
function restoreLobbyView() {
    // Hide registration form, show lobby view
    document.getElementById('registration-view').classList.add('hidden');
    document.getElementById('lobby-view').classList.remove('hidden');

    // Show reconnecting state (Story 11.4: updated to use ticker)
    const ticker = document.getElementById('lobby-players-ticker');
    const countEl = document.getElementById('lobby-player-count');

    if (ticker) {
        ticker.innerHTML = '<span class="px-3 py-1 bg-gray-100 text-gray-500 rounded-full text-sm">Reconnecting...</span>';
    }

    if (countEl) {
        countEl.textContent = 'Reconnecting to game...';
    }

    console.log('Lobby view restored, waiting for WebSocket connection');
}

/**
 * Story 4.4 Task 13: Show reconnection loader
 * AC-1: Loading spinner displays: "Reconnecting to game..."
 */
function showReconnectionLoader() {
    const loader = document.getElementById('reconnection-loader');
    if (loader) {
        loader.classList.remove('hidden');
    }

    // Hide registration and lobby views during reconnection
    document.getElementById('registration-view').classList.add('hidden');
    document.getElementById('lobby-view').classList.add('hidden');
}

/**
 * Story 4.4 Task 13: Hide reconnection loader
 */
function hideReconnectionLoader() {
    const loader = document.getElementById('reconnection-loader');
    if (loader) {
        loader.classList.add('hidden');
    }
}

/**
 * Story 4.4 Task 2: Send reconnect WebSocket message
 * AC-1: WebSocket establishes connection and sends reconnect message
 * AC-6: 5-second timeout for reconnection response
 */
let reconnectTimeout = null;

function attemptReconnection(sessionId, playerName) {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        console.error('WebSocket not connected, cannot send reconnect message');
        handleReconnectionFailure('timeout');
        return;
    }

    try {
        // Send reconnect message following Story 4.4 protocol
        const message = {
            type: 'beatsy/reconnect',
            session_id: sessionId,
            player_name: playerName,
            id: Date.now()  // HA WebSocket API requires id field
        };

        console.log('Sending reconnect message:', { session: sessionId.substring(0, 8) + '...', player: playerName });
        ws.send(JSON.stringify(message));

        // AC-6: Set 5-second timeout for reconnection response
        reconnectTimeout = setTimeout(() => {
            console.warn('Reconnection timeout after 5 seconds');
            clearReconnectTimeout();
            handleReconnectionFailure('timeout');
        }, 5000);

    } catch (error) {
        console.error('Error sending reconnect message:', error);
        handleReconnectionFailure('network_error');
    }
}

/**
 * Clear reconnection timeout (on success or failure)
 */
function clearReconnectTimeout() {
    if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
        reconnectTimeout = null;
    }
}

/**
 * Story 4.4 Task 5: Handle reconnection response
 * AC-2: Valid session restoration - routes to appropriate view
 * AC-3: Invalid session handling - clears localStorage and shows registration
 */
function handleReconnectResponse(data) {
    clearReconnectTimeout();
    hideReconnectionLoader();

    if (!data.success) {
        // AC-3, AC-7: Reconnection failed
        console.warn('Reconnection failed:', data.reason);
        handleReconnectionFailure(data.reason);
        return;
    }

    // AC-2: Reconnection successful
    console.log('✅ Reconnection successful!', data);

    // Story 8.6: Initialize global gameState with player name (before local variable shadows it)
    gameState.playerName = data.player.name;

    const reconnectGameState = data.game_state;
    const player = data.player;

    // Update localStorage with current session info
    localStorage.setItem('beatsy_session_id', player.session_id);
    localStorage.setItem('beatsy_player_name', player.name);

    // Route to appropriate view based on game status
    switch (reconnectGameState.status) {
        case 'lobby':
            console.log('Restoring to lobby view');
            showLobbyViewAfterReconnect(reconnectGameState);
            break;

        case 'active':
            console.log('Restoring to active round view');
            // TODO Story 4.5+: Implement active round view restoration
            showLobbyViewAfterReconnect(reconnectGameState);  // Fallback to lobby for now
            break;

        case 'results':
            console.log('Restoring to results view');
            // TODO Story 4.5+: Implement results view restoration
            showLobbyViewAfterReconnect(reconnectGameState);  // Fallback to lobby for now
            break;

        default:
            console.error('Unknown game status:', reconnectGameState.status);
            showLobbyViewAfterReconnect(reconnectGameState);
    }

    // Setup form validation and event listeners
    setupFormValidation();
    setupEventListeners();
}

/**
 * Show lobby view after successful reconnection
 */
function showLobbyViewAfterReconnect(gameState) {
    document.getElementById('registration-view').classList.add('hidden');
    document.getElementById('lobby-view').classList.remove('hidden');

    // Initialize lobby with current players
    const players = gameState.players.map(name => ({
        name: name,
        joined_at: Date.now()  // Timestamp not critical for display
    }));

    initializeLobby(players);
}

/**
 * Story 4.4 Task 7: Handle reconnection failure
 * AC-3: Invalid session - clears localStorage and shows registration
 * AC-6: Reconnection failure fallback - shows error with retry options
 * AC-7: Session expiration - clears localStorage and shows registration
 */
function handleReconnectionFailure(reason) {
    hideReconnectionLoader();

    console.warn('Reconnection failed, reason:', reason);

    // Determine error message based on reason
    const errorMessages = {
        'session_not_found': 'Previous game ended. Please register again.',
        'session_expired': 'Session expired. Please register again.',
        'timeout': 'Reconnection failed. Please check your connection.',
        'network_error': 'Network error. Please check your connection.'
    };

    const message = errorMessages[reason] || 'Unable to reconnect. Please register again.';

    // AC-3, AC-7: Clear localStorage for session not found or expired
    if (reason === 'session_not_found' || reason === 'session_expired') {
        localStorage.removeItem('beatsy_session_id');
        localStorage.removeItem('beatsy_player_name');
        console.log('Session cleared from localStorage');

        // Show registration form with error message
        showRegistrationWithError(message);
    } else {
        // AC-6: Show error with retry option
        showReconnectionError(message);
    }
}

/**
 * Show registration form with error message
 */
function showRegistrationWithError(message) {
    // Hide all other views
    document.getElementById('lobby-view').classList.add('hidden');
    hideReconnectionError();

    // Show registration form
    document.getElementById('registration-view').classList.remove('hidden');

    // Display error message
    showError(message);

    // Setup form validation and event listeners
    setupFormValidation();
    setupEventListeners();
}

/**
 * Story 4.4 Task 7: Show reconnection error UI
 * AC-6: User can click "Try Again" to retry or "Join New Game" to reset
 */
function showReconnectionError(message) {
    const errorDiv = document.getElementById('reconnection-error');
    const messageEl = document.getElementById('reconnection-error-message');

    if (errorDiv && messageEl) {
        messageEl.textContent = message;
        errorDiv.classList.remove('hidden');

        // Setup retry button
        const retryBtn = document.getElementById('reconnect-retry-btn');
        if (retryBtn) {
            retryBtn.onclick = () => {
                hideReconnectionError();
                showReconnectionLoader();
                const sessionId = localStorage.getItem('beatsy_session_id');
                const playerName = localStorage.getItem('beatsy_player_name');
                if (sessionId && playerName) {
                    attemptReconnection(sessionId, playerName);
                }
            };
        }

        // Setup reset button
        const resetBtn = document.getElementById('reconnect-reset-btn');
        if (resetBtn) {
            resetBtn.onclick = () => {
                localStorage.removeItem('beatsy_session_id');
                localStorage.removeItem('beatsy_player_name');
                hideReconnectionError();
                showRegistrationWithError('');
            };
        }
    }
}

/**
 * Hide reconnection error UI
 */
function hideReconnectionError() {
    const errorDiv = document.getElementById('reconnection-error');
    if (errorDiv) {
        errorDiv.classList.add('hidden');
    }
}

/**
 * Task 3: Connect to Beatsy WebSocket (unauthenticated)
 * Reuses patterns from Story 2.6 and Story 3.7
 */
function connectWebSocket() {
    try {
        // Connect to Beatsy WebSocket (unauthenticated per Epic 1 POC)
        const wsUrl = `ws://${window.location.host}/api/beatsy/ws`;
        console.log('Connecting to WebSocket:', wsUrl);

        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('✅ Connected to Beatsy WebSocket');
            connectionAttempts = 0;

            // Story 4.4 AC-1: Attempt reconnection if session exists
            const sessionId = localStorage.getItem('beatsy_session_id');
            const playerName = localStorage.getItem('beatsy_player_name');

            if (sessionId && playerName) {
                console.log('Sending reconnect message for existing session');
                attemptReconnection(sessionId, playerName);
            }
        };

        ws.onmessage = (event) => {
            handleWebSocketMessage(event);
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            showError('Unable to connect. Check WiFi connection.');
        };

        ws.onclose = () => {
            console.warn('WebSocket connection closed');
            // Implement reconnection logic (Story 3.7 pattern)
            attemptReconnect();
        };

    } catch (error) {
        console.error('Failed to establish WebSocket connection:', error);
        showError('Unable to connect. Check WiFi connection.');
    }
}

/**
 * Attempt to reconnect with exponential backoff (Story 3.7 pattern)
 */
function attemptReconnect() {
    if (connectionAttempts >= MAX_RECONNECT_ATTEMPTS) {
        console.error('Max reconnection attempts reached');
        showError('Connection lost. Please refresh the page.');
        return;
    }

    connectionAttempts++;
    const delay = Math.min(1000 * Math.pow(2, connectionAttempts - 1), 8000);
    console.log(`Reconnecting in ${delay}ms (attempt ${connectionAttempts}/${MAX_RECONNECT_ATTEMPTS})`);

    setTimeout(() => {
        connectWebSocket();
    }, delay);
}

/**
 * Task 4: Setup client-side form validation
 */
function setupFormValidation() {
    const nameInput = document.getElementById('player-name');
    const joinButton = document.getElementById('join-button');

    if (!nameInput || !joinButton) {
        console.error('Form elements not found');
        return;
    }

    // Initial state: Enable button if input has value
    const initialValue = nameInput.value.trim();
    joinButton.disabled = initialValue.length === 0;

    // Real-time validation on input
    nameInput.addEventListener('input', () => {
        const name = nameInput.value.trim();

        // Enable/disable button based on name length
        if (name.length === 0) {
            joinButton.disabled = true;
        } else if (name.length > 20) {
            // maxlength attribute prevents this, but double-check
            nameInput.value = name.substring(0, 20);
            joinButton.disabled = false;
        } else {
            joinButton.disabled = false;
        }
    });

    console.log('✓ Form validation setup complete');
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Task 5: Form submit handler
    const joinForm = document.getElementById('join-form');
    if (joinForm) {
        joinForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await joinGame();
        });
    }

    // Task 9: Enter key submit handler (mobile keyboard)
    const nameInput = document.getElementById('player-name');
    if (nameInput) {
        nameInput.addEventListener('keypress', (e) => {
            const joinButton = document.getElementById('join-button');
            if (e.key === 'Enter' && !joinButton.disabled) {
                document.getElementById('join-form').requestSubmit();
            }
        });
    }

    // Story 8.3: Bet toggle click handler
    const betToggle = document.getElementById('bet-toggle');
    if (betToggle) {
        betToggle.addEventListener('click', onBetToggle);
        console.log('✓ Bet toggle listener registered');
    }

    // Story 8.2: Year selector change handler
    setupYearSelectorListener();

    console.log('✓ Event listeners registered');
}

/**
 * Task 5: Implement join game request handler
 * Sends WebSocket message: {type: "join_game", name: "Sarah"}
 */
async function joinGame() {
    const nameInput = document.getElementById('player-name');
    const joinButton = document.getElementById('join-button');

    const name = nameInput.value.trim();

    if (!name) {
        showError('Name required');
        return;
    }

    if (name.length > 20) {
        showError('Max 20 characters');
        return;
    }

    // Check WebSocket connection
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        showError('Unable to connect. Check WiFi connection.');
        return;
    }

    try {
        // Show loading state
        joinButton.disabled = true;
        joinButton.innerHTML = '<span class="inline-block animate-spin mr-2">⏳</span> Joining...';

        // Send WebSocket message (AC-4)
        const message = {
            type: 'join_game',
            name: name
        };

        console.log('Sending join_game message:', message);
        ws.send(JSON.stringify(message));

        // Response will be handled in handleWebSocketMessage()

    } catch (error) {
        console.error('Error joining game:', error);
        showError('Failed to join. Please try again.');
        resetJoinButton();
    }
}

/**
 * Task 6: Handle WebSocket messages (including join_game_response)
 * Story 4.3 Task 5: Added beatsy/event handler for player_joined
 * Story 4.4 Task 5: Added reconnect response handler
 */
function handleWebSocketMessage(event) {
    try {
        const data = JSON.parse(event.data);
        console.log('WebSocket message received:', data);

        // Handle HA WebSocket API responses (type: "result")
        if (data.type === 'result') {
            // Check if this is a response to our reconnect or join_game message
            if (data.success === false && data.error) {
                console.warn('Command failed:', data.error);
                // Handle as reconnection failure if we're waiting for reconnect
                if (reconnectTimeout) {
                    clearReconnectTimeout();
                    handleReconnectionFailure(data.error.code || 'unknown_error');
                    return;
                }
            }
            // Handle successful result responses
            if (data.result) {
                // Check if this is a reconnect response
                if ('success' in data.result && 'game_state' in data.result) {
                    handleReconnectResponse(data.result);
                    return;
                }
                // Check if this is a join_game response
                if ('success' in data.result && 'session_id' in data.result) {
                    handleJoinGameResponse(data.result);
                    return;
                }
            }
            // Story 8.6: Check if this is a submit_guess response
            if (data.id && data.result && ('success' in data.result || 'error' in data.result)) {
                handleSubmitGuessResponse(data.result);
                return;
            }
        }

        // Handle message types
        if (data.type === 'connected') {
            // WebSocket connection confirmation (Story 4.5)
            console.log('✅ WebSocket connection confirmed:', data.data.connection_id);
        } else if (data.type === 'join_game_response') {
            // Handle join game response (backward compatibility)
            handleJoinGameResponse(data);
        } else if (data.type === 'beatsy/event') {
            // Handle broadcast events (Story 4.3 Task 5, Story 4.5 Task 1, Story 8.5 Task 6)
            if (data.event_type === 'player_joined') {
                handlePlayerJoined(data.data);
            } else if (data.event_type === 'round_started') {
                // Story 4.5 Task 1: Handle round_started event
                handleRoundStarted(data.data);
            } else if (data.event_type === 'round_ended') {
                // Story 8.7 & Story 9.1-9.3: Handle round_ended event
                handleRoundEnded(data.data);
            } else if (data.event_type === 'bet_placed') {
                // Story 8.4: Handle bet_placed event
                handleBetPlaced(data.data);
            } else {
                console.log('Unhandled event type:', data.event_type);
            }
        } else {
            console.log('Unhandled message type:', data.type);
        }

    } catch (error) {
        console.error('Error parsing WebSocket message:', error);
    }
}

/**
 * Handle join_game_response (AC-5, AC-6)
 * Story 4.2: Added duplicate name handling
 * Story 4.3: Added lobby initialization with player list (Task 2)
 */
function handleJoinGameResponse(data) {
    if (data.success) {
        // Success response (AC-5)
        console.log('Join game successful:', data);

        // Story 4.2: Check if name was adjusted due to duplicate
        if (data.name_adjusted) {
            const message = `Your name "${data.original_name}" was taken. You're registered as: "${data.player_name}"`;
            showNameNotification(message);
        }

        // Store session_id and player_name in localStorage
        localStorage.setItem('beatsy_session_id', data.session_id);
        localStorage.setItem('beatsy_player_name', data.player_name);

        // Story 8.6: Initialize gameState with player name
        gameState.playerName = data.player_name;

        console.log('Session stored:', {
            session_id: data.session_id.substring(0, 8) + '...',
            player_name: data.player_name
        });

        // Hide registration form
        document.getElementById('registration-view').classList.add('hidden');

        // Show lobby view
        document.getElementById('lobby-view').classList.remove('hidden');

        // Story 4.3 Task 2: Initialize lobby with current players
        initializeLobby(data.players || []);

    } else {
        // Error response (AC-6)
        const errorMessages = {
            'game_not_started': 'Game hasn\'t started yet. Check with the host.',
            'invalid_name': 'Invalid name. Please use letters and numbers only.',
            'server_error': 'Server error. Please try again.'
        };

        const message = errorMessages[data.error] || 'Failed to join. Please try again.';
        showError(message);
        resetJoinButton();
    }
}

/**
 * Story 11.4: Initialize lobby with existing player list using horizontal ticker
 * Includes defensive programming with try-catch and null checks
 * @param {Array} players - Array of player objects {name, joined_at}
 */
function initializeLobby(players) {
    try {
        console.log('Initializing lobby view');

        const ticker = document.getElementById('lobby-players-ticker');
        const countEl = document.getElementById('lobby-player-count');

        if (!ticker) {
            console.error('Lobby ticker element not found');
            return;
        }

        if (!countEl) {
            console.error('Lobby player count element not found');
            return;
        }

        // Get current player name for highlighting
        const currentPlayerName = localStorage.getItem('beatsy_player_name');

        // Clear ticker
        ticker.innerHTML = '';

        // Populate ticker with badges
        if (players && Array.isArray(players)) {
            players.forEach(player => {
                const isCurrent = player.name === currentPlayerName;
                const badge = createPlayerBadge(player.name, isCurrent);
                if (badge) {
                    ticker.appendChild(badge);
                }
            });
        }

        // Update count
        const count = players ? players.length : 0;
        countEl.textContent = `${count} player${count !== 1 ? 's' : ''} joined`;

        console.log(`Lobby initialized with ${count} players`);

    } catch (error) {
        console.error('Lobby initialization failed:', error);
    }
}

/**
 * Story 11.4: Create player badge element for horizontal ticker
 * Creates a styled badge for a player, with highlight for current player
 * @param {string} playerName - The player's name to display
 * @param {boolean} isCurrent - Whether this is the current player
 * @returns {HTMLSpanElement} The created badge element
 */
function createPlayerBadge(playerName, isCurrent) {
    if (!playerName) {
        console.error('createPlayerBadge called with empty playerName');
        return null;
    }

    const badge = document.createElement('span');
    badge.className = isCurrent
        ? 'px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-semibold border-2 border-blue-500'
        : 'px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm';
    badge.textContent = isCurrent ? `${playerName} (You)` : playerName;
    badge.dataset.playerName = playerName;  // For deduplication

    return badge;
}

/**
 * Story 4.3 Task 7: Update player count display
 * Updates the count text with proper singular/plural
 * @param {number} count - Number of players
 */
function updatePlayerCount(count) {
    const countEl = document.getElementById('lobby-player-count');
    if (!countEl) {
        console.error('Player count element not found');
        return;
    }

    const plural = count === 1 ? 'player' : 'players';
    countEl.textContent = `${count} ${plural} joined`;
}

/**
 * Story 11.4: Handle player_joined event from server with defensive programming
 * Adds new player badge to horizontal ticker in real-time
 * @param {Object} data - Event data {player_name, total_players}
 */
function handlePlayerJoined(data) {
    try {
        console.log('Player joined event:', data);

        // Only update if we're in lobby view
        const lobbyView = document.getElementById('lobby-view');
        if (!lobbyView || lobbyView.classList.contains('hidden')) {
            return;
        }

        const ticker = document.getElementById('lobby-players-ticker');
        const countEl = document.getElementById('lobby-player-count');

        if (!ticker || !countEl) {
            console.error('Lobby elements not found in handlePlayerJoined');
            return;
        }

        const newPlayerName = data.player_name || data.name;
        if (!newPlayerName) {
            console.error('Player name missing from event data');
            return;
        }

        // Check for duplicates
        const existing = ticker.querySelector(`[data-player-name="${newPlayerName}"]`);
        if (existing) {
            console.warn('Player badge already exists:', newPlayerName);
            return;
        }

        // Add new badge (not current player - new player joining)
        const badge = createPlayerBadge(newPlayerName, false);
        if (badge) {
            ticker.appendChild(badge);
        }

        // Update count
        const currentCount = ticker.children.length;
        countEl.textContent = `${currentCount} player${currentCount !== 1 ? 's' : ''} joined`;

        // Show toast notification
        showToast(`${newPlayerName} joined the lobby`);

    } catch (error) {
        console.error('handlePlayerJoined failed:', error);
    }
}

/**
 * Story 4.3 Task 11: Show toast notification
 * Displays a temporary notification at the top of the screen
 * @param {string} message - Message to display
 * @param {number} duration - Duration in ms (default 3000)
 */
function showToast(message, duration = 3000) {
    const toast = document.createElement('div');
    toast.className = 'fixed top-4 left-1/2 transform -translate-x-1/2 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 transition-opacity duration-500';
    toast.textContent = message;
    document.body.appendChild(toast);

    // Auto-hide after duration
    setTimeout(() => {
        toast.classList.add('opacity-0');
        setTimeout(() => toast.remove(), 500);
    }, duration);
}

/**
 * Story 8.1 Functions - To be added to ui-player.js
 * Insert these after showToast() and before hideLobbyView()
 */

/**
 * Story 8.1: Populate year dropdown selector
 * AC-1: Year dropdown populated from year_range
 * @param {number} minYear - Minimum year (e.g., 1950)
 * @param {number} maxYear - Maximum year (e.g., 2024)
 */
function populateYearSelector(minYear, maxYear) {
    const yearDropdown = document.getElementById('year-dropdown') || document.getElementById('year-selector');
    if (!yearDropdown) {
        console.warn('Year dropdown not found');
        return;
    }

    // Clear existing options
    yearDropdown.innerHTML = '';

    // Use DocumentFragment for performance optimization (single DOM operation)
    const fragment = document.createDocumentFragment();

    // Add placeholder option
    const placeholder = document.createElement('option');
    placeholder.value = '';
    placeholder.textContent = 'Select Year...';
    placeholder.disabled = true;
    placeholder.selected = true;
    fragment.appendChild(placeholder);

    // Generate options in descending order (2024 → 1950)
    for (let year = maxYear; year >= minYear; year--) {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        fragment.appendChild(option);
    }

    // Single DOM append operation
    yearDropdown.appendChild(fragment);

    console.log(`✓ Year dropdown populated (${minYear}-${maxYear})`);
}

/**
 * Story 8.2: Get the currently selected year from dropdown
 * @returns {number|null} Selected year as integer, or null if not selected
 */
function getSelectedYear() {
    const yearSelector = document.getElementById('year-dropdown') || document.getElementById('year-selector');
    if (!yearSelector || !yearSelector.value) {
        return null;
    }
    return parseInt(yearSelector.value);
}

/**
 * Story 8.2: Reset year selector to placeholder (no selection)
 */
function resetYearSelector() {
    const yearSelector = document.getElementById('year-dropdown') || document.getElementById('year-selector');
    if (yearSelector) {
        yearSelector.value = '';
        console.log('✓ Year selector reset');
    }
}

/**
 * Story 8.2: Validate that a year has been selected
 * @returns {boolean} True if year is selected, false otherwise
 */
function validateYearSelection() {
    return getSelectedYear() !== null;
}

/**
 * Story 8.2: Setup year selector change event listener
 * Provides visual confirmation and updates game state when year is selected
 */
function setupYearSelectorListener() {
    const yearSelector = document.getElementById('year-dropdown') || document.getElementById('year-selector');
    if (!yearSelector) {
        console.warn('Year selector not found for event listener setup');
        return;
    }

    yearSelector.addEventListener('change', (e) => {
        const selectedYear = parseInt(e.target.value);

        // Update visual state - green border for confirmation
        if (selectedYear) {
            e.target.classList.remove('border-gray-300');
            e.target.classList.add('border-green-500', 'border-2');

            // Update game state
            gameState.yearGuess = selectedYear;

            console.log(`✓ Year selected: ${selectedYear}`);
        } else {
            // Reset visual state if cleared
            e.target.classList.remove('border-green-500', 'border-2');
            e.target.classList.add('border-gray-300');
            gameState.yearGuess = null;
        }
    });

    console.log('✓ Year selector listener registered');
}

/**
 * Story 8.1: Display active round view with song metadata
 * AC-1: Layout includes album cover, song title, artist, timer, year dropdown, bet toggle, submit button
 * AC-4: Layout renders within 500ms of event receipt
 * @param {Object} roundData - Round data from round_started event
 */
function showActiveRound(roundData) {
    const startTime = performance.now();

    // Hide lobby, show active round
    document.getElementById('lobby-view').classList.add('hidden');
    const activeView = document.getElementById('active-round-view');
    activeView.classList.remove('hidden');

    // Populate song metadata - try both ID patterns
    const albumCover = document.getElementById('album-cover');
    const songTitle = document.getElementById('song-title');
    const songArtist = document.getElementById('song-artist') || document.getElementById('artist-name');

    if (albumCover && roundData.song.cover_url) {
        albumCover.src = roundData.song.cover_url;
        albumCover.alt = `${roundData.song.title} by ${roundData.song.artist}`;
    }

    if (songTitle) {
        songTitle.textContent = roundData.song.title || 'Unknown Title';
    }

    if (songArtist) {
        songArtist.textContent = roundData.song.artist || 'Unknown Artist';
    }

    // Initialize timer - try both ID patterns
    const timerDisplay = document.getElementById('timer-display') || document.getElementById('timer');
    if (timerDisplay) {
        timerDisplay.textContent = `${roundData.timer_duration}s`;
    }

    // Populate year dropdown
    if (roundData.year_range) {
        populateYearSelector(roundData.year_range.min, roundData.year_range.max);
    }

    // Reset bet toggle to OFF
    const betToggle = document.getElementById('bet-toggle');
    if (betToggle) {
        betToggle.dataset.betActive = 'false';
        betToggle.classList.remove('bg-red-600', 'bg-green-500', 'border-green-700', 'bg-yellow-400', 'border-yellow-600');
        betToggle.classList.add('bg-gray-300');
        betToggle.textContent = 'BET ON IT';
        betToggle.setAttribute('aria-pressed', 'false');
    }

    // Hide submission confirmation
    const submissionConf = document.getElementById('submission-confirmation');
    if (submissionConf) {
        submissionConf.classList.add('hidden');
    }

    // Unlock inputs
    unlockInputs();

    // Story 8.6: Setup submit button event listener
    const submitButton = document.getElementById('submit-guess');
    if (submitButton) {
        // Remove any existing listener to avoid duplicates
        submitButton.replaceWith(submitButton.cloneNode(true));
        const newSubmitButton = document.getElementById('submit-guess');
        newSubmitButton.addEventListener('click', onSubmitGuess);
        console.log('✓ Submit button event listener registered');
    }

    // Measure render time
    const renderTime = performance.now() - startTime;
    console.log(`Active round rendered in ${renderTime.toFixed(2)}ms`);

    if (renderTime > 500) {
        console.warn(`Render time exceeded 500ms target: ${renderTime.toFixed(2)}ms`);
    }
}

/**
 * Story 8.7 Task 2: Stop and clear active round timer
 * AC-4: Active round timer stops and clears
 * Prevents memory leaks from lingering intervals
 */
function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
        console.log('✓ Timer stopped and cleared');
    }

    // Clear timer display
    const timerDisplay = document.getElementById('timer');
    if (timerDisplay) {
        timerDisplay.textContent = '';
    }
}

/**
 * Story 8.7 Task 3: Hide active round view
 * AC-1, AC-2: Hide active round view with fade-out animation (<500ms)
 * @returns {Promise<void>} Resolves when fade-out completes
 */
function hideActiveRound() {
    return new Promise((resolve) => {
        const activeRoundView = document.getElementById('active-round-view');
        if (!activeRoundView) {
            console.warn('Active round view not found');
            resolve();
            return;
        }

        // Add fade-out transition (200ms)
        activeRoundView.classList.add('opacity-0', 'transition-opacity', 'duration-200');

        // Wait for transition to complete before hiding
        setTimeout(() => {
            activeRoundView.classList.add('hidden');
            console.log('✓ Active round view hidden');
            resolve();
        }, 200);
    });
}

/**
 * Story 8.7 Task 7: Cleanup active round state
 * AC-4: Reset all active round state variables and UI elements
 * Story 8.1 Task 5.3, 5.4: Clear album cover and reset form inputs
 */
function cleanupActiveRound() {
    // Story 8.1 Task 5.3: Clear album cover src (prevent flash on next round)
    const albumCover = document.getElementById('album-cover');
    if (albumCover) {
        albumCover.src = '';
    }

    // Reset year dropdown selection
    const yearDropdown = document.getElementById('year-selector');
    if (yearDropdown) {
        yearDropdown.value = '';
    }

    // Reset bet toggle to unchecked state
    const betToggle = document.getElementById('bet-toggle');
    if (betToggle) {
        betToggle.setAttribute('aria-pressed', 'false');
        betToggle.classList.remove('bg-green-500', 'border-green-700');
        betToggle.classList.add('bg-yellow-400', 'border-yellow-600');
        betToggle.textContent = '🎲 BET ON IT';
    }

    // Clear any submission confirmation messages
    const submissionConfirmation = document.getElementById('submission-confirmation');
    if (submissionConfirmation) {
        submissionConfirmation.classList.add('hidden');
    }

    // Clear any error messages from active round
    const errorMessage = document.getElementById('error-message');
    if (errorMessage) {
        errorMessage.classList.add('hidden');
    }

    console.log('✓ Active round state cleaned up');
}

/**
 * Story 8.7 Task 4: Placeholder for Epic 9 showResults function
 * Epic 9 Story 9-1 will fully implement this function
 * For now, just log the data and show a placeholder
 * @param {Object} resultsData - Round results {correct_year, results, leaderboard}
 */
function showResults(resultsData) {
    console.log('📊 Showing results view (Story 9.1-9.3):', resultsData);

    // Story 9.1-9.3: Call renderResultsView from ui-results.js
    renderResultsView(resultsData);
}

/**
 * Story 8.7 Task 9: Transition orchestrator
 * AC-2: Complete transition in <500ms
 * Coordinates: Stop timer → Hide active round → Show results → Cleanup
 * @param {Object} resultsData - Round results data from round_ended event
 */
async function transitionToResults(resultsData) {
    console.log('Round ended, transitioning to results');
    const transitionStart = performance.now();

    try {
        // Step 1: Stop timer (synchronous, <10ms)
        stopTimer();

        // Step 2: Hide active round view (async, 200ms fade-out)
        await hideActiveRound();

        // Step 3: Show results view (Epic 9 function)
        showResults(resultsData);

        // Step 4: Cleanup state
        cleanupActiveRound();

        // Measure transition time
        const transitionEnd = performance.now();
        const transitionTime = transitionEnd - transitionStart;
        console.log(`✓ Active Round → Results transition completed in ${transitionTime.toFixed(2)}ms`);

        if (transitionTime > 500) {
            console.warn(`⚠️ Transition time exceeded 500ms target (${transitionTime.toFixed(2)}ms)`);
        }

    } catch (error) {
        console.error('Error during transition to results:', error);
        // Fallback: Show error to user
        showError('Unable to display results. Please refresh.');
    }
}

/**
 * Story 8.7 Task 1: Handle round_ended WebSocket event
 * AC-1: Receive round_ended event and trigger transition to results
 * @param {Object} data - Event data {correct_year, results, leaderboard}
 */
function handleRoundEnded(data) {
    console.log('Round ended event received:', data);

    // Validate event payload structure (AC-1)
    if (!data.correct_year || !data.results || !data.leaderboard) {
        console.error('Round ended event missing required fields:', data);
        showError('Results unavailable, please refresh');
        return;
    }

    // Prevent duplicate transitions (edge case handling)
    const activeRoundView = document.getElementById('active-round-view');
    if (!activeRoundView || activeRoundView.classList.contains('hidden')) {
        console.log('Already transitioned to results, ignoring duplicate event');
        return;
    }

    // Clear betting indicators when round ends (Story 8.4)
    clearBettingIndicators();

    // Trigger transition to results
    transitionToResults(data);
}

// Story 8.1 lockInputs/unlockInputs moved to Story 8.6 section (lines 1563-1619) to consolidate implementation


/**
 * Story 4.5 Task 2: Hide lobby view on round start
 * AC-2: Lobby view hidden immediately when round_started event received
 */
function hideLobbyView() {
    const lobbyView = document.getElementById('lobby-view');
    if (lobbyView) {
        lobbyView.classList.add('hidden');
        console.log('✓ Lobby view hidden');
    }
}

/**
 * Story 4.5 Task 3: Show active round view with song metadata
 * AC-3: Active round view displayed with all elements
 * @param {Object} songMetadata - Song data {title, artist, album, cover_url}
 */
function showActiveRoundView(songMetadata) {
    const activeRoundView = document.getElementById('active-round-view');
    if (!activeRoundView) {
        console.error('Active round view not found');
        return;
    }

    // Display active round section
    activeRoundView.classList.remove('hidden');

    // Populate song info
    const albumCover = document.getElementById('album-cover');
    const songTitle = document.getElementById('song-title');
    const artistName = document.getElementById('artist-name');

    if (albumCover) {
        // AC-4: Lazy-load album cover with placeholder
        albumCover.src = songMetadata.cover_url || '';
        albumCover.alt = `${songMetadata.title} by ${songMetadata.artist}`;
    }

    if (songTitle) {
        songTitle.textContent = songMetadata.title || 'Unknown Title';
    }

    if (artistName) {
        artistName.textContent = songMetadata.artist || 'Unknown Artist';
    }

    // Ensure bet toggle is in default state
    const betToggle = document.getElementById('bet-toggle');
    if (betToggle) {
        betToggle.setAttribute('aria-pressed', 'false');
        betToggle.classList.remove('bg-green-500', 'border-green-700');
        betToggle.classList.add('bg-yellow-400', 'border-yellow-600');
        betToggle.textContent = '🎲 BET ON IT';
    }

    // Ensure submit button is enabled
    const submitButton = document.getElementById('submit-guess');
    if (submitButton) {
        submitButton.disabled = false;
    }

    console.log('✓ Active round view shown with song metadata');
}

/**
 * Story 8.5 Task 1: Update timer display
 * AC-2: Timer updates smoothly
 * AC-3: Calculated from server timestamp
 * AC-5: Changes color to red when < 10 seconds
 * AC-6: Accuracy within ±1 second
 * @param {number} startedAt - Server UTC timestamp (seconds)
 * @param {number} timerDuration - Round duration in seconds
 * @returns {number} Remaining seconds
 */
function updateTimer(startedAt, timerDuration) {
    const timerDisplay = document.getElementById('timer');
    if (!timerDisplay) {
        console.warn('Timer display not found');
        return 0;
    }

    // AC-3, AC-6: Use server timestamp for calculation (NOT client Date.now())
    const now = Date.now() / 1000; // Convert to seconds
    const elapsed = now - startedAt;
    const remaining = Math.max(0, timerDuration - elapsed);

    // AC-1: Display remaining seconds in "XXs" format
    if (remaining > 0) {
        timerDisplay.textContent = Math.ceil(remaining).toString();
    } else {
        timerDisplay.textContent = '0';
    }

    // AC-5: Change color to red when < 10 seconds for urgency
    if (remaining < 10 && remaining > 0) {
        timerDisplay.classList.remove('text-gray-800');
        timerDisplay.classList.add('text-red-600');
    } else {
        timerDisplay.classList.remove('text-red-600');
        timerDisplay.classList.add('text-gray-800');
    }

    return remaining;
}

/**
 * Story 4.5 Task 5 & 6: Initialize timer from server timestamp
 * Story 8.5 Task 3: Start countdown timer
 * AC-2: Timer updates every second
 * AC-4: Timer auto-locks inputs when reaching 0
 * @param {number} startedAt - Server UTC timestamp (seconds)
 * @param {number} timerDuration - Round duration in seconds
 */
function startTimer(startedAt, timerDuration) {
    // Clear any existing timer
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }

    const timerDisplay = document.getElementById('timer');
    if (!timerDisplay) {
        console.error('Timer display not found');
        return;
    }

    // Update timer display every 100ms for smooth countdown
    timerInterval = setInterval(() => {
        const remaining = updateTimer(startedAt, timerDuration);

        // AC-4: Auto-lock inputs when timer expires
        if (remaining <= 0) {
            clearInterval(timerInterval);
            timerInterval = null;
            // Story 8.6: Trigger auto-lock inputs when timer expires
            onTimerExpire();
        }
    }, 100);

    console.log(`✓ Timer started (duration: ${timerDuration}s, started: ${new Date(startedAt * 1000).toISOString()})`);
}

/**
 * Story 9.5 Task 5: Transition from results view to active round view
 * AC-5: Auto-transition when round_started event received
 * AC-5: Transition smooth and immediate (<500ms)
 * @param {Object} roundData - Round data from round_started event
 */
function transitionToActiveRound(roundData) {
    console.log('🎵 Transitioning from results to active round');
    const transitionStart = performance.now();

    // Hide results view (and waiting state automatically)
    const resultsView = document.getElementById('results-view');
    if (resultsView) {
        resultsView.classList.add('hidden');
    }

    // Show active round view
    const activeRoundView = document.getElementById('active-round-view');
    if (activeRoundView) {
        activeRoundView.classList.remove('hidden');
    }

    // Render active round (delegate to existing function)
    showActiveRoundView(roundData.song);

    // Initialize timer
    if (roundData.started_at && roundData.timer_duration) {
        startTimer(roundData.started_at, roundData.timer_duration);
    }

    // Populate year dropdown if year_range provided
    if (roundData.year_range) {
        populateYearSelector(roundData.year_range.min, roundData.year_range.max);
    }

    // Measure transition latency
    const transitionEnd = performance.now();
    const transitionTime = transitionEnd - transitionStart;
    console.log(`✓ Results → Active Round transition completed in ${transitionTime.toFixed(2)}ms`);

    if (transitionTime > 500) {
        console.warn(`⚠️ Transition time exceeded 500ms target (${transitionTime.toFixed(2)}ms)`);
    }
}

/**
 * Story 4.5 Task 1: Handle round_started WebSocket event
 * AC-1: Receive round_started event with song metadata and timer info
 * AC-4: Transition timing <500ms
 * Story 9.5: Enhanced to handle transition from results view
 * @param {Object} data - Event data {song, timer_duration, started_at, round_number}
 */
function handleRoundStarted(data) {
    console.log('🎵 Round started event received:', data);

    // Validate event structure
    if (!data.song || !data.timer_duration || !data.started_at) {
        console.error('Invalid round_started event structure:', data);
        return;
    }

    // Story 9.5: Check if we're transitioning from results view
    const resultsView = document.getElementById('results-view');
    const isFromResults = resultsView && !resultsView.classList.contains('hidden');

    if (isFromResults) {
        // Story 9.5 Task 5: Transition from results to active round
        transitionToActiveRound(data);
    } else {
        // Original Story 4.5: Transition from lobby to active round
        // AC-4: Log timestamp for transition timing measurement
        const transitionStart = performance.now();

        // Task 2: Hide lobby view immediately
        hideLobbyView();

        // Task 3: Show active round view with song metadata
        showActiveRoundView(data.song);

        // Task 5: Initialize timer from server timestamp
        startTimer(data.started_at, data.timer_duration);

        // AC-4: Log transition timing
        const transitionEnd = performance.now();
        const transitionTime = transitionEnd - transitionStart;
        console.log(`✓ Lobby → Active Round transition completed in ${transitionTime.toFixed(2)}ms`);

        if (transitionTime > 500) {
            console.warn(`⚠️ Transition time exceeded 500ms target (${transitionTime.toFixed(2)}ms)`);
        }
    }
}

/**
 * Reset join button to default state
 */
function resetJoinButton() {
    const joinButton = document.getElementById('join-button');
    if (joinButton) {
        joinButton.disabled = false;
        joinButton.textContent = 'Join Game';
    }
}

/**
 * Show error message (AC-6)
 */
function showError(message) {
    console.error('[ERROR]', message);

    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');

        // Auto-hide after 5 seconds
        setTimeout(() => {
            errorDiv.classList.add('hidden');
        }, 5000);
    }
}

/**
 * Story 4.2: Show name adjusted notification
 * Displays notification banner when player name is adjusted due to duplicate
 */
function showNameNotification(message) {
    console.log('[NAME NOTIFICATION]', message);

    const notificationDiv = document.getElementById('name-notification');
    const messageP = document.getElementById('notification-message');

    if (notificationDiv && messageP) {
        messageP.textContent = message;
        notificationDiv.classList.remove('hidden');

        // Auto-hide after 5 seconds
        setTimeout(() => {
            notificationDiv.classList.add('hidden');
        }, 5000);
    }
}

// ============================================================================
// Story 8.6: Guess Submission & Input Locking Functions
// ============================================================================

/**
 * Story 8.6 Task 1: Validate and submit guess
 * AC-1: Validates year selected before submission
 * AC-1: Sends WebSocket command with player_name, year_guess, bet_placed
 * AC-2: Locks inputs immediately (optimistic locking)
 * AC-3: Shows submission confirmation message
 * AC-6: Executes within 200ms
 */
function onSubmitGuess() {
    const startTime = performance.now();

    // Task 1.2: Validate year is selected
    const yearSelector = document.getElementById('year-selector');
    if (!yearSelector || !yearSelector.value) {
        // Task 1.3: Show error if no year selected
        showError('Please select a year');
        console.warn('Guess submission validation failed: No year selected');
        return;
    }

    // Task 1.5: Get current bet state
    const betToggle = document.getElementById('bet-toggle');
    const betPlaced = betToggle ? betToggle.getAttribute('aria-pressed') === 'true' : false;

    // Task 5.4: Check if already submitted (prevent duplicates)
    if (gameState.locked) {
        console.warn('Duplicate submission attempt prevented');
        return;
    }

    // Task 3: Lock inputs immediately (optimistic locking)
    lockInputs();
    gameState.locked = true;

    // Task 10.2: Show loading spinner briefly
    const submitButton = document.getElementById('submit-guess');
    if (submitButton) {
        submitButton.innerHTML = '<span class="inline-block animate-spin mr-2">⏳</span> Submitting...';
    }

    // Task 2: Send WebSocket command
    const playerName = localStorage.getItem('beatsy_player_name');
    const yearGuess = parseInt(yearSelector.value);

    const message = {
        type: 'beatsy/submit_guess',
        player_name: playerName,
        year_guess: yearGuess,
        bet_placed: betPlaced,
        submitted_at: Date.now(),
        id: Date.now()  // HA WebSocket API requires id field
    };

    console.log('Sending guess submission:', { player: playerName, year: yearGuess, bet: betPlaced });

    // Task 2.4: Send via WebSocket
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        showError('Connection lost. Please refresh the page.');
        unlockInputs();
        gameState.locked = false;
        return;
    }

    ws.send(JSON.stringify(message));

    // Task 4: Show submission confirmation
    showSubmissionConfirmation();

    // AC-6: Log execution time
    const executionTime = performance.now() - startTime;
    console.log(`✓ Guess submission completed in ${executionTime.toFixed(2)}ms`);

    if (executionTime > 200) {
        console.warn(`⚠️ Submission exceeded 200ms target (${executionTime.toFixed(2)}ms)`);
    }
}

/**
 * Story 8.6 Task 3: Lock all input controls
 * AC-2: Disables year dropdown, bet button, submit button
 * AC-6: Executes within 200ms (synchronous DOM update)
 * AC-2: Adds visual disabled state
 */
function lockInputs() {
    // Update game state
    gameState.locked = true;

    // Task 3.2: Disable year dropdown
    const yearSelector = document.getElementById('year-selector');
    if (yearSelector) {
        yearSelector.disabled = true;
    }

    // Task 3.3: Disable bet button
    const betToggle = document.getElementById('bet-toggle');
    if (betToggle) {
        betToggle.disabled = true;
        // Visual feedback for disabled bet toggle
        betToggle.classList.add('opacity-50', 'cursor-not-allowed');
    }

    // Task 3.4: Disable submit button
    const submitButton = document.getElementById('submit-guess');
    if (submitButton) {
        submitButton.disabled = true;
        // Task 3.5: Add visual disabled state
        submitButton.classList.add('opacity-50', 'cursor-not-allowed');
    }

    console.log('✓ Inputs locked');
}

/**
 * Story 8.6 Task 7: Unlock input controls
 * AC-4: Re-enables all inputs for error recovery
 * Only called for recoverable errors (not late submissions)
 */
function unlockInputs() {
    // Task 7.5: Reset submission flag
    gameState.locked = false;

    // Task 7.2: Enable all inputs
    const yearSelector = document.getElementById('year-selector');
    if (yearSelector) {
        yearSelector.disabled = false;
    }

    const betToggle = document.getElementById('bet-toggle');
    if (betToggle) {
        betToggle.disabled = false;
        // Remove disabled visual feedback
        betToggle.classList.remove('opacity-50', 'cursor-not-allowed');
    }

    const submitButton = document.getElementById('submit-guess');
    if (submitButton) {
        submitButton.disabled = false;
        // Task 7.3: Remove disabled styling
        submitButton.classList.remove('opacity-50', 'cursor-not-allowed');
        submitButton.textContent = 'Submit Guess';
    }

    console.log('✓ Inputs unlocked');
}

/**
 * Story 8.6 Task 4: Display submission confirmation
 * AC-3: Shows "Guess submitted! Waiting for results..." message
 * Task 4.3: Prominent green styling with checkmark
 * Task 4.5: Mobile-friendly display
 */
function showSubmissionConfirmation() {
    const confirmationDiv = document.getElementById('submission-confirmation');
    if (confirmationDiv) {
        // Task 4.2 & 4.3: Display confirmation message with styling
        confirmationDiv.innerHTML = '✓ Guess submitted! Waiting for results...';
        confirmationDiv.classList.remove('hidden');
        confirmationDiv.classList.add('text-green-600', 'font-semibold', 'text-center', 'mt-4', 'p-3', 'bg-green-100', 'rounded-md');
    }

    // Hide submit button (replaced by confirmation)
    const submitButton = document.getElementById('submit-guess');
    if (submitButton) {
        submitButton.classList.add('hidden');
    }

    console.log('✓ Submission confirmation displayed');
}

/**
 * Story 8.6 Task 5 & 6: Handle submission response from server
 * Processes both success and error responses
 * @param {Object} data - Server response {success, error}
 */
function handleSubmitGuessResponse(data) {
    if (data.success) {
        // Task 5.2 & 5.3: Success - keep locked, log success
        console.log('✓ Guess submitted successfully');
        // Inputs already locked and confirmation shown optimistically
    } else {
        // Task 6: Handle errors
        // Error format: {code: 'error_code', message: 'Error message'}
        const errorCode = data.error?.code || '';
        const errorMessage = data.error?.message || data.error || 'Submission failed';

        if (errorCode === 'timer_expired' || errorMessage.includes('timer') || errorMessage.includes('expired') || errorMessage.includes('Too late')) {
            // Task 6.2: Late submission error (AC-5)
            showError('Too late! Timer expired.');
            // Task 6.3: Keep inputs locked (don't allow retry)
            console.log('Late submission rejected by server');
        } else if (errorCode === 'already_submitted' || errorMessage.includes('already submitted')) {
            // Duplicate submission
            showError('You have already submitted a guess for this round');
            console.log('Duplicate guess rejected by server');
        } else {
            // Other errors - allow retry
            showError(typeof errorMessage === 'string' ? errorMessage : 'Submission failed');
            unlockInputs();
            const confirmationDiv = document.getElementById('submission-confirmation');
            if (confirmationDiv) {
                confirmationDiv.classList.add('hidden');
            }
            const submitButton = document.getElementById('submit-guess');
            if (submitButton) {
                submitButton.classList.remove('hidden');
            }
        }
    }
}

/**
 * Story 8.6 Task 8: Handle timer expiration auto-lock
 * AC-4: Timer continues for other players
 * AC-5: Prevents submission after timer expires
 * Called from startTimer() when remaining time reaches 0
 */
function onTimerExpire() {
    console.log('⏰ Timer expired');

    // Task 8.1: Lock inputs automatically
    lockInputs();

    // Task 8.2: Show appropriate message
    if (gameState.locked) {
        // Task 8.3: Already submitted - keep confirmation visible
        console.log('Timer expired - guess already submitted');
    } else {
        // Task 8.2: Not submitted - show time's up message
        const confirmationDiv = document.getElementById('submission-confirmation');
        if (confirmationDiv) {
            confirmationDiv.innerHTML = '⏱️ Time\'s up! Waiting for results...';
            confirmationDiv.classList.remove('hidden');
            confirmationDiv.classList.add('text-orange-600', 'font-semibold', 'text-center', 'mt-4', 'p-3', 'bg-orange-100', 'rounded-md');
        }

        // Hide submit button
        const submitButton = document.getElementById('submit-guess');
        if (submitButton) {
            submitButton.classList.add('hidden');
        }

        gameState.locked = true;
        console.log('Timer expired - inputs locked, no guess submitted');
    }
}

/**
 * Story 8.5 Task 6: Handle round_ended event
 * AC-2: Timer stops cleanly on round end
 * Stops the timer when round ends and clears state
 * @param {Object} data - Event data (results, leaderboard, etc.)
 */

/**
 * Main initialization - runs when DOM is fully loaded
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('=== Beatsy Player UI Starting (Story 4.1) ===');
    initPlayerUI();
    console.log('=== Beatsy Player UI Ready ===');
});

/**
 * Export functions for testing
 */

// Story 8.3 lockInputs/unlockInputs consolidated into Story 8.6 implementation (lines 1563-1619)

/**
 * Story 8.3 Task 2: Handle bet toggle button click.
 * Toggles bet state and sends WebSocket command.
 * AC-1: Button changes state visually (gray → red, label changes)
 * AC-3: Toggle bet on/off before submitting
 * AC-4: Send WebSocket command beatsy/place_bet
 * AC-5: Visual feedback instant (< 50ms perceived delay)
 */
function onBetToggle() {
    const startTime = performance.now();

    const button = document.getElementById('bet-toggle');
    if (!button) {
        console.error('Bet toggle button not found');
        return;
    }

    // Check if inputs are locked
    if (gameState.locked || button.disabled) {
        console.log('Bet toggle disabled (inputs locked)');
        return;
    }

    const currentState = button.dataset.betActive === 'true';
    const newState = !currentState;

    // Update button state
    button.dataset.betActive = newState.toString();
    button.setAttribute('aria-pressed', newState.toString());

    // Update visual appearance
    if (newState) {
        // Bet ON: Red background, "BETTING ✓" text
        button.classList.remove('bg-gray-300', 'hover:bg-gray-400');
        button.classList.add('bg-red-600', 'hover:bg-red-700', 'text-white');
        button.textContent = 'BETTING ✓';
    } else {
        // Bet OFF: Gray background, "BET ON IT" text
        button.classList.remove('bg-red-600', 'hover:bg-red-700', 'text-white');
        button.classList.add('bg-gray-300', 'hover:bg-gray-400');
        button.textContent = 'BET ON IT';
    }

    // Update client-side state
    gameState.betActive = newState;

    // Send WebSocket command to broadcast to all players
    placeBet(newState);

    // Story 8.4: Update local player's bet status in betting indicators
    updateLocalPlayerBetStatus(newState);

    const duration = performance.now() - startTime;
    console.log(`Bet toggled: ${newState ? 'ON' : 'OFF'} (${duration.toFixed(2)}ms)`);

    if (duration > 50) {
        console.warn(`⚠️ Bet toggle exceeded 50ms target: ${duration.toFixed(2)}ms`);
    }
}

/**
 * Story 8.3 Task 3: Send place_bet WebSocket command.
 * AC-4: WebSocket command beatsy/place_bet is sent
 * @param {boolean} betActive - True if betting, false if cancelled
 */
function placeBet(betActive) {
    const playerName = gameState.playerName;

    if (!playerName) {
        console.error('Cannot place bet: Player name not set');
        return;
    }

    if (!ws || ws.readyState !== WebSocket.OPEN) {
        console.error('Cannot place bet: WebSocket not connected');
        return;
    }

    const message = {
        type: 'beatsy/place_bet',
        player_name: playerName,
        bet_active: betActive
    };

    try {
        ws.send(JSON.stringify(message));
        console.log('Place bet command sent', message);
    } catch (error) {
        console.error('Failed to send place_bet command', error);
        // Don't revert visual state - player will see their bet, broadcast will retry on reconnect
    }
}

/**
 * Story 8.3: Get current bet state.
 * @returns {boolean} - True if betting, false otherwise
 */
function getBetState() {
    const button = document.getElementById('bet-toggle');
    if (!button) return false;
    return button.dataset.betActive === 'true';
}

/**
 * Story 8.3: Reset bet toggle to OFF state.
 * Called when new round starts.
 */
function resetBetToggle() {
    const button = document.getElementById('bet-toggle');
    if (!button) {
        console.warn('Bet toggle button not found for reset');
        return;
    }

    button.dataset.betActive = 'false';
    button.setAttribute('aria-pressed', 'false');
    button.classList.remove('bg-red-600', 'hover:bg-red-700', 'text-white');
    button.classList.add('bg-gray-300', 'hover:bg-gray-400');
    button.textContent = 'BET ON IT';

    // Update client-side state
    gameState.betActive = false;

    console.log('✓ Bet toggle reset to OFF');
}

// ============================================================================
// Story 8.4: Live Bet Indicators (Who's Betting)
// ============================================================================

// Story 8.4: Client-side array to track betting players
const bettingPlayers = [];

/**
 * Story 8.4: Add a player to the betting list
 * AC-1: Player names appear in "Betting Now" list when they place bets
 * @param {string} playerName - Name of player who placed bet
 */
function addBettingPlayer(playerName) {
    if (!playerName) return;

    // Prevent duplicates
    if (!bettingPlayers.includes(playerName)) {
        bettingPlayers.push(playerName);
        console.log(`✓ Added ${playerName} to betting list`);
        updateBettingIndicators();
    }
}

/**
 * Story 8.4: Remove a player from the betting list
 * @param {string} playerName - Name of player who removed bet
 */
function removeBettingPlayer(playerName) {
    const index = bettingPlayers.indexOf(playerName);
    if (index !== -1) {
        bettingPlayers.splice(index, 1);
        console.log(`✓ Removed ${playerName} from betting list`);
        updateBettingIndicators();
    }
}

/**
 * Story 8.4: Update the betting indicators UI
 * AC-2: Updates appear within 500ms of bet placement
 * AC-3: Own bet status included and highlighted
 * AC-5: Shows first 10 players + "and N more" for overflow
 */
function updateBettingIndicators() {
    const startTime = performance.now();

    const listEl = document.getElementById('betting-players-list');
    if (!listEl) {
        console.warn('Betting players list element not found');
        return;
    }

    // AC-1: Show "None" when no players betting
    if (bettingPlayers.length === 0) {
        listEl.innerHTML = '<span class="text-gray-500">None</span>';
        return;
    }

    const currentPlayer = localStorage.getItem('beatsy_player_name');
    const maxDisplay = 10;

    // AC-5: Handle overflow (more than 10 players)
    if (bettingPlayers.length > maxDisplay) {
        const displayPlayers = bettingPlayers.slice(0, maxDisplay);
        const overflow = bettingPlayers.length - maxDisplay;

        let html = displayPlayers.map(name => {
            // AC-3: Highlight current player in bold blue
            if (name === currentPlayer) {
                return `<strong class="text-blue-700">${name}</strong>`;
            }
            return `<span class="text-blue-600">${name}</span>`;
        }).join(', ');

        html += `, <span class="text-gray-600">and ${overflow} more</span>`;
        listEl.innerHTML = html;
    } else {
        // Show all players
        const html = bettingPlayers.map(name => {
            // AC-3: Highlight current player in bold blue
            if (name === currentPlayer) {
                return `<strong class="text-blue-700">${name}</strong>`;
            }
            return `<span class="text-blue-600">${name}</span>`;
        }).join(', ');

        listEl.innerHTML = html;
    }

    // AC-2: Performance logging
    const updateTime = performance.now() - startTime;
    console.log(`✓ Betting indicators updated in ${updateTime.toFixed(2)}ms`);

    if (updateTime > 500) {
        console.warn(`⚠️ Betting indicators update exceeded 500ms: ${updateTime.toFixed(2)}ms`);
    }
}

/**
 * Story 8.4: Clear all betting indicators
 * AC-4: List cleared on round end
 */
function clearBettingIndicators() {
    bettingPlayers.length = 0; // Clear array
    updateBettingIndicators(); // Update UI to show "None"
    console.log('✓ Betting indicators cleared');
}

/**
 * Story 8.4: Handle bet_placed WebSocket event
 * Called from handleWebSocketMessage when bet_placed event received
 * @param {Object} data - Event data {player_name, bet_active}
 */
function handleBetPlaced(data) {
    const { player_name, bet_active } = data;

    if (!player_name) {
        console.warn('bet_placed event missing player_name');
        return;
    }

    console.log(`Bet placed event: ${player_name} - ${bet_active ? 'ON' : 'OFF'}`);

    if (bet_active) {
        addBettingPlayer(player_name);
    } else {
        removeBettingPlayer(player_name);
    }
}

/**
 * Story 8.4: Update local player's bet status in indicators
 * Called from Story 8.3 onBetToggle to update current player's status
 * @param {boolean} betActive - True if bet is ON, false if OFF
 */
function updateLocalPlayerBetStatus(betActive) {
    const playerName = localStorage.getItem('beatsy_player_name');
    if (!playerName) {
        console.warn('Cannot update local bet status: player name not found');
        return;
    }

    if (betActive) {
        addBettingPlayer(playerName);
    } else {
        removeBettingPlayer(playerName);
    }
}


export {
    initPlayerUI,
    connectWebSocket,
    joinGame,
    handleWebSocketMessage,
    handleRoundStarted,
    hideLobbyView,
    showActiveRoundView,
    startTimer,
    showError,
    showNameNotification,
    // Story 8.2: Year dropdown selector
    populateYearSelector,
    getSelectedYear,
    resetYearSelector,
    validateYearSelection,
    // Story 8.4: Betting indicators
    addBettingPlayer,
    removeBettingPlayer,
    updateBettingIndicators,
    clearBettingIndicators,
    updateLocalPlayerBetStatus,
    // Story 8.7: Results transition functions
    stopTimer,
    hideActiveRound,
    cleanupActiveRound,
    showResults,
    transitionToResults,
    handleRoundEnded,
    // Story 8.3: Bet toggle functions
    onBetToggle,
    placeBet,
    getBetState,
    resetBetToggle,
    lockInputs,
    unlockInputs,
    // Story 8.6: Guess submission functions
    onSubmitGuess,
    showSubmissionConfirmation,
    handleSubmitGuessResponse,
    onTimerExpire
};

// Duplicate updateLocalPlayerBetStatus() removed - using version from Story 8.4 (lines 2056-2068)
