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
async function startGame() {
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

        console.log('Starting game with config:', config);

        // POST to start_game endpoint
        const response = await fetch('/api/beatsy/api/start_game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ config })
        });

        const data = await response.json();

        if (response.ok) {
            // Success! Handle 200 response
            console.log('Game started successfully:', data);

            // Save admin_key and game_id to localStorage
            localStorage.setItem('beatsy_admin_key', data.admin_key);
            localStorage.setItem('beatsy_game_id', data.game_id);

            // Update button state to "Game Active"
            buttonTextElement.textContent = 'Game Active';
            spinnerElement.classList.add('hidden');
            startGameBtn.disabled = true;  // Keep disabled

            // Display player URL (Task 7-8 will handle this)
            if (typeof displayPlayerUrl === 'function') {
                displayPlayerUrl(data.player_url);
            } else {
                console.log('Player URL:', data.player_url);
            }

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
    setupCopyButton
};
