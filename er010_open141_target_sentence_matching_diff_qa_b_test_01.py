# ============================================================
# er010_open141_target_sentence_matching_diff_qa_b_test_01.py
# OPEN-141-TARGET-SENTENCE-MATCHING-AND-DIFF-QA-COMMON-BASE-TRIAL-01 Phase B
# ============================================================
# 実LLM呼び出しを一切行わず(mock/保存済みflagのみ)、B1(target-sentence-
# matching、opt-in既定OFF)・B3(split_sentences見出し除外)の回帰テスト。
# Phase A(A3: 保存済み実データ8件、A4: 合成危険11件)で確認した結果を、
# 実際のProduction関数(classify_deviation_role/evaluate_target_sentence_
# status/split_sentences/rewrite_ng_item)を使って再現する。追加API呼び出し
# 0件(¥0)。

import unittest

import er010_ledger_local_rewrite_09 as local_rewrite


# ============================================================
# B3: split_sentences()の見出し行除外
# ============================================================
class SplitSentencesHeadingExclusionTests(unittest.TestCase):
    def test_no_heading_input_unchanged(self):
        """見出しを含まない入力に対する挙動は従来と完全に同一(byte一致)。"""
        text = "First sentence here. Second sentence follows. Third one ends it."
        result = local_rewrite.split_sentences(text)
        self.assertEqual(result, [
            "First sentence here.", "Second sentence follows.", "Third one ends it.",
        ])

    def test_heading_line_excluded_from_sentence_join(self):
        text = (
            "The early lead faced one clear challenge, not repeated waves of pressure.\n\n"
            "### More than one hitter finished the job\n\n"
            "Late in the game, more than one hitter supplied the scoring."
        )
        result = local_rewrite.split_sentences(text)
        self.assertIn("The early lead faced one clear challenge, not repeated waves of pressure.", result)
        self.assertIn("Late in the game, more than one hitter supplied the scoring.", result)
        for s in result:
            self.assertNotIn("More than one hitter finished the job", s)

    def test_h1_and_h2_headings_also_excluded(self):
        text = "# Title Line\n\nIntro sentence here.\n\n## In one line\n\nClosing sentence here."
        result = local_rewrite.split_sentences(text)
        joined = " ".join(result)
        self.assertNotIn("Title Line", joined)
        self.assertNotIn("In one line", joined)

    def test_real_article_reproduction_daily_news_focus_layer_trial_04(self):
        """OPEN-141 Phase B実データ確認: `er011_output/daily_news_focus_
        layer_comparison_trial_04/b1b/focus/run2`のarticle.mdで実際に発生
        していた見出し混入(旧split_sentencesでは対象文が見出し+隣接文と
        結合され、locate_target_sentenceのfallback対象文字列が実際の記事
        本文[改行あり]とbyte一致せず、apply_rewritesの文字列置換が
        サイレントに失敗していた)が、修正後は解消することを確認する。"""
        section_text = (
            "The key contrast was not simply how many runs Hanshin scored. Hiroshima never "
            "built a long rally. Its only run came on Montero’s solo shot, while Ihara "
            "allowed just two hits and one run over five innings. The early lead faced one "
            "clear challenge, not repeated waves of pressure.\n\n"
            "### More than one hitter finished the job\n\n"
            "Late in the game, more than one hitter supplied the scoring. Seishiro Sakamoto "
            "drove in a run in the seventh and added an RBI double in the eighth."
        )
        sentences = local_rewrite.split_sentences(section_text)
        # 修正前は "The early lead faced one clear challenge, not repeated waves of pressure. "
        # "### More than one hitter finished the job Late in the game, more than one hitter "
        # "supplied the scoring." という1つの結合済み文字列になっていた(Phase A2実例)。
        target = "The early lead faced one clear challenge, not repeated waves of pressure."
        self.assertIn(target, sentences)
        idx = sentences.index(target)
        # 対象文の直後の文が、見出しを挟まず正しく取得できる(before/after contextの
        # 正確性、B1のtarget-sentence-matchingが正しい前後文を参照するための前提)。
        self.assertEqual(
            sentences[idx + 1],
            "Late in the game, more than one hitter supplied the scoring.")


