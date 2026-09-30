# -*- coding: utf-8 -*-
# ============================================================
# er051_open233_checker_trial_variant_01.py
# OPEN-233-CHECKER-REDESIGN-TRIAL-01 (Phase A、委任_01)
# ============================================================
# 目的: Ledger Deviation Checker再設計(v0.2)のFamily X限定Trial variant
# (V1=post-hoc v2のみ/V2=Prompt+schema variant+post-hoc v2/V3=V2+notes
# factual_constraintのみ)を実装する。
#
# 重要な設計制約(委任文より):
# - Production code(er003_v1_en_direct_vfl_01_generate.py、以下vfl01)は
#   一切変更しない。本ファイルはvfl01を**importのみ**で使用し
#   (グローバル定数・関数を読み取り専用で参照)、vfl01側のモジュール
#   レベル定数・関数を上書き/monkeypatchしない。
# - Production Prompt/schema/severity/routingは変更しない。本ファイルの
#   3層(BLOCKING/QUALITY/ACCEPTABLE)分類・schema拡張・Prompt差分ブロックは
#   すべてTrial限定(Family X限定)であり、Production経路(er012_e_family_
#   entertainment_two_level_runner_01.py等)からは呼び出されない。
# - Phase A(本委任)ではTrial実行(有料API呼び出し)を行わない。
#   `run_trial_deviation_check()`はTrial実行時(将来の別委任)に使う
#   実装であり、本委任のテスト(er051_open233_checker_trial_variant_01_
#   test_01.py)はネットワーク呼び出しを一切行わない(既存
#   er050_output/配下の保存済みrun jsonを再生[replay]して検証する)。
#
# 設計書: docs/pm/design_open233_checker_redesign_trial_01.md
from __future__ import annotations

import hashlib
import json
import re
import time

import er003_v1_en_direct_vfl_01_generate as vfl01

OUT_DIR = "er051_output/open233_checker_trial_variant_01"

# ------------------------------------------------------------
# 委任_27 Part1-5(OPEN-233-SELF-RECOVERY-TRIAL-01、design書§0/§4-18):
# ユーザー上位原則「重大誤解原則」(2026-10-01)をStage1(V4A)判定の最初の
# 問いとして追加する変種。vfl01.DEVIATION_DEVELOPER_MESSAGE(Production
# 定数)自体は変更せず、読み取り専用で参照して新しい文字列を作るのみ
# (Production非接続)。**本委任ではrun_trial_deviation_checkへ未配線**
# (予算制約、design書§4-18に既知の未検証事項として記載)。
# ------------------------------------------------------------
MISCONCEPTION_PRINCIPLE_TEXT = """
【重大誤解原則(2026-10-01ユーザー指示、最初の問い)】
まず「この違いは英語学習者に記事の本質について重大な誤解を与えるか」を
判断してください。主要な意味・主体・方向・規模・時間軸を誤認させる場合
のみBLOCKINGとしてください。用語の近似・一般化(例: Brent futures→
oil prices、Brent crude futures→crude prices)・数値丸め(例: 2.6%→
about 3%、above 85 dollars→about 85 dollars)・確認済みFactから自然に
導ける解釈や演出は、厳密には違うというだけの理由でBLOCKINGにしないで
ください。一方、以下のような違いは記事の本質的な誤解を招くため明確に
BLOCKINGとしてください: 特定の指標(例: Brent futures)を無関係な
商品(例: gasoline prices)や世界全体の価格(world energy prices)へ
一般化する、1企業の株価を株式市場全体の動きとして述べる、方向を反転
させる(上昇→下落)、主体を別の主体へ入れ替える、継続していた出来事を
一度消えて戻った出来事として述べる、未確認の人物・行動・動機・具体的な
数字を追加する、因果関係を逆転させる。"""

V4A_DEVELOPER_MSG_WITH_MISCONCEPTION_PRINCIPLE = (
    vfl01.DEVIATION_DEVELOPER_MESSAGE + "\n" + MISCONCEPTION_PRINCIPLE_TEXT
)

