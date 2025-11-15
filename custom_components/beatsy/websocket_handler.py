"""WebSocket handler for Beatsy component.

Provides unauthenticated WebSocket endpoint for real-time game communication
between server and player clients.

This module implements the generic WebSocket event bus (Epic 6, Story 6.1)
for pub/sub messaging using 2025 asyncio best practices.
"""
import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from aiohttp import web, WSMsgType
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class BeatsyWebSocketView(HomeAssistantView):
    """Unauthenticated WebSocket endpoint for player connections.

    Provides bidirectional real-time communication for game events, player
    actions, and state synchronization without requiring HA authentication.
    """

    url = "/api/beatsy/ws"
    name = "api:beatsy:websocket"
    requires_auth = False

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the WebSocket view.

        Args:
            hass: The Home Assistant instance.
        """
        self.hass = hass

    async def get(self, request: web.Request) -> web.WebSocketResponse:
        """Handle WebSocket connection upgrade.

        Args:
            request: The aiohttp request object.

        Returns:
            WebSocket response handler.
        """
        # Story 6.2, AC-5: Configure heartbeat/ping-pong (20-30 sec interval)
        # Using 25 seconds as middle ground for 2025 best practice
        ws = web.WebSocketResponse(
            heartbeat=25.0,  # Send PING every 25 seconds
            timeout=20.0     # Wait 20 seconds for PONG response
        )
        await ws.prepare(request)

        # Generate unique connection ID
        conn_id = str(uuid.uuid4())

        # Store connection in registry using add_connection()
        add_connection(self.hass, conn_id, ws, player_name=None)

        _LOGGER.info("WebSocket client connected: %s", conn_id)

        try:
            # Send connection confirmation
            await ws.send_json(
                {
                    "type": "connected",
                    "data": {"connection_id": conn_id},
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

            # Message receive loop
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        _LOGGER.debug("Received from %s: %s", conn_id, data)

                        # Validate message format (support both "action" and "type" fields)
                        if not isinstance(data, dict):
                            _LOGGER.warning("Invalid message format from %s: not a dict", conn_id)
                            await ws.send_json(
                                {
                                    "type": "error",
                                    "data": {
                                        "message": "Invalid message format: must be JSON object"
                                    },
                                    "timestamp": datetime.now(timezone.utc).isoformat(),
                                }
                            )
                            continue

                        # Support both "action" (legacy) and "type" (Story 4.1) fields
                        if "type" not in data and "action" not in data:
                            _LOGGER.warning(
                                "Invalid message format from %s: missing 'type' or 'action' field",
                                conn_id,
                            )
                            await ws.send_json(
                                {
                                    "type": "error",
                                    "data": {
                                        "message": "Invalid message format: 'type' or 'action' field required"
                                    },
                                    "timestamp": datetime.now(timezone.utc).isoformat(),
                                }
                            )
                            continue

                        # Process message based on action or type
                        await self._handle_message(conn_id, ws, data)

                    except json.JSONDecodeError as e:
                        _LOGGER.warning("Invalid JSON from %s: %s", conn_id, str(e))
                        await ws.send_json(
                            {
                                "type": "error",
                                "data": {"message": "Invalid JSON format"},
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                            }
                        )

                    except Exception as e:
                        _LOGGER.error("Error processing message from %s: %s", conn_id, str(e))
                        await ws.send_json(
                            {
                                "type": "error",
                                "data": {"message": "Internal server error"},
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                            }
                        )

                elif msg.type == WSMsgType.PONG:
                    # Story 6.2, AC-5: Update last_ping timestamp on successful PONG
                    # aiohttp automatically handles PING/PONG frames, but we track for monitoring
                    update_last_ping(self.hass, conn_id)
                    _LOGGER.debug("PONG received from %s, last_ping updated", conn_id[:8] + "...")

                elif msg.type == WSMsgType.ERROR:
                    _LOGGER.warning(
                        "WebSocket error for %s: %s", conn_id, ws.exception()
                    )

        except asyncio.CancelledError:
            _LOGGER.debug("WebSocket connection cancelled: %s", conn_id)

        except Exception as e:
            _LOGGER.error("WebSocket error for %s: %s", conn_id, str(e))

        finally:
            # Cleanup: Remove connection from registry
            remove_connection(self.hass, conn_id)
            _LOGGER.info("Client disconnected: %s", conn_id)

        return ws

    async def _handle_message(
        self, conn_id: str, ws: web.WebSocketResponse, data: dict[str, Any]
    ) -> None:
        """Handle incoming message from client.

        Args:
            conn_id: The connection ID.
            ws: The WebSocket response object.
            data: The message data.
        """
        # Support both "action" (legacy) and "type" (Story 4.1) fields
        action = data.get("action") or data.get("type")

        if action == "test_ping":
            # Acknowledge ping
            await ws.send_json(
                {
                    "type": "pong",
                    "data": {"received": data.get("data", {})},
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
            _LOGGER.debug("Processed test_ping from %s", conn_id)

        elif action == "test_broadcast":
            # Trigger broadcast to all clients
            await broadcast_event(
                self.hass,
                "test_broadcast",
                {"message": "Test broadcast from server", "sender": conn_id},
            )
            _LOGGER.debug("Triggered test broadcast from %s", conn_id)

        elif action == "join_game":
            # Story 4.1 Task 8: Handle player registration
            await self._handle_join_game(conn_id, ws, data)

        else:
            _LOGGER.debug("Unknown action '%s' from %s", action, conn_id)
            await ws.send_json(
                {
                    "type": "ack",
                    "data": {"action": action, "status": "received"},
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

    async def _handle_join_game(
        self, conn_id: str, ws: web.WebSocketResponse, data: dict[str, Any]
    ) -> None:
        """Handle player registration (Story 4.1 Task 8).

        Args:
            conn_id: The connection ID.
            ws: The WebSocket response object.
            data: The message data containing player name.
        """
        try:
            name = data.get("name", "").strip()

            # Validate name (AC-4, AC-6)
            if not name or len(name) > 20:
                _LOGGER.warning("Invalid name from %s: '%s'", conn_id, name)
                await ws.send_json(
                    {
                        "type": "join_game_response",
                        "success": False,
                        "error": "invalid_name"
                    }
                )
                return

            # Check if game started (game must be in "lobby" status)
            if DOMAIN not in self.hass.data:
                _LOGGER.warning("No game session found for join_game")
                await ws.send_json(
                    {
                        "type": "join_game_response",
                        "success": False,
                        "error": "game_not_started"
                    }
                )
                return

            game_data = self.hass.data[DOMAIN]

            # Get game state
            from .game_state import get_game_state

            try:
                game_state = get_game_state(self.hass)
            except ValueError:
                # No game state initialized
                _LOGGER.warning("Game not started (no game state)")
                await ws.send_json(
                    {
                        "type": "join_game_response",
                        "success": False,
                        "error": "game_not_started"
                    }
                )
                return

            # Check if game has started (must be in lobby or later)
            if not game_state.game_started:
                _LOGGER.warning("Game not started (game_started=False)")
                await ws.send_json(
                    {
                        "type": "join_game_response",
                        "success": False,
                        "error": "game_not_started"
                    }
                )
                return

            # Generate UUID session_id (AC-5)
            session_id = str(uuid.uuid4())

            # Create player object (Story 4.2 will handle duplicate names)
            from .game_state import Player

            player = Player(
                name=name,
                session_id=session_id,
                score=0,
                is_admin=False,
                guesses=[],
                bets_placed=[],
                joined_at=datetime.now(timezone.utc).timestamp()
            )

            # Add player to game state
            game_state.players.append(player)

            _LOGGER.info(
                "Player joined: name=%s, session_id=%s, total_players=%d",
                name,
                session_id[:8] + "...",
                len(game_state.players)
            )

            # Send success response (AC-5)
            await ws.send_json(
                {
                    "type": "join_game_response",
                    "success": True,
                    "player_name": name,
                    "session_id": session_id
                }
            )

            # Story 4.3: Broadcast player_joined event to all clients
            # TODO: Implement in Story 4.3
            # await broadcast_message(
            #     self.hass,
            #     "player_joined",
            #     {"name": name, "player_count": len(game_state.players)}
            # )

        except Exception as e:
            _LOGGER.error("Error in handle_join_game: %s", str(e), exc_info=True)
            await ws.send_json(
                {
                    "type": "join_game_response",
                    "success": False,
                    "error": "server_error"
                }
            )


# ============================================================================
# Connection Management Functions (Epic 6, Story 6.1)
# ============================================================================


def add_connection(
    hass: HomeAssistant,
    connection_id: str,
    connection: web.WebSocketResponse,
    player_name: Optional[str] = None,
) -> None:
    """Register new WebSocket connection with metadata.

    Args:
        hass: Home Assistant instance.
        connection_id: Unique connection identifier.
        connection: WebSocket response object.
        player_name: Optional player name (None if not registered yet).
    """
    connections = hass.data[DOMAIN]["websocket_connections"]
    connections[connection_id] = {
        "connection": connection,
        "connection_id": connection_id,
        "player_name": player_name,
        "connected_at": time.time(),
        "last_ping": time.time(),
        "subscribed_events": [],  # Empty list = all events
    }
    _LOGGER.info(
        "WebSocket connected: conn_id=%s player=%s",
        connection_id[:8] + "...",
        player_name or "unregistered",
    )


def remove_connection(hass: HomeAssistant, connection_id: str) -> None:
    """Unregister connection on disconnect.

    Args:
        hass: Home Assistant instance.
        connection_id: Connection identifier to remove.
    """
    connections = hass.data[DOMAIN]["websocket_connections"]
    if connection_id in connections:
        player_name = connections[connection_id].get("player_name")
        del connections[connection_id]
        _LOGGER.info(
            "WebSocket disconnected: conn_id=%s player=%s",
            connection_id[:8] + "...",
            player_name or "unregistered",
        )


def get_connection_count(hass: HomeAssistant) -> int:
    """Return number of active connections.

    Args:
        hass: Home Assistant instance.

    Returns:
        Number of active WebSocket connections.
    """
    return len(hass.data[DOMAIN]["websocket_connections"])


def update_last_ping(hass: HomeAssistant, connection_id: str) -> None:
    """Update last_ping timestamp for connection (Story 6.2, AC-5).

    Called when PONG frame received from client to track connection health.

    Args:
        hass: Home Assistant instance.
        connection_id: Connection identifier to update.
    """
    connections = hass.data[DOMAIN]["websocket_connections"]
    if connection_id in connections:
        connections[connection_id]["last_ping"] = time.time()


def get_connection_by_player_name(
    hass: HomeAssistant, player_name: str
) -> Optional[dict]:
    """Lookup connection by player name (Story 6.2, Task 5).

    Returns first matching connection if player has multiple connections.

    Args:
        hass: Home Assistant instance.
        player_name: Player name to search for.

    Returns:
        Connection metadata dict or None if not found.
    """
    connections = hass.data[DOMAIN]["websocket_connections"]
    for conn_info in connections.values():
        if conn_info.get("player_name") == player_name:
            return conn_info
    return None


# ============================================================================
# Generic Event Bus - Broadcast Functions (Epic 6, Story 6.1)
# ============================================================================


async def broadcast_event(
    hass: HomeAssistant,
    event_type: str,
    payload: dict,
    exclude_connection_id: Optional[str] = None,
) -> None:
    """Broadcast event to all connected WebSocket clients concurrently.

    Uses asyncio.gather() for optimal performance (2025 best practice).
    Silently skips clients with send errors (best-effort delivery).

    Implements Epic 6, Story 6.1 acceptance criteria:
    - AC #1: Backend can call broadcast_event() from any module
    - AC #2: Standardized message format {type: "beatsy/event", event_type: "...", data: {...}}
    - AC #3: Optional event filtering via subscribed_events
    - AC #4: Disconnected clients automatically removed
    - AC #5: Best-effort delivery with return_exceptions=True

    Args:
        hass: Home Assistant instance.
        event_type: Event type identifier (e.g., "player_joined").
        payload: Event-specific data dict.
        exclude_connection_id: Optional connection ID to skip (for joining player).
    """
    if DOMAIN not in hass.data or "websocket_connections" not in hass.data[DOMAIN]:
        _LOGGER.warning("Cannot broadcast: WebSocket connections not initialized")
        return

    connections = hass.data[DOMAIN]["websocket_connections"]

    if not connections:
        _LOGGER.debug("No WebSocket clients connected for broadcast")
        return

    # Standardized event message format (AC #2)
    message = {
        "type": "beatsy/event",
        "event_type": event_type,
        "data": payload,
    }

    _LOGGER.debug(
        "Broadcasting event: type=%s clients=%d", event_type, len(connections)
    )

    # Build list of send tasks for concurrent execution
    send_tasks = []
    connection_ids = []

    for conn_id, conn_info in connections.items():
        # Skip excluded connection (e.g., joining player already has full list)
        if exclude_connection_id and conn_id == exclude_connection_id:
            continue

        # Optional event filtering (AC #3)
        subscribed_events = conn_info.get("subscribed_events", [])
        if subscribed_events and event_type not in subscribed_events:
            # Client has filter and event doesn't match
            _LOGGER.debug(
                "Skipping conn_id=%s: event %s not in subscription filter",
                conn_id[:8] + "...",
                event_type,
            )
            continue

        # Add send task
        ws = conn_info["connection"]
        send_tasks.append(ws.send_json(message))
        connection_ids.append(conn_id)

    if not send_tasks:
        _LOGGER.debug("No clients to broadcast to (after filtering)")
        return

    # Concurrent broadcast using asyncio.gather (2025 best practice)
    # return_exceptions=True ensures one failure doesn't stop others (AC #5)
    results = await asyncio.gather(*send_tasks, return_exceptions=True)

    # Handle failures: log errors and cleanup dead connections (AC #4, #5)
    failed_connections = []
    for conn_id, result in zip(connection_ids, results):
        if isinstance(result, Exception):
            _LOGGER.error(
                "Failed to send event to conn_id=%s: %s", conn_id[:8] + "...", result
            )
            failed_connections.append(conn_id)

    # Cleanup failed connections
    for conn_id in failed_connections:
        if conn_id in connections:
            del connections[conn_id]
            _LOGGER.info(
                "Removed dead connection during broadcast: %s", conn_id[:8] + "..."
            )

    _LOGGER.debug(
        "Broadcast complete: %d delivered, %d failed",
        len(send_tasks) - len(failed_connections),
        len(failed_connections),
    )


# Legacy alias for backward compatibility
async def broadcast_message(
    hass: HomeAssistant, msg_type: str, data: dict[str, Any]
) -> None:
    """Legacy broadcast function - delegates to broadcast_event.

    DEPRECATED: Use broadcast_event() directly for new code.

    Args:
        hass: The Home Assistant instance.
        msg_type: The message type identifier.
        data: The message payload data.
    """
    await broadcast_event(hass, msg_type, data)


async def cleanup_all_connections(hass: HomeAssistant) -> None:
    """Close all connections on component unload.

    Called from async_unload_entry() to ensure clean shutdown.

    Args:
        hass: The Home Assistant instance.
    """
    if DOMAIN not in hass.data or "websocket_connections" not in hass.data[DOMAIN]:
        return

    connections = hass.data[DOMAIN]["websocket_connections"]

    if not connections:
        return

    _LOGGER.info("Closing %d WebSocket connections", len(connections))

    # Close all connections concurrently
    close_tasks = []
    for conn_id, conn_info in connections.items():
        ws = conn_info["connection"]
        close_tasks.append(ws.close())

    # Use gather to close all at once
    results = await asyncio.gather(*close_tasks, return_exceptions=True)

    # Log any failures
    for conn_id, result in zip(connections.keys(), results):
        if isinstance(result, Exception):
            _LOGGER.warning(
                "Error closing connection %s: %s", conn_id[:8] + "...", result
            )

    # Clear registry
    connections.clear()
    _LOGGER.info("All WebSocket connections closed")


# Legacy alias for backward compatibility
async def close_all_connections(hass: HomeAssistant) -> None:
    """Legacy function - delegates to cleanup_all_connections.

    DEPRECATED: Use cleanup_all_connections() for new code.

    Args:
        hass: The Home Assistant instance.
    """
    await cleanup_all_connections(hass)
