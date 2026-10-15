# -*- coding: utf-8 -*-
"""AUW 委任_06b: 実音声 runtime evidence runner(残Section / 残Family / 最終ページ / 3回NG->LR・HR)。
Production コードは無編集。共有 state は evidence 配下へ隔離(er077 apply_isolation を再利用)。
有料 API は --execute 指定時のみ。**全経路の費用を事前に wrapper で記録**(SDK レベル: OpenAI ASR / Gemini TTS+text / Azure 4関数)。
累計費用 ledger(cost/spend_ledger.jsonl)を run 前に読み、残額が 0 以下なら実行しない。監督ループ・自動再試行なし。
使い方: .venv\\Scripts\\python.exe er078_auw_runtime_evidence_06b.py <part> [--execute --budget-jpy N]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import er078_auw_runtime_evidence_06 as e6

ROOT = e6.ROOT
EV = "er058_output/unified_all_roles_production_wiring_01/evidence_06b"
CAP_JPY = 80.0
TTS_JPY = 0.062       # DESIGN_01 §9 の1clip単価(推定)
TEXT_LLM_JPY = 0.5    # Gemini text(Luna candidate / QA 等)の保守的な1call推定
LEDGER = f"{EV}/cost/spend_ledger.jsonl"
MANAGED_IDS = e6.MANAGED_IDS + ["AUW-06B"]
e6.MANAGED_IDS[:] = MANAGED_IDS


def ledger_total():
    """累計費用。token 実測で記録した run(basis=token_actual)はその値、固定単価で過小記録した初期 run は cost/revised_estimates.json(校正付き推定 or Production runner の cost log 実額)を run 名ごとに1回だけ採用。"""
    if not os.path.exists(LEDGER):
        return 0.0
    rev_p = f"{EV}/cost/revised_estimates.json"
    rev = json.load(open(rev_p, encoding="utf-8")) if os.path.exists(rev_p) else {}
    tot, by_run = 0.0, {}
    for l in open(LEDGER, encoding="utf-8"):
        if not l.strip():
            continue
        r = json.loads(l)
        if r.get("basis") == "token_actual":
            tot += r["est_total_jpy"]
        else:
            by_run[r["run"]] = by_run.get(r["run"], 0.0) + r["est_total_jpy"]
    for run, v in by_run.items():
        tot += rev[run]["revised_est_jpy"] if run in rev else v
    return tot


def ledger_append(run, meter, extra=None):
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    rec = {"run": run, "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "basis": "token_actual", "est_total_jpy": round(meter.jpy, 4), "n_tts": meter.n_tts,
           "n_openai_asr": meter.n_openai, "n_azure": meter.n_azure, "azure_seconds": round(meter.azure_seconds, 2),
           "n_text_llm": meter.n_text, "azure_duplicate_wavs": sum(1 for v in meter.azure_by_sha.values() if v > 1)}
    rec.update(extra or {})
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


class Meter(e6.Meter):
    def __init__(self, out_dir, hard_stop):
        super().__init__(out_dir, hard_stop)
        self.n_tts = 0
        self.n_text = 0
        self.azure_seconds = 0.0
        self.out_dir_rel = out_dir

    def check(self):
        super().check()
        hit = e6.stop_present(self.out_dir_rel)
        if hit:
            raise RuntimeError(f"[STOP] sentinel present: {hit}")
        if ledger_total() + self.jpy > CAP_JPY:
            raise RuntimeError(f"[STOP] cumulative cap {CAP_JPY} exceeded: ledger {ledger_total():.2f} + run {self.jpy:.2f}")


def install(meter):
    """全有料経路を SDK/関数レベルで計測。呼出『前』に check(予算/STOP) し、呼出ごとに usage_log.jsonl へ記録。"""
    from openai.resources.audio import transcriptions as tm
    from google.genai import models as gm
    import er006_secondary_asr_01 as sec
    import er007_ja_secondary_asr_01 as ja
    import er003_b1_p3u_audio as p3u
    import er003_b1_p4_audio as p4

    # 実費は応答の usage(token)×pricing_snapshot で算出(Production の compute_cost_jpy_so_far と同じ式、USD_JPY=160)。
    # 06b 初期(zep/ja_hr/lega/head/lr_en)は固定単価で記録しており過小(§12 逸脱)。以降の run は token 実測で記録する。
    import er019_family_x_audio_production_runner_01 as _X
    price = _X._load_pricing()
    fx = _X.USD_JPY

    def tok_cost(provider, model, in_tok, out_tok):
        try:
            return ((in_tok or 0) * price(provider, model, "input_tokens") + (out_tok or 0) * price(provider, model, "output_tokens")) / 1e6 * fx
        except Exception:  # noqa: BLE001  単価未登録は固定単価へ(保守側にならない場合は ledger に basis を残す)
            return None

    _oc = tm.Transcriptions.create

    def oc(self, *a, **k):
        meter.check()
        resp = _oc(self, *a, **k)
        u = getattr(resp, "usage", None)
        c = tok_cost("openai_asr", k.get("model"), getattr(u, "input_tokens", None), getattr(u, "output_tokens", None)) if u is not None else None
        basis = "token_actual"
        if c is None:
            c, basis = 0.15, "fallback_const_0.15"
        meter.n_openai += 1
        meter.jpy += c
        meter.rec(provider="openai_asr", api="audio.transcriptions.create", model=k.get("model"), lang=k.get("language"),
                  in_tok=getattr(u, "input_tokens", None), out_tok=getattr(u, "output_tokens", None), est_jpy=round(c, 5), basis=basis)
        return resp
    tm.Transcriptions.create = oc

    _gc = gm.Models.generate_content

    def gc(self, *a, **k):
        meter.check()
        cfg = k.get("config")
        mods = getattr(cfg, "response_modalities", None) if cfg else None
        is_audio = bool(mods and "AUDIO" in mods)
        resp = _gc(self, *a, **k)
        um = getattr(resp, "usage_metadata", None)
        c = tok_cost("gemini", k.get("model"), getattr(um, "prompt_token_count", None), getattr(um, "candidates_token_count", None)) if um is not None else None
        basis = "token_actual"
        if c is None:
            c, basis = (1.0 if is_audio else TEXT_LLM_JPY), "fallback_const"
        meter.jpy += c
        if is_audio:
            meter.n_tts += 1
        else:
            meter.n_text += 1
        meter.rec(provider="gemini", api="generate_content(TTS)" if is_audio else "generate_content(text)", model=k.get("model"),
                  in_tok=getattr(um, "prompt_token_count", None), out_tok=getattr(um, "candidates_token_count", None), est_jpy=round(c, 5), basis=basis)
        return resp
    gm.Models.generate_content = gc

    from openai.resources.responses import responses as rm
    _rc = rm.Responses.create

    def rc(self, *a, **k):
        meter.check()
        resp = _rc(self, *a, **k)
        u = getattr(resp, "usage", None)
        model = getattr(resp, "model", None) or k.get("model")
        c = tok_cost("openai", model, getattr(u, "input_tokens", None), getattr(u, "output_tokens", None)) if u is not None else None
        basis = "token_actual"
        if c is None:
            c, basis = 0.5, "fallback_const_0.5"
        meter.n_text += 1
        meter.jpy += c
        meter.rec(provider="openai", api="responses.create", model=model, in_tok=getattr(u, "input_tokens", None),
                  out_tok=getattr(u, "output_tokens", None), est_jpy=round(c, 5), basis=basis)
        return resp
    rm.Responses.create = rc

    def wrap_az(mod, name, api):
        orig = getattr(mod, name)

        def w(wav, *a, **k):
            meter.check()
            s = e6.sha(wav)
            sec_ = e6.wav_seconds(wav)
            meter.azure_by_sha[s] = meter.azure_by_sha.get(s, 0) + 1
            meter.n_azure += 1
            meter.azure_seconds += sec_
            c = e6.AZURE_JPY_PER_S * sec_
            meter.jpy += c
            r = orig(wav, *a, **k)
            meter.rec(provider="azure", api=api, wav=wav, sha=s[:12], seconds=round(sec_, 2), est_jpy=round(c, 5),
                      text=r[0] if isinstance(r, tuple) and r else None)
            return r
        setattr(mod, name, w)
    wrap_az(sec, "get_full_text_via_azure_stt_with_phrase_list", "stt_phrase_list")
    wrap_az(ja, "_azure_stt_strict", "stt_strict_ja")
    wrap_az(p4, "get_full_text_via_azure_stt_continuous", "stt_continuous")
    wrap_az(p3u, "get_word_timestamps_via_azure_stt", "stt_word_ts")


def redirect_local_rewrite(out):
    """Local Rewrite の回復 artifact(既定 er011_output/local_rewrite_recovery/...)を evidence 配下へ差替(共有 state を汚さない)。"""
    import er020_tts_retry_local_rewrite_01 as rp
    _orig = rp.run_local_rewrite_recovery

    def w(*a, **k):
        k["out_dir"] = f"{out}/local_rewrite_recovery"
        return _orig(*a, **k)
    rp.run_local_rewrite_recovery = w


def shared_snapshot():
    """tracked の modified/untracked(evidence 以外)の md5 snapshot。run 前後で一致=共有 state 無変更。"""
    import hashlib
    import subprocess
    r = subprocess.run(["git", "status", "--porcelain", "-uall"], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    snap = {}
    for line in r.stdout.splitlines():
        p = line[3:].strip().strip('"')
        if p.startswith("er058_output/unified_all_roles_production_wiring_01/evidence_06b") or p.startswith("user_test/") or p in ("er078_auw_runtime_evidence_06b.py", "er078_auw_tabulate_06b.py"):
            continue
        if " -> " in p:
            p = p.split(" -> ")[-1]
        full = os.path.join(ROOT, p)
        if os.path.isfile(full):
            snap[p] = hashlib.md5(open(full, "rb").read()).hexdigest()
        else:
            snap[p] = None
    return snap


def snapshot_diff(before, after):
    return sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))


def begin(part, budget, execute, copy_master=False):
    out = f"{EV}/{part}"
    os.makedirs(out, exist_ok=True)
    if copy_master:
        import shutil
        dst = f"{out}/master_audio_store"
        if not os.path.exists(dst):
            shutil.copytree("er006_output/master_audio_store_01", dst)
    r77, before, iso = e6.isolate(out)
    import er003_audio_tts_asr_safety as _safety  # JA Foreign Token Gate の HR queue(既定 er009_output/...)も隔離(06b 初回 ja_hr で共有 queue へ1行追記した逸脱の再発防止)
    _safety.FOREIGN_TOKEN_HUMAN_REVIEW_LOG_PATH = f"{out}/foreign_token_hr_queue.jsonl"
    iso["foreign_token_hr_queue"] = _safety.FOREIGN_TOKEN_HUMAN_REVIEW_LOG_PATH
    import er007_ja_secondary_asr_01 as _ja  # JA 側 HR queue(既定 er007_output/ja_asr_cascade_01/...)も隔離(06b ja_hr 初回で1行追記した逸脱の再発防止)
    _ja.HUMAN_REVIEW_LOG_PATH_JA = f"{out}/human_review_queue_ja.jsonl"
    iso["human_review_queue_ja"] = _ja.HUMAN_REVIEW_LOG_PATH_JA
    snap0 = shared_snapshot()
    hit = e6.stop_present(out)
    remaining = CAP_JPY - ledger_total()
    meter = None
    ok = execute and not hit and remaining > 0
    if ok:
        meter = Meter(out, hard_stop=min(budget, remaining))
        install(meter)
        redirect_local_rewrite(out)
    res = {"part": part, "mode": "execute" if execute else "dry-run", "stop_files_present": hit, "isolation": iso,
           "budget_jpy": budget, "ledger_before": round(ledger_total(), 4), "cap_remaining": round(remaining, 4)}
    return out, r77, before, snap0, res, meter, ok


def finish(out, r77, before, snap0, res, meter, extra_print=()):
    after = r77.snapshot_state()
    res["shared_state_unchanged"] = before == after
    snap1 = shared_snapshot()
    res["shared_files_changed_outside_evidence"] = snapshot_diff(snap0, snap1)
    if meter is not None:
        res["cost"] = {"est_total_jpy": round(meter.jpy, 4), "n_tts": meter.n_tts, "n_openai_asr": meter.n_openai, "n_azure": meter.n_azure,
                       "azure_seconds": round(meter.azure_seconds, 2), "n_text_llm": meter.n_text,
                       "azure_duplicate_wavs": sum(1 for v in meter.azure_by_sha.values() if v > 1)}
        ledger_append(res["part"], meter)
        res["ledger_after"] = round(ledger_total(), 4)
    json.dump(res, open(f"{out}/runner_{res['mode']}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    keys = ("part", "mode", "stop_files_present", "ledger_before", "stage_result", "cost", "shared_state_unchanged",
            "shared_files_changed_outside_evidence", "ledger_after") + tuple(extra_print)
    print(json.dumps({k: res.get(k) for k in keys}, ensure_ascii=False, default=str))


# ---------------------------------------------------------------- A: Family Z 最小 episode(a2 + b1b)、全Section
ZEP_STORY = {
    "a2": [
        ("full_story_part1_c1", "narrator", "Coffee beans have become cheaper. But the price tag in a shop may not change right away."),
        ("full_story_part1_c2", "melos", "I did not see a lower price today."),
        ("full_story_part2_c1", "narrator", "A price index fell 8.7% from the previous month, a report said."),
        ("full_story_part3_c1", "narrator", "Shops may keep their prices for about nine months."),
    ],
    "b1b": [
        ("full_story_part1_c1", "narrator", "Coffee beans have become cheaper. But the price tag in a shop may not change right away."),
        ("full_story_part1_c2", "melos", "I did not see a lower price today."),
        ("full_story_part2_c1", "narrator", "A price index fell 8.7% from the previous month, a report said."),
        ("full_story_part3_c1", "narrator", "Shops may keep their prices for about nine months."),
    ],
}
ZEP_KP = [{"rank": 1, "used_form": "price tag", "japanese_gloss": "値札"}]
ZEP_COMMENT_JA = {1: "コーヒー豆の値段が下がっても、お店の値札はすぐには変わりません。",
                  2: "価格指数は前の月より8.7%下がったと報告されています。",
                  3: "値札が変わるまで、およそ9か月かかるかもしれません。"}
ZEP_COMMENT_EN = {1: "Cheaper beans do not always mean a cheaper cup.",
                  2: "A fall of 8.7% in an index is a big move.",
                  3: "Nine months is a long time to wait for a lower price."}
ZEP_PREVIEW = {"a2": "今日は、コーヒー豆の値段と、お店の値札のずれについてお話しします。",
               "b1b": "Today we look at why coffee bean prices fall while the price tags in shops stay the same for a while."}
ZEP_KP_EXPL = {1: "A price tag is the label that shows how much something costs in a shop."}


def zep_plan(level):
    import er063_family_z_audio_01 as Z
    story = [{"id": cid, "speaker": spk, "text": t} for cid, spk, t in ZEP_STORY[level]]
    comments = ZEP_COMMENT_JA if level == "a2" else ZEP_COMMENT_EN
    plan = Z.build_level_plan(
        level, story, ZEP_PREVIEW[level], comments, ZEP_KP, "Coffee Prices",
        japanese_title_text="コーヒー豆は値下がり。値札は、まだ旅の途中？" if level == "a2" else None,
        kp_explanations=ZEP_KP_EXPL if level == "b1b" else None)
    return Z, story, plan


def _pww_variant():
    """zep2: PASS_WITH_WARNING が自然発生しやすい原稿(Ledger low-confidence の固有名 'Melos'、JA 数字読みの曖昧表記)へ差替。"""
    ZEP_STORY["a2"][0] = ("full_story_part1_c1", "narrator", "Melos said the shop kept its price.")
    ZEP_STORY["b1b"][0] = ("full_story_part1_c1", "narrator", "Melos said the shop kept its price.")
    ZEP_COMMENT_JA[1] = "会議は十分で終わります。"
    ZEP_COMMENT_EN[1] = "Melos said that cheaper beans do not always mean a cheaper cup."


def run_zep(execute, budget, name="zep"):
    if name == "zep2":
        _pww_variant()
    out, r77, before, snap0, res, meter, ok = begin(name, budget, execute)
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    run_dir = f"{out}/run"
    res["plan"] = {}
    for level in ("a2", "b1b"):
        Z, story, plan = zep_plan(level)
        res["plan"][level] = [{"clip_id": s.clip_id, "kind": s.kind, "lang": s.language, "text": s.text} for s in plan]
    if ok:
        stage = {}
        try:
            for level in ("a2", "b1b"):
                Z, story, plan = zep_plan(level)
                r = Z.run_tts_stage(run_dir, level, plan)
                stage[level] = {k: r[k] for k in ("results_path", "evidence_path", "statuses")}
                shells = list(Z.provision_shell_assets(run_dir, level, kp_count=1))
                res.setdefault("gate", {})[level] = Z.run_audio_gate(run_dir, level, plan, shells, article_text="", skip_shared_gate=True)
                tl = Z.run_assembly(run_dir, level, story, ZEP_KP, kp_third="japanese" if level == "a2" else "explanation")
                stage[level]["assembly"] = {"wav": tl["wav"], "duration_seconds": tl["duration_seconds"]}
            pages = Z.build_pages(run_dir, pages_dir=f"{out}/pages")
            stage["pages"] = pages
        except Exception as e_:  # noqa: BLE001  証拠として残す
            import traceback
            res["exception"] = f"{type(e_).__name__}: {str(e_)[:600]}"
            res["traceback"] = traceback.format_exc()[-1500:]
        res["stage_result"] = stage
    finish(out, r77, before, snap0, res, meter, extra_print=("exception",))


# ---------------------------------------------------------------- C: 3回NG -> LR(EN) / HR(JA)
LR_EN_TEXT = "Mayor Xzqwtrlk said the new bridge would open in May."
HR_JA_TEXT = "合言葉はブルルクル、グロルプ、ヴンムプ、フヌクです。"


def _run_fail_part(part, execute, budget, spec_fn, level, exception_label):
    out, r77, before, snap0, res, meter, ok = begin(part, budget, execute)
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    import er063_family_z_audio_01 as Z
    plan = [spec_fn(Z)]
    res["plan"] = [{"clip_id": c.clip_id, "kind": c.kind, "level": c.level, "text": c.text} for c in plan]
    run_dir = f"{out}/run"
    if ok:
        try:
            r = Z.run_tts_stage(run_dir, level, plan)
            res["stage_result"] = {k: r[k] for k in ("results_path", "evidence_path", "statuses")}
        except Exception as e_:  # noqa: BLE001  deferred STOP 等。証拠として種別を残す
            res["stage_exception"] = f"{type(e_).__name__}: {str(e_)[:500]}"
    finish(out, r77, before, snap0, res, meter, extra_print=("stage_exception",))


def run_lr_en(execute, budget):
    def spec(Z):
        return Z.ClipSpec("full_story_part1_c1", "b1b", "narrator", LR_EN_TEXT, voice="Aoede", role_key="NARRATOR_FULL_STORY_ADV", part=1)
    _run_fail_part("lr_en", execute, budget, spec, "b1b", "lr_en")


def run_a2_fail(execute, budget):
    def spec(Z):
        return Z.ClipSpec("full_story_part1_c1", "a2", "narrator", "Mayor Qvxzmtk said the old bridge would close in June.",
                          voice="Aoede", role_key="NARRATOR_FULL_STORY_STD", part=1)
    _run_fail_part("a2_fail", execute, budget, spec, "a2", "a2_fail")


def run_ja_hr(execute, budget):
    def spec(Z):
        return Z.ClipSpec("comment_1", "a2", "comment", HR_JA_TEXT, voice="Aoede", role_key="STD_JA_COMMENT", language="ja")
    _run_fail_part("ja_hr", execute, budget, spec, "a2", "ja_hr")


# ---------------------------------------------------------------- B: Family A (legacy n3) 最小 theme(b1b + a2 の全Section: Topic/Preview/Comment/Point見出し/Point本文/Full Story/In One Line/KP)
LEGA_PARTS = {
    "title": "Cheaper Beans, Same Price Tag",
    "part1": "Coffee beans have become cheaper. But the price tag in a shop may not change right away.",
    "part2": "A price index fell 8.7% from the previous month, a report said. Shops may keep their prices for about nine months.",
    "point_one_heading": "Why prices change slowly",
    "point_one_body": "Shops often buy beans months before they sell the coffee. So an old high price can stay on the tag.",
    "point_two_heading": "What you can do",
    "point_two_body": "You can compare several shops. You do not have to buy at the first price you see.",
    "in_one_line": "Cheaper beans do not always mean a cheaper cup right away.",
}
LEGA_SUPPORT_EN = {
    "preview": "Today we look at why coffee bean prices fall while the price tags in shops stay the same for a while.",
    "comment_1": "Listen for why a shop price does not change right away.",
    "comment_2": "A fall of 8.7 percent in an index is a big move. Now, why do shops wait?",
    "comment_3": "Cheaper beans do not always mean a cheaper cup. Next, what can you do?",
    "comment_4": "You can compare shops before you buy. Finally, one line to remember.",
}
LEGA_SUPPORT_JA = {
    "preview": "今日は、コーヒー豆の値段と、お店の値札のずれについてお話しします。",
    "comment_1": "お店の値札がすぐに変わらない理由を聞いてみましょう。",
    "comment_2": "価格指数は前の月より8.7%下がりました。では、お店はなぜ待つのでしょうか。",
    "comment_3": "豆が安くなっても、コーヒーがすぐ安くなるとは限りません。次は、私たちにできることです。",
    "comment_4": "買う前にお店を比べることができます。最後に、英語のまとめを聞きましょう。",
}
LEGA_KP = {"items": [{"rank": 1, "used_form": "price tag", "japanese_gloss": "値札", "japanese_gloss_tts": "ねふだ"}]}
LEGA_JA_TITLE = "コーヒー豆は値下がり。値札は、まだ旅の途中？"


def run_lega(execute, budget):
    out, r77, before, snap0, res, meter, ok = begin("lega", budget, execute, copy_master=True)
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    theme_dir = f"{out}/theme"
    for lvl, sup in (("b1b", LEGA_SUPPORT_EN), ("a2", LEGA_SUPPORT_JA)):
        d = f"{theme_dir}/{lvl}"
        os.makedirs(f"{d}/key_phrases", exist_ok=True)
        json.dump(LEGA_PARTS, open(f"{d}/parts.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        json.dump(sup, open(f"{d}/{'b1_support_texts' if lvl == 'b1b' else 'a2_support_texts'}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        json.dump(LEGA_KP, open(f"{d}/key_phrases/keywords_canonicalized.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    theme = {"theme_id": "auw06b_min", "out_dir": theme_dir}
    if ok:
        import er003_v1_n3_01_tts_generate as n3
        n3.JAPANESE_TITLES["auw06b_min"] = LEGA_JA_TITLE
        stage = {}
        try:
            stage["b1b"] = n3.generate_b1_segments(theme)
            stage["a2"] = n3.generate_a2_segments(theme)
        except Exception as e_:  # noqa: BLE001
            import traceback
            res["exception"] = f"{type(e_).__name__}: {str(e_)[:600]}"
            res["traceback"] = traceback.format_exc()[-1500:]
        res["stage_result"] = stage
    finish(out, r77, before, snap0, res, meter, extra_print=("exception",))


# ---------------------------------------------------------------- B: Family X(Production runner CLI を in-process で tts -> assemble -> player。scaffold 成果物のみ既存 Coffee run からコピー)
X_SRC = "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01"


def _copy_x_scaffold(xdir):
    import shutil
    for lvl, sup in (("a2", "a2_support_texts.json"), ("b1b", "b1_support_texts.json")):
        os.makedirs(f"{xdir}/{lvl}", exist_ok=True)
        for f in ("parts.json", "segment_plan.json", sup):
            shutil.copyfile(f"{X_SRC}/{lvl}/{f}", f"{xdir}/{lvl}/{f}")
        kd = f"{xdir}/{lvl}/key_phrases"
        if not os.path.exists(kd):
            shutil.copytree(f"{X_SRC}/{lvl}/key_phrases", kd, ignore=shutil.ignore_patterns("*_attempt_invalid"))
    os.makedirs(f"{xdir}/audit", exist_ok=True)
    shutil.copyfile(f"{X_SRC}/audit/scaffold_article_sha256.json", f"{xdir}/audit/scaffold_article_sha256.json")


def run_xrun(execute, budget):
    out, r77, before, snap0, res, meter, ok = begin("xrun", budget, execute, copy_master=True)
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    xdir = f"{out}/x_out"
    _copy_x_scaffold(xdir)
    import er019_family_x_audio_production_runner_01 as X
    common = ["--slug", "coffee_prices", "--run", "run_v5_ms_01", "--level", "both", "--out-dir", xdir,
              "--tts-backend", "speech_metadata_flash_lite", "--style-profile", "coffee_n01_r2_p3_e1", "--budget-jpy", str(min(budget, 40) if budget else 40)]
    stages = ["plan"] if not ok else ["tts", "assemble", "player"]
    stage_log = {}
    for st in stages:
        sys.argv = ["er019_family_x_audio_production_runner_01.py", "--stage", st] + common
        try:
            X.main()
            stage_log[st] = "OK"
        except SystemExit as e_:
            stage_log[st] = f"SystemExit({e_.code})"
        except Exception as e_:  # noqa: BLE001
            import traceback
            stage_log[st] = f"{type(e_).__name__}: {str(e_)[:500]}"
            res["traceback_" + st] = traceback.format_exc()[-1500:]
            break
    res["stage_result"] = stage_log
    finish(out, r77, before, snap0, res, meter)


# ---------------------------------------------------------------- B: Family B(Production runner main() level=a2 stage=all。出力先定数のみ evidence へ差替)
def run_brun(execute, budget):
    out, r77, before, snap0, res, meter, ok = begin("brun", budget, execute, copy_master=True)
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    import er012_b_family_production_runner_01 as B
    base = f"{out}/b_a2"
    B.A2_OUT_DIR = base
    B.A2_A2_DIR = f"{base}/a2"
    B.A2_NARRATION_DIR = f"{base}/a2/narration"
    B.A2_KP_DIR = f"{base}/a2/key_phrases"
    B.A2_AUDIT_DIR = f"{base}/a2/audit"
    B.A2_COST_LOG_PATH = f"{base}/a2/audit/raw_usage_log.jsonl"
    res["paths"] = {"A2_OUT_DIR": base}
    if ok:
        sys.argv = ["er012_b_family_production_runner_01.py", "all", "a2"]
        try:
            B.main()
            res["stage_result"] = {"main_a2_all": "OK"}
        except SystemExit as e_:
            res["stage_result"] = {"main_a2_all": f"SystemExit({e_.code})"}
        except Exception as e_:  # noqa: BLE001
            import traceback
            res["stage_result"] = {"main_a2_all": f"{type(e_).__name__}: {str(e_)[:500]}"}
            res["traceback"] = traceback.format_exc()[-1500:]
    finish(out, r77, before, snap0, res, meter)


# ---------------------------------------------------------------- B: Family C(Production runner CLI main() level=a2、--only-segments で narrator/device/brother の3 segment のみ再生成、他は reuse_from)
def run_crun(execute, budget):
    out, r77, before, snap0, res, meter, ok = begin("crun", budget, execute, copy_master=True)
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    cfg = json.load(open("er013_output/family_c_production/memory/article_config.json", encoding="utf-8"))
    cfg["levels"] = {"a2": cfg["levels"]["a2"]}
    cfg_path = f"{out}/c_out/article_config.json"
    os.makedirs(os.path.dirname(cfg_path), exist_ok=True)
    json.dump(cfg, open(cfg_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    import er013_family_c_production_runner_01 as C
    segs = ["story_003", "story_002", "story_007"]
    res["only_segments"] = segs
    if ok:
        sys.argv = ["er013_family_c_production_runner_01.py", "--config", cfg_path, "--level", "a2", "--budget-jpy", "15",
                    "--only-segments"] + segs
        try:
            C.main()
            res["stage_result"] = {"main": "OK"}
        except SystemExit as e_:
            res["stage_result"] = {"main": f"SystemExit({e_.code})"}
        except Exception as e_:  # noqa: BLE001
            import traceback
            res["stage_result"] = {"main": f"{type(e_).__name__}: {str(e_)[:500]}"}
            res["traceback"] = traceback.format_exc()[-1500:]
    finish(out, r77, before, snap0, res, meter)


# ---------------------------------------------------------------- A: Point見出し(見出し・短文の独立QA維持の確認: 数値/否定を含む見出し + 固有名詞見出し)
HEAD_CASES = [("head_numeric", "Why prices fell 8.7 percent in one month"),
              ("head_negation", "Why a cheaper bean does not mean a cheaper cup"),
              ("head_hardname", "Why Mayor Xzqwtrlk delayed the bridge")]


def run_head(execute, budget):
    out, r77, before, snap0, res, meter, ok = begin("head", budget, execute)
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    res["plan"] = HEAD_CASES
    if ok:
        import er003_v1_n3_01_tts_generate as n3
        import er003_v1_sing01_point_headings_aoede as ph
        import er005_cost_logger as cl
        rows = []
        for name, text in HEAD_CASES:
            wav = f"{out}/run/b1b/narration/{name}.wav"
            os.makedirs(os.path.dirname(wav), exist_ok=True)
            with cl.segment_context(name):
                r = ph.generate(n3.tts_safe_number_words_en(n3.tts_safe_en(text)), wav)
            aj = r.get("asr_judgement") or {}
            rows.append({"case": name, "canonical": text, "status": r.get("status"), "asr_text": r.get("asr_text"), "state": aj.get("state"),
                         "reason": aj.get("reason_code"), "value_guard": (aj.get("final_gate") or {}).get("value_guard"),
                         "negation_diff": (aj.get("final_gate") or {}).get("negation_diff"),
                         "secondary_called": (aj.get("secondary") or {}).get("called"), "secondary_text": (aj.get("secondary") or {}).get("text"),
                         "max_len": r.get("max_len"), "disfluency_checked": r.get("disfluency_checked"), "n_attempts": len(r.get("attempts_log") or []),
                         "has_asr_judgement": bool(aj)})
        res["rows"] = rows
        res["stage_result"] = {"headings": [(x["case"], x["status"], x["state"]) for x in rows]}
    finish(out, r77, before, snap0, res, meter)


# ---------------------------------------------------------------- B: Family B (B1) Voice A/B 本文 leaf(er012 run_tts と同一引数。B1 全体は LLM scaffold を要するため segment 単位)
def run_bb1(execute, budget):
    out, r77, before, snap0, res, meter, ok = begin("bb1", budget, execute)
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    import er012_b_family_production_runner_01 as B
    base = f"{out}/b_b1"
    B.OUT_DIR = base
    B.OUT_B1_DIR = f"{base}/b1b"
    B.NARRATION_DIR = f"{base}/b1b/narration"
    B.COST_LOG_PATH = f"{base}/audit/raw_usage_log.jsonl"
    prep = B.prepare()   # Production の prepare(): 記事読取+parts 構築+parts.json 書出(API 0、出力先は evidence)
    parts = prep["parts"]
    res["plan"] = {"point_one_body": parts["point_one_body"][:120], "point_two_body": parts["point_two_body"][:120], "voice_a": "Algieba", "voice_b": "Erinome"}
    if ok:
        import er005_cost_logger as cl
        os.makedirs(B.NARRATION_DIR, exist_ok=True)
        os.makedirs(f"{base}/b1b/audit", exist_ok=True)
        results = {}
        try:
            for name, text, voice_name in (("point_one", parts["point_one_body"], "Algieba"), ("point_two", parts["point_two_body"], "Erinome")):
                with cl.segment_context(name):
                    results[name] = B.b1prod.generate_voice_body_wide_margin(
                        B.tts_gen.tts_safe_news_en(text), f"{B.NARRATION_DIR}/{name}.wav", voice_name,
                        enable_connected_speech_equivalence_layer=True, enable_repetition_qa=True)   # er012:run_tts と同一引数
                results[name]["canonical_text"] = text
            B.save_json(f"{base}/b1b/audit/tts_generation_results.json", {"segments": results, "key_phrases": {}})
            import er078_pass_with_warning_registry_01 as pww
            res["listening_list"] = pww.write_listening_list_safe(f"{base}/b1b", standalone_html=True)
            res["stage_result"] = {n: r.get("status") for n, r in results.items()}
        except Exception as e_:  # noqa: BLE001
            res["exception"] = f"{type(e_).__name__}: {str(e_)[:500]}"
    finish(out, r77, before, snap0, res, meter, extra_print=("exception",))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("part", choices=["zep", "zep2", "lr_en", "ja_hr", "lega", "xrun", "brun", "crun", "head", "a2_fail", "bb1"])
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--budget-jpy", type=float, default=0.0)
    a = ap.parse_args()
    os.chdir(ROOT)
    {"zep": run_zep, "zep2": lambda e, b: run_zep(e, b, "zep2"), "lr_en": run_lr_en, "ja_hr": run_ja_hr, "lega": run_lega, "xrun": run_xrun, "brun": run_brun, "crun": run_crun, "head": run_head, "a2_fail": run_a2_fail, "bb1": run_bb1}[a.part](a.execute, a.budget_jpy)


if __name__ == "__main__":
    main()
