# ============================================================
# er003_v1_n3_01_scaffold_generate.py
# ER-003-A2-B1-N3-01: 3テーマ×2レベル Scaffold(Preview/Comments/
# semantic heading/Key Phrases)生成
# ============================================================
# B1のPreview/Comment1-4は er003_v1_b1_scaffold_01_generate.py
# (b1s)のCOMMENT_1〜4_ROLE/PREVIEW_ROLE/run_support_textをそのまま
# 再利用する(すでにComment 3=Bridge role、Comment 4=sentence数非断定
# へ修正済み)。A2のPreview/Comment1・2・4は er003_v1_iran01_a2_
# generate.py (a2gen)のROLEをそのまま再利用するが、Comment 3のみ、
# 今回のN3-01 spec 25節(A2ではPoint内容を多少先出ししてよい)に従った
# 専用roleを新規定義する。
#
# semantic headingは、article.md自体の「###」見出し(writerが本文と
# 同時に生成したもの)をそのまま使う。新しいLLM呼び出しは行わない
# (見出し先頭の"⭐ "装飾のみ除去する)。
#
# Key Phrase選定はer003_b1_p2_keywords/er003_key_words_canonicalization/
# er003_key_words_productionを直接importし、b1s/a2genと同一の呼び出し
# パターンで再利用する(新しい選定ロジックは設計しない)。article_idを
# 動的に渡せるよう、b1s/a2genの関数をそのまま呼ばず薄いwrapperを用意する。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_n3_01_scaffold_generate.py

from __future__ import annotations

import json
import os
import re

import er003_b1_p2_keywords as bk
import er003_key_words_canonicalization as kc
import er003_key_words_production as prod
import er003_v1_b1_scaffold_01_generate as b1s
import er003_v1_iran01_a2_generate as a2gen
import er003_v1_n3_01_articles_generate as gen
import er006_model_routing_contract_01 as routing

THEMES = gen.THEMES

# ER-006-MODEL-ROUTING-CONTRACT-01 / 追補(SSOT迂回防止): B1/A2 Support
# (Comment/Preview/Key Phrase選定・正規化含む)はApproved Model(Luna)をSSOTから
# 明示指定する。モジュール変数へ事前計算せず、呼び出しの都度この関数を経由させる
# ことで、各API call直前にfail-closed検証が実行される。


def _b1_support_model() -> str:
    return routing.require_model("B1_SUPPORT", routing.SUPPORT_MODEL)


def _a2_support_model() -> str:
    return routing.require_model("A2_SUPPORT", routing.SUPPORT_MODEL)


# ============================================================
# 記事本文の分割(title / part1 / part2 / point heading+body ×2 / in_one_line)
# ============================================================
_HEADING_DECORATION_RE = re.compile(r"^[\W_]+\s*")

# ER-005-E2E-TTS-ANALYSIS-FIX-01(2026-08-21)で発見: ER-003-POINT-
# NOTIFICATION-01(CURRENT_SPEC.md、DECIDED)は「Point One./Point Two.」
# という番号の読み上げをNotification音で置き換える決定だが、Writerが
# 生成する### semantic headingに"Point One: "のような番号ラベルの
# 語がそのまま残っていることがあり、_HEADING_DECORATION_RE(先頭の記号・
# 装飾のみ除去)ではこの語自体は除去できない。その結果、番号ラベル入りの
# 見出しがTTSへそのまま渡り、B1のpoint_one_heading/point_two_headingが
# ASR検証に8回とも失敗する実例が見つかった(TTSが"Point One:"を安定して
# 読み上げず、検証がすり抜けなかったため運良く発覚したに過ぎない)。
# clean_heading側でこのラベルそのものも除去する(表示用H3見出し自体は
# 変更しない。TTS入力に渡す前の値のみを加工する)。
_POINT_NUMBER_LABEL_RE = re.compile(
    r"^\s*(Point\s+(One|Two|1|2)|第(一|二)に)\s*[:：,、\-–—.]?\s*", flags=re.IGNORECASE)


def clean_heading(raw: str) -> str:
    no_decoration = _HEADING_DECORATION_RE.sub("", raw).strip()
    return _POINT_NUMBER_LABEL_RE.sub("", no_decoration).strip()


