"""委任_01B Trial専用Prompt(After)の静的test。API呼出なし。実行: python er064_kp_opt_01_prompt_test.py"""
import subprocess, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er064_kp_opt_01_prompt_build as B

LINE_A = "優先順位は、初回音声での処理困難、未知の可能性、瞬時の推測困難、本文の事実・感情・面白さへの影響、記事内重要度、汎用性の順です。"
COFFEE_WORDS = ["time lag", "lag", "in the ring", "pumps its fist", "pump one", "hidden clock", "be behind", "price increases",
                "raw bean", "coffee", "Coffee", "take time", "right away", "push prices", "show up", "come down", "price measure"]
V5 = "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_v5_ms_01"
results = []


def check(name, cond):
    results.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name)


bs = B.before_static()
check("T1 before: 6指標の優先順位行が逐語で1回存在", bs.count(LINE_A) == 1)
for lv in ("std", "adv"):
    a = B.after_static(lv) + B.AFTER_TAIL
    check(f"T2 after({lv}): 6指標の優先順位行が逐語で1回存在(順序維持)", a.count(LINE_A) == 1)
    check(f"T3 after({lv}): Coffee記事語句をPromptに含まない", not any(w in a for w in COFFEE_WORDS))
    for must in ['key_phrase_role="topic"', 'key_phrase_role="important"', "backup_item", "source_candidate_id", "surface_echo",
                 "[重要な単語・単語群候補]", "漢数字", "1〜5語", "ちょうど5個", "括弧", "「含む:Cn」", "established_or_article_specific"]:
        check(f"T4 after({lv}): 必須語『{must}』を保持", must in a)
check("T5 after: Std/Advの差はLEVEL_RULEのみ",
      B.after_static("std").replace(B.LEVEL_RULE["std"], "{X}") == B.after_static("adv").replace(B.LEVEL_RULE["adv"], "{X}"))
for lv, d in (("std", "a2"), ("adv", "b1b")):
    p = open(f"{V5}/{d}/key_phrases/key_phrases_db_hybrid/keywords_selector_prompt.txt", encoding="utf-8").read()
    check(f"T6 before({lv}): v5実run先頭=static逐語", p.startswith(bs.rstrip()))
    check(f"T7 before({lv}): v5実run末尾=guidance逐語", p.rstrip().endswith(B.BEFORE_GUIDANCE.strip()))
    cand = B.extract_candidate_block(p)
    aft = B.render(B.after_static(lv), B.AFTER_TAIL, cand)
    check(f"T8 after({lv}): 候補セクション(行・SENTENCE REFERENCE)がBeforeとバイト一致", cand in aft)
sb, sa = B.schema_json(False), B.schema_json(True)
ib, ia = sb["schema"]["properties"]["items"]["items"], sa["schema"]["properties"]["items"]["items"]
check("T9 schema: 追加は1フィールドのみ(他不変)", set(ia["properties"]) - set(ib["properties"]) == {"established_or_article_specific"}
      and all(ia["properties"][k] == ib["properties"][k] for k in ib["properties"]))
check("T10 schema: 追加フィールドはenum(established/article_specific/unsure)でrequired", ia["properties"]["established_or_article_specific"]["enum"] ==
      ["established", "article_specific", "unsure"] and "established_or_article_specific" in ia["required"])
check("T11 schema: backup_itemにも同schema", sa["schema"]["properties"]["backup_item"] == ia)
r = subprocess.run(["git", "diff", "--quiet", "--",
                    "er030_key_phrase_db_hybrid_source_reference_contract_01.py", "er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt",
                    "er003_key_words_min_unit.py", "er030_key_phrase_db_hybrid_selector_01.py"])
check("T12 Production Prompt/schema/builder 4ファイルの未コミット差分なし", r.returncode == 0)
fail = [n for n, ok in results if not ok]
print(f"\n{len(results) - len(fail)}/{len(results)} PASS")
sys.exit(1 if fail else 0)
