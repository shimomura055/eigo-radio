"""LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 委任_08(Phase B / B4): 採用take分類核 `classify_adopted_take`(未配線の純module)。

目的(ユーザー正式決定UD-3、`docs/pm/delegation_log/2026-10-28_LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01_USER.md` §5):
  X M3 / Y style gate / Z style gate が共通で呼ぶ「最終採用takeが正常なLR/Fallbackか、異常か」の判定核。
  - 通過(PASS_WITH_WARNING): 承認済みStyle allowlistに含まれ・slotがpolicy許可範囲・記録完全・ASR PASS系・三者一致PASS・確定内容非干渉の
    正常Fallback(`FALLBACK_APPLIED`)/正常LR(`LR_APPLIED`)。HR・組立停止は要求しない。
  - BLOCK(従来どおり): 未承認/不明Style・許可されないFallback方式・記録欠落/不一致・ASR NG・overlap干渉・parity不一致・例外(fail-closed)。
設計: W3_UD3_GATE_DESIGN_01 §2/§6/§9、INTEGRATION_01 F-4/F-5/F-6/F-16、OPUS_REVIEW_01 (b)-1/(b)-5/M-5/M-8/M-9/M-10。

性質(厳守):
  - 純関数・読取専用・LLMなし・API 0。run dirを書き換えない。
  - **未配線**: どのProductionコードからもimportされない(`test_no_production_module_imports_er130`で固定)。X M3 `m3_assembly_gate`・
    Y `y_style_gate`・Z `z_style_actual_gate`の呼出切替は統合配線commit(B-wire)で行う。既定動作は何も変わらない。
  - 検査を再実装しない(Opus (b)-5): 採用take解決・三者一致(parity)・確定内容重なり(T1-T3)はer129の導出結果(ledger clip)を**受け取る**。
  - allowlistはleaf側の既存定数をimportして導出する(コピー禁止)。driftはtestで固定(Style変更時に承認判断を強制)。
  - profile非依存(F-4)。policy(er127 PROFILES)だけが許可範囲を決める。
"""
from __future__ import annotations

import hashlib
from typing import Any, Iterable

import er127_tts_block_policy_01 as er127
import er129_lr_display_reflection_01 as er129

PASS = "PASS"
PASS_WITH_WARNING = "PASS_WITH_WARNING"
BLOCK = "BLOCK"

# policy.third_style -> er129のStyle種別(kind)
THIRD_STYLE_TO_KIND = {
    "FALLBACK_MINIMAL_EN": er129.KIND_MINIMAL_EN,
    "FALLBACK_MINIMAL_JA": er129.KIND_MINIMAL_JA,
    "ENGLISH_LOCK": er129.KIND_ENGLISH_LOCK,
    "LEGACY_DIALOGUE": er129.KIND_LEGACY_DIALOGUE,
}
# 採用takeのStyleをshaでなく「直接記録(mode・段)」で確定している導出経路(shaは記録に無いがStyle種別は一意)
_DIRECT_KIND_RECORD_HOWS = frozenset({"dialogue_tts.final_mode", "english_lock_attempts_log.verified"})
# 旧記録でshaが取れないがstandard段のverifiedかつfallback_used False(=role Style段)と直接記録されている経路
_STANDARD_STAGE_HOWS = frozenset({"standard_attempts_log.verified(no fallback)"})
_ASR_PASS_STATES = frozenset({"PASS", "PASS_WITH_WARNING"})
# attempt json上でrole Style(または既定Style)を送ったことを示すroute(instruction_textを保存しない旧attempt記録で、shaの代わりにrouteで確認する)。
# driftはtestで固定(leaf source内に存在すること)。minimal/fallback/custom_*以外の既知routeだけを許す。
_ROLE_STYLE_ROUTES = frozenset({"english_style_prefix_wide_margin", "english_style_prefix"})


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ----------------------------------------------------------------------------- allowlist(leaf定数からimportして導出)
def _leaf_constants() -> dict:
    """leaf側の承認済みStyle定数。import失敗はそのまま例外(allowlistを作れない=Gateは通さない)。"""
    import er003_b1_p9a_audio as p9a
    import er003_v1_n3_01_tts_generate as n3
    import er003_v1_repro01_main_generate as repro01
    import er019_family_x_style_profile_01 as xsp
    import er033_tts_flash_lite_family_x_styles_01 as er033
    import er063_family_z_audio_01 as z
    return {"p9a": p9a, "n3": n3, "repro01": repro01, "xsp": xsp, "er033": er033, "z": z}


