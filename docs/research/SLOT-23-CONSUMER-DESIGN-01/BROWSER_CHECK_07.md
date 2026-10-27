# BROWSER_CHECK_07 (委任_07G) X標準公開page 実ブラウザ検証
tool=F班 `tools/browser_check_s23f_01.py`(playwright chromium)再利用。対象=pages_s23g_1/index.html(X Std+Adv同一page)。結果json=evidence_runs/x2/30_browser_check.json、screenshots/X_public_s23g_*(11枚)。
- ①: underline double + 700、PC1280で画素差分の下線行2グループ(21-23px)、375(DPR3)/390(DPR2)でも2本。 ②: solid+700、1本。 ③: solid+400、1本。font-size/colorは本文同一(15.2px/黒)、背景なし。
- 装飾剥がしtextContent同一(strip_equal n=14 all_equal)、innerText⏸なし、data属性文字混入なし、コピーに余計な記号なし(public)、PC横スクロールなし(375/390は横スクロールtrue=F班が記録した「装飾の無いベースページでも発生する既存挙動」と同じ。本修正で新規発生ではない)。凡例1個(「本文の下線: …」)。
- 所見: F班(BROWSER_CHECK_06)と同一の見え方。
