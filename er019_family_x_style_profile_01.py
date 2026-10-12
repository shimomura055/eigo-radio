# ============================================================
# er019_family_x_style_profile_01.py
# FAMILY-X-COFFEE-P8-FINAL-AUDIO-AND-PRODUCTION-WIRING-01 委任_02
# (OPEN-300、設計書 docs/pm/design/2026-10-12_COFFEE-P8-PRODUCTION-WIRING-DESIGN-02.md)
# ============================================================
# 目的: Coffee Full Story限定のStyle置換(P8、ユーザー決定2026-10-12、
# APPROVED_FOR_PRODUCTION[Coffee限定]、Production未配線=PRODUCTION_WIRED未達)を、
# Family X runner(er019_family_x_audio_production_runner_01.py)へ
# 「明示CLI --style-profile + out_dir固定記録」で配線するための副作用の少ない
# 定数+純関数module。runnerからのみimportされる(Dangling Reference Check)。
#
# 重要な不変条件:
#   - "default" profileは現行とバイト同一(resolve_role_style は base_getter を素通し)。
#     defaultでは新しいkey/fileを一切書かない(S3)。
#   - 共有module(er003/er006/er011/er033定数/Master Store)は一切変更しない。
#   - Phase 1 = Coffee Full Story(FULL_STORY role)のみ。他Role(K2/M2/A5/B5/E1/R2等)は
#     後続Phase(OPEN申し送り、設計書S5)。
#   - OPEN-298(全記事共通Style展開)・OPEN-299(In One Line 2文方針)は範囲外。
#
# S1(Coffee限定の決定ID付き例外 COFFEE-P8-STD-VERBATIM-EXCEPTION-01、
# DECISION_LOG 2026-10-12): Standard(A2)のFull Storyは、通常の
# `er003_v1_n3_01_tts_generate.py`説明文(「A2_ENGLISH_STYLE_PREFIX_SLOWER[自然言語の
# 『わずかに遅く』instruction]を渡し、instruction+6% time-stretchの承認済み組合せを
# 正確に再現すること」)および現行runnerの`_role_style_slower`(6-role短style+
# A2_SLOWER_PACE_INSTRUCTIONを連結)とは異なり、**P8逐語(減速指示を連結しない)+
# 生成後6%減速(post-process自体は共有module側で無変更)**とする。根拠: Coffee v3 Std は
# P8(旧PD8)逐語+6%減速でユーザーが試聴・承認した組合せである。この例外はCoffee
# profile("coffee_p8")限定であり、defaultのStandard仕様・他記事・共有moduleは不変。
# テスト(er019_family_x_style_profile_01_test_01.py)で固定する。
# ============================================================
from __future__ import annotations

import hashlib
import json
import os
import time

DESIGN_ID = "COFFEE-P8-PRODUCTION-WIRING-DESIGN-02"
# FAMILY-X-COFFEE-FINAL-V5-PRODUCTION-WIRING-01 委任_01(2026-10-12、ユーザー正式決定B/C):
# profile "coffee_final_v5" = coffee_p8(Full Story=P8) + Std Preview/Comment1〜4=R2 + Adv KP英英解説=P3。
# 全てCoffee限定(他記事/他Familyへ横展開しない)。既存機構(resolve_role_style/記録/M2/M3/M4/M5)を
# roleごとに拡張しただけで、新しい構造ではない。
V5_DESIGN_ID = "FAMILY-X-COFFEE-FINAL-V5-PRODUCTION-WIRING-01"
STD_VERBATIM_EXCEPTION_ID = "COFFEE-P8-STD-VERBATIM-EXCEPTION-01"

# P8原文(逐語): er057_output/aoede_style_trial_03/prompts/prompts_aoede_style_03.md の
# "## P8" 節コードブロック。402文字。数値WPM・速度倍率は含まない。
P8_TEXT = (
    "Warm, bright, cozy storytelling in the manner of a well-loved radio feature: unhurried, "
    "richly expressive, with full vowels and gentle emphasis, never flat or sleepy. "
    "Let the pitch rise and fall a little more on key words. "
    "Add a touch more brightness and a hint of a smile in the voice, while staying unhurried. "
    "Articulate crisply: distinct consonants, clean word endings, every syllable clearly heard."
)
P8_SHA256 = "3eadf4f6f788b822c90f17ba56d893bccb5fab840358cf48845472cd4f4e5595"
P8_LENGTH = 402

