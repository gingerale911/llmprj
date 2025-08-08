#!/bin/zsh
# Install nvm in current venv
mkdir -p "$VIRTUAL_ENV/.nvm"
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | NVM_DIR="$VIRTUAL_ENV/.nvm" bash

# Load nvm
export NVM_DIR="$VIRTUAL_ENV/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Install Node.js LTS & Vercel CLI
nvm install --lts
npm install vercel

# Add auto-load to venv's activate script
echo '
export NVM_DIR="$VIRTUAL_ENV/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
' >> "$VIRTUAL_ENV/bin/activate"

echo "✅ Node + npm + Vercel installed inside venv"
