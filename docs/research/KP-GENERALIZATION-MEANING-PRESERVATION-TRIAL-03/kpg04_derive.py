# -*- coding: utf-8 -*-
"""N5(=N2+全候補sol検査)の保存結果から、N2(検査前)とN4(flag済み候補のみ検査)を『決定論に導出』する(API 0)。
根拠: N5のCHKは候補ごとに独立した判定で、N2の出力(GEN5/VER5後)を入力にする。item['flags']はCHK直前のN2状態で計算された値(凍結flag定義FLAGS_V1)。
  N2導出 = CHKによる変更(形・訳・戻し)を全て元に戻した状態 / N4導出 = flagが付いた候補だけCHKの変更を残し、それ以外はN2状態。
限界: CHKは7件前後のバッチで呼ばれるため、N4を実際に走らせた場合とはバッチ構成の違いによる判定ぶれがありうる(HARD6では実走のN4とN5導出を比較して差を報告)。
導出した結果ファイルには derived_from を記録する(実走結果と区別)。"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kpg04_llm as L


def state_before_check(item, log):
    """CHK直前(N2)の状態へ戻したitemを返す(コピー)。"""
    it = json.loads(json.dumps(item))
    rv = {x["span"]: x for x in (log.get("check_reverted_to_span") or [])}
    if it["source_span"] in rv:
        x = rv[it["source_span"]]
        it["display_form"], it["gloss_ja"] = x["from"], x.get("gloss_from") or it["gloss_ja"]
        it["reverted"] = False
        it["display_form_pre_revert"] = it["gloss_pre_revert"] = None
    elif it.get("display_form_pre_check"):
        it["display_form"] = it["display_form_pre_check"]
        it["gloss_ja"] = it.get("gloss_pre_check") or it["gloss_ja"]
    elif it.get("gloss_pre_check"):
        it["gloss_ja"] = it["gloss_pre_check"]
    it["display_form_pre_check"] = it["gloss_pre_check"] = None
    it["check"] = None
    return it


def derive(n5, mode):
    """mode: 'N2'(全て元に戻す) / 'N4'(flag済みはCHK結果を残す)。"""
    log = n5["log"]
    items = []
    for it in n5["items"]:
        if mode == "N4" and it.get("flags"):
            items.append(json.loads(json.dumps(it)))
        else:
            items.append(state_before_check(it, log))
    out = {"items": items, "log": {"stages": [s for s in log["stages"] if s["stage"] != "CHK5"] if mode == "N2" else log["stages"], "tag": mode + "(derived)",
           "derived_from": "N5", "note": "N5の保存結果から決定論に導出(kpg04_derive.py)"}, "case": n5.get("case"), "arm": mode, "derived_from": "N5"}
    out["cost_jpy"] = round(sum(s["cost_jpy"] for s in out["log"]["stages"]), 3)
    out["sec"] = n5.get("sec")
    return out


def derive_all(cases, modes=("N2", "N4"), overwrite=False):
    d = os.path.join(L.WORK, "results")
    done = []
    for cid in cases:
        p = os.path.join(d, f"{cid}__N5.json")
        if not os.path.exists(p):
            continue
        n5 = json.load(open(p, encoding="utf-8"))
        for m in modes:
            q = os.path.join(d, f"{cid}__{m}.json")
            if os.path.exists(q) and not overwrite:
                continue
            json.dump(derive(n5, m), open(q, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            done.append((cid, m))
    return done


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("--cases", required=True); ap.add_argument("--modes", default="N2,N4"); ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args()
    print(derive_all(a.cases.split(","), tuple(a.modes.split(",")), a.overwrite))