# ============================================================
# B1: classify_deviation_role / evaluate_target_sentence_status
# ============================================================
class ClassifyDeviationRoleTests(unittest.TestCase):
    def test_exact_substring_to_target(self):
        result = local_rewrite.classify_deviation_role(
            "The tool rejects women", "The tool rejects women more often.", "Intro.", "Closing.")
        self.assertEqual(result["role"], "target")
        self.assertEqual(result["method"], "exact_substring")

    def test_exact_substring_to_adjacent_before(self):
        result = local_rewrite.classify_deviation_role(
            "Intro sentence text.", "Target sentence text.", "Intro sentence text.", "Closing.")
        self.assertEqual(result["role"], "before")

    def test_not_found_is_ambiguous(self):
        result = local_rewrite.classify_deviation_role(
            "completely unrelated content about vegetables", "Target sentence text.",
            "Intro.", "Closing.")
        self.assertEqual(result["role"], "ambiguous")
        self.assertEqual(result["method"], "not_found")

    def test_multi_exact_match_is_ambiguous(self):
        result = local_rewrite.classify_deviation_role(
            "shared phrase", "shared phrase in target", "shared phrase in before", "")
        self.assertEqual(result["role"], "ambiguous")
        self.assertEqual(result["method"], "exact_substring_multi_match")


