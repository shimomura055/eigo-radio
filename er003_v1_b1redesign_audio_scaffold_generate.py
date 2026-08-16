# ============================================================
# er003_v1_b1redesign_audio_scaffold_generate.py
# ER-003-B1-REDESIGN-AUDIO-01: B1-B本文を固定Sourceとした
# Preview/Comment1-4再生成 + Key Phrase選定
# ============================================================
# ER-003-B1-REDESIGN-TEST-01で確定したB1-B candidate(Full Story
# Part1/2・Point One/Two・In One Line)は文字列レベルで一切書き換えない。
# 旧IRAN01 B1 Support(B2本文向け)は流用せず、B1-B本文を基準に
# Preview/Comment1-4を新規生成し、Key PhraseもB1-B最終本文から改めて
# 選定する(旧B2版Key Phraseの流用禁止)。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1redesign_audio_scaffold_generate.py

from __future__ import annotations

import hashlib
import json
import os
import re

import er003_v1_b1_scaffold_01_generate as b1s
import er003_v1_en_direct_ab_01_generate as ab01

B1_B_SOURCE_PATH = "er003_output/b1redesign_test_01/IRAN01/b1_b/article.md"
EXPECTED_B1_B_SHA256 = "3df23dd3ae40947e7ebffdd69f8f5f22325225a444858e8348b5e39383607370"

OUT_DIR = "er003_output/b1redesign_audio_01/IRAN01"