# ER-005-E2E-TTS-ANALYSIS-FIX-01 Part D: clean_heading側の除去に加えて、
# 実際にTTSへ渡す直前(Script Assembly / pre-TTS)でも独立した機械的
# チェックを行う。LLM(Writer)の出力内容やclean_headingの実装に依存
# せず、この文字列が万一残っていた場合はTTS API呼び出し自体を行わず
# 例外で止める「最後の砦」。Point見出し・Point本文の4segment
# (point_one_heading/point_two_heading/point_one/point_two)の
# TTS入力テキストに対して呼び出す。
_POINT_NUMBER_LABEL_ANYWHERE_RE = re.compile(
    r"Point\s+(One|Two|1|2)\b|第(一|二)に", flags=re.IGNORECASE)


def assert_no_point_number_label(text: str, segment_name: str) -> None:
    m = _POINT_NUMBER_LABEL_ANYWHERE_RE.search(text)
    if m:
        raise RuntimeError(
            f"[ER-003-POINT-NOTIFICATION-01違反] segment={segment_name!r} のTTS入力テキストに"
            f"Point番号ラベル({m.group(0)!r})が含まれています。Point番号はNotification音で"
            f"表現する仕様のため、この文字列をTTSへ渡してはいけません。TTS呼び出しを中止します。"
            f"\nテキスト: {text!r}")


def split_article_text(text: str) -> dict:
    title_match = re.match(r"^#\s+(.+?)\s*\n", text)
    title = title_match.group(1).strip() if title_match else ""

    h3_matches = list(re.finditer(r"^###\s+(.+?)\s*$", text, flags=re.MULTILINE))
    if len(h3_matches) != 2:
        raise RuntimeError(f"###見出しがちょうど2つではありません(検出数: {len(h3_matches)})")
    in_one_line_match = re.search(r"^##\s+In [Oo]ne [Ll]ine[…\.]*\s*\n(.+)", text, flags=re.MULTILINE | re.DOTALL)
    if not in_one_line_match:
        raise RuntimeError("『## In one line…』見出しが見つかりません")

    intro_text = text[title_match.end():h3_matches[0].start()].strip() if title_match else text[:h3_matches[0].start()].strip()
    point_one_heading = clean_heading(h3_matches[0].group(1))
    point_one_body = text[h3_matches[0].end():h3_matches[1].start()].strip()
    point_two_heading = clean_heading(h3_matches[1].group(1))
    point_two_body = text[h3_matches[1].end():in_one_line_match.start()].strip()
    in_one_line_text = in_one_line_match.group(1).strip()

    def strip_markdown_bold(s: str) -> str:
        # writerが一部の文だけを**bold**で強調することがあるため、
        # 文中どこにあってもMarkdown強調記号だけを取り除く(語は変更しない)。
        return re.sub(r"\*\*(.+?)\*\*", r"\1", s)

    title = strip_markdown_bold(title)
    intro_text = strip_markdown_bold(intro_text)
    point_one_heading = strip_markdown_bold(point_one_heading)
    point_one_body = strip_markdown_bold(point_one_body)
    point_two_heading = strip_markdown_bold(point_two_heading)
    point_two_body = strip_markdown_bold(point_two_body)
    in_one_line_text = strip_markdown_bold(in_one_line_text)

    # Main Storyを段落単位で前半/後半に分割する(記事固有マーカー文を
    # 使わない汎用ロジック。語数がなるべく均等になる段落境界で分割する)。
    paragraphs = [p.strip() for p in intro_text.split("\n\n") if p.strip()]
    if len(paragraphs) < 2:
        raise RuntimeError(f"Main Storyの段落数が2未満です(検出数: {len(paragraphs)})")
    para_word_counts = [len(re.findall(r"[A-Za-z']+", p)) for p in paragraphs]
    total = sum(para_word_counts)
    running = 0
    split_idx = 1
    best_diff = None
    for i in range(1, len(paragraphs)):
        running += para_word_counts[i - 1]
        diff = abs(running - (total - running))
        if best_diff is None or diff < best_diff:
            best_diff = diff
            split_idx = i
    part1 = "\n\n".join(paragraphs[:split_idx])
    part2 = "\n\n".join(paragraphs[split_idx:])

    return {
        "title": title, "part1": part1, "part2": part2,
        "point_one_heading": point_one_heading, "point_one_body": point_one_body,
        "point_two_heading": point_two_heading, "point_two_body": point_two_body,
        "in_one_line": in_one_line_text,
    }


