# NUANCE-CORNER-ABOLITION-01 委任_02 EVIDENCE_01(2026-10-30、API 0)

## 1. 撤去の範囲と恒久方式
- 恒久撤去(flag無し)。runner(X=er019/Y=er121/Z=er026)のN1呼出・finalize・nuance見積・page検査、er120の表示/期待値、HR(exporter/V3フォーム/form_logic.js/er128/er119)、End User adapter/verifyから撤去。
- 残置: 構造ガード`count_nuance_blocks`/`verify_no_nuance_in_section`(`<h3>ニュアンス解説</h3>`見出しの構造一致のみ。部分文字列一致でSTOPしない)。旧データ・`confirmed_nuance.json`・`rec["nuance"]`は読まない・削除しない。
- 旧フォーム形式(schema_minor=2 / selection.nuance / AIF2)は`NUANCE_CORNER_ABOLISHED`で明示拒否(er128 cmd_from_form/readable_restore、form_logic.js validateIndex)。
- 触っていない(M2): `enduser_page_assets/rev01-e/*`、DEV `dev_enduser_page_01`、公開済みスナップショット(Y姓以外)。

## 2. test結果
- 変更したtest 15ファイル(pytest): 554 passed / 9 failed。9件の内訳: Step B(er134撤去)後に解消=5(er119_isolation, er120 P3, er136 Dangling, er119_grammar_review static 1)、
  baseline(HEAD worktree)でも同一失敗=er003 ZPart1 2件・er119_grammar_review `test_public_builder_and_standard_never_call_part2`(事前から失敗)、
  単独実行で合格=er121 2件(全体実行時のみ失敗、事前失敗リスト外・原因は並行agentのgit/ファイル状態と推定、要追跡ではない)。
  `er119_output/`が未追跡で存在(2026-10-25作成、本タスク以前)→`er119_grammar_review_test_01::test_grammar_files_not_tracked_dirs`は私の変更と無関係。
- Step B後の再実行(er136, er119_isolation, er120 grammar, er121 runner, er009 pricing, er053, er054): 203 passed / 1 failed。失敗1件=`er054...::test_production_keys_unchanged`はbaselineでも失敗(事前不具合・FAMILY_Y_*キー追加が閉集合testに未反映)。
- 新設`er136_nuance_abolition_test_01.py`(18 test): Dangling(旧識別子0、er134 import 0、廃止API面の消滅、DEPRECATED 2 processの呼出元0)/旧ファイル非読込/フォーム・payload明示拒否/form_logic.js/M6(旧summary・nuance_cand_*・rec["nuance"]・`--regenerate-stage nuance_cand_*`の明示エラー)。

## 3. copy-run(API 0)
- X moon_shrinking(spec有/無の2 copy): pages+page_verify PASS、player byte一致、ニュアンス見出し0。
- Y surname copy(`run_nca02_y`): 想定差分のみ(後述M5と同一)。
- Z in_a_grove(`--pages-dir`明示のcopy 2本zn2/zs2): rc=0、TOTAL 170 NG 0、両pagesはrun名正規化後sha256一致(851805af...)、ニュアンス見出し0、追跡済み`user_test/family_z_in_a_grove_01`は無変更。
- **事故の開示**: 初回のZ in_a_grove copy-runで`--pages-dir`を指定せず、追跡済み公開物`user_test/family_z_in_a_grove_01/{index.html,enduser/build_info.json,enduser/data/article.json}`を上書き。`git checkout --`で3ファイルを復元しcleanを確認(公開済みと同一)。以降は全copy-runで`--pages-dir`明示。

## 4. Y姓 実run(`--stages pages,page_verify`、spent_jpy=55.2(累計表示。今回の新規API 0))
- 差分(M5): HTMLトークン単位で差分3箇所のみ = ニュアンス解説2ブロック(Std「at least a little」/Adv「at least」)削除 + 重複アラーム導入文(「ニュアンス解説の間に」→「Key Phrase・Key Word等の間に」)。見出し数 2→0。
- 音声: 52ファイル全sha256一致。本文・訳文は不変。
- 公開: `index.html`をpublic dirへcopy、`er135_enduser_page_01.py produce --family y --dev-dir user_test/family_y_production_surname_choice_01`(idをdir名に揃えるため。pages経由のpublish-copyだとid="pages"になるためやり直し)。article.jsonの差分=`nuance`2配列の削除のみ(追加行なし)、build_infoはsha/asr時間のみ。
- 公開5記事のverify-consistency: 5/5 `ok: true`(X moon_shrinking_reselect_01 / Y fee_03 / Y surname / Z in_a_grove / Z melos_kphr_evidence_r3)。X/Z/Y fee_03の公開物は無変更。

## 5. X 4記事のHRフォーム(M3)
- 再出力8ファイル(+Yuki-Onna a2 1)。旧データとの比較(ニュアンスキーのみ除外): 全9ファイルでequal=True(candidates_sha256・grammar_sha・提示順は不変)。新データのnuanceキー=0。
- ユーザー提示物=`docs/research/FAMILY-X-SELECTED-4-ARTICLES-PRODUCTION-01/HR_REQUEST_02.md`(旧HR_REQUEST_01と旧フォームdataは無効)。Yuki: `docs/research/FAMILY-Z-YUKI-ONNA-PRODUCTION-01/HR_REQUEST_02.md`、run_yo_prod_01/review_request.md再生成(ニュアンス節なし)。

## 6. 削減量
- 費用: ニュアンスLLM(候補生成+重複判定)=1レベルあたり2 call・約0.22円 → 0(2レベル=記事セットあたり約0.45円、70円目標の約0.6%)。
- HR項目: 1レベルあたりニュアンス選定(採用/不採用+重複確認)1件 → 0。照合コードAIF2・nuanceサブコマンド4件(show/select/issue-spec/state) → 0。
- LLM call: 4 call/記事セット → 0。
- code: Step A = +631 / -1,302行(46ファイル、新設test 18件を含む)、Step B = +13 / -3,799行(er134本体1,177行+専用test 6本)。
- test: 専用6ファイル撤去、混在test 15ファイルのnuance assertを削除/修正、新設1ファイル。
