#!/usr/bin/env python3
"""
Add stopTimer() call to handleRoundEnded function for Story 8.5
"""

def add_stop_timer_to_round_ended():
    file_path = "/Volumes/My Passport/HA_Dashboard/custom_components/beatsy/www/js/ui-player.js"

    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Find all occurrences of "function handleRoundEnded("
    function_indices = []
    for i, line in enumerate(lines):
        if 'function handleRoundEnded(' in line:
            function_indices.append(i)
            print(f"Found handleRoundEnded at line {i+1}")

    print(f"\nFound {len(function_indices)} handleRoundEnded functions")

    # For each function, check if stopTimer() is already called
    for idx in function_indices:
        # Look ahead ~20 lines to see if stopTimer() is already there
        search_range = lines[idx:idx+20]
        has_stop_timer = any('stopTimer()' in line for line in search_range)

        if has_stop_timer:
            print(f"  Line {idx+1}: Already has stopTimer() call")
            continue

        # Find the opening brace and add stopTimer() call after it
        for offset in range(20):
            if idx + offset >= len(lines):
                break

            line = lines[idx + offset]

            # Look for the first console.log after function opening
            if 'console.log(' in line and offset > 0:
                # Insert stopTimer() call before this console.log
                indent = len(line) - len(line.lstrip())
                stop_timer_line = ' ' * indent + "// Story 8.5 Task 6: Stop timer on round end\n"
                stop_timer_call = ' ' * indent + "stopTimer();\n"
                stop_timer_blank = '\n'

                lines.insert(idx + offset, stop_timer_blank)
                lines.insert(idx + offset, stop_timer_call)
                lines.insert(idx + offset, stop_timer_line)

                print(f"  Line {idx+1}: Added stopTimer() call at offset {offset}")
                break

    # Write back to file
    with open(file_path, 'w') as f:
        f.writelines(lines)

    print(f"\n✓ Updated {file_path}")

if __name__ == '__main__':
    add_stop_timer_to_round_ended()
