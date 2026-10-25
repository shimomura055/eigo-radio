# OPEN517_EVAL_02(OPEN-517是正案 F1+F2 v4 のAPI 0評価。委任_06、2026-10-25)
事前登録=`OPEN517_PREREGISTERED_02.md`(§0〜§4。§4=評価判定前のv4初版欠陥1件の修正記録)。評価=`eval_open517_api0_04.py`(proto v4 `proto_value_gate_fix_04.py` sha `19aea160aa4bb4b45ec4e8094cc7eac5c58a9bfc8e3bd866208dd75fc4fa4dfa`)。**API 0(socket guard)・LLM/ASR/TTS呼出0・費用0円・Production file変更0**(`git status`で`er078_*`/`er007_*`/`er066_*`/`CURRENT_SPEC.md`/`DESIGN_02_ADDENDUM_01.md`無変更を確認)。使用モデル: なし(保存済み転写のみ。転写元は既存のOpenAI `gpt-4o-mini-transcribe`/Azure ja-JP)。再現: リポジトリrootで`PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/eval_open517_api0_04.py`。2回実行で標準出力・出力JSONが完全一致(`cmp`)=決定的。出力JSON=`open517_api0_eval_04.out.json`(sha `ea097581c7eb…`)。
評価方式: Productionのadapter(`evaluate_attempt_ja_with_cascade_detail`→`unified_judge`)を実際に通し、in-process差替え(`apply_in_process`)で現行 / v3 / v4 を比較。Secondary(Azure)はstub(呼出0。DEMOTE時の`NG_SECONDARY_UNAVAILABLE`はstubの表示)。
## 1. 基準別の結果
| 基準 | 結果 | 合否 |
|---|---|---|
| 1 増分誤NG=0(P4 133+正例10=現行READING_MATCH PASS 143件) | NG化/降格 **0**。`comment_4_attempt1`の`いちばん低い`↔`一番低い`はPASSのまま | 合格 |
| 2 既知負例9件がPASS以外 | **9/9**(NG_PROTECTED 8、`一分`↔`いちふん`=DEMOTE) | 合格 |
| 3 非回帰(全1,264件) | 変化13件=F1 10件(PASS→NG)+F2警告追加3件(PASS→PASS_WITH_WARNING)。**非READING_MATCH PASSの変化0・NG→PASS 0・警告喪失0・other 0** | 合格 |
| 4 決定性 | 2回実行で完全一致 | 合格 |
| 5 API 0・費用0円・Production変更0 | 確認済み | 合格 |
| 7 合成負例一式=全件PASS以外 | `proto_value_gate_fix_04_test_01.py` **19 passed**。M2_NEG 5件(うち3件はv3が実際にPASSした反例)・M3_NEG 7件・SOKU_NEG 5件・TWIN_NEG 4件・NEGATION_NEG 3件が全てNG_PROTECTED/DEMOTE、正例(さんぼん・みっかかん・二十四日↔にじゅうよっか等)はPASS | 合格 |
| 8 未知データ | 下記§3。判定変化0・誤NG0。**ただし反証機会が実質無い**(開示) | 合格(限定) |
| 9 F2発動全件+値同一 | 下記§4。7件(全て正常143件の内)。機械確認(a/b/c)失敗0。fallback 0 | 合格 |
## 2. 判定が変わった全件(現行→v4、1,264件中13件=既存771件中13件、未知データ0件)
v3の13件(`OPEN517_EVAL_01.md` §2)と**完全に同一**(v3→v4差分0件)。内訳: 既知負例8件(NG_PROTECTED 7[N1-er066a-028, N1-er066b-020, N1-er066b-022, N1-prodbug-006, N1-prodbug-007, N1-new-044, N1-new-057])+DEMOTE系1件(N1-new-042 `一分`↔`いちふん`)+N3-02(`8,900`↔`八万九千`)+月題実転写1件(`8000九百本超`)+F2警告追加3件(pos-022 `みっかかん`/pos-024 `しがつ`/pos-032 `しちがつ`)。全件の表=`open517_api0_eval_04.out.json`の`rows`(`base_state`/`fix_state`)および`OPEN517_EVAL_01.md` §2(同一内容)。
**v3→v4で実コーパス上の判定は変わらない**。v4の意味は『v3が実コーパスに現れなかった穴(M-2/M-3)を持っていたことを合成負例と系統スイープで実証し、塞いだ』点にある(§5)。
## 3. 未知データ評価(R-1。基準8)
- **列挙方法**: `collect_unknown_pool_02.py`(機械的、全件、選別なし)。出典S1=`tts_generation_results*.json`のattempts_log、S2=`attempts/*.json`、S3=`human_review_queue.jsonl`のopenai_asr step、S4=docs/research・er*_output配下のjson(l)で`canonical系`+`asr_text系`キーを持つ日本語record。走査2,303 record、うち既存771件のキーと一致する1,336を除き、重複(canon,Primary転写)を畳んで**未知493件**(`unknown_pool_02.json`)。
- **内訳**: 出典はlegacy/その他488件(`audio_retry_cascade_prod_01` 140、`pool_pilot_01` 96、`n3_01` 27、`unified_all_roles_production_wiring_01` 25、`ja_support_calm_style_trial_04` 22 他)+X 5件。**X/Z/Yの直近runのattemptは、既存771件のP4(attempt_pool_01、421ユニーク)に既に含まれており未知ではない**(要求書の「X/Z/Y直近run」はコーパス内)。現行ラベル: TRUE_CONTENT_MISMATCH 196・NORMALIZED_MATCH 132・**PHONETIC_MATCH 96**・EXACT_MATCH 60・ASR_VALIDATION_UNCERTAIN 9。
- **結果**: `apply_in_process()`(F1+F2 v4、judge全経路)の判定変化 **0件**(現行PASS 288[PASS 280+WARN 8]→同、NG 205→同)。F2発動0件。
- **開示(反証機会)**: 未知データの現行READING_MATCH PASS 96件を値ガードで見ると **NO_VALUES 74・EQUAL 22・DIFF 0・UNKNOWN 0**。数値を含む文はあるが全て値が一致(漢数字↔算用数字、`子ども`↔`子供` 等)で、**F1が止めるべき値違いも、F2が働くべきかな書き数詞も含まれない**。したがって未知データは『誤NG(増分)が出ないこと』の確認(96件で0)にはなるが、F1/F2の検出力・F2の汎化の検証にはならない。これを補う目的で§5の系統スイープを追加した。
## 4. F2発動全件(基準9)
既存771件で7件、未知493件で0件。7件は全て正常143件の内(P4 1件+正例対照6件)。**全件で機械確認(a)置換後のpartner atom表層が置換前のpartner atomと同一、(b)置換したかな列が当該unit内の逆引き表(n=1..20000)で当該値にのみ対応、(c)F2後のpairがEQUAL、を満たす**(失敗0)。monotonic guardによるF2前結果への巻戻し(fallback)は0件。
| ID | 原稿 | 転写 | 置換 | 置換側 | 結果(現行→v4) |
|---|---|---|---|---|---|
| comment_4_attempt1(P4) | …体の活動がいちばん低い… | …体の活動が一番低い… | `いちばん`→`一番`(値1・ban) | 原稿 | PASS→PASS |
| pos-022 | 三日間の旅 | みっかかんの旅 | `みっかかん`→`三日間` | 転写 | PASS→PASS_WITH_WARNING(不規則読み警告) |
| pos-024 | 四月に会う | しがつに会う | `しがつ`→`四月` | 転写 | PASS→PASS_WITH_WARNING |
| pos-026 | 三人で行く | さんにんで行く | `さんにん`→`三人` | 転写 | PASS→PASS |
| pos-028 | 百円です | ひゃくえんです | `ひゃくえん`→`百円` | 転写 | PASS→PASS |
| pos-032 | 七月に行く | しちがつに行く | `しちがつ`→`七月` | 転写 | PASS→PASS_WITH_WARNING |
| pos-036 | 十代の若者 | じゅうだいの若者 | `じゅうだい`→`十代` | 転写 | PASS→PASS |
正常143件(P4 READING_MATCH PASS 133+正例10)のうちF2発動は7件(P4 1・正例6)。
## 5. 補助: 系統スイープ(基準ではなく開示。`sweep_open517_04.py`、結果=`sweep_open517_04.out.txt`)
助数詞29種×値46個の期待読みを機械的に総当たり(約1.5万ケース。原稿数字↔転写かな[A]/逆向き[C]/誤った値のかな読み[B,B_rev]/2atom文[D])。
- **誤NG**(正しい読みなのにPASS以外): A/C/D_ok で計3件、全て`いつか`(5日。曖昧語atomとして現行からAMBIGUOUS→P3降格=Production現行の設計)。v4初版では`5日間`↔`いつかかん`が追加で誤NG化(v3はPASS)していたため、V4-5(曖昧かな数詞の吸収許可)で修正済み(`OPEN517_PREREGISTERED_02.md` §4)。
- **F2起因の誤PASS = 0**: D_ng(2atom文で他方の値が違う)1,341件全てNG_PROTECTED、B/B_rev(誤った値のかな読み)10,504件のうちPASSは各17件(計34件)のみで、**全て弱いかな数詞`なのか`(7日)/`ようか`(8日)を含む文**(例: 原稿`6日`↔転写`なのか`)。これは**F2が発動しない(弱い読みは置換候補から除外)状態で、F2前の値ガードが`UNKNOWN`(弱いかな数詞を『数詞が相手側にある』と見て素通し)を返す既存の挙動**で、v3・現行Productionでも同数(17+17)。F1/F2では変わらない既知の限界(`OPEN517_APPLY_PLAN_01.md` §7、新OPEN候補)。
- v3比較: v3の誤PASSも同じ34件(v3はスイープの2atom文では誤PASSなし)。v3の穴(M-2/M-3)は実コーパスには現れないが、合成文では再現した(例: `とおくの町で7日`↔`とおくの町で8日、なのか`=v3 PASS・v4 NG、`10人`↔`さんじゅうにん`=v3 PASS・v4 NG、`8日に会う。7日も`↔`どうしようか。8日に会う。7日も`=現行PASS[値ガードEQUAL]なのにv3は誤NG・v4はPASS)。
## 6. 限界(隠さない)
1. 未知データは値ガード上すべてEQUAL/NO_VALUESで、F1/F2の検出力・汎化の実コーパス検証にはならない(§3)。汎化は合成スイープ(§5)と合成負例test(基準7)で補った。
2. v1→v4は同一の既存コーパスを見て再設計した履歴。v4初版の欠陥1件はスイープで発見・修正(§5、PREREGISTERED_02 §4)。
3. `一分↔いちふん`のDEMOTEはSecondary stubの結果(`NG_SECONDARY_UNAVAILABLE`表示)。実運用ではAzure転写次第(PASSなら`PASS_WITH_WARNING`、NGなら`NG_BOTH`)。
4. 取りこぼし(F1/F2対象外)は`OPEN517_EVAL_01.md` §4と同一(是正後もPASSのREADING_MATCH PASS 259件。値ガードで原理的に検出不能な型+弱いかな数詞UNKNOWN+語境界欠如の既存の穴[`4日`↔`にじゅうよっか`=EQUAL])。
## 7. 結論
事前登録基準1〜5・7〜9を全て満たす → **F1+F2 v4 = API 0検証PASS(DEV/proto)**。未知データは検出力の検証にならない旨を併記。Production適用の可否はFable判断+ユーザー報告後(`OPEN517_APPLY_PLAN_01.md`)。
