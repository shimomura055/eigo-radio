# -*- coding: utf-8 -*-
"""FAMILY-Z-STANDARD-PREVIEW-PROMPT-TRIAL-01 (Trial専用、Production経路非接続)。
Melos Std(A2)原稿に対し、Family X Standard Preview Prompt(er003_v1_iran01_a2_generate.PREVIEW_ROLE)の設計を
Fiction向けに最小調整した新Prompt(AFTER)で、Previewを1回だけ生成する。既存Previewは再生成せず
run_e2e_02/support/a2_support.json から取得する。TTS・runner起動・state書込なし。"""
import difflib
import glob
import hashlib
import json
import os
import sys
import datetime as dt

OUT = "er067_output/family_z_std_preview_trial_01"
RUN = "er026_output/family_z_production_e2e_01/melos/run_e2e_02"
os.makedirs(OUT, exist_ok=True)

# --- STOP確認(Melos用STOP_NOTICEはrun_e2e_01向け旧記録で非適用。STOP/STOP_ALLセンチネルのみ阻止条件) ---
notices = glob.glob("docs/pm/delegation_log/*STOP_NOTICE*")
sentinels = [p for p in (f"{RUN}/STOP", "er026_output/family_z_production_e2e_01/STOP_ALL") if os.path.exists(p)]
if sentinels:
    print("STOP sentinel present:", sentinels)
    sys.exit(3)

import er006_model_routing_contract_01 as routing
import er003_v1_iran01_a2_generate as a2gen
import er013_family_c_production_01 as fam_c
import er062_family_z_structure_01 as st
import er062_family_z_writer_01 as w62
import er026_family_z_fiction_production_runner_01 as er026

USD_JPY = 160.0
PRICE = {"input": 0.10, "output": 0.50}   # USD per 1M tokens, gpt-6-luna (er006_model_routing_pricing_coverage_test_01.py:50-52)


def sha(p):
    h = hashlib.sha256()
    h.update(open(p, "rb").read())
    return h.hexdigest()


def state_snapshot():
    files = [p for p in glob.glob(f"{RUN}/**/*", recursive=True) if os.path.isfile(p)]
    files += ["er026_family_z_fiction_production_runner_01.py", "er062_family_z_writer_01.py",
              "er062_family_z_structure_01.py", "er003_v1_iran01_a2_generate.py", "er006_model_routing_contract_01.py"]
    return {p.replace("\\", "/"): sha(p) for p in sorted(files)}


# --- prompts ---
COMMENT1 = json.load(open(f"{RUN}/support/a2_support.json", encoding="utf-8"))["comments"]["1"]
DEDUP = f"\n\n【重複回避】直前に流れるComment 1は次の通りです。これと内容が重複しないようにしてください。\n{COMMENT1}"
BEFORE_ROLE = er026.build_family_z_preview_prompt() + DEDUP

AFTER_ROLE = (
    "あなたは英語学習者向け音声番組の冒頭を担当するナビゲーターです。これからリスナーは、"
    "英語の短い物語(A2レベル、Public Domain文学のリライト)を、Preview・Comment・Key Phrasesに続いて聞きます。"
    "エピソードの一番最初に流す、日本語のPreviewを書いてください。\n\n"
    "役割: この物語の\n"
    "- theme(何についての物語か)\n"
    "- problem(主人公がどんな状況で、何に迷い・何と向き合っているか)\n"
    "- value(なぜこの物語を聴く価値があるか)\n"
    "を、リスナーの関心を引き「続きを聴きたい」と思わせるために必要十分な範囲で、ごく短く提示します。"
    "3つすべてを別々の文で書き並べる必要はありません。\n\n"
    "【重要・分量】2文程度、80〜110字程度を目安にしてください(多少の増減は許容しますが、"
    "4文・150字を超える長いPreviewにはしないでください)。短く聞きやすいことを優先し、"
    "theme/problem/valueを尽くそうとして冗長にならないよう注意してください。\n\n"
    "以下は避けてください:\n"
    "- 物語の出来事を順に説明する(あらすじの紹介にしない)\n"
    "- 結末や答えを先に言う\n"
    "- 物語の重要な転換点や、後半の具体的な展開(障害・出来事・場面の経過)を先に明かす\n"
    "- 後で流れるComment 1と内容が重複する\n"
    "- 本文にない設定・事実を追加する\n"
    + fam_c._BANNED_PHRASES_INSTRUCTION
    + DEDUP
)


def full_prompt(role, ctx):
    return a2gen.build_support_prompt(role, ctx)


text_a2 = w62.rd(w62.level_text_path(RUN, "a2"))
CTX = f"【物語全文(参考、新しい設定・事実の追加禁止)】\n{text_a2}"

open(f"{OUT}/prompt_before_01.txt", "w", encoding="utf-8").write(BEFORE_ROLE + "\n")
open(f"{OUT}/prompt_after_01.txt", "w", encoding="utf-8").write(AFTER_ROLE + "\n")
diff = "\n".join(difflib.unified_diff(BEFORE_ROLE.splitlines(), AFTER_ROLE.splitlines(),
                                      "prompt_before_01", "prompt_after_01", lineterm=""))
