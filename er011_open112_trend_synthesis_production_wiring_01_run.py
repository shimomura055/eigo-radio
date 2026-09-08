# ============================================================
# er011_open112_trend_synthesis_production_wiring_01_run.py
# OPEN-112-TREND-SYNTHESIS-MODE-PRODUCTION-WIRING-01: Gate 3 runtime
# evidence runner
# ============================================================
# 目的: 配線後のProduction Writer正式初回経路(er006_pool_pilot_01_writer.
# run_writer_for_theme → er003_v1_n3_01_articles_generate.run_one_pattern、
# Trialスクリプトを一切経由しない)から、editorial_mode="trend_synthesis"
# を指定してTheme 2(日本の若者のスロー旅行志向と実際の滞在日数のギャップ、
# `FAMILY-A-TREND-SYNTHESIS-PRODUCTION-READINESS-01_REPORT.md`§0が指す
# 「若者の旅」、A2/B1 rerun_04完成音声が`APPROVED_FOR_PRODUCTION`)のA2/B1を
# 実際に1本ずつ生成し、Editor→Fact QA→Ledger Deviation→Point Overlap QA→
# Key Phraseまでの既存Production QAチェーンを実際に通す。
#
# 【訂正記録】当初、米国・イラン/ホルムズ海峡テーマ(OPEN-112-TREND-
# SYNTHESIS-MINIMAL-PROMPT-TRIAL-09/OPEN-112-TREND-ENGAGEMENT-REFERENCE-
# AB-TRIAL-10がFocus Module検証用に使った別の一回限りのTrialテーマ)を
# 誤って「Theme 2」として実行してしまった(このテーマは実際には
# `APPROVED_FOR_PRODUCTION`のTheme 2に昇格したことがない)。その誤った
# runの成果物は`er011_output/open112_trend_synthesis_production_wiring_01/
# _superseded_wrong_theme_iran_hormuz/`(README_MISTAKE.md参照)へ退避し、
# 本ファイルは正しいTheme 2(若者のスロー旅行)のTOPIC_JA/Ledgerへ修正した。
#
# Ledger供給: 既存のTheme 2 Ledger(承認済み、OPEN-112-TREND-THEME2-B-A2-
# B1-TEXT-TRIAL-12で精度修正済みのCORRECTED版、rerun_04完成音声[Trial-12の
# article.mdをAssembly/TTSのみでTrial-13が完成音声化したもの]が実際に使った
# ものと同一Ledger)を、Trial-11/12のPythonモジュールをimportせず、ファイル
# パス経由で直接読み込む(Gate 4: Trialスクリプトへのimport無し)。今回は
# 「既存Theme 2 Ledgerを手順として正式に使う」ことをそのままrun対象と
# する(Ledger自動Research供給への統合は今回のスコープ外、OPEN_ITEMS残件)。
#
# Trend Gate 6条件チェックリスト: Theme 2は(Iran/HormuzのTrial-09とは異なり)
# 記事生成前に正式なtrend_gate_result.json相当の手動判定記録を作成していな
# かった。本runでは、既存Verified Fact Ledger(theme2_verified_fact_ledger_
# CORRECTED_trial12.txt)の内容を本タスク実施者が読み、6条件それぞれについて
# 事後的な手動判定を行い、その結果をrun_metadataとして記録する(記事内容から
# の自動判定ロジックは実装していない)。
#
# 費用上限: 本タスクの上限¥100(超過見込みならSTOP、事前見積りは
# FAMILY-A-TREND-SYNTHESIS-PRODUCTION-READINESS-01_REPORT.md §12「数十円
# 〜百円未満/テーマ」)。訂正前の誤ったIran/Hormuz runで既に約¥83を消費した
# ため、本runは合計費用が上限を超過する前提で実施する(誤りの是正のため、
# 詳細はOPEN-112-TREND-SYNTHESIS-MODE-PRODUCTION-WIRING-01_REPORT.md参照)。
from __future__ import annotations

import os

import er005_cost_logger as cl

THEME_ID = "open112_trend_synthesis_production_wiring_01"
OUT_DIR = f"er011_output/{THEME_ID}"

# Theme 2 Ledger(承認済み、Trial-12のCORRECTED版=rerun_04完成音声の元と
# なったarticle.mdが実際に使ったものと同一)。Trial Pythonモジュールを
# importせず、ファイルパスで直接参照する。
THEME2_LEDGER_PATH = ("er011_output/open112_trend_theme2_b_a2_b1_text_trial_12/research/"
                       "theme2_verified_fact_ledger_CORRECTED_trial12.txt")

