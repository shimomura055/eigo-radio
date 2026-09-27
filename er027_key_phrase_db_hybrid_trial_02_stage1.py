# ============================================================
# er027_key_phrase_db_hybrid_trial_02_stage1.py
# KEY-PHRASE-DB-HYBRID-TRIAL-02
# ============================================================
# Stage 1(機械処理のみ、LLM不使用、決定論的): KEY-PHRASE-DB-BASED-
# SELECTION-TRIAL-01(er023_*)の取込・抽出ロジックを再利用しつつ、
# ユーザー指示の機械処理改善(不規則活用正規化・見出し連結artifact
# 除外・品詞の明らかな不一致除外・duplicate/near-duplicate整理・DB種別/
# 頻度情報付与)を追加する。新規ファイルのみで、er023_*は一切変更しない
# (importして再利用するだけ)。
#
# 本モジュールは「候補生成→除外Gate→~20件へのshortlist構築」までを
# 担当し、LLM呼び出しは一切行わない(Stage 2の呼び出しは
# er027_key_phrase_db_hybrid_trial_02_run.pyが別途担当する)。
#
# 重要な設計上の注意(実データ検証で判明した点、コード内に記録):
# 「品詞の明らかな不一致」ルールは、window(前方参照範囲)を広く取ると
# 既存の良い最終候補(pulled back/rolled back/standing behind/take over
# 等)まで誤って除外してしまうことが実データ検証で確認された。そのため
# 各ルールは「直前1語のみ」等の狭いスコープに限定し、6本文の既存final
# candidate 30件全件に対して誤除外が起きないことを起動時に自己検証する
# (run_stage1_for_article内のregression assertion)。
# ============================================================

from __future__ import annotations

import re
import unicodedata
from collections import Counter

import wordfreq

import er023_key_phrase_db_extraction as ext
import er023_key_phrase_db_ingest as ing

_WORD_TOKEN_RE = ext._WORD_TOKEN_RE
_SENTENCE_SPLIT_RE = ext._SENTENCE_SPLIT_RE
_normalize_key = ext._normalize_key
_CLOSED = ext._CLOSED_CLASS_FUNCTION_WORDS


# ------------------------------------------------------------
# (0) 見出し連結artifact除外: heading-aware sentence分割
# ------------------------------------------------------------
def tokenize_sentences_heading_aware(article_markdown: str) -> list:
    """既存er023.tokenize_sentencesは句読点(.!?)のみで文境界を決めるため、
    終端記号のないmarkdown見出し行が次の段落の先頭語と連結し、
    "line In"のような偽の2-gramを生成する不具合が実データで確認された
    (KEY-PHRASE-DB-BASED-SELECTION-TRIAL-01 REPORT §13.3)。本関数は
    見出し行を独立したブロックとして扱い、見出し行の前後で必ず文境界を
    切ることでこの問題を構造的に修正する(個別の誤検出語を都度除外する
    のではなく、tokenizeの段階で再発を防ぐ)。"""
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

    sentences = []
    for block in blocks:
        joined = unicodedata.normalize("NFKC", block)
        joined = joined.translate(str.maketrans({"‘": "'", "’": "'",
                                                  "“": '"', "”": '"'}))
        for s in _SENTENCE_SPLIT_RE.split(joined):
            toks = _WORD_TOKEN_RE.findall(s)
            if toks:
                sentences.append(toks)
    return sentences


