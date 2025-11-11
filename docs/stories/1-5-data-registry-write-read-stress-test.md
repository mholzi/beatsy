# Story 1.5: Data Registry Write/Read Stress Test

Status: done

## Story

As a **Beatsy developer**,
I want **to validate that HA's data registry can handle rapid game state updates**,
So that **I avoid performance issues during live gameplay**.

## Acceptance Criteria

**AC-1: Data Registry Write/Read Operations (2025 Pattern)**
- **Given** Beatsy component has access to in-memory state storage (via `entry.runtime_data` or `hass.data[DOMAIN]`)
- **When** the test writes game state 100 times in 30 seconds (simulating 10 players, 3 rounds)
- **Then** all writes complete without errors
- **And** subsequent reads return accurate data
- **And** no data corruption occurs during rapid updates
- **And** HA logs confirm: "Beatsy: State test completed - {operations} ops in {duration}s"
- **And** test validates both legacy `hass.data` and modern `entry.runtime_data` patterns

**AC-2: Performance Metrics**
- **Given** stress test runs for 100 write+read cycles
- **When** performance metrics are calculated
- **Then** average write latency is < 300ms per operation
- **And** maximum latency for any single operation is < 500ms
- **And** total test duration is < 30 seconds
- **And** performance metrics are logged for POC Decision Document

**AC-3: Home Assistant Responsiveness**
- **Given** stress test is running
- **When** monitoring HA system state
- **Then** Home Assistant remains responsive (no UI lag)
- **And** HA logs show no performance warnings
- **And** HA resource usage stays acceptable (< 50% CPU spike)
- **And** other HA integrations continue functioning normally

**AC-4: Data Integrity Validation**
- **Given** 100 write+read cycles have completed
- **When** validating data integrity
- **Then** all reads return exactly what was written (no data loss)
- **And** player score increments are sequential and correct
- **And** no race conditions or data corruption detected
- **And** data structure remains valid after all operations

**AC-5: Test Documentation**
- **Given** all stress tests complete
- **When** developer reviews test results
- **Then** test script outputs performance metrics to JSON file
- **And** metrics include: total operations, duration, avg latency, max latency, errors, storage_pattern_used
- **And** results confirm in-memory storage (both patterns) is suitable for active gameplay
- **And** documentation includes confirmation of storage strategy (in-memory for game, persistent for config only)
- **And** test compares performance between `hass.data` and `entry.runtime_data` patterns

## Tasks / Subtasks

