# ASR-FLAP-T-PRODUCTION-WIRING-01 委任_02: 保存ASR記録(6,979転写)・Voice probe転写の Production判定replay(API 0・読取専用・副作用ファイル0)。
# 実行(cwd=データのあるmain working tree、コードはworktreeのProduction moduleをimport):
#   PYTHONUTF8=1 <venv python> <worktree>/docs/research/ASR-FLAP-T-PRODUCTION-WIRING-01/tools/flapt_replay_prod_02.py --code <worktree> --out <ev02 dir>
# 各転写を『現行の既存判定(classify_asr_match+同音救済)→ er109_xz_scope_01.decision(er109→Flap-T第3層)』で判定し、4条件で行単位に出力する:
#   S0 = Flap-T flag OFF(変更前と同じ判定)、S1 = 確認済みVoice(Aoede|fl)の出自あり、S2 = 出自なし、S3 = 未確認Voice(Puck|pro)
# 合格条件: S2/S3 は S0 と行単位で完全一致。S1 と S0 の差は Flap-T 行(latter/ladder, bertie/birdie 型)のみ。
import argparse, collections, glob, hashlib, json, os, sys

ap = argparse.ArgumentParser()
ap.add_argument("--code", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--data", default=".")
a = ap.parse_args()
CODE = os.path.abspath(a.code)
DATA = os.path.abspath(a.data)
sys.path.insert(0, CODE)
sys.path.insert(0, os.path.join(CODE, "docs", "research", "ASR-FLAP-T-EQUIVALENCE-TRIAL-01", "tools"))
os.chdir(CODE)          # import中はcwd=worktree(研究toolが sys.path.insert(0,'.') するため、データ側のcodeを拾わない)
import er021_en_asr_semantic_equivalence_production_01 as _er021
_er021.append_telemetry_log = lambda *a, **k: None          # 副作用ファイル0
import er109_stored_census_01 as c109
import er109_xz_scope_01 as xz
import er139_flapt_equivalence_01 as fe
import er139_flapt_provenance_01 as prov
import flapt_stored_census_01 as census
import warnings
warnings.simplefilter("ignore")
assert os.path.dirname(os.path.abspath(xz.__file__)) == CODE, xz.__file__      # Production codeはworktreeから読んでいること
assert os.path.dirname(os.path.abspath(fe.__file__)) == CODE

FL, PRO = "gemini-3.8-flash-lite-tts", "gemini-2.5-pro-preview-tts"
SCEN = {"S0_flag_off": None, "S1_aoede_fl_confirmed": ("Aoede", FL), "S2_no_provenance": "none", "S3_puck_pro_unconfirmed": ("Puck", PRO)}


def collect_rows():
    os.chdir(DATA)
    try:
        return _collect_rows()
    finally:
        os.chdir(CODE)


def _collect_rows():
    files = sorted(f for f in glob.glob("**/*tts_generation_results*.json", recursive=True) if not f.startswith(".venv"))
    rows = []
    for f in files:
        rows += c109.rows_from_results(f)
        rows += census.walk_rows(f)
    seen, uniq = set(), []
    for r in rows:
        k = (r["src"], r.get("attempt"), r["canonical"], r["asr"], r.get("azure"))
        if k in seen:
            continue
        seen.add(k)
        uniq.append(r)
    n = len(uniq)
    uniq += census.hr_rows()
    return uniq, n, len(files)


def judge_line(canon, txt, seg, scen):
    """既存判定→er109→Flap-T。戻り=行ラベル。"""
    ok, label = c109.current_pass(canon, txt, seg)
    if ok:
        return f"PASS:{label}"
    sink = {}
    d = xz.decision(canon, txt, sink=sink)
    if d is None:
        return "NG"
    return "ORTHO:" + ",".join(d.warning_labels or ("none",))


def run_scenario(name, spec, rows):
    lines = []
    flag_on = spec is not None
    fe.FLAP_T_EQUIVALENCE_ENABLED = flag_on
    prov.reset_for_tests()
    sha = "replay_" + hashlib.sha1(name.encode()).hexdigest()
    with xz.run_scope("X"):
        if isinstance(spec, tuple):
            prov.hydrate(sha, spec[0], spec[1], source="replay", transforms=[], transforms_known=True)
        with prov.judging_wav(sha if spec is not None else None):
            for r in rows:
                for which, txt in (("openai", r["asr"]), ("azure", r.get("azure"))):
                    if not txt:
                        continue
                    lines.append(f"{r['src']}|{r['seg']}|{r.get('attempt')}|{which}|{r['canonical'][:80]}|{txt[:80]}\t{judge_line(r['canonical'], txt, r['seg'], name)}")
    return lines


def main():
    rows, nres, nfiles = collect_rows()
    out = {"population": {"results_rows": nres, "hr_queue_rows": len(rows) - nres, "tts_results_files": nfiles}}
    res = {}
    for name, spec in SCEN.items():
        res[name] = run_scenario(name, spec, rows)
        # judging_wav memo はcontext内で共有されるため (canonical,text) は1回だけ評価される。これは本番の1 attempt = 1 wav と同じ。
    base = res["S0_flag_off"]
    out["lines"] = len(base)
    diffs = {}
    for name in ("S1_aoede_fl_confirmed", "S2_no_provenance", "S3_puck_pro_unconfirmed"):
        d = [(x, y) for x, y in zip(base, res[name]) if x != y]
        diffs[name] = d
        out[f"{name}_diff_rows"] = len(d)
    pairs = collections.Counter()
    flap_rows = []
    for x, y in diffs["S1_aoede_fl_confirmed"]:
        assert y.endswith("ORTHO:FLAP_T_EQUIVALENT"), (x, y)         # 差はFlap行のみ
        flap_rows.append({"before": x.split("\t")[1], "after": y.split("\t")[1], "row": x.split("\t")[0]})
        c, t = x.split("\t")[0].split("|")[-2:]
        pairs[(c.lower()[:40], t.lower()[:40])] += 1
    out["S1_flap_rows"] = flap_rows
    out["S1_flap_word_pairs_head"] = [[f"{k[0]} -> {k[1]}", v] for k, v in pairs.most_common(30)]
    out["S0_label_counts"] = dict(collections.Counter(x.split("\t")[1].split(":")[0] for x in base))
    out["pass_conditions"] = {"S2_equals_S0": out["S2_no_provenance_diff_rows"] == 0, "S3_equals_S0": out["S3_puck_pro_unconfirmed_diff_rows"] == 0,
                              "S1_diff_only_flap": all(r["after"].endswith("FLAP_T_EQUIVALENT") for r in flap_rows)}
    # ---- probe転写(writer/rider/title/tidal 等の反例+d綴り正例)
    probe = {"writer_rider": [], "positive": []}
    for fn, key in (("docs/research/ASR-FLAP-T-EQUIVALENCE-TRIAL-01/voice_probe_02.json", "voices"),
                    ("docs/research/ASR-FLAP-T-PRODUCTION-WIRING-01/voice_probe_03.json", "combos")):
        p = os.path.join(CODE, fn)
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding="utf-8"))
        for ck, cv in (d.get(key) or {}).items():
            if not isinstance(cv, dict):
                continue
            for prov_name, txt in (cv.get("writer_asr") or {}).items():
                probe["writer_rider"].append((ck, prov_name, txt))
            for item, iv in (cv.get("items") or {}).items():
                for prov_name, txt in (iv.get("asr") or {}).items():
                    probe["positive"].append((ck, item, prov_name, txt))
    fe.FLAP_T_EQUIVALENCE_ENABLED = True
    prov.reset_for_tests()
    wr_res = collections.Counter()
    with xz.run_scope("X"):
        prov.hydrate("probe_sha", "Aoede", FL, source="replay", transforms=[], transforms_known=True)
        with prov.judging_wav("probe_sha"):
            for ck, pn, txt in probe["writer_rider"]:
                if not txt:
                    continue
                canon = "writer"
                wr_res[judge_line(canon, txt, "probe", "wr")] += 1
            out["probe_writer_asr_transcripts"] = sum(1 for _ in probe["writer_rider"] if _[2])
            out["probe_writer_judgement"] = dict(wr_res)
            pos = collections.Counter()
            pos_examples = {}
            for ck, item, pn, txt in probe["positive"]:
                if not txt or item.startswith("the latter"):
                    continue
                lab = judge_line(item, txt, "probe", "pos")
                pos[(item, lab)] += 1
            out["probe_item_judgement"] = {f"{k[0]}|{k[1]}": v for k, v in sorted(pos.items())}
    os.makedirs(a.out, exist_ok=True)
    json.dump(out, open(os.path.join(a.out, "replay_prod_02.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(os.path.join(a.out, "replay_prod_02_line_diff_S1_vs_S0.txt"), "w", encoding="utf-8") as f:
        for x, y in diffs["S1_aoede_fl_confirmed"]:
            f.write(f"- {x}\n+ {y}\n")
    print(json.dumps({k: v for k, v in out.items() if k not in ("S1_flap_rows",)}, ensure_ascii=False, indent=1)[:6000])


if __name__ == "__main__":
    main()
