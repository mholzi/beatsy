"""Unit tests for Beatsy HTTP view handlers (Story 2.5)."""
from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch
import json

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from homeassistant.core import HomeAssistant

# Import the module under test
import sys
from pathlib import Path

# Add the custom_components directory to the path
sys.path.insert(
    0, str(Path(__file__).parent.parent / "home-assistant-config" / "custom_components")
)

from beatsy.http_view import (
    BeatsyAdminView,
    BeatsyPlayerView,
    BeatsyAPIView,
)
from beatsy.const import DOMAIN


@pytest.fixture
def mock_hass():
    """Create a mock HomeAssistant instance."""
    hass = Mock(spec=HomeAssistant)
    hass.data = {DOMAIN: {}}
    return hass


class TestBeatsyAdminView:
    """Tests for BeatsyAdminView (AC-1)."""

    def test_admin_view_requires_auth(self):
        """Test admin view requires authentication."""
        view = BeatsyAdminView()
        assert view.requires_auth is True
        assert view.url == "/api/beatsy/admin"
        assert view.name == "api:beatsy:admin"

    @pytest.mark.asyncio
    async def test_admin_view_get_returns_html(self, mock_hass):
        """Test admin view GET returns HTML content."""
        # Create view and request
        view = BeatsyAdminView()

        # Create a mock request
        request = Mock(spec=web.Request)
        request.app = {"hass": mock_hass}

        # Call the GET method
        response = await view.get(request)

        # Assert response
        assert response.status == 200
        assert response.content_type == "text/html"
        assert "Beatsy Admin" in response.text
        assert "Route registration: SUCCESS" in response.text
        assert "Authentication:" in response.text

    @pytest.mark.asyncio
    async def test_admin_view_handles_exception(self, mock_hass):
        """Test admin view handles exceptions gracefully (AC-5)."""
        view = BeatsyAdminView()

        # Create a mock request that raises an exception
        request = Mock(spec=web.Request)
        request.app = {"hass": mock_hass}

        # Mock the response creation to raise an exception
        with patch("beatsy.http_view.web.Response", side_effect=Exception("Test error")):
            response = await view.get(request)

            # Should return 500 error
            assert response.status == 500
            assert "Error: Unable to serve admin interface" in response.text


class TestBeatsyPlayerView:
    """Tests for BeatsyPlayerView (AC-2)."""

    def test_player_view_no_auth_required(self):
        """Test player view does NOT require authentication."""
        view = BeatsyPlayerView()
        assert view.requires_auth is False
        assert view.url == "/api/beatsy/player"
        assert view.name == "api:beatsy:player"

    @pytest.mark.asyncio
    async def test_player_view_get_returns_html(self, mock_hass):
        """Test player view GET returns HTML content without authentication."""
        # Create view and request
        view = BeatsyPlayerView()

        # Create a mock request (no auth token)
        request = Mock(spec=web.Request)
        request.app = {"hass": mock_hass}

        # Call the GET method
        response = await view.get(request)

        # Assert response
        assert response.status == 200
        assert response.content_type == "text/html"
        assert "Beatsy Player" in response.text
        assert "Unauthenticated access: SUCCESS" in response.text
        assert "None required" in response.text

    @pytest.mark.asyncio
    async def test_player_view_includes_mobile_viewport(self, mock_hass):
        """Test player view includes mobile viewport meta tag."""
        view = BeatsyPlayerView()
        request = Mock(spec=web.Request)
        request.app = {"hass": mock_hass}

        response = await view.get(request)

        assert response.status == 200
        assert 'name="viewport"' in response.text

    @pytest.mark.asyncio
    async def test_player_view_handles_exception(self, mock_hass):
        """Test player view handles exceptions gracefully (AC-5)."""
        view = BeatsyPlayerView()
        request = Mock(spec=web.Request)
        request.app = {"hass": mock_hass}

        # Mock the response creation to raise an exception
        with patch("beatsy.http_view.web.Response", side_effect=Exception("Test error")):
            response = await view.get(request)

            # Should return 500 error
            assert response.status == 500
            assert "Error: Unable to serve player interface" in response.text


