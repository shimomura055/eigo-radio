"""LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 委任_10(Phase B / B3準備): 表示本文overlay・三者一致Gate・公開ページ混入検知(未配線の純module)。

目的(ユーザー正式決定UD-1、`docs/pm/delegation_log/2026-10-28_LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01_USER.md` §2/§3/§10-9):
  LR後の英文を公開ページの表示本文にも反映する(表示本文=TTS入力=ASR正解)。LR/Fallbackの注記は公開ページ・TTS入力・ASR正解・Style Promptへ混入させない。
  設計=INTEGRATION_01 §1/F-1/F-5/F-9、OPUS_REVIEW_01 (b)-5/(b)-8/M-7、W2 §3/§5。

性質(厳守):
  - 純関数・読取専用・API 0・LLMなし。ファイルを書かない。run dirは書き換えない。
  - **未配線**: どのProductionコードからもimportされない(Fable指示=既存module無編集。配線は`patches/B3_wiring_01.patch`を統合配線commitで適用)。
  - 台帳導出・位置特定・overlay適用・三者一致照合は`er129_lr_display_reflection_01`の実装を再利用する(規則の二重化なし)。er129は遅延importする
    (公開ページ検査`public_leak_hits`だけを使う呼出元に、er020/er128の重いimportを強いない)。
  - 台帳が空(LR 0)ならoverlayは入力をそのまま返す(同一object=byte同一)。
  - 位置特定不能・曖昧・STOP判定のclipは黙って原文表示にせず例外(fail-closed)。
"""
from __future__ import annotations

import os
import re
from typing import Any

MANAGEMENT_ID = "LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01"

STATUS_DISPLAY_CONSISTENCY = "BLOCKED_LR_DISPLAY_CONSISTENCY"                 # X/Yのassemble summary status(W2 §5-2)
STATUS_CONFIRMED_INTERFERENCE = "BLOCKED_LR_CONFIRMED_CONTENT_INTERFERENCE"   # T1/T2/T3(確定内容との重なり)

ENTRY_SOURCE = "entry.canonical_text"


def _e129():
    import er129_lr_display_reflection_01 as e129
    return e129


# ----------------------------------------------------------------------------- 例外
class LRDisplayConsistencyStop(RuntimeError):
    """表示本文とTTS入力/ASR正解の不一致・位置特定不能・overlay未適用(=本文と音声の不一致の技術STOP)。HRキューへ入れない。
    属性: status(STATUS_*)・problems(原因list)・family。Z側は`stop_cls=FamilyZLRDisplayConsistencyStop`(FamilyZAudioStop系列)を渡して同形で上げる。"""
    status = STATUS_DISPLAY_CONSISTENCY

    def __init__(self, message: str, problems: list | None = None, status: str | None = None):
        super().__init__(message)
        self.problems = list(problems or [])
        if status:
            self.status = status


class LROverlayError(LRDisplayConsistencyStop):
    """overlay適用時の位置特定不能・曖昧・STOP判定(黙って原文表示にしない)。"""


# ----------------------------------------------------------------------------- 公開ページ混入検知(M-7、原文§2)
# 公開ページ・TTS入力・ASR正解・Style Prompt・KP表示・study_textに出してはならない語。最終Human報告用資料(user_test外)だけが使う。
PUBLIC_FORBIDDEN_PATTERNS: tuple = (
    ("fhr_class", re.compile(r"""class\s*=\s*["'][^"']*\bfhr-""", re.I)),       # 最終Human報告のCSS class接頭辞
    ("fhr_css", re.compile(r"""(?<![A-Za-z0-9_-])\.fhr-[a-z]""", re.I)),
    ("LR_REWRITTEN", re.compile(r"LR_REWRITTEN")),
    ("LR_APPLIED", re.compile(r"LR_APPLIED")),
    ("FALLBACK_APPLIED", re.compile(r"FALLBACK_APPLIED")),
    ("FALLBACK_MINIMAL", re.compile(r"FALLBACK_MINIMAL_(?:EN|JA)")),
    ("ENGLISH_LOCK", re.compile(r"ENGLISH_LOCK")),
    ("LEGACY_DIALOGUE", re.compile(r"LEGACY_DIALOGUE")),
    ("minimal_fallback", re.compile(r"minimal_fallback|english_lock_fallback")),
    ("note_local_rewrite", re.compile(r"Local Rewrite採用")),
    ("note_lr_fallback_jp", re.compile(r"Fallback(?:発動|採用)|Local Rewrite(?:発動|適用)|音声は原稿から変更")),
)


