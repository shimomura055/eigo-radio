# -*- coding: utf-8 -*-
"""er135_enduser_sync_01 tests (API 0). Synthetic audio + fake ASR for unit tests; one real-audio test (skips when the
local faster-whisper model or the segment mp3 is unavailable, or ER135_SKIP_REAL_ASR=1)."""
import json
import os
import shutil
import tempfile
import threading
import time
import unittest
import wave

import numpy as np

import er135_enduser_sync_01 as S

SR = 16000
FAKE = {}   # audio length (samples) -> raw dict, filled by synth_wav()


def tone(sec):
    t = np.arange(int(sec * SR)) / SR
    return (0.3 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)


def sil(sec):
    return np.zeros(int(sec * SR), dtype=np.float32)


def write_wav(path, a):
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((a * 32767).astype(np.int16).tobytes())


def synth_wav(path, sentences, gap=0.5, tok_s=0.25, drop=(), extra_tail=0.3, gaps=None):
    # lead silence differs per file name so that rows get distinct audio bytes (distinct sha256 / cache key)
    lead = 0.3 + (sum(map(ord, os.path.basename(path))) % 40) * 0.001
    """sentences: list[list[str]] ASR tokens per sentence. Returns the fake ASR raw (also registered in FAKE).
    drop: set of (sentence_idx, token_idx) the fake ASR does not output."""
    parts, words, t = [sil(lead)], [], lead
    for si, toks in enumerate(sentences):
        for ti, w in enumerate(toks):
            parts.append(tone(tok_s))
            if (si, ti) not in drop:
                words.append({'w': ' ' + w, 'start': round(t, 3), 'end': round(t + tok_s, 3), 'p': 0.9})
            t += tok_s
        g = gaps[si] if gaps else gap
        parts.append(sil(g))
        t += g
    parts.append(sil(extra_tail))
    a = np.concatenate(parts)
    write_wav(path, a)
    raw = {'text': ' '.join(w['w'].strip() for w in words), 'words': words}
    FAKE[len(a)] = raw
    return raw


PROMPTS = []


def fake_transcribe(model_obj, audio, lang, initial_prompt=None):
    S.ASR_STATS['fake_calls'] = S.ASR_STATS.get('fake_calls', 0) + 1
    PROMPTS.append(initial_prompt)
    return json.loads(json.dumps(FAKE[len(audio)]))


def kp_wav(path, nblocks, expr_words=('make', 'an', 'effort'), assembly=None):
    """number / English / meaning(ja or English explanation) / English again [+ extra blocks]; blocks separated by 0.4 s silence."""
    blocks = [('one',), tuple(expr_words), ('ja_x',), tuple(expr_words), ('extra',)][:max(nblocks, 1)]
    if nblocks == 3:
        blocks = [('one',), tuple(expr_words), ('ja_x',)]
    if nblocks == 5:
        blocks = [('one',), tuple(expr_words), ('ja_x',), ('more', 'words'), tuple(expr_words)]
    parts, words, t = [sil(0.3)], [], 0.3
    for b in blocks:
        for w in b:
            parts.append(tone(0.25))
            words.append({'w': ' ' + w, 'start': round(t, 3), 'end': round(t + 0.25, 3), 'p': 0.9})
            t += 0.25
        parts.append(sil(0.4))
        t += 0.4
    a = np.concatenate(parts)
    write_wav(path, a)
    # the module transcribes only the English window slice (language=en): register the fake ASR for that slice
    if assembly:
        ws_, we_ = assembly
    else:
        bl = S.speech_blocks(a)
        ws_, we_ = (bl[1] if len(bl) > 1 else (0.0, len(a) / SR))
    sl = S.kp_slice(ws_, we_, len(a) / SR)
    n = len(a[int(sl[0] * SR):int(sl[1] * SR)])
    FAKE[n] = {'text': '', 'words': [dict(w, start=round(w['start'] - sl[0], 3), end=round(w['end'] - sl[0], 3))
                                     for w in words if w['start'] >= sl[0] - 0.01 and w['end'] <= sl[1] + 0.01]}
    return words


class Base(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix='er135t_')
        self.cache = os.path.join(self.d, 'cache')
        self._lm, self._tr = S._load_model, S._transcribe
        S._load_model = lambda model: object()
        S._transcribe = fake_transcribe
        S.ASR_STATS.update({'transcribe_calls': 0, 'cache_hits': 0, 'model_loads': 0, 'fake_calls': 0})

    def tearDown(self):
        S._load_model, S._transcribe = self._lm, self._tr
        shutil.rmtree(self.d, ignore_errors=True)

    def mk_row(self, name, sentences, **kw):
        """sentences: list[str] display texts; ASR tokens derived by S.tokens (numbers stay as given)."""
        toks = [S.tokens(s) for s in sentences]
        p = os.path.join(self.d, name + '.wav')
        raw = synth_wav(p, toks, drop=kw.pop('drop', ()))
        row = {'row_id': name, 'kind': 'script', 'audio_path': p,
               'sentences': [{'sid': '%s-s%d' % (name, i + 1), 'text': s} for i, s in enumerate(sentences)]}
        row.update(kw)
        return row, raw


