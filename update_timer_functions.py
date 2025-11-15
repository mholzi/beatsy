#!/usr/bin/env python3
"""
Script to update timer functions in ui-player.js for Story 8.5
"""

def update_timer_functions():
    file_path = "/Volumes/My Passport/HA_Dashboard/custom_components/beatsy/www/js/ui-player.js"

    with open(file_path, 'r') as f:
        content = f.read()

    # Find and replace the startTimer function
    old_start_timer = '''/**
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
}'''

    new_timer_functions = '''/**
 * Story 8.5 Task 1: Update timer display with remaining time
 * AC-1: Remaining seconds displayed prominently (e.g., "28s")
 * AC-3: Timer calculated client-side from started_at timestamp
 * AC-5: Color changes to red when < 10 seconds remaining
 * AC-6: Timer accuracy within ±1 second of server time
 * @returns {number} Remaining seconds (for testing/validation)
 */
function updateTimer() {
    const timerDisplay = document.getElementById('timer');
    if (!timerDisplay) {
        console.error('Timer display element not found');
        return 0;
    }

    // AC-3: Calculate remaining time from server timestamp
    const now = Date.now();
    const elapsed = now - roundStartedAt;
    const remaining = Math.max(0, timerDuration - Math.floor(elapsed / 1000));

    // AC-1: Display timer in "XXs" format
    timerDisplay.textContent = `${remaining}s`;

    // AC-5: Color change for urgency (< 10 seconds)
    if (remaining < 10) {
        timerDisplay.classList.remove('text-gray-800');
        timerDisplay.classList.add('text-red-600');
    } else {
        timerDisplay.classList.remove('text-red-600');
        timerDisplay.classList.add('text-gray-800');
    }

    // AC-4: Auto-lock inputs on timer expiration
    if (remaining <= 0) {
        clearInterval(timerInterval);
        timerInterval = null;
        lockInputs();
        onTimerExpire();
        console.log('⏰ Timer expired, inputs locked');
    }

    // Debug logging for accuracy validation (AC-6)
    if (remaining % 5 === 0 && remaining > 0) {
        console.log(`[Timer] Remaining: ${remaining}s`);
    }

    return remaining;
}

/**
 * Story 8.5 Task 2: Start timer interval on round start
 * AC-2: Timer updates every second smoothly
 * AC-3: Timer calculated client-side from started_at timestamp
 * @param {number} startedAt - Unix timestamp in milliseconds
 * @param {number} duration - Timer duration in seconds
 */
function startTimer(startedAt, duration) {
    // Clear any existing timer
    stopTimer();

    // Store timer state globally
    roundStartedAt = startedAt;
    timerDuration = duration;

    console.log(`[Timer] Starting timer: started_at=${new Date(startedAt).toISOString()}, duration=${duration}s`);

    // AC-2: Update timer every 1 second (1000ms)
    timerInterval = setInterval(updateTimer, 1000);

    // Immediate first update
    updateTimer();

    console.log('✓ Timer started successfully');
}

/**
 * Story 8.5 Task 6: Stop timer on round end
 * AC-2: Timer stops cleanly on round end
 * Clears interval and resets timer state
 */
function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
        console.log('[Timer] Timer stopped and cleared');
    }

    // Reset timer display element
    const timerDisplay = document.getElementById('timer');
    if (timerDisplay) {
        timerDisplay.textContent = '--';
        timerDisplay.classList.remove('text-red-600');
        timerDisplay.classList.add('text-gray-800');
    }

    // Clear timer state variables
    roundStartedAt = null;
    timerDuration = null;
}

/**
 * Story 8.5 Task 5: Handle timer expiration
 * AC-4: When timer reaches 0, inputs are locked automatically
 * Displays waiting message and triggers expiration logic
 */
function onTimerExpire() {
    console.log('[Timer] Timer expired, waiting for results...');

    // Display waiting message
    const timerDisplay = document.getElementById('timer');
    if (timerDisplay && timerDisplay.parentElement) {
        const waitingMsg = document.createElement('p');
        waitingMsg.id = 'timer-expired-message';
        waitingMsg.className = 'text-sm text-gray-600 mt-2 text-center';
        waitingMsg.textContent = "Time's up! Waiting for results...";

        // Remove old message if exists
        const oldMsg = document.getElementById('timer-expired-message');
        if (oldMsg) {
            oldMsg.remove();
        }

        timerDisplay.parentElement.appendChild(waitingMsg);
    }

    // TODO Story 8.6+: Additional expiration logic (results transition, etc.)
}

/**
 * Story 8.5 Task 5: Lock inputs when timer expires
 * AC-4: When timer reaches 0, inputs are locked automatically
 * Disables year selector, bet toggle, and submit button
 */
function lockInputs() {
    const yearSelector = document.getElementById('year-selector');
    const betToggle = document.getElementById('bet-toggle');
    const submitButton = document.getElementById('submit-guess');

    if (yearSelector) {
        yearSelector.disabled = true;
        console.log('[Timer] Year selector locked');
    }

    if (betToggle) {
        betToggle.disabled = true;
        console.log('[Timer] Bet toggle locked');
    }

    if (submitButton) {
        submitButton.disabled = true;
        console.log('[Timer] Submit button locked');
    }

    // Update game state
    gameState.locked = true;

    console.log('✓ All inputs locked due to timer expiration');
}'''

    # Replace the old function with new functions
    if old_start_timer in content:
        content = content.replace(old_start_timer, new_timer_functions)
        print("✓ Successfully replaced startTimer function with Story 8.5 implementation")
    else:
        print("✗ Could not find old startTimer function - content may have changed")
        return False

    # Write updated content back to file
    with open(file_path, 'w') as f:
        f.write(content)

    print(f"✓ File updated successfully: {file_path}")
    return True

if __name__ == '__main__':
    update_timer_functions()
