FABLE-DELEGATION-MARKER: KP3V-DESIGN-委任_01-20261022

# 委任(KP-THREE-ASR-MAJORITY-PRODUCTION-01 委任_01: ユーザー正式承認(`APPROVED_FOR_PRODUCTION`)の「Key Phrase英語フレーズ=OpenAI・Azure・Whisperの3-ASR多数決(2/3 PASSで最終PASS、片側NGのときだけWhisper実行)」を、現行の「両方PASS必須」(er096、OPEN-440)の置き換えとしてFamily X/Zへ配線するための**現状調査+実装設計+未配線module/test+Whisper実行環境確認**。Production .py未編集・API 0・JPY0。設計後にOpus条件Aレビュー→配線は次委任)

## 管理ID
KP-THREE-ASR-MAJORITY-PRODUCTION-01 委任_01(新規。置換対象=FAMILY-XZ-ASR-PASS-CONDITION-SPEC-AUDIT-01のKP両方PASS(`er096_kp_dual_pass_01.py`、OPEN-440 CLOSED_PRODUCTION_WIRED、CURRENT_SPEC「KP PASS条件表」)。関連=ASR-THREE-WAY-COMPARISON-TRIAL-01(ローカルWhisper runner)、FAMILY-X-BYUS-KP-ASR-LISTENING-PAGE-01(think up/blurt/take partの保存音声・転写)、PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01(並行設計中、KPは対象外)。並行: `PNAP 委任_01`(er103設計、OPEN新規行)、`HRQFIX 委任_02`(er021系test)、`KPMP 委任_02`(OPEN-448、FOLLOWUPS)が作業中。共有SSOTは`git status`→該当行再Grep→自分の行だけ→即add+commit、`index.lock`は30秒待ち。`er103_*`/`er021*_test*`/`er102_*`は触らない)。