class TestStructure(Base):
    def test_schema_and_invariants_direct(self):
        row, _ = self.mk_row('r1', ['The cat sat on the mat.', 'Then it left the room quickly.', 'Nobody saw it again.'])
        out = S.sync_level(self.d, [row], cache_dir=self.cache)
        self.assertEqual(out['schema'], 'enduser_sync_v1')
        self.assertEqual(out['model'], 'medium')
        self.assertEqual(out['gate']['status'], 'PASS')
        self.assertEqual(out['params']['compute_type'], 'int8')
        self.assertEqual(out['params']['beam_size'], 5)
        self.assertEqual(out['params']['time_base'], 'row_local_seconds')
        self.assertEqual(out['cost']['api_calls'], 0)
        r = out['rows'][0]
        self.assertEqual(set(r), {'row_id', 'mp3_sha256', 'sentences'})
        self.assertEqual([s['sid'] for s in r['sentences']], ['r1-s1', 'r1-s2', 'r1-s3'])
        self.assertEqual([s['text'] for s in r['sentences']], ['The cat sat on the mat.', 'Then it left the room quickly.', 'Nobody saw it again.'])
        prev = 0.0
        for s in r['sentences']:
            self.assertGreaterEqual(s['start'], prev - 1e-9)
            self.assertGreater(s['end'], s['start'])
            prev = s['end']
        self.assertEqual(set(out['gate']['thresholds']) >= {'en', 'ja', 'kp_min_ratio'}, True)
        # snapped to the synthetic silence: 0.3 s lead + 6 tokens * 0.25 = 1.8 s -> sentence 1 ends 1.8, sentence 2 starts 2.3
        self.assertAlmostEqual(r['sentences'][0]['end'], 1.8, delta=0.08)
        self.assertAlmostEqual(r['sentences'][1]['start'], 2.3, delta=0.08)

    def test_check_structure_violations(self):
        ok = [{'sid': 'a', 'start': 0.1, 'end': 1.0}, {'sid': 'b', 'start': 1.2, 'end': 2.0}]
        S.check_structure('r', ok, 2.0, 0.05)
        for bad in ([{'sid': 'a', 'start': 0.5, 'end': 0.5}],                       # zero length
                    [{'sid': 'a', 'start': 0.1, 'end': 2.5}],                       # beyond audio
                    [{'sid': 'a', 'start': 0.1, 'end': 1.5}, {'sid': 'b', 'start': 1.0, 'end': 2.0}],   # overlap
                    [{'sid': 'a', 'start': None, 'end': 1.0}],
                    [{'sid': 'a', 'start': -0.5, 'end': 1.0}]):
            with self.assertRaises(S.EnduserSyncError) as cm:
                S.check_structure('r', bad, 2.0, 0.05)
            self.assertEqual(cm.exception.code, 'ENDUSER_SYNC_STRUCT')

    def test_rows_validation(self):
        for rows in ([], [{'row_id': 'x', 'kind': 'script'}], [{'row_id': 'x', 'kind': 'script', 'audio_path': 'a.mp3', 'sentences': []}]):
            with self.assertRaises(S.EnduserSyncError) as cm:
                S.sync_level(self.d, rows, cache_dir=self.cache)
            self.assertEqual(cm.exception.code, 'ENDUSER_SYNC_ROWS_INVALID')
        with self.assertRaises(S.EnduserSyncError) as cm:
            S.sync_level(self.d, [{'row_id': 'x', 'kind': 'script', 'audio_path': 'nope.mp3', 'sentences': [{'sid': 's', 'text': 'Hi there.'}]}], cache_dir=self.cache)
        self.assertEqual(cm.exception.code, 'ENDUSER_SYNC_AUDIO_MISSING')


class TestTwoStage(Base):
    def test_two_stage_maps_display_with_number_and_quotes(self):
        # TTS script says "eight blocks", display shows 8 and curly quotes; display sentence 2 merges nothing
        tts = ['The team found eight blocks near the base. They called it the Cathedral.']
        disp = ['The team found 8 blocks near the base.', 'They called it “the Cathedral.”']
        script_sents = S.split_sentences(tts[0], 'en')
        p = os.path.join(self.d, 'ts.wav')
        synth_wav(p, [S.tokens(s) for s in script_sents])
        row = {'row_id': 'ts', 'kind': 'script', 'audio_path': p, 'tts_text': tts,
               'sentences': [{'sid': 'ts-s1', 'text': disp[0]}, {'sid': 'ts-s2', 'text': disp[1]}]}
        out = S.sync_level(self.d, [row], cache_dir=self.cache)
        st = out['gate']['token_match']['rows']['ts']
        self.assertEqual(st['mode'], 'two_stage')
        ss = out['rows'][0]['sentences']
        self.assertEqual(len(ss), 2)
        self.assertLess(ss[0]['end'], ss[1]['start'])
        # direct mode on the same row gives the same boundaries (number normalised)
        outd = S.sync_level(self.d, [row], cache_dir=self.cache, align_mode='direct')
        self.assertEqual(outd['gate']['token_match']['rows']['ts']['mode'], 'direct')
        for a, b in zip(ss, outd['rows'][0]['sentences']):
            self.assertAlmostEqual(a['start'], b['start'], delta=0.03)
            self.assertAlmostEqual(a['end'], b['end'], delta=0.03)

    def test_display_not_in_script_stops(self):
        tts = ['The team found eight blocks near the base.']
        p = os.path.join(self.d, 'nd.wav')
        synth_wav(p, [S.tokens(tts[0])])
        row = {'row_id': 'nd', 'kind': 'script', 'audio_path': p, 'tts_text': tts,
               'sentences': [{'sid': 'nd-s1', 'text': 'Completely different words appear here instead.'}]}
        with self.assertRaises(S.EnduserSyncError) as cm:
            S.sync_level(self.d, [row], cache_dir=self.cache)
        self.assertEqual(cm.exception.code, 'ENDUSER_SYNC_DISPLAY_UNMATCHED')


