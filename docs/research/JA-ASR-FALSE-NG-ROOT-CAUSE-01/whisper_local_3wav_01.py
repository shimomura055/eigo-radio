import sys,json,time
from faster_whisper import WhisperModel
A='er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_ms_03/a2/narration/attempts/'
fs=['japanese_title_attempt1_customb8f0ff16.wav','japanese_title_attempt2_customb8f0ff16.wav','japanese_title_attempt3_minimalfallback.wav']
out={}
for size in ['small','medium']:
    m=WhisperModel(size,device='cpu',compute_type='int8')
    for f in fs:
        t=time.time()
        segs,info=m.transcribe(A+f,language='ja',beam_size=5)
        txt=''.join(s.text for s in segs)
        out[f"{size}:{f}"]=txt; print(size,f,txt,round(time.time()-t,1),flush=True)
json.dump(out,open(sys.argv[1],'w',encoding='utf8'),ensure_ascii=False,indent=1)
