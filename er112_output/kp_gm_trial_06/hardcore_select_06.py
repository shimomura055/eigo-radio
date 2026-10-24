# -*- coding: utf-8 -*-
"""委任_30 OF-KP2-01(b): 設計に使っていない新hard-core KP集合の事前固定(API 0、gloss出力は一切見ない)。結果非依存の基準:
 [H] held-out未使用: Trial_05 held-out選定順(heldout_selection_log_05.json selected)のうち、nheld=10で評価に使わなかった末尾4件(選定順で機械的に決まる)。
 [Z] Z小説(family=Z)の過去Production run由来KP(er112_kp_gm_kpset_03.candidates と同じ走査・除外規則)から、次を全て満たすもの:
     (z1) all_kps()115KP・PRE_A1_DROP・R hard-core 4KP・held-out選定14KP(使用10+未使用4)のいずれでもない
     (z2) key_phrase が上記使用済みKPを語として含まない/含まれない(例: 'rise above everyone's voices' は 'rise above' を含むので除外)
     (z3) 3語以上
     (z4) key_phrase に『字義でも文法が成立する具体物・身体・自然語』の合図語(下記CUE。本script作成時に固定)を含む
          = 字義訳が文法的に成立する型(hard-core型の構造的代理指標。意味の良否や本番gloss出力は参照しない)
     選定=key名ソート順、上限6件。
 出力: hardcore_set_06.json(KP詳細)、hardcore_select_log_06.json(基準・全候補・除外理由)。"""
import json, re, sys, collections
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')
import er112_kp_gm_kpset_03 as K3
import er112_kp_gm_trial_04 as X
import er112_kp_gm_trial_02 as T
OUT = "er112_output/kp_gm_trial_06/"
CUE = {"leg", "legs", "eye", "eyes", "face", "faces", "voice", "voices", "tear", "tears", "hand", "hands", "heart", "light", "rain",
       "water", "stick", "door", "window", "clock", "wall", "walls", "fire", "wind", "shadow", "shadows", "road", "river", "bridge", "knife"}
R4 = ["draw a line", "an unseen clock", "question shaped like a trophy", "greener grass"]
H = json.load(open("er112_output/kp_gm_trial_05/heldout_selection_log_05.json", encoding="utf-8"))
HSET5 = json.load(open("er112_output/kp_gm_trial_05/heldout_set_05.json", encoding="utf-8"))
A = X.all_kps()
used = set(A) | set(T.PRE_A1_DROP) | set(R4) | set(H["selected"])
reserved = H["selected"][10:]
words = lambda k: re.findall(r"[a-z']+", k.lower())


def overlaps(k, u):
    a, b = words(k), words(u)
    def has(x, y):
        return any(x[i:i + len(y)] == y for i in range(len(x) - len(y) + 1))
    return has(a, b) or has(b, a)


pool = K3.candidates(set(used))
log = dict(criteria=__doc__, CUE=sorted(CUE), reserved_heldout_unused=reserved, z_candidates=[], excluded={})
sel = []
for k in sorted(k for k, v in pool.items() if v["family"] == "Z"):
    w = words(k)
    why = None
    if any(overlaps(k, u) for u in used):
        why = "z2_overlap_with_used"
    elif len(w) < 3:
        why = "z3_fewer_than_3_words"
    elif not (set(w) & CUE):
        why = "z4_no_cue_word"
    if why:
        log["excluded"][k] = why
        continue
    sel.append(k)
log["z_selected_all"] = sel
sel = sel[:6]
out = {}
for k in reserved:
    v = dict(HSET5[k]); v["tier"] = "hc06_reserved"; v["src"] = "hardcore06"; out[k] = v
for k in sel:
    v = dict(pool[k]); v["tier"] = "hc06_z"; v["src"] = "hardcore06"; out[k] = v
log["selected"] = list(out)
log["n_pool_Z"] = sum(1 for v in pool.values() if v["family"] == "Z")
json.dump(out, open(OUT + "hardcore_set_06.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(log, open(OUT + "hardcore_select_log_06.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("selected", len(out), "(reserved %d + Z %d)" % (len(reserved), len(sel)), "Z pool", log["n_pool_Z"], "excluded", dict(collections.Counter(log["excluded"].values())))
for k, v in out.items():
    print(v["tier"], "|", k, "|", v["sent"][:90], "|", v["run"][-50:])
