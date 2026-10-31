# ENDUSER-JA-CAPTION-PRODUCTION-WIRING-01 6経路runner用shim(処理は追加しない)。
# コード=wt_cap(sys.path先頭)、cwd=主worktree(未追跡の依存資源とrun dataを解決。ENDUSER-CLICK-HIGHLIGHT-NO-SEEK-01と同方式。run dir内の変更はsnapshot前後差分で記録)、.envは読まない。
# API 0の構造的担保: APIキーはダミー・dead proxy(localhostのみNO_PROXY) -> キャッシュミスがあれば呼出が失敗する(課金0)。
import importlib, os, sys
WT, RR, MOD = sys.argv[1:4]
argv = sys.argv[4:]
sys.path.insert(0, WT)
os.chdir(RR)
os.environ["PYTHONUTF8"] = "1"
for k in ("OPENAI_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY", "ANTHROPIC_API_KEY", "ELEVENLABS_API_KEY"):
    os.environ[k] = "DUMMY-NO-API-CAPW"
os.environ["HTTPS_PROXY"] = os.environ["HTTP_PROXY"] = os.environ["ALL_PROXY"] = "http://127.0.0.1:9"
os.environ["NO_PROXY"] = os.environ["no_proxy"] = "127.0.0.1,localhost"
if os.environ.get("ECH_KEEP_CWD"):   # er019はmain()冒頭でos.chdir(ROOT=WT)する。run dataはrr(相対path)にあるためcwdを固定
    os.chdir = lambda p: None
m = importlib.import_module(MOD)
sys.exit(m.main(argv))
