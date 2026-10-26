# -*- coding: utf-8 -*-
"""CURRENT_BASELINE_01.md を current_baseline_01.json + 現行方式fresh run(trial_runs_01.json)から生成する(API 0)。"""
import json
import os

OUT = os.path.dirname(os.path.abspath(__file__))
base = json.load(open(os.path.join(OUT, "current_baseline_01.json"), encoding="utf-8"))["levels"]
runs = json.load(open(os.path.join(OUT, "trial_runs_01.json"), encoding="utf-8"))["runs"]

L = ["# CURRENT_BASELINE_01 (現行Production方式の候補一覧。KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01)", "",
     "現行方式 = Production既定 `er119_kp_candidates_01.generate_candidates`(call1=Prompt 2で3件 + call2=Prompt 2-Vで最大5件 = 要求最大8件)。",
     "単語/フレーズ判定基準(事前固定): `used_form` が空白を含まない1トークン(ハイフン複合語を含む)=単語、空白区切りの2語以上=フレーズ(句動詞・空白区切り複合名詞もフレーズ)。", "",
     "## 使用run・本文・sha256", "",
     "| 記事 | Family | level | 本文ファイル | 本文sha256(先頭12) | 本文=Production selector promptの本文 | 現行候補の出所 |", "|---|---|---|---|---|---|---|"]
SRC = {"ai_island_temple": "er019_output/ai_island_temple/run_ai_01/{lv}/article.md (正式run: er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01)",
       "uk_train_speaker_playback": "er019_output/uk_train_speaker_playback/run_nws_02/{lv}/article.md (正式run: .../uk_train_speaker_playback__run_nws_02)",
       "monkeys_paw": "er026_output/family_z_production_e2e_01/the_monkeys_paw/run_sf_prod_01/writer/{zf} を canonical_article_text 化 (CLOSED_USER_PASS。a2=std.md / b1b=r2.md)"}
for k, v in base.items():
    eq = v.get("prompt_body_equals_text", v.get("formal_3kp_prompt_body_equals_text"))
    src = SRC[v["article"]].format(lv=v["level"], zf="std.md" if v["level"] == "a2" else "r2.md")
    L.append(f"| {v['ja']} | {v['family']} | {v['level']}({v['level_name']}) | {src} | {v['text_sha256'][:12]} | {eq} | {v['current_source']} |")
L += ["", "注: 英国電車マナー・猿の手には『8候補方式(KP Human Review導入後)』の既存候補成果物が存在しない(両者とも正式runは3KP時代の `keywords_canonicalized.json`)ため、"
      "現行方式の候補は同一本文に対して Production既定の `generate_candidates` をDEV出力dirで1回実行して取得した(fresh。費用は下表)。AI島のみ既存 `kp_candidates.json` を再利用。"
      "run_fzcw_e1_01(STOP残置)は不使用。", ""]
L += ["## レベル別の現行方式実績", ""]
for k, v in base.items():
    L.append(f"### {v['ja']} / {v['level_name']} ({v['level']})")
    if v.get("current"):
        cur = v["current"]
        rows, dropped = cur["candidates"], cur["dropped"] or []
        L.append(f"- 出所: 既存再利用(`{v['formal_run']}/{v['level']}/key_phrases/kp_candidates.json`)。要求最大8、AI返答={len(rows) + len(dropped)}、Gate除外={len(dropped)}、最終={len(rows)}"
                 f"(フレーズ{cur['summary']['n_phrase']}・単語{cur['summary']['n_word']})。費用=この成果物単体の記録なし(fresh現行平均から推計)。")
    else:
        r = runs[f"{v['article']}__{v['level']}__current__r1"]
        rows, dropped = r["candidates"], r["dropped"]
        L.append(f"- 出所: fresh(`docs/research/KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01/runs/{r['tag']}/`)。要求最大8、AI返答={r['returned']['total']}、Gate除外={len(dropped)}、最終={r['n_final']}"
                 f"(フレーズ{r['n_phrase']}・単語{r['n_word']})。実費=¥{r['cost']['jpy']}({r['cost']['calls']} call)。")
    if v.get("formal_3kp_reference"):
        L.append("- 参考(正式runの確定3KP): " + " / ".join(f"{x['used_form']}({x['japanese_gloss']})" for x in v["formal_3kp_reference"]))
    L += ["", "| 順位 | 区分 | 英語表現 | 日本語意味 | 出典文 | 選定理由 | origin |", "|---|---|---|---|---|---|---|"]
    for c in rows:
        L.append(f"| {c['ai_rank']} | {'単語' if c['kind'] == 'word' else 'フレーズ'} | {c['used_form']} | {c['japanese_gloss']} | {c['source_sentence']} | {c.get('reason_ja') or ''} | {c['origin']}#{c['raw_rank']} |")
    for d in dropped:
        L.append(f"| (除外) | - | {d['phrase']} | - | - | **{d['stage']}**: {d['reasons'][0][:110]} | {d.get('origin')} |")
    L.append("")
with open(os.path.join(OUT, "CURRENT_BASELINE_01.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")
print("ok", len(L))
