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

    Requires Home Assistant authentication. Returns placeholder HTML in Epic 2.
    Real admin UI will be implemented in Epic 3.
    """

    url = "/api/beatsy/admin"
    name = "api:beatsy:admin"
    requires_auth = True  # HA authentication required

    async def get(self, request: web.Request) -> web.Response:
        """Serve admin interface.

        Args:
            request: The aiohttp request object.

        Returns:
            HTML response with admin interface content.
        """
        try:
            _LOGGER.debug("Admin interface accessed")

            # Placeholder HTML for Epic 2 (real UI in Epic 3)
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Beatsy Admin</title>
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
                    <h1>Beatsy Admin Interface</h1>
                    <p>Welcome to the Beatsy administration panel.</p>
                    <div class="status">
                        <strong>Route registration: SUCCESS ✅</strong><br>
                        <small>Admin UI will be implemented in Epic 3</small>
                    </div>
                    <p><strong>Authentication:</strong> Verified (HA token required)</p>
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

    Requires Home Assistant authentication for all API endpoints.
    Provides JSON responses for game control and data access.

    Endpoints:
    - GET /api/beatsy/api/media_players - Get available Spotify media players
    - POST /api/beatsy/api/validate_playlist - Validate Spotify playlist
    - POST /api/beatsy/api/start_game - Start a new game (Epic 3)
    - POST /api/beatsy/api/next_song - Advance to next song (Epic 5)
    - POST /api/beatsy/api/reset_game - Reset game state (Epic 3)
    """

    url = "/api/beatsy/api/{endpoint}"
    name = "api:beatsy:api"
    requires_auth = True  # API endpoints require authentication

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
                # Import spotify_helper from Story 2.4
                # Future: get_spotify_media_players will be implemented
                # For now, return placeholder response

                # Placeholder for Story 2.4 integration
                _LOGGER.debug("GET /api/beatsy/api/media_players called")
                return web.json_response(
                    {
                        "players": [],
                        "message": "Spotify helper not yet fully integrated (Story 2.4)",
                    }
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
                # Placeholder for game start logic (Epic 3)
                _LOGGER.debug("POST /api/beatsy/api/start_game called")
                return web.json_response(
                    {
                        "success": True,
                        "message": "Game start not yet implemented (Epic 3)",
                        "config": data,
                    }
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
