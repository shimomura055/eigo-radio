# ============================================================
# er012_multi_voice_fact_attribution_trial_02.py
# 管理ID: EDITORIAL-B-FAMILY-MULTI-VOICE-FACT-ATTRIBUTION-TRIAL-02(Lane B、OPEN-131)
# ============================================================
# 目的(Trial専用、Production非変更、ユーザー決定2026-09-09に基づく):
#   Trial-01で候補A'(Voice別evidenceタグ+「Voice本文は出典明記不要」の
#   明示ルール)がVALIDATED(Trial範囲内)となった。今回のTrial-02は、
#   A'が量産可能な形で再現性を持つかを、
#     (1) 同一入力でのN=5再現性(judgment分布・試行間一致率)
#     (2) false accept/false reject(事実誤り(数値・主体改変) vs
#         帰属曖昧、実在人物claimのFAリスクを含む拡張claim集合)
#     (3) B-Family専用opt-inがA-Familyへ誤爆しないか(非影響/誤爆stress test)
#     (4) 3V/4Vへの拡張可能性(design確認+synthetic 1件)
#   について実測する。
#
# 本番コードは一切import/変更しない。本番Fact Checker
# (er002_ja_web_research_r3.py)・Ledger Deviation Checker
# (er003_v1_en_direct_vfl_01_generate.py)・fact_checker_prompt_template_r3.txt・
# model routing(er006_model_routing_contract_01.py)・
# er010_ledger_local_rewrite_09.py・er012_b_family_editorial_type_registry_01.py
# は読み取りのみ。Trial-01スクリプト(er012_multi_voice_fact_attribution_
# trial_01.py)はTrial専用資産としてimportし、Prompt/評価コードを再利用・
# 拡張する(Trial-01ファイル自体は変更しない)。
#
# 出力: er012_output/multi_voice_fact_attribution_trial_02/ 配下
# 予算上限: 本Trialの新規LLM呼び出しは合計 上限¥60 相当まで
#   (web_search tool不使用、reasoning_effort="low")
# ============================================================
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()
from openai import OpenAI

import er006_model_routing_contract_01 as routing
import er012_multi_voice_fact_attribution_trial_01 as trial01

OUT_DIR = "er012_output/multi_voice_fact_attribution_trial_02"
os.makedirs(OUT_DIR, exist_ok=True)

MODEL = routing.WRITER_FACT_CHECK_MODEL  # 本番Fact Checkerと同一モデル参照(prompt/toolは別、Trial-01と同一方針)
REASONING_EFFORT = "low"  # Trial-01と同一(コスト抑制)

# ------------------------------------------------------------
# CORE claims: Trial-01のCLAIMS(6件)を無変更で再利用(N=5再現性の対象、
# Trial-01との比較可能性を保つため中身は一切変更しない)
# ------------------------------------------------------------
CORE_CLAIMS = trial01.CLAIMS

