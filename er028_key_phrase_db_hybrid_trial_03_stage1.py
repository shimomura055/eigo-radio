# ============================================================
# er028_key_phrase_db_hybrid_trial_03_stage1.py
# KEY-PHRASE-DB-HYBRID-TRIAL-03
# ============================================================
# KEY-PHRASE-DB-HYBRID-TRIAL-02(er027_*)のStage 1(機械screening)を
# import/再利用しつつ、ユーザー指示の既知bug一般化修正(A〜C)と、
# LLM input軽量化(article全文を渡さない)に必要な最小限のcompact
# context(候補ごとの短い引用文・記事内出現回数・sentence ID)を追加する。
#
# er027_*/er023_*は一切変更しない(import/再利用のみ)。新規ロジックは
# 全て本ファイルへ追加する。
#
# 修正した既知bug(すべて個別語のhardcodeではなく、既存のCEFR-J品詞
# 情報・既存の閉じた文法クラスを使った一般化):
#   A. discontinuous phrasal verb false positive
#      ("large bags out"->"bags out"、"an unexpected move in oil
#      prices"->"move in"、"a short play in three acts"->"play in")。
#      候補の直前1語(狭いスコープ、既存設計を踏襲)がCEFR-J品詞で
#      "adjective"の場合、2語のphrasal_verb/idiom候補を除外する
#      (ADJ+NOUNの名詞句読みが疑われるため)。ただし英語文法上
#      「述語専用形容詞("a-adjective"、alone/afraid/asleep等の閉じた
#      クラス)」は例外とする(このクラスは名詞の前には通常置かれず、
#      既存の良い候補"one size alone sits on the throne"のような
#      floating用法を誤って壊さないため)。
#   B. Wiktionary multiword_termタグの粗さ("even though"/"other side"/
#      "other end"が重要名詞句バケットへ誤混入): 群1DB内の
#      repeated_compound_noun検出は既にCEFR-J品詞で名詞句として妥当かを
#      判定済みだが(er027 find_repeated_compound_noun_candidates内の
#      _is_plausible_noun_component)、Wiktionary multiword targeted
#      lookupのhit(er027 build_multiword_hit_evidences)はこの判定を
#      経由せず無条件にimportant_noun_phrase_candidate=Trueにしていた。
#      本ファイルでは同じ品詞判定基準を、lookupで見つかったhitにも
#      後付けで適用し、妥当でなければimportant_noun_phrase_candidateを
#      Falseへ落とす(候補自体は捨てず、phrase/discourse候補として
#      残す)。
#   C. possessive 's等のnoise(user's/chart's/season's): 群1DB照合は
#      lemma化(語尾's除去含む)で成功しているが、surface_form/
#      canonical_formには元の"'s"が残ったままlist化されていた。
#      本ファイルでは、word候補のcanonical_formが所有格"'s"で終わる
#      場合、表示形を所有格なしの基本形へ正規化する(既に基本形の
#      候補が別途存在する場合は所有格側を破棄して重複させない)。
# ============================================================

from __future__ import annotations

import re
from typing import Optional

import er023_key_phrase_db_extraction as ext
import er027_key_phrase_db_hybrid_trial_02_stage1 as s1

_WORD_TOKEN_RE = ext._WORD_TOKEN_RE
_normalize_key = ext._normalize_key

# ------------------------------------------------------------
# (A) 述語専用形容詞("a-adjective")の閉じたクラス。英語文法上、この
# クラスは通常名詞の前(attributive)には置けず、floating/predicative
# 用法(例: "size alone"/"a man asleep")が中心であるという既存の一般
# 文法知識(新規ライセンス不要)。個別バグの後付けhardcodeではなく、
# 既存の閉じた語彙クラスをそのまま参照する。
# ------------------------------------------------------------
_PREDICATIVE_ONLY_ADJECTIVES = {
    "alone", "afraid", "alike", "alive", "asleep", "awake", "aware",
    "ablaze", "adrift", "aghast", "ajar", "akin", "aloof", "amiss",
    "astir", "awry", "unaware", "unafraid",
}