def public_leak_hits(text: str | None) -> list:
    """公開物の文字列(HTML/TTS入力/ASR正解/Style Prompt/KP表示/study_text)に含まれる禁止語の識別子list(0件=空)。"""
    t = text or ""
    return [name for name, rx in PUBLIC_FORBIDDEN_PATTERNS if rx.search(t)]


def assert_no_public_leak(text: str | None, *, where: str = "public") -> None:
    hits = public_leak_hits(text)
    if hits:
        raise LRDisplayConsistencyStop(f"LR_FALLBACK_NOTE_IN_PUBLIC({where}): 公開物にLR/Fallback注記が混入しています: {hits}", [{"where": where, "hits": hits}])


# ----------------------------------------------------------------------------- 台帳(メモリ導出)
def level_dir_of(run_dir: str, level: str) -> str:
    return os.path.join(run_dir, level)


def level_ledger(run_dir: str, level: str, *, results_path: str | None = None, level_dir: str | None = None) -> dict:
    """run×levelのLR台帳(er129.build_lr_ledgerの薄いwrapper。X/Y/Z共通=`<run>/<level>/audit/tts_generation_results.json`)。
    tts_generation_results.jsonが無いlevel(未TTS)は空台帳(LR 0=overlayなし)。"""
    e129 = _e129()
    ld = level_dir or level_dir_of(run_dir, level)
    rp = results_path or os.path.join(ld, "audit", "tts_generation_results.json")
    if not os.path.exists(rp):
        return {"schema": "lr_fallback_ledger_derived_v0", "run_dir": run_dir, "level": level, "results_path": rp, "results_sha256": None, "clips": [], "skipped_no_event": 0}
    return e129.build_lr_ledger(run_dir, level, results_path=rp, level_dir=ld)


def unit_key(clip: dict) -> str:
    """表示unitの識別キー。共有unit(parts.json:part1等)はsource、clip単位(entry.canonical_text)はclip_id付き。"""
    src = ((clip.get("display") or {}).get("source")) or ""
    return f"{ENTRY_SOURCE}:{clip.get('clip_id')}" if src == ENTRY_SOURCE else src


def overlay_clips(ledger: dict | None, *, source: str | None = None, clip_id: str | None = None) -> list:
    """表示へ反映すべきclip(LR採用・人間承認で原文復帰でない・判定PASS系)。source/clip_idで絞る。STOP判定のclipが該当すれば例外(原文表示に黙って倒さない)。"""
    e129 = _e129()
    out = []
    for clip in (ledger or {}).get("clips") or []:
        lr = clip.get("lr")
        if not lr or not lr.get("adopted_in_final"):
            continue
        key_ok = (clip_id is not None and clip.get("clip_id") == clip_id) or (source is not None and ((clip.get("display") or {}).get("source")) == source) \
            or (source is not None and unit_key(clip) == source)
        if not key_ok:
            continue
        v = clip.get("verdict")
        if v == e129.V_PASS:
            out.append(clip)
        elif v in (e129.V_UNLOCATABLE, e129.V_AMBIGUOUS, e129.V_PARITY, e129.V_T1, e129.V_T2, e129.V_T3):
            raise LROverlayError(f"LR_DISPLAY_OVERLAY_BLOCKED({clip.get('clip_id')}): 台帳判定={v}。表示本文を原文のまま通しません", [{"clip_id": clip.get("clip_id"), "verdict": v}])
    return out


