# VALIDATION_03 (KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01 委任_03、2026-10-15)

**Trial分類(Sonnet提案、最終判定はFable): `VALIDATED`(DEV/Trial専用mode=correctedのTrial基準を満たした。標本は小・限界は§6)**。`APPROVED_FOR_PRODUCTION`・`PRODUCTION_WIRED`ではない。Production既定OFF(`GLOSS_ALIGNMENT_ENABLED`="0")は無変更で維持、量産run凍結継続。VALIDATEDとなったため、gloss再整合工程を正式Production採用するかはユーザー判断(Fableが諮る)。

使用モデル: 要求=応答とも`gpt-6-luna`(effort=high、現行SUPPORT_MODEL=本番ラインと同一。VALIDATION_02と同一条件。最新性の外部再確認は本委任では未実施で前回記載に依拠)。承認規則sha256 `447e07cb…`不変。

## 0. 原因確認(P3 4/16)
対象: `trial_t1/results_P1_P2_P3_P4_P4b_P5_P6_P7.json`の rows[11][12][43][44](`fall into`『～に落ちる』rep1/2、`speak for`『～の代わりに話す』rep1/2)。
- 4件すべて `llm_current_consistent=false`・`attempts_used=1`・`first_attempt_verdict=VALID`・qa=PASS・`machine_check.pass=true`(必須内容語なし=機械検査対象外)。
- reasoningの要旨: 「『～に落ちる』より、債務などの状態に入る意味を自然に表す『～に陥る』が適切」(fall into)/「『～を代表して話す』が意味に合う(『代わりに話す』では意味が足りない)」(speak for)。
- **結論 = (a)**: LLMが「不一致」と**判定して**書き換えた。「一致」と判定しつつ別文字列を返した経路(b)=機械チェックの穴では**ない**(真⇔不変の矛盾チェックは効いている: 該当4件は`current_gloss_consistent=false`なので矛盾に該当しない)。よって原因は課題指示文(「より適切」な訳への書換えを抑止する文言が無い)であり、コード修正は不要。

## 1. 文言差分(correctedの`build_user_message_corrected`のみ。`build_user_message`[legacy]・承認規則本文・選定/canonicalization Prompt・Rule7・Gate・Lock・既定OFF・A'構造は無変更)
指示2へ追加:
> current_japanese_glossが最終key_phrase全体の意味を既に表している場合は、より自然・より適切と思える言い換えがあっても書き換えず、current_japanese_glossをそのまま返してください。書き換えるのは、key_phraseの語の意味が欠けている・誤っている場合だけです。

判定の参考例へ1行追加:
> key_phrase「fall into」にcurrent「～に落ちる」: 意味は表れているので一致です(「～に陥る」へ書き換えません)。

unit: `er003_test_key_words_gloss_alignment.py` 79 passed(既存矛盾文削除test・承認規則sha test・OF-KGDC(b)文testはそのまま通過、新規`test_message_has_no_unnecessary_rewrite_instruction`で追加文2点の存在+矛盾文なし+legacy課題指示文に追加文が無いことを固定)。差分: `er003_key_words_gloss_alignment.py` +6/-2行。