# ============================================================
# A2 Comment 3: 今回のN3-01専用role(spec 25節: Point内容を多少
# 先出ししてよい。B1のように機械的に重複削除しない)
# ============================================================
A2_COMMENT_3_ROLE_N3 = """あなたはPodcastのナビゲーターです。リスナーはFull Story Part 1・Part 2
(本文全体)をすでに聞き終わり、これからPoint One・Point Two(補足の視点)を
聞きます。その間に流す、Comment 3(役割: Story Meaning + Bridge to Points)を
日本語で書いてください。

役割: このニュース全体の意味を短く整理し、これから聞くPointへの橋渡しをします。
A2はJapanese Scaffoldとして機能するため、Point Oneの見出しが示す視点に軽く
触れる程度は許容されます(ただしPointの結論・具体的な答えまでは先に言わない
でください)。新しいFactを追加しないでください。易しい日本語で2〜3文に
してください。

【今回聞くPointの見出し】
Point One heading: {point_one_heading}
Point Two heading: {point_two_heading}"""


def get_client():
    return b1s.get_client()


# ============================================================
# Key Phrase選定(article_idを動的に渡すための薄いwrapper)
# ============================================================
def run_key_phrase_selection(article_text: str, out_dir: str, article_id: str, source_level: str,
                              process: str = None) -> dict:
    """process(ER-006-MODEL-ROUTING-CONTRACT-01追補): "B1_SUPPORT"/"A2_SUPPORT"を
    渡すと、routing.require_model()で検証済みのApproved ModelをAPI call直前に
    このスコープ内で確定させる(呼び出し元でmodelを事前計算させない)。Noneの
    場合はbk.make_selector_fnの既定値(Sol系譜)のまま、後方互換を保つ。"""
    os.makedirs(out_dir, exist_ok=True)
    template = bk.load_prompt_template()
    user_message = bk.build_user_message(article_text, template=template)
    with open(f"{out_dir}/keywords_selector_prompt.txt", "w", encoding="utf-8") as f:
        f.write(user_message)

    def make_selector_factory():
        model = routing.require_model(process, routing.SUPPORT_MODEL) if process else None
        return bk.make_selector_fn(user_message, model=model)

    parsed, status, attempts, model_id, response_id = prod.run_production_selection_gate(
        article_id, make_selector_factory, article_text,
        strategy_id=prod.STANDARD_STRATEGY_ID, max_attempts=1,
    )
    runtime_metadata = {
        "article_id": article_id, "strategy_id": prod.STANDARD_STRATEGY_ID, "source_level": source_level,
        "record_status": "PROTOTYPE", "approval_status": "NOT_APPROVED",
        "model": bk.SELECTOR_MODEL, "reasoning_effort": bk.SELECTOR_REASONING_EFFORT,
        "final_status": status, "model_id": model_id, "response_id": response_id,
        "attempts_detail": [{k: v for k, v in a.items() if k != "raw_text"} for a in attempts],
    }
    with open(f"{out_dir}/keywords_runtime_metadata.json", "w", encoding="utf-8") as f:
        json.dump(runtime_metadata, f, ensure_ascii=False, indent=2)

    result = {"status": status, "parsed": parsed}
    if status != "KEY_WORDS_STRUCTURE_PASS":
        return result
    result["original_items"] = parsed["items"]
    return result


