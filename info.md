# Beatsy - Music Year Guessing Party Game

Beatsy transforms your Home Assistant into an interactive multiplayer party game where players compete to guess the release year of songs from your Spotify playlists.

## Key Features

- **Instant Player Join**: No authentication required - players join with just a name
- **Real-Time Multiplayer**: WebSocket-powered synchronized gameplay
- **Spotify Integration**: Works with your existing HA Spotify setup
- **Smart Scoring**: Points for exact, close, and near guesses
- **Betting System**: Optional 2x multiplier for confident players
- **Mobile-Optimized**: Perfect for phones and tablets

## How It Works

The admin (game host) selects a Spotify playlist and configures game settings. Players join via their phones by entering a name. When the game starts, songs play through your Spotify-enabled speaker, and players race to guess the release year before the timer expires. Points are awarded based on accuracy, with bonus points for exact guesses.

## Requirements

- Home Assistant 2024.1 or later
- Configured Spotify integration
- Spotify-capable media player (Sonos, Chromecast, etc.)
- Players on the same local network

## Quick Start

1. Install via HACS
2. Navigate to `/api/beatsy/admin` to configure and start a game
3. Players join at `/api/beatsy/player`
4. Have fun guessing!

## Technical Details

Beatsy is a custom Home Assistant integration built following the official integration blueprint structure. It uses unauthenticated HTTP views for player access, WebSocket for real-time communication, and integrates seamlessly with HA's Spotify integration.

All gameplay occurs locally on your network - no cloud services or external dependencies required.

## Changelog

### v0.1.0 - Initial Epic 2 Release

**Infrastructure Foundation**
- HACS-compliant distribution structure
- Production-ready component lifecycle management
- In-memory game state system
- Spotify media player detection
- HTTP route registration for admin and player interfaces
- WebSocket command infrastructure
- Configuration entry support (HA 2025 best practices)

This release establishes the core infrastructure that subsequent features will build upon. Admin and player UI implementations coming in future releases.

---

Perfect for parties, family gatherings, or just testing your music knowledge with friends!