PART1_SPLIT_MARKER = "At the same time, a quieter and more practical development was taking place."


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def split_b1_b_text(text: str) -> dict:
    """B1-B本文を一切書き換えず、既存の見出し規則(#/###/## In one line…)
    のみを使って分割する(er003_v1_iran01_b1_generate.split_fixed_news_text
    と同じロジック、B1-B用にsplit markerのみ差し替え)。"""
    title_match = re.match(r"^#\s+(.+?)\s*\n", text)
    title = title_match.group(1).strip() if title_match else ""

    h3_matches = list(re.finditer(r"^###\s+(.+?)\s*$", text, flags=re.MULTILINE))
    if len(h3_matches) != 2:
        raise RuntimeError(f"###見出しがちょうど2つではありません(検出数: {len(h3_matches)})。B1-B本文が想定と異なります。")
    in_one_line_match = re.search(r"^##\s+In one line[…\.]*\s*\n(.+)", text, flags=re.MULTILINE | re.DOTALL)
    if not in_one_line_match:
        raise RuntimeError("『## In one line…』見出しが見つかりません。B1-B本文が想定と異なります。")

    intro_text = text[title_match.end():h3_matches[0].start()].strip() if title_match else text[:h3_matches[0].start()].strip()
    point_one_heading = h3_matches[0].group(1).strip()
    point_one_body = text[h3_matches[0].end():h3_matches[1].start()].strip()
    point_two_heading = h3_matches[1].group(1).strip()
    point_two_body = text[h3_matches[1].end():in_one_line_match.start()].strip()
    in_one_line_text = in_one_line_match.group(1).strip()

    if PART1_SPLIT_MARKER not in intro_text:
        raise RuntimeError(f"Part1/Part2分割マーカー『{PART1_SPLIT_MARKER}』がB1-B本文に見つかりません。")
    idx = intro_text.index(PART1_SPLIT_MARKER)
    part1 = intro_text[:idx].strip()
    part2 = intro_text[idx:].strip()

    return {
        "title": title, "part1": part1, "part2": part2,
        "point_one_heading": point_one_heading, "point_one_body": point_one_body,
        "point_two_heading": point_two_heading, "point_two_body": point_two_body,
        "in_one_line": in_one_line_text,
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    client = b1s.get_client()

    b1_b_text = load_text(B1_B_SOURCE_PATH)
    actual_sha256 = hashlib.sha256(b1_b_text.encode("utf-8")).hexdigest()
    identity_ok = actual_sha256 == EXPECTED_B1_B_SHA256
    print(f"[B1REDESIGN-AUDIO] B1-B source sha256={actual_sha256} "
          f"expected={EXPECTED_B1_B_SHA256} identity_ok={identity_ok}")
    if not identity_ok:
        raise RuntimeError("B1-B本文のsha256が、ER-003-B1-REDESIGN-TEST-01時点の値と一致しません。"
                            "本文が意図せず変更されている可能性があるため中断します。")

    parts = split_b1_b_text(b1_b_text)
    with open(f"{OUT_DIR}/audit/text_identity.json", "w", encoding="utf-8") as f:
        json.dump({"source_path": B1_B_SOURCE_PATH, "sha256": actual_sha256,
                    "expected_sha256": EXPECTED_B1_B_SHA256, "identity_ok": identity_ok,
                    "parts": parts}, f, ensure_ascii=False, indent=2)
    print(f"[B1REDESIGN-AUDIO] B1-B分割完了: part1={ab01.compute_word_count(parts['part1'])}語 "
          f"part2={ab01.compute_word_count(parts['part2'])}語 "
          f"point_one={ab01.compute_word_count(parts['point_one_body'])}語 "
          f"point_two={ab01.compute_word_count(parts['point_two_body'])}語")

    # --- Comment 1〜4(B1-B本文基準、旧仕様の役割定義をそのまま再利用) ---
    print("[B1REDESIGN-AUDIO] Comment 1生成開始...")
    c1_context = f"【Full Story Part 1(これから聞く本文)】\n{parts['part1']}"
    c1_result = b1s.run_support_text(client, b1s.COMMENT_1_ROLE, c1_context)

    print("[B1REDESIGN-AUDIO] Comment 2生成開始...")
    c2_context = f"【Full Story Part 1(聞き終えた本文)】\n{parts['part1']}\n\n【Full Story Part 2(これから聞く本文)】\n{parts['part2']}"
    c2_result = b1s.run_support_text(client, b1s.COMMENT_2_ROLE, c2_context)

    print("[B1REDESIGN-AUDIO] Comment 3生成開始...")
    c3_context = (f"【Full Story Part 1】\n{parts['part1']}\n\n【Full Story Part 2】\n{parts['part2']}\n\n"
                  f"【これから聞くPointの見出しのみ(内容は伏せる)】\n"
                  f"Point One heading: {parts['point_one_heading']}\nPoint Two heading: {parts['point_two_heading']}")
    c3_result = b1s.run_support_text(client, b1s.COMMENT_3_ROLE, c3_context)

    print("[B1REDESIGN-AUDIO] Comment 4生成開始...")
    c4_context = (f"【Point One(聞き終えた内容)】\n{parts['point_one_heading']}\n{parts['point_one_body']}\n\n"
                  f"【Point Two(聞き終えた内容)】\n{parts['point_two_heading']}\n{parts['point_two_body']}\n\n"
                  f"【これから聞くIn One Line】\n{parts['in_one_line']}")
    c4_result = b1s.run_support_text(client, b1s.COMMENT_4_ROLE, c4_context)

    comments = {"comment_1": c1_result, "comment_2": c2_result, "comment_3": c3_result, "comment_4": c4_result}
    for key, result in comments.items():
        with open(f"{OUT_DIR}/audit/{key}_attempts.json", "w", encoding="utf-8") as f:
            json.dump(result["attempts"], f, ensure_ascii=False, indent=2, default=str)
        if result["status"] != "OK":
            print(f"[B1REDESIGN-AUDIO] {key}生成失敗: {result['status']}")

    # --- Preview(Comment1/2完成後に生成し、重複を避ける) ---
    b1_b_full_text = (f"# {parts['title']}\n\n{parts['part1']}\n\n{parts['part2']}\n\n"
                       f"### {parts['point_one_heading']}\n{parts['point_one_body']}\n\n"
                       f"### {parts['point_two_heading']}\n{parts['point_two_body']}\n\n"
                       f"## In one line…\n{parts['in_one_line']}")
    print("[B1REDESIGN-AUDIO] Preview生成開始...")
    preview_role = b1s.PREVIEW_ROLE.format(
        comment_1=c1_result.get("text") or "(生成失敗)",
        comment_2=c2_result.get("text") or "(生成失敗)",
    )
    preview_context = f"【エピソード全文(参考、新しいFactの追加禁止)】\n{b1_b_full_text}"
    preview_result = b1s.run_support_text(client, preview_role, preview_context)
    with open(f"{OUT_DIR}/audit/preview_attempts.json", "w", encoding="utf-8") as f:
        json.dump(preview_result["attempts"], f, ensure_ascii=False, indent=2, default=str)

    support_texts = {
        "preview": preview_result.get("text"), "comment_1": c1_result.get("text"),
        "comment_2": c2_result.get("text"), "comment_3": c3_result.get("text"),
        "comment_4": c4_result.get("text"),
    }
    with open(f"{OUT_DIR}/support_texts.json", "w", encoding="utf-8") as f:
        json.dump(support_texts, f, ensure_ascii=False, indent=2)

    # --- Key Phrases(B1-B最終本文全体に対し、方式L+Canonicalizationで新規選定) ---
    kp_dir = f"{OUT_DIR}/key_phrases"
    print("[B1REDESIGN-AUDIO] Key Phrase選定開始(B1-B最終本文から、旧B2版の流用なし)...")
    kp_selection = b1s.run_key_phrase_selection(b1_b_full_text, kp_dir)
    print(f"[B1REDESIGN-AUDIO] Key Phrase選定status={kp_selection['status']}")
    kp_final = None
    if kp_selection["status"] == "KEY_WORDS_STRUCTURE_PASS":
        print("[B1REDESIGN-AUDIO] Key Phrase Canonicalization開始...")
        kp_canon = b1s.run_key_phrase_canonicalization(b1_b_full_text, kp_selection["original_items"], kp_dir)
        print(f"[B1REDESIGN-AUDIO] Canonicalization status={kp_canon['status']}")
        kp_final = kp_canon.get("merged")

    summary = {
        "b1_b_source_sha256": actual_sha256, "b1_b_identity_ok": identity_ok,
        "comment_status": {k: v["status"] for k, v in comments.items()},
        "preview_status": preview_result["status"],
        "key_phrase_selection_status": kp_selection["status"],
        "key_phrase_canonicalization_status": (kp_final is not None),
    }
    with open(f"{OUT_DIR}/run_summary_scaffold.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print("[B1REDESIGN-AUDIO] 完了。summary:", json.dumps(summary, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