class EvaluateTargetSentenceStatusPhaseAReproductionTests(unittest.TestCase):
    """OPEN-141 Phase A3(保存済み実データ8件、stage1b1_results.json由来、
    追加API呼び出し0件)の再分類結果を、実際のevaluate_target_sentence_
    status()で再現する。before_ctx/after_ctxはPhase A実行時に別途保存
    していなかったため、各deviationのclaim_in_article自体を「対象文以外の
    隣接文」の実データとして流用し(捏造ではなく実際に保存されたLLM出力
    文字列)、対象文への対応付けを検証する。期待値はPhase A REPORT A3節の
    表と完全に一致させる(8件中6件がCOMPLIANTへ変わり、1件は元々
    COMPLIANTのまま、1件は正しくDEVIATIONのまま維持)。"""

    def _status(self, target, deviations, before_ctx="", after_ctx=""):
        check_result = {"overall_status": "LEDGER_DEVIATION" if any(
            d["severity"] == "MAJOR" for d in deviations) else "LEDGER_COMPLIANT",
            "deviations": deviations}
        return local_rewrite.evaluate_target_sentence_status(
            check_result, target, before_ctx, after_ctx)["overall_status"]

    def test_a_narrow_final_text_becomes_compliant(self):
        target = ("In these cases, their power may be uneven: the applicant may have limited "
                   "influence over the process and may face difficulty understanding or "
                   "challenging it; the recruiter or hiring manager may use the tool and, in "
                   "some cases, help decide whether it is used; and the company or business "
                   "leader may weigh efficiency against fairness, legal, and other risks and "
                   "consequences.")
        claim = "The owner must keep the company running and carry the result personally."
        deviations = [{"claim_in_article": claim, "severity": "MAJOR"}]
        status = self._status(target, deviations, before_ctx=claim)
        self.assertEqual(status, "LEDGER_COMPLIANT")

    def test_a_wide_final_text_becomes_compliant(self):
        target = ("In these cases, their power may be uneven: the applicant may have limited "
                   "influence over the process and may face difficulty understanding or "
                   "challenging it; the recruiter or hiring manager may use the tool and, in "
                   "some cases, help decide whether it is used; and the company or business "
                   "leader may weigh efficiency against fairness, legal, and other risks and "
                   "consequences.")
        claim = ("New York City requires a recent bias audit and notice when these tools are "
                  "used, while the EU treats hiring AI as high-risk, with oversight and "
                  "transparency duties.")
        deviations = [{"claim_in_article": claim, "severity": "MAJOR"}]
        status = self._status(target, deviations, before_ctx=claim)
        self.assertEqual(status, "LEDGER_COMPLIANT")

    def test_b_narrow_final_text_becomes_compliant(self):
        target = ("In the evidence gathered here, their power appears uneven: the applicant is "
                   "judged, while the recruiter may be involved in using the tool or in "
                   "decisions about its use.")
        claim1 = "New York City’s yearly bias check and notice rule"
        claim2 = "New York City’s yearly bias check and notice rule ... leaves the applicant without control."
        deviations = [
            {"claim_in_article": claim1, "severity": "MAJOR"},
            {"claim_in_article": claim2, "severity": "MAJOR"},
        ]
        status = self._status(target, deviations, before_ctx=claim2)
        self.assertEqual(status, "LEDGER_COMPLIANT")

    def test_b_wide_final_text_becomes_compliant(self):
        target = ("In the evidence gathered here, their power appears uneven: the applicant is "
                   "judged, while the recruiter may be involved in using the tool or in "
                   "decisions about its use.")
        claim1 = "New York City’s yearly bias check and notice rule"
        claim2 = "[ニューヨーク市の規則が] leaves the applicant without control"
        claim3 = "One company stopped an internal tool after it rated women’s résumés lower."
        deviations = [
            {"claim_in_article": claim1, "severity": "MAJOR"},
            {"claim_in_article": claim2, "severity": "MAJOR"},
            {"claim_in_article": claim3, "severity": "MAJOR"},
        ]
        status = self._status(target, deviations, before_ctx=f"{claim1} {claim2}", after_ctx=claim3)
        self.assertEqual(status, "LEDGER_COMPLIANT")

    def test_control_wide_trial02_attempt2_becomes_compliant(self):
        target = ("The applicant cannot choose the system; the recruiter runs it and may also "
                   "help decide whether to adopt it; the owner may make the final call.")
        claim = "One company stopped a tool after it rated women lower."
        deviations = [{"claim_in_article": claim, "severity": "MAJOR"}]
        status = self._status(target, deviations, before_ctx=claim)
        self.assertEqual(status, "LEDGER_COMPLIANT")

    def test_control_wide_regression_attempt2_evenif_stays_compliant(self):
        """元々window全体判定でもCOMPLIANT(deviationがMINORのみ)。
        target-sentence単位でも変わらずCOMPLIANTを維持することを確認する。"""
        target = "I prepare plain explanations and audit summaries, even as I help decide how the tool is used."
        claim = "I prepare plain explanations and audit summaries."
        deviations = [{"claim_in_article": claim, "severity": "MINOR"}]
        status = self._status(target, deviations, before_ctx=claim)
        self.assertEqual(status, "LEDGER_COMPLIANT")

    def test_control_wide_regression_attempt3_powerisuneven_becomes_compliant(self):
        target = ("Power can be uneven: in some cases, the applicant may have little control "
                   "over the process, while the recruiter may operate the tool or help decide "
                   "whether to use it, and the employer may remain responsible for how it is "
                   "used.")
        claim1 = "“the applicant still cannot control the score”"
        claim2 = "“One company stopped a tool that rated resumes with women’s terms lower.”"
        deviations = [
            {"claim_in_article": claim1, "severity": "MAJOR"},
            {"claim_in_article": claim2, "severity": "MAJOR"},
        ]
        status = self._status(target, deviations, before_ctx=claim1, after_ctx=claim2)
        self.assertEqual(status, "LEDGER_COMPLIANT")

    def test_control_wide_run1ng_cycle2_nyc_stays_deviation(self):
        """本物の危険な変更(対象文自身に「毎年」という未確認の頻度が追加
        されている)は、target-sentence単位でも正しくLEDGER_DEVIATIONの
        まま維持されなければならない(安全側の副作用がないことの確認)。"""
        target = ("New York City’s yearly bias check and notice rule adds work for the "
                   "recruiter, limits the owner’s choice, and requires notice to the "
                   "applicant.")
        claim_on_target = target  # Ledger Deviation Checkerが対象文自身を引用
        claim_adjacent = "One company stopped an internal tool after it rated women’s résumés lower."
        deviations = [
            {"claim_in_article": claim_on_target, "severity": "MAJOR"},
            {"claim_in_article": claim_adjacent, "severity": "MAJOR"},
        ]
        status = self._status(target, deviations, before_ctx=claim_adjacent)
        self.assertEqual(status, "LEDGER_DEVIATION")


