# 委任_03c: AUW — beta 9 idへ選択肢A適用→gamma確認→commit/push(branch)+事故記録
(sandwich-pm -> sonnet-worker 委任文の要約保存。2026-10-15)
管理ID: ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 / 委任_03c。branch feat/auw-unified-asr-01。禁止: git add -A/-f/stash/reset --hard/checkout -f/clean/rebase/amend/force push、mainへのpush/merge。有料API呼出0厳守(外部呼出関数は全てmock)。

## Fable判断
beta 9 id(論理5件)は選択肢A採用。旧期待(内容語差ではSecondary不呼出→verified False)はユーザー原文L54「Primary NGなら、不一致の種類によらず原則Secondaryを実行する」L55「Primary NG・Secondary PASSならPASS_WITH_WARNINGとして採用する」と矛盾し、承認済みフローへの追随。L97(重大内容差)は値ガード/否定ゲートで別途担保。Bは新ガード=未承認仕様追加のため不採用。layer単位の判定(Tier1/CS gate・role gate・MIXED)は不変(DESIGN_01:65)。

## やること
1. patch_03b/*_PROPOSED.py を元test 3ファイルへ適用(コメント付与、安全側assert維持)。
2. 9系統96ファイルをrun_tests_per_file.pyで再実行→patch_03b/test_post_03c.json。
3. IMPLEMENTATION_03.md 見出し改番(§9)、§9-2 beta A根拠、§9-3 事故記録(03bで未mock testから_resolve_unresolved_entity_for_review経由Perplexity sonarへ最大2回実request、実額はログGrepで確認)、再発防止mock化(ファイル:行)。
4. 明示addのみでcommit/push(secret_scan --staged hits=0)。
5. commit後gamma 4件(er019 FamilyAUnchanged/er020x2/er064)再実行。
6. §9-4 委任_06向けメモ(Melos said 26/27・M1 20/21、「Melos said. 12/12」構成は実音声runtime evidence必須)。

## 報告様式
受入記録5項目(当初目的L39-60・L97・L112-117逐語/成果物/証拠/一致不一致/判定)+逸脱・委任_04注意点・費用。
