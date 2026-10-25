# -*- coding: utf-8 -*-
"""Family Y Production runner(FAMILY-Y-PRODUCTION-LAUNCH-01 委任_02B)。

Zのstage framework(er026_family_z_fiction_production_runner_01)と同型の骨格を、Yの契約(5パート・Voice3人・Comment 1〜3・IOLなし)で実装する。
- stage単位: ensure_stage(来歴 provenance + 入力sha + 出力sha)、DEPENDENTS(親を再生成すると子孫がstale)、--regenerate-stage、resume(再利用はAPI 0)。
- 安全装置: STOP/STOP_ALLセンチネル、RUN_LOCK(二重起動拒否)、RESTART_STORM(短時間の再起動連発の遮断)はer062の関数をそのまま使う(再実装しない)。
  exit code: STOP=3、RUN_LOCK/KP_REVIEW_PENDING=4(stdoutの `[KP_REVIEW_PENDING]` で区別)、その他の停止=2。
- KP Human Review: 最初から er119_kp_wiring_01.run_kp_with_review 経由(Human確認 or 明示の不在宣言まで rc=4 で待機。有料の後続工程へ進まない)。
- 実modelの記録: 各stageの来歴entryに routing_key / requested_model / actual_model_id / response_id / prompt_sha256 / cost を残す(closing_recordはtext stage)。
- mode: dry-run(副作用0・API 0)/ mock(偽client・偽TTS。実APIへ出ない)/ real(承認予算内のみ。本委任では起動しない)。
- Part 2(文法)・Part 1(Vocabulary & Expressions)は『未接続スロット』として study_text_slots.json に記録する(PART2-GRAMMAR-PRODUCTION-WIRING-01 は別案件で未配線)。
- 隔離: 本ファイルはYの新入口。X/Zのruntime・既存Prompt・閾値・辞書は無変更。Chunk TTS・中核数値v4/J2はY非適用。
"""
from __future__ import annotations

import argparse
import contextlib
import dataclasses
import json
import os
import re
import shutil
import sys
import time

import er121_family_y_structure_01 as ys

MANAGEMENT_ID = ys.MANAGEMENT_ID
RUN_ROOT = "er121_output/family_y_production_01"
DEFAULT_RUN = "run_01"
APPROVED_BUDGET_MAX_JPY = 150.0          # 案件個別Cap(BUDGET_PLAN_01: 見積上限113円+約30%)。これを超える承認は受け付けない
WARN_THRESHOLD_JPY = 100.0
STAGES = ("seed_check", "text", "translate", "support", "kp", "tts_b1b", "tts_a2", "gate", "assemble", "pages", "page_verify")
STAGE_EST_JPY = {"text": 45.0, "translate": 12.0, "support": 6.0, "kp": 10.0, "tts_b1b": 30.0, "tts_a2": 30.0}
TTS_CLIP_EST_JPY = 1.0
STYLE_PROFILE = "default"
LEVELS = ("b1b", "a2")

# 来歴(provenance)の単位。CLIのstageより細かい。--regenerate-stage の許可値でもある。
UNIT_NAMES = ("text", "translate_b1b", "translate_a2", "support_b1b", "support_a2", "kp_b1b", "kp_a2", "kp_expl_b1b", "tts_b1b", "tts_a2")
# 親→子。親を明示再生成すると、推移的な子孫がstaleになり、明示 --regenerate-stage が無い限りSTOP(自動再生成しない)。
DEPENDENTS = {
    "text": ["translate_b1b"],
    "translate_b1b": ["translate_a2", "support_b1b", "kp_b1b", "tts_b1b"],
    "translate_a2": ["support_a2", "kp_a2", "tts_a2"],
    "support_b1b": ["tts_b1b"], "support_a2": ["tts_a2"],
    "kp_b1b": ["kp_expl_b1b", "tts_b1b"], "kp_a2": ["tts_a2"], "kp_expl_b1b": ["tts_b1b"],
}
# 来歴entryの `routing_key`(er006 PROCESS_MODEL_MAP の登録名)。unit→key
UNIT_ROUTING_KEY = {"translate_b1b": "FAMILY_Y_TRANSLATE_ADV", "translate_a2": "FAMILY_Y_TRANSLATE_STD"}


class YE2EStop(RuntimeError):
    """Y E2EのSTOP(自動で通さない・自動再生成しない)。"""


class YBudgetStop(YE2EStop):
    pass


class YTextCoreNotConnected(YE2EStop):
    pass


class YKpReviewPending(YE2EStop):
    """KP Human Review待ち(失敗ではなく待機)。pending=[{level,kp_dir,request_md}]。"""

    def __init__(self, message, pending=None):
        super().__init__(message)
        self.pending = pending or []


# ------------------------------------------------------------
# 遅延import(軽量importを保つ。dry-run/describeはX音声系を読まない)
# ------------------------------------------------------------
_MODS = None


def _m():
    global _MODS
    if _MODS is None:
        import types
        import er062_family_z_structure_01 as st
        import er062_family_z_writer_01 as w62
        _MODS = types.SimpleNamespace(st=st, w62=w62)
    return _MODS


def _routing():
    import er006_model_routing_contract_01 as routing
    return routing


def _ya():
    import er121_family_y_audio_01 as ya
    return ya


def _khr():
    import er119_kp_human_review_01 as khr
    return khr


def _sha(s) -> str:
    return _m().st.sha(s)


# ------------------------------------------------------------
# 予算(新規API呼出の前に累計+見積が上限を超えるならSTOP)
# ------------------------------------------------------------
class E2EBudget:
    def __init__(self, approved_jpy: float, warn_jpy: float = WARN_THRESHOLD_JPY, spent_fn=None, ack_warn: bool = False):
        if approved_jpy <= 0:
            raise YBudgetStop("FAMILY_Y_BUDGET_NOT_APPROVED: --approved-budget-jpy(>0)が必須です")
        if approved_jpy > APPROVED_BUDGET_MAX_JPY:
            raise YBudgetStop(f"FAMILY_Y_BUDGET_ABOVE_CASE_CAP: {approved_jpy} > {APPROVED_BUDGET_MAX_JPY}(個別Cap超過はFable報告・承認が必要)")
        self.approved, self.warn, self.ack_warn = float(approved_jpy), float(warn_jpy), bool(ack_warn)
        self.spent_fn = spent_fn or (lambda: 0.0)
        self.log = []

    def spent(self) -> float:
        v = self.spent_fn()
        return float(v[0] if isinstance(v, tuple) else v)

    def limit(self) -> float:
        return self.approved if self.ack_warn else min(self.warn, self.approved)

    def remaining(self) -> float:
        return max(self.limit() - self.spent(), 0.0)

    def guard(self, label: str, est_jpy: float) -> float:
        s = self.spent()
        self.log.append({"label": label, "est_jpy": est_jpy, "spent_jpy": round(s, 4)})
        if s + est_jpy > self.limit():
            kind = "APPROVED_CAP" if self.ack_warn else "WARN_THRESHOLD"
            raise YBudgetStop(f"FAMILY_Y_BUDGET_STOP({kind}): label={label!r} spent={s:.2f} + est={est_jpy:.2f} > limit={self.limit():.2f}"
                              f"(warn={self.warn}, approved={self.approved})。新規API呼出の前に停止。続行は確認の上 --ack-warn-threshold を付けて再実行")
        return s


