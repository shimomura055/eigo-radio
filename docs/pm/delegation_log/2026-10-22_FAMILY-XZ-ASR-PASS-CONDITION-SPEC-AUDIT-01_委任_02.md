FABLE-DELEGATION-MARKER: KPDUAL-PROD-D1-委任_02-20261022

# 委任(FAMILY-XZ-ASR-PASS-CONDITION-SPEC-AUDIT-01 委任_02 [D-1]: Key Phrase英語フレーズ「Primary・Secondary両方PASS必須」のFamily X/Z Production実装設計書+承認記録+未配線test準備。**Production既存ファイルの編集は行わない**=Opus独立レビュー(11-3条件A/C)後のD-2で、進行中の多語同音救済配線(A-2)完了後に実施。API 0・JPY0)

## 0. 運用ルール・並列注意(重要)
- 他agent稼働中: (A-2)多語同音救済配線=`er006_preprod_hardening_01_validation.py`・`er006_secondary_asr_01.py`・`er094_*`・PNMH docs・`CURRENT_SPEC.md`(1839注記+新節)を編集中。(C-1)B3丸め設計=`er090_*`/`er095_*`/B3 docs。(B-2)発音取得計画=`docs/research/PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02/`。**あなたはProduction .py(`er003_*`/`er006_*`/`er063_*`/`er078_*`/`er012_*`/`er019_*`等)を一切編集しない。** 成果物は `docs/research/FAMILY-XZ-ASR-PASS-CONDITION-SPEC-AUDIT-01/` と新規testファイル(`er096_kp_dual_pass_01_test_01.py`等、Production import可・未配線)のみ。共有ファイル(`OPEN_ITEMS.md`/`DECISION_LOG.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/`docs/pm/REPORT_LEDGER.md`)編集前に `git status` → 該当行を再Grep → 自分の行だけ編集 → 即 `git add <file>` + commit。`index.lock`は30秒待って再試行。`CURRENT_SPEC.md`は本委任では編集しない(D-2で)。
- `git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f 禁止。secret_scan `--staged` hits=0。push=`git push origin HEAD:main`。一時ファイルはforce-add禁止。SSOT全文読込禁止。他人の未commit差分を混ぜない。コード行番号は `git show HEAD:` 基準(作業treeにA-2の未commit差分がありうる)。

## 1. ユーザー原文(2026-10-22、逐語。`docs/pm/delegation_log/2026-10-22_FAMILY-XZ-ASR-PASS-CONDITION-SPEC-AUDIT-01_KP-DUAL-PASS-APPROVAL_USER.md` へ本文無改変で保存、文字数・sha256[本文のみ]を記録)
---
# Claude Code指示：ASR PASS条件の正式採用・Family X/Z Production配線

## 1. ユーザー正式決定

以下のASR判定仕様を**Family X/Z共通仕様として正式採用**する。

Status：`APPROVED_FOR_PRODUCTION`

| 対象 | 正式PASS条件 |
|---|---|
| ① Key Phraseの英語フレーズ | **Primary（OpenAI）とSecondary（Azure）の両方PASSが必須** |
| ② Key Phraseの英語解説文 | 現行維持。Primary PASSで合格、Secondary不要 |
| ③ その他すべての音声 | 現行維持。Primary PASSで合格、Secondary不要 |

②③についても、Primary NG時のSecondary判定、承認済み例外、retry／fallback等の既存仕様を維持する。

①は、Primary単独PASSやSecondary単独PASSでは最終合格としない。同音・表記揺れの救済を行う場合も、両Providerそれぞれが承認済み判定基準を満たすこと。

**対象Family：X/Z両方。片方だけの実装完了をもってCloseしない。**

## 2. 実装方針

既存調査 `FAMILY-XZ-ASR-PASS-CONDITION-SPEC-AUDIT-01` を起点とし、既存の共通ASR判定関数および `force_secondary` 等を最大限再利用する。

- Key Phraseの英語フレーズに限り、PrimaryがPASSしてもAzure判定を実行する。
- 両方PASSした場合のみ、そのtakeを採用可能とする。
- どちらかがNGの場合は既存の次slot／再生成処理へ進める。
- 最大試行回数、Human Review Lock、安全STOP条件は承認済み仕様を維持する。
- Azure障害・タイムアウト時にPrimary単独PASSへ自動降格させない。
- Key Phraseの英語解説文、その他の音声には新たなAzure必須条件を適用しない。
- 既存のA2本文minimal fallback等の例外を壊さない。

適用対象の識別は、音声role・正式実行経路に基づいて確実に行うこと。誤って対象を広げたり狭めたりしない。

## 3. 既存実装との整合

並行して進んでいる**多語同音救済**とASR共通判定関数が重なるため、変更競合・仕様矛盾・二重検証を避ける。

可能な範囲でRegressionとruntime evidence取得を統合し、全体のDeliveryと費用を最小化する。

なお、多語同音救済については既存のユーザー承認内容・作業範囲を守り、本指示を理由に仕様を変更しない。

既存のASR重み2.0、Provider routing、数値・否定語の厳格判定、発音救済等も維持する。

## 4. 必須検証

少なくとも次のケースを検証する。

1. Key Phrase：Primary PASS／Secondary PASS → 合格
2. Key Phrase：Primary PASS／Secondary NG → 不合格、次slotへ
3. Key Phrase：Primary NG／Secondary PASS → 不合格、次slotへ
4. Key Phrase：Primary NG／Secondary NG → 不合格、次slotへ
5. Key Phrase：Azure障害・タイムアウト → Primary単独合格にしない
6. Key Phraseの英語解説文：Primary PASS → Azure不要
7. その他の音声：Primary PASS → Azure不要
8. その他の音声：Primary NG → 既存Secondary判定が機能
9. 既存例外、retry／fallback／regeneration／resume、Store再利用時の既存品質保証との整合

**Family X/Zそれぞれで、正式Production初回経路からの実行を確認すること。**

DEV／Trial経路でのPASSやunit testだけでは完了としない。

runtime evidenceには、音声role、両Providerの実際の判定、呼出有無、採否結果、使用model_id／routing、retry／fallbackの動作を残す。

過去の「take part」のように、PrimaryがPASSしてもSecondaryがNGとなるケースが確実に拒否されることを確認する。

## 5. QCD・自律実行

品質（Q）＞速度（D）＞量産単価（C）≫開発費用を厳守する。

- 品質基準を引き下げず、既存機構の再利用と必要最小限の変更で実装する。
- 独立作業は並列化し、不要な日付分割・待機をしない。
- 既存データや保存済み音声を再利用し、API実走は必要十分な範囲に抑える。
- 実測で追加Azure費用、retry・Human Review増分、記事セットあたりの原価影響を評価する。
- 既存承認範囲・日次開発費1,000円（JST）を遵守する。
- 承認範囲内の不具合は原因究明→修正→検証まで自律的に進める。

新仕様の追加、品質基準変更、重要なQCDトレードオフ、予算超過、解決不能なblockerが生じた場合のみSTOPして報告する。

## 6. SSOT・完了条件

- CURRENT_SPECにFamily X/Z共通の新PASS条件を正式記載する。
- 旧文言「同音救済はSecondary側も一致したときのみPASS」と現行仕様との関係を整理し、矛盾を解消する。
- DECISION_LOG／OPEN_ITEMS／PM管理記録を更新する。
- Productionの後続経路に未承認仕様やTrial専用実装へのDangling Referenceがないことを確認する。
- 必須unit／Regression／Validator／integration testをPASSする。
- 必要なcommit・pushを完了する。

**Family XとFamily Zの双方について、正式Production経路で実際に発火した証拠が確認できた場合にのみ `PRODUCTION_WIRED` と判定する。**

## 7. 最終報告

報告は以下に絞る。

1. Family X/ZそれぞれのProduction配線・runtime evidence・最終Status
2. Key Phrase／英語解説文／その他のPASS条件が仕様どおり動いた証拠
3. Primary PASS・Secondary NG時にKey Phraseが確実に拒否された結果
4. retry／fallback／Store再利用への影響
5. 回帰テスト結果
6. 量産追加原価・処理時間・Human Reviewへの影響
7. SSOT・Git反映状況と残存Open Item

**ユーザーは正式採用を承認済み。仕様どおりの実装・検証について追加承認を求めず、Family X/Z両方の `PRODUCTION_WIRED` まで自律的に完了させること。**
---

## 2. 前提(既存調査、再照合すること)
- `docs/research/FAMILY-XZ-ASR-PASS-CONDITION-SPEC-AUDIT-01/SPEC_IMPL_MATRIX_01.md`(OPEN-440): KP英語phrase=X `er003_v1_repro01_main_generate.py` `generate_key_phrase_component_verified`(L779付近、4回構成 Minimal 2+English Lock 2)、Z `er063_family_z_audio_01.py:817-836`。Production本番の`force_secondary`呼出は`er003_v1_crosslevel_audio_02_common.py:381`(A2 minimal fallback)のみ。統一judge `er078_asr_unified_judge_01.py`(Primary PASS→即PASS L421-441、`force_secondary`の意味=primary.passed AND secondary.accepted、`NG_SECONDARY_UNAVAILABLE`=PASS不可、circuit breaker、最終ANDゲート)。`SecondaryCache`(同一wav重複呼出0)。
- 承認済み仕様: CURRENT_SPEC:2818-2819(統一ASR判定仕様、本決定で①のみ上書き)、2827(KP 4回構成・最終slotのみHR)、2820/2828(U2 force_secondaryの範囲=minimal fallbackのみ→本決定で①を追加)、1839(同音救済のSecondary同意要件。A-2がFable照合注記を追記中: 非KPは2818で上書き、Secondary参照時の受理条件として有効)。
- Trial資産(再利用、Production未接続): `er088_kp_asr_dual_pass_trial_01.py`(KPにforce_secondaryを適用したTrial、VALIDATED n=1)、`er091_asr_three_way_trial_01_*`(C1d=両方PASS必須)、`docs/research/ASR-THREE-WAY-COMPARISON-TRIAL-01/`(take part: 現行C1は10件中3件見逃し、C1dK/C5K)、KP4是正(`er092_kp4_remediation_01.py`、旧`kp4_en.invalid_20261021.wav`=Primary PASS/Azure NGの実音声=検証ケース3「take part型拒否」の既存音声)。
- 多語同音救済(A-2、進行中): `protected_check`への配線+steps additive証跡。両Providerとも同じ`classify_asr_match`を通るため、①の両方PASSでもSecondary側で同じ救済が働く(Opus OF-PNMH-P-08)。本設計はそれを前提にし、A-2の変更点と衝突しない配線点(KP生成関数の呼出引数とjudgeの判定モード)に限定する。

## 3. 設計書 `docs/research/FAMILY-XZ-ASR-PASS-CONDITION-SPEC-AUDIT-01/IMPLEMENTATION_DESIGN_01.md`(Opusレビュー用、簡潔)に含めること
(a) **判定モード**: 既存`force_secondary`(=Primary PASSでもSecondaryを呼び、両方で成立したときのみPASS)の現行意味を`git show HEAD:er078_asr_unified_judge_01.py`で正確に確認し、①の要件「Primary NG/Secondary PASSも不合格(PASS_WITH_WARNING不可)」「Azure障害・タイムアウト・空転写・circuit breaker時はPASS不可(次slot。技術STOPの既存扱いを確認)」「同音救済も両Providerそれぞれが基準を満たす」を満たすか検証。満たさない点があれば、新モード(例: `dual_required=True`、minimal fallbackの既存`force_secondary`挙動は不変)の最小追加案を示す(A2 minimal fallbackの既存挙動=U2を変えない)。
(b) **配線点**: X `generate_key_phrase_component_verified`(Minimal 2+English Lock 2の全slotでdual_required。4回上限・最終slotのみHRは不変)、Z `er063:817-836`のKP英語phrase生成。**KP英語解説(`KP_EXPLANATION_MAX_ATTEMPTS=3`)と`phrase_repeat`等は対象外**であることをrole識別で保証(呼出関数単位で識別し、正規表現や文字列判定に頼らない)。K2 Master Audio Store再利用時(ASR 0回)の扱い: Store entryの採用時判定が旧仕様(Primary単独)のもの→**再利用可否をどうするか**を設計(案: Storeの`asr_judgement`に`dual_required`が無いentryは再利用時にSecondaryのみ追加実行して両方成立を確認[Azure費用のみ]、または再生成。費用・Delivery比較を出しFable判断材料に)。resume/regeneration/retryでの一貫性。
(c) **Secondary転写の判定基準**: Secondary側は既存の受理判定(`_secondary_accept`: classify_asr_match→_step_alternate_pass、値・否定ガード独立適用)。Phrase List重み2.0不変。
(d) **費用**: KP英語phrase 1本あたりのAzure追加(音声秒切上×$1/h、JPY160/USD)×記事あたりKP本数(X: 5 KP×Std/Adv?、Z: 実数を確認)×再試行期待値。OPEN-433の見込み(約JPY0.6〜0.9/記事セット)を再計算し出典付きで。
(e) **検証計画**: ユーザー§4の9ケースを(i)unit(judge層・差込み)、(ii)API 0の保存転写差込みでX/Z各KP関数、(iii)実API runtime evidence(X・Z各1 KP以上の正式初回経路、両Provider判定・呼出有無・model_id・routing記録)、(iv)「take part型拒否」=旧`kp4_en.invalid_20261021.wav`をProduction judgeに通しPrimary PASS/Secondary NG→不採用を確認(Azure再呼出1本、またはcache)、(v)Azure障害注入(モック)でPASS不可、(vi)②③がAzure不要のまま(既存回帰test+telemetryでSecondary呼出0を確認)、(vii)minimal fallbackの既存挙動不変、(viii)A-2と統合したRegression(既存回帰test群)。費用見積(出典付き、目安JPY20〜40)。
(f) **A-2との統合計画**: A-2完了commit後にD-2を開始(同一ファイルの競合回避)。Regression/runtime evidenceは共通化(KPの実音声は多語同音の証跡キーも同時に確認)。
(g) **rollback**: module定数(例: `KP_EN_PHRASE_DUAL_REQUIRED=True`)。
(h) **SSOT案**: CURRENT_SPEC新表(①②③)、2818/2820/2827/2831(U2)への追記、1839整理(A-2注記との整合)、Dangling Reference確認(Trial er088/er091への参照がProductionに無いこと)。

## 4. 先行作業(API 0)
- 承認記録: `DECISION_LOG.md`に`APPROVED_FOR_PRODUCTION`エントリ(原文§1逐語)、`docs/pm/USER_DECISION_REGISTER_01.md`のOPEN-440関連行(KP両方PASS)を判断済みへ、`OPEN_ITEMS.md` OPEN-440→`APPROVED_FOR_PRODUCTION_WIRING_IN_PROGRESS`。
- 未配線test `er096_kp_dual_pass_01_test_01.py`: judge層でユーザー§4の1〜5・7・8を差込みで表現(現行コードに対しては「現行挙動」を記録、D-2後に期待値へ切替える設計。Production .pyは編集しない)。
- T-0保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_FAMILY-XZ-ASR-PASS-CONDITION-SPEC-AUDIT-01_委任_02.md`(Nは jsonl 内で `FABLE-DELEGATION-MARKER: KPDUAL-PROD-D1-委任_02-20261022` を含むAgent tool_useの0始まり通番、247前後)。`check_delegation_prompt.py`(見出し不一致FAILは既知の偽陽性)。
- commit(対象のみ)→push→到達確認。`docs/pm/ACTIVE_TASK.md`先頭に固定ヘッダ。`docs/pm/RESULT_PACKET_APCA2.md`へ報告: 設計要約((a)の現行force_secondary意味の確認結果と新モード要否/配線点/Store再利用の扱い案/費用/検証計画/A-2統合/rollback)+Opusレビュー論点3〜5個+RESULT_PACKET 4行+JPY0。

## 5. 禁止
Production .pyの編集、CURRENT_SPECの編集、KP英語解説・その他音声への適用拡大、minimal fallback既存挙動の変更、多語同音救済の仕様変更、有料API。