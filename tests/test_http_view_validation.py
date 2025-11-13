"""Validation script for HTTP views (Story 2.5) - No HA dependencies required.

This script validates that:
1. All view classes are properly defined
2. Authentication settings are correct
3. URL patterns are correct
4. Methods exist and have correct signatures
"""
import sys
from pathlib import Path

# Add the custom_components directory to the path
sys.path.insert(
    0, str(Path(__file__).parent.parent / "home-assistant-config" / "custom_components")
)

def validate_view_class(view_name, expected_url, expected_auth, expected_methods):
    """Validate a view class has correct configuration."""
    try:
        from beatsy.http_view import BeatsyAdminView, BeatsyPlayerView, BeatsyAPIView

        views = {
            "BeatsyAdminView": BeatsyAdminView,
            "BeatsyPlayerView": BeatsyPlayerView,
            "BeatsyAPIView": BeatsyAPIView,
        }

        view_class = views[view_name]
        view = view_class()

        # Validate URL
        assert view.url == expected_url, f"{view_name}: Expected url={expected_url}, got {view.url}"
        print(f"✓ {view_name}: URL correct ({view.url})")

        # Validate authentication
        assert view.requires_auth == expected_auth, f"{view_name}: Expected requires_auth={expected_auth}, got {view.requires_auth}"
        auth_status = "requires auth" if expected_auth else "NO auth required"
        print(f"✓ {view_name}: Authentication correct ({auth_status})")

        # Validate methods exist
        for method in expected_methods:
            assert hasattr(view, method), f"{view_name}: Missing method {method}"
            assert callable(getattr(view, method)), f"{view_name}: {method} is not callable"
        print(f"✓ {view_name}: All methods present ({', '.join(expected_methods)})")

        return True

    except Exception as e:
        print(f"✗ {view_name}: FAILED - {str(e)}")
        return False

def main():
    """Run all validation checks."""
    print("=" * 60)
    print("HTTP View Validation (Story 2.5)")
    print("=" * 60)
    print()

    all_passed = True

    # Validate BeatsyAdminView
    print("Testing BeatsyAdminView...")
    if not validate_view_class(
        "BeatsyAdminView",
        "/api/beatsy/admin",
        True,  # requires_auth = True
        ["get"]
    ):
        all_passed = False
    print()

    # Validate BeatsyPlayerView
    print("Testing BeatsyPlayerView...")
    if not validate_view_class(
        "BeatsyPlayerView",
        "/api/beatsy/player",
        False,  # requires_auth = False (Epic 1 POC pattern)
        ["get"]
    ):
        all_passed = False
    print()

    # Validate BeatsyAPIView
    print("Testing BeatsyAPIView...")
    if not validate_view_class(
        "BeatsyAPIView",
        "/api/beatsy/api/{endpoint}",
        True,  # requires_auth = True
        ["get", "post"]
    ):
        all_passed = False
    print()

    # Summary
    print("=" * 60)
    if all_passed:
        print("✅ ALL VALIDATION CHECKS PASSED")
        print("=" * 60)
        print()
        print("Implementation Summary:")
        print("- BeatsyAdminView: Authenticated admin interface")
        print("- BeatsyPlayerView: Unauthenticated player interface (Epic 1 POC)")
        print("- BeatsyAPIView: Authenticated REST API endpoints")
        print()
        print("Ready for manual testing:")
        print("1. Start Home Assistant with Beatsy integration")
        print("2. Access /api/beatsy/admin (should require login)")
        print("3. Access /api/beatsy/player (should work without login)")
        print("4. Test API endpoints with curl/Postman")
        return 0
    else:
        print("❌ SOME VALIDATION CHECKS FAILED")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    exit(main())
