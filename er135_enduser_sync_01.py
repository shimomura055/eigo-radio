# -*- coding: utf-8 -*-
"""END-USER-LISTENING-PAGE-PRODUCTION-WIRING-01 WP-C: End User listening page sentence-sync module.

Production code (no flag; the End User page generator er135_enduser_page_01.py (WP-B) calls sync_level()).
Local faster-whisper only: API cost 0, no audio regeneration, no fallback generation.

Public API
    sync_level(level_dir, rows, *, cache_dir, model="medium", thresholds=None, align_mode="auto") -> dict
rows (from the adapter):
    [{"row_id", "kind", "audio_path", "sentences":[{"sid","text"}],
      "tts_text": [str,...]   # optional: TTS input script chunks of this row (enables the 2-stage alignment)
      "lang": "en"|"ja"       # optional override
      "kp": {"expressions":[str,...], "assembly":{"en_start":s,"en_end":e}}  # kind=="kp" only
    }]
Output schema "enduser_sync_v1" (times = seconds from the start of the row's segment mp3):
    {"schema","model","params","rows":[{"row_id","mp3_sha256","sentences":[{"sid","text","start","end"}], ["kp_en"]}],
     "gate":{"status":"PASS","token_match":{...},"thresholds":{...}}}
Any failure raises EnduserSyncError (code ENDUSER_SYNC_*); there is no fallback output.

Alignment: main = 2-stage like the DEV (T/sync_build_01.py + T/tools/build_sync_index_02.py):
  TTS script -> deterministic sentence split -> ASR word alignment -> silence snap -> char-alignment onto the display sentences.
When a row has no tts_text the display sentences are aligned directly to the ASR words (same align/fill_gaps/snap code).
ASR raw output is cached per segment mp3 sha256 (raw only; alignment is always re-run).
"""
import argparse
import difflib
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import time
import unicodedata

SCHEMA = "enduser_sync_v1"
ASR_PARAMS = {"engine": "faster-whisper", "device": "cpu", "compute_type": "int8", "beam_size": 5,
              "condition_on_previous_text": False, "vad_filter": False, "word_timestamps": True}
HOP = 160           # 10 ms @ 16 kHz
SIL_DB = -40.0
MIN_SIL = 0.08
SR = 16000
DEFAULT_THRESHOLDS = {
    # row passes when matched/total >= min_ratio, or (short row: tokens <= short_tokens, misses <= short_max_miss,
    # ratio >= short_min_ratio). Values fixed from the Phase-0 distribution (PHASE0_SYNC_01.md).
    "en": {"min_ratio": 0.90, "short_tokens": 20, "short_max_miss": 2, "short_min_ratio": 0.75},
    "ja": {"min_ratio": 0.90, "short_tokens": 30, "short_max_miss": 3, "short_min_ratio": 0.75},
    "zero_match_sentence_min_tokens": 2,   # a sentence with >= this many tokens and 0 matched ASR words (fully interpolated) fails
    "display_min_coverage": 0.60,     # 2-stage: share of a display sentence's chars found in the script
    "kp_min_ratio": 0.80,             # KP expression tokens found in the ASR of the chosen English block
    "kp_min_blocks": 4,
    # ASR dropout repair (WP-E, 2026-10-29): Whisper sometimes skips a spoken span inside a long row (Y redelivery fee std_18 lost 10 words /
    # 4.2 s; the words exist in the audio). A gap between ASR words (or lead/tail) longer than dropout_gap_s that holds >= dropout_min_voiced_s of
    # non-silence is re-transcribed as its own window (same model/params, cached per window) and merged. Gates are NOT relaxed.
    "dropout_gap_s": 2.0,
    "dropout_min_voiced_s": 1.0,
    "dropout_margin_s": 0.4,
    "audio_len_tol_s": 0.05,
}
LOCK_NAME = ".asr.lock"
LOCK_STALE_S = 6 * 3600
LOCK_TIMEOUT_S = 4 * 3600

ABBR = {'mr', 'mrs', 'ms', 'dr', 'st', 'vs', 'etc', 'inc', 'ltd', 'jr', 'sr', 'prof', 'no', 'u.s', 'e.g', 'i.e'}
NUMW = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
        'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15, 'sixteen': 16,
        'seventeen': 17, 'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
        'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90}

ASR_STATS = {"transcribe_calls": 0, "cache_hits": 0, "model_loads": 0}


