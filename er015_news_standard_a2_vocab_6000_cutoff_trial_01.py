# ============================================================
# er015_news_standard_a2_vocab_6000_cutoff_trial_01.py
# NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01 (ユーザー指示、2026-09-25)
# ============================================================
# 目的: これまでの頻度帯設計(NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01、
# 4段階・REJECTED)を簡素化し、「頻出上位6,000語以内は原則そのまま残して
# よい/6,000語超は自然さを壊さない範囲で平易な語へ強く置換/固有名詞は
# 別扱い/専門語は意味保持に必要なら例外可」という単一しきい値+自然さ
# 優先の設計に絞ったv5 Promptで、Sewer/Metaを各1 call生成し、v3(Sewer)・
# v4(Sewer/Meta)と比較する。追加LLM call・新Validator・新QA工程・
# 生成後の追加修正call・Variation量産は行わない(生成は2 call、Sewer/Meta
# 各1)。Web Searchなし。
#
# 対象記事(いずれも改変禁止の既存Trial成果物を入力として使用):
#   Sewer Advanced: er015_output/news_natural_advanced_standard_a2_trial_01/
#                   a1_advanced_sewer.md
#   Sewer v3:       er015_output/news_standard_a2_vocab_effectiveness_trial_01/
#                   a2v3_standard_sewer.md
#   Sewer v4:       er015_output/news_standard_a2_vocab_banding_trial_01/
#                   a2v4_standard_sewer.md
#   Meta Advanced:  er015_output/news_ja_to_en_adaptation_trial_01/
#                   arms/arm3/output.md (sha256をsources.jsonと照合)
#   Meta v4:        er015_output/news_standard_a2_vocab_banding_trial_01/
#                   b1v4_standard_meta.md
#
# 頻度基準: wordfreq.top_n_list("en", 20000)からlemma単位の順位表を作り
# (NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01と同じ方法の再利用、追加install
# なし)、単一しきい値rank<=6000を「6,000語以内」、rank>6000(表外=20,000超
# 含む)を「6,000語超」とする2分類のみ使う(帯A/B/C/Dの細分は行わない)。
# 記事内で文頭以外に大文字表記される語は固有名詞候補として別枠
# (proper_noun、機械ヒューリスティック、限界は既存Trialと同じ)。
#
# 固定: 2 call(Sewer 1・Meta 1)、previous_response_idなし、Web Searchなし、
# model=gpt-5.6-luna effort=high、Production Prompt/routing/retry/fallback/
# Audio配線は変更しない。Production実装ではない。追加Variation禁止。
# 費用上限: 累計JPY 100円(--budget-jpyで超過見込みならSTOP、暴走防止目的)。
#
# 依存(いずれも無変更・import再利用のみ):
#   - er015_news_standard_a2_vocab_effectiveness_trial_01 (v3mod):
#       v1mod/v2mod へのアクセス、extract_content_words, simple_lemma,
#       simple_lemma_candidates, capitalized_positions, FUNCTION_WORDS,
#       DEVELOPER_STD_V3, STANDARD_USER_TEMPLATE_V3, _V3_FIVE_LINES,
#       SEWER_ADVANCED_PATH
#   - er015_news_natural_advanced_standard_a2_trial_01 (v1mod, v3mod経由):
#       out_path/save_text/save_json/load_text/load_json/install_logger,
#       _sha256_of_file, _strip_title, _level_metrics, _fact_tokens,
#       _call_and_record, vfl01.get_client, er015base._load_pricing,
#       WRITER_MODEL/WRITER_EFFORT
#   - er015_news_standard_a2_prompt_v2_trial_01 (v2mod, v3mod経由):
#       METAPHOR_WORDS, _metaphor_presence
#   - wordfreq (既存installを再利用、追加installなし): top_n_list
#
# サブコマンド (--step):
#   generate  (--article sewer|meta): v5 Promptで対象記事を1 call生成
#   evaluate  : 6,000超語の測定(2記事、Advanced/v3or無/v4/v5)+level_metrics+
#               fact_diff(Advanced->v5)+structure_map(段落数・比喩語・
#               reveal/endingマーカー)。LLM不使用。
#   assemble  : comparison_sewer_v5.md / comparison_meta_v5.md / cost.json
#               (vocab_over6000_*.md/level_metrics.md/vocab_transition_
#               11words.mdの最終稿はSonnetがevaluate出力を読んで直接執筆・
#               追記する。ここではevaluateが書いた素データ版を保持する)
# ============================================================
from __future__ import annotations