def run_key_phrase_canonicalization(article_text: str, original_items: list, out_dir: str, article_id: str,
                                     process: str = None) -> dict:
    """processの意味はrun_key_phrase_selection()と同じ(ER-006-MODEL-ROUTING-
    CONTRACT-01追補)。"""
    template = kc.load_prompt_template()
    user_message = kc.build_user_message(original_items, article_text, template=template)
    with open(f"{out_dir}/canonicalization_prompt.txt", "w", encoding="utf-8") as f:
        f.write(user_message)

    def make_factory():
        kwargs = {}
        if process is not None:
            kwargs["model"] = routing.require_model(process, routing.SUPPORT_MODEL)
        return kc.make_canonicalization_fn(user_message, **kwargs)

    parsed, status, attempts, model_id, response_id = kc.run_canonicalization_gate(make_factory, original_items)
    with open(f"{out_dir}/canonicalization_runtime_metadata.json", "w", encoding="utf-8") as f:
        json.dump({
            "article_id": article_id, "canonicalization_version": kc.CANONICALIZATION_VERSION,
            "record_status": "PROTOTYPE", "approval_status": "NOT_APPROVED",
            "final_status": status, "model_id": model_id, "response_id": response_id,
            "attempts_detail": [{k: v for k, v in a.items() if k != "raw_text"} for a in attempts],
        }, f, ensure_ascii=False, indent=2)

    result = {"status": status}
    if status not in ("CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
        return result
    merged = kc.merge_canonicalization_result(original_items, parsed["items"])
    with open(f"{out_dir}/keywords_canonicalized.json", "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    result["merged"] = merged
    return result


def run_key_phrases(article_text: str, out_dir: str, article_id: str, source_level: str,
                     process: str = None) -> dict:
    """processの意味はrun_key_phrase_selection()と同じ(ER-006-MODEL-ROUTING-
    CONTRACT-01追補、"B1_SUPPORT"/"A2_SUPPORT"を渡す)。"""
    sel = run_key_phrase_selection(article_text, out_dir, article_id, source_level, process=process)
    if sel["status"] != "KEY_WORDS_STRUCTURE_PASS":
        return {"selection": sel, "canonicalization": None}
    canon = run_key_phrase_canonicalization(article_text, sel["original_items"], out_dir, article_id, process=process)
    return {"selection": sel, "canonicalization": canon}


# ============================================================
# B1 Scaffold(English Preview/Comment1-4)
# ============================================================
def run_b1_scaffold(client, parts: dict, out_dir: str, article_text: str) -> dict:
    print(f"[N3-SCAFFOLD] B1 Comment 1生成開始({out_dir})...")
    c1_context = f"【Full Story Part 1(これから聞く本文)】\n{parts['part1']}"
    c1 = b1s.run_support_text(client, b1s.COMMENT_1_ROLE, c1_context, model=_b1_support_model())

    print(f"[N3-SCAFFOLD] B1 Comment 2生成開始({out_dir})...")
    c2_context = f"【Full Story Part 1(聞き終えた本文)】\n{parts['part1']}\n\n【Full Story Part 2(これから聞く本文)】\n{parts['part2']}"
    c2 = b1s.run_support_text(client, b1s.COMMENT_2_ROLE, c2_context, model=_b1_support_model())

    print(f"[N3-SCAFFOLD] B1 Comment 3生成開始({out_dir})...")
    c3_context = (f"【Full Story Part 1】\n{parts['part1']}\n\n【Full Story Part 2】\n{parts['part2']}\n\n"
                  f"【これから聞くPointの見出しのみ(内容は伏せる)】\n"
                  f"Point One heading: {parts['point_one_heading']}\nPoint Two heading: {parts['point_two_heading']}")
    c3 = b1s.run_support_text(client, b1s.COMMENT_3_ROLE, c3_context, model=_b1_support_model())

    print(f"[N3-SCAFFOLD] B1 Comment 4生成開始({out_dir})...")
    c4_context = (f"【Point One(聞き終えた内容)】\n{parts['point_one_heading']}\n{parts['point_one_body']}\n\n"
                  f"【Point Two(聞き終えた内容)】\n{parts['point_two_heading']}\n{parts['point_two_body']}")
    c4 = b1s.run_support_text(client, b1s.COMMENT_4_ROLE, c4_context, model=_b1_support_model())

    print(f"[N3-SCAFFOLD] B1 Preview生成開始({out_dir})...")
    preview_prompt_role = b1s.PREVIEW_ROLE.format(
        comment_1=c1.get("text") or "(生成失敗)", comment_2=c2.get("text") or "(生成失敗)")
    preview_context = f"【エピソード全文(参考、新しいFactの追加禁止)】\n{article_text}"
    preview = b1s.run_support_text(client, preview_prompt_role, preview_context, model=_b1_support_model())

    results = {"preview": preview, "comment_1": c1, "comment_2": c2, "comment_3": c3, "comment_4": c4}
    os.makedirs(out_dir, exist_ok=True)
    with open(f"{out_dir}/b1_support_texts.json", "w", encoding="utf-8") as f:
        json.dump({k: v.get("text") for k, v in results.items()}, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/b1_support_generation.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    return results


# ============================================================
# A2 Scaffold(Japanese Preview/Comment1-4)
# ============================================================
def run_a2_scaffold(client, parts: dict, out_dir: str, article_text: str) -> dict:
    print(f"[N3-SCAFFOLD] A2 Comment 1生成開始({out_dir})...")
    c1_context = f"【Full Story Part 1(これから聞く本文、英語)】\n{parts['part1']}"
    c1 = a2gen.run_support_text(client, a2gen.COMMENT_1_ROLE, c1_context, model=_a2_support_model())

    print(f"[N3-SCAFFOLD] A2 Comment 2生成開始({out_dir})...")
    c2_context = f"【Full Story Part 1(聞き終えた本文)】\n{parts['part1']}\n\n【Full Story Part 2(これから聞く本文)】\n{parts['part2']}"
    c2 = a2gen.run_support_text(client, a2gen.COMMENT_2_ROLE, c2_context, model=_a2_support_model())

    print(f"[N3-SCAFFOLD] A2 Comment 3生成開始({out_dir})...")
    c3_role = A2_COMMENT_3_ROLE_N3.format(
        point_one_heading=parts["point_one_heading"], point_two_heading=parts["point_two_heading"])
    c3_context = f"【Full Story Part 1】\n{parts['part1']}\n\n【Full Story Part 2】\n{parts['part2']}"
    c3 = a2gen.run_support_text(client, c3_role, c3_context, model=_a2_support_model())

    print(f"[N3-SCAFFOLD] A2 Comment 4生成開始({out_dir})...")
    c4_context = (f"【Point One(聞き終えた内容)】\n{parts['point_one_heading']}\n{parts['point_one_body']}\n\n"
                  f"【Point Two(聞き終えた内容)】\n{parts['point_two_heading']}\n{parts['point_two_body']}")
    c4 = a2gen.run_support_text(client, a2gen.COMMENT_4_ROLE, c4_context, model=_a2_support_model())

    print(f"[N3-SCAFFOLD] A2 Preview生成開始({out_dir})...")
    preview_prompt_role = a2gen.PREVIEW_ROLE.format(
        comment_1=c1.get("text") or "(生成失敗)", comment_2=c2.get("text") or "(生成失敗)")
    preview_context = f"【エピソード全文(参考、新しいFactの追加禁止)】\n{article_text}"
    preview = a2gen.run_support_text(client, preview_prompt_role, preview_context, model=_a2_support_model())

    results = {"preview": preview, "comment_1": c1, "comment_2": c2, "comment_3": c3, "comment_4": c4}
    os.makedirs(out_dir, exist_ok=True)
    with open(f"{out_dir}/a2_support_texts.json", "w", encoding="utf-8") as f:
        json.dump({k: v.get("text") for k, v in results.items()}, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/a2_support_generation.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    return results


def run_theme_scaffold(client, theme: dict) -> dict:
    theme_id = theme["theme_id"]
    result = {}

    for label, run_fn, source_level in [
        ("b1b", run_b1_scaffold, "B1-B(N3-01, direct generation)"),
        ("a2", run_a2_scaffold, "A2(V2改1, N3-01)"),
    ]:
        out_dir = f"{theme['out_dir']}/{label}"
        os.makedirs(f"{out_dir}/audit", exist_ok=True)
        with open(f"{out_dir}/article.md", encoding="utf-8") as f:
            article_text = f.read()
        parts = split_article_text(article_text)
        with open(f"{out_dir}/parts.json", "w", encoding="utf-8") as f:
            json.dump(parts, f, ensure_ascii=False, indent=2)

        support = run_fn(client, parts, out_dir, article_text)

        kp_dir = f"{out_dir}/key_phrases"
        article_id = f"N3_{theme_id}_{label}"
        kp_process = "B1_SUPPORT" if label == "b1b" else "A2_SUPPORT"
        kp = run_key_phrases(article_text, kp_dir, article_id, source_level, process=kp_process)
        kp_status = (kp["canonicalization"] or {}).get("status") if kp["canonicalization"] else kp["selection"]["status"]
        print(f"[N3-SCAFFOLD] {theme_id}/{label}: key phrase status={kp_status}")

        result[label] = {"parts": parts, "support": {k: v.get("status") for k, v in support.items()},
                          "key_phrases_status": kp_status}

    with open(f"{theme['out_dir']}/scaffold_run_summary.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[N3-SCAFFOLD] {theme_id} 完了。")
    return result


def main():
    client = get_client()
    for theme in THEMES:
        run_theme_scaffold(client, theme)
    print("[N3-SCAFFOLD] 全テーマ完了。")


if __name__ == "__main__":
    main()
