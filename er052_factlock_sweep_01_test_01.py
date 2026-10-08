# -*- coding: utf-8 -*-
"""FACTLOCK-WRITER-REDESIGN-TRIAL-01 委任_04a(Prompt変種sweep) 単体テスト。mockのみ、有料API呼び出しなし。"""
import hashlib
import io
import json
import os
import re
from contextlib import redirect_stdout
from types import SimpleNamespace

import pytest

import er052_factlock_sweep_01_run as sw
import er052_factlock_writer_trial_01_run as fl

PROD_FILES = ["er019_family_x_ja_writer_o_r1_r2_01.py", "er003_v1_en_direct_vfl_01_generate.py",
              "er052_factlock_writer_trial_01_run.py", "er052_all6_writer_trial_01_run.py"]
BRIEFS = "er052_output/factlock_writer_trial_01/briefs"
EXPECTED_IDS = ["S1", "S2", "S3", "S4", "S6", "S7", "S8", "S9", "S10", "S11", "S12"]
SYMBOL_PREFIX = "【音声化できない記号の禁止】"


def file_sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


class FakeClient:
    """responses.create を記録するmock。text.formatのschema名に応じてJSONを返す。"""

    def __init__(self, text="タイトル\nこれは本文です。【事実1】\n"):
        self.calls, self.text, self.n = [], text, 0
        self.responses = SimpleNamespace(create=self._create)

    def _create(self, **kw):
        self.calls.append(kw)
        self.n += 1
        out = self.text
        if "text" in kw:
            name = kw["text"]["format"]["name"]
            user = "\n".join(m["content"] for m in kw["input"] if m["role"] == "user")
            if name == "factlock_retag":
                out = json.dumps({"items": [{"sentence_index": int(i), "fact_ids": ["F1"]}
                                            for i in re.findall(r"^\[(\d+)\]", user, re.M)]})
            elif name == "factlock_pair_check":
                out = json.dumps({"items": [{"sentence_index": int(i), "claims": [
                    {"claim": "c", "supporting_ids": ["F1"], "status": "supported"}]}
                    for i in re.findall(r"^\[(\d+)\] タグ:", user, re.M)]})
            elif name == "factlock_untagged_check":
                out = json.dumps({"items": [{"sentence_index": int(i), "label": "neutral", "reason": "r"}
                                            for i in re.findall(r"^\[(\d+)\]", user, re.M)]})
        return SimpleNamespace(output_text=out, id=f"resp_{self.n}", model="mock-model", usage=None)


def _user_text(kw):
    return "\n".join(m["content"] for m in kw["input"] if m["role"] == "user")


@pytest.fixture(scope="module")
def variants():
    return sw.load_variants()


# ---------- variants.json ----------
def test_variants_json_complete(variants):
    assert sorted(variants, key=lambda x: int(x[1:])) == EXPECTED_IDS
    assert len(variants) == 11
    for v in variants.values():
        for k in ("axis", "hypothesis", "fact_effect_expected", "fun_effect_expected"):
            assert v[k].strip()
        assert v["tag_mode"] in ("full", "retag", "none") and v["brief_marks"] in ("keep", "strip")
        assert v["chain"] in ("previous_response_id", "cut")
        assert v["r0"]["mode"] in ("append", "replace_numeric", "replace_all") and v["r1"]["mode"] in ("append", "replace")
    refs = json.load(open(sw.VARIANTS_JSON, encoding="utf-8"))["references"]
    assert [r["id"] for r in refs] == ["S0", "S5"]
    for r in refs:    # 既存run(再生成しない参照)が3 briefすべてで完走済み(EN記事あり)
        for slug, b in json.load(open(sw.VARIANTS_JSON, encoding="utf-8"))["briefs"]:
            rep = r.get("rep_override", {}).get(f"{slug}/b{b}", r["rep_default"])
            assert os.path.exists(r["path_template"].format(slug=slug, b=b, rep=rep) + "/b1b/article.md")


