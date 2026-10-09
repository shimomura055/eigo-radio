# -*- coding: utf-8 -*-
"""WRITER-EVAL-DUAL-LLM-METHOD-TRIAL-01 委任_01: ケース定義 -> cases_01.json(人間/Checker情報つき・評価LLMへ渡さない)
と eval_items_01.json(評価LLMへ渡す盲検版)を生成する。API呼び出しなし(Cost 0)。
再現性: case_id と提示順は固定seedで決定論的に生成。"""
import json, os, random

HERE = os.path.dirname(os.path.abspath(__file__))
SEED_ID, SEED_ORDER = 20261011, 20261012  # 委任_01c: 新規2件のcase_id用seed / 再シャッフル用seed。既存8件のcase_idは委任_01と同一(OLD_IDS)
OLD_IDS = dict(K01="y84g5r", K02="ur5649", K03="hdr8y4", K04="yjjmk8", K06="7b6trp", K08="6urnmg", K09="sq5c2g", K10="7suvyn")

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
    dict(key="K01", frame="重大(ユーザー確認済み)", fact_id="MUSE-HC-012",
         fact_src="er019_output/meta/run_03/ledger/verified_fact_ledger.txt L74", fact=HC012, lang="EN",
         sentence="The company also restored the human concierge feature to the way it had been before, at least for now.",
         before="A Meta executive admitted that starting the test without properly explaining it was a mistake.",
         after="The real challenge for AI phone calls is not just how they talk.",
         sentence_src="er052_output/open233_prod_e2e_02 meta_run03_advanced EN(claim逐語は labels/labels_merged.json 他)。対象文・前後文とも runs/meta_run03_advanced.json の local_context から逐語採取【確認】",
         human_tier="ユーザー確認済み(C、2026-10-09)", human="C=重大(ユーザー確認済み 2026-10-09。方向反転: ロールバックを復元と記述)。履歴: Fable確定+ユーザー呼称(旧区分)",
         human_src="er052_output/open233_prod_e2e_02/labels/labels_w2_notes.md L24-L26; report_final/critical_trace.md L12-L14; DECISION_LOG.md L20019(Fable確定)・L20053(ユーザーが『今回発見した重大見逃し』と呼称)。ユーザー個別ラベルの記録は未発見(docs/pm/rollback_misread_history_01.md §5)",
         checker="見逃し: 機械候補(negation_polarity_mismatch)→Stage1/Stage2=ACCEPTABLE→S1第2意見=ACCEPTABLE→最終 RESOLVED_STAGE2_DOWNGRADE",
         checker_src="critical_trace.md L12-L14 / rollback_misread_history_01.md §2 #4", expect="C", scoring="M1必須"),
    dict(key="K02", frame="重大(人間確認済み)", fact_id="EVID-008",
         fact_src="er052_output/open233_control_checker_polysemy_trial_01/eval/HUMAN_REVIEW_PACK.md L154-L162", fact=EVID008, lang="EN",
         sentence="Nor has anyone reported that an AI got out of the test environment.",
         before="The unusual activity in AISI's incident was brought under control about an hour after it was found. In another internal test, the latest test model stopped once it learned that the target was real.",
         after="",
         sentence_src="er052_output/open233_control_checker_polysemy_trial_01/eval/blind/ai_control/jb9k/b1b/article.md L15",
         human_tier="ユーザー確認済み", human="重大(台帳EVID-008の外部到達・不正アクセスと矛盾し、外へ出ていないと誤解させる)",
         human_src="er052_output/open233_control_checker_polysemy_trial_01/eval/HUMAN_REVIEW_RESULT.md L12; DECISION_LOG.md L20214付近(2026-10-07 ユーザー人間判定)",
         checker="見逃し: Stage1 dev=MAJOR(scope拡大・unsupported_new_claim)→Stage2 materiality=QUALITY(basis=ledger_scope)→第2意見QUALITY→最終 RESOLVED_REWRITE_THEN_DOWNGRADE(PASS系)",
         checker_src="er052_output/open233_control_checker_polysemy_trial_01/eval/RCA_jb9k_qvqc.md RCA-①", expect="C", scoring="M1必須"),
    dict(key="K03", frame="重大(ユーザー確認済み、gold A5-0)", fact_id="MUSE-HC-012", fact_src="同上(HC-012)", fact=HC012, lang="EN",
         sentence="They also temporarily put back the feature in which humans handled the calls.",
         before="Meta executives admitted that starting the test without a proper explanation was a mistake.",
         after="They did not stop Muse itself.",
         sentence_src="er045_output/family_x_no_heading_segmentation_trial_01/meta/trial_translation.json(同文を含む段落)",
         human_tier="ユーザー確認済み(C、2026-10-09)", human="C=重大(ユーザー確認済み 2026-10-09。再有効化と読める意味反転。Safety-critical gold A5-0)。履歴: Fable確定(旧区分)",
         human_src="DECISION_LOG.md L17940-L17943(A5-0=時期・経過の創作[重大])、docs/pm/investigation_ledger_deviation_check_01_part_b.md A-5(MAJOR)。ユーザー個別確認の一次記録は本委任では未発見",
         checker="Checkerではなく旧Deviation Check: v1でMAJOR検出→must-fix retry 1回→LEDGER_COMPLIANT(当時は検出できた事例)",
         checker_src="docs/pm/investigation_ledger_deviation_check_01_part_b.md A-5", expect="C", scoring="M1必須"),
    dict(key="K04", frame="境界(JA、Rollback語義)", fact_id="MUSE-HC-012", fact_src="同上(HC-012)", fact=HC012, lang="JA",
         sentence="Metaの幹部は、適切な開示なしにこのテストを始めたのはミスだったと認め、人間コンシェルジュ機能を当面、以前の状態に戻しました。",
         before="ただし、これは一件の報告です。契約スタッフ全体の話に広げることはできません。",
         after="電話の便利さを急いで見せるより、誰が話しているのかを先に伝える。",
         sentence_src="er019_output/meta/run_03/ja_writer/original.md L13(前後文も同ファイル)",
         human_tier="Sonnet暫定(未ラベル)",
         human="未確定: Sonnetは『誤読はJA R0で既に発生』と記述(ユーザー未確認)。同型の『元に戻した』系はRB/CCP評価で『曖昧』(ユーザーはCCPの10件に異議なし)、Opusは『元に戻したを禁じると正しい読みまで禁じる』と指摘",
         human_src="docs/pm/ledger_clarity_p_trial/00c_before_evidence.md L10; docs/pm/opus_l2_review_pn_design_01.md L47; er052_output/open233_control_checker_polysemy_trial_01/eval/HUMAN_REVIEW_RESULT.md L16",
         checker="なし(JA R0はChecker未適用)", checker_src="docs/pm/rollback_misread_history_01.md §2 #2", expect="B?", scoring="境界(採点なし)"),
    dict(key="K11", frame="重大寄り(参考・実Writer出力、ユーザー判断C寄りB余地)", fact_id="F-001",
         fact_src="er052_output/open233_allfact_note_e2e_02/ledger/space_weapons/research_ledger/verified_fact_ledger.txt L1", fact=F001, lang="JA",
         sentence="宇宙、通信、地上の設備をまとめて守るための仕組みを、米国が公の言葉で認めたということです。",
         before="つまり今回の発表は、「衛星を狙う兵器を配備した」と単純に読む話ではありません。",
         after="では、なぜ今この話が出てきたのでしょうか。",
         sentence_src="er052_output/open233_allfact_note_e2e_02/runs/space_weapons/nb/p2/rep2/ja_writer/revision2.md(JA R2、実Writer出力・逐語)。sw-p2r2-01(docs/pm/ng_root_cause_01/ng_origin_by_stage.md §4 L95)",
         human_tier="ユーザー判断(C寄り・Bの余地あり、2026-10-09)",
         human="C寄り・B余地あり(ユーザー判断 2026-10-09)。履歴: 重大(Sonnet判定。認められたのは『軌道上space control weapons配備』だが、counterspace定義(F-011)を発表内容にすり替え。主体・対象の取り違え)で、当時ユーザー未確認",
         human_src="er052_output/open233_allfact_note_e2e_02/eval/stagewise/NG_space_weapons.md L66(sw-p2r2-01、重大); docs/pm/ng_root_cause_01/ng_origin_by_stage.md L95",
         checker="JA文のためChecker評価対象外(Checkerはなし EN のみ評価)。同内容のEN文はRewrite cycle1で BLOCKING検出→修正済(NG_space_weapons.md L66)",
         checker_src="NG_space_weapons.md L66", expect="C or B", scoring="参考(M1必須外。Aなら見逃しとして報告)"),
    dict(key="K06", frame="境界(不在・非公開の断定)", fact_id="F-001",
         fact_src="er052_output/factlock_astra_e2e_trial_01/runs/space_weapons/shared/ledger.txt L1", fact=F001, lang="EN",
         sentence="But the name of the device and exactly what it can do in an attack have not been made public.",
         before="An official U.S. government article describes this statement as the first public acknowledgment that the Space Force had put weapons in space.",
         after="So we know the weapon's address, but its details are still unclear.",
         sentence_src="er052_output/factlock_astra_e2e_trial_01/runs/space_weapons/old/b1b/article.md L5",
         human_tier="Sonnet暫定(ユーザー未裁定)",
         human="Sonnet W1=軽微(確信0.5、基準(6)字義なら重大寄り)。ユーザー回答待ち(HUMAN_CHECK_E2E_01 S-2)",
         human_src="er052_output/factlock_astra_e2e_trial_01/eval/labels_merged.jsonl w1-73; eval/HUMAN_CHECK_E2E_01.md S-1/S-2",
         checker="最終EN本文に残存(residual_miss。Checkerは修正せず)", checker_src="labels_merged.jsonl w1-73(kind=residual_miss)", expect="B?", scoring="境界(採点なし)"),
    dict(key="K12", frame="問題なし(A対照・HC-012の忠実文、実Writer出力、Sonnet判定)", fact_id="MUSE-HC-012", fact_src="同上(HC-012)", fact=HC012, lang="EN",
         sentence="The human concierge feature was then put on hold for the time being.",
         before="By September 22, the vice president of Meta's Superintelligence Labs division acknowledged that starting the tests without proper disclosure had been a “mistake.”",
         after="Meta explained that it would launch the phone feature publicly only when it was ready and could give proper information.",
         sentence_src="er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/ua6f/b1b/article.md L15(EN、実Writer出力・逐語。前文は同段落、後文は次段落冒頭)",
         human_tier="Sonnet暫定(Rollback評価で『正しい』、ユーザー未確認)",
         human="問題なし(Rollback評価ラベル=correct。『取りやめ/put on hold』で方向が確定、と単独評価)。ただしユーザー未確認。なお『put on hold』は台帳の『ロールバック』と語が異なる点でBと読める余地もある【推測】",
         human_src="er052_output/open233_control_checker_polysemy_trial_01/eval/rollback_x/meta_ua6f.json(en_final=correct); SUMMARY_CCP.md L28",
         checker="記事は最終PASS系(当該文でCheckerが候補化したかは未確認)", checker_src="-", expect="A", scoring="M2"),
    dict(key="K08", frame="明らかに問題なし(日付・数値あり)", fact_id="HF-007",
         fact_src="er019_output/family_x_refresh_e2e_01/hormuz/run_03/ledger/verified_fact_ledger.txt L44", fact=HF007, lang="EN",
         sentence="Trump announced that he would drop the 20 percent fee plan and replace it with trade and investment deals between Gulf countries and the United States.",
         before="Then, the next day, the story suddenly changed.", after="",
         sentence_src="er019_output/family_x_refresh_e2e_01/hormuz/run_03/b1b/article.md L9",
         human_tier="Sonnet暫定(明白、本委任で逐語照合)",
         human="問題なし(類似文F-12は新9 runでSonnetが問題なしとラベル。この文自体のFable/ユーザー確認なし)",
         human_src="er052_output/open233_directional_misread_trial_01/testset_01.json F-12(類似); 本委任で台帳と照合",
         checker="当該文は候補化されず(local_contextとして登場のみ)",
         checker_src="er052_output/open233_prod_e2e_02/runs/hormuz_run03_advanced.json stage2_results", expect="A", scoring="M2"),
    dict(key="K09", frame="明らかに問題なし(日付・数値あり)", fact_id="HF-002",
         fact_src="er019_output/family_x_refresh_e2e_01/hormuz/run_03/ledger/verified_fact_ledger.txt L8", fact=HF002, lang="EN",
         sentence="On July 13, Trump posted that all cargo passing through the Strait of Hormuz should provide a 20 percent reimbursement.",
         before="", after="",
         sentence_src="er052_output/open233_directional_misread_trial_01/testset_01.json F-15(前後文なし、記事本体未保存)",
         human_tier="Sonnet暫定(明白)", human="問題なし(新9 runでSonnetが問題なしとラベル、台帳とほぼ逐語一致)",
         human_src="testset_01.json F-15 origin=新9 runラベル問題なし",
         checker="未確認(参考なし)", checker_src="-", expect="A", scoring="M2"),
    dict(key="K10", frame="境界(因果追加型、M2採点対象外)", fact_id="EVID-008", fact_src="同上(EVID-008)", fact=EVID008, lang="EN",
         sentence="But because of a setup mistake, it was able to connect to the outside internet.",
         before="The AI was trying a task like a made-up game of capturing flags.", after="",
         sentence_src="er052_output/open233_control_checker_polysemy_trial_01/eval/blind/ai_control/jb9k/b1b/article.md L5",
         human_tier="Sonnet暫定(因果語を含むため境界へ移動)",
         human="未確定(台帳のmisconfiguredと矛盾しないが『because of』で因果を明示=因果追加型。Opus所見によりM2から除外。ユーザー判定の対象は別文)",
         human_src="HUMAN_REVIEW_RESULT.md(重大1文は別。この文の人間確認なし)",
         checker="Stage1で候補化(causal_not_in_fact, negation_polarity_mismatch)→Stage2 ACCEPTABLE",
         checker_src="er052_output/open233_control_checker_polysemy_trial_01/runs/ai_control/control/rep1/checker/runs/meta_run03_advanced.json cycles[0].stage2_results[2]",
         expect="B?", scoring="境界(採点なし)"),
]

