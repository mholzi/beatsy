/**
 * Beatsy Admin UI - JavaScript Initialization
 * ES6 module for admin interface initialization
 * Mobile-first, vanilla JavaScript (no frameworks)
 */

/**
 * Initialize admin UI on DOM ready
 */
function initAdminUI() {
    console.log('Beatsy Admin UI initialized');
    console.log('Version: 1.0.0');
    console.log('Environment:', {
        userAgent: navigator.userAgent,
        viewportWidth: window.innerWidth,
        viewportHeight: window.innerHeight,
        devicePixelRatio: window.devicePixelRatio
    });

    // Verify all critical elements are present
    verifyPageStructure();

    // Setup placeholder event listeners (will be implemented in later stories)
    setupPlaceholderListeners();

    // Story 3.2: Load media players on page initialization
    loadMediaPlayers();

    // Story 3.3: Load playlists on page initialization
    loadPlaylists();

    // Story 3.4: Load game settings from localStorage and setup event listeners
    loadSettingsFromLocalStorage();
    setupGameSettingsListeners();

    // Story 3.5: Initialize Start Game button state
    updateStartGameButton();

    // Story 3.7: Initialize game status display
    initGameStatus();

    // Log successful initialization
    console.log('DOM ready - All sections loaded successfully');
}

/**
 * Global game configuration state
 * Story 3.2: Stores media player selection
 * Story 3.3: Stores playlist selection
 * Story 3.4: Stores game settings
 */
const gameConfig = {
    mediaPlayer: null,      // Selected entity_id (e.g., "media_player.spotify_living_room")
    playlist: null,         // Playlist ID
    timerDuration: 30,      // Timer duration (10-120 seconds)
    yearRangeMin: 1950,     // Year range minimum
    yearRangeMax: 2024,     // Year range maximum
    exactPoints: 10,        // Points for exact match
    closePoints: 5,         // Points for ±2 years
    nearPoints: 2,          // Points for ±5 years
    betMultiplier: 2        // Bet multiplier (1-10x)
};

/**
 * Load available Spotify media players from backend API
 * Story 3.2: Fetch media players and populate dropdown
 */
async function loadMediaPlayers() {
    const dropdown = document.getElementById('media-player');
    const errorElement = document.getElementById('media-player-error');
    const checkmarkElement = document.getElementById('media-player-check');

    try {
        console.log('Fetching media players from API...');

        const response = await fetch('/api/beatsy/api/media_players');
        const data = await response.json();

        if (response.ok && data.players && data.players.length > 0) {
            console.log(`Successfully fetched ${data.players.length} media player(s)`);
            populateMediaPlayerDropdown(data.players);

            // Hide error message if previously shown
            errorElement.classList.add('hidden');
        } else if (response.status === 404 || (data.players && data.players.length === 0)) {
            // No players found
            console.warn('No Spotify media players found');
            showMediaPlayerError(data.message || 'No Spotify media players detected. Please configure Spotify integration in Home Assistant.');
            dropdown.innerHTML = '<option value="">No Spotify players found</option>';
            dropdown.disabled = true;
            checkmarkElement.classList.add('hidden');
        } else {
            // Other error
            console.error('Failed to load media players:', data);
            showMediaPlayerError(data.message || 'Failed to load media players. Please try again.');
            dropdown.disabled = true;
            checkmarkElement.classList.add('hidden');
        }
    } catch (error) {
        console.error('Error fetching media players:', error);
        showMediaPlayerError('Connection error. Please check your network and try again.');
        dropdown.innerHTML = '<option value="">Connection error</option>';
        dropdown.disabled = true;
    }
}

/**
 * Populate media player dropdown with fetched players
 * Story 3.2: AC-2, AC-4
 */
function populateMediaPlayerDropdown(players) {
    const dropdown = document.getElementById('media-player');
    const checkmarkElement = document.getElementById('media-player-check');

    // Clear loading state
    dropdown.innerHTML = '';

    // Add options with friendly names
    players.forEach(player => {
        const option = document.createElement('option');
        option.value = player.entity_id;
        option.textContent = player.friendly_name;

        // Add state indicator for context (idle/playing)
        if (player.state && player.state !== 'idle') {
            option.textContent += ` (${player.state})`;
        }

        dropdown.appendChild(option);
    });

    // Enable dropdown for selection
    dropdown.disabled = false;
    dropdown.classList.remove('bg-gray-100', 'cursor-not-allowed');
    dropdown.classList.add('cursor-pointer');

    // Restore saved selection from localStorage (Story 3.2: AC-4)
    const savedPlayer = localStorage.getItem('beatsy_media_player');
    if (savedPlayer) {
        // Check if saved player exists in current list
        const playerExists = players.some(p => p.entity_id === savedPlayer);
        if (playerExists) {
            dropdown.value = savedPlayer;
            gameConfig.mediaPlayer = savedPlayer;
            console.log('Restored saved media player selection:', savedPlayer);

            // Show visual feedback for restored selection
            updateVisualFeedback(dropdown, true);
        } else {
            // Saved player no longer available, select first
            dropdown.selectedIndex = 0;
            gameConfig.mediaPlayer = players[0].entity_id;
            localStorage.setItem('beatsy_media_player', players[0].entity_id);
            console.log('Saved player not found, selected first player:', players[0].entity_id);

            // Show visual feedback
            updateVisualFeedback(dropdown, true);
        }
    } else {
        // No saved selection, select first player by default
        dropdown.selectedIndex = 0;
        gameConfig.mediaPlayer = players[0].entity_id;
        localStorage.setItem('beatsy_media_player', players[0].entity_id);
        console.log('No saved selection, selected first player:', players[0].entity_id);

        // Show visual feedback
        updateVisualFeedback(dropdown, true);
    }
}

/**
 * Show error message for media player loading failures
 * Story 3.2: AC-3
 */
function showMediaPlayerError(message) {
    const errorElement = document.getElementById('media-player-error');
    errorElement.textContent = message;
    errorElement.classList.remove('hidden');
}

/**
 * Handle media player selection change
 * Story 3.2: AC-4 (Save selection), AC-5 (Visual feedback)
 */
function handleMediaPlayerChange(event) {
    const selectedEntityId = event.target.value;

    if (selectedEntityId && selectedEntityId !== '') {
        // Save to state
        gameConfig.mediaPlayer = selectedEntityId;

        // Save to localStorage for persistence
        localStorage.setItem('beatsy_media_player', selectedEntityId);

        console.log('Media player selected:', selectedEntityId);

        // Update visual feedback
        updateVisualFeedback(event.target, true);

        // Update Start Game button state (partial - other fields needed too)
        updateStartGameButtonState();
    } else {
        // No valid selection
        gameConfig.mediaPlayer = null;
        updateVisualFeedback(event.target, false);
        updateStartGameButtonState();
    }
}

/**
 * Update visual feedback for media player dropdown
 * Story 3.2: AC-5 (Green border, checkmark icon)
 */
function updateVisualFeedback(dropdown, isValid) {
    const checkmarkElement = document.getElementById('media-player-check');

    if (isValid) {
        // Valid selection: Green border + checkmark
        dropdown.classList.remove('border-gray-300', 'border-red-500');
        dropdown.classList.add('border-green-500');
        checkmarkElement.classList.remove('hidden');
    } else {
        // Invalid/no selection: Red border, no checkmark
        dropdown.classList.remove('border-gray-300', 'border-green-500');
        dropdown.classList.add('border-red-500');
        checkmarkElement.classList.add('hidden');
    }
}