class TestThresholds(Base):
    def test_short_row_tolerates_one_miss_long_row_does_not(self):
        # short: 6 tokens, 1 dropped -> 5/6=0.83 < 0.90 but short rule (<=20 tokens, <=2 misses, ratio>=0.75) passes
        row, _ = self.mk_row('sh', ['Welcome to English.', 'Your Way now.'], drop={(0, 2)})
        out = S.sync_level(self.d, [row], cache_dir=self.cache)
        self.assertTrue(out['gate']['token_match']['rows']['sh']['pass'])
        # short: 2 dropped -> STOP
        row2, _ = self.mk_row('sh2', ['Welcome to English.', 'Your Way now.'], drop={(0, 2), (1, 0)})
        with self.assertRaises(S.EnduserSyncError) as cm:
            S.sync_level(self.d, [row2], cache_dir=self.cache)
        self.assertEqual(cm.exception.code, 'ENDUSER_SYNC_TOKEN_MATCH')
        # long: 20 tokens, 3 dropped -> 17/20=0.85 -> STOP (short rule does not apply)
        txt = 'one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty'
        long_words = 'alpha bravo charlie delta echo foxtrot golf hotel india juliet kilo lima mike november oscar papa quebec romeo sierra tango'
        lw = long_words.split()
        row3, _ = self.mk_row('lg', [' '.join(lw[:10]) + '.', ' '.join(lw[10:]) + '.'], drop={(0, 2), (0, 7), (1, 2)})
        with self.assertRaises(S.EnduserSyncError) as cm:
            S.sync_level(self.d, [row3], cache_dir=self.cache)
        self.assertEqual(cm.exception.code, 'ENDUSER_SYNC_TOKEN_MATCH')
        # long: 2 dropped -> 18/20 = 0.90 -> PASS
        row4, _ = self.mk_row('lg2', [' '.join(lw[:10]) + '.', ' '.join(lw[10:]) + '.'], drop={(0, 2), (0, 7)})
        out = S.sync_level(self.d, [row4], cache_dir=self.cache)
        self.assertTrue(out['gate']['token_match']['rows']['lg2']['pass'])
        del txt

    def test_real_phase0_case_17_tokens_2_misses_passes_but_3_misses_in_24_fails(self):
        words17 = 'today topic is more than eight thousand nine hundred wrinkles on the moon the secret of its hidden coat'.split()
        row, _ = self.mk_row('p17', [' '.join(words17[:8]) + '.', ' '.join(words17[8:]) + '.'], drop={(0, 6), (0, 7)})        # 15/17 = 0.882 (Phase-0: moon Std Topic intro)
        out = S.sync_level(self.d, [row], cache_dir=self.cache)
        self.assertTrue(out['gate']['token_match']['rows']['p17']['pass'])
        words24 = ('alpha bravo charlie delta echo foxtrot golf hotel india juliet kilo lima mike november oscar papa quebec romeo sierra tango '
                   'uniform victor whiskey xray').split()
        row2, _ = self.mk_row('p24', [' '.join(words24[:12]) + '.', ' '.join(words24[12:]) + '.'], drop={(0, 1), (0, 9), (1, 3)})   # 21/24 = 0.875 > 2 misses and > 20 tokens
        with self.assertRaises(S.EnduserSyncError) as cm:
            S.sync_level(self.d, [row2], cache_dir=self.cache)
        self.assertEqual(cm.exception.code, 'ENDUSER_SYNC_TOKEN_MATCH')

    def test_fully_interpolated_sentence_fails_even_if_row_ratio_is_high(self):
        long_s = ' '.join('w%d' % i for i in range(60))
        row, _ = self.mk_row('zm', [long_s + '.', 'alpha bravo.'], drop={(1, 0), (1, 1)})     # row: 60/62 = 0.97 but sentence 2 has 0/2 matched
        with self.assertRaises(S.EnduserSyncError) as cm:
            S.sync_level(self.d, [row], cache_dir=self.cache)
        self.assertEqual(cm.exception.code, 'ENDUSER_SYNC_TOKEN_MATCH')

    def test_threshold_override_is_explicit(self):
        row, _ = self.mk_row('ov', ['alpha bravo charlie delta echo foxtrot.', 'golf hotel india juliet kilo lima.'], drop={(0, 1), (0, 5), (1, 3)})
        with self.assertRaises(S.EnduserSyncError):
            S.sync_level(self.d, [row], cache_dir=self.cache)
        out = S.sync_level(self.d, [row], cache_dir=self.cache, thresholds={'en': {'min_ratio': 0.7}})
        self.assertEqual(out['gate']['thresholds']['en']['min_ratio'], 0.7)

    def test_japanese_chars_use_ja_threshold(self):
        # Japanese rows are aligned per character; fake ASR emits one word per character
        text = 'これはテストの文です。次の文もあります。'
        sents = S.split_sentences(text, 'ja')
        chars = [[c] for s in sents for c in S.ja_chars(s)]
        flat = [S.ja_chars(s) for s in sents]
        p = os.path.join(self.d, 'ja.wav')
        synth_wav(p, flat)
        row = {'row_id': 'ja', 'kind': 'script', 'audio_path': p, 'sentences': [{'sid': 'ja-s%d' % (i + 1), 'text': s} for i, s in enumerate(sents)]}
        out = S.sync_level(self.d, [row], cache_dir=self.cache)
        self.assertEqual(out['gate']['token_match']['rows']['ja']['lang'], 'ja')
        self.assertEqual(len(out['rows'][0]['sentences']), 2)
        del chars


