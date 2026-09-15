# RESULT_PACKET: USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-SPEC-AUDIT

管理ID: USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-SPEC-AUDIT
種別: read-only調査+登録案作成(OPEN-154/OPEN-155)。API不使用、費用¥0。
詳細: `docs/pm/spec_traceability_audit_03.md`

## 1) OPEN-154(B1 Preview長さ仕様)
- 実績: 旧67語/4文→Trial 38語/2文→Production wiring runtime evidence
  46語/2文(`ER-011-PREVIEW-ROLE-AND-NUMERIC-PRECISION-PRINCIPLE-PRODUCTION-
  WIRING-01`、2026-09-07)。
- 現Prompt(`er003_v1_b1_scaffold_01_generate.py::PREVIEW_ROLE`、B-Family
  共有): 「2〜3文程度」の文数soft guidanceのみ、語数・字数目安なし。
  A2側は80〜110字目安+150字上限を維持(非対称)。
- CURRENT_SPEC 847行は「hard word-count gateなし」を正式記録済み(反映漏れ
  ではなく仕様の選択)。ただしB1/A2非対称自体はOpen Item化されていなかった。
- Voices 2V v2 Preview実測(本タスクで手動カウント): 3文・65語
  (`er014_output/.../b1_2v_v2/comment_fact_safety_evidence.json` 18行)。
- 登録行案・個別例外記録文案とも作成済み(1.5/1.6節)。40/45/50語等は
  「決定」として提示していない(実績値の列挙のみ)。

## 2) OPEN-155(User Decision→Formal Spec反映漏れ)
- 限定監査5領域(Preview length/Family C/Voices 2V-3V/Discovery S2/
  Audio-TTS)を表形式で整理(spec_traceability_audit_03.md 2.1節)。
- 明確な途切れ実例: Discovery A2/S2のlength soft target定数が生成経路に
  未配線、Open Item番号も未採番のまま(DECISION_LOG 7424-7429行、
  PM-CLOSEOUT-CONSOLIDATION-134で言及のみ)。B1 Preview非対称も同様に
  未登録だった(本タスクでOPEN-154として初起票案作成)。
- 反例(模範例): Discovery/News共通のPoint-only regeneration除外は
  仕様→Production→SSOT→Open Item closeout(OPEN-88 CLOSE)まで完走済み。
- 未確認(推測で「反映済み」と書いていない): Family CがCURRENT_SPEC未掲載
  なのはTrial段階ゆえか単純な反映漏れかは断定せず。Voices Key Phrase音声の
  CURRENT_SPEC記載有無も事前指定Grep範囲では確認不能。
- 再発防止案5件(2.5節)を候補整理。うち4件(Decision ID必須化/Closeout
  Mandatory Check追加/Trial REPORT必須記載/Dangling Reference逆方向版)は
  新しい強制Gateに該当するため**案の提示のみでSTOP**(実装しない)。
  1件(未配線一覧の自動集計ツール)は集計部分自体は新Gate非該当だが、
  Closeoutの必須確認事項へ組み込む場合はGate該当としてSTOP対象と明記。

## 3) DECISION_LOG追記案
- spec_traceability_audit_03.md 3節に草案あり(統合タスクが転記・反映)。

## 4) commit対象候補
- `docs/pm/spec_traceability_audit_03.md`(新規)
- `docs/pm/RESULT_PACKET_FU03_SPEC_AUDIT.md`(新規)
- `docs/pm/delegation_log/USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-SPEC-AUDIT.md`(新規)
- `docs/pm/delegation_log/USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-SPEC-AUDIT_check.json`(新規)
- SSOT本体(CURRENT_SPEC.md/DECISION_LOG.md/OPEN_ITEMS.md)は本タスクで
  未編集、commit対象に含めない。

## 5) T-0・事前指定外Read・STOP有無
- T-0: PASS(reasons: none、`_check.json`保存済み)。
- 事前指定外Read: (i) `er003_v1_b1_scaffold_01_generate.py`(PREVIEW_ROLE
  の実定義本体、B-Familyが`b1s`として参照する先。事前指定の
  `er003_v1_n3_01_scaffold_generate.py`にはPREVIEW_ROLE定義自体がなく
  import元を追う必要があった)。(ii) `er012_b_family_production_runner_01.py`
  冒頭のimport文(`b1s`のalias先特定のため)。(iii) `OPEN_ITEMS.md`該当行
  抽出をReadでなくBash sed/grepへ切替(Read toolがoffset/limit指定でも
  ファイル総トークン数超過エラーを返したため)。(iv) `CURRENT_SPEC.md`での
  "Family C"全文grep(0件を確認するため、事前指定Grep一覧の範囲内で
  Family C該当行が見つからなかったことの裏付け)。
- STOP: 新Gate提案4件(2.5節の1/3/4/5)は**案の提示のみ**、実装・
  PM_GOVERNANCE編集はしていない。SSOT編集・コード変更・Prompt変更・
  Voices v2 Preview再生成もいずれも実施していない(禁止事項遵守)。
