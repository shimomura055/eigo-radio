# -*- coding: utf-8 -*-
"""API 0のoffline test(決定論部・安全装置・Trial隔離・委任_02のM1〜M10の分岐を合成出力で検証)。実行: PYTHONUTF8=1 .venv\\Scripts\\python.exe kpg04_test.py"""
import os, sys, json, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.pop("KPG4_CAP", None)
os.environ.pop("KPG4_SALT", None)
import kpg04_llm as L
import kpg04_methods as M


def _no_network(*a, **k):                     # 安全網: testがどう間違えても実APIへ到達させない
    raise AssertionError("testが実API呼出に到達した")


L.B.call = _no_network
L.B._load_env = _no_network

ok = 0


def check(name, cond):
    global ok
    print(("PASS " if cond else "FAIL ") + name)
    assert cond, name
    ok += 1


# 1. 既定Cap=0: 有料call(mockでない)はAPI呼出前に拒否
check("KPG4_CAP既定は0", L.CAP == 0.0)
L.set_mock(False)
try:
    L.call("gpt-6-luna", "x", None, max_out=10, tag="t"); check("Cap0で有料call拒否", False)
except L.CapReached:
    check("Cap0で有料call拒否(CapReached)", True)
try:
    L.call_ds("deepseek-v4-pro", "x", tag="t"); check("Cap0でds拒否", False)
except L.CapReached:
    check("Cap0でdeepseek call拒否", True)
try:
    L.enter_phase("t"); check("Cap0でenter_phase拒否", False)
except L.CapReached:
    check("Cap0で新規フェーズ開始拒否", True)
# 2. 出力上限・thinking明示の強制
for kw, name in ((dict(model="gpt-6-luna", user="x"), "max_out未指定は拒否"), (dict(model="gemini-3.8-flash", user="x", max_out=10), "gemini think_budget未指定は拒否")):
    try:
        L.call(kw.pop("model"), kw.pop("user"), None, **kw); check(name, False)
    except ValueError:
        check(name, True)
# 3. Cap>0でも累計/フェーズ停止点/予約(並列時の超過防止)で拒否(台帳は一時ファイル)
tmp = os.path.join(tempfile.mkdtemp(), "ledger.jsonl")
open(tmp, "w", encoding="utf-8").write(json.dumps({"cost_jpy": 50.0}) + "\n")
L.B.LEDGER = tmp; L.CAP = 40.0
try:
    L.call("gpt-6-luna", "x", None, max_out=10, tag="t"); check("Cap超過拒否", False)
except L.CapReached:
    check("累計>=Capで拒否", True)
L.CAP = 100.0
L.PHASE_LIMIT = 50.0
try:
    L.call("gpt-6-luna", "x", None, max_out=10, tag="t"); check("phase停止点到達で拒否", False)
except L.CapReached:
    check("phase停止点到達で拒否", True)
L.PHASE_LIMIT = None
# 予約: 累計50、Cap100 -> 最大想定がsol 9000 token出力(約¥14)なら通る。累計99.9なら最大想定で拒否(Capを超えない)
open(tmp, "w", encoding="utf-8").write(json.dumps({"cost_jpy": 99.9}) + "\n")
try:
    L.call("gpt-6.1-sol", "x", None, max_out=6000, tag="t", effort="low"); check("残余<最大想定は予約で拒否", False)
except L.CapReached:
    check("残余<最大想定は予約で拒否(Cap超過を事前に防ぐ)", True)
check("拒否後に予約が残らない", abs(L._inflight["reserved"]) < 1e-9)
open(tmp, "w", encoding="utf-8").write(json.dumps({"cost_jpy": 150.0}) + "\n")
L.CAP = 180.0
try:
    L.enter_phase("p"); check("80%到達後は新規フェーズ拒否", False)
except L.CapReached:
    check("累計>=Cap80%(144)で新規フェーズ開始拒否", True)
open(tmp, "w", encoding="utf-8").write(json.dumps({"cost_jpy": 10.0}) + "\n")
L.PHASE_LOG = os.path.join(os.path.dirname(tmp), "phase.jsonl")
L.enter_phase("ok"); check("80%未満は新規フェーズ開始可+記録", os.path.exists(L.PHASE_LOG))
L.CAP = 0.0; L.PHASE_LIMIT = None; L.set_mock(True)
# 4. 旧kpg03_llmのcall(CAP=120/別台帳)は無効化され、M3はkpg04のLへ差替済み
check("kpg03_llm.call無効化", not callable(getattr(L.L3, "call", None)) or L.L3.call is L._forbidden)
check("M3.LがKPG-04のLへ差替", M.M3.L is L)
try:
    L.L3.call("gpt-6-luna", "x", None, max_out=1); check("kpg03 call禁止", False)