class TestSingleSentenceRow(Base):
    """Fable case B (FZ-DIALOGUE-LR-ADOPTION-01): one-sentence rows are structure-checked only; token ratio is recorded as a warning."""

    def test_single_sentence_row_passes_despite_token_mismatch_and_records_warning(self):
        row, _ = self.mk_row('one', ['alpha bravo charlie.'], drop={(0, 0), (0, 2)})   # 1/3 matched
        out = S.sync_level(self.d, [row], cache_dir=self.cache)
        self.assertTrue(out['gate']['token_match']['rows']['one']['pass'])
        w = [x for x in out['gate']['warnings'] if x.get('single_sentence_row_structural_only')]
        self.assertEqual(len(w), 1)
        self.assertEqual(w[0]['row_id'], 'one')
        self.assertAlmostEqual(w[0]['token_match_ratio'], 0.3333, places=3)
        r = out['rows'][0]['sentences'][0]
        self.assertGreater(r['end'], r['start'])

    def test_two_sentence_row_still_stops(self):
        row, _ = self.mk_row('two', ['alpha bravo charlie.', 'delta echo foxtrot.'], drop={(0, 0), (0, 2), (1, 1), (1, 2)})
        with self.assertRaises(S.EnduserSyncError) as cm:
            S.sync_level(self.d, [row], cache_dir=self.cache)
        self.assertEqual(cm.exception.code, 'ENDUSER_SYNC_TOKEN_MATCH')

    def test_single_sentence_structure_check_still_applies(self):
        with self.assertRaises(S.EnduserSyncError) as cm:
            S.check_structure('x', [{'sid': 'x1', 'start': 0.0, 'end': 9.0}], 2.0, 0.05)
        self.assertEqual(cm.exception.code, 'ENDUSER_SYNC_STRUCT')


