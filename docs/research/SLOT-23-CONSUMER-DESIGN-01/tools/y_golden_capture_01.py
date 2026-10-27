"""SLOT-23 委任_04D: 既存Y run(マーク無し)のページHTML(build_page_rows+render_y_page。mp3は別、HTMLのみ)のsha256を記録する(API 0・read-only)。
配線変更の前後で同一であること(マーク無し=従来バイト同一)を固定する。使い方: python y_golden_capture_01.py <run_dir> <out_json>"""
import hashlib
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
import er121_family_y_audio_01 as ya  # noqa: E402
import er121_family_y_structure_01 as ys  # noqa: E402


def capture(run_dir: str) -> dict:
    out = {}
    title = ys.split_y_article(open(f"{run_dir}/text/article_ja.md", encoding="utf-8").read())["title"]
    ja_segs = ys.split_y_article(open(f"{run_dir}/text/article_ja.md", encoding="utf-8").read())["segments"]
    for audience in ("public", "dev"):
        tmp = tempfile.mkdtemp(prefix="ygold_")
        try:
            levels = [ya.build_page_rows(run_dir, lv, tmp, "audio", ja_paragraphs=ja_segs, audience=audience) for lv in ("a2", "b1b")]
            html_text = ya.render_y_page(title, levels, show_notice=False, audience=audience)
            out[audience] = {"sha256": hashlib.sha256(html_text.encode("utf-8")).hexdigest(), "len": len(html_text)}
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return out


if __name__ == "__main__":
    run, dest = sys.argv[1], sys.argv[2]
    res = {"run": run.replace("\\", "/"), **capture(run)}
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(json.dumps(res))
