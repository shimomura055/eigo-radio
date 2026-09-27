# ============================================================
# er029_key_phrase_db_hybrid_trial_04_stage1.py
# KEY-PHRASE-DB-HYBRID-TRIAL-04
# ============================================================
# KEY-PHRASE-DB-HYBRID-TRIAL-03(er028_*)の確定版Stage 1を無変更のまま
# import/再利用しつつ、Trial-03追加評価run(2026-09-27、
# KEY-PHRASE-DB-HYBRID-TRIAL-03_REPORT.md §15-3/§15-4)で見つかった
# 2つの構造的limitationを一般化して修正する。
#
#   Fix A. 会話文のsentence segmentation:
#     既存`er023_key_phrase_db_extraction._SENTENCE_SPLIT_RE`
#     (`[.!?]+(?=\s|$)`)は、終端句読点の直後に閉じ引用符が続く場合
#     (例: `"You asked me to wake you." "I did not."`)に分割できず、
#     複数の独立した発話文が1個のsentence unitへ結合されてしまう
#     (実データ: twins_a2のS6、`validate_min_unit_selection`が
#     「source_sentenceがB2本文に存在しない」でINVALIDにした原因)。
#     本ファイルは、終端句読点の直後に閉じ引用符・閉じ括弧が0〜2文字
#     続く場合も分割対象に含める一般規則(英語の一般的な約物規則、
#     個別作品のhardcodeではない)を追加した
#     `build_sentence_units_v4`を新設する。er023/er027/er028自体は
#     一切変更しない(Trial-03の再現性を保つ)。
#
#   Fix B. rare / technical single wordの機械screening漏れ:
#     既存Stage 1は、n-gram候補がgroup1 DB(CEFR-J/NGSL/Wiktionary
#     idiom系)のいずれにも一致しない場合、`db_match_count==0`として
#     無条件に候補から除外する(`run_stage1_for_article_v3`内
#     `if core["db_match_count"] == 0: continue`)。これにより、
#     "grogginess"/"self-awakening"のようなCEFR-J/NGSL外・1-token・
#     Wiktionary未登録(self-awakeningは実際にページ自体が存在しない、
#     2026-09-27実データ確認)の重要語が、LLMに届く前の機械screening
#     段階で完全に消えてしまう(Trial-03 REPORT §15-4、wake_a2で
#     既存Production公開Key Phrase5件中0件しか一致しなかった実害)。
#
#     本ファイルは、ユーザー指示どおりまず
#     `select_unmatched_ngram_candidates_for_lookup`のmin_n=1拡張に
#     相当する経路(Wiktionary `Category:English lemmas`所属確認、
#     `wiktionary_unigram_lemma_lookup`)を実装したが、実データ検証の
#     結果「grogginess」は回収できる一方「self-awakening」はWiktionary
#     に見出し自体が存在せずこの経路だけでは回収できないことが判明した
#     (§下記コメント参照)。そのため、`find_repeated_compound_noun_
#     candidates`(er027、複数語の重要名詞句をDB一致なしでも
#     wordfreq実在判定+CEFR-J品詞妥当性で拾う、既存の設計前例)と同じ
#     設計思想を1-tokenへ一般化し、形態素条件(内部ハイフン=複合語で
#     ある形態論的シグナル、または-ness/-tion/-sion/-ity/-ism/-ology/
#     -ography/-ative/-ization等の技術語・抽象名詞に典型的な派生
#     接尾辞)+頻度条件(wordfreq zipf頻度が閾値未満、または頻度データ
#     自体が存在しない=一般語彙コーパスにも载っていないほど稀)+
#     文脈条件(記事内出現・固有名詞/会話タグ除外のための「本文中に
#     小文字表記の出現が最低1回ある」ガード)を満たす1-token候補を
#     新規に候補化する(`select_rare_single_word_candidates`)。
#     新しいDB(有料辞書・大規模コーパス等)は一切導入していない
#     (既存のCEFR-J/NGSL/Wiktionary/wordfreqの範囲内)。
# ============================================================

from __future__ import annotations

import json
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from typing import Optional

import wordfreq

import er023_key_phrase_db_extraction as ext
import er023_key_phrase_db_ingest as ing
import er027_key_phrase_db_hybrid_trial_02_stage1 as s1v2
import er028_key_phrase_db_hybrid_trial_03_stage1 as s1v3

_normalize_key = ext._normalize_key
_WORD_TOKEN_RE = ext._WORD_TOKEN_RE
_CLOSED = ext._CLOSED_CLASS_FUNCTION_WORDS


