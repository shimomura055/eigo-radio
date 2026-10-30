import json,sys,shutil,os
sys.path.insert(0,r'C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\7eda59a9-ca6c-4f6c-9eb5-2b973c0ca046\scratchpad\wt')
import er135_enduser_translate_01 as T
R=r'C:\Users\tensh\eigo-radio'
cases={'melos':('family_z_melos_kphr_evidence_r3',R+r'\er026_output\family_z_production_e2e_01\melos\run_p2_evidence_r3\enduser_sync_cache','adv','adv_14'),
       'yuki':('family_z_yuki_onna_01',R+r'\er026_output\family_z_production_e2e_01\yuki_onna\run_yo_prod_01\enduser_sync_cache','std','std_11')}
name=sys.argv[1]; dry=len(sys.argv)>2 and sys.argv[2]=='dry'
d,cache,lv,key=cases[name]
a=json.load(open(rf'{R}\user_test\{d}\enduser\data\article.json',encoding='utf8'))
p=[p for p in a['levels'][lv]['parts'] if p['key']==key][0]
sents=[{'sid':s['sid'],'en':s['text'],'para':pi} for pi,pa in enumerate(p['paragraphs']) for s in pa]
print(name,'kind',p['kind'],'sents',len(sents),'paras',len(p['paragraphs']),'has_ja',bool(p.get('ja')))
work=rf'C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\7eda59a9-ca6c-4f6c-9eb5-2b973c0ca046\scratchpad\ejh04\cache_{name}'
if os.path.exists(work): shutil.rmtree(work)
os.makedirs(work); shutil.copy(cache+r'\ja_generated.json',work)
before=json.load(open(work+r'\ja_generated.json',encoding='utf8'))
if dry:
    for pa in p['paragraphs']: print(len(pa), T.para_key([{'sid':s['sid'],'en':s['text']} for s in pa]) in before['entries'])
    sys.exit()
class Rec(T.DefaultLLM):
    def __call__(self,kind,prompt):
        t=super().__call__(kind,prompt)
        open(work+r'\log.jsonl','a',encoding='utf8').write(json.dumps({'kind':kind,'prompt':prompt,'resp':t},ensure_ascii=False)+'\n')
        return t
llm=Rec()
res=T.translate_part(f'{lv}:{key}',sents,level=lv,family='Z',cache_dir=work,llm=llm)
json.dump({'res':res,'calls':[{k:v for k,v in c.items()} for c in llm.calls]},open(work+r'\result.json','w',encoding='utf8'),ensure_ascii=False,indent=1,default=str)
print(json.dumps(res['coverage']),json.dumps(res['meta'],ensure_ascii=False)[:1500])
