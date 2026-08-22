# ER-006-POOL-ADOPTION-AUDIT-01 — 既存3記事のProduction差分記録

**管理ID: ER-006-POOL-ADOPTION-AUDIT-01**
**日付: 2026-08-22**

このファイルは、Pool Topic No.1〜3(Public Benches/Subscriptions/Startups)
の最終採用Candidateが、**生成された当時どの実装方式で作られたか**と、
**現行Production仕様**との差分を記録する。過去の生成物を「現行仕様で
生成した」と履歴を書き換えないための、Provenance(来歴)の正式記録。

差分は`CONTENT_AFFECTING`(script内容・学習体験に影響しうる)/
`QA_ONLY`(検証方法だけが異なる)/`COST_ONLY`(出力品質には原則影響せず
コスト/処理方式のみ異なる)/`UNKNOWN`(影響を確定できない)に分類する。
分類は各成果物の実際のaudit/manifestファイル(model名・timestamp)を
確認した上で行った(ファイル名やcommit日付からの推測ではない)。

## 1. 最終採用Candidateの特定

| Topic | Level | Script(出典) | Audio(出典) | 選定理由 |
|---|---|---|---|---|
| Public Benches | B1/A2 | `er006_output/pool_pilot_01/pool_benches_luna/{b1b,a2}/` (Luna Writer版) | `er006_output/pool_pilot_01/pool_benches_pilot_02/{b1b,a2}/` (OpenAI ASR Primary + Master Audio Store配線後の再生成) | 3世代存在(`pool_benches`=Sol初版、`pool_benches_luna`=Luna版、`pool_benches_pilot_02`=Luna記事のままASR/Master Audio刷新版)。`pool_benches_pilot_02/*/parts.json`が`pool_benches_luna`のparts.jsonとbyte単位で完全一致することを確認済み(記事内容は無変更、audio生成方式のみ更新)。現行Productionに最も近い組み合わせとして、記事=Luna版、audio=pilot_02版を採用 |
| Subscriptions | B1/A2 | `er006_output/pool_pilot_01/pool_subscriptions/{b1b,a2}/` | 同左(script/audioとも単一世代のみ存在) | 再生成・再検証は一度も行われていない(Luna版・ASR-Pilot-02版いずれも作成されていない)。存在する唯一の版をCandidateとする |
| Startups | B1/A2 | `er006_output/pool_pilot_01/pool_startups/{b1b,a2}/` | 同左(script/audioとも単一世代のみ存在) | 同上 |

## 2. Script/Audio一致確認結果(タスク仕様§6/PART A §7対応)

各Candidateについて、TTSへ実際に送信されたtext(`audit/tts_generation_
results.json`の`text`フィールド)と、正式script(`parts.json`/
`*_support_texts.json`)を全15区分(Preview/Comment1-4/Full Story Part1-2/
Point One/Point Two/In One Line + 見出し類)+Key Phrase 5件で突き合わせた。

**結論: 送信テキストと正式scriptは、既知の安全な正規化(curly quote→
straight quote、"three"→"3"等のTTS-safe数字置換、パラグラフ改行の
単一空白化)を除き完全一致。script側だけが後から書き換わり、audioが
旧scriptのまま、という不一致は見つからなかった。**

ただし、**一部segmentのaudioがASR検証未合格のまま(status="STOPPED")
最終assembled音声へ含まれている**ことを検出した(いずれもTTSへ送信した
テキスト自体は正しく、ASR側の書き起こし精度・当時のValidator世代側の
限界による既知の問題)。

