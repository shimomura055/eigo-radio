# WIRING_DESIGN_01(JA-ASR-V2-BETA-PRODUCTION-WIRING-01 委任_01A。配線設計。実装前・API 0・Productionコード編集0)
正本(目的)=`docs/pm/delegation_log/2026-10-29_JA-ASR-V2-BETA-PRODUCTION-WIRING-01_USER.md` §1A・§3。技術根拠=`docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/`(`EVAL_UNIFIED_03.md`・`DESIGN_PROPOSAL_01.md`・`OPUS_REVIEW_01.md`・`PREREGISTERED_03.md`・`proto_unified_03.py`)と `docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/{proto_reading_compare_02.py, b_light_proto_02.py}`。
姉妹文書: `COVERAGE_MATRIX_01.md`(Family/Level/Section)・`TEST_PLAN_01.md`(試験・費用)。

## 0. 結論(先に)
1. **承認仕様の中身(固定)**: v2読み規則 + B-light β、**R-1 OFF**、ASR再試行なし、L3別表(超→こえ)なし、合意再試行なし。Opus必須修正のうち M-1(不規則読みガード)・M-2(専用warning・`APPROVED_EQUIVALENCE_BASES`に入れない)・M-6(E3/E4構造ガード)・M-7(βのPhraseList独立性fail-closed)は「承認済み安全対策の維持」に含まれるので**移植する**。M-3/M-4/M-5(再試行・L3)・R-1・R-2の対象外経路は**移植しない**。
2. **配線点は JA adapter 1関数 `er007_ja_secondary_asr_01.evaluate_attempt_ja_with_cascade_detail`(`:556`)内の4 seam**。X/Y/Z全Section(COVERAGE_MATRIX_01 §0)が全てここを通る。**`er078_asr_unified_judge_01.unified_judge`本体(英語/A/B/Cと共有)は無改変**(状態機械・最終ANDゲート・F1+F2・Secondary 1回・circuit breakerを現状のまま使う)。新ロジックは新module `er078_ja_v2beta_01.py`(純関数+単一flag読取関数)に置く。
3. **有効範囲は X/Y/Z run scope内のみ**(`er109_xz_scope_01.current_scope()`∈{X,Y,Z}、既存のTTS段decorator再利用、新規decorator不要)。scope外(A/B/C・単体)は従来コードパス=出力byte同一(27-7)。
4. **判定結果は `verdict`(PASS/PASS_W/NG/HR)・`rescue_basis`(v2|beta|null)・`judge_rule_version` を既存`asr_judgement`にadditiveで追加**。PASS_Wは既存のPASS_WITH_WARNING状態そのもの(新状態を作らない)なので、Gate通過・retry終了・HR Lock非投入・Store再利用・継承・事後試聴リストは**既存の非ブロッキング経路をそのまま使う**。
5. 最終制作報告は既存の**事後試聴リスト(registry)を共通データ源**にし、(a)各Family試聴ページ節(Yに欠落→追加)・(b)生成完了hookの標準出力ブロック・(c)JSON を共通helperから出す。
6. 緊急OFFは**モジュール定数1個+読取関数1個**(既存`READING_MATCH_FINAL_GATE`/`JA_SECONDARY_VALUE_EQUIVALENCE_ENABLED`/er109 flagと同型、env/引数/設定dictから変更不可)を推奨(論点f、Fable/Opus判断)。
7. Opus独立技術レビュー(CLAUDE.md条件A: 新しい構造・処理フローの設計)を**実装前に**入れることを推奨。論点は§11。

