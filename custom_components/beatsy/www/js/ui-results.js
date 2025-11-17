/**
 * Beatsy Results View UI
 * Story 9.1-9.3: Results View Rendering Functions
 *
 * This module handles rendering of the results view after round ends:
 * - Correct year display (Story 9.2)
 * - Round results board with all players' guesses (Story 9.3)
 * - Overall leaderboard (Story 9.4)
 * - Waiting state (Story 9.5)
 */

import { escapeHtml } from './utils.js';

/**
 * Story 9.3: Render round results board (all players' guesses)
 * Story 9.6: Responsive scrolling for long results
 *
 * Displays all players' guesses and points earned, sorted by points descending.
 * Implements sorting, highlighting, bet indicators, points color coding, and XSS prevention.
 * If more than ~8-10 players, list becomes scrollable (max-h-80 = 320px).
 * Ensures correct year and leaderboard remain accessible outside scroll container.
 *
 * @param {Array} results - Array of player result objects from round_ended event
 * @param {string} currentPlayer - Current player's name for highlighting
 *
 * Story 9.3:
 * AC-1: All players who submitted guesses are shown
 * AC-2: Results sorted by points_earned descending, then alphabetically
 * AC-3: Each entry shows player name, guess, points earned, bet indicator
 * AC-4: Current player row has yellow background
 * AC-5: Bet indicator (🔥 emoji) shown for bet_placed: true
 * AC-6: Positive points display with "+" prefix and green color
 * AC-7: Ties handled with stable alphabetical sort
 * AC-8: Scrolling enabled for 10+ players
 * AC-9: XSS prevention using escapeHtml()
 *
 * Story 9.6:
 * AC-6: Scroll position resets to top for each new round
 * AC-6: Smooth scrolling on mobile (60fps, iOS momentum, GPU acceleration)
 * AC-6: Keyboard accessible (tabindex="0" in HTML)
 * AC-6: Screen reader accessible (role="region" aria-label in HTML)
 *
 * @see Story 9.3 AC-1 through AC-9
 * @see Story 9.6 AC-6 (Responsive Scrolling)
 * @see docs/tech-spec-epic-9.md#APIs-and-Interfaces
 */
export function renderRoundResults(results, currentPlayer) {
    const listEl = document.getElementById('round-results-list');
    if (!listEl) {
        console.error('Round results list element not found');
        return;
    }

    // Handle empty results
    if (!results || results.length === 0) {
        listEl.innerHTML = '<p class="text-gray-500 text-center p-4">No results available</p>';
        return;
    }

    // AC-2, AC-7: Sort by points earned descending, then alphabetically for ties
    const sorted = [...results].sort((a, b) => {
        if (b.points_earned !== a.points_earned) {
            return b.points_earned - a.points_earned;  // Primary: points descending
        }
        return a.player_name.localeCompare(b.player_name);  // Secondary: alphabetical
    });

    // AC-11: Build full HTML string first (batch update for performance)
    const html = sorted.map(r => {
        // AC-4: Highlight current player with yellow background
        const isCurrentPlayer = r.player_name === currentPlayer;
        const bgClass = isCurrentPlayer ? 'bg-yellow-100' : 'bg-white';

        // AC-6: Points color coding
        let pointsClass = 'text-gray-400';  // Default for 0 points
        if (r.points_earned > 0) {
            pointsClass = 'text-green-600';  // Positive points: green
        } else if (r.points_earned < 0) {
            pointsClass = 'text-red-600';  // Negative points (bet loss): red
        }

        // AC-6: Add "+" prefix for positive points
        const pointsPrefix = r.points_earned > 0 ? '+' : '';

        // AC-5: Bet indicator (🔥 emoji) if bet was placed
        const betIndicator = r.bet_placed
            ? '<span class="text-xl ml-1">🔥</span>'
            : '';

        // AC-3, AC-9: Display all required info with XSS prevention
        return `
            <div class="result-row ${bgClass} p-3 border-b border-gray-200 flex justify-between items-center">
                <div class="flex items-center gap-2">
                    <span class="font-semibold">${escapeHtml(r.player_name)}</span>
                    ${betIndicator}
                    <span class="text-gray-600 text-sm">guessed ${r.guess}</span>
                </div>
                <div class="flex items-center gap-2">
                    <span class="font-bold ${pointsClass}">
                        ${pointsPrefix}${r.points_earned}
                    </span>
                </div>
            </div>
        `;
    }).join('');

    // AC-1: Insert HTML into DOM (single batch update)
    listEl.innerHTML = html;

    // Story 9.6: Reset scroll position to top for each new round
    listEl.scrollTop = 0;

    console.log(`✓ Round results rendered (${sorted.length} players)`);
}

