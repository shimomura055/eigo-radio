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

import functools
import itertools
import json
import os
import re
import shutil
import time
from collections import Counter

import er003_audio_tts_asr_safety as safety
import er003_b1_p2_keywords as bk
import er003_key_words_canonicalization as kc
import er003_key_words_gloss_alignment as gloss_align
import er003_key_words_production as prod
import er003_v1_b1_scaffold_01_generate as b1s
import er003_v1_iran01_a2_generate as a2gen
import er003_v1_n3_01_articles_generate as gen
import er006_model_routing_contract_01 as routing
import er008_shared_point_blueprint_01 as blueprint_mod
import er011_key_phrase_set_redundancy_qa_01 as redundancy_qa

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
# FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W1、2026-09-29、ユーザー正式
# 決定APPROVED_FOR_PRODUCTION): Family X新記事構造(途中Heading廃止・
# 忠実英訳・段落境界での決定論的3分割)。上のsplit_article_text()(###
# 見出し2つ前提、Family A本体はじめ多数のFamilyが現役利用)は一切変更
# しない。本関数は完全に別名・別実装であり、Family X経路
# (er012_e_family_entertainment_two_level_runner_01.run_writer_stage())
# のみが呼び出す(他Familyは無影響)。
#
# アルゴリズムはer045_family_x_no_heading_segmentation_trial_01.
# deterministic_three_way_split()と同一(段落単位、2境界全探索、二乗誤差
# 最小化)。段落数<3の場合はRuntimeErrorを送出せず
# status="TOO_FEW_PARAGRAPHS"を返す(retry要否は呼び出し側が判断する。
# OPEN-228のような無retryクラッシュを新経路では起こさない)。
# ============================================================
def _family_x_word_count_en(s: str) -> int:
    return len(re.findall(r"[A-Za-z']+", s or ""))


def split_family_x_article_text_v2(text: str) -> dict:
    """Family X新構造(# Title -> 本文[段落、見出しなし] ->『## In one
    line』)を、段落境界のみを使った決定論的アルゴリズムでpart1/2/3へ
    3分割する。段落数<3、title行欠落、In one line欠落、本文中への
    Markdown見出し行混入は、いずれもRuntimeErrorではなくstatus値で返す
    (呼び出し側`_family_x_ensure_split_or_paragraph_retry()`が既に
    status!="OK"を共通に1回だけmust-fix retryする設計のため、このGate
    自体をここへ集約する。OPEN-228のような無retryクラッシュを新経路では
    起こさない)。

    FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W5、Opus L2所見MAJOR-2
    是正、2026-09-29): 旧実装はAdvanced側の`_FAMILY_X_TITLE_BODY_RE`
    (`^#\\s+`必須)と非対称に、title行が無くても`title=""`のままstatus=
    "OK"を返し、`## In one line`欠落時はRuntimeErrorを直接送出していた
    (retryされず課金後にクラッシュしていた)。加えて本文中のMarkdown見出し
    行混入を検査する機械Gateがどこにも無かった。以下の3点をAdvancedと
    対称のGateとして追加する: (1) `^#\\s+`のtitle行必須、(2)『## In one
    line』必須、(3) 本文にMarkdown見出し行(`^#{1,6}\\s`)が混入していない
    こと。"""
    title_match = re.match(r"^#\s+(.+?)\s*\n", text)
    if not title_match:
        return {"status": "NG_MISSING_TITLE", "paragraph_count": None, "title": ""}
    title = title_match.group(1).strip()
    body_start = title_match.end()

    in_one_line_match = re.search(
        r"^##\s+In [Oo]ne [Ll]ine[…\.]*\s*\n(.+)", text, flags=re.MULTILINE | re.DOTALL)
    if not in_one_line_match:
        return {"status": "NG_MISSING_IN_ONE_LINE", "paragraph_count": None, "title": title}
    if in_one_line_match.start() < title_match.end():
        return {"status": "NG_IN_ONE_LINE_BEFORE_TITLE", "paragraph_count": None, "title": title}

    def strip_markdown_bold(s: str) -> str:
        return re.sub(r"\*\*(.+?)\*\*", r"\1", s)

    title = strip_markdown_bold(title)
    body_text = strip_markdown_bold(text[body_start:in_one_line_match.start()].strip())
    in_one_line_text = strip_markdown_bold(in_one_line_match.group(1).strip())

    heading_in_body_match = re.search(r"^#{1,6}\s", body_text, flags=re.MULTILINE)
    if heading_in_body_match:
        return {"status": "NG_HEADING_IN_BODY", "paragraph_count": None, "title": title,
                "in_one_line": in_one_line_text}

    paragraphs = [p.strip() for p in body_text.split("\n\n") if p.strip()]
    n = len(paragraphs)
    if n < 3:
        return {"status": "TOO_FEW_PARAGRAPHS", "paragraph_count": n, "title": title,
                "in_one_line": in_one_line_text}

    counts = [_family_x_word_count_en(p) for p in paragraphs]
    total = sum(counts)
    target = total / 3.0

    best = None
    for i, j in itertools.combinations(range(1, n), 2):
        c1 = sum(counts[:i])
        c2 = sum(counts[i:j])
        c3 = sum(counts[j:])
        cost = (c1 - target) ** 2 + (c2 - target) ** 2 + (c3 - target) ** 2
        key = (cost, i, j)
        if best is None or key < best[0]:
            best = (key, i, j, c1, c2, c3)

    _, i, j, c1, c2, c3 = best
    part1 = "\n\n".join(paragraphs[:i])
    part2 = "\n\n".join(paragraphs[i:j])
    part3 = "\n\n".join(paragraphs[j:])

    return {
        "status": "OK", "title": title, "paragraph_count": n,
        "boundary_i": i, "boundary_j": j,
        "part1": part1, "part2": part2, "part3": part3,
        "in_one_line": in_one_line_text,
        "word_counts": {
            "part1": c1, "part2": c2, "part3": c3,
            "in_one_line": _family_x_word_count_en(in_one_line_text), "total": total,
        },
    }


