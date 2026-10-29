"""Run local faster-whisper (word timestamps) over all sentence-bearing segments of one article. usage: asr_batch_01.py <article_key> <model> [langs]"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))
from sync_common_01 import *
from asr_raw_01 import load_audio
from faster_whisper import WhisperModel
key, model = sys.argv[1], sys.argv[2]
langs = (sys.argv[3] if len(sys.argv) > 3 else 'en').split(',')
a, units = load_article(key)
m = WhisperModel(model, device='cpu', compute_type='int8', cpu_threads=4)
os.makedirs(os.path.join(ROOT, 'docs/research/END-USER-LISTENING-PAGE-PROTOTYPE-01/sync/_asr_raw'), exist_ok=True)
for u in units:
    if u['lang'] not in langs: continue
    out = os.path.join(ROOT, 'docs/research/END-USER-LISTENING-PAGE-PROTOTYPE-01/sync/_asr_raw/%s__%s__%s.json' % (key, u['key'], model))
    if os.path.exists(out): continue
    t0 = time.time(); au = load_audio(os.path.join(ROOT, u['mp3']))
    segs, info = m.transcribe(au, language=u['lang'], word_timestamps=True, beam_size=5, condition_on_previous_text=False, vad_filter=False)
    words, texts = [], []
    for s in segs:
        texts.append(s.text)
        for w in (s.words or []): words.append({'w': w.word, 'start': round(w.start, 3), 'end': round(w.end, 3), 'p': round(w.probability, 3)})
    json.dump({'mp3': u['mp3'], 'model': model, 'lang': u['lang'], 'duration': round(len(au) / 16000, 3), 'text': ''.join(texts).strip(), 'words': words},
              open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(key, u['key'], len(words), round(time.time() - t0, 1), flush=True)
