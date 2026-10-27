# -*- coding: utf-8 -*-
"""Family Y Production runner(FAMILY-Y-PRODUCTION-LAUNCH-01 委任_02B)。

Zのstage framework(er026_family_z_fiction_production_runner_01)と同型の骨格を、Yの契約(5パート・Voice3人・Comment 1〜3・IOLなし)で実装する。
- stage単位: ensure_stage(来歴 provenance + 入力sha + 出力sha)、DEPENDENTS(親を再生成すると子孫がstale)、--regenerate-stage、resume(再利用はAPI 0)。
- 安全装置: STOP/STOP_ALLセンチネル、RUN_LOCK(二重起動拒否)、RESTART_STORM(短時間の再起動連発の遮断)はer062の関数をそのまま使う(再実装しない)。
  exit code: STOP=3、RUN_LOCK/KP_REVIEW_PENDING=4(stdoutの `[KP_REVIEW_PENDING]` で区別)、その他の停止=2。
- KP Human Review: 最初から er119_kp_wiring_01.run_kp_with_review 経由(Human確認 or 明示の不在宣言まで rc=4 で待機。有料の後続工程へ進まない)。
- 実modelの記録: 各stageの来歴entryに routing_key / requested_model / actual_model_id / response_id / prompt_sha256 / cost を残す(closing_recordはtext stage)。
- mode: dry-run(副作用0・API 0)/ mock(偽client・偽TTS。実APIへ出ない)/ real(承認予算内のみ。本委任では起動しない)。
- Part 1(Vocabulary & Expressions)・Part 2(Grammar & Sentence Structure)は委任_06でX/Zと同形に接続済み(Part 1はAdvancedは常に・Standardはdisplay_spec付き[SLOT-23 委任_04D]のときだけ、Part 2は両level[Std/Adv]。kp stage内でKP/文法のHR待機点を共有し、
  使う側[tts_b1b/gate/assemble=Advancedの文法、pages/page_verify=両levelの文法]の入口でfail-closed確認。共通核はer119/er120/er003_kp_*を呼ぶだけで再実装しない)。接続状態は study_text_slots.json に記録する。
- 隔離: 本ファイルはYの新入口。X/Zのruntime・既存Prompt・閾値・辞書は無変更。中核数値v4/J2はY非適用。Chunk TTSはX方式を正式採用(委任_04、USER_02 ①。分割判定はaudio層の audit/chunk_tts_decision.json)。
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
APPROVED_BUDGET_MAX_JPY = 170.0          # 案件個別Cap(Fable判断 委任_02C: 150→170円。BUDGET_PLAN_03 §1)。これを超える承認は受け付けない
WARN_THRESHOLD_JPY = 100.0
STAGES = ("seed_check", "text", "translate", "support", "kp", "tts_b1b", "tts_a2", "gate", "assemble", "pages", "page_verify")
STAGE_EST_JPY = {"text": 45.0, "translate": 12.0, "support": 6.0, "kp": 10.0, "tts_b1b": 30.0, "tts_a2": 30.0}
TTS_CLIP_EST_JPY = 2.0     # clip単位guard見積り。TTS統一委任_02(Opus R-6): 最悪clip=6TTS+ASR+LR LLM≒2円へ更新(旧1.0)
# OPEN-537是正(FAMILY-Y-STYLE-PROFILE-FIX-01 委任_02): 旧 `STYLE_PROFILE = "default"` を撤去。Yのprofileは承認profile(_ya().Y_APPROVED_STYLE_PROFILE=fx_20261017)を
# resolve_style_profile()で課金前に解決・固定記録(audit/style_profile.json)し、ctx.style_profileとして生成/Gate/組立へ透過する。
LEVELS = ("b1b", "a2")
ADV_LEVEL, STD_LEVEL = LEVELS     # SLOT-23 委任_04D: Part 1(Vocabulary & Expressions)系の関数は level 引数(既定=Advanced)で動く。levelのリテラル直書きをしない

# 来歴(provenance)の単位。CLIのstageより細かい。--regenerate-stage の許可値でもある。
UNIT_NAMES = ("text", "translate_b1b", "translate_a2", "support_b1b", "support_a2", "kp_b1b", "kp_a2", "kp_expl_b1b", "tts_b1b", "tts_a2",
              "kp_part1_b1b", "kp_part1_ja_b1b", "kp_part1_a2", "kp_part1_ja_a2", "part2_cand_b1b", "part2_b1b", "part2_cand_a2", "part2_a2")
# 親→子。親を明示再生成すると、推移的な子孫がstaleになり、明示 --regenerate-stage が無い限りSTOP(自動再生成しない)。
DEPENDENTS = {
    "text": ["translate_b1b"],
    "translate_b1b": ["translate_a2", "support_b1b", "kp_b1b", "tts_b1b", "part2_cand_b1b"],     # Part 2(文法)の候補は英訳Advancedの本文に依存(X/Zと同じ)
    "part2_cand_b1b": ["part2_b1b"],
    "translate_a2": ["support_a2", "kp_a2", "tts_a2", "part2_cand_a2"],     # Standardの文法候補は英訳Standardの本文に依存。葉(TTS等への依存辺を張らない=文法はページ専用)
    "part2_cand_a2": ["part2_a2"],
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
    reuse_manifest_path: str = None          # 再利用manifest(E-1: 既存R0のVoice/Lead/紹介をbyte一致検証して採用)。None=全て新規生成
    budget: object = None
    llm_client: object = None
    hooks: dict = dataclasses.field(default_factory=dict)
    only_segments: object = None
    regenerate_stage: object = None
    mock_api: object = None
    style_profile: str = None                   # resolve_style_profile()が設定(課金前)。None=未解決=stageはSTOP(fail-closed)
    style_profile_source: str = None
    page_audience: str = "public"               # pages stageの表示対象。"public"(既定)=Chunk境界マーカーなし / "dev"=開発用ページ(index_dev.html)のみ⏸を表示(CLI --page-audience で明示指定。委任_08)

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
            "FAMILY_Y_LEAD_GENERATE", "FAMILY_Y_PERSONA_INTRO", "FAMILY_Y_TRANSLATE_ADV", "FAMILY_Y_TRANSLATE_STD",
            "FAMILY_Y_VOICE_PROVENANCE_MAP", "FAMILY_Y_VOICE_STRUCTURE_TAG", "STUDY_TEXT_GRAMMAR_EXTRACT", "STUDY_TEXT_GRAMMAR_EXPLAIN")
    res["routing"] = {k: routing.PROCESS_MODEL_MAP.get(k) for k in keys}
    missing = [k for k, v in res["routing"].items() if not v]
    if missing:
        raise YE2EStop(f"FAMILY_Y_ROUTING_KEY_UNREGISTERED: {missing}(er006へ登録されていません。fail-closed)")
    res["chunk_tts"] = ys.chunk_decision_record("b1b")
    res["core_numeric_applicable"] = ys.CORE_NUMERIC_APPLICABLE
    tp = ctx.theme_package_path
    res["theme_package"] = {"path": tp, "exists": bool(tp and os.path.exists(tp))}
    tc = ctx.hooks.get("text_core")
    if tc is None and ctx.mode in ("real", "dry-run"):          # import自体はI/Oなし(isolation testで固定)。dry-runでも接続状態を正しく表示する
        import er121_family_y_text_core_01 as tc
    res["text_core_connected"] = bool(tc is not None and hasattr(tc, "produce_article"))
    res["study_text_slots"] = STUDY_TEXT_SLOTS
    return res


STUDY_TEXT_SLOTS = {"part1_vocabulary_expressions": "接続済み(委任_06。5件[vocab_confirmed.json]・kp stage内で生成・使う側入口でfail-closed。Advancedは常に、Standardはdisplay_spec付き[SLOT-23 委任_04D・遡及なし]のときだけ=level別stage kp_part1_<level>)",
                    "part2_grammar": "接続済み(委任_06→GRAMMAR-PREGEN-ALL-LEVELS-01 委任_03で両level化。Advanced+Standard・KP候補生成と同じ待機点の前に候補抽出+全候補の解説の事前生成・KPと1つのreview_request.md/rc=4・確定後はfinalize[LLM 0]・Standardはページ専用)"}
CHUNK_TTS_MANIFEST = "applied_X_method"      # 委任_04/OT-44(b): X方式Chunk TTSをYへ正式採用(分割の有無は各levelの audit/chunk_tts_decision.json。1段落segmentは分割0)
PART1_STAGES = {lv: {"gen": f"kp_part1_{lv}", "ja": f"kp_part1_ja_{lv}"} for lv in LEVELS}     # Part 1の来歴stage名(level別。旧 PART1_STAGE/PART1_JA_STAGE[Advancedのみ]は撤去)
# Part 2(文法)の来歴stage名(level別。er120_part2_wiring_01.stage_namesと同一。cand=候補抽出+解説の事前生成 / final=finalize[LLM 0])
PART2_STAGES = {lv: {"cand": f"part2_cand_{lv}", "expl": f"part2_expl_{lv}", "final": f"part2_{lv}"} for lv in LEVELS}
PART2_CAND_STAGE, PART2_FINAL_STAGE = PART2_STAGES["b1b"]["cand"], PART2_STAGES["b1b"]["final"]   # Advancedの名前(既存の参照用。Standardは PART2_STAGES["a2"])


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
        res = fn(ctx.llm_client, slug=ctx.slug, theme_package=tp, out_dir=out, guard=lambda label: _guard(ctx, label, 1.0),
                 theme_package_path=ctx.theme_package_path, reuse=ctx.reuse_manifest_path)
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

    r = _ensure(ctx, prov, "text", _sha(f"text|{w62.file_sha(ctx.theme_package_path)}|reuse={w62.file_sha(ctx.reuse_manifest_path) if ctx.reuse_manifest_path else 'none'}"), _ja_path(ctx), runner)
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
# stage: support(Preview / Comment 1〜3。Comment 4・In One Lineは無い。Advanced(b1b)はComment 2なし=Preview/Comment 1/Comment 3のみ)
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
            if "comment_2" in ys.support_names(lv):        # Standardのみ(日本語側は現状維持)。AdvancedはComment 2を生成しない(2026-10-26ユーザー承認)
                c2 = call(ys.Y_COMMENT_2_ROLE[lv], ctxs["comment_2"], "comment_2")
            else:
                c2 = None
            c3 = call(ys.Y_COMMENT_3_ROLE[lv], ctxs["comment_3"], "comment_3")
            if c2 is not None:
                prev_role = gen.PREVIEW_ROLE.format(comment_1=c1["text"], comment_2=c2["text"])
            else:
                prev_role = ys.advanced_preview_role(gen.PREVIEW_ROLE).format(comment_1=c1["text"])
            prev = call(prev_role, ctxs["preview"], "preview")
            res = {"preview": prev, "comment_1": c1, **({"comment_2": c2} if c2 is not None else {}), "comment_3": c3}
            pat = ys.AI_ANNOUNCE_RE if lv == "a2" else ys.AI_ANNOUNCE_EN_RE
            hit = [k for k, v in res.items() if pat.search(v["text"])]
            if hit:
                raise YE2EStop(f"FAMILY_Y_AI_ANNOUNCE_IN_SUPPORT({lv}): {hit}(音声へAIアナウンスを入れない。再生成が必要)")
            doc = {k: v["text"] for k, v in res.items()}
            doc["_meta"] = {"model_requested": model, "comment_4_generated": False,
                            **({"removed_by_spec": {n: ys.COMMENT2_REMOVED_SPEC for n in ys.Y_REMOVED_SUPPORT_NAMES[lv]}} if ys.Y_REMOVED_SUPPORT_NAMES[lv] else {}),
                            "attempts": {k: v.get("attempts") for k, v in res.items()}}
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
        rev = khr.require_final_consistent(src, level=lv, require_src_contract=False, assets_json=f"{_kp_assets_dir(ctx, lv)}/keywords_canonicalized.json")
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


def _rebind_kp_on_confirmation(ctx, prov, lv: str, text: str, kr: dict, input_sha: str):
    """KCP3所見D1: 自動採用runへ後からユーザー確定(フォーム/HR)を入れて KP review署名が変わっても、`kp_<lv>` 来歴の親sha不一致STOPにしない(API 0で再バインド)。
    条件(すべて満たすときだけ): 明示 --regenerate-stage kp_<lv> ではない / 確定レコードがユーザー確定(live) / 旧署名で再計算した入力shaが記録済みentryと一致(=本文は不変) /
    現在のKP assetsが新しい確定と一致(内容が変わっていれば再バインドせず従来どおりSTOP・再生成)。付け替えは entry['rebinds'] に履歴。TTS等の子孫はstale化しない。"""
    name = f"kp_{lv}"
    if ctx.regenerate_stage == name:
        return None
    entry = prov.stage_entry(name)
    if entry is None or entry["input_sha256"] == input_sha or not entry.get("kp_selection_signature"):
        return None
    if _khr()._cc().live_user_record(_kp_src_dir(ctx, lv)) is None:
        return None
    try:
        _assert_kp_review_consistent(ctx, lv, "stage_kp_rebind_check")
    except (YE2EStop, YKpReviewPending):
        return None
    return _m().w62.rebind_confirmation_input(prov, name, expected_old_input_sha=_sha(f"{text}|{entry['kp_selection_signature']}"), new_input_sha=input_sha,
                                              new_signature=kr["signature"], new_status=kr.get("status"))


def stage_kp(ctx) -> dict:
    prov = _prov(ctx)
    st = _m().st
    summary, pending = {}, []
    # Part 2(文法): 両level(Advanced=b1b / Standard=a2)で 候補抽出(Step A'')→全候補の解説の事前生成 を、KP候補生成と同じ待機点の前に実行する
    # (未確定ならKPのpendingと1回にまとめて待機)。resumeはAPI 0(生成済みの解説は再利用、未生成分のみ生成)。
    for lv in ("b1b", "a2"):
        p2c = _part2_cand_step(ctx, prov, lv)
        summary[PART2_STAGES[lv]["cand"]] = {"state": p2c["state"], "status": p2c["review"]["status"], "generated": p2c["generated"],
                                              "pregen_generated": p2c["pregen"]["generated"], "pregen_reused": p2c["pregen"]["reused"]}
        if p2c["state"] == "PENDING":
            pending.append(p2c["pending"])
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
        _rebind_kp_on_confirmation(ctx, prov, lv, text, kr, input_sha)     # D1: 確定(ユーザー)による署名変化だけならAPI 0で来歴を付け替える

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
        _assert_kp_review_consistent(ctx, lv, "stage_kp_post_install")   # 確定内容保護 G1(M-1): 解説LLM/Part 1/Part 2の有料生成の前に確定レコードと照合
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
    # Part 1(Vocabulary & Expressions): 対象level(Advanced=常に / Standard=display_spec付きのときだけ。遡及なし)ごとに level 別 stage・別dirで生成。
    # Part 1の失敗はそのlevelのTTS前STOP(KP確定は保持)。Std/Advは別dir・別stageで相互独立。
    p1_by_level = {}
    for lv in LEVELS:
        if not _part1_level_enabled(ctx, lv):
            continue
        p1_by_level[lv] = _part1_items(ctx, lv)     # M-9: Part 1の入力=vocab_confirmed.json(最大5件、KP3件を含む)。KP(音声・Adv解説)は3件のまま
        summary[PART1_STAGES[lv]["gen"]] = _stage_kp_part1(ctx, prov, p1_by_level[lv], lv)
        summary[PART1_STAGES[lv]["ja"]] = _stage_kp_part1_ja(ctx, prov, p1_by_level[lv], lv)     # 解説とは独立の別stage・別call(引用英文のみ入力)
        _assemble_study_rows(ctx, p1_by_level[lv], lv)                                           # 組立検証(gloss HR/未評価・引用の逐語実在・訳の最新性)+study_text/保存
    for lv in LEVELS:
        summary[PART2_STAGES[lv]["final"]] = _part2_final_step(ctx, prov, lv, p1_by_level.get(lv))     # Part 2の確定(文法Human確認 or 明示宣言)からfinalize(LLM 0)。再抽出・Step Bなし
    _wj(f"{ctx.out_dir}/study_text_slots.json", {**STUDY_TEXT_SLOTS, "state": {**{PART1_STAGES[lv][k]: summary[PART1_STAGES[lv][k]] for lv in p1_by_level for k in ("gen", "ja")},
                                                                              **{PART2_STAGES[lv]["final"]: summary[PART2_STAGES[lv]["final"]] for lv in LEVELS}}})
    return summary


# ------------------------------------------------------------
# 学習テキスト Part 1「Vocabulary & Expressions」(Advanced=常に/Standard=display_spec付きのときだけ)/ Part 2「Grammar & Sentence Structure」(Std+Adv両level。X/Zと同形・共通核を呼ぶだけ)
# 共通核: er003_kp_general_explanation_01(Part 1解説)/er003_kp_source_sentence_ja_01(引用英文の訳)/er120_part2_wiring_01(Part 2)/er119(KP/文法HR)。
# 使う側(tts_b1b/gate/assemble/pages/page_verify)で存在・最新性・確定との一致をfail-closed確認する(_assert_study_ready)。
# ------------------------------------------------------------
def _p1():
    import er003_kp_general_explanation_01 as p1
    return p1


def _p1ja():
    import er003_kp_source_sentence_ja_01 as ja
    return ja


def _p2w():
    import er120_part2_wiring_01 as p2w
    return p2w


def _part1_level_enabled(ctx, level: str = ADV_LEVEL) -> bool:
    """Part 1の対象level(vocab可否の単一関数 er119.vocab_enabled): Advancedは常に、Standardは確定reviewがstd_part1マーク付き[=display_spec付き]のときだけ
    (SLOT-23 ユーザー正式決定2026-10-27・遡及なし: マーク無しの旧Std記事はPart 1なし=従来どおり)。"""
    khr = _khr()
    return khr.vocab_enabled(level, khr.load_review(_kp_src_dir(ctx, level)))


def _part1_items(ctx, level: str = ADV_LEVEL) -> list:
    """Part 1の入力の単一アクセサ(M-9)。reviewがあればvocab_confirmed.json(最大5件)が必須(fail-closed)。KP側rankで他ファイルと結合しない。"""
    khr = _khr()
    try:
        return khr.part1_items(_kp_src_dir(ctx, level))
    except khr.KpReviewError as e:
        raise YE2EStop(f"FAMILY_Y_KP_PART1_ITEMS_NOT_READY({level}): {e}") from e


def _part1_path(ctx, level: str = ADV_LEVEL) -> str:
    return f"{_kp_src_dir(ctx, level)}/{_p1().EXPLANATIONS_FILENAME}"


def _part1_ja_path(ctx, level: str = ADV_LEVEL) -> str:
    return f"{_kp_src_dir(ctx, level)}/{_p1ja().TRANSLATIONS_FILENAME}"


def _part1_cost_tag(level: str, base: str) -> str:
    """費用ログのstageタグ。Advancedは従来の `kp_part1`/`kp_part1_ja` のまま(過去runのタグと同一)、Standardは `<base>_<level>`。"""
    return base if level == ADV_LEVEL else f"{base}_{level}"


def _cli_hint(ctx, regen_name: str) -> str:
    tp = f" --theme-package {ctx.theme_package_path}" if ctx.theme_package_path else ""
    return f"`--mode real --slug {ctx.slug} --run {ctx.run}{tp} --stage kp --regenerate-stage {regen_name} --approved-budget-jpy <承認額>`"


def _require_part1_fresh(ctx, items: list, where: str, level: str = ADV_LEVEL) -> dict:
    p1 = _p1()
    path = _part1_path(ctx, level)
    doc = _rj(path) if os.path.exists(path) else None
    try:
        p1.require_fresh_general_explanations(items, doc, where=where, level=level,
                                              next_command=f"{_cli_hint(ctx, PART1_STAGES[level]['gen'])}(Part 1だけ再生成。KP選定・TTSはやり直さない。KP表現が変わっている場合は先に kp_expl_b1b)")
    except p1.KpGeneralExplanationStale as e:
        raise YE2EStop(f"FAMILY_Y_KP_PART1_NOT_READY: {e}") from e
    return doc


def _require_part1_ja_fresh(ctx, items: list, where: str, level: str = ADV_LEVEL) -> dict:
    ja = _p1ja()
    path = _part1_ja_path(ctx, level)
    doc = _rj(path) if os.path.exists(path) else None
    try:
        ja.require_fresh_translations(items, doc, where=where, next_command=f"{_cli_hint(ctx, PART1_STAGES[level]['ja'])}(訳だけ再生成。KP選定・TTS・解説はやり直さない)")
    except ja.KpSourceSentenceJaStale as e:
        raise YE2EStop(f"FAMILY_Y_KP_PART1_JA_NOT_READY: {e}") from e
    return doc


def _assemble_study_rows(ctx, items: list, level: str = ADV_LEVEL) -> list:
    p1 = _p1()
    doc = _require_part1_fresh(ctx, items, "assemble", level)
    ja_doc = _require_part1_ja_fresh(ctx, items, "assemble", level)
    text = ys.canonical_body(_rd(_level_text_path(ctx, level)))
    try:
        rows = p1.assemble_part1(items, doc, _p1ja().translations_by_rank(ja_doc), text, level=level)
    except p1.KpGeneralExplanationError as e:
        raise YE2EStop(f"FAMILY_Y_KP_PART1_ASSEMBLE_NOT_OK({level}): {e}") from e
    p1.write_study_text(_part2_dir(ctx, level), rows, level=level)     # Advanced=<out>/study_text(既存と同一)・Standard=<out>/a2/study_text
    return rows


def _stage_kp_part1(ctx, prov, items: list, level: str = ADV_LEVEL) -> str:
    st = _m().st
    p1 = _p1()
    stage = PART1_STAGES[level]["gen"]
    try:
        sig = p1.phrases_signature(items, level=level)
    except p1.KpGeneralExplanationInputError as e:
        raise YE2EStop(f"FAMILY_Y_KP_GENERAL_EXPLANATION_INPUT_INVALID: {e}(Part 1の入力は全文選定KP[fulltext_source_ref+used_form]のみ。TTSへ進まない)") from e

    def runner_p1():
        _guard(ctx, stage, 0.5)
        hook = ctx.hooks.get("part1_call_fn")
        if hook is None and ctx.mode != "real":
            raise YE2EStop("FAMILY_Y_KP_PART1_NO_HOOK: mock/dry-runではhooks.part1_call_fnが必要(実APIへは出さない)")
        try:
            with ctx.stage_context(_part1_cost_tag(level, "kp_part1")):
                res = p1.generate_for_kp_items(items, call_fn=hook, client=ctx.llm_client, level=level)
        except p1.KpGeneralExplanationError as e:
            raise YE2EStop(f"FAMILY_Y_KP_GENERAL_EXPLANATION_NOT_OK({level}): {e}(旧方式fallbackなし・空欄続行なし。TTSへ渡さずSTOP。次の一手: 原因確認後に{_cli_hint(ctx, stage)})") from e
        a = res["audit"]
        return st.dumps(res), {"model": a["model"], "prompt_sha256": a["prompt_sha256"], "total_cost_jpy": a["total_cost_jpy"],
                               "retried_for_parse": a["retried_for_parse"], "response_ids": a["response_ids"]}

    try:
        r = _ensure(ctx, prov, stage, sig, _part1_path(ctx, level), runner_p1)
    except _m().w62.FamilyZProvenanceMismatchStop as e:
        raise type(e)(f"{e} 次の一手: {_cli_hint(ctx, stage)}(KP表現・順序・Prompt・modelが変わった場合は明示再生成。自動再生成しない)") from e
    return r["status"]


def _stage_kp_part1_ja(ctx, prov, items: list, level: str = ADV_LEVEL) -> str:
    """引用英文のみを入力に日本語訳を1 callで生成(解説stageとは独立)。訳のPromptはlevel非依存(level別dirに保存するためlevel間の再利用は起きない)。"""
    st = _m().st
    ja = _p1ja()
    stage = PART1_STAGES[level]["ja"]
    try:
        sig = ja.translations_signature(items)
    except ja.KpSourceSentenceJaInputError as e:
        raise YE2EStop(f"FAMILY_Y_KP_PART1_JA_INPUT_INVALID: {e}(訳の入力は本文引用英文のみ。TTSへ進まない)") from e

    def runner_ja():
        _guard(ctx, stage, 0.3)
        hook = ctx.hooks.get("part1_ja_call_fn")
        if hook is None and ctx.mode != "real":
            raise YE2EStop("FAMILY_Y_KP_PART1_JA_NO_HOOK: mock/dry-runではhooks.part1_ja_call_fnが必要(実APIへは出さない)")
        text = ys.canonical_body(_rd(_level_text_path(ctx, level)))
        try:
            with ctx.stage_context(_part1_cost_tag(level, "kp_part1_ja")):
                res = ja.generate_for_kp_items(items, call_fn=hook, client=ctx.llm_client, article_text=text)
        except (ja.KpSourceSentenceJaError, ja.KpSourceSentenceJaInputError) as e:
            raise YE2EStop(f"FAMILY_Y_KP_PART1_JA_NOT_OK({level}): {e}(旧方式fallbackなし・空欄続行なし。TTSへ渡さずSTOP。次の一手: 原因確認後に{_cli_hint(ctx, stage)})") from e
        a = res["audit"]
        return st.dumps(res), {"model": a["model"], "prompt_sha256": a["prompt_sha256"], "total_cost_jpy": a["total_cost_jpy"],
                               "retried_for_parse": a["retried_for_parse"], "response_ids": a["response_ids"]}

    try:
        r = _ensure(ctx, prov, stage, sig, _part1_ja_path(ctx, level), runner_ja)
    except _m().w62.FamilyZProvenanceMismatchStop as e:
        raise type(e)(f"{e} 次の一手: {_cli_hint(ctx, stage)}(引用英文・Prompt・modelが変わった場合は明示再生成。自動再生成しない)") from e
    return r["status"]


# --- Part 2(文法) ---
def _part2_dir(ctx, level: str = "b1b") -> str:
    """level別のstudy dir(単一関数 er120_part2_wiring_01.study_dir_for)。Advanced=<out>/study_text(既存)・Standard=<out>/a2/study_text。"""
    return _p2w().study_dir_for("y", ctx.out_dir, level)


def _part2_inputs(ctx, level: str):
    """(段落list, label)。段落=ys.canonical_body(当該level)の空行区切り(KP/Part 1と同じ入力。Voiceの紹介行+本文は1段落に結合)、label=当該levelの英訳のタイトル行。"""
    text = _rd(_level_text_path(ctx, level))
    return ys.canonical_body(text).split("\n\n"), _p2w().label_for(text)


def _part2_next(ctx, level: str, regen: str = None) -> str:
    regen = regen or PART2_STAGES[level]["final"]
    return (f"{_cli_hint(ctx, regen)}(Part 2({level})だけ再finalize。本文・KP・TTSはやり直さない。再抽出はしない)。"
            f"未確定なら `py er119_kp_human_review_cli_01.py grammar-select --run {ctx.out_dir} --level {level} ...` で決めてから `--stage kp` を同じまま再実行")


def _part2_resume_next(ctx, level: str) -> str:
    """候補抽出/解説の事前生成の失敗時の次の一手: `--stage kp` を同じまま再実行(候補と生成済みの解説は再利用=未生成分だけ生成。再抽出・regenerateは案内しない)。"""
    return (f"`--stage kp` を同じまま再実行(Part 2({level})の候補と生成済みの解説は再利用し、未生成分だけを生成します。--regenerate-stage は使わない)")


def _stage_precheck(prov, name: str, input_sha: str, force: bool) -> None:
    """有料呼出の前に、ensure_stageと同じ来歴規則(stale/親sha不一致)で止める(確認前に抽出・解説を発注しない)。"""
    if force:
        return
    w62 = _m().w62
    if name in prov.data["downstream_stale"]:
        raise w62.FamilyZProvenanceMismatchStop(f"{name}はstale(親の再生成後)。明示 --regenerate-stage {name} が必要(自動再生成しない)")
    entry = prov.stage_entry(name)
    if entry is not None and entry["input_sha256"] != input_sha:
        raise w62.FamilyZProvenanceMismatchStop(f"{name}: 親sha不一致 entry.input={entry['input_sha256'][:12]} 現在={input_sha[:12]}")


def _part2_hook(ctx, key: str):
    hook = ctx.hooks.get(key)
    if hook is None and ctx.mode != "real":
        raise YE2EStop(f"FAMILY_Y_PART2_NO_HOOK: mock/dry-runではhooks.{key}が必要(実APIへは出さない)")
    return hook


def _part2_cand_step(ctx, prov, level: str) -> dict:
    """候補抽出(または保存済みの再利用)→全候補の解説の事前生成(Step Bの唯一の呼出点=pregen_stage。resumeは未生成分のみ)→Human確認/明示宣言/適格0件の即確定の評価。
    KP候補生成と同じ待機点の前に呼ぶ(両level)。"""
    p2w = _p2w()
    g = p2w.g
    names = PART2_STAGES[level]
    paragraphs, label = _part2_inputs(ctx, level)
    sd = _part2_dir(ctx, level)
    force = ctx.regenerate_stage == names["cand"]
    cand_sha = p2w.cand_input_sha(sd, paragraphs, label, prov.stage_entry(names["cand"]))   # 確定済みの文法はmodel/Prompt変更で再抽出しない(来歴の入力shaを据え置く)
    _stage_precheck(prov, names["cand"], cand_sha, force)
    hook = _part2_hook(ctx, "part2_extract_call_fn")
    try:
        with ctx.stage_context(f"part2_cand_{level}"):
            res = p2w.candidate_stage(sd, level=level, run_dir=ctx.out_dir, family="y", slug=ctx.slug, paragraphs=paragraphs, label=label, run_hint=ctx.out_dir,
                                      extract_call_fn=hook, client=ctx.llm_client, budget_guard=lambda stage, est: _guard(ctx, f"part2_{stage}", est),
                                      force_extract=force)
    except (g.Part2Error, g.Part2InputError) as e:
        # D4: 拒否された --regenerate-stage(確定済み文法のrevoke前)は part2_failed.json を書かない(失敗ではなく操作の拒否)。次の一手は同じregenerateの繰り返しにしない
        refused = _regenerate_refused(e)
        if not refused:
            g.write_failed_record(sd, e, next_command=_part2_resume_next(ctx, level), stage=names["cand"])
        raise YE2EStop(f"FAMILY_Y_PART2_NOT_OK({names['cand']}): {e}(候補抽出に失敗。TTSへ渡さずSTOP。"
                       f"次の一手: {_regenerate_refused_hint(ctx, level) if refused else _part2_resume_next(ctx, level)})") from e
    _m().w62.ensure_stage(prov, names["cand"], cand_sha, f"{sd}/part2_cand_stage.json",
                          lambda: (p2w.cand_marker(sd, paragraphs, label, level=level), {"label": label}), regenerate=force)
    pre_hook = _part2_hook(ctx, "part2_explain_call_fn")
    try:
        with ctx.stage_context(f"part2_expl_{level}"):
            pre = p2w.pregen_stage(sd, level=level, next_command=_part2_resume_next(ctx, level), run_hint=ctx.out_dir, explain_call_fn=pre_hook,
                                   client=ctx.llm_client, budget_guard=lambda stage, est: _guard(ctx, f"part2_{stage}", est))   # 失敗記録(part2_failed.json)はpregen_stageが書く
    except (g.Part2Error, g.Part2InputError) as e:
        raise YE2EStop(f"FAMILY_Y_PART2_NOT_OK({names['expl']}): {e}(解説の事前生成に失敗。TTSへ渡さずSTOP。記録={sd}/{g.FAILED_FILENAME}。"
                       f"次の一手: {_part2_resume_next(ctx, level)})") from e
    return dict(res, pregen=pre)


def _regenerate_refused(e) -> bool:
    """確定済み文法のrevoke前の --regenerate-stage / 再選定系の拒否(確定内容保護のguard由来)かどうか。"""
    msg = str(e)
    return "CONFIRMED_CONTENT_LOCKED" in msg


def _regenerate_refused_hint(ctx, level: str) -> str:
    return (f"確定済みの文法(Part 2 {level})は --regenerate-stage では変えられません。内容を変えるときは先に "
            f"`py er128_kp_confirmed_content_01.py revoke --run {ctx.out_dir} --level {level} ...`(確定の取消し)を実行してください。変えないなら何もせず `--stage kp` を再実行")


def _part2_final_step(ctx, prov, level: str, p1_items: list = None) -> str:
    """確定済みの文法reviewから finalize(**LLM 0 call**・再抽出なし・Step Bなし)。part2_<level>のinput_sha=sha(text_sha|label|文法の確定selection_signature)。"""
    p2w = _p2w()
    g = p2w.g
    w62 = _m().w62
    khr = _khr()
    names = PART2_STAGES[level]
    paragraphs, label = _part2_inputs(ctx, level)
    sd = _part2_dir(ctx, level)
    doc, review, _res = p2w.load_state(sd)
    if doc is None or review is None:
        raise YE2EStop(f"FAMILY_Y_PART2_NOT_READY: 文法の候補/reviewがありません({names['cand']}が未実行)")
    if review["status"] not in khr.FORWARD_STATUSES_BY_KIND["grammar"]:
        raise YKpReviewPending(f"{khr.PENDING_MARKER} Part 2(文法 {level})のHuman確認待ち: status={review['status']}", [p2w.gr.pending_summary(sd, review)])
    pool = _part2_pool(ctx, level, p1_items)
    input_sha = g.final_stage_input_sha(paragraphs, label, review)
    force = ctx.regenerate_stage == names["final"]
    try:
        _stage_precheck(prov, names["final"], input_sha, force)
    except w62.FamilyZProvenanceMismatchStop as e:
        raise type(e)(f"{e} 次の一手: {_part2_next(ctx, level)}") from e

    def runner():
        try:
            with ctx.stage_context(f"part2_final_{level}"):
                out = p2w.finalize_stage(sd, level=level, paragraphs=paragraphs, label=label, ref_ja_pool=pool, write=False)
        except g.Part2PendingReview as e:
            raise YKpReviewPending(f"{khr.PENDING_MARKER} Part 2(文法 {level})のHuman確認待ち: {e.status}", [p2w.gr.pending_summary(sd, review)]) from e
        except p2w.Part2NotConfirmed as e:   # Part 1訳との食い違いISSUE(失敗ではなく待機)
            raise YKpReviewPending(str(e), e.pending) from e
        except (g.Part2Error, g.Part2InputError) as e:
            g.write_failed_record(sd, e, next_command=_part2_next(ctx, level), stage=names["final"])
            raise YE2EStop(f"FAMILY_Y_PART2_NOT_OK({names['final']}): {e}(finalizeに失敗。TTSへ渡さずSTOP。記録={sd}/{g.FAILED_FILENAME}。"
                           f"次の一手: {_part2_next(ctx, level)})") from e
        res = out["result"]
        p2w.write_md(sd, res)
        return json.dumps(res, ensure_ascii=False, indent=2), {"part2_status": res.get("status"), "review_status": review["status"],
                                                              "grammar_selection_signature": review["selection_signature"]}

    r = _ensure(ctx, prov, names["final"], input_sha, f"{sd}/{g.RESULT_FILENAME}", runner)
    fp = f"{sd}/{g.FAILED_FILENAME}"
    if os.path.exists(fp):
        os.replace(fp, fp.replace(".json", ".resolved.json"))     # 成功したら失敗記録は解決済みへ退避(削除しない)
    return r["status"]


def _part2_pool(ctx, level: str, p1_items: list = None) -> dict:
    """Part 1訳との食い違い検査用pool。Part 1の対象level(Advanced=常に / Standard=display_spec付き)だけ。マーク無しStandardはPart 1が無い=空(検査対象なし)。"""
    if not _part1_level_enabled(ctx, level):
        return {}
    p2w = _p2w()
    p = _part1_ja_path(ctx, level)
    return p2w.part1_ref_ja_pool(p1_items if p1_items is not None else _part1_items(ctx, level), _rj(p) if os.path.exists(p) else None)


def _assert_part2_final(ctx, where: str, *, level: str) -> dict:
    """Part 2を使う側の入口: 無い/古い/確定不一致=YE2EStop、文法のHuman確認待ち=YKpReviewPending(rc=4)。resultを返す。"""
    p2w = _p2w()
    g = p2w.g
    paragraphs, label = _part2_inputs(ctx, level)
    try:
        return p2w.require_final(_part2_dir(ctx, level), paragraphs, label, level=level, next_command=_part2_next(ctx, level), where=where,
                                 ref_ja_pool=_part2_pool(ctx, level))
    except p2w.Part2NotConfirmed as e:
        raise YKpReviewPending(str(e), e.pending) from e
    except (g.Part2Error, g.Part2InputError) as e:
        raise YE2EStop(f"FAMILY_Y_PART2_NOT_READY({where}, {level}): {e}") from e


def _assert_study_ready(ctx, where: str) -> dict:
    """使う側(tts_b1b/gate/assemble/pages/page_verify)の入口: KP確定+Part 1(解説・訳)の存在と最新性+Part 2(文法)の確定・最新性(Advanced)。未確定=rc=4待機、古い/不整合=STOP。"""
    _assert_kp_review_consistent(ctx, ADV_LEVEL, where)
    items = _part1_items(ctx, ADV_LEVEL)
    _require_part1_fresh(ctx, items, where, ADV_LEVEL)
    _require_part1_ja_fresh(ctx, items, where, ADV_LEVEL)
    return _assert_part2_final(ctx, where, level=ADV_LEVEL)


def _assert_std_study_ready(ctx, where: str) -> dict:
    """Standardの学習テキスト(Part 1[display_spec付きのときだけ]+Part 2[文法])の入口。**pages/page_verifyだけ**から呼ぶ(ページ専用=tts_a2/gate/assembleの前提にしない)。
    マーク無しの旧StandardはPart 1なし(従来どおり)。Part 1が対象なのに解説・訳が無い/古い=STOP(黙って欠落させない)。"""
    _assert_kp_review_consistent(ctx, STD_LEVEL, where)
    if _part1_level_enabled(ctx, STD_LEVEL):
        items = _part1_items(ctx, STD_LEVEL)
        _require_part1_fresh(ctx, items, where, STD_LEVEL)
        _require_part1_ja_fresh(ctx, items, where, STD_LEVEL)
    return _assert_part2_final(ctx, where, level=STD_LEVEL)


PART1_MARKER = "Vocabulary &amp; Expressions"
PART2_MARKER = "Grammar &amp; Sentence Structure"


PAGE_SECTION_IDS = {"b1b": "advanced", "a2": "standard"}


def _verify_part2_outputs(ctx) -> dict:
    """両levelについて 確定 <-> part2_result.json <-> study_text/*.md <-> 試聴ページ(index.html)の**当該levelの節**を照合(節単位の4者一致、kind="grammar")。
    各節に文法ブロックがちょうど1個(取り違え・欠落・重複はfail-closed)。Advancedの節はPart 1の直後にPart 2。"""
    import er_user_listening_page_common_01 as cp
    p2w = _p2w()
    g = p2w.g
    idx = f"{ctx.pages_dir}/index.html"
    with open(idx, encoding="utf-8") as f:
        idx_html = f.read()
    out = {"index_page": "OK"}
    for lv in LEVELS:
        paragraphs, label = _part2_inputs(ctx, lv)
        section = cp.level_section_html(idx_html, PAGE_SECTION_IDS[lv])
        try:
            p2w.verify_outputs(_part2_dir(ctx, lv), paragraphs, label, level=lv, next_command=_part2_next(ctx, lv), where=f"stage_page_verify({lv})",
                               ref_ja_pool=_part2_pool(ctx, lv), md_path=f"{_part2_dir(ctx, lv)}/{g.PART2_FILE_STEM}.md", html_text=section)
        except (g.Part2Error, g.Part2InputError) as e:
            raise YE2EStop(f"FAMILY_Y_PART2_OUTPUT_MISMATCH({lv}): {e}") from e
        n2 = g.count_grammar_blocks(section)
        if n2 != 1:
            raise YE2EStop(f"FAMILY_Y_PART2_OUTPUT_MISMATCH({lv}): {PAGE_SECTION_IDS[lv]}の節のPart 2ブロックが{n2}個です(ちょうど1個のはず)")
        n1 = section.count(PART1_MARKER)
        if _part1_level_enabled(ctx, lv):      # vocab対象level(Advanced=常に / Standard=display_spec付き): Part 1がちょうど1個・Part 2の直前(0個・2個はSTOP。黙った欠落を許さない=M11)
            if n1 != 1 or section.index(PART1_MARKER) > section.index(PART2_MARKER):
                raise YE2EStop(f"FAMILY_Y_PART1_OUTPUT_MISMATCH({lv}): Part 1が{n1}個です(vocab対象levelではちょうど1個、かつPart 2の直前[Part 1→Part 2の順]のはず)")
        elif n1:
            raise YE2EStop(f"FAMILY_Y_PART1_OUTPUT_MISMATCH({lv}): Part 1が{n1}個あります(display_specの無い旧Standardは従来どおりPart 1なし。遡及なし)")
        out[lv] = {"section": PAGE_SECTION_IDS[lv], "part1_blocks": n1, "part2_blocks": n2}
    return out


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


def resolve_style_profile(ctx, *, write: bool = True) -> str:
    """承認Style profileを課金前に解決する(X方式 resolve_run_profile+固定記録+M2/M5。DESIGN_02)。新規run dirは承認profileを固定記録、
    既存run state(TTS結果/Review Lock/人間承認)があり記録の無いdirは Style混在を避けるため課金前にSTOP(M2。legacy waiver/`default`指定の経路は作らない)。
    migrate_record(同一dirでのprofile移行)はYでは使用しない(日本語roleの照合が自己一致になるため。Opus見落とし1)。"""
    ya = _ya()
    sp = ya.style_profile_mod
    approved = ya.Y_APPROVED_STYLE_PROFILE
    try:
        sp.assert_profile_backend(approved, ya.TTS_BACKEND)
        pid, source = sp.resolve_run_profile(ctx.out_dir, approved, write=False, tts_backend=ya.TTS_BACKEND)
        if write:
            pid, source = sp.resolve_run_profile(ctx.out_dir, approved, write=True, tts_backend=ya.TTS_BACKEND)
    except sp.StyleProfileStop as e:
        raise YE2EStop(f"FAMILY_Y_STYLE_PROFILE_STOP: {e}") from e
    if pid != approved:
        raise YE2EStop(f"FAMILY_Y_STYLE_PROFILE_NOT_APPROVED: resolved={pid!r} approved={approved!r}")
    ctx.style_profile, ctx.style_profile_source = pid, source
    return pid


def _style_profile(ctx) -> str:
    """stageが使うprofile。未解決/承認profile以外/固定記録の欠落・不一致はSTOP(resume時に別profileが紛れない)。"""
    ya = _ya()
    sp = ya.style_profile_mod
    if ctx.style_profile != ya.Y_APPROVED_STYLE_PROFILE:
        raise YE2EStop(f"FAMILY_Y_STYLE_PROFILE_NOT_RESOLVED: ctx.style_profile={ctx.style_profile!r}(resolve_style_profile未実行または承認profile以外。Y新規runは承認profile必須)")
    try:
        rec = sp.read_record(ctx.out_dir)
        if rec is None or sp.verify_record(rec) != ctx.style_profile:
            raise YE2EStop(f"FAMILY_Y_STYLE_PROFILE_RECORD_MISSING_OR_MISMATCH: {sp.record_path(ctx.out_dir)}")
    except sp.StyleProfileStop as e:
        raise YE2EStop(f"FAMILY_Y_STYLE_PROFILE_RECORD_INVALID: {e}") from e
    return ctx.style_profile


def _tts_input_sha(ctx, lv) -> str:
    ya = _ya()
    kp = f"{_kp_assets_dir(ctx, lv)}/keywords_canonicalized.json"
    ex = f"{ctx.out_dir}/key_phrases/b1b/kp_explanations.json"
    parts = [_sha(_rd(_level_text_path(ctx, lv))), _sha(_rd(f"{ctx.out_dir}/support/{lv}_support.json")), _m().w62.file_sha(kp),
             _m().w62.file_sha(ex) if lv == "b1b" else "", json.dumps(ya.segment_voice_map(), sort_keys=True), _sha(_rd(_ja_path(ctx))) if lv == "a2" else "",
             ya.TTS_BACKEND, _style_profile(ctx)]
    return _sha("|".join(parts))


def stage_tts(ctx, lv: str) -> dict:
    ya = _ya()
    w62 = _m().w62
    prov = _prov(ctx)
    _assert_kp_review_consistent(ctx, lv, f"tts_{lv}")
    _resolve_highlights_or_stop(ctx, f"tts_{lv}", (lv,))     # SLOT-23: 本文ハイライトの特定不能(ISSUE)は有料TTSの前にSTOP(display_spec付きlevelだけ。マーク無しは何もしない)
    if lv == "b1b":
        _assert_study_ready(ctx, "tts_b1b")        # Part 1/Part 2(Advanced)の存在・最新性・確定を使う側の入口で確認(未確定=rc=4待機、古い=STOP)。Standardはページ専用[pages/page_verifyの入口]
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
                s = ya.generate_y_b1_segments(ctx.out_dir, style_profile=_style_profile(ctx), guard=guard)
            else:
                s = ya.generate_y_a2_segments(ctx.out_dir, ja_title, style_profile=_style_profile(ctx), guard=guard)
        res_path = f"{ctx.out_dir}/{lv}/audit/tts_generation_results.json"
        return json.dumps({"summary": s, "results_sha256": w62.file_sha(res_path)}, ensure_ascii=False, indent=2), \
            {"tts_backend": ya.TTS_BACKEND, "narrator_voice": ya.narrator_voice(), "voices": ya.segment_voice_map(), "chunk_tts": CHUNK_TTS_MANIFEST}

    r = _ensure(ctx, prov, unit, _tts_input_sha(ctx, lv), f"{ctx.out_dir}/tts_{lv}_stage.json", runner)
    return {"status": r["status"], "unit": unit}


# ------------------------------------------------------------
# stage: gate / assemble / pages / page_verify(API 0)
# ------------------------------------------------------------
def _require_fresh(prov, name):
    if name in prov.data["downstream_stale"] or prov.stage_entry(name) is None:
        raise YE2EStop(f"FAMILY_Y_STAGE_NOT_FRESH: {name}(未実行またはstale。明示 --regenerate-stage {name} または該当stageの実行が必要)")


def _write_style_actual_vs_approved(ctx) -> None:
    """level別の照合表(a2/b1b/audit/style_actual_vs_approved.json)を theme直下 audit/style_actual_vs_approved.json に統合する(受入の実測照合表。Gate 7(3))。"""
    levels = {}
    for lv in LEVELS:
        p = f"{ctx.out_dir}/{lv}/audit/style_actual_vs_approved.json"
        if os.path.exists(p):
            levels[lv] = _rj(p)
    _wj(f"{ctx.out_dir}/audit/style_actual_vs_approved.json",
        {"profile_id": ctx.style_profile, "approved_profile": _ya().Y_APPROVED_STYLE_PROFILE, "levels": levels,
         "all_match": bool(levels) and all(v.get("all_match") for v in levels.values())})


def stage_gate(ctx) -> dict:
    ya = _ya()
    prov = _prov(ctx)
    for lv in LEVELS:
        _require_fresh(prov, f"tts_{lv}")
    _assert_study_ready(ctx, "gate")
    out = {}
    for lv in LEVELS:
        _require_fresh(prov, f"tts_{lv}")
        g = ya.y_style_gate(ctx.out_dir, lv, _style_profile(ctx))
        out[lv] = {"status": g["status"], "y_body_blocked": g["y_body_blocked"], "x_gate_blocked_after_filter": g["x_gate_blocked_after_filter"],
                   "y_profile_blocked": g.get("y_profile_blocked", []), "coverage": g.get("coverage")}
    _wj(f"{ctx.out_dir}/gate_summary.json", out)
    _write_style_actual_vs_approved(ctx)
    bad = {lv: v for lv, v in out.items() if v["status"] != "PASS"}
    if bad:
        raise YE2EStop(f"FAMILY_Y_GATE_BLOCK: {json.dumps(bad, ensure_ascii=False)[:600]}(Gateを回避しない。該当segmentの再生成/Human確認が必要)")
    return out


def stage_assemble(ctx) -> dict:
    ya = _ya()
    prov = _prov(ctx)
    for lv in LEVELS:
        _require_fresh(prov, f"tts_{lv}")
    _assert_study_ready(ctx, "assemble")
    out = {}
    for lv in LEVELS:
        _require_fresh(prov, f"tts_{lv}")
        s = ya.assemble_level(ctx.out_dir, lv, style_profile=_style_profile(ctx), slug=ctx.slug, article_text=ys.canonical_body(_rd(_level_text_path(ctx, lv))))
        out[lv] = {k: s.get(k) for k in ("status", "out_path", "duration_seconds", "clipping_detected")}
        if s.get("status") != "OK":
            _wj(f"{ctx.out_dir}/assemble_summary.json", out)
            raise YE2EStop(f"FAMILY_Y_ASSEMBLE_BLOCKED({lv}): status={s.get('status')}(Gateを回避して通し音声を作らない)")
    _wj(f"{ctx.out_dir}/assemble_summary.json", out)
    return out


def _page_notice_applies(ctx) -> bool:
    """Voice説明文(承認文言)の適用判定: 実投稿に基づく記事か(Theme Packageの全Voiceの経験に非空source_ids)。
    Theme Packageを読めない場合は判定不能=STOP(黙って説明文を落とさない/根拠なく出さない)。"""
    if not ctx.theme_package_path or not os.path.exists(ctx.theme_package_path):
        raise YE2EStop("FAMILY_Y_THEME_PACKAGE_MISSING_FOR_NOTICE: Voice説明文の適用判定(実投稿に基づく記事か)に --theme-package <json> が必要です(pages/page_verifyも同じ指定)")
    return ys.theme_package_is_post_based(_rj(ctx.theme_package_path))


def _page_audience(ctx) -> str:
    import er_user_listening_page_common_01 as cp
    return cp.normalize_audience(getattr(ctx, "page_audience", "public"))


def _resolve_highlights_or_stop(ctx, where: str, levels: tuple = LEVELS) -> dict:
    """SLOT-23(委任_04D): 本文ハイライト(①太字+二重下線/②太字+下線/③下線)の解決。display_spec付き(=確定レコードのマーク。flag非経由)のlevelだけ
    {level: 解決結果} を返す。マーク無しlevel(旧run)は含めない=従来とバイト同一。解決器は共通 er_learning_highlight_01 の1箇所(再実装しない)。
    ISSUE(特定不能・部分交差・本文sha不一致・範囲内0件の①②)は原因コード付きでSTOP(部分適用・黙って落とすことはしない)。NOTICEはauditへ記録(停止しない)。
    マーク発行(new_review接続)は本関数の範囲外(B班)。"""
    ya = _ya()
    out = {}
    for lv in levels:
        try:
            res = ya.resolve_y_highlights(ctx.out_dir, lv)
        except (OSError, ValueError, KeyError) as e:
            raise YE2EStop(f"FAMILY_Y_HIGHLIGHT_INPUT_NOT_READY({lv}, {where}): {type(e).__name__}: {e}(確定レコード・候補doc・本文のいずれかが読めません。ページを生成しません)") from e
        if res is None:
            continue
        slim = {"level": lv, "status": res["status"], "stats": res.get("stats"), "notices": res.get("notices"), "issues": res.get("issues"),
                "highlights": [{k: h.get(k) for k in ("candidate_id", "kind", "used_form", "surface", "sentence_id", "relocated_from", "decorate")}
                               | {"units": [p["unit_key"] for p in h.get("pieces") or []]} for h in res.get("highlights") or []]}
        os.makedirs(f"{ctx.out_dir}/audit", exist_ok=True)
        _wj(f"{ctx.out_dir}/audit/highlight_resolution_{lv}.json", slim)
        if res["status"] != "OK":
            raise YE2EStop(f"FAMILY_Y_HIGHLIGHT_ISSUE({lv}, {where}): " + "; ".join(f"{i['code']}[{i.get('candidate_id')}] {i.get('detail')}" for i in res["issues"])
                           + f"(原因コードは er_learning_highlight_01 / CONTRACT_03 §4。ページを生成しません。記録={ctx.out_dir}/audit/highlight_resolution_{lv}.json)")
        out[lv] = res
    return out


def stage_pages(ctx) -> dict:
    import er_user_listening_page_common_01 as cp
    ya = _ya()
    audience = _page_audience(ctx)                              # 既定public(マーカーなし)。devはCLI --page-audience devの明示指定のみ(env/設定での暗黙ONなし)
    show_notice = _page_notice_applies(ctx)
    ja_segs = ys.split_y_article(_rd(_ja_path(ctx)))["segments"]
    title = ys.split_y_article(_rd(_ja_path(ctx)))["title"]
    _assert_kp_review_consistent(ctx, "a2", "stage_pages")
    p2res = _assert_study_ready(ctx, "stage_pages")           # Part 1/Part 2(Advanced)の存在・最新性・確定との一致(未確定=rc=4、古い=STOP)
    p2res_std = _assert_std_study_ready(ctx, "stage_pages")   # Standardの学習テキスト(Part 1[display_spec付きのみ]+Part 2)。ページ専用=ここ(pages/page_verify)だけで確認する
    hl_results = _resolve_highlights_or_stop(ctx, "stage_pages")  # SLOT-23: display_spec付きlevelだけ。特定不能(ISSUE)はページ生成(mp3化)前にSTOP。マーク無しlevelは空=従来とバイト同一
    study_by_level = {}
    for lv, p2r in ((ADV_LEVEL, p2res), (STD_LEVEL, p2res_std)):
        part1_html = ""
        if _part1_level_enabled(ctx, lv):                          # Adv=常に / Std=display_spec付きのときだけ。study_text/は毎回再組立して保存(本文・gloss更新に追従)
            rows = _assemble_study_rows(ctx, _part1_items(ctx, lv), lv)
            try:
                part1_html = _p1().render_html_block(rows)
            except _p1().KpGeneralExplanationError as e:
                raise YE2EStop(f"FAMILY_Y_KP_PART1_RENDER_NOT_OK({lv}): {e}") from e
        study_by_level[lv] = _p2w().compose_page_html(part1_html, p2r)   # 共通builder1つ・同じテンプレート: Part 1ブロック直後にPart 2(0件は固定文面)。Part 1が無いlevelはPart 2のみ
    study_html, study_html_std = study_by_level[ADV_LEVEL], study_by_level[STD_LEVEL]
    audio_dir = f"{ctx.pages_dir}/audio"
    os.makedirs(audio_dir, exist_ok=True)
    levels = [ya.build_page_rows(ctx.out_dir, lv, audio_dir, "audio", ja_paragraphs=ja_segs, audience=audience, highlights_result=hl_results.get(lv))
              for lv in (STD_LEVEL, ADV_LEVEL)]     # Standard, Advanced の順
    meaning_by_lv = ya.highlight_meaning_html(hl_results)     # ③の訳リスト(level節の台本表の直後=table/div.scriptの外。Part 1の前)
    for lv, lvd in zip((STD_LEVEL, ADV_LEVEL), levels):
        html_by_id = {"advanced": study_html, "standard": study_html_std}
        pre = meaning_by_lv.get(lv, "")
        if html_by_id.get(lvd["id"]) or pre:
            lvd["study_html"] = pre + (html_by_id.get(lvd["id"]) or "")
    html_text = ya.render_y_page(title, levels, aux_html=ya.voice1_candidates_aux_html(ctx.out_dir, audio_dir, "audio"),      # 候補が無ければ空(従来と同一)
                                 show_notice=show_notice, audience=audience, highlight=bool(hl_results))
    if audience == cp.AUDIENCE_PUBLIC and cp.count_chunk_markers(html_text):
        raise YE2EStop(f"FAMILY_Y_PUBLIC_PAGE_HAS_CHUNK_MARKER: 公開用ページに開発用Chunk境界マーカーが{cp.count_chunk_markers(html_text)}件あります(出力しない)")
    page = f"{ctx.pages_dir}/index.html" if audience == cp.AUDIENCE_PUBLIC else f"{ctx.pages_dir}/index_dev.html"      # devは公開用index.htmlを上書きしない
    with open(page, "w", encoding="utf-8") as f:
        f.write(html_text)
    return {"page": page, "levels": [lv["id"] for lv in levels], "audience": audience, "voice_notice_shown": show_notice,
            "chunk_markers": cp.count_chunk_markers(html_text), **({"highlight_levels": sorted(hl_results)} if hl_results else {})}


def evaluate_page_verify(html_text: str, base_dir: str, expect_notice: bool = True) -> list:
    """公開用(public)ページの検証。開発用Chunk境界マーカーが1件でもあればNG(check_pageのno_chunk_marker_in_public)。
    expect_notice=False=実投稿に基づかない記事(説明文が無いこと)。"""
    import er_user_listening_page_common_01 as cp
    v = []
    chk = cp.check_page(html_text, base_dir=base_dir, audience=cp.AUDIENCE_PUBLIC)
    if chk.get("overall") != "PASS":
        v.append(f"STANDARD_PAGE_CHECK_NOT_PASS: {[n for n, x in (chk.get('checks') or {}).items() if not x.get('ok')]}")
    n = ys.check_y_page_notice(html_text, expect_notice=expect_notice)
    v.extend(n["violations"])
    return v


def _verify_kp_selection(ctx, html_text: str) -> dict:
    """KP Human Review検証5: 確定KP <-> KP artifact <-> TTS結果 <-> study_text(Part 1) <-> 試聴ページ。不一致=STOP。"""
    import er_user_listening_page_common_01 as cp
    khr = _khr()
    out = {}
    for lv in LEVELS:
        has_p1 = _part1_level_enabled(ctx, lv)      # Part 1の対象level(Advanced=常に / Standard=display_spec付き)。study_textは当該levelのdir(Advanced=<out>/study_text・Standard=<out>/a2/study_text)
        in_section = PART1_MARKER in cp.level_section_html(html_text, PAGE_SECTION_IDS[lv])
        try:
            out[lv] = khr.verify_selection_matches_outputs(
                _kp_src_dir(ctx, lv), level=lv, tts_results_path=f"{ctx.out_dir}/{lv}/audit/tts_generation_results.json",
                study_text_json=(f"{_part2_dir(ctx, lv)}/{_p1().PART1_FILE_STEM}.json" if has_p1 else None),
                page_paths=[f"{ctx.pages_dir}/index.html"], vocab_page_paths=([f"{ctx.pages_dir}/index.html"] if has_p1 and in_section else None),
                require_src_contract=False)
        except khr.KpReviewInconsistent as e:
            raise YE2EStop(f"FAMILY_Y_KP_SELECTION_OUTPUT_MISMATCH({lv}): {e}") from e
    return out


def _verify_highlights_on_page(ctx, html_text: str) -> dict:
    """SLOT-23 G3(委任_04D): level節ごとに er128_kp_highlight_01.verify_highlights を実行(網羅=data-hl単位ちょうど1出現/本文不変/③訳一致/public混入0)。
    FAIL=STOP。確定内容保護のkill switch無効時はSKIPPED_DISABLED(disabled markerを記録)。マーク無しlevelの節に data-hl/lk-meaning があればSTOP。"""
    import er_user_listening_page_common_01 as cp
    import er128_kp_highlight_01 as g3
    ya = _ya()
    out = {}
    for lv in LEVELS:
        section = cp.level_section_html(html_text, PAGE_SECTION_IDS[lv])
        res = ya.resolve_y_highlights(ctx.out_dir, lv)
        if res is None:
            if "data-hl" in section or "lk-meaning" in section:
                raise YE2EStop(f"FAMILY_Y_HIGHLIGHT_UNEXPECTED({lv}): display_specが無いlevelのページ節に本文ハイライト/訳リストがあります(遡及なし・マーク無しは従来表示のはず)")
            out[lv] = {"status": "NOT_MARKED"}
            continue
        if res["status"] != "OK":
            raise YE2EStop(f"FAMILY_Y_HIGHLIGHT_ISSUE({lv}, stage_page_verify): " + "; ".join(f"{i['code']}[{i.get('candidate_id')}]" for i in res["issues"]))
        texts = [u["texts"][0] for u in ya.y_highlight_display_units(ctx.out_dir, lv)]
        v = g3.verify_highlights(section, {"result": res, "script_texts": texts, "audience": "public"})
        if v["status"] == "FAIL":
            raise YE2EStop(f"FAMILY_Y_HIGHLIGHT_G3_FAILED({lv}): " + "; ".join(f"{p['code']}[{p.get('candidate_id')}] {p['detail']}" for p in v["problems"]))
        out[lv] = {"status": v["status"], "counts": v["counts"], "disabled_marker": v["disabled_marker"], "notices": [n["code"] for n in res.get("notices") or []]}
    return out


def stage_page_verify(ctx) -> dict:
    if _page_audience(ctx) != "public":
        raise YE2EStop("FAMILY_Y_PAGE_VERIFY_DEV_PAGE: 開発用ページ(audience=dev, index_dev.html)は公開用の検証・final manifestの対象外です。--page-audienceを指定せず(public)検証してください")
    page = f"{ctx.pages_dir}/index.html"
    if not os.path.exists(page):
        raise YE2EStop(f"FAMILY_Y_PAGE_MISSING: {page}(pages stageを先に実行)")
    with open(page, encoding="utf-8") as f:
        html_text = f.read()
    viol = evaluate_page_verify(html_text, ctx.pages_dir, expect_notice=_page_notice_applies(ctx))
    _assert_study_ready(ctx, "stage_page_verify")
    _assert_std_study_ready(ctx, "stage_page_verify")
    rec = {"page": page, "violations": viol, "ok": not viol}
    rec["part2_verified"] = _verify_part2_outputs(ctx)           # 確定 <-> part2_result.json <-> md <-> ページの各levelの節(節単位の4者一致。Advancedは Part 1直後)
    rec["kp_selection_verified"] = _verify_kp_selection(ctx, html_text)
    rec["highlight_verified"] = _verify_highlights_on_page(ctx, html_text)     # SLOT-23 G3: 本文ハイライト(level節単位・fail-closed)。マーク無しlevelは装飾0を確認
    _wj(f"{ctx.out_dir}/page_verify_local.json", rec)
    if viol:
        raise YE2EStop(f"FAMILY_Y_PAGE_VERIFY_FAILED: {viol}")
    write_final_manifest(ctx)
    return rec


# unit -> 費用ログ(cost_log.jsonl)のstageタグ。モデルを来歴entryへ転記する(委任_06: text/kp/supportのmodel欄nullの是正。API 0・記録の転記のみ)
UNIT_COST_TAGS = {"text": ("yp_",), "translate_b1b": ("translate",), "translate_a2": ("translate",), "support_b1b": ("support",), "support_a2": ("support",),
                  "kp_b1b": ("kp", "kp_gloss_alignment"), "kp_a2": ("kp", "kp_gloss_alignment"), "kp_expl_b1b": ("kp",), "kp_part1_b1b": ("kp_part1",),
                  "kp_part1_ja_b1b": ("kp_part1_ja",), "kp_part1_a2": ("kp_part1_a2",), "kp_part1_ja_a2": ("kp_part1_ja_a2",), "part2_cand_b1b": ("part2_cand_b1b", "part2_expl_b1b"), "part2_b1b": ("part2_final_b1b",),
                  "part2_cand_a2": ("part2_cand_a2", "part2_expl_a2"), "part2_a2": ("part2_final_a2",),
                  "tts_b1b": ("tts_b1b",), "tts_a2": ("tts_a2",)}
_TEXT_ROUTE_PARTS = ("voice_generate", "lead", "intros", "closing")


def _cost_models_by_tag(ctx) -> dict:
    """{stageタグ: {model_id: 呼出数}}(費用ログの転記。無ければ空)。"""
    path = f"{ctx.out_dir}/cost_log.jsonl"
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            tag, mid = r.get("stage") or "", r.get("model_id")
            if mid:
                out.setdefault(tag, {})
                out[tag][mid] = out[tag].get(mid, 0) + 1
    return out


def _unit_models(unit: str, by_tag: dict) -> dict:
    agg = {}
    for tag, models in by_tag.items():
        if any((tag == pat) or (pat.endswith("_") and tag.startswith(pat)) for pat in UNIT_COST_TAGS.get(unit, ())):
            for m, n in models.items():
                agg[m] = agg.get(m, 0) + n
    return agg


def write_final_manifest(ctx) -> str:
    """成功終了時の最終成果物の一覧(path・実model・routing・prompt sha)。公開(docs/へのコピー)は含まない=別手順。"""
    prov = _prov(ctx)
    tr = {}
    p = f"{ctx.out_dir}/text/text_records.json"
    if os.path.exists(p):
        tr = _rj(p)
    by_tag = _cost_models_by_tag(ctx)
    entries = {}
    for n in UNIT_NAMES:
        e = prov.stage_entry(n)
        if e is None:
            continue
        ent = {k: e.get(k) for k in ("routing_key", "requested_model", "actual_model_id", "response_id", "prompt_sha256", "cost_jpy", "input_sha256", "output_sha256")}
        models = _unit_models(n, by_tag)
        if models:
            ent["models_used"] = models                    # 費用ログ由来(実際に呼ばれたmodel_idと呼出数。LLM+TTS+ASRを含む)
            ent["models_used_scope"] = "費用ログのstageタグ単位の集計(同じタグを共有するunit[translate/support/kp系]は同じ値)"
            llm = [m for m in models if not m.startswith(("gemini", "azure", "gpt-4o"))]
            if ent["actual_model_id"] is None and len(llm) == 1:
                ent["actual_model_id"] = llm[0]
        if n == "text":
            routes = {}
            for part in _TEXT_ROUTE_PARTS:
                rec = tr.get("closing_record") if part == "closing" else (tr.get("records") or {}).get(part)
                if rec:
                    routes[part] = {k: rec.get(k) for k in ("routing_key", "model_id", "expected_model", "effort", "prompt_sha256")}
            if routes:
                ent["routes"] = routes
        if e.get("model") and ent["actual_model_id"] is None:      # Part 1/訳など、entryがmodelを`model`として持つ場合
            ent["actual_model_id"] = e.get("model")
        if e.get("model") and ent["prompt_sha256"] is None:
            ent["prompt_sha256"] = e.get("prompt_sha256")
        entries[n] = ent
    man = {"management_id": MANAGEMENT_ID, "slug": ctx.slug, "run": ctx.run, "mode": ctx.mode, "entry_status": ys.ENTRY_STATUS,
           "page": f"{ctx.pages_dir}/index.html",
           "assembled": {lv: _glob_one(f"{ctx.out_dir}/{lv}/assembled/*.wav") for lv in LEVELS},
           "ja_article": _ja_path(ctx), "closing_record": tr.get("closing_record"),
           "stage_entries": entries,
           "study_text_slots": STUDY_TEXT_SLOTS, "chunk_tts": CHUNK_TTS_MANIFEST, "core_numeric_v4_j2": "not_applicable_Y",
           "support_segments": {lv: list(ys.support_names(lv)) for lv in LEVELS},
           "removed_by_spec": {lv: {n: ys.COMMENT2_REMOVED_SPEC for n in ys.Y_REMOVED_SUPPORT_NAMES[lv]} for lv in LEVELS if ys.Y_REMOVED_SUPPORT_NAMES[lv]},
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
    "support": "Preview/Comment 1〜3(Comment 4・In One Lineなし。AdvancedはComment 2なし)→ support/{b1b,a2}_support.json",
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
    ctx = YContext(slug=args.slug, run=args.run, mode="real", theme_package_path=args.theme_package, reuse_manifest_path=args.reuse_manifest)
    cost_log = f"{ctx.out_dir}/cost_log.jsonl"
    ctx.budget = E2EBudget(args.approved_budget_jpy, args.warn_threshold_jpy, spent_fn=make_real_spent_fn(cost_log), ack_warn=args.ack_warn_threshold)
    st = _m().st
    st.check_stop_sentinel("client:build_real_context", ctx.out_dir)       # client生成前のSTOP確認
    _launch_guard(ctx.out_dir)                                             # client生成前に RESTART_STORM / RUN_LOCK
    resolve_style_profile(ctx)                                             # 課金前: 承認Style profileの解決・固定記録(M2違反/不一致は課金前STOP)
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
    resolve_style_profile(ctx)
    return ctx


def build_parser():
    p = argparse.ArgumentParser(description="Family Y Production runner(FAMILY-Y-PRODUCTION-LAUNCH-01 委任_02B)")
    p.add_argument("--slug", default="y_article")
    p.add_argument("--run", default=DEFAULT_RUN)
    p.add_argument("--theme-package", default=None, help="Theme Package(json)。text stageの入力。seed shaとして来歴に記録")
    p.add_argument("--reuse-manifest", default=None, help="再利用manifest(json)。E-1(宅配案B)でR0のVoice/Lead/紹介を再利用。未指定=全て新規生成")
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
    p.add_argument("--page-audience", default="public", choices=("public", "dev"),
                   help="pages stageの表示対象。public(既定)=Chunk境界マーカーなし(公開用index.html)。dev=開発確認用(index_dev.html)のみ実TTS Chunk境界に⏸を表示。page_verifyはpublic専用")
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
            ctx = YContext(slug=args.slug, run=args.run, mode="dry-run", theme_package_path=args.theme_package, reuse_manifest_path=args.reuse_manifest)
            plan = describe_plan(ctx, stages)
            try:
                plan["style_profile"] = {"approved": _ya().Y_APPROVED_STYLE_PROFILE, "resolved": resolve_style_profile(ctx, write=False), "source": ctx.style_profile_source}
            except Exception as e:  # noqa: BLE001
                plan["style_profile"] = {"approved": _ya().Y_APPROVED_STYLE_PROFILE, "error": f"{e.__class__.__name__}: {e}"}
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
            ctx.reuse_manifest_path = args.reuse_manifest
            _launch_guard(ctx.out_dir)
        else:
            ctx = build_real_context(args)
        ctx.only_segments, ctx.regenerate_stage = ya_only, args.regenerate_stage
        ctx.page_audience = args.page_audience
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
