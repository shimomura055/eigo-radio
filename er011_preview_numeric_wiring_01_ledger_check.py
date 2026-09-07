# ============================================================
# er011_preview_numeric_wiring_01_ledger_check.py
# ER-011-PREVIEW-ROLE-AND-NUMERIC-PRECISION-PRINCIPLE-PRODUCTION-WIRING-01
# ============================================================
# er011_preview_numeric_wiring_01_runtime_evidence.pyが生成した
# numeric_precision_evidence.json(新Evidence Compression Editorの実出力)
# に対し、Production正式のLedger Deviation Checker
# (er003_v1_en_direct_vfl_01_generate.run_deviation_check、hook_aware=True、
# Production呼び出しと同一引数)を実際に1回ずつ実行し、LEDGER_COMPLIANTで
# あることを確認する(TTSなし、テキスト工程のみ)。
from __future__ import annotations

import json

import er003_v1_b1_scaffold_01_generate as b1s
import er003_v1_en_direct_vfl_01_generate as vfl01
import er006_model_routing_contract_01 as routing

OUT_DIR = "er011_output/preview_role_numeric_precision_wiring_01"
LEDGER_PATH = (
    "er011_output/open112_trend_theme2_b_a2_b1_text_trial_12/research/"
    "theme2_verified_fact_ledger_CORRECTED_trial12.txt"
)


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def main():
    client = b1s.get_client()
    ledger_text = load_text(LEDGER_PATH)

    with open(f"{OUT_DIR}/numeric_precision_evidence.json", encoding="utf-8") as f:
        numeric_evidence = json.load(f)

    b1_article_text = numeric_evidence["b1_editor_result"]["raw_text"]
    a2_article_text = numeric_evidence["a2_editor_result"]["raw_text"]

    b1_model = routing.require_model("B1_WRITER", routing.WRITER_MODEL)
    a2_model = routing.require_model("A2_WRITER", routing.WRITER_MODEL)

    print("[LEDGER-CHECK] B1(after)...")
    b1_deviation = vfl01.run_deviation_check(client, ledger_text, b1_article_text,
                                              model=b1_model, hook_aware=True)
    print(f"[LEDGER-CHECK] B1(after) overall_status={b1_deviation['parsed']['overall_status']} "
          f"deviations={len(b1_deviation['parsed']['deviations'])}")

    print("[LEDGER-CHECK] A2(after)...")
    a2_deviation = vfl01.run_deviation_check(client, ledger_text, a2_article_text,
                                              model=a2_model, hook_aware=True)
    print(f"[LEDGER-CHECK] A2(after) overall_status={a2_deviation['parsed']['overall_status']} "
          f"deviations={len(a2_deviation['parsed']['deviations'])}")

    with open(f"{OUT_DIR}/ledger_deviation_after_b1.json", "w", encoding="utf-8") as f:
        json.dump(b1_deviation, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{OUT_DIR}/ledger_deviation_after_a2.json", "w", encoding="utf-8") as f:
        json.dump(a2_deviation, f, ensure_ascii=False, indent=2, default=str)

    print("[DONE] ledger_deviation_after_b1.json / ledger_deviation_after_a2.json written to", OUT_DIR)


if __name__ == "__main__":
    main()