class EnduserSyncError(Exception):
    """Sync failure. code is always ENDUSER_SYNC_*; callers must stop End User generation (no fallback)."""

    def __init__(self, code, message, detail=None):
        assert code.startswith("ENDUSER_SYNC_"), code
        super().__init__("%s: %s" % (code, message))
        self.code = code
        self.message = message
        self.detail = detail


# ----------------------------------------------------------------------------- text
def split_sentences(text, lang):
    """Deterministic (port of T/sync_build_01.py:split_sentences)."""
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
    return [s for s in out if s]


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
    return [c for c in unicodedata.normalize('NFKC', s) if re.match(r'[0-9A-Za-z぀-ヿ一-鿿]', c)]


def has_cjk(s):
    return bool(re.search(r'[぀-ヿ一-鿿]', s))


def norm_chars(s):
    s = unicodedata.normalize('NFKC', html.unescape(s)).lower()
    return re.sub(r'[\s\W_]+', '', s)


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


# ----------------------------------------------------------------------------- audio / ASR
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def load_audio(path, sr=SR):
    import numpy as np
    import av
    c = av.open(path)
    st = c.streams.audio[0]
    rs = av.AudioResampler(format='fltp', layout='mono', rate=sr)
    out = []
    for f in c.decode(st):
        for g in rs.resample(f):
            out.append(g.to_ndarray()[0])
    for g in rs.resample(None):
        out.append(g.to_ndarray()[0])
    c.close()
    return np.concatenate(out).astype(np.float32)


def silence_runs(a):
    import numpy as np
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
    merged = []   # a <=0.10 s blip between two silences does not split one pause
    for r in runs:
        if merged and r[0] - merged[-1][1] <= 0.10 + 1e-9:
            merged[-1] = (merged[-1][0], r[1])
        else:
            merged.append(r)
    return merged


def speech_blocks(a, d=0.2, db_thr=-40.0):
    """KP clip speech blocks = gaps between silences of >=d seconds below db_thr (DEV: ffmpeg silencedetect noise=-40dB d=0.2)."""
    import numpy as np
    hop = 80  # 5 ms
    n = len(a) // hop
    peak = np.abs(a[:n * hop]).reshape(n, hop).max(1)
    sil = 20 * np.log10(peak + 1e-9) < db_thr
    runs, s = [], None
    for i, v in enumerate(sil):
        if v and s is None:
            s = i
        if (not v) and s is not None:
            if (i - s) * 0.005 >= d:
                runs.append((s * 0.005, i * 0.005))
            s = None
    if s is not None and (n - s) * 0.005 >= d:
        runs.append((s * 0.005, n * 0.005))
    dur = len(a) / SR
    sp, t = [], 0.0
    for s0, e0 in runs:
        if s0 > t + 0.02:
            sp.append((t, s0))
        t = e0
    if dur > t + 0.02:
        sp.append((t, dur))
    return sp


def _load_model(model):
    """Patchable (tests). Raises ENDUSER_SYNC_MODEL_MISSING when the model cannot be loaded."""
    try:
        from faster_whisper import WhisperModel
        ASR_STATS["model_loads"] += 1
        return WhisperModel(model, device='cpu', compute_type='int8')
    except Exception as e:  # noqa: BLE001 - any load failure is a STOP
        raise EnduserSyncError("ENDUSER_SYNC_MODEL_MISSING", "cannot load faster-whisper model %r: %s" % (model, e))


def _transcribe(model_obj, audio, lang):
    """Patchable (tests). Returns {'text','words':[{'w','start','end','p'}]}."""
    segs, _info = model_obj.transcribe(audio, language=lang, word_timestamps=True, beam_size=5,
                                       condition_on_previous_text=False, vad_filter=False)
    words, texts = [], []
    for s in segs:
        texts.append(s.text)
        for w in (s.words or []):
            words.append({'w': w.word, 'start': round(w.start, 3), 'end': round(w.end, 3), 'p': round(w.probability, 3)})
    return {'text': ''.join(texts).strip(), 'words': words}


def _params_key(model, lang):
    blob = json.dumps(ASR_PARAMS, sort_keys=True) + '|' + str(lang)
    return "%s_%s_%s" % (model, lang or 'auto', hashlib.sha1(blob.encode()).hexdigest()[:8])


def _cache_path(cache_dir, sha, model, lang):
    return os.path.join(cache_dir, "%s_%s.json" % (sha, _params_key(model, lang)))


def _pid_alive(pid):
    try:
        if os.name == 'nt':
            out = subprocess.run(['tasklist', '/FI', 'PID eq %d' % pid, '/NH'], capture_output=True, text=True).stdout
            return str(pid) in out
        os.kill(pid, 0)
        return True
    except Exception:  # noqa: BLE001
        return False


