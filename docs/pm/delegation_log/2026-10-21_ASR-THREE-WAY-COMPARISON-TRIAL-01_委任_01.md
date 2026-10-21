# 委任文(Fable→sonnet-worker)

## 管理ID
ASR-THREE-WAY-COMPARISON-TRIAL-01 委任_01(ユーザー指示「KP4音声是正＋ASR 3方式総合比較Trial」のTask B専任: 事前調査→評価データ台帳→設計→Phase 1/2/3実行→集計→Trial記録。到達上限=`VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`の材料[最終ラベルはFable]。VALIDATEDでもProduction採用・配線はしない)。
並行agent: Task A(`FAMILY-X-MANGA-AI-CHAT-BYUS-KP4-TAKE-PART-REMEDIATION-01`、記事B KP4の再生成・差替え・Store無効化。`er019_output/.../manga_ai_chat_byus__run_byus_01/`・Master Store manifest・`user_test/manga_ai_chat_byus_e2e_01/`を編集する)と、B3丸めTrial agent。**あなたはこれらのファイルを書き換えない**(読み取り・コピーのみ)。旧KP4 `kp4_en.wav`(sha 675cd6b1…)はTask Aが`kp4_en.invalid_20261021.wav`等へ改名するので、S0で自分の作業dirへコピーして使う(どちらの名前でも拾えるようにする)。SSOT共有プロトコル: OPEN_ITEMS新規行/REPORT_LEDGER編集直前に`git status --porcelain`+再Grep→自分の行だけ→即add/commit、index.lock 30秒待ち。**`git add -f`/`-A`/`-u`禁止**。作業領域は `er091_asr_three_way_trial_01_*.py` / `er091_output/asr_three_way_trial_01/` / `docs/research/ASR-THREE-WAY-COMPARISON-TRIAL-01/` に限定。

## 性質/Status/禁止事項
- 性質: Trial(Trial専用評価実装)。**禁止**: ASR Primary/Secondary変更・モデル切替・Validator/救済機構/Cascade/Phrase List重みのProduction変更、ProductionのPrompt・routing変更、Master Store/記事成果物の変更、HR Lock迂回、有料runの再起動(26節)。
- 費用: Trial承認済みだが金額は未指定→7-7により**T-3 Guardrail=JPY250**(これを超える見込みが出たらその時点で実測・残作業・追加見積を添えてSTOP。先に無料・オフラインで得られる結論を確定させる)。日次1,000円: 本日既に約JPY420+並列2件(上限合計約130)あり、**S0で`docs/pm/tools/daily_dev_cost_01.py --date 2026-10-21`を実測**し、Phase実行前後にも再計測して残枠内で進める。Azureは秒課金のため長尺本文は高い(例: 60秒音声≒JPY2.7/回)→本文音声は音声数を絞り、反復(安定性)はKPなど短尺で行う。費用は`paid_calls.jsonl`に全件記録(出典単価: `er078_asr_unified_judge_01.py:80` JPY160/USD、pricing_snapshot)。
- 新規TTS: 原則不要。過去教材で正解ラベル付きの誤発音音声が不足する種類(子音/母音取り違え・脱落/追加・数字/否定)について、どうしても必要な場合のみ合計**8本以内**(Gemini、Trial専用dir、意図的作成音声として量産集計と区別)。それ以上はSTOP。
- 最新モデル原則(25節): 3方式はProduction同一(gpt-4o-mini-transcribe / Azure Speech en-US / faster-whisper small)=比較目的の例外として明記。Whisper別サイズ(medium/large-v3等)は、smallの誤りが「モデル容量由来」と実測で示された場合に限り1サイズ追加可。文字起こし正確性の採点にLLMを使う場合は最新上位系を明記。
- STOP: Guardrail超過見込み/新規TTS 8本超/新しい品質基準が必要/重大な品質問題(例: 現行Production構成が正常音声の大半を落とす等)/Trial承認範囲を超える変更が必要。

## 固定ブロック
E-1/D-1/G-1/F-1: 標準(SSOT全文読込禁止)。T-0: 本委任文を`docs/pm/delegation_log/2026-10-21_ASR-THREE-WAY-COMPARISON-TRIAL-01_委任_01.md`へ逐語保存(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、N=「ASR-THREE-WAY-COMPARISON-TRIAL-01 委任_01」を含む最新index)。check結果1行。T-2: 原則TTSなし(例外は上記8本以内)。
ユーザー指示原文は **Task A agentが** `docs/pm/delegation_log/2026-10-21_KP4-REMEDIATION-AND-ASR-THREE-WAY-TRIAL_USER.md` へ保存しcommitする。あなたはこのファイルを作成・編集しない(存在すればsha256を記録して参照。未作成でも作業は本委任文中の原文で進める)。

