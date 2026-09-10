## 要点(5行)

1. Production core差分は概ね「承認済み設計の範囲内の是正+既存関数の再利用」に収まっており、**commitをブロックする重大欠陥は検出されなかった**。
2. ただし1点だけ「移設」ではない挙動追加がある: content integrity checkはTrialでは**record-only(TTS後)**だったものが、Production では**fail-closed STOP(scaffold内)**になっている(安全方向だが2Vには無い非対称、REPORT 13-2の書き方が「ロジックそのまま移設」に寄っている)。
3. 2V regressionは実質担保されている: `ValueError`化の対象呼び出し元はゼロ、`point_three_heading`追加は「存在するsegmentのみ判定」ロジックのためA-Family/2Vにfalse rejectを生まない、Comment 3文言をpinする既存テストは無い。
4. Dangling Referenceは重大なものなし(Ledger実ファイル・記事側Trialとの**同一Ledger**まで一致確認)。軽微な不整合が3件(未使用定数`THEME_3V`、3V scaffold summaryにdeviation status欠落、「2重定義解消」の記述と実態)。
5. 実行(¥150 cap)前に片付けるべきMED課題が1件: `run_tts_3v()`に**予算ガードが1つも無い**(2V `run_tts()`は5回`assert_budget_ok`)。commit自体は可だが、3V実発火前には対処が要る。

---

## 論点1: Production core差分の正当性

### 1-a (MED) content integrity checkは「移設」ではなく「移設+fail-closed化」
- 根拠: Trial側 `C:\Users\tensh\eigo-radio\er012_editorial_b_voices_3v_audio_trial_01.py` L879-903 は結果を`save_json`して返すだけで、呼び出しは L956(**ttsステージ内=TTS後**)、NGでも停止しない。Production側は `C:\Users\tensh\eigo-radio\er012_b_family_voices_production_01.py::run_content_integrity_check_3v()`(pure関数、ロジックは同一)+ `C:\Users\tensh\eigo-radio\er012_b_family_production_runner_01.py::run_scaffold_3v()` L785-789 で `RuntimeError("[CONTENT_INTEGRITY_STOP]...")`。
- 評価: 判定ロジック自体は同一(テスト`test_matches_trial_function_output_for_same_input`で同値をpin)なので「新QA基準の発明」ではないが、**pipelineをブロックする合否判定としては新規**であり、かつ2V B1/A2経路には同等gateが無い(3Vのみfail-closed)。方向は安全側。
- 提案: REPORT 13-2へ「Trialはrecord-only、Productionはfail-closed STOP(=挙動追加、2V非対称は意図的)」を1行明記。コード変更は不要。

### 1-b (MED) `run_tts_3v()`に予算ガードが無い(2Vとの非対称、Phase 1由来)
- 根拠: 2V `run_tts()`(runner L303-382)は`assert_budget_ok`をtopic_intro後/comment後/heading後/Voice A/B後/Hook他後の**5箇所**で呼ぶ。3Vは本体が`er012_b_family_voices_production_01.py::run_tts_3v()`へ移り、この関数内に予算チェックが1つも無い(runnerをimportできないため構造上呼べない)。`main_b1_3v()`は L1066 の**TTS全完了後**にしか`assert_budget_ok_3v`を呼ばない。
- 影響: `BUDGET_JPY_CAP_3V = 150.0`(runner L649)が事後判定になり、3声ぶんのTTSを全部撃ってから超過を知る。
- 提案: `run_tts_3v(..., budget_check_fn=None)`(既定None=現挙動)を追加し、runnerから`assert_budget_ok_3v`を渡す。commit前でも後でもよいが、**3V実走前には必須**。

### 1-c (LOW-MED) integrity checkの実行位置がsupport text生成(LLM 5回)の後
- 根拠: `run_scaffold_3v()`はComment 1-4+Preview生成→保存→L783でintegrity check。parserの抽出誤りは`build_parts_3v()`時点で確定しているので、LLM課金前に検出できる。
- 制約: 現実装は`kp_merged`(key_phrases/keywords_canonicalized.json)を必要とするため、`prepare_3v()`直後ではなく`kp_reuse`後に置く必要がある。
- 提案: `main_b1_3v()`の`kp_reuse`直後へ移すか、section本文チェックのみ先に走らせる。任意(safety上の必須ではない)。

