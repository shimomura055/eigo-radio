# ============================================================
# er039_family_xy_concreteness_control_trial_02.py
# FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02(ユーザー承認済みTrial、Trialのみ)
# ============================================================
# 目的: Trial-01(er037)で観測した「JA段階で固有名詞9→English Advanced段階
# で19」(Hormuz AN)が (a) 実際の新規固有名詞追加なのか (b) カウント方式の
# アーティファクトなのかを実データで切り分け、かつ AN3(A3+N2)/AN2(A2+N2)
# × T0(現行英語化)/T1(Trial限定の抑制追記)の2x2 Matrixで「減らしながら
# 内容を壊さない組み合わせ」を比較する。
#
# 本ファイルはTrial専用の新規スクリプトであり、既存Production Prompt定数
# (er019_family_x_ja_writer_o_r1_r2_01.R0_PROMPT/REVISION_INSTRUCTIONS、
# er003_v1_n3_01_advanced_adaptation_generate.ADVANCED_*ブロック/
# build_prompt())は一切変更しない。T1は`adv_gen.build_prompt()`の出力
# (production callと同一)に、このファイル内でのみ定義する短い追記文を
# 連結した新しいpromptで、production関数とは別経路(`vfl01.
# run_writer_with_technical_retry`を直接呼ぶ)で1回callする。
#
# 既存Production/Trial-01関数の再利用(無変更import):
#   - er037_family_xy_concreteness_control_trial_01: ARTICLE_SOURCES /
#     load_article_inputs / PATTERNS_A / PATTERNS_N / COMBO_PATTERNS /
#     extract_entities_ja / extract_entities_en / deterministic_metrics /
#     run_essential_fact_check / run_rubric_eval / budget_check /
#     save_text / save_json / merge_save_json / word_count /
#     count_numeric_tokens / _KATAKANA_ENTITY_RE / _ROMAN_ENTITY_RE /
#     _EN_STOPWORDS_CAPWORD
#   - er019_family_x_ja_writer_o_r1_r2_01: DEVELOPER_MESSAGE /
#     REVISION_INSTRUCTIONS / build_original_prompt / call_fresh /
#     call_with_previous_response_id / WRITER_EFFORT
#   - er003_v1_n3_01_advanced_adaptation_generate: build_prompt /
#     ADVANCED_DEVELOPER / generate_advanced_adaptation / PROCESS_LABEL /
#     _load_pricing / _compute_cost_jpy(cost計算、private命名だが
#     モジュール属性として無変更のまま参照するのみ)
#   - er003_v1_en_direct_vfl_01_generate: run_writer_with_technical_retry /
#     get_client / MODEL
#   - er006_model_routing_contract_01: require_model / WRITER_MODEL
#   - er019_family_x_entertainment_production_runner_01:
#     compute_stage_cost_breakdown
#   - er005_cost_logger: install
#
# 設計書: docs/pm/design_family_xy_concreteness_control_trial_02.md
# ============================================================
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time

import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_advanced_adaptation_generate as adv_gen
import er037_family_xy_concreteness_control_trial_01 as t1

TRIAL_TAG = "FAMILY_XY_CONCRETENESS_CONTROL_TRIAL_02"

# ------------------------------------------------------------
# T1(Trial限定の抑制追記文、逐語)
# ------------------------------------------------------------
# production `adv_gen.build_prompt()` の出力に、このファイル内でのみ連結
# する。production定数(ADVANCED_*ブロック)自体は一切書き換えない。
T1_SUPPRESSION_SUFFIX = (
    "\n\n[Trial-only additional instruction -- not part of the production "
    "prompt]\n"
    "Do not add any number, time, or proper noun (a person's name, a "
    "company or product name, or a place name) that is not already in the "
    "Japanese article above. Where the Japanese article uses a general or "
    "vague expression instead of a specific number, time, or name, keep "
    "that expression general in the English version as well. Do not use "
    "this instruction as a reason to remove facts, numbers, times, or "
    "names that ARE already stated in the Japanese article."
)

# ------------------------------------------------------------
# AN2(A2+N2)パターン文言(delegation指定、Trial-01のPATTERNS_A/N2を
# そのまま連結。既存COMBO_PATTERNS["AN"]=A3+N2はTrial-01の値を無変更で
# AN3として再利用する)
# ------------------------------------------------------------
JA_PATTERN_TEXT = {
    "AN3": t1.COMBO_PATTERNS["AN"],  # = A3 + N2(Trial-01と同一文言)
    "AN2": t1.PATTERNS_A["A2"] + "\n" + t1.PATTERNS_N["N2"],
}

CELL_IDS = ["AN3-T0", "AN3-T1", "AN2-T0", "AN2-T1"]


