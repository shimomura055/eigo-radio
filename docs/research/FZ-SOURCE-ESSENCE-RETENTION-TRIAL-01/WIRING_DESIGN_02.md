# WIRING_DESIGN_02: 案A Production Wiring 最終設計(Opus条件A必須修正1〜5+推奨の反映後。実装済み)

作成: 2026-10-25 / 委任_04 / 前版=`WIRING_DESIGN_01.md`(設計の骨格・先行検証16/16 byte一致は不変)。案A=APPROVED_FOR_PRODUCTION(ユーザー正式承認2026-10-25、UDR #192/#193)。**Statusは`WIRED_PENDING_FABLE`(PRODUCTION_WIREDはFable受入後)。ユーザー最終試聴PASSは先取りしない。**
Opus条件Aレビュー全文=`OPUS_REVIEW_02.md`(判定=必須修正5・設計見直し不要)。

## 1. 変更箇所表(実装済み。file:行は実装後)
| # | 場所 | 内容 |
|---|---|---|
| W1 | `er062_family_z_writer_01.py` `_REVISE_TAIL`直後 | `_REVISE_THIRD`/`_REVISE_NARR`/`_NARR_LINE`定数を追加(文言はDEV `fz_essence_dev_runner_01.py:26-30`と同一) |
| W2 | `_render_essentials_block` 導入2行の直後 | `L.append(_NARR_LINE.format(voice=ess["narration_voice"].strip()))`。full/std共通 |
| W3 | `build_revise_prompt` の `if essentials is not None:` 内 | `assert _REVISE_THIRD in tmpl; tmpl = tmpl.replace(_REVISE_THIRD, _REVISE_NARR, 1)`(置換条件は既存`essentials is not None`のみ。新flag・新分岐なし) |
| W4 | `Essentials.__init__` 先頭 | `narration_voice`が非空文字列でなければ`FamilyZSeedEssentialsStop`(essentialsを作る唯一の入口で必須化=第3状態に到達しない) |
| W5 | `validate_source_essentials` | `free_to_cut`検査の直後に`narration_voice`必須検査、戻り値dictへ`narration_voice`を追加(**実装後の訂正**: runnerの`e2e_stage_log.jsonl`は戻り値のキー名のみ記録するためstage logに記入文は残らない。追跡はessentials sha・各Prompt dump・`cp_checklist.md`#9。runner無変更の方針は維持)。5件上限には数えない |
| W6 | `build_cp_checklist` | `key_causality`行の直後に`("重大","narration(人称・語り手の立場が各stageで保たれている)", ess["narration_voice"])` |
| W6' | `CP_TREATMENT_RULE`(**Opus必須修正4**) | (A)重大の列挙に`narration(人称・視点・語り手の立場の変更)`を追加。根拠=案A承認(2026-10-25)§1語り口維持・§6 PRODUCTION_WIRED条件。処置は既存の明示`--regenerate-stage`と決定論パッチのみ(新retry・自動判定なし)→承認範囲内の整合作業としてDECISION_LOGに記録 |
| W7 | `run_writer_chain` / `REVISE_USER_TMPL` / runner | **無変更**(runnerのコード変更0) |
| S1 | 5作品のSeed(`er026_seeds/<story>/seed.json`と`er026_output/family_z_production_e2e_01/<story>/seed/seed.json`の両方) | `source_essentials.narration_voice`追記。告げ口心臓のみ`free_to_cut`もdev_seed文へ差替え(Trial検証済み条件)。旧Seedは`seed_STALE_20261025.json`へ退避。`SEED_PROVENANCE.json`のsha更新 |
| D1 | `fz_essence_dev_runner_01.py`(**Opus必須修正5-(a)**) | import直後のfail-fast guard: Production writerが`_NARR_LINE`を持てば`SystemExit("HISTORICAL_RUNNER…")`。docstring/ガードに「歴史的(案A昇格前のTrial専用)」と注記。runner本体・Trial成果物は削除しない |
| D2 | `fz_essence_dev_runner_01_test_01.py` | import時にSystemExitなら`pytest.skip(allow_module_level)`。移植先=`er062_family_z_source_essentials_test_01.py`の`NarrationVoiceWiringTest`(欄なし=例外[W4]、描画位置、REVISE置換、DefaultOffIsolationに相当するMelos byte固定) |

## 2. Seed補完(作品別)
| 作品 | `narration_voice` | 状態 |
|---|---|---|
| 告げ口心臓 | The narrator speaks as 'I' (an unnamed first-person speaker) and keeps addressing the listener as 'you'; his calm, proud, over-confident voice, insisting that he is sane while he relishes his own cunning, is where the horror comes from. + `free_to_cut`をdev_seed文へ差替え | dev_seed全体と一致(Trial Phase 1/1b/1c検証済み) |
| 賢者の贈り物 | The story is told in the third person by an outside narrator, close on Della and Jim, in a warm, gently ironic voice. | dev_seedと一致 |
| 開いた窓 | …close on Framton, in a cool, dry, matter-of-fact voice that plays the events straight. | dev_seedと一致 |
| 猿の手 | …in a quiet, restrained voice; the fear comes from sounds, silence and what the characters say and do. | dev_seedと一致 |
| 二十年後 | The story is told in the third person by an outside narrator, close on Bob, in a plain, matter-of-fact voice. | Trial未検証のSonnet起案。Opus論点b: 受容して記録(Bob中心は既存`conversion_plan`と一致、警官の正体を結末前に伏せる働きと矛盾しない)。次回再生成時の初回CPで確認 |
| 走れメロス | 記入しない(essentials対象外) | 下記§3 |

**告げ口心臓`free_to_cut`差替えの根拠(DECISION_LOG記録対象)**: 現行「the narrator's repeated arguments that he is wise and cunning, …」は、語りの質の源(自己正当化・自己陶酔)を削除可と宣言しており、ユーザー原文§4-3(自己正当化の維持)と矛盾する。dev_seed文「repetitions of the narrator's arguments …」は反復のみを削除可とし、Trialで検証済み(承認範囲内。Opus論点d)。

**推奨(今回は変更せず記録)**: (1) 『賢者の贈り物』`free_to_cut`の"the narrator's jokes and asides"は記入規則(c)と緊張関係にあるが、Trialとのbyte同一性を守るため今回変更せず、**次回この作品を再生成する際に見直す**。(2) R0共通ブロック94行付近の例示(her mother/his father)は三人称の所有格だが、Trialとbyte一致の範囲なので今回変更しない。

## 3. 旧固定文言の残置(Melos専用経路)
`REVISE_USER_TMPL`のベース文言`in third person, `は、essentialsのあるSeed(Melos以外の全Z作品)では必ず`_REVISE_NARR`へ置換される。**残るのはessentials無し=`ESSENTIALS_EXEMPT_STORIES == ("melos",)`の『走れメロス』専用経路のみ**。原作が三人称で、案Aの承認(一人称原作の人称を壊す指示の撤去)と矛盾しない。汎用句へ置換するとMelosのPromptがbyteで変わり完成版不変の前提と衝突する。→ **完了報告・DECISION_LOGに「Melos専用経路に原作どおりの三人称指定を残置」と明記**。推奨1: `ESSENTIALS_EXEMPT_STORIES == ("melos",)`を固定するtestを追加(`test_in_third_person_remains_only_in_revise_base_template`)し、残置がMelos以外へ広がらないことを保証。

## 4. 再生成計画(Opus必須修正1・2・3反映後の最終版)
- 新run `run_sf_prod_02`(旧`run_sf_prod_01`は上書きしない=Seed sha変更でresume不可。S-1)。共通引数: `.venv\Scripts\python.exe er026_family_z_fiction_production_runner_01.py --story the_tell_tale_heart --run run_sf_prod_02 --mode real --approved-budget-jpy 80 --tts-execution-mode STANDARD --stages <段>`(Fable判断: 300円以下の自律範囲で70→80円へ引上げ。概算約40円)。
- **起動構成(必須修正1)**: ①`seed_check,writer,std_adjust` → CP確認(Fable目視用抜粋=COMPARISON_03.md) → ②`plan,support,kp` → ③`tts_b1b,tts_a2,provision_shell,gate,assemble,pages,page_verify`を**1起動**(OPEN-480準拠)。**「tts_b1bとtts_a2の並列2process」は撤回**。直列化の理由は同一run dirの排他lock(`acquire_run_lock`、`er062_family_z_structure_01.py:558-587`)と、5分に3回以上の起動でRESTART_STORM→`STOP`自動作成(607-636、解除は`--clear-stop`のみ=自分では行わない)。各起動の間隔は5分以上、再起動回数を記録。
- **各起動の直前**: `tools/stop_scope_check_01.py --managed-id FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 --run-dir <run> --out <json>`(rc=3なら新規API呼出をせず停止)。TTS直列化(並行agentのTTSと並走しない)。
- **公開差替え(必須修正2)**: `user_test/family_z_tell_tale_heart_01/`のindex/standard/advancedとaudio_standard/audio_advancedを**全てrun_sf_prod_02由来に**。旧ページはscratchpadへ退避。(ii)確認対象に`standard.html`と`audio_standard`を追加(旧StdもR2由来の旧三人称Advから作られているため): sha差分(旧ファイル残存0、全ファイルがrun_sf_prod_02由来)、「housemate」0件(否定条件)に加え、**Std/Adv本文の一人称`I`と聞き手への`you`の箇所をFableが目視で引用確認**(自動判定は作らない)。
- **runtime evidence(必須修正3)**: `{stage}_prompt.txt`は`ensure_stage`で本文を再利用した場合でも書き直される(`run_writer_chain` `wt(...)`)ため、**dumpの存在だけでは送信の証拠にならない**。受入時の手順: (a) run_sf_prod_02のr0/r1/r2/std_adjustの4段全てstatus=generated (b) 各dumpから`sha((dev or "") + "\n\n---\n\n" + user)`を再計算しprovenanceの`prompt_sha256`と一致(r1/r2のdumpはdev・区切りを含まないため`"" + "\n\n---\n\n" + dump`に合わせる) (c) git HEADと`er062_family_z_writer_01.py`のfile shaを`RUNTIME_EVIDENCE_02.md`に記録(Trial専用経路ではない証拠)。PM Gateの「各工程」=R0/R1/R2/Std調整(plan/support/kpは本文Promptを作らない)。新しいログ機構は不要。
- 撤退: 実装(writer+test+Seed+provenance+DEV guard)は**単一commit**=revert単位。公開差替え・成果物は別commit、SSOTも別commit。

## 5. 量産単価
追加LLM呼出0・新Validator 0・新retry 0。Prompt+約90 token/段(Trial実測1208→1300 token)。70円/記事セット目標への影響は無視できる水準。

## 6. 残る未解決・限界
1. S-1(Seed変更で既存run dirのplan/support/kp再実行不可): 受容して記録(M3)。試聴待ちの既存Z作品でKPやsupportをその場で直す必要が出たらSTOP→M4(provenance付替え手順)を別委任で作る、または新runで作り直す。
2. 猿の手の段落数+8は事前基準±4未達のまま(ノイズ可能性、PHASE2_RESULT_01.md)。再利用した「副作用なし」の結論の限界。
3. 二十年後はTrial dumpが無く構造testのみ(Prompt組立の検証)。