# ============================================================
# Fix A: 引用符を閉じた発話単位を認識できる一般化した文分割
# ============================================================

# 終端句読点(.!?)の直後に、閉じ引用符・閉じ括弧が0〜2文字続く場合も
# 分割点として認める(既存er023._SENTENCE_SPLIT_REは"直後が空白/文末"の
# 場合しか分割できず、`."`のように閉じ引用符が挟まる境界を見逃していた)。
QUOTE_AWARE_SENTENCE_SPLIT_RE = re.compile(r'[.!?]+[)\]"\']{0,2}(?=\s|$)')


def build_sentence_units_v4(article_markdown: str) -> list:
    """er028.build_sentence_units(v3)と同じブロック分割・引用符正規化を
    使うが、文境界検出にFix A(引用符を閉じた発話単位を認識できる一般化
    規則)を適用する。分割後、各sentence unitの先頭・末尾に残る単独の
    引用符(対応する相手が同じunit内に無い、発話の開始/終了境界の
    片割れ)は1文字だけ取り除く(SENTENCE REFERENCEテーブル表示
    `f'{sid}: "{text}"'`との二重引用符表示を避けるため。取り除いても
    記事本文中の連続部分文字列であることは変わらず、
    `validate_min_unit_selection`のsubstring照合には影響しない)。"""
    lines = article_markdown.splitlines()
    blocks = []
    current = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            if current:
                blocks.append(" ".join(current))
                current = []
            blocks.append(stripped.lstrip("#").strip())
        else:
            current.append(stripped)
    if current:
        blocks.append(" ".join(current))

    units = []
    for block in blocks:
        joined = unicodedata.normalize("NFKC", block)
        joined = joined.translate(str.maketrans({"‘": "'", "’": "'",
                                                  "“": '"', "”": '"'}))
        for raw_sentence in QUOTE_AWARE_SENTENCE_SPLIT_RE.split(joined):
            raw_sentence = raw_sentence.strip()
            if not raw_sentence:
                continue
            if raw_sentence[0] in "\"'":
                raw_sentence = raw_sentence[1:].strip()
            if raw_sentence and raw_sentence[-1] in "\"'":
                raw_sentence = raw_sentence[:-1].strip()
            if not raw_sentence:
                continue
            toks = _WORD_TOKEN_RE.findall(raw_sentence)
            if not toks:
                continue
            units.append({"tokens": toks, "raw_text": raw_sentence})
    return units


# ============================================================
# Fix B: rare / technical single word候補(1-gram)の一般化した候補生成
# ============================================================

# 技術語・抽象名詞に典型的な派生接尾辞(閉じたクラス、個別語のhardcodeでは
# ない既存の一般的な英語形態論知識)。内部ハイフンも複合語シグナルとして
# 同格に扱う("self-awakening"のような、まだ辞書化されていない専門複合語)。
_RARE_TECHNICAL_SUFFIXES = (
    "ness", "tion", "sion", "ity", "ism", "ology", "ography", "ative", "ization",
)
_RARE_WORD_ZIPF_THRESHOLD = 3.3
_MIN_RARE_WORD_LETTER_LEN = 4

_UNIGRAM_CANDIDATE_TOKEN_RE = re.compile(r"^[a-z]+(?:-[a-z]+)*$")


def _has_rare_morphology(key: str) -> bool:
    if "-" in key:
        return True
    return any(key.endswith(suf) for suf in _RARE_TECHNICAL_SUFFIXES)


def _is_frequency_rare(key: str) -> bool:
    try:
        zf = wordfreq.zipf_frequency(key, "en")
    except Exception:
        return True
    if zf <= 0:
        return True
    return zf < _RARE_WORD_ZIPF_THRESHOLD


def _iter_unigram_occurrences(sentence_units: list) -> dict:
    """sentence_unit群から1-gram候補ごとの出現情報(表層バリアント・
    出現回数・小文字表記での出現有無=固有名詞/会話タグの簡易除外ガード)
    を集約する。"""
    info: dict = {}
    for u in sentence_units:
        for tok in u["tokens"]:
            key = _normalize_key(tok)
            if not key:
                continue
            entry = info.setdefault(key, {
                "surface_variants": Counter(), "occurrence_count": 0,
                "has_lowercase_occurrence": False,
            })
            entry["surface_variants"][tok] += 1
            entry["occurrence_count"] += 1
            if tok[:1].islower():
                entry["has_lowercase_occurrence"] = True
    return info


