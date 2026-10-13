# JA-ASR-ORTHOGRAPHIC-EQUIVALENCE-COMPREHENSIVE-01 委任_01(2026-10-13)

親: EIGO-RADIO-QUALITY-CROSS-FAMILY-FOLLOWUP-01 ③。実行: sonnet-worker。費用 JPY0 / 上限10(ASR・TTS・LLM呼出なし、`cost_01.json`)。
Production変更なし。Trial: `er066_ja_asr_orthographic_equivalence_01_*`(Production非import)。委任文は固定ブロック見出し抄録のため`check_delegation_prompt.py`のFAILは記録のみ。
証跡: `er066_output/ja_asr_orthographic_equivalence_01/`(harvest_raw_01.json / baseline_prod_01.json / before_after_01.json / before_after_tables_01.md / cost_01.json / state_guard_01.json)。
使用モデル: なし(既存転写のオフライン再判定のみ、最新モデル原則の対象外)。

## 結論
- 「三日間/3日間」型は助数詞追加では終わらず、「数値+助数詞→値署名+読み」層(Trial)で包括可能。実run由来6件を新規救済(Melos三日間3、`20％/20パーセント`、`10代/十代`、`1日/一日`)。敵対的反例35件の誤PASS 0。
- 既存承認仕様(閉リスト助数詞)の配線漏れ・不具合は**なし**(単一funnel、閉リスト15対x2文脈=30件全PASS実測)。日/人は仕様どおり除外+SCG S1除外であり配線漏れではない。Production無変更。
- 日/人/代/円/%等を署名一致のみで救済する層は新自動PASS条件=Trial止まり(USER_DECISION_REQUIRED)。
- 副次発見: 現行Production Candidate Eが`三日間`->`三日目`を誤PASS(間/目が候補読み「め」共有)。OPEN-333候補、Trialの署名ガードで取消可、Production無変更。

## 1. 既存機構の表(コード位置・判定順序・適用範囲)
入口はすべて `generate_narration_snippet_verified_strict(language="ja")` または `generate_a2_japanese_with_fallback`(minimal fallback)->`er007_ja_secondary_asr_01.evaluate_attempt_ja_with_cascade[_detail]`->`er007_ja_asr_validator_01.classify_ja_asr_match`。

| # | 機構 | 位置/順序 | 適用範囲 | 日/人・表記差への効き | Status |
|---|---|---|---|---|---|
| 1 | `normalize_ja`(NFKC+句読点除去+`safety.normalize_kanji_counter_numerals_ja`) | EXACT判定直後 | 全JA経路 | 閉リスト(つ/泊/回/件/年/時間/か月/週/歳)直前の単独漢数字1-9のみ。日/人は意図的除外 | PRODUCTION_WIRED |
| 2 | `protected_check_ja` `_DIGIT_RE`数字集合比較 | opcode単位 | 全JA経路 | 片側のみ算用数字(三日間/3日間)でnumber_mismatch->TRUE_CONTENT_MISMATCH | PRODUCTION_WIRED |
| 3 | Variant Layer `try_rescue_before_resolver`(B/C/D-1/E) | number_mismatch単独時+Resolver直前の2箇所 | A2 JA。D-1は閉リスト助数詞のみ(十/百/千/万) | `10件/十件`は救済、`3日間`は不可 | OPEN-145 APPROVED(Gate3) |
| 4 | Candidate E(漢字1字ずつ候補読み総当たり) | 3の末尾 | A2 JA | 過許容を発見(7節) | APPROVED(Phase2) |
| 5 | Reading Resolver(LLM) | 3の後、非number差分のみ | A2 JA(SCGでは`allow_reading_resolver=False`) | number_mismatchはResolver前に確定、到達しない | PRODUCTION_WIRED |
| 6 | Cascade D-2 `try_upgrade_voicing_cascade` | UNCERTAIN直後、4step | A2 JA | 濁点差のみ | APPROVED |
| 7 | SCG(`_scg_exclusion_reason`, `_azure_stt_strict`) | TRUE_CONTENT_MISMATCH時 | JA全経路 | **number_mismatch除外(S1)**。表記差でもSecondary非実行->再生成(OPEN-319/287) | PRODUCTION_WIRED |
| 8 | Pronunciation Ledger/expected_readings | protected_check_ja内 | 辞書トークン | 数値表記に無関係 | PRODUCTION_WIRED |
| 9 | `validate_japanese_short_segment_match` | -- | Production未呼出(testのみ) | 同じ閉リスト共有 | 未使用 |
| 10 | 統一フロー案(`er058_output/RECONCILIATION_FINAL_REPORT_01.md` D-3/D-4、OPEN-286〜291) | -- | 提案のみ | S1を「値の不一致」で判定する案。本Trialはその具体化 | 未承認 |