## 2. 再Trial結果(fresh、`trial_t1b/`・`trial_t1c/`・`trial_t2b/`。STOP確認[`tools/stop_scope_check_01.py` stop=false]後に実行、全rc=0)
| 指標 | 前回(VALIDATION_02) | 今回 | 95%上限(Clopper-Pearson) |
|---|---|---|---|
| P3 書換(『～』正当表現を強制投入) | 4/16 | **0/16** | 17.1% |
| P2 書換(整合済み) | 0/4 | **0/4** | 52.7% |
| P7 書換・record-only誤NG(追加語あり×自然訳) | 0/12 | **0/12**(誤NG 0、gate追加誤NG 0) | 22.1% |
| 整合済み3パターン合算の書換 | 4/32 | **0/32** | 8.9% |
| P1 反映率(既知不整合・拡張KP) | 12/12 | **6/6**(『～』『〜』2表記含む) | 失敗側上限39.3% |
| P4 反映率(具体語欠落の注入) | 12/12 | **6/6** | 失敗側上限39.3% |
| T2 誤PASS(意味違い注入) | 0/24 | **0/12**(12/12を不一致と判定し修正)。前回と合算 誤PASS 0/36 | 今回のみ22.1%/合算8.0% |
| 1回目attempt INVALID率 | 0/88 | **0/57**(P2/P3/P7 32+P1/P4 13[P4b含む]+T2 12) | 5.1% |
| 2回失敗(HR到達相当) | 0/88 | **0/57** | 5.1% |
実LLMで2回目retry経路は今回も一度も発火せず(全itemが1回目で成立)。P4b(`put solo travel at`、観察のみ): 『ソロ旅行を～％とする』を整合と判定して不変(前回rep2と同じ。規則15行違反の検出は選定段の責務=想定どおり)。
- 費用: P2/P3/P7 JPY0.8184(8 call、30.7秒)/P1/P4/P4b JPY0.4241(3 call、24.0秒)/T2 JPY0.3589(3 call、19.3秒)= **今回JPY1.6014**(見込み1.8内)。**累計JPY4.0961/5**(2.4947+1.6014、残JPY0.90)。単価平均0.114/call(前回0.125)。
- 目視(全出力、Sonnet、ユーザー未確認): P1/P4/T2の最終glossは平易で自然(`人間の助っ人を招き入れる`/`真水を使い果たす`/`秘密を漏らす`等)。前回指摘の直訳気味`新鮮な水がなくなる`は再発せず(P4 `真水を使い果たす`、T2 `真水が尽きる`)。直訳化への圧力は観測されず。
- 効果不足時の追加策(§4手順): 不要(基準達成のため未実施。追加の文言変更・スキーマ変更・コード変更なし)。

## 3. 終了条件5点の対応表(ユーザー③)
| # | 条件 | 証拠・数値 | provenance | 未確認事項 |
|---|---|---|---|---|
| 1 | 正しいglossを不必要に変更しない | `trial_t1b/results_P2_P3_P7.json`: 整合済み32 eval(P2 4/P3 16/P7 12)で書換0(上限8.9%)。本番ではそもそも対象外itemは非LLM入力(O1差分0、VALIDATION_02) | fresh(Trial)+reuse(O1) | **`fall into`は課題指示文の判定例に使ったため当該item(rep2件)は独立検証ではない**。独立の検証は`speak for`ほか未例示の7表現(14 eval、書換0)。『～』正当表現の母集団は小 |
| 2 | 不一致glossを適切に修正できる | P1 6/6・P4 6/6・T2 12/12で反映・修正(`trial_t1c/`・`trial_t2b/`)。前回のT1/T2と合わせ P1/P4 36/36・T2 36/36(合算) | fresh+reuse(VALIDATION_02) | 前回との条件差=課題指示文の1文のみ。標本小(上限は表の通り) |
| 3 | 既存承認済みglossルールと矛盾しない | 承認規則本文はsha256 `447e07cb…`不変(実行時抽出、unit test)。追加文は「意味が既に一致している時に書き換えない」であり規則本文と非矛盾。規則15行型(数値穴埋め)の検出は再整合段の責務外(P4b観察、前回と同一) | fresh+synthetic | 規則15行違反を再整合段が検出しない点は設計どおり(選定段の責務)。**この責務分担のままProduction採用してよいかはユーザー判断材料** |
| 4 | 失敗時に不整合なglossが完成物に混入しない | T3 mock 27/27 PASS(`trial_t3_rerun_02/T3_RESULTS.json`、実API・実TTS 0): HR待ちstatus・Audio Validation Gate・FamilyZE2EStop・B1解説LLM 0 call・page省略・resolve後の再開。**今回の文言変更はこの経路に影響しない**(コード経路無変更) | synthetic/mock | **実LLMで2回失敗する経路は未発火**(0/145: 前回88+今回57)で、実環境のHR停止はmockのみで確認。fresh Production E2Eは未実施(E2E自己確認 No) |
| 5 | 品質・速度・量産費用に許容できない副作用がない | 単価0.114/call(前回0.125)、追加量産費は§5。1 call 約15〜25秒。P1/P4/T2の質は維持。Regression新規failure 0(§3-2) | fresh+reuse | 実際の量産フロー全体での時間・費用の増減は未計測(Production既定OFFのため) |

