# Beatsy - Music Year Guessing Party Game for Home Assistant

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/markusholzhaeuser/beatsy.svg)](https://github.com/markusholzhaeuser/beatsy/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Transform your Home Assistant into an interactive party game! Beatsy is a music year guessing game where players compete to identify the release year of songs from your Spotify playlists.

Perfect for parties, family gatherings, or testing your music knowledge with friends!

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
- **Spotify Integration**: Configured and working in Home Assistant ([Configuration Guide](https://www.home-assistant.io/integrations/spotify/))
  - At least one Spotify-capable media player (e.g., Sonos, Chromecast, native Spotify)
  - Active Spotify Premium account (required for playback control)
- **HACS** (Home Assistant Community Store) for easy installation ([HACS Installation Guide](https://hacs.xyz/docs/setup/download))
- **Local Network Access**: All players must be on the same network as your Home Assistant instance

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

## Quick Start Guide

### Step 1: Access Admin Interface

Navigate to the admin interface in your browser:
```
http://YOUR_HOME_ASSISTANT_IP:8123/api/beatsy/admin
```

![Admin Interface](docs/screenshots/admin-interface.png)
*Admin interface showing game configuration options*

### Step 2: Configure Your First Game

1. **Select Media Player**: Choose your Spotify-enabled speaker from the dropdown
2. **Enter Playlist URI**:
   - Open Spotify and find a playlist
   - Click "Share" → "Copy Spotify URI"
   - Paste the URI (format: `spotify:playlist:37i9dQZF1DXcBWIGoYBM5M`)
3. **Adjust Settings** (optional):
   - Timer Duration: 30 seconds (default)
   - Year Range: 1950-2024 (default)
   - Scoring: Exact (+100), Close ±2 years (+50), Near ±5 years (+25)

### Step 3: Start the Game

Click "Start Game" to begin. Share the player URL with your guests:
```
http://YOUR_HOME_ASSISTANT_IP:8123/api/beatsy/player
```

You can also display a QR code for easy mobile access.

### For Admin (Game Host)

**During the Game:**
1. Monitor player list and game status
2. Control playback (next song, pause if needed)
3. End rounds when timer expires
4. View leaderboard between rounds
5. End game when complete

![Admin Controls](docs/screenshots/admin-controls.png)
*Admin game controls during active gameplay*

### For Players

**Joining and Playing:**

1. Navigate to `/api/beatsy/player` in your browser (or scan QR code)
2. Enter your name to join the lobby
3. Wait for the admin to start the game
4. When a song plays:
   - Listen carefully to identify the release year
   - Select the year from the dropdown (1950-2024)
   - Optionally toggle "Bet" for 2x points (risk: lose points if wrong)
   - Submit your guess before the timer runs out
5. View results showing:
   - Correct year
   - Your guess and points earned
   - Other players' guesses
6. Check the overall leaderboard after each round

![Player Interface](docs/screenshots/player-interface.png)
*Player interface during an active round*

![Results View](docs/screenshots/results-view.png)
*Results screen showing round outcome and leaderboard*

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

For comprehensive troubleshooting information, see the **[Troubleshooting Guide & FAQ](docs/TROUBLESHOOTING.md)**.

### Common Issues and Solutions

#### "No Spotify players found" or "Can't select media player"
**Problem**: Admin interface doesn't show any Spotify players in the dropdown.

**Solutions**:
- Verify the Spotify integration is configured in Home Assistant ([Setup Guide](https://www.home-assistant.io/integrations/spotify/))
- Ensure at least one Spotify-capable media player is available and online
- Check that the media player is powered on and connected to your network
- Restart the Spotify integration: Settings → Devices & Services → Spotify → Reload

#### Players can't access the player page
**Problem**: Players get "Access Denied" or connection errors when visiting `/api/beatsy/player`.

**Solutions**:
- Verify all player devices are on the same local network as Home Assistant
- Check that Home Assistant's HTTP component is configured correctly
- Ensure your firewall allows access to port 8123
- Try accessing from the admin device first to confirm connectivity
- Clear browser cache and try again in incognito/private mode
- For HTTPS setups: Ensure your SSL certificate is valid

#### Songs won't play or playback errors
**Problem**: Game starts but no music plays, or playback stops unexpectedly.

**Solutions**:
- Ensure you're using a Spotify Premium account (Free accounts don't support API playback)
- Check the media player is not in use by another application
- Verify the playlist URI is valid and contains tracks (test in Spotify app)
- Confirm the media player has an active internet connection
- Check Spotify integration token hasn't expired: Settings → Devices & Services → Spotify → Re-authenticate if needed
- Try playing music manually through Home Assistant to test the media player

#### WebSocket connection errors or players don't see updates
**Problem**: Players joined but don't see live updates, or "WebSocket disconnected" errors.

**Solutions**:
- Check Home Assistant logs for WebSocket errors: Settings → System → Logs
- Verify WebSocket is enabled in your HTTP configuration
- If using a reverse proxy (nginx, Caddy), ensure WebSocket passthrough is configured
- Check browser console for JavaScript errors (F12 → Console tab)
- Try a different browser or device to isolate the issue

#### Players see "Game not started" when it's running
**Problem**: Game shows as active on admin but players see lobby or error state.

**Solutions**:
- Refresh the player page (game state should sync)
- Check that players joined before the game started
- Verify the game session hasn't been reset on the backend
- Check Home Assistant logs for state management errors

#### Timer or round doesn't advance
**Problem**: Round timer stuck or doesn't end when it reaches zero.

**Solutions**:
- Check browser console for JavaScript errors
- Refresh admin page and use "End Round" manually
- Verify WebSocket connection is active
- Restart the game if issue persists

### Getting Help

If you encounter issues not covered here:

- **Full Troubleshooting Guide**: See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for detailed solutions, error messages, debug instructions, and FAQ
- **Search Issues**: Check [existing GitHub issues](https://github.com/markusholzhaeuser/beatsy/issues) for similar problems
- **Report a Bug**: [Open a new issue](https://github.com/markusholzhaeuser/beatsy/issues/new) with:
  - Home Assistant version
  - Beatsy version
  - Steps to reproduce
  - Relevant logs from Settings → System → Logs
  - Browser and device information
- **Community Discussion**: Join the [GitHub Discussions](https://github.com/markusholzhaeuser/beatsy/discussions) for questions and tips

### Enable Debug Logging

For detailed troubleshooting, enable debug logging in your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.beatsy: debug
```

Restart Home Assistant and check logs at Settings → System → Logs. See the [Troubleshooting Guide](docs/TROUBLESHOOTING.md) for more debugging information.

## Contributing

Contributions are welcome! Whether it's bug reports, feature requests, or code contributions:

- **Bug Reports**: [Open an issue](https://github.com/markusholzhaeuser/beatsy/issues/new) with detailed reproduction steps
- **Feature Requests**: [Start a discussion](https://github.com/markusholzhaeuser/beatsy/discussions) to propose new ideas
- **Pull Requests**: Fork the repository, make your changes, and submit a PR
  - Follow existing code style and patterns
  - Add tests for new features
  - Update documentation as needed
- **Documentation**: Help improve this README, add examples, or write guides

## Screenshots

### Admin Interface
![Admin Configuration](docs/screenshots/admin-interface.png)
*Configure game settings, select playlists, and control gameplay*

### Player Experience
![Player Round View](docs/screenshots/player-interface.png)
*Mobile-optimized interface for making guesses and placing bets*

![Results Screen](docs/screenshots/results-view.png)
*See round results and overall leaderboard*

### Gameplay Flow
![Lobby Screen](docs/screenshots/lobby-view.png)
*Players wait in the lobby before the game starts*

## Browser Support

Beatsy is designed with a mobile-first approach and has been extensively tested across all major browsers:

### Supported Browsers

| Platform | Browser | Minimum Version | Status |
|----------|---------|----------------|--------|
| **iOS** | Safari | 16.0+ | ✅ Fully Supported |
| **Android** | Chrome | 118.0+ | ✅ Fully Supported |
| **Desktop** | Chrome | 118.0+ | ✅ Fully Supported |
| **Desktop** | Firefox | 119.0+ | ✅ Fully Supported |
| **Desktop** | Safari | 16.0+ | ✅ Fully Supported |

### Key Features Tested

- **Mobile-First Design**: Optimized for phones (320px-428px width)
- **Touch Targets**: All buttons meet 44x44px minimum (Apple HIG standard)
- **WebSocket Support**: Real-time updates work across all browsers
- **Smooth Scrolling**: 60fps scrolling performance on mobile devices
- **Responsive Layout**: No horizontal scrolling, readable text on all screen sizes

**For detailed browser compatibility information, see [docs/browser-compatibility.md](docs/browser-compatibility.md).**

### Unsupported Browsers

- Internet Explorer 11 (no WebSocket support)
- iOS Safari <16.0 (outdated, please update)
- Very old Android browsers (<2022)

## Frequently Asked Questions

For more detailed answers and additional questions, see the [full FAQ in the Troubleshooting Guide](docs/TROUBLESHOOTING.md#faq).

**Q: Do players need Home Assistant accounts?**
A: No! Players join with just a name - no authentication required.

**Q: Can I use Spotify Free?**
A: Spotify Premium is required for playback control via the API.

**Q: How many players can join?**
A: Currently tested with up to 20 concurrent players. Performance may vary based on your Home Assistant hardware.

**Q: Can players join mid-game?**
A: Players should join before the game starts. Mid-game joining is not currently supported.

**Q: Do I need an internet connection?**
A: Yes, for Spotify streaming. However, all game communication happens locally on your network.

**Q: Can I use my own music files instead of Spotify?**
A: Not currently. Beatsy is designed specifically for Spotify integration.

**More questions?** See the [comprehensive FAQ](docs/TROUBLESHOOTING.md#faq) covering topics like browser support, Apple Music compatibility, admin participation, scoring customization, and more.

## Roadmap

Future enhancements being considered:

- Team play mode
- Custom scoring formulas
- Song hints and difficulty levels
- Historical statistics and player profiles
- Multiple playlist rotation
- Genre-specific game modes
- Official HACS default repository submission

## License

MIT License - see [LICENSE](LICENSE) file for details

Copyright (c) 2025 Markus Holzhaeuser

## Support & Community

For bugs, feature requests, or questions:
- **Issues**: [GitHub Issues](https://github.com/markusholzhaeuser/beatsy/issues)
- **Discussions**: [GitHub Discussions](https://github.com/markusholzhaeuser/beatsy/discussions)
- **Documentation**: This README and inline code documentation

## Acknowledgments

Built for the Home Assistant community with love. Special thanks to:
- The Home Assistant core team for the excellent platform
- HACS for making custom integrations easy to distribute
- All contributors and beta testers

---

**Version**: 0.1.22 (MVP Release)

**Status**: Active development - Features and UI subject to change based on community feedback

Made with music and code by [Markus Holzhaeuser](https://github.com/markusholzhaeuser)
