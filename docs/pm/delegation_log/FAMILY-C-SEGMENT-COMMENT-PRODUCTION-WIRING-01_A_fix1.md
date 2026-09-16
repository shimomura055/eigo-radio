## 管理ID

`FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-AND-USER-TEST-INVENTORY-01`(委任A 差し戻し1回目: Family C Production runnerの初回生成本体・retry/regeneration/resume経路の実装+Gate再判定+SSOT是正+監査報告commit)
並行タスクなし(委任A初回=commit `a04c9221`/`0156ceea`、委任B=read-only完了、いずれも終了)。報告は`docs/pm/RESULT_PACKET_WIRING_FAMILY_C.md`末尾に「## 差し戻し1回目」節を追記。`docs/pm/ACTIVE_TASK.md`は本タスクで上書き。

## 性質/到達上限Status/禁止事項

- 性質: **Fable受入照合の結果、初回委任の`PRODUCTION_WIRED`判定を差し戻す。** 理由: `er013_family_c_production_runner_01.py`は`--plan-only`と`--comments-only --no-tts`のみを実装し(同ファイル213-236行、「実TTSを伴う全体生成経路は…未実装」と自記)、Family C episodeの初回生成本体(Story/Support TTS→ASR整合→Assembly→Audio Validation Gate→player→web_delivery)・TTS retry/fallback cascade・segment単位regeneration・resume(.ok reuse)がProduction経路に存在しない。したがってユーザー完了判定「1. Production正式初回path実装」「2. retry/fallback/regeneration整合」が未充足であり、Family C episodeを実際に生成できる経路は依然Trial script(`er013_family_c_episode_trial_1[012]_*`)のみ=「Trial-11/12専用scriptにしか存在しない状態」が解消されていない。現時点の正しいStatusは`APPROVED_FOR_PRODUCTION / WIRING_INCOMPLETE`。
- 本差し戻しの目標: runnerに全体生成経路を実装し、最小限のruntime evidenceで実発火を示し、完了判定12項目を再判定する。全項目充足なら`PRODUCTION_WIRED`、不足があれば`APPROVED_FOR_PRODUCTION / WIRING_INCOMPLETE`+不足列挙(自己宣言せず証跡で示す)。
- 禁止: Trial scriptのimport(module/runnerとも0件維持)、既存承認episode(Trial-09 v2/b1・Trial-11・Trial-12成果物)の上書き・再TTS、runtime evidence目的での全音声再生成、B1 CommentへのA2 Contract適用、Family A/Bへの横展開、hard cap Validator化、Opus、新規仕様決定(承認済み仕様の配置のみ)、`git add -A`/`stash`/`amend`、wavのcommit。
- 費用上限: ¥15(runtime evidence用の新規TTS 1〜2 segment+ASR。それ以外はbyte-identical reuse)。
- STOP条件: 全体生成経路の実装に未承認の新仕様決定が必要/既存Production関数(er003/er012共通)との重大な衝突/費用上限超過。該当時は`WIRING_INCOMPLETE`のまま不足と選択肢を報告して停止。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
(保存名: `docs/pm/delegation_log/FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-01_A_fix1.md`)

## ユーザー指示(原文)

ユーザー原文(2026-09-16)の該当部分:
---
2-A. Story segmentation: 確認・実装対象: Family C Production正式初回生成経路/A2 / B1双方/Story segment生成/retry/regeneration/fallback/resume / reuse時/Comment挿入境界との整合/Voice assignmentとの整合。Trial-11 / Trial-12専用scriptにしか存在しない状態を禁止する。Trial scriptをProductionコードが暗黙参照する構造にもしてはならない。
2-B. A2 Comment理解ガイド型: 初回生成だけでなく、retry/regeneration/fallbackでも同じ思想が維持されること。B1 Commentへ誤適用しないこと。
4. Production runtime evidence: 実際のFamily C Production正式pathでruntime発火を確認すること。(中略)既存完成episodeを壊す必要はない。無駄な全音声再生成は避ける。必要最小限のProduction runtime evidenceを取得すること。
9. Production Wiring完了判定: 以下すべて満たした場合のみPRODUCTION_WIREDとする。Production正式初回path実装/retry / fallback / regeneration整合/Trial専用script依存なし/runtime evidenceあり/Regression / integration PASS/actual model / routing等必要証跡あり/CURRENT_SPEC更新/DECISION_LOG更新/OPEN_ITEMS更新/Dangling Referenceなし/Git commit / push確認/ユーザー承認内容とProduction挙動一致。1件でも未確認なら、APPROVED_FOR_PRODUCTION / WIRING_INCOMPLETEとして不足項目を明示する。
---