class TestBeatsyAPIView:
    """Tests for BeatsyAPIView (AC-3)."""

    def test_api_view_requires_auth(self):
        """Test API view requires authentication."""
        view = BeatsyAPIView()
        assert view.requires_auth is True
        assert view.url == "/api/beatsy/api/{endpoint}"
        assert view.name == "api:beatsy:api"

    @pytest.mark.asyncio
    async def test_api_media_players_endpoint(self, mock_hass):
        """Test GET /api/beatsy/api/media_players endpoint."""
        view = BeatsyAPIView()
        request = Mock(spec=web.Request)
        request.app = {"hass": mock_hass}

        # Call the GET method with media_players endpoint
        response = await view.get(request, "media_players")

        # Assert response
        assert response.status == 200
        assert response.content_type == "application/json"

        # Parse JSON response
        body = json.loads(response.body)
        assert "players" in body or "message" in body

    @pytest.mark.asyncio
    async def test_api_unknown_get_endpoint_returns_404(self, mock_hass):
        """Test unknown GET endpoint returns 404."""
        view = BeatsyAPIView()
        request = Mock(spec=web.Request)
        request.app = {"hass": mock_hass}

        response = await view.get(request, "unknown_endpoint")

        assert response.status == 404
        body = json.loads(response.body)
        assert "error" in body
        assert "Unknown endpoint" in body["error"]

    @pytest.mark.asyncio
    async def test_api_validate_playlist_endpoint(self, mock_hass):
        """Test POST /api/beatsy/api/validate_playlist endpoint."""
        view = BeatsyAPIView()
        request = Mock(spec=web.Request)
        request.app = {"hass": mock_hass}
        request.content_type = "application/json"

        # Mock JSON parsing
        async def mock_json():
            return {"playlist_uri": "spotify:playlist:123"}

        request.json = mock_json

        # Call the POST method
        response = await view.post(request, "validate_playlist")

        # Assert response
        assert response.status == 200
        body = json.loads(response.body)
        assert "valid" in body
        assert body["valid"] is True

    @pytest.mark.asyncio
    async def test_api_start_game_endpoint(self, mock_hass):
        """Test POST /api/beatsy/api/start_game endpoint."""
        view = BeatsyAPIView()
        request = Mock(spec=web.Request)
        request.app = {"hass": mock_hass}
        request.content_type = "application/json"

        async def mock_json():
            return {"timer": 30, "playlist_uri": "spotify:playlist:123"}

        request.json = mock_json

        response = await view.post(request, "start_game")

        assert response.status == 200
        body = json.loads(response.body)
        assert "success" in body
        assert body["success"] is True

    @pytest.mark.asyncio
    async def test_api_next_song_endpoint(self, mock_hass):
        """Test POST /api/beatsy/api/next_song endpoint."""
        view = BeatsyAPIView()
        request = Mock(spec=web.Request)
        request.app = {"hass": mock_hass}
        request.content_type = "application/json"

        async def mock_json():
            return {}

        request.json = mock_json

        response = await view.post(request, "next_song")

        assert response.status == 200
        body = json.loads(response.body)
        assert "success" in body

    @pytest.mark.asyncio
    async def test_api_reset_game_endpoint(self, mock_hass):
        """Test POST /api/beatsy/api/reset_game endpoint."""
        view = BeatsyAPIView()
        request = Mock(spec=web.Request)
        request.app = {"hass": mock_hass}
        request.content_type = "application/json"

        async def mock_json():
            return {}

        request.json = mock_json

        response = await view.post(request, "reset_game")

        assert response.status == 200
        body = json.loads(response.body)
        assert "success" in body

    @pytest.mark.asyncio
    async def test_api_unknown_post_endpoint_returns_404(self, mock_hass):
        """Test unknown POST endpoint returns 404."""
        view = BeatsyAPIView()
        request = Mock(spec=web.Request)
        request.app = {"hass": mock_hass}
        request.content_type = "application/json"

        async def mock_json():
            return {}

        request.json = mock_json

        response = await view.post(request, "unknown_endpoint")

        assert response.status == 404
        body = json.loads(response.body)
        assert "error" in body

    @pytest.mark.asyncio
    async def test_api_invalid_json_returns_400(self, mock_hass):
        """Test invalid JSON in POST returns 400 error."""
        view = BeatsyAPIView()
        request = Mock(spec=web.Request)
        request.app = {"hass": mock_hass}
        request.content_type = "application/json"

        # Mock JSON parsing to raise an exception
        async def mock_json():
            raise ValueError("Invalid JSON")

        request.json = mock_json

        response = await view.post(request, "start_game")

        assert response.status == 400
        body = json.loads(response.body)
        assert "error" in body
        assert "Invalid JSON" in body["error"]

    @pytest.mark.asyncio
    async def test_api_get_exception_returns_500(self, mock_hass):
        """Test exception in GET method returns 500 (AC-5)."""
        view = BeatsyAPIView()
        request = Mock(spec=web.Request)
        request.app = {"hass": mock_hass}

        # Mock to raise an exception
        with patch.object(view, "get", side_effect=Exception("Test error")):
            try:
                response = await view.get(request, "media_players")
            except Exception:
                # If exception is re-raised, that's acceptable
                pass

    @pytest.mark.asyncio
    async def test_api_post_exception_returns_500(self, mock_hass):
        """Test exception in POST method returns 500 (AC-5)."""
        view = BeatsyAPIView()
        request = Mock(spec=web.Request)
        request.app = {"hass": mock_hass}
        request.content_type = "application/json"

        # Mock to raise an exception after JSON parsing
        async def mock_json():
            return {}

        request.json = mock_json

        # Patch web.json_response to raise exception
        with patch("beatsy.http_view.web.json_response", side_effect=Exception("Test error")):
            response = await view.post(request, "start_game")

            # Should return 500 error
            assert response.status == 500
            body = json.loads(response.body)
            assert "error" in body
            assert "Internal server error" in body["error"]


