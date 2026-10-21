# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-KP-ASR-DUAL-PASS-TRIAL-01 委任_01(Key Phrase音声QA「Primary+Secondary両方PASS方式」の限定Trial: 既存採用音声`kp4_en.wav`[run_byus_01 Std KP4「take part」]に対し、Primary ASR/Secondary Azure/ローカルWhisperを各10回**独立に**実行し、両方PASS方式の検出能力・安定性・費用を事実として記録する)。並行agentなし。

## 性質/到達上限Status/禁止事項
- 性質: ユーザー承認済みの限定Trial(ASR再実行のみ)。到達上限=`VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`の材料提示(最終StatusはFable)。Production採用は別途ユーザー判断。
- 費用: 本日2026-10-21(JST)既使用=S0で`daily_dev_cost_01.py --date 2026-10-21`実測(直近275.17+α)。本Trial見積: Primary gpt-4o-mini-transcribe 約2秒音声×10(約0.01〜0.05円/回)+Azure STT 約2秒×10(約0.09円/回、`er078_asr_unified_judge_01.py:79-80,110-113`の式)+Whisperローカル0=**約JPY1〜3**。承認区分C。T-3 Guardrail=JPY30(想定外の呼出増があればSTOP)。
- 禁止: TTS新規生成/既存記事・音声・Master Audio Store・run dir・Ledger・review_queueの変更/Production code・Prompt・Validator・ASR routing・同音等価判定・Phrase List設定の変更/Trial途中での認識条件・判定基準の変更と再試行/10分cooldownの挿入/`git add -A`等。
- 共有ログ(attempt_history/review_queue/telemetry/master store)へ**書き込まない**(Trial専用out_dirのみ。既存関数が共有ログへ書く副作用を持つ場合は、書込を避ける呼び方[引数/モード]を選ぶか、Trial専用pathへ向ける。避けられなければ実行前にSTOP報告)。
- 最新モデル原則(25節): 比較目的のためProductionと同一(Primary gpt-4o-mini-transcribe、Azure speech STT、ローカルfaster-whisper small=吃音QAと同設定)。理由=現行QAの検出能力の実測。報告に明記。
- 時間見込み: 設計・harness 30分、実行10分(10セットは独立。Primary/Azureは同時3〜4並列可、Whisperはローカル直列)、集計・報告20分。

## 固定ブロック
E-1/D-1/G-1/F-1: 標準。T-0: 本委任文を`docs/pm/delegation_log/2026-10-21_FAMILY-X-KP-ASR-DUAL-PASS-TRIAL-01_委任_01.md`へ逐語保存(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、N=「KP-ASR-DUAL-PASS-TRIAL-01 委任_01」を含む最新index)。check結果1行。T-2: TTSなし(ASRのみ)。

## ユーザー指示(原文・2026-10-21、全文)
`docs/pm/delegation_log/2026-10-21_FAMILY-X-KP-ASR-DUAL-PASS-TRIAL-01_USER.md`へ逐語保存(先頭に`# ユーザー指示原文(2026-10-21)`と`管理ID: FAMILY-X-KP-ASR-DUAL-PASS-TRIAL-01`の2行、以降一字一句変えない。文字数・sha256[本文のみ]を報告)。
--- 原文ここから ---
# Claude Code／Fableへの指示
## Family X Key Phrase音声QA — Primary／Secondary両方PASS方式のTrial-01

### 1. 目的・背景

Family X「漫画のキャラクターとAIで会話（byUs）」のStandard Key Phrase 4「take part」に、ユーザーから「take tart」と聞こえるとの指摘があった。

既存調査では以下を確認済み。

- Primary ASR：`Take part.` → PASS
- ローカルWhisper：`Take Tarte.` → 不一致（判定に未使用）
- Secondary Azure：Primary PASSのため未実行
- TTS再生成：なし
- 最終音声：誤発音の疑いが強いが、音声学的な確定は未了

Key Phraseは学習者が発音に注目するセクションであり、通常本文よりも誤発音の影響が重大。

**ユーザーは、Key PhraseについてPrimary／Secondaryの両方を必須とし、両方が既存の同音等価判定を含む品質基準でPASSした場合のみOKとする方式を、検証する方針に同意した。**

ただし、Production正式採用はTrial結果確認後に別途判断する。

### 2. Trial対象・条件

対象は既存のStandard Key Phrase 4「take part」の採用音声。

- Production run：`run_byus_01`
- 音声：`kp4_en.wav`（実際に採用されたTake 1）
- 既存音声をそのまま使用
- 同一音声・同一台本・同一判定条件を固定
- Primary／Secondary／ローカルWhisperで各10回の認識を実施
- 既存の同音等価判定・発音照合仕様を変更しない
- Azure Phrase Listは既存Production設定（重み2.0）を維持し、実際に使用したPhrase Listも記録する

