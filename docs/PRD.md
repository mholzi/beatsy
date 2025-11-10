# Beatsy - Product Requirements Document

**Author:** Markus
**Date:** 2025-11-09
**Version:** 1.0

---

## Executive Summary

Beatsy is a Home Assistant Custom Component (HACS) that transforms your smart home into an interactive party game platform. Inspired by the popular Hitster board game, Beatsy brings the excitement of music year-guessing to your living room using your existing Spotify integration and Home Assistant media players.

**The Vision:** Create the perfect social gathering game with zero friction - guests simply open a link on their phones, the music plays through your HA speakers, and everyone competes to guess song release years while building memories together.

**Core Experience:** An admin sets up the game through a web interface, players join instantly by entering their name, and rounds of music trivia begin. Players see album art, artist, and song title, then race against a 30-second timer to guess the year. A proximity-based scoring system rewards accuracy, while a betting mechanism adds strategic risk/reward. After each round, players see detailed results and live leaderboards, creating moments of celebration and friendly competition.

### What Makes This Special

**The Magic Moment:** Your smart home becomes the life of the party. Friends gather, music fills the room from your HA speakers, and everyone's frantically guessing on their phones. Someone bets big and nails a 1983 song - the room erupts. The leaderboard updates live. The next song starts. The energy is electric.

**Why Beatsy is Special:**
- **Zero Friction:** No apps to download, no accounts, no setup time - just share a link and play
- **Smart Home Native:** Uses your existing Home Assistant infrastructure (Spotify + media players)
- **Social-First:** Designed for people in the same room, not isolated screen time
- **Perfect Ice-Breaker:** Get any gathering energized in under 60 seconds
- **Nostalgia Engine:** Music triggers memories, debates about eras, and shared experiences
- **Your House = Game Console:** A completely novel use of smart home technology

---

## Project Classification

**Technical Type:** Web Application (Browser-based, Mobile-first)
**Domain:** General (Social Gaming / Entertainment)
**Complexity:** Low-Medium

**Classification Details:**

This is a **Home Assistant Custom Component** that:
- Integrates with Home Assistant Core via HACS (Home Assistant Community Store)
- Provides a web-based user interface (admin + player views)
- Interfaces with Spotify integration for music playback
- Uses Home Assistant's data registry for state persistence (no helper entities)
- Serves multiple concurrent users via websockets/HTTP

**Technical Stack:**
- Backend: Python (Home Assistant integration)
- Frontend: HTML/CSS/JavaScript (mobile-optimized web interface)
- Integration: Spotify API via HA's existing Spotify integration
- Storage: Home Assistant Registry API
- Real-time: WebSockets for live updates (leaderboards, bets, timers)