# ------------------------------------------------------------
# (1) 不規則動詞正規化(規則語尾ロジックでは吸収できないgave/went/took/
#     taken等)。標準的な英文法の不規則動詞一覧であり、新規ライセンス
#     取得を要しない一般知識(KEY-PHRASE-DB-BASED-SELECTION-TRIAL-01
#     REPORT §13.2で「小〜中の改修規模」と評価済みの対応)。
# ------------------------------------------------------------
IRREGULAR_VERB_BASE_FORM = {
    "went": "go", "gone": "go",
    "took": "take", "taken": "take",
    "gave": "give", "given": "give",
    "came": "come",
    "made": "make",
    "did": "do", "done": "do",
    "saw": "see", "seen": "see",
    "got": "get", "gotten": "get",
    "broke": "break", "broken": "break",
    "spoke": "speak", "spoken": "speak",
    "wrote": "write", "written": "write",
    "rose": "rise", "risen": "rise",
    "fell": "fall", "fallen": "fall",
    "held": "hold",
    "kept": "keep",
    "left": "leave",
    "brought": "bring",
    "bought": "buy",
    "caught": "catch",
    "taught": "teach",
    "thought": "think",
    "sought": "seek",
    "fought": "fight",
    "found": "find",
    "sent": "send",
    "spent": "spend",
    "built": "build",
    "sold": "sell",
    "told": "tell",
    "stood": "stand",
    "understood": "understand",
    "won": "win",
    "wound": "wind",
    "drew": "draw", "drawn": "draw",
    "drove": "drive", "driven": "drive",
    "rode": "ride", "ridden": "ride",
    "rang": "ring", "rung": "ring",
    "sang": "sing", "sung": "sing",
    "sank": "sink", "sunk": "sink",
    "swam": "swim", "swum": "swim",
    "ran": "run",
    "began": "begin", "begun": "begin",
    "blew": "blow", "blown": "blow",
    "grew": "grow", "grown": "grow",
    "threw": "throw", "thrown": "throw",
    "flew": "fly", "flown": "fly",
    "knew": "know", "known": "know",
    "wore": "wear", "worn": "wear",
    "tore": "tear", "torn": "tear",
    "bore": "bear", "born": "bear", "borne": "bear",
    "chose": "choose", "chosen": "choose",
    "froze": "freeze", "frozen": "freeze",
    "stole": "steal", "stolen": "steal",
    "spoke": "speak",
    "shook": "shake", "shaken": "shake",
    "swore": "swear", "sworn": "swear",
    "hung": "hang",
    "hid": "hide", "hidden": "hide",
    "bit": "bite", "bitten": "bite",
    "led": "lead",
    "shot": "shoot",
    "lay": "lie", "lain": "lie",
    "laid": "lay",
    "paid": "pay",
    "said": "say",
    "meant": "mean",
    "read": "read",
    "set": "set",
    "put": "put",
    "cut": "cut",
    "hit": "hit",
    "let": "let",
    "cost": "cost",
    "hurt": "hurt",
    "shut": "shut",
    "split": "split",
    "spread": "spread",
    "burst": "burst",
    "sat": "sit",
    "lost": "lose",
    "met": "meet",
    "felt": "feel",
    "slept": "sleep",
    "dealt": "deal",
    "dreamt": "dream",
    "smelt": "smell",
    "learnt": "learn",
    "spoiled": "spoil", "spoilt": "spoil",
    "forgot": "forget", "forgotten": "forget",
    "forgave": "forgive", "forgiven": "forgive",
    "withdrew": "withdraw", "withdrawn": "withdraw",
    "overcame": "overcome", "overcome": "overcome",
    "became": "become",
    "showed": "show", "shown": "show",
    "struck": "strike",
    "swung": "swing",
    "dug": "dig",
    "stuck": "stick",
    "bent": "bend",
    "lent": "lend",
    "sped": "speed",
    "rode": "ride",
    "bound": "bind",
    "wove": "weave", "woven": "weave",
    "arose": "arise", "arisen": "arise",
}


def irregular_base_form(token: str) -> str | None:
    return IRREGULAR_VERB_BASE_FORM.get(token.lower())


