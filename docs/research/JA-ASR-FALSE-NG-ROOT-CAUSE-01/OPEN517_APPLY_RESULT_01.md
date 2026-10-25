# OPEN517_APPLY_RESULT_01(OPEN-517 F1+F2 / OPEN-523 / OPEN-524 のProduction適用結果。JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_07A、2026-10-25)
**区分: 承認済み不具合是正(PM_GOVERNANCE 11-8 T1)であり、新しい合格条件の導入ではない。** 根拠=2026-10-25ユーザー指示(`docs/pm/delegation_log/2026-10-25_JA-ASR-FALSE-NG-ROOT-CAUSE-01_USER_02.md` §③『承認済み安全条件が正しく機能するよう修正する』『Productionへ反映する際は、承認済み不具合修正の範囲か、新しい合格条件の導入かを区別する』『純粋な実装不具合修正は新仕様採用と区別』)。
API 0・有料run 0・実費0円。Statusは**APPLIED(Production適用済み・初回run集計待ち)**。`VALIDATED→Production採用`の新仕様採用ではない。Candidate E(OPEN-333)・助数詞表(OPEN-522)・公開物・`er0XX_output/`は変更していない(遡及再判定なし)。
## 1. 区分の説明(不具合是正か、新合格条件か)
- 承認済み安全条件=`CURRENT_SPEC.md:2855`『最終ANDゲートは採用しようとする転写すべてに値ガードDIFF・否定差が無いことを独立に再確認する。重大内容差を警告だけで解放しない(原文L97)』。旧コード(`er078_asr_unified_judge_01.py:68-73,526-530`)は`READING_MATCH`のPrimary PASSでこの最終ゲートをskipしており、**承認済み条件が機能していなかった**(追補`DESIGN_02_ADDENDUM_01.md:65`はFable採用OF-AUW-01でユーザー個別承認なし)。
- 是正後のPASS集合 ⊂ 是正前のPASS集合(F1+F2+OPEN-523/524はいずれも合格を狭める/維持するのみ)。API 0再評価で『NG→PASS(広がり)=0』を実測(§4)。よって**新しい合格条件ではない**。OPEN-523/524も『承認済み安全条件[値の最終確認]が一部の入力で機能していなかった』実装不具合であり、狭める方向のみで同じ区分。
## 2. 変更一覧(Production差分)
| file | 行 | 内容 |
|---|---|---|
| `er078_asr_unified_judge_01.py` | +27/-5 | (a)`APPROVED_EQUIVALENCE_BASES`から`READING_MATCH`除去+`READING_MATCH_BASIS`・**rollback定数`READING_MATCH_FINAL_GATE = True`**(b)`_protected(canonical,text,lang,*,kana_unify=False,info_out=None)`(F2は明示引数のみ。`negation_diff`は常に元テキスト)(c)Primary PASS最終ゲートの`_protected`呼出だけ`kana_unify = READING_MATCH_FINAL_GATE ∧ pr.passed ∧ basis=="READING_MATCH"`(Secondary・Primary NG・KPは既定False)(d)`approved`はrollback定数False時のみREADING_MATCHを含む(e)F2置換があれば`audit.value_guard.kana_unify`を追記(R-3集計用) |
| `er078_asr_value_guard_01.py` | +425/-5 | (a)期待読み表を`er066 _cands`周辺(L114-280)から移設(`_er_cands`等。Production→Trial import無し)+unit別逆引き(n=1..20000、遅延生成)+`expected_reads`(弱い読み・非一意読み除外)(b)F2: `unify_kana_numerals`/`value_guard_kana_unified(_detail)`/`KanaUnifyInfo`(v4のM-2(a)(b)・M-3最長一致境界・単調性ガード)(c)**OPEN-524**: `embedded_in_larger_reading`+定数`KANA_WORD_BOUNDARY_CHECK=True`(かな数詞が『より大きいかな数詞の一部』なら部分一致印=他atomと不一致[DIFF]。みっか+かん=3日間も部分一致扱い)(d)**OPEN-523**: `_weak_kana_compatible`+定数`WEAK_KANA_REGION_COMPAT=True`(弱いかな数詞は脱落atomの値と一致しうるときだけ数詞の証拠。それ以外は従来のDIFF(b)判定へ)|
| `er007_ja_secondary_asr_01.py` | +2/-2 | コメントのみ(L407『READING_MATCH等は再否定しない』→『HOMOPHONE_MATCH_NUMBER_EXCEPTION・TIER1_*は再否定しない。READING_MATCHは最終ANDゲートを適用』、L426) |
| test | | 既存更新: `er078_asr_unified_ja_wiring_test_01.py::test_reading_match_is_subject_to_final_gate_and_passes_when_no_diff`(旧`test_approved_reading_match_is_not_renegated_by_final_gate`。skip期待→applied=True・reason=`primary_pass`)。`er078_asr_unified_judge_01_test_01.py:56-57`の`test_final_gate_does_not_reject_approved_equivalence`はAPPROVED集合のparametrizeのため無変更でPASS(READING_MATCH欠落分は新testが固定)。新規`er078_asr_value_guard_kana_unify_test_01.py`(44件) |
| DEV proto | | `proto_value_gate_fix_04.py`(`_prot(**kw)`)・`proto_value_gate_fix_01/04_test_01.py`: Production適用で『適用前の穴/元の集合』前提が変わった4 testを、定数Falseで適用前を再現する形へ最小更新(proto 5群 計49件PASS) |
`er007`のadapter本体(`basis = "READING_MATCH" if ...`)・`unified_judge`の他分岐・Secondary・KP vote・EN・`er109`/ortho・`er078_reuse_value_guard_01.py`(`PROTECTED_REASON_PREFIXES`に`final_gate_value_diff`あり=F1適用後、保存転写の再判定でREADING_MATCH+値DIFFのentryは`blocked`=再生成。コード変更不要を確認)は無変更。
## 3. 既存仕様整合・影響調査(照合した箇所)
- `CURRENT_SPEC.md:2855`(最終ANDゲート)・ユーザー原文L97へ**コードを合わせた**(L2855は不変)。追補L65は上書き注記(SSOT更新参照)。
- reason文字列: `primary_pass_approved_equivalence:READING_MATCH`→`primary_pass`。Grep(`approved_equivalence|primary_pass_approved|APPROVED_EQUIVALENCE_BASES`、*.py): production依存は`er078_asr_unified_judge_01.py`のみ。他はtest(更新済み)・DEV研究script(`er109_*`は`READING_MATCH`を参照せず[Grep 0件]、EN専用=影響なし。`eval_open517_api0_01〜03`は`_rs`で両表記を同一視、`open517_public_audit_01.py`は過去runの`approved_equivalence:READING_MATCH`を読む専用=不変)。
- 既定値Grep: `READING_MATCH_FINAL_GATE = True`/`KANA_WORD_BOUNDARY_CHECK = True`/`WEAK_KANA_REGION_COMPAT = True`。env/flag/起動scriptでの切替なし(testで固定)。承認済み不具合是正のためflag化・Default Off隔離は不要(11-7の適用外=新仕様ではない)。
- 既存のretry/fallback/Gate: NG_PROTECTEDはSecondary不呼出で次slot(既存設計)。DEMOTE(AMBIGUOUS)はP3(Secondary 1回)。`force_secondary`(LR後v1)も最終ゲートがSecondary前に作用(test固定)。Gate・上限回数・resume/HR Lockの機構は無変更。
## 4. API 0再評価(`eval_open517_api0_prod_01.py`、出力=`open517_api0_prod_01.out.json`/`.out.txt`。2回実行で出力sha256同一=`eca28287…f5ee`、決定的)
| 項目 | 結果 |
|---|---|
| (A)既存771+未知493=1264件: Production(523/524 OFF)とproto v4保存値の差分 | **0** |
| (A) Production(523/524 ON)とv4の差分 | 1件(N1-er066b-021『三日目』↔『みっかかん』: v4=NG_SECONDARY_UNAVAILABLE[Secondaryはstub]→NG_PROTECTED p1_value_diff。目と間の違い=真の値違いでOPEN-524が値DIFFとして検出。**NG→NG**、PASSへの広がりなし) |
| (B)合成15,877件(系統スイープ+基準7合成負例24+OPEN-523/524例+受入例): OFF とv4の差分 | **0** |
| (B) ON とv4の差分 | 42件=全て『PASS→NG_PROTECTED』(狭まり)。広がり0。内訳: 弱いかな数詞(なのか/ようか/とお)と別値の組 34件+O523固定4、かな数詞部分一致(にじゅうよっか↔4日等)O524固定4 |
| 正常143件(P4+正例のREADING_MATCH PASS)のNG化(ON) | **0** |
| 既知負例9件(READING_MATCH PASS) | 9/9 PASS以外 |
| 現行READING_MATCH PASS 269件→是正後もPASS | 259件(10件=既知負例9+月題1) |
| NG→PASS(広がり) | **0** |
| 未知データ493件の判定変化 | **0**(検出力が不足している旨はOPEN517_EVAL_02に開示済み) |
| 基準7合成負例24件(M-2〜M-5)をProduction関数で | 24/24 PASS以外 |
| 合成誤PASS(B/B_rev/D_ng) / 誤NG(A/C/D_ok) | 誤PASS 0 / 誤NG 3(いつか=5日。仕様のDEMOTE_P3[someday衝突]。v4も同数=悪化なし) |
### 受入項目の個別結果
| 受入項目 | 結果 |
|---|---|
| 8,900↔89,000 | N3-02『月のしわ、8,900本超』↔『月野氏は八万九千本町。』: 現行PASS→**NG_PROTECTED(final_gate_value_diff)**。合成『8,900本です』↔『89,000本です』も遮断 |
| しわ↔すわ | N3-07『月の巣は八千九百本長。』は**PASS維持**(値は8,900で同一。Candidate E[OPEN-333]の近音救済による別問題で、本是正では遮断されない=事実。OPEN-333の範囲) |
| みっか↔さんにち | N3-21『三日待った』↔『三日間待った。』は元からNG_PROTECTED。『三日待ちます』↔『さんにち待ちます』=NG_PROTECTED(F1)、『みっか待ちます』=PASS(正しい読み)。`さんにち`は期待読み表に無い非標準読みのため遮断(必要に応じて区別) |
| 正常月題の救済 | 『月のすわ、8,900本超』等の値同一はPASS維持。正常143件NG化0 |
| 既存負例に悪影響なし | 9/9遮断維持。広がり0 |
| 正しい音声を不要にNGにしない | 正常143件・未知データでNG化0。合成の正しいかな読み(A/C/D_ok 4,011件)は誤NG 3(いつか)のみ=v4と同一 |
## 5. 回帰(全てネットワーク遮断harness`netblock_harness_01`+`.venv`)
- 新規`er078_asr_value_guard_kana_unify_test_01.py` 44 PASS。DEV proto 49 PASS。
- er078/er007/er066/er109系+JA ASR関連+Family Y(er121)の対象58 file+6 file(約1,930件): 1,916 PASS / 13 FAILED。**13件の分類**:
  - 既存の失敗でありF1+F2+523/524と無関係(全定数OFFで同一に失敗を確認): er007_ja_secondary_asr_01_test 2件(HEADのみのworktreeでも失敗)、er103_run_entity_table_test_01 5件(英語RET)、er109_xz_isolation_01_test_01 2件(`er118`/`er121`の追加による固定リスト不一致)、er109_wiring_golden_test_01 3件(英語KP行の署名差。HEADのみのworktreeでも同一失敗)。
  - `er020_*ProductionModuleUnchangedTest` 2件: 『`er007_ja_secondary_asr_01.py`に未commit差分が無い』を要求するため、commit前は必然的に失敗(commit後に解消。commit後に再実行して確認する)。
  - er121 2件: 別agent(Family Y)が並行編集中の不安定test(単独再実行では別のtestが失敗=編集途中)。ASR非関連。
