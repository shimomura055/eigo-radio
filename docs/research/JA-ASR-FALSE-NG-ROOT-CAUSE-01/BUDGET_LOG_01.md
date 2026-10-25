# BUDGET_LOG_01(Phase 3 有料実行の実費、委任_03、2026-10-25)
Cap ¥60(PHASE3_GO.json)。runner見積もり(`usage_log.jsonl` est_jpy)は保守側、実費は`phase3_run/raw_usage_log.jsonl`の音声秒数・TTS cost_jpyから算出。
| stage | 件数 | runner見積(円) | 実費ベース(円) |
|---|---|---|---|
| A1_azure_moon | Azure 2 | 0.63 | 0.62(+失敗2回の未記録Azure約0.62) |
| A2_openai_moon_x3 | OpenAI 9 | 0.05 | 約0.05(公表単価概算) |
| A3_azure_flip | Azure 2 | 0.63 | 約0.67 |
| N3_tts | TTS 30(+書込失敗1回分1clip) | 19.50 | 0.84(raw log cost_jpy、31 call) |
| N3_asr | OpenAI 30+Azure 30 | 8.19 | Azureは30×約6秒≒約2.6 + OpenAI約0.15 |
| O1_format_prompt | OpenAI 6 | 0.03 | 約0.03 |
| 合計 | | **29.03(+未記録0.62=29.65)** | **約5.6円(Azure全34+失敗2呼出=約4.5、TTS 0.84、OpenAI約0.25)** |
Cap ¥60以内(保守側でも49%)。日次: 起動前表示adopted 981.18円(Round 2分94.28円が未反映でも+94.28=1,075.46円)+保守側29.65円=最大1,105.11円<1,500円。
実測の教訓: TTS実費は¥0.027/clipで見積(¥0.65/clip)の約1/24。Azure STTは音声秒単価¥0.0447で見積どおり。
## 起動記録(停止・失敗の開示)
1. A1: 1回目 rc=1(`init_logger()が呼ばれていません`。runner live経路の欠陥、API応答後のcost logger例外。Azure約¥0.31が未記録)。修正を試みたが`python`(shim)がEdit不成立で未適用のまま2回目 rc=1(同原因、Azure約¥0.31)。Editで修正(`er005_cost_logger.init_logger`をrunnerに追加)し3回目で成功。原因は2回とも特定済み(外部停止・原因不明ではない)。
2. N3_tts: 1回目 rc=1(`n3/`出力dir未作成でwav書込失敗、TTS 1 clip分約¥0.03)。`os.makedirs`追加で2回目で全30 clip成功(約35分)。
3. A2/A3/N3_asr/O1: 各1回で成功。起動間隔は155秒以上。stop_scope_check rc=0(各起動冒頭+手動1回)。PHASE3_GO.jsonはFable権限(委任文)で作成。
4. `phase3_paid_runner_01.py`はlive経路の欠陥2点のみ修正(各1行)。test 4/4 PASS。prototype v1の変更なし(sha不変)。