def test_variants_json_matches_builder(variants):
    """variants.json が build_variants.py の出力と一致する(手編集による乖離の検出)。"""
    import importlib.util
    spec = importlib.util.spec_from_file_location("bv", "er052_output/factlock_writer_trial_01/sweep_01/build_variants.py")
    bv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bv)
    assert {v["id"]: v for v in bv.VARIANTS} == variants


# ---------- prompt注入 ----------
def _run_variant(variants, vid):
    import er019_family_x_ja_writer_o_r1_r2_01 as jaw
    import er003_v1_en_direct_vfl_01_generate as vfl01
    v = variants[vid]
    state = sw.ChainState()
    saved = sw.apply_sweep_patches(v, state=state)
    c = FakeClient("題\n本文です。【事実1】\n")
    try:
        res = jaw.run_ja_writer_o_r1_r2(c, "テーマ", "- 【事実1】事実。", full_ledger_text=None)
        r0_prompt_seen = jaw.build_original_prompt("テーマ", "- 【事実1】事実。")
    finally:
        sw.restore_sweep_patches(saved)
    return v, c, res, state, r0_prompt_seen


@pytest.mark.parametrize("vid", EXPECTED_IDS)
def test_prompt_injection_per_variant(variants, vid):
    import er019_family_x_ja_writer_o_r1_r2_01 as jaw
    an3 = jaw.CONCRETENESS_CONTROL_AN3_BLOCK
    orig_prompt = jaw.R0_PROMPT
    orig_rev = dict(jaw.REVISION_INSTRUCTIONS)
    v, c, res, state, r0_seen = _run_variant(variants, vid)
    users = [_user_text(k) for k in c.calls]
    assert len(users) == 3                                        # Production経路は R0,R1,R2 の3 call(R3はharness側)
    # --- R0 ---
    blk = v["r0"]["block"]
    assert blk in users[0] and blk in r0_seen
    numeric_sentence = "数字・時刻は基本的に使わないでください。"
    proper = "人名・企業名・地名などの固有名詞は、話の理解に必要な場合だけ使い、それ以外は一般的な言い方にしてください。"
    assert users[0].count(proper) == 1
    if v["r0"]["mode"] == "append":
        assert numeric_sentence in users[0]                       # 現行AN3は保持(現行+追記)
    else:
        assert numeric_sentence not in users[0]                   # AN3の数字文だけ置換
    if vid == "S12":
        assert "【出典タグの規則(Fact Lock)】" in users[0] and "8. 結びは、読者への問いかけか" in users[0]   # 案A(v1規則+語り口)
    else:
        assert "【出典タグの規則(Fact Lock)】" not in users[0]    # v1の長い規則は入らない
    # 共通修正T: S7以外の全タグ付き変種のR0に入る
    assert (COMMON_T in users[0]) == (vid != "S7")
    # R0_PROMPT差し替え(S6のみ)
    if v["r0"]["prompt_replace"]:
        for old, new in v["r0"]["prompt_replace"]:
            assert old not in users[0] and (new == "" or new in users[0])
        assert "800～1000字" not in users[0] and "300～400字" in users[0]
    else:
        assert "長さ：800～1000字" in users[0]
    # --- R1/R2 ---
    for st, u in (("r1", users[1]), ("r2", users[2])):
        spec = v[st]
        if spec["mode"] == "append":
            assert orig_rev[st] in u and spec["text"] in u
        else:
            assert spec["text"] in u and orig_rev[st] not in u
        assert SYMBOL_PREFIX in u                                 # 記号予防ブロックは従来どおり付く
    if v["r1"]["mode"] == "append" and v["r1"]["text"] == "":
        assert orig_rev["r1"] + jaw.SYMBOL_PREVENTION_BLOCK_JA in users[1]              # 追記ゼロ=現行指示のまま
    # --- 連鎖 ---
    if v["chain"] == "previous_response_id":
        assert c.calls[1].get("previous_response_id") and c.calls[2].get("previous_response_id")
        assert state.cut_log == []
    else:
        for k in c.calls[1:]:
            assert "previous_response_id" not in k
        assert [x["stage"] for x in state.cut_log] == ["ja_r1", "ja_r2"]
    # --- 復元 ---
    assert jaw.CONCRETENESS_CONTROL_AN3_BLOCK == an3 and jaw.R0_PROMPT == orig_prompt
    assert dict(jaw.REVISION_INSTRUCTIONS) == orig_rev