## 事前指定Read一覧

- `er013_family_c_production_runner_01.py`: 全文(自作、213-236行の未実装明記を含む。構造変更のため全文Read許可)
- `er013_family_c_production_01.py`: Grepで`^def |^[A-Z_]+ = `→関数・定数一覧(既存API把握、必要箇所のみ範囲Read)
- `er013_family_c_episode_trial_12_twins_b1_run.py`: Grepで`def stage_|def run_|def main|tts_narrator|tts_device|tts_support_charon|tts_brother|generate_voice_body_wide_margin|generate_charon_english|asr_diag|_load_prior_seg_asr_cache|def assemble|build_b1_timeline|verify_episode_audio_validation_gate|write_player|web_delivery|\.ok|--only-segments|cascade|fallback`→各stage(TTS/ASR/Assembly/Gate/player/resume/regeneration)の実装範囲Read。**移植元として参照するがimportしない**(ロジックをmodule/runnerへ写し、Trial固有設定は`article_config.json`へ)。
- `er013_family_c_episode_trial_12_twins_run.py`(A2側): Grepで同上+`japanese_title|preview_ja|comment_.*_ja|build_a2_timeline|generate_a2_japanese`→A2 stage範囲Read。
- 既存Production共通関数の所在確認(編集しない): `er003_v1_n3_01_assemble.py`(Grep`def verify_episode_audio_validation_gate|def build_a2_timeline|def build_b1_timeline`)、`er003_v1_n3_01_tts_generate.py`/`er003_v1_crosslevel_audio_02_common.py`(Grep`def generate_english_segment_with_fallback|def generate_a2_segment_with_slowdown`)、`er012_b_family_voices_production_01.py`(Grep`def generate_voice_body_wide_margin`)、`er003_v1_sing01_voice01_generate.py`(Grep`def generate_charon_english`)、`er003_v1_iran01_a2_generate.py`(Grep`def run_support_text|PREVIEW_ROLE`)、`er003_v1_b1_scaffold_01_generate.py`(Grep`def run_support_text|PREVIEW_ROLE|COMMENT_1_ROLE`)。
- `er013_output/family_c_episode_trial_11/memory_a2/`: Glob`**/*.ok`・`audit/tts_generation_results.json`(Grep`"path"`)→承認済みwavの所在・.okマーカー形式(resume evidence用にコピーする対象)。
- `CURRENT_SPEC.md`: Grepで`Family C`→初回委任で新設した節(見出し文字列を実測で特定)の範囲Read(Status欄是正対象)。
- `DECISION_LOG.md`: Grepで`^## FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-AND-USER-TEST-INVENTORY-01`→エントリ範囲Read(Gate判定行の是正対象)。
- `OPEN_ITEMS.md`: python抽出でOPEN-147/157/158行の末尾追記部(`PRODUCTION_WIRED`記載箇所)を特定。
- `docs/pm/RESULT_PACKET_UT_INVENTORY.md`: 1-10行(委任B成果、commit対象の存在確認のみ)。

## 事前指定Grep一覧+追記位置・更新位置の手順