def cell_ja_pattern(cell_id: str) -> str:
    return cell_id.split("-")[0]


def cell_t_variant(cell_id: str) -> str:
    return cell_id.split("-")[1]


# ------------------------------------------------------------
# JA Original(+pattern追記) -> R1(現行) -> R2(現行)。t1と同型だが、
# pattern_idではなく直接テキストを受け取る(AN2はt1のPATTERNS辞書に
# 存在しないため)。
# ------------------------------------------------------------
def run_ja_original_with_extra(client, article_inputs: dict, extra_text: str, stage_tag: str) -> dict:
    base_prompt = t1.jaw.build_original_prompt(
        article_inputs["selected_storyline"], article_inputs["selected_fact_brief_text"])
    prompt = base_prompt if not extra_text else base_prompt + "\n\n" + extra_text
    t0 = time.time()
    response = t1.jaw.call_fresh(client, t1.jaw.DEVELOPER_MESSAGE, prompt, t1.jaw.WRITER_EFFORT,
                                  f"trial02_original_{stage_tag}")
    text = response.output_text.strip()
    return {"text": text, "response_id": response.id, "elapsed_seconds": round(time.time() - t0, 3)}


def run_ja_chain(client, article_inputs: dict, extra_text: str, stage_tag: str) -> dict:
    original = run_ja_original_with_extra(client, article_inputs, extra_text, stage_tag)
    r1 = t1.run_ja_revision(client, original["response_id"], t1.jaw.REVISION_INSTRUCTIONS["r1"],
                             f"trial02_r1_{stage_tag}")
    r2 = t1.run_ja_revision(client, r1["response_id"], t1.jaw.REVISION_INSTRUCTIONS["r2"],
                             f"trial02_r2_{stage_tag}")
    return {"original": original, "r1": r1, "r2": r2}


# ------------------------------------------------------------
# Advanced(English)生成: T0=production build_prompt()をそのまま1回call
# (t1.run_advanced_translationと同じ、production関数を無変更で呼ぶ)。
# T1=同じbuild_prompt()の出力にTrial限定の抑制文を追記した別promptで、
# production関数(generate_advanced_adaptation)は呼ばず、その内部で使って
# いるのと同じ既存primitive(vfl01.run_writer_with_technical_retry)を
# 直接呼ぶ(production関数自体は無変更のまま別経路で使う)。
# ------------------------------------------------------------
def run_advanced_translation_t0(client, ja_r2_text: str) -> dict:
    return t1.run_advanced_translation(client, ja_r2_text)


def run_advanced_translation_t1(client, ja_r2_text: str) -> dict:
    base_prompt = adv_gen.build_prompt(ja_r2_text)
    prompt = base_prompt + T1_SUPPRESSION_SUFFIX
    price_fn = adv_gen._load_pricing()
    requested_model = adv_gen.routing.require_model(adv_gen.PROCESS_LABEL, adv_gen.routing.WRITER_MODEL)
    t0 = time.time()
    result = vfl01.run_writer_with_technical_retry(
        client, prompt, max_attempts=2, model=requested_model, developer=adv_gen.ADVANCED_DEVELOPER)
    elapsed = round(time.time() - t0, 3)
    if result["status"] not in ("STRUCTURE_PASS", "STRUCTURE_INVALID"):
        raise RuntimeError(f"[T1] {result['status']} attempts={len(result['attempts'])}")
    if result["status"] != "STRUCTURE_PASS":
        raise RuntimeError(f"[T1] structure gate failed: attempts={len(result['attempts'])}")
    text = result["raw_text"]
    usage = result.get("usage") or {}
    cost_usd, cost_jpy = adv_gen._compute_cost_jpy(
        price_fn, result["model"], usage.get("input_tokens") or 0,
        usage.get("cached_input_tokens") or 0, usage.get("output_tokens") or 0)
    return {
        "text": text, "cost_jpy": cost_jpy, "model": result["model"],
        "attempts": len(result["attempts"]), "elapsed_seconds": elapsed,
        "base_prompt_matches_production": prompt.startswith(base_prompt),
        "t1_suffix_sha256": hashlib.sha256(T1_SUPPRESSION_SUFFIX.encode("utf-8")).hexdigest(),
    }