class AsrLock:
    """Single ASR process at a time (CPU contention). Lock file <cache_dir>/.asr.lock, waits for acquisition."""

    def __init__(self, cache_dir, timeout_s=LOCK_TIMEOUT_S, poll_s=0.5, stale_s=LOCK_STALE_S):
        self.path = os.path.join(cache_dir, LOCK_NAME)
        self.timeout_s, self.poll_s, self.stale_s = timeout_s, poll_s, stale_s
        self.held = False

    def _stale(self):
        try:
            age = time.time() - os.path.getmtime(self.path)
            if age > self.stale_s:
                return True
            pid = int(open(self.path).read().split()[0])
            return not _pid_alive(pid)
        except (OSError, ValueError, IndexError):
            return False

    def acquire(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        t0 = time.time()
        while True:
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, ("%d %f\n" % (os.getpid(), time.time())).encode())
                os.close(fd)
                self.held = True
                return self
            except FileExistsError:
                if self._stale():
                    try:
                        os.remove(self.path)
                    except OSError:
                        pass
                    continue
                if time.time() - t0 > self.timeout_s:
                    raise EnduserSyncError("ENDUSER_SYNC_LOCK_TIMEOUT", "ASR lock %s not acquired in %ss" % (self.path, self.timeout_s))
                time.sleep(self.poll_s)

    def release(self):
        if self.held:
            try:
                os.remove(self.path)
            except OSError:
                pass
            self.held = False

    def __enter__(self):
        return self.acquire()

    def __exit__(self, *a):
        self.release()


def _job_label(lang, window):
    return lang if window is None else "%s@%.2f-%.2f" % (lang, window[0], window[1])


def asr_raw_many(jobs, cache_dir, model):
    """jobs: [(mp3_path, sha, lang[, window])] -> {(sha, label): raw}; label = lang or lang@start-end for a slice.
    Cache hit = no ASR. Raw ASR output only is stored."""
    os.makedirs(cache_dir, exist_ok=True)
    res, todo, seen = {}, [], set()
    for job in jobs:
        path, sha, lang = job[:3]
        window = job[3] if len(job) > 3 else None
        label = _job_label(lang, window)
        if (sha, label) in seen:
            continue
        seen.add((sha, label))
        cp = _cache_path(cache_dir, sha, model, label)
        if os.path.exists(cp):
            try:
                res[(sha, label)] = json.load(open(cp, encoding='utf-8'))
                ASR_STATS["cache_hits"] += 1
                continue
            except (OSError, ValueError):
                pass
        todo.append((path, sha, lang, window, label))
    if todo:
        with AsrLock(cache_dir):
            m = None
            for path, sha, lang, window, label in todo:
                cp = _cache_path(cache_dir, sha, model, label)
                if os.path.exists(cp):          # another process filled it while we waited for the lock
                    res[(sha, label)] = json.load(open(cp, encoding='utf-8'))
                    ASR_STATS["cache_hits"] += 1
                    continue
                if m is None:
                    m = _load_model(model)
                t0 = time.time()
                try:
                    a = load_audio(path)
                    if window is not None:
                        a = a[int(window[0] * SR):int(window[1] * SR)]
                    raw = _transcribe(m, a, lang)
                except EnduserSyncError:
                    raise
                except Exception as e:  # noqa: BLE001
                    raise EnduserSyncError("ENDUSER_SYNC_ASR_FAILED", "ASR failed for %s: %s" % (path, e))
                ASR_STATS["transcribe_calls"] += 1
                raw.update({'mp3_sha256': sha, 'model': model, 'lang': lang, 'window': window, 'duration': round(len(a) / SR, 3),
                            'elapsed': round(time.time() - t0, 1), 'params': ASR_PARAMS})
                tmp = cp + '.tmp%d' % os.getpid()
                json.dump(raw, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False)
                os.replace(tmp, cp)
                res[(sha, label)] = raw
    return res


# ----------------------------------------------------------------------------- alignment (port of T/sync_build_01.py)
def align_tokens(script_toks, asr, lang='en'):
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


