# ============================================================
# er030_key_phrase_db_hybrid_m2_supply_01_test_01.py
# FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_02: M2供給のtest(TEST_PLAN_01 M-1〜7 / S-1〜7、Opus必須1〜4)。
# 有料API・ネットワークなし(Wiktionary照会はTrial snapshot再生、LLMはmock)。
# Trial module(er064_*)はこのtest内でのみimportする(Productionからは一切importしない=M-7)。
# ============================================================
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import os
import tempfile
import unittest
from unittest import mock

import er003_b1_p2_keywords as bk
import er003_v1_n3_01_scaffold_generate as sc
import er023_key_phrase_db_ingest as ing
import er030_key_phrase_db_hybrid_core_01 as core
import er030_key_phrase_db_hybrid_m2_supply_01 as m2
import er030_key_phrase_db_hybrid_selector_01 as sel
import er030_key_phrase_db_hybrid_source_reference_contract_01 as contract

# ---- Trial module(test内のみ) ----
import er064_kp_idiom_trial_01_matcher as TM
import er064_kp_idiom_trial_01_pipeline as TP
import er064_kp_int_01_machine as TMC
import er064_kp_opt_01_phase2_run_03 as TR
import er064_kp_opt_01_upstream_core as TU

R1_PATH = "er064_output/kp_integrated_opt_01/round1/shortlists_r1.json"
PREP_PATHS = [f"er064_output/kp_integrated_opt_01/round1/prep_stage{i}_r1.json" for i in (1, 2, 3)]
ARTICLE_KEYS = ["coffee_std", "coffee_adv", "meta_std", "meta_adv", "hormuz_std", "hormuz_adv",
                "smallbag_std", "smallbag_adv", "semi_std", "semi_adv"]

# P0無変更sha(WIRING_DESIGN_01 A-iii)
P0_TEMPLATE_FILE_SHA = "69d0e6ff548987896b561c0684e7aca10eae5b35a4974490fe92d42933d2e8f6"
P0_STATIC_SHA = "b8af4d50669fbd3e47de73f3b4f48e54226f293fa61697138397b190896d6025"
P0_GUIDANCE_SHA = "026aa7306afcde5cb8c4ee1f2b40928543909fe0fe4a371c4fe98affa5bcd08c"

# 逐語copy元(Trial)の関数ソースsha256(Er028UtilByteParityTests方式。Trial側が変われば検知する)
TRIAL_FUNCTION_SOURCE_SHA = {
    ("U", "_stem"): "0e6d87b8ec83367732dcd0485f3fa81820cff9dc2e357062d2cf3b84df87878f",
    ("U", "stem_tokens"): "db938cc0d9fd3fa086f693c3833c7d31aee9a2c4517e1954b997cb3048f383c4",
    ("U", "occurrences"): "14327257bb08fa6b650091a74edd2e3b949c3611e3743f13b35a88768d1d843d",
    ("U", "is_dictionary_registered"): "64e884875514378a5ec4c20787b914c577191fe841bf4a87ebcf7456ce71153b",
    ("U", "compute_containment"): "5f8f5935681e9bb7da6569aa160f08ebba943677f713170965c237d5d695e151",
    ("U", "all_closed_only"): "1e31414f3025ccdabbb72f39d84e1b32299dca543e98c7d3a45b8c6371156bf2",
    ("U", "fragment_risk"): "3e270fd7a7b450598cac129c5c5285849d463e154d1900089f3ae77e2cb6d9ad",
    ("U", "_first_pos"): "cee5678545b5d594df80044580f53c519044606b006984b445358573630c7e2c",
    ("U", "is_online_multiword_hit"): "bc5c7049452dd8e217507acdb83989f9f2a9a89e94fc8aabd34c23507dbe4953",
    ("U", "assemble_shortlist"): "84957e98e4d3973a6db4def9ae46665d191dc78670e561bbba47250315878cc2",
    ("M", "build_pattern_index"): "b44b1426b15f0d55e7bdef9d27390fddf56be9178b71b4f1fb426d2fc1da1b8e",
    ("M", "_lem"): "2c6463482d3de7931be77e9be6ff1cfd7651527d98e504832225e1407a8347ad",
    ("M", "_tok_match"): "0617aadda3eaf33a59460b70e2e31c84f674c8bcccc3755eb08a27b58d2977ad",
    ("M", "match_sentence_tokens"): "ed3df00c6a3071667fb25592197edc233978384615259994edd1c4f87a5c0fb0",
    ("M", "baseline_hit"): "766456575d58e7d81db4bf4f3f8994b9df0a5876175324da3e7323d0c904d942",
    ("M", "placeholder_candidates"): "f6eac103085c8e2644d4e69e466874bbd8dc4d4b5ee818179a3e61bce0e3d611",
    ("M", "rule_possessive_pattern_candidates"): "d8133afe14c7c27012505f816ce8b1629c97c3feb5cdcc2d42270a0e8ff22116",
    ("P", "min_content_zipf"): "beb6d70448330c647f40297a26955e771d2a97d31b6c1e9a6e11e6bcddd9f026",
    ("P", "reserved_sort_key"): "82acb5fef3fc01d205e4eb0d4d91231b6ccc838cfca4293f85a502033f719bd0",
    ("P", "_canon_set"): "2d084a483be74445be4544236e181cdaa8d4c282a6a89fe49cd1a3230079c490",
}
_TRIAL_MODS = {"U": TU, "M": TM, "P": TP}


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