def overlay_text(ledger: dict | None, text: str, *, source: str | None = None, clip_id: str | None = None) -> str:
    """表示unit(text)に、該当clipのLR後語句を派生適用して返す(原本不変)。台帳が空・該当clipなし=入力と同一object(byte同一)。
    位置は変更箇所前後k語のanchorで特定(er129.locate_op)。反映済み(AFTER)なら何もしない(冪等)。特定不能・曖昧=LROverlayError。"""
    clips = overlay_clips(ledger, source=source, clip_id=clip_id)
    if not clips:
        return text
    e129 = _e129()
    placed = []
    for clip in clips:
        lr = clip["lr"]
        lb_full = e129._lw(lr["before"])
        for op in e129.compute_ops(lr["before"], lr["after"]):
            loc = e129.locate_op(text, op, lb_full)
            if loc["status"] != "OK":
                raise LROverlayError(f"LR_DISPLAY_OVERLAY_UNLOCATABLE({clip.get('clip_id')}): {loc.get('status')} {op['core_before_text']!r}->{op['core_after_text']!r}",
                                     [{"clip_id": clip.get("clip_id"), "status": loc.get("status")}])
            placed.append((op, loc["h"], loc["state"]))
    return e129.apply_overlay(text, placed)


def display_text_of_clip(ledger: dict | None, clip_id: str, text: str) -> str:
    """Z(clip単位表示)・Y topic_intro等の共通入口=`overlay_text(..., clip_id=)`。"""
    return overlay_text(ledger, text, clip_id=clip_id)


def _copy_with(d: dict, path: list, value: str) -> dict:
    out = dict(d)
    if len(path) == 1:
        out[path[0]] = value
    else:
        out[path[0]] = _copy_with(dict(d.get(path[0]) or {}), path[1:], value)
    return out


def overlay_level_units(ledger: dict | None, parts: dict, support: dict | None = None) -> tuple:
    """X/Yのページ描画・ハイライト解決が使う`parts`/`support`のoverlay済みコピーを返す((parts2, support2))。入力dictは変更しない。
    対象=parts.json(`part1`/`in_one_line`/`segments.<sid>`)と`*support_texts.json`のキー。台帳が空=入力と同一object(byte同一)。
    `entry.canonical_text`出典のclip(Z・Y topic_intro等)はここでは扱わず`display_text_of_clip`を使う。"""
    p2, s2 = parts, support
    for clip in (ledger or {}).get("clips") or []:
        lr = clip.get("lr")
        if not lr or not lr.get("adopted_in_final"):
            continue
        src = (clip.get("display") or {}).get("source") or ""
        if src == ENTRY_SOURCE or ":" not in src:
            continue
        fname, key = src.split(":", 1)
        if fname == "parts.json":
            path = ["segments", key[len("segments."):]] if key.startswith("segments.") else [key]
            cur = p2
            for k in path:
                cur = (cur or {}).get(k) if isinstance(cur, dict) else None
            if not isinstance(cur, str):
                raise LROverlayError(f"LR_DISPLAY_OVERLAY_SOURCE_MISSING({clip.get('clip_id')}): {src}")
            new = overlay_text(ledger, cur, source=src)
            if new != cur:
                p2 = _copy_with(p2, path, new)
        elif fname.endswith("support_texts.json") and support is not None:
            cur = (s2 or {}).get(key)
            if not isinstance(cur, str):
                raise LROverlayError(f"LR_DISPLAY_OVERLAY_SOURCE_MISSING({clip.get('clip_id')}): {src}")
            new = overlay_text(ledger, cur, source=src)
            if new != cur:
                s2 = _copy_with(s2, [key], new)
    return p2, s2