class EvaluateTargetSentenceStatusSyntheticDangerCasesTests(unittest.TestCase):
    """OPEN-141 Phase A4(合成危険11件、rule-based、追加API呼び出し0件)の
    再現。対象文自身にMAJOR(数値/固有名詞・制度名/否定/第三者行動/因果/
    比較等)が付与されている場合、無関係な隣接文のdistractor deviationが
    あってもtarget-sentence-matchingがMAJORを取りこぼさないことを、実際の
    evaluate_target_sentence_status()で確認する。"""

    ALL_FLAGS = [
        "changed_fact", "changed_scope", "changed_causality", "changed_certainty",
        "changed_number", "changed_actor", "changed_negation", "changed_comparison",
        "changed_time", "unsupported_new_claim",
    ]

    CASES = [
        ("syn01_number", "The audit found that 62% of applicants were rejected within the first minute.",
         "Some hiring tools raise legitimate fairness questions."),
        ("syn02_propernoun_institution",
         "Meta paid a $14 million settlement after the EEOC found discriminatory ad targeting.",
         "Recruiters must balance speed with fairness."),
        ("syn03_negation", "The recruiter no longer has any say in the process.",
         "The applicant hopes for a fair review."),
        ("syn04_thirdparty_action",
         "Another applicant said he was scored lower after the system flagged his resume.",
         "Companies are adopting AI screening tools quickly."),
        ("syn05_causality_reversal",
         "The audit requirement caused the company to stop using the tool entirely.",
         "The owner wants to keep costs low."),
        ("syn06_comparison", "This tool rejects twice as many women as men for the same role.",
         "Employers must post clear job descriptions."),
        ("syn07_time_institution",
         "Since 2019, New York City has fined over 40 companies for AI hiring violations.",
         "The recruiter reviews each flagged case personally."),
        ("syn08_negation_actor", "The owner never reviews the audit summary before it is sent.",
         "Applicants can request an explanation of their score."),
        ("syn09_thirdparty_institution",
         "The EEOC ordered Acme Corp to suspend its hiring algorithm nationwide.",
         "Hiring managers juggle many competing priorities."),
        ("syn10_number_causality",
         "Because of the new law, processing time dropped from 30 days to 3 days.",
         "The applicant waits anxiously for a response."),
        ("syn11_no_distractor_control",
         "The company fired 200 employees after the algorithm audit failed.", None),
    ]

    def test_all_11_synthetic_dangerous_cases_retain_major(self):
        for case_id, target, distractor in self.CASES:
            with self.subTest(case_id=case_id):
                deviations = [{"claim_in_article": target, "severity": "MAJOR",
                               **{k: False for k in self.ALL_FLAGS}}]
                before_ctx = ""
                if distractor:
                    deviations.append({"claim_in_article": distractor, "severity": "MAJOR",
                                        **{k: False for k in self.ALL_FLAGS}})
                    before_ctx = distractor
                check_result = {"overall_status": "LEDGER_DEVIATION", "deviations": deviations}
                result = local_rewrite.evaluate_target_sentence_status(
                    check_result, target, before_ctx, "")
                self.assertEqual(result["overall_status"], "LEDGER_DEVIATION",
                                  f"{case_id} lost its MAJOR under target-sentence-matching")


