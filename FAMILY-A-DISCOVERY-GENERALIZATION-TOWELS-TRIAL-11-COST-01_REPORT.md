# FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-COST-01 — Report

管理ID: `FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-COST-01`
(Sonnet委任、PM-CLOSEOUT-CONSOLIDATION-77の一部)。実施者: Sonnet
(sonnet-worker)。対象: `FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11`
(A2+B1B、Discovery Focus Module Part A単独、タオル臭テーマ、Trial扱い・
Production未採用)。**本Reportは「コスト報告ルール(1記事あたり総コスト)」
新設ルールの初回適用**であり、新規API呼び出し・コード変更・Production
変更は一切行っていない(既存artifact/ログの読み取り集計のみ、追加費用¥0)。

並列稼働中の他タスク(A2表記ゆれreconcile/B1B Secondary ASR+retry timing
分析/Repetition QA根本原因/日本人名英語表記再調査)の生成物・出力先には
一切触れていない。

## 0. データソース

- text-gen(記事本体生成)側: `er011_output/discovery_generalization_
  towels_trial_11/raw_usage_log.jsonl`(19レコード、全てopenai/
  gpt-5.6-luna)、`cost_summary.json`(公式集計、`total_jpy=117.72`)。
- audio(TTS/ASR)側: `er011_output/discovery_generalization_towels_
  trial_11/audit/raw_usage_log_audio_01.jsonl`(179レコード)、
  `audit/cost_summary_audio_01.json`(公式集計、`total_jpy=12.76`、
  `gemini_batch`分は**OPEN-144バグにより¥0計上**)。
- 単価: `er005_output/cost_baseline_01/pricing_snapshot.json`
  (`gpt-5.6-luna`/`gpt-4o-mini-transcribe`/`gemini-2.5-pro-preview-tts`
  Standard・Batch各tier、`OFFICIAL_SOURCE`/`PROJECT_INTERNAL_RECORD`)。
- 為替: `USD_TO_JPY = 160`(`compute_topic_cost.py`等、既存プロジェクト
  定数)。

## 1. 検算方法と一致確認

公式`cost_summary.json`の集計ロジック(`cost_stage()`)を独自に模した
再集計script(本タスク限りのscratchpad、Production/既存scriptへの変更
なし)で、pricing_snapshot.jsonの単価をレコードごとのtoken数へ適用し
再集計した。

- text-gen側: 再集計合計 **¥117.72** で公式`cost_summary.json`の
  `total_jpy=117.72`と**完全一致**(検算成功)。
- audio側(gemini_batchをバグ修正前の`provider=="gemini"`判定のまま
  再現): 再集計合計 **¥12.76** で公式`cost_summary_audio_01.json`と
  完全一致(バグの再現も含め検算成功)。
- audio側(gemini_batchをBatch単価[input $0.5/1M・output $10/1M]で
  正しく計算): 再集計合計 **¥62.83**。OPEN-144登録時の手動概算
  (¥62.83)と完全一致。

## 2. 費用内訳(1記事一式 = A2+B1B合計)

### 2-1. text-gen(記事本体生成: Research/Ledger/Writer/Fact Check/
Support/Key Phrase)

| 費目 | 金額(¥) | 備考 |
|---|---|---|
| Research(Researcher、Web検索14件) | 27.87 | うちWeb検索tool呼出し手数料**¥22.40**(2-2「外部呼び出し費用の分離報告」、$10/1000件換算)、token分¥5.47 |
| Ledger Verification(独立検証、Web検索14件) | 27.60 | うちWeb検索tool呼出し手数料**¥22.40**、token分¥5.20 |
| Writer+Fact Check+Support+Key Phrase(A2、6 API call) | 28.30 | ログの`stage`タグが`writer_a2`で一括されており、Writer本文生成/Fact Checker/Support文/Key Phrase選定を個別費目へ分離**不可**(取得不可: 理由=stageタグ粒度不足) |
| Writer+Fact Check+Support+Key Phrase(B1B、11 API call) | 33.94 | 同上(取得不可: 理由=同上) |
| **text-gen小計** | **117.72** | 公式`cost_summary.json`と完全一致 |

Web検索手数料(Research+Ledger合計¥44.80)は、記事生成の主経路とは別に
独立して外部API(web_search tool)を呼び出すComponentの費用であり、
PM_GOVERNANCE 2-2「外部呼び出し費用の分離報告」に基づき分離表示した。

### 2-2. audio(TTS/ASR: 通常運用範囲)

