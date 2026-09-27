# ============================================================
# er032_key_phrase_db_hybrid_core_v2_trial_05_stage1.py
# KEY-PHRASE-DB-HYBRID-CORE-V2-TRIAL-05
# ============================================================
# KEY-PHRASE-DB-HYBRID-FAMILY-Z-CORE-APPLICABILITY-TRIAL-01
# (er031_*)で見つかった「Family Z固有ではなくCore共通の候補生成品質
# 課題」2件+ユーザー指示の3点目(proper noun/dialogue tag除外の明示化)
# を一般化して改善する。Family Z向け特殊化ではなく、Family X/Z共通の
# Core候補生成品質を上げることが目的(ユーザー指示)。
#
#   V2-1. word bucket ranking改善(生wordfreq屈折形バイアス低減):
#     既存`_word_rarity_key`(er027/er029、生surface形のzipf頻度で
#     昇順ソート)は、過去形/複数形等の屈折形が独立してカウントされる
#     ことで見かけ上の頻度が本来の語族頻度より低く出る(例:
#     "hurried"のzipfが本来の"hurry"より低い)ため、"loyalty"のような
#     無活用の重要語がword bucket枠(既定5枠)から溢れる(Family Z Trial
#     REPORT §4-2で発見、Core共通のranking方式そのものの弱点と判定
#     済み)。本ファイルはlemma正規化後の頻度(表層形+lemma候補群の中で
#     最も高いzipf頻度)を第一候補として使う`_lemma_normalized_word_
#     rarity_key`を新設する。新DBは追加しない(既存wordfreq+既存
#     er015 lemma化ロジックの範囲内)。
#
#   V2-2. multiword/idiom lookup改善(重要multiwordのlookup対象漏れ):
#     Wiktionary辞書のidiom見出しは、可変スロット(代名詞)を`one's`/
#     `one`/`someone`/`someone's`のプレースホルダで表す一般的な慣習が
#     あるが(例: 実データ確認、`Category:English idioms`に
#     `"one's place"`が存在)、既存の候補照合(lemma化のみ)は代名詞
#     スロットを吸収できず、本文中の実際の表現(例: "in his place")が
#     見出し(`one's place`)に一致しない(Family Z Trial REPORT §4-3で
#     発見)。本ファイルは代名詞プレースホルダ置換バリアントでの追加
#     照合(`match_candidate_with_pronoun_placeholder_rescue`)と、
#     Wiktionary live lookup候補選定の優先順位付け改善(単純なbudget増
#     ではなく、代名詞スロット・前置詞/助詞を伴うidiom/phrasal verb
#     形状の候補を優先する一般化、`select_unmatched_ngram_candidates_
#     for_lookup_v2`)を追加する。
#
#   V2-3. proper noun / dialogue tag除外の明示化:
#     既存の除外は「たまたまwordfreq実在語判定の閾値(zipf>=2.0)に
#     引っかからなかった」偶然の副産物であり(Family Z Trial REPORT
#     §4-4で発見、"echo"のように一般語と綴りが一致する固有名詞では
#     機能しない)、既存`apply_exclusion_gate`の`proper_noun`項目も
#     `rule_determined: False`(観測のみ、規則未実装)のままである。
#     本ファイルは、本文中の大文字化パターン(文頭以外での大文字始まり・
#     dialogue attribution動詞への隣接)から固有名詞らしさを判定する
#     一般的なヒューリスティック(`compute_proper_noun_signals`/
#     `is_proper_noun_like`)を新設し、(a) 1-gram候補(V2版Fix B)、
#     (b) 会話タグ形状の2-3gram(dialogue-tag-shape、"Echo said"等)、
#     (c) 単語バケット(group1 DB一致語)へ適用する。一般英単語と固有
#     名詞が同形の場合のfalse exclusion回避のため、本文中に小文字表記
#     での出現が一度でもあれば固有名詞判定しない(既存の真のphrase/
#     idiom・技術複合語[例: "Brent crude"]を保護するため、複合名詞
#     ヒューリスティックへの適用は「会話タグ形状(dialogue attribution
#     動詞への直接隣接)」に限定し、固有名詞を含むという理由だけでは
#     複合語候補を除外しない)。
#
# er023/er027/er028/er029/er030(v1 baseline)は一切変更しない
# (read-only import)。Fix A(sentence segmentation)はer029のv4実装を
# そのまま再利用する(無変更)。
# ============================================================