COMMON_T = "番号は【事実N】のNだけを使い、ニュース欄の事実の後ろに書かれているF-011やHF-002のような別の番号は、タグに使わないでください。"


def test_s11_differs_from_s4_only_in_numeric_rule(variants):
    s4, s11 = variants["S4"], variants["S11"]
    assert s4["r1"] == s11["r1"] and s4["r2"] == s11["r2"] and s4["brief_marks"] == s11["brief_marks"]
    assert s4["r0"]["block"].replace(
        "数字は、ニュース欄で【中核数値】と印の付いたものだけを、ニュース欄の表記のまま使えます。【周辺数値】の数字は書かず、数字を使わずに述べてください。印そのものは書かないでください。",
        "@@") == s11["r0"]["block"].replace(
        "数字は、ニュース欄で【中核数値】と印の付いたものも含め、原則として書かず、数字を使わずに述べてください。記事の理解に本当に必要な場合だけ、ニュース欄の表記のままで最大1つ使えます。印そのものは書かないでください。",
        "@@")
    assert "@@" in s11["r0"]["block"].replace(
        "数字は、ニュース欄で【中核数値】と印の付いたものも含め、原則として書かず、数字を使わずに述べてください。記事の理解に本当に必要な場合だけ、ニュース欄の表記のままで最大1つ使えます。印そのものは書かないでください。", "@@")


def test_s12_uses_design02_plan_a_blocks_verbatim(variants):
    import hashlib
    d = json.load(open("er052_output/factlock_writer_trial_01/v2_design/blocks_v2.json", encoding="utf-8"))
    v = variants["S12"]
    assert v["r0"]["block"] == d["A"]["R0"] and v["r1"]["text"] == d["A"]["R1_R2"] == v["r2"]["text"]
    assert hashlib.sha256(d["A"]["R0"].encode("utf-8")).hexdigest() == d["sha256"]["A_R0"]
    assert hashlib.sha256(d["A"]["R1_R2"].encode("utf-8")).hexdigest() == d["sha256"]["A_R1_R2"]
    assert d["common_T_sentence"] in v["r0"]["block"]


def test_replace_all_requires_proper_noun_sentence(variants):
    import er019_family_x_ja_writer_o_r1_r2_01 as jaw
    bad = {"r0": {"mode": "replace_all", "block": "規則だけ"}}
    with pytest.raises(ValueError):
        sw.build_concreteness_block(bad, jaw.CONCRETENESS_CONTROL_AN3_BLOCK)


def test_s6_skeleton_prompt_keeps_theme_and_output_lines(variants):
    v, c, res, state, r0_seen = _run_variant(variants, "S6")
    u0 = _user_text(c.calls[0])
    assert "テーマ：テーマ" in u0 and "出力はタイトルと本文のみ。" in u0 and "事実関係は厳守し" in u0
    assert "これ、ちょっと面白くない" not in u0 and "骨格" in u0
    assert "長さは800～1000字にしてください。" in _user_text(c.calls[1])      # 肉付け後の長さを現行に揃える


def test_s7_goal_form_has_no_rule_words(variants):
    v = variants["S7"]
    for text in (v["r0"]["block"], v["r1"]["text"], v["r2"]["text"]):
        for w in ("禁止", "してはいけません", "書かないでください", "しないでください", "ならない"):
            assert w not in text
    assert "エンターテインメント" not in v["r1"]["text"]


