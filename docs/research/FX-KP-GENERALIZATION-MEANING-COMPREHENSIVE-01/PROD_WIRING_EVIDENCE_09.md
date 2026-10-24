# PROD_WIRING_EVIDENCE_09 (委任_27, 2026-10-24): A-1 Opus条件C必須修正 W-03/W-02 の是正、replay、全回帰の整備 (API 0・費用0)

## 1. 是正内容(`er105_kp_fulltext_selector_01.py`。受理範囲を狭めるのみ。配線(4128fffeb)・template・schema・enumは不変)
### W-03(置換しない条件のvalidator決定論却下)
- `reference_pair_ok(..., prev_d=None)`: 窓の直前のdisplay語(`find_inflection_window`が`d[start-1]`を渡す)を使えるようにした。
- (a) 直前語除外 `_DEM_PREV_BLOCK`={not, all, quite, just, only, like, at, with, than, that, so} と否定縮約形(`*n't`): `not that bad`/`isn't that bad`/`all that`/`just that step`/`at that step`/`with that idea`/`like that line`/`quite that step` を却下。
- (b) 直後語除外: 時間名詞 `_TIME_NOUNS`(year/week/weekend/month/evening/afternoon/season/decade/century/minute/hour/morning/moment/time 等)と `_DEM_NEXT_BLOCK2`={same, other, very, exact, whole, only, first, last, next, previous}: `this year`/`this week`/`this weekend`/`that month`/`this morning`/`that same X`/`that other X`/`that very X` を却下。
- (c) 不可算判定を後方へ拡張: that/this 以降の窓内いずれかの語が `_UNCOUNTABLE` なら却下(`take that good advice`/`take that good information`)。
- (d) me系固定表現 `_REF_OBJ_PREV_BLOCK`={between, excuse, beats, beat, trust, lucky, poor, pardon, bless, dear, believe, and, or, than, like, as, except, but, me, us}: him/me/us/her(目的格)の直前語がこれなら却下(`between you and me`/`excuse me`/`beats me`/`trust me`/`lucky me`)。
- 肯定ケース(`draw that line`/`float that idea`/`take that step`/`make that call`/`pulled him under`/`told her the truth`/`close around me`/`gave him a hand`)は維持。
- template(`b1_p2_..._fulltext_prompt_template.txt` 規則5「置換しない」列挙)との整合(1行): templateはnot that bad/that advice/that said/at that point/in that case/this time/like that/between you and me/all that等を「置換しない」と指示済みで、validatorは同列挙を決定論で却下し、さらにtemplate未列挙の時間名詞・same/other/very・me系固定表現・不可算後方語も却下する(validatorがtemplateより狭い=安全側。template文字列は不変でPROMPT hash・pinへ影響なし)。

### W-02(CMU辞書の扱い。Opus案に合わせた)
- `_first_phone_classes`新設: 辞書に無い語・辞書例外は空集合(判定不能)。簡易綴り規則へのフォールバックを撤去(旧: hour/honest/uni/use等の綴り規則)。
- `starts_with_vowel_sound`=全発音が母音始まりのときのみTrue、新設`starts_with_consonant_sound`=全発音が子音始まりのときのみTrue(保守的)。`reference_pair_ok`は a には consonant 確定、an には vowel 確定を要求(判定不能・複数発音の混在は不許可=無変更。例外は送出しない)。
- 注: `starts_with_vowel_sound`置き場は引き続きer105(Opus W-02の置き場所指摘どおり。kc・er108は変更なし)。

## 2. test(`er003_test_kp_possessor_roles_wiring_01.py` に `TestA1ValidatorTighteningW03W02` 6件追加、合計57件OK)
否定24ケース(+reason 3種の`_is_valid_fulltext_normalization`も否定)/正例8維持/窓外直前語/辞書に無い語/辞書例外/複数発音混在。`.venv\Scripts\python.exe -W error -m unittest er003_test_kp_possessor_roles_wiring_01` = Ran 57 OK。