# ------------------------------------------------------------
# 改良カウンタ(Trial限定関数。Production無変更。実固有名詞のみ・複合語は
# 1件・漢字固有名詞も検出・Title Case見出しは除外。Hormuz/Meta 2記事の
# 観測語彙に基づく簡易辞書であり、汎用NER/形態素解析器の代替ではない
# ことを明記する)
# ------------------------------------------------------------
KATAKANA_STOPWORDS_JA_IMPROVED = {
    "ニュース", "バレル", "ドル", "タンカー", "ガソリン", "エネルギー", "カーブ",
    "チャート", "ドラマ", "ドラマチック", "エージェント", "コンシェルジュ",
    "コールセンター", "スタッフ", "テスト", "プルルル", "ミス", "ルール",
    "ロールバック", "サービス", "プライバシー", "ユーザー", "イラン",  # イランは
    # 実際には国名(固有名詞)だが後段KNOWN_KANJI経由で"イラン"をカタカナ国名
    # として別途KEEPするため、ここでは重複させず単純化のためstopword扱い
    # にしない方が正確 -> 下記で訂正(このコメントは意図の記録用)。
    "アクセル", "ブレーキ", "パーセント",  # AN2実測(Hormuz)で新たに観測した
    # 一般名詞(アクセル/ブレーキの比喩表現、パーセント=%の読み下し)。
}
# 上記コメントの訂正: イランはstopwordから除外し、実固有名詞として残す。
KATAKANA_STOPWORDS_JA_IMPROVED.discard("イラン")

EXTRA_COMMON_TOKENS_JA_IMPROVED = {"AI"}

KNOWN_KANJI_ENTITIES_JA = [
    "湾岸諸国", "湾岸の国々", "湾岸国", "中東", "米国", "アメリカ", "英国", "日本",
    "国際海事機関", "中国", "韓国", "北朝鮮", "台湾", "ロシア", "ウクライナ",
    "イスラエル", "パレスチナ", "インド", "ドイツ", "フランス", "国連",
]
KANJI_CANONICAL_EN = {
    "湾岸諸国": "Gulf states", "湾岸の国々": "Gulf states", "湾岸国": "Gulf states",
    "中東": "Middle East", "米国": "United States", "アメリカ": "United States",
    "英国": "United Kingdom", "日本": "Japan", "国際海事機関": "International Maritime Organization",
    "中国": "China", "韓国": "South Korea", "北朝鮮": "North Korea", "台湾": "Taiwan",
    "ロシア": "Russia", "ウクライナ": "Ukraine", "イスラエル": "Israel",
    "パレスチナ": "Palestine", "インド": "India", "ドイツ": "Germany",
    "フランス": "France", "国連": "United Nations",
}


def extract_entities_ja_improved(text: str) -> set:
    remaining = text
    entities = set()
    for phrase in sorted(KNOWN_KANJI_ENTITIES_JA, key=len, reverse=True):
        if phrase in remaining:
            entities.add(KANJI_CANONICAL_EN.get(phrase, phrase))
            remaining = remaining.replace(phrase, " ")
    katakana_raw = set(t1._KATAKANA_ENTITY_RE.findall(remaining))
    roman_raw = set(tok for tok in t1._ROMAN_ENTITY_RE.findall(remaining) if len(tok) >= 2)
    for tok in katakana_raw:
        # 既存正規表現[゠-ヿ]は「・」(中黒)もKatakanaブロックに含むため、
        # 「米国・イラン」のような並列表現が「・イラン」ごと1トークンに
        # なる既知の挙動がある(t1側は無変更のため、ここでのみ正規化する)。
        tok_norm = tok.lstrip("・")
        if not tok_norm or tok_norm in KATAKANA_STOPWORDS_JA_IMPROVED:
            continue
        entities.add(tok_norm)
    for tok in roman_raw:
        if tok in EXTRA_COMMON_TOKENS_JA_IMPROVED:
            continue
        entities.add(tok)
    return entities


MONTH_NAMES_EN = {
    "January", "February", "March", "April", "May", "June", "July", "August",
    "September", "October", "November", "December",
}
EXTRA_COMMON_ACRONYMS_EN_IMPROVED = {"AI"}

KNOWN_MULTIWORD_ENTITIES_EN = [
    "Donald Trump", "United States", "Strait of Hormuz", "Middle Eastern",
    "Middle East", "Gulf states", "Gulf-state", "Gulf countries",
    "Financial Times", "Yahoo Finance",
    "International Maritime Organization", "Persian Gulf",
]
MULTIWORD_CANONICAL_EN = {
    "Donald Trump": "Donald Trump", "United States": "United States",
    "Strait of Hormuz": "Strait of Hormuz", "Middle Eastern": "Middle East",
    "Middle East": "Middle East", "Gulf states": "Gulf states",
    "Gulf-state": "Gulf states", "Gulf countries": "Gulf states",
    "Financial Times": "Financial Times", "Yahoo Finance": "Yahoo Finance",
    "International Maritime Organization": "International Maritime Organization",
    "Persian Gulf": "Gulf states",
}