# ============================================================
# A2 Comment 3: 今回のN3-01専用role(spec 25節: Point内容を多少
# 先出ししてよい。B1のように機械的に重複削除しない)
# ============================================================
A2_COMMENT_3_ROLE_N3 = """あなたはPodcastのナビゲーターです。リスナーは本文の前半・後半
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
                              process: str = None, diagnostic_note: str = None,
                              kp_backend: str = "strategy_l", synthetic: bool = False,
                              excluded_phrases: list = None) -> dict:
    """process(ER-006-MODEL-ROUTING-CONTRACT-01追補): "B1_SUPPORT"/"A2_SUPPORT"を
    渡すと、routing.require_model()で検証済みのApproved ModelをAPI call直前に
    このスコープ内で確定させる(呼び出し元でmodelを事前計算させない)。Noneの
    場合はbk.make_selector_fnの既定値(Sol系譜)のまま、後方互換を保つ。

    diagnostic_note(ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01追加): 前回の
    選定でKey Phrase Set Redundancy QA(er011_key_phrase_set_redundancy_qa_01.py)
    がNGと判定した場合、その診断情報をprompt末尾へ追加して再選定させる
    (記事固有のハードコードではなく、直前の判定結果をそのまま渡すだけ)。

    kp_backend(KPFT 委任_02[2026-10-22]で整理): `"fulltext_p2"`=Family X/Zの正式backend(全文選定・Prompt 2・最大3件、
    `er105_kp_fulltext_selector_01`)。既定`"strategy_l"`=従来のStrategy L全文方式(Family A/B/C等、本関数の従来挙動を変更しない)。
    旧`"db_hybrid"`(DB Hybrid+M2供給+Strategy Lへのfallback)はX/Zから撤去済み。未対応の値はValueError(黙ってStrategy Lへ
    倒さない)。いずれの経路でも1回`_log_kp_backend_telemetry()`を記録する。
    `synthetic`(既定False)は、evidence/testスクリプトが強制failure注入等でこの呼び出しを発生させた場合にTrueを渡す。"""
    if kp_backend == FULLTEXT_BACKEND_ID:
        return _run_key_phrase_selection_fulltext(
            article_text, out_dir, article_id, source_level, process=process,
            diagnostic_note=diagnostic_note, synthetic=synthetic, excluded_phrases=excluded_phrases)
    if excluded_phrases:
        raise ValueError("excluded_phrases(外側retryの明示除外)は全文選定backend(fulltext_p2)専用。A/B/C(strategy_l)には適用しない")
    if kp_backend != "strategy_l":
        raise ValueError(f"未対応のkp_backend={kp_backend!r}(対応: 'strategy_l', {FULLTEXT_BACKEND_ID!r}。旧db_hybridはKPFT 委任_02で撤去)")
    result = _run_key_phrase_selection_strategy_l(
        article_text, out_dir, article_id, source_level, process=process,
        diagnostic_note=diagnostic_note)
    result["kp_backend_used"] = "strategy_l"
    # 修正1回目(Opus L2所見S1、2026-09-28): result["role_counts"]は
    # `_run_key_phrase_selection_strategy_l`がstatus(PASS/INVALID)を
    # 問わず常に計算・格納する(旧: result.get("original_items")経由の
    # 計算はstatus PASS時のみ入手可能なitemsに依存していたため、role
    # 不成立でINVALIDになった瞬間だけtelemetryがrole_counts: nullに
    # なる観測性の欠落があった)。
    _log_kp_backend_telemetry(
        article_id, source_level, requested_backend="strategy_l", backend_used="strategy_l",
        final_status=result.get("status"), fallback_triggered=False,
        model_id=result.get("model_id"), cost_jpy=None, synthetic=synthetic,
        source_reference_contract=FREE_TEXT_SOURCE_REFERENCE_CONTRACT_ID,
        role_counts=result.get("role_counts"),
        strategy_l_attempts=result.get("strategy_l_attempts"),
        retry_reached_second_attempt=result.get("retry_reached_second_attempt"))
    return result


# KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01 委任_02(2026-10-22、ユーザーAPPROVED_FOR_PRODUCTION): Family X/Zの既定backend。
# 記事全文+正式Prompt 2(GPT-6 Luna、一字一句固定)で最大3件を直接選定する(`er105_kp_fulltext_selector_01`)。
# 選定段のみを置換し、後段(canonicalization/gloss再整合/Redundancy QA/Z D1/音声/組立)は既存を再利用する。
# A/B/C(kp_backend="strategy_l"既定)は無変更(27-7: 開発対象外)。
FULLTEXT_BACKEND_ID = "fulltext_p2"


def _run_key_phrase_selection_fulltext(article_text: str, out_dir: str, article_id: str, source_level: str,
                                        process: str = None, diagnostic_note: str = None, synthetic: bool = False,
                                        excluded_phrases: list = None) -> dict:
    """全文選定backend(Prompt 2)。選定失敗はretry上限(er105)後にstatus!=PASSを返す(fail-closed。旧経路へのfallbackはしない)。
    モデルrouting違反・API 400等の設定不備はFulltextSelectionErrorを送出して即停止する。"""
    import er105_kp_fulltext_selector_01 as ft
    result = ft.run_fulltext_selection(article_text, out_dir, article_id, source_level, process=process,
                                       diagnostic_note=diagnostic_note, excluded_phrases=excluded_phrases)
    _log_kp_backend_telemetry(
        article_id, source_level, requested_backend=FULLTEXT_BACKEND_ID, backend_used=FULLTEXT_BACKEND_ID,
        final_status=result.get("status"), fallback_triggered=False, model_id=result.get("model_id"),
        cost_jpy=None, synthetic=synthetic, source_reference_contract=ft.FULLTEXT_SOURCE_REF_ID,
        kp_attempts=result.get("kp_attempts"), shortfall=result.get("shortfall"),
        prompt_sha256=ft.PROMPT_2_SHA256)
    return result


def _run_key_phrase_selection_strategy_l(article_text: str, out_dir: str, article_id: str, source_level: str,
                                          process: str = None, diagnostic_note: str = None) -> dict:
    """既存Strategy L全文方式(本文全体をprompt送信)。2026-09-27に
    run_key_phrase_selection()から名前を分離しただけで、本体は無変更
    (KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01のFallback経路
    としてもそのまま再利用する)。"""
    os.makedirs(out_dir, exist_ok=True)
    template = bk.load_prompt_template()
    user_message = bk.build_user_message(article_text, template=template)
    if diagnostic_note:
        user_message = user_message + "\n\n" + diagnostic_note
    with open(f"{out_dir}/keywords_selector_prompt.txt", "w", encoding="utf-8") as f:
        f.write(user_message)

    def make_selector_factory():
        model = routing.require_model(process, routing.SUPPORT_MODEL) if process else None
        return bk.make_selector_fn(user_message, model=model)

    # KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01 修正1回目(2026-09-28、
    # ユーザー既決事項): この経路のmax_attempts=1固定(本タスク以前からの
    # 既存挙動、role構成不成立でも自動retryしなかった)を、Production
    # 既定のMAX_PRODUCTION_RETRY_ATTEMPTS(=2)に揃える。2回目に到達した
    # 場合は報告必須のため、下記でruntime_metadata/telemetryへ記録し、
    # printで明示する。
    parsed, status, attempts, model_id, response_id = prod.run_production_selection_gate(
        article_id, make_selector_factory, article_text,
        strategy_id=prod.STANDARD_STRATEGY_ID, max_attempts=prod.MAX_PRODUCTION_RETRY_ATTEMPTS,
    )
    strategy_l_attempts = len(attempts)
    retry_reached_second_attempt = strategy_l_attempts >= 2
    if retry_reached_second_attempt:
        first_attempt_status = attempts[0].get("status") if attempts else None
        print(f"[KP-BACKEND][STRATEGY-L][RETRY] {article_id}: Key Phrase選定が2回目の試行に到達しました"
              f"(1回目status={first_attempt_status}, 最終status={status})。")
    # KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01(2026-09-28、Fable判断):
    # Strategy L経路にもDB Hybridと同名のcontract表示・role_countsを
    # 追加する。5枠外候補データ(F-4)は本Phaseでは実装しない(新出力契約は
    # ユーザー判断待ち)ため、明示的にauxiliary_candidates=nullで
    # 「未提供」を記録する(黙示的な欠落にしない)。
    role_counts = dict(Counter(
        it.get("key_phrase_role") for it in ((parsed or {}).get("items") or []) if isinstance(it, dict)))
    runtime_metadata = {
        "article_id": article_id, "strategy_id": prod.STANDARD_STRATEGY_ID, "source_level": source_level,
        "record_status": "PROTOTYPE", "approval_status": "NOT_APPROVED",
        "model": bk.SELECTOR_MODEL, "reasoning_effort": bk.SELECTOR_REASONING_EFFORT,
        "final_status": status, "model_id": model_id, "response_id": response_id,
        "selection_contract": "4plus1_v1", "role_counts": role_counts,
        "auxiliary_candidates": None, "auxiliary_candidates_reason": "not_available_strategy_l",
        "attempts_detail": [{k: v for k, v in a.items() if k != "raw_text"} for a in attempts],
        # KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01 修正1回目(2026-09-28、
        # ユーザー既決事項): retry最大2回・2回目到達時の報告必須。
        "strategy_l_attempts": strategy_l_attempts,
        "retry_reached_second_attempt": retry_reached_second_attempt,
    }
    with open(f"{out_dir}/keywords_runtime_metadata.json", "w", encoding="utf-8") as f:
        json.dump(runtime_metadata, f, ensure_ascii=False, indent=2)

    result = {
        "status": status, "parsed": parsed, "model_id": model_id, "role_counts": role_counts,
        "strategy_l_attempts": strategy_l_attempts,
        "retry_reached_second_attempt": retry_reached_second_attempt,
    }
    if status != "KEY_WORDS_STRUCTURE_PASS":
        return result
    result["original_items"] = parsed["items"]
    return result


KP_BACKEND_TELEMETRY_PATH = os.path.join("er030_output", "kp_backend_telemetry_01", "telemetry.jsonl")

# 修正1回目(Opus L2所見B1、2026-09-27): telemetry各行にspec_idを付与し、
# 将来別specがtelemetry.jsonlを共有する場合でも起源を区別できるようにする。
KP_BACKEND_SPEC_ID = "KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01"

# Strategy L全文方式はLLMがsource_sentence/source_spanを自由記述する契約(telemetryで全文選定の契約と区別するタグ)。
FREE_TEXT_SOURCE_REFERENCE_CONTRACT_ID = "free_text_strategy_l"


def _log_kp_backend_telemetry(article_id: str, source_level: str, requested_backend: str,
                               backend_used: str, final_status, fallback_triggered: bool,
                               fallback_reason_code: str = None, model_id: str = None,
                               cost_jpy: float = None, synthetic: bool = False, **extra) -> None:
    """KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01: Key Phrase選定
    backendの使用実績・fallback発火をjsonlへ追記する。

    修正1回目(Opus L2所見B1、2026-09-27): 既定"strategy_l"経路も含め、
    `run_key_phrase_selection`のすべての呼び出しで必ず1行記録する
    (旧: db_hybrid経路のみ記録、legacy既定経路は無記録だった観測性の
    欠落を解消)。全エントリが`requested_backend`/`backend_used`/
    `final_status`/`fallback_triggered`/`fallback_reason_code`/
    `synthetic`(bool)/`spec_id`/`article_id`/`level`/`model_id`/
    `cost_jpy`を持つ(fallbackが黙示的に通常経路化しないよう、常にこの
    1ファイルへ記録する)。"""
    os.makedirs(os.path.dirname(KP_BACKEND_TELEMETRY_PATH), exist_ok=True)
    entry = {
        "timestamp": time.time(), "spec_id": KP_BACKEND_SPEC_ID,
        "article_id": article_id, "level": source_level,
        "requested_backend": requested_backend, "backend_used": backend_used,
        "final_status": final_status, "fallback_triggered": fallback_triggered,
        "fallback_reason_code": fallback_reason_code, "model_id": model_id, "cost_jpy": cost_jpy,
        "synthetic": bool(synthetic),
        **extra,
    }
    with open(KP_BACKEND_TELEMETRY_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def run_key_phrase_canonicalization(article_text: str, original_items: list, out_dir: str, article_id: str,
                                     process: str = None) -> dict:
    """processの意味はrun_key_phrase_selection()と同じ(ER-006-MODEL-ROUTING-
    CONTRACT-01追補)。

    gloss再整合(KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01、2026-10-15): 修正版が唯一の方式で既定ON。
    kill switchはプロセス環境変数EIGO_KP_GLOSS_ALIGNMENT=0のみ(gloss_align.flag_enabled())。"""
    # KPFT 委任_02: 全文選定itemがあるときだけ、fulltext版template(Listening Blocker/5件記述を除去、基本形化規則を追加)と
    # fulltext専用schema(lemma_normalization enum)を使う。A/B/C(fulltext_source_refなし)は従来のtemplate/schemaのまま(バイト同一)。
    is_fulltext = any(kc.is_fulltext_item(it) for it in original_items)
    template = kc.load_prompt_template(kc.FULLTEXT_PROMPT_TEMPLATE_PATH) if is_fulltext else kc.load_prompt_template()
    user_message = kc.build_user_message(original_items, article_text, template=template)
    with open(f"{out_dir}/canonicalization_prompt.txt", "w", encoding="utf-8") as f:
        f.write(user_message)

    def make_factory():
        kwargs = {}
        if process is not None:
            kwargs["model"] = routing.require_model(process, routing.SUPPORT_MODEL)
        if is_fulltext:
            kwargs["schema"] = kc.CANONICALIZATION_JSON_SCHEMA_FULLTEXT
        return kc.make_canonicalization_fn(user_message, **kwargs)

    # OF-KPFT-P-07: 技術失敗の再試行前に待機する(canonicalization gateの既存sleep_fn(2)機構を全文選定itemにだけ有効化。A/B/Cは従来どおり即再試行)。
    # FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_20(課題②、UDR #173): 全文選定itemのときだけ、parse直後・validate前に
    # 所有格role後処理(er105.postprocess_possessor_roles: revertのみ・API 0)を適用する。A/B/Cの呼出点(他scaffold/generate)はhookを渡さない。
    # X/Z共通の唯一の経路(初回/外側retry/fallback/regeneration/resumeはすべて本関数を通る)。
    _postprocess = None
    if is_fulltext:
        import er105_kp_fulltext_selector_01 as _ft_pp
        _postprocess = _ft_pp.postprocess_possessor_roles
    parsed, status, attempts, model_id, response_id = kc.run_canonicalization_gate(
        make_factory, original_items, sleep_fn=(time.sleep if is_fulltext else None), postprocess=_postprocess)
    _canon_meta = {
        "article_id": article_id, "canonicalization_version": kc.CANONICALIZATION_VERSION,
        "record_status": "PROTOTYPE", "approval_status": "NOT_APPROVED",
        "final_status": status, "model_id": model_id, "response_id": response_id,
        "attempts_detail": [{k: v for k, v in a.items() if k != "raw_text"} for a in attempts],
    }
    if is_fulltext:
        _canon_meta["template"] = "fulltext_p2"
    with open(f"{out_dir}/canonicalization_runtime_metadata.json", "w", encoding="utf-8") as f:
        json.dump(_canon_meta, f, ensure_ascii=False, indent=2)

    result = {"status": status}
    if status not in ("CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
        return result
    merged = kc.merge_canonicalization_result(original_items, parsed["items"])
    # KP-GLOSS-ALIGNMENT-01(2026-10-14): 最終KPが表示候補に無い語を含む場合だけ、glossを最終KP基準で再整合する
    # (対象0件ならAPI呼出なし・merged無変更)。初回/redundancy retry/fallback/regenerationの全経路がこの関数を通る。
    def _align_factory(msg: str):
        kwargs = {}
        if process is not None:
            kwargs["model"] = routing.require_model(process, routing.SUPPORT_MODEL)
        else:
            kwargs["model"] = routing.SUPPORT_MODEL
        return gloss_align.make_alignment_fn(msg, **kwargs)

    # OF-233: alignment呼出のusageをcost loggerのstageタグ付きで記録できるようにする(cl.install()済みの場合のみ
    # raw_usage_log.jsonlへ記録される。未installなら何も起きない純粋加算)。
    import er005_cost_logger as _cl
    import time as _time
    _t_align0 = _time.monotonic()
    with _cl.logging_context(article_id or "unknown_article", "kp_gloss_alignment"):
        aligned = gloss_align.align_glosses(merged, article_text, _align_factory, out_dir=out_dir,
                                            article_id=article_id, enabled=gloss_align.flag_enabled())   # flagが唯一のkill switch
    _t_align = round(_time.monotonic() - _t_align0, 3)
    merged = aligned["merged"]
    result["gloss_alignment_status"] = aligned["status"]
    result["gloss_alignment_cost_jpy"] = aligned.get("cost_jpy")
    result["gloss_alignment_unresolved_ranks"] = aligned.get("unresolved_ranks") or []
    # OF-KGCPW-16: 監視指標(記録のみ。アラート機構は作らない。閾値はSSOT)。
    result["gloss_alignment_metrics"] = {
        "targets": len(aligned.get("targets") or []), "items": len(merged.get("items") or []),
        "attempts_max": max([len(v) for v in (aligned.get("item_log") or {}).values()] or [0]),
        "status": aligned["status"], "cost_jpy": aligned.get("cost_jpy"), "elapsed_sec": _t_align}
    with open(f"{out_dir}/keywords_canonicalized.json", "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    result["merged"] = merged
    return result


def run_key_phrase_redundancy_qa(article_text: str, merged_items: list, out_dir: str, article_id: str,
                                  process: str = None) -> dict:
    """ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01: canonicalization後の5件を
    対象に、意味・使用場面・文法/構文上の学習価値・記事内で担う概念の
    4観点で相互重複を判定する(processの意味は他のKey Phrase関数と同じ)。"""
    if len(merged_items) < 2:
        # KPFT 委任_02: 全文選定でKPが1件(shortfall)のとき、比較するペアが無いのでQAを呼ばない(API 0)。記録は残す。
        result = {"article_id": article_id, "redundancy_qa_version": redundancy_qa.REDUNDANCY_QA_VERSION,
                  "status": "REDUNDANCY_PASS", "model_id": None, "response_id": None, "duplicate_pairs": [],
                  "attempts_detail": [], "skipped": "ペアが無い(KP件数が2未満)"}
        with open(f"{out_dir}/keyphrase_redundancy_qa.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        return result
    user_message = redundancy_qa.build_user_message(merged_items, article_text)
    with open(f"{out_dir}/keyphrase_redundancy_qa_prompt.txt", "w", encoding="utf-8") as f:
        f.write(user_message)
    _dev_msg = redundancy_qa.developer_message_for(len(merged_items))   # 件数語を実件数に(5件ではバイト同一)

    def make_factory():
        model = routing.require_model(process, routing.SUPPORT_MODEL) if process else routing.SUPPORT_MODEL
        return redundancy_qa.make_redundancy_qa_fn(user_message, model=model, developer_message=_dev_msg)

    ranks = [it["rank"] for it in merged_items]
    parsed, status, attempts, model_id, response_id = redundancy_qa.run_redundancy_qa_gate(make_factory, ranks)
    duplicate_pairs = attempts[-1].get("duplicate_pairs", []) if attempts else []
    result = {
        "article_id": article_id, "redundancy_qa_version": redundancy_qa.REDUNDANCY_QA_VERSION,
        "status": status, "model_id": model_id, "response_id": response_id,
        "duplicate_pairs": duplicate_pairs,
        "attempts_detail": [{k: v for k, v in a.items() if k != "raw_text"} for a in attempts],
    }
    with open(f"{out_dir}/keyphrase_redundancy_qa.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result


# ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01: 5件相互の意味重複がNGだった
# 場合、Key Phrase選定(方式L)からやり直す。記事本文は変更しないため、
# Point Overlap QAの記事全体retryとは異なり、選定+canonicalization+
# redundancy QAの3工程のみを再実行すれば足りる。上限はPoint Overlap
# retry(POINT_OVERLAP_ARTICLE_RETRY_MAX=2)と同じ値をそのまま踏襲する
# (新しい独自の上限を発明しない)。
KEY_PHRASE_REDUNDANCY_RETRY_MAX = gen.POINT_OVERLAP_ARTICLE_RETRY_MAX


def detect_key_phrase_symbol_findings(merged_items: list) -> list:
    """TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01(Layer 2、
    2026-09-27): canonicalization後のKey Phrase 5件(used_form英語・
    japanese_gloss_tts)に音声化禁止記号が残っていないかを検出する
    (〜/～は`convert_display_gloss_to_tts_text`が既に全位置変換するため
    ここでは主に括弧・スラッシュ・URL/email・絵文字・残存placeholderを
    捕捉する)。戻り値の各findingにrank/fieldを付与する(既存
    classify_foreign_tokens_in_japanese_text等と同じ「findings配列」
    パターン)。"""
    findings = []
    for it in merged_items:
        for f in safety.detect_prohibited_symbols(it.get("used_form") or "", language="en"):
            findings.append({**f, "rank": it["rank"], "field": "used_form"})
        for f in safety.detect_prohibited_symbols(it.get("japanese_gloss_tts") or "", language="ja"):
            findings.append({**f, "rank": it["rank"], "field": "japanese_gloss_tts"})
    return findings


# ============================================================
# KPFT 委任_02(OF-KPFT-P-07/P-08): X/Z共通の外側retry(全文選定backend用)。
# 旧: Z限定・暫定(`er062.run_kp_with_outer_retry`、OPEN-310回避)。Xには無く、canonicalization INVALIDで旧attemptのKPが残った
# (KPMP B1)。全文選定+最小化圧力でINVALID頻度が上がるため、X/Zで同じ関数を共有する(er062は薄いdelegateに変更)。
# 構造(P-08): カウンタを入れ子にしない。1つのwhileループで次の2つを別々に数える。
#   failures      = 選定の失敗(INVALID/PARSE_FAILED/TECHNICAL_FAILED)+ canonicalization INVALID(通算max_outer回まで。P-07: 選定INVALIDも予算に含む)
#   red_attempt   = Redundancy NG/記号NGによる選定やり直し(KEY_PHRASE_REDUNDANCY_RETRY_MAX回まで)
# 最大周回 = max_outer + KEY_PHRASE_REDUNDANCY_RETRY_MAX(=5)。各周の開始時にSTOPセンチネルを確認する(stop_check_fn)。
# 最終失敗時は直近attemptが書いたkeywords_canonicalized.jsonを`keywords_canonicalized.STALE_attempt{n}.json`へ改名し、
# 後段が旧KPを読めないようにする(KPMP B1の恒久修正)。
# ============================================================
KP_OUTER_RETRY_MAX = 3   # 旧Z_KP_OUTER_RETRY_MAX(=3)と同値
KP_STALE_PREFIX = "keywords_canonicalized.STALE_attempt"


def _kp_sha(s: str) -> str:
    import hashlib
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def _kp_copy_attempt_artifacts(kp_dir: str, attempt: int) -> str:
    dst = f"{kp_dir}/outer_retry/attempt_{attempt}"
    os.makedirs(dst, exist_ok=True)
    for name in os.listdir(kp_dir):
        src_p = f"{kp_dir}/{name}"
        if os.path.isfile(src_p):
            shutil.copyfile(src_p, f"{dst}/{name}")
    return dst


def _kp_canon_reasons(kp_dir: str):
    p = f"{kp_dir}/canonicalization_runtime_metadata.json"
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    return [{k: v for k, v in a.items() if k != "raw_text"} for a in d.get("attempts_detail", [])]


def _kp_retire_stale_artifact(kp_dir: str, attempt: int):
    """最終失敗時: 本名のkeywords_canonicalized.jsonを退避名へ改名(後段が旧attemptのKPを読めないようにする)。"""
    p = f"{kp_dir}/keywords_canonicalized.json"
    if os.path.exists(p):
        stale = f"{kp_dir}/{KP_STALE_PREFIX}{attempt}.json"
        os.replace(p, stale)
        return stale
    return None


def make_stop_check(run_dir: str = None):
    """STOPセンチネル(<run>/STOP, STOP_ALL)確認。あれば例外(新規API呼出なし)。er062_family_z_structure_01の既存実装を遅延importで再利用。"""
    def check(where: str):
        import er062_family_z_structure_01 as _st
        _st.check_stop_sentinel(where, run_dir)
    return check


def _kp_accepts_kwarg(fn, name: str) -> bool:
    import inspect
    try:
        params = inspect.signature(fn).parameters
    except (TypeError, ValueError):
        return False
    return name in params or any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values())


def _kp_invalid_item_reasons(canon: dict, entry: dict):
    """canonicalization INVALIDの項目別理由 -> [(rank, index, [reasons])]。最終attemptの診断を使う(無ければ空=除外しない)。"""
    attempts = entry.get("canonicalization_attempts") or []
    if not attempts:
        return []
    last = attempts[-1]
    return [(ir.get("rank"), ir.get("index"), list(ir.get("reasons") or [])) for ir in (last.get("item_reasons") or [])]


def _kp_review_required_reasons(entry: dict):
    """canonicalization REVIEW_REQUIRED(QA FAILあり)の項目別理由 -> [(rank, None, [reasons])]。最終attemptのitems_requiring_reviewと
    そのparsed itemのFAILフィールドから作る(診断が無ければ空=除外しない)。再選定時の除外語の理由文に使う。"""
    attempts = entry.get("canonicalization_attempts") or []
    if not attempts:
        return []
    last = attempts[-1]
    parsed_items = {it.get("rank"): it for it in ((last.get("parsed") or {}).get("items") or []) if isinstance(it, dict)}
    out = []
    for rank in (last.get("items_requiring_review") or []):
        it = parsed_items.get(rank) or {}
        fails = [k for k, v in it.items() if k.startswith("qa_") and v == "FAIL"]
        reason = "canonicalization QAでFAIL(学習単位として不適切の疑い)" + (": " + ", ".join(fails) if fails else "")
        out.append((rank, None, [reason]))
    return out


def _kp_add_exclusions(excluded: list, original_items: list, bad: list, outer: int, source: str) -> None:
    """KP-OUTER-RETRY-SAME-PHRASE-FIX: INVALID確定した選定句(display_phrase=選定時の本文表層形)を、理由付きで累積除外リストへ追加する(重複は理由を併合)。"""
    import er105_kp_fulltext_selector_01 as ft
    for rank, index, reasons in bad:
        it = next((x for x in original_items if rank is not None and x.get("rank") == rank), None)
        if it is None and index is not None and 0 <= index < len(original_items):
            it = original_items[index]
        if not it or not it.get("display_phrase"):
            continue
        key = ft.phrase_key(it["display_phrase"])
        ex = next((e for e in excluded if ft.phrase_key(e["phrase"]) == key), None)
        if ex is None:
            excluded.append({"phrase": it["display_phrase"], "reasons": list(reasons), "outer_attempt": outer, "source": source})
        else:
            ex["reasons"] = list(dict.fromkeys(ex["reasons"] + list(reasons)))


def run_kp_with_outer_retry(text: str, kp_dir: str, article_id: str, source_level: str, process=None, *,
                            max_outer: int = KP_OUTER_RETRY_MAX, generic_note: str = "",
                            select_fn=None, canon_fn=None, redundancy_fn=None, stop_check_fn=None,
                            scope_note: str = "KP外側retry(全文選定backend、X/Z共通)", **_):
    select_fn = select_fn or functools.partial(run_key_phrase_selection, kp_backend=FULLTEXT_BACKEND_ID)
    canon_fn = canon_fn or run_key_phrase_canonicalization
    redundancy_fn = redundancy_fn or run_key_phrase_redundancy_qa
    os.makedirs(kp_dir, exist_ok=True)
    import er105_kp_fulltext_selector_01 as ft_sel
    red_max = KEY_PHRASE_REDUNDANCY_RETRY_MAX
    red_note, red_attempt, failures, log, redundancy_retry_log = None, 0, 0, [], []
    outer = 0
    excluded = []   # KP-OUTER-RETRY-SAME-PHRASE-FIX(OPEN-456 F1): 前周までにINVALID確定した選定句[{"phrase","reasons","outer_attempt","source"}]。累積して次周の選定へ渡す
    cmu_note = ""   # KP-QUALITY-2ITEMS M2(OF-KPQ-P-02): canonicalization後のCMU未登録診断。NGのたびに作り直し、次周の選定noteへ確実に渡す
    import er108_kp_cmu_lexicon_gate_01 as cmu

    def save_log():
        with open(f"{kp_dir}/outer_retry_log.json", "w", encoding="utf-8") as f:
            json.dump({"scope": scope_note, "max_outer": max_outer, "generic_note": generic_note, "attempts": log,
                       "excluded_phrases": excluded},
                      f, ensure_ascii=False, indent=2)

    def fail(entry, sel, canon, status):
        """最終失敗: 旧attemptのKPを残さない。"""
        stale = _kp_retire_stale_artifact(kp_dir, outer)
        if stale:
            entry["stale_artifact"] = stale
        save_log()
        res = {"selection": sel, "canonicalization": canon, "redundancy_qa": None,
               "redundancy_retry_log": redundancy_retry_log, "outer_retry_log": log}
        if status:
            res["status"] = status
        return res

    while True:
        outer += 1
        if stop_check_fn is not None:
            stop_check_fn(f"kp_outer_retry:{article_id}:attempt{outer}")   # OF-KPFT-P-08: 各周の開始時(新規API呼出の前)
        note = (generic_note or "") + (("\n\n" if generic_note else "") + red_note if red_note else "")
        if cmu_note:
            note = note + ("\n\n" if note else "") + cmu_note
        if excluded:
            note = note + ("\n\n" if note else "") + ft_sel.build_exclusion_note(excluded)
        sel_kwargs = {}
        if excluded and _kp_accepts_kwarg(select_fn, "excluded_phrases"):
            sel_kwargs["excluded_phrases"] = [dict(e) for e in excluded]
        sel = select_fn(text, kp_dir, article_id, source_level, process=process, diagnostic_note=(note or None), **sel_kwargs)
        entry = {"outer_attempt": outer, "note_sha256": _kp_sha(note), "selection_status": sel.get("status"),
                 "selection_phrases": [it.get("display_phrase") for it in ((sel.get("parsed") or {}).get("items") or [])],
                 "excluded_phrases_in": [e["phrase"] for e in excluded]}
        # F1: select_fnがgate(er105)を通らない/除外を受け取れない場合の保険。除外句が再び返ったら、canonicalization(Luna)呼出前に不適合とする。
        if sel.get("status") == "KEY_WORDS_STRUCTURE_PASS" and excluded:
            ex_keys = {ft_sel.phrase_key(e["phrase"]) for e in excluded}
            again = [it.get("display_phrase") for it in (sel.get("original_items") or []) if ft_sel.phrase_key(it.get("display_phrase")) in ex_keys]
            if again:
                entry["excluded_phrase_reselected"] = again
                sel = dict(sel, status="KEY_WORDS_STRUCTURE_INVALID")
        if sel.get("status") != "KEY_WORDS_STRUCTURE_PASS":
            failures += 1
            entry["artifacts"] = _kp_copy_attempt_artifacts(kp_dir, outer)
            log.append(entry)
            if failures >= max_outer:
                return fail(entry, sel, None, "OUTER_RETRY_EXHAUSTED")
            save_log()
            continue
        canon = canon_fn(text, sel["original_items"], kp_dir, article_id, process=process)
        entry["canonicalization_status"] = canon.get("status")
        entry["canonicalization_attempts"] = _kp_canon_reasons(kp_dir)
        # KP-CANON-REVIEW-REQUIRED-FIX-01(OPEN-504、2026-10-25): 承認済み3状態モデル(CURRENT_SPEC「REVIEW_REQUIREDは自動採用しない・
        # 人間確認後に採用可」、er003_key_words_canonicalization.validate_canonicalization_response)への整合是正。採用はPASSのみ。
        # REVIEW_REQUIRED(構造OK・QA FAILあり)もINVALID同様に除外語付き再選定(通算max_outer内)の対象とし、上限到達後は
        # OUTER_RETRY_EXHAUSTEDで停止する(X/Z runnerの既存HR停止へ)。旧attemptのKP(canonicalizationが書いた本名ファイル)は退避する。
        if canon.get("status") != "CANONICALIZATION_PASS":
            failures += 1
            if canon.get("status") == "CANONICALIZATION_REVIEW_REQUIRED":
                bad = _kp_review_required_reasons(entry)
                entry["review_required_ranks"] = [b[0] for b in bad]
                entry["artifacts"] = _kp_copy_attempt_artifacts(kp_dir, outer)   # 退避前の本名ファイルも証跡へ残す
                stale = _kp_retire_stale_artifact(kp_dir, outer)
                if stale:
                    entry["stale_artifact"] = stale
                _kp_add_exclusions(excluded, sel.get("original_items") or [], bad, outer, "canonicalization_review_required")
            else:
                _kp_add_exclusions(excluded, sel.get("original_items") or [], _kp_invalid_item_reasons(canon, entry), outer, "canonicalization_invalid")
                entry["artifacts"] = _kp_copy_attempt_artifacts(kp_dir, outer)
            entry["excluded_phrases_added"] = [e["phrase"] for e in excluded if e["outer_attempt"] == outer]
            log.append(entry)
            if failures >= max_outer:
                return fail(entry, sel, canon, "OUTER_RETRY_EXHAUSTED")
            save_log()
            continue
        merged_items = canon["merged"]["items"]
        # KP-QUALITY-2ITEMS M2: canonicalization(基本形化・人称一般化)後の最終used_formをCMUで再確認。不適合=INVALID扱い(外側retry通算内)。
        # OF-KPQ-P-02: NGになった時点で`keywords_canonicalized.json`を即座に退避(本名のまま残さない=TTS段/resumeが読まない)し、次周のnoteへCMU診断を渡す。
        chk = cmu.canonicalized_check(merged_items)
        entry["cmu_post_canon"] = {"version": chk["version"], "ok": chk["ok"], "checked": chk["checked"], "bad": chk["bad"]}
        if not chk["ok"]:
            failures += 1
            entry["artifacts"] = _kp_copy_attempt_artifacts(kp_dir, outer)
            stale = _kp_retire_stale_artifact(kp_dir, outer)
            if stale:
                entry["stale_artifact"] = stale
            cmu_note = cmu.build_canonicalized_note(chk)
            _kp_add_exclusions(excluded, sel.get("original_items") or [],
                               [(b.get("rank"), None, ["基本形化・一般化後「%s」にCMU未登録語 %s" % (b.get("used_form"), ", ".join(b.get("unregistered") or []))]) for b in chk["bad"]],
                               outer, "cmu_post_canon")
            entry["excluded_phrases_added"] = [e["phrase"] for e in excluded if e["outer_attempt"] == outer]
            entry["canonicalization_status"] = "CMU_POST_CANON_INVALID"
            log.append(entry)
            if failures >= max_outer:
                return fail(entry, sel, canon, "OUTER_RETRY_EXHAUSTED")
            save_log()
            continue
        cmu_note = ""
        red = redundancy_fn(text, merged_items, kp_dir, article_id, process=process)
        findings = detect_key_phrase_symbol_findings(merged_items)
        flagged = safety.symbol_gate_requires_stop(findings)
        redundancy_retry_log.append({"attempt": red_attempt, "status": red.get("status"),
                                     "duplicate_pairs": red.get("duplicate_pairs"), "symbol_flagged": flagged,
                                     "symbol_findings": findings})
        entry.update({"redundancy_status": red.get("status"), "symbol_flagged": flagged,
                      "artifacts": _kp_copy_attempt_artifacts(kp_dir, outer)})
        log.append(entry)
        if red.get("status") != "REDUNDANCY_NG" and not flagged:
            save_log()
            return {"selection": sel, "canonicalization": canon, "redundancy_qa": red,
                    "redundancy_retry_log": redundancy_retry_log, "redundancy_retry_attempts": red_attempt,
                    "outer_retry_log": log}
        if red_attempt >= red_max:
            stale = _kp_retire_stale_artifact(kp_dir, outer)
            if stale:
                entry["stale_artifact"] = stale
            save_log()
            return {"selection": sel, "canonicalization": canon, "redundancy_qa": red,
                    "redundancy_retry_log": redundancy_retry_log, "redundancy_retry_attempts": red_attempt,
                    "outer_retry_log": log, "status": "NG_REVIEW_REQUIRED"}
        save_log()
        by_rank = {it["rank"]: it for it in merged_items}
        red_note = ""
        if red.get("status") == "REDUNDANCY_NG":
            red_note += redundancy_qa.build_redundancy_diagnostic_note(red["duplicate_pairs"], by_rank)
        if flagged:
            red_note += ("\n\n" if red_note else "") + safety.build_symbol_violation_prompt_note(findings)
        red_attempt += 1


def run_key_phrases(article_text: str, out_dir: str, article_id: str, source_level: str,
                     process: str = None, synthetic: bool = False,
                     kp_backend: str = "strategy_l", stop_run_dir: str = None) -> dict:
    """Key Phrase stage(選定→canonicalization→Redundancy QA)。kp_backend=fulltext_p2(X/Z)は共通の外側retry、
    それ以外(strategy_l=A/B/C)は従来の`_run_key_phrases_impl`。最後に最終artifactへgloss HR報告を1回行う。
    (旧: M2->Strategy L Fallback eventのM2 fallback event一覧の戻り値追記はdb_hybrid撤去に伴い廃止[KPFT 委任_02])"""
    # OF-229: gloss規則の抽出失敗は記事内容に依存しない設定不備なので、run開始時(最初の記事のAPI呼出前)に即時停止する。
    gloss_align.preflight()
    if kp_backend == FULLTEXT_BACKEND_ID:
        # KPFT 委任_02: 全文選定backendはX/Z共通の外側retry(選定失敗/canonicalization INVALIDの通算3回+Redundancy NGの選定やり直し)。
        result = run_kp_with_outer_retry(
            article_text, out_dir, article_id, source_level, process=process,
            select_fn=functools.partial(run_key_phrase_selection, kp_backend=FULLTEXT_BACKEND_ID, synthetic=synthetic),
            stop_check_fn=make_stop_check(stop_run_dir))
    else:
        result = _run_key_phrases_impl(article_text, out_dir, article_id, source_level, process=process,
                                       synthetic=synthetic, kp_backend=kp_backend)
    # 委任_02(OF-KGDC-04 / OF-KGCPW-03): HR報告は外側retry確定後に、**ディスク上の最終artifact**(消費側が読むものと同一の
    # keywords_canonicalized.json)に対して1回だけ行う。途中attemptでHR→次attemptで失敗(canonicalization=None)でも、
    # ディスク上のHR itemを見落とさず報告書・event・stdoutを出す。artifactが無ければ報告なし。
    # 書込/再読検証の失敗は例外(fail-closed)=当該stageを止める。queue/Lockは使わない。
    events = []
    kp_path = os.path.join(out_dir, "keywords_canonicalized.json")
    disk_doc = None
    if os.path.exists(kp_path):
        with open(kp_path, encoding="utf-8") as f:
            disk_doc = json.load(f)
    if disk_doc is not None:
        ev = gloss_align.emit_human_review_notice(out_dir, article_id, source_level, disk_doc)
        if ev is not None:
            events.append(ev)
    result["gloss_alignment_human_review_events"] = events
    result["gloss_alignment_run_status"] = gloss_align.STOPPED_STATUS if events else None   # OF-KGCPW-04: 既存statusと別キー
    if events and "status" not in result:
        result["status"] = gloss_align.STOPPED_STATUS   # 非OK(run summaryのstatus)。下流停止は消費側(X関所/Z stage_kp)
    return result


def _run_key_phrases_impl(article_text: str, out_dir: str, article_id: str, source_level: str,
                     process: str = None, synthetic: bool = False,
                     kp_backend: str = "strategy_l") -> dict:
    """processの意味はrun_key_phrase_selection()と同じ(ER-006-MODEL-ROUTING-
    CONTRACT-01追補、"B1_SUPPORT"/"A2_SUPPORT"を渡す)。

    ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01: canonicalization成功後、
    5件相互の意味重複QA(Key Phrase Set Redundancy QA)を実行する。NGの
    場合は選定からやり直す(最大KEY_PHRASE_REDUNDANCY_RETRY_MAX回)。
    上限まで再試行してもNGが残る場合は、既存のKey Phrase QAの人間確認
    運用(REVIEW_REQUIRED = 自動不採用・人間確認後に採用可)にならい、
    本文は変更せず"NG_REVIEW_REQUIRED"として報告する(黙示的な自動採用は
    しない)。

    kp_backend: 意味はrun_key_phrase_selection()と同じ(retryでも同じkp_backendを一貫して使う。既定"strategy_l"は
    全既存呼び出し元[A/B/C等]で無変更)。X/Z(fulltext_p2)は`run_key_phrases`が共通の外側retryへ振り分けるため本関数を通らない。"""
    redundancy_retry_log = []
    diagnostic_note = None
    for attempt in range(0, KEY_PHRASE_REDUNDANCY_RETRY_MAX + 1):
        sel = run_key_phrase_selection(article_text, out_dir, article_id, source_level, process=process,
                                        diagnostic_note=diagnostic_note, kp_backend=kp_backend,
                                        synthetic=synthetic)
        if sel["status"] != "KEY_WORDS_STRUCTURE_PASS":
            return {"selection": sel, "canonicalization": None, "redundancy_qa": None,
                     "redundancy_retry_log": redundancy_retry_log}
        canon = run_key_phrase_canonicalization(article_text, sel["original_items"], out_dir, article_id,
                                                  process=process)
        if canon["status"] not in ("CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
            return {"selection": sel, "canonicalization": canon, "redundancy_qa": None,
                     "redundancy_retry_log": redundancy_retry_log}

        merged_items = canon["merged"]["items"]
        redundancy = run_key_phrase_redundancy_qa(article_text, merged_items, out_dir, article_id, process=process)
        redundancy_retry_log.append({"attempt": attempt, "status": redundancy["status"],
                                      "duplicate_pairs": redundancy["duplicate_pairs"]})

        # TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01(Layer 2、
        # 2026-09-27): Redundancy QAとは独立に、音声化禁止記号を検出する。
        # 既存のRedundancy QA NG retryと同じループ(選定からやり直す、上限
        # KEY_PHRASE_REDUNDANCY_RETRY_MAXを共有)へ接続する(新しいRetry
        # 上限は作らない)。
        symbol_findings = detect_key_phrase_symbol_findings(merged_items)
        symbol_flagged = safety.symbol_gate_requires_stop(symbol_findings)
        redundancy_retry_log[-1]["symbol_flagged"] = symbol_flagged
        redundancy_retry_log[-1]["symbol_findings"] = symbol_findings

        if redundancy["status"] != "REDUNDANCY_NG" and not symbol_flagged:
            return {"selection": sel, "canonicalization": canon, "redundancy_qa": redundancy,
                     "redundancy_retry_log": redundancy_retry_log, "redundancy_retry_attempts": attempt}

        if attempt >= KEY_PHRASE_REDUNDANCY_RETRY_MAX:
            return {"selection": sel, "canonicalization": canon, "redundancy_qa": redundancy,
                     "redundancy_retry_log": redundancy_retry_log, "redundancy_retry_attempts": attempt,
                     "status": "NG_REVIEW_REQUIRED"}

        items_by_rank = {it["rank"]: it for it in merged_items}
        diagnostic_note = ""
        if redundancy["status"] == "REDUNDANCY_NG":
            diagnostic_note += redundancy_qa.build_redundancy_diagnostic_note(
                redundancy["duplicate_pairs"], items_by_rank)
        if symbol_flagged:
            diagnostic_note += ("\n\n" if diagnostic_note else "") + safety.build_symbol_violation_prompt_note(
                symbol_findings)
        print(f"[N3-01][{article_id}] Key Phrase Set Redundancy/Symbol QA NG "
              f"(重複ペア: {redundancy['duplicate_pairs']}, symbol_flagged={symbol_flagged})。"
              f"選定からやり直します(retry {attempt + 1}/{KEY_PHRASE_REDUNDANCY_RETRY_MAX})...")

    # ループはreturnで抜けるため、ここへは到達しない想定
    raise RuntimeError("run_key_phrases: 予期しないループ終了")


# ============================================================
# B1 Scaffold(English Preview/Comment1-4)
# ============================================================
_BLUEPRINT_COMMENT_SELF_REPORT_SUFFIX = (
    "\n\n【重要・追加指示(Shared Point Blueprint)】このCommentは、A2/B1双方で共用される"
    "可能性があります。上記のcomment_anchorの範囲だけを参照し、それ以外のFact"
    "(まだ聞いていないPointの内容、B1限定の詳細情報)には触れないでください。"
    "Comment本文を書き終えたら、最後に、実際に参照したfact_idを以下の形式のfenced "
    "code blockで1つだけ追加してください(音声化されないメタデータです。無ければ"
    "空配列でかまいません)。\n```json\n{\"referenced_fact_ids\": [\"FACT-xxx\", ...]}\n```"
)


def run_b1_scaffold(client, parts: dict, out_dir: str, article_text: str, blueprint=None) -> dict:
    """blueprint(er008_shared_point_blueprint_01.SharedPointBlueprint、
    A2/B1 Point Structure Semantic Alignmentタスクで追加)を渡すと、
    Comment 3・4(Point構造を参照するComment)のcontextがBlueprintの
    comment_anchorへ差し替えられ、fact_id自己申告(末尾fenced JSON block)
    を要求する。Comment 1・2・PreviewはFull Story本文のみに依存する
    ためBlueprintの対象外のまま変更しない(ER-008監査でもComment 1〜3の
    大半は互換性ありと確認済み)。Noneの場合(既定)は旧来の挙動と完全に
    同一(後方互換)。"""
    print(f"[N3-SCAFFOLD] B1 Comment 1生成開始({out_dir})...")
    c1_context = f"【これから聞く本文(前半)】\n{parts['part1']}"
    c1 = b1s.run_support_text(client, b1s.COMMENT_1_ROLE, c1_context, model=_b1_support_model())

    print(f"[N3-SCAFFOLD] B1 Comment 2生成開始({out_dir})...")
    c2_context = f"【すでに聞いた本文(前半)】\n{parts['part1']}\n\n【これから聞く本文(後半)】\n{parts['part2']}"
    c2 = b1s.run_support_text(client, b1s.COMMENT_2_ROLE, c2_context, model=_b1_support_model())

    print(f"[N3-SCAFFOLD] B1 Comment 3生成開始({out_dir})...")
    if blueprint is not None:
        c3_context = (f"【本文(前半)】\n{parts['part1']}\n\n【本文(後半)】\n{parts['part2']}\n\n"
                      f"【これから聞くPointの見出しのみ(内容は伏せる)】\n"
                      f"Point One heading: {parts['point_one_heading']}\nPoint Two heading: {parts['point_two_heading']}\n\n"
                      f"{blueprint_mod.render_comment_anchor_block(blueprint, 'point_1')}")
        c3_role = b1s.COMMENT_3_ROLE + _BLUEPRINT_COMMENT_SELF_REPORT_SUFFIX
    else:
        c3_context = (f"【本文(前半)】\n{parts['part1']}\n\n【本文(後半)】\n{parts['part2']}\n\n"
                      f"【これから聞くPointの見出しのみ(内容は伏せる)】\n"
                      f"Point One heading: {parts['point_one_heading']}\nPoint Two heading: {parts['point_two_heading']}")
        c3_role = b1s.COMMENT_3_ROLE
    c3 = b1s.run_support_text(client, c3_role, c3_context, model=_b1_support_model())
    c3_clean_text, c3_fact_refs = blueprint_mod.extract_trailing_metadata_block(c3.get("text") or "")
    if c3.get("text") is not None:
        c3["text"] = c3_clean_text
    if c3_fact_refs is not None:
        c3["referenced_fact_ids"] = c3_fact_refs.get("referenced_fact_ids")

    print(f"[N3-SCAFFOLD] B1 Comment 4生成開始({out_dir})...")
    if blueprint is not None:
        c4_context = (f"【Point One(聞き終えた内容)】\n{parts['point_one_heading']}\n{parts['point_one_body']}\n\n"
                      f"【Point Two(聞き終えた内容)】\n{parts['point_two_heading']}\n{parts['point_two_body']}\n\n"
                      f"{blueprint_mod.render_comment_anchor_block(blueprint, 'point_2')}")
        c4_role = b1s.COMMENT_4_ROLE + _BLUEPRINT_COMMENT_SELF_REPORT_SUFFIX
    else:
        c4_context = (f"【Point One(聞き終えた内容)】\n{parts['point_one_heading']}\n{parts['point_one_body']}\n\n"
                      f"【Point Two(聞き終えた内容)】\n{parts['point_two_heading']}\n{parts['point_two_body']}")
        c4_role = b1s.COMMENT_4_ROLE
    c4 = b1s.run_support_text(client, c4_role, c4_context, model=_b1_support_model())
    c4_clean_text, c4_fact_refs = blueprint_mod.extract_trailing_metadata_block(c4.get("text") or "")
    if c4.get("text") is not None:
        c4["text"] = c4_clean_text
    if c4_fact_refs is not None:
        c4["referenced_fact_ids"] = c4_fact_refs.get("referenced_fact_ids")

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
    c1_context = f"【これから聞く本文(前半、英語)】\n{parts['part1']}"
    c1 = a2gen.run_support_text(client, a2gen.COMMENT_1_ROLE, c1_context, model=_a2_support_model())

    print(f"[N3-SCAFFOLD] A2 Comment 2生成開始({out_dir})...")
    c2_context = f"【すでに聞いた本文(前半)】\n{parts['part1']}\n\n【これから聞く本文(後半)】\n{parts['part2']}"
    c2 = a2gen.run_support_text(client, a2gen.COMMENT_2_ROLE, c2_context, model=_a2_support_model())

    print(f"[N3-SCAFFOLD] A2 Comment 3生成開始({out_dir})...")
    c3_role = A2_COMMENT_3_ROLE_N3.format(
        point_one_heading=parts["point_one_heading"], point_two_heading=parts["point_two_heading"])
    c3_context = f"【本文(前半)】\n{parts['part1']}\n\n【本文(後半)】\n{parts['part2']}"
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