本Trialの音声生成は`TTS_EXECUTION_MODE`環境変数を明示指定しておらず、
`er006_batch_tts_wiring_01.py`の既定値(`DEFAULT_TTS_EXECUTION_MODE =
BATCH`)により**Gemini Batch API経由(`provider=="gemini_batch"`)で
実行された**(Standard同期ではない)。

| 費目 | 金額(¥、Batch単価で訂正後) | 備考 |
|---|---|---|
| TTS本番(標準3take+既存fallback cascade) | 40.22 | gemini_batch¥35.67+openai(narration系)¥0.28+openai_asr(ASR)¥4.27 |
| Audio用scaffold(TTS読み上げ用テキスト整形等) | 0.92 | openai |
| Audio用Key Phrase整合性retry(TTS用、B1B初回`KEY_WORDS_STRUCTURE_INVALID`→再選定) | 5.69 | openai |
| **通常運用範囲 小計** | **46.83** | |

### 2-3. audio(TTS/ASR: retry・Human Review由来の上振れ分)

Human Review Lock機構(既存Production機構、ER-011-HUMAN-REVIEW-
COST-GUARD-01)の`approve_regenerate()`による追加1round(標準+fallback、
既存の合計上限3回budget内、新規Gate・閾値は追加していない)。

| 費目 | 金額(¥、Batch単価で訂正後) | 備考 |
|---|---|---|
| A2 `comment_2`+`meaning_4`追加take | 2.01 | gemini_batch¥1.75+openai¥0.10+openai_asr¥0.17 |
| B1B `full_story_part1`+`full_story_part2`追加take | 13.99 | gemini_batch¥12.65+openai_asr¥1.34 |
| **retry/Human Review由来 小計** | **16.00** | 音声生成合計¥62.83の約25.5% |

### 2-4. audio合計(訂正後)

46.83 + 16.00 = **¥62.83**(OPEN-144訂正後の実額。公式script報告値
¥12.76は`gemini_batch`¥0計上バグにより過小、差額¥50.07)。

## 3. 1記事一式(A2+B1B)の総コスト(最終値、2026-09-12更新)

A2・B1B両レベルともHuman Review解消(comment_2はOPEN-145配線後の
Validatorでoffline再判定しPASS採用、TTS再生成なし)後にAssembly
(`stage_assemble_a2`/`stage_assemble_b1`)を実行しPASSしたことを反映
した最終値。Assembly自体はexisting narration wavの結合・gain/headroom
処理・SFX付与のみでLLM/TTS/ASR API呼び出しを伴わないため、Assembly
実行による追加費用は**両レベルとも¥0**。

| 区分 | 金額(¥) | 説明 |
|---|---|---|
| **①今回実測(訂正後、実際に使われた実行経路ベース=Batch API)** | **180.55** | text-gen 117.72 + audio(訂正後)62.83。**本Trialは既にBatch APIで実行済み**であり、「同期実行ベース」ではない(下記4節参照)。A2/B1B Assembly実行による追加費用は¥0(4節参照)。 |
| ②今回実測(未訂正、公式script報告値) | 130.48 | text-gen 117.72 + audio(バグ影響)12.76。OPEN-144未修正のまま参照すると過小。 |
| ③量産想定(Batch適用時の1記事見込み) | 180.55 | ①と同値。本Trialが既にBatch APIの既定経路で実行されているため、追加のBatch化余地は無い(TTS側は既にBatch)。 |
| ④retry/Human Review由来の上振れ分(内数) | 16.00 | ①のaudio 62.83のうち16.00(25.5%)がHuman Review Lock追加takeによる上振れ。通常運用分は46.83。OPEN-145配線後のcomment_2/meaning_4 resync・A2 Assembly(`OPEN-145-JA-ASR-ORTHOGRAPHIC-VARIANT-PRODUCTION-WIRING-01`)はoffline再判定のみで新規API呼び出しがないため、この上振れ額に追加は生じていない。 |
| ⑤(参考、机上換算・未実行)同一segment数をStandard同期TTSで実行した場合 | 約230.6 | pricing_snapshot.jsonでBatch tierはStandardの50%(input/output とも)と確認済み。audio側訂正額62.83のうちTTS部分(gemini)を2倍換算した理論値(実行はしていない)。 |

**通常コストとTrial/異常対応コストの区分**: ①のうち¥16.00(④)は
Human Review発生に伴う異常対応コストであり、通常の量産1本あたり
コストは¥164.55(180.55-16.00)相当と見るのが妥当。ただし本Trialは
N=1であり、Human Review発生率・retry発生率の量産平均は未確定
(既存`OPEN_ITEMS.md`OPEN-135行参照)。