from __future__ import annotations

import re
from collections import Counter
from typing import Optional

import wordfreq

import er023_key_phrase_db_extraction as ext
import er027_key_phrase_db_hybrid_trial_02_stage1 as s1v2
import er028_key_phrase_db_hybrid_trial_03_stage1 as s1v3
import er029_key_phrase_db_hybrid_trial_04_stage1 as s1v4

_normalize_key = ext._normalize_key
_WORD_TOKEN_RE = ext._WORD_TOKEN_RE
_CLOSED = ext._CLOSED_CLASS_FUNCTION_WORDS

# Fix A(sentence segmentation、引用符を閉じた発話単位認識)はer029のまま
# 無変更で再利用する。
build_sentence_units = s1v4.build_sentence_units_v4


# ============================================================
# V2-3. proper noun / dialogue tag 判定(一般化した明示的機構)
# ============================================================

# 会話文の attribution(帰属)動詞の一般的な閉じたリスト(創作文体の一般
# 知識であり、個別作品・個別人物名のhardcodeではない)。
DIALOGUE_ATTRIBUTION_VERBS = {
    "said", "asked", "replied", "answered", "whispered", "shouted",
    "muttered", "murmured", "exclaimed", "cried", "called", "announced",
    "declared", "insisted", "argued", "protested", "agreed", "objected",
    "remarked", "observed", "noted", "stated", "interrupted", "repeated",
    "warned", "begged", "pleaded", "demanded", "ordered", "suggested",
    "proposed", "questioned", "inquired", "sighed", "laughed", "nodded",
    "yelled", "screamed", "snapped", "grumbled", "wondered", "continued",
    "added",
}


_MIN_NONINITIAL_CAPITALIZED_REPETITION = 2


def compute_proper_noun_signals(sentence_units: list) -> dict:
    """本文全体(sentence_unit群)から、トークン(小文字key)ごとの
    固有名詞らしさシグナルを集計する。
    - has_lowercase_occurrence: 本文中に小文字表記での出現が1回でも
      あるか(あれば「一般語と同形の固有名詞」false exclusion回避の
      ための安全策として、固有名詞とは判定しない)。
    - noninitial_capitalized_occurrence_count: 文頭以外の位置で大文字
      始まりの出現が何回あるか(通常の英文法では文頭以外の大文字始まり
      は固有名詞の強いシグナルだが、引用符内の発話冒頭の語[会話タグの
      直後に続く感嘆・命令、例:「shouted, "Wait!"」の"Wait"]は既存の
      文分割[Fix A、カンマは文境界にしない]の都合上「文頭以外」扱いに
      なる一方、記事中で1回しか出現しない偶然の産物であることが実データ
      で判明した。登場人物名は記事中で繰り返し・複数の文位置に出現する
      という一般的な性質を踏まえ、2回以上の「文頭以外の大文字始まり」
      出現を要求することでこの偶然を除外する)。
    - adjacent_to_dialogue_verb: 会話attribution動詞(直前または直後)
      に隣接する大文字始まりの出現があるか(dialogue tag形状の判定
      [`_ngram_is_dialogue_tag_shape`]で補助的に使う診断用シグナル)。"""
    signals: dict = {}
    for u in sentence_units:
        toks = u["tokens"]
        n = len(toks)
        for i, tok in enumerate(toks):
            if not tok.isalpha():
                continue
            key = tok.lower()
            entry = signals.setdefault(key, {
                "has_lowercase_occurrence": False,
                "noninitial_capitalized_occurrence_count": 0,
                "adjacent_to_dialogue_verb": False,
            })
            if tok[:1].islower():
                entry["has_lowercase_occurrence"] = True
            elif tok[:1].isupper() and i > 0:
                entry["noninitial_capitalized_occurrence_count"] += 1
            if tok[:1].isupper():
                prev_tok = toks[i - 1].lower() if i > 0 else None
                next_tok = toks[i + 1].lower() if i + 1 < n else None
                if prev_tok in DIALOGUE_ATTRIBUTION_VERBS or next_tok in DIALOGUE_ATTRIBUTION_VERBS:
                    entry["adjacent_to_dialogue_verb"] = True
    return signals