| Topic | Level | Segment | 状態 | 内容 |
|---|---|---|---|---|
| Benches | B1 | Point One | 6回ASR試行全てTRUE_CONTENT_MISMATCH判定 | 研究者名"Ottoni"をASRが"A Tony"/"Atoni"/"O'Toole"等に誤認識(既知のASR限界、[OPEN-46/47/48]参照)。TTS自体は正しく読み上げている可能性が高いが未確認 |
| Benches | B1 | Comment 3 | 同上 | ASR書き起こしは script と句読点(ピリオド vs カンマ)のみ差異。意味内容は一致しており、生成当時のValidatorがこの種の句読点差を吸収できなかった可能性が高い(現行Validatorなら通る可能性があるが未検証) |
| Benches | A2 | Full Story Part1 | 標準+minimal instruction経路とも6回不合格 | 同じく研究者名の異表記("O'Toone"等)がASRで生じている。Ottoni系の既知限界 |
| Subscriptions | B1 | Comment 2 | 6回ASR試行全てFAIL判定 | ASR書き起こしは"cancelling"(英)/"canceling"(米)の綴り違いのみ。**この正確なケースは現行Validatorのregression fixtureに"POSITIVE(吸収してよい)"として明示登録されており([er006_preprod_hardening_01_validation_test.py](er006_preprod_hardening_01_validation_test.py)の"cancelling/canceling (subscriptions/b1/comment_2)")、現行Validatorであれば合格していたはずの生成当時のみの誤検知**と判断できる |
| Subscriptions | A2 | Full Story Part2 | 標準+minimal instruction経路とも6回不合格 | ASR書き起こしに断片的な乱れが見られる("consent.Records pepped for"等)。日付表記("October 16th"等)や区切りの取り違えの可能性があるが、実際の音声を聞かないと断定できない |
| Startups | A2 | Full Story Part1 | 標準+minimal instruction経路とも6回不合格 | ASRが"may first run"を"May 1st run"と誤認識。**このケースも現行Validatorのregression fixtureに"NEGATIVE(絶対に吸収してはいけない)"として明示登録されており([er006_preprod_hardening_01_validation_test.py](er006_preprod_hardening_01_validation_test.py)の"may misheard as May 1st")、現行Validatorでも引き続き自動PASSにはならず、Human Review対象のまま**(=これは「古いValidatorの誤検知」ではなく「現在も未解決の曖昧ケース」) |

**この表の意味**: 上記6箇所は、script内容そのものは正しい可能性が高い
一方、機械的なASR検証には合格していない状態でassembled音声に含まれて
いる。「Script/Audioの対応」自体は取れているため`FINAL_ADOPTION_PENDING_
USER_REVIEW`へ進めるが、下記5節のユーザー確認Artifactでは、この6箇所を
名指しでユーザーに注意喚起する(実際に聞いて問題なければ手動でPASS
扱いにできるが、機械QAだけでは合否を判定していないことを明示する)。

## 3. Production差分表(生成時 vs 現行Production)

### 3-1. Public Benches(script=Luna版、audio=pilot_02版)