def build_allowlist() -> dict:
    """承認済みStyle allowlist。
      fallback[kind]  = 承認済みFallback Styleのsha群(EN Minimal / JA短文 / ENGLISH_LOCK / 従来Dialogue)
      role_style      = 承認済みrole Styleのsha群(X STYLE_PROFILES全override + Z FAMILY_Z_ROLE_STYLE + 既定Dialogue/英語Style)
    すべてleaf定数のimportから導出(コピーしない)。"""
    c = _leaf_constants()
    fb = {
        # 委任_15(B10) D1: KP解説③(er019 `_kp_explanation_unified`、X/Y/Z共通の単一関数 er019_family_x_audio_production_runner_01.py:1316)が現に送る既存Production Style
        # `repro01.MINIMAL_INSTRUCTION_PREFIX`(er003_v1_repro01_main_generate.py:566)の登録漏れ是正。新Styleの採用ではない(同定数をimportしてsha導出、コピーなし)
        er129.KIND_MINIMAL_EN: frozenset({sha256_text(c["er033"].FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]),
                                          sha256_text(c["repro01"].MINIMAL_INSTRUCTION_PREFIX)}),
        er129.KIND_MINIMAL_JA: frozenset({sha256_text(c["n3"]._A2_JA_MINIMAL_INSTRUCTION_PREFIX)}),
        er129.KIND_ENGLISH_LOCK: frozenset({sha256_text(c["repro01"].KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION)}),
        er129.KIND_LEGACY_DIALOGUE: frozenset({sha256_text(c["p9a"].ENGLISH_STYLE_PREFIX)}),
    }
    role = set()
    for prof in c["xsp"].STYLE_PROFILES.values():
        for o in (prof.get("overrides") or {}).values():
            role.add(o["sha256"])
    for rk in c["z"].FAMILY_Z_ROLE_STYLE:
        exp = c["z"].z_expected_style(rk)
        if exp:
            role.add(exp["sha256"])
    role.add(sha256_text(c["p9a"].ENGLISH_STYLE_PREFIX))   # 既定Dialogue/英語Style(overrideされないrole、Z Dialogue)
    texts = []
    for prof in c["xsp"].STYLE_PROFILES.values():
        for o in (prof.get("overrides") or {}).values():
            texts.append(o["text"])
    for rk in c["z"].FAMILY_Z_ROLE_STYLE:
        exp = c["z"].z_expected_style(rk)
        if exp:
            texts.append(exp["text"])
    texts.append(c["p9a"].ENGLISH_STYLE_PREFIX)
    return {"fallback": fb, "role_style": frozenset(role), "role_style_texts": tuple(dict.fromkeys(t for t in texts if t))}


def _prefix_ok(instruction_text: str | None, allowlist: dict) -> bool:
    """hint追記後のStyleでも承認role Styleで始まる(M4と同じ規則: len>=原文長 かつ 先頭が原文[:200])。"""
    if not isinstance(instruction_text, str) or not instruction_text:
        return False
    return any(instruction_text.startswith(t[:200]) and len(instruction_text) >= len(t) for t in allowlist.get("role_style_texts", ()))


def adopted_instruction_text(entry: dict, take: dict | None) -> str | None:
    """採用takeのattempt jsonに保存された送信instruction全文(あれば)。audio sha一致→attempt番号一致→人間承認wav隣のjsonの順。"""
    import os
    if not isinstance(take, dict):
        return None
    for aj in er129._load_attempt_jsons(entry):
        if (take.get("audio_sha") and aj.get("sha256") == take["audio_sha"]) or (take.get("ordinal") is not None and aj.get("attempt_number") == take["ordinal"]):
            if isinstance(aj.get("instruction_text"), str):
                return aj["instruction_text"]
    hp = entry.get("adopted_attempt_audio_path")
    if hp:
        aj = er129._jl(os.path.splitext(er129._abs(hp))[0] + ".json")
        if isinstance(aj, dict) and isinstance(aj.get("instruction_text"), str):
            return aj["instruction_text"]
    return None


