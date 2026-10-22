# -*- coding: utf-8 -*-
"""第3巡 有料生成(Trial専用): TTS入力側の読み制御。
 arm R=綴り置換(Reicher->Riker方式。TTS入力と比較対象テキストを置換語にする方式と同じ考え方)、arm H=styleへ発音ヒント注入(本文は原綴りのまま。
 既存の注入形式 er006_pronunciation_tts_injection_01.apply_precomputed_hints_to_style_prefix を読取のみで利用)。
 供給元はA/B階層(取得済み)に限る。ESTIMATED/取得なしの語(Toteme/Zabelina/Melos/Canele)は供給しない。
 誤読対照(wrong供給)各語1本x2 arm。無供給対照(alt_short)のみ追加生成。他の無供給対照は第2巡r2のtake1/take2音声を再利用(追加生成なし)。
 Production runner/Review Lock/Store/HR queue/attempt_historyは経由せず書込まない(実行前後sha256+行数をassert)。1回だけ起動(再起動しない)。"""
import json, os, sys
sys.path.insert(0, os.getcwd())
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import er100_pnps_stage2_trial_01_r2_gen as G
import er006_pronunciation_tts_injection_01 as INJ

R3 = Path("er100_output/pnps_stage2_trial_01/r3")
G.AUD = R3 / "audio"
G.LEDGER = R3 / "paid_calls.jsonl"
G.GUARD_STOP = 52.0     # 本巡Guardrail60の手前で新規有料呼出を止める(ASR分を加味)
R2 = Path("er100_output/pnps_stage2_trial_01/r2")
SEGS = {s["id"]: s for s in json.load(open(R2 / "plan.json", encoding="utf-8"))["segments"]}
ALT_SHORT = "Vogue showed small pouches from Prada and large shoulder bags from Altuzarra."
# 供給発音(tier: A=Wikipedia本人記事 / B=報道・ファッション媒体の一致)
SUPPLY = {
    "khaite": {"orig": "Khaite", "tier": "B", "src": "nylon.com fashion-designer-pronunciation-guide(quoted 'kate'、1媒体)", "resp": "Kate", "hint": "kate", "wrong_resp": "Kite", "wrong_hint": "kite"},
    "meink": {"orig": "Meink", "tier": "A", "src": "en.wikipedia.org/wiki/Troy_Meink(/miːnk/ MEENK、本人記事)", "resp": "Meenk", "hint": "meenk", "wrong_resp": "Mink", "wrong_hint": "mink"},
    "altuzarra": {"orig": "Altuzarra", "tier": "B", "src": "businessinsider/nylon/elle.com.au/herworld 他5件一致(ahl-too-ZAH-rah)", "resp": "Altoozahra", "hint": "ahl-too-ZAH-rah", "wrong_resp": "Altuzairah", "wrong_hint": "al-tuh-ZAIR-ah"},
}
BASE = [("s09", "khaite"), ("s12", "khaite"), ("s13", "khaite"), ("s16", "khaite"), ("s02", "meink"), ("s03", "meink"), ("s17", "altuzarra"), ("alt_short", "altuzarra")]
CONTROL = [("s09", "khaite"), ("s02", "meink"), ("alt_short", "altuzarra")]


def seg_text(sid):
    return ALT_SHORT if sid == "alt_short" else SEGS[sid]["text"]


def replace_word(text, orig, rep):
    import re
    return re.sub(r"\b" + re.escape(orig) + r"\b", rep, text, count=0)


def build_items(settings):
    items = []

    def add(sid, w, arm, wrong, take_tags):
        S = SUPPLY[w]
        canon = seg_text(sid)
        if arm == "R":
            rep = S["wrong_resp"] if wrong else S["resp"]
            ttext = replace_word(canon, S["orig"], rep)
            it = {"id": f"{sid}_{w}_R{'W' if wrong else ''}", "canon": ttext, "tts_text": ttext, "words": [rep.lower()], "word": w, "orig_canon": canon, "supplied": rep}
            st = dict(settings)
        else:
            hint = S["wrong_hint"] if wrong else S["hint"]
            style = INJ.apply_precomputed_hints_to_style_prefix(settings["style_text"], [{"surface": S["orig"], "pronunciation_hint": hint}])
            it = {"id": f"{sid}_{w}_H{'W' if wrong else ''}", "canon": canon, "tts_text": canon, "words": [w], "word": w, "orig_canon": canon, "supplied": hint}
            st = dict(settings); st["style_text"] = style
        it.update(arm=arm, wrong=wrong, sid=sid, tier=S["tier"], family="X")
        for t in take_tags:
            items.append((it, st, t))

    for sid, w in BASE:
        for arm in ("R", "H"):
            add(sid, w, arm, False, ("t1", "t2"))
    for sid, w in CONTROL:
        for arm in ("R", "H"):
            add(sid, w, arm, True, ("t1",))
    # 無供給の対照: alt_shortのみ新規(他は第2巡音声を再利用)
    n = {"id": "alt_short_altuzarra_N", "canon": ALT_SHORT, "tts_text": ALT_SHORT, "words": ["altuzarra"], "word": "altuzarra", "orig_canon": ALT_SHORT, "supplied": None,
         "arm": "N", "wrong": False, "sid": "alt_short", "tier": None, "family": "X"}
    items += [(n, dict(settings), "t1"), (n, dict(settings), "t2")]
    return items


def main():
    settings = json.load(open(R2 / "plan.json", encoding="utf-8"))["tts_settings"]
    items = build_items(settings)
    print(len(items), "audio planned")
    before = G.protect_snapshot()
    json.dump(before, open(R3 / "protect_before.json", "w"), indent=1)
    out = []

    def work(x):
        it, st, tag = x
        r = G.process(it, st, tag)
        for k in ("arm", "wrong", "sid", "tier", "supplied", "orig_canon"):
            r[k] = it[k]
        return r

    with ThreadPoolExecutor(max_workers=3) as ex:
        for r in ex.map(work, items):
            out.append(r)
            print(r["id"], r["take"], r.get("sec"), r.get("api_scope"), r.get("error", ""), round(G.ledger_total(), 2), flush=True)
            json.dump(out, open(R3 / "gen.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    after = G.protect_snapshot()
    json.dump(after, open(R3 / "protect_after.json", "w"), indent=1)
    assert before == after, "保護対象ファイルが変化した"
    print("PROTECTED_UNCHANGED ledger total jpy", round(G.ledger_total(), 3))


if __name__ == "__main__":
    main()
