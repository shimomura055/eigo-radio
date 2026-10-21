# Std Key Phrase「take part」発音指摘 原因調査(FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01 委任_05、2026-10-21)

調査のみ。API/TTS/ASR(有料・新規)呼出0、SSOT・原稿・Prompt・音声・QA仕様は未変更。ローカル解析(波形/スペクトル、既存JSON読取)のみ。**発音の良否は未試聴=断定しない**(客観指標のみ)。

## 1. 報告表(ユーザー§5)

| 項目 | 結果 |
|---|---|
| 正しい台本 | take part |
| Primary ASR転写 | gpt-4o-mini-transcribe: 「Take part.」(`a2/audit/tts_generation_results.json` key_phrases.4.english.attempts_log[0].asr_text / cascade_steps[0])。台本との差分なし(大小文字・句読点のみ) |
| Primary判定 | PASS(`reason_code=primary_pass`、label=NORMALIZED_MATCH=大小文字・句読点除去後にtoken列一致。同音等価・編集距離許容は不関与、`equivalence_basis=null`、`warning_labels=[]`) |
| Secondary ASR使用 | NO(`secondary.called=false`、azure_calls=0)。理由=承認済み基本フロー「Primary PASSならSecondary不要」(CURRENT_SPEC.md:2808)。force_secondaryはfallback音声限定(CURRENT_SPEC.md:2055)で今回はK2 primary・fallback_used=False |
| Secondary転写・判定 | なし(未呼出) |
| TTS再生成 | NO・0回(call_count=1、retry_count=0、attempts_log 1件、Store `no_existing_master`で今回新規生成) |
| Fallback／Local Rewrite | なし(fallback_used=False、Local RewriteはEN 5 role対象外でKP非該当) |
| 最終採用Take | attempt1(`kp4_en.wav`、sha256 675cd6b1…2186、Store master_audio_id 0714639d351b47c34b4d4103、key A=k2 primary)。**別の独立検査(ローカルfaster-whisper small、disfluency QA)は同一wavを「Take  Tarte.」と転写**したが、判定に使われない |
| 最終音声の発音評価 | 未試聴(断定不可)。客観指標: 第2語頭の破裂音が旧Take(同句、両ASRとも"part")より強い広帯域・高域burst(0.58-0.60s、重心5.2-6.1kHz、>3kHz energy 88-90%、rms 0.045)で、旧Takeは弱いburst(rms 0.0004〜)。/t/様の可能性と整合するが、母音遷移(F2)等は未計測=確定ではない。ユーザー聴感「tart」と矛盾しない |
| 見逃しの原因 | (確認済み)QAが検出手段を1つしか実質使っていない: 判定はgpt-4o-mini-transcribe単独の転写「Take part.」のみ。同一wavにローカルwhisperが「Tarte」と出していた不一致は、disfluency QAが「隣接同一語の繰返しのみ」を見る設計(`er008_disfluency_qa_18.py:83-93,96-107`)のため判定に不関与。(推定・最有力)TTSの実誤発音をgpt-4o-mini-transcribeが高頻度連語prior("take part")で補正(文脈補正)。区別には試聴が必要 |
| 再発リスク・対策要否 | 再発リスクあり(Key Phrase短句全般。同種の「ASR間不一致が出ているのに通る」件はStore内EN 333件中29件=8.7%、後述)。対策要否はユーザー判断(§6)。Master Audio Store(id 0714639d…)に同音声が保存済みで、K2 key A再利用時は**再検証なしで他記事へ伝播**する |

## 2. S1-S4: 該当KP・経路・ASR全記録・公開音声との同一性

