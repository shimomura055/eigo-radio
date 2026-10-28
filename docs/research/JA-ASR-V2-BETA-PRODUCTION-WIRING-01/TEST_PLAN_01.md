# TEST_PLAN_01(JA-ASR-V2-BETA-PRODUCTION-WIRING-01 委任_01A。実装前・API 0)
設計=`WIRING_DESIGN_01.md`、対象範囲=`COVERAGE_MATRIX_01.md`。目的=USER §3-4「必須検証」・§3-5「Production Wiring完了条件」を、実装(委任_02)で何をどう確認するかの計画に落とす。**本書の「実測」はHEAD(f215c3537)に対する本委任での実行結果のみ**。新test・runtime evidenceは02で取得する(未実行の想定をPASSと書かない)。

## 0. HEADベースライン(本委任で実測。API 0)
- 実行系: **`.venv/Scripts/python.exe`**(Python 3.14.6、pykakasi有)。システムの`py -3`/`python`は`pykakasi`未導入で`er011_a2_reading_resolver_01`のimportに失敗する(02の実行手順に明記)。
- A) `er078_asr_unified_ja_wiring_test_01.py er007_ja_secondary_value_equivalence_test_01.py er078_pass_with_warning_registry_01_test_01.py er007_ja_secondary_asr_01_test.py er109_xz_scope_01_test_01.py` → **138 passed / 2 failed**(71 subtests)。
- B) `er078_asr_unified_judge_01_test_01 / wiring_05 / wiring_06c / wiring_13 / backcompat_07 / value_guard_01 / value_guard_kana_unify / er011_ja_asr_variant_layer_candidate_e_cascade_return / candidate_e_full_diff / er007_ja_scg_test_01 / scg_c2_neg / scg_phase0_regression / er007_ja_tts_retry_path_fix / er006_master_audio_store_01_test / er109_xz_isolation_01_test_01` → **517 passed / 3 failed**(112秒)。
- HEADで既に失敗する5件(本件前から。**02冒頭で原因確認→最小是正**。承認済み仕様との矛盾の是正=11-8の範囲):
  | test | 症状(観測) | 仮説(未検証) |
  |---|---|---|
  | `er007_ja_secondary_asr_01_test.py::test_koro_kanji_variant_confirmed_by_reading_candidates`(`:134`) | `r["final_status"]=="PHONETIC_MATCH"`(期待`ORTHOGRAPHIC_VARIANT_CONFIRMED`、verified自体はTrue `:152`) | 後続のVariant Layer(`er011_ja_asr_variant_layer_01.py`、OPEN-333 E3/E4 `2a66b4eb6`/`7953f5969`)で分類が上位ラベルに変わった=fixtureの期待値が古い |
  | `er007_ja_secondary_asr_01_test.py::test_single_engine_repetition_does_not_confirm_orthographic_variant`(`:240`) | `verified`が期待False→実際True | 同上(同表記の単独エンジン収束がPHONETIC_MATCH等で既にPrimary PASS) |
  | `er109_xz_isolation_01_test_01.py::StaticIsolation::test_importers_of_scope_module_are_a_fixed_production_list` | 固定リスト外の未知importer4件: `er118_fz_full_episode_trial_01.py / er122_fz_ctx_fakes_01.py / er118_fz_dialogue_context_tts_trial_01.py / er121_e1_slowed_asr_recheck_01.py` | Trial/test補助moduleが追加された後に固定リストを更新していない |
  | `er109_xz_isolation_01_test_01.py::StaticIsolation::test_m3_scope_entry_call_sites_are_fixed_and_literal` | scope入口call siteのCounterが期待と不一致(`er118_*`ほか) | 同上 |
  | `er078_asr_unified_wiring_05_test_01.py::test_hr_lock_module_unchanged_and_stop_retrying_branches_recorded_only`(`:689`) | `git diff --name-only 961d5b360 -- er011_human_review_lock_01.py`が非空 | 後続の正規変更(`6e7fa7cf5` TTS-RETRY-FALLBACK-LR-UNIFICATION委任_04)で「無変更」前提が失効 |
  → 新importer(`er078_ja_v2beta_01.py`)を`er109_xz_isolation`の固定リストへ入れる際に同test群を現行実態へ更新する(Y/Zの既存importerも同時に正す)。

