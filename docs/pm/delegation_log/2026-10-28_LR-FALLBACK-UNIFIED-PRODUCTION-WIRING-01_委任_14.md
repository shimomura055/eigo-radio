# 委任_14: PM-SSOT-SYNC-30 ユーザー正式決定_02(告げ口心臓Narrator Voice=Schedar/報告資料=試聴フォーム定義+⏸・赤・青表示仕様)のSSOT登録+Phase B進捗の転記(転記のみ、API 0)

管理ID: LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 / FZ-TELL-TALE-HEART-NARRATOR-VOICE-01(Fable→sonnet-worker、2026-10-28)。ユーザー原文(全文必読)=`docs/pm/delegation_log/2026-10-28_LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01_USER_02.md`。判断を加えない転記。全文読込禁止(Grep+該当行)。既存行は書き換えず追記。Productionコード・`docs/research/`・ACTIVE_TASKは触らない。

## 登録内容
1. `docs/pm/USER_DECISION_REGISTER_01.md`: 判断済み2件を追記。(a)告げ口心臓Narrator Voice: Aoede→Schedar(Std/Adv、本作品限定、Family Z共通ルール化しない、英文不変、既存完成版再利用、APPROVED_FOR_PRODUCTION、配線=FZ-TELL-TALE-HEART-NARRATOR-VOICE-01)。(b)「報告資料」定義=現在の試聴・確認フォーム(全Family・全レベル共通。エンドユーザー向けアプリ表示は未決定)+表示仕様①Chunk境界`⏸`(実際の分割記録、既存分割仕様不変)②LR赤(前後英文・範囲)③Fallback濃青(Style名・範囲)、全Role(英日)、重複識別、制作本文・TTS入力に混入しない。受入7条件(§7)を逐語。
2. `DECISION_LOG.md`: 末尾へ1エントリ(両決定、原文path、Status=APPROVED_FOR_PRODUCTION・配線中)。併せてPhase B進捗を1行: 委任_06(d3775dae7)/07(e56c9a04f)/08(de9d53085)/09(ef20eb878)完了、Opus条件A完了(OPUS_REVIEW_01)、統合配線commit前。
3. `OPEN_ITEMS.md`: OPEN-569(本案件親)へ「原文_02により報告資料=試聴フォーム、⏸追加、Phase B進捗(上記commit)」を追記。新規OPEN(次番号)「FZ-TELL-TALE-HEART-NARRATOR-VOICE-01 告げ口心臓Narrator Voice Schedar版(本作品限定)」Status=制作中(run_voice_schedar_01、候補ページ`user_test/family_z_tell_tale_heart_schedar_01`予定)、公開差替えはユーザー試聴後。OPEN-503へ関連追記。
4. `CURRENT_SPEC.md`: (a)Family Z Voice割当節(Grep `narrator_voice`/`voice_assignment`/「告げ口心臓」のVoice記述)へ追記「【2026-10-28ユーザー正式決定】告げ口心臓のみNarrator=Schedar(Std/Adv)。Z共通ルールではない。原文path」。(b)統一仕様節末尾の2026-10-28 bulletへ追記「原文_02: 報告資料=試聴・確認フォーム、⏸/赤/青の表示仕様(詳細は原文§4)、配線中」。
5. 整合Grep、Git: SSOT 4件+本委任文のみ`git add`、commit「PM-SSOT-SYNC-30: 告げ口心臓Narrator Schedar・報告資料=試聴フォーム定義+⏸/赤/青表示仕様の登録(API 0)」+`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`、`git push origin HEAD:main`(競合時`git pull --no-rebase origin main`)。最終応答: 変更ファイル・commit・新規OPEN番号・raw URL。