## ユーザー指示原文(2026-10-21、Task A/B共通の全文。あなたの担当はTask B・§7・§8 Task B)
--- 原文ここから ---
# Claude Code指示：KP4音声是正＋ASR 3方式総合比較Trial

## 目的

eigo-radioの音声品質検査について、品質を最優先に、処理速度・量産単価も含めた最適なASR構成を判断できる状態にする。

以下の2タスクを実施する。

- **Task A：記事B Standard KP4「take part」の問題音声是正**
- **Task B：OpenAI／Azure／ローカルWhisperの総合精度比較Trial**

Task Aはユーザーが実施承認済み。Task BはTrial実施承認済みだが、新しいASR構成のProduction採用は未承認。

両者を混同せず、独立して並列実行すること。

---

## Task A：KP4「take part」の問題音声是正

### Status・範囲

**既存の承認済み音声品質基準に基づく不具合修正。**

対象：
- Family X 記事B Standard
- Key Phrase 4「take part」
- 既存音声 `kp4_en.wav`

### 実施内容

1. 問題音声がMaster Storeから再利用されないよう、該当エントリを無効化する。正常な他エントリは変更しない。
2. 承認済みのProduction TTS仕様で音声を再生成する。
3. 既存のASR Validator・音声QAを実施する。
4. 「take part」が「take tart」「take heart」等に誤発音されていないことを確認する。
5. 正常な音声が得られたら、正式記事Bの該当箇所を差し替える。
6. Master Store、正式記事の音声、再生成・fallback・resume経路の整合を確認する。
7. 必要なRegression、SSOT、Git反映を完了させる。

**重要：**
- 現行ASR判定基準を勝手に変更してPASSさせない。
- Task Bの新方式を未承認のまま適用しない。
- 再生成だけで完成とせず、音声品質を確認する。
- 通常の品質検査で解決できない場合は、原因究明・修正を承認範囲内で自律的に進める。
- 発音の正誤を機械検査だけで確定できない場合は、試聴用音声と判断事項を報告する。

### 完了条件

問題音声が再利用されず、正しい音声への差し替えと既存品質検査が完了していること。

Production経路・runtime evidence・Regression・SSOT/Gitを照合してPRODUCTION_WIRED可否を報告する。記事全体のユーザー最終試聴PASSとは区別する。

---

## Task B：ASR 3方式 総合精度比較Trial

### Status

`TRIAL`。到達可能Statusは `VALIDATED`／`REJECTED`／`USER_DECISION_REQUIRED`。

**ASRのPrimary／Secondary変更、モデル切替、ValidatorのProduction仕様変更は禁止。**

### 1. 比較対象

| ASR | 現行の役割 |
|---|---|
| OpenAI `gpt-4o-mini-transcribe` | Primary |
| Azure Speech STT | Secondary |
| ローカル `faster-whisper small` | 独立検証 |

ローカルWhisperをPrimaryにする可能性も含め、先入観なく比較する。

必要性が実測で確認された場合は、Whisperの別モデルサイズもTrial内で比較してよい。ただし、無益なモデル探索は避ける。

### 2. 検証データの構成

**既存教材・過去Trial音声の再利用を優先する。**

少なくとも次の種類を含める。

**A. 正常音声**

- Key Phrase：短文、定型表現、固有名詞、造語、同音異綴り
- 本文：通常のニュース文章、長文、数字、固有名詞を含む文章、連結発音
- Standard／Advanced
- Family X／Z

原則として、過去に正しい発音が確認された音声を使用する。

**B. 問題音声**

- 既知の誤発音
- 子音・母音の取り違え
- 固有名詞の誤発音
- 単語の脱落・追加
- 数字・否定・意味を変える発音ミス
- 「take part」の既存NG音声

正常音声・誤発音音声の正解ラベルは、過去の人間試聴・信頼できる既存評価を優先する。ASR結果そのものを正解の根拠にしない。

過去教材だけでは十分な評価ができない場合は、必要な種類のTTSを新規生成してよい。ただし、正解発音・誤発音の確認方法を明確にし、追加音声数は必要十分に抑える。