## 1. 既存regression(実装後も全て同一結果であること。`.venv`で実行)
| 層 | file | 目的 / 本件との関係 |
|---|---|---|
| 統一judge本体 | `er078_asr_unified_judge_01_test_01.py` `er078_asr_unified_wiring_05/06c/06d/06e/10/11/13_test_01.py` `er078_asr_unified_backcompat_07_test_01.py` `er078_asr_unified_en_wiring_test_01.py` | `unified_judge`**無改変**の証明(英語/A/B/C含む)。旧readerが新keyで壊れないこと(backcompat_07) |
| JA adapter | `er078_asr_unified_ja_wiring_test_01.py` `er007_ja_secondary_asr_01_test.py` `er007_ja_secondary_value_equivalence_test_01.py` `er007_ja_scg_test_01.py` `er007_ja_scg_c2_neg_test_01.py` `er007_ja_scg_phase0_regression_test_01.py` `er007_ja_tts_retry_path_fix_test_01.py` `er007_ja_blindspot_test_01.py` `er007_ja_asr_validator_01_test.py` | **scope None=従来出力byte同一**。seam S1P/S1S/S2で既存分岐を壊さない |
| 値ガード/F1+F2 | `er078_asr_value_guard_01_test_01.py` `er078_asr_value_guard_kana_unify_test_01.py` `er078_time_atom_test_01.py` | READING_MATCH最終ANDゲート・かな数詞統一が不変 |
| Variant Layer E3/E4 | `er011_ja_asr_variant_layer_candidate_e_full_diff_test_01.py` `…_cascade_return_test_01.py` | M-6の前提(`candidate_e_rejections`/`cascade_diffs`)の仕様不変 |
| 事後試聴リスト | `er078_pass_with_warning_registry_01_test_01.py` | registry拡張後も旧record出力byte互換 |
| Store/再利用 | `er006_master_audio_store_01_test.py` `er078_asr_unified_wiring_06c_test_01.py`(reuse guard系) `er109_wiring_golden_test_01.py` | `guard_entry`拡張で印の無いentryに作用しない |
| scope/isolation | `er109_xz_scope_01_test_01.py` `er109_xz_isolation_01_test_01.py`(§0の2件含む) `er127_tts_block_policy_01_test_01.py` `er127_test_golden_01.py` `er127_final_adoption_b1_test_01.py` | 新moduleのscope読取が固定importer集合に入る。統一3回構成の回数/180秒が不変 |
| 静的監査 | `er078_asr_unified_wiring_static_audit_01.py`(post_wiring tests) | JA closure・adapter唯一性。新module分のallowlist更新 |
| X runner | `er019_family_x_audio_production_runner_01_test_01.py` `er019_test_family_x_validation_inheritance_01.py` `er019_family_x_ja_recheck_retry_01_test_01.py` `er019_family_x_b3_production_wiring_01_test_01.py` `er019_family_x_new_structure_wiring_01_test_01.py` | JA Section生成・継承 |
| Y runner | `er121_family_y_runner_01_test_01.py` `er121_family_y_runner_text_wiring_test_01.py` `er121_y_generator_decorator_test_01.py` `er121_family_y_hr_approval_guard_test_01.py` | Y試聴ページ節追加のregression |
| Z runner | `er063_family_z_audio_01_test_01.py` `er026_family_z_fiction_production_runner_01_test.py` `er026_family_z_e2e_integration_test_01.py` | Z JA Section・試聴ページ |
| Gate | `er130_adopted_take_classifier_01_test_01.py` `er130_gate_wiring_mock_e2e_01_test_01.py` | JA PASS_WITH_WARNINGがBLOCKされないこと(ASR PASS系 `er130:41`) |
02では**実装前後の全suiteをセットで実行**し、HEAD比の差分(増減したtest ID)を表で報告する。実行は独立suiteを並列(8原則2: 並列化。state競合のあるHR queue/Store系は`test_state_isolation_01.py:46`のredirectを使う)。