/**
 * Story 9.2: Render correct year reveal
 * AC-4: Year extracted from round_ended event with validation
 * AC-5: Renders immediately within 100ms budget
 *
 * Displays the correct year in large, prominent text with proper validation.
 *
 * @param {number} correctYear - The correct year for the song (1900-2099)
 */
export function renderCorrectYear(correctYear) {
    const correctYearEl = document.getElementById('correct-year');
    if (!correctYearEl) {
        console.warn('Correct year element not found');
        return;
    }

    // AC-4: Validate year input
    let displayYear = correctYear;
    if (typeof correctYear !== 'number' || correctYear < 1900 || correctYear > 2099) {
        console.error('Invalid year:', correctYear);
        displayYear = 'Unknown';
    }

    // AC-5: Single DOM update (fastest method)
    correctYearEl.textContent = displayYear;

    // AC-3: Apply fade-in animation for reveal moment
    correctYearEl.classList.add('animate-fade-in');

    console.log(`✓ Correct year rendered: ${displayYear}`);
}

/**
 * Story 11.10: Display fun fact in results view
 *
 * Shows a fun fact about the song if available. Section is hidden by default
 * and only shown when a valid fun fact exists. Uses textContent for XSS prevention.
 *
 * @param {string} funFact - Fun fact text from song data
 *
 * AC-2: Extracts fun_fact from round_ended event payload
 * AC-2: Handles missing or undefined fun_fact gracefully
 * AC-2: XSS prevention using textContent assignment (auto-escapes HTML)
 * AC-3: Section visible when fun_fact exists and is non-empty string
 * AC-3: Section hidden when fun_fact is missing, null, undefined, or empty string
 *
 * @see Story 11.10 AC-2, AC-3
 */
export function displayFunFact(funFact) {
    const funFactSection = document.getElementById('fun-fact-section');
    const funFactText = document.getElementById('fun-fact-text');

    if (!funFactSection || !funFactText) {
        console.error('Fun fact elements not found');
        return;
    }

    // Check if fun fact exists and is non-empty
    if (funFact && funFact.trim() !== '') {
        // Escape HTML to prevent XSS - textContent auto-escapes
        funFactText.textContent = funFact;
        funFactSection.classList.remove('hidden');
        console.log('✓ Fun fact displayed:', funFact.substring(0, 50) + '...');
    } else {
        // Hide section if no fun fact
        funFactSection.classList.add('hidden');
        console.log('Fun fact not available, section hidden');
    }
}

/**
 * Story 9.4: Render overall leaderboard
 *
 * Displays top 5 players by total points with rank, name, and total points.
 * Highlights current player and shows them separately if not in top 5.
 *
 * @param {Array} leaderboard - Leaderboard array from server (sorted by total_points desc)
 * @param {string} currentPlayer - Current player's name
 *
 * AC-4: Top 5 players by total accumulated points shown
 * AC-4: Each entry displays: rank number, player name, total points
 * AC-4: Current player's entry highlighted (yellow background, bold text)
 * AC-4: If current player not in top 5, shown separately below
 * AC-4: Ties handled correctly with same rank and skip numbering
 * AC-4: Leaderboard updates immediately when round_ended event received
 *
 * @see Story 9.4 AC-4
 */