class TestKnownProperNouns(Base):
    """FZ-DIALOGUE-LR-ADOPTION-01 委任_07: Whisper initial_prompt (in the cache key) + known-name-only normalisation. Thresholds unchanged."""
    NAMES = {'en': ['Tajomaru', 'Takehiro', 'Masago']}

    def _row(self, heard, shown):
        p = os.path.join(self.d, 'pn.wav')
        synth_wav(p, [heard[0], heard[1]])
        return {'row_id': 'pn', 'kind': 'script', 'audio_path': p,
                'sentences': [{'sid': 'pn-s1', 'text': shown[0]}, {'sid': 'pn-s2', 'text': shown[1]}]}

    def test_split_name_and_edit_distance_match_known_names_only(self):
        shown = ['Tajomaru says he freed Takehiro and they fought.', 'What does Masago say happened after the bandit left?']
        heard = [['tajo', 'maru', 'says', 'he', 'freed', 'takahiro', 'and', 'they', 'fought'],
                 ['what', 'does', 'misago', 'say', 'happened', 'after', 'the', 'bandit', 'left']]
        row = self._row(heard, shown)
        with self.assertRaises(S.EnduserSyncError) as cm:           # without the known names: 6/17 style miss -> STOP (threshold unchanged)
            S.sync_level(self.d, [row], cache_dir=self.cache + '0')
        self.assertEqual(cm.exception.code, 'ENDUSER_SYNC_TOKEN_MATCH')
        out = S.sync_level(self.d, [row], cache_dir=self.cache + '1', proper_nouns=self.NAMES)
        self.assertEqual(out['gate']['status'], 'PASS')
        self.assertEqual(out['gate']['token_match']['rows']['pn']['n_match'], out['gate']['token_match']['rows']['pn']['n_tok'])
        w = {(x['known_name_normalized'], x['to']) for x in out['gate']['warnings'] if 'known_name_normalized' in x}
        self.assertEqual(w, {('tajo maru', 'Tajomaru'), ('takahiro', 'Takehiro'), ('misago', 'Masago')})
        self.assertEqual([s['text'] for s in out['rows'][0]['sentences']], shown)          # displayed names unchanged

    def test_general_words_are_not_normalised(self):
        words = [{'w': ' ' + t, 'start': i * 0.3, 'end': i * 0.3 + 0.25, 'p': 0.9} for i, t in enumerate(['masaga', 'mastery', 'takes', 'tajomar'])]
        new, log = S.normalize_known_names_en(words, ['Tajomaru', 'Masago', 'Takehiro'], ['tajomaru', 'masago', 'takehiro', 'mastery', 'takes'])
        self.assertEqual([x['from'] for x in log], ['masaga', 'tajomar'])        # near known names (distance <= 2)
        self.assertEqual([w['w'].strip() for w in new if w['w'].strip() in ('mastery', 'takes')], ['mastery', 'takes'])   # general words stay
        # a name that is NOT in this row's script is never applied, and a far token is not read as a name
        new2, log2 = S.normalize_known_names_en(words, ['Tajomaru', 'Masago'], ['masago', 'mastery'])
        self.assertEqual([x['to'] for x in log2], ['Masago'])
        _, log3 = S.normalize_known_names_en([{'w': ' banana', 'start': 0, 'end': 1, 'p': 1.0}], ['Tajomaru'], ['tajomaru'])
        self.assertEqual(log3, [])
        # short names (< 5 letters) are not fuzzy-matched
        _, log4 = S.normalize_known_names_en([{'w': ' moon', 'start': 0, 'end': 1, 'p': 1.0}], ['Monk'], ['monk'])
        self.assertEqual(log4, [])

    def test_exact_name_does_not_swallow_neighbours(self):
        words = [{'w': ' ' + t, 'start': i * 0.3, 'end': i * 0.3 + 0.25, 'p': 0.9} for i, t in enumerate(['Masago', 'is', 'proud', 'Taki', 'Hiro'])]
        new, log = S.normalize_known_names_en(words, ['Masago', 'Takehiro'], ['masago', 'is', 'proud', 'takehiro'])
        self.assertEqual([w['w'].strip() for w in new], ['Masago', 'is', 'proud', 'Takehiro'])
        self.assertEqual(log, [{'from': 'Taki Hiro', 'to': 'Takehiro'}])

    def test_initial_prompt_is_part_of_the_cache_key(self):
        self.assertNotEqual(S._params_key('medium', 'en', None), S._params_key('medium', 'en', 'Tajomaru.'))
        self.assertNotEqual(S._params_key('medium', 'en', 'A.'), S._params_key('medium', 'en', 'B.'))
        self.assertEqual(S._params_key('medium', 'en'), S._params_key('medium', 'en', None))     # old cache entries stay valid when no prompt
        row, _ = self.mk_row('ck', ['alpha bravo charlie delta.', 'echo foxtrot golf hotel.'])
        S.sync_level(self.d, [row], cache_dir=self.cache)
        self.assertEqual(S.ASR_STATS['transcribe_calls'], 1)
        S.sync_level(self.d, [row], cache_dir=self.cache)
        self.assertEqual(S.ASR_STATS['transcribe_calls'], 1)             # same (no) prompt -> cache hit
        del PROMPTS[:]
        S.sync_level(self.d, [row], cache_dir=self.cache, proper_nouns=self.NAMES)
        self.assertEqual(S.ASR_STATS['transcribe_calls'], 2)             # prompted run does not reuse the unprompted cache
        self.assertEqual(PROMPTS, ['Tajomaru, Takehiro, Masago.'])
        S.sync_level(self.d, [row], cache_dir=self.cache, proper_nouns=self.NAMES)
        self.assertEqual(S.ASR_STATS['transcribe_calls'], 2)

    def test_thresholds_unchanged(self):
        self.assertEqual(S.DEFAULT_THRESHOLDS['en'], {'min_ratio': 0.90, 'short_tokens': 20, 'short_max_miss': 2, 'short_min_ratio': 0.75})
        self.assertEqual(S.DEFAULT_THRESHOLDS['ja'], {'min_ratio': 0.90, 'short_tokens': 30, 'short_max_miss': 3, 'short_min_ratio': 0.75})

    def test_collect_failures_lists_every_failing_row(self):
        r1, _ = self.mk_row('f1', ['alpha bravo charlie delta echo.', 'foxtrot golf hotel india juliet.'], drop={(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)})
        r2, _ = self.mk_row('f2', ['kilo lima mike november oscar.', 'papa quebec romeo sierra tango.'], drop={(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)})
        out = S.sync_level(self.d, [r1, r2], cache_dir=self.cache, collect_failures=True)
        self.assertEqual(out['gate']['status'], 'FAIL')
        self.assertEqual([f['row_id'] for f in out['dry_failures']], ['f1', 'f2'])
        with self.assertRaises(S.EnduserSyncError):
            S.sync_level(self.d, [r1, r2], cache_dir=self.cache)


