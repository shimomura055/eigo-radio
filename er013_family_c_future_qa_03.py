# ============================================================
# er013_family_c_future_qa_03.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-FINAL-TUNING-TRIAL-03
# ============================================================
# 目的: er013_family_c_future_qa_02.py(無編集のまま保持)を全面的に再輸出
# (re-export)しつつ、決定的スキャンへ2項目を追加する:
#   (1) 枠内hedge密度: [[IMAGINED]]枠内の文数に対する
#       may/might/could/perhaps/possibly/would等の出現率。
#   (2) 語数: 読者向け本文(reader_text)全体の語数が、レベル別の目安
#       範囲(er013_family_c_future_writer_03.WORD_COUNT_TARGET_RANGE)
#       に収まっているか。
# 上記いずれかが閾値超過の場合、完成記事の編集Gateを FAIL とし、Writer
# 再生成(最大1回)へつなげる(既存のscan_editorial_gate[v2]が担う
# 5項目[統計値・研究語・製品名・FACT件数上限・冒頭段落]はfcq2から
# 無改変のまま呼び出すのみで、閾値・判定ロジック自体は変更しない)。
#
# 実データからの発見(本タスクで実施した検証、詳細はwriter_03.py docstring
# 参照): Trial-02のA2 [[IMAGINED]]枠内自体は実測hedge語0件/59文であり、
# hedging過多は主に枠外(場面直後の反応・帰結パラグラフ)に集中していた。
# 枠内hedge密度スキャンは、v3 Writerが「場面直結の反応・選択まで枠内に
# 含める」設計変更を行った前提で有効に機能する仕組みであり、本ファイル
# 単体のスキャンロジック自体は合成fixtureで正しさを検証した
# (er013_family_c_future_qa_test_03.py参照)。Trial-02実データに対する
# 編集Gate FAIL回帰は、主に語数超過(A2実測1161語 > 目安上限600語)側で
# 確認する。
#
# 既存Fact Checker A'/Ledger Deviation Checker関数・fcq2の5判定基準は
# 一切改変しない。
# Status: Trial専用、未承認draft実装(`APPROVED_FOR_PRODUCTION`ではない)。
# ============================================================
from __future__ import annotations

import re

import er013_family_c_future_qa_01 as fcq_v1  # 再輸出用(fcq2と同じ再利用方針)
import er013_family_c_future_qa_02 as fcq2

# ------------------------------------------------------------
# fcq2(v2)の全公開関数・定数を無変更のまま再輸出する(既存呼び出し元が
# fcq3 経由でv2相当の機能をすべて使えるようにするため。個別値・
# 判定ロジック自体はfcq2側の実装のまま)。
# ------------------------------------------------------------
IMAGINED_OPEN_PREFIX = fcq2.IMAGINED_OPEN_PREFIX
IMAGINED_CLOSE = fcq2.IMAGINED_CLOSE
DEFAULT_LAYER1_PLACEHOLDER = fcq2.DEFAULT_LAYER1_PLACEHOLDER
META_OPEN = fcq2.META_OPEN
META_CLOSE = fcq2.META_CLOSE
FACT_OPEN_PREFIX = fcq2.FACT_OPEN_PREFIX
FACT_CLOSE = fcq2.FACT_CLOSE
MAX_FACT_EXCEPTIONS = fcq2.MAX_FACT_EXCEPTIONS
DEFAULT_CURRENT_YEAR = fcq2.DEFAULT_CURRENT_YEAR

extract_meta_blocks = fcq2.extract_meta_blocks
strip_meta_blocks = fcq2.strip_meta_blocks
extract_fact_blocks = fcq2.extract_fact_blocks
validate_fact_markers_balanced = fcq2.validate_fact_markers_balanced
strip_fact_markers_keep_body = fcq2.strip_fact_markers_keep_body
check_fact_markers_inside_imagined = fcq2.check_fact_markers_inside_imagined
route_article_for_qa_v2 = fcq2.route_article_for_qa_v2
scan_numeric_hits = fcq2.scan_numeric_hits
scan_research_term_hits = fcq2.scan_research_term_hits
scan_product_name_hits = fcq2.scan_product_name_hits
get_opening_paragraph = fcq2.get_opening_paragraph
scan_editorial_gate = fcq2.scan_editorial_gate  # v2の5項目判定(無変更のまま再輸出)
run_future_framing_qa_v2 = fcq2.run_future_framing_qa_v2
build_future_framing_qa_v2_prompt = fcq2.build_future_framing_qa_v2_prompt


