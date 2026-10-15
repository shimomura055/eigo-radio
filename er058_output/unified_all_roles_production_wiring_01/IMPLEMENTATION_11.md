# IMPLEMENTATION_11 (AUW 委任_11, 2026-10-16 JST)

管理ID: `ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01` 委任_11。到達上限Status: `AUW_EVIDENCE_COMPLETE_PENDING_FABLE_15` には**到達していない**(下記の未取得evidenceが残るため。`PRODUCTION_WIRED`は宣言しない)。

## 1. U1発効(実施済み)

| 項目 | 内容 |
|---|---|
| 変更 | `er078_asr_unified_judge_01.py:73` `U1_KEEP_C1_SIMILARITY_EXCLUSIONS = True` → `False`(1行)。コメントを「委任_11発効。True=旧挙動ロールバック用」へ更新 |
| 効果 | JAの類似度<0.4(A5)・C1固有名詞差(A6)のP2事前除外が無効化され、Primary NGなら原則Secondaryへ回る。A1/A2(数値・否定)、A3(length、§3)、A4(C2同形異音)、**A7(登録読み保護)は不変** |
| 判断根拠 | Fable判断: s1は非該当(委任文「前委任の受入記録」)。委任_10のlive負例でPrimary PASSの3件(N1/N2/N4)は U1 True/False で同一・Secondary不呼出=U1と因果なし |

### α test更新(旧挙動固定→解放後期待。βは不変)
1. `er078_asr_unified_ja_wiring_test_01.py::test_u1_constants_unchanged` — assertを `is False`。
2. `er078_asr_unified_wiring_10_test_01.py::test_u1_default_state_documented` — assertを `is False`。
3. `er078_asr_unified_judge_01_test_01.py::test_u1_flag_releases_a5_a6_in_one_line` — 先頭assertを `is False`(委任文の一覧外の1件。`IMPLEMENTATION_10.md` §3の7番。既定値に依存していたため追加更新)。
4. `er007_ja_scg_phase0_regression_test_01.py`(旧挙動固定5 test):
   - `test_rescue_success_7_groups_pass` — g8のNOT_APPLIED期待を削除(8 audio全てverified)。
   - `test_g7_short_text_similarity_below_0_4_not_executed` → `..._released_by_u1`(n==1・verified)へ改め、旧挙動は新規 `test_g7_short_text_old_behavior_under_u1_rollback`(`U1=True`をmock.patch)で維持。
   - `test_every_row_matches_phase0_secondary_pass_judgement` — g7(ratio<0.4)/g8を実行対象へ。executed 21→23・passed 13→15。
   - `ProductionConditionRegression::test_g8_excluded_by_implementation_not_fixture` → `test_g8_released_by_u1_not_excluded`(azure 1回・verified)+旧挙動 `test_g8_old_behavior_under_u1_rollback`(`U1=True`)。
   - `test_rescue_and_c_group_under_production_conditions` — 期待pass 13→15(g7/g8追加)。C群5行は解放後もNG(誤受理0)。
5. β期待値(数値・否定・C群誤PASS・A7・A4)は変更なし。ロールバックtest(`U1=True` monkeypatch)は維持(`test_u1_true_rolls_back_to_previous_exclusions` ほか)。
6. 新規 `er078_asr_unified_wiring_11_test_01.py`(6 test): U1既定False・低類似度/C1がSecondaryへ・A7維持・ロールバック・A1/A2/A4維持・harness事前検査(tension_body欠落でAPI前に停止)。

## 2. 実音声evidence(harness: `er078_auw_runtime_evidence_11.py`、06b `begin/finish`を再利用、隔離=evidence_11/<part>)
結果の詳細は `RUNTIME_EVIDENCE_06.md` §17。

## 3. A3是正(OPEN-388): **条件付きSTOP s4により是正を保留(設計案のみ)**