# ----------------------------------------------------------------------------- 補助
class Classification(dict):
    """verdict: PASS|PASS_WITH_WARNING|BLOCK、reasons[](BLOCK理由コード)、warnings[](構造化: kind=LR_APPLIED|FALLBACK_APPLIED|…)、notes[]。"""

    @property
    def verdict(self) -> str:
        return self["verdict"]

    @property
    def reasons(self) -> list:
        return self["reasons"]

    @property
    def warnings(self) -> list:
        return self["warnings"]

    @property
    def notes(self) -> list:
        return self["notes"]


def _block(reasons: list, warnings: list | None = None, notes: list | None = None) -> Classification:
    seen = []
    for r in reasons:
        if r not in seen:
            seen.append(r)
    return Classification(verdict=BLOCK, reasons=seen, warnings=list(warnings or []), notes=list(notes or []))


def resolve_policy(policy: Any):
    """policy引数(er127.Profile / policy名)をProfileへ。解決できなければNone(呼出側がBLOCK)。"""
    if isinstance(policy, er127.Profile):
        return policy
    if isinstance(policy, str):
        return er127.PROFILES.get(policy)
    return None


def normalize_slot(slot: Any) -> int | None:
    """slot表記を1..6へ。①②③=1..3、①'②'③'(prime付き)=4..6、整数はそのまま。解釈できなければNone(未確認)。"""
    circled = "①②③④⑤⑥"
    if isinstance(slot, bool):
        return None
    if isinstance(slot, int):
        return slot if 1 <= slot <= 6 else None
    if isinstance(slot, str) and slot:
        s = slot.strip()
        prime = any(ch in s for ch in ("'", "′", "’", "ʹ"))
        for ch in s:
            if ch in circled:
                n = circled.index(ch) + 1
                return n + 3 if (prime and n <= 3) else n
        if s.isdigit():
            return normalize_slot(int(s))
    return None


def _allowed_fallback_slots(profile: er127.Profile, kind: str) -> set:
    base = {3, 4} if kind == er129.KIND_ENGLISH_LOCK else {3}      # KP_ENはENGLISH_LOCK段=3,4(4回構成)
    if profile.lr:
        base = base | {6}
    return base


def policy_for_clip(seg_id: str, entry: dict, level: str | None = None):
    """clip(seg_id, entry)からer127 policy名を決める(監査・test用の補助)。決められなければNone(=呼出側でBLOCK、fail-closed)。"""
    import er020_tts_retry_local_rewrite_01 as er020
    sid = seg_id or ""
    import re
    ck = str(entry.get("clip_kind") or "")       # Z形entryはclip_kindで種別を持つ
    if ck in ("kp_en", "kp_ja", "kp_expl_en", "japanese_title"):
        return {"kp_en": "KP_EN", "kp_ja": "JA_STD", "kp_expl_en": "KP_EXPL", "japanese_title": "JA_STD"}[ck]
    if er127.SHELL_EN_ID_RE.fullmatch(sid):
        return "SHELL_EN"
    if re.fullmatch(r"kp\d+_(en|english)", sid):
        return "KP_EN"
    if re.fullmatch(r"kp\d+_(explanation|expl_en)", sid):
        return "KP_EXPL"
    if re.fullmatch(r"kp\d+_(japanese_meaning|ja|meaning)", sid):
        return "JA_STD"
    dt = entry.get("dialogue_tts")
    if isinstance(dt, dict) or str(entry.get("clip_kind") or "") in ("dialogue", "conversation"):
        legacy = isinstance(dt, dict) and str(dt.get("policy") or "").lower() == "legacy"
        return "Z_DLG_LEGACY" if legacy else "Z_DLG_CTX"
    lang = er129._lang_of(entry)
    if lang.startswith("ja"):
        return "JA_STD"
    if ck in ("narrator", "preview", "topic_intro", "comment"):
        return "EN_LR_ADV" if level == "b1b" else "EN_LR_STD"
    try:
        role = er020.resolve_narrative_role(re.sub(r"_c\d+$", "", sid)) if sid else None
    except Exception:
        role = None
    if role in er127.LR_ROLES:
        return "EN_LR_ADV" if level == "b1b" else "EN_LR_STD"
    return None


