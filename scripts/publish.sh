#!/usr/bin/env bash
# Merge hits → sites.json and push to GitHub Pages repo.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SHARE="${HOME}/.local/share/webcafe-emd"
python3 "$ROOT/scripts/merge_sites.py"
# Prefer dedicated clone; fall back to ROOT itself.
CLONE="${SHARE}/gh-pages-repo"
if [[ -d "$CLONE/.git" ]]; then
  DEST="$CLONE"
else
  DEST="$ROOT"
fi
mkdir -p "$DEST/data"
cp -f "$SHARE/site/sites.json" "$DEST/data/sites.json"
cp -f "$SHARE/site/meta.json" "$DEST/data/meta.json"
# keep index.html from repo if present
if [[ -f "$ROOT/index.html" && "$DEST" != "$ROOT" ]]; then
  cp -f "$ROOT/index.html" "$DEST/index.html"
fi
cd "$DEST"
git add data/sites.json data/meta.json index.html 2>/dev/null || git add data/sites.json data/meta.json
if git diff --cached --quiet; then
  echo "no changes"
  exit 0
fi
NEW=$(python3 -c "import json;print(json.load(open('data/meta.json'))['new_today'])")
TOTAL=$(python3 -c "import json;print(json.load(open('data/meta.json'))['site_count'])")
git -c user.name='webcafe-emd-radar' -c user.email='radar@users.noreply.github.com' \
  commit -m "chore: EMD sites ${NEW} new / ${TOTAL} total ($(date +%F))"
git push origin HEAD
echo "pushed pages"
