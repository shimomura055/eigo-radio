"""委任_07: OPEN_ITEMS/DECISION_LOG/CURRENT_SPEC/REPORT_LEDGERへの追記(各1回、CRLF保持)。"""
import re

OI = ("委任_07(2026-10-06): 正式集計A〜E完了(主要値: Checker候補66[旧151]/floor発火4[旧37、数字3+S1 1]/Rewrite 6件・4 run[旧40件・8 run、必要4/不要2/再修正要0]/"
      "Human Review 0[旧1]/真の重大見逃し1件(meta_adv HC-012)/重大検出3件/¥31.52[旧¥43.91])、REPORT §81、ラベル=Sonnet推測+Fable突合(ユーザー未確認)。"
      "9/20 run時点、PRODUCTION_WIRED未。残11 runはユーザー総合レビュー待ち(開始禁止)。")
DL = ("\n(e) 【委任_07追記(2026-10-06、正式集計、¥0)】9/20 run正式集計: Checker候補66(旧151、AI46/機械20/重複0)、後段AI重大4(Y3/N1)・真に重大なのに非重大1、数字floor発火3(Y1/N2)+S1 BLOCKING化1(N)、"
      "Rewrite 6件/4 run(必要4/不要2/再修正要0)、Human Review 0、真の重大Fact見逃し1(meta_adv HC-012 restored、機械候補=reclassify対象外、Stage 2/S1が誤降格)/重大検出3、¥31.52(旧¥43.91)。"
      "Fable突合判定1〜6: (1)meta_adv HC-012=重大/Y/Y(方向反転、A5-0同型)、(2)meta_std HC-011=重大維持、(3)neg3 HF-002=問題なし、(4)neg7 Hook=軽微/Y/N、(5)neg2 ease of AI=問題なし、(6)neg1 HC-008=UNDECIDABLE維持(材料はREPORT §81-8)。"
      "ラベルはSonnet推測+Fable突合でユーザー未確認。ユーザー総合レビュー事項: Checker改善の実効/数字のみfloorのSafety(HC-012見逃し)/不要Rewrite減/Human Review 0/残11 run可否。PRODUCTION_WIRED未、残11 runはユーザー確認待ち。REPORT §81、`er052_output/open233_prod_e2e_02/report_final/`。\n")
CS = "【2026-10-06 9/20 run E2E完了(REPORT §81)】新仕様9 run E2E完走・正式集計済み(真の重大見逃し1/重大検出3、Human Review 0)、PRODUCTION_WIRED未(残11 runはユーザー総合レビュー待ち)。"
RL = "- 2026-10-06 | OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01 委任_05〜07 | 新仕様9/20 run E2E完走+正式集計(Checker候補66[旧151]、floor発火4[旧37]、Rewrite 6件/4run[旧40/8]、Human Review 0、真の重大見逃し1/重大検出3、¥31.52[旧¥43.91])、ラベル=Sonnet推測+Fable突合(ユーザー未確認)。REPORT §80/§81。PRODUCTION_WIRED未、残11 runはユーザー確認待ち、¥0。\n"


def rw(path, fn):
    t = open(path, encoding="utf-8", newline="").read()
    t2 = fn(t)
    assert t2 != t, path
    open(path, "w", encoding="utf-8", newline="").write(t2)


def oi(t):
    ls = t.split("\n")
    i = next(k for k, l in enumerate(ls) if l.startswith("| OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01 |"))
    l = ls[i]
    j = l.index(" | 区分:")
    l = l[:j].rstrip() + " " + OI + l[j:]
    l = l.replace("E2E9/20完走・ラベル未・PRODUCTION_WIRED未", "E2E9/20完走・正式集計済・PRODUCTION_WIRED未")
    ls[i] = l
    return "\n".join(ls)


def dl(t):
    k = t.index("\n## 2026-10-06 PROJECT-DELIVERY-SPEED-PARALLELIZATION-RULE-01 委任_01")
    nl = "\r\n" if "\r\n" in t else "\n"
    return t[:k].rstrip("\r\n") + nl + DL.replace("\n", nl) + nl + t[k:]


def cs(t):
    ls = t.split("\n")
    i = next(k for k, l in enumerate(ls) if l.startswith("【2026-10-06 ユーザー決定・配線中】"))
    cr = "\r" if ls[i].endswith("\r") else ""
    ls[i] = ls[i].rstrip("\r") + CS + cr
    return "\n".join(ls)


def rl(t):
    nl = "\r\n" if "\r\n" in t else "\n"
    return t.rstrip("\r\n") + nl + RL.rstrip("\n") + nl


rw("OPEN_ITEMS.md", oi)
rw("DECISION_LOG.md", dl)
rw("CURRENT_SPEC.md", cs)
rw("docs/pm/REPORT_LEDGER.md", rl)
print("ok")