/**
 * Validate if all requirements are met to enable Start Game button
 * Story 3.5: AC-1 (Complete validation)
 * Returns: boolean (true if all valid, false otherwise)
 */
function validateStartGameReady() {
    // Check media player selected
    const isMediaPlayerSelected = gameConfig.mediaPlayer !== null && gameConfig.mediaPlayer !== '';

    // Check playlist selected
    const isPlaylistSelected = gameConfig.playlist !== null && gameConfig.playlist !== '';

    // Check all game settings are valid
    const settingsValidation = validateGameSettings();
    const areSettingsValid = settingsValidation.valid;

    // Log validation state for debugging
    console.log('Start Game validation:', {
        mediaPlayer: isMediaPlayerSelected,
        playlist: isPlaylistSelected,
        settings: areSettingsValid,
        allValid: isMediaPlayerSelected && isPlaylistSelected && areSettingsValid
    });

    return isMediaPlayerSelected && isPlaylistSelected && areSettingsValid;
}

/**
 * Update Start Game button enabled state and tooltip
 * Story 3.5: AC-1 (Enable/disable based on validation)
 */
function updateStartGameButton() {
    const startGameBtn = document.getElementById('start-game-btn');
    if (!startGameBtn) return;

    const isReady = validateStartGameReady();

    if (isReady) {
        // Enable button
        startGameBtn.disabled = false;
        startGameBtn.setAttribute('aria-disabled', 'false');
        startGameBtn.title = 'Click to start a new game session';
        console.log('✓ Start Game button ENABLED - all requirements met');
    } else {
        // Disable button with appropriate tooltip
        startGameBtn.disabled = true;
        startGameBtn.setAttribute('aria-disabled', 'true');

        // Determine specific reason for disabled state
        if (!gameConfig.mediaPlayer) {
            startGameBtn.title = 'Select a media player first';
        } else if (!gameConfig.playlist) {
            startGameBtn.title = 'Select a playlist first';
        } else {
            startGameBtn.title = 'Complete configuration first (check for validation errors)';
        }

        console.log('Start Game button disabled:', startGameBtn.title);
    }
}

/**
 * Legacy alias for backwards compatibility
 * Story 3.2 and 3.4 call this, now points to new function
 */
function updateStartGameButtonState() {
    updateStartGameButton();
}

/**
 * Load available playlists from backend API
 * Story 3.3: Fetch playlists and populate dropdown
 */
async function loadPlaylists() {
    const dropdown = document.getElementById('playlist');
    const errorElement = document.getElementById('playlist-error');
    const descElement = document.getElementById('playlist-desc');
    const checkmarkElement = document.getElementById('playlist-check');

    try {
        console.log('Fetching playlists from API...');

        const response = await fetch('/api/beatsy/api/playlists');
        const data = await response.json();

        if (response.ok && data.playlists && data.playlists.length > 0) {
            console.log(`Successfully fetched ${data.playlists.length} playlist(s)`);
            populatePlaylistDropdown(data.playlists);

            // Hide error message if previously shown
            errorElement.classList.add('hidden');
        } else if (response.status === 404 || (data.playlists && data.playlists.length === 0)) {
            // No playlists found
            console.warn('No playlists found');
            showPlaylistError(data.message || 'No playlists found. Add playlist JSON files to custom_components/beatsy/playlists/ directory.');
            dropdown.innerHTML = '<option value="">No playlists found</option>';
            dropdown.disabled = true;
            checkmarkElement.classList.add('hidden');
            descElement.classList.add('hidden');
        } else {
            // Other error
            console.error('Failed to load playlists:', data);
            showPlaylistError(data.message || 'Failed to load playlists. Please try again.');
            dropdown.disabled = true;
            checkmarkElement.classList.add('hidden');
            descElement.classList.add('hidden');
        }
    } catch (error) {
        console.error('Error fetching playlists:', error);
        showPlaylistError('Connection error. Please check your network and try again.');
        dropdown.innerHTML = '<option value="">Connection error</option>';
        dropdown.disabled = true;
        descElement.classList.add('hidden');
    }
}

/**
 * Populate playlist dropdown with fetched playlists
 * Story 3.3: AC-2, AC-5
 */
function populatePlaylistDropdown(playlists) {
    const dropdown = document.getElementById('playlist');
    const checkmarkElement = document.getElementById('playlist-check');
    const descElement = document.getElementById('playlist-desc');

    // Clear loading state
    dropdown.innerHTML = '';

    // Add options with playlist name and track count
    playlists.forEach(playlist => {
        const option = document.createElement('option');
        option.value = playlist.playlist_id;
        option.textContent = `${playlist.name} (${playlist.track_count} tracks)`;
        dropdown.appendChild(option);
    });

    // Enable dropdown for selection
    dropdown.disabled = false;
    dropdown.classList.remove('bg-gray-100', 'cursor-not-allowed');
    dropdown.classList.add('cursor-pointer');

    // Restore saved selection from localStorage (Story 3.3: AC-5)
    const savedPlaylist = localStorage.getItem('beatsy_playlist');
    if (savedPlaylist) {
        // Check if saved playlist exists in current list
        const playlistExists = playlists.some(p => p.playlist_id === savedPlaylist);
        if (playlistExists) {
            dropdown.value = savedPlaylist;
            gameConfig.playlist = savedPlaylist;
            console.log('Restored saved playlist selection:', savedPlaylist);

            // Show visual feedback and metadata
            const selectedPlaylist = playlists.find(p => p.playlist_id === savedPlaylist);
            updatePlaylistVisualFeedback(dropdown, true, selectedPlaylist);
        } else {
            // Saved playlist no longer available, select first
            dropdown.selectedIndex = 0;
            gameConfig.playlist = playlists[0].playlist_id;
            localStorage.setItem('beatsy_playlist', playlists[0].playlist_id);
            console.log('Saved playlist not found, selected first playlist:', playlists[0].playlist_id);

            // Show visual feedback and metadata
            updatePlaylistVisualFeedback(dropdown, true, playlists[0]);
        }
    } else {
        // No saved selection, select first playlist by default
        dropdown.selectedIndex = 0;
        gameConfig.playlist = playlists[0].playlist_id;
        localStorage.setItem('beatsy_playlist', playlists[0].playlist_id);
        console.log('No saved selection, selected first playlist:', playlists[0].playlist_id);

        // Show visual feedback and metadata
        updatePlaylistVisualFeedback(dropdown, true, playlists[0]);
    }
}

/**
 * Show error message for playlist loading failures
 * Story 3.3: AC-3
 */
function showPlaylistError(message) {
    const errorElement = document.getElementById('playlist-error');
    errorElement.textContent = message;
    errorElement.classList.remove('hidden');
}

/**
 * Handle playlist selection change
 * Story 3.3: AC-5 (Save selection), AC-6 (Visual feedback)
 */