def adopted_asr_state(entry: dict) -> tuple:
    """採用takeのASR判定(state, source)。LR採用=LR block採用take(retts_result)、それ以外=entry.asr_judgement、Z形=z_adoption=='adopted'かつstatus OK。
    取れなければ(None, None)(=記録欠落)。"""
    lr = entry.get("local_rewrite_recovery")
    if isinstance(lr, dict) and lr.get("status") == "RESOLVED_BY_LOCAL_REWRITE" and not entry.get("local_rewrite_audio_superseded_by_human_approval") \
            and not entry.get(er129.er020.HUMAN_APPROVAL_SUPERSEDES_LR_AUDIO_FLAG):
        aj = ((lr.get("retts_result") or {}).get("asr_judgement")) or {}
        if aj.get("state"):
            return aj["state"], "local_rewrite_recovery.retts_result.asr_judgement"
    aj = entry.get("asr_judgement")
    if isinstance(aj, dict) and aj.get("state"):
        return aj["state"], "asr_judgement"
    # 委任_15(B10) D6: Master Audio Store再利用時はrunner(er019 `_mark_asr_judgement_inherited`)が`asr_judgement`を`asr_judgement_inherited`へ改名する。
    # 元の判定(state付き)が残っている場合に限りそれを採用ASR判定として読む(stateなし・記録欠落は従来どおり(None, None)=ASR_RECORD_MISSING)
    ij = entry.get("asr_judgement_inherited")
    if isinstance(ij, dict) and ij.get("state"):
        return ij["state"], "asr_judgement_inherited"
    if entry.get("z_adoption") == "adopted" and entry.get("status") in (None, "OK"):
        return "PASS", "z_adoption"
    if entry.get("status") == "OK":
        # 旧記録: ASR判定の独立記録はないがTTS層が採用(status OK=verified take)した。採用の事実のみ(state名は不明)
        att = [r for r in (entry.get("attempts_log") or entry.get("attempts") or entry.get("standard_attempts_log") or []) if isinstance(r, dict)]
        if any(r.get("verified") is True for r in att):
            return "PASS", "attempts.verified(legacy)"
    return None, None


def lr_gate_facts(entry: dict) -> Any:
    """LR 7 Gate+Natural English QAの結果。X/Y形=selection.selected.{all_seven_gates_pass,adoptable}が両方Trueなら True、記録があり偽なら False、
    記録なし=None。Z形(2026-10-12ユーザー決定でValidator撤廃、local_rewrite_revalidation.verdict==NOT_REQUIRED)="NOT_REQUIRED"。"""
    lr = entry.get("local_rewrite_recovery")
    if isinstance(lr, dict):
        sel = (lr.get("selection") or {}).get("selected") or {}
        if "all_seven_gates_pass" in sel or "adoptable" in sel:
            return bool(sel.get("all_seven_gates_pass")) and bool(sel.get("adoptable"))
        return None
    rv = entry.get("local_rewrite_revalidation")
    if isinstance(rv, dict) and rv.get("verdict") == "NOT_REQUIRED" and isinstance(entry.get("audio_text_deviation"), dict):
        return "NOT_REQUIRED"
    return None


def dialogue_legacy_fallback_direct(entry: dict, take: dict | None) -> bool:
    """委任_15(B10) D2: Z会話ctx→legacy_fallback(③、policy fz_ctx_v1)の採用が`dialogue_tts`の直接記録で確定しているか。
    final_mode=="legacy_fallback"・policy!="legacy"・final_attempt_n==採用take ordinal・そのattemptが mode=legacy_fallback かつ verified=True のとき True
    (送信Styleは既定Dialogue Style=allowlist LEGACY_DIALOGUE。final_adoptionはsent_style_shaを持たないため、この記録がkind確定の直接証跡)。"""
    dt = (entry or {}).get("dialogue_tts")
    if not isinstance(dt, dict) or dt.get("final_mode") != "legacy_fallback" or str(dt.get("policy") or "").lower() == "legacy":
        return False
    n = dt.get("final_attempt_n")
    if n is None or not isinstance(take, dict) or take.get("ordinal") != n:
        return False
    return any(isinstance(a, dict) and a.get("n") == n and a.get("mode") == "legacy_fallback" and a.get("verified") is True
               for a in dt.get("attempts") or [])