def is_proper_noun_like(key: str, signals: dict) -> bool:
    """1-token単位の固有名詞らしさ判定(本文中に小文字出現が一度でも
    あれば固有名詞とは判定しない=一般語と同形の固有名詞のfalse
    exclusion回避、例: "mark"という一般語の出現がある記事では"Mark"も
    固有名詞として除外しない)。判定の主軸は「文頭以外の位置での大文字
    始まり出現が2回以上」(実在の登場人物名は記事中で繰り返し・複数の
    文位置に出現するため成立する。1回限りの「文頭以外」出現は、引用符内
    発話冒頭の語が既存文分割の都合で偶然「文頭以外」扱いになる場合が
    あり[実データで発見]、固有名詞の判定根拠として使わない)。"""
    entry = signals.get(key)
    if not entry:
        return False
    if entry["has_lowercase_occurrence"]:
        return False
    return entry["noninitial_capitalized_occurrence_count"] >= _MIN_NONINITIAL_CAPITALIZED_REPETITION


def _ngram_is_dialogue_tag_shape(toks_lower: list, signals: dict) -> bool:
    """2-3gram候補が「固有名詞らしい語+会話attribution動詞」の隣接
    構成(会話タグ、例: "echo said"/"mara said")であるかを判定する。
    会話attribution動詞を含まないn-gram(例: "brent crude"のような
    既存の真の技術複合語)は対象外のため、この判定は既存の良い候補を
    誤って除外しない(固有名詞を含むという理由だけでは除外しない、
    会話タグという構造的形状に限定した除外)。"""
    for i, t in enumerate(toks_lower):
        if t not in DIALOGUE_ATTRIBUTION_VERBS:
            continue
        prev_t = toks_lower[i - 1] if i > 0 else None
        next_t = toks_lower[i + 1] if i + 1 < len(toks_lower) else None
        if (prev_t and is_proper_noun_like(prev_t, signals)) or \
                (next_t and is_proper_noun_like(next_t, signals)):
            return True
    return False


# ============================================================
# V2-1. word bucket ranking改善(lemma正規化後の頻度を第一候補に使う)
# ============================================================

def _extra_lemma_candidates_for_ranking(key: str) -> list:
    """既存er015 lemma_candidates_v2(er023.lemma_candidates_for_word
    経由、無変更のまま再利用)が捕捉できない「子音+y→ied」型の一般的な
    英語過去形綴り規則(例: hurry→hurried、carry→carried、
    marry→married、worry→worried)を、word bucket ranking専用に補う
    (個別語のhardcodeではなく英語綴り規則の一般知識、既存er015自体は
    無変更)。"""
    cands = []
    if key.endswith("ied") and len(key) > 4:
        cands.append(key[:-3] + "y")
    return cands


def _lemma_normalized_word_rarity_key(canonical_form: str):
    """屈折形(過去形・複数形等)のwordfreq分割による見かけ上の低頻度化
    バイアスを減らすため、表層形自身に加えlemma候補群の中で最も高い
    zipf頻度(=その語族の最も確立した使われ方の頻度)を採用する。lemma
    候補が無い語(loyaltyのような無活用の名詞等)は表層形のzipfのまま
    変わらない(既存v1の挙動を包含する上位互換)。"""
    variants = {canonical_form}
    variants.update(ext.lemma_candidates_for_word(canonical_form))
    variants.update(_extra_lemma_candidates_for_ranking(canonical_form))
    best_zf = 0.0
    for v in variants:
        try:
            zf = wordfreq.zipf_frequency(v, "en")
        except Exception:
            zf = 0.0
        if zf > best_zf:
            best_zf = zf
    return (best_zf, canonical_form)


