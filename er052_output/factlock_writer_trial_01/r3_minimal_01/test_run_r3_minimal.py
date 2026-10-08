# -*- coding: utf-8 -*-
"""mockテスト(APIなし): 入力構成・ソース選択・費用計算。"""
import os, sys, types, tempfile
sys.path.insert(0, os.path.dirname(__file__))
import run_r3_minimal as m

def test_select_sources():
    its = m.select_sources()
    assert len(its) == 12
    pick = {i["key"]: i["rep"] for i in its}
    assert pick["meta/b3__all6__r2"] == 2 or any(i["slug"] == "meta" and i["b"] == 3 and i["rep"] == 2 for i in its)
    assert all(os.path.exists(i["r2_path"]) and os.path.exists(i["ledger_path"]) for i in its)

def test_inputs():
    import er019_family_x_ja_writer_o_r1_r2_01 as jaw
    s = m.build_fresh_input("本文X", jaw.SYMBOL_PREVENTION_BLOCK_JA)
    assert s.startswith("以下の記事:\n\n本文X\n\n事実は変えずにエンターテイメント性をもっと上げた記事にReviseください。")
    assert jaw.SYMBOL_PREVENTION_BLOCK_JA in s and "台帳" not in s
    c = m.build_chain_instruction(jaw.SYMBOL_PREVENTION_BLOCK_JA)
    assert c.startswith(m.R3_SENTENCE)

def test_cost():
    assert abs(m.jpy(1_000_000, 0, 0) - 16.0) < 1e-6
    assert abs(m.jpy(0, 0, 1_000_000) - 80.0) < 1e-6

def test_gen_fresh_mock(tmp_path=None):
    import er019_family_x_ja_writer_o_r1_r2_01 as jaw
    calls = []
    class R: id="resp_x"; model="gpt-6-luna"; output_text=" 出力 "; usage=types.SimpleNamespace(input_tokens=10, output_tokens=5, input_tokens_details=None, output_tokens_details=None)
    class C:
        class responses:
            @staticmethod
            def create(**k): calls.append(k); return R()
    it = m.select_sources()[0]
    d = tempfile.mkdtemp(); it = dict(it, out=d)
    m.BASE = d
    m.gen_one(C, jaw, it, "fresh", 60, {})
    assert calls[0]["model"] == "gpt-6-luna" and calls[0]["input"][0]["role"] == "developer"
    assert "事実は変えずに" in calls[0]["input"][1]["content"]
    assert open(f"{d}/r3_fresh.md", encoding="utf-8").read() == "出力"

if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"): f(); print("OK", n)
