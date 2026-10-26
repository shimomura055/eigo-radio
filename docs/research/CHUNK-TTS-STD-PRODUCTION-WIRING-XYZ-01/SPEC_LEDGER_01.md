# SPEC_LEDGER_01 — ユーザー原文§2「Chunk分割の正式Production Wiring」の要求項目台帳

管理ID: CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_01(2026-10-26)。原文(逐語・案件A/B共通)=`docs/pm/delegation_log/2026-10-26_CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01_USER.md`。
Status語彙: `IMPLEMENTED_PENDING_EVIDENCE`(コード+遮断下test PASS、正式runtime evidence未取得)/ `DESIGN_READY`(設計のみ、実装は次委任)/ `NOT_STARTED`。**PRODUCTION_WIREDは本委任では付与しない**(正式runtime evidence取得後にFable判定)。

## 1. 承認仕様(原文§2の表)
| Family | 分割方式 | 追加ポーズ | 対象 |
|---|---|---|---|
| X | 段落境界分割(Trial B0.2) | 0.2秒 | Standard／Advanced |
| Y | Family Xと同じ | 0.2秒 | Standard／Advanced |
| Z | 約70語を目安とした段落境界分割(B_r1) | 0.2秒 | Standard／Advanced |
Status(原文)=APPROVED_FOR_PRODUCTION、目標=PRODUCTION_WIRED(XYZ各レベル)。「Standardを除外することは認めない。」

> 照合注記(11-8): 原文の「約70語を目安」は承認Trial B_r1(`FZ-TELL-TALE-HEART-CHUNK-FINAL-01_USER.md:6,13`「約70語Chunk分割」)の記述。Production実装は閾値100語超・`k=ceil(語数/100)`(`er117_chunk_tts_production_01.py:26-27`)で、100〜140語のclipが約50〜70語のchunkになる=Trialの『約70語』と整合する(chunkサイズの目安であり別規則ではない)。**本委任のX/Y範囲外**であり、Zの分割規則は一切変更していない(「新しい分割規則・語数閾値変更の禁止」に従う)。Z側委任でFableが承認原文・Trial結果(`FZ-NARRATION-CHUNK-TTS-TRIAL-01/TRIAL_RESULT_01.md`)と実装値を再照合すること。

## 2. 要求項目(原文を分解)
| ID | 原文(逐語) | 実装先 | 検証 | Status(本委任末) |
|---|---|---|---|---|
| R-01 | 「承認済みTrial B0.2／B_r1の規則を維持し、Standardにも正式適用する。」 | X: `er019`の`generate_family_x_a2_segments`(`_generate_x_body_part_chunked_a2`)。Y: `er121_family_y_audio_01.py`の`generate_y_a2_segments`・`CHUNK_TTS_Y_LEVELS=("b1b","a2")`(`er121_family_y_structure_01.py`)。planner規則は`er117.plan_x_part(s)`を無変更で共用(元々レベル条件なし)。Z: `er117.plan_z_clip`の`level!="b1b"`(撤去は次委任) | `er117_std_chunk_wiring_test_01.py`(Adv golden一致=規則不変)、`er019_x_std_chunk_test_01.py`、`er121_family_y_std_chunk_test_01.py` | X Std=IMPLEMENTED_PENDING_EVIDENCE / Y Std=IMPLEMENTED_PENDING_EVIDENCE / Z Std=DESIGN_READY |
| R-02 | 「Standardの既存6%減速とChunk分割・0.2秒ポーズの合成を適切に設計する。」 | `DESIGN_01.md` §2(chunkごとに既存`generate_a2_segment_with_slowdown`→減速後の各chunk wavを0.2秒の無音(減速対象外)で連結) | `er117_std_chunk_wiring_test_01.py::StdSlowdownCompositionPhysics`(実ffmpegで『ポーズ=正確に4800サンプル』および連結後減速が採れない根拠) | 設計=DESIGN_READY、X/Y実装=IMPLEMENTED_PENDING_EVIDENCE |
| R-03 | 「初回Production生成、retry、fallback、regeneration、resumeへ一貫して反映する。」 | chunkは通常segmentと同じ関数・同じ3 attempt・同じfallback。resume=`_generate_or_reuse`(+`drop_cached_std_chunks_without_slowdown`で減速証跡なしcacheを拒否)、再計画禁止=`reconcile_saved_plan(chunk_plan_a2.json)`、版=`drop_stale_chunk_entries` | X/Y各testのresume・replan・失敗継続(R1)・証跡なし再生成 | X/Y=IMPLEMENTED_PENDING_EVIDENCE(Zは設計) |
| R-04 | 「各Family／各レベルの正式runtimeで、分割位置・Chunk数・追加ポーズの発火証拠を取得する。」 | Phase 2(次委任)。`DESIGN_01.md` §7、`BUDGET_PLAN_01.md` | 未実施(本委任はAPI 0) | **未取得(全行)** |
| R-05 | 「必須Validator・音声QA・統合テスト・Regressionを実施する。」 | 共有Gate・Style gate・Y style gate・X追加Gate(`_x_std_chunk_slowdown_blocked`)・Y`check_std_slowdown`(chunk対応) | 遮断下の既存回帰(er117/er019/er121 pattern)前後比較+新規test | 遮断下offline=実施(`FIX_01.md`)。音声QA/統合runtimeは未実施 |
| R-06 | 「Fable独立レビューを経て、CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／Gitを更新する。」 | 本委任はSSOT編集禁止。文案のみ(`DESIGN_01.md` §8、RESULT_PACKET) | — | 文案提示のみ |
| R-07 | 「X/Zで既に確認済みのAdvanced動作を回帰させない。」 | Advの分割計画・0.2秒・chunk数・attach_chunk_meta・evidence形式・親entryをバイト不変に保つ | golden(`golden/adv_plans_golden_01.json`、実装前HEAD bb578265cで凍結)バイト一致test、Adv generate/refresh非汚染test、既存Adv test全PASS | PASS(X/Y Adv。Z Advは`er063`未変更=下記) |
| R-08 | Yの注意事項:「文境界分割や本文契約の変更を追加承認したものではない。…段落構造を持つ入力に対して正式経路が正しく発火することを検証し、実記事が1段落のため不発火ならその事実を記録する。」 | 新規則を追加していない(`plan_x_part`のまま)。Y Std/Advの複数段落入力での発火はtest(合成入力)、実記事の不発火は`chunk_tts_decision.json`に`chunked:false, paragraphs:1`として記録 | `er121_family_y_std_chunk_test_01.py`(実記事相当1段落=不発火、複数段落=発火) | 発火test=PASS(合成入力)、実記事の不発火記録=既存`RUNTIME_EVIDENCE_01`+test。**正式runtime(複数段落dev入力)は未取得** |
| R-09 | 「コード配線済み・テストPASSだけで、実際には確認できていないruntime evidenceを取得済みと扱わないこと。…Gate 3の必須条件が欠ける場合は、未確認事項を明示する。」 | 各表のruntime列を「未取得」と明記 | — | 遵守(RESULT_PACKET 6行表で全runtime列=未取得) |
| R-10 | 再発防止:「Family共通仕様や対象レベルをAI側の判断で狭める場合は、今後必ずユーザー承認を得る。『TrialではAdvancedのみだった』という事実だけで、正式Production採用の対象レベルまで限定しないこと。」 | 下記§3の恒久記録 | — | 記録済み |