def _looks_like_past_tense_verb_form(token: str) -> bool:
    """CEFR-Jは語ごとに単一のpos(代表的な語義)しか持たないため、
    "human"(名詞/形容詞)・"only"(副詞/形容詞)のような多品詞語を
    形容詞と誤認し、"A human stood behind..."/"...only pulled back..."
    のような正しい候補まで誤って除外してしまう実データ上の問題が
    見つかった(2026-09-27、regression実行で発見)。過去分詞・規則過去形
    ("-ed"語尾)・既存の不規則動詞過去形テーブル(IRREGULAR_VERB_BASE_
    FORM、既存流用)に一致する場合、その語は英語の形態論上ほぼ確実に
    動詞の過去形であり名詞として読める余地がないため、直前語が形容詞
    タグでも本ルールを発火させない(個別語のhardcodeではなく、既存の
    不規則動詞テーブル+規則的な形態論パターンの一般化)。"""
    tl = token.lower()
    if tl in s1.IRREGULAR_VERB_BASE_FORM:
        return True
    if len(tl) > 3 and tl.endswith("ed"):
        return True
    return False


def detect_context_mismatch_v3(surface_tokens: list, unit_type: str, sentence_tokens: list,
                                start: int, cefr_j: dict) -> Optional[str]:
    """er027.detect_context_mismatch(既存6ルール、無変更のまま再利用)に
    加え、discontinuous phrasal verb false positive(bug A)を一般化して
    捕捉する新ルールR7を追加する。"""
    existing_rule = s1.detect_context_mismatch(surface_tokens, unit_type, sentence_tokens, start)
    if existing_rule:
        return existing_rule

    if len(surface_tokens) != 2:
        return None
    if unit_type not in (ext.UNIT_TYPE_PHRASAL_VERB, ext.UNIT_TYPE_IDIOM):
        return None
    if start - 1 < 0:
        return None
    if _looks_like_past_tense_verb_form(surface_tokens[0]):
        return None
    prev_tok = sentence_tokens[start - 1].lower()
    if prev_tok in _PREDICATIVE_ONLY_ADJECTIVES:
        return None
    entry = cefr_j.get(prev_tok)
    if entry and entry.get("pos") == "adjective":
        return "preceded_by_attributive_adjective_np_misparse"
    return None


# ------------------------------------------------------------
# (B) Wiktionary multiword hitのnoun-phrase妥当性再判定
# ------------------------------------------------------------
def refine_multiword_hits_noun_phrase_flag(hits: list, cefr_j: dict) -> list:
    """er027.build_multiword_hit_evidences()の出力(important_noun_phrase_
    candidate=True固定)を、er027.find_repeated_compound_noun_candidates
    内で既に使われている品詞妥当性判定(_is_plausible_noun_component)と
    同じ基準で再評価する。妥当でなければimportant_noun_phrase_candidate
    をFalseへ落とすが、候補自体は削除しない(phrase/discourse候補として
    は残す、ユーザー指示どおり)。"""
    refined = []
    for h in hits:
        tokens = h["surface_form"].split(" ")
        plausible = all(s1._is_plausible_noun_component(t, cefr_j) for t in tokens)
        h = dict(h)
        h["important_noun_phrase_candidate"] = bool(plausible)
        h["noun_phrase_plausibility_checked"] = True
        refined.append(h)
    return refined


# ------------------------------------------------------------
# (C) possessive 's正規化
# ------------------------------------------------------------
_POSSESSIVE_SUFFIX_RE = re.compile(r"(?:'s|s')$", re.IGNORECASE)


def strip_possessive_noise_from_word_survivors(word_survivors: list) -> list:
    """word候補(unit_type==word)のcanonical_form/surface_formが所有格
    "'s"(または複数所有格"s'")で終わる場合、所有格を取り除いた基本形へ
    正規化する。基本形の候補が既に別に存在する場合は所有格側を除去して
    重複させない(基本形側の候補を優先して残す)。"""
    cleaned = []
    seen_canonical = set()
    for c in word_survivors:
        canonical = c["canonical_form"]
        m = _POSSESSIVE_SUFFIX_RE.search(canonical)
        if m:
            stripped_canonical = canonical[:m.start()]
            stripped_surface = _POSSESSIVE_SUFFIX_RE.sub("", c.get("surface_form", canonical))
            if not stripped_canonical:
                continue
            c = dict(c)
            c["canonical_form"] = stripped_canonical
            c["surface_form"] = stripped_surface
            c["possessive_noise_stripped"] = True
        if c["canonical_form"] in seen_canonical:
            continue
        seen_canonical.add(c["canonical_form"])
        cleaned.append(c)
    return cleaned


