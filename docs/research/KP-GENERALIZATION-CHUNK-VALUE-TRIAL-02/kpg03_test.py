# -*- coding: utf-8 -*-
"""API 0のoffline test(決定論部・安全装置)。実行: PYTHONUTF8=1 .venv\\Scripts\\python.exe kpg03_test.py"""
import os, sys, json, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kpg03_llm as L
import kpg03_methods as M

ok = 0
def check(name, cond):
    global ok
    print(("PASS " if cond else "FAIL ") + name)
    assert cond, name
    ok += 1

# 1. 出力上限・thinking明示の強制
for kw, name in ((dict(model="gpt-6-luna", user="x"), "max_out未指定は拒否"), (dict(model="gemini-3.8-flash", user="x", max_out=10), "gemini think_budget未指定は拒否")):
    try:
        L.call(kw.pop("model"), kw.pop("user"), None, **kw); check(name, False)
    except ValueError:
        check(name, True)

# 2. Cap超過で新規call拒否(API呼出前に拒否されることを確認。台帳は一時ファイル)
tmp = os.path.join(tempfile.mkdtemp(), "ledger.jsonl")
open(tmp, "w", encoding="utf-8").write(json.dumps({"cost_jpy": 121.0}) + "\n")
old = L.B.LEDGER; L.B.LEDGER = tmp; L.set_mock(False); L.B.LEDGER = tmp
try:
    L.call("gpt-6-luna", "x", None, max_out=10, tag="t"); check("Cap超過でCapReached", False)
except L.CapReached:
    check("Cap超過でCapReached", True)
open(tmp, "w", encoding="utf-8").write(json.dumps({"cost_jpy": 10.0}) + "\n")
L.PHASE_LIMIT = 5.0
try:
    L.call("gpt-6-luna", "x", None, max_out=10, tag="t"); check("phase停止点超過でCapReached", False)
except L.CapReached:
    check("phase停止点超過でCapReached", True)
L.PHASE_LIMIT = None; L.set_mock(True)

# 3. pick: 難易度はソート用のみ(easyも残る)・重複除去・上限
J = [dict(span="rely on", display_form="rely on", keep=True, difficulty="easy"), dict(span="blow a whistle", display_form="blow a whistle", keep=True, difficulty="advanced"),
     dict(span="rely on it", display_form="rely on", keep=True, difficulty="upper_intermediate"), dict(span="deep image", display_form="deep image", keep=False, difficulty="advanced")]
p = M.pick(J, 7)
check("pick: easyを除外しない・advanced先頭・重複(rely on)除去・keep=falseは除外", [c["span"] for c in p] == ["blow a whistle", "rely on"] or [c["span"] for c in p] == ["blow a whistle", "rely on it"])
check("pick: cap", len(M.pick(J, 1)) == 1)

# 4. ゲート: FREE_COMBINATION/WORD_ONLYのみ除外。OVER_GENERALIZEDやTOO_EASYは除外しない(記録のみ)
def fake_call(model, user, schema=None, **kw):
    n = 4
    codes = [("C", "OK"), ("F", "FREE_COMBINATION"), ("C", "OVER_GENERALIZED"), ("W", "WORD_ONLY")]
    vs = [{"id": i + 1, "verdict": "OK", "meaning_preserved": True, "gloss_consistent": True, "natural_headword": True, "issue": "", "fix_display_form": "", "fix_gloss_ja": "",
           "gate_cls": codes[i][0], "gate_code": codes[i][1]} for i in range(n)]
    return {"verdicts": vs}, {"model_id": "fake", "in": 1, "out": 1, "cost_jpy": 0, "sec": 0}
L_call = M.L.call; M.L.call = fake_call
items = [dict(span=s, sentence="s", display_form=s, gloss_ja="g", chunk_reason_ja="r") for s in ("take up a", "deep image", "set a limit", "red tape")]
log = {"stages": []}
fin = M.verify({"id": "t", "text": "x"}, items, log, tag="t", gate=True)
M.L.call = L_call
check("gate: FREE/WORD_ONLYのみ除外(OK・OVER_GENERALIZEDは残る)", [c["span"] for c in fin] == ["take up a", "set a limit"])
check("gate: 除外はlogに記録", len(log["gate_dropped"]) == 2)

# 5. 既定動作: 本ファイル群はProduction module(er*)をimportしない(Trial隔離)
bad = [m for m in sys.modules if m.startswith("er0") or m.startswith("er1")]
check("Production module(er*)非import", not bad)
print(f"ALL PASS ({ok})")