- [x] Task 1: Create Typed Game State Data Structure (AC: #1, #4) **[2025 PATTERN]**
  - [x] Create `GameStateData` dataclass in `state_test.py` (HA 2025 best practice)
  - [x] Define typed structure with dataclass fields: players, current_round, played_songs
  - [x] Include 10 simulated players with names and scores (list of Player dataclass)
  - [x] Include current round data with song URI and guesses (Round dataclass)
  - [x] Include played songs list (3-5 songs, list of strings)
  - [x] Add type hints throughout: `players: list[Player]`, `played_songs: list[str]`, etc.

- [x] Task 2: Create State Test Module with Dual Pattern Support (AC: #1, #2, #4) **[2025 PATTERN]**
  - [x] Create `custom_components/beatsy/state_test.py` module
  - [x] Import: `homeassistant.core`, `homeassistant.config_entries`, `logging`, `time`, `dataclasses`
  - [x] Implement `async def run_state_stress_test(hass, use_runtime_data: bool = False) -> PerformanceMetrics`
  - [x] If `use_runtime_data=True`: Use mock config entry with `entry.runtime_data = GameStateData(...)`
  - [x] If `use_runtime_data=False`: Use legacy `hass.data[DOMAIN]["game_state"]` pattern
  - [x] Loop 100 iterations for EACH pattern:
    - Write: Update player score (either in entry.runtime_data or hass.data)
    - Read: Retrieve and validate updated score
    - Measure: Record latency for write+read cycle
  - [x] Calculate metrics for each pattern: total ops, duration, avg latency, max latency, errors
  - [x] Return `PerformanceMetrics` dataclass with results and pattern comparison

- [x] Task 3: Add Performance Metrics Tracking (AC: #2, #5) **[2025 PATTERN]**
  - [x] Define `PerformanceMetrics` dataclass in `state_test.py`
  - [x] Include fields: test_type, storage_pattern, total_operations, duration_seconds, success_count, failure_count, avg_latency_ms, max_latency_ms, errors
  - [x] Add `storage_pattern` field: "hass.data" or "entry.runtime_data"
  - [x] Track timestamp for each write+read operation
  - [x] Calculate latency: `end_time - start_time` in milliseconds
  - [x] Store all latencies in list for avg/max calculation
  - [x] Count successes and failures
  - [x] Add comparison metrics: performance difference between patterns

- [x] Task 4: Create Test Script for Manual Execution (AC: #1-5) **[2025 PATTERN]**
  - [x] Create `tests/poc_state_test.py` test script
  - [x] Accept CLI arguments: `--output` (optional JSON file path), `--pattern` (hass_data, runtime_data, or both)
  - [x] Connect to HA instance (use HA test environment)
  - [x] Run test with both patterns: Call `run_state_stress_test(hass, use_runtime_data=False)` then `run_state_stress_test(hass, use_runtime_data=True)`
  - [x] Print results to console: operations/sec, avg latency, max latency, pattern comparison
  - [x] Output metrics to JSON file if `--output` specified
  - [x] Format: `{test_type, storage_pattern, total_operations, duration_seconds, avg_latency_ms, max_latency_ms, errors, timestamp, pattern_comparison}`

- [x] Task 5: Implement Data Integrity Validation (AC: #4)
  - [x] After each write, immediately read back the value
  - [x] Compare written value with read value
  - [x] Track any mismatches as errors
  - [x] Validate player score increments are sequential (e.g., 10 → 15 → 20)
  - [x] Validate data structure remains valid (no missing keys, correct types)
  - [x] Log any corruption detected with details

- [x] Task 6: Update Component Init to Support Test Mode (AC: #1)
  - [x] Update `custom_components/beatsy/__init__.py`
  - [x] Import: `from .state_test import run_state_stress_test`
  - [x] Add test invocation method (if needed for POC)
  - [x] Ensure `hass.data[DOMAIN]` is initialized before test runs
  - [x] Log: "Beatsy: State test module loaded"

- [ ] Task 7: Monitor HA System Responsiveness (AC: #3)
  - [ ] During test execution, monitor HA system state
  - [ ] Check HA logs for performance warnings or errors
  - [ ] Verify HA web UI remains responsive (manual check)
  - [ ] Note resource usage: CPU, memory (if monitoring tools available)
  - [ ] Document any observed HA lag or slowdowns
  - [ ] Confirm other HA integrations continue working

- [x] Task 8: Document Storage Strategy (AC: #5) **[2025 PATTERN UPDATE]**
  - [x] Document both in-memory patterns: `hass.data` (legacy) and `entry.runtime_data` (2025 best practice)
  - [x] Confirm in-memory storage is appropriate for active game state (both patterns)
  - [x] Document: Fast, no persistence needed for active gameplay
  - [x] Note: Game state resets on HA restart (acceptable for games)
  - [x] Note: Use HA's persistent storage (`hass.helpers.storage`) ONLY for game config
  - [x] Document `entry.runtime_data` advantages: type safety, automatic cleanup, cleaner code
  - [x] Recommend `entry.runtime_data` for Epic 2+ production implementation
  - [x] Add documentation comment in `state_test.py` with references to HA 2025 blog post
  - [x] Reference this decision in POC Decision Document (Story 1.7)

- [ ] Task 9: Run Test and Collect Metrics (AC: #1-5) **[MANUAL TESTING REQUIRED - 2025 PATTERN]**
  - [ ] **[USER ACTION]** Deploy updated component to Home Assistant test instance
  - [ ] **[USER ACTION]** Run test script: `python tests/poc_state_test.py --output tests/poc_metrics.json --pattern both`
  - [ ] **[USER ACTION]** Verify both pattern tests complete successfully (100 ops each in < 30s)
  - [ ] **[USER ACTION]** Review metrics for both patterns: avg latency < 300ms, max latency < 500ms
  - [ ] **[USER ACTION]** Compare performance: hass.data vs entry.runtime_data
  - [ ] **[USER ACTION]** Check HA logs for errors or performance warnings
  - [ ] **[USER ACTION]** Verify HA UI remained responsive during test
  - [ ] **[USER ACTION]** Save metrics JSON with pattern comparison for Story 1.7 POC Decision Document

- [ ] Task 10: Validate Results Against Targets (AC: #2, #5) **[2025 PATTERN]**
  - [ ] Review collected metrics from test execution (both patterns)
  - [ ] Verify for BOTH patterns: Total duration < 30 seconds (PASS/FAIL)
  - [ ] Verify for BOTH patterns: Avg latency < 300ms (PASS/FAIL)
  - [ ] Verify for BOTH patterns: Max latency < 500ms (PASS/FAIL)
  - [ ] Verify for BOTH patterns: 100% success rate (no data corruption)
  - [ ] Verify: HA responsiveness maintained (no UI lag)
  - [ ] Compare patterns: Document which performs better (if any difference)
  - [ ] Document final verdict: PASS or FAIL with details for each pattern
  - [ ] Recommend pattern for production: entry.runtime_data (2025 best practice)
  - [ ] If FAIL: Document observed issues and pivot strategy

## Dev Notes

### Architecture Patterns and Constraints

**From Tech Spec (Epic 1 - Story 1.5) - UPDATED FOR HA 2025:**
- **Purpose:** Validate HA's in-memory storage can handle rapid game state updates
- **Test Pattern:** 100 write+read cycles simulating 10 players over 3 rounds (BOTH storage patterns)
- **Storage Strategy (2025 Update):** Test both `hass.data[DOMAIN]` (legacy) AND `entry.runtime_data` (2025 best practice)
- **Performance Target:** All writes complete in < 30 seconds, no data corruption (for BOTH patterns)
- **Why This Matters:** During live gameplay, we'll update player scores, guesses, and round state rapidly
- **2025 Pattern Advantage:** `entry.runtime_data` provides type safety, automatic cleanup, better code organization

**State Management Approach (from Architecture ADR-002) - 2025 UPDATE:**
- **In-Memory Options:** `hass.data[DOMAIN]` (legacy) OR `entry.runtime_data` (2025 best practice)
- **Persistent Storage:** `hass.helpers.storage` ONLY for game config (admin settings)
- **Rationale:** Games are ephemeral - no need to persist active game state across HA restarts
- **Epic 2 Dependency:** This story validates in-memory performance; Epic 2 implements full state management
- **Recommendation:** Use `entry.runtime_data` for production (Epic 2+) - better type safety and automatic cleanup
- **Reference:** https://developers.home-assistant.io/blog/2024/04/30/store-runtime-data-inside-config-entry/

**Realistic Game State Structure (for Testing) - 2025 TYPED PATTERN:**
```python
# New 2025 pattern: Typed dataclasses for entry.runtime_data
from dataclasses import dataclass

@dataclass
class Player:
    name: str
    score: int

@dataclass
class Guess:
    player: str
    year: int
    bet: bool

@dataclass
class Round:
    song_uri: str
    started_at: int
    timer_duration: int
    guesses: list[Guess]

@dataclass
class GameStateData:
    players: list[Player]
    current_round: Round
    played_songs: list[str]

# Example instance:
game_state = GameStateData(
    players=[
        Player("Player1", 10),
        Player("Player2", 15),
        Player("Player3", 8),
        # ... 10 total players
    ],
    current_round=Round(
        song_uri="spotify:track:xxxxx",
        started_at=1704805200,
        timer_duration=30,
        guesses=[
            Guess("Player1", 1985, True),
            Guess("Player2", 1987, False)
        ]
    ),
    played_songs=["spotify:track:xxxxx", "spotify:track:yyyyy"]
)

# For entry.runtime_data pattern:
# entry.runtime_data = game_state

# For legacy hass.data pattern (also tested):
# hass.data[DOMAIN]["game_state"] = asdict(game_state)
```

**Test Simulation Logic:**
- Simulate 10 players, 3 rounds (10 score updates per round = 30 updates)
- Run 100 write+read cycles to stress test
- Each cycle: Increment a random player's score, then read it back
- Measure latency for each cycle (write + read time)
- Validate no data corruption (read matches what was written)

**Performance Targets (from Tech Spec NFR-P1, NFR-P4):**
- **Avg Write Latency:** < 300ms per operation (fast enough for gameplay)
- **Max Latency:** < 500ms (even worst case should be acceptable)
- **Total Duration:** < 30 seconds for 100 ops (proves scalability)
- **Acceptable Degradation:** Up to 20% slower than targets acceptable for POC

**Why NOT Use Persistent Storage for Game State:**
- `hass.helpers.storage` is designed for persistent data (survives restarts)
- Persistent storage involves disk I/O (slower than in-memory)
- Game state is ephemeral - players expect games to reset on HA restart
- Performance requirement: Rapid updates during gameplay (real-time social features)
- Decision: Use persistent storage ONLY for game config (admin settings persist)

**From PRD NFR-R2 (Data Integrity):**
- **Zero Tolerance for Score Corruption:** Any data loss or corruption = FAIL
- **Validation Approach:** Read-after-write verification on every cycle
- **Error Detection:** Compare written value with read value, log any mismatches

### Learnings from Previous Story

**From Story 1.4 (Status: review)**

**Component Foundation Confirmed Stable:**
- Component loads successfully in HA without errors (Story 1.1 validated)
- `hass.data[DOMAIN]` initialized and accessible
- Component lifecycle working correctly (async setup/unload)
- All foundational modules stable for building upon

**2025 Standards Applied & Validated:**
- Modern Python 3.11+ type hints used throughout (`dict[str, Any]`)
- Async/await patterns established and working
- Module-level `_LOGGER = logging.getLogger(__name__)` logging
- Error handling with comprehensive try/except blocks
- Type hints for all function signatures

**Pattern to Reuse from Previous Stories:**
- State access pattern from `__init__.py` (accessing `hass.data[DOMAIN]`)
- Logging approach: INFO for operations, DEBUG for details, ERROR for failures
- Test script pattern from Story 1.4 (CLI args, JSON metrics output)
- Type hints and dataclasses for structured data
- Performance measurement: Use `time.perf_counter()` for high-precision timing

**No Blocking Technical Debt:**
- All foundational components stable from Story 1.1-1.3
- Component initialization working correctly
- `hass.data[DOMAIN]` accessible and ready for use
- No errors or warnings in HA logs from previous stories

**Key Architectural Validation from Story 1.4:**
- Async operations working smoothly with HA
- Service calls and state access patterns established
- Error handling patterns proven effective
- Test script approach validated (manual execution, metrics output)

[Source: stories/1-4-spotify-api-basic-integration-test.md#Dev-Agent-Record]

### Home Assistant 2025 Pattern Update

**CRITICAL UPDATE (Researched 2025-11-10):**

Home Assistant introduced `entry.runtime_data` in April 2024 as the recommended replacement for storing integration runtime data in `hass.data`. This story has been updated to test BOTH patterns and validate the migration path.

**Key Changes from HA 2024 Developer Blog:**
- **Old Pattern:** `hass.data[DOMAIN][entry_id] = coordinator`
- **New Pattern:** `entry.runtime_data = coordinator` (with typed ConfigEntry)
- **Benefits:** Type safety, automatic cleanup, cleaner code organization

**Implementation for This Story:**
1. Test both patterns: `hass.data` (legacy) AND `entry.runtime_data` (2025)
2. Compare performance between both approaches
3. Validate that both patterns meet performance targets
4. Recommend `entry.runtime_data` for Epic 2+ production code

**Type Safety Pattern:**
```python
from homeassistant.config_entries import ConfigEntry
from dataclasses import dataclass

@dataclass
class GameStateData:
    players: list[Player]
    current_round: Round
    played_songs: list[str]

# Create type alias for typed ConfigEntry
type BeatsyConfigEntry = ConfigEntry[GameStateData]

# In async_setup_entry:
async def async_setup_entry(hass: HomeAssistant, entry: BeatsyConfigEntry) -> bool:
    entry.runtime_data = GameStateData(...)
    return True

# Access in platforms with type safety:
def __init__(self, entry: BeatsyConfigEntry):
    self.game_state = entry.runtime_data  # Fully typed!
```

**Migration Path:**
- POC (Story 1.5): Test both patterns, validate performance
- Epic 2 Production: Use `entry.runtime_data` exclusively
- Benefits: Better IDE support, type checking, automatic cleanup on unload

**Reference:**
- Blog Post: https://developers.home-assistant.io/blog/2024/04/30/store-runtime-data-inside-config-entry/
- HA Core 2024.6+: Multiple integrations migrated to this pattern
- Best Practice: All new integrations should use `entry.runtime_data`

**Impact on This Story:**
- Added Task 1 subtask: Create typed `GameStateData` dataclass
- Updated Task 2: Test both storage patterns
- Updated Task 3: Add `storage_pattern` field to metrics
- Updated Task 4: CLI arg `--pattern` to test hass_data, runtime_data, or both
- Updated Task 8: Document both patterns and recommend runtime_data
- Updated Task 10: Validate and compare performance of both patterns

### Project Structure Notes

**Expected File Paths:**
```
/config/custom_components/beatsy/
├── __init__.py              # EXISTS (from Story 1.1) - MODIFY: Import state test
├── manifest.json            # EXISTS (from Story 1.1)
├── const.py                # EXISTS (from Story 1.1)
├── state_test.py           # NEW FILE: State stress test module
├── spotify_helper.py       # EXISTS (from Story 1.4)
└── websocket_handler.py    # EXISTS (from Story 1.3)

/tests/
├── poc_spotify_test.py     # EXISTS (from Story 1.4)
└── poc_state_test.py       # NEW FILE: Test script for POC validation
```

**New File: state_test.py**
- Purpose: State stress test implementation for POC validation
- Responsibilities:
  - Initialize test game state structure
  - Perform 100 write+read cycles on `hass.data[DOMAIN]`
  - Measure latency for each operation
  - Validate data integrity (read matches write)
  - Calculate performance metrics
  - Return `PerformanceMetrics` dataclass with results
- Pattern: Pure async functions, minimal state storage
- No external dependencies (uses only HA core and Python stdlib)

**New File: tests/poc_state_test.py**
- Standalone Python script (not pytest test)
- CLI arguments for optional metrics output path
- Manual execution for POC validation
- Connects to HA test instance and runs stress test
- Outputs metrics JSON for Story 1.7 POC Decision Document

**Modified File: __init__.py**
- Add import: `from .state_test import run_state_stress_test`
- Optional: Add test trigger method for POC validation
- No impact on normal component operation (test mode is separate)
- Ensure `hass.data[DOMAIN]` initialized before test can run

**File Alignment with Architecture:**
- `state_test.py` → Validates ADR-002 (Hybrid State Storage - Memory + Registry)
- Test pattern → Proves in-memory performance is sufficient
- Metrics collection → Feeds into POC Decision Document (Story 1.7)
- Storage strategy → Confirms `hass.data` for game, `storage` for config

**No Conflicts:**
- State test is isolated module, doesn't interfere with other components
- Test mode is manual/on-demand, not part of normal operation
- Uses same `hass.data[DOMAIN]` structure that Epic 2 will implement

### Testing Standards Summary

**Test Approach (POC Validation - Manual):**
- Automated stress test with manual execution
- No mocking - real HA instance and real data operations
- Verification via:
  1. Performance metrics (ops/sec, latency)
  2. HA logs (errors, warnings)
  3. Manual observation (HA UI responsiveness)
  4. Data integrity validation (read-after-write)

**Success Criteria:**
- 100 write+read cycles complete successfully
- Total duration < 30 seconds (faster is better)
- Avg latency < 300ms (acceptable performance)
- Max latency < 500ms (worst case still acceptable)
- No data corruption (100% accuracy)
- HA remains responsive (no UI lag or crashes)

**Edge Cases to Test:**
- Rapid sequential updates (no delays between ops)
- Different data structure sizes (small vs large player lists)
- Concurrent access patterns (if applicable)
- HA resource constraints (low-end hardware vs high-end)

**Manual Test Steps:**
1. Deploy updated Beatsy component to HA test instance
2. Ensure HA is in stable state (no other heavy operations running)
3. Run test script: `python tests/poc_state_test.py --output tests/poc_metrics.json`
4. Observe:
   - Console output (real-time progress and results)
   - HA logs (check for errors or warnings)
   - HA web UI (verify responsiveness during test)
5. Review metrics JSON: Verify all targets met
6. Document results in POC Decision Document (Story 1.7)

**Performance Validation:**
- Measure: Time for each write+read cycle
- Calculate: Total duration, avg latency, max latency
- Target: 100 ops in < 30 seconds = avg 300ms per op (meets target)
- Acceptable: Up to 36 seconds (360ms avg) = 20% slower than target (POC tolerance)

**Metrics to Collect:**
```json
{
  "test_type": "state_writes",
  "status": "PASS",
  "total_operations": 100,
  "duration_seconds": 22.4,
  "avg_latency_ms": 224,
  "max_latency_ms": 310,
  "success_count": 100,
  "failure_count": 0,
  "errors": []
}
```

**POC Decision Criteria:**
- **PASS:** All metrics meet targets, no errors, HA responsive
- **FAIL (Performance):** Latency exceeds targets significantly (> 500ms avg)
- **FAIL (Integrity):** Any data corruption detected
- **FAIL (Stability):** HA becomes unresponsive or crashes

**If Test Fails:**
- Document observed issues in metrics JSON
- Propose pivot strategy:
  - Alternative A: Reduce update frequency in game logic
  - Alternative B: Use more optimized data structures
  - Alternative C: Implement debouncing/batching for state updates
  - Alternative D: Re-evaluate if HA is suitable platform for this use case

### References

**Source Documents:**
- [Source: docs/tech-spec-epic-1.md#Story-1.5-Data-Registry-Write-Read-Stress-Test]
- [Source: docs/epics.md#Story-1.5-Data-Registry-Write-Read-Stress-Test]
- [Source: docs/architecture.md#ADR-002 - Hybrid State Storage (Memory + Registry)]

**Key Technical Decisions:**
- Use in-memory `hass.data[DOMAIN]` for active game state (fast, ephemeral)
- Use persistent storage (`hass.helpers.storage`) ONLY for game config
- 100 write+read cycles simulate realistic gameplay load
- Performance targets: < 300ms avg latency, < 30 seconds total
- Data integrity: 100% accuracy required (zero tolerance for corruption)

**Dependencies:**
- Story 1.1: Component structure and registration (COMPLETE)
- Home Assistant Core: Access to `hass.data` registry

**Home Assistant API References:**
- `hass.data[DOMAIN]` - In-memory data registry for custom integrations
- `hass.helpers.storage` - Persistent storage API (NOT used in this story, but referenced for comparison)
- Python `time.perf_counter()` - High-precision timing for latency measurement

**Performance Testing Concepts:**
- **Write Latency:** Time to update data in `hass.data[DOMAIN]`
- **Read Latency:** Time to retrieve data from `hass.data[DOMAIN]`
- **Data Integrity:** Verification that read data matches written data
- **Stress Test:** Rapid repeated operations to find performance limits
- **Baseline Performance:** Establish expected performance for future comparison

**POC Philosophy:**
- Prove in-memory storage is fast enough for gameplay
- Document exact performance characteristics for Epic 2 design
- Validate architectural assumption (ADR-002) before building upon it
- Provide data for POC Decision Document (Story 1.7)

## Change Log

**Story Created:** 2025-11-10
**Author:** Bob (Scrum Master)
**Epic:** Epic 1 - Foundation & Multi-Risk POC
**Story ID:** 1.5
**Status:** drafted (was backlog)

**Requirements Source:**
- Tech Spec Epic 1: Validate data registry can handle rapid game state updates
- Epics: Confirm in-memory state performance sufficient for gameplay
- Architecture ADR-002: Hybrid State Storage - validates in-memory approach

**Technical Approach:**
- Create state stress test module with 100 write+read cycles
- Measure performance: duration, avg latency, max latency
- Validate data integrity with read-after-write verification
- Test with realistic game state structure (10 players, 3 rounds)
- Output metrics to JSON for POC Decision Document
- Manual execution on real HA instance (no mocking)

**Dependencies:**
- Story 1.1 complete: Component loads, `hass.data[DOMAIN]` initialized
- No blocking issues from previous stories
- Can run in parallel with Story 1.4 (Spotify test) - independent validation

**Learnings Applied from Story 1.4:**
- Use async patterns (same as Spotify helper)
- Module-level `_LOGGER` logging pattern
- Test script with CLI args and JSON metrics output
- Type hints and dataclasses for structured data
- Error handling with comprehensive try/except blocks

**Learnings Applied from Stories 1.1-1.3:**
- Component initialization pattern working correctly
- `hass.data[DOMAIN]` access pattern established
- Logging: INFO for operations, DEBUG for details, ERROR for failures
- Test approach: Manual execution for POC validation

**Critical POC Validation:**
- This story validates ADR-002 (Hybrid State Storage)
- Success = Epic 2 proceeds with in-memory game state architecture
- Failure = Pivot to optimized data structures or reduced update frequency
- Decision documented in Story 1.7 (POC Decision Document)

**Future Story Dependencies:**
- Story 1.7: POC Decision Document consumes metrics from this story
- Epic 2 (Story 2.3): In-Memory Game State Management builds upon this validation
- Performance data informs Epic 5 (scoring logic) and Epic 6 (real-time updates) design

**Novel Patterns Introduced:**
- Performance metrics collection for POC validation
- Data integrity validation with read-after-write pattern
- Stress test simulation of realistic gameplay load
- Confirmation of storage strategy (in-memory vs persistent)

## Dev Agent Record

### Context Reference

- docs/stories/1-5-data-registry-write-read-stress-test.context.xml

### Agent Model Used

claude-sonnet-4-5-20250929 (Sonnet 4.5)

### Debug Log References

**Implementation Approach:**
- Created complete state stress test implementation with dual pattern support
- Followed HA 2025 best practices using typed dataclasses
- Implemented comprehensive data integrity validation (read-after-write)
- Built test script with CLI args for flexible testing
- All code validated with Python syntax checks

**Technical Decisions:**
- Used TypeAlias instead of PEP 695 syntax for broader Python compatibility
- Implemented both hass.data and entry.runtime_data patterns for comparison
- Added comprehensive docstring documenting storage strategy and recommendations
- Performance tracking uses time.perf_counter() for high-precision measurement
- Data integrity validation compares expected vs actual on every write+read cycle

### Completion Notes List

**2025-11-11: Story Implementation Complete**

All development tasks (1-6, 8) completed successfully:
- Task 1: Created typed GameStateData, Player, Round, Guess dataclasses
- Task 2: Implemented dual-pattern state test module (state_test.py)
- Task 3: Added PerformanceMetrics tracking with storage_pattern field
- Task 4: Created POC test script with --pattern and --output CLI args
- Task 5: Implemented read-after-write data integrity validation
- Task 6: Updated __init__.py to import state_test module
- Task 8: Documented storage strategy in module docstring

**Key Features Implemented:**
- Dual pattern testing: hass.data (legacy) and entry.runtime_data (2025)
- 100 write+read cycles per pattern with latency tracking
- Comprehensive pattern comparison and recommendation logic
- JSON metrics output for POC Decision Document (Story 1.7)
- Full type hints and HA 2025 coding standards

**Testing & Validation:**
- All Python files validated with py_compile (no syntax errors)
- Code follows established patterns from Stories 1.1-1.4
- Ready for manual execution by user (Tasks 7, 9, 10)

**User Action Required:**
Tasks 7, 9, 10 require manual testing on live HA instance:
- Deploy component to HA test instance
- Run: `python tests/poc_state_test.py --output tests/poc_metrics.json --pattern both`
- Monitor HA responsiveness and logs during test
- Validate results against performance targets
- Save metrics for Story 1.7

### File List

**New Files Created:**
- home-assistant-config/custom_components/beatsy/state_test.py (State test module with dual pattern support)
- tests/poc_state_test.py (POC test script with CLI args)

**Modified Files:**
- home-assistant-config/custom_components/beatsy/__init__.py (Added state_test import and log message)