def ctx_from_entry(entry: dict, *, take: dict | None = None, human_approved: bool | None = None, role_style_prefix_ok: bool | None = None) -> dict:
    """entryからctxを組み立てる補助(呼出側gateが渡す値の標準形)。
      asr_state/asr_source、lr_gates_ok、extra_approved_shas(Z ctx Style・entryのrole base sha)、role_style_prefix_ok(既存evaluate_segment_evidence=hint追記時のhead一致)。"""
    st, src = adopted_asr_state(entry)
    extra = set()
    dt = entry.get("dialogue_tts")
    if isinstance(dt, dict) and dt.get("ctx_style_sha256"):
        extra.add(dt["ctx_style_sha256"])
    sp = entry.get("style_profile")
    if isinstance(sp, dict) and sp.get("expected_base_sha256"):
        extra.add(sp["expected_base_sha256"])
    return {"asr_state": st, "asr_source": src, "lr_gates_ok": lr_gate_facts(entry), "extra_approved_shas": extra,
            "dialogue_legacy_direct": dialogue_legacy_fallback_direct(entry, take),
            "role_style_prefix_ok": role_style_prefix_ok, "adopted_instruction_text": adopted_instruction_text(entry, take),
            "human_approved": bool(entry.get(er129.er020.HUMAN_APPROVAL_SUPERSEDES_LR_AUDIO_FLAG) or entry.get("adopted_attempt_audio_path"))
            if human_approved is None else human_approved}


# ----------------------------------------------------------------------------- 分類核
def classify_adopted_take(ledger_clip: dict, policy: Any, allowlist: dict, ctx: dict | None) -> Classification:
    """採用takeの正常/異常を判定する(fail-closed: 例外・検証不能は必ずBLOCK)。

    入力: ledger_clip=er129.build_lr_ledger()のclip(adopted_take/fallback/lr/text_parity/overlap/verdict/warnings)、policy=er127 policy(名前またはProfile)、
          allowlist=build_allowlist()、ctx=ctx_from_entry()形(asr_state・lr_gates_ok・extra_approved_shas・role_style_prefix_ok・human_approved)。"""
    try:
        return _classify(ledger_clip, policy, allowlist, ctx or {})
    except Exception as e:   # noqa: BLE001 - fail-closed
        return _block(["CLASSIFIER_EXCEPTION"], notes=[f"{type(e).__name__}: {str(e)[:200]}"])