export function renderLeaderboard(leaderboard, currentPlayer) {
    console.log('Rendering leaderboard with', leaderboard.length, 'entries');

    // Validate input
    if (!leaderboard || !Array.isArray(leaderboard)) {
        console.error('Invalid leaderboard data:', leaderboard);
        return;
    }

    const listEl = document.getElementById('leaderboard-list');
    if (!listEl) {
        console.error('Leaderboard list element not found');
        return;
    }

    // Task 2: Determine if we need to show only top 5
    const showTop5Only = leaderboard.length > 5;
    const topFive = showTop5Only ? leaderboard.slice(0, 5) : leaderboard;

    // Task 3 & 4: Check if current player is in top 5
    const currentPlayerInTop5 = topFive.some(entry => entry.is_current_player);

    // Task 1: Generate HTML for top 5 (or all if fewer than 5)
    const html = topFive.map(entry => `
        <div class="leaderboard-row ${entry.is_current_player ? 'bg-yellow-100 font-bold' : ''} p-3 border-b flex justify-between">
            <div>
                <span class="text-gray-600">#${entry.rank}</span>
                <span class="ml-2">${escapeHtml(entry.player_name)}</span>
            </div>
            <span class="font-semibold">${entry.total_points} pts</span>
        </div>
    `).join('');

    // Set main leaderboard HTML
    listEl.innerHTML = html;

    // Task 4: If current player not in top 5, show separately
    if (!currentPlayerInTop5 && showTop5Only) {
        const currentPlayerEntry = leaderboard.find(e => e.is_current_player);
        if (currentPlayerEntry) {
            const separateHtml = `
                <div class="mt-4 p-3 bg-yellow-100 border-t-2 border-yellow-400 rounded">
                    <span class="text-gray-600">Your position:</span>
                    <span class="font-bold ml-2">#${currentPlayerEntry.rank} - ${escapeHtml(currentPlayerEntry.player_name)} - ${currentPlayerEntry.total_points} pts</span>
                </div>
            `;
            listEl.insertAdjacentHTML('beforeend', separateHtml);
        }
    }

    console.log(`✓ Leaderboard rendered: ${topFive.length} displayed, current player ${currentPlayerInTop5 ? 'in top 5' : 'shown separately'}`);
}

/**
 * Story 9.5: Display "Waiting for next song..." message.
 *
 * Shows the waiting state message after results are displayed.
 * Message remains visible until next round starts (round_started event).
 *
 * AC-5: Message displayed prominently after leaderboard
 * AC-5: Message visually distinct from results content
 *
 * @see Story 9.5 AC-5
 */
export function showWaitingState() {
    const waitingEl = document.getElementById('waiting-state');
    if (!waitingEl) {
        console.error('Waiting state element not found');
        return;
    }
    waitingEl.classList.remove('hidden');
    console.log('✓ Waiting state displayed');
}

/**
 * Story 9.1: Render results view (orchestration function)
 *
 * Coordinates rendering of all results view sections:
 * - Correct year reveal (Story 9.2)
 * - Round results board (Story 9.3)
 * - Overall leaderboard (Story 9.4)
 * - Waiting state (Story 9.5)
 *
 * @param {Object} resultsData - Full results payload from round_ended event
 *
 * AC-1: Transition from active round to results view in <500ms
 * AC-5: Performance target met for 10-20 players
 *
 * @see Story 9.1 AC-1, AC-5
 */
export function renderResultsView(resultsData) {
    console.log('🎯 Rendering results view:', resultsData);

    // AC-5: Performance measurement
    const renderStart = performance.now();

    // Hide active round view
    const activeRoundView = document.getElementById('active-round-view');
    if (activeRoundView) {
        activeRoundView.classList.add('hidden');
    }

    // Show results view
    const resultsView = document.getElementById('results-view');
    if (resultsView) {
        resultsView.classList.remove('hidden');
    }

    // Story 9.2: Render correct year
    if (resultsData.correct_year) {
        renderCorrectYear(resultsData.correct_year);
    }

    // Story 11.10: Display fun fact if available
    const funFact = resultsData.song?.fun_fact;
    displayFunFact(funFact);

    // Story 9.3: Render round results board
    if (resultsData.results && resultsData.results.length > 0) {
        // Get current player from localStorage
        const currentPlayer = localStorage.getItem('beatsy_player_name') || '';
        renderRoundResults(resultsData.results, currentPlayer);
    } else {
        console.warn('No results to display');
        const listEl = document.getElementById('round-results-list');
        if (listEl) {
            listEl.innerHTML = '<p class="text-gray-500 text-center p-4">No results available</p>';
        }
    }

    // Story 9.4: Render overall leaderboard
    if (resultsData.leaderboard && resultsData.leaderboard.length > 0) {
        const currentPlayer = localStorage.getItem('beatsy_player_name') || '';
        renderLeaderboard(resultsData.leaderboard, currentPlayer);
    } else {
        console.warn('No leaderboard data to display');
    }

    // Story 9.5: Show waiting state after all other sections
    showWaitingState();

    // AC-5: Log render time for debugging
    const renderEnd = performance.now();
    const renderTime = renderEnd - renderStart;
    console.log(`✓ Results view rendered in ${renderTime.toFixed(2)}ms`);

    if (renderTime > 500) {
        console.warn(`⚠️ Results render time exceeded 500ms target (${renderTime.toFixed(2)}ms)`);
    }
}

/**
 * Export all functions
 */
export default {
    renderRoundResults,
    renderCorrectYear,
    displayFunFact,
    renderLeaderboard,
    renderResultsView,
    showWaitingState
};