# ============================================================
# V2-2. multiword/idiom lookup改善
# ============================================================

_POSSESSIVE_PRONOUNS = {"my", "your", "his", "her", "its", "our", "their"}
_OBJECT_OR_SUBJECT_PRONOUNS = {
    "me", "you", "him", "her", "it", "us", "them", "i", "he", "she", "we", "they",
}
# 前置詞・助詞で始まる/終わる候補を優先シグナルにする初期案は、実データ
# (hormuz_a2で2-3gram全体528件中162件)で粗すぎることが判明したため
# 不採用とした(下記select_unmatched_ngram_candidates_for_lookup_v2の
# docstring参照)。定数自体もこのファイルでは使用しない。


def _pronoun_placeholder_variants(surface_tokens: list) -> list:
    """英語辞書のidiom見出しは可変スロット(代名詞)を`one's`/`one`/
    `someone`/`someone's`のプレースホルダで表す一般的な慣習がある
    (実データ確認: Wiktionary`Category:English idioms`ローカルdumpに
    `"one's place"`が存在、"in his place"/"in her place"等の実際の
    代名詞入り表現を代表する見出し)。本文中の実際の代名詞を機械的に
    プレースホルダへ置換したバリアントを生成する(個別idiomのhardcode
    ではなく、英語辞書の一般的な見出し慣習を踏まえた一般化)。"""
    lower_tokens = [t.lower() for t in surface_tokens]
    variants = []
    for i, tok in enumerate(lower_tokens):
        if tok in _POSSESSIVE_PRONOUNS:
            placeholders = ("one's", "someone's")
        elif tok in _OBJECT_OR_SUBJECT_PRONOUNS:
            placeholders = ("one", "someone")
        else:
            continue
        for ph in placeholders:
            v = list(lower_tokens)
            v[i] = ph
            variants.append(" ".join(v))
    return variants


def match_candidate_with_pronoun_placeholder_rescue(ngram: dict, dbs: dict) -> dict:
    """既存の不規則動詞rescue(s1v2.match_candidate_with_irregular_
    rescue、無変更のまま再利用)を先に試し、それでも不一致
    (db_match_count==0)かつn>=2の場合のみ、代名詞プレースホルダ置換
    バリアントで群1DB(cefr_j multiword/wiktionary)への追加照合を試みる。
    一致すればidiom/phrasal_verb等の分類を反映するが、元のsurface_form/
    canonical_formは変更しない(表示・validator照合は本文中の実際の
    表現のまま、既存irregular_verb_rescueと同じ設計方針)。"""
    core = dict(s1v2.match_candidate_with_irregular_rescue(ngram, dbs))
    core["pronoun_placeholder_rescue"] = False
    if core["db_match_count"] > 0 or ngram["n"] < 2:
        return core

    variants = _pronoun_placeholder_variants(ngram["surface_tokens"])
    if not variants:
        return core

    matched_dbs, db_categories, cefr_level = set(), set(), None
    matched_variant = None
    for v in variants:
        if v in dbs["cefr_j"] and dbs["cefr_j"][v]["is_multiword"]:
            matched_dbs.add("cefr_j")
            cefr_level = cefr_level or dbs["cefr_j"][v]["cefr"]
            matched_variant = matched_variant or v
        if v in dbs["wiktionary"]:
            matched_dbs.add("wiktionary")
            db_categories.update(dbs["wiktionary"][v]["categories"])
            matched_variant = matched_variant or v

    if not matched_dbs:
        return core

    core["matched_dbs"] = sorted(matched_dbs)
    core["db_match_count"] = len(matched_dbs)
    core["db_categories"] = sorted(db_categories)
    core["cefr_level"] = cefr_level
    core["pronoun_placeholder_rescue"] = True
    core["pronoun_placeholder_variant_matched"] = matched_variant
    unit_type = ext.UNIT_TYPE_PHRASE
    if "phrasal_verb" in db_categories:
        unit_type = ext.UNIT_TYPE_PHRASAL_VERB
    elif "idiom" in db_categories:
        unit_type = ext.UNIT_TYPE_IDIOM
    elif "proverb" in db_categories:
        unit_type = ext.UNIT_TYPE_DISCOURSE
    core["unit_type"] = unit_type
    return core


