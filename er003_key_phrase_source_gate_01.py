# ============================================================
# er003_key_phrase_source_gate_01.py
# 管理ID: KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01(ユーザー正式決定
# 2026-09-18、OPEN-170採用)
# ============================================================
# 目的: 「本文平易化後にKey Phraseが古いまま残る」事故(Free-Address A2/
# AI Hiring A2、USER-TEST-SCRIPT-READABILITY-PROD-01で発見)の再発防止。
#
# Gate (a): Assembly直前に、`keywords_canonicalized.json`の各Key Phrase
#   項目の`source_span`(無ければ`source_sentence`)が、当該Assemblyが
#   使う「現行本文」に実在するかを機械確認する。1件でも不在ならFAIL。
# Gate (b): 他記事からKey Phraseを流用する経路(`reuse_key_phrases*`)で、
#   供給元本文と流用先本文のsha256一致を必須化する。不一致ならFAIL
#   (流用しない)。
#
# 費用: API呼び出しなし(ローカル文字列比較・sha256のみ)。
# 実装は本モジュールに集約し、呼び出し側(er003_v1_n3_01_assemble.py
# ::verify_episode_audio_validation_gate、各reuse_key_phrases*系関数)から
# 呼び出す設計とする(コピー実装を作らない)。
# ============================================================
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re

NORMALIZATION_RULES = [
    "lowercase",
    "html_entity_unescape",
    "apostrophe_variants_to_ascii",
    "dash_variants_to_hyphen",
    "collapse_whitespace",
]

_APOSTROPHE_VARIANTS = "‘’ʼ`´"
_DASH_VARIANTS = "‐‑‒–—―"

_APOSTROPHE_TRANSLATION = {ord(ch): "'" for ch in _APOSTROPHE_VARIANTS}
_DASH_TRANSLATION = {ord(ch): "-" for ch in _DASH_VARIANTS}


def normalize_text(text: str) -> str:
    """Gate (a)の本文照合専用の正規化(大小文字・apostrophe種・HTML
    entity・ダッシュ種・連続空白を吸収する)。Key Phrase Canonicalization
    (`er003_key_words_canonicalization.py`)のTraceability正規化とは別物
    (あちらは「意味的に説明可能な導出」を許容する緩い基準、こちらは
    「本文に実在するか」という機械的な部分文字列一致のための表記ゆれ
    吸収のみ)。"""
    if text is None:
        return ""
    t = html.unescape(text)
    t = t.translate(_APOSTROPHE_TRANSLATION)
    t = t.translate(_DASH_TRANSLATION)
    t = t.lower()
    t = re.sub(r"\s+", " ", t).strip()
    return t


def sha256_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def check_key_phrase_source_presence(article_text: str, keywords_path: str) -> dict:
    """Gate (a)。`keywords_path`(keywords_canonicalized.json)の各itemの
    `source_span`(無ければ`source_sentence`、どちらも無ければ
    `reason="NO_SOURCE_FIELD_AVAILABLE"`で不在扱い)が、`article_text`
    (正規化後)に部分文字列として実在するかを確認する。

    戻り値: {status: "PASS"|"FAIL", total, present, missing:[...],
             normalized_rules, keywords_path}
    本関数はraiseしない(呼び出し側がstatusを見てRuntimeErrorを送出する
    設計、Gate結果のJSON保存も呼び出し側の責務)。"""
    with open(keywords_path, encoding="utf-8") as f:
        kp = json.load(f)
    items = kp.get("items") or []
    normalized_article = normalize_text(article_text)

    missing = []
    present = 0
    for item in items:
        rank = item.get("rank")
        used_form = item.get("used_form")
        source_span = item.get("source_span")
        source_sentence = item.get("source_sentence")

        field_used = None
        raw_value = None
        if source_span:
            field_used = "source_span"
            raw_value = source_span
        elif source_sentence:
            field_used = "source_sentence"
            raw_value = source_sentence
        else:
            missing.append({
                "rank": rank, "used_form": used_form, "source_span": source_span,
                "reason": "NO_SOURCE_FIELD_AVAILABLE",
            })
            continue

        normalized_span = normalize_text(raw_value)
        if normalized_span and normalized_span in normalized_article:
            present += 1
        else:
            missing.append({
                "rank": rank, "used_form": used_form, "source_span": source_span,
                "source_sentence": source_sentence, "field_used": field_used,
                "reason": "SOURCE_SPAN_NOT_FOUND_IN_ARTICLE",
            })

    status = "PASS" if not missing else "FAIL"
    return {
        "status": status, "total": len(items), "present": present, "missing": missing,
        "normalized_rules": NORMALIZATION_RULES, "keywords_path": keywords_path,
    }