_DBS = None


def dbs():
    global _DBS
    if _DBS is None:
        _DBS = core.load_group1_dbs()
    return _DBS


def _snapshot_lookups():
    """Trial snapshot再生(ネットワーク禁止)。snapshotに無い照会が出たらRuntimeErrorでtest失敗。"""
    snap = TU.Snapshot()
    return (mock.patch.object(ing, "wiktionary_multiword_targeted_lookup", snap.make_mw_lookup(False)),
            mock.patch.object(core, "wiktionary_unigram_lemma_lookup", snap.make_uni_lookup(False)))


def build_production_m2(key):
    text = TU.read_article(key)
    title = sel.extract_article_title(text)
    p1, p2 = _snapshot_lookups()
    with p1, p2:
        r = m2.build_m2_stage1_and_shortlist(text, dbs(), title)
    return text, title, r


def rows_text_for(r, title):
    """Trial `rows_for` と同形(static_instructions空)。Productionの注釈関数を使う。"""
    sl = r["shortlist_info"]["shortlist"]
    wc = contract.assign_candidate_ids(sl)
    ev = m2.make_annotating_evidence_fn(r["containment_pairs"], wc["shortlist_with_ids"], sel._compact_evidence_string)
    return contract.build_lightweight_user_message(title, wc["shortlist_with_ids"], r["shortlist_info"]["sentence_reference"],
                                                   "", "family_x", None, ev)


class VerbatimCopyTests(unittest.TestCase):
    """M-1: 純関数は逐語copy(第1段)。Trial定義とソース一致+sha256固定。"""

    def test_functions_source_identical_to_trial_and_pinned(self):
        for (mod_key, name), pinned in TRIAL_FUNCTION_SOURCE_SHA.items():
            trial_src = inspect.getsource(getattr(_TRIAL_MODS[mod_key], name))
            prod_src = inspect.getsource(getattr(m2, name))
            self.assertEqual(prod_src, trial_src, f"{name}: Trial定義と一致しません(逐語copyが崩れた)")
            self.assertEqual(_sha(trial_src), pinned, f"{name}: Trial側ソースが変わった(固定sha不一致)")

    def test_constants_identical_to_trial(self):
        self.assertEqual(m2.THREEGRAM_CAP, TU.THREEGRAM_CAP)
        self.assertEqual(m2.RESERVED_CAP, TMC.RESERVED_CAP)
        self.assertEqual(m2.RESERVED_CAP, TP.RESERVED_SLOT_CAP)
        self.assertEqual(m2.FRAG_START, TU.FRAG_START)
        self.assertEqual(m2.AUX_START, TU.AUX_START)
        self.assertEqual(m2.FRAG_START_NOAUX, TU.FRAG_START_NOAUX)
        self.assertEqual((m2.LABEL_CONTAINS, m2.LABEL_CONTAINED, m2.LABEL_FRAGMENT),
                         (TU.LABEL_CONTAINS, TU.LABEL_CONTAINED, TU.LABEL_FRAGMENT))
        self.assertEqual((m2.POSS, m2.OBJ, m2.REFL, m2.PLACE), (TM.POSS, TM.OBJ, TM.REFL, TM.PLACE))
        self.assertEqual(m2._FINITE_AUX, TM._FINITE_AUX)
        self.assertEqual(m2._SOURCE_PRIORITY, TP._SOURCE_PRIORITY)
        self.assertEqual(m2.CLOSED, TU.CLOSED)

    def test_m1_params_are_explicit_and_match_trial(self):
        """Opus必須2: 省略禁止のM1パラメータ。phase2_run_03 L124-125と一致。"""
        self.assertEqual(m2.M1_PARAMS, {"phrase_cap": 20, "realign": True, "u2": "tierH+S", "r2": True, "r3": True,
                                        "u3_exclude": True, "u3_annotate": True})
        src = inspect.getsource(TR.build_method1)
        for frag in ("u2=\"tierH+S\"", "u3_exclude=True", "u3_annotate=True", "phrase_cap=20", "realign=True", "r2=True", "r3=True"):
            self.assertIn(frag, src)
        self.assertEqual(m2.CURRENT_LOOKUP_WINDOW, core.DEFAULT_WIKTIONARY_MULTIWORD_LOOKUP_BUDGET)


