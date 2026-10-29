"""Build per-part 1-sentence sync data: sync/<out>/<part>.sentences.json (DEV, API 0).
Method: script (TTS input) deterministic sentence split -> local faster-whisper word timestamps on the SHIPPED segment mp3
-> difflib token alignment (script<->ASR) -> boundary snap to measured silence (RMS < -40 dBFS) -> self-verification (sync_verify_01.py).
usage: sync_build_01.py <article_key> [model=medium] [langs=en]"""
import sys, os, re, json, difflib
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from sync_common_01 import *
from asr_raw_01 import load_audio

HOP = 160  # 10 ms @16 kHz
SIL_DB = -40.0
MIN_SIL = 0.08
ABBR = {'mr', 'mrs', 'ms', 'dr', 'st', 'vs', 'etc', 'inc', 'ltd', 'jr', 'sr', 'prof', 'no', 'u.s', 'e.g', 'i.e'}
NUMW = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10, 'eleven': 11, 'twelve': 12,
        'thirteen': 13, 'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30, 'forty': 40,
        'fifty': 50, 'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90}


def split_sentences(text, lang):
    """Deterministic. en: split after . ! ? (+closing quotes) followed by space + capital/digit/opening quote;
    skip abbreviations and single-letter initials. ja: split after full-width terminators."""
    text = re.sub(r'\s+', ' ', text.strip())
    if lang == 'ja':
        out = re.findall(r'.+?(?:[。！？!?]+[」』）)]*|$)', text)
        return [s.strip() for s in out if s.strip()]
    out, cur = [], 0
    for m in re.finditer(r'([.!?]+)(["”’\')\]]*)\s+(?=["“‘(\[]?[A-Z0-9])', text):
        before = text[cur:m.start()]
        last = re.findall(r'[A-Za-z.]+$', before)
        last = last[0].lower().rstrip('.') if last else ''
        if m.group(1) == '.' and (last in ABBR or (len(last) == 1 and last.isalpha())):
            continue
        out.append(text[cur:m.end()].strip())
        cur = m.end()
    if cur < len(text):
        out.append(text[cur:].strip())
    return out


def norm_tok(w):
    w = w.lower().replace('’', "'")
    w = re.sub(r"'s\b", '', w)
    w = re.sub(r'[^a-z0-9]', '', w)
    if w in NUMW:
        w = str(NUMW[w])
    return w


def tokens(s):
    out = []
    for t in re.split(r'\s+|(?<=\w)[—–-](?=\w)', s):
        n = norm_tok(t)
        if n:
            out.append(n)
    return out


def ja_chars(s):
    import unicodedata
    return [c for c in unicodedata.normalize('NFKC', s) if re.match(r'[0-9A-Za-z぀-ヿ一-鿿]', c)]


def expand_ja_words(words):
    out = []
    for w in words:
        cs = ja_chars(w['w'])
        if not cs:
            continue
        d = (w['end'] - w['start']) / len(cs)
        for k, c in enumerate(cs):
            out.append({'w': c, 'start': round(w['start'] + k * d, 3), 'end': round(w['start'] + (k + 1) * d, 3), 'p': w['p']})
    return out


def silence_runs(a):
    n = len(a) // HOP
    rms = np.sqrt((a[:n * HOP].reshape(n, HOP) ** 2).mean(1))
    db = 20 * np.log10(rms + 1e-9)
    sil = db < SIL_DB
    runs, s = [], None
    for i, v in enumerate(sil):
        if v and s is None:
            s = i
        if (not v) and s is not None:
            if (i - s) * 0.01 >= MIN_SIL:
                runs.append((s * 0.01, i * 0.01))
            s = None
    if s is not None:
        runs.append((s * 0.01, n * 0.01))
    merged = []   # a <=0.10 s blip (breath/click) between two silences does not split one pause
    for r in runs:
        if merged and r[0] - merged[-1][1] <= 0.10 + 1e-9:
            merged[-1] = (merged[-1][0], r[1])
        else:
            merged.append(r)
    return merged


def align(script_toks, asr, lang='en'):
    at = [w['w'] for w in asr] if lang == 'ja' else [norm_tok(w['w']) for w in asr]
    sm = difflib.SequenceMatcher(None, script_toks, at, autojunk=False)
    res = [None] * len(script_toks)
    matched = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            for k in range(i2 - i1):
                w = asr[j1 + k]
                res[i1 + k] = (w['start'], w['end'], w['p'])
                matched += 1
    return res, matched, sm.ratio()