def assert_key_phrase_reuse_source_matches(source_article_text: str, target_article_text: str,
                                            context: str = "") -> dict:
    """Gate (b)。他記事(または旧run)からKey Phraseを流用する経路で、
    供給元本文(source_article_text)と流用先本文(target_article_text)の
    sha256が一致することを必須化する。不一致ならRuntimeErrorを送出し
    (流用しない、fail-closed)、一致すればPASS結果を返す。"""
    source_sha256 = sha256_text(source_article_text)
    target_sha256 = sha256_text(target_article_text)
    if source_sha256 != target_sha256:
        raise RuntimeError(
            f"KEY_PHRASE_REUSE_SOURCE_MISMATCH: Key Phrase流用元本文と流用先本文のsha256が"
            f"一致しません(source_sha256={source_sha256}, target_sha256={target_sha256}"
            f"{', context=' + context if context else ''})。他記事のKey Phraseをそのまま"
            "流用することはできません(KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01)。流用先本文から"
            "改めてKey Phraseを選定してください。")
    return {"status": "PASS", "source_sha256": source_sha256, "target_sha256": target_sha256,
            "context": context}


def _resolve_article_text(level_dir: str) -> tuple[str | None, str | None]:
    """CLI/評価用: level_dir配下の慣例ファイル名からarticle本文を解決する。
    (article.md優先、無ければarticle_normalized.txt)。呼び出し側
    Production関数は、本文がin-memoryで既にある場合はこの解決に頼らず
    直接article_textを渡すことを推奨する(このヘルパーはevidence収集・
    CLI専用)。"""
    for name in ("article.md", "article_normalized.txt"):
        path = f"{level_dir}/{name}"
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return f.read(), path
    return None, None


def _resolve_article_text_climb(start_dir: str, max_up: int = 5) -> tuple[str | None, str | None]:
    """CLI --index評価専用: index.jsonの`key_phrase_asset_path`はKey
    Phrase再選定サブディレクトリ配下(例: `.../kp5_regen_and_completion_01/
    kp5_replacement_selection_01/keywords_canonicalized.json`)を指す
    ことがあり、本文(article.md)自体はその親階層に留まる場合がある
    (KP1件だけの差し替えで記事全体は移動しないケース)。evidence収集の
    ため、start_dirから祖先方向へ`max_up`階層まで遡ってarticle.md/
    article_normalized.txtを探索する(見つかったpathは結果に記録され、
    人間が確認できる)。Production Gate呼び出し側は、この探索に頼らず
    実際のAssembly out_dir/article_textを直接渡すこと。"""
    d = start_dir
    for _ in range(max_up + 1):
        text, path = _resolve_article_text(d)
        if text is not None:
            return text, path
        parent = os.path.dirname(d)
        if not parent or parent == d:
            break
        d = parent
    return None, None


def _cli_gate_a(args: argparse.Namespace) -> dict:
    if args.keywords and args.article:
        keywords_path = args.keywords
        with open(args.article, encoding="utf-8") as f:
            article_text = f.read()
        result = check_key_phrase_source_presence(article_text, keywords_path)
        result["article_path"] = args.article
        return {"mode": "single", "result": result}

    if args.index:
        with open(args.index, encoding="utf-8") as f:
            index = json.load(f)
        per_item = []
        for entry in index.get("items", []):
            kp_path = entry["key_phrase_asset_path"]
            level_dir = os.path.dirname(os.path.dirname(kp_path))  # .../key_phrases/keywords... -> level dir
            article_text, article_path = _resolve_article_text_climb(level_dir)
            if article_text is None:
                per_item.append({
                    "article_id": entry.get("article_id"), "level": entry.get("level"),
                    "family": entry.get("family"), "keywords_path": kp_path,
                    "status": "SKIPPED_NO_ARTICLE_FILE", "article_path": None,
                })
                continue
            result = check_key_phrase_source_presence(article_text, kp_path)
            result.update({
                "article_id": entry.get("article_id"), "level": entry.get("level"),
                "family": entry.get("family"), "article_path": article_path,
            })
            per_item.append(result)
        pass_count = sum(1 for r in per_item if r.get("status") == "PASS")
        fail_count = sum(1 for r in per_item if r.get("status") == "FAIL")
        skipped_count = sum(1 for r in per_item if r.get("status") == "SKIPPED_NO_ARTICLE_FILE")
        return {"mode": "index", "total": len(per_item), "pass": pass_count, "fail": fail_count,
                "skipped": skipped_count, "items": per_item}

    raise SystemExit("--index、または--keywords + --articleのいずれかを指定してください。")


def main() -> None:
    parser = argparse.ArgumentParser(description="KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01 Gate (a) runtime evidence CLI")
    parser.add_argument("--index", help="user_test/translations/index.json形式のpath(canonical一括評価)")
    parser.add_argument("--keywords", help="単一評価: keywords_canonicalized.jsonのpath")
    parser.add_argument("--article", help="単一評価: 本文(article.md等)のpath")
    parser.add_argument("--out", required=True, help="結果JSONの出力先path")
    args = parser.parse_args()

    result = _cli_gate_a(args)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[KEY-PHRASE-SOURCE-GATE] mode={result['mode']} -> {args.out}")
    if result["mode"] == "single":
        print(f"  status={result['result']['status']} missing={len(result['result']['missing'])}")
    else:
        print(f"  total={result['total']} pass={result['pass']} fail={result['fail']} "
              f"skipped={result['skipped']}")


if __name__ == "__main__":
    main()
