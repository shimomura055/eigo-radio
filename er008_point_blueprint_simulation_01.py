# ============================================================
# er008_point_blueprint_simulation_01.py
# A2/B1 Point Structure Semantic Alignment: No.4-6 Simulation
# ============================================================
# 【重要な位置づけ】これはDry Run/Simulationであり、実LLM呼び出しは
# 一切行わない。以下はすべて、このタスクの担当者(Claude)が既存の
# Verified Fact Ledger(stage_b3_vfl.json)と、既に公開されているNo.4-6
# のA2/B1記事本文(ER-008-A2-STORY-B1-SUPPORT-COMPATIBILITY-AUDIT-01で
# 読み込み済み)を手作業で突き合わせて構築した「後付けBlueprint」および
# 「後付けfact利用申告」である。実際にShared Point Blueprint生成LLMや
# Writer LLMがこれらを出力したわけではない(そのような新規API呼び出しは
# 本タスクでは実施していない、実行には承認が必要)。
#
# 目的: 新設したStructural Validator(er008_point_blueprint_validator_01.py)
# が、ER-008で発見された実際の不整合(No.5のComment 4問題、No.6の
# Point間Fact移動問題)を正しく検出し、問題のなかったNo.4を正しくPASS
# させることを、実データに基づいて確認する。
from __future__ import annotations

from er008_shared_point_blueprint_01 import SharedPointBlueprint, PointBlueprint
from er008_point_blueprint_validator_01 import validate_topic


# ============================================================
# No.4(スーパーマーケットの棚配置)
# ============================================================
# Point One(両レベル共通、Greeceの205人フィールド研究、店舗デザイン/
# 雰囲気と買い物客の感情・意思決定の関連): FACT-010, FACT-011
# Point Two(両レベル共通、2022年のデータ駆動型棚配置研究、衝動買い
# 最大化が目的): FACT-012, FACT-013
NO4_BLUEPRINT = SharedPointBlueprint(
    topic_id="pool_n4_supermarket",
    point_1=PointBlueprint(
        role="店舗デザイン・雰囲気が買い物客の意思決定に関わることを示す",
        common_claim="店の空間デザインは、買い物客の感情や意思決定に関わる",
        common_fact_ids=["FACT-010", "FACT-011"],
        optional_b1_fact_ids=[],
        required_in_a2_fact_ids=["FACT-011"],
        comment_anchor="店の空間デザインが、買い物客の気持ちや意思決定に関わるという研究があります。",
        prohibited_reference_fact_ids=["FACT-012", "FACT-013"],
    ),
    point_2=PointBlueprint(
        role="棚の再配置がデータに基づいて行われうることを示す",
        common_claim="一部の棚の再配置は、データに基づいて計画されている",
        common_fact_ids=["FACT-012", "FACT-013"],
        optional_b1_fact_ids=[],
        required_in_a2_fact_ids=["FACT-012"],
        comment_anchor="棚の再配置の中には、購買データに基づいて計画されているものもあります。",
        prohibited_reference_fact_ids=[],
    ),
    point_transition="事実(店の雰囲気の影響) -> 事実(データ駆動の再配置手法)",
)
# 実際に公開されたNo.4 A2/B1記事本文を読み、Point One/Twoが実際にどの
# fact_idを使っているかを手作業で対応づけたもの(ER-008監査時の読解に
# 基づく)。
NO4_A2_USAGE = {"point_1_fact_ids_used": ["FACT-010", "FACT-011"],
                "point_2_fact_ids_used": ["FACT-012", "FACT-013"]}
NO4_B1_USAGE = {"point_1_fact_ids_used": ["FACT-010", "FACT-011"],
                "point_2_fact_ids_used": ["FACT-012", "FACT-013"]}
# Comment 4(B1、実際にA2でも流用検討された文)は「データに基づく再配置」
# (FACT-012/013)のみを参照しており、Point Oneの内容は参照していない。
NO4_COMMENT_AFTER_P2 = ["FACT-012", "FACT-013"]


