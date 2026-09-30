# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_stage2_calibration_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (Self-Recovery Flow, Phase 1、委任_08 作業A)
# ============================================================
# 目的: 委任_07で発見されたStage2較正リスク(per-claim Stage2でReal-but-
# fixable群[B1-c/B4-a]がQUALITYへ誤降格)に対し、Fable判定(§1、Safety方向の
# 較正=ユーザー指示の自律範囲)に基づき、rubric較正Trialを実行する。
#
# variant:
# - R1 = 現行rubric(er052_open233_self_recovery_stage2_production_01.
#   MATERIALITY_RUBRIC、対照)。既存出力(B1/B4計6claim分)を再利用し新規
#   callは行わない。
# - R2 = 較正rubric(本ファイルRUBRIC_R2)。QUALITYを「Ledgerに記録された
#   観測同士の関係付け・強調・言い回し」に限定し、Ledgerに無い新規の具体的
#   主張(製品・仕組み・動機・理由・因果・数値・主体・時期)を最優先で
#   BLOCKINGへ倒す。batch(instance単位1call)で新規call。
# - R3 = R2のLLM出力 + post-hoc deterministic floor(Stage1のunsupported_
#   new_claim=trueかつR2のbasisがledger_claim/ledger_scope/ledger_
#   conditions/notes_for_writerのいずれでもない場合、BLOCKINGへ強制)。
#   新規APIコールなし(R2の出力を再利用)。
#
# 重要な設計制約(既存er051/er052系Trialと同一原則):
# - Production code(er003_v1_en_direct_vfl_01_generate.py)は一切変更しない。
# - Model Routing Contractは経由しない。
# - API keyは環境変数のみ。保存jsonにはprompt本体ではなくsha256のみ記録。
# - 既存er052_open233_self_recovery_stage2_production_01.pyは変更しない
#   (rubric較正はTrial専用の本ファイル内で完結させる)。
from __future__ import annotations

import argparse
import json
import os
import time

import er003_v1_en_direct_vfl_01_generate as vfl01
import er050_gpt6_checker_comparison_trial_01 as g6
import er052_open233_self_recovery_phase1_step3_stage1_compare_01 as step3cmp
import er052_open233_self_recovery_stage2_production_01 as s2p

OUT_DIR = "er052_output/open233_self_recovery_stage2_calibration_01"
BUDGET_STATE_PATH = f"{OUT_DIR}/budget_state_c233l_a.json"
TOTAL_BUDGET_JPY = 12.0  # 委任_08 作業A Guardrail
MAX_RETRIES_PER_CALL = 2
MAX_CONSECUTIVE_ERRORS = 3
N_RUNS = 2  # design書委任文の想定どおりn=2

RUBRIC_R2 = """【材料性(materiality)の判定基準・較正版(R2、委任_08)】
- QUALITY: Ledgerに記録された観測同士の関係付け・強調・言い回しに限る。Ledgerが実際に
  記録した2つ以上の観測を、因果接続詞・強調・言い回しでつないでいるだけで、新しい具体的
  主張を何も追加していない場合のみQUALITYとする。
- BLOCKING: Ledgerに存在しない新規の具体的主張(製品仕様・仕組み・動機・理由・因果関係・
  数値・主体・時期のいずれか)を1つでも追加している場合はBLOCKINGとする。Ledgerのclaim/
  scope/numeric_value/date_or_period/conditionsのいずれかと矛盾する場合、Ledgerが別の
  原因・別の主体を明記しているのに異なるものを述べる場合、notes_for_writerが明示的に
  禁じた断定をしている場合も同様にBLOCKINGとする。「Ledgerの観測と矛盾しない関係付け
  だから」という理由だけでQUALITYへ倒してはならない。新規の具体的主張が1つでも含まれる
  かどうかを最優先で確認すること。
- ACCEPTABLE: Ledgerに無い新規の固有名詞・数値・時期・主体・因果・仕組みを一切加えず
  (Ledgerに既出の固有名詞を繰り返すことはこの制約に抵触しない)、Ledgerが確認した事象の
  一般常識レベルの背景説明・条件付きの一般論にとどまる場合のみ。
- 上記のどれに該当するか迷う場合は、BLOCKINGとしてください(fail-closed)。"""

