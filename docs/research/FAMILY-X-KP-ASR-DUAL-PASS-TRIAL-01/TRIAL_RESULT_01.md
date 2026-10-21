# TRIAL_RESULT_01 (FAMILY-X-KP-ASR-DUAL-PASS-TRIAL-01 委任_01、2026-10-21)

実行: `er088_kp_asr_dual_pass_trial_01.py`(1回のみ実行、再試行なし)→ `er088_kp_asr_dual_pass_summarize_01.py`(集計、API 0)。証跡: `er088_output/kp_asr_dual_pass_trial_01/`(setup.json / results.jsonl[回ごと全項目・audit_record全体] / summary.json / table.md / timing.json / raw_usage_log.jsonl)。設計=`TRIAL_DESIGN_01.md`(実行前commit 04c09cf7a、以後変更なし)。TTS新規生成0、既存記事・音声・Master Audio Store・Ledger・review_queue・telemetry・attempt_historyは無変更(実行前後のmtime比較で全9共有ファイルが非更新)。Production code/Prompt/閾値は無変更。

モデル(25節): Primary=gpt-4o-mini-transcribe(Production同一)、Secondary=Azure Speech STT en-US(Production同一)、ローカル=faster-whisper small cpu int8(吃音QA同一、`dq18.transcribe_verbatim`)。Productionと同一にした理由=現行QAの検出能力の実測(最新モデル原則の例外ではなく比較目的)。

## 1. 結果表(ユーザー§7)

| 回 | Primary転写／判定 | Azure転写／判定 | Whisper転写／判定 | 両方PASS方式 |
|---|---|---|---|---|
| 1 | 「Take part.」/ NORMALIZED_MATCH → PASS | 「Take Tart.」/ TRUE_CONTENT_MISMATCH → NG | 「Take  Tarte.」/ TRUE_CONTENT_MISMATCH → NG相当 | NG(NG_BOTH, secondary_not_accepted) |
| 2 | 「Take tart.」/ TRUE_CONTENT_MISMATCH → NG | 「Take Tart.」/ TRUE_CONTENT_MISMATCH → NG | 「Take  Tarte.」→ NG相当 | NG |
| 3 | 「Take tart.」→ NG | 「Take Tart.」→ NG | 「Take  Tarte.」→ NG相当 | NG |
| 4 | 「Take part.」/ NORMALIZED_MATCH → PASS | 「Take Tart.」→ NG | 「Take  Tarte.」→ NG相当 | NG(secondary_not_accepted) |
| 5 | 「Take heart.」/ TRUE_CONTENT_MISMATCH → NG | 「Take Tart.」→ NG | 「Take  Tarte.」→ NG相当 | NG |
| 6 | 「Take tart.」→ NG | 「Take Tart.」→ NG | 「Take  Tarte.」→ NG相当 | NG |
| 7 | 「Take tart.」→ NG | 「Take Tart.」→ NG | 「Take  Tarte.」→ NG相当 | NG |
| 8 | 「Take tart.」→ NG | 「Take Tart.」→ NG | 「Take  Tarte.」→ NG相当 | NG |
| 9 | 「Take part.」/ NORMALIZED_MATCH → PASS | 「Take Tart.」→ NG | 「Take  Tarte.」→ NG相当 | NG(secondary_not_accepted) |
| 10 | 「Take tart.」→ NG | 「Take Tart.」→ NG | 「Take  Tarte.」→ NG相当 | NG |

(全行の判定labelは `table.md` / `results.jsonl`。Whisperは全10回label=TRUE_CONTENT_MISMATCH、CMU同音等価・entity救済なし。)

## 2. 数値(ユーザー§7 1〜4)
1. Primary PASS: **3/10**(回1,4,9。すべてNORMALIZED_MATCH=大小文字・句読点除去後token一致。同音等価・編集距離許容は不関与)。NG 7/10(「Take tart.」6回・「Take heart.」1回)。
2. Secondary(Azure) PASS: **0/10**(10回とも「Take Tart.」、TRUE_CONTENT_MISMATCH)。
3. Primary+Secondary両方PASS: **0/10**(Production判定関数 `force_secondary=True` の`verified`と、定義`primary.passed AND secondary.accepted`は10/10一致)。
4. 本音声を両方PASS方式でNGとして検出: **10/10回**。うち「Primary PASSをSecondaryが覆した」=3回(回1,4,9)、「Primary自身がNG」=7回。
参考(総合判定に不含): ローカルWhisper PASS相当 0/10(10回とも「Take  Tarte.」)。

