# OFFLINE_C5K_TRIGGER_RATE_01 (ASR-THREE-WAY-COMPARISON-TRIAL-01 委任_02、S2 / Opus R-13 ①′、2026-10-21)

費用JPY0・有料API 0・TTS/ASR再実行なし(保存済みJSONを読んだだけ)。Production・Store・Ledgerは無変更。

## 1. 問い
C5K(KPのみ「Primary PASSでもWhisper転写が内容語で不一致ならAzure必須」)の発動率。= 過去のProduction KPのうち「Primary(OpenAI)転写はPASS済み、かつ吃音QAのlocal Whisper small転写が不一致」の件数/全KP件数。

## 2. 保存の有無(結論: 保存あり。打ち切りなし)
- `er006_output/master_audio_store_01/manifest.json` の各EN KP entry の `qa_evidence.asr_text`(Primary転写)と `qa_evidence.disfluency_evidence.transcript`(local Whisper small、`method=faster_whisper_small_local_verbatim`)。例: 先頭の qa_evidence付きentry `15563db064ed013938298203`(asr_text `Uneven choice.` / transcript `Uneven  Choice.`)。
- 各run `tts_generation_results.json` の `key_phrases.<n>.english.attempts_log[].{asr_text,disfluency_evidence.transcript}`(同型)。
- 注意: Storeの`qa_evidence.asr_text`は採用されたPASS take(Primary PASS)の転写。`asr_judgement`が残るのは40件のみで、他は`asr_verified=true`のみ(Secondary救済 `PASS_WITH_WARNING` の take が混ざる可能性は未区別=未確認)。

## 3. 集計結果(スクリプトは一時作成・実行1回、転写をlower+英数字のみに正規化して比較)
| 母集団 | 全件(分母) | Whisper転写あり | 正規化後不一致(=C5KならAzure必須) | 率 |
|---|---|---|---|---|
| Master Audio Store EN KP(style=`key_phrase_english_component`/`_k2`) | 333 | 333 | **28** | **8.4%** |
| run別 `attempts_log`(283 tts_generation_results.json中、KP attempt 747、両転写あり367、重複除外275) | 275 | 275 | 23(20種の転写対) | 8.4% |

- 突合: 既存`KP_TAKE_PART_INVESTIGATION_01.md §5`「EN 333件中29件(8.7%)」に対し、同一分母333で本集計は28件(8.4%)。差1件の原因は**未確認**(推定: 当時の不一致の1つ=KP4 take part原音声[Whisper `Take  Tarte.`]が、KP4是正[commit 5a92f9c73]でStore上の0714639dが再生成後の音声[現Whisper転写`Take  part.`]に入れ替わったため。確認していない)。attempts_log側の不一致20転写対は全てStore側28件の部分集合(attempts_log限定の不一致なし)。
- 全KPが`asr_verified=true`(Primary転写がPASSして採用された音声)。C5Kの発動条件(Primary PASS かつ Whisper不一致)に該当するのは、このうち不一致の28件。

## 4. 28件の内訳(機械的なテキスト目視分類。音声は聴取していない。どちらが正しいかは未確定)
- 表記・活用・同音の差と読める9件: `Happened to see`/`happen to see`、`Answer four`/`Answer 4`、`Acknowledgment`/`Acknowledgement`、`Anti-satellite use`/`anti -satellite used`、`Put a number to`/`...two`、`Store stock`/`Stores stock`、`Point two`/`0 .2`、`Grogginess`/`groggy -ness`、`Ad revenue`/`Add Revenue`。C5Kでは(Whisper側の正規化規則を作らなければ)Azure必須になるが、Azure許容集合では通る見込みが高い(未実測)。
- 内容語が異なる19件: `Pull at attention`/`a tension`、`Be read`/`Be red`、`Screen a resume`/`Resonade`、`Cytokine release syndrome`/`Central`、`Crisper drawer`/`CRISPR DRR`、`Lowest arousal state`/`steak`、`Retail adoption`/`Aboption`、`stakes`/`steaks`、`A place of one's own`/`one zone`、`Sea blockade`/`C Blockade`(2件)、`Settle at`/`Satellite`、`Raw bean`/`Robbing`、`Raw bean prices`/`Raw Being Prices`、`Character-driven`/`Tariff Driven`、`Bean shortages`/`Being Shortages`、`weaken`/`WEEKEND`、`Greener grass`/`green or grass`、`Blur`/`Blurt`。ここには「Whisper small側の誤り」「実音声の誤発音(Primaryが補正)」が混在し、本集計では区別できない(区別には聴取、またはAzure 1回照会=OPUS R-13 ①″が必要)。

## 5. C5K原価・時間への含意(S1の再計算の根拠)
- 発動率8.4% → 1記事セット(KP10音声)あたりAzure追加呼出の期待値 約0.84回。Azure 1KP呼出は約JPY0.09(RESULT_TABLES H の「KP10音声x約JPY0.09」と同じ前提、`er078_asr_unified_judge_01.py:110-113`のceil秒課金)→ 追加約JPY0.08/記事、追加時間 約0.6秒(Azure KP平均0.72s x 0.84)。
- Whisper small自体は、KPが`disfluency_qa=True`既定(`er003_v1_repro01_main_generate.py:782`)でPrimary verified時に既に走る(`er008_disfluency_qa_18.py:108-117`)ため、追加CPU・追加時間は0(旧記載の「+17 CPU秒」「検査時間+約17秒」は取り下げ)。
- 限界: ①Storeは採用take中心で、Primary NGで棄却されたtakeの網羅ではない(生存バイアス: 発動率は現行Primary通過音声の分布)。②Whisper転写は二重空白・分割の癖があり、空白除去のみの単純比較(本集計)。③不一致=誤発音ではない(上記のとおり約1/3は表記差)。④Azure拒否率そのものは未実測(R-13 ①″の範囲、約JPY30)。