# 複合固有名詞の一部だけが単独語として別文で再出現するケース(例:
# 「Donald Trump」の後段落で単に「Trump」とだけ書かれる)を、名称単位の
# 数え直しで二重計上しないための別名統合(Trial-02限定、観測語彙ベース)。
ALIAS_MERGE_EN = {
    "Trump": "Donald Trump",
    "Hormuz": "Strait of Hormuz",
    "Strait": "Strait of Hormuz",
    "US": "United States",
    "Gulf": "Gulf states",
}


def _strip_possessive_en(word: str) -> str:
    if word.endswith("’s") or word.endswith("'s"):
        return word[:-2]
    return word


def extract_entities_en_improved(text: str) -> set:
    # 複合固有名詞(Donald Trump等)の置換は、行分割前の全文に対して先に行う
    # (t1.extract_entities_enと同じ「行単位でsentence分割」の挙動自体は
    # 崩さないよう、見出し除外+文頭語除外のロジックは行単位を維持する。
    # 段落をまたいで1つのblobへ結合すると、段落末尾の引用符付き文末記号
    # [."]等の直後にlookbehind regexがマッチせず、次段落の先頭語を
    # 誤って「文頭でない語」と判定してしまう実測不具合があったため、
    # 行単位処理を維持する)。
    remaining = text
    entities = set()
    for phrase in sorted(KNOWN_MULTIWORD_ENTITIES_EN, key=len, reverse=True):
        if phrase in remaining:
            entities.add(MULTIWORD_CANONICAL_EN.get(phrase, phrase))
            remaining = remaining.replace(phrase, " ")
    # em/enダッシュ(-)は空白なしで単語に密着することがあり(例: "not AI-made"の
    # ような挿入句)、素朴な空白split単体では"AI-made"のように1語へ誤結合
    # される。通常のハイフン"-"(Gulf-state等の複合語)は壊さないよう、
    # em/enダッシュのみ空白へ正規化する。
    remaining = remaining.replace("—", " ").replace("–", " ")
    lines = remaining.split("\n")
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue  # 見出し行は本文抽出の対象外(Title Case由来ノイズ除外)
        sentences = re.split(r"(?<=[.!?])\s+", stripped)
        for sent in sentences:
            words = sent.split()
            for idx, w in enumerate(words):
                w_clean = w.strip(".,!?\"'()[]’‘")
                w_clean = _strip_possessive_en(w_clean)
                if not w_clean or not w_clean[0].isupper():
                    continue
                if idx == 0:
                    continue
                if w_clean in t1._EN_STOPWORDS_CAPWORD:
                    continue
                if w_clean in MONTH_NAMES_EN:
                    continue
                if w_clean in EXTRA_COMMON_ACRONYMS_EN_IMPROVED:
                    continue
                entities.add(w_clean)
    for alias, canonical in ALIAS_MERGE_EN.items():
        if alias in entities and canonical in entities:
            entities.discard(alias)
    return entities


# canonical(改良カウンタの正規化名) -> {JA表記候補, EN表記候補}(投資家向け
# 名称単位diff表とTrial-02固有の「JA->EN新規出現」判定に使う、Hormuz/Meta
# 2記事の観測語彙ベースの対応表)
CANONICAL_ENTITY_PAIRS = {
    "Donald Trump": {"ja": ["トランプ"], "en": ["Donald Trump", "Trump"]},
    "Strait of Hormuz": {"ja": ["ホルムズ"], "en": ["Strait of Hormuz", "Hormuz"]},
    "Brent": {"ja": ["ブレント"], "en": ["Brent"]},
    "Iran": {"ja": ["イラン"], "en": ["Iran"]},
    # extract_entities_ja_improved()は漢字表記をKANJI_CANONICAL_ENで英語
    # canonical名へ正規化して返す(例: "米国"->"United States")ため、
    # "ja"側フォームには元の漢字表記と正規化後の英語canonical文字列の両方を
    # 含める(どちらの形でJA entity集合に入っていても対応表として機能する)。
    "United States": {"ja": ["米国", "アメリカ", "United States"], "en": ["United States"]},
    "Middle East": {"ja": ["中東", "Middle East"], "en": ["Middle East"]},
    "Gulf states": {"ja": ["湾岸諸国", "湾岸の国々", "湾岸国", "Gulf states"], "en": ["Gulf states"]},
    "Meta": {"ja": ["Meta"], "en": ["Meta"]},
    "Muse": {"ja": ["Muse"], "en": ["Muse"]},
}


