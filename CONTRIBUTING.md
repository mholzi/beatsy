# Contributing to Beatsy

Welcome! Thank you for your interest in contributing to Beatsy, a music guessing game integration for Home Assistant. This guide will help you get started with contributing code, documentation, or bug reports.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Project Structure](#project-structure)
- [Contact](#contact)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, background, or identity.

### Expected Behavior

- Be respectful and constructive in all interactions
- Welcome newcomers and help them get started
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, discriminatory language, or personal attacks
- Trolling, insulting comments, or political attacks
- Publishing others' private information without permission
- Any conduct that would be inappropriate in a professional setting

### Reporting

If you experience or witness unacceptable behavior, please report it by opening a GitHub issue or contacting the maintainers directly.

## How to Contribute

### Reporting Bugs

Before creating a bug report, please:
1. Check existing issues to avoid duplicates
2. Ensure you're using the latest version
3. Verify the bug is reproducible

When reporting a bug, include:
- **Description**: Clear summary of the issue
- **Steps to reproduce**: Detailed steps to recreate the bug
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Environment**: Home Assistant version, Beatsy version, browser (if UI bug)
- **Logs**: Relevant error messages from Home Assistant logs
- **Screenshots**: If applicable (especially for UI bugs)

### Suggesting Features

Feature requests are welcome! When suggesting a feature:
1. Check existing feature requests to avoid duplicates
2. Provide clear use case and benefits
3. Consider implementation complexity
4. Be open to discussion and feedback

### Contributing Code

We welcome code contributions! Here's how to get started:

1. **Fork the repository** on GitHub
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes** following our code style guidelines
4. **Add tests** for your changes
5. **Run tests and linting** to ensure quality
6. **Commit your changes** with clear commit messages
7. **Push to your fork**: `git push origin feature/your-feature-name`
8. **Submit a pull request** with a detailed description

## Development Setup

### Prerequisites

- **Python 3.11+** (Home Assistant 2025 requirement)
- **Home Assistant Core** (for testing integration)
- **Spotify Account** (for Spotify API features)
- **Git** (for version control)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/beatsy.git
   cd beatsy
   ```

2. **Set up development environment**
   ```bash
   # Create virtual environment
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install --upgrade pip
   pip install -r requirements_dev.txt
   ```

3. **Install Beatsy in Home Assistant development mode**
   ```bash
   # Symlink to HA config directory
   ln -s $(pwd)/custom_components/beatsy ~/.homeassistant/custom_components/beatsy

   # Or copy files manually:
   # cp -r custom_components/beatsy ~/.homeassistant/custom_components/
   ```

4. **Configure Spotify integration** in Home Assistant (required for Spotify features)

5. **Restart Home Assistant** to load the integration

### Running Beatsy Locally

1. **Start Home Assistant** in development mode
   ```bash
   hass -c ~/.homeassistant
   ```

2. **Add Beatsy integration** via UI: Settings → Devices & Services → Add Integration → Search "Beatsy"

3. **Configure settings**:
   - Select Spotify media player
   - Choose playlist
   - Set timer duration and year range

4. **Access UIs**:
   - Admin UI: `http://localhost:8123/api/beatsy/admin`
   - Player UI: `http://localhost:8123/api/beatsy/player`

## Code Style Guidelines

### Python Code Style

We follow **PEP 8** with some Home Assistant-specific conventions.

#### Formatting

- **Line length**: 100 characters maximum (HA standard)
- **Indentation**: 4 spaces (no tabs)
- **Encoding**: UTF-8
- **Imports**: Sorted alphabetically, grouped by standard/third-party/local

#### Linting

Use **ruff** for fast, comprehensive linting:

```bash
# Check code
ruff check custom_components/beatsy/

# Fix auto-fixable issues
ruff check --fix custom_components/beatsy/

# Format code (alternative: use black)
ruff format custom_components/beatsy/
```

Or use **black** for formatting:

```bash
black custom_components/beatsy/
```

#### Type Hints

**Required** for all public functions and methods:

```python
from typing import Any, Optional

async def validate_player_name(name: str) -> ValidationResult:
    """Validate and sanitize player name."""
    # Implementation...
    return ValidationResult(valid=True, sanitized_value=name)

async def safe_play_track(
    hass: HomeAssistant,
    entity_id: str,
    track_uri: str,
    retries: int = 3
) -> bool:
    """Play track with retry logic and error handling."""
    # Implementation...
    return True
```

Use `from __future__ import annotations` for forward references.

#### Docstrings

**Required** for all public functions, classes, and modules.

Use **Google style** docstrings:

```python
def calculate_score(actual_year: int, guess_year: int, bet_placed: bool, config: dict) -> int:
    """Calculate points for a single guess based on proximity and bet.

    Pure function implementing proximity-based scoring algorithm.
    Deterministic, no side effects, fully testable.

    Args:
        actual_year: The actual year of the song.
        guess_year: The player's guessed year.
        bet_placed: Whether the player placed a bet on this guess.
        config: Game configuration dict with scoring values.

    Returns:
        Integer points earned for this guess (0 or positive).

    Raises:
        ValueError: If config is missing required scoring parameters.

    Example:
        >>> calculate_score(1995, 1995, False, {"points_exact": 10})
        10
        >>> calculate_score(1995, 1997, True, {"points_close": 5, "points_bet_multiplier": 2.0})
        10
    """
    # Implementation...
```

#### Naming Conventions

- **Functions/Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private members**: Prefix with `_` (e.g., `_internal_helper()`)

```python
# Good
class BeatsyGameState:
    MAX_PLAYERS = 50

    def __init__(self):
        self.current_round = None
        self._internal_cache = {}

    async def validate_config(self, config: dict) -> bool:
        """Validate game configuration."""
        return True

# Bad
class beatsyGameState:  # Wrong: Class should be PascalCase
    maxPlayers = 50  # Wrong: Constant should be UPPER_SNAKE_CASE

    def ValidateConfig(self, config):  # Wrong: Function should be snake_case
        return True
```

#### Code Quality Principles

1. **Readability**: Code is read more than written - prioritize clarity over cleverness
2. **Self-documenting**: Use descriptive names; avoid unnecessary comments
3. **Single Responsibility**: Each function should do one thing well
4. **DRY (Don't Repeat Yourself)**: Extract repeated logic into reusable functions
5. **Error Handling**: Fail gracefully with clear error messages

**Good examples:**

```python
# Good: Self-documenting function with clear responsibility
async def select_random_song(hass: HomeAssistant, entry_id: str) -> dict:
    """Select random song from available playlist without repeating."""
    state = get_game_state(hass, entry_id)

    if not state.available_songs:
        raise PlaylistExhaustedError("All songs have been played")

    return random.choice(state.available_songs)

# Good: Clear error handling
try:
    await play_track(hass, entity_id, track_uri)
except HomeAssistantError as e:
    _LOGGER.error("Playback failed: %s", e)
    raise PlaybackError(f"Failed to play track: {e}") from e
```

**Bad examples:**

```python
# Bad: Cryptic variable names
def f(x, y):
    """Process data."""
    a = x + y
    b = a * 2
    return b

# Bad: Too complex, multiple responsibilities
def process_everything(hass, data):
    """Process data and update state."""
    # Validation
    if not data: return None
    # Parsing
    parsed = json.loads(data)
    # Business logic
    result = parsed['value'] * 2
    # State update
    hass.data[DOMAIN]['state'] = result
    # API call
    await hass.services.async_call('notify', 'send', {'message': result})
    # Logging
    _LOGGER.info("Done")
    return result
```

### JavaScript Code Style

#### Formatting

- **Indentation**: 2 spaces (consistent with web conventions)
- **Line length**: ~100 characters (flexible)
- **Semicolons**: Use them for statement termination
- **Quotes**: Single quotes for strings (e.g., `'hello'`)

#### Modern JavaScript

Use **modern ES6+ syntax**:

```javascript
// Good: Use const/let
const playerName = 'Alice';
let score = 0;

// Bad: Avoid var
var playerName = 'Alice';

// Good: Arrow functions
const handleClick = (event) => {
    console.log('Clicked!', event);
};

// Good: Template literals
const message = `Player ${playerName} scored ${score} points`;

// Good: Destructuring
const {year, artist, title} = song;

// Good: Async/await
async function fetchData() {
    const response = await fetch('/api/data');
    const data = await response.json();
    return data;
}
```

#### Comments

Add comments for **complex logic** or **non-obvious behavior**:

```javascript
/**
 * Calculate remaining time from round start timestamp.
 * Uses client-side calculation to avoid timer desync issues.
 * Grace period accounts for network latency.
 */
function calculateRemainingTime(startedAt, duration) {
    const elapsed = Date.now() - startedAt;
    const gracePeriod = 2000; // 2 seconds for network latency
    return Math.max(0, duration + gracePeriod - elapsed);
}

// Complex WebSocket message format
ws.send(JSON.stringify({
    type: 'beatsy/submit_guess',
    player_name: playerName,
    year_guess: year,
    bet_placed: betActive,
    id: Date.now()  // Required by HA WebSocket API
}));
```

Avoid **redundant comments**:

```javascript
// Bad: Comment just restates code
counter += 1; // Increment counter

// Good: Comment explains WHY
counter += 1; // Account for zero-indexed array in next iteration
```

#### Naming Conventions

- **Functions/Variables**: `camelCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Classes** (if used): `PascalCase`

```javascript
// Good
const MAX_RETRIES = 3;
let playerName = 'Alice';

function handleSubmitGuess(yearGuess) {
    console.log('Submitting guess:', yearGuess);
}

// Bad
const maxRetries = 3;  // Should be UPPER_SNAKE_CASE for constants
let PlayerName = 'Alice';  // Should be camelCase

function HandleSubmitGuess(yearGuess) {  // Should be camelCase
    console.log('guess:', yearGuess);
}
```

#### Linting (Optional for MVP)

For production projects, consider **ESLint**:

```bash
npm install --save-dev eslint
npx eslint www/js/
```

Example `.eslintrc.json`:

```json
{
  "env": {
    "browser": true,
    "es2021": true
  },
  "extends": "eslint:recommended",
  "parserOptions": {
    "ecmaVersion": 12,
    "sourceType": "module"
  },
  "rules": {
    "indent": ["error", 2],
    "quotes": ["error", "single"],
    "semi": ["error", "always"]
  }
}
```

## Testing Requirements

All code contributions **must include tests**.

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_game_state.py

# Run with coverage
pytest --cov=custom_components/beatsy tests/

# Run only fast tests (skip slow integration tests)
pytest -m "not slow" tests/
```

### Test Coverage

- **Target**: >80% code coverage for Python code
- **Required**: Tests for all new features
- **Required**: Tests for bug fixes to prevent regressions

Check coverage:

```bash
pytest --cov=custom_components/beatsy --cov-report=html tests/
# Open htmlcov/index.html in browser
```

### Writing Tests

Use **pytest** with descriptive test names:

```python
import pytest
from custom_components.beatsy.game_state import calculate_score

def test_calculate_score_exact_match_without_bet():
    """Test exact year match awards correct points (no bet)."""
    config = {"points_exact": 10, "points_bet_multiplier": 2.0}

    score = calculate_score(
        actual_year=1995,
        guess_year=1995,
        bet_placed=False,
        config=config
    )

    assert score == 10

def test_calculate_score_exact_match_with_bet():
    """Test exact year match with bet multiplier."""
    config = {"points_exact": 10, "points_bet_multiplier": 2.0}

    score = calculate_score(
        actual_year=1995,
        guess_year=1995,
        bet_placed=True,
        config=config
    )

    assert score == 20  # 10 * 2.0

@pytest.mark.parametrize("actual,guess,expected_points", [
    (1995, 1997, 5),  # ±2 years = close
    (1995, 1993, 5),
    (1995, 2000, 2),  # ±5 years = near
    (1995, 1990, 2),
    (1995, 1985, 0),  # >5 years = wrong
])
def test_calculate_score_proximity_ranges(actual, guess, expected_points):
    """Test all proximity ranges award correct points."""
    config = {
        "points_exact": 10,
        "points_close": 5,
        "points_near": 2,
        "points_wrong": 0,
        "points_bet_multiplier": 1.0
    }

    score = calculate_score(
        actual_year=actual,
        guess_year=guess,
        bet_placed=False,
        config=config
    )

    assert score == expected_points
```

### Mocking External Services

Mock **Spotify API** and **Home Assistant** services:

```python
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.mark.asyncio
async def test_play_track_success(hass):
    """Test successful track playback."""
    with patch('homeassistant.core.ServiceRegistry.async_call') as mock_call:
        mock_call.return_value = None

        result = await play_track(
            hass,
            'media_player.spotify_living_room',
            'spotify:track:123'
        )

        assert result is True
        mock_call.assert_called_once_with(
            'media_player',
            'play_media',
            {
                'entity_id': 'media_player.spotify_living_room',
                'media_content_id': 'spotify:track:123',
                'media_content_type': 'music'
            }
        )
```

### Integration Tests

Add **integration tests** for user-facing features:

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_game_round_flow(hass, setup_integration):
    """Test complete round: start → guess → scoring → leaderboard."""
    # Setup
    await add_player(hass, "Alice", "session1")
    await add_player(hass, "Bob", "session2")

    # Start round
    song = await select_random_song(hass)
    round_state = await initialize_round(hass, song)

    # Submit guesses
    await add_guess(hass, "Alice", 1995, bet_placed=True)
    await add_guess(hass, "Bob", 1997, bet_placed=False)

    # End round and calculate scores
    results = await calculate_round_scores(hass)
    leaderboard = get_leaderboard(hass)

    # Assertions
    assert len(results) == 2
    assert leaderboard[0]["player_name"] == "Alice"  # Alice should win with bet
```

## Pull Request Process

### Before Submitting

1. **Test your changes** locally
2. **Run linting** and fix all errors
3. **Update documentation** if you changed APIs or features
4. **Add changelog entry** if applicable

### PR Title Format

Use clear, descriptive titles:

- `feat: Add bet multiplier configuration`
- `fix: Resolve timer desync on slow networks`
- `docs: Update installation guide`
- `refactor: Extract validation logic to separate module`
- `test: Add integration tests for reconnection flow`

### PR Description Template

```markdown
## Description
Brief summary of changes

## Motivation
Why is this change needed?

## Changes
- List of specific changes made
- Include any breaking changes

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Linting passes (ruff/black)
- [ ] Documentation updated
- [ ] No breaking changes (or marked as BREAKING)
```

### Review Process

1. **Automated checks** run on all PRs (CI/CD if configured)
2. **Code review** by maintainers (expect 1-3 days)
3. **Feedback incorporation**: Address review comments
4. **Approval**: Once approved, maintainers will merge

### After Merge

- PR will be merged to `main` branch
- Changes will be included in next release
- You'll be credited in release notes

## Project Structure

```
beatsy/
├── custom_components/beatsy/    # Integration code
│   ├── __init__.py              # Entry point, component setup
│   ├── config_flow.py           # Configuration UI flow
│   ├── const.py                 # Constants (DOMAIN, etc.)
│   ├── game_state.py            # Game state management
│   ├── websocket_api.py         # WebSocket command handlers
│   ├── websocket_handler.py     # WebSocket connection management
│   ├── http_view.py             # HTTP routes (admin/player UIs)
│   ├── spotify_helper.py        # Spotify API integration
│   ├── spotify_service.py       # Spotify playback services
│   ├── validation.py            # Input validation and sanitization
│   ├── rate_limiter.py          # Rate limiting for spam prevention
│   ├── error_responses.py       # Standardized error responses
│   ├── events.py                # WebSocket event helpers
│   ├── manifest.json            # HA integration metadata
│   └── www/                     # Frontend files
│       ├── admin.html           # Admin UI
│       ├── start.html           # Player UI
│       ├── css/                 # Styles
│       └── js/                  # JavaScript modules
│           ├── ui-admin.js      # Admin UI logic
│           ├── ui-player.js     # Player UI logic
│           ├── ui-results.js    # Results view
│           └── utils.js         # Shared utilities
├── docs/                        # Documentation
│   ├── stories/                 # User stories
│   ├── epics.md                 # Epic definitions
│   ├── tech-spec-epic-*.md      # Technical specifications
│   └── sprint-status.yaml       # Development tracking
├── tests/                       # Test suite
│   ├── test_game_state.py       # State management tests
│   ├── test_validation.py       # Validation tests
│   └── conftest.py              # pytest fixtures
├── pyproject.toml               # Python project configuration
├── README.md                    # User-facing documentation
├── CONTRIBUTING.md              # This file
├── LICENSE                      # MIT License
└── hacs.json                    # HACS metadata
```

### Key Modules

- **game_state.py**: Core game logic (rounds, scoring, state management)
- **websocket_api.py**: WebSocket command handlers (join, guess, bet, etc.)
- **validation.py**: Input validation and XSS prevention
- **spotify_helper.py**: Spotify API integration (playlist, playback)
- **UI files**: Mobile-first web interfaces (admin and player)

## Contact

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and community support
- **Pull Requests**: For code contributions

Thank you for contributing to Beatsy! Your efforts help make this project better for everyone.
