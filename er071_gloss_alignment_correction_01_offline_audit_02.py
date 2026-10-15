# -*- coding: utf-8 -*-
"""KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01 委任_02: O1/O2 オフライン検証(API 0円、決定論)。

O1: 既存glossの非劣化。全er*_output/**/keywords_canonicalized.jsonの全recordを、**corrected modeのalign_glosses**へ
    「LLMは常にcurrentを正と答える(current_gloss_consistent=真・gloss不変)」fakeで通し、
      (1) 対象外item(KPが候補から伸びていない)は1件もLLM入力に載らない(呼出0)
      (2) 対象外itemのmergedが完全一致(差分0)
      (3) 対象0件のrecordではAPI呼出0・mergedは同一object
    を検証する。fakeはAPIを呼ばない。
O2: 追加内容語の機械算出(既知の対象ユニーク)。
Relabel: census「KPにスロット語が無いのにglossに『～』」29件の推定ラベルを再点検(OF-KGDC-07)。
usage: .venv/Scripts/python.exe er071_gloss_alignment_correction_01_offline_audit_02.py --mode corrected --census <census_01.json> --out <OFFLINE_AUDIT_02.json>
"""
import argparse
import glob
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
import er003_key_words_gloss_alignment as ga  # noqa: E402

# census 29件の再点検(Sonnet目視、ユーザー未確認)。key=(kp, gloss) -> (label, 理由)。未掲載の項目は機械推定(MACHINE_INFERRED_LEGIT)。
RELABEL = {
    ("put solo travel at", "ソロ旅行を～％とする"): (
        "RULE15_NUMERIC_SLOT_EXPECTED_NG", "承認規則15行『ソロ旅行を～％とする』型(数値の穴埋め必須)そのもの=選ばれてはいけない側。辞書的な『～』の正当例ではない"),
    ("urge to watch", "～したい衝動"): ("STALE_OMISSION", "KPのwatchに当たる語がglossに無い"),
    ("draw on", "〜のデータを利用する"): ("REVIEW_NEEDED", "KP『draw on』に無い『データ』をglossが補っている(過剰具体化の疑い)。辞書的な『〜』自体は問題なし"),
    ("stay on", "～に向けたままでいる"): ("REVIEW_NEEDED", "意味が不自然/不明確な疑い(文脈なしでは判定不能)"),
    ("account for", "〜を説明する要因となる"): ("REVIEW_NEEDED", "『要因となる』の付加が過剰かの判断が必要(軽微)"),
    ("moderate-to-vigorous activity", "中～高強度の運動"): ("LEGIT_RANGE_NOTATION", "範囲表記の『～』(スロットではない)。TTS変換は別問題"),
}


def load_records():
    out = []
    for p in sorted(glob.glob("er*_output/**/keywords_canonicalized.json", recursive=True)):
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        if isinstance(d, dict) and isinstance(d.get("items"), list):
            out.append((p.replace("\\", "/"), d))
    return out


_TARGET_BLOCK_RE = re.compile(r"【対象項目】\n(.*?)\n\n【記事本文", re.S)


