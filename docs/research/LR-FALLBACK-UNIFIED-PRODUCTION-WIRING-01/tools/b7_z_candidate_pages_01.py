# -*- coding: utf-8 -*-
"""委任_12(B7)専用: Part 1/Part 2導入前に完成・公開済みのZ run(猿の手 run_sf_prod_01)の候補ページを、統合配線済みのZ page builder
(er063.build_pages: overlay・LR注記置換・er133赤/濃青/⏸)で再描画する(API 0)。stage_pagesはPart 1(LLM生成が必要)を要求して止まるため、
公開版(2026-10-24、Part 1/2なし)と同じ入力=study_htmlなしでbuild_pagesを直接呼ぶ。出力はpages-dirのみ(run dirは読取専用)。
使い方: python b7_z_candidate_pages_01.py --story the_monkeys_paw --run run_sf_prod_01 --pages-dir user_test/<candidate dir>"""
import argparse, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, ROOT); os.chdir(ROOT)
import er026_family_z_fiction_production_runner_01 as R

ap = argparse.ArgumentParser(); ap.add_argument("--story", required=True); ap.add_argument("--run", required=True); ap.add_argument("--pages-dir", required=True)
a = ap.parse_args()
cfg = R.STORY_REGISTRY[a.story]
out_dir = f"{R.E2E_RUN_ROOT}/{a.story}/{a.run}"
assert os.path.isdir(out_dir), out_dir
assert not os.path.abspath(a.pages_dir).startswith(os.path.abspath(out_dir)), "pages-dir must be outside the run dir"
assert a.pages_dir.rstrip("/") != cfg["e2e_pages_dir"].rstrip("/"), "公開dirへは出力しない"
res = R._m().a63.build_pages(out_dir, a.pages_dir, page_title=cfg["page_title_ja"], audio_file_prefix=cfg["audio_file_prefix"])
print("build_pages ok", sorted(res) if isinstance(res, dict) else res)
