"""Self-verification of sync/<out>/*.sentences.json (DEV, API 0).
Checks: (1) monotonic / no overlap / inside audio length (2) script<->ASR token match (3) speech presence inside each sentence & silence in gaps (RMS, independent of the aligner)
(4) chunk-gap consistency (exact chunk boundaries known from chunk_tts_assembly) (5) cross-model boundary difference (medium vs small, if small ASR exists)
(6) offset check: part mp3 position inside the shipped full-episode mp3 (cross-correlation) (7) outlier list (>0.5 s, >1.5 s).
usage: sync_verify_01.py <article_key> [out_json]"""
import sys, os, json, glob
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from sync_common_01 import *
from asr_raw_01 import load_audio
import sync_build_01 as B

BASE = 'docs/research/END-USER-LISTENING-PAGE-PROTOTYPE-01/sync'


def frames_db(a):
    n = len(a) // B.HOP
    rms = np.sqrt((a[:n * B.HOP].reshape(n, B.HOP) ** 2).mean(1))
    return 20 * np.log10(rms + 1e-9)


def xcorr_offset(full, seg, expected_s, sr=16000, search_s=1.0):
    """Return best lag (s) of seg inside full near expected_s, and normalized correlation peak."""
    lo = max(0, int((expected_s - search_s) * sr))
    hi = min(len(full), int((expected_s + search_s) * sr) + len(seg))
    x = full[lo:hi]
    n = len(x) + len(seg)
    nf = 1 << (n - 1).bit_length()
    X = np.fft.rfft(x, nf)
    Y = np.fft.rfft(seg[::-1], nf)
    c = np.fft.irfft(X * Y, nf)[len(seg) - 1:len(x)]
    # normalize by local energy
    e = np.sqrt(np.convolve(x ** 2, np.ones(len(seg)), 'valid')[:len(c)] + 1e-12) * np.sqrt((seg ** 2).sum() + 1e-12)
    cn = c[:len(e)] / e
    k = int(np.argmax(cn))
    return (lo + k) / sr, float(cn[k])


