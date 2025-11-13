"""Integration tests for HTTP route registration (Story 2.5)."""
from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch
import json

import pytest

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

# Import the module under test
import sys
from pathlib import Path

# Add the custom_components directory to the path
sys.path.insert(
    0, str(Path(__file__).parent.parent / "home-assistant-config" / "custom_components")
)

from beatsy import async_setup_entry, DOMAIN
from beatsy.http_view import BeatsyAdminView, BeatsyPlayerView, BeatsyAPIView


@pytest.fixture
def mock_hass():
    """Create a mock HomeAssistant instance."""
    hass = Mock(spec=HomeAssistant)
    hass.data = {}
    hass.config_entries = Mock()
    hass.http = Mock()
    hass.services = Mock()

    # Mock async methods
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
    hass.config_entries.async_entries = Mock(return_value=[])
    hass.http.register_view = Mock()
    hass.services.async_register = Mock()

    return hass


@pytest.fixture
def mock_config_entry():
    """Create a mock ConfigEntry."""
    entry = Mock(spec=ConfigEntry)
    entry.entry_id = "test_entry_id"
    entry.data = {}
    return entry


class TestHTTPRouteRegistration:
    """Integration tests for HTTP route registration (AC-1, AC-2, AC-3)."""

    @pytest.mark.asyncio
    async def test_admin_view_registered_on_setup(self, mock_hass, mock_config_entry):
        """Test that admin view is registered during component setup."""
        # Mock get_spotify_media_players to avoid actual API calls
        with patch("beatsy.get_spotify_media_players", return_value=AsyncMock(return_value=[])):
            result = await async_setup_entry(mock_hass, mock_config_entry)

        assert result is True

        # Verify hass.http.register_view was called
        assert mock_hass.http.register_view.called

        # Check that views were registered
        calls = mock_hass.http.register_view.call_args_list
        view_types = [type(call[0][0]) for call in calls]

        # Verify all three new views were registered
        assert BeatsyAdminView in view_types
        assert BeatsyPlayerView in view_types
        assert BeatsyAPIView in view_types

    @pytest.mark.asyncio
    async def test_player_view_registered_on_setup(self, mock_hass, mock_config_entry):
        """Test that player view is registered during component setup."""
        with patch("beatsy.get_spotify_media_players", return_value=AsyncMock(return_value=[])):
            result = await async_setup_entry(mock_hass, mock_config_entry)

        assert result is True

        # Find the PlayerView call
        calls = mock_hass.http.register_view.call_args_list
        view_types = [type(call[0][0]) for call in calls]

        assert BeatsyPlayerView in view_types

    @pytest.mark.asyncio
    async def test_api_view_registered_on_setup(self, mock_hass, mock_config_entry):
        """Test that API view is registered during component setup."""
        with patch("beatsy.get_spotify_media_players", return_value=AsyncMock(return_value=[])):
            result = await async_setup_entry(mock_hass, mock_config_entry)

        assert result is True

        # Find the APIView call
        calls = mock_hass.http.register_view.call_args_list
        view_types = [type(call[0][0]) for call in calls]

        assert BeatsyAPIView in view_types

    @pytest.mark.asyncio
    async def test_all_routes_registered_together(self, mock_hass, mock_config_entry):
        """Test that all HTTP routes are registered in a single setup."""
        with patch("beatsy.get_spotify_media_players", return_value=AsyncMock(return_value=[])):
            result = await async_setup_entry(mock_hass, mock_config_entry)

        assert result is True

        # Verify multiple views were registered
        assert mock_hass.http.register_view.call_count >= 3

    @pytest.mark.asyncio
    async def test_registration_failure_returns_false(self, mock_hass, mock_config_entry):
        """Test that registration failure returns False (AC-5)."""
        # Mock register_view to raise an exception
        mock_hass.http.register_view.side_effect = Exception("Registration failed")

        with patch("beatsy.get_spotify_media_players", return_value=AsyncMock(return_value=[])):
            result = await async_setup_entry(mock_hass, mock_config_entry)

        # Setup should return False on registration failure
        assert result is False


class TestViewAuthentication:
    """Tests for view authentication configuration."""

    def test_admin_view_authentication(self):
        """Test admin view requires authentication."""
        view = BeatsyAdminView()
        assert view.requires_auth is True

    def test_player_view_no_authentication(self):
        """Test player view does NOT require authentication (Epic 1 POC pattern)."""
        view = BeatsyPlayerView()
        assert view.requires_auth is False

    def test_api_view_authentication(self):
        """Test API view requires authentication."""
        view = BeatsyAPIView()
        assert view.requires_auth is True