# ============================================================
# B1: rewrite_ng_item()のopt-in既定OFF不変性 + opt-in ON時の実受理判定
# ============================================================
class RewriteNgItemOptInInvarianceTests(unittest.TestCase):
    def _fake_client(self, texts):
        client = __import__("unittest.mock", fromlist=["mock"]).Mock()
        resp_iter = iter(texts)

        def _create(**kwargs):
            resp = __import__("unittest.mock", fromlist=["mock"]).Mock()
            resp.output_text = next(resp_iter)
            return resp
        client.responses.create.side_effect = _create
        return client

    def test_default_off_matches_pre_open141_shape_exactly(self):
        """use_target_sentence_matchingを渡さない(既定False)場合、attempts
        エントリは従来通り{'attempt','text','ledger_status'}の3キーのみで
        あり、window全体のoverall_statusだけで受理判定される(byte一致)。"""
        client = self._fake_client(["Tip rates can rise after screens appear."])
        check_fn = lambda window_text: {"overall_status": "LEDGER_COMPLIANT",
                                         "deviations": [{"claim_in_article": "unrelated", "severity": "MAJOR"}]}
        deviation = {"issue": "certainty強化", "explanation": "explanation", "changed_certainty": True}
        result = local_rewrite.rewrite_ng_item(
            client, "fake-model", "medium", "LEDGER TEXT", "POINT CONTEXT",
            "Tip rates always rise after screens appear.", deviation, "before.", "after.", check_fn)
        self.assertTrue(result["resolved"])
        self.assertEqual(result["attempts"], [{
            "attempt": 1, "text": "Tip rates can rise after screens appear.",
            "ledger_status": "LEDGER_COMPLIANT",
        }])

    def test_opt_in_on_reclassifies_using_target_sentence_only(self):
        """opt-in ON: window全体はLEDGER_DEVIATION(隣接文にMAJORがある)だが、
        対象文自身にはdeviationが対応付かないため、target-sentence単位では
        LEDGER_COMPLIANTとして受理される(false reject解消の実動作確認)。"""
        client = self._fake_client(["The early lead was narrowed by a solo shot."])
        adjacent_claim = "Hiroshima never built a long rally."

        def check_fn(window_text):
            return {"overall_status": "LEDGER_DEVIATION",
                    "deviations": [{"claim_in_article": adjacent_claim, "severity": "MAJOR"}]}

        deviation = {"issue": "issue", "explanation": "explanation", "unsupported_new_claim": True}
        result = local_rewrite.rewrite_ng_item(
            client, "fake-model", "medium", "LEDGER TEXT", "POINT CONTEXT",
            "The early lead faced one clear challenge.", deviation,
            before_ctx=adjacent_claim, after_ctx="Late in the game, more hitters scored.",
            run_check_window_fn=check_fn, use_target_sentence_matching=True)
        self.assertTrue(result["resolved"])
        self.assertEqual(result["attempts"][0]["ledger_status"], "LEDGER_COMPLIANT")
        self.assertEqual(result["attempts"][0]["ledger_status_window"], "LEDGER_DEVIATION")
        self.assertIn("target_sentence_eval", result["attempts"][0])

    def test_opt_in_on_still_blocks_when_target_itself_is_major(self):
        """opt-in ON でも、対象文自身がMAJORでフラグされる場合は3回escalate
        してもLEDGER_DEVIATIONのまま human_review_required になる
        (安全側の副作用がないことの確認)。"""
        client = self._fake_client(["attempt1 text", "attempt2 text", "attempt3 text"])

        def check_fn(window_text):
            # 対象文(rewrite後テキスト)自身がclaimとして返る = 常にtargetへ紐づく
            for candidate in ("attempt1 text", "attempt2 text", "attempt3 text"):
                if candidate in window_text:
                    return {"overall_status": "LEDGER_DEVIATION",
                            "deviations": [{"claim_in_article": candidate, "severity": "MAJOR"}]}
            return {"overall_status": "LEDGER_COMPLIANT", "deviations": []}

        deviation = {"issue": "issue", "explanation": "explanation", "changed_number": True}
        result = local_rewrite.rewrite_ng_item(
            client, "fake-model", "medium", "LEDGER TEXT", "POINT CONTEXT",
            "Original NG sentence.", deviation, before_ctx="before.", after_ctx="after.",
            run_check_window_fn=check_fn, use_target_sentence_matching=True)
        self.assertFalse(result["resolved"])
        self.assertTrue(result["human_review_required"])
        self.assertEqual(len(result["attempts"]), local_rewrite.MAX_REWRITE_ATTEMPTS)

    def test_opt_in_on_falls_back_to_window_status_when_mapping_ambiguous(self):
        """対応付けがambiguous(claimがtarget/before/afterのどれとも十分に
        一致しない)な場合、安全側としてwindow全体のoverall_statusへ
        フォールバックする(match_fallback=True)。"""
        client = self._fake_client(["attempt1 text", "attempt2 text", "attempt3 text"])

        def check_fn(window_text):
            return {"overall_status": "LEDGER_DEVIATION",
                    "deviations": [{"claim_in_article": "completely unrelated vegetable content",
                                     "severity": "MAJOR"}]}

        deviation = {"issue": "issue", "explanation": "explanation", "changed_fact": True}
        result = local_rewrite.rewrite_ng_item(
            client, "fake-model", "medium", "LEDGER TEXT", "POINT CONTEXT",
            "Original NG sentence.", deviation, before_ctx="before.", after_ctx="after.",
            run_check_window_fn=check_fn, use_target_sentence_matching=True)
        # 3回ともambiguousなdeviationしか無く、window全体がLEDGER_DEVIATIONの
        # ままフォールバックし続けるため、最終的にhuman_review_requiredとなる
        # (安全側フォールバックが「誤って通す」方向には作用しないことの確認)。
        self.assertFalse(result["resolved"])
        self.assertTrue(result["human_review_required"])
        for attempt in result["attempts"]:
            self.assertEqual(attempt["ledger_status"], "LEDGER_DEVIATION")
            self.assertTrue(attempt["target_sentence_eval"]["match_fallback"])


