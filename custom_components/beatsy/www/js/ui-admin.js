/**
 * Beatsy Admin UI - JavaScript Initialization
 * ES6 module for admin interface initialization
 * Mobile-first, vanilla JavaScript (no frameworks)
 */

/**
 * Story 11.1: Load game configuration from backend on page initialization
 * Fetches persisted config from /api/beatsy/api/config and populates form fields
 */
async function loadConfigFromBackend() {
    try {
        console.log('Loading config from backend...');
        const response = await fetch('/api/beatsy/api/config');

        if (!response.ok) {
            throw new Error(`Config load failed: ${response.status}`);
        }

        const config = await response.json();

        // Handle empty config (first installation or no config saved yet)
        if (!config || Object.keys(config).length === 0) {
            console.log('No persisted config found, using defaults');
            return;
        }

        // Populate gameConfig state
        if (config.media_player) gameConfig.mediaPlayer = config.media_player;
        if (config.playlist_id) gameConfig.playlist = config.playlist_id;
        if (config.timer_duration) gameConfig.timerDuration = config.timer_duration;
        if (config.round_timer_seconds) gameConfig.timerDuration = config.round_timer_seconds;
        if (config.year_range_min) gameConfig.yearRangeMin = config.year_range_min;
        if (config.year_range_max) gameConfig.yearRangeMax = config.year_range_max;
        if (config.exact_points) gameConfig.exactPoints = config.exact_points;
        if (config.points_exact) gameConfig.exactPoints = config.points_exact;
        if (config.close_points) gameConfig.closePoints = config.close_points;
        if (config.points_close) gameConfig.closePoints = config.points_close;
        if (config.near_points) gameConfig.nearPoints = config.near_points;
        if (config.points_near) gameConfig.nearPoints = config.points_near;
        if (config.bet_multiplier) gameConfig.betMultiplier = config.bet_multiplier;
        if (config.points_bet_multiplier) gameConfig.betMultiplier = config.points_bet_multiplier;

        // Populate form inputs
        const timerInput = document.getElementById('timer-duration');
        if (timerInput && gameConfig.timerDuration) {
            timerInput.value = gameConfig.timerDuration;
        }

        const yearMinInput = document.getElementById('year-range-min');
        if (yearMinInput && gameConfig.yearRangeMin) {
            yearMinInput.value = gameConfig.yearRangeMin;
        }

        const yearMaxInput = document.getElementById('year-range-max');
        if (yearMaxInput && gameConfig.yearRangeMax) {
            yearMaxInput.value = gameConfig.yearRangeMax;
        }

        const exactPointsInput = document.getElementById('exact-points');
        if (exactPointsInput && gameConfig.exactPoints) {
            exactPointsInput.value = gameConfig.exactPoints;
        }

        const closePointsInput = document.getElementById('close-points');
        if (closePointsInput && gameConfig.closePoints) {
            closePointsInput.value = gameConfig.closePoints;
        }

        const nearPointsInput = document.getElementById('near-points');
        if (nearPointsInput && gameConfig.nearPoints) {
            nearPointsInput.value = gameConfig.nearPoints;
        }

        const betMultiplierInput = document.getElementById('bet-multiplier');
        if (betMultiplierInput && gameConfig.betMultiplier) {
            betMultiplierInput.value = gameConfig.betMultiplier;
        }

        // Media player and playlist will be auto-selected by their respective load functions
        // after the dropdown options are populated

        console.log('✓ Config loaded from backend:', config);
    } catch (error) {
        console.error('Failed to load config from backend:', error);
        // Don't show error to user - gracefully fall back to defaults
        // The form will work with manual configuration
    }
}

/**
 * Initialize admin UI on DOM ready
 */
async function initAdminUI() {
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

    // Initialize year range inputs with current year
    initializeYearRange();

    // Story 11.1: Load config from backend BEFORE localStorage
    // This ensures persisted config takes precedence
    await loadConfigFromBackend();

    // Setup collapsible sections
    setupCollapsibleSections();

    // Setup placeholder event listeners (will be implemented in later stories)
    setupPlaceholderListeners();

    // Story 3.2: Load media players on page initialization
    loadMediaPlayers();

    // Story 3.3: Load playlists on page initialization
    loadPlaylists();

    // Story 3.4: Load game settings from localStorage (as fallback only)
    // Note: Backend config already loaded above, this is backup
    loadSettingsFromLocalStorage();
    setupGameSettingsListeners();

    // Story 3.5: Initialize Start Game button state
    updateStartGameButton();

    // Story 3.7: Initialize game status display
    initGameStatus();

    // Story 11.6: Initialize QR modal event listeners
    initQRModal();

    // Log successful initialization
    console.log('DOM ready - All sections loaded successfully');
}

