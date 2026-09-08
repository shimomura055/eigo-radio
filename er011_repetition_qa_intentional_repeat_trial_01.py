# ============================================================
# er011_repetition_qa_intentional_repeat_trial_01.py
# 管理ID: TTS-REPETITION-QA-INTENTIONAL-REPEAT-FALSE-POSITIVE-TRIAL-01
# ============================================================
# Trial(Production変更なし)。Production module
# `er011_open121_repetition_qa_production_01.py` はread-onlyでimportする
# だけで、一切編集・monkeypatchしない。本ファイルは独立した候補ロジックの
# 実装・評価専用。
#
# 背景: B-Family Phase 1 Voice B `point_two` の意図的並行構文
#   "...the people I need—or do not need—around me."
# が、Production `_canonical_repeat_count()` の
#   canonical_tokens = [normalize(w) for w in text.split()]
# という素朴な空白split実装により、em dash(—)が単語に空白なしで隣接
# している箇所("need—or"/"need—around")が1つのtokenとして扱われ、
# canonical側の"do not need"出現が2回ではなく1回としてしか数えられない
# ことが根本原因(実データで確認、詳細はREPORTのfindings章参照)。
#
# 本ファイルはこの根本原因を再現し、複数の候補修正ロジックを実装した上で、
# 既存corpusデータ(新規ASR/TTS呼び出しなし、費用¥0)でTP/FP/FNを比較する。
# ============================================================

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

# Production moduleをread-onlyでimportする(関数呼び出しのみ、編集なし)。
import er011_open121_repetition_qa_production_01 as prod  # noqa: E402
import er008_disfluency_qa_18 as dq18  # noqa: E402  (prod内部が依存するのと同一module)

OUT_DIR = REPO_ROOT / "er011_output" / "repetition_qa_intentional_repeat_trial_01"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 1. 候補ロジック(canonical側tokenization / repeat count)
# ============================================================
# BASELINE: Production `_canonical_repeat_count()` / `_normalize_tokens()`
# を完全にそのまま呼ぶ(比較の基準点)。


def baseline_canonical_tokens(canonical_text: str) -> list:
    return prod._normalize_tokens(canonical_text)


def baseline_repeat_count(span_tokens: list, canonical_text: str) -> int:
    canonical_tokens = baseline_canonical_tokens(canonical_text)
    return prod._canonical_repeat_count(span_tokens, canonical_tokens)


# --- 候補1a(推奨): em dash(—, U+2014)のみを、分割前に空白へ置換する
# 最小修正。ハイフン(-、複合語区切り、例: hobby-based)は対象外のため
# 複合語の意図しない分割は発生しない。en dash(–, U+2013)も対象外とする
# (下記候補1bとの比較・理由はコーパス調査結果を参照。en dashはこの
# コーパスで"1–1"のような番号・スコア表記[空白なし複合token]にも
# 使われており、空白置換すると番号系tokenを不必要に分割するリスクが
# あるため、実際に問題を再現したem dashのみへ意図的にスコープを絞る)。
_EM_DASH_ONLY_RE = re.compile(r"—")  # em dash(—、U+2014)のみ


def candidate1_canonical_tokens(canonical_text: str) -> list:
    text = _EM_DASH_ONLY_RE.sub(" ", canonical_text)
    return [dq18._normalize_token(w) for w in text.split() if dq18._normalize_token(w)]


def candidate1_repeat_count(span_tokens: list, canonical_text: str) -> int:
    canonical_tokens = candidate1_canonical_tokens(canonical_text)
    return prod._canonical_repeat_count(span_tokens, canonical_tokens)


# --- 候補1b(比較用、非推奨): em dash + en dashの両方を空白へ置換する
# 広めの候補。本コーパスのcontrol群では候補1aと全く同じ結果になるが、
# en dashは他所で"1–1"のようなスコア表記(空白なし)にも使われており、
# 数字を含むspanの誤intentional化リスク(候補2で確認した"108.95"→
# "108"+"95"の副作用と同種のリスク)を理論上は否定できない。この
# コーパスにはen dash絡みの実例陽性/陰性が無いため未検証のまま
# 参考として残す。
_CLAUSE_DASH_RE = re.compile(r"[—–]")  # em dash(—) / en dash(–)