# ------------------------------------------------------------
# Sentence units(raw文字列を保持したheading-aware文分割、context引用・
# occurrence計測・source_sentence検証整合のため。tokenize結果と1:1で
# 対応する順序を保証する)。
# ------------------------------------------------------------
def build_sentence_units(article_markdown: str) -> list:
    """er027.tokenize_sentences_heading_awareと同じブロック分割規則を
    使い、tokensとraw_text(記事中の実際の文字列、句読点・大文字小文字を
    保持)を同じ順序で1組ずつ返す。raw_textは既存validator
    (validate_min_unit_selection)のsource_sentence照合(本文への部分
    文字列一致)にそのまま使える形にする(見出し記号除去・スマート引用符
    正規化のみ、その他の文字は変更しない)。"""
    import unicodedata
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
        for raw_sentence in ext._SENTENCE_SPLIT_RE.split(joined):
            raw_sentence = raw_sentence.strip()
            if not raw_sentence:
                continue
            toks = _WORD_TOKEN_RE.findall(raw_sentence)
            if not toks:
                continue
            units.append({"tokens": toks, "raw_text": raw_sentence})
    return units


# ------------------------------------------------------------
# Stage 1メインエントリポイント(v3): er027の各パーツを再利用しつつ、
# bug A/B/Cの修正とsentence unit対応を組み込む。
# ------------------------------------------------------------
def run_stage1_for_article_v3(article_text: str, dbs: dict) -> dict:
    sentence_units = build_sentence_units(article_text)
    sentences_tokens = [u["tokens"] for u in sentence_units]
    cefr_j = dbs["cefr_j"]

    all_evidences = []
    irregular_rescued = []

    for sent_tokens in sentences_tokens:
        ngrams_local = ext.generate_ngrams([sent_tokens])
        for ng in ngrams_local:
            core = s1.match_candidate_with_irregular_rescue(ng, dbs)
            if core["db_match_count"] == 0:
                continue
            if core.get("irregular_verb_rescue"):
                irregular_rescued.append(dict(core))
            mismatch_rule = detect_context_mismatch_v3(
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
    word_survivors = strip_possessive_noise_from_word_survivors(word_survivors_raw)
    phrase_survivors_raw = [c for c in stage_b_survivors if c["unit_type"] != ext.UNIT_TYPE_WORD]
    phrase_survivors = s1.merge_near_duplicates(phrase_survivors_raw)
    phrase_survivors.sort(key=lambda c: (-c["db_match_count"], c["canonical_form"]))

    important_noun_candidates = s1.find_repeated_compound_noun_candidates(sentences_tokens, dbs)
    existing_canonicals = {c["canonical_form"] for c in phrase_survivors}
    important_noun_candidates = [c for c in important_noun_candidates
                                  if c["canonical_form"] not in existing_canonicals]

    import wordfreq

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


# ------------------------------------------------------------
# Compact context付与(occurrence count・sentence ID割当・sentence
# reference table構築)。Stage 2(LLM)へ渡すのは、この関数が返す
# compact shortlist + sentence reference tableのみであり、article全文
# は一切含まない。
# ------------------------------------------------------------
def _candidate_search_terms(c: dict) -> list:
    terms = list(c.get("observed_surface_variants") or [])
    if c.get("surface_form"):
        terms.append(c["surface_form"])
    if not terms:
        terms = [c["canonical_form"]]
    return sorted(set(terms), key=lambda t: (-len(t), t))


def attach_compact_context(shortlist: list, sentence_units: list) -> dict:
    """各候補について、記事内occurrence回数と、最初に出現した文の
    sentence ID(参照テーブルへの索引、重複文は1回だけ載せる)を付与する。
    戻り値: {"shortlist": [...], "sentence_reference": {sid: raw_text}}"""
    raw_lower = [u["raw_text"].lower() for u in sentence_units]
    sentence_reference = {}
    enriched = []
    for c in shortlist:
        terms = _candidate_search_terms(c)
        occurrence_count = 0
        first_sid = None
        for idx, low in enumerate(raw_lower):
            hit_here = False
            for term in terms:
                pattern = r"\b" + re.escape(term.lower()) + r"\b"
                n_hits = len(re.findall(pattern, low))
                if n_hits:
                    occurrence_count += n_hits
                    hit_here = True
            if hit_here and first_sid is None:
                first_sid = idx
        c = dict(c)
        c["occurrence_count_in_article"] = occurrence_count
        if first_sid is not None:
            sid_label = f"S{first_sid + 1}"
            c["context_sentence_id"] = sid_label
            sentence_reference[sid_label] = sentence_units[first_sid]["raw_text"]
        else:
            c["context_sentence_id"] = None
        enriched.append(c)
    return {"shortlist": enriched, "sentence_reference": sentence_reference}