def _unigram_candidate_reason(key: str, entry: dict, dbs: dict) -> Optional[str]:
    """1-gram候補の採否理由を返す(採用しない場合はNone)。
    "morphology"/"frequency_known_rare"はこの時点で確定採用(direct)。
    "frequency_unknown"(wordfreqに頻度データが一切無い)は、実データで
    アクセント文字の非対応(既存`ext._WORD_TOKEN_RE`はASCII英字のみを
    トークン化するため、"minaudières"のような非ASCII文字混じりの語が
    "minaudi"のような無意味な断片へ壊れる、2026-09-27実データで発見)を
    含む「実在しない語」を誤って拾う恐れがあるため、Wiktionary lemma
    lookupでの確認が取れた場合のみ最終的に採用する(orchestrator側が
    `wiktionary_unigram_lemma_lookup`の結果でこの区分だけを絞り込む)。"""
    if key in _CLOSED:
        return None
    if not _UNIGRAM_CANDIDATE_TOKEN_RE.match(key):
        return None
    if len(key.replace("-", "")) < _MIN_RARE_WORD_LETTER_LEN:
        return None
    if not entry["has_lowercase_occurrence"]:
        return None
    # 既存group1 DB(CEFR-J/NGSL/Wiktionary idiom系)に一致する語は対象外
    # (既存match_candidate_against_group1をそのまま再利用、判定基準の
    # 二重実装を避ける)。
    ngram = {"n": 1, "surface_tokens": [key], "surface_form": key}
    core = ext.match_candidate_against_group1(ngram, dbs)
    if core["db_match_count"] > 0:
        return None
    if _has_rare_morphology(key):
        return "morphology"
    try:
        zf = wordfreq.zipf_frequency(key, "en")
    except Exception:
        zf = 0.0
    if zf <= 0:
        return "frequency_unknown"
    if zf < _RARE_WORD_ZIPF_THRESHOLD:
        return "frequency_known_rare"
    return None


def select_rare_single_word_candidates(sentence_units: list, dbs: dict,
                                        article_title: str = "", budget: int = 15) -> list:
    """記事本文の1-gram候補のうち、group1 DBに一致せず(fix対象=db_match_
    count 0で機械screeningから完全に消えていた語)、かつ形態素/頻度条件を
    満たすものを、Wiktionary lookup予定の候補として選ぶ(呼び出し順は
    occ多い順→zipf低い順→タイトル関連語優先)。ネットワークI/Oは行わない
    (呼び出し側=orchestratorがwiktionary_unigram_lemma_lookupを呼ぶ)。
    戻り値: [(canonical_key, entry, reason), ...]。reasonは
    "morphology"/"frequency_known_rare"(direct採用)/
    "frequency_unknown"(Wiktionary確認が取れた場合のみ採用)。"""
    info = _iter_unigram_occurrences(sentence_units)
    title_keys = {_normalize_key(t) for t in _WORD_TOKEN_RE.findall(article_title or "")}

    eligible = []
    for k, e in info.items():
        reason = _unigram_candidate_reason(k, e, dbs)
        if reason is not None:
            eligible.append((k, e, reason))

    def _priority(item):
        key, entry, _reason = item
        title_related = key in title_keys
        try:
            zf = wordfreq.zipf_frequency(key, "en")
        except Exception:
            zf = 0.0
        return (0 if title_related else 1, zf, -entry["occurrence_count"], key)

    eligible.sort(key=_priority)
    return eligible[:budget]


