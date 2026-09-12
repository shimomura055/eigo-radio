# ============================================================
# er011_news_point_quality_generalization_trial_16_run.py
# FAMILY-A-NEWS-POINT-QUALITY-GENERALIZATION-HUBBLE-SATURN-TRIAL-16
# (Lane A, Sonnet委任)
# ============================================================
# 目的(ユーザー決定 2026-09-12、委任文どおり): Hanshin系Trial(12/12b/14/15)
# で得られた仮説「Fact数そのものではなく、Pointに使える非headlineの周辺
# Factの質が重要」が、異なるNewsテーマ(英語一次情報源、NASA/ESAの
# Hubble宇宙望遠鏡による土星南極の異常な形状発見)でも再現するかを確認する。
# 採用テーマ(ユーザー指定、変更禁止): "New Hubble images reveal an unusual
# shape over Saturn's south pole" / 「ハッブル宇宙望遠鏡が土星の南極に
# 捉えた奇妙な形」。
#
# **Trial(Production実装ではない)**。Production/Prompt/QA/Validator/retry
# コード・SSOT(OPEN_ITEMS.md/DECISION_LOG.md/CURRENT_SPEC.md/
# ARTIFACT_REGISTRY.md)・docs/pm/ACTIVE_TASK.md/RESULT_PACKET.md・Git操作は
# 一切行わない。monkeypatch・グローバル書き換えなし。単純にfact数を増やす
# Trialへは戻さない(委任文の明示禁止)。
#
# 設計(Hanshin系Trial-12b/14条件A/Eの再現、fact総数を条件間で揃える):
#   条件H(headlineのみ、条件Aに相当): base 5件(headlineそのものを構成する
#     直接的事実)+ headline角度の追加fact 2件 = usable 7件
#   条件P(headline+非headline周辺fact、条件D/Eに相当): base 5件 +
#     非headline周辺fact 2件(観測手段の比較・過去観測との対比等) = usable 7件
#   fact総数(7件)を条件間で完全に一致させることで、「数」ではなく「角度」
#   の効果を分離する(委任文の明示要求)。
#
# 分類規則(機械的+目視、根拠を明記): 新規research(1回のWeb検索API実行、
# Production関数 er002_ja_web_research_r3.make_writer_research_fn を無改変で
# 直接呼び出す)で得た検証済みFactのうち、
#   - headline_group: 「何が観測されたか」という発見そのもの(形状・場所・
#     観測日・観測機器・見た目の記述)を構成する事実。これが無いと記事の
#     Main Story(見出しの内容)自体が成立しない。
#   - peripheral_group: 見出しの成立には不要だが、Point One/Twoに別角度を
#     供給できる事実(過去の観測との比較、他の天体の類似現象との比較、
#     観測技術上のメカニズム、研究者の見解、今後の観測計画等)。
# の2群に、本Sonnetが目視で分類する(キーワード自動判定ではなく、内容の
# 意味を読んで判断する。分類結果とその理由はresearch_classification.jsonへ
# 記録する)。
#
# OPEN-146観測(自然発火の記録、人工的に発火させない): Ledger構築後、
# Production関数 er011_open146_ledger_canonical_en_spelling_production_01.
# make_proper_noun_extraction_fn を無改変で条件H/P Ledger本文に対して実行し、
# 日本語表記のみの固有名詞候補が検出されるか(=canonical_en_spelling機構が
# 発火するか)を観測する。英語一次情報源テーマのため非発火が予想されるが、
# それ自体も記録する(委任文どおり)。
#
# 再利用(import・無変更、コピー改変はしない):
#   - er011_point_role_planning_focus_connection_trial_03(t3、既存
#     VALIDATED Trial): run_one_pattern_connected / load_text / vfl01 / ab01
#     / r3(t3内でimport済み)。
#   - er011_daily_news_focus_layer_comparison_trial_04(t4): analyze_run /
#     load_role_planning_used / LEVELS。
#   - er011_news_ledger_enrichment_ab_trial_12_run(t12): USD_JPY /
#     _call_cost_usd / evidence_allocation_metrics / load_initial_flag。
#   - er011_news_ledger_enrichment_leaveout_trial_12b_run(t12b): load_text /
#     load_initial_attempt0_qa / evidence_allocation_metrics(委任文の
#     evidence_allocation指標を再利用)。
#   - er003_v1_n3_01_articles_generate(prod_gen): build_common_block /
#     build_prompt。
#   - er011_open146_ledger_canonical_en_spelling_production_01(canon_spelling):
#     has_canonical_en_spelling / make_proper_noun_extraction_fn /
#     parse_proper_noun_extraction_output / run_canonical_spelling_research /
#     build_canonical_spelling_ledger_section /
#     append_canonical_spelling_instruction_if_present /
#     build_canonical_spelling_fact_check_block(観測のみ、Fact Checker側は
#     firing想定が0件の場合は使用しない。0件でなかった場合はREPORTに追記の
#     うえ、Trial限定の追加呼び出しとして正直に記録する)。
#
# 書き込み範囲: er011_output/news_point_quality_generalization_hubble_
# saturn_trial_16/ のみ(新規ディレクトリ)。既存Trial-12/12b/14/15の成果物
# は一切変更しない。
#
# 費用上限: ¥300(Ledger研究≈¥150+記事12本)。TTSは実行しない
# (text-onlyまで)。combo単位で逐次実行し、実行前に都度
# compute_cost_so_far_jpy()で確認する(前面同期のみ、バックグラウンド
# 待機・二重起動なし)。
# ============================================================
from __future__ import annotations

