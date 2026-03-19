#!/usr/bin/env bash
set -e

INSTALL_DIR="$HOME/airtune"
BIN_PATH="/usr/local/bin/airtune"

echo "Uninstalling Airtune..."

# Remove symlink
if [ -L "$BIN_PATH" ]; then
  rm -f "$BIN_PATH"
  echo "  ✓ Removed $BIN_PATH"
fi

# Optionally remove install dir
read -r -p "Remove $INSTALL_DIR ? [y/N] " confirm
if [[ "$confirm" =~ ^[Yy]$ ]]; then
  rm -rf "$INSTALL_DIR"
  echo "  ✓ Removed $INSTALL_DIR"
else
  echo "  - Kept $INSTALL_DIR"
fi

echo "Done."
