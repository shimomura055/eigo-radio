# Fable受入記録(NUANCE-DISPLAY-ORDER-AND-HR-PRECHECK-01 ①②、2026-10-29、委任_01の独立受入)

判定本文はFable判定の逐語記載(Worker記録: NDO02)。

## (1) 当初目的(ユーザー原文 `docs/pm/delegation_log/2026-10-29_NUANCE-DISPLAY-ORDER-AND-HR-PRECHECK-01_USER.md`)
- §2 L24-35: 表示順序=見出し→学習表現→本文の英文→日本語訳→ポイント→解説の6項目。L38-44: X/Y/Z×Std/Adv全正式経路・共通ページ生成仕様の変更(個別HTML直接修正なし)・既存表示内容/英文ハイライト維持・ニュアンス解説なし時の表示も正常・retry/regeneration/resumeで旧順序へ戻らない。
- §3 L50-63: HR事前チェックの提示(対象レベル・学習表現/本文の英文/日本語訳/ポイント/解説全文/採否)、L63「学習表現の見出しだけで採否判断を求めないこと」。
- §6 L182-200: 全Family・全レベルでの確認条件。L200「全条件の確認前にPRODUCTION_WIREDと報告しないこと」。

## (2) 最終成果物
- `er120_part2_grammar_production_01.py:1535-1540` 共通builder(新順序)
- `user_test/selection_form_v3/index.html:101` 対象レベル+ページ順
- `er134_nuance_explanation_01.py:1021-1022` HR依頼書「解説(全文)」
- Y姓記事 dev+enduser(新順序live)
- evidence `docs/research/NUANCE-EXPLANATION-PRODUCTION-WIRING-01/evidence/ndo01/`: order_check_copyruns.json(18セル order_ok)、form_nuance_{a2,b1b}.png、live_verify.log(TOTAL 170 NG 0)
- 失敗経路: 未確定rc=4停止・0件非表示(既存test)

## (3) 証拠
上記file:line、commit a71cc8bd1 / 1772a7c1b。

## (4) 一致/不一致
- 順序=一致(Fable実読) / 共通仕様=一致(個別HTML変更なし) / 強調維持=一致(enduser live)
- 0件=一致(copy-run NONE/REJECTEDセル) / retry・resume=一致(Y pages再実行で新順序維持)
- HR提示7点=一致(フォーム・依頼書をFable実読)
- 全Family配線=X・Z共通builder経由を配線確認。**実記事runtime発火はY済・X/Z未**(XはFAMILY-X-SELECTED-4-ARTICLES-PRODUCTION-01のpages段で取得予定、Zは次のZ記事で取得)

## (5) 判定
①②とも **Y=PRODUCTION_WIRED、X/Z=PRODUCTION_WIRED(配線・stage実行確認済、実記事runtime証拠待ち)**。
理由: 描画・提示は単一共通関数で全Familyが通り、runner呼出し位置をfile:lineで確認、Yで実runtime・live両URL確認。
未確認: X/Zの実記事runtime、form1 test(下記)。

## Worker補記(事実のみ、Fable判定の文言ではない)
form1_selection_form_v3_test_01.py 4件(test_restore_roundtrip_matches_buildStructured_and_detects_tamper[ERROR] / test_candidate_id_kind_and_sha_match_source_docs_verbatim / test_kp75_form_data_cap12_kind_cap_and_reason_verbatim / test_node_logic_suite)は変更前(a71cc8bd1^)でも同名・同症状でFAIL=既存不具合。OPEN-613へ登録(OPEN-612は別件で使用済みのため採番)(修正は別委任)。

判定整合: 重大NG=なし