def build_name_unit_diff_table(ja_entities: set, en_entities: set) -> list:
    """改良カウンタで抽出したJA/EN entity集合を名称単位で突き合わせる。
    CANONICAL_ENTITY_PAIRSに登録済みの概念はJA<->EN対応の有無で判定し、
    未登録の新規語(観測外)は`unmapped`として別掲する(黙って握りつぶさ
    ない)。"""
    rows = []
    seen_ja = set()
    seen_en = set()
    for canonical, forms in CANONICAL_ENTITY_PAIRS.items():
        ja_hit = any(f in ja_entities for f in forms["ja"])
        en_hit = any(f in en_entities for f in forms["en"])
        if not ja_hit and not en_hit:
            continue
        seen_ja.update(f for f in forms["ja"] if f in ja_entities)
        seen_en.update(f for f in forms["en"] if f in en_entities)
        rows.append({
            "canonical": canonical, "in_ja": ja_hit, "in_en": en_hit,
            "en_new_vs_ja": (en_hit and not ja_hit),
        })
    unmapped_ja = sorted(ja_entities - seen_ja)
    unmapped_en = sorted(en_entities - seen_en)
    for tok in unmapped_ja:
        rows.append({"canonical": tok, "in_ja": True, "in_en": False, "en_new_vs_ja": False,
                     "note": "unmapped(JAのみ、CANONICAL_ENTITY_PAIRS未登録)"})
    for tok in unmapped_en:
        rows.append({"canonical": tok, "in_ja": False, "in_en": True, "en_new_vs_ja": True,
                     "note": "unmapped(ENのみ、CANONICAL_ENTITY_PAIRS未登録=要目視確認)"})
    return rows


def improved_metrics(text: str, lang: str) -> dict:
    entities = extract_entities_ja_improved(text) if lang == "ja" else extract_entities_en_improved(text)
    return {"entity_count_improved": len(entities), "entities_improved": sorted(entities)}


# ------------------------------------------------------------
# 固有名詞9->19投資(read-only, API不要)
# ------------------------------------------------------------
def investigate_entities(from_dir: str, out_path: str) -> None:
    ja_text = t1.load_text(f"{from_dir}/task_a_ja/AN_r2.md")
    en_text = t1.load_text(f"{from_dir}/task_a_advanced/AN.md")
    a0_ja_text = t1.load_text(f"{from_dir}/task_a_ja/A0_r2.md")
    a0_en_text = t1.load_text(f"{from_dir}/task_a_advanced/A0.md")

    old_ja = t1.extract_entities_ja(ja_text)
    old_en = t1.extract_entities_en(en_text)
    old_ja_a0 = t1.extract_entities_ja(a0_ja_text)
    old_en_a0 = t1.extract_entities_en(a0_en_text)

    imp_ja = extract_entities_ja_improved(ja_text)
    imp_en = extract_entities_en_improved(en_text)
    imp_ja_a0 = extract_entities_ja_improved(a0_ja_text)
    imp_en_a0 = extract_entities_en_improved(a0_en_text)

    diff_table = build_name_unit_diff_table(imp_ja, imp_en)

    lines = []
    lines.append(f"# 固有名詞 9->19 実体調査({from_dir})\n")
    lines.append("## 旧カウンタ(Trial-01 `extract_entities_ja`/`extract_entities_en`)\n")
    lines.append(f"- AN JA (旧): {len(old_ja)}件 -> {sorted(old_ja)}")
    lines.append(f"- AN EN (旧): {len(old_en)}件 -> {sorted(old_en)}")
    lines.append(f"- A0 JA (旧, baseline参考): {len(old_ja_a0)}件 -> {sorted(old_ja_a0)}")
    lines.append(f"- A0 EN (旧, baseline参考): {len(old_en_a0)}件 -> {sorted(old_en_a0)}\n")
    lines.append("## 改良カウンタ(Trial-02限定。実固有名詞のみ・複合語は1件・"
                  "漢字固有名詞も検出・Title Case見出しは除外)\n")
    lines.append(f"- AN JA (改良): {len(imp_ja)}件 -> {sorted(imp_ja)}")
    lines.append(f"- AN EN (改良): {len(imp_en)}件 -> {sorted(imp_en)}")
    lines.append(f"- A0 JA (改良, baseline参考): {len(imp_ja_a0)}件 -> {sorted(imp_ja_a0)}")
    lines.append(f"- A0 EN (改良, baseline参考): {len(imp_en_a0)}件 -> {sorted(imp_en_a0)}\n")
    lines.append("## 名称単位 JA->EN 差分表(改良カウンタ、AN)\n")
    lines.append("| 固有名詞(canonical) | JA出現 | EN出現 | ENで新規か | 備考 |")
    lines.append("|---|---|---|---|---|")
    for row in diff_table:
        lines.append(f"| {row['canonical']} | {row['in_ja']} | {row['in_en']} | "
                      f"{row['en_new_vs_ja']} | {row.get('note', '')} |")
    lines.append("")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[OK] entity investigation written: {out_path}")


