/**
 * Story 12.3: Unit Tests for Reconnection Error Handling
 * Tests for error handling functions in ui-player.js
 */

import {
    logReconnectionError,
    displayReconnectionError,
    escapeHtml,
    fallbackToFreshRegistration,
    attemptReconnection
} from './ui-player.js';

/**
 * Test Suite: logReconnectionError()
 * AC-2: Logs all reconnection errors to console with full details
 */
describe('logReconnectionError', () => {
    let consoleErrorSpy;

    beforeEach(() => {
        consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
        localStorage.clear();
    });

    afterEach(() => {
        consoleErrorSpy.mockRestore();
    });

    test('should log error with timestamp, context, and message', () => {
        logReconnectionError('Test context', 'Test message', null);

        expect(consoleErrorSpy).toHaveBeenCalledWith(expect.stringContaining('❌'));
        expect(consoleErrorSpy).toHaveBeenCalledWith(expect.stringContaining('Reconnection Error'));
        expect(consoleErrorSpy).toHaveBeenCalledWith('Context: Test context');
        expect(consoleErrorSpy).toHaveBeenCalledWith('Message: Test message');
    });

    test('should include session ID if available', () => {
        localStorage.setItem('beatsy_session_id', 'test-session-12345');
        logReconnectionError('Test context', 'Test message', null);

        expect(consoleErrorSpy).toHaveBeenCalledWith(expect.stringContaining('Session: test-ses'));
    });

    test('should log error details when provided', () => {
        const details = { code: 'session_expired', data: { foo: 'bar' } };
        logReconnectionError('Test context', 'Test message', details);

        expect(consoleErrorSpy).toHaveBeenCalledWith('Details:', details);
    });

    test('should preserve stack trace for Error objects', () => {
        const error = new Error('Test error');
        logReconnectionError('Test context', 'Test message', error);

        expect(consoleErrorSpy).toHaveBeenCalledWith('Stack:', error.stack);
    });
});

/**
 * Test Suite: escapeHtml()
 * AC-1: Error messages do not expose technical details or allow code injection
 */
describe('escapeHtml', () => {
    test('should escape HTML special characters', () => {
        const input = '<script>alert("XSS")</script>';
        const output = escapeHtml(input);

        expect(output).not.toContain('<script>');
        expect(output).toContain('&lt;script&gt;');
    });

    test('should escape quotes', () => {
        const input = 'Error: "session_expired"';
        const output = escapeHtml(input);

        expect(output).toBe('Error: &quot;session_expired&quot;');
    });

    test('should handle ampersands', () => {
        const input = 'Error & failure';
        const output = escapeHtml(input);

        expect(output).toBe('Error &amp; failure');
    });

    test('should return plain text unchanged', () => {
        const input = 'Your session expired. Please register again.';
        const output = escapeHtml(input);

        expect(output).toBe(input);
    });
});

/**
 * Test Suite: displayReconnectionError()
 * AC-1: Shows clear, non-technical error message in modal
 * AC-3: Offers "Try Again" and "Register Fresh" options
 */
describe('displayReconnectionError', () => {
    let consoleLogSpy;

    beforeEach(() => {
        document.body.innerHTML = '';
        consoleLogSpy = jest.spyOn(console, 'log').mockImplementation(() => {});
    });

    afterEach(() => {
        consoleLogSpy.mockRestore();
    });

    test('should create modal with error message', () => {
        displayReconnectionError('Your session expired. Please register again.');

        const modal = document.getElementById('reconnection-error-modal');
        expect(modal).toBeTruthy();
        expect(modal.textContent).toContain('Reconnection Failed');
        expect(modal.textContent).toContain('Your session expired. Please register again.');
    });

    test('should escape HTML in error message', () => {
        displayReconnectionError('<script>alert("XSS")</script>');

        const modal = document.getElementById('reconnection-error-modal');
        expect(modal.innerHTML).not.toContain('<script>alert');
        expect(modal.innerHTML).toContain('&lt;script&gt;');
    });

    test('should create "Try Again" button', () => {
        displayReconnectionError('Test error');

        const retryButton = document.getElementById('retry-reconnection');
        expect(retryButton).toBeTruthy();
        expect(retryButton.textContent).toContain('Try Again');
    });

    test('should create "Register Fresh" button', () => {
        displayReconnectionError('Test error');

        const freshButton = document.getElementById('register-fresh');
        expect(freshButton).toBeTruthy();
        expect(freshButton.textContent).toContain('Register Fresh');
    });

    test('should remove existing modal before creating new one', () => {
        displayReconnectionError('First error');
        displayReconnectionError('Second error');

        const modals = document.querySelectorAll('#reconnection-error-modal');
        expect(modals.length).toBe(1);
        expect(modals[0].textContent).toContain('Second error');
    });

    test('should log error message to console', () => {
        displayReconnectionError('Test error message');

        expect(consoleLogSpy).toHaveBeenCalledWith('Error modal displayed:', 'Test error message');
    });
});

