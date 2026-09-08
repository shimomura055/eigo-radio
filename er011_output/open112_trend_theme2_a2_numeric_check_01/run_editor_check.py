# ============================================================
# er011_output/open112_trend_theme2_a2_numeric_check_01/run_editor_check.py
# 管理ID: OPEN-112-THEME2-A2-NUMERIC-PRECISION-COMMON-WIRING-CHECK-01
# ============================================================
# Part 1 step2: 現行Production Evidence Compression Editor関数
# (er003_v1_n3_01_evidence_compression_editor.run_lossless_editor、無変更)
# を、Theme 2 A2完成音声(rerun_02/a2)の元になった圧縮前草稿(Trial-12
# a2_run01のpre_editor_article.md、article.md/rerun_02/a2/article.mdと
# byte-for-byte一致することを別途diffで確認済み)に対して1回だけ実行し、
# 「24.1%」がどう出力されるかを記録するだけの読み取り専用runtime evidence
# 取得スクリプト。Editor自体・呼び出しシグネチャ・Prompt・設定は一切変更
# しない(model引数もProduction経路と同じrouting.require_model("A2_WRITER",
# routing.WRITER_MODEL)を使用)。
from __future__ import annotations

import json
import os

import er003_v1_n3_01_evidence_compression_editor as ec_editor
import er003_v1_b1_scaffold_01_generate as b1s
import er006_model_routing_contract_01 as routing

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
PRE_EDITOR_DRAFT_PATH = (
    "er011_output/open112_trend_theme2_b_a2_b1_text_trial_12/a2_run01/audit/pre_editor_article.md"
)


def main():
    with open(PRE_EDITOR_DRAFT_PATH, encoding="utf-8") as f:
        pre_editor_text = f.read()
    assert "24.1%" in pre_editor_text, "対象草稿に24.1%が見つかりません(想定と異なる入力)"

    client = b1s.get_client()
    model = routing.require_model("A2_WRITER", routing.WRITER_MODEL)
    editor_result = ec_editor.run_lossless_editor(client, pre_editor_text, model=model)

    out = {
        "pre_editor_text": pre_editor_text,
        "editor_result": editor_result,
        "model_used": model,
    }
    with open(f"{OUT_DIR}/editor_check_result.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, default=str)

    raw = editor_result.get("raw_text", "")
    with open(f"{OUT_DIR}/editor_output.md", "w", encoding="utf-8") as f:
        f.write(raw)

    contains_2401 = "24.1%" in raw
    print("[DONE] contains_24.1_percent_after_editor =", contains_2401)
    print("input_tokens=", editor_result.get("input_tokens"),
          "output_tokens=", editor_result.get("output_tokens"))


if __name__ == "__main__":
    main()