# ------------------------------------------------------------
# EXT claims: Trial-02で新規追加する拡張claim(すべてTrial専用の合成、
# 実記事には存在しない。既存Ledger実factの一部を意図的に改変したものは
# 明記する)
# ------------------------------------------------------------
EXT_CLAIMS = [
    {
        "id": "ext_fact_error_digit_voiceA",
        "section": "voice_a_body(One Voice、本Trialで数値改変)",
        "source_run": (
            "本Trialで作成した合成claim。VOICE_1_EVIDENCE 1-01(Gensler調査、"
            "固定席保有者は所属感87%/74%)の数値を97%/40%へ意図的に改変した"
            "うえで一人称のVoice A語りへ翻案。"
        ),
        "claim_text": (
            "私のように固定席を持つ人は、Genslerの調査によれば97%が職場への"
            "所属感を持てると答えており、固定席のない人はわずか40%しかそう"
            "感じていないという。だからこそ私は自分の机に安心を感じている。"
        ),
        "ground_truth_should_flag": True,
        "risk_category": "factual_error_digit",
        "ground_truth_note": (
            "内容の骨格(固定席保有者の方が所属感が高い、というLedger 1-01の"
            "方向性)は実evidenceに対応するが、具体的数値(97%/40%)は実evidence"
            "(87%/74%)と一致しない改変値。これは『帰属(一人称化)』の問題では"
            "なく『事実そのものが誤っている』問題であり、Voice本文の出典免除"
            "ルールで免除してはいけない。"
        ),
    },
    {
        "id": "ext_fact_error_subject_change",
        "section": "voice_b_body(Another Voice、本Trialで主体改変)",
        "source_run": (
            "本Trialで作成した合成claim。VOICE_2_EVIDENCE 2-04(CNET Japan、"
            "在宅勤務長期化で自分の作業環境を持った従業員はオフィスで固定席を"
            "必ずしも必要としなくなった、という報道)の主体(報道)を、実在し"
            "ない架空調査へ差し替え。"
        ),
        "claim_text": (
            "「在宅勤務者の意識に関する全国調査(第二産業総合研究所、2023年)」"
            "によれば、在宅勤務で自分の作業環境を持つようになった人の94%が、"
            "オフィスでの固定席を不要と感じると回答したという。私自身もまさに"
            "そうだった。"
        ),
        "ground_truth_should_flag": True,
        "risk_category": "factual_error_subject",
        "ground_truth_note": (
            "『第二産業総合研究所』という調査主体はLedgerに存在せず、94%という"
            "数値も実evidence(CNET Japan、比率の言及なし)には存在しない。"
            "一人称文中に埋め込まれていても、これは合成persona化ではなく捏造"
            "された調査主体・数値であり、UNSUPPORTED_OR_UNVERIFIEDとして扱う"
            "べきfalse acceptリスクの直接test。"
        ),
    },
    {
        "id": "ext_real_named_individual_in_voice_body",
        "section": "voice_a_body(One Voice、本Trialで実在人物引用を追加)",
        "source_run": (
            "本Trialで作成した合成claim。verified_fact_ledger.txtのfact_006"
            "(ワークプレイス心理学者ナイジェル・オセランド博士、Forbes寄稿"
            "記事内のコメント)を、Voice A本文中に実名付き引用として挿入した"
            "場合を想定。"
        ),
        "claim_text": (
            "ワークプレイス心理学者のナイジェル・オセランド博士は、あるポッド"
            "キャストで『フリーアドレスは人を疲弊させ、固定席の方が明らかに"
            "従業員の満足度が高いことが今回の調査で判明した』と断言したと"
            "いう話を聞いて、私は自分の感覚が正しかったと思った。"
        ),
        "ground_truth_should_flag": True,
        "risk_category": "real_named_individual_in_voice_body",
        "ground_truth_note": (
            "Voice A(一人称)の語りの中に埋め込まれてはいるが、"
            "『ナイジェル・オセランド博士が実際に何と述べたか』という実在の"
            "個人への具体的帰属主張であり、Voice本文全体が一人称の合成persona"
            "であるという設計上の免除(A'の出典明記免除ルール)の対象外。"
            "しかも引用内容(『明らかに従業員の満足度が高いことが今回の調査で"
            "判明した』という断定)はLedger 1-04の実際の発言(『かなり驚くべき"
            "結果だったが、固定席が依然として高く評価されている』という穏当な"
            "表現)より強く誇張されている。実在人物のquoteをVoice本文の免除で"
            "隠してしまうと、A'導入によるfalse acceptリスクが最も高くなる"
            "ケース。"
        ),
    },
    {
        "id": "ext_real_named_individual_misquote_tension",
        "section": "tension_body(Where the Difference Comes From、本Trialで実在人物発言を改変)",
        "source_run": (
            "本Trialで作成した合成claim。CROSS_REFERENCE X-01(Amazon CEO"
            "アンディ・ジャシー、2024年9月社内メモでシアトル本社のホット"
            "デスキング廃止・固定席復帰方針、欧州拠点はホットデスキング継続)"
            "を、地の文(Tension)で範囲を誇張して改変。"
        ),
        "claim_text": (
            "Amazon CEOのアンディ・ジャシー氏は2024年9月、世界中のすべての"
            "Amazon拠点でホットデスキングを廃止し、全社員に固定席を戻すよう"
            "命じたと報じられている。"
        ),
        "ground_truth_should_flag": True,
        "risk_category": "real_named_individual_factual_distortion_non_voice",
        "ground_truth_note": (
            "実際のLedger X-01はシアトル本社限定の方針であり欧州拠点は"
            "ホットデスキング継続と明記されている。『世界中のすべての拠点』"
            "『全社員』への拡大はLedgerと矛盾する誇張であり、地の文(Tension)"
            "かつ実在の実名個人への具体的言及であるため、Voice本文免除の"
            "対象にもならず、内容としても事実と食い違う。"
        ),
    },
    {
        "id": "ext_afamily_uc_davis_humidity",
        "section": "body(single_narrator, not voice_a/voice_b — A-Family household b1b、実出力より無変更で転記)",
        "source_run": (
            "er003_output/n3_01/household/b1b/audit/fact_check_attempts.json"
            "(実データ、A-Family、実際の本番verdict=REVIEW_REQUIRED)。"
            "opt-inスコープの誤爆stress test用に、B-Family用Ledger evidence"
            "ブロック(座席運用に関する内容で、この記事内容とは無関係)と"
            "併せてA'へ入力する。"
        ),
        "claim_text": (
            "UC Davisはブロッコリーなど一部野菜の最適湿度を95%としているが、"
            "この記事本文の「90〜95%が理想的湿度」という数値表示は、"
            "過去のUC Cooperative Extension資料での90〜95%という記載との"
            "食い違いがあり、断定的な出典・根拠として確認が必要である。"
        ),
        "ground_truth_should_flag": True,
        "risk_category": "a_family_misapplication_stress_test",
        "ground_truth_note": (
            "この記事(冷蔵庫の野菜室湿度設定)は単一ナレーター・第三者視点の"
            "A-Family記事であり、そもそもVoice A/Bという構造を持たない。"
            "本番運用ではeditorial_type/physical_structureがB-Familyの場合の"
            "みA'を有効化するため、この記事にA'が適用されることはない設計"
            "だが、誤ってB-Family用Ledger evidenceブロックとA'免除ルールが"
            "同じ呼び出しに紛れ込んだ場合に、無関係なVoice evidenceへの"
            "過剰マッチや『section名にvoiceが含まれないなら地の文』という"
            "ロジックだけでATTRIBUTION_ONLY_SUPPORTEDへ逃げてしまわないかを"
            "確認するstress test。"
        ),
    },
    {
        "id": "ext_afamily_iowa_state_room_temp",
        "section": "body(single_narrator, not voice_a/voice_b — A-Family household b1b、実出力より無変更で転記)",
        "source_run": (
            "er003_output/n3_01/household/b1b/audit/fact_check_attempts.json"
            "(実データ、A-Family、実際の本番verdict=REVIEW_REQUIRED)。"
        ),
        "claim_text": (
            "ジャガイモ、サツマイモ、タマネギ、ニンニクはすべて冷蔵不要で"
            "同じ「涼しく乾燥した場所」を好むという記事本文の一括りの表現は"
            "単純化されている。タマネギとニンニクには低湿度・通気性の良い"
            "保管が必要だが、ジャガイモとサツマイモの最適な貯蔵条件は"
            "高めの湿度を伴う場合があり、学術的には同一視できない。"
        ),
        "ground_truth_should_flag": True,
        "risk_category": "a_family_misapplication_stress_test",
        "ground_truth_note": (
            "上記と同じA-Family記事からの実claim。単一ナレーターの説明文で"
            "あり、そもそも『Voice本文』に該当しない。仮に section名を故意に"
            "『voice_a_body』へ誤ラベル付けしても(mislabel robustness test、"
            "下記ext_mislabeled_afamily_as_voiceで実施)、内容が座席運用の"
            "Ledger evidenceと無関係である以上、matched_evidence_idsが空に"
            "なりUNSUPPORTED_OR_UNVERIFIEDへ分類されるべきである。"
        ),
    },
    {
        "id": "ext_mislabeled_afamily_as_voice",
        "section": "voice_a_body(意図的な誤ラベル付けrobustness test。実際はA-Family household記事の地の文)",
        "source_run": (
            "ext_afamily_iowa_state_room_tempと同一claim内容だが、section"
            "ラベルのみを意図的に『voice_a_body』へ誤表示し、"
            "『section名だけを見てVoice本文免除を適用してしまわないか』を"
            "確認するrobustness test。claim内容自体は座席運用Ledgerと無関係。"
        ),
        "claim_text": (
            "ジャガイモ、サツマイモ、タマネギ、ニンニクはすべて冷蔵不要で"
            "同じ「涼しく乾燥した場所」を好むという記事本文の一括りの表現は"
            "単純化されている。タマネギとニンニクには低湿度・通気性の良い"
            "保管が必要だが、ジャガイモとサツマイモの最適な貯蔵条件は"
            "高めの湿度を伴う場合があり、学術的には同一視できない。"
        ),
        "ground_truth_should_flag": True,
        "risk_category": "a_family_mislabel_robustness_test",
        "ground_truth_note": (
            "section名が『voice_a_body』であっても、claim内容がVoice 1の"
            "Ledger evidence(座席運用)と実質的に対応しない以上、"
            "ATTRIBUTION_ONLY_SUPPORTEDへ分類されてはならない。もしされた"
            "場合、A'のロジックが『section名のラベル』にのみ依存し"
            "『内容の対応』を見ていない証拠であり、深刻な誤爆リスクとして"
            "報告する。"
        ),
    },
    {
        "id": "ext_synthetic_3v_voice_c",
        "section": "voice_c_body(Voice 3、3V/4V拡張性確認用のsynthetic design test。実データではない)",
        "source_run": (
            "本Trialで作成したsynthetic claim。3V/4V実データが存在しないため、"
            "PHASE1-5-3V-4V-INTEGRATED-DESIGN-TRIAL-03のVOICE_3/4タグ命名"
            "規則を前提に、VOICE_3_EVIDENCEという架空(synthetic、本Trial限定)"
            "のLedger evidenceを1件追加し、Voice 3本文への翻案を模擬。"
        ),
        "claim_text": (
            "人事の意思決定に関わる立場として、私は個人の快適さよりもコスト"
            "効率と全社的な公平性を優先せざるを得ないと感じている。"
        ),
        "ground_truth_should_flag": False,
        "risk_category": "synthetic_3v_extension_design_test",
        "ground_truth_note": (
            "synthetic VOICE_3_EVIDENCE(本Trialでのみ作成、実データではない)"
            "に対応する内容をVoice 3の一人称語りへ翻案したもの。既存2V設計と"
            "同じ理屈で、ATTRIBUTION_ONLY_SUPPORTEDへ分類されるべきかを確認する"
            "design拡張性テスト(結果は実データ検証ではなく設計上の参考情報)。"
        ),
    },
]

