# FICTION-FAMILY-Z-PRODUCTION-E2E-01 REPORT (Phase 1: text工程=TTS直前まで)

管理ID: `FICTION-FAMILY-Z-PRODUCTION-E2E-01`(Phase 1)
Status起点: `APPROVED_FOR_PRODUCTION`(CURRENT_SPEC.md「Family Z(Fiction)」節、
Z-1〜Z-4いずれもユーザー確定済み) / **WIRING INCOMPLETE**(TTS以降未実装)。
本ReportはPhase 1(text工程)の実装・実行結果のみを扱う。**TTS/audio
validation/runtime audio evidence/listening artifactは本委任の対象外
(未実行)**。`PRODUCTION_WIRED`判定はFableが別途行う。

---

## 1. 現在の状態

- Family Z専用Production entry point(新規runner)を新設し、実際に
  Melos("The Three-Day Promise")のtext工程(canonical text確定→
  Preview/Comment/In One Line生成→Key Phrase選定)を**実際にLLM呼び出し
  込みで完走**させた(dry-runではなく実運用、runtime evidence取得済み)。
- Key Phrase canonicalization結果は`overall_status: "REVIEW_REQUIRED"`
  (5件中1件、既存運用どおり自動不採用・人間確認待ち。詳細§4)。
- TTS/assemble stageは明示的スタブ(`NotImplementedError`)。呼び出し経路
  自体はCLI(`--stage tts/assemble`)から到達可能だが未実装であることを
  unit testで固定済み(§8)。

## 2. 実装内容(ファイル・関数)

新規ファイル(2件、いずれもGlobで空き番号er026を確認済み):
- `er026_family_z_fiction_production_runner_01.py`(本体、約480行)
- `er026_family_z_fiction_production_runner_01_test.py`(unit test、19件)

主な関数:
- `check_rights_gate()`/`RightsGateError`: Z-1権利Gate、fail-closed。
- `resolve_canonical_text()`/`check_word_count()`/`check_character_name_rule()`/
  `restore_character_names()`: canonical text受入判定+最小修正。
- `build_segment_plan()`: Family C `plan_story_segments()`/
  `build_flat_voice_chunks()`/`classify_quote_voice_window()`をread-only
  importで再利用(Z-2)。
- `generate_family_z_preview()`/`generate_family_z_comment_1()`/
  `generate_family_z_in_one_line()`: 実LLM生成(Z-2/Z-3)。
- `build_story_type_metadata()`: item5のstory_type分岐。
- `run_text_stage()`/`run_keyphrase_stage()`/`stage_tts()`/`stage_assemble()`:
  CLIから呼ばれるstage関数。

Import専用(read-only、一切編集なし): `er013_family_c_production_01.py`
(Z-2)、`er020_tts_retry_local_rewrite_01.py`(§7マッピング用)、
`er003_v1_n3_01_scaffold_generate.py`(Key Phrase、内部で
`er003_key_words_production.py`/`er003_key_words_canonicalization.py`を
未変更のまま呼ぶ)、`er018_fiction_external_seed_selection_criteria_trial_02.py`
(pricing/cost計算・`get_client()`のヘルパ再利用)。

## 3. rights block(逐語証跡)

`er026_family_z_fiction_production_runner_01.py`内`MELOS_RIGHTS_BLOCK`へ
`FICTION-FAMILY-Z-RIGHTS-RECHECK-01_REPORT.md`§6のユーザー決定原文、
および同REPORT§1/recon§1のURAA分析結果を逐語転記(推測で埋めていない)。
必須フィールド(author/author_death_date/jp_public_domain_basis/
source_url/confirmed_date/us_copyright_status_record_only/
legal_use_basis)を`check_rights_gate()`でfail-closed判定する
(unit test: 陽性1件+陰性2件、全PASS)。米国PD状況は記録事項のみ
(必須条件にしない、ユーザー決定どおり)。

## 4. canonical text確定の根拠

- Trialテキスト(`er018_output/.../stories/03_japanese_lit_2/story.md`、
  385語)は受入条件(語数280〜420語、A2レベル、構造)を満たしたが、
  **CURRENT_SPEC.md「Family Z(Fiction)」節 項目2(人物名変更をしない)
  に違反**していた(原作の"Selinuntius"[友人]・"Dionysius"[統治者]の
  名前が失われ、"his friend"/"the ruler"という役割語だけに置換されて
  いた。unit test`test_trial_text_fails_name_rule_before_edit`で再現
  確認済み)。