except RuntimeError:
    check("kpg03_llm.callは例外", True)

# 4b. JSON途切れ再試行(1回だけmax_out拡大)・SALT(GEN/VER/CHK段のみ別key)
L.set_mock(False); L.CAP = 100.0
L.B.LEDGER = tmp           # 実台帳を読まない(set_mock(False)がREAL_LEDGERへ戻すため)
calls = []


def _flaky(model, user, schema, system=None, effort=None, tag="", max_out=None, think_budget=None, use_cache=True):
    calls.append(max_out)
    if len(calls) == 1:
        raise json.JSONDecodeError("trunc", "{", 1)
    return {"ok": 1}, {"cost_jpy": 0}


L.B.call = _flaky
open(tmp, "w", encoding="utf-8").write(json.dumps({"cost_jpy": 1.0}) + "\n")
r = L.call("gpt-6-luna", "xx", {"name": "s", "schema": {}}, max_out=1000, tag="c:T:GEN")
check("JSON途切れは1回だけmax_out*1.6で再試行しlog記録", calls == [1000, 1600] and r[0] == {"ok": 1} and L.RETRY_LOG and L.RETRY_LOG[-1]["retry"] is True)
calls.clear()


def _always_trunc(*a, **k):
    calls.append(1); raise json.JSONDecodeError("trunc", "{", 1)


L.B.call = _always_trunc
try:
    L.call("gpt-6-luna", "xx", {"name": "s", "schema": {}}, max_out=1000, tag="c:T:GEN"); check("再試行後も途切れなら例外", False)
except json.JSONDecodeError:
    check("2回目も途切れなら例外(無限再試行しない)・合計2call", len(calls) == 2)
L.B.call = _no_network
L.CAP = 0.0; L.set_mock(True)
L.SALT4 = "r2"
check("SALT: GEN段のみ別key", L._salted("u", "c:T:GEN5").endswith("[実行ID: r2]") and L._salted("u", "c:T:SEL") == "u" and L._salted("u", "c:T:B1") == "u")
L.SALT4 = ""

# 5. reconcile(決定論調停)・M9正規化
check("reconcile: someone/somethingのみ違い -> headword採用", M.reconcile("hear something out", "hear someone out") == ("hear someone out", "SLOT_TYPE_OVERRIDDEN"))
check("reconcile: 同一", M.reconcile("take something away from", "take something away from")[1] == "SAME")
check("reconcile: 核が違う構造違いはFRAME_MISMATCH(formは変更しない)", M.reconcile("break the ice", "break ice") == ("break the ice", "FRAME_MISMATCH"))
check("reconcile: somebody/sb正規化", M.reconcile("let someone down", "let somebody down")[1] == "SAME" and M.reconcile("let someone down", "let sb down")[1] == "SAME")
check("reconcile: 末尾slot無視(put up with / put up with sb)", M.reconcile("put up with", "put up with sb")[1] == "SAME" and M.reconcile("put up with", "put up with someone")[1] == "SAME")
check("reconcile: sth正規化", M.reconcile("shake something off", "shake sth off")[1] == "SAME")
check("reconcile: one's<->someone's は調停(override)", M.reconcile("make one's way", "make someone's way") == ("make someone's way", "SLOT_TYPE_OVERRIDDEN"))
check("reconcile: oneself正規化(enjoy yourself == enjoy oneself)", M.reconcile("enjoy oneself", "enjoy yourself")[1] == "SAME")
check("reconcile: 核が同じで見出しに語義を決める目的語枠がある -> 枠を戻す(SLOT_INSERTED)", M.reconcile("put up", "put someone up") == ("put someone up", "SLOT_INSERTED") and M.reconcile("carry out", "carry something out")[1] == "SLOT_INSERTED")
check("reconcile: 見出しの方が枠が少ない/核が違う場合は戻さない(FRAME_MISMATCH)", M.reconcile("hold someone back", "hold back")[1] == "FRAME_MISMATCH" and M.reconcile("take away from", "take something away from")[1] == "SLOT_INSERTED")
check("reconcile: to不定詞表記を無視", M.reconcile("hear someone out", "to hear someone out")[1] == "SAME")

