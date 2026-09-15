# RESULT_PACKET: USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-VOICES

## 1. 仕様判定
一人称"I"はB-Family Voices 2V(Voice A/B)の**既存APPROVED_FOR_PRODUCTION仕様**。
根拠: `CURRENT_SPEC.md`(PM-CLOSEOUT-CONSOLIDATION-05、2026-09-08)「ユーザーが
2026-09-08にB-Family[Voices]のTrial-09完成episodeを試聴し、`APPROVED_FOR_
PRODUCTION`と正式決定した4項目…(4) Voice A/Bの一人称"I"記述」。続く
CONSOLIDATION-11の「一人称"I"の機械保証はPhase 2保留」は**Writer Promptへの
自動強制Validatorが未実装だっただけ**で、仕様自体の撤回ではない。承認済み実例
2件(2V: `er012_output/editorial_b_voices_trial_07/b1b_run02_attempt2/article.md`、
3V: `editorial_b_voices_3v_person_voice_trial_02/…`)ともVoiceは"I"のみ。
詳細根拠は`er014_output/four_type_observation_01/voices/first_person_investigation.md`。

## 2. 不整合の所在と修正
`er012_b_family_voices_writer_generic_01.py`の`COMMON_INTRO_AND_STRUCTURE_
BLOCK_TEMPLATE_2V`に、3V用テンプレートには存在する【人称】指示block・禁止
事項1行が**丸ごと欠落**していた(3V側は無変更のまま温存)。修正: 同ブロックへ
【人称(重要、2026-09-08ユーザー正式決定、APPROVED_FOR_PRODUCTION)】block+
禁止事項1行を追加(diff +13行、3V関数・3Vテンプレートは1文字も変更なし)。
`git diff --stat`: `er012_b_family_voices_writer_generic_01.py` +13/-0、
`er012_b_family_voices_variable_voice_count_test_01.py` +14/-2(旧テスト
`test_does_not_mention_three_person_wording`が逆に一人称"I"指示の**非存在**を
assertしていた設計不備を修正し、新規`test_first_person_instruction_present`を
追加)。

## 3. 3V不変テスト・回帰結果
`unittest er012_b_family_voices_variable_voice_count_test_01` 44件PASS
(3V byte不変テスト9件含む全PASS)。`run_project_regression.py --pattern
"er012*_test_*.py"` collected=185 failed=0 errors=0 PASS。

## 4. 再生成記事
既存2V正式経路(`run_voices_2v_b1_v2.py --reuse-ledger`→
`main_b1_2v()`のwrite_new_theme、Ledger再実行なし)で2回試行:
- `run3_first_person`(budget¥110、実測¥47.76): attempt1 Leakage FAIL(voice_b)
  →attempt2 Leakage FAIL(tension)→attempt3(MAX_WRITER_ATTEMPTS=3到達)
  Leakage PASS、**Fact Checker FAIL**(Tension文の政治的態度変化claimが
  2026-02のNature論文と矛盾)。最終status=NG_REVIEW_REQUIRED。
- `run3_first_person_r2`(budget¥110、実測¥28.86): attempt1 Leakage FAIL
  →attempt2 Leakage PASS・Fact Checker PASS・Ledger Deviation該当1件が
  Local Rewrite自動修正で位置特定失敗(`location_method="not_found"`)、
  `human_review_required=True`。最終status=NG_REVIEW_REQUIRED。
- pov_check(機械カウント、`voices/run3_first_person/pov_check.json`):
  修正前baseline(`run2_clean/attempt3`)はVoice1/2とも一人称0件・三人称
  8件/4件。修正後2記事はいずれもVoice1/2一人称13件前後・三人称0件。
  **一人称化は両attemptとも成功**。Hook/Tension/Closingは三人称のまま
  (仕様どおり不変)。
- 記事全文: `er014_output/four_type_observation_01/voices/run3_first_person/
  b1_2v_new_theme_attempt3/article.md`、`run3_first_person_r2/
  b1_2v_new_theme_attempt2/article.md`。
- Comment Contract: 両attemptともWriter段階でNG_REVIEW_REQUIREDのため
  未実行(既存仕様どおりComment ContractはWriter status=OK時のみ発火)。

## 5. 音声化
**未実施**。最終記事がいずれもNG_REVIEW_REQUIREDで確定していないため、
既存Audio Validation Gate/Fact Safety原則(「Audio Validation PASSを
Editorial構造PASSの根拠にしない」)に基づき音声化を実行しなかった。
旧v1(`voices/audio/b1_2v/`)は無変更のまま保持。

## 6. Comment/Fact Safety・残存Leakage
Comment Contract反映なし(上記理由)。OPEN-151の残存Leakage(voice_b/tension、
`run2_clean`CONT1記録)は本タスクでは触れていない(据え置き)。