import argparse
import os

import er015_news_standard_a2_vocab_effectiveness_trial_01 as v3mod

v1mod = v3mod.v1mod
v2mod = v3mod.v2mod

WRITER_MODEL = v3mod.WRITER_MODEL     # "gpt-5.6-luna"
WRITER_EFFORT = v3mod.WRITER_EFFORT   # "high"

# ------------------------------------------------------------
# 入力source path(いずれも改変禁止)
# ------------------------------------------------------------
V3_OUT_DIR = os.path.join("er015_output", "news_standard_a2_vocab_effectiveness_trial_01")
V1_OUT_DIR = os.path.join("er015_output", "news_natural_advanced_standard_a2_trial_01")
BANDING_OUT_DIR = os.path.join("er015_output", "news_standard_a2_vocab_banding_trial_01")
META_ADAPT_OUT_DIR = os.path.join("er015_output", "news_ja_to_en_adaptation_trial_01")

SEWER_ADVANCED_PATH = v3mod.SEWER_ADVANCED_PATH
SEWER_V3_PATH = os.path.join(V3_OUT_DIR, "a2v3_standard_sewer.md")
SEWER_V4_PATH = os.path.join(BANDING_OUT_DIR, "a2v4_standard_sewer.md")

META_ADVANCED_PATH = os.path.join(META_ADAPT_OUT_DIR, "arms", "arm3", "output.md")
META_V4_PATH = os.path.join(BANDING_OUT_DIR, "b1v4_standard_meta.md")
SOURCES_JSON_PATH = os.path.join(V1_OUT_DIR, "sources.json")

RANK_CUTOFF = 6000


def out_path(out_dir: str, *parts: str) -> str:
    return v1mod.out_path(out_dir, *parts)


def install_logger(out_dir: str) -> None:
    v1mod.install_logger(out_dir)


# ------------------------------------------------------------
# sha256照合(Meta Advanced Baselineのみ。Sewer Advancedは既存Trialで
# sources.jsonに期待値エントリが無いため実測記録のみ)
# ------------------------------------------------------------
def _verify_meta_advanced_sha256() -> str:
    sources = v1mod.load_json(SOURCES_JSON_PATH)
    expected = sources["meta_advanced_baseline"]["sha256"]
    actual = v1mod._sha256_of_file(META_ADVANCED_PATH)
    if actual != expected:
        raise SystemExit(
            f"[STOP] meta_advanced_baseline sha256 mismatch: "
            f"expected={expected} actual={actual}")
    return actual


# ------------------------------------------------------------
# 頻度順位ルックアップ(lemma -> 最小順位)の構築(banding Trialと同じ方法)
# ------------------------------------------------------------
def _build_lemma_rank_map(wordlist: list) -> dict:
    rank_map = {}
    for idx, w in enumerate(wordlist, start=1):
        lem = v3mod.simple_lemma(w)
        if lem not in rank_map:
            rank_map[lem] = idx
    return rank_map


def _word_rank(word: str, rank_map: dict):
    candidates = v3mod.simple_lemma_candidates(word)
    ranks = [rank_map[c] for c in candidates if c in rank_map]
    if not ranks:
        return None
    return min(ranks)


def _get_rank_map():
    import wordfreq
    top20000 = wordfreq.top_n_list("en", 20000)
    return _build_lemma_rank_map(top20000)


