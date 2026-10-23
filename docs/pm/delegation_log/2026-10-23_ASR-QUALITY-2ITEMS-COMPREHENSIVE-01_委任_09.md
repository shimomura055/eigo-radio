FABLE-DELEGATION-MARKER: ASR-QUALITY-2ITEMS-COMPREHENSIVE-01-委任_09-FABLE-FINAL-ACCEPTANCE-RECORD-20261023

# 記録のみ(API 0・コード変更0)。ASR①②のFable最終判定をSSOTへ反映し、Git。

## 0. 読むもの
`docs/pm/ACTIVE_TASK.md`(line 2 Git注意、ASR行)、`docs/pm/RESULT_PACKET_ASRQ_B8.md`、`OPEN_ITEMS.md`のOPEN-471/472/479/465/480行(Grepで該当行のみ)、`docs/pm/USER_DECISION_REGISTER_01.md`のUDR #157/#168。

## 1. Fable最終判定(2026-10-23、逐語で反映)
- **②英米綴り(UKUS、OPEN-471)**: X=PRODUCTION_WIRED(Fable受入、正式TTS段関数の実run発火)/**Z=PRODUCTION_WIRED(Fable受入、正式CLI実run `full_story_part3_c12` speciality/specialty attempt1 PASS、`ukus_spelling_variant`、pron_differs=true、完成版に反映)**。受入条件1〜9充足。残リスク: pron_differs対の実際の読みはユーザー試聴で確認。Status→`PRODUCTION_WIRED(X/Z)`。
- **①固有名詞(RET、OPEN-472)**: X=PRODUCTION_WIRED(Fable受入)/**Z=PRODUCTION_WIRED(Fable受入、開示付き)**: 根拠=正式Z実runでRET構築hook発火(NER 2call、`audit/entity_table.json`、Bertie/Framton/Vera=person/confirmed、再開時NER 0、operator報告別欄)+正式`run_tts_stage`経由の隔離run(Ledger空)でENTITY_ONLY_ACCEPT(`entity_table:confirmed:person`、HR 0)+会話経路はOPEN-479修正で役割解決(case B FULL_STORY PASS、test 11件、replay不変、B/C不変)。開示: 実runの会話clip(c14)はTier3(Azure corroborate)が先に受理したためPNAP/RETの受理寄与は未観測。次回のZ作品・X記事(CLI入口)で自然発火を追認する(OPEN-472は`PRODUCTION_WIRED(X/Z)・追認待ち項目1件`として残す)。
- **OPEN-479**: CLOSED(Fable確認: X/Z scope限定修正、実run c14 a2/b1b attempt1受理、test 11 PASS、replay before/after一致、B/C golden不変)。
- **OPEN-480**(運用事故): CLOSED(再発防止反映済み)。
- 『開いた窓』(OPEN-465): 完成版提出済み・ユーザー最終試聴待ち(確認点3つ: Adv c12 speciality の英式/米式、part3_c2 Bertie、part1_c14 Bertie Std/Adv)。変更なしなら触らない。

## 2. 更新
- OPEN_ITEMS.md: OPEN-471/472/479/480 のStatusと1行要約を上記どおり更新(履歴は残す)。
- DECISION_LOG.md: Fable最終判定1エントリ(①②X/Z PRODUCTION_WIRED、開示事項、OPEN-479/480 CLOSED)。
- CURRENT_SPEC.md: ①②の該当参照行に「PRODUCTION_WIRED(X/Z、Fable受入2026-10-23)」が未記載なら1〜2行で追記(全文読込禁止、Grepで該当行のみ)。
- UDR #168: 状態を「採用→配線完了(X/Z PRODUCTION_WIRED、Fable受入2026-10-23)」に更新。
- ACTIVE_TASK ASR行: Status=`CLOSED_PRODUCTION_WIRED_XZ(①②)/OPEN_WINDOW_USER_LISTENING_PENDING`。
- 委任文逐語保存 `docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_委任_09.md`(抽出toolが無ければ手で逐語保存し末尾に注記)。
- Git: secret scan(`Glob **/secret_scan*`、無ければcached差分のkey/tokenパターンGrep 0件)→`git diff --cached --name-status`(他agentのstaged変更を巻き込まない)→`git commit --only -- <path…>`→`git push origin HEAD:main`。
## 3. 禁止
Production/テストコード変更0。`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・一時index禁止。他agentの行(ACTIVE_TASK)を編集しない。完了したらcommit hash・更新pathのみ報告。

(注記: 抽出toolが無いため手で逐語保存。)