def fill_gaps(res):
    """Linear interpolation (by token index) for script tokens not matched to an ASR word."""
    n = len(res)
    out = list(res)
    known = [i for i, r in enumerate(res) if r is not None]
    if not known:
        return None
    for i in range(n):
        if out[i] is not None:
            continue
        L = max([k for k in known if k < i], default=None)
        R = min([k for k in known if k > i], default=None)
        if L is None:
            d = R - i
            out[i] = (max(0.0, res[R][0] - 0.25 * d), max(0.0, res[R][0] - 0.25 * (d - 1)), 0.0)
        elif R is None:
            d = i - L
            out[i] = (res[L][1] + 0.25 * (d - 1), res[L][1] + 0.25 * d, 0.0)
        else:
            a, b = res[L][1], res[R][0]
            span = R - L
            out[i] = (a + (b - a) * (i - L - 1) / span, a + (b - a) * (i - L) / span, 0.0)
    return out


def build_unit(key, u, model, silr, audur):
    raw_path = os.path.join(ROOT, 'docs/research/END-USER-LISTENING-PAGE-PROTOTYPE-01/sync/_asr_raw/%s__%s__%s.json' % (key, u['key'], model))
    asr = json.load(open(raw_path, encoding='utf-8'))
    sents = []
    for ch in u['chunks']:
        # topic_intro embeds the article title ("...Resets! But AI Has Strategy Notes.") -> one display unit
        ss = [re.sub(r'\s+', ' ', ch['text'].strip())] if u['key'] in ('topic_intro', 'japanese_title') else split_sentences(ch['text'], u['lang'])
        ds = split_sentences(ch['display_text'], u['lang']) if ch.get('display_text') else None
        if ds is not None and len(ds) != len(ss):
            ds = None
        for k, s in enumerate(ss):
            sents.append((ch['chunk_id'], s, ds[k] if ds else None))
    toks, owner = [], []
    for si, (_, s, _) in enumerate(sents):
        t = ja_chars(s) if u['lang'] == 'ja' else tokens(s)
        toks += t
        owner += [si] * len(t)
    awords = expand_ja_words(asr['words']) if u['lang'] == 'ja' else asr['words']
    res, matched, ratio = align(toks, awords, u['lang'])
    full = fill_gaps(res)
    ws = []
    for si in range(len(sents)):
        idx = [i for i, o in enumerate(owner) if o == si]
        m = [res[i] for i in idx if res[i] is not None]
        conf = (len(m) / len(idx)) * (sum(x[2] for x in m) / len(m) if m else 0)
        ws.append(dict(asr_start=full[idx[0]][0], asr_end=full[idx[-1]][1], conf=conf, n_tok=len(idx), n_match=len(m)))
    n = len(sents)
    start = [w['asr_start'] for w in ws]
    end = [w['asr_end'] for w in ws]
    snapped = [None] * (n + 1)
    snapped_wide = [False] * (n + 1)
    for k in range(1, n):
        lo, hi = end[k - 1] - 0.20, start[k] + 0.20
        cand = [(s, e) for (s, e) in silr if min(e, hi) - max(s, lo) > 0]
        long_ = [c for c in cand if c[1] - c[0] >= 0.18]   # sentence-final TTS pauses are >=0.2 s; short dips (stop consonants/commas) are not boundaries
        wide = False
        best = max(long_, key=lambda c: c[1] - c[0]) if long_ else None
        if best is None:   # stage 2: ASR boundary may be off by up to ~0.7 s -> accept only a clearly sentence-final pause (>=0.20 s) nearest to the ASR gap
            mid = (end[k - 1] + start[k]) / 2
            cands = [(abs((sx + ex) / 2 - mid), (sx, ex)) for (sx, ex) in silr if ex - sx >= 0.20 and sx < mid + 0.7 and ex > mid - 0.7]
            if cands:
                best, wide = min(cands)[1], True
        if best is None and cand:   # stage 3: only a short dip near the ASR boundary (kept, but flagged low confidence via source tag)
            best, wide = max(cand, key=lambda c: min(c[1], hi) - max(c[0], lo)), True
        snapped[k] = best
        snapped_wide[k] = wide
    firsts = [(s, e) for (s, e) in silr if s <= 0.05]
    onset = firsts[0][1] if firsts else 0.0
    onset = min(onset, start[0] + 0.3)
    lasts = [(s, e) for (s, e) in silr if e >= audur - 0.05]
    offset = lasts[0][0] if lasts else audur
    offset = max(offset, end[-1] - 0.3)
    sentences = []
    for i, (cid, txt, dtxt) in enumerate(sents):
        s_i = onset if i == 0 else (snapped[i][1] if snapped[i] else start[i])
        e_i = offset if i == n - 1 else (snapped[i + 1][0] if snapped[i + 1] else end[i])
        ok = (i == 0 or snapped[i] is not None) and (i == n - 1 or snapped[i + 1] is not None)
        wide_i = snapped_wide[i] or snapped_wide[i + 1]
        src = ('asr_local_whisper_%s+silence_snap' % model + ('_wide' if wide_i else '')) if ok else 'asr_local_whisper_%s' % model
        conf = round(min(1.0, ws[i]['conf']) * (1.0 if (ok and not wide_i) else (0.9 if ok else 0.85)), 3)
        sentences.append(dict(sentence_id='%s-%02d' % (u['key'], i + 1), chunk_id=cid, text=txt, display_text=dtxt,
                              start=round(s_i, 3), end=round(e_i, 3), confidence=conf, source=src,
                              asr_raw=dict(start=round(ws[i]['asr_start'], 3), end=round(ws[i]['asr_end'], 3),
                                           token_match='%d/%d' % (ws[i]['n_match'], ws[i]['n_tok']))))
    return dict(sentences=sentences, tok_match=matched, tok_total=len(toks), seq_ratio=round(ratio, 4), asr_text=asr['text'])