function handlePlaylistChange(event) {
    const selectedPlaylistId = event.target.value;
    const dropdown = event.target;

    if (selectedPlaylistId && selectedPlaylistId !== '') {
        // Find the selected playlist from dropdown options
        const selectedOption = dropdown.options[dropdown.selectedIndex];
        const playlistName = selectedOption.textContent;

        // Save to state
        gameConfig.playlist = selectedPlaylistId;

        // Save to localStorage for persistence
        localStorage.setItem('beatsy_playlist', selectedPlaylistId);

        console.log('Playlist selected:', selectedPlaylistId);

        // Extract track count from option text (format: "Name (N tracks)")
        const trackCountMatch = playlistName.match(/\((\d+) tracks\)/);
        const trackCount = trackCountMatch ? parseInt(trackCountMatch[1]) : 0;

        // Update visual feedback with metadata
        updatePlaylistVisualFeedback(dropdown, true, {
            playlist_id: selectedPlaylistId,
            name: playlistName.replace(/\s*\(\d+ tracks\)$/, ''),
            track_count: trackCount
        });

        // Update Start Game button state (partial - other fields needed too)
        updateStartGameButtonState();
    } else {
        // No valid selection
        gameConfig.playlist = null;
        updatePlaylistVisualFeedback(dropdown, false, null);
        updateStartGameButtonState();
    }
}

/**
 * Update visual feedback for playlist dropdown
 * Story 3.3: AC-6 (Green border, checkmark icon, metadata display)
 */
function updatePlaylistVisualFeedback(dropdown, isValid, playlist) {
    const checkmarkElement = document.getElementById('playlist-check');
    const descElement = document.getElementById('playlist-desc');

    if (isValid && playlist) {
        // Valid selection: Green border + checkmark + metadata
        dropdown.classList.remove('border-gray-300', 'border-red-500');
        dropdown.classList.add('border-green-500');
        checkmarkElement.classList.remove('hidden');

        // Display playlist metadata
        descElement.textContent = `${playlist.name} - ${playlist.track_count} tracks`;
        descElement.classList.remove('hidden', 'text-red-600');
        descElement.classList.add('text-gray-500');
    } else {
        // Invalid/no selection: Red border, no checkmark
        dropdown.classList.remove('border-gray-300', 'border-green-500');
        dropdown.classList.add('border-red-500');
        checkmarkElement.classList.add('hidden');
        descElement.classList.add('hidden');
    }
}

/**
 * Verify that all required page sections exist
 */
function verifyPageStructure() {
    const requiredSections = [
        'game-config',
        'game-control',
        'game-status'
    ];

    const missingElements = [];

    requiredSections.forEach(sectionId => {
        const element = document.getElementById(sectionId);
        if (!element) {
            missingElements.push(sectionId);
            console.error(`Missing required section: ${sectionId}`);
        } else {
            console.log(`✓ Section loaded: ${sectionId}`);
        }
    });

    if (missingElements.length > 0) {
        console.error('Page structure validation failed:', missingElements);
    } else {
        console.log('✓ Page structure validation passed');
    }
}

/**
 * Setup placeholder event listeners for future functionality
 * These will be implemented in Stories 3.2-3.7
 */
function setupPlaceholderListeners() {
    // Story 3.2: Media player selector - now implemented
    const mediaPlayerSelect = document.getElementById('media-player');
    if (mediaPlayerSelect) {
        mediaPlayerSelect.addEventListener('change', handleMediaPlayerChange);
    }

    // Story 3.3: Playlist selector - now implemented
    const playlistSelect = document.getElementById('playlist');
    if (playlistSelect) {
        playlistSelect.addEventListener('change', handlePlaylistChange);
    }

    // Story 3.5: Start game button
    const startGameBtn = document.getElementById('start-game-btn');
    if (startGameBtn) {
        startGameBtn.addEventListener('click', async (e) => {
            await startGame();
        });
    }

    // Story 3.6 Task 2: Join as Player button (click handler will be implemented in Task 3)
    const joinAsPlayerBtn = document.getElementById('join-as-player-btn');
    if (joinAsPlayerBtn) {
        joinAsPlayerBtn.addEventListener('click', async (e) => {
            await joinAsPlayer();
        });
    }

    // Story 5.7: Reset Game button
    const resetGameBtn = document.getElementById('reset-game-btn');
    if (resetGameBtn) {
        resetGameBtn.addEventListener('click', async (e) => {
            if (confirm('Are you sure? This will end the current game and clear all players.')) {
                await resetGame();
            }
        });
    }

    console.log('✓ Placeholder event listeners registered');
}

/**
 * Handle viewport resize events (for responsive testing)
 */
function handleResize() {
    console.log('Viewport resized:', {
        width: window.innerWidth,
        height: window.innerHeight
    });
}

// Debounced resize handler
let resizeTimeout;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(handleResize, 250);
});

/**
 * Check for mobile device and log device info
 */
function detectMobileDevice() {
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

    console.log('Device detection:', {
        isMobile,
        isTouchDevice,
        platform: navigator.platform,
        screenWidth: window.screen.width,
        screenHeight: window.screen.height
    });

    return { isMobile, isTouchDevice };
}

/**
 * Main initialization - runs when DOM is fully loaded
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('=== Beatsy Admin UI Starting ===');

    // Detect device type
    detectMobileDevice();

    // Initialize UI
    initAdminUI();

    console.log('=== Beatsy Admin UI Ready ===');
});

/**
 * Handle page visibility changes (for future WebSocket connection management)
 */
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        console.log('Page hidden - connection management will be handled in Story 3.7');
    } else {
        console.log('Page visible - connection management will be handled in Story 3.7');
    }
});

// ============================================================================
// Story 3.4: Game Settings Functions
// ============================================================================

/**
 * Debounce utility function
 * Story 3.4: AC-7 (Debounced localStorage saves)
 */
function debounce(fn, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn.apply(this, args), delay);
    };
}

/**
 * Validate all game settings inputs
 * Story 3.4: AC-9 (Validation logic)
 * Returns: {valid: boolean, errors: {field: message}}
 */
function validateGameSettings() {
    const errors = {};

    // Timer validation
    const timer = parseInt(document.getElementById('timer-duration').value);
    if (isNaN(timer) || timer < 10 || timer > 120) {
        errors.timer = "Timer must be between 10-120 seconds";
    }

    // Year range validation
    const yearMin = parseInt(document.getElementById('year-range-min').value);
    const yearMax = parseInt(document.getElementById('year-range-max').value);

    if (isNaN(yearMin) || yearMin < 1900 || yearMin > 2024) {
        errors.yearMin = "Year min must be between 1900-2024";
    }
    if (isNaN(yearMax) || yearMax < 1900 || yearMax > 2024) {
        errors.yearMax = "Year max must be between 1900-2024";
    }
    if (!isNaN(yearMin) && !isNaN(yearMax) && yearMin >= yearMax) {
        errors.yearRange = "Year min must be less than year max";
    }

    // Scoring validation
    const exactPoints = parseInt(document.getElementById('exact-points').value);
    const closePoints = parseInt(document.getElementById('close-points').value);
    const nearPoints = parseInt(document.getElementById('near-points').value);

    if (isNaN(exactPoints) || exactPoints < 0 || exactPoints > 100) {
        errors.exactPoints = "Points must be between 0-100";
    }
    if (isNaN(closePoints) || closePoints < 0 || closePoints > 100) {
        errors.closePoints = "Points must be between 0-100";
    }
    if (isNaN(nearPoints) || nearPoints < 0 || nearPoints > 100) {
        errors.nearPoints = "Points must be between 0-100";
    }

    // Bet multiplier validation
    const betMultiplier = parseInt(document.getElementById('bet-multiplier').value);
    if (isNaN(betMultiplier) || betMultiplier < 1 || betMultiplier > 10) {
        errors.betMultiplier = "Bet multiplier must be between 1-10";
    }

    return {
        valid: Object.keys(errors).length === 0,
        errors: errors
    };
}