PM_GOVERNANCE 21節分類: 閉リスト助数詞の表記差=**A**(動作確認済み)/日・人・代・円・%等の署名+読み正規化=**C**(新自動PASS条件、ただしD-1の`kanji_numeral_run_to_int`とOPEN-145 Trial結果を再利用=一部B)/Candidate E取消=**C**(既存機構への新規制限)。

## 2. 過去事例の横断収集
`er066_..._harvest.py`で32,026 json/jsonlを走査(telemetry/attempt_history除外)。原稿!=ASRの日本語ペア1,002(重複排除)。現行Production相当(Resolver LLM OFF+D-2): 通過752/非通過250。実run由来の非通過213の機械分類(診断用):

| 分類(実run由来) | 件数 | 備考 |
|---|---|---|
| (既存PASS) | 690 | |
| 真の誤読(別語・脱落・挿入) | 138 | ASR差分からの推定、試聴なし |
| 数値表記差(漢数字/算用数字・助数詞・単位) | 6 | 本Trial対象。Melos三日間3(HR承認済み=真値OK)、`20％/20パーセント`、`10代/十代`、`1日/一日` |
| 数値を含む差(他の誤読を併発) | 19 | メオス、端のない、伊藤評価 等の実誤読あり |
| 真の値/助数詞違い | 8 | 三->4つ、十件->100件、2泊->三泊、150->140人、2020->2021年 等。救済してはならない |
| 外来語・固有名詞(ラテン<->カタカナ/長音) | 13 | Meta/メタ、ELLE/エル、Dionysius等。Cascade/Ledger域 |
| 同音異表記・漢字/かな(Cascade域) | 6 | 規則/帰属、鍵/柿 等(UNCERTAIN) |
| ASR断片・脱落 | 5 | |
| ASR幻覚・プロンプト漏洩 | 18 | 「The message below…」等 |
句読点差はnormalize_jaで吸収済みのため収集上は不可視。真値(正しく発音)が確認できるのはMelos Std comment_1(ユーザー試聴で問題なし、個別HR承認済み2026-10-13)のみ。

## 3. 是正した配線漏れ・不具合
**該当なし**。根拠: (1)全JA経路が同一`classify_ja_asr_match`(6節)。(2)閉リスト15対x2文脈の全件PASSをProduction関数で実測。(3)日/人は仕様どおり除外。(4)減速後再検証はJAに存在しない(`apply_a2_slowdown_postprocess`はStd英語narratorのみ)。(5)JA Local RewriteはProduction未適用(OPEN-290)。

## 4. Trial設計(`er066_ja_asr_orthographic_equivalence_01_trial.py`)
- (i)表記正規化: 数値+助数詞スパン(算用数字/漢数字/桁区切り/万千百。助数詞ID30種・表層38)を`<値:助数詞ID>`署名へ。表に無い助数詞は一切変換しない(fail-safe)。
- (ii)読み等価: スパンを助数詞別かな読み(みっか/ふたり/じゅっぷん/さんぼん/しがつ/はたち 等)へ展開し、展開後の文を**既存Production判定**(pykakasi/fugashi)に委譲。ASRがかな(みっかかん)でも救済。
- (iii)安全条件: 署名(値,助数詞)の不一致=不許容。否定・別語・読み違いは展開後もNG。曖昧語「十分」「三日月」は救済しない。追加型(現行PASSは不変)。数値署名ガード=Candidate E由来PASSで署名が異なり読みも交差しない時のみ取消(同音の一回/1階は取消さない)。
- 新規依存なし。