class CoreResultsAppendOnlyTests(unittest.TestCase):
    """Opus必須1(Fable判断): coreの戻り値へ`results`を追記。既存の戻り値は不変。"""

    def test_results_key_added_existing_values_unchanged(self):
        text = TU.read_article("coffee_std")
        title = sel.extract_article_title(text)
        calls = []

        def fake_mw(cands, batch_size=50, sleep_sec=1.5):
            u = sorted(set(cands))
            calls.append(u)
            return {"results": {c: False for c in u}, "api_calls": 1, "elapsed_sec": 0.0, "candidate_count": len(u)}

        def fake_uni(cands, batch_size=50, sleep_sec=1.5):
            u = sorted(set(cands))
            return {"results": {c: False for c in u}, "api_calls": 0, "elapsed_sec": 0.0, "candidate_count": len(u)}

        with mock.patch.object(ing, "wiktionary_multiword_targeted_lookup", fake_mw), \
                mock.patch.object(core, "wiktionary_unigram_lemma_lookup", fake_uni):
            out = core.run_stage1_and_shortlist(text, dbs(), title)
        self.assertEqual(set(out), {"stage1", "shortlist_info", "results"})
        self.assertEqual(out["results"], {c: False for c in calls[0]})
        self.assertEqual(len(calls), 1)
        self.assertTrue(len(out["results"]) <= core.DEFAULT_WIKTIONARY_MULTIWORD_LOOKUP_BUDGET)
        self.assertIn("shortlist", out["shortlist_info"])
        self.assertIn("sentence_reference", out["shortlist_info"])


class SnapshotRegressionTests(unittest.TestCase):
    """M-2/M-3/M-6: Trial snapshot(¥0・ネットワークなし)でProduction版M2が Trial M2 と一致。"""

    @classmethod
    def setUpClass(cls):
        cls.r1 = json.load(open(R1_PATH, encoding="utf-8"))
        cls.built = {k: build_production_m2(k) for k in ARTICLE_KEYS}

    def test_rows_sha256_identical_to_trial_m2_all_10(self):
        for key in ARTICLE_KEYS:
            _text, title, r = self.built[key]
            exp = self.r1["articles"][key]
            self.assertEqual(title, exp["title"], key)
            rows = rows_text_for(r, title)
            self.assertEqual(_sha(rows), exp["M2"]["rows_sha256"], f"{key}: M2 rows sha不一致(B'方式の原因特定が必要)")
            self.assertEqual(rows, exp["M2"]["rows_text"], key)
            self.assertEqual(r["m2_meta"]["reserved"], exp["M2"]["reserved"], key)
            self.assertEqual(len(r["shortlist_info"]["shortlist"]), exp["M2"]["n_candidates"], key)

    def test_demoted_allow_identical_to_trial_current_window_survivors(self):
        """M-3(必須1 B'): 拡大1回+先頭60窓の再計算が、Trialの『現行窓で照会した場合のsurvivors』と同値。"""
        p1, p2 = _snapshot_lookups()
        for key in ARTICLE_KEYS:
            text = TU.read_article(key)
            title = sel.extract_article_title(text)
            st0 = core.run_stage1_for_article(text, dbs())
            plan = m2.compute_lookup_plan(st0)
            with p1 as _a, p2 as _b:
                exp_run = core.run_stage1_and_shortlist(text, dbs(), title, wiktionary_multiword_lookup_budget=plan["expanded_budget"])
            allow = m2.compute_demoted_allow(st0, plan, exp_run["results"], dbs())
            # Trial: 現行(予算60)窓の再生
            TR._init()
            cur = TR._replay(key, "default", 10, 60)
            self.assertEqual(allow, TR._mw_survivors(cur["stage1"]), key)
            self.assertEqual(plan["expanded_budget"], plan["n2"] + m2.THREEGRAM_CAP)

    def test_single_lookup_call_for_expanded_window(self):
        """照会は1回(2回照会に逃げない): multiword照会関数の呼出が1回で、候補数=n2+100(または全プール以下)。"""
        text = TU.read_article("coffee_std")
        title = sel.extract_article_title(text)
        snap = TU.Snapshot()
        mw = snap.make_mw_lookup(False)
        seen = []

        def spy(cands, batch_size=50, sleep_sec=1.5):
            seen.append(len(set(cands)))
            return mw(cands, batch_size, sleep_sec)
        with mock.patch.object(ing, "wiktionary_multiword_targeted_lookup", spy), \
                mock.patch.object(core, "wiktionary_unigram_lemma_lookup", snap.make_uni_lookup(False)):
            r = m2.build_m2_stage1_and_shortlist(text, dbs(), title)
        self.assertEqual(len(seen), 1)
        self.assertEqual(seen[0], min(r["m2_meta"]["expanded_budget"], len(m2.compute_lookup_plan(core.run_stage1_for_article(text, dbs()))["pool"])))

    def test_reserved_slot_cap3_outside_phrase_cap_and_no_match_label(self):  # M-4 / M-5
        for key in ARTICLE_KEYS:
            _t, title, r = self.built[key]
            meta = r["m2_meta"]
            self.assertLessEqual(len(meta["reserved"]), 3, key)
            rows = rows_text_for(r, title)
            self.assertNotIn("match:", rows, key)
            self.assertNotIn("| match", rows, key)
            for c in r["shortlist_info"]["shortlist"]:
                if c["canonical_form"] in meta["reserved"]:
                    self.assertIn(c.get("evidence"), ("placeholder_title", "rule_poss_pattern"))
        # 予約枠が実際に載る記事(coffee_std)では、予約枠候補がphrase cap(20)の外側に追加されている
        _t, title, r = self.built["coffee_std"]
        meta = r["m2_meta"]
        self.assertTrue(meta["reserved"])
        rows = rows_text_for(r, title)
        for canon in meta["reserved"]:
            line = [ln for ln in rows.splitlines() if f'"{canon}"' in ln or canon in ln.lower()]
            self.assertTrue(line, canon)
        ev_lines = [ln for ln in rows.splitlines() if "rule_poss_pattern" in ln or "placeholder_title[" in ln]
        self.assertTrue(ev_lines)

    def test_deterministic_twice(self):  # M-6
        for key in ("coffee_std", "semi_std"):
            _t, title, r1 = self.built[key]
            _t2, _title2, r2 = build_production_m2(key)
            self.assertEqual(_sha(rows_text_for(r1, title)), _sha(rows_text_for(r2, title)))

    def test_m2_meta_has_runtime_evidence_fields(self):
        _t, _title, r = self.built["coffee_std"]
        meta = r["m2_meta"]
        for k in ("kp_supply", "n2", "expanded_budget", "reserved", "overflow_beyond_cap", "dropped_non_contiguous",
                  "tier_h_dropped_after_reserved", "fragment_risk_candidates", "wiktionary_multiword_lookup",
                  "m2_lookup_seconds", "n_candidates"):
            self.assertIn(k, meta)
        self.assertEqual(meta["kp_supply"], "m2")