class TestViewURLs:
    """Tests for view URL configuration."""

    def test_admin_view_url(self):
        """Test admin view has correct URL."""
        view = BeatsyAdminView()
        assert view.url == "/api/beatsy/admin"
        assert view.name == "api:beatsy:admin"

    def test_player_view_url(self):
        """Test player view has correct URL."""
        view = BeatsyPlayerView()
        assert view.url == "/api/beatsy/player"
        assert view.name == "api:beatsy:player"

    def test_api_view_url(self):
        """Test API view has correct URL pattern."""
        view = BeatsyAPIView()
        assert view.url == "/api/beatsy/api/{endpoint}"
        assert view.name == "api:beatsy:api"


class TestEndpointAvailability:
    """Tests for API endpoint availability (AC-3)."""

    @pytest.mark.asyncio
    async def test_media_players_endpoint_available(self):
        """Test media_players endpoint is handled."""
        view = BeatsyAPIView()
        request = Mock()
        request.app = {"hass": Mock()}

        response = await view.get(request, "media_players")

        # Should return a valid response (not 404)
        assert response.status == 200

    @pytest.mark.asyncio
    async def test_validate_playlist_endpoint_available(self):
        """Test validate_playlist endpoint is handled."""
        view = BeatsyAPIView()
        request = Mock()
        request.app = {"hass": Mock()}
        request.content_type = "application/json"

        async def mock_json():
            return {"playlist_uri": "spotify:playlist:123"}

        request.json = mock_json

        response = await view.post(request, "validate_playlist")

        # Should return a valid response (not 404)
        assert response.status == 200

    @pytest.mark.asyncio
    async def test_start_game_endpoint_available(self):
        """Test start_game endpoint is handled."""
        view = BeatsyAPIView()
        request = Mock()
        request.app = {"hass": Mock()}
        request.content_type = "application/json"

        async def mock_json():
            return {}

        request.json = mock_json

        response = await view.post(request, "start_game")
        assert response.status == 200

    @pytest.mark.asyncio
    async def test_next_song_endpoint_available(self):
        """Test next_song endpoint is handled."""
        view = BeatsyAPIView()
        request = Mock()
        request.app = {"hass": Mock()}
        request.content_type = "application/json"

        async def mock_json():
            return {}

        request.json = mock_json

        response = await view.post(request, "next_song")
        assert response.status == 200

    @pytest.mark.asyncio
    async def test_reset_game_endpoint_available(self):
        """Test reset_game endpoint is handled."""
        view = BeatsyAPIView()
        request = Mock()
        request.app = {"hass": Mock()}
        request.content_type = "application/json"

        async def mock_json():
            return {}

        request.json = mock_json

        response = await view.post(request, "reset_game")
        assert response.status == 200


class TestErrorResponses:
    """Tests for error response handling (AC-5)."""

    @pytest.mark.asyncio
    async def test_unknown_endpoint_returns_404(self):
        """Test unknown endpoint returns 404."""
        view = BeatsyAPIView()
        request = Mock()
        request.app = {"hass": Mock()}

        response = await view.get(request, "nonexistent_endpoint")

        assert response.status == 404
        body = json.loads(response.body)
        assert "error" in body

    @pytest.mark.asyncio
    async def test_invalid_json_returns_400(self):
        """Test invalid JSON returns 400."""
        view = BeatsyAPIView()
        request = Mock()
        request.app = {"hass": Mock()}
        request.content_type = "application/json"

        async def mock_json():
            raise ValueError("Invalid JSON")

        request.json = mock_json

        response = await view.post(request, "start_game")

        assert response.status == 400
        body = json.loads(response.body)
        assert "error" in body

    @pytest.mark.asyncio
    async def test_exception_returns_500(self):
        """Test internal exception returns 500."""
        view = BeatsyAPIView()
        request = Mock()
        request.app = {"hass": Mock()}
        request.content_type = "application/json"

        async def mock_json():
            return {}

        request.json = mock_json

        # Mock to raise an exception during processing
        with patch("beatsy.http_view.web.json_response", side_effect=Exception("Internal error")):
            response = await view.post(request, "start_game")

            assert response.status == 500
            body = json.loads(response.body)
            assert "error" in body
            assert "Internal server error" in body["error"]
