# -*- coding: utf-8 -*-
"""FACTLOCK-WRITER-REDESIGN-TRIAL-01 単体テスト(mockのみ、有料API呼び出しなし)。"""
import glob
import json
import os
import re
import subprocess
from types import SimpleNamespace

import pytest

import er052_factlock_writer_trial_01_run as h

PROD_FILES = ["er019_family_x_ja_writer_o_r1_r2_01.py", "er003_v1_en_direct_vfl_01_generate.py",
              "er006_model_routing_contract_01.py", "er019_family_x_entertainment_production_runner_01.py",
              "er003_audio_tts_asr_safety.py"]
BRIEFS = "er052_output/factlock_writer_trial_01/briefs"


class FakeClient:
    """responses.create を記録し、固定テキストを返すmock。"""

    def __init__(self, text="タイトル\nこれは本文です。【事実1】\n"):
        self.calls, self.text, self.n = [], text, 0
        self.responses = SimpleNamespace(create=self._create)

    def _create(self, **kw):
        self.calls.append(kw)
        self.n += 1
        return SimpleNamespace(output_text=self.text, id=f"resp_{self.n}", model="mock-model", usage=None)


def _user_text(kw):
    return "\n".join(m["content"] for m in kw["input"] if m["role"] == "user")


def test_production_files_unchanged_vs_head():
    r = subprocess.run(["git", "diff", "--stat", "HEAD", "--"] + PROD_FILES,
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0 and r.stdout.strip() == "", r.stdout


def test_prompt_injection_reaches_r0_r1_r2_and_restores():
    import er019_family_x_ja_writer_o_r1_r2_01 as jaw
    import er003_v1_en_direct_vfl_01_generate as vfl01
    before = (h.sha256_text(jaw.CONCRETENESS_CONTROL_AN3_BLOCK), dict(jaw.REVISION_INSTRUCTIONS),
              vfl01.run_deviation_check)
    saved = h.apply_factlock_patches()
    try:
        c = FakeClient()
        res = jaw.run_ja_writer_o_r1_r2(c, "テーマ", "- 【事実1】事実。", full_ledger_text=None)
        users = [_user_text(k) for k in c.calls]
        assert len(users) == 3
        assert "【出典タグの規則(Fact Lock)】" in users[0]
        assert "数字・時刻は基本的に使わないでください" not in users[0]
        assert users[0].count("人名・企業名・地名などの固有名詞は") == 1 and "【中核数値】" in users[0]
        for u in users[1:]:
            assert "【事実固定の規則(Fact Lock)】" in u
        # M2: must-fix最優先条項がR0/R1/R2すべてに入る
        assert all("事実確認の修正指示がある場合はそれを最優先し、直すか削る。" in u for u in users)
        # O1: 新タグ形式の説明(旧【F1】は出ない)
        assert "【事実1,事実2】" in users[0] and "【F1】" not in users[0] and "【F1】" not in users[1]
        # M4
        assert "「〜しなかった」「〜はない」「唯一」「初めて」" in users[0]
        assert "暮らしとのつながりは、問いかけや「〜かもしれない」の形で示し、具体的な事実を断定しない" in users[0]
        # M5: 周辺数値は数字を省けば書ける、タイトルは中核数値OKだがタグなし
        assert "数字を省いて述べてよい" in users[0] and "禁じるのは、数字の大きさを" in users[0]
        assert "タイトルでも使えますが、タイトルにはタグを付けません" in users[0]
        # M6
        for u in users[1:]:
            assert "文をまとめたら両方のタグを付け、分けたらそれぞれに該当するタグを付けます" in u
            assert "記事にすでにある事実の言い直しは、新しい事実に当たりません" in u
            assert "「もし〜なら」と分かる形のたとえ話・仮定" in u
        assert "事実関係は変えずに" in users[1] and "さらにもっと" in users[2]
        assert c.calls[1]["previous_response_id"] and c.calls[2]["previous_response_id"]
        assert res["final_text"]
    finally:
        h.restore_factlock_patches(saved)
    assert h.sha256_text(jaw.CONCRETENESS_CONTROL_AN3_BLOCK) == before[0]
    assert dict(jaw.REVISION_INSTRUCTIONS) == before[1] and vfl01.run_deviation_check is before[2]


def test_fact_check_input_is_tag_stripped():
    rec = {}

    def fake_dev(client, ledger, article, *a, **k):
        rec["article"], rec["k"] = article, k
        return {}
    an3 = ("数字・時刻は基本的に使わないでください。\n"
           "人名・企業名・地名などの固有名詞は、話の理解に必要な場合だけ使い、それ以外は一般的な言い方にしてください。")
    jaw = SimpleNamespace(CONCRETENESS_CONTROL_AN3_BLOCK=an3, REVISION_INSTRUCTIONS={"r1": "a", "r2": "b"})
    vfl = SimpleNamespace(run_deviation_check=fake_dev)
    saved = h.apply_factlock_patches({"jaw": jaw, "vfl01": vfl})
    vfl.run_deviation_check(None, "L", "題\n文です。【事実1】\n次です。【事実2,事実3】", source_article_text="源【事実9】")
    assert rec["article"] == "題\n文です。\n次です。" and rec["k"]["source_article_text"] == "源"
    h.restore_factlock_patches(saved)
    assert vfl.run_deviation_check is fake_dev and jaw.REVISION_INSTRUCTIONS == {"r1": "a", "r2": "b"}
    assert jaw.CONCRETENESS_CONTROL_AN3_BLOCK == an3


def test_tag_symbol_is_not_blocked_by_existing_symbol_gate():
    import er003_audio_tts_asr_safety as safety
    f = safety.detect_prohibited_symbols("彼は謝った。【事実3】\nそれが問題だ。【事実1,事実2】", "ja")
    assert not safety.symbol_gate_requires_stop(f)
    f2 = safety.detect_prohibited_symbols("彼は謝った。[F-3]", "ja")
    assert safety.symbol_gate_requires_stop(f2)    # 角括弧案は既存Gateに止められる(不採用の根拠)


def test_strip_and_sentences():
    t = "題名\n彼は言った。【事実1】それは「本当だ。」と。【事実2,事実3】 えっ？\n"
    assert h.strip_tags(t) == "題名\n彼は言った。それは「本当だ。」と。 えっ？\n"
    s = h.split_sentences(t)
    assert s[0]["is_title"] and not s[0]["tags"]
    assert [x["tags"] for x in s[1:]] == [["F1"], ["F2", "F3"], []]
    assert s[2]["text"] == "それは「本当だ。」と。"
    assert h.tag_ids("【事実1,事実2】") == ["F1", "F2"]


@pytest.mark.parametrize("text,expect", [
    ("20％の償還", [("20", "%")]),
    ("約2.6％高で1バレル85ドル", [("2.6", "%"), ("1", "バレル"), ("85", "ドル")]),
    ("７月１３日午前１０時１６分", [("7", "月"), ("13", "日"), ("10", "時"), ("16", "分")]),
    ("1,500個超", [("1500", "個")]),
    ("二十パーセントと三万人", [("20", "%"), ("30000", "人")]),
    ("一部は十分に。万が一、千葉で。一方で", []),
    ("MUSE-HC-006 と F-001 と HF-009【事実12】", []),
    ("第4条と2025年", [("4", "条"), ("2025", "年")]),
    ("二人と三千五百円", [("2", "人"), ("3500", "円")]),
])
def test_extract_numbers(text, expect):
    assert [t["key"] for t in h.extract_numbers(text)] == [tuple(e) for e in expect]


def test_hedge_detected():
    t = h.extract_numbers("約2.6％と1,500個超")
    assert t[0]["hedge"] == ("約", None) and t[1]["hedge"] == (None, "超")


def test_check_numbers_against_core():
    core = h.load_core_numbers(f"{BRIEFS}/hormuz/b1/core_numbers.json")
    text = ("題\n20％を求めた。【事実1】\nおよそ2.6％高だった。【事実3】\n85ドルを超えた。\n"
            "7月13日に投稿。【事実1】\n約20％だと。【事実1】\n")
    r = h.check_numbers(text, core)
    st = [(x["surface"], x["status"]) for x in r["tokens"]]
    assert ("20%", "match") in st
    assert any(x["status"] == "hedge_changed" and x["surface"].startswith("およそ2.6") for x in r["tokens"])
    assert ("7月", "not_core") in st
    assert any(x["status"] == "hedge_changed" and x["surface"].startswith("約20") for x in r["tokens"])
    assert [w["surface"] for w in r["core_used_without_tag"]] == ["85ドル"]
    assert r["mismatch_total"] == r["counts"]["hedge_changed"] + r["counts"]["not_core"] >= 4


def test_meta_core_empty_flags_every_number():
    core = h.load_core_numbers(f"{BRIEFS}/meta/b1/core_numbers.json")
    assert core["atoms"] == {}
    r = h.check_numbers("題\n3人が来た。【事実1】\n", core)
    assert r["counts"]["not_core"] == 1


def test_diff_tagged_kept_modified_deleted_added():
    a = "題\nトランプ氏は20％を求めると投稿した。【事実1】\n攻撃の懸念が続いた。【事実3】\nこれは削られる。【事実2】\n"
    b = "題\nさてトランプ氏は20％を求めると投稿した。【事実1】\n攻撃の懸念が続いた。【事実3】\n新しい事実である。【事実4】\n問いかけはどう？\n"
    d = h.diff_tagged(a, b)
    kinds = {tuple(p["tags_prev"]): p["kind"] for p in d["pairs"]}
    assert kinds[("F3",)] == "kept" and kinds[("F2",)] == "deleted" and kinds[("F1",)] in ("kept", "modified")
    assert d["counts"]["added"] == 1


def test_annotated_briefs_valid():
    import er052_open233_polysemy_nb_dev_01 as dev
    files = sorted(glob.glob(f"{BRIEFS}/*/b*/selected_brief_factlock.md"))
    assert len(files) == 12
    for f in files:
        txt = open(f, encoding="utf-8").read()
        dev.parse_brief_md(txt)                                    # DEV runnerのbrief形式
        facts = h.parse_annotated_facts(txt)
        assert facts and list(facts) == [f"F{i}" for i in range(1, len(facts) + 1)]
        core = json.load(open(os.path.join(os.path.dirname(f), "core_numbers.json"), encoding="utf-8"))
        assert len(core["core"]) <= 3
        assert "【F" not in txt                                      # O1: 旧形式が残っていない
        assert all(re.match(r"^\s*(?:-|・)\s*【事実\d+】", l) for l in txt.split("\n")
                   if l.strip() and re.search(r"【事実\d+】", l))
        for c in core["core"]:
            assert any(l + "【中核数値】" in txt for l in c["literals"])
        for p in core["peripheral"]:
            assert p + "【周辺数値】" in txt


def test_postprocess_phase1_with_mock(tmp_path):
    out = tmp_path / "run"
    jd = out / "ja_writer"
    jd.mkdir(parents=True)
    t0 = "題\nトランプ氏は20％を求めると投稿した。【事実1】\nどう思う？\n"
    t1 = "題\nさてトランプ氏は20％を求めると投稿した。【事実1】\n実は誰も知らない裏話がある。\n"
    t2 = "題\nトランプ氏は30％を求めた。【事実1】\n"
    for n, t in zip(("original.md", "revision1.md", "revision2.md"), (t0, t1, t2)):
        (jd / n).write_text(t, encoding="utf-8")
    brief = f"{BRIEFS}/hormuz/b1/selected_brief_factlock.md"
    core = f"{BRIEFS}/hormuz/b1/core_numbers.json"

    class C(FakeClient):
        def _create(self, **kw):
            self.calls.append(kw)
            name = kw["text"]["format"]["name"]
            if name == "factlock_pair_check":
                data = {"items": [{"sentence_index": 1, "claims": [
                    {"claim": "数値違い", "supporting_ids": [], "status": "unsupported"}]}]}
            else:
                data = {"items": [{"sentence_index": 2, "label": "new_specific_claim", "reason": "新事実"}]}
            return SimpleNamespace(output_text=json.dumps(data), id="r", model="mock", usage=None)
    c = C()
    s = h.postprocess_phase1(str(out), brief, core, client=c, model="mock")
    assert len(c.calls) == 6                                        # M7: タイトルも(ii)の対象なのでr2でも(ii)を呼ぶ
    assert s["strip"]["r2"]["residual_brackets_after_strip"] == 0 and s["residual_brackets_total"] == 0
    assert s["stages"]["r2"]["iii_numbers"]["counts"]["not_core"] == 1  # 30％
    assert s["stages"]["r2"]["i_pairs"]["counts"]["不整合"] == 1
    assert (jd / "revision2.md").read_text(encoding="utf-8") == "題\nトランプ氏は30％を求めた。\n"
    assert (jd / "revision2_with_tags.md").read_text(encoding="utf-8") == t2
    for st in ("r0", "r1", "r2"):
        assert (out / f"factlock_check_{st}.json").exists()
    assert (out / "factlock_diff.json").exists() and (out / "factlock_summary.json").exists()
    assert all("【" not in (jd / n).read_text(encoding="utf-8")
               for n in ("original.md", "revision1.md", "revision2.md"))


def test_dry_run_makes_no_api_and_no_dir(tmp_path, capsys):
    brief = f"{BRIEFS}/meta/b1/selected_brief_factlock.md"
    core = f"{BRIEFS}/meta/b1/core_numbers.json"
    ledger = "er052_output/open233_polysemy_trial_02/ledgers/meta/control/research_ledger/verified_fact_ledger.txt"
    if not os.path.exists(ledger):
        pytest.skip("ledger not present")
    out = tmp_path / "x"
    rc = h.main(["--slug", "meta", "--brief-md", brief, "--core-numbers-json", core, "--ledger-txt", ledger,
                 "--out-dir", str(out), "--dry-run"])
    assert rc == 0 and not out.exists()
    j = json.loads(capsys.readouterr().out)
    assert j["arm"] == "factlock_6luna" and j["core_numbers_sha256"] and j["prompt_sha256"]["FACTLOCK_R0_BLOCK"]


# ---------------- v2(Opus条件A M1〜M9 / O1・O2)追加テスト ----------------
def test_m1_aggregate_claims():
    S = lambda *st: [{"claim": "c", "supporting_ids": [], "status": x} for x in st]
    assert h.aggregate_claims(S("supported", "supported")) == "整合"
    assert h.aggregate_claims(S("supported", "unsupported")) == "不整合"
    assert h.aggregate_claims(S("undecidable", "unsupported")) == "不整合"
    assert h.aggregate_claims(S("supported", "undecidable")) == "判定不能"
    assert h.aggregate_claims([]) == "判定不能"


def test_m1_pair_blocks_union_and_prev_context():
    sents = h.split_sentences("題\nAが起きた。【事実1】\nそれでBになった。【事実1,事実2】\n")
    facts = {"F1": "Aが起きた事実", "F2": "Bになった事実", "F3": "無関係な事実"}
    blocks, tagged, unknown = h.build_pair_blocks(sents, facts)
    assert [s["idx"] for s in tagged] == [1, 2] and unknown == []
    b2 = blocks.split("\n\n")[1]
    assert "直前の文: Aが起きた。" in b2                        # 直前の文を文脈として渡す
    assert "F1: Aが起きた事実" in b2 and "F2: Bになった事実" in b2   # タグ事実の和集合
    assert "F3" not in blocks                                    # 付いていない事実は渡さない
    _, _, unk = h.build_pair_blocks(h.split_sentences("題\n本文。【事実9】\n"), facts)
    assert unk == [{"sentence_idx": 1, "tag": "F9"}]


def test_m1_pair_check_sentence_level_with_mock():
    sents = h.split_sentences("題\nAが起きた。【事実1】\nそれでBになった。【事実1,事実2】\n三つ目。【事実2】\n")
    facts = {"F1": "a", "F2": "b"}

    class C(FakeClient):
        def _create(self, **kw):
            self.calls.append(kw)
            data = {"items": [
                {"sentence_index": 1, "claims": [{"claim": "A", "supporting_ids": ["F1"], "status": "supported"}]},
                {"sentence_index": 2, "claims": [{"claim": "A", "supporting_ids": ["F1"], "status": "supported"},
                                                 {"claim": "B", "supporting_ids": ["F1", "F2", "F3"], "status": "supported"}]},
                {"sentence_index": 3, "claims": [{"claim": "X", "supporting_ids": [], "status": "unsupported"},
                                                 {"claim": "Y", "supporting_ids": ["F2"], "status": "supported"}]}]}
            return SimpleNamespace(output_text=json.dumps(data), id="r", model="mock", usage=None)
    c = C()
    r = h.pair_check(c, "mock", "r0", sents, facts)
    assert [i["verdict"] for i in r["items"]] == ["整合", "整合", "不整合"]
    assert r["counts"] == {"整合": 2, "不整合": 1, "判定不能": 0}
    assert r["claim_counts"] == {"supported": 4, "unsupported": 1, "undecidable": 0}
    assert r["items"][1]["supporting_outside_tags"] == ["F3"] and r["inconsistent_sentences"] == [3]
    assert "claims" in _user_text(c.calls[0]) or "主張" in _user_text(c.calls[0])


def test_m3_broad_strip_and_residual_counts():
    t = "題\n文。【事実1】また。【Ｆ2】さらに。【F2-3】そして。【F9】次。【事実1】【事実2】 末【 事実 3-4】\n"
    s = h.strip_tags(t)
    assert "【" not in s and h.count_residual_brackets(s) == 0
    assert h.count_broad_only_tags(t) == 4   # Ｆ2・F2-3・F9・事実 3-4 は変形
    assert h.count_broad_only_tags("題\n文。【事実1】\n") == 0
    # 広め除去に掛からない【】は残り、件数として記録される(HF-002 は『F』始まりでなく『H』始まりなので残る)
    assert h.count_residual_brackets(h.strip_tags("文。【HF-002】【中核数値】")) == 1
    assert h.strip_tags("文20％【中核数値】と80【周辺数値】。【事実1】") == "文20％と80。"


def test_m3_scan_residual_brackets(tmp_path):
    (tmp_path / "ja_writer").mkdir()
    (tmp_path / "ja_writer" / "revision2.md").write_text("題\n本文。\n", encoding="utf-8")
    (tmp_path / "ja_writer" / "revision2_with_tags.md").write_text("題\n本文。【事実1】\n", encoding="utf-8")
    (tmp_path / "factlock_check_r0.json").write_text('{"x": "【事実1】"}', encoding="utf-8")
    assert h.scan_residual_brackets(str(tmp_path))["unexpected"] == []
    (tmp_path / "en_article.md").write_text("Title\nBody 【事実1】\n", encoding="utf-8")
    r = h.scan_residual_brackets(str(tmp_path))
    assert [u["file"] for u in r["unexpected"]] == ["en_article.md"] and r["unexpected_total"] == 1


def test_o1_tag_format_strict_and_ids():
    assert h.tag_ids("【事実1,事実2】") == ["F1", "F2"] and h.tag_ids("【事実3,4】") == ["F3", "F4"]
    s = h.split_sentences("題\n本文。【事実1,事実2】\n別。【事実3】\n")
    assert [x["tags"] for x in s[1:]] == [["F1", "F2"], ["F3"]]
    assert h.TAG_RE.fullmatch("【事実12】") and not h.TAG_RE.fullmatch("【F1】")
    facts = h.parse_annotated_facts("## Selected Facts\n- 【事実1】甲20％【中核数値】。\n- 【事実2】乙。\n")
    assert facts == {"F1": "甲20％。", "F2": "乙。"}


def test_m7_untagged_five_labels_and_title_included():
    assert h.UNTAGGED_LABELS == ("neutral", "untagged_brief_fact", "hedged_speculation",
                                 "background_general", "new_specific_claim")
    sents = h.split_sentences("題名は20％\n問いかけ？\n本文。【事実1】\n")
    seen = {}

    class C(FakeClient):
        def _create(self, **kw):
            self.calls.append(kw)
            seen["prompt"] = _user_text(kw)
            data = {"items": [{"sentence_index": 0, "label": "new_specific_claim", "reason": "題"},
                              {"sentence_index": 1, "label": "neutral", "reason": "問い"}]}
            return SimpleNamespace(output_text=json.dumps(data), id="r", model="mock", usage=None)
    r = h.untagged_check(C(), "mock", "r0", sents, {"F1": "x"})
    assert "(タイトル)" in seen["prompt"] and "[0](タイトル) 題名は20％" in seen["prompt"]
    assert r["untagged_sentences"] == 2 and r["title_label"] == "new_specific_claim"
    assert r["counts"] == {"neutral": 1, "untagged_brief_fact": 0, "hedged_speculation": 0,
                           "background_general": 0, "new_specific_claim": 1}
    assert all(lab in seen["prompt"] for lab in h.UNTAGGED_LABELS)


def test_title_numbers_checked_deterministically():
    core = h.load_core_numbers(f"{BRIEFS}/hormuz/b1/core_numbers.json")
    r = h.check_numbers("20％の衝撃と99社\n本文。【事実1】\n", core)
    st = {(x["surface"], x["status"], x["is_title"]) for x in r["tokens"]}
    assert ("20%", "match", True) in st and ("99社", "not_core", True) in st
    assert r["core_used_without_tag"] == []                      # タイトルの中核数値はタグ不要


def test_o2_quantity_words_counted_separately():
    r = h.count_quantity_words("題\n半分が、二倍に。いくつかが、ひとつだけ。【事実1】多数とたくさん。\n")
    assert r["count"] == 6 and r["items"][:2] == ["半分", "二倍"]
    core = h.load_core_numbers(f"{BRIEFS}/meta/b1/core_numbers.json")
    c = h.check_numbers("題\n半分が来た。【事実1】\n", core)
    assert c["quantity_words"]["count"] == 1 and c["mismatch_total"] == 0   # 判定(mismatch)には使わない


def test_manifest_sha_includes_new_prompts_and_dry_run_shas_stable(tmp_path):
    import hashlib
    assert h.MUSTFIX_PRIORITY in h.FACTLOCK_REVISION_BLOCK and h.MUSTFIX_PRIORITY in h.FACTLOCK_R0_BLOCK_TAIL
    assert hashlib.sha256(h.PAIR_PROMPT.encode("utf-8")).hexdigest() != hashlib.sha256(
        h.UNTAGGED_PROMPT.encode("utf-8")).hexdigest()