1. **runner全体生成経路の実装**(`er013_family_c_production_runner_01.py`、既定モード=全体生成): stage順=`plan`(既存`build_plan_for_level`)→`assets`(article_configの`reuse_from`ディレクトリ指定があれば非Story共通asset[Intro/Outro/SFX/Notification/topic_intro/日本語タイトル/Preview/Key Phrase/B1 Support]を`.ok`付きでコピー、無ければ既存Production関数で生成)→`tts_story`(planの各segmentをvoice_mapに従い既存Production TTS関数[narrator/人物/装置=`generate_voice_body_wide_margin`または`generate_charon_english`等、A2 slowdownは既存関数]で生成。`.ok`が存在しwav sha256がplanの`tts_text`と対応するsegmentはskip=resume。既存cascade[標準2+fallback1]をそのまま使用=retry/fallback)→`asr_consistency`(現物wavでASR、名前キャッシュは**音声sha256一致時のみ**再利用[Trial scriptの名前のみキャッシュを踏襲しない、承認済み方針: 再生成segmentは必ず現物ASR])→`comments`(A2: `generate_family_c_a2_comment`[理解ガイド型Contract、内蔵retry]→TTS[Aoede日本語]。B1: 既存B1 Support経路`er003_v1_b1_scaffold_01_generate`のPreview/Comment role+Charon voice。A2 Contractへの分岐はlevel=="a2"のみ、`guard_a2_only`維持)→`assemble`(既存`build_a2_timeline`/`build_b1_timeline`相当をFamily C構成[Comment 4なし、B1日本語タイトルなし]で呼ぶ。Trial-12と同じpause値はarticle_configまたはmodule定数)→`gate`(既存`verify_episode_audio_validation_gate`)→`player`+`web_delivery.json`。引数: `--only-segments <ids>`(regeneration: 指定segmentのwav/.okのみ削除して再TTS→現物ASR→再Assembly)、`--resume`(既定True)、`--plan-only`/`--comments-only --no-tts`(既存維持)、`--budget-jpy`。既存Trial scriptはimportしない(Grep 0件維持)。
2. **runtime evidence(最小費用)**: Memory A2で`article_config.json`の`reuse_from`=`er013_output/family_c_episode_trial_11/memory_a2`を指定し、承認済みwav(Story 10 segment+Comment 3件+非Story asset)を`.ok`付きでコピーした状態から全体生成をresumeモードで実行→TTS stageが**全segment skip(resume発火の証跡)**→ASR consistencyはsha256一致でキャッシュ再利用→Assembly→Gate→player→web_delivery.jsonが`er013_output/family_c_production/memory/a2/`に生成されること(¥0)。生成episode mp3のsha256または長さが承認済みTrial-11 episode(316.569秒)と一致することを報告。続けて`--only-segments story_002`(装置2語segment、最小コスト)でregeneration経路を実行→当該1 segmentのみ再TTS(cascade経由)・現物ASR・再Assembly・Gate再PASSを確認(¥1.5前後)。これで初回path(resume)・regeneration・retry/fallback(cascade関数呼び出しのログ)・Gate・playerの実発火を示す。生成物は`family_c_production/`配下のevidenceであり、ユーザー実検証用playerには載せない(RESULT_PACKETに明記)。B1は`--plan-only`済み+同一stage関数を共有するため、B1側は`--comments-only`相当のdry-run(B1 Support経路がA2 Contractを呼ばないログ)で担保(TTSなし)。
3. **テスト追加**(`er013_family_c_production_test_01.py`): resume skip判定(sha256一致でskip/不一致で再生成)、`--only-segments`が指定segmentのみ削除、ASRキャッシュがsha256不一致時に再利用されない、B1経路がA2 Contractを呼ばない(モック)、TTS stageが既存cascade関数を呼ぶ(モック)、Assembly構成にComment 4/B1日本語タイトルが含まれない。既存306件+新規で回帰。
4. **SSOT是正**: 初回委任で`PRODUCTION_WIRED`と記載した箇所(CURRENT_SPEC Family C節Status欄、DECISION_LOGエントリのGate判定行、OPEN-147/157/158追記文)を、本差し戻しの再判定結果に合わせて修正。再判定が`PRODUCTION_WIRED`なら「初回委任時点では初回生成本体未実装のため`WIRING_INCOMPLETE`、差し戻し1回目で全体生成経路実装+runtime evidence取得により`PRODUCTION_WIRED`(2026-09-16)」と経緯を残す。`WIRING_INCOMPLETE`のままなら`APPROVED_FOR_PRODUCTION / WIRING_INCOMPLETE(不足: …)`へ書き換える。履歴の書き換えではなく追記・訂正として記録。
5. **監査報告commit**: 委任B成果物`docs/pm/RESULT_PACKET_UT_INVENTORY.md`・`USER-TEST-INVENTORY-01_REPORT.md`・`docs/pm/delegation_log/FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-01_B_inventory.md`・同`_check.json`を本タスクのcommitに含める(内容は編集しない。ただしFable判断として`USER-TEST-INVENTORY-01_REPORT.md`末尾に「Fable注記(2026-09-16): Memory B1/Digital Twins A2/B1はユーザー正式決定(FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-01 項目0)により試聴OK=USER_LISTENING_DONE。監査時点のDECISION_LOG本文は反映前だった」を1段落追記)。DECISION_LOGの委任Aエントリにも「Memory B1/Twins A2/B1ユーザー試聴OK(2026-09-16)」が記録済みであることを確認(未記録なら追記)。
6. `docs/pm/ACTIVE_TASK.md`固定ヘッダ更新(APPROVED未配線欄にFamily C 2仕様の最終Status)。

