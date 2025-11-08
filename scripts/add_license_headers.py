#!/usr/bin/env python3
# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#
"""Script to add PolyForm Noncommercial License 1.0.0 headers to all Python files."""

import os
import sys
from pathlib import Path

LICENSE_HEADER = """# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#
"""


def has_license_header(content: str) -> bool:
    """Check if file already has a license header."""
    # Check for the key license text in the first 500 characters
    if "PolyForm Noncommercial License" not in content[:500]:
        return False
    
    # Also check for the copyright line to ensure it's a proper header
    if "Copyright (c) 2025 SubtitleFlow Team" not in content[:500]:
        return False
    
    # Check if the header is at the beginning (after optional shebang)
    lines = content.split("\n")
    start_idx = 0
    if lines and lines[0].startswith("#!"):
        start_idx = 1
        if len(lines) > 1 and not lines[1].strip():
            start_idx = 2
    
    # Check if the first non-shebang line is the copyright
    if start_idx < len(lines) and "Copyright (c) 2025 SubtitleFlow Team" in lines[start_idx]:
        return True
    
    return False


def add_license_header(file_path: Path) -> bool:
    """Add license header to a Python file if it doesn't already have one."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return False

    # Check if header already exists - if so, don't modify the file
    if has_license_header(content):
        return False  # Header exists, no changes needed

    # Skip if file starts with shebang
    lines = content.split("\n")
    new_content = []
    shebang = None

    if lines and lines[0].startswith("#!"):
        shebang = lines[0]
        lines = lines[1:]
        # Skip blank line after shebang if present
        if lines and not lines[0].strip():
            lines = lines[1:]

    # Add license header
    if shebang:
        new_content.append(shebang)
        new_content.append("")
    new_content.append(LICENSE_HEADER.rstrip())
    new_content.append("")
    new_content.extend(lines)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(new_content))
        return True
    except Exception as e:
        print(f"Error writing {file_path}: {e}", file=sys.stderr)
        return False


def main():
    """Main function to add license headers to all Python files."""
    project_root = Path(__file__).parent.parent
    python_files = []

    # Find all Python files
    for root, dirs, files in os.walk(project_root):
        # Skip certain directories
        dirs[:] = [
            d
            for d in dirs
            if d
            not in {
                ".git",
                ".venv",
                "__pycache__",
                ".mypy_cache",
                ".pytest_cache",
                "legacy",
                "dist",
                "build",
            }
        ]

        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                python_files.append(file_path)

    # Sort for consistent output
    python_files.sort()

    modified_count = 0
    skipped_count = 0

    for file_path in python_files:
        if add_license_header(file_path):
            print(f"Added license header to: {file_path.relative_to(project_root)}")
            modified_count += 1
        else:
            skipped_count += 1

    print(f"\nSummary: {modified_count} files modified, {skipped_count} files skipped")
    return 0 if modified_count > 0 or skipped_count > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