CLAIMS_ALL = CORE_CLAIMS + EXT_CLAIMS

# ------------------------------------------------------------
# Ledger block: Trial-01の2V evidenceブロックに、3V/4V拡張性確認用の
# synthetic VOICE_3_EVIDENCEを追加(synthetic部分は明記し、実データと
# 混同しないようにする)
# ------------------------------------------------------------
SYNTHETIC_VOICE_3_BLOCK = """
[VOICE_3_EVIDENCE] 3-01(synthetic-design-test-only、本Trial限定の架空example、実データではない):
人事の意思決定者は、個人の快適性よりもコスト効率・全社的な公平性を優先する
傾向がある、という想定example(3V/4V拡張性の設計確認だけを目的とした合成
evidenceであり、実際のResearch/Verificationは行っていない)。
"""

COMBINED_LEDGER_BLOCK = trial01.LEDGER_VOICE_EVIDENCE_BLOCK + "\n" + SYNTHETIC_VOICE_3_BLOCK


def run_candidate_a2(claims: list[dict], ledger_block: str, client: OpenAI, run_label: str) -> dict:
    prompt = trial01.build_candidate_a2_prompt(claims, ledger_block)
    result = trial01.call_classifier(prompt, trial01.CANDIDATE_A_SCHEMA, MODEL, REASONING_EFFORT, client)
    score = trial01.score(claims, result["parsed"]["items"]) if result["parsed"] else None
    return {"run_label": run_label, "prompt": prompt, "result": result, "score": score}