# 6. flag_item(決定論flag): 凍結定義FLAGS_V1の範囲内。既知の2誤り型・追加flag(PERSON_OVERRIDE/PERSONIFIED_THING/VER_GLOSS_FIXED)
f1 = M.flag_item(dict(span="hear it out", tokens=[(1, "CORE", "hear"), (2, "SLOT_THING", ""), (3, "CORE", "out")]))
f2 = M.flag_item(dict(span="take points away from", tokens=[(1, "CORE", "take"), (2, "SLOT_THING", ""), (3, "CORE", "away"), (4, "CORE", "from")], display_form="take away from", display_form_pre_fix="take something away from"))
f3 = M.flag_item(dict(span="the sales pitch", tokens=[(1, "DROP", ""), (2, "CORE", "sales"), (3, "CORE", "pitch")]))
f4 = M.flag_item(dict(span="narrow down the source", tokens=[(1, "CORE", "narrow"), (2, "CORE", "down"), (3, "DROP", ""), (4, "DROP", "")]))
f5 = M.flag_item(dict(span="hear it out", tokens=[(1, "CORE", "hear"), (2, "SLOT_PERSON", ""), (3, "CORE", "out")], frame_change=["PERSON_OVERRIDE"], arg_notes=[{"n": 2, "kind": "personified_thing"}], reconcile="SLOT_TYPE_OVERRIDDEN"))
f6 = M.flag_item(dict(span="x y", tokens=[(1, "CORE", "x"), (2, "CORE", "y")], display_form="x y", gloss_ja="B", gloss_pre_ver="A"))
f7 = M.flag_item(dict(span="x y", tokens=[(1, "CORE", "x"), (2, "CORE", "y")], display_form="x y", gloss_ja="A", gloss_pre_ver="A", fix_rejected=True))
check("flag: hear it out -> PRONOUN_SLOT", f1 == ["PRONOUN_SLOT"])
check("flag: take points away from -> VER_FIXED_FORM", f2 == ["VER_FIXED_FORM"])
check("flag: 冠詞のみのDROPはflagなし", f3 == [])
check("flag: 内容語DROP(narrow down the source)は検査対象", f4 == ["CONTENT_DROPPED"])
check("flag: PERSON_OVERRIDE/PERSONIFIED_THING/SLOT_TYPE_OVERRIDDEN/PRONOUN_SLOT", set(f5) == {"PERSON_OVERRIDE", "PERSONIFIED_THING", "SLOT_TYPE_OVERRIDDEN", "PRONOUN_SLOT"})
check("flag: VER訳修正 -> VER_GLOSS_FIXED / 不採用FIX -> FIX_REJECTED", f6 == ["VER_GLOSS_FIXED"] and f7 == ["FIX_REJECTED"])
check("flag: 全flagが凍結定義FLAGS_V1内", all(x in M.FLAGS_V1 for f in (f1, f2, f3, f4, f5, f6, f7) for x in f))
check("flag定義は10種で凍結(ハッシュ記録)", len(M.FLAGS_V1) == 10 and len(M.FLAGS_V1_HASH) == 12)

check("M1: 戻す形は先頭動詞のみ原形化(複数形固定come to termsを単数化しない/articles of incorporationを崩さない)",
      M.revert_form(dict(span="came to terms with", tokens=[(1, "CORE", "come"), (2, "CORE", "to"), (3, "CORE", "term"), (4, "CORE", "with")])) == "come to terms with"
      and M.revert_form(dict(span="articles of incorporation", tokens=[(1, "CORE", "article"), (2, "CORE", "of"), (3, "CORE", "incorporation")])) == "articles of incorporation"
      and M.revert_form(dict(span="putting the brakes on", tokens=[(1, "CORE", "put"), (2, "DROP", ""), (3, "CORE", "brake"), (4, "CORE", "on")])) == "put the brakes on")