- 該当KP: Std(a2)Key Phrase 4=「take part」/ meaning=「参加する」(index.html「Key Phrase 4」75.3秒〜(7.0秒)= `std_12.mp3`)。同run KP1-5の「Primary転写 / ローカルwhisper転写」: think up(ThinkUp. / Think up.)、can't wait(同)、fan stories(同)、**take part(Take part. / Take  Tarte.)**、story maker(StoryMaker/StoryMaker)。KP4のみ不一致。
- 生成: 今回新規生成(`reused=false`、`cache_miss_reason=no_existing_master`)。他記事音声のreuseではない。Std KPの英語は1回のみ再生(Std構成=英語+日本語meaning。phrase_repeatはAdvのみ。runner L2090-2094)。Store key A(`key_phrase_english_component_k2`、`v2_margin030+k2.9d905cfe6c04`)、Aoede、gemini-3.8-flash-lite-tts。ASR promptは「逐語・英語綴り・翻訳禁止」で**canonical句を含まない**(`er003_v1_repro01_main_generate.py:771-775`)=prompt経由の誘導ではない。
- 旧Takeとの比較: 2026-10-15にStore登録の同句(key `key_phrase_english_component`旧style、id b62276d0…、E7_x_b1b生成)は両ASRとも"part"。K2導入でkeyが変わり再生成→今回のTake。
- 公開音声との同一性: 検査対象wavと採用wavはsha256完全一致(`kp4_en.wav`=`attempts/kp4_en_attempt1_custom60ebc452.wav`、Store audio同sha)。assembled wav内で正規化相互相関=1.0000(0.99999998)、公開`std_12.mp3`(48kHz mp3)内で相関0.9987=検査対象音声が公開音声にそのまま含まれる(差し替え・別音声なし)。

## 3. S5: コード上の判定(file:行)

- Primary判定: `er003_v1_repro01_main_generate.py:348-372`で転写→`evaluate_attempt_with_cascade`。`er006_preprod_hardening_01_validation.py:1000-1011`: 完全一致でなく、`tokenize`後のtoken列一致で`NORMALIZED_MATCH`(case/句読点)。「part/tart」を対象にした規則は存在せず、Primaryが「part」と書いた時点で規則は発動しない(同音等価・Connected Speech・CMU・Phrase Listは不関与)。
- Secondary: Primary PASSなら呼ばない(CURRENT_SPEC.md:2808、`secondary.called=false`)。force_secondaryは`er003_v1_crosslevel_audio_02_common.py:374-381`(fallback音声のみ)で、KP primary経路(`generate_key_phrase_component_verified`、`er019_family_x_kp_en_k2_store_01.py`)からは渡されない(grep確認: `er003_v1_repro01_main_generate.py`に`force_secondary`なし)。
- Azure Phrase List: Secondary未呼出のため不関与(`AZURE_PHRASE_LIST_WEIGHT=2.0`は`er006_secondary_asr_01.py:75`、Secondary呼出時のみ)。Connected Speech Equivalence LayerはA2/B1本文segment限定でKP非適用(CURRENT_SPEC.md:2151)。
- 追加ゲート: disfluency QA(ローカルfaster-whisper)は呼ばれたが`flagged`判定は隣接同一token繰返しのみ(`er008_disfluency_qa_18.py:83-93`)。転写内容(Tarte)は記録されるだけ(`transcript`)で判定に使われない。repetition QAはKP非適用(`repetition_qa_checked=false`)。
- 発動条件の抜け: 「Primary PASS」×「別の独立ASRが不一致」を拾う経路が存在しない(設計通りの挙動=承認済み仕様が正しく発動した結果。仕様違反の不具合ではなく、仕様上の検出能力の限界)。

## 4. S6: 仮説別の支持/不支持

| 仮説 | 判定 | 根拠 |
|---|---|---|
| 実際のTTSが「tart」様に誤発音 | **支持(有力・未試聴)** | 独立ローカルASRが同wavをTarteと転写。第2語頭burstが強い広帯域(上記)。旧Takeは"part"。ただしlocal whisper-smallは短句でしばしば誤る(下記8.7%の例: Crisper→CRISPR DRR等)ため単独では決定不可 |
| ASRが文脈補正で「part」と誤認識 | **支持(推定・同上と表裏)** | 台本由来promptなし。gpt-4o-mini-transcribeは言語priorで補正しうる(同モデルは過去にも「Uneven choice」平滑化事故あり、`er008_disfluency_qa_18.py`冒頭)。確定は試聴が必要 |
| 同音等価・許容規則で誤PASS | **不支持** | Primary転写自体が「Take part.」で台本と一致。`equivalence_basis=null`、NORMALIZED_MATCHは大小文字・句読点のみ |
| ASR不一致を無視/Primary・Secondary・再生成の発動条件の抜け | **一部支持** | Primary PASS時にSecondary非発動は承認済み設計。disfluency側の別ASR不一致を判定に使わない設計が検出漏れの直接要因 |
| 検査対象音声と公開音声の差異 | **不支持** | sha一致・相関1.0・mp3内確認 |
| KP固有QA経路の漏れ(Full Story等との差) | **支持(構造)** | KPは短句(2語)で、Primary単独PASS+repetition限定disfluencyのみ。Full StoryはConnected Speech Layer・repetition QA・文脈長でASR補正が効きにくい。reuse時は保存済みQAを信用し再検証なし(`er019_family_x_kp_en_k2_store_01.py`設計) |

