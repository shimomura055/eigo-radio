FABLE-DELEGATION-MARKER: FAMILY-Z-DIALOGUE-SPEED-PRODUCTION-WIRING-01-委任_01-20261023

# 委任_01: Family Z 会話速度仕様(APPROVED_FOR_PRODUCTION)の正式Production配線+既存2作品(4組)の音声更新+受入資料

## T-0
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FAMILY-Z-DIALOGUE-SPEED-PRODUCTION-WIRING-01_委任_01.md`(N≈328〜338、先頭行MARKER一致確認)。
2. ユーザー指示原文(§1)を `docs/pm/delegation_log/2026-10-23_FAMILY-Z-DIALOGUE-SPEED-PRODUCTION-WIRING-01_USER.md` に逐語保存。
3. ACTIVE_TASK.md: 別agent複数が並行中(ASR-HOMOPHONE 委任_05[Z melos `run_aho4_z_h3` のtts_b1bを1回実行し得る]、FAMILY-Z-SOURCE-FIDELITY 01A/01B[01Bは本文Trialで有料生成、音声なし]、FAMILY-Y 委任_03[read-only])。編集直前に再読込し、OPEN-462行を本管理IDの状態へ更新。有料呼出・Production成果物差替えの直前/直後に同行へ「進行中/終了(時刻)」。

## 1. ユーザー指示原文(逐語)
```
# Claude Codeへの指示:Family Z 会話速度改善 — 正式Production Wiring

## 1. ユーザー正式決定