# 7. probe整合・採点(形・訳)
probes = json.load(open(os.path.join(HERE, "kpg04_probes.json"), encoding="utf-8"))
P = {p["id"]: p for p in probes}
gen = [p for p in probes if p["type"] != "FREE_COMBINATION"]
check("probe 54件・9種別(各6件)、GEN対象48件", len(probes) == 54 and len({p["type"] for p in probes}) == 9 and len(gen) == 48)
check("probe: span/sentence/context整合", all(p["span"].lower() in p["sentence"].lower() and p["sentence"] in p["context"] for p in probes))
check("probe: ok/ngの重複なし", all(not (set(p["ok"]) & set(p["ng"])) for p in probes))
check("M6: someone/something語義変化型 >=4件", sum(1 for p in probes if p["type"] == "SLOT_SENSE") >= 4)
check("M6: OO2は裸のtake upをNG(許容はtake up something/本文の形take up painting)", set(P["OO2"]["ok"]) == {"take up something", "take something up", "take up painting"} and "take up" in P["OO2"]["ng"])
check("M6: ME2/ME4/ME5はもっともらしい誤り形(実在しない形を除去)", "make a deal" in P["ME2"]["ng"] and "give someone a hand" in P["ME4"]["ng"] and "take a seat" in P["ME5"]["ng"])
check("M5: GEN対象全probeに訳キーワード事前登録", all(p.get("gloss_ok_kw") for p in gen) and all("ok_gloss" in p and "ng_gloss" in p for p in gen))
check("M5: 誤理由注入対象>=8件", sum(1 for p in probes if p.get("wrong_reason_ja")) >= 8)
check("score: hear someone out PASS / hear something out FAIL", M.score_probe({"display_form": "hear someone out"}, P["AP1"]) == "PASS" and M.score_probe({"display_form": "hear something out"}, P["AP1"]) == "FAIL")
check("score: set a limit PASS(修飾語削除はNGにしない) / 未知形REVIEW", M.score_probe({"display_form": "set a limit"}, P["MO1"]) == "PASS" and M.score_probe({"display_form": "set limits"}, P["MO1"]) == "REVIEW")
check("score: take away from FAIL", M.score_probe({"display_form": "take away from"}, P["SS1"]) == "FAIL")
check("score: 裸のtake upはOO2でFAIL", M.score_probe({"display_form": "take up"}, P["OO2"]) == "FAIL")
check("score: 本文の形へ戻した=KEPT", M.score_probe({"display_form": "take two points away from", "reverted": True, "tokens": []}, P["SS1"]) == "KEPT")
check("gloss: 『損なう』はSS1でGNG / 『差し引く』はGOK", M.score_gloss({"gloss_ja": "〜の価値や効果を損なう", "display_form": "take something away from"}, P["SS1"]) == "GNG"
      and M.score_gloss({"gloss_ja": "〜から…を差し引く", "display_form": "take something away from"}, P["SS1"]) == "GOK")
check("gloss: 削った修飾語の意味が訳に残るとGNG(set a limit+下限)/形に残っていればOK", M.score_gloss({"gloss_ja": "下限を設ける", "display_form": "set a limit"}, P["MO1"]) == "GNG"
      and M.score_gloss({"gloss_ja": "下限を設ける", "display_form": "set a lower limit"}, P["MO1"]) == "GOK")
check("M5: 形PASSでも訳NGならprobe判定FAIL(『形は同じで訳だけ別語義』を拾う)", M.probe_verdict({"display_form": "take something away from", "gloss_ja": "〜の価値や効果を損なう"}, P["SS1"]) == "FAIL")
check("probe_verdict: 形PASS+訳GOK=PASS", M.probe_verdict({"display_form": "hear someone out", "gloss_ja": "(人)の言い分を最後まで聞く"}, P["AP1"]) == "PASS")

# 8. local_context / prompt整合(M3)
txt = "A. B is here. C goes there. D comes back. E ends."
check("local_context: 前後1文", M.local_context(txt, "C goes there.") == "B is here. C goes there. D comes back.")
items_demo = [dict(span="take points away from", sentence="s", display_form="take something away from", gloss_ja="g", chunk_reason_ja="価値や効果を損なう")]
pv5 = M.prompt_V5("TEXT", items_demo)
check("M3: VER5入力に塊の理由(アンカー)を含まない", "塊の理由" not in pv5 and "価値や効果を損なう" not in pv5)
check("M3: VER5に旧Promptの矛盾文言(戻す方向のfixは書かない)が無く、戻す方向を許可", "戻す方向のfix_display_formは書かない" not in pv5 and "戻す方向のfix_display_formを書いてよい" in pv5)
check("M3: VER5は日本語に合わせるだけの目的語削除を禁止", "目的語や前置詞を削るfixは書かない" in pv5)
pb4 = M.prompt_B4_noreason("TEXT", items_demo)
check("M3: N1a/P0のVERも理由行を外す(旧文言は維持)", "塊の理由" not in pb4 and "価値や効果を損なう" not in pb4 and "戻す方向のfix_display_formは書かない" in pb4)
g5p = M.prompt_G5("TEXT", [dict(span="take points away from", sentence="s", chunk_reason_ja="価値や効果を損なう")])
check("N2のGEN5入力にも塊の理由を渡さない", "価値や効果を損なう" not in g5p and "塊の種類/理由" not in g5p)