## 1. 現行Production経路(file:line)
| 項目 | 場所 | 要点 |
|---|---|---|
| JA統一judge入口(唯一) | `er007_ja_secondary_asr_01.py:556`(`evaluate_attempt_ja_with_cascade_detail`)、`:793`(wrapper。最終slot NGのみ`:809-810`でHR queue) | 全JA呼出は `repro01:407` / `n3_tts:842` / `voice01:616,677` / `er038:354,393`(Trial) / `er019_coffee_s3_support_regen_01:138`(補助tool)から。X/Y/Z Std JAは `repro01:407`(標準)と `n3_tts:842`(fallback)のみ |
| Primary: OpenAI | `routing.transcribe(path, language="ja-JP")`(呼出側)。モデル/routingは `er006_asr_provider_routing_01.require_asr_route("ja")`(adapter記録 `er007:775-781`) | R-5計測がmodel_idをauditへ複写済み(`:768-773`) |
| Primary側 値等価層 | `er007:595`(`eq_cls = None if cls.should_pass else _numeric_value_equivalence(...)`)→ 定義 `:532` | 表記差(三十人=30人・桁区切り`8,900`)だけ救済。**読み差は救済しない** |
| E3/E4読取専用記録 | `er007:575-577`(`_ce_rej`/`_ce_casc`)、監査 `:779-784` | Candidate E(OPEN-333)がE3拒否/E4でCascadeへ戻した差分。判定不変の記録のみ |
| PrimaryResult生成 | `er007:631`(`warning_labels=()`、`equivalence_basis`はREADING_MATCH系のみ) | |
| AttemptCtx | `er007:636-650`(`phrase_list_hash=""`、`max_len`、`force_secondary=False`) | β M-7の前提(Azureに原稿を渡さない)がここ |
| Secondary: Azure | `_secondary_fn :652`(flag/COST_GUARD/`_azure_stt_strict`)、`_secondary_accept :670`(Secondary転写の許容集合。値等価層`:675-681`) | |
| Primary NG→P1/P2/P3 | `er078_asr_unified_judge_01.py:640-655`(P1 `p1_value_diff` `:642`: 値DIFFはSecondary不呼出でNG_PROTECTED) | βがP1型を救うには**Secondaryを追加呼出**する必要がある(§4-S2) |
| 最終ANDゲート | `er078:597-633`(Primary PASS側)・`:831`(Secondary受理側) | Primary PASS/Secondary受理とも値DIFF・否定差でNG |
| F1+F2 | `er078:73-80`(`READING_MATCH_FINAL_GATE=True`)・`:577`(kana_unify) | READING_MATCH根拠のみ。v2/βは**READING_MATCH根拠を使わない**(M2)ので影響しない |
| PASS_WITH_WARNING | `er078:552-566`(`done()`でPASS+警告→PASS_WITH_WARNING)・`:57`(`PASSING_STATES`)| `jr.verified`は両方True |
| retry/fallback | `n3_tts:763-870`(標準2回+fallback1回、`min(max_attempts, review_lock.PRODUCTION_MAX_TTS_ATTEMPTS)`=3 `er011_human_review_lock_01.py:81`)、`repro01:200`(標準loop)、X/Y/Z scope内は`er127.with_block`(`er127_tts_block_policy_01.py`)で①②→180秒→③ | 上限回数・180秒待機は本件で不変 |
| 同一音声ASR再試行 | **廃止済み**(`CURRENT_SPEC.md:2926`、`er007:590`コメント`stop_retrying=False`) | USER §1A-2「ASR再試行不採用」と整合。新規導入しない |
| 3回NG→HR Lock | `er011_human_review_lock_01.py`(`guarded_generate :674`/`record_outcome :358`)、`er127.register_ja_terminal_hr :726`、JA queue=`er007:39`(`HUMAN_REVIEW_LOG_PATH_JA`) | 不変 |
| HUMAN_APPROVED | `er003_v1_n3_01_assemble.py:96`(`record_human_approval`)・`:89`(`AUDIO_GATE_ALLOWED_STATUSES`)・`er011_human_review_lock_01.py:322` | 不変。USER §1A-4/§3-2-6のとおり記録・証跡を保持 |
| Master Audio Store | `er006_master_audio_store_01.py:130-137`(reuse前guard)・`:197`(`asr_judgement_inherited`復元)・`:234`(`manifest["asr_judgement"]`保存)・reuse_telemetry `_log_telemetry` | 保存済み`asr_judgement`を再利用でも継承。guard=`er078_reuse_value_guard_01.py:46` |
| 継承(J11) | `er019_family_x_validation_inheritance_01.py:256`(JA=保存採用転写に最終ANDゲートのみ。`:234`採用転写の決め方) | |
| 事後試聴リスト | `er078_pass_with_warning_registry_01.py:93,153,169,198` | 非ブロッキング。導出失敗は「導出失敗(要確認)」表示 |

## 2. 移植対象と移植先(L1・L2)
### 2-1. 新module `er078_ja_v2beta_01.py`(Production。research protoの「複製」ではなく**再配置+境界整理**。凍結protoは`docs/research/`にそのまま残す)
| 新module内 | 出典(research proto) | 変更点 |
|---|---|---|
| `pron_hira / _tag_pron / _diff_spans / c2_blocked / pron_value_equivalence / to_classification` | `proto_reading_compare_02.py` | 同一ロジック。`design_a`(旧ラッパー)は不移植 |
| `irregular_atoms(canon)` | `proto_unified_02.py:37`(`proto_unified_03`が使用) | M-1 |
| `value_layer(canonical, asr, cls, side, ctx)` | `proto_unified_03.make_layer`(`:101-`) | **frame検査(`sys._getframe`でsideを推定)を廃止し`side`引数で明示**。M-1(不規則読みはside・kind不問でProduction判定へ戻す)・R-2除外(`ENGINE_reading_difference`はProduction判定へ戻す)を維持。**R-1は呼ばない** |
| `explain_garble / analyze_primary_values / composite_core / composite_judge / precheck_composite`、`AtomStatus/BResult/PrecheckResult` | `b_light_proto_02.py` | `reading_rule`は`"v2"`固定(strictは評価用で不移植)。`secondary_reading_conflict`は`"warn"`固定(`"veto"`はM-4=再試行併用時のみ=不移植)。`composite_reuse_decision`は不移植(再利用は§6の`guard_entry`方式に統合) |
| `beta_guarded(...)` | `proto_unified_03.beta_guarded`(`:201-`) | **M-7**: `phrase_list_hash`が空でなければfail-closed。R-1の事後検査は不移植 |
| ELIG | `proto_unified_03.ELIG` | `("p1_value_diff","final_gate_value_diff","p1_protected_diff:number_mismatch","secondary_not_accepted")` を逐語 |
| M-6 | `proto_unified_03.e34_state`(Primary分類を再計算) | 再計算せず、adapterが既に持つ`_ce_rej/_ce_casc`(`er007:575-577`)を渡す(同一入力) |
| 追加(新規コード) | - | `is_active_for_run()`、`JUDGE_RULE_VERSION`、warning定数、`finalize_audit()`、`rejudge_contributed(entry)`(§6)、`contributed(aj)` |

