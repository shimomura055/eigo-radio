# FAMILY-X-KP-EXTRACTION-SELECTION-OPTIMIZATION-01 委任_01A (Phase 1-A): Trial専用コア。
# Production非接続: 既存Production関数(er030/er027/er023)は「読取・呼出」のみ。ファイル改変なし。
# process内のmonkeypatchはcontext manager内に限定し、終了時に必ず復元する。
# 有料LLM呼出なし。Wiktionary公開API(無料)のみ、既存関数と同じ1回50件・待ち1.5秒を踏襲し、結果はsnapshotへ保存。
import contextlib
import datetime
import hashlib
import inspect
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.getcwd())
import wordfreq  # noqa: E402

import er023_key_phrase_db_extraction as ext  # noqa: E402
import er023_key_phrase_db_ingest as ing  # noqa: E402
import er027_key_phrase_db_hybrid_trial_02_stage1 as s1v2  # noqa: E402
import er030_key_phrase_db_hybrid_core_01 as core  # noqa: E402
import er030_key_phrase_db_hybrid_source_reference_contract_01 as contract  # noqa: E402

OUT_DIR = "er064_output/kp_extraction_selection_opt_01/phase1_a"
SNAPSHOT_PATH = OUT_DIR + "/wiktionary_snapshot_01.json"

# 記事 x Level (Std=a2, Adv=b1b)。Coffee + Family X既存4テーマ = 5記事。
ARTICLES = {
    "coffee_std": "er019_output/coffee_prices/run_v5_ms_01/a2/article.md",
    "coffee_adv": "er019_output/coffee_prices/run_v5_ms_01/b1b/article.md",
    "meta_std": "er019_output/meta/run_03/a2/article.md",
    "meta_adv": "er019_output/meta/run_03/b1b/article.md",
    "hormuz_std": "er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/a2/article.md",
    "hormuz_adv": "er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/b1b/article.md",
    "smallbag_std": "er019_output/family_x_b3_diversity_trial_01/small_bag/run_02/a2/article.md",
    "smallbag_adv": "er019_output/family_x_b3_diversity_trial_01/small_bag/run_02/b1b/article.md",
    "semi_std": "er019_output/semiconductor_earnings/run_devconfirm_01/a2/article.md",
    "semi_adv": "er019_output/semiconductor_earnings/run_devconfirm_01/b1b/article.md",
}
TITLES = {  # article_title (rare word title_related優先用)。Phase1では本文テーマ語のみ。
    "coffee": "Coffee prices", "meta": "Meta", "hormuz": "Strait of Hormuz", "smallbag": "Small bag", "semi": "Semiconductor earnings",
}
CLOSED = ext._CLOSED_CLASS_FUNCTION_WORDS
BATCH_SIZE = 50
SLEEP_SEC = 1.5
THREEGRAM_CAP = 100  # 「3語は上限付き」の上限(Trial既定)

ORIG_MW = ing.wiktionary_multiword_targeted_lookup
ORIG_UNI = core.wiktionary_unigram_lemma_lookup
ORIG_SELECT = s1v2.select_unmatched_ngram_candidates_for_lookup


def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def sha256_text(s):
    return hashlib.sha256(s.encode("utf8")).hexdigest()


