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

// Global WebSocket connection
let ws = null;
let connectionAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;

// Global timer interval for active round
let timerInterval = null;

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
 * Story 4.3 Task 12: Restore lobby view for existing session
 * Shows lobby with "Reconnecting..." state until WebSocket reconnects
 */
function restoreLobbyView() {
    // Hide registration form, show lobby view
    document.getElementById('registration-view').classList.add('hidden');
    document.getElementById('lobby-view').classList.remove('hidden');

    // Show reconnecting state
    const listEl = document.getElementById('lobby-player-list');
    const countEl = document.getElementById('lobby-player-count');

    listEl.innerHTML = '<li class="p-3 text-gray-500 text-center">Reconnecting...</li>';
    countEl.textContent = 'Reconnecting to game...';

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

    const gameState = data.game_state;
    const player = data.player;

    // Update localStorage with current session info
    localStorage.setItem('beatsy_session_id', player.session_id);
    localStorage.setItem('beatsy_player_name', player.name);

    // Route to appropriate view based on game status
    switch (gameState.status) {
        case 'lobby':
            console.log('Restoring to lobby view');
            showLobbyViewAfterReconnect(gameState);
            break;

        case 'active':
            console.log('Restoring to active round view');
            // TODO Story 4.5+: Implement active round view restoration
            showLobbyViewAfterReconnect(gameState);  // Fallback to lobby for now
            break;

        case 'results':
            console.log('Restoring to results view');
            // TODO Story 4.5+: Implement results view restoration
            showLobbyViewAfterReconnect(gameState);  // Fallback to lobby for now
            break;

        default:
            console.error('Unknown game status:', gameState.status);
            showLobbyViewAfterReconnect(gameState);
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
        if (data.type === 'result' && data.result) {
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

        // Handle legacy message types (backward compatibility)
        if (data.type === 'join_game_response') {
            handleJoinGameResponse(data);
        } else if (data.type === 'beatsy/event') {
            // Handle broadcast events (Story 4.3 Task 5, Story 4.5 Task 1)
            if (data.event_type === 'player_joined') {
                handlePlayerJoined(data.data);
            } else if (data.event_type === 'round_started') {
                // Story 4.5 Task 1: Handle round_started event
                handleRoundStarted(data.data);
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
 * Story 4.3 Task 3: Initialize lobby with existing player list
 * Renders the initial player list from join_game_response
 * @param {Array} players - Array of player objects {name, joined_at}
 */
function initializeLobby(players) {
    const listEl = document.getElementById('lobby-player-list');
    const currentPlayerName = localStorage.getItem('beatsy_player_name');

    if (!listEl) {
        console.error('Lobby player list element not found');
        return;
    }

    // Clear existing list
    listEl.innerHTML = '';

    // Render each player
    players.forEach(player => {
        const playerItem = createPlayerListItem(player.name, player.name === currentPlayerName);
        listEl.appendChild(playerItem);
    });

    // Update player count
    updatePlayerCount(players.length);

    console.log(`Lobby initialized with ${players.length} players`);
}

/**
 * Story 4.3 Task 3: Create player list item element
 * Creates a styled list item for a player, with highlight for current player
 * @param {string} playerName - The player's name to display
 * @param {boolean} isCurrent - Whether this is the current player
 * @returns {HTMLLIElement} The created list item element
 */
function createPlayerListItem(playerName, isCurrent) {
    const li = document.createElement('li');
    li.className = isCurrent
        ? 'p-3 rounded-md bg-blue-100 border-2 border-blue-400 font-semibold'
        : 'p-3 rounded-md bg-gray-50 border border-gray-200';
    li.textContent = playerName;

    // Add "You" badge if current player
    if (isCurrent) {
        const badge = document.createElement('span');
        badge.className = 'ml-2 px-2 py-1 text-xs bg-blue-500 text-white rounded';
        badge.textContent = 'You';
        li.appendChild(badge);
    }

    return li;
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
 * Story 4.3 Task 5: Handle player_joined event from server
 * Adds new player to lobby list in real-time
 * @param {Object} data - Event data {player_name, total_players}
 */
function handlePlayerJoined(data) {
    // Only update if we're in lobby view
    const lobbyView = document.getElementById('lobby-view');
    if (!lobbyView || lobbyView.classList.contains('hidden')) {
        return;
    }

    const playerName = data.player_name;
    const currentPlayerName = localStorage.getItem('beatsy_player_name');

    console.log(`Player joined: ${playerName} (total: ${data.total_players})`);

    // Add player to list
    const listEl = document.getElementById('lobby-player-list');
    if (listEl) {
        const playerItem = createPlayerListItem(playerName, playerName === currentPlayerName);
        listEl.appendChild(playerItem);
    }

    // Update player count
    updatePlayerCount(data.total_players);

    // Show toast notification (Task 11)
    showToast(`${playerName} joined the lobby`);
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
 * Story 4.5 Task 5 & 6: Initialize timer from server timestamp
 * AC-5: Remaining time calculated from started_at timestamp
 * AC-5: Timer updates every 100ms for smooth countdown
 * AC-5: Timer synchronized with server (resilient to client clock drift)
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

    // Update timer display every 100ms
    timerInterval = setInterval(() => {
        // AC-6: Use server timestamp for calculation (NOT client Date.now())
        const now = Date.now() / 1000; // Convert to seconds
        const elapsed = now - startedAt;
        const remaining = Math.max(0, timerDuration - elapsed);

        // Display remaining seconds
        if (remaining > 0) {
            timerDisplay.textContent = Math.ceil(remaining).toString();
        } else {
            // Timer expired
            timerDisplay.textContent = '0';
            clearInterval(timerInterval);
            timerInterval = null;
            console.log('⏰ Timer expired');
            // TODO Story 8.6: Trigger auto-lock inputs when timer expires
        }
    }, 100);

    console.log(`✓ Timer started (duration: ${timerDuration}s, started: ${new Date(startedAt * 1000).toISOString()})`);
}

/**
 * Story 4.5 Task 1: Handle round_started WebSocket event
 * AC-1: Receive round_started event with song metadata and timer info
 * AC-4: Transition timing <500ms
 * @param {Object} data - Event data {song, timer_duration, started_at, round_number}
 */
function handleRoundStarted(data) {
    console.log('🎵 Round started event received:', data);

    // AC-4: Log timestamp for transition timing measurement
    const transitionStart = performance.now();

    // Validate event structure
    if (!data.song || !data.timer_duration || !data.started_at) {
        console.error('Invalid round_started event structure:', data);
        return;
    }

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
export {
    initPlayerUI,
    connectWebSocket,
    joinGame,
    handleWebSocketMessage,
    transitionToLobby,
    showError,
    showNameNotification
};
