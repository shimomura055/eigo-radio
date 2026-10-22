# -*- coding: utf-8 -*-
"""er070 (FAMILY-Z-STANDARD-PREVIEW-X-ALIGNMENT-01) 検証。API呼出なし(mockのみ)。"""
import json
import re
import sys
import unittest

import er070_family_z_std_preview_x_alignment_01 as m
import er003_v1_iran01_a2_generate as a2gen
import er062_family_z_writer_01 as w62

RUN = m.RUN
passed = 0


def check(name, cond):
    global passed
    assert cond, name
    passed += 1
    print("PASS", name)


# 1. 差分は SUBSTITUTIONS のみ(Xから置換リストを逆適用すると一致する)
t = m.Z_ROLE_TEMPLATE
for src, dst, _r, _y in m.SUBSTITUTIONS:
    t = t.replace(dst, src)
check("only listed substitutions differ from Family X", t == m.X_ROLE)
check("all substitutions news<->story derived", all(y for *_x, y in m.SUBSTITUTIONS))
check("no news-specific tokens remain", not any(k in m.Z_ROLE_TEMPLATE for k in ("ニュース", "記事", "Points", "In One Line")))
for k in m.VERBATIM_KEEP:
    check(f"verbatim keep: {k[:24]}", k in m.Z_ROLE_TEMPLATE and k in m.X_ROLE)

# 2. Dangling Reference: プレースホルダは comment_1/comment_2 のみで両方埋まる
ph = sorted(set(re.findall(r"\{(\w+)\}", m.Z_ROLE_TEMPLATE)))
check("placeholders == [comment_1, comment_2]", ph == ["comment_1", "comment_2"])
role = m.assemble_role("C1本文", "C2本文")
check("both comments embedded, no leftover braces", "C1本文" in role and "C2本文" in role and "{" not in role)
sup = json.load(open(f"{RUN}/support/a2_support.json", encoding="utf-8"))
role_real = m.assemble_role(sup["comments"]["1"], sup["comments"]["2"])
check("real Melos Comment 1 and 2 both in assembled role",
      sup["comments"]["1"] in role_real and sup["comments"]["2"] in role_real)
check("full prompt via build_support_prompt contains both",
      all(c in a2gen.build_support_prompt(role_real, "ctx") for c in (sup["comments"]["1"], sup["comments"]["2"])))
check("context heading is Family X verbatim", "新しいFactの追加禁止" in m.CONTEXT_HEAD_X)

# 3. Production(run_support_std)の事実確認(FZQI委任_06以降: Adv方式の日本語適用。Preview roleにComment 1・2が入る)
calls = []


def fn(client, role, ctx, model=None, **kw):
    calls.append((role, ctx))
    n = len(calls)
    txt = {1: "メロスは王に呪文のような約束を求められ、友人を人質に残して、妹の待つ村へ向かって一人で出発します。三日の約束があります。",
           2: "メロスは増水した川を渡り山道へ進みますが、途中で足を痛めて岩のそばに止まります。ここで待つか戻るかの選択があります。",
           3: "メロスは疲れた体で水を飲んで立ち上がり、一歩ずつ最後の道を進みます。町の門まではまだ遠い道のりが続いています。"}.get(n, "約束と友情をめぐって、一人の男が試される状況に置かれた物語です。いったいどう進むのかを見ていきます。")
    return {"status": "OK", "text": txt, "prompt": role, "attempts": []}


parts = {1: "Part one text.", 2: "Part two text.", 3: "Part three text.\n\nMore."}
try:
    out = w62.run_support_std(object(), parts, "FULL STORY", ja_support_fn=fn)
    prole = calls[-1][0]
    # 2026-10-19 FZQI委任_06で期待値更新: Production Std Previewは Adv方式の日本語適用(a2gen.PREVIEW_ROLE、Comment1・2両方を埋め込む)
    check("[updated] Production Std Preview role is a2gen.PREVIEW_ROLE with Comment 1 AND Comment 2",
          prole == a2gen.PREVIEW_ROLE.format(comment_1=out["comments"]["1"], comment_2=out["comments"]["2"]))
    check("[updated] Production Std Preview role contains Comment 1 and Comment 2",
          out["comments"]["1"] in prole and out["comments"]["2"] in prole)
    check("[order] Comment 1-3 generated before Preview (Comment 2 available at Preview time)", len(calls) == 4)
except Exception as e:   # mockシグネチャ不一致等でも原因を表示
    print("BASELINE_MOCK_NOTE", type(e).__name__, str(e)[:200])
    raise

# 4. prior再利用: prior指定時はComment1/2・Previewが再利用される(Preview再生成なし)
calls.clear()
out2 = w62.run_support_std(object(), parts, "FULL STORY", ja_support_fn=fn, prior=out)
check("[prior] Comment 1/2/Preview reused, only Comment 3 regenerated", len(calls) == 1 and out2["preview"] == out["preview"]
      and out2["comments"]["1"] == out["comments"]["1"] and out2["comments"]["2"] == out["comments"]["2"])

print(f"ALL PASS: {passed} checks")


class ScriptChecksTest(unittest.TestCase):
    """unittest discovery用(TEST-HYGIENE-02、2026-10-22): 本fileはstandalone script形式(`python <file>`で実行、
    終了codeで判定)。モジュール読込時に全checkが実行済みなので、その結果を1件のtestとして検証する。"""
    def test_all_checks_pass(self):
        # check()は失敗時にAssertionErrorを送出するため、ここへ到達した時点で全check PASS
        self.assertGreater(passed, 0)


if __name__ == "__main__":
    sys.exit(0)
