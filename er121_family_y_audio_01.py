# -*- coding: utf-8 -*-
# ============================================================
# er121_family_y_audio_01.py
# FAMILY-Y-PRODUCTION-LAUNCH-01 委任_02B: Family Y 正式Production の音声層(TTS / Gate / 組立 / 試聴ページ)
# ============================================================
# 位置づけ: Family Y **正式Production**(entry status=FAMILY_Y_PRODUCTION)。DEV Trial(er110_family_y_*)は import しない(隔離: test固定)。
#   Trialの patched_*・alias segment ID(full_story_part3_c2/c3)・Aoede直書き・In One Line・DEV予算skip・Trial名前空間のMaster store を持ち込まない。
# 方針(M-3): 共通工程は X/Z が使う共通module(er019 runner の部品・er103/er109 scope・er117 chunk判定・er078 pww・Master Audio Store 等)を **直接importして呼ぶ**。
#   Y固有として新規に書くのは segment計画・timeline順・Y style gate・試聴ページ行 だけ(構造は er121_family_y_structure_01)。
#   X/Zに新しい共通呼出しが増えるとYのtest(構造一致test: er121_family_y_structure_match_test_01)が落ちる。意図的差分は許可リスト(台帳ID付き)。
# Y固有の要点:
#   - segment ID: y_lead / y_intro_1..3 / y_voice_1..3 / y_closing(er020.resolve_narrative_role がFULL_STORYへ解決)。
#   - Voice: voice_n=固定割当(Algieba/Zephyr/Schedar)。ナレーター=Xの既存Full Story設定 `er003_b1_p9a_audio.VOICE_NAME` を実行時に読む(コードに固定しない)。
#   - 固有名詞アラーム(PNAP)/Run Entity Table/er109 scope は "Y" で入る(Family非依存の仕組み。er103/er109 の APPROVED_SCOPES に "Y" 追加済み)。
#   - Chunk TTS: Y=適用(X方式=段落単位chunk+0.2秒ポーズ。ユーザー正式決定2026-10-25 USER_02 ①、YL-B08)。分割・親wav連結・親集約entry・整合検査・
#     chunk別gain+0.2秒組立は共通module er117(chunk_tts)を直接importして呼ぶ(Yは segment ID規則と segment単位の呼出し配線のみ)。
#     Adv(b1b)本文のみ(X同様、Std本文はchunk化しない)。分割はsegment内の段落単位。segment境界(話者切替)は結合しない。ZのB_r1方式は不採用。
#   - 中核数値v4/J2: 呼ばない(YL-B05)。In One Line/Comment 4/RF(Risk Flagger): 呼ばない(YL-C08/YL-C09/YL-B02)。
#   - Std(a2)本文は X準拠で全segmentに6%減速(YL-A02)。共有 A2_SLOWDOWN_TARGET_SEGMENTS はYのIDを持たないため、Y独自の必須確認(check_std_slowdown)を行う。
# ============================================================
from __future__ import annotations

import contextlib
import functools
import glob
import json
import os
import re

import er003_v1_crosslevel_audio_02_common as crosslevel_common
import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_tts_generate as n3_tts
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er003_v1_sing01_voice01_generate as voice01
import er005_cost_logger as cl
import er006_audio_cost_pilot_02_shared_narration as shared_narration
import er011_human_review_lock_01 as review_lock
import er019_family_x_audio_production_runner_01 as xr
import er019_family_x_kp_explanation_01 as kp_explanation_gen
import er019_family_x_style_profile_01 as style_profile_mod
import er019_family_x_validation_inheritance_01 as validation_inheritance
import er020_tts_retry_local_rewrite_01 as retry_primitive
import er078_pass_with_warning_registry_01 as pww_registry
import er078_secondary_run_scope_01 as secondary_run_scope
import er117_chunk_tts_production_01 as chunk_tts   # 委任_04(USER_02 ①): X方式Chunk TTSの共通module(importのみ・変更しない)
import er103_pnap_runner_hooks_01 as pnap_hooks
import er103_pronunciation_tts_supply_01 as pnap_supply   # noqa: F401  (PNAP供給はxr._pnap_supply経由で呼ぶ。共通moduleの存在・scope連動をtestで確認)
import er109_xz_scope_01 as er109_scope
import er121_family_y_structure_01 as ys

TTS_BACKEND = xr.FAMILY_X_APPROVED_PRODUCTION_TTS_BACKEND
load_json, save_json, load_text, save_text = xr.load_json, xr.save_json, xr.load_text, xr.save_text


class YAudioStop(ys.FamilyYStop):
    pass


# ============================================================
# Voice / scope
# ============================================================
def narrator_voice() -> str:
    """ナレーターのTTS Voice = Xの既存Full Story設定(本文生成関数が呼出時に読む `p9a.VOICE_NAME`)。コードに固定しない。"""
    v = xr.p9a.VOICE_NAME
    if not v:
        raise YAudioStop("FAMILY_Y_NARRATOR_VOICE_MISSING: er003_b1_p9a_audio.VOICE_NAME が空です")
    return v


@contextlib.contextmanager
def tts_voice(voice_name: str):
    """X本文生成関数が呼出時に読む `p9a.VOICE_NAME` をprocess内で一時差替え(finallyで必ず復元)。共有fileは編集しない。"""
    p9a = xr.p9a
    prev = p9a.VOICE_NAME
    p9a.VOICE_NAME = voice_name
    try:
        yield
    finally:
        p9a.VOICE_NAME = prev


def segment_voice_map() -> dict:
    nv = narrator_voice()
    return {sid: ys.voice_of_segment(sid, nv) for sid in ys.Y_SEGMENT_IDS}


@contextlib.contextmanager
def only_segments_scope(selected):
    """`--only-segments`(X仕様と同じ: 非選択segmentは生成せずSKIPPED_NOT_SELECTED、検証済みentryは引継ぎ)。X runnerのモジュール変数を一時差替え。"""
    prev = xr._ONLY_SEGMENTS
    xr._ONLY_SEGMENTS = set(selected) if selected else None
    try:
        yield
    finally:
        xr._ONLY_SEGMENTS = prev


_ONLY_OK_RE = re.compile(r"^(topic_intro|japanese_title|preview|comment_[1-3]|y_(?:lead|closing|intro_[1-3]|voice_[1-3])(?:_k[1-9][0-9]*)?|kp[1-5]_(english|explanation|japanese_meaning))$")


def validate_only_segments(raw: str, level: str):
    """戻り値=(set, error|None)。Y IDとsupport/KPのみ許可(X専用のfull_story_part*/in_one_line/comment_4は拒否)。"""
    sel = {x.strip() for x in (raw or "").split(",") if x.strip()}
    if not sel:
        return None, "--only-segmentsが空です。"
    if level == "both":
        return None, "--only-segmentsは--level both併用禁止です(a2またはb1bを明示)。"
    bad = sorted(x for x in sel if not _ONLY_OK_RE.match(x))
    if bad:
        return None, f"--only-segmentsに未知/対象外のsegment名があります: {bad}"
    k_sel = sorted(x for x in sel if ys.parse_y_chunk_id(x))
    if k_sel and level not in ys.CHUNK_TTS_Y_LEVELS:   # Std/Adv両方がchunk対象(2026-10-26ユーザー正式承認)。対象外levelへの_k指定のみ拒否
        return None, f"--only-segmentsの_k指定(chunk)はchunk対象level({'/'.join(ys.CHUNK_TTS_Y_LEVELS)})のみです: level={level} {k_sel}"
    return sel, None


# ============================================================
# Run Entity Table provider("Y")
# ============================================================
def _ret_seg(text: str, role: str, segment_id: str, alt: str):
    import er103_run_entity_table_01 as ret
    return ret.Seg(text=text, role=role, segment_id=segment_id, alt_texts=(alt,))


class YProvider:
    """Family Y: `<theme_out_dir>/{b1b,a2}/parts.json`+`support_texts.json` から、TTSへ渡るEN script(topic_intro/preview/comment_1-3/Y本文8segment)を集める
    (XProvider と同じ契約: table_path / collect()->(segs, []))。Std(a2)のpreview/commentは日本語のため除外。KP/japanese_titleは対象外。"""

    def __init__(self, theme_out_dir: str):
        self.run_dir = theme_out_dir
        self.table_path = f"{theme_out_dir}/audit/entity_table.json"

    def collect(self) -> tuple:
        segs: list = []
        for lvl in ("b1b", "a2"):
            pj = f"{self.run_dir}/{lvl}/parts.json"
            if not os.path.exists(pj):
                continue
            parts = load_json(pj)
            if parts.get("title"):
                txt = f"Today's topic is {parts['title']}."
                segs.append(_ret_seg(txt, "TOPIC_INTRO", f"{lvl}:topic_intro", n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(txt))))
            sp = f"{self.run_dir}/{lvl}/support_texts.json"
            if lvl == "b1b" and os.path.exists(sp):
                support = load_json(sp)
                for name in ys.support_names("b1b"):          # Advancedはcomment_2なし(2026-10-26ユーザー承認)。Stdのpreview/commentは日本語のため対象外
                    txt = support.get(name)
                    if txt:
                        segs.append(_ret_seg(txt, "PREVIEW" if name == "preview" else "COMMENT", f"{lvl}:{name}",
                                             n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(txt))))
            for sid in ys.Y_SEGMENT_IDS:
                txt = (parts.get("segments") or {}).get(sid)
                if txt:
                    segs.append(_ret_seg(txt, retry_primitive.resolve_narrative_role(sid), f"{lvl}:{sid}", n3_tts.tts_safe_news_en(txt)))
        return segs, []


def y_family_scope(subdir: str):
    """Y TTS段関数(第1引数=theme_out_dir)用decorator。PNAP run scope(Y)+finallyの完成報告hook+Run Entity Table構築(provider=YProvider)。
    共通の `pnap_hooks.run_with_alarm_hook` を直接呼ぶ(XはXProviderを束ねた `pnap_hooks.family_scope` 経由=許可リスト Y-DIFF-RET-PROVIDER)。flag OFFなら素通し。"""
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(theme_out_dir, *args, **kwargs):
            return pnap_hooks.run_with_alarm_hook("Y", f"{theme_out_dir}/{subdir}", fn, theme_out_dir, *args,
                                                  _ret_provider=(lambda: YProvider(theme_out_dir)), **kwargs)
        wrapper.__pnap_scoped__ = True
        return wrapper
    return deco


