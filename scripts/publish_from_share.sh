#!/usr/bin/env bash
set -euo pipefail
SHARE="${HOME}/.local/share/webcafe-emd"
CLONE="${SHARE}/gh-pages-repo"
python3 "${SHARE}/merge_sites.py"
if [[ ! -d "$CLONE/.git" ]]; then
  git clone https://github.com/lilike/webcafe-emd.git "$CLONE"
fi
cd "$CLONE"
git pull --ff-only origin main
mkdir -p data
cp -f "$SHARE/site/sites.json" data/sites.json
cp -f "$SHARE/site/meta.json" data/meta.json
# refresh index from workspace copy if newer exists
if [[ -f /workspace/webcafe-emd/index.html ]]; then
  cp -f /workspace/webcafe-emd/index.html index.html
fi
git add data/sites.json data/meta.json index.html
if git diff --cached --quiet; then
  echo "no changes"
  exit 0
fi
NEW=$(python3 -c "import json;print(json.load(open('data/meta.json'))['new_today'])")
TOTAL=$(python3 -c "import json;print(json.load(open('data/meta.json'))['site_count'])")
git -c user.name='webcafe-emd-radar' -c user.email='radar@users.noreply.github.com' \
  commit -m "chore: EMD sites ${NEW} new / ${TOTAL} total ($(date +%F))"
git push origin HEAD
PAGE="https://lilike.github.io/webcafe-emd/"
echo "pushed $PAGE new=$NEW total=$TOTAL"