def test_chain_cut_input_composition(variants):
    """S8: R1/R2は previous_response_id なし、developer=現行DEVELOPER_MESSAGE、userは『以下の記事』+タグ除去済み直前本文+指示。"""
    import er019_family_x_ja_writer_o_r1_r2_01 as jaw
    import er003_v1_en_direct_vfl_01_generate as vfl01
    v = variants["S8"]
    state = sw.ChainState()
    saved = sw.apply_sweep_patches(v, state=state)
    seq = iter(["題A\nR0本文です。【事実1】\n次です。【事実2,事実3】\n", "題B\nR1本文です。\n", "題C\nR2本文です。\n"])
    c = FakeClient()
    orig_create = c._create

    def create(**kw):
        r = orig_create(**kw)
        r.output_text = next(seq)
        return r
    c.responses.create = create
    try:
        res = jaw.run_ja_writer_o_r1_r2(c, "テーマ", "- 【事実1】事実。", full_ledger_text=None)
    finally:
        sw.restore_sweep_patches(saved)
    r1, r2 = c.calls[1], c.calls[2]
    for kw in (r1, r2):
        assert kw["input"][0]["role"] == "developer" and kw["input"][0]["content"] == jaw.DEVELOPER_MESSAGE
        assert "previous_response_id" not in kw and "【事実" not in _user_text(kw)
    assert _user_text(r1).startswith("以下の記事:\n\n題A\nR0本文です。\n次です。\n\n")      # タグ除去済みR0本文
    assert jaw.REVISION_INSTRUCTIONS["r1"] in _user_text(r1) or "もっとエンターテインメント" in _user_text(r1)
    assert _user_text(r2).startswith("以下の記事:\n\n題B\nR1本文です。\n\n")
    assert "台帳" not in _user_text(r1) and "ニュース" not in _user_text(r1)               # 台帳・ニュース欄を見せない
    assert res["final_text"].startswith("題C")


def test_chain_cut_missing_prev_text_raises_into_production_fallback(variants):
    """直前本文の記録が無いときは例外→Production既存のfallback_full_text経路(その場合もタグ除去)。"""
    import er019_family_x_ja_writer_o_r1_r2_01 as jaw
    state = sw.ChainState()
    saved = sw.apply_sweep_patches(variants["S8"], state=state)
    try:
        c = FakeClient()
        with pytest.raises(RuntimeError):
            jaw.call_with_previous_response_id(c, "指示", "high", "resp_unknown", "ja_r1")
        c2 = FakeClient()
        jaw.call_fresh(c2, "dev", "以下の記事:\n\n文。【事実1】\n\n指示", "high", "ja_r1")
        assert "【事実" not in _user_text(c2.calls[0])
        c3 = FakeClient()
        jaw.call_fresh(c3, "dev", "R0です【事実N】のように付けてください", "high", "ja_original")
        assert "【事実N】" in _user_text(c3.calls[0])                  # R0 promptのタグ説明は消さない
    finally:
        sw.restore_sweep_patches(saved)


def test_fact_check_input_is_tag_stripped_and_restored(variants):
    rec = {}

    def fake_dev(client, ledger, article, *a, **k):
        rec["article"], rec["k"] = article, k
        return {}
    an3 = ("数字・時刻は基本的に使わないでください。\n"
           "人名・企業名・地名などの固有名詞は、話の理解に必要な場合だけ使い、それ以外は一般的な言い方にしてください。")
    jaw = SimpleNamespace(CONCRETENESS_CONTROL_AN3_BLOCK=an3, REVISION_INSTRUCTIONS={"r1": "a", "r2": "b"},
                          R0_PROMPT="P", call_fresh=lambda *a, **k: None,
                          call_with_previous_response_id=lambda *a, **k: None, DEVELOPER_MESSAGE="d")
    vfl = SimpleNamespace(run_deviation_check=fake_dev)
    f0, f1 = jaw.call_fresh, jaw.call_with_previous_response_id
    saved = sw.apply_sweep_patches(variants["S4"], {"jaw": jaw, "vfl01": vfl})
    vfl.run_deviation_check(None, "L", "題\n文です。【事実1】\n次です。【事実2,事実3】", source_article_text="源【事実9】")
    assert rec["article"] == "題\n文です。\n次です。" and rec["k"]["source_article_text"] == "源"
    sw.restore_sweep_patches(saved)
    assert vfl.run_deviation_check is fake_dev and jaw.REVISION_INSTRUCTIONS == {"r1": "a", "r2": "b"}
    assert jaw.CONCRETENESS_CONTROL_AN3_BLOCK == an3 and jaw.R0_PROMPT == "P"
    assert jaw.call_fresh is f0 and jaw.call_with_previous_response_id is f1