# ============================================================
# 新設(1): 枠内hedge密度スキャン(決定的、¥0)
# ============================================================
# 対象語はユーザー指示書で明示された6語(may/might/could/perhaps/
# possibly/would)。"would"は条件法以外の用法(習慣過去等)でも出現し
# うるため誤検知の余地はあるが、指示書の明示的な指定語をそのまま採用する
# (指示範囲外の語追加・除外は行わない)。
HEDGE_WORDS_RE = re.compile(r"\b(may|might|could|perhaps|possibly|would)\b", re.IGNORECASE)

# 閾値: 枠内の文の15%を超えてhedge語を含む文があればFAIL。Trial-02実測
# (A2枠内密度0.0/59文、B1枠内密度0.19/58文)を踏まえ、「ほぼゼロに近い
# 密度」を許容しつつ、B1 Trial-02相当の高密度(約19%)は引き続き検出できる
# 水準として設定した(Trial限定の目安値、Production閾値として正式化する
# ものではない)。
HEDGE_DENSITY_MAX_IN_MARKERS = 0.15


def _split_sentences_simple(text: str) -> list:
    """簡易文分割(ピリオド/感嘆符/疑問符の後の空白で分割)。想像枠内の
    平文英語向けの簡便な決定的分割であり、Production共有の文分割関数
    (rewrite09.split_sentences等)を流用せず本ファイル内で完結させる
    (Trial専用スキャンのため、既存Production関数へ新しい依存を追加
    しない)。"""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", (text or "").strip())]
    return [s for s in sentences if s]


def compute_imagined_hedge_density(imagined_blocks: list) -> dict:
    """[[IMAGINED]]枠内の文を対象に、hedge語を含む文の比率を計算する。
    枠が1つも無い場合はdensity=0.0(判定不能ではなくhedging過多なし
    として扱う、既存の「想像枠を使わない」記事構成自体は編集Gateの
    別項目[冒頭場面性等]で評価されるため、本関数はhedging過多の有無
    のみに責務を限定する)。"""
    per_block = []
    total_sentences, total_hedge_sentences = 0, 0
    for b in imagined_blocks or []:
        sentences = _split_sentences_simple(b.get("body", ""))
        hedge_sentences = [s for s in sentences if HEDGE_WORDS_RE.search(s)]
        per_block.append({
            "timeframe": b.get("timeframe"),
            "sentence_count": len(sentences),
            "hedge_sentence_count": len(hedge_sentences),
            "hedge_sentences_sample": hedge_sentences[:5],
        })
        total_sentences += len(sentences)
        total_hedge_sentences += len(hedge_sentences)
    density = (total_hedge_sentences / total_sentences) if total_sentences else 0.0
    return {
        "per_block": per_block,
        "total_sentence_count": total_sentences,
        "total_hedge_sentence_count": total_hedge_sentences,
        "hedge_density": density,
        "within_limit": density <= HEDGE_DENSITY_MAX_IN_MARKERS,
    }


# ============================================================
# 新設(2): 語数スキャン(決定的、¥0)
# ============================================================
def scan_word_count(reader_text: str, min_words: int, max_words: int) -> dict:
    word_count = len((reader_text or "").split())
    return {
        "word_count": word_count,
        "min_words": min_words, "max_words": max_words,
        "within_range": min_words <= word_count <= max_words,
    }


# ============================================================
# 完成記事の編集Gate v3(v2の5項目 + hedge密度 + 語数)
# ============================================================
def scan_editorial_gate_v3(reader_text: str, fact_blocks: list, banned_product_names: list,
                            imagined_blocks: list, level: str, word_count_range: tuple,
                            current_year: int = DEFAULT_CURRENT_YEAR,
                            hedge_density_max: float = HEDGE_DENSITY_MAX_IN_MARKERS) -> dict:
    """v2の`scan_editorial_gate()`(5項目、無変更)に、枠内hedge密度と
    語数の2項目を追加した編集Gate。fail_reasonsはv2の理由リストへ追記
    する形で統合する(既存項目の判定・文言は変更しない)。"""
    base = fcq2.scan_editorial_gate(reader_text, fact_blocks, banned_product_names,
                                     current_year=current_year)
    hedge_result = compute_imagined_hedge_density(imagined_blocks)
    min_words, max_words = word_count_range
    word_result = scan_word_count(reader_text, min_words, max_words)

    fail_reasons = list(base["fail_reasons"])
    if not hedge_result["within_limit"]:
        fail_reasons.append(
            f"imagined_hedge_density={hedge_result['hedge_density']:.3f} "
            f"(limit={hedge_density_max})"
        )
    if not word_result["within_range"]:
        fail_reasons.append(
            f"word_count={word_result['word_count']} "
            f"(target_range={min_words}-{max_words})"
        )

    result = dict(base)
    result["imagined_hedge_density_result"] = hedge_result
    result["word_count_result"] = word_result
    result["level"] = level
    result["fail_reasons"] = fail_reasons
    result["overall_status"] = "FAIL" if fail_reasons else "PASS"
    return result
