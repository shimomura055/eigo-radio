# ENDUSER-CLICK-HIGHLIGHT-NO-SEEK-01 環境shim(処理は追加しない): コードは一時worktree(WT=origin/mainのrev01-h)を優先し、cwd=主worktree(既存run dataの相対pathを解決)、.envは主worktreeから読む。
# 使い方: python runner_shim.py <WT> <MAIN> <module> [CLI引数...]
import importlib, os, sys
WT, MAIN, MOD = sys.argv[1:4]
argv = sys.argv[4:]
sys.path.insert(0, WT)
os.chdir(MAIN)
os.environ.setdefault("PYTHONUTF8", "1")
from dotenv import load_dotenv
load_dotenv(os.path.join(MAIN, ".env"))
if os.environ.get("ECH_KEEP_CWD"):   # er019はmain()冒頭でos.chdir(ROOT=WT)する。既存run dataは主worktree(相対path)にあるためcwdを固定(コード自体はWTのrev01-h)
    os.chdir = lambda p: None
m = importlib.import_module(MOD)
sys.exit(m.main(argv))