# ------------------------------------------------------------
# post-hoc v2: deterministic昇格ルール(ユーザー決定2)
# ------------------------------------------------------------
# changed_actor/changed_number/changed_negation/changed_comparisonの
# いずれかがtrueかつ既存severityがMINORの場合、severity_final=BLOCKINGへ
# 昇格する(設計書§3-1)。
PROMOTABLE_FLAG_KEYS = ["changed_actor", "changed_number", "changed_negation", "changed_comparison"]

VARIANTS = ("V0", "V1", "V2", "V3", "V4A")


def classify_deviation_trial(deviation: dict, variant: str) -> dict:
    """1件のdeviation dict(既存vfl01._apply_deviation_post_hoc_validation()
    適用後の形、severity/10フラグ/explanationを持つ。schema variant使用時は
    追加でqualifier_present/qualifier_text/ledger_field_basis/
    observation_consistent/matched_notes_idを持ちうる)へ、severity_final/
    action/basis/rule_idを追加する(deviation自体は変更せずcopyを返す)。

    優先順位(設計書§3-1):
    1. 既存severity=="MAJOR" -> BLOCKING(fail-closed維持、ユーザー決定1)
    2. 4カテゴリいずれかのflag=trueでseverity=MINOR -> BLOCKING(昇格)
    3. それ以外(MINORかつ4カテゴリ非該当) -> variant別にQUALITY/ACCEPTABLE

    origin fieldは一切参照しない(v0.2 §1-E/§6-1が実データで確認した
    「JA段origin=None誤降格の罠」を踏まえ、「causality-only &
    origin!=ja_source -> demote」のようなorigin基準の非STOP化ルールは
    本関数に実装しない)。
    """
    if variant not in VARIANTS:
        raise ValueError(f"unknown variant: {variant}")

    d = dict(deviation)
    triggered = [k for k in PROMOTABLE_FLAG_KEYS if bool(d.get(k))]

    if d.get("severity") == "MAJOR":
        d["severity_final"] = "BLOCKING"
        d["action"] = "STOP"
        d["basis"] = "ledger_fact"
        d["rule_id"] = "existing_major_v2"
        return d

    if triggered:
        d["severity_final"] = "BLOCKING"
        d["action"] = "STOP"
        d["basis"] = "deterministic_flag:" + ",".join(triggered)
        d["rule_id"] = "promote_deterministic_flag_v1"
        return d

    # MINOR、4カテゴリ非該当
    if variant in ("V0", "V1"):
        # V0はPrompt/schema/post-hoc全て現行のまま(本関数は比較用にのみ
        # 使用、Trial実行での実際の判定には現行overall_statusを使う)。
        # V1はpost-hoc v2(昇格のみ)、schema variant未使用のため
        # QUALITY/ACCEPTABLEを区別する追加シグナルを持たない。安全側の
        # デフォルトとしてQUALITY(通過+ログ)にする。
        d["severity_final"] = "QUALITY"
        d["action"] = "LOG_AND_PASS"
        d["basis"] = "model_minor_no_schema_signal"
        d["rule_id"] = "default_quality_v1"
        return d

    # V2/V3: schema variantフィールドがあれば使う
    ledger_field_basis = d.get("ledger_field_basis")
    observation_consistent = d.get("observation_consistent")

    # 必須の除外条件(v0.2 §6-3): factual_constraintの明示禁止パターンと
    # 一致する場合、qualifier(留保文)の有無に関わらず非STOP化しない。
    if ledger_field_basis == "notes_factual_constraint" and observation_consistent is False:
        d["severity_final"] = "BLOCKING"
        d["action"] = "STOP"
        d["basis"] = "notes_factual_constraint_conflict"
        d["rule_id"] = "factual_constraint_override_v1"
        return d

    if observation_consistent is True and ledger_field_basis == "ledger_fact":
        d["severity_final"] = "ACCEPTABLE"
        d["action"] = "PASS"
        d["basis"] = "ledger_fact_consistent"
        d["rule_id"] = "acceptable_consistent_v1"
        return d

    if observation_consistent is True:
        d["severity_final"] = "QUALITY"
        d["action"] = "LOG_AND_PASS"
        d["basis"] = ledger_field_basis or "unknown"
        d["rule_id"] = "quality_consistent_v1"
        return d

    # observation_consistentがFalse/None/未指定(旧データreplay含む) ->
    # 安全側のデフォルト(ACCEPTABLEへは倒さない)
    d["severity_final"] = "QUALITY"
    d["action"] = "LOG_AND_PASS"
    d["basis"] = ledger_field_basis or "no_schema_signal"
    d["rule_id"] = "default_quality_v2_conservative"
    return d