class FinalPromptParityGateTests(unittest.TestCase):
    """Opus必須3: Parity Gateは最終Promptで判定。Trial `build_ctx` 記録の `prompt_sha256`(M2P0 msg全文)と、
    Production経路 `build_production_selection_message` が作るメッセージshaが一致する。"""

    @classmethod
    def setUpClass(cls):
        cls.expected = {}
        for p in PREP_PATHS:
            d = json.load(open(p, encoding="utf-8"))["prompts"]
            for k, v in d.items():
                if k.endswith("_M2P0"):
                    cls.expected[k[:-len("_M2P0")]] = v["msg_sha256"]
        cls.static = sel.extract_static_instructions(bk.load_prompt_template())

    def test_p0_unchanged_sha(self):
        self.assertEqual(hashlib.sha256(open(bk.PROMPT_TEMPLATE_PATH, "rb").read()).hexdigest(), P0_TEMPLATE_FILE_SHA)
        self.assertEqual(_sha(self.static), P0_STATIC_SHA)
        self.assertEqual(_sha(contract._FAMILY_X_SOURCE_REFERENCE_SELECTION_GUIDANCE), P0_GUIDANCE_SHA)

    def test_final_message_sha_equals_trial_m2p0_for_recorded_articles(self):
        self.assertEqual(set(self.expected), {"coffee_std", "coffee_adv", "meta_std", "meta_adv", "hormuz_std", "hormuz_adv"})
        for key, exp_sha in self.expected.items():
            _t, title, r = build_production_m2(key)
            built = sel.build_production_selection_message(title, r["shortlist_info"], self.static, "family_x",
                                                           containment_pairs=r["containment_pairs"])
            self.assertEqual(_sha(built["message"]), exp_sha, f"{key}: 最終Prompt sha不一致(Parity Gate)")
            # 静的部・guidance部はP0そのまま、変わるのは候補行のみ
            self.assertTrue(built["message"].startswith(self.static.rstrip()))
            self.assertTrue(built["message"].rstrip().endswith(contract._FAMILY_X_SOURCE_REFERENCE_SELECTION_GUIDANCE.rstrip()))

    def test_annotation_id_table_built_from_span_corrected_shortlist(self):
        """Trialは補正前・Productionは補正後。補正で除外された候補への参照は捨てる。"""
        sl = [{"surface_form": "a b", "canonical_form": "a b", "candidate_id": "C1", "unit_type": "phrase"},
              {"surface_form": "a", "canonical_form": "a", "candidate_id": "C2", "unit_type": "word"}]
        pairs = [{"small": "a", "big": "a b", "tier": "S"}, {"small": "gone", "big": "a b", "tier": "S"},
                 {"small": "a", "big": "also gone", "tier": "S"}]
        ev = m2.make_annotating_evidence_fn(pairs, sl, lambda c: "BASE")
        self.assertEqual(ev(sl[0]), "BASE | contains: C2")
        self.assertEqual(ev(sl[1]), "BASE | contained_in: C1")
        sl2 = [dict(sl[0], fragment_risk=True, evidence="rule_poss_pattern")]
        self.assertEqual(m2.make_annotating_evidence_fn([], sl2, lambda c: "BASE")(sl2[0]), "rule_poss_pattern | fragment_risk")
        sl3 = [dict(sl[0], evidence="placeholder_title", matched_title="pump one's fist")]
        self.assertEqual(m2.make_annotating_evidence_fn([], sl3, lambda c: "BASE")(sl3[0]), "placeholder_title[pump one's fist]")