# ============================================================
# No.5(カフェの座席問題)
# ============================================================
# Point One(両レベル共通、店のデザインが仕事客への姿勢を示す):
#   FACT-004(Archetypal=仕事抑制的デザイン), FACT-005(PTP=仕事歓迎的デザイン)
# Point Two: ★A2とB1で実際に異なるfactを中心に据えていた箇所★
#   A2実際の中心: FACT-010(研究の中心的結論、店の差別化の明確さが結果を左右する)
#   B1実際の中心: FACT-008, FACT-009(customer-workersが支払い以上の価値[閑散期の
#     収入・活気の演出]をもたらすという研究の解釈)
# 後付けBlueprintでは、Ledgerの記述上「研究の中心的結論」と明記されている
# FACT-010をcommon_claim/common_fact_idsとし、FACT-008/009はB1のみが
# 使ってよいoptional_b1_fact_idsとして扱う(A2の実際の記述と整合する
# 割り当て)。
NO5_BLUEPRINT = SharedPointBlueprint(
    topic_id="pool_n5_cafes",
    point_1=PointBlueprint(
        role="店のデザインが仕事客への姿勢を伝えることを示す",
        common_claim="カフェのデザインは、仕事をする客を歓迎するかどうかを伝える",
        common_fact_ids=["FACT-004", "FACT-005"],
        optional_b1_fact_ids=[],
        required_in_a2_fact_ids=["FACT-005"],
        comment_anchor="カフェのデザイン(Wi-Fiの有無、席や電源など)が、仕事をする客への姿勢を伝えます。",
        prohibited_reference_fact_ids=["FACT-010", "FACT-008", "FACT-009"],
    ),
    point_2=PointBlueprint(
        role="店が方針を明確にすることの重要性を示す(研究の中心的結論)",
        common_claim="仕事客を歓迎するかどうかを明確にすることが重要である",
        common_fact_ids=["FACT-010"],
        optional_b1_fact_ids=["FACT-008", "FACT-009"],
        required_in_a2_fact_ids=["FACT-010"],
        comment_anchor="店が仕事客への方針を明確にするかどうかが、結果を左右するという研究結果があります。",
        prohibited_reference_fact_ids=[],
    ),
    point_transition="事実(デザインが姿勢を伝える) -> 判断軸(明確な方針の重要性)",
)
NO5_A2_USAGE = {"point_1_fact_ids_used": ["FACT-004", "FACT-005"],
                "point_2_fact_ids_used": ["FACT-010"]}
# 実際のB1記事は、Point TwoでFACT-010(研究の中心的結論)に触れず、
# FACT-008/009(支払い以上の価値)だけを中心に書いている
# (ER-008監査で確認済み: B1 point_two_body「PTPs may gain more than a
# payment from customer-workers...」)。
NO5_B1_USAGE = {"point_1_fact_ids_used": ["FACT-004", "FACT-005"],
                "point_2_fact_ids_used": ["FACT-008", "FACT-009"]}
# 実際のB1 Comment 4は、B1自身のPoint Two本文(FACT-008/009)から生成され、
# 「customers who work there may offer the café more than their payment」
# と述べている(=FACT-008/009を参照)。
NO5_COMMENT_AFTER_P2 = ["FACT-008", "FACT-009"]