def match_candidate_with_irregular_rescue(ngram: dict, dbs: dict) -> dict:
    """まず既存er023の照合(規則語尾lemma化込み)を試し、db_match_count==0
    だった場合のみ、不規則動詞の基本形へ還元した variant で再照合する
    (規則語尾ロジックが既に一致を見つけている場合は上書きしない=既存
    ロジックの決定を尊重する、副作用の少ない追加的rescueとして設計)。"""
    core = dict(ext.match_candidate_against_group1(ngram, dbs))
    if core["db_match_count"] > 0:
        core["irregular_verb_rescue"] = False
        return core

    surface_tokens = ngram["surface_tokens"]
    n = ngram["n"]
    variants = []
    if n == 1:
        base = irregular_base_form(surface_tokens[0])
        if base:
            variants.append(base)
    else:
        base = irregular_base_form(surface_tokens[0])
        if base:
            variants.append(" ".join([base] + [t.lower() for t in surface_tokens[1:]]))
    if not variants:
        core["irregular_verb_rescue"] = False
        return core

    matched_dbs, db_categories, cefr_level = set(), set(), None
    for v in variants:
        if n == 1:
            if v in dbs["cefr_j"]:
                matched_dbs.add("cefr_j")
                cefr_level = cefr_level or dbs["cefr_j"][v]["cefr"]
            if v in dbs["ngsl_family"]:
                matched_dbs.add("ngsl_family")
            if v in dbs["wiktionary"]:
                matched_dbs.add("wiktionary")
                db_categories.update(dbs["wiktionary"][v]["categories"])
        else:
            if v in dbs["wiktionary"]:
                matched_dbs.add("wiktionary")
                db_categories.update(dbs["wiktionary"][v]["categories"])
            if v in dbs["cefr_j"] and dbs["cefr_j"][v]["is_multiword"]:
                matched_dbs.add("cefr_j")
                cefr_level = cefr_level or dbs["cefr_j"][v]["cefr"]

    if not matched_dbs:
        core["irregular_verb_rescue"] = False
        return core

    core["matched_dbs"] = sorted(matched_dbs)
    core["db_match_count"] = len(matched_dbs)
    core["db_categories"] = sorted(db_categories)
    core["cefr_level"] = cefr_level
    core["irregular_verb_rescue"] = True
    core["irregular_base_form_used"] = variants[0]
    unit_type = ext.UNIT_TYPE_WORD if n == 1 else ext.UNIT_TYPE_PHRASE
    if n > 1:
        if "phrasal_verb" in db_categories:
            unit_type = ext.UNIT_TYPE_PHRASAL_VERB
        elif "idiom" in db_categories:
            unit_type = ext.UNIT_TYPE_IDIOM
        elif "proverb" in db_categories:
            unit_type = ext.UNIT_TYPE_DISCOURSE
        elif not db_categories and matched_dbs:
            unit_type = ext.UNIT_TYPE_PHRASE
    core["unit_type"] = unit_type
    return core


# ------------------------------------------------------------
# (2) 品詞の明らかな不一致・文脈誤検出のうち規則化可能なものを除外
# ------------------------------------------------------------
# 実データ検証(2026-09-27、KEY-PHRASE-DB-HYBRID-TRIAL-02設計段階)で
# window=2等の広い前方参照は"a person take over"の"take over"のような
# 正しい候補まで誤って除外することが判明したため、各ルールは直前1語のみ
# を見る狭いスコープに限定している。widowを広げて"play in"/"move in"や
# "bags out"(discontinuous phrasal verb)まで捕捉することは、既存の
# 良い候補を壊さずには実現できなかった(POSタグ付けが必要、既存REPORT
# §13.2/13.3の結論と整合)。この2件は本Stage1では捕捉できない既知の
# 残存ギャップとして報告する。
_DETERMINER_QUANTIFIER_CLOSED = {
    "a", "an", "the", "this", "that", "these", "those", "my", "your",
    "his", "her", "its", "our", "their", "no", "what", "some", "any",
    "each", "every", "either", "neither",
}
_COPULA_WORDS = {"is", "are", "was", "were", "be", "been", "being"}
_AMBIGUOUS_PARTICLE_FIRST_TOKENS = {"back", "over", "away", "off", "around", "about", "through"}
_SUBJECT_PRONOUNS = {"i", "you", "he", "she", "we", "they"}
_WH_WORDS = {"what", "who", "where", "when", "why", "how", "which"}
_TEMPORAL_MARKERS = {
    "day", "days", "week", "weeks", "month", "months", "year", "years",
    "morning", "afternoon", "evening", "night", "date", "occasion", "time",
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "january", "february", "march", "april", "may", "june", "july", "august",
    "september", "october", "november", "december",
}