正常音声と問題音声の構成比・選定理由を記録し、難例に偏った評価を避ける。評価用に意図的に作った音声は、通常量産の集計と区別する。

### 3. 比較方式

#### Phase 1：ASR単体の認識性能

同一音声を3方式に入力し、以下を比較する。

- 文字起こしの正確性
- 発音ミスの検出能力
- 正しい音声の過剰NG
- 固有名詞・同音異綴り・数字への対応
- 同一音声での認識安定性

単なる文字列一致率だけでは判断しない。

#### Phase 2：Production運用条件での比較

各方式の実際の補助機能を含めて評価する。

- OpenAI：Productionで使用しているPrompt等
- Azure：Phrase List、承認済み重み2.0
- Whisper：現行ローカル実行条件

Phrase Listが使えるケースと、今回の「take part」のように空になるケースを区別する。

Azure Phrase Listへ供給する発音情報の品質問題と、Azureモデル自体の認識性能を混同しない。

#### Phase 3：Validatorを含む最終品質

既存のValidator・救済機構・Cascadeを変更せず、候補構成ごとの最終判定を検証する。

候補：
1. OpenAI Primary → Azure Secondary（現行）
2. Azure Primary → OpenAI Secondary
3. Whisper Primary → OpenAI Secondary
4. Whisper Primary → Azure Secondary
5. その他、実測上有望な構成

Primary／Secondaryを入れ替えた場合に、現在の判定ルールや発動条件をそのまま使用できるとは限らない。

必要な変更と、その品質リスクを明示すること。

既存判定ロジックで比較できない構成についてはTrial専用の評価実装を使用し、正式Productionへ配線しない。

### 4. 主要評価指標

**品質（最優先）**

- 正常音声の正しいPASS率
- 誤発音音声の検出率
- 誤PASS率（誤発音の見逃し）
- 過剰NG率（正常音声の誤検出）
- 認識の安定性
- 固有名詞・同音異綴り・連結発音への対応

特に、誤PASSと過剰NGを混ぜず、それぞれ実例を提示する。

**Delivery**

- 1音声あたりの処理時間
- 1記事セットの想定検査時間
- 並列実行の可能性
- retry／fallbackによる時間増
- ローカルWhisperのCPU負荷・同時実行時の性能

**Cost**

- ASR API料金
- ローカルWhisperの計算資源・運用負荷
- 1記事セットの想定ASR原価
- 過剰NGに伴うTTS再生成費用
- Human Review増減による実質的な運用負荷

単純なASR呼出単価だけではなく、最終的な量産コストを比較する。

目標は70円／記事セット。品質を維持した原価削減を継続的に検討する。

### 5. Trial実施方針

事前にCURRENT_SPEC・DECISION_LOG・OPEN_ITEMS・過去ASR関連Trialを確認する。

特に以下の既存結果を再利用する。

- `FAMILY-X-KP-ASR-DUAL-PASS-TRIAL-01`
- Azure Phrase List重み1.0／1.5／2.0比較Trial
- byUs発音同等性の原因調査
- 過去のASR誤PASS／過剰NG検証
- 既存のHuman Review・再生成履歴

**品質上の重要な区別：**

今回のtake part Trialで確認されたのは「問題音声をAzureが検出したこと」であり、「Azureが正常音声も高精度に判定できること」ではない。

同様に、ローカルWhisperが同じNGを検出したことだけでPrimary採用に適すると判断しない。

試験対象数、音声の偏り、判定根拠、信頼性の限界を明示する。

同一音声の反復実行と、独立した複数音声での検証を区別する。

### 6. QCD・自律実行

- 既存の評価音声・正解ラベル・過去Trial結果を最大限再利用する。
- 独立する比較・集計作業は並列化する。
- 品質を守れる範囲で全体の完了時間を最小化する。
- API費用と残予算を管理する。
- 開発費は既存のJST日次予算1,000円および承認範囲を遵守する。
- 新規TTSが必要な場合も、Trial承認範囲内で必要十分な本数に限定する。
- 失敗が続く場合、同一条件の反復でなく原因・方法を見直す。
- 有効な結論が出た時点で追加検証を止める。

予算超過、新しい品質基準の必要性、重大な品質問題、またはTrial承認範囲を超える変更が必要な場合はSTOPし、ユーザー判断を求める。

---

## 7. Fable独立評価