def align_sentences(sents, lang, asr_words, silr, audur):
    """sents: list[str] (already split). Returns (list of dict(start,end,n_tok,n_match,low_conf), matched, total, ratio)."""
    toks, owner = [], []
    for si, s in enumerate(sents):
        t = ja_chars(s) if lang == 'ja' else tokens(s)
        if not t:
            raise EnduserSyncError("ENDUSER_SYNC_EMPTY_SENTENCE", "sentence without alignable tokens: %r" % s)
        toks += t
        owner += [si] * len(t)
    awords = expand_ja_words(asr_words) if lang == 'ja' else asr_words
    if not awords:
        raise EnduserSyncError("ENDUSER_SYNC_ALIGN_FAILED", "ASR returned no words")
    res, matched, ratio = align_tokens(toks, awords, lang)
    full = fill_gaps(res)
    if full is None:
        raise EnduserSyncError("ENDUSER_SYNC_ALIGN_FAILED", "no script token matched any ASR word")
    n = len(sents)
    ws = []
    for si in range(n):
        idx = [i for i, o in enumerate(owner) if o == si]
        m = [res[i] for i in idx if res[i] is not None]
        ws.append(dict(asr_start=full[idx[0]][0], asr_end=full[idx[-1]][1], n_tok=len(idx), n_match=len(m)))
    start = [w['asr_start'] for w in ws]
    end = [w['asr_end'] for w in ws]
    snapped = [None] * (n + 1)
    wide_ = [False] * (n + 1)
    prev_end = 0.0      # end of the silence chosen for the previous boundary: boundaries must stay strictly ordered
    for k in range(1, n):
        lo, hi = end[k - 1] - 0.20, start[k] + 0.20
        silk = [(s, e) for (s, e) in silr if s >= prev_end + 0.05]
        cand = [(s, e) for (s, e) in silk if min(e, hi) - max(s, lo) > 0]
        long_ = [c for c in cand if c[1] - c[0] >= 0.18]
        wide = False
        best = max(long_, key=lambda c: c[1] - c[0]) if long_ else None
        if best is None:
            mid = (end[k - 1] + start[k]) / 2
            cands = [(abs((sx + ex) / 2 - mid), (sx, ex)) for (sx, ex) in silk if ex - sx >= 0.20 and sx < mid + 0.7 and ex > mid - 0.7]
            if cands:
                best, wide = min(cands)[1], True
        if best is None and cand:
            best, wide = max(cand, key=lambda c: min(c[1], hi) - max(c[0], lo)), True
        snapped[k] = best
        wide_[k] = wide
        if best is not None:
            prev_end = best[1]
    firsts = [(s, e) for (s, e) in silr if s <= 0.05]
    onset = firsts[0][1] if firsts else 0.0
    onset = min(onset, start[0] + 0.3)
    lasts = [(s, e) for (s, e) in silr if e >= audur - 0.05]
    offset = lasts[0][0] if lasts else audur
    offset = max(offset, end[-1] - 0.3)
    out = []
    for i in range(n):
        s_i = onset if i == 0 else (snapped[i][1] if snapped[i] else start[i])
        e_i = offset if i == n - 1 else (snapped[i + 1][0] if snapped[i + 1] else end[i])
        ok = (i == 0 or snapped[i] is not None) and (i == n - 1 or snapped[i + 1] is not None)
        out.append(dict(start=s_i, end=e_i, n_tok=ws[i]['n_tok'], n_match=ws[i]['n_match'],
                        low_conf=bool((not ok) or wide_[i] or wide_[i + 1])))
    return out, matched, len(toks), ratio


def map_to_display(timed, script_sents, display_sents):
    """2nd stage (port of T/tools/build_sync_index_02.py): char-align script sentences onto display sentences.
    Returns [dict(start,end,status,cov)] per display sentence (status exact|merged|split|unmatched)."""
    sn, smap = '', []
    for k, s in enumerate(script_sents):
        n = norm_chars(s)
        smap += [(k, i, len(n)) for i in range(len(n))]
        sn += n
    pn, pr = '', []
    for s in display_sents:
        n = norm_chars(s)
        pr.append((len(pn), len(pn) + len(n)))
        pn += n
    sm = difflib.SequenceMatcher(None, pn, sn, autojunk=False)
    p2s = [None] * len(pn)
    for tag, a1, a2, b1, b2 in sm.get_opcodes():
        if tag == 'equal':
            for d in range(a2 - a1):
                p2s[a1 + d] = b1 + d
    rows = []
    for (a, b) in pr:
        ok = [p2s[i] for i in range(a, b) if p2s[i] is not None]
        cov = len(ok) / max(1, b - a)
        if not ok:
            rows.append(dict(start=None, end=None, status='unmatched', cov=round(cov, 3)))
            continue
        i0, i1 = ok[0], ok[-1]
        k0, o0, n0 = smap[i0]
        k1, o1, n1 = smap[i1]

        def tm(k, o, n, edge):
            x = timed[k]
            return x['start'] + (x['end'] - x['start']) * (o / n if edge == 's' else (o + 1) / n)
        t0 = timed[k0]['start'] if o0 == 0 else tm(k0, o0, n0, 's')
        t1 = timed[k1]['end'] if o1 == n1 - 1 else tm(k1, o1, n1, 'e')
        if k0 == k1 and o0 == 0 and o1 == n1 - 1:
            st = 'exact'
        elif k0 == k1:
            st = 'split'
        else:
            st = 'merged' if (o0 == 0 and o1 == n1 - 1) else 'split'
        rows.append(dict(start=t0, end=t1, status=st, cov=round(cov, 3)))
    return rows


