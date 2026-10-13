# JA-ASR-ORTHOGRAPHIC-EQUIVALENCE-COMPREHENSIVE-01 委任_02 REPORT(2026-10-13、記録補完は委任_03)

Opus独立レビュー必須修正の反映・再Trial・訂正記録。採用判断なし。Production未配線・無変更。費用JPY0(API呼出なし、既存転写のオフライン再判定のみ)。commit 7710925d。
本ファイルは委任_02 agentがWriteツールに拒否され作成できなかったため、委任_03で`docs/pm/RESULT_PACKET_JA_ASR.md`・`before_after_tables_02.md`・`eval_02_stdout.txt`・OPEN-319/333/334・DECISION_LOG委任_02エントリの事実のみを転記して作成した(新しい主張なし)。

## 1. 結論
- 限定Stage 1(署名一致のみ)の実run救済は3件(10代・1日・Melos Std)。Stage 1'で6件、Stage 2(読み展開)の実コーパス追加救済は0。
- 敵対的反例74件の誤PASSは全段階0。Before(現行Production)の誤PASS3件はTrial署名ガードで取消。
- 推奨: (a) 不規則読みはPASS_WITH_WARNING。採用するならStage 1+1'一体・追加型・閉リスト拡張不可。採用判断はUSER_DECISION_REQUIRED継続。

## 2. 必須修正5点の反映
1. 真値確認件数: ユニーク1組(`asr_root_cause_01/pre_regen_backup`由来のMelos Std三日間、HR承認済み)のみ。`run_e2e_01/a2`由来2件を含む残り5件は真値未確認(委任_01の「Melos三日間3」は真値3件の意味ではない)。
2. Stage 1'実装: `er066_ja_asr_orthographic_equivalence_01_trial.py`。
3. 根拠訂正: 「三日坊主回帰が再現しない」理由を「両側が同形に置換されるため」から「追加型(既存判定NGのときだけ動き、normalize_jaと_CLOSED_COUNTERS_JAを変更しない)ため」へ訂正。経緯は`er003_audio_tts_asr_safety.py` 484-499行(フル閉リスト化がnormalize_jaで「3日坊主」へ書換え、kakasiが数字を音声化せず読み一致フォールバックが壊れた)。Production実装条件: 閉リスト拡張方式では実装しない。
4. 残余リスク(a)/(b)の明示(7節)。
5. Status表記訂正(8節)。

## 3. Before / After 3列表(コーパス1,002ペア + 合成)
| 指標 | Before(現行Production) | Stage 1 | Stage 1' | Stage 2 |
|---|---|---|---|---|
| コーパス通過ペア数 | 752 | 759 | 762 | 762 |
| 実run由来の新規救済(累積) | 0 | 3 | 6 | 6 |
| うち不規則読み署名(WARN) | -- | 2 | 4 | 4 |
| 既存PASSの取消(Candidate E署名ガード) | -- | 0 | 0 | 0 |
| 正常例(合成47件)通過 | 14 | 38 | 40 | 47 |
| 敵対的反例74件の誤PASS | 3 | 0 | 0 | 0 |

- 実run救済6件の内訳: 不規則読み署名を含む(PASS_WITH_WARNING候補)4件 / 含まない2件。合成fixture由来の救済4件は別掲(`before_after_tables_02.md` B節)。
- Stage 1=署名一致の表記差のみ救済。Melos A2の2件(あと/後・つけ/付け併発)と`20％/20パーセント`(あと/後併発)は限定Stage 1では救済不可。
- Stage 2の追加は合成かな書きASR 7件のみ(正常例40->47)。
- 正常例のうちWARN(不規則読み署名)は10件。
- 反例74件=旧35+新規39(範囲・列挙・不正桁区切り・概数・時刻・序数かな書き・N分ぶ読み・一月/一時/一分・三日坊主ひらがな誤読・万単独)。Before誤PASS3件は全てCandidate E由来(三日間->三日目型)で、Trial層が新たに救済した反例は0件。
- 注: baselineは`expected_readings`/Resolver未使用のため「752件通過」は厳密なProduction値ではない。

## 4. Stage 1'の定義
両側の署名スパン(値署名が一致した数値+助数詞部分)を同一の不透明記号へ置換し、既存`classify_ja_asr_match`へ委ねる方式(読み表は不使用)。追加型であり、既存判定がNGのときだけ動く。`normalize_ja`と`_CLOSED_COUNTERS_JA`を変更しない。

## 5. 副次発見: normalize_ja範囲/列挙の誤PASS(OPEN-334)
現行Production `er007_ja_asr_validator_01.normalize_ja`が`〜`・`、`を除去した直後、`classify_ja_asr_match`の`c_norm == a_norm`でNORMALIZED_MATCHとなり、`protected_check_ja`(数字保護)に到達しない。実測(Resolver OFF、`before_after_tables_02.md` E節):

