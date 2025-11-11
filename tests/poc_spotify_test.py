#!/usr/bin/env python3
"""POC Spotify Integration Test Script.

This script validates Spotify API integration for Beatsy by testing:
1. Playlist track fetching
2. Metadata extraction
3. Playback initiation
4. Media player state reading

Usage:
    python tests/poc_spotify_test.py --playlist_uri=<uri> --media_player_entity=<entity_id>

Example:
    python tests/poc_spotify_test.py \\
        --playlist_uri="spotify:playlist:37i9dQZF1DXcBWIGoYBM5M" \\
        --media_player_entity="media_player.spotify_living_room"
"""
import argparse
import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

# Add custom_components to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "home-assistant-config" / "custom_components"))

from beatsy.spotify_helper import (
    fetch_playlist_tracks,
    extract_track_metadata,
    play_track,
    get_media_player_metadata,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
_LOGGER = logging.getLogger(__name__)


class MockHomeAssistant:
    """Mock Home Assistant instance for testing (simplified).

    Note: This is a placeholder. For actual testing, you would need
    to connect to a real Home Assistant instance via REST API or
    run this script within Home Assistant's context.
    """

    def __init__(self):
        self.data = {}
        self.config = None
        self.states_data = {}

    class States:
        def __init__(self, parent):
            self.parent = parent

        def get(self, entity_id):
            return self.parent.states_data.get(entity_id)

    class Services:
        async def async_call(self, domain, service, service_data, blocking=False):
            _LOGGER.info(
                "Service call: %s.%s with data: %s",
                domain, service, service_data
            )

    def __init__(self):
        self.data = {}
        self.states = self.States(self)
        self.services = self.Services()


async def run_poc_test(playlist_uri: str, media_player_entity: str) -> dict:
    """Run POC Spotify integration test.

    Args:
        playlist_uri: Spotify playlist URI
        media_player_entity: Media player entity ID

    Returns:
        Test results dictionary
    """
    results = {
        "test": "spotify_integration",
        "status": "FAIL",
        "timestamp": datetime.now().isoformat(),
        "playlist_uri": playlist_uri,
        "media_player_entity": media_player_entity,
        "tracks_fetched": 0,
        "tracks_with_year": 0,
        "tracks_without_year": 0,
        "metadata_fields_present": [],
        "playback_time_ms": None,
        "errors": []
    }

    # Note: This is a placeholder implementation
    # Real implementation requires actual Home Assistant connection
    _LOGGER.warning("=" * 60)
    _LOGGER.warning("POC TEST SCRIPT - PLACEHOLDER IMPLEMENTATION")
    _LOGGER.warning("=" * 60)
    _LOGGER.warning("")
    _LOGGER.warning("This script demonstrates the test flow but requires")
    _LOGGER.warning("integration with a real Home Assistant instance.")
    _LOGGER.warning("")
    _LOGGER.warning("To run actual tests:")
    _LOGGER.warning("1. Deploy Beatsy component to HA")
    _LOGGER.warning("2. Configure Spotify integration in HA")
    _LOGGER.warning("3. Run this script from HA's Python environment")
    _LOGGER.warning("   or adapt it to use HA's REST API")
    _LOGGER.warning("")
    _LOGGER.warning("=" * 60)
    _LOGGER.warning("")

    try:
        # Create mock hass instance
        # TODO: Replace with actual HA connection
        hass = MockHomeAssistant()

        _LOGGER.info("Step 1: Fetching playlist tracks...")
        _LOGGER.info("Playlist URI: %s", playlist_uri)

        # TODO: Uncomment when integrated with real HA
        # tracks = await fetch_playlist_tracks(hass, playlist_uri)
        # results["tracks_fetched"] = len(tracks)
        # _LOGGER.info("✓ Fetched %d tracks", len(tracks))

        _LOGGER.info("[SIMULATED] Would fetch tracks from playlist")
        results["errors"].append("Test not run - requires HA integration")

        _LOGGER.info("")
        _LOGGER.info("Step 2: Extracting metadata from first 3 tracks...")

        # TODO: Uncomment when integrated with real HA
        # for i, track in enumerate(tracks[:3], 1):
        #     metadata = extract_track_metadata(track)
        #     _LOGGER.info("Track %d: %s - %s (%s)",
        #                  i, metadata['title'], metadata['artist'], metadata['year'])
        #
        #     if metadata['year']:
        #         results["tracks_with_year"] += 1
        #     else:
        #         results["tracks_without_year"] += 1

        _LOGGER.info("[SIMULATED] Would extract metadata for first 3 tracks")

        _LOGGER.info("")
        _LOGGER.info("Step 3: Playing first track...")
        _LOGGER.info("Media player: %s", media_player_entity)

        # TODO: Uncomment when integrated with real HA
        # first_track = tracks[0]
        # first_track_metadata = extract_track_metadata(first_track)
        # track_uri = first_track_metadata['uri']
        #
        # start_time = time.time()
        # success = await play_track(hass, media_player_entity, track_uri)
        # playback_time_ms = int((time.time() - start_time) * 1000)
        #
        # results["playback_time_ms"] = playback_time_ms
        # _LOGGER.info("✓ Playback initiated in %d ms", playback_time_ms)

        _LOGGER.info("[SIMULATED] Would initiate playback")

        _LOGGER.info("")
        _LOGGER.info("Step 4: Waiting 2 seconds for HA state update...")

        # TODO: Uncomment when integrated with real HA
        # await asyncio.sleep(2)

        _LOGGER.info("[SIMULATED] Would wait 2 seconds")

        _LOGGER.info("")
        _LOGGER.info("Step 5: Reading media player state...")

        # TODO: Uncomment when integrated with real HA
        # player_metadata = await get_media_player_metadata(hass, media_player_entity)
        #
        # _LOGGER.info("Media Title: %s", player_metadata.get('media_title'))
        # _LOGGER.info("Media Artist: %s", player_metadata.get('media_artist'))
        # _LOGGER.info("Media Album: %s", player_metadata.get('media_album_name'))
        # _LOGGER.info("Cover URL: %s", player_metadata.get('entity_picture'))
        #
        # # Track which fields are present
        # for field in ['media_title', 'media_artist', 'media_album_name', 'entity_picture']:
        #     if player_metadata.get(field):
        #         results["metadata_fields_present"].append(field)

        _LOGGER.info("[SIMULATED] Would read media player state")

        _LOGGER.info("")
        _LOGGER.info("=" * 60)
        _LOGGER.info("TEST INCOMPLETE - REQUIRES HOME ASSISTANT INTEGRATION")
        _LOGGER.info("=" * 60)

        # For now, mark as incomplete rather than pass/fail
        results["status"] = "INCOMPLETE"

    except Exception as e:
        _LOGGER.error("Test failed with error: %s", str(e), exc_info=True)
        results["errors"].append(str(e))
        results["status"] = "ERROR"

    return results


def main():
    """Main entry point for POC test script."""
    parser = argparse.ArgumentParser(
        description='Test Spotify integration for Beatsy POC'
    )
    parser.add_argument(
        '--playlist_uri',
        required=True,
        help='Spotify playlist URI (spotify:playlist:xxx or https://...)'
    )
    parser.add_argument(
        '--media_player_entity',
        required=True,
        help='Media player entity ID (e.g., media_player.spotify_living_room)'
    )
    parser.add_argument(
        '--output',
        default='tests/poc_metrics.json',
        help='Output file for test metrics (default: tests/poc_metrics.json)'
    )

    args = parser.parse_args()

    # Run async test
    results = asyncio.run(run_poc_test(args.playlist_uri, args.media_player_entity))

    # Save results to JSON
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    _LOGGER.info("")
    _LOGGER.info("Results saved to: %s", output_path)

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Status: {results['status']}")
    print(f"Playlist URI: {results['playlist_uri']}")
    print(f"Tracks Fetched: {results['tracks_fetched']}")
    print(f"Tracks with Year: {results['tracks_with_year']}")
    print(f"Tracks without Year: {results['tracks_without_year']}")
    print(f"Playback Time: {results['playback_time_ms']} ms" if results['playback_time_ms'] else "Playback Time: N/A")
    print(f"Metadata Fields: {', '.join(results['metadata_fields_present']) if results['metadata_fields_present'] else 'None'}")

    if results['errors']:
        print("\nErrors:")
        for error in results['errors']:
            print(f"  - {error}")

    print("=" * 60)

    # Exit code based on status
    if results['status'] == 'PASS':
        sys.exit(0)
    elif results['status'] == 'INCOMPLETE':
        sys.exit(2)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