class DanglingReferenceTests(unittest.TestCase):
    """M-7: Production moduleはTrial module(er064_*/er057_*)をimportしない。"""

    def test_no_trial_imports_in_production_modules(self):
        for path in ("er030_key_phrase_db_hybrid_m2_supply_01.py", "er030_key_phrase_db_hybrid_selector_01.py",
                     "er030_key_phrase_db_hybrid_core_01.py", "er003_v1_n3_01_scaffold_generate.py",
                     "er019_family_x_style_profile_01.py", "er019_family_x_audio_production_runner_01.py",
                     "er063_family_z_audio_01.py"):
            tree = ast.parse(open(path, encoding="utf-8").read())
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [node.module or ""]
                for n in names:
                    for bad in ("er064_", "er057_", "er065_", "er068_", "er069_"):
                        self.assertFalse(n.startswith(bad), f"{path} imports Trial/unapproved module {n}")


# ------------------------------------------------------------
# S: selector配線(LLM・Wiktionary照会はmock)
# ------------------------------------------------------------
def _min_shortlist_info(n=20):
    sl = []
    for i in range(n):
        sl.append({"surface_form": f"phr{i} x", "canonical_form": f"phr{i} x", "unit_type": "phrase",
                   "important_noun_phrase_candidate": False, "occurrence_count_in_article": 1,
                   "context_sentence_id": "S1", "matched_dbs": [], "db_categories": []})
    return {"shortlist": sl, "shortlist_total_count": n, "phrase_included_count": 10,
            "important_noun_included_count": 5, "word_included_count": 5,
            "sentence_reference": {"S1": "A test sentence " + " ".join(f"phr{i} x" for i in range(n)) + "."}}


def _fake_m2_result():
    return {"stage1": {}, "shortlist_info": _min_shortlist_info(),
            "containment_pairs": [{"small": "phr1 x", "big": "phr0 x", "tier": "S"}],
            "m2_meta": {"kp_supply": "m2", "reserved": ["phr19 x"], "n_candidates": 20}}


_PASS_GATE = {"status": "KEY_WORDS_STRUCTURE_PASS", "parsed": {"items": []}, "model_id": "fake-model",
              "response_id": "resp_1", "raw_text": "{}", "restore_telemetry": {}, "validation_reasons": [], "item_reasons": []}