def make_real_spent_fn(cost_log_path: str):
    def fn():
        import er019_family_x_audio_production_runner_01 as x_runner     # compute_cost_jpy_so_far(読み取り専用)
        return x_runner.compute_cost_jpy_so_far(cost_log_path)[0]
    return fn


# ------------------------------------------------------------
# Context
# ------------------------------------------------------------
@dataclasses.dataclass
class YContext:
    slug: str = "y_article"
    run: str = DEFAULT_RUN
    mode: str = "dry-run"                       # dry-run | mock | real
    run_root: str = RUN_ROOT
    pages_dir: str = None                       # None -> <out_dir>/pages(公開dirではない。公開は別手順)
    theme_package_path: str = None
    budget: object = None
    llm_client: object = None
    hooks: dict = dataclasses.field(default_factory=dict)
    only_segments: object = None
    regenerate_stage: object = None
    mock_api: object = None

    def __post_init__(self):
        if self.pages_dir is None:
            self.pages_dir = f"{self.run_root}/{self.slug}/{self.run}/pages"

    @property
    def management_id(self) -> str:
        return MANAGEMENT_ID

    @property
    def theme_tag(self) -> str:
        return f"FAMILY_Y_PRODUCTION_{re.sub(r'[^A-Za-z0-9]+', '_', self.slug).upper()}"

    @property
    def out_dir(self) -> str:
        return f"{self.run_root}/{self.slug}/{self.run}"

    def stage_context(self, name: str):
        if self.mode != "real":
            return contextlib.nullcontext()
        import er005_cost_logger as cl
        return cl.logging_context(self.theme_tag, name)


def _stop_sentinel(ctx, where):
    _m().st.check_stop_sentinel(where, ctx.out_dir)


def _guard(ctx, label, est):
    _stop_sentinel(ctx, label)
    if ctx.budget is not None:
        ctx.budget.guard(label, est)


def _regen(ctx, name) -> bool:
    return ctx.regenerate_stage == name


# ------------------------------------------------------------
# 来歴(Yのstage単位。w62.ensure_stageがそのまま使えるよう、Provenanceの規則だけY用に差し替える)
# ------------------------------------------------------------
def _make_prov_class():
    w62 = _m().w62

    class YProvenance(w62.Provenance):
        def stage_entry(self, name):
            return self.data["downstream_stages"].get(name)

        def set_entry(self, name, entry):
            if name in self.data["downstream_stages"]:
                self.data["regenerations"].append({"stage": name, "replaced_at": w62._now(), "old": self.data["downstream_stages"][name]})
            self.data["downstream_stages"][name] = entry
            if name in self.data["downstream_stale"]:
                self.data["downstream_stale"].remove(name)

        def mark_stale_descendants(self, name):
            seen, todo = [], list(DEPENDENTS.get(name, []))
            while todo:
                n = todo.pop(0)
                if n not in seen:
                    seen.append(n)
                    todo.extend(DEPENDENTS.get(n, []))
            for n in seen:
                if self.stage_entry(n) is not None and n not in self.data["downstream_stale"]:
                    self.data["downstream_stale"].append(n)

        def save(self):
            w62.wj(self.path, self.data)
    return YProvenance


def _prov(ctx):
    w62 = _m().w62
    seed_sha = w62.file_sha(ctx.theme_package_path) if ctx.theme_package_path and os.path.exists(ctx.theme_package_path) else "no_theme_package"
    return _make_prov_class()(f"{ctx.out_dir}/provenance.json", ctx.slug, seed_sha)


def _ensure(ctx, prov, name, input_sha, out_path, runner):
    if name not in UNIT_NAMES:
        raise YE2EStop(f"FAMILY_Y_UNKNOWN_UNIT: {name}")
    return _m().w62.ensure_stage(prov, name, input_sha, out_path, runner, regenerate=_regen(ctx, name))


def _rd(path):
    return _m().w62.rd(path)


def _rj(path):
    return _m().w62.rj(path)


def _wt(path, text):
    _m().w62.wt(path, text)


def _wj(path, obj):
    _m().w62.wj(path, obj)


def _ja_path(ctx):
    return f"{ctx.out_dir}/text/article_ja.md"


def _level_text_path(ctx, lv):
    return f"{ctx.out_dir}/translate/{lv}.md"


# ------------------------------------------------------------
# stage: seed_check(読み取りのみ。API 0・書込 0)
# ------------------------------------------------------------
def _text_core(ctx):
    tc = ctx.hooks.get("text_core")
    if tc is not None:
        return tc
    if ctx.mode != "real":
        raise YE2EStop("FAMILY_Y_NO_TEXT_CORE_HOOK: mock/dry-runでは偽text core(hooks.text_core)が必要(実APIへは出さない)")
    import er121_family_y_text_core_01 as tc
    return tc


def stage_seed_check(ctx) -> dict:
    routing = _routing()
    res = {"management_id": MANAGEMENT_ID, "family": ys.FAMILY, "entry_status": ys.ENTRY_STATUS}
    res["voice_assignment"] = ys.verify_voice_assignment()
    keys = ("FAMILY_Y_CLOSING_GENERATE", "FAMILY_Y_CLOSING_REWRITE", "FAMILY_Y_LEAK_JUDGE", "FAMILY_Y_VOICE_GENERATE", "FAMILY_Y_VOICE_REWRITE",
            "FAMILY_Y_LEAD_GENERATE", "FAMILY_Y_PERSONA_INTRO", "FAMILY_Y_TRANSLATE_ADV", "FAMILY_Y_TRANSLATE_STD")
    res["routing"] = {k: routing.PROCESS_MODEL_MAP.get(k) for k in keys}
    missing = [k for k, v in res["routing"].items() if not v]
    if missing:
        raise YE2EStop(f"FAMILY_Y_ROUTING_KEY_UNREGISTERED: {missing}(er006へ登録されていません。fail-closed)")
    res["chunk_tts"] = ys.chunk_decision_record("b1b")
    res["core_numeric_applicable"] = ys.CORE_NUMERIC_APPLICABLE
    tp = ctx.theme_package_path
    res["theme_package"] = {"path": tp, "exists": bool(tp and os.path.exists(tp))}
    tc = ctx.hooks.get("text_core")
    if tc is None and ctx.mode == "real":
        import er121_family_y_text_core_01 as tc
    res["text_core_connected"] = bool(tc is not None and hasattr(tc, "produce_article"))
    res["study_text_slots"] = STUDY_TEXT_SLOTS
    return res