# R2原文(逐語、Standard日本語Aoede Style Trial-02、ユーザー承認済み 2026-10-12): 168文字。
# 出典: er057_output/ja_aoede_style_trial_02/prompts/prompts_R.md "## R2" 節コードブロック。
R2_TEXT = (
    "明るく、温かみのある話し方で。身近な人にちょっとした話題を教えてあげるように、"
    "自然な抑揚と軽やかなリズムをつけてください。ニュース番組としての明瞭さは保ち、"
    "演技がかった話し方は避けてください。句読点の記号そのものに反応して声の高さを変えないでください。"
    "読点は短い息継ぎの間、句点はやや長めの間として、音程は変えずに自然に置いてください。"
)
R2_SHA256 = "625826c1187b6381fe36ff444f1f568fc1f68d639d6a6a8931e728463692252f"
R2_LENGTH = 168

# P3原文(逐語、Adv KP英英解説Style Trial-01、ユーザー正式選択済み 2026-10-12): 141文字。
# = 現行P0(KEY_PHRASE_EXPLANATION_EN)+半角空白1つ+差分句(P3)。
# 出典: er057_output/kp_en_explanation_style_trial_01/prompts/prompts_kp_en_explanation_style_01.md "## P3" 節。
P3_TEXT = (
    "clear, precise, at a measured pace, without dragging "
    "Let the sentence flow from its first word to its last, without stopping partway through."
)
P3_SHA256 = "a8aaec591ef6d9acb42532cc0c84b6edfb2f75991e713d413c565b7e27677acc"
P3_LENGTH = 141

PROFILE_DEFAULT = "default"
PROFILE_COFFEE_P8 = "coffee_p8"
PROFILE_COFFEE_FINAL_V5 = "coffee_final_v5"

# role名(Std JA Preview/Comment1〜4、Adv KP英英解説)
ROLE_SUPPORT_JA = "SUPPORT_JA"
ROLE_KP_EXPLANATION_EN = "KP_EXPLANATION_EN"

# 上書き対象role -> そのroleに対応するsegment名(runner側のsegment名)。
ROLE_SEGMENTS = {
    "FULL_STORY": ("full_story_part1", "full_story_part2", "full_story_part3"),
    # Std(a2)のみ。japanese_title・Key Phrase日本語意味・IN_ONE_LINEは対象外。
    ROLE_SUPPORT_JA: ("preview", "comment_1", "comment_2", "comment_3", "comment_4"),
}
# roleが適用されるlevel("a2"=Standard、"b1b"=Advanced)。levelが対象外ならbase_getterを素通し。
ROLE_LEVELS = {
    "FULL_STORY": ("a2", "b1b"),
    ROLE_SUPPORT_JA: ("a2",),
    ROLE_KP_EXPLANATION_EN: ("b1b",),
}

_FULL_STORY_OVERRIDE = {
    "text": P8_TEXT, "sha256": P8_SHA256,
    # S1: Standardは逐語(減速指示非連結)+生成後6%減速(共有module側)。
    "std_append_slower_instruction": False,
}

STYLE_PROFILES = {
    PROFILE_DEFAULT: {"overrides": {}},
    PROFILE_COFFEE_P8: {
        "overrides": {"FULL_STORY": dict(_FULL_STORY_OVERRIDE)},
    },
    # V5: P8(Full Story) + R2(Std Preview/Comment1〜4) + P3(Adv KP英英解説)。Coffee限定。
    PROFILE_COFFEE_FINAL_V5: {
        "overrides": {
            "FULL_STORY": dict(_FULL_STORY_OVERRIDE),
            ROLE_SUPPORT_JA: {"text": R2_TEXT, "sha256": R2_SHA256},
            ROLE_KP_EXPLANATION_EN: {"text": P3_TEXT, "sha256": P3_SHA256},
        },
    },
}

PROFILE_RECORD_RELPATH = "audit/style_profile.json"
APPROVED_BACKEND = "speech_metadata_flash_lite"

# M2: これらのうち1つでも存在するout_dirでは、新規にprofile記録を作れない
# (Review Lock/人間承認はtext shaのみで照合され、Styleを区別しないため)。
_RUN_STATE_FILES = ("tts_generation_results.json", "review_lock_state.json", "human_approved_segments.json")