def detect_context_mismatch(surface_tokens: list, unit_type: str, sentence_tokens: list, start: int) -> str | None:
    """2語のphrasal_verb/idiom候補に対し、規則化可能な範囲でPOS不一致・
    文脈誤検出を検出する。戻り値は発火したルール名(なければNone)。
    sentence_tokens/startは、その候補が含まれる「同一文」内でのトークン
    列と開始位置(前後の文を跨がない)。"""
    if len(surface_tokens) != 2:
        return None
    first = surface_tokens[0].lower()
    second = surface_tokens[1].lower()
    prev_tok = sentence_tokens[start - 1].lower() if start - 1 >= 0 else None

    if unit_type in (ext.UNIT_TYPE_PHRASAL_VERB, ext.UNIT_TYPE_IDIOM):
        # R1: 直前語が決定詞・限定詞(直接隣接のみ) -> 名詞句読みの疑い
        if prev_tok is not None and prev_tok in _DETERMINER_QUANTIFIER_CLOSED:
            return "preceded_by_determiner_immediate"
        # R2: 直前語がbe動詞、かつ候補先頭語が verb/adjective 両義の
        #     小さな閉集合に属する -> 叙述補語(predicate complement)読み
        if prev_tok is not None and prev_tok in _COPULA_WORDS and first in _AMBIGUOUS_PARTICLE_FIRST_TOKENS:
            return "preceded_by_copula_ambiguous_particle"

    if unit_type == ext.UNIT_TYPE_IDIOM:
        # R4: 先頭語が主語人称代名詞 -> 主語+動詞の節断片の疑い
        if first in _SUBJECT_PRONOUNS:
            return "subject_pronoun_verb_fragment"
        # R5: 2語目がwh語 -> 動詞+wh節(間投詞idiomではない)の疑い
        if second in _WH_WORDS:
            return "wh_complement_clause_continuation"

    # R6: 2語目が on/in/at で、その後3語以内に時間表現があれば時間の前置詞句
    if second in ("on", "in", "at"):
        following = [t.lower() for t in sentence_tokens[start + 2: start + 5]]
        if any(t in _TEMPORAL_MARKERS for t in following):
            return "temporal_prepositional_phrase"

    return None


# ------------------------------------------------------------
# (3) duplicate / near-duplicate整理
# ------------------------------------------------------------
def _lemma_variant_set(word: str) -> set:
    w = word.lower()
    return {w} | set(ext.lemma_candidates_for_word(w))


def merge_near_duplicates(candidates: list) -> list:
    """先頭語のlemma variant集合が重なり、かつ残りの語が同一・unit_typeが
    同一の候補を1件へ統合する(例: "pulled back"と"pull back"が両方
    candidate化された場合、db_match_countが高い方を残し、他方を
    observed_surface_variantsへ記録)。候補は既に(canonical_form,
    unit_type)でdedupe済みのものを渡す前提。

    設計上の注意: 当初は各候補の先頭語を「lemma候補の中で辞書順最小の
    文字列」へ一意に還元するアプローチを取っていたが、"pulled"->lemma
    候補に子音重複規則由来の"pul"(誤った過縮約)が含まれ、辞書順最小
    選択がこれを拾ってしまい"pull"と一致しなくなるバグが単体テストで
    実際に見つかった。そのため「lemma候補集合同士の共通部分があるか」
    という頑健な判定へ変更した。"""
    groups = []  # [{"variant_set": set, "remaining": str, "unit_type": str, "members": [..]}]
    for c in candidates:
        tokens = c["canonical_form"].split(" ")
        first_variants = _lemma_variant_set(tokens[0])
        remaining = " ".join(tokens[1:])
        placed = False
        for group in groups:
            if (group["remaining"] == remaining and group["unit_type"] == c["unit_type"]
                    and group["variant_set"] & first_variants):
                group["variant_set"] |= first_variants
                group["members"].append(c)
                placed = True
                break
        if not placed:
            groups.append({"variant_set": first_variants, "remaining": remaining,
                            "unit_type": c["unit_type"], "members": [c]})

    merged = []
    for group in groups:
        members = group["members"]
        best = dict(max(members, key=lambda c: c["db_match_count"]))
        best["observed_surface_variants"] = sorted({m["canonical_form"] for m in members})
        merged.append(best)
    return merged