# ------------------------------------------------------------
# Matrix生成(AN3/AN2 x T0/T1)
# ------------------------------------------------------------
def run_cell(client, article: str, cell_id: str, inputs: dict, out_dir: str,
             baseline_from: str, ja_cache: dict) -> dict:
    ja_pattern = cell_ja_pattern(cell_id)
    t_variant = cell_t_variant(cell_id)
    ledger_text = inputs["full_ledger_text"]
    a0_en_text = t1.load_text(f"{baseline_from}/task_a_advanced/A0.md")

    reused_ja = False
    reused_en = False

    if ja_pattern == "AN3":
        ja_r2_text = t1.load_text(f"{baseline_from}/task_a_ja/AN_r2.md")
        reused_ja = True
    else:  # AN2
        if "AN2" not in ja_cache:
            chain = run_ja_chain(client, inputs, JA_PATTERN_TEXT["AN2"], "AN2")
            t1.save_text(f"{out_dir}/task_a_ja/AN2_original.md", chain["original"]["text"])
            t1.save_text(f"{out_dir}/task_a_ja/AN2_r1.md", chain["r1"]["text"])
            t1.save_text(f"{out_dir}/task_a_ja/AN2_r2.md", chain["r2"]["text"])
            ja_cache["AN2"] = chain["r2"]["text"]
        ja_r2_text = ja_cache["AN2"]

    if ja_pattern == "AN3" and t_variant == "T0":
        en_text = t1.load_text(f"{baseline_from}/task_a_advanced/AN.md")
        deviation = t1.load_json(f"{baseline_from}/task_a_advanced/AN_deviation.json")
        rubric = t1.load_json(f"{baseline_from}/task_a_advanced/AN_rubric.json")
        reused_en = True
    elif t_variant == "T0":
        adv = run_advanced_translation_t0(client, ja_r2_text)
        en_text = adv["text"]
        deviation = t1.run_essential_fact_check(client, ledger_text, en_text, source_article_text=ja_r2_text)
        rubric = t1.run_rubric_eval(client, a0_en_text, en_text)
    else:  # T1(AN3-T1 or AN2-T1、常に新規生成)
        adv = run_advanced_translation_t1(client, ja_r2_text)
        en_text = adv["text"]
        deviation = t1.run_essential_fact_check(client, ledger_text, en_text, source_article_text=ja_r2_text)
        rubric = t1.run_rubric_eval(client, a0_en_text, en_text)

    ja_metrics_old = t1.count_numeric_tokens(ja_r2_text)
    ja_metrics_old["entity_count"] = len(t1.extract_entities_ja(ja_r2_text))
    ja_metrics_old["entities"] = sorted(t1.extract_entities_ja(ja_r2_text))
    ja_metrics_old["word_count"] = t1.word_count(ja_r2_text)
    ja_metrics_improved = improved_metrics(ja_r2_text, "ja")

    en_metrics_old = t1.count_numeric_tokens(en_text)
    en_metrics_old["entity_count"] = len(t1.extract_entities_en(en_text))
    en_metrics_old["entities"] = sorted(t1.extract_entities_en(en_text))
    en_metrics_old["word_count"] = t1.word_count(en_text)
    en_metrics_improved = improved_metrics(en_text, "en")

    name_unit_diff = build_name_unit_diff_table(
        extract_entities_ja_improved(ja_r2_text), extract_entities_en_improved(en_text))
    new_en_entities = [r["canonical"] for r in name_unit_diff if r["en_new_vs_ja"]]

    t1.save_text(f"{out_dir}/cells/{cell_id}_ja.md", ja_r2_text)
    t1.save_text(f"{out_dir}/cells/{cell_id}_en.md", en_text)
    t1.save_json(f"{out_dir}/cells/{cell_id}_deviation.json", deviation)
    t1.save_json(f"{out_dir}/cells/{cell_id}_rubric.json", rubric)

    result = {
        "cell_id": cell_id, "reused_ja": reused_ja, "reused_en": reused_en,
        "ja_metrics_old": ja_metrics_old, "ja_metrics_improved": ja_metrics_improved,
        "en_metrics_old": en_metrics_old, "en_metrics_improved": en_metrics_improved,
        "name_unit_diff": name_unit_diff, "new_en_entities_vs_ja": new_en_entities,
        "deviation_overall_status": (deviation or {}).get("parsed", {}).get("overall_status"),
        "rubric": rubric,
    }
    t1.save_json(f"{out_dir}/cells/{cell_id}_summary.json", result)
    return result


