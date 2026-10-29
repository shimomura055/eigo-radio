"""Option (d) probe: sentence boundaries from audio silence + script character proportion ONLY (no ASR at all).
Compares against the ASR-based final boundaries (sync/*/ *.sentences.json). DEV, API 0.
usage: silence_only_probe_01.py <article_key>"""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from sync_common_01 import *
import sync_build_01 as B
from asr_raw_01 import load_audio

def pick(silr, dur, weights):
    """silr: merged silence runs; weights: per-sentence char weights. Return list of N-1 chosen silence runs (monotonic) by DP on speech-time fraction."""
    N = len(weights)
    if N == 1:
        return []
    inner = [(s, e) for (s, e) in silr if s > 0.15 and e < dur - 0.15 and e - s >= 0.18]
    if len(inner) < N - 1:
        return None
    # speech-time before each silence
    sil_before = np.cumsum([0.0] + [e - s for s, e in inner])[:-1]
    lead = sum(e - s for s, e in silr if s <= 0.05)
    trail = sum(e - s for s, e in silr if e >= dur - 0.05)
    total_speech = dur - sum(e - s for s, e in silr)
    pos = [(s - sil_before[i] - lead) / max(total_speech, 1e-6) for i, (s, e) in enumerate(inner)]
    cum = np.cumsum(weights)[:-1] / float(sum(weights))
    # DP: choose indices i_1<...<i_{N-1}
    M, K = len(inner), N - 1
    INF = 1e9
    dp = np.full((K, M), INF); bk = np.zeros((K, M), dtype=int)
    for i in range(M):
        dp[0][i] = abs(pos[i] - cum[0])
    for k in range(1, K):
        best, bi = INF, -1
        for i in range(M):
            if i > 0 and dp[k - 1][i - 1] < best:
                best, bi = dp[k - 1][i - 1], i - 1
            dp[k][i] = best + abs(pos[i] - cum[k]) if bi >= 0 else INF
            bk[k][i] = bi
    i = int(np.argmin(dp[K - 1])); idx = [i]
    for k in range(K - 1, 0, -1):
        i = bk[k][i]; idx.append(i)
    return [inner[j] for j in reversed(idx)]

key = sys.argv[1]
a, units = load_article(key)
tot = ok = 0; worst = 0.0; bad = []
for u in units:
    p = os.path.join(ROOT, 'docs/research/END-USER-LISTENING-PAGE-PROTOTYPE-01/sync', a['out'], u['key'] + '.sentences.json')
    if not os.path.exists(p):
        continue
    d = json.load(open(p, encoding='utf-8')); S = d['sentences']
    au = load_audio(os.path.join(ROOT, u['mp3'])); silr = B.silence_runs(au)
    w = [len(B.ja_chars(s['text'])) if u['lang'] == 'ja' else max(1, len(s['text'])) for s in S]
    ch = pick(silr, len(au) / 16000, w)
    if ch is None:
        bad.append((u['key'], 'too_few_silences')); continue
    for k, (s, e) in enumerate(ch):
        tot += 1
        err = max(abs(s - S[k]['end']), abs(e - S[k + 1]['start']))
        worst = max(worst, err)
        if err <= 0.05: ok += 1
        else: bad.append((u['key'], S[k]['sentence_id'], round(err, 2)))
print(key, 'boundaries', tot, 'within 50ms of ASR-based', ok, 'worst', round(worst, 2), 'misses', bad)
