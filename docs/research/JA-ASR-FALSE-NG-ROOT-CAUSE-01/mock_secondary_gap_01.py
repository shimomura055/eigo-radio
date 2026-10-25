import sys,wave,os,json; sys.path.insert(0,'.')
import er007_ja_asr_validator_01 as javal; javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED=False
import er007_ja_secondary_asr_01 as s
wav=os.environ['TEMP']+'/mock.wav'
w=wave.open(wav,'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000); w.writeframes(b'\x00\x00'*16000*3); w.close()
def run(canon,prim,sec):
    s._azure_stt_strict=lambda p,language='ja-JP',timeout_seconds=90: (sec,None)
    r=s.evaluate_attempt_ja_with_cascade_detail(canon,prim,wav,cascade_enabled=True,attempt_ctx={'max_len':200})
    a=r['asr_judgement']; print(a['state'],a['reason_code'],'| sec.label=',a['secondary']['label'],'| sec text=',a['secondary']['text'])
run('三人で、お店に行きます','三人で駅に行きます','3人で、お店に行きます')       # numeric notation only
run('三人で、お店に行きます','三人で駅に行きます','三人でお店に行きます')       # exact (control)
run('月のしわ、8,900本超','月の死は八千九百本超','月の詩は8900本超')               # moon attempt2 replica
