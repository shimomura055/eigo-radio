# ============================================================
# er011_preview_numeric_wiring_01_runtime_evidence.py
# ER-011-PREVIEW-ROLE-AND-NUMERIC-PRECISION-PRINCIPLE-PRODUCTION-WIRING-01
# ============================================================
# Production正式初回path経由のruntime evidence取得専用スクリプト(TTSなし、
# テキスト工程のみ)。以下2件を1回ずつ実施する。
#
# (1) Preview: 新PREVIEW_ROLE(B1)で、Theme 2 B1記事(Trial-12 b1b_run01)の
#     Production関数 er003_v1_b1_scaffold_01_generate.run_support_text() を
#     無変更のまま呼び出し、新Previewを1回生成する。Comment 1/2は既存
#     Production生成物(full_audio_trial_13)をそのまま再利用する(比較の
#     土台を固定、新規生成しない)。あわせてA2側 PREVIEW_ROLE(無変更)でも
#     1回生成し、影響がないことを確認する。
# (2) Numeric Precision: Theme 2 B1/A2の実際のPre-editor Writer出力
#     (Trial-12、Production Writerによる既存生成物、再生成しない)を
#     入力として、更新後のEvidence Compression Editor
#     (er003_v1_n3_01_evidence_compression_editor.run_lossless_editor、
#     Production関数、無変更のシグネチャ)を1回ずつ呼び出す。
#
# 出力先: er011_output/preview_role_numeric_precision_wiring_01/
from __future__ import annotations

import json
import os

import er003_v1_b1_scaffold_01_generate as b1s
import er003_v1_iran01_a2_generate as a2gen
import er003_v1_n3_01_evidence_compression_editor as ec_editor
import er006_model_routing_contract_01 as routing

OUT_DIR = "er011_output/preview_role_numeric_precision_wiring_01"
TRIAL12_B1_DIR = "er011_output/open112_trend_theme2_b_a2_b1_text_trial_12/b1b_run01"
TRIAL12_A2_DIR = "er011_output/open112_trend_theme2_b_a2_b1_text_trial_12/a2_run01"
TRIAL13_SUPPORT_JSON = (
    "er011_output/open112_trend_theme2_b_full_audio_trial_13/b1b/b1_support_texts.json"
)


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def run_preview_evidence(client) -> dict:
    article_text = load_text(f"{TRIAL12_B1_DIR}/article.md")
    with open(TRIAL13_SUPPORT_JSON, encoding="utf-8") as f:
        existing_support = json.load(f)
    comment_1 = existing_support["comment_1"]
    comment_2 = existing_support["comment_2"]
    assert isinstance(comment_1, str) and isinstance(comment_2, str), \
        "b1_support_texts.jsonのcomment_1/2形式が想定(plain string)と異なります"

    preview_role = b1s.PREVIEW_ROLE.format(comment_1=comment_1, comment_2=comment_2)
    b1_context = f"【エピソード全文(参考、新しいFactの追加禁止)】\n{article_text}"
    b1_model = routing.require_model("B1_SUPPORT", routing.SUPPORT_MODEL)
    b1_result = b1s.run_support_text(client, preview_role, b1_context, model=b1_model)

    # A2側は無変更であることの確認用に1件生成する(同一記事のA2版・
    # A2既存Comment1/2を再利用)。
    a2_article_text = load_text(f"{TRIAL12_A2_DIR}/article.md")
    trial13_a2_support_path = (
        "er011_output/open112_trend_theme2_b_full_audio_trial_13/a2/a2_support_texts.json"
    )
    a2_comment_1 = a2_comment_2 = None
    if os.path.exists(trial13_a2_support_path):
        with open(trial13_a2_support_path, encoding="utf-8") as f:
            a2_existing_support = json.load(f)
        a2_comment_1 = a2_existing_support["comment_1"]
        a2_comment_2 = a2_existing_support["comment_2"]
        assert isinstance(a2_comment_1, str) and isinstance(a2_comment_2, str), \
            "a2_support_texts.jsonのcomment_1/2形式が想定(plain string)と異なります"

    a2_result = None
    if a2_comment_1 and a2_comment_2:
        a2_preview_role = a2gen.PREVIEW_ROLE.format(comment_1=a2_comment_1, comment_2=a2_comment_2)
        a2_context = f"【エピソード全文(参考、新しいFactの追加禁止)】\n{a2_article_text}"
        a2_model = routing.require_model("A2_SUPPORT", routing.SUPPORT_MODEL)
        a2_result = a2gen.run_support_text(client, a2_preview_role, a2_context, model=a2_model)

    return {
        "b1_preview_result": b1_result,
        "b1_comment_1_reused": comment_1,
        "b1_comment_2_reused": comment_2,
        "a2_preview_result": a2_result,
        "a2_comment_1_reused": a2_comment_1,
        "a2_comment_2_reused": a2_comment_2,
    }


def run_numeric_precision_evidence(client) -> dict:
    b1_pre_editor_text = load_text(f"{TRIAL12_B1_DIR}/audit/pre_editor_article.md")
    a2_pre_editor_text = load_text(f"{TRIAL12_A2_DIR}/audit/pre_editor_article.md")

    b1_model = routing.require_model("B1_WRITER", routing.WRITER_MODEL)
    a2_model = routing.require_model("A2_WRITER", routing.WRITER_MODEL)
    b1_editor_result = ec_editor.run_lossless_editor(client, b1_pre_editor_text, model=b1_model)
    a2_editor_result = ec_editor.run_lossless_editor(client, a2_pre_editor_text, model=a2_model)

    return {
        "b1_pre_editor_text": b1_pre_editor_text,
        "b1_editor_result": b1_editor_result,
        "a2_pre_editor_text": a2_pre_editor_text,
        "a2_editor_result": a2_editor_result,
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    client = b1s.get_client()

    preview_evidence = run_preview_evidence(client)
    with open(f"{OUT_DIR}/preview_evidence.json", "w", encoding="utf-8") as f:
        json.dump(preview_evidence, f, ensure_ascii=False, indent=2, default=str)

    numeric_evidence = run_numeric_precision_evidence(client)
    with open(f"{OUT_DIR}/numeric_precision_evidence.json", "w", encoding="utf-8") as f:
        json.dump(numeric_evidence, f, ensure_ascii=False, indent=2, default=str)

    print("[DONE] preview_evidence.json / numeric_precision_evidence.json written to", OUT_DIR)


if __name__ == "__main__":
    main()
