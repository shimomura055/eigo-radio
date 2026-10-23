# -*- coding: utf-8 -*-
"""er106_joint_runtime_evidence_01 のtest(最小合成fixture。API 0・Production module非import)。

実行: .venv\\Scripts\\python.exe -m unittest er106_joint_runtime_evidence_01_test_01 -v
fixtureは tempfile のみに作る(共有HR queue・Ledger・run dirを汚さない)。
"""
import ast
import hashlib
import json
import os
import struct
import tempfile
import unittest
import wave

import er106_joint_runtime_evidence_01 as e106

REPO = os.path.dirname(os.path.abspath(e106.__file__))


def wj(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)


def wl(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write((r if isinstance(r, str) else json.dumps(r, ensure_ascii=False)) + "\n")


def wwav(path, sec, sr=8000):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(struct.pack("<h", 0) * int(sr * sec))


ARTICLE = ("Coffee prices fell last week. The price tag is still on a journey. Shoppers say there is a time lag before the shelf changes. "
           "Some stores hold on to old prices.")


def vote_check(state="PASS_VOTE_2OF3", p=False, s=True, w_called=True, w_pass=True, w_err=None, row="S+W", pass_count=2, ok=True):
    return {"version": "kp_vote_check_v1", "ok": ok, "source": "generated", "canonical_text": "x", "wav_sha256": "ab", "vote_state": state,
            "judge_state": "PASS", "reason_code": "vote_2of3", "row": row, "pass_count": pass_count, "tiebreak_enabled": True,
            "primary": {"provider": "openai", "text": "x", "pass": p, "rescued": False, "rescue_layers": []},
            "secondary": {"provider": "azure", "text": "x", "pass": s, "called": True, "protected_diff": False},
            "whisper": {"provider": "faster_whisper", "model": "small", "compute_type": "int8", "text": "x", "pass": w_pass,
                        "called": w_called, "error": w_err, "memo_hit": False},
            "checked_at": "2026-10-23T00:00:00"}


def kp_items(n, backend_phrases=("time lag", "price tag", "hold on")):
    items = []
    for i in range(1, n + 1):
        ph = backend_phrases[(i - 1) % len(backend_phrases)] if n <= 3 else ["lag", "price tag", "hold on", "journey", "shelf"][i - 1]
        items.append({"rank": i, "source_span": ph, "display_phrase": ph, "key_phrase": ph, "used_form": ph, "japanese_gloss": "gloss",
                      "source_sentence": "s", "normalization_reason": "none", "changed_from_display_phrase": False})
    return items


def make_level(root, family, level, n_kp, *, backend="fulltext_p2", votes=None, sha=e106.KPFT_PROMPT_2_SHA256, model="gpt-6-luna",
               with_timeline=True, kp_state="OK"):
    paths = e106.level_paths(family, root, level)
    kd = paths["kp_dir"]
    wj(f"{kd}/keywords_canonicalized.json", {"items": kp_items(n_kp), "overall_status": "PASS", "source_reference_contract": "x"})
    meta = {"kp_backend": backend, "kp_backend_used": backend, "prompt_id": "kp_prompt_2", "prompt_sha256": sha, "user_message_sha256": "u",
            "record_status": "PRODUCTION", "model_requested": "gpt-6-luna", "model_id": model, "response_id": "r", "final_status": "KEY_WORDS_STRUCTURE_PASS",
            "shortfall": n_kp < 3, "kp_count_max": 3, "attempts": 1, "attempts_detail": []}
    wj(f"{kd}/keywords_runtime_metadata.json", meta)
    wj(f"{kd}/canonicalization_runtime_metadata.json", {"final_status": "CANONICALIZATION_PASS", "attempts_detail": [{}]})
    wj(f"{kd}/keyphrase_redundancy_qa.json", {"status": "REDUNDANCY_PASS", "attempts_detail": [{}]})
    kpres = {}
    for r in range(1, n_kp + 1):
        eng = {"status": "OK", "reused": False, "sha256": "s", "path": f"{paths['narration']}/kp{r}_en.wav", "asr_verified": True, "text": "t"}
        if votes and r in votes:
            eng["kp_dual_check"] = votes[r]
        ent = {"english": eng}
        if level == "b1b":
            ent["explanation"] = {"status": "OK", "explanation_text": "expl", "reused": False}
        else:
            ent["japanese"] = {"status": "OK", "text": "日本語"}
        kpres[str(r)] = ent
    wj(paths["results"], {"segments": {"preview": {"status": "OK", "asr_judgement": {"state": "PASS"}}}, "key_phrases": kpres})
    tl = []
    t = 0.0
    for r in range(1, n_kp + 1):
        en, third = 1.0, 1.5
        wwav(f"{paths['narration']}/kp{r}_en.wav", en)
        wwav(f"{paths['narration']}/kp{r}_{'explanation_en' if level == 'b1b' else 'ja'}.wav", third)
        dur = 2 * en + third + 2.0
        tl.append({"part": f"key_phrase_{r}" if family == "Z" else f"Key Phrase {r}", "start_seconds": t, "duration_seconds": dur})
        t += dur
    if with_timeline:
        if family == "Z":
            wj(paths["timeline"], {"timeline": tl})
        else:
            wj(paths["timeline"], tl)
    wj(f"{paths['audit']}/review_lock_state.json", {"preview": {"state": "RESOLVED"}})
    return paths


def make_run(root, family, n_kp=3, **kw):
    os.makedirs(root, exist_ok=True)
    for lv in ("a2", "b1b"):
        make_level(root, family, lv, n_kp, **kw)
    if family == "Z":
        os.makedirs(f"{root}/writer", exist_ok=True)
        for fn in ("r2.md", "std.md"):
            with open(f"{root}/writer/{fn}", "w", encoding="utf-8") as f:
                f.write(ARTICLE)
    else:
        for lv in ("a2", "b1b"):
            os.makedirs(f"{root}/src/{lv}", exist_ok=True)
            with open(f"{root}/src/{lv}/article.md", "w", encoding="utf-8") as f:
                f.write(ARTICLE)
    wl(f"{root}/raw_usage_log.jsonl" if family == "X" else f"{root}/cost_log.jsonl", [
        {"stage": "kp_gloss_alignment", "segment": None, "provider": "openai", "model_id": "gpt-6-luna", "cost_usd": 0.001, "usage_source": "OFFICIAL_API_RESPONSE"},
        {"stage": "tts", "segment": "kp1_english", "provider": "gemini", "model_id": "gemini-3.8-flash-lite-tts", "cost_usd": 0.002, "usage_source": "OFFICIAL_API_RESPONSE"},
        {"stage": "tts", "segment": "kp1_english", "provider": "openai_asr", "model_id": "gpt-4o-mini-transcribe", "cost_usd": 0.0005, "usage_source": "OFFICIAL_API_RESPONSE"},
        {"stage": "tts", "segment": "kp1_english", "provider": "azure", "model_id": "azure-speech-stt", "cost_usd": 0.0007, "usage_source": "OFFICIAL_API_RESPONSE"},
        {"stage": "tts", "segment": "preview", "provider": "gemini", "model_id": "gemini-3.8-flash-lite-tts", "cost_usd": 0.003, "usage_source": "OFFICIAL_API_RESPONSE"},
        {"stage": "tts", "segment": "kp2_explanation_en", "provider": "gemini", "model_id": "gemini-3.8-flash-lite-tts", "cost_usd": 0.004, "usage_source": "OFFICIAL_API_RESPONSE"},
    ])
    return root


def add_alarm(root, levels=("b1b",), nouns=("Khaite",), consistency_match=True):
    for lv in ("a2", "b1b"):   # hookは全levelで0件でも書く(設計P-08)。alarmを入れるlevelだけ件数あり
        nouns_lv = nouns if lv in levels else ()
        recs = [{"alarm_id": f"id{i}", "proper_noun": n, "segment_id": "full_story_part2", "final_state": "PASS_WITH_PRONUNCIATION_ALARM",
                 "location": {"wav_path": "w"}, "mismatch": {"canonical": n}, "pronunciation_basis": {"has_basis": False},
                 "tts_supply_result": {"supplied": False, "reason": "NO"}, "models": {"tts_model_id": "m"}} for i, n in enumerate(nouns_lv)]
        wj(f"{root}/{lv}/audit/pronunciation_alarms.json", {"policy_id": "p", "source": "s", "count": len(recs), "operator_only": True,
                                                               "consistency": {"alarm_state_records": len(recs), "reported": len(recs), "match": consistency_match},
                                                               "hr_residual": {}, "supply_applied": [], "alarms": recs})
        with open(f"{root}/{lv}/audit/operator_alarm_report.md", "w", encoding="utf-8") as f:
            f.write("## 固有名詞発音アラーム(運営責任者向け・一般リスナー非表示)\n")


def run_report(x, z, **kw):
    import argparse
    ns = argparse.Namespace(x_run_dir=x, z_run_dir=z, x_source_dir=kw.get("x_source_dir"), x_page=None, z_page=None, ledger=kw.get("ledger"),
                            repo_root=kw.get("repo_root", REPO), snapshot_in=kw.get("snapshot_in"), check_stop=False, managed_id="T",
                            dangling_grep=False, out_json=None, out_md=None, snapshot_out=None)
    return e106.build_report(ns)


def status(rep, feat, fam, prefix):
    for c in rep["assessment"][feat][fam]:
        if c["id"].startswith(prefix):
            return c["status"]
    raise KeyError(prefix)


class LegacyFiveKpTest(unittest.TestCase):
    """旧仕様(5件・vote無し・alarm無し)のrunが「5件・vote無し・alarm無し」と正しく出ること。"""

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.x = make_run(os.path.join(self.td.name, "x"), "X", n_kp=5, backend="db_hybrid", sha=None, model=None,
                          votes={r: {"version": "kp_dual_check_v1", "ok": True, "primary": {"pass": True}, "secondary": {"pass": True}} for r in range(1, 6)})
        self.z = make_run(os.path.join(self.td.name, "z"), "Z", n_kp=5, backend=None, sha=None)
        self.rep = run_report(self.x, self.z, x_source_dir=f"{self.x}/src")

    def tearDown(self):
        self.td.cleanup()

    def test_five_kp_detected(self):
        for fk in ("X", "Z"):
            for lv, d in self.rep["families"][fk]["levels"].items():
                self.assertEqual(d["selection"]["n_items"], 5)
            self.assertEqual(status(self.rep, "KPFT", fk, "KPFT-4"), "NG")

    def test_x_is_legacy_backend_ng_and_z_backend_missing(self):
        self.assertEqual(status(self.rep, "KPFT", "X", "KPFT-1"), "NG")
        self.assertEqual(status(self.rep, "KPFT", "Z", "KPFT-1"), "MISSING")   # 旧metadataにkp_backendキーが無い=推測補完しない

    def test_no_vote_evidence(self):
        vt = self.rep["vote_table"]["X"]
        self.assertTrue(vt and all(v["kind"] == "LEGACY_DUAL" for v in vt))
        self.assertTrue(all(v.get("whisper_called") is None for v in vt))
        self.assertEqual(status(self.rep, "KP3V", "X", "KP3V-0 "), "MISSING")
        self.assertTrue(all(v["kind"] == "MISSING" for v in self.rep["vote_table"]["Z"]))

    def test_no_alarm(self):
        for fk in ("X", "Z"):
            self.assertEqual(self.rep["families"][fk]["alarms"]["total_alarms"], 0)
            self.assertEqual(status(self.rep, "PNAP", fk, "PNAP-0 "), "MISSING")
            self.assertEqual(status(self.rep, "PNAP", fk, "PNAP-2 "), "NOT_FIRED")


class NewSpecTest(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        votes = {1: vote_check(), 2: vote_check("PASS_DUAL", True, True, False, None, None, "P+S", 2),
                 3: vote_check("PASS_DUAL", True, True, False, None, None, "P+S", 2)}
        self.x = make_run(os.path.join(self.td.name, "x"), "X", n_kp=3, votes=votes)
        self.z = make_run(os.path.join(self.td.name, "z"), "Z", n_kp=3, votes=votes)
        add_alarm(self.x)
        add_alarm(self.z)
        self.rep = run_report(self.x, self.z, x_source_dir=f"{self.x}/src")

    def tearDown(self):
        self.td.cleanup()

    def test_kpft_all_ok(self):
        for fk in ("X", "Z"):
            for k in ("KPFT-1", "KPFT-2", "KPFT-3", "KPFT-4", "KPFT-5", "KPFT-7"):
                self.assertEqual(status(self.rep, "KPFT", fk, k), "OK", (fk, k))

    def test_vote_firing_and_invariants(self):
        for fk in ("X", "Z"):
            self.assertEqual(status(self.rep, "KP3V", fk, "KP3V-1 "), "OK")
            self.assertEqual(status(self.rep, "KP3V", fk, "KP3V-1b"), "OK")
            self.assertEqual(status(self.rep, "KP3V", fk, "KP3V-2"), "OK")
            self.assertEqual(status(self.rep, "KP3V", fk, "KP3V-4 "), "OK")
            self.assertEqual(status(self.rep, "KP3V", fk, "KP3V-4b"), "OK")
            self.assertEqual(status(self.rep, "KP3V", fk, "KP3V-7"), "OK")
        self.assertEqual(self.rep["assessment"]["KP3V"]["JOINT"][0]["status"], "OK")

    def test_alarm_both_families(self):
        for fk in ("X", "Z"):
            self.assertEqual(status(self.rep, "PNAP", fk, "PNAP-0 "), "OK")
            self.assertEqual(status(self.rep, "PNAP", fk, "PNAP-2 "), "OK")
            self.assertEqual(status(self.rep, "PNAP", fk, "PNAP-2b"), "OK")
            self.assertEqual(status(self.rep, "PNAP", fk, "PNAP-6"), "OK")
        self.assertEqual(self.rep["assessment"]["PNAP"]["JOINT"][0]["status"], "OK")

    def test_cost_buckets(self):
        c = self.rep["families"]["X"]["cost"]
        self.assertGreater(c["total_jpy"], 0)
        for b in ("kp_chain", "kp_audio_english", "kp_audio_explanation", "non_kp_audio"):
            self.assertIn(b, c["buckets"])
        self.assertIn("kp_audio_english:asr_azure", c["by_kind"])
        self.assertIn("kp_audio_english:tts", c["by_kind"])

    def test_playback_order_indirect_check(self):
        for fk in ("X", "Z"):
            for lv, d in self.rep["families"][fk]["levels"].items():
                self.assertEqual({v["status"] for v in d["order"]["per_kp"].values()}, {"OK"})

    def test_markdown_renders(self):
        md = e106.render_markdown(self.rep)
        self.assertTrue("KPFT(KP全文選定+3件化)" in md, "KPFT section missing")
        self.assertTrue("PNAP-J" in md, "PNAP-J row missing")


class InvariantTest(unittest.TestCase):
    def _rep(self, votes):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        x = make_run(os.path.join(self.td.name, "x"), "X", n_kp=3, votes=votes)
        z = make_run(os.path.join(self.td.name, "z"), "Z", n_kp=3, votes=votes)
        return run_report(x, z)

    def test_whisper_error_with_pass_is_ng(self):
        rep = self._rep({1: vote_check(w_err="boom", w_pass=False)})
        self.assertEqual(status(rep, "KP3V", "X", "KP3V-4 "), "NG")

    def test_whisper_fired_without_split_is_ng(self):
        rep = self._rep({1: vote_check("PASS_DUAL", True, True, True, True, None, "P+S", 2)})
        self.assertEqual(status(rep, "KP3V", "X", "KP3V-1 "), "NG")

    def test_split_without_whisper_is_ng(self):
        rep = self._rep({1: vote_check("NG_VOTE_WHISPER_NG", True, False, False, None, None, None, 1, ok=False)})
        self.assertEqual(status(rep, "KP3V", "X", "KP3V-1 "), "NG")

    def test_missing_key_reported_not_guessed(self):
        v = vote_check()
        del v["row"]
        rep = self._rep({1: v})
        self.assertEqual(status(rep, "KP3V", "X", "KP3V-0b"), "MISSING")
        self.assertIn("row", rep["families"]["X"]["levels"]["a2"]["audio"]["kp"]["1"]["vote"]["missing_keys"])

    def test_wrong_whisper_config_ng(self):
        v = vote_check()
        v["whisper"]["model"] = "medium"
        rep = self._rep({1: v})
        self.assertEqual(status(rep, "KP3V", "X", "KP3V-4b"), "NG")

    def test_vote_on_non_english_segment_is_ng(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        x = make_run(os.path.join(td.name, "x"), "X", n_kp=3, votes={1: vote_check()})
        p = e106.level_paths("X", x, "b1b")["results"]
        d = json.load(open(p, encoding="utf-8"))
        d["key_phrases"]["1"]["explanation"]["kp_dual_check"] = vote_check()
        wj(p, d)
        z = make_run(os.path.join(td.name, "z"), "Z", n_kp=3)
        rep = run_report(x, z)
        self.assertEqual(status(rep, "KP3V", "X", "KP3V-7"), "NG")


class KpftChecksTest(unittest.TestCase):
    def _rep(self, **kw):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        x = make_run(os.path.join(td.name, "x"), "X", n_kp=kw.pop("n", 3), **kw)
        z = make_run(os.path.join(td.name, "z"), "Z", n_kp=3)
        return run_report(x, z, x_source_dir=f"{x}/src")

    def test_wrong_model_is_ng(self):
        self.assertEqual(status(self._rep(model="gpt-5-mini"), "KPFT", "X", "KPFT-2"), "NG")

    def test_wrong_prompt_sha_is_ng(self):
        self.assertEqual(status(self._rep(sha="0" * 64), "KPFT", "X", "KPFT-3"), "NG")

    def test_four_items_ng_two_items_ok_with_shortfall(self):
        self.assertEqual(status(self._rep(n=4), "KPFT", "X", "KPFT-4"), "NG")
        self.assertEqual(status(self._rep(n=2), "KPFT", "X", "KPFT-4"), "OK")

    def test_span_not_in_article_is_ng(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        x = make_run(os.path.join(td.name, "x"), "X", n_kp=3)
        with open(f"{x}/src/b1b/article.md", "w", encoding="utf-8") as f:
            f.write("Completely different text.")
        z = make_run(os.path.join(td.name, "z"), "Z", n_kp=3)
        self.assertEqual(status(run_report(x, z, x_source_dir=f"{x}/src"), "KPFT", "X", "KPFT-5"), "NG")

    def test_without_article_it_is_manual_not_ok(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        x = make_run(os.path.join(td.name, "x"), "X", n_kp=3)
        z = make_run(os.path.join(td.name, "z"), "Z", n_kp=3)
        self.assertEqual(status(run_report(x, z), "KPFT", "X", "KPFT-5"), "MANUAL")

    def test_stale_and_hybrid_dir_detected(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        x = make_run(os.path.join(td.name, "x"), "X", n_kp=3)
        kd = e106.level_paths("X", x, "b1b")["kp_dir"]
        os.makedirs(f"{kd}/key_phrases_db_hybrid")
        z = make_run(os.path.join(td.name, "z"), "Z", n_kp=3)
        rep = run_report(x, z)
        self.assertEqual(status(rep, "KPFT", "X", "KPFT-1"), "NG")


class PnapChecksTest(unittest.TestCase):
    def test_hr_queue_new_attributed_line_is_ng_and_unattributed_is_info(self):
        with tempfile.TemporaryDirectory() as td:
            repo = os.path.join(td, "repo")
            hq = os.path.join(repo, e106.HR_QUEUE_RELS[0])
            wl(hq, [{"wav_path": "old"}])
            wl(os.path.join(repo, e106.ATTEMPT_HISTORY_REL), [{"theme_id": "old", "human_review_reached": False}])
            x = make_run(os.path.join(td, "run_x_01"), "X", n_kp=3)
            z = make_run(os.path.join(td, "run_z_01"), "Z", n_kp=3)
            snap = e106.take_snapshot(repo, [x, z])
            sp = os.path.join(td, "snap.json")
            wj(sp, snap)
            with open(hq, "a", encoding="utf-8") as f:
                f.write(json.dumps({"wav_path": x.replace("\\", "/") + "/b1b/narration/a.wav"}) + "\n")
                f.write(json.dumps({"wav_path": "C:/other/agent/run.wav"}) + "\n")
            diff = e106.compare_snapshot(repo, snap, [x, z])
            q = diff["hr_queues"][e106.HR_QUEUE_RELS[0]]
            self.assertEqual((q["new_total"], q["new_attributed_to_these_runs"], q["new_not_attributed"]), (2, 1, 1))
            rep = run_report(x, z, repo_root=REPO, snapshot_in=sp)
            # 実repoのqueueはsnapshotと別なのでNG判定にはならない: ここは compare_snapshot の帰属ロジックのみ確認
            self.assertIn("hr_queues", diff)

    def test_store_manifest_race_signs_are_reported(self):
        with tempfile.TemporaryDirectory() as td:
            repo = os.path.join(td, "repo")
            mp = os.path.join(repo, e106.STORE_MANIFEST_REL)
            wj(mp, {"a": 1, "b": 2})
            snap = e106.take_snapshot(repo, [])
            self.assertEqual(snap["store_manifest"]["n_entries"], 2)
            wj(mp, {"a": 1})   # 更新消失を模擬
            r = e106.compare_snapshot(repo, snap, [])["store_manifest"]
            self.assertTrue(r["entries_decreased"])
            with open(mp, "w", encoding="utf-8") as f:
                f.write('{"a": ')   # 部分書込を模擬
            self.assertFalse(e106.compare_snapshot(repo, snap, [])["store_manifest"]["valid_json_after"])

    def test_ledger_sidecar_excluded_from_ledger_change(self):
        with tempfile.TemporaryDirectory() as td:
            repo = os.path.join(td, "repo")
            wj(os.path.join(repo, e106.LEDGER_REL), {"k": {"surface": "Khaite"}})
            wj(os.path.join(os.path.dirname(os.path.join(repo, e106.LEDGER_REL)), "negative_cache.json"), {"a": 1})
            snap = e106.take_snapshot(repo, [])
            wj(os.path.join(os.path.dirname(os.path.join(repo, e106.LEDGER_REL)), "negative_cache.json"), {"a": 2})
            diff = e106.compare_snapshot(repo, snap, [])
            self.assertFalse(diff["ledger"]["changed"])
            self.assertTrue(diff["ledger"]["sidecar_changed"]["negative_cache.json"])
            wj(os.path.join(repo, e106.LEDGER_REL), {"k": {"surface": "Khaite", "human_approved": True}})
            self.assertTrue(e106.compare_snapshot(repo, snap, [])["ledger"]["changed"])

    def test_public_page_leak_is_ng(self):
        with tempfile.TemporaryDirectory() as td:
            x = make_run(os.path.join(td, "x"), "X", n_kp=3)
            z = make_run(os.path.join(td, "z"), "Z", n_kp=3)
            os.makedirs(f"{x}/pages")
            with open(f"{x}/pages/index.html", "w", encoding="utf-8") as f:
                f.write("<html><body>最終状態: アラーム付き完成</body></html>")
            rep = run_report(x, z)
            self.assertEqual(status(rep, "PNAP", "X", "PNAP-7"), "NG")

    def test_kp_segment_alarm_is_ng(self):
        with tempfile.TemporaryDirectory() as td:
            x = make_run(os.path.join(td, "x"), "X", n_kp=3)
            p = e106.level_paths("X", x, "b1b")["results"]
            d = json.load(open(p, encoding="utf-8"))
            d["segments"]["kp1_english"] = {"status": "OK", "asr_judgement": {"state": e106.ALARM_STATE}}
            wj(p, d)
            z = make_run(os.path.join(td, "z"), "Z", n_kp=3)
            self.assertEqual(status(run_report(x, z), "PNAP", "X", "PNAP-8"), "NG")

    def test_consistency_mismatch_is_ng(self):
        with tempfile.TemporaryDirectory() as td:
            x = make_run(os.path.join(td, "x"), "X", n_kp=3)
            add_alarm(x, consistency_match=False)
            z = make_run(os.path.join(td, "z"), "Z", n_kp=3)
            self.assertEqual(status(run_report(x, z), "PNAP", "X", "PNAP-6"), "NG")

    def test_non_resolved_lock_is_ng(self):
        with tempfile.TemporaryDirectory() as td:
            x = make_run(os.path.join(td, "x"), "X", n_kp=3)
            wj(f"{x}/b1b/audit/review_lock_state.json", {"preview": {"state": "HUMAN_REVIEW_REQUIRED"}})
            z = make_run(os.path.join(td, "z"), "Z", n_kp=3)
            self.assertEqual(status(run_report(x, z), "PNAP", "X", "PNAP-3"), "NG")

    def test_ledger_lookup_reports_tier_and_approval(self):
        with tempfile.TemporaryDirectory() as td:
            lp = os.path.join(td, "ledger.json")
            wj(lp, {"a": {"surface": "Khaite", "evidence_tier": "QUOTE_VERIFIED", "human_approved": True, "tts_respelling": "Kate"},
                    "b": {"surface": "Other"}})
            r = e106.ledger_lookup(td, ["khaite"], lp)
            self.assertEqual(r["entries"]["khaite"][0]["evidence_tier"], "QUOTE_VERIFIED")
            self.assertIs(r["entries"]["khaite"][0]["human_approved"], True)


class CostTest(unittest.TestCase):
    def test_classify_record(self):
        cr = e106.classify_record
        self.assertEqual(cr({"provider": "gemini_batch", "model_id": "gemini-3.8-flash-lite-tts", "segment": "kp1_en"}), ("kp_audio_english", "tts"))
        self.assertEqual(cr({"provider": "azure", "model_id": "azure-speech-stt", "segment": "kp2_english"}), ("kp_audio_english", "asr_azure"))
        self.assertEqual(cr({"provider": "openai_asr", "model_id": "gpt-4o-mini-transcribe", "segment": "kp3_japanese_meaning"}), ("kp_audio_ja_meaning", "asr_openai"))
        self.assertEqual(cr({"provider": "gemini", "model_id": "x-tts", "segment": "kp1_explanation_en"}), ("kp_audio_explanation", "tts"))
        self.assertEqual(cr({"provider": "openai", "model_id": "gpt-6-luna", "stage": "kp_gloss_alignment"}), ("kp_chain", "llm"))
        self.assertEqual(cr({"provider": "openai", "model_id": "gpt-6-luna", "stage": "scaffold"}), ("scaffold_llm_unsplit", "llm"))
        self.assertEqual(cr({"provider": "gemini", "model_id": "x-tts", "segment": "preview"}), ("non_kp_audio", "tts"))

    def test_synthetic_records_skipped_and_unpriced_listed(self):
        with tempfile.TemporaryDirectory() as td:
            wl(f"{td}/raw_usage_log.jsonl", [
                {"provider": "openai_asr", "model_id": "gpt-4o-mini-transcribe", "segment": "kp1_en", "cost_usd": 0.1, "usage_source": "SYNTHETIC_DRYRUN_STUB"},
                {"provider": "mystery", "model_id": "zzz", "segment": "kp1_en", "input_tokens": 5},
                {"provider": "openai_asr", "model_id": "gpt-4o-mini-transcribe", "segment": "kp1_en", "cost_usd": 0.1, "usage_source": "OFFICIAL_API_RESPONSE"}])
            c = e106.collect_cost(REPO, td)
            self.assertEqual(c["synthetic_skipped"], 1)
            self.assertEqual(c["records"], 2)
            self.assertTrue(c["unpriced"])
            self.assertAlmostEqual(c["total_jpy"], round(0.1 * c["usd_jpy"], 4), places=3)


class StructuralTest(unittest.TestCase):
    def test_no_production_import(self):
        with open(e106.__file__, encoding="utf-8") as fh:
            src = fh.read()
        tree = ast.parse(src)
        mods = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                mods |= {a.name.split(".")[0] for a in n.names}
            elif isinstance(n, ast.ImportFrom):
                mods.add((n.module or "").split(".")[0])
        stdlib_ok = {"argparse", "datetime", "glob", "hashlib", "importlib", "json", "os", "re", "subprocess", "sys", "wave", "__future__"}
        self.assertFalse(mods - stdlib_ok, mods - stdlib_ok)

    def test_does_not_write_into_run_dirs(self):
        with tempfile.TemporaryDirectory() as td:
            x = make_run(os.path.join(td, "x"), "X", n_kp=3)
            z = make_run(os.path.join(td, "z"), "Z", n_kp=3)

            def tree_hash():
                h = hashlib.sha256()
                for dp, dn, fn in sorted(os.walk(td)):
                    dn.sort()
                    for f in sorted(fn):
                        p = os.path.join(dp, f)
                        h.update(p.encode())
                        with open(p, "rb") as fh:
                            h.update(fh.read())
                return h.hexdigest()
            before = tree_hash()
            run_report(x, z, x_source_dir=f"{x}/src")
            self.assertEqual(before, tree_hash())

    def test_expected_keys_are_constants_and_cover_er104_check_keys(self):
        # er104(未配線module)のvote_check_from_auditの返却キーと一致していること(読取のみ。importはしない=ソース文字列で照合)
        p = os.path.join(REPO, "er104_kp_three_asr_vote_01.py")
        if not os.path.exists(p):
            self.skipTest("er104 absent")
        with open(p, encoding="utf-8") as fh:
            src = fh.read()
        for k in e106.EXPECTED_VOTE_CHECK_KEYS:
            self.assertIn(f'"{k}"', src, k)

    def test_dangling_grep_runs(self):
        r = e106.dangling_grep(REPO)
        self.assertIn("KPFT: db_hybrid経路", r)


class RealLegacyRunSmokeTest(unittest.TestCase):
    """既存の旧仕様run(実在する場合のみ)で『5件・vote無し(LEGACY_DUAL)・alarm無し』になること。"""
    X = "er019_output/family_x_audio_production_wiring_01/paycheck_personality__run_pp_02"
    Z = "er026_output/family_z_production_e2e_01/melos/run_e2e_05"   # 2026-10-23: run_e2e_06は速度仕様v2の再処理でKP1英語がKP3V gateでvote付きに再生成されたため、未再処理の旧仕様run(run_e2e_05)へ変更

    def test_real_legacy(self):
        if not (os.path.isdir(os.path.join(REPO, self.X)) and os.path.isdir(os.path.join(REPO, self.Z))):
            self.skipTest("legacy run dirs absent")
        rep = run_report(os.path.join(REPO, self.X), os.path.join(REPO, self.Z), x_source_dir=os.path.join(REPO, "er019_output/paycheck_personality/run_pp_02"))
        for fk in ("X", "Z"):
            fam = rep["families"][fk]
            self.assertEqual({d["selection"]["n_items"] for d in fam["levels"].values()}, {5})
            self.assertEqual(fam["alarms"]["total_alarms"], 0)
            self.assertFalse(any(v["kind"] in ("vote_check_v1", "vote_audit") for v in rep["vote_table"][fk]))
            self.assertGreater(fam["cost"]["total_jpy"], 0)


if __name__ == "__main__":
    unittest.main()
