import sys,os,json,re,collections
sys.path.insert(0,os.getcwd())
import er006_preprod_hardening_01_validation as val
import pronouncing
D='docs/research/PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01/'
pairs=[json.loads(l) for l in open(D+'pairs_02.jsonl',encoding='utf8')]
def art(src):
    src=src.replace(chr(92),'/'); src=src.split(':')[0]; parts=[x for x in src.split('/') if not re.match(r'(audit|b1b|a2|b1|narration|parts?|segments?|results?|raw|evidence|attempts?|tts_generation_results.json|human_review_queue.jsonl|runtime|fixtures.*|.*\.(json|jsonl|wav|txt|md))$',x)]; parts=[re.sub(r'(__)?run_[A-Za-z0-9_()]+$','',x) for x in parts]; parts=[x for x in parts if x]; return '/'.join(parts[:3])
allart=set(); oovart=collections.defaultdict(set); entart=collections.defaultdict(set); names=collections.Counter()
nodiff=0
for p in pairs:
    c=p['canonical']
    if re.search(r'[\u3040-\u30ff\u4e00-\u9fff]',c): continue
    ar={art(s) for s in p['sources']}
    allart|=ar
    try: r=val.classify_asr_match(c,p['asr'])
    except Exception as e: continue
    if r.should_pass: continue
    for d in r.protected.content_word_diffs:
        cw=d['canonical'].split()
        oov=[w for w in cw if not pronouncing.phones_for_word(w)]
        if oov:
            for w in oov:
                names[w]+=1; oovart[w]|=ar
        if d['entity_like']:
            for w in cw: entart[w]|=ar
tot=len(allart)
a_oov=set().union(*oovart.values()) if oovart else set()
a_ent=set().union(*entart.values()) if entart else set()
print('article-ish dirs',tot,'with OOV-canonical unpassed diff',len(a_oov),'with entity-like unpassed diff',len(a_ent))
print('distinct OOV names with unpassed diff',len(oovart))
print(sorted(((w,len(a)) for w,a in oovart.items()),key=lambda x:-x[1])[:30])
json.dump({'article_dirs':tot,'dirs_with_oov_unpassed':len(a_oov),'dirs_with_entity_unpassed':len(a_ent),'oov_names':{w:len(a) for w,a in oovart.items()}},open(os.environ['SCRATCH_OUT'],'w'))