# ============================================================
# No.6(配達追跡ページの確認衝動)
# ============================================================
# Point One/Twoの間で、実験の詳細(F-008、28人の実験)がA2とB1で
# 別のPointへ配置されている(ER-008監査で確認済み):
#   A2 Point One = 不確実性が確認を誘う(F-008の実験詳細を含む)
#   A2 Point Two = 意識的自覚が確認行動を予測する(F-005/F-006/F-007)
#   B1 Point One = 無力な待機下の小さな行動(概念的枠組みのみ、F-008は含まない)
#   B1 Point Two = 実験の詳細(F-008を含む)
NO6_BLUEPRINT = SharedPointBlueprint(
    topic_id="pool_n6_delivery",
    point_1=PointBlueprint(
        role="不確実性が確認行動を誘うという実験結果を示す",
        common_claim="判断が難しく不確実なときほど、人は確認する回数を増やす",
        common_fact_ids=["F-004", "F-008"],
        optional_b1_fact_ids=[],
        required_in_a2_fact_ids=["F-004"],
        comment_anchor="判断が難しく不確実なときほど、人は確認する回数を増やすという実験結果があります。",
        prohibited_reference_fact_ids=["F-005", "F-006", "F-007"],
    ),
    point_2=PointBlueprint(
        role="意識的な不確実性の自覚が確認行動を予測することを示す",
        common_claim="自分の不確実性を意識できるかどうかが、確認行動を予測する",
        common_fact_ids=["F-005"],
        optional_b1_fact_ids=["F-006", "F-007"],
        required_in_a2_fact_ids=["F-005"],
        comment_anchor="自分がどれくらい不確実だと意識しているかが、確認行動を予測するという結果もありました。",
        prohibited_reference_fact_ids=[],
    ),
    point_transition="事実(不確実性が確認を誘う実験) -> 精緻化(意識的自覚の役割)",
)
NO6_A2_USAGE = {"point_1_fact_ids_used": ["F-004", "F-008"],
                "point_2_fact_ids_used": ["F-005"]}
# 実際のB1記事は、F-008(28人の実験詳細)をPoint Oneではなく
# Point Twoで導入している(ER-008監査で確認済み: B1 point_two_body
# 「In a 2021 Scientific Reports experiment, 28 healthy people...」)。
NO6_B1_USAGE = {"point_1_fact_ids_used": ["F-004"],
                "point_2_fact_ids_used": ["F-005", "F-008"]}
# 実際のB1 Comment 4は、Point One/Twoの両方を要約する形で、F-008
# (実験の詳細)をPoint Twoの内容として参照している。
NO6_COMMENT_AFTER_P2 = ["F-005", "F-008"]


def run_simulation_for_topic(name, bp, a2_usage, b1_usage, comment_after_p2):
    print(f"\n{'='*60}\n{name}\n{'='*60}")
    result = validate_topic(
        bp, a2_writer_usage=a2_usage, b1_writer_usage=b1_usage,
        comment_after_point_2_refs=comment_after_p2,
    )
    print(f"validate_topic().ok = {result.ok}")
    if result.violations:
        for v in result.violations:
            print(f"  [FAIL] {v.check}: {v.message}")
    else:
        print("  (violation無し)")
    return result


def run():
    r4 = run_simulation_for_topic("No.4 (pool_n4_supermarket)", NO4_BLUEPRINT,
                                    NO4_A2_USAGE, NO4_B1_USAGE, NO4_COMMENT_AFTER_P2)
    r5 = run_simulation_for_topic("No.5 (pool_n5_cafes)", NO5_BLUEPRINT,
                                    NO5_A2_USAGE, NO5_B1_USAGE, NO5_COMMENT_AFTER_P2)
    r6 = run_simulation_for_topic("No.6 (pool_n6_delivery)", NO6_BLUEPRINT,
                                    NO6_A2_USAGE, NO6_B1_USAGE, NO6_COMMENT_AFTER_P2)

    print(f"\n{'='*60}\nSUMMARY\n{'='*60}")
    print(f"No.4: ok={r4.ok} (期待: True、ER-008でDIRECTLY_REUSABLEと判定済み)")
    print(f"No.5: ok={r5.ok} (期待: False、ER-008で発見したComment 4のB1限定fact参照を検出できるはず)")
    print(f"No.6: ok={r6.ok} (期待: False、ER-008で発見したPoint間Fact移動を検出できるはず)")


if __name__ == "__main__":
    run()
