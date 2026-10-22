# er109_pattern_probe_01.py
# ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_01: 同音異表記パターンの体系カタログ(下限。ユーザー例示に限定しない)を、
# 既存の3つの票経路(P-chain相当/KP-chain相当/Whisper票)と、提案層(er109)で判定して一覧化する。API 0・ローカル処理のみ。
# 既存経路の再現範囲: val.classify_asr_match(+segment_id role gating) + homophone/entity同音救済(_step_alternate_pass) +
#   非KPのみ最終ANDゲート(er078 _protected)。M1/CS Equivalence/Tier3はwav/Azure/凍結候補が要るため含めない(旨をレポートに明記)。
# 使い方: .venv\Scripts\python.exe er109_pattern_probe_01.py [--out <json>]
import argparse
import json
import sys

sys.path.insert(0, ".")
import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as S
import er078_asr_unified_judge_01 as uj
import er104_kp_three_asr_vote_01 as kp3v
import er109_asr_orthographic_equivalence_01 as e109

# (id, category, canonical, asr, same_pron[True/False], note)
CATALOG = [
    # --- 数字<->英単語
    ("N01", "number", "one", "1", True, "ユーザー例"),
    ("N02", "number", "pump one's fist", "Pump 1's fist.", True, "ユーザー例 one's<->1's(NG3 coffee実例)"),
    ("N03", "number", "the right one", "the right 1", True, "代名詞one"),
    ("N04", "number", "two apples", "2 apples", True, ""),
    ("N05", "number", "twelve years", "12 years", True, ""),
    ("N06", "number", "twenty-eight days", "28 days", True, ""),
    ("N07", "number", "one hundred and five", "105", True, "英式and"),
    ("N08", "number", "one thousand two hundred", "1,200", True, ""),
    ("N09", "number", "two million people", "2 million people", True, ""),
    ("N10", "number", "third place", "3rd place", True, "序数"),
    ("N11", "number", "the twenty first century", "the 21st century", True, "複合序数"),
    ("N12", "number", "in twenty twenty four", "in 2024", True, "年号"),
    ("N13", "number", "in nineteen ninety", "in 1990", True, "年号"),
    ("N14", "number", "in two thousand and five", "in 2005", True, "年号 英式"),
    ("N15", "number", "the nineties", "the 90s", True, "年代"),
    ("N16", "number", "three point five", "3.5", True, "小数"),
    ("N17", "number", "zero point five", "0.5", True, "小数"),
    ("N18", "number", "one half", "1/2", True, "分数"),
    ("N19", "number", "three quarters", "3/4", True, "分数"),
    ("N20", "number", "at five thirty", "at 5:30", True, "時刻"),
    ("N21", "number", "at five o'clock", "at 5:00", True, "時刻"),
    ("N22", "number", "at eight a m", "at 8 a.m.", True, "時刻+meridiem"),
    ("N23", "number", "thirty percent", "30%", True, "%"),
    ("N24", "number", "30 percent", "30%", True, "%"),
    ("N25", "number", "five dollars", "$5", True, "通貨"),
    ("N26", "number", "five dollars and fifty cents", "$5.50", True, "通貨(セント)"),
    ("N27", "number", "ten euros", "€10", True, "通貨"),
    ("N28", "number", "minus five", "-5", True, "負数"),
    ("N29", "number", "two's company", "2's company", True, "'s付き数"),
    ("N30", "number", "a hundred dollars", "$100", False, "値は同じだが読みが違う(a hundred/one hundred)=C候補外"),
    ("N31", "number", "I have two cats", "I have to cats", True, "数詞<->同音語(to/too/two)=承認済みTrack B系"),
    ("N32", "number", "four people", "for people", True, "数詞<->同音語"),
    ("N33", "number", "one person", "won person", True, "数詞<->同音語"),
    # --- 発音が異なる数(負例)
    ("X01", "neg_number", "two", "three", False, "負例"),
    ("X02", "neg_number", "2 apples", "3 apples", False, "負例"),
    ("X03", "neg_number", "ten", "100", False, "負例"),
    ("X04", "neg_number", "in 1990", "in 1999", False, "負例"),
    ("X05", "neg_number", "3.5", "35", False, "負例"),
    ("X06", "neg_number", "$5", "5%", False, "負例"),
    ("X07", "neg_number", "thirteen", "thirty", False, "負例(最小対)"),
    ("X08", "neg_number", "fifteen", "fifty", False, "負例(最小対)"),
    ("X09", "neg_number", "the 3rd", "the 4th", False, "負例"),
    ("X10", "neg_number", "1,000", "1.000", False, "負例(桁区切り/小数)"),
    ("X11", "neg_number", "at 5:30", "at 5:13", False, "負例"),
    # --- 所有格・アポストロフィ・短縮形
    ("C01", "contraction", "it's", "its", True, ""),
    ("C02", "contraction", "they're here", "their here", True, "they're/their/there"),
    ("C03", "contraction", "they're here", "there here", True, ""),
    ("C04", "contraction", "you're right", "your right", True, "variant一致"),
    ("C05", "contraction", "who's there", "whose there", True, ""),
    ("C06", "contraction", "let's go", "lets go", True, ""),
    ("C07", "contraction", "I'm here", "I am here", True, "承認済みcontraction展開"),
    ("C08", "contraction", "it's here", "it is here", True, ""),
    ("C09", "contraction", "I can't go", "I cannot go", True, "承認済み"),
    ("C10", "contraction", "o'clock", "oclock", True, ""),
    ("C11", "contraction", "John's book", "Johns book", True, ""),
    ("C12", "contraction", "I can't go", "I can go", False, "否定反転(負例)"),
    ("C13", "contraction", "he's here", "his here", False, "負例(IY/IH)"),
    ("C14", "contraction", "I don't know", "I do know", False, "否定反転(負例)"),
    ("C15", "contraction", "I won't go", "I want go", False, "負例"),
    ("C16", "contraction", "I want to go", "I wanna go", False, "口語縮約: 2026-09-07ユーザー不採用"),
    ("C17", "contraction", "I'm going to go", "I'm gonna go", False, "口語縮約: 発音差あり/ユーザー不採用系"),
    ("C18", "contraction", "because it works", "'cause it works", False, "CMU音素が異なる"),
    # --- 同音異義語・異綴語
    ("H01", "homophone", "wait here", "weight here", True, ""),
    ("H02", "homophone", "grey sky", "gray sky", True, "英米綴り"),
    ("H03", "homophone", "colour", "color", True, "BR_AM既存"),
    ("H04", "homophone", "whisky", "whiskey", True, ""),
    ("H05", "homophone", "he passed", "he past", True, "活用形の同音"),
    ("H06", "homophone", "a flour mill", "a flower mill", True, ""),
    ("H07", "homophone", "right now", "write now", True, ""),
    ("H08", "homophone", "see the sea", "sea the sea", True, ""),
    ("H09", "homophone", "no way", "know way", True, "否定語の同音異表記(品質原則どおりなら同値)"),
    ("H10", "homophone", "analyze data", "analyse data", True, "英米綴り"),
    ("H11", "homophone", "the theatre", "the theater", True, "英米綴り"),
    ("H12", "homophone", "a licence", "a license", True, ""),
    ("H13", "homophone", "judgement", "judgment", True, ""),
    ("H14", "homophone", "the tyre", "the tire", True, ""),
    ("H15", "homophone", "he learned", "he learnt", False, "CMU: D/T で発音が異なる"),
    ("H16", "homophone", "it burned", "it burnt", False, "発音が異なる"),
    ("H17", "homophone", "my mum", "my mom", False, "母音が異なる"),
    ("H18", "homophone", "aluminium", "aluminum", False, "音節数が異なる"),
    ("H19", "homophone", "wait", "weight", True, "1語のみ=ratio<0.4でTTS_FAILURE側に落ちる既存の穴"),
    ("H20", "homophone", "take part", "take tart", False, "既知NG例(問題音声)"),
    ("H21", "homophone", "the affect", "the effect", True, "CMU variant一致(AH0 F EH1 K T)。既存同音救済どおり"),
    ("H22", "homophone", "better then that", "better than that", False, "負例(then/than)"),
    ("H23", "homophone", "a ship", "a sheep", False, "負例(最小対)"),
    ("H24", "homophone", "three men", "tree men", False, "負例"),
    ("H25", "homophone", "very good", "berry good", False, "負例"),
    ("H26", "homophone", "a cat", "a cut", False, "負例"),
    ("H27", "homophone", "increase", "decrease", False, "負例"),
    ("H28", "homophone", "the word", "the world", False, "負例"),
    # --- 単語<->複数単語
    ("M01", "multiword", "a lot of", "alot of", True, ""),
    ("M02", "multiword", "every one of them", "everyone of them", True, ""),
    ("M03", "multiword", "in to the room", "into the room", True, ""),
    ("M04", "multiword", "work out daily", "workout daily", True, ""),
    ("M05", "multiword", "may be", "maybe", True, ""),
    ("M06", "multiword", "all right", "alright", True, ""),
    ("M07", "multiword", "by us", "buy us", True, "PNMH承認済み系"),
    ("M08", "multiword", "ice cream", "I scream", True, "別語列(音素同一)"),
    ("M09", "multiword", "some time", "sometime", True, ""),
    ("M10", "multiword", "a part", "apart", True, ""),
    ("M11", "multiword", "under way", "underway", True, ""),
    ("M12", "multiword", "per cent", "percent", True, ""),
    ("M13", "multiword", "any one", "anyone", True, ""),
    ("M14", "multiword", "take part", "take apart", False, "負例"),
    ("M15", "multiword", "cannot", "can not", True, "既存"),
    # --- 略語・頭字語・記号
    ("A01", "abbrev", "the U.S. economy", "the US economy", True, ""),
    ("A02", "abbrev", "the AI model", "the A.I. model", True, ""),
    ("A03", "abbrev", "FBI agent", "F.B.I. agent", True, ""),
    ("A04", "abbrev", "FBI agent", "F B I agent", True, "文字読み分かち書き"),
    ("A05", "abbrev", "rock & roll", "rock and roll", True, ""),
    ("A06", "abbrev", "two plus two", "2 + 2", True, "+"),
    ("A07", "abbrev", "twenty degrees", "20°", True, "°"),
    ("A08", "abbrev", "Tom vs. Jerry", "Tom versus Jerry", True, ""),
    ("A09", "abbrev", "Mr. Smith", "mister Smith", True, ""),
    ("A10", "abbrev", "Dr. Lee", "doctor Lee", True, ""),
    ("A11", "abbrev", "St. Louis", "Saint Louis", True, ""),
    ("A12", "abbrev", "Main Street", "Main St.", True, "既存の通り種別"),
    ("A13", "abbrev", "OK", "okay", True, ""),
    ("A14", "abbrev", "etc.", "et cetera", True, ""),
    ("A15", "abbrev", "the TV show", "the television show", True, "CMU辞書のtv変種=television(辞書quirk。TTSの実読みは音声依存)"),
    ("A16", "abbrev", "e.g. this", "for example this", False, "読み規約: 発音同一ではない"),
    ("A17", "abbrev", "a 3D model", "a three D model", True, ""),
    ("A18", "abbrev", "5G network", "five G network", True, ""),
    ("A19", "abbrev", "Wi-Fi", "wifi", True, "wifi=CMU未登録の可能性(判定不能は同値化しない)"),
    ("A20", "abbrev", "COVID-19", "COVID nineteen", True, "covid=CMU未登録(判定不能)"),
    ("A21", "abbrev", "20 degrees Celsius", "20°C", True, "°C=未対応(単位記号)"),
    ("A22", "abbrev", "Jan. 5", "January 5", True, "月名略語=未対応"),
    ("A23", "abbrev", "the US", "the us", True, "CMUのus変種=Y UW EH S。既存は大小無視で同一視(承認済み)"),
    # --- ハイフン・スペース・句読点・大文字小文字
    ("P01", "punct", "well-being", "wellbeing", True, ""),
    ("P02", "punct", "well-being", "well being", True, ""),
    ("P03", "punct", "e-mail", "email", True, ""),
    ("P04", "punct", "co-operate", "cooperate", True, ""),
    ("P05", "punct", "T-shirt", "t shirt", True, ""),
    ("P06", "punct", "state-of-the-art", "state of the art", True, ""),
    ("P07", "punct", "Hello, world.", "hello world", True, ""),
    ("P08", "punct", "the shortcut—fruit", "the shortcut fruit", True, "em dash"),
    ("P09", "punct", "“Low” on one side", "low on one side", True, "引用符"),
    ("P10", "punct", "ice-cream", "ice cream", True, ""),
    ("P11", "punct", "Apple", "apple", True, "大小"),
    # --- ASR各社の自動整形
    ("T01", "asr_itn", "gonna", "going to", False, "ITN: 発音が異なる(ユーザー不採用系)"),
    ("T02", "asr_itn", "um, I think so", "I think so", False, "filler除去=脱落(発音一致ではない)"),
    ("T03", "asr_itn", "twenty twenty-four", "2024", True, ""),
    ("T04", "asr_itn", "okay then", "OK then", True, ""),
    ("T05", "asr_itn", "dr. Lee said", "Dr Lee said", True, ""),
    ("T06", "asr_itn", "nine to five", "9 to 5", True, ""),
    ("T07", "asr_itn", "one on one", "1 on 1", True, ""),
    ("T08", "asr_itn", "number one", "No. 1", True, "No.=否定語noと衝突するため未対応"),
    ("T09", "asr_itn", "the one percent", "the 1%", True, ""),
    ("T10", "asr_itn", "one by one", "1 by 1", True, ""),
]