- 対応: 既存SSOTルール(項目2)への機械的適合のみを目的とした**決定的
  (deterministic)テキスト置換**で、両名の初出箇所へ同格で名前を復元
  (「the ruler was afraid of enemies」→「the ruler, Dionysius, was
  afraid of enemies」、「Melos's friend stepped forward」→
  「Melos's friend, Selinuntius, stepped forward」)。**LLMではなく
  決定的処理を選んだ理由**: 委任文は「(LLM、¥)」を想定していたが、
  これは創作的な書き直しではなく既存ルールへの機械的適合であり、
  決定的処理の方が(a)$0、(b)diffがそのまま監査証跡になる、
  (c)LLM再生成に伴う語数変動・トーン変化・A2レベル逸脱のリスクが
  ない、という利点があるため。委任文の想定と異なる手段を採った点を
  ここに明記する(内容自体は既存ルールへの適合のみで新しい仕様変更は
  含まない)。
- 編集後: 383語(受入条件内)、人物名ルールPASS、sha256を
  `article_config.json`に記録(`trial_sha256`/`final_sha256`)。
- 採用ファイル: `er026_output/family_z_production_e2e_01/melos/run_01/article.md`

## 5. Preview・Comment・In One Line・Key Phraseの成果物・model_id・費用

実行パス: `er026_output/family_z_production_e2e_01/melos/run_01/`

| 要素 | ファイル | model_id | 備考 |
|---|---|---|---|
| Preview(JA) | `preview.txt` | gpt-5.6-luna | Family C Comment Contractの禁止語句リストを流用した新規prompt(Family Cにはpreview生成関数自体が無いため) |
| Comment 1(JA) | `comment_1.json` | gpt-5.6-luna | `fam_c.generate_family_c_a2_comment()`をそのまま再利用、quality check PASS |
| In One Line(EN) | `in_one_line.txt` | gpt-5.6-luna | **バグ修正あり**(§9参照) |
| Key Phrase選定+canonicalization+redundancy QA | `key_phrases/keywords_canonicalized.json` | gpt-5.6-sol(選定/canon)+gpt-5.6-luna(redundancy) | `overall_status: REVIEW_REQUIRED`(1/5件、後述) |

費用(実測、`cost.json`/`key_phrases/cost.json`):
- text stage(Preview+Comment 1+In One Line、計3 LLM call): 実測$0.002898
  ≈ **¥0.46**
- keyphrase stage(選定+canonicalization+redundancy QA、計3 LLM call):
  実測$0.161364 ≈ **¥25.82**
- **合計 実測約¥26.28**(Guardrail ¥200上限、¥150到達なし。recon概算
  ¥40〜135/記事より低い実測値)。

Key Phrase最終5件(rank/used_form/qa_overall_status):
1. in someone's place — PASS
2. execution — PASS
3. give one's word — **REVIEW_REQUIRED**(`qa_traceable_contiguous_span`
   のみFAIL、理由: source_spanの人称代名詞"my"を辞書形"one's"へ一般化
   したため文字列として連続一致しない。既存Production運用どおり
   「自動不採用・人間確認後に採用可」の扱いであり、新しい問題ではない)
4. fair trial — PASS
5. loyalty — PASS

`overall_status: REVIEW_REQUIRED`は既存Key Phrase QA運用の想定内動作
(rank3のみ人間確認待ち)であり、選定(`KEY_WORDS_STRUCTURE_PASS`)・
redundancy QA(`REDUNDANCY_PASS`、重複ペアなし)自体は正常完了している。

## 6. segment_id規約表(Connected Speech, §7)

`segment_plan.json`に固定。Melos本文は8 segmentに分割される
(`plan_story_segments()`の音声境界原則どおり)。

| position | raw_segment_id | voice | word_count | proposed_segment_id | resolved_role | connected_speech |
|---|---|---|---|---|---|---|
| 1 | story_001 | narrator | 61 | full_story_part1 | FULL_STORY | true |
| 2 | story_002 | dionysius | 4 | full_story_part2 | FULL_STORY | true |
| 3 | story_003 | narrator | 33 | full_story_part3 | FULL_STORY | true |
| 4 | story_004 | dionysius | 5 | story_004(unresolved) | None | false |
| 5 | story_005 | narrator | 5 | story_005(unresolved) | None | false |
| 6 | story_006 | selinuntius | 7 | story_006(unresolved) | None | false |
| 7 | story_007 | narrator | 133 | story_007(unresolved) | None | false |
| 8 | story_008 | narrator | 135 | story_008(unresolved) | None | false |