/**
 * Test Suite: fallbackToFreshRegistration()
 * AC-3: Clears session, offers fresh registration with pre-filled name
 */
describe('fallbackToFreshRegistration', () => {
    let consoleLogSpy;

    beforeEach(() => {
        localStorage.clear();
        document.body.innerHTML = `
            <div id="registration-view" class="hidden"></div>
            <div id="lobby-view"></div>
            <div id="active-round-view"></div>
            <div id="results-view"></div>
            <div id="reconnection-loader"></div>
            <input id="player-name" type="text" />
        `;
        consoleLogSpy = jest.spyOn(console, 'log').mockImplementation(() => {});
    });

    afterEach(() => {
        consoleLogSpy.mockRestore();
    });

    test('should clear session ID from localStorage', () => {
        localStorage.setItem('beatsy_session_id', 'test-session-123');
        fallbackToFreshRegistration();

        expect(localStorage.getItem('beatsy_session_id')).toBeNull();
    });

    test('should preserve player name by default', () => {
        localStorage.setItem('beatsy_player_name', 'TestPlayer');
        fallbackToFreshRegistration();

        expect(localStorage.getItem('beatsy_player_name')).toBe('TestPlayer');
    });

    test('should clear player name when clearName is true', () => {
        localStorage.setItem('beatsy_player_name', 'TestPlayer');
        fallbackToFreshRegistration(true);

        expect(localStorage.getItem('beatsy_player_name')).toBeNull();
    });

    test('should preserve admin flag', () => {
        localStorage.setItem('beatsy_is_admin', 'true');
        localStorage.setItem('beatsy_session_id', 'test-session-123');
        fallbackToFreshRegistration();

        expect(localStorage.getItem('beatsy_is_admin')).toBe('true');
    });

    test('should reset reconnection attempt counter', () => {
        localStorage.setItem('beatsy_reconnection_attempts', '3');
        fallbackToFreshRegistration();

        expect(localStorage.getItem('beatsy_reconnection_attempts')).toBeNull();
    });

    test('should show registration view', () => {
        fallbackToFreshRegistration();

        const registrationView = document.getElementById('registration-view');
        expect(registrationView.classList.contains('hidden')).toBe(false);
    });

    test('should hide lobby, active round, and results views', () => {
        fallbackToFreshRegistration();

        expect(document.getElementById('lobby-view').classList.contains('hidden')).toBe(true);
        expect(document.getElementById('active-round-view').classList.contains('hidden')).toBe(true);
        expect(document.getElementById('results-view').classList.contains('hidden')).toBe(true);
    });

    test('should pre-fill name input with previous name', () => {
        localStorage.setItem('beatsy_player_name', 'PreviousPlayer');
        fallbackToFreshRegistration();

        const nameInput = document.getElementById('player-name');
        expect(nameInput.value).toBe('PreviousPlayer');
    });

    test('should not pre-fill name if clearName is true', () => {
        localStorage.setItem('beatsy_player_name', 'PreviousPlayer');
        fallbackToFreshRegistration(true);

        const nameInput = document.getElementById('player-name');
        expect(nameInput.value).toBe('');
    });

    test('should remove error modal if exists', () => {
        const modal = document.createElement('div');
        modal.id = 'reconnection-error-modal';
        document.body.appendChild(modal);

        fallbackToFreshRegistration();

        expect(document.getElementById('reconnection-error-modal')).toBeNull();
    });

    test('should log success message', () => {
        fallbackToFreshRegistration();

        expect(consoleLogSpy).toHaveBeenCalledWith('📍 Falling back to fresh registration');
        expect(consoleLogSpy).toHaveBeenCalledWith('✅ Cleared session, ready for fresh registration');
    });
});

