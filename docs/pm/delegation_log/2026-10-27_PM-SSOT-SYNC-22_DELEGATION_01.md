## 管理ID

PM-SSOT-SYNC-22(SSOT同期。対象=GPG委任_05A(a1bb5fa71)・05B(c76784bef)、FORM委任_06(b8917f366)・07(b62a070cf/a87da3ab6)・07R(e75ff4853/9fd1b65b2)、YSP委任_08(53434b004)、SLOT-23-CONSUMER-DESIGN-01委任_01(c44853cec)、AI-ISLAND委任_02(11ffec634/703f2e5d3)、ユーザー正式決定USER_03(V3フォーム送信・コピー改善=APPROVED_FOR_PRODUCTION、AI島Std/Adv文法0件確定)。API 0)。あなたが唯一のSSOT編集権者(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/ACTIVE_TASK.md`/`docs/pm/PM_GOVERNANCE.md`違反記録節)。並行Agent: GPG委任_05(evidence、SSOT権なし)、AI-ISLAND委任_03、YSP委任_09(静的ページ)。全文読込禁止(管理ID/OPEN番号/節名Grep)。pathspec付きcommit。

## 性質/禁止

- 性質: 記録同期。Status格上げ禁止(VALIDATED/IMPLEMENTED/EVIDENCE/APPROVED_FOR_PRODUCTION/PRODUCTION_WIREDを混同しない。PRODUCTION_WIRED判定はFable受入後のみ。本SYNCでは**新たにWIREDと書かない**)。
- 禁止: 禁止Git操作、要約で承認範囲を広げること。
- 時間見込み: 約1h。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check(jsonl index=736付近から順に試し、先頭「## 管理ID」+「PM-SSOT-SYNC-22」一致を採用。NOT_FOUNDなら5分待ち再試行3回、不可なら要約再構成と明記)。T-2/T-3: なし。

## 実施事項

1. **ユーザー原文の逐語保存確認**: `docs/pm/delegation_log/2026-10-27_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_USER_03.md`(送信・コピー改善+AI島文法0件確定)が存在し逐語であることを確認(無ければFableへ報告、生成しない)。
2. **DECISION_LOG**(新規エントリ、既存形式に倣う): (a)V3フォーム送信・コピー改善 APPROVED_FOR_PRODUCTION(1操作でChatGPTへ、人間可読コピー正常代替、JSON/SHA/candidate_id分離+復元可能、受入条件12、6経路PRODUCTION_WIRED到達目標)、(b)AI島Std/Adv文法0件正式確定(全Family共通仕様=Top1/Top2・原則1件は不変)、(c)Fable採否=人間可読コピー+照合コード1行+送信常時コピー併用(URL 6000字内で`?q=`起動)、PREFACE簡素化、JSONは技術情報`<details>`残置、Opus不要(FORM6所見)。原文refを付ける。
3. **CURRENT_SPEC**: (a)フォームv3節(OPEN-545関連)に送信形式v3=人間可読+照合コード`AIF1-<stem>-<d6>-<c8>-<t8>-<s10>-<g10>-<m8>-<k4>`(`d6`=データJSONをLF正規化したsha256先頭6桁)、復元・照合tool`er128_form_readable_restore_01.py`/`confirm --from-readable`(fail-closed、rc=2)、Status=IMPLEMENTED+公開(ユーザー実操作確認待ち)。(b)文法新仕様節: 05A/05Bで全配線IMPLEMENTED(`PREGEN_MAX=2`/`GRAMMAR_MAX=1`、`all_candidates`撤去、凍結文法のmodel変更耐性=05B是正)、evidence=委任_05進行中。(c)Family Y Voice説明文の正式文言「Voice 1〜3は実在人物の発言をそのまま再現したものではなく、実際に投稿された意見をもとに、AIが編集・再構成したものです。」+適用条件(Theme Package全Voiceの`source_ids`非空、判定不能=非表示、Package不可読=STOP `FAMILY_Y_THEME_PACKAGE_MISSING_FOR_NOTICE`)+単一ソース`er121_family_y_structure_01.py PAGE_NOTICE_JA`、アプリ同一文言。(d)開発用Chunk境界マーカー仕様(X/Y/Z共通`audience=public|dev`既定public、実Chunk境界のみ・秒数なし、`check_page no_chunk_marker_in_public`、dev出力=別名`index_dev.html`/`player_dev.html`、旧ASRポーズ表示撤去)。文案は`docs/pm/RESULT_PACKET_YSP8.md`(6)・`RESULT_PACKET_FORM7.md`・`RESULT_PACKET_FORM7R.md`・`RESULT_PACKET_GPG5B.md`(7)を基に、既存節へ重複追記なしで。
4. **OPEN_ITEMS**: OPEN-545(送信改善IMPLEMENTED+公開、ユーザー実操作確認項目4点、残課題=データ終端`。=====`1件(AI島b1b文法Top1、見た目のみ・往復可)、コメント「なし」のみは復元拒否(fail-closed、フォーム側で空扱いにする小修正候補)、`rank/rank_label`非出力(実害なし))、OPEN-556(復元tool IMPLEMENTED)、OPEN-559(全配線IMPLEMENTED、GPG4既知不具合解消、evidence委任_05中)、OPEN-537(委任_08完了、`_03`凡例⏸1件残存→委任_09で撤去中、条件1〜7充足・条件8=Fable受入待ち、残置`pause_scan/pause_align/pause_stats`)、OPEN-543(既存失敗: `er121 StudyTextWiring test_two_items_adopted_in_standard`=旧2件仕様test→要更新、`R4HunkClassifier`差分更新要、`er119_isolation`3件、`er119_grammar_review_test` 2件)、OPEN-561(AI島: KP/KW確定済み・文法0件確定・制作中=委任_03)、**新規OPEN**(11-8分類=ユーザー判断要)「SLOT-23 区分②(Std)/③消費者=設計済み(DESIGN_01)・ユーザー確認Q1〜Q3待ち(Std②=A/B/C推奨B、ハイライト範囲、遡及)→Opus条件A→実装」。
5. **PM_GOVERNANCE 違反・逸脱記録節**: (a)FORM7 agentが`/tmp`共有の他Agentファイル`/tmp/patch1.py`を自分のpatchと誤認して2回実行(対象`export_form_data_01.py`再書込み、idempotent・差分なし見込み)→再発防止=scratchpad専用サブdir使用、(b)GPG5B agentの所有外編集(`er128_kp_confirmed_content_02b_test_01.py`のexpectedFailure解除=是正対象の実体のため合理、記録のみ)、(c)GPG5Bの委任文jsonl抽出NOT_FOUND→要約再構成、(d)SYNC-21の要約再構成の是正: `extract_delegation_from_jsonl_01.py`でindex 720〜740を再走査し、SYNC-21委任文が見つかれば逐語版へ差し替え(見つからなければその旨記録)。(e)GPG05Aの「branch push」疑義=05Bでorigin/main反映済みと確認(疑義解消)。
6. **ACTIVE_TASK.md**固定ヘッダ更新(管理ID=PM-SSOT-SYNC-22、Status、進行中=GPG05/AIF3/YSP9、次=フォーム改善報告/AI島第2報/6経路最終報告/SLOT-23ユーザー回答待ち、STOP条件、UDR-blocking=SLOT-23 Q1〜Q3・フォーム実操作確認・UDR-MONKEY-1、QDC=当日約¥40+AIF3/GPG5見込み)。
7. commit: `PM-SSOT-SYNC-22: USER_03決定(送信改善APPROVED/AI島文法0件)・GPG05A/05B・FORM06/07/07R・YSP08・SLOT-23設計・OPEN-545/556/559/537/543/561更新・新規OPEN(SLOT-23)・違反記録(API 0)`、`git push origin HEAD:main`。Secret grep 0件。

## 事前指定Grep一覧

`OPEN-545|OPEN-556|OPEN-559|OPEN-537|OPEN-543|OPEN-561`(OPEN_ITEMS.md)、`PM-SSOT-SYNC-21|KP-CONFIRMED-CONTENT-PROTECTION-01|GRAMMAR-PREGEN-ALL-LEVELS-01|selection_form_v3|PAGE_NOTICE_JA|Chunk境界`(CURRENT_SPEC.md/DECISION_LOG.md)、`違反・逸脱|11-8`(PM_GOVERNANCE.md)。追記位置=各既存行の末尾追記または直下行、新規OPENは最新番号+1。

## 報告

`docs/pm/RESULT_PACKET_SSOT22.md`(gitignore): (0)T-0、(1)変更箇所一覧(file:line)、(2)Status表(OPEN別)、(3)逐語再抽出の結果、(4)判断候補、(5)必須4行+「判定整合」、commit hash・raw URL。末尾5行要約。