### 1-d (LOW) STOP判定に含まれない項目がある
- `all_section_bodies_verbatim_from_article` は `hook_part1_and_part2_reconstruct_hook_body` を**除外**して算出(production_01.py L299)、`key_phrase_used_form_appears_in_article`も判定外。Trialと同一なので意図どおりと読めるが、「Hook分割ミス・Key Phrase不在は記録のみでSTOPしない」ことをREPORTに1行残すと後任が誤解しない。

### 1-e (OK) Tension語数の観測ログ
- `compute_tension_segment_word_count_3v()`(production_01.py L310-326)は`ab01.compute_word_count`の再利用のみ、閾値・status・gateキーなし。テスト`test_result_has_no_pass_fail_field`で"status/pass/gate/overall_status"不在をpin。**新QA基準の混入なしと判断**。
- 新規import `er003_v1_en_direct_ab_01_generate`(production_01.py L64)は、既にProduction module `C:\Users\tensh\eigo-radio\er012_b_family_voices_a2_production_01.py` L56 が同じくmodule-level importしている前例と同型。新種の依存クラスではない。

### 1-f (OK) Ledger Deviation接続は2Vと同一
- 2V: runner L293 `vfl01.run_deviation_check(client, ledger_text, support_concat)` → parsedをsave、**status評価なし(monitoring専用)**。3V: L797-798 で完全に同一の呼び方・同一の非gate。失敗時挙動(例外は上位へ伝播しstage停止)も同一。新閾値・新判定なし。

### 1-g (OK) Voice衝突ガードは2Vで誤発火しない
- 衝突判定は`resolve_voice_names_3v()`(production_01.py L422-432)内のみ。2V `resolve_voice_names()`は無変更、呼び出し元は`voice_check()`/`voice_check_a2()`のみ。2Vのfallback対は`Algieba→Schedar`/`Erinome→Sulafat`で相互衝突は原理的に発生しない。**2V誤発火リスクなし**。

### 1-h (MED、運用注意) Voice A一過性失敗が3V全体STOPになる
- `generate_voice_sample_single_take()`はASR検証・retry cascade無しの単発生成。Algiebaのsampleが一時的に失敗しただけで`voice_a→Schedar`となり`voice_c`と衝突→`[VOICE_COLLISION_STOP]`で全停止する。ユーザー決定(Voice 3の代替を発明しない)とは整合するが、**運用上は「一過性失敗=全停止」**。
- 提案: REPORTの運用注記へ「衝突STOP時はまず`voice_check`ステージのみ再実行して一過性か切り分ける」を追記(コード変更なし)。

---

## 論点2: 2V regressionの実質