# ------------------------------------------------------------
# (4) 重要な単語・単語群(repeated compound noun)検出
# ------------------------------------------------------------
# group1 DB(CEFR-J/NGSL/Wiktionary)は教育用コア語彙リストであり、
# "blockade"のようなやや高度だが実在する語を収録していないことが実データ
# 検証で判明した(KEY-PHRASE-DB-BASED-SELECTION-TRIAL-01の"sea blockade"
# 相当語がgroup1 word DBに一切ヒットしない、本Trialの設計段階で新規確認)。
# そのためこの検出ではwordfreqのzipf頻度を「実在の英単語か」の判定に使う
# (閾値2.0、KEY-PHRASE-DB-BASED-SELECTION-TRIAL-01時点で既にwordfreqは
# 観測目的の補助として導入済みであり、新規DB導入ではない)。
_WORDFREQ_REAL_WORD_ZIPF_THRESHOLD = 2.0


def _is_real_content_word(token: str) -> bool:
    tl = token.lower()
    if tl in _CLOSED:
        return False
    if not tl.isalpha() or len(tl) < 3:
        return False
    try:
        zf = wordfreq.zipf_frequency(tl, "en")
    except Exception:
        return False
    return zf >= _WORDFREQ_REAL_WORD_ZIPF_THRESHOLD


_NON_NOUN_POS_DISALLOWED = {
    "verb", "adverb", "preposition", "conjunction", "pronoun",
    "determiner", "auxiliary verb", "interjection",
}


def _is_plausible_noun_component(token: str, cefr_j: dict) -> bool:
    """CEFR-Jのpos情報を使い、動詞・副詞・前置詞等が紛れ込んだ候補
    ("clearly telling"/"without clearly"等、記事の定型言い回しの一部が
    偶然2回以上出現しただけのartifact)を除外する。CEFR-Jに見出しが無い
    語(例: "blockade"のようなgroup1 word DB未収録語)は許容する(pos情報
    が無いことを理由に「重要な名詞句」候補から排除しない)。"""
    key = token.lower()
    lookup_keys = [key] + ext.lemma_candidates_for_word(key)
    irregular = irregular_base_form(key)
    if irregular:
        lookup_keys.append(irregular)
    for k in lookup_keys:
        entry = cefr_j.get(k)
        if entry and entry.get("pos") in _NON_NOUN_POS_DISALLOWED:
            return False
    return True


def find_repeated_compound_noun_candidates(sentences: list, dbs: dict, min_repetition: int = 2,
                                            max_n: int = 3) -> list:
    """全content語(実在語、group1 DBの有無は問わない)から構成される
    2〜3語のn-gramのうち、記事本文中に2回以上(表層/単数複数を還元した
    形で)出現するものを「重要な単語群(multiword_term)」候補として拾う。
    群1DB(idiom/phrasal_verb/multiword_term)の被覆範囲外にある
    「重要な名詞句」("contract worker(s)"/"sea blockade"相当)を拾うための
    補完機構(ユーザー確定原則4「1枠=重要単語・単語群」に対応)。"""
    counter = Counter()
    surface_by_merge_key = {}
    first_seen_source = {}
    cefr_j = dbs["cefr_j"]

    for sent_tokens in sentences:
        ngrams_local = ext.generate_ngrams([sent_tokens], min_n=2, max_n=max_n)
        for ng in ngrams_local:
            toks = ng["surface_tokens"]
            toks_lower = [t.lower() for t in toks]
            if any(t in _CLOSED for t in toks_lower):
                continue
            if not all(_is_real_content_word(t) for t in toks):
                continue
            if not all(_is_plausible_noun_component(t, cefr_j) for t in toks):
                continue
            last_lemmas = ext.lemma_candidates_for_word(toks_lower[-1])
            base_last = sorted([toks_lower[-1]] + last_lemmas)[0] if last_lemmas else toks_lower[-1]
            merge_key = " ".join(toks_lower[:-1] + [base_last])
            counter[merge_key] += 1
            surface_by_merge_key.setdefault(merge_key, Counter())[ng["surface_form"]] += 1
            first_seen_source.setdefault(merge_key, " ".join(sent_tokens))

    results = []
    for merge_key, count in counter.items():
        if count < min_repetition:
            continue
        surface_counter = surface_by_merge_key[merge_key]
        best_surface = surface_counter.most_common(1)[0][0]
        results.append({
            "surface_form": best_surface,
            "canonical_form": _normalize_key(best_surface),
            "n": len(merge_key.split(" ")),
            "unit_type": ext.UNIT_TYPE_PHRASE,
            "matched_dbs": ["repeated_compound_noun_heuristic"],
            "db_match_count": 0,
            "db_categories": ["important_noun_phrase_heuristic"],
            "cefr_level": None,
            "repetition_count_in_article": count,
            "observed_surface_variants": sorted(surface_counter.keys()),
            "source_span": first_seen_source.get(merge_key, best_surface),
            "important_noun_phrase_candidate": True,
        })
    results.sort(key=lambda r: (-r["repetition_count_in_article"], r["canonical_form"]))
    return results


