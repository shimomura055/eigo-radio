# 診断(翻訳の数値不一致の原因): 失敗した段落だけ翻訳呼出→原文英文と訳の数値を並べる(verify呼出はしない)。cwd=MAIN(.env), code=WT。
import json, sys, tempfile
sys.path.insert(0, "C:/Users/tensh/AppData/Local/Temp/claude/C--Users-tensh-eigo-radio/7eda59a9-ca6c-4f6c-9eb5-2b973c0ca046/scratchpad/ejh03b")
import er135_enduser_translate_01 as TR
WT = "C:/Users/tensh/AppData/Local/Temp/claude/C--Users-tensh-eigo-radio/7eda59a9-ca6c-4f6c-9eb5-2b973c0ca046/scratchpad/ejh03b"
art = json.load(open(f"{WT}/user_test/family_z_yuki_onna_01/enduser/data/article.json", encoding="utf-8"))
want = {("std", "std_11"), ("adv", "adv_10"), ("adv", "adv_12"), ("adv", "adv_14")}
real = TR.DefaultLLM()
raw = []
def llm(kind, prompt):
    if kind == "verify":
        return '{"results": []}'
    t = real(kind, prompt); raw.append(t); return t
for lv, L in art["levels"].items():
    for p in L["parts"]:
        if (lv, p["key"]) not in want:
            continue
        sents = [dict(sid=s["sid"], en=s["text"], para=pi) for pi, pa in enumerate(p["paragraphs"]) for s in pa]
        d = tempfile.mkdtemp()
        raw.clear()
        try:
            TR.translate_part(p["key"], sents, level=lv, family="z", cache_dir=d, llm=llm)
        except Exception as e:
            print("EXC", type(e).__name__, str(e)[:100])
        print("=====", lv, p["key"], "sents", len(sents), "calls", len(raw))
        for t in raw[:1]:
            try:
                tr = json.loads(t)["translations"]
            except Exception:
                print(" unparsable", t[:200]); continue
            for s, o in zip(sents, tr):
                try:
                    TR.check_numbers(s["en"], o["ja"])
                except ValueError as e:
                    print(" NUMNG", s["sid"], "|", s["en"], "|", o["ja"], "|", e)
