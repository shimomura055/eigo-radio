# ============================================================
# er003_v1_p2i_manifest.py
# ER-003-P2I: B2 Key Words標準方式リファレンスマニフェストの構築
# ============================================================
# ER-003-P2Iで承認されたL方式(Listening Blocker Ranking)Key Wordsを
# 「公式リファレンス」として明示し、P2D/P2E/P2F/P2Gの成果物は「実験的
# 証跡(experimental evidence)」として区別する記録を1つのJSONに
# まとめる。APIは一切呼ばない。er003_v1_p2i_approve.pyの実行後に
# 実行すること(各記事のkey_words_approved.json等を読み込む)。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_p2i_manifest.py

from __future__ import annotations

import json

import er003_ja_to_en_translation as er003

P2I_ROOT = "er003_output/p2i"
ARTICLE_IDS = ("A01", "A02", "ADD03")


def build_manifest() -> dict:
    articles = {}
    for article_id in ARTICLE_IDS:
        out_dir = f"{P2I_ROOT}/{article_id}"
        approved_path = f"{out_dir}/key_words_approved.json"
        reading_copy_path = f"{out_dir}/key_words_approved_reading_copy.md"
        approval_path = f"{out_dir}/key_words_approval.json"
        with open(f"{out_dir}/key_words_approved_sha256.txt", encoding="utf-8") as f:
            approved_sha256 = f.read().strip()
        articles[article_id] = {
            "approved_key_words_path": approved_path,
            "approved_reading_copy_path": reading_copy_path,
            "approval_metadata_path": approval_path,
            "approved_key_words_sha256": approved_sha256,
        }

    return {
        "decision_id": "ER-003-P2I",
        "production_selection_strategy": "L",
        "production_selection_strategy_name": "Listening Blocker Ranking",
        "production_item_count": 5,
        "adoption_basis": "Top5同点(L=24/U=24, 30点満点)後の、標準運用上の"
                          "説明可能性によるtie-break。スコアでの勝利ではない。",
        "articles": articles,
        "future_tts_source": "本ステージ(P2I)ではTTSは実行しない。将来のKey Words "
                             "TTSは、articles.*.approved_reading_copy_pathのファイルを"
                             "入力とする。",
        "personalization_candidate": {
            "strategy_id": "U",
            "strategy_name": "Observed Learner Profile",
            "status": "NOT_ADOPTED_RETAINED_AS_FUTURE_PERSONALIZATION_CANDIDATE",
            "note": "標準方式としては不採用だが、Top5評価はLと同点(24/30)であり、"
                   "将来の学習者プロファイル別パーソナライズ機能の候補として保持する。",
        },
        "excluded_candidate": {
            "strategy_id": "P",
            "strategy_name": "Difficulty Portfolio",
            "status": "EXCLUDED_FROM_STANDARD_CANDIDATES",
            "note": "Top5・Total双方の評価で他方式に劣ったため、標準方式候補から除外する。",
        },
        "experimental_evidence": {
            "note": "以下は標準方式決定に至る過程の実験的証跡であり、削除・上書きは"
                   "行わない。本番運用の参照元はP2Iの承認済み成果物のみである。",
            "ER-003-P2D": "er003_output/p2d",
            "ER-003-P2E": "er003_output/p2e",
            "ER-003-P2F": "er003_output/p2f",
            "ER-003-P2G": "er003_output/p2g",
            "ER-003-P2H": "er003_output/p2h",
        },
        "production_code": {
            "prompt_template": "er003_v1_translator_briefs/b2_key_words_production_l_prompt_template.txt",
            "selector_and_validator_module": "er003_key_words_production.py",
        },
    }


if __name__ == "__main__":
    manifest = build_manifest()
    manifest_path = f"{P2I_ROOT}/key_words_reference_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    manifest_sha256 = er003.sha256_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    with open(f"{P2I_ROOT}/key_words_reference_manifest_sha256.txt", "w", encoding="utf-8") as f:
        f.write(manifest_sha256)
    print(f"manifest written: {manifest_path} (sha256={manifest_sha256[:12]}...)")
