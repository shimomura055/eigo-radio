# -*- coding: utf-8 -*-
"""WRITER-EVAL-DUAL-LLM-METHOD-TRIAL-01 委任_01: ケース定義 -> cases_01.json(人間/Checker情報つき・評価LLMへ渡さない)
と eval_items_01.json(評価LLMへ渡す盲検版)を生成する。API呼び出しなし(Cost 0)。
再現性: case_id と提示順は固定seedで決定論的に生成。"""
import json, os, random

HERE = os.path.dirname(os.path.abspath(__file__))
SEED_ID, SEED_ORDER = 20261009, 20261010

HC012 = ("MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを"
         "「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。")
EVID008 = ("Anthropic reported that a review of 141,006 evaluation runs identified three incidents in which Claude models reached the "
           "internet from third-party evaluation environments and gained unauthorized access to real systems belonging to three "
           "organizations. The environments were misconfigured, standard cyber safeguards were absent, and the models were operating "
           "on capture-the-flag tasks. Anthropic stated that the models did not exfiltrate themselves or deliberately attempt to "
           "escape their test environments.")
F001 = ("2026年9月14日、米空軍長官Troy Meinkは、米国が「敵対的な相手の行動から統合軍を防護できる軌道上のspace control weapons"
        "（宇宙管制兵器）」を配備していると述べた。米政府機関の公式記事は、これをSpace Forceが宇宙に兵器を配備したことを初めて認めた発言として記録している。")
HF007 = "トランプ大統領は7月14日午前11時4分（米東部夏時間）、20％の米国償還料を、湾岸諸国による対米貿易・投資案件に置き換えると投稿した。"
HF002 = ("ドナルド・トランプ米大統領は7月13日午前10時16分（米東部夏時間）、米国がホルムズ海峡の安全確保に要する費用について、"
         "同海峡を通るすべての貨物に20％の率で償還を求めると投稿した。")