# ============================================================
# 入力準備(LLM/API 0): 英語記事 → level別 parts.json / support_texts.json
# ============================================================
def write_level_inputs(theme_out_dir: str, level: str, parsed_en: dict, support: dict) -> dict:
    """<theme>/<level>/parts.json(title+Y segment text map)と support_texts.json(preview/comment_1..3。Comment 4は無い)を書く。"""
    names = ys.support_names(level)             # Advancedはcomment_2なし。support dictに旧comment_2が残っていても書き出さない/検査しない
    for k in names:
        if not (support.get(k) or "").strip():
            raise YAudioStop(f"FAMILY_Y_SUPPORT_TEXT_MISSING({level}): {k}")
    d = f"{theme_out_dir}/{level}"
    os.makedirs(f"{d}/audit", exist_ok=True)
    parts = {"family": ys.FAMILY, "level": level, "title": parsed_en["title"], "segments": dict(parsed_en["segments"]),
             "y_segment_order": list(ys.Y_SEGMENT_IDS), "status": "OK"}
    if ys.Y_REMOVED_SUPPORT_NAMES[level]:
        parts["removed_by_spec"] = {n: ys.COMMENT2_REMOVED_SPEC for n in ys.Y_REMOVED_SUPPORT_NAMES[level]}
    save_json(f"{d}/parts.json", parts)
    save_json(f"{d}/support_texts.json", {k: support[k] for k in names})
    return parts


def voice_guard_cached(cached: dict | None) -> dict | None:
    """同一out_dirのresume時、Y本文segmentの前回entryを再利用してよいのは『要求Voiceが記録され一致する』場合だけ
    (run内cacheはsegment ID+テキストのみで照合するため、Voice名を追加照合する。記録なし/不一致entryは再利用せず再生成)。"""
    if not cached:
        return cached
    segs = dict(cached.get("segments") or {})
    dropped = []
    for sid, voice in segment_voice_map().items():
        e = segs.get(sid)
        if e is not None and e.get("y_tts_voice_requested") != voice:
            segs.pop(sid)
            dropped.append(sid)
    vmap = segment_voice_map()
    for k in list(segs):                                  # 委任_04: chunk entryも『親segmentの要求Voiceが記録され一致する』場合だけ再利用
        pc = ys.parse_y_chunk_id(k)
        if pc is not None and (segs[k] or {}).get("y_tts_voice_requested") != vmap.get(pc[0]):
            segs.pop(k)
            dropped.append(k)
    out = dict(cached)
    out["segments"] = segs
    if dropped:
        out["y_dropped_for_voice_mismatch"] = dropped
    return out


def seed_kp_explanations_cache(cached: dict | None, kp: dict, expl_doc: dict) -> dict:
    """kp stageで生成・来歴管理済みのAdv英語解説(kp_explanations.json)を、X共通関数 `_resolve_kp_explanations_text` が再利用できる形で
    cacheへ注入する(TTS段で解説LLMを呼び直さない=隠れたAPI呼出を作らない)。署名はX関数と同じ式。署名不一致ならX関数が再生成するためここで厳密に検査してSTOP。"""
    kp_items = sorted(kp["items"], key=lambda it: it["rank"])
    sig = [kp_explanation_gen.explanation_phrase(it) for it in kp_items]
    gsig = [[kp_explanation_gen.explanation_phrase(it), it.get("key_phrase"), it.get("japanese_gloss", "")] for it in kp_items]
    items = (expl_doc or {}).get("items")
    if not items:
        raise YAudioStop("FAMILY_Y_KP_EXPLANATIONS_MISSING: kp_explanations.jsonがありません(kp stageを先に実行)")
    for it in kp_items:
        row = items.get(str(it["rank"])) or items.get(it["rank"])
        if not row or row.get("status") != "OK":
            raise YAudioStop(f"FAMILY_Y_KP_EXPLANATION_NOT_OK(rank={it['rank']}): TTSへ渡さずSTOP")
    out = dict(cached or {})
    out["key_phrase_explanations_text"] = {**expl_doc, "phrases_signature": sig, "gloss_signature": gsig, "reused_from_previous_run": False}
    if "style_version" not in out:
        out["style_version"] = xr.FAMILY_X_VARIABLE_ROLE_STYLE_VERSION
    return out


# ============================================================
# TTS: Advanced(b1b)
# ============================================================
def _style_resolvers(level: str, tts_backend: str, style_profile: str):
    import er033_tts_flash_lite_family_x_styles_01 as fl_styles

    def _base(role: str):
        if tts_backend != "speech_metadata_flash_lite":
            return None
        return fl_styles.FAMILY_X_ROLE_STYLE_EN.get(role)

    def _role_style(role: str):
        return style_profile_mod.resolve_role_style(style_profile, role, level, _base)
    return _role_style, _base, fl_styles


def _guarded(guard, label, fn):
    """各clipの新規API呼出の直前にSTOP/予算guardを通す(生成時のみ。再利用では呼ばれない)。"""
    if guard is None:
        return fn

    def wrapped():
        guard(label)
        return fn()
    return wrapped


# ============================================================
# Chunk TTS(X方式=段落単位chunk+0.2秒。USER_02 ①、YL-B08)
# 共通er117を直接importして呼ぶ。Yが持つのは(1)Y segment単位の呼出し配線 (2)Y chunk ID規則(ys.Y_CHUNK_ID_RE) だけ。
# ============================================================
def plan_y_chunks(parts: dict) -> dict:
    """Adv(b1b)Y本文8 segmentそれぞれに、X規則(空行区切りの段落が2つ以上のときだけ段落単位chunk。1段落=従来の1 call)を適用する決定論plan。
    親id=segment_id(chunk id=`<segment_id>_k<j>`)。分割はsegmentの内側だけ=segment境界(話者切替)は構造上結合も分割もされない。"""
    segs = parts.get("segments") or {}
    out = {}
    for sid in ys.Y_SEGMENT_IDS:
        pl = chunk_tts.plan_x_part(segs[sid], sid)
        out[sid] = {**pl, "family": ys.FAMILY, "split_method": ys.CHUNK_TTS_Y_METHOD}
    return out


def _assert_chunk_roles(plans: dict) -> None:
    """chunk idが共通role判定でFULL_STORYへ解決されること(ASR/Style/Local Rewrite/Connected Speechの共通機構が正しく掛かる前提)。
    解決されない場合は課金前にSTOP(fail-closed。黙ってrole無しで生成しない)。共通er020のY chunk ID正規表現が未追加のときに発火する。"""
    bad = [c["chunk_id"] for pl in plans.values() if pl.get("chunked") for c in pl["chunks"]
           if retry_primitive.resolve_narrative_role(c["chunk_id"]) != "FULL_STORY"]
    if bad:
        raise YAudioStop(f"FAMILY_Y_CHUNK_ID_ROLE_UNRESOLVED: Y chunk id {bad} が resolve_narrative_role() でFULL_STORYへ解決されません"
                         "(共通er020の_FAMILY_Y_SEGMENT_PATTERNにchunk接尾辞[_k<j>]の追加が必要=委任_04からの要求)。課金前にSTOP")


def _record_chunk_decision(out_dir: str, level: str) -> dict:
    """Chunk TTSの決定記録(audit/chunk_tts_decision.json)+plan(audit/chunk_plan_<level>.json)。戻り値=plan辞書(a2・非適用levelは{})。
    適用可否表がYを非適用に戻されている場合は、承認済み仕様(USER_02 ①)からの逸脱として課金前にSTOP。"""
    if not ys.chunk_tts_applicable(ys.FAMILY):
        raise YAudioStop("FAMILY_Y_CHUNK_TTS_SCOPE_REVERTED: Chunk TTSのY適用はUSER_02 ①でAPPROVED_FOR_PRODUCTION。適用可否表がYを非適用にしています。課金前にSTOP")
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    rec = ys.chunk_decision_record(level)
    plans: dict = {}
    if level in ys.CHUNK_TTS_Y_LEVELS:
        parts = load_json(f"{out_dir}/parts.json")
        plans = plan_y_chunks(parts)
        _assert_chunk_roles(plans)
        try:
            chunk_tts.reconcile_saved_plan(f"{out_dir}/audit/chunk_plan_{level}.json", plans)
        except chunk_tts.ChunkIntegrityError as exc:
            raise YAudioStop(f"FAMILY_Y_CHUNK_PLAN_RECONCILE: {exc}") from exc
        rec["segments"] = {sid: {"chunked": pl["chunked"], "paragraphs": len(chunk_tts.split_x_paragraphs(parts["segments"][sid])),
                                 "reason": pl.get("reason"), "chunk_ids": chunk_tts.chunk_ids(pl)} for sid, pl in plans.items()}
        rec["planner_version"] = chunk_tts.CHUNK_PLANNER_VERSION
        rec["extra_pause_seconds"] = chunk_tts.EXTRA_PAUSE_SECONDS
    else:
        rec["not_applied_reason"] = f"levelがchunk対象外({level}は{ys.CHUNK_TTS_Y_LEVELS}に含まれない)"
    if level == chunk_tts.STD_LEVEL:
        rec["std_slowdown_composition"] = chunk_tts.STD_SLOWDOWN_COMPOSITION    # chunk別6%減速→0.2秒無音→連結(連結後減速は採らない)
    save_json(f"{out_dir}/audit/chunk_tts_decision.json", rec)
    return plans


def _drop_stale_chunk_cache(cached, plans: dict):
    """前回resultsのうち (a)planner_versionが現行と異なるY chunk entry (b)chunk化しなくなったsegmentの前回chunk集約entry は再利用しない。"""
    if not cached:
        return cached
    segs = dict(cached.get("segments") or {})
    drop = [k for k, v in segs.items() if ys.parse_y_chunk_id(k) and ((v or {}).get("chunk_tts") or {}).get("planner_version") != chunk_tts.CHUNK_PLANNER_VERSION]
    drop += [sid for sid, p in plans.items() if not p.get("chunked") and (segs.get(sid) or {}).get("chunk_tts")]
    if not drop:
        return cached
    out = dict(cached)
    out["segments"] = {k: v for k, v in segs.items() if k not in drop}
    return out


@contextlib.contextmanager
def _only_includes_chunks(plans: dict):
    """`--only-segments y_voice_1` のとき、親が選択されていればそのchunk id(`y_voice_1_k<j>`)も選択扱いにする(共通runnerの_only_segments_skipは
    Xのchunk id形式しか親選択を解釈しないため、Yではchunk idを選択集合へ展開する。xr._ONLY_SEGMENTSをfinallyで復元)。"""
    prev = xr._ONLY_SEGMENTS
    if prev is not None:
        extra = {c["chunk_id"] for sid, pl in plans.items() if pl.get("chunked") and sid in prev for c in pl["chunks"]}
        xr._ONLY_SEGMENTS = set(prev) | extra
    try:
        yield
    finally:
        xr._ONLY_SEGMENTS = prev