# ----------------------------------------------------------------------------- 描画単位(三者一致Gateの入力)
def rendered_display_units(run_dir: str, level: str, *, ledger: dict | None = None, results_path: str | None = None, level_dir: str | None = None) -> dict:
    """「配線後にページが描画する表示unit」={unit_key: overlay後の本文}。台帳のLR採用clipごとに、表示出典(er129._display_candidates)の原文へoverlayを適用して返す。
    ページ描画側(patchでoverlay_level_units/display_text_of_clipを呼ぶ)と同じoverlay関数を通すので、Gateが検査する本文=ページが描く本文。"""
    e129 = _e129()
    ld = level_dir or level_dir_of(run_dir, level)
    ledger = ledger if ledger is not None else level_ledger(run_dir, level, results_path=results_path, level_dir=ld)
    rp = results_path or os.path.join(ld, "audit", "tts_generation_results.json")
    entries = {sid: e for sid, e, _ in e129._iter_entries(e129._jl(rp) or {})} if os.path.exists(rp) else {}
    out: dict = {}
    for clip in ledger.get("clips") or []:
        lr = clip.get("lr")
        if not lr or not lr.get("adopted_in_final"):
            continue
        src = (clip.get("display") or {}).get("source")
        ent = entries.get(clip["clip_id"])
        if not src or ent is None:
            continue
        base = next((t for s, t in e129._display_candidates(clip["clip_id"], ent, ld) if s == src), None)
        if base is None:
            continue
        key = unit_key(clip)
        out[key] = overlay_text(ledger, base, source=key) if src != ENTRY_SOURCE else overlay_text(ledger, base, clip_id=clip["clip_id"])
    return out


# ----------------------------------------------------------------------------- 三者一致Gate(assemble入口1か所、Opus (b)-5)
def evaluate_text_parity(run_dir: str, level: str, *, rendered_display: dict | None = None, ledger: dict | None = None,
                         results_path: str | None = None, level_dir: str | None = None, not_rendered_clip_ids=()) -> dict:
    """三者一致(表示本文=TTS入力=ASR正解)を台帳全clipで評価する(例外を上げない)。戻り値={status: OK|BLOCKED_LR_DISPLAY_CONSISTENCY|BLOCKED_LR_CONFIRMED_CONTENT_INTERFERENCE,
    problems[], confirmed[], record_mismatch[], checked[]}。
    rendered_display=ページが実際に描画する表示unit(`rendered_display_units`相当、unit_key→本文)。**None(=overlay未配線の呼出)は、LR採用clipがあれば常に異常側**
    (DISPLAY_NOT_OVERLAID)=配線後に初めて通る設計(INTEGRATION F-5)。LR 0のrunは表示unitが不要なのでNone・{}どちらでもOK。
    not_rendered_clip_ids=そのFamilyのページが`entry.canonical_text`を描画しないclip(X: `topic_intro`/`japanese_title`はテンプレート表示)。これらにLR採用があると
    ページ表示にoverlayを届ける経路が無いため`DISPLAY_SOURCE_NOT_RENDERED`で停止する(見逃さない=fail-closed)。"""
    e129 = _e129()
    ld = level_dir or level_dir_of(run_dir, level)
    ledger = ledger if ledger is not None else level_ledger(run_dir, level, results_path=results_path, level_dir=ld)
    rp = results_path or os.path.join(ld, "audit", "tts_generation_results.json")
    entries = {sid: e for sid, e, _ in e129._iter_entries(e129._jl(rp) or {})} if os.path.exists(rp) else {}
    problems, confirmed, record, checked = [], [], [], []
    for clip in ledger.get("clips") or []:
        v, cid = clip.get("verdict"), clip.get("clip_id")
        if v == e129.V_NO_LR:
            continue
        if v in (e129.V_UNLOCATABLE, e129.V_AMBIGUOUS, e129.V_PARITY):
            problems.append({"clip_id": cid, "code": v, "detail": clip.get("text_parity") or (clip.get("display") or {}).get("failure")})
        elif v in (e129.V_T1, e129.V_T2, e129.V_T3):
            confirmed.append({"clip_id": cid, "code": v, "detail": clip.get("overlap")})
        elif v == e129.V_RECORD_MISMATCH:
            record.append({"clip_id": cid, "code": v})        # 採用take記録不一致=B4(style gate)の領分。本Gateは表示一致だけを見る
        elif v == e129.V_PASS_SUPERSEDED:
            checked.append({"clip_id": cid, "verdict": v, "display": "original(HR採用で音声=原文)"})
        elif v == e129.V_PASS:
            key = unit_key(clip)
            if cid in set(not_rendered_clip_ids or ()):
                problems.append({"clip_id": cid, "code": "DISPLAY_SOURCE_NOT_RENDERED",
                                 "detail": "このFamilyのページは当該clipのentry.canonical_textを描画しない(テンプレート表示)ため、LR後の英文を表示へ反映できません"})
                continue
            if rendered_display is None or key not in rendered_display:
                problems.append({"clip_id": cid, "code": "DISPLAY_NOT_OVERLAID",
                                 "detail": f"LR採用clipの描画本文({key})が渡されていません(表示overlay未配線=本文と音声が不一致のまま)"})
                continue
            ent = entries.get(cid)
            info = e129._lr_info(ent, ent.get("canonical_text") if isinstance(ent.get("canonical_text"), str) else (ent.get("text") or "")) if ent else None
            if not info:
                problems.append({"clip_id": cid, "code": "LR_RECORD_UNAVAILABLE", "detail": "entryからLR記録を再取得できません"})
                continue
            tts_in = (ent.get("text") if info["form"] == "X/Y" else info["after"]) or info["after"]
            strict = [op["after_tokens"] for op in e129.compute_ops(info["before"], info["after"]) if op["after_tokens"]]
            par = e129.check_text_parity(rendered_display[key], tts_in, info["asr_expected"], strict)
            checked.append({"clip_id": cid, "verdict": par["verdict"], "unit": key})
            if not par["verdict"].startswith("PASS"):
                problems.append({"clip_id": cid, "code": par["verdict"], "detail": par["detail"]})
    status = "OK"
    if problems:
        status = STATUS_DISPLAY_CONSISTENCY
    elif confirmed:
        status = STATUS_CONFIRMED_INTERFERENCE
    return {"status": status, "problems": problems, "confirmed": confirmed, "record_mismatch": record, "checked": checked, "run_dir": run_dir, "level": level}


