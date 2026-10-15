# FAMILY-C-JA-TTS-PRODUCTION-FIX-01 委任_02 実装説明 (2026-10-16)

到達Status: `FIX_IMPLEMENTED_EVIDENCE_PENDING_FABLE`相当(ただし有料evidence未実施・条件付きSTOP(b)該当。`PRODUCTION_WIRED`は宣言しない)。

## 差分(`er013_family_c_production_runner_01.py`のみ。Voice・Validator・閾値・Prompt・er078_reuse_value_guard_01は無変更)
1. `tts_call_for_voice(..., language="en")`: `language`引数追加(既定"en"=既存呼出と引数同一)。narratorは`generate_narration_snippet_verified_strict(text, language, ...)`へ伝達、費用記録も実言語。**非narrator voiceでen以外はRuntimeError、`budget.check_before`より前**(R9)。
2. `run_simple_narrator_asset`: 受け取った`language`を`tts_call_for_voice`へ伝達(japanese_title/preview_jaがJA、topic_intro_enがEN)。`run_comments_stage_a2`: `language="ja"`。
3. 新規`reuse_provenance_check`(読取のみ): 由来証拠は(a)src側の**正規**`.ok.meta.json`(`upgraded_from_legacy_ok`でない・text sha256一致・wav sha256==src実測)、または(b)meta無し/legacyの場合のみ`audit/tts_generation_results.json`の**`reused`が偽**のentry(sha256(canonical_text)一致かつ記録sha256==src実測)。legacy-upgraded metaと`reused`真のauditは由来証拠にしない(R1)。
4. 新規`adopt_from_reuse_source`: 照合を通った場合のみ、dstの`wav/.ok/.ok.meta.json`を**先に全削除**してsrc wavをコピーし、`{tts_text_sha256, wav_sha256(実測), reuse_from_source, provenance_basis}`(+元`asr_judgement`)を本関数が書く(R2。`_copy_with_ok`は経由しない)。通らなければNone→新規TTS。3つの呼出点(Story / simple asset / Comment)を置換。`_copy_with_ok`は固定共有asset(TTSなし)用に残置。
5. 新規`clear_ok_markers`を`tts_call_for_voice`の実TTS呼出直前に実行(R3)。
6. Comment: `--only-segments comment_N`/`comment_N_ja`指定時はreuse_fromから旧wavを復活させない。
   注意(R7): `forced_comment_regen`が真なら原稿(`comments_ja.md`)がLLMで**3本とも**再生成されるため、`--only-segments comment_1`でも3本とも新規TTSになる(既存挙動、変更なし)。
7. ローカルresume(reuse_fromなし)のmeta欠如legacy分岐は後方互換のため**維持**(`er013_family_c_production_test_01.py`の既存test)。OPEN候補として記録。

## R1〜R11対応表
| R | 対応 | 場所 |
|---|---|---|
| R1 | legacy-upgraded meta・`reused`真audit不採用、由来照合 | runner `reuse_provenance_check`、test `ProvenanceCheckTests` |
| R2 | 既存dst全削除→コピー→meta自書 | runner `adopt_from_reuse_source`、test `AdoptCopyTests` |
| R3 | 新規TTS前に`.ok`/meta削除 | runner `clear_ok_markers`、test `test_failed_tts_leaves_no_ok_marker` |
| R4 | reuse plan dry-run | `evidence_02/reuse_plan_dryrun.json`(結果は`EVIDENCE_02.md`) |
| R5 | INVESTIGATION 5-4の誤記訂正(追記) | `INVESTIGATION_01.md`末尾「訂正」 |
| R6 | 記号Gate事前検査(違反0件) | `evidence_02/symbol_gate_check.json` |
| R7 | Run Bの注記(上記6)。Run B自体は未実施 | 本書 |
| R8 | 禁止語を新規コードに書かない | test `test_forbidden_words_not_in_runner_source`、静的監査PASS |
| R9 | 非enガード/language伝達 | test `TtsCallTests`/`SimpleAssetLanguageTests` |
| R10 | Family C Status不変、06 L370はDangling注記対象 | SSOT追記 |
| R11 | runner内部予算見積はclip 1回分(`TTS_CALL_EST_JPY=0.9`)のみ、実際は最大3 attempt→harness meterが実費上限(hard_stop JPY11)。metaに言語・voice・model無し→OPEN候補(実装せず) | 本書、OPEN |

## 既定値・Production到達性
新規flagなし。`language`既定"en"、新ルールは常時有効(不具合是正でありflag隔離の対象ではない)。
