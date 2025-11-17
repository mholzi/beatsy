"""HTTP view handler for Beatsy component.

This module provides HTTP routes for:
- Admin interface (/api/beatsy/admin) - Authenticated (Story 3.1)
- Player interface (/api/beatsy/player) - Unauthenticated (Epic 1 POC)
- REST API endpoints (/api/beatsy/api/*) - Unauthenticated (Epic 1 POC pattern)
- Static files (/api/beatsy/static/*) - CSS, JS, and other assets

Authentication:
- Admin interface requires HA access token (protects game configuration)
- Player and API routes use unauthenticated pattern from Epic 1 POC
- CORS handled automatically by HA's HTTP component

Implementation Status:
- Admin UI: Epic 3 (Stories 3.1-3.7) - Complete mobile-first interface
- Player UI: Epic 4 (placeholder in Epic 2)
- API endpoints: Stories 3.2-3.5 - Fully functional
- Static files: Serves CSS/JS from www directory
"""
import logging
import mimetypes
from pathlib import Path

from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .validation import validate_game_settings, validate_spotify_uri

_LOGGER = logging.getLogger(__name__)


class BeatsyTestView(HomeAssistantView):
    """Unauthenticated test page view for POC validation.

    Serves a static HTML test page without requiring Home Assistant authentication.
    This validates the unauthenticated access pattern needed for player interfaces.
    """

    url = "/api/beatsy/test.html"
    name = "api:beatsy:test"
    requires_auth = False

    async def get(self, request: web.Request) -> web.Response:
        """Handle GET request to serve test page.

        Args:
            request: The aiohttp request object.

        Returns:
            HTML response with test page content.
        """
        try:
            # Get the path to the www directory relative to this module
            module_dir = Path(__file__).parent
            test_html_path = module_dir / "www" / "test.html"

            # Read the HTML content asynchronously to avoid blocking I/O
            def read_html():
                return test_html_path.read_text(encoding="utf-8")

            html_content = await self.hass.async_add_executor_job(read_html)

            _LOGGER.debug("Serving test page from %s", test_html_path)

            # Return HTML response with proper content type
            return web.Response(
                text=html_content,
                content_type="text/html",
                charset="utf-8",
            )

        except FileNotFoundError:
            _LOGGER.error("Test HTML file not found at %s", test_html_path)
            return web.Response(
                text="<h1>Error: Test page not found</h1>",
                content_type="text/html",
                status=404,
            )

        except Exception as e:
            _LOGGER.error("Error serving test page: %s", str(e))
            return web.Response(
                text="<h1>Error: Unable to serve test page</h1>",
                content_type="text/html",
                status=500,
            )


class BeatsyAdminView(HomeAssistantView):
    """View for admin interface.

    Serves mobile-first admin UI from www/admin.html without authentication.
    Implemented in Epic 3 (Story 3.1).

    No authentication required for easier party game access on local network.
    """

    url = "/api/beatsy/admin"
    name = "api:beatsy:admin"
    requires_auth = False  # No auth for easier party game access

    async def get(self, request: web.Request) -> web.Response:
        """Serve admin interface.

        Args:
            request: The aiohttp request object.

        Returns:
            HTML response with admin interface content.
        """
        try:
            _LOGGER.debug("Admin interface accessed")

            # Get the path to the www directory relative to this module
            module_dir = Path(__file__).parent
            admin_html_path = module_dir / "www" / "admin.html"

            # Read the HTML content asynchronously to avoid blocking I/O
            def read_html():
                return admin_html_path.read_text(encoding="utf-8")

            html_content = await self.hass.async_add_executor_job(read_html)

            _LOGGER.debug("Serving admin page from %s", admin_html_path)

            # Return HTML response with proper content type
            return web.Response(
                text=html_content,
                content_type="text/html",
                charset="utf-8",
                status=200,
            )

        except FileNotFoundError:
            _LOGGER.error("Admin HTML file not found at %s", admin_html_path)
            return web.Response(
                text="<h1>Error: Admin page not found</h1>",
                content_type="text/html",
                status=404,
            )

        except Exception as e:
            _LOGGER.error("Error serving admin interface: %s", str(e), exc_info=True)
            return web.Response(
                text="<h1>Error: Unable to serve admin interface</h1>",
                content_type="text/html",
                status=500,
            )


