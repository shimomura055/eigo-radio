# -*- coding: utf-8 -*-
"""er110_family_y_m7_calibration_01.py -- M7: 日本語版Leakage Checkの事前校正(DEV/Trial専用、Production参照0)。

旧B(3 Voices)記事の英語本文を日本語化(校正データ作成用の機械翻訳)し、日本語版Leakage Checkの誤検知・見逃しを測る。
正解ラベル = 旧B英語版Leakage Check(承認済みGate)の判定結果 + ユーザー指摘が記録されている個体(出典は各itemに記載)。
ラベルの限界(旧Checkが同じ系統のLLM判定であり完全な独立正解ではない)はLEAKAGE_CALIBRATION_01.mdに明記する。
"""
import argparse
import json
import os
import re
import sys

import er005_cost_logger as cl
import er003_v1_en_direct_vfl_01_generate as vfl01
import er012_e_family_entertainment_two_level_runner_01 as efam
import er053_family_x_factlock_ja_writer_01 as w1
import er110_family_y_text_trial_01 as y

OUT = "er110_output/family_y_trial_01/m7_calibration"
BUDGET = 40.0

ITEMS = [
    # id, 旧B json, 区分(ラベル出典)
    ("NG1_regression01_a1", "er012_output/editorial_b_voices_3v_generalization_regression_01_attempt1/analytical_leakage_check_3v_attempt1.json", "NG"),
    ("NG2_persontrial02_a1", "er012_output/editorial_b_voices_3v_person_voice_trial_02/b1b_run01_attempt1/analytical_leakage_check_3v_attempt1.json", "NG"),
    ("NG3_aihiring_a2_reeval", "er012_output/b_family_voices_position_spec01_offline_reeval_01/analytical_leakage_check_3v_attemptreeval_ai_hiring_3v_a2.json", "NG"),
    ("NG4_factsafety_a1", "er012_output/fact_safety_relaxation_trial_01/stage3_gate_on_run01_attempt1/analytical_leakage_check_3v_attempt1.json", "NG"),
    ("NG5_regression01_n2_a3", "er012_output/editorial_b_voices_3v_generalization_regression_01_n2_attempt3/analytical_leakage_check_3v_attempt3.json", "NG"),
    ("OK1_persontrial02_a2", "er012_output/editorial_b_voices_3v_person_voice_trial_02/b1b_run01_attempt2/analytical_leakage_check_3v_attempt2.json", "OK"),
    ("OK2_aihiring_b1_reeval", "er012_output/b_family_voices_position_spec01_offline_reeval_01/analytical_leakage_check_3v_attemptreeval_ai_hiring_3v_b1.json", "OK"),
]

SEC_MARKERS = [("voice_1", "【Voice 1本文】"), ("voice_2", "【Voice 2本文】"), ("voice_3", "【Voice 3本文】"),
               ("tension", "【Tension本文】"), ("closing", "【Closing本文】")]


def extract_sections(path: str) -> dict:
    d = json.load(open(path, encoding="utf-8"))
    prompt = d["prompt"]
    pos = []
    for k, m in SEC_MARKERS:
        i = prompt.index(m)
        pos.append((k, i, i + len(m)))
    out = {}
    for n, (k, i, j) in enumerate(pos):
        end = pos[n + 1][1] if n + 1 < len(pos) else len(prompt)
        out[k] = prompt[j:end].strip()
    old = {sec: (d["parsed"][sec] if sec in d["parsed"] else None) for sec in ("voice_1", "voice_2", "voice_3", "tension")}
    labels = {sec: [f for f, v in old[sec].items() if f.startswith("leak_") and v == "FAIL"] for sec in old}
    return {"sections": out, "old_labels": labels, "old_any_flagged": d["any_flagged"]}


TRANS_SCHEMA = {"name": "m7_translation", "strict": True, "schema": {
    "type": "object", "additionalProperties": False, "required": ["voice_1", "voice_2", "voice_3", "tension"],
    "properties": {k: {"type": "string"} for k in ("voice_1", "voice_2", "voice_3", "tension")}}}


def translate(client, secs: dict) -> tuple:
    prompt = ("次の英語の4つの文章(Voice 1〜3は人物本人が一人称で語る文章、Tensionは語り手の文章)を、校正用データとして日本語に忠実に翻訳してください。\n"
              "- 要約・言い換え・分析的な表現の除去・改善をしない。原文の内容、数字、調査や統計への言及、文の主語(調査が主語の文は調査が主語のまま)、"
              "語りの構造をそのまま残す。原文が分析的・報告的ならその印象を保つ。\n"
              "- 文体は話し言葉の常体(だ・である)。人物の語りの一人称は「私」。\n"
              "- 括弧・コロン・スラッシュ・三点リーダーは使わない。\n\n"
              + "\n\n".join(f"【{k}】\n{secs[k]}" for k in ("voice_1", "voice_2", "voice_3", "tension")))
    resp = y.chat(client, model=y.MODEL_CHEAP, effort="low", user=prompt, schema=TRANS_SCHEMA, stage="m7_translate")
    return json.loads(resp.output_text), y.resp_meta(resp)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", choices=("translate", "judge"), required=True)
    ap.add_argument("--judge-model", default=y.MODEL_CHEAP)
    ap.add_argument("--judge-effort", default="high")
    ap.add_argument("--tag", required=True, help="判定結果の保存名(例 luna_high)")
    ap.add_argument("--only", default="", help="カンマ区切りitem id(省略=全件)")
    ap.add_argument("--lang", choices=("ja", "en"), default="ja", help="en=旧B英語原文に日本語版Check Promptを適用(日本語化の影響切り分け用)")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    cl.install(f"{OUT}/raw_usage_log.jsonl")
    client = vfl01.get_client()
    only = {x for x in a.only.split(",") if x}
    if a.step == "translate":
        for iid, path, lab in ITEMS:
            if only and iid not in only:
                continue
            tp = f"{OUT}/{iid}_ja.json"
            if os.path.exists(tp):
                print("skip", iid)
                continue
            ex = extract_sections(path)
            ja, meta = translate(client, ex["sections"])
            w1.wj(tp, {"id": iid, "label": lab, "src": path, "old_labels": ex["old_labels"], "old_any_flagged": ex["old_any_flagged"],
                       "en": {k: ex["sections"][k] for k in ("voice_1", "voice_2", "voice_3", "tension")}, "ja": ja, "translate_meta": meta,
                       "translate_model": y.MODEL_CHEAP,
                       "translate_model_reason": "校正データ作成用の機械翻訳(評価対象外)。費用最小化(Charter 3)"})
            efam.assert_budget_ok(OUT, BUDGET, f"after translate {iid}")
    else:
        for iid, path, lab in ITEMS:
            if only and iid not in only:
                continue
            jp = f"{OUT}/{iid}_judge_{a.tag}.json"
            if os.path.exists(jp):
                print("skip", iid)
                continue
            d = json.load(open(f"{OUT}/{iid}_ja.json", encoding="utf-8"))
            check = y.run_leakage_check(client, d[a.lang], model=a.judge_model, effort=a.judge_effort, stage=f"m7_judge_{a.tag}",
                                        language_note=("英語" if a.lang == "en" else "日本語"))
            w1.wj(jp, {"id": iid, "label": lab, "tag": a.tag, "old_labels": d["old_labels"], "check": check})
            efam.assert_budget_ok(OUT, BUDGET, f"after judge {iid} {a.tag}")


if __name__ == "__main__":
    main()
