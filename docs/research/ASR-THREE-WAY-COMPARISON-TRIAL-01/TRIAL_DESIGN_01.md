# TRIAL_DESIGN_01 (ASR-THREE-WAY-COMPARISON-TRIAL-01 委任_01、2026-10-21、有料ASR実行前に確定)

性質: Trial(Trial専用評価実装)。Production(ASR Primary/Secondary・Validator・救済機構・Cascade・Phrase List重み・Prompt・routing)は一切変更しない。Production関数は**呼び出す**のみ。到達上限=VALIDATED/REJECTED/USER_DECISION_REQUIREDの材料(最終ラベルはFable)。
使用モデル(25節): 3方式はProduction同一=比較目的の例外 — OpenAI `gpt-4o-mini-transcribe`(Primary、`er006_asr_provider_routing_01.py:31`)、Azure Speech STT en-US(SDK 1.50.0、`er006_secondary_asr_01.py:78`)、faster-whisper `small` cpu int8(`er008_disfluency_qa_18.py:50-60`)。Whisper別サイズは「smallの誤りがモデル容量由来と実測で示された場合のみ1サイズ追加」(本設計では未実行、結果次第)。新規TTSはGemini `gemini-3.8-flash-lite-tts`(Production同一)。LLM採点は使わない(機械的な正規化比較とProduction判定関数のみ)。

## 1. 目的と範囲
ユーザー原文(`docs/pm/delegation_log/2026-10-21_KP4-REMEDIATION-AND-ASR-THREE-WAY-TRIAL_USER.md`、sha256 b5a7cab9…822fd)Task B。品質(Q)>速度(D)>量産単価(C)の順で、3方式のASR単体性能(Phase 1)・Production運用条件(Phase 2)・Validator込み最終品質(Phase 3)を、正解ラベル付き音声で比較し、構成候補ごとの誤PASS/過剰NG/速度/原価を出す。Task A(KP4是正)とは独立。

## 2. 評価データ(S1、`dataset_manifest.jsonl`、詳細は`DATASET_01.md`)
**正常(normal)ラベルの根拠(優先順)**:
1. 人間試聴済み記事: ユーザー試聴PASS済みの Boredom-Aggression(X、OPEN-408、2026-10-17、Std/Adv)・Yemen-Saudi run_mey_02(X、OPEN-416、2026-10-21、Std/Adv)・Melos run_e2e_06(Z、OPEN-422、2026-10-21、Std/Adv)。KP 30本(各記事Std5+Adv5)+本文24セグメント。**注意: 記事全体の試聴PASSであり、KP/セグメント単位の個別聴取記録ではない**(記事B KP4 "take part" がStore経由でASR PASSしたまま試聴前に見つかった事例のとおり、個別見逃しはありうる)。Store再利用により同一wavが複数記事に出る場合は`duplicate_of`で重複除外。
2. Human Review承認済みsegment(`human_approved_segments.json`): ASRがUNCERTAIN/不一致でも人間が正読と確認した難例(Melos drank・Melos said・Troy Meink・Toteme/Kallmeyer・Oimo no Cane・pool_n9 KP "default")。承認時wavと現存wavの同一性は未照合(承認hashはcanonical_text hash)なので注記付き。
3. 構成ラベルの正常(plw): 過去Trial(FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01)の"Melos"を読ませたTTS音声(人間試聴ではない)。
**問題(problem)ラベルの根拠**:
1. 人間聴感: 記事B KP4 "take part"(ユーザー聴感「take tartに聞こえる」、`…KP-TAKE-PART_USER.md:16`、旧wav sha 675cd6b1…)=1本。
2. 構成ラベル(**人間試聴ではない**): (a)新規TTS 8本(上限内): canonicalと異なる文面を読ませた(take tart/weekend/turn off/make reward smaller/fur bank/thirteen days/will not return/Milos)。TTSがcanonicalへ自動補正した場合ラベルが成立しないため、3方式の転写が全てcanonical一致の音声は「構成ラベル疑義(要人間試聴)」と表示し、除外あり/なし両方で集計。(b)splice 5本: 正常wavから語を物理的に削除/重複(almost・not・in・late削除、sword重複)。語の消失は構成上確実(切断位置にだけWhisper word timestampを使用)。(c)過去Trial plwの"Mello/Melon/Mullos"minimal pair 9本。
3. ラベルを付けられない候補(Store EN 333件中の29件のASR間不一致、`KP_TAKE_PART_INVESTIGATION_01.md` §5): 今回は聴取者がいないため正誤を確定できず**混同行列に含めない**(必要なら別途ユーザー試聴)。

**ASR結果そのものは正解ラベルにしない**。偏りの開示: 問題音声は人工(構成)が大半で、実運用で現れる誤発音の分布を代表しない。正常は完成記事由来で難例は少なめ(HR承認難例6本で補強)。KP問題は目標8〜15に対し実数は少ない(新規TTS上限8本のため)。X/Z・Std/Adv、Phrase List有/無(Melos等のLedger hint有のものと、KP全般=空)を含む。