STUDY_TEXT_SLOTS = {"part1_vocabulary_expressions": "未接続(Yへは未配線。別案件)", "part2_grammar": "未接続(PART2-GRAMMAR-PRODUCTION-WIRING-01はX/Zのみ。Y接続は別案件)"}


# ------------------------------------------------------------
# stage: text(JA 5パート記事。text core adapter。未接続ならSTOP)
# ------------------------------------------------------------
def stage_text(ctx) -> dict:
    w62 = _m().w62
    if not ctx.theme_package_path or not os.path.exists(ctx.theme_package_path):
        raise YE2EStop("FAMILY_Y_THEME_PACKAGE_MISSING: --theme-package <json> が必要です(Theme Package=実在意見ベースの入力。存在しないままVoiceを作らない)")
    tp = _rj(ctx.theme_package_path)
    prov = _prov(ctx)

    def runner():
        tc = _text_core(ctx)
        fn = getattr(tc, "produce_article", None)
        if fn is None:
            raise YTextCoreNotConnected(
                "FAMILY_Y_TEXT_CORE_NOT_CONNECTED: er121_family_y_text_core_01.produce_article(Voice/Lead/紹介の生成+Gate+Closing)が未接続です。"
                "Closing lane(produce_closing)だけでは記事全体を作れません。02Aの記事組立I/F確定後に接続(未接続のまま本文を手書き・流用しない)")
        _guard(ctx, "text", STAGE_EST_JPY["text"])
        out = f"{ctx.out_dir}/text"
        res = fn(ctx.llm_client, slug=ctx.slug, theme_package=tp, out_dir=out, guard=lambda label: _guard(ctx, label, 1.0))
        for k in ("title", "lead", "intros", "voices", "closing", "closing_record"):
            if not res.get(k):
                raise YE2EStop(f"FAMILY_Y_TEXT_CORE_RESULT_INCOMPLETE: {k}がありません(closing_recordは実model/routing/prompt shaを含むため必須)")
        ja = ys.render_y_article(res["title"], res["lead"], res["intros"], res["voices"], res["closing"])
        chk = ys.check_y_article(ja, lang="ja")
        if not chk["ok"]:
            raise YE2EStop(f"FAMILY_Y_JA_CONTRACT_VIOLATION: {chk['violations']}(音声へAIアナウンスを入れない。Lead/紹介の再生成で対処。本文の手修正はしない)")
        _wj(f"{out}/text_records.json", {"closing_record": res["closing_record"], "records": res.get("records") or {}, "theme_package_sha256": w62.file_sha(ctx.theme_package_path),
                                        "entry_status": ys.ENTRY_STATUS})
        return ja, {"closing_source": res["closing_record"].get("source"), "closing_final_sha256": res["closing_record"].get("final_sha256"),
                    "text_records_sha256": w62.file_sha(f"{out}/text_records.json")}

    r = _ensure(ctx, prov, "text", _sha(f"text|{w62.file_sha(ctx.theme_package_path)}"), _ja_path(ctx), runner)
    return {"status": r["status"], "entry": r["entry"]}


# ------------------------------------------------------------
# stage: translate(英訳=X承認済み関数を呼ぶだけ。Advanced=忠実英訳、Standard=Advancedから)
# ------------------------------------------------------------
def _chain_fields(unit, res, requested) -> dict:
    return {"routing_key": UNIT_ROUTING_KEY[unit], "requested_model": requested, "actual_model_id": res.model_id_actual,
            "response_id": res.response_id, "attempts": res.attempts, "retried": res.retried, "cost_jpy": res.cost_jpy,
            "fallback_detected": res.fallback_detected}


def _paragraph_retry_must_fix() -> list:
    import er012_e_family_entertainment_two_level_runner_01 as efam
    return list(efam._FAMILY_X_PARAGRAPH_RETRY_MUST_FIX)


def _translate_once(ctx, lv, ja_text, adv_text):
    routing = _routing()
    if lv == "b1b":
        import er003_v1_n3_01_advanced_adaptation_generate as adv_gen
        req = routing.require_model("FAMILY_Y_TRANSLATE_ADV", routing.WRITER_MODEL)
        fn = ctx.hooks.get("translate_adv_fn") or adv_gen.generate_family_x_faithful_translation

        def gen(must_fix):
            r = fn(ja_text, client=ctx.llm_client, model=req, must_fix=must_fix)
            return r, f"# {r.title}\n\n{r.body}\n"
    else:
        import er003_v1_n3_01_standard_a2_generate as std_gen
        req = routing.require_model("FAMILY_Y_TRANSLATE_STD", routing.WRITER_MODEL)
        fn = ctx.hooks.get("translate_std_fn") or std_gen.generate_family_x_standard_a2_no_heading

        def gen(must_fix):
            r = fn(adv_text, client=ctx.llm_client, model=req, must_fix=must_fix)
            return r, r.text.strip() + "\n"
    return req, gen


def stage_translate(ctx) -> dict:
    w62 = _m().w62
    prov = _prov(ctx)
    ja = _rd(_ja_path(ctx))
    summary = {}
    adv_text = None
    for lv in LEVELS:
        if lv == "a2":
            adv_text = _rd(_level_text_path(ctx, "b1b"))
        unit = f"translate_{lv}"
        base_mf = ys.y_contrast_must_fix() + (ys.y_no_iol_must_fix() if lv == "a2" else [])
        in_sha = _sha(f"{unit}|{_sha(ja)}|{_sha(adv_text) if adv_text else ''}|{_sha(json.dumps(base_mf, ensure_ascii=False, sort_keys=True))}")

        def runner(lv=lv, unit=unit, base_mf=base_mf, adv_text=adv_text):
            req, gen = _translate_once(ctx, lv, ja, adv_text)
            _guard(ctx, unit, STAGE_EST_JPY["translate"] / 2)
            res, text = gen(base_mf)
            chk = ys.check_y_article(text, lang="en")
            retried = False
            if not chk["ok"] and any(("PARAGRAPH_COUNT" in v or "NOT_2_LINES" in v or "MULTI_LINE" in v) for v in chk["violations"]):
                retried = True
                _guard(ctx, unit + "_retry", STAGE_EST_JPY["translate"] / 2)       # 構造違反のみ1回だけ再試行(上限1回。それでも違反ならSTOP)
                res, text = gen(base_mf + _paragraph_retry_must_fix())
                chk = ys.check_y_article(text, lang="en")
            if not chk["ok"]:
                raise YE2EStop(f"FAMILY_Y_EN_CONTRACT_VIOLATION({lv}): {chk['violations']}(英訳の契約違反。自動で本文を直さずSTOP。再試行済み={retried})")
            if not ys.model_id_matches(req, res.model_id_actual):
                raise YE2EStop(f"FAMILY_Y_MODEL_DRIFT({unit}): requested={req} actual={res.model_id_actual}")
            return text, {**_chain_fields(unit, res, req), "contract_retried": retried}

        r = _ensure(ctx, prov, unit, in_sha, _level_text_path(ctx, lv), runner)
        summary[lv] = r["status"]
    return summary