FableはClaudeの試験結果を独立評価する。

特に以下を確認する。

1. 正解ラベルの信頼性
2. 通常音声と難例の偏り
3. 正常音声の過剰NGと誤発音の見逃し
4. ASR単体性能とValidator込み性能の区別
5. Primary／Secondary候補の品質・速度・原価
6. 既存Production仕様との整合
7. 追加検証の必要性と費用対効果

FableはProduction採用を代行しない。

---

## 8. 最終報告

Task AとTask Bを分けて報告する。

### Task A

- 問題音声の無効化結果
- 再生成音声の品質判定
- 差し替え結果
- Master Store・正式音声・retry/fallback/resumeの整合
- runtime evidence／Regression／SSOT／Git
- 完了Statusと未処理事項

### Task B

以下を経営・PM判断ができる形で報告する。

1. **結論：どのASR構成が最も有望か**
2. 正常音声のPASS率・誤発音検出率・誤PASS率・過剰NG率
3. Key Phrase／本文／固有名詞／数字等の種類別比較
4. 3方式の安定性と実例
5. 処理速度・原価比較（1記事セット換算）
6. Primary／Secondary入れ替えの利点・リスク
7. 現行Productionと候補構成の差分
8. Fable独立評価
9. 残存問題・必要な追加Trial
10. Production採用に関するユーザー判断事項

Trial結果は `VALIDATED`／`REJECTED`／`USER_DECISION_REQUIRED` に分類し、SSOT・OPEN_ITEMS・Gitへ記録する。

**重要：VALIDATEDはProduction採用を意味しない。ユーザーの正式承認があるまで、Primary／Secondary構成と既存ValidatorのProduction実装は変更しない。**

---

## 最終指示

**品質（Q）＞速度（D）＞量産単価（C）≫開発費用。**

Task Aは既存の品質基準に従って速やかに修正・完成させる。

Task Bは、ASRの単純なランキングではなく、eigo-radioの量産に最適なASR構成を判断できる客観的証拠を得ることをゴールとする。

十分な結論が得られたら過剰な検証を行わずTrialを終了し、ユーザーへ採用候補と判断材料を提示すること。
--- 原文ここまで ---

## 手がかり(鵜呑みにせず原文で確認)
- 再利用資産: `er088_kp_asr_dual_pass_trial_01.py`(3方式並列実行・Production判定関数呼出・費用記録の雛形。`er091`はこれを一般化する)、`docs/research/FAMILY-X-KP-ASR-DUAL-PASS-TRIAL-01/TRIAL_RESULT_01.md`、`docs/research/FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01/`(重み1.0/1.5/2.0比較の結果・音声・Phrase List有無別の判定)、`docs/research/FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01/{BYUS_EQUIVALENCE_INVESTIGATION_01.md, KP_TAKE_PART_INVESTIGATION_01.md}`(Store内EN 333件中29件のASR間不一致リスト=正常/問題の候補)、`docs/research/FAMILY-XZ-ASR-MULTI-DIFF-JUDGE-FIX-01/`、`docs/research/FAMILY-XZ-PROPER-NOUN-EN-PRONUNCIATION-SUPPLY-TRIAL-01/`。
- 正解ラベル源(優先順): (1)人間試聴記録=HR queue解決済み(`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`、`er007_output/ja_asr_cascade_01/human_review_queue.jsonl`)・`human_approved_segments.json`・ユーザー試聴PASS済み記事(Family X: melos等のFamily Z完成版、記事A/Bは試聴未了なので「正常」ラベルには使わない[ASR PASSのみでは正解にしない]、Family X過去完成記事のうちユーザー試聴PASS記録があるもの=OPEN_ITEMS/DECISION_LOGで`試聴PASS|LISTENING_PASS|USER_LISTENING_PASS`をGrep)、(2)過去Trialの人間ラベル付き誤発音集(`er008_*`吃音/disfluency QA教材、`er006_output/pool_pilot_01/`、`er020`/`er021`のequivalence検証セット、telemetry `er021_output/.../telemetry.jsonl`・`er025_output/.../telemetry.jsonl`=ラベルの出所を確認)、(3)Fable/Sonnet通読ラベルは「暫定」と明記し別集計。ASR結果そのものを正解にしない。
- Productionの各方式の呼出条件: Primary=`er006_preprod_hardening_01_validation.py`(Prompt/温度/言語指定の箇所)、Secondary=`er006_secondary_asr_01.py`(`AZURE_PHRASE_LIST_WEIGHT=2.0` L75、Phrase List=`er006_pronunciation_ledger_01.get_hint_for_text`)、統合判定=`er078_asr_unified_judge_01.py`(`force_secondary`、PASS条件)、Whisper=`er008_disfluency_qa_18.py:83-107`(`transcribe_verbatim`、small cpu int8)。Phase 3の入替構成は、Production関数を**呼び出す**(改変しない)形で「Primary転写文字列をどの方式から得るか」を差し替えるTrial wrapperで実現し、既存ルールがそのまま使えない点(例: Primaryの言語prior前提のCMU同音救済、Secondaryの`accepted`定義、`low_ratio`閾値0.98、entity救済、M1のUNCERTAIN限定)を構成ごとに列挙。
- 既存のKP音声: `er006_output/master_audio_store_01/manifest.json`(EN 333件。正常ラベルは「人間試聴PASS記事に含まれる+ASR間一致」など根拠を明記し、一致だけを根拠にしない)。本文音声: 完成記事の`full_story_part*.wav`/`support*.wav`(Std/Adv、X/Z)。

