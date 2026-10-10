#!/bin/bash
# usage: run_levels.sh <level> [...]  各レベルの9セルを並列(最大9)で実行。セルごとに別ファイル(書込衝突なし)
HERE="$(cd "$(dirname "$0")" && pwd)"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
for lv in "$@"; do
  for th in streaming_price space_weapons byd_recall; do for m in gpt-6-luna gpt-6.1-sol gpt-6-astra; do echo "$lv $th $m"; done; done
done | xargs -P 9 -L 1 sh -c 'python "'"$HERE"'/antenna_driver.py" "$0" "$1" "$2" 2>&1 | tail -3'