# ------------------------------------------------------------
# stage: support(Preview / Comment 1〜3。Comment 4・In One Lineは無い)
# ------------------------------------------------------------
def _support_modules(lv):
    if lv == "b1b":
        import er003_v1_b1_scaffold_01_generate as gen
        import er019_family_x_audio_production_runner_01 as xr
        return gen, xr._b1_support_model()
    import er003_v1_iran01_a2_generate as gen
    import er019_family_x_audio_production_runner_01 as xr
    return gen, xr._a2_support_model()


def stage_support(ctx) -> dict:
    prov = _prov(ctx)
    summary = {}
    for lv in LEVELS:
        text = _rd(_level_text_path(ctx, lv))
        unit = f"support_{lv}"
        out_path = f"{ctx.out_dir}/support/{lv}_support.json"

        def runner(lv=lv, text=text):
            gen, model = _support_modules(lv)
            parsed = ys.split_y_article(text)
            ctxs = ys.comment_contexts(parsed)
            fn = ctx.hooks.get("support_fn") or gen.run_support_text

            def call(role, block, label):
                _guard(ctx, f"support_{lv}_{label}", 1.0)
                r = fn(ctx.llm_client, role, block, model=model)
                if r.get("status") != "OK" or not (r.get("text") or "").strip():
                    raise YE2EStop(f"FAMILY_Y_SUPPORT_FAILED({lv},{label}): status={r.get('status')}")
                return r
            c1 = call(gen.COMMENT_1_ROLE, ctxs["comment_1"], "comment_1")
            c2 = call(ys.Y_COMMENT_2_ROLE[lv], ctxs["comment_2"], "comment_2")
            c3 = call(ys.Y_COMMENT_3_ROLE[lv], ctxs["comment_3"], "comment_3")
            prev_role = gen.PREVIEW_ROLE.format(comment_1=c1["text"], comment_2=c2["text"])
            prev = call(prev_role, ctxs["preview"], "preview")
            res = {"preview": prev, "comment_1": c1, "comment_2": c2, "comment_3": c3}
            pat = ys.AI_ANNOUNCE_RE if lv == "a2" else ys.AI_ANNOUNCE_EN_RE
            hit = [k for k, v in res.items() if pat.search(v["text"])]
            if hit:
                raise YE2EStop(f"FAMILY_Y_AI_ANNOUNCE_IN_SUPPORT({lv}): {hit}(音声へAIアナウンスを入れない。再生成が必要)")
            doc = {k: v["text"] for k, v in res.items()}
            doc["_meta"] = {"model_requested": model, "comment_4_generated": False, "attempts": {k: v.get("attempts") for k, v in res.items()}}
            return json.dumps(doc, ensure_ascii=False, indent=2), {"routing_key": "B1_SUPPORT" if lv == "b1b" else "A2_SUPPORT", "requested_model": model}

        r = _ensure(ctx, prov, unit, _sha(f"{unit}|{_sha(text)}"), out_path, runner)
        summary[lv] = r["status"]
    return summary


# ------------------------------------------------------------
# stage: kp(KP Human Review経由。rc=4待機)
# ------------------------------------------------------------
def _kp_src_dir(ctx, lv):
    return f"{ctx.out_dir}/key_phrases/{lv}"


def _kp_assets_dir(ctx, lv):
    return f"{ctx.out_dir}/{lv}/key_phrases"


def install_kp_assets(ctx, lv) -> str:
    src = f"{_kp_src_dir(ctx, lv)}/keywords_canonicalized.json"
    if not os.path.exists(src):
        raise YE2EStop(f"FAMILY_Y_KP_CANONICALIZED_MISSING: {src}")
    dst = f"{_kp_assets_dir(ctx, lv)}/keywords_canonicalized.json"
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
    return dst


def _review_signature(ctx, lv):
    r = _khr().load_review(_kp_src_dir(ctx, lv))
    return None if r is None else r.get("selection_signature")


def _assert_kp_review_consistent(ctx, lv, where) -> None:
    """消費側検査: review/確定物が現在のKP assetsと一致すること。未確定=待機(rc=4)、不整合=STOP。"""
    khr = _khr()
    src = _kp_src_dir(ctx, lv)
    try:
        rev = khr.require_final_consistent(src, level=lv, require_src_contract=False)
    except khr.KpReviewNotConfirmed as e:
        raise YKpReviewPending(f"{khr.PENDING_MARKER} {where}: {e}", [{"level": lv, "kp_dir": src, "request_md": khr.paths(src)["request"]}]) from e
    except khr.KpReviewInconsistent as e:
        raise YE2EStop(f"FAMILY_Y_KP_REVIEW_INCONSISTENT({lv}) at {where}: {e}") from e
    if rev is None:
        raise YE2EStop(f"FAMILY_Y_KP_REVIEW_MISSING({lv}) at {where}: KP Human Reviewの記録がありません(Yは最初からreview経由。旧run互換経路は無い)")
    asset = f"{_kp_assets_dir(ctx, lv)}/keywords_canonicalized.json"
    if not os.path.exists(asset):
        raise YE2EStop(f"FAMILY_Y_KP_CANONICALIZED_MISSING: {asset}(kp stageを再実行)")
    got = sorted(it.get("candidate_id") for it in _rj(asset).get("items") or [])
    want = sorted(khr.sel_ids(rev["selection"], "kp"))
    if got != want:
        raise YE2EStop(f"FAMILY_Y_KP_ASSETS_STALE({lv}) at {where}: assetsのKP候補{got}が確定集合{want}と一致しません")


def _kp_generate_hook(ctx, lv, text):
    """test/mock用の候補生成hook。realでhookが無ければNone(=実の候補生成)。real以外でhookが無ければ実APIへ出さずSTOP。"""
    hook = ctx.hooks.get("kp_generate_fn")
    if hook is not None:
        return hook
    legacy = ctx.hooks.get("kp_fn")
    if legacy is not None:
        import er119_kp_candidates_01 as kcand
        src_level, process = ("A2", "A2_SUPPORT") if lv == "a2" else ("B1", "B1_SUPPORT")
        art_id = f"family_y_{ctx.slug}_{lv}"

        def adapter(round_no, ng_entries):
            work = f"{_kp_src_dir(ctx, lv)}/kp_candidates/round_{round_no}/work"
            os.makedirs(work, exist_ok=True)
            res = legacy(text, work, art_id, src_level, process=process)
            cs = (res.get("canonicalization") or {}).get("status")
            if res.get("status") in ("NG_REVIEW_REQUIRED", "OUTER_RETRY_EXHAUSTED") or cs != "CANONICALIZATION_PASS" or not os.path.exists(f"{work}/keywords_canonicalized.json"):
                return {"ok": False, "status": res.get("status") or cs or "OUTER_RETRY_EXHAUSTED"}
            return {"ok": True, "doc": kcand.candidate_doc_from_items(_rj(f"{work}/keywords_canonicalized.json")["items"], lv, round_no=round_no)}
        return adapter
    if ctx.mode != "real":
        raise YE2EStop(f"FAMILY_Y_KP_NO_CANDIDATE_HOOK({lv}): mock/dry-runでは候補生成hookが必要(実APIへは出さない)")
    return None