def _classify(clip: dict, policy: Any, allowlist: dict, ctx: dict) -> Classification:
    if not isinstance(clip, dict) or not isinstance(allowlist, dict) or "fallback" not in allowlist or "role_style" not in allowlist:
        return _block(["INPUT_INVALID"])
    prof = resolve_policy(policy)
    if prof is None:
        return _block(["POLICY_UNRESOLVED"])
    reasons: list = []
    warnings: list = []
    notes: list = []
    cid = clip.get("clip_id")
    take = clip.get("adopted_take")
    # --- 採用takeの存在・完全性
    if not isinstance(take, dict):
        reasons.append("ADOPTED_TAKE_RECORD_INCOMPLETE")      # UNKNOWN(記録欠落)
        take = None
    elif take.get("status") == "NOT_ADOPTED":
        reasons.append("NO_ADOPTED_TAKE")                      # 終端NG・STOPPED(採用takeなし)=音声品質NG
        take = None
    elif take.get("status") == er129.V_RECORD_MISMATCH:
        reasons.append("RECORD_MISMATCH")
    elif take.get("status") != "OK":
        reasons.append("ADOPTED_TAKE_RECORD_INCOMPLETE")
    lr = clip.get("lr")
    lr_adopted = bool(isinstance(lr, dict) and lr.get("adopted_in_final"))
    human = bool((take or {}).get("source") == "human_approval" or ctx.get("human_approved"))
    kind = (take or {}).get("kind")
    sha = (take or {}).get("style_sha")
    how = (take or {}).get("how")
    fb_used = kind in er129.FALLBACK_KINDS
    if take is not None and kind is None:
        reasons.append("STYLE_RECORD_MISSING")
    # --- ledger側で既に否定された項目(検査は再実装せず結果を受け取る)
    v = clip.get("verdict")
    verdict_map = {er129.V_PARITY: "TEXT_AUDIO_PARITY_MISMATCH", er129.V_UNLOCATABLE: "TEXT_AUDIO_PARITY_UNLOCATABLE",
                   er129.V_AMBIGUOUS: "TEXT_AUDIO_PARITY_UNLOCATABLE", er129.V_T1: "LR_OVERLAPS_CONFIRMED_CONTENT",
                   er129.V_T2: "LR_OVERLAPS_CONFIRMED_CONTENT", er129.V_T3: "LR_OVERLAPS_CONFIRMED_CONTENT"}
    if v in verdict_map:
        reasons.append(verdict_map[v])
    # --- 非対象policy(SHELL_EN/NO_TTS/Z_DLG_LEGACY等third_style=SAME/NONE)でFallback・LR
    third = prof.third_style
    allowed_kind = THIRD_STYLE_TO_KIND.get(third)
    if lr_adopted and not prof.lr:
        reasons.append("LR_ON_NON_LR_ROLE")
    # --- Style(採用takeの実測がallowlistに含まれるか)
    if take is not None and kind is not None:
        if fb_used:
            if allowed_kind is None or kind != allowed_kind:
                reasons.append("FALLBACK_NOT_ALLOWED_FOR_POLICY")
            else:
                al = allowlist["fallback"].get(kind, frozenset())
                if sha is not None:
                    if sha not in al:
                        reasons.append("STYLE_NOT_APPROVED_OR_UNKNOWN")
                elif how in _DIRECT_KIND_RECORD_HOWS:
                    pass
                elif kind == er129.KIND_LEGACY_DIALOGUE and ctx.get("dialogue_legacy_direct") is True:
                    notes.append("STYLE_BY_DIALOGUE_TTS_RECORD(final_mode=legacy_fallback, attempt verified; default Dialogue Style)")
                elif kind == er129.KIND_MINIMAL_JA and any(str(n) == "route=minimal_fallback" for n in (take.get("notes") or [])):
                    # JA短文Fallbackはleaf(`_generate_a2_japanese_minimal_instruction`)が単一定数のみで送り、attemptにはroute名だけ残す(sha非保存)。
                    # route名がStyle識別の直接記録(W3 B-3)。EN短文は別Styleが存在し得るためshaを要求する
                    notes.append("STYLE_BY_ROUTE(minimal_fallback; JA single constant)")
                else:
                    reasons.append("STYLE_RECORD_MISSING")     # Style実測shaが無く、直接記録でもない
                slot_raw = take.get("slot")
                slot = normalize_slot(slot_raw)
                if slot_raw is not None:
                    if slot is None or slot not in _allowed_fallback_slots(prof, kind):
                        reasons.append("FALLBACK_SLOT_INCONSISTENT")
                else:
                    notes.append("SLOT_UNVERIFIED(derived record, slot not recorded)")
        else:
            approved_set = allowlist["role_style"] | frozenset(ctx.get("extra_approved_shas") or ()) \
                | (frozenset({take["from_style_sha"]}) if take.get("from_style_sha") and take["from_style_sha"] in allowlist["role_style"] else frozenset())
            route = next((str(n)[6:] for n in (take.get("notes") or []) if str(n).startswith("route=")), None)
            if sha is not None:
                if sha not in approved_set and ctx.get("role_style_prefix_ok") is not True and not _prefix_ok(ctx.get("adopted_instruction_text"), allowlist):
                    reasons.append("STYLE_NOT_APPROVED_OR_UNKNOWN")
            elif route in _ROLE_STYLE_ROUTES and take.get("from_style_sha") in approved_set:
                notes.append(f"STYLE_BY_ROUTE({route}; instruction text not recorded)")
            elif route in _ROLE_STYLE_ROUTES and take.get("from_style_sha"):
                reasons.append("STYLE_NOT_APPROVED_OR_UNKNOWN")      # role Style routeだが、そのStyleが現行承認集合に無い(置換済み旧Style等)
            elif how in _STANDARD_STAGE_HOWS and take.get("from_style_sha") in approved_set:
                notes.append("OLD_RECORD_STANDARD_STAGE(style sha unavailable; standard stage with fallback_used=False)")
            elif how in _DIRECT_KIND_RECORD_HOWS:
                pass
            elif take.get("source") in ("store_reuse", "fixed_asset"):
                pass
            else:
                reasons.append("STYLE_RECORD_MISSING")
            # 通常Styleのtakeがpolicy third slot(Fallback位置)に出ても、Styleが承認済みなら異常ではない(Styleが変わらない再試行)
    # --- ASR判定(人間承認takeは既存の個別承認経路=ASRを人が代替判断。waiveせず注記)
    if take is not None:
        st = ctx.get("asr_state")
        if human:
            notes.append("HUMAN_APPROVED_TAKE(ASR requirement replaced by existing individual approval)")
        elif st is None:
            reasons.append("ASR_RECORD_MISSING")
        elif st not in _ASR_PASS_STATES:
            reasons.append("ADOPTED_TAKE_ASR_NOT_PASS")
    # --- LR固有
    lr_normal = False
    if lr_adopted:
        gates = ctx.get("lr_gates_ok")
        if gates is False:
            reasons.append("LR_NOT_ADOPTABLE")
        elif gates is None:
            reasons.append("LR_RECORD_INCOMPLETE")
        tp = clip.get("text_parity")
        if not isinstance(tp, dict) or not str(tp.get("verdict") or "").startswith("PASS"):
            if "TEXT_AUDIO_PARITY_MISMATCH" not in reasons and "TEXT_AUDIO_PARITY_UNLOCATABLE" not in reasons:
                reasons.append("TEXT_AUDIO_PARITY_NOT_PASS")     # 未評価(parity未配線)も常にBLOCK(F-5)
        ov = clip.get("overlap")
        if not isinstance(ov, dict):
            reasons.append("OVERLAP_NOT_EVALUATED")
        else:
            for t in ("T1", "T2", "T3"):
                if (ov.get(t) or {}).get("status") == "STOP":
                    reasons.append("LR_OVERLAPS_CONFIRMED_CONTENT")
        if take is not None and take.get("how") == "final_adoption" and take.get("lr_block") is False:
            reasons.append("LR_TAKE_INCONSISTENT")
        lr_normal = True
    elif isinstance(lr, dict) and lr.get("superseded_by_human"):
        tp = clip.get("text_parity")
        if isinstance(tp, dict) and not str(tp.get("verdict") or "").startswith("PASS"):
            reasons.append("TEXT_AUDIO_PARITY_NOT_PASS")
    # --- ledgerの警告
    for w in clip.get("warnings") or []:
        if str(w).startswith("RECORD_INCOMPLETE"):
            if "ADOPTED_TAKE_RECORD_INCOMPLETE" not in reasons and not str(w).endswith("adopted_take"):
                reasons.append("STYLE_RECORD_MISSING" if "adopted_style" in str(w) else "ADOPTED_TAKE_RECORD_INCOMPLETE")
        elif str(w) == "RECORD_MISMATCH":
            if "RECORD_MISMATCH" not in reasons:
                reasons.append("RECORD_MISMATCH")
        else:
            notes.append(f"ledger_warning:{w}")
            if str(w).startswith("LR_REASON_UNAVAILABLE") or str(w).startswith("STYLE_RECORD_CONFLICT"):
                warnings.append({"kind": str(w).split(":")[0], "clip_id": cid})
    if reasons:
        return _block(reasons, warnings, notes)
    # --- 通過(警告記録)
    if fb_used:
        warnings.append({"kind": "FALLBACK_APPLIED", "clip_id": cid, "style_name": take.get("style_name") or kind, "style_kind": kind,
                         "from_style": (clip.get("fallback") or {}).get("from_style"), "slot": take.get("slot"), "ordinal": take.get("ordinal"),
                         "lr_block": take.get("lr_block")})
    if lr_normal:
        warnings.append({"kind": "LR_APPLIED", "clip_id": cid, "changed_spans": clip.get("changed_spans"),
                         "reason": (lr or {}).get("reason")})
    return Classification(verdict=PASS_WITH_WARNING if any(w["kind"] in ("FALLBACK_APPLIED", "LR_APPLIED") for w in warnings) else PASS,
                          reasons=[], warnings=warnings, notes=notes)