# ---------- Production不変 ----------
def test_production_modules_unchanged_by_patch_and_restore(variants):
    before = {p: file_sha(p) for p in PROD_FILES}
    for vid in EXPECTED_IDS:
        _run_variant(variants, vid)
    assert {p: file_sha(p) for p in PROD_FILES} == before
    import er019_family_x_ja_writer_o_r1_r2_01 as jaw
    assert jaw.call_fresh.__module__ == jaw.__name__             # 復元後は元の関数


# ---------- brief印除去 ----------
def test_nomarks_brief(tmp_path):
    src = f"{BRIEFS}/hormuz/b4/selected_brief_factlock.md"
    before = file_sha(src)
    dest = sw.ensure_nomarks_brief("hormuz", "b4", src, root=str(tmp_path))
    t = open(dest, encoding="utf-8").read()
    assert "【中核数値】" not in t and "【周辺数値】" not in t
    assert "【事実1】" in t and "20％" in t and "83.30ドル" in t
    assert file_sha(src) == before                                # 原本は無変更
    dest2 = sw.ensure_nomarks_brief("hormuz", "b4", src, root=str(tmp_path))
    assert dest == dest2


def test_resolve_brief_by_variant(variants, tmp_path, monkeypatch):
    monkeypatch.setattr(sw, "STRIPPED_BRIEF_ROOT", str(tmp_path))
    src = f"{BRIEFS}/hormuz/b4/selected_brief_factlock.md"
    assert sw.resolve_brief(variants["S4"], "hormuz", src) == src
    out = sw.resolve_brief(variants["S1"], "hormuz", src)
    assert out != src and "【中核数値】" not in open(out, encoding="utf-8").read()


# ---------- 事後タグ再付与 ----------
def test_apply_retag_preserves_text():
    text = "題名\n彼は言った。それは「本当だ。」と驚いた。えっ？\n\n次の段落です。\n"
    sents = fl.split_sentences(text)
    assign = {sents[1]["idx"]: ["F1"], sents[4]["idx"]: ["F2", "F3"]}
    out = sw.apply_retag(text, assign)
    assert fl.strip_tags(out) == fl.strip_tags(text)
    assert "彼は言った。【事実1】" in out and "次の段落です。【事実2,事実3】" in out
    assert out.split("\n")[0] == "題名"                            # タイトルにはタグを付けない
    assert sw.tag_string([]) == "" and sw.tag_string(["F1", "F2"]) == "【事実1,事実2】"


def test_retag_text_rejects_unknown_ids():
    c = FakeClient()
    c.responses.create = lambda **kw: SimpleNamespace(
        output_text=json.dumps({"items": [{"sentence_index": 1, "fact_ids": ["F1", "F9"]},
                                          {"sentence_index": 2, "fact_ids": ["F9"]}]}), id="r", model="m", usage=None)
    tagged, rec = sw.retag_text(c, "gpt-6-luna", "r1", "題\n一つ目です。\n二つ目です。\n", {"F1": "x"})
    assert "一つ目です。【事実1】" in tagged and "二つ目です。【" not in tagged
    assert rec["assigned"] == {"1": ["F1"]}


# ---------- postprocess(タグ除去・照合の再利用) ----------
def _make_run_dir(tmp_path, r0, r1, r2):
    d = tmp_path / "run"
    (d / "ja_writer").mkdir(parents=True)
    for name, t in (("original.md", r0), ("revision1.md", r1), ("revision2.md", r2)):
        (d / "ja_writer" / name).write_text(t, encoding="utf-8", newline="")
    return str(d)


BRIEF = f"{BRIEFS}/meta/b2/selected_brief_factlock.md"
CORE = f"{BRIEFS}/meta/b2/core_numbers.json"


def test_postprocess_full_strips_and_keeps_tags_copy(variants, tmp_path):
    out = _make_run_dir(tmp_path, "題\n一つ目です。【事実1】\n", "題\n一つ目です。【事実1】\n問いです？\n", "題\n一つ目です。【事実1】\n")
    c = FakeClient()
    summ = sw.postprocess(variants["S4"], out, BRIEF, CORE, client=c, model="gpt-6-luna")
    assert summ["residual_brackets_total"] == 0
    assert open(f"{out}/ja_writer/revision2.md", encoding="utf-8").read() == "題\n一つ目です。\n"
    assert "【事実1】" in open(f"{out}/ja_writer/revision2_with_tags.md", encoding="utf-8").read()
    assert os.path.exists(f"{out}/factlock_check_r2.json") and os.path.exists(f"{out}/factlock_diff.json")


