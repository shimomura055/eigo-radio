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
import time

import er003_audio_tts_asr_safety as safety
import er003_b1_p2_keywords as bk
import er003_key_words_canonicalization as kc
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
                              shortlist_cache: dict = None) -> dict:
    """process(ER-006-MODEL-ROUTING-CONTRACT-01追補): "B1_SUPPORT"/"A2_SUPPORT"を
    渡すと、routing.require_model()で検証済みのApproved ModelをAPI call直前に
    このスコープ内で確定させる(呼び出し元でmodelを事前計算させない)。Noneの
    場合はbk.make_selector_fnの既定値(Sol系譜)のまま、後方互換を保つ。

    diagnostic_note(ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01追加): 前回の
    選定でKey Phrase Set Redundancy QA(er011_key_phrase_set_redundancy_qa_01.py)
    がNGと判定した場合、その診断情報をprompt末尾へ追加して再選定させる
    (記事固有のハードコードではなく、直前の判定結果をそのまま渡すだけ)。

    kp_backend(KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01追加、
    2026-09-27): 既定`"strategy_l"`は本関数の従来どおりの挙動(本文全文を
    prompt送信するStrategy L方式、以下の関数本体)を変更しない。
    `"db_hybrid"`を渡すと、Family X通常記事向けにユーザーが正式採用した
    DB Hybrid方式(Primary、`er030_key_phrase_db_hybrid_selector_01`)を
    試み、失敗した場合のみこの関数の既存挙動(Strategy L全文方式、
    Fallback)へ自動的に切り替える(失敗理由は
    `er030_output/kp_backend_telemetry_01/telemetry.jsonl`へ記録する)。
    既定値を変更していないため、Family X以外の全既存呼び出し元
    (Family A/B/C/News/Z等)は無変更のまま影響を受けない。

    修正1回目(Opus L2所見B1/S8、2026-09-27): 呼び出し経路によらず
    (`kp_backend`の値にかかわらず)常に1回`_log_kp_backend_telemetry()`を
    記録する(既定"strategy_l"経路が無記録だった観測性の欠落を解消)。
    `synthetic`(既定False)は、evidence/testスクリプトが強制failure注入
    等でこの呼び出しを発生させた場合にTrueを渡す(本番実行との区別)。
    `shortlist_cache`はdb_hybrid経路のみで使う(S8、Redundancy QA retry
    時のStage1再計算を避ける、Strategy L経路では無視される)。"""
    if kp_backend == "db_hybrid":
        return _run_key_phrase_selection_db_hybrid_with_fallback(
            article_text, out_dir, article_id, source_level, process=process,
            diagnostic_note=diagnostic_note, synthetic=synthetic, shortlist_cache=shortlist_cache)
    result = _run_key_phrase_selection_strategy_l(
        article_text, out_dir, article_id, source_level, process=process,
        diagnostic_note=diagnostic_note)
    result["kp_backend_used"] = "strategy_l"
    _log_kp_backend_telemetry(
        article_id, source_level, requested_backend="strategy_l", backend_used="strategy_l",
        final_status=result.get("status"), fallback_triggered=False,
        model_id=result.get("model_id"), cost_jpy=None, synthetic=synthetic,
        source_reference_contract=FREE_TEXT_SOURCE_REFERENCE_CONTRACT_ID)
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

    result = {"status": status, "parsed": parsed, "model_id": model_id}
    if status != "KEY_WORDS_STRUCTURE_PASS":
        return result
    result["original_items"] = parsed["items"]
    return result


KP_BACKEND_TELEMETRY_PATH = os.path.join("er030_output", "kp_backend_telemetry_01", "telemetry.jsonl")

# 修正1回目(Opus L2所見B1、2026-09-27): telemetry各行にspec_idを付与し、
# 将来別specがtelemetry.jsonlを共有する場合でも起源を区別できるようにする。
KP_BACKEND_SPEC_ID = "KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01"

# KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01
# (2026-09-28新設): Fallback(Strategy L全文方式)は従来どおりLLMが
# source_sentence/source_spanを自由記述する契約のままである(候補ID
# 契約はDB Hybrid経路にのみ適用する)。telemetryへ両契約の混在を観測
# 可能にするためのタグ(db_hybrid成功時のタグは
# `er030_key_phrase_db_hybrid_source_reference_contract_01.
# SOURCE_REFERENCE_CONTRACT_ID`側で定義、ここでは循環import回避のため
# 文字列を直接複製する[両定数は意味的に対になる、値の変更時は両方を
# 揃えて更新する])。
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


