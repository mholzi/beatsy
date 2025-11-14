"""WebSocket handler for Beatsy component.

Provides unauthenticated WebSocket endpoint for real-time game communication
between server and player clients.
"""
import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

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
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        # Generate unique connection ID
        conn_id = str(uuid.uuid4())

        # Store connection in registry
        connections = self.hass.data[DOMAIN]["ws_connections"]
        connections[conn_id] = ws

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
            if conn_id in connections:
                del connections[conn_id]
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
            await broadcast_message(
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


async def broadcast_message(
    hass: HomeAssistant, msg_type: str, data: dict[str, Any]
) -> None:
    """Broadcast message to all connected WebSocket clients.

    Args:
        hass: The Home Assistant instance.
        msg_type: The message type identifier.
        data: The message payload data.
    """
    if DOMAIN not in hass.data or "ws_connections" not in hass.data[DOMAIN]:
        _LOGGER.warning("Cannot broadcast: WebSocket connections not initialized")
        return

    connections = hass.data[DOMAIN]["ws_connections"]

    if not connections:
        _LOGGER.debug("No WebSocket clients connected for broadcast")
        return

    # Prepare message
    message = {
        "type": msg_type,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Track failed connections for cleanup
    failed_connections = []

    # Broadcast to all connections
    for conn_id, ws in connections.items():
        try:
            await ws.send_json(message)
            _LOGGER.debug("Broadcast sent to %s", conn_id)

        except ConnectionResetError:
            _LOGGER.debug("Connection reset for %s during broadcast", conn_id)
            failed_connections.append(conn_id)

        except Exception as e:
            _LOGGER.warning("Failed to send broadcast to %s: %s", conn_id, str(e))
            failed_connections.append(conn_id)

    # Cleanup failed connections
    for conn_id in failed_connections:
        if conn_id in connections:
            del connections[conn_id]
            _LOGGER.info("Removed dead connection during broadcast: %s", conn_id)

    if failed_connections:
        _LOGGER.debug(
            "Broadcast complete: %d delivered, %d failed",
            len(connections),
            len(failed_connections),
        )
    else:
        _LOGGER.debug("Broadcast complete: %d clients", len(connections))


async def close_all_connections(hass: HomeAssistant) -> None:
    """Close all active WebSocket connections.

    Called during component unload to gracefully shutdown all connections.

    Args:
        hass: The Home Assistant instance.
    """
    if DOMAIN not in hass.data or "ws_connections" not in hass.data[DOMAIN]:
        return

    connections = hass.data[DOMAIN]["ws_connections"]

    if not connections:
        return

    _LOGGER.info("Closing %d WebSocket connections", len(connections))

    # Close all connections
    for conn_id, ws in list(connections.items()):
        try:
            await ws.close()
            _LOGGER.debug("Closed WebSocket connection: %s", conn_id)
        except Exception as e:
            _LOGGER.warning("Error closing connection %s: %s", conn_id, str(e))

    # Clear registry
    connections.clear()
    _LOGGER.info("All WebSocket connections closed")