class TestKanaFold(unittest.TestCase):
    def test_katakana_and_hiragana_same_reading_compare_equal(self):
        self.assertEqual(S.ja_chars('タジョマル'), S.ja_chars('たじょまる'))
        self.assertEqual(S.ja_chars('ー'), ['ー'])      # long-vowel mark unchanged
        self.assertNotEqual(S.ja_chars('真砂'), S.ja_chars('まさ'))   # kanji vs kana is NOT folded


class TestSnapMonotone(Base):
    def test_short_dip_after_one_word_sentence_does_not_reuse_previous_silence(self):
        # Z Adv Part 1 case: '"Go." / "I know you'll come back."' is spoken without a real pause (only a 0.12 s dip).
        sents = ['Melos looked at his friend for a long moment.', 'Go.', "I know you will come back."]
        toks = [S.tokens(x) for x in sents]
        p = os.path.join(self.d, 'mono.wav')
        synth_wav(p, toks, gaps=[0.5, 0.12, 0.5])
        row = {'row_id': 'mono', 'kind': 'script', 'audio_path': p,
               'sentences': [{'sid': 'mono-s%d' % (i + 1), 'text': x} for i, x in enumerate(sents)]}
        out = S.sync_level(self.d, [row], cache_dir=self.cache)       # must not raise ENDUSER_SYNC_STRUCT
        ss = out['rows'][0]['sentences']
        for a, b in zip(ss, ss[1:]):
            self.assertLessEqual(a['end'], b['start'] + 1e-6)
        for x in ss:
            self.assertGreater(x['end'], x['start'])
        self.assertGreaterEqual(ss[1]['end'] - ss[1]['start'], 0.2)
        self.assertEqual(out['gate']['token_match']['rows']['mono']['low_conf'] >= 1, True)


class TestCache(Base):
    def test_cache_hit_no_asr_and_raw_only_and_alignment_rerun(self):
        row, _ = self.mk_row('c1', ['The cat sat on the mat.', 'Then it left the room.'])
        row2, _ = self.mk_row('c2', ['A second row has other words today.'])
        S.sync_level(self.d, [row, row2], cache_dir=self.cache)
        self.assertEqual(S.ASR_STATS['transcribe_calls'], 2)
        files = [f for f in os.listdir(self.cache) if f.endswith('.json')]
        self.assertEqual(len(files), 2)
        for f in files:                                   # raw ASR output only: no sentences / alignment inside
            d = json.load(open(os.path.join(self.cache, f), encoding='utf-8'))
            self.assertNotIn('sentences', d)
            self.assertNotIn('rows', d)
            self.assertIn('words', d)
            self.assertEqual(len(d['mp3_sha256']), 64)
        S.ASR_STATS.update({'transcribe_calls': 0, 'cache_hits': 0, 'model_loads': 0})
        out = S.sync_level(self.d, [row, row2], cache_dir=self.cache)
        self.assertEqual(S.ASR_STATS['transcribe_calls'], 0)
        self.assertEqual(S.ASR_STATS['model_loads'], 0)
        self.assertEqual(out['cost']['cached_segments'], 2)
        # alignment is re-run every time: split the same audio into different display sentences -> different boundaries
        row_alt = dict(row, sentences=[{'sid': 'c1-s1', 'text': 'The cat sat on the mat. Then it left the room.'}])
        out2 = S.sync_level(self.d, [row_alt], cache_dir=self.cache)
        self.assertEqual(len(out2['rows'][0]['sentences']), 1)
        self.assertEqual(S.ASR_STATS['transcribe_calls'], 0)

    def test_only_changed_segment_is_recomputed(self):
        row, _ = self.mk_row('d1', ['The cat sat on the mat.'])
        row2, _ = self.mk_row('d2', ['Another row with words.'])
        S.sync_level(self.d, [row, row2], cache_dir=self.cache)
        S.ASR_STATS.update({'transcribe_calls': 0, 'cache_hits': 0, 'model_loads': 0})
        row2b, _ = self.mk_row('d2', ['Another row with different words here.'])   # same path, new audio -> new sha
        out = S.sync_level(self.d, [row, row2b], cache_dir=self.cache)
        self.assertEqual(S.ASR_STATS['transcribe_calls'], 1)
        self.assertEqual(out['cost']['asr_transcribed'], 1)
        self.assertEqual(out['cost']['cached_segments'], 1)

    def test_cache_key_includes_model(self):
        row, _ = self.mk_row('m1', ['The cat sat on the mat.'])
        S.sync_level(self.d, [row], cache_dir=self.cache, model='medium')
        S.sync_level(self.d, [row], cache_dir=self.cache, model='small')
        self.assertEqual(S.ASR_STATS['transcribe_calls'], 2)