# ------------------------------------------------------------
# 記事1本の6,000語しきい値測定(over6000/within6000/proper_noun)
# ------------------------------------------------------------
def measure_over6000(text: str, rank_map: dict) -> dict:
    content_tokens = v3mod.extract_content_words(text)
    token_total = len(content_tokens)

    distinct_lower = sorted(set(w.lower() for w in content_tokens))
    per_word = {}
    for w in distinct_lower:
        cap_info = v3mod.capitalized_positions(text, w)
        is_proper = cap_info["capitalized_non_sentence_initial"] > 0
        if is_proper:
            per_word[w] = {"bucket": "proper_noun", "rank": None}
        else:
            rank = _word_rank(w, rank_map)
            if rank is None:
                per_word[w] = {"bucket": "over6000", "rank": None}
            elif rank <= RANK_CUTOFF:
                per_word[w] = {"bucket": "within6000", "rank": rank}
            else:
                per_word[w] = {"bucket": "over6000", "rank": rank}

    bucket_counts_token = {"within6000": 0, "over6000": 0, "proper_noun": 0}
    bucket_words = {"within6000": [], "over6000": [], "proper_noun": []}
    for tok in content_tokens:
        key = tok.lower()
        bucket_counts_token[per_word[key]["bucket"]] += 1

    for key, info in per_word.items():
        entry = {"word": key, "rank": info.get("rank"),
                  "count": sum(1 for t in content_tokens if t.lower() == key)}
        bucket_words[info["bucket"]].append(entry)
    for bucket in bucket_words:
        # over6000 は順位が低い(数字が大きい/Noneが最下位)ほど後ろに
        bucket_words[bucket].sort(
            key=lambda d: (d["rank"] is None, d["rank"] if d["rank"] is not None else 0, -d["count"]))

    return {
        "content_word_token_total": token_total,
        "content_word_distinct_total": len(distinct_lower),
        "bucket_token_counts": bucket_counts_token,
        "bucket_distinct_counts": {k: len(v) for k, v in bucket_words.items()},
        "bucket_words": bucket_words,
    }


def _over6000_md_table(label: str, m: dict) -> list:
    lines = [f"### {label}\n",
             "| 帯 | 異なり語数 | 延べ語数 |",
             "|---|---|---|"]
    for b in ["within6000", "over6000", "proper_noun"]:
        lines.append(f"| {b} | {m['bucket_distinct_counts'][b]} | "
                      f"{m['bucket_token_counts'][b]} |")
    lines.append(f"\ncontent word 延べ={m['content_word_token_total']} "
                 f"異なり={m['content_word_distinct_total']}\n")
    words = m["bucket_words"]["over6000"]
    if words:
        lines.append(f"\n#### {label} — over6000語一覧"
                     "(異なり語、順位順、rank=Noneは表外[20,000超])\n")
        lines.append("| 語 | 頻度順位(lemma最小) | 出現回数 |")
        lines.append("|---|---|---|")
        for w in words:
            lines.append(f"| {w['word']} | {w['rank']} | {w['count']} |")
    return lines


# ------------------------------------------------------------
# v5 Prompt(v3の5行 -> 6行に置換。developer・他の行は一字も変えない)
# ------------------------------------------------------------
DEVELOPER_STD_V5 = v3mod.DEVELOPER_STD_V3  # v3と同一(一字も変えない)

_V5_SIX_LINES = (
    "Prefer words within roughly the 6,000 most common English words.\n"
    "If a word is clearly outside that range, replace it when a simpler "
    "natural alternative exists.\n"
    "Do not force a replacement if it makes the sentence less natural or "
    "changes the meaning.\n"
    "Proper names are excluded from this rule.\n"
    "Essential technical terms may remain when a simpler equivalent would "
    "lose important meaning.\n"
    "Do not add an explanation for a hard word; make the sentence around "
    "it simple instead."
)

assert v3mod._V3_FIVE_LINES in v3mod.STANDARD_USER_TEMPLATE_V3, (
    "v3 template内に置換対象の5行が見つからない(逐語不一致)")

STANDARD_USER_TEMPLATE_V5 = v3mod.STANDARD_USER_TEMPLATE_V3.replace(
    v3mod._V3_FIVE_LINES, _V5_SIX_LINES)

assert STANDARD_USER_TEMPLATE_V5 != v3mod.STANDARD_USER_TEMPLATE_V3
_v3_rest = v3mod.STANDARD_USER_TEMPLATE_V3.replace(v3mod._V3_FIVE_LINES, "")
_v5_rest = STANDARD_USER_TEMPLATE_V5.replace(_V5_SIX_LINES, "")
assert _v3_rest == _v5_rest, "v3/v5で置換対象以外の本文に差異がある"
assert DEVELOPER_STD_V5 == v3mod.DEVELOPER_STD_V3