# ----------------------------------------------------------------------------- per-row sync
def _row_lang(row):
    if row.get('lang') in ('en', 'ja'):
        return row['lang']
    text = ' '.join(s['text'] for s in row.get('sentences') or []) + ' ' + ' '.join(row.get('tts_text') or [])
    return 'ja' if has_cjk(text) else 'en'


def sync_row(row, raw, audio, thresholds, align_mode):
    """Returns (sentences_out, stats). raises EnduserSyncError on structural problems."""
    lang = _row_lang(row)
    sents = row['sentences']
    silr = silence_runs(audio)
    audur = len(audio) / SR
    tts = [t for t in (row.get('tts_text') or []) if t and t.strip()]
    two_stage = bool(tts) and align_mode != 'direct'
    display = [s['text'] for s in sents]
    if two_stage:
        script = []
        for chunk in tts:
            script += split_sentences(chunk, lang)
        timed, matched, total, ratio = align_sentences(script, lang, raw['words'], silr, audur)
        mapped = map_to_display(timed, script, display)
        dmin = thresholds['display_min_coverage']
        for s, m in zip(sents, mapped):
            if m['status'] == 'unmatched' or m['cov'] < dmin:
                raise EnduserSyncError("ENDUSER_SYNC_DISPLAY_UNMATCHED",
                                       "row %s sid %s: display sentence not found in TTS script (cov=%s)" % (row['row_id'], s['sid'], m['cov']),
                                       {'row_id': row['row_id'], 'sid': s['sid'], 'text': s['text']})
        spans = [(m['start'], m['end']) for m in mapped]
        stat = dict(mode='two_stage', n_tok=total, n_match=matched, seq_ratio=round(ratio, 4),
                    low_conf=sum(1 for t in timed if t['low_conf']),
                    zero_match_sentences=sum(1 for t in timed if t['n_match'] == 0),
                    zero_match_long_sentences=sum(1 for t in timed if t['n_match'] == 0 and t['n_tok'] >= thresholds['zero_match_sentence_min_tokens']),
                    min_sentence_ratio=round(min(t['n_match'] / t['n_tok'] for t in timed), 3),
                    display_status={k: sum(1 for m in mapped if m['status'] == k) for k in ('exact', 'merged', 'split')},
                    n_script_sentences=len(script))
    else:
        timed, matched, total, ratio = align_sentences(display, lang, raw['words'], silr, audur)
        spans = [(t['start'], t['end']) for t in timed]
        stat = dict(mode='direct', n_tok=total, n_match=matched, seq_ratio=round(ratio, 4),
                    low_conf=sum(1 for t in timed if t['low_conf']),
                    zero_match_sentences=sum(1 for t in timed if t['n_match'] == 0),
                    zero_match_long_sentences=sum(1 for t in timed if t['n_match'] == 0 and t['n_tok'] >= thresholds['zero_match_sentence_min_tokens']),
                    min_sentence_ratio=round(min(t['n_match'] / t['n_tok'] for t in timed), 3))
    stat['lang'] = lang
    stat['audio_s'] = round(audur, 3)
    out = [dict(sid=s['sid'], text=s['text'], start=round(a, 3), end=round(b, 3)) for s, (a, b) in zip(sents, spans)]
    pauses = [out[i + 1]['start'] - out[i]['end'] for i in range(len(out) - 1)]
    stat['min_pause'] = round(min(pauses), 3) if pauses else None
    return out, stat