{{#if domain_context_summary}}

### Domain Context

{{domain_context_summary}}
{{/if}}

---

## Success Criteria

**Beatsy succeeds when:**

**Primary Success Metrics:**

1. **Instant Playability** - From sharing the link to first song playing: < 60 seconds
   - Admin setup: < 30 seconds (select player, paste playlist, start)
   - Player join: < 10 seconds (open link, type name, ready)
   - Zero technical friction or confusion

2. **Engagement & Energy** - Players are fully engaged, not distracted
   - Players complete 80%+ of rounds (don't abandon mid-game)
   - At least 30% of players use the BET feature (indicates strategic engagement)
   - Admin starts at least 10 songs per session (game has momentum)

3. **Social Magic** - Creates memorable moments
   - Players return for repeat sessions (not a one-time novelty)
   - "Wow" reactions when first introduced ("You built this in Home Assistant?!")
   - Organic sharing (players tell others about it)

4. **Technical Reliability** - No technical issues break the experience
   - Real-time updates work flawlessly (leaderboards, timers, bets visible instantly)
   - No music playback failures or sync issues
   - Handles 10+ concurrent players smoothly

5. **Home Assistant Native** - Feels like it belongs in the HA ecosystem
   - Installable via HACS (standard HA distribution)
   - Uses HA patterns (no external databases, uses registry)
   - Respects HA's Spotify integration (doesn't conflict or duplicate)

**Success Means:**
- The game becomes the go-to party starter for HA users
- Friends ask "Can we play Beatsy again?" when visiting
- Players experience that "wow, this is amazing" moment when they realize their smart home is the game console
- Zero technical barriers prevent the social magic from happening

---

## Product Scope

### MVP - Minimum Viable Product

**Core Game Loop (Must Have):**
- Admin web interface (`/admin.html`) to configure and control game
  - Select Home Assistant Spotify media player from dropdown
  - Paste Spotify playlist URI
  - Configure game settings (timer duration, point values, year range)
  - Start game (clears previous players)
  - Admin registers own name and sees "Next Song" button in player view

- Player web interface (`/start.html`) for joining and playing
  - Simple name registration (no password, no email)
  - Lobby view while waiting for first song
  - Active game view with:
    - Album cover, artist name, song title
    - Year dropdown selector (configurable range, default 1950-2024)
    - "BET ON IT" checkbox/button
    - 30-second countdown timer
    - Live bet indicators (see who's betting)

- Round results view (shown after timer expires)
  - Round Results Board: All players sorted by proximity to correct year
    - Player name, their guess, actual year, points earned, bet indicator
  - Overall Leaderboard: Top 5 + current player's position
  - "Waiting for next song..." state until admin advances

- Core game mechanics
  - Proximity-based scoring (configurable in admin):
    - Exact year: 10 points
    - Within ±2 years: 5 points
    - Within ±5 years: 2 points
    - Wrong: 0 points
  - Betting: Doubles points (win or lose) - ±20 for exact
  - Random song selection from playlist (no repeats in same game)
  - All players guess simultaneously (30-second window)

- Backend integration
  - Home Assistant custom component (Python)
  - HACS compatible installation
  - Uses HA's Spotify integration for playback
  - Stores game state in HA registry (no helper entities)
  - WebSocket support for real-time updates

- Technical requirements
  - Mobile-first responsive design (primary use case: phones)
  - Supports 10+ concurrent players
  - Works on local network (same WiFi as HA instance)

**MVP Must Deliver:**
The complete party game experience - from zero to playing in under 60 seconds, with smooth gameplay, live scoring, and the social magic intact.

### Growth Features (Post-MVP)

**Phase 1 - Enhanced Gameplay:**
- Difficulty modes (Original, Pro, Expert) like physical Hitster
  - Pro: Must name artist + title for points
  - Expert: Must name exact year + artist + title
- Custom scoring formulas (admin-defined point ranges)
- Round history view (review past rounds in current game)
- Sound effects for correct/incorrect guesses
- Celebration animations for perfect scores

**Phase 2 - Social Features:**
- Player profiles (optional, saved across sessions)
- All-time leaderboards (persistent stats)
- Game history/archives
- Share results to social media (leaderboard screenshots)
- Team mode (players form teams, combined scores)

**Phase 3 - Content & Customization:**
- Multiple playlist support (rotate between playlists)
- Genre-specific games (80s night, rock anthems, etc.)
- Custom themes (color schemes, fonts)
- Admin can skip songs mid-round
- Pause/resume functionality

**Phase 4 - Advanced Integration:**
- Home Assistant automation triggers (game start/end, player wins)
- Smart home notifications (lights flash on correct answer, etc.)
- Voice announcements through TTS
- Integration with HA dashboards (game status cards)

### Vision (Future)

**The Ultimate Smart Home Party Platform:**
- Multiple game modes beyond Hitster-style (trivia, karaoke voting, etc.)
- Cross-game leaderboards and achievements
- Tournament mode (brackets, playoffs)
- Remote play capability (players join from different locations)
- AI-powered playlist generation based on player preferences
- Integration with Home Assistant presence detection (auto-invite nearby users)
- Beatsy becomes the #1 HACS download for social/entertainment
- The reference implementation for "party games in your smart home"

**Long-term Vision:**
Beatsy demonstrates that Home Assistant isn't just automation - it's the platform for shared experiences. Your house becomes the most fun place to gather because you can instantly launch amazing social experiences using the tech you already have.

---

{{#if domain_considerations}}

## Domain-Specific Requirements

{{domain_considerations}}

This section shapes all functional and non-functional requirements below.
{{/if}}

---

{{#if innovation_patterns}}

## Innovation & Novel Patterns

{{innovation_patterns}}

### Validation Approach

{{validation_approach}}
{{/if}}

---

{{#if project_type_requirements}}

## {{project_type}} Specific Requirements

{{project_type_requirements}}

{{#if endpoint_specification}}

### API Specification

{{endpoint_specification}}
{{/if}}

{{#if authentication_model}}

### Authentication & Authorization

{{authentication_model}}
{{/if}}

{{#if platform_requirements}}

### Platform Support

{{platform_requirements}}
{{/if}}

{{#if device_features}}

### Device Capabilities

{{device_features}}
{{/if}}

{{#if tenant_model}}

### Multi-Tenancy Architecture

{{tenant_model}}
{{/if}}

{{#if permission_matrix}}

### Permissions & Roles

{{permission_matrix}}
{{/if}}
{{/if}}

---

{{#if ux_principles}}

## User Experience Principles

{{ux_principles}}

### Key Interactions

{{key_interactions}}
{{/if}}

---

## Functional Requirements

### FR-1: Home Assistant Integration

**FR-1.1: HACS Installation**
- Beatsy must be installable via HACS (Home Assistant Community Store)
- Standard HACS manifest structure (`hacs.json`)
- Automatic updates through HACS
- **Acceptance Criteria:** User can search "Beatsy" in HACS, click install, restart HA, and component is active

**FR-1.2: Spotify Integration**
- Detect and use existing HA Spotify integration
- Do not require separate Spotify authentication (leverage HA's existing connection)
- Support selecting any Spotify-capable media player from HA
- **Acceptance Criteria:** Admin dropdown shows all available Spotify media players from HA configuration

**FR-1.3: Data Persistence**
- Store all game state in Home Assistant's data registry (no helper entities)
- Persist: game configuration, active players, scores, round history, played songs
- Data clears when "Start Game" is clicked (fresh session)
- **Acceptance Criteria:** No `input_*` helper entities created; data survives HA restarts during active game

**FR-1.4: WebSocket Communication**
- Real-time updates to all connected clients (players and admin)
- Events: player joins, bet placed, timer tick, round complete, leaderboard update
- **Acceptance Criteria:** When one player places bet, all other players see indicator within 500ms

### FR-2: Admin Interface (`/admin.html`)

**FR-2.1: Game Configuration**
- **Media Player Selection:** Dropdown of all Spotify-enabled media players
- **Playlist Input:** Text field for Spotify playlist URI
- **Timer Duration:** Number input (default: 30 seconds, range: 10-120)
- **Year Range:** Min/max year dropdowns (default: 1950-2024)
- **Point Values:** Configurable scores for exact/±2/±5 (defaults: 10/5/2)
- **Bet Multiplier:** Configurable (default: 2x = ±20 for exact)
- **Acceptance Criteria:** All settings persist in registry; settings visible on admin panel with sensible defaults

**FR-2.2: Game Control**
- **Start Game Button:** Clears all previous players, resets scores, loads playlist
- **Game Status Display:** Shows number of joined players, songs remaining in playlist
- **Acceptance Criteria:** Clicking "Start Game" immediately clears lobby and allows new player registration

**FR-2.3: Admin as Player**
- Admin must register name like any player (no special treatment in gameplay)
- Admin player view shows additional "Next Song" button (hidden for other players)
- Admin can play and score points while controlling game flow
- **Acceptance Criteria:** Admin name appears in leaderboard; only admin sees song control button

### FR-3: Player Interface (`/start.html`)

**FR-3.1: Player Registration**
- **Name Input:** Single text field (max 20 characters)
- **Join Button:** Submits registration
- **No Authentication:** No passwords, emails, or accounts required
- **Duplicate Handling:** If name exists, append number (e.g., "Sarah" → "Sarah (2)")
- **Acceptance Criteria:** Player types name, clicks join, immediately enters lobby in < 3 seconds

**FR-3.2: Lobby View**
- Display: "Waiting for game to start..."
- Show: List of players who have joined (live updates)
- Show: Total player count
- **Acceptance Criteria:** Lobby updates in real-time as players join; clear indication game hasn't started

**FR-3.3: Active Round View**
- **Song Information Display:**
  - Album cover art (from Spotify metadata)
  - Artist name
  - Song title
  - Note: Year is NOT shown (that's what they're guessing!)
- **Year Selection:** Dropdown populated with configured year range
- **Bet Toggle:** Checkbox or button labeled "BET ON IT" (clearly visible)
- **Timer Display:** Large countdown showing remaining seconds
- **Live Bet Indicators:** Visual list/badges showing which players have bet
- **Submit Button:** Confirms year guess and bet choice
- **Lock State:** After submission, inputs disabled but timer still visible
- **Acceptance Criteria:** All information clearly visible on mobile screen; 30-second timer counts down smoothly; bet indicators update live

**FR-3.4: Round Results View**
- **Correct Year Revealed:** Large, prominent display of actual release year
- **Round Results Board:** Table/list showing ALL players, sorted by proximity to correct year
  - Columns: Player Name | Their Guess | Points Earned | Bet Indicator (icon/badge)
  - Highlight current player's row
- **Overall Leaderboard:**
  - Top 5 players by total points
  - Current player's position (if not in top 5, show separately below)
  - Total accumulated points for each player
- **Waiting State:** After viewing results, show "Waiting for next song..." until admin advances
- **Acceptance Criteria:** Results appear immediately when timer expires; leaderboards accurate; clear visual hierarchy

### FR-4: Game Mechanics

**FR-4.1: Song Selection**
- Load all tracks from provided Spotify playlist URI
- Select songs randomly from playlist
- Track played songs (no repeats in same game session)
- Handle playlist exhaustion (notify admin if all songs played)
- **Acceptance Criteria:** Songs play in random order; no song plays twice in one game

**FR-4.2: Music Playback**
- Use HA's Spotify integration to play selected song on configured media player
- Start playback automatically when admin clicks "Next Song"
- Song plays for full 30-second guess window (or configured duration)
- **Acceptance Criteria:** Music starts playing on HA media player within 2 seconds of "Next Song" click

**FR-4.3: Scoring Calculation**
- **Base Points (configurable):**
  - Exact year match: 10 points (default)
  - Within ±2 years: 5 points (default)
  - Within ±5 years: 2 points (default)
  - Beyond ±5 years: 0 points
- **Bet Modifier:** If "BET ON IT" selected, multiply points by 2 (can be negative)
  - Exact with bet: 20 points
  - Wrong with bet: -20 points (or 0 if base was 0)
- **Edge Case:** If multiple scoring tiers apply, use highest tier (e.g., ±2 trumps ±5)
- **Acceptance Criteria:** Scoring accurate for all scenarios; negative scores supported; leaderboard reflects calculations

**FR-4.4: Timer Management**
- Start 30-second countdown when song begins
- Synchronize timer across all clients (WebSocket broadcast)
- When timer expires:
  - Lock all inputs (no more guesses accepted)
  - Calculate scores
  - Transition to results view
  - Stop music playback (optional - or let song continue)
- **Acceptance Criteria:** All players see timer expire simultaneously (±1 second tolerance); late submissions rejected

**FR-4.5: Game Session Management**
- Game session exists from "Start Game" until admin closes/restarts
- Support admin leaving and returning (session persists)
- Handle players disconnecting/reconnecting (rejoin with same name)
- **Acceptance Criteria:** Game continues if admin refreshes page; players can refresh without losing progress

### FR-5: Real-Time Features

**FR-5.1: Live Bet Visibility**
- When any player clicks "BET ON IT", broadcast to all clients
- Display betting players as badges/icons on active round screen
- Updates appear within 500ms
- **Acceptance Criteria:** Social pressure visible - everyone knows who's confident

**FR-5.2: Leaderboard Updates**
- After each round, recalculate and broadcast updated leaderboard
- Top 5 + current player position
- Support for ties (multiple players with same score)
- **Acceptance Criteria:** Leaderboard updates immediately after timer expires; accurate rankings

**FR-5.3: Player Join/Leave Notifications**
- Lobby shows live player count
- Players joining mid-game join for next round (don't disrupt current round)
- **Acceptance Criteria:** Lobby player list updates live; mid-game joins handled gracefully

### FR-6: Mobile-First Design

**FR-6.1: Responsive Layout**
- Primary target: Phone screens (320px - 428px width)
- All interfaces must be usable on iPhone SE through iPhone Pro Max
- Touch-friendly buttons (min 44x44px touch targets)
- Readable text without zooming
- **Acceptance Criteria:** All features accessible and usable on mobile Safari and Chrome

**FR-6.2: Performance**
- Fast page loads (< 2 seconds on 3G)
- Smooth animations and transitions
- No scrolling required for primary actions
- **Acceptance Criteria:** Game playable on slower connections without frustration

### FR-7: Admin Controls

**FR-7.1: Next Song Trigger**
- Admin sees "Next Song" button in player interface after viewing results
- Clicking advances game to next round:
  - Selects random unplayed song from playlist
  - Resets timer
  - Clears previous guesses
  - Starts music playback
- **Acceptance Criteria:** Only admin can advance; game flow controlled by admin

**FR-7.2: Game Stop/Reset**
- Admin can stop game manually (returns to setup screen)
- Option to review final leaderboard before exiting
- **Acceptance Criteria:** Clean exit from game; data optionally preserved for review

### FR-8: Error Handling

**FR-8.1: Spotify Integration Errors**
- Handle: Playlist not found, playback failures, token expiration
- Display clear error messages to admin
- Graceful degradation (show error, don't crash game)
- **Acceptance Criteria:** Users understand what went wrong and how to fix it

**FR-8.2: Network Issues**
- Handle: Client disconnections, WebSocket failures
- Auto-reconnect when possible
- Show connection status to players
- **Acceptance Criteria:** Players rejoin seamlessly; minimal disruption

**FR-8.3: Edge Cases**
- Handle: Empty playlist, all songs played, no players joined, invalid year range
- Prevent: Division by zero, negative timers, invalid scores
- **Acceptance Criteria:** No crashes; user-friendly error messages

---

## Non-Functional Requirements

### Performance

**NFR-P1: Response Time**
- Admin interface loads in < 2 seconds
- Player interface loads in < 2 seconds
- Page transitions (lobby → game → results) in < 500ms
- **Why it matters:** Fast setup is critical to the "zero friction" promise

**NFR-P2: Real-Time Updates**
- WebSocket events delivered in < 500ms
- Timer synchronization across clients within ±1 second
- Leaderboard updates visible within 500ms of round completion
- **Why it matters:** Social magic requires everyone seeing the same thing simultaneously

**NFR-P3: Music Playback**
- Song starts playing within 2 seconds of "Next Song" click
- No audio stuttering or interruptions during 30-second window
- **Why it matters:** Music is the core experience - delays kill momentum

**NFR-P4: Concurrent Players**
- Support minimum 10 simultaneous players without degradation
- Support target 20 players smoothly
- Graceful degradation beyond 20 players (may increase latency but remain functional)
- **Why it matters:** Party games need to accommodate various group sizes

### Reliability

**NFR-R1: Uptime**
- Component must not crash Home Assistant
- Graceful failure modes (errors shown, game paused, not crashed)
- **Why it matters:** Can't break someone's entire smart home for a party game

**NFR-R2: Data Integrity**
- Scores calculated accurately 100% of the time
- No duplicate players in same game
- Played songs list maintained correctly (no repeats)
- **Why it matters:** Fairness is essential for competitive games

**NFR-R3: Network Resilience**
- Handle temporary WiFi dropouts gracefully
- Auto-reconnect WebSocket connections
- Players can rejoin after connection loss
- **Why it matters:** Home WiFi can be unreliable with many devices

**NFR-R4: Browser Compatibility**
- Works on mobile Safari (iOS)
- Works on Chrome mobile (Android)
- Works on desktop browsers (for admin on laptop/tablet)
- Graceful fallback for unsupported features
- **Why it matters:** Can't assume everyone has the same device

### Security

**NFR-S1: Local Network Only**
- Beatsy only accessible on local network (same as HA instance)
- No external internet exposure required
- Uses HA's existing authentication for admin panel access
- **Why it matters:** Party game doesn't need to be on the internet; security through isolation

**NFR-S2: Input Validation**
- Sanitize all player name inputs (prevent XSS)
- Validate Spotify playlist URIs (prevent injection)
- Validate numeric inputs (years, timers, points)
- **Why it matters:** Basic security hygiene even for trusted local users

**NFR-S3: Rate Limiting**
- Prevent spam registrations (max 1 join per IP per 5 seconds)
- Prevent rapid-fire betting toggles (debounce)
- **Why it matters:** Prevent accidental or malicious disruption

### Usability

**NFR-U1: Mobile-First Design**
- All text readable without zooming on 320px width screens
- Touch targets minimum 44x44px (Apple HIG standard)
- Single-column layouts (no horizontal scrolling)
- **Why it matters:** Primary use case is phones in hand while music plays

**NFR-U2: Visual Clarity**
- Timer clearly visible and prominent
- Current player's position highlighted in leaderboards
- Betting status unmistakable (large icons/badges)
- Results easy to scan (sorted, color-coded)
- **Why it matters:** Fast-paced game requires instant visual comprehension

**NFR-U3: Error Messages**
- User-friendly language (no technical jargon)
- Clear next steps ("Check your Spotify playlist URL")
- Errors don't block non-affected features
- **Why it matters:** Non-technical users need guidance, not confusion

### Integration

**NFR-I1: Home Assistant Compatibility**
- Compatible with Home Assistant Core 2024.1+
- Works with standard Spotify integration (no custom forks)
- No conflicts with other custom components
- **Why it matters:** Can't require special HA configurations

**NFR-I2: HACS Standards**
- Follows HACS repository structure
- Proper versioning (semantic versioning)
- Changelog maintained
- **Why it matters:** Standard distribution method for HA custom components

**NFR-I3: Spotify API Limits**
- Respect Spotify API rate limits
- Handle API errors gracefully (token expiration, etc.)
- Don't interfere with other Spotify usage in HA
- **Why it matters:** Can't break user's existing Spotify integrations

### Maintainability

**NFR-M1: Code Quality**
- Follow Home Assistant development guidelines
- Type hints for Python code
- Clear component structure (manifest, config flow, etc.)
- **Why it matters:** Community contributions and long-term maintenance

**NFR-M2: Documentation**
- README with installation instructions
- Configuration examples
- Troubleshooting guide
- **Why it matters:** Users need to understand how to set it up

**NFR-M3: Logging**
- Debug logs for troubleshooting (playlist loading, scoring, WebSocket events)
- Error logs for failures
- No excessive logging (keep HA logs clean)
- **Why it matters:** Developers and users need visibility when issues occur

---

## Implementation Planning

### Epic Breakdown Required

Requirements must be decomposed into epics and bite-sized stories (200k context limit).

**Recommended Epic Structure:**

1. **Epic 1: HACS Integration & HA Core**
   - Component manifest and HACS setup
   - Data registry integration
   - Spotify media player detection

2. **Epic 2: Admin Interface**
   - Admin web UI (`/admin.html`)
   - Game configuration
   - Start/stop game controls

3. **Epic 3: Player Interface - Registration & Lobby**
   - Player registration (`/start.html`)
   - Lobby view
   - WebSocket connection

4. **Epic 4: Game Mechanics - Core Loop**
   - Song selection from playlist
   - Timer management
   - Score calculation

5. **Epic 5: Real-Time Features**
   - WebSocket event broadcasting
   - Live bet indicators
   - Leaderboard updates

6. **Epic 6: Active Round UI**
   - Song display (cover, artist, title)
   - Year selection & betting
   - Timer countdown UI

7. **Epic 7: Results & Leaderboards**
   - Round results view
   - Leaderboard display
   - Waiting state

8. **Epic 8: Music Playback Integration**
   - Spotify API integration via HA
   - Playback control
   - Error handling

9. **Epic 9: Mobile Optimization**
   - Responsive design
   - Touch interactions
   - Performance optimization

10. **Epic 10: Testing & Polish**
    - Error handling
    - Edge case coverage
    - Documentation

**Next Step:** Run `/bmad:bmm:workflows:create-epics-and-stories` to create the detailed implementation breakdown.

---

## Technical Considerations

### Home Assistant Integration Points

**Component Structure:**
```
custom_components/beatsy/
├── __init__.py          # Component setup
├── manifest.json        # HACS metadata
├── config_flow.py       # Configuration UI (optional)
├── const.py            # Constants
├── game_manager.py     # Core game logic
├── websocket_api.py    # WebSocket handlers
├── www/                # Static web files
│   ├── admin.html
│   ├── start.html
│   ├── css/
│   └── js/
└── translations/       # i18n (optional)
```

**Key HA APIs to Use:**
- `hass.data` registry for game state
- `media_player` domain for Spotify control
- `websocket_api` for real-time communication
- `http` component for serving web interface

**Spotify Integration:**
- Use existing `spotify` integration entity
- Call `media_player.play_media` with Spotify URIs
- Fetch track metadata from Spotify API (via HA)

### Data Model

**Game State (stored in HA registry):**
```python
{
  "game_id": "uuid",
  "status": "lobby|active|paused|ended",
  "config": {
    "media_player": "media_player.spotify_living_room",
    "playlist_uri": "spotify:playlist:...",
    "timer_duration": 30,
    "year_range": [1950, 2024],
    "points": {"exact": 10, "close": 5, "near": 2},
    "bet_multiplier": 2
  },
  "players": [
    {"name": "Sarah", "total_points": 45, "session_id": "..."}
  ],
  "current_round": {
    "song": {"uri": "...", "title": "...", "artist": "...", "year": 1985, "cover": "..."},
    "guesses": [{"player": "Sarah", "year": 1987, "bet": true}],
    "started_at": "timestamp"
  },
  "played_songs": ["uri1", "uri2", ...],
  "round_history": [...]
}
```

### WebSocket Event Schema

**Client → Server:**
- `beatsy/join_game` - Player registration
- `beatsy/submit_guess` - Submit year guess + bet
- `beatsy/next_song` - Admin triggers next round
- `beatsy/start_game` - Admin starts game

**Server → Client:**
- `beatsy/player_joined` - New player in lobby
- `beatsy/round_started` - Song playing, timer started
- `beatsy/bet_placed` - Player placed bet (broadcast)
- `beatsy/timer_tick` - Countdown update
- `beatsy/round_ended` - Results available
- `beatsy/leaderboard_updated` - New standings

---

## References

**Inspiration:**
- Hitster Board Game: https://hitstergame.com/
- Gameplay research conducted 2025-11-09

**Home Assistant Resources:**
- HACS: https://hacs.xyz/
- HA Developer Docs: https://developers.home-assistant.io/
- Spotify Integration: https://www.home-assistant.io/integrations/spotify/

**No prior product briefs or research documents** (greenfield project)

---

## Next Steps

1. **Epic & Story Breakdown** (Required) - Run: `/bmad:bmm:workflows:create-epics-and-stories`
2. **Architecture** (Recommended) - Run: `/bmad:bmm:workflows:architecture` for technical decisions
3. **UX Design** (Optional) - Run: `/bmad:bmm:workflows:create-ux-design` for visual mockups

---

**What Makes Beatsy Special:**

_Beatsy transforms your Home Assistant into the ultimate party game platform - where your smart home becomes the social hub, music fills the room from your HA speakers, and everyone competes on their phones in real-time. Zero friction, maximum fun, pure social magic._

_Your house becomes the game console. That's the Beatsy magic._

---

_Created through collaborative discovery between Markus and AI facilitator on 2025-11-09._
