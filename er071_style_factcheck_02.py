# -*- coding: utf-8 -*-
"""FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 委任_02 (OF-X10): Std/Adv各segmentの承認Style vs 引継ぎ元(e_tone_01等)の実style vs
main runner `coffee_n01_r2_p3`の解決styleを突き合わせる(API 0円。style解決関数の直接呼出+results読み取りのみ)。"""
import hashlib
import json
import sys

import er003_v1_n3_01_tts_generate as n3_tts
import er019_family_x_style_profile_01 as sp
import er033_tts_flash_lite_family_x_styles_01 as fl

PROFILE = "coffee_n01_r2_p3"
T = "../eigo-radio-tone/er019_output/family_x_audio_production_wiring_01/coffee_prices__run_e_tone_01/"
V5 = "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_v5_ms_01/"
OUT = "er071_output/m2p0_n01_production_wiring_01/completion_02/ADV_STYLE_FACTCHECK_02.md"
E1 = "calm, composed news anchor; steady and unhurried, clear and natural."  # er057_tone_trial_tts_gen_01.py SPECS E/E1(Advanced Preview)


def sha(s):
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()[:12] if s else "-"


def recorded_style(entry):
    st = entry.get("style_prefix")
    if isinstance(st, dict):
        return None, st.get("sha256"), st.get("head200")
    return st, (hashlib.sha256(st.encode("utf-8")).hexdigest() if st else None), (st or "")[:200]


def main_style_b1b(role):
    base = lambda r: fl.FAMILY_X_ROLE_STYLE_EN.get(r)
    v = sp.resolve_role_style(PROFILE, role, "b1b", base)
    if role in ("PREVIEW", "COMMENT"):
        v = v or n3_tts.B1_PREVIEW_STYLE_PREFIX_CALM
    return v


def main_style_a2(label):
    base = lambda r: fl.FAMILY_X_ROLE_STYLE_EN.get(r)
    base_slow = lambda r: (base(r) + "\n" + n3_tts.A2_SLOWER_PACE_INSTRUCTION.strip()) if base(r) else None
    if label == "topic_intro":
        return sp.resolve_role_style(PROFILE, "TOPIC_INTRO", "a2", base)
    if label == "in_one_line":
        return sp.resolve_role_style(PROFILE, "IN_ONE_LINE", "a2", base_slow)
    if label == "japanese_title":
        return fl.FAMILY_X_ROLE_STYLE_JA
    if label in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
        return sp.resolve_role_style(PROFILE, sp.ROLE_SUPPORT_JA, "a2", lambda _r: fl.FAMILY_X_ROLE_STYLE_JA)
    return None


# 承認Style(CURRENT_SPEC L2620-2625 + 可変segment Role Style節)。値の出典を併記。
APPROVED_B1B = {
    "topic_intro": (fl.FAMILY_X_ROLE_STYLE_EN["TOPIC_INTRO"], "可変segment Role Style節: EN TOPIC_INTRO=E2(現行定数FAMILY_X_ROLE_STYLE_EN)。Coffee限定のIntro A5/B5は固定Master phrase(welcome/preview_intro)用"),
    "preview": (E1, "L2620: Advanced Preview=E1(er057_tone_trial_tts_gen_01.py SPECS['E']['E1'])"),
    "comment": (fl.FAMILY_X_ROLE_STYLE_EN["COMMENT"], "可変segment Role Style節: PREVIEW/COMMENTはE2未検証のためE0のまま(=現行定数)。Coffee限定のComment Style決定記述はCURRENT_SPECに無い"),
    "in_one_line": (fl.FAMILY_X_ROLE_STYLE_EN["IN_ONE_LINE"], "L2620: In One Line=既存承認Style(=FAMILY_X_ROLE_STYLE_EN['IN_ONE_LINE']=E2)"),
}
APPROVED_A2 = {
    "topic_intro": (fl.FAMILY_X_ROLE_STYLE_EN["TOPIC_INTRO"], "同上(E2)"),
    "japanese_title": (fl.FAMILY_X_ROLE_STYLE_JA, "可変segment Role Style節: JA=J3(japanese_titleも対象、W3)"),
    "preview": (sp.R2_TEXT, "L2624(C): Standard Preview/Comment1-4=R2"),
    "in_one_line": (fl.FAMILY_X_ROLE_STYLE_EN["IN_ONE_LINE"] + "\n" + n3_tts.A2_SLOWER_PACE_INSTRUCTION.strip(), "既存承認Style(E2)+Standardの既承認減速instruction"),
}