- 外部接続: harnessログでapi.openai.comへの接続**試行が9件(遮断済み、既存testのうち上記失敗test由来)**、評価script・新規testは0件(個別実行でログ未生成)。有料API到達0。
## 6. R-3: 適用後の初回run集計手順(API 0・読取専用)
`PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/open517_first_run_tally_01.py <run_dir>`(smoke確認済み)。(a)`final_gate_value_diff/negation_diff`かつREADING_MATCH件数 (b)P3降格(`primary_pass_demoted_ambiguous_value`)件数 (c)(a)(b)のうちHR Lock入り (d)F2発動(`value_guard.kana_unify.fired`)・`JA_NUMERIC_IRREGULAR_READING`付与PASS (e)OPEN-523/524由来pair件数。結果は`OPEN_ITEMS.md` OPEN-517へ1行記録。**異常値(例: (a)が1runで3件超)なら自動rollbackせずFableへ報告**し、rollback定数の判断を仰ぐ。
## 7. rollback手順
- F1+F2一括: `er078_asr_unified_judge_01.py`の`READING_MATCH_FINAL_GATE = True`→`False`(1行)=READING_MATCHが再び承認基底扱い・F2無効・reason=`primary_pass_approved_equivalence:READING_MATCH`(旧挙動をtestで固定)。
- OPEN-524のみ: `er078_asr_value_guard_01.py`の`KANA_WORD_BOUNDARY_CHECK = False`。OPEN-523のみ: `WEAK_KANA_REGION_COMPAT = False`(各1行。旧挙動の値ガード結果をtestで固定)。
- または適用commitの`git revert`(単一commit)。
## 8. リスク(隠さない)
- 再生成/HR Lock増: 真の値違いのREADING_MATCH PASSがNG_PROTECTED→次slotでTTS再生成(retry消費)。実コーパスの該当は既知負例のみ・正常143/未知493のNG化0。実運用頻度は低いと推定されるが証明ではない(§6の初回run集計で確認)。
- OPEN-524で`三日`(原稿)↔`みっかかん`(転写)がP1値DIFFとなる(従来EQUAL)。真の値違い(間/目)だがSecondaryに回らない設計(P1)による。
- 期待読み表に無い『正しいが珍しい読み』は置換されずNG/DEMOTEになり得る(例: いつか=5日はDEMOTE)。
- `OPEN-522`(助数詞表外)は適用していない=既知の限界のまま。