## 3. 認識の安定性(②)
- Primary転写: 「Take part.」3 / 「Take tart.」6 / 「Take heart.」1 = **3種に変動**(同一wav・同一prompt・同一設定で10回)。単回Primary判定ではPASS確率が約30%相当(本音声n=1・10回の観測。一般化は不可)。当初Production採用時の1回目(Take part.)はこの3/10のPASS側を引いた例と整合する。
- Azure: 10/10「Take Tart.」(**変動なし**)。
- Whisper: 10/10「Take  Tarte.」(**完全同一**。seed指定なし・CPU int8・条件同一の決定論的動作。語確率は`Take` 0.83/`Tarte.` 0.58[回1]。10回でも新しい情報は増えない旨の事実記録)。

## 4. 誤PASS可能性(③、断定しない)
- 本Trialの事実: 発音の絶対的な正解(試聴によるground truth)は未取得。3種のASRのうち、Azure・Whisperは一貫して「tart/Tarte」側、Primaryは「part」側と「tart」側・「heart」側に割れた。ユーザー聴感「take tart」は、Azure 10/10・Whisper 10/10・Primary 6/10(+heart 1)と矛盾しない。
- 両方PASSは発音の正しさの証明ではない。「同じ発音不良を両ASRが見逃す」型は、本音声では起きなかった(Secondaryが検出した)が、これは1音声の観測で、見逃し率は推定できない。Primary・Secondary双方が高頻度連語priorで「part」へ補正する語(例: 文脈補正が強い連語)での同時見逃しは**未検証**。
- 逆に過剰NG(正しい音声をSecondaryがNGにする)リスクは**本Trialでは測定していない**(正しい音声を使っていない)。

## 5. Phrase List / Cache / 独立実行の証拠
- Azure Phrase List: Production同一呼出 `get_hint_for_text("take part", min_confidence="low")` = `[]`(空)。`phrase_list_size=0`。`PhraseListGrammar`未作成・`setWeight`**未実行**(重み2.0定数は存在するがPL空では送信されない=既存Production設定どおり)。setup.json参照。
- Primary独立実行: 10回ともAPIを実呼出。`openai_calls_in_thread=1`/回、OpenAI `_request_id` 10種ユニーク(req_d6a299af…, req_8782b805…, req_cf6b1756…, req_a9f21c44…, req_105c9319…, req_e1c82ba2…, req_8424a24e…, req_1d85229e…, req_2763dbf8…, req_65f07d39…、全文はresults.jsonl)、usage tokens/回(input 57, output 5)、経過0.44〜1.48秒、UTC timestamp各回。キャッシュ機構は無い(`er006_asr_provider_routing_01.py:93-103`)。
- Secondary独立実行: 各回`azure_real_calls=1`(合計10)、`secondary_cached=false`、`cache hits=0`(SecondaryCacheはcall単位で新規。`calls=2`は judge→`_AzureShared.outcome`のネスト参照でありreal call数ではない)、各回の経過ms(1138/1138/1638/534/541/533/548/543/539/538)。`begin_secondary_run()`未使用(`_RUN_CACHE is None`をassert)。
- 記録上の注意: Trial専用`raw_usage_log.jsonl`のAzure行は9件(OpenAI 10件)。3並列で`cl.record`(排他なしのfile append)が同時刻の1件を取りこぼしたと推定(各回auditは`azure_real_calls=1`・固有のsecondary_msと転写を保持。回1,2のsecondary_ms=1138が同時刻起動で、ログのelapsed 1.003は1件のみ)。費用は保守側にaudit(10回)基準で算出した。ログ件数ずれ自体はProductionへの影響ではなく、並列実行時のTrial計測上の事実としてのみ記録。
- 共有ログ非書込: 実行前後で `ledger.json / master manifest / reuse_telemetry / attempt_history / 両human_review_queue / en_asr_semantic_equivalence telemetry / pronunciation core telemetry / er005 raw_usage_log` の全9件がmtime非更新。

