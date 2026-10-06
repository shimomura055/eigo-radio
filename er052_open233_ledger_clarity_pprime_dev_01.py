# -*- coding: utf-8 -*-
"""OPEN-233-LEDGER-CLARITY-P-TRIAL-01 委任_01a-2: P'(Researcher/Verification prompt追記)のDEV専用ラッパ。

性質: DEV/Trial専用(Production経路ではない、APPROVED_FOR_PRODUCTIONではない)。新規ファイルのみ。
- import時は何もしない(M-b(1))。`main()`内のcontextmanagerでのみ vfl01.build_researcher_prompt /
  vfl01.build_verification_prompt を「元の戻り値+追記ブロック」へ差し替え、終了時(例外時含む)に元へ戻す。
- schema/enum/build_verified_ledger_text(台帳生成の決定論処理)は触らない。
- env OPEN233_RESEARCHER_VARIANT: 未設定/baseline=差し替えなし、pprime=差し替え、他=ValueError。
- er019 runnerの main をプロセス内で呼ぶ(subprocessではmonkeypatchが効かない)。
- 有料APIは --yes-run-paid 指定時のみ。--dry-run は¥0。
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import sys
import time

ENV_NAME = "OPEN233_RESEARCHER_VARIANT"
VARIANTS = ("baseline", "pprime")
SEP = "\n\n"

BEFORE_THEME = "Meta Muse AI電話代行「人間コンシェルジュ」実験"
DEFAULT_OUT_DIR = "er052_output/open233_ledger_clarity_p_trial_01/after_pprime_01"
E2E02_SWITCH_DUMP = "er052_output/open233_prod_e2e_02/approved_switches_dump_worker1.json"
LEDGER_STAGE_GATE_JPY = 40.0

RESEARCHER_APPEND = """【Factの記述規則(明確化、記述だけの規則。検索対象・検索方法・Source優先順位は変えない)】
1. claimは「誰/何が・何をした/どうなった・対象・時点」が分かる1〜2文で書き、原資料の語を要約で曖昧にしない。
2. 同じ主体・同じ指標の時系列変化のときだけ、途中→最終の順で書く(date_or_period/conditions/notes_for_writerに順序を明記)。別の出来事は別factのままにし、順序づけで結合しない。
3. 多義的な動詞・名詞は、原資料が示す具体的な動作・状態に置き換えるか、原資料の語をそのまま添える(notes_for_writer)。
4. 原資料にない主体・因果・時系列・数値・事実を足さない。新しいFactを追加しない。
5. 解釈に不確実さが残る点は断定せずambiguityに書き、notes_for_writerにも1行残す。
6. 断定の強さ(確定/報道/予定/可能性)を原資料より強めない。
7. 原資料にない否定・因果・括弧・番号をclaimに入れない(注意はnotes_for_writerへ)。
8. 検索対象・検索方法・Source優先順位は変えない(本ブロックは記述だけの規則)。
9. どのフィールドにも改行を含めない(1フィールド1行で書く)。
10. (任意)notes_for_writer内で順序や語義を示す場合は、「順序: 途中…→最終…」「語義: 原語=…」の固定書き出しを使う。"""

VERIFICATION_APPEND = """【追加の確認観点(明確化された記述の検証。verdictの種類・判定基準の枠組みは変えない)】
- 明確化された主体・動作・対象・時系列・多義語の確定意味が、原資料の記述と一致するか。一致が確認できない場合は無理にVERIFIEDとせずAMBIGUOUSとし、verification_notesに理由を書く。
- 原資料より強い断定、または原資料にない否定表現が足されていないか。
- 原資料にない因果・主体・時系列が足されていないか(因果の強さを原資料より強めていないか)。"""


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sha256_file(path: str):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def resolve_variant(env=None) -> str:
    env = os.environ if env is None else env
    v = env.get(ENV_NAME)
    if v is None:
        return "baseline"
    if v not in VARIANTS:
        raise ValueError(f"{ENV_NAME}={v!r} は不正(許可: {VARIANTS}、未設定=baseline)")
    return v


def append_researcher(base: str) -> str:
    return base + SEP + RESEARCHER_APPEND


def append_verification(base: str) -> str:
    return base + SEP + VERIFICATION_APPEND


@contextlib.contextmanager
def patched_prompts(variant: str, vfl01_module=None):
    """variant=pprimeの間だけvfl01の2関数を差し替え、終了時(例外含む)に必ず元へ戻す。baselineは何もしない。"""
    if variant not in VARIANTS:
        raise ValueError(f"variant不正: {variant!r}")
    if vfl01_module is None:
        import er003_v1_en_direct_vfl_01_generate as vfl01_module
    orig_r = vfl01_module.build_researcher_prompt
    orig_v = vfl01_module.build_verification_prompt
    try:
        if variant == "pprime":
            def new_r(*a, **k):
                return append_researcher(orig_r(*a, **k))

            def new_v(*a, **k):
                return append_verification(orig_v(*a, **k))

            vfl01_module.build_researcher_prompt = new_r
            vfl01_module.build_verification_prompt = new_v
        yield variant
    finally:
        vfl01_module.build_researcher_prompt = orig_r
        vfl01_module.build_verification_prompt = orig_v


def assert_fresh_out_dir(out_dir: str) -> None:
    """M-b(4): 既存の台帳再利用(er019 L92-97等)を避けるため、研究・後段dirが存在しないことを確認。"""
    present = [d for d in ("research_ledger", "storyline_b3", "ja_writer") if os.path.exists(os.path.join(out_dir, d))]
    if present:
        raise SystemExit(f"out_dir既存物あり(再利用防止のためSTOP): {out_dir} -> {present}")


def _load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _write_json(path, obj):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def collect_post_run(out_dir: str) -> dict:
    """実行後に audit から検索回数・引用URLを抽出(存在するものだけ)。"""
    ld = f"{out_dir}/research_ledger"
    rr = _load_json(f"{ld}/audit/researcher_full_record.json") or {}
    vr = _load_json(f"{ld}/audit/verification_full_record.json") or {}
    draft = _load_json(f"{ld}/fact_ledger_draft.json") or {}
    urls = {f.get("source_url") for f in (draft.get("facts") or []) if f.get("source_url")}
    for rec in (rr, vr):
        for s in rec.get("sources") or []:
            if s.get("url"):
                urls.add(s["url"])
    return {
        "researcher_prompt_sent_sha256": sha256_text(rr["prompt"]) if rr.get("prompt") else None,
        "verification_prompt_sent_sha256": sha256_text(vr["prompt"]) if vr.get("prompt") else None,
        "model_id_actual": {"researcher": rr.get("model"), "verification": vr.get("model")},
        "web_search_call_count": {"researcher": (rr.get("search_usage") or {}).get("web_search_call_count"),
                                  "verification": (vr.get("search_usage") or {}).get("web_search_call_count")},
        "search_queries_researcher": (rr.get("search_usage") or {}).get("queries"),
        "cited_urls": sorted(urls),
        "reused": (_load_json(f"{ld}/runtime_evidence.json") or {}).get("reused", None),
        "ledger_txt_sha256": sha256_file(f"{ld}/verified_fact_ledger.txt"),
    }


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--theme", default=BEFORE_THEME)
    p.add_argument("--slug", default="meta")
    p.add_argument("--out-dir", default=DEFAULT_OUT_DIR)
    p.add_argument("--budget-jpy", type=float, default=60.0)
    p.add_argument("--stage", default="advanced", choices=("ledger", "advanced"))
    p.add_argument("--ledger-gate-jpy", type=float, default=LEDGER_STAGE_GATE_JPY)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--yes-run-paid", action="store_true")
    return p


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = build_arg_parser().parse_args(argv)
    variant = resolve_variant()
    if variant != "pprime":
        print(f"[DEV] {ENV_NAME} 未設定/baseline: prompt差し替えなし(Before再現用)。")
    out_dir = args.out_dir
    assert_fresh_out_dir(out_dir)
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er019_family_x_entertainment_production_runner_01 as er019

    started = time.strftime("%Y-%m-%dT%H:%M:%S")
    with patched_prompts(variant, vfl01):
        r_prompt = vfl01.build_researcher_prompt(args.theme)
        v_prompt_probe = vfl01.build_verification_prompt(args.theme, {"facts": []})
    prov = {
        "variant": variant, "env": ENV_NAME, "topic": args.theme, "slug": args.slug,
        "stage": args.stage, "budget_jpy": args.budget_jpy, "ledger_gate_jpy": args.ledger_gate_jpy,
        "started_at": started, "model_id": vfl01.MODEL,
        "researcher_append_sha256": sha256_text(RESEARCHER_APPEND),
        "verification_append_sha256": sha256_text(VERIFICATION_APPEND),
        "researcher_prompt_final_sha256_pre": sha256_text(r_prompt),
        "verification_prompt_probe_sha256_pre": sha256_text(v_prompt_probe),
        "verification_prompt_probe_note": "ledger_json={'facts': []}でのprobe。実送信promptのsha256は実行後 verification_prompt_sent_sha256",
        "e2e02_approved_switches_dump_worker1_sha256": sha256_file(E2E02_SWITCH_DUMP),
        "args": vars(args),
    }
    prov_path = f"{out_dir}/pprime_provenance.json"
    if args.dry_run or not args.yes_run_paid:
        print(json.dumps(prov, ensure_ascii=False, indent=2))
        if not args.dry_run:
            raise SystemExit("--yes-run-paid が必要(有料API実行)。確認のみなら --dry-run")
        print("[dry-run] 有料API呼び出しなし(JPY0)。out_dirは作成していない。")
        return 0

    _write_json(prov_path, prov)
    orig_ledger_fn = er019.run_research_and_ledger

    def gated_ledger(client, topic, ledger_dir):
        res = orig_ledger_fn(client, topic, ledger_dir)
        total = er019.compute_stage_cost_breakdown(f"{out_dir}/raw_usage_log.jsonl").get("total_jpy", 0.0)
        print(f"[DEV][ledger-gate] 台帳段完了時点の実費=JPY{total:.2f} (gate JPY{args.ledger_gate_jpy})")
        prov["ledger_stage_cost_jpy"] = round(total, 4)
        _write_json(prov_path, prov)
        if total > args.ledger_gate_jpy:
            raise SystemExit(f"台帳段実費JPY{total:.2f}>gate JPY{args.ledger_gate_jpy}: 後段へ続行しない")
        return res

    old_argv = sys.argv
    sys.argv = ["er019", "--theme", args.theme, "--slug", args.slug, "--out-dir", out_dir,
                "--budget-jpy", str(args.budget_jpy), "--stage", args.stage]
    exit_reason = "completed"
    try:
        with patched_prompts(variant, vfl01):
            er019.run_research_and_ledger = gated_ledger
            try:
                er019.main()
            finally:
                er019.run_research_and_ledger = orig_ledger_fn
    except SystemExit as e:
        exit_reason = f"SystemExit: {e}"
        raise
    except Exception as e:  # noqa: BLE001
        exit_reason = f"error: {e!r}"
        raise
    finally:
        sys.argv = old_argv
        prov.update(collect_post_run(out_dir))
        prov["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        prov["exit_reason"] = exit_reason
        _write_json(prov_path, prov)
    return 0


if __name__ == "__main__":
    sys.exit(main())