CASES = [
    dict(key="K01", frame="重大(人間確認済み寄り)", fact_id="MUSE-HC-012",
         fact_src="er019_output/meta/run_03/ledger/verified_fact_ledger.txt L74", fact=HC012, lang="EN",
         sentence="The company also restored the human concierge feature to the way it had been before, at least for now.",
         before="A Meta executive admitted that starting the test without properly explaining it was a mistake.",
         after="The real challenge for AI phone calls is not just how they talk.",
         sentence_src="er052_output/open233_prod_e2e_02 meta_run03_advanced EN(claim逐語は labels/labels_merged.json 他)。前後文は同文を含む er019_output/meta/run_03/b1b/article.md L17-L19 から採取【推測: prod_e2e_02の記事本体は未保存のため同一記事とみなす】",
         human_tier="Fable確定+ユーザー呼称", human="重大(方向反転: ロールバックを復元と記述)",
         human_src="er052_output/open233_prod_e2e_02/labels/labels_w2_notes.md L24-L26; report_final/critical_trace.md L12-L14; DECISION_LOG.md L20019(Fable確定)・L20053(ユーザーが『今回発見した重大見逃し』と呼称)。ユーザー個別ラベルの記録は未発見(docs/pm/rollback_misread_history_01.md §5)",
         checker="見逃し: 機械候補(negation_polarity_mismatch)→Stage1/Stage2=ACCEPTABLE→S1第2意見=ACCEPTABLE→最終 RESOLVED_STAGE2_DOWNGRADE",
         checker_src="critical_trace.md L12-L14 / rollback_misread_history_01.md §2 #4", expect="C"),
    dict(key="K02", frame="重大(人間確認済み)", fact_id="EVID-008",
         fact_src="er052_output/open233_control_checker_polysemy_trial_01/eval/HUMAN_REVIEW_PACK.md L154-L162", fact=EVID008, lang="EN",
         sentence="Nor has anyone reported that an AI got out of the test environment.",
         before="The unusual activity in AISI's incident was brought under control about an hour after it was found. In another internal test, the latest test model stopped once it learned that the target was real.",
         after="",
         sentence_src="er052_output/open233_control_checker_polysemy_trial_01/eval/blind/ai_control/jb9k/b1b/article.md L15",
         human_tier="ユーザー確認済み", human="重大(台帳EVID-008の外部到達・不正アクセスと矛盾し、外へ出ていないと誤解させる)",
         human_src="er052_output/open233_control_checker_polysemy_trial_01/eval/HUMAN_REVIEW_RESULT.md L12; DECISION_LOG.md L20214付近(2026-10-07 ユーザー人間判定)",
         checker="見逃し: Stage1 dev=MAJOR(scope拡大・unsupported_new_claim)→Stage2 materiality=QUALITY(basis=ledger_scope)→第2意見QUALITY→最終 RESOLVED_REWRITE_THEN_DOWNGRADE(PASS系)",
         checker_src="er052_output/open233_control_checker_polysemy_trial_01/eval/RCA_jb9k_qvqc.md RCA-①", expect="C"),
    dict(key="K03", frame="重大(Fable確定gold)", fact_id="MUSE-HC-012", fact_src="同上(HC-012)", fact=HC012, lang="EN",
         sentence="They also temporarily put back the feature in which humans handled the calls.",
         before="Meta executives admitted that starting the test without a proper explanation was a mistake.",
         after="They did not stop Muse itself.",
         sentence_src="er045_output/family_x_no_heading_segmentation_trial_01/meta/trial_translation.json(同文を含む段落)",
         human_tier="Fable確定", human="重大(再有効化と読める意味反転。Safety-critical gold A5-0)",
         human_src="DECISION_LOG.md L17940-L17943(A5-0=時期・経過の創作[重大])、docs/pm/investigation_ledger_deviation_check_01_part_b.md A-5(MAJOR)。ユーザー個別確認の一次記録は本委任では未発見",
         checker="Checkerではなく旧Deviation Check: v1でMAJOR検出→must-fix retry 1回→LEDGER_COMPLIANT(当時は検出できた事例)",
         checker_src="docs/pm/investigation_ledger_deviation_check_01_part_b.md A-5", expect="C"),
    dict(key="K04", frame="境界(JA、Rollback語義)", fact_id="MUSE-HC-012", fact_src="同上(HC-012)", fact=HC012, lang="JA",
         sentence="Metaの幹部は、適切な開示なしにこのテストを始めたのはミスだったと認め、人間コンシェルジュ機能を当面、以前の状態に戻しました。",
         before="ただし、これは一件の報告です。契約スタッフ全体の話に広げることはできません。",
         after="電話の便利さを急いで見せるより、誰が話しているのかを先に伝える。",
         sentence_src="er019_output/meta/run_03/ja_writer/original.md L13(前後文も同ファイル)",
         human_tier="Sonnet暫定(未ラベル)",
         human="未確定: Sonnetは『誤読はJA R0で既に発生』と記述(ユーザー未確認)。同型の『元に戻した』系はRB/CCP評価で『曖昧』(ユーザーはCCPの10件に異議なし)、Opusは『元に戻したを禁じると正しい読みまで禁じる』と指摘",
         human_src="docs/pm/ledger_clarity_p_trial/00c_before_evidence.md L10; docs/pm/opus_l2_review_pn_design_01.md L47; er052_output/open233_control_checker_polysemy_trial_01/eval/HUMAN_REVIEW_RESULT.md L16",
         checker="なし(JA R0はChecker未適用)", checker_src="docs/pm/rollback_misread_history_01.md §2 #2", expect="B?"),
    dict(key="K05", frame="境界(Rollback語義、ラベル揺れ)", fact_id="MUSE-HC-012", fact_src="同上(HC-012)", fact=HC012, lang="EN",
         sentence="The company also changed the human concierge feature back to how it was before, at least for now.",
         before="A Meta executive admitted that starting the test without explaining it clearly was a mistake.",
         after="The real challenge for AI phone calls is not only how they speak.",
         sentence_src="claim逐語: er052_output/open233_prod_e2e_02/labels/labels_merged.json idx96。前後文は同文を含む er019_output/meta/run_03/a2/article.md L17-L19 から採取【推測: neg2記事本体は一部のみ保存】",
         human_tier="Sonnet暫定(ラベル揺れあり)",
         human="Sonnet W3=問題なし(N)。一方、方向Trialのgold設定G-06は『曖昧』。Fable/ユーザーの最終ラベルなし",
         human_src="labels_merged.json idx96(confirmed_by空); er052_output/open233_directional_misread_trial_01/testset_01.json G-06",
         checker="未確認(当該runのCheckerでの候補化有無は今回未読)", checker_src="-", expect="B?"),
    dict(key="K06", frame="境界(不在・非公開の断定)", fact_id="F-001",
         fact_src="er052_output/factlock_astra_e2e_trial_01/runs/space_weapons/shared/ledger.txt L1", fact=F001, lang="EN",
         sentence="But the name of the device and exactly what it can do in an attack have not been made public.",
         before="An official U.S. government article describes this statement as the first public acknowledgment that the Space Force had put weapons in space.",
         after="So we know the weapon's address, but its details are still unclear.",
         sentence_src="er052_output/factlock_astra_e2e_trial_01/runs/space_weapons/old/b1b/article.md L5",
         human_tier="Sonnet暫定(ユーザー未裁定)",
         human="Sonnet W1=軽微(確信0.5、基準(6)字義なら重大寄り)。ユーザー回答待ち(HUMAN_CHECK_E2E_01 S-2)",
         human_src="er052_output/factlock_astra_e2e_trial_01/eval/labels_merged.jsonl w1-73; eval/HUMAN_CHECK_E2E_01.md S-1/S-2",
         checker="最終EN本文に残存(residual_miss。Checkerは修正せず)", checker_src="labels_merged.jsonl w1-73(kind=residual_miss)", expect="B?"),
    dict(key="K07", frame="境界(因果語 so)", fact_id="MUSE-HC-012", fact_src="同上(HC-012)", fact=HC012, lang="EN",
         sentence="Meta's AI calling test used human contractors without proper disclosure, so the company rolled back that feature.",
         before="", after="",
         sentence_src="er052_output/open243_translation_ng_analysis_01/S0_USER_CHECK.md 確認2(要約の1文、前後文なし)",
         human_tier="未裁定", human="ユーザー回答待ち(S0_USER_CHECK 確認2: 許容/不許容)",
         human_src="er052_output/open243_translation_ng_analysis_01/S0_USER_CHECK.md",
         checker="Checkerではなく翻訳Deviation Check: MAJOR(changed_causality)が解消せずSTOP",
         checker_src="er052_output/open243_translation_ng_analysis_01/S0_AUDIT_01.md G09 / S0_USER_CHECK.md", expect="B?"),
    dict(key="K08", frame="明らかに問題なし(日付・数値あり)", fact_id="HF-007",
         fact_src="er019_output/family_x_refresh_e2e_01/hormuz/run_03/ledger/verified_fact_ledger.txt L44", fact=HF007, lang="EN",
         sentence="Trump announced that he would drop the 20 percent fee plan and replace it with trade and investment deals between Gulf countries and the United States.",
         before="Then, the next day, the story suddenly changed.", after="",
         sentence_src="er019_output/family_x_refresh_e2e_01/hormuz/run_03/b1b/article.md L9",
         human_tier="Sonnet暫定(明白、本委任で逐語照合)",
         human="問題なし(類似文F-12は新9 runでSonnetが問題なしとラベル。この文自体のFable/ユーザー確認なし)",
         human_src="er052_output/open233_directional_misread_trial_01/testset_01.json F-12(類似); 本委任で台帳と照合",
         checker="当該文は候補化されず(local_contextとして登場のみ)",
         checker_src="er052_output/open233_prod_e2e_02/runs/hormuz_run03_advanced.json stage2_results", expect="A"),
    dict(key="K09", frame="明らかに問題なし(日付・数値あり)", fact_id="HF-002",
         fact_src="er019_output/family_x_refresh_e2e_01/hormuz/run_03/ledger/verified_fact_ledger.txt L8", fact=HF002, lang="EN",
         sentence="On July 13, Trump posted that all cargo passing through the Strait of Hormuz should provide a 20 percent reimbursement.",
         before="", after="",
         sentence_src="er052_output/open233_directional_misread_trial_01/testset_01.json F-15(前後文なし、記事本体未保存)",
         human_tier="Sonnet暫定(明白)", human="問題なし(新9 runでSonnetが問題なしとラベル、台帳とほぼ逐語一致)",
         human_src="testset_01.json F-15 origin=新9 runラベル問題なし",
         checker="未確認(参考なし)", checker_src="-", expect="A"),
    dict(key="K10", frame="明らかに問題なし(ai_control)", fact_id="EVID-008", fact_src="同上(EVID-008)", fact=EVID008, lang="EN",
         sentence="But because of a setup mistake, it was able to connect to the outside internet.",
         before="The AI was trying a task like a made-up game of capturing flags.", after="",
         sentence_src="er052_output/open233_control_checker_polysemy_trial_01/eval/blind/ai_control/jb9k/b1b/article.md L5",
         human_tier="Sonnet暫定(明白、本委任で逐語照合)",
         human="問題なし(台帳: misconfigured・インターネットへ到達。ユーザー判定の対象は別文)",
         human_src="HUMAN_REVIEW_RESULT.md(重大1文は別。この文の人間確認なし)",
         checker="Stage1で候補化(causal_not_in_fact, negation_polarity_mismatch)→Stage2 ACCEPTABLE",
         checker_src="er052_output/open233_control_checker_polysemy_trial_01/runs/ai_control/control/rep1/checker/runs/meta_run03_advanced.json cycles[0].stage2_results[2]",
         expect="A"),
]


