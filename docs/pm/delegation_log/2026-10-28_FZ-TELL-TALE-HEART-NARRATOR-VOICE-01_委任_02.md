# 委任_02: PM-SSOT-SYNC-31 告げ口心臓Narrator Voice(Schedar→Fenrir修正、Fenrir版完成・候補ページ)のSSOT同期+Fable受入結果の転記(転記のみ、API 0)

管理ID: FZ-TELL-TALE-HEART-NARRATOR-VOICE-01(Fable→sonnet-worker、2026-10-28)。ユーザー原文=`…_FZ-TELL-TALE-HEART-NARRATOR-VOICE-01_USER_02.md` §1(Fenrir修正、必読)+`…_LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01_USER_02.md` §2(当初Schedar)。成果=`docs/research/FZ-TELL-TALE-HEART-NARRATOR-VOICE-01/VOICE_CHANGE_01.md`(委任_01、commit 8faf3bd58)。転記のみ・判断を加えない。全文読込禁止(Grep+該当行)。既存行は書き換えず追記。Productionコード・docs/research・ACTIVE_TASKは触らない。

## Fable確定事項(転記内容)
- ユーザー修正(2026-10-28): Narrator=**Fenrir**(Schedar不採用。理由=警官役にSchedar割当済みで重複)。警官・老人のVoice不変。本作品限定、Z共通仕様不変。
- 実装: `er062_family_z_structure_01.py` `STORY_NARRATOR_VOICE_PINS`(告げ口心臓のみFenrir)+`narrator_voice_for()`。対象=本文narration clip(`full_story_*`、speaker=narrator)のみ。intro/preview/comment/KP/JA/Shellは既存role表のVoice(不変)。既定`FAMILY_Z_NARRATOR_VOICE`=Aoedeは不変。test: er062 voice_assignment 16件+registry 23件PASS。
- 実走: `run_voice_fenrir_01`(正式runner 1起動、既存完成版run_reselect_01を複製・再利用)。Std/Adv narrator 7chunk+親2を再生成、dialogue(Algieba)・KP・解説・JA・intro等はsha一致で再利用。ASR全PASS、Style実測Gate・速度v2 Gate通過、Chunk計画不変(Std [60,69][68,71]/Adv [58,62][65,61])、本文不変(Std b94c7305…/Adv e11b84dd…)、page_verify全再生OK、LR 0、新規Fallback 0(再利用のAdv kp2_en ENGLISH_LOCK 1件は継続)。候補ページ=`user_test/family_z_tell_tale_heart_fenrir_01/`(公開差替えなし、ユーザー最終試聴待ち)。公開中`family_z_tell_tale_heart_reselect_01`・run_reselect_01は不変。
- 実費: Fenrir版¥10.23。Schedar版(修正指示が起動後に届いたため途中停止、不要費用)約¥8〜10(b1b実測¥5.04、a2概算)。合算約¥20(Cap¥60内)。Schedar版clipは`run_voice_schedar_01`に記録のみ残置(未使用)。
- **Fable受入(2026-10-28)**: 目的適合(Narrator=Fenrir、他Voice不変、本文・学習項目・解説不変)/未承認機能なし(作品限定pin、既定不変)/失敗終了なし/撤去・残置: officer再割当は撤回・未実施。**Status=PRODUCTION_WIRED(本作品限定pinの配線+正式経路runtime evidence+test、Fable判定)**。完成版はユーザー最終試聴待ち(試聴PASSではない)。
- 軽微発見(C、新規OPEN): attempt JSON(`narration/attempts/*.json`)の`"voice"`欄がleaf定数(`p9a.VOICE_NAME`=Aoede)のラベルで、実際の送信Voice(results `reuse_key.voice`=Fenrir)を反映しない(`er003_v1_n3_01_tts_generate.py:859`付近)。判定・再利用には影響なし(reuse_keyが正)。記録の観測性として「修正へ進む(軽微)」。

## 作業
1. `CURRENT_SPEC.md`: Z Voice割当節のSYNC-30追記行(「告げ口心臓…Schedar」)の直後へ「【2026-10-28修正】Narrator=Fenrir(Schedar不採用、理由)、PRODUCTION_WIRED(Fable受入2026-10-28、run_voice_fenrir_01)、候補ページ、ユーザー最終試聴待ち」を追記(Schedar行は書き換えず履歴として残す)。
2. `OPEN_ITEMS.md`: OPEN-570へ上記(修正・完成・受入・実費・試聴待ち)を追記、Status=`PRODUCTION_WIRED`+`USER_LISTENING_PENDING`。新規OPEN(次番号)「attempt JSONの`voice`ラベルがleaf定数(観測性、軽微)」。OPEN-503へ「Fenrir版候補あり(OPEN-570)」を1行。
3. `DECISION_LOG.md`: 末尾1エントリ(修正決定・実装・受入・実費・commit 8faf3bd58)。`docs/pm/USER_DECISION_REGISTER_01.md`: SYNC-30の告げ口心臓Voice判断済み行へ「→2026-10-28修正: Fenrir」を追記、「次工程をブロックするUDR」に「告げ口心臓 Fenrir版 最終試聴(ユーザー)」を記載。
4. 整合Grep(`Schedar`/`Fenrir`/`OPEN-570`)。Git: SSOT 4件+本委任文のみ`git add`、commit「PM-SSOT-SYNC-31: 告げ口心臓Narrator Fenrir版 PRODUCTION_WIRED・候補ページ・実費・attempt voiceラベルOPEN(API 0)」+`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`、`git push origin HEAD:main`(競合時`git pull --no-rebase origin main`)。最終応答: 変更ファイル・commit・新規OPEN番号。
