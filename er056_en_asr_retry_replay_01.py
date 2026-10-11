"""FAMILY-X-EN-ASR-CONFIRM-RETRY-REDESIGN-01 委任_01: 過去の英語TTS attempt記録を用いた無料再計算(read-only)。

- 課金API呼び出しを一切含まない(OpenAI/Azure/Gemini/LLMは呼ばない)。ローカルfaster-whisper(無料、
  CPU)のみ使用する `local` サブコマンドを除き、既存JSONの読み込みと既存Validatorの純関数呼び出しだけ。
- Production code/Prompt/Validator/Routingは変更しない(importして純関数を呼ぶのみ)。
- 入力: リポジトリ内の `*/narration/attempts/*.json`(attempt単位の実音声メタ、saved_at/route/ASR転写/
  classification/cascade_steps)、同階層の `audit/tts_generation_results.json`(canonical text)、
  Coffee snapshot(evidence_snapshot/a2_attempts)。
- 出力: er056_output/en_asr_confirm_retry_redesign_01/replay_results_01.json ほか。

使い方:
  python er056_en_asr_retry_replay_01.py collect      # 集計(高速、API/モデル不要)
  python er056_en_asr_retry_replay_01.py local        # NG attempt等の保存wavをローカルwhisperで再確認(無料、低速)
"""
from __future__ import annotations

import collections
import io
import json
import os
import random
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
OUT = os.path.join(ROOT, "er056_output", "en_asr_confirm_retry_redesign_01")
SNAP = os.path.join(OUT, "evidence_snapshot")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import er006_preprod_hardening_01_validation as val  # noqa: E402
import er020_tts_retry_local_rewrite_01 as er020  # noqa: E402


def role_of(segment_id: str | None) -> str:
    """5 narrative role(Full Story/Comment/Preview/Topic intro/In One Line)以外は 'OTHER'
    (共有殻num_*/welcome等、Key Phrase、見出し)。b1b_/a2_en_ 接頭辞付きの旧名も吸収する。"""
    sid = segment_id or ""
    for pre in ("a2_en_", "b1b_", "a2_", "b1_"):
        if sid.startswith(pre):
            sid = sid[len(pre):]
    r = er020.resolve_narrative_role(sid)
    return r if r in ("FULL_STORY", "COMMENT", "PREVIEW", "TOPIC_INTRO", "IN_ONE_LINE") else "OTHER"

FLASH_LITE_ERA_START = "2026-09-27"
BODY_SEGMENTS = ("full_story_part1", "full_story_part2", "full_story_part3", "point_one", "point_two")


def _walk_attempt_jsons():
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in (".venv", ".git", "node_modules", "evidence_snapshot")]
        if os.path.basename(dp) != "attempts":
            continue
        for f in fn:
            if f.endswith(".json"):
                p = os.path.join(dp, f)
                try:
                    d = json.load(open(p, encoding="utf-8"))
                except Exception:
                    continue
                d["_path"] = p
                d["_wav"] = p[:-5] + ".wav"
                yield d


def _snapshot_coffee():
    d0 = os.path.join(SNAP, "a2_attempts")
    for f in sorted(os.listdir(d0)):
        if f.endswith(".json"):
            p = os.path.join(d0, f)
            d = json.load(open(p, encoding="utf-8"))
            d["_path"] = p
            d["_wav"] = p[:-5] + ".wav"
            d["_coffee_snapshot"] = True
            yield d


_canon_cache: dict = {}


def canonical_for(rec: dict):
    """attempt記録からcanonical(TTS入力)を復元する。復元できなければNone。"""
    if rec.get("_coffee_snapshot"):
        import er003_v1_n3_01_tts_generate as n3
        parts = json.load(open(os.path.join(SNAP, "a2_parts.json"), encoding="utf-8"))
        return n3.tts_safe_news_en(parts["part2"])
    p = rec["_path"]
    audit = os.path.normpath(os.path.join(os.path.dirname(p), "..", "..", "audit", "tts_generation_results.json"))
    if audit not in _canon_cache:
        try:
            _canon_cache[audit] = json.load(open(audit, encoding="utf-8")).get("segments") or {}
        except Exception:
            _canon_cache[audit] = {}
    seg = _canon_cache[audit].get(rec.get("segment_id"))
    if isinstance(seg, dict):
        return seg.get("text") or seg.get("canonical_text")
    return None