open(f"{OUT}/prompt_diff_01.md", "w", encoding="utf-8").write("# Prompt diff (before -> after)\n\n```diff\n" + diff + "\n```\n")

if "--prep" in sys.argv:
    print("prepared; full prompt chars:", len(full_prompt(AFTER_ROLE, CTX)), "notices:", notices)
    sys.exit(0)

model = routing.require_model("A2_SUPPORT", routing.SUPPORT_MODEL)
fp = full_prompt(AFTER_ROLE, CTX)
est_in = len(fp) + 100       # 日本語は概ね1文字<=1token の保守的見積
est_out = 3000               # reasoning含む保守的上限
est_jpy = (est_in * PRICE["input"] + est_out * PRICE["output"]) / 1e6 * USD_JPY
assert est_jpy < 20, est_jpy

before_state = state_snapshot()

import er003_v1_en_direct_vfl_01_generate as vfl01
client = vfl01.get_client()
captured = {}
orig_create = client.responses.create


def create(*a, **k):
    r = orig_create(*a, **k)
    captured["usage"] = r.usage
    captured["model"] = r.model
    captured["id"] = r.id
    captured["effort"] = k.get("reasoning")
    return r


client.responses.create = create

res = a2gen.run_support_text(client, AFTER_ROLE, CTX, max_attempts=1, model=model)   # 1 call only
usage = captured.get("usage")
ui = getattr(usage, "input_tokens", None)
uo = getattr(usage, "output_tokens", None)
rt = getattr(getattr(usage, "output_tokens_details", None), "reasoning_tokens", None)
act_jpy = ((ui or 0) * PRICE["input"] + (uo or 0) * PRICE["output"]) / 1e6 * USD_JPY
json.dump({"estimate_jpy": round(est_jpy, 4), "estimate_basis": {"input_tokens_est": est_in, "output_tokens_est": est_out},
           "price_usd_per_1M": PRICE,
           "price_source": "er006_model_routing_pricing_coverage_test_01.py:50-52 (gpt-6-luna input 0.10 / output 0.50)",
           "usd_jpy": USD_JPY, "calls": 1, "actual_input_tokens": ui, "actual_output_tokens": uo, "reasoning_tokens": rt,
           "actual_jpy": round(act_jpy, 4), "budget_jpy": 20, "hard_stop_jpy": 25, "within_budget": act_jpy < 20,
           "requested_model": model, "response_model_id": captured.get("model"), "response_id": captured.get("id"),
           "reasoning": captured.get("effort"), "status": res["status"]},
          open(f"{OUT}/cost_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
if res["status"] != "OK":
    print("FAILED", res["attempts"])
    sys.exit(2)
after = res["text"].strip()
sup = json.load(open(f"{RUN}/support/a2_support.json", encoding="utf-8"))
before = sup["preview"].strip()
open(f"{OUT}/preview_before_01.txt", "w", encoding="utf-8").write(before + "\n")
open(f"{OUT}/preview_after_01.txt", "w", encoding="utf-8").write(after + "\n")
open(f"{OUT}/prompt_after_full_assembled_01.txt", "w", encoding="utf-8").write(fp)
open(f"{OUT}/prompt_before_full_assembled_01.txt", "w", encoding="utf-8").write(full_prompt(BEFORE_ROLE, CTX))


def charlen(t):
    return len(t.replace("\n", ""))


def sentences(t):
    return [s for s in t.replace("。", "。\n").split("\n") if s.strip()]


vr = {}
for name, t in (("before", before), ("after", after)):
    vr[name] = {"text": t, "chars": charlen(t), "sentences": len(sentences(t)),
                "lint_support_text_ja_melos": st.lint_support_text(t, "ja", "melos"),
                "within_80_110": 80 <= charlen(t) <= 110,
                "within_le_150_and_le_3_sentences": charlen(t) <= 150 and len(sentences(t)) <= 3}
vr["validator"] = ("er062_family_z_structure_01.lint_support_text(text,'ja','melos') "
                   "(Production Preview/Comment lint, same call as er062_family_z_writer_01.run_support_std)")
vr["note"] = "文字数/文数は参考指標(Productionではhard gateではない)。lintのみProduction validator。"
json.dump(vr, open(f"{OUT}/validator_result_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

after_state = state_snapshot()
changed = [p for p in before_state if before_state[p] != after_state.get(p)]
json.dump({"files_checked": len(before_state), "changed": changed, "unchanged_all": not changed,
           "before_sha256": before_state, "after_sha256": after_state, "generated_at": dt.datetime.now().isoformat()},
          open(f"{OUT}/state_guard_01.json", "w", encoding="utf-8"), indent=1)
print("BEFORE:", before)
print("AFTER:", after)
print(json.dumps(vr, ensure_ascii=False)[:900])
print("cost JPY", act_jpy, "changed", changed)