_PRONOUN_SLOT_RESERVED_SUBBUDGET = 15


def select_unmatched_ngram_candidates_for_lookup_v2(sentences: list, existing_canonical_forms: set,
                                                     budget: int = 60) -> list:
    """既存er027.select_unmatched_ngram_candidates_for_lookupと同じ収集
    条件・同じ既定の優先順位(len昇順→content語数降順→アルファベット順)を
    維持しつつ、代名詞スロット(his/her/my等)を含む候補(idiomの可変
    スロットである可能性が高い、英語の一般的な語形特徴)だけを、budget内の
    小さな予約枠(既定15、budgetの小部分)で優先する。

    設計上の注意(実データ検証で判明): 前置詞・助詞(in/on/back/over等)
    で始まる/終わる候補を優先候補に含める初期案は、2-3gram全体の
    過半数(実データ確認: hormuz_a2で528件中162件)を占めるほど粗い
    シグナルであり、優先枠を無制限にすると既存の良い候補("Brent
    crude"等、v1では528件中12位相当で楽に budget=60 内に入っていた)を
    budget外へ押し出してしまうことが実データで判明した。そのため
    優先シグナルは「代名詞スロットを含む」という、より狭く再現性の高い
    idiom形状シグナルに限定し、かつ予約枠を小さく固定することで、
    既存の良い候補への影響を最小限にする(単純なbudget増ではなく質改善、
    ただし既存候補を壊さない範囲に限定した保守的な質改善)。"""
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

    def _v1_sort_key(s):
        return (len(s.split()), -_content_count(s), s.lower())

    def _has_pronoun_slot(s):
        toks_lower = s.lower().split()
        return any(t in _POSSESSIVE_PRONOUNS or t in _OBJECT_OR_SUBJECT_PRONOUNS for t in toks_lower)

    all_candidates = list(seen.values())
    pronoun_slot_candidates = sorted((s for s in all_candidates if _has_pronoun_slot(s)), key=_v1_sort_key)
    reserved = pronoun_slot_candidates[:min(_PRONOUN_SLOT_RESERVED_SUBBUDGET, budget)]
    reserved_set = set(reserved)

    remaining_budget = max(0, budget - len(reserved))
    rest = sorted((s for s in all_candidates if s not in reserved_set), key=_v1_sort_key)
    return reserved + rest[:remaining_budget]


# ============================================================
# V2-3(続き). find_repeated_compound_noun_candidates v2
# (会話タグ形状の除外のみ追加、それ以外は既存er027ロジックのまま)
# ============================================================

def find_repeated_compound_noun_candidates_v2(sentence_units: list, dbs: dict, signals: dict,
                                               min_repetition: int = 2, max_n: int = 3) -> list:
    """既存er027.find_repeated_compound_noun_candidatesと同じ収集条件に、
    会話タグ形状(dialogue-tag-shape)除外ガードを追加する(例: "echo
    said"のような2-gramが偶然wordfreq閾値をすり抜けて候補化されるのを
    防ぐ)。既存の真のphrase/idiom・技術複合語("Brent crude"等)は
    会話attribution動詞を含まないため対象外のまま保持される。"""
    counter = Counter()
    surface_by_merge_key = {}
    first_seen_source = {}
    cefr_j = dbs["cefr_j"]

    for u in sentence_units:
        sent_tokens = u["tokens"]
        ngrams_local = ext.generate_ngrams([sent_tokens], min_n=2, max_n=max_n)
        for ng in ngrams_local:
            toks = ng["surface_tokens"]
            toks_lower = [t.lower() for t in toks]
            if any(t in _CLOSED for t in toks_lower):
                continue
            if not all(s1v2._is_real_content_word(t) for t in toks):
                continue
            if not all(s1v2._is_plausible_noun_component(t, cefr_j) for t in toks):
                continue
            if _ngram_is_dialogue_tag_shape(toks_lower, signals):
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


