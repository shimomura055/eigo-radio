# -*- coding: utf-8 -*-
"""FACTLOCK-WRITER-REDESIGN-TRIAL-01 委任_04a: Prompt変種sweep harness(Trial専用、Production経路ではない)。

既存 er052_factlock_writer_trial_01_run.py(以下 fl)を編集せず import して再利用する
(タグ照合(i)-(iv)・タグ除去・manifest部品)。変種定義は
er052_output/factlock_writer_trial_01/sweep_01/variants.json(R0/R1/R2/R3ブロック全文)から読む。
Production module(er019 writer 等)は import したものを in-process で monkeypatch し、終了時に必ず復元する。
本ファイルは import 時に API を呼ばない。有料実行には --yes-run-paid が必要(--dry-run は呼び出しなし)。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time

import er052_factlock_writer_trial_01_run as fl

TRIAL_ID = "FACTLOCK-WRITER-REDESIGN-TRIAL-01"
SWEEP_ID = "FACTLOCK-SWEEP-01"
BASE_ROOT = "er052_output/factlock_writer_trial_01"
SWEEP_ROOT = f"{BASE_ROOT}/sweep_01"
RUNS_ROOT = f"{SWEEP_ROOT}/runs"
VARIANTS_JSON = f"{SWEEP_ROOT}/variants.json"
STRIPPED_BRIEF_ROOT = f"{SWEEP_ROOT}/briefs_nomarks"
CHECK_MODEL = fl.CHECK_MODEL
R3_FILE = "revision3.md"


def sha256_text(s):
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def load_variants(path: str = VARIANTS_JSON) -> dict:
    d = json.load(open(path, encoding="utf-8"))
    return {v["id"]: v for v in d["variants"]}


# ============================================================
# 1. R0 / R1 / R2 / R3 の組み立て(純関数)
# ============================================================
def _proper_noun_line(an3_block: str) -> str:
    lines = (an3_block or "").strip("\n").split("\n")
    proper = [l for l in lines if l.startswith("人名・企業名・地名")]
    if len(proper) != 1:
        raise ValueError("AN3ブロックの固有名詞文が特定できない")
    return proper[0]


def build_concreteness_block(variant: dict, an3_original: str) -> str:
    """jaw.CONCRETENESS_CONTROL_AN3_BLOCK の差替え値。
    append: AN3原文(数字文+固有名詞文)を保持したまま variant のR0ブロックを後置する(現行+追記)。
    replace_numeric: AN3の数字文だけを variant のR0ブロックで置換し、固有名詞文は逐語で保持する。"""
    r0 = variant["r0"]
    mode = r0["mode"]
    if mode == "append":
        return an3_original + r0["block"]
    if mode == "replace_numeric":
        return r0["block"] + "\n" + _proper_noun_line(an3_original)
    if mode == "replace_all":
        # S12(案A): ブロックが固有名詞文(規則6)を逐語で含む前提。含まなければ例外(取り違え防止)
        if _proper_noun_line(an3_original) not in r0["block"]:
            raise ValueError("replace_all: ブロックにAN3の固有名詞文が逐語で含まれない")
        return r0["block"]
    raise ValueError(f"unknown r0 mode: {mode}")


def build_revision_instruction(variant: dict, stage: str, original: str) -> str:
    """stage in (r1, r2)。append: 現行指示+追記、replace: variantの文で置換(追記なしの目標文)。"""
    spec = variant[stage]
    if spec["mode"] == "append":
        return original + spec["text"]
    if spec["mode"] == "replace":
        return spec["text"]
    raise ValueError(f"unknown {stage} mode: {spec['mode']}")


def apply_prompt_replace(r0_prompt: str, pairs: list) -> str:
    out = r0_prompt
    for old, new in pairs:
        if old not in out:
            raise ValueError(f"R0_PROMPTに置換元が無い: {old[:30]}")
        out = out.replace(old, new, 1)
    return out


# ============================================================
# 2. brief(印の除去)
# ============================================================
def strip_marks(text: str) -> str:
    return fl.MARK_RE.sub("", text or "")


def ensure_nomarks_brief(slug: str, b: str, brief_md: str, root: str | None = None) -> str:
    """【中核数値】【周辺数値】の印を除いた brief 複写を作る(印の説明を持たない変種用)。
    brief内容はそれ以外同一(【事実N】は残す)。同内容の冪等な書込。"""
    dest = f"{root or STRIPPED_BRIEF_ROOT}/{slug}/{b}/selected_brief_nomarks.md"
    text = strip_marks(open(brief_md, encoding="utf-8").read())
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if not os.path.exists(dest) or open(dest, encoding="utf-8").read() != text:
        with open(dest, "w", encoding="utf-8", newline="") as f:
            f.write(text)
    return dest


# ============================================================
# 3. 連鎖切り(S8)
# ============================================================
class ChainState:
    """response_id -> タグ除去済み本文 の記録と、連鎖切りの実施ログ。"""

    def __init__(self):
        self.texts = {}
        self.cut_log = []


CUT_STAGES = ("ja_r1", "ja_r2", "ja_r2_must_fix")


def make_chain_wrappers(jaw, state: ChainState, cut: bool):
    """jaw.call_fresh / jaw.call_with_previous_response_id の包み。
    cut=False: 応答本文(タグ除去済み)を記録するだけで挙動は不変。
    cut=True: previous_response_id を使わず、直前の本文(タグ除去済み)を新規contextで渡す
              (Production fallback_full_text と同じ書式: 「以下の記事:\\n\\n{本文}\\n\\n{指示}」)。"""
    orig_fresh = jaw.call_fresh
    orig_prev = jaw.call_with_previous_response_id

    def record(resp):
        try:
            state.texts[resp.id] = fl.strip_tags((resp.output_text or "").strip())
        except Exception:  # noqa: BLE001
            pass
        return resp

    def fresh(client, developer, user, effort, stage):
        if cut and stage in CUT_STAGES:
            user = fl.strip_tags(user)     # フォールバック経路でも本文のタグを見せない
        return record(orig_fresh(client, developer, user, effort, stage))

    def prev(client, user, effort, previous_response_id, stage):
        if not cut:
            return record(orig_prev(client, user, effort, previous_response_id, stage))
        prev_text = state.texts.get(previous_response_id)
        if prev_text is None:
            raise RuntimeError(f"連鎖切り: 直前応答の本文が記録に無い({previous_response_id})")
        new_user = f"以下の記事:\n\n{prev_text}\n\n{user}"
        state.cut_log.append({"stage": stage, "prev_id": previous_response_id,
                              "input_sha256": sha256_text(new_user), "article_chars": len(prev_text)})
        return record(orig_fresh(client, jaw.DEVELOPER_MESSAGE, new_user, effort, stage))

    return fresh, prev, (orig_fresh, orig_prev)


# ============================================================
# 4. patch(Production無編集のmonkeypatch)
# ============================================================
def apply_sweep_patches(variant: dict, mods: dict | None = None, state: ChainState | None = None) -> dict:
    if mods is None:
        import er003_v1_en_direct_vfl_01_generate as vfl01
        import er019_family_x_ja_writer_o_r1_r2_01 as jaw
        mods = {"vfl01": vfl01, "jaw": jaw}
    jaw, vfl01 = mods["jaw"], mods["vfl01"]
    state = state or ChainState()
    saved = {"_mods": mods, "state": state, "an3": jaw.CONCRETENESS_CONTROL_AN3_BLOCK, "r0_prompt": jaw.R0_PROMPT,
             "rev": dict(jaw.REVISION_INSTRUCTIONS), "dev": vfl01.run_deviation_check,
             "call_fresh": jaw.call_fresh, "call_prev": jaw.call_with_previous_response_id}
    jaw.CONCRETENESS_CONTROL_AN3_BLOCK = build_concreteness_block(variant, saved["an3"])
    jaw.R0_PROMPT = apply_prompt_replace(saved["r0_prompt"], variant["r0"].get("prompt_replace") or [])
    for k in ("r1", "r2"):
        jaw.REVISION_INSTRUCTIONS[k] = build_revision_instruction(variant, k, saved["rev"][k])
    fresh, prev, _ = make_chain_wrappers(jaw, state, cut=(variant["chain"] == "cut"))
    jaw.call_fresh, jaw.call_with_previous_response_id = fresh, prev
    orig = saved["dev"]

    def dev_strip(client, verified_ledger_text, article_text, *a, **k):
        if k.get("source_article_text") is not None:
            k["source_article_text"] = fl.strip_tags(k["source_article_text"])
        return orig(client, verified_ledger_text, fl.strip_tags(article_text), *a, **k)

    vfl01.run_deviation_check = dev_strip
    return saved


def restore_sweep_patches(saved: dict) -> None:
    jaw, vfl01 = saved["_mods"]["jaw"], saved["_mods"]["vfl01"]
    jaw.CONCRETENESS_CONTROL_AN3_BLOCK = saved["an3"]
    jaw.R0_PROMPT = saved["r0_prompt"]
    for k, v in saved["rev"].items():
        jaw.REVISION_INSTRUCTIONS[k] = v
    jaw.call_fresh, jaw.call_with_previous_response_id = saved["call_fresh"], saved["call_prev"]
    vfl01.run_deviation_check = saved["dev"]


# ============================================================
# 5. 事後タグ再付与(S8、測定のみ)
# ============================================================
RETAG_DEVELOPER = ("あなたは出典タグ付けの担当です。文章の面白さ・文体は評価しません。"
                   "各文が世界について述べている主張が、事実一覧のどの事実に基づくかだけを答えます。")

RETAG_PROMPT = """次の「事実一覧」と「文」を見て、各文が世界について断定している内容(出来事・数値・人物の発言や行動・原因・結果・比較・時期など)が、事実一覧のどの事実に基づくかを答えてください。

