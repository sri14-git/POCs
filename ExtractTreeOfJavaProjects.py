#!/usr/bin/env python3
"""
Walk a Java project and emit its .java-file structure as both JSON and ASCII-art tree.

At runtime it will prompt you for the project root (accepts relative or absolute paths).

Toggle the output behaviors at the top as needed.
"""

import os
import json
from pathlib import Path

# ───────────────────────
# Output toggles
# ───────────────────────
PRINT_JSON       = False   # show JSON on stdout
WRITE_JSON_FILE  = False   # write JSON to structure.json
PRINT_TREE       = False   # show ASCII tree on stdout
WRITE_TREE_FILE  = True   # write ASCII tree to structure_tree.txt

# ───────────────────────
# Build nested structure
# ───────────────────────
def build_structure(root: Path) -> dict:
    """
    Recursively walk `root` and include only .java files.
    Returns a nested dict where keys are names, and
    values are dict (subdir) or None (file).
    """
    tree = {}
    # Files directly under root
    for p in sorted(root.iterdir()):
        if p.is_file() and p.suffix == ".java":
            tree[p.name] = None

    # Recurse into subdirectories
    for p in sorted(root.iterdir()):
        if p.is_dir():
            subtree = build_structure(p)
            if subtree:  # only include if it has .java files
                tree[p.name] = subtree
    return tree

# ───────────────────────
# ASCII-art tree printer
# ───────────────────────
def print_ascii_tree(node: dict, prefix: str = ""):
    entries = list(node.items())
    for idx, (name, child) in enumerate(entries):
        is_last = (idx == len(entries) - 1)
        branch = "└── " if is_last else "├── "
        print(f"{prefix}{branch}{name}")
        if isinstance(child, dict):
            extension = "    " if is_last else "│   "
            print_ascii_tree(child, prefix + extension)

def flatten_ascii_tree(node: dict, prefix: str = "", lines=None):
    if lines is None:
        lines = []
    entries = list(node.items())
    for idx, (name, child) in enumerate(entries):
        is_last = (idx == len(entries) - 1)
        branch = "└── " if is_last else "├── "
        lines.append(f"{prefix}{branch}{name}")
        if isinstance(child, dict):
            extension = "    " if is_last else "│   "
            flatten_ascii_tree(child, prefix + extension, lines)
    return lines

# ───────────────────────
# Main
# ───────────────────────
def main():
    # Prompt for project path
    raw = input("Enter path to your Java project (relative or absolute): ").strip()
    root = Path(raw).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        print(f"Error: `{root}` is not a valid directory.", file=os.sys.stderr)
        return

    structure = build_structure(root)

    # JSON output
    if PRINT_JSON:
        print(json.dumps({root.name: structure}, indent=2))
    if WRITE_JSON_FILE:
        json_path = root / "structure.json"
        with open(json_path, "w", encoding="utf-8") as jf:
            json.dump({root.name: structure}, jf, indent=2)
        print(f"Written JSON structure to {json_path}")

    # ASCII-art tree
    if PRINT_TREE:
        print(f"{root.name}/")
        print_ascii_tree(structure)
    if WRITE_TREE_FILE:
        lines = [f"{root.name}/"] + flatten_ascii_tree(structure)
        tree_path = root / "structure_tree.txt"
        with open(tree_path, "w", encoding="utf-8") as tf:
            tf.write("\n".join(lines))
        print(f"Written ASCII tree to {tree_path}")

if __name__ == "__main__":
    main()
