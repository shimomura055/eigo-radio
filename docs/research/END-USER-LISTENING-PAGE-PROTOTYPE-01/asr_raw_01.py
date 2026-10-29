"""Local faster-whisper word-timestamp ASR for published segment mp3 (API 0, no audio regeneration).
usage: .venv/Scripts/python.exe asr_raw_01.py <mp3> <out.json> [model] [lang]"""
import sys, json, time, numpy as np, av
from faster_whisper import WhisperModel

def load_audio(path, sr=16000):
    c = av.open(path); st = c.streams.audio[0]
    rs = av.AudioResampler(format='fltp', layout='mono', rate=sr)
    out = []
    for f in c.decode(st):
        for g in rs.resample(f):
            out.append(g.to_ndarray()[0])
    for g in rs.resample(None): out.append(g.to_ndarray()[0])
    return np.concatenate(out).astype(np.float32)

if __name__ == '__main__':
    mp3, outp = sys.argv[1], sys.argv[2]
    model_name = sys.argv[3] if len(sys.argv) > 3 else 'medium'
    lang = sys.argv[4] if len(sys.argv) > 4 else 'en'
    t0 = time.time()
    a = load_audio(mp3)
    m = WhisperModel(model_name, device='cpu', compute_type='int8')
    segs, info = m.transcribe(a, language=lang, word_timestamps=True, beam_size=5,
                              condition_on_previous_text=False, vad_filter=False)
    words = []; texts = []
    for s in segs:
        texts.append(s.text)
        for w in (s.words or []):
            words.append({'w': w.word, 'start': round(w.start, 3), 'end': round(w.end, 3), 'p': round(w.probability, 3)})
    json.dump({'mp3': mp3, 'model': model_name, 'lang': lang, 'duration': round(len(a) / 16000, 3),
               'text': ''.join(texts).strip(), 'words': words, 'elapsed': round(time.time() - t0, 1)},
              open(outp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(outp, len(words), 'words', round(time.time() - t0, 1), 's')