# 委任_01b: 前後文の出典整合(対象文と前後文が同一artifactから逐語で取れていることを確認した結果)。
# context_source は評価LLMへ渡さない運用情報(eval_items_01.jsonには監査用に載せるが、runnerは5項目のみ渡す)。
RB = "er052_output/open233_prod_e2e_02/runs/"
CTX = {
 "K01": (RB + "meta_run03_advanced.json 内 local_context(Checkerが実際に評価した記事の抜粋。対象文・前文・後文が同一local_context内に逐語で存在【確認】)。補足: er019_output/meta/run_03/b1b/article.md L17-L19 とも逐語一致"),
 "K02": ("er052_output/open233_control_checker_polysemy_trial_01/eval/blind/ai_control/jb9k/b1b/article.md L15(対象文・前文とも同一段落【確認】)。後文は同記事L17に存在するが非採用(片側のみ)"),
 "K03": ("er045_output/family_x_no_heading_segmentation_trial_01/meta/trial_translation.json(同一段落内に前文・対象文・後文が逐語で存在【確認】)"),
 "K04": ("er019_output/meta/run_03/ja_writer/original.md L11(前文=段落末尾)・L13(対象文)・L15(後文=段落冒頭)、同一ファイル【確認】"),
 "K11": ("er052_output/open233_allfact_note_e2e_02/runs/space_weapons/nb/p2/rep2/ja_writer/revision2.md(対象文・前文は同一段落、後文は次段落冒頭、同一ファイル逐語【確認】)"),
 "K12": ("er052_output/open233_control_checker_polysemy_trial_01/eval/blind/meta/ua6f/b1b/article.md L15(対象文・前文は同一段落、後文はL17冒頭文、同一ファイル逐語【確認】)"),
 "K06": ("er052_output/factlock_astra_e2e_trial_01/runs/space_weapons/old/b1b/article.md L5(対象文・前文・後文とも同一段落【確認】)"),
 "K08": ("er019_output/family_x_refresh_e2e_01/hormuz/run_03/b1b/article.md L9(対象文・前文とも同一段落【確認】)。後文は同段落に存在するが非採用(片側のみ)"),
 "K09": ("前後文なし(記事本体未保存のため。対象文のみ testset_01.json F-15)"),
 "K10": ("er052_output/open233_control_checker_polysemy_trial_01/eval/blind/ai_control/jb9k/b1b/article.md L5(対象文・前文とも同一段落【確認】)。後文は同記事に存在するが非採用(片側のみ)"),
}
# K08-K10(問題なし群)の根拠: 台帳Fact逐語 vs Writer文逐語 と差分
COMPARE = {
 "K08": ("[VERIFIED] HF-007: トランプ大統領は7月14日午前11時4分（米東部夏時間）、20％の米国償還料を、湾岸諸国による対米貿易・投資案件に置き換えると投稿した。",
         "Trump announced that he would drop the 20 percent fee plan and replace it with trade and investment deals between Gulf countries and the United States.",
         "20%=20 percent、置き換え=replace、湾岸諸国による対米貿易・投資案件=trade and investment deals between Gulf countries and the United States、主体=Trump が一致。差分: Writer文は日付・時刻(7月14日11:04)を省略(前文の『the next day』で相対表現)。『投稿した』→『announced』(語の選択差、意味は同方向)。矛盾・方向反転・追加主張なし。前日(HF-002=7月13日)との整合も『the next day』で一致。"),
 "K09": ("[VERIFIED] HF-002: ドナルド・トランプ米大統領は7月13日午前10時16分（米東部夏時間）、米国がホルムズ海峡の安全確保に要する費用について、同海峡を通るすべての貨物に20％の率で償還を求めると投稿した。",
         "On July 13, Trump posted that all cargo passing through the Strait of Hormuz should provide a 20 percent reimbursement.",
         "7月13日=July 13、投稿した=posted、ホルムズ海峡を通るすべての貨物=all cargo passing through the Strait of Hormuz、20％の率で償還=a 20 percent reimbursement が一致。差分: 時刻(10:16)・『安全確保に要する費用』の目的説明を省略(情報の省略のみで、矛盾・追加主張なし)。"),
 "K12": ("[VERIFIED] MUSE-HC-012: ...副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。",
         "The human concierge feature was then put on hold for the time being.",
         "当面=for the time being、機能(人間コンシェルジュ)=The human concierge feature、ミス認定の後=then(前文が acknowledged ... a mistake)が一致。差分: 『ロールバック』を『put on hold(保留)』と表現。方向は『止めた/引いた』側で、restoredのような再開方向ではない。ただし『rollback=元に戻した』と『保留』は厳密には同義でなく、評価LLMがBと読む余地は残る【推測】。Sonnet(Rollback評価)はcorrectとラベル、ユーザー未確認。"),
 "K10": ("(EVID-008)... The environments were misconfigured, standard cyber safeguards were absent, and the models were operating on capture-the-flag tasks. ... Claude models reached the internet from third-party evaluation environments ...",
         "But because of a setup mistake, it was able to connect to the outside internet.",
         "misconfigured=a setup mistake、reached the internet=connect to the outside internet、capture-the-flag(前文: a made-up game of capturing flags)が一致。差分: 『third-party evaluation environments』の第三者性は省略、『it』は単数(台帳はmodels複数・3件)。いずれも省略/平易化の範囲で、台帳に反する主張・方向反転なし。注意: 『but because of』の因果語は台帳の『misconfigured』が原因の一つとして記すためOK(台帳 conditions: Third-party evaluation misconfiguration)。ただし委任_01cのOpus所見により『因果追加型』として境界枠へ移し、M2採点対象外(Checkerも因果で候補化)。"),
}