import json
import os
import re
import time
from collections import defaultdict

import er002_ja_web_research_r3 as r3
import er003_v1_n3_01_articles_generate as prod_gen
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er011_daily_news_focus_layer_comparison_trial_04 as t4
import er011_news_ledger_enrichment_ab_trial_12_run as t12
import er011_news_ledger_enrichment_leaveout_trial_12b_run as t12b
import er011_open146_ledger_canonical_en_spelling_production_01 as canon_spelling
import er011_point_role_planning_focus_connection_trial_03 as t3

THEME_ID = "news_point_quality_generalization_hubble_saturn_trial_16"
OUT_BASE = f"er011_output/{THEME_ID}"
LOG_PATH = f"{OUT_BASE}/raw_usage_log.jsonl"
BUDGET_JPY = 300.0

USD_JPY = t12.USD_JPY
_call_cost_usd = t12._call_cost_usd

# ユーザー指定テーマ(変更禁止)。TOPIC_JAはWriterプロンプトの「今回の
# テーマ」欄へそのまま挿入する短い日本語説明(他Trialと同一の使い方、
# Hanshin系のHANSHIN_TOPIC_JAに相当)。research_stage()で確認した事実
# (FACT-01〜05、decagon wave、南緯58〜63度、2026年9月2日発表)に基づき
# 確定した文言(research実行後に確定、以降変更しない)。
TOPIC_JA = (
    "NASAとESAのハッブル宇宙望遠鏡による観測から、土星の南極(南緯58〜63度"
    "付近)を取り巻く、これまで確認されていなかった巨大な十角形(decagon)の"
    "大気波が見つかった。2025年8月29日に撮影された画像を含む複数年分の観測"
    "データに基づき、2026年9月2日にNASA・ESAが公式発表し、同日付で論文が"
    "Science Advances誌にオンライン掲載された。"
)