if __name__ == '__main__':
    key = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else 'medium'
    langs = (sys.argv[3] if len(sys.argv) > 3 else 'en').split(',')
    a, units = load_article(key)
    outdir = os.path.join(ROOT, 'docs/research/END-USER-LISTENING-PAGE-PROTOTYPE-01/sync', a['out'])
    os.makedirs(outdir, exist_ok=True)
    index = []
    for u in units:
        if u['lang'] not in langs:
            continue
        if not os.path.exists(os.path.join(ROOT, 'docs/research/END-USER-LISTENING-PAGE-PROTOTYPE-01/sync/_asr_raw/%s__%s__%s.json' % (key, u['key'], model))):
            print('SKIP (no raw ASR yet)', key, u['key'])
            continue
        au = load_audio(os.path.join(ROOT, u['mp3']))
        silr = silence_runs(au)
        r = build_unit(key, u, model, silr, len(au) / 16000)
        doc = dict(schema='eigo_radio_sentence_sync_v1', status='DEV_TRIAL_NOT_PRODUCTION', article=a['title'], level_dir=a['out'], part=u['key'],
                   part_label=u['part'], audio=u['mp3'], audio_duration_s=round(len(au) / 16000, 3), timeline_duration_s=u['duration'],
                   part_start_in_episode_s=u['start'],
                   method='local faster-whisper %s word timestamps + deterministic sentence split + silence snap (RMS<%ddBFS, >=%dms)' % (model, SIL_DB, MIN_SIL * 1000),
                   time_base='seconds from the start of the part mp3 (episode time = part_start_in_episode_s + start)',
                   chunk_gaps_in_part_s=u['gaps'], seq_ratio=r['seq_ratio'], token_match='%d/%d' % (r['tok_match'], r['tok_total']),
                   asr_text=r['asr_text'], sentences=r['sentences'])
        json.dump(doc, open(os.path.join(outdir, u['key'] + '.sentences.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        index.append(dict(part=u['key'], file=u['key'] + '.sentences.json', audio=u['mp3'], part_start_in_episode_s=u['start'], sentences=len(r['sentences'])))
        print(key, u['key'], len(r['sentences']), 'sent', 'tokmatch', doc['token_match'], 'ratio', r['seq_ratio'])
    json.dump(dict(article=a['title'], parts=index), open(os.path.join(outdir, 'index.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
