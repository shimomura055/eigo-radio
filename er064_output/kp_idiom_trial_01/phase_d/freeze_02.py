# Phase D 再凍結スクリプト 委任_04 (extractor v3)。FROZEN_PLAN_02.json/.md を生成する。API不使用。有料call開始前に1回だけ実行。
import glob, hashlib, json, os, sys, time
sys.path.insert(0, ".")
import er064_kp_idiom_trial_01_extractor as X
import er064_kp_idiom_trial_01_select as S
import er064_kp_idiom_trial_01_pipeline as P

PD = "er064_output/kp_idiom_trial_01/phase_d"
PR = "er064_output/kp_idiom_trial_01/prompts"
if os.path.exists(f"{PD}/FROZEN_PLAN_02.json"):
    sys.exit("already frozen")


def T(i, exact, partial, role="gold", **kw):
    d = {"id": i, "exact": exact, "partial_all": partial, "role": role}
    d.update(kw)
    return d


D2 = [T("d2_temper", ["lost his temper", "lose his temper", "lose one's temper"], ["temper"]),
      T("d2_leg", ["pulling my leg", "pull my leg", "pull one's leg", "pull someone's leg"], ["leg"]),
      T("d2_tongue", ["bit her tongue", "bite her tongue", "bite one's tongue"], ["tongue"]),
      T("d2_mind", ["change her mind", "change one's mind"], ["mind"]),
      T("d2_eye", ["kept an eye on", "keep an eye on"], ["eye"]),
      T("d2_beans", ["spill the beans"], ["beans"])]
D3 = [T("d3_breath", ["holding its breath", "hold its breath", "hold one's breath"], ["breath"]),
      T("d3_shrug", ["shrugged off", "shrug off"], ["shrug"]),
      T("d3_surface", ["under the surface"], ["surface"]),
      T("d3_whisper", ["whisper a different story"], ["whisper"], b1_only=True),
      T("d3_asleep", ["are asleep"], ["asleep"], b1_only=True),
      T("d3_loan", ["a loan taken out against the future", "taken out against the future", "loan taken out against the future"], ["loan"], b1_only=True)]
D4 = [T("d4_comeswith", ["comes with", "come with"], ["come", "with"], cd=True),
      T("d4_addup", ["add up", "add up to"], ["add up"], cd=True),
      T("d4_pickedup", ["picked up", "pick up"], ["picked up"], cd=True),
      T("d4_showup", ["show up"], ["show up"], cd=True),
      T("d4_raninto", ["ran into", "run into"], ["ran into"], cd=True),
      T("d4_figure", ["figure out"], ["figure out"]),
      T("d4_putoff", ["put off"], ["put off"]),
      T("d4_turneddown", ["turned down", "turn down"], ["turned down"])]
N1 = [T("n1_tongue", ["bit her tongue", "bite her tongue", "bite one's tongue"], ["tongue"], "literal_neg"),
      T("n1_eyes", ["opened his eyes", "open his eyes", "open one's eyes", "open someone's eyes"], ["eyes"], "literal_neg"),
      T("n1_keys", ["lost her keys", "lose one's keys"], ["keys"], "literal_neg"),
      T("n1_ice", ["broke the ice", "break the ice"], ["ice"], "literal_neg"),
      T("n1_beans", ["spill the beans", "spilled the beans"], ["beans"], "literal_neg")]
R3 = [T("r3_eyes", ["open your eyes", "open one's eyes", "open someone's eyes"], ["eyes"], "literal_neg")]
R1 = [T("r1_mind", ["changes my mind", "change my mind", "change one's mind"], ["mind"], "natural_use")]
R2 = [T("r2_mark", ["made his mark", "make his mark", "make one's mark"], ["mark"], "ambiguous")]
COFFEE = [T("m1_pump", ["pumps its fist", "pump its fist", "pump one's fist"], ["pump", "fist"], "must1")]