## 手順
S0. daily cost、`git status`、T-0。旧KP4をコピー。Phase 0: 過去Trial・SSOT確認(`PRIOR_WORK_01.md`、既存結果の再利用表)。
S1. **評価データ台帳**(`dataset_manifest.jsonl`+`DATASET_01.md`): 各音声=path/sha/種類(KP短文・定型・固有名詞・造語・同音異綴り/本文通常・長文・数字・固有名詞・連結)/Level/Family/正解ラベル(正常/問題[誤発音種別])/ラベル根拠(出典file:行、人間試聴か否か)/Phrase List有無。目標規模(費用内): KP 正常 30〜40本・問題 8〜15本、本文 正常 10〜15本・問題 3〜6本(短め区間を優先、Azure秒課金)。X/Z・Std/Adv・Phrase List有/無を含める。偏りと不足を明記。不足種類は新規TTS(≤8本)で補う可否を見積り、作る場合は「正解発音/誤発音の確認方法」(例: 意図的誤綴り入力でTTSさせ、Whisper/Azure/Primary全一致+Sonnet聴取でラベル)を先に記す。**費用見積(方式別・Phase別)をここで出し、Guardrail JPY250・日次残枠と照合してからPhase 1へ**。
S2. Phase 1(3方式×全音声×1回+安定性は短尺20本×3回): 転写・WER/CER・内容語差分・固有名詞/数字の扱い・処理時間・Whisper CPU負荷/同時実行(2並列と直列の比較)。Phase 2: OpenAI Production Prompt条件/Azure Phrase List有無(Ledger hintあり語は供給あり・なしの両方)/Whisper現行条件=Phase 1の実行条件をProduction同一にして差を記録(追加呼出は最小)。Phase 3: 候補構成1〜5の最終判定(Production判定関数呼出、Trial wrapper)。混同行列(正常/問題×PASS/NG)を構成別・種類別に出し、誤PASS実例と過剰NG実例を別々に列挙。
S3. 集計・原価: 1記事セット換算(KP 5×2+本文 Std/Adv各3部+Support等=実際のセグメント数を記事Bの構成から数える)の検査時間・ASR原価・過剰NG由来の再生成TTS費用期待値・HR到達期待値を構成別に試算(前提を明記)。
S4. 記録: `TRIAL_DESIGN_01.md`(S1終了時にcommit)、`TRIAL_RESULT_01.md`(ユーザー§8 Task Bの1〜10順、8はFable欄を空けておく)、`paid_calls.jsonl`、results/集計csv、OPEN_ITEMS新規行(Status `TRIAL_DONE_PENDING_FABLE`、またはSTOP時は `USER_DECISION_REQUIRED`候補)、REPORT_LEDGER、ACTIVE_TASK(ローカル)。CURRENT_SPEC/DECISION_LOGは変更しない。secret scan→明示add→commit→`git push origin HEAD:main`。

## 報告(docs/pm/RESULT_PACKET_ASR3W1.md 上書き。ユーザー§8 Task Bの1〜10順[8はFable独立評価用に「Sonnetが自己申告する限界」のみ記載]+費用[出典付き]+使用モデル/最新か+限界。Sonnetは「判断候補」表記、Statusラベルは付けない)