| 観点 | 所見 | 根拠 | 重大度 |
|---|---|---|---|
| `ValueError`化が既存呼び出しを壊すか | **壊さない**。`voice_c`/`"b1_3v"`を渡す既存呼び出しは1件も存在しない | 全呼び出し元は`C:\Users\tensh\eigo-radio\er011_open129_structural_completeness_production_wiring_evidence_01.py` L84/L86(いずれも2引数)とテストのみ | — |
| 2V出力のbyte不変 | テストで固定済み(`test_voice_c_omitted_matches_pre_existing_2v_b1_output`、`test_voice_c_explicit_none_is_identical_to_omitted`) | 期待値をハードコードした比較 | — |
| `point_three_heading`のGate辞書追加 | **A-Family/2Vへ影響しない**。`_segment_missing_mandatory_disfluency_qa()`(`C:\Users\tensh\eigo-radio\er003_v1_n3_01_assemble.py` L191-195)は「記録に存在するsegmentのみ」判定し、不在は不問 | 実装確認済み。A2/B_FAMILY_A2非波及もテストでpin | — |
| fail-open/fail-closedの向き | 追加はすべてfail-closed(衝突STOP・integrity STOP)、緩和方向の変更はゼロ | — | — |
| Comment 3役割行変更のテスト影響 | **なし**。既存pinは`"なぜ違って感じるのか"`のみで、変更した「どちらが正しいか」文字列をpinするテストは repo 内に存在しない | `C:\Users\tensh\eigo-radio\er012_editorial_b_family_production_phase1_test_01.py` L299-305 | — |
| Comment 3変更のA2日本語出力への波及 | **潜在的にあるが、現行A2 Production runnerの出力は変わらない**。A2の日本語Commentは`C:\Users\tensh\eigo-radio\er012_b_family_voices_a2_production_01.py` L485-503 が`registry.COMMENT_ROLES`を共有するが、`main_a2()`はComment音声を**承認済みbyte再利用**(`A2_SEGMENTS_TO_REUSE`)しており`run_scaffold_a2()`を呼ばない。将来A2 Commentを再生成した時点で文言が変わる | runner L1415-1464、L1117-1121 | LOW-MED(要ユーザー認識) |
| Comment 3プロンプト内の表現混在 | タイトル行は「どちらが正しいか」のまま、役割行のみ「どの声が正しいか」。同一プロンプト内に両表現が同居する状態(ユーザー判断待ちのため意図的) | registry L144 と L147 | LOW(判断待ち事項) |
| 2V本体コード | `run_scaffold`/`run_tts`/`build_b1_voices_timeline`/`main()`の2V分岐はいずれも無変更を読み合わせで確認 | runner L250-382、L1483-1537 | — |
| regression実測 | 2301件中2298 PASS/failed 3(`er003_test_p2j_investigate.py`のみ)というREPORT記述は、本レビューでは**ログ実物を再実行検証していない**(読み取り専用のため)。既知failが「テスト総数カウント照合」型であれば、今回テスト数が48/81へ増えたこと自体で数値がズレる性質のfailである点に注意 | REPORT 14-6 | LOW(commit時に「新規failでない」ことの1行確認を推奨) |

---

## 論点3: Dangling Reference

- **OK(強い根拠あり)**: `LEDGER_PATH_3V`(runner L643)は実在(`C:\Users\tensh\eigo-radio\er012_output\ai_screening_ledger_trial_01\research\verified_fact_ledger.txt`)。さらに、3V記事の出典である `C:\Users\tensh\eigo-radio\er012_editorial_b_voices_3v_person_voice_trial_02.py` L132-133 が**同一Ledger**を使って記事を書いている(REPORTはファイル実在のみ記載)。Deviation Checkの入力整合性は担保されている。REPORT 14-7へ「記事側Trial-02と同一Ledger」の1行追加を推奨。
- **OK**: 新エラー種別 `[VOICE_COLLISION_STOP]` / `[CONTENT_INTEGRITY_STOP]` は既存の `[TEXT_HASH_MISMATCH]` / `[BUDGET_GUARD]` / `[ASSET_HASH_MISMATCH]` / `[REUSE_SOURCE_NOT_OK]` と同じ角括弧大文字規約で整合。
- **OK**: `run_scaffold_3v(`の呼び出し元は定義+`main_b1_3v()` L1057のみで新signature追随済み。`resolve_voice_names_3v(`も定義+`voice_check_3v()`のみ。
- **(LOW) 記述と実態のズレ**: registry L316-317 のコメント「Trial側の暫定正本はregistry側へ統合され(2重定義解消)」は、実際にはTrial側 `er012_editorial_b_voices_3v_audio_trial_01.py` の `build_required_structure_3v()` / `run_content_integrity_check()` が**物理的に残存**している(Trial無変更方針のため意図的)。「正本宣言であって削除ではない/テストで同値をpin」と書き分けるのが正確。
- **(LOW) 未使用定数**: `THEME_3V`(runner L651)はリポジトリ全体で他に参照ゼロ。削除または用途コメント。
- **(LOW-MED) 監視可視性の非対称**: 2Vは`scaffold_summary.json`に`deviation_overall_status`を入れる(runner L1511-1513)が、3Vは`support_status`のみ(L1058-1059)。Deviation Checkはmonitoring専用なので、人が見るrollupに出ないと接続した意味が薄れる。**1行で対称化可能**。
- **(LOW) audit名の非対称**: 3Vだけ`support_ledger_deviation_3v.json`/`content_integrity_3v.json`と接尾辞付き(出力先ディレクトリが既に別なので冗長)。Trial側は`content_integrity_check.json`で名前が違う。害はないが突き合わせ時の混乱要因。
- **(SSOT、commit時タスク)**: `HISTORY_INDEX.md`に本レポート(`EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1-01_REPORT.md`)の行が無い。また Phase 1b は別管理ID(`...PHASE1B-01`)でありながらPHASE1-01レポート内の章として同居。SSOT反映はPM Closeout Mandatory Checkの対象で、commit可否そのものとは別軸。