class TestFailure(Base):
    def test_model_missing_raises_and_no_fallback_output(self):
        row, _ = self.mk_row('f1', ['The cat sat on the mat.'])

        S._load_model = self._lm      # real loader; the model constructor is made to fail (no network access)
        import faster_whisper
        from unittest import mock
        with mock.patch.object(faster_whisper, 'WhisperModel', side_effect=OSError('model not found')):
            with self.assertRaises(S.EnduserSyncError) as cm:
                S.sync_level(self.d, [row], cache_dir=self.cache, model='definitely-not-a-model-xyz')
        self.assertEqual(cm.exception.code, 'ENDUSER_SYNC_MODEL_MISSING')
        self.assertFalse(os.path.exists(os.path.join(self.cache, S.LOCK_NAME)), 'lock released on failure')

    def test_asr_exception_raises(self):
        row, _ = self.mk_row('f2', ['The cat sat on the mat.'])

        def bad(m, a, l):
            raise RuntimeError('asr crashed')
        S._transcribe = bad
        with self.assertRaises(S.EnduserSyncError) as cm:
            S.sync_level(self.d, [row], cache_dir=self.cache)
        self.assertEqual(cm.exception.code, 'ENDUSER_SYNC_ASR_FAILED')
        self.assertFalse(os.path.exists(os.path.join(self.cache, S.LOCK_NAME)), 'lock released on failure')

    def test_cli_failure_writes_no_output(self):
        row, _ = self.mk_row('f3', ['The cat sat.', 'on the mat now.'], drop={(0, 1), (0, 2), (1, 0)})
        rows_json = os.path.join(self.d, 'rows.json')
        json.dump([row], open(rows_json, 'w', encoding='utf-8'))
        out = os.path.join(self.d, 'sync.json')
        rc = S.main(['--level-dir', self.d, '--rows-json', rows_json, '--out', out, '--cache-dir', self.cache])
        self.assertEqual(rc, 3)
        self.assertFalse(os.path.exists(out))
        self.assertFalse(os.path.exists(out + '.tmp'))

    def test_cli_success_writes_schema(self):
        row, _ = self.mk_row('f4', ['The cat sat on the mat now.'])
        rows_json = os.path.join(self.d, 'rows.json')
        json.dump([row], open(rows_json, 'w', encoding='utf-8'))
        out = os.path.join(self.d, 'sync.json')
        rc = S.main(['--level-dir', self.d, '--rows-json', rows_json, '--out', out, '--cache-dir', self.cache])
        self.assertEqual(rc, 0)
        self.assertEqual(json.load(open(out, encoding='utf-8'))['schema'], 'enduser_sync_v1')

    def test_no_fallback_constructs_in_module(self):
        src = open(S.__file__, encoding='utf-8').read()
        for forbidden in ('ENDUSER_SYNC_FALLBACK', 'dummy', 'proportional', 'equal_split', 'highlight_off'):
            self.assertNotIn(forbidden, src)

    def test_error_code_prefix(self):
        with self.assertRaises(AssertionError):
            S.EnduserSyncError('OTHER_CODE', 'x')


class TestLock(Base):
    def test_second_acquirer_waits_for_release(self):
        os.makedirs(self.cache, exist_ok=True)
        first = S.AsrLock(self.cache, poll_s=0.05).acquire()
        got = {}

        def second():
            t0 = time.time()
            with S.AsrLock(self.cache, poll_s=0.05, timeout_s=10):
                got['waited'] = time.time() - t0
        th = threading.Thread(target=second)
        th.start()
        time.sleep(0.5)
        self.assertNotIn('waited', got)           # still waiting while the first holds the lock
        first.release()
        th.join(5)
        self.assertGreaterEqual(got.get('waited', 0), 0.4)
        self.assertFalse(os.path.exists(os.path.join(self.cache, S.LOCK_NAME)))

    def test_timeout_raises(self):
        os.makedirs(self.cache, exist_ok=True)
        first = S.AsrLock(self.cache).acquire()
        with self.assertRaises(S.EnduserSyncError) as cm:
            S.AsrLock(self.cache, poll_s=0.05, timeout_s=0.3).acquire()
        self.assertEqual(cm.exception.code, 'ENDUSER_SYNC_LOCK_TIMEOUT')
        first.release()

    def test_stale_lock_is_taken_over(self):
        os.makedirs(self.cache, exist_ok=True)
        lp = os.path.join(self.cache, S.LOCK_NAME)
        open(lp, 'w').write('999999 0\n')                       # dead pid
        old = time.time() - 10 * 3600
        os.utime(lp, (old, old))
        with S.AsrLock(self.cache, poll_s=0.05, timeout_s=3):
            self.assertTrue(os.path.exists(lp))
        self.assertFalse(os.path.exists(lp))

    def test_sync_level_holds_lock_only_during_asr(self):
        row, _ = self.mk_row('l1', ['The cat sat on the mat.'])
        seen = {}
        orig = S._transcribe

        def spy(m, a, l):
            seen['lock'] = os.path.exists(os.path.join(self.cache, S.LOCK_NAME))
            return orig(m, a, l)
        S._transcribe = spy
        S.sync_level(self.d, [row], cache_dir=self.cache)
        self.assertTrue(seen['lock'])
        self.assertFalse(os.path.exists(os.path.join(self.cache, S.LOCK_NAME)))