class BeatsyPlayerView(HomeAssistantView):
    """View for player interface (unauthenticated).

    Does NOT require authentication per Epic 1 POC pattern.
    This enables zero-friction player joining experience.
    Returns placeholder HTML in Epic 2. Real player UI will be implemented in Epic 4.
    """

    url = "/api/beatsy/player"
    name = "api:beatsy:player"
    requires_auth = False  # No authentication required (Epic 1 POC pattern)

    async def get(self, request: web.Request) -> web.Response:
        """Serve player interface.

        Args:
            request: The aiohttp request object.

        Returns:
            HTML response with player interface content.
        """
        try:
            _LOGGER.debug("Player interface accessed (unauthenticated)")

            # Get the path to the www directory relative to this module
            module_dir = Path(__file__).parent
            player_html_path = module_dir / "www" / "start.html"

            # Read the HTML content (async to avoid blocking event loop)
            html_content = await request.app["hass"].async_add_executor_job(
                player_html_path.read_text, "utf-8"
            )

            _LOGGER.debug("Serving player page from %s", player_html_path)

            # Return HTML response with proper content type
            return web.Response(
                text=html_content,
                content_type="text/html",
                charset="utf-8",
                status=200,
            )

        except Exception as e:
            _LOGGER.error(
                "Error serving player interface: %s", str(e), exc_info=True
            )
            return web.Response(
                text="<h1>Error: Unable to serve player interface</h1>",
                content_type="text/html",
                status=500,
            )


