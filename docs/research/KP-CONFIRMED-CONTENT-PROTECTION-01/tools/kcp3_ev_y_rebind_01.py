# -*- coding: utf-8 -*-
"""KCP委任_03 evidence用(コピーdirのみ・API 0): 自動採用(UNREVIEWED_AUTO_ADOPTED)のrunへ確定(REVIEWED)を後から入れると
review.selection_signatureが変わり、Yのkp_<lv>来歴(input_sha=sha(text|signature))が親sha不一致STOPになる(=確定をkp stage前に入れた状況の再現のため、
コピーの来歴entryのinput_shaだけを現在値へ付け替える。出力shaは触らない)。旧/新値をJSONで出力する。
使い方: py kcp3_ev_y_rebind_01.py --run <copy> [--only kp_a2,kp_b1b] [--part2]"""
import argparse, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, ROOT)
import er121_family_y_runner_01 as yr  # noqa: E402
import er121_family_y_structure_01 as ys  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--part2-sha", default=None, help="part2_b1bの新input_sha(エラーメッセージの現在値でなく完全値が必要な場合に指定)")
    a = ap.parse_args()
    run = a.run.replace("\\", "/").rstrip("/")
    slug, name = run.split("/")[-2], run.split("/")[-1]
    ctx = yr.YContext(slug=slug, run=name, mode="dry-run", run_root=os.path.dirname(os.path.dirname(run)))
    pj = f"{run}/provenance.json"
    prov = json.load(open(pj, encoding="utf-8"))
    out = {}
    for lv in yr.LEVELS:
        text = ys.canonical_body(yr._rd(yr._level_text_path(ctx, lv)))
        sig = yr._review_signature(ctx, lv)
        new = yr._sha(f"{text}|{sig}")
        e = prov["downstream_stages"][f"kp_{lv}"]
        out[f"kp_{lv}"] = {"old": e["input_sha256"], "new": new, "changed": e["input_sha256"] != new}
        e["input_sha256"] = new
    json.dump(prov, open(pj, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
