FABLE-DELEGATION-MARKER: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01-委任_05-A1-WIRING-PREP-DECISIONS-OPEN477-20261023

# 委任_05: (a)ユーザー決定のSSOT記録 (b)A-1 Production配線の設計・準備(配線実施はA-3判断後。コード変更はtest/準備のみ) (c)OPEN-477 再発防止のPM_GOVERNANCE・agent定義反映。API 0。

## 背景(ユーザー決定 2026-10-23)
A-1(参照語の不定化: this/that→a/an、him/her/me/us→someone、本文存在/5語/安全条件維持)=APPROVED_FOR_PRODUCTION(X/Z)。配線はA-3追加検証(委任_04が並行)の採否判断後にまとめて実施、準備は先行。A-3 v3=VALIDATED_LIMITED/USER_DECISION_REQUIRED(追加検証中)。OPEN-476=DEFERRED(ユーザー判断による保留、停止理由にしない)。OPEN-477=再発防止承認(正常解決時は報告不要)。原文=`docs/pm/delegation_log/2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_USER_02.md`(委任_04 agentが保存中。未着なら数分待ち、無ければ自分でjsonl最新userメッセージ「# 指示｜Family X/Z Key Phrase品質改善・追加Trial・Open Items整理」を同パスへ保存、衝突時は委任_04側を正)。

## T-0
委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_委任_05.md`(index 365以降、先頭MARKER一致)。ACTIVE_TASK自分の行のみ(並行: 委任_04、ASR PN/UKUS配線設計、FAMILY-Y 委任_08[有料run中の可能性]。**pythonプロセスは自分が起動したPIDのみ終了可、イメージ名一括kill禁止**)。共有SSOTは編集直前`git status`→自分の行のみ→即commit。

## (a) SSOT記録
- UDR #169=判断済み(①A-1採用 ②A-3は追加検証後 ③記事BのKP修正は採用配線後 ④OPEN-476保留)。OPEN-474 Status=`A1_APPROVED_FOR_PRODUCTION(2026-10-23)_WIRING_PREP / A3_ADDITIONAL_VERIFICATION_IN_PROGRESS`。OPEN-476=`DEFERRED(ユーザー判断2026-10-23、停止理由にしない、将来対応時に原形化仕様との整合確認)`。OPEN-477=対策承認済み→(c)完了後 `CLOSED`。DECISION_LOG(ユーザー決定エントリ)、REPORT_LEDGER。

## (b) A-1 配線設計・準備(`docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/WIRING_DESIGN_01.md`)
Trial(`er112_kp_gm_trial_01.py`、DESIGN_02、OPUS_REVIEW_01 OF-KPGM-01〜13)を正式経路へ移す設計:
1. 変更対象(file:line): template `b1_p2_keywords_canonicalization_fulltext_prompt_template.txt`(規則5本文・自問文:7・him/her:11・reason列挙:41、計6箇所)、`er003_key_words_canonicalization.py`(reason enum :113-136 に `generalize_reference_word`、`_PERSON_DEPENDENT_TO_GENERIC` 拡張[him/her/me/us→someone、this/that→a/an/the]、validator `_is_valid_person_generalization` :431-469、3ゲート :502/:512/:571)、`er105_kp_fulltext_selector_01.py:670-709`(`_token_pair_ok`)、`er003_key_words_gloss_alignment.py:167-168,236-243`(`_CONCRETE_PERSON_EN`/pairs のimport時固定への対応)、a/an決定論検査(CMU母音音素)、固定表現例外・置換条件(句末/直後語/不可算)、OPEN-476は触らない。
2. X/Z共通であることの確認(呼出経路)、retry/fallback/regen/resume整合(reason変更でREVIEW_REQUIRED/INVALIDが増えないこと、OUTER_RETRY)、音声側(used_form=TTS入力→Store reuse_key・説明signature `er019_family_x_audio_production_runner_01.py:1077-1081` の再生成挙動、KP3V/CMU gate/5語)、ページ表示。
3. Trial依存0(`er112_*` をProductionからimportしない、DEV注入の撤去)、golden/test更新計画(`er019_family_x_b3_min2_test_01.py` のRULES_SHA256ピン等、er105隔離test許可リスト)、PROMPT_SHA256管理。
4. runtime evidence計画: X=既存記事の `kp` 段のみ再実行(例 記事B uk_train_speaker_playback で `draw that line→draw a line` が正式経路で出ること、費用≤5円)、Z=メロス or 開いた窓のkp段再実行(`him` 型、≤5円)。A-3採用時はAdv説明Prompt変更を同じevidenceで確認。
5. 先行実施してよい準備(コード変更なし): 新規test(規則5の肯定/否定ケース、a/an、固定表現)を**skip状態または未配線で**追加はしない(Production test群を汚さない)→代わりにtest草案を `WIRING_DESIGN_01.md` 付録に。Opus条件Cレビューは配線実施委任の直前にFableが依頼(本委任では論点整理のみ `OPUS_REVIEW_REQUEST_02.md`)。
6. 費用・時間見込み、撤去対象(template:11「him/herは残す」、Trial注入、許可リスト)。

## (c) OPEN-477 再発防止
- `docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/INCIDENT_TASKKILL_01.md` の案に基づき、`docs/pm/PM_GOVERNANCE.md` 26節へ(f)〜(h)(プロセス終了は自分が起動・管理するPIDのみ/イメージ名による一括強制終了[`taskkill /F /IM python.exe` 等]禁止/待機はsleep・pollingで行う)を追加、`.claude/agents/sonnet-worker.md`(および `haiku-worker.md` に該当節があれば)へ同趣旨1〜2行追記。CLAUDE.mdは変更しない。
- 検証: 既存のPM_GOVERNANCE構造test/lint(あれば)PASS、Grepで追記確認。OPEN-477=`CLOSED(2026-10-23 再発防止反映)`、DECISION_LOG。

## Git
明示add、secret_scan hits=0、`git push origin HEAD:main`。論理単位でcommit(SSOT決定/設計doc/OPEN-477反映)。

## 禁止
A-1の配線実施(Production .py/template変更)、OPEN-476の修正、委任_04のファイル編集、有料run。

## 報告(docs/pm/RESULT_PACKET_KPGM5.md)
(1)SSOT記録 (2)配線設計要点(変更対象表・evidence計画・費用) (3)OPEN-477反映と検証 (4)commit・raw URL + RESULT_PACKET 4行 + 「判定整合: 重大NG=なし」。