## 5. Before/After(オフライン、ASR再呼出なし)
| 区分 | 件数 | Before通過 | After通過 | 誤PASS |
|---|---|---|---|---|
| 過去コーパス | 1,002 | 752 | 762 | -- |
| 新規救済(実run) | 6 | 0 | 6 | 0(下記) |
| 新規救済(合成fixture) | 4 | 0 | 4 | -- |
| 既存PASSの取消 | 752 | -- | 0件 | -- |
| 正常例(合成) | 37 | 11 | 37 | -- |
| 敵対的反例(合成) | 35 | 1(三日間->三日目、Candidate E) | 0 | **1->0** |
実run新規救済6件の内訳: 署名一致のみ(Stage 1)3、読み展開要(Stage 2)3。コーパス中の真の値違い8件も全て非救済のまま。敵対的反例: 値違い7+桁違い6+小数点1+助数詞違い4+順序入替1+慣用句値違い1+代/階値違い2+%値違い1+曖昧語3+否定3+別語2+読み違い4(計35)。Melos三日間以外の実run救済(%・10代・1日)は構成上同値だが音声真値は未確認。

## 6. 適用漏れ監査
| 経路 | JAに存在 | 同じ正規化を通る | 備考 |
|---|---|---|---|
| 初回 / retry / minimal fallback | あり | はい | 同一`evaluate_attempt_ja_with_cascade` |
| Cascade Primary#2/Secondary#1/#2 | あり | はい | D-2を各stepで適用 |
| SCG(Azure) | あり | はい(Resolver OFF) | **number_mismatchは実行除外(S1)**、日/人表記差は到達しない |
| 減速後再検証 | JAに存在しない | 該当なし | Std英語narratorのみ |
| Local Rewrite | JAはProduction未適用 | 該当なし | OPEN-290 |
| Family X / Z JA clip | あり | はい | `generate_a2_japanese_with_reading_safety`(Zは`ja_simple`/`kp_ja`) |
| Family Y | 未着手 | -- | |
| B1 JA | あり | はい | `voice01.generate_charon_japanese` |

## 7. 副次発見: Candidate E過許容
`classify_ja_asr_match("三日間","三日目")`=PHONETIC_MATCH(Candidate E)。`間`と`目`が候補読み「め」を共有するため、日数と序数の取り違えを通す(flag OFFならTRUE_CONTENT_MISMATCH)。`3日間/3日目`、`二日間/二日目`も同様。実運用でこれが原因の問題記録は未確認(ASRが「三日目」と書くのは音声が「みっかめ」の時のみ)。Trialの署名ガードで取消可(実コーパス取消0件)。Production無変更。OPEN-333として起票。

## 8. 残余リスク(型と検知方法)
未登録助数詞(羽・匹・冊・杯・軒)=誤NG残存、telemetryの「片側のみ数字」TRUE_CONTENT_MISMATCH集計で検知/複合数`3万5千円`=解析不能で救済せず/同音異表記(一日・一回/1階)=ASRで区別不能、既存PHONETIC方針に従う/曖昧語十分=Cascade/HR温存/展開後の数値以外の差=Production判定に依存/小標本(実run6件、真値確認はMelos3件のみ)=試験運用で救済ログを記録/Candidate Eの非数値同音過許容は未評価。

## 9. 推奨(ユーザー判断、採用は人間ユーザーのみ)
1. 限定Stage 1(署名一致=表記差のみ、読み展開なし)を先行採用案。実run6件中3件を救済、読み表の誤りリスクなし。Stage 2(読み展開)は後続。
2. 日・人・代・円・%等を署名一致のみで表記差扱い(新自動PASS条件)。三日坊主副作用は両側が同形に置換されるため再現しない。
3. Candidate E署名ガード(7節)の採用可否。
4. SCG S1(OPEN-287/D-4)は署名比較を流用する案(表記差のみのnumber_mismatchはSecondary実行可)。
Status案: Trial=`VALIDATED`(オフライン・小標本)、Production=未配線。

## テスト・runtime evidence
`.venv\Scripts\python.exe -m unittest er066_ja_asr_orthographic_equivalence_01_test_01`: 18件全PASS(約2秒、API不使用)。既存Production無変更のため既存test suiteの再実行は省略(`git diff`でProduction 4ファイル=er007_ja_asr_validator_01/er011_ja_asr_variant_layer_01/er003_audio_tts_asr_safety/er007_ja_secondary_asr_01 の差分なしを確認)。
state不変: `state_guard_01.json`(telemetry/HR queue/ledger/master store/attempt_history等11件の行数+sha256、評価run前後で変化なし。並行worker由来の変化が混ざりうる旨も記録)。