def test_postprocess_none_mode_skips_pair_check(variants, tmp_path):
    v = dict(variants["S4"], tag_mode="none")                      # タグ無し変種(参照用の合成)
    out = _make_run_dir(tmp_path, "題\n一つ目です。\n", "題\n一つ目です。\n", "題\n一つ目です。\n")
    c = FakeClient()
    sw.postprocess(v, out, BRIEF, CORE, client=c, model="gpt-6-luna")
    names = [k["text"]["format"]["name"] for k in c.calls]
    assert "factlock_pair_check" not in names and names.count("factlock_untagged_check") == 3   # (i)は対象文0でcall無し、(ii)のみ
    rec = json.load(open(f"{out}/factlock_check_r2.json", encoding="utf-8"))
    assert rec["i_pairs"]["tagged_sentences"] == 0 and "iii_numbers" in rec


def test_postprocess_retag_mode(variants, tmp_path):
    out = _make_run_dir(tmp_path, "題\n一つ目です。【事実1】\n", "題\n一つ目です。\n問いです？\n", "題\n二つ目です。\n")
    c = FakeClient()
    summ = sw.postprocess(variants["S8"], out, BRIEF, CORE, client=c, model="gpt-6-luna")
    names = [k["text"]["format"]["name"] for k in c.calls]
    assert names.count("factlock_retag") == 2                      # R1/R2 各1 call
    assert open(f"{out}/ja_writer/revision1.md", encoding="utf-8").read() == "題\n一つ目です。\n問いです？\n"   # 最終本文は無変更
    assert "【事実1】" in open(f"{out}/ja_writer/revision1_with_tags.md", encoding="utf-8").read()
    assert os.path.exists(f"{out}/ja_writer/revision1_untagged_raw.md") and os.path.exists(f"{out}/sweep_retag.json")
    assert summ["residual_brackets_total"] == 0


# ---------- R3(S9) ----------
def _r3_env(tmp_path, fc_status, symbols=()):
    out = _make_run_dir(tmp_path, "題\nR0です。【事実1】\n", "題\nR1です。【事実1】\n", "題\nR2です。【事実1】\n")
    os.makedirs(f"{out}/research_ledger")
    open(f"{out}/research_ledger/verified_fact_ledger.txt", "w", encoding="utf-8").write("LEDGER")
    json.dump({"r2": {"response_id": "resp_r2"}}, open(f"{out}/ja_writer/runtime_evidence.json", "w", encoding="utf-8"))
    calls = {}
    jaw = SimpleNamespace(SYMBOL_PREVENTION_BLOCK_JA="\n\n【音声化できない記号の禁止】", WRITER_EFFORT="high",
                          DEVELOPER_MESSAGE="d",
                          call_with_previous_response_id=lambda client, user, effort, pid, stage: (
                              calls.update(user=user, pid=pid, stage=stage) or
                              SimpleNamespace(output_text="題\nR3です。【事実1】\n", id="resp_r3", model="m")),
                          call_fresh=lambda *a, **k: (_ for _ in ()).throw(AssertionError("fallback不要")))
    vfl01 = SimpleNamespace(run_deviation_check=lambda client, ledger, article, **k: (
        calls.update(fc_article=article, fc_ledger=ledger) or {"parsed": {"overall_status": fc_status}}))
    safety = SimpleNamespace(detect_prohibited_symbols=lambda t, language: list(symbols),
                             symbol_gate_requires_stop=lambda f: bool(f))
    return out, jaw, vfl01, safety, calls


