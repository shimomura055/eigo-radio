import re, json, sys, os, hashlib
sys.path.insert(0, '.')
import er121_family_y_audio_01 as ya, er121_family_y_structure_01 as ys, er_user_listening_page_common_01 as cp
R = "er121_output/family_y_production_01/redelivery_fee/run_style_fix_01"
S = sys.argv[1]
audio = os.path.join(S, "v06_audio"); os.makedirs(audio, exist_ok=True)
ja = ys.split_y_article(open(f"{R}/text/article_ja.md", encoding="utf-8").read())
levels = [ya.build_page_rows(R, lv, audio, "audio", ja_paragraphs=ja["segments"], audience="public") for lv in ("a2", "b1b")]
new_pub = ya.render_y_page(ja["title"], levels, show_notice=True, audience="public")
levels_dev = [ya.build_page_rows(R, lv, audio, "audio", ja_paragraphs=ja["segments"], audience="dev") for lv in ("a2", "b1b")]
new_dev = ya.render_y_page(ja["title"], levels_dev, show_notice=True, audience="dev")
old = open("user_test/family_y_production_redelivery_fee_03/index.html", encoding="utf-8").read()
rx_script = re.compile(r"<div class='script'>(.*?)</div>", re.S)
rx_kp = re.compile(r"<table class='kp'>(.*?)</table>", re.S)
rx_audio = re.compile(r"src='([^']+\.mp3)'")
ns, os_ = rx_script.findall(new_pub), rx_script.findall(old)
nk, ok_ = rx_kp.findall(new_pub), rx_kp.findall(old)
def subseq(a, b):
    it = iter(b); return all(any(x == y for y in it) for x in a)
res = {
 "new_public_scripts": len(ns), "old_03_scripts": len(os_), "new_scripts_subsequence_of_03": subseq(ns, os_),
 "new_kp_tables": len(nk), "old_kp_tables": len(ok_), "kp_new_subsequence_of_03": subseq(nk, ok_),
 "notice_in_new_public": ys.PAGE_NOTICE_JA in new_pub, "notice_count_new": new_pub.count(ys.PAGE_NOTICE_CLASS),
 "notice_text_in_03": old.count(ys.PAGE_NOTICE_JA), "old_notice_wording_in_03": "実在する人々の意見を参考に" in old,
 "markers_new_public": cp.count_chunk_markers(new_pub), "markers_new_dev_spans": cp.count_boundary_marker_spans(new_dev),
 "markers_03_all": cp.count_chunk_markers(old),
 "chunked_segments_in_run": sum(1 for lv in ("a2","b1b") for p in cp.load_chunk_plans(f"{R}/{lv}/audit/chunk_plan_{lv}.json").values() if p.get("chunked")),
 "audio_refs_new": sorted(set(re.findall(r"src='audio/([^']+)'", new_pub)))[:3],
 "check_page_public": cp.check_page(new_pub, audience="public")["overall"],
 "y_notice_check": ys.check_y_page_notice(new_pub)["ok"],
}
# per-row audio src names: _03 vs new
na = [m for m in rx_audio.findall(new_pub)]
res["audio_srcs_new"] = len(na)
res["audio_srcs_new_all_in_03"] = all(("audio/"+os.path.basename(x)) in old or x in old for x in na)
# audio file sha vs _03/audio
def sha(p):
    return hashlib.sha256(open(p,'rb').read()).hexdigest()
shared = [f for f in ("std_full.mp3","adv_full.mp3") if os.path.exists(f"user_test/family_y_production_redelivery_fee_03/audio/{f}")]
res["full_audio_files_03"] = shared
res["full_audio_same_as_03"] = {f: sha(f"{audio}/{f}") == sha(f"user_test/family_y_production_redelivery_fee_03/audio/{f}") for f in shared}
print(json.dumps(res, ensure_ascii=False, indent=1))