plan = {
    "plan_id": "FAMILY-X-KP-IDIOM-EXTRACTION-SELECTION-TRIAL-01 / PHASE_D_FROZEN_PLAN_02 (委任_04, extractor v3)",
    "model": S.MODEL,
    "budget_limit_jpy": 34.28,
    "m1": [
        {"id": "coffee_std", "level": "std", "file": "er064_output/kp_idiom_trial_01/phase_a/inputs/v4_std_article.md", "targets": COFFEE},
        {"id": "coffee_adv", "level": "adv", "file": "er064_output/kp_idiom_trial_01/phase_a/inputs/v4_adv_article.md", "targets": COFFEE}],
    "articles": [
        {"id": "N1", "level": "std", "file": "n1_std.md", "role": "negative_control", "extract_n": 3, "final_runs": {"V0": [1], "V2": [1, 2]}, "targets": N1},
        {"id": "D6", "level": "adv", "file": "d6_adv.md", "role": "negative_control", "extract_n": 3, "final_runs": {"V0": [1], "V2": [1, 2]}, "targets": []},
        {"id": "D2", "level": "std", "file": "d2_std.md", "role": "positive", "extract_n": 2, "final_runs": {"V0": [1], "V2": [1, 2]}, "targets": D2},
        {"id": "D5", "level": "std", "file": "d5_std.md", "role": "negative_control", "extract_n": 3, "final_runs": {"V0": [1], "V2": [1, 2]}, "targets": []},
        {"id": "D3", "level": "adv", "file": "d3_adv.md", "role": "positive", "extract_n": 2, "final_runs": {"V0": [1], "V2": [1, 2]}, "targets": D3},
        {"id": "R3", "level": "adv", "file": "r3_adv.md", "role": "negative_control", "extract_n": 3, "final_runs": {"V2": [1]}, "targets": R3},
        {"id": "D4", "level": "adv", "file": "d4_adv.md", "role": "regression_watch", "extract_n": 2, "final_runs": {"V0": [1], "V2": [1, 2]}, "targets": D4},
        {"id": "R1", "level": "adv", "file": "r1_adv.md", "role": "shortlist_only", "extract_n": 0, "final_runs": {}, "targets": R1},
        {"id": "R2", "level": "std", "file": "r2_std.md", "role": "shortlist_only", "extract_n": 0, "final_runs": {}, "targets": R2}],
    "variants": {"V0": "Production現行shortlist + Production guidance",
                 "V1+d": "V0 + placeholder予約枠 + Trial guidance(b1抽出なし)",
                 "V2": "a(placeholder) + b1(extractor v3: cap3/不透明度rank順/transparency記録のみ/core_span/包含重複除外) + 予約枠cap3(cap15外) + Trial guidance(d, M4反映)",
                 "V3": "shortlistのみ(b2ルール候補+c)。最終選定なし"},
    "acceptance": {
        "negative_control_fail": "N1/D6/D5/R3 の run単位で、最終5件の llm_noncompositional/placeholder_title 由来件数 == 0 をPASS。1件でもあればFAIL。",
        "negative_control_extraction": "陰性対照4記事×n=3のaccepted件数の1回あたり平均 <= 1 を合格(2.0超は枠埋め偏りと判定)",
        "D2_shortlist": "V2 shortlistのexact再現 >=5/6(V0は2/6。予約枠cap3のため(a)placeholder 4件のうち最大3件が回復対象。cap3と抽出候補で押し出された件数も別途報告)",
        "D2_final": "run単位: gold6件のうち >=2件が最終5件(exact or partial)。V2 n=2の両runでPASS",
        "D3_shortlist": "run単位: b1_only 3件のうち>=1件がshortlist(exact or partial)。両runでPASS",
        "D3_final": "run単位: gold6件のうち >=2件が最終5件(partial可)。両runでPASS",
        "D4_final": "run単位: gold8件のうち >=2件が最終5件(partial可) かつ CD(cd=true)5件の最終内件数 >= V0最終のCD件数-1。両runでPASS",
        "M1_must1": "Coffee Std/Adv n=3: pump&fistが抽出accepted 6/6 かつ V2 shortlist 6/6。未達ならSTOP(事後基準変更・再実行禁止)",
        "MUST3_unit": "MUST-3(正規化PASS・重複QA PASS・source_span整合)の判定単位は item単位(対象項目)とrun単位(run最終のgate全PASS)を分けて報告する。run単位=retry後の最終状態"
    },
    "retry_policy": "Redundancy QA NGの場合のみ、Productionのretry方式(診断メモ追記、選定からやり直し)を1回(Production上限2回のうち1回)。V0はretryしない",
    "subject_included_heuristic": "近似: 限定詞/所有格で始まり3語以上で後続にbe動詞または-s/-ed/-es/-ing語尾語を含む、またはcore_span縮約が発生した場合を主語込みとみなす",
    "job_cost_estimate_jpy": 1.4,
    "execution_order": "m1 -> extract(全記事) -> final: [N1,D6] -> [D2] -> [D5] -> [D3] -> [R3] -> [D4] -> 任意 V1+d Coffee Adv n=2 (残額>=3)",
}

# prompt/guidance 実体(sha固定用にファイル化)
for lv in ("std", "adv"):
    open(f"{PR}/trial_guidance_{lv}_v2.txt", "w", encoding="utf-8").write(S.trial_guidance(lv))
