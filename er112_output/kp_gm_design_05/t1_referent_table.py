"""T-1: 所有格を含む見出し語の本文の指示対象(目視ラベル)と、正規形の一致/不一致を集計 (API 0)。
referent: self=動詞句の主語自身の所有(one's)/ other=主語とは別の人(someone's)/ nonperson=人でない所有者(its等)
gold_class: 慣習上正しい一般形 one's / someone's / keep(一般化しない/the等)"""
import json,glob,re,os,collections
REF={ # display_phrase -> (referent, 根拠)
 "pumps its fist":("self","its=your wallet(擬人化)=動詞の主語自身 -> pump one's fist 可"),
 "pump its fist":("self","同上"),
 "in your place":("other","he will die in your place: 主語heとは別人(あなた) -> someone's"),
 "held out his hands":("self","his=主語his friend自身"),
 "go out of their way":("self","their=主語they自身"),
 "brace yourself for":("self","再帰(oneself)"),
 "reach for your wallet":("self","make you reach for your wallet: 動作主=you自身"),
 "kept you company":("other","目的格you(規則5=someone領域): 主語Veraとは別人"),
 "told her the truth":("other","目的格her(規則5): 主語Tomとは別人"),
 "lose her job":("self","She ... lose her job: 主語自身"),
 "shock your wallet":("other","its price shocks your wallet: 主語price(非人)とは別、読者の財布 -> someone's"),
 "apply its findings":("nonperson","its=研究(人でない)。主語weとも別"),
 "use its results":("nonperson","its=研究"),
 "at their own pace":("self","their=主語young people"),
 "room for their own pace":("self","同上"),
 "a place of my own":("self","me自身"),
 "change my surroundings":("self","I自身"),
 "make something your whole life":("self","命令文の主語you(動作主)"),
 "occupy their thoughts":("self","students自身"),
 "give my word":("self","I自身"),"my word":("self","I自身"),
 "catch your breath":("self","動作主自身"),"catch my breath":("self","I自身"),
 "choose their words":("self","some people自身"),
 "turned on its head":("nonperson","its=hope(非人)"),
 "catch their attention":("other","their=聞き手(主語soundとは別)"),
 "a piece of your attention":("other","notification takes ... your attention: 主語は通知(非人)、所有者=読者"),
 "compete through its presence":("nonperson","its=silent phone"),
 "enforce their rules":("nonperson","their=places(店・場所=組織)"),
 "out of our hands":("self_group","our=話者側(we)"),
 "find its way back":("nonperson","its=personal desk"),
 "look her in the face":("other","her=別の人(相手)"),
 "before you know it":("keep","定型(you固定)"),
 "between you and me":("keep","定型(you and me固定)"),
}
def cls(kp):
    k=kp.lower()
    if re.search(r"\bone's\b|\boneself\b",k): return "one's"
    if re.search(r"\bsomeone's\b|\bsomebody's\b|\bsomeone\b|\bsomebody\b",k): return "someone's"
    return "kept"
items=json.load(open("er112_output/kp_gm_design_05/t1_possessive_items.json",encoding="utf-8"))
tab=collections.defaultdict(collections.Counter); det=[]
for r in items:
    ref=REF.get(r["display"])
    if ref is None: det.append(("UNLABELED",r["display"])); continue
    c=cls(r["kp"]); referent=ref[0]
    if c=="kept": continue
    gold={"self":"one's","self_group":"one's","other":"someone's","nonperson":"nonperson-NA","keep":"keep"}[referent]
    ok = (gold==c) or (gold=="one's" and c=="one's")
    tab[(referent,c)][r["display"]+" => "+r["kp"]]+=1
    det.append((referent,c,"OK" if ok else "MISMATCH",r["display"],r["kp"],r["nfiles"]))
for d in det: print(d)
print()
for k,v in sorted(tab.items()): print(k,len(v),"distinct")