def _kp_review_step(ctx, lv, text) -> dict:
    import er119_kp_wiring_01 as kw
    khr = _khr()
    st = _m().st
    gen_hook = _kp_generate_hook(ctx, lv, text)
    red_hook = ctx.hooks.get("kp_redundancy_fn")
    if red_hook is None and ctx.mode != "real":
        def red_hook(items, name):
            return {"status": "REDUNDANCY_PASS", "duplicate_pairs": [], "model_id": None, "response_id": None, "attempts_detail": [],
                    "skipped": "mock/dry-run: Redundancy QAは実APIへ出さない"}
    try:
        return kw.run_kp_with_review(
            text=text, kp_dir=_kp_src_dir(ctx, lv), run_dir=ctx.out_dir, family="y", slug=ctx.slug, level=lv, article_id=f"family_y_{ctx.slug}_{lv}",
            stop_run_dir=ctx.out_dir, generate_hook=gen_hook, redundancy_hook=red_hook, src_fn=None, person_repair_fn=None,
            guard_fn=lambda label: _guard(ctx, label, STAGE_EST_JPY["kp"] / 2), run_hint=ctx.out_dir,
            stop_check_fn=lambda where: st.check_stop_sentinel(where, ctx.out_dir))
    except khr.KpReviewPending:
        raise
    except khr.KpReviewError as e:
        raise YE2EStop(f"FAMILY_Y_KP_REVIEW_STOP({lv}): {e}") from e


def stage_kp(ctx) -> dict:
    prov = _prov(ctx)
    st = _m().st
    summary, pending = {}, []
    for lv in LEVELS:
        text = ys.canonical_body(_rd(_level_text_path(ctx, lv)))
        review_res = _kp_review_step(ctx, lv, text)
        kr = review_res.get("kp_review") or {}
        if kr.get("state") == "PENDING":
            pending.append(kr["pending"])
            summary[lv] = {"status": "KP_REVIEW_PENDING", "pending": kr["pending"]}
            continue
        if kr.get("state") == "FAILED":
            raise YE2EStop(f"FAMILY_Y_KP_NOT_PASSED({lv}): status={review_res.get('status')}(自動採用しない)")
        input_sha = _sha(f"{text}|{kr['signature']}")

        def runner(lv=lv, review_res=review_res):
            canon = (review_res.get("canonicalization") or {}).get("status")
            if review_res.get("status") in ("NG_REVIEW_REQUIRED", "OUTER_RETRY_EXHAUSTED") or canon != "CANONICALIZATION_PASS":
                raise YE2EStop(f"FAMILY_Y_KP_NOT_PASSED({lv}): status={review_res.get('status')} canonicalization={canon}(自動採用しない)")
            if review_res.get("gloss_alignment_human_review_events"):
                raise YE2EStop(f"FAMILY_Y_KP_GLOSS_HR_EVENTS({lv}): gloss整合のHuman Review事象があります。Yには解消経路が未接続のためSTOP(自動で通さない)")
            return st.dumps(review_res), {"kp_review_status": (review_res.get("kp_review") or {}).get("status"),
                                          "kp_selection_signature": (review_res.get("kp_review") or {}).get("signature")}

        r = _ensure(ctx, prov, f"kp_{lv}", input_sha, f"{ctx.out_dir}/key_phrases/{lv}_result.json", runner)
        install_kp_assets(ctx, lv)
        summary[lv] = {"status": r["status"]}
    if pending:
        os.makedirs(ctx.out_dir, exist_ok=True)
        _wj(f"{ctx.out_dir}/kp_review_pending.json", {"pending": pending, "summary": summary})
        raise YKpReviewPending(f"{_khr().PENDING_MARKER} Human Review待ち: " + ", ".join((p.get("level") or p.get("kind", "?")) for p in pending), pending)
    # Adv KP英語解説(X B1と同一構成)。TTS段で解説LLMを呼び直さないよう、ここで来歴管理する。
    import er019_family_x_kp_explanation_01 as kexp
    items = sorted(_rj(f"{_kp_assets_dir(ctx, 'b1b')}/keywords_canonicalized.json")["items"], key=lambda x: x["rank"])
    sig = _sha(json.dumps({"display": [kexp.explanation_phrase(it) for it in items], "gloss": [it.get("japanese_gloss", "") for it in items]}, ensure_ascii=False))

    def runner_ex():
        _guard(ctx, "kp_expl_b1b", 2.0)
        inp = [{"rank": it["rank"], "display_phrase": kexp.explanation_phrase(it), "source_sentence": it.get("source_sentence", ""),
                "japanese_gloss": it.get("japanese_gloss", "")} for it in items]
        res = kexp.generate_kp_explanations(inp, call_fn=ctx.hooks.get("expl_call_fn"), client=ctx.llm_client)
        bad = {r_: v.get("status") for r_, v in res["items"].items() if v.get("status") != "OK"}
        if bad:
            raise YE2EStop(f"FAMILY_Y_KP_EXPLANATION_NOT_OK: {bad}(TTSへ渡さずSTOP)")
        return st.dumps(res), {}

    try:
        r = _ensure(ctx, prov, "kp_expl_b1b", sig, f"{ctx.out_dir}/key_phrases/b1b/kp_explanations.json", runner_ex)
    except _m().w62.FamilyZProvenanceMismatchStop as e:
        raise type(e)(f"{e} 次の一手: `--regenerate-stage kp_expl_b1b` を1回だけ明示して再実行(KP表現が変わった場合)") from e
    summary["kp_explanations_b1b"] = r["status"]
    _wj(f"{ctx.out_dir}/study_text_slots.json", STUDY_TEXT_SLOTS)
    return summary


# ------------------------------------------------------------
# stage: tts_b1b / tts_a2
# ------------------------------------------------------------
@contextlib.contextmanager
def _mock_isolation(ctx):
    """real以外は偽TTS(hooks.tts_patch)の中でだけTTSを走らせる。無ければTTS stageはSTOP(実APIへ出さない)。"""
    if ctx.mode == "real":
        yield
        return
    patch = ctx.hooks.get("tts_patch")
    if patch is None:
        raise YE2EStop("FAMILY_Y_NO_MOCK_TTS: mock/dry-runでは偽TTS(hooks.tts_patch)が必要(実TTS APIへは出さない)")
    with patch():
        yield


def _tts_input_sha(ctx, lv) -> str:
    ya = _ya()
    kp = f"{_kp_assets_dir(ctx, lv)}/keywords_canonicalized.json"
    ex = f"{ctx.out_dir}/key_phrases/b1b/kp_explanations.json"
    parts = [_sha(_rd(_level_text_path(ctx, lv))), _sha(_rd(f"{ctx.out_dir}/support/{lv}_support.json")), _m().w62.file_sha(kp),
             _m().w62.file_sha(ex) if lv == "b1b" else "", json.dumps(ya.segment_voice_map(), sort_keys=True), _sha(_rd(_ja_path(ctx))) if lv == "a2" else "",
             ya.TTS_BACKEND, STYLE_PROFILE]
    return _sha("|".join(parts))