FILES = (["er064_kp_idiom_trial_01_extractor.py", "er064_kp_idiom_trial_01_matcher.py", "er064_kp_idiom_trial_01_pipeline.py",
          "er064_kp_idiom_trial_01_select.py", "er064_kp_idiom_trial_01_phase_d_run.py", "er064_kp_idiom_trial_01_test_01.py",
          f"{PR}/extractor_prompt_v3.txt", f"{PR}/trial_guidance_std_v2.txt", f"{PR}/trial_guidance_adv_v2.txt",
          f"{PR}/production_guidance_before.txt", "er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt",
          f"{PD}/GOLD_TABLE_02.md"] + sorted(glob.glob(f"{PD}/inputs/*.md")) +
         ["er064_output/kp_idiom_trial_01/phase_a/inputs/v4_std_article.md", "er064_output/kp_idiom_trial_01/phase_a/inputs/v4_adv_article.md"])
plan["file_sha256"] = {f: hashlib.sha256(open(f, "rb").read()).hexdigest() for f in FILES}
now = time.time()
plan["frozen_at_epoch"] = now
plan["frozen_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(now))
plan["caps"] = {"ITEM_CAP": X.ITEM_CAP, "RESERVED_SLOT_CAP": P.RESERVED_SLOT_CAP}
json.dump(plan, open(f"{PD}/FROZEN_PLAN_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

DIFF = ["## FROZEN_PLAN_01(委任_03)からの変更点(v2->v3のみ。受入基準・variant定義・記事・run数・正解表GOLD_TABLE_02.mdは01と同一)",
        "- extractor Prompt: v2 -> v3(`prompts/extractor_prompt_v3.txt`)。「通常は0〜2件」「枠が3件あることは3件出す理由にならない」を削除。不透明度の高い順に最大3件、最も不透明な表現を必ず rank 1 にする構造へ。schemaに `rank`(integer)追加。",
        "- transparency自己申告: schemaに残すが除外ロジックから外す(記録のみ。`self_declared_transparent` 除外を廃止)。抽出側はrank昇順に並べ替えてからcap3を適用。",
        "- extractor LEVEL_DESC['adv']: 旧『基本的な句動詞・高頻度コロケーションは既知』を、選定guidance(M4)と整合する文言へ修正(句動詞でも基本義と異なる意味で使われ推測しにくいものは対象、構成語どおりの基本的な句動詞は既知)。",
        "- 修正(バグ): LLM候補dict生成行でコメントが `cefr_level`/`source_span` キーを飲み込んでいた箇所を修正(キーが候補に入る。Phase C/委任_03のコードでは欠落していた。testで固定)。",
        "- 実行ランナー: 凍結ファイルを02へ、費用記録を `cost_02.json`(予算上限34.28)、M1は `m1_recheck_02`、`--stage v1d` 追加、STOP判定を本件用STOP/STOP_NOTICEのみに限定(Family Z STOP_ALLはログのみ)。",
        "- 費用ベース: 本件上限50 - Phase C 14.4411 - 委任_03 M1 1.2792 = 34.2797。",
        ""]
md = ["# FROZEN_PLAN_02 (Phase D 再凍結、委任_04 / extractor v3)", "",
      f"- frozen_at: **{plan['frozen_at']}** (epoch {now:.3f})。この時刻より後にのみ有料callを開始する(各callの `started_at` を `cost.json` に記録し、報告で照合する)。",
      f"- モデル: {plan['model']}、残予算上限 JPY{plan['budget_limit_jpy']}、caps={plan['caps']}",
      "- 正解表本体: `GOLD_TABLE_02.md`(sha下記)。machine可読な正解(target)は `FROZEN_PLAN_02.json` の `m1`/`articles[].targets`。",
      "", "## variant定義"] + [f"- {k}: {v}" for k, v in plan["variants"].items()] + ["", "## 受入基準"] + \
     [f"- {k}: {v}" for k, v in plan["acceptance"].items()] + \
     ["", f"## retry: {plan['retry_policy']}", f"## 主語込み近似: {plan['subject_included_heuristic']}", f"## 実行順: {plan['execution_order']}", "",
      "## 記事・run数"] + [f"- {a['id']} ({a['level']}, {a['role']}): 抽出n={a['extract_n']}, 最終={a['final_runs']}" for a in plan["articles"]] + \
     [""] + DIFF + ["## sha256(凍結対象ファイル)"] + [f"- `{f}`: {h}" for f, h in plan["file_sha256"].items()]
open(f"{PD}/FROZEN_PLAN_02.md", "w", encoding="utf-8").write("\n".join(md) + "\n")
print("frozen at", plan["frozen_at"])