## 2. 新規test(委任_02)
命名は`er078_ja_v2beta_01_test_01.py`(unit)・`er078_ja_v2beta_wiring_test_01.py`(adapter/Store/registry/runner integration)・`er078_ja_v2beta_parity_test_01.py`(proto対照)。ID=T-*。API 0(mock ASR、socket guard `docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/eval_common_02.py`流用)。
### 2-1. 判定規則(L1: v2、L2: β)と承認済み基準線の再現
| ID | 内容 | 期待 |
|---|---|---|
| T-P1 | **月6本の保存draw**(`redraw_03.json`+`EVAL_UNIFIED_03`の決定対)を新Production adapter(scope X、R-1なし、L3なし)で判定 | ms_03 a2=PASS_W(v2 `A3_value+A2_particle`、`JA_NEWLAYER_PRON_EQUIVALENT`)・ms_03 a3=PASS_W(β、`JA_NEWLAYER_BETA_COMPOSITE`+`JA_COMPOSITE_SECONDARY_READING_CONFLICT`+`…LISTEN_ADVISED`)・reselect a1/a2=PASS_W(v2)=**4 PASS_W**。ms_03 a1(`p1_value_diff`)・reselect a3(`secondary_not_accepted`)=NG(最終slotならHR)=**2 HR**。根拠=`EVAL_UNIFIED_03.md` §1B(R-1 OFF) |
| T-P2 | 全draw対27の層別PASS系件数 | proto `Flags(l1,l2,l3=False,r1=False)` を同一harnessで再実行して**期待JSONを生成**(API 0・決定的)し、Production結果と全行一致(参考値: L1(R1off)=7/27、L1+L2+L3(R1off)=11/27、L3の寄与は本構成から除かれる) |
| T-P3 | **parity**: `eval_unified_03.py`の2103行(正例213/負例1803/不明87)を、protoの`judge()`とProductionで比較 | `cat`(PASS/PASS_W_PROD/PASS_W_NEW/NG)・理由・警告が全行一致(protoのmonkeypatch層=本設計のseam差替えと同一関数なので一致するはず。差が出たら設計/移植の欠陥) |
| T-L1a | v2単体: `三十人=30人`、`8,900=8900`、助詞は→わ・へ→え、漢数字/算用数字、正例/負例ペア(UC6_U1〜U6) | proto `proto_unified_03_test_01.py`(48 test)の対応test全てをProduction moduleに移植して全PASS |
| T-L1b | v2が受理範囲を超えるVALUE_ONLY(Production値等価層が受理しない)で`JA_NEWLAYER_VALUE_ONLY_BEYOND_PROD`が付く。Productionが受理する対は警告なし(寄与なし) | |
| T-B1 | β: Primary数値garble(`8000900`)+Secondary正値→PASS_W。`explain_garble`観測形(F-A `[1-9]0+`の2断片、F-B 数字+漢数字)以外は不成立 | proto `b_light_proto_02` test相当 |
| T-B2 | βのSecondary fail-closed: Secondary不可/空/cost guard/circuit open/`JA_SCG`flag off → 元のNGのまま(`NG_PROTECTED p1_value_diff`/`NG_BOTH`)。**追加Secondary呼出の失敗でcircuit breakerカウントが増えない・技術STOPに変わらない** | |
| T-B3 | β: Secondary値≠原稿、原子列の位置/個数/順序不一致、かな数詞・あいまい原子(R-4)→NG | |
| T-B4 | **M-7**: `ctx.phrase_list_hash!=""` またはAzure呼出が原稿をPhrase Listに渡す→fail-closed。静的test: `_azure_stt_strict`が`phrase_list`系関数を呼ばない | |
| T-B5 | P1型(`p1_value_diff`でSecondary未呼出): `precheck_composite`がFalseならAzureを**呼ばない**(費用0)。Trueのときだけ1回(SecondaryCache経由、同一shaで重複0) | |
| T-B6 | βは`p2_exclusion:*`(A5類似度/A6固有名詞/A7読み辞書/A4 C2)・否定差では発火しない | |
### 2-2. 維持する安全対策との整合
| ID | 内容 | 期待 |
|---|---|---|
| T-E1 | **M-6 E3**: `candidate_e_rejections`非空(corpus `OPEN333_sweep8`のE3由来15行ほか34行)→全新層不適用・出力=L0と同一・`ja_v2beta.blocked_by="M6_E3"` | EVAL §9: 34行ブロック |
| T-E2 | **M-6 E4**: `candidate_e_cascade_diffs`非空→不適用(corpus `OPEN333_E4` 168行) | |
| T-M1 | **M-1**: 原稿に不規則読み数詞(一日・二日・三日・二十歳・一人・二人…)→v2は両側・VALUE_ONLY/PRON両経路で不適用、βは`irregular_reading_value`でNG。**M0基準線PASS_W(『三人で一日に会った』型)は不変** | `一日中→ついたち中` 3行がNG |
| T-W1 | **M-2**: 新層救済は必ず`JA_NEWLAYER_*`警告→`PASS_WITH_WARNING`(clean PASSにならない)。`APPROVED_EQUIVALENCE_BASES`に新ラベル/新分類名が**無い**(import時assert+test)。`_READING_MATCH_CLASSIFICATIONS`にも無い | |
| T-F1 | F1+F2: READING_MATCH PASSの最終ANDゲート(8,900↔89,000・しわ↔すわ)が不変 | 既存`kana_unify` testsが無改変でPASS |
| T-N-NG | 数値・桁・助数詞・脱落・否定・意味変化の負例で**新層による増分誤PASSなし**(UC6_U2〜U5=0、OPEN517_wrongvalue_kana 471行=0) | EVAL §4c |
### 2-3. PASS_W非ブロッキング(USER §3-2)
| ID | 内容 | 期待 |
|---|---|---|
| T-NB1 | adapter: PASS_W結果で `verified=True`・`human_review_required=False`・`stop_retrying=False`・`_log_human_review`不呼出(JA queueの行数不変) | |
| T-NB2 | retry loop(標準→fallback、mock TTS/ASR): attempt1がPASS_Wなら**attempt数=1で`status:"OK"`終了**、TTS呼出1回、HR Lock非登録(`record_outcome`が失敗を数えない)。attempt1=NG→attempt2=PASS_Wなら2回で終了 | `repro01:407`/`n3_tts:842`/X/Y/Z各stage |
| T-NB3 | 通常NG・3回NG→HR Lock・E3/E4 NG・`reuse_blocked`・既存HR Lock・`HUMAN_APPROVED`記録(`record_human_approval`→`verify_episode_audio_validation_gate`)が**PASS_W導入前後で同一** | HEAD golden(`er127_test_golden_01.json`)と一致 |
| T-NB4 | 組立: 全JA segmentがPASS_Wでも`verify_episode_audio_validation_gate`が許可(`VALIDATED`)。`er130`が`BLOCK`しない | |
| T-NB5 | 静的test: `verdict`/`rescue_basis`/`listen_advised`/`JA_COMPOSITE_LISTEN_ADVISED`を**制御フローの条件に使う箇所が報告系module以外に無い**(AST/Grep)。`JA_COMPOSITE_LISTEN_REQUIRED`がProduction 0件。公開前試聴必須の条件を復活させていない | USER §1A末尾 |
| T-NB6 | 自動配信・公開機構が無い: 新moduleがpush/publish/upload系を呼ばない(静的) | |
### 2-4. 再利用・継承・resume(USER §3-4)
| ID | 内容 | 期待 |
|---|---|---|
| T-S1 | Store: PASS_W(新方式)entryを`register`→再利用。`asr_judgement`(`verdict`/`rescue_basis`/β provenance)が`manifest`に保存され、再利用時`asr_judgement_inherited`に復元される(警告引継ぎ)。registryが`inherited=True`で列挙 | |
| T-S2 | Store: scope外(scope None=A/B/C)・flag OFFで同entryを再利用→**ブロック・再生成**(`JA_V2BETA_AUDIO_OUT_OF_SCOPE_OR_FLAG_OFF`)。印の無い既存entryは再利用可否不変 | ortho前例 `er109_xz_isolation_01_test_01`/`er109_wiring_golden` と同型 |
| T-S3 | Store: scope内で寄与entryを**現行規則でAPI 0再判定**。規則が変わってNGになるentryは再利用せず再生成。API呼出0・Secondary新規呼出0 | `composite_reuse_decision`同型 |
| T-S4 | J11継承(JA): v2救済(Primary転写採用)/β救済(Secondary転写採用)の両方で最終ANDゲートを通り、元の警告・`rescue_basis`が`asr_judgement_inherited`に残る。値DIFFの転写では継承NG | `er019_test_family_x_validation_inheritance_01.py`拡張 |
| T-S5 | 同一out_dir resume(`_generate_or_reuse`): PASS_W entryは再生成せず再利用、事後試聴リストに残る。`er127`のstub_row/resumeで成功attemptが二重計上されない | |
| T-S6 | `judge_rule_version`が将来変わったentryは再判定対象になる(版不一致=黙って通さない) | |
### 2-5. 汎用性(USER §3-1「題固有の例外を作らない」)
| ID | 内容 | 期待 |
|---|---|---|
| T-G1 | 静的scan: 新moduleソースに題由来語(月・しわ・詩・超・岩・縮・8,900等)を含まない。許可=助詞「は」「へ」・数詞文字・桁区切り・一般的な読み変換定数のみ | |
| T-G2 | 汎用題positive(≥10題: 売上/参加者/価格/距離/年齢/所要時間/割合…。助詞は→わ・桁区切り・数詞garble型)でv2/β PASS_W | proto UC6/BLIGHT汎用題と同等以上 |
| T-G3 | metamorphic: 月題positive/negativeの名詞句を別名詞へ置換しても判定カテゴリ(PASS_W/NG)不変 | |
| T-G4 | `ja_v2beta`が題・記事IDを参照しない(adapter引数の`canonical_text`以外を読まない) | |
### 2-6. 有効範囲・既定値・flag
| ID | 内容 | 期待 |
|---|---|---|
| T-A1 | **A/B/C互換**: scope None(A/B/C・単体)で、2103行 corpus+既存fixtureの`asr_judgement`が**HEAD出力とbyte同一**(新keyを一切作らない)。`conftest.py:8`(scope残留検査)で他testに漏れない | 27-7 |
| T-A2 | X/Y/Z各stage entry(mock ASR/mock TTS)で`current_scope()`がX/Y/Zになり、終了時(例外・STOP含む)にNoneへ復元 | `er109_xz_scope_01`既存testの拡張 |
| T-D1 | 既定値: `JA_V2_BETA_ENABLED is True`(APPROVED_FOR_PRODUCTION)、読取関数は`is_active_for_run()`**のみ**(AST: 他module/他関数が定数を直接読まない、env/引数/設定dictから変更不可)。定数をFalseにすると全経路が従来出力に戻る(L0同一) | `grep -rn JA_V2_BETA_ENABLED` = 定義+読取関数のみ |
| T-D2 | R-1/L3/合意再試行/best-of-N/veto/frame検査/monkeypatchがProduction moduleに**存在しない**(Grep) | `grep -rn "r1_block\|KUNYOMI_OKURIGANA\|consensus(\|best_of_n\|_getframe" er078_ja_v2beta_01.py er007_ja_secondary_asr_01.py` = 0 |
| T-D3 | 同一音声のASR再試行が増えていない: 1 attemptあたりOpenAI呼出=1、Azure呼出≤1(β追加呼出はsha単位キャッシュ共有) | USER §1A-2 |
### 2-7. 最終制作報告(USER §3-2-4)
| ID | 内容 | 期待 |
|---|---|---|
| T-RP1 | X/Z/Y各stageで、PASS_W(新方式)があるとき`audit/pass_with_warning_listening_list.json`の各entryに`verdict`/`rescue_basis`/`rescue_reason_ja`/`warning_labels`/原稿・Primary・Secondary転写/音声path+shaが入る | |
| T-RP2 | X/Z試聴ページ節・**Y試聴ページ節(新設)**・標準出力ブロックに同内容が出る。0件時も「0件」と明記。導出失敗は「導出失敗(要確認)」 | |
| T-RP3 | 報告の失敗がstageを失敗させない(`write_listening_list_safe`と同契約) | |
| T-RP4 | 旧record(`verdict`無し)の出力はHEADとbyte同一 | `er078_pass_with_warning_registry_01_test_01.py` |
### 2-8. runner integration(mock ASR/TTS。X/Y/Z)
`generate_family_x_a2_segments`(`er019…:2026`)・`generate_y_a2_segments`(`er121_family_y_audio_01.py:640`)・`run_tts_stage`(`er063…:1519`、Std)を、**TTSは保存wavを返すfake**(`er127_test_fakes_01.py`・`er122_fz_ctx_fakes_01.py`のパターン)、**ASRは月題/汎用題の転写を返すmock**で実走し、①日本語題・Preview・Comment・KP日本語意味の4 Sectionが全てadapterを通る(呼出ログ) ②PASS_W/NG/HRが期待どおり ③retry回数・HR queue(redirect済み)・results json・事後試聴リストの内容 ④scope復元、を確認。Family A/B/Cの同等fakeでは新層が発火しない。