# ------------------------------------------------------------
# Stage 1 メインエントリポイント
# ------------------------------------------------------------
def run_stage1_for_article(article_text: str, dbs: dict) -> dict:
    sentences = tokenize_sentences_heading_aware(article_text)
    tokens_total = sum(len(s) for s in sentences)

    all_evidences = []
    context_mismatch_excluded = []
    irregular_rescued = []

    for sent_tokens in sentences:
        ngrams_local = ext.generate_ngrams([sent_tokens])
        for ng in ngrams_local:
            core = match_candidate_with_irregular_rescue(ng, dbs)
            if core["db_match_count"] == 0:
                continue
            if core.get("irregular_verb_rescue"):
                irregular_rescued.append(dict(core))
            mismatch_rule = detect_context_mismatch(
                ng["surface_tokens"], core["unit_type"], sent_tokens, ng["start"])
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

    word_survivors = [c for c in stage_b_survivors if c["unit_type"] == ext.UNIT_TYPE_WORD]
    phrase_survivors_raw = [c for c in stage_b_survivors if c["unit_type"] != ext.UNIT_TYPE_WORD]
    phrase_survivors = merge_near_duplicates(phrase_survivors_raw)
    phrase_survivors.sort(key=lambda c: (-c["db_match_count"], c["canonical_form"]))

    important_noun_candidates = find_repeated_compound_noun_candidates(sentences, dbs)
    # phrase_survivorsと同一canonical_formのものは重複させない
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
        "sentences": sentences,
        "tokens_total": tokens_total,
        "sentences_total": len(sentences),
        "raw_ngrams_evaluated_note": "sentence-aware 1-5gram, heading-boundary-safe",
        "before_dedup_count": before_dedup_count,
        "after_dedup_count": len(deduped),
        "stage_a_excluded_by_existing_gate_count": len(stage_a_excluded_by_existing_gate),
        "stage_a_survivors_count": len(stage_a_survivors),
        "irregular_verb_rescued": irregular_rescued,
        "irregular_verb_rescued_count": len(irregular_rescued),
        "context_mismatch_excluded": context_mismatch_excluded,
        "context_mismatch_excluded_count": len(context_mismatch_excluded),
        "stage_b_survivors_count": len(stage_b_survivors),
        "word_survivors": word_survivors_sorted,
        "phrase_survivors": phrase_survivors,
        "important_noun_candidates": important_noun_candidates,
    }