def stage_tts(ctx, lv: str) -> dict:
    ya = _ya()
    w62 = _m().w62
    prov = _prov(ctx)
    _assert_kp_review_consistent(ctx, lv, f"tts_{lv}")
    text = _rd(_level_text_path(ctx, lv))
    parsed = ys.split_y_article(text)
    support = _rj(f"{ctx.out_dir}/support/{lv}_support.json")
    ja_title = ys.split_y_article(_rd(_ja_path(ctx)))["title"]
    unit = f"tts_{lv}"

    def runner():
        ya.write_level_inputs(ctx.out_dir, lv, parsed, support)
        guard = lambda label: _guard(ctx, f"tts_{lv}_{label}", TTS_CLIP_EST_JPY)     # noqa: E731  各clipの新規API呼出の前
        with _mock_isolation(ctx), ya.only_segments_scope(ctx.only_segments):
            if lv == "b1b":
                s = ya.generate_y_b1_segments(ctx.out_dir, style_profile=STYLE_PROFILE, guard=guard)
            else:
                s = ya.generate_y_a2_segments(ctx.out_dir, ja_title, style_profile=STYLE_PROFILE, guard=guard)
        res_path = f"{ctx.out_dir}/{lv}/audit/tts_generation_results.json"
        return json.dumps({"summary": s, "results_sha256": w62.file_sha(res_path)}, ensure_ascii=False, indent=2), \
            {"tts_backend": ya.TTS_BACKEND, "narrator_voice": ya.narrator_voice(), "voices": ya.segment_voice_map(), "chunk_tts": "not_applicable_Y"}

    r = _ensure(ctx, prov, unit, _tts_input_sha(ctx, lv), f"{ctx.out_dir}/tts_{lv}_stage.json", runner)
    return {"status": r["status"], "unit": unit}


# ------------------------------------------------------------
# stage: gate / assemble / pages / page_verify(API 0)
# ------------------------------------------------------------
def _require_fresh(prov, name):
    if name in prov.data["downstream_stale"] or prov.stage_entry(name) is None:
        raise YE2EStop(f"FAMILY_Y_STAGE_NOT_FRESH: {name}(未実行またはstale。明示 --regenerate-stage {name} または該当stageの実行が必要)")


def stage_gate(ctx) -> dict:
    ya = _ya()
    prov = _prov(ctx)
    out = {}
    for lv in LEVELS:
        _require_fresh(prov, f"tts_{lv}")
        g = ya.y_style_gate(ctx.out_dir, lv, STYLE_PROFILE)
        out[lv] = {"status": g["status"], "y_body_blocked": g["y_body_blocked"], "x_gate_blocked_after_filter": g["x_gate_blocked_after_filter"]}
    _wj(f"{ctx.out_dir}/gate_summary.json", out)
    bad = {lv: v for lv, v in out.items() if v["status"] != "PASS"}
    if bad:
        raise YE2EStop(f"FAMILY_Y_GATE_BLOCK: {json.dumps(bad, ensure_ascii=False)[:600]}(Gateを回避しない。該当segmentの再生成/Human確認が必要)")
    return out


def stage_assemble(ctx) -> dict:
    ya = _ya()
    prov = _prov(ctx)
    out = {}
    for lv in LEVELS:
        _require_fresh(prov, f"tts_{lv}")
        s = ya.assemble_level(ctx.out_dir, lv, style_profile=STYLE_PROFILE, slug=ctx.slug, article_text=ys.canonical_body(_rd(_level_text_path(ctx, lv))))
        out[lv] = {k: s.get(k) for k in ("status", "out_path", "duration_seconds", "clipping_detected")}
        if s.get("status") != "OK":
            _wj(f"{ctx.out_dir}/assemble_summary.json", out)
            raise YE2EStop(f"FAMILY_Y_ASSEMBLE_BLOCKED({lv}): status={s.get('status')}(Gateを回避して通し音声を作らない)")
    _wj(f"{ctx.out_dir}/assemble_summary.json", out)
    return out


def stage_pages(ctx) -> dict:
    ya = _ya()
    ja_segs = ys.split_y_article(_rd(_ja_path(ctx)))["segments"]
    title = ys.split_y_article(_rd(_ja_path(ctx)))["title"]
    audio_dir = f"{ctx.pages_dir}/audio"
    os.makedirs(audio_dir, exist_ok=True)
    levels = [ya.build_page_rows(ctx.out_dir, lv, audio_dir, "audio", ja_paragraphs=ja_segs) for lv in ("a2", "b1b")]     # Standard, Advanced の順
    html_text = ya.render_y_page(title, levels)
    page = f"{ctx.pages_dir}/index.html"
    with open(page, "w", encoding="utf-8") as f:
        f.write(html_text)
    return {"page": page, "levels": [lv["id"] for lv in levels]}


def evaluate_page_verify(html_text: str, base_dir: str) -> list:
    import er_user_listening_page_common_01 as cp
    v = []
    chk = cp.check_page(html_text, base_dir=base_dir)
    if chk.get("overall") != "PASS":
        v.append(f"STANDARD_PAGE_CHECK_NOT_PASS: {[n for n, x in (chk.get('checks') or {}).items() if not x.get('ok')]}")
    n = ys.check_y_page_notice(html_text)
    v.extend(n["violations"])
    return v


def stage_page_verify(ctx) -> dict:
    page = f"{ctx.pages_dir}/index.html"
    if not os.path.exists(page):
        raise YE2EStop(f"FAMILY_Y_PAGE_MISSING: {page}(pages stageを先に実行)")
    with open(page, encoding="utf-8") as f:
        html_text = f.read()
    viol = evaluate_page_verify(html_text, ctx.pages_dir)
    rec = {"page": page, "violations": viol, "ok": not viol}
    _wj(f"{ctx.out_dir}/page_verify_local.json", rec)
    if viol:
        raise YE2EStop(f"FAMILY_Y_PAGE_VERIFY_FAILED: {viol}")
    write_final_manifest(ctx)
    return rec


