# GACHA_HOMOPHONE_01 (FAMILY-X-WORD-GACHA-PRODUCTION-01 委任_02, 2026-10-24) 「gacha↔gotcha」型の分類と対応案(実装なし・API 0)

## 1. 事実(観測値)
- 対象: Adv `full_story_part3`。canonical `a gacha at the entrance` をASR(OpenAI gpt-4o-mini-transcribe)が `a gotcha at the entrance` と転写。Secondary(Azure)も文が混線し裏付けにならず NG_BOTH。委任_01の3回+委任_02の再生成(3回+Local Rewrite 1回)=Adv計7テイク全てで `gacha→gotcha`(他の差は attempt2 `oh` 脱落、attempt3 `you've→you` の1語のみ。いずれもgachaとは別)。
- 原因: `gacha` はCMU辞書に無い(`er008_asr_variant_hardening_15_homophone_en._phone_variants('gacha')=None`、`('gotcha')=['G AA1 CH AH0']`)。er109 `evaluate()` の結果は `equivalent=False, rule=incomparable, why=cmu_unregistered_or_no_strong_reading`(fail-closed。再現: `.venv\Scripts\python.exe`でevaluate(canonical, asr))。固有名詞でないため PNAP/RET実体表の対象外(実体表は3件、gachaは載らず)。
- 発音(Fable提示のIPA): gacha /ˈɡɑːtʃə/(米)と gotcha /ˈɡɑtʃə/ は同音。TTSがそう読み、ASRが高頻度語へ寄せた可能性が高い(音声欠陥の証拠なし。Fable判断と同じ)。

## 2. 既存の承認済み機構ごとの適用可否
| 機構 | 適用可否 | 根拠 |
|---|---|---|
| er109(表記・同音正規化。X/ZでAPPROVED_FOR_PRODUCTION) | 不可(データ追加の口なし) | 音素はCMU由来のみ。`er109_asr_orthographic_equivalence_01.py`冒頭「CMU未登録/判定不能は非同値(fail-closed)」。補完辞書は DESIGN_PROPOSAL_01 §7「新規救済範囲(別判断)」 |
| er109 UKUS対表(`er109_ukus_pairs_v1.json`) | 不可 | 英米綴り差の固定対表のみ。同音の別語は対象外。表の追加・昇格は仕様変更扱い(`er109_ukus_spelling_01.py`冒頭) |
| PNAP/RET実体表・受理境界 | 不可 | 固有名詞(entity)専用。gachaは一般語/借用語でentity化されない |
| approved equivalence(Tier1/READING_MATCH等) | 不可 | 数詞・読み・差分アンカー型。借用語の同音は枠外 |
| **`er008_asr_variant_hardening_15_homophone_en._HOMOPHONE_OVERRIDE_GROUPS`(空の閉じた補完テーブル)** | **データ追加のみで可能(部分的)** | 同ファイル:40-46に「CMU辞書で解決できない同音語ペアが量産時に見つかった場合のみ、ここへ追記する」と設計済み。`homophone_arpabet_equivalent()`が参照(:65-95) |

## 3. オフライン再現(API 0、ファイル無編集、プロセス内だけで`_HOMOPHONE_OVERRIDE_GROUPS=(frozenset({'gacha','gotcha'}),)`を差し替え)
Production判定 `val.classify_asr_match(canonical_before_LR, asr_text, segment_id='full_story_part3', role='FULL_STORY')` を委任_02の再生成の3テイクに適用:
| テイク | 現行 | 追加後 |
|---|---|---|
| 1(gachaのみ差) | TRUE_CONTENT_MISMATCH | ASR_VALIDATION_UNCERTAIN |
| 2(`oh`脱落+gacha) | TRUE_CONTENT_MISMATCH | ASR_VALIDATION_UNCERTAIN |
| 3(`you've→you`+gacha) | TRUE_CONTENT_MISMATCH | TRUE_CONTENT_MISMATCH(別の差が残る) |
意味: データ追加でgachaだけが原因のテイクは「内容誤り(TTS失敗)」から「ASR不確実」へ降格され、Cascade(Secondary)が確認すれば通る経路に乗る。ただし**自動PASSにはならず**、Secondary確認が別途必要(今回のSecondary=Azureは混線出力でNG_BOTHだった)。効果は部分的で、Local Rewrite(Style gate)問題は解消しない。

## 4. 分類(PM_GOVERNANCE 11-8)
**修正へ進む(Fable判断後、影響分析gate付き)**。理由: (a) 原則「同一発音=同等」は承認済み(A既判断: ASR-HOMOPHONE委任の原文、`DESIGN_ADDENDUM_02.md` §8冒頭の27-3分類)、(b) 手段は設計上データ追加を想定した既存の閉じた補完テーブルで、新しい受理クラスではない。
留意: ①`homophone_en`は共有Validatorのため A/B/C にも効く(動作変化は NG→UNCERTAIN の降格のみ。gacha/gotchaがA/B/C記事に現れる確率は極小)。②「既存Production辞書の直接編集」は11-7の限定例外の外=Fable判断(承認根拠の確認)が前提。もしFableが「新規救済範囲」と判断するなら**ユーザー判断要**(案B参照)。③個別語whitelistを増やし続けるのは非スケーラブル(同ファイルのコメントも「主方式にはしない」)。借用語(gacha, bento, karaoke…)が増えるなら下記案Cが要検討。

## 5. 対応案
- **案A(推奨・データ追加のみ)**: `_HOMOPHONE_OVERRIDE_GROUPS` に `frozenset({"gacha","gotcha"})` を追加。影響分析gate(実装時): (1)保存ASR記録(`ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01/stored_census_01.json` 4,877 attempt)への再判定で PASS→NG=0、NG→UNCERTAIN の件数と中身の列挙、(2)X/Z golden・wiring signature(`er109_wiring_signature_01.py`)再作成の要否確認、(3)DefaultOffIsolationではなくdata追加testを1件追加、(4)本件Adv part3の保存テイクをAPI 0で再判定(上表)。費用0〜数円(再生成なし)。効果: gacha型の同音NGは減るが、Secondary確認とLocal Rewrite/Style gateは別。
- **案B(ユーザー判断要の場合)**: 借用語・外来語向けの発音補完辞書(CMU未登録語の音素を閉じた表で供給する新規救済範囲)を新設。広く効くが「新しい受理クラス」で承認済み仕様の拡張(DESIGN_PROPOSAL_01 §7)。QCD: 開発費中(Trial+Opus条件A)、品質=誤同値リスクを閉じた表で制御、量産単価=HR/再生成の削減が見込める。
- **案C(現状維持)**: 同音でNGになったsegmentは既存のHR手順(approve_regenerate 1〜2回→人間承認 record_human_approval)で処理。費用増: 本件で1 segmentに約+14.7円(Azure Secondary 8.6円+TTS/ASR 6.1円)+ユーザー耳確認の手間。
- 採否はFable。本委任では実装していない(コード・辞書変更0)。

## 6. OPEN登録
OPEN-498(分類=修正へ進む、次委任案=案A実装+影響分析gate+ユーザー耳確認後の記録)。