## 実行コマンド全文

作業ディレクトリ`C:\Users\tensh\eigo-radio`、pythonは`.venv\Scripts\python.exe`。

T-0:
```
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-01_A_fix1.md --json-out docs\pm\delegation_log\FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-01_A_fix1_check.json
```

runtime evidence(Memory A2、resume全体生成、TTS skip期待、¥0):
```
.venv\Scripts\python.exe er013_family_c_production_runner_01.py --config er013_output\family_c_production\memory\article_config.json --level a2 --resume --budget-jpy 5
```
regeneration経路(1 segmentのみ、¥1.5前後):
```
.venv\Scripts\python.exe er013_family_c_production_runner_01.py --config er013_output\family_c_production\memory\article_config.json --level a2 --only-segments story_002 --budget-jpy 5
```
B1経路dry-run(A2 Contract非呼び出しの確認、TTSなし):
```
.venv\Scripts\python.exe er013_family_c_production_runner_01.py --config er013_output\family_c_production\memory\article_config.json --level b1 --plan-only
```
Trial script非依存確認:
```
.venv\Scripts\python.exe -c "import re;[print(f, len(re.findall(r'import\s+er013_family_c_episode_trial|from\s+er013_family_c_episode_trial', open(f,encoding='utf-8').read()))) for f in ['er013_family_c_production_01.py','er013_family_c_production_runner_01.py']]"
```
回帰:
```
.venv\Scripts\python.exe run_project_regression.py --pattern "er013*_test_*.py"
```
承認済み成果物無変更確認: `git status --porcelain er013_output/family_c_episode_trial_09/ er013_output/family_c_episode_trial_10/ er013_output/family_c_episode_trial_11/ er013_output/family_c_episode_trial_12/`が空。
Dangling Reference Check: 初回委任の表を再実行し、新規関数(stage関数・`--only-segments`)を追加した表を報告。

## SSOT追記文