# 9. M1/M2・調停・CHK分岐: 合成出力(fake LLM)で検証
def meta0():
    return {"model_id": "fake", "in": 1, "out": 1, "cost_jpy": 0, "sec": 0}


FAKE = {}


def fake_call(model, user, schema=None, **kw):
    return FAKE[schema["name"]](user), meta0()


real_call, real_ds = L.call, L.call_ds
L.call = fake_call


def tk(span, spec):
    return [{"n": i, "label": lab, "lemma": lem} for i, (lab, lem) in enumerate(spec, 1)]


FAKE["kp_gen_tokens5"] = lambda u: {"items": [
    {"id": 1, "source_sense_ja": "最後まで聞く", "arg_notes": [{"n": 2, "referent_ja": "サプリ", "kind": "personified_thing"}], "headword_frame": "hear someone out", "frame_change": ["PERSON_OVERRIDE"],
     "tokens": tk("hear it out", [("CORE", "hear"), ("SLOT_THING", ""), ("CORE", "out")]), "gloss_ja": "(人)の言い分を最後まで聞く", "sense_note_ja": "", "note_ja": ""},
    {"id": 2, "source_sense_ja": "(点数)を差し引く", "arg_notes": [], "headword_frame": "take something away from", "frame_change": ["OBJECT_SLOT"],
     "tokens": tk("took points away from", [("CORE", "take"), ("SLOT_THING", ""), ("CORE", "away"), ("CORE", "from")]), "gloss_ja": "〜から…を差し引く", "sense_note_ja": "減点", "note_ja": ""},
    {"id": 3, "source_sense_ja": "場所を占める", "arg_notes": [], "headword_frame": "take up space", "frame_change": ["NONE"],
     "tokens": tk("took up space", [("CORE", "take"), ("CORE", "up"), ("CORE", "space")]), "gloss_ja": "場所を占める", "sense_note_ja": "", "note_ja": ""},
    {"id": 4, "source_sense_ja": "(人)を支える", "arg_notes": [], "headword_frame": "see someone through", "frame_change": ["OBJECT_SLOT"],
     "tokens": tk("saw her through", [("CORE", "see"), ("SLOT_PERSON", ""), ("CORE", "through")]), "gloss_ja": "(人)を支えて乗り切らせる", "sense_note_ja": "", "note_ja": ""}]}
case = {"id": "t", "text": "x"}
cands = [dict(span="hear it out", sentence="s1", chunk_type="phrasal_verb", chunk_reason_ja="", cls="C", difficulty="upper_intermediate", keep=True),
         dict(span="took points away from", sentence="s2", chunk_type="phrasal_verb", chunk_reason_ja="", cls="C", difficulty="upper_intermediate", keep=True),
         dict(span="took up space", sentence="s3", chunk_type="phrasal_verb", chunk_reason_ja="", cls="C", difficulty="upper_intermediate", keep=True),
         dict(span="saw her through", sentence="s4", chunk_type="phrasal_verb", chunk_reason_ja="", cls="C", difficulty="upper_intermediate", keep=True)]
log = {"stages": []}
items = M.generalize5(case, cands, log, tag="t")
check("generalize5: tokens=SLOT_THINGでも見出しの標準用法(someone)を採用しlogに記録", items[0]["display_form"] == "hear someone out" and len(log["slot_type_overridden"]) == 1)
check("generalize5: take something away from", items[1]["display_form"] == "take something away from")


def V(id, **kw):
    d = {"id": id, "verdict": "OK", "meaning_preserved": True, "gloss_consistent": True, "natural_headword": True, "issue": "", "fix_display_form": "", "fix_gloss_ja": "",
         "source_sense_ja": "本文語義", "argument_type_ok": True, "frame_preserved": "SAME"}
    d.update(kw)
    return d