### 3-1. 呼出元の一覧(Primary由来 `length_ok` をANDに使う箇所。Grep `and length_ok`)
| # | ファイル:行 | 備考 |
|---|---|---|
| 1 | `er003_v1_crosslevel_audio_02_common.py:368` | EN(A2 minimal fallback)。`length_ok`を判定ctxへ渡さない |
| 2 | `er003_v1_n3_01_tts_generate.py:734` | JA(`length_ok=`を`evaluate_attempt_ja_with_cascade`へ渡す:731) |
| 3 | `er003_v1_repro01_main_generate.py:366` | EN |
| 4 | `er003_v1_repro01_main_generate.py:388` | JA(`length_ok=`:384) |
| 5 | `er003_v1_sing01_news_tail_fix.py:212` | EN(narrator広帯域) |
| 6 | `er003_v1_sing01_point_headings_aoede.py:132` | EN(見出し) |
| 7 | `er003_v1_sing01_voice01_generate.py:255` | EN |
| 8 | `er003_v1_sing01_voice01_generate.py:527` | JA(`length_ok=`:524) |
| 9 | `er003_v1_sing01_voice01_generate.py:579` | JA(`length_ok=`:576) |
| 10 | `er012_b_family_voices_production_01.py:557` | Family B Voice本文 |
(ほかlegacy/Trial scriptあり: `er003_v1_b1_scaffold_audio_*`・`iran01`・`sing01_audio_generate`・`er010_no9_*`・`er038_*`・`er057_*`・`er058_kp_*`。Production正式経路は上記10箇所・7ファイル。`er006_secondary_asr_01.py:920`はEN側が`actx.get("length_ok", True)`で、ENではA3事前除外が事実上発火しない)

### 3-2. s4に該当する理由
A3是正の本体(judge内: Secondary受理時にSecondary転写でlength再評価、A3をP2除外から外す)は局所変更で書ける。しかし**各呼出元が `verified = verified_content and length_ok`(Primary転写由来のlength)で最終ANDを取っている**ため、judgeだけ直すと「Secondaryを呼んだ(費用が発生)のに呼出元ANDでNG」となり**現状(Secondary不呼出で再生成)より悪化**する。これを避けるには上記10箇所(7ファイル、うち4箇所はJAの`length_ok`渡し)のAND修正が必要=委任文のs4(5箇所以上)に該当。HR Lockの変更は不要。よって是正を実装せず保留した(judge側だけの部分実装は行わない)。

### 3-3. 設計案(Fable判断用)
- D1(推奨・最小): judgeの`AttemptCtx`に`max_len: int | None`を追加し、`JudgeResult.audit_record["length"]={"primary_ok":..,"adopted_ok":..,"adopted_from":"primary|secondary"}`を出す。`_exclusion_hit`からA3を外し、Primary NGでもSecondaryへ回す。Secondary受理(PASS_WITH_WARNING候補)時のみ、Secondary転写長で再評価し、NGなら`NG_BOTH`(reason=`secondary_length_ng`)。呼出元は共通helper `er078_asr_unified_judge_01.final_length_ok(length_ok_primary, detail)` を呼ぶ形で10箇所のAND(`verified_content and length_ok`→`verified_content and final_length_ok(length_ok, detail)`)を置換、JA 4箇所は`max_len`も渡す。Primary PASS時は従来どおりPrimary length。
- D2(代替): 呼出元ANDに触れず、cascade wrapper(`evaluate_attempt_with_cascade`/`_ja_`)の戻り値`verified_content`にlength結果を内包させ、呼出元側の`length_ok`変数をwrapper経由で上書き(detail_outで返す)。呼出元は結局変更が要る(変数上書きは不可能)ため不採用。
- 影響: 10箇所・7ファイル(Production TTS生成の中核)。回帰範囲が広く、Opus独立レビュー不要(U1R-04で方向性は示済み)だが、実音声Regression(長さ超過事例)と全callerのunitが必要。想定作業 90〜120分。
- 保存データのA3作用件数(API 0、`er0*_output`の`*.json/*.jsonl`を走査): `"length_ok": false` が **216件(104ファイル)**、`true` が16194件。うち**統一judge導入後の記録(`asr_judgement`併存)は0件**(`p2_exclusion:A3_LENGTH_NG`の記録も全repoで0件)。=Production実績上、A3が実際に作用した記録は存在しない(ENはctxへlength_okを渡さないため事前除外自体が発火せず、JAのみ)。長さ超過(旧記録216件)は全てpre-AUW attempt。

## 4. その他
- OPEN: `-k test_g`の件数差(5 passed、期待3)の原因=`-k`が部分一致のため `test_genuine_secondary_error_still_unavailable` 等も選択される(軽微。不具合ではない)。
- 費用: §2/RUNTIME_EVIDENCE_06 §17。