## 3. 「PASS_Wを非ブロッキングにしたことによる実際の誤PASSリスク」の再確認(USER §3-4 特記)
過去Trialの負例・実音声データで**Production実装を実際に走らせて**測る。結果は表で報告し、既知値(EVAL_UNIFIED_03 §4)を超える増分があれば停止してFableへ(判断候補)。
| ID | データ | 期待(R-1 OFF構成の既知値) | 備考 |
|---|---|---|---|
| T-R1 | 負例コーパス 1803行(群: N1_150, N3_real30, N3_redraw 240, R4R3_extra18, UC6_U1〜U6, BLIGHT 86, L3_NEG 124, OPEN333_E4 168, OPEN333_sweep8 63, OPEN517_wrongvalue_kana 471)。sha256 `d55f24e2…`(1439行)+L3_NEG+N3_redraw | **増分誤PASS=8**(T1同音異表記6[R4R3_extra18 4+UC6_U6 2]+T2 β最悪露出2[N1_150 1+R4R3_extra18 1])、OTHER=0、T3(不規則読み)=0、**回帰(L0 PASS→NG)=0** | L3を外しても増分は変わらない見込み(L3_NEG増分0、EVAL §8)。**protoを`Flags(l1,l2,l3=False,r1=False)`で再実行して確定** |
| T-R2 | N3 実音声30本(意図的誤読TTS=真値NEG)×記録+新4 draw(`n3_redraw_02.json`)、scenario real(Azure保存転写)/S_canon(Secondary=原稿の最悪露出) | real: 49%→49%(増分0)。S_canon: 75%→75%(増分0)。**実誤読wavに対する新規PASS=0** | EVAL §5 |
| T-R3 | 拡張負例(新規・API 0): 汎用題×変異種(値違い/桁違い/助数詞違い/脱落/否定/意味変化/同音異表記/不規則読み)×{P_only, PS_same, S_canon}の決定的生成(`gen_neg_02.py`、乱数seed固定、題固有語なし) | 新層の増分はT1/T2型のみ(OTHER=0、T3=0) | 月題比率の偏り(OPUS R-5)の補正。生成器と期待は02で実装前に凍結 |
| T-R4 | 正例側(救済率): 月6本+拡張4wav(Y preview 2本・Z comment_1・X comment_2)の保存draw | 月6本4/6。Y preview(思いどおり↔思い通り)は**救済されない**(`not_tcm`=v2は発火しない。別ID。EVAL §7a)。X comment_2(タイフーン機↔台風機)は対象外(OOV同音) | |
| T-R5 | 実害の質的整理: T1が起きる条件=「ASRが書いた漢字が複数の読みを持ち、TTSが別の読みで読んだ場合に区別できない」。N3実誤読30本での再発数0を実測で添える | 報告に「非ブロッキング化で追加で見逃し得るのはT1型の同音異表記読み違いとT2型(β最悪露出)のみ」と範囲を明記 | R-1 OFFのユーザー決定(USER `:63`)の帰結。数値が既知値を超えない限り判断候補にしない |
| T-R6 | β読み相違(`JA_COMPOSITE_SECONDARY_READING_CONFLICT`)付きPASS_Wの件数・割合を全corpusで集計し、最終報告に「試聴推奨」として必ず載ることを確認 | ms_03 a3型は報告に出る | WIRING_DESIGN J-3 |

