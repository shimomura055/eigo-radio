# FIX_01 (KP-GLOSS-ALIGNMENT-PRODUCTION-01 委任_01、Opus所見OF-225〜235の是正)

管理ID: KP-GLOSS-ALIGNMENT-PRODUCTION-01。対象: `er003_key_words_gloss_alignment.py`(OPEN-356)。承認済みPrompt(選定/canonicalization)・Rule7・Gate・A'は無変更。Production採用(`APPROVED_FOR_PRODUCTION`)・`PRODUCTION_WIRED`は未宣言。

## 所見→修正対応表

| OF | Fable採否 | 修正内容(実装) | 検証(test/evidence) |
|---|---|---|---|
| OF-225/226 | 記録のみ | 分類=新仕様のProduction採用。Q1(再整合段の採否、課題指示文全文込み)を`RESULT_PACKET_KGA.md`に提示文案として記載 | - |
| OF-227/228 | 採用 | fallback既定を(ii)へ変更。2回retry失敗時は**最終KPを維持**、itemに`gloss_alignment_status="FAILED"`/`gloss_alignment.status=GLOSS_ALIGNMENT_FAILED_KP_KEPT`/`gloss_review_hint=True`、`merged["gloss_alignment_failed"]`、戻り値`gloss_alignment_fallback`(m2_fallbackと同形: article/stage/reason_code/reason/fallback_result/note)。`run_key_phrases`戻り値に`gloss_alignment_fallback_events`(list、m2_fallback_eventsと同じ位置づけ)、run dirに`GLOSS_ALIGNMENT_FAILED_NOTICE.md`、標準出力に`[GLOSS-ALIGN][NOTICE]`。人間確認Queueへは送らない。例外(i): config定数`GLOSS_ALIGNMENT_FALLBACK_MODE="REVERT_TO_CANDIDATE_IF_SAFE"`のときのみ、`revert_to_candidate_allowed`(display_phraseが末尾機能語[`_DANGLING_TAIL_WORDS`]で終わらない/source_span内の連続部分文字列/`validate_canonicalization_item`(Rule7)再判定OK)を満たすitemだけKPを候補へ戻す。戻す場合は`normalization_reason="none"`・`reasoning`差替え・`qa`各値を`INVALIDATED_BY_GLOSS_REVERT`・`canonicalization_source_span`削除・`gloss_review_hint=True`維持。条件を満たさないitemは(ii)。**既定は(ii)、Q2判断後にconfig 1行で確定** | test: `test_fallback_default_keeps_kp_and_marks_failed` / `..._revert_mode_reverts_when_safe_and_invalidates_qa` / `..._blocked_by_dangling_tail_and_span` / 統合`test_failed_alignment_keeps_kp_flags_failed_not_human_review` / `NoticeFiles` |
| OF-229 | 採用 | 規則抽出を堅牢化: 『日本語グロス』で始まる3段落以上+選定Promptテンプレート17行『短く自然な日本語グロスを付けてください』を含む段落(ちょうど1つ)を抽出。欠落時は`GlossRulesExtractionError`。`preflight()`で抽出を1回だけ行いキャッシュ、`run_key_phrases`の冒頭で呼ぶ(最初の記事のAPI呼出前に例外=記事内容に依存しない即時停止)。抽出結果sha256(`447e07cb...9949b`)をtestで固定、`gloss_alignment_runtime_metadata.json`の`rules_sha256`へ記録。固定文の複製なし(単一正本) | `RulesExtraction` 5件 |
| OF-230 | 採用 | 決定論チェック: KP側にスロット語(`SLOT_TOKENS`=someone/somebody/something/one's/someone's/somebody's/oneself)が無いのにglossに「～」「〜」「~」が残れば`validate_alignment_response`でFAIL(retry→最終的にfallback)。LLM自己申告`qa_reflects_all_key_phrase_words`に依存しない。GLOSS_ALREADY_CONSISTENT申告でも最終glossに同じチェックが走るため、旧glossがスロット付きで残るケースもFAIL | `test_slot_tilde_allowed_only_when_kp_has_slot_word` / `test_already_consistent_with_stale_slot_gloss_is_rejected` |
| OF-231 | 採用 | 有効性検証。`VALIDATION_01.md`。注意: 指示の『Parity 10記事の`keywords_canonicalized.json`(A'/M2下)』という記録corpusは存在しない(§VALIDATION_01 1節)。代替=記録済みcanonicalization応答を案A'窓で再判定した153 attempt/765 itemの集計+全er*_output 226 record/1,129 itemのJPY0集計。『based on interviews』行のBefore値誤記(再整合後の値がBefore欄に入っていた)を訂正(`before=～をもとにした`) | `census_01.json` `aprime_targets_01.json` `replay_high_01.json` |
| OF-232 | 採用 | 費用再見積り(実測)と`reasoning effort high→medium`比較(切替はしない)。`VALIDATION_01.md`・`cost_01.json` | `replay_medium_01.json` |
| OF-233 | 採用 | alignment呼出ごとの`usage`と`cost_jpy`(`er009 pricing.cost_jpy_for_call`)を`attempts`へ記録し`gloss_alignment_runtime_metadata.json`へ保存。`run_key_phrase_canonicalization`でalignment呼出を`er005_cost_logger.logging_context(article_id, "kp_gloss_alignment")`で包み、`cl.install()`済みのrunでは`raw_usage_log.jsonl`にstage付きで記録(未installなら無影響の加算のみ)。canonicalization側の同種欠落は本管理IDでは触らず新規OPEN-358で記録 | `test_usage_cost_recorded_in_attempts` |
| OF-234(a) | 採用 | Family Z音声test `er063_family_z_audio_01_test_01`+`..._n01_test_01` 59件PASS(他の有料プロセスなしを確認後。mock/既存wav範囲) | `regression/er063.log` |
| OF-234(b) | 採用(記録のみ) | 『KPがdisplayより短い/人称一般化でglossが過剰』頻度: 全1,129 itemで**内容語の欠落0件**、人称代名詞の一般化(my/their/your→one's等)・助動詞beの脱落のみ22 item(1.9%)。頻度が低いため対象条件への追加はしない(`census_01.json`の`kp_shorter_than_display_items`) | `VALIDATION_01.md` 4節 |
| OF-234(c) | 採用(記録のみ) | 『close around me』のmeはcanonicalizationの一般化品質(人称一般化の漏れ)の問題 → 新規OPEN-357へ記録のみ。本段では`私の周りを取り囲む`のようにmeを反映して整合させた | OPEN-357 |
| OF-235 | 採用 | 明示flag `GLOSS_ALIGNMENT_ENABLED`(既定ON、環境変数`EIGO_KP_GLOSS_ALIGNMENT=0`でOFF、`align_glosses(enabled=...)`で上書き)。OFF時は`status=DISABLED`・API無し・mergedを無変更で返し、`preflight`も何もしない。撤回なし、`PRODUCTION_WIRED`未宣言。運用: **ユーザー判断(Q1)までは新規量産runでこの段を通さない=run起動側で`EIGO_KP_GLOSS_ALIGNMENT=0`を指定する**(OPEN-356に明記) | `test_flag_off_no_api_no_change` / `test_default_flag_on_and_default_mode_keep` |

## 追加観察(Fableへ)
- 課題指示文の「スロット語がある場合に限り『～』を許可」と、承認済みgloss規則の「辞書的な表記として自然な範囲であれば『～』を使ってもよい」は文面上緊張関係にある。決定論チェックは前者(課題指示文)側に倒している。Q1で課題指示文の承認を求める際に併記する。
- 決定論チェックの副作用(過剰FAIL)の可能性: 全er*_output 1,129 item中、KPにスロット語が無いのにglossに『～』がある item が29件(多くは`point to`『～を示す』等の正当な辞書表記)。ただし再整合の**対象itemのみ**に適用されるため量産への影響は対象率(約1〜7%)の範囲。実測した対象8件×2回では誤FAIL0。
- 対象外itemの『～』残存(上記29件)は本段の対象外(拡張されていないKPのため)。必要なら別管理で扱う提案材料(本委任では実装しない)。