def main():
    rng = random.Random(SEED_ID)
    alphabet = "abcdefghjkmnpqrstuvwxyz23456789"
    used = set()
    for c in CASES:
        while True:
            cid = "".join(rng.choice(alphabet) for _ in range(6))
            if cid not in used and not cid.isdigit() and not cid.isalpha():
                used.add(cid)
                c["case_id"] = cid
                break
    order = list(range(len(CASES)))
    random.Random(SEED_ORDER).shuffle(order)
    private = dict(created="2026-10-09", seeds=dict(case_id=SEED_ID, order=SEED_ORDER),
                   eval_order=[CASES[i]["case_id"] for i in order], cases=CASES)
    with open(os.path.join(HERE, "cases_01.json"), "w", encoding="utf-8") as f:
        json.dump(private, f, ensure_ascii=False, indent=1)
    items = []
    for i in order:
        c = CASES[i]
        items.append(dict(case_id=c["case_id"], fact=c["fact"], target_sentence=c["sentence"],
                          context_before=c["before"], context_after=c["after"]))
    with open(os.path.join(HERE, "eval_items_01.json"), "w", encoding="utf-8") as f:
        json.dump(dict(items=items), f, ensure_ascii=False, indent=1)
    L = ["# CASES_01: 評価方式Trial用ケース一覧(人間/Checker情報つき、評価LLMには渡さない)", "",
         "凡例: 【確認】=一次資料で逐語確認 / 【推測】=資料から推した解釈 / 人間既知判定の区分: ユーザー確認済み > Fable確定 > Sonnet暫定 > 未裁定。",
         "評価LLMへ渡すのは `eval_items_01.json`(case_id・Fact・対象文・前後文のみ)。本ファイルと `cases_01.json` は評価LLMへ渡さない。",
         f"case_idは固定seed {SEED_ID}、提示順は固定seed {SEED_ORDER} でシャッフル(`build_cases_01.py`、API呼び出しなし)。", ""]
    L += ["## 一覧(K番号順)", "", "| K | case_id | 枠 | 言語 | 人間既知の区分 | 事前期待 |", "|---|---|---|---|---|---|"]
    for c in CASES:
        L.append(f"| {c['key']} | {c['case_id']} | {c['frame']} | {c['lang']} | {c['human_tier']} | {c['expect']} |")
    L.append("")
    L.append("期待欄: C=重大 / A=問題なし / B?=境界(期待を固定しない)。K03はユーザー個別確認ではなくFable確定goldのため、PREREGISTRATION_01では必須判定から外し参考扱い。")
    for c in CASES:
        L += ["", f"## {c['key']} (case_id={c['case_id']}) {c['frame']}", "",
              f"- Fact({c['fact_id']}): {c['fact']}", f"  - 出典: {c['fact_src']}",
              f"- Writer文({c['lang']}): {c['sentence']}", f"  - 出典: {c['sentence_src']}",
              f"- 前文: {c['before'] or '(なし)'}", f"- 後文: {c['after'] or '(なし)'}",
              f"- 人間既知判定[{c['human_tier']}]: {c['human']}", f"  - 出典: {c['human_src']}",
              f"- Checker参考判定(正解扱いしない): {c['checker']}", f"  - 出典: {c['checker_src']}"]
    with open(os.path.join(HERE, "CASES_01.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("ok", len(CASES), "cases; order", [CASES[i]["key"] for i in order])


if __name__ == "__main__":
    main()