R3_FLOOR_SAFE_BASIS = {"ledger_claim", "ledger_scope", "ledger_conditions", "notes_for_writer"}


class TrialAbort(RuntimeError):
    pass


def load_budget_state() -> dict:
    if os.path.exists(BUDGET_STATE_PATH):
        with open(BUDGET_STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}


def save_budget_state(state: dict) -> None:
    os.makedirs(os.path.dirname(BUDGET_STATE_PATH), exist_ok=True)
    with open(BUDGET_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def check_budget(state: dict) -> None:
    if state["cumulative_jpy"] >= TOTAL_BUDGET_JPY:
        raise TrialAbort(f"累計¥{state['cumulative_jpy']:.3f}が委任_08 作業A Guardrail¥{TOTAL_BUDGET_JPY}に到達")


def save_json(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


# ------------------------------------------------------------
# batch call(rubric差替え版、s2p.run_stage2_batchと同一構造だがrubric_textを
# 引数化する。s2p.py自体は変更しない)
# ------------------------------------------------------------
def run_stage2_batch_variant(client, verified_ledger_text: str, source_article_text: str | None,
                              claims: list, rubric_text: str, model: str = s2p.MODEL) -> dict:
    blocks = []
    for i, c in enumerate(claims):
        blocks.append(
            f"[claim_index={i}]\nclaim: {c['claim_text']}\n"
            f"ローカル文脈(段落±1): {c['local_context']}\n"
            f"origin: {c.get('origin') or '(不明)'}\n"
            f"related_fact_id: {c.get('related_fact_id') or '(不明)'}"
        )
    claims_block = "\n\n".join(blocks)
    prompt = s2p.BATCH_PROMPT_TEMPLATE.format(
        verified_ledger_text=verified_ledger_text,
        source_article_text=source_article_text or "(なし)",
        claims_block=claims_block,
        materiality_rubric=rubric_text,
    )
    t0 = time.time()
    response = client.responses.create(
        model=model,
        reasoning={"effort": vfl01.REASONING_EFFORT},
        text={"format": {"type": "json_schema", **s2p.BATCH_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": s2p.STAGE2_PROD_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    elapsed = round(time.time() - t0, 3)
    parsed = json.loads(response.output_text)
    usage_dict = s2p._extract_usage(response)
    return {
        "prompt_sha256": s2p.sha256_text(prompt), "parsed": parsed, "model": response.model,
        "response_id": response.id, "usage": usage_dict,
        "cost_jpy": round(s2p.official_cost_jpy(usage_dict), 4), "elapsed_seconds": elapsed,
    }


# ------------------------------------------------------------
# 評価セット(14 instance相当、13 batch call)の構築
# ------------------------------------------------------------
def _claim(sub_id, claim_text, correct_label, origin=None, related_fact_id=None,
           unsupported_new_claim=False):
    return {
        "sub_id": sub_id, "claim_text": claim_text, "correct_label": correct_label,
        "origin": origin, "related_fact_id": related_fact_id,
        "unsupported_new_claim": unsupported_new_claim,
    }


def build_eval_groups() -> list:
    g6_step2 = {f["id"]: f for f in g6.step2_fixtures()}
    g6_step1 = {f["id"]: f for f in g6.step1_fixtures()}
    g6_step3 = {f["id"]: f for f in g6.step3_fixtures()}

    b1 = g6_step2["B1"]
    b2 = g6_step2["B2_hormuz"]
    b3 = g6_step2["B3"]
    b4 = g6_step2["B4"]
    meta = g6_step2["Meta_run03_standard"]
    hormuz = g6_step3["hormuz_run03_standard"]

    groups = [
        {
            "group_id": "B1", "fixture": b1,
            "claims": [
                _claim("B1-a", "ホルムズ海峡は、中東から原油を運ぶ船が多く通る重要な海の道だ。",
                       "ACCEPTABLE", unsupported_new_claim=False),
                _claim("B1-b", "「原油価格が高い状態が続けば、ガソリンや輸送費など、私たちの身近な"
                       "価格にも影響する。」", "ACCEPTABLE", unsupported_new_claim=True),
                _claim("B1-c", "「市場が見ているのは『言葉』より海の安全」「投資家が気にしているの"
                       "は、20％の料金案が残るかどうかだけではない」とし、海上の危険がBrent価格の"
                       "反発を説明するかのように述べている。", "BLOCKING", unsupported_new_claim=True),
            ],
        },
        {
            "group_id": "B2", "fixture": b2,
            "claims": [
                _claim("B2", "The disappearance of the fee plan did not lead to a large, lasting "
                       "fall in prices. So the price reacted once, then returned to a high level.",
                       "QUALITY", origin="ja_source", related_fact_id="HF-009",
                       unsupported_new_claim=False),
            ],
        },
        {
            "group_id": "B3", "fixture": b3,
            "claims": [
                _claim("B3", "“Concerns about US-Iran attacks, the sea blockade, and tanker "
                       "safety continued on July 14, so the flashy 20% plan left the stage” "
                       "links the continuing concerns causally to the plan’s withdrawal.",
                       "BLOCKING", origin="ja_source", related_fact_id="HF-007",
                       unsupported_new_claim=True),
            ],
        },
        {
            "group_id": "B4", "fixture": b4,
            "claims": [
                _claim("B4-d", "“Meta had run a test that produced exactly this kind of "
                       "surprise.”", "BLOCKING", origin="translation",
                       related_fact_id="MUSE-HC-006", unsupported_new_claim=True),
                _claim("B4-a", "“A person can take over when AI alone has trouble.”",
                       "BLOCKING", origin="ja_source", related_fact_id="MUSE-HC-002",
                       unsupported_new_claim=True),
                _claim("B4-b", "“People feel differently when they think they are speaking to "
                       "a machine and when they know a person is listening. Names, plans, and "
                       "private matters are easier to share when you know who is hearing them.”",
                       "QUALITY", origin="ja_source", related_fact_id="MUSE-HC-010",
                       unsupported_new_claim=True),
                _claim("B4-c", "“As AI makes calls and reservations, useful features make "
                       "people want to know whether AI or a person is on the other end.”",
                       "QUALITY", origin="ja_source", related_fact_id="MUSE-HC-004",
                       unsupported_new_claim=True),
            ],
        },
        {
            "group_id": "Meta_run03_standard", "fixture": meta,
            "claims": [
                _claim("Meta-1", meta["baseline_parsed"]["deviations"][0]["claim_in_article"],
                       "BLOCKING", origin="translation", related_fact_id="MUSE-HC-010",
                       unsupported_new_claim=True),
                _claim("Meta-2", meta["baseline_parsed"]["deviations"][1]["claim_in_article"]
                       if len(meta["baseline_parsed"]["deviations"]) > 1 else
                       meta["baseline_parsed"]["deviations"][0]["claim_in_article"],
                       "BLOCKING", origin="ja_source", related_fact_id="MUSE-HC-012",
                       unsupported_new_claim=True),
            ],
        },
        {
            "group_id": "hormuz_run03_standard", "fixture": hormuz,
            "claims": [
                _claim("hormuz-HF009", "Oil prices did not fall across the whole market after the "
                       "plan was withdrawn.", "BLOCKING", origin="ja_source",
                       related_fact_id="HF-009", unsupported_new_claim=True),
            ],
        },
    ]

    for fixture_id, path in step3cmp.NEGATIVE_SOURCE_FILES:
        if fixture_id not in ("neg1_meta_b3prod_a2", "neg2_meta_refresh_a2",
                               "neg3_hormuz_prodrunner_b1b", "neg5_hormuz_div_a2"):
            continue
        fx = step3cmp.load_negative_fixture(fixture_id, path)
        devs = fx["baseline_parsed"]["deviations"] if fx.get("baseline_parsed") else []
        claim_text = devs[0]["claim_in_article"] if devs else "(claim not found in baseline)"
        unc = bool(devs[0].get("unsupported_new_claim")) if devs else True
        groups.append({
            "group_id": fixture_id, "fixture": fx,
            "claims": [_claim(fixture_id, claim_text, "NOT_BLOCKING(ACCEPTABLE/QUALITY)",
                               unsupported_new_claim=unc)],
        })

    for fid in ["A2A3", "A4", "A5"]:
        fx = g6_step1[fid]
        path = f"er051_output/open233_checker_trial_01/trial_02/step1/{fid}/V4A/run_1.json"
        with open(path, encoding="utf-8") as f:
            v4a = json.load(f)
        devs = [dv for dv in v4a["parsed"]["deviations"] if dv.get("severity_final") == "BLOCKING"]
        claims = []
        for i, dv in enumerate(devs):
            claims.append(_claim(f"{fid}-{i}", dv.get("claim_in_article", ""), "BLOCKING",
                                  origin=dv.get("origin"), related_fact_id=dv.get("related_fact_id"),
                                  unsupported_new_claim=bool(dv.get("unsupported_new_claim"))))
        groups.append({"group_id": fid, "fixture": fx, "claims": claims})

    return groups


def build_claim_records_for_group(group: dict) -> list:
    fixture = group["fixture"]
    out = []
    for c in group["claims"]:
        local_context, fallback = s2p.build_local_context(fixture["article_text"], c["claim_text"])
        out.append({**c, "local_context": local_context, "fallback_used": fallback})
    return out


# ------------------------------------------------------------
# R1(既存出力の再利用、0 call)
# ------------------------------------------------------------
R1_EXISTING_MAP = {
    "B1-c": "er052_output/open233_self_recovery_phase1_step4_stage2_unitcost_01/"
            "per_claim_vs_batch/B1/per_claim_0.json",
    "B1-b": "er052_output/open233_self_recovery_phase1_step4_stage2_unitcost_01/"
            "per_claim_vs_batch/B1/per_claim_1.json",
    "B4-d": "er052_output/open233_self_recovery_phase1_step4_stage2_unitcost_01/"
            "per_claim_vs_batch/B4/per_claim_0.json",
    "B4-a": "er052_output/open233_self_recovery_phase1_step4_stage2_unitcost_01/"
            "per_claim_vs_batch/B4/per_claim_1.json",
    "B4-b": "er052_output/open233_self_recovery_phase1_step4_stage2_unitcost_01/"
            "per_claim_vs_batch/B4/per_claim_2.json",
    "B4-c": "er052_output/open233_self_recovery_phase1_step4_stage2_unitcost_01/"
            "per_claim_vs_batch/B4/per_claim_3.json",
}


def load_r1_existing() -> dict:
    out = {}
    for sub_id, path in R1_EXISTING_MAP.items():
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        out[sub_id] = {"materiality": d["parsed"]["materiality"], "basis": d["parsed"]["basis"],
                        "source_path": path, "cost_jpy": 0.0, "call_type": "reused_existing_0call"}
    return out


def apply_r3_floor(r2_materiality: str, r2_basis: str, unsupported_new_claim: bool) -> tuple:
    if unsupported_new_claim and r2_basis not in R3_FLOOR_SAFE_BASIS and r2_materiality != "BLOCKING":
        return "BLOCKING", True
    return r2_materiality, False


def guarded_batch_call(state: dict, consecutive_errors: list, label: str, save_path: str, **kwargs) -> dict:
    check_budget(state)
    last_err = None
    result = None
    for _ in range(1 + MAX_RETRIES_PER_CALL):
        try:
            result = run_stage2_batch_variant(**kwargs)
            break
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(1.0)
    state["cumulative_calls"] += 1
    if result is not None:
        state["cumulative_jpy"] += result["cost_jpy"]
        state["history"].append({"label": label, "cost_jpy": result["cost_jpy"], "usage": result["usage"]})
        save_json(save_path, {"label": label, **result})
        consecutive_errors[0] = 0
    else:
        state["cumulative_errors"] += 1
        save_json(save_path, {"label": label, "error": last_err})
        consecutive_errors[0] += 1
    save_budget_state(state)
    if consecutive_errors[0] >= MAX_CONSECUTIVE_ERRORS:
        raise TrialAbort(f"API errorが{MAX_CONSECUTIVE_ERRORS}call連続(STOP条件)")
    return result if result is not None else {"error": last_err}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_runs", type=int, default=N_RUNS)
    args = parser.parse_args()

    client = vfl01.get_client()
    state = load_budget_state()
    consecutive_errors = [0]
    groups = build_eval_groups()
    r1_existing = load_r1_existing()

    stopped, stop_reason = False, None
    r2_runs = {}  # group_id -> [run1_parsed, run2_parsed, ...]
    per_claim_rows = []

    try:
        for run_idx in range(1, args.n_runs + 1):
            for group in groups:
                claims = build_claim_records_for_group(group)
                fixture = group["fixture"]
                label = f"{group['group_id']}_R2_run{run_idx}"
                save_path = f"{OUT_DIR}/R2/{group['group_id']}/run_{run_idx}.json"
                res = guarded_batch_call(
                    state, consecutive_errors, label, save_path,
                    client=client, verified_ledger_text=fixture["ledger_text"],
                    source_article_text=fixture.get("source_article_text"),
                    claims=claims, rubric_text=RUBRIC_R2,
                )
                r2_runs.setdefault(group["group_id"], []).append({
                    "run": run_idx, "claims": claims, "result": res,
                })
    except TrialAbort as e:
        stopped = True
        stop_reason = str(e)

    # 集計: claim単位でR1(reused)/R2(実測、n runs)/R3(post-hoc)を並べる
    for group in groups:
        gid = group["group_id"]
        runs = r2_runs.get(gid, [])
        for c in group["claims"]:
            sub_id = c["sub_id"]
            r1 = r1_existing.get(sub_id)
            r2_labels = []
            r3_labels = []
            for run in runs:
                if "error" in run["result"]:
                    continue
                judgments = run["result"]["parsed"].get("judgments", [])
                claim_idx = [cc["sub_id"] for cc in run["claims"]].index(sub_id)
                match = next((j for j in judgments if j.get("claim_index") == claim_idx), None)
                if match is None:
                    continue
                r2_labels.append(match["materiality"])
                r3_label, overridden = apply_r3_floor(match["materiality"], match["basis"],
                                                       c["unsupported_new_claim"])
                r3_labels.append({"label": r3_label, "floor_overridden": overridden,
                                   "r2_basis": match["basis"]})
            per_claim_rows.append({
                "group_id": gid, "sub_id": sub_id, "correct_label": c["correct_label"],
                "origin": c["origin"], "related_fact_id": c["related_fact_id"],
                "unsupported_new_claim": c["unsupported_new_claim"],
                "r1": r1, "r2_labels_by_run": r2_labels, "r3_labels_by_run": r3_labels,
            })

    summary = {
        "stopped": stopped, "stop_reason": stop_reason,
        "cumulative_jpy": round(state["cumulative_jpy"], 4),
        "cumulative_calls": state["cumulative_calls"],
        "cumulative_errors": state["cumulative_errors"],
        "n_runs": args.n_runs, "n_groups": len(groups),
    }
    save_json(f"{OUT_DIR}/summary_stage2_calibration.json", {
        "summary": summary, "per_claim_rows": per_claim_rows,
    })
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
