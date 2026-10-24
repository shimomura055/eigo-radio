ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_06(Fableから): OPEN-494を是正し、OPEN-492を「修正へ進む/対応不要」に決着させ、OPEN-487・491のFable受入(PRODUCTION_WIRED)をSSOTに記録してcommit/pushする。API 0・有料run 0。

## 0. 前提
- 直前の委任_05成果: commits d6d17562b(487案A)/7d4ec5bc4(491)/6b2fe25e0(SSOT)。報告本文 `docs/pm/RESULT_PACKET_ATN5.md`(gitignore)、`docs/research/ASR-TIME-NUMERAL-EQUIVALENCE-01/{IMPL_487_01,IMPL_491_01}.md`、`runtime06_compare.txt`。ユーザー指示原文 `docs/pm/delegation_log/2026-10-24_ASR-TIME-NUMERAL-EQUIVALENCE-01_USER.md`(§6 Production受入必須条件、「既存承認仕様の不具合で対応が自明・委任範囲内なら、発見・登録・報告だけで止めることを禁止」)。PM_GOVERNANCE 11-8(Open Item運用5段階)。
- Fable受入判定(委任_05に対して): OPEN-487・OPEN-491とも §6 必須条件(X/Z正式経路配線・runtime evidence 保存entry変化0・replay 5,330対 最終judge変化0・TEST_MATRIX 181件不一致0・全回帰自分起因失敗0・SSOT・Git)を満たすと認め、**PRODUCTION_WIRED(X/Z)として受入**。副作用開示(`At 1030`↔`At 10:30`等の数字列↔H:MMが一次分類NG→X/Zはer109で救済、A/B/C Legacyは救済なし・保存corpus該当0・§27-3凍結)も受入範囲内と判断。OPEN-494は「修正へ進む」に分類されたまま未着手で返ってきたため、本委任で是正する(ユーザー指示: 登録・報告だけで止めない)。
- 並行agent(Family Y 委任_22、KP 委任_30)あり。対象コードは分離(er006/er021のみ触る)。SSOT編集は該当行を編集直前に再読して最小差分。commit前に`git status`でindex確認、`git commit --only -- <paths>`。`git add -A/-u/-f/-N`、amend/rebase/force push/stash/clean/reset --hard/checkout -f 禁止。telemetry等の追跡ファイル自動書換えは復元・stageしない(OPEN-490)。`py`でpytest(`.venv\Scripts\python.exe`が必要なscriptはそれを使う)。secret grep 0件。

## 1. OPEN-494 是正(数字2〜12+scale語のcanon `2 hundred` を er006 正規化が `2 100`/`2 105` にする)
- 委任_05の次委任案どおり: er006 `_convert_cardinal_words`で「直前の数字2〜12+scale語」を1つの数として読む1ブロック(flagなし、個別例外なし)。er021側に同型の取りこぼしがあれば同時に是正(各層1ブロック原則)。
- 影響分析gate(従来と同型、全て数値で記録): TEST_MATRIX追補(新規case、`2 hundred dollars`↔`200`/`two hundred`、`2 hundred and 5`↔`205`、`3 thousand 12`↔`3012`、境界: `2 100`(本当に2と100)等の誤統合がないこと、13以上・scale語なしは不変)期待不一致0 / replay 5,330対 最終judge PASS→NG・NG→PASS・value_guard・Tier1 変化0(Family別) / 全回帰(純base比較、`regress_wrap_06.py`の順序修正を踏襲)自分起因失敗0 / runtime evidence(X/Z正式Primary chain、保存entry変化0、合成variantで`NG_SECONDARY_UNAVAILABLE`解消を確認)。
- 記録: `IMPL_494_01.md`(原因・差分・gate表・副作用開示・撤去/残置)。

## 2. OPEN-492 決着(7桁以上の生数字列literal扱い→`1,000,000`↔`1000000`誤NG)
- 11-8の分類をやり直す: (a)literal扱いが意図された仕様か(電話番号・ID等の保護目的か)を CURRENT_SPEC/er021コメント/DECISION_LOGでGrep確認。(b)既存承認仕様の不具合で修正が自明(例: カンマ除去後の数字列同士の比較を桁数に関わらず同値とする、または7桁以上もnumber化するが前後の文脈で保護)なら、同じ影響分析gate付きで修正まで進める(1ブロック)。(c)仕様判断が必要(新仕様・判定範囲の拡張)なら、修正案・QCD影響・推奨を `OPEN492_ASSESSMENT_01.md` にまとめ、OPEN-492を「ユーザー判断要」に再分類する。(d)実害なしで対応不要と結論するなら根拠(保存corpus・ASR出力傾向)を数値で示す。報告だけで止めない。

## 3. SSOT
- `OPEN_ITEMS.md`: OPEN-487・OPEN-491を「FIXED_PENDING_FABLE→PRODUCTION_WIRED(X/Z、Fable受入 2026-10-24 委任_06)」に更新、OPEN-494は結果に応じCLOSED(FIXED)、OPEN-492は決着内容で更新。A/B/C Legacy非救済の開示を各項目に残す。
- `DECISION_LOG.md`: 487/491のFable受入、494是正、492決着を1〜3エントリで。`CURRENT_SPEC.md`: 487/491のStatus行をPRODUCTION_WIREDへ(他agentの未commit差分を巻き込まない。委任_05と同じく必要なら一時index経由)。
- 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_ASR-TIME-NUMERAL-EQUIVALENCE-01_委任_06.md`(Nは本委任文先頭「ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_06」を含むAgent呼出の0始まり通番、jsonl検索で特定し先頭行一致を確認)。
- commit(`--only`、本委任のファイルのみ)→`git push origin HEAD:main`。message「ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_06: …」。

## 4. 報告(`docs/pm/RESULT_PACKET_ATN6.md` に全文、handbackは要約)
494の原因・差分行数・gate表・副作用、492の分類結果と根拠(修正した場合はgate表)、SSOT更新箇所、commit hash、raw URL、Fable判定が必要な点(なければ「なし」)。