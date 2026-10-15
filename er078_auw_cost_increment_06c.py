# AUW 委任_06c (i): 「Primary NGのたびにAzure 1回」による増分費用の試算(API 0、offline)。
# 入力: er011_output/attempt_history.jsonl(test/wiring系themeの行は除外)。出力: JSON(標準出力 + --out)。
# 単価: Azure 0.0444円/秒(= $1/h x 160 JPY/USD / 3600、RUNTIME_EVIDENCE_06 §12)。
import argparse
import collections
import json
import math
import re

TEST = re.compile(r"^(pool_test_theme|unittest_scratch_theme|wiring_theme.*|p1|rerun_01|evidence_theme_01|meta|audio)$")
AZ_JPY_PER_SEC = 0.0444


def wilson_upper(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c + m) / d


def role(seg):
    s = seg or ""
    if s.startswith("full_story") or (s.startswith("point_") and "heading" not in s):
        return "body"
    if s == "in_one_line":
        return "in_one_line"
    if s.startswith("kp") or "key_phrase" in s:
        return "kp"
    if s in ("preview", "topic_intro") or s.startswith("comment"):
        return "short_narration"
    return "other"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--history", default="er011_output/attempt_history.jsonl")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(a.history, encoding="utf-8") if l.strip()]
    st = collections.defaultdict(collections.Counter)
    calls = collections.Counter()
    tts_att = collections.Counter()  # tts_attempts_this_call は全PROCEED行にある(attempts_detailは近年の行のみ)
    for r in rows:
        if r.get("action") != "PROCEED" or r.get("language") != "en" or TEST.match(r.get("theme_id") or ""):
            continue
        ro = role(r.get("segment_id"))
        calls[ro] += 1
        tts_att[ro] += int(r.get("tts_attempts_this_call") or 0)
        for d in r.get("attempts_detail") or []:
            c = d.get("audio_classification")
            if not c:
                continue
            st[ro]["attempts"] += 1
            if c == "TRUE_CONTENT_MISMATCH":
                st[ro]["tcm"] += 1
            if c == "ASR_VALIDATION_UNCERTAIN":
                st[ro]["unc"] += 1
    out = {"source": a.history, "filter": "action=PROCEED, language=en, test/wiring theme excluded", "by_role": {}}
    for ro, c in st.items():
        n = c["attempts"]
        out["by_role"][ro] = {"calls": calls[ro], "attempts": n, "attempts_per_call": round(tts_att[ro] / calls[ro], 3) if calls[ro] else None,
                              "attempts_with_detail_per_call": round(n / calls[ro], 3) if calls[ro] else None,
                              "tcm": c["tcm"], "tcm_rate": round(c["tcm"] / n, 4), "tcm_rate_95_upper": round(wilson_upper(c["tcm"], n), 4),
                              "uncertain": c["unc"], "uncertain_rate": round(c["unc"] / n, 4)}
    b = out["by_role"]["body"]
    apc, p, pu, pu_ng = b["attempts_per_call"], b["tcm_rate"], b["tcm_rate_95_upper"], (b["tcm"] + b["uncertain"]) / b["attempts"]
    res = {}
    for sec in (40, 60):
        per_call = round(sec * AZ_JPY_PER_SEC, 2)
        # 1 part の 1 Primary NG = Azure 1回(wav秒数分)。Adv=本文3 part(減速なし)、Std(A2)=本文3 part x 減速前後の2判定(最大2回)。
        adv = 3 * apc * p * per_call
        std = 3 * apc * p * per_call * 2
        res[f"{sec}s"] = {"azure_jpy_per_call": per_call,
                          "central_adv": round(adv, 2), "central_std": round(std, 2), "central_set": round(adv + std, 2),
                          "upper95_set": round((3 * apc * pu * per_call) * 3, 2),
                          "pessimistic_all_NG_rate_set(TCM+UNC全てを増分と見なす)": round((3 * apc * pu_ng * per_call) * 3, 2),
                          "worst_every_part_NG_once_set(6 part, Std減速後も)": round(per_call * 3 + per_call * 3 * 2, 2)}
    out["body_inputs"] = {"attempts_per_call": apc, "tcm_rate": p, "tcm_rate_95_upper": pu, "tcm_plus_uncertain_rate": round(pu_ng, 4)}
    out["increment_jpy_per_article_set"] = res
    out["notes"] = ["増分は TRUE_CONTENT_MISMATCH(旧=Secondary不呼出→新=Secondary 1回)に由来。UNCERTAIN は旧Cascadeでも Azure を呼んでいた(旧 最大2回→新1回で削減側)。",
                    "『記事セット』= Advanced(B1B) + Standard(A2) の本文3 part。Std は減速前後の2判定で最大2回(減速後は同一wavでも別sha256)。",
                    "KP(英語phrase 約2秒)は Azure 0.09円/呼出 x TCM率5.6% x 5本 = 約0.03円/level で無視できる。"]
    s = json.dumps(out, ensure_ascii=False, indent=2)
    print(s)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(s)


if __name__ == "__main__":
    main()