def candidate1b_canonical_tokens(canonical_text: str) -> list:
    text = _CLAUSE_DASH_RE.sub(" ", canonical_text)
    return [dq18._normalize_token(w) for w in text.split() if dq18._normalize_token(w)]


def candidate1b_repeat_count(span_tokens: list, canonical_text: str) -> int:
    canonical_tokens = candidate1b_canonical_tokens(canonical_text)
    return prod._canonical_repeat_count(span_tokens, canonical_tokens)


# --- 候補2: 全ての非英数字(アポストロフィ以外)を区切り文字として扱う
# 汎用regex tokenizer。em dash以外の任意の記号(コロン・セミコロン・
# 括弧・スラッシュ・通常のハイフンも含む)を境界とみなす、より汎用的だが
# より積極的な候補。複合語(hobby-based等)も分割される。


_WORD_RE = re.compile(r"[a-z0-9']+")


def candidate2_canonical_tokens(canonical_text: str) -> list:
    return _WORD_RE.findall(canonical_text.lower())


def candidate2_span_tokens_from_text(span_text: str) -> list:
    return _WORD_RE.findall(span_text.lower())


def candidate2_repeat_count(span_tokens_raw_norm: list, canonical_text: str, span_text: str) -> int:
    # span側もcandidate2と同じtokenizerで作り直す(ASR側token文字列に
    # 記号が残っている場合の一貫性のため)。span_textが無い場合は既存の
    # normalizeされたspan_tokensをそのまま使う。
    if span_text:
        span_tokens = candidate2_span_tokens_from_text(span_text)
    else:
        span_tokens = span_tokens_raw_norm
    canonical_tokens = candidate2_canonical_tokens(canonical_text)
    n, m = len(canonical_tokens), len(span_tokens)
    if not span_tokens or not canonical_tokens or m == 0:
        return 0
    count = 0
    for i in range(n - m + 1):
        if canonical_tokens[i:i + m] == span_tokens:
            count += 1
    return count


# --- 候補3: em/en dashのみ除去(空白置換ではなく単純delete)。
# 比較用の"やってはいけない実装"の例として残す(縮約されて誤って
# 別の単語にmergeしてしまうリスクを実データで示すため)。
def candidate3_canonical_tokens_naive_delete(canonical_text: str) -> list:
    text = _CLAUSE_DASH_RE.sub("", canonical_text)
    return [dq18._normalize_token(w) for w in text.split() if dq18._normalize_token(w)]


def candidate3_repeat_count(span_tokens: list, canonical_text: str) -> int:
    canonical_tokens = candidate3_canonical_tokens_naive_delete(canonical_text)
    return prod._canonical_repeat_count(span_tokens, canonical_tokens)


CANDIDATES = ["baseline", "candidate1a_emdash_only_split", "candidate1b_em_en_dash_split",
              "candidate2_regex_word", "candidate3_naive_delete"]


def compute_all(span_tokens: list, canonical_text: str, span_text: str) -> dict:
    return {
        "baseline": baseline_repeat_count(span_tokens, canonical_text),
        "candidate1a_emdash_only_split": candidate1_repeat_count(span_tokens, canonical_text),
        "candidate1b_em_en_dash_split": candidate1b_repeat_count(span_tokens, canonical_text),
        "candidate2_regex_word": candidate2_repeat_count(span_tokens, canonical_text, span_text),
        "candidate3_naive_delete": candidate3_repeat_count(span_tokens, canonical_text),
    }


def span_tokens_from_span_text(span_text: str) -> list:
    """既存JSON上のspan_text(word.word由来、先頭空白付きのことがある)を
    Production方式Aと同じ正規化で再トークン化する(dq18._normalize_token、
    空白split)。"""
    return [dq18._normalize_token(w) for w in span_text.split()]


# ============================================================
# 2. コーパス読み込み(既存JSON/既存ASR結果のみ、新規API呼び出しなし)
# ============================================================
def _load_json(rel_path: str):
    p = REPO_ROOT / rel_path
    return json.loads(p.read_text(encoding="utf-8"))


def _get(d, path):
    cur = d
    for part in path.split("."):
        if cur is None:
            return None
        cur = cur.get(part) if isinstance(cur, dict) else None
    return cur