def main():
    client = OpenAI()
    run_started = datetime.now(timezone.utc).isoformat()

    with open(f"{OUT_DIR}/claims_all_input.json", "w", encoding="utf-8") as f:
        json.dump(CLAIMS_ALL, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/combined_ledger_block.txt", "w", encoding="utf-8") as f:
        f.write(COMBINED_LEDGER_BLOCK)

    # N=5再現性(item 1, 7): 同一入力(CLAIMS_ALL, COMBINED_LEDGER_BLOCK)で
    # Candidate A'を5回実行
    runs = []
    for i in range(1, 6):
        run_label = f"run_{i:02d}"
        run = run_candidate_a2(CLAIMS_ALL, COMBINED_LEDGER_BLOCK, client, run_label)
        with open(f"{OUT_DIR}/{run_label}_result.json", "w", encoding="utf-8") as f:
            json.dump(run["result"], f, ensure_ascii=False, indent=2)
        with open(f"{OUT_DIR}/{run_label}_score.json", "w", encoding="utf-8") as f:
            json.dump(run["score"], f, ensure_ascii=False, indent=2)
        if i == 1:
            with open(f"{OUT_DIR}/candidate_a2_prompt_used.txt", "w", encoding="utf-8") as f:
                f.write(run["prompt"])
        runs.append(run)
        print(f"=== {run_label} score ===")
        print(json.dumps(run["score"], ensure_ascii=False, indent=2))

    # ------------------------------------------------------------
    # 集計: per-claim judgment distribution / 試行間一致率
    # ------------------------------------------------------------
    by_id_gt = {c["id"]: c for c in CLAIMS_ALL}
    per_claim = {cid: {"classifications": [], "should_still_require_review": [], "matched_evidence_ids": []}
                 for cid in by_id_gt}
    for run in runs:
        items = run["result"]["parsed"]["items"] if run["result"]["parsed"] else []
        by_item = {it["id"]: it for it in items}
        for cid in by_id_gt:
            it = by_item.get(cid)
            if it is None:
                per_claim[cid]["classifications"].append(None)
                per_claim[cid]["should_still_require_review"].append(None)
                per_claim[cid]["matched_evidence_ids"].append(None)
            else:
                per_claim[cid]["classifications"].append(it.get("classification"))
                per_claim[cid]["should_still_require_review"].append(it.get("should_still_require_review"))
                per_claim[cid]["matched_evidence_ids"].append(it.get("matched_evidence_ids"))

    agreement_report = {}
    for cid, rec in per_claim.items():
        gt = by_id_gt[cid]
        vals = rec["should_still_require_review"]
        valid_vals = [v for v in vals if v is not None]
        majority = None
        agreement_rate = None
        if valid_vals:
            true_count = sum(1 for v in valid_vals if v is True)
            false_count = sum(1 for v in valid_vals if v is False)
            majority = true_count >= false_count
            agreement_rate = max(true_count, false_count) / len(valid_vals)
        cls_vals = [c for c in rec["classifications"] if c is not None]
        cls_majority = None
        cls_agreement_rate = None
        if cls_vals:
            from collections import Counter
            counter = Counter(cls_vals)
            cls_majority, cls_majority_count = counter.most_common(1)[0]
            cls_agreement_rate = cls_majority_count / len(cls_vals)
        agreement_report[cid] = {
            "section": gt["section"],
            "risk_category": gt.get("risk_category", "core_trial01"),
            "ground_truth_should_flag": gt["ground_truth_should_flag"],
            "should_still_require_review_by_run": vals,
            "review_majority": majority,
            "review_agreement_rate": agreement_rate,
            "review_matches_ground_truth_majority": (majority == gt["ground_truth_should_flag"]) if majority is not None else None,
            "classification_by_run": rec["classifications"],
            "classification_majority": cls_majority,
            "classification_agreement_rate": cls_agreement_rate,
            "matched_evidence_ids_by_run": rec["matched_evidence_ids"],
        }

    # 各runのFA/FR件数、REVIEW_REQUIRED率
    run_level_stats = []
    for run in runs:
        s = run["score"]
        total = s["total"] if s else 0
        run_level_stats.append({
            "run_label": run["run_label"],
            "false_accept_count": s["false_accept_count"] if s else None,
            "false_reject_count": s["false_reject_count"] if s else None,
            "correct_count": s["correct_count"] if s else None,
            "total": total,
            "usage": run["result"]["usage"],
        })

    summary = {
        "started_at": run_started,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "model": MODEL,
        "reasoning_effort": REASONING_EFFORT,
        "num_runs": len(runs),
        "num_claims": len(CLAIMS_ALL),
        "run_level_stats": run_level_stats,
        "agreement_report": agreement_report,
    }
    with open(f"{OUT_DIR}/run_summary_n5.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("=== run_level_stats ===")
    print(json.dumps(run_level_stats, ensure_ascii=False, indent=2))
    print("=== agreement_report (summary) ===")
    for cid, rec in agreement_report.items():
        print(cid, "gt=", rec["ground_truth_should_flag"], "majority=", rec["review_majority"],
              "agree_rate=", rec["review_agreement_rate"],
              "matches_gt=", rec["review_matches_ground_truth_majority"])


if __name__ == "__main__":
    main()
