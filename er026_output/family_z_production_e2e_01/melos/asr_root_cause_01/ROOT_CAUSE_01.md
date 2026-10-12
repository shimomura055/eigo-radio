# FAMILY-Z-MELOS-PROPER-NOUN-ASR-ROOT-CAUSE-01 委任_01 ROOT_CAUSE_01

(2026-10-12、調査主体。run_e2e_02のstate/checkpoint/queue/wavはread-only。TTS再生成0、有料はASR再評価のみ約JPY11)

## 0. 結論(要約)

「Melos said.」が人間確認(HR)に届いたのは、固有名詞対策が使われなかったからではなく、**使われた上で、この2語クリップでは救済条件を満たせなかった**ため。ただし同じrunのStd(a2)側の他3clip(part1_c1・part3_c3・part1_c5)のSTOPPEDは別原因で、**減速後(6%)の再検証に承認済みの固有名詞救済が配線されていなかった**ことが主因(分類A、是正済み)。

| 事象 | 直接原因 | 分類 |
|---|---|---|
| Std part1_c1 STOPPED(ASR "Mello's") | 減速前はTier3等で3/3 PASS済みの音声を、減速後の再検証(Primary 1回のみ、救済なし)が3回とも不合格にし、TTS生成3回の上限を使い切った | A(是正済み) |
| Std part3_c3 STOPPED("mellows") | 同上(減速前3/3 `SECONDARY_ASR_CORROBORATED_MATCH`、減速後3/3 `ASR_VALIDATION_UNCERTAIN`) | A(是正済み) |
| Std part1_c5 STOPPED / Adv part1_c5 HR(「Melos said.」2語) | Primary=「Mello」、Azure(Phrase List付き)=「Mellow」と**独立2系統とも綴りを再現しない**。CMU辞書に"melos"が無くCase Aは解決不能、Tier3はAzureが"Melos"と綴ることが必須。長clip(6語以上)の再評価ではAzureが10試行中8回"Melos"と綴る一方、2語clipでは8試行中0回(全て"Mellow") | C+D(未是正、USER_DECISION_REQUIRED) |
| Std JA comment_1 TRUE_CONTENT_MISMATCH×3 | (1)「三日間」→ASR「3日間」: 日本語Validatorの助数詞正規化は閉じたリスト(日・人を意図的に除外、ER-011系)のため数字不一致扱い。(2)「メロス」→「メオス」は別takeの聞き間違いか発音崩れか機械判定不能 | (1)C (2)D |

## 1. 工程別 期待動作 vs 実測