def write_final_manifest(ctx) -> str:
    """成功終了時の最終成果物の一覧(path・実model・routing・prompt sha)。公開(docs/へのコピー)は含まない=別手順。"""
    prov = _prov(ctx)
    tr = {}
    p = f"{ctx.out_dir}/text/text_records.json"
    if os.path.exists(p):
        tr = _rj(p)
    man = {"management_id": MANAGEMENT_ID, "slug": ctx.slug, "run": ctx.run, "mode": ctx.mode, "entry_status": ys.ENTRY_STATUS,
           "page": f"{ctx.pages_dir}/index.html",
           "assembled": {lv: _glob_one(f"{ctx.out_dir}/{lv}/assembled/*.wav") for lv in LEVELS},
           "ja_article": _ja_path(ctx), "closing_record": tr.get("closing_record"),
           "stage_entries": {n: {k: e.get(k) for k in ("routing_key", "requested_model", "actual_model_id", "response_id", "prompt_sha256", "cost_jpy", "input_sha256", "output_sha256")}
                             for n in UNIT_NAMES if (e := prov.stage_entry(n)) is not None},
           "study_text_slots": STUDY_TEXT_SLOTS, "chunk_tts": "not_applicable_Y", "core_numeric_v4_j2": "not_applicable_Y",
           "spent_jpy": round(ctx.budget.spent(), 4) if ctx.budget is not None else None}
    path = f"{ctx.out_dir}/final_manifest.json"
    _wj(path, man)
    return path


def _glob_one(pattern):
    import glob
    g = sorted(glob.glob(pattern))
    return g[0] if g else None


# ------------------------------------------------------------
# stage実行
# ------------------------------------------------------------
def run_stage(ctx, name: str) -> dict:
    fns = {"seed_check": stage_seed_check, "text": stage_text, "translate": stage_translate, "support": stage_support, "kp": stage_kp,
           "gate": stage_gate, "assemble": stage_assemble, "pages": stage_pages, "page_verify": stage_page_verify}
    with ctx.stage_context(name):
        if name in ("tts_b1b", "tts_a2"):
            return stage_tts(ctx, name.split("_", 1)[1])
        return fns[name](ctx)


