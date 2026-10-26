# -*- coding: utf-8 -*-
"""KP-PHRASE7-WORD5-PRODUCTION-01 委任_02: evidence用の新規run dirを作る(既存run dirの入力だけを複製。KP/文法/ログ等の出力は複製しない)。
公開済み/進行中runには触れない(コピー元は読取のみ)。API 0。"""
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
NEW = "run_kp75_ev_01"


def cp(src, dst):
    if not os.path.exists(src):
        raise SystemExit(f"コピー元がありません: {src}")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.isdir(src):
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)


def x(slug, old_src, old_out):
    s_old = f"{ROOT}/er019_output/{slug}/{old_src}"
    s_new = f"{ROOT}/er019_output/{slug}/{NEW}"
    o_old = f"{ROOT}/er019_output/family_x_audio_production_wiring_01/{slug}__{old_out}"
    o_new = f"{ROOT}/er019_output/family_x_audio_production_wiring_01/{slug}__{NEW}"
    for p in (s_new, o_new):
        if os.path.exists(p):
            raise SystemExit(f"既に存在: {p}")
    for lv in ("a2", "b1b"):
        cp(f"{s_old}/{lv}/article.md", f"{s_new}/{lv}/article.md")
    cp(f"{o_old}/a2/a2_support_texts.json", f"{o_new}/a2/a2_support_texts.json")
    cp(f"{o_old}/b1b/b1_support_texts.json", f"{o_new}/b1b/b1_support_texts.json")
    for lv in ("a2", "b1b"):
        cp(f"{o_old}/{lv}/parts.json", f"{o_new}/{lv}/parts.json")
    cp(f"{o_old}/audit", f"{o_new}/audit")
    return o_new


def y():
    old = f"{ROOT}/er121_output/family_y_production_01/redelivery_fee/run_kpbf_ev_01"
    new = f"{ROOT}/er121_output/family_y_production_01/redelivery_fee/{NEW}"
    if os.path.exists(new):
        raise SystemExit(f"既に存在: {new}")
    for name in ("audit", "text", "translate", "provenance.json", "voice_assignment.json"):
        cp(f"{old}/{name}", f"{new}/{name}")
    return new


def z():
    old = f"{ROOT}/er026_output/family_z_production_e2e_01/melos/run_kpbf_ev_01"
    new = f"{ROOT}/er026_output/family_z_production_e2e_01/melos/{NEW}"
    if os.path.exists(new):
        raise SystemExit(f"既に存在: {new}")
    cp(f"{old}/writer", f"{new}/writer")
    cp(f"{old}/voice_assignment.json", f"{new}/voice_assignment.json")
    return new


if __name__ == "__main__":
    what = sys.argv[1:] or ["x_uk", "x_ai", "y", "z"]
    out = {}
    if "x_uk" in what:
        out["x_uk"] = x("uk_train_speaker_playback", "run_kprescue_ev_01", "run_kprescue_ev_01")
    if "x_ai" in what:
        out["x_ai"] = x("ai_island_temple", "run_kpbf_ev_01", "run_kpbf_ev_01")
    if "y" in what:
        out["y"] = y()
    if "z" in what:
        out["z"] = z()
    for k, v in out.items():
        print(k, v)
