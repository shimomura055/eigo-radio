## 管理ID

`B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-01-CLOSEOUT`(+`VOICES-POSITION-CLARITY-OPEN-ITEM-01`)。報告は`docs/pm/RESULT_PACKET_VOICES_SPEC_01_CLOSEOUT.md`(新規、★★★★報告ここから/ここまで)。一時ファイル`docs/pm/ACTIVE_TASK_VOICES_SPEC_01.md`継続。現在main=origin/main=`542d557b`(要fetch確認)。**並行Agentなし。API呼び出し0、Productionコード変更0(SSOT・記録のみ)。**

## ユーザー正式判断(2026-09-17、そのまま反映)

1. **Personalized News A2 新版(`er012_output/b_family_a2_new_topic_production_01/personalized_news_2v_a2/`、SHA `a54d0201`のplayer)= 承認/PASS**(成果物の正式ユーザー品質承認。`USER_TEST_READY`)。ただしユーザー指摘: 肯定派Voiceに「I still worry an important story could be left out.」という相手側の中心懸念を取り込む表現が残存。今回は記事全体として許容、A2は承認。**記事の再生成・修正はしない。**
2. **Voices基盤`B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-01` = `PRODUCTION_WIRED`へ確定してよい**(理由: CURRENT_SPEC/Writer Prompt/Validator/Acceptance Gate/retry・regeneration整合/regression PASS/PN A2 runtime発火・Leakage 7項目PASS/TTS〜E2E確認/ユーザー試聴承認。PN B1未完はVoices仕様原因ではなくLedger鮮度[OPEN-166])。
3. **PN B1**はVoices基盤のwiring未達として扱わず、**OPEN-166(Ledger freshness)として分離管理**。既存B1(古いFact+Leakage flag残存)はユーザーテスト対象から除外のまま。再Research/Ledger更新/B1再生成は別タスク(本タスクでは着手しない)。
4. **新Open Item登録**(仮題「Voices: Position Clarity / Synthetic Opinion Construction」)。今回はProduction実装しない。Status=`OPEN / DEFERRED`(量産前または次回Voices改善時)、`USER_DECISION_REQUIRED`ではない。

## 実施内容

### (1) Dangling Reference / Closeout確認(PRODUCTION_WIRED確定の前提、各項目にevidence[ファイル:行/grep結果/テスト名]を付ける。1つでも×ならPRODUCTION_WIREDにせず`PARTIAL`のままSTOP報告)
a. A+C+F+E正式仕様がCURRENT_SPECに存在(L679付近の「Voiceの立場境界」行)
b. initial Production path(`run_pipeline_2v`/`run_pipeline_3v`経由の`main_a2_2v`/`main_b1_2v`/`main_b1_3v`)に新原則Prompt・Validator・Acceptance Gateが存在
c. retry/regeneration経路(corrective retry、`approve_regenerate`後の再生成、Local Rewrite後の再検証)でも同一schema/原則を参照(古いschemaへの参照が残っていない)
d. `leak_position_blur` Validatorが孤立していない(schema→check prompt→corrective note→Acceptance Gate判定に接続)
e. Tension定義(共通前提→分岐点→非対称性)と整合(TensionのLeakage field集合は無変更、Fの明文化のみ)
f. Fact attribution A' default OFFと矛盾なし(`fact_attribution_mode`既定値の確認、ON時の注記がCURRENT_SPECにある)
g. DEV/Trial定義への暗黙依存なし(`er012_*trial*`/A-Bテスト用モジュールを本経路がimportしていないこと)
h. `APPROVED_FOR_PRODUCTION`残件なし(本管理IDに紐づく未配線項目がCURRENT_SPEC/OPEN_ITEMSに残っていない。PN B1はOPEN-166へ分離済みであることを明記)
i. regression最終確認: `run_project_regression.py`の再実行は不要(直近結果`docs/pm/delegation_log/voices_spec01_regression_summary.json`を参照・引用)。ターゲット3テストファイルのみ再実行(`.venv\Scripts\python.exe -m pytest er012_b_family_voices_writer_generic_01_test_01.py er012_b_family_voices_variable_voice_count_test_01.py er012_b_family_voices_a2_new_topic_production_01_test_01.py -q`)して全PASSを確認。