def assert_text_parity(run_dir: str, level: str, *, rendered_display: dict | None = None, ledger: dict | None = None, results_path: str | None = None,
                       level_dir: str | None = None, stop_cls=None, not_rendered_clip_ids=()) -> dict:
    """X/Y/Z各assembleの直前に置くGate(未配線=どこからも呼ばれない)。不一致・位置不能・overlay未適用=技術STOP(例外。HRキューへ入れない)。
    X/Yは`blocked_summary(exc)`をrun_summary_assemble.jsonへ保存して返す形、Zは`stop_cls=FamilyZLRDisplayConsistencyStop`(FamilyZAudioStop系)を渡す。
    T1/T2/T3(確定内容との重なり)は`status=BLOCKED_LR_CONFIRMED_CONTENT_INTERFERENCE`の例外(ユーザー判断)。全PASS=評価結果dictを返す。"""
    res = evaluate_text_parity(run_dir, level, rendered_display=rendered_display, ledger=ledger, results_path=results_path, level_dir=level_dir,
                               not_rendered_clip_ids=not_rendered_clip_ids)
    if res["status"] == "OK":
        return res
    items = res["problems"] if res["status"] == STATUS_DISPLAY_CONSISTENCY else res["confirmed"]
    names = "; ".join(f"{p['clip_id']}:{p['code']}" for p in items)[:600]
    if res["status"] == STATUS_DISPLAY_CONSISTENCY:
        msg = f"{res['status']}({level}): {names}。技術STOP(音声・LRは正常のためHuman Reviewへは入れない)"
    else:
        msg = f"{res['status']}({level}): {names}。確定内容に干渉=ユーザー判断"
    if stop_cls is not None:
        exc = stop_cls(msg)
        try:
            exc.problems, exc.status = items, res["status"]
        except Exception:
            pass
        raise exc
    raise LRDisplayConsistencyStop(msg, items, status=res["status"])