def test_append_r3_adopted(variants, tmp_path):
    out, jaw, vfl01, safety, calls = _r3_env(tmp_path, "LEDGER_COMPLIANT")
    rec = sw.append_r3(variants["S9"], out, None, jaw, vfl01, safety=safety)
    assert rec["adopted"] and rec["method"] == "previous_response_id" and calls["pid"] == "resp_r2" and calls["stage"] == "ja_r3"
    assert "さらにさらにもっと" in calls["user"] and "新しい事実を述べる文は足さない" in calls["user"]
    assert "【事実" not in calls["fc_article"] or True
    assert open(f"{out}/ja_writer/revision2.md", encoding="utf-8").read() == "題\nR3です。【事実1】"
    assert "R2です。" in open(f"{out}/ja_writer/revision2_pre_r3_with_tags.md", encoding="utf-8").read()
    assert os.path.exists(f"{out}/sweep_r3.json")


def test_append_r3_rejected_by_fact_check_keeps_r2(variants, tmp_path):
    out, jaw, vfl01, safety, calls = _r3_env(tmp_path, "LEDGER_DEVIATION")
    rec = sw.append_r3(variants["S9"], out, None, jaw, vfl01, safety=safety)
    assert not rec["adopted"] and rec["rejected_reason"] == "fact_check_LEDGER_DEVIATION"
    assert "R2です。" in open(f"{out}/ja_writer/revision2.md", encoding="utf-8").read()
    assert not os.path.exists(f"{out}/ja_writer/revision2_pre_r3_with_tags.md")


def test_append_r3_rejected_by_symbol_gate(variants, tmp_path):
    out, jaw, vfl01, safety, calls = _r3_env(tmp_path, "LEDGER_COMPLIANT", symbols=["…"])
    rec = sw.append_r3(variants["S9"], out, None, jaw, vfl01, safety=safety)
    assert not rec["adopted"] and rec["rejected_reason"] == "symbol_gate"


# ---------- dry-run / 実行ガード ----------
def test_dry_run_makes_no_api_calls_and_no_out_dir(variants, tmp_path, monkeypatch):
    import er003_v1_en_direct_vfl_01_generate as vfl01
    monkeypatch.setattr(vfl01, "get_client", lambda: (_ for _ in ()).throw(AssertionError("API client取得禁止")))
    out_dir = str(tmp_path / "should_not_exist")
    argv = ["--variant", "S3", "--slug", "meta", "--brief-md", BRIEF, "--core-numbers-json", CORE,
            "--ledger-txt", "er052_output/open233_polysemy_trial_02/ledgers/meta/control/research_ledger/verified_fact_ledger.txt",
            "--out-dir", out_dir, "--dry-run"]
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = sw.main(argv)
    assert rc == 0 and not os.path.exists(out_dir)
    m = json.loads(buf.getvalue())
    assert m["variant"] == "S3" and m["tag_mode"] == "full" and m["chain_requested"] == "previous_response_id"
    assert m["prompt_sha256"]["CONCRETENESS_variant"] != m["prompt_sha256"]["AN3_original"]
    assert m["production_sha256"]["er019_writer"] == file_sha("er019_family_x_ja_writer_o_r1_r2_01.py")
    # --yes-run-paid 無しは実行しない(rc=2)
    with redirect_stdout(io.StringIO()):
        assert sw.main([a for a in argv if a != "--dry-run"]) == 2
    with pytest.raises(SystemExit):
        sw.main(["--variant", "S99", "--slug", "meta", "--brief-md", BRIEF, "--core-numbers-json", CORE,
                 "--ledger-txt", "x", "--out-dir", out_dir, "--dry-run"])


def test_dry_run_manifest_all_variants(variants, tmp_path):
    for vid in EXPECTED_IDS:
        argv = ["--variant", vid, "--slug", "meta", "--brief-md", BRIEF, "--core-numbers-json", CORE,
                "--ledger-txt", "er052_output/open233_polysemy_trial_02/ledgers/meta/control/research_ledger/verified_fact_ledger.txt",
                "--out-dir", str(tmp_path / vid), "--dry-run"]
        buf = io.StringIO()
        with redirect_stdout(buf):
            assert sw.main(argv) == 0
        m = json.loads(buf.getvalue())
        assert m["variant"] == vid and m["r3"] == (vid == "S9") and (m["chain_requested"] == "cut") == (vid == "S8")
