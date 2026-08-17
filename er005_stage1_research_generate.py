# ============================================================
# er005_stage1_research_generate.py
# ER-005-COST-BASELINE-01: Stage 1(Research→Verified Fact Ledger draft)
# ============================================================
# 既存のResearch Pipeline(er003_v1_en_direct_vfl_01_generate.py の
# run_researcher/run_verification、OpenAI Responses API+web_search tool)を
# そのまま再利用する。新しいResearch/Personalizationロジックは作らない。
# vfl01.run_researcher/run_verificationはモジュールレベルのTOPIC定数を
# 読むため、呼び出し前にvfl01.TOPICを一時的に上書きする(関数自体は無改変)。
#
# 実行方法:
#   .venv/Scripts/python.exe er005_stage1_research_generate.py <theme_id>

from __future__ import annotations

import json
import sys

import er005_cost_logger as cl
import er003_v1_en_direct_vfl_01_generate as vfl01

TOPICS = {
    "akb48": (
        "AKB48の68thシングル『好きish』(2026年8月19日発売)。センターを務める"
        "伊藤百花は前作『名残り桜』に続く2作連続センターで、同一メンバーの2作連続"
        "単独センターは2014年の渡辺麻友以来12年ぶり。同シングルでは20期研究生・"
        "近藤沙樹(14歳)がAKB48史上最年少で初選抜入りした。"
    ),
    "parenting": (
        "2026年3-4月号のChild Development誌(Vol.97 Issue 2、DOI 10.1093/chidev/"
        "aacaf050)に掲載された、ニュージーランドDunedin Studyのコホート追跡研究"
        "(Islam, Jaffee, Belsky, Hancox, Poulton, Ramrakha, Wertz)。出生から"
        "追跡された参加者のうち719人が親になった時点(平均32.7歳)で、3歳の"
        "3歳の子どもに対する養育行動(sensitivity・cognitive stimulation)を測定し、"
        "親自身の社会階層の世代間変化(上昇移動/安定低位/安定高位)との関連を検証した。"
        "上昇移動した親は、安定して低いSESの親より養育の質が高かったが、"
        "一貫して高いSESの親より低かった。"
    ),
}

OUT_DIRS = {
    "akb48": "er005_output/cost_baseline_01/akb48/research",
    "parenting": "er005_output/cost_baseline_01/parenting/research",
}


def run(theme_id: str) -> None:
    # 注意: vfl01.run_researcher()/run_verification()はtopicをmodule変数TOPIC経由の
    # デフォルト引数(def build_researcher_prompt(topic: str = TOPIC))で受け取る実装で、
    # Pythonのデフォルト引数はmodule import時に一度だけ束縛されるため、呼び出し前に
    # vfl01.TOPICへ代入しても実際のプロンプトには反映されない(実測で確認済みの不具合)。
    # vfl01.pyの関数自体は無改変のまま、build_researcher_prompt/build_verification_prompt
    # という既存のtopic引数対応関数を直接呼び出すことで正しくtopicを渡す。
    topic = TOPICS[theme_id]
    out_dir = OUT_DIRS[theme_id]
    import os
    os.makedirs(out_dir, exist_ok=True)

    cl.install("er005_output/cost_baseline_01/raw_usage_log.jsonl")
    client = vfl01.get_client()

    with cl.logging_context(theme_id, "research_ledger_draft"):
        print(f"[Stage1][{theme_id}] Researcher呼び出し開始...")
        prompt = vfl01.build_researcher_prompt(topic)
        response = client.responses.create(
            model=vfl01.MODEL,
            reasoning={"effort": vfl01.REASONING_EFFORT},
            tools=[{"type": "web_search"}],
            text={"format": {"type": "json_schema", **vfl01.FACT_LEDGER_JSON_SCHEMA}},
            input=[
                {"role": "developer", "content": vfl01.RESEARCHER_DEVELOPER_MESSAGE},
                {"role": "user", "content": prompt},
            ],
        )
        text = response.output_text
        draft = {
            "prompt": prompt, "raw_text": text, "parsed": json.loads(text),
            "model": response.model, "response_id": response.id,
            "search_usage": vfl01.r3.extract_web_search_usage(response),
            "sources": vfl01.r3.extract_sources(response),
        }
    with open(f"{out_dir}/ledger_draft_raw.json", "w", encoding="utf-8") as f:
        json.dump(draft, f, ensure_ascii=False, indent=2, default=str)
    print(f"[Stage1][{theme_id}] Researcher完了。fact数={len(draft['parsed'].get('facts', []))}")

    with cl.logging_context(theme_id, "research_ledger_verification"):
        print(f"[Stage1][{theme_id}] Verification呼び出し開始...")
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
    print(f"[Stage1][{theme_id}] Verification完了。")


if __name__ == "__main__":
    theme_id = sys.argv[1]
    run(theme_id)
