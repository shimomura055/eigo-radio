# Opus独立技術レビュー(ループ3)要約: WRITER-DEV-RISK-FLAGGER-DESIGN-01 Closeout前

- 対象: `er052_output/writer_dev_risk_flagger_01/`(FINAL_REPORT_DRAFT_01.md、HUMAN_CHECK_RISK_FLAGGER_01.md、P3/P4結果)
- 保存日: 2026-10-10(委任_04で保存)。Fableから受領した所見要約であり、Opus原文全文ではない。
- Fable照合: 全10件を採用(KPI定義・判定線は変更していない。STOP条件に該当せず)。推奨Closeout=USER_DECISION_REQUIRED を採用。

## 所見(10件)と反映先

1. 確認パック(a)がC_mainとD1v2を混在させKPI5が測れない -> C_main 3件必須提示・4択(A/B1/B2/C)・新規重大候補欄。反映: `make_human_check_01.py` v2、`HUMAN_CHECK_RISK_FLAGGER_01.md`。
2. KPI4は登録定義(開発+保留合算)でRollback 4/4合格。草稿は過小報告。反映: FINAL_REPORT_01 §0。
3. KPI1・2は合格だが余裕ゼロ(S0反転で8/13)。反映: §0 余裕欄。
4. Recall_human 3/3の独立証拠はK02のみ。反映: §2、§6。
5. 強制列挙でKPI3は構造上合格。可変件数は新仕様候補。rank1確信度分布は¥0で確認可。反映: §0、§1、§10。
6. 万能vs専用は1件差で結論を弱める。反映: §5。
7. 費用超過原因=dev外挿・大台帳・キャッシュ不発。次回見積法。今夜の有料追加は原則無し(D2 prompt変更時のみdev4件再確認<=¥5)。反映: §8(D2 promptは不変のため再確認不要、¥0)。
8. ラベル再確認は結果合わせの偏り -> 登録時ラベルを主値、修正後は併記。反映: パック(b)、§10。
9. パック分量は制約に合う。(c)にS0の文と質問を載せる。反映: パック(c)。
10. Checker比較は選択バイアス。偏りの少ない材料はK02の1件。反映: §6、§7。

推奨Closeout: USER_DECISION_REQUIRED。