class SelectorWiringTests(unittest.TestCase):
    def _run(self, cache=None, supply="m2", m2_side_effect=None, m2_return=None, core_return=None, **kw):
        out_dir = tempfile.mkdtemp()
        with mock.patch.object(m2, "build_m2_stage1_and_shortlist", side_effect=m2_side_effect,
                               return_value=m2_return if m2_return is not None else _fake_m2_result()) as mm2, \
                mock.patch.object(core, "run_stage1_and_shortlist",
                                  return_value=core_return or {"stage1": {}, "shortlist_info": _min_shortlist_info()}) as mcore, \
                mock.patch.object(sel.src_ref_contract, "make_instrumented_selector_factory") as mfac, \
                mock.patch.object(sel.src_ref_contract, "run_source_reference_contract_gate", return_value=dict(_PASS_GATE)), \
                mock.patch.object(sel.pricing, "cost_jpy_for_call", return_value=0.5):
            try:
                result = sel.run_db_hybrid_selection(
                    "A test sentence with enough words to pass basic checks.", out_dir, "T_M2", "A2_SUPPORT",
                    process=None, dbs={}, shortlist_cache=cache, candidate_supply=supply, **kw)
            except sel.DbHybridFailure as e:
                return e, mm2, mcore, mfac, out_dir
        return result, mm2, mcore, mfac, out_dir

    def test_m2_is_default_and_telemetry_kp_supply(self):  # S-2
        out_dir = tempfile.mkdtemp()
        with mock.patch.object(m2, "build_m2_stage1_and_shortlist", return_value=_fake_m2_result()) as mm2, \
                mock.patch.object(core, "run_stage1_and_shortlist") as mcore, \
                mock.patch.object(sel.src_ref_contract, "make_instrumented_selector_factory"), \
                mock.patch.object(sel.src_ref_contract, "run_source_reference_contract_gate", return_value=dict(_PASS_GATE)), \
                mock.patch.object(sel.pricing, "cost_jpy_for_call", return_value=0.5):
            result = sel.run_db_hybrid_selection("A test sentence with enough words to pass basic checks.", out_dir,
                                                 "T", "A2_SUPPORT", process=None, dbs={})
        mm2.assert_called_once()
        mcore.assert_not_called()
        self.assertEqual(result["kp_supply"], "m2")
        self.assertEqual(result["m2_report"]["m2_meta"]["reserved"], ["phr19 x"])
        self.assertTrue(os.path.exists(os.path.join(out_dir, "m2_supply_report.json")))
        meta = json.load(open(os.path.join(out_dir, "keywords_runtime_metadata.json"), encoding="utf-8"))
        self.assertEqual(meta["kp_supply"], "m2")
        msg = open(os.path.join(out_dir, "keywords_selector_prompt.txt"), encoding="utf-8").read()
        self.assertIn("| contains: C", msg)  # 注釈が実送信Promptに入る
        self.assertNotIn("match:", msg)
        self.assertEqual(sel.src_ref_contract.SOURCE_REFERENCE_CONTRACT_ID, result["source_reference_contract"])

    def test_m0_still_available_and_has_no_kp_supply(self):
        result, mm2, mcore, _mf, _d = self._run(supply="m0")
        mm2.assert_not_called()
        mcore.assert_called_once()
        self.assertIsNone(result["kp_supply"])
        self.assertIsNone(result["m2_report"])

    def test_invalid_candidate_supply_rejected(self):
        with self.assertRaises(ValueError):
            sel.run_db_hybrid_selection("x", tempfile.mkdtemp(), "T", "A2_SUPPORT", dbs={}, candidate_supply="m3")

    def test_family_z_still_not_implemented(self):  # S-7
        with self.assertRaises(NotImplementedError):
            sel.run_db_hybrid_selection("x", tempfile.mkdtemp(), "T", "A2_SUPPORT", dbs={}, family_profile="family_z")

    def test_retry_with_cache_does_not_requery_and_annotations_identical(self):  # S-3(+pairs/m2メタ cache同一)
        cache = {}
        r1, mm2, _c, _f, d1 = self._run(cache=cache)
        r2, mm2b, _c2, _f2, d2 = self._run(cache=cache)
        self.assertEqual(mm2.call_count, 1)
        self.assertEqual(mm2b.call_count, 0)  # cache hit: M2構築(Wiktionary照会)を再実行しない
        self.assertEqual(len(cache), 1)
        cached = list(cache.values())[0]
        self.assertIn("containment_pairs", cached)
        self.assertIn("m2_meta", cached)
        m1 = open(os.path.join(d1, "keywords_selector_prompt.txt"), encoding="utf-8").read()
        m2_ = open(os.path.join(d2, "keywords_selector_prompt.txt"), encoding="utf-8").read()
        self.assertEqual(m1, m2_)  # cache hit時も注釈が同一
        self.assertEqual(r1["m2_report"]["m2_meta"], r2["m2_report"]["m2_meta"])

    def test_wiktionary_failure_uses_selector_exception_reason_and_never_falls_to_m0(self):  # S-4 / 必須4
        e, mm2, mcore, _f, _d = self._run(m2_side_effect=m2.M2LookupFailure("HTTPError: 429"))
        self.assertIsInstance(e, sel.DbHybridFailure)
        self.assertEqual(e.reason_code, "SELECTOR_EXCEPTION")
        self.assertTrue(e.fallback_allowed)
        self.assertEqual(e.telemetry.get("kp_supply_attempted"), "m2")
        mcore.assert_not_called()  # M0へ黙って落ちない

    def test_m2_internal_exception_has_distinct_reason_code(self):  # 必須4
        e, _mm2, mcore, _f, _d = self._run(m2_side_effect=m2.M2SupplyInternalError("KeyError: 'x'"))
        self.assertEqual(e.reason_code, "M2_SUPPLY_EXCEPTION")
        self.assertTrue(e.fallback_allowed)  # Fable判断: 既存Strategy L fallbackに乗せる(新STOP条件なし)
        self.assertEqual(e.telemetry["reason_code"], "M2_SUPPLY_EXCEPTION")
        mcore.assert_not_called()

    def test_fallback_telemetry_records_reason_and_no_kp_supply(self):
        """fallback発火時: telemetryにreason_code、kp_supplyは付かない(M2未発火=evidence不成立)。"""
        tmp = tempfile.mkdtemp()
        tel = os.path.join(tmp, "telemetry.jsonl")
        fail = sel.DbHybridFailure("M2_SUPPLY_EXCEPTION", "x", telemetry={"reason_code": "M2_SUPPLY_EXCEPTION",
                                                                          "kp_supply_attempted": "m2"})
        with mock.patch.object(sc, "KP_BACKEND_TELEMETRY_PATH", tel), \
                mock.patch("er030_key_phrase_db_hybrid_selector_01.run_db_hybrid_selection", side_effect=fail), \
                mock.patch.object(sc, "_run_key_phrase_selection_strategy_l", return_value={"status": "KEY_WORDS_STRUCTURE_PASS"}):
            res = sc._run_key_phrase_selection_db_hybrid_with_fallback("art", tmp, "T", "A2", process=None)
        self.assertEqual(res["kp_backend_used"], "strategy_l_fallback")
        row = json.loads(open(tel, encoding="utf-8").read().splitlines()[-1])
        self.assertEqual(row["fallback_reason_code"], "M2_SUPPLY_EXCEPTION")
        self.assertEqual(row["kp_supply_attempted"], "m2")
        self.assertNotIn("kp_supply", row)

    def test_success_telemetry_has_kp_supply_and_m2_summary(self):
        tmp = tempfile.mkdtemp()
        tel = os.path.join(tmp, "telemetry.jsonl")
        ok = {"status": "KEY_WORDS_STRUCTURE_PASS", "parsed": {"items": []}, "original_items": [], "model_id": "m",
              "cost_jpy": 1.0, "shortlist_total_count": 20, "kp_backend": "db_hybrid", "kp_supply": "m2",
              "m2_report": {"m2_meta": {"n_candidates": 20, "reserved": ["a b c"]},
                            "selected_reserved_slot_candidates": [], "selected_fragment_risk_candidates": []}}
        with mock.patch.object(sc, "KP_BACKEND_TELEMETRY_PATH", tel), \
                mock.patch("er030_key_phrase_db_hybrid_selector_01.run_db_hybrid_selection", return_value=ok):
            res = sc._run_key_phrase_selection_db_hybrid_with_fallback("art", tmp, "T", "A2", process=None)
        self.assertEqual(res["kp_backend_used"], "db_hybrid")
        row = json.loads(open(tel, encoding="utf-8").read().splitlines()[-1])
        self.assertEqual(row["kp_supply"], "m2")
        self.assertEqual(row["m2_summary"]["reserved"], ["a b c"])
        rm = json.load(open(os.path.join(tmp, "keywords_runtime_metadata.json"), encoding="utf-8"))
        self.assertEqual(rm["kp_backend_kp_supply"], "m2")


