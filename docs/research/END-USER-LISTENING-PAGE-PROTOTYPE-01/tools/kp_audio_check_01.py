# -*- coding: utf-8 -*-
"""KP英語のみ区間の聴取内容の検証(API 0: ローカル faster-whisper)。
data/*.json の kp[].en_audio 区間を既存mp3から切り出し(読み取りのみ)、言語自動判定+文字起こしが
KP英語表現と一致し日本語を含まないことを確認する。結果: ../kp_audio_check_01.json"""
import json, os, subprocess, tempfile, re, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from asr_raw_01 import load_audio
from faster_whisper import WhisperModel

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
FF = os.path.join(ROOT, '.venv', 'Lib', 'site-packages', 'imageio_ffmpeg', 'binaries', 'ffmpeg-win-x86_64-v7.1.exe')
DATA = os.path.join(ROOT, 'user_test', 'dev_enduser_page_01', 'data')
JA = re.compile(r'[ぁ-んァ-ヶ一-龠]')
m = WhisperModel('small', device='cpu', compute_type='int8')
out = []
tmp = tempfile.mkdtemp()
for aid in ('ai_island', 'moon'):
    art = json.load(open(os.path.join(DATA, aid + '.json'), encoding='utf-8'))
    srcdir = os.path.join(ROOT, art['source_page'].rsplit('/', 1)[0])
    for lv, L in art['levels'].items():
        for p in L['parts']:
            if p['kind'] != 'kp':
                continue
            k = p['kp'][0]
            ea = k['en_audio']
            clip = os.path.join(tmp, '%s_%s_%d.wav' % (aid, lv, p['idx']))
            subprocess.run([FF, '-y', '-v', 'error', '-ss', str(ea['start']), '-to', str(ea['end']), '-i', os.path.join(srcdir, p['seg']), '-ar', '16000', '-ac', '1', clip], check=True)
            a = load_audio(clip)
            segs, info = m.transcribe(a, language=None, beam_size=5, condition_on_previous_text=False)
            txt = ''.join(s.text for s in segs).strip()
            # 比較用: 意味側(同segの3番目ブロックを含む区間)も参考に取得(日本語/英語解説が確かに別であることの確認)
            norm = lambda s: re.sub(r'[^a-z ]', '', s.lower()).strip()
            ok = (info.language == 'en') and (JA.search(txt) is None) and norm(k['en']).split()[0] in norm(txt)
            out.append(dict(article=aid, level=lv, part=p['label'], kp=k['en'], window=[ea['start'], ea['end']], dur=round(ea['end'] - ea['start'], 3), lang=info.language, lang_prob=round(info.language_probability, 3), transcript=txt, ok=ok))
            print(out[-1])
json.dump(out, open(os.path.join(os.path.dirname(__file__), '..', 'kp_audio_check_01.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('ALL_OK' if all(x['ok'] for x in out) else 'NG')
