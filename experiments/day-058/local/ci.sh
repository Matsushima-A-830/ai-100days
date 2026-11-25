#!/bin/bash
# Same steps as .github/workflows/ci.yml, run on a writable copy of the repo
cp -r /src /w && cd /w || exit 1
pip install -q -e . ruff pytest >/dev/null 2>&1
echo '$ ruff check .'; ruff check . || exit 1
echo '$ pytest -q'; pytest -q -p no:cacheprovider; rc=$?
echo "Process completed with exit code $rc."; exit $rc
