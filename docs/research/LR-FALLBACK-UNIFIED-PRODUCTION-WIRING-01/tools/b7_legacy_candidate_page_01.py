# -*- coding: utf-8 -*-
"""委任_12(B7)専用: 旧per-article試聴ページ(er019_nws2_final_page_01、Word Gacha公開版の生成script)に、統合配線と同じ共通部品
(er132 overlay=LR後の英文、er133 赤/濃青/⏸)を重ねて候補ページを作る一回限りのwrapper。API 0。Production codeは変更しない。
- 公開版(2026-10-24)はPart 1導入前のrunのためPart 1(kp_general_explanations.json)が無い。公開版と同じく学習ブロックを出さない(無ければ空文字)。
- --no-overlay: 配線なしの再現(公開版とbyte一致するかの確認用)。
- ⏸はchunk_plan記録があるunitにだけ(記録が無い=分割なし=出さない)。
使い方: python b7_legacy_candidate_page_01.py --audio-dir <run> --out <dir> --tag word_gacha --title-ja 英単語ガチャ [--no-overlay]"""
import copy, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, ROOT); os.chdir(ROOT)
no_overlay = "--no-overlay" in sys.argv
if no_overlay:
    sys.argv.remove("--no-overlay")
import er019_pp_page_01 as pp
import er019_nws2_final_page_01 as nw
import er003_kp_general_explanation_01 as p1
import er132_lr_overlay_pages_01 as e132
import er133_report_marks_01 as rm
import er_user_listening_page_common_01 as uc

_orig_study = p1.study_html_for_audio_dir
def _study(run, level="b1b"):
    if not os.path.exists(os.path.join(run, level, "key_phrases", "kp_general_explanations.json")):
        return ""   # Part 1導入前のrun(公開版と同じ)
    return _orig_study(run, level=level)
p1.study_html_for_audio_dir = _study

_orig_seg = pp.seg_html
_cache, RENDERED = {}, set()
def _ctx(level):
    if level not in _cache:
        ld = os.path.join(pp.RUN, level)
        _cache[level] = (e132.level_ledger(pp.RUN, level, level_dir=ld), rm.load_events(pp.RUN, level, level_dir=ld), uc.load_chunk_plans(f"{ld}/audit/chunk_plan_{level}.json") if os.path.exists(f"{ld}/audit/chunk_plan_{level}.json") else {})
    return _cache[level]

def seg_html(res, parts, part, kp_items, kp_expl, level):
    if no_overlay:
        return _orig_seg(res, parts, part, kp_items, kp_expl, level)
    ledger, events, plans = _ctx(level)
    parts2, _ = e132.overlay_level_units(ledger, parts)
    res2 = res
    segs = res.get("segments") or {}
    for sid, ent in segs.items():
        t = (ent or {}).get("text")
        if isinstance(t, str):
            t2 = e132.display_text_of_clip(ledger, sid, t)
            if t2 != t:
                if res2 is res:
                    res2 = copy.deepcopy(res)
                res2["segments"][sid]["text"] = t2
    html = _orig_seg(res2, parts2, part, kp_items, kp_expl, level)
    pl = part.lower()
    m = re.match(r"full story part (\d)", pl)
    uk = f"full_story_part{m.group(1)}" if m else ("in_one_line" if pl.startswith("in one line") else None)
    if uk is None:
        return html
    text = parts2["part" + m.group(1)] if m else parts2["in_one_line"]
    mk = rm.marks_for(events, text, ids=() if m else (uk,), block=uk if m else None, whole=not m)
    cts = uc.chunk_texts_of_plan(plans.get(uk)) if (m and plans) else None
    if not mk and not cts:
        return html
    old = "<div class='script'>" + pp.esc(text).replace("\n", "<br>") + "</div>"
    assert old in html, f"script div not found for {uk}"
    new = uc.script_block(text, cts, marks=mk)
    if mk:
        RENDERED.update(c["id"] for c in rm.select(events, ids=() if m else (uk,), block=uk if m else None))
    j = new.index("</div>")   # 先頭のdiv.script内だけ旧ページと同じく改行を<br>へ(注記側は触らない)
    new = new[:j].replace(chr(10), "<br>") + new[j:]
    return html.replace(old, new, 1)
pp.seg_html = seg_html

if __name__ == "__main__":
    nw.main()
    out = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    idx = os.path.join(out, "index.html")
    page = open(idx, encoding="utf-8").read()
    if not no_overlay:
        total = {c for lv in ("a2", "b1b") for c in _ctx(lv)[1]}
        missing = total - RENDERED
        assert not missing, f"events not rendered in page: {missing}"
        if "rpt-" in page:
            page = page.replace("</div><div class='tabs'>", "</div>" + rm.legend_html() + "<div class='tabs'>", 1)
            assert "rpt-legend" in page
        open(idx, "w", encoding="utf-8").write(page)
    cp = uc.check_page(page, base_dir=out, levels=("Standard", "Advanced"), audience="public")
    print("check_page", cp["overall"], {k: v["ok"] for k, v in cp["checks"].items()})