# ------------------------------------------------------------
# (5) Wiktionary multiword terms targeted lookup(group1未一致の重要句を
#     拾う補完機構、KEY-PHRASE-DB-BASED-SELECTION-TRIAL-01と同じAPI・
#     同じ既存モジュール[er023_key_phrase_db_ingest]を再利用する)。
#     "brent crude"のように記事中1回しか出現しないため(4)の repeated
#     compound noun検出では拾えない、かつgroup1 word DBにも一致しない
#     重要複合語を拾うための補完(ネットワークI/Oはorchestrator側が行い、
#     本モジュールは候補選定・結果反映のpure関数のみを提供する)。
# ------------------------------------------------------------
def select_unmatched_ngram_candidates_for_lookup(sentences: list, existing_canonical_forms: set,
                                                  budget: int = 40) -> list:
    seen = {}
    for sent_tokens in sentences:
        for ng in ext.generate_ngrams([sent_tokens], min_n=2, max_n=3):
            surface = ng["surface_form"]
            key = _normalize_key(surface)
            if key in existing_canonical_forms or key in seen:
                continue
            toks_lower = [t.lower() for t in ng["surface_tokens"]]
            if all(t in _CLOSED for t in toks_lower):
                continue
            if any(ch.isdigit() for ch in surface):
                continue
            seen[key] = surface

    def _content_count(s):
        return sum(1 for t in s.lower().split() if t not in _CLOSED)

    # 2-gramを3-gramより優先する(辞書上のmultiword termは2語が最も多く、
    # 3-gramを同列に扱うと"brent crude"のような有望な2-gramが3-gramに
    # 押し出されてしまうことが実データ検証で判明したための修正)。
    ordered = sorted(seen.values(), key=lambda s: (len(s.split()), -_content_count(s), s.lower()))
    return ordered[:budget]


def build_multiword_hit_evidences(lookup_results: dict) -> list:
    """{candidate_surface: bool}(er023_key_phrase_db_ingest.
    wiktionary_multiword_targeted_lookupの'results')から、一致した候補の
    evidence dictを構築する(既存er023 trial_run.pyと同じ組み立て方)。"""
    hits = []
    for surface, matched in lookup_results.items():
        if not matched:
            continue
        key = _normalize_key(surface)
        hits.append({
            "surface_form": surface, "canonical_form": key, "n": len(surface.split()),
            "matched_dbs": ["wiktionary"], "db_match_count": 1,
            "db_categories": ["multiword_term"], "unit_type": ext.UNIT_TYPE_PHRASE,
            "cefr_level": None, "source_span": surface, "context_mismatch_rule": None,
            "important_noun_phrase_candidate": True, "repetition_count_in_article": None,
            "observed_surface_variants": [surface],
        })
    return hits


def gate_and_merge_multiword_hits(hits: list) -> list:
    """multiword hitへ既存の除外Gate(too_easy_or_common/unnatural_out_of_
    context)を適用し、通過したものだけを返す。"""
    survivors = []
    for h in hits:
        gate = ext.apply_exclusion_gate(h, [], {})
        rule_excluded = ((gate["too_easy_or_common"]["rule_determined"] and gate["too_easy_or_common"]["value"]) or
                        (gate["unnatural_out_of_context"]["rule_determined"] and gate["unnatural_out_of_context"]["value"]))
        if not rule_excluded:
            h["exclusion_gate_result"] = gate
            survivors.append(h)
    return survivors


def build_shortlist(stage1_result: dict, target_total: int = 20, phrase_cap: int = 15,
                     word_min: int = 5) -> dict:
    """~20件のshortlistを組む。件数固定が目的ではないため、実際の候補数が
    少ない場合はそのまま少ない件数で返す(ユーザー確定原則5)。"""
    phrase_included = list(stage1_result["phrase_survivors"][:phrase_cap])
    important_noun_included = list(stage1_result["important_noun_candidates"])

    remaining = max(0, target_total - len(phrase_included) - len(important_noun_included))
    word_fill_count = remaining
    if remaining < word_min and len(stage1_result["word_survivors"]) > 0:
        word_fill_count = min(word_min, len(stage1_result["word_survivors"]))
    word_included = list(stage1_result["word_survivors"][:word_fill_count])

    shortlist = phrase_included + important_noun_included + word_included
    return {
        "shortlist": shortlist,
        "phrase_included_count": len(phrase_included),
        "important_noun_included_count": len(important_noun_included),
        "word_included_count": len(word_included),
        "shortlist_total_count": len(shortlist),
    }