## 3. replay(API 0): 是正前(git HEAD)と是正後のvalidatorを同一入力へ適用
入力: `er112_output/kp_gm_prod_01/pt2/*.json`(P-T2 35 unit。key_raw_llm/key_final)+ 同dir配下の全`keywords_canonicalized.json`(X uk_train a2/b1b、Z melos run_kpgm20_01/02、outer_retry含む)。ユニーク(display,key)でkey≠displayの55組。
| 項目 | 是正前 | 是正後 |
|---|---|---|
| validator受理(valid) | 50/55 | 50/55 |
| 変化した組 | - | **0**(意図した狭め以外の変化も0) |
受理維持のA-1系: pulled him under→pull someone under / sentenced him to death→sentence someone to death / look her in the face→look someone in the face / draw that line→draw a line / told her the truth→tell someone the truth / gave him a hand→give someone a hand / close around me→close around someone。(他の3組[lose her job→lose one's job等]は所有格系で不変。)
再現: replayスクリプトは一時領域(commit対象外)。HEAD版は`git show HEAD:er105_kp_fulltext_selector_01.py`。

## 4. 全回帰の整備(他agent起因の恒常失敗の最小修正。別commit不要・同commit内でも各対象を明記)
| # | 失敗 | 原因(対象管理ID) | 修正 |
|---|---|---|---|
| 1 | `er109_xz_isolation_01_test_01` StaticIsolation 2件 (`test_importers_of_scope_module_are_a_fixed_production_list` / `test_m3_scope_entry_call_sites_are_fixed_and_literal`) | `docs/research/ASR-TIME-NUMERAL-EQUIVALENCE-01/{er109_probe_01.py,runtime_evidence_02.py}`(研究script、ASR-TIME-NUMERAL-EQUIVALENCE-01)がscope入口をimport/呼出 | 当該2検査のみ`docs/research/`配下を対象外(`is_research_script`)。Production側importer/呼出点の固定list検査は不変 |
| 1b | `er109_asr_orthographic_equivalence_01_test.test_only_scope_module_and_research_tools_import_the_pure_module` | `er012_b_open479_xz_segment_id_test_01.py`(OPEN-479のtest。rollback flag確認で純関数をimport)が検出された(委任文の2件とは別。同根の他agent起因) | `_test`を含むファイル(test)を除外。Production .pyの直接import禁止は不変 |
| 2 | `er110_family_y_text_trial_01_test_01.test_no_production_reference` | `er019_family_x_fx_20261016_wiring_01_test_01.py:702`と`er003_test_kp_possessor_roles_wiring_01.py`(Y隔離確認のtestがer110名を文字列で保持) | testファイルを検査対象外(他3つのer110 isolation testと同じ除外) |
| 2b | `er110_family_y_persona_audio_trial_01_test_01.test_no_production_reference` | `er110_family_y_opinion_based_01.py`(Y DEV runner、FAMILY-Y-VOICES-DESIGN-01 委任_18)がpersona moduleを参照 | `er110_`接頭ファイルを対象外(audio trial testと同じ) |
| 2c | `er110_family_y_persona_text_trial_01_test_01.test_no_production_reference` | 同上(opinion_based_01.pyがpersona_text_trialをimport) | `er110_`接頭を対象外 |
| 3 | `er019_family_x_fx_20261016_wiring_01_test_01.test_fallback_used_consumers_do_not_read_kp_english_entries` | 実際の未許可readerは`er019_nws2_eval_01.py`ではなく`er110_family_y_persona_audio_trial_01.py`(Y DEV。`y_style_gate`がY本文4segmentの`fallback_used`を読むのみ、KP英語Store entryは読まず、書込みはY出力dirのgate結果のみ)。nws2_evalは既に許可リストにあり | 許可リストへ`er110_family_y_persona_audio_trial_01.py`を追加(read-only確認済み) |
| 4 | `er020_tts_retry_local_rewrite_fullseg_test_01.test_recorded_candidates` | `er011_output/local_rewrite_recovery/it2/b1b/`・`it3/{a2,b1b}/`(untracked。内容=school_phone_ban=Family Y 委任_09B/Trial。共有Local Rewrite recovery機構が既定出力先`er011_output/`へ書く既存挙動)をX/Z corpus testが全件globして拾った | 3 fileを無加工のまま`er110_output/family_y_persona_trial_01/local_rewrite_recovery_moved_from_er011/`へ退避(README付き)。参照先は過去docの歴史的path表記のみで更新しない(READMEに明記)。**再発リスク**: Y Trial再実行で共有機構が再びer011_outputへ書く(Y側で出力先を変える別対応が必要) |
| 5 | er026 3件 | 一時状態(単独42 OK) | 対応なし。今回の全回帰では再現せず(失敗に含まれない) |

## 5. 回帰結果(`.venv\Scripts\python.exe run_project_regression.py`、2026-10-24、本是正適用後)
- 既定pattern `er0*_test_*.py`: 327 files / collected 7071 / passed 7060 / failed 1 / errors 0 / skipped 10。before(委任_24時点)の恒常失敗は er109 StaticIsolation 2・er110 1・er019 1・er020 1(+er026 3一時)。
- 残る失敗の内訳: (1) `er003_test_bad.FixtureTests.test_case_0`: runner自身のtestがtempに作る意図的失敗fixture(subprocess出力の再掲であり失敗件数には数えない。summaryのfailed=1は下記(2)の1件)。(2) `er064_kp_int_01_test_01.ProductionUnchanged.test_no_tracked_py_or_template_modified`: 「git上tracked .py/templateが未commitで変更されている」検査。実行時点の未commit変更10件のうち本委任の分は9件(commit後に解消)、`er110_family_y_opinion_based_02.py`/`..._test_01.py`は他agent(Family Y)の作業中変更で帰属は別。commit後の再確認結果は`RESULT_PACKET_KPGM27.md`に記載。
- 追加pattern `er1*_test_*.py`(Opus W-04(3)、er105/er108/er112/er109等): 32 files / collected 477 / passed 477 / failed 0。