def classify_parsed_result_trial(parsed: dict, variant: str) -> dict:
    """vfl01.run_deviation_check()の戻り値parsed(deviations配列+
    overall_status)へclassify_deviation_trial()を適用し、
    overall_action_trial(STOP/LOG_AND_PASS/PASS)を追加する。"""
    deviations = [classify_deviation_trial(d, variant) for d in parsed.get("deviations", [])]
    if any(d["severity_final"] == "BLOCKING" for d in deviations):
        overall_action_trial = "STOP"
    elif any(d["severity_final"] == "QUALITY" for d in deviations):
        overall_action_trial = "LOG_AND_PASS"
    else:
        overall_action_trial = "PASS"
    return {
        "deviations": deviations,
        "overall_status": parsed.get("overall_status"),
        "overall_action_trial": overall_action_trial,
        "variant": variant,
    }


# ------------------------------------------------------------
# Prompt variant(Family X限定、vfl01.DEVIATION_PROMPT_TEMPLATE本体は不変)
# ------------------------------------------------------------
TRIAL_PROMPT_DIFF_BLOCK_V01 = """

【Family X限定 Trial追加指示(OPEN-233-CHECKER-REDESIGN-TRIAL-01、Production非適用)】
- claim単体だけでなく、その前後1〜2文の限定語・留保文(qualifier/hedge)を踏まえて、
  記事の最終的な理解がVerified Fact Ledgerの観測と矛盾しないかをobservation_consistentとして
  判定してください。
- 限定語・留保文(例: "may", "some", "temporarily", "briefly"等およびその訳語)がclaim自体
  またはその前後1〜2文に存在する場合、qualifier_presentをtrueとし、該当箇所をqualifier_text
  に記録してください。存在しない場合はfalseとし、qualifier_textは空文字列にしてください。
  留保文が存在するだけで機械的にobservation_consistent=trueにはしないでください
  (定型ヘッジによる免罪符化を禁止します)。
- Verified Fact Ledgerのnotesには、判定根拠として使用すべき禁止・限定事項
  (factual_constraint)が含まれる場合があります。判定の根拠がfactual_constraintの記述と
  一致・矛盾する場合はledger_field_basisを"notes_factual_constraint"とし、一致する
  fact_idをmatched_notes_idに記録してください。Factの本体フィールド
  (claim/scope/numeric_value/causal_strength等)のみを根拠にした場合はledger_field_basis
  を"ledger_fact"としてください。
- writer_guidance(トーン・文体等の執筆助言であり、factual_constraintではないもの)は
  判定根拠として使用しないでください。
- 各deviationについて、qualifier_present/qualifier_text/ledger_field_basis/
  observation_consistent/matched_notes_idを必ず出力してください。"""