## 3. 再発防止条項(恒久記録)
- Family共通仕様・対象レベルを狭める設計判断(例: 「Std対象外」)は、**Trialの実施範囲(Advancedのみ)を理由にしてはならず**、ユーザー明示承認が無い限り採用しない。狭める必要が技術的に生じたら、実装せずに(1)理由 (2)QCD影響 (3)代替(全レベル適用のままの設計案)を添えて Fable へ報告する。
- 本件の経緯(`docs/research/CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01/APPROVAL_TRACE_01.md`): Std除外は `2026-10-25_FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01_DELEGATION_01.md:8` のFable委任文と Sonnet Phase 0設計(`EXISTING_SPEC_CHECK_01.md:116,120`、`WIRING_DESIGN_01.md:117`)に由来し、ユーザー原文には除外の指示が無かった(PM Gate・承認管理の不備)。
- 本委任のコード上の再発防止: Yは`CHUNK_TTS_Y_LEVELS`に両レベルを定義し、`er121_family_y_std_chunk_test_01.py::test_std_is_in_scope...`が`("b1b","a2")`を固定する。Xはレベル別関数(Std/Adv)の双方にchunk経路の存在をsource検査testで固定する(`er117_x_chunk_wiring_test_01.py::test_std_a2_path_has_chunk_route_after_2026_10_26_approval`。旧『Std非chunk固定』testは撤去)。

## 4. 撤去・書換えしたtest(旧『Std除外』を期待値に固定していたもの)
| test | 旧期待値 | 新期待値 |
|---|---|---|
| `er117_x_chunk_wiring_test_01.py::XGenerateTests::test_std_a2_path_untouched_no_chunk_ids`(撤去→`test_std_a2_path_has_chunk_route_after_2026_10_26_approval`) | a2関数のソースに`chunk_tts`が無い | a2生成・gain・読込・組立にchunk経路がある |
| `er117_x_chunk_wiring_test_01.py::XOnlySegmentsTests::test_validate_only_segments_chunk_forms`(該当assertのみ) | `--level a2`で`_k`指定を拒否(I5) | 受理(`in_one_line_k1`等の誤指定は引き続き拒否) |
| `er121_family_y_audio_chunk_test_01.py::TestPlan::test_a2_is_not_chunked_and_chunk_only_segments_rejected`(書換え) | `chunk_tts_applied_at_this_level is False`・a2の`_k`拒否 | `("b1b","a2")`・applied=True・a2の`_k`受理 |
| `er117_z_chunk_wiring_test_01.py:130-132,202`(Z Std固定) | 不変 | **本委任では不変のまま維持**(Z Std配線は次委任。その時に書換え) |
