#!/usr/bin/env bash
# Sugeneruoja svetainę ir paskelbia ją į šaką „hosting“ (iš jos Hostinger pasiima failus).
# Naudojimas: ./deploy.sh [YYYY-MM-DD]
set -euo pipefail
cd "$(dirname "$0")"
UPD="${1:-$(date +%F)}"
python3 build.py --owner jokubasmail123-cmd --updated "$UPD"
git fetch -q origin hosting 2>/dev/null || true
rm -rf .hosting
if git rev-parse -q --verify origin/hosting >/dev/null; then
  git worktree add -q -f .hosting origin/hosting 2>/dev/null || git worktree add -q -f -B hosting .hosting origin/hosting
  (cd .hosting && git checkout -q -B hosting)
else
  git worktree add -q --detach .hosting
  (cd .hosting && git checkout -q --orphan hosting && git rm -rqf . >/dev/null 2>&1 || true)
fi
find .hosting -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
cp -a public/. .hosting/
cd .hosting
git add -A
if git diff --cached --quiet; then echo "Svetainėje pakeitimų nėra"; else
  git -c user.name="jokubasmail123-cmd" -c user.email="jokubasmail.123@gmail.com" commit -qm "Svetainė $UPD"
  git push -q origin hosting
  echo "Paskelbta į šaką hosting"
fi
cd .. && git worktree remove --force .hosting