def sha256_file(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def read_article(key):
    return open(ARTICLES[key], encoding="utf8").read()


def article_theme(key):
    return key.rsplit("_", 1)[0]


# ------------------------------------------------------------
# snapshot (cache + 再現性)
# ------------------------------------------------------------
class Snapshot:
    KINDS = ("multiword", "multiword_lower", "unigram")

    def __init__(self, path=SNAPSHOT_PATH):
        self.path = path
        if os.path.exists(path):
            self.d = json.load(open(path, encoding="utf8"))
        else:
            self.d = {"meta": {"created": now_iso(), "purpose": "KP-OPT-01 Phase1-A Wiktionary照会snapshot(Trial専用、Production state非接続)",
                               "batch_size": BATCH_SIZE, "sleep_sec": SLEEP_SEC,
                               "endpoint": ing.WIKTIONARY_API, "category_multiword": "Category:English multiword terms",
                               "category_unigram": "Category:English lemmas"},
                      "multiword": {}, "multiword_lower": {}, "unigram": {}, "batches": [], "http429_total": 0}
        self.http429_this_process = 0

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        json.dump(self.d, open(self.path, "w", encoding="utf8"), ensure_ascii=False, indent=1, sort_keys=True)

    def has(self, kind, t):
        return t in self.d[kind]

    def hit(self, kind, t):
        return bool(self.d[kind][t]["hit"])

    def _count_429_urlopen(self):
        orig = urllib.request.urlopen
        me = self

        def wrapped(*a, **k):
            try:
                return orig(*a, **k)
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    me.http429_this_process += 1
                    me.d["http429_total"] += 1
                raise
        return orig, wrapped

    def fetch(self, kind, titles, allow_net):
        missing = sorted({t for t in titles if t not in self.d[kind]})
        if not missing:
            return
        if not allow_net:
            raise RuntimeError(f"snapshot miss ({kind}) {len(missing)} titles, e.g. {missing[:3]}: replay mode forbids network")
        fn = ORIG_UNI if kind == "unigram" else ORIG_MW
        orig, wrapped = self._count_429_urlopen()
        urllib.request.urlopen = wrapped
        try:
            r429_before = self.http429_this_process
            res = fn(missing, batch_size=BATCH_SIZE, sleep_sec=SLEEP_SEC)
        finally:
            urllib.request.urlopen = orig
        ts = now_iso()
        for t, h in res["results"].items():
            self.d[kind][t] = {"hit": bool(h), "ts": ts}
        self.d["batches"].append({"kind": kind, "n": len(missing), "api_calls": res["api_calls"], "elapsed_sec": res["elapsed_sec"],
                                  "http429": self.http429_this_process - r429_before, "ts": ts})
        self.save()

    # --- monkeypatch用の差し替え関数(既存関数と同じ戻り値形式) ---
    def make_mw_lookup(self, allow_net=False):
        def fn(candidates, batch_size=50, sleep_sec=1.5):
            uniq = sorted(set(candidates))
            self.fetch("multiword", uniq, allow_net)
            return {"results": {c: self.hit("multiword", c) for c in uniq}, "api_calls": math.ceil(len(uniq) / BATCH_SIZE) if uniq else 0,
                    "elapsed_sec": 0.0, "candidate_count": len(uniq)}
        return fn

    def make_uni_lookup(self, allow_net=True):
        def fn(candidates, batch_size=50, sleep_sec=1.5):
            uniq = sorted(set(candidates))
            self.fetch("unigram", uniq, allow_net)
            return {"results": {c: self.hit("unigram", c) for c in uniq}, "api_calls": math.ceil(len(uniq) / BATCH_SIZE) if uniq else 0,
                    "elapsed_sec": 0.0, "candidate_count": len(uniq)}
        return fn

    def batch_stats(self, kind="multiword"):
        bs = [b for b in self.d["batches"] if b["kind"] == kind and b["api_calls"] > 0]
        calls = sum(b["api_calls"] for b in bs)
        el = sum(b["elapsed_sec"] for b in bs)
        sleeps = sum(max(0, b["api_calls"] - 1) for b in bs) * SLEEP_SEC
        lat = (el - sleeps) / calls if calls else None
        return {"api_calls": calls, "elapsed_sec": round(el, 2), "mean_request_latency_sec": round(lat, 3) if lat is not None else None,
                "http429": sum(b["http429"] for b in bs)}


def estimate_lookup_seconds(n_candidates, latency):
    """n件の照会に必要なcall数と所要時間の推定(1回50件、回間sleep 1.5秒、latencyは実測した1call平均)。"""
    calls = math.ceil(n_candidates / BATCH_SIZE) if n_candidates else 0
    if not calls:
        return 0, 0.0
    return calls, round(calls * (latency or 1.0) + (calls - 1) * SLEEP_SEC, 1)


@contextlib.contextmanager
def patched(order_fn, snap, allow_net_mw=False, allow_net_uni=True):
    saved = (s1v2.select_unmatched_ngram_candidates_for_lookup, ing.wiktionary_multiword_targeted_lookup, core.wiktionary_unigram_lemma_lookup)
    s1v2.select_unmatched_ngram_candidates_for_lookup = order_fn
    ing.wiktionary_multiword_targeted_lookup = snap.make_mw_lookup(allow_net_mw)
    core.wiktionary_unigram_lemma_lookup = snap.make_uni_lookup(allow_net_uni)
    try:
        yield
    finally:
        (s1v2.select_unmatched_ngram_candidates_for_lookup, ing.wiktionary_multiword_targeted_lookup,
         core.wiktionary_unigram_lemma_lookup) = saved


# ------------------------------------------------------------
# 照会プール順序 (現行 / U1各種)
# ------------------------------------------------------------
def _norm_tok(t):
    return ext._normalize_key(t)


def proper_noun_tokens(sentences):
    """固有名詞らしいtoken(小文字)集合: 先頭大文字で、(文頭以外に出現)または(小文字形が記事中に一度も現れない)もの。ヒューリスティック。"""
    lower_seen = set()
    cap_nonfirst = set()
    cap_first_only = set()
    for toks in sentences:
        for i, t in enumerate(toks):
            if not t[:1].isalpha():
                continue
            if t == t.lower():
                lower_seen.add(t)
            elif t[0].isupper():
                (cap_nonfirst if i > 0 else cap_first_only).add(t.lower())
    return {t for t in cap_nonfirst if t not in lower_seen} | {t for t in cap_first_only if t not in lower_seen and t not in CLOSED}


def _pool_by_default(sentences, existing):
    return ORIG_SELECT(sentences, existing, budget=10 ** 7)


def make_order_fn(mode, rare_words, k=10, budget_override=None):
    """mode:
       default      : 現行(語数昇順・内容語数降順・alphabet)
       u1           : 希少語(上位k)を含む2語を先頭 (固有名詞を含む2語も優先)
       u1np         : 同上、固有名詞らしいtokenを含む2語は優先しない(通常順位のまま)
       u1np3        : u1np + 希少語を含む3語を優先2語の後ろ(優先総数は最大45)
       返す関数は select_unmatched_ngram_candidates_for_lookup と同じシグネチャ。budgetは呼出側が渡す値(または budget_override)。"""
    rare = [w for w in rare_words[:k]]
    rare_set = set(rare)

    def has_rare(surface):
        return any((t.lower() in rare_set) or (_norm_tok(t) in rare_set) for t in surface.split())

    def fn(sentences, existing, budget=40):
        pool = _pool_by_default(sentences, existing)
        if mode == "default":
            ordered = pool
        else:
            props = proper_noun_tokens(sentences) if mode in ("u1np", "u1np3") else set()

            def is_prop(s):
                return any(t.lower() in props for t in s.split())
            pri2 = [s for s in pool if len(s.split()) == 2 and has_rare(s) and not is_prop(s)]
            pri3 = []
            if mode == "u1np3":
                pri3 = [s for s in pool if len(s.split()) == 3 and has_rare(s) and not is_prop(s)][: max(0, 45 - len(pri2))]
            pri = pri2 + pri3
            ps = set(pri)
            ordered = pri + [s for s in pool if s not in ps]
        b = budget_override if budget_override is not None else budget
        return ordered[:b]
    fn.mode = mode
    return fn


def pool_for_article(stage1):
    ex = ({c["canonical_form"] for c in stage1["phrase_survivors"]} | {c["canonical_form"] for c in stage1["important_noun_candidates"]} |
          {c["canonical_form"] for c in stage1["word_survivors"]})
    sents = [u["tokens"] for u in stage1["sentence_units"]]
    return _pool_by_default(sents, ex), sents, ex


# ------------------------------------------------------------
# 候補の関係・断片 (U2 / U3)
# ------------------------------------------------------------
_TOK_RE = ext._WORD_TOKEN_RE


def _stem(t):
    t = t.lower()
    t = re.sub(r"(?:'s|s')$", "", t)
    for s in ("ing", "ed", "es", "s"):
        if t.endswith(s) and len(t) - len(s) >= 3:
            return t[: -len(s)]
    return t


def stem_tokens(surface):
    return [_stem(t) for t in _TOK_RE.findall(surface)]


def occurrences(sentence_stems, seq):
    """sentence_stems: list[list[stem]]、seq: list[stem]。戻り: [(sent_idx, start)]"""
    n = len(seq)
    res = []
    if n == 0:
        return res
    for si, st in enumerate(sentence_stems):
        for i in range(0, len(st) - n + 1):
            if st[i:i + n] == seq:
                res.append((si, i))
    return res


def is_dictionary_registered(c):
    """辞書登録(Wiktionary見出し/online hit)の判定。ヒューリスティック(repeated_compound_noun等)・cefr_jのみは未登録扱い。"""
    return "wiktionary" in (c.get("matched_dbs") or [])


def compute_containment(cands, sentence_units):
    """各候補(shortlist内)について、含む/含まれる関係と Tier-H(word整理対象)を機械算出。
    戻り: {"pairs":[{small,big,small_type,big_registered,all_small_occurrences_inside_big,tier}], }"""
    sent_stems = [[_stem(t) for t in u["tokens"]] for u in sentence_units]
    info = []
    for c in cands:
        seq = stem_tokens(c["surface_form"])
        info.append({"c": c, "seq": seq, "occ": occurrences(sent_stems, seq)})
    pairs = []
    for a in info:
        for b in info:
            if a is b or len(a["seq"]) >= len(b["seq"]) or not a["seq"]:
                continue
            # a ⊂ b (連続token列)
            inside = [(si, i) for (si, i) in b["occ"]]
            covered = set()
            for (si, i) in inside:
                for off in range(len(b["seq"])):
                    covered.add((si, i + off))
            contained_any = any(b["seq"][j:j + len(a["seq"])] == a["seq"] for j in range(len(b["seq"]) - len(a["seq"]) + 1))
            if not contained_any:
                continue
            # aの各出現がbの出現の内側に収まるか
            a_occs = a["occ"]
            # a_occs are positions in sentences of a; check coverage
            all_inside = bool(a_occs) and all(all((si, i + off) in covered for off in range(len(a["seq"]))) for (si, i) in a_occs)
            small_is_word = a["c"].get("unit_type") == "word"
            reg = is_dictionary_registered(b["c"])
            tier = "H" if (small_is_word and reg and all_inside) else "S"
            pairs.append({"small": a["c"]["canonical_form"], "big": b["c"]["canonical_form"], "small_unit_type": a["c"].get("unit_type"),
                          "big_registered": reg, "all_small_occurrences_inside_big": all_inside, "tier": tier})
    return pairs


FRAG_START = {"a", "an", "the", "of", "in", "on", "at", "to", "for", "from", "by", "with", "into", "onto", "about", "as", "and", "or", "but",
              "so", "than", "that", "is", "are", "was", "were", "be", "been", "being", "do", "does", "did", "has", "have", "had", "can", "could",
              "may", "might", "must", "should", "will", "would"}


def all_closed_only(surface):
    toks = [t.lower() for t in _TOK_RE.findall(surface)]
    return bool(toks) and all(t in CLOSED for t in toks)


def fragment_risk(surface, registered):
    """U3(ii): 辞書未登録かつ先頭が閉じた語類(前置詞/冠詞/助動詞/接続詞)の複数語 -> 注釈のみ(置換しない)。"""
    toks = [t.lower() for t in _TOK_RE.findall(surface)]
    return bool(len(toks) >= 2 and toks[0] in FRAG_START and not registered)


# ------------------------------------------------------------
# shortlist組立 (U2/U3/U4をstackable flagで)
# ------------------------------------------------------------
def _first_pos(cand, sentence_units):
    seq = stem_tokens(cand["surface_form"])
    for si, u in enumerate(sentence_units):
        st = [_stem(t) for t in u["tokens"]]
        n = len(seq)
        for i in range(0, len(st) - n + 1):
            if st[i:i + n] == seq:
                return (si, i)
    return (10 ** 6, 0)


def is_online_multiword_hit(c):
    return c.get("matched_dbs") == ["wiktionary"] and c.get("db_categories") == ["multiword_term"]


def assemble_shortlist(stage1_after_lookup, *, phrase_cap=15, realign=False, tiebreak_pos=False, u3_exclude=False, u3_annotate=False,
                       u2="none", dbs=None, demoted_allow=None):
    """run_stage1_and_shortlist(patched)が返したstage1(= demoted_to_phrase付与済み)を受けて、U2/U3/U4を適用した
    shortlist_infoを返す。u2: none / tierH+S / tierS。realign: demoted_to_phraseを含むphrase_survivorsを(-db_match_count, canonical)へ整列し直す。
    tiebreak_pos: 同値内を本文の出現順にする(U4(b))。Production関数のbuild_shortlistを再利用する。"""
    st = dict(stage1_after_lookup)
    phrases = list(st["phrase_survivors"])
    excluded_u3 = []
    if demoted_allow is not None:
        # 精度ガード(Trial比較用): 現行の照会窓(予算60)の外で新規に拾った「名詞句判定で外れたhit(demoted)」はphraseへ入れない。
        # important判定のhit(time lag等)は影響を受けない。
        phrases = [c for c in phrases if not (is_online_multiword_hit(c) and c["canonical_form"] not in demoted_allow)]
    if u3_exclude:
        keep = []
        for c in phrases:
            if all_closed_only(c["surface_form"]):
                excluded_u3.append(c["canonical_form"])
            else:
                keep.append(c)
        phrases = keep
    if realign or tiebreak_pos:
        if tiebreak_pos:
            phrases.sort(key=lambda c: (-c["db_match_count"], _first_pos(c, st["sentence_units"])))
        else:
            phrases.sort(key=lambda c: (-c["db_match_count"], c["canonical_form"]))
    st["phrase_survivors"] = phrases
    info = s1v2.build_shortlist(st, phrase_cap=phrase_cap)
    sl = list(info["shortlist"])
    removed_tier_h = []
    pairs = []
    if u2 in ("tierH+S", "tierS"):
        pairs = compute_containment(sl, st["sentence_units"])
        if u2 == "tierH+S":
            drop = {p["small"] for p in pairs if p["tier"] == "H"}
            # backfill: wordを削った分だけ次の希少word_survivorsを補う(shortlist word枠の件数を維持)
            before_words = sum(1 for c in sl if c["unit_type"] == "word" and not c.get("important_noun_phrase_candidate"))
            sl = [c for c in sl if c["canonical_form"] not in drop]
            removed_tier_h = sorted(drop)
            in_sl = {c["canonical_form"] for c in sl}
            n_words_now = sum(1 for c in sl if c["unit_type"] == "word" and not c.get("important_noun_phrase_candidate"))
            need = before_words - n_words_now
            if need > 0:
                for c in st["word_survivors"]:
                    if need <= 0:
                        break
                    if c["canonical_form"] in in_sl or c["canonical_form"] in drop:
                        continue
                    sl.append(c)
                    in_sl.add(c["canonical_form"])
                    need -= 1
                pairs = compute_containment(sl, st["sentence_units"])
    ctx = core.attach_compact_context(sl, st["sentence_units"])
    sl = ctx["shortlist"]
    for c in sl:
        c = c  # 注釈(候補dictへ非破壊に付与)
    out = []
    for c in sl:
        c2 = dict(c)
        if u3_annotate:
            c2["fragment_risk"] = fragment_risk(c2["surface_form"], is_dictionary_registered(c2) or c2["canonical_form"] in (dbs or {}).get("wiktionary", {}))
        out.append(c2)
    return {"shortlist": out, "sentence_reference": ctx["sentence_reference"], "containment_pairs": pairs, "u2_removed_tier_h": removed_tier_h,
            "u3_excluded_closed_only": excluded_u3,
            "counts": {"phrase": info["phrase_included_count"], "important": info["important_noun_included_count"],
                       "word": info["word_included_count"], "total": len(out)}}


def candidate_row_text(sl, sentence_reference, with_annotations=True, pairs=()):
    """選定LLMへ渡す候補行+SENTENCE REFERENCE部分の文字列(static_instructions空、実Promptと同じ整形関数を使用)。
    注釈(含む/含まれる、fragment_risk)は行末に追加した場合の増分を含める。"""
    wc = contract.assign_candidate_ids(sl)
    ids = {c["canonical_form"]: c["candidate_id"] for c in wc["shortlist_with_ids"]}
    contains, contained = {}, {}
    if with_annotations:
        for p in pairs:
            if p["small"] in ids and p["big"] in ids:
                contains.setdefault(p["big"], []).append(ids[p["small"]])
                contained.setdefault(p["small"], []).append(ids[p["big"]])

    import er030_key_phrase_db_hybrid_selector_01 as sel
    base_ev = sel._compact_evidence_string

    def ev(c):
        s = base_ev(c)
        if with_annotations:
            if c["canonical_form"] in contains:
                s += " | contains: " + ",".join(contains[c["canonical_form"]])
            if c["canonical_form"] in contained:
                s += " | contained_in: " + ",".join(contained[c["canonical_form"]])
            if c.get("fragment_risk"):
                s += " | fragment_risk"
        return s
    return contract.build_lightweight_user_message("T", wc["shortlist_with_ids"], sentence_reference, "", "family_x", None, ev)


def approx_tokens(text):
    """tokenizer近似(tiktoken未導入): 英数字主体のため UTF-8 bytes/4 を切り上げ。相対比較用。"""
    return math.ceil(len(text.encode("utf8")) / 4)