def check_structure(row_id, out, audur, tol):
    """Hard gate (1)(2): 0<=start<end<=audio length (+tol), monotone, no overlap."""
    prev = 0.0
    for s in out:
        if s['start'] is None or s['end'] is None:
            raise EnduserSyncError("ENDUSER_SYNC_STRUCT", "row %s sid %s has no time" % (row_id, s['sid']))
        if s['start'] < -1e-9 or s['end'] <= s['start'] or s['end'] > audur + tol:
            raise EnduserSyncError("ENDUSER_SYNC_STRUCT", "row %s sid %s bad span [%s,%s] audio=%.3f" % (row_id, s['sid'], s['start'], s['end'], audur),
                                   {'row_id': row_id, 'sid': s['sid']})
        if s['start'] < prev - 1e-6:
            raise EnduserSyncError("ENDUSER_SYNC_STRUCT", "row %s sid %s overlaps previous (start %s < prev end %s)" % (row_id, s['sid'], s['start'], prev),
                                   {'row_id': row_id, 'sid': s['sid']})
        prev = s['end']


def token_gate(stat, thresholds):
    """Language- and length-specific token match rule. Returns True when the row passes."""
    t = thresholds[stat['lang']]
    n, m = stat['n_tok'], stat['n_match']
    if stat.get('zero_match_long_sentences', 0) > 0:
        return False
    ratio = m / n if n else 0.0
    if ratio >= t['min_ratio']:
        return True
    return n <= t['short_tokens'] and m >= 1 and (n - m) <= t['short_max_miss'] and ratio >= t['short_min_ratio']


# ----------------------------------------------------------------------------- KP English span
def kp_window(row, audio, thresholds):
    """KP clip (number -> English -> meaning/explanation -> English again): the English span is the 2nd speech block
    (>= kp_min_blocks blocks; Z Adv KP2-type clips may have 5). Assembly-record times, when given, are the first basis.
    Returns (start, end, source, n_blocks)."""
    kp = row.get('kp') or {}
    if not (kp.get('expressions') or []):
        raise EnduserSyncError("ENDUSER_SYNC_KP_NOEXPR", "row %s: kp.expressions missing" % row['row_id'])
    blocks = speech_blocks(audio)
    asm = kp.get('assembly')
    if asm and asm.get('en_start') is not None and asm.get('en_end') is not None:
        return float(asm['en_start']), float(asm['en_end']), 'assembly_record', len(blocks)
    if len(blocks) < thresholds['kp_min_blocks']:
        raise EnduserSyncError("ENDUSER_SYNC_KP_BLOCKS", "row %s: %d speech blocks (<%d)" % (row['row_id'], len(blocks), thresholds['kp_min_blocks']),
                               {'blocks': [(round(a, 3), round(b, 3)) for a, b in blocks]})
    return blocks[1][0], blocks[1][1], 'silencedetect_block2', len(blocks)


def kp_slice(s, e, audur):
    return (round(max(0.0, s - 0.10), 2), round(min(audur, e + 0.20), 2))


def kp_verify(row, raw_win, s, e, src, nblocks, thresholds):
    """The English window is transcribed on its own with language=en (a whole-clip auto-language ASR renders English
    words as katakana in Japanese clips). KP expression must be found in it (token score or joined-character coverage)."""
    win = [norm_tok(w['w']) for w in raw_win['words']]
    win = [w for w in win if w]
    wjoin = ''.join(win)
    worst = 1.0
    for ex in row['kp']['expressions']:
        et = tokens(ex)
        if not et:
            continue
        hit = 0
        for t in et:
            if t in win or any(difflib.SequenceMatcher(None, t, w).ratio() >= 0.8 for w in win if len(t) > 3):
                hit += 1
        tok_score = hit / len(et)
        # ASR may split/merge words ("shoving match" -> "shove in match"): also score by character coverage of the joined phrase
        ej = ''.join(et)
        sm = difflib.SequenceMatcher(None, ej, wjoin, autojunk=False)
        char_score = sum(b.size for b in sm.get_matching_blocks()) / len(ej)
        worst = min(worst, max(tok_score, char_score))
    if worst < thresholds['kp_min_ratio']:
        raise EnduserSyncError("ENDUSER_SYNC_KP_MISMATCH",
                               "row %s: KP expression not found in chosen English window [%.2f,%.2f] (match %.2f); window ASR=%r" % (row['row_id'], s, e, worst, win),
                               {'window': [round(s, 3), round(e, 3)]})
    return dict(start=round(max(0.0, s - 0.08), 3), end=round(e + 0.15, 3), source=src, blocks=nblocks, token_match=round(worst, 3))


# ----------------------------------------------------------------------------- public API
def _merge_thresholds(th):
    out = json.loads(json.dumps(DEFAULT_THRESHOLDS))
    for k, v in (th or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k].update(v)
        else:
            out[k] = v
    return out