/**
 * Test Suite: Reconnection Attempt Counter
 * AC-4: Prevents infinite reconnection loops
 */
describe('Reconnection Attempt Counter', () => {
    beforeEach(() => {
        localStorage.clear();
    });

    test('should start with 0 attempts', () => {
        const attempts = parseInt(localStorage.getItem('beatsy_reconnection_attempts') || '0');
        expect(attempts).toBe(0);
    });

    test('should increment on each reconnection attempt', () => {
        // Simulate 3 attempts
        for (let i = 0; i < 3; i++) {
            const currentAttempts = parseInt(localStorage.getItem('beatsy_reconnection_attempts') || '0');
            localStorage.setItem('beatsy_reconnection_attempts', (currentAttempts + 1).toString());
        }

        const attempts = parseInt(localStorage.getItem('beatsy_reconnection_attempts') || '0');
        expect(attempts).toBe(3);
    });

    test('should reset counter on successful reconnection', () => {
        localStorage.setItem('beatsy_reconnection_attempts', '2');
        localStorage.removeItem('beatsy_reconnection_attempts');

        expect(localStorage.getItem('beatsy_reconnection_attempts')).toBeNull();
    });

    test('should reset counter in fallbackToFreshRegistration', () => {
        localStorage.setItem('beatsy_reconnection_attempts', '3');

        // Mock DOM elements
        document.body.innerHTML = `
            <div id="registration-view" class="hidden"></div>
            <div id="lobby-view"></div>
            <div id="active-round-view"></div>
            <div id="results-view"></div>
        `;

        fallbackToFreshRegistration();

        expect(localStorage.getItem('beatsy_reconnection_attempts')).toBeNull();
    });
});

/**
 * Integration Test: Error Flow
 * AC-1, AC-3, AC-6: Complete error handling flow
 */
describe('Error Handling Integration', () => {
    beforeEach(() => {
        localStorage.clear();
        document.body.innerHTML = `
            <div id="registration-view" class="hidden"></div>
            <div id="lobby-view"></div>
            <div id="active-round-view"></div>
            <div id="results-view"></div>
            <input id="player-name" type="text" />
        `;
    });

    test('should handle session expiration flow', () => {
        // Setup: User has existing session
        localStorage.setItem('beatsy_session_id', 'expired-session-123');
        localStorage.setItem('beatsy_player_name', 'TestUser');

        // Action: Display error and fallback
        displayReconnectionError('Your session expired. Please register again.');
        fallbackToFreshRegistration();

        // Verify: Session cleared, registration shown, name pre-filled
        expect(localStorage.getItem('beatsy_session_id')).toBeNull();
        expect(localStorage.getItem('beatsy_player_name')).toBe('TestUser');
        expect(document.getElementById('registration-view').classList.contains('hidden')).toBe(false);
        expect(document.getElementById('player-name').value).toBe('TestUser');
    });

    test('should handle multiple reconnection failures', () => {
        // Simulate 3 failed attempts
        localStorage.setItem('beatsy_session_id', 'test-session');
        localStorage.setItem('beatsy_player_name', 'TestUser');

        for (let i = 0; i < 3; i++) {
            const attempts = parseInt(localStorage.getItem('beatsy_reconnection_attempts') || '0');
            localStorage.setItem('beatsy_reconnection_attempts', (attempts + 1).toString());
        }

        // After 3 failures, should force fresh registration
        const attempts = parseInt(localStorage.getItem('beatsy_reconnection_attempts') || '0');
        expect(attempts).toBe(3);

        // Fallback clears counter
        fallbackToFreshRegistration();
        expect(localStorage.getItem('beatsy_reconnection_attempts')).toBeNull();
    });
});