def _merge_kp_backend_metadata_into_runtime_file(out_dir: str, extra: dict) -> None:
    """修正1回目(Opus L2所見B2、2026-09-27): {kp_dir}/keywords_runtime_
    metadata.json(per-article traceability、既存Strategy L/db_hybrid
    どちらも書き込む正式ファイル)へ、kp_backend関連のfield(kp_backend/
    kp_backend_used/fallback_reason_code/cost_jpy/model_id/attempt履歴等)
    を追記型(既存内容を保持したままdictをupdate)で記録する。db_hybrid
    成功時は新規作成、fallback時は既存Strategy L出力へ「db_hybridを
    試して失敗した事実」を追記する。"""
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "keywords_runtime_metadata.json")
    existing = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            existing = json.load(f)
    existing.update(extra)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)


def _run_key_phrase_selection_db_hybrid_with_fallback(
        article_text: str, out_dir: str, article_id: str, source_level: str,
        process: str = None, diagnostic_note: str = None, synthetic: bool = False,
        shortlist_cache: dict = None) -> dict:
    """KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01: Primary=DB
    Hybrid方式(`er030_key_phrase_db_hybrid_selector_01`)を試み、
    `DbHybridFailure`が送出された場合、`fallback_allowed`が真であれば
    Fallback=既存Strategy L全文方式(`_run_key_phrase_selection_
    strategy_l`、無変更)へ切り替える。`fallback_allowed`が偽(修正1回目、
    Opus L2所見B3: モデルルーティング契約違反等)の場合はfallbackせず
    そのまま再raiseしてSTOPする(fail-closed)。いずれの経路でも
    telemetry・per-article metadataへ記録する(fallbackの黙示的な通常
    経路化を防ぐ)。"""
    import er030_key_phrase_db_hybrid_selector_01 as db_hybrid

    try:
        result = db_hybrid.run_db_hybrid_selection(
            article_text, os.path.join(out_dir, "key_phrases_db_hybrid"), article_id, source_level,
            process=process, diagnostic_note=diagnostic_note, shortlist_cache=shortlist_cache)
    except db_hybrid.DbHybridFailure as e:
        if not e.fallback_allowed:
            _log_kp_backend_telemetry(
                article_id, source_level, requested_backend="db_hybrid", backend_used="db_hybrid",
                final_status="STOP", fallback_triggered=False, fallback_reason_code=e.reason_code,
                fallback_reason=str(e), synthetic=synthetic,
                source_reference_contract=db_hybrid.src_ref_contract.SOURCE_REFERENCE_CONTRACT_ID,
                **e.telemetry)
            _merge_kp_backend_metadata_into_runtime_file(out_dir, {
                "kp_backend": "db_hybrid", "kp_backend_used": None,
                "kp_backend_fallback_allowed": False, "kp_backend_stop_reason_code": e.reason_code,
                "kp_backend_stop_reason": str(e),
            })
            print(f"[KP-BACKEND][STOP] db_hybrid selectorがfallback不可の理由で失敗しました"
                  f"({e.reason_code}: {e})。安全のためfallbackせず処理を停止します({article_id})。")
            raise
        _log_kp_backend_telemetry(
            article_id, source_level, requested_backend="db_hybrid", backend_used="strategy_l_fallback",
            final_status="FALLBACK_TRIGGERED", fallback_triggered=True, fallback_reason_code=e.reason_code,
            fallback_reason=str(e), synthetic=synthetic,
            source_reference_contract=FREE_TEXT_SOURCE_REFERENCE_CONTRACT_ID, **e.telemetry)
        print(f"[KP-BACKEND] db_hybrid selectorが失敗しました({e.reason_code}: {e})。"
              f"Strategy L全文方式へfallbackします({article_id})。")
        result = _run_key_phrase_selection_strategy_l(
            article_text, out_dir, article_id, source_level, process=process,
            diagnostic_note=diagnostic_note)
        result["kp_backend_used"] = "strategy_l_fallback"
        result["kp_backend_fallback_reason_code"] = e.reason_code
        _merge_kp_backend_metadata_into_runtime_file(out_dir, {
            "kp_backend": "db_hybrid_attempted", "kp_backend_used": "strategy_l_fallback",
            "kp_backend_fallback_reason_code": e.reason_code, "kp_backend_fallback_reason": str(e),
            "kp_backend_attempted_telemetry": e.telemetry,
            "kp_backend_source_reference_contract": FREE_TEXT_SOURCE_REFERENCE_CONTRACT_ID,
        })
        return result

    _log_kp_backend_telemetry(
        article_id, source_level, requested_backend="db_hybrid", backend_used="db_hybrid",
        final_status=result.get("status"), fallback_triggered=False,
        cost_jpy=result.get("cost_jpy"), model_id=result.get("model_id"), synthetic=synthetic,
        shortlist_total_count=result.get("shortlist_total_count"),
        cost_guard_exceeded=result.get("cost_guard_exceeded"),
        source_reference_contract=result.get("source_reference_contract"),
        candidate_mismatch_suspected_count=result.get("candidate_mismatch_suspected_count"))
    result["kp_backend_used"] = "db_hybrid"
    _merge_kp_backend_metadata_into_runtime_file(out_dir, {
        "kp_backend": "db_hybrid", "kp_backend_used": "db_hybrid",
        "kp_backend_fallback_reason_code": None,
        "kp_backend_cost_jpy": result.get("cost_jpy"), "kp_backend_model_id": result.get("model_id"),
        "kp_backend_shortlist_total_count": result.get("shortlist_total_count"),
        "kp_backend_cost_guard_exceeded": result.get("cost_guard_exceeded"),
        "kp_backend_attempts_detail": result.get("attempts_detail"),
        "kp_backend_source_reference_contract": result.get("source_reference_contract"),
        "kp_backend_candidate_mismatch_suspected_count": result.get("candidate_mismatch_suspected_count"),
    })
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