## 性質/到達上限Status/禁止事項
- 性質: Production実装の前段(調査・設計・未配線module+test・環境確認)。到達Status: `APPROVED_FOR_PRODUCTION_DESIGN_PENDING_OPUS`(Production既存ファイル未編集=`PRODUCTION_WIRED`ではない)。
- Opus Gate: **条件A該当(判定フローの変更: 2段AND→3-ASR多数決+ローカルWhisperのProduction依存追加)**。Fableが設計書を対象にOpusレビューを手配する。
- 修正範囲(11-8): 本委任で編集可=新規`er104_*`(未配線module/test/環境確認script)、`docs/research/KP-THREE-ASR-MAJORITY-PRODUCTION-01/`、OPEN_ITEMS新規行、REPORT_LEDGER、delegation_log。**Production既存.py・Prompt・CURRENT_SPEC・DECISION_LOG・Store manifest・HR queueは編集不可**(SSOT本文案はRESULT_PACKETへ)。
- 時間見込み(8-X): 約3〜4時間(調査1.5h/設計1h/module+test 1h/環境確認0.5h、並列可)。
- 費用/日次: JPY0(API呼出なし。Whisperはローカル)。当日既使用 約JPY878。実装後のruntime evidence(Primary/Azure各数呼出+Whisperローカル、見積≤10円)は本委任で見積のみ。
- 禁止: `git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f。secret_scan hits=0。push=`git push origin HEAD:main`。ACTIVE_TASK/RESULT_PACKETはgitignore。SSOT全文読込禁止(Grep)。他agentの未commit差分を混ぜない。承認範囲を広げない(KP英語解説文・その他音声は現行維持。再生成上限・retry/fallback・安全STOPは維持。Whisper失敗/未実行時はPASSにしない=fail-closed)。

## ユーザー原文(2026-10-22、逐語。`docs/pm/delegation_log/2026-10-22_KP-THREE-ASR-MAJORITY-PRODUCTION-01_USER.md`へ本文無改変で保存、文字数・sha256を記録)
---
# Claude Code指示：Key Phrase 3-ASR多数決方式 — Family X/Z Production正式反映

## 1. 目的・正式承認

Key Phrase英語フレーズの発音判定について、**OpenAI・Azure・Whisperの3-ASR多数決方式を正式採用する。**

対象はFamily X/Z共通。既存の「OpenAI・Azure両方PASS必須」を置き換え、Production配線・テスト・runtime evidence・SSOT/Git反映まで完了させる。

- Status：`APPROVED_FOR_PRODUCTION`
- 到達目標：Family X/Z双方で`PRODUCTION_WIRED`
- Key Phrase英語解説文、その他の音声は現行判定ルールを維持する。

## 2. 正式判定仕様

| Primary（OpenAI） | Secondary（Azure） | Whisper | 最終判定 |
|---|---|---|---|
| PASS | PASS | 不要 | PASS |
| PASS | NG | PASS | PASS |
| PASS | NG | NG | NG |
| NG | PASS | PASS | PASS |
| NG | PASS | NG | NG |
| NG | NG | 不要 | NG |

**基本原則：3-ASR中、2つ以上がPASSなら最終PASS。**

処理効率のため、両方PASSならWhisperを呼ばない。両方NGの場合も、Whisperだけでは多数決PASSにならないため呼ばない。

片方だけNGの場合に限りWhisperを実行する。

既存の再生成回数上限、retry/fallback、安全STOP条件は維持する。

## 3. 既存検証の再評価

今回の実測結果：

- `think up`：OpenAI PASS／Azure NG／Whisper PASS → 新方式PASS
- `blurt`：OpenAI NG／Azure PASS／Whisper PASS → 新方式PASS
- `take part`旧問題音声：OpenAI・Azure・WhisperともNG → 新方式NG
- `take part`合格音声：3系統ともPASS → 新方式PASS

これまでの検証で品質改善の合理性は十分示されていると判断している。

**大規模な追加Trialを行わず、既存証拠・保存音声・テストを再利用すること。**

ただし、明確な誤発音の新規誤PASS、または既存品質条件との重大な衝突がないことを確認する。

## 4. Whisper導入・速度・費用

Whisperは既存検証で使用したローカル実行方式を基本とする。

- Whisper API利用料：0円
- 実際のCPU処理時間・実行環境・必要な依存ライブラリを確認
- 正式Production環境で利用できることを確認
- 既存検証で使用したsmall/mediumの結果と費用・速度を踏まえ、必要十分な構成を採用する
- 不要なモデル比較や再検証は行わない
- Whisper実行は片側NGのケースだけに限定
- 不要なTTS再生成の削減効果も評価する

既存Production環境でローカルWhisperが利用できない場合は、品質とQCDを満たす実現方法を検討し、重大な制約がある場合のみ報告する。

## 5. Family X/Z Production配線

両Familyの正式初回Production経路に適用する。

特に以下を確認する。

1. Primary・Secondaryの結果が分かれた場合のみWhisperが発動する。
2. 2/3 PASSで正常終了する。
3. 2/3 NGは従来どおりNGとして処理する。
4. Whisper実行エラーや未利用の場合に、勝手にPASSへ変更しない。
5. retry／fallback／regeneration／resumeに新判定が一貫して適用される。
6. Storeの既存音声再利用時にも新判定が反映される。
7. Key Phrase英語解説文とその他の音声には影響しない。
8. 既存の固有名詞アラーム方式との適用範囲の整合を確認する。
9. 両Familyで正式runtime evidenceを取得する。

従来の両PASS必須ルールが後続経路に残って新方式と矛盾しないことを確認し、不要な旧判定を整理する。

## 6. 受入条件・STOP

- Family X/Zで正式Production経路の判定が期待どおり動作
- 既存の正常音声・問題音声でRegression PASS
- 明確な誤発音を新たに自動PASSさせない
- 追加API費用0円
- 量産速度に重大な悪影響がない
- 必須Validator・integration test PASS
- 実際のmodel ID・Whisper実行環境・判定記録を確認可能
- SSOT・Git反映済み

重大な品質リスク、実行環境上の解決困難な制約、承認範囲・予算上限超過がある場合はSTOPして報告する。

軽微な問題は委任範囲内で自律解決する。

## 7. QCD・Closeout

品質（Q）＞速度（D）＞量産単価（C）。

開発費の日次原則1,000円（JST）を遵守し、既存の検証資産を再利用して最短で完成させる。

Fable独立評価を実施し、以下を簡潔に報告する。

1. Family X/ZのProduction配線Status
2. `think up`・`blurt`・`take part`の新旧判定結果
3. Whisperの正式runtimeでの発火証拠
4. 重大な誤PASSが発生していないことの検証結果
5. 追加コスト・処理時間・再生成削減効果
6. retry／fallback／Store再利用との整合
7. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／Git反映
8. Fable受入判定と残存Open Item

**すべてのGateを満たした場合のみ`PRODUCTION_WIRED`とする。**

既に正式承認された仕様について、重大な問題がない限り、追加のユーザー承認を求めずProduction配線まで進めること。
---

## Fableの事前整理(設計の前提。再照合しズレは報告)
- 現行(置換対象): `er096_kp_dual_pass_01.py`(`KP_EN_PHRASE_DUAL_REQUIRED=True`、`dual_enabled()`、`kp_dual_reuse_ok` 6箇所、Store field `kp_dual_check`、X profile key suffix `+dual1`、`er078_asr_unified_judge_01.py`の`dual_required`モード/`NG_DUAL_PRIMARY_NOT_PASS`/`NG_SECONDARY_UNAVAILABLE`、`er006_secondary_asr_01.py`の`secondary_dual` step/`audit["dual"]`、X: `er019_family_x_audio_production_runner_01.py`/`er019_family_x_kp_en_k2_store_01.py`/`er019_family_x_validation_inheritance_01.py`、Z: `er063_family_z_audio_01.py`、`er003_v1_repro01_main_generate.py`の`dual_pass_required`kwarg、`er006_master_audio_store_01.py`)。設計書=`docs/research/FAMILY-XZ-ASR-PASS-CONDITION-SPEC-AUDIT-01/IMPLEMENTATION_DESIGN_01.md`、証跡=`er096_output/kp_dual_prod_01/`。**新方式はこの構造を拡張する形(最小差分)で、Whisper tie-breakを追加し、最終判定を「2/3 PASS」にする。**
- 判定表(ユーザー§2)を真理値表として固定し、Whisperの呼出条件=「PrimaryとSecondaryの判定が割れた場合のみ」。Whisper失敗/未導入/timeout=`NG_WHISPER_UNAVAILABLE`(PASSにしない、fail-closed)。Secondary障害時(`NG_SECONDARY_UNAVAILABLE`)の扱い=従来どおりPASS不可(Azure不可でPrimary+Whisperの2/3に降格しない。これは現行承認の「Azure障害時にPrimary単独PASSへ降格しない」と整合。設計書に明記、Opusに確認観点として渡す)。
- Whisperの判定: 転写文字列を既存の判定関数(`classify_asr_match`+正規化+同音救済、KP用の経路と同一)に通す。新しい判定基準は作らない。モデル=既存検証と同じfaster-whisper small(int8)を基本(ASR3W・`er099_byus_kp_asr_listen_page_01.py`の実装を再利用。mediumは不要=ユーザー§4「不要なモデル比較はしない」。smallで7件・take partの結果が指示§3と一致していることを再掲)。CPU時間・モデル取得・依存(`faster_whisper`、CTranslate2、モデルキャッシュ場所)・初回ロード時間・1 KP clipあたり処理時間を`er104_whisper_env_check_01.py`で実測(API 0)。Production環境=本リポジトリを実行するこのWindows環境(venv)である前提を確認。
- Store再利用: 既存`kp_dual_check`エントリの再判定ロジックを拡張(保存転写があればWhisperだけ追加実行、無ければ従来どおり)。think up/blurtのStoreエントリ(現行NG)は新方式で再利用時にPASSになる想定→Store fieldを`kp_vote_check`(version付き)へ、profile key suffix `+dual1`→`+vote1`等の扱い(既存A/B/Cへの副作用回避=OF-KPD-Pの既存指摘を踏襲)。
- retry/fallback/regeneration/resume: er096配線時に設計した6箇所の`kp_dual_reuse_ok`と`dual_pass_required`の呼出点を全て新方式へ(残置すると矛盾)。旧`dual_required`モードは残置せず置換(ロールバックは定数で)。既存のretry上限内での再生成削減効果=「片側NGでWhisper PASSなら再生成しない」件数を保存データ(D-2 survey 7件・記事A/B/他のkp_dual_audit)から見積。
- 固有名詞アラーム方式(PNAP、並行設計中)との整合: KPは対象外(アラーム方式はKP以外のsegment)。KPに固有名詞が含まれる場合は3-ASR多数決が適用される(緩和なし)ことを明記。
- 誤PASSの確認(大規模Trialなし): 保存音声で再評価=byUs 7件+take part 2本+D-2 take part型拒否10本+Stage 2の負例(KP相当ではないが短句)のうちKP経路相当のものに、新方式を適用して「明確な誤発音がPASSに変わる件数」を0円で算出(保存転写+Whisper small)。新方式でPASSに変わるのはthink up/blurtのような「2系統が正しく聞く」ケースに限ることを示す。
- runtime evidence計画: X=byUs記事のKP Store再利用で正式runner(KPステージのみ)を1回→think up/blurtでWhisper発火→PASS(Primary/Azure再呼出は最小、見積≤5円)。Z=Family Z KP経路(er063)で同様に最小。見積・翌JST日可否を明記。

## 実行内容
1. 調査(0円)→`INVESTIGATION_01.md`(現行er096配線点一覧[file:行]、判定順序、Store/resume/retryの流れ、X/Zの差)。
2. 設計→`IMPLEMENTATION_DESIGN_01.md`(真理値表・呼出条件・fail-closed・Secondary障害時の扱い・Whisper構成と環境・Store field/profile key・配線点ごとの差分案・旧ルール整理一覧・test計画[unit真理値表/配線test/Regression pattern]・runtime evidence計画と見積・ロールバック定数・処理時間影響・再生成削減見込み・PNAPとの適用範囲)。Opus条件Aに答えられる粒度。
3. 未配線module `er104_kp_three_asr_vote_01.py`(真理値表判定・Whisper tie-break呼出のインターフェース・fail-closed・監査record)+`er104_kp_three_asr_vote_01_test_01.py`(6行の真理値表+失敗系+Secondary unavailable)+`er104_whisper_env_check_01.py`(環境・処理時間実測、結果json)+保存音声での誤PASS再評価script(0円)。Production .py無編集。
4. SSOT: `OPEN_ITEMS.md`新規行「KP-THREE-ASR-MAJORITY-PRODUCTION-01」`APPROVED_FOR_PRODUCTION_DESIGN_PENDING_OPUS`(ユーザー承認2026-10-22・原文所在・置換対象OPEN-440・Production未編集)。`REPORT_LEDGER.md`1行。CURRENT_SPEC(KP PASS条件表の置換案)/DECISION_LOG追記文案はRESULT_PACKETへ。T-0: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_KP-THREE-ASR-MAJORITY-PRODUCTION-01_委任_01.md`(Nは`FABLE-DELEGATION-MARKER: KP3V-DESIGN-委任_01-20261022`を含むAgent tool_useの通番、280前後。先頭行で一致確認)。
5. commit→push→到達確認。`ACTIVE_TASK.md`固定ヘッダ。`RESULT_PACKET_KP3V1.md`。

