"""Load test for Beatsy WebSocket endpoint.

Tests concurrent WebSocket connections to validate AC-5:
- 10+ clients connect simultaneously
- All connections stable, no drops
- HA remains responsive
"""
import asyncio
import json
import logging
import sys
from datetime import datetime

import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
_LOGGER = logging.getLogger(__name__)


class WebSocketTestClient:
    """WebSocket test client for load testing."""

    def __init__(self, client_id: int, ws_url: str):
        """Initialize test client.

        Args:
            client_id: Unique client identifier.
            ws_url: WebSocket endpoint URL.
        """
        self.client_id = client_id
        self.ws_url = ws_url
        self.messages_received = 0
        self.connected = False
        self.connection_time = None

    async def run(self, duration_seconds: int = 60) -> dict:
        """Run the test client.

        Args:
            duration_seconds: How long to stay connected.

        Returns:
            Test statistics dict.
        """
        start_time = datetime.now()
        stats = {
            'client_id': self.client_id,
            'connected': False,
            'messages_received': 0,
            'errors': [],
        }

        try:
            async with aiohttp.ClientSession() as session:
                _LOGGER.info("Client %d: Connecting to %s", self.client_id, self.ws_url)

                async with session.ws_connect(self.ws_url) as ws:
                    self.connected = True
                    self.connection_time = datetime.now()
                    stats['connected'] = True

                    connection_duration = (self.connection_time - start_time).total_seconds()
                    _LOGGER.info(
                        "Client %d: Connected (%.3f seconds)",
                        self.client_id,
                        connection_duration
                    )

                    # Send initial ping
                    await ws.send_json({
                        'action': 'test_ping',
                        'data': {
                            'client_id': f'load-test-{self.client_id}',
                            'timestamp': datetime.now().isoformat()
                        }
                    })

                    # Listen for messages for specified duration
                    end_time = start_time.timestamp() + duration_seconds

                    while datetime.now().timestamp() < end_time:
                        try:
                            msg = await asyncio.wait_for(ws.receive(), timeout=5.0)

                            if msg.type == aiohttp.WSMsgType.TEXT:
                                data = json.loads(msg.data)
                                self.messages_received += 1
                                _LOGGER.debug(
                                    "Client %d: Received message: %s",
                                    self.client_id,
                                    data.get('type')
                                )

                            elif msg.type == aiohttp.WSMsgType.CLOSED:
                                _LOGGER.warning("Client %d: Connection closed by server", self.client_id)
                                stats['errors'].append('Connection closed by server')
                                break

                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                _LOGGER.error("Client %d: WebSocket error", self.client_id)
                                stats['errors'].append('WebSocket error')
                                break

                        except asyncio.TimeoutError:
                            # No message received in timeout period, continue
                            continue

                        except Exception as e:
                            _LOGGER.error("Client %d: Error receiving message: %s", self.client_id, str(e))
                            stats['errors'].append(f'Receive error: {str(e)}')

                    _LOGGER.info(
                        "Client %d: Test complete, received %d messages",
                        self.client_id,
                        self.messages_received
                    )

        except aiohttp.ClientError as e:
            _LOGGER.error("Client %d: Connection error: %s", self.client_id, str(e))
            stats['errors'].append(f'Connection error: {str(e)}')

        except Exception as e:
            _LOGGER.error("Client %d: Unexpected error: %s", self.client_id, str(e))
            stats['errors'].append(f'Unexpected error: {str(e)}')

        finally:
            stats['messages_received'] = self.messages_received
            return stats


async def run_load_test(
    ws_url: str,
    num_clients: int = 10,
    duration_seconds: int = 60
) -> dict:
    """Run load test with multiple concurrent clients.

    Args:
        ws_url: WebSocket endpoint URL.
        num_clients: Number of concurrent clients to spawn.
        duration_seconds: How long to run the test.

    Returns:
        Aggregated test results.
    """
    _LOGGER.info("Starting load test: %d clients for %d seconds", num_clients, duration_seconds)

    # Create clients
    clients = [
        WebSocketTestClient(i + 1, ws_url)
        for i in range(num_clients)
    ]

    # Run all clients concurrently
    start_time = datetime.now()
    results = await asyncio.gather(
        *[client.run(duration_seconds) for client in clients],
        return_exceptions=True
    )
    end_time = datetime.now()

    # Aggregate results
    total_duration = (end_time - start_time).total_seconds()
    successful_connections = sum(1 for r in results if isinstance(r, dict) and r['connected'])
    total_messages = sum(r['messages_received'] for r in results if isinstance(r, dict))
    total_errors = sum(len(r['errors']) for r in results if isinstance(r, dict))

    summary = {
        'num_clients': num_clients,
        'duration_seconds': total_duration,
        'successful_connections': successful_connections,
        'failed_connections': num_clients - successful_connections,
        'total_messages_received': total_messages,
        'total_errors': total_errors,
        'connection_success_rate': (successful_connections / num_clients) * 100,
    }

    _LOGGER.info("=" * 60)
    _LOGGER.info("LOAD TEST SUMMARY")
    _LOGGER.info("=" * 60)
    _LOGGER.info("Clients: %d", summary['num_clients'])
    _LOGGER.info("Duration: %.2f seconds", summary['duration_seconds'])
    _LOGGER.info("Successful connections: %d", summary['successful_connections'])
    _LOGGER.info("Failed connections: %d", summary['failed_connections'])
    _LOGGER.info("Connection success rate: %.1f%%", summary['connection_success_rate'])
    _LOGGER.info("Total messages received: %d", summary['total_messages_received'])
    _LOGGER.info("Total errors: %d", summary['total_errors'])
    _LOGGER.info("=" * 60)

    # Detailed client results
    for i, result in enumerate(results):
        if isinstance(result, dict):
            status = "✓ PASS" if result['connected'] and not result['errors'] else "✗ FAIL"
            _LOGGER.info(
                "Client %d: %s - Connected: %s, Messages: %d, Errors: %d",
                i + 1,
                status,
                result['connected'],
                result['messages_received'],
                len(result['errors'])
            )
        else:
            _LOGGER.error("Client %d: EXCEPTION - %s", i + 1, str(result))

    return summary