# ============================================================
# V2-3(続き). Fix B(rare single word)のproper noun/dialogue tag gate版
# ============================================================

def _unigram_candidate_reason_v2(key: str, entry: dict, dbs: dict, signals: dict) -> Optional[str]:
    """er029_stage1._unigram_candidate_reasonと同じ形態素/頻度条件・同じ
    固有名詞除外ガード(「本文中に小文字出現が一度もない語は対象外」、
    v1のまま無変更)を使う。Fix B(1-gram)はgroup1 DB不一致(=辞書に
    無い語)専用の経路であり、実データ検証の結果、この簡易ガードは
    Dionysius/Selinuntius(記事中1回しか出現しない固有名詞)を正しく
    除外できる一方、`is_proper_noun_like`(文頭以外の大文字始まり2回以上
    要求)へ差し替えると1回しか出現しない固有名詞を誤って許してしまう
    ことが分かったため、Fix Bではv1のガードを維持する(固有名詞
    除外の一般化=`is_proper_noun_like`はword_survivors・会話タグ形状
    複合語gateという別経路[下記]に適用する)。"""
    if key in _CLOSED:
        return None
    if not s1v4._UNIGRAM_CANDIDATE_TOKEN_RE.match(key):
        return None
    if len(key.replace("-", "")) < s1v4._MIN_RARE_WORD_LETTER_LEN:
        return None
    if not entry["has_lowercase_occurrence"]:
        return None
    ngram = {"n": 1, "surface_tokens": [key], "surface_form": key}
    core = ext.match_candidate_against_group1(ngram, dbs)
    if core["db_match_count"] > 0:
        return None
    if s1v4._has_rare_morphology(key):
        return "morphology"
    try:
        zf = wordfreq.zipf_frequency(key, "en")
    except Exception:
        zf = 0.0
    if zf <= 0:
        return "frequency_unknown"
    if zf < s1v4._RARE_WORD_ZIPF_THRESHOLD:
        return "frequency_known_rare"
    return None


def select_rare_single_word_candidates_v2(sentence_units: list, dbs: dict, signals: dict,
                                          article_title: str = "", budget: int = 15) -> list:
    """er029_stage1.select_rare_single_word_candidatesと同じ枠組みだが、
    採否判定に`_unigram_candidate_reason_v2`(proper noun/dialogue tag
    明示ガード版)を使う。"""
    info = s1v4._iter_unigram_occurrences(sentence_units)
    title_keys = {_normalize_key(t) for t in _WORD_TOKEN_RE.findall(article_title or "")}

    eligible = []
    for k, e in info.items():
        reason = _unigram_candidate_reason_v2(k, e, dbs, signals)
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


# wiktionary lemma lookup / evidence構築はer029のまま無変更で再利用
# (proper noun候補は既に_unigram_candidate_reason_v2で除外済みのため、
# frequency_unknown区分のWiktionary確認gateはv1と同じロジックでよい)。
wiktionary_unigram_lemma_lookup = s1v4.wiktionary_unigram_lemma_lookup
build_rare_single_word_evidences = s1v4.build_rare_single_word_evidences


# ============================================================
# Stage 1 メインエントリポイント(Core v2)
# ============================================================

