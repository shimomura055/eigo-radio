# -*- coding: utf-8 -*-
"""API 0のoffline test(決定論部・安全装置・Trial隔離)。実行: PYTHONUTF8=1 .venv\\Scripts\\python.exe kpg04_test.py"""
import os, sys, json, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.pop("KPG4_CAP", None)
import kpg04_llm as L
import kpg04_methods as M


def _no_network(*a, **k):                     # 安全網: testがどう間違えても実APIへ到達させない
    raise AssertionError("testが実API呼出に到達した")


L.B.call = _no_network

ok = 0


def check(name, cond):
    global ok
    print(("PASS " if cond else "FAIL ") + name)
    assert cond, name
    ok += 1


# 1. 既定Cap=0: 有料call(mockでない)はAPI呼出前に拒否
check("KPG4_CAP既定は0", L.CAP == 0.0)
L.set_mock(False)
try:
    L.call("gpt-6-luna", "x", None, max_out=10, tag="t"); check("Cap0で有料call拒否", False)
except L.CapReached:
    check("Cap0で有料call拒否(CapReached)", True)
try:
    L.call_ds("deepseek-v4-pro", "x", tag="t"); check("Cap0でds拒否", False)
except L.CapReached:
    check("Cap0でdeepseek call拒否", True)
# 2. 出力上限・thinking明示の強制
for kw, name in ((dict(model="gpt-6-luna", user="x"), "max_out未指定は拒否"), (dict(model="gemini-3.8-flash", user="x", max_out=10), "gemini think_budget未指定は拒否")):
    try:
        L.call(kw.pop("model"), kw.pop("user"), None, **kw); check(name, False)
    except ValueError:
        check(name, True)
# 3. Cap>0でも累計/フェーズ停止点超過で拒否(台帳は一時ファイル)
tmp = os.path.join(tempfile.mkdtemp(), "ledger.jsonl")
open(tmp, "w", encoding="utf-8").write(json.dumps({"cost_jpy": 50.0}) + "\n")
L.B.LEDGER = tmp; L.CAP = 40.0
try:
    L.call("gpt-6-luna", "x", None, max_out=10, tag="t"); check("Cap超過拒否", False)
except L.CapReached:
    check("累計>=Capで拒否", True)
L.CAP = 100.0
L.PHASE_LIMIT = 50.0     # 累計50に対しphase停止点50 -> 到達で拒否
try:
    L.call("gpt-6-luna", "x", None, max_out=10, tag="t"); check("phase停止点到達で拒否", False)
except L.CapReached:
    check("phase停止点到達で拒否", True)
L.CAP = 0.0; L.PHASE_LIMIT = None; L.set_mock(True)
# 4. 旧kpg03_llmのcall(CAP=120/別台帳)は無効化され、M3はkpg04のLへ差替済み
check("kpg03_llm.call無効化", not callable(getattr(L.L3, "call", None)) or L.L3.call is L._forbidden)
check("M3.LがKPG-04のLへ差替", M.M3.L is L)
try:
    L.L3.call("gpt-6-luna", "x", None, max_out=1); check("kpg03 call禁止", False)
except RuntimeError:
    check("kpg03_llm.callは例外", True)

# 5. reconcile(決定論調停)
check("reconcile: someone/somethingのみ違い -> headword採用", M.reconcile("hear something out", "hear someone out") == ("hear someone out", "SLOT_TYPE_OVERRIDDEN"))
check("reconcile: 同一", M.reconcile("take something away from", "take something away from")[1] == "SAME")
check("reconcile: 構造違いはFRAME_MISMATCH(formは変更しない)", M.reconcile("take away from", "take something away from") == ("take away from", "FRAME_MISMATCH"))
check("reconcile: somebody正規化", M.reconcile("let someone down", "let somebody down")[1] == "SAME")

# 6. flag_item(決定論flag): 既知の2誤りが検出され、無関係な通常項目は検出されない
f1 = M.flag_item(dict(span="hear it out", tokens=[(1, "CORE", "hear"), (2, "SLOT_THING", ""), (3, "CORE", "out")]))
f2 = M.flag_item(dict(span="take points away from", tokens=[(1, "CORE", "take"), (2, "SLOT_THING", ""), (3, "CORE", "away"), (4, "CORE", "from")], display_form_pre_fix="take something away from"))
f3 = M.flag_item(dict(span="the sales pitch", tokens=[(1, "DROP", ""), (2, "CORE", "sales"), (3, "CORE", "pitch")]))
f4 = M.flag_item(dict(span="narrow down the source", tokens=[(1, "CORE", "narrow"), (2, "CORE", "down"), (3, "DROP", ""), (4, "DROP", "")]))
check("flag: hear it out -> PRONOUN_SLOT", f1 == ["PRONOUN_SLOT"])
check("flag: take points away from -> VER_FIXED_FORM", f2 == ["VER_FIXED_FORM"])
check("flag: 冠詞のみのDROPはflagなし", f3 == [])
check("flag: 内容語DROP(narrow down the source)は検査対象", f4 == ["CONTENT_DROPPED"])