def blocked_summary(exc: LRDisplayConsistencyStop) -> dict:
    """X/Yのrun_summary_assemble.jsonへ保存する形(既存`BLOCKED_*` summaryと同形: status+reason)。HRキュー(register_terminal_hr)には流さない。"""
    return {"status": exc.status, "reason": str(exc), "problems": exc.problems, "hr_queue": False}


# ----------------------------------------------------------------------------- 配線用の薄い入口(patch側の呼出を1行にする。未配線の間はどこからも呼ばれない)
def overlay_level_dir_units(level_dir: str, parts: dict, support: dict | None = None) -> tuple:
    """X/Yページ描画・ハイライト解決用: `<run>/<level>`のdirから台帳を導出してparts/supportをoverlay(台帳が空=入力と同一object)。"""
    ld = level_dir.rstrip("/\\")
    return overlay_level_units(level_ledger(os.path.dirname(ld), os.path.basename(ld), level_dir=ld), parts, support)


def unit_sources(unit_key_: str) -> list:
    """ハイライトのDisplayUnit key(`full_story_part1`/`in_one_line`/Yのsegment id)に対応する台帳の表示出典候補。"""
    m = re.match(r"^full_story_(part\d+)$", unit_key_)
    out = [f"parts.json:{unit_key_}", f"parts.json:segments.{unit_key_}"]
    if m:
        out.append(f"parts.json:{m.group(1)}")
    return out


def overlay_highlight_units(ledger: dict | None, units: list) -> list:
    """DisplayUnit列(`[{"key","texts":[...],"joiner"}]`)のoverlay済みコピー。変更なし=入力と同一object。texts(1要素=1本文)単位に適用する。"""
    changed, out = False, []
    for u in units:
        texts = list(u.get("texts") or [])
        new_texts = texts
        if ledger and len(texts) == 1:
            t = texts[0]
            for src in unit_sources(u.get("key") or ""):
                t2 = overlay_text(ledger, t, source=src)
                if t2 != t:
                    t = t2
            if t != texts[0]:
                new_texts = [t]
        if new_texts is not texts:
            changed = True
            out.append(dict(u, texts=new_texts))
        else:
            out.append(u)
    return out if changed else units


X_NOT_RENDERED_CLIP_IDS = ("topic_intro", "japanese_title")   # Xのページはテンプレート表示(`Today's topic is {title}.`・日本語title)でentry.canonical_textを描かない


def assemble_gate_summary(run_dir: str, level: str, *, not_rendered_clip_ids=()) -> dict | None:
    """X/Y assemble入口用: None=通過 / dict=`run_summary_assemble.json`へ保存して返すBLOCKED summary(HRキューへ流さない)。
    ページが描画する表示unit(rendered_display_units)を渡して三者一致を検査する。台帳・overlayの内部異常(例外)も同じBLOCKEDへ倒す(黙って通さない)。"""
    try:
        assert_text_parity(run_dir, level, rendered_display=rendered_display_units(run_dir, level), not_rendered_clip_ids=not_rendered_clip_ids)
    except LRDisplayConsistencyStop as exc:
        return blocked_summary(exc)
    return None


def z_assemble_gate(run_dir: str, level: str, stop_cls) -> dict:
    """Z assemble入口用: 不一致は`stop_cls`(FamilyZLRDisplayConsistencyStop、FamilyZAudioStop系列)を上げる。"""
    try:
        rendered = rendered_display_units(run_dir, level)
    except LRDisplayConsistencyStop as exc:
        z = stop_cls(str(exc))
        z.problems, z.status = exc.problems, exc.status
        raise z from exc
    return assert_text_parity(run_dir, level, rendered_display=rendered, stop_cls=stop_cls)