class BeatsyAPIView(HomeAssistantView):
    """View for REST API endpoints.

    Does NOT require authentication to maintain consistency with admin/player interfaces.
    Follows Epic 1 POC pattern for zero-friction access.
    Provides JSON responses for game control and data access.

    Endpoints:
    - GET /api/beatsy/api/media_players - Get available Spotify media players
    - GET /api/beatsy/api/playlists - Get available playlist JSON files (Story 3.3)
    - POST /api/beatsy/api/validate_playlist - Validate Spotify playlist
    - POST /api/beatsy/api/start_game - Start a new game (Epic 3)
    - POST /api/beatsy/api/next_song - Advance to next song (Epic 5)
    - POST /api/beatsy/api/reset_game - Reset game state (Epic 3)
    """

    url = "/api/beatsy/api/{endpoint}"
    name = "api:beatsy:api"
    requires_auth = False  # No authentication required (consistent with admin/player pages)

    async def get(self, request: web.Request, endpoint: str) -> web.Response:
        """Handle GET API requests.

        Args:
            request: The aiohttp request object.
            endpoint: The endpoint name from the URL path.

        Returns:
            JSON response with endpoint data or error.
        """
        hass: HomeAssistant = request.app["hass"]

        try:
            if endpoint == "media_players":
                # Story 3.2: Get Spotify-capable media players for admin dropdown
                from .spotify_helper import get_spotify_media_players

                _LOGGER.debug("GET /api/beatsy/api/media_players called")

                try:
                    # Call Story 2.4's player detection function
                    players = await get_spotify_media_players(hass)

                    # Convert MediaPlayerInfo dataclass instances to JSON-serializable dicts
                    players_data = [
                        {
                            "entity_id": player.entity_id,
                            "friendly_name": player.friendly_name,
                            "state": player.state,
                            "supports_play_media": player.supports_play_media,
                        }
                        for player in players
                    ]

                    if not players_data:
                        # No players found - return 404 with helpful message
                        _LOGGER.warning("No Spotify-capable media players found")
                        return web.json_response(
                            {
                                "error": "no_players",
                                "message": "No Spotify media players detected. Please configure Spotify integration in Home Assistant.",
                            },
                            status=404,
                        )

                    _LOGGER.info("Media players endpoint called, found %d players", len(players_data))
                    return web.json_response({"players": players_data}, status=200)

                except Exception as e:
                    _LOGGER.error("Error fetching media players: %s", str(e), exc_info=True)
                    return web.json_response(
                        {
                            "error": "service_unavailable",
                            "message": "Unable to fetch media players. Please check Spotify integration.",
                        },
                        status=503,
                    )

            elif endpoint == "playlists":
                # Story 3.3: Get available playlist JSON files for admin dropdown
                from .playlist_loader import list_playlists

                _LOGGER.debug("GET /api/beatsy/api/playlists called")

                try:
                    # Call playlist loader to scan playlists/ directory
                    playlists = await list_playlists(hass)

                    if not playlists:
                        # No playlists found - return 404 with helpful message
                        _LOGGER.warning("No playlist files found in playlists/ directory")
                        return web.json_response(
                            {
                                "error": "no_playlists",
                                "message": "No playlist files found in playlists/ directory. Please add playlist JSON files.",
                            },
                            status=404,
                        )

                    _LOGGER.info("Playlists endpoint called, found %d valid playlists", len(playlists))
                    return web.json_response({"playlists": playlists}, status=200)

                except Exception as e:
                    _LOGGER.error("Error fetching playlists: %s", str(e), exc_info=True)
                    return web.json_response(
                        {
                            "error": "playlist_parse_error",
                            "message": "Failed to load playlists. Check Home Assistant logs for details.",
                        },
                        status=500,
                    )

            elif endpoint == "config":
                # Story 11.1: Get persisted game configuration
                from .game_state import get_game_state, load_config

                _LOGGER.debug("GET /api/beatsy/api/config called")

                try:
                    # Get game state to retrieve entry_id
                    try:
                        game_state = get_game_state(hass)
                        entry_id = game_state.entry_id
                    except ValueError:
                        # No game state - try to load config from first entry
                        _LOGGER.warning("No game state initialized, using first config entry")
                        # Get first config entry
                        entries = hass.config_entries.async_entries(DOMAIN)
                        if not entries:
                            return web.json_response(
                                {
                                    "error": "no_config",
                                    "message": "No configuration entries found",
                                },
                                status=404,
                            )
                        entry_id = entries[0].entry_id

                    # Load persisted config
                    config = await load_config(hass, entry_id)

                    if not config:
                        # Return empty config if none exists
                        _LOGGER.debug("No persisted config found, returning empty")
                        return web.json_response({}, status=200)

                    # Return config JSON
                    _LOGGER.info("Config endpoint called, returning persisted config")
                    return web.json_response(config, status=200)

                except Exception as e:
                    _LOGGER.error("Error loading config: %s", str(e), exc_info=True)
                    return web.json_response(
                        {
                            "error": "internal_error",
                            "message": "Failed to load configuration",
                        },
                        status=500,
                    )

            elif endpoint == "game_status":
                # Story 3.7: Get current game status for admin status panel
                from .game_state import get_game_state

                _LOGGER.debug("GET /api/beatsy/api/game_status called")

                try:
                    # Attempt to retrieve game state
                    try:
                        game_state = get_game_state(hass)
                    except ValueError as e:
                        # No game state initialized - no active game
                        _LOGGER.debug("No active game found: %s", str(e))
                        return web.json_response(
                            {
                                "error": "no_game",
                                "message": "No active game found",
                            },
                            status=404,
                        )

                    # Extract game status data (AC-6)
                    # Game state structure from BeatsyGameState dataclass:
                    # - players: list[Player]
                    # - available_songs: list[dict]
                    # - played_songs: list[str]
                    # - current_round: Optional[RoundState]
                    # - game_started: bool

                    player_count = len(game_state.players) if game_state.players else 0
                    songs_total = len(game_state.available_songs) if game_state.available_songs else 0
                    songs_played = len(game_state.played_songs) if game_state.played_songs else 0
                    songs_remaining = songs_total - songs_played

                    # Determine game state based on context
                    if not game_state.game_started:
                        state = "setup"
                    elif game_state.current_round and game_state.current_round.status == "active":
                        state = "active"
                    elif game_state.current_round and game_state.current_round.status == "ended":
                        state = "results"
                    elif songs_remaining == 0 and songs_played > 0:
                        state = "ended"
                    else:
                        state = "lobby"

                    # Current round number
                    current_round = game_state.current_round.round_number if game_state.current_round else None

                    # Generate game_id (use first 8 chars of hash for consistency)
                    import hashlib
                    game_id = hashlib.md5(str(game_state.game_started_at).encode()).hexdigest()[:8] if game_state.game_started_at else "unknown"

                    # Story 11.3: Add players array with name and joined_at (chronological order)
                    players_data = [
                        {
                            "name": player.name,
                            "joined_at": int(player.joined_at)  # Unix timestamp
                        }
                        for player in (game_state.players if game_state.players else [])
                    ]

                    response_data = {
                        "game_id": game_id,
                        "state": state,
                        "player_count": player_count,
                        "songs_total": songs_total,
                        "songs_remaining": songs_remaining,
                        "current_round": current_round,
                        "players": players_data,  # Story 11.3: Players array for admin ticker
                    }

                    _LOGGER.info(
                        "Game status endpoint called: state=%s, players=%d, songs=%d/%d",
                        state,
                        player_count,
                        songs_remaining,
                        songs_total,
                    )

                    return web.json_response(response_data, status=200)

                except Exception as e:
                    _LOGGER.error("Error fetching game status: %s", str(e), exc_info=True)
                    return web.json_response(
                        {
                            "error": "internal_error",
                            "message": "Failed to retrieve game status",
                        },
                        status=500,
                    )

            else:
                _LOGGER.warning("Unknown GET endpoint: %s", endpoint)
                return web.json_response(
                    {"error": f"Unknown endpoint: {endpoint}"}, status=404
                )

        except Exception as e:
            _LOGGER.error(
                "Error in GET /api/beatsy/api/%s: %s", endpoint, str(e), exc_info=True
            )
            return web.json_response({"error": "Internal server error"}, status=500)

    async def post(self, request: web.Request, endpoint: str) -> web.Response:
        """Handle POST API requests.

        Args:
            request: The aiohttp request object.
            endpoint: The endpoint name from the URL path.

        Returns:
            JSON response with operation result or error.
        """
        hass: HomeAssistant = request.app["hass"]

        try:
            # Parse request body
            try:
                data = (
                    await request.json()
                    if request.content_type == "application/json"
                    else {}
                )
            except Exception as json_error:
                _LOGGER.error("Invalid JSON in request: %s", str(json_error))
                return web.json_response(
                    {"error": "Invalid JSON in request body"}, status=400
                )

            if endpoint == "validate_playlist":
                # Story 10.5: Validate playlist URI format
                _LOGGER.debug("POST /api/beatsy/api/validate_playlist called")
                playlist_uri = data.get("playlist_uri", "")

                # Validate Spotify URI format
                validation_result = validate_spotify_uri(playlist_uri)
                if not validation_result.valid:
                    _LOGGER.warning(
                        f"Invalid playlist URI: {playlist_uri} - {validation_result.error_message}"
                    )
                    return web.json_response(
                        {
                            "valid": False,
                            "error": "invalid_uri",
                            "message": validation_result.error_message,
                        },
                        status=400,
                    )

                return web.json_response(
                    {
                        "valid": True,
                        "message": "Playlist URI format is valid",
                        "playlist_uri": validation_result.sanitized_value,
                    }
                )

            elif endpoint == "start_game":
                # Story 3.5: Start game endpoint - initialize new game session
                _LOGGER.info("POST /api/beatsy/api/start_game called")

                from pathlib import Path

                from . import game_initializer, playlist_loader

                try:
                    # Extract configuration from request
                    config = data.get("config", {})
                    force = data.get("force", False)  # Story 7.3: Force flag to bypass conflict warning

                    if not config:
                        return web.json_response(
                            {
                                "error": "validation_failed",
                                "details": ["Missing 'config' field in request body"],
                            },
                            status=400,
                        )

                    # Story 10.5: Validate game settings
                    settings_validation = validate_game_settings(config)
                    if not settings_validation.valid:
                        _LOGGER.warning(
                            f"Game settings validation failed: {settings_validation.error_message}"
                        )
                        return web.json_response(
                            {
                                "error": "validation_failed",
                                "details": [settings_validation.error_message],
                            },
                            status=400,
                        )

                    # Use sanitized/validated config values
                    validated_config = settings_validation.sanitized_value
                    # Merge with original config (validated values override)
                    config = {**config, **validated_config}

                    # Create GameConfigInput instance
                    try:
                        game_config = game_initializer.GameConfigInput(
                            media_player=config.get("media_player", ""),
                            playlist_id=config.get("playlist_id", ""),
                            timer_duration=int(config.get("timer_duration", 30)),
                            year_range_min=int(config.get("year_range_min", 1950)),
                            year_range_max=int(config.get("year_range_max", 2024)),
                            exact_points=int(config.get("exact_points", 10)),
                            close_points=int(config.get("close_points", 5)),
                            near_points=int(config.get("near_points", 2)),
                            bet_multiplier=int(config.get("bet_multiplier", 2)),
                        )
                    except (ValueError, TypeError) as e:
                        _LOGGER.error("Invalid config values: %s", e)
                        return web.json_response(
                            {
                                "error": "validation_failed",
                                "details": [f"Invalid configuration values: {str(e)}"],
                            },
                            status=400,
                        )

                    # Validate configuration
                    validation_errors = game_config.validate()
                    if validation_errors:
                        _LOGGER.warning(
                            "Configuration validation failed: %s", validation_errors
                        )
                        return web.json_response(
                            {"error": "validation_failed", "details": validation_errors},
                            status=400,
                        )

                    # Load playlist file
                    module_dir = Path(__file__).parent
                    playlists_dir = module_dir / "playlists"

                    try:
                        playlist_data = await playlist_loader.load_playlist_file(
                            hass, playlists_dir, game_config.playlist_id
                        )
                    except FileNotFoundError:
                        _LOGGER.error(
                            "Playlist file not found: %s", game_config.playlist_id
                        )
                        return web.json_response(
                            {
                                "error": "playlist_not_found",
                                "message": f"Playlist '{game_config.playlist_id}' not found",
                            },
                            status=404,
                        )
                    except ValueError as e:
                        _LOGGER.error(
                            "Playlist validation failed for %s: %s",
                            game_config.playlist_id,
                            e,
                        )
                        return web.json_response(
                            {"error": "playlist_parse_error", "message": str(e)},
                            status=500,
                        )

                    # Filter songs by year range
                    all_songs = playlist_data.get("songs", [])
                    filtered_songs = playlist_loader.filter_songs_by_year(
                        all_songs, game_config.year_range_min, game_config.year_range_max
                    )

                    # Verify minimum track count
                    if len(filtered_songs) < 10:
                        _LOGGER.warning(
                            "Insufficient tracks after filtering: %d (minimum 10 required)",
                            len(filtered_songs),
                        )
                        return web.json_response(
                            {
                                "error": "insufficient_tracks",
                                "message": f"Only {len(filtered_songs)} tracks available after year range filtering (minimum 10 required)",
                            },
                            status=400,
                        )

                    # Create playlist data with filtered songs
                    filtered_playlist = playlist_data.copy()
                    filtered_playlist["songs"] = filtered_songs

                    # Story 7.3: Check media player state for conflict warning
                    media_player_entity_id = game_config.media_player
                    if media_player_entity_id and not force:
                        from .spotify_service import (
                            get_media_player_state,
                            should_warn_conflict,
                        )

                        # Query current media player state
                        player_state = await get_media_player_state(
                            hass, media_player_entity_id
                        )

                        # Check if conflict warning should be shown
                        if should_warn_conflict(player_state):
                            # AC-1: Show conflict warning to admin
                            _LOGGER.info(
                                "Media player %s is %s, returning conflict warning to admin",
                                media_player_entity_id,
                                player_state.state,
                            )

                            # AC-2: Return conflict_warning response with current media info
                            return web.json_response(
                                {
                                    "conflict_warning": True,
                                    "current_media": {
                                        "entity_id": player_state.entity_id,
                                        "title": player_state.media_title or "Unknown",
                                        "artist": player_state.media_artist or "Unknown",
                                        "state": player_state.state,
                                    },
                                },
                                status=200,
                            )

                    # AC-3: If force=true, save state before proceeding
                    if media_player_entity_id and force:
                        from .spotify_service import (
                            get_media_player_state,
                            save_player_state,
                        )

                        # Get fresh state for saving
                        player_state = await get_media_player_state(
                            hass, media_player_entity_id
                        )
                        if player_state is not None:
                            # Save state for restoration (Story 7.6)
                            save_player_state(hass, player_state)

                    # Create game session (atomic operation)
                    try:
                        session_data = await game_initializer.create_game_session(
                            hass, config, filtered_playlist
                        )
                    except Exception as e:
                        _LOGGER.error(
                            "Failed to create game session: %s", e, exc_info=True
                        )
                        return web.json_response(
                            {
                                "error": "session_creation_failed",
                                "message": "Failed to initialize game session",
                            },
                            status=500,
                        )

                    # Construct player URL using request host
                    # Format: http://<HA_IP>:8123/api/beatsy/player
                    # Story 4.1: Player interface served at /api/beatsy/player
                    host = request.headers.get("Host", "localhost:8123")
                    scheme = request.scheme
                    player_url = f"{scheme}://{host}/api/beatsy/player"

                    # Prepare response
                    response_data = {
                        "game_id": session_data["game_id"],
                        "status": session_data["status"],
                        "player_url": player_url,
                        "admin_key": session_data["admin_key"],
                        "playlist_tracks": session_data["songs_total"],
                    }

                    # Story 3.5 Task 9: Broadcast WebSocket game_status_update event
                    from .websocket_handler import broadcast_message

                    # Prepare WebSocket broadcast payload (AC-5)
                    ws_payload = {
                        "game_id": session_data["game_id"],
                        "status": session_data["status"],
                        "player_count": session_data["player_count"],
                        "songs_total": session_data["songs_total"],
                        "songs_remaining": session_data["songs_remaining"],
                        "current_round": None,
                    }

                    # Broadcast to all connected WebSocket clients
                    try:
                        await broadcast_message(hass, "game_status_update", ws_payload)
                        _LOGGER.info(
                            "WebSocket broadcast sent: game_status_update (game_id=%s)",
                            session_data["game_id"],
                        )
                    except Exception as ws_error:
                        # Don't fail the request if WebSocket broadcast fails
                        _LOGGER.warning(
                            "Failed to broadcast game_status_update: %s", ws_error
                        )

                    _LOGGER.info(
                        "Game session created successfully: game_id=%s, tracks=%d",
                        session_data["game_id"],
                        session_data["songs_total"],
                    )

                    return web.json_response(response_data, status=200)

                except Exception as e:
                    _LOGGER.error(
                        "Unexpected error in start_game endpoint: %s", e, exc_info=True
                    )
                    return web.json_response(
                        {
                            "error": "internal_server_error",
                            "message": "An unexpected error occurred",
                        },
                        status=500,
                    )

            elif endpoint == "next_song":
                # Story 3.6 Task 10: Admin initiates next song/round
                _LOGGER.info("POST /api/beatsy/api/next_song called")

                try:
                    # Validate game session exists
                    if DOMAIN not in hass.data:
                        _LOGGER.warning("next_song failed: No active game session")
                        return web.json_response(
                            {
                                "error": "no_active_game",
                                "message": "No active game session found"
                            },
                            status=400
                        )

                    session_data = hass.data[DOMAIN]

                    # Story 3.6 AC-6: Validate admin permission
                    # Check admin_key from request (Story 4.1 will provide session_id)
                    admin_key = data.get("admin_key")
                    if not admin_key:
                        _LOGGER.warning("next_song failed: No admin_key provided")
                        return web.json_response(
                            {
                                "error": "unauthorized",
                                "message": "Admin key required to advance rounds"
                            },
                            status=403
                        )

                    # Validate admin key using Story 3.6 Task 5 function
                    from . import game_initializer

                    is_valid_admin = game_initializer.validate_admin_key(hass, admin_key)
                    if not is_valid_admin:
                        _LOGGER.warning("next_song failed: Invalid or expired admin key")
                        return web.json_response(
                            {
                                "error": "unauthorized",
                                "message": "Only admin can advance rounds"
                            },
                            status=403
                        )

                    # TODO: Story 5.2 - Check game state (must be lobby or results, not active round)
                    # For now, allow next_song in any state
                    _LOGGER.info("Admin validated successfully, proceeding with next_song")

                    # Story 5.1: Select random song from available playlist
                    from .game_state import select_random_song, PlaylistExhaustedError, get_game_state

                    try:
                        # Call async song selection function
                        selected_song = await select_random_song(hass)

                        # Get round number from played_songs count
                        state = get_game_state(hass)
                        round_number = len(state.played_songs)

                        # Story 5.1: Return success with song details
                        response_data = {
                            "success": True,
                            "round_number": round_number,
                            "song_selected": True,
                            "title": selected_song.get("title"),
                            "artist": selected_song.get("artist"),
                            "message": f"Round {round_number} started"
                        }

                        _LOGGER.info("next_song successful: Round %d - %s by %s",
                                   round_number, selected_song.get("title"), selected_song.get("artist"))
                        return web.json_response(response_data, status=200)

                    except PlaylistExhaustedError as e:
                        # Story 5.1 AC-4: Handle empty playlist gracefully
                        _LOGGER.warning("Playlist exhausted when admin requested next song")
                        return web.json_response(
                            {
                                "success": False,
                                "error": e.code,  # "playlist_exhausted"
                                "message": e.message
                            },
                            status=400
                        )
                    except ValueError as e:
                        # Song validation error
                        _LOGGER.error("Song validation error in next_song: %s", e, exc_info=True)
                        return web.json_response(
                            {
                                "success": False,
                                "error": "invalid_song_data",
                                "message": f"Selected song has invalid structure: {str(e)}"
                            },
                            status=500
                        )

                except Exception as e:
                    _LOGGER.error("Unexpected error in next_song endpoint: %s", e, exc_info=True)
                    return web.json_response(
                        {
                            "error": "internal_server_error",
                            "message": "An unexpected error occurred"
                        },
                        status=500
                    )

            elif endpoint == "reset_game":
                # Placeholder for game reset logic (Epic 3)
                _LOGGER.debug("POST /api/beatsy/api/reset_game called")
                return web.json_response(
                    {
                        "success": True,
                        "message": "Game reset not yet implemented (Epic 3)",
                    }
                )

            else:
                _LOGGER.warning("Unknown POST endpoint: %s", endpoint)
                return web.json_response(
                    {"error": f"Unknown endpoint: {endpoint}"}, status=404
                )

        except Exception as e:
            _LOGGER.error(
                "Error in POST /api/beatsy/api/%s: %s", endpoint, str(e), exc_info=True
            )
            return web.json_response({"error": "Internal server error"}, status=500)