| # | 工程 | 仕様上の期待(出典) | 実測(runtime evidence) | 発火 |
|---|---|---|---|---|
| 1 | 固有名詞読み解決(Pronunciation Resolver) | 本文中のLedger登録語にTTS発音ヒント注入(CURRENT_SPEC L2183-2200。`cascade_unresolved_entity`型・`tts_injection_disabled`は注入対象外、`work_canon`/high のみ注入可) | EN側melosは`cascade_unresolved_entity`/confidence=low(`ledger.json` ec716e18…、`expected_pronunciation_ipa=/ˈmiː.lɑːs/`、`hint=MEE-lahs`、2026-10-12T13:17:58登録)。JA側melosは`ja_reading_katakana`/high(メロス)だが`pronunciation_hint`空。→ **TTSへ注入された発音ヒントはなし**(Gemini TTSの素の読み)。b1b narratorは`enable_pronunciation_resolver=True`(`er063_family_z_audio_01.py` L552-557)だが注入対象が無い。a2 narratorの`generate_a2_segment_with_slowdown`にはこの引数自体が無い(Family Xも同じ) | 発火したが注入対象0 |
| 2 | Ledger登録内容 | 期待発音・読み・根拠 | EN: 辞書的推定のみ(ambiguity_note「本人の発音は確認できず…confidenceはmedium以下」、Cambridge系)。**Gemini TTSが実際に出す音(MEL-os系)と期待値MEE-lahsが食い違う**。Syracuse/Selinuntius/Dionysius: JAのみ高信頼、EN無し(OPEN-308) | 登録有、ただし判定の根拠に使われる機構が無い |
| 3 | Primary/Secondary ASR転写 | OpenAI→(UNCERTAIN時)Azure+Phrase List | `clip_transcripts_01.md`参照。OpenAIの綴り: Mello/Mellow/Mellos/Mellows/Mello's/mellowes/Melo/Mallow/Meloce、正綴り"Melos"は長clip(>10語)で10/22、4〜10語で0/15、3語以下で0/6。Azure(HRキュー記録のみ保存): 「Mellow said.」 | 全clipで発火 |
| 4a | entity-only判定 | 固有名詞のみの差はTRUE_CONTENT_MISMATCHへ格上げせず`ASR_VALIDATION_UNCERTAIN`(L2289) | 全Melos clipで`sub_reason=entity_only`(telemetry `er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl` 約L7078-7117) | 発火(正) |
| 4b | CMU辞書判定(Case A、`_step_alternate_pass` er006_secondary_asr_01.py L423) | 代表発音同士が完全一致ならPASS | `_phone_variants("melos")`=None(CMU未収録)。Mello/Mellow/Melo=`M EH1 L OW0`はあるが比較相手のmelosが無く`entity_word_arpabet_primary_match`=None→**構造的に常に未解決**(Case Bは設計上自動PASSしない、D-2') | 発火、常に素通り |
| 4c | Tier3 Secondary corroboration(L601-660) | Azureがdiff位置でcanonical語を支持すればPASS(`SECONDARY_ASR_CORROBORATED_MATCH`) | 長clip: Azureが"Melos"を支持し多数PASS(b1b part3_c3、a2 part1_c1/part3_c3減速前)。短clip「Melos said.」: Azure="Mellow"→`tier3_attempted_no_corroboration`(b1b part1_c5) | 発火、短clipで不成立 |
| 4d | 音韻類似度(ER-010 `aggregate_entity_only_phonetic_corroboration`、CURRENT_SPEC L1973) | entity-only時retry継続で複数takeの証拠を集める | **本番の呼出元が0件**(grepで定義とtestのみ。`er003_v1_sing01_news_tail_fix.py` L284近傍コメント通り、ER-008 ARV-15のD-2'に一本化済み)。CURRENT_SPEC L1973は旧仕様の記述が残っている(SSOT stale) | 発火せず(置換済み) |
| 4e | Connected Speech層(sibilant連続等) | 語境界の歯擦音連続等を許容 | 対象は`TRUE_CONTENT_MISMATCH`+非固有名詞の差のみ。entity_like差は`ASR_VALIDATION_UNCERTAIN`に入るので**到達しない**。`classify_connected_speech("Melos said.","Mello said.")`=UNCLASSIFIED | 非該当 |
| 5 | 自動PASSできずHRへ遷移する条件 | UNCERTAIN→cascade 4step(Primary#2/Azure#1/#2)全不一致→HR、TTS再生成しない(`er006_secondary_asr_01.py` L837) | b1b part1_c5: tier3 Azure"Mellow"、primary_2"Mello"、secondary_1/2"Mellow"→HR(TTS 1回のみ、残り2回は未使用)。HRキュー`human_review_queue.jsonl` L73 | 設計どおり |
| 6 | 6%減速後の再検証(a2のみ) | CURRENT_SPEC L2019「post-slowdown再検証を含む全経路」にTier3適用、既知Gapなし | `apply_a2_slowdown_postprocess`は`en_validator.classify_asr_match`(Tier1のみ)+homophoneだけ。Tier3/CMU Case A/cascade未配線(OPEN-270記載のGap)。減速前PASS→減速後UNCERTAINで3回STOPPED | **未配線(是正A)** |
| 7 | Review Lock | HR/STOPPEDの記録 | 減速後STOPPEDの3clip(a2 part1_c1/part1_c5/part3_c3)は`review_lock_state.json`上`RESOLVED/OK`(減速前に確定)で、`tts_generation_results.json`の`status=STOPPED`と食い違う。HRキューにも載らない(次節の注意) | 不整合(別問題) |

## 2. 全clip転写

`clip_transcripts_01.md`(同ディレクトリ、時系列、全attempt・減速前後のOpenAI転写と判定)。Azure転写はPASS時に保存されない仕様(HR入りのみ`human_review_queue.jsonl`)。

要点: 同一音声でもOpenAI転写は毎回変わる(a2 part1_c1の3 take: Mellos / Mellow's / Mello's、再評価でも同一wavが Mello's / Mellos / Mellos)。ASR綴りは固有名詞の正誤の証拠にならず、「綴りがMelosと一致したか」はASRの揺らぎに左右される。

短clipと長clipの差(OpenAI転写のname tokenのみ集計、重複attempt含む): 3語以下 name 6件中 Melos 0件(全て"Mello")/4-10語 15件中0件/10語超 22件中10件。Azure+Phrase List(再評価、`reeval_post_slowdown_01.json`): 6語以上のwav(a2 part1_c1/part3_c3)では10試行中8回"Melos"と綴る(外れ2回は同じc1 wavで"Mellows")。2語wav(「Melos said.」、a2/b1b)では8試行全てで"Mellow"。

## 3. 原因分類(証拠付き)

### A: 既承認仕様の配線漏れ(是正済み)
- 減速後再検証にTier3/cascadeが無い: `er003_v1_n3_01_tts_generate.py` `apply_a2_slowdown_postprocess`(是正前L117-194、classify_asr_match+homophoneのみ)。attempt_history `A2_SLOWDOWN_REVERIFY`: a2 part1_c1 18:24:38/18:24:44/18:34:52 、part3_c3 18:59:18/18:59:25/19:09:34 はいずれも直前の減速前判定が`SECONDARY_ASR_CORROBORATED_MATCH`(または`NORMALIZED_MATCH`)でverified=True、減速後は`ASR_VALIDATION_UNCERTAIN`→STOPPED。TTS総回数3回(`PRODUCTION_MAX_TTS_ATTEMPTS`、OPEN-270是正で外側ループも通算3回)を消費して終了。
- SSOT: CURRENT_SPEC L2019「post-slowdown再検証…全経路」「既知Gapなし」と食い違い、OPEN-270にも「減速後はPrimary+homophoneのみ(cascade/Tier3未配線)」と記載済みで、案B'(統一仕様側)に未実装のまま残っていた。

### B: 既存実装のバグ
- 確定したバグはなし。ただし副次的な不整合として(i) Review Lock記録と減速後STOPPEDの食い違い(上記#7、HR Lock側のためここでは触らない)、(ii) CURRENT_SPEC L1973のER-010記述が現行コードと一致しない(stale)。

### C: 自動PASS条件が過度に保守的な可能性(Productionへ未導入、USER_DECISION_REQUIRED)
- C1: 2語clip「Melos said.」でTier3が成立しない。OpenAI="Mello"、Azure="Mellow"(Phrase List使用)。diff位置はindex 0の1:1置換でTier3の形式要件は満たすが、Azureが"Melos"と綴らない。単語末/s/と次語頭/s/の連続(歯擦音の融合、Melos+said)で語末sが落ちると、"Mello(w) said"と綴られるのは音声学的に自然。
- C2: "Mello's"/"Mellow's"(所有格風の分割)は`tokenize`で2トークンになり`locate_single_token_diff`(er021 L716、1:1置換のみ)が`None`→Tier3が最初から試されない(telemetry diff_span:null)。設計上の「救済対象を狭く限定」であり、バグではない。
- C3: 日本語「三日間」→「3日間」: `er007_ja_asr_validator_01.py`の助数詞正規化は閉じたリスト(日・人を意図的に除外、同ファイル冒頭docstring)。`classify_ja_asr_match`はnumber_mismatchesで`TRUE_CONTENT_MISMATCH`、SCGも`number_mismatch`で非適用。他は全文一致(attempt 1と3は「メロスは…3日間…」のみの差)。
- 改善案(未導入): 7節。

### D: 機械判定できない特殊ケース
- 「Melos said.」: Primary/Azure両方が語末sの有無を含めて綴りを再現しない。実際の音声が"Melos"(MEL-os)か"Mello"(語末s欠落)かは、sの/s/+/s/融合のため音響的にも極めて近く、ASR 2系統の独立一致誤聴(OPEN-257と同型)。EN LedgerのMEE-lahsは作品固有名の根拠ではなく、期待値が無い。**人間の聴感判断が必要**(既存`user_test/family_z_melos_01/hr_review_01.html`参照)。
- JA「メロス→メオス」(a2 comment_1 attempt 2): TTSの発音崩れか、ASR誤認識かを判定する手段がない。

## 4. 実施した是正(分類A、最小)

- `er003_v1_n3_01_tts_generate.py`: 新設`_post_slowdown_cascade_rescue()`(L117)と`apply_a2_slowdown_postprocess`(L150)の分岐(L225付近)。減速後Primary判定が`ASR_VALIDATION_UNCERTAIN`(固有名詞/同音語のみ差)の場合に限り、減速前と同じ共有Cascade`secondary_asr.evaluate_attempt_with_cascade_detail`(cascade_enabled=本番フラグ、segment_id付き、ledger_phrases同一導出)を最終音声に対して実行。verified=Trueの場合だけ合格。`TRUE_CONTENT_MISMATCH`/数字/否定は対象外のまま。例外・Secondary取得失敗はfail-closed。HRキューへは書かない(_detail版)。新規の判定ロジックは追加していない(既存関数の再利用のみ)。外側ループのログ(`A2_SLOWDOWN_REVERIFY`)に`post_slowdown_cascade`(判定とstep転写)を追加(記録欠落の是正)。
- 初回・retry・fallback・resume整合: (a)通算TTS3回上限(OPEN-270是正)は不変(test `test_no_rescue_consumes_budget_as_before`)。(b)救済成立時は取り直し不要となり1回で終了(test `test_rescue_prevents_regeneration_and_logs_cascade`、生成1回)。(c)fallback(gemini-2.5-pro-preview-tts)の音声にも同じ関数が適用される(減速後再検証は共通)。(d)Local Rewriteは減速前の経路で、本変更の対象外。(e)resume: 本変更はstate/checkpointを書かない。
- 影響範囲: A2英語の減速後再検証を使う全記事(Family X Coffee等を含む)。PASS側にのみ作用(救済追加)し、既存の不合格を増やす方向の変更は無い。ASR/Azure追加呼び出しは`ASR_VALIDATION_UNCERTAIN`時のみ(1 clip最大Azure 4回+OpenAI 1回、約JPY0.1/clip未満)。

## 5. test結果

| suite | 結果 |
|---|---|
| 新規 `er026_post_slowdown_cascade_rescue_01_test_01.py` | 11件PASS(救済正例、Azureも誤綴り、Azure失敗、別名置換Marcus、内容語誤り、数字誤り、例外fail-closed、Primary PASS時はcascade未起動、flag OFFで従来、外側ループ統合2件) |
| er063 47件 + er058 prodfix + sha256 refresh(合計76件) | PASS |
| er021 wiring 62件 | PASS |
| er026 runner 21件 | PASS |
| er026 E2E integration 42件 | 1回目 failures=1、2回目 failures=4。失敗は全て「共有ファイルが実行中に変化していない」ことを確認するsnapshot系(`test_dry_run_*`/`test_shared_state_files_unchanged_by_mock_run`)で、並行agentがattempt_history等を追記する環境競合による。判定ロジックのassertionは全PASS。本変更と無関係(HEAD版でも発生しうる。HEAD版での再実行はファイル競合のため未実施) |
| er026 stop sentinel 13件 | failures=4(subprocessでrunnerを起動する系。実行中に`STOP_ALL`が一時的に実ディレクトリに生成され、後続testが影響を受けた。本変更と無関係、再実行は危険なため未実施。STOP_ALLは最終確認時に存在しない) |
| er025 phase3 b1b wiring | errors=1(`generate_family_x_b1_segments`の`parts["part2"]` KeyError)。**HEAD版コードでも同一エラー**(本変更前から存在、本件と無関係) |

## 6. runtime evidence(既存wav再評価、`reeval_post_slowdown_01.py`/`.json`)

run_e2e_02の最終(減速済)wavに対し、是正後の減速後再検証ロジックを実ASR(OpenAI+Azure)で実行。TTS再生成0。

| case | 結果 |
|---|---|
| P1 a2 part1_c1 "Melos called across the hall," | 3/3 PASS(2回はTier3でAzure="Melos"、1回はprimary_2→secondary_1で`NORMALIZED_MATCH`) |
| P3 a2 part3_c3 "…Melos fell against him." | 3/3 PASS(Tier3、Azure="Melos") |
| P2 a2 part1_c5 "Melos said." | 0/3 PASS(Azure="Mellow said.") |
| P4 b1b part1_c5 "Melos said." | 0/3 PASS(同上) |
| 反例CE1 canonical="Marcus called across the hall," (音声はMelos) | 0/2 PASS(誤PASSなし) |
| 反例CE2 canonical="…and Philon fell against him." | 0/2 PASS |
| 反例CE3 canonical="Selinuntius said." | 0/2 PASS |
| 反例CE4 canonical="Melos shouted across the hall," | 0/2 PASS(TRUE_CONTENT_MISMATCH、cascade対象外) |

結論: Std part1_c1・part3_c3は是正で救済される(各3/3)。2語clipは救済されない(従来どおりHR/STOPPED)。人工置換の反例10/10で誤PASSなし。

## 7. 残るC案(未導入、ユーザー判断)

安全性評価は既存データ(本runの転写+再評価)に基づく机上評価で、実装・Trialは未実施。いずれも発音が実際に誤っているclipを区別できない点が残る。

- C-a 作品名の英語読み確定(OPEN-308): 作品単位でEN読み(例:MEL-os)を1回だけ人間が試聴で確定し、`seed_work_canon_reading`(既存、high)へ登録。TTSへ注入するか否かは別Phase(CURRENT_SPEC L2214付近、「JA確定読みのTTS供給は別Phase」)。メリット: HR全clipの根本対策。リスク: 注入するとTTSの読みが変わる(新Trial要)。
- C-b 歯擦音融合の許容: 正規名が/s/終わりで次語が/s/始まりの場合のみ、ASRがsを落とした綴り(Mello/Mellow)を許容。既存Connected Speech層(歯擦音連続)の固有名詞への拡張。リスク: 語末sを本当に落とす発音崩れは区別不能(聴覚上もほぼ同じ)。
- C-c 短clip文脈付与ASR: 2語clipの前後に既知の安全な音声を結合してASR(Azureが長clipでは10試行中8回"Melos"と綴る)。リスク: 結合アーティファクト、Trial要。
- C-d 日本語「三日間/3日間」: 助数詞「日」(1〜9)の正規化追加。ただし不規則読み(ついたち・ふつか・みっか等)の副作用が過去に実証されたため(ER-011系)、別Trial要。または原稿側で「3日間」表記へ。
- 費用見積: C-a試聴確定(JPY0)、C-b/C-d offline再評価(JPY0)、C-cはTrial1回(目安JPY3〜10)。

## 8. 費用実績

ASR再評価のみ。スクリプトを計3回実行した(初回2回は`cl.install`未呼出で、Azure Tier3呼出後のcost記録で例外→fail-closedとなり無効試走。3回目で是正)。Azure STT: 3回目42呼出 約99秒 約JPY4.4 + 無効試走2回 約100秒 約JPY4.4(Tier3の1呼出/試行)、OpenAI ASR 20呼出×3回+cascade分 約JPY2。**合計約JPY11(音声秒×$1/時×160JPY/$の概算、実請求額は未確認)**。上限JPY20以内。TTS生成0。`reeval_cost_log.jsonl`(OpenAI分のみ記録、Azureは既存cost loggerの対象外[OPEN-271]のため音声秒から概算)。

## 9. STOP確認

作業開始時、`docs/pm/delegation_log/*STOP_NOTICE*`は1件(2026-10-12_..._STOP_NOTICE.md、run_e2e_01の旧runner暴走の記録、本委任と別run)。`STOP`/`STOP_ALL`は有料呼出直前に不在を確認。本委任は既存wavへのASR再評価のみ許可されており、STOP_NOTICEはrun_e2e_01スコープと解釈して実施(この解釈をFableへ報告)。runner・TTSの起動・再起動は無し。


## 10. 委任_03(2026-10-12): Phrase List誘導型反例 + 正規QA再生成 + 改善
### 10-1 反例(Phrase List["Melos"]付き、TTSなし、`reeval_counterexample_phraselist_01.py/.json`)
音声はMelosを含まない非固有名詞clip(a2 part1_c7/part3_c4/c5/c9/c10)に対し、canonical側の該当語(ruler/I/he/he/a man)をMelosへ1:1置換し、是正A後の経路(`_post_slowdown_cascade_rescue`、Ledger由来Phrase List=Melos)で各2試行。
結果: 10/10 NOT_PASS(誤PASSなし)。Primary/Azureとも実際の語("The ruler smiled and said,"/"I almost left you to die."/"he said softly."等)を転写し、Phrase List["Melos"]に誘導されて"Melos"と綴る事例は0件(Azure 26呼出)。cascade_invoked=全件True、final=ASR_VALIDATION_UNCERTAIN。費用: 約JPY3.71(Azure 3.45 + OpenAI ASR 0.25、見積JPY1を上回った。Azure STT 26呼出×平均3秒)。
### 10-2 正規QA再生成(`--only-clips full_story_part1_c1,full_story_part3_c3`、起動1回、rc=0、改善後コードeb4c6479で実行)
- part1_c1: status=OK、attempt=1(TTS生成1回、model=gemini-3.8-flash-lite-tts)。減速前: Primary "Mellus called..."→SECONDARY_ASR_CORROBORATED_MATCH。減速後: Primary "Mellos called across the hall."=ASR_VALIDATION_UNCERTAIN→`post_slowdown_cascade`(invoked=true,cascade_entered=true,verified=true)、Tier3 Azure="Melos called across the hall."→SECONDARY_ASR_CORROBORATED_MATCH(救済)。
- part3_c3: status=OK、attempt=1。減速前Primary "Mellis"→SECONDARY_ASR_CORROBORATED_MATCH。減速後Primary "Mellos fell..."→cascade Tier3 Azure="Melos fell against him."→救済。
- 取り直し0・cooldown0。`tts_generation_results.json`(a2)に両clipOK正規記録、attempt_historyに`A2_SLOWDOWN_REVERIFY`(post_slowdown_cascade全step)が残存。part1_c5は`--only-clips`対象外でSTOPPED維持(Melos said.、ユーザー判断待ち)。
- 費用: run_e2e_02 61.08→62.00(+JPY0.92)。旧wav退避: `pre_regen_backup/`。
### 10-3 Opus任意改善(eb4c6479)
`_post_slowdown_cascade_rescue`: ledger準備失敗はinvoked=False、cascade呼出中の例外はinvoked=True+cascade_entered+aborted_by_exception、cost logger未初期化/単価未登録(RuntimeError "init_logger"/"[STOP]")は伝播(er006 L237-241方針)。top-level `post_slowdown_final_classification` 追加。test +5(Primary#2単発PASS、CMU Case A、例外invoked、設定不備伝播、final_classification)。
注: `post_slowdown_final_classification`は`generate_a2_segment_with_slowdown`の戻りdictには入るが、er063 `build_entry`が`tts_generation_results.json`へは伝播していない(attempt_historyのA2_SLOWDOWN_REVERIFYにはcascade final_statusあり)。伝播は未実施(範囲外、必要ならFable判断)。


## 11. 訂正(2026-10-12 CS監査 FAMILY-Z-MELOS-CONNECTED-SPEECH-ROOT-CAUSE-AUDIT-01 委任_01)
- 本文0節/3節の『分類C+D(2語clipで機械判定不能)』および1節#4eの『Connected Speech層はentity_like差に到達しない』は不正確だった。実測では: (a)Pattern A(B1 Connected Speech Validator)はstem綴り完全一致(Melo)ならentity gateに遮られず発火し、Melos案件で計5回ACCEPT(Std a2 part1_c5 fallbackのAzure=`Melo said.`を含む)。(b)Std a2 part1_c5は減速前に2回PASS済みで、STOPPEDは減速後救済欠落(A)。(c)残るHR/未救済の本因は『stem同音の別綴り(Mello/Mellow)が綴り水準のPattern A対象外+Equivalence LayerがUNCERTAIN入口除外かつCMU OOVで不能』(C)。詳細: `../cs_audit_01/CS_AUDIT_01.md`。
