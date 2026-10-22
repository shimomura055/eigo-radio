"""KP-OPT-01 委任_02 test (Trial専用。ネットワーク・有料呼出なし)。実行: TIKTOKEN_PATH=... python er064_kp_opt_01_fix_test_02.py"""
import hashlib, json, os, re, subprocess, sys, unittest

sys.path.insert(0, os.getcwd())
if os.environ.get("TIKTOKEN_PATH"):
    sys.path.insert(0, os.environ["TIKTOKEN_PATH"])
import er064_kp_opt_01_upstream_core as U
import er064_kp_opt_01_prompt_build as B1
import er064_kp_opt_01_prompt_build_02 as B

OUT = "er064_output/kp_extraction_selection_opt_01/phase1_fix"
RES = []


def check(name, cond, detail=""):
    RES.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name + ((" :: " + str(detail)[:300]) if detail and not cond else ""))


LINE_A = "優先順位は、初回音声での処理困難、未知の可能性、瞬時の推測困難、本文の事実・感情・面白さへの影響、記事内重要度、汎用性の順です。"
COFFEE_WORDS = ["time lag", "lag", "in the ring", "pumps its fist", "pump one", "hidden clock", "be behind", "price increases", "raw bean", "coffee",
                "Coffee", "take time", "right away", "push prices", "show up", "come down", "price measure", "take care", "give back", "sharp turn", "hormuz"]
fx = json.load(open(f"{OUT}/shortlists_fixed_02.json", encoding="utf8"))
side = open(f"{OUT}/shortlists_fixed_02.sha256.txt").read().split()[0]
A = fx["articles"]

# ---- M3: Prompt短縮・不変条件 ----
for lv in ("std", "adv"):
    a = B.after_static(lv) + B.AFTER_TAIL
    check(f"M3 {lv}: 6指標の順序行が逐語で1回", a.count(LINE_A) == 1)
    check(f"M3 {lv}: Coffee/記事語句なし(take care含む)", not any(w in a for w in COFFEE_WORDS), [w for w in COFFEE_WORDS if w in a])
    check(f"M3 {lv}: established_or_article_specific欄の言及なし", "established" not in a and "article_specific" not in a)
    check(f"M3 {lv}: 『takeよりtake care of』例示なし", "take care of" not in a)
    for must in ['key_phrase_role="topic"', 'key_phrase_role="important"', "backup_item", "source_candidate_id", "surface_echo", "[重要な単語・単語群候補]",
                 "漢数字", "1〜5語", "ちょうど5個", "括弧", "質が同程度のときの補充規則"]:
        check(f"M3 {lv}: 必須語『{must}』保持", must in a)
check("M3: Level差は各1文のみ(句点1つ)", all(v.count("。") == 1 for v in B.LEVEL_RULE.values()))
check("M3: Std/Advの差はLEVEL_RULEのみ", B.after_static("std").replace(B.LEVEL_RULE["std"], "{X}") == B.after_static("adv").replace(B.LEVEL_RULE["adv"], "{X}"))
check("M3: schemaはProduction同一(追加欄なし)", B.schema_json() == B1.schema_json(False))
tm = json.load(open(f"{OUT}/token_measure_02.json", encoding="utf8"))
check("M3: Std After <= 現行(2,755)", tm["std"]["after_total_02"] <= 2755, tm["std"])
check("M3: Adv After <= 現行(3,127)", tm["adv"]["after_total_02"] <= 3127, tm["adv"])
check("M3: 現行token=2,755/3,127(Phase1-Bと同一計測)", tm["std"]["before_total"] == 2755 and tm["adv"]["before_total"] == 3127)
for lv, d in (("std", "a2"), ("adv", "b1b")):
    p = open(f"{B.V5}/{d}/key_phrases/key_phrases_db_hybrid/keywords_selector_prompt.txt", encoding="utf-8").read()
    aft = B.render(B.after_static(lv), B.AFTER_TAIL, B.extract_candidate_block(p))
    check(f"M3 {lv}: 候補セクションがBeforeとバイト一致", B.extract_candidate_block(p) in aft)
    check(f"M3 {lv}: specimenファイルとsha一致", hashlib.sha256(open(f"{OUT}/specimen_after_{lv}_v5_02.txt", "rb").read()).hexdigest() == tm[lv]["after_prompt_sha256"])