def o1(records):
    stats = {"records": 0, "items": 0, "target_items": 0, "non_target_items": 0, "records_with_targets": 0,
             "llm_calls": 0, "calls_in_zero_target_records": 0, "non_target_items_sent_to_llm": 0,
             "non_target_diffs": 0, "target_gloss_or_kp_changes_when_llm_says_consistent": 0,
             "zero_target_records_not_same_object": 0, "api_calls": 0}
    diffs = []
    ga.preflight(True)
    for path, doc in records:
        stats["records"] += 1
        items = doc["items"]
        stats["items"] += len(items)
        targets = ga.select_alignment_targets(items)
        tr = {t["rank"] for t in targets}
        stats["target_items"] += len(targets)
        stats["non_target_items"] += len(items) - len(targets)
        calls = []

        def make(msg, _targets=targets, _calls=calls):
            def fn():
                _calls.append(msg)
                blk = _TARGET_BLOCK_RE.search(msg)
                sent = {x["rank"] for x in json.loads(blk.group(1))}
                stats["non_target_items_sent_to_llm"] += len(sent - {t["rank"] for t in _targets})
                payload = {"items": [{"rank": t["rank"], "current_gloss_consistent": True,
                                      "japanese_gloss": t.get("japanese_gloss") or "", "added_word_mappings": [],
                                      "qa_reflects_all_key_phrase_words": "PASS", "reasoning": "fake"} for t in _targets]}
                return json.dumps(payload, ensure_ascii=False), "fake-model", "fake"
            return fn
        merged = {"items": items, "overall_status": doc.get("overall_status")}
        r = ga.align_glosses(merged, "", make, mode="corrected", enabled=True)
        stats["llm_calls"] += len(calls)
        if not targets:
            stats["calls_in_zero_target_records"] += len(calls)
            if r["merged"] is not merged:
                stats["zero_target_records_not_same_object"] += 1
            continue
        stats["records_with_targets"] += 1
        for old, new in zip(items, r["merged"]["items"]):
            if old["rank"] in tr:
                if (new.get("key_phrase"), new.get("japanese_gloss")) != (old.get("key_phrase"), old.get("japanese_gloss")):
                    stats["target_gloss_or_kp_changes_when_llm_says_consistent"] += 1
                continue
            if json.dumps(old, sort_keys=True, ensure_ascii=False) != json.dumps(new, sort_keys=True, ensure_ascii=False):
                stats["non_target_diffs"] += 1
                diffs.append({"file": path, "rank": old["rank"]})
    return stats, diffs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=["corrected"])
    ap.add_argument("--census", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    census = json.load(open(a.census, encoding="utf-8"))["all_er_output"]
    records = load_records()
    stats, diffs = o1(records)
    # O2
    uniq = []
    for t in census["unique_target_triples"]:
        uniq.append({"display": t["display"], "kp": t["kp"], "gloss": t["gloss"],
                     "added_content_words": ga.added_content_words(t["display"], t["kp"]),
                     "adds_words_legacy_flag": ga.kp_adds_words_beyond_display(t["display"], t["kp"])})
    extra = [("based on", "based on interviews"), ("raw beans", "raw-bean prices"), ("bring in", "bring in a human helper"),
             ("close around", "close around me"), ("locked into", "locked into a narrow view"), ("take", "take someone's place")]
    for d, k in extra:
        uniq.append({"display": d, "kp": k, "added_content_words": ga.added_content_words(d, k),
                     "adds_words_legacy_flag": ga.kp_adds_words_beyond_display(d, k)})
    # Relabel
    rows = []
    for x in census["tilde_gloss_without_kp_slot_items"]:
        lab = RELABEL.get((x["kp"], x["gloss"]))
        rows.append({"file": x["file"], "rank": x["rank"], "kp": x["kp"], "gloss": x["gloss"],
                     "label": lab[0] if lab else "MACHINE_INFERRED_LEGIT", "reason": lab[1] if lab else "KP==display、末尾が前置詞/不変化詞で辞書的な『～』と推定(機械推定、目視は上記以外未実施)"})
    cnt = {}
    for r in rows:
        cnt[r["label"]] = cnt.get(r["label"], 0) + 1
    ok = (stats["non_target_diffs"] == 0 and stats["non_target_items_sent_to_llm"] == 0
          and stats["calls_in_zero_target_records"] == 0 and stats["zero_target_records_not_same_object"] == 0
          and stats["target_gloss_or_kp_changes_when_llm_says_consistent"] == 0)
    doc = {"managed_id": "KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01", "delegation": "02", "mode": a.mode, "cost_jpy": 0,
           "O1": {**stats, "pass": ok, "diffs": diffs,
                  "census_expected": {"records": census["records"], "items": census["items"], "targets": census["targets"]}},
           "O2_added_content_words": uniq,
           "relabel_census_tilde_items": {"total": len(rows), "counts": cnt, "rows": rows,
                                          "note": "Sonnet目視/機械推定、ユーザー未確認。旧『28/29正当』は『正当推定24+範囲表記1=25、要確認3、規則15行違反1、欠落1』へ訂正"}}
    json.dump(doc, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({"O1": {k: v for k, v in doc["O1"].items() if k != "diffs"}, "relabel_counts": cnt}, ensure_ascii=False, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
