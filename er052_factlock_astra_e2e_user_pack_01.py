# -*- coding: utf-8 -*-
"""FACTLOCK-ASTRA-E2E-TRIAL-01 委任_13: ユーザー提示パック生成(API 0、読取専用)。
9テーマの 旧腕/新腕 の最終本文を対で並べる。JA=R2最終(STOP時は最後の不採用本文と明記)、EN=Advanced/Standard最終。
使い方: .venv/Scripts/python.exe -X utf8 er052_factlock_astra_e2e_user_pack_01.py --root <runs>
"""
from __future__ import annotations

import argparse
import glob
import os
import sys

import er052_factlock_astra_e2e_runner_01 as R
import er052_factlock_astra_e2e_aggregate_01 as A

ORDER = ["meta", "hormuz", "space_weapons", "small_bag", "byd_recall", "central_bank_mortgage", "openai_copyright", "semiconductor_earnings", "streaming_price"]


def read(p):
    return R.rdt(p) if os.path.exists(p) else None


def ja_text(ad, arm, st):
    """(本文, 注記)。採用本文=ja_writer/revision2.md。STOP等で無ければ audit/rejected_*.md の最後(更新時刻最新)。"""
    p = f"{ad}/ja_writer/revision2.md"
    stg = "new_r2" if arm == "new" else "old_ja"
    if R.stage_ok(p):
        note = "JA最終(R2)"
        if arm == "new" and st.get("new_r2") != "done":
            note += f"(stage={st.get('new_r2')})"
        return read(p), note
    rej = sorted(glob.glob(f"{ad}/ja_writer/audit/rejected_*.md") + glob.glob(f"{ad}/new_writer/rejected*.md"), key=os.path.getmtime)
    rej = [x for x in rej if not x.endswith("_must_fix.md")]
    if rej:
        return read(rej[-1]), f"JA STOP: 採用されなかった最後の本文(`{os.path.relpath(rej[-1], ad)}`、stage={st.get(stg) or st.get('new_r0')})"
    stops = sorted(glob.glob(f"{ad}/new_writer/*_stop.json"), key=os.path.getmtime)
    if stops:      # 新腕のR0/R1段STOP: rejected_text を採用されなかった本文として提示
        d = R.rj(stops[-1])
        if d.get("rejected_text"):
            return d["rejected_text"], f"JA STOP(新腕{d.get('stage')}段): 採用されなかった最後の本文(`{os.path.relpath(stops[-1], ad)}` の rejected_text)"
    # 新腕でR2前にSTOPした場合などは、最も新しい中間成果物
    for cand in ("new_writer/r1.p1.md", "new_writer/r0.md"):
        if os.path.exists(f"{ad}/{cand}"):
            return read(f"{ad}/{cand}"), f"JA未完(STOP/未実行): 最後の中間成果物 `{cand}`"
    return None, "本文なし"


def en_text(ad, dname, level, status):
    p = f"{ad}/{dname}/article.md"
    if R.stage_ok(p):
        return read(p), f"EN {level} 最終(status={status})" + ("" if status == "done" else ": **STOP記録後に残る成果物**(採用不可の可能性あり)")
    rej = sorted(glob.glob(f"{ad}/{dname}/audit/rejected_*.md"), key=os.path.getmtime)
    rej = [x for x in rej if not x.endswith("_must_fix.md")]
    if rej:
        return read(rej[-1]), f"EN {level} STOP: 採用されなかった最後の本文(`{os.path.relpath(rej[-1], ad)}`)"
    dc = sorted(glob.glob(f"{ad}/{dname}/audit/deviation_checks/*_attempt*.json"), key=os.path.getmtime)
    hint = f"。被検EN本文は `{os.path.relpath(dc[-1], ad)}` のprompt内にのみ残る(採用成果物としては未保存)" if dc else ""
    return None, f"EN {level} 採用本文なし(status={status}){hint}"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    a = ap.parse_args(argv)
    os.chdir(R.HERE)
    root = a.root
    ja_out = ["# USER_PACK_E2E_01: 旧腕JA vs 新腕JA(Astra R2)最終本文の対(9テーマ)", "",
              "旧腕=Luna Writer(Production相当経路)、新腕=Fact Lock+gpt-6-astra(R0→Astra R1→R2)。腕名は開示(X系列採用済み)。STOPの場合は『最後の採用されなかった本文』と明記。",
              "本文は自動抽出のまま。判定・推奨は含まない。", ""]
    en_out = ["# USER_PACK_E2E_EN_01: 旧腕EN vs 新腕EN(Advanced/Standard)最終本文の対(9テーマ)", "",
              "旧腕=Production相当、新腕=Fact Lock+Astra JA後のEN生成。STOPの場合は採用されなかった本文と明記。判定・推奨なし。", ""]
    for i, t in enumerate(ORDER, 1):
        if not os.path.isdir(f"{root}/{t}"):
            continue
        topic = (read(f"{root}/{t}/shared/topic.txt") or "").strip()
        ja_out += [f"## {i}. {t}", "", f"topic: {topic}", ""]
        en_out += [f"## {i}. {t}", "", f"topic: {topic}", ""]
        for arm, label in (("old", "旧腕"), ("new", "新腕")):
            ad = f"{root}/{t}/{arm}"
            if not os.path.isdir(ad):
                ja_out += [f"### {label}: (未実行)", ""]
                en_out += [f"### {label}: (未実行)", ""]
                continue
            st = {}
            for e in R.ArmState(ad).events():
                if e["ev"] in ("stage_done", "stage_stop", "stage_failed"):
                    st[e["stage"]] = e["ev"][6:]
                elif e["ev"] == "reset":
                    for s in e["stages"]:
                        st.pop(s, None)
            body, note = ja_text(ad, arm, st)
            ja_out += [f"### {label} JA — {note}", "", "```text", (body or "(なし)").strip(), "```", ""]
            for level, dname, short in A.LEVELS:
                stg = f"new_en_{short}" if arm == "new" else f"old_{short}"
                body, note = en_text(ad, dname, level, st.get(stg, "-"))
                cj = A._safe(f"{ad}/checker/{level}.json") or {}
                note += f" / Checker: {cj.get('final_state', '-')}"
                en_out += [f"### {label} EN {level} — {note}", "", "```text", (body or "(なし)").strip(), "```", ""]
    R.wt(f"{root}/USER_PACK_E2E_01.md", "\n".join(ja_out) + "\n")
    R.wt(f"{root}/USER_PACK_E2E_EN_01.md", "\n".join(en_out) + "\n")
    print("pack written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