def ng_category(canon: str, asr: str, segment_id: str):
    """既存Validator(純関数)で再判定し、NGの種類を返す。"""
    c = val.classify_asr_match(canon, asr, segment_id=segment_id)
    if c.should_pass:
        return c.classification, "PASS", []
    p = c.protected
    diffs = [(d["canonical"], d["asr"], d["entity_like"], d["homophone_candidate"]) for d in p.content_word_diffs]
    if p.number_mismatches or p.negation_mismatches:
        return c.classification, "NUM_OR_NEGATION", diffs
    if c.classification == "TTS_FAILURE":
        return c.classification, "TTS_FAILURE_LOW_RATIO", diffs
    non_ent = [d for d in diffs if not d[2] and not d[3]]
    if non_ent:
        return c.classification, "CONTENT_WORD_NONENTITY", diffs
    if any(d[2] for d in diffs):
        return c.classification, "ENTITY_ONLY", diffs
    if any(d[3] for d in diffs):
        return c.classification, "HOMOPHONE_ONLY", diffs
    return c.classification, "OTHER_LOW_SIMILARITY", diffs


def group_calls(recs):
    by = collections.defaultdict(list)
    for r in recs:
        by[(os.path.dirname(r["_path"]), r.get("segment_id"))].append(r)
    calls = []
    for key, lst in by.items():
        lst.sort(key=lambda r: r["saved_at"])
        cur = []
        for r in lst:
            starts_new = (r.get("loop_attempt_index") == 1 and r.get("route") != "minimal_fallback")
            if starts_new and cur:
                calls.append(cur)
                cur = []
            cur.append(r)
        if cur:
            calls.append(cur)
    return calls


