# -*- coding: utf-8 -*-
"""FAMILY-Z-MELOS-SOL-B3Z-COMPARISON-TRIAL-01 委任_01: 『走れメロス』3方式比較Trial 生成driver。

【範囲】Trial専用(到達上限はVALIDATED止まり)。Production Writer/Prompt/Routing/CURRENT_SPEC/Family Z正式構成は変更しない。
        Production runnerからimportされない。TTS/Assemblyなし。
【方式】 (1)従来方式: 既存成果物(再生成しない) / (2)Sol変更のみ: Sol R0->R1->R2 / (3)Sol+B3Z: B3Z Brief -> Sol R0(+Brief)->R1->R2
        (2)(3)は同一の R0 Prompt(=既存Trial story_prompt.txt逐語)/R1/R2 Prompt・model・effort。差分はB3Z Brief有無のみ。
【Model】 Writer = gpt-6.1-sol(pricing登録は gpt-6.1-sol のみ、gpt-6-solは未登録。routing FAMILY_X_FACTLOCK_R0 値と一致を実行時assert。
          Trial専用: routingへ新keyは追加しない)。
【費用】 --approved-budget-jpy 必須(real)。1call前に累計+次call見積が上限超なら STOP。技術retryは各call最大1回(B3Zはschema/検証失敗のみ)。
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "er059_output", "melos_sol_b3z_trial_01")
SEED_DIR = os.path.join(ROOT, "er018_output", "fiction_external_seed_selection_criteria_trial_02", "stories", "03_japanese_lit_2")
PRICING = os.path.join(ROOT, "er005_output", "cost_baseline_01", "pricing_snapshot.json")
USD_JPY = 160.0
THEME_TAG = "FAMILY_Z_MELOS_SOL_B3Z_TRIAL_01"
WRITER_MODEL = "gpt-6.1-sol"
EFFORT = "high"          # 既存(1)(er018 step_story)と同じeffort=high。温度は推論モデルのため指定しない(全call同一)
WORD_RANGE = (280, 420)

# ---- B3Z (Family X B3 storyline_b3 の Family Z向け最小変更版。差分と理由は B3Z_DESIGN_01.md) ----
B3Z_DEVELOPER = (
    "You are the Editor for an English-learning magazine's Fiction article family. Before the Writer writes, you organize "
    "the Story Seed into a short Story Brief. You do not write the story itself."
)
B3Z_USER_TMPL = """Below is the Story Seed (and conversion plan) that the Writer will use to write a short A2-level English story.

{seed_block}

Your job: organize what this Seed's story needs, so the Writer keeps the central story and its appeal. Use ONLY what is in the Seed above.
Rules:
- Do NOT invent new events, new characters, new causes or new outcomes. You may decide which details can be simplified or omitted (minor details, order of minor obstacles), but the central story, character relationships, cause-and-effect, and the story's appeal must stay.
- Only the main character (Melos) has a personal name. Refer to everyone else by role (the ruler, his friend, his sister).
- Write the brief in plain English.