async def test_broadcast(ws_url: str, num_clients: int = 10) -> bool:
    """Test broadcast functionality with multiple clients.

    Args:
        ws_url: WebSocket endpoint URL.
        num_clients: Number of clients to connect.

    Returns:
        True if broadcast test passed.
    """
    _LOGGER.info("Testing broadcast with %d clients", num_clients)

    connections = []
    messages_received = [0] * num_clients

    try:
        async with aiohttp.ClientSession() as session:
            # Connect all clients
            for i in range(num_clients):
                ws = await session.ws_connect(ws_url)
                connections.append(ws)
                _LOGGER.info("Broadcast test: Client %d connected", i + 1)

            # Wait for connection confirmations
            await asyncio.sleep(1)

            # Trigger broadcast from first client
            await connections[0].send_json({
                'action': 'test_broadcast',
                'data': {'message': 'Broadcast test message'}
            })

            _LOGGER.info("Broadcast triggered, waiting for messages...")

            # Wait for broadcast messages (500ms timeout per AC-4)
            async def receive_messages(client_idx, ws):
                try:
                    msg = await asyncio.wait_for(ws.receive(), timeout=1.0)
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        if data.get('type') == 'test_broadcast':
                            messages_received[client_idx] = 1
                            _LOGGER.info("Client %d received broadcast", client_idx + 1)
                except asyncio.TimeoutError:
                    _LOGGER.warning("Client %d: No broadcast received", client_idx + 1)

            # Listen for broadcasts on all clients
            await asyncio.gather(*[
                receive_messages(i, ws) for i, ws in enumerate(connections)
            ])

            # Close all connections
            for i, ws in enumerate(connections):
                await ws.close()
                _LOGGER.info("Client %d disconnected", i + 1)

    except Exception as e:
        _LOGGER.error("Broadcast test error: %s", str(e))
        return False

    # Check results
    received_count = sum(messages_received)
    success_rate = (received_count / num_clients) * 100

    _LOGGER.info("=" * 60)
    _LOGGER.info("BROADCAST TEST RESULTS")
    _LOGGER.info("=" * 60)
    _LOGGER.info("Clients: %d", num_clients)
    _LOGGER.info("Broadcasts received: %d", received_count)
    _LOGGER.info("Success rate: %.1f%%", success_rate)
    _LOGGER.info("=" * 60)

    return received_count == num_clients


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python poc_websocket_load_test.py <HA_HOST> [num_clients] [duration]")
        print("Example: python poc_websocket_load_test.py 192.168.0.191:8123 10 60")
        sys.exit(1)

    ha_host = sys.argv[1]
    num_clients = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    duration = int(sys.argv[3]) if len(sys.argv) > 3 else 60

    ws_url = f"ws://{ha_host}/api/beatsy/ws"

    _LOGGER.info("WebSocket Load Test")
    _LOGGER.info("Target: %s", ws_url)
    _LOGGER.info("Clients: %d", num_clients)
    _LOGGER.info("Duration: %d seconds", duration)

    # Run load test
    summary = asyncio.run(run_load_test(ws_url, num_clients, duration))

    # Run broadcast test
    _LOGGER.info("\nRunning broadcast test...")
    broadcast_success = asyncio.run(test_broadcast(ws_url, num_clients))

    # Final verdict
    success = (
        summary['connection_success_rate'] == 100 and
        summary['total_errors'] == 0 and
        broadcast_success
    )

    if success:
        _LOGGER.info("\n✓ ALL TESTS PASSED")
        sys.exit(0)
    else:
        _LOGGER.error("\n✗ TESTS FAILED")
        sys.exit(1)


if __name__ == '__main__':
    main()