def _write_prompt_files(out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    v1mod.save_text(
        out_path(out_dir, "prompt_standard_v5_6000.txt"),
        "DEVELOPER:\n" + DEVELOPER_STD_V5 + "\n\n"
        "USER TEMPLATE ({advanced_article} is substituted):\n" +
        STANDARD_USER_TEMPLATE_V5)

    diff_md = (
        "# prompt_diff_v3_v5.md — Standard Prompt v3 -> v5(6000-cutoff)"
        "差分\n\n"
        "developerはv3と一字も変えていない。変更したのはuser template内の"
        "次の5行のみで、それ以外の本文(段落順・改行含む、比喩語保持の行を"
        "含む)は一字も変えていない(機械assertで確認済み)。\n\n"
        "## v3の該当5行(置換対象、逐語)\n\n```\n" + v3mod._V3_FIVE_LINES + "\n```\n\n"
        "## v5の置換後6行(逐語)\n\n```\n" + _V5_SIX_LINES + "\n```\n\n"
        "## v5 developer(逐語、v3と同一文)\n\n```\n" + DEVELOPER_STD_V5 + "\n```\n\n"
        "## v5 user template全文(逐語)\n\n```\n" + STANDARD_USER_TEMPLATE_V5 + "\n```\n\n"
        "## 変更意図(背景: v4=頻度帯4段階設計はREJECTED、再現性向上せず)\n\n"
        "- v3は「簡単な語で同じ意味を表せるなら簡単な語を使う」という二値的な"
        "判断基準のみで、頻度の高低による段階的な扱いの違いを与えていなかった。"
        "v4はこれを4段階(very common/fairly common/uncommon/rare)に細分した"
        "が、NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01の実測で"
        "collects->gathers/distant->farawayが解消されず、invisible->unseen"
        "のような新たな悪化も発生し、REJECTEDとなった。\n"
        "- v5では頻度帯の細分をやめ、単一のしきい値「上位約6,000語」のみを"
        "示す。6,000語以内は原則そのまま許容し、6,000語超は「自然さを壊さ"
        "ない範囲で」平易な語への置換を強く優先する、という単純な二分法に"
        "戻した。\n"
        "- 固有名詞除外・専門語の意味保持例外はv3/v4から一貫して維持。\n"
        "- 追加した行数は1行(5行->6行)。過剰にPromptを増やさない指示に"
        "従い、既存のmetaphor保持指示・Story保持指示・Fact保持指示には"
        "触れていない。\n"
    )
    v1mod.save_text(out_path(out_dir, "prompt_diff_v3_v5.md"), diff_md)


# ------------------------------------------------------------
# STEP: generate (--article sewer|meta)
# ------------------------------------------------------------
def cmd_generate(out_dir: str, article: str, budget_jpy: float, force: bool) -> None:
    os.makedirs(out_dir, exist_ok=True)
    _write_prompt_files(out_dir)
    install_logger(out_dir)

    if article == "sewer":
        adv_path = SEWER_ADVANCED_PATH
        adv_sha = v1mod._sha256_of_file(adv_path)
        adv_text = v1mod.load_text(adv_path)
        stage = "a2v5_standard_sewer"
        output_path = out_path(out_dir, "a2v5_standard_sewer.md")
        meta_path = out_path(out_dir, "a2v5_standard_sewer.meta.json")
        sources_out = out_path(out_dir, "sewer_v5_generation_sources.json")
        sources_note = ("sewer_advancedのsha256は、Meta用sources.jsonに"
                         "期待値エントリが無いため突合対象ではなく実測値の"
                         "記録(逐語入力の証跡)。")
    elif article == "meta":
        adv_sha = _verify_meta_advanced_sha256()
        adv_path = META_ADVANCED_PATH
        adv_text = v1mod.load_text(adv_path)
        stage = "b1v5_standard_meta"
        output_path = out_path(out_dir, "b1v5_standard_meta.md")
        meta_path = out_path(out_dir, "b1v5_standard_meta.meta.json")
        sources_out = out_path(out_dir, "meta_v5_generation_sources.json")
        sources_note = ("meta_advancedのsha256はsources.json"
                         "(news_natural_advanced_standard_a2_trial_01)の"
                         "期待値と一致することを確認済み。")
    else:
        raise SystemExit(f"[STOP] unknown --article: {article}")

    v1mod.save_json(sources_out, {
        "advanced_path": adv_path,
        "advanced_sha256": adv_sha,
        "note": sources_note,
    })

    client = v1mod.vfl01.get_client()
    pricing = v1mod.er015base._load_pricing()

    user_prompt = STANDARD_USER_TEMPLATE_V5.format(advanced_article=adv_text)
    m = v1mod._call_and_record(client, pricing, DEVELOPER_STD_V5, user_prompt,
                                stage, output_path, meta_path, force)
    total_jpy = m.get("cost_jpy", 0.0)
    if total_jpy > budget_jpy:
        stop = {"stop_reason": f"budget exceeded after {stage} call",
                "total_jpy": total_jpy, "budget_jpy": budget_jpy}
        v1mod.save_json(out_path(out_dir, f"stop_reason_{article}.json"), stop)
        print(f"[STOP] budget exceeded after {stage}: {total_jpy} > {budget_jpy}")
        raise SystemExit(1)
    text = v1mod.load_text(output_path)
    if not text.strip():
        stop = {"stop_reason": f"empty output after retry ({stage})"}
        v1mod.save_json(out_path(out_dir, f"stop_reason_{article}.json"), stop)
        print(f"[STOP] empty output after retry ({stage})")
        raise SystemExit(1)

    print(f"[DONE] generate --article {article} complete. "
          f"cost_jpy={round(total_jpy, 4)} budget_jpy={budget_jpy} "
          f"retried={m.get('retried')} model={m.get('response_model_actual')} "
          f"advanced_sha256={adv_sha[:16]}...")


# ------------------------------------------------------------
# STEP: evaluate (LLM不使用)
# ------------------------------------------------------------
def cmd_evaluate(out_dir: str) -> None:
    rank_map = _get_rank_map()

    sewer_texts = {
        "sewer_advanced": v1mod.load_text(SEWER_ADVANCED_PATH),
        "sewer_standard_v3": v1mod.load_text(SEWER_V3_PATH),
        "sewer_standard_v4": v1mod.load_text(SEWER_V4_PATH),
        "sewer_standard_v5": v1mod.load_text(out_path(out_dir, "a2v5_standard_sewer.md")),
    }
    meta_texts = {
        "meta_advanced": v1mod.load_text(META_ADVANCED_PATH),
        "meta_standard_v4": v1mod.load_text(META_V4_PATH),
        "meta_standard_v5": v1mod.load_text(out_path(out_dir, "b1v5_standard_meta.md")),
    }

    sewer_bands = {k: measure_over6000(t, rank_map) for k, t in sewer_texts.items()}
    meta_bands = {k: measure_over6000(t, rank_map) for k, t in meta_texts.items()}
    v1mod.save_json(out_path(out_dir, "vocab_over6000_sewer.json"), sewer_bands)
    v1mod.save_json(out_path(out_dir, "vocab_over6000_meta.json"), meta_bands)

    sewer_lines = ["# vocab_over6000_sewer.md — Sewer 6,000語しきい値測定"
                   "(Advanced/v3/v4/v5、素データ。necessary/replaceable分類は"
                   "REPORT側でSonnetが追記)\n"]
    for key, label in [("sewer_advanced", "Sewer Advanced"),
                        ("sewer_standard_v3", "Sewer Standard v3"),
                        ("sewer_standard_v4", "Sewer Standard v4"),
                        ("sewer_standard_v5", "Sewer Standard v5 (6000-cutoff)")]:
        sewer_lines += _over6000_md_table(label, sewer_bands[key])
    v1mod.save_text(out_path(out_dir, "vocab_over6000_sewer.md"), "\n".join(sewer_lines))

    meta_lines = ["# vocab_over6000_meta.md — Meta 6,000語しきい値測定"
                  "(Advanced/v4/v5、素データ。necessary/replaceable分類は"
                  "REPORT側でSonnetが追記)\n"]
    for key, label in [("meta_advanced", "Meta Advanced"),
                        ("meta_standard_v4", "Meta Standard v4"),
                        ("meta_standard_v5", "Meta Standard v5 (6000-cutoff)")]:
        meta_lines += _over6000_md_table(label, meta_bands[key])
    v1mod.save_text(out_path(out_dir, "vocab_over6000_meta.md"), "\n".join(meta_lines))

    print(f"[OK] vocab_over6000 written. sewer over6000(distinct) "
          f"adv={sewer_bands['sewer_advanced']['bucket_distinct_counts']['over6000']} "
          f"v3={sewer_bands['sewer_standard_v3']['bucket_distinct_counts']['over6000']} "
          f"v4={sewer_bands['sewer_standard_v4']['bucket_distinct_counts']['over6000']} "
          f"v5={sewer_bands['sewer_standard_v5']['bucket_distinct_counts']['over6000']} | "
          f"meta over6000(distinct) "
          f"adv={meta_bands['meta_advanced']['bucket_distinct_counts']['over6000']} "
          f"v4={meta_bands['meta_standard_v4']['bucket_distinct_counts']['over6000']} "
          f"v5={meta_bands['meta_standard_v5']['bucket_distinct_counts']['over6000']}")

    # --- level_metrics ---
    level_files = {
        "sewer_advanced": SEWER_ADVANCED_PATH,
        "sewer_standard_v3": SEWER_V3_PATH,
        "sewer_standard_v4": SEWER_V4_PATH,
        "sewer_standard_v5": out_path(out_dir, "a2v5_standard_sewer.md"),
        "meta_advanced": META_ADVANCED_PATH,
        "meta_standard_v4": META_V4_PATH,
        "meta_standard_v5": out_path(out_dir, "b1v5_standard_meta.md"),
    }
    level_metrics = {k: v1mod._level_metrics(v1mod.load_text(p))
                      for k, p in level_files.items()}
    v1mod.save_json(out_path(out_dir, "level_metrics.json"), level_metrics)

    label_map = {
        "sewer_advanced": "Sewer Advanced", "sewer_standard_v3": "Sewer Standard v3",
        "sewer_standard_v4": "Sewer Standard v4", "sewer_standard_v5": "Sewer Standard v5",
        "meta_advanced": "Meta Advanced", "meta_standard_v4": "Meta Standard v4",
        "meta_standard_v5": "Meta Standard v5",
    }
    md_lines = ["# level_metrics.md — Level比較(Sewer 4段階 + Meta 3段階、"
                "参考値、機械判定は最終判断に用いない)\n",
                "| 記事 | words | sentences | avg words/sent | avg syll/word | "
                "long-sent(>=20w)率 | subordinator/100w | FK grade(heuristic) |",
                "|---|---|---|---|---|---|---|---|"]
    for key in ["sewer_advanced", "sewer_standard_v3", "sewer_standard_v4",
                "sewer_standard_v5", "meta_advanced", "meta_standard_v4",
                "meta_standard_v5"]:
        m = level_metrics[key]
        md_lines.append(
            f"| {label_map[key]} | {m['word_count']} | {m['sentence_count']} | "
            f"{m['avg_sentence_length_words']} | {m['avg_syllables_per_word_heuristic']} | "
            f"{m['long_sentence_ratio_ge20words']} | {m['subordinators_per_100_words']} | "
            f"{m['flesch_kincaid_grade_heuristic']} |")
    v1mod.save_text(out_path(out_dir, "level_metrics.md"), "\n".join(md_lines))
    print("[OK] level_metrics.json / level_metrics.md written")

    # --- fact_diff (Advanced -> v5, both articles) ---
    for key, adv_path, v5_path, dst in [
        ("sewer", SEWER_ADVANCED_PATH, out_path(out_dir, "a2v5_standard_sewer.md"),
         out_path(out_dir, "fact_diff_machine_sewer_v5.json")),
        ("meta", META_ADVANCED_PATH, out_path(out_dir, "b1v5_standard_meta.md"),
         out_path(out_dir, "fact_diff_machine_meta_v5.json")),
    ]:
        adv = v1mod._fact_tokens(v1mod.load_text(adv_path))
        v5 = v1mod._fact_tokens(v1mod.load_text(v5_path))
        result = {
            "advanced_to_v5": {
                "advanced": adv, "v5": v5,
                "numbers_missing_in_v5": sorted(set(adv["numbers"]) - set(v5["numbers"])),
                "numbers_added_in_v5": sorted(set(v5["numbers"]) - set(adv["numbers"])),
                "proper_nouns_missing_in_v5": sorted(
                    set(adv["proper_nouns"]) - set(v5["proper_nouns"])),
                "proper_nouns_added_in_v5": sorted(
                    set(v5["proper_nouns"]) - set(adv["proper_nouns"])),
            }
        }
        v1mod.save_json(dst, result)
        print(f"[OK] fact_diff_machine_{key}_v5.json written")

    # --- structure_map ---
    def para_count(text: str) -> int:
        _, body = v1mod._strip_title(text)
        return len([p for p in body.split("\n\n") if p.strip()])

    sm_lines = ["# structure_map.md — 段落対応・比喩語保持・Reveal/Ending"
                "マーカー確認(Sewer 4段階 + Meta 3段階)\n"]
    sm_lines.append("## 段落数対応\n")
    sm_lines.append(f"- Sewer: Advanced {para_count(sewer_texts['sewer_advanced'])}段落 / "
                    f"v3 {para_count(sewer_texts['sewer_standard_v3'])}段落 / "
                    f"v4 {para_count(sewer_texts['sewer_standard_v4'])}段落 / "
                    f"v5 {para_count(sewer_texts['sewer_standard_v5'])}段落")
    sm_lines.append(f"- Meta: Advanced {para_count(meta_texts['meta_advanced'])}段落 / "
                    f"v4 {para_count(meta_texts['meta_standard_v4'])}段落 / "
                    f"v5 {para_count(meta_texts['meta_standard_v5'])}段落")

    sm_lines.append("\n## 比喩語保持有無(語単位、大小無視の部分一致、"
                    "v2mod.METAPHOR_WORDSをそのまま再利用)\n")
    sm_lines.append("| 語 | Sewer Adv | Sewer v3 | Sewer v4 | Sewer v5 | "
                    "Meta Adv | Meta v4 | Meta v5 |")
    sm_lines.append("|---|---|---|---|---|---|---|---|")
    presence = {
        "sewer_adv": v2mod._metaphor_presence(sewer_texts["sewer_advanced"]),
        "sewer_v3": v2mod._metaphor_presence(sewer_texts["sewer_standard_v3"]),
        "sewer_v4": v2mod._metaphor_presence(sewer_texts["sewer_standard_v4"]),
        "sewer_v5": v2mod._metaphor_presence(sewer_texts["sewer_standard_v5"]),
        "meta_adv": v2mod._metaphor_presence(meta_texts["meta_advanced"]),
        "meta_v4": v2mod._metaphor_presence(meta_texts["meta_standard_v4"]),
        "meta_v5": v2mod._metaphor_presence(meta_texts["meta_standard_v5"]),
    }
    for w in v2mod.METAPHOR_WORDS:
        row = [w]
        for key in ["sewer_adv", "sewer_v3", "sewer_v4", "sewer_v5",
                    "meta_adv", "meta_v4", "meta_v5"]:
            row.append("○" if presence[key].get(w) else "-")
        sm_lines.append("| " + " | ".join(row) + " |")

    sewer_v5_lower = sewer_texts["sewer_standard_v5"].lower()
    meta_v5_lower = meta_texts["meta_standard_v5"].lower()
    sewer_reveal_ok = ("combined septic tank" in sewer_v5_lower and
                        "small water-treatment" in sewer_v5_lower)
    sewer_metaphor_marker_ok = (("like a hidden main artery" in sewer_v5_lower or
                                  "is like" in sewer_v5_lower) and
                                 "washing machine" in sewer_v5_lower)
    sewer_ending_ok = "surprisingly familiar place" in sewer_v5_lower
    meta_reveal_ok = ("human concierges" in meta_v5_lower and "backstage" in meta_v5_lower)
    meta_ending_ok = ("who is speaking on the stage" in meta_v5_lower and
                       "who is behind the curtain" in meta_v5_lower)
    meta_scope_ok = "some parts of the calls" in meta_v5_lower

    sm_lines.append("\n## Reveal / 中心比喩 / Ending マーカー確認(手動判定、○×。"
                    "v3mod/banding既存Trialが使った逐語マーカーをv5にもそのまま"
                    "適用。v5が異なる自然な言い回しで同じ内容を表現していれば"
                    "×になり得るため、最終判断はSonnet目視[REPORT本文参照]・"
                    "Fable評価に委ねる)\n")
    sm_lines.append(f"- Sewer Reveal(combined septic tank / small water-treatment "
                    f"の表現残存): {'○' if sewer_reveal_ok else '×(要確認、本文参照)'}")
    sm_lines.append(f"- Sewer 中心比喩(main artery / washing machineが直喩のまま "
                    f"保持): {'○' if sewer_metaphor_marker_ok else '×(要確認、本文参照)'}")
    sm_lines.append(f"- Sewer Ending(\"surprisingly familiar place\"の結び): "
                    f"{'○' if sewer_ending_ok else '×(要確認、本文参照)'}")
    sm_lines.append(f"- Meta Reveal(human concierges/backstageの発見という段落構成): "
                    f"{'○' if meta_reveal_ok else '×(要確認、本文参照)'}")
    sm_lines.append(f"- Meta Ending(\"Who is speaking on the stage? And who is "
                    f"behind the curtain?\"の結び): "
                    f"{'○' if meta_ending_ok else '×(要確認、本文参照)'}")
    sm_lines.append(f"- Meta 数量表現\"some parts of the calls\"の維持: "
                    f"{'○' if meta_scope_ok else '×(要確認、本文参照)'}")

    v1mod.save_text(out_path(out_dir, "structure_map.md"), "\n".join(sm_lines))
    print(f"[OK] structure_map.md written. sewer_reveal={sewer_reveal_ok} "
          f"sewer_metaphor={sewer_metaphor_marker_ok} sewer_ending={sewer_ending_ok} "
          f"meta_reveal={meta_reveal_ok} meta_ending={meta_ending_ok} "
          f"meta_scope={meta_scope_ok}")


# ------------------------------------------------------------
# STEP: assemble (comparison_*.md + cost.json)
# ------------------------------------------------------------
def cmd_assemble(out_dir: str) -> None:
    sewer_adv = v1mod.load_text(SEWER_ADVANCED_PATH)
    sewer_v3 = v1mod.load_text(SEWER_V3_PATH)
    sewer_v5 = v1mod.load_text(out_path(out_dir, "a2v5_standard_sewer.md"))
    comparison_sewer = (
        "# comparison_sewer_v5.md — Sewer: Advanced -> Standard v3 -> "
        "Standard v5 (6000-cutoff)\n\n"
        "## Advanced (改変禁止Baseline)\n\n" + sewer_adv + "\n\n---\n\n"
        "## Standard v3 (NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01、"
        "改変禁止)\n\n" + sewer_v3 + "\n\n---\n\n"
        "## Standard v5 (NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01、本Trial)"
        "\n\n" + sewer_v5 + "\n"
    )
    v1mod.save_text(out_path(out_dir, "comparison_sewer_v5.md"), comparison_sewer)

    meta_adv = v1mod.load_text(META_ADVANCED_PATH)
    meta_v4 = v1mod.load_text(META_V4_PATH)
    meta_v5 = v1mod.load_text(out_path(out_dir, "b1v5_standard_meta.md"))
    comparison_meta = (
        "# comparison_meta_v5.md — Meta: Advanced -> Standard v4 -> "
        "Standard v5 (6000-cutoff)\n\n"
        "## Advanced (改変禁止Baseline)\n\n" + meta_adv + "\n\n---\n\n"
        "## Standard v4 (NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01、"
        "改変禁止)\n\n" + meta_v4 + "\n\n---\n\n"
        "## Standard v5 (NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01、本Trial)"
        "\n\n" + meta_v5 + "\n"
    )
    v1mod.save_text(out_path(out_dir, "comparison_meta_v5.md"), comparison_meta)
    print("[OK] comparison_sewer_v5.md / comparison_meta_v5.md written")

    calls = []
    total_jpy = 0.0
    for meta_file in ["a2v5_standard_sewer.meta.json", "b1v5_standard_meta.meta.json"]:
        p = out_path(out_dir, meta_file)
        if os.path.exists(p):
            m = v1mod.load_json(p)
            calls.append(m)
            total_jpy += m.get("cost_jpy", 0.0)
        else:
            print(f"[WARN] missing meta: {p}")
    cost = {
        "calls": calls,
        "additional_llm_call_count": len(calls),
        "total_cost_jpy": round(total_jpy, 4),
        "budget_jpy": 100,
        "within_budget": total_jpy <= 100,
    }
    v1mod.save_json(out_path(out_dir, "cost.json"), cost)
    print(f"[OK] cost.json written. total_cost_jpy={round(total_jpy, 4)} "
          f"within_budget={cost['within_budget']} "
          f"additional_llm_call_count={len(calls)}")


# ------------------------------------------------------------
# main
# ------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--step", required=True,
                     choices=["generate", "evaluate", "assemble"])
    ap.add_argument("--article", choices=["sewer", "meta"], default=None)
    ap.add_argument("--budget-jpy", type=float, default=100.0)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    print(f"[INFO] out_dir(resolved)={os.path.abspath(args.out_dir)}")

    if args.step == "generate":
        if not args.article:
            raise SystemExit("[STOP] --step generate requires --article sewer|meta")
        cmd_generate(args.out_dir, args.article, args.budget_jpy, args.force)
    elif args.step == "evaluate":
        cmd_evaluate(args.out_dir)
    elif args.step == "assemble":
        cmd_assemble(args.out_dir)


if __name__ == "__main__":
    main()
