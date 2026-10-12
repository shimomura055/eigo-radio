"""FAMILY-Z-MELOS-CONNECTED-SPEECH-ROOT-CAUSE-AUDIT-01: オフライン再評価(API 0、TTS 0、既存ログと純関数のみ)。
(1) 実データ走査: HR queue(canonical+全step転写)とer021 telemetry(canonical/asr)の実対を、Production関数で再評価。
(2) 合成対照マトリクス: 同一子音境界/固有名詞+動詞/一般名詞+動詞/非接尾辞/真の誤発音/無関係置換。
(3) 仮説規則A'(stem同音: ASR語のCMU音素 == canonical語から-s/-es接尾辞を除いたstemのCMU音素)の何件が追加救済され、
    何件が誤PASSリスクかを机上評価(A'はこのscript内のみ、Productionには未導入)。
Production関数は全て無変更で呼ぶのみ。"""
import json, sys, os, re, collections
sys.path.insert(0, ".")
import er006_preprod_hardening_01_validation as val
import er011_b1_connected_speech_validator_01 as csv3
import er011_connected_speech_equivalence_layer_production_01 as eq
import er021_en_asr_semantic_equivalence_production_01 as _se
# classify_asr_match(role適用)は不合格時に共有telemetry.jsonlへ追記する。再評価の副作用を防ぐため無効化する
# (注: 初回実行時はこの無効化が無く、共有telemetryへ再評価分が追記された。CS_AUDIT_01.md参照)。
_se.append_telemetry_log = lambda *a, **k: None

OUTDIR = os.path.dirname(os.path.abspath(__file__))
ROLE_SEG = "full_story_part1"

def stem_candidates(w):
    w = w.lower().strip(".,!?;:\"'")
    c = []
    if w.endswith("ies") and len(w) > 4: c.append(w[:-3] + "y")
    if w.endswith("es") and len(w) > 3: c.append(w[:-2])
    if w.endswith("s") and len(w) > 2: c.append(w[:-1])
    return c

def hypothetical_A_prime(canon, asr):
    """仮説規則A'(未導入): 最初の食い違い語(c_word, a_word)について、c_wordが-s/-es形で次語頭が歯擦音、
    かつa_wordのCMU音素列がc_wordのstem候補のCMU音素列と完全一致(綴りは問わない)。"""
    diff = csv3.word_diff(canon, asr)
    if not diff or diff.get("canonical_word") is None or diff.get("asr_word") is None or diff.get("next_word") is None:
        return None
    c, a, nx = diff["canonical_word"], diff["asr_word"], diff["next_word"]
    if csv3.initial_sound(nx) not in csv3.SIBILANTS: return None
    if csv3.final_s_sound(c) not in csv3.SIBILANTS: return None
    ap = eq.word_phones(a)
    if not ap: return None
    for st in stem_candidates(c):
        sp = eq.word_phones(st)
        if sp and sp == ap:
            return {"c_word": c, "a_word": a, "stem": st, "stem_phones": sp}
    return None

def row(canon, asr, label=""):
    cls = val.classify_asr_match(canon, asr, segment_id=ROLE_SEG)
    cs = csv3.classify_connected_speech(canon, asr)
    e = eq.classify_connected_speech_equivalence(canon, asr)
    diffs = cls.protected.content_word_diffs
    return {
        "label": label, "canonical": canon, "asr": asr, "classification": cls.classification, "should_pass": cls.should_pass,
        "entity_diff": any(d.get("entity_like") for d in diffs),
        "cs_validator": cs["new_judgment"], "cs_rule": cs.get("rule"),
        "equivalence_cheap": e["layer_judgment"],
        "shadowed_by_entity_gate": (cls.classification == "ASR_VALIDATION_UNCERTAIN" and cs["new_judgment"] in
                                    ("CONNECTED_SPEECH_ACCEPT", "CONNECTED_SPEECH_RESEGMENTATION")),
        "A_prime": hypothetical_A_prime(canon, asr),
    }

# ---------- (1) 実データ ----------
pairs = {}
for l in open("er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl", encoding="utf-8"):
    try: d = json.loads(l)
    except Exception: continue
    c = d.get("canonical_text")
    for s in d.get("steps", []):
        if s.get("text") and c: pairs[(c, s["text"])] = "HRqueue:" + s.get("step", "")