def main():
    rows = ["# ADV_STYLE_FACTCHECK_02 (OF-X10、API 0円、2026-10-13)", "",
            "管理ID: FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 委任_02。TTSなし。`er071_style_factcheck_02.py`で生成(style解決関数の直接呼出+results読取)。", "",
            "判定ルール(Fable既定): (i)元run(e_tone_01)のstyleが承認Styleと一致→seed+引継ぎ / (ii)不一致かつmain runner `coffee_n01_r2_p3`の解決styleが承認Styleと一致→正式経路で再生成 / (iii)両方不一致→STOP(approved-but-unwired)。", ""]
    decisions = {}
    for level, results_path, approved, mainfn in (
            ("b1b(Adv)", T + "b1b/audit/tts_generation_results.json", APPROVED_B1B, lambda l: main_style_b1b(
                {"topic_intro": "TOPIC_INTRO", "preview": "PREVIEW", "in_one_line": "IN_ONE_LINE"}.get(l, "COMMENT"))),
            ("a2(Std)", T + "a2/audit/tts_generation_results.json", APPROVED_A2, main_style_a2)):
        res = json.load(open(results_path, encoding="utf-8"))
        rows += [f"## {level}", "", "| segment | 承認Style(出典) | 承認sha | e_tone_01実style sha | e_tone一致 | main解決style sha | main一致 | 判定 |", "|---|---|---|---|---|---|---|---|"]
        labels = (["topic_intro", "preview", "comment_1", "comment_2", "comment_3", "comment_4", "in_one_line"] if level.startswith("b1b")
                  else ["topic_intro", "japanese_title", "preview", "comment_1", "comment_2", "comment_3", "comment_4", "in_one_line"])
        for l in labels:
            key = l if l in approved else ("comment" if ("comment" in approved and l.startswith("comment")) else "preview")
            appr, src = approved[key]
            e = res["segments"].get(l) or {}
            rec_text, rec_sha, _ = recorded_style(e)
            tone_ok = (rec_sha == hashlib.sha256(appr.encode("utf-8")).hexdigest())
            m = mainfn(l)
            main_ok = (m == appr)
            if tone_ok:
                dec = "(i) seed+引継ぎ"
            elif main_ok:
                dec = "(ii) 正式経路で再生成"
            else:
                dec = "(iii) STOP: approved-but-unwired"
            decisions[(level, l)] = dec
            rows.append(f"| {l} | `{appr[:50]}...` ({src}) | `{sha(appr)}` | `{(rec_sha or '-')[:12]}` | {'一致' if tone_ok else '不一致'} | `{sha(m)}` | {'一致' if main_ok else '不一致'} | {dec} |")
        rows.append("")
    rows += ["## e_tone_01実styleの文言(参考)", ""]
    for lv in ("b1b", "a2"):
        res = json.load(open(T + f"{lv}/audit/tts_generation_results.json", encoding="utf-8"))
        for l in ("topic_intro", "preview", "comment_1", "in_one_line", "japanese_title"):
            if l in res["segments"]:
                t, s, h = recorded_style(res["segments"][l])
                rows.append(f"- {lv}/{l}: sha `{(s or '-')[:12]}` / `{(t or h or '')[:110]!r}`")
    rows += ["", "## main runner (coffee_n01_r2_p3) 解決style(参考)", ""]
    rows.append(f"- b1b PREVIEW/COMMENT: `{main_style_b1b('PREVIEW')!r}`  (E1は未配線: PREVIEW定数は'calm, conversational')")
    rows.append(f"- b1b TOPIC_INTRO: `{main_style_b1b('TOPIC_INTRO')!r}`")
    rows.append(f"- b1b IN_ONE_LINE: `{main_style_b1b('IN_ONE_LINE')!r}`")
    open(OUT, "w", encoding="utf-8").write("\n".join(rows) + "\n")
    print("\n".join(rows))
    return decisions


if __name__ == "__main__":
    main()