/**
 * Show validation error for a field
 * Story 3.4: AC-9 (Visual feedback)
 */
function showValidationError(fieldId, message) {
    const input = document.getElementById(fieldId);
    const errorElement = document.getElementById(`${fieldId}-error`);

    if (input) {
        // Add red border to input
        input.classList.remove('border-gray-300', 'border-green-500');
        input.classList.add('border-red-500');
        input.setAttribute('aria-invalid', 'true');
    }

    if (errorElement) {
        // Display error message
        errorElement.textContent = message;
        errorElement.classList.remove('hidden');
    }
}

/**
 * Clear validation error for a field
 * Story 3.4: AC-9 (Visual feedback)
 */
function clearValidationError(fieldId) {
    const input = document.getElementById(fieldId);
    const errorElement = document.getElementById(`${fieldId}-error`);

    if (input) {
        // Remove red border, add green border for valid state
        input.classList.remove('border-red-500');
        input.classList.add('border-green-500');
        input.removeAttribute('aria-invalid');
    }

    if (errorElement) {
        // Hide error message
        errorElement.classList.add('hidden');
        errorElement.textContent = '';
    }
}

/**
 * Save game settings to localStorage
 * Story 3.4: AC-7 (Persistence)
 */
function saveSettingsToLocalStorage() {
    const settings = {
        timer_duration: document.getElementById('timer-duration').value,
        year_range_min: document.getElementById('year-range-min').value,
        year_range_max: document.getElementById('year-range-max').value,
        exact_points: document.getElementById('exact-points').value,
        close_points: document.getElementById('close-points').value,
        near_points: document.getElementById('near-points').value,
        bet_multiplier: document.getElementById('bet-multiplier').value
    };

    localStorage.setItem('beatsy_game_settings', JSON.stringify(settings));
    console.log('Game settings saved to localStorage');
}

/**
 * Load game settings from localStorage
 * Story 3.4: AC-7 (Persistence restore)
 */
function loadSettingsFromLocalStorage() {
    const saved = localStorage.getItem('beatsy_game_settings');

    if (saved) {
        try {
            const settings = JSON.parse(saved);

            // Restore input values
            if (settings.timer_duration) document.getElementById('timer-duration').value = settings.timer_duration;
            if (settings.year_range_min) document.getElementById('year-range-min').value = settings.year_range_min;
            if (settings.year_range_max) document.getElementById('year-range-max').value = settings.year_range_max;
            if (settings.exact_points) document.getElementById('exact-points').value = settings.exact_points;
            if (settings.close_points) document.getElementById('close-points').value = settings.close_points;
            if (settings.near_points) document.getElementById('near-points').value = settings.near_points;
            if (settings.bet_multiplier) document.getElementById('bet-multiplier').value = settings.bet_multiplier;

            // Update gameConfig state
            gameConfig.timerDuration = parseInt(settings.timer_duration) || 30;
            gameConfig.yearRangeMin = parseInt(settings.year_range_min) || 1950;
            gameConfig.yearRangeMax = parseInt(settings.year_range_max) || 2024;
            gameConfig.exactPoints = parseInt(settings.exact_points) || 10;
            gameConfig.closePoints = parseInt(settings.close_points) || 5;
            gameConfig.nearPoints = parseInt(settings.near_points) || 2;
            gameConfig.betMultiplier = parseInt(settings.bet_multiplier) || 2;

            // Update dynamic examples
            updateScoringExample();
            updateBetExample();

            console.log('Game settings restored from localStorage');
        } catch (error) {
            console.error('Error loading settings from localStorage:', error);
        }
    }
}

/**
 * Update scoring example text dynamically
 * Story 3.4: AC-4 (Dynamic example)
 */
function updateScoringExample() {
    const closePoints = parseInt(document.getElementById('close-points').value) || 5;
    const exampleElement = document.getElementById('scoring-example');

    if (exampleElement) {
        exampleElement.textContent = `Example: Guess 1987, Actual 1986 = Close Match (+${closePoints} pts)`;
    }
}

/**
 * Update bet example text dynamically
 * Story 3.4: AC-5 (Dynamic example)
 */
function updateBetExample() {
    const exactPoints = parseInt(document.getElementById('exact-points').value) || 10;
    const betMultiplier = parseInt(document.getElementById('bet-multiplier').value) || 2;
    const result = exactPoints * betMultiplier;
    const exampleElement = document.getElementById('bet-example');

    if (exampleElement) {
        exampleElement.textContent = `With ${betMultiplier}x multiplier: Exact match bet = ${result} points`;
    }
}

/**
 * Setup event listeners for game settings inputs
 * Story 3.4: AC-7 (Debounced saves), AC-9 (Validation on blur), AC-4, AC-5 (Dynamic examples)
 */
function setupGameSettingsListeners() {
    // Create debounced save function (300ms delay)
    const debouncedSave = debounce(saveSettingsToLocalStorage, 300);

    // Get all settings inputs
    const settingsInputs = [
        'timer-duration',
        'year-range-min',
        'year-range-max',
        'exact-points',
        'close-points',
        'near-points',
        'bet-multiplier'
    ];

    settingsInputs.forEach(inputId => {
        const input = document.getElementById(inputId);
        if (!input) return;

        // Debounced save on input change
        input.addEventListener('input', () => {
            // Update gameConfig immediately
            switch(inputId) {
                case 'timer-duration':
                    gameConfig.timerDuration = parseInt(input.value) || 30;
                    break;
                case 'year-range-min':
                    gameConfig.yearRangeMin = parseInt(input.value) || 1950;
                    break;
                case 'year-range-max':
                    gameConfig.yearRangeMax = parseInt(input.value) || 2024;
                    break;
                case 'exact-points':
                    gameConfig.exactPoints = parseInt(input.value) || 10;
                    updateScoringExample();  // Update example
                    updateBetExample();       // Update bet example (uses exact points)
                    break;
                case 'close-points':
                    gameConfig.closePoints = parseInt(input.value) || 5;
                    updateScoringExample();   // Update example
                    break;
                case 'near-points':
                    gameConfig.nearPoints = parseInt(input.value) || 2;
                    break;
                case 'bet-multiplier':
                    gameConfig.betMultiplier = parseInt(input.value) || 2;
                    updateBetExample();       // Update example
                    break;
            }

            // Debounced save to localStorage
            debouncedSave();
        });

        // Validation on blur
        input.addEventListener('blur', () => {
            const validation = validateGameSettings();

            // Handle year-range error separately (spans two fields)
            if (inputId === 'year-range-min' || inputId === 'year-range-max') {
                if (validation.errors.yearRange) {
                    showValidationError('year-range', validation.errors.yearRange);
                } else if (!validation.errors.yearMin && !validation.errors.yearMax) {
                    clearValidationError('year-range');
                }
            }

            // Handle field-specific errors
            if (validation.errors[inputId]) {
                showValidationError(inputId, validation.errors[inputId]);
            } else if (validation.errors.yearMin && inputId === 'year-range-min') {
                showValidationError(inputId, validation.errors.yearMin);
            } else if (validation.errors.yearMax && inputId === 'year-range-max') {
                showValidationError(inputId, validation.errors.yearMax);
            } else {
                clearValidationError(inputId);
            }

            // Update Start Game button state
            updateStartGameButtonState();
        });
    });

    console.log('✓ Game settings event listeners registered');
}