`DECISION_LOG.md`(委任Aエントリ末尾に追記):
```
- 2026-09-16 Fable差し戻し1回目: 初回委任のrunnerは`--plan-only`/`--comments-only`のみで初回生成本体(TTS→Assembly→Gate→player)・regeneration・resume経路が未実装だったため、Fable受入照合で`PRODUCTION_WIRED`判定を差し戻し(`APPROVED_FOR_PRODUCTION / WIRING_INCOMPLETE`)。差し戻し1回目で全体生成経路(<stage一覧>)・`--only-segments`regeneration・sha256ベースresume/ASRキャッシュを実装。runtime evidence: Memory A2 resume全体生成(TTS skip <n>/<n>、episode <秒>=Trial-11一致、Gate PASS、¥0)+`--only-segments story_002`regeneration(cascade経由再TTS・現物ASR・Gate再PASS、¥<実測>)+B1経路A2 Contract非呼び出し確認。テスト<n>件PASS。再判定: **<PRODUCTION_WIRED / APPROVED_FOR_PRODUCTION / WIRING_INCOMPLETE(不足: …)>**。commit <hash>。
- 監査(委任B)成果物`USER-TEST-INVENTORY-01_REPORT.md`をcommit(Fable注記: Family C 3 episodeはユーザー正式決定により試聴OK)。
```
`CURRENT_SPEC.md`Family C節Status欄・`OPEN_ITEMS.md`OPEN-147/157/158追記文: 再判定結果に合わせて訂正(Grep 4のとおり)。
`docs/pm/ACTIVE_TASK.md`: 固定ヘッダ形式で上書き。

## Git(明示add対象・コミットメッセージ・trailer)

- 明示add対象(wav除外、mp3可): `er013_family_c_production_01.py`、`er013_family_c_production_runner_01.py`、`er013_family_c_production_test_01.py`、`er013_output/family_c_production/**`(article_config.json・evidence/*.json・memory/a2/配下のsegments.json/audit/*.json/player.html/web/*.mp3/web_delivery.json。evidence用episode mp3はcommit可だが、RESULT_PACKETで「evidence専用、ユーザー実検証候補ではない」と明記)、`CURRENT_SPEC.md`、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/RESULT_PACKET_WIRING_FAMILY_C.md`、`docs/pm/RESULT_PACKET_UT_INVENTORY.md`、`USER-TEST-INVENTORY-01_REPORT.md`、`docs/pm/delegation_log/FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-01_A_fix1.md`、同`_check.json`、`docs/pm/delegation_log/FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-01_B_inventory.md`、同`_check.json`。
- `er013_output/family_c_episode_trial_*/`・`er006_output/`・`er011_output/`の既存M、`docs/pm/ACTIVE_TASK_*.md`/`RESULT_PACKET_*.md`の既存??は触らない。
- コミットメッセージ: `FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-01 (fix1): Family C Production runnerに全体生成・regeneration・resume経路を実装+runtime evidence+Gate再判定(<結果>)+ユーザー実検証記事一覧REPORT`
- trailer: `Task-ID: FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-AND-USER-TEST-INVENTORY-01`
- push: `git push origin main`。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_WIRING_FAMILY_C.md`末尾「## 差し戻し1回目」に:
1. T-0結果
2. 実装したstage一覧(関数名・ファイル:行)、retry/fallback(cascade関数の呼び出し箇所)、regeneration(`--only-segments`)、resume(sha256判定)、ASRキャッシュ方針、B1非適用ガードの維持
3. runtime evidence: (a) Memory A2 resume全体生成のログ要約(TTS skip件数/総数、ASRキャッシュ再利用件数、Assembly結果、Gate PASS/FAIL、duration vs Trial-11 316.569秒、生成物パス)、(b) `--only-segments story_002`のログ要約(削除→再TTS attempt数・cascade関数名・現物ASR結果・Gate再PASS・費用)、(c) B1 dry-runでA2 Contract非呼び出しの証跡、(d) 使用model/voice/routing
4. Trial script非依存Grep結果、承認済み成果物無変更確認
5. テスト結果(新規件数・総件数)
6. Dangling Reference Check再実行表
7. 完了判定12項目チェック表(再判定、各項目の証跡所在)と**Gate判定**
8. SSOT是正位置(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS各行)
9. 監査報告commitの確認(4ファイル)、Fable注記追記位置
10. 費用(TTS/ASR/LLM)、commit hash・push結果、残差分要約
11. STOP該当有無、事前指定外Read(理由付き)

ユーザー向け表記は「B1」に統一(「B1B」不使用)。