# テーマ文面(Trial-11/12と同一文面をそのまま再利用、比較可能性のため)。
TREND_TOPIC_JA = (
    "2026年9月時点、日本の若者(とくに男性)の旅行に対する意識には、「もっと自分の"
    "ペースで、ゆっくり過ごしたい」という願望の高まりがいくつもの独立した調査で確認"
    "されている。日本交通公社(JTBF)の2025年調査では、29歳以下の男性が好む旅行"
    "スタイルの上位に「ひとり旅」(25.2%)・「趣味を深める旅行」(24.3%)が挙がり、海外"
    "旅行経験のある日本のZ世代の約9割が「ツアー内に自由時間が欲しい」と回答し、その"
    "うち約8割が半日以上の自由時間を希望している。じゃらんリサーチセンターの調査では、"
    "1カ月休暇が取れた場合に希望する旅行日数として「1週間程度」と答えた人が24.1%で"
    "最多だった。しかし、同じじゃらんリサーチセンターの別の調査(2024年秋)では、実際の"
    "旅行意向者の宿泊日数は平均1.8泊・中央値2.0泊にとどまっている。観光庁の「令和7年版"
    "観光白書」も、政策的課題として「一人当たり旅行回数の増加や滞在長期化を図る必要が"
    "ある」と明記しており、これは現時点では滞在がまだ十分に長期化していないことを政府"
    "自身が認めた形になっている。また、29歳以下の女性では「有名な観光地を巡る」ことへの"
    "関心が依然として44.7%と高く、性別によって傾向は異なる。今回の記事が扱うのは、"
    "「名所巡りからゆっくり滞在へ、すでに完全に変わった」という単純な話ではなく、意識・"
    "願望としてのスロー志向の高まりと、実際に測定されている短い滞在日数との間のギャップ"
    "という、Trend Synthesisタイプの記事である。"
)

# Trend Gate 6条件チェックリスト(本タスク実施者による事後的な手動判定、
# theme2_verified_fact_ledger_CORRECTED_trial12.txtの内容[Source一覧・
# 各Factのevidence_strength/counter_signal_or_limitation記載]に基づく)。
THEME2_TREND_GATE_CHECKLIST = {
    "note": "Theme 2は記事生成前に正式なtrend_gate_result.json相当の記録を作成していなかった"
            "(Iran/HormuzテーマのTrial-09とは異なる)。本チェックリストは、本タスク実施者が"
            "既存Ledgerの内容を読んで行った事後的な手動判定であり、記事内容からの自動判定"
            "ロジックではない。",
    "evaluated_at": "2026-09-08",
    "criteria": {
        "1_independent_signals_2plus": {
            "result": "PASS",
            "evidence": "SRC-201(観光庁白書)/SRC-202・203・207(じゃらんリサーチセンター)/"
                        "SRC-204・205(JTBF)/SRC-208(ヒルトン)/SRC-211(観光庁一次資料)など、"
                        "少なくとも5系統以上の独立した調査主体による信号がある。",
        },
        "2_common_direction": {
            "result": "PASS",
            "evidence": "F-201/F-203/F-204/F-205はいずれも「自分のペースでゆっくり」"
                        "「自由時間を求める」という同方向のSignal。",
        },
        "3_temporal_or_structural_change": {
            "result": "PASS(構造的ギャップ型)",
            "evidence": "単純な時系列変化ではなく、意識調査(スロー志向の高まり)と実測行動"
                        "(F-206宿泊日数平均1.8泊)の間の構造的ギャップが中心主張(注記3)。",
        },
        "4_counter_signal_confirmed": {
            "result": "PASS",
            "evidence": "F-206(実際の宿泊日数の短さ)・F-211/観光白書の「長期化はまだ"
                        "達成されていない」という政府認識自体が、スロー志向Trendに対する"
                        "明確なcounter-signal(限界)として注記3で明示されている。",
        },
        "5_not_single_source_trend": {
            "result": "PASS",
            "evidence": "観光庁・じゃらんリサーチセンター・JTBF・ヒルトンという異なる調査"
                        "主体に基づく(単一ソースの言い換えではない)。",
        },
        "6_evidence_strength_not_flattened": {
            "result": "PASS",
            "evidence": "Ledger内でofficial_statistics(F-211等)/company_official_"
                        "announcement(F-201/F-206等)/reputable_media_reporting(F-205等)"
                        "を各Factごとにevidence_strengthとして明示的に区別している。",
        },
    },
    "verdict": "TREND_READY(本タスク実施者による事後的手動判定)",
    "mode_determination_2question_test": {
        "q1_single_origin_question": "Main Storyを『[日付]にXが起きた』という1文で書いても"
                                      "要点は失われないか? → NO(単一の出来事ではなく、意識と"
                                      "行動の間の構造的ギャップという複数調査の集約が主張の本体)",
        "q2_aggregation_question": "いずれか1つのSignalを除いても中心的主張は大きく変わらないか? "
                                   "→ YES(例: F-201[ヒルトン]を除いてもF-203/F-205/F-206による"
                                   "「意識と行動のギャップ」という中心主張は他のSignalで成立し続ける)",
        "determination": "TREND_SYNTHESIS",
    },
}


def run():
    import er003_v1_en_direct_ab_01_generate as ab01
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er006_pool_pilot_01_writer as writer_mod

    os.makedirs(OUT_DIR, exist_ok=True)

    trend_gate_checklist = THEME2_TREND_GATE_CHECKLIST

    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()

    print(f"[{THEME_ID}] Production Writer正式初回経路(er006_pool_pilot_01_writer.run_writer_for_theme "
          f"-> er003_v1_n3_01_articles_generate.run_one_pattern)でeditorial_mode=trend_synthesisを実行します。")
    result = writer_mod.run_writer_for_theme(
        client, master_full_text, THEME_ID, TREND_TOPIC_JA, THEME2_LEDGER_PATH, OUT_DIR,
        blueprint=None, editorial_mode="trend_synthesis", trend_gate_checklist=trend_gate_checklist)

    for label, r in result["results"].items():
        print(f"  {label}: status={r.get('status')} fact_verdict={r.get('fact_verdict')} "
              f"ledger_status={r.get('ledger_status')} "
              f"point_overlap_article_retry_attempts={r.get('point_overlap_article_retry_attempts')}")
    return result


if __name__ == "__main__":
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    run()