// ============================================================================
// Story 3.5: Start Game Functions
// ============================================================================

/**
 * Start a new game session
 * Story 3.5: AC-8 (Client-Side State Management), AC-9 (Error Handling)
 */
async function startGame(forceStart = false) {
    const startGameBtn = document.getElementById('start-game-btn');
    const spinnerElement = document.getElementById('start-game-spinner');
    const buttonTextElement = document.getElementById('start-game-text');

    try {
        // Final validation check
        if (!validateStartGameReady()) {
            showToast('Please complete all configuration fields before starting', 'error');
            return;
        }

        // Disable button and show loading state
        startGameBtn.disabled = true;
        spinnerElement.classList.remove('hidden');
        buttonTextElement.textContent = 'Starting...';

        // Collect game configuration from form inputs
        const config = {
            media_player: gameConfig.mediaPlayer,
            playlist_id: gameConfig.playlist,
            timer_duration: parseInt(document.getElementById('timer-duration').value),
            year_range_min: parseInt(document.getElementById('year-range-min').value),
            year_range_max: parseInt(document.getElementById('year-range-max').value),
            exact_points: parseInt(document.getElementById('exact-points').value),
            close_points: parseInt(document.getElementById('close-points').value),
            near_points: parseInt(document.getElementById('near-points').value),
            bet_multiplier: parseInt(document.getElementById('bet-multiplier').value)
        };

        console.log('Starting game with config:', config, 'force:', forceStart);

        // Story 7.3: POST to start_game endpoint with optional force parameter
        const response = await fetch('/api/beatsy/api/start_game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                config,
                force: forceStart  // Story 7.3: Include force flag
            })
        });

        const data = await response.json();

        // Story 7.3: Check for conflict warning (media player already playing)
        if (response.ok && data.conflict_warning) {
            console.log('Media player conflict detected:', data.current_media);

            // Reset button state before showing modal
            startGameBtn.disabled = false;
            spinnerElement.classList.add('hidden');
            buttonTextElement.textContent = 'Start Game';

            // Show conflict warning modal
            showConflictWarningModal(data.current_media);
            return;  // Exit early - wait for user decision
        }

        if (response.ok) {
            // Success! Handle 200 response
            console.log('Game started successfully:', data);

            // Story 3.6 Task 1: Save admin_key and game_id to localStorage with 24-hour expiry
            localStorage.setItem('beatsy_admin_key', data.admin_key);
            localStorage.setItem('beatsy_admin_key_expiry', Date.now() + (24 * 60 * 60 * 1000)); // 24 hours
            localStorage.setItem('beatsy_game_id', data.game_id);

            // Log admin key storage (security: first 8 chars only)
            console.log('Admin key stored:', data.admin_key.substring(0, 8) + '... (expires in 24 hours)');

            // Update button state to "Game Active"
            buttonTextElement.textContent = 'Game Active';
            spinnerElement.classList.add('hidden');
            startGameBtn.disabled = true;  // Keep disabled

            // Story 3.6 Task 2: Show "Join as Player" button after successful game start
            const joinAsPlayerBtn = document.getElementById('join-as-player-btn');
            if (joinAsPlayerBtn) {
                joinAsPlayerBtn.classList.remove('hidden');
                console.log('✓ "Join as Player" button now visible');
            }

            // Display player URL (Task 7-8 will handle this)
            if (typeof displayPlayerUrl === 'function') {
                displayPlayerUrl(data.player_url);
            } else {
                console.log('Player URL:', data.player_url);
            }

            // Story 3.7 Task 9: Refresh game status after successful game start
            loadGameStatus();

            // Show success toast
            showToast(`Game started! ${data.playlist_tracks} tracks loaded.`, 'success');

            console.log('Game info:', {
                game_id: data.game_id,
                status: data.status,
                playlist_tracks: data.playlist_tracks,
                admin_key_saved: !!localStorage.getItem('beatsy_admin_key')
            });

        } else {
            // Handle error responses
            console.error('Start game failed:', response.status, data);

            let errorMessage = 'Failed to start game';

            if (response.status === 400) {
                // Validation errors
                if (data.error === 'validation_failed' && data.details) {
                    errorMessage = 'Configuration errors: ' + data.details.join(', ');
                } else if (data.error === 'insufficient_tracks') {
                    errorMessage = data.message || 'Not enough tracks after year filtering';
                } else {
                    errorMessage = data.message || 'Invalid configuration';
                }
            } else if (response.status === 404) {
                // Playlist not found
                errorMessage = data.message || 'Playlist not found';
            } else if (response.status === 500) {
                // Server error
                errorMessage = data.message || 'Server error - check Home Assistant logs';
            } else if (response.status === 503) {
                // Media player unavailable
                errorMessage = data.message || 'Media player unavailable';
            }

            showToast(errorMessage, 'error');

            // Re-enable button for retry
            startGameBtn.disabled = false;
            spinnerElement.classList.add('hidden');
            buttonTextElement.textContent = 'Start Game';
        }

    } catch (error) {
        // Network error or other exception
        console.error('Error starting game:', error);
        showToast('Connection error. Please check your network and try again.', 'error');

        // Re-enable button for retry
        startGameBtn.disabled = false;
        spinnerElement.classList.add('hidden');
        buttonTextElement.textContent = 'Start Game';
    }
}

/**
 * Reset game and clear all state
 * Story 5.7: Send reset_game WebSocket command, handle response
 */
async function resetGame() {
    const resetGameBtn = document.getElementById('reset-game-btn');

    try {
        console.log('Resetting game...');

        // Disable button to prevent double-click
        resetGameBtn.disabled = true;
        resetGameBtn.textContent = 'Resetting...';

        // Send WebSocket reset_game command
        if (window.ws && window.ws.readyState === WebSocket.OPEN) {
            const msgId = Date.now();
            window.ws.send(JSON.stringify({
                id: msgId,
                type: 'beatsy/reset_game'
            }));

            console.log('Reset game command sent');
            showToast('Game reset in progress...', 'info');
        } else {
            throw new Error('WebSocket not connected');
        }

        // Note: Actual state clearing will happen when game_reset event is received
        // The button will be re-enabled and hidden by the event handler

    } catch (error) {
        console.error('Error resetting game:', error);
        showToast('Failed to reset game: ' + error.message, 'error');

        // Re-enable button on error
        resetGameBtn.disabled = false;
        resetGameBtn.innerHTML = '<span class="flex items-center justify-center space-x-2"><svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd"/></svg><span>Reset Game</span></span>';
    }
}

/**
 * Handle game_reset event received from server (Story 5.7)
 * Update admin UI to reflect reset state
 */
