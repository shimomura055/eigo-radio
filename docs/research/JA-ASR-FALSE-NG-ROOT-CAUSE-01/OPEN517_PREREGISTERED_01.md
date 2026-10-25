# OPEN517_PREREGISTERED_01(OPEN-517是正案のAPI 0検証 事前登録。JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_05、2026-10-25)
## 0. 凍結
- 凍結対象=`proto_value_gate_fix_01.py` sha256 `ec2388f8856b57b7afd140ea6f7caeb87eb7c621482c3e615f15705bb2b91ff2`(評価script `eval_open517_api0_01.py` の作成・実行より前に固定。評価中・後に変更しない)。Production file(`er078_asr_unified_judge_01.py`/`er078_asr_value_guard_01.py`/`er007_*`)は無変更(`git status`で確認)。
- 評価データ=既存の保存済み転写のみ(P-4実attempt 421ユニーク[READING_MATCH PASSは133]・N-1 151対・N-3 30 clip[OpenAI転写]・正例対照47[er066 POSITIVE+POSITIVE_02]・月題/Melos Phase 3転写)。新規ASR/TTS/LLM 0=有料API 0・実費0円。socket guardでAPI呼出を例外化。
## 1. 是正案の定義(評価対象)
- F1: READING_MATCH(PHONETIC_MATCH/READING_RESOLVED_MATCH)のPrimary PASSにも最終ANDゲート(値ガードDIFF・否定差)を適用。値ガードDIFFまたは否定差=NG_PROTECTED、AMBIGUOUS=P3(Secondary)へ降格(=Productionの既存分岐と同一)。
- F2: かな書き『数詞(1〜10)+番/度』を漢数字表記へ統一してから値ガードへ渡す(値不変の等価表記。`いちばん`↔`一番`)。規則読み助数詞の閉集合{番,度}のみ。
## 2. 判定の定義
- 「現行」=Production現状(READING_MATCHは最終ゲートskip)。「是正後」=`apply_in_process()`(F1+F2をin-processで差替え。judge全経路を実際に通す)と、純関数`reading_match_final_gate()`の両方。
- 正常attempt=P-4の実attempt(現行でPASSしたもの全件。個別審査で誤PASSと確定したものを除く)と、正例対照(現行PASSのもの)。
- 既知負例=N-1の値/否定違い負例、N-3の実音声負例のうち、現行がREADING_MATCHでPASSしているもの(open517_value_gate_probe_01の9件: N1-er066a-028,N1-er066b-020,N1-er066b-022,N1-prodbug-006,N1-prodbug-007,N1-new-042,N1-new-044,N1-new-057,N3-02)。
- 「NG化」=現行PASS→是正後がPASS以外(NG_PROTECTED または P3降格[DEMOTE]を別集計。どちらも正常attemptでは0を要求)。
## 3. 合格基準(緩和禁止・厳格化可)
1. **増分誤NG=0**: P-4実attempt(現行READING_MATCH PASS 133)と正例対照で、現行PASS→NG_PROTECTED/DEMOTE = 0件。特に`comment_4_attempt1`の`いちばん低い`↔`一番低い`はPASSのまま。
2. **既知負例の是正**: 上記9件のうち**値/助数詞が実際に違う8件**(三日間/三日目×4・3~5日/35日×2・三日/さんにち・N3-02)はNG_PROTECTED、`一分`↔`いちふん`はDEMOTE(AMBIGUOUS)以上(=PASSのままは不可)。N3-02型(89,000 vs 8,900)・三日間/三日目・3~5日/35日が全てPASS以外になること。
3. **非回帰(判定全件表)**: 是正後(F1+F2、judge全経路)と現行で、全コーパスの最終state/ラベルを比較し、変化は①READING_MATCH PASS→(NG_PROTECTED/DEMOTE)(F1の意図)②F2の副作用(かな統一で値同一と判定され、現行の脱落DIFFが消える)のみ。それ以外の変化=0。F2の副作用が出た件は全件を個別提示し、値が実際に同一であることを確認する。EXACT/NORMALIZED等の非READING_MATCH PASS、およびNG→PASSへの変化(緩和方向。F2由来のP1解除を除く)は0。
4. **決定性**: 評価を2回実行して標準出力・出力JSONが完全一致。
5. **API 0**: socket guardが発動しない。費用0円。Production file変更0。
6. **取りこぼしの報告(基準ではなく開示)**: 現行READING_MATCH PASSのうち是正後もPASSする既存誤PASS(N3-07近音[Candidate E]・同形異音・助詞誤読など値ガードで原理的に検出不能な型)は件数と型を一覧し「F1/F2の対象外」と明記する。
## 4. 事前登録写像
- 基準1〜5を全て満たす → 「是正案=API 0検証PASS(Production適用はOpus軽量レビュー+ユーザー報告後)」。
- 基準1が1件でも不合格 → 除外規則(F2)の再設計(F2の対象拡大/変更はこのファイルに差分を追記し、再凍結してから再評価)。
- 基準2が不合格 → 検出不能型として原因提示、F1単独でも再評価。
- 到達上限=DEV/proto検証。Production適用は含まない。
## 5. 追記(F2 v1の評価結果と再凍結。基準1〜6は変更・緩和なし)
- F2 v1(`proto_value_gate_fix_01.py`、閉集合{番,度}の書換え。凍結・変更なし)をAPI 0評価(`eval_open517_api0_01.py`→`open517_api0_eval_01.out.json`、出力sha `ca60496f…`)した結果: **基準1不合格** = 正例対照の現行READING_MATCH PASS 6件(`三日間の旅`↔`みっかかんの旅`、`四月に会う`↔`しがつに会う`、`三人で行く`↔`さんにんで行く`、`百円です`↔`ひゃくえんです`、`七月に行く`↔`しちがつに行く`、`十代の若者`↔`じゅうだいの若者`)が、かな書き数詞の脱落DIFFでNG_PROTECTED化(F1適用時の副作用)。P4実attempt 133では`いちばん/一番`のみが対象で、F2 v1はこれを解消(P4のNG化0)。基準2(既知負例9件全てPASS以外)・非回帰(F1以外の変化0)は合格。
- 原因: 正しい読みのかな書き数詞(期待読み表にある読み)を、閉集合では網羅できない。→ F2を『期待読み表による汎用規則』へ再設計(**v2**、`proto_value_gate_fix_02.py` sha256 `31e6323503278b566ec56ff659a734358917c7f90ee27cfc2039a584d9ae84f0`、評価script `eval_open517_api0_02.py`/test `proto_value_gate_fix_02_test_01.py` 作成後・評価実行前に凍結)。ID特例ではなく、(値,助数詞)の期待読み(er066 Trial `_cands`)に完全一致するかな列のみ表記統一する規則。期待読みに無い読み(`さんにち`・`いちふん`)は統一されずNGのまま。
- 開示する限界: v2の設計は、同一コーパス(正例対照のv1不合格)を見た後の再設計であり、未知データでの汎化は未確認(評価データが同一である点を限界として結果に併記する)。基準・データ・判定は変更しない。F2 v1の結果は証跡として残し、v2の結果を最終とする。
## 6. 追記(F2 v2の評価結果と再凍結。基準1〜6は変更・緩和なし。基準3に『警告喪失0』を明文化=厳格化)
- F2 v2(`proto_value_gate_fix_02.py`、凍結・変更なし。`eval_open517_api0_02.py`→`open517_api0_eval_02.out.json`)の結果: 基準1=0・基準2=9/9合格。ただし基準3(非回帰)で副作用2点を検出: (1)`JA_NUMERIC_IRREGULAR_READING`警告(事後試聴対象)の喪失 8件(PASS_WITH_WARNING→PASS: ふたり/はたち/むいか/みっかぼうず/ついたち 等、KANA_NUMERALSで既にatom化済みの位置までv2が書換えたため)。(2)Primary NGのP1(値DIFF短絡)まで解除され NG_PROTECTED→Secondary呼出 6件(pos-025/027/029/042/043/044。Production挙動の拡大=是正の範囲外)。
- v3(`proto_value_gate_fix_03.py` sha256 `00c8c133a760a3e620e07e3b0d77c2d174cab70c29f1cf72d348b0004c9ef631`、評価script `eval_open517_api0_03.py`)で修正: V3-1=既atom位置は書換えない+統一前の警告を併合+統一で認識した不規則読み署名には同警告を付与、V3-2=F2をPrimary PASS(根拠READING_MATCH)の最終ゲートにだけ適用。評価前に凍結。
- 基準3の明文化(厳格化): 現行PASS→是正後PASSの件で、現行の警告が是正後に失われる件=0。非READING_MATCH経路(Primary NG/P1/Secondary gate)の判定変化=0。
- 開示する限界: v2/v3とも、評価データは同一コーパスで、v1/v2の不合格を見てから再設計している(未知データでの汎化は未確認)。