/**
 * Initialize year range inputs with current year
 * Sets max attribute and default value to current year
 */
function initializeYearRange() {
    const currentYear = new Date().getFullYear();
    const yearMinInput = document.getElementById('year-range-min');
    const yearMaxInput = document.getElementById('year-range-max');

    if (yearMinInput) {
        yearMinInput.max = currentYear;
    }

    if (yearMaxInput) {
        yearMaxInput.max = currentYear;
        // Only set value if not already set (e.g., from localStorage)
        if (!yearMaxInput.value) {
            yearMaxInput.value = currentYear;
        }
    }

    // Update gameConfig default
    if (!gameConfig.yearRangeMax || gameConfig.yearRangeMax === 2024) {
        gameConfig.yearRangeMax = currentYear;
    }

    console.log(`Year range initialized: min=1900, max=${currentYear}`);
}

/**
 * Setup collapsible sections with chevron rotation
 * Handles Game Configuration and Game Settings collapse/expand
 */
function setupCollapsibleSections() {
    // Game Configuration collapse
    const gameConfigToggle = document.getElementById('game-config-toggle');
    const gameConfigContent = document.getElementById('game-config-content');
    const gameConfigChevron = document.getElementById('game-config-chevron');

    if (gameConfigToggle && gameConfigContent && gameConfigChevron) {
        gameConfigToggle.addEventListener('click', () => {
            const isExpanded = gameConfigToggle.getAttribute('aria-expanded') === 'true';

            if (isExpanded) {
                // Collapse
                gameConfigContent.classList.add('hidden');
                gameConfigToggle.setAttribute('aria-expanded', 'false');
                gameConfigChevron.classList.remove('rotate-180');
            } else {
                // Expand
                gameConfigContent.classList.remove('hidden');
                gameConfigToggle.setAttribute('aria-expanded', 'true');
                gameConfigChevron.classList.add('rotate-180');
            }
        });
        console.log('✓ Game Configuration collapse initialized');
    }

    // Game Settings collapse
    const gameSettingsToggle = document.getElementById('game-settings-toggle');
    const gameSettingsContent = document.getElementById('game-settings-content');
    const gameSettingsChevron = document.getElementById('game-settings-chevron');

    if (gameSettingsToggle && gameSettingsContent && gameSettingsChevron) {
        gameSettingsToggle.addEventListener('click', () => {
            const isExpanded = gameSettingsToggle.getAttribute('aria-expanded') === 'true';

            if (isExpanded) {
                // Collapse
                gameSettingsContent.classList.add('hidden');
                gameSettingsToggle.setAttribute('aria-expanded', 'false');
                gameSettingsChevron.classList.remove('rotate-180');
            } else {
                // Expand
                gameSettingsContent.classList.remove('hidden');
                gameSettingsToggle.setAttribute('aria-expanded', 'true');
                gameSettingsChevron.classList.add('rotate-180');
            }
        });
        console.log('✓ Game Settings collapse initialized');
    }
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
    yearRangeMax: new Date().getFullYear(),     // Year range maximum (current year)
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

    // Story 11.1: Restore from backend config first (gameConfig.mediaPlayer set by loadConfigFromBackend)
    // Then fallback to localStorage if no backend config
    let selectedPlayer = gameConfig.mediaPlayer || localStorage.getItem('beatsy_media_player');

    if (selectedPlayer) {
        // Check if saved player exists in current list
        const playerExists = players.some(p => p.entity_id === selectedPlayer);
        if (playerExists) {
            dropdown.value = selectedPlayer;
            gameConfig.mediaPlayer = selectedPlayer;
            console.log('Restored media player selection:', selectedPlayer);

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

    // Story 11.1: Restore from backend config first (gameConfig.playlist set by loadConfigFromBackend)
    // Then fallback to localStorage if no backend config
    let selectedPlaylist = gameConfig.playlist || localStorage.getItem('beatsy_playlist');

    if (selectedPlaylist) {
        // Check if saved playlist exists in current list
        const playlistExists = playlists.some(p => p.playlist_id === selectedPlaylist);
        if (playlistExists) {
            dropdown.value = selectedPlaylist;
            gameConfig.playlist = selectedPlaylist;
            console.log('Restored playlist selection:', selectedPlaylist);

            // Show visual feedback and metadata
            const selectedPlaylistObj = playlists.find(p => p.playlist_id === selectedPlaylist);
            updatePlaylistVisualFeedback(dropdown, true, selectedPlaylistObj);
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
        'game-control',
        'game-status',
        'game-config-collapsed',
        'game-settings-collapsed'
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

    // Start Round button (sends beatsy/next_song command)
    const startRoundBtn = document.getElementById('start-round-btn');
    if (startRoundBtn) {
        startRoundBtn.addEventListener('click', async (e) => {
            await startRound();
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
    const currentYear = new Date().getFullYear();

    if (isNaN(yearMin) || yearMin < 1900 || yearMin > currentYear) {
        errors.yearMin = `Year min must be between 1900-${currentYear}`;
    }
    if (isNaN(yearMax) || yearMax < 1900 || yearMax > currentYear) {
        errors.yearMax = `Year max must be between 1900-${currentYear}`;
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
            // Double-check: if admin_key is missing, this might be a conflict warning
            if (!data.admin_key && data.conflict_warning) {
                console.log('Conflict warning detected (fallback check):', data.current_media);
                showConflictWarningModal(data.current_media);

                // Reset button state
                startGameBtn.disabled = false;
                spinnerElement.classList.add('hidden');
                buttonTextElement.textContent = 'Start Game';
                return;
            }

            // Success! Handle 200 response
            console.log('Game started successfully:', data);

            // Story 3.6 Task 1: Save admin_key and game_id to localStorage with 24-hour expiry
            localStorage.setItem('beatsy_admin_key', data.admin_key);
            localStorage.setItem('beatsy_admin_key_expiry', Date.now() + (24 * 60 * 60 * 1000)); // 24 hours
            localStorage.setItem('beatsy_game_id', data.game_id);

            // Log admin key storage (security: first 8 chars only)
            console.log('Admin key stored:', data.admin_key.substring(0, 8) + '... (expires in 24 hours)');

            // Story 11.7: Hide Start Game button and show Game Active badge
            spinnerElement.classList.add('hidden');
            startGameBtn.classList.add('hidden');
            const gameActiveBadge = document.getElementById('game-active-badge');
            if (gameActiveBadge) {
                gameActiveBadge.classList.remove('hidden');
                console.log('✓ Game Active badge shown, Start Game button hidden');
            }

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
/**
 * Start a new round by sending beatsy/next_song command
 * Shows/hides the button based on game state (lobby or results)
 */
async function startRound() {
    const startRoundBtn = document.getElementById('start-round-btn');
    const startRoundText = document.getElementById('start-round-text');

    try {
        console.log('Starting new round...');

        // Disable button to prevent double-click
        startRoundBtn.disabled = true;
        if (startRoundText) {
            startRoundText.textContent = 'Starting...';
        }

        // Send WebSocket next_song command using helper
        const result = await sendWebSocketCommand('beatsy/next_song', {});

        if (result.success) {
            console.log('Round started successfully:', result.result);
            showToast(`Round ${result.result.round_number} started!`, 'success');

            // Hide the button - it will be shown again when round ends
            setTimeout(() => {
                startRoundBtn.classList.add('hidden');
                startRoundBtn.disabled = false;
                if (startRoundText) {
                    startRoundText.textContent = 'Start Round';
                }
            }, 500);
        } else {
            throw new Error(result.error?.message || 'Failed to start round');
        }

    } catch (error) {
        console.error('Error starting round:', error);
        showToast('Failed to start round: ' + error.message, 'error');

        // Re-enable button on error
        startRoundBtn.disabled = false;
        if (startRoundText) {
            startRoundText.textContent = 'Start Round';
        }
    }
}

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

    // Story 11.7: Show Start Game button and hide Game Active badge
    const startGameBtn = document.getElementById('start-game-btn');
    const startGameText = document.getElementById('start-game-text');
    const spinner = document.getElementById('start-game-spinner');

    if (startGameBtn) {
        startGameBtn.classList.remove('hidden');
        startGameBtn.disabled = false;  // Re-enable (if config valid)
        if (spinner) spinner.classList.add('hidden');
        if (startGameText) startGameText.textContent = 'Start Game';

        const gameActiveBadge = document.getElementById('game-active-badge');
        if (gameActiveBadge) {
            gameActiveBadge.classList.add('hidden');
            console.log('✓ Start Game button shown, Game Active badge hidden (game reset)');
        }
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

    // Use the correct player URL path (no game_id parameter needed - it's in localStorage)
    // The player interface will read game_id and admin_key from localStorage
    const playerUrl = `/api/beatsy/player`;

    console.log('Redirecting to player registration:', playerUrl);
    console.log('Game ID in localStorage:', gameId);
    console.log('Admin key in localStorage:', !!localStorage.getItem('beatsy_admin_key'));

    // Navigate to player registration page
    window.location.href = playerUrl;
}

// Story 11.6: Store player URL globally for modal access
let currentPlayerUrl = '';

/**
 * Display player URL after successful game start
 * Story 3.5: AC-8 (Player URL Display)
 * Story 11.6: Modified to show QR icon instead of inline section
 */
function displayPlayerUrl(playerUrl) {
    // Store player URL for modal access
    currentPlayerUrl = playerUrl;

    const qrIconBtn = document.getElementById('qr-icon-btn');

    if (!qrIconBtn) {
        console.error('QR icon button not found');
        return;
    }

    // Show the QR icon
    qrIconBtn.classList.remove('hidden');

    console.log('QR icon displayed, player URL stored:', playerUrl);
}

// ============================================================================
// Story 11.6: QR Code Modal Functions
// ============================================================================

/**
 * Generate QR code from player URL
 * Story 11.6: AC-4 (QR code generation with error handling)
 */
function generateQRCode(playerUrl) {
    const canvas = document.getElementById('qr-canvas');

    if (!canvas) {
        console.error('QR canvas element not found');
        return;
    }

    // Check if QRCode library is available
    if (typeof QRCode === 'undefined') {
        console.error('QRCode library not loaded');
        alert('QR code generation unavailable. Please use the URL to share manually.');
        return;
    }

    QRCode.toCanvas(canvas, playerUrl, {
        width: 200,
        margin: 2,
        color: {
            dark: '#000000',
            light: '#FFFFFF'
        }
    }, (error) => {
        if (error) {
            console.error('QR generation failed:', error);
            alert('Failed to generate QR code. Please use the URL to share manually.');
        } else {
            console.log('QR code generated successfully');
        }
    });
}

/**
 * Show QR code modal with player URL
 * Story 11.6: AC-3, AC-5 (Display modal with QR code and URL)
 */
function showQRModal() {
    const modal = document.getElementById('qr-modal');
    const urlInput = document.getElementById('qr-modal-player-url');

    if (!modal || !urlInput) {
        console.error('QR modal elements not found');
        return;
    }

    // Show modal
    modal.classList.remove('hidden');

    // Set player URL
    urlInput.value = currentPlayerUrl;

    // Generate QR code
    generateQRCode(currentPlayerUrl);

    // Setup copy button for modal
    setupModalCopyButton();

    console.log('QR modal opened');
}

/**
 * Hide QR code modal
 * Story 11.6: AC-3 (Close modal functionality)
 */
function hideQRModal() {
    const modal = document.getElementById('qr-modal');

    if (!modal) {
        console.error('QR modal not found');
        return;
    }

    modal.classList.add('hidden');
    console.log('QR modal closed');
}

/**
 * Setup copy button for modal
 * Story 11.6: AC-5 (Copy button functionality)
 */
function setupModalCopyButton() {
    const copyBtn = document.getElementById('qr-modal-copy-btn');
    const urlInput = document.getElementById('qr-modal-player-url');

    if (!copyBtn || !urlInput) return;

    // Remove existing listener to avoid duplicates
    copyBtn.replaceWith(copyBtn.cloneNode(true));
    const newCopyBtn = document.getElementById('qr-modal-copy-btn');

    newCopyBtn.addEventListener('click', async () => {
        try {
            await navigator.clipboard.writeText(urlInput.value);

            // Visual feedback
            const originalHTML = newCopyBtn.innerHTML;
            newCopyBtn.innerHTML = '<span class="text-sm">Copied!</span>';

            setTimeout(() => {
                newCopyBtn.innerHTML = originalHTML;
            }, 2000);

            console.log('Player URL copied to clipboard from modal');
        } catch (err) {
            console.error('Failed to copy URL:', err);
            alert('Failed to copy URL. Please copy manually.');
        }
    });
}

/**
 * Initialize QR modal event listeners
 * Story 11.6: AC-1, AC-3 (Event listeners for all close methods)
 */
function initQRModal() {
    const qrIconBtn = document.getElementById('qr-icon-btn');
    const qrModalClose = document.getElementById('qr-modal-close');
    const qrModal = document.getElementById('qr-modal');

    // QR icon click
    if (qrIconBtn) {
        qrIconBtn.addEventListener('click', showQRModal);

        // Keyboard support (Enter or Space)
        qrIconBtn.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                showQRModal();
            }
        });
    }

    // Close button click
    if (qrModalClose) {
        qrModalClose.addEventListener('click', hideQRModal);
    }

    // Click outside modal to close
    if (qrModal) {
        qrModal.addEventListener('click', (e) => {
            if (e.target === qrModal) {
                hideQRModal();
            }
        });
    }

    // Escape key to close
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const modal = document.getElementById('qr-modal');
            if (modal && !modal.classList.contains('hidden')) {
                hideQRModal();
            }
        }
    });

    console.log('QR modal event listeners initialized');
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

            // If game is active (not in setup state), update UI accordingly
            if (data.state !== 'setup') {
                updateUIForActiveGame(data);
            }
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

    // Update player count circle (Story 11.5)
    updatePlayerCountCircle(status.player_count || 0);

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

    // Story 11.3: Update players ticker (AC-3, AC-6)
    if (status.players && Array.isArray(status.players)) {
        updatePlayersList(status.players);
    }

    console.log('Status panel updated:', status);
}

/**
 * Update UI elements when an active game is detected on page load
 * Restores game active state: button states, Join as Player visibility, etc.
 */
function updateUIForActiveGame(gameStatus) {
    console.log('Restoring UI for active game:', gameStatus);

    // Restore game_id to localStorage if available
    // This ensures "Join as Player" works after page reload
    if (gameStatus.game_id && gameStatus.game_id !== 'unknown') {
        localStorage.setItem('beatsy_game_id', gameStatus.game_id);
        console.log('✓ Game ID restored to localStorage:', gameStatus.game_id);
    }

    // Story 11.7: Hide Start Game button and show Game Active badge
    const startGameBtn = document.getElementById('start-game-btn');
    const spinnerElement = document.getElementById('start-game-spinner');

    if (startGameBtn && spinnerElement) {
        startGameBtn.classList.add('hidden');
        spinnerElement.classList.add('hidden');
        const gameActiveBadge = document.getElementById('game-active-badge');
        if (gameActiveBadge) {
            gameActiveBadge.classList.remove('hidden');
            console.log('✓ Game Active badge shown, Start Game button hidden (reconnection)');
        }
    }

    // Show "Join as Player" button if game is in lobby or active state
    if (gameStatus.state === 'lobby' || gameStatus.state === 'active' || gameStatus.state === 'results') {
        const joinAsPlayerBtn = document.getElementById('join-as-player-btn');
        if (joinAsPlayerBtn) {
            joinAsPlayerBtn.classList.remove('hidden');
            console.log('✓ "Join as Player" button shown');
        }
    }

    // Show "Start Round" button if game is in lobby or results state (waiting to start next round)
    if (gameStatus.state === 'lobby' || gameStatus.state === 'results') {
        const startRoundBtn = document.getElementById('start-round-btn');
        if (startRoundBtn) {
            startRoundBtn.classList.remove('hidden');
            startRoundBtn.disabled = false;
            const startRoundText = document.getElementById('start-round-text');
            if (startRoundText) {
                startRoundText.textContent = gameStatus.state === 'lobby' ? 'Start First Round' : 'Next Round';
            }
            console.log('✓ "Start Round" button shown');
        }
    }

    // Display player URL if we have the host information
    const playerUrl = `${window.location.protocol}//${window.location.host}/api/beatsy/player`;
    if (typeof displayPlayerUrl === 'function') {
        displayPlayerUrl(playerUrl);
        console.log('✓ Player URL displayed:', playerUrl);
    }
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

    // Story 11.5: Use player count circle instead of deleted status-players element
    updatePlayerCountCircle(0);

    const songsElement = document.getElementById('status-songs');
    if (songsElement) songsElement.textContent = '-';

    const roundElement = document.getElementById('status-round');
    if (roundElement) roundElement.textContent = '-';

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
 * Story 11.5: Updated to use circle-only indicator with tooltip
 */
function updateConnectionStatus(connected) {
    const circle = document.getElementById('connection-indicator-circle');
    if (!circle) return;

    if (connected) {
        circle.classList.remove('bg-gray-400', 'bg-red-500');
        circle.classList.add('bg-green-500');
        circle.title = 'Connected';
        console.log('Connection status: Connected');
    } else {
        circle.classList.remove('bg-gray-400', 'bg-green-500');
        circle.classList.add('bg-red-500');
        circle.title = 'Reconnecting...';
        console.log('Connection status: Disconnected');
    }
}

/**
 * Get player count circle color based on count
 * Story 11.5: Helper function for dynamic circle color
 * @param {number} count - Current player count
 * @returns {string} Tailwind color class
 */
function getPlayerCountColor(count) {
    if (count === 0) return 'bg-gray-400';
    if (count <= 3) return 'bg-blue-500';
    return 'bg-green-500';
}

/**
 * Update player count circle display
 * Story 11.5: Shows player count in colored circle
 * @param {number} count - Current player count
 */
function updatePlayerCountCircle(count) {
    const circle = document.getElementById('player-count-circle');
    if (!circle) return;

    // Update count display
    circle.textContent = count;

    // Update color based on count
    circle.classList.remove('bg-gray-400', 'bg-blue-500', 'bg-green-500');
    const colorClass = getPlayerCountColor(count);
    circle.classList.add(colorClass);

    console.log(`Player count circle updated: ${count} players`);
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
 * WebSocket connection variables
 */
let connectionAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;

/**
 * Connect to Beatsy WebSocket for real-time updates
 * Story 3.7: WebSocket integration for admin UI
 */
function connectWebSocket() {
    try {
        // Connect to Beatsy WebSocket
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/api/beatsy/ws`;
        console.log('Connecting to WebSocket:', wsUrl);

        window.ws = new WebSocket(wsUrl);

        window.ws.onopen = () => {
            console.log('✅ Connected to Beatsy WebSocket');
            connectionAttempts = 0;
            updateConnectionStatus(true);

            // Load game status when connected
            loadGameStatus();
        };

        window.ws.onmessage = (event) => {
            handleWebSocketMessage(event);
        };

        window.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            updateConnectionStatus(false);
        };

        window.ws.onclose = () => {
            console.warn('WebSocket connection closed');
            updateConnectionStatus(false);
            attemptReconnect();
        };

    } catch (error) {
        console.error('Failed to establish WebSocket connection:', error);
        updateConnectionStatus(false);
    }
}

/**
 * Attempt to reconnect with exponential backoff
 */
function attemptReconnect() {
    if (connectionAttempts >= MAX_RECONNECT_ATTEMPTS) {
        console.error('Max reconnection attempts reached');
        updateConnectionStatus(false);
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
 * Send WebSocket command and wait for response
 */
let messageIdCounter = 1;
const pendingMessages = new Map();

function sendWebSocketCommand(type, payload = {}) {
    return new Promise((resolve, reject) => {
        if (!window.ws || window.ws.readyState !== WebSocket.OPEN) {
            reject(new Error('WebSocket not connected'));
            return;
        }

        const messageId = messageIdCounter++;
        const message = {
            id: messageId,
            type: type,
            ...payload
        };

        // Store promise callbacks
        pendingMessages.set(messageId, { resolve, reject });

        // Set timeout for response
        setTimeout(() => {
            if (pendingMessages.has(messageId)) {
                pendingMessages.delete(messageId);
                reject(new Error('WebSocket command timeout'));
            }
        }, 10000); // 10 second timeout

        // Send message
        window.ws.send(JSON.stringify(message));
        console.log('Sent WebSocket command:', message);
    });
}

/**
 * Handle incoming WebSocket messages
 */
function handleWebSocketMessage(event) {
    try {
        const data = JSON.parse(event.data);
        console.log('WebSocket message received:', data);

        // Handle command responses
        if (data.id && pendingMessages.has(data.id)) {
            const { resolve, reject } = pendingMessages.get(data.id);
            pendingMessages.delete(data.id);

            if (data.success === false || data.error) {
                reject(data);
            } else {
                resolve(data);
            }
            return;
        }

        // Handle different event types
        if (data.type === 'beatsy/event') {
            switch (data.event_type) {
                case 'game_reset':
                    console.log('🔄 Game reset event received');
                    handleAdminGameReset(data.data);
                    break;

                case 'playback_error':
                    console.log('⚠️ Playback error event received');
                    showPlaybackErrorNotification(data.data);
                    break;

                case 'player_joined':
                    console.log('👤 Player joined event received:', data.data);
                    // Story 11.3: Add player to ticker immediately (AC-1, AC-2, AC-5)
                    if (data.data && data.data.player_name) {
                        addPlayerToTicker(data.data.player_name);
                        // Story 11.5: Update player count circle (AC-13)
                        if (data.data.total_players !== undefined) {
                            updatePlayerCountCircle(data.data.total_players);
                        } else {
                            // Fallback: count from ticker children
                            const ticker = document.getElementById('players-list');
                            if (ticker) {
                                updatePlayerCountCircle(ticker.children.length);
                            }
                        }
                    }
                    // Also reload game status to ensure consistency
                    loadGameStatus();
                    break;

                case 'round_started':
                    console.log('🎵 Round started event received');
                    loadGameStatus();
                    break;

                case 'round_ended':
                    console.log('🏁 Round ended event received');
                    loadGameStatus();
                    break;

                case 'game_status_update':
                    console.log('📊 Game status update event received');
                    loadGameStatus();
                    break;

                default:
                    console.log('Unknown event type:', data.event_type);
            }
        }
    } catch (error) {
        console.error('Error parsing WebSocket message:', error);
    }
}

/**
 * Setup WebSocket event listeners for game status updates
 * Story 3.7 Task 5: AC-3, AC-4, AC-5 (WebSocket listeners)
 */
function setupGameStatusWebSocketListeners() {
    console.log('Setting up WebSocket connection...');
    connectWebSocket();

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

    // Story 11.3: Set up periodic API sync for reliability (AC-6)
    // Poll game_status endpoint every 30 seconds to recover from missed WebSocket messages
    setInterval(async () => {
        try {
            const response = await fetch('/api/beatsy/api/game_status');
            if (response.ok) {
                const data = await response.json();
                if (data.players && Array.isArray(data.players)) {
                    updatePlayersList(data.players);
                }
            }
        } catch (error) {
            console.debug('Periodic sync failed (non-critical):', error.message);
        }
    }, 30000);  // 30 seconds

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

// ============================================================================
// Story 11.3: Admin Player Ticker Functions
// ============================================================================

/**
 * Add a player badge to the admin ticker
 * Story 11.3: AC-2, AC-3, AC-4
 */
function addPlayerToTicker(playerName) {
    const playersList = document.getElementById('players-list');
    if (!playersList) {
        console.warn('Players list element not found');
        return;
    }

    // Check for duplicate using dataset attribute
    const existing = playersList.querySelector(`[data-player-name="${playerName}"]`);
    if (existing) {
        console.log('Player badge already exists:', playerName);
        return;
    }

    // Create badge element
    const badge = document.createElement('span');
    badge.className = 'px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm';
    badge.textContent = playerName;
    badge.dataset.playerName = playerName;  // For deduplication

    // Append badge (chronological order - append to end)
    playersList.appendChild(badge);

    console.log('Player badge added to ticker:', playerName);
}

/**
 * Update players list from API response (periodic sync)
 * Story 11.3: AC-6 (Periodic API sync for reliability)
 */
function updatePlayersList(players) {
    const playersList = document.getElementById('players-list');
    if (!playersList) {
        console.warn('Players list element not found');
        return;
    }

    // Get current players from DOM
    const currentPlayers = new Set(
        Array.from(playersList.children).map(badge => badge.dataset.playerName)
    );

    // Add any missing players from API response
    let addedCount = 0;
    players.forEach(player => {
        if (!currentPlayers.has(player.name)) {
            addPlayerToTicker(player.name);
            addedCount++;
        }
    });

    if (addedCount > 0) {
        console.log(`Periodic sync: Added ${addedCount} missing player(s)`);
    }
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
    showPlaybackErrorNotification,
    // Story 11.6 exports
    generateQRCode,
    showQRModal,
    hideQRModal,
    setupModalCopyButton,
    initQRModal
};
