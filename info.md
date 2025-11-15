# Beatsy - Music Year Guessing Party Game

Transform your Home Assistant into an interactive multiplayer party game! Beatsy lets players compete to guess the release year of songs from your Spotify playlists.

## What Makes Beatsy Special

- **Zero Friction**: Players join instantly with just a name - no accounts or authentication needed
- **Real-Time Fun**: WebSocket-powered live updates keep everyone synchronized
- **Your Music**: Uses your existing Spotify integration and playlists
- **Smart Scoring**: Points for exact (+100), close (+50), and near (+25) guesses
- **Betting Mechanic**: Confident? Toggle "Bet" for 2x points (but lose points if wrong!)
- **Mobile-First**: Designed for phones and tablets - perfect for party play

## How to Play

**For the Host:**
1. Open admin interface at `/api/beatsy/admin`
2. Select your Spotify media player and playlist
3. Configure settings (timer, year range, scoring)
4. Start the game and share the player URL

**For Players:**
1. Visit `/api/beatsy/player` on your phone
2. Enter your name to join the lobby
3. When a song plays, guess the year and optionally bet
4. Earn points based on accuracy
5. Check the leaderboard after each round

## Requirements

- **Home Assistant**: Version 2024.1 or later
- **Spotify Integration**: Configured with at least one media player
- **Spotify Premium**: Required for playback control
- **Network**: All players must be on the same local network

## Installation via HACS

1. Open HACS in Home Assistant
2. Go to Integrations → Three dots menu → Custom repositories
3. Add repository: `https://github.com/markusholzhaeuser/beatsy`
4. Category: Integration
5. Search for "Beatsy" and install
6. Restart Home Assistant
7. Add the Beatsy integration via Settings → Devices & Services

Full installation instructions and troubleshooting available in the [README](https://github.com/markusholzhaeuser/beatsy/blob/main/README.md).

## What's New

### v0.1.22 - Current MVP Release

**Complete Gameplay Experience:**
- Full admin interface with game configuration and control
- Player registration, lobby, and active round views
- Proximity-based scoring system (exact, close, near)
- Betting system with 2x multiplier
- Results view with round breakdown
- Overall leaderboard tracking
- Real-time WebSocket synchronization
- Mobile-responsive design
- Configuration entry flow (HA 2025 standards)

**Infrastructure:**
- HACS-compliant structure
- Spotify integration with media player detection
- HTTP routes for unauthenticated player access
- WebSocket command system
- In-memory game state management

## Coming Soon

- Enhanced error handling and rate limiting
- Comprehensive testing suite
- Detailed troubleshooting documentation
- Team play mode
- Historical statistics

---

**Perfect for**: Parties, family gatherings, game nights, or testing your music knowledge with friends!

**Support**: [GitHub Issues](https://github.com/markusholzhaeuser/beatsy/issues) | [Discussions](https://github.com/markusholzhaeuser/beatsy/discussions)
