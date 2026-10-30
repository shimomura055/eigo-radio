# 委任_02C 実TTS証跡用の環境shim(処理は一切追加しない)。一時worktreeのコードを使い、cwd/.envを主worktree(実wav・Master Audio Store・.envの場所)にする。
# 使い方: python sub02c_shim.py <WT> <MAIN> <module> [CLI引数...]  -> <module>.main(argv) をそのまま呼ぶ(CLIの引数・stage・STOP・Cap・RESTART_STORM検査は各runner本体のまま)。
import importlib
import os
import sys

WT, MAIN, MOD = sys.argv[1:4]
argv = sys.argv[4:]
sys.path.insert(0, WT)
os.chdir(MAIN)
os.environ.setdefault("PYTHONUTF8", "1")
from dotenv import load_dotenv  # noqa: E402
load_dotenv(os.path.join(MAIN, ".env"))   # find_dotenvは呼出ファイル基準で一時worktreeを探すため明示
m = importlib.import_module(MOD)
sys.exit(m.main(argv))