# ============================================================
# A/B-Family両呼び出し元との整合(シグネチャ後方互換の確認)
# ============================================================
class CallerSignatureCompatibilityTests(unittest.TestCase):
    """A-Family(er003_v1_n3_01_articles_generate.py)・B-Family
    (er012_b_family_voices_writer_generic_01.py)は、いずれも
    rewrite_ng_item()を10個の位置引数のみで呼び出しており(11個目の
    use_target_sentence_matchingは渡さない)、既定Falseの挙動を維持した
    まま無変更で動作し続けることを、実際の呼び出しパターンを再現して
    確認する(両ファイル自体は本タスクでは変更しない、読取専用)。"""

    def test_ten_positional_args_call_pattern_still_works(self):
        client = __import__("unittest.mock", fromlist=["mock"]).Mock()
        resp = __import__("unittest.mock", fromlist=["mock"]).Mock()
        resp.output_text = "fixed text"
        client.responses.create.return_value = resp
        check_fn = lambda window_text: {"overall_status": "LEDGER_COMPLIANT"}
        deviation = {"issue": "i", "explanation": "e", "changed_fact": True}
        # A-Family/B-Family双方の実呼び出しと同じ10位置引数のみのパターン
        result = local_rewrite.rewrite_ng_item(
            client, "model", "medium", "LEDGER", "POINT CONTEXT", "ng sentence",
            deviation, "before.", "after.", check_fn)
        self.assertTrue(result["resolved"])
        self.assertEqual(set(result["attempts"][0].keys()), {"attempt", "text", "ledger_status"})


if __name__ == "__main__":
    unittest.main()