## 3. 方式と条件
**Phase 1(ASR単体・中立条件)**: OpenAI(prompt無し)・Azure(Phrase List無し)・Whisper small を全音声に1回。出力: 転写・正規化WER/CER(正解=canonical)・内容語差分・固有名詞/数字の扱い・処理時間・Whisper CPU時間。**安定性**: 短尺KP 20本(正常+問題KPを含む)×追加2回(計3回)×3方式(Production条件)。独立音声での検証(多数音声)と同一音声反復(安定性)を区別して報告。
**Phase 2(Production運用条件)**: OpenAI=KPはProduction promptあり(`KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT`、`er003_v1_repro01_main_generate.py:771`)・本文は無し(Productionも`asr_prompt=None`)。Azure=Ledger hint(`get_hint_for_text(min_confidence="low")`)があれば Phrase List 重み2.0(`er006_secondary_asr_01.py:75,106-111`)、空ならPL未作成。Whisper=現行条件(Phase 1と同一なので追加呼出なし)。追加の有料呼出は「条件が実際に異なる音声」のみ(KP全て→OpenAI prompt付き、Ledger hint有の本文→Azure PL付き)。PL有/PL空は分けて集計(Azureモデル自体の性能とPL供給品質を混同しない)。
**Phase 3(Validator込み)**: Phase 1/2で得た転写をキャッシュとして、**Production判定関数`er006_secondary_asr_01.evaluate_attempt_with_cascade_detail`を呼ぶ**。構成ごとに「Primary転写=どの方式の転写か」「Secondary転写の供給元」だけを差し替える(Secondary取得関数`get_full_text_via_azure_stt_with_phrase_list`の呼出を、Trialプロセス内でキャッシュ転写返却へ差替え。ファイル改変なし、API呼出なし)。構成: C1 現行(OpenAI→Azure、Primary PASSならSecondary不要)/C1d 現行+force_secondary(両方PASS必須; FAMILY-X-KP-ASR-DUAL-PASS-TRIAL-01の案)/C2 Azure→OpenAI/C3 Whisper→OpenAI/C4 Whisper→Azure/C5 現行+Whisper不一致時のみSecondary必須(KP_TAKE_PART_INVESTIGATION案A)/C6 3方式多数決(Trial専用の単純評価、Production判定関数は使わない・参考)。**入替構成でProduction規則がそのまま使えない点**(Primaryの言語prior前提のCMU同音救済・Tier1/baseline、Secondary`accepted`集合の定義、`low_ratio`閾値0.98、entity救済、M1のUNCERTAIN限定)は結果に構成別に列挙し、入替構成の数値は「現行ルールを流用した場合の参考値」と明記する(新ルール設計・Production採用提案ではない)。
**Delivery**: 音声ごとの処理時間(API/ Whisper)、1記事セット換算、Whisperの直列/2・4プロセス同時実行(別process、同一24音声)とCPU時間(`time.process_time`)。**Cost**: OpenAI=トークン実測×$1.25/$5.0 per M(`er005_output/cost_baseline_01/pricing_snapshot.json`)、Azure=ceil秒×$1/h(`er078_asr_unified_judge_01.py:110-113`)、JPY=160/USD(同:80)、TTS再生成費用期待値は過剰NG率×KP/セグメント単価(既存実績値を出典付きで使用)。

## 4. 費用見積(Guardrail JPY250、7-7。日次1,000円はS0実測 adopted 350.42(max(log,ledger))+並行2件の見込みを考慮)
- 新規TTS 8本(Gemini batch): 実績値からの推定 JPY約1〜3(2〜4秒音声x8)。
- Phase 1/2 API(`run.py api --dry`): 約170 call、見積 JPY約31(OpenAI約0.0154/回、Azureは音声秒×$1/h[全音声合計約500秒])。plw 15本(約45秒)追加でさらに約+2。
- 安定性追加: 20本×2回×(OpenAI+Azure)≒JPY約4。
- Phase 3: 転写キャッシュ流用、追加API 0。
- **合計見込み JPY約40(最大でも約60)**、Guardrail 250の約16〜24%。自動停止閾値は実行中200円(`GUARDRAIL_STOP_JPY`)。超過見込みならSTOP。
- 日次: 本日の既存使用+上記約40で1,000円に対し余裕あり(実行前後に`daily_dev_cost_01.py`を再計測)。

## 5. 実行ルール
- 有料runは各コマンド1回。resumable(既存keyは再実行しない)。外部停止/rc≠0が原因不明で2回続いたら再起動せずSTOP。監督ループ・別名ラッパ無し。stop_scope_checkをS0(rc=0)・TTS前・API前に実行。
- 共有ログ・HR queue・Master Store・記事成果物・Ledgerには書かない(Trial dir=`er091_output/asr_three_way_trial_01/`のみ)。cost loggerはTrial dirへ。
- 不整合な出力を期待値としてassertするtestは書かない(本Trialは評価であり、Production testは追加しない)。
- 結果は正解ラベル件数が少ない種類は「n=…」を併記し、割合のみの結論にしない。同一音声の反復で独立性を水増ししない。