## 6. 費用・速度(④)
- 実費(出典: pricing_snapshot.json[OpenAI $1.25/M in・$5.0/M out、Azure S0/S1 $1.0/音声h]、JPY=160/USD[er078_asr_unified_judge_01.py:80]):
  - Primary 10回: input 570 / output 50 tokens → **JPY0.154**(0.0154/回)。
  - Azure 10回: Production式 ceil(1.3→2秒)×$1/3600×160 = JPY0.0889/回 → **JPY0.889**(正確秒数1.3秒式なら0.0578/回、0.578)。
  - ローカルWhisper: JPY0。
  - **合計 JPY1.04(Production式)/ JPY0.73(Azure正確秒数式)**。T-3 Guardrail JPY30の約3.5%、見積(JPY1〜3)の範囲内。
- 壁時計: API段(Primary+Azure、3並列10セット)7.06秒、Whisper直列10回 21.1秒(初回3.7秒=モデルロード、以降約1.9秒/回)、全体28.2秒。1セット内Azureは0.53〜1.64秒。
- 量産見込み(Key Phrase 5件×Standard/Advanced=10音声/記事セットにSecondaryを毎回追加した場合): 追加Azure費用 **≒JPY0.89/記事セット**(Production式、0.0889×10)〜0.58(正確秒数)。70円/記事セット目標比で約+0.8〜1.3%(ceil式)。ただし既にPrimary NGの音声ではSecondaryが現行でも呼ばれる(`unified_judge`)ため、純増はPrimary PASS音声分のみ(最大10件)。追加時間: 1音声あたり約0.5秒(典型)〜1.6秒、10音声直列で約5〜16秒(音声生成の直列区間に重なる分は追加なし。3並列なら1/3程度)。
- NG増加に伴うTTS再生成・Human Reviewのリスク(定性・断定しない): 両方PASSを必須にすると、Primary PASSでもSecondaryがNGなら現行のKP 4回構成(Minimal 2+English Lock 2)の再生成枠へ入るため、NGが増えた分だけTTS(Gemini)再生成費用と時間が増え、4回尽きた場合は最終slotのNGがHR queueに入る。増加率は本Trial(1音声)からは推定できない。参考値として、過去調査(KP_TAKE_PART_INVESTIGATION_01.md §5)がStore内EN 333件中29件(8.7%)で「ASR間不一致が出ているのに通る」件数を報告しており、これが上限の目安になりうるが、本Trialでは検証していない。また、Azureが誤ってNGにする過剰NG率も未測定。

## 7. 未検証事項(Production採用に向けて)
1. 正しい発音のKey Phrase(Primary・Azureとも一致する既存音声)での過剰NG率(false reject)。複数KP・複数語長・固有名詞/Phrase List有無。
2. 両ASRが同時に補正して見逃す誤発音の頻度(ground truthはユーザー聴感または音声学的確認が必要。本音声の聴感確定は未了)。
3. 他KP音声に対するPrimary転写の変動幅(本音声は3種に変動。他音声での分布)。
4. NG増加時の実TTS再生成回数・HR到達率・費用(量産シミュレーションなし)。
5. Phrase Listが非空になるKP(固有名詞等)でのsetWeight 2.0動作との相互作用(本音声は空PL)。
6. Azure短音声(1.3秒)での`ceil`課金試算と実請求の差(S0契約tier未確認、既存の注記どおり)。

## 8. Sonnet所見(判断材料。Status付与はFable)
- 事実: 本音声では、Primary+Secondary両方PASS方式は10/10でNGを検出。内訳はPrimary単独でも7/10がNGで、Primary PASSの3回はいずれもSecondary(Azure)が「Tart」として覆した。Primary単独の判定はprior補正により不安定で、Secondaryは10/10安定。
- 費用は量産で記事セットあたり約JPY0.6〜0.9の追加(70円目標に対し小さい)。主な不確実性は過剰NG率とNG増加による再生成・HR増加で、本Trialでは未測定。
- 判断候補(Sonnetは分類のみ): 「Key Phrase英語のProduction採用化(Primary+Secondary両方PASS)」へ進める前の追加検証(過剰NG率の既存KP音声を使った計測等)は、費用・新仕様に関わる別判断(分類D候補)。本Trial範囲では実施しない。
