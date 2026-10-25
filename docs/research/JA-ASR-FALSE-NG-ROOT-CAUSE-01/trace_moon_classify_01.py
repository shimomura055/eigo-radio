import sys; sys.path.insert(0,'.')
import er007_ja_asr_validator_01 as j
import er003_audio_tts_asr_safety as s
j.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED=False
C='月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密'
T={'p1':'月野詩は8000句800本超え。その奥に潜む岩の上着の秘密。','p2':'月の死は八千九百本超。その奥に潜む岩の上着の秘密。','a2':'月の詩は8900本超。その奥に潜む岩の上着の秘密。','p3':'月の氏は8000900本超。その奥に潜む岩の上着の秘密。'}
cn=j.normalize_ja(C); print('canon norm',cn)
for k,t in T.items():
    r=j.classify_ja_asr_match(C,t,allow_reading_resolver=False)
    an=j.normalize_ja(t)
    print('---',k,an); print(r.classification,round(r.similarity_ratio,3),r.reason[:400])
    print(' numm',r.protected.number_mismatches,'diffs',r.protected.content_diffs)
    print(' kakasi canon',s._kakasi_reading(cn),'| asr',s._kakasi_reading(an))
    print(' hira',j._hira_reading(cn),'|',j._hira_reading(an))
