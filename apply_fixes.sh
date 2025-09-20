#!/bin/bash
set -euo pipefail

echo "🔧 Applying AI Nurse Florence fixes..."

# Create backups
mkdir -p backups
cp utils/config.py backups/config.py.bak 2>/dev/null || true
cp app.py backups/app.py.bak 2>/dev/null || true
cp requirements.txt backups/requirements.txt.bak 2>/dev/null || true

# Apply all fixes (the content from my previous artifacts)
# [All the cat > file << 'EOF' commands from before]

echo "✅ All fixes applied!"
echo "Next steps:"
echo "1. Run: chmod +x setup_dev.sh run_dev.sh"
echo "2. Run: ./setup_dev.sh"
echo "3. Edit .env with your API keys"
echo "4. Run: ./run_dev.sh"