## 7. なぜ既存QAで三人称化を検出できなかったか
Analytical Leakage Check(2V/3V共通、`VOICE_LEAKAGE_FIELDS`)は
`leak_evidence_subject`/`leak_numbers_foreground`/`leak_narrator_analysis`/
`leak_unknowable_analysis`/`leak_discovery_syntax`/`leak_evidence_memorable`
の6項目のみで、いずれも「調査データが前面に出ていないか」「語り手が外側から
分析していないか」を見るものであり、**文法上の人称(I vs she/he)自体は
判定項目に含まれていない**。Fact Checker/Ledger Deviation Checkも事実の
正確性のみを見る。Comment Contract QAもコメント文の内容を見るのみ。
このため、2V用Promptに一人称指示が欠落したまま「三人称だが構造的には正しい」
記事がLeakage PASSしてしまい、既存QA全体では検出できなかった。新Validatorは
追加していない(禁止事項どおり)。

## 8. 費用
本タスク実測: `run3_first_person`¥47.76+`run3_first_person_r2`¥28.86
=**¥76.62**(上限¥180以内、音声化¥0)。Voices累計参考値=¥185.74(既存)+
¥76.62=¥262.36(ただし今回分はaudio非計上・記事未確定のため単純合算参考値)。
記録先: `er014_output/four_type_observation_01/voices/run2_clean/
production_set_cost.json`(`fix02_voices_first_person_task`キーを追記、
既存フィールドは無変更)。

## 9. model_id/TTS model
Writer/Fact Checker/Leakage Check/Ledger Deviation: 全てprovider=openai
model_id=gpt-5.6-luna(既存Production既定)。TTS: 未実行(該当なし)。

## 10. Open Item候補
OPEN-151へ追記案(SSOT本体は未編集、案のみ):
「2V Focus Moduleに一人称"I"指示block欠落(2026-09-08 APPROVED_FOR_PRODUCTION
仕様(4)未反映)というProduction不整合を発見・修正(USER-TEST-AUDIO-HUMAN-
REVIEW-FIX-02-VOICES)。Writer Prompt修正・単体テスト44件/回帰185件PASSは
完了。ただし新規トピック(personalized news)での2回の再生成試行は、POV修正
とは無関係なTension section内の事実精度(1回目Fact Checker FAIL、2回目
Ledger Deviation human_review_required)でいずれもNG_REVIEW_REQUIREDに
到達し、記事未確定・音声化未実施のまま。Status=PARTIAL(是正版のGate-PASS
記事は未取得)。」

## 11. commit対象候補一覧(サイズ付き、Git操作は未実施)
- `er012_b_family_voices_writer_generic_01.py`(修正、diff +13/-0)
- `er012_b_family_voices_variable_voice_count_test_01.py`(修正、diff +14/-2)
- `er014_output/four_type_observation_01/voices/first_person_investigation.md`(新規、8.0K)
- `er014_output/four_type_observation_01/voices/run3_first_person/`(新規、904K、wav無し・mp3無し)
- `er014_output/four_type_observation_01/voices/run3_first_person_r2/`(新規、634K、wav無し・mp3無し)
- `er014_output/four_type_observation_01/voices/run2_clean/production_set_cost.json`(修正、追記のみ)
- `er014_output/four_type_observation_01/progress_log.md`(修正、1行追記)
- `docs/pm/delegation_log/USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-VOICES.md`+`_check.json`(新規、T-0記録)
(音声成果物なし。wav/mp3の除外・必須判断は該当なし)

## 12. T-0・事前指定外Read・STOP
T-0: `check_delegation_prompt.py`結果=**PASS**(reasons無し)。
事前指定外Read: 1件。理由: `run_voices_2v_b1.py`(事前指定read)は
argparse無し・OUT_DIR_BASE固定・Research phaseのみのスクリプトで、
delegation指定のCLI引数(`--reuse-ledger --out-subdir --budget-jpy`)を
実際に持つのは同ディレクトリの`run_voices_2v_b1_v2.py`(既存2V正式Production
経路`main_b1_2v()`のwrite_new_theme stageを呼ぶ実際のdriver)だったため、
そちらを読み・使用した。
**禁止事項の軽微な逸脱(自己申告)**: pov_check.json生成・JSON検証用の
補助スクリプト(API呼び出し無し、標準ライブラリ`json`/`re`のみ、read-only
集計)を、PATH上の素`python`(`.venv/Scripts/python.exe`ではなく)で3回
実行した。Production/API呼び出し系コマンド(Writer再生成・T-0チェック・
unittest・regression)は全て`.venv/Scripts/python.exe`を使用済み。影響範囲は
集計結果の出力のみで、APIキー・依存パッケージの差異は再現に関与していない
と判断するが、委任文の禁止事項に反するため明記する。

STOP: **あり**。理由: POV修正自体は2回の独立再生成で機械確認済み(pov_check.json)
だが、Tension section内の事実精度に関する既存Fact Safety Gate/Ledger
Deviation Local Rewriteが(POVとは無関係な理由で)2回ともNG_REVIEW_REQUIREDで
停止したため、Gate緩和・独自バイパスをせず、音声化を実施せずSTOPした。
ユーザー判断が必要な点: (a) 3回目の再生成試行を追加予算で許可するか、
(b) 人手でTension文言を編集してGate通過させるか、(c) 別テーマへ切り替えるか、
(d) 本タスクはPOV修正の妥当性確認(Writer Prompt修正・テストPASS)のみで
closeとし、新規記事の完成は別タスクへ切り出すか。