function handleAdminGameReset(data) {
    console.log('Admin UI handling game_reset event:', data);

    // Hide reset button (game no longer active)
    const resetBtn = document.getElementById('reset-game-btn');
    if (resetBtn) {
        resetBtn.classList.add('hidden');
        resetBtn.disabled = false;  // Re-enable for next use
        resetBtn.innerHTML = '<span class="flex items-center justify-center space-x-2"><svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd"/></svg><span>Reset Game</span></span>';
    }

    // Update start game button state
    const startGameBtn = document.getElementById('start-game-btn');
    const startGameText = document.getElementById('start-game-text');
    const spinner = document.getElementById('start-game-spinner');

    if (startGameBtn) {
        startGameBtn.disabled = false;  // Re-enable (if config valid)
        if (spinner) spinner.classList.add('hidden');
        if (startGameText) startGameText.textContent = 'Start Game';
    }

    // Hide game info section
    const gameInfoSection = document.getElementById('game-info-section');
    if (gameInfoSection) {
        gameInfoSection.classList.add('hidden');
    }

    // Hide join as player button
    const joinAsPlayerBtn = document.getElementById('join-as-player-btn');
    if (joinAsPlayerBtn) {
        joinAsPlayerBtn.classList.add('hidden');
    }

    // Clear localStorage admin state
    localStorage.removeItem('beatsy_game_id');

    // Reload game status to reflect reset
    if (typeof loadGameStatus === 'function') {
        loadGameStatus();
    }

    // Show toast notification
    const message = data.message || 'Game has been reset';
    showToast(message, 'info');

    console.log('✓ Admin UI reset to setup state');
}

/**
 * Join game as player (admin redirect to player registration)
 * Story 3.6 Task 3: Redirect admin to player registration page
 */
async function joinAsPlayer() {
    console.log('Join as Player clicked');

    // Get game_id from localStorage (stored after game start)
    const gameId = localStorage.getItem('beatsy_game_id');

    if (!gameId) {
        console.error('No game_id found in localStorage');
        showToast('Error: Game not started. Please start a game first.', 'error');
        return;
    }

    // Construct player URL with game_id query parameter
    // Admin key is already in localStorage from Task 1, will be detected by player registration
    const playerUrl = `/local/beatsy/start.html?game_id=${gameId}`;

    console.log('Redirecting to player registration:', playerUrl);
    console.log('Admin key in localStorage:', !!localStorage.getItem('beatsy_admin_key'));

    // Navigate to player registration page
    window.location.href = playerUrl;
}

/**
 * Display player URL after successful game start
 * Story 3.5: AC-8 (Player URL Display)
 */
function displayPlayerUrl(playerUrl) {
    const gameInfoSection = document.getElementById('game-info-section');
    const playerUrlInput = document.getElementById('player-url');

    if (!gameInfoSection || !playerUrlInput) {
        console.error('Player URL display elements not found');
        return;
    }

    // Set the player URL value
    playerUrlInput.value = playerUrl;

    // Show the game info section
    gameInfoSection.classList.remove('hidden');

    // Focus on URL input for easy manual copying
    playerUrlInput.focus();
    playerUrlInput.select();

    console.log('Player URL displayed:', playerUrl);

    // Setup copy button listener (do this once)
    setupCopyButton();
}

/**
 * Setup copy-to-clipboard functionality for player URL
 * Story 3.5: AC-8 (Copy to clipboard)
 */
function setupCopyButton() {
    const copyBtn = document.getElementById('copy-url-btn');
    const playerUrlInput = document.getElementById('player-url');

    if (!copyBtn || !playerUrlInput) return;

    // Remove any existing listeners (prevent duplicates)
    copyBtn.replaceWith(copyBtn.cloneNode(true));
    const newCopyBtn = document.getElementById('copy-url-btn');

    newCopyBtn.addEventListener('click', async () => {
        const playerUrl = playerUrlInput.value;

        try {
            // Modern clipboard API
            if (navigator.clipboard && navigator.clipboard.writeText) {
                await navigator.clipboard.writeText(playerUrl);
                showToast('Player URL copied to clipboard!', 'success');
                console.log('URL copied via clipboard API');
            } else {
                // Fallback for older browsers
                playerUrlInput.select();
                const success = document.execCommand('copy');

                if (success) {
                    showToast('Player URL copied to clipboard!', 'success');
                    console.log('URL copied via execCommand');
                } else {
                    throw new Error('execCommand failed');
                }
            }
        } catch (error) {
            console.error('Failed to copy URL:', error);
            showToast('Failed to copy. Please copy manually.', 'error');

            // Select the text so user can copy manually
            playerUrlInput.select();
        }
    });

    console.log('Copy button setup complete');
}

/**
 * Show toast notification
 * Story 3.5: Helper function for user feedback
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

// ============================================================================
// Story 3.7: Game Status Functions
// ============================================================================

/**
 * Load game status from API
 * Story 3.7 Task 3: AC-2 (Initial Status Load)
 */
async function loadGameStatus() {
    try {
        console.log('Loading game status from API...');

        const response = await fetch('/api/beatsy/api/game_status');
        const data = await response.json();

        if (response.ok) {
            // Game exists, update status panel
            console.log('Game status loaded successfully:', data);
            updateStatusPanel(data);
        } else if (response.status === 404) {
            // No game active
            console.log('No active game found');
            showNoGameStatus();
        } else {
            // Other error
            console.error('Failed to load game status:', response.status, data);
            showStatusError(data.message || 'Failed to load game status');
        }
    } catch (error) {
        console.error('Error loading game status:', error);
        showStatusError('Connection error loading game status');
    }
}

/**
 * Update status panel with game data
 * Story 3.7 Task 4: AC-1, AC-3, AC-4, AC-5
 */
function updateStatusPanel(status) {
    // Update game state with formatted text
    const stateElement = document.getElementById('status-state');
    if (stateElement) {
        stateElement.textContent = formatGameState(status.state);

        // Add color based on state (AC-4 visual indicators)
        stateElement.className = 'text-lg sm:text-xl font-semibold';
        switch(status.state) {
            case 'lobby':
                stateElement.classList.add('text-blue-600');
                break;
            case 'active':
                stateElement.classList.add('text-green-600');
                break;
            case 'results':
                stateElement.classList.add('text-yellow-600');
                break;
            case 'ended':
                stateElement.classList.add('text-gray-600');
                break;
            default:
                stateElement.classList.add('text-gray-800');
        }
    }

    // Update player count
    const playersElement = document.getElementById('status-players');
    if (playersElement) {
        playersElement.textContent = status.player_count || 0;
    }

    // Update songs remaining
    const songsElement = document.getElementById('status-songs');
    if (songsElement) {
        songsElement.textContent = status.songs_remaining >= 0 ? status.songs_remaining : '-';
    }

    // Update current round
    const roundElement = document.getElementById('status-round');
    if (roundElement) {
        roundElement.textContent = status.current_round || '-';
    }

    console.log('Status panel updated:', status);
}

/**
 * Format game state for display
 * Story 3.7 Task 4: State formatting helper
 */
function formatGameState(state) {
    const stateMap = {
        'setup': 'Setup',
        'lobby': 'Lobby',
        'active': 'Round Active',
        'results': 'Results',
        'ended': 'Game Ended'
    };
    return stateMap[state] || state;
}

/**
 * Show "No active game" status
 * Story 3.7 Task 7: AC-2, AC-9
 */