LEVELS = t4.LEVELS
LABEL_LOOKUP = {label: (label, instruction, level_dir, stage_tag)
                for (label, instruction, level_dir, stage_tag) in LEVELS}


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def compute_cost_so_far_jpy() -> float:
    if not os.path.exists(LOG_PATH):
        return 0.0
    total_usd = 0.0
    with open(LOG_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            total_usd += _call_cost_usd(json.loads(line))
    return total_usd * USD_JPY


def check_budget_or_raise():
    cost_so_far = compute_cost_so_far_jpy()
    if cost_so_far > BUDGET_JPY:
        raise RuntimeError(f"費用上限超過見込み(実測¥{cost_so_far:.1f} > 上限¥{BUDGET_JPY})。STOPします。")
    return cost_so_far


# ============================================================
# 段階1: 新規Ledger研究(Web検索、Production関数を無改変で1回実行)
# ============================================================
RESEARCH_PROMPT = """あなたは事実確認を重視する調査アシスタントです。以下のニュースについて、
Web検索で検証済みの事実を調査してください。

【調査対象のニュース】
2026年、NASA・ESA(ハッブル宇宙望遠鏡)が新たに撮影した土星の画像で、南極
(south polar region)上空に、これまでの観測では見られなかった、または
これまでの観測と異なる、珍しい/奇妙な形状(unusual shape)の現象が確認
された、という発表(英語圏の一次情報源: NASA/ESA/STScI等の公式発表・
プレスリリース)。

【調査してほしいこと】
このニュースについて、複数の独立した情報源(NASA公式・ESA公式・STScI
(Space Telescope Science Institute)公式・信頼できる宇宙科学メディア等)
を確認しながら、以下の両方を含む形で確認済み事実を10件程度調査してくだ
さい。

(A) 発見そのものを構成する事実(見出しの成立に必須、例):
- 具体的にどのような形状/現象が観測されたか(できるだけ具体的に)
- いつ撮影されたか(観測日・発表日)
- どの観測機器・望遠鏡・装置で撮影されたか
- 土星のどの位置(南極、緯度等)で観測されたか
- 誰が(どの機関・チーム)発表したか

(B) 見出しの成立には不要だが、記事の別角度になり得る周辺事実(例):
- 過去の土星南極/北極の観測(Cassini探査機によるものを含む)との比較
- 他の惑星(木星等)の極域で見られる類似現象との比較
- この形状が生じるメカニズムについての研究者の見解・仮説(確定していない
  場合はその旨明記)
- 今後の追加観測・研究計画(JWST等との連携を含む)
- この観測がハッブル宇宙望遠鏡の性能・運用年数の文脈でどう位置づけられるか

【出力形式(厳守、既存Ledger形式と同一)】
各Factについて、以下の形式で出力してください(FACT-01から開始し連番で)。
実際に複数ソースで確認できたことだけを書いてください。1ソースでしか
確認できなかった事実はconfidenceを「中」とし、その旨をnotesに明記して
ください。存在しない事実を創作しないでください。検証できなかった項目は
無理に含めないでください。

[CONFIRMED_FACT] FACT-XX: (事実の内容、1-3文程度)
  source: (実際に参照した情報源名)
  date_or_period: (いつの事実か)
  confidence: 高 or 中
  number_classification: ANCHOR or SUPPORTING or DISPENSABLE
    (記事の核心に近いほどANCHOR/SUPPORTING、周辺情報はDISPENSABLE)
  exactness_requirement: EXACT_REQUIRED or APPROXIMATE_OK
  usable: yes
  notes: (検証時の注意点があれば)

最後に、参照した情報源のタイトルとURLを一覧で列挙してください。
"""


def research_stage() -> dict:
    os.makedirs(OUT_BASE, exist_ok=True)
    cl.install(LOG_PATH)
    client = t3.vfl01.get_client()
    research_fn = r3.make_writer_research_fn(RESEARCH_PROMPT, client=client, reasoning_effort="high")
    theme_tag = f"{THEME_ID}_research"
    t0 = time.time()
    with cl.logging_context(theme_tag, "ledger_research"):
        text, model, response_id, search_usage, sources = research_fn()
    elapsed = round(time.time() - t0, 2)
    result = {
        "model": model, "response_id": response_id, "raw_text": text,
        "web_search_call_count": search_usage["web_search_call_count"],
        "queries": search_usage.get("queries"), "sources": sources,
        "elapsed_seconds": elapsed,
    }
    with open(f"{OUT_BASE}/research_raw_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] research_stage完了: web_search_call_count="
          f"{search_usage['web_search_call_count']}, sources={len(sources)}件, elapsed={elapsed}s")
    print(text)
    return result


# ============================================================
# 段階2: Fact分類(機械的+目視、根拠を明記)+Ledger H/P構築
# ============================================================
FACT_BLOCK_RE = re.compile(r"\n\[CONFIRMED_FACT\] FACT-(\d{2}):")


def _extract_fact_blocks(raw_text: str) -> dict:
    """research_stage()のraw_text(既存Ledger形式と同一のFACTブロック)から
    fact_id -> ブロック本文(strip()のみ、文言変更なし)の辞書を作る。
    最後のブロックは、Markdown見出し"## 参照情報源一覧"の直前までを本文と
    する(このresearch呼び出し特有の出力構造、Hanshin系t12b._extract_
    fact_blocksとは終端マーカー文字列が異なるため、本Trial用に軽量に
    独立実装する。ロジック自体[正規表現でブロック単位に切り出す]は同一)。"""
    matches = list(FACT_BLOCK_RE.finditer(raw_text))
    blocks = {}
    for i, m in enumerate(matches):
        fact_id = m.group(1)
        start = m.start() + 1
        end = matches[i + 1].start() if i + 1 < len(matches) else raw_text.find("## 参照情報源一覧")
        block_text = raw_text[start:end]
        cut = block_text.find("\n## ")
        if cut != -1:
            block_text = block_text[:cut]
        blocks[fact_id] = block_text.strip()
    return blocks


# 分類規則(目視、根拠はREPORT本体に詳細記載): headline_groupは「何が・
# いつ・どこで・どの機材で・誰が発表したか」という発見そのものの成立に
# 必須な事実。peripheral_groupは、見出しの成立には不要だが、過去観測との
# 比較・発生メカニズムの仮説等、Point One/Twoに別角度を供給できる事実。
HEADLINE_BASE_IDS = ["01", "02", "03", "04", "05"]  # base 5件(現象そのもの・発表・撮影日時/機材・位置・発見経緯)
HEADLINE_ANGLE_ADDITIONAL_IDS = ["06", "07"]  # 条件H専用(headline角度の追加、同一現象のさらなる物理的記述)
PERIPHERAL_IDS = ["08", "09"]  # 条件P専用(過去観測との比較/発生メカニズムの仮説、別角度)
UNUSED_IDS = ["10", "11"]  # 条件H/Pいずれにも不使用(木星比較・今後の計画、記録のためLedgerには含めない)

CLASSIFICATION_RATIONALE = {
    "01": "十角形の大気波そのものの発見内容(形状・構造)。見出しの核心。",
    "02": "公式発表日・発表機関・査読論文情報(誰が・いつ発表したか)。見出しの成立に必須。",
    "03": "実際にHubbleが撮影した日付・観測装置・観測提案(いつ・どの機材で撮影したか)。",
    "04": "十角形の位置(南緯58〜63度)。見出しの「どこで」に必須。",
    "05": "発見の経緯(2024年の地上観測での気づき、2023年までの遡及確認)。発見そのものの時系列の一部。",
    "06": "複数波長画像により3次元的な波動構造と判明(同一現象のさらなる物理的記述、新しい別角度ではない)。",
    "07": "波の移動速度とジェット気流速度の対比(同一現象の物理的性質のさらなる数値、新しい別角度ではない)。",
    "08": "過去のVoyager/Cassini観測ではこの現象が確認されていない(歴史的比較という別角度、見出しの成立には不要)。",
    "09": "発生メカニズムは未確定、複数の仮説(mechanism/limitationという別角度、見出しの成立には不要)。",
    "10": "木星の極域サイクロンとの比較(未使用、別角度だがH/P比較の主眼[Point Role候補: mechanism/beyond-the-headline]と重複するため今回は不使用)。",
    "11": "今後の観測計画・Hubbleの運用年数(未使用、future outlookの別角度だが今回はfact総数7件に揃えるため不使用)。",
}

LEDGER_H_PATH = f"{OUT_BASE}/ledger_condition_h_headline_only.txt"
LEDGER_P_PATH = f"{OUT_BASE}/ledger_condition_p_headline_plus_peripheral.txt"

USABLE_FACT_COUNT_H = len(HEADLINE_BASE_IDS) + len(HEADLINE_ANGLE_ADDITIONAL_IDS)  # 7
USABLE_FACT_COUNT_P = len(HEADLINE_BASE_IDS) + len(PERIPHERAL_IDS)  # 7

LEDGER_HEADER = """=== Verified Fact Ledger: Hubble/Saturn Decagon Wave(FAMILY-A-NEWS-POINT-QUALITY-GENERALIZATION-HUBBLE-SATURN-TRIAL-16) ===
作成方法: Production Research関数(er002_ja_web_research_r3.make_writer_research_fn、
無改変)による1回のWeb検索API実行(web_search_call_count=14、情報源21件)で取得した
検証済みFactのうち、以下で採用したFACT-IDのブロックのみを機械的に抽出し、文言を一切
変更せずそのまま連結したものである。全文は{out_base}/research_raw_result.jsonを参照。

"""

LEDGER_FOOTER_TEMPLATE = """

=== usable fact数の集計(Trial実施者による機械集計) ===
条件: {condition_label}
採用FACT-ID: {included}
usable(ANCHOR+SUPPORTING)合計 = {count}件
"""


def build_ledgers_stage() -> dict:
    os.makedirs(OUT_BASE, exist_ok=True)
    with open(f"{OUT_BASE}/research_raw_result.json", encoding="utf-8") as f:
        research_result = json.load(f)
    fact_blocks = _extract_fact_blocks(research_result["raw_text"])
    expected_ids = set(HEADLINE_BASE_IDS) | set(HEADLINE_ANGLE_ADDITIONAL_IDS) | set(PERIPHERAL_IDS) | set(UNUSED_IDS)
    missing = expected_ids - set(fact_blocks.keys())
    if missing:
        raise RuntimeError(f"抽出できなかったFACTブロックがあります: {missing}")
    for fid in expected_ids:
        if not fact_blocks[fid].startswith(f"[CONFIRMED_FACT] FACT-{fid}:"):
            raise RuntimeError(f"FACT-{fid}ブロックの抽出結果が不正です(先頭不一致): {fact_blocks[fid][:60]!r}")

    header = LEDGER_HEADER.format(out_base=OUT_BASE)

    def build(included_ids: list, label: str) -> str:
        blocks_text = "\n\n".join(fact_blocks[fid] for fid in included_ids)
        footer = LEDGER_FOOTER_TEMPLATE.format(
            condition_label=label, included="/".join(included_ids), count=len(included_ids))
        return header + blocks_text + footer

    ledger_h_text = build(HEADLINE_BASE_IDS + HEADLINE_ANGLE_ADDITIONAL_IDS,
                           "条件H(headlineのみ、base5+headline角度追加2)")
    ledger_p_text = build(HEADLINE_BASE_IDS + PERIPHERAL_IDS,
                           "条件P(headline+非headline周辺fact、base5+周辺2)")

    with open(LEDGER_H_PATH, "w", encoding="utf-8") as f:
        f.write(ledger_h_text)
    with open(LEDGER_P_PATH, "w", encoding="utf-8") as f:
        f.write(ledger_p_text)

    # 健全性チェック: 各条件のfact数が7件、H/Pで異なる集合、baseは共通
    for fid in HEADLINE_BASE_IDS:
        assert f"[CONFIRMED_FACT] FACT-{fid}:" in ledger_h_text
        assert f"[CONFIRMED_FACT] FACT-{fid}:" in ledger_p_text
    for fid in HEADLINE_ANGLE_ADDITIONAL_IDS:
        assert f"[CONFIRMED_FACT] FACT-{fid}:" in ledger_h_text
        assert f"[CONFIRMED_FACT] FACT-{fid}:" not in ledger_p_text
    for fid in PERIPHERAL_IDS:
        assert f"[CONFIRMED_FACT] FACT-{fid}:" not in ledger_h_text
        assert f"[CONFIRMED_FACT] FACT-{fid}:" in ledger_p_text
    for fid in UNUSED_IDS:
        assert f"[CONFIRMED_FACT] FACT-{fid}:" not in ledger_h_text
        assert f"[CONFIRMED_FACT] FACT-{fid}:" not in ledger_p_text

    classification_record = {
        "headline_base_ids": HEADLINE_BASE_IDS,
        "headline_angle_additional_ids_condition_h_only": HEADLINE_ANGLE_ADDITIONAL_IDS,
        "peripheral_ids_condition_p_only": PERIPHERAL_IDS,
        "unused_ids": UNUSED_IDS,
        "rationale": CLASSIFICATION_RATIONALE,
        "usable_fact_count_h": USABLE_FACT_COUNT_H,
        "usable_fact_count_p": USABLE_FACT_COUNT_P,
        "classification_rule": (
            "headline_group: 発見そのもの(何が・いつ・どこで・どの機材で・誰が発表したか)の"
            "成立に必須な事実。peripheral_group: 見出しの成立には不要だが、過去観測との比較・"
            "発生メカニズムの仮説等、Point One/Twoに別角度を供給できる事実。目視判定(自動"
            "キーワード判定ではない)。"
        ),
    }
    with open(f"{OUT_BASE}/research_classification.json", "w", encoding="utf-8") as f:
        json.dump(classification_record, f, ensure_ascii=False, indent=2)
    print(f"[{THEME_ID}] build_ledgers_stage完了: 条件H={len(ledger_h_text)}文字, "
          f"条件P={len(ledger_p_text)}文字")
    return {"ledger_h_chars": len(ledger_h_text), "ledger_p_chars": len(ledger_p_text)}


# ============================================================
# 段階3: OPEN-146観測(自然発火の有無、Production関数を無改変で実行)
# ============================================================
def open146_firing_check_stage() -> dict:
    client = t3.vfl01.get_client()
    results = {}
    for cond_name, ledger_path in (("condition_h", LEDGER_H_PATH), ("condition_p", LEDGER_P_PATH)):
        ledger_text = load_text(ledger_path)
        already_has_field = canon_spelling.has_canonical_en_spelling(ledger_text)
        extraction_fn = canon_spelling.make_proper_noun_extraction_fn(ledger_text, client=client)
        theme_tag = f"{THEME_ID}_open146_{cond_name}"
        t0 = time.time()
        with cl.logging_context(theme_tag, "open146_proper_noun_extraction"):
            raw_text, model, response_id = extraction_fn()
        elapsed = round(time.time() - t0, 2)
        try:
            entities = canon_spelling.parse_proper_noun_extraction_output(raw_text)
            parse_error = None
        except canon_spelling.ProperNounExtractionSchemaError as e:
            entities = None
            parse_error = str(e)
        results[cond_name] = {
            "ledger_already_has_canonical_en_spelling_field": already_has_field,
            "raw_text": raw_text, "model": model, "response_id": response_id,
            "entities": entities, "parse_error": parse_error,
            "fired": bool(entities), "elapsed_seconds": elapsed,
        }
        print(f"[{THEME_ID}] open146_firing_check {cond_name}: entities={entities} elapsed={elapsed}s")
    with open(f"{OUT_BASE}/open146_firing_check.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    return results


# ============================================================
# 段階4: 記事生成(N=6/条件、A2×3+B1B×3、計12本)
# ============================================================
CONDITIONS = {
    "condition_h": {"ledger_path": LEDGER_H_PATH, "usable_fact_count": USABLE_FACT_COUNT_H,
                    "out_subdir": f"{OUT_BASE}/condition_h"},
    "condition_p": {"ledger_path": LEDGER_P_PATH, "usable_fact_count": USABLE_FACT_COUNT_P,
                    "out_subdir": f"{OUT_BASE}/condition_p"},
}


def run_one_combo(client, master_full_text: str, condition_name: str, run_idx: int, label: str,
                   instruction: str, level_dir: str, stage_tag: str) -> dict:
    cond = CONDITIONS[condition_name]
    raw_ledger_text = load_text(cond["ledger_path"])
    # OPEN-146-LEDGER-CANONICAL-EN-SPELLING-PRODUCTION-WIRING-01と同一の
    # wiring point(Production run_theme()と同一呼び出し、無改変)。
    # canonical_en_spelling行が無いLedgerではno-op(byte不変)であり、
    # 段階3の観測結果どおり本Trialでは常にno-opになる想定。
    ledger_text = canon_spelling.append_canonical_spelling_instruction_if_present(raw_ledger_text)
    out_dir = f"{cond['out_subdir']}/{level_dir}/run{run_idx}"
    common_block = prod_gen.build_common_block(
        master_full_text, TOPIC_JA, ledger_text, editorial_type_module_block="")
    prompt = prod_gen.build_prompt(common_block, instruction)
    theme_tag = f"{THEME_ID}_{condition_name}_{level_dir}_run{run_idx}"
    t0 = time.time()
    with cl.logging_context(theme_tag, stage_tag):
        result = t3.run_one_pattern_connected(
            client, theme_tag, label, prompt, ledger_text, TOPIC_JA, out_dir,
            point_role_hint_block="")
    elapsed = round(time.time() - t0, 2)
    analysis = t4.analyze_run(out_dir, result)
    analysis["elapsed_seconds"] = elapsed
    analysis["condition"] = condition_name
    analysis["level"] = label
    analysis["run"] = run_idx
    analysis.update(t12.load_initial_flag(out_dir))
    analysis.update(t12b.load_initial_attempt0_qa(out_dir))
    analysis["evidence_allocation"] = t12.evidence_allocation_metrics(
        out_dir, analysis["retry_attempts"], cond["usable_fact_count"])
    if analysis["point_one_overlap_ratio"] is not None and analysis["point_two_overlap_ratio"] is not None:
        analysis["gate_indicator_max_overlap"] = max(
            analysis["point_one_overlap_ratio"], analysis["point_two_overlap_ratio"])
    else:
        analysis["gate_indicator_max_overlap"] = None
    analysis["final_ng"] = result.get("status") != "OK"
    with open(f"{out_dir}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in result.items() if k != "article_text"}, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{out_dir}/analysis.json", "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] {condition_name} {level_dir} run{run_idx}: status={result.get('status')} "
          f"retry={analysis['retry_attempts']} initial_value_qa={analysis['initial_value_qa_label']} "
          f"fact_verdict={analysis.get('fact_verdict')} elapsed={elapsed}s")
    return analysis


def combo_stage(condition_name: str, label: str, run_idx: int) -> dict:
    cond = CONDITIONS[condition_name]
    os.makedirs(cond["out_subdir"], exist_ok=True)
    cl.install(LOG_PATH)
    cost_so_far = check_budget_or_raise()
    client = t3.vfl01.get_client()
    master_full_text = t3.ab01.load_master_full_text()
    _, instruction, level_dir, stage_tag = LABEL_LOOKUP[label]
    analysis = run_one_combo(client, master_full_text, condition_name, run_idx, label, instruction,
                              level_dir, stage_tag)
    combo_results_dir = f"{OUT_BASE}/_combo_results"
    os.makedirs(combo_results_dir, exist_ok=True)
    with open(f"{combo_results_dir}/{condition_name}_{level_dir}_run{run_idx}.json", "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] combo_stage完了、事前cost_so_far=¥{cost_so_far:.1f}")
    return analysis


def aggregate_stage() -> list:
    all_results = []
    combo_results_dir = f"{OUT_BASE}/_combo_results"
    if os.path.isdir(combo_results_dir):
        for fname in sorted(os.listdir(combo_results_dir)):
            with open(f"{combo_results_dir}/{fname}", encoding="utf-8") as f:
                all_results.append(json.load(f))
    with open(f"{OUT_BASE}/all_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] aggregate_stage: {len(all_results)}本を集約しました。")
    return all_results


# ============================================================
# 段階5: 打ち切りバイアス対策(final_ng=True かつ fact_verdict=Noneの記事へ
# Fact Checker単独適用、Trial-14/15と同一Production呼び出し列)。
# ============================================================
CENSORED_DIR = f"{OUT_BASE}/factcheck_censored"


def identify_censored_targets(all_results: list) -> list:
    return [r for r in all_results if r.get("final_ng") is True and r.get("fact_verdict") is None]


def run_standalone_factcheck(condition_name: str, level_dir: str, run_idx: int) -> dict:
    article_path = f"{CONDITIONS[condition_name]['out_subdir']}/{level_dir}/run{run_idx}/article.md"
    with open(article_path, encoding="utf-8") as f:
        article_text = f.read()
    out_dir = f"{CENSORED_DIR}/{condition_name}_{level_dir}_run{run_idx}"
    os.makedirs(out_dir, exist_ok=True)

    fc_prompt = r3.build_fact_check_prompt(TOPIC_JA, article_text, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(
            fc_prompt, model=routing.require_model("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL))

    theme_tag = f"{THEME_ID}_censored_{condition_name}_{level_dir}_run{run_idx}"
    t0 = time.time()
    with cl.logging_context(theme_tag, "fact_check_censored"):
        fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
            r3.run_fact_checker_with_gates(make_fc_fn, sleep_fn=time.sleep)
    elapsed = round(time.time() - t0, 2)
    verdict = fc_result.get("verdict") if fc_result else None

    fact_qa_record = {
        "condition": condition_name, "level_dir": level_dir, "run": run_idx,
        "final_status": fc_status, "model": fc_model, "response_id": fc_response_id,
        "web_search_call_count": fc_search_usage["web_search_call_count"] if fc_search_usage else None,
        "attempts": len(fc_attempts), "verdict": verdict, "result": fc_result,
        "elapsed_seconds": elapsed,
    }
    with open(f"{out_dir}/fact_qa.json", "w", encoding="utf-8") as f:
        json.dump(fact_qa_record, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{out_dir}/fact_check_attempts.json", "w", encoding="utf-8") as f:
        json.dump(fc_attempts, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] censored {condition_name} {level_dir} run{run_idx}: status={fc_status} "
          f"verdict={verdict} elapsed={elapsed}s")
    return fact_qa_record


def censored_stage(condition_name: str, level_dir: str, run_idx: int) -> dict:
    os.makedirs(CENSORED_DIR, exist_ok=True)
    cl.install(LOG_PATH)
    check_budget_or_raise()
    return run_standalone_factcheck(condition_name, level_dir, run_idx)


def write_cost_summary() -> dict:
    records = []
    if os.path.exists(LOG_PATH):
        records = [json.loads(l) for l in open(LOG_PATH, encoding="utf-8")]
    for r in records:
        r["_cost_usd"] = _call_cost_usd(r)
    by_theme, counts = defaultdict(float), defaultdict(int)
    for r in records:
        by_theme[r["theme"]] += r["_cost_usd"]
        counts[r["theme"]] += 1
    result = {
        "usd_jpy_rate": USD_JPY,
        "methodology": "全て実測usage(actual)。単価はer005_output/cost_baseline_01/"
                       "pricing_snapshot.json(OFFICIAL_SOURCE、Trial-12/12b/14/15と同一参照元・"
                       "同一ロジック)。",
        "by_theme_jpy": {k: round(v * USD_JPY, 1) for k, v in by_theme.items()},
        "call_counts": dict(counts),
        "total_usd": round(sum(by_theme.values()), 4),
        "total_jpy": round(sum(by_theme.values()) * USD_JPY, 1),
        "total_calls": len(records),
    }
    with open(f"{OUT_BASE}/cost_summary_16.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result


if __name__ == "__main__":
    import sys

    which = sys.argv[1] if len(sys.argv) > 1 else "help"
    if which == "research":
        research_stage()
    elif which == "build_ledgers":
        build_ledgers_stage()
    elif which == "open146_check":
        open146_firing_check_stage()
    elif which == "combo":
        combo_stage(sys.argv[2], sys.argv[3], int(sys.argv[4]))
    elif which == "aggregate":
        results = aggregate_stage()
        for t in identify_censored_targets(results):
            print(t["condition"], t["level"], t["run"])
    elif which == "censored":
        censored_stage(sys.argv[2], sys.argv[3], int(sys.argv[4]))
    elif which == "cost":
        r = write_cost_summary()
        print(f"[{THEME_ID}] 費用実測合計: ¥{r['total_jpy']}")
    else:
        print("usage: python er011_news_point_quality_generalization_trial_16_run.py "
              "[research|build_ledgers|open146_check|combo <condition_h|condition_p> <A2|B1B> <run>|"
              "aggregate|censored <condition_h|condition_p> <a2|b1b> <run>|cost]")


def canonical_spelling_research_stage() -> dict:
    """OPEN-146観測(段階3)で発火が確認された場合のみ実行する。Production
    関数(canon_spelling.run_canonical_spelling_research、内部でr3.
    make_writer_research_fnを無改変で再利用)をentities=1件("バスク大学")
    に対して1回だけ呼び出す。"""
    os.makedirs(OUT_BASE, exist_ok=True)
    cl.install(LOG_PATH)
    client = t3.vfl01.get_client()
    entities = [{"ja": "バスク大学", "context": "Agustín Sánchez-Lavegaが所属する大学(Science Advances論文の筆頭著者)"}]
    theme_tag = f"{THEME_ID}_canonical_spelling_research"
    t0 = time.time()
    with cl.logging_context(theme_tag, "canonical_spelling_research"):
        record = canon_spelling.run_canonical_spelling_research(entities, client=client)
    elapsed = round(time.time() - t0, 2)
    record["elapsed_seconds"] = elapsed
    with open(f"{OUT_BASE}/canonical_spelling_research_raw.json", "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] canonical_spelling_research完了: parsed={record['parsed']} elapsed={elapsed}s")
    return record


def append_canonical_spelling_to_ledgers_stage() -> dict:
    """段階3.5(発火時のみ): 確認済みcanonical_en_spellingを両条件の
    Ledgerファイルへ追記する(canon_spelling.append_canonical_spelling_
    section、無改変)。base facts(FACT-01〜05)は両条件共通のため、同じ
    entryを両方へ追記する。"""
    with open(f"{OUT_BASE}/canonical_spelling_research_raw.json", encoding="utf-8") as f:
        record = json.load(f)
    entries = record["parsed"]
    updated = {}
    for path in (LEDGER_H_PATH, LEDGER_P_PATH):
        original = load_text(path)
        updated_text = canon_spelling.append_canonical_spelling_section(original, entries)
        with open(path, "w", encoding="utf-8") as f:
            f.write(updated_text)
        assert canon_spelling.has_canonical_en_spelling(updated_text)
        updated[path] = len(updated_text)
    print(f"[{THEME_ID}] append_canonical_spelling_to_ledgers_stage完了: {updated}")
    return updated