固定segment: `topic_intro`/`preview`/`comment_1`/`in_one_line`は
resolverの完全一致文字列とそのまま整合(全件`connected_speech_enabled=true`)。

**既知のgap(新しい判断ではなく`er020_tts_retry_local_rewrite_01.
resolve_narrative_role()`の既存の完全一致判定をread-only参照した結果の
事実)**: (a) resolverは`full_story_part1/2/3`の3スロットしか認識せず、
本Storyは8 segmentあるためposition 4以降はConnected Speech適用外。
(b) position 1-3の機械的・位置基準の割当は、position 2が実際には
narratorではなくdialogue voice(4語の短い引用)であるという**voice不整合**
を含む(`mapping_caveat_voice_mismatch`フィールドに記録)。resolver側へ
Family Z用パターンを追加する(recon §8-2選択肢b)か、segment_id命名を
作り直す(選択肢a)かは本委任のスコープ外であり、**Fable/ユーザー判断が
必要**(§12)。

Z-4 Dialogue Voice適用計画(plan only、TTS未実行): narrator=Aoede、
Selinuntius=Erinome、Dionysius=Charon(CURRENT_SPEC.md Z-4追記の参照先
をそのまま採用)。`classify_quote_voice_window()`のkeyword window判定は、
文末の"Free him," he said.のような遠方参照(直前90文字以内に人物名/
"ruler"が無い)を検出できず`narrator`にfallbackする既知の限界がある
(runtime evidenceで実際に確認、TTS段階での人手確認が必要)。

## 7. unit test結果

`er026_family_z_fiction_production_runner_01_test.py`: **19件、全PASS**
(¥0、API呼び出しなし)。カバー範囲: rights gate陽性/陰性3件、canonical
text受入/人物名ルール復元3件、segment mapping(reconstruction一致・
position1-3のFULL_STORY・position4以降None・known_gap記録)5件、
fixed segment role map 1件、story_type metadata 3件、dry-run副作用ゼロ
2件、TTS/assembleスタブ2件。

**全体regression**: 並走Agent(読み解決Phase2/Family X Stage3c)のTTS実行
と並行のため本委任では未実施(次Phaseで実施、本委任文の記載どおり)。

## 8. 待ち工程(TTS以降)と接続点

`stage_tts()`/`stage_assemble()`は明示的に`NotImplementedError`
(unit testで固定)。読み解決Phase2の共有TTS入口commit後、以下を
既承認仕様のまま呼び出す予定:
- TTS: CURRENT_SPEC.md「Family Z(Fiction)」節項目6(attempt1→即時
  attempt2→10分cool-down→attempt3→NGならLocal Rewrite+Natural
  English QA)。
- Voice: `voice_tts_names_plan`(§6)を実際のvoice割当として確定
  (現在はplanのみ)。
- Connected Speech: §6のsegment_id_role_mapをそのまま入力に使うが、
  §6の既知gapの解消方針が先に必要。
- Assembly以降: Family C既存の共有nav asset(`welcome.wav`等)・
  Assembly/Audio Validation Gate/player/web_delivery経路の再利用可否は
  未検証(本委任のスコープ外)。

## 9. 実装中に見つけた不具合と修正(実行証跡込み)

初回実行で`in_one_line.txt`が**日本語で生成される**バグを検出した
(`a2gen.run_support_text()`の`SUPPORT_DEVELOPER_MESSAGE`が
「日本語のListening Support原稿を作成してください。」に固定されており、
プロンプト内の英語指示を無視していたため)。修正として、In One Line
専用の英語developer messageを使うraw client呼び出しへ差し替え、
ASCII優占率>0.9でない場合は再試行するチェックを追加した。修正後、
実際に英語で生成されることを確認済み(§5の`in_one_line.txt`参照、
"Melos kept his promise, and his loyalty saved his friend...")。

## 10. Gate 3 checklist(現時点の充足/未充足)

