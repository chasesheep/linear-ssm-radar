#!/bin/bash
# Research Radar - Daily Auto-Run
# Runs at 08:00 CST, pushes to kimi-inbox/YYYY-MM-DD

set -euo pipefail

RADAR_DIR="/root/linear-ssm-radar"
ENV_FILE="/root/.openclaw/workspace/.env"
LOG_FILE="/tmp/radar-$(date +%Y%m%d).log"

exec >> "$LOG_FILE" 2>&1

echo "=== Radar Auto-Run: $(date '+%Y-%m-%d %H:%M:%S') ==="

# Load PAT
if [ -f "$ENV_FILE" ]; then
    export $(grep RESEARCH_RADAR_GITHUB_TOKEN "$ENV_FILE" | xargs)
fi

if [ -z "${RESEARCH_RADAR_GITHUB_TOKEN:-}" ]; then
    echo "ERROR: PAT not found in $ENV_FILE"
    exit 1
fi

cd "$RADAR_DIR"

# Pull latest main to avoid conflicts
git fetch origin main 2>/dev/null || true
git checkout main 2>/dev/null || git checkout -b main
git reset --hard origin/main 2>/dev/null || true

# Run scan
TODAY=$(date +%Y-%m-%d)
echo "Running scan for $TODAY..."
python3 scripts/daily_scan.py

# Safety check: no token in outputs
echo "Verifying no token leakage..."
if grep -rq "github_pat" data/ reports/ scripts/ 2>/dev/null; then
    echo "ERROR: Token found in output files, aborting push"
    exit 1
fi
if grep -rq "AHXKCEY" data/ reports/ scripts/ 2>/dev/null; then
    echo "ERROR: Token fragment found, aborting push"
    exit 1
fi

# Commit and push to inbox branch
BRANCH="kimi-inbox/$TODAY"
git checkout -b "$BRANCH" 2>/dev/null || git checkout "$BRANCH"

git add -A
git diff --cached --quiet && { echo "No changes to push"; exit 0; }

git commit -m "[radar] $TODAY daily scan (auto)"

# Push with token via askpass
cat > /tmp/radar_askpass.sh << EOF
#!/bin/bash
echo "$RESEARCH_RADAR_GITHUB_TOKEN"
EOF
chmod 700 /tmp/radar_askpass.sh

GIT_ASKPASS=/tmp/radar_askpass.sh git push origin "$BRANCH"

echo "=== Push complete: $BRANCH ==="
rm -f /tmp/radar_askpass.sh