# er021 telemetry は本監査の初回実行前の行数(7155行)までを実データとして使う(それ以降は本監査自身の再評価が
# 追記した重複行と他agentの追記が混在するため除外)。
for _n, l in enumerate(open("er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl", encoding="utf-8")):
    if _n >= 7155: break
    try: d = json.loads(l)
    except Exception: continue
    if d.get("canonical") and d.get("asr"): pairs.setdefault((d["canonical"], d["asr"]), "er021_telemetry")
real = [row(c, a, src) for (c, a), src in pairs.items() if c.strip() != a.strip()]

# CS環境該当(最初の食い違い語がs/es終わりで次語頭が歯擦音、または-ed終わりで次語頭が破裂音)
def cs_env(r):
    diff = csv3.word_diff(r["canonical"], r["asr"])
    if not diff or not diff.get("canonical_word") or not diff.get("next_word"): return None
    c, nx = diff["canonical_word"], diff["next_word"]
    if csv3.final_s_sound(c) in csv3.SIBILANTS and csv3.initial_sound(nx) in csv3.SIBILANTS: return "sibilant_boundary"
    if csv3.final_ed_sound(c) in csv3.STOPS_ALVEOLAR and csv3.initial_sound(nx) in csv3.STOPS_ALVEOLAR: return "stop_boundary"
    return None
env_rows = [dict(r, env=cs_env(r)) for r in real if cs_env(r)]
summary_real = {
    "n_pairs": len(real),
    "n_cs_environment": len(env_rows),
    "cs_environment_by_classification": collections.Counter(r["classification"] for r in env_rows),
    "cs_environment_by_cs_validator": collections.Counter(r["cs_validator"] for r in env_rows),
    "n_shadowed_by_entity_gate": sum(1 for r in real if r["shadowed_by_entity_gate"]),
    "n_A_prime_candidates": sum(1 for r in real if r["A_prime"]),
}

# ---------- (2) 合成対照 ----------
S = [
 # 固有名詞+動詞(語末s + 歯擦音語頭)
 ("Melos said.", "Melo said.", "proper_noun_exact_stem_drop"),
 ("Melos said.", "Mello said.", "proper_noun_stem_homophone_spelling(今回)"),
 ("Melos said.", "Mellow said.", "proper_noun_stem_homophone_spelling(今回)"),
 ("Melos said.", "Melon said.", "COUNTER_real_mispronunciation_or_other_word"),
 ("Melos said.", "Marcus said.", "COUNTER_unrelated_name"),
 ("Melos said.", "Melody said.", "COUNTER_unrelated_word"),
 ("Marcus smiled.", "Marcu smiled.", "proper_noun_exact_stem_drop"),
 ("Marcus smiled.", "Markus smiled.", "proper_noun_variant_spelling_full_s_present"),
 ("Marcus smiled.", "Marker smiled.", "COUNTER_unrelated"),
 ("Chris saw him.", "Kris saw him.", "proper_noun_variant_spelling_s_present"),
 ("Chris saw him.", "Cree saw him.", "proper_noun_s_dropped_variant_spelling"),
 ("Thomas sat down.", "Thoma sat down.", "proper_noun_exact_stem_drop"),
 ("Dionysius spoke.", "Dionysia spoke.", "proper_noun_other"),
 # 一般名詞+動詞
 ("The studies suggest a link.", "The study suggests a link.", "general_noun_PatternA(承認済み)"),
 ("The bosses said so.", "The boss said so.", "general_noun_exact_stem_drop"),
 ("The classes started late.", "The class started late.", "general_noun_exact_stem_drop"),
 ("The glasses sit there.", "The glass sit there.", "general_noun_exact_stem_drop"),
 # 語尾が接尾辞でない最終子音の連続
 ("The bus stops here.", "The bu stops here.", "non_suffix_final_consonant"),
 ("This school starts soon.", "This schoo starts soon.", "non_suffix_final_consonant"),
 ("A nice sign.", "A nigh sign.", "non_suffix_final_consonant"),
 ("He opened the door.", "He open the door.", "PatternB_not_applicable_nextword"),
 ("He opened to them.", "He open to them.", "PatternB(承認済み)"),
 # 本当に語尾を誤発音した反例 / 無関係置換
 ("The studies suggest a link.", "The studio suggests a link.", "COUNTER_real_error_other_word"),
 ("The bosses said so.", "The bonus said so.", "COUNTER_unrelated"),
 ("The cities seem calm.", "The city seem calm.", "general_noun_ies_drop"),
]
synth = [row(c, a, lab) for c, a, lab in S]