| Stage | Artifact生成時 | Current Production | Difference分類 |
|---|---|---|---|
| Query Planning | 該当なし(Pool Topicは通常のQuery Planningを経由しない) | 同左 | 差異なし |
| Topic Selection | 手動選定(Topic Selectionをスキップ、コスト0円) | POOL_TOPIC_MASTER.mdでの正式リスト化(本タスクで整理)。No.1-3は生成後に遡ってMasterへ編入 | `QA_ONLY`(記録・管理方法の違いのみ、記事内容に影響しない) |
| Research(Evidence Pack/VFL/Verification) | GPT-5.6 Luna | GPT-5.6 Luna | 差異なし(Research層はER-006新規構築時からLuna) |
| Writer(B1/A2) | GPT-5.6 Luna | GPT-5.6 Luna | 差異なし |
| Fact Check | GPT-5.6 Luna | GPT-5.6 Luna | 差異なし |
| Support | GPT-5.6 Luna | GPT-5.6 Luna | 差異なし |
| Key Phrase | GPT-5.6 Luna(Support経由) | GPT-5.6 Luna | 差異なし |
| TTS API | Standard(`client.models.generate_content`) | Gemini Batch API(`client.batches.create`) | `COST_ONLY`(ER-006-AUDIO-COST-SPEC-FIX-01でHuman Review試聴によりStandardとBatchの品質差なしを確認済み) |
| ASR Primary(英語) | OpenAI `gpt-4o-mini-transcribe`(PILOT-02で切替済み) | 同左 | 差異なし |
| ASR Primary(日本語) | Azure Speech STT | 同左 | 差異なし |
| ASR Secondary(Cascade) | 未実装(Cascade導入前) | Secondary ASR Cascade実装済み(`FEATURE_FLAG_SECONDARY_ASR_ENABLED=False`が既定、Production defaultは無効のまま) | `QA_ONLY`(featureが既定無効のため、現行実行でも動作は同じになる可能性が高い) |
| Validator | street/St.吸収・canonical placeholder修正済みだが、数値正規化の一般化前(cardinal/ordinal/percent等の吸収は未実装) | 数値正規化を含む一般化Validator | `QA_ONLY`(上記2節の一部STOPPED segmentは、この差分が原因の可能性が高い) |
| Master Audio | 最小実装で配線済み(PILOT-02) | 同左(最小実装のまま、変更なし) | 差異なし |
| Retry policy | 単純retry(ASR-first Cascade導入前) | ASR-first Retry Policy(Primary#1→#2→Secondary#1→#2→Human Review) | `QA_ONLY` |
| Pronunciation Ledger | 未実装 | 実装済み(ASR側Phrase List配線のみ、TTS Hint注入は未配線) | `QA_ONLY`(Ottoniのような固有名詞ASR誤認識は、Pronunciation Ledger導入後でも実証的な改善効果が確認できていない[ER-006-PRONUNCIATION-LEDGER-SECONDARY-ASR-01]ため、この差分がPoint One等の解決を保証するわけではない) |

### 3-2. Subscriptions / Startups(script/audioとも単一の原初版)

| Stage | Artifact生成時 | Current Production | Difference分類 |
|---|---|---|---|
| Query Planning | 該当なし | 同左 | 差異なし |
| Topic Selection | 手動選定 | POOL_TOPIC_MASTER.mdでの正式リスト化 | `QA_ONLY` |
| Research(Evidence Pack/VFL/Verification) | GPT-5.6 Luna | GPT-5.6 Luna | 差異なし |
| **Writer(B1/A2)** | **GPT-5.6 Sol** | **GPT-5.6 Luna** | **`CONTENT_AFFECTING`**(Writer modelの変更は文章表現・構成に影響しうる。ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01でSol版とLuna版を比較した際、Audio面のSTOPPED数はLuna版でやや増加したが、原因はLuna特有の品質劣化ではなくASR表記揺れ・固有名詞発音差と判定された。Subscriptions/StartupsはLuna版が一度も作られていないため、Sol版とLuna版の直接比較評価は行われていない) |
| **Fact Check** | **GPT-5.6 Sol** | **GPT-5.6 Luna** | **`CONTENT_AFFECTING`**(Writerと同じ理由) |
| **Support** | **GPT-5.6 Sol** | **GPT-5.6 Luna** | **`CONTENT_AFFECTING`**(同上) |
| Key Phrase | GPT-5.6 Sol(Support経由) | GPT-5.6 Luna | `CONTENT_AFFECTING`(同上) |
| TTS API | Standard | Gemini Batch API | `COST_ONLY` |
| **ASR Primary(英語)** | **Azure Speech STT** | **OpenAI `gpt-4o-mini-transcribe`** | **`QA_ONLY`**(検証方法の違いのみ、記事・音声の内容自体は変わらない) |
| ASR Primary(日本語) | Azure Speech STT | 同左 | 差異なし |
| ASR Secondary(Cascade) | 未実装 | 実装済み(default無効) | `QA_ONLY` |
| Validator | Pool Pilot最初期のValidator(街路名等の限定的略語吸収のみ、street/St.やcanonical placeholder修正すら未反映) | 数値正規化含む一般化Validator | `QA_ONLY`(Comment 2の"cancelling/canceling"誤検知はこの差分が直接原因) |
| Master Audio | 未実装 | 実装済み(最小実装) | `COST_ONLY`(重複TTS呼び出しの削減のみ、内容には影響しない) |
| Retry policy | 単純retry | ASR-first Retry Policy | `QA_ONLY` |
| Pronunciation Ledger | 未実装 | 実装済み(ASR側配線のみ) | `QA_ONLY` |

**Subscriptions/Startupsについての重要な注記**: Writer/Support系がSol
のままである点は、Benches(Luna版・pilot_02版が既に存在)と異なり、
**現行Production仕様との差分の中で唯一`CONTENT_AFFECTING`に分類される
項目**である。ただし、これは「品質が低い」ことを意味しない
(Sol版articleがFact Check/Ledger Deviation Checkに合格していることは
別途確認済み)。あくまで「現行の標準生成経路(Luna)とは異なるモデルで
生成された」という事実の記録であり、最終的な採用可否はユーザーが
script/audioを確認した上で判断する。

## 4. Provenance文(成果物への付記文言)

タスク仕様§12に基づき、正式採用時も生成履歴を書き換えない。以下の
文言をARTIFACT_REGISTRY.md等、成果物の記録箇所へ付記する:

> Final artifact adopted after user review.
> This artifact predates parts of the current Production pipeline
> (see [ER-006-POOL-ADOPTION-AUDIT-01_diff.md](ER-006-POOL-ADOPTION-AUDIT-01_diff.md) for exact differences).
> Generation provenance is preserved separately from adoption status.

## 参照元

[POOL_TOPIC_MASTER.md](POOL_TOPIC_MASTER.md)、[CURRENT_SPEC.md](CURRENT_SPEC.md)、
[DECISION_LOG.md](DECISION_LOG.md)、[OPEN_ITEMS.md](OPEN_ITEMS.md)、
ER-006-POOL-PILOT-01完了報告、ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01完了報告、
ER-006-AUDIO-COST-PILOT-02完了報告、ER-006-VALIDATOR-NUMERIC-COST-RECONCILE-01完了報告
