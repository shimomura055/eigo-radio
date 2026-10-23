FABLE-DELEGATION-MARKER: FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01-委任_02-STORY-REGISTRATION-DATA-ONLY-AND-FULL-PRODUCTION-RUN-20261023

# FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01 委任_02: 委任_01のblocker(作品が静的登録表に未登録)に対するFable判断を受け、**作品登録(data表への値追加のみ)を行ったうえで**、委任_01の全工程(T-0〜T-4)をそのまま実行する。委任_01の委任文 `docs/pm/delegation_log/2026-10-23_FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01_委任_01.md` は未保存のため、本委任のT-0で委任_01・委任_02の両方を逐語保存する(`py docs/pm/tools/extract_delegation_from_jsonl_01.py ...`、各MARKER一致。委任_01のMARKER=`FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01-委任_01-FULL-PRODUCTION-RUN-20261023`)。ユーザー原文は委任_01文の§9から `..._USER.md` へ逐語保存。

## 1. Fable判断(2026-10-23)
- 新作品ごとに `STORY_REGISTRY` 等のdata表へ登録するのは、『開いた窓』(FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01 委任_01)で確立した**承認済みの量産手順**(同一機構のstory_key別config、新しい検査方式ではない)。したがって**案1を承認**: 以下の**値の追加のみ**をProduction変更0原則の例外として許可する。ロジック・Prompt・閾値・Gate・flag・既存作品(melos/the_open_window)のentryには触れない。
  - `er026_family_z_fiction_production_runner_01.py` `STORY_REGISTRY`(e2e_management_id、theme_tag、pages_dir、タイトル、trial_seed_dir、rights_block[パブリックドメイン・出典URL]、speaker_config、voice_keywords)。`--story` choicesが固定定義なら、choicesをSTORY_REGISTRY導出にする最小変更ではなく、**値の追加1行**で対応(ロジック変更しない)。
  - `er062_family_z_structure_01.py` `STORY_VOICE_ROSTER`・`STORY_SPEAKER_CONFIG`・lint表(forbidden_names/spoiler語: 結末「警官=Jimmy Wells」「Bob=指名手配犯」を本文序盤で先回りしないための語。the_open_window と同形式)。
  - `er062_family_z_writer_01.py` `STORY_MAIN_CHARACTER`。
  - `er026_seeds/after_twenty_years/`(story.md、seed.json、SOURCE_PROVENANCE.json: 新規ファイル)。
  - test: `er026_family_z_story_registry_open_window_test_01.py` と同形式の `..._after_twenty_years_test_01.py` を追加(登録値の整合、既存2作品のtestは変更なしでPASS)。
- 量産性の所見として、「作品登録のSeed駆動化(data表の編集を不要にする一般化)」を**OPEN候補として記録のみ**(実装しない。ユーザー判断事項として報告に含める)。
- その他の前提・制約・禁止事項・上限(100円)・HR Lock/再起動/完成段1起動/TTS直列化/報告8項目は委任_01のとおり。

## 2. 実行
1. T-0(記録・予算、ACTIVE_TASK自行を `STORY_REGISTERED_PRODUCTION_RUN_IN_PROGRESS` へ)。
2. 作品登録(上記data追加)→登録test+既存story test+関連回帰(`er026`/`er062`系、`run_project_regression.py` のZ関連)をPASSさせ、`git diff --stat` で変更がdata表・seeds・新testのみであることを確認→この時点で一度 `git commit --only -- <path…>`(message: "Family Z『二十年後』作品登録(data表の値追加のみ、ロジック変更0)")→push。
3. 委任_01のT-1〜T-4を実行(正式Production run→試聴ページ→SSOT→Git→報告 `docs/pm/RESULT_PACKET_FZ20Y1.md` 上書き)。
4. 報告に「作品登録がdata追加のみであること(diff要約)」「Seed駆動化のOPEN候補」「追加開発の負担の実態(登録に要した時間・行数)」を含める(ユーザー最重要事項「追加開発の負担なく安定制作できるか」の検証結果として)。

## 3. 禁止
上記data追加以外のProduction code/Prompt/flag/閾値/golden変更。未承認仕様・DEV flag・Family Y仕様の導入。作品個別のLedger手動登録・個別例外。Gate/HR Lock/STOP迂回。`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・一時index。PIDは自分のもののみ。`TTS_EXECUTION_MODE=STANDARD`。上限100円無断超過。
## 4. handback
完了/HR Lock/予算警告/blocker のいずれかで。