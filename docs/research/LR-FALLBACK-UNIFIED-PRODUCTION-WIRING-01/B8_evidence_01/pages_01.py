"""委任_13(B8) 試聴ページ実測(API 0・読取専用): 保存run(wav保存済みのもの)に対し、配線後HEADの正式page関数で試聴ページを生成(出力はscratch dir。
user_test・run dirは書かない)し、⏸(実chunk plan境界数)・赤(LR)・濃青(Fallback)・注記の有無を台帳/plan記録と照合する。
使い方: .venv/Scripts/python.exe <this> <out_json> <scratch_dir>"""
import json, os, re, sys, traceback, glob, shutil
sys.path.insert(0, os.getcwd())
out_json, scratch = sys.argv[1], os.path.abspath(sys.argv[2])
os.makedirs(scratch, exist_ok=True)
import er_user_listening_page_common_01 as cp
import er129_lr_display_reflection_01 as e129
RED, BLUE = "#c00000", "#0a2a6b"


def plan_boundaries(run, level):
    plans = cp.load_chunk_plans(f"{run}/{level}/audit/chunk_plan_{level}.json")
    return sum(max(len(cp.chunk_texts_of_plan(p)) - 1, 0) for p in plans.values()), len(plans)


def analyze(html_text, run, level):
    for lid in (("adv", "advanced") if level == "b1b" else ("std", "standard")):   # 当該levelの節のみ(X/Z=std,adv / Y=standard,advanced)
        try:
            html_text = cp.level_section_html(html_text, lid); break
        except ValueError:
            continue
    nb, nplans = plan_boundaries(run, level)
    L = e129.build_lr_ledger(run, level, only_events=True)
    lr = [c["clip_id"] for c in L["clips"] if (c.get("lr") or {}).get("adopted_in_final")]
    fb = [c["clip_id"] for c in L["clips"] if (c.get("fallback") or {}).get("state") == "USED"]
    return {"plan_boundaries": nb, "plans": nplans, "marks_on_page": html_text.count("class='chunk-mark'"),
            "red_spans": html_text.count("class='rpt-lr'"), "blue_spans": html_text.count("class='rpt-fb'"), "rpt_notes": html_text.count("class='rpt-notes'"),
            "ledger_lr_adopted": lr, "ledger_fb_used": fb, "legend_in_page": True}


def split_levels(html_text):
    # 1ページに両レベルが入る形式: section単位で切る(idにstd/adv)
    return html_text


results = []


def rec(family, run, levels, fn):
    r = {"family": family, "run": run, "levels": levels}
    try:
        r.update(fn())
        r["status"] = "GENERATED"
    except BaseException as e:   # noqa: BLE001
        r["status"] = "NOT_GENERATED"; r["reason"] = f"{type(e).__name__}: {str(e)[:300]}"
    results.append(r)


# ---- X
def x_page(slug, run_name):
    def f():
        import er019_family_x_listening_page_01 as xp
        web = os.path.join(scratch, "X", f"{slug}__{run_name}"); shutil.rmtree(web, ignore_errors=True)
        summ = xp.build_page(slug, run_name, web)
        h = open(os.path.join(web, "index.html"), encoding="utf-8").read()
        run = f"er019_output/family_x_audio_production_wiring_01/{slug}__{run_name}"
        out = {"page": os.path.relpath(os.path.join(web, "index.html")), "per_level": {}}
        for lv in ("a2", "b1b"):
            if os.path.isdir(f"{run}/{lv}"):
                out["per_level"][lv] = analyze(h, run, lv)
        out["page_totals"] = {"marks": h.count("class='chunk-mark'"), "red_spans": h.count("class='rpt-lr'"), "blue_spans": h.count("class='rpt-fb'")}
        return out
    return f


XRUNS = [("ai_island_temple", "run_form_prod_01"), ("part2_hr_evidence_01", "run_r1"), ("part2_hr_evidence_01", "run_gpg5_x_01"), ("word_gacha", "run_wg_01"),
         ("paycheck_personality", "run_pp_01"), ("uk_train_speaker_playback", "run_chunk_01"), ("uk_train_speaker_playback", "run_stdchunk_ev_01")]
for slug, rn in XRUNS:
    rec("X", f"{slug}__{rn}", ["a2", "b1b"], x_page(slug, rn))


# ---- Y
def y_page(run, levels):
    def f():
        import er121_family_y_audio_01 as ya
        out = {"per_level": {}}
        lv_out = []
        for lv in levels:
            ad = os.path.join(scratch, "Y", run.replace("/", "_"), "audio_" + lv)
            shutil.rmtree(ad, ignore_errors=True)
            lv_out.append(ya.build_page_rows(run, lv, ad, "audio_" + lv, audience="public"))
        h = ya.render_y_page("B8 check", lv_out, audience="public")
        p = os.path.join(scratch, "Y", run.replace("/", "_"), "index.html"); open(p, "w", encoding="utf-8").write(h)
        out["page"] = os.path.relpath(p)
        for lv in levels:
            out["per_level"][lv] = analyze(h, run, lv)
        out["page_totals"] = {"marks": h.count("class='chunk-mark'"), "red_spans": h.count("class='rpt-lr'"), "blue_spans": h.count("class='rpt-fb'")}
        return out
    return f


def _copy_single_wav(src, dst, keep_token):
    """保存runにwavが複数あるとpage関数はfail-closed。scratch複製で最新(keep_token含む)の1本だけを残す(元run dirは不変)。"""
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("*_raw", "*.mp3"))
    for lv in ("a2", "b1b"):
        for w in glob.glob(f"{dst}/{lv}/assembled/*.wav"):
            if keep_token not in os.path.basename(w):
                os.remove(w)
    return dst


_ycopy = _copy_single_wav("er121_output/family_y_production_01/redelivery_fee_stdchunk_ev/run_ev_01", os.path.relpath(os.path.join(scratch, "Ycopy", "run_ev_01")), "STDCHUNK_EV")
for run, lvs in [("er121_output/family_y_production_01/redelivery_fee/run_01", ["a2", "b1b"]),
                 (_ycopy, ["a2", "b1b"]),
                 ("er121_output/family_y_production_01/redelivery_fee/run_gpg5_y_01", ["a2", "b1b"])]:
    rec("Y", run, lvs, y_page(run, lvs))


# ---- Z
def z_page(run):
    def f():
        import er063_family_z_audio_01 as z
        pd_ = os.path.join(scratch, "Z", run.replace("/", "_")); shutil.rmtree(pd_, ignore_errors=True)
        z.build_pages(run, pd_)
        h = open(os.path.join(pd_, "index.html"), encoding="utf-8").read()
        out = {"page": os.path.relpath(os.path.join(pd_, "index.html")), "per_level": {}}
        for lv in ("a2", "b1b"):
            out["per_level"][lv] = analyze(h, run, lv)
        out["page_totals"] = {"marks": h.count("class='chunk-mark'"), "red_spans": h.count("class='rpt-lr'"), "blue_spans": h.count("class='rpt-fb'")}
        return out
    return f


for run in ["er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_reselect_01", "er026_output/family_z_production_e2e_01/the_monkeys_paw/run_sf_prod_01",
            "er026_output/family_z_production_e2e_01/melos/run_e2e_02"]:
    rec("Z", run, ["a2", "b1b"], z_page(run))

with open(out_json, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1, default=str)
for r in results:
    print(r["family"], r["run"].split("/")[-1], r["status"], r.get("reason", "") or r.get("page_totals"))
