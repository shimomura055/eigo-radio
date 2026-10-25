"""FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01 委任_02: 無音(統合後)を台本の語境界へ単調DPで概算対応付け(ASR語タイムスタンプ無しのため推定)。
推定位置 e_i = 発話時間(無音除外)に対する比率 x 全語の重み(文字数+2)。語境界候補は『句読点直後』を優先(罰0)、非句読点境界は罰3語。
出力: 各ポーズの(開始秒, 長さ, 直前語, 直後語, 句読点境界か)。分類 (b)句読点自然ポーズ / (c)文中(非句読点境界)ポーズ。精度限界: ±2〜3語。
使い方: py -I yfb_pause_align_01.py --measure <json> --text-file <txt> --out <json>
"""
import argparse, json, re, sys
sys.path.insert(0, __file__.rsplit("tools", 1)[0] + "tools")
from yfb_pause_stats_01 import merge


def align(meas, text, blip_ms=120):
    tot = meas["duration_s"]
    inner = [p for p in meas["pauses"] if p["start_s"] >= 0.05 and p["end_s"] < tot - 0.05]
    m = merge(inner, blip_ms)
    words = text.split()
    wt = [len(re.sub(r"\W", "", w)) + 2 for w in words]
    W = sum(wt)
    lead = meas["leading_silence_ms"] / 1000
    trail = meas["trailing_silence_ms"] / 1000
    act = tot - lead - trail - sum(p["dur_ms"] for p in m) / 1000
    cum = [sum(wt[: i + 1]) for i in range(len(words))]
    cand = list(range(1, len(words)))            # 境界k = words[k-1] と words[k] の間
    punct = {k for k in cand if re.search(r"[.?!,;:]$", words[k - 1])}
    est, acc = [], 0.0
    for p in m:
        sp = p["start_s"] - lead - acc
        acc += p["dur_ms"] / 1000
        est.append(W * sp / act if act > 0 else 0)
    def cost(i, k):
        return abs(cum[k - 1] / W * W - est[i]) / 3.0 * 0.5 + (0 if k in punct else 3)
    n = len(m)
    INF = 1e18
    dp = [[INF] * (len(cand) + 1) for _ in range(n + 1)]
    bp = [[0] * (len(cand) + 1) for _ in range(n + 1)]
    dp[0] = [0.0] * (len(cand) + 1)
    for i in range(1, n + 1):
        best, bj = INF, 0
        for j in range(1, len(cand) + 1):
            if dp[i - 1][j - 1] < best:
                best, bj = dp[i - 1][j - 1], j - 1
            k = cand[j - 1]
            dp[i][j] = best + cost(i - 1, k)
            bp[i][j] = bj
    j = min(range(1, len(cand) + 1), key=lambda t: dp[n][t]) if n else 0
    res = []
    for i in range(n, 0, -1):
        k = cand[j - 1]
        p = m[i - 1]
        res.append({"start_s": p["start_s"], "dur_ms": p["dur_ms"], "merged_blips": p.get("merged", 1) - 1,
                    "after_word": words[k - 1], "before_word": words[k], "word_index": k,
                    "at_punctuation": k in punct, "class": "b_punct_natural" if k in punct else "c_mid_clause"})
        j = bp[i][j]
    res.reverse()
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--measure", required=True)
    ap.add_argument("--text-file", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    r = align(json.load(open(a.measure, encoding="utf8")), open(a.text_file, encoding="utf8").read().strip())
    json.dump(r, open(a.out, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    c = sum(1 for x in r if not x["at_punctuation"])
    print(a.out, "pauses", len(r), "mid_clause", c, "mid>=500ms", sum(1 for x in r if not x["at_punctuation"] and x["dur_ms"] >= 500))