# ---- M1: 注釈ラベル統一 ----
prompt_all = B.after_static("std") + B.after_static("adv")
check("M1: Promptがrows側定数のラベル(contains: Cn / contained_in: Cn)を参照", f"`{U.LABEL_CONTAINS} Cn`" in prompt_all and f"`{U.LABEL_CONTAINED} Cn`" in prompt_all)
check("M1: Promptに旧日本語ラベル(含む:Cn/含まれる:Cn)が残っていない", "含む:" not in prompt_all and "含まれる:" not in prompt_all)
labels_in_rows = set()
for key, ent in A.items():
    for cfg in ("current", "improved", "alt_precision_guarded", "alt_precision_guarded_r1"):
        for m in re.finditer(r"\| (contains:|contained_in:|fragment_risk)", ent[cfg]["rows_text"]):
            labels_in_rows.add(m.group(1))
check("M1: rows内の注釈ラベルは全てPromptが説明している(未説明のfragment_risk等が無い)", labels_in_rows <= {U.LABEL_CONTAINS, U.LABEL_CONTAINED}, labels_in_rows)
check("M1: rows内注釈の書式 `| contains: C1,C2`", all(re.search(r"\| contains: C\d+(,C\d+)*", e["alt_precision_guarded"]["rows_text"]) for k, e in A.items() if "contains:" in e["alt_precision_guarded"]["rows_text"]))
check("M1: current(C0)のrowsに注釈が無い", all(not any(x in e["current"]["rows_text"] for x in ("contains:", "contained_in:", "fragment_risk")) for e in A.values()))

# ---- M2: 再固定 ----
check("M2: shortlists_fixed_02.json sha一致", side == U.sha256_file(f"{OUT}/shortlists_fixed_02.json"))
check("M2: snapshot sha一致", fx["snapshot_sha256"] == U.sha256_file(U.SNAPSHOT_PATH))
bad = [(k, c) for k, e in A.items() for c in ("current", "improved", "alt_precision_guarded", "alt_precision_guarded_r1")
       if hashlib.sha256(e[c]["rows_text"].encode("utf8")).hexdigest() != e[c]["rows_text_sha256"]]
check("M2: 全rows_text sha自己整合", not bad, bad)
tbad = []
for k, e in A.items():
    first = open(U.ARTICLES[k], encoding="utf8").read().lstrip().splitlines()[0].lstrip("#").strip()
    for c in ("current", "improved", "alt_precision_guarded", "alt_precision_guarded_r1"):
        if f"【Topic】title: {first}\n" not in e[c]["rows_text"] or "title: T\n" in e[c]["rows_text"]:
            tbad.append((k, c))
check("M2: 全条件・全記事で実タイトルが入っている('T'なし)", not tbad, tbad)
c0 = json.load(open(f"{OUT}/c0_byte_match_02.json", encoding="utf8"))
check("M2: C0がProduction実runの候補行とバイト一致(Coffee Std/Adv, meta Std/Adv)", all(c0[k]["byte_identical"] is True for k in ("coffee_std", "coffee_adv", "meta_std", "meta_adv")), c0)
check("M2: hormuzは旧方式のPromptで判定不能と記録(None)", c0["hormuz_std"]["byte_identical"] is None and c0["hormuz_adv"]["byte_identical"] is None)
live = U.sha256_file(f"{OUT}/shortlists_fixed_02.json")
check("M2: 旧01固定shortlistは無変更のまま存在", os.path.exists("er064_output/kp_extraction_selection_opt_01/phase1_a/shortlists_improved_01.json"))

# ---- M4: 方式1 shortlistに存在しない語句 ----
ABSENT = ["push prices up", "be behind price increases", "in the ring", "its own hidden clock", "pump one's fist", "give back gains", "take a sharp turn", "strait of hormuz"]
present = [(k, c, n["canonical_form"]) for k, e in A.items() for c in ("current", "improved", "alt_precision_guarded", "alt_precision_guarded_r1")
           for n in e[c]["candidates"] if n["canonical_form"].replace("'", "'") in ABSENT]
