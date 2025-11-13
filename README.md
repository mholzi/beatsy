# Beatsy - Music Year Guessing Party Game for Home Assistant

Transform your Home Assistant into an interactive party game! Beatsy is a music year guessing game where players compete to identify the release year of songs from your Spotify playlists.

## Features

- **Zero-Friction Player Join**: Players join instantly via web interface without authentication
- **Real-Time Gameplay**: Live updates via WebSocket for synchronized multiplayer experience
- **Spotify Integration**: Uses your existing Home Assistant Spotify integration and playlists
- **Proximity-Based Scoring**: Points awarded for exact, close (±2 years), and near (±5 years) guesses
- **Betting System**: Optional bet multiplier for confident players
- **Mobile-First Design**: Optimized for phones and tablets
- **Local Network Only**: All gameplay happens on your local network - no cloud dependencies

## Prerequisites

- **Home Assistant Core 2024.1+**
- **Spotify Integration**: Configured and working in Home Assistant
  - At least one Spotify-capable media player (e.g., Sonos, Chromecast, native Spotify)
  - Active Spotify Premium account recommended for best experience
- **HACS** (Home Assistant Community Store) for easy installation

## Installation

### Method 1: HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/markusholzhaeuser/beatsy`
6. Select category: "Integration"
7. Click "Add"
8. Find "Beatsy" in the integration list and click "Install"
9. Restart Home Assistant

### Method 2: Manual Installation

1. Download the latest release from GitHub
2. Extract the `custom_components/beatsy/` directory
3. Copy it to your Home Assistant `config/custom_components/` directory
4. Restart Home Assistant

## Basic Usage

### For Admin (Game Host)

1. Navigate to `/api/beatsy/admin` in your browser
2. Select your Spotify media player
3. Enter a Spotify playlist URI
4. Configure game settings (timer duration, year range, scoring)
5. Click "Start Game" to begin
6. Control game flow: next song, end round, view leaderboard

### For Players

1. Navigate to `/api/beatsy/player` in your browser
2. Enter your name to join
3. Wait in lobby until admin starts the game
4. When a song plays:
   - Select the year you think the song was released
   - Optionally toggle "Bet" for 2x points (but lose points if wrong)
   - Submit before the timer runs out
5. View results after each round
6. Check the leaderboard to see your ranking

## Configuration

### Initial Setup (Home Assistant 2024.1+)

Beatsy uses the modern Home Assistant configuration entry system for easy setup:

1. **Add the Integration:**
   - Navigate to **Settings** → **Devices & Services** → **Integrations**
   - Click **+ ADD INTEGRATION** (bottom right)
   - Search for **"Beatsy"** and select it

2. **Configure Default Settings:**
   <!-- TODO: Add screenshot of config flow form here -->
   - **Timer Duration**: Set default round timer (10-120 seconds, default: 30)
   - **Year Range Minimum**: Earliest year for songs (1900-2024, default: 1950)
   - **Year Range Maximum**: Latest year for songs (1900-2024, default: 2024)
   - Click **Submit** to complete setup

3. **Verify Installation:**
   - Beatsy should appear in your Integrations list
   - Click the integration to see configuration options
   - Click **CONFIGURE** to update settings anytime

### Reconfiguring Settings

To update default game settings after installation:

1. Go to **Settings** → **Devices & Services** → **Integrations**
2. Find **Beatsy** in the list
3. Click **CONFIGURE**
4. Update timer duration or year ranges
5. Click **Submit** - integration will reload automatically with new settings

### Game Settings (Admin Interface)

Additional game settings are configured through the admin web interface at `/api/beatsy/admin`:

- **Timer Duration**: Per-round timer (uses default from config entry)
- **Year Range**: Song year filter (uses defaults from config entry)
- **Scoring**: Points for exact/close/near guesses
- **Bet Multiplier**: Risk/reward factor for betting
- **Playlist**: Select Spotify playlist for the game

### Backward Compatibility

**Note:** If you installed Beatsy before v0.2.0, the integration will continue to work with default settings. You can optionally migrate to the configuration entry system by:
1. Removing the old integration (if manually configured)
2. Following the "Initial Setup" steps above to add it via the UI

The integration gracefully handles both modern config entry and legacy setups.

## Troubleshooting

### "No Spotify players found"
- Verify Spotify integration is configured in Home Assistant
- Ensure at least one Spotify-capable media player is available
- Check that media player is powered on and connected

### Players can't connect
- Verify all devices are on the same local network
- Check Home Assistant is accessible at the URL players are using
- Clear browser cache and reload the player page

### Songs won't play
- Ensure Spotify Premium account is linked
- Check media player is not in use by another application
- Verify playlist URI is valid and contains tracks

## License

MIT License - see LICENSE file for details

## Support

For bugs, feature requests, or questions:
- Open an issue: https://github.com/markusholzhaeuser/beatsy/issues
- Discussions: https://github.com/markusholzhaeuser/beatsy/discussions

## HACS Official Submission (Future)

This integration is currently available as a custom repository. For future official HACS submission:

1. Ensure all HACS validation checks pass
2. Repository must be public on GitHub
3. Submit pull request to `hacs/default` repository
4. Await HACS team review and approval

**Current MVP Status**: Users add Beatsy as a custom repository. Official HACS submission is deferred to post-MVP after additional features and testing are complete.

## Acknowledgments

Built for the Home Assistant community. Uses the official HA integration blueprint structure and follows HACS distribution standards.

---

**Note**: This is an MVP release (v0.1.0). Features and UI are subject to change as development continues.