function showNoGameStatus() {
    const stateElement = document.getElementById('status-state');
    if (stateElement) {
        stateElement.textContent = 'No active game';
        stateElement.className = 'text-lg sm:text-xl font-semibold text-gray-500';
    }

    document.getElementById('status-players').textContent = '0';
    document.getElementById('status-songs').textContent = '-';
    document.getElementById('status-round').textContent = '-';

    console.log('No active game status displayed');
}

/**
 * Show status error message
 * Story 3.7 Task 8: AC-9 (Error handling)
 */
function showStatusError(message) {
    console.error('Status error:', message);
    showToast(message, 'error');
}

/**
 * Update connection status indicator
 * Story 3.7 Task 6: AC-8 (Connection indicator)
 */
function updateConnectionStatus(connected) {
    const indicator = document.getElementById('connection-indicator');
    const text = document.getElementById('connection-text');

    if (!indicator || !text) return;

    if (connected) {
        // Green indicator + "Connected" text
        indicator.classList.remove('bg-gray-400', 'bg-red-500');
        indicator.classList.add('bg-green-500');
        text.textContent = 'Connected';
        text.classList.remove('text-gray-600', 'text-red-600');
        text.classList.add('text-green-600');
        console.log('Connection status: Connected');
    } else {
        // Red indicator + "Reconnecting..." text
        indicator.classList.remove('bg-gray-400', 'bg-green-500');
        indicator.classList.add('bg-red-500');
        text.textContent = 'Reconnecting...';
        text.classList.remove('text-gray-600', 'text-green-600');
        text.classList.add('text-red-600');
        console.log('Connection status: Disconnected');
    }
}

/**
 * Load game status with retry logic
 * Story 3.7 Task 8: AC-9 (Exponential backoff retry)
 */
let retryCount = 0;
const maxRetries = 3;
const retryDelays = [1000, 2000, 4000]; // Exponential backoff: 1s, 2s, 4s

async function loadGameStatusWithRetry() {
    try {
        await loadGameStatus();
        retryCount = 0; // Reset on success
    } catch (error) {
        if (retryCount < maxRetries) {
            const delay = retryDelays[retryCount];
            console.warn(`Failed to load status. Retrying in ${delay / 1000}s... (attempt ${retryCount + 1}/${maxRetries})`);
            showToast(`Failed to load status. Retrying in ${delay / 1000}s...`, 'error');

            setTimeout(loadGameStatusWithRetry, delay);
            retryCount++;
        } else {
            console.error('Failed to load game status after max retries');
            showToast('Failed to load game status. Please refresh the page.', 'error');
            retryCount = 0; // Reset for next attempt
        }
    }
}

/**
 * Setup WebSocket event listeners for game status updates
 * Story 3.7 Task 5: AC-3, AC-4, AC-5 (WebSocket listeners)
 *
 * Note: This is a placeholder for WebSocket integration.
 * Full WebSocket client will be implemented in future stories.
 * For now, we demonstrate the event handling pattern.
 */
function setupGameStatusWebSocketListeners() {
    console.log('Game status WebSocket listeners ready (placeholder)');

    // TODO: Story 3.7 - Integrate with WebSocket client when available
    // Expected WebSocket events:
    // 1. player_joined - Update player count
    // 2. round_started - Update game state, round number, songs remaining
    // 3. round_ended - Update game state to "Results"
    // 4. game_reset - Return to setup state (Story 5.7)

    // Story 5.7: Listen for game_reset event to update admin UI
    if (window.ws) {
        const originalOnMessage = window.ws.onmessage;

        window.ws.onmessage = function(event) {
            // Call original handler if exists
            if (originalOnMessage) {
                originalOnMessage.call(window.ws, event);
            }

            // Handle game_reset event and playback_error event
            try {
                const data = JSON.parse(event.data);

                if (data.type === 'beatsy/event' && data.event_type === 'game_reset') {
                    console.log('🔄 Game reset event received in admin UI:', data.data);
                    handleAdminGameReset(data.data);
                }

                // Story 7.5: Handle playback_error event
                if (data.type === 'beatsy/event' && data.event_type === 'playback_error') {
                    console.log('⚠️ Playback error event received in admin UI:', data.data);
                    showPlaybackErrorNotification(data.data);
                }
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };
    }

    // Example handler structure (to be connected to real WebSocket):
    /*
    websocket.addEventListener('beatsy:player_joined', (event) => {
        console.log('Player joined event received:', event.detail);
        const currentCount = parseInt(document.getElementById('status-players').textContent);
        document.getElementById('status-players').textContent = currentCount + 1;
    });

    websocket.addEventListener('beatsy:round_started', (event) => {
        console.log('Round started event received:', event.detail);
        document.getElementById('status-state').textContent = 'Round Active';
        const roundNum = event.detail.round_number;
        document.getElementById('status-round').textContent = roundNum;

        // Decrement songs remaining
        const remaining = parseInt(document.getElementById('status-songs').textContent);
        if (!isNaN(remaining) && remaining > 0) {
            document.getElementById('status-songs').textContent = remaining - 1;
        }
    });

    websocket.addEventListener('beatsy:round_ended', (event) => {
        console.log('Round ended event received:', event.detail);
        document.getElementById('status-state').textContent = 'Results';
    });

    websocket.addEventListener('open', () => {
        updateConnectionStatus(true);
        loadGameStatus(); // Sync status on connection
    });

    websocket.addEventListener('close', () => {
        updateConnectionStatus(false);
    });

    websocket.addEventListener('error', () => {
        updateConnectionStatus(false);
    });
    */
}

// Initialize game status on page load (called from initAdminUI)
// Story 3.7: Load status when admin page opens
function initGameStatus() {
    console.log('Initializing game status display...');

    // Set initial connection status to "Connecting..."
    updateConnectionStatus(false);

    // Load initial game status
    loadGameStatusWithRetry();

    // Setup WebSocket listeners (placeholder)
    setupGameStatusWebSocketListeners();

    console.log('✓ Game status initialization complete');
}

// ============================================================================
// Story 7.3: Media Player Conflict Warning Modal
// ============================================================================

/**
 * Show conflict warning modal when media player is already playing
 * Story 7.3: AC-1, AC-2 (Display warning to admin with current media info)
 */
function showConflictWarningModal(currentMedia) {
    const modal = document.getElementById('conflict-warning-modal');
    const entityNameEl = document.getElementById('conflict-modal-entity-name');
    const titleEl = document.getElementById('conflict-modal-title-text');
    const artistEl = document.getElementById('conflict-modal-artist-text');

    if (!modal || !entityNameEl || !titleEl || !artistEl) {
        console.error('Conflict warning modal elements not found');
        // Fallback: ask via browser confirm dialog
        const proceed = confirm(
            `Media player is currently playing "${currentMedia.title}" by ${currentMedia.artist}. ` +
            'Starting the game will take over playback. Continue?'
        );
        if (proceed) {
            startGame(true);  // Retry with force=true
        }
        return;
    }

    // Populate modal with current media info
    entityNameEl.textContent = getFriendlyEntityName(currentMedia.entity_id);
    titleEl.textContent = currentMedia.title || 'Unknown Title';
    artistEl.textContent = `by ${currentMedia.artist || 'Unknown Artist'}`;

    // Show modal
    modal.classList.remove('hidden');

    // Setup button listeners (one-time setup)
    setupConflictModalListeners();

    console.log('Conflict warning modal shown:', currentMedia);
}

/**
 * Hide conflict warning modal
 * Story 7.3: AC-2 (Cancel button returns to config)
 */
function hideConflictWarningModal() {
    const modal = document.getElementById('conflict-warning-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

/**
 * Setup event listeners for conflict modal buttons
 * Story 7.3: AC-2 (Proceed/Cancel buttons)
 */
function setupConflictModalListeners() {
    const cancelBtn = document.getElementById('conflict-cancel-btn');
    const proceedBtn = document.getElementById('conflict-proceed-btn');

    if (!cancelBtn || !proceedBtn) {
        console.error('Conflict modal buttons not found');
        return;
    }

    // Remove existing listeners to avoid duplicates
    cancelBtn.replaceWith(cancelBtn.cloneNode(true));
    proceedBtn.replaceWith(proceedBtn.cloneNode(true));

    // Get fresh references after cloning
    const freshCancelBtn = document.getElementById('conflict-cancel-btn');
    const freshProceedBtn = document.getElementById('conflict-proceed-btn');

    // AC-2: Cancel button - hide modal and return to config
    freshCancelBtn.addEventListener('click', () => {
        console.log('User cancelled game start (media player conflict)');
        hideConflictWarningModal();
    });

    // AC-2, AC-3: Proceed button - retry with force=true
    freshProceedBtn.addEventListener('click', async () => {
        console.log('User chose to proceed despite media player conflict');
        hideConflictWarningModal();

        // Retry startGame with force=true to save state and proceed
        await startGame(true);
    });

    // Also handle Escape key to close modal
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const modal = document.getElementById('conflict-warning-modal');
            if (modal && !modal.classList.contains('hidden')) {
                hideConflictWarningModal();
            }
        }
    });
}