def run_key_phrase_redundancy_qa(article_text: str, merged_items: list, out_dir: str, article_id: str,
                                  process: str = None) -> dict:
    """ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01: canonicalization後の5件を
    対象に、意味・使用場面・文法/構文上の学習価値・記事内で担う概念の
    4観点で相互重複を判定する(processの意味は他のKey Phrase関数と同じ)。"""
    user_message = redundancy_qa.build_user_message(merged_items, article_text)
    with open(f"{out_dir}/keyphrase_redundancy_qa_prompt.txt", "w", encoding="utf-8") as f:
        f.write(user_message)

    def make_factory():
        model = routing.require_model(process, routing.SUPPORT_MODEL) if process else routing.SUPPORT_MODEL
        return redundancy_qa.make_redundancy_qa_fn(user_message, model=model)

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


def run_key_phrases(article_text: str, out_dir: str, article_id: str, source_level: str,
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

    kp_backend(KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01追加):
    意味はrun_key_phrase_selection()と同じ。retry(選定からやり直す
    ループ)でも同じkp_backendが一貫して使われる(既定"strategy_l"は
    全既存呼び出し元で無変更)。

    修正1回目(Opus L2所見S4/S8、2026-09-27): (1)本関数スコープで
    article_id単位の累積コスト(db_hybrid選定+fallback選定の合算、
    canonicalization/Redundancy QA自体は既存Productionが元々cost計測
    していないため対象外[N5])を追跡し、`KP_ARTICLE_COST_CAP_JPY`
    (既定¥15.0、`er030_key_phrase_db_hybrid_selector_01`定数)を超えた
    場合はfallbackではなく`status="KP_ARTICLE_COST_CAP_EXCEEDED"`で
    STOPする(retryを続けない)。(2)`shortlist_cache`(本関数ローカル、
    article_textのsha256をkeyとするdict)をretryループ全体で共有し、
    db_hybrid経路のStage1/Wiktionary lookup再計算を防ぐ(retryは
    prompt[diagnostic_note]再生成のみ)。"""
    redundancy_retry_log = []
    diagnostic_note = None
    shortlist_cache: dict = {}
    cumulative_cost_jpy = 0.0
    for attempt in range(0, KEY_PHRASE_REDUNDANCY_RETRY_MAX + 1):
        sel = run_key_phrase_selection(article_text, out_dir, article_id, source_level, process=process,
                                        diagnostic_note=diagnostic_note, kp_backend=kp_backend,
                                        synthetic=synthetic, shortlist_cache=shortlist_cache)
        cumulative_cost_jpy += (sel.get("cost_jpy") or 0.0)
        if kp_backend == "db_hybrid":
            import er030_key_phrase_db_hybrid_selector_01 as _db_hybrid_mod
            if cumulative_cost_jpy > _db_hybrid_mod.KP_ARTICLE_COST_CAP_JPY:
                print(f"[KP-BACKEND][STOP] {article_id}: 記事単位の累積コスト"
                      f"(JPY {cumulative_cost_jpy:.4f})が上限(JPY "
                      f"{_db_hybrid_mod.KP_ARTICLE_COST_CAP_JPY})を超過しました。"
                      "fallbackせず処理を停止します。")
                return {"selection": sel, "canonicalization": None, "redundancy_qa": None,
                        "redundancy_retry_log": redundancy_retry_log,
                        "status": "KP_ARTICLE_COST_CAP_EXCEEDED",
                        "cumulative_cost_jpy": round(cumulative_cost_jpy, 4)}
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