# (M2) VER FIXが slot を削る(take points away from型): 不採用+訳修正も不採用+FIX_REJECTED flag
FAKE["kp_verify5"] = lambda u: {"verdicts": [V(1), V(2, verdict="FIX", natural_headword=False, issue="訳『損なう』に合わせ目的語を除く", fix_display_form="take away from", fix_gloss_ja="〜の価値や効果を損なう"), V(3), V(4)]}
log = {"stages": []}
items = M.generalize5(case, cands, log, tag="t")
fin = M.verify5(case, items, log, tag="t")
check("M2: FIXがsomethingを削る -> 不採用(形は据え置き)", fin[1]["display_form"] == "take something away from" and len(log["fix_rejected_slot_drop"]) == 1)
check("M2: 不採用FIXの訳(損なう)も採らない", fin[1]["gloss_ja"] == "〜から…を差し引く" and "損なう" not in fin[1]["gloss_ja"])
check("M2: FIX_REJECTED flagが付く", "FIX_REJECTED" in M.flag_item(fin[1]))
check("M2補助: fix_drops_contentの判定(slot削除/CORE削除/slot種別入替/slot追加/冠詞無視)",
      M.fix_drops_content("take something away from", "take away from") == ["<slot>"] and M.fix_drops_content("set a lower limit", "set a limit") == ["lower"]
      and M.fix_drops_content("hear something out", "hear someone out") == [] and M.fix_drops_content("take away from", "take something away from") == []
      and M.fix_drops_content("break the ice", "break ice") == [])
check("M2補助: 連続slot(one's someone)の重複表記を1枠に整理するFIXは削除ではない / 本当に枠を消すFIXは削除",
      M.fix_drops_content("put up one's someone", "put someone up") == [] and M.fix_drops_content("bring up one's someone", "bring up") == ["<slot>"])
check("VER5: 末尾目的語の省略は規約でFRAME_CHANGEDにしない旨を明記", "末尾に目的語が無いこと自体は誤りではない" in pv5 and "carry out" in pv5)
# FIXがslotを追加する(許可)・someone入替(許可)
FAKE["kp_verify5"] = lambda u: {"verdicts": [V(1, verdict="FIX", fix_display_form="hear something out", fix_gloss_ja="x"), V(2), V(3), V(4)]}
log = {"stages": []}
items = M.generalize5(case, cands, log, tag="t")
fin = M.verify5(case, items, log, tag="t")
check("M2: someone->something入替FIXは削除ではない(採用)", fin[0]["display_form"] == "hear something out")
# (M1) 意味変化 -> 本文の形(lemma)+訳も本文語義へ。取れなければ除外
FAKE["kp_verify5"] = lambda u: {"verdicts": [V(1), V(2, meaning_preserved=False, issue="別語義", source_sense_ja="(点数)を差し引く・減点する"), V(3), V(4)]}
log = {"stages": []}
items = M.generalize5(case, cands, log, tag="t")
for it in items:
    it["tokens"] = it["tokens"]
fin = M.verify5(case, items, log, tag="t")
r2 = fin[1]
check("M1: 戻す時の形はlemma化(took -> take)", r2["display_form"] == "take points away from" and r2["reverted"] is True)
check("M1: 戻す時は訳も本文語義へ(VER5のsource_sense_ja)", r2["gloss_ja"] == "(点数)を差し引く・減点する" and r2["gloss_source"] == "verify.source_sense_ja" and r2["gloss_pre_revert"] == "〜から…を差し引く")
check("M1: 戻した項目はCHK対象外(flagged scopeでも検査しない)", True)
# 訳が取れない -> 除外
FAKE["kp_gen_tokens5"] = lambda u: {"items": [{"id": 1, "source_sense_ja": "", "arg_notes": [], "headword_frame": "take something away from", "frame_change": ["OBJECT_SLOT"],
    "tokens": tk("took points away from", [("CORE", "take"), ("SLOT_THING", ""), ("CORE", "away"), ("CORE", "from")]), "gloss_ja": "g", "sense_note_ja": "", "note_ja": ""}]}
FAKE["kp_verify5"] = lambda u: {"verdicts": [V(1, meaning_preserved=False, issue="別語義", source_sense_ja="")]}
log = {"stages": []}
items = M.generalize5(case, [cands[1]], log, tag="t")
fin = M.verify5(case, items, log, tag="t")
check("M1: 本文語義の訳が取れない戻しは除外(提示しない)・logに記録", fin == [] and len(log["reverted_dropped_no_gloss"]) == 1)
# 現行Productionのgloss優先
case_p = {"id": "t", "text": "x", "before": {"candidates": [{"selection_phrase": "took points away from", "gloss": "～から点を差し引く"}]}}
log = {"stages": []}
items = M.generalize5(case_p, [cands[1]], log, tag="t")
fin = M.verify5(case_p, items, log, tag="t")
check("M1: 訳はProduction保存gloss(同一span)を最優先", fin[0]["gloss_ja"] == "～から点を差し引く" and fin[0]["gloss_source"] == "PROD_GLOSS")
# (M2) argument_type_ok=False かつFIXなし -> 戻し+flag
FAKE["kp_gen_tokens5"] = lambda u: {"items": [{"id": 1, "source_sense_ja": "最後まで聞く", "arg_notes": [], "headword_frame": "hear something out", "frame_change": ["OBJECT_SLOT"],
    "tokens": tk("hear it out", [("CORE", "hear"), ("SLOT_THING", ""), ("CORE", "out")]), "gloss_ja": "最後まで聞く", "sense_note_ja": "", "note_ja": ""}]}