# ------------------------------------------------------------
# V4-A差分ブロック(Step2診断の原因分類、委任_03): changed_actorと
# unsupported_new_claimのカテゴリ境界明確化。Fable判定(2)により、fixture
# 固有の文言(実在の研究者名・記事の固有名詞等)は含めない一般的な境界記述
# とする。changed_number/negation/comparisonについても同一原則(他カテゴリと
# の同時true許容)を一文で明記する。V2のPrompt差分ブロック
# (TRIAL_PROMPT_DIFF_BLOCK_V01)に追記する形で連結し、schema variant・
# post-hoc v2(classify_deviation_trial)はV2と同一とする(設計書§1-補(2))。
# ------------------------------------------------------------
TRIAL_PROMPT_DIFF_BLOCK_V4A = """

【Family X限定 Trial追加指示(V4-A、OPEN-233-CHECKER-REDESIGN-TRIAL-01、Production非適用)】
- 上記10種類のカテゴリは互いに排他的ではありません。1つの逸脱の内容が複数カテゴリの定義に
  同時に該当する場合は、該当するカテゴリを全てtrueにしてください(最も強く該当する1つだけに
  絞る必要はありません)。
- 特に、Ledgerが特定している主体(行為者・被行為者・発言者)が、記事では別の主体に置き換わって
  いる場合は、その置き換えが新規の具体的主張(unsupported_new_claim)を伴っていても、必ず
  changed_actorもtrueにしてください(changed_actorとunsupported_new_claimは同時にtrueで
  構いません。主体の置き換えをunsupported_new_claimだけに分類しないでください)。
- 同じ原則を、changed_number(Ledgerと異なる数値・割合・件数への変更)・changed_negation
  (肯定・否定の反転)・changed_comparison(比較方向の反転・変更)にも適用してください。これらに
  明確に該当する変更が生じている場合は、他のカテゴリ(changed_fact/unsupported_new_claim等)と
  重複してでも、必ず該当カテゴリをtrueにしてください。"""


def build_trial_prompt_template(variant: str) -> str:
    """V0/V1はvfl01.DEVIATION_PROMPT_TEMPLATEをそのまま返す(Prompt変更なし)。
    V2/V3は差分ブロックを末尾に連結した文字列を返す(vfl01側の定数自体は
    書き換えない)。V4AはV2の差分ブロックにさらにカテゴリ境界明確化ブロック
    (TRIAL_PROMPT_DIFF_BLOCK_V4A)を連結した文字列を返す。"""
    if variant not in VARIANTS:
        raise ValueError(f"unknown variant: {variant}")
    if variant == "V4A":
        return vfl01.DEVIATION_PROMPT_TEMPLATE + TRIAL_PROMPT_DIFF_BLOCK_V01 + TRIAL_PROMPT_DIFF_BLOCK_V4A
    if variant in ("V2", "V3"):
        return vfl01.DEVIATION_PROMPT_TEMPLATE + TRIAL_PROMPT_DIFF_BLOCK_V01
    return vfl01.DEVIATION_PROMPT_TEMPLATE


# ------------------------------------------------------------
# schema variant(Trial出力schema、vfl01.DEVIATION_JSON_SCHEMA本体は不変)
# ------------------------------------------------------------
TRIAL_SCHEMA_EXTRA_PROPS = {
    "qualifier_present": {"type": "boolean"},
    "qualifier_text": {"type": "string"},
    "ledger_field_basis": {
        "type": "string",
        "enum": ["ledger_fact", "notes_factual_constraint", "notes_writer_guidance", "none"],
    },
    "observation_consistent": {"type": "boolean"},
    "matched_notes_id": {"type": "string"},
}
TRIAL_SCHEMA_EXTRA_KEYS = list(TRIAL_SCHEMA_EXTRA_PROPS.keys())


def build_trial_deviation_item_schema(include_related_fact_id: bool = False, include_origin: bool = False) -> dict:
    """vfl01._extended_deviation_item_schema()(既存拡張、hook_aware/
    related_fact_id/origin)を土台に、Trial限定の5フィールドを追加する。
    vfl01側の関数はread-onlyで呼び出すのみ(vfl01は変更しない)。"""
    base = vfl01._extended_deviation_item_schema(False, include_related_fact_id, include_origin)
    props = dict(base["properties"])
    props.update(TRIAL_SCHEMA_EXTRA_PROPS)
    required = list(base["required"]) + TRIAL_SCHEMA_EXTRA_KEYS
    return {"type": "object", "properties": props, "required": required, "additionalProperties": False}


