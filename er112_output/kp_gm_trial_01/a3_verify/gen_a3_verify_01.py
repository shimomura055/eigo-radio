# -*- coding: utf-8 -*-
"""A-3 v3 追加検証(委任_04) 生成段: 正常KP25件(既存production run由来)を 現行Prompt(a1gE0相当) vs A-3 v3(a1gE3相当)で各2回、説明1callのみ生成。
DEV専用。Production不触(er112 dispatcherをinstallして説明段だけ呼ぶ)。台帳=a3_verify/paid_calls.jsonl、上限20円。"""
import json, sys, time, hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT = Path(r"C:\Users\tensh\eigo-radio")
sys.path.insert(0, str(ROOT))
import er112_kp_gm_trial_01 as tr
V = ROOT / "er112_output/kp_gm_trial_01/a3_verify"
tr.LEDGER = V / "paid_calls.jsonl"
CAP = 20.0
SEL = {  # (run dir relative) -> list of key used_form(lower)
 "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01": ["off the hook", "jump to conclusions", "shock someone's wallet"],
 "er019_output/family_x_audio_production_wiring_01/middle_east_yemen_saudi__run_mey_02": ["take the wheel", "mix up", "refueling support", "all the same kind"],
 "er019_output/family_x_audio_production_wiring_01/paycheck_personality__run_pp_01": ["play a part", "turn out", "former self", "small positive link"],
 "er019_output/family_x_audio_production_wiring_01/paycheck_personality__run_pp_02": ["in the spotlight", "come first", "hold on"],
 "er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01": ["think up", "bring in"],
 "er019_output/family_x_audio_production_wiring_01/ig_nobel_2026__run_nws_02": ["leap into action"],
 "er019_output/family_x_audio_production_wiring_01/boredom_aggression__run_bape_01": ["apply one's findings"],
 "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_jre_01": ["time lag", "behind price increases"],
 "er026_output/family_z_production_e2e_01/the_open_window/run_e2e_01": ["take turns", "letter of introduction"],
 "er026_output/family_z_production_e2e_01/the_open_window/run_sf_prod_01": ["at a moment's notice"],
 "er026_output/family_z_production_e2e_01/melos/run_kgcpw_z_01": ["execution bell", "abandon"],
}
def build():
    units = []
    for run, keys in SEL.items():
        p = ROOT / run / "b1b" / "key_phrases" / "keywords_canonicalized.json"
        if not p.exists(): p = ROOT / run / "key_phrases" / "b1b" / "keywords_canonicalized.json"
        m = json.loads(p.read_text(encoding="utf-8"))
        items = []
        for it in m["items"]:
            if it["key_phrase"].lower() in keys:
                items.append(dict(rank=it["rank"], display_phrase=it["display_phrase"], key_phrase=it["key_phrase"], used_form=it["used_form"],
                                  gloss=it.get("japanese_gloss"), source_sentence=it.get("source_sentence"), prod_expl=None))
        assert len(items) == len(keys), (run, keys, [i["key_phrase"] for i in items])
        fam = "X" if "er019_output" in run else "Z"
        units.append(dict(unit_id=f"{fam}_" + run.split("/")[-2] + "__" + run.split("/")[-1], run=run, family=fam, items=items, article_text=""))
    return units
def job(arm, rep, u):
    f = V / "runs" / arm / f"rep{rep}" / (u["unit_id"] + ".json")
    if f.exists(): return json.loads(f.read_text(encoding="utf-8"))
    if (V / "STOP").exists() or tr.stop_present(): return None
    if tr.ledger_total_jpy(("gen", "judge")) >= CAP: return None
    c = tr.ArmCtx(arm, rep, u["unit_id"], u["article_text"]); c.dir = None
    tr._TL.ctx = c
    rec = {}
    try:
        tr._expl_stage(dict(article_text="", level="b1b"), [dict(i) for i in u["items"]], rec)
    finally:
        tr._TL.ctx = None
    out = dict(arm=arm, rep=rep, unit_id=u["unit_id"], family=u["family"], items=u["items"], expl=rec.get("expl"), expl_error=rec.get("expl_error"), retried=rec.get("expl_retried"))
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out
if __name__ == "__main__":
    units = build()
    (V / "units_a3verify.json").write_text(json.dumps(units, ensure_ascii=False, indent=1), encoding="utf-8")
    print("units", len(units), "items", sum(len(u["items"]) for u in units))
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        tr.install_dev_patches()
        h0 = tr.prod_hashes()
        jobs = [(a, r, u) for r in (1, 2) for a in ("a1gE0", "a1gE3") for u in units]
        with ThreadPoolExecutor(6) as ex:
            res = list(ex.map(lambda x: job(*x), jobs))
        print("done", sum(1 for r in res if r), "/", len(jobs), "cost", tr.ledger_total_jpy())
        assert h0 == tr.prod_hashes()
        (V / "production_hash_unchanged.json").write_text(json.dumps(dict(start=h0, end=tr.prod_hashes(), unchanged=h0 == tr.prod_hashes()), indent=1), encoding="utf-8")
