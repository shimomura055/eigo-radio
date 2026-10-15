import sys, json; sys.path.insert(0,'.')
import er006_secondary_asr_01 as secondary, er008_disfluency_qa_18 as dq, er021_en_asr_semantic_equivalence_production_01 as _se
_se.append_telemetry_log = lambda *a, **k: None
def run(c, p, sec_text, seg, local_text=None, eq=True):
    o1, o2 = secondary.get_full_text_via_azure_stt_with_phrase_list, dq.transcribe_verbatim
    n = {"s":0,"l":0}
    def s(*a, **k): n["s"]+=1; return sec_text, None
    def l(*a, **k): n["l"]+=1; return [{"text": w} for w in (local_text or sec_text).split()]
    secondary.get_full_text_via_azure_stt_with_phrase_list = s; dq.transcribe_verbatim = l
    try:
        r = secondary.evaluate_attempt_with_cascade_detail(c, p, [], "dummy.wav", cascade_enabled=True, enable_connected_speech_equivalence_layer=eq, segment_id=seg)
    finally:
        secondary.get_full_text_via_azure_stt_with_phrase_list, dq.transcribe_verbatim = o1, o2
    a = r["asr_judgement"]
    return dict(verified=r["verified"], state=a["state"], reason=a["reason_code"], prim_passed=a["primary"]["passed"], prim_label=a["primary"]["label"], layers=a["adapter"]["layers"], eq_invoked=r["connected_speech_equivalence_layer_invoked"], calls=n, warnings=a.get("warnings"))
C="The studies suggest cats today."; P="The study suggests dogs today."
for seg in ("full_story_part1", None):
    print("F1 user ex seg",seg, "supporting secondary:", run(C,P,C,seg))
    print("F1 user ex seg",seg, "non-supporting secondary(=primary):", run(C,P,P,seg))
c2="Young travelers still showed strong interest in the results."; p2="Young travelers still show strong interest in the outcomes."
for seg in ("full_story_part1", None):
    print("F1 multi seg",seg, "supporting:", run(c2,p2,c2,seg))
    print("F1 multi seg",seg, "non-supporting:", run(c2,p2,p2,seg))
c3="The cars turned back before reaching the bridge."; p3="The cars turn back before reaching the bridge."
print("CS mixed supporting-sec/local-primary:", run(c3,p3,c3,"full_story_part1",local_text=p3))
print("CS mixed non-supporting:", run(c3,p3,p3,"full_story_part1",local_text=p3))