def _y_chunk_parent_display(plan: dict, segments: dict, voice: str, level: str = "b1b") -> dict:
    d = xr._x_chunk_parent_display(plan, segments)    # 共通の表示用項目(voice/model/style要約・asr_verified。style_profile/prefixはchunk側が正=M1)
    if level == chunk_tts.STD_LEVEL:                  # Std: 親wav=減速後chunk wavの生連結。全chunk減速済みのときだけ親にslowdown_applied=Trueを集約
        d.update(chunk_tts.std_parent_slowdown_fields(plan, segments))
    d["y_tts_voice_requested"] = voice
    d["y_role"] = "voice" if plan["parent_id"] in ys.Y_VOICE_IDS else "narrator"
    d["y_chunked"] = True
    return d


def refresh_y_chunk_parents(out_dir: str, parts: dict, segments: dict, plans: dict, level: str = "b1b") -> dict:
    """chunk化したsegmentの親集約entry(status=planのchunk id一覧から導出。失敗・未生成でも常に書く)+親wav(生連結)を(再)構築する(冪等)。
    generate末尾と、assembleのGate前で呼ぶ(人間承認後の再assembleで親も通る)。親statusはCHUNKS_NOT_ALL_VALIDATED(共有Gateで必ずブロック)かOK。"""
    ap = asm.human_approval_path(out_dir)
    approvals = load_json(ap) if os.path.exists(ap) else {}
    vmap = segment_voice_map()
    out = {}
    for sid, plan in plans.items():
        if not plan.get("chunked"):
            continue
        out[sid] = chunk_tts.refresh_parent_status(
            plan, segments, approvals, asm._segment_gate_status, narration_dir=f"{out_dir}/narration",
            parent_text=parts["segments"][sid], display=_y_chunk_parent_display(plan, segments, vmap[sid], level))
    return out


def _generate_y_body_segment_chunked(plan: dict, cached, narration_dir: str, results: dict, voice: str, role_style, style_profile: str,
                                     tts_backend: str, guard) -> None:
    """chunkごとに、非chunkの本文segmentと『同じ呼出』(news_tail_fix.generate_news_narration_wide_margin。同一Voice/Style/model/Gate/retry/fallback)。
    chunk失敗(status!=OK)後も後続chunkの生成を続ける(OK chunkは再利用されるので再課金は無く、未生成entryを作らない)。直列(chunk順)。"""
    n = len(plan["chunks"])
    for c in plan["chunks"]:
        cid, ctext = c["chunk_id"], c["text"]
        with cl.segment_context(cid):
            def _gen(ctext=ctext, cid=cid):
                with tts_voice(voice):
                    return news_tail_fix.generate_news_narration_wide_margin(
                        xr._pnap_supply(ctext, n3_tts.tts_safe_news_en(ctext)), f"{narration_dir}/{cid}.wav",
                        disfluency_qa=False,
                        enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(cid),
                        enable_repetition_qa=True, enable_pronunciation_resolver=True,
                        style_prefix_override=role_style("FULL_STORY"), tts_backend=tts_backend)
            results[cid] = xr._generate_or_reuse(cached, cid, f"{narration_dir}/{cid}.wav", _guarded(guard, cid, _gen), expected_text=ctext)
        results[cid]["canonical_text"] = ctext
        results[cid]["y_tts_voice_requested"] = voice
        results[cid]["y_role"] = "voice" if plan["parent_id"] in ys.Y_VOICE_IDS else "narrator"
        chunk_tts.attach_chunk_meta(results[cid], plan["parent_id"], c, n)
        if not validation_inheritance.is_untouched_entry(results[cid]):     # Style profile記録は『chunkごと』(親へコピーしない)
            style_profile_mod.attach_segment_profile_record(results[cid], style_profile, "FULL_STORY", role_style("FULL_STORY"))


def _generate_y_body_segment_chunked_a2(plan: dict, cached, narration_dir: str, results: dict, voice: str, role_style_slower, style_profile: str,
                                        tts_backend: str, guard) -> None:
    """Standard(a2)のY本文segment用(CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01、2026-10-26ユーザー正式承認)。chunkごとに、非chunkのStd本文segmentと『同じ呼出』
    (n3_tts.generate_a2_segment_with_slowdown = TTS→6%減速→減速後ASR再検証、同一Voice/Style[減速instruction込み]/Gate/retry/fallback、通算TTS3回の予算もchunk単位)を
    適用する。0.2秒の無音は連結時(減速後)に挿入=ポーズは減速されない。chunk失敗後も後続chunkを続ける。直列(chunk順)。"""
    n = len(plan["chunks"])
    for c in plan["chunks"]:
        cid, ctext = c["chunk_id"], c["text"]
        tts_input = xr._pnap_supply(ctext, n3_tts.tts_safe_news_en(ctext))
        sub = n3_tts.first_words(ctext)
        with cl.segment_context(cid):
            def _gen(tts_input=tts_input, sub=sub, cid=cid):
                with tts_voice(voice):
                    return n3_tts.generate_a2_segment_with_slowdown(
                        tts_input, f"{narration_dir}/{cid}.wav", sub,
                        style_prefix_override=(role_style_slower("FULL_STORY") or n3_tts.A2_ENGLISH_STYLE_PREFIX_SLOWER),
                        disfluency_qa=False,
                        enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(cid),
                        enable_repetition_qa=True, tts_backend=tts_backend)
            results[cid] = xr._generate_or_reuse(cached, cid, f"{narration_dir}/{cid}.wav", _guarded(guard, cid, _gen), expected_text=ctext)
        results[cid]["canonical_text"] = ctext
        results[cid]["y_tts_voice_requested"] = voice
        results[cid]["y_role"] = "voice" if plan["parent_id"] in ys.Y_VOICE_IDS else "narrator"
        chunk_tts.attach_chunk_meta(results[cid], plan["parent_id"], c, n, level=chunk_tts.STD_LEVEL)
        if not validation_inheritance.is_untouched_entry(results[cid]):
            style_profile_mod.attach_segment_profile_record(results[cid], style_profile, "FULL_STORY", role_style_slower("FULL_STORY"))


@secondary_run_scope.with_secondary_run   # AUW 委任_05: run単位SecondaryCache+circuit breaker(Xと同じ共通hook)
@y_family_scope("b1b")   # PNAP run scope(Y)+完成報告hook+Run Entity Table(YProvider)
@er109_scope.family_scope("Y")   # er109 run scope(Y)。例外・STOP時もfinallyで復元
def generate_y_b1_segments(theme_out_dir: str, *, tts_backend: str = TTS_BACKEND, style_profile: str = "default", guard=None) -> dict:
    style_profile_mod.assert_profile_backend(style_profile, tts_backend)
    _role_style, _base, _fl = _style_resolvers("b1b", tts_backend, style_profile)
    out_dir = f"{theme_out_dir}/b1b"
    narration_dir = f"{out_dir}/narration"
    os.makedirs(narration_dir, exist_ok=True)
    chunk_plans = _record_chunk_decision(out_dir, "b1b")      # 課金前: 適用表・plan・role解決・保存済みplanとの一致を確認(違反はSTOP)
    parts = load_json(f"{out_dir}/parts.json")
    support = load_json(f"{out_dir}/support_texts.json")
    kp_path = f"{out_dir}/key_phrases/keywords_canonicalized.json"
    kp = load_json(kp_path) if os.path.exists(kp_path) else None
    shared_raw = ({} if xr._ONLY_SEGMENTS is not None else shared_narration.ensure_all_shared_narration_b1(narration_dir, tts_backend=tts_backend))
    shared_status = xr._summarize_shared_narration(shared_raw)
    cached = _drop_stale_chunk_cache(voice_guard_cached(xr._load_cached_tts_results(out_dir)), chunk_plans)
    if kp is not None:
        expl_path = f"{theme_out_dir}/key_phrases/b1b/kp_explanations.json"
        cached = seed_kp_explanations_cache(cached, kp, load_json(expl_path) if os.path.exists(expl_path) else None)
    results = {}

    topic_text = f"Today's topic is {parts['title']}."
    with cl.segment_context("topic_intro"):
        results["topic_intro"] = xr._generate_or_reuse(
            cached, "topic_intro", f"{narration_dir}/topic_intro.wav", _guarded(guard, "topic_intro", lambda: voice01.generate_charon_english(
                xr._pnap_supply(topic_text, n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(topic_text))),
                f"{narration_dir}/topic_intro.wav",
                enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for("topic_intro"),
                enable_pronunciation_resolver=True, style_prefix_override=_role_style("TOPIC_INTRO"),
                tts_backend=tts_backend)), expected_text=topic_text)
    results["topic_intro"]["canonical_text"] = topic_text

    for name in ys.support_names("b1b"):      # Comment 4は無い(YL-C09)。Comment 2はAdvancedでは削除(2026-10-26ユーザー承認)
        text = support[name]
        with cl.segment_context(name):
            results[name] = xr._generate_or_reuse(
                cached, name, f"{narration_dir}/{name}.wav", _guarded(guard, name, lambda text=text, name=name: voice01.generate_charon_english(
                    xr._pnap_supply(text, n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(text))), f"{narration_dir}/{name}.wav",
                    style_prefix_override=(_role_style("PREVIEW" if name == "preview" else "COMMENT") or n3_tts.B1_PREVIEW_STYLE_PREFIX_CALM),
                    disfluency_qa=True,
                    enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(name),
                    enable_pronunciation_resolver=True, tts_backend=tts_backend)), expected_text=text)
        results[name]["canonical_text"] = text
        if name == "preview" and not validation_inheritance.is_untouched_entry(results[name]):
            style_profile_mod.attach_segment_profile_record(results[name], style_profile, style_profile_mod.ROLE_PREVIEW, _role_style("PREVIEW"))

    vmap = segment_voice_map()
    for name in ys.Y_SEGMENT_IDS:
        text = parts["segments"][name]
        voice = vmap[name]
        if chunk_plans[name]["chunked"]:       # 段落が2つ以上のsegment: 段落単位chunk(親集約entryはループ後に常に書く)。1段落=下の従来経路(1 call)
            with _only_includes_chunks(chunk_plans):
                _generate_y_body_segment_chunked(chunk_plans[name], cached, narration_dir, results, voice, _role_style, style_profile, tts_backend, guard)
            continue
        with cl.segment_context(name):
            def _gen(text=text, name=name, voice=voice):
                with tts_voice(voice):
                    return news_tail_fix.generate_news_narration_wide_margin(
                        xr._pnap_supply(text, n3_tts.tts_safe_news_en(text)), f"{narration_dir}/{name}.wav",
                        disfluency_qa=False,
                        enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(name),
                        enable_repetition_qa=True, enable_pronunciation_resolver=True,
                        style_prefix_override=_role_style("FULL_STORY"), tts_backend=tts_backend)
            results[name] = xr._generate_or_reuse(cached, name, f"{narration_dir}/{name}.wav", _guarded(guard, name, _gen), expected_text=text)
        results[name]["canonical_text"] = text
        results[name]["y_tts_voice_requested"] = voice
        results[name]["y_role"] = "voice" if name in ys.Y_VOICE_IDS else "narrator"
        if not validation_inheritance.is_untouched_entry(results[name]):
            style_profile_mod.attach_segment_profile_record(results[name], style_profile, "FULL_STORY", _role_style("FULL_STORY"))

    refresh_y_chunk_parents(out_dir, parts, results, chunk_plans)       # chunk親集約entry(失敗・未生成でも常に書く)+親wav(生連結)
    if any(pl.get("chunked") for pl in chunk_plans.values()):          # chunk TTSのruntime evidence(分割位置・種別・attempts/fallback/LR/ASR判定)
        save_json(f"{out_dir}/audit/chunk_tts_evidence_b1b.json",
                  {"planner_version": chunk_tts.CHUNK_PLANNER_VERSION, "family": ys.FAMILY, "style_profile": style_profile, "tts_backend": tts_backend,
                   "parents": {sid: chunk_tts.evidence_record(pl, results) for sid, pl in chunk_plans.items() if pl.get("chunked")}})
    if kp is not None:
        kp_results, kp_bundle = xr._generate_key_phrase_segments_b1(kp, narration_dir, cached, tts_backend=tts_backend, style_profile=style_profile)
    else:
        kp_results, kp_bundle = {}, None
    kp_status_str = "OK" if kp is not None else "KP_SCAFFOLD_JSON_MISSING"
    return _finish_results(out_dir, results, kp_results, kp_bundle, shared_status, kp_status_str, level="b1b", tts_backend=tts_backend)


