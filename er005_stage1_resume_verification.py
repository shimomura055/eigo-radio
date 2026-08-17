# ER-005: 子育て研究テーマのVerification再開(Researcher結果は既存draftを再利用、
# quota切れによる失敗の再実行として、Researcher呼び出しを重複させない)
from __future__ import annotations

import json

import er005_cost_logger as cl
import er003_v1_en_direct_vfl_01_generate as vfl01

theme_id = "parenting"
out_dir = "er005_output/cost_baseline_01/parenting/research"
topic = (
    "2026年3-4月号のChild Development誌(Vol.97 Issue 2、DOI 10.1093/chidev/"
    "aacaf050)に掲載された、ニュージーランドDunedin Studyのコホート追跡研究"
    "(Islam, Jaffee, Belsky, Hancox, Poulton, Ramrakha, Wertz)。出生から"
    "追跡された参加者のうち719人が親になった時点(平均32.7歳)で、3歳の"
    "子どもに対する養育行動(sensitivity・cognitive stimulation)を測定し、"
    "親自身の社会階層の世代間変化(上昇移動/安定低位/安定高位)との関連を検証した。"
    "上昇移動した親は、安定して低いSESの親より養育の質が高かったが、"
    "一貫して高いSESの親より低かった。"
)

cl.install("er005_output/cost_baseline_01/raw_usage_log.jsonl")
client = vfl01.get_client()

with open(f"{out_dir}/ledger_draft_raw.json", encoding="utf-8") as f:
    draft = json.load(f)

with cl.logging_context(theme_id, "research_ledger_verification"):
    print(f"[Stage1-resume][{theme_id}] Verification呼び出し開始...")
    v_prompt = vfl01.build_verification_prompt(topic, draft["parsed"])
    v_response = client.responses.create(
        model=vfl01.MODEL,
        reasoning={"effort": vfl01.REASONING_EFFORT},
        tools=[{"type": "web_search"}],
        text={"format": {"type": "json_schema", **vfl01.VERIFICATION_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": vfl01.VERIFICATION_DEVELOPER_MESSAGE},
            {"role": "user", "content": v_prompt},
        ],
    )
    v_text = v_response.output_text
    verification = {
        "prompt": v_prompt, "raw_text": v_text, "parsed": json.loads(v_text),
        "model": v_response.model, "response_id": v_response.id,
        "search_usage": vfl01.r3.extract_web_search_usage(v_response),
        "sources": vfl01.r3.extract_sources(v_response),
    }
with open(f"{out_dir}/ledger_verification_raw.json", "w", encoding="utf-8") as f:
    json.dump(verification, f, ensure_ascii=False, indent=2, default=str)
print(f"[Stage1-resume][{theme_id}] Verification完了。")