# ----------------------------------------------------------------------------- Gate配線用の入口(B-wire、委任_11)
# X M3 / Y style gate / Z style gate が共通で呼ぶ。旧Gateの「LR/Fallback/採用Style由来の違反コード」は、イベントclip(LR・Fallback証跡あり)に限り
# 分類核の判定へ置換する。その他の旧違反(記録欠落・status NG・Store key等=維持項目)・イベントでないclip・台帳を作れない場合は旧判定のまま(fail-closed)。
X_REPLACED = frozenset({
    "LOCAL_REWRITE_RECOVERY", "ADV_MINIMAL_FALLBACK", "STD_FALLBACK_USED_OR_UNKNOWN", "JA_FALLBACK_USED_OR_UNKNOWN",
    "KP_JA_MEANING_FALLBACK_USED_OR_UNKNOWN", "PREVIEW_MINIMAL_FALLBACK", "ADV_STYLE_PREFIX_NOT_PROFILE_PREFIXED",
    "PREVIEW_STYLE_PREFIX_NOT_E1_PREFIXED", "FINAL_STYLE_SHA_MISMATCH_NO_HINT", "FINAL_STYLE_HEAD200_MISMATCH_WITH_HINT",
    "FINAL_STYLE_RECORD_MISSING", "JA_STYLE_ACTUAL_MISMATCH", "JA_STYLE_ACTUAL_UNMEASURED"})
