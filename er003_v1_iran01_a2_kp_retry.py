# IRAN01 A2: Key Phrase選定のみ再実行(初回KEY_WORDS_STRUCTURE_INVALID対応)
import json

import er003_v1_iran01_a2_generate as a2gen

OUT_DIR = a2gen.OUT_DIR


def main():
    a2_text = a2gen.load_text(a2gen.A2_ARTICLE_PATH)
    kp_dir = f"{OUT_DIR}/key_phrases"

    print("[IRAN01-A2-KP-RETRY] Key Phrase選定再実行...")
    kp_selection = a2gen.run_key_phrase_selection(a2_text, kp_dir)
    print(f"[IRAN01-A2-KP-RETRY] status={kp_selection['status']}")
    kp_final = None
    if kp_selection["status"] == "KEY_WORDS_STRUCTURE_PASS":
        print("[IRAN01-A2-KP-RETRY] Canonicalization開始...")
        kp_canon = a2gen.run_key_phrase_canonicalization(a2_text, kp_selection["original_items"], kp_dir)
        print(f"[IRAN01-A2-KP-RETRY] Canonicalization status={kp_canon['status']}")
        kp_final = kp_canon.get("merged")
    else:
        print("[IRAN01-A2-KP-RETRY] 再度失敗。詳細を確認してください。")
        return

    # 完成版スクリプトへKey Phrase一覧を反映して再書き出し
    parts = json.load(open(f"{OUT_DIR}/fixed_news_parts.json", encoding="utf-8"))
    support_texts = json.load(open(f"{OUT_DIR}/support_texts_ja.json", encoding="utf-8"))
    script_lines = [
        f"# A2 V2改1 — {parts['title']}", "",
        "## 1. Preview(日本語)", support_texts["preview"] or "(生成失敗)", "",
        "## 2. Key Phrases",
    ]
    for item in kp_final["items"]:
        script_lines.append(f"{item['rank']}. {item['used_form']} — {item['japanese_gloss']} — {item['used_form']}")
    script_lines += [
        "", "## 3. Comment 1(日本語)", support_texts["comment_1"] or "(生成失敗)", "",
        "## 4. Full Story Part 1(英語、無変更)", parts["part1"], "",
        "## 5. Comment 2(日本語)", support_texts["comment_2"] or "(生成失敗)", "",
        "## 6. Full Story Part 2(英語、無変更)", parts["part2"], "",
        "## 7. Comment 3(日本語)", support_texts["comment_3"] or "(生成失敗)", "",
        "## 8. Point One(英語、無変更)", f"### {parts['point_one_heading']}", parts["point_one_body"], "",
        "## 9. Point Two(英語、無変更)", f"### {parts['point_two_heading']}", parts["point_two_body"], "",
        "## 10. Comment 4(日本語)", support_texts["comment_4"] or "(生成失敗)", "",
        "## 11. In One Line(英語、無変更)", parts["in_one_line"],
    ]
    with open(f"{OUT_DIR}/a2_supported_script.md", "w", encoding="utf-8") as f:
        f.write("\n".join(script_lines))

    summary = json.load(open(f"{OUT_DIR}/run_summary.json", encoding="utf-8"))
    summary["key_phrase_selection_status"] = kp_selection["status"]
    summary["key_phrase_canonicalization_status"] = (kp_final is not None)
    with open(f"{OUT_DIR}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print("[IRAN01-A2-KP-RETRY] 完了。")


if __name__ == "__main__":
    main()
