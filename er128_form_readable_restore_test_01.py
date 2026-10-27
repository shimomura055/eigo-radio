# -*- coding: utf-8 -*-
"""er128_form_readable_restore_01 のtest(LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_07R。API 0)。

- 全公開データ(live) x 乱択: 人間可読コピー -> 復元payload が既存 FormLogic.buildStructured(node)と一致
- 改変9種=fail-closed / 揺れ吸収 / データ更新(履歴あり/なし) / 照合コードの契約(COPY_FORMAT_01の実例とバイト一致)
- 共有fixture(docs/research/.../fixtures/readable_cases_01/): 委任_07(JS側)と共有する契約。--regen-fixtures で再生成
- AI島Std/Advのユーザー確定payloadを 人間可読化 -> 復元 で逆変換一致
- 既存confirmへの委譲(cmd_from_form)の薄さ・CLI配線
"""
import test_state_isolation_01  # noqa: F401  (Production監査ログ汚染防止)
import copy
import glob
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import er128_form_readable_restore_01 as R  # noqa: E402

LIVE_DATA = R.DEFAULT_DATA_DIR
FORM_LOGIC = os.path.join(ROOT, "user_test", "selection_form_v3", "form_logic.js")
FX = os.path.join(ROOT, "docs", "research", "LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01", "fixtures", "readable_cases_01")
NODE_BATCH = os.path.join(FX, "node_structured_batch.js")
PAYLOAD_DIR = os.path.join(ROOT, "docs", "research", "AI-ISLAND-FORM-PRODUCTION-01", "payloads")
HAVE_NODE = shutil.which("node") is not None
COMPARE_KEYS = ("article", "selection", "comment", "grammar_status", "grammar_decision", "kp_confirmed")


def load(p):
    with open(p, "rb") as f:
        return f.read()


def jload(p):
    return json.loads(load(p).decode("utf-8"))


def data_files(data_dir):
    return sorted(f for f in os.listdir(data_dir) if f.endswith(".json") and f != "articles.json" and "__" in f)


def d6_of_file(p):
    return R.d6_of_bytes(load(p))


