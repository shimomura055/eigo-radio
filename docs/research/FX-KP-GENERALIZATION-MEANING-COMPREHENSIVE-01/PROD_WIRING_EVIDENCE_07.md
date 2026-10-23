# PROD_WIRING_EVIDENCE_07: 課題②(所有格一般化)+A-1(参照語不定化)のX/Z Production配線 — 実装・test・runtime evidence

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_20 / 2026-10-24 / 承認: 課題②=UDR #173(改善案+付帯(a)〜(f))・A-1=UDR #169(いずれも`APPROVED_FOR_PRODUCTION`) / 設計正本=WIRING_DESIGN_05.md(+WIRING_DESIGN_01.md §1のA-1)。
Status: **WIRED_PENDING_FABLE**(コード・test・runtime evidence揃い。`PRODUCTION_WIRED`の宣言はFable受入後)。実装commit=`4128fffeb`(単一commit、`git revert 4128fffeb`で戻る)。

## 1. 変更(file:行、実装commit 4128fffeb)
| 場所 | 変更 |
|---|---|
| `er105_kp_fulltext_selector_01.py` :750 `reference_pair_ok` / :779 `find_inflection_window` / :797 `is_valid_inflection_normalization` | A-1(this/that→a/an[theは不可]、him/me/us→someone、her→someone[直後語条件])とrole条件付きmy/our→someone's受理を**窓判定1箇所に一本化**。validator(kc経由)と後処理が同じ関数を使う。a/an判定は本番既存のCMU辞書(`pronouncing`=cmudict 1.1.3、er108と同一) |
| 同 :813 `validate_possessor_roles` / :875 `postprocess_possessor_roles` / :852 `_recompute_item_fields` | roles検証(個数・token・enum)→roleと食い違う一般形(one's/someone's/somebody's)を**displayの語へrevertのみ**(書換えなし)。検証不能/窓なし/revert後にvalidator不通過は`UNVERIFIED_ROLES`/`NO_WINDOW`/`REVERT_SKIPPED`でkey無変更。`person_role_repair`を残す。reason/changed/qa再計算(`generalize_reference_word`を消さない、人称QAの無条件PASS上書きはしない) |
| `er003_key_words_canonicalization.py` :122 `REFERENCE_WORD_REASON`、`NORMALIZATION_REASONS_FULLTEXT`、:151 `FULLTEXT_CANON_PASSTHROUGH_FIELDS`、:162 `_role_ok_poss_of`、:528 `_is_valid_fulltext_normalization`、`_qa_field_effective_verdict`、`validate_canonicalization_item`、`validate_canonicalization_response`、:735 `run_canonicalization_gate(postprocess=None)`、`merge_canonicalization_result`(:900) | fulltext専用schemaに`possessor_roles`(rank直後・required)とenum追加。`role_ok_poss`(既定空)を各validatorへ。hook(既定None=従来と同一)。merge時にcanon側の`possessor_roles`/`person_role_repair`をfulltextのみ複写。共有schema・共有enum・共有許可表は不変 |
| `er003_v1_n3_01_scaffold_generate.py` :502-507 | `is_fulltext`のときだけ`postprocess=er105.postprocess_possessor_roles`を渡す。A/B/Cの約10呼出点は無変更(hookを渡さない) |
| `er003_key_words_gloss_alignment.py` :236 `person_generalization_pairs` | G1: him/her/me/us→someone/somebody、G1': role検証済みmy/our→someone's/somebody'sを組として返す(共有表は拡張しない) |
| `er003_v1_translator_briefs/b1_p2_keywords_canonicalization_fulltext_prompt_template.txt` | A-1の規則5(T1〜T7)+課題②のROLE_BLOCK・規則3/4例示の均等化・QA定義(P-T1〜P-T4)+P-T2(「迷う場合は置換せずdisplay_phraseの語のまま」=旧「より自然な側を選ぶ」を置換)。規則5(a)のreason説明に残っていた`a/an/the`は本文の「theは使いません」・validator(theを許可しない)と矛盾していたため`a/an`へ整合(Trial文言からの唯一の意味変更でなく矛盾除去) |

### X/Z共通性(コード上の呼出経路)
- X: `er019_family_x_audio_production_runner_01.py:441 sc.run_key_phrases(..., kp_backend=...)`(`run_theme_scaffold`:385、`--scaffold-only kp`含む)→ `er003_v1_n3_01_scaffold_generate.py:855 run_kp_with_outer_retry` → :908 `run_key_phrase_canonicalization`(:475)→ :502-507 hook。
- Z: `er062_family_z_writer_01.py:1289 run_kp_stage` → `run_kp_with_outer_retry_fulltext`(:1293) → `sc.run_kp_with_outer_retry`(:712)→ :908 → :502-507 hook。`er026` `stage_kp`の初回・再利用・`--regenerate-stage kp_*`・外側retry・resumeはいずれも`ensure_stage`→`run_kp_stage`を通る。
- **canonicalization gateの呼出は`sc.run_key_phrase_canonicalization`の1箇所のみ**(`kc.run_canonicalization_gate(`のscaffold内出現=1、testで固定)。外側retry(最大3)・fallback(旧5件経路へfallbackしない)・fail-closedは無変更。
- A/B/C: `is_fulltext`でない呼出は旧template・旧enum・旧validator・hook無し(template blob sha1 `6e19a905…`、共有schema sha `1daac908…`、`NORMALIZATION_REASONS` sha `fd341920…`、`er064_kp_idiom_trial_01_test_01.py:55-56`のINVALID固定をtestで維持)。

## 2. test
- 新規 `er003_test_kp_possessor_roles_wiring_01.py` 51件PASS: A-1真理値表(肯定11/否定8/固定表現/a-an CMU/her所有格vs目的格/reason gate)、②(self維持・other_person維持・誤one's→revert・誤someone's→revert・non_person its維持/revert・role=none目的格herのsomeone維持・A-1同居・再帰+二重所有・UNVERIFIED_ROLES5種でkey無変更・REVERT_SKIPPED・NO_WINDOW・入力非破壊・冪等・reason保持・人称QA非上書き)、role条件付き受理(my→someone'sはother_person検証済みのみ、self→revert、roles無し→従来どおりINVALID、LLMの`person_role_repair`偽装は上書き、共有表不変)、A/B/C非適用(role_ok_poss不渡し・template/enum不変・hook呼出点がscaffold 1箇所のみ)、gate hook(hook無し=従来/有り=revert+raw_text保持+retry消費なし/例外時は生応答続行)、merge passthrough(fulltextのみ)、template/schema(旧文0・新文あり・ROLE順)、Dangling Reference(Production→er112 import 0、実験flag無し)、Family Yの共通KP path固定。
- 更新: `er003_test_kp_fulltext_wiring_01.py`(schema test=差分許可リスト方式、旧「目的格someoneはINVALID」test→受理2ケースへ書換え)、`er105_..._test_01.py`(isolation testでDEV `er112_`を除外)、`er112_kp_gm_trial_01_test_01.py`・`er112_kp_gm_poss_04_test_01.py`(配線によりDEV installerは**drift guardでfail-closed**する新仕様をassertへ書換え。Production側4関数のhashを配線後へ更新、skipはせず新実態をassert)。
- 全回帰: §5。

## 3. runtime evidence(新規TTS 0・既存記事の自動再生成0・公開物の書換え0。出力は`er112_output/kp_gm_prod_01/`のみ)
共通: STOP確認 rc=0(`stop_check_10.json`/`stop_check_x.json`/`stop_check_z.json`/`stop_check_z2.json`)、`TTS_EXECUTION_MODE=STANDARD`、flag: 新規flagなし・`EIGO_KP_*`未設定(gloss再整合flagは既定ON=従来どおり、`[GLOSS-ALIGN] 実効flag=ON (source=default)`)、**actual model_id=`gpt-6-luna`**(全canonicalization応答の`response.model`一致検査を通過、routing: process `B1_SUPPORT`/`A2_SUPPORT`→`routing.SUPPORT_MODEL`)、template sha256(LF読込)=`a57e8e38026f9710d5c53449fea07eec3e70b3c969c1b1ebda0531e36444076c`(git blob `6f64165de87a62219f9cfc52fd55bb3124f6c5b7`)、schema sha256=`64044994620480a7a3b051e41c6648607fc692d7cd60675727d24ef4f4e86b6d`、developer message sha256=`26d8374cc6f808439e1a55b942a79a4471c83b56bcf87fa852995769128639ef`。費用台帳=`paid_calls.jsonl`+各run `cost_log`。

### 3-1. P-T2確認 + 正式経路の関数evidence(35 unit×1rep、`er112_kp_gm_prod_evidence_01.py pt2`)
DEV patchなしでProductionのcanonicalization部品(fulltext template・fulltext schema・`run_canonicalization_gate(postprocess=)`・`merge`)を呼び、Trial_04の所有格unit(poss_units.json)で実行。結果=`pt2/*.json`(生出力と後処理後のkey・roles・`person_role_repair`併記)。
- canonicalization: PASS 34/35、INVALID 1(`R_63ec43c18c`の`close around`→`close around someone`=語の追加。**Trial_04のC0A/C1Aでも同unitが同じINVALID**=今回起因でない既存事象)。外側retry相当(gate attempts)は全unit 1回(INVALIDの1 unitのみ2回)。
- 所有格item 40(gold付き44slot): **WRONG 0/44**(CORRECT_GENERALIZED 29、KEPT[置換なし・its等] 15)。roles検証OK 40/40(`UNVERIFIED_ROLES` 0、`NO_WINDOW` 0)、role判定 gold一致42/44(不一致2=`pumps its fist`のself→non_person、いずれも置換なし=安全側)。
- 後処理の発火: `NO_CHANGE` 40/40、`REPAIRED` 0(LLMがrole先行判定に従ったため。revert経路は自然発火しなかったので**単体testで担保**し、mockをruntime evidenceと呼ばない)。
- A-1(同unit内): `told her the truth`→`tell someone the truth`(role=none)、`look her in the face`→`look someone in the face`。
- P-T2の1文(迷えば置換しない)の影響: `catch your breath`・`mind your own business`(gold=self)は置換なし(KEPT)。誤りではなく安全側の後退。費用=10.22円(35 call、0.29円/call)。

### 3-2. 正式Production経路(KP段のみ、音声なし)
- **X**: `er019_family_x_audio_production_runner_01.py --slug uk_train_speaker_playback --run run_nws_02 --level both --stage scaffold --scaffold-only kp --out-dir er112_output/kp_gm_prod_01/x_uk_train --tts-backend speech_metadata_flash_lite`(supportはsha照合済みcopy、既存記事dirは不変)。rc=0、費用1.09円。a2/b1b とも `CANONICALIZATION_PASS`(外側retry 1周):
  - `draw that line` → **`draw a line`**(reason `generalize_reference_word`、gloss「一線を引く」ALIGNED)=A-1発火(両level)。
  - `reach for your wallet` → **`reach for one's wallet`**(`possessor_roles=[{your,self}]`、`person_role_repair.status=NO_CHANGE`、gloss「自分の財布に手を伸ばす」)=②発火(両level)。
- **Z**: `er026_family_z_fiction_production_runner_01.py --story melos --slug melos --run run_kpgm20_01|02 --mode real --stage kp --approved-budget-jpy 6`(run_kpq_01のwriter/plan/supportをcopyした新run dir)。rc=0、費用1.19円/1.29円:
  - run_01: `sentenced him to death` → **`sentence someone to death`**(gloss「人に死刑を言い渡す」)、`pulled him under` → **`pull someone under`**(gloss「人を水中に引きずり込む」)=A-1発火(目的格→someone)。
  - run_02: `blocked his way` → **`block someone's way`**(`{his, other_person}`、gloss「人の行く手をふさぐ」)、`kept his eyes on them` → **`keep one's eyes on them`**(`{his, self}`、gloss「彼らから目を離さない」)、`sentenced him to death` → `sentence someone to death`。両runとも `CANONICALIZATION_PASS`・外側retry 1周・gloss ALIGNED。
- 費用合計(本委任のevidence)=13.79円(P-T2 10.22+X 1.09+Z 1.19+1.29。上限25円内、見込み11〜15円内)。

## 4. Family Y実装状況(ユーザー§1-2の1〜5に対する事実)
1. 制作ラインの構築段階: DEV/Trial専用。`er110_family_y_*`(text/persona/audio trial、`*_run.py`)。音声Trialは`y_entry_point.json`に`"production_reachable": False`を記録(`er110_family_y_audio_trial_01.py:155`、`er110_family_y_persona_audio_trial_01.py:123`)。Y専用の正式Production runner・正式入口は存在しない(CURRENT_SPEC.md:1476・:1646「Family Yは将来Voices系…実装は存在しない」、AUW Closeout「Yの開発時に正式配線する」)。
2. KP選定・一般化・意味生成工程: **存在する(Trial scaffold内)**。`er110_family_y_text_trial_01_run.py:264`・`er110_family_y_persona_text_trial_01_run.py:281`が`sc.run_key_phrases(..., kp_backend="fulltext_p2")`を呼ぶ。意味生成(gloss)・Adv説明・KP音声もX部品(`er019_family_x_audio_production_runner_01 as xr`、`xr._generate_key_phrase_segments_b1`)を呼ぶ。
3. 共通実装かY専用か: **共通(X/Zと同一module`er003_v1_n3_01_scaffold_generate`)**。Y専用のKP実装はない。
4. 今回仕様のYへの配線・検証: **コード上は追加配線不要で既に同じ経路に載る**(Y Trial scaffoldの新規runは本commit以降、②+A-1が効く。`TestFamilyYSharedKpPath`で呼出経路を固定)。ただしY側のProduction経路が無いため**`PRODUCTION_WIRED`とは判定しない**(Trial専用経路=11-7相当のTrial扱い)。既存のY Trial成果物(KP生成済みのscaffold)は自動再生成しない。Y Trialでのruntime evidenceは、費用最小化のため追加の有料Y runは行わず、同一共通module・同一関数のX/Z正式経路evidenceで代表させた(Y scaffoldの追加runは別目的のY費用[Y累計上限]を消費するため)。
5. Production化までに必要な作業: **新規OPEN-484に登録**(Y正式Production入口の新設[Writer/Plan/Support/KP/TTS/Assemble/Page]、KP段をX/Zと同一の`sc.run_key_phrase_canonicalization`経由で呼ぶこと、`production_reachable=False`の解消、Y Production化時の必須受入条件=②+A-1のruntime evidence[Y正式初回経路]・retry/fallback/regeneration/resume整合・test・Dangling Reference 0)。

## 5. 付帯条件(a)〜(f)の充足(UDR #173)
| 付帯 | 内容 | 充足 |
|---|---|---|
| (a) | 物が動作主のits | 選択肢A採用(non_personの一般形をrevertし`its`維持)。`run its course`/`pump its fist`/`apply its findings`等がNO_CHANGE(runtime 3-1)、`test_non_person_its_kept_and_generalized_is_reverted`。選択肢B(`non_person_agent`分割)=OPEN-481を維持(未実装) |
| (b) | 受理条件=role条件付き | `my/our→someone's/somebody's`はrole=other_person検証済みのみ(`find_inflection_window(role_ok_poss)`)。共有許可表`_PERSON_DEPENDENT_TO_GENERIC`・A/B/C不変(test) |
| (c) | `qa_person_reference_generalized`定義の整合 | template(P-T4)に「roleに従い一般化しなかった場合もPASS」を追記。後処理は無条件PASS上書きをしない(repair時のみ、test) |
| (d) | 決定論後処理(revertのみ) | API 0・revertのみ・検証不能は無変更・hookはfulltext専用 |
| (e) | 承認済みPrompt変更(規則3例示均等化・「迷う場合は置換しない」) | template配線済み(P-T1〜P-T3、P-T2)。P-T2のDEV確認=§3-1(WRONG 0/44) |
| (f) | 既存完成記事の自動再生成なし | 既存記事dir・公開物は無変更(evidenceは別out-dir)。KP段再実行時のみ反映 |

## 6. 限界・申し送り
- **W-01〜04(A-1に対するOpus条件C必須修正)の本文はrepo内に無く、本委任文にも転記されていなかった**(WIRING_DESIGN_03 §1・05 §1冒頭と同じ)ため、反映済みとは言えない。W-02(窓判定のer105一本化)のみWIRING_DESIGN_05 §1で確認でき反映した。W-01/03/04は未確認=Fableが本文を渡せば追加照合する。
- A-1と②は同じ関数・同じtemplate文を編集するため**同一commit**にした(設計の「別commit」からの変更)。`git revert 4128fffeb`で両方が1手順で戻る。A-1のみ残す個別revertは不可(必要なら別途)。
- 窓特定時のみ、my/ourの全slotを許容して窓を特定し(受理可否はrole照合後)、食い違いをrevertで解消する(`lose someone's job`←`lose my job`[role=self]がINVALIDでなくrevertになる=新しいINVALIDを作らない方向)。受理自体は検証済みroleに限る。
- 全回帰の残failureは§7参照(自分起因0)。

## 7. 全回帰(`.venv\Scripts\python.exe run_project_regression.py`、実装commit 4128fffeb後)
collected=7061 passed=7045 failed=6 errors=0 skipped=10。配線前の基準(OPEN-456 F6: failed 0/errors 0)に対し、失敗6件は**すべて自分起因でない**:
| test | 原因 | 根拠 |
|---|---|---|
| `er019_family_x_fx_20261016_wiring_01_test_01 ...test_fallback_used_consumers_do_not_read_kp_english_entries` | 他agent(Family Y)が追加した`er110_family_y_persona_audio_trial_01.py`が許可リスト外(`fallback_used`読取) | 差分計算で当該1ファイルのみ。自分の変更ファイルに`fallback_used`読取なし |
| `er020_tts_retry_local_rewrite_fullseg_test_01 ...test_recorded_candidates` | 他agentの未追跡`er011_output/local_rewrite_recovery/hormuz__run_0x`等のデータ依存 | KP/canonicalizationと無関係 |
| `er026_family_z_e2e_integration_test_01`の3件(`test_dry_run_all_stages_zero_side_effects`/`test_legacy_dry_run_flag_maps_to_dry_run`/`test_shared_state_files_unchanged_by_mock_run`) | 回帰中に並行runが共有state fileを更新(自分のZ real run含め複数agent稼働)→ 共有state比較が不一致 | 同ファイル単独再実行は42 passed(配線直後)。最終再確認は報告参照 |
| `er064_kp_int_01_test_01 ...ProductionUnchanged.test_no_tracked_py_or_template_modified` | 他agent(ASR-TIME-NUMERAL)の未commit変更(`er021_en_asr_semantic_equivalence_production_01.py`ほか)を検出 | 検出された2ファイルは自分の変更でない。自分の変更はcommit済み |
(`er003_test_bad.FixtureTests`のFAIL表示は意図的な失敗fixtureの出力で、集計の失敗には含まれない。)