class StyleProfileStop(RuntimeError):
    """USER_DECISION_REQUIRED相当のSTOP(課金前に止める)。"""


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _verify_constants() -> None:
    import er002_common as common
    for label, text, sha, length in (("P8", P8_TEXT, P8_SHA256, P8_LENGTH), ("R2", R2_TEXT, R2_SHA256, R2_LENGTH),
                                     ("P3", P3_TEXT, P3_SHA256, P3_LENGTH)):
        if sha256_text(text) != sha or len(text) != length:
            raise StyleProfileStop(
                f"[STOP][STYLE-PROFILE] {label}定数のsha256/長さが原典と一致しません"
                f"(sha={sha256_text(text)}, len={len(text)})。コード改変の疑い。")
        common.assert_no_wpm_specification(text)


_verify_constants()  # import時にも検証(不一致=即STOP)


def get_profile(profile_id: str) -> dict:
    if profile_id not in STYLE_PROFILES:
        raise StyleProfileStop(f"[STOP][STYLE-PROFILE] 未知のstyle profile: {profile_id!r}"
                                f"(choices={sorted(STYLE_PROFILES)})")
    return STYLE_PROFILES[profile_id]


def overridden_roles(profile_id: str) -> list[str]:
    return sorted(get_profile(profile_id)["overrides"])


def overridden_segment_names(profile_id: str, level: str | None = None) -> list[str]:
    """segment名(runner側)。KP英英解説はsegmentではなくkey_phrases配下のため含まない。
    levelを渡すとそのlevelに適用されるroleのsegmentだけを返す(既定None=全level、従来互換)。"""
    names = []
    for role in overridden_roles(profile_id):
        if level is not None and level not in ROLE_LEVELS.get(role, ("a2", "b1b")):
            continue
        names.extend(ROLE_SEGMENTS.get(role, ()))
    return names


def resolve_role_style(profile_id: str, role: str, level: str, base_getter):
    """単一解決関数(runnerの_role_style/_role_style_slowerは全てここを経由する)。
    profileにそのroleのoverrideが無ければ base_getter(role) を素通しで返す
    (default・他roleはバイト同一)。overrideがあれば検証済みtextを返す。
    level("a2"|"b1b")はStd/Advの区別用。P8は両levelとも逐語(Stdも減速指示を連結しない、S1)。
    SUPPORT_JA(R2)はa2のみ、KP_EXPLANATION_EN(P3)はb1bのみ(対象外levelはbase_getter素通し)。"""
    override = get_profile(profile_id)["overrides"].get(role)
    if override is None:
        return base_getter(role)
    if level not in ("a2", "b1b"):
        raise StyleProfileStop(f"[STOP][STYLE-PROFILE] 不正なlevel: {level!r}")
    if level not in ROLE_LEVELS.get(role, ("a2", "b1b")):
        return base_getter(role)
    text = override["text"]
    if sha256_text(text) != override["sha256"]:
        raise StyleProfileStop(f"[STOP][STYLE-PROFILE] profile={profile_id} role={role} のsha256不一致")
    return text


def assert_profile_backend(profile_id: str, tts_backend: str) -> None:
    """M5: profile != default のとき tts_backend は speech_metadata_flash_lite 必須
    (--allow-legacy-backend でも同じ)。legacy backendでは_role_style()がNoneを返し
    P8が黙って落ちるため、課金前にSTOPする。"""
    if profile_id != PROFILE_DEFAULT and tts_backend != APPROVED_BACKEND:
        raise StyleProfileStop(
            f"[STOP][M5][USER_DECISION_REQUIRED] style profile {profile_id!r}は"
            f"tts_backend={APPROVED_BACKEND!r}でのみ実行できます(現在={tts_backend!r}、"
            "--allow-legacy-backendでも不可)。課金前にSTOPしました。")


# ------------------------------------------------------------
# 固定記録(out_dir/audit/style_profile.json)
# ------------------------------------------------------------
def record_path(out_dir: str) -> str:
    return f"{out_dir}/{PROFILE_RECORD_RELPATH}"


def build_record(profile_id: str) -> dict:
    profile = get_profile(profile_id)
    return {
        "profile_id": profile_id, "design_id": DESIGN_ID,
        "overridden_roles": overridden_roles(profile_id),
        "roles": {role: {"sha256": o["sha256"], "length": len(o["text"]),
                          **({"std_append_slower_instruction": o["std_append_slower_instruction"]}
                             if "std_append_slower_instruction" in o else {}),
                          **({"levels": list(ROLE_LEVELS[role])} if profile_id == PROFILE_COFFEE_FINAL_V5 else {})}
                  for role, o in profile["overrides"].items()},
        "std_verbatim_exception_id": STD_VERBATIM_EXCEPTION_ID,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }


def read_record(out_dir: str) -> dict | None:
    path = record_path(out_dir)
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:  # 壊れた記録=fail-closed
        raise StyleProfileStop(f"[STOP][STYLE-PROFILE] {path} を読めません: {type(e).__name__}") from e


def verify_record(record: dict) -> str:
    """記録が現行コードのprofile定義(roleごとのsha256)と一致することを検証し、profile_idを返す。"""
    profile_id = record.get("profile_id")
    profile = get_profile(profile_id)
    for role, o in profile["overrides"].items():
        rec_role = (record.get("roles") or {}).get(role) or {}
        if rec_role.get("sha256") != o["sha256"]:
            raise StyleProfileStop(
                f"[STOP][STYLE-PROFILE] 記録されたprofile={profile_id} role={role} のsha256が現行定義と不一致です"
                f"(記録={rec_role.get('sha256')}, 現行={o['sha256']})。")
    if sorted(record.get("overridden_roles") or []) != overridden_roles(profile_id):
        raise StyleProfileStop("[STOP][STYLE-PROFILE] 記録のoverridden_rolesが現行定義と不一致です。")
    return profile_id


def existing_run_artifacts(out_dir: str) -> list[str]:
    """M2: out_dir直下および各level(a2/b1b)のaudit/配下で、Review Lock/人間承認/TTS結果の
    いずれかが既に存在するパスを返す。"""
    found = []
    for base in (out_dir, f"{out_dir}/a2", f"{out_dir}/b1b"):
        for name in _RUN_STATE_FILES:
            path = f"{base}/audit/{name}"
            if os.path.exists(path):
                found.append(path)
    return found


def resolve_run_profile(out_dir: str, cli_profile: str | None, write: bool = True) -> tuple[str, str]:
    """run全体のprofileを決定する。戻り値は (profile_id, source)。
    - 固定記録がある場合は記録を正とする。CLI未指定なら記録を採用(resume)。CLI明示で
      記録と食い違う場合はSTOP(silentにdefaultへ戻らない/途中でprofileが混在しない)。
    - 記録が無い場合: CLI未指定/default -> default(新規file/keyは書かない、S3)。
      CLI coffee_p8: 既存run記録(M2)があればSTOP、無ければ記録を作成する。"""
    if cli_profile is not None:
        get_profile(cli_profile)
    record = read_record(out_dir)
    if record is not None:
        recorded = verify_record(record)
        if cli_profile is not None and cli_profile != recorded:
            raise StyleProfileStop(
                f"[STOP][USER_DECISION_REQUIRED] --style-profile={cli_profile!r} が{record_path(out_dir)}の"
                f"固定記録({recorded!r})と食い違います。途中でprofileを変更できません。")
        return recorded, "record"
    if cli_profile is None or cli_profile == PROFILE_DEFAULT:
        return PROFILE_DEFAULT, "default_no_record"
    existing = existing_run_artifacts(out_dir)
    if existing:
        raise StyleProfileStop(
            f"[STOP][M2][USER_DECISION_REQUIRED] --style-profile={cli_profile!r} は新しいout_dirでのみ実行できます"
            f"(Review Lock/人間承認はtext shaのみで照合されStyleを区別しないため、既存run記録の混在を防ぐ)。"
            f"既存の記録: {existing}。style_profile.jsonは作成していません。")
    if write:
        os.makedirs(os.path.dirname(record_path(out_dir)), exist_ok=True)
        with open(record_path(out_dir), "w", encoding="utf-8") as f:
            json.dump(build_record(cli_profile), f, ensure_ascii=False, indent=2)
    return cli_profile, "cli_new_record"


# ------------------------------------------------------------
# segment記録(S3: 上書き対象roleのsegmentにだけ付ける)
# ------------------------------------------------------------
def segment_profile_record(profile_id: str, role: str, applied_style: str | None):
    """上書き対象roleのsegmentにだけ付ける記録。非対象(default/他role)はNone(新keyを書かない)。
    style_base_sha256 = hint追記前にrunnerが渡したStyle文字列のsha256(M4)。"""
    override = get_profile(profile_id)["overrides"].get(role)
    if override is None:
        return None
    return {
        "profile_id": profile_id, "role": role, "expected_base_sha256": override["sha256"],
        "style_base_sha256": sha256_text(applied_style) if applied_style is not None else None,
    }