def _validate_rows(rows):
    if not isinstance(rows, list) or not rows:
        raise EnduserSyncError("ENDUSER_SYNC_ROWS_INVALID", "rows must be a non-empty list")
    seen = set()
    for r in rows:
        for k in ('row_id', 'kind', 'audio_path'):
            if not r.get(k):
                raise EnduserSyncError("ENDUSER_SYNC_ROWS_INVALID", "row missing %s: %r" % (k, r.get('row_id')))
        if r['row_id'] in seen:
            raise EnduserSyncError("ENDUSER_SYNC_ROWS_INVALID", "duplicate row_id %s" % r['row_id'])
        seen.add(r['row_id'])
        if r['kind'] == 'kp':
            continue
        if not r.get('sentences'):
            raise EnduserSyncError("ENDUSER_SYNC_ROWS_INVALID", "row %s has no sentences" % r['row_id'])
        sids = [s['sid'] for s in r['sentences']]
        if len(set(sids)) != len(sids):
            raise EnduserSyncError("ENDUSER_SYNC_ROWS_INVALID", "row %s duplicate sid" % r['row_id'])


def find_dropouts(words, audio, th):
    """ASR dropout candidates: [(gap_start, gap_end, (win_start, win_end))]. A gap (before the first word, between words, after the last word)
    longer than dropout_gap_s that contains >= dropout_min_voiced_s of non-silence (silence_runs) is a spoken span the ASR skipped."""
    audur = len(audio) / SR
    ws = sorted(words, key=lambda w: w['start'])
    edges = [(0.0, ws[0]['start'])] if ws else [(0.0, audur)]
    edges += [(ws[i]['end'], ws[i + 1]['start']) for i in range(len(ws) - 1)]
    if ws:
        edges.append((ws[-1]['end'], audur))
    silr = silence_runs(audio)
    out = []
    for g0, g1 in edges:
        if g1 - g0 <= th['dropout_gap_s']:
            continue
        sil_in = sum(max(0.0, min(g1, b) - max(g0, a)) for a, b in silr)
        if (g1 - g0) - sil_in < th['dropout_min_voiced_s']:
            continue
        m = th['dropout_margin_s']
        out.append((g0, g1, (round(max(0.0, g0 - m), 2), round(min(audur, g1 + m), 2))))
    return out


def merge_dropouts(raw, gaps, rraws, sha, lang):
    """Merge window re-transcriptions into the row raw (a copy; the cached raw is untouched). Only words whose centre lies inside the gap are taken."""
    words = [dict(w) for w in raw['words']]
    n = 0
    for g0, g1, win in gaps:
        rr = rraws[(sha, _job_label(lang, win))]
        for w in rr['words']:
            st, en = w['start'] + win[0], w['end'] + win[0]
            c = (st + en) / 2
            if g0 - 0.02 <= c <= g1 + 0.02:
                words.append(dict(w, start=round(st, 3), end=round(en, 3)))
                n += 1
    words.sort(key=lambda w: (w['start'], w['end']))
    return dict(raw, words=words, text=''.join(w['w'] for w in words).strip()), n