/**
 * Get friendly name from entity_id
 * Helper function to display human-readable entity names
 */
function getFriendlyEntityName(entityId) {
    if (!entityId) return 'Media Player';

    // Extract domain and name: "media_player.living_room" -> "Living Room"
    const parts = entityId.split('.');
    if (parts.length > 1) {
        const name = parts[1];
        // Replace underscores with spaces and capitalize words
        return name
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    return entityId;
}

// ============================================================================
// Story 7.5: Playback Error Notification
// ============================================================================

/**
 * Show playback error notification banner to admin
 * Story 7.5: AC-2, Task 3 (Display error notification with retry/skip options)
 */
function showPlaybackErrorNotification(errorData) {
    const {
        track_title = 'Unknown Track',
        track_artist = 'Unknown Artist',
        error_message = 'Playback failed',
        retry_count = 0,
        max_retries = 3,
        can_retry = true
    } = errorData;

    // Create error notification banner
    const banner = document.createElement('div');
    banner.id = 'playback-error-banner';
    banner.className = 'fixed top-4 left-1/2 transform -translate-x-1/2 z-50 max-w-lg w-full mx-4';
    banner.innerHTML = `
        <div class="bg-red-50 border-2 border-red-500 rounded-lg p-4 shadow-lg">
            <div class="flex items-start">
                <div class="flex-shrink-0">
                    <svg class="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                </div>
                <div class="ml-3 flex-1">
                    <h3 class="text-sm font-medium text-red-800">Playback Failed</h3>
                    <div class="mt-2 text-sm text-red-700">
                        <p>Could not play "<strong>${track_title}</strong>" by <strong>${track_artist}</strong></p>
                        <p class="mt-1 text-xs">${error_message}</p>
                        ${retry_count > 0 ? `<p class="mt-1 text-xs">Retry attempts: ${retry_count}/${max_retries}</p>` : ''}
                    </div>
                    ${can_retry ? `
                        <div class="mt-4 flex gap-2">
                            <button id="playback-error-skip-btn" class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors text-sm font-medium">
                                Skip to Next Song
                            </button>
                            <button id="playback-error-dismiss-btn" class="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors text-sm font-medium">
                                Dismiss
                            </button>
                        </div>
                    ` : `
                        <div class="mt-4">
                            <p class="text-sm font-semibold text-red-900">⚠️ Max retries exhausted. Please check:</p>
                            <ul class="mt-2 text-xs text-red-800 list-disc list-inside">
                                <li>Spotify connection status</li>
                                <li>Media player availability</li>
                                <li>Network connectivity</li>
                            </ul>
                            <button id="playback-error-dismiss-btn" class="mt-3 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors text-sm font-medium">
                                Dismiss and Check Settings
                            </button>
                        </div>
                    `}
                </div>
                <div class="ml-auto pl-3">
                    <button id="playback-error-close-btn" class="inline-flex text-red-400 hover:text-red-600 focus:outline-none">
                        <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    `;

    // Remove any existing error banner
    const existingBanner = document.getElementById('playback-error-banner');
    if (existingBanner) {
        existingBanner.remove();
    }

    // Add to document
    document.body.appendChild(banner);

    // Setup event listeners
    const closeBtn = document.getElementById('playback-error-close-btn');
    const dismissBtn = document.getElementById('playback-error-dismiss-btn');
    const skipBtn = document.getElementById('playback-error-skip-btn');

    const closeBanner = () => {
        banner.remove();
    };

    closeBtn.addEventListener('click', closeBanner);
    dismissBtn.addEventListener('click', closeBanner);

    if (skipBtn && can_retry) {
        skipBtn.addEventListener('click', async () => {
            console.log('Admin clicked "Skip to Next Song"');
            closeBanner();

            // Story 7.5 Task 4: Send skip_song WebSocket command
            try {
                const result = await sendWebSocketCommand('beatsy/skip_song', {});

                if (result.success) {
                    console.log(`Successfully skipped to round ${result.result.round_number}`);
                    showToast(`Skipped to new song (Round ${result.result.round_number})`, 'success');
                } else {
                    console.error('Skip song failed:', result.error);
                    showToast(`Failed to skip: ${result.error?.message || 'Unknown error'}`, 'error');
                }
            } catch (error) {
                console.error('Error sending skip_song command:', error);
                showToast('Failed to skip song', 'error');
            }
        });
    }

    // Auto-dismiss after 30 seconds for non-critical errors
    if (can_retry) {
        setTimeout(() => {
            if (document.getElementById('playback-error-banner')) {
                closeBanner();
            }
        }, 30000);
    }

    console.log('Playback error notification displayed:', errorData);
}

/**
 * Export functions for testing (optional - for future test suite)
 */
export {
    initAdminUI,
    verifyPageStructure,
    setupPlaceholderListeners,
    detectMobileDevice,
    loadMediaPlayers,
    loadPlaylists,
    validateGameSettings,
    showValidationError,
    clearValidationError,
    saveSettingsToLocalStorage,
    loadSettingsFromLocalStorage,
    startGame,
    showToast,
    displayPlayerUrl,
    setupCopyButton,
    // Story 3.7 exports
    loadGameStatus,
    updateStatusPanel,
    formatGameState,
    showNoGameStatus,
    updateConnectionStatus,
    loadGameStatusWithRetry,
    initGameStatus,
    // Story 7.3 exports
    showConflictWarningModal,
    hideConflictWarningModal,
    setupConflictModalListeners,
    getFriendlyEntityName,
    // Story 7.5 exports
    showPlaybackErrorNotification
};