| 原稿 | ASR | 判定 | PASS |
|---|---|---|---|
| 3〜5日待つ | 35日待つ | NORMALIZED_MATCH | True |
| 3、4人来た | 34人来た | NORMALIZED_MATCH | True |
| 3、4日待つ | 34日待つ | NORMALIZED_MATCH | True |
| 1、2回試した | 12回試した | NORMALIZED_MATCH | True |
| 2〜3時間かかる | 23時間かかる | NORMALIZED_MATCH | True |
| 5〜10人来た | 510人来た | NORMALIZED_MATCH | True |
| 3~5日待つ(ASCII) | 35日待つ | PHONETIC_MATCH | True |
| 3～5日待つ(全角) | 35日待つ | PHONETIC_MATCH | True |
| 35日待つ(逆方向) | 3〜5日待つ | NORMALIZED_MATCH | True |

`3-5日`/`3,4日`/`3，4日`はTRUE_CONTENT_MISMATCHで止まる。実コーパス1,002ペアの原稿に「数字+〜/、+数字」は0件、実害の既知事例なし。Trialは無変更(修正対象外)で、特性化testは`er066_ja_asr_orthographic_equivalence_01_test_02.py` TestExistingProductionDefectCharacterization。修正案(未実装・Fable/ユーザー判断): 数字に挟まれた`〜`/`、`は除去しない、または除去前にnumber_mismatchを評価。

## 6. 曖昧語の非救済
一月に会う/1月、一時に会う/1時、一分待つ/1分、三分の一/3分の1、十分待った/10分待った は全てAMBIGUOUS_NO_RESCUE(曖昧語リストへ一時/一月/一分/N分の(ぶ読み)を追加済み)。

## 7. 残余リスクと対応案
- 最大の残余リスク(USER_DECISION_REQUIRED): 値は同じだが読みが誤った音声(さんにちかん/いちがつ/いっぷん/いちじ/ついたち・いちにち/はたち・にじゅっさい)をASRが算用数字で書けば通る。現行でもASRが漢字で書けばEXACTで通るため増分は限定的だがゼロでなく、実コーパスに負例0件で誤PASS率はオフラインでは原理的に測定不能(当初「日・人」除外理由と同根)。
- 対応案(a) 不規則読み署名(日1〜10/14/20/24、人1/2、歳20、つ、月/時の4/7/9)の救済はPASS_WITH_WARNINGとして最終試聴リストへ: 実run救済6件(うちWARN 4件を試聴リスト化)。**推奨**。
- 対応案(b) 不規則読み署名は対象外: 実run救済2件に減少(真値確認済みの1組Melos Std三日間も対象外になる)。

## 8. Status表記と採用前提
Status: Trial: 安全側=合成反例で誤PASS 0(オフライン限定) / 救済の有効性=PRELIMINARY(実run 6件、真値確認1件) / runtime evidenceなし / Production=未配線。「VALIDATED(オフライン・小標本)」から変更。
Production採用前の前提9項目(採用提案時):
1. feature flag既定OFF+rollback
2. 実装位置は`classify_ja_asr_match`内1箇所(number_mismatch検出後に追加型)
3. 例外時は既存判定へフォールバック
4. `expected_readings`/Ledger不一致時は救済しない
5. 救済ごとのtelemetry+最終試聴連動
6. 回帰test固定
7. CURRENT_SPEC文言
8. Family X/Z/B1横断適用
9. 閉リスト拡張方式では実装しない
(Opus推奨のうち反映: Candidate E取消ガード修正(片側かな書きは読み展開で比較、構造化フィールド前提、Stage 2/1'にも適用)、OPEN-333を重大度低へ、桁区切り3桁のみ、読み表誤り修正(6歳ろくさい等)、S1署名判定は「締める」側の言い直し。)

## 9. テストとstate_guard
- test_01 18件 + test_02 31件 = 49件全PASS。
- state不変確認: `state_guard_02.json`(changed=[])。
- 付帯: commit b46ec8b8の事後secret scan(--rev/--paths)hits=0。

## 10. 証跡一覧(`er066_output/ja_asr_orthographic_equivalence_01/`)
`before_after_tables_02.md` / `before_after_02.json` / `state_guard_02.json` / `eval_02_stdout.txt`。コード: `er066_ja_asr_orthographic_equivalence_01_{trial,cases_02,eval_02,tables_02,state_guard_02,test_02}.py`。委任ログ: `docs/pm/delegation_log/2026-10-13_JA-ASR-ORTHOGRAPHIC-EQUIVALENCE-COMPREHENSIVE-01_02.md`。
SSOT: OPEN-319 / OPEN-287 / OPEN-333(更新)、OPEN-334(新規)、DECISION_LOG委任_02エントリ。
