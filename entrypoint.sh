#!/bin/sh
set -e

# Start Scrapyd in the background (it reads /app/scrapyd.conf)
scrapyd &
SCRAPYD_PID=$!
trap 'kill $SCRAPYD_PID' TERM INT

# Wait until the API answers
python - <<'EOF'
import time, urllib.request
for _ in range(30):
    try:
        urllib.request.urlopen("http://localhost:6800/daemonstatus.json")
        break
    except Exception:
        time.sleep(1)
else:
    raise SystemExit("Scrapyd did not start in time")
EOF

# Deploy the project, then keep the container alive
scrapyd-deploy
echo "Project deployed. Scrapyd is ready on port 6800."
wait $SCRAPYD_PID