def main():
    rng = random.Random(SEED_ID)
    alphabet = "abcdefghjkmnpqrstuvwxyz23456789"
    used = set(OLD_IDS.values())
    for c in CASES:
        if c["key"] in OLD_IDS:
            c["case_id"] = OLD_IDS[c["key"]]
            continue
        while True:
            cid = "".join(rng.choice(alphabet) for _ in range(6))
            if cid not in used and not cid.isdigit() and not cid.isalpha():
                used.add(cid)
                c["case_id"] = cid
                break
    order = list(range(len(CASES)))
    random.Random(SEED_ORDER).shuffle(order)
    private = dict(created="2026-10-09", revision="委任_01d", seeds=dict(case_id_new_only=SEED_ID, order=SEED_ORDER),
                   eval_order=[CASES[i]["case_id"] for i in order], cases=CASES)
    with open(os.path.join(HERE, "cases_01.json"), "w", encoding="utf-8") as f:
        json.dump(private, f, ensure_ascii=False, indent=1)
    items = []
    for i in order:
        c = CASES[i]
        items.append(dict(case_id=c["case_id"], fact=c["fact"], target_sentence=c["sentence"],
                          context_before=c["before"], context_after=c["after"],
                          context_source=CTX[c["key"]] + ("" if (c["before"] or c["after"]) else "【前後文なし】")))
    with open(os.path.join(HERE, "eval_items_01.json"), "w", encoding="utf-8") as f:
        json.dump(dict(items=items), f, ensure_ascii=False, indent=1)
    L = ["# CASES_01: 評価方式Trial用ケース一覧(人間/Checker情報つき、評価LLMには渡さない)", "",
         "凡例: 【確認】=一次資料で逐語確認 / 【推測】=資料から推した解釈 / 人間既知判定の区分: ユーザー確認済み > Fable確定 > Sonnet暫定 > 未裁定。",
         "評価LLMへ渡すのは `eval_items_01.json`(case_id・Fact・対象文・前後文のみ)。本ファイルと `cases_01.json` は評価LLMへ渡さない。",
         f"case_idは固定seed {SEED_ID}、提示順は固定seed {SEED_ORDER} でシャッフル(委任_01cで再シャッフル)(`build_cases_01.py`、API呼び出しなし)。", ""]
    L += ["## 一覧(K番号順)", "", "| K | case_id | 枠 | 言語 | 人間既知の区分 | 事前期待 | 採点対象 |", "|---|---|---|---|---|---|---|"]
    for c in CASES:
        L.append(f"| {c['key']} | {c['case_id']} | {c['frame']} | {c['lang']} | {c['human_tier']} | {c['expect']} | {c['scoring']} |")
    L.append("")
    L.append("期待欄: C=重大 / A=問題なし / B?=境界(期待を固定しない)。K01,K02,K03はユーザー確認済みCのためM1必須(K01,K03は2026-10-09確認、旧区分Fable確定は履歴)。K11はユーザー判断「C寄り・Bの余地あり」のため期待=CまたはB、参考扱い(Aなら見逃しとして報告)。")
    L += ["", "## 委任_01c(Opus条件Aレビュー反映)での変更", "",
          "- K05(K01とほぼ同文でラベル揺れ)を削除し、K11(space_weapons P2 r2のsw-p2r2-01、JA R2の実Writer出力・逐語、Sonnet判定重大・ユーザー未確認)を追加。",
          "- K07(open243の『so』因果、未裁定)を削除し、K12(HC-012の忠実文=A対照、ua6f EN最終稿の実Writer出力・逐語、Rollback評価で『正しい』・ユーザー未確認)を追加。合成文ではない。",
          "- K10(因果追加型)は境界枠へ移動しM2採点対象外。",
          "- 枠: 重大=K01,K02,K03(M1必須、委任_01dでK03昇格)+K11(参考) / 境界=K04,K06,K10 / 問題なし(M2採点)=K08,K09,K12。合計10件。",
          f"- 既存8件のcase_idは不変。新規2件のcase_idはseed {SEED_ID}。提示順は固定seed {SEED_ORDER} で再シャッフル(`eval_order`は cases_01.json に記録)。", ""]
    L += ["", "## 委任_01d(ユーザー判定の記録、2026-10-09)", "",
          "- ユーザー判断(逐語): 「1. K01 → C 2. K03 → C 3. K11 → C寄り。ただしBの余地あり」(A=問題なし/B=境界・曖昧/C=重大NG)。",
          "- K01=C(ユーザー確認済み)、K03=C(ユーザー確認済み)、K11=C寄り・B余地あり(ユーザー判断)。従来の「Fable確定」「Sonnet判定」は履歴として各ケースに残す。",
          "- K03はM1必須へ昇格。K11は参考のまま、期待=CまたはB(Aなら見逃しとして報告)。",
          "- eval_items_01.json(評価LLMへ渡す版)は変更なし(人間判定を含めない)。", ""]
    for c in CASES:
        L += ["", f"## {c['key']} (case_id={c['case_id']}) {c['frame']}", "",
              f"- Fact({c['fact_id']}): {c['fact']}", f"  - 出典: {c['fact_src']}",
              f"- Writer文({c['lang']}): {c['sentence']}", f"  - 出典: {c['sentence_src']}",
              f"- 前文: {c['before'] or '(なし)'}", f"- 後文: {c['after'] or '(なし)'}",
              f"- context_source: {CTX[c['key']]}",
              f"- 人間既知判定[{c['human_tier']}]: {c['human']}", f"  - 出典: {c['human_src']}",
              f"- Checker参考判定(正解扱いしない): {c['checker']}", f"  - 出典: {c['checker_src']}"]
    L += ["", "## 付録: K08・K09・K12(問題なし群)およびK10(境界)の根拠対比(台帳Fact逐語 / Writer文逐語 / 差分)", ""]
    for k in ("K08", "K09", "K12", "K10"):
        a, b, d = COMPARE[k]
        L += [f"### {k}", f"- 台帳Fact逐語: {a}", f"- Writer文逐語: {b}", f"- 差分: {d}", ""]
    with open(os.path.join(HERE, "CASES_01.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("ok", len(CASES), "cases; order", [CASES[i]["key"] for i in order])


if __name__ == "__main__":
    main()
