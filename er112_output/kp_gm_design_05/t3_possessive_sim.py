"""T-3 (API 0): 提案の決定論部分(possessor_role -> 見出し語写像/validator修復)を既存45件で再計算。
role=T-1の目視ラベル(LLMのrole判定精度は未測定=次Trialの測定対象)。"""
import json,re,io,contextlib,importlib.util
spec=importlib.util.spec_from_file_location('rt','er112_output/kp_gm_design_05/t1_referent_table.py')
with contextlib.redirect_stdout(io.StringIO()):
    rt=importlib.util.module_from_spec(spec); spec.loader.exec_module(rt)
ROLE={"self":"same_as_subject","self_group":"same_as_subject","other":"different_person","nonperson":"not_a_person","keep":"fixed_expression"}
POSS=r"\b(my|your|his|her|their|our|its)\b"
def repair(display,kp,role):
    """LLMが書いたkpに対する決定論修復。role別の許可集合に収まらない人称placeholderだけを直す。"""
    k=kp
    if role=="same_as_subject":
        return re.sub(r"\b(someone's|somebody's)\b","one's",k)
    if role=="different_person":
        return re.sub(r"\bone's\b","someone's",k)
    if role=="not_a_person":
        # placeholder化されていたら、元の所有格(display側)へ戻す(語数不変の1対1置換のみ)
        if re.search(r"\b(one's|someone's|somebody's)\b",k):
            m=re.search(POSS,display.lower())
            return re.sub(r"\b(one's|someone's|somebody's)\b",m.group(1) if m else "",k)
    return k
items=json.load(open('er112_output/kp_gm_design_05/t1_possessive_items.json',encoding='utf-8'))
chg=0;tot=0
for r in items:
    role=ROLE[rt.REF[r['display']][0]]
    new=repair(r['display'],r['kp'],role)
    if rt.cls(r['kp'])=='kept': continue
    tot+=1
    if new!=r['kp']:
        chg+=1
        print("CHANGE |",r['display'],"|",r['kp'],"->",new,"|",role,"| sent:",r['sent'][:90],"| copies",r['nfiles'])
print("generalized rows",tot,"changed",chg)
