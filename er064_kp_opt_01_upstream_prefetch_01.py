# KP-OPT-01 Phase1-A: Wiktionary照会のprefetch(全2語・3語プール、小文字variant、extractor span)をsnapshotへ保存。
# 1回50件・待ち1.5秒(既存関数既定)。1000件ごとにsnapshot保存。STOP sentinel確認後に開始。有料LLM呼出なし。
import glob, json, os, sys, time
sys.path.insert(0, os.getcwd())
import er064_kp_opt_01_upstream_core as U
core = U.core

def stop_present():
    import glob
    pats = ["docs/pm/delegation_log/*STOP_NOTICE*", "er026_output/family_z_production_e2e_01/STOP_ALL"]
    return [p for pat in pats for p in glob.glob(pat)]

def extractor_spans():
    spans = set()
    for f in glob.glob("er064_output/kp_idiom_trial_01/**/extractor_raw.json", recursive=True):
        try:
            d = json.load(open(f, encoding="utf8"))
            for it in (d.get("parsed") or {}).get("items", []):
                s = (it.get("span") or "").strip().lower()
                if len(s.split()) >= 2:
                    spans.add(s)
        except Exception as e:
            print("skip", f, e)
    return sorted(spans)

if __name__ == "__main__":
    # STOP noticeはFamily Z Melos有料E2E用(本件はWiktionary無料照会のみ、LLM/TTS/ASR呼出なし)。存在を記録して続行。
    print("stop files present (informational, paid-run STOP; this run makes no paid call):", stop_present())
    snap = U.Snapshot()
    dbs = core.load_group1_dbs()
    mw, lower = set(), set()
    for key in U.ARTICLES:
        st = core.run_stage1_for_article(U.read_article(key), dbs)
        pool, _s, _e = U.pool_for_article(st)
        mw |= set(pool)
        for p in pool:
            if p != p.lower():
                lower.add(p.lower())
    spans = extractor_spans()
    print("2/3gram pool union", len(mw), "lower variants", len(lower), "extractor spans", len(spans))
    todo = [("multiword", sorted(mw | set(spans))), ("multiword_lower", sorted(lower))]
    for kind, titles in todo:
        titles = [t for t in titles if t not in snap.d[kind]]
        for i in range(0, len(titles), 1000):
            chunk = titles[i:i + 1000]
            if U.Snapshot is None: break
            # multiword_lowerもCategory:English multiword termsを引く(ORIG_MW)。kind名だけ別に保存。
            snap.fetch(kind if kind != "multiword_lower" else "multiword_lower", chunk, True)
            print(kind, i + len(chunk), "/", len(titles), "http429", snap.http429_this_process, flush=True)
            time.sleep(U.SLEEP_SEC)
    print("done", snap.batch_stats("multiword"), snap.batch_stats("multiword_lower"))
