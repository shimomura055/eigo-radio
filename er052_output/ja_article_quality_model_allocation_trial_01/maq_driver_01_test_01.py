# -*- coding: utf-8 -*-
"""maq_driver_01_test_01.py  無課金ドリフト検査(stub client のみ。API呼出なし)。
A構成(Luna/Astra)で Production run_w1_writer と driver の request列(model/effort/messages/Prompt本文/追加kwarg)と出力ファイルが完全一致すること、
記号QA分岐(R0再生成/R2再実行/STOP)が同一であること、B3呼出がProduction呼出と同一であること、予算guard・単価再計算・module sha を検査する。
実行: .venv/Scripts/python.exe -X utf8 maq_driver_01_test_01.py"""
import copy
import hashlib
import json
import os
import shutil
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import maq_driver_01 as D   # noqa: E402

w1, b3, safety = D.w1, D.b3, D.safety
FAIL = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  {detail}" if (detail and not cond) else ""))
    if not cond:
        FAIL.append(name)


def _usage(i, o):
    return types.SimpleNamespace(input_tokens=i, output_tokens=o, input_tokens_details=types.SimpleNamespace(cached_tokens=0),
                                 output_tokens_details=types.SimpleNamespace(reasoning_tokens=o // 2))


class Stub:
    """リクエストから決定論で応答を作る stub。symbol_r0 / symbol_r2 = 最初のN回の該当stageで禁止記号(括弧)を混ぜる。"""

    def __init__(self, r0_bad=0, r2_bad=0, model_override=None):
        self.calls, self.responses, self.r0_bad, self.r2_bad, self.mo = [], self, r0_bad, r2_bad, model_override
        self.n_r0 = self.n_r2 = 0

    def create(self, **kw):
        self.calls.append(copy.deepcopy(kw))
        msgs = kw["input"]
        user = msgs[-1]["content"]
        h = hashlib.sha256(user.encode()).hexdigest()[:8]
        if "text" in kw:   # B3
            ids = b3.extract_fact_ids_from_ledger(user)
            sel = ids[:2]
            out = {"selected_storyline": "テストのストーリー", "selected_fact_ids": sel, "selected_fact_brief": "テストのストーリー\n\n" + "。".join(f"{i}の文" for i in sel),
                   "recheck_note": None,
                   "fact_tests": [{"fact_id": i, "test1_answer": "NO", "test2_answer": "YES", "test3_answer": "YES", "test4_answer": "NO",
                                   "decision": "selected" if i in sel else "excluded", "reason": "r"} for i in ids]}
            text = json.dumps(out, ensure_ascii=False)
        elif msgs[0]["role"] == "developer":   # R0
            self.n_r0 += 1
            bad = "（補足）" if self.n_r0 <= self.r0_bad else ""
            text = f"# タイトル{h}\n\n本文です{bad}。【事実1】\n\n続きの文です。【事実1,事実2】\n"
        else:  # R1/R2
            self.n_r2 += 1 if user.startswith("以下の記事:\n\n# ") or True else 0
            is_r2 = "**" in user   # R1出力に ** を混ぜ、R2入力かどうかを判別
            bad = ""
            if is_r2:
                self._r2_seen = getattr(self, "_r2_seen", 0) + 1
                bad = " a/b" if self._r2_seen <= self.r2_bad else ""
            text = f"# 改題{h}\n\n**強調**の本文——つづき…です{bad}\n\n- 箇条です\n"
        n = len(self.calls)
        return types.SimpleNamespace(id=f"resp_{n}", model=self.mo or kw["model"], output_text=text, usage=_usage(100 + n, 200 + n))


def prep(tmp, name):
    od = os.path.join(tmp, name)
    D.prepare_inputs(od, copy_b3_from=D.A_RUN)
    D.produce_annotation(od)
    return od


def read(p):
    with open(p, "rb") as f:
        return f.read()


FILES = ["ja_writer/factlock/r0.md", "ja_writer/factlock/r0_with_tags.md", "ja_writer/factlock/r1.raw.md", "ja_writer/factlock/r1.p1.md",
         "ja_writer/factlock/r2.raw.md", "ja_writer/original.md", "ja_writer/revision1.md", "ja_writer/revision2.md"]


def compare(name, r0_bad=0, r2_bad=0):
    tmp = tempfile.mkdtemp(prefix="maq_test_")
    try:
        pa, pb = prep(tmp, "prod"), prep(tmp, "drv")
        s1, s2 = Stub(r0_bad, r2_bad), Stub(r0_bad, r2_bad)
        e1 = e2 = None
        try:
            w1.run_w1_writer(pa, client=s1)
        except Exception as e:  # noqa: BLE001
            e1 = e
        guard = D.GuardedClient(s2, "A", None, None, verbose=False)
        try:
            D.run_writer(pb, guard, D.LUNA, D.ASTRA, D.ASTRA)
        except Exception as e:  # noqa: BLE001
            e2 = e
        check(f"[{name}] request列 完全一致({len(s1.calls)}件)", s1.calls == s2.calls and len(s1.calls) > 0)
        check(f"[{name}] 例外型・findings一致", type(e1) is type(e2) and (getattr(e1, "findings", None) == getattr(e2, "findings", None)),
              f"{e1!r} vs {e2!r}")
        for f in FILES:
            ea, eb = os.path.exists(os.path.join(pa, f)), os.path.exists(os.path.join(pb, f))
            same = ea == eb and (not ea or read(os.path.join(pa, f)) == read(os.path.join(pb, f)))
            check(f"[{name}] file一致 {f}", same)
        for extra in ("ja_writer/factlock/r2.rerun.raw.md", "ja_writer/audit/rejected_w1_r0_symbol.md", "ja_writer/audit/rejected_w1_r2_symbol.md"):
            ea, eb = os.path.exists(os.path.join(pa, extra)), os.path.exists(os.path.join(pb, extra))
            check(f"[{name}] 分岐file有無一致 {extra}", ea == eb)
        # request中の各kwargキー集合(追加kwarg無し)
        keys = {tuple(sorted(c)) for c in s2.calls}
        check(f"[{name}] kwarg集合=model/reasoning/inputのみ", keys == {("input", "model", "reasoning")}, str(keys))
        check(f"[{name}] developerはR0(+R0再生成)のみ", all((c["input"][0]["role"]=="developer")==("[ニュース]" in c["input"][-1]["content"]) for c in s2.calls))
        return s1, s2, e1, e2
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    print("== 1. A構成 stub等価(Production run_w1_writer vs driver) ==")
    compare("normal")
    s1, s2, e1, e2 = compare("R0再生成", r0_bad=1)
    check("R0再生成が実際に発火(calls=R0,R0b,R1,R2=4)", len(s1.calls) == 4, str(len(s1.calls)))
    s1, s2, e1, e2 = compare("R2再実行", r2_bad=1)
    check("R2再実行が実際に発火(calls=R0,R1,R2,R2b=4)", len(s1.calls) == 4, str(len(s1.calls)))
    s1, s2, e1, e2 = compare("R0再生成後も残存STOP", r0_bad=2)
    check("R0 STOP例外", isinstance(e1, w1.JASymbolCheckStopError) and isinstance(e2, w1.JASymbolCheckStopError))
    s1, s2, e1, e2 = compare("R2再実行後も残存STOP", r2_bad=2)
    check("R2 STOP例外", isinstance(e1, w1.JASymbolCheckStopError) and isinstance(e2, w1.JASymbolCheckStopError))

    print("== 2. B3呼出: driver(guard経由) vs Production呼出 ==")
    tmp = tempfile.mkdtemp(prefix="maq_test_b3_")
    try:
        od = os.path.join(tmp, "x")
        D.prepare_inputs(od)
        led = w1.rdt(os.path.join(od, "research_ledger", "verified_fact_ledger.txt"))
        sa, sb = Stub(), Stub()
        b3.run_storyline_b3_selection(sa, D.TOPIC, led, model=D.jaw.vfl01.MODEL, effort=D.jaw.vfl01.REASONING_EFFORT)
        g = D.GuardedClient(sb, "A", None, None, verbose=False)
        D.run_b3_stage(g, od, D.LUNA)
        check("B3 request完全一致(Production呼出と)", sa.calls == sb.calls and len(sa.calls) == 1)
        check("B3 modelはLuna指定時Productionと一致", D.jaw.vfl01.MODEL == D.LUNA)
        check("B3 成果物(selected_brief/evidence/runtime_evidence/full_ledger)生成", all(os.path.exists(os.path.join(od, "storyline_b3", n)) for n in
              ("selected_brief.md", "fact_selection_evidence.json", "runtime_evidence.json", "full_ledger.json")))
        for m, in ((D.ASTRA,), (D.SOL,)):
            s = Stub()
            D.run_b3_stage(D.GuardedClient(s, "X", None, None, verbose=False), od, m)
            c0 = s.calls[0]
            ref = sa.calls[0]
            same = {k: v for k, v in c0.items() if k != "model"} == {k: v for k, v in ref.items() if k != "model"} and c0["model"] == m
            check(f"B3 model差替({m})のみ差分(Prompt/schema/effort同一)", same)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("== 3. Prompt sha / module sha ==")
    vs = w1.verbatim_shas()
    exp = {"USER_TMPL": "313120e94232497290e7efac2df1210dc628a8a1b497bb04e7174b5a98442f7f", "R0_PROMPT": "6108a7cddaa9eaf31262354ba32d33e4683ccaf810d861f27e3dcc8972028366",
           "DEVELOPER_MESSAGE": "d1fbb04224d346e79c588b8e69da4dcfe26e758ceefc71aa83d13ff7f216ed8d",
           "SYMBOL_PREVENTION_BLOCK_JA": "0629ab47a18ccb986844d8cff4ea087a9690eb8a7b8aefb28039496eec603b73",
           "CONCRETENESS_CONTROL_AN3_BLOCK": "067030ff53ecb76a4d1477a3deace07b3e1fac438a33cb873edbe045cf6927fe",
           "R0_BLOCK": "74b948719e14fd7184ff3719d36639ede7905e45cef95b97c1cca1a5638b2bf1"}
    for k, v in exp.items():
        check(f"sha {k}", vs[k] == v)
    ps = b3.prompt_shas()
    check("sha B3 developer", ps["developer_message_sha256"] == "b4391b0387c54d39cf2ed095e7c00e028b13f173065ed0077b3a16f0fe37981a")
    check("sha B3 user template", ps["user_prompt_template_sha256"] == "d6fe9bc33ceccf4c4af3a44ce12b9d83ef7c2efe04de4dfbb2cf17adb02ff333")
    check("sha B3 fact test", ps["fact_test_definitions_sha256"] == "91513c8999a63439adb40d5c28a253e4cdbb438228ba1deda199d2ae6c6c5a8a")
    schema_sha = hashlib.sha256(json.dumps(b3.STORYLINE_B3_JSON_SCHEMA, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    check("sha B3 json schema(参考)", schema_sha == "ccfef73de9a12a232284786d9a52d935fcb3d66357e7f123febd2665c4903d51", schema_sha)
    ms = D.module_shas()
    expm = {"er053_family_x_factlock_ja_writer_01.py": "87339033ee0d8e1b84a989fad73819012e25d6b5ad9beac1a38ca4e93f2e4a38",
            "er019_family_x_storyline_b3_fact_selection_01.py": "93d0e31e735057ae874bbf27be48449fdd5bd5188e535b0a280eada9d314b758",
            "er053_b3_deterministic_producer_01.py": "8899d0fa4a9b2274fcd79165b447ab02988d40f799cbca01e06df51a6f7155f2",
            "er053_b3_annotation_contract_01.py": "5f4c725e0b332e028b8285389532dedc28e067f29caf6c63863b0be4f0017885",
            "er019_family_x_ja_writer_o_r1_r2_01.py": "a696d8f261033bc6d49054ce9805c32479abfd0b23825c21f93c5365d21cb8b0",
            "er006_model_routing_contract_01.py": "438df87d959fad3af7085c198c09bd2344d5ed308c98d78e574583373ab5c285"}
    for k, v in expm.items():
        check(f"module sha {k}", ms[k] == v)

    print("== 4. 単価再計算(A既存実測=35.645円) ==")
    tmp = tempfile.mkdtemp(prefix="maq_test_a_")
    try:
        u = D.prepare_a(out_root=tmp)
        check("A usage合計 35.645円(±0.01)", abs(u["total"]["jpy"] - 35.645) < 0.01, str(u["total"]))
        check("A R2 = 既存revision2とバイト一致", read(os.path.join(tmp, "A", "ja_writer", "revision2.md")) == read(os.path.join(D.A_RUN, "ja_writer", "revision2.md")))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("== 5. 予算guard ==")
    g = D.GuardedClient(Stub(), "C", 1.0, None, verbose=False)
    with D.cl.logging_context("t", "w1_r0"):
        try:
            g.create(model=D.ASTRA, reasoning={"effort": "high"}, input=[{"role": "user", "content": "x"}])
            check("cap超過見込みでBudgetStop(Astra R0 est>1円)", False)
        except D.BudgetStop:
            check("cap超過見込みでBudgetStop(Astra R0 est>1円)", True)
    check("BudgetStop時にAPI(stub)未呼出", len(g._real.calls) == 0)
    est = {m: {s: round(D.conservative_estimate_jpy(s, m), 2) for s in ("storyline_b3", "w1_r0", "w1_astra_r1", "w1_astra_r2")} for m in (D.LUNA, D.ASTRA, D.SOL)}
    print("   保守見積(x1.5, JPY):", json.dumps(est))
    for arm, cfg in D.ARMS.items():
        if cfg["cap"] is None:
            continue
        stages = [("storyline_b3", cfg["b3"]), ("w1_r0", cfg["r0"]), ("w1_astra_r1", cfg["r1"]), ("w1_astra_r2", cfg["r2"])]
        tot = sum(D.conservative_estimate_jpy(s, m) for s, m in stages if m)
        check(f"事前ゲート: {arm}案 保守見積合計{tot:.1f} <= cap{cfg['cap']}", tot <= cfg["cap"])
    check("事前ゲート: 案cap合計(C+D+E)<=250", sum(c["cap"] for c in D.ARMS.values() if c["cap"]) <= D.TOTAL_CAP_JPY)

    print("== 6. 互換エラー(400)でCompatStop・以後API不呼出 ==")

    class Rej(Stub):
        def create(self, **kw):
            e = Exception("unsupported")
            e.status_code = 400
            self.calls.append(1)
            raise e
    g = D.GuardedClient(Rej(), "E", 45.0, None, verbose=False)
    with D.cl.logging_context("t", "storyline_b3"):
        for _ in range(2):
            try:
                g.create(model=D.SOL, reasoning={"effort": "high"}, text={}, input=[{"role": "user", "content": "x"}])
            except Exception as e:  # noqa: BLE001
                last = e
    check("400後は2回目でAPIを呼ばない(CompatStop)", isinstance(last, D.CompatStop) and len(g._real.calls) == 1)

    print("\nRESULT:", "ALL_PASS" if not FAIL else f"FAIL({len(FAIL)}): {FAIL}")
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
