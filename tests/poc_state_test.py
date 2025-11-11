#!/usr/bin/env python3
"""POC State Stress Test Script.

This script tests both hass.data and entry.runtime_data patterns for storing
game state in Home Assistant. Validates performance and compares patterns.

Usage:
    python tests/poc_state_test.py [--output metrics.json] [--pattern both|hass_data|runtime_data]

Requirements:
    - Home Assistant test instance must be running
    - Beatsy component must be installed

Reference: Story 1.5 - Data Registry Write/Read Stress Test
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run Beatsy state stress test with pattern comparison"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Optional JSON file path for metrics output",
        default=None,
    )
    parser.add_argument(
        "--pattern",
        type=str,
        choices=["both", "hass_data", "runtime_data"],
        default="both",
        help="Storage pattern to test (default: both)",
    )
    return parser.parse_args()


async def setup_test_environment():
    """Setup Home Assistant test environment."""
    # Add custom_components to Python path
    import os

    repo_root = Path(__file__).parent.parent
    custom_components_path = repo_root / "home-assistant-config" / "custom_components"

    if str(custom_components_path) not in sys.path:
        sys.path.insert(0, str(custom_components_path))

    # Import Home Assistant core
    try:
        from homeassistant.core import HomeAssistant

        # Create test HA instance
        hass = HomeAssistant()
        await hass.async_start()

        print("✓ Home Assistant test instance started")
        return hass

    except ImportError as e:
        print(f"✗ Failed to import Home Assistant: {e}")
        print("\nPlease ensure Home Assistant is installed:")
        print("  pip install homeassistant")
        sys.exit(1)


async def run_pattern_test(
    hass, pattern_name: str, use_runtime_data: bool
) -> dict[str, any]:
    """Run test for a specific storage pattern."""
    from beatsy.state_test import run_state_stress_test

    print(f"\n{'='*60}")
    print(f"Testing Pattern: {pattern_name}")
    print(f"{'='*60}\n")

    # Run stress test
    metrics = await run_state_stress_test(hass, use_runtime_data=use_runtime_data)

    # Print results
    print(f"\n📊 Results for {pattern_name}:")
    print(f"  Total Operations: {metrics.total_operations}")
    print(f"  Duration: {metrics.duration_seconds}s")
    print(f"  Avg Latency: {metrics.avg_latency_ms}ms")
    print(f"  Max Latency: {metrics.max_latency_ms}ms")
    print(f"  Success Rate: {metrics.success_count}/{metrics.total_operations}")
    print(f"  Failures: {metrics.failure_count}")

    # Validate against targets
    passed = True
    print("\n✓ Target Validation:")

    if metrics.duration_seconds < 30:
        print(f"  ✓ Duration < 30s: {metrics.duration_seconds}s PASS")
    else:
        print(f"  ✗ Duration < 30s: {metrics.duration_seconds}s FAIL")
        passed = False

    if metrics.avg_latency_ms < 300:
        print(f"  ✓ Avg latency < 300ms: {metrics.avg_latency_ms}ms PASS")
    else:
        print(f"  ✗ Avg latency < 300ms: {metrics.avg_latency_ms}ms FAIL")
        passed = False

    if metrics.max_latency_ms < 500:
        print(f"  ✓ Max latency < 500ms: {metrics.max_latency_ms}ms PASS")
    else:
        print(f"  ✗ Max latency < 500ms: {metrics.max_latency_ms}ms FAIL")
        passed = False

    if metrics.failure_count == 0:
        print(f"  ✓ No data corruption: 100% integrity PASS")
    else:
        print(f"  ✗ Data corruption detected: {metrics.failure_count} errors FAIL")
        passed = False

    status = "PASS" if passed else "FAIL"
    print(f"\n{'='*60}")
    print(f"Overall Status: {status}")
    print(f"{'='*60}")

    # Convert to dict for JSON serialization
    return {
        "test_type": metrics.test_type,
        "storage_pattern": metrics.storage_pattern,
        "status": status,
        "total_operations": metrics.total_operations,
        "duration_seconds": metrics.duration_seconds,
        "avg_latency_ms": metrics.avg_latency_ms,
        "max_latency_ms": metrics.max_latency_ms,
        "success_count": metrics.success_count,
        "failure_count": metrics.failure_count,
        "errors": metrics.errors,
        "timestamp": datetime.now().isoformat(),
    }


async def main() -> None:
    """Main test execution."""
    args = parse_args()

    print("╔═══════════════════════════════════════════════════════════╗")
    print("║     Beatsy POC State Stress Test (Story 1.5)             ║")
    print("║     Testing: HA 2025 Storage Patterns                    ║")
    print("╚═══════════════════════════════════════════════════════════╝\n")

    # Setup test environment
    hass = await setup_test_environment()

    results = {}

    try:
        # Run tests based on pattern selection
        if args.pattern in ["both", "hass_data"]:
            results["hass_data"] = await run_pattern_test(
                hass, "hass.data (Legacy)", use_runtime_data=False
            )

        if args.pattern in ["both", "runtime_data"]:
            results["runtime_data"] = await run_pattern_test(
                hass, "entry.runtime_data (2025)", use_runtime_data=True
            )

        # Pattern comparison (if both tested)
        if len(results) == 2:
            print(f"\n{'='*60}")
            print("Pattern Comparison")
            print(f"{'='*60}\n")

            hass_data_metrics = results["hass_data"]
            runtime_data_metrics = results["runtime_data"]

            duration_diff = (
                runtime_data_metrics["duration_seconds"]
                - hass_data_metrics["duration_seconds"]
            )
            avg_latency_diff = (
                runtime_data_metrics["avg_latency_ms"]
                - hass_data_metrics["avg_latency_ms"]
            )

            print(f"Duration difference: {duration_diff:+.2f}s")
            print(f"Avg latency difference: {avg_latency_diff:+.2f}ms")

            if abs(duration_diff) < 1.0:
                print("\n✓ Both patterns show similar performance")
                print("  Recommendation: Use entry.runtime_data for production")
                print("  Benefits: Type safety, automatic cleanup, cleaner code")
            elif duration_diff < 0:
                print("\n✓ entry.runtime_data is faster")
                print("  Recommendation: Use entry.runtime_data for production")
            else:
                print("\n✓ hass.data is faster")
                print(
                    "  Note: Despite speed advantage, entry.runtime_data recommended"
                )
                print("  Reason: Type safety and code quality benefits outweigh minor performance difference")

            results["pattern_comparison"] = {
                "duration_difference_seconds": round(duration_diff, 2),
                "avg_latency_difference_ms": round(avg_latency_diff, 2),
                "recommendation": "entry.runtime_data",
                "rationale": "HA 2025 best practice - type safety, automatic cleanup, better code organization",
            }

        # Output to JSON if requested
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with output_path.open("w") as f:
                json.dump(results, f, indent=2)

            print(f"\n✓ Metrics saved to: {output_path}")

        print("\n✓ Test execution complete!")

    finally:
        # Cleanup
        await hass.async_stop()
        print("\n✓ Home Assistant test instance stopped")


if __name__ == "__main__":
    asyncio.run(main())