def run_stage1_for_article_core_v2(article_text: str, dbs: dict) -> dict:
    """er029.run_stage1_for_article_v4と同じ全体構造(Fix A適用済み
    sentence分割→1-5gram生成→群1DB照合[V2-2: 代名詞プレースホルダ
    rescue追加]→除外Gate→word/phrase振り分け[V2-3: proper noun gate
    追加]→重要複合名詞検出[V2-3: 会話タグ形状除外]→word bucket
    ranking[V2-1: lemma正規化頻度])を実装する。"""
    sentence_units = build_sentence_units(article_text)
    sentences_tokens = [u["tokens"] for u in sentence_units]
    cefr_j = dbs["cefr_j"]
    signals = compute_proper_noun_signals(sentence_units)

    all_evidences = []
    irregular_rescued = []
    pronoun_placeholder_rescued = []

    for sent_tokens in sentences_tokens:
        ngrams_local = ext.generate_ngrams([sent_tokens])
        for ng in ngrams_local:
            core = match_candidate_with_pronoun_placeholder_rescue(ng, dbs)
            if core["db_match_count"] == 0:
                continue
            if core.get("irregular_verb_rescue"):
                irregular_rescued.append(dict(core))
            if core.get("pronoun_placeholder_rescue"):
                pronoun_placeholder_rescued.append(dict(core))
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
    # V2-3: word候補にproper noun gateを適用(一般語と同形の固有名詞の
    # みが本文中で使われている場合[小文字出現が一度もない場合]に除外)。
    proper_noun_excluded_words = [c for c in word_survivors_raw
                                   if is_proper_noun_like(c["canonical_form"], signals)]
    word_survivors_raw = [c for c in word_survivors_raw
                          if not is_proper_noun_like(c["canonical_form"], signals)]
    word_survivors = s1v3.strip_possessive_noise_from_word_survivors(word_survivors_raw)
    phrase_survivors_raw = [c for c in stage_b_survivors if c["unit_type"] != ext.UNIT_TYPE_WORD]
    phrase_survivors = s1v2.merge_near_duplicates(phrase_survivors_raw)
    phrase_survivors.sort(key=lambda c: (-c["db_match_count"], c["canonical_form"]))

    important_noun_candidates = find_repeated_compound_noun_candidates_v2(sentence_units, dbs, signals)
    existing_canonicals = {c["canonical_form"] for c in phrase_survivors}
    important_noun_candidates = [c for c in important_noun_candidates
                                  if c["canonical_form"] not in existing_canonicals]

    word_survivors_sorted = sorted(word_survivors, key=lambda c: _lemma_normalized_word_rarity_key(
        c["canonical_form"]))

    return {
        "sentence_units": sentence_units,
        "tokens_total": sum(len(u["tokens"]) for u in sentence_units),
        "sentences_total": len(sentence_units),
        "before_dedup_count": before_dedup_count,
        "after_dedup_count": len(deduped),
        "stage_a_excluded_by_existing_gate_count": len(stage_a_excluded_by_existing_gate),
        "stage_a_survivors_count": len(stage_a_survivors),
        "irregular_verb_rescued_count": len(irregular_rescued),
        "pronoun_placeholder_rescued_count": len(pronoun_placeholder_rescued),
        "pronoun_placeholder_rescued": pronoun_placeholder_rescued,
        "context_mismatch_excluded": context_mismatch_excluded,
        "context_mismatch_excluded_count": len(context_mismatch_excluded),
        "stage_b_survivors_count": len(stage_b_survivors),
        "word_survivors": word_survivors_sorted,
        "phrase_survivors": phrase_survivors,
        "important_noun_candidates": important_noun_candidates,
        "proper_noun_signals_summary": {
            "flagged_keys": sorted(k for k in signals if is_proper_noun_like(k, signals)),
        },
        "proper_noun_excluded_words": [c["canonical_form"] for c in proper_noun_excluded_words],
    }


# attach_compact_contextはer028(v3)を無変更のまま再利用する。
attach_compact_context = s1v3.attach_compact_context