def collect():
    recs = []
    all_en = [r for r in _walk_attempt_jsons() if r.get("language") == "en" and r["saved_at"] >= FLASH_LITE_ERA_START]
    fl_dirs = {os.path.dirname(r["_path"]) for r in all_en if r.get("model") == "gemini-3.8-flash-lite-tts"}
    for r in all_en:
        # Flash-Lite期の判定は model で行う。ただし minimal_fallback route の attempt json は
        # main では model を p9a.ENGLISH_MODEL_NAME(=2.5-pro)と誤記録し tts_backend も保存しない(発見F-3追補)ため、
        # 同一ディレクトリにFlash-Lite標準attemptがある fallback 記録は Flash-Lite として扱う。
        if r.get("model") == "gemini-3.8-flash-lite-tts":
            recs.append(r)
        elif r.get("route") == "minimal_fallback" and os.path.dirname(r["_path"]) in fl_dirs:
            recs.append(r)
    coffee = list(_snapshot_coffee())
    # Coffeeの run_e_tone_01 は main ツリーには存在しない(worktree)。snapshot側だけを使うため、重複は無い。
    recs_all = recs + coffee
    calls = group_calls(recs_all)
    summary = {"n_attempt_records": len(recs_all), "n_calls": len(calls)}
    outcomes = collections.Counter()
    per_call = []
    ng_rows = []
    join_ok = join_total = 0
    cat_by_path = {}
    for call in calls:
        verified_idx = None
        for i, r in enumerate(call):
            if r.get("verified"):
                verified_idx = i + 1
                break
        std = [r for r in call if r.get("route") != "minimal_fallback"]
        fb = [r for r in call if r.get("route") == "minimal_fallback"]
        rec0 = call[0]
        per_call.append({
            "dir": os.path.relpath(os.path.dirname(rec0["_path"]), ROOT) if not rec0.get("_coffee_snapshot") else "coffee_snapshot",
            "segment_id": rec0.get("segment_id"), "level": rec0.get("level"), "role": role_of(rec0.get("segment_id")),
            "n_tts_in_call": len(call), "n_std": len(std), "n_fallback": len(fb),
            "verified_at_tts_index": verified_idx,
            "classes": [r.get("audio_classification") for r in call],
            "cascade_invoked": [bool(r.get("cascade_invoked")) for r in call],
            "first_saved_at": rec0["saved_at"],
        })
        if verified_idx is None:
            outcomes["no_pass_within_call(n_tts=%d)" % len(call)] += 1
        else:
            outcomes["pass_at_tts_%d(%s)" % (verified_idx, call[verified_idx - 1].get("route")[:16])] += 1
        for r in call:
            if r.get("verified"):
                continue
            canon = canonical_for(r)
            asr = r.get("asr_text")
            row = {"segment_id": r.get("segment_id"), "level": r.get("level"), "saved_at": r["saved_at"],
                   "route": r.get("route"), "recorded_class": r.get("audio_classification"),
                   "cascade_invoked": r.get("cascade_invoked"), "coffee": bool(r.get("_coffee_snapshot")),
                   "wav": r["_wav"] if os.path.exists(r["_wav"]) else None}
            if canon and asr:
                join_total += 1
                replay_class, cat, diffs = ng_category(canon, asr, r.get("segment_id"))
                row.update({"replay_class": replay_class, "category": cat, "diffs": diffs[:6],
                            "replay_matches_recorded": replay_class == r.get("audio_classification")})
                if replay_class == r.get("audio_classification"):
                    join_ok += 1
            else:
                row.update({"replay_class": None, "category": "NO_CANONICAL_OR_ASR", "diffs": []})
            ng_rows.append(row)
            cat_by_path[r["_path"]] = row["category"]
        per_call[-1]["attempt_categories"] = [cat_by_path.get(r["_path"], "PASS") for r in call]
        per_call[-1]["attempt_routes"] = [("fallback" if r.get("route") == "minimal_fallback" else "std") for r in call]
    # 集計
    cat = collections.Counter(r["category"] for r in ng_rows)
    cat_matched = collections.Counter(r["category"] for r in ng_rows if r.get("replay_matches_recorded"))
    seg_cat = collections.Counter((("narrative5" if role_of(r["segment_id"]) != "OTHER" else "other"), r["category"]) for r in ng_rows)
    n_calls = len(calls)
    pass_at = collections.Counter()
    for c in per_call:
        pass_at[c["verified_at_tts_index"]] += 1
    summary.update({
        "outcomes": dict(outcomes), "ng_attempt_rows": len(ng_rows), "ng_category": dict(cat),
        "ng_category_replay_matches_recorded_only": dict(cat_matched),
        "join_replay_match": f"{join_ok}/{join_total}", "ng_by_body_vs_other": {f"{k[0]}:{k[1]}": v for k, v in seg_cat.items()},
        "calls_pass_at_tts_index": {str(k): v for k, v in sorted(pass_at.items(), key=lambda x: (x[0] is None, x[0]))},
    })
    # 条件付き通過確率: 1回目NG後に2回目(std)で通る割合、3回目(fallback or std)で通る割合
    cond = {"std1_ng_calls": 0, "pass_at_2": 0, "ng_after_2": 0, "pass_at_3": 0, "ng_after_3": 0, "pass_at_3_by_route": {}}
    for c in per_call:
        cl = c["classes"]
        v = c["verified_at_tts_index"]
        if len(cl) >= 1 and v != 1:
            cond["std1_ng_calls"] += 1
            if v == 2:
                cond["pass_at_2"] += 1
            elif len(cl) >= 2:
                cond["ng_after_2"] += 1
                if v == 3:
                    cond["pass_at_3"] += 1
                elif len(cl) >= 3:
                    cond["ng_after_3"] += 1
    summary["conditional"] = cond
    # role別(5 narrative role vs OTHER)の通過位置と条件付き通過率
    by_role = {}
    for grp in ("NARRATIVE5", "OTHER"):
        sub = [c for c in per_call if (c["role"] != "OTHER") == (grp == "NARRATIVE5")]
        pa = collections.Counter(c["verified_at_tts_index"] for c in sub)
        n1ng = [c for c in sub if c["verified_at_tts_index"] != 1]
        ge2 = [c for c in n1ng if len(c["classes"]) >= 2]
        ng2 = [c for c in ge2 if c["verified_at_tts_index"] != 2]
        ge3 = [c for c in ng2 if len(c["classes"]) >= 3]
        by_role[grp] = {
            "calls": len(sub), "pass_at_1": pa.get(1, 0), "pass_at_2": pa.get(2, 0), "pass_at_3": pa.get(3, 0),
            "no_pass": pa.get(None, 0), "ng_at_1": len(n1ng), "reached_attempt2": len(ge2),
            "pass_at_2_given_reached2": pa.get(2, 0), "ng_after_2": len(ng2), "reached_attempt3": len(ge3),
            "pass_at_3_given_reached3": pa.get(3, 0),
            "calls_with_fallback_route": sum(1 for c in sub if c["n_fallback"] > 0),
        }
    summary["by_role_group"] = by_role
    # 新フロー(同一Prompt最大3回 + Primary NG時のSecondary確認)での完了見込み: 下限/上限(保存済みデータのみ)
    #  下限: Secondary救済ゼロ。旧フローでstd route 3回目までにPASSしたcallだけ完了とみなす
    #        (旧fallback route=別Promptの3回目は、同一Promptでの結果が不明なため完了に数えない)。
    #  上限: NG attempt全てがSecondary救済可能な種別(NUM_OR_NEGATION以外・CONTENT_WORD含む)なら、
    #        Secondaryがcanonicalを支持すると仮定して完了とみなす(誤認識側の救済上限)。
    nar = [c for c in per_call if c["role"] != "OTHER"]
    low = up = 0
    unknown_cat = 0
    for c in nar:
        v = c["verified_at_tts_index"]
        routes = c["attempt_routes"]
        if v is not None and v <= 3 and routes[v - 1] == "std":
            low += 1
            up += 1
            continue
        if v is not None and v <= 3 and routes[v - 1] == "fallback":
            up += 1  # 旧fallback PASSは、同一Promptで通る可能性(不明)として上限側のみ計上
            continue
        cats = [x for x in c["attempt_categories"] if x != "PASS"]
        if cats and all(x in ("ENTITY_ONLY", "HOMOPHONE_ONLY", "CONTENT_WORD_NONENTITY", "OTHER_LOW_SIMILARITY") for x in cats):
            up += 1
        if any(x == "NO_CANONICAL_OR_ASR" for x in cats):
            unknown_cat += 1
    summary["new_flow_completion_bounds_narrative5"] = {
        "calls": len(nar), "lower_bound_complete": low, "upper_bound_complete": up,
        "old_flow_complete_within_call": sum(1 for c in nar if c["verified_at_tts_index"] is not None),
        "calls_with_unclassifiable_ng": unknown_cat,
    }
    # 6%減速loop由来の重複(同一segmentで1callがOK後に再call)を検出: 同一dir+segmentでcallが2つ以上
    by_seg = collections.Counter((c["dir"], c["segment_id"]) for c in per_call)
    summary["segments_with_multiple_calls_(slowdown_or_regen)"] = sum(1 for v in by_seg.values() if v > 1)
    summary["segments_total"] = len(by_seg)
    json.dump({"summary": summary, "per_call": per_call, "ng_rows": ng_rows},
              open(os.path.join(OUT, "replay_results_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return summary, per_call, ng_rows


def unit_costs() -> dict:
    """Coffee実run(evidence_snapshot/raw_usage_log.jsonl)の実測usageと、登録単価(pricing_snapshot.json)から
    1call当たりの単価(JPY、USD/JPY=160)を計算する。課金APIは呼ばない。"""
    pricing = json.load(open(os.path.join(ROOT, "er005_output", "cost_baseline_01", "pricing_snapshot.json"),
                             encoding="utf-8"))["prices"]

    def price(provider, model, meter, tier="Standard"):
        return next(p["price"] for p in pricing if p["provider"] == provider and p["model"] == model
                    and p["meter"] == meter and p.get("tier", "Standard") == tier)

    rows = [json.loads(l) for l in open(os.path.join(SNAP, "raw_usage_log.jsonl"), encoding="utf-8")]
    jpy = 160.0
    tts = [r for r in rows if r["provider"] == "gemini_batch"]
    oa = [r for r in rows if r["provider"] == "openai_asr"]
    az = [r for r in rows if r["provider"] == "azure"]
    az_hour = next(p["price"] for p in pricing if p["provider"] == "azure")
    in_p, out_p = price("openai_asr", "gpt-4o-mini-transcribe", "input_tokens"), price("openai_asr", "gpt-4o-mini-transcribe", "output_tokens")
    part2_az = [r for r in az if r.get("audio_duration_submitted_seconds")]
    return {
        "usd_jpy": jpy,
        "tts_flash_lite_batch_jpy_per_call": round(sum(r.get("cost_usd") or 0 for r in tts) * jpy / len(tts), 4),
        "tts_elapsed_sec_mean": round(sum(r["elapsed_seconds"] for r in tts) / len(tts), 1),
        "openai_asr_jpy_per_call": round(sum((r["input_tokens"] * in_p + r["output_tokens"] * out_p) / 1e6 for r in oa) * jpy / len(oa), 4),
        "openai_asr_elapsed_sec_mean": round(sum(r["elapsed_seconds"] for r in oa) / len(oa), 2),
        "azure_usd_per_audio_hour": az_hour,
        "azure_jpy_per_call_mean_audio_%.0fs" % (sum(r["audio_duration_submitted_seconds"] for r in part2_az) / len(part2_az)):
            round(sum(r["audio_duration_submitted_seconds"] for r in part2_az) / 3600 * az_hour * jpy / len(part2_az), 4),
        "azure_jpy_per_second_audio": round(az_hour * jpy / 3600, 5),
        "azure_elapsed_sec_mean": round(sum(r["elapsed_seconds"] for r in az) / len(az), 1),
        "n_tts": len(tts), "n_openai_asr": len(oa), "n_azure": len(az),
        "azure_total_jpy_in_this_run": round(sum(r["audio_duration_submitted_seconds"] for r in az) / 3600 * az_hour * jpy, 3),
        "openai_asr_total_jpy_in_this_run": round(sum((r["input_tokens"] * in_p + r["output_tokens"] * out_p) / 1e6 for r in oa) * jpy, 3),
        "tts_total_jpy_in_this_run": round(sum(r.get("cost_usd") or 0 for r in tts) * jpy, 3),
    }


def qcd_model():
    """過去データ(replay_results_01.json)のnarrative5実測から、旧フロー実測値と新フロー推定値(Secondary救済率rの感度)を出す。"""
    d = json.load(open(os.path.join(OUT, "replay_results_01.json"), encoding="utf-8"))
    nar = [c for c in d["per_call"] if c["role"] != "OTHER"]
    uc = unit_costs()
    n = len(nar)
    tot_tts = sum(c["n_tts_in_call"] for c in nar)
    ng_attempts = sum(1 for c in nar for x in c["attempt_categories"] if x != "PASS")
    prot_or_fail = sum(1 for c in nar for x in c["attempt_categories"] if x in ("NUM_OR_NEGATION", "TTS_FAILURE_LOW_RATIO"))
    eligible = ng_attempts - prot_or_fail
    az_s = 40.0  # 本文segmentの平均音声長の概算(秒)。Coffee part2は約50秒、comment/previewは10〜20秒。
    out = {"unit_costs": uc, "narrative5_calls": n, "old_mean_tts_per_call": round(tot_tts / n, 3),
           "old_ng_attempts_per_call": round(ng_attempts / n, 3), "eligible_ng_fraction": round(eligible / max(ng_attempts, 1), 3),
           "assumed_audio_seconds_for_secondary": az_s}
    az_per = uc["azure_jpy_per_second_audio"] * az_s
    out["azure_jpy_per_secondary_call_assumed"] = round(az_per, 3)
    out["new_flow_extra_secondary_calls_per_call_if_every_eligible_ng_goes_to_secondary"] = round(eligible / n, 3)
    out["new_flow_extra_azure_jpy_per_call"] = round(eligible / n * az_per, 3)
    out["tts_jpy_per_call_old"] = round(tot_tts / n * uc["tts_flash_lite_batch_jpy_per_call"], 3)
    json.dump(out, open(os.path.join(OUT, "qcd_model_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1))


STRICT_SECONDARY_ACCEPT = ("EXACT_MATCH", "NORMALIZED_MATCH", "TRANSCRIPT_STYLE_NORMALIZED_MATCH", "NUMERIC_EQUIVALENCE_MATCH")


def mutation_safety():
    """Secondary転写が「真の内容誤り」を含む場合に、既存Validator(classify_asr_match)+厳格PASS集合
    (STRICT_SECONDARY_ACCEPT)が誤PASSしないかを、合成した転写で無料検証する(API不使用)。
    canonicalはCoffee full_story_part2のTTS入力。mutationは1箇所ずつ入れる。"""
    import er003_v1_n3_01_tts_generate as n3
    parts = json.load(open(os.path.join(SNAP, "a2_parts.json"), encoding="utf-8"))
    base = n3.tts_safe_news_en(parts["part2"])
    reps = [  # (name, kind, old, new)  kind: MUST_REJECT=真の内容誤り, MAY_ACCEPT=表記・ASR表記差
        ("number_6.1->6.7", "MUST_REJECT", "6.1%", "6.7%"),
        ("number_nine->ten months", "MUST_REJECT", "about 9 months", "about 10 months"),
        ("number_2->3 numbers", "MUST_REJECT", "the 2 numbers", "the 3 numbers"),
        ("negation_does_not->does", "MUST_REJECT", "It also does not show", "It also does show"),
        ("negation_does_not->did_not", "MUST_REJECT", "does not change the moment", "did not change the moment"),
        ("tense_showed->show", "MUST_REJECT", "showed coffee cost", "show coffee cost"),
        ("tense_spoke->speak", "MUST_REJECT", "experts spoke with Reuters", "experts speak with Reuters"),
        ("key_word_omitted_raw", "MUST_REJECT", "raw-bean prices", "bean prices"),
        ("key_word_substituted_raw_beans->Robbins", "MUST_REJECT", "keep raw beans in stock", "keep Robbins in stock"),
        ("key_word_fall->rise", "MUST_REJECT", "Did prices fall or rise", "Did prices rise or rise"),
        ("word_at_least->at_most", "MUST_REJECT", "at least about", "at most about"),
        ("entity_Reuters->Router", "MUST_REJECT", "Reuters", "Router"),
        ("benign_plural_cost->costs", "MAY_ACCEPT", "coffee cost 6.1%", "coffee costs 6.1%"),
        ("benign_US->U.S.", "MAY_ACCEPT", "US data", "U.S. data"),
        ("benign_contraction_Don't->Do not", "MAY_ACCEPT", "Don't put", "Do not put"),
        ("benign_nine_vs_9", "MAY_ACCEPT", "about 9 months", "about nine months"),
        ("benign_two_vs_2", "MAY_ACCEPT", "the 2 numbers", "the two numbers"),
        ("benign_punct_dash", "MAY_ACCEPT", "raw-bean", "raw bean"),
        ("compound_US_U.S.+cost->costs (Coffee attempt3 pattern)", "MAY_ACCEPT", None, None),
    ]
    rows = []
    for name, kind, old, new in reps:
        if old is None:
            t = base.replace("US data", "U.S. data").replace("coffee cost 6.1%", "coffee costs 6.1%")
        else:
            if old not in base:
                rows.append({"name": name, "kind": kind, "error": f"pattern not found: {old!r}"})
                continue
            t = base.replace(old, new, 1)
        c = val.classify_asr_match(base, t, segment_id="full_story_part2")
        p = c.protected
        accepted = c.should_pass and c.classification in STRICT_SECONDARY_ACCEPT
        rows.append({"name": name, "kind": kind, "classification": c.classification, "should_pass": c.should_pass,
                     "strict_accept": accepted, "num_neg_mismatch": bool(p.number_mismatches or p.negation_mismatches),
                     "diffs": [(d["canonical"], d["asr"]) for d in p.content_word_diffs][:4]})
    # 追加: 文長・欠落系(語尾脱落/幻覚追加/文反復)
    sents = re.split(r"(?<=[.?!])\s+", base)
    tails = {
        "tail_truncated_last_sentence": " ".join(sents[:-1]),
        "extra_hallucinated_sentence": base + " This is a brand new claim about tea prices.",
        "repeated_sentence": " ".join(sents[:3] + [sents[2]] + sents[3:]),
        "middle_sentence_missing": " ".join(sents[:4] + sents[5:]),
    }
    for name, t in tails.items():
        c = val.classify_asr_match(base, t, segment_id="full_story_part2")
        rows.append({"name": name, "kind": "MUST_REJECT", "classification": c.classification, "should_pass": c.should_pass,
                     "strict_accept": c.should_pass and c.classification in STRICT_SECONDARY_ACCEPT,
                     "num_neg_mismatch": bool(c.protected.number_mismatches or c.protected.negation_mismatches),
                     "diffs": [(d["canonical"], d["asr"]) for d in c.protected.content_word_diffs][:4]})
    must = [r for r in rows if r["kind"] == "MUST_REJECT" and "error" not in r]
    may = [r for r in rows if r["kind"] == "MAY_ACCEPT" and "error" not in r]
    summ = {"must_reject_total": len(must), "must_reject_falsely_accepted": [r["name"] for r in must if r["strict_accept"]],
            "may_accept_total": len(may), "may_accept_accepted": [r["name"] for r in may if r["strict_accept"]],
            "may_accept_rejected": [r["name"] for r in may if not r["strict_accept"]]}
    json.dump({"summary": summ, "rows": rows}, open(os.path.join(OUT, "mutation_safety_01.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(json.dumps(summ, ensure_ascii=False, indent=1))
    for r in rows:
        print(r.get("name"), "|", r.get("kind"), "|", r.get("classification"), "|strict_accept=", r.get("strict_accept"), "|", r.get("diffs"))


def wilson(k: int, n: int, z: float = 1.96):
    if n == 0:
        return (None, None)
    ph = k / n
    den = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / den
    h = z * ((ph * (1 - ph) / n + z * z / (4 * n * n)) ** 0.5) / den
    return (round(c - h, 3), round(c + h, 3))


def qcd_scenarios():
    """新フロー(同一Prompt最大3回 + Primary NG時のSecondary 1回)の期待TTS/ASR/HR率を、
    過去実測(narrative5, replay_results_01.json)のPrimary通過率とSecondary救済率rの感度で試算する(確率モデル)。"""
    d = json.load(open(os.path.join(OUT, "replay_results_01.json"), encoding="utf-8"))
    g = d["summary"]["by_role_group"]["NARRATIVE5"]
    n = g["calls"]
    p1 = g["pass_at_1"] / n
    p2 = g["pass_at_2_given_reached2"] / g["reached_attempt2"]
    p3 = g["pass_at_3_given_reached3"] / g["reached_attempt3"]
    q = json.load(open(os.path.join(OUT, "qcd_model_01.json"), encoding="utf-8"))
    e = q["eligible_ng_fraction"]
    uc = q["unit_costs"]
    az_s = q["assumed_audio_seconds_for_secondary"]
    az_jpy = uc["azure_jpy_per_second_audio"] * az_s
    tts_jpy, asr_jpy = uc["tts_flash_lite_batch_jpy_per_call"], uc["openai_asr_jpy_per_call"]
    rows = []
    for r in (0.0, 0.2, 0.4, 0.6, 0.8):
        rescue = e * r
        n1 = 1 - p1
        reach2 = n1 * (1 - rescue)
        reach3 = reach2 * (1 - p2) * (1 - rescue)
        e_tts = 1 + reach2 + reach3
        e_prim = e_tts
        sec_calls = e * (n1 + reach2 * (1 - p2) + reach3 * (1 - p3))
        hr = reach3 * (1 - p3) * (1 - rescue)
        cost = e_tts * tts_jpy + e_prim * asr_jpy + sec_calls * az_jpy
        rows.append({"secondary_rescue_rate_r": r, "E_TTS": round(e_tts, 3), "E_primary_ASR": round(e_prim, 3),
                     "E_secondary_calls": round(sec_calls, 3), "P_human_review": round(hr, 4),
                     "E_cost_jpy_per_segment_azure": round(cost, 3),
                     "E_cost_jpy_per_segment_if_secondary_is_local_whisper": round(e_tts * tts_jpy + e_prim * asr_jpy, 3)})
    out = {"params": {"p_pass_attempt1": round(p1, 4), "p_pass_attempt1_wilson95": wilson(g["pass_at_1"], n),
                      "p_pass_attempt2_given_reached": round(p2, 4),
                      "p2_wilson95": wilson(g["pass_at_2_given_reached2"], g["reached_attempt2"]),
                      "p_pass_attempt3_given_reached": round(p3, 4),
                      "p3_wilson95": wilson(g["pass_at_3_given_reached3"], g["reached_attempt3"]),
                      "eligible_ng_fraction": e, "tts_jpy": tts_jpy, "openai_asr_jpy": asr_jpy,
                      "azure_jpy_per_call(assumed_audio_s=%d)" % az_s: round(az_jpy, 3), "n_calls": n},
           "old_flow_observed": {"E_TTS_per_call": q["old_mean_tts_per_call"], "calls": n,
                                 "no_pass_within_call": g["no_pass"],
                                 "no_pass_rate": round(g["no_pass"] / n, 4),
                                 "no_pass_wilson95": wilson(g["no_pass"], n)},
           "new_flow_scenarios": rows}
    json.dump(out, open(os.path.join(OUT, "qcd_scenarios_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1))


def local_medium_followup():
    """local(small)で Primary PASS 対照が NG になった項目と、NG attempt全件を、より精度の高い medium で再転写する(無料)。
    smallの偽NG(精度限界)と、Primary誤PASSの切り分けのため。"""
    small = json.load(open(os.path.join(OUT, "local_proxy_results_01.json"), encoding="utf-8"))
    cache_path = os.path.join(OUT, "local_asr_cache_01.json")
    cache = json.load(open(cache_path, encoding="utf-8")) if os.path.exists(cache_path) else {}
    out = []
    # 優先順: (1) Primary PASS対照でsmallがNGだった項目(Primary誤PASSかsmall精度限界かの切り分け)、
    #         (2) 内容語NG(救済余地の確認)。数値/否定/entity-onlyは小規模検証済みのため省略(時間短縮)。
    order = [x for x in small if x["kind"] == "CONTROL_PRIMARY_PASS" and not x["local_pass"]] +             [x for x in small if x["kind"] == "NG" and x["primary_category"] in ("CONTENT_WORD_NONENTITY", "OTHER_LOW_SIMILARITY")]
    for x in order:
        wav = os.path.join(ROOT, x["wav"])
        key = f"medium|{wav}"
        if key not in cache:
            cache[key] = _local_text(wav, "medium")
            json.dump(cache, open(cache_path, "w", encoding="utf-8"), ensure_ascii=False)
        rec = json.load(open(wav[:-4] + ".json", encoding="utf-8"))
        canon = canonical_for({**rec, "_path": wav[:-4] + ".json"})
        c = val.classify_asr_match(canon, cache[key], segment_id=rec.get("segment_id"))
        out.append({**x, "medium_class": c.classification, "medium_pass": c.should_pass,
                    "medium_diffs": [(d["canonical"], d["asr"]) for d in c.protected.content_word_diffs][:4]})
        print(x["kind"], x["primary_category"], "small:", x["local_class"], "medium:", c.classification, flush=True)
    json.dump(out, open(os.path.join(OUT, "local_proxy_medium_followup_01.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)


def _local_text(path: str, size: str = "small") -> str:
    import er008_disfluency_qa_18 as dq
    model = dq._get_model(size)
    segments, _info = model.transcribe(path, language="en", condition_on_previous_text=False, vad_filter=False)
    t = " ".join(s.text.strip() for s in segments).strip()
    return re.sub(r"\s+([.%,?!])", lambda m: m.group(1), t)


def local(max_ng: int = 120, n_control: int = 40, size: str = "small"):
    """NG attempt(保存wavがあるもの)と、通過済みattemptの対照サンプルを、ローカルwhisper(無料)で再転写し、
    Primary(OpenAI)とは独立な第三のASRとして、Validatorで再判定する(Secondary救済率・Primary誤PASS率の代理指標)。
    ※Azure Secondaryそのものではない。結果は代理指標として扱うこと。"""
    cache_path = os.path.join(OUT, "local_asr_cache_01.json")
    cache = json.load(open(cache_path, encoding="utf-8")) if os.path.exists(cache_path) else {}
    summary, per_call, ng_rows = collect()
    ng_with_wav = [r for r in ng_rows if r.get("wav") and r.get("category") not in ("NO_CANONICAL_OR_ASR",)
                   and r.get("replay_matches_recorded")]
    random.seed(20261011)
    # NG attempt
    targets = []
    for r in ng_with_wav[:max_ng]:
        targets.append(("NG", r))
    # control: verified attempts
    ctrl_pool = []
    for rec in _walk_attempt_jsons():
        if rec.get("language") != "en" or not rec.get("verified"):
            continue
        if rec.get("model") != "gemini-3.8-flash-lite-tts" or rec["saved_at"] < FLASH_LITE_ERA_START:
            continue
        if not os.path.exists(rec["_wav"]):
            continue
        canon = canonical_for(rec)
        if canon and rec.get("asr_text"):
            ctrl_pool.append((rec, canon))
    random.shuffle(ctrl_pool)
    results = []
    for kind, r in targets:
        wav = r["wav"]
        key = f"{size}|{wav}"
        if key not in cache:
            cache[key] = _local_text(wav, size)
            json.dump(cache, open(cache_path, "w", encoding="utf-8"), ensure_ascii=False)
        rec_path = wav[:-4] + ".json"
        rec = json.load(open(rec_path, encoding="utf-8"))
        canon = canonical_for({**rec, "_path": rec_path})
        if not canon:
            continue
        c = val.classify_asr_match(canon, cache[key], segment_id=rec.get("segment_id"))
        results.append({"kind": kind, "wav": os.path.relpath(wav, ROOT), "segment_id": rec.get("segment_id"),
                        "primary_recorded_class": rec.get("audio_classification"), "primary_category": r["category"],
                        "local_class": c.classification, "local_pass": c.should_pass,
                        "local_num_neg_mismatch": bool(c.protected.number_mismatches or c.protected.negation_mismatches)})
    for rec, canon in ctrl_pool[:n_control]:
        wav = rec["_wav"]
        key = f"{size}|{wav}"
        if key not in cache:
            cache[key] = _local_text(wav, size)
            json.dump(cache, open(cache_path, "w", encoding="utf-8"), ensure_ascii=False)
        c = val.classify_asr_match(canon, cache[key], segment_id=rec.get("segment_id"))
        results.append({"kind": "CONTROL_PRIMARY_PASS", "wav": os.path.relpath(wav, ROOT), "segment_id": rec.get("segment_id"),
                        "primary_recorded_class": rec.get("audio_classification"), "primary_category": "PASS",
                        "local_class": c.classification, "local_pass": c.should_pass,
                        "local_num_neg_mismatch": bool(c.protected.number_mismatches or c.protected.negation_mismatches)})
    json.dump(results, open(os.path.join(OUT, "local_proxy_results_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    agg = collections.Counter()
    for x in results:
        agg[(x["kind"], x["primary_category"], "local_pass" if x["local_pass"] else "local_ng")] += 1
    for k, v in sorted(agg.items()):
        print(k, v)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "collect"
    {"collect": collect, "local": local, "qcd": qcd_model, "mutations": mutation_safety, "medium": local_medium_followup, "scenarios": qcd_scenarios}[cmd]()
