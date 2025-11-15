/**
 * Beatsy Utility Functions
 * Story 9.3: XSS Prevention and Helper Functions
 */

/**
 * Escape HTML to prevent XSS attacks
 *
 * This function sanitizes user-generated content (e.g., player names) before
 * rendering in the DOM to prevent cross-site scripting (XSS) attacks.
 *
 * Implementation uses DOM API approach:
 * 1. Creates a temporary div element
 * 2. Sets textContent (safe - treats input as plain text)
 * 3. Reads innerHTML (returns escaped HTML entities)
 *
 * Example transformations:
 * - "<script>alert('XSS')</script>" → "&lt;script&gt;alert('XSS')&lt;/script&gt;"
 * - "<img src=x onerror='alert(1)'>" → "&lt;img src=x onerror='alert(1)'&gt;"
 * - "Markus" → "Markus" (unchanged)
 *
 * @param {string} text - User input text to escape
 * @returns {string} - HTML-escaped text safe for rendering
 *
 * @see Story 9.3 AC-9: XSS Prevention for Player Names
 * @see docs/tech-spec-epic-9.md NFR-S1: XSS Prevention
 */
export function escapeHtml(text) {
    if (text === null || text === undefined) {
        return '';
    }

    // Convert to string if not already
    const str = String(text);

    // Use DOM API to escape HTML entities
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

/**
 * Validate player name (client-side)
 *
 * Story 10.5: Client-side validation for UX (server-side is authoritative)
 *
 * Validation rules:
 * - Length: 1-20 characters (after trimming)
 * - Characters: Alphanumeric, spaces, hyphens, underscores only
 * - No HTML tags: Rejects < > &
 * - No script content: Rejects 'script' or 'javascript'
 *
 * @param {string} name - Player name to validate
 * @returns {object} - {valid: boolean, error: string|null}
 */
export function validatePlayerName(name) {
    if (!name || typeof name !== 'string') {
        return { valid: false, error: 'Player name is required' };
    }

    const trimmed = name.trim();

    // Check length
    if (trimmed.length === 0 || trimmed.length > 20) {
        return { valid: false, error: 'Player name must be between 1 and 20 characters' };
    }

    // Check for HTML tags
    if (trimmed.includes('<') || trimmed.includes('>') || trimmed.includes('&')) {
        return { valid: false, error: 'Player name contains invalid characters' };
    }

    // Check for script content
    const lower = trimmed.toLowerCase();
    if (lower.includes('script') || lower.includes('javascript')) {
        return { valid: false, error: 'Player name contains invalid content' };
    }

    // Check for allowed characters
    const allowedPattern = /^[a-zA-Z0-9 _-]+$/;
    if (!allowedPattern.test(trimmed)) {
        return { valid: false, error: 'Player name can only contain letters, numbers, spaces, hyphens, and underscores' };
    }

    return { valid: true, error: null };
}

/**
 * Validate year guess (client-side)
 *
 * Story 10.5: Client-side validation for UX (server-side is authoritative)
 *
 * @param {number|string} year - Year guess to validate
 * @param {number} minYear - Minimum allowed year
 * @param {number} maxYear - Maximum allowed year
 * @returns {object} - {valid: boolean, error: string|null}
 */
export function validateYearGuess(year, minYear, maxYear) {
    // Try to convert to number
    const yearNum = Number(year);

    // Check if valid number
    if (isNaN(yearNum) || !Number.isInteger(yearNum)) {
        return { valid: false, error: 'Year must be a valid integer' };
    }

    // Check range
    if (yearNum < minYear || yearNum > maxYear) {
        return { valid: false, error: `Year must be between ${minYear} and ${maxYear}` };
    }

    return { valid: true, error: null };
}

/**
 * Debounce function to limit how often a function can be called
 *
 * Story 10.6: Client-side debouncing for bet toggle (UX improvement)
 *
 * Creates a debounced version of a function that delays execution until
 * after the specified wait time has elapsed since the last call.
 *
 * Use case: Prevent accidental rapid clicks on bet toggle button
 *
 * @param {Function} func - Function to debounce
 * @param {number} wait - Milliseconds to wait before calling function
 * @returns {Function} - Debounced function
 *
 * @example
 * const debouncedClick = debounce(() => console.log('clicked'), 500);
 * button.addEventListener('click', debouncedClick);
 * // Multiple rapid clicks will only trigger console.log once after 500ms
 */
export function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function to limit how often a function can be called
 *
 * Story 10.6: Client-side throttling for rate-limited actions
 *
 * Creates a throttled version of a function that can only be called once
 * per specified time window. Subsequent calls within the window are ignored.
 *
 * Difference from debounce:
 * - Debounce: Waits for quiet period before executing
 * - Throttle: Executes immediately, then enforces cooldown
 *
 * @param {Function} func - Function to throttle
 * @param {number} limit - Milliseconds between allowed calls
 * @returns {Function} - Throttled function
 *
 * @example
 * const throttledClick = throttle(() => sendBet(), 500);
 * button.addEventListener('click', throttledClick);
 * // First click executes immediately, subsequent clicks ignored for 500ms
 */
export function throttle(func, limit) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => {
                inThrottle = false;
            }, limit);
        }
    };
}

/**
 * Export for testing and external use
 */
export default {
    escapeHtml,
    validatePlayerName,
    validateYearGuess,
    debounce,
    throttle
};