class UnchangedLimitsTests(unittest.TestCase):
    def test_retry_and_cost_limits_unchanged(self):  # S-5
        import er003_key_words_production as prod
        self.assertEqual(prod.MAX_PRODUCTION_RETRY_ATTEMPTS, 2)
        self.assertEqual(sel.KP_ARTICLE_COST_CAP_JPY, 15.0)
        self.assertEqual(sc.KEY_PHRASE_REDUNDANCY_RETRY_MAX, 2)
        self.assertEqual(sel.MIN_SHORTLIST_COUNT, 12)

    def test_family_z_kp_stage_still_strategy_l(self):  # S-7(Z-1未決の間のguard)
        src = open("er062_family_z_writer_01.py", encoding="utf-8").read()
        i = src.index("def run_kp_stage")
        seg = src[i:i + 3000]
        self.assertNotIn("kp_backend", seg)
        self.assertNotIn("db_hybrid", seg)
        zsrc = open("er026_family_z_fiction_production_runner_01.py", encoding="utf-8").read()
        self.assertNotIn("kp_backend", zsrc)
        self.assertNotIn("m2_supply", zsrc)


class ScaffoldOnlyKpTests(unittest.TestCase):
    """Opus Q5条件: `--scaffold-only kp`。S-6。(i)run_key_phrases呼出は同じ行を通す・support生成skip (ii)article sha記録/scaffold_run_summary/
    kp_backend_used維持 (iii)support成果物が無ければSTOP (iv)KP再生成は1レベル1回。"""

    SRC_DIR = "er019_output/coffee_prices/run_v5_ms_01"

    def setUp(self):
        import er019_family_x_audio_production_runner_01 as runner
        self.runner = runner
        self.out = tempfile.mkdtemp()

    def _put_support(self, levels):
        for lv in levels:
            os.makedirs(f"{self.out}/{lv}", exist_ok=True)
            name = "b1_support_texts.json" if lv == "b1b" else "a2_support_texts.json"
            with open(f"{self.out}/{lv}/{name}", "w", encoding="utf-8") as f:
                f.write("{}")

    def _kp_result(self):
        return {"canonicalization": {"status": "OK"}, "selection": {"status": "KEY_WORDS_STRUCTURE_PASS", "kp_backend_used": "db_hybrid"}}

    def test_kp_only_skips_support_generation_and_keeps_records(self):
        self._put_support(["a2", "b1b"])
        calls = []
        budget_notes = []
        with mock.patch.object(self.runner.sc, "run_key_phrases", side_effect=lambda *a, **k: (calls.append((a, k)), self._kp_result())[1]), \
                mock.patch.object(self.runner, "run_family_x_a2_scaffold") as ma2, \
                mock.patch.object(self.runner, "run_family_x_b1_scaffold") as mb1:
            res = self.runner.run_theme_scaffold(None, self.SRC_DIR, self.out, ["a2", "b1b"], scaffold_only="kp",
                                                 budget_check=budget_notes.append)
        ma2.assert_not_called()
        mb1.assert_not_called()                                    # support(Preview/Comment)は再生成しない
        self.assertEqual(len(calls), 2)                            # Std -> Adv 直列で各1回
        for (a, k), lv in zip(calls, ("a2", "b1b")):
            self.assertEqual(k.get("kp_backend"), "db_hybrid")     # 既存と同じ呼出(kp_backend引数)
            self.assertEqual(a[3], lv)
        self.assertEqual(res["a2"]["kp_backend_used"], "db_hybrid")
        self.assertEqual(res["b1b"]["scaffold_only"], "kp")
        self.assertTrue(os.path.exists(f"{self.out}/audit/scaffold_article_sha256.json"))     # (ii)
        summ = json.load(open(f"{self.out}/scaffold_run_summary.json", encoding="utf-8"))
        self.assertEqual(summ["a2"]["kp_backend_used"], "db_hybrid")
        self.assertEqual(budget_notes, ["after scaffold a2", "after scaffold b1b"])

    def test_missing_support_stops_before_any_kp_call(self):                                     # (iii)
        with mock.patch.object(self.runner.sc, "run_key_phrases") as mk:
            with self.assertRaises(RuntimeError) as cm:
                self.runner.run_theme_scaffold(None, self.SRC_DIR, self.out, ["a2"], scaffold_only="kp")
        mk.assert_not_called()
        self.assertIn("support成果物", str(cm.exception))

    def test_existing_kp_artifacts_stop_one_kp_regeneration_per_level(self):                     # (iv)
        self._put_support(["a2"])
        os.makedirs(f"{self.out}/a2/key_phrases", exist_ok=True)
        with open(f"{self.out}/a2/key_phrases/keywords_runtime_metadata.json", "w") as f:
            f.write("{}")
        with mock.patch.object(self.runner.sc, "run_key_phrases") as mk:
            with self.assertRaises(RuntimeError) as cm:
                self.runner.run_theme_scaffold(None, self.SRC_DIR, self.out, ["a2"], scaffold_only="kp")
        mk.assert_not_called()
        self.assertIn("1レベル1回", str(cm.exception))

    def test_default_scaffold_unchanged_generates_support(self):
        # scaffold_only未指定は従来どおりsupport生成を呼ぶ(挙動不変)
        with mock.patch.object(self.runner.sc, "run_key_phrases", return_value=self._kp_result()), \
                mock.patch.object(self.runner, "run_family_x_a2_scaffold", return_value={"preview": {"status": "OK"}}) as ma2:
            res = self.runner.run_theme_scaffold(None, self.SRC_DIR, self.out, ["a2"])
        ma2.assert_called_once()
        self.assertNotIn("scaffold_only", res["a2"])

    def test_invalid_scaffold_only_rejected(self):
        with self.assertRaises(ValueError):
            self.runner.run_theme_scaffold(None, self.SRC_DIR, self.out, ["a2"], scaffold_only="support")

    def test_kp_backend_remains_last_default(self):
        self.assertEqual(self.runner.run_theme_scaffold.__defaults__[-1], "db_hybrid")


if __name__ == "__main__":
    unittest.main()