def attach_segment_profile_record(entry: dict, profile_id: str, role: str, applied_style: str | None) -> dict:
    rec = segment_profile_record(profile_id, role, applied_style)
    if rec is not None:
        entry["style_profile"] = rec
    return entry


# ------------------------------------------------------------
# M4: runtime evidence判定(hint追記を考慮)
# ------------------------------------------------------------
def _final_style_record(entry: dict, level: str) -> dict | None:
    """segment結果から実送信Style(hint追記後)のsha256/head200/lenを取り出す。
    Adv(news_tail_fix)=top-level style_prefix(文字列)、Std(repro01)=attempts_log末尾のstyle_prefix(record)。"""
    sp = entry.get("style_prefix")
    if isinstance(sp, str):
        if sp.startswith("<default:"):
            return None
        return {"sha256": sha256_text(sp), "head200": sp[:200], "len": len(sp)}
    if isinstance(sp, dict):
        return sp
    for att in reversed(entry.get("attempts_log") or []):
        rec = att.get("style_prefix") if isinstance(att, dict) else None
        if isinstance(rec, dict):
            return rec
    return None


def evaluate_segment_evidence(entry: dict, level: str, profile_id: str = PROFILE_COFFEE_P8,
                              role: str = "FULL_STORY") -> dict:
    """M4判定。base sha==role原文 かつ hintなしなら最終sha==原文、hintありなら先頭200字==原文[:200]
    (+ cache_hits列挙)。roleはFULL_STORY(P8)/KP_EXPLANATION_EN(P3)=英語(最終style記録あり)。
    SUPPORT_JA(R2)=日本語は発音hint追記が無く、attempt側にstyle記録も無いため、base shaのみで判定する
    (最終送信styleはraw_usage_log/attemptsのinstruction_textで別途実測する)。"""
    override = get_profile(profile_id)["overrides"][role]
    exp_sha, exp_text = override["sha256"], override["text"]
    reasons = []
    prof = entry.get("style_profile") or {}
    base_ok = prof.get("style_base_sha256") == exp_sha
    if not base_ok:
        reasons.append("STYLE_BASE_SHA_MISMATCH_OR_MISSING")
    if role == ROLE_SUPPORT_JA:
        return {"pass": base_ok and not reasons, "base_sha_ok": base_ok, "hint_applied": False,
                "cache_hits": [], "final_style_record": None, "reasons": reasons}
    info = entry.get("en_pronunciation_resolver_info") or {}
    hint_applied = bool(info.get("hints_applied"))
    cache_hits = [h.get("surface", h) if isinstance(h, dict) else h for h in (info.get("cache_hits") or [])]
    final = _final_style_record(entry, level)
    final_ok = False
    if final is None:
        reasons.append("FINAL_STYLE_RECORD_MISSING")
    elif hint_applied:
        # 原文が200字未満(P3=141字)だとhead200にhint冒頭が混ざるため、==ではなくstartswithで判定する。
        final_ok = (str(final.get("head200") or "").startswith(exp_text[:200])) and (final.get("len", 0) >= len(exp_text))
        if not final_ok:
            reasons.append("FINAL_STYLE_HEAD200_MISMATCH_WITH_HINT")
    else:
        final_ok = final.get("sha256") == exp_sha
        if not final_ok:
            reasons.append("FINAL_STYLE_SHA_MISMATCH_NO_HINT")
    return {"pass": base_ok and final_ok and not reasons, "base_sha_ok": base_ok, "hint_applied": hint_applied,
            "cache_hits": cache_hits, "final_style_record": final, "reasons": reasons}


# ------------------------------------------------------------
# M3: Assembly前Gate(Family X runnerのstage_assemble内でのみ呼ぶ。共有assembleは不変)
# ------------------------------------------------------------
def _approved(approvals: dict, name: str, entry: dict) -> bool:
    approval = (approvals or {}).get(name)
    if not approval:
        return False
    canon = entry.get("canonical_text") or entry.get("text") or ""
    return approval.get("canonical_text_sha256") == sha256_text(canon)


def _gate_targets(profile_id: str, level: str, results: dict) -> list[tuple[str, str, dict | None]]:
    """(gate上の名前, role, entry or None)の列。KP英英解説はkey_phrases[rank]["explanation"]から取る。"""
    segments = (results or {}).get("segments") or {}
    targets = []
    for role in overridden_roles(profile_id):
        if level not in ROLE_LEVELS.get(role, ("a2", "b1b")):
            continue
        if role == ROLE_KP_EXPLANATION_EN:
            kps = (results or {}).get("key_phrases") or {}
            if not kps:
                targets.append(("kp_explanation(no key_phrases record)", role, None))
            for rank in sorted(kps, key=lambda k: int(k)):
                targets.append((f"kp{rank}_explanation", role, (kps[rank] or {}).get("explanation")))
            continue
        for name in ROLE_SEGMENTS.get(role, ()):
            targets.append((name, role, segments.get(name)))
    return targets


