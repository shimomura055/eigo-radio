# ============================================================
# er011_family_a_trend_synthesis_ai_manufacturing_production_run_01_writer.py
# 管理ID: FAMILY-A-TREND-SYNTHESIS-AI-MANUFACTURING-PRODUCTION-RUN-01
# ============================================================
# 目的: ユーザー決定(2026-09-12)により承認されたテーマ「AI investment is
# reshaping factories and manufacturing / AI投資が工場・製造業をどう変え
# 始めているか」で、既存Production Writer正式初回経路
# (er006_pool_pilot_01_writer.run_writer_for_theme -> er003_v1_n3_01_
# articles_generate.run_one_pattern、Trialスクリプトを一切経由しない)から
# editorial_mode="trend_synthesis"を指定してA2/B1Bを1本ずつ生成する。
# 前例(er011_open112_trend_synthesis_production_wiring_01_run.py、Theme2
# 「若者のスロー旅行」)と全く同じ呼び出しパターンをテーマだけ差し替えて
# 使う。Production関数(gen.run_one_pattern内のWriter/Fact Checker/Ledger
# Deviation Checker/Point Overlap QA含む)は一切変更しない。
#
# Ledger供給: 本タスク実施者(Claude Code)が2026-09-12にIFR(国際ロボット
# 連盟)・Deloitte・米連邦準備制度理事会(FRB Beige Book)という4つの独立
# した組織の公式Webページへcurlで直接アクセスして取得したテキストのみを
# 根拠に、手動でVerified Fact Ledgerを作成した
# (er011_output/family_a_trend_ai_manufacturing_prod_run_01/research/
# ai_manufacturing_verified_fact_ledger_01.txt)。これはCURRENT_SPEC.md
# 「Research/Ledger供給経路」行が定める正式initial path(既存の承認済み
# Ledgerを手動作成してファイルとしてそのまま使う)をそのまま踏襲した
# ものであり、新しい供給経路を追加するものではない。
#
# 費用上限: 本タスクの上限¥400(Research+記事2本+音声、合算)。Research
# 自体はLLM呼び出しを使わず(curlでの直接取得+人手構造化)実費¥0。
from __future__ import annotations

import os

import er005_cost_logger as cl

THEME_ID = "family_a_trend_ai_manufacturing_prod_run_01"
OUT_DIR = f"er011_output/{THEME_ID}"

LEDGER_PATH = f"{OUT_DIR}/research/ai_manufacturing_verified_fact_ledger_01.txt"

TREND_TOPIC_JA = (
    "2026年9月時点、世界の製造業ではAI・自律ロボットへの投資意欲と投資計画が、"
    "複数の独立した調査で急速に高まっていることが確認されている。国際ロボット"
    "連盟(IFR)の年次統計「World Robotics 2025」では、2024年の産業用ロボット"
    "新規設置台数が542,000台に達し、10年前の2倍以上になったことが示され、IFR"
    "は2026年の業界トップトレンドの第1位に「AI & Autonomy」を挙げている。"
    "米国でも2025年の設置台数が前年比11%増の38,000台に回復し、食品産業での"
    "導入が30%急増した。大手コンサルティングファームDeloitteが製造業幹部"
    "600人に行った調査では、80%が今後、改善予算の20%以上をスマート製造技術"
    "(agentic AIを含む)へ投資する計画だと回答している。中国は第15次五カ年"
    "計画でAIロボティクスを国家の産業戦略の中核に据えた。しかし、同じ調査群は"
    "「実際の稼働導入」がまだ限定的であることも示している。Manufacturing"
    "Leadership Councilの調査では、「今後2年以内にphysical AI(自律ロボット)"
    "を使う」と答えた企業は22%だが、これは裏を返せば現時点の実導入率がまだ"
    "9%にとどまることを意味する。IFR自身も、中国のヒューマノイドロボットの"
    "華やかな公開実演について「実際の生産現場での能力は依然デモンストレーター"
    "やパイロットプロジェクトに限られる」と述べている。さらに、AI関連投資の"
    "一部(半導体製造・データセンター向け電力設備など5,000億ドル超規模)は、"
    "工場の生産工程そのものをAI化するというより「AIを支えるための製造業」に"
    "流れている。米連邦準備制度理事会(FRB)のBeige Book(2026年9月公表)も、"
    "一部地区の製造業活動の底堅さがデータセンター関連受注に支えられていると"
    "報告している。今回の記事が扱うのは「工場はすでにAIで動いている」という"
    "単純な話ではなく、投資意欲・計画の急拡大と実際の稼働導入の現状との間の"
    "ギャップ、そして「AIを使う製造業」と「AIのために製造する製造業」という"
    "異なる2つの投資ベクトルが同時進行しているという、Trend Synthesisタイプの"
    "記事である。"
)