res = {"summary_real": summary_real, "env_rows": env_rows, "synthetic": synth,
       "shadowed_rows": [r for r in real if r["shadowed_by_entity_gate"]],
       "A_prime_rows": [r for r in real if r["A_prime"]]}
json.dump(res, open(os.path.join(OUTDIR, "cs_offline_reeval_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print(json.dumps(summary_real, ensure_ascii=False, indent=1, default=str))
print("--- synthetic ---")
for r in synth:
    print(f"{r['label'][:46]:46s} | {r['canonical']!r} <- {r['asr']!r} | cls={r['classification']} pass={r['should_pass']} entity={r['entity_diff']} cs={r['cs_validator']} eq={r['equivalence_cheap']} A'={'Y' if r['A_prime'] else '-'} shadow={r['shadowed_by_entity_gate']}")
print("--- real: env rows ---")
for r in env_rows[:40]:
    print(r["env"], "|", r["label"], "|", repr(r["canonical"])[:70], "<-", repr(r["asr"])[:70], "|", r["classification"], r["cs_validator"], "A'" if r["A_prime"] else "")

# ---------- (4) 系統的スイープ: 固有名詞(-s/-es終わり)+歯擦音語頭の次語。ASR=(a)stem完全一致(接尾辞脱落) (b)stem同音の別綴り ----------
NAMES = [("Melos","Melo",["Mello","Mellow"]), ("Marcus","Marcu",["Markus"]), ("Thomas","Thoma",["Tomma"]),
         ("Dionysius","Dionysiu",["Dionysia"]), ("Brutus","Brutu",["Brootu"]), ("Jesus","Jesu",["Jezu"]),
         ("Chris","Chri",["Cree"]), ("James","Jame",["Jaim"]), ("Lucas","Luca",["Looka"]), ("Atlas","Atla",["Atlah"]),
         ("Hades","Hade",["Hayde"]), ("Paris","Pari",["Parry"]), ("Silas","Sila",["Seela"]), ("Judas","Juda",["Judah"]),
         ("Nicholas","Nichola",["Nicola"]), ("Carlos","Carlo",["Carlo"]), ("Venus","Venu",["Venew"]), ("Orpheus","Orpheu",["Orfew"])]
NEXT = ["said", "spoke", "smiled", "sat", "saw", "stood"]
sweep = []
for full, stem, variants in NAMES:
    for nx in NEXT:
        c = f"{full} {nx}."
        for kind, asr_name in [("exact_stem_drop", stem)] + [("stem_variant_spelling", v) for v in variants]:
            r = row(c, f"{asr_name} {nx}.", f"{kind}:{full}")
            r["kind"] = kind; sweep.append(r)
agg = collections.defaultdict(collections.Counter)
for r in sweep:
    agg[r["kind"]][("PASS" if r["should_pass"] else "NOT_PASS", r["classification"], "A'" if r["A_prime"] else "-")] += 1
res["sweep_summary"] = {k: {str(kk): vv for kk, vv in v.items()} for k, v in agg.items()}
res["sweep_rows"] = sweep
res["sweep_shadowed"] = sum(1 for r in sweep if r["shadowed_by_entity_gate"])
json.dump(res, open(os.path.join(OUTDIR, "cs_offline_reeval_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("--- sweep ---")
for k, v in agg.items():
    print(k, dict(v))
print("sweep_shadowed_by_entity_gate:", res["sweep_shadowed"])
for r in sweep:
    if r["kind"] == "exact_stem_drop" and not r["should_pass"]:
        print("exact-stem-drop NOT PASS:", r["canonical"], "<-", r["asr"], r["classification"])
