#!/bin/sh
# Commit and push the mirror's data files. Refuses if anything outside data/ changed,
# so a sync run can never alter the page code.
set -e
cd "$(dirname "$0")/.."
git add data
if git status --porcelain | grep -v '^.. data/' | grep -q .; then
  echo "REFUSED: changes outside data/:"; git status --porcelain | grep -v '^.. data/'; exit 1
fi
if git diff --cached --quiet; then echo "no changes"; exit 0; fi
git commit -q -m "data: sync from hub $(date -u +%Y-%m-%dT%H:%MZ)"
git push -q
echo "pushed"