def existing(canon, asr, *, sid):
    cls = val.classify_asr_match(canon, asr, segment_id=sid)
    if cls.should_pass:
        return {"pass": True, "label": cls.classification, "basis": S._equivalence_basis_of(cls)}
    alt = S._step_alternate_pass(cls)
    if alt:
        return {"pass": True, "label": str(alt)}
    return {"pass": False, "label": cls.classification}


def run():
    rows = []
    for pid, cat, c, a, same, note in CATALOG:
        p = existing(c, a, sid="full_story_part1")
        vgr, neg = uj._protected(c, a, "en")
        # 本物の統一judgeと同じ: 承認済みequivalence_basis(Tier1/数字ゲート例外)は最終ANDゲートを再否定しない
        approved = (p.get("basis") in uj.APPROVED_EQUIVALENCE_BASES) if p["pass"] else False
        gate_block = bool((vgr.kind == uj.vg.DIFF or neg) and not approved)
        p_final = bool(p["pass"] and not gate_block)
        k = existing(c, a, sid="kp1_en")
        okw, labw = kp3v._classify(c, a)
        r = e109.evaluate(c, a)
        rows.append({
            "id": pid, "cat": cat, "canonical": c, "asr": a, "same_pron_expected": same, "note": note,
            "body_P": p["pass"], "body_P_label": p["label"], "body_final_after_value_gate": p_final,
            "value_gate": vgr.kind + ("+NEG" if neg else ""),
            "kp_P": k["pass"], "kp_P_label": k["label"], "whisper_vote": bool(okw), "whisper_label": labw,
            "er109": r.equivalent, "er109_reason": r.reason, "er109_rules": r.rules,
        })
    return rows


def summarize(rows):
    pos = [r for r in rows if r["same_pron_expected"]]
    neg = [r for r in rows if not r["same_pron_expected"]]

    def rate(rs, key):
        return [sum(1 for r in rs if r[key]), len(rs)]
    keys = ("body_P", "body_final_after_value_gate", "kp_P", "whisper_vote", "er109")
    return {"pos": {k: rate(pos, k) for k in keys}, "neg": {k: rate(neg, k) for k in keys}}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="docs/research/ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01/pattern_probe_01.json")
    a = ap.parse_args()
    rows = run()
    summ = summarize(rows)
    json.dump({"generated_by": "er109_pattern_probe_01.py", "api_calls": 0, "cost_jpy": 0, "summary": summ, "rows": rows},
              open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(summ, ensure_ascii=False))
    for r in rows:
        print(f"{r['id']} {r['cat'][:8]:8} exp={'S' if r['same_pron_expected'] else 'D'} body={int(r['body_P'])}/{int(r['body_final_after_value_gate'])} "
              f"kp={int(r['kp_P'])} W={int(r['whisper_vote'])} e109={int(r['er109'])} | {r['canonical']!r} / {r['asr']!r} | "
              f"{r['body_P_label']} {r['er109_reason'][:40]}")