def build_corpus() -> list:
    """positive control(真の重複、flagged=Trueを維持しなければならない)、
    negative control(意図的反復、Voice B em dash、flagged=Falseに
    ならなければならない)、regression control(em dashと無関係な既存
    flagged item、候補適用後もbaselineと同じ挙動を維持しなければ
    ならない)の3群を、既存JSON(method_d_flag23_review_01・
    open121_existing_audio_dprime_sweep_01・er012 phase1_02・
    er012 trial08)から構築する。"""
    items = []

    # --- positive controls: method_d_flag23_review_01 index 0-7
    # (「真の重複(証拠あり)」、既知バグPoint Two/In One Lineと同一script・
    # 同一flag位置と確定済み)。
    review = _load_json("er011_output/method_d_flag23_review_01/classification_table.json")
    for it in review[:8]:
        span = it["a_flagged_spans"][0]
        items.append({
            "control_type": "positive_true_duplicate",
            "item_id": it["item_id"],
            "canonical_text": it["canonical_text"],
            "span_text": span["span_text"],
            "prod_canonical_repeat_count": span["canonical_repeat_count"],
            "prod_flagged": span["flagged"],
            "source": "method_d_flag23_review_01/classification_table.json",
        })

    # --- positive controls追加: known_case (BUGGY_UNFIXED backup /
    # BEFORE_FIX buggy backup)。同一classification_table.json内、
    # item_idで抽出(canonical_textはsweep内の別item_idと同一script)。
    sweep_classified = _load_json(
        "er011_output/open121_existing_audio_dprime_sweep_01/results/classified_table.json")
    known_case_ids = [
        "known_case::point_two_BUGGY_UNFIXED_backup",
        "known_case::in_one_line_BEFORE_FIX_buggy_backup",
    ]
    # canonical_textがclassified_table.json自体には無いため、method_d_flag23の
    # 同一script(point_two/in_one_line)のcanonical_textを流用する。
    canonical_by_segment = {
        "point_two": next(x["canonical_text"] for x in review if x["segment_id"] == "point_two"),
        "in_one_line": next(x["canonical_text"] for x in review if x["segment_id"] == "in_one_line"),
    }
    for it in sweep_classified:
        if it["item_id"] in known_case_ids:
            span = it["a_flagged_spans"][0]
            seg_key = "point_two" if "point_two" in it["item_id"] else "in_one_line"
            items.append({
                "control_type": "positive_true_duplicate",
                "item_id": it["item_id"],
                "canonical_text": canonical_by_segment[seg_key],
                "span_text": span["span_text"],
                "prod_canonical_repeat_count": span["canonical_repeat_count"],
                "prod_flagged": span["flagged"],
                "source": "open121_existing_audio_dprime_sweep_01/results/classified_table.json",
            })

    # --- negative controls: Voice B phase1_02 point_two attempt1-3
    # (em dash並行構文、ユーザー試聴でPASS確定済み)。
    attempts_dir = REPO_ROOT / "er012_output/editorial_b_family_production_phase1_02/b1b/narration/attempts"
    for fn in sorted(attempts_dir.glob("point_two_attempt*_englishstyleprefixwidemargin.json")):
        d = json.loads(fn.read_text(encoding="utf-8"))
        matches = _get(d, "repetition_qa_evidence.method_a_ngram.matches") or []
        parts = json.loads(
            (REPO_ROOT / "er012_output/editorial_b_family_production_phase1_02/b1b/parts.json")
            .read_text(encoding="utf-8"))
        canonical_text = parts["point_two_body"]
        for m in matches:
            items.append({
                "control_type": "negative_intentional_repeat",
                "item_id": f"phase1_02::{fn.stem}",
                "canonical_text": canonical_text,
                "span_text": m["span_text"],
                "prod_canonical_repeat_count": m["canonical_repeat_count"],
                "prod_flagged": m["flagged"],
                "source": str(fn.relative_to(REPO_ROOT)),
            })

    # --- negative control追加: trial_08(phase1_02より前の同一script・
    # 同一bug再現、classified_table.json内に既存記録あり)。
    for it in sweep_classified:
        if it["item_id"] == "er012_laneb_trial08::er012_output/editorial_b_voices_trial_08_audio/p1::b1b::point_two":
            span = it["a_flagged_spans"][0]
            tts_gen = _load_json(
                "er012_output/editorial_b_voices_trial_08_audio/p1/b1b/audit/tts_generation_results.json")
            canonical_text = tts_gen["segments"]["point_two"]["text"]
            items.append({
                "control_type": "negative_intentional_repeat",
                "item_id": it["item_id"],
                "canonical_text": canonical_text,
                "span_text": span["span_text"],
                "prod_canonical_repeat_count": span["canonical_repeat_count"],
                "prod_flagged": span["flagged"],
                "source": "er012_output/editorial_b_voices_trial_08_audio/p1/b1b/audit/tts_generation_results.json"
                          " + open121_existing_audio_dprime_sweep_01/results/classified_table.json",
            })

    # --- regression controls: em dashと無関係な既存flagged item(方式A
    # 誤検知の別原因[%記号 vs "percent"表記/小数点付き数字]。em dash非関与
    # であることをcanonical_textに"—"/"–"が含まれないことで機械的に確認し、
    # 候補適用後もbaselineと完全一致することを検証する回帰対照群)。
    regression_targets = [
        ("pool_pilot_01/pool_n18_notifications::er006_output/pool_pilot_01/pool_n18_notifications::b1b::point_one",
         "er006_output/pool_pilot_01/pool_n18_notifications/b1b/audit/tts_generation_results.json", "point_one"),
        ("pool_pilot_01/pool_n4_supermarket::er006_output/pool_pilot_01/pool_n4_supermarket::a2::full_story_part2",
         "er006_output/pool_pilot_01/pool_n4_supermarket/a2/audit/tts_generation_results.json", "full_story_part2"),
        ("pool_pilot_01/pool_n4_supermarket::er006_output/pool_pilot_01/pool_n4_supermarket::a2::"
         "full_story_part2_original",
         "er006_output/pool_pilot_01/pool_n4_supermarket/a2/audit/tts_generation_results.json", "full_story_part2"),
        ("pool_pilot_01/pool_n4_supermarket::er006_output/pool_pilot_01/pool_n4_supermarket::b1b::full_story_part2",
         "er006_output/pool_pilot_01/pool_n4_supermarket/b1b/audit/tts_generation_results.json", "full_story_part2"),
        ("pool_pilot_01/pool_n9_tip_screens::er006_output/pool_pilot_01/pool_n9_tip_screens::a2::point_one",
         "er006_output/pool_pilot_01/pool_n9_tip_screens/a2/audit/tts_generation_results.json", "point_one"),
        ("pool_pilot_01/pool_n9_tip_screens::er006_output/pool_pilot_01/pool_n9_tip_screens::a2::point_two",
         "er006_output/pool_pilot_01/pool_n9_tip_screens/a2/audit/tts_generation_results.json", "point_two"),
        ("pool_pilot_01/pool_n9_tip_screens::er006_output/pool_pilot_01/pool_n9_tip_screens::a2::"
         "point_two_original",
         "er006_output/pool_pilot_01/pool_n9_tip_screens/a2/audit/tts_generation_results.json", "point_two"),
        ("er003_output/n3_01::er003_output/n3_01/household::a2::full_story_part2",
         "er003_output/n3_01/household/a2/audit/tts_generation_results.json", "full_story_part2"),
    ]
    for item_id, gen_path, seg in regression_targets:
        match = next((x for x in sweep_classified if x["item_id"] == item_id), None)
        if match is None:
            continue
        tts_gen = _load_json(gen_path)
        # 注意: `er011_open121_existing_audio_dprime_sweep_01.py`のbuild_inventory()は
        # segments[cid].get("text")(実際にTTSへ送られた文字列)をcanonical_textとして
        # 使っている(`canonical_source`ラベルの文言に反しtts_generation_results.json
        # 側の"canonical_text"フィールドは別の正規化済みフィールドで実際には未使用)。
        # 再現性を保つため本Trialでも同じ"text"フィールドを使う。
        canonical_text = tts_gen["segments"][seg]["text"]
        for span in match["a_flagged_spans"] or []:
            items.append({
                "control_type": "regression_unrelated_flag",
                "item_id": item_id,
                "canonical_text": canonical_text,
                "span_text": span["span_text"],
                "prod_canonical_repeat_count": span["canonical_repeat_count"],
                "prod_flagged": span["flagged"],
                "source": gen_path + " + open121_existing_audio_dprime_sweep_01/results/classified_table.json",
            })

    return items