def build_trial_deviation_schema(variant: str, include_related_fact_id: bool = False,
                                  include_origin: bool = False) -> dict:
    """V0/V1はvfl01の既存schema(必要に応じてrelated_fact_id/origin拡張のみ)
    をそのまま返す。V2/V3/V4AはTrial限定5フィールドを追加したschemaを返す
    (V4AのschemaはV2と同一、設計書§1-補(2))。"""
    if variant not in VARIANTS:
        raise ValueError(f"unknown variant: {variant}")
    if variant not in ("V2", "V3", "V4A"):
        if include_related_fact_id or include_origin:
            return vfl01._build_extended_deviation_schema(False, include_related_fact_id, include_origin, False)
        return vfl01.DEVIATION_JSON_SCHEMA

    item_schema = build_trial_deviation_item_schema(include_related_fact_id, include_origin)
    return {
        "name": f"open233_trial_deviation_schema_{variant.lower()}",
        "schema": {
            "type": "object",
            "properties": {"deviations": {"type": "array", "items": item_schema}},
            "required": ["deviations"],
            "additionalProperties": False,
        },
        "strict": True,
    }


# ------------------------------------------------------------
# notes_for_writer分類(Phase Aで実施、設計書§3-2)
# ------------------------------------------------------------
# Hormuz HF-001〜012: 全件factual_constraint
# (docs/pm/review_ledger_deviation_redesign_01_part_b.md Part B分類を使用)。
HORMUZ_NOTES_CLASSIFICATION = {f"HF-{i:03d}": "factual_constraint" for i in range(1, 13)}

# Meta Ledger MUSE-HC-001〜015: 本Phase Aで新規分類(設計書§3-2表)。
# 出典: er019_output/family_x_b3_production_wiring_01/run_01/b1b/audit/
# deviation_checks/advanced_attempt1.json (prompt埋め込みLedgerテキスト)。
META_NOTES_CLASSIFICATION = {f"MUSE-HC-{i:03d}": "factual_constraint" for i in range(1, 16)}


def filter_ledger_notes_by_classification(ledger_text: str, classification: dict) -> str:
    """ledger_text(vfl01.build_verified_ledger_text()が生成する形式)から、
    classificationで"writer_guidance"に分類されたfact_idのnotes_for_writer
    行のみを除去する(factual_constraintは残す)。classificationに存在
    しないfact_idは安全側でfactual_constraint扱い(除去しない)。"""
    id_pattern = re.compile(r"^\[(?:VERIFIED|AMBIGUOUS[^\]]*)\]\s*([^:]+):")
    blocks = ledger_text.split("\n\n")
    out_blocks = []
    for block in blocks:
        m = id_pattern.match(block.strip())
        if not m:
            out_blocks.append(block)
            continue
        fact_id = m.group(1).strip()
        cls = classification.get(fact_id, "factual_constraint")
        if cls == "writer_guidance":
            lines = [ln for ln in block.split("\n") if not ln.strip().startswith("notes_for_writer:")]
            block = "\n".join(lines)
        out_blocks.append(block)
    return "\n\n".join(out_blocks)


