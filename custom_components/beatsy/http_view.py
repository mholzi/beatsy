"""HTTP view handler for Beatsy component.

This module provides HTTP routes for:
- Admin interface (/api/beatsy/admin) - Authenticated
- Player interface (/api/beatsy/player) - Unauthenticated (Epic 1 POC)
- REST API endpoints (/api/beatsy/api/*) - Authenticated

Authentication:
- Admin and API routes require HA access token
- Player route uses unauthenticated pattern from Epic 1 POC
- CORS handled automatically by HA's HTTP component

Epic 2 Implementation:
- Routes return placeholder content
- Real UIs implemented in Epic 3 (Admin) and Epic 4 (Player)
- API endpoints have placeholders for future logic
"""
import logging
from pathlib import Path

from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant

from .const import DOMAIN

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

            # Read the HTML content
            html_content = test_html_path.read_text(encoding="utf-8")

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
    """

    url = "/beatsy/admin"
    name = "beatsy:admin"
    requires_auth = False  # No authentication required (like player interface)

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

            # Read the HTML content
            html_content = admin_html_path.read_text(encoding="utf-8")

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

            # Placeholder HTML for Epic 2 (real UI in Epic 4)
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Beatsy Player</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                        max-width: 800px;
                        margin: 50px auto;
                        padding: 20px;
                        background: #f5f5f5;
                    }
                    .container {
                        background: white;
                        padding: 40px;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }
                    h1 { color: #1DB954; margin-top: 0; }
                    .status {
                        background: #d4edda;
                        color: #155724;
                        padding: 12px;
                        border-radius: 4px;
                        margin: 20px 0;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Beatsy Player Interface</h1>
                    <p>Welcome to Beatsy! Get ready to guess that song.</p>
                    <div class="status">
                        <strong>Unauthenticated access: SUCCESS ✅</strong><br>
                        <small>Player UI will be implemented in Epic 4</small>
                    </div>
                    <p><strong>Authentication:</strong> None required (zero-friction access)</p>
                    <p><strong>Story:</strong> 2.5 - HTTP Route Registration</p>
                </div>
            </body>
            </html>
            """

            return web.Response(
                text=html,
                content_type="text/html",
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
                # Placeholder for future Spotify integration
                _LOGGER.debug("POST /api/beatsy/api/validate_playlist called")
                playlist_uri = data.get("playlist_uri")
                return web.json_response(
                    {
                        "valid": True,
                        "message": "Playlist validation not yet implemented",
                        "playlist_uri": playlist_uri,
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

                    if not config:
                        return web.json_response(
                            {
                                "error": "validation_failed",
                                "details": ["Missing 'config' field in request body"],
                            },
                            status=400,
                        )

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
                        playlist_data = playlist_loader.load_playlist_file(
                            playlists_dir, game_config.playlist_id
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

                    # Create game session (atomic operation)
                    try:
                        session_data = game_initializer.create_game_session(
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
                    # Format: http://<HA_IP>:8123/local/beatsy/start.html?game_id=<uuid>
                    host = request.headers.get("Host", "localhost:8123")
                    scheme = request.scheme
                    player_url = (
                        f"{scheme}://{host}/local/beatsy/start.html"
                        f"?game_id={session_data['game_id']}"
                    )

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
                # Placeholder for next song logic (Epic 5)
                _LOGGER.debug("POST /api/beatsy/api/next_song called")
                return web.json_response(
                    {
                        "success": True,
                        "message": "Next song not yet implemented (Epic 5)",
                    }
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