def m3_assembly_gate(profile_id: str, level: str, results: dict, approvals: dict | None = None) -> dict:
    """profile対象role各segmentについて:
      - style_profile.style_base_sha256 == そのroleの原文sha
      - FULL_STORY(Adv): style_prefix が原文で始まる / instruction_type != minimal_fallback
      - FULL_STORY(Std)/SUPPORT_JA: fallback_used が False(minimal instruction fallbackはroleのStyleを落とす)
      - local_rewrite_recovery なし
      - KP_EXPLANATION_EN: status OK
      - M4のFinal Style判定(英語role、hintあり/なし)
    を満たさない場合、record_human_approval(人間承認、canonical text sha一致)が無ければBLOCK。
    profile==default なら何もしない(PASS)。"""
    if profile_id == PROFILE_DEFAULT:
        return {"status": "PASS", "profile_id": profile_id, "checked": [], "blocked": [], "human_approved": []}
    checked, blocked, human_approved = [], [], []
    for name, role, entry in _gate_targets(profile_id, level, results):
        violations = []
        if entry is None:
            violations.append("NO_SEGMENT_RECORD")
        else:
            exp_text = get_profile(profile_id)["overrides"][role]["text"]
            if entry.get("status") not in (None, "OK") and role == ROLE_KP_EXPLANATION_EN:
                violations.append("KP_EXPLANATION_STATUS_NOT_OK")
            ev = evaluate_segment_evidence(entry, level, profile_id, role)
            violations.extend(ev["reasons"])
            if role == "FULL_STORY":
                if level == "b1b":
                    sp = entry.get("style_prefix")
                    if not (isinstance(sp, str) and sp.startswith(exp_text)):
                        violations.append("ADV_STYLE_PREFIX_NOT_P8_PREFIXED")
                    if entry.get("instruction_type") == "minimal_fallback":
                        violations.append("ADV_MINIMAL_FALLBACK")
                else:
                    if entry.get("fallback_used") is not False:
                        violations.append("STD_FALLBACK_USED_OR_UNKNOWN")
            elif role == ROLE_SUPPORT_JA:
                if entry.get("fallback_used") is not False:
                    violations.append("JA_FALLBACK_USED_OR_UNKNOWN")
            if entry.get("local_rewrite_recovery"):
                violations.append("LOCAL_REWRITE_RECOVERY")
        checked.append(name)
        if violations:
            if entry is not None and _approved(approvals, name, entry):
                human_approved.append({"segment": name, "violations": violations})
            else:
                blocked.append({"segment": name, "violations": violations})
    return {"status": "BLOCK" if blocked else "PASS", "profile_id": profile_id, "level": level,
            "checked": checked, "blocked": blocked, "human_approved": human_approved}


# ------------------------------------------------------------
# S2: plan段階のPronunciation Ledger hit計算(読み取りのみ、web lookup無効、課金0)
# ------------------------------------------------------------
def compute_ledger_hits(parts: dict, tts_safe_fn=None) -> dict:
    """Full Story各part(part1..3)について、現行Pronunciation Ledger(cache)のhintが
    P8へ追記されるかを事前計算する。augment_style_prefix_with_pronunciation を直接呼ぶ
    (resolve_and_augment_en_style_prefixの第1段と同一。低confidence再research[web]は呼ばない)。"""
    import er006_pronunciation_tts_injection_01 as en_injection
    out = {}
    for key in ("part1", "part2", "part3"):
        text = parts.get(key)
        if text is None:
            continue
        safe = tts_safe_fn(text) if tts_safe_fn else text
        augmented, hits = en_injection.augment_style_prefix_with_pronunciation(P8_TEXT, safe, min_confidence="medium")
        out[f"full_story_{key}"] = {
            "hint_applied": bool(hits),
            "cache_hits": [{"surface": h.get("surface"), "confidence": h.get("confidence")} for h in hits],
            "p8_len": len(P8_TEXT), "augmented_len": len(augmented),
            "augmented_startswith_p8": augmented.startswith(P8_TEXT),
        }
    return out
