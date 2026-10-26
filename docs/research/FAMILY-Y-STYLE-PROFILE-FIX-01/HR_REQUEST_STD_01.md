# HR_REQUEST_STD_01 — Standard 承認待ち2 segment の試聴・承認依頼(委任_03、API 0)

管理ID: FAMILY-Y-STYLE-PROFILE-FIX-01 委任_03。公開ページ: https://shimomura055.github.io/eigo-radio/user_test/family_y_production_redelivery_fee_03/index.html (節 `#std_hr`)。
到達Status=Adv修正版公開・Std HR承認待ち(「完成」ではない)。承認は人間(ユーザー)のみ。AI/Fableは代行しない。

## 1. 対象と候補take(run `run_style_fix_01`、`a2/narration/attempts/`)
| segment | take | 経路 | 長さ | 判定 | 台本との語句差(句読点・大小文字除く) |
|---|---|---|---|---|---|
| y_voice_1(Puck) | 1 | 承認Style PD06(標準経路) | 39.2秒 | NG_BOTH/secondary_not_accepted | OpenAI: `redeliveries`→`re-deliveries`、`was not home`→`is not home`、`redelivery`→`re-delivery`。Azure: `was`→`is`、`want it`→`wanted` |
| y_voice_1 | 2 | 同上 | 35.87秒 | 同上 | OpenAI: take 1と同じ3点。Azure: `was`→`is`、`want it`→`wanted` |
| y_voice_1 | 3 | **fallback短文Style**(minimal_fallback。承認Styleと異なる) | 34.88秒 | 3回ともNG_BOTH(最終)。fallbackはStd規則でHR承認必須 | OpenAI転写は語句差なし(`redeliveries—they`のダッシュ表記のみ) |
| preview(Aoede) | 1 | 承認Style S3(標準経路) | 15.72秒 | NG_BOTH | 台本「思いどおり」→ASR「思い通り」(読み同じ) |
| preview | 2 | 同上 | 15.75秒 | NG_BOTH | 同上 |
| preview | 3 | fallback短文Style | 14.69秒 | 3回ともNG_BOTH(最終) | 同上(OpenAI) |
各takeのASR全文は公開ページの `#std_hr` 節(`build_summary_03.json` にも保存)。

## 2. 所見と推奨(判断材料。採否はユーザー)
- preview: 差は表記ゆれのみ(読みが同じ)。take 1または2(承認Style)の推奨。
- y_voice_1: take 1/2は「re-deliveries」のハイフン表記に加え、**台本の `who was not home` が両ASR(OpenAI・Azure)で `who is not home` と聞こえている**。実際の言い違いか否かは耳で確認が必要(委任_02時点の『表記ゆれのみ』という整理はこの点で不十分だったため訂正)。take 3は語句差が無いが、承認Styleと異なるfallback短文Styleであり、採用するとStyle実測照合(承認PD06との一致)が崩れる。特段の理由がなければ、`was`が正しく読まれているtake 1または2を推奨。どれも不可なら再生成も選べる(費用・可否はFableが別途見積もる。review lockの解除はFable/ユーザー権限)。
- 参考(Std 通過16 segmentは同ページ `#std_ok` で個別再生可能。通し版は承認後に追加)。

## 3. 承認の操作方法
1. ページの `#std_hr` で各takeを聴き、次の形式で返答する(例): 「Std y_voice_1 = take 1 承認、preview = take 2 承認」。再生成希望なら「y_voice_1 = 再生成」。
2. その返答を受けて、Fableが委任で次を実行する(別委任。本委任では実行しない):
   - ユーザー返答の逐語保存(`docs/pm/delegation_log/`)。
   - 採用手続き: run_01の先例 `er121_e1_hr_adopt_r0_01.py`(`TARGETS`が`run_01`固定・attempt番号固定のため、`run_style_fix_01`・指定takeに対応する版が必要)に準じ、採用wavを `a2/narration/<seg>.wav` へ置換 → `asm.record_human_approval()`(`er003_v1_n3_01_assemble.py:96`)→ `review_lock_state` を RESOLVED/HUMAN_APPROVED へ。
   - y_voice_1は、run_01先例と同じくStd 6%減速(ffmpeg atempo)と減速後ASR再検証(`er121_e1_slowed_asr_recheck_01.py`、ASR 1回)が付随する。
   - 注意: 採用takeのStyle記録を結果entryへ反映しないと `style_actual_vs_approved` の y_voice_1/preview 行が不一致のまま(Gateが再度BLOCKする)。採用手続きの設計に含める(fallback=take 3を採用する場合は承認Styleと異なるため、Gate側の扱いを要確認)。
   - その後 `--stages gate,assemble,pages,page_verify` を1起動で実行し、Std/Adv通し版を `_03` に追加(委任_04)。
## 4. run_01での先例(参考)
`run_01/a2/audit/human_approved_segments.json`: preview 2026-10-26T06:45:07、y_voice_1 06:45:15(approved_by=user)。いずれも **attempt5**(R0本文)を採用(`ypl7_user_approval_record_preview.json`/`..._y_voice_1.json`)。y_voice_1は6%減速(43.85→46.465秒)付き。承認根拠=`docs/pm/delegation_log/2026-10-26_FAMILY-Y-PRODUCTION-LAUNCH-01_USER_E1_APPROVAL.md`。この承認は旧Voice(Algieba)・旧Styleに紐づくため新runには流用されない(OPEN-535どおり。`b1b/audit/human_approved_segments.voice_guard_quarantine.json`)。