### (2) SSOT更新
- `CURRENT_SPEC.md` L679行(「Voiceの立場境界」)のStatus列: `APPROVED_FOR_PRODUCTION`→`PRODUCTION_WIRED`(2026-09-17ユーザー正式決定、根拠=`docs/pm/RESULT_PACKET_VOICES_SPEC_01.md`10節+本closeout確認(1)a〜i)。同行末尾に短い注記: 「PN B1はOPEN-166(Ledger鮮度)として分離、本行のwiring条件から除外」「ユーザー指摘(肯定派Voiceの相手側懸念取り込み)はOPEN-167で継続検討、本行の仕様は変更しない」。行本文の既存記述は削除しない。
- `OPEN_ITEMS.md`: 新規行(次番号を実際に確認して採番、OPEN-167想定)「Voices: Position Clarity / Synthetic Opinion Construction(Voiceの立場をどこまで純化するか)」。内容: 問題意識(現行VoicesはリアルInterview再現ではなく、対立する意見を学習者が比較しやすいようVoiceごとに構造化する教育的構造。各Voiceが相手側の中心論点を抱え込むと立場が曖昧・Voice間の差が弱まる・代表性不明・Voices形式の意味が薄れる)、具体例(PN A2新版の肯定派Voice「I still worry an important story could be left out.」= 反対側の中心懸念「重要な情報を見逃す可能性」を自ら語る。今回はユーザー許容)、検討論点7つ(①実在人物らしい複雑さ vs 立場の代表性・理解しやすさ ②現行目的では後者が本来の主旨ではないか ③`nuance allowed`の許容範囲 ④相手側中心懸念をVoice自身に言わせることを原則禁止に近づけるか ⑤nuanceは自陣営内部の留保・条件に限定すべきか[OK寄り例「Personalization is useful when I can still choose what to follow.」/NG寄り例「Personalization is useful, but I worry I may miss important stories.」] ⑥Tension/opposing Voiceに置くべき内容との境界 ⑦`leak_position_blur` Validatorのさらなる厳格化)、Status=`OPEN / DEFERRED`、期限=量産前または次回Voices改善時、Blocking対象なし、今回Production実装しない。
- `OPEN_ITEMS.md` OPEN-151行: 本closeoutで基盤`PRODUCTION_WIRED`確定・PN A2ユーザー承認・PN B1はOPEN-166へ分離、を追記(OPEN-151自体をcloseしてよいか判断し、closeするなら`CLOSED`表記と理由)。OPEN-166行: 「PN B1はユーザーテスト対象外のまま、再Research/再生成は別タスク管理(2026-09-17ユーザー決定)」を追記。
- `DECISION_LOG.md`: `## B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-01-CLOSEOUT`(索引+本体): PN A2=USER APPROVED(URL/SHA)、基盤=PRODUCTION_WIRED(確認(1)a〜iの結果)、PN B1=OPEN-166分離、OPEN-167登録、ユーザー指摘の原文。
- `ARTIFACT_REGISTRY.md`: PN A2(新版)行User Quality=PASS(USER_TEST_READY)、PN B1行=ユーザーテスト対象外(OPEN-166)。
- `docs/pm/PM_BRIEF.md`に基盤Statusの記載があれば同期(Grepで確認、無ければ無変更)。

### (3) Git
明示add(SSOT4+PM_BRIEF[変更時]+RESULT_PACKET+delegation_log)、`git add -A`禁止、fetch→merge、message `B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-01-CLOSEOUT: Voices基盤PRODUCTION_WIRED確定+PN A2ユーザー承認+PN B1をOPEN-166へ分離+OPEN-167(Position Clarity)登録`、trailer `Task-ID: B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-01-CLOSEOUT`。

T-0: 委任文を`docs/pm/delegation_log/B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-01-CLOSEOUT.md`へ保存し`.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file <path> --json-out <path>_check.json`、結果1行記録(FAILでも継続)。事前指定Read: `docs/pm/RESULT_PACKET_VOICES_SPEC_01.md`、CURRENT_SPEC L652-720、OPEN_ITEMS OPEN-151/166行+末尾採番、`er012_b_family_voices_writer_generic_01.py`(schema/gate箇所のgrep)、`er012_b_family_production_runner_01.py`(入口3関数)、PM_GOVERNANCE 18節。事前指定外Readは理由付き報告。

## 報告項目(★ブロック内)
0.T-0 1.PN A2=USER APPROVED記録(DECISION_LOG抜粋) 2.Voices基盤=PRODUCTION_WIRED(確認(1)a〜iのevidence表、ターゲットテスト結果) 3.PN B1=OPEN-166分離(記載箇所) 4.新Open Item登録内容(番号・全文) 5.OPEN_ITEMS更新箇所 6.DECISION_LOG更新 7.CURRENT_SPEC Status更新(before/after) 8.Git SHA 9.未処理USER_DECISION_REQUIRED有無 10.approved-but-unwired残件有無 11.ユーザー判断 A/B(想定: いずれも「なし」) 12.無変更証跡(`git status --porcelain er0*.py`にProduction変更なし、API 0)/事前指定外Read。