# ============================================================
# TTS: Standard(a2)
# ============================================================
@secondary_run_scope.with_secondary_run
@y_family_scope("a2")
@er109_scope.family_scope("Y")
def generate_y_a2_segments(theme_out_dir: str, japanese_title: str, *, tts_backend: str = TTS_BACKEND, style_profile: str = "default", guard=None) -> dict:
    style_profile_mod.assert_profile_backend(style_profile, tts_backend)
    _role_style, _base, fl_styles = _style_resolvers("a2", tts_backend, style_profile)

    def _base_slower(role: str):
        base = _base(role)
        if base is None:
            return None
        combined = f"{base}\n{n3_tts.A2_SLOWER_PACE_INSTRUCTION.strip()}"
        import er002_common as common
        common.assert_no_wpm_specification(combined)
        return combined

    def _role_style_slower(role: str):
        return style_profile_mod.resolve_role_style(style_profile, role, "a2", _base_slower)

    def _role_style_ja():
        if tts_backend != "speech_metadata_flash_lite":
            return None
        return fl_styles.FAMILY_X_ROLE_STYLE_JA

    def _role_style_ja_support():
        return style_profile_mod.resolve_role_style(style_profile, style_profile_mod.ROLE_SUPPORT_JA, "a2", lambda _r: _role_style_ja())

    out_dir = f"{theme_out_dir}/a2"
    narration_dir = f"{out_dir}/narration"
    os.makedirs(narration_dir, exist_ok=True)
    chunk_plans = _record_chunk_decision(out_dir, "a2")       # 課金前: 適用表・plan・role解決・保存済みplanとの一致を確認(違反はSTOP)。Stdもchunk対象(2026-10-26ユーザー正式承認)
    parts = load_json(f"{out_dir}/parts.json")
    support = load_json(f"{out_dir}/support_texts.json")
    kp_path = f"{out_dir}/key_phrases/keywords_canonicalized.json"
    kp = load_json(kp_path) if os.path.exists(kp_path) else None
    shared_raw = ({} if xr._ONLY_SEGMENTS is not None else shared_narration.ensure_all_shared_narration_a2(narration_dir, tts_backend=tts_backend))
    shared_status = xr._summarize_shared_narration(shared_raw)
    cached = chunk_tts.drop_cached_std_chunks_without_slowdown(
        _drop_stale_chunk_cache(voice_guard_cached(xr._load_cached_tts_results(out_dir)), chunk_plans), is_chunk_id=lambda k: ys.parse_y_chunk_id(k) is not None)
    results = {}

    topic_text = f"Today's topic is {parts['title']}."
    with cl.segment_context("topic_intro"):
        results["topic_intro"] = xr._generate_or_reuse(
            cached, "topic_intro", f"{narration_dir}/topic_intro.wav",
            _guarded(guard, "topic_intro", lambda: crosslevel_common.generate_english_segment_with_fallback(
                xr._pnap_supply(topic_text, n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(topic_text))),
                f"{narration_dir}/topic_intro.wav", n3_tts.first_words(parts["title"], 3), max_extra_chars=30,
                style_prefix_override=_role_style("TOPIC_INTRO"),
                enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for("topic_intro"),
                tts_backend=tts_backend)), expected_text=topic_text)
    results["topic_intro"]["canonical_text"] = topic_text

    with cl.segment_context("japanese_title"):
        results["japanese_title"] = xr._generate_or_reuse(
            cached, "japanese_title", f"{narration_dir}/japanese_title.wav",
            _guarded(guard, "japanese_title", lambda: n3_tts.generate_a2_japanese_with_reading_safety(
                japanese_title, f"{narration_dir}/japanese_title.wav", n3_tts.expected_substring_ja(japanese_title),
                max_extra_chars=30, style_prefix_override=_role_style_ja(), tts_backend=tts_backend)),
            expected_text=japanese_title)

    for name in ys.support_names("a2"):      # Comment 4は無い(YL-C09)。Standardはcomment_2を維持(日本語側は現状維持)。J2(範囲値正規化)=中核数値v4はY対象外(YL-B05)
        text = support[name]
        with cl.segment_context(name):
            results[name] = xr._generate_or_reuse(
                cached, name, f"{narration_dir}/{name}.wav",
                _guarded(guard, name, lambda text=text, name=name: n3_tts.generate_a2_japanese_with_reading_safety(
                    text, f"{narration_dir}/{name}.wav", n3_tts.expected_substring_ja(text),
                    style_prefix_override=_role_style_ja_support(), tts_backend=tts_backend)), expected_text=text)
        if not validation_inheritance.is_untouched_entry(results[name]):
            style_profile_mod.attach_segment_profile_record(results[name], style_profile, style_profile_mod.ROLE_SUPPORT_JA, _role_style_ja_support())

    vmap = segment_voice_map()
    for name in ys.Y_SEGMENT_IDS:
        text = parts["segments"][name]
        voice = vmap[name]
        if chunk_plans[name]["chunked"]:       # 段落が2つ以上のsegment: 段落単位chunk+chunkごとの6%減速(親集約entryはループ後に常に書く)。1段落=下の従来経路(1 call)
            with _only_includes_chunks(chunk_plans):
                _generate_y_body_segment_chunked_a2(chunk_plans[name], cached, narration_dir, results, voice, _role_style_slower, style_profile, tts_backend, guard)
            continue
        tts_input = xr._pnap_supply(text, n3_tts.tts_safe_news_en(text))
        sub = n3_tts.first_words(text)
        with cl.segment_context(name):
            def _gen(tts_input=tts_input, sub=sub, name=name, voice=voice):
                with tts_voice(voice):
                    return n3_tts.generate_a2_segment_with_slowdown(
                        tts_input, f"{narration_dir}/{name}.wav", sub,
                        style_prefix_override=(_role_style_slower("FULL_STORY") or n3_tts.A2_ENGLISH_STYLE_PREFIX_SLOWER),
                        disfluency_qa=False,
                        enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(name),
                        enable_repetition_qa=True, tts_backend=tts_backend)
            results[name] = xr._generate_or_reuse(cached, name, f"{narration_dir}/{name}.wav", _guarded(guard, name, _gen), expected_text=text)
        results[name]["canonical_text"] = text
        results[name]["y_tts_voice_requested"] = voice
        results[name]["y_role"] = "voice" if name in ys.Y_VOICE_IDS else "narrator"
        if not validation_inheritance.is_untouched_entry(results[name]):
            style_profile_mod.attach_segment_profile_record(results[name], style_profile, "FULL_STORY", _role_style_slower("FULL_STORY"))

    refresh_y_chunk_parents(out_dir, parts, results, chunk_plans, "a2")     # chunk親集約entry(失敗・未生成でも常に書く)+親wav(減速後chunkの生連結+0.2秒)+減速集約
    if any(pl.get("chunked") for pl in chunk_plans.values()):              # Std chunk TTSのruntime evidence
        save_json(f"{out_dir}/audit/chunk_tts_evidence_a2.json",
                  {"planner_version": chunk_tts.CHUNK_PLANNER_VERSION, "family": ys.FAMILY, "level": "a2", "composition": chunk_tts.STD_SLOWDOWN_COMPOSITION,
                   "style_profile": style_profile, "tts_backend": tts_backend,
                   "parents": {sid: chunk_tts.evidence_record(pl, results) for sid, pl in chunk_plans.items() if pl.get("chunked")}})

    kp_results = xr._generate_key_phrase_segments_a2(kp, narration_dir, cached, tts_backend=tts_backend, style_profile=style_profile) if kp is not None else {}
    kp_status_str = "OK" if kp is not None else "KP_SCAFFOLD_JSON_MISSING"
    return _finish_results(out_dir, results, kp_results, None, shared_status, kp_status_str, level="a2", tts_backend=tts_backend)