Fill these five items:
1. central_conflict: the central conflict / tension of the story, in 1-2 sentences.
2. key_scenes: the important scenes and turning points that must remain (4-7 items, in story order). For each: id (S1, S2, ...), scene (1 sentence), role ("setup" | "turning_point" | "climax" | "resolution"), why (why it is needed for the central story).
3. engaging_progression: the developments that pull the reader forward (how tension rises from scene to scene; what makes the reader want to know what happens next), in 2-4 sentences, using only events from the Seed.
4. climax_and_aftertaste: what the climax is, how the ending should land, and what feeling should remain after the ending, in 2-3 sentences.
5. preservation_conditions: 3-6 short conditions that must hold so the central story and its appeal are kept (e.g. which relationships, which cause-and-effect links, which emotional turn).
Also give may_simplify_or_omit: details the Writer may simplify or drop (0-5 short items).
Finally write brief_text: a Story Brief for the Writer (plain text, 120-250 words) that combines the five items. It must start with one line "Storyline: ..." and must contain no new events or names beyond the Seed."""

B3Z_SCHEMA = {
    "name": "storyline_b3z_story_brief",
    "schema": {
        "type": "object",
        "properties": {
            "central_conflict": {"type": "string"},
            "key_scenes": {"type": "array", "items": {"type": "object", "properties": {
                "id": {"type": "string"}, "scene": {"type": "string"},
                "role": {"type": "string", "enum": ["setup", "turning_point", "climax", "resolution"]},
                "why": {"type": "string"}}, "required": ["id", "scene", "role", "why"], "additionalProperties": False}},
            "engaging_progression": {"type": "string"},
            "climax_and_aftertaste": {"type": "string"},
            "preservation_conditions": {"type": "array", "items": {"type": "string"}},
            "may_simplify_or_omit": {"type": "array", "items": {"type": "string"}},
            "brief_text": {"type": "string"},
        },
        "required": ["central_conflict", "key_scenes", "engaging_progression", "climax_and_aftertaste",
                     "preservation_conditions", "may_simplify_or_omit", "brief_text"],
        "additionalProperties": False,
    },
    "strict": True,
}
BRIEF_APPEND = ("\n\n[Story Brief -- organized by the editor from the Seed above. Use it to decide what to keep; "
                "do not add events that are not in the Seed or this Brief.]\n{brief}\n")

# ---- R1/R2 (Family X W-1 の USER_TMPL[事実は変えずにエンタメ性を上げる]のFamily Z向け最小変更) ----
REVISE_USER_TMPL = ("Here is a short story:\n\n{body}\n\n"
                    "Without changing the events, the characters, or the cause-and-effect, please revise it into a more engaging story. "
                    "Keep it at A2 level (short, clear sentences, common vocabulary), about 280-420 words, in third person, "
                    "and only Melos may have a personal name. Output the title and the story only.")
FORBIDDEN_NAMES = ("Selinuntius", "Dionysius", "Dionys", "Phidias")


def sha(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def wt(p, text):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def wj(p, obj):
    wt(p, json.dumps(obj, ensure_ascii=False, indent=2, default=str))


def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def word_count(text: str) -> int:
    """見出し行(#で始まる行)を除いた語数。タイトルが#無しの場合は先頭行も含む(参考値)。"""
    lines = [l for l in text.splitlines() if not l.lstrip().startswith("#")]
    return len(" ".join(lines).split())


def load_pricing(model):
    d = json.load(open(PRICING, encoding="utf-8"))
    out = {}
    for e in d["prices"]:
        if e.get("provider") == "openai" and e.get("model") == model and e.get("tier") == "Standard":
            out[e["meter"]] = e["price"]
    for k in ("input_tokens", "cached_input_tokens", "output_tokens"):
        if k not in out:
            raise RuntimeError(f"[STOP] 単価未登録 {model} {k}")
    return out


def cost_jpy(model, usage):
    p = load_pricing(model)
    inp = getattr(usage, "input_tokens", 0) or 0
    det = getattr(usage, "input_tokens_details", None)
    cached = (getattr(det, "cached_tokens", 0) or 0) if det is not None else 0
    outp = getattr(usage, "output_tokens", 0) or 0
    usd = (max(inp - cached, 0) * p["input_tokens"] + cached * p["cached_input_tokens"] + outp * p["output_tokens"]) / 1e6
    return usd * USD_JPY


class Guard:
    def __init__(self, cap, est_per_call):
        self.cap, self.est, self.spent = cap, est_per_call, 0.0

    def before(self, label):
        if self.spent + self.est > self.cap:
            raise SystemExit(f"[STOP] 費用上限: 累計{self.spent:.2f}円+次call見積{self.est:.2f}円 > 上限{self.cap}円 ({label})")

    def add(self, v):
        self.spent += v


class _MockResp:
    def __init__(self, t, model):
        self.output_text, self.id, self.model = t, "mock", model
        self.usage = type("U", (), {"input_tokens": 1000, "output_tokens": 1000, "input_tokens_details": None})()


class _MockResponses:
    def create(self, **kw):
        if "text" in kw:
            obj = {"central_conflict": "c",
                   "key_scenes": [{"id": f"S{i}", "scene": "s", "role": "setup", "why": "w"} for i in range(1, 5)],
                   "engaging_progression": "p", "climax_and_aftertaste": "a", "preservation_conditions": ["x", "y", "z"],
                   "may_simplify_or_omit": [], "brief_text": "Storyline: test " + " ".join(["w"] * 130)}
            return _MockResp(json.dumps(obj), kw["model"])
        return _MockResp("The Title\n\n" + " ".join(["word"] * 350), kw["model"])


class Mock:
    responses = _MockResponses()


def call(client, guard, label, **kw):
    """1call。技術失敗(例外・空出力)のみ最大1回retry。返却model不一致はSTOP。"""
    last = None
    for attempt in (1, 2):
        guard.before(f"{label}#{attempt}")
        t0 = time.time()
        try:
            r = client.responses.create(model=WRITER_MODEL, reasoning={"effort": EFFORT}, **kw)
        except Exception as e:  # noqa: BLE001
            last = e
            continue
        c = cost_jpy(WRITER_MODEL, r.usage)
        guard.add(c)
        if not str(r.model).startswith(WRITER_MODEL):
            raise SystemExit(f"[STOP] 返却modelが{WRITER_MODEL}で始まらない: {r.model}")
        if not (r.output_text or "").strip():
            last = RuntimeError("empty output")
            continue
        u = r.usage
        meta = {"label": label, "attempt": attempt, "requested_model": WRITER_MODEL, "model": r.model, "response_id": r.id,
                "effort": EFFORT, "elapsed_sec": round(time.time() - t0, 1), "input_tokens": getattr(u, "input_tokens", None),
                "output_tokens": getattr(u, "output_tokens", None),
                "reasoning_tokens": getattr(getattr(u, "output_tokens_details", None), "reasoning_tokens", None),
                "cost_jpy": round(c, 3)}
        return r, meta
    raise SystemExit(f"[STOP] {label}: 技術失敗(2回): {last!r}")


def validate_b3z(p: dict):
    errs = []
    if len(p.get("key_scenes", [])) < 4:
        errs.append("KEY_SCENES<4")
    for k in ("central_conflict", "engaging_progression", "climax_and_aftertaste"):
        if not (p.get(k) or "").strip():
            errs.append(f"EMPTY_{k}")
    if len(p.get("preservation_conditions", [])) < 3:
        errs.append("PRESERVATION<3")
    bt = p.get("brief_text", "")
    if not bt.startswith("Storyline:"):
        errs.append("BRIEF_NO_STORYLINE_LINE")
    n = len(bt.split())
    if not (60 <= n <= 320):
        errs.append(f"BRIEF_WORDS_OUT_OF_RANGE:{n}")
    blob = json.dumps(p, ensure_ascii=False).lower()
    for nm in FORBIDDEN_NAMES:
        if nm.lower() in blob:
            errs.append(f"NEW_NAME:{nm}")
    return errs


def stage_b3z(client, guard, seed_block, d):
    user = B3Z_USER_TMPL.format(seed_block=seed_block)
    wt(f"{d}/b3z_prompt.txt", B3Z_DEVELOPER + "\n\n---\n\n" + user)
    kw = dict(text={"format": {"type": "json_schema", **B3Z_SCHEMA}},
              input=[{"role": "developer", "content": B3Z_DEVELOPER}, {"role": "user", "content": user}])
    errs = []
    for attempt in (1, 2):   # schema/検証の技術retryは1回(Xの B3 と同じ思想)
        r, meta = call(client, guard, f"b3z_attempt{attempt}", **kw)
        try:
            p = json.loads(r.output_text)
        except Exception as e:  # noqa: BLE001
            errs, p = [f"JSON:{e}"], None
        else:
            errs = validate_b3z(p)
        meta["validation_errors"] = errs
        wj(f"{d}/b3z_meta_attempt{attempt}.json", meta)
        wt(f"{d}/b3z_raw_attempt{attempt}.json", r.output_text)
        if not errs:
            wj(f"{d}/b3z_brief.json", p)
            wt(f"{d}/b3z_brief.md", "# B3Z Story Brief\n\n" + p["brief_text"] + "\n")
            return p, meta
    raise SystemExit(f"[STOP] B3Z検証が2回失敗: {errs}")


def run_chain(client, guard, label, r0_prompt, devmsg, d):
    metas = []
    wt(f"{d}/r0_prompt.txt", r0_prompt)
    r, m = call(client, guard, f"{label}_r0", input=[{"role": "developer", "content": devmsg}, {"role": "user", "content": r0_prompt}])
    r0 = r.output_text.strip() + "\n"
    wt(f"{d}/r0.md", r0)
    m["words"] = word_count(r0)
    metas.append(m)
    texts = {"r0": r0}
    prev = r0
    for k in ("r1", "r2"):
        u = REVISE_USER_TMPL.format(body=prev.strip())
        wt(f"{d}/{k}_prompt.txt", u)
        r, m = call(client, guard, f"{label}_{k}", input=[{"role": "user", "content": u}])
        prev = r.output_text.strip() + "\n"
        wt(f"{d}/{k}.md", prev)
        m["words"] = word_count(prev)
        metas.append(m)
        texts[k] = prev
    wj(f"{d}/chain_meta.json", metas)
    return texts, metas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("mock", "estimate", "real"), required=True)
    ap.add_argument("--approved-budget-jpy", type=float, default=0.0)
    ap.add_argument("--est-per-call-jpy", type=float, default=6.0, help="Sol 1call保守見積(guard用)")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--only", choices=("m2", "m3", "all"), default="all")
    a = ap.parse_args()
    sys.path.insert(0, ROOT)
    story_prompt = rd(f"{SEED_DIR}/story_prompt.txt")
    seed_block = story_prompt.split("[Common principles for this story family]")[0].strip()
    import er018_fiction_story_dna_e_axis_redesign_01 as e_axis
    import er006_model_routing_contract_01 as routing
    assert WRITER_MODEL == routing.PROCESS_MODEL_MAP["FAMILY_X_FACTLOCK_R0"], "Sol model ID drift"
    load_pricing(WRITER_MODEL)
    devmsg = e_axis.WRITER_DEVELOPER_MESSAGE
    if a.mode == "estimate":
        n = 7  # m2:3 + m3:4(B3Z含む)
        print(json.dumps({"sol_calls": n, "per_call_guard_jpy": a.est_per_call_jpy, "base_jpy": n * a.est_per_call_jpy,
                          "with_retry_margin_jpy": n * a.est_per_call_jpy * 1.3}, ensure_ascii=False))
        return
    if a.mode == "mock":
        client, out = Mock, a.out + "_mock"
        guard = Guard(1e9, 0)
    else:
        if a.approved_budget_jpy <= 0:
            sys.exit("STOP: real は --approved-budget-jpy(>0)必須")
        from dotenv import load_dotenv
        load_dotenv()
        import er005_cost_logger as cl
        import er003_v1_en_direct_vfl_01_generate as vfl01
        out = a.out
        os.makedirs(out, exist_ok=True)
        cl.install(os.path.join(out, "raw_usage_log.jsonl"))
        client = vfl01.get_client()
        guard = Guard(a.approved_budget_jpy, a.est_per_call_jpy)
    os.makedirs(out, exist_ok=True)
    summary = {"started": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "model": WRITER_MODEL, "effort": EFFORT,
               "r0_prompt_sha256": sha(story_prompt), "devmsg_sha256": sha(devmsg), "revise_tmpl_sha256": sha(REVISE_USER_TMPL),
               "b3z_tmpl_sha256": sha(B3Z_USER_TMPL)}
    if a.mode == "real":
        import er005_cost_logger as cl
        ctx = cl.logging_context(THEME_TAG, "trial")
    else:
        ctx = contextlib.nullcontext()
    with ctx:
        if a.only in ("m2", "all"):
            t, m = run_chain(client, guard, "m2", story_prompt, devmsg, f"{out}/m2_sol_only")
            summary["m2"] = {"words": {k: word_count(v) for k, v in t.items()}, "spent_jpy_so_far": round(guard.spent, 3)}
        if a.only in ("m3", "all"):
            p, bm = stage_b3z(client, guard, seed_block, f"{out}/m3_sol_b3z")
            mk = "[Common principles for this story family]"
            r0p = story_prompt.replace(mk, BRIEF_APPEND.format(brief=p["brief_text"]).lstrip("\n") + "\n" + mk, 1)
            assert r0p != story_prompt
            t, m = run_chain(client, guard, "m3", r0p, devmsg, f"{out}/m3_sol_b3z")
            summary["m3"] = {"words": {k: word_count(v) for k, v in t.items()}, "b3z_meta": bm}
    summary["spent_jpy"] = round(guard.spent, 3)
    summary["finished"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    wj(f"{out}/gen_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
