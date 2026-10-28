# 委任_03 要点(2026-10-28、FX-MOON-SHRINKING-RESELECT-REMAKE-01、関連調査: 日本語タイトルASR NG再発)
原文=USER_04。Python=.venv\Scripts\python.exe。
## 範囲
- 2A: 今回3 attemptごと(OpenAI/Azure書き起こし、F1+F2/E3/E4発動有無・判定(記録キー名・値をfile:path)、各段階NG原因、TTS発音ミスvsASR誤認識/誤判定(推測PASS不可、聴取必要ならHuman Review HTML)、既知残存か新回帰か)。
- 2B: run_ms_03の3 attempt・Task B評価時判定と突合。現行Production判定器で保存音声再判定(保存転写あればAPI 0、再ASRは合計¥5以内)。検証でありfixではない。
- 2C: F1+F2/E3/E4の配線総点検。Family(X/Y/Z)xLevel(Std/Adv)xSection行列。各セル=WIRED+runtime証拠/配線のみ(runtime未確認)/未配線/承認済み除外(根拠file:line)。コード存在だけでWIREDにしない。
## 修正線引き(11-8)
- 範囲内=配線漏れ/経路漏れ/回帰/記録不整合の是正+Regression+検証。範囲外(新合格条件・適用拡大・閾値変更・本文題変更・承認記録注入再利用)は判断候補としてfile:line付き報告。新構造設計は停止して設計案報告(Opus条件A)。誤NG是正と誤PASS検出能力の両方検証。Family A/B/C不可触。月Std組立再開・承認音声再利用注入は行わない。
## 予算
Cap ¥20(ASR再判定・最小実走のみ。TTS再生成はFable指示なしに不可)。各有料起動前に見積+stop_check。日次1,000円。
## 成果物
- docs/research/FX-MOON-SHRINKING-RESELECT-REMAKE-01/JA_TITLE_ASR_RECURRENCE_01.md
- docs/pm/RESULT_PACKET_FXMS4.md(原文§6の順1〜7、対象ごとStatus、証拠、費用、失敗終了時の最終成果物)
- 修正時: test全PASS後、変更ファイルのみ明示git add、commit(末尾に実費)、git push origin HEAD:main(ff確認、force禁止)。SSOT本体更新は行わず更新案をRESULT_PACKETへ。
- ユーザー向け文面は書かない。