def node_expected(jobs):
    """jobs=[{'data': path, 'state': st}] -> buildStructuredの比較対象配列(既存フォームの正本ロジック)"""
    fd, jp = tempfile.mkstemp(suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(jobs, f, ensure_ascii=False)
        out = subprocess.run(["node", NODE_BATCH, FORM_LOGIC, jp], capture_output=True, check=True).stdout
        return json.loads(out.decode("utf-8"))
    finally:
        os.remove(jp)


def random_state(d, rnd, with_gram):
    terms = [it["term"] for it in R.items_of(d)]
    rnd.shuffle(terms)
    ch = {}
    n1 = n2 = n3 = 0
    for t in terms:
        if n1 < 3:
            ch[t] = 1; n1 += 1
        elif n1 + n2 < 5:
            ch[t] = 2; n2 += 1
        elif n1 + n2 + n3 < 12:
            ch[t] = 3; n3 += 1
    pres = [g["id"] for g in R.grammar_presented(d)]
    gr, zero = {}, False
    if with_gram and pres:
        gr[rnd.choice(pres)] = True
    elif pres:
        zero = True
    return {"choices": ch, "grammar": gr, "grammar_zero": zero,
            "comment": rnd.choice(["", "", "snatch の説明を修正。", "複数行\nコメント：テスト 2行目", "全角：スペース　と ASCII: 混在", "  前後空白あり  "])}


def diff_payload(payload, exp):
    diffs = []
    for k in COMPARE_KEYS:
        got = payload.get(k)
        want = exp.get(k)
        if k == "comment":
            want = (want or "").strip()
        if got != want and not (got is None and want is None):
            diffs.append((k, got, want))
    return diffs


# ---------------------------------------------------------------- fixture 生成(委任_07と共有する契約)
SYNTH_TEXT_SHA = hashlib.sha256(b"synthetic text").hexdigest()


def _synth_grammar(i, title, rank, body):
    gid = f"g{i:010d}"
    full = body + "\n====="
    return {"id": gid, "candidate_id": gid, "title": title, "body": full, "example": f"Example {i}.", "explanation_full": full, "explanation_status": "provided",
            "explanation_sha256": hashlib.sha256(full.encode("utf-8")).hexdigest(), "level": "Standard", "rank": rank}


def synth_datasets():
    base = {"schema": "eigo_radio_selection_article_v1", "slug": "fixture_synth", "level": "a2", "level_label": "Standard", "name": "合成テスト記事", "family": "X",
            "candidates_sha256": hashlib.sha256(b"synthetic candidates").hexdigest(), "candidates_sha256_source": "candidate_doc_field",
            "source_kp_candidates_path": "fixtures/synth/kp_candidates.json", "source": {"kind": "TEST_FIXTURE", "text_sha256": SYNTH_TEXT_SHA}}

    def it(i, term, gloss, status, kind="phrase"):
        o = {"id": f"p_{i:010d}", "candidate_id": f"p_{i:010d}", "term": term, "kind": kind, "ja_gloss": gloss, "ja_gloss_status": status, "meaning_ja": gloss}
        if term == "run out of":
            o["selection_phrase"] = "ran out of"
        return o
    gb = [_synth_grammar(1, "関係節を含む長い主語", 1, "【日本語訳】\nそのAIが建てられる塔の平均数は減少した。\n\n【文法・構文の仕組み】\n主語は **the average number of towers it could build** 全体です。"),
          _synth_grammar(2, "関係節を含む長い主語", 2, "【日本語訳】\n別の文です。\n\n【文法・構文の仕組み】\n同名・別本文の候補(AI島Stdの同名3件と同じ構造)です。"),
          _synth_grammar(3, "提示範囲外の文法", 3, "【日本語訳】\n3位。\n\n【文法・構文の仕組み】\n提示されない。")]
    spec = dict(base, phrases=[it(1, "run out of", "を使い果たす", "official"), it(2, "take off", "離陸する", "provisional"), it(3, "give up", "あきらめる", "official")],
                words=[it(4, "ephemeral", "", "missing", "word"), it(5, "mundane", "ありふれた", "official", "word")], grammar=gb,
                grammar_spec={"version": "top2_select1_v1", "presented_max": 2, "max_select": 1, "allow_zero": True})
    legacy = dict(base, slug="fixture_synth_legacy", level="b1b", level_label="Advanced", name="合成テスト記事(旧形式)",
                  phrases=[it(11, "look into", "調べる", "official"), it(12, "come across", "出くわす", "official")], words=[it(13, "ubiquitous", "どこにでもある", "official", "word")],
                  grammar=[dict(g, rank=None) for g in gb[:3]])
    for g in legacy["grammar"]:
        g.pop("rank")
    dup = dict(base, slug="fixture_synth_dup", name="同一表現が複数候補", phrases=[it(21, "bank", "銀行", "official"), it(22, "bank", "土手", "official"), it(23, "light", "光", "official")], words=[], grammar=[])
    return {"fixture_synth__a2": spec, "fixture_synth_legacy__b1b": legacy, "fixture_synth_dup__a2": dup}


SNAPSHOT_FILES = ["ai_island_temple__a2__prod", "ai_island_temple__b1b__prod", "melos__a2__prod", "monkeys_paw__b1b__prod", "ui_check_dummy__dummy", "uk_train_speaker_playback__b1b__prod"]


def regen_fixtures():
    os.makedirs(os.path.join(FX, "data"), exist_ok=True)
    os.makedirs(os.path.join(FX, "cases"), exist_ok=True)
    for old in glob.glob(os.path.join(FX, "cases", "*")) + glob.glob(os.path.join(FX, "data", "*")):
        os.remove(old)
    for stem in SNAPSHOT_FILES:
        with open(os.path.join(FX, "data", stem + ".json"), "wb") as f:
            f.write(load(os.path.join(LIVE_DATA, stem + ".json")).replace(b"\r\n", b"\n"))
    for stem, d in synth_datasets().items():
        with open(os.path.join(FX, "data", stem + ".json"), "wb") as f:
            f.write((json.dumps(d, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    rnd = random.Random(20261027)
    cases = []
    for stem in sorted(f[:-5] for f in os.listdir(os.path.join(FX, "data"))):
        if stem == "fixture_synth_dup__a2":
            continue
        d = jload(os.path.join(FX, "data", stem + ".json"))
        for k in range(3):
            cases.append((f"{stem}__r{k}", stem, random_state(d, rnd, with_gram=(k % 2 == 1))))
    # 特定ケース
    d = jload(os.path.join(FX, "data", "fixture_synth__a2.json"))
    ch_all = {"run out of": 1, "take off": 1, "give up": 2, "ephemeral": 3, "mundane": 3}
    g_ids = [g["id"] for g in R.grammar_presented(d)]
    cases += [("synth_provisional_missing_marks", "fixture_synth__a2", {"choices": ch_all, "grammar": {}, "grammar_zero": True, "comment": ""}),
              ("synth_same_title_grammar_2nd", "fixture_synth__a2", {"choices": {"give up": 1}, "grammar": {g_ids[1]: True}, "grammar_zero": False, "comment": "文法の例文をもう少し短く"}),
              ("synth_empty_selection", "fixture_synth__a2", {"choices": {}, "grammar": {}, "grammar_zero": True, "comment": ""})]
    manifest = {"contract": "COPY_FORMAT_01.md", "d6_note": "d6=データJSON全体のsha256先頭6桁(CRLFはLFへ正規化してから計算)。JSは公開Pagesのバイト列(LF)から計算すること",
                "data": {}, "cases": []}
    for f in sorted(os.listdir(os.path.join(FX, "data"))):
        manifest["data"][f[:-5]] = d6_of_file(os.path.join(FX, "data", f))
    jobs = []
    for name, stem, st in cases:
        jobs.append({"data": os.path.join(FX, "data", stem + ".json"), "state": st})
    exp = node_expected(jobs)
    for (name, stem, st), e in zip(cases, exp):
        d = jload(os.path.join(FX, "data", stem + ".json"))
        d6 = manifest["data"][stem]
        text = R.build_readable(stem, d, st, d6)
        with open(os.path.join(FX, "cases", name + ".state.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"stem": stem, "state": st}, f, ensure_ascii=False, indent=1)
        with open(os.path.join(FX, "cases", name + ".readable.txt"), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        with open(os.path.join(FX, "cases", name + ".expected_structured.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(e, f, ensure_ascii=False, indent=1)
        manifest["cases"].append({"name": name, "stem": stem, "d6": d6, "readable_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), "code": R.CODE_RE.search(text).group(0)})
    with open(os.path.join(FX, "manifest.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print(f"fixtures regenerated: {len(cases)} cases, {len(manifest['data'])} data -> {FX}")


# ---------------------------------------------------------------- tests
class TestFixtureContract(unittest.TestCase):
    """委任_07(JS側)と共有する契約fixture: Pythonの人間可読出力がfixtureとバイト一致し、復元がnode正本(expected_structured)と一致する。"""

    def test_fixture_present(self):
        self.assertTrue(os.path.exists(os.path.join(FX, "manifest.json")), "fixtureが無い: py er128_form_readable_restore_test_01.py --regen-fixtures")

    def test_each_case_bytes_and_restore(self):
        man = jload(os.path.join(FX, "manifest.json"))
        self.assertGreaterEqual(len(man["cases"]), 20)
        dd = os.path.join(FX, "data")
        for c in man["cases"]:
            with self.subTest(case=c["name"]):
                self.assertEqual(d6_of_file(os.path.join(dd, c["stem"] + ".json")), c["d6"])
                sj = jload(os.path.join(FX, "cases", c["name"] + ".state.json"))
                d = jload(os.path.join(dd, c["stem"] + ".json"))
                want = load(os.path.join(FX, "cases", c["name"] + ".readable.txt")).decode("utf-8").replace("\r\n", "\n")   # Windowsのautocrlfで作業ツリーがCRLFになっても契約はLF
                self.assertEqual(R.build_readable(c["stem"], d, sj["state"], c["d6"]), want)
                self.assertNotIn("\r", want)
                payload, _ = R.restore(want, dd)
                exp = jload(os.path.join(FX, "cases", c["name"] + ".expected_structured.json"))
                self.assertEqual(diff_payload(payload, exp), [])


@unittest.skipUnless(HAVE_NODE, "node が無い")
class TestRoundtripAgainstBuildStructured(unittest.TestCase):
    def test_all_live_data_random_states(self):
        rnd = random.Random(20261027)
        jobs, texts, meta = [], [], []
        for f in data_files(LIVE_DATA):
            dp = os.path.join(LIVE_DATA, f)
            d = jload(dp)
            stem = f[:-5]
            for trial in range(6):
                st = random_state(d, rnd, with_gram=(trial % 2 == 1))
                jobs.append({"data": dp, "state": st})
                texts.append(R.build_readable(stem, d, st, d6_of_file(dp)))
                meta.append((f, trial))
        exp = node_expected(jobs)
        self.assertGreaterEqual(len(jobs), 66)
        bad = []
        for text, e, mt in zip(texts, exp, meta):
            try:
                payload, _ = R.restore(text, LIVE_DATA)
            except R.RestoreError as ex:
                bad.append((mt, str(ex)))
                continue
            df = diff_payload(payload, e)
            if df:
                bad.append((mt, df[:1]))
        self.assertEqual(bad, [], f"不一致 {len(bad)}/{len(jobs)}")

    def test_code_is_deterministic_and_has_no_json_noise(self):
        dp = os.path.join(LIVE_DATA, "melos__a2__prod.json")
        d = jload(dp)
        st = random_state(d, random.Random(1), True)
        t1 = R.build_readable("melos__a2__prod", d, st, d6_of_file(dp))
        self.assertEqual(t1, R.build_readable("melos__a2__prod", d, copy.deepcopy(st), d6_of_file(dp)))
        for noise in ("{", '"candidate_id"', "candidates_all", "ai_reference"):
            self.assertNotIn(noise, t1)
        self.assertIsNone(re.search(r"[0-9a-f]{64}", t1))


@unittest.skipUnless(HAVE_NODE, "node が無い")
class TestJsBuildReadableMatchesPython(unittest.TestCase):
    """T-C契約test: フォームJS(FormLogic.buildReadable)の出力が、Pythonの参照実装/fixtureとバイト一致する(照合コードのsha含む)。"""

    def test_js_equals_fixture_bytes(self):
        src = load(FORM_LOGIC).decode("utf-8")
        if "buildReadable" not in src:
            self.skipTest("form_logic.js に buildReadable が未実装")
        out = subprocess.run(["node", os.path.join(FX, "node_readable_batch.js"), FORM_LOGIC, FX], capture_output=True, check=True).stdout
        js = json.loads(out.decode("utf-8"))
        man = jload(os.path.join(FX, "manifest.json"))
        self.assertEqual(sorted(js), sorted(c["name"] for c in man["cases"]))
        for c in man["cases"]:
            want = load(os.path.join(FX, "cases", c["name"] + ".readable.txt")).decode("utf-8").replace("\r\n", "\n")
            self.assertEqual(js[c["name"]], want, c["name"])


class TestCopyFormatContract(unittest.TestCase):
    """COPY_FORMAT_01.md §2の実例とバイト一致(照合コードの定義: s10/c8/t8/k4)。"""

    def _sel(self, d, words):
        its = {i["term"]: i for i in R.items_of(d)}
        return [(cat, R.cid_of(its[w])) for cat, ws in words for w in ws]

    def test_std_user_example_code(self):
        d = jload(os.path.join(LIVE_DATA, "ai_island_temple__a2__prod.json"))
        words = [(1, ["carry over", "take a detour", "card to play"]), (2, ["worth paying attention to", "obstacle"]), (3, ["make a difference", "separately", "feature", "Strategy", "setup"])]
        code = R.make_code("ai_island_temple__a2__prod", d, "915481", self._sel(d, words), [], "")
        self.assertEqual(code, "AIF1-ai_island_temple__a2__prod-915481-25a7bce9-76f80f62-ccce40d25f-0-0-9cd3")

    def test_adv_grammar_comment_example_code(self):
        d = jload(os.path.join(LIVE_DATA, "ai_island_temple__b1b__prod.json"))
        self.assertEqual(R.make_code("x", d, "000000", [], [], "")[:2], "AI")
        # COPY_FORMAT実例のg10/m8は『実際の確定内容ではない動作確認用』。ここでは部品(m8=sha(trim(comment))[:8])の定義だけを固定する
        code = R.make_code("ai_island_temple__b1b__prod", d, "78503a", [], [], "文法の例文をもう少し短く")
        self.assertEqual(R.CODE_RE.fullmatch(code).group(7), "89851cb6")
        self.assertEqual(R.CODE_RE.fullmatch(code).group(3), "5d8c1b12")
        self.assertEqual(R.CODE_RE.fullmatch(code).group(4), "00f14092")

    def test_d6_is_crlf_invariant(self):
        raw = b'{"a": "b"}\n'
        self.assertEqual(R.d6_of_bytes(raw), R.d6_of_bytes(raw.replace(b"\n", b"\r\n")))

    def test_readable_example_matches_doc(self):
        d = jload(os.path.join(LIVE_DATA, "ai_island_temple__a2__prod.json"))
        ch = {w: c for c, ws in [(1, ["carry over", "take a detour", "card to play"]), (2, ["worth paying attention to", "obstacle"]),
                                 (3, ["make a difference", "separately", "feature", "Strategy", "setup"])] for w in ws}
        txt = R.build_readable("ai_island_temple__a2__prod", d, {"choices": ch, "grammar": {}, "grammar_zero": True, "comment": ""}, "915481")
        self.assertEqual(txt, "\n".join([
            "記事：AIの仮想の島｜Standard", "", "① Key Phrase", "- carry over：持ち越す", "- take a detour：寄り道をする", "- card to play：使える手", "",
            "② 追加解説", "- worth paying attention to：注目する価値がある", "- obstacle：障害物", "",
            "③ 本文意味表示", "- make a difference：影響を与える", "- separately：個別に", "- feature：性質", "- Strategy：作戦", "- setup：設定", "",
            "文法：選定なし", "", "自由コメント：なし", "",
            "照合コード(変更しないでください)：AIF1-ai_island_temple__a2__prod-915481-25a7bce9-76f80f62-ccce40d25f-0-0-9cd3"]))


class _Base(unittest.TestCase):
    stem = "ai_island_temple__b1b__prod"   # 文法あり(提示2件)・KPロック済みのデータ

    @classmethod
    def setUpClass(cls):
        cls.dp = os.path.join(LIVE_DATA, cls.stem + ".json")
        cls.d = jload(cls.dp)
        cls.d6 = d6_of_file(cls.dp)

    def state(self, **kw):
        g = R.grammar_presented(self.d)[0]
        st = {"choices": {}, "grammar": {g["id"]: True}, "grammar_zero": False, "comment": "強調したい"}
        st.update(kw)
        return st

    def base(self, **kw):
        return R.build_readable(self.stem, self.d, self.state(**kw), self.d6)


class TestTamperDetection(_Base):
    stem = "uk_train_speaker_playback__b1b__prod"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        its = R.items_of(cls.d)
        cls.its = its
        cls.st = {"choices": {its[0]["term"]: 1, its[1]["term"]: 1, its[2]["term"]: 2, its[5]["term"]: 3}, "grammar": {}, "grammar_zero": False, "comment": "強調したい"}
        # 文法つき改変用: 文法を持つ合成データ
        cls.tmp = tempfile.mkdtemp()
        for k, d in synth_datasets().items():
            with open(os.path.join(cls.tmp, k + ".json"), "wb") as f:
                f.write((json.dumps(d, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
        cls.sd = jload(os.path.join(cls.tmp, "fixture_synth__a2.json"))
        cls.s6 = d6_of_file(os.path.join(cls.tmp, "fixture_synth__a2.json"))
        g = R.grammar_presented(cls.sd)[0]
        cls.gst = {"choices": {"run out of": 1, "give up": 2}, "grammar": {g["id"]: True}, "grammar_zero": False, "comment": "強調したい"}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def base_plain(self):
        return R.build_readable(self.stem, self.d, self.st, self.d6)

    def base_gram(self):
        return R.build_readable("fixture_synth__a2", self.sd, self.gst, self.s6)

    def assert_refused(self, text, data_dir=LIVE_DATA, frag=None):
        with self.assertRaises(R.RestoreError) as cm:
            R.restore(text, data_dir)
        if frag:
            self.assertIn(frag, str(cm.exception))

    def test_baselines_restore(self):
        R.restore(self.base_plain(), LIVE_DATA)
        R.restore(self.base_gram(), self.tmp)

    def test_1_gloss_rewritten(self):
        it = self.its[0]
        b = self.base_plain()
        t = b.replace(R.gloss_text(it), R.gloss_text(it) + "こと", 1)
        self.assertNotEqual(t, b)
        self.assert_refused(t, frag="日本語訳が候補データと一致しません")

    def test_2_item_dropped(self):
        b = self.base_plain()
        it = self.its[1]
        t = b.replace(f"- {it['term']}：{R.gloss_text(it)}\n", "", 1)
        self.assertNotEqual(t, b)
        self.assert_refused(t, frag="照合コードと一致しません")

    def test_3_category_swapped(self):
        b = self.base_plain()
        it = self.its[1]
        line = f"- {it['term']}：{R.gloss_text(it)}\n"
        t = b.replace(line, "", 1).replace("② 追加解説\n", "② 追加解説\n" + line, 1)
        self.assertNotEqual(t, b)
        self.assert_refused(t, frag="照合コードと一致しません")

    def test_4_grammar_body_omitted(self):
        t = re.sub(r"(【解説全文】\n).*?(\n【解説ここまで】)", r"\1(省略)\2", self.base_gram(), flags=re.S)
        self.assert_refused(t, self.tmp, "解説全文が候補データと一致しません")

    def test_5_grammar_body_modified(self):
        b = self.base_gram()
        t = b.replace("【文法・構文の仕組み】", "【文法・構文の仕組み】(追記)", 1)
        self.assertNotEqual(t, b)
        self.assert_refused(t, self.tmp, "解説全文が候補データと一致しません")

    def test_6_grammar_body_truncated(self):
        b = self.base_gram()
        self.assert_refused(b.replace("【解説ここまで】", "", 1), self.tmp, "途中で切れています")

    def test_7_comment_modified(self):
        b = self.base_plain()
        self.assert_refused(b.replace("強調したい", "強調しない"), frag="自由コメントが照合コードと一致しません")

    def test_8_code_missing(self):
        t = re.sub(r"照合コード.*$", "", self.base_plain())
        self.assert_refused(t, frag="照合コードが見つかりません")

    def test_9_code_corrupted(self):
        t = re.sub(r"(AIF1-[A-Za-z0-9_]+?-)([0-9a-f])", lambda m: m.group(1) + ("0" if m.group(2) != "0" else "1"), self.base_plain(), count=1)
        self.assert_refused(t, frag="壊れています")

    def test_extra_unknown_version(self):
        self.assert_refused(self.base_plain().replace("AIF1-", "AIF2-"), frag="未対応の形式バージョン")

    def test_extra_item_added_in_other_category(self):
        b = self.base_plain()
        extra = self.its[7]
        t = b.replace("③ 本文意味表示\n", f"③ 本文意味表示\n- {extra['term']}：{R.gloss_text(extra)}\n", 1)
        self.assert_refused(t, frag="照合コードと一致しません")

    def test_extra_term_unknown(self):
        t = self.base_plain().replace(f"- {self.its[0]['term']}：", "- not a candidate：", 1)
        self.assert_refused(t, frag="候補にありません")

    def test_extra_grammar_title_replaced(self):
        t = self.base_gram().replace("文法：関係節を含む長い主語", "文法：提示範囲外の文法", 1)
        self.assert_refused(t, self.tmp)

    def test_extra_grammar_outside_presented(self):
        # 提示範囲外(3位)の文法を、タイトル・本文とも正しく差し込んだテキストは、解説が逐語一致でも拒否する
        g3 = self.sd["grammar"][2]
        b = self.base_gram()
        m = re.search(r"文法：.*?【解説ここまで】", b, flags=re.S)
        t = b[:m.start()] + "\n".join([f"文法：{g3['title']}", R.MARK_BEGIN, R.body_view(g3["body"]), R.MARK_END]) + b[m.end():]
        self.assert_refused(t, self.tmp)
        with self.assertRaises(R.RestoreError) as cm:
            R.restore(t, self.tmp)
        self.assertIn("提示範囲", str(cm.exception))

    def test_extra_header_mismatch(self):
        self.assert_refused(self.base_plain().replace("記事：", "記事：別の記事", 1), frag="記事見出し")

    def test_extra_data_json_hash_mismatch_without_history(self):
        d2 = tempfile.mkdtemp()
        try:
            shutil.copy(self.dp, os.path.join(d2, self.stem + ".json"))
            with open(os.path.join(d2, self.stem + ".json"), "ab") as f:
                f.write(b" ")
            self.assert_refused(self.base_plain(), d2, "選び直して")
        finally:
            shutil.rmtree(d2, ignore_errors=True)

    def test_extra_gloss_marker_contradiction(self):
        d = self.sd
        st = {"choices": {"take off": 1}, "grammar": {}, "grammar_zero": True, "comment": ""}
        t = R.build_readable("fixture_synth__a2", d, st, self.s6)
        self.assertIn("離陸する（仮訳・未確定）", t)
        R.restore(t, self.tmp)
        self.assert_refused(t.replace("（仮訳・未確定）", "（日本語訳未生成）"), self.tmp, "日本語訳が候補データと一致しません")


class TestToleratedVariations(_Base):
    stem = "uk_train_speaker_playback__b1b__prod"

    def setUp(self):
        its = R.items_of(self.d)
        self.its = its
        self.st = {"choices": {its[0]["term"]: 1, its[1]["term"]: 1, its[2]["term"]: 2, its[5]["term"]: 3}, "grammar": {}, "grammar_zero": False, "comment": "強調したい"}
        self.b = R.build_readable(self.stem, self.d, self.st, self.d6)
        self.exp = node_expected([{"data": self.dp, "state": self.st}])[0] if HAVE_NODE else None

    def ok(self, text, notes_expected=None):
        payload, notes = R.restore(text, LIVE_DATA)
        if self.exp:
            self.assertEqual(diff_payload(payload, self.exp), [])
        return notes

    def test_baseline(self):
        self.ok(self.b)

    def test_chatgpt_codeblock_and_preface(self):
        self.ok("了解です。内容はそのままです。\n```text\n" + self.b + "\n```\n以上です。")
        self.ok("```\n" + self.b + "\n```")

    def test_halfwidth_colon(self):
        t = re.sub(r"(?m)^(- [^：\n]+)：", r"\1:", self.b).replace("自由コメント：", "自由コメント:")
        self.assertNotEqual(t, self.b)
        self.ok(t)

    def test_bullet_variants(self):
        self.ok(self.b.replace("\n- ", "\n・"))
        self.ok(self.b.replace("\n- ", "\n• "))
        n = [0]

        def num(m):
            n[0] += 1
            return f"\n{n[0]}. "
        self.ok(re.sub(r"\n- ", num, self.b))

    def test_crlf_trailing_spaces(self):
        self.ok(self.b.replace("\n", "  \r\n"))

    def test_first_letter_capitalized(self):
        term = self.its[0]["term"]
        t = self.b.replace(f"- {term}：", f"- {term[0].upper() + term[1:]}：", 1)
        if t == self.b:
            self.skipTest("先頭が既に大文字")
        notes = self.ok(t)
        self.assertTrue(any("term正規化一致" in n for n in notes))

    def test_fullwidth_space_and_punct_in_gloss(self):
        it = self.its[0]
        g = R.gloss_text(it)
        t = self.b.replace(f"：{g}\n", f"：　{g} \n", 1)
        self.ok(t)

    def test_multiline_comment_with_trailing_spaces(self):
        st = dict(self.st, comment="複数行\nコメント：テスト 2行目")
        b = R.build_readable(self.stem, self.d, st, self.d6)
        exp = node_expected([{"data": self.dp, "state": st}])[0] if HAVE_NODE else None
        t = b.replace("\n", "  \r\n")
        payload, _ = R.restore(t, LIVE_DATA)
        self.assertEqual(payload["comment"], "複数行\nコメント：テスト 2行目")
        if exp:
            self.assertEqual(diff_payload(payload, exp), [])

    def test_comment_literal_nashi_is_refused(self):
        st = dict(self.st, comment="なし")
        b = R.build_readable(self.stem, self.d, st, self.d6)
        with self.assertRaises(R.RestoreError):   # 『コメントなし』と区別できないため確定しない(fail-closed)
            R.restore(b, LIVE_DATA)


class TestDataUpdate(_Base):
    stem = "uk_train_speaker_playback__b1b__prod"

    def test_history_hit_and_miss(self):
        its = R.items_of(self.d)
        st = {"choices": {its[0]["term"]: 1}, "grammar": {}, "grammar_zero": False, "comment": ""}
        text = R.build_readable(self.stem, self.d, st, self.d6)
        tmp = tempfile.mkdtemp()
        try:
            d2 = copy.deepcopy(self.d)
            d2["note_updated"] = "after selection"
            with open(os.path.join(tmp, self.stem + ".json"), "w", encoding="utf-8") as f:
                json.dump(d2, f, ensure_ascii=False)
            old = load(self.dp)
            with self.assertRaises(R.RestoreError):
                R.restore(text, tmp)
            with self.assertRaises(R.RestoreError):
                R.restore(text, tmp, lambda s, d6: None)
            p, n = R.restore(text, tmp, lambda s, d6: old if R.d6_of_bytes(old) == d6 else None)
            self.assertTrue(any("履歴から復元" in x for x in n))
            self.assertEqual(p["selection"]["key_phrase"][0]["term"], its[0]["term"])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_real_git_history_lookup(self):
        """実際のgit履歴から選定時の版を引ける(d6=過去版のshaを、現在版が異なる状態で)。"""
        r = subprocess.run(["git", "log", "--format=%H", "-3", "--", "user_test/selection_form_v3/data/ai_island_temple__a2__prod.json"], cwd=ROOT, capture_output=True)
        hs = r.stdout.decode().split()
        if len(hs) < 2:
            self.skipTest("履歴が2版未満")
        old = subprocess.run(["git", "show", f"{hs[-1]}:user_test/selection_form_v3/data/ai_island_temple__a2__prod.json"], cwd=ROOT, capture_output=True).stdout
        d6 = R.d6_of_bytes(old)
        if d6 == d6_of_file(os.path.join(LIVE_DATA, "ai_island_temple__a2__prod.json")):
            self.skipTest("最古版が現在版と同一")
        self.assertEqual(R.git_history_lookup("ai_island_temple__a2__prod", d6), old.replace(b"\r\n", b"\n") if False else old)
        self.assertIsNone(R.git_history_lookup("ai_island_temple__a2__prod", "ffffff"))


class TestDuplicateTermResolution(unittest.TestCase):
    def test_same_term_two_candidates_resolved_by_gloss_and_s10(self):
        tmp = tempfile.mkdtemp()
        try:
            d = synth_datasets()["fixture_synth_dup__a2"]
            p = os.path.join(tmp, "fixture_synth_dup__a2.json")
            with open(p, "wb") as f:
                f.write((json.dumps(d, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
            d6 = d6_of_file(p)
            # 土手(2つ目)を①、銀行(1つ目)を②に選ぶ。termは同一(bank)だが訳で候補が決まる
            sel_ids = [(1, "p_0000000022"), (2, "p_0000000021")]
            code = R.make_code("fixture_synth_dup__a2", d, d6, sel_ids, [], "")
            text = "\n".join(["記事：同一表現が複数候補｜Standard", "", "① Key Phrase", "- bank：土手", "", "② 追加解説", "- bank：銀行", "", "③ 本文意味表示", "（選択なし）", "",
                             "文法：選定なし", "", "自由コメント：なし", "", "照合コード(変更しないでください)：" + code])
            payload, _ = R.restore(text, tmp)
            self.assertEqual([i["candidate_id"] for i in payload["selection"]["key_phrase"]], ["p_0000000022"])
            self.assertEqual([i["candidate_id"] for i in payload["selection"]["extra_explanation"]], ["p_0000000021"])
            # 区分を入れ替えたテキスト(コードはそのまま)は拒否
            sw = text.replace("- bank：土手", "- bank：@@").replace("- bank：銀行", "- bank：土手").replace("- bank：@@", "- bank：銀行")
            with self.assertRaises(R.RestoreError):
                R.restore(sw, tmp)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TestSameTitleGrammar(unittest.TestCase):
    def test_second_same_title_candidate_resolved_by_body(self):
        man = jload(os.path.join(FX, "manifest.json"))
        c = next(x for x in man["cases"] if x["name"] == "synth_same_title_grammar_2nd")
        text = load(os.path.join(FX, "cases", c["name"] + ".readable.txt")).decode("utf-8").replace("\r\n", "\n")
        payload, _ = R.restore(text, os.path.join(FX, "data"))
        self.assertEqual(payload["selection"]["grammar"][0]["id"], "g0000000002")
        self.assertEqual(payload["selection"]["grammar"][0]["rank"], 2)
        # 同名・同題で本文だけ取り違えたテキストは拒否
        self.assertNotIn("同名・別本文", text.split("【解説全文】")[0])
        swapped = text.replace("同名・別本文の候補", "その人の別の候補")
        with self.assertRaises(R.RestoreError):
            R.restore(swapped, os.path.join(FX, "data"))


class TestAiIslandUserConfirmedReverse(unittest.TestCase):
    """AI島Std/Advのユーザー確定payload -> 人間可読化 -> 復元 で、確定内容(英語・訳・区分・candidate_id・kind)が逆変換で完全一致する。"""

    def _check(self, level_stem, fname):
        uc = jload(os.path.join(PAYLOAD_DIR, fname))
        dp = os.path.join(LIVE_DATA, level_stem + ".json")
        d = jload(dp)
        ch = {}
        for k in ("key_phrase", "extra_explanation", "meaning_display"):
            for it in uc["selection"][k]:
                ch[it["term"]] = it["category"]
        self.assertEqual(len(ch), 10)
        st = {"choices": ch, "grammar": {}, "grammar_zero": True, "comment": ""}
        text = R.build_readable(level_stem, d, st, d6_of_file(dp))
        payload, _ = R.restore(text, LIVE_DATA)
        for k in ("key_phrase", "extra_explanation", "meaning_display"):
            self.assertEqual(payload["selection"][k], uc["selection"][k], k)
        self.assertEqual(payload["selection"]["grammar"], [])
        self.assertEqual(payload["article"]["candidates_sha256"], uc["article"]["candidates_sha256"])
        self.assertEqual(payload["article"]["text_sha256"], uc["article"]["text_sha256"])
        # 文法1件(Top1)を選んだ版も復元できる
        g = R.grammar_presented(d)[0]
        st2 = dict(st, grammar={g["id"]: True}, grammar_zero=False, comment="文法の例文をもう少し短く")
        p2, _ = R.restore(R.build_readable(level_stem, d, st2, d6_of_file(dp)), LIVE_DATA)
        self.assertEqual(p2["selection"]["grammar"][0]["explanation_full"], g["body"])
        self.assertEqual(p2["comment"], "文法の例文をもう少し短く")
        self.assertEqual(p2["grammar_decision"]["state"], "selected")

    def test_standard(self):
        self._check("ai_island_temple__a2__prod", "ai_island_temple__a2__user_confirmed_01.json")

    def test_advanced(self):
        self._check("ai_island_temple__b1b__prod", "ai_island_temple__b1b__user_confirmed_01.json")


class TestDelegationToCmdFromForm(unittest.TestCase):
    """confirmは既存cmd_from_formへ委譲する(検証を緩めない)。実run不要で、委譲の結線・dry-run・拒否時の無副作用を確認する。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        dp = os.path.join(LIVE_DATA, "uk_train_speaker_playback__b1b__prod.json")
        d = jload(dp)
        its = R.items_of(d)
        self.text_path = os.path.join(self.tmp, "paste.txt")
        with open(self.text_path, "w", encoding="utf-8") as f:
            f.write("```\n" + R.build_readable("uk_train_speaker_playback__b1b__prod", d, {"choices": {its[0]["term"]: 1}, "grammar": {}, "grammar_zero": False, "comment": "c"}, d6_of_file(dp)) + "\n```")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_dry_run_does_not_touch_run(self):
        out = R.cmd_from_readable(self.text_path, os.path.join(self.tmp, "no_such_run"), "b1b", "tester", "ref", dry_run=True)
        self.assertTrue(out["dry_run"])
        self.assertEqual(out["restored"]["comment"], "c")
        self.assertNotIn("confirmed", out)
        self.assertEqual(sorted(os.listdir(self.tmp)), ["paste.txt"])

    def test_level_mismatch_refused(self):
        with self.assertRaises(R.RestoreError):
            R.cmd_from_readable(self.text_path, self.tmp, "a2", "tester", "ref", dry_run=True)

    def test_confirm_calls_cmd_from_form_with_restored_payload(self):
        import er128_kp_confirmed_content_01 as c
        calls = []
        orig, orig_kd, orig_paths = c.cmd_from_form, c._kp_dir_for, c.paths_of

        def fake(run, level, payload_path, by, user_ref, **kw):
            calls.append((run, level, json.loads(load(payload_path).decode("utf-8")), by, user_ref, kw))
            return {"revision": 7}
        try:
            c.cmd_from_form = fake
            c._kp_dir_for = lambda run, level: self.tmp
            c.paths_of = lambda kp: {"source_dir": os.path.join(self.tmp, "source")}
            out = R.cmd_from_readable(self.text_path, "RUN", "b1b", "tester", "ref", actor="evidence", grammar_pending=True)
        finally:
            c.cmd_from_form, c._kp_dir_for, c.paths_of = orig, orig_kd, orig_paths
        self.assertEqual(len(calls), 1)
        run, level, payload, by, uref, kw = calls[0]
        self.assertEqual((run, level, by, uref), ("RUN", "b1b", "tester", "ref"))
        self.assertEqual(kw, {"actor": "evidence", "grammar_pending": True})
        self.assertEqual(payload["schema_version"], 2)
        self.assertEqual(payload["schema_minor"], 1)
        saved = os.path.join(self.tmp, "source", "rev7_readable.txt")
        self.assertEqual(out["readable_saved"], saved)
        self.assertEqual(load(saved), load(self.text_path))   # 貼付原文を逐語で保存

    def test_restore_failure_does_not_call_confirm(self):
        import er128_kp_confirmed_content_01 as c
        bad = os.path.join(self.tmp, "bad.txt")
        with open(bad, "w", encoding="utf-8") as f:
            f.write(load(self.text_path).decode("utf-8").replace("自由コメント：c", "自由コメント：d"))
        called = []
        orig = c.cmd_from_form
        try:
            c.cmd_from_form = lambda *a, **k: called.append(1)
            with self.assertRaises(R.RestoreError):
                R.cmd_from_readable(bad, "RUN", "b1b", "tester", "ref")
        finally:
            c.cmd_from_form = orig
        self.assertEqual(called, [])

    def test_cli_wiring(self):
        rc = R.run(["restore", "--text", self.text_path])
        self.assertEqual(rc, 0)
        rc = R.run(["confirm", "--from-readable", self.text_path, "--run", "X", "--level", "b1b", "--by", "t", "--user-ref", "r", "--dry-run"])
        self.assertEqual(rc, 0)
        src = load(os.path.join(ROOT, "er119_kp_human_review_cli_01.py")).decode("utf-8")
        self.assertIn("--from-readable", src)


class TestDoesNotModifyCore(unittest.TestCase):
    def test_module_imports_no_er119_and_no_environ(self):
        s = load(os.path.join(ROOT, "er128_form_readable_restore_01.py")).decode("utf-8")
        self.assertIsNone(re.search(r"^\s*(import|from)\s+er119_", s, re.M))
        self.assertNotIn("os.environ", s)
        self.assertNotIn("getenv", s)
        self.assertNotIn("openai", s.lower())

    def test_no_http(self):
        s = load(os.path.join(ROOT, "er128_form_readable_restore_01.py")).decode("utf-8")
        for w in ("urllib", "requests", "http.client", "socket"):
            self.assertNotIn(w, s)


# ---------------------------------------------------------------- 実 cmd_from_form との結線(mock候補doc。er128のtest基盤を再利用。API 0)
from er128_kp_confirmed_content_test_01 import FormHelpers  # noqa: E402
from er119_test_support_01 import Env, rd  # noqa: E402
import er119_kp_human_review_01 as _rv  # noqa: E402
import er128_kp_confirmed_content_01 as _cc  # noqa: E402


class TestEndToEndRealConfirm(FormHelpers):
    """人間可読テキスト -> 復元 -> 実 cmd_from_form で確定。直接payloadを渡した確定と同じ確定内容になり、改変時は何も確定されない。"""

    def _data_from_cands(self, cands):
        its = []
        for c in cands["candidates"]:
            its.append({"id": c["candidate_id"], "candidate_id": c["candidate_id"], "term": c["item"]["used_form"], "kind": c.get("kind") or "phrase",
                        "ja_gloss": c["item"]["japanese_gloss"], "ja_gloss_status": "official", "meaning_ja": c["item"]["japanese_gloss"], "_rank": c["ai_rank"]})
        by = {i["_rank"]: i for i in its}
        for i in its:
            i.pop("_rank")
        d = {"schema": "eigo_radio_selection_article_v1", "slug": "coffee", "level": "b1b", "level_label": "Advanced", "name": "コーヒー", "family": "X",
             "candidates_sha256": cands["candidates_sha256"], "candidates_sha256_source": "candidate_doc_field", "source_kp_candidates_path": "x/kp_candidates.json",
             "source": {"kind": "TEST", "text_sha256": cands["text_sha256"]}, "phrases": [i for i in its if i["kind"] == "phrase"], "words": [i for i in its if i["kind"] == "word"], "grammar": []}
        return d, by

    def _setup(self, env):
        cands = self._gen(env)
        d, by = self._data_from_cands(cands)
        ddir = os.path.join(self.tmp, "data")
        os.makedirs(ddir, exist_ok=True)
        dp = os.path.join(ddir, "fixture_e2e__b1b.json")
        with open(dp, "wb") as f:
            f.write((json.dumps(d, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
        ch = {}
        for r in (1, 2, 3):
            ch[by[r]["term"]] = 1
        for r in (4, 5):
            ch[by[r]["term"]] = 2
        text = R.build_readable("fixture_e2e__b1b", d, {"choices": ch, "grammar": {}, "grammar_zero": False, "comment": "コメント"}, d6_of_file(dp))
        return cands, ddir, text

    def _paste(self, text, name="paste.txt"):
        p = os.path.join(self.tmp, name)
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write("ChatGPTの返信です。\n```\n" + text + "\n```")
        return p

    def test_readable_confirm_equals_direct_form_confirm_and_saves_readable(self):
        with Env(self.tmp) as env:
            cands, ddir, text = self._setup(env)
            pp = self._paste(text)
            out = R.cmd_from_readable(pp, self.run_dir, "b1b", "human", self.uref, data_dir=ddir)
            self.assertEqual(out["confirmed"]["revision"], 1)
            rec = self.rec()
            self.assertEqual(rec["origin"]["kind"], "form_submission")
            src = os.path.join(_cc.paths_of(self.kp_dir)["source_dir"], "rev1_readable.txt")
            self.assertEqual(rd(src), rd(pp))   # 貼付原文を逐語保存
            self.assertTrue(os.path.exists(os.path.join(_cc.paths_of(self.kp_dir)["source_dir"], "rev1_payload.json")))
            ids = [(i["candidate_id"], i["category"], i["used_form"]) for i in rec["items"]]
            self.assertEqual(sorted(ids), sorted(out["confirmed"]["items"]))
            # 再送(確定済み)は従来どおり拒否(冪等性は既存仕様)
            with self.assertRaises(Exception):
                R.cmd_from_readable(pp, self.run_dir, "b1b", "human", self.uref, data_dir=ddir)
            self.assertEqual(self.rec()["revision"], 1)

    def test_tampered_readable_confirms_nothing(self):
        with Env(self.tmp) as env:
            cands, ddir, text = self._setup(env)
            bad = self._paste(text.replace("コメント", "コメントX"), "bad.txt")
            with self.assertRaises(R.RestoreError):
                R.cmd_from_readable(bad, self.run_dir, "b1b", "human", self.uref, data_dir=ddir)
            self.assertIsNone(_cc.load_record(self.kp_dir))
            self.assertFalse(os.path.exists(os.path.join(_cc.paths_of(self.kp_dir)["source_dir"], "rev1_readable.txt")))

    def test_er128_still_rejects_when_candidate_doc_differs(self):
        """復元側は緩めない: データJSONの候補集合shaが現在の候補docと違えば、cmd_from_form(ISSUE)が確定を拒否する。"""
        with Env(self.tmp) as env:
            cands, ddir, text = self._setup(env)
            dp = os.path.join(ddir, "fixture_e2e__b1b.json")
            d = jload(dp)
            d["candidates_sha256"] = "ab" * 32
            with open(dp, "wb") as f:
                f.write((json.dumps(d, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
            ch = {it["term"]: 1 for it in (d["phrases"] + d["words"])[:3]}
            text2 = R.build_readable("fixture_e2e__b1b", d, {"choices": ch, "grammar": {}, "grammar_zero": False, "comment": ""}, d6_of_file(dp))
            with self.assertRaises(_rv.ConfirmedContentIssue):
                R.cmd_from_readable(self._paste(text2, "p2.txt"), self.run_dir, "b1b", "human", self.uref, data_dir=ddir)
            self.assertIsNone(_cc.load_record(self.kp_dir))


if __name__ == "__main__":
    if "--regen-fixtures" in sys.argv:
        regen_fixtures()
    else:
        unittest.main()
