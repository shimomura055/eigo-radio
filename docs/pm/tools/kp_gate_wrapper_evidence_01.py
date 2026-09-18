# ============================================================
# docs/pm/tools/kp_gate_wrapper_evidence_01.py
# 管理ID: KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01 FIX-01
# ============================================================
# F-2: 実Assembly経路(`er003_v1_n3_01_assemble.verify_key_phrase_source_
# gate`)を各Production driverが実際に渡す引数と同じ形で直接呼び、
# 20 canonical out_dir + 旧2 out_dir(true positive FAIL確認用)に対して
# 実行した結果を記録する。CLI独自の本文解決ロジックは一切使わない
# (Gate関数自身のarticle.md→article_normalized.txt fallback、または
# 明示article_textのみ)。実API呼び出しなし、費用¥0。
#
# 副作用の注意: `verify_key_phrase_source_gate`は正常設計として
# `<out_dir>/audit/key_phrase_source_gate.json`へ結果を書き込む(実
# Production Assembly時も同じ副作用が発生する既存仕様)。これは本
# スクリプトが新設する副作用ではなく、Gate関数自体の既存の記録動作。
import argparse
import json
import os
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, _REPO_ROOT)
os.chdir(_REPO_ROOT)

import er003_v1_n3_01_assemble as asm  # noqa: E402


# young_travelers B1のindex.json記載の`key_phrase_asset_path`は、KP5差し替え
# の「選定」中間出力(kp5_regen_and_completion_01/kp5_replacement_selection_01/
# ...)を指しているが、実Production Assembly呼び出し(er011_family_a_
# completion_a2_trend_end_to_end_01_run.py L601、b1_out_dir = f"{OUT_DIR}/b1b")
# が実際にverify_episode_audio_validation_gate/Gate (a)を実行するのは、KP5
# 差し替え後の最終keywords_canonicalized.jsonがコピーされる`{OUT_DIR}/b1b`
# (同ファイルにarticle.mdも存在する)。よってこの1件のみ実際のAssembly呼び出し
# out_dirへ明示的に差し替える(Read一覧6で確認した事実、CLI独自解決ではない)。
OUT_DIR_OVERRIDES = {
    ("young_travelers", "B1"): "er011_output/family_a_completion_a2_trend_end_to_end_01/b1b",
}


def derive_out_dir(item: dict) -> str:
    key = (item["article_id"], item["level"])
    if key in OUT_DIR_OVERRIDES:
        return OUT_DIR_OVERRIDES[key]
    kp_path = item["key_phrase_asset_path"]
    return os.path.dirname(os.path.dirname(kp_path))


def run_one(article_id: str, level: str, out_dir: str, expect_fail: bool = False) -> dict:
    entry = {
        "article_id": article_id, "level": level, "out_dir": out_dir,
        "kp_asset_exists": os.path.exists(f"{out_dir}/key_phrases/keywords_canonicalized.json"),
        "article_md_exists": os.path.exists(f"{out_dir}/article.md"),
        "article_normalized_exists": os.path.exists(f"{out_dir}/article_normalized.txt"),
    }
    try:
        # Production driverが実際に渡す引数と同じ形: out_dir, levelのみ
        # (article_text明示なし、Gate関数自身のfallback解決に委ねる)。
        result = asm.verify_key_phrase_source_gate(out_dir, level)
        entry["call_status"] = "NO_EXCEPTION"
        entry["gate_result_status"] = (result or {}).get("status")
        entry["article_source"] = (result or {}).get("article_source")
        entry["expect_fail"] = expect_fail
        entry["pass_check"] = (entry["gate_result_status"] == "PASS") if not expect_fail else False
    except RuntimeError as e:
        entry["call_status"] = "RUNTIME_ERROR"
        entry["error_message"] = str(e)[:600]
        entry["expect_fail"] = expect_fail
        entry["pass_check"] = bool(expect_fail)
    return entry


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--old-dirs", default="")
    args = ap.parse_args()

    with open(args.index, encoding="utf-8") as f:
        index_data = json.load(f)

    results = []
    for item in index_data["items"]:
        out_dir = derive_out_dir(item)
        results.append(run_one(item["article_id"], item["level"], out_dir, expect_fail=False))

    old_dir_results = []
    for old_dir in [d for d in args.old_dirs.split(",") if d.strip()]:
        old_dir = old_dir.replace("\\", "/")
        level = "A2"  # 旧2 dirはいずれもA2(委任文記載どおり)
        old_dir_results.append(run_one(f"OLD:{old_dir}", level, old_dir, expect_fail=True))

    not_applicable = [r for r in results if r.get("gate_result_status") == "NOT_APPLICABLE"]
    passed = [r for r in results if r.get("pass_check")]
    failed_canonical = [r for r in results if not r.get("pass_check")]
    old_true_positive = [r for r in old_dir_results if r.get("pass_check")]

    summary = {
        "canonical_total": len(results),
        "canonical_pass": len(passed),
        "canonical_not_applicable": len(not_applicable),
        "canonical_unexpected_fail": [r["article_id"] + "/" + r["level"] for r in failed_canonical],
        "old_dirs_total": len(old_dir_results),
        "old_dirs_true_positive_fail": len(old_true_positive),
    }

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "canonical_results": results, "old_dir_results": old_dir_results},
                   f, ensure_ascii=False, indent=2)

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