def _finish_results(out_dir, results, kp_results, kp_bundle, shared_status, kp_status_str, *, level, tts_backend):
    all_status = {k: v.get("status") for k, v in results.items()}
    if level == "b1b":
        kp_status = {r: {"en": v["english"].get("status"), "explanation": v["explanation"].get("status")} for r, v in kp_results.items()}
    else:
        kp_status = {r: {"en": v["english"].get("status"), "ja": v["japanese_meaning"].get("status")} for r, v in kp_results.items()}
    review_lock.archive_prior_tts_results(f"{out_dir}/audit/tts_generation_results.json")
    doc = {"segments": results, "key_phrases": kp_results, "shared_narration": shared_status, "kp_scaffold_status": kp_status_str,
           "tts_backend": tts_backend, "style_version": xr.FAMILY_X_VARIABLE_ROLE_STYLE_VERSION, "family": ys.FAMILY,
           **({"only_segments": sorted(xr._ONLY_SEGMENTS)} if xr._ONLY_SEGMENTS is not None else {})}
    if level == "b1b":
        doc["key_phrase_explanations_text"] = kp_bundle
    save_json(f"{out_dir}/audit/tts_generation_results.json", doc)
    pww_registry.write_listening_list_safe(out_dir)
    summary = {"segment_status": all_status, "key_phrase_status": kp_status,
               "shared_narration_status": {k: v["status"] for k, v in shared_status.items()},
               "kp_scaffold_status": kp_status_str, "tts_backend": tts_backend, "family": ys.FAMILY}
    save_json(f"{out_dir}/run_summary_tts.json", summary)
    xr._assert_shared_narration_ok(shared_status, level)      # 監査記録の保存後にSTOP(記録は必ず残す)
    return summary


# ============================================================
# Gate: Y style gate(Xの Assembly前M3 Gate を継承し、Y本文8segmentにも同じ判定を掛ける)+ Std減速の必須確認
# ============================================================
_X_ONLY_SEGMENTS = ("full_story_part1", "full_story_part2", "full_story_part3", "comment_4", "in_one_line")


def check_std_slowdown(results: dict, plans: dict | None = None) -> list:
    """Std(a2): Y本文8segment全てでslowdown_applied=Trueを要求(共有A2_SLOWDOWN_TARGET_SEGMENTSはYのIDを知らないためY独自に確認。YL-A02)。
    chunk化したsegmentは『親ではなく全chunk』を検査する(CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01: 親の集約値だけで通さない=chunk2以降の減速欠落を見逃さない)。
    plans=None(chunk planなし)は従来の親検査のまま。"""
    bad = []
    segs = results.get("segments") or {}
    for sid in ys.Y_SEGMENT_IDS:
        pl = (plans or {}).get(sid)
        if pl and pl.get("chunked"):
            bad += chunk_tts.std_chunk_slowdown_violations(pl, segs)
            continue
        e = segs.get(sid) or {}
        if e.get("slowdown_applied") is not True:
            bad.append({"segment": sid, "violations": ["Y_MISSING_MANDATORY_A2_SLOWDOWN"]})
    return bad


def name_not_approved(approvals, name, entry) -> bool:
    return not (entry is not None and style_profile_mod._approved(approvals, name, entry))


def y_style_gate(theme_out_dir: str, level: str, style_profile: str) -> dict:
    """XのM3 Assembly前Gate(style_profile_mod.m3_assembly_gate)を呼び、X専用segment(full_story_part*/comment_4/in_one_line)の『記録なし』だけを除外して、
    Y本文8segmentにも同じ判定(Style/fallback/Local Rewrite)を掛ける。それ以外は一切緩和しない。"""
    sp = style_profile_mod
    out_dir = f"{theme_out_dir}/{level}"
    results = load_json(f"{out_dir}/audit/tts_generation_results.json")
    approvals_path = asm.human_approval_path(out_dir)
    approvals = load_json(approvals_path) if os.path.exists(approvals_path) else {}
    gate = sp.m3_assembly_gate(style_profile, level, results, approvals)
    blocked = [b for b in gate["blocked"] if not (b["segment"] in _X_ONLY_SEGMENTS and b["violations"] == ["NO_SEGMENT_RECORD"])]
    extra = []
    segs = results.get("segments") or {}
    prof = sp.get_profile(style_profile)["overrides"].get("FULL_STORY")
    exp_text = prof["text"] if prof else None
    plans = plan_y_chunks(load_json(f"{out_dir}/parts.json")) if level in ys.CHUNK_TTS_Y_LEVELS and os.path.exists(f"{out_dir}/parts.json") else {}
    targets = []
    for sid in ys.Y_SEGMENT_IDS:     # chunk化したsegmentは『親ではなく全chunk』を検査する(親にはstyle記録が無く、chunk1の値を親へ写すとchunk2以降の違反が通るため)
        pl = plans.get(sid)
        targets += chunk_tts.chunk_ids(pl) if pl and pl.get("chunked") else [sid]
    for name in targets:
        entry = segs.get(name)
        viol = []
        if entry is None:
            viol.append("NO_SEGMENT_RECORD")
        else:
            if prof is not None:
                ev = sp.evaluate_segment_evidence(entry, level, style_profile, "FULL_STORY")
                viol.extend(ev["reasons"])
                if level == "b1b":
                    spx = entry.get("style_prefix")
                    if not (isinstance(spx, str) and spx.startswith(exp_text)):
                        viol.append("ADV_STYLE_PREFIX_NOT_PROFILE_PREFIXED")
                    if entry.get("instruction_type") == "minimal_fallback":
                        viol.append("ADV_MINIMAL_FALLBACK")
            if level == "a2" and entry.get("fallback_used") is not False:
                viol.append("STD_FALLBACK_USED_OR_UNKNOWN")
            if entry.get("local_rewrite_recovery"):
                viol.append("LOCAL_REWRITE_RECOVERY")
        extra.append({"segment": name, "violations": viol})
    extra_blocked = [e for e in extra if e["violations"] and name_not_approved(approvals, e["segment"], segs.get(e["segment"]))]
    if level == "a2":
        extra_blocked += check_std_slowdown(results, plans)
    res = {"status": "BLOCK" if (blocked or extra_blocked) else "PASS", "x_gate_blocked_after_filter": blocked,
           "y_body_checks": extra, "y_body_blocked": extra_blocked,
           "x_gate": {k: gate.get(k) for k in ("status", "checked", "human_approved", "warnings")}}
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    save_json(f"{out_dir}/audit/y_style_profile_gate.json", res)
    return res


# ============================================================
# 組立
# ============================================================
def _read(narration_dir, name):
    mono, sr, _, _ = xr.common.read_wav_float(f"{narration_dir}/{name}.wav")
    assert sr == xr.common.SAMPLE_RATE
    return mono


def _load_y_body_chunks(out_dir: str) -> tuple:
    """chunk化したsegmentについて、音声を読む前に整合検査(chunk集合・順序・語数・版・本文)と『親wav==ディスク上のchunk wavの生連結』
    (整数サンプル完全一致)を確認し、chunk別monoを返す(共通er117の関数。X組立と同じ手順)。戻り値=(body_chunks, plans_used)。"""
    nd = f"{out_dir}/narration"
    parts_json = load_json(f"{out_dir}/parts.json")
    plans = plan_y_chunks(parts_json)
    rp = f"{out_dir}/audit/tts_generation_results.json"
    segs = (load_json(rp).get("segments") or {}) if os.path.exists(rp) else {}
    body_chunks, used = {}, {}
    for sid, plan in plans.items():
        text = parts_json["segments"][sid]
        ids = chunk_tts.chunk_ids(plan)
        try:
            chunk_tts.verify_parent_integrity(plan, text, {i: segs[i] for i in ids if i in segs}, segs.get(sid))
            if not plan.get("chunked"):
                continue
            paths = [f"{nd}/{i}.wav" for i in ids]
            chunk_tts.verify_raw_parent(f"{nd}/{sid}.wav", paths)
        except chunk_tts.ChunkIntegrityError as exc:
            raise YAudioStop(f"FAMILY_Y_CHUNK_INTEGRITY({sid}): {exc}") from exc
        monos = []
        for pth in paths:
            m_, sr_, _, _ = xr.common.read_wav_float(pth)
            assert sr_ == xr.common.SAMPLE_RATE
            monos.append(m_)
        body_chunks[sid] = monos
        used[sid] = plan
    return body_chunks, used


def load_y_sources(theme_out_dir: str, level: str, article_text: str | None = None) -> dict:
    out_dir = f"{theme_out_dir}/{level}"
    nd = f"{out_dir}/narration"
    p9a = xr.p9a
    asm.verify_episode_audio_validation_gate(out_dir, "B1" if level == "b1b" else "A2", article_text=article_text)
    kp = load_json(f"{out_dir}/key_phrases/keywords_canonicalized.json")
    items = sorted(kp["items"], key=lambda it: it["rank"])
    common_in = {"intro": p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH),
                 "notification": p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH),
                 "outro": p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH), "kp_items": items}
    nums = ("num_one", "num_two", "num_three", "num_four", "num_five")
    if level == "b1b":
        narration = {n: _read(nd, f"{n}_charon") for n in ("welcome", "preview_intro", "key_phrases_intro", "full_story_intro", *nums)}
        narration["topic_intro"] = _read(nd, "topic_intro")
        segs = {n: _read(nd, n) for n in (*ys.Y_SEGMENT_IDS, *ys.body_comment_names("b1b"), "preview")}
        segs["full_story_part1"] = segs[ys.Y_LEAD]       # 共通gain関数のRMSアンカー用alias(gain後に除去する。出力には残さない)
        comp = {it["rank"]: _read(nd, f"kp{it['rank']}_en") for it in items}
        mean = {it["rank"]: _read(nd, f"kp{it['rank']}_explanation_en") for it in items}
        body_chunks, chunk_plan_used = _load_y_body_chunks(out_dir)
        return {**common_in, "narration": narration, "b1_segments": segs, "key_phrase_components": comp, "key_phrase_meanings": mean,
                "body_chunks": body_chunks, "chunk_plans": chunk_plan_used}
    preview_mono = _read(nd, "preview")
    narration = {n: _read(nd, n) for n in ("welcome", "preview_intro", "key_phrases_intro", "full_story_intro", *nums, "topic_intro", "japanese_title")}
    comp = {}
    for i, it in enumerate(items, start=1):
        comp[it["rank"]] = _read(nd, f"kp{it['rank']}_en")
        narration[f"meaning_{i}"] = _read(nd, f"meaning_{i}")
    segs = {n: _read(nd, n) for n in (*ys.Y_SEGMENT_IDS, *ys.body_comment_names("a2"))}
    segs["full_story_part1"] = segs[ys.Y_LEAD]
    body_chunks, chunk_plan_used = _load_y_body_chunks(out_dir)    # Std chunk(2026-10-26ユーザー正式承認): Advと同じ整合検査+親wav生連結検証
    return {**common_in, "preview_mono": preview_mono, "narration": narration, "key_phrase_components": comp, "a2_segments": segs,
            "body_chunks": body_chunks, "chunk_plans": chunk_plan_used}