| 項目 | 状態 |
|---|---|
| Production正式初回経路 | text工程のみ充足。TTS以降は未実装 |
| retry/fallback/regenerationとの整合 | text工程内は既存関数(Family C Comment Contract retry等)をそのまま再利用。TTS側は未着手 |
| DEV/Trial-onlyではないこと | text工程は実LLM呼び出し・実Production module経由(Trial scriptではない) |
| Production runtimeでの実発火 | text/keyphrase stageは実発火済み(runtime evidence: `cost.json`/`raw_usage_log.jsonl`)。TTS未発火 |
| 必要testのPASS | unit test19件PASS。全体regressionは未実施(§7) |
| runtime evidence | あり(§5成果物パス) |
| 実際のmodel_id・routing確認 | gpt-5.6-luna(Preview/Comment/In One Line)、gpt-5.6-sol+luna(Key Phrase)を実測確認 |
| コスト影響評価 | 実測¥26.28(§5)、Guardrail ¥200未達 |
| SSOT反映(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS) | **未実施**(本委任は記載案のみ、§11参照。実反映はFable判断) |
| approved specとProduction挙動の一致 | text工程は一致(項目2名前ルール等)。§6の既知gapは要判断 |

**結論: `PRODUCTION_WIRED`未達(TTS以降未実装のため)。** 判定自体は
Fableが行う。

## 11. SSOT記載案(実施はFable判断、本委任では未反映)

- `CURRENT_SPEC.md`「Family Z(Fiction)」節冒頭Status行(現在「Phase 0の
  みか完了・USER_DECISION_REQUIRED」表記のまま、RESULT_PACKET_FZS指摘
  どおり): 「Phase 1(text工程)完了、TTS以降未実装、`PRODUCTION_WIRED`
  未達」への更新案。
- `OPEN_ITEMS.md` OPEN-185: 「Production配線」の内訳を「text工程完了
  (本REPORT)/TTS工程未着手」に細分化する更新案。
- `DECISION_LOG.md`: 本REPORTへの参照エントリ追加案(§9の
  In One Line言語バグ修正、§6の既知gapをrecordとして残す)。

## 12. Family A/B/C未変更の確認(git diff対象一覧)

本委任で新規作成・変更したファイルは以下のみ(`git status --porcelain`で
確認済み、`git add -A`は使用していない):
- `er026_family_z_fiction_production_runner_01.py`(新規)
- `er026_family_z_fiction_production_runner_01_test.py`(新規)
- `er026_output/family_z_production_e2e_01/`配下(新規、全てtext/JSON、
  wavなし)
- 本REPORT.md(新規)

`er012_b_*`/`er013_family_c_*`/`er003_key_words_production.py`/
`er003_key_words_canonicalization.py`/`er003_v1_n3_01_scaffold_generate.py`/
`er020_tts_retry_local_rewrite_01.py`/`er018_fiction_external_seed_selection_criteria_trial_02.py`
はいずれもimportのみ(read-only参照)で、`git status`上も変更なし
(0バイト差分)。並走Agent対象ファイル(`er003_audio_tts_asr_safety.py`/
`er003_v1_n3_01_tts_generate.py`/`er006_pronunciation_*`/`er019_*`/
`docs/pm/PM_GOVERNANCE.md`/`docs/pm/PM_BRIEF.md`)は一切開いていない。

## 13. STOP該当

なし(実装作業自体はGuardrail内で完走、危険な自己判断や上限到達はなし)。

## 14. ユーザー判断が本当に必要な事項

1. **Connected Speech segment_id規約の統一方法**(§6既知gap):
   (a) resolver(`er020`)へFamily Z用パターンを追加する、(b) Family Z
   側のsegment_id命名を作り直す、(c) 当面Connected Speechの適用範囲を
   position1-3(voice不整合を許容)のまま進める、のいずれを取るか。
2. **Key Phrase rank3("give one's word")の`REVIEW_REQUIRED`**: 既存運用
   どおり人間確認後に採用するか、選定からやり直すか。
3. **Preview生成prompt(§5、新規)**: Family Cに前例が無いため本委任で
   新規に設計したが、正式なProduction prompt文言としてこのまま採用して
   良いか(内容自体は既存Comment Contractの禁止語句・方針を流用した
   もので、新しいコンテンツポリシーの追加ではない)。
4. **SSOT記載案(§11)の反映可否**。

---

## 費用(合計)

実測 ¥26.28(text stage ¥0.46 + keyphrase stage ¥25.82)。Guardrail
¥200上限、¥150警告到達なし。