Family Z会話速度A/B Trial(OPEN-462/UDR #159)について、ユーザーが『走れメロス』『開いた窓』のStandard/Advanced全4組を試聴し、**すべてTrial B版の正式採用を決定**しました。

**Status:APPROVED_FOR_PRODUCTION**

Trialの追加や再評価は不要です。正式Productionへの配線から、既存2作品の音声更新、検証、Fable独立受入まで進めてください。

対象は**Family Zのみ**です。

## 2. 正式採用する速度仕様

| 音声区分 | 採用仕様 |
|---|---|
| Standard Narrator | 従来どおり6%減速 |
| Standard Dialogue(登場人物の会話) | **生成後6%減速を撤去** |
| Advanced Narrator | 従来どおり速度変更なし |
| Advanced Dialogue | **生成後に約6%高速化** |

Advancedの高速化はTrial Bで検証済みの、音程を維持する機械処理を使用してください。

以下は変更しません。

- Voice割当
- TTSモデル・Prompt・Style
- 台詞・本文
- 音声の再生順序
- 効果音・BGM
- 承認済みの音声品質基準

## 3. Production Wiring

今回の速度仕様を、Family Zの正式Production経路へ実装してください。

**新規記事の初回制作だけでなく、retry/fallback/regeneration/resume/Store再利用でも同じ速度仕様が適用されることを必須条件とします。**

特に以下を確認してください。

1. StandardのDialogueに旧6%減速処理が残らない。
2. AdvancedのDialogueにTrial Bと同一の高速化処理が適用される。
3. NarratorとDialogueが正しく区別される。
4. 速度処理の二重適用や処理漏れが発生しない。
5. Storeの再利用キー・音声メタデータが新仕様と整合する。
6. 旧仕様の音声が誤って新仕様として再利用されない。
7. TTS再試行上限や既存のASR品質検査を維持する。

旧仕様の不要な分岐・設定・検査があれば、正式経路との整合を確認して適切に整理してください。

実装方法は既存構造を最大限再利用し、不要な新機構を増やさないこと。

## 4. 既存2作品への適用

以下の4組を、承認済みTrial B版の速度へ更新してください。

| 作品 | Standard | Advanced |
|---|---|---|
| 走れメロス | 会話6%減速撤去 | 会話約6%高速化 |
| 開いた窓 | 会話6%減速撤去 | 会話約6%高速化 |

既存のTrial成果物・原音を再利用し、原則としてTTS再生成なしで再組立してください。

『走れメロス』の既存Voice割当は維持します。新しいVoice割当規則に合わせた再生成は不要です。

既存完成音声は、QA合格・公開確認後に安全に差し替えてください。

### 『開いた窓』に関する注意

『開いた窓』では、原作の重要な結末欠落と固有名詞ルールに関する別作業が進行中です。

今回の速度改善では、その本文・台詞を変更しないでください。

ただし、後続の原作忠実性改善で本文・台詞が更新される場合、新速度仕様が確実に適用されるようにしてください。

**速度仕様のProduction Wiring完了と、『開いた窓』作品全体の完成判定を混同しないこと。**

『開いた窓』は引き続き本文品質の問題が未解決であり、作品全体をCLOSEDにしません。

## 5. 検証・受入条件

以下を完了してください。

- Family Z正式初回Production経路への配線確認。
- Standard/Advancedそれぞれの速度処理に関するruntime evidence。
- Trial B版との速度・音声処理の一致確認。
- Voice・本文・台詞・Narrator・BGM等の非対象部分が不変であること。
- retry/fallback/regeneration/resume/Store再利用との整合。
- 速度変更後のASR・音声QA。
- 必須Regression/Validator/Integration test PASS。
- 公開試聴ページの通し再生・個別再生確認。
- Dangling Referenceなし。
- CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS更新。
- Git commit・push完了。
- Fable独立受入。

**正式Production経路での実動作証拠がない場合、PRODUCTION_WIREDとは判定しないでください。**

追加の有料TTS生成を伴う検証は、既存Trial音声や保存音声で代替できないか先に検討してください。

## 6. QCD・作業進行

優先順位:**品質 > 完了速度 > 量産単価**

- Trialは完了済み。追加の速度探索Trialを行わない。
- 既存音声・Trial B成果物を最大限再利用する。
- 2作品・2レベルの独立作業は並列化する。
- 不要な待機・日付分割をしない。
- 新たなTTS費用・ASR費用は必要最小限に抑える。
- 承認済み範囲内の実装不具合は自律的に原因究明・修正・検証する。
- 未承認の仕様変更や重大な品質リスクが必要になった場合のみSTOPして報告する。

## 7. Status・Closeout

今回の正式採用仕様について、Family Zで以下の状態まで到達してください。

**APPROVED_FOR_PRODUCTION → PRODUCTION_WIRED**

Fableは、コード実装だけでなく正式Production実経路、runtime evidence、試験結果、SSOT・Git反映を照合して受入判断すること。

OPEN-462/UDR #159はユーザー判断済みとして更新し、同じ採用判断を再度求めないでください。

既存2作品の公開音声更新状況も個別に記録してください。

## 8. 最終報告

以下を簡潔に報告してください。

1. **Production Wiring結果・Fable受入Status**
2. Standard/Advancedの新速度仕様とruntime evidence
3. 『走れメロス』『開いた窓』各4組の音声更新結果
4. 更新後の試聴URL
5. QA・回帰テスト結果
6. TTS再生成数・実費・量産単価への影響
7. SSOT/Git反映結果・残Open Item

**ユーザーが4組すべてのTrial B版を正式採用したことは確定済みです。**

新たなユーザー判断を不要に増やさず、承認された仕様を必要十分な品質でProduction Wiredまで完成させてください。
```

## 2. 前提(Fable)
- Trial成果: `docs/research/FAMILY-Z-STD-DIALOGUE-SPEED-AB-TRIAL-01/{TRIAL_RESULT_01,TRIAL_RESULT_ADV_01}.md`、`er026_output/family_z_std_dialogue_speed_ab_01/`(Std B: `_original.wav`そのまま/Adv B: `er008_a2_postprocess_slowdown_01.apply_a2_slowdown`をtempo=1.06[slowdown_pct=-5.660377]で再利用、ピッチ保持。組立は`er063.run_assembly`無変更)。元run: melos=`run_e2e_06`、開いた窓=`run_e2e_01`。公開ページ: `user_test/family_z_melos_02/`、`user_test/family_z_open_window_01/`(**今回ユーザー承認により更新対象**。`family_z_melos_jre_01`は証拠ページで対象外)。
- 現行実装: Std 6%減速は`er003_v1_n3_01_tts_generate.py:194-222 apply_a2_slowdown_postprocess`(X/Z共有、`<id>_original.wav`退避→atempo上書き)、対象判定に`A2_SLOWDOWN_TARGET_SEGMENTS`(:115-118)、Audio Validationの未適用ガード`er003_v1_n3_01_assemble.py:273`。Zの後処理呼出は`er063_family_z_audio_01.py`(Grepで特定)。clip kind(narrator/dialogue)は`ClipSpec.kind`。
- **X/A/B/Cの挙動は変えない**(共有moduleを触る場合はZ専用引数/分岐とし、X出力のbyte一致を回帰で示す)。Opus条件Aは、既存後処理段へのkind別分岐+Store/再利用key整合の範囲なら不要(Fable判断)。**処理フロー自体(後処理の位置・Storeの保存形態)を変える必要が出たら、実装前に設計をRESULT_PACKETへ書いて一旦停止**。
- 費用: Fable自律枠(300円以内)。TTS再生成は原則0。ASR再検査は、Production経路の出力がTrial B clipとsha一致なら**Trialの検査結果を流用**し、不一致clipのみ再検査(出典付き)。本日累計 約95円。

## 3. 実装(Family Zのみ)
1. **仕様の実装**: Z TTS後処理で `level×kind` により (a2, narrator)=6%減速維持 / (a2, dialogue)=減速なし / (b1b, narrator)=無処理 / (b1b, dialogue)=tempo 1.06 高速化(Trial Bと同一関数・係数・ピッチ保持)。原音退避(`_original.wav`)と処理記録(`speed_profile`: 例 `z_speed_v2`、係数、適用有無)をclipメタデータ・`tts_generation_results`に残す。二重適用防止(処理済みフラグ/原音からの再適用のみ)。
2. **retry/fallback/regen/resume**: TTS再試行・Local Rewrite・`--only-clips`・resume・`--regenerate-stage`で同一の後処理が通ることを確認(コード経路+test)。
3. **Store/再利用**: Z clipのreuse_key・Master Audio Storeの等価keyに速度仕様version(`speed_profile`)を含める、または保存形態を「原音(後処理前)」に統一して再利用時に後処理を再適用する、のどちらかを既存構造に合う方で選び理由を記録。**旧仕様(減速済みStd dialogue/未処理Adv dialogue)の保存音声が新仕様として再利用されない**ことをtestで固定。
4. **未適用ガードの整合**: `A2_SLOWDOWN_TARGET_SEGMENTS`/assemble:273のガードがZのdialogue除外と矛盾しないよう整理(Zでは「Std narratorのみ減速必須・dialogueは減速禁止・Adv dialogueは高速化必須」を検知できる形に。Xには影響させない)。旧仕様の不要分岐は撤去し残存Grep 0。
5. **テスト**: 単体(level×kind 4通り、二重適用防止、原音からの再適用、reuse key、旧entry非再利用、Narrator/Dialogue区別)、統合(Z runnerのtts段をmock/dry-runで通す)、X出力byte一致回帰、全回帰 `run_project_regression.py` 単独実行 failed 0/errors 0、pytest系別枠。

## 4. 既存2作品の更新(4組)+runtime evidence
1. **直列化**: 他agentのZ有料run(ASR-HOMOPHONE 委任_05の`run_aho4_z_h3`)と重ならないよう、`Get-Process python`とACTIVE_TASKのOPEN-459行を確認。実装は`git worktree`で行い、本線反映はZ runが走っていない時に。
2. **正式経路での再処理**: 各元run(`melos/run_e2e_06`、`the_open_window/run_e2e_01`)のa2/b1bに対し、**Production runnerの正式経路**(例: `--stage tts_a2 --reapply-speed`相当の既存resume/regenerate機構。TTS呼出0で原音から後処理のみ再適用→assemble→gate)を実行し、runtime evidence(適用ログ、`speed_profile`記録、Narrator不変sha、dialogue clipの長さ比、Trial B clipとのsha/長さ一致、gate PASS)を取得。**元runの旧成果物はSTALE退避(削除しない)**。TTS再生成が必要になった場合は理由・clip数・費用を記録(上限30円、超えるならSTOP)。
3. **QA**: 組立後の通し音声の長さ・順序・無音・peak、Narrator/Preview/Comment/KP clipのsha不変、Trial Bとの一致。ASRはsha一致ならTrial結果流用、不一致のみ再検査。
4. **公開更新**: QA合格後、`family_z_melos_02`・`family_z_open_window_01`のStandard/Advanced通しmp3(と個別mp3があれば)を差替え(旧mp3は`_prev_<date>`等でバックアップ、ページ本文の秒数表示があれば更新)。push後にHTTP 200+Playwright実再生(全audio)。
5. 『開いた窓』の本文・台詞は変更しない。作品全体のStatusは`USER_LISTENING_PENDING`+本文品質未解決(OPEN-4xx原作忠実性)のまま。

## 5. SSOT/Git
- CURRENT_SPEC: Family Z速度仕様(Std Full Story 6%減速の記述 :1612/:1627③/:1689 等)を新仕様へ改定(Narrator/Dialogue別、Adv dialogue高速化、旧記述は履歴)。Status=`PRODUCTION_WIRED`は**Fable受入後**。SSOTには`WIRED_PENDING_FABLE`で記載。
- OPEN-462=ユーザー判断済み(4組B採用)→配線Status、UDR #159=判断済み、新OPEN itemは不要(462を継続)。DECISION_LOG(ユーザー決定+配線)。REPORT_LEDGER。OPEN-461(速度調査)はCLOSED(462で解決)へ。
- commitは論理単位(実装+test / 2作品更新evidence / 公開ページ / SSOT)、明示add、secret_scan `--staged` hits=0、`git push origin HEAD:main`。wavはpushしない。共有SSOTは編集直前`git status`→自分の行のみ→即commit。

## 6. 禁止
- X/A/B/Cの挙動変更、Voice割当・Prompt・Style・台詞・順序の変更、追加の速度Trial、承認品質基準の変更、TTS再生成の多用、Trial成果物の直接コピーでProduction成果物を置換すること(Production経路の再処理結果を使う。Trial Bとの一致は検証に使う)、有料runの再起動、HR/STOP迂回。

## 7. 報告(docs/pm/RESULT_PACKET_FZDSW.md、同内容を最終報告で)
(1)Status候補 (2)実装(ファイル:行、level×kind表、Store/再利用key方式、ガード整理、撤去分岐) (3)runtime evidence(作品×レベル、Trial B一致、Narrator不変、gate) (4)4組の更新結果と公開URL+再生検証 (5)テスト・回帰数値・X byte一致 (6)費用(出典)・量産単価影響 (7)commit・raw URL・SSOT (8)残件 + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。