**不移植(明示)**: `r1_block`/R-1(論点1参照)、`KUNYOMI_OKURIGANA`/`l3_*`(別表L3、USER §1A-3)、`consensus/contradicts/retry_eligible/best_of_n`(ASR再試行・合意再試行、USER §1A-2)、`Flags`、`_adapter`のmonkeypatch(`sec._numeric_value_equivalence`/`sec._azure_stt_strict`の差替え。Production codeでは**差替えず明示seam**にする)、`w_listen`系の「試聴必須」語(§2-3)。

### 2-2. R-1の扱い(両案比較と推奨)
| 案 | 内容 | 長所 | 短所 |
|---|---|---|---|
| R1-a(推奨) | **R-1のコードを入れない** | ONにできる経路が物理的に無い(「持ち込まない」を構造で保証)。テスト面積が小さい。EVAL「R-1 OFF」数値(月6本4/6、増分誤PASS 8[T1 6+T2 2])と実装が**1対1対応**(parity testが単純) | 将来R-1を採る場合は再実装が要る(研究protoの`r1_block`をそのまま再配置するだけ。コスト小) |
| R1-b | R-1を入れて定数`R1_ENABLED=False`固定 | 将来ONが1行 | 死んだコードがProductionに残り、flag迂回経路(誤ONの可能性)・DefaultOff型testの追加・「R-1 ON時の4本NG化」の仕様誤解を招く。USER §3-1は「R-1 OFF」のみで将来ON計画なし |
推奨=**R1-a**。R-1 ONは「受理面の変更(6本中4本が再びNG化=#207付随論点)」であり新たなユーザー判断が要るため、判断が出た時点で実装すれば足りる。

### 2-3. β内部ラベルの再定義(「試聴必須」語の撤去)
研究protoのβは `JA_COMPOSITE_LISTEN_REQUIRED`(`b_light_proto_02.py:62`)・`BResult.listen_required`・`listen_reasons` を持つ。USER §1A/§3-2で**量産PASS_Wは試聴必須ではない**ため、Productionではこれらを以下に改名・再定義する(意味づけの是正=承認済み仕様との矛盾解消、PM_GOVERNANCE 11-8の範囲内の不具合是正):
- `JA_COMPOSITE_LISTEN_REQUIRED` → `JA_COMPOSITE_LISTEN_ADVISED`(「試聴推奨(必須ではない)」)。`listen_required`→`listen_advised`。**いかなる分岐もこの値でretry・停止・HR投入・Assembly停止を行わない**(testで固定、TEST_PLAN T-N2)。
- 最終制作報告の文言は「試聴推奨(任意・生産を止めない)」。

## 3. 維持するもの((b))
| 安全対策 | 維持の仕組み | 確認test |
|---|---|---|
| F1+F2(READING_MATCH最終ANDゲート・かな数詞統一) | v2/βは`equivalence_basis`を設定しない(READING_MATCH以外)。`READING_MATCH_FINAL_GATE`未編集 | 既存`er078_asr_value_guard_kana_unify_test_01`/OPEN-517系 + 新T-E |
| E3(`candidate_e_rejections`) | `_ce_rej`非空→**全新層不適用**(Production判定のまま。M-6) | 新T-E1(proto M-6 testの移植) |
| E4(`candidate_e_cascade_diffs`) | 非空→全新層不適用(保守側。発火件数を監査記録) | 新T-E2 |
| βのSecondary fail-closed | Secondary不可(障害/空/cost guard/circuit open)・Secondary値≠原稿・Secondary原子列不一致・`phrase_list_hash`非空・provenance欠落→**従来判定(元のNG)へ戻す**。βのSecondary追加呼出の失敗はcircuit breakerを動かさず元のNGのまま | 新T-B1〜B6 |
| 数値・桁・助数詞・脱落NG | v2は`value_guard`がEQUAL(or NO_VALUESでnumber_mismatchなし)のときだけ。βは原稿原子列とSecondary原子列を位置・個数・順序で照合し、Primary側原子が矛盾/欠落ならNG | 回帰corpus 1803行(UC6_U1〜U6、OPEN517、BLIGHT、N1_150、N3) |
| 否定差 | 両層とも否定語/否定マーカー差があればNG(`negation_diff`/`_scg_negation_marker_diff`) | 同上 |
| A7(登録読み辞書)/C2(同形異音) | `_scg_reading_dict_reason`、`c2_blocked`(順方向・逆方向span)を維持 | 同上 |
| 不規則読み数詞(一日・三日等) | M-1: 原稿に不規則読み原子があればv2は両側・VALUE_ONLY/PRON両経路で不適用、βは`irregular_reading_value`でNG | 新T-M1 |
| 新層救済は必ず警告付き(M-2) | 救済(v2 PRON/v2 VALUE_ONLY[Production範囲超え]/β)は専用`JA_NEWLAYER_*`警告を必ず付与。`APPROVED_EQUIVALENCE_BASES`に**入れない**(import時assert) | 新T-W1 |

## 4. 配線設計: 4 seam(`er007_ja_secondary_asr_01.py`のみ編集。unified_judge無改変)
```
evaluate_attempt_ja_with_cascade_detail(...)   # er007:556
  cls = classify...; cls = _apply_variant_layer_voicing_upgrade(...)
  _ce_rej, _ce_casc = (読取専用記録)                      # 既存 :566-571
  v2b = ja_v2beta.begin(canonical_text, primary_asr_text, e3=_ce_rej, e4=_ce_casc)   # S0
      # active = is_active_for_run() ∧ lang=ja ∧ not (e3 or e4)。M-6でblockedなら v2b.blocked_by を記録
  eq_cls = None if cls.should_pass else _value_layer(canonical_text, primary_asr_text, cls, "primary", v2b)   # S1P (:595)
  primary = PrimaryResult(..., warning_labels=v2b.primary_warning_labels())                                    # (:631) 新層Primary救済のとき専用警告
  ...
  _secondary_accept(canon, stext): ... eq_s = _value_layer(canon, stext, cls_s, "secondary", v2b)              # S1S (:677)
  jr = unified_judge(...)                                                                                      # 無改変 (:691)
  jr = ja_v2beta.maybe_beta_rescue(v2b, jr, ..., cache, _secondary_fn, ctx)                                    # S2 (:691直後)
  ...(既存: result["verified"]=jr.verified / HR判定 :736-764)
  ja_v2beta.finalize_audit(audit, jr, v2b, human_review_required=result["human_review_required"])              # S3 (:784付近)
```
- `_value_layer(...)`(er007内の小関数): `v2b.active`なら `ja_v2beta.value_layer(...)`、そうでなければ従来の `_numeric_value_equivalence`(**scope外=従来コードパス**)。`JA_SECONDARY_VALUE_EQUIVALENCE_ENABLED`(`:515`)の既存意味(Secondary側適用のrollback)は維持。
- **S1P(Primary)**: v2が救済したら `classification=JA_PRON_VALUE_EQUIVALENT_MATCH`(PRON)または `NUMERIC_VALUE_EQUIVALENT_MATCH`(VALUE_ONLY)の`should_pass=True`を返す(`_READING_MATCH_CLASSIFICATIONS`に入れない=最終ANDゲートを維持)。v2が不成立ならProduction判定へフォールバック(L1 ⊇ L0)。Production既存の値等価層が受理するVALUE_ONLYは警告なし(寄与なし)、受理範囲を**超える**VALUE_ONLYのみ`JA_NEWLAYER_VALUE_ONLY_BEYOND_PROD`。
- **S1S(Secondary受理)**: 同じ`_value_layer(...,"secondary",...)`。Secondary側で新層が寄与した場合は、`unified_judge`が`done(PASS_WITH_WARNING,"secondary_confirmed")`(`er078:840-842`)を返した後、S3で`JA_NEWLAYER_*`警告を`jr.warning_labels`/`audit["warnings"]`へ追記(既存の`adapter.layers`追記パターン`er007:784-787`と同型)。
- **S2(β救済)**: 条件=`v2b.active ∧ not jr.verified ∧ jr.reason_code ∈ ELIG(前方一致) ∧ not jr.secondary_unavailable ∧ ctx.phrase_list_hash==""(M-7)`。
  1. `audit["secondary"]["text"]`があればそれを使う(`secondary_not_accepted`型)。無ければ(P1型=`p1_value_diff`でSecondary未呼出)**`precheck_composite(canon, primary)`(S:=原稿を仮定してβが成立し得るか)がTrueのときだけ**、`cache.get_or_call((sha,"azure","ja",""), lambda: _secondary_fn(ctx))`で**Secondaryを1回だけ追加呼出**(同一shaのSecondaryCache共有=重複0円。COST_GUARD・`JA_SCG`flag・circuit openは`_secondary_fn`/rsで尊重)。取得失敗は元のNGのまま(fail-closed、circuit breakerは動かさない)。
  2. `composite_judge(canon, primary, secondary, {engine:"azure", wav_sha256, model_id:"azure-speech-stt", phrase_list_hash:""})`。成立→新`JudgeResult(state=PASS_WITH_WARNING, reason_code="ja_beta_composite")`を構築(auditのstate/reason/warnings/final_gate/cost/secondary.text・`ja_v2beta.beta`〔§5〕を更新)。不成立→元の`jr`を返す。
  3. 長さ判定は変えない(呼出元の`verified_content and final_length_ok`はPrimary由来の`length_ok`を引き続きANDする。βの`adopted_from`は"primary"のまま=fail-closed)。
- **S3**: `verdict`/`rescue_basis`/`judge_rule_version`を追加(§5)。scope外(`v2b.active=False`)は**何も追加しない**(キー自体を作らない=A/B/C出力byte同一。ortho前例`er078_pass_with_warning_registry_01.py:77-(orthographic_equivalence)`と同じ流儀)。ただしscope内でM-6によりblockedなら`ja_v2beta.blocked_by`を記録。
- **共通1箇所の根拠**: seamは全てJA adapter内で、X/Y/Z Std JAの4 Section全部が通る(COVERAGE_MATRIX_01 §0-2)。FamilyごとのSection別配線は無い。
- 代替案(不採用): `unified_judge`内にフックを入れる案。英語/A/B/Cと共有の状態機械に言語固有ロジックを足すことになり、`p1_value_diff`のSecondary短絡の再設計(影響大)が要る。adapter案の方が影響範囲が小さく、`unified_judge`のregression(`er078_asr_unified_*`)を無変更で通せる。
- 循環import回避: 新moduleはer007の関数(`_scg_c2_candidate`等)を**関数内で遅延import**(`er078_secondary_run_scope_01._secondary_module()`と同型)。

## 5. 判定結果schema((c))
`asr_judgement`(`unified_judge`のaudit record)へ**additive**に追加(旧readerは壊れない。`er078_asr_unified_backcompat_07_test_01`で固定済みの方針):
```
verdict:            "PASS" | "PASS_W" | "NG" | "HR"      # state PASS→PASS / PASS_WITH_WARNING→PASS_W / 最終slot NG(human_review_required)→HR / その他NG(技術STOP含む)→NG
rescue_basis:       null | "v2" | "beta"                   # 新方式が合否に寄与したときのみ。β救済は"beta"(v2が併発しても"beta")
judge_rule_version: "ja_v2beta_r1off_01"                   # scope内の全JA判定に付与(寄与なしでも。再判定/再利用の版管理)
warnings:           [...]                                  # 既存キー(=JudgeResult.warning_labels と同一内容)。新ラベル: JA_NEWLAYER_PRON_EQUIVALENT / JA_NEWLAYER_VALUE_ONLY_BEYOND_PROD / JA_NEWLAYER_BETA_COMPOSITE (+β内部: JA_COMPOSITE_VALUE_FROM_SECONDARY, JA_COMPOSITE_PRIMARY_VALUE_GARBLE_EXPLAINED, JA_COMPOSITE_SECONDARY_READING_CONFLICT, JA_PRON_EQUIVALENT, JA_COMPOSITE_LISTEN_ADVISED)
ja_v2beta: {                                               # 寄与の有無によらずscope内で記録
  "active": true, "scope": "X|Y|Z", "blocked_by": null | "M6_E3" | "M6_E4" | "M1_irregular" | ...,
  "layers": [{"layer":"v2_pron|v2_value_only|beta","side":"primary|secondary","cause":"A3_value+A2_particle|..."}],
  "beta": {                                                # β寄与時のみ(再判定に必要な保存)
    "composite_contributed": true, "canonical_text": "...", "primary_transcript": "...", "secondary_transcript": "...",
    "secondary_engine": "azure", "secondary_wav_sha256": "...", "secondary_model_id": "azure-speech-stt",
    "reading_source": "primary", "value_source": "secondary", "explained_spans": [...], "secondary_reading_conflict": false, "phrase_list_hash": ""},
  "rescue_reason_ja": "…(最終制作報告用の人間可読文)"
}
```
- `warning_labels`という別キーは**作らない**(既存`warnings`と二重管理になるため)。registryは既に`judgement["warnings"]`を`entry["warning_labels"]`として出す(`er078_pass_with_warning_registry_01.py:61`)。Fable指定の`warning_labels`は「registry entry/JudgeResult属性」で満たす。
- 保存先(全て**既存の保存点がそのまま運ぶ**。新store無し): (1) `tts_generation_results.json`のsegment entryと`attempts_log[*].asr_judgement`(`repro01:417`付近(`attempts_log`)・`n3_tts:849`・`voice01:623,684`)=ASR結果json。(2) `audit/pass_with_warning_listening_list.json`(registryの再導出)=audit。(3) `Master Audio Store manifest["asr_judgement"]`(`er006_master_audio_store_01.py:234`)=Store manifest。再利用時は`asr_judgement_inherited`として復元(`:197`)されるので**警告・rescue_basis・β provenanceを引き継ぐ**。(4) J11継承はdeepcopy(`er019_family_x_validation_inheritance_01.py:404-416`)。
- 版管理: `judge_rule_version`が将来変わっても、`contributed`寄与entryは再利用時に現行規則で**API 0再判定**する(§6)ので、版違いの古い救済を黙って通さない。

## 6. 再利用・継承・resume整合((c)(d)関連)
| 経路 | 設計 |
|---|---|
| 同一out_dir resume | `status=OK`のentryは`_generate_or_reuse`(`er019_family_x_audio_production_runner_01.py:1248-1311`)で再利用され`asr_judgement→asr_judgement_inherited`(PASS_Wと警告を維持)。`er127`の`stub_row`/resumeは成功attemptに影響しない |
| Master Audio Store再利用 | `guard_entry`(`er078_reuse_value_guard_01.py:46`)に**新層寄与ブロック**を追加(ortho/UKUS前例`:70-100`と同型): ①`ja_v2beta.contributed(aj)`(`asr_judgement`と`asr_judgement_inherited`の両方・fail-closed検出=警告`JA_NEWLAYER_*`/`ja_v2beta.layers`/`rescue_basis`)が真で、かつ`is_active_for_run()`が偽(A/B/C scope・flag OFF)→ **再利用せず再生成**(理由`JA_V2BETA_AUDIO_OUT_OF_SCOPE_OR_FLAG_OFF`)。②scope内かつ寄与あり→保存転写で**API 0再判定**(`rejudge_contributed(entry)`: v2はPrimary保存転写+原稿、βは`ja_v2beta.beta`の保存転写+provenanceで`composite_judge`を現行規則で再実行)。NG→再利用せず再生成(`composite_reuse_decision`同型) |
| J11継承(JA) | 現行どおり保存採用転写に最終ANDゲートのみ(`:262-264`)。v2救済はPrimary転写採用(`prim.passed=True`)、β救済は`prim.passed=False`なので採用転写=Secondary転写(値が原稿と一致するため最終ANDゲートを通る)。**新層の判定核は継承側で再実行しない**(Primary再導出=LLM/API回避の既存方針)。元の警告・`rescue_basis`は`rec=deepcopy(aj)`で継承される |
| 再生成(NG→次attempt) | 不変。PASS_W attemptは`verified=True`でretry loopを終了(`repro01:413`・`n3_tts:849`の`verified`、`return {"status":"OK"...}`)。通算TTS上限3・180秒・fallback Style・Local Rewrite対象外(JA)は不変 |
| HR Lock後の人間承認 | `record_human_approval`・`HUMAN_APPROVED`は不変。USER §3-5(月6本の残り2本)の扱いは§9 |

## 7. 非ブロッキング設計((d))
- PASS_W = 既存`PASS_WITH_WARNING`。経路: `jr.verified=True` → `result["verified"]=True`・`result["human_review_required"]`は`not jr.verified`の分岐内でのみTrueになる(`er007:736-763`)ため**PASS_Wでは立たない** → `evaluate_attempt_ja_with_cascade`の`_log_human_review`(`:809-810`)不到達 → retry loopは`verified`で`status:"OK"`を返す(`repro01`/`n3_tts`/`voice01`)→ `register_ja_terminal_hr`不到達(`last_attempt.verified`で除外`er127:732`)→ `verify_episode_audio_validation_gate`は`status=OK`→`VALIDATED`(`er003_v1_n3_01_assemble.py:89,487`)→ 組立・納品候補作成を止めない。
- 不変にするもの: 通常NG・3回NG→HR Lock・E3/E4 NG・`reuse_blocked`印・明示HR Lock・HUMAN_APPROVED記録(上記§1の各line)。**PASS_WをNG/HRと混同しない**ため`verdict`で分離。
- **新規Gateを作らない**: `verdict`/`rescue_basis`/`listen_advised`を読んで制御フローを変える箇所を作らない(静的test T-N1)。報告出力だけが読む。
- **自動配信・公開機構は作らない**。最終制作報告は既存の限定共有ページ/JSON/標準出力のみ(エンドユーザー導線は別設計=USER §1A末尾)。公開前人間試聴必須条件は**復活させない**(§2-3の改名と静的testで担保)。

## 8. 最終制作報告への掲載((e))
**現状の「最終制作報告」相当artifact(file:line)**:
| Family | 既存artifact | PASS_W掲載 |
|---|---|---|
| X | 試聴ページ節 `er019_family_x_audio_production_runner_01.py:3432-3433`・`er019_family_x_listening_page_01.py:179-186`(Stage完了hook `er019_family_x_audio_production_runner_01.py:1847,2269`が`write_listening_list_safe`)、PNAP完了報告 `er103_pnap_runner_hooks_01.py:16`(英語固有名詞アラーム。flag依存) | 有(節あり) |
| Z | 試聴ページ節 `er063_family_z_audio_01.py:2716-2774`(hook `:1627-1630`) | 有 |
| Y | `audit/pass_with_warning_listening_list.json`(hook `er121_family_y_audio_01.py:762`)。試聴ページ `er121_family_y_runner_01.py:1282`の`aux_html`は音声候補のみ | **JSONのみ。ページ節が無い(欠落)** |
| 共通 | `er131_final_human_report_01.py`(LR赤/Fallback濃青の最終Human報告資料)は**未配線**(`:1-18`「どのProductionコードからもimportされない」)。PASS_Wは現在載らない | 対象外(配線済になった時点で同registryを参照させる) |

**設計(共通helper=`er078_pass_with_warning_registry_01.py`の拡張。新store・新Gateなし)**:
1. `_entry()`(`:51-`)に `verdict`/`rescue_basis`/`rescue_reason_ja`/`judge_rule_version`/`listen_advised` を追加(キーが無い旧recordは`None`で従来表示のまま=byte互換)。
2. `render_html_section()`(`:198`)に列「新方式(v2/β)」「救済理由」を追加し、`rescue_basis`付きを先頭にグルーピング。文言は「公開をブロックしません。事後に試聴して確認してください」を維持し、新方式分には「試聴推奨(任意)・制作は止めません」と明記。
3. 新関数 `render_completion_block(entries, level_label)` と `emit_completion_block(run_dir, level)`(`write_listening_list_safe`と同契約=例外を投げない、失敗は「導出失敗(要確認)」)。既存の`write_listening_list_safe`呼出点(X `:1847,2269` / Z `:1630` / Y `:762`)の直後で**標準出力へ**「【日本語ASR PASS_W(新方式)】N件: 対象音声(segment_id/音声path/sha)・発生理由・警告ラベル・原稿/Primary/Secondary転写」を出す(=最終制作報告に載せる文)。
4. Yの試聴ページ(`er121_family_y_runner_01.py:1282`)の`aux_html`に`render_html_section(load_listening_list(...))`を連結(X/Zと同じ補助表示。`er_user_listening_page_common_01.py:312`の`_AUX_MARK_RE`が補助節を許容)。
5. 生成されるJSON(`audit/pass_with_warning_listening_list.json`)が、Fable/Claudeの最終ユーザー報告(`★★★★`ブロック)の入力。`count_by_rescue_basis`を追加して集計を1行で出せるようにする。
**報告例(月題の想定。実データは02A)**: 「PASS_W(新方式) 4件: ms_03 a2〔v2: 助詞は→わ+桁区切り〕・ms_03 a3〔β: 数値=Azure/読み=OpenAI、Azure='杉野氏'と読み相違あり・試聴推奨〕・reselect a1,a2〔v2〕。要HR 2件: ms_03 a1・reselect a3(通常NG→HR Lock経路)」。

## 9. 既定ON・緊急OFF flag((f)。Fable/Opus判断の論点)
- 既定: `JA_V2_BETA_ENABLED = True`(`APPROVED_FOR_PRODUCTION`、USER §1A-1)。**単一読取関数 `is_active_for_run()`**(= flag ∧ `er109_xz_scope_01.current_scope()`∈{X,Y,Z})のみが他moduleから参照される。env/引数/設定dict/起動scriptからONにもOFFにもできない。
- 案F1(推奨): 上記のモジュール定数1個(rollbackは定数をFalseにする1行のcommit)。前例=`READING_MATCH_FINAL_GATE`(`er078:80`)・`JA_SECONDARY_VALUE_EQUIVALENCE_ENABLED`(`er007:515`)・er109 flag。利点: 誤PASS発覚時に即座に従来挙動(新層なし)へ戻せる。OFF時の副作用=新層寄与entryはStore再利用がブロック(再生成費用が出る。ortho前例と同じ)。
- 案F2: 緊急OFF flagなし(戻す場合はrevert commit)。利点: 経路が最小。欠点: 戻し作業が重く、Store内の寄与entryの扱いが定数なしでは制御できない。
- 論点: 「flagを置くこと自体が『承認済み機能に迂回路を作る』」ことにならないか。→ 値の変更はソース編集+commitのみで、実行時迂回は無い(AST testで読取関数以外の参照ゼロを固定)。

## 10. 汎用性の担保((g))
- 題固有語・記事固有語を持たない: 新moduleのソースに題由来の語(月・しわ・詩・超・岩・8,900等)を含まない静的scan(allowlist: 助詞「は」「へ」、数詞文字〇零一〜億兆、桁区切りカンマ)。
- 汎用題のpositive/negative: 売上・参加者・価格・距離・年齢など≥10題でv2/β positive、同構造の負例(値違い・桁違い・助数詞違い・脱落・否定)で誤PASS増分0(TEST_PLAN T-G)。
- metamorphic test: 月題positiveの名詞句を別名詞へ置換しても判定カテゴリが不変。

## 11. 変更ファイル一覧と影響範囲((h))
| ファイル | 種別 | 変更 | 影響 |
|---|---|---|---|
| `er078_ja_v2beta_01.py` | **新規** | §2のロジック・flag・版・`finalize_audit`・`rejudge_contributed`・`contributed` | scope外では呼ばれても副作用0(`is_active_for_run()`偽) |
| `er007_ja_secondary_asr_01.py` | 編集 | seam S0〜S3(`:575-577`後/`:595`/`:631`/`:677`/`:691`直後/`:784`付近)。他は無改変 | X/Y/Z+(共有のため)A/B/Cが通る。**scope None=従来出力byte同一**をT-Aで固定 |
| `er078_reuse_value_guard_01.py` | 編集 | `guard_entry`に新層寄与ブロック(§6)+API 0再判定 | A/B/C共有Store。印の無いentryには作用しない |
| `er078_pass_with_warning_registry_01.py` | 編集 | §8の列・helper追加(旧record互換) | X/Y/Z/legacy A/B/Cの試聴リスト出力。旧keyのまま読める |
| `er121_family_y_runner_01.py` | 編集 | Y試聴ページ`aux_html`に節を連結(`:1282`) | Yのみ |
| X/Z runner hook呼出点(`er019_..._runner_01.py:1847,2269`・`er063:1630`・`er121_family_y_audio_01.py:762`) | 編集(各1行: `emit_completion_block`) | 非ブロッキング | 各Familyのstage完了時の標準出力のみ |
| `er078_asr_unified_wiring_static_audit_01.py` | 編集 | allowlist/到達性(er007→新module→er109_xz_scope_01) | 静的監査test |
| `er109_xz_isolation_01_test_01.py` | 編集 | scope importer固定リストへ新module追加 | **HEADで既に3 fail(drift)。TEST_PLAN §0** |
| `er078_asr_unified_judge_01.py` | **無改変** | - | 英語/A/B/C回帰リスク0 |
| `er006_master_audio_store_01.py` | **無改変** | `asr_judgement`は既存保存点が運ぶ | - |
| `CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`USER_DECISION_REGISTER_01.md` | 委任_03で更新 | §12 | - |
- **Family A/B/C**: 共有基盤(adapter・guard・registry)を通るが、新層はscope Noneで非活性。互換性確認のみ(編集0、T-Aでbyte同一)。27-7に従いA/B/Cの開発・Trial・API 0以外の実費は発生させない。

## 12. 撤去・残置の確認((i)。Charter原則8)
- **撤去する旧規則・旧検査: なし**。理由: (1)`_numeric_value_equivalence`/`_digit_group_comma_only_diff`(`er007:519-557`)は新層のフォールバック(L1 ⊇ L0)かつA/B/C(scope外)の現役規則のため残置。(2)β/v2の凍結protoは`docs/research/`の根拠資料として残置(Productionからimportされない既存testは維持)。
- 新設時に**同時に外す**もの: protoの`sys._getframe`によるside推定、monkeypatch差替え、`listen_required`の「試聴必須」意味、R-1・L3・合意再試行・best-of-N・veto。
- 旧記述の是正(SSOT、委任_03): `CURRENT_SPEC.md:2925/2927`付近「新方式は試聴必須」の記述が無いか(Grep)と、`OPEN_ITEMS` OPEN-515/517関連の「J1/β保留」記述を最新決定へ更新。
- 残存Grep確認(02で実施): `grep -rn "JA_V2_BETA_ENABLED"`=定義1+読取関数1のみ / `grep -rn "JA_COMPOSITE_LISTEN_REQUIRED"`=0(Production)/ `grep -rn "r1_block\|KUNYOMI_OKURIGANA\|consensus(" er*.py`=Production 0。

## 13. UDR整合表((6))
UDR=`docs/pm/USER_DECISION_REGISTER_01.md:548-556`(#201〜#207)。ユーザー決定=`..._USER.md`。
| ユーザー決定(2026-10-29) | 該当UDR | 判断済みになる内容 | 備考 |
|---|---|---|---|
| §1A-1 v2+β 正式採用(`:11`)+§3-1 R-1 OFF(`:63`) | **#201**(v2採否)・**#202**(β採否)・**#207付随論点**(R-1採否) | #201=採用、#202=採用(`APPROVED_FOR_PRODUCTION`)、R-1=OFF(=区別不能な同音異表記T1は受理する側) | #202のFable旧推奨「当面不採用」は決定により失効 |
| §1A-2 ASR再試行不採用(`:12`) | **#204** | 選択肢(a)不採用(現行維持)。(b)合意規則・(c)best-of-Nとも不採用。`CURRENT_SPEC.md:2926`(Primary#2廃止)を維持 | |
| §1A-3 「超→こえ」等の非標準読み救済の追加方式は不採用(`:13`) | **#205** | 選択肢(a)受理しない(別表L3・辞書拡張とも不採用) | **(c)TTS入力側の読み固定(v-a)は決定文に無く未判断のまま**。救済ではなく発生源対策で、ms_03 a1型の再発防止のみ。本IDの停止根拠ではなく独立事項(分類C)。再提示トリガー=「超え」型の誤NGが再発した時 |
| §1A-4 HUMAN_APPROVED方式で承認した音声は最終PASS(`:14`) | **#207**(本体) | (a)HUMAN_APPROVEDを最終判定PASSに数える。USER §3-5は「6本すべて機械PASS」を合格条件にしない | 既存HUMAN_APPROVED記録は不変(§1) |
| 量産時PASS_Wは試聴を必須条件としない(`:18-26`、§3-2) | **#206** | 非ブロッキングの事後試聴(公開前試聴必須にしない)。新方式PASS_Wは`JA_NEWLAYER_*`で既存PASS_Wと別枠集計(M-2) | 「公開前人間試聴必須条件の復活禁止」(`:26`)を§7・§2-3で担保 |
| (本IDの対象外) | **#203**(月Std題6音声の試聴判断・採用方法・記事単位承認) | 本IDでは扱わない。記事『月は少しずつ縮んでいる？』の公開差替えを行わない(USER §3-5末尾) | 6音声の再掲は事実の再掲のみ |
→ #201,#202,#204,#205(a),#206,#207 は2026-10-29のユーザー決定で**判断済みになる**(SSOT更新は委任_03)。残るのは#203と#205(c)のみ(どちらも本配線の停止根拠ではない)。

## 14. 判断候補・Opus論点(停止根拠file:line付き)
本設計でユーザー判断(`USER_DECISION_REQUIRED`)に値するものは**ない**(下は全てFable/Opus判断またはB=承認範囲内)。
| # | 論点 | 分類(27-3) | 根拠 | 推奨 |
|---|---|---|---|---|
| J-1 | 緊急OFF flagの要否 | B(承認範囲内。Fable/Opus判断) | 前例 `er078_asr_unified_judge_01.py:80`・`er007_ja_secondary_asr_01.py:515`(単一定数で戻す)。USER原文に禁止も指定も無い(`..._USER.md:11`,`:55-63`) | F1(定数+読取関数1個)。§9 |
| J-2 | Yの試聴ページに事後試聴リスト節が無い | B(最終制作報告を載せるための補完) | `er121_family_y_runner_01.py:1282`(aux_htmlは音声候補のみ)vs X `er019_family_x_listening_page_01.py:179-186`・Z `er063_family_z_audio_01.py:2716-2774` | 02でY節を追加(§8-4) |
| J-3 | β「Secondary読み相違=warn」(Azureが別内容を聞いたケース)の扱い | B(承認済みTrial構成そのもの) | `b_light_proto_02.py:258-264,277`・EVAL_UNIFIED_03.md §1B(ms_03 a3はAzure='杉野氏'でPASS_W)・USER §3-5「残る2本のHR」=ms_03 a1・reselect a3(`..._USER.md:139-140`)。a3はPASS_W側に入る前提 | Trial構成どおり`warn`固定。ただし**試聴必須でなくなる**ため02Aで実音声のN3負例に対する誤PASS増分を再実測し、増分が既知(T1 6+T2 2)を超える場合のみFableへ報告(TEST_PLAN T-R) |
| J-4 | HEADで既に失敗している関連test 5件(`er007_ja_secondary_asr_01_test.py` 2件、`er109_xz_isolation_01_test_01.py` 2件、`er078_asr_unified_wiring_05_test_01.py` 1件) | 新規OPEN候補: **修正へ進む**(本件の合格基準を曖昧にするため02の冒頭で原因確認→最小是正。期待値は現行承認済み仕様[Variant Layer Candidate B/E、OPEN-333]と照合) | TEST_PLAN §0(HEAD実測) | 02冒頭で是正(承認済み仕様との矛盾の是正は不具合=11-8の範囲内) |
| J-5 | Opus条件Aレビューの要否 | 手順(CLAUDE.md Opus Gate) | 新しい処理フロー設計(adapterのseam追加・Store寄与ガード追加)に該当 | 実装前に1回。論点: (1)adapter案 vs unified_judge案 (2)β追加Secondary呼出の費用/circuit扱い (3)Store寄与ブロックのscope外再生成の費用 (4)緊急OFF (5)T1/T2の非ブロッキング化後のリスク |
