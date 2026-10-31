# ②再生成経路確認(API 0): 公開article.jsonのgenerated全partを、是正済みキャッシュの「コピー」に対し
# 本番translate_part(origin/main版)で再翻訳要求し、LLM呼出0・訳が公開dirと一致を確認する。LLMは呼ばれたら例外(=API 0を構造的に保証)。
import json, os, shutil, sys, tempfile
sys.path.insert(0, os.getcwd())
import er135_enduser_translate_01 as TR
cache_src, article_path, out = sys.argv[1:4]
art = json.load(open(article_path, encoding="utf-8"))
class NoLLM:
    calls = []
    n = 0
    def __call__(self, kind, prompt):
        NoLLM.n += 1
        raise RuntimeError("LLM call attempted (cache miss): " + kind)
tmp = tempfile.mkdtemp(); shutil.copy(os.path.join(cache_src, "ja_generated.json"), tmp)
rows = []; ok = True
for lv, L in art["levels"].items():
    for p in L["parts"]:
        if p.get("ja_source") != "generated": continue
        sents = [{"sid": s["sid"], "en": s["text"], "para": pi} for pi, pa in enumerate(p["paragraphs"]) for s in pa]
        r = TR.translate_part(f"{lv}:{p['key']}", sents, level=lv, family="X", cache_dir=tmp, llm=NoLLM())
        got = TR.build_ja_fields(p["paragraphs"], r["ja"]) if r["coverage"]["complete"] else None
        same = bool(got) and got[0] == p["ja"] and got[1] == p["ja_align"]
        ok &= same
        rows.append({"level": lv, "part": p["key"], "cache_hits": r["meta"]["cache_hits"], "paragraphs": r["coverage"]["paragraphs"], "api_calls": r["meta"]["api_calls"], "equal_to_published_ja_and_align": same})
res = {"parts": rows, "llm_call_attempts": NoLLM.n, "all_equal": ok, "adv_19_ja0": next(p["ja"][0] for p in art["levels"]["adv"]["parts"] if p["key"] == "adv_19")}
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
shutil.rmtree(tmp)