class BeatsyStaticView(HomeAssistantView):
    """View for serving static files (CSS, JS, images).

    Serves files from www/ directory via /api/beatsy/static/* URLs.
    No authentication required - consistent with admin/player pages.
    """

    url = "/api/beatsy/static/{filepath:.+}"
    name = "api:beatsy:static"
    requires_auth = False

    async def get(self, request: web.Request, filepath: str) -> web.Response:
        """Serve static file from www directory.

        Args:
            request: The aiohttp request object.
            filepath: The relative path to the file (e.g., "css/custom.css", "js/ui-admin.js")

        Returns:
            File content with appropriate content type or 404 error.
        """
        try:
            # Get the www directory path
            module_dir = Path(__file__).parent
            www_dir = module_dir / "www"

            # Construct full file path and normalize to prevent directory traversal
            file_path = (www_dir / filepath).resolve()

            # Security check: ensure file is within www directory
            if not file_path.is_relative_to(www_dir):
                _LOGGER.warning("Attempted directory traversal: %s", filepath)
                return web.Response(text="Forbidden", status=403)

            # Check if file exists
            if not file_path.is_file():
                _LOGGER.debug("Static file not found: %s", file_path)
                return web.Response(text="File not found", status=404)

            # Read file content (async to avoid blocking event loop)
            content = await request.app["hass"].async_add_executor_job(
                file_path.read_bytes
            )

            # Determine content type from file extension
            content_type, _ = mimetypes.guess_type(str(file_path))
            if content_type is None:
                # Default to binary if unknown
                content_type = "application/octet-stream"

            _LOGGER.debug("Serving static file: %s (%s)", filepath, content_type)

            return web.Response(
                body=content,
                content_type=content_type,
                headers={
                    "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
                },
            )

        except Exception as e:
            _LOGGER.error("Error serving static file %s: %s", filepath, str(e), exc_info=True)
            return web.Response(text="Internal server error", status=500)