キャッシュされた文字起こし結果を10回表示するのではなく、各回の認識処理を独立して実行すること。

ただし、外部API呼び出しの重複防止機構などが存在する場合は、その動作を確認し、実行回数を正確に記録する。

### 3. 実施方法

以下を10セット実施する。

| Trial | Primary | Secondary | ローカルWhisper |
|---|---|---|---|
| 1 | 実行 | 実行 | 実行 |
| 2 | 実行 | 実行 | 実行 |
| 3 | 実行 | 実行 | 実行 |
| 4 | 実行 | 実行 | 実行 |
| 5 | 実行 | 実行 | 実行 |
| 6 | 実行 | 実行 | 実行 |
| 7 | 実行 | 実行 | 実行 |
| 8 | 実行 | 実行 | 実行 |
| 9 | 実行 | 実行 | 実行 |
| 10 | 実行 | 実行 | 実行 |

各回で必ず以下を保存する。

- Primary ASRの文字起こし原文とPASS／NG
- Secondary Azureの文字起こし原文とPASS／NG
- ローカルWhisperの文字起こし原文とPASS／NG相当の評価
- Primary＋Secondaryの両方PASS方式による総合判定
- 判定理由（完全一致・同音等価・不一致等）
- API実費・実行時間

Whisperは今回の比較用とし、総合判定の条件には加えない。

### 4. 評価すること

**① 検出能力**

今回の疑わしい音声が、Primary＋Secondary両方PASS方式によって何回NGになるか。

**② 認識の安定性**

同一音声を10回認識させたとき、Primary・Secondaryそれぞれの転写がどの程度変動するか。

**③ 誤PASSの可能性**

両方PASSとなった場合でも、それを発音の正しさの証明とはしない。

同じ発音不良を両ASRが見逃す可能性を評価する。

**④ 原価・速度**

- 追加Secondaryの実測費用
- Key Phrase 5件×Standard／Advancedの10音声に適用した場合の費用見込み
- 追加処理時間
- NG増加に伴うTTS再生成・Human Reviewリスク

今回の音声1件だけで一般的な検出率・誤NG率を断定しない。

### 5. Fable独立評価

Fableは次を確認する。

- 実際に各ASRを10回実行した証拠
- 同一音声・同一設定で比較したこと
- 同音等価判定を既存仕様どおり適用したこと
- Primary／Secondary両方PASSの判定結果
- 誤PASS・過剰NGのリスク
- Production採用に向けて残る未検証事項

結果が期待どおりでなくても、Trial途中でPrompt・認識条件・判定基準を変更して再試行しない。

### 6. 費用・STOP条件

- 今回は承認済みの限定Trialとして実行する。
- TTS新規生成は禁止。
- 既存記事・音声・Master Audio Storeは変更しない。
- Productionコード・Prompt・Validator・ASR routingは変更しない。
- 日次開発予算1,000円（JST）と既存の個別予算枠を遵守する。
- 想定を超える費用や重大な技術的問題が判明した場合は停止して報告する。

試行間に不要な10分Cooldown等を設けない。独立実行・並列化が安全に可能な範囲で、品質と正確な計測を維持しながら最短で完了する。

### 7. Trial終了報告

10回分の結果を、次の形式で一覧表示する。

| 回 | Primary転写／判定 | Azure転写／判定 | Whisper転写／判定 | 両方PASS方式 |
|---|---|---|---|---|
| 1〜10 | | | | |

さらに以下を簡潔に報告する。

1. Primary PASS回数（10回中）
2. Secondary PASS回数（10回中）
3. Primary＋Secondary両方PASS回数（10回中）
4. 今回の疑わしい音声を何回NGとして検出できたか
5. 実費と量産時の追加費用見込み
6. Fableの独立評価と推奨

**Trial終了Statusは `VALIDATED`／`REJECTED`／`USER_DECISION_REQUIRED` のいずれかとする。**

今回の結果からProduction採用を自動的に決定しない。未承認の追加Trial・Production実装へ進まない。

### 8. 最重要事項

今回知りたいのは、**「take tart」のように聞こえる音声を、Primary＋Secondary両方PASS方式で検出できるのか**という一点。

対策を先に作るのではなく、まず既存音声で事実を確認すること。
--- 原文ここまで ---

