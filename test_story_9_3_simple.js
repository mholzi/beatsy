#!/usr/bin/env node

/**
 * Story 9.3: Simple Verification Test
 *
 * This script verifies the implementation of Story 9.3:
 * - HTML structure exists
 * - JavaScript functions are properly defined
 * - All acceptance criteria are addressable
 */

const fs = require('fs');
const path = require('path');

console.log('=== Story 9.3: Round Results Board - Verification Test ===\n');

let allTestsPassed = true;

// Test 1: HTML Structure
console.log('Test 1: HTML Structure');
const html = fs.readFileSync(path.join(__dirname, 'custom_components/beatsy/www/start.html'), 'utf8');

const htmlTests = [
    { name: 'results-view container exists', check: () => html.includes('id="results-view"') },
    { name: 'round-results-section exists', check: () => html.includes('id="round-results-section"') },
    { name: 'round-results-list exists', check: () => html.includes('id="round-results-list"') },
    { name: 'round-results-list has overflow-y-auto', check: () => html.includes('overflow-y-auto') },
    { name: 'round-results-list has max-h-80', check: () => html.includes('max-h-80') },
    { name: 'round-results-list has space-y-2', check: () => html.includes('space-y-2') },
];

htmlTests.forEach(test => {
    const passed = test.check();
    console.log(`  ${passed ? '✓' : '✗'} ${test.name}`);
    if (!passed) allTestsPassed = false;
});

// Test 2: utils.js - escapeHtml function
console.log('\nTest 2: utils.js - escapeHtml function');
const utils = fs.readFileSync(path.join(__dirname, 'custom_components/beatsy/www/js/utils.js'), 'utf8');

const utilsTests = [
    { name: 'escapeHtml function exported', check: () => utils.includes('export function escapeHtml') },
    { name: 'Uses DOM API (createElement)', check: () => utils.includes('document.createElement') },
    { name: 'Sets textContent for safety', check: () => utils.includes('textContent') },
    { name: 'Returns innerHTML (escaped)', check: () => utils.includes('return div.innerHTML') },
];

utilsTests.forEach(test => {
    const passed = test.check();
    console.log(`  ${passed ? '✓' : '✗'} ${test.name}`);
    if (!passed) allTestsPassed = false;
});

// Test 3: ui-results.js - renderRoundResults function
console.log('\nTest 3: ui-results.js - renderRoundResults function');
const results = fs.readFileSync(path.join(__dirname, 'custom_components/beatsy/www/js/ui-results.js'), 'utf8');

const resultsTests = [
    { name: 'renderRoundResults function exported', check: () => results.includes('export function renderRoundResults') },
    { name: 'Imports escapeHtml from utils.js', check: () => results.includes("import { escapeHtml } from './utils.js'") },
    { name: 'Sorts by points_earned descending', check: () => results.includes('b.points_earned - a.points_earned') },
    { name: 'Secondary sort alphabetical', check: () => results.includes('localeCompare') },
    { name: 'Highlights current player (bg-yellow-100)', check: () => results.includes('bg-yellow-100') },
    { name: 'Bet indicator emoji (🔥)', check: () => results.includes('🔥') },
    { name: 'Points color coding (text-green-600)', check: () => results.includes('text-green-600') },
    { name: 'Plus prefix for positive points', check: () => results.includes("points_earned > 0 ? '+' : ''") },
    { name: 'Uses escapeHtml on player_name', check: () => results.includes('escapeHtml(r.player_name)') },
    { name: 'Batch update (innerHTML)', check: () => results.includes('listEl.innerHTML = html') },
];

resultsTests.forEach(test => {
    const passed = test.check();
    console.log(`  ${passed ? '✓' : '✗'} ${test.name}`);
    if (!passed) allTestsPassed = false;
});

// Test 4: ui-results.js - renderResultsView function
console.log('\nTest 4: ui-results.js - renderResultsView function');

const renderViewTests = [
    { name: 'renderResultsView function exported', check: () => results.includes('export function renderResultsView') },
    { name: 'Hides active-round-view', check: () => results.includes("getElementById('active-round-view')") },
    { name: 'Shows results-view', check: () => results.includes("getElementById('results-view')") },
    { name: 'Renders correct year', check: () => results.includes('renderCorrectYear') },
    { name: 'Calls renderRoundResults', check: () => results.includes('renderRoundResults(resultsData.results') },
    { name: 'Performance measurement', check: () => results.includes('performance.now()') },
    { name: 'Logs render time', check: () => results.includes('Results view rendered in') },
];

renderViewTests.forEach(test => {
    const passed = test.check();
    console.log(`  ${passed ? '✓' : '✗'} ${test.name}`);
    if (!passed) allTestsPassed = false;
});

// Test 5: ui-player.js - Integration
console.log('\nTest 5: ui-player.js - Integration');
const player = fs.readFileSync(path.join(__dirname, 'custom_components/beatsy/www/js/ui-player.js'), 'utf8');

const playerTests = [
    { name: 'Imports renderResultsView', check: () => player.includes("import { renderResultsView } from './ui-results.js'") },
    { name: 'Handles round_ended event', check: () => player.includes("data.event_type === 'round_ended'") },
    { name: 'Calls handleRoundEnded on round_ended', check: () => player.includes("handleRoundEnded(data.data)") },
    { name: 'handleRoundEnded function exists', check: () => player.includes('function handleRoundEnded(data)') },
    { name: 'Calls renderResultsView', check: () => player.includes('renderResultsView(resultsData)') },
];

playerTests.forEach(test => {
    const passed = test.check();
    console.log(`  ${passed ? '✓' : '✗'} ${test.name}`);
    if (!passed) allTestsPassed = false;
});

// Summary
console.log('\n=== Test Summary ===');
if (allTestsPassed) {
    console.log('✓ All verification tests passed!');
    console.log('\nStory 9.3 implementation is complete and ready for review.');
    console.log('\nNext steps:');
    console.log('1. Open test_story_9_3.html in a browser to manually test all acceptance criteria');
    console.log('2. Verify XSS prevention with malicious input');
    console.log('3. Test scrolling with 20+ players');
    console.log('4. Test on mobile devices (320px viewport)');
    process.exit(0);
} else {
    console.log('✗ Some verification tests failed.');
    console.log('Please review the implementation and fix any issues.');
    process.exit(1);
}