### 3-2 T3・Regression(新規failure 0)
- T3 mock再実行: `trial_t3_rerun_02/` 27/27 PASS(実API 0、`TTS_EXECUTION_MODE=STANDARD`明示)。注意: 最初にRegressionと並列で走らせたところ T3(r)(共有state sha同一)が共有stateを同時に書換える他suite(Regression)の影響で1件FAILしたため、**Regression完了後に単独で再実行して27/27**(並列実行による干渉であり、コード不具合ではない。`regression_03/t3_rerun_02.log`)。
- Regression(`regression_03/`): er003 1668件 passed 1664/failed 3/errors 1(`er003_test_bad`のfixture 1+`er003_test_p2j_investigate` 3=既存4件のみ、前回`PREEXISTING_FAILURES_CHECK.md`と同一)/er019 421/421/er030 37/37/er063 59/59/er026 単独再実行 86件中79 pass・failed 7(既存7件と同一)。**最初のer026並列実行は9 failedだったが、追加2件[`er026_family_z_e2e_integration_test_01`の`test_legacy_dry_run_flag_maps_to_dry_run`/`test_shared_state_files_unchanged_by_mock_run`]は他suiteの並列実行による共有state干渉で、単独再実行(`er026_serial.log`)で消えた**。
- unit: 79 passed。

## 4. Status分類と根拠
`VALIDATED`(提案)。根拠: (REJECTED条件)該当なし。(VALIDATED条件)TRIAL_PLAN_02の未達だった「P2/P3の書換・誤FAIL 0」が P2 0/4・P3 0/16・P7 0/12で達成、それ以外(P1/P4反映維持、T2誤PASS 0、INVALID率0、新規failure 0、費用Guardrail内)も維持。したがってVALIDATION_02で`USER_DECISION_REQUIRED`の理由だった項目は技術的に解消した。
ただし§3の未確認事項(特に#1の`fall into`例示、#4の実LLM retry/HR未発火)があるため、最終Statusは**Fableが§3の証拠を照合して確定する**。

## 5. Production採用判断に必要な情報
- 量産費見積(推定、出典=VALIDATION_02 §5を平均単価0.114/callで再スケール): 通常0.014〜0.08(前回見積りとほぼ同等、本文変更による入力増は約150 tokenで影響軽微)、最悪約0.6、絶対最悪約1.7/記事セット。70円/記事セットの約0.02〜0.13%。
- 時間: 対象itemがある記事levelにのみ+15〜50秒。対象は全itemの0.6%・記事の約7%(census、reuse)。
- HR見込み頻度: 実測2回失敗0/145(前回88+今回57、retry経路は実LLMで未発火)。上限は VALIDATION_02 §5と同じ算式で約0.2%/記事level未満(標本依存)。
- 残リスク: (1)`fall into`の独立性(§3 #1)、(2)実LLMでretry/HR経路が未発火(mockのみ)、(3)規則15行型を再整合段が検出しない(選定段の責務)、(4)機械検査(追加語→span対応)のgate化は未決(実LLMでは常にmappingが埋まり効果未観測)、(5)OF-KGDC-11=OPEN-359(Family X `NG_REVIEW_REQUIRED`素通り)は別件で未解決、(6)本番既定OFF・量産run凍結のまま。

## 6. 未解決
- ユーザー③に従い、**VALIDATEDなら**gloss再整合工程の正式Production採用(既定ON化・Production Wiring)をユーザーへ諮る(Fable)。それまで既定OFF維持・Production採用表記なし。
- gate化の是非・OPEN-359・HR運用の正式採用(通知失敗時fail-closed等)は、Production採用判断時に併せてユーザー判断。
- 今回はTTS未実行、`.env`未読込(認証は既存`ga.make_alignment_fn`内の`load_dotenv()`経由)。