**真の累計(参考、本表①には含まれず開示のみ)**: 別タスク
`FAMILY-A-DISCOVERY-TOWELS-B1B-SECONDARY-ASR-AND-RETRY-TIMING-
RECONCILE-01`のAzure Secondary ASR診断呼び出し実費用約¥1.81を①(¥180.55)
に加えた**真の累計は約¥182.36**(`OPEN-145-JA-ASR-ORTHOGRAPHIC-VARIANT-
PRODUCTION-WIRING-01_REPORT.md`8節と同一の開示、本REPORTの区分①自体は
記事生成一式[text-gen+audio]のみを対象とする定義のため変更しない)。

## 4. 重要な観測(コード変更なし、報告のみ)

`er006_batch_tts_wiring_01.py`の`DEFAULT_TTS_EXECUTION_MODE`は
`BATCH`であり、呼び出し側が明示的に`TTS_EXECUTION_MODE=STANDARD`を
設定しない限りGemini Batch API経由で実行される。本Trial
(`er011_discovery_generalization_towels_trial_11_audio_run.py`他)は
この環境変数を設定していないことをGrepで確認した(該当箇所0件)。

一方、`OPEN-144`起票時の確認では、Household最終版・News Trial-09は
`gemini_batch`記録0件(標準TTS経路のみ使用)と記録されている。本Trial
がBatch経路になった経緯(呼び出し元の違い/既定値変更の時期等)は本タスク
の範囲では調査していない。

`PM_GOVERNANCE.md` 7-1「正式リリース前は原則Standard同期」との整合が
本Trialで保たれていたかは、本タスクの範囲では判断していない
(**新たな検証課題として報告のみ、コード修正・Trial追加は行っていない**)。
修正要否・調査要否はユーザー判断を仰ぐ(`USER_DECISION_REQUIRED`候補)。

## 5. 取得不可の内訳(理由付き)

1. text-gen側のWriter本文生成/Fact Checker/Support文/Key Phrase選定の
   個別費用: ログの`stage`タグが`writer_a2`/`writer_b1`で一括されており、
   API呼び出し単位ではこれらの機能を区別できない(コード側でstageタグを
   細分化しない限り再集計不可)。
2. Human Review追加takeの内訳のうち「元run(2026-09-10当初3take)」と
   「resume(Human Review追加take)」の按分は、`stage`タグ
   (`tts`/`tts_human_review_resume_02`/`tts_human_review_resume_04`)で
   区別可能だったため取得**できた**(2-3節に反映済み、当初想定していた
   「取得不可」ではなかった)。
3. Assembly/最終音声(player.html)生成後の追加費用: 本REPORT初版作成時点
   では両レベルともAssembly未実行(Human Review承認待ちで意図的に保留)
   だったが、その後B1B(take5個別承認)・A2(OPEN-145配線後のcomment_2/
   meaning_4 resync)とも解消し、両レベルともAssembly実行・PASSした
   (2026-09-12更新、3節参照)。Assembly自体はLLM/TTS/ASR API呼び出しを
   伴わないため追加費用は¥0(取得不可ではなく実測¥0)。
4. 量産時の月次・記事本数あたりコスト予測: N=1のためHuman Review発生率
   の統計的な見込みが立てられず、上記表③は「本Trialと同一retry発生
   パターンだった場合」の見込みに限る(取得不可: 理由=統計的サンプル
   不足)。

## 6. Production採用範囲

本Reportはコスト実測・再集計・報告のみであり、Production Prompt・
コード・費用集計script(`_call_cost_usd()`等)・TTS実行モードの変更は
一切行っていない。`OPEN-144`(gemini_batch ¥0計上バグ)の修正要否・
7-1整合確認の要否はユーザー判断待ちのまま(`OPEN_ITEMS.md`OPEN-144行、
`docs/pm/ACTIVE_TASK.md`UDR-deferred参照)。

## 7. 参照ファイル

- `er011_output/discovery_generalization_towels_trial_11/raw_usage_log.jsonl`
- `er011_output/discovery_generalization_towels_trial_11/cost_summary.json`
- `er011_output/discovery_generalization_towels_trial_11/audit/raw_usage_log_audio_01.jsonl`
- `er011_output/discovery_generalization_towels_trial_11/audit/cost_summary_audio_01.json`
- `er005_output/cost_baseline_01/pricing_snapshot.json`
- `FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-AUDIO-01_REPORT.md`
- `OPEN_ITEMS.md` OPEN-144行
