# -*- coding: utf-8 -*-
"""END-USER-LISTENING-PAGE-PRODUCTION-WIRING-01 委任_02B: golden fixtureの凍結(API 0)。

現行builderが出した最終dev HTML(X月reselect / Y再配達料fee_03 / Z走れメロスmelos_02)と、その元になった中間データ(timeline・KP確定・承認済み日本語原稿)を
fixtureとして保存する。testはこのfixtureだけで動く(runのdirに依存しない)。OPEN-596(閉じ無し引用符)行は藪の中の実本文断片で最小Zページを作る。
実行: .venv\\Scripts\\python.exe er135_enduser_fixtures_01\\freeze_fixtures_01.py
"""
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
OUT = Path(__file__).resolve().parent

SRC = {
    "x_moon": dict(family="x", page="user_test/family_x_moon_shrinking_reselect_01/index.html",
                   run="er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01",
                   ja="er019_output/moon_shrinking/run_reselect_01/ja_writer/revision2.md"),
    "y_fee03": dict(family="y", page="user_test/family_y_production_redelivery_fee_03/index.html",
                    run="er121_output/family_y_production_01/redelivery_fee/run_gpg5_y_01",
                    ja_article="er121_output/family_y_production_01/redelivery_fee/run_gpg5_y_01/text/article_ja.md"),
    "z_melos02": dict(family="z", page="user_test/family_z_melos_02/index.html",
                      run="er026_output/family_z_production_e2e_01/melos/run_e2e_06"),
}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def timeline(run, sub):
    for pat in ("{s}/audit/timeline.json", "{s}/assembly/timeline.json"):
        p = ROOT / run / pat.format(s=sub)
        if p.is_file():
            d = json.load(open(p, encoding="utf-8"))
            tl = d["timeline"] if isinstance(d, dict) else d
            return [{"part": x["part"], "start_seconds": x["start_seconds"]} for x in tl if not str(x["part"]).startswith(("pause_", "_silence"))], str(p.relative_to(ROOT))
    raise SystemExit(f"timeline not found {run} {sub}")


def kp_x_y(run, sub, family):
    cands = [f"{sub}/key_phrases/confirmed_selection.json", f"{sub}/audit/confirmed_selection.json", f"key_phrases/{sub}/confirmed_selection.json"]
    for c in cands:
        p = ROOT / run / c
        if p.is_file():
            d = json.load(open(p, encoding="utf-8"))
            return [i["key_phrase"] for i in d["items"] if i.get("slot") == "kp"], c
    raise SystemExit(f"confirmed_selection not found {run} {sub}")


def kp_z(run, sub):
    p = ROOT / run / "key_phrases" / f"{sub}_result.json"
    d = json.load(open(p, encoding="utf-8"))
    return [i["display_phrase"] for i in d["selection"]["parsed"]["items"]], str(p.relative_to(ROOT))


def main():
    manifest = {}
    for name, cfg in SRC.items():
        shutil.copyfile(ROOT / cfg["page"], OUT / f"{name}_index.html")
        m = {"family": cfg["family"], "html": f"{name}_index.html", "source_page": cfg["page"], "html_sha256": sha(OUT / f"{name}_index.html"), "timeline": {}, "kp": {}}
        for lv, sub in (("std", "a2"), ("adv", "b1b")):
            m["timeline"][lv], tp = timeline(cfg["run"], sub)
            m["timeline"][lv + "_source"] = tp
            if cfg["family"] == "z":
                m["kp"][lv], kpp = kp_z(cfg["run"], sub)
            else:
                m["kp"][lv], kpp = kp_x_y(cfg["run"], sub, cfg["family"])
            m["kp"][lv + "_source"] = kpp
        if "ja" in cfg:
            txt = (ROOT / cfg["ja"]).read_text(encoding="utf-8").strip()
            m["ja_manuscript"] = {"source": cfg["ja"], "sha256": sha(ROOT / cfg["ja"]), "paragraphs_after_title": [x.strip() for x in re.split(r"\n\s*\n", txt) if x.strip()][1:]}
        if "ja_article" in cfg:
            import er121_family_y_structure_01 as ys
            segs = ys.split_y_article((ROOT / cfg["ja_article"]).read_text(encoding="utf-8"))["segments"]
            m["y_segments"] = {"source": cfg["ja_article"], "sha256": sha(ROOT / cfg["ja_article"]), "segments": segs}
        manifest[name] = m
    # OPEN-596(閉じ無し引用符)行: 藪の中の実本文(公開dev pageのdiv.script)を最小のZ形式ページへ
    g = (ROOT / "user_test/family_z_in_a_grove_01/index.html").read_text(encoding="utf-8")
    rows = re.split(r"(?=<tr><td><b>)", g.split("<h2 id='adv'>")[0])
    pick = [r for r in rows if r.startswith("<tr><td><b>Full Story Part 2 ")]
    assert len(pick) == 1, len(pick)
    part2 = pick[0]
    part2 = re.sub(r"</td></tr>.*$", "</td></tr>", part2, flags=re.S)
    # 藪の中の公開page(HEAD)は学習項目の修正途中でlk3下線に対応する意味一覧が無い。本fixtureは文分割(OPEN-596)用なので下線markupは外し本文のみ使う
    part2 = re.sub(r'<(span|strong) class="lk\d" data-hl="[^"]*">(.*?)</\1>', r"\2", part2)
    part2 = re.sub(r'<ul class="lk-meaning">.*?</ul>', "", part2, flags=re.S)
    unclosed = [d for d in re.findall(r"<div class='script'>(.*?)</div>", part2, re.S) if (d.count("&quot;") % 2 == 1)]
    assert unclosed, "閉じ無し引用符の行が見つからない"
    topic = "<tr><td><b>Topic intro (Charon)</b><br><span class='sec'>13.8秒〜 (3.3秒)</span><br><button class='jump' data-target='main_std' data-t='13.797'>全編のこの位置へ</button></td><td class='play'><audio controls preload='none' src='audio_standard/a2_02.mp3'></audio></td><td><div class='script'>Today&#x27;s topic is In a Grove.</div></td></tr>"
    jt = "<tr><td><b>Japanese title (Aoede)</b><br><span class='sec'>17.7秒〜 (1.4秒)</span><br><button class='jump' data-target='main_std' data-t='17.727'>全編のこの位置へ</button></td><td class='play'><audio controls preload='none' src='audio_standard/a2_03.mp3'></audio></td><td><div class='script'>藪の中</div></td></tr>"
    page = ("<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>藪の中 試聴(OPEN-596 fixture)</title></head><body><h1>藪の中 試聴</h1>"
            "<h2 id='std'>Standard(通し全編 60秒)</h2><div class='combo'><audio id='main_std' controls preload='none' src='audio_standard/full.mp3'></audio></div>"
            "<table><thead><tr><th>パート</th><th>音声</th><th>Script / Key Phrase</th></tr></thead><tbody>" + topic + jt +
            part2.replace("data-target='main_std'", "data-target='main_std'") + "</tbody></table></body></html>")
    (OUT / "z_open596_min_index.html").write_text(page, encoding="utf-8")
    manifest["z_open596_min"] = {"family": "z", "html": "z_open596_min_index.html", "source_page": "user_test/family_z_in_a_grove_01/index.html(Full Story Part 2のdiv.script実本文)",
                                 "unclosed_quote_divs": [re.sub(r"<[^>]+>", "", d)[:80] for d in unclosed]}
    (OUT / "manifest_01.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v.get("html_sha256", "") for k, v in manifest.items()}, indent=1))


if __name__ == "__main__":
    main()