def apply_y_gain(sources: dict, level: str) -> dict:
    """共通gain関数(xr.apply_family_x_b1_gain / _a2_gain)を呼び、RMSアンカー用aliasをgain後に除去する(YのIDで再実装しない)。"""
    if level == "b1b":
        parts = xr.apply_family_x_b1_gain(sources)
        parts["b1_segments"].pop("full_story_part1", None)
        parts["gain_report"].pop("b1_full_story_part1", None)
    else:
        parts = xr.apply_family_x_a2_gain(sources)
        parts["a2_segments"].pop("full_story_part1", None)
        parts["gain_report"].pop("a2_full_story_part1", None)
    return parts


def _body_seq(seg: dict, comment_to_story_gap: float, story_to_comment_gap: float, level: str) -> list:
    """Y本文の再生順(Intro→…→Full story intro の後):
    Advanced(b1b)=Comment1→Lead→[紹介1→Voice1]→[紹介2→Voice2]→[紹介3→Voice3]→Comment3→Closing(Comment 2は削除。2026-10-26ユーザー承認)。
    Standard(a2)=Comment1→Lead→Comment2→[紹介1→Voice1]→…→Comment3→Closing(現状維持)。
    ナレーター↔Voice切替のpauseはXの語り手切替値(CHARON_TO_AOEDE_PAUSE_SECONDS)を再利用(Y固有の新値なし)。"""
    S = xr.p9a.silence_stereo
    gap = asm.CHARON_TO_AOEDE_PAUSE_SECONDS
    seq = [("Comment 1", seg["comment_1"]), ("pause_comment_to_story", S(comment_to_story_gap)),
           (ys.PAGE_LABEL[ys.Y_LEAD], seg[ys.Y_LEAD]), ("pause_story_to_comment", S(story_to_comment_gap))]
    if "comment_2" in ys.body_comment_names(level):
        seq += [("Comment 2", seg["comment_2"]), ("pause_comment_to_story", S(comment_to_story_gap))]
    for i in (1, 2, 3):
        seq += [(ys.PAGE_LABEL[f"y_intro_{i}"], seg[f"y_intro_{i}"]), ("pause_intro_to_voice", S(gap)),
                (ys.PAGE_LABEL[f"y_voice_{i}"], seg[f"y_voice_{i}"])]
        seq.append(("pause_voice_gap", S(gap)) if i < 3 else ("pause_story_to_comment", S(story_to_comment_gap)))
    seq += [("Comment 3", seg["comment_3"]), ("pause_comment_to_story", S(comment_to_story_gap)), (ys.PAGE_LABEL[ys.Y_CLOSING], seg[ys.Y_CLOSING])]
    return seq


def build_y_timeline(level: str, parts: dict) -> list:
    S = xr.p9a.silence_stereo
    if level == "b1b":
        blocks = asm.build_b1_key_phrase_blocks(parts)
        b1 = parts["b1_segments"]
        seq = [("Intro", parts["intro"]), ("Welcome", parts["welcome"]), ("pause_0.5", S(0.5)),
               ("Topic intro", parts["topic_intro"]), ("pause_0.65", S(0.65)), ("Notification 1", parts["notification"]),
               ("pause_0.4", S(0.4)), ("Preview intro", parts["preview_intro"]), ("pause_0.65", S(0.65)),
               ("Preview", b1["preview"]), ("pause_0.5", S(0.5)), ("Notification 2", parts["notification"]),
               ("pause_0.4", S(0.4)), ("Key phrases intro", parts["key_phrases_intro"]), ("pause_0.5", S(0.5))]
        for i, block in enumerate(blocks, start=1):
            seq.append((f"Key Phrase {i}", block))
        seq += [("Notification 3", parts["notification"]), ("pause_0.4", S(0.4)), ("Full story intro", parts["full_story_intro"]),
                ("pause_1.0", S(asm.AOEDE_TO_CHARON_PAUSE_SECONDS))]
        seq += _body_seq(b1, asm.CHARON_TO_AOEDE_PAUSE_SECONDS, asm.AOEDE_TO_CHARON_PAUSE_SECONDS, "b1b")
        seq += [("pause_closing_to_outro", S(asm.IN_ONE_LINE_TO_OUTRO_PAUSE_SECONDS)), ("Outro", parts["outro"])]
        return seq
    blocks = asm.build_a2_key_phrase_blocks(parts)
    a2 = parts["a2_segments"]
    seq = [("Intro", parts["intro"]), ("Welcome", parts["welcome"]), ("pause_0.5", S(0.5)), ("Topic intro", parts["topic_intro"]),
           ("pause_0.65", S(0.65)), ("Japanese title", parts["japanese_title"]), ("pause_0.5", S(0.5)),
           ("Notification 1", parts["notification"]), ("pause_0.4", S(0.4)), ("Preview intro", parts["preview_intro"]),
           ("pause_0.65", S(0.65)), ("Preview", parts["preview"]), ("pause_0.5", S(0.5)), ("Notification 2", parts["notification"]),
           ("pause_0.4", S(0.4)), ("Key phrases intro", parts["key_phrases_intro"]), ("pause_0.5", S(0.5))]
    for i, block in enumerate(blocks, start=1):
        seq.append((f"Key Phrase {i}", block))
    seq += [("Notification 3", parts["notification"]), ("pause_0.4", S(0.4)), ("Full story intro", parts["full_story_intro"]),
            ("pause_1.0_en_to_ja", S(1.0))]
    seq += _body_seq(a2, 0.8, 1.0, "a2")
    seq += [("pause_closing_to_outro", S(0.5)), ("Outro", parts["outro"])]
    return seq


def _chunk_assembly_summary_y(plans: dict, gain_chunks: dict, timeline: list) -> dict:
    """組立のruntime evidence: 分割位置・種別・chunk数・0.2秒の実測offset(segment内/episode内)・chunk別gain/RMS/peak(cap発動を含む)。"""
    starts = {}
    label_to_sid = {v: k for k, v in ys.PAGE_LABEL.items()}
    for item in timeline:
        sid = label_to_sid.get(item.get("part", ""))
        if sid:
            starts[sid] = item["start_seconds"]
    out = {"planner_version": chunk_tts.CHUNK_PLANNER_VERSION, "extra_pause_seconds": chunk_tts.EXTRA_PAUSE_SECONDS, "family": ys.FAMILY,
           "method": ys.CHUNK_TTS_Y_METHOD, "parents": {}}
    for sid, plan in plans.items():
        rep_ = gain_chunks.get(sid) or {}
        base = starts.get(sid)
        out["parents"][sid] = {
            "chunk_ids": chunk_tts.chunk_ids(plan), "words": [c["words"] for c in plan["chunks"]],
            "boundary_kinds": [c["boundary_kind"] for c in plan["chunks"]],
            "segment_start_in_episode_s": base, "gap_offsets_in_segment_s": rep_.get("boundary_offsets_s"),
            "gap_offsets_in_episode_s": ([[round(base + a, 4), round(base + b, 4)] for a, b in rep_.get("boundary_offsets_s") or []] if base is not None else None),
            "gains": rep_.get("gains"), "pre_rms": rep_.get("pre_rms"), "post_rms": rep_.get("post_rms"),
            "peak_after": rep_.get("peak_after"), "peak_capped": rep_.get("peak_capped"), "chunk_samples": rep_.get("chunk_samples")}
    return out


def _refresh_y_chunk_parents_on_disk(out_dir: str, level: str = "b1b") -> None:
    """tts_generation_results.json上のchunk親集約entryを(再)構築して保存する(chunk化したsegmentが無ければファイルに触れない)。"""
    rp, pp = f"{out_dir}/audit/tts_generation_results.json", f"{out_dir}/parts.json"
    if not (os.path.exists(rp) and os.path.exists(pp)):
        return
    data, parts = load_json(rp), load_json(pp)
    plans = plan_y_chunks(parts)
    if not any(pl.get("chunked") for pl in plans.values()):
        return
    refresh_y_chunk_parents(out_dir, parts, data.setdefault("segments", {}), plans, level)
    save_json(rp, data)


def assemble_level(theme_out_dir: str, level: str, *, style_profile: str, slug: str, article_text: str | None = None) -> dict:
    """Y組立(Audio Validation Gate→Y style gate→gain→timeline→headroom→wav)。Gate不合格は組み立てない(BLOCKED_*。回避しない)。"""
    out_dir = f"{theme_out_dir}/{level}"
    os.makedirs(f"{out_dir}/assembled", exist_ok=True)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    if not os.path.exists(f"{out_dir}/key_phrases/keywords_canonicalized.json"):
        s = {"status": "BLOCKED_KP_SCAFFOLD_MISSING", "reason": "key_phrases/keywords_canonicalized.jsonが存在しません(上流KP Gateを回避しません)"}
        save_json(f"{out_dir}/run_summary_assemble.json", s)
        return s
    xr._assert_no_gloss_alignment_hr(out_dir, "B1" if level == "b1b" else "A2")
    shared_blocked = xr._shared_narration_gate_blocked_summary(out_dir)
    if shared_blocked is not None:
        save_json(f"{out_dir}/run_summary_assemble.json", shared_blocked)
        return shared_blocked
    if level in ys.CHUNK_TTS_Y_LEVELS:      # Style Gate・共有Gateより前に、chunk親集約entry(status・親wav・human_approved_chunks)を再構築する(人間承認後の再assembleで親も通る)
        _refresh_y_chunk_parents_on_disk(out_dir, level)
    gate = y_style_gate(theme_out_dir, level, style_profile)
    if gate["status"] != "PASS":
        s = {"status": "BLOCKED_STYLE_PROFILE_GATE", "gate": gate}
        save_json(f"{out_dir}/run_summary_assemble.json", s)
        return s
    sources = load_y_sources(theme_out_dir, level, article_text=article_text)
    parts = apply_y_gain(sources, level)
    seq = build_y_timeline(level, parts)
    result = asm.assemble_with_timeline(seq)
    headroom = asm.apply_headroom_safety_valve(result["assembled"], seq)
    assembled = headroom["assembled"]
    out_path = f"{out_dir}/assembled/Family_Y_{slug.upper()}_{'B1' if level == 'b1b' else 'A2'}.wav"
    save_json(f"{out_dir}/audit/gain_report.json", parts["gain_report"])
    save_json(f"{out_dir}/audit/timeline.json", result["timeline"])
    save_json(f"{out_dir}/audit/headroom_report.json", headroom["report"])
    xr.common.write_wav_float(out_path, assembled, xr.SR, 2)
    metrics = xr.common.measure_metrics(assembled[:, 0], xr.SR)
    summary = {"status": "OK", "out_path": out_path, "duration_seconds": result["total_duration_seconds"],
               "clipping_detected": metrics["clipping_detected"], "peak": round(xr.p9a.peak(assembled), 5),
               "sample_rate": xr.SR, "channels": 2, "headroom_safety_valve": headroom["report"], "family": ys.FAMILY}
    if sources.get("body_chunks"):
        summary["chunk_tts"] = _chunk_assembly_summary_y(sources["chunk_plans"], parts["gain_report"].get("chunk_tts") or {}, result["timeline"])
        if level == chunk_tts.STD_LEVEL:
            summary["chunk_tts"]["level"] = "a2"
            summary["chunk_tts"]["composition"] = chunk_tts.STD_SLOWDOWN_COMPOSITION
        save_json(f"{out_dir}/audit/chunk_tts_assembly_{level}.json", summary["chunk_tts"])
    xr._attach_kp_vote_audit(summary, out_dir, level)
    pnap_hooks.attach_alarm_audit(summary, out_dir, level)
    save_json(f"{out_dir}/run_summary_assemble.json", summary)
    return summary


