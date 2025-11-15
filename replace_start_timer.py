#!/usr/bin/env python3
"""
Replace startTimer function with Story 8.5 implementation and add helper functions
"""

def replace_start_timer():
    file_path = "/Volumes/My Passport/HA_Dashboard/custom_components/beatsy/www/js/ui-player.js"

    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Find startTimer function
    start_timer_idx = None
    for i, line in enumerate(lines):
        if 'function startTimer(startedAt, timerDuration)' in line:
            start_timer_idx = i
            break

    if start_timer_idx is None:
        print("✗ Could not find startTimer function")
        return False

    # Find the end of startTimer function (next function or export)
    end_timer_idx = None
    for i in range(start_timer_idx + 1, len(lines)):
        if lines[i].startswith('function ') or lines[i].startswith('/**'):
            end_timer_idx = i
            break

    if end_timer_idx is None:
        print("✗ Could not find end of startTimer function")
        return False

    print(f"Found startTimer at line {start_timer_idx + 1}, ends at line {end_timer_idx + 1}")

    # Prepare new timer functions
    new_timer_code = '''/**
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

'''

    # Replace lines from start_timer_idx to end_timer_idx with new code
    new_lines = lines[:start_timer_idx] + [new_timer_code] + lines[end_timer_idx:]

    with open(file_path, 'w') as f:
        f.writelines(new_lines)

    print(f"✓ Replaced startTimer and added updateTimer, onTimerExpire functions")
    print(f"✓ File updated successfully: {file_path}")
    return True

if __name__ == '__main__':
    replace_start_timer()
