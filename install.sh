#!/usr/bin/env bash
set -e

INSTALL_DIR="$HOME/airtune"
BIN_PATH="/usr/local/bin/airtune"

echo "Installing Airtune..."

# Copy files
mkdir -p "$INSTALL_DIR"
cp "$(dirname "$0")/airtune.py" "$INSTALL_DIR/airtune.py"
cp "$(dirname "$0")/server.py"  "$INSTALL_DIR/server.py"
cp "$(dirname "$0")/index.html" "$INSTALL_DIR/index.html"
chmod +x "$INSTALL_DIR/airtune.py"

# Symlink
if [ -L "$BIN_PATH" ] || [ -f "$BIN_PATH" ]; then
  rm -f "$BIN_PATH"
fi
ln -s "$INSTALL_DIR/airtune.py" "$BIN_PATH"

echo "  ✓ Installed to $INSTALL_DIR"
echo "  ✓ Symlinked airtune → $BIN_PATH"
echo ""
echo "Run: airtune install"
echo "     airtune start"
echo "     airtune recognize https://stream.example.com/radio"
