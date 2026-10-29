# -*- coding: utf-8 -*-
"""ASR dropout repair (END-USER-LISTENING-PAGE-PRODUCTION-WIRING-01 WP-E) tests (API 0, synthetic audio + fake ASR).
Background: Whisper skipped 10 spoken words (4.2 s) inside a 40 s row of the Y redelivery-fee Std audio; the audio holds the words (window re-ASR
recovers them). The sync module re-transcribes such voiced gaps as separate cached windows and merges them. Gates are not relaxed."""
import unittest

import numpy as np

import er135_enduser_sync_01 as S
import er135_enduser_sync_test_01 as T

SR = T.SR
TH = S._merge_thresholds(None)


def tok_sentences(n_sent=3, per=12):
    return [["w%d_%d" % (s, i) for i in range(per)] for s in range(n_sent)]


class TestFindDropouts(unittest.TestCase):
    def test_voiced_gap_detected_silent_gap_not(self):
        a = np.concatenate([T.tone(1.0), T.sil(3.0), T.tone(3.0), T.sil(0.5)])      # 0-1 voiced, 1-4 silent, 4-7 voiced
        words = [{'w': ' a', 'start': 0.1, 'end': 0.9, 'p': 0.9}, {'w': ' b', 'start': 4.1, 'end': 4.5, 'p': 0.9}]
        g = S.find_dropouts(words, a, TH)
        # gap 0.9-4.1 is silent (3 s silence) -> not a dropout; tail 4.5-7.5 has 2.5 s voiced -> dropout
        self.assertEqual([(round(x[0], 1), round(x[1], 1)) for x in g], [(4.5, 7.5)])

    def test_short_gap_ignored(self):
        a = np.concatenate([T.tone(5.0)])
        words = [{'w': ' a', 'start': 0.0, 'end': 1.0, 'p': 0.9}, {'w': ' b', 'start': 2.5, 'end': 5.0, 'p': 0.9}]   # gap 1.5 s <= 2.0
        self.assertEqual(S.find_dropouts(words, a, TH), [])

    def test_window_has_margin_and_is_clipped(self):
        a = np.concatenate([T.tone(8.0)])
        words = [{'w': ' a', 'start': 0.0, 'end': 1.0, 'p': 0.9}, {'w': ' b', 'start': 5.0, 'end': 8.0, 'p': 0.9}]
        g = S.find_dropouts(words, a, TH)
        self.assertEqual(g[0][2], (0.6, 5.4))


class TestRepairIntegration(T.Base):
    def _row(self, drop_from=12, drop_n=10):
        sents = tok_sentences()
        disp = [" ".join(t) for t in sents]
        # reference raw without dropout (registered first; the dropout version overwrites the same-length key)
        full = T.synth_wav(self.d + "/ref.wav", sents)
        drop = {(1, i) for i in range(2, 2 + drop_n)}       # 10 consecutive tokens (2.5 s) inside sentence 2
        row, raw = self.mk_row("r1", disp, drop=drop)
        return row, raw, full, drop

    def _register_window(self, row, full):
        a = S.load_audio(row['audio_path'])
        raw = S.asr_raw_many.__globals__['_transcribe']          # fake
        # find the dropout gap exactly as the module will, then register the fake ASR for the window slice
        words = T.FAKE[len(a)]['words']
        gaps = S.find_dropouts(words, a, TH)
        self.assertEqual(len(gaps), 1)
        w0, w1 = gaps[0][2]
        n = len(a[int(w0 * SR):int(w1 * SR)])
        T.FAKE[n] = {'text': '', 'words': [dict(w, start=round(w['start'] - w0, 3), end=round(w['end'] - w0, 3)) for w in full['words']
                                           if w['start'] >= w0 - 0.01 and w['end'] <= w1 + 0.01]}
        return gaps

    def test_dropout_repaired_and_gate_passes(self):
        row, raw, full, drop = self._row()
        self.register = self._register_window(row, full)
        out = S.sync_level(self.d, [row], cache_dir=self.cache, model='medium')
        self.assertEqual(out['gate']['status'], 'PASS')
        self.assertEqual(len(out['gate']['asr_dropout_repairs']), 1)
        self.assertGreaterEqual(out['gate']['asr_dropout_repairs'][0]['repaired_words'], 8)
        st = out['gate']['token_match']['rows']['r1']
        self.assertGreaterEqual(st['n_match'] / st['n_tok'], 0.95)
        # warnings (low-confidence boundaries) are not polluted by the repair record
        self.assertFalse(any('repaired_words' in w for w in out['gate']['warnings']))

    def test_rerun_uses_cache_for_row_and_window(self):
        row, raw, full, drop = self._row()
        self._register_window(row, full)
        S.sync_level(self.d, [row], cache_dir=self.cache, model='medium')
        before = S.ASR_STATS['fake_calls']
        out2 = S.sync_level(self.d, [row], cache_dir=self.cache, model='medium')
        self.assertEqual(S.ASR_STATS['fake_calls'], before)                  # row + window both cached -> ASR 0
        self.assertEqual(out2['cost']['asr_transcribed'], 0)

    def test_unrecoverable_dropout_still_fails_gate(self):
        row, raw, full, drop = self._row(drop_n=10)
        a = S.load_audio(row['audio_path'])
        gaps = S.find_dropouts(T.FAKE[len(a)]['words'], a, TH)
        w0, w1 = gaps[0][2]
        T.FAKE[len(a[int(w0 * SR):int(w1 * SR)])] = {'text': '', 'words': []}      # window ASR also returns nothing
        with self.assertRaises(S.EnduserSyncError) as cm:
            S.sync_level(self.d, [row], cache_dir=self.cache, model='medium', thresholds={'en': {'min_ratio': 0.95, 'short_tokens': 0, 'short_max_miss': 0, 'short_min_ratio': 0.99}})
        self.assertEqual(cm.exception.code, 'ENDUSER_SYNC_TOKEN_MATCH')

    def test_no_dropout_no_extra_asr(self):
        sents = tok_sentences()
        row, raw = self.mk_row("r2", [" ".join(t) for t in sents])
        S.ASR_STATS['fake_calls'] = 0
        out = S.sync_level(self.d, [row], cache_dir=self.cache, model='medium')
        self.assertEqual(S.ASR_STATS['fake_calls'], 1)
        self.assertEqual(out['gate']['asr_dropout_repairs'], [])


if __name__ == '__main__':
    unittest.main()