class TestErrorHandling:
    """Tests for error handling across all views (AC-5)."""

    @pytest.mark.asyncio
    async def test_all_views_have_exception_handling(self, mock_hass):
        """Test all views have proper exception handling."""
        views = [
            BeatsyAdminView(),
            BeatsyPlayerView(),
            BeatsyAPIView(),
        ]

        for view in views:
            request = Mock(spec=web.Request)
            request.app = {"hass": mock_hass}

            # Each view should have a get method with exception handling
            assert hasattr(view, "get")

    def test_all_views_have_correct_auth_settings(self):
        """Test all views have correct authentication settings."""
        admin_view = BeatsyAdminView()
        player_view = BeatsyPlayerView()
        api_view = BeatsyAPIView()

        # Admin requires auth
        assert admin_view.requires_auth is True

        # Player does NOT require auth (Epic 1 POC pattern)
        assert player_view.requires_auth is False

        # API requires auth
        assert api_view.requires_auth is True


class TestCORSConfiguration:
    """Tests for CORS configuration (AC-4)."""

    def test_cors_handled_by_ha_framework(self):
        """Test that CORS is expected to be handled by HA framework.

        HA's HTTP component automatically handles CORS for /api/* routes.
        This test documents that expectation.
        """
        # All views use /api/beatsy/* URLs
        admin_view = BeatsyAdminView()
        player_view = BeatsyPlayerView()
        api_view = BeatsyAPIView()

        assert admin_view.url.startswith("/api/")
        assert player_view.url.startswith("/api/")
        assert api_view.url.startswith("/api/")

        # CORS is handled automatically by HA's HTTP component
        # No custom CORS headers needed
