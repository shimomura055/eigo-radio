# E0_RECONCILIATION_04 (委任_04 1-5、read-only・API 0円、事実のみ。OPEN-350の結論はFable判断後に更新)

管理ID: FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 委任_04。ユーザー指示(2026-10-14): 「今回、E0の新規採用を承認したわけではない」。

## 1. E0とはどの仕様か
- 「E0」= Family X英語TTSのRole別Style値のうち**Trial(TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01 / Stage3 ROLE_ATTEMPT1_STYLE)実測値をそのまま転記した初期値**の呼称。
  `er033_tts_flash_lite_family_x_styles_01.py` の `FAMILY_X_ROLE_STYLE_EN["PREVIEW"|"COMMENT"] = "calm, conversational"`(sha256先頭12桁 `57c3fda67c1d`)。
  同定数の他Role(TOPIC_INTRO/FULL_STORY/IN_ONE_LINE)は2026-09-28にE2値へ更新済み。PREVIEW/COMMENT/HEADING_READOUTは「E2未検証のためE0のまま(不変)」と明記(CURRENT_SPEC 可変segment Role Style節 L1733-1735、DECISION_LOG L12342)。
- 別物: 「Advanced Preview=E1」(`calm, composed news anchor; steady and unhurried, clear and natural.`、sha `8862317ff766`)はTone Trial(er057_tone_trial_tts_gen_01.py SPECS["E"]["E1"])でユーザー承認済みの別Style(CURRENT_SPEC L2620、委任_03で配線)。

## 2. いつ・どの経緯で導入されたか
- 導入: `TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01` Phase 1(2026-09-28、commit f548541e4)。Gemini 3.8 Flash-Lite TTSの`speech_metadata`方式は2026-09-27にユーザーが`APPROVED_FOR_PRODUCTION`と正式決定(CURRENT_SPEC L1632)、Gate 3全16項目完了(DECISION_LOG L10830)、Fable Gate 3判定`PRODUCTION_WIRED`(2026-09-28、CURRENT_SPEC L1708付近)。
- Role別Style変更: `TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01`(2026-09-28)でTOPIC_INTRO/FULL_STORY/IN_ONE_LINEをE0→E2へユーザー決定のうえ更新。PREVIEW/COMMENTは対象外としてE0維持(DECISION_LOG L12336-12362)。

## 3. CURRENT_SPEC / DECISION_LOG / 過去承認との整合
| 項目 | 結果 |
|---|---|
| Coffee Adv comment_1〜4が実際に使ったStyle | `b1b/audit/tts_generation_results.json` の各entry `style_prefix`=`calm, conversational`、sha `57c3fda67c1d`(委任_03で再生成、runner mainの標準解決値) |
| 上記が既存承認済み仕様の定数と一致するか | **一致**(`FAMILY_X_ROLE_STYLE_EN["COMMENT"]`と文字列・sha一致。Family X全Production記事の既定COMMENT Styleそのもの) |
| CURRENT_SPECの記載 | 「PREVIEW/COMMENTはE2未検証のためE0のまま」=現行定数(L1733-1735)。**Coffee限定のComment Style決定記述はCURRENT_SPECに無い**(ADV_STYLE_FACTCHECK_02と同じ) |
| e_tone_01(委任_02時点の引継ぎ元)のComment Style | `warm, upbeat and engaging; ...`(sha `37c52d6ec237`)。tone worktree由来で**main SSOTに承認記載なし**(未承認Styleだったため委任_03で採用せず、main標準E0で再生成) |
| 新Style導入になるか | **ならない**。今回の再生成は新Style採用ではなく、既承認・配線済みの標準定数への復帰 |

## 4. 結果(事実)
- 分類: **一致(既存承認済み仕様=Family X既定のE0、Close可の材料)**。Coffee Adv Commentで使ったStyleは新規Styleではなく、2026-09-27/28に承認・配線された既存定数。
- 残る論点(別問題、新Style採用ではない): 「Coffeeに限りCommentを標準E0以外(例: e_tone_01のwarm/upbeat)にするか」は、ユーザーがCoffeeでそれを承認した記録がmain SSOTに無い=現時点で存在しない。もし将来Coffee専用Style変更を望む場合のみ別途Trial・ユーザー判断が必要。
- OPEN-350の更新(Close可否)はFable判断。本委任ではOPEN-350本文の結論を変更しない(事実参照の追記のみ)。
