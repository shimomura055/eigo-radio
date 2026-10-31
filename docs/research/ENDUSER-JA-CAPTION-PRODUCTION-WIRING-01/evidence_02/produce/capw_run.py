# ENDUSER-JA-CAPTION-PRODUCTION-WIRING-01 環境shim(処理は追加しない): cwd=wt_cap、.envは読まない。
# API 0の構造的担保: APIキーはダミー・ネットワークはdead proxy(localhostのみNO_PROXY) -> キャッシュミスがあれば呼出が失敗する(課金0)。
import importlib, os, sys
WT, MOD = sys.argv[1:3]
argv = sys.argv[3:]
sys.path.insert(0, WT)
os.chdir(WT)
os.environ["PYTHONUTF8"] = "1"
for k in ("OPENAI_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY", "ANTHROPIC_API_KEY", "ELEVENLABS_API_KEY"):
    os.environ[k] = "DUMMY-NO-API-CAPW"
os.environ["HTTPS_PROXY"] = os.environ["HTTP_PROXY"] = os.environ["ALL_PROXY"] = "http://127.0.0.1:9"
os.environ["NO_PROXY"] = os.environ["no_proxy"] = "127.0.0.1,localhost"
m = importlib.import_module(MOD)
sys.exit(m.main(argv))
