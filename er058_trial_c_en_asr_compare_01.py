"""ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_04C: Trial C 英語ASR比較(縮小版、Trial限定)。

現行方式(Primary -> UNCERTAIN時のみ4段Cascade、Phrase List付きAzure ...)と統一案(Primary NG -> Secondary
[Phrase Listなし・厳格ラベル] -> 両NGなら同一条件再生成 ...)を、過去の保存済み英語音声・転写で比較する。

- 新規TTS生成なし(保存音声のみ)。Production telemetry / queue / attempt_history / Master Store へ書込まない
  (出力は er058_output/trial_c/ のみ。er006_secondary_asr_01 の Azure関数は cl.record で
  Production費用ログへ書込むため使わず、本scriptに書込なしのAzure転写関数を持つ)。
- 追加課金は Azure STT(Phrase Listなし)のみ。--approved-budget-jpy 40 必須、累積見込が超えたら停止。

使い方:
  python er058_trial_c_en_asr_compare_01.py estimate                     # 対象選定+費用見積(課金0)
  python er058_trial_c_en_asr_compare_01.py local                        # ローカルwhisper(無料)で転写キャッシュ作成
  python er058_trial_c_en_asr_compare_01.py dry                          # mock(Azure擬似応答)で全工程を乾式実行(課金0)
  python er058_trial_c_en_asr_compare_01.py real --approved-budget-jpy 40   # 本実行(Azure課金あり)
  python er058_trial_c_en_asr_compare_01.py analyze [--mock]             # 集計(課金0、real後に再計算可)
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import random
import re
import sys
import time
import wave

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
OUT = os.path.join(ROOT, "er058_output", "trial_c")
P56 = os.path.join(ROOT, "er056_output", "en_asr_confirm_retry_redesign_01")
sys.stdout = open(1, "w", encoding="utf-8", closefd=False, buffering=1)

JPY_PER_USD = 160.0
AZURE_USD_PER_HOUR = 1.0  # er005_output/cost_baseline_01/pricing_snapshot.json(azure STT S1/S0 real-time)
AZURE_JPY_PER_SEC = AZURE_USD_PER_HOUR * JPY_PER_USD / 3600.0
BUDGET_JPY_HARD = 40.0
STRICT = ("EXACT_MATCH", "NORMALIZED_MATCH", "TRANSCRIPT_STYLE_NORMALIZED_MATCH", "NUMERIC_EQUIVALENCE_MATCH")
SEED = 20261012

import er006_preprod_hardening_01_validation as val  # noqa: E402


# ---------------------------------------------------------------- 対象選定
def _dur(w):
    with wave.open(w) as f:
        return f.getnframes() / f.getframerate()


def _sha(w):
    return hashlib.sha256(open(w, "rb").read()).hexdigest()


def _abs(p):
    return p if os.path.isabs(p) else os.path.join(ROOT, p)


def build_sample():
    import er056_en_asr_retry_replay_01 as rp  # read-only helper(canonical_for)。import時にstdoutを再ラップする
    sys.stdout = open(1, "w", encoding="utf-8", closefd=False, buffering=1)
    proxy = json.load(open(os.path.join(P56, "local_proxy_results_01.json"), encoding="utf-8"))
    rnd = random.Random(SEED)
    items, seen = [], set()

    def add(it):
        if it["sha"] in seen:
            return False
        seen.add(it["sha"])
        items.append(it)
        return True

    # (1) Primary NG 群: er056 の保存wav NG attempt 全件(sha重複除外)
    for x in proxy:
        if x["kind"] != "NG":
            continue
        w = _abs(x["wav"])
        rec = json.load(open(w[:-4] + ".json", encoding="utf-8"))
        canon = rp.canonical_for({**rec, "_path": w[:-4] + ".json"})
        rep = rec.get("repetition_qa_evidence") or {}
        dis = rec.get("disfluency_evidence")
        add({"group": "PRIMARY_NG", "wav": os.path.relpath(w, ROOT), "sha": _sha(w), "dur": _dur(w),
             "segment_id": rec.get("segment_id"), "canonical": canon, "primary_text": rec.get("asr_text"),
             "primary_recorded_class": rec.get("audio_classification"), "primary_category": x["primary_category"],
             "verified": bool(rec.get("verified")), "length_ok": rec.get("length_ok") is not False,
             "repetition_flagged": bool(rep.get("flagged")) if isinstance(rep, dict) else False,
             "disfluency_flagged": bool(dis.get("flagged")) if isinstance(dis, dict) else False,
             "cascade_invoked": bool(rec.get("cascade_invoked")), "cascade_steps": rec.get("cascade_steps") or [],
             "azure_pl_text": next((s.get("text") for s in (rec.get("cascade_steps") or []) if s.get("step") == "secondary_1"), None)})
    # (2) HR queue(現行方式でHumanReviewに落ちた実例): forced-Secondary 優先 + 短い順に補充(上限6本、<=12秒)
    hr = [json.loads(l) for l in open(os.path.join(ROOT, "er006_output", "audio_retry_cascade_prod_01", "human_review_queue.jsonl"), encoding="utf-8")]
    cand = []
    for r in hr:
        w = _abs(r["wav_path"])
        if not os.path.exists(w):
            continue
        forced = any(s["step"] == "secondary_forced" for s in r["steps"])
        cand.append((0 if forced else 1, _dur(w), w, r, forced))
    cand.sort(key=lambda t: (t[0], t[1]))
    n_hr = 0
    for _, d, w, r, forced in cand:
        if n_hr >= 6 or d > 12:
            continue
        steps = r["steps"]
        p1 = next(s for s in steps if s["step"] == "primary_1")
        az = next((s for s in steps if s["step"] in ("secondary_1", "secondary_forced")), None)
        if add({"group": "HR_QUEUE_FORCED" if forced else "HR_QUEUE", "wav": os.path.relpath(w, ROOT), "sha": _sha(w), "dur": d,
                "segment_id": os.path.basename(w)[:-4], "canonical": r["canonical_text"], "primary_text": p1.get("text"),
                "primary_recorded_class": p1.get("classification"), "primary_category": "PASS" if forced else "HR_QUEUE_UNCERTAIN",
                "verified": False, "length_ok": True, "repetition_flagged": False, "disfluency_flagged": False,
                "cascade_invoked": True, "cascade_steps": steps, "azure_pl_text": az.get("text") if az else None}):
            n_hr += 1
    # (3) Primary PASS 対照(<=8本、合計<=90秒): local small が NG だった4本 + PASS だった4本(短い音声から無作為)
    ctrl = [x for x in proxy if x["kind"] == "CONTROL_PRIMARY_PASS"]
    rnd.shuffle(ctrl)
    total, got = 0.0, collections.Counter()
    for x in ctrl:
        w = _abs(x["wav"])
        d = _dur(w)
        key = "local_ng" if not x["local_pass"] else "local_pass"
        if d > 20 or got[key] >= 4 or total + d > 90 or _sha(w) in seen:
            continue
        rec = json.load(open(w[:-4] + ".json", encoding="utf-8"))
        canon = rp.canonical_for({**rec, "_path": w[:-4] + ".json"})
        if not canon or not rec.get("asr_text"):
            continue
        add({"group": "CONTROL_PRIMARY_PASS", "wav": os.path.relpath(w, ROOT), "sha": _sha(w), "dur": d,
             "segment_id": rec.get("segment_id"), "canonical": canon, "primary_text": rec.get("asr_text"),
             "primary_recorded_class": rec.get("audio_classification"), "primary_category": "PASS", "verified": True,
             "length_ok": True, "repetition_flagged": False, "disfluency_flagged": False, "cascade_invoked": False,
             "cascade_steps": rec.get("cascade_steps") or [], "azure_pl_text": None})
        total += d
        got[key] += 1
    for i, it in enumerate(items):
        it["id"] = f"S{i + 1:02d}"
    return items


def estimate(items):
    tot = sum(i["dur"] for i in items)
    est = tot * AZURE_JPY_PER_SEC
    by = collections.defaultdict(lambda: [0, 0.0])
    for i in items:
        by[i["group"]][0] += 1
        by[i["group"]][1] += i["dur"]
    return {"n_files": len(items), "total_audio_sec": round(tot, 1), "jpy_per_sec": round(AZURE_JPY_PER_SEC, 5),
            "estimated_azure_jpy": round(est, 2),
            "by_group": {k: {"n": v[0], "sec": round(v[1], 1), "jpy": round(v[1] * AZURE_JPY_PER_SEC, 2)} for k, v in by.items()}}


# ---------------------------------------------------------------- ASR
def azure_nopl(wav, language="en-US", timeout=90.0):
    """Phrase Listなし連続認識。er006 の関数と同一方式だが cl.record(Production費用ログ書込)を行わない。"""
    from dotenv import load_dotenv
    import azure.cognitiveservices.speech as speechsdk
    load_dotenv()
    key, region = os.getenv("SPEECH_KEY"), os.getenv("SPEECH_REGION")
    if not key or not region:
        return None, "SPEECH_KEY/REGION missing", 0.0
    cfg = speechsdk.SpeechConfig(subscription=key, region=region)
    cfg.speech_recognition_language = language
    rec = speechsdk.SpeechRecognizer(speech_config=cfg, audio_config=speechsdk.audio.AudioConfig(filename=wav))
    segs, done = [], {"f": False}
    rec.recognized.connect(lambda e: segs.append(e.result.text) if e.result.reason == speechsdk.ResultReason.RecognizedSpeech else None)
    rec.session_stopped.connect(lambda e: done.__setitem__("f", True))
    rec.canceled.connect(lambda e: done.__setitem__("f", True))
    t0 = time.time()
    rec.start_continuous_recognition()
    while not done["f"] and time.time() - t0 < timeout:
        time.sleep(0.3)
    rec.stop_continuous_recognition()
    el = round(time.time() - t0, 2)
    if not done["f"]:
        return None, "timeout", el
    return "".join(segs), None, el


def local_text(wav, size):
    import er008_disfluency_qa_18 as dq
    model = dq._get_model(size)
    segs, _ = model.transcribe(wav, language="en", condition_on_previous_text=False, vad_filter=False)
    t = " ".join(s.text.strip() for s in segs).strip()
    return re.sub(r"\s+([.%,?!])", lambda m: m.group(1), t)


def cmd_local(items):
    """local small/medium(無料、CPU)。既存キャッシュ(er056、読込のみ)を再利用し、新規分は本Trialのキャッシュへ書く。"""
    old = json.load(open(os.path.join(P56, "local_asr_cache_01.json"), encoding="utf-8"))
    path = os.path.join(OUT, "local_asr_cache_C_01.json")
    cache = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    for it in items:
        w = _abs(it["wav"])
        for size in ("small", "medium"):
            k = f"{size}|{w}"
            if k in cache:
                continue
            if k in old:
                cache[k] = old[k]
                continue
            t0 = time.time()
            cache[k] = local_text(w, size)
            print(it["id"], size, round(time.time() - t0, 1), "s", flush=True)
            json.dump(cache, open(path, "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(cache, open(path, "w", encoding="utf-8"), ensure_ascii=False)
    print("local cache entries", len(cache))


def cmd_azure(items, mock, budget):
    fn = os.path.join(OUT, "azure_nopl_C_01%s.json" % ("_mock" if mock else ""))
    res = json.load(open(fn, encoding="utf-8")) if os.path.exists(fn) else {}
    spent = sum(v.get("billed_jpy", 0) for v in res.values())
    for it in items:
        if it["id"] in res and res[it["id"]].get("text") is not None:
            continue
        cost = it["dur"] * AZURE_JPY_PER_SEC
        if not mock and spent + cost > min(budget, BUDGET_JPY_HARD):
            print("STOP: budget guard", spent, cost)
            break
        if mock:
            text, err, el = it["canonical"], None, 0.0  # 乾式: 原稿そのまま(パイプライン検証のみ、結果は評価に使わない)
            billed = 0.0
        else:
            text, err, el = azure_nopl(_abs(it["wav"]))
            billed = cost  # 成否に関わらず送信秒数分を課金見込みとして計上(保守的)
        spent += billed
        res[it["id"]] = {"text": text, "error": err, "elapsed_sec": el, "audio_sec": round(it["dur"], 2),
                         "billed_jpy": round(billed, 4), "phrase_list": False}
        json.dump(res, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(it["id"], it["group"], round(it["dur"], 1), "s", "err=" + str(err) if err else "ok", "spent=%.2f" % spent, flush=True)
    actual = {"mock": mock, "n_calls": sum(1 for v in res.values() if v.get("text") is not None or v.get("error")),
              "audio_sec_total": round(sum(v["audio_sec"] for v in res.values()), 1),
              "azure_jpy_actual_estimate": round(sum(v["billed_jpy"] for v in res.values()), 2),
              "basis": "送信秒数(WAVヘッダ)x $1.00/h x 160円/USD。Azure課金は送信音声秒数ベース(成否問わず計上)。",
              "budget_jpy_approved": budget,
              "elapsed_sec_mean": round(sum(v["elapsed_sec"] for v in res.values()) / max(1, len(res)), 1),
              "other_paid_calls": "なし(OpenAI/Gemini/LLM/TTS呼出0。localはfaster-whisper CPU無料)"}
    json.dump(actual, open(os.path.join(OUT, "cost_actual_C_01%s.json" % ("_mock" if mock else "")), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(json.dumps(actual, ensure_ascii=False))


# ---------------------------------------------------------------- 判定
def cls(canon, text, seg):
    if text is None:
        return None
    return val.classify_asr_match(canon, text, segment_id=seg)


def sig(c):
    """差分の署名(内容語diff + 数字/否定差の有無)。"""
    if c is None:
        return None
    p = c.protected
    s = {("d", d["canonical"], d["asr"]) for d in p.content_word_diffs}
    if p.number_mismatches or p.negation_mismatches:
        s.add(("numneg",))
    return frozenset(s)


def numneg(c):
    return bool(c is not None and (c.protected.number_mismatches or c.protected.negation_mismatches))


def strict_pass(c):
    return bool(c is not None and c.should_pass and c.classification in STRICT)


def lev(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[-1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def minimal_pair(c):
    """Primary差分が最小対・形態素型(-s/-ed/-ing/冠詞/編集距離<=2)のみか。PASS_WITH_WARNING(最終試聴連動)の判定。"""
    if c is None:
        return False
    diffs = c.protected.content_word_diffs
    if not diffs or numneg(c):
        return False
    for d in diffs:
        a, b = (d["canonical"] or "").lower().strip(), (d["asr"] or "").lower().strip()
        if (not a and b in ("a", "an", "the")) or (not b and a in ("a", "an", "the")):
            continue
        if a and b and lev(a, b) <= 2:
            continue
        return False
    return True


def gate_reason(it, cp):
    """Secondary不呼出条件(統一案の安全条件)。"""
    from er006_secondary_asr_01 import is_non_latin_dominant_mismatch
    if numneg(cp):
        return "numeric_or_negation_diff"
    if not it["length_ok"]:
        return "length_not_ok"
    if it["repetition_flagged"] or it["disfluency_flagged"]:
        return "repetition_or_disfluency_QA"
    if is_non_latin_dominant_mismatch(it["primary_text"]):
        return "language_drift"
    return None


def evaluate_item(it, az_text, cache):
    w = _abs(it["wav"])
    canon, seg = it["canonical"], it["segment_id"]
    systems = {"openai_primary": it["primary_text"], "azure_noPL": az_text, "azure_PL_stored": it["azure_pl_text"],
               "local_small": cache.get(f"small|{w}"), "local_medium": cache.get(f"medium|{w}")}
    cl = {k: cls(canon, t, seg) for k, t in systems.items()}
    row = {"id": it["id"], "group": it["group"], "wav": it["wav"], "segment_id": seg, "dur_sec": round(it["dur"], 2),
           "primary_category": it["primary_category"], "systems": {}}
    for k, c in cl.items():
        row["systems"][k] = None if c is None else {
            "class": c.classification, "should_pass": c.should_pass, "strict_pass": strict_pass(c), "numneg": numneg(c),
            "diffs": [(d["canonical"], d["asr"]) for d in c.protected.content_word_diffs][:5]}
    # 代理ラベル(真の正解はない。独立系統の合意): 系統族 = openai / azure / whisper
    fam = {"openai": cl["openai_primary"], "azure": cl["azure_noPL"], "whisper": cl["local_medium"] or cl["local_small"]}
    # 族の合否は Validator の should_pass(lenientを含む=Validator自身が良性と扱う差)で判定。厳格ラベル判定は統一案側で別に行う
    fails = {f: c for f, c in fam.items() if c is not None and not c.should_pass}
    passes = {f for f, c in fam.items() if c is not None and c.should_pass}
    common = collections.Counter()
    benign = {("d", "us", "u s")}  # 既知のASR表記アーティファクト(F-5: US -> "u s")は一致診断から除く
    for c in fails.values():
        for x in (sig(c) or ()):
            if x not in benign:
                common[x] += 1
    agree_err = [x for x, n in common.items() if n >= 2]
    if agree_err:
        label = "TRUE_ERROR_SUSPECT"
    elif len(passes) >= 2:
        label = "FALSE_NG_LIKELY" if it["group"] != "CONTROL_PRIMARY_PASS" else "PRIMARY_PASS_CONFIRMED"
    else:
        label = "AMBIGUOUS" if it["group"] != "CONTROL_PRIMARY_PASS" else "PRIMARY_PASS_UNCONFIRMED"
    # canonical復元の健全性: 保存された Primary 分類を再現できない(原稿が後で書換わった等)場合は評価対象から除外
    if it["group"] != "HR_QUEUE" and it.get("primary_recorded_class") and cl["openai_primary"] is not None and (cl["openai_primary"].should_pass != (it["primary_recorded_class"] not in ("TRUE_CONTENT_MISMATCH", "TTS_FAILURE", "ASR_VALIDATION_UNCERTAIN"))):
        label = "EXCLUDED_CANONICAL_MISMATCH"
        row["excluded_reason"] = f"Primary再判定 {cl['openai_primary'].classification} != 記録 {it['primary_recorded_class']}"
    if it["azure_pl_text"] is not None and az_text is not None and it["group"].startswith("HR"):
        import difflib
        ratio = difflib.SequenceMatcher(None, re.sub(r"\W+", " ", it["azure_pl_text"].lower()), re.sub(r"\W+", " ", az_text.lower())).ratio()
        row["pl_vs_nopl_text_ratio"] = round(ratio, 3)
        if ratio < 0.5:  # 同じwavなら両Azure転写は近いはず -> wavが後から上書きされたと判断
            label = "EXCLUDED_AUDIO_CHANGED"
            row["excluded_reason"] = f"保存PL転写とnoPL転写が大きく異なる(ratio={ratio:.2f}): wavが後から上書きされた疑い"
    row["proxy_label"] = label
    row["proxy_label_agreed_error_signature"] = [list(x) for x in agree_err][:4]
    cp, ca = cl["openai_primary"], cl["azure_noPL"]
    # --- 現行(実績): 記録されたverified/HRをそのまま採用
    row["current_flow"] = {"outcome": "PASS" if it["verified"] else ("HUMAN_REVIEW" if it["group"].startswith("HR") else "NG_REGEN_OR_CASCADE_NG"),
                           "cascade_invoked": it["cascade_invoked"]}
    if it["group"] == "HR_QUEUE_FORCED":
        row["current_flow"]["outcome"] = "HUMAN_REVIEW(Primary PASSだがforced-Secondary NG)"
    # --- 統一案(安全条件あり): Primary PASS完了 / NG -> 安全条件 -> Secondary(noPL, 厳格ラベル)
    if it["group"] in ("CONTROL_PRIMARY_PASS", "HR_QUEUE_FORCED"):
        u = {"outcome": "PASS", "secondary_called": False, "reason": "primary_pass(Secondaryは呼ばない)"}
        o = {"outcome": "PASS", "secondary_called": False}
    else:
        g = gate_reason(it, cp)
        if g:
            u = {"outcome": "NG_REGEN", "secondary_called": False, "gate": g}
        elif ca is None:
            u = {"outcome": "NG_REGEN", "secondary_called": True, "reason": "secondary_error"}
        elif strict_pass(ca):
            u = {"outcome": "PASS_WITH_WARNING" if minimal_pair(cp) else "PASS", "secondary_called": True,
                 "secondary_class": ca.classification}
        else:
            u = {"outcome": "NG_REGEN", "secondary_called": True, "secondary_class": ca.classification}
        # --- 単純OR(安全条件なし): Secondaryが should_pass(厳格ラベル外・数値否定・length/QA gate無視)なら PASS
        o = {"outcome": "PASS" if (ca is not None and ca.should_pass) else "NG_REGEN", "secondary_called": True,
             "secondary_class": ca.classification if ca else None}
    row["unified_safe"], row["unified_simple_or"] = u, o
    if it["azure_pl_text"] is not None and az_text is not None:
        cpl = cl["azure_PL_stored"]
        row["pl_vs_nopl"] = {"id": it["id"], "pl_class": cpl.classification if cpl else None,
                             "nopl_class": ca.classification if ca else None,
                             "pl_strict": strict_pass(cpl), "nopl_strict": strict_pass(ca),
                             "texts_identical": it["azure_pl_text"].strip() == az_text.strip()}
    return row


def mutations(canon):
    out = []
    m = re.search(r"\b(\d+)\b(?![.,]\d)", canon)
    if m:
        v = int(m.group(1))
        out.append(("number", canon[:m.start()] + str(v + 1 if v < 1900 else v - 1) + canon[m.end():]))
    if re.search(r"\b(did|does|do|was|were|is|are) not\b", canon):
        out.append(("negation_drop", re.sub(r"\b(did|does|do|was|were|is|are) not\b", lambda m_: m_.group(1), canon, count=1)))
    elif re.search(r"\b(is|was|did|does|are|were)\b", canon):
        out.append(("negation_add", re.sub(r"\b(is|was|did|does|are|were)\b", lambda m_: m_.group(1) + " not", canon, count=1)))
    m = re.search(r"\b([a-z]{4,}[^su])s\b", canon)
    if m:
        out.append(("plural_drop", canon[:m.start()] + m.group(1) + canon[m.end():]))
    m = re.search(r"\b([a-z]{3,})ed\b", canon)
    if m:
        out.append(("tense_ed_drop", canon[:m.start()] + m.group(1) + canon[m.end():]))
    if " the " in canon:
        out.append(("article_drop", canon.replace(" the ", " ", 1)))
    words = [(mm.start(), mm.end()) for mm in re.finditer(r"\b[a-z]{6,}\b", canon)]
    if len(words) >= 3:
        s, e = words[2]
        out.append(("content_sub_unrelated", canon[:s] + "tea" + canon[e:]))
        s, e = words[1]
        out.append(("content_omit", canon[:s] + canon[e:]))
    m = re.search(r"(?<=[a-z,] )([A-Z][a-z]{3,})\b", canon)
    if m:
        out.append(("entity_sub", canon[:m.start()] + "Brown" + canon[m.end():]))
    return out


def mutation_test(items):
    """真の誤読注入(合成): 音声が誤読Yを発話した場合、Primaryは(完全に)Yを転写する。Secondaryが最悪ケースで
    「原稿に寄せて補正」して原稿そのままを返す(ASRのLM prior)と仮定したとき、単純ORと安全条件案のどちらが誤PASSを通すか。
    ※Validatorの許容度とゲートの効果を測る合成試験であり、実ASRの補正率の測定ではない。"""
    rows = []
    for it in items:
        canon = it["canonical"]
        if not canon:
            continue
        for mt, y in mutations(canon):
            if y == canon:
                continue
            cp = cls(canon, y, it["segment_id"])
            if cp.should_pass:
                r = {"primary": "PASS(両フロー共通の誤PASS)", "or": "PASS", "safe": "PASS"}
            else:
                g = gate_reason({**it, "primary_text": y, "length_ok": True, "repetition_flagged": False, "disfluency_flagged": False}, cp)
                r = {"primary": "NG", "or": "PASS(誤PASS)",
                     "safe": ("BLOCKED(" + g + ")") if g else ("PASS_WITH_WARNING" if minimal_pair(cp) else "PASS(誤PASS)")}
            rows.append({"id": it["id"], "mutation": mt, "primary_class": cp.classification, **r})
    agg = collections.defaultdict(collections.Counter)
    for r in rows:
        a = agg[r["mutation"]]
        a["n"] += 1
        if r["primary"].startswith("PASS"):
            a["primary_false_pass_both_flows"] += 1
        else:
            a["primary_NG"] += 1
            if r["or"].startswith("PASS"):
                a["or_false_pass_via_autocorrected_secondary"] += 1
            if r["safe"].startswith("BLOCKED"):
                a["safe_blocked"] += 1
            elif r["safe"] == "PASS_WITH_WARNING":
                a["safe_warning_to_final_listening"] += 1
            else:
                a["safe_residual_false_pass"] += 1
    return rows, {k: dict(v) for k, v in agg.items()}


def hr_offline():
    """HR queue 67行(全件、課金0): 保存済みAzure(PL付き)転写を代理に、統一案(厳格ラベル)で救済できた/誤って通した数。"""
    hr = [json.loads(l) for l in open(os.path.join(ROOT, "er006_output", "audio_retry_cascade_prod_01", "human_review_queue.jsonl"), encoding="utf-8")]
    c = collections.Counter()
    ex = []
    for r in hr:
        steps = r["steps"]
        p1 = next(s for s in steps if s["step"] == "primary_1")
        sec = next((s for s in steps if s["step"] == "secondary_1"), None)
        forced = next((s for s in steps if s["step"] == "secondary_forced"), None)
        canon = r["canonical_text"]
        if forced:
            c["forced_secondary rows(Primary PASS, Azure PL NG)"] += 1
            c["  -> unified: Primary PASSで完了(Secondaryを呼ばない)"] += 1
            continue
        cp = cls(canon, p1["text"], "x")
        cs = cls(canon, sec["text"], "x") if sec and sec.get("text") is not None else None
        c["cascade rows(Primary NG, 4段とも不救済でHR)"] += 1
        if numneg(cp):
            c["  gated(numeric/negation) -> Secondary不呼出"] += 1
        elif cs is not None and strict_pass(cs):
            c["  unified strict Secondary PASS(救済)"] += 1
            ex.append(("strict_pass", canon[:80], sec["text"][:80]))
        elif cs is not None and cs.should_pass:
            c["  unified: Secondary lenient only(厳格ラベル外 -> NG)"] += 1
        else:
            c["  unified: Secondary NG(再生成へ)"] += 1
    return dict(c), ex


# ---------------------------------------------------------------- QCD射影(call単位)
def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (round(max(0, c - h), 3), round(min(1, c + h), 3))


def qcd_projection(rows):
    """er056 replay_results_01.json の narrative5 160 call(読込のみ)へ、測定したカテゴリ別Secondary救済率を適用した期待値。"""
    rp = json.load(open(os.path.join(P56, "replay_results_01.json"), encoding="utf-8"))
    nar = [c for c in rp["per_call"] if c["role"] != "OTHER"]
    qc = json.load(open(os.path.join(P56, "qcd_model_01.json"), encoding="utf-8"))["unit_costs"]
    ng_rows = [r for r in rows if r["group"] == "PRIMARY_NG"]
    cat_stats = collections.defaultdict(lambda: [0, 0])
    for r in ng_rows:
        cat_stats[r["primary_category"]][1] += 1
        if r["unified_safe"]["outcome"].startswith("PASS"):
            cat_stats[r["primary_category"]][0] += 1
    k_all = sum(v[0] for v in cat_stats.values())
    n_all = sum(v[1] for v in cat_stats.values())
    pooled = k_all / n_all if n_all else 0.0

    def rate(cat, scenario):
        if cat in ("NUM_OR_NEGATION", "PASS"):  # 数値/否定、およびASR以外のGate(length/QA)は救済しない
            return 0.0
        k, n = cat_stats.get(cat, [0, 0])
        if n < 3:
            k, n = k_all, n_all
        lo, hi = wilson(k, n)
        return {"low": lo, "mid": (k / n if n else 0.0), "high": hi}[scenario]

    p_regen = {2: 13 / 22, 3: 2 / 8}
    res = {}
    for sc in ("low", "mid", "high"):
        tts_total = done3 = extrap = hr_pre_lr = azure_calls = 0.0
        for c in nar:
            v = c["verified_at_tts_index"]
            alive = 1.0
            n_tts = 0.0
            for k in range(1, 4):
                n_tts += alive
                observed = (k - 1) < len(c["classes"]) and c["attempt_routes"][k - 1] == "std"
                if observed:
                    if v == k:
                        done3 += alive
                        alive = 0.0
                        break
                    cat = c["attempt_categories"][k - 1]
                    r = rate(cat, sc)
                    if cat not in ("NUM_OR_NEGATION", "PASS"):
                        azure_calls += alive
                    done3 += alive * r
                    alive *= (1 - r)
                else:  # 旧フローがここで打切り(HR/LR/fallback) -> 同一Prompt再生成の通過率を実測の条件付き確率で外挿
                    pr = p_regen.get(k, 0.25)
                    extrap += alive
                    done3 += alive * pr
                    alive *= (1 - pr)
                if alive <= 1e-9:
                    break
            tts_total += n_tts
            hr_pre_lr += alive
        n = len(nar)
        res[sc] = {"mean_tts_per_call": round(tts_total / n, 3), "complete_within_3tts": round(done3 / n, 4),
                   "to_local_rewrite_or_HR_rate": round(hr_pre_lr / n, 4),
                   "extrapolated_attempt_share_of_calls": round(extrap / n, 3),
                   "azure_secondary_calls_per_call": round(azure_calls / n, 3)}
    old_tts = sum(c["n_tts_in_call"] for c in nar) / len(nar)
    old_done = sum(1 for c in nar if c["verified_at_tts_index"] is not None) / len(nar)
    old_cascade = sum(1 for c in nar for ci in c["cascade_invoked"] if ci)
    azure_s = 40.0 * AZURE_JPY_PER_SEC
    old = {"n_calls": len(nar), "mean_tts_per_call(fallback含む)": round(old_tts, 3),
           "complete_within_call(LR前、fallback含む)": round(old_done, 4), "cascade_invoked_attempts": old_cascade,
           "est_cascade_asr_jpy_per_call": round(old_cascade * (2 * azure_s + qc["openai_asr_jpy_per_call"]) / len(nar), 3)}
    for sc in res:
        res[sc]["est_secondary_jpy_per_call"] = round(res[sc]["azure_secondary_calls_per_call"] * azure_s, 3)
        res[sc]["est_tts_jpy_per_call"] = round(res[sc]["mean_tts_per_call"] * qc["tts_flash_lite_batch_jpy_per_call"], 3)
    return {"category_rescue_measured": {k: {"rescued": v[0], "n": v[1]} for k, v in cat_stats.items()},
            "pooled_rescue": round(pooled, 3), "old_flow_observed": old, "new_flow_expected": res,
            "assumptions": ["Secondary救済率=本Trial実測(カテゴリ別、n<3は全体平均)の下限/中央/上限(Wilson 95%)",
                            "旧フローが打切った後の再生成通過率は実測(narrative5: 2回目13/22, 3回目2/8)で外挿",
                            "Azure音声長は平均40秒と仮定(単価0.0444円/秒)", "tts単価0.135円/call(qcd_model_01)",
                            "Local Rewrite以降は未モデル化"]}


# ---------------------------------------------------------------- 集計
def cmd_analyze(items, mock):
    sfx = "_mock" if mock else ""
    az = json.load(open(os.path.join(OUT, "azure_nopl_C_01%s.json" % sfx), encoding="utf-8"))
    cp_ = os.path.join(OUT, "local_asr_cache_C_01.json")
    cache = json.load(open(cp_, encoding="utf-8")) if os.path.exists(cp_) else {}
    rows = [evaluate_item(it, (az.get(it["id"]) or {}).get("text"), cache) for it in items]
    for r in rows:
        r["azure_elapsed_sec"] = (az.get(r["id"]) or {}).get("elapsed_sec")
    agg = collections.defaultdict(collections.Counter)
    for r in rows:
        g = r["group"]
        agg[g]["n"] += 1
        agg[g]["label_" + r["proxy_label"]] += 1
        for fl in ("unified_safe", "unified_simple_or"):
            o = r[fl]["outcome"]
            agg[g][f"{fl}:{o}"] += 1
        agg[g]["current:" + r["current_flow"]["outcome"]] += 1
    rows_all = rows
    rows = [r for r in rows if not r["proxy_label"].startswith("EXCLUDED")]
    ng_like = [r for r in rows if r["group"] in ("PRIMARY_NG", "HR_QUEUE")]
    m = {}
    for fl in ("unified_safe", "unified_simple_or"):
        m[fl] = {"n_primary_ng_items": len(ng_like),
                 "false_pass_on_TRUE_ERROR_SUSPECT": sum(1 for r in ng_like if r[fl]["outcome"].startswith("PASS") and r["proxy_label"] == "TRUE_ERROR_SUSPECT"),
                 "pass_on_AMBIGUOUS(要試聴)": sum(1 for r in ng_like if r[fl]["outcome"].startswith("PASS") and r["proxy_label"] == "AMBIGUOUS"),
                 "rescued_FALSE_NG_LIKELY": sum(1 for r in ng_like if r[fl]["outcome"].startswith("PASS") and r["proxy_label"] == "FALSE_NG_LIKELY"),
                 "unnecessary_NG_FALSE_NG_LIKELY": sum(1 for r in ng_like if (not r[fl]["outcome"].startswith("PASS")) and r["proxy_label"] == "FALSE_NG_LIKELY"),
                 "pass_with_warning": sum(1 for r in ng_like if r[fl]["outcome"] == "PASS_WITH_WARNING"),
                 "secondary_not_called_gate": sum(1 for r in ng_like if r[fl].get("gate"))}
    m["current_flow"] = {"n_primary_ng_items": len(ng_like),
                         "unnecessary_NG_FALSE_NG_LIKELY": sum(1 for r in ng_like if r["proxy_label"] == "FALSE_NG_LIKELY"),
                         "false_pass": 0, "rescued": 0,
                         "note": "標本はPrimary NG(現行で不合格/HR)に限定して選定しているため、現行の救済は定義上0"}
    forced = [r for r in rows if r["group"] == "HR_QUEUE_FORCED"]
    ctrl = [r for r in rows if r["group"] == "CONTROL_PRIMARY_PASS"]
    m["forced_secondary_items"] = {"n": len(forced), "azure_noPL_strict_pass": sum(1 for r in forced if (r["systems"]["azure_noPL"] or {}).get("strict_pass")),
                                   "labels": dict(collections.Counter(r["proxy_label"] for r in forced))}
    m["control_primary_pass"] = {"n": len(ctrl), "azure_noPL_strict_pass": sum(1 for r in ctrl if (r["systems"]["azure_noPL"] or {}).get("strict_pass")),
                                 "azure_noPL_ng(Secondary単独なら偽NG)": sum(1 for r in ctrl if r["systems"]["azure_noPL"] and not r["systems"]["azure_noPL"]["strict_pass"]),
                                 "labels": dict(collections.Counter(r["proxy_label"] for r in ctrl))}
    pl = [r["pl_vs_nopl"] for r in rows if "pl_vs_nopl" in r]
    m["phrase_list_effect"] = {"n_compared": len(pl), "identical_texts": sum(1 for p in pl if p["texts_identical"]),
                               "pl_strict_pass": sum(1 for p in pl if p["pl_strict"]),
                               "nopl_strict_pass": sum(1 for p in pl if p["nopl_strict"]), "detail": pl}
    mrows, magg = mutation_test(items)
    hr_off, hr_ex = hr_offline()
    qcd = qcd_projection(rows)
    azs = [v["elapsed_sec"] for v in az.values() if v.get("elapsed_sec")]
    out = {"mock": mock, "n_items": len(items), "group_aggregate": {k: dict(v) for k, v in agg.items()}, "metrics": m,
           "mutation_aggregate": magg, "hr_queue_offline_67rows": hr_off, "hr_queue_offline_examples": hr_ex[:6],
           "qcd_projection": qcd, "azure_elapsed_mean_sec": round(sum(azs) / len(azs), 1) if azs else None,
           "excluded_items": [{"id": r["id"], "reason": r.get("excluded_reason")} for r in rows_all if r["proxy_label"].startswith("EXCLUDED")],
           "rows": rows_all, "mutation_rows": mrows}
    json.dump(out, open(os.path.join(OUT, "trial_c_results_01%s.json" % sfx), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k not in ("rows", "mutation_rows")}, ensure_ascii=False, indent=1)[:7000])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["estimate", "local", "dry", "real", "analyze"])
    ap.add_argument("--approved-budget-jpy", type=float, default=None)
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    sp = os.path.join(OUT, "sample_C_01.json")
    items = json.load(open(sp, encoding="utf-8")) if os.path.exists(sp) else None
    if items is None or a.cmd == "estimate":
        items = build_sample()
        json.dump(items, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if a.cmd == "estimate":
        e = estimate(items)
        json.dump(e, open(os.path.join(OUT, "estimate_C_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(json.dumps(e, ensure_ascii=False, indent=1))
        for i in items:
            print(i["id"], i["group"], round(i["dur"], 1), i["segment_id"], i["primary_category"])
    elif a.cmd == "local":
        cmd_local(items)
    elif a.cmd == "dry":
        cmd_azure(items, True, 0)
        cmd_analyze(items, True)
    elif a.cmd == "real":
        if a.approved_budget_jpy is None or a.approved_budget_jpy > BUDGET_JPY_HARD or a.approved_budget_jpy <= 0:
            sys.exit("--approved-budget-jpy 40 が必須(上限40円)")
        e = estimate(items)
        if e["estimated_azure_jpy"] > a.approved_budget_jpy:
            sys.exit("見積 %.2f円 > 承認予算。STOP" % e["estimated_azure_jpy"])
        cmd_azure(items, False, a.approved_budget_jpy)
    elif a.cmd == "analyze":
        cmd_analyze(items, a.mock)


if __name__ == "__main__":
    main()