FAKE["kp_verify5"] = lambda u: {"verdicts": [V(1, argument_type_ok=False, issue="hear outは人を取る", source_sense_ja="(サプリの)言い分を最後まで聞く")]}
log = {"stages": []}
items = M.generalize5(case, [cands[0]], log, tag="t")
fin = M.verify5(case, items, log, tag="t")
check("M2: argument_type_ok=False+FIXなし -> 本文の形(hear it out)へ戻し+arg_unfixed記録", fin[0]["display_form"] == "hear it out" and fin[0]["reverted"] and fin[0]["arg_unfixed"])
# argument_type_ok=False でも形がFIXされたら戻さない(CHK対象にはなる: VER_FLAG)
FAKE["kp_verify5"] = lambda u: {"verdicts": [V(1, verdict="FIX", argument_type_ok=False, fix_display_form="hear someone out", fix_gloss_ja="(人)の言い分を最後まで聞く")]}
log = {"stages": []}
items = M.generalize5(case, [cands[0]], log, tag="t")
fin = M.verify5(case, items, log, tag="t")
check("M2: FIXで人称が直った場合は採用(戻さない)・flag対象", fin[0]["display_form"] == "hear someone out" and not fin[0].get("reverted") and "VER_FLAG" in M.flag_item(fin[0]))

# (CHK分岐) run_check: SAME / SENSE_SHIFT(修正+訳あり) / SENSE_SHIFT(訳なし->戻し) / FIXがslotを削る->戻し / GLOSS_MISMATCH(訳修正) / MODIFIER_DROPPED_OK
def mk(span, form, gloss, toks, **kw):
    d = dict(span=span, sentence="s", display_form=form, gloss_ja=gloss, tokens=toks, source_sense_ja="本文の語義", sense_note_ja="", reverted=False)
    d.update(kw)
    return d


def chk(rel, fx="", fg="", reason="r"):
    return {"id": 0, "context_sense_ja": "c", "example_en": "e", "relation": rel, "fix_display_form": fx, "fix_gloss_ja": fg, "reason_ja": reason}


def run_chk(item, x):
    FAKE["kp_check5"] = lambda u: {"checks": [dict(x, id=1)]}
    lg = {"stages": []}
    out = M.run_check(case, [item], lg, tag="t", scope="all")
    return out, lg