# ------------------------------------------------------------
# ユーザー確認用成果物(本文読み比べ)
# ------------------------------------------------------------
ARTICLE_LABELS = {"hormuz": "Hormuz(ホルムズ海峡)", "meta": "Meta(Museの人間対応)"}
CELL_LABELS = {
    "Baseline": "Baseline(A0 + 現行英語化)",
    "AN3-T0": "AN3-T0(A3+N2 + 現行英語化)",
    "AN3-T1": "AN3-T1(A3+N2 + 抑制追記英語化)",
    "AN2-T0": "AN2-T0(A2+N2 + 現行英語化)",
    "AN2-T1": "AN2-T1(A2+N2 + 抑制追記英語化)",
}


def _cell_row_md(label: str, ja_text: str, en_text: str, metrics: dict | None) -> list:
    lines = [f"## {label}\n"]
    if metrics:
        lines.append(
            f"- 数字(旧/改良は数字のみ旧カウンタ共通): JA={metrics['ja_metrics_old']['numeric_token_count']} "
            f"(過度精度{metrics['ja_metrics_old']['over_precision_count']}) / "
            f"EN={metrics['en_metrics_old']['numeric_token_count']} "
            f"(過度精度{metrics['en_metrics_old']['over_precision_count']})")
        lines.append(
            f"- 固有名詞: JA 旧={metrics['ja_metrics_old']['entity_count']} "
            f"改良={metrics['ja_metrics_improved']['entity_count_improved']} / "
            f"EN 旧={metrics['en_metrics_old']['entity_count']} "
            f"改良={metrics['en_metrics_improved']['entity_count_improved']}")
        lines.append(f"- JA->ENで新規出現した固有名詞(改良カウンタ, 名称単位): "
                      f"{metrics['new_en_entities_vs_ja'] or 'なし'}")
        lines.append(f"- Ledger Deviation Check: **{metrics['deviation_overall_status']}**")
        if metrics.get("rubric"):
            r = metrics["rubric"]
            lines.append(
                f"- rubric: causality={r['storyline_causality_score']} "
                f"entertainment={r['entertainment_score']} "
                f"comprehension={r['comprehension_score']} thinness={r['thinness_score']}")
    lines.append("\n**[JA]**\n")
    lines.append(ja_text.strip())
    lines.append("\n**[EN]**\n")
    lines.append(en_text.strip())
    lines.append("")
    return lines


def build_comparison_markdown(article: str, out_dir: str, baseline_from: str) -> str:
    summary = t1.load_json(f"{out_dir}/matrix_summary.json")
    baseline_ja = t1.load_text(f"{baseline_from}/task_a_ja/A0_r2.md")
    baseline_en = t1.load_text(f"{baseline_from}/task_a_advanced/A0.md")

    lines = [f"# {ARTICLE_LABELS.get(article, article)} 本文比較({TRIAL_TAG})\n"]
    lines += _cell_row_md(CELL_LABELS["Baseline"], baseline_ja, baseline_en, None)
    for cell_id in CELL_IDS:
        if cell_id not in summary:
            continue
        ja_text = t1.load_text(f"{out_dir}/cells/{cell_id}_ja.md")
        en_text = t1.load_text(f"{out_dir}/cells/{cell_id}_en.md")
        lines += _cell_row_md(CELL_LABELS[cell_id], ja_text, en_text, summary[cell_id])
    md_text = "\n".join(lines)
    t1.save_text(f"{out_dir}/comparison_{article}.md", md_text)
    return md_text