# ------------------------------------------------------------
# Trial実行時(将来の別委任)にのみ使用する呼び出し関数。
# Phase A(本委任)ではテストから一切呼び出さない(ネットワーク呼び出しなし)。
# ------------------------------------------------------------
def run_trial_deviation_check(client, verified_ledger_text: str, article_text: str, model: str, variant: str,
                               include_related_fact_id: bool = False, source_article_text: str | None = None,
                               developer_message_override: str | None = None) -> dict:
    """V2/V3用: Trial Prompt/schemaでvfl01と同形式のResponses API呼び出しを
    行う(vfl01.run_deviation_check()はPrompt差し替えを受け付けないため、
    Trial専用に薄いラッパーとして実装。vfl01の関数・定数は読み取り専用で
    使うのみ)。V0/V1で新規API呼び出しは不要(既存er050_output/の
    raw_parsedをclassify_parsed_result_trial()へ再適用するだけで計算できる、
    設計書§4)。

    委任_27 Part1-5(design書§4-18): `developer_message_override`(既定
    None)を追加した。Noneの場合は従来どおり`vfl01.DEVIATION_DEVELOPER_
    MESSAGE`(Production定数、読み取り専用参照)をそのまま使う(既存呼び
    出し元9箇所は全て無変更のまま動作する)。値を渡した場合のみ、その
    文字列をdeveloper roleへ使う(例:
    `V4A_DEVELOPER_MSG_WITH_MISCONCEPTION_PRINCIPLE`、重大誤解原則の
    追加検証用、本委任では未配線)。"""
    prompt_template = build_trial_prompt_template(variant)
    prompt = prompt_template.format(verified_ledger_text=verified_ledger_text, article_text=article_text)
    include_origin = source_article_text is not None
    if include_related_fact_id:
        prompt += vfl01.RELATED_FACT_ID_INSTRUCTION
    if include_origin:
        prompt += vfl01.ORIGIN_INSTRUCTION_TEMPLATE.format(source_article_text=source_article_text)

    schema = build_trial_deviation_schema(variant, include_related_fact_id, include_origin)
    developer_message = developer_message_override or vfl01.DEVIATION_DEVELOPER_MESSAGE

    t0 = time.time()
    response = client.responses.create(
        model=model,
        reasoning={"effort": vfl01.REASONING_EFFORT},
        text={"format": {"type": "json_schema", **schema}},
        input=[
            {"role": "developer", "content": developer_message},
            {"role": "user", "content": prompt},
        ],
    )
    elapsed = round(time.time() - t0, 3)
    text = response.output_text
    raw_parsed = json.loads(text)
    parsed = vfl01._apply_deviation_post_hoc_validation(raw_parsed)
    parsed_trial = classify_parsed_result_trial(parsed, variant)

    usage = getattr(response, "usage", None)
    input_tokens = getattr(usage, "input_tokens", None) if usage else None
    output_tokens = getattr(usage, "output_tokens", None) if usage else None
    cached_tokens = None
    reasoning_tokens = None
    if usage is not None:
        in_details = getattr(usage, "input_tokens_details", None)
        if in_details is not None:
            cached_tokens = getattr(in_details, "cached_tokens", None)
        out_details = getattr(usage, "output_tokens_details", None)
        if out_details is not None:
            reasoning_tokens = getattr(out_details, "reasoning_tokens", None)

    return {
        "prompt": prompt, "raw_text": text, "raw_parsed": raw_parsed, "parsed": parsed_trial,
        "model": response.model, "response_id": response.id, "variant": variant,
        "usage": {
            "input_tokens": input_tokens, "cached_input_tokens": cached_tokens,
            "output_tokens": output_tokens, "reasoning_tokens": reasoning_tokens,
        },
        "elapsed_seconds": elapsed,
    }


# ------------------------------------------------------------
# replay用ユーティリティ(既存er050_output/配下の保存済みrun jsonを再利用)
# ------------------------------------------------------------
V0_OUT_DIR = "er050_output/gpt6_checker_comparison_trial_01"


def load_v0_parsed(step_dir: str, fixture_id: str, model: str, attempt: int = 1) -> dict:
    """V0(GPT6-MODEL-COMPARISON-TRIAL-01)で保存済みのrun_N.jsonから
    parsed(既存post-hoc validation適用後のdeviations+overall_status)を
    読み込む。新規API呼び出しは行わない(設計書§4のV0/V1再利用方式)。"""
    path = f"{V0_OUT_DIR}/{step_dir}/{fixture_id}/{model}/run_{attempt}.json"
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    return d["parsed"]


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()
