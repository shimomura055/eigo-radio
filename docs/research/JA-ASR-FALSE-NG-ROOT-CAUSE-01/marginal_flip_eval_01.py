import sys,json,os; sys.path.insert(0,'.'); sys.path.insert(0,'docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01')
import er007_ja_asr_validator_01 as javal; javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED=False
import er007_ja_secondary_asr_01 as sec
import proto_reading_compare_01 as P
cases=json.load(open('docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/ng_pool_cases_01.json',encoding='utf8'))
def prod_pass(c,t):
    r=javal.classify_ja_asr_match(c,t,allow_reading_resolver=False)
    if r.should_pass: return True,r.classification
    e=sec._numeric_value_equivalence(c,t,r)
    if e is not None: return True,e.classification
    return False,r.classification
flip=[];tot=0
for c in cases:
    if not c['canon']: continue
    for who in ('primary','secondary'):
        t=c[who]
        if not t: continue
        tot+=1
        ok0,cl=prod_pass(c['canon'],t)
        if ok0: continue
        ok,why=P.design_a(c['canon'],t)
        if ok: flip.append((c['file'].split('_output/')[1][:60],c['seg'],c['state'],who,why,cl,c['canon'][:40],t[:60]))
print(tot,'texts;',len(flip),'marginal flips over production(classify+numeric_equiv)')
for f in flip: print(f)
