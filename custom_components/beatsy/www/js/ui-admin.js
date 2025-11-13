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

    // Log successful initialization
    console.log('DOM ready - All sections loaded successfully');
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
    // Story 3.2: Media player selector
    const mediaPlayerSelect = document.getElementById('media-player');
    if (mediaPlayerSelect) {
        mediaPlayerSelect.addEventListener('change', (e) => {
            console.log('Media player changed (placeholder):', e.target.value);
            // TODO: Story 3.2 - Implement media player selection logic
        });
    }

    // Story 3.3: Playlist URI input
    const playlistInput = document.getElementById('playlist-uri');
    if (playlistInput) {
        playlistInput.addEventListener('input', (e) => {
            console.log('Playlist URI input (placeholder):', e.target.value);
            // TODO: Story 3.3 - Implement playlist validation logic
        });
    }

    // Story 3.5: Start game button
    const startGameBtn = document.getElementById('start-game-btn');
    if (startGameBtn) {
        startGameBtn.addEventListener('click', (e) => {
            console.log('Start game clicked (placeholder)');
            // TODO: Story 3.5 - Implement start game logic
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

/**
 * Export functions for testing (optional - for future test suite)
 */
export {
    initAdminUI,
    verifyPageStructure,
    setupPlaceholderListeners,
    detectMobileDevice
};