# ============================================================
# 試聴ページ(限定共有)。共通builder(er_user_listening_page_common_01.render_standard_page)を使い、注意書きは本文外(intro_html)
# ============================================================
NOINDEX_META = "<meta name=\"robots\" content=\"noindex,nofollow\">"


# ============================================================
# 試聴ページ用: TTS分割/追加0.2秒の明示・実測停止の重畳・Voice 1候補表(表示専用。音声・Gate・採否に使わない。API 0)
# 2026-10-26 FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01 委任_03(ユーザー原文§4)。位置は台本語への推定(ASRに語時刻が無いため±2〜3語)。
# ============================================================
PAUSE_MARK_MIN_MS = 700                 # 台本上に⏸を出す下限(表示専用)
PAUSE_SCAN_DBFS, PAUSE_SCAN_MIN_MS, PAUSE_BLIP_MS = -40.0, 150, 120
PAUSE_MID_CLAUSE_MIN_MS = 500           # Voice 1候補表の『文中停止数』= 句読点外の統合後停止のうち500ms以上
_PZ_STYLE = "background:#ffe0b2;color:#a30;font-weight:bold;padding:0 3px;border-radius:3px;font-size:.9em"
_BADGE_STYLE = "display:inline-block;background:#e8f0fe;border:1px solid #9ab;border-radius:3px;padding:1px 6px;font-size:.8em;margin:2px 0"


def pause_scan(arr, sr, thr_db: float = PAUSE_SCAN_DBFS, min_ms: int = PAUSE_SCAN_MIN_MS, blip_ms: int = PAUSE_BLIP_MS) -> dict:
    """10msフレームRMS<thr_dbが min_ms 以上続く区間を列挙し、無音間の有音が blip_ms 未満なら統合した『内部停止』を返す(numpyのみ)。
    docs/research/FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01/tools/yfb_silence_scan_01.py+yfb_pause_stats_01.py と同じ手順(測定値の同一性はtestで固定)。"""
    import numpy as np
    x = np.asarray(arr, dtype="float64")
    if x.ndim > 1:
        x = x.mean(axis=1)
    f = int(sr * 10 / 1000)
    nf = len(x) // f
    if nf == 0:
        return {"duration_s": 0.0, "lead_ms": 0, "trail_ms": 0, "pauses": []}
    fr = x[: nf * f].reshape(nf, f)
    db = 20 * np.log10(np.sqrt((fr ** 2).mean(axis=1) + 1e-20) + 1e-12)
    sil = db < thr_db
    runs, i = [], 0
    while i < nf:
        if sil[i]:
            j = i
            while j < nf and sil[j]:
                j += 1
            if (j - i) * 10 >= min_ms:
                runs.append({"start_s": round(i * 10 / 1000, 3), "end_s": round(j * 10 / 1000, 3), "dur_ms": (j - i) * 10})
            i = j
        else:
            i += 1
    tot = nf * 10 / 1000
    lead = runs[0]["dur_ms"] if runs and runs[0]["start_s"] < 0.05 else 0
    trail = runs[-1]["dur_ms"] if runs and runs[-1]["end_s"] >= tot - 0.05 else 0
    inner = [r for r in runs if r["start_s"] >= 0.05 and r["end_s"] < tot - 0.05]
    merged = []
    for p_ in inner:
        if merged and (p_["start_s"] - merged[-1]["end_s"]) * 1000 < blip_ms:
            merged[-1]["end_s"] = p_["end_s"]
            merged[-1]["dur_ms"] = round((merged[-1]["end_s"] - merged[-1]["start_s"]) * 1000)
        else:
            merged.append(dict(p_))
    return {"duration_s": tot, "lead_ms": lead, "trail_ms": trail, "pauses": merged}


def pause_align(scan: dict, text: str) -> list:
    """統合後の停止を台本の語境界へ単調DPで概算対応付け(句読点直後を優先)。精度は±2〜3語。各要素に word_index/after_word/before_word/at_punctuation を足して返す。"""
    m = scan["pauses"]
    words = (text or "").split()
    if not m or len(words) < 2:
        return [dict(p_, word_index=None, after_word="", before_word="", at_punctuation=False) for p_ in m]
    wt = [len(re.sub(r"\W", "", w)) + 2 for w in words]
    W = sum(wt)
    act = scan["duration_s"] - scan["lead_ms"] / 1000 - scan["trail_ms"] / 1000 - sum(p_["dur_ms"] for p_ in m) / 1000
    cum = [sum(wt[: i + 1]) for i in range(len(words))]
    cand = list(range(1, len(words)))
    punct = {k for k in cand if re.search(r"[.?!,;:]$", words[k - 1])}
    est, acc = [], 0.0
    for p_ in m:
        sp = p_["start_s"] - scan["lead_ms"] / 1000 - acc
        acc += p_["dur_ms"] / 1000
        est.append(W * sp / act if act > 0 else 0)

    def cost(i, k):
        return abs(cum[k - 1] - est[i]) / 3.0 * 0.5 + (0 if k in punct else 3)
    n, INF = len(m), 1e18
    dp = [[INF] * (len(cand) + 1) for _ in range(n + 1)]
    bp = [[0] * (len(cand) + 1) for _ in range(n + 1)]
    dp[0] = [0.0] * (len(cand) + 1)
    for i in range(1, n + 1):
        best, bj = INF, 0
        for j in range(1, len(cand) + 1):
            if dp[i - 1][j - 1] < best:
                best, bj = dp[i - 1][j - 1], j - 1
            dp[i][j] = best + cost(i - 1, cand[j - 1])
            bp[i][j] = bj
    j = min(range(1, len(cand) + 1), key=lambda t: dp[n][t])
    out = []
    for i in range(n, 0, -1):
        k = cand[j - 1]
        out.append(dict(m[i - 1], word_index=k, after_word=words[k - 1], before_word=words[k], at_punctuation=(k in punct)))
        j = bp[i][j]
    out.reverse()
    return out


def pause_stats(arr, sr, text: str) -> dict:
    """Voice 1候補表の停止統計(1秒以上停止数・停止占有率・文中停止数・最長停止)。"""
    sc = pause_scan(arr, sr)
    al = pause_align(sc, text)
    tot = sc["duration_s"]
    return {"duration_s": round(tot, 2), "pauses_total": len(al), "ge1000": sum(1 for p_ in al if p_["dur_ms"] >= 1000),
            "ge700": sum(1 for p_ in al if p_["dur_ms"] >= 700),
            "mid_clause_ge500": sum(1 for p_ in al if not p_["at_punctuation"] and p_["dur_ms"] >= PAUSE_MID_CLAUSE_MIN_MS),
            "max_ms": max([p_["dur_ms"] for p_ in al], default=0),
            "pause_ratio_pct": round(100 * sum(p_["dur_ms"] for p_ in al) / 1000 / tot, 1) if tot else 0.0}


def _mmss(sec: float) -> str:
    return f"{int(sec // 60)}:{sec % 60:04.1f}"


def _script_with_pauses(text: str, marks: list) -> str:
    """台本1ブロック。実測した長い停止(>=PAUSE_MARK_MIN_MS)を該当語の直後に ⏸(長さ@行内の秒)で重ねる。marksは pause_align の結果。"""
    import html
    toks = re.split(r"(\s+)", text or "")
    wpos = {}
    for i, t in enumerate(toks):
        if t and not t.isspace():
            wpos[i] = len(wpos)
    after = {}
    for p_ in marks:
        k = p_.get("word_index")
        if k is not None and p_["dur_ms"] >= PAUSE_MARK_MIN_MS:
            after.setdefault(k - 1, []).append(p_)
    out = []
    for i, t in enumerate(toks):
        out.append(html.escape(t))
        for p_ in after.get(wpos.get(i), []):
            out.append(f" <span style=\"{_PZ_STYLE}\" title=\"実測の停止(位置は推定)\">&#9208;{p_['dur_ms'] / 1000:.2f}s@{_mmss(p_['start_s'])}</span>")
    return "<div class='script'>" + "".join(out) + "</div>"


def _tts_unit_badge(level: str, decision: dict, sid: str) -> str:
    """R1: segmentごとのTTS生成単位バッジ。分割の有無は chunk_tts_decision.json(実際の判定)から読む。"""
    import html
    seg = ((decision or {}).get("segments") or {}).get(sid) or {}
    if not seg and level == "a2" and not (decision or {}).get("chunk_tts_applied_at_this_level"):
        # 2026-10-26以前に生成されたStandardの判定記録(当時Standardは分割対象外だった旧記録)。現行はStd/Adv双方が段落境界分割の対象。
        txt = "TTS 1回 / 分割なし(旧記録: この生成時点ではStandardは分割対象外) / 追加0.2秒ポーズ: なし"
    elif seg.get("chunked"):
        n = len(seg.get("chunk_ids") or [])
        txt = f"TTS {n}分割(段落境界) / 追加0.2秒ポーズ: あり(境界ごと)"
    else:
        txt = f"TTS 1回 / 分割なし(段落={seg.get('paragraphs', '?')}) / 追加0.2秒ポーズ: なし"
    return f"<div><span style=\"{_BADGE_STYLE}\">{html.escape(txt)}</span></div>"