def sync_level(level_dir, rows, *, cache_dir, model="medium", thresholds=None, align_mode="auto"):
    """Sync one level (Std or Adv). Returns the enduser_sync_v1 dict or raises EnduserSyncError."""
    if align_mode not in ('auto', 'direct'):
        raise EnduserSyncError("ENDUSER_SYNC_ROWS_INVALID", "align_mode must be auto|direct")
    th = _merge_thresholds(thresholds)
    _validate_rows(rows)
    t_start = time.time()
    s0 = dict(ASR_STATS)
    prepared = []
    for r in rows:
        p = r['audio_path'] if os.path.isabs(r['audio_path']) else os.path.join(level_dir, r['audio_path'])
        if not os.path.isfile(p):
            raise EnduserSyncError("ENDUSER_SYNC_AUDIO_MISSING", "row %s: audio not found %s" % (r['row_id'], p))
        try:
            audio = load_audio(p)
        except Exception as e:  # noqa: BLE001
            raise EnduserSyncError("ENDUSER_SYNC_AUDIO_MISSING", "row %s: cannot decode %s: %s" % (r['row_id'], p, e))
        sha = sha256_file(p)
        kpw = None
        if r['kind'] == 'kp':
            ks, ke, ksrc, nb = kp_window(r, audio, th)
            kpw = (ks, ke, ksrc, nb)
            job = (p, sha, 'en', kp_slice(ks, ke, len(audio) / SR))
        else:
            job = (p, sha, _row_lang(r))
        prepared.append((r, audio, sha, kpw, job))
    raws = asr_raw_many([x[4] for x in prepared], cache_dir, model)
    repairs = {}
    rjobs = []
    for r, audio, sha, kpw, job in prepared:
        if r['kind'] == 'kp':
            continue
        raw = raws[(sha, _job_label(job[2], job[3] if len(job) > 3 else None))]
        gaps = find_dropouts(raw['words'], audio, th)
        if gaps:
            repairs[r['row_id']] = gaps
            rjobs += [(job[0], sha, job[2], g[2]) for g in gaps]
    rraws = asr_raw_many(rjobs, cache_dir, model) if rjobs else {}
    out_rows, stats, warnings, repair_log = [], {}, [], []
    for r, audio, sha, kpw, job in prepared:
        raw = raws[(sha, _job_label(job[2], job[3] if len(job) > 3 else None))]
        if r['row_id'] in repairs:
            raw, nrep = merge_dropouts(raw, repairs[r['row_id']], {(sha, _job_label(job[2], g[2])): rraws[(sha, _job_label(job[2], g[2]))] for g in repairs[r['row_id']]}, sha, job[2])
            repair_log.append({'row_id': r['row_id'], 'repaired_words': nrep, 'gaps': [[round(g[0], 2), round(g[1], 2)] for g in repairs[r['row_id']]]})
        audur = len(audio) / SR
        ro = dict(row_id=r['row_id'], mp3_sha256=sha, sentences=[])
        if r['kind'] == 'kp':
            ro['kp_en'] = kp_verify(r, raw, kpw[0], kpw[1], kpw[2], kpw[3], th)
        else:
            sents, st = sync_row(r, raw, audio, th, align_mode)
            check_structure(r['row_id'], sents, audur, th['audio_len_tol_s'])
            st['pass'] = token_gate(st, th)
            stats[r['row_id']] = st
            if not st['pass']:
                raise EnduserSyncError("ENDUSER_SYNC_TOKEN_MATCH",
                                       "row %s token match %d/%d (%s) below threshold" % (r['row_id'], st['n_match'], st['n_tok'], st['lang']),
                                       {'row_id': r['row_id'], 'stat': st})
            if st['low_conf']:
                warnings.append({'row_id': r['row_id'], 'low_conf_boundaries': st['low_conf']})
            ro['sentences'] = sents
        out_rows.append(ro)
    tot = sum(s['n_tok'] for s in stats.values())
    mat = sum(s['n_match'] for s in stats.values())
    ratios = [s['n_match'] / s['n_tok'] for s in stats.values() if s['n_tok']]
    keep = ('mode', 'lang', 'n_tok', 'n_match', 'seq_ratio', 'min_sentence_ratio', 'zero_match_long_sentences', 'low_conf', 'min_pause', 'pass')
    return {
        "schema": SCHEMA, "model": model,
        "params": dict(ASR_PARAMS, sil_db=SIL_DB, min_sil_s=MIN_SIL, align_mode=align_mode, time_base="row_local_seconds",
                       languages="ja if CJK else en (kp window: en)"),
        "rows": out_rows,
        "gate": {"status": "PASS",
                 "token_match": {"rows": {k: {kk: v[kk] for kk in keep} for k, v in stats.items()},
                                 "total_tokens": tot, "total_matched": mat,
                                 "min_row_ratio": round(min(ratios), 4) if ratios else None},
                 "thresholds": th, "warnings": warnings, "asr_dropout_repairs": repair_log},
        "cost": {"api_calls": 0, "wall_s": round(time.time() - t_start, 1),
                 "asr_transcribed": ASR_STATS["transcribe_calls"] - s0["transcribe_calls"],
                 "cached_segments": ASR_STATS["cache_hits"] - s0["cache_hits"], "model": model},
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="End User page sentence sync (local faster-whisper, API 0)")
    ap.add_argument('--level-dir', required=True)
    ap.add_argument('--rows-json', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--cache-dir', required=True)
    ap.add_argument('--model', default='medium')
    a = ap.parse_args(argv)
    rows = json.load(open(a.rows_json, encoding='utf-8'))
    try:
        res = sync_level(a.level_dir, rows, cache_dir=a.cache_dir, model=a.model)
    except EnduserSyncError as e:
        print(e.code, e.message, file=sys.stderr)
        return 3
    tmp = a.out + '.tmp'
    json.dump(res, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    os.replace(tmp, a.out)
    print('OK', a.out, 'rows', len(res['rows']), 'min_row_ratio', res['gate']['token_match']['min_row_ratio'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