check("M4: 8表現(Coffee5+hormuz3)が全記事・全構成のshortlistに存在しない", not present, present)

# ---- R1 / R2 / R3 ----
r1 = json.load(open(f"{OUT}/r1_and_metrics_02.json", encoding="utf8"))["r1"]
imp_r1 = {n for m in A.values() for n in [c["canonical_form"] for c in m["alt_precision_guarded_r1"]["candidates"] if c["important_noun_phrase_candidate"]]}
check("R1: want to/close to/call itがR1構成のimportantに残らない", not ({"want to", "close to", "call it"} & imp_r1), imp_r1 & {"want to", "close to", "call it"})
check("R1: take care/be wrongはR1構成にも残る(最後が内容語)", {"take care", "be wrong"} <= imp_r1, imp_r1)
check("R1: 除去3種=call it/close to/want to", r1["r1_moved_from_important_all"] == ["call it", "close to", "want to"])
check("R1: 希少単語の押し出し件数は減らない(guarded==guarded_r1)", r1["totals_words_pushed_out"]["alt_precision_guarded"] == r1["totals_words_pushed_out"]["alt_precision_guarded_r1"])
mk = lambda surf, ut, dbs_, imp=False, cats=None: {"surface_form": surf, "canonical_form": surf.lower(), "unit_type": ut, "matched_dbs": dbs_,
                                                   "db_categories": cats, "important_noun_phrase_candidate": imp}
units = [{"tokens": "The crude price rose .".split()}]
units2 = [{"tokens": "A time lag exists .".split()}]
dem = U.compute_containment([mk("time lag", "phrase", ["wiktionary"], False, ["multiword_term"]), mk("lag", "word", ["ngsl_family"])], units2, r2=True)
imp = U.compute_containment([mk("time lag", "phrase", ["wiktionary"], True, ["multiword_term"]), mk("lag", "word", ["ngsl_family"])], units2, r2=True)
old = U.compute_containment([mk("time lag", "phrase", ["wiktionary"], False, ["multiword_term"]), mk("lag", "word", ["ngsl_family"])], units2, r2=False)
check("R2: 長い側がdemoted(online hit・非important)ならTier-H発火せずTier-S", dem and dem[0]["tier"] == "S")
check("R2: 長い側がimportant判定ならTier-H発火", imp and imp[0]["tier"] == "H")
check("R2: r2=False(01互換)ではdemotedでもTier-H", old and old[0]["tier"] == "H")
check("R3: 助動詞始まり(been behind price increases等)はfragment_riskでない(no_aux)", not U.fragment_risk("been behind price increases", False, no_aux=True)
      and not U.fragment_risk("has read the clock", False, no_aux=True))
check("R3: in the ring / the two numbers in the ringは引き続きfragment_risk", U.fragment_risk("in the ring", False, no_aux=True) and U.fragment_risk("the two numbers in the ring", False, no_aux=True))
check("R3: 01互換(no_aux=False)では助動詞始まりも対象", U.fragment_risk("been behind price increases", False))

# ---- Production無変更 ----
r = subprocess.run(["git", "diff", "--quiet", "--", "er030_key_phrase_db_hybrid_source_reference_contract_01.py", "er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt",
                    "er003_key_words_min_unit.py", "er030_key_phrase_db_hybrid_selector_01.py", "er030_key_phrase_db_hybrid_core_01.py",
                    "er027_key_phrase_db_hybrid_trial_02_stage1.py", "er023_key_phrase_db_ingest.py", "er023_key_phrase_db_extraction.py"])
check("Production 8ファイルの未コミット差分なし", r.returncode == 0)

fail = [n for n, ok in RES if not ok]
print(f"\nRESULT {len(RES) - len(fail)}/{len(RES)} PASS")


class ScriptChecksTest(unittest.TestCase):
    """unittest discovery用(TEST-HYGIENE-02、2026-10-22): 本fileはstandalone script形式(`python <file>`で実行、
    終了codeで判定)。モジュール読込時に全checkが実行済みなので、その結果を1件のtestとして検証する。"""
    def test_all_checks_pass(self):
        self.assertEqual(fail, [])


if __name__ == "__main__":
    sys.exit(1 if fail else 0)