def _log_stage(ctx, name, result, t0):
    rec = {"stage": name, "mode": ctx.mode, "elapsed_sec": round(time.time() - t0, 1),
           "spent_jpy_cumulative": round(ctx.budget.spent(), 4) if ctx.budget is not None else None,
           "result_keys": sorted(result) if isinstance(result, dict) else None}
    os.makedirs(ctx.out_dir, exist_ok=True)
    with open(f"{ctx.out_dir}/e2e_stage_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def run_stages(ctx, stages) -> dict:
    results = {}
    for name in stages:
        t0 = time.time()
        if ctx.mode != "dry-run":
            _m().st.set_stop_run_dir(ctx.out_dir)
            _stop_sentinel(ctx, f"stage:{name}")
        print(f"[Y-E2E] stage={name} mode={ctx.mode} ...", flush=True)
        results[name] = run_stage(ctx, name)
        _log_stage(ctx, name, results[name], t0)
    return results


STAGE_PLAN_INFO = {
    "seed_check": "読み取りのみ(routing登録・Voice割当・Theme Package・text core接続)",
    "text": "text core(Voice/Lead/紹介/Closing+Leakage Gate。routing FAMILY_Y_*)→ text/article_ja.md, text/text_records.json(closing_record)",
    "translate": "Advanced忠実英訳 → Standard(X承認済み関数。FAMILY_Y_TRANSLATE_ADV/STD)→ translate/{b1b,a2}.md",
    "support": "Preview/Comment 1〜3(Comment 4・In One Lineなし)→ support/{b1b,a2}_support.json",
    "kp": "KP Human Review(rc=4待機)→ KP確定 → Adv英語解説 → key_phrases/",
    "tts_b1b": "Y body 8seg + shared narration + KP(TTS flash-lite+ASR。Chunk/中核数値はY非適用)",
    "tts_a2": "同(Standard。6%減速)",
    "gate": "API 0(Y style gate + Std減速確認)", "assemble": "API 0(Audio Validation Gate→gain→timeline→headroom→wav)",
    "pages": "API 0(試聴ページ。注意書き=本文外・noindex。出力先は<run>/pages、公開は別手順)", "page_verify": "API 0(標準check+注意書きcheck→final_manifest.json)",
}


def describe_plan(ctx, stages=STAGES) -> dict:
    return {"management_id": MANAGEMENT_ID, "mode": "dry-run", "slug": ctx.slug, "run": ctx.run, "out_dir": ctx.out_dir, "side_effects": 0, "api_calls": 0,
            "stages": [{"stage": s, "plan": STAGE_PLAN_INFO[s], "est_jpy": STAGE_EST_JPY.get(s)} for s in stages],
            "units": list(UNIT_NAMES), "dependents": DEPENDENTS, "study_text_slots": STUDY_TEXT_SLOTS}


# ------------------------------------------------------------
# 起動guard(RESTART_STORM + RUN_LOCK。mock/real共通)
# ------------------------------------------------------------
_RUN_LOCK_DIR = None


def _launch_guard(out_dir: str) -> None:
    global _RUN_LOCK_DIR
    st = _m().st
    st.record_launch_and_check_storm(out_dir, sys.argv)
    st.acquire_run_lock(out_dir, sys.argv)
    _RUN_LOCK_DIR = out_dir


def _release_launch_lock() -> None:
    global _RUN_LOCK_DIR
    if _RUN_LOCK_DIR:
        _m().st.release_run_lock(_RUN_LOCK_DIR)
        _RUN_LOCK_DIR = None


def build_real_context(args) -> YContext:
    ctx = YContext(slug=args.slug, run=args.run, mode="real", theme_package_path=args.theme_package)
    cost_log = f"{ctx.out_dir}/cost_log.jsonl"
    ctx.budget = E2EBudget(args.approved_budget_jpy, args.warn_threshold_jpy, spent_fn=make_real_spent_fn(cost_log), ack_warn=args.ack_warn_threshold)
    st = _m().st
    st.check_stop_sentinel("client:build_real_context", ctx.out_dir)       # client生成前のSTOP確認
    _launch_guard(ctx.out_dir)                                             # client生成前に RESTART_STORM / RUN_LOCK
    from dotenv import load_dotenv
    load_dotenv()
    if args.tts_execution_mode:
        os.environ["TTS_EXECUTION_MODE"] = args.tts_execution_mode
    os.makedirs(ctx.out_dir, exist_ok=True)
    import er005_cost_logger as cl
    cl.install(cost_log)
    st.install_api_stop_guard()                                            # SDK入口でSTOP確認(共有moduleのretry/fallback内部も含む)
    import er003_v1_en_direct_vfl_01_generate as vfl01
    ctx.llm_client = vfl01.get_client()
    return ctx


def build_mock_context(run_root: str, run: str = "run_mock", slug: str = "y_article", theme_package_path: str = None, hooks: dict = None,
                       pages_dir: str = None) -> YContext:
    import er121_family_y_mock_01 as mk
    ctx = YContext(slug=slug, run=run, mode="mock", run_root=run_root, pages_dir=pages_dir, theme_package_path=theme_package_path)
    api = mk.MockApi(ctx.out_dir)
    ctx.mock_api = api
    ctx.llm_client = mk.MockClient(api)
    ctx.hooks = mk.default_hooks(api)
    ctx.hooks.update(hooks or {})
    ctx.budget = E2EBudget(APPROVED_BUDGET_MAX_JPY, WARN_THRESHOLD_JPY, spent_fn=lambda: 0.0)
    return ctx


def build_parser():
    p = argparse.ArgumentParser(description="Family Y Production runner(FAMILY-Y-PRODUCTION-LAUNCH-01 委任_02B)")
    p.add_argument("--slug", default="y_article")
    p.add_argument("--run", default=DEFAULT_RUN)
    p.add_argument("--theme-package", default=None, help="Theme Package(json)。text stageの入力。seed shaとして来歴に記録")
    p.add_argument("--stage", default="all", choices=list(STAGES) + ["all"])
    p.add_argument("--stages", default=None, help="カンマ区切りのstage名を1回の起動でSTAGES順に実行(例 tts_b1b,tts_a2,gate,assemble,pages,page_verify)。--stageと併用不可")
    p.add_argument("--stop-after", default=None, choices=list(STAGES))
    p.add_argument("--mode", default="dry-run", choices=("dry-run", "mock", "real"))
    p.add_argument("--only-segments", default=None, help="カンマ区切りsegment id(TTS stageの当該segmentのみ。X共通のonly-segments機構)")
    p.add_argument("--regenerate-stage", default=None, choices=list(UNIT_NAMES), help="明示指定したunitだけ再生成(自動再生成は行わない)")
    p.add_argument("--kp-review", default=None, choices=("wait", "auto"))
    p.add_argument("--kp-review-by", default=None)
    p.add_argument("--kp-review-reason", default=None)
    p.add_argument("--kp-review-user-ref", default="")
    p.add_argument("--approved-budget-jpy", type=float, default=0.0, help=f"real必須(上限{APPROVED_BUDGET_MAX_JPY}=案件個別Cap)")
    p.add_argument("--warn-threshold-jpy", type=float, default=WARN_THRESHOLD_JPY)
    p.add_argument("--ack-warn-threshold", action="store_true")
    p.add_argument("--tts-execution-mode", default="STANDARD", choices=("STANDARD", "BATCH"))
    p.add_argument("--clear-stop", action="store_true")
    p.add_argument("--reason", default=None)
    return p


def _select_stages(args):
    if args.stages:
        if args.stage != "all":
            raise YE2EStop("--stages と --stage は併用できません")
        want = [x.strip() for x in args.stages.split(",") if x.strip()]
        bad = [x for x in want if x not in STAGES]
        if bad or not want:
            raise YE2EStop(f"--stages に不正なstage名: {bad}(許可={list(STAGES)})")
        stages = [x for x in STAGES if x in want]
    else:
        stages = list(STAGES) if args.stage == "all" else [args.stage]
    if args.stop_after:
        stages = stages[: stages.index(args.stop_after) + 1] if args.stop_after in stages else stages
    return stages


def main(argv=None):
    import er_secret_mask_01 as _sm
    _sm.install_stream_masking()
    args = build_parser().parse_args(argv)
    st = _m().st
    if args.clear_stop:
        return _clear_stop_main(args)
    try:
        stages = _select_stages(args)
    except YE2EStop as e:
        print(f"[STOP] {e}", file=sys.stderr)
        return 2
    ya_only = None
    if args.only_segments:
        ya_only = {x.strip() for x in args.only_segments.split(",") if x.strip()}
    ctx = None
    try:
        if args.mode == "dry-run":
            ctx = YContext(slug=args.slug, run=args.run, mode="dry-run", theme_package_path=args.theme_package)
            plan = describe_plan(ctx, stages)
            try:
                plan["preflight"] = stage_seed_check(ctx)
            except Exception as e:  # noqa: BLE001
                plan["preflight"] = {"error": f"{e.__class__.__name__}: {e}"}
            print(json.dumps(plan, ensure_ascii=False, indent=1, default=str))
            return 0
        startup_dir = f"{RUN_ROOT}/{args.slug}/{args.run}" + ("_mock" if args.mode == "mock" else "")
        st.check_stop_sentinel("startup", startup_dir)
        if args.mode == "mock":
            ctx = build_mock_context(RUN_ROOT, run=f"{args.run}_mock", slug=args.slug, theme_package_path=args.theme_package)
            _launch_guard(ctx.out_dir)
        else:
            ctx = build_real_context(args)
        ctx.only_segments, ctx.regenerate_stage = ya_only, args.regenerate_stage
        os.makedirs(ctx.out_dir, exist_ok=True)
        _wj(f"{ctx.out_dir}/voice_assignment.json", ys.verify_voice_assignment())
        if args.kp_review == "auto":
            import er119_kp_wiring_01 as kw
            if not (args.kp_review_by and args.kp_review_reason):
                print("[STOP] --kp-review auto には --kp-review-by と --kp-review-reason が必要です", file=sys.stderr)
                return 2
            try:
                kw.declare_from_runner_args(ctx.out_dir, by=args.kp_review_by, reason=args.kp_review_reason, user_ref=args.kp_review_user_ref)
            except _khr().KpReviewError as e:
                print(f"[STOP] {e}", file=sys.stderr)
                return 2
        results = run_stages(ctx, stages)
        print(json.dumps({"management_id": MANAGEMENT_ID, "mode": ctx.mode, "stages": list(results),
                          "spent_jpy": round(ctx.budget.spent(), 4) if ctx.budget is not None else None}, ensure_ascii=False))
        return 0
    except YKpReviewPending as e:
        import er119_kp_wiring_01 as kw
        print(kw.pending_banner(e.pending, restart_command="py " + " ".join(sys.argv), run_dir=ctx.out_dir))
        return _khr().EXIT_CODE_PENDING
    except (st.FamilyZStopSentinel, st.FamilyZStopSentinelAbort) as e:
        print(f"[STOP_SENTINEL] {e}", file=sys.stderr)
        return st.STOP_EXIT_CODE
    except st.FamilyZRunLockHeld as e:
        print(f"[RUN_LOCK] {e}", file=sys.stderr)
        return st.LOCK_EXIT_CODE
    except Exception as e:  # noqa: BLE001  (STOP: 自動retry/再生成/迂回はしない)
        print(f"[STOP] {e.__class__.__name__}: {e}", file=sys.stderr)
        return 2
    finally:
        _release_launch_lock()


def _clear_stop_main(args) -> int:
    st = _m().st
    if not (args.reason or "").strip():
        print("[CLEAR_STOP] --reason が必須", file=sys.stderr)
        return 2
    out = {}
    try:
        for d in (f"{RUN_ROOT}/{args.slug}/{args.run}", f"{RUN_ROOT}/{args.slug}/{args.run}_mock"):
            if os.path.isdir(d):
                out[d] = st.clear_stop(d, args.reason)
    except st.FamilyZStop as e:
        print(f"[CLEAR_STOP_REFUSED] {e}", file=sys.stderr)
        return st.CLEAR_REFUSED_EXIT_CODE
    print(json.dumps({"clear_stop": out, "stop_all_path": st.STOP_ALL_PATH, "stop_all_present": os.path.exists(st.STOP_ALL_PATH)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