def main():
    key = sys.argv[1]
    a, units = load_article(key)
    outdir = os.path.join(ROOT, BASE, a['out'])
    full = None
    rep = dict(article=key, parts=[], summary={})
    all_bound = []
    n_sent = 0
    n_viol = 0
    outl05, outl15, unsnapped = [], [], []
    xm_diffs = []
    chunk_err_all = []
    wide_l = []
    for u in units:
        p = os.path.join(outdir, u['key'] + '.sentences.json')
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding='utf-8'))
        S = d['sentences']
        au = load_audio(os.path.join(ROOT, d['audio']))
        dur = len(au) / 16000
        db = frames_db(au)
        pr = dict(part=u['key'], sentences=len(S), audio_s=round(dur, 3), seq_ratio=d['seq_ratio'], token_match=d['token_match'], issues=[])
        # (1) structure
        for i, s in enumerate(S):
            if not (0 <= s['start'] < s['end'] <= dur + 0.02):
                pr['issues'].append('range:%s' % s['sentence_id'])
            if i and s['start'] < S[i - 1]['end'] - 1e-6:
                pr['issues'].append('overlap:%s' % s['sentence_id'])
        if abs(dur - u['duration']) > 0.15:
            pr['issues'].append('mp3_vs_timeline_dur:%.3f/%.3f' % (dur, u['duration']))
        # (3) speech presence
        frac_in, frac_gap = [], []
        for i, s in enumerate(S):
            a0, a1 = int((s['start'] + 0.05) * 100), int((s['end'] - 0.05) * 100)
            if a1 > a0:
                seg = db[a0:a1]
                frac_in.append(float((seg > B.SIL_DB).mean()))
            if i:
                g0, g1 = int(S[i - 1]['end'] * 100), int(s['start'] * 100)
                if g1 - g0 >= 3:
                    frac_gap.append(float((db[g0 + 1:g1 - 1] > B.SIL_DB).mean()) if g1 - g0 > 2 else 0.0)
                all_bound.append(s['start'] - S[i - 1]['end'])
        pr['speech_frac_in_sentence_min'] = round(min(frac_in), 3) if frac_in else None
        pr['speech_frac_in_sentence_mean'] = round(float(np.mean(frac_in)), 3) if frac_in else None
        pr['speech_frac_in_gap_max'] = round(max(frac_gap), 3) if frac_gap else None
        # (4) chunk gap consistency
        for (g0, g1) in u['gaps']:
            before = [s for s in S if s['end'] <= g0 + 0.35]
            after = [s for s in S if s['start'] >= g1 - 0.35]
            ok = bool(before) and bool(after) and before[-1]['chunk_id'] != after[0]['chunk_id'] and before[-1]['end'] <= g0 + 0.35 and after[0]['start'] >= g1 - 0.35
            # the sentence straddling the gap would violate
            straddle = [s for s in S if s['start'] < g0 - 0.05 and s['end'] > g1 + 0.05]
            if straddle:
                ok = False
            if not ok:
                pr['issues'].append('chunk_gap_conflict:%.2f-%.2f' % (g0, g1))
        # exact ground truth: the 0.2 s pad inserted between chunks must lie inside [end of last sentence of chunk k, start of first sentence of chunk k+1]
        gap_err = []
        for (g0, g1) in u['gaps']:
            before = [s for s in S if s['end'] <= g1]
            after = [s for s in S if s['start'] >= g0]
            if before and after:
                gap_err.append(round(max(before[-1]['end'] - g0, g1 - after[0]['start'], 0.0), 3))
        pr['chunk_gap_containment_error_s'] = gap_err   # 0.0 = the known exact gap lies fully in the silence between the two sentences
        chunk_err_all.extend(gap_err)
        pr['chunk_gaps_checked'] = len(u['gaps'])
        # (5)(7) outliers vs raw ASR and cross-model
        for s in S:
            ds, de = abs(s['start'] - s['asr_raw']['start']), abs(s['end'] - s['asr_raw']['end'])
            if max(ds, de) > 0.5:
                outl05.append((u['key'], s['sentence_id'], round(ds, 2), round(de, 2)))
            if max(ds, de) > 1.5:
                outl15.append((u['key'], s['sentence_id'], round(ds, 2), round(de, 2)))
            if s['source'].endswith('silence_snap_wide'):
                wide_l.append((u['key'], s['sentence_id'], s['confidence']))
            elif not s['source'].endswith('silence_snap'):
                unsnapped.append((u['key'], s['sentence_id']))
        sm = os.path.join(ROOT, BASE, '_asr_raw', '%s__%s__small.json' % (key, u['key']))
        if os.path.exists(sm):
            # independent second ASR model (small) through the same pipeline: compare RAW (before silence snap) and FINAL (after snap) boundaries
            r2 = B.build_unit(key, u, 'small', B.silence_runs(au), dur)
            for s1, s2 in zip(S, r2['sentences']):
                raw = (round(abs(s2['asr_raw']['start'] - s1['asr_raw']['start']), 3), round(abs(s2['asr_raw']['end'] - s1['asr_raw']['end']), 3))
                fin = (round(abs(s2['start'] - s1['start']), 3), round(abs(s2['end'] - s1['end']), 3))
                xm_diffs.append((u['key'], s1['sentence_id'], raw, fin[0], fin[1]))
        # (6) offset in full episode
        if full is None:
            full = load_audio(os.path.join(ROOT, a['mp3dir'], a['full_mp3']))
        lag, cn = xcorr_offset(full, au, u['start'])
        pr['episode_offset_check'] = dict(expected_s=u['start'], found_s=round(lag, 3), delta_s=round(lag - u['start'], 3), corr=round(cn, 3))
        if abs(lag - u['start']) > 0.1 or cn < 0.5:
            pr['issues'].append('episode_offset:%.3f corr %.2f' % (lag - u['start'], cn))
        n_sent += len(S)
        n_viol += len(pr['issues'])
        rep['parts'].append(pr)
    gaps = np.array(all_bound) if all_bound else np.array([0.0])
    rep['summary'] = dict(sentences=n_sent, parts=len(rep['parts']), issue_count=n_viol,
                          inter_sentence_gap_s=dict(min=round(float(gaps.min()), 3), median=round(float(np.median(gaps)), 3), max=round(float(gaps.max()), 3)),
                          raw_vs_snapped_outliers_gt_0_5s=outl05, raw_vs_snapped_outliers_gt_1_5s=outl15, not_silence_snapped=unsnapped, snapped_wide_or_short_pause_lower_confidence=wide_l,
                          cross_model_small_vs_medium_raw_gt_0_5s=[x for x in xm_diffs if max(x[2]) > 0.5],
                          cross_model_small_vs_medium_raw_max=(max(max(x[2]) for x in xm_diffs) if xm_diffs else None),
                          cross_model_small_vs_final_snapped_max=(max(max(x[3], x[4]) for x in xm_diffs) if xm_diffs else None),
                          cross_model_small_vs_final_snapped_median=(round(float(np.median([max(x[3], x[4]) for x in xm_diffs])), 3) if xm_diffs else None),
                          chunk_gap_containment_error_s=dict(n=len(chunk_err_all), max=(max(chunk_err_all) if chunk_err_all else None)),
                          cross_model_compared=len(xm_diffs))
    outp = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, BASE, a['out'], 'VERIFY.json')
    json.dump(rep, open(outp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(rep['summary'], ensure_ascii=False, indent=1)[:3000])
    for pr in rep['parts']:
        print(pr['part'], pr['sentences'], 'ratio', pr['seq_ratio'], 'match', pr['token_match'], 'in-speech min/mean', pr['speech_frac_in_sentence_min'], pr['speech_frac_in_sentence_mean'],
              'gap max', pr['speech_frac_in_gap_max'], 'offset', pr['episode_offset_check']['delta_s'], pr['episode_offset_check']['corr'], 'issues', pr['issues'])


if __name__ == '__main__':
    main()
