# 委任文: USER-TEST-PERSONALIZED-NEWS-B1-REBUILD-01

## 管理ID

`USER-TEST-PERSONALIZED-NEWS-B1-REBUILD-01`。報告は`docs/pm/RESULT_PACKET_PN_B1_REBUILD_01.md`(新規、★★★★報告ここから/ここまで、累積Full Report)。一時ファイル`docs/pm/ACTIVE_TASK_PN_B1_REBUILD_01.md`。現在main=origin/main=`bf32dfda`(要fetch確認)。**並行Agentなし**。`docs/pm/locks/audio_stage.lock`を原子的作成(`open(path,"x")`)で取得し終了時に削除。`er005_cost_logger.install()`を最初に呼ぶ。**費用上限¥400**(Research/Ledger≈¥50、Writer/QA/Leakage≈¥120、TTS/ASR≈¥150目安。超過見込みならSTOP)。

## 目的(ユーザー明示承認済み: 再Research→Ledger更新→B1再生成→Gate→Browser E2E)

「Personalized News: Useful or Narrowing?」のAdvanced(B1)を**最新Researchに基づいて再構築**し、正式なAdvanced視聴ページまで完成させる。**旧B1(`er014_output/four_type_observation_01/voices/audio/b1_2v_v2/`)の単純再利用・表面修正は禁止。** Standard(A2新版、`er012_output/b_family_a2_new_topic_production_01/personalized_news_2v_a2/`、USER_TEST_READY)は**一切変更しない**(audio/script/player/status。開始時と終了時のsha256一覧で非変更を証跡化)。

新B1は、Gate/E2E/Production経路/証跡が全て揃うまで`USER_TEST_READY`扱いしない。中間Status: RESEARCH_COMPLETE→LEDGER_UPDATED→B1_GENERATED→GATE_PASS→(ユーザー試聴が必要なら)`USER_DECISION_REQUIRED`でSTOP。**Fable/Sonnetが「ユーザー試聴不要」と決めない**(最終のUSER_TEST_READYはユーザー試聴PASS後)。

## 出力先

新規dir `er012_output/personalized_news_b1_rebuild_01/`(旧B1・旧Ledgerは無変更で保持)。Research/Ledgerも同dir配下(`research/`)へ新規生成(旧`.../voices/research/verified_fact_ledger.txt`は上書きしない)。

## 必須工程(要旨)

1. 再Research(B-Family Voices正式Research経路: vfl01 researcher+verification web_search、VOICE_1/2_EVIDENCEタグ付きLedger)。既存Ledgerを信用せず現在時点の一次情報・高品質ソースを再確認。旧B1で問題となった主張(短期テストで政治的態度の測定可能な変化は確認されていない、等)の現在の妥当性/2026-02のNature論文を含む競合研究/観測と因果推論の区別/単一研究の一般化禁止/地域・母集団・期間明示/contested・uncertain明示。旧Ledgerの何がstale/invalid/ambiguousだったかを明確化。Research 1回。STOP: 旧前提と大きく異なる事実関係が判明時。
2. Ledger更新: claim/source/date/population・context/evidence type/VERIFIED・AMBIGUOUS・REJECTED/freshness/B1使用可否を明示。Fact/Ledger Checkerを通しFAILならB1生成へ進まずSTOP。
3. B1再生成(Voices 2V、Production正式経路): `er012_b_family_production_runner_01.main_b1_2v()`(write_new_theme)を新theme moduleで実行。承認済みVoices仕様(CURRENT_SPEC L679、PRODUCTION_WIRED)厳守(A/C/F/E)。leak_position_blur含む7項目Validator、残存flagはblocking、max attempt後も残ればSTOP。OPEN-167を新仕様として適用しない。品質: Advancedとして自然だが情報密度過剰にしない。
4. 後段(既存Production経路): Comment Contract→Key Phrase(B1本文から選定)→日本語タイトル(独立)→TTS(B1 2V Production経路)→ASR cascade→Pronunciation Ledger→Human Review必要ならuser_test/human_review.html(raw mp3禁止、level=Advanced)→Assembly(Gate)→player.html→user_test/unified.html→user_test_page_e2e_check.py+seek確認。
5. Production Wiring/Runtime Evidence: retry/fallback整合、DEV/Trial-onlyでないこと、actual model_id/routing、Dangling Reference Check。

## SSOT

DECISION_LOG.md: `## USER-TEST-PERSONALIZED-NEWS-B1-REBUILD-01`。OPEN_ITEMS.md: OPEN-166/151更新。ARTIFACT_REGISTRY.md: PN B1(新版)行追加。CURRENT_SPEC.md: 無変更確認。Git: 明示add、`git add -A`禁止、wav禁止、mp3可、fetch→merge、trailer `Task-ID: USER-TEST-PERSONALIZED-NEWS-B1-REBUILD-01`。

## STOP条件

Researchで旧前提と大きく異なる事実/Voices仕様変更が必要/新Product判断が必要/leakageがmax attempts後も残存/Ledger Checker FAIL解消に仕様変更が必要/TTS発音でHuman Review必要/Production path未整備/A2への影響が避けられない/費用¥400超見込み/新規OPEN itemがblocking/git conflict。承認代行禁止。

## 事前指定Read一覧

`docs/pm/RESULT_PACKET_VOICES_SPEC_01.md`、`er014_output/four_type_observation_01/voices/`(theme module・run script・research/ledger)、`er012_output/b_family_voices_position_spec01_pn_b1_regen_01*`、`er012_b_family_production_runner_01.py`の`main_b1_2v`とresearch/TTS stage、`EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-02_REPORT.md`、CURRENT_SPEC L586/L676-679/L1277-1280、OPEN_ITEMS OPEN-151/166/167、PM_GOVERNANCE 9-12・Gate 7(n)、`docs/pm/tools/user_test_page_e2e_check.py`。

## 報告項目(18項目)

1.Research結果サマリ 2.旧Ledgerの何が古かったか 3.新Ledger主要claim一覧 4.Fact/Ledger Checker結果 5.新B1構成・word count 6.Voices leakage/position結果 7.TTS/ASR結果 8.Assembly/Gate結果 9.actual model_id/routing/runtime evidence 10.Browser E2E結果 11.A2非変更証跡 12.最新Advanced URL 13.Google Sheet貼付用情報 14.OPEN-166/151等の更新 15.SSOT/Git SHA 16.コスト 17.未解決問題 18.USER_DECISION_REQUIRED有無+ユーザー判断A/B。

性質: 本タスクは新規記事のテーマ選定ではなく既存承認済みテーマ(Personalized News)の再構築であり、PM_GOVERNANCE 13節の新規記事テーマ選定ルールの対象外。

## 事前指定Grep一覧+追記位置・更新位置の手順

- `OPEN_ITEMS.md`: `grep -n "^| OPEN-166\|^| OPEN-167\|^| OPEN-151"`で該当行を特定し、各行末尾(次の`|`区切り直前)に追記する形でEditする。
- `DECISION_LOG.md`: 索引セクション(`## 参照元`直前)に1行追加、本体は末尾に新規`## USER-TEST-PERSONALIZED-NEWS-B1-REBUILD-01`セクションを追加する。
- `ARTIFACT_REGISTRY.md`: 既存Personalized News B1行を`grep -n "Personalized News B1"`で特定し、その直後に新版行を追加する。
- `CURRENT_SPEC.md`: 変更しない(整合確認のみ)。

## pytestコマンド(絶対パス・長形式引数)

`C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m pytest --verbose C:\Users\tensh\eigo-radio\er012_b_family_voices_writer_generic_01_test_01.py`