## 4. runtime evidence計画(実音声でProduction judgeを実走。委任_02A)
**判定規則・model_id・routingの証跡**を、実音声に対する**本物のProduction path**から取る。
| ID | 内容 | API | 取得する証跡 |
|---|---|---|---|
| E0 | 月6本wav(`er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_{ms_03,reselect_01}/a2/narration/attempts/japanese_title_attempt{1,2,3}_*.wav`)を、`run_scope("X")`内で本物の`evaluate_attempt_ja_with_cascade_detail`に通す。Primary/Secondary転写は**保存値を注入**(`_azure_stt_strict`差替=API 0) | 0 | 判定結果(verdict/rescue_basis/warnings/layers)、`judge_rule_version`、E0=T-P1の実音声版 |
| E1 | 同6本を**実ASR**(Primary=`routing.transcribe(ja-JP)` OpenAI、Secondary=Azure)で判定(各wav 3 draw)。draw揺らぎ(OpenAI draw 48%のみ値正等)を踏まえ**合否基準にせず分布を報告**(決定的な再現はE0/T-P1) | 有 | **`asr_judgement.r5.models`(`er007:773`)=実際のProvider/model_id**、Azure `model_id="azure-speech-stt"`、`primary.text`/`secondary.text`、raw usage log。`routing`が`require_asr_route("ja")`のSSOT通りであること |
| E2 | **正式TTS段関数3本**(X a2・Y a2・Z a2)を、TTSをfake(保存wavをコピー)にして**実ASR**で走らせる(前例: `er109_ukus_runtime_evidence_01.py:5`の「本物の入口でdecorator付き段関数を実走」)。対象= 日本語題+Preview+Comment+KP日本語意味(各Familyで最低日本語題2本+Preview/Commentそれぞれ1本) | 有 | `tts_generation_results.json`(`asr_judgement.verdict`)、`pass_with_warning_listening_list.json`、試聴ページ節(X/Z/Y)、標準出力ブロック、scope復元、retry回数(PASS_Wで1回終了)、HR queue行数不変 |
| E3 | 汎用題の実音声(拡張4wav: `middle_east_yemen_saudi__run_mey_02` comment_2 / `melos run_e2e_02` comment_1 / `redelivery_fee run_01` preview / `run_gpg5_y_01` preview)を実ASRで1 draw | 有(小) | 汎用性・Y/Z/X各Familyでの発火/非発火 |
| E4 | N3負例wavの実ASR(意図的誤読TTSのうちL0でNGの約16本から≤10本)で、新層が**実音声でも発火しない/NGのまま**であることを確認(T-R2の実ASR版) | 有(小) | 誤PASS 0の実証 |
| E5 | Family A相当(scope None)で同wavを判定し、HEADと同一出力 | 0(E0の注入方式) | A/B/C互換の実証 |
**月タイトル6音声の再掲(USER §3-5)**: E0の結果を表にし、「更新後の判定: PASS_W(新方式)4本/HR扱い2本(ms_03 a1・reselect a3)」「ユーザーが既に行った試聴判断(`USER_DECISION_REGISTER_01.md:550`の#203、ms_03 a2は個別承認済み=`HUMAN_APPROVED`)との整合」を記載。**6本すべての機械PASSは合格条件にしない**。記事『月は少しずつ縮んでいる？』の公開差替え・FX-MOON-SHRINKING判断は行わない。

## 5. 費用見積(委任_02A実走分。**300円超なら事前承認要**)
単価の出典: `EVAL_UNIFIED_03.md` §13・`PREREGISTERED_03.md` §5(OpenAI gpt-4o-mini-transcribe 分課金 ¥0.0075/秒≒6秒題¥0.045、Azure Speech $1/時間≒6秒¥0.27)。TTS 0(fake)。LLM 0。
| 項目 | 内訳 | 見積(円) |
|---|---|---|
| E0/E5/T-P*/T-R1,R3,R4 | API 0 | 0 |
| E1 | 6wav×3draw OpenAI(≈¥0.045)=18呼出≈¥0.8、Azure 6wav×1(shaキャッシュ。Opus: Azure決定的)≈¥1.6 | ≈2.4 |
| E2 | 3Family×約4clip(Std日本語題・Preview・Comment・KP日本語意味)=約12clip×(¥0.045+¥0.27) | ≈3.8 |
| E3 | 4wav×1draw≈¥0.18+Azure≈¥1.1(Secondary要の分のみ) | ≈1.3 |
| E4 | ≤10wav×(¥0.045+¥0.27) | ≈3.2 |
| 予備(再実行・追加draw、委任文が明示許可した回数内) | | 5 |
| **合計** | | **≈¥16(上限¥20を個別Capとして提案)** |
→ 案件見積300円以下かつ承認済みScope内(7-7)。日次1,000円(JST)内。分割・日付分割は不要(8原則2)。**見積300円超・日次1,000円超過見込み・個別Cap超過が出たら実走せずFableへ**。TTS生成は一切行わない(新規TTS 0円)。

## 6. 合格基準(02完了=PRODUCTION_WIRED候補の条件。USER §3-5の対応)
1. §2の新test全PASS+§1の既存suiteがHEAD比で悪化0(§0の既存失敗5件は是正して0にするか、是正不能なら原因を添えて明示)。
2. T-R1〜T-R6: 増分誤PASSが既知値(8: T1 6+T2 2)以下、OTHER=0、回帰0、実誤読wav(N3)に対する新規PASS=0。超過は停止→Fable。
3. E0=T-P1(月6本: PASS_W 4・HR扱い2)。E1〜E4で`model_id`/`routing`/判定規則の証跡が`asr_judgement`に残る。
4. X/Y/Z各Family・Std各Sectionで適用確認(E2)、Advは日本語音声なしの理由を記録済み(COVERAGE_MATRIX_01)。
5. PASS_Wが最終制作報告(X/Z/Y試聴ページ節・標準出力・JSON)に載る(E2)。
6. A/B/C出力byte同一(T-A1/E5)。
7. SSOT更新(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/USER_DECISION_REGISTER)・Git commit/push・**Fableによる独立受入**(ここまでPRODUCTION_WIREDと呼ばない)。

## 7. 実行順・並列化(クリティカルパス)
依存: ①既存失敗5件の原因確認(独立・先行可) ②`er078_ja_v2beta_01.py`移植+T-L1/B unit(protoをoracleにparity)=クリティカル ③seam S0〜S3+T-P/E/M/W/NB/A ④Store/継承/registry/Y節+T-S/RP ⑤runner integration ⑥API 0 corpus(T-R1〜R4,E0,E5)と有料E1〜E4(費用上限内)は③後に並列 ⑦SSOT更新+commit。①と②は並列、④は③と並列(registry/Y節は新moduleに非依存)、⑥内のE1〜E4は並列。待機・日付分割なし。