def _html_escape(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def build_html_index(articles: list, out_dir_root: str, html_out: str) -> None:
    sections = []
    for article in articles:
        out_dir = f"{out_dir_root}/{article}"
        summary = t1.load_json(f"{out_dir}/matrix_summary.json")
        baseline_ja = t1.load_text(f"er037_output/family_xy_concreteness_control_trial_01/{article}/task_a_ja/A0_r2.md")
        baseline_en = t1.load_text(f"er037_output/family_xy_concreteness_control_trial_01/{article}/task_a_advanced/A0.md")
        cards = []
        cell_order = ["Baseline"] + CELL_IDS
        texts = {"Baseline": (baseline_ja, baseline_en, None)}
        for cell_id in CELL_IDS:
            if cell_id in summary:
                ja_text = t1.load_text(f"{out_dir}/cells/{cell_id}_ja.md")
                en_text = t1.load_text(f"{out_dir}/cells/{cell_id}_en.md")
                texts[cell_id] = (ja_text, en_text, summary[cell_id])
        for cell_id in cell_order:
            if cell_id not in texts:
                continue
            ja_text, en_text, metrics = texts[cell_id]
            metrics_html = ""
            if metrics:
                metrics_html = (
                    f"<p class='metrics'>数字 JA={metrics['ja_metrics_old']['numeric_token_count']} "
                    f"EN={metrics['en_metrics_old']['numeric_token_count']} | "
                    f"固有名詞(改良) JA={metrics['ja_metrics_improved']['entity_count_improved']} "
                    f"EN={metrics['en_metrics_improved']['entity_count_improved']} | "
                    f"JA-&gt;EN新規固有名詞={_html_escape(str(metrics['new_en_entities_vs_ja']) or '[]')} | "
                    f"Deviation=<b>{metrics['deviation_overall_status']}</b></p>"
                )
            cards.append(f"""
        <div class="cell-card">
          <h3>{_html_escape(CELL_LABELS.get(cell_id, cell_id))}</h3>
          {metrics_html}
          <div class="col2">
            <div class="ja-col"><h4>JA</h4><pre>{_html_escape(ja_text.strip())}</pre></div>
            <div class="en-col"><h4>EN</h4><pre>{_html_escape(en_text.strip())}</pre></div>
          </div>
        </div>""")
        sections.append(f"""
      <section id="{article}">
        <h2>{_html_escape(ARTICLE_LABELS.get(article, article))}</h2>
        {''.join(cards)}
      </section>""")

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02 本文読み比べ</title>
<style>
body {{ font-family: -apple-system, "Hiragino Kaku Gothic ProN", sans-serif; margin: 24px; max-width: 1400px; }}
h1 {{ font-size: 1.4em; }}
h2 {{ border-bottom: 2px solid #333; margin-top: 40px; }}
.cell-card {{ border: 1px solid #ccc; border-radius: 8px; padding: 12px; margin: 16px 0; }}
.col2 {{ display: flex; gap: 16px; }}
.ja-col, .en-col {{ flex: 1; min-width: 0; }}
pre {{ white-space: pre-wrap; word-wrap: break-word; background: #f7f7f7; padding: 8px; border-radius: 4px; }}
.metrics {{ font-size: 0.85em; color: #444; background: #eef; padding: 6px; border-radius: 4px; }}
nav a {{ margin-right: 12px; }}
</style>
</head>
<body>
<h1>FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02: Hormuz/Meta 本文読み比べ
(Baseline / AN3-T0 / AN3-T1 / AN2-T0 / AN2-T1)</h1>
<p>Standard/Advanced: AN3=A3+N2、AN2=A2+N2。T0=現行英語化Prompt、T1=Trial限定の抑制追記。</p>
<nav>{''.join(f'<a href="#{a}">{_html_escape(ARTICLE_LABELS.get(a, a))}</a>' for a in articles)}</nav>
{''.join(sections)}
</body>
</html>
"""
    os.makedirs(os.path.dirname(html_out), exist_ok=True)
    with open(html_out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] html index written: {html_out}")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--article", choices=list(t1.ARTICLE_SOURCES.keys()))
    p.add_argument("--cells", default="")
    p.add_argument("--baseline-from", default="")
    p.add_argument("--out-dir", default="")
    p.add_argument("--budget-jpy", type=float, default=70.0)
    p.add_argument("--investigate-entities", action="store_true")
    p.add_argument("--from", dest="from_dir", default="")
    p.add_argument("--out", dest="out_path", default="")
    p.add_argument("--build-comparison", action="store_true")
    p.add_argument("--build-html-index", action="store_true")
    p.add_argument("--html-out", default="user_test/concreteness_trial_02/index.html")
    return p


def main() -> None:
    args = build_arg_parser().parse_args()

    if args.investigate_entities:
        investigate_entities(args.from_dir, args.out_path)
        return

    if args.build_comparison:
        out_dir = f"{args.out_dir}/{args.article}"
        build_comparison_markdown(args.article, out_dir, args.baseline_from)
        return

    if args.build_html_index:
        build_html_index(list(t1.ARTICLE_SOURCES.keys()), args.out_dir, args.html_out)
        return

    out_dir = f"{args.out_dir}/{args.article}"
    os.makedirs(out_dir, exist_ok=True)
    t1.cl.install(f"{out_dir}/raw_usage_log.jsonl")

    client = vfl01.get_client()
    inputs = t1.load_article_inputs(args.article)

    cells = [c.strip() for c in args.cells.split(",") if c.strip()]
    ja_cache: dict = {}
    summary = {}
    for cell_id in cells:
        result = run_cell(client, args.article, cell_id, inputs, out_dir, args.baseline_from, ja_cache)
        summary[cell_id] = result
        t1.budget_check(out_dir, args.budget_jpy)

    t1.merge_save_json(f"{out_dir}/matrix_summary.json", summary)
    final_cost = t1.budget_check(out_dir, args.budget_jpy)
    t1.save_json(f"{out_dir}/cost_matrix.json",
                  t1.fxrunner.compute_stage_cost_breakdown(f"{out_dir}/raw_usage_log.jsonl"))
    print(f"[DONE] article={args.article} cells={cells} total_jpy={final_cost:.3f}")


if __name__ == "__main__":
    main()