## 5. S7: failure mode一般化と既存対策との関係

- 型: 「1音素差の実在語対(part/tart、weaken/weekend、Blur/Blurt、Raw bean/Robbing等)で、LLM型ASR(gpt-4o-mini-transcribe)が高頻度連語priorで補正しPrimary単独PASS」。語頭・語中の破裂音(p/t/k)、短句(2語)、句の語彙が一般的なほど起きやすい。
- 既存対策との関係: 表記揺れ(case/ハイフン/英米綴り/despace)・Connected Speech・Phrase List・CMU・EN semantic equivalenceはいずれも「ASR出力が台本とずれた時に救済(PASS側へ寄せる)」ためのもので、「ASRが台本どおりに書いたが実音声は違う」型を検出しない。検出系は(a)Primary一致、(b)ローカルdisfluency(繰返しのみ)。
- 事実の裏付け(Store `er006_output/master_audio_store_01/manifest.json` EN 333件、qa_evidenceのasr_text vs ローカルwhisper転写、正規化後不一致): 29件(8.7%)。内訳は表記差(Acknowledgment/Acknowledgement等)、whisper-small側の誤り(CRISPR DRR、Satellite等)、実音声の疑い(weaken→WEEKEND、Character-driven→Tariff Driven、Raw bean→Robbing、take part→Tarte等)が混在。**不一致=NGではない(偽陽性が多い)**=全件を再生成すると過剰再生成になる。
- 今回の件で同一run内の他KPは不一致なし(1/5のみ)。

## 6. S8: 改善方針案(提案のみ・実装禁止・QCD影響)

1. 立場: 新仕様のため`判断候補`(ユーザー承認前に実装・Trialしない)。
2. 案A(推奨候補): KP英語のみ、「Primary PASSかつローカルwhisper転写がcanonicalとtoken不一致(正規化後、約8.7%)」の場合に限り、既存Secondary(Azure、Phrase List付き)を1回確認に追加。Azure短句1回≒0.09円(`er078_asr_unified_judge_01.py:79-80,110-113`の式、2秒分=2×$1/3600×160)→1記事5KPで≒0.4回=実質ほぼ追加費用0、再生成・HRは増やさない(Secondaryも不一致の場合のみ既存再生成枠[合計4回]へ)。Azureが"Take part"と一致しても誤PASSが残る余地はあるため「検出率向上の上限」は要Trial。
3. 案B: ローカル不一致を即NG(再生成)=過剰再生成(偽陽性高)でC悪化、非推奨。
4. 案C: Store reuse時の再確認(ローカル不一致記録のあるentryのみ)。伝播防止。追加費用小。
5. 案D: 現状維持(1件/5KP/記事相当の個別指摘として扱い、Human試聴で拾う)。QCD変化なし・再発は残る。
6. 今回の成果物の扱い(判断候補): 完成音声の差し替え/該当KPのみ再生成(1回分のTTS+検証で数円)は、ユーザー判断(委任文で禁止のため実施せず)。同entry(0714639d…)をStoreに残すと将来記事へ伝播するため、差し替え時はStore無効化も同時検討。

## 7. 証跡・再現

- JSON: `er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01/a2/audit/tts_generation_results.json`(key_phrases.4)、`er006_output/master_audio_store_01/manifest.json`(0714639d…、b62276d0…)、`reuse_telemetry.jsonl:2020`(generated、2026-10-21T13:15:12)。
- スペクトログラム: `docs/research/FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01/kp_take_part_spectrogram_01.png`(上=今回K2 Take、下=旧Take。判断はしない)。
- 未実施(委任文のAPI 0制約): 試聴、ローカルfaster-whisperの再実行/他ASRでの再転写、Azure Secondary照会。
