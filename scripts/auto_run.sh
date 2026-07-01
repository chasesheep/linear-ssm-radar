# Research Radar - Daily Auto-Run (No token logic, no push)
# Runs at 08:00 CST
# Push is handled by an external script NOT in git

set -euo pipefail

RADAR_DIR="/root/linear-ssm-radar"
ENV_FILE="/root/.openclaw/workspace/.env"
LOG_FILE="/tmp/radar-$(date +%Y%m%d).log"

exec >> "$LOG_FILE" 2>&1

echo "=== Radar Auto-Run: $(date '+%Y-%m-%d %H:%M:%S') ==="

cd "$RADAR_DIR"

# Pull latest main to avoid conflicts
git fetch origin main 2>/dev/null || true
git checkout main 2>/dev/null || git checkout -b main
git reset --hard origin/main 2>/dev/null || true

# Run scan
TODAY=$(date +%Y-%m-%d)
echo "Running scan for $TODAY..."
python3 scripts/daily_scan.py

# Commit locally (push handled externally)
BRANCH="kimi-inbox/$TODAY"
git checkout -b "$BRANCH" 2>/dev/null || git checkout "$BRANCH"

git add -A
git diff --cached --quiet && { echo "No changes to commit"; exit 0; }

git commit -m "[radar] $TODAY daily scan (auto)"

echo "=== Scan complete. Run /root/linear-ssm-radar/scripts/push.sh to push ==="