---

## 論点4: commit可否の材料(決定はFable/ユーザー)

**Blocking(これが無いとcommit不可): 該当なし。**

**commit前に直すと安いもの(いずれも軽微):**
| # | 内容 | 重大度 | コスト |
|---|---|---|---|
| A | REPORT 13-2へ「Trial=record-only → Production=fail-closed STOP(挙動追加、2V非対称は意図的)」を明記 | MED(記述の正確性) | 文書1〜2行 |
| B | 3V `scaffold_summary.json`へ`deviation_overall_status`を追加(2V対称化) | LOW-MED | コード1行 |
| C | REPORT 14-7へ「Ledgerは記事側Trial-02と同一」を追記 | LOW | 文書1行 |
| D | registry L316-317の「2重定義解消」表現を「正本宣言(Trial側は据え置き、テストで同値pin)」へ修正 | LOW | コメント1行 |

**commit後・3V実発火前に必須:**
| # | 内容 | 重大度 |
|---|---|---|
| E | `run_tts_3v()`への予算ガード配線(`budget_check_fn`既定None)。現状は¥150 capが事後判定 | MED |

**ユーザー判断待ち(コード修正の可否そのものが未決):**
- Comment 3タイトル行・Comment 4の「どちらが正しいか」を汎用化するか。
- 上記変更がA2日本語Comment(将来の再生成時)へ及ぶことの承認。

**総合所見**: A〜Dは文書中心の軽微修正。「このままcommit」でも技術的破壊はなく、「A+Bだけ直してcommit」が費用対効果は最も高い、という材料を提示する。Eはcommit判断ではなく実行判断の前提条件。

---

## 見落とし候補(未確定・要確認)

1. `run_scaffold_3v()`は`key_phrases/keywords_canonicalized.json`を読むため、**stage="scaffold"単独実行はkp_reuse済みが前提**(2V `run_scaffold`には無い新依存)。`all`順序では問題なし。単独ステージ実行の手順書へ注記が要る。
2. 衝突STOP時の`audit/voice_resolution.json`は`{"status": "VOICE_COLLISION_STOP", ...}`のみで`voice_a`キーを持たないため、後続の`stage="tts"`単独実行は`KeyError`で落ちる(停止自体は正しいが、メッセージが不親切)。
3. `run_assembly_3v()`はopt-in構造Gate(OPEN-129)へ`required_structure`を渡さない(2Vと同じ非mandatory運用、意図的)。つまり registry の 3V required_segments は**Production実走経路では今も検証されない**(evidence取得スクリプト専用)。「registryが正本」という位置づけと実効性の差は認識しておくべき。
4. `er003_test_p2j_investigate.py`の既知fail 3件が「テスト総数カウント照合」型なら、今回テスト数が増えたこと自体で数値が動く。commit時に「fail内容が従前と同一(新規failではない)」ことを1行確認しておくと安全。
5. 本レビューはregressionログの実物再検証・実行を行っていない(読み取り専用制約)。REPORT 14-6の数値はコードとの整合のみ確認した。