【事実一覧】
{facts}

【文】
{sentences}

- 事実に基づく文は、根拠にした事実のID(F1, F2 など)を fact_ids に入れる(複数可)。
- 問いかけ・感想・読者への語りかけ・つなぎ・比喩だけの文、および事実一覧に根拠が見つからない文は fact_ids を空にする。
- 事実一覧にないIDを作らない。"""

RETAG_SCHEMA = {"name": "factlock_retag", "strict": True, "schema": {
    "type": "object", "additionalProperties": False, "required": ["items"],
    "properties": {"items": {"type": "array", "items": {
        "type": "object", "additionalProperties": False, "required": ["sentence_index", "fact_ids"],
        "properties": {"sentence_index": {"type": "integer"},
                       "fact_ids": {"type": "array", "items": {"type": "string"}}}}}}}}


def tag_string(ids: list) -> str:
    nums = [i[1:] for i in ids if re.fullmatch(r"F\d+", i)]
    return "【" + ",".join(f"事実{n}" for n in nums) + "】" if nums else ""


def apply_retag(text: str, assignments: dict) -> str:
    """text(タグ無し)の文のうち、assignments{sentence_idx: [F-id,...]} にあるものの句点の直後へタグを付けて返す。
    strip_tags(結果) == strip_tags(text) を保つ(タグ以外は変えない)。"""
    sents = fl.split_sentences(text)
    by_line = {}
    for s in sents:
        by_line.setdefault(s["line"], []).append(s)
    out = []
    for ln, line in enumerate((text or "").split("\n")):
        if ln not in by_line:
            out.append(line)
            continue
        parts = []
        for s in by_line[ln]:
            tag = "" if s["is_title"] else tag_string(assignments.get(s["idx"], []))
            parts.append(s["raw"] + tag)
        out.append("".join(parts))
    return "\n".join(out)


def retag_text(client, model, stage, text, facts):
    """6-luna 1 call で各文に事実IDを割り当て、タグ付き本文を返す。戻り値: (tagged_text, record)"""
    sents = [s for s in fl.split_sentences(text) if not s["is_title"]]
    if not sents:
        return text, {"stage": stage, "assigned": {}, "response_id": None}
    lines = "\n".join(f"[{s['idx']}] {s['text']}" for s in sents)
    data, resp = fl._call_json(client, model, RETAG_PROMPT.format(facts=fl._facts_block(facts), sentences=lines),
                               RETAG_SCHEMA, f"sweep_retag_{stage}")
    valid = set(facts)
    assigned = {}
    for it in data["items"]:
        ids = [i for i in it["fact_ids"] if i in valid]
        if ids:
            assigned[it["sentence_index"]] = ids
    tagged = apply_retag(text, assigned)
    return tagged, {"stage": stage, "assigned": {str(k): v for k, v in assigned.items()},
                    "response_id": getattr(resp, "id", None), "model": getattr(resp, "model", None),
                    "untagged_sentences": len([s for s in sents if s["idx"] not in assigned])}


# ============================================================
# 6. R3(S9): phase1後にharness側で1回追加(Production経路は2回のまま)
# ============================================================
def append_r3(variant: dict, out_dir: str, client, jaw, vfl01, safety=None, chain: ChainState | None = None) -> dict:
    """R2確定後にR3を1回生成し、JA Fact Check(MAJORなら不採用)と記号Gateを通ったときだけ最終記事を差し替える。
    採用: revision2.md を R3 本文(タグ付きのまま、後段postprocessでタグ除去)に差し替え、
          R3前のR2を revision2_pre_r3_with_tags.md へ退避。不採用: R2のまま(理由を記録)。
    これは Trial 側の措置で、Production の R2直後Fact Check/must-fix/STOP は変更しない。"""
    d = f"{out_dir}/ja_writer"
    r2_raw = open(f"{d}/revision2.md", encoding="utf-8").read()
    ev = json.load(open(f"{d}/runtime_evidence.json", encoding="utf-8"))
    prev_id = (ev.get("r2") or {}).get("response_id")
    instruction = variant["r3"]["instruction"] + jaw.SYMBOL_PREVENTION_BLOCK_JA
    rec = {"r3_instruction_sha256": sha256_text(instruction), "prev_id": prev_id}
    resp, method = None, None
    if prev_id:
        try:
            resp = jaw.call_with_previous_response_id(client, instruction, jaw.WRITER_EFFORT, prev_id, "ja_r3")
            method = "previous_response_id"
        except Exception as exc:  # noqa: BLE001
            rec["chain_error"] = repr(exc)
    if resp is None:
        resp = jaw.call_fresh(client, jaw.DEVELOPER_MESSAGE, f"以下の記事:\n\n{r2_raw}\n\n{instruction}",
                              jaw.WRITER_EFFORT, "ja_r3")
        method = "fallback_full_text"
    r3 = (resp.output_text or "").strip()
    rec.update({"method": method, "response_id": getattr(resp, "id", None), "model": getattr(resp, "model", None)})
    with open(f"{d}/{R3_FILE}", "w", encoding="utf-8", newline="") as f:
        f.write(r3)
    ledger = open(f"{out_dir}/research_ledger/verified_fact_ledger.txt", encoding="utf-8").read()
    chk = vfl01.run_deviation_check(client, ledger, r3, hook_aware=False, include_related_fact_id=True)
    status = (chk.get("parsed") or {}).get("overall_status")
    sym = []
    if safety is not None:
        sym = safety.detect_prohibited_symbols(fl.strip_tags(r3), language="ja")
    rec.update({"fact_check_status": status, "symbol_findings": [str(x) for x in sym]})
    adopted = (status != "LEDGER_DEVIATION") and not (safety is not None and safety.symbol_gate_requires_stop(sym))
    rec["adopted"] = bool(adopted)
    rec["rejected_reason"] = None if adopted else ("fact_check_LEDGER_DEVIATION" if status == "LEDGER_DEVIATION"
                                                   else "symbol_gate")
    if adopted:
        with open(f"{d}/revision2_pre_r3_with_tags.md", "w", encoding="utf-8", newline="") as f:
            f.write(r2_raw)
        with open(f"{d}/revision2.md", "w", encoding="utf-8", newline="") as f:
            f.write(r3)
    with open(f"{out_dir}/sweep_r3.json", "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)
    return rec


# ============================================================
# 7. 後処理(タグ照合→タグ除去)。fl.postprocess_phase1 を再利用
# ============================================================
def postprocess(variant: dict, out_dir: str, brief_md: str, core_json: str, client=None, model: str = CHECK_MODEL,
                use_llm: bool = True) -> dict:
    """tag_mode: full=そのまま fl.postprocess_phase1 / retag=R1,R2を事後タグ再付与してから同処理 /
    none=タグ無しで同処理((i)(iv)は対象文0で自然に空、(ii)(iii)のみ)。"""
    d = f"{out_dir}/ja_writer"
    extra = {}
    if variant["tag_mode"] == "retag":
        facts = fl.parse_annotated_facts(open(brief_md, encoding="utf-8").read())
        recs = {}
        for st in ("r1", "r2"):
            p = f"{d}/{fl.STAGE_FILES[st]}"
            raw = open(p, encoding="utf-8").read()
            with open(p[:-3] + "_untagged_raw.md", "w", encoding="utf-8", newline="") as f:
                f.write(raw)
            if use_llm:
                tagged, rec = retag_text(client, model, st, raw, facts)
                assert fl.strip_tags(tagged) == fl.strip_tags(raw), "再付与で本文が変わった"
                with open(p, "w", encoding="utf-8", newline="") as f:
                    f.write(tagged)
                recs[st] = rec
        extra["retag"] = recs
        with open(f"{out_dir}/sweep_retag.json", "w", encoding="utf-8") as f:
            json.dump(recs, f, ensure_ascii=False, indent=2)
    if variant.get("r3") is not None and os.path.exists(f"{d}/revision2_pre_r3_with_tags.md") and use_llm:
        facts = fl.parse_annotated_facts(open(brief_md, encoding="utf-8").read())
        core = fl.load_core_numbers(core_json)
        pre = open(f"{d}/revision2_pre_r3_with_tags.md", encoding="utf-8").read()
        rec = fl.check_stage(client, model, "r2pre", pre, facts, core, use_llm=True)
        with open(f"{out_dir}/factlock_check_r2pre.json", "w", encoding="utf-8") as f:
            json.dump(rec, f, ensure_ascii=False, indent=2)
    summ = fl.postprocess_phase1(out_dir, brief_md, core_json, client=client, model=model, use_llm=use_llm)
    summ["sweep_extra"] = extra
    return summ


# ============================================================
# 8. main
# ============================================================
def build_parser():
    p = argparse.ArgumentParser()
    p.add_argument("--variant", required=True)
    p.add_argument("--slug", required=True)
    p.add_argument("--brief-md", required=True, help="注記版 selected_brief_factlock.md(印除去が必要な変種はharnessが複写を作る)")
    p.add_argument("--core-numbers-json", required=True)
    p.add_argument("--ledger-txt", required=True)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--budget-jpy", type=float, default=12.0)
    p.add_argument("--theme-file", default=None)
    p.add_argument("--checker-budget-jpy", type=float, default=10.0)
    p.add_argument("--variants-json", default=VARIANTS_JSON)
    p.add_argument("--yes-run-paid", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    return p


def resolve_brief(variant: dict, slug: str, brief_md: str) -> str:
    if variant["brief_marks"] == "strip":
        b = os.path.basename(os.path.dirname(brief_md))
        return ensure_nomarks_brief(slug, b, brief_md)
    return brief_md


def make_manifest(args, variant, jaw, vfl01, all6, brief_used) -> dict:
    return {
        "trial_id": TRIAL_ID, "sweep_id": SWEEP_ID, "arm": f"sweep_{variant['id']}_6luna", "variant": variant["id"],
        "variant_axis": variant["axis"], "tag_mode": variant["tag_mode"], "brief_marks": variant["brief_marks"],
        "chain_requested": variant["chain"], "r3": variant["r3"] is not None,
        "slug": args.slug, "out_dir": args.out_dir, "brief_md": args.brief_md, "brief_used": brief_used,
        "brief_sha256": fl.sha256_file(args.brief_md), "brief_used_sha256": fl.sha256_file(brief_used),
        "core_numbers_sha256": fl.sha256_file(args.core_numbers_json), "ledger_sha256": fl.sha256_file(args.ledger_txt),
        "variants_json_sha256": fl.sha256_file(args.variants_json),
        "prompt_sha256": {
            "R0_PROMPT_original": sha256_text(jaw.R0_PROMPT),
            "R0_PROMPT_variant": sha256_text(apply_prompt_replace(jaw.R0_PROMPT, variant["r0"].get("prompt_replace") or [])),
            "AN3_original": sha256_text(jaw.CONCRETENESS_CONTROL_AN3_BLOCK),
            "CONCRETENESS_variant": sha256_text(build_concreteness_block(variant, jaw.CONCRETENESS_CONTROL_AN3_BLOCK)),
            "R1_instruction_variant": sha256_text(build_revision_instruction(variant, "r1", jaw.REVISION_INSTRUCTIONS["r1"])),
            "R2_instruction_variant": sha256_text(build_revision_instruction(variant, "r2", jaw.REVISION_INSTRUCTIONS["r2"])),
            "R3_instruction_variant": sha256_text(variant["r3"]["instruction"]) if variant["r3"] else None,
            "DEVELOPER_MESSAGE": sha256_text(jaw.DEVELOPER_MESSAGE),
            "PAIR_PROMPT": sha256_text(fl.PAIR_PROMPT), "UNTAGGED_PROMPT": sha256_text(fl.UNTAGGED_PROMPT),
            "RETAG_PROMPT": sha256_text(RETAG_PROMPT)},
        "harness_sha256": {"sweep_run": fl.sha256_file(__file__), "factlock_run": fl.sha256_file(fl.__file__),
                           "all6_run": fl.sha256_file(all6.__file__)},
        "production_sha256": {"er019_writer": fl.sha256_file(jaw.__file__), "vfl01": fl.sha256_file(vfl01.__file__)},
        "reasoning_effort": vfl01.REASONING_EFFORT, "all6_model": all6.ALL6_MODEL,
        "checker_enabled": True, "budget_jpy": args.budget_jpy, "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "phases": [],
    }


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    variants = load_variants(args.variants_json)
    if args.variant not in variants:
        raise SystemExit(f"未知のvariant: {args.variant}(許可: {sorted(variants)})")
    variant = variants[args.variant]
    theme_file = args.theme_file or os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(args.ledger_txt))), "topic.txt")
    os.environ["OPEN233_RUNS_ROOT"] = RUNS_ROOT
    os.environ.pop("OPEN233_B3_VARIANT", None)
    import er052_open233_polysemy_nb_dev_01 as dev
    import er052_all6_writer_trial_01_run as all6
    import er019_family_x_ja_writer_o_r1_r2_01 as jaw
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er003_audio_tts_asr_safety as safety

    if args.dry_run or not args.yes_run_paid:
        brief_used = args.brief_md   # dry-runではファイルを作らない
        manifest = make_manifest(args, variant, jaw, vfl01, all6, brief_used)
        manifest["dry_run_note"] = "brief_marks=strip の複写はdry-runでは作らない(実行時に作成)"
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0 if args.dry_run else 2

    theme = open(theme_file, encoding="utf-8").read().strip()
    brief_used = resolve_brief(variant, args.slug, args.brief_md)
    manifest = make_manifest(args, variant, jaw, vfl01, all6, brief_used)
    saved_all6 = all6.apply_all6_patches()
    state = ChainState()
    saved_sw = apply_sweep_patches(variant, state=state)
    t0, rc, exit_reason = time.time(), 0, "completed"
    try:
        check_model = all6.resolve_all6_model(fl.CHECK_PROCESS)
        common = ["--theme", theme, "--slug", args.slug, "--ledger-txt", args.ledger_txt, "--out-dir", args.out_dir,
                  "--yes-run-paid"]
        for phase in ("phase1", "phase2"):
            argv2 = common + ["--phase", phase, "--budget-jpy", str(args.budget_jpy)]
            argv2 += ["--brief-md", brief_used] if phase == "phase1" else ["--checker-budget-jpy", str(args.checker_budget_jpy)]
            ts = time.time()
            try:
                prc = dev.main(argv2)
                manifest["phases"].append({"phase": phase, "rc": prc, "sec": round(time.time() - ts, 1)})
                if prc not in (0, None):
                    rc, exit_reason = (prc if isinstance(prc, int) else 1), f"{phase}_rc={prc}"
                    break
                if phase == "phase1":
                    client = vfl01.get_client()
                    if variant["r3"] is not None:
                        manifest["r3"] = append_r3(variant, args.out_dir, client, jaw, vfl01, safety=safety)
                    ts2 = time.time()
                    summ = postprocess(variant, args.out_dir, brief_used, args.core_numbers_json,
                                       client=client, model=check_model)
                    manifest["postprocess_sec"] = round(time.time() - ts2, 1)
                    manifest["factlock_shas"] = summ["shas"]
            except SystemExit as e:
                manifest["phases"].append({"phase": phase, "rc": f"SystemExit:{e}", "sec": round(time.time() - ts, 1)})
                rc, exit_reason = 1, f"{phase}_SystemExit: {e}"
                break
            except Exception as e:  # noqa: BLE001
                manifest["phases"].append({"phase": phase, "rc": f"error:{e!r}", "sec": round(time.time() - ts, 1)})
                rc, exit_reason = 1, f"{phase}_error: {e!r}"
                break
    finally:
        restore_sweep_patches(saved_sw)
        all6.restore_patches(saved_all6)
        manifest["chain_actual_cut_log"] = state.cut_log   # runtime_evidenceのchain_methodは連鎖切りでも previous_response_id と表示される
        manifest["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        manifest["wall_sec"] = round(time.time() - t0, 1)
        manifest["exit_reason"] = exit_reason
        manifest["model_ids_actual"] = all6.collect_models(args.out_dir)
        manifest["checker"] = all6.checker_summary(args.out_dir)
        cj = f"{args.out_dir}/cost.json"
        manifest["cost"] = json.load(open(cj, encoding="utf-8")) if os.path.exists(cj) else None
        os.makedirs(args.out_dir, exist_ok=True)
        manifest["residual_bracket_scan"] = fl.scan_residual_brackets(args.out_dir)
        with open(f"{args.out_dir}/manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
    return rc


if __name__ == "__main__":
    sys.exit(main())