# 7. score_probe / probes.json整合
probes = json.load(open(os.path.join(HERE, "kpg04_probes.json"), encoding="utf-8"))
check("probe 48件・8種別x6", len(probes) == 48 and len({p["type"] for p in probes}) == 8)
check("probe: span/sentence/context整合", all(p["span"].lower() in p["sentence"].lower() and p["sentence"] in p["context"] for p in probes))
check("probe: ok/ngの重複なし", all(not (set(p["ok"]) & set(p["ng"])) for p in probes))
P = {p["id"]: p for p in probes}
check("score: hear someone out PASS / hear something out FAIL", M.score_probe({"display_form": "hear someone out"}, P["AP1"]) == "PASS" and M.score_probe({"display_form": "hear something out"}, P["AP1"]) == "FAIL")
check("score: set a limit PASS(修飾語削除はNGにしない) / 未知形REVIEW", M.score_probe({"display_form": "set a limit"}, P["MO1"]) == "PASS" and M.score_probe({"display_form": "set limits"}, P["MO1"]) == "REVIEW")
check("score: take away from FAIL", M.score_probe({"display_form": "take away from"}, P["SS1"]) == "FAIL")

# 8. local_context
txt = "A. B is here. C goes there. D comes back. E ends."
check("local_context: 前後1文", M.local_context(txt, "C goes there.") == "B is here. C goes there. D comes back.")

# 9. generalize5: tokensがSLOT_THINGでもheadword_frameがsomeoneなら見出しの標準用法を採用 / fake LLMで検証・検査経路
def fake_call(model, user, schema=None, **kw):
    n = schema["schema"]["properties"]
    meta = {"model_id": "fake", "in": 1, "out": 1, "cost_jpy": 0, "sec": 0}
    nm = schema["name"]
    if nm == "kp_gen_tokens5":
        return {"items": [
            {"id": 1, "source_sense_ja": "s", "arg_notes": [], "headword_frame": "hear someone out", "frame_change": ["PERSON_OVERRIDE"],
             "tokens": [{"n": 1, "label": "CORE", "lemma": "hear"}, {"n": 2, "label": "SLOT_THING", "lemma": ""}, {"n": 3, "label": "CORE", "lemma": "out"}], "gloss_ja": "(人)の言い分を最後まで聞く", "sense_note_ja": "", "note_ja": ""},
            {"id": 2, "source_sense_ja": "s", "arg_notes": [], "headword_frame": "take something away from", "frame_change": ["OBJECT_SLOT"],
             "tokens": [{"n": 1, "label": "CORE", "lemma": "take"}, {"n": 2, "label": "SLOT_THING", "lemma": ""}, {"n": 3, "label": "CORE", "lemma": "away"}, {"n": 4, "label": "CORE", "lemma": "from"}], "gloss_ja": "〜から…を差し引く", "sense_note_ja": "", "note_ja": ""}]}, meta
    if nm == "kp_verify5":
        return {"verdicts": [
            {"id": 1, "verdict": "OK", "meaning_preserved": True, "gloss_consistent": True, "natural_headword": True, "issue": "", "fix_display_form": "", "fix_gloss_ja": "", "source_sense_ja": "s", "argument_type_ok": True, "frame_preserved": "SAME"},
            {"id": 2, "verdict": "FIX", "meaning_preserved": True, "gloss_consistent": True, "natural_headword": False, "issue": "目的語を除く", "fix_display_form": "take away from", "fix_gloss_ja": "損なう", "source_sense_ja": "s", "argument_type_ok": True, "frame_preserved": "OBJECT_DROPPED_SENSE_CHANGED"}]}, meta
    if nm == "kp_check5":
        return {"checks": [{"id": 1, "context_sense_ja": "c", "example_en": "e", "relation": "SAME", "fix_display_form": "", "fix_gloss_ja": "", "reason_ja": ""},
                           {"id": 2, "context_sense_ja": "c", "example_en": "e", "relation": "SENSE_SHIFT", "fix_display_form": "take something away from", "fix_gloss_ja": "〜から…を差し引く", "reason_ja": "別見出し"}]}, meta
    raise AssertionError(nm)


real_call = L.call
L.call = fake_call
case = {"id": "t", "text": "x"}
cands = [dict(span="hear it out", sentence="s1", chunk_type="phrasal_verb", chunk_reason_ja="", cls="C", difficulty="upper_intermediate", keep=True),
         dict(span="take points away from", sentence="s2", chunk_type="phrasal_verb", chunk_reason_ja="", cls="C", difficulty="upper_intermediate", keep=True)]
log = {"stages": []}
items = M.generalize5(case, cands, log, tag="t")
check("generalize5: tokens=SLOT_THINGでも見出しの標準用法(someone)を採用しlogに記録", items[0]["display_form"] == "hear someone out" and len(log["slot_type_overridden"]) == 1)
check("generalize5: take something away from", items[1]["display_form"] == "take something away from")
fin = M.verify5(case, items, log, tag="t")
# 目的語を除くFIX(frame_preserved=OBJECT_DROPPED_SENSE_CHANGED)は、display_checkを通っても『意味変化』として扱い本文の形へ戻る…ではなく、FIXが採用された場合はflag->検査へ
check("verify5: 目的語を除くFIXは採用されるがVER_FIXED_FORM flagになる", fin[1]["display_form"] == "take away from" and "VER_FIXED_FORM" in M.flag_item(fin[1]))
log2 = {"stages": []}
fin = M.run_check(case, fin, log2, tag="t", scope="flagged")
check("run_check(flagged): SENSE_SHIFTを検出しfix_display_formで復元", fin[1]["display_form"] == "take something away from")
check("run_check(flagged): flagなし(hear someone outはPRONOUN_SLOT? tokens=SLOT_THINGのためflag)対象数", len(log2["check_targets"]) == 2)
L.call = real_call

# 10. Production module非import(Trial隔離)
bad = [m for m in sys.modules if m.startswith("er0") or m.startswith("er1")]
check("Production module(er*)非import", not bad)
print(f"ALL PASS ({ok})")