def page_legend_html(decisions: dict) -> str:
    """ページ冒頭の凡例1ブロック(本文外)。実分割の有無はchunk_tts_decision.json(level別)から集計して明示する。"""
    n_chunked = sum(1 for d in decisions.values() for sg in ((d or {}).get("segments") or {}).values() if sg.get("chunked"))
    split_txt = "なし(全segmentが1段落のため、各segmentを1回のTTSで生成)" if n_chunked == 0 else f"{n_chunked} segmentで分割"
    zero = "なし" if n_chunked == 0 else "分割境界のみあり"
    return ("<div class='note'><b>この試聴ページの見方</b><br>"
            f"TTSの実分割: <b>{split_txt}</b> / 追加0.2秒ポーズ: <b>{zero}</b>(StandardもAdvancedと同じ段落境界分割の対象。段落が1つのsegmentは分割しません)。"
            "台本の見た目の段落とTTSの実分割は別のものです。<br>"
            f"<span style=\"{_PZ_STYLE}\">&#9208;1.25s@0:13.7</span> = 完成音声を実測した{PAUSE_MARK_MIN_MS}ms以上の停止(長さ@その行の音声内の時刻)。"
            "台本上の位置は語への割当てで<b>推定(前後2〜3語の誤差)</b>です。聴いて不自然に感じた時刻と見比べてください。"
            "&#9660;(TTS実分割位置)の表示は、分割があるsegmentでのみ出ます(今回はありません)。</div>")


def voice1_candidates_aux_html(theme_out_dir: str, audio_dir: str, audio_rel: str) -> str:
    """Voice 1の個別再生: 現行採用+候補(hr_adopt_prep/voice1_candidates/take*/、未採用)を並べ、停止統計を併記する。候補が無ければ空文字。
    候補はユーザーの試聴選択前=『候補・未採用』。採用は別手続き(approved_by="user"はユーザーのみ)。Std候補で減速未適用のもの(STOPPED=人間確認待ちのraw attempt)は、採用時と同じ6%減速(API 0)を適用した音で提示・計測する。"""
    import html
    import tempfile
    import imageio_ffmpeg
    import soundfile as sf
    import subprocess
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    blocks = []
    for level, label in (("a2", "Standard"), ("b1b", "Advanced")):
        base = f"{theme_out_dir}/{level}"
        takes = sorted(glob.glob(f"{base}/hr_adopt_prep/voice1_candidates/take*/result.json"))
        if not takes:
            continue
        text = load_json(f"{base}/parts.json")["segments"]["y_voice_1"]
        cur_wav = f"{base}/narration/y_voice_1.wav"
        items = [("現行(採用済み)", cur_wav, "採用済み", None)]
        for tp in takes:
            r = load_json(tp)
            wav = r.get("wav")
            if not wav or not os.path.exists(wav):
                continue
            note = {"OK": "ASR判定PASS(正式経路で完走)", "STOPPED": "ASR判定NG→人間確認待ち扱い(正式経路の停止状態。聴いて選ぶ候補)"}.get(r.get("status"), str(r.get("status")))
            items.append((f"候補{r['take']}(未採用)", wav, note, r))
        rows = []
        for idx, (name, wav, note, r) in enumerate(items):
            src = wav
            tmp_dir = None
            if level == "a2" and r is not None and r.get("status") != "OK":
                import er008_a2_postprocess_slowdown_01 as slow
                tmp_dir = tempfile.mkdtemp()
                src = os.path.join(tmp_dir, "slowed.wav")
                slow.apply_a2_slowdown(wav, src)
                note += " / 6%減速適用後の音を提示"
            x, sr = sf.read(src, dtype="float32")
            fn = f"v1cand_{level}_{idx}.mp3"
            tmp = os.path.join(audio_dir, fn + ".tmp.wav")
            sf.write(tmp, x, sr)
            subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-i", tmp, "-codec:a", "libmp3lame", "-b:a", "96k", os.path.join(audio_dir, fn)], check=True)
            os.remove(tmp)
            st_ = pause_stats(x, sr, text)
            rows.append(f"<div style='border:1px solid #ccc;padding:6px;margin:4px 0'><b>{html.escape(name)}</b> <span class='sec'>{html.escape(note)}</span><br>"
                        f"<audio controls preload='none' src='{html.escape(audio_rel)}/{fn}'></audio><br>"
                        f"<span class='sec'>実測の停止(参考): {st_['duration_s']:.1f}秒 / 1秒以上の停止 <b>{st_['ge1000']}</b> / 停止占有率 <b>{st_['pause_ratio_pct']}%</b> / "
                        f"文中停止(500ms以上) <b>{st_['mid_clause_ge500']}</b> / 最長 <b>{st_['max_ms'] / 1000:.2f}秒</b></span></div>")
        blocks.append(f"<h4>{label} Voice 1</h4>" + "".join(rows))      # table/h2を使わない(標準適合checkのレベル節の行判定に触れない)
    if not blocks:
        return ""
    return ("<details class='aux' open><summary><b>Voice 1の聴き比べ(候補・未採用)</b></summary>"
            "<p class='sec'>現行の採用音声と、同じ設定(同じVoice・同じ本文)で取り直した候補です。<b>候補はすべて未採用</b>で、聴いて選ぶまで本編は変わりません。"
            "停止の数値は完成音声の実測(参考。品質の合否判定には使いません)。</p>" + "".join(blocks) + "</details>")


def _script(text):
    import er_user_listening_page_common_01 as cp
    return cp.script_block(text or "")


def build_page_rows(theme_out_dir: str, level: str, audio_dir: str, audio_rel: str, ja_paragraphs: list | None = None) -> dict:
    """assembled wav+timeline から、再生順の全スクリプト表の行を作る(mp3化込み)。行ラベルに内部ID・Voice名を出さない。"""
    import imageio_ffmpeg
    import soundfile as sf
    import subprocess
    import er_user_listening_page_common_01 as cp
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    base = f"{theme_out_dir}/{level}"
    wavs = sorted(glob.glob(f"{base}/assembled/*.wav"))
    if len(wavs) != 1:
        raise YAudioStop(f"FAMILY_Y_PAGE_ASSEMBLED_WAV: {level}の組立済み全編wavが1つではありません({wavs})。Gateを回避して通し音声は作りません")
    x, sr = sf.read(wavs[0], dtype="float32")

    def mp3(arr, out, br="96k"):
        tmp = out + ".tmp.wav"
        sf.write(tmp, arr, sr)
        subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-i", tmp, "-codec:a", "libmp3lame", "-b:a", br, out], check=True)
        os.remove(tmp)
    os.makedirs(audio_dir, exist_ok=True)
    tag = "adv" if level == "b1b" else "std"
    full = f"{tag}_full.mp3"
    mp3(x, f"{audio_dir}/{full}", br="128k")
    tl = load_json(f"{base}/audit/timeline.json")
    parts = load_json(f"{base}/parts.json")
    res = load_json(f"{base}/audit/tts_generation_results.json")
    support = load_json(f"{base}/support_texts.json")
    kp_items = sorted(load_json(f"{base}/key_phrases/keywords_canonicalized.json")["items"], key=lambda it: it["rank"])
    expl = res.get("key_phrase_explanations_text") or {}
    label_to_sid = {v: k for k, v in ys.PAGE_LABEL.items()}
    dec_path = f"{base}/audit/chunk_tts_decision.json"
    decision = load_json(dec_path) if os.path.exists(dec_path) else {}
    rows = []
    for e in tl:
        part = e["part"]
        if part.startswith("pause"):
            continue
        s0, dur = e["start_seconds"], e["duration_seconds"]
        fn = f"{tag}_{len(rows):02d}.mp3"
        mp3(x[int(round(s0 * sr)): int(round((s0 + dur) * sr))], f"{audio_dir}/{fn}")
        blocks, pl = [], part.lower()
        if part in label_to_sid:
            sid = label_to_sid[part]
            blocks.append(_tts_unit_badge(level, decision, sid))                  # R1: TTS生成単位(分割の有無・追加0.2秒の有無)
            row_arr = x[int(round(s0 * sr)): int(round((s0 + dur) * sr))]
            blocks.append(_script_with_pauses(parts["segments"][sid], pause_align(pause_scan(row_arr, sr), parts["segments"][sid])))   # R4: 実測停止を台本へ重畳(推定位置)
            if ja_paragraphs is not None:
                blocks.append("<details><summary>日本語の元原稿</summary><div class='ja'>" + cp.esc(ja_paragraphs.get(sid, "")) + "</div></details>")
        elif pl.startswith("topic intro"):
            blocks.append(_script(res["segments"]["topic_intro"].get("canonical_text")))
        elif pl.startswith("japanese title"):
            blocks.append(_script(res["segments"]["japanese_title"].get("canonical_text") or res["segments"]["japanese_title"].get("text")))
        elif pl == "preview":
            blocks.append(_script(support["preview"]))
        elif re.match(r"comment (\d)$", pl):
            blocks.append(_script(support["comment_" + re.match(r"comment (\d)$", pl).group(1)]))
        elif re.match(r"key phrase (\d)$", pl):
            r = int(re.match(r"key phrase (\d)$", pl).group(1))
            it = kp_items[r - 1]
            k = res["key_phrases"][str(it["rank"])]
            if level == "a2":
                ja = k["japanese_meaning"].get("canonical_text") or it.get("japanese_gloss") or ""
                blocks.append(cp.kp_block(["英語", "日本語の意味"], [it["used_form"], ja]))
            else:
                ex = (expl.get("items") or {})
                row = ex.get(str(it["rank"])) or ex.get(it["rank"]) or {}
                blocks.append(cp.kp_block(["Key Phrase", "英語での解説"], [it["used_form"], k["explanation"].get("explanation_text") or row.get("english_explanation") or ""]))
        else:
            blocks.append("<span class='sec'>(定型音声)</span>")
        rows.append({"part": part, "start": s0, "dur": dur, "src": f"{audio_rel}/{fn}", "blocks": blocks})
    return {"id": "advanced" if level == "b1b" else "standard", "label": "Advanced" if level == "b1b" else "Standard", "chunk_decision": decision,
            "full_src": f"{audio_rel}/{full}", "duration": x.shape[0] / sr, "rows": rows}


def render_y_page(title: str, levels: list, aux_html: str = "") -> str:
    """限定共有ページ(noindex)。注意書きは本文外(冒頭のintro_html)。X/Zページには出さない(共通builderの既定は不変)。"""
    import er_user_listening_page_common_01 as cp
    legend = page_legend_html({lv["id"]: lv.get("chunk_decision") for lv in levels})
    html_text = cp.render_standard_page(title, levels, intro_html=ys.notice_html() + legend, aux_html=aux_html)
    return html_text.replace("<meta charset='utf-8'>", "<meta charset='utf-8'>" + NOINDEX_META, 1)
