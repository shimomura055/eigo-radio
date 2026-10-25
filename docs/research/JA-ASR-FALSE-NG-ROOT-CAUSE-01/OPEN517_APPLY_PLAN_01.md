# OPEN517_APPLY_PLAN_01(OPEN-517 F1+F2 v4 のProduction適用計画。JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_06、2026-10-25)
**本書は計画のみ。Production code/Prompt/CURRENT_SPEC/追補は一切変更していない。** 適用の可否はFableがOpus所見・`OPEN517_EVAL_02.md`・`OPEN517_PUBLIC_AUDIT_01.md`を見て判断し、ユーザーへは『報告+確認』の形で提示する。実装見積: 0.5〜1日相当・API 0・費用0円。
## 0. 適用前の位置づけ(11-8判定と報告)
- 判定: 不具合(T1)。コード(`er078_asr_unified_judge_01.py:68-73,526-530`)が`CURRENT_SPEC.md:2855`およびユーザー原文L97と矛盾。合格範囲を狭める(安全側)是正。ユーザー承認必須ではないが**報告必須**: (a)追補`DESIGN_02_ADDENDUM_01.md:65`(Fable採用OF-AUW-01、ユーザー個別承認は見つからない)との矛盾、(b)前回Opus条件A推奨を今回撤回する方向、(c)再生成・HR Lock増リスク(§8)。Fableが追補L65を『ユーザー承認済み仕様』と判断する場合は仕様変更=ユーザー判断。
- 事前条件(Opus): M-1〜M-5解消=本委任で充足(DESIGN_02・v4・基準7・未知データ・公開物監査)。
## 1. Production差分(最小・全て`er078_*`/`er007_*`の小変更)
| # | ファイル | 変更 |
|---|---|---|
| P1 | `er078_asr_value_guard_01.py` | (a)期待読み表を`er066 Trial _cands`から移設(約100行)+unit別逆引き表(n=1..20000、遅延生成)(b)`unify_kana_numerals`/`value_guard_kana_unified`(proto v4の純関数部分)を追加。Trial moduleをProductionがimportしない |
| P2 | `er078_asr_unified_judge_01.py` | (a)`APPROVED_EQUIVALENCE_BASES`から`"READING_MATCH"`を除く(コメントでOPEN-517・追補L65上書きを明記)(b)`_protected(canonical, text, lang, *, kana_unify=False)`に明示引数を追加(c)`:509`の呼出のみ`kana_unify=bool(pr.passed and pr.equivalence_basis == "READING_MATCH" and READING_MATCH_FINAL_GATE)`。Secondary側・他の`_protected`呼出は既定False |
| P3 | `er078_asr_unified_judge_01.py` | **1行rollback用module定数** `READING_MATCH_FINAL_GATE = True`(env/flag/起動script不可。Falseで`READING_MATCH`を承認基底へ戻し`kana_unify`をFalseにする=現行挙動へ完全復元)。flagではなく『単一merge/1行revert』の運用(OF-AUW-02踏襲) |
| P4 | `er007_ja_secondary_asr_01.py:407` | コメント『READING_MATCH等の承認済み根拠は再否定しない』を『HOMOPHONE_MATCH_NUMBER_EXCEPTION・TIER1_*は再否定しない。READING_MATCHは最終ANDゲートを適用(OPEN-517)』へ更新(コメントのみ) |
Production挙動の変化=『READING_MATCHのPrimary PASS+値DIFF/否定差 → PASS→NG_PROTECTED(Secondary不呼出・次slot)、AMBIGUOUS→P3降格、正しいかな書き数詞→PASS維持(警告付与の場合あり)』のみ。X/Z/Y/legacy共通(JA経路)。英語・他の承認根拠(HOMOPHONE_MATCH_NUMBER_EXCEPTION/TIER1_*)は不変。
## 2. 期待読み表移設のparity test(R-6)
- 移設後の表と`er066 _cands`を `n in 1..20000 × 全unit`で突合し、**意図差分のみ許す**: ①`WEAK_KANA_NUMERALS`(なのか/ようか/とお)の読みを置換候補から除外 ②同unit内で値が一意でない読みを除外。この2種以外の差分0をtestで固定(差分の個数と内容を期待値として列挙)。
## 3. testの更新・追加(R-5)
更新(既存): `er078_asr_unified_judge_01_test_01.py:56-57`(`test_final_gate_does_not_reject_approved_equivalence`がAPPROVED集合をparametrize→READING_MATCHが集合から外れるため、別testで『READING_MATCHは最終ゲートを受ける』を固定)、`er078_asr_unified_ja_wiring_test_01.py:194-195`(`approved_equivalence`でskipを期待→`final_gate.applied==True`・reason=`primary_pass`へ)。
新規: (1)既知負例9件+月題1件がNG_PROTECTED/DEMOTE (2)正常143件(P4+正例)のPASS維持 (3)basis別: `PHONETIC_MATCH`由来READING_MATCHと**`READING_RESOLVED_MATCH`(LLM resolver)由来READING_MATCH**の両方にF1/F2 (4)**Candidate E由来PHONETIC_MATCH**(`er011_ja_asr_variant_layer_01.py:347-372`)のREADING_MATCHにも値ゲートが働くこと (5)**`force_secondary=True`経路**(minimal fallback/LR後v1): Primary PASS(READING_MATCH)+値DIFFがSecondary呼出前にNG_PROTECTED、値OKはSecondary 1回の既存挙動 (6)`_ortho_unlock_primary`が`lang!="en"`でNone→JA READING_MATCHはspan解除されず従来どおりNG_PROTECTED(`er078_asr_unified_judge_01.py:370-378`) (7)合成負例一式=`proto_value_gate_fix_04_test_01.py`の`M2_NEG`/`M3_NEG`/`SOKU_NEG`/`TWIN_NEG`/`NEGATION_NEG`をProduction関数へ移植 (8)M-4: Primary NG(P1)・Secondary gateでF2無効、`negation_diff`は元テキスト (9)単調性ガードの人為無効化test(proto test移植) (10)DefaultOff不要(承認済み是正のためflag無し)だが、`READING_MATCH_FINAL_GATE=False`で現行判定が完全復元することのtest (11)全er078/er007 regression+静的監査(`unlisted_new_calls`/`vanished`/`count_changed`が空)。
## 4. reason文字列の下流影響調査(R-5。Grep実施済み)
- `primary_pass_approved_equivalence:READING_MATCH` → READING_MATCH PASSは今後`primary_pass`になる(承認根拠でないため)。`Grep "approved_equivalence|primary_pass_approved|APPROVED_EQUIVALENCE_BASES" *.py`(2026-10-25): production codeで依存するのは`er078_asr_unified_judge_01.py:68,526,530,559`のみ。他は**test**(`er078_asr_unified_judge_01_test_01.py:56-57`、`er078_asr_unified_ja_wiring_test_01.py:195`)と、**研究script**(`er109_b_fix_before_after_01.py:32`、`er109_gate_exposure_01.py:34`、`er109_pattern_probe_01.py:196`、`er109_stored_onoff_compare_01.py:47`、`er109_xz_scope_01_test_01.py:183`[ORTHO_BASISが集合に無いことのtest=影響なし])。研究scriptは過去実験の再実行時に集合を読むだけで、Production経路ではない。
- `final_gate.skipped`/`final_gate.applied`の消費者: 集計script(`er078_auw_aggregate_06b/06d.py:69`、`er078_auw_tabulate_06b.py:23`)はREADING_MATCHの`skipped`を特別扱いしていないことをGrepで確認(`fg = aj.get("final_gate")`の読取のみ)。allowlist(`er078_asr_unified_wiring_allowlist_01.json`)は呼出点の列挙で文字列を持たない。
- 再利用guard(`er078_reuse_value_guard_01.py:19`の`PROTECTED_REASON_PREFIXES`に`final_gate_value_diff`あり): F1適用後、保存転写の再判定でREADING_MATCH PASS+値DIFFのentryが`blocked`(再生成)になる。監査上の過去該当は0(`OPEN517_PUBLIC_AUDIT_01.md`)で増分はほぼ無い。
## 5. SSOT更新文案(適用時。本委任では変更しない)
- `DESIGN_02_ADDENDUM_01.md:65`: 末尾へ追記『**(2026-10-xx OPEN-517で上書き)**: `読み一致(READING_MATCH)`は本項の対象から外す。READING_MATCHのPrimary PASSにも最終ANDゲート(値DIFF/否定差=NG_PROTECTED、AMBIGUOUS=P3)を適用し、正しいかな書き数詞は値同一として維持する(`OPEN517_DESIGN_02.md`)。元の理由『承認済み救済が値ガードで無効化される(誤NG防止)』はかな数詞表記統一(F2)で手当てした。』。本文の『、読み一致』は削除せず取消線相当の注記で履歴を残す(既存行は書き換えず追記)。
- `CURRENT_SPEC.md`: L2850直後に1行追記『Status追記(OPEN-517適用): `READING_MATCH`はAPPROVED_EQUIVALENCE_BASESから除外し最終ANDゲートを適用(追補§1-3の上書き)』。L2855は既存文のまま(コードを合わせる)。
- `DECISION_LOG.md`: 適用時に『OF-AUW-01(Fable採用)のうち読み一致skipをOPEN-517で撤回。理由=CURRENT_SPEC:2855・ユーザー原文L97との矛盾(11-8 T1)。ユーザー報告済み。Opus条件Cレビュー・API 0評価・公開物監査は`docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/`』を記録。
- `OPEN_ITEMS.md` OPEN-517: Status=適用済み(Production適用の別委任後)。
## 6. 適用後初回runの集計(R-3)
- 対象: 適用後の最初の本番run(X/Z/Y/legacyのJA)。`tts_generation_results.json`の`attempts_log[*].asr_judgement`から(API 0): (a)`reason_code=="final_gate_value_diff"`かつ`primary.equivalence_basis=="READING_MATCH"`の件数、(b)`reason_code=="primary_pass_demoted_ambiguous_value"`かつ`READING_MATCH`の件数(P3降格)、(c)(a)(b)のうち最終slot(slot3)に到達してHR Lockに入った数(`review_lock_state.json`)、(d)F2発動(`PASS_WITH_WARNING`でwarning=`JA_NUMERIC_IRREGULAR_READING`が新たに付いた数)。集計は`open517_public_audit_01.py`のA節ロジックを流用した読取専用scriptで行い、結果を`OPEN_ITEMS.md` OPEN-517へ1行記録する。異常値(例: (a)が1runで3件超)ならrollback定数(P3)を検討しFableへ報告。
## 7. 別OPEN登録(既知の限界。F1/F2では悪化しない・変わらない)
1. **R-7 助数詞表外(`晩`等)**: `七晩`↔`七番`のように助数詞表(`COUNTERS`)に無い語はatomにならず`UNKNOWN`素通し。分類=既知の限界(拡張はB-light/助数詞表拡張の別判断)。
2. **弱いかな数詞のUNKNOWN素通し**: `なのか`/`ようか`/`とお`を含む文は値ガードが`UNKNOWN`を返し、値が違ってもPASS(例: 原稿`6日`↔転写`なのか`。系統スイープで34件=B/B_rev各17。現行Productionも同じ)。分類=既知の限界/修正候補(11-8: 承認済み安全条件[値の最終確認]との整合を満たさない型だが、弱い読みを一般語と区別する根拠が現状無いため、Fable判断で『修正へ進む』か『許容』か決める)。
3. **`KANA_NUMERALS`の語境界欠如**: `にじゅうよっか`内の`よっか`を4日atomと拾い、原稿`4日`↔`にじゅうよっか`が現行からEQUAL(=PASS)。分類=修正へ進む(既存の値ガードの小修正[語境界lookaround]+test。F1/F2とは独立なので別委任)。
(新規OPEN番号は`OPEN_ITEMS.md`に登録。)
## 8. リスクと影響(隠さない)
- 再生成: 真の値違い(READING_MATCHで通っていたもの)がNG_PROTECTED→次slotでTTS再生成(retry消費)。実コーパスでの該当は既知負例のみで、正常143件・未知96件のNG化は0。実運用での頻度は低いと推定(公開物監査0件)だが、証明ではない。
- HR Lock増: 最終slotでも値DIFFが残る真の誤読のみ。正常音声のLock入りは実測0。
- `一分`↔`いちふん`型のDEMOTE(P3)はSecondary 1回を増やす(費用微増。Azure秒数ベース)。実運用の最終結果はAzure転写次第。
- 誤NG: かな書き数詞のうち期待読み表に無い『正しいが珍しい読み』は置換されずNG/DEMOTEになり得る(例: `いつか`=5日はProduction現行のAMBIGUOUS設計でDEMOTE)。警告付与でなくNGになるため、適用後の初回run集計(§6)で観察する。
- ロールアウト: 単一commit/merge(squash禁止)、revert=1個。rollback=P3定数をFalse(1行)または当該commitのrevert。
## 9. 実装の順序(適用が決まった場合)
P1(表移設+parity test)→P2/P3→test更新・追加→全er078/er007 regression→静的監査→SSOT更新→commit/push→§6の集計準備。API 0・費用0円。Opus再レビューは不要(本委任のM-1〜M-5反映で条件Cを満たす。Fable判断)。