## 事前指定Read/Grep
- Read: `er096_kp_dual_pass_01.py`(全文)、`docs/research/FAMILY-XZ-ASR-PASS-CONDITION-SPEC-AUDIT-01/IMPLEMENTATION_DESIGN_01.md`、`er099_byus_kp_asr_listen_page_01.py`(Whisper呼出部)、`docs/research/FAMILY-X-BYUS-KP-ASR-LISTENING-PAGE-01/mapping_01.json`、`er096_output/kp_dual_prod_01/{evidence_summary.json,survey_article_b.json}`。
- Grep: `kp_dual_reuse_ok|dual_pass_required|dual_required|kp_dual_check|\+dual1|NG_DUAL_PRIMARY_NOT_PASS|NG_SECONDARY_UNAVAILABLE` in `*.py`(配線点全列挙)、`faster_whisper|WhisperModel` in `er0*.py`、CURRENT_SPEC `KP PASS条件|両方PASS`(節位置)、`docs/pm/OPUS_FINDINGS_LEDGER.md` `OF-KPD-P-`(既存指摘の再利用)。

## Git
- 明示add: `er104_*.py`、`docs/research/KP-THREE-ASR-MAJORITY-PRODUCTION-01/**`、delegation_log 2件、`OPEN_ITEMS.md`、`docs/pm/REPORT_LEDGER.md`。
- commit: `KP3V 委任_01: KP英語フレーズ3-ASR多数決(ユーザー承認APPROVED_FOR_PRODUCTION)のX/Z配線に向けた調査・設計・未配線module+test・Whisper環境実測、Production未編集、¥0`。

## 報告(RESULT_PACKET_KP3V1.md)
配線点一覧/真理値表と失敗系/Whisper環境実測(依存・ロード・1clip処理時間)/保存音声での新旧判定表(think up/blurt/take part×2/take part型10本/他)と誤PASS件数/再生成削減見込み/旧ルール整理一覧/runtime evidence計画・見積/CURRENT_SPEC・DECISION_LOG追記文案/RESULT_PACKET 4行/raw URL(設計書)。