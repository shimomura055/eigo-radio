# -*- coding: utf-8 -*-
"""ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 委任_03B(兼 SELECTION-UI-BATCH-AND-VOCAB-AUDIO-01 委任_02D): Vocabulary & Expressions掲載項目の英語音声のEnd User組込み。
 - 掲載項目は全件音声必須(M6): 索引なし/complete=false/mp3欠落・sha不一致/項目に対応する音声なし = ENDUSER_VOCAB_AUDIO_INCOMPLETEでSTOP(音声なしの項目を掲載しない)
 - 組込み: article.json `levels[std|adv].vocab[i].audio`、mp3を`enduser/audio/`へコピー(sha照合)、build_info.vocab_audio、verify_consistency(validate_article)
 - 掲載Vocabularyが無いlevel(Y再配達Std・ZメロスStd)は音声不要。run_dirが無い直呼びは従来どおり(音声なし)
実行: .venv\\Scripts\\python.exe -m pytest er135_enduser_vocab_audio_test_01.py -q   (API 0)
"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import er135_enduser_page_01 as E
import er135_enduser_page_test_01 as PT
import er137_vocab_extra_audio_01 as V


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def write_run_vocab_audio(run: Path, b, drop=None, complete=True, corrupt=None):
    """production runの `<a2|b1b>/vocab_audio/vocab_audio.json` と mp3 をfixtureの掲載Vocabularyから作る。"""
    shas = {}
    for lv_run, akey in V.LEVEL_TO_ARTICLE_KEY.items():
        vocab = (b.study.get(akey) or {}).get("vocab") or []
        if not vocab:
            continue
        d = run / lv_run / "vocab_audio"
        d.mkdir(parents=True)
        items = []
        for n, v in enumerate(vocab, start=1):
            if drop and (akey, v["heading"]) == drop:
                continue
            mp3 = d / f"vocab_{lv_run}_{n}.mp3"
            body = f"mp3:{lv_run}:{n}:{v['heading']}".encode()
            mp3.write_bytes(body)
            sha = _sha(body if corrupt != (akey, v["heading"]) else b"x")
            items.append({"vocab_index": n, "candidate_id": None, "term": v["heading"], "source": "kp_reuse", "file": f"audio/vocab_{lv_run}_{n}.mp3",
                          "mp3": mp3.name, "dur": 1.5, "sha256": sha, "wav_sha256": "0" * 64, "gate_status": "VALIDATED", "tts_status": "OK"})
        (d / "vocab_audio.json").write_text(json.dumps({"schema": V.SCHEMA_VERSION, "level": lv_run, "complete": complete, "errors": [], "items": items}), encoding="utf-8")
    return shas


class VA1_Load(unittest.TestCase):
    def setUp(self):
        self.b = PT.Built("x_moon")

    def load(self, run):
        return E.load_vocab_audio(run, self.b.rows, self.b.study)

    def test_complete_run_loads_all_items(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td) / "run"
            write_run_vocab_audio(run, self.b)
            va = self.load(run)
            n = sum(len((self.b.study[lv] or {}).get("vocab") or []) for lv in ("std", "adv"))
            self.assertEqual(len(va["paths"]), n)
            self.assertEqual(set(va["docs"]), {"a2", "b1b"})

    def test_missing_index_is_stop(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(PT.stop_code(self.load, Path(td) / "run"), "ENDUSER_VOCAB_AUDIO_INCOMPLETE")

    def test_incomplete_or_corrupt_is_stop(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td) / "run"
            write_run_vocab_audio(run, self.b, complete=False)
            self.assertEqual(PT.stop_code(self.load, run), "ENDUSER_VOCAB_AUDIO_INCOMPLETE")
        with tempfile.TemporaryDirectory() as td:
            run = Path(td) / "run"
            h = self.b.study["adv"]["vocab"][0]["heading"]
            write_run_vocab_audio(run, self.b, corrupt=("adv", h))
            self.assertEqual(PT.stop_code(self.load, run), "ENDUSER_VOCAB_AUDIO_INCOMPLETE")

    def test_no_vocab_means_no_requirement(self):
        study = {lv: {"vocab": []} for lv in ("std", "adv")}
        with tempfile.TemporaryDirectory() as td:
            self.assertIsNone(E.load_vocab_audio(Path(td) / "run", self.b.rows, study))
        # 片方のlevelだけVocabularyが無い(Y再配達Std・ZメロスStd): そのlevelの音声は要求しない
        study = {"std": {"vocab": []}, "adv": self.b.study["adv"]}
        with tempfile.TemporaryDirectory() as td:
            run = Path(td) / "run"
            write_run_vocab_audio(run, PT.Built("x_moon"))
            va = E.load_vocab_audio(run, self.b.rows, study)
            self.assertEqual(set(va["docs"]), {"b1b"})


class VA2_BuildAndVerify(unittest.TestCase):
    def build(self, td, drop=None):
        pub, b = PT.T12_AtomicWrite.make_public(None, td)
        run = Path(td) / "run"
        write_run_vocab_audio(run, b, drop=drop)
        va = E.load_vocab_audio(run, b.rows, b.study)
        return pub, b, E.build_enduser(pub, b.family, b.sync, kp_audio=PT.kp_fake(b.rows), probe=b.probe, ja_manuscript=None, vocab_audio=va)

    def test_every_vocab_item_gets_audio_and_mp3_is_copied_and_verified(self):
        with tempfile.TemporaryDirectory() as td:
            pub, b, res = self.build(td)
            ed = pub / "enduser"
            art = json.load(open(ed / "data" / "article.json", encoding="utf-8"))
            n = 0
            for L in art["levels"].values():
                for v in L["vocab"]:
                    a = v["audio"]
                    self.assertEqual(a["kind"], "standalone")
                    self.assertTrue((ed / a["file"]).is_file())
                    self.assertEqual(E.sha256_file(ed / a["file"]), a["sha256"])
                    n += 1
            self.assertGreater(n, 0)
            bi = json.load(open(ed / "build_info.json", encoding="utf-8"))
            self.assertEqual(len(bi["vocab_audio"]["files"]), n)
            self.assertEqual(V.validate_article(art, str(ed)), [])
            r = E.verify_consistency(pub)
            self.assertTrue(r["ok"], r["violations"])
            self.assertEqual(r["checked"]["vocab_audio"], n)
            # 改竄検知: mp3を変えるとNG / 消すとNG / audioを外すとNG
            f = next(iter(bi["vocab_audio"]["files"]))
            (ed / f).write_bytes(b"tampered")
            r2 = E.verify_consistency(pub)
            self.assertTrue(any(x["code"] == "ENDUSER_VOCAB_AUDIO" for x in r2["violations"]))
            (ed / f).unlink()
            r3 = E.verify_consistency(pub)
            self.assertTrue(any(x["code"] == "ENDUSER_VOCAB_AUDIO" for x in r3["violations"]))

    def test_item_without_audio_is_stop_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as td:
            pub, b = PT.T12_AtomicWrite.make_public(None, td)
            run = Path(td) / "run"
            h = b.study["adv"]["vocab"][-1]["heading"]
            write_run_vocab_audio(run, b, drop=("adv", h))
            va = E.load_vocab_audio(run, b.rows, b.study)
            code = PT.stop_code(E.build_enduser, pub, b.family, b.sync, kp_audio=PT.kp_fake(b.rows), probe=b.probe, ja_manuscript=None, vocab_audio=va)
            self.assertEqual(code, "ENDUSER_VOCAB_AUDIO_INCOMPLETE")
            self.assertFalse((pub / "enduser").exists())                  # 失敗時は何も書かない(音声なしの項目を掲載したページを残さない)

    def test_direct_call_without_run_dir_is_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            pub, b = PT.T12_AtomicWrite.make_public(None, td)
            E.build_enduser(pub, b.family, b.sync, kp_audio=PT.kp_fake(b.rows), probe=b.probe, ja_manuscript=None)
            art = json.load(open(pub / "enduser" / "data" / "article.json", encoding="utf-8"))
            self.assertFalse(any("audio" in v for L in art["levels"].values() for v in L["vocab"]))
            self.assertNotIn("audio", {p.name for p in (pub / "enduser").iterdir()})


class VA3_Asset(unittest.TestCase):
    def test_asset_has_vocab_play_button_and_preview_translation(self):
        root = Path(__file__).resolve().parent / "enduser_page_assets" / E.R.ASSET_BUILD_ID
        js = (root / "app.js").read_text(encoding="utf-8")
        for needle in ("data-act=\"vocab\"", "function playVocab", "function endVocab", "mode === 'vocab'", "sentHtml(p)) + trHtml(p)"):
            self.assertIn(needle, js)
        self.assertEqual((root / "index.html").read_text(encoding="utf-8").count("rev01-g"), 4)
        self.assertEqual(E.R.ASSET_BUILD_ID, "rev01-g")


if __name__ == "__main__":
    unittest.main()