# ============================================================
# 3. 評価実行
# ============================================================
def main():
    corpus = build_corpus()
    results = []
    for item in corpus:
        span_tokens = span_tokens_from_span_text(item["span_text"])
        counts = compute_all(span_tokens, item["canonical_text"], item["span_text"])
        # 再現確認: baseline候補がProduction実データ記録値と一致するか
        # (整合性チェック、Trial側の再実装がProductionと食い違っていないか)
        reproduced_match = (counts["baseline"] == item["prod_canonical_repeat_count"])
        row = dict(item)
        row["recomputed_counts"] = counts
        row["recomputed_intentional"] = {c: (counts[c] >= 2) for c in CANDIDATES}
        row["recomputed_flagged_if_only_this_span"] = {c: (counts[c] < 2) for c in CANDIDATES}
        row["baseline_matches_production_recorded_value"] = reproduced_match
        # 期待値判定
        if item["control_type"] == "positive_true_duplicate":
            row["expected"] = "flagged=True(count<2)を維持すべき"
            row["candidate_correct"] = {c: (counts[c] < 2) for c in CANDIDATES}
        elif item["control_type"] == "negative_intentional_repeat":
            row["expected"] = "flagged=False(count>=2)へ是正すべき"
            row["candidate_correct"] = {c: (counts[c] >= 2) for c in CANDIDATES}
        else:  # regression_unrelated_flag
            row["expected"] = "baselineと完全一致を維持すべき(em dash非関与)"
            row["candidate_correct"] = {c: (counts[c] == counts["baseline"]) for c in CANDIDATES}
        results.append(row)

    # --- 集計 ---
    summary = {c: {"TP": 0, "FP": 0, "FN": 0, "TN": 0, "regression_ok": 0, "regression_break": 0}
               for c in CANDIDATES}
    for row in results:
        ct = row["control_type"]
        for c in CANDIDATES:
            ok = row["candidate_correct"][c]
            if ct == "positive_true_duplicate":
                if ok:
                    summary[c]["TP"] += 1  # 正しくflagged維持(真陽性)
                else:
                    summary[c]["FN"] += 1  # 誤って"intentional"扱い(見逃し)
            elif ct == "negative_intentional_repeat":
                if ok:
                    summary[c]["TN"] += 1  # 正しくintentional判定(真陰性=誤検知の是正)
                else:
                    summary[c]["FP"] += 1  # 依然誤検知のまま
            else:
                if ok:
                    summary[c]["regression_ok"] += 1
                else:
                    summary[c]["regression_break"] += 1

    out = {
        "management_id": "TTS-REPETITION-QA-INTENTIONAL-REPEAT-FALSE-POSITIVE-TRIAL-01",
        "candidates": CANDIDATES,
        "corpus_size": len(corpus),
        "corpus_breakdown": {
            "positive_true_duplicate": sum(1 for r in results if r["control_type"] == "positive_true_duplicate"),
            "negative_intentional_repeat": sum(1 for r in results if r["control_type"] == "negative_intentional_repeat"),
            "regression_unrelated_flag": sum(1 for r in results if r["control_type"] == "regression_unrelated_flag"),
        },
        "summary": summary,
        "all_baseline_reproduced": all(r["baseline_matches_production_recorded_value"] for r in results),
        "details": results,
    }

    out_path = OUT_DIR / "evaluation_results.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"corpus_size={out['corpus_size']}  breakdown={out['corpus_breakdown']}")
    print(f"all_baseline_reproduced={out['all_baseline_reproduced']}")
    for c in CANDIDATES:
        s = summary[c]
        print(f"[{c}] TP={s['TP']} FN={s['FN']} | TN={s['TN']} FP={s['FP']} | "
              f"regression_ok={s['regression_ok']} regression_break={s['regression_break']}")
    print(f"saved: {out_path}")


if __name__ == "__main__":
    main()
