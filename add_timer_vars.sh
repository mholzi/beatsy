#!/bin/bash
# Add timer state variables after timerInterval declaration

file="custom_components/beatsy/www/js/ui-player.js"

# Check if variables already exist
if grep -q "let roundStartedAt" "$file"; then
    echo "✓ Timer state variables already exist"
    exit 0
fi

# Find line with "let timerInterval" and add after it
awk '/^let timerInterval = null;/ {
    print $0
    print ""
    print "// Global timer state variables (Story 8.5)"
    print "let roundStartedAt = null;  // Unix timestamp in milliseconds"
    print "let timerDuration = null;   // Duration in seconds"
    next
}
{print}' "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"

echo "✓ Added timer state variables"