# Trend Gate 6条件チェックリスト(本タスク実施者による、上記Ledgerの内容に
# 基づく手動判定。記事内容からの自動判定ロジックではない。既存Theme2運用と
# 同一パターン)。
TREND_GATE_CHECKLIST = {
    "note": "本チェックリストは、本タスク実施者(Claude Code)が新規作成したVerified "
            "Fact Ledger(ai_manufacturing_verified_fact_ledger_01.txt)の内容を読んで"
            "行った事前の手動判定であり、記事内容からの自動判定ロジックではない。",
    "evaluated_at": "2026-09-12",
    "criteria": {
        "1_independent_signals_2plus": {
            "result": "PASS",
            "evidence": "SRC-401〜405(IFR、業界団体公式統計)/SRC-406〜407"
                        "(Deloitte自社調査、Manufacturing Leadership Council)/"
                        "SRC-408(米連邦準備制度理事会Beige Book)という4つの独立した"
                        "組織による信号がある。",
        },
        "2_common_direction": {
            "result": "PASS",
            "evidence": "F-401/F-402/F-403/F-404/F-405/F-406はいずれも「AI・自律"
                        "ロボットへの投資・導入意欲の高まり」という同方向のSignal。",
        },
        "3_temporal_or_structural_change": {
            "result": "PASS(構造的ギャップ型)",
            "evidence": "単純な時系列変化ではなく、投資意欲・計画調査(急拡大)と実際の"
                        "稼働導入率(F-406: 現状9%)の間の構造的ギャップ、および「AIを"
                        "使う製造業」と「AIのために製造する製造業」という2つの投資"
                        "ベクトルの併存が中心主張(注記3)。",
        },
        "4_counter_signal_confirmed": {
            "result": "PASS",
            "evidence": "F-406(physical AIの現状実導入率はまだ9%)・F-404(IFR自身が"
                        "ヒューマノイドロボットの実生産能力は依然デモ・パイロット段階"
                        "と明記)が、AI投資拡大Trendに対する明確なcounter-signal"
                        "(限界)として注記3で明示されている。",
        },
        "5_not_single_source_trend": {
            "result": "PASS",
            "evidence": "IFR・Deloitte・Manufacturing Leadership Council・米連邦準備"
                        "制度理事会という異なる調査主体に基づく(単一ソースの言い換え"
                        "ではない)。",
        },
        "6_evidence_strength_not_flattened": {
            "result": "PASS",
            "evidence": "Ledger内でgovernment_official_announcement(F-409)/"
                        "industry_association_official_statistics(F-401〜404)/"
                        "company_official_announcement(F-405/407/408)/"
                        "reputable_secondary_reporting(F-406、MLC一次資料"
                        "COULD_NOT_CONFIRM)を各Factごとにevidence_strengthとして"
                        "明示的に区別している。",
        },
    },
    "verdict": "TREND_READY(本タスク実施者による事前手動判定)",
    "mode_determination_2question_test": {
        "q1_single_origin_question": "Main Storyを『[日付]にXが起きた』という1文で"
                                      "書いても要点は失われないか? → NO(単一の出来事"
                                      "ではなく、複数の独立調査が示す投資意欲の急拡大と、"
                                      "実際の稼働導入の現状との間のギャップという集約が"
                                      "主張の本体)",
        "q2_aggregation_question": "いずれか1つのSignalを除いても中心的主張は大きく"
                                   "変わらないか? → YES(例: F-404[中国の国家戦略]を"
                                   "除いても、F-401/F-403/F-405/F-406による「投資拡大"
                                   "と実導入のギャップ」という中心主張は他のSignalで"
                                   "成立し続ける)",
        "determination": "TREND_SYNTHESIS",
    },
}


def run():
    import er003_v1_en_direct_ab_01_generate as ab01
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er006_pool_pilot_01_writer as writer_mod

    os.makedirs(OUT_DIR, exist_ok=True)

    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()

    print(f"[{THEME_ID}] Production Writer正式初回経路(er006_pool_pilot_01_writer."
          f"run_writer_for_theme -> er003_v1_n3_01_articles_generate.run_one_pattern)で"
          f"editorial_mode=trend_synthesisを実行します。")
    result = writer_mod.run_writer_for_theme(
        client, master_full_text, THEME_ID, TREND_TOPIC_JA, LEDGER_PATH, OUT_DIR,
        blueprint=None, editorial_mode="trend_synthesis",
        trend_gate_checklist=TREND_GATE_CHECKLIST)

    for label, r in result["results"].items():
        print(f"  {label}: status={r.get('status')} fact_verdict={r.get('fact_verdict')} "
              f"ledger_status={r.get('ledger_status')} "
              f"point_overlap_article_retry_attempts={r.get('point_overlap_article_retry_attempts')}")
    return result


if __name__ == "__main__":
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    run()