Z_REPLACED = frozenset({"Z_STYLE_ACTUAL_MISMATCH", "Z_STYLE_FALLBACK_ADOPTED"})
# 委任_15(B10) D2: Z会話のStyle実測(style_actual、leafが送信prefixを返さないためctx shaによる推定)は、採用がlegacy_fallbackの正常Fallbackのときは実際の送信Styleと
# 食い違うのが正常(実測=ctx sha、実送信=既定Dialogue Style)。分類核が正常Fallback(PASS系)と判定した場合に限り置換する(異常=BLOCKなら旧違反のまま)
Z_REPLACED_WHEN_FALLBACK = frozenset({"Z_DIALOGUE_STYLE_ACTUAL_MISMATCH"})


def gate_name_to_clip_id(name: str) -> str:
    """X/Y gate名(kpN_english)をledger clip id(kpN_en)へ。"""
    import re
    m = re.fullmatch(r"kp(\d+)_english", name or "")
    return f"kp{m.group(1)}_en" if m else (name or "")


def event_ledger_clips(level_dir: str) -> dict | None:
    """`<level_dir>/audit/tts_generation_results.json`から台帳(イベントclipのみ)を導出して{clip_id: clip}を返す。導出できない(例外)場合はNone
    (呼出側は旧判定のまま=fail-closed)。run dirは読むだけ。"""
    import os
    try:
        ld = level_dir.rstrip("/\\")
        led = er129.build_lr_ledger(os.path.dirname(ld), os.path.basename(ld), level_dir=ld, only_events=True)
        return {c["clip_id"]: c for c in led["clips"]}
    except Exception:   # noqa: BLE001 - 台帳を作れない=置換しない(旧判定=BLOCK側のまま)
        return None


def override_violations(seg_id: str, entry: dict, level: str, violations: list, ledger_clips: dict | None, *, replaced: frozenset,
                        allowlist: dict | None = None, role_style_prefix_ok: bool | None = None,
                        replaced_when_fallback: frozenset = frozenset()) -> dict:
    """旧Gateの違反listのうち`replaced`(LR/Fallback/採用Style由来)を、イベントclipに限り分類核の判定へ置換する。
    戻り値: {violations: 新違反list, warnings: [構造化warning(LR_APPLIED/FALLBACK_APPLIED…)], classification: Classification|None, applied: bool}。
    - ledger_clipsがNone/対象clipがイベントでない/entryが無い=旧違反のまま(applied=False)。
    - 分類核がBLOCK=旧違反を全て残し、分類核の理由コードを追加(旧BLOCKを緩めない)。PASS系=replaced違反だけを除去し警告のみ記録(維持項目は残る)。"""
    cid = gate_name_to_clip_id(seg_id)
    clip = (ledger_clips or {}).get(cid)
    if clip is None or not isinstance(entry, dict):
        return {"violations": list(violations), "warnings": [], "classification": None, "applied": False}
    try:
        allow = allowlist if allowlist is not None else build_allowlist()
        take = clip.get("adopted_take") if isinstance(clip.get("adopted_take"), dict) else None
        pol = policy_for_clip(cid, entry, level)
        ctx = ctx_from_entry(entry, take=take, role_style_prefix_ok=role_style_prefix_ok)
        cls = classify_adopted_take(clip, pol, allow, ctx)
    except Exception as e:   # noqa: BLE001 - fail-closed
        cls = _block(["CLASSIFIER_EXCEPTION"], notes=[f"{type(e).__name__}: {str(e)[:200]}"])
    if cls["verdict"] == BLOCK:
        # 異常=従来どおりBLOCK: 旧違反は残したまま(旧コードの説明を失わない)、分類核の理由コードを追加する
        new = list(violations) + list(cls["reasons"])
    else:
        is_fb = isinstance(take, dict) and take.get("kind") in er129.FALLBACK_KINDS
        new = [v for v in violations if v not in replaced and not (is_fb and v in replaced_when_fallback)]     # 正常なLR/Fallback: 置換対象の旧違反だけを除去(他の旧違反=維持項目は残る)
    return {"violations": list(dict.fromkeys(new)), "warnings": list(cls["warnings"]) if cls["verdict"] != BLOCK else [],
            "classification": cls, "applied": True}