## 設計(生成前に`docs/research/FAMILY-X-KP-ASR-DUAL-PASS-TRIAL-01/TRIAL_DESIGN_01.md`へ固定しcommit。以後変更しない)
- 対象音声: `er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01/a2/narration/kp4_en.wav`(sha256 675cd6b1…2186を確認し記録、読み取りのみ。Trial out_dirへコピーして使用)。台本canonical="take part"(KP英語Componentの検証に渡される正確なcanonical文字列を`tts_generation_results.json`のkey_phrases.4.englishから取得)。
- 判定関数: Production KP英語Componentが使う**同じ**判定経路(`generate_key_phrase_component_verified`内のPrimary判定=`er006_preprod_hardening_01_validation.py:1000-1011`付近のclassify/NORMALIZED_MATCH、Secondary=`er006_secondary_asr_01.py`のAzure評価[Phrase List構築含む]、統一judge `er078_asr_unified_judge_01`があればそれ)。Trial harness(`er088_kp_asr_dual_pass_trial_01.py`)はこれらをimportして呼ぶ(コピー・改変禁止)。各回の判定ラベル(EXACT/NORMALIZED/HOMOPHONE_EQUIVALENT/TRUE_CONTENT_MISMATCH等)と理由をそのまま保存。
- Primary: gpt-4o-mini-transcribe、Productionと同じprompt/言語/温度設定(`er003_v1_repro01_main_generate.py:771-775`付近の呼び方を特定し同一に)。**キャッシュ/重複防止の確認**: 転写結果cache(wav sha keyのqa_evidence再利用、Master Storeのcache、OpenAI側のidempotency等)が無いかコードで確認し、各回が実際にAPIを呼ぶ経路を使う(raw_usage/応答id/timestampを各回保存して独立実行の証拠にする)。
- Secondary: Azure STT、Production設定(Phrase List構築関数に同じcanonical/Ledgerを渡し、**実際に構築されたPhrase List内容とsetWeight実行有無をharnessで記録**。Phrase Listが空ならその事実を記録、空のままで実行=既存Production設定どおり)。
- ローカルWhisper: 吃音QA(`er008_disfluency_qa_18.py`)が使うfaster-whisper small と同じモデル/設定で10回(seed固定の有無も記録。決定論的なら10回同一になる旨を記録し、それも事実として報告)。判定はPrimaryと同じclassify関数に通して「PASS相当/NG相当」。
- 両方PASS方式: 総合OK=PrimaryがPASS(EXACT/NORMALIZED/既存の同音等価含む) かつ SecondaryがPASS(既存のaccept基準)。WhisperはOKの条件に含めない。
- 並列: Primary/Azureは10回を同時3並列まで、Whisperは直列。各回の壁時計時間・API応答時間を記録。10分cooldownを入れない。
- 費用: 各呼出のusage(秒数/トークン)から実費算出(単価の出典を明記)。

## 手順
S0. daily cost/`git status`件数/T-0・原文保存/対象wav sha確認/cache機構の確認結果を設計書に記載→commit(`FAMILY-X-KP-ASR-DUAL-PASS-TRIAL-01 委任_01: T-0+ユーザー原文+事前登録設計(実行前)`)→push。
S1. harness実行(out_dir `er088_output/kp_asr_dual_pass_trial_01/`、`results.jsonl`[回ごと全項目]、`summary.json`、各API応答生データ)。
S2. 集計: ユーザー§7の表(10行)+PASS回数(Primary/Secondary/両方)+NG検出回数+転写のバリエーション一覧(Primary/Azure/Whisperそれぞれのユニーク転写と出現回数)+費用(実測)+量産見込み(KP5件×Std/Adv=10音声/記事セットにSecondary追加: 実測単価×10+処理時間)+NG増加時の再生成/HRリスクの定性記載(断定しない)。
S3. `docs/research/FAMILY-X-KP-ASR-DUAL-PASS-TRIAL-01/TRIAL_RESULT_01.md`(表・集計・独立実行の証拠[応答id/timestamp一覧]・Phrase List記録・未検証事項)。Sonnet所見は「判断材料」として記載、最終Status(VALIDATED/REJECTED/USER_DECISION_REQUIRED)はFable。
S4. SSOT: `OPEN_ITEMS.md`新規行1件(Status `KP_ASR_DUAL_PASS_TRIAL_DONE_PENDING_FABLE`)、REPORT_LEDGER 1行、ACTIVE_TASK先頭追記。CURRENT_SPEC/DECISION_LOGは変更しない。secret scan→明示add(delegation_log 2件、docs/research/...、er088_*.py、er088_output配下[wavコピーはgitignore対象なら除外しsha記録])→commit→`git push origin HEAD:main`。

## 報告(docs/pm/RESULT_PACKET_KPDP1.md 上書き)
ユーザー§7の表→1〜5の数値→独立実行の証拠要約(10回分のAPI応答id/時刻、cache非使用の根拠)→Phrase List内容・setWeight実行有無→転写バリエーション→費用(実測・出典)と量産見込み→未検証事項→判断候補(Sonnetは「判断候補」表記、Statusは付けない)→commit hash・raw URL→4行判定。