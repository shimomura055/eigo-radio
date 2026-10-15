import netguard, tempfile, os, wave, json
import er006_secondary_asr_01 as sec
d=tempfile.mkdtemp(); p=os.path.join(d,'a.wav')
w=wave.open(p,'wb'); w.setnchannels(1); w.setsampwidth(1); w.setframerate(8000); w.writeframes(b'\0'*8000); w.close()
canon="Today's topic is A Fast Start and a Strong Finish: Hanshin Wins 8–1."
prim="Today's topic is a fast start and a strong finish. Hanshin wins 8-1."
azure="Today's topic is a fast start and a strong finish. Hanshin wins 8 to 1."
sec.get_full_text_via_azure_stt_with_phrase_list=lambda *a,**k:(azure,None)
sec._log_human_review=lambda d:None
import er005_cost_logger as cl
cl._LOG_PATH=os.path.join(d,'log.jsonl'); open(cl._LOG_PATH,'w').close()
r=sec.evaluate_attempt_with_cascade_detail(canon,prim,[],p,language="en-US",cascade_enabled=True,force_secondary=True)
print("OLD(main) verified=",r.get("verified"),"final_status=",r.get("final_status"),"steps=",[(s.get('step'),s.get('classification'),s.get('text')) for s in (r.get('steps') or [])])