def wiktionary_unigram_lemma_lookup(candidates: list, batch_size: int = 50,
                                     sleep_sec: float = 1.5) -> dict:
    """1-gram候補がWiktionary英語見出し(`Category:English lemmas`、
    英語の見出し語全体を包含する既存カテゴリ)に実在するかどうかを確認
    する。既存`er023_key_phrase_db_ingest.wiktionary_multiword_targeted_
    lookup`と同じAPI・同じUser-Agent・同じbatch/retry方式を、確認対象
    カテゴリだけ変えて実装した(er023自体は無変更、定数
    `ing.WIKTIONARY_API`/`ing.WIKTIONARY_USER_AGENT`のみ再利用)。

    実データ確認(2026-09-27): "grogginess"はこのカテゴリに所属する
    ページが存在し(=Wiktionary lookupで回収可能)、"self-awakening"は
    ページ自体が存在しない(`missing`、Wiktionary未登録)。そのため本
    lookupは、reason="morphology"/"frequency_known_rare"の候補には
    「確認・注釈するための補助情報」として使い(lookup失敗を理由に
    候補から除外しない)、reason="frequency_unknown"の候補にだけは
    「採用可否を決めるゲート」として使う(`build_rare_single_word_
    evidences`側で判定、§コメント参照。非ASCII文字を含む語がASCII限定
    トークナイザで壊れて生じる無意味な断片[例:
    "minaudières"→"minaudi"、2026-09-27実データで発見]を、頻度データが
    全く無いことだけを理由に「重要な稀少語」として誤採用しないための
    安全策)。"""
    results = {}
    calls = 0
    t0 = time.time()
    unique_candidates = sorted(set(candidates))
    for i in range(0, len(unique_candidates), batch_size):
        batch = unique_candidates[i:i + batch_size]
        titles_param = "|".join(batch)
        params = {
            "action": "query", "titles": titles_param, "prop": "categories",
            "clcategories": "Category:English lemmas", "cllimit": "500",
            "format": "json",
        }
        url = ing.WIKTIONARY_API + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"User-Agent": ing.WIKTIONARY_USER_AGENT})
        data = None
        for retry_i in range(5):
            try:
                with urllib.request.urlopen(req, timeout=20) as resp:
                    data = json.load(resp)
                break
            except urllib.error.HTTPError as e:
                if e.code == 429 and retry_i < 4:
                    wait = float(e.headers.get("Retry-After", 5)) if e.headers else 5
                    time.sleep(max(wait, 2 ** retry_i))
                    continue
                raise
        calls += 1
        pages = data.get("query", {}).get("pages", {})
        matched_titles = set()
        for _, page in pages.items():
            if "categories" in page and page.get("categories"):
                matched_titles.add(page.get("title"))
        for cand in batch:
            results[cand] = cand in matched_titles
        if i + batch_size < len(unique_candidates):
            time.sleep(sleep_sec)
    elapsed = time.time() - t0
    return {"results": results, "api_calls": calls, "elapsed_sec": round(elapsed, 2),
            "candidate_count": len(unique_candidates)}


def build_rare_single_word_evidences(selected: list, wiktionary_confirmed: dict) -> list:
    """select_rare_single_word_candidatesの結果(key, entry, reason)+
    Wiktionary lemma lookup結果から、evidence dictを構築する。
    reason="frequency_unknown"(wordfreqに頻度データが一切無い、非ASCII
    文字混じり語のトークナイザ破損断片等が混入しうる区分)は、
    Wiktionary lemma lookupで実在確認が取れたものだけを採用する
    (確認できなければ黙って除外、STOP対象ではない=単に候補化しない)。
    reason="morphology"/"frequency_known_rare"はWiktionary確認の有無に
    関わらず採用する(確認結果はevidenceへ注釈として残すのみ)。

    重要な単語・単語群候補バケット(`important_noun_phrase_candidate`)へ
    合流させる(bucket名自体が「単語・単語群」であり、1-tokenの重要語も
    このbucketに収まる設計、run側prompt文言は無変更のまま再利用可能)。"""
    results = []
    dropped_unconfirmed = []
    for key, entry, reason in selected:
        confirmed = bool(wiktionary_confirmed.get(key))
        if reason == "frequency_unknown" and not confirmed:
            dropped_unconfirmed.append(key)
            continue
        surface = entry["surface_variants"].most_common(1)[0][0]
        results.append({
            "surface_form": surface,
            "canonical_form": key,
            "n": 1,
            "unit_type": ext.UNIT_TYPE_WORD,
            "matched_dbs": [],
            "db_match_count": 0,
            "db_categories": ["rare_technical_single_word_heuristic"],
            "cefr_level": None,
            "repetition_count_in_article": entry["occurrence_count"],
            "observed_surface_variants": sorted(entry["surface_variants"]),
            "source_span": surface,
            "important_noun_phrase_candidate": True,
            "rare_word_selection_reason": reason,
            "wiktionary_lemma_confirmed": confirmed,
        })
    results.sort(key=lambda r: r["canonical_form"])
    return {"evidences": results, "dropped_unconfirmed_frequency_unknown": dropped_unconfirmed}


# ============================================================
# Stage 1 メインエントリポイント(v4): er028(v3)の各パーツを再利用しつつ
# Fix A(sentence segmentation)を組み込む。Fix B(rare single word)は
# ネットワークI/Oを伴うため、orchestrator側(er029_run.py)が
# select_rare_single_word_candidates -> wiktionary_unigram_lemma_lookup
# -> build_rare_single_word_evidences の順で呼び出し、戻り値を
# important_noun_candidatesへ合流させる(run_stage1_and_shortlist_v3の
# 既存Wiktionary multiword hit合流パターンと同じ設計)。
# ============================================================