class TestKP(Base):
    def kp_row(self, name, nblocks, expr=('make', 'an', 'effort'), words=None, **kw):
        asm = kw.pop('assembly', None)
        kw['assembly'] = asm
        p = os.path.join(self.d, name + '.wav')
        kp_wav(p, nblocks, words or expr, assembly=kw.get('assembly'))
        row = {'row_id': name, 'kind': 'kp', 'audio_path': p, 'sentences': [], 'kp': {'expressions': [' '.join(expr)]}}
        row.pop('assembly', None)
        return row

    def test_four_blocks_second_is_english(self):
        out = S.sync_level(self.d, [self.kp_row('k4', 4)], cache_dir=self.cache)
        k = out['rows'][0]['kp_en']
        self.assertEqual(k['blocks'], 4)
        self.assertEqual(k['source'], 'silencedetect_block2')
        # block 2 starts at 0.3 + 0.25 + 0.4 = 0.95 and lasts 0.75 s
        self.assertAlmostEqual(k['start'], 0.95 - 0.08, delta=0.04)
        self.assertAlmostEqual(k['end'], 1.70 + 0.15, delta=0.04)

    def test_five_blocks_like_z_adv_kp2(self):
        out = S.sync_level(self.d, [self.kp_row('k5', 5)], cache_dir=self.cache)
        k = out['rows'][0]['kp_en']
        self.assertEqual(k['blocks'], 5)
        self.assertAlmostEqual(k['start'], 0.95 - 0.08, delta=0.04)

    def test_three_blocks_stops(self):
        with self.assertRaises(S.EnduserSyncError) as cm:
            S.sync_level(self.d, [self.kp_row('k3', 3)], cache_dir=self.cache)
        self.assertEqual(cm.exception.code, 'ENDUSER_SYNC_KP_BLOCKS')

    def test_asr_mismatch_stops(self):
        row = self.kp_row('km', 4, expr=('completely', 'different', 'phrase'), words=('make', 'an', 'effort'))
        with self.assertRaises(S.EnduserSyncError) as cm:
            S.sync_level(self.d, [row], cache_dir=self.cache)
        self.assertEqual(cm.exception.code, 'ENDUSER_SYNC_KP_MISMATCH')

    def test_fuzzy_token_tolerance(self):
        row = self.kp_row('kf', 4, expr=('make', 'an', 'effort'), words=('make', 'an', 'efforts'))
        out = S.sync_level(self.d, [row], cache_dir=self.cache)
        self.assertGreaterEqual(out['rows'][0]['kp_en']['token_match'], 0.8)

    def test_assembly_record_is_first_basis(self):
        row = self.kp_row('ka', 3, assembly=(0.95, 1.70))      # 3 blocks would STOP without the assembly record
        row['kp']['assembly'] = {'en_start': 0.95, 'en_end': 1.70}
        out = S.sync_level(self.d, [row], cache_dir=self.cache)
        self.assertEqual(out['rows'][0]['kp_en']['source'], 'assembly_record')
        self.assertEqual(out['rows'][0]['kp_en']['blocks'], 3)

    def test_kp_without_expression_stops(self):
        row = self.kp_row('kx', 4)
        row['kp']['expressions'] = []
        with self.assertRaises(S.EnduserSyncError) as cm:
            S.sync_level(self.d, [row], cache_dir=self.cache)
        self.assertEqual(cm.exception.code, 'ENDUSER_SYNC_KP_NOEXPR')


class TestRealAudio(unittest.TestCase):
    """One real-audio test (Family X moon Std 'Topic intro'; 1 mp3, real faster-whisper medium). Skips when unavailable."""
    MP3 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_test', 'family_x_moon_shrinking_reselect_01', 'audio', 'std_02.mp3')

    def test_real_topic_intro(self):
        if os.environ.get('ER135_SKIP_REAL_ASR') == '1' or not os.path.isfile(self.MP3):
            self.skipTest('real audio/ASR disabled or mp3 missing')
        try:
            import faster_whisper  # noqa: F401
            S._load_model('medium')
        except Exception as e:  # noqa: BLE001
            self.skipTest('faster-whisper medium unavailable: %s' % e)
        d = tempfile.mkdtemp(prefix='er135real_')
        try:
            row = {'row_id': 'real1', 'kind': 'script', 'audio_path': self.MP3,
                   'sentences': [{'sid': 'real1-s1', 'text': "Today's topic is More Than 8,900 Wrinkles on the Moon! The Secret of Its Hidden “Rock Coat”."}]}
            out = S.sync_level(d, [row], cache_dir=os.path.join(d, 'cache'))
            s = out['rows'][0]['sentences'][0]
            self.assertGreater(s['end'], s['start'])
            self.assertLess(s['end'], 12.0)
            self.assertGreaterEqual(out['gate']['token_match']['min_row_ratio'], 0.85)   # Phase-0: 15/17 (8,900 is read differently); passes via the short-row rule
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