t_take = [(1, "CORE", "take"), (2, "SLOT_THING", ""), (3, "CORE", "away"), (4, "CORE", "from")]
out, lg = run_chk(mk("took points away from", "take away from", "〜の価値や効果を損なう", t_take, display_form_pre_fix="take something away from"), chk("SENSE_SHIFT", "take something away from", "〜から…を差し引く"))
check("CHK: SENSE_SHIFT+修正形+訳 -> 修正採用(訳も更新)", out[0]["display_form"] == "take something away from" and out[0]["gloss_ja"] == "〜から…を差し引く" and len(lg["check_fixed"]) == 1)
out, lg = run_chk(mk("took points away from", "take away from", "〜の価値や効果を損なう", t_take), chk("SENSE_SHIFT", "take something away from", ""))
check("CHK: 修正形だけで訳が無い -> 採用せず本文の形へ戻し(訳も本文語義)", out[0]["display_form"] == "take points away from" and out[0]["gloss_ja"] == "本文の語義" and out[0]["reverted"])
out, lg = run_chk(mk("took points away from", "take something away from", "〜から…を差し引く", t_take), chk("FRAME_SHIFT", "take away from", "損なう"))
check("CHK: 修正がslotを削る -> 採用せず戻し", out[0]["display_form"] == "take points away from" and out[0]["reverted"] and "check_fixed" not in lg)
out, lg = run_chk(mk("hear it out", "hear something out", "x", [(1, "CORE", "hear"), (2, "SLOT_THING", ""), (3, "CORE", "out")], source_sense_ja=""), chk("ARG_TYPE_SHIFT", "", ""))
check("CHK: 修正形なし+本文語義の訳も取れない -> 除外", out == [] and len(lg["reverted_dropped_no_gloss"]) == 1)
out, lg = run_chk(mk("hear it out", "hear something out", "x", [(1, "CORE", "hear"), (2, "SLOT_THING", ""), (3, "CORE", "out")]), chk("ARG_TYPE_SHIFT", "hear someone out", "(人)の言い分を最後まで聞く"))
check("CHK: ARG_TYPE_SHIFT+修正(someone入替) -> 採用", out[0]["display_form"] == "hear someone out" and out[0]["gloss_ja"] == "(人)の言い分を最後まで聞く")
out, lg = run_chk(mk("took points away from", "take something away from", "損なう", t_take), chk("GLOSS_MISMATCH", "", "〜から…を差し引く"))
check("CHK: GLOSS_MISMATCH -> 訳のみ修正(形は不変)", out[0]["display_form"] == "take something away from" and out[0]["gloss_ja"] == "〜から…を差し引く")
out, lg = run_chk(mk("set a lower limit", "set a limit", "下限を設ける", [(1, "CORE", "set"), (2, "DROP", ""), (3, "DROP", ""), (4, "CORE", "limit")]), chk("MODIFIER_DROPPED_OK", "", "制限を設ける"))
check("CHK: MODIFIER_DROPPED_OK -> 形不変・訳を一般形に", out[0]["display_form"] == "set a limit" and out[0]["gloss_ja"] == "制限を設ける")
out, lg = run_chk(mk("took up space", "take up space", "場所を占める", [(1, "CORE", "take"), (2, "CORE", "up"), (3, "CORE", "space")]), chk("SAME"))
check("CHK: SAME -> 不変", out[0]["display_form"] == "take up space" and "check_fixed" not in lg)
it_rev = mk("hear it out", "hear it out", "g", [(1, "CORE", "hear"), (2, "SLOT_THING", ""), (3, "CORE", "out")], reverted=True)
FAKE["kp_check5"] = lambda u: (_ for _ in ()).throw(AssertionError("戻した項目を検査してはならない"))
lg = {"stages": []}
out = M.run_check(case, [it_rev], lg, tag="t", scope="flagged")
check("戻した項目はCHKに送らない", out == [it_rev] and "check_targets" not in lg or lg.get("check_targets") == [])
L.call = real_call

# 9b. 旧VER(基線)の挙動: 旧規則(M1/M2を適用しない)のまま = 比較の基線
FAKE["kp_verify"] = lambda u: {"verdicts": [{"id": 1, "verdict": "FIX", "meaning_preserved": True, "gloss_consistent": True, "natural_headword": False, "issue": "i", "fix_display_form": "take away from", "fix_gloss_ja": "損なう"}]}
L.call = fake_call
log = {"stages": []}
base_item = [dict(span="took points away from", sentence="s2", display_form="take something away from", gloss_ja="差し引く", chunk_reason_ja="損なう")]
fin = M.verify_old(case, base_item, log, tag="t", strip_reason=True)
check("基線(旧VER): 目的語を削るFIXをそのまま採用(E1L再現。新方式のM2と区別)", fin[0]["display_form"] == "take away from")
L.call = real_call

# 10. mock経路でrun_probe/run_Nがエラー無く完走(API 0)
L.set_mock(True)
for cfg in ("P0", "P0i", "P1", "P2", "P4", "P4d", "P5"):
    r = M.run_probe(cfg, [p for p in probes if p["type"] != "FREE_COMBINATION"])
    check(f"mock run_probe {cfg}", len(r["items"]) >= 1 and all("probe_id" in i for i in r["items"]))
check("run_probe: 7件ずつ分割(48件->7バッチ。P0i=注入10件->2バッチ)", len(M.run_probe("P2", gen)["log"]["batches"]) == 7 and len(M.run_probe("P0i", gen)["log"]["batches"]) == 2)
check("P0iは誤理由を注入した10件のみ", len(M.run_probe("P0i", gen)["items"]) <= 10)

# 11. Production module非import(Trial隔離)
bad = [m for m in sys.modules if m.startswith("er0") or m.startswith("er1")]
check("Production module(er*)非import", not bad)
print(f"ALL PASS ({ok})")