def run_stage1_for_article_v4(article_text: str, dbs: dict) -> dict:
    sentence_units = build_sentence_units_v4(article_text)
    sentences_tokens = [u["tokens"] for u in sentence_units]
    cefr_j = dbs["cefr_j"]

    all_evidences = []
    irregular_rescued = []

    for sent_tokens in sentences_tokens:
        ngrams_local = ext.generate_ngrams([sent_tokens])
        for ng in ngrams_local:
            core = s1v2.match_candidate_with_irregular_rescue(ng, dbs)
            if core["db_match_count"] == 0:
                continue
            if core.get("irregular_verb_rescue"):
                irregular_rescued.append(dict(core))
            mismatch_rule = s1v3.detect_context_mismatch_v3(
                ng["surface_tokens"], core["unit_type"], sent_tokens, ng["start"], cefr_j)
            core["context_mismatch_rule"] = mismatch_rule
            core["source_span"] = ng["surface_form"]
            core["final_selection_reason"] = None
            all_evidences.append(core)

    before_dedup_count = len(all_evidences)
    deduped = ext.dedupe_candidates_by_canonical_form(all_evidences)

    for cand in deduped:
        cand["exclusion_gate_result"] = ext.apply_exclusion_gate(cand, [], {})

    def _rule_excluded(cand):
        gate = cand["exclusion_gate_result"]
        return ((gate["too_easy_or_common"]["rule_determined"] and gate["too_easy_or_common"]["value"]) or
                (gate["unnatural_out_of_context"]["rule_determined"] and gate["unnatural_out_of_context"]["value"]))

    stage_a_survivors = [c for c in deduped if not _rule_excluded(c)]
    stage_a_excluded_by_existing_gate = [c for c in deduped if _rule_excluded(c)]

    context_mismatch_excluded = [c for c in stage_a_survivors if c.get("context_mismatch_rule")]
    stage_b_survivors = [c for c in stage_a_survivors if not c.get("context_mismatch_rule")]

    word_survivors_raw = [c for c in stage_b_survivors if c["unit_type"] == ext.UNIT_TYPE_WORD]
    word_survivors = s1v3.strip_possessive_noise_from_word_survivors(word_survivors_raw)
    phrase_survivors_raw = [c for c in stage_b_survivors if c["unit_type"] != ext.UNIT_TYPE_WORD]
    phrase_survivors = s1v2.merge_near_duplicates(phrase_survivors_raw)
    phrase_survivors.sort(key=lambda c: (-c["db_match_count"], c["canonical_form"]))

    important_noun_candidates = s1v2.find_repeated_compound_noun_candidates(sentences_tokens, dbs)
    existing_canonicals = {c["canonical_form"] for c in phrase_survivors}
    important_noun_candidates = [c for c in important_noun_candidates
                                  if c["canonical_form"] not in existing_canonicals]

    def _word_rarity_key(c):
        try:
            zf = wordfreq.zipf_frequency(c["canonical_form"], "en")
        except Exception:
            zf = 0.0
        return (zf, c["canonical_form"])

    word_survivors_sorted = sorted(word_survivors, key=_word_rarity_key)

    return {
        "sentence_units": sentence_units,
        "tokens_total": sum(len(u["tokens"]) for u in sentence_units),
        "sentences_total": len(sentence_units),
        "before_dedup_count": before_dedup_count,
        "after_dedup_count": len(deduped),
        "stage_a_excluded_by_existing_gate_count": len(stage_a_excluded_by_existing_gate),
        "stage_a_survivors_count": len(stage_a_survivors),
        "irregular_verb_rescued_count": len(irregular_rescued),
        "context_mismatch_excluded": context_mismatch_excluded,
        "context_mismatch_excluded_count": len(context_mismatch_excluded),
        "stage_b_survivors_count": len(stage_b_survivors),
        "word_survivors": word_survivors_sorted,
        "phrase_survivors": phrase_survivors,
        "important_noun_candidates": important_noun_candidates,
    }


# attach_compact_contextはer028(v3)を無変更のまま再利用する(sentence_
# unitsの中身がv4由来かv3由来かに関わらず同じインターフェースで動く)。
attach_compact_context = s1v3.attach_compact_context
