"""PNMH-PLAN-01: Trialケース表のオフライン事前測定(API 0)。実例(pairs_01.jsonl由来)と合成carrier文を現行/提案で判定。
出力: TRIAL_CASES_01.json と標準出力(markdown行)。expect: PASS=救済すべき正例 / NOT_PASS=誤PASSしてはならない負例 / KEEP=現行判定を維持"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import proto_multiword_span_01 as P
val = P.val
import er006_secondary_asr_01 as sec
pairs = [json.loads(l) for l in open(os.path.join(HERE, "pairs_01.jsonl"), encoding="utf8")]

def judge(c, a):
    r = val.classify_asr_match(c, a)
    if r.should_pass: return "PASS(" + r.classification + ")"
    if sec.is_entity_like_mismatch(r) or sec.is_homophone_candidate_mismatch(r):
        lab = sec._step_alternate_pass(r)
        if lab: return "PASS(" + lab + ")"
    return "NOT_PASS(" + r.classification + ")"

def find(pred, engine=None):
    for p in pairs:
        if (engine is None or engine in p["engines"]) and pred(p): return p
    return None

CARR = "LINE Manga has launched byUs, an AI service that lets you shape stories."
def carrier(span_asr): return CARR.replace("byUs", span_asr)
cases = []
def add(cid, kind, canon, asr, expect, basis, origin, stage="O+P"):
    cases.append(dict(id=cid, kind=kind, canonical=canon, asr=asr, expect=expect, label_basis=basis, origin=origin, stage=stage))

# --- 実例(pairs_01由来) ---
def real(cid, kind, expect, basis, pred, engine=None):
    p = find(pred, engine)
    if p is None: print("MISSING", cid); return
    add(cid, kind, p["canonical"], p["asr"], expect, basis, "実保存転写:" + p["sources"][0][:110])
import re
def has_asr(p, pat): return re.search(pat, p["asr"], re.I) is not None
def has_c(p, s): return s in re.sub(r"[^a-z]", "", p["canonical"].lower())
real("M1", "1語⇔複数語(正例)", "PASS", "音韻定義: byus=B AY1 AH0 S, buy us=B AY1+AH1 S(ストレス無視で一致)。ただしbyUs自体の公式発音は未確認(J7依存)", lambda p: has_c(p, "byus") and has_asr(p, r"\bbuy us\b") and "secondary" in p["engines"] and p["n_src"] >= 1, "secondary")
real("M2", "1語⇔複数語(正例)", "PASS", "同上(Primary転写)", lambda p: has_c(p, "byus") and has_asr(p, r"\bbuy us\b") and "primary" in p["engines"], "primary")
real("M3", "1語⇔複数語+他差分(Azure by us)", "KEEP", "span自体は空白差(HEADで吸収)。ペアは他差分(and脱落・was→with・a way→away)があるためNG維持が正(提案でも変わらないことを確認)", lambda p: has_c(p, "byus") and has_asr(p, r"\bby us\b") and "secondary" in p["engines"] and "away" in p["asr"].lower())
add("M4", "1語⇔複数語(正例・一般語、綴り違い)", "It is already late.", "It is all ready late.", "PASS", "音韻定義: already=AO2 L R EH1 D IY0, all ready=AO1 L+R EH1 D IY0(CMU、ストレス無視で一致)。一般語への適用域の確認(空白差ではなく綴り違い)", "合成")
add("M7", "1語⇔複数語(正例・同一spanが他の1:1同音差分と共存)", "Please wait. LINE Manga has launched byUs now.", "Please weight. LINE Manga has launched buy us now.", "PASS", "wait/weight(既存1:1)+byus→buy us(新)の共存。全差分が同音のときのみPASS", "合成")
add("EX1", "既存の穴(AI→eye、悪化させない)", "The AI phone rings.", "The eye phone rings.", "KEEP", "AIは『エー・アイ』と読むべき。eyeはTTSの誤読。**現行でもPASSしてしまう既存の穴(INVESTIGATION_01 §2-追加5)**。提案で悪化/拡大させないことのみ確認(KEEP)。是正は別管理", "合成")
add("EX2", "既存の穴(us→u s、despace吸収、悪化させない)", "He told us the plan.", "He told u s the plan.", "KEEP", "usの文字読みu sは単独差分では全文despace(NORMALIZED_MATCH)でPASS(既存の穴、canonical=pronoun us)。canonical=国名USなら正読。提案で変化なしを確認(KEEP)", "合成")
add("M6", "略語+多語(負例)", "Some AI Phone Calls Had Humans Behind the Scenes.", "Some iPhone calls had humans behind the scenes.", "NOT_PASS", "ai phone→iphone: ガードG5(canonical側3字未満)で非救済。ガード無しだとAIを『アイ』と読む誤りを素通し", "telemetry実例")
for cid, c, a, basis in [
    ("N1", "The service is called byUs now.", "The service is called BIOS now.", "実ASR出力BIOS(run_byus_01 p1/2)。CMU: bios=B AY1 OW0 S≠byus。1:1で非同音"),
    ("N2", "The service is called byUs now.", "The service is called buys now.", "buys=B AY1 Z≠byus(Z/S)"),
    ("N3", "The service is called byUs now.", "The service is called bus now.", "bus=B AH1 S≠"),
    ("N4", "The service is called byUs now.", "The service is called buy now.", "脱落(us)。1:1で非同音"),
    ("N5", "The service is called byUs now.", "The service is called buy us on now.", "追加語(on): 連結音素列が不一致"),
    ("N6", "The service is called byUs now.", "The service is called buy a now.", "buy a=B AY1 AH0≠(終端S無し)"),
    ("N7", "The service is called byUs now.", "The service is called buy us us now.", "重複語(追加): 連結が不一致"),
    ("N10", "Melos ran to the city.", "Mellow s ran to the city.", "OOV+文字読み(G4/G6)。Melosの公式EN発音は未確認(PNEP Z1)"),
    ("N11", "Walk uphill slowly.", "Walk a pill slowly.", "uphill=AH1 P HH IH1 L≠a pill(K7実例)"),
    ("N12", "The qualitative study ran.", "The qual of study ran.", "実例(qualitative→qual of)。音素不一致"),
    ("N13", "The line was long.", "The lion was long.", "K5実例(LINE→Lion、独立エンジン2/3が実音声でLion)。line=L AY1 N≠lion=L AY1 AH0 N"),
    ("N14", "The study followed two groups.", "The study followed three groups.", "数値ガード(既存)"),
]:
    add(N := cid, "近音/脱落/追加/文字読み(負例)", c, a, "NOT_PASS", basis, "合成(実例由来の型)")
# 実ASR出力(OOV)
real("N15", "実ASR出力・CMU辞書外(負例/判定不能)", "NOT_PASS", "Baias/BAYAS/FAYAS: CMU辞書外→判定不能=推測でPASSさせない(委任_07 §2-4)", lambda p: has_c(p, "byus") and has_asr(p, r"\b(baias|bayas|fayas)\b"))
# 既存1:1・Regression
real("R1", "既存1語⇔1語同音(Regression)", "KEEP", "run_byus_01 p1/3 Primary Byus: cmu_alternateでPASS採用(現行PASS維持)", lambda p: has_c(p, "byus") and has_asr(p, r"\bbyus\b") and "primary" in p["engines"] and not has_asr(p, r"\bby us\b"), "primary")
real("R2", "既存1語⇔1語同音(Regression)", "KEEP", "p3/3 Azure bias: secondary_confirmedで採用", lambda p: has_c(p, "byus") and has_asr(p, r"\bbias\b") and "secondary" in p["engines"], "secondary")
real("R3", "story-making(Regression)", "KEEP", "HEADでstory making→storymaking+byUs→Bias共存=HOMOPHONE_EQUIVALENT(MDJF是正)", lambda p: has_c(p, "byus") and has_asr(p, r"storymaking") and has_asr(p, r"\bbias\b"))
add("EX3", "既存の穴(am→a m、despace吸収、悪化させない)", "Please wait. The meeting is at 10 am sharp.", "Please weight. The meeting is at 10 a m sharp.", "KEEP", "am→a mは空白差のみのspanとして既存の全文/span despace規則が吸収(提案の対象外)。canonical=時刻のAM(10 a.m.)なら正読。現行判定の維持のみ確認", "合成")
add("R4", "既存1語⇔1語同音(Regression)", "Please wait here.", "Please weight here.", "KEEP", "wait/weight(No.8、完全同音)", "合成")
add("R5", "固有名詞Case A(Regression)", "Christie spoke first.", "Kristie spoke first.", "KEEP", "CMU代表発音一致(PROPER_NOUN_ENTITY_ARPABET_CONFIRMED)", "合成")
add("R6", "空白差(Regression)", "We read the story-making guide.", "We read the story making guide.", "KEEP", "NORMALIZED_MATCH(despace)", "合成")
add("R7", "空白差(Regression)", "By Us lets you shape stories.", "byUs lets you shape stories.", "KEEP", "run_byus_01 topic_intro: Primary 'By Us'=NORMALIZED_MATCH", "実例型")
add("R8", "複合語(Regression)", "A blitz scaling approach.", "A blitzscaling approach.", "KEEP", "despace(冠詞除外版)", "合成")
out = []
for c in cases:
    c["before"] = judge(c["canonical"], c["asr"])
out_before = {c["id"]: c["before"] for c in cases}
P.install_proto()
for c in cases:
    c["after"] = judge(c["canonical"], c["asr"])
    P.GUARDS["single_letter"] = P.GUARDS["short_canon"] = False
    c["after_noguard_ablation"] = judge(c["canonical"], c["asr"])
    P.GUARDS["single_letter"] = P.GUARDS["short_canon"] = True
    exp = c["expect"]
    if exp == "PASS": c["ok"] = c["after"].startswith("PASS")
    elif exp == "NOT_PASS": c["ok"] = c["after"].startswith("NOT_PASS")
    else: c["ok"] = c["after"] == c["before"]
json.dump(cases, open(os.path.join(HERE, "TRIAL_CASES_01.json"), "w", encoding="utf8", newline="\n"), ensure_ascii=False, indent=1)
for c in cases:
    print("|", c["id"], "|", c["kind"], "|", c["expect"], "|", c["before"], "|", c["after"], "|", c["after_noguard_ablation"], "|", "OK" if c["ok"] else "**NG**", "|")
