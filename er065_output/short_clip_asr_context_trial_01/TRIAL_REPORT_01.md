# TRIAL_REPORT_01: FAMILY-Z-SHORT-CLIP-ASR-CONTEXT-GENERALIZATION-TRIAL-01 委任_01

日付 2026-10-13 / Status(委任_02で訂正): **C-c(ASR時のみ文脈結合)のauto-accept化: REJECTED(Trial実測) / 推奨(2)(4)+音響証拠: 未実装・未検証、USER_DECISION_REQUIRED / 計測: Trial完了**(「VALIDATED」は使わない。旧表記を廃止) / Production無変更・TTS生成0・Production state書込0
委任_02(2026-10-13、Opus独立レビュー必須修正反映): 記述訂正と既存`results_01.jsonl`からの再集計のみ(費用JPY0、API呼出・TTS・ASR無し)。訂正箇所は本文中に「[委任_02訂正]」で明記。再集計表は付録の C-2b/C-2c/C-2d/D-4b。
出力dir: `er065_output/short_clip_asr_context_trial_01/`(er065は空き番号だったため使用)
コード: `er065_short_clip_asr_context_trial_01_{lib,build,make_config_melos,make_config_counter,runner,analyze,finalize}.py`(作品固有語は`config_*_01.json`に閉じ、コードはMelosハードコード無し)

## 0. 結論(先に要点)

1. **[委任_02訂正] 単独2語clipで`Melos said.`が不安定な原因は、本Trialでは1つに確定できない**。OpenAI(gpt-4o-mini-transcribe)は単独2語clipで`melos said`を**0/13**(綴り変種Mello/Mellow/Mellis/Melo等)。前後clipを結合して文脈を3〜28秒まで増やしても、同一/異ナレーターとも一貫した改善はなく(`melos said`一致 0〜31%、Rwin7[28.6秒]のみ67%)、安定閾値は**試した範囲では見つからなかった**。原因として併記すべき3点:
   - (a) **att6以外のtakeではプライミングが優勢**: 改善して見える条件は文脈clipに「Melos」という語自体が含まれる場合に偏る。a2_att6を除いて再集計すると、文脈にMelos語を**含まない 3/198 (2%)** vs **含む 13/55 (24%)**(付録C-2b。att6を含む旧集計は 18/234 (8%) vs 16/64 (25%))。この場合の`melos said`は、ASRが前出の綴りへ引きずられた結果であり、当該clipの発音確認ではない。
   - (b) **a2_att6では音響に基づく効果の可能性があり、真値は試聴待ち**: att6の文脈付き`melos said`は17/45のうち15件が文脈にMelosを含まない条件。文脈付きで`melos said`化したdistinct recipe 11件のうち**9件は`ctx_has_focus_word=false`**(付録C-2c)。さらにDpre25(異voice前置25秒・Melos語なし)でatt3/att5/att6が`melos said`(att6は2/2、att3/att5は1/2。付録C-2d)。これはプライミング(文脈のMelos語)では説明できず、文脈で綴りが安定する音響上の効果、または実際の発音差を拾った結果の可能性がある。ただし真値(耳で確認)が無く、「maskingの証拠」とも「正しく拾った証拠」とも確定できない。→ att6の17/45は「masking主証拠」ではなく**真値未確定の候補**に弱める。
   - (c) **「clipの長さ」と「`Melos said`のs+s融合(`Melos`語末sと`said`語頭sの連続)の有無」が交絡して未分離**: 長いclipでAzure/OpenAIが`Melos`と書けた例は、Melosの後ろがs始まりの語ではない(Opus指摘。個別に全例は再検証していない)。したがって「主因はclipの短さではない」とも「短さが主因」とも断定できない。本Trialは2語clipでの長さとs+s融合の効果を分離する実験をしていない。
2. **文脈結合は正認識率を明確には上げず、誤PASS(masking)の候補を増やす可能性がある**(ただし真値未確定): 本番NG take由来のproxy反例で、単独NG→文脈付きPASSに反転した観測は**13/41**(単独NGの10 targetの全rep観測。D-4。母集団はD-5のG0[13/36=target x recipeのrep1単位、単独PASSのtargetも含む]と異なる)。13件の内訳は nat_feet 4・nat_design 4・nat_bements 3(同音語・文脈で語が推測できるタイプ、**実効標本は3 target**)と nat_paused 2(語末子音付加のASR揺れ)(付録D-4b)。Melos a2_att6の17/45は上記(1)(b)のとおり真値未確定の候補。proxyの限界(正解は検証済みtake等であり真の発音は未確定)があるため、これらは確定false acceptではない。
3. **既知欠陥の反例(オフライン編集、真値既知)と、語末子音脱落の一般化範囲の限定**: 語の欠落/誤語(Melos→ruler、Melos削除、said削除)は文脈付きでも**0/12**でPASSにならない(文脈にMelosが有っても幻覚補完せず)。clip末の予測しやすい語(`said`/`death`、基音声3本)の末尾70〜460msを切り詰めた音声は、単独でも文脈付きでもOpenAI/whisperとも最終語を**綴りとしては**正しく書き、検出されなかった(42/42。ただし12音声x recipeの非独立観測であり、例えばsyn_B1_trunc*は`mello said`等でProduction判定ならほぼNG[18観測中PASSは3]になるため、42/42は「最終語の綴り一致」の基準での数字)。→ 結論は「**clip末の予測しやすい語(said/death、基音声3本)の切詰めは、単独・文脈付きともASRの綴りでは検出されなかった**」に限定する。**語中の語末子音(`Melos`の語末s、OPEN-330の対象)は未検証**(切詰は`said`等のclip末語に対してのみ。語中の語末s脱落・s+s接続への切詰反例は無い)。70ms切詰が知覚上の欠陥かは真値未確認、300〜460msは語末子音だけでなく母音まで削っている。
4. **Azure STT+Phrase Listは決定的**(同一音声2回で15/15一致)で、文脈の有無でtakeごとの結果がほぼ不変(att1=Melos、att3=Melo、他=Mellow/Mallow)。ただし**決定的であることは忠実であることを意味しない**(Phrase Listも綴りを誘導する)。take別の結果が先行調査の摩擦区間長と矛盾しない程度の観測であり、「Azureは音響差を拾う」とは言い切らない。OpenAIは同一音声でも領域転写が2回で一致するのは**72%**にとどまる(非決定的)。
5. **推奨案(採用はユーザー判断。いずれも未実装・未検証)**: ASR文脈結合をauto-acceptの根拠にする案は**非推奨**(REJECTED)。合理的な候補は、(a)**発生源を断つ**: 固有名詞語末の歯擦音+歯擦音始まり語の連続を避け、引用間narrator chunkに最小語数を持たせる原稿/構造ルール(OPEN-318代替③。ただし長clip化の効果自体は(1)(c)の交絡のため**未検証**)、(b)**作品単位のallow-list**(ただし後述E-(4)のとおり「その名前の語末s脱落リスクを作品内で許容する方針決定」と等価であり、1 takeの人間承認は別takeを守らない。選択肢i/ii/iiiはユーザー判断)、(c)Azure+Phrase List+HR fallbackは維持、(d)語末子音脱落には**音響的な独立証拠**(語末エネルギー/継続長、参照テキスト付き音素評価)を設計する(本Trial未検証)。いずれも新仕様でありTrial+Opus独立レビュー(条件A/C)+人間承認が必要。OPEN-331(HR承認take→6%減速後再検証Gate STOP)と一体で検討する必要がある。
6. 費用 **JPY39.61 / 40**(OpenAI 19.87、Azure 19.74、local whisper 0)。ただし**OpenAIの音声入力token単価は未確認**(`pricing_snapshot.json`にtext単価$1.25/Mしか無く、音声入力の別掲が無い。過小評価の可能性あり。OpenAI usage画面との照合が必要。詳細は費用節の[委任_02追記])。Melos累計は 185.4+39.61 = **約JPY225.0 / 300**(旧記述の「+39.5」混在を39.61に統一、[委任_02訂正])。TTS再生成0。Production state不変(sha256一致、write guard遮断0件[Production側])。

注: 本Trialの評価モデルは**Production同一モデル(gpt-4o-mini-transcribe、Azure Speech STT+PhraseList)**。最新モデル原則(PM_GOVERNANCE 25節)の例外理由=「比較可能性」(Productionと同じASRで、文脈結合の効果だけを測るため)。local faster-whisper(small/medium)は無料の第三者参照engine(Production対象外)。

## A. 既存仕様・実装の確認(¥0。新規重複機構を作らないためのGate)

調査方法: 既存evidence(`melos/asr_root_cause_01/ROOT_CAUSE_01.md`・`melos/cs_audit_01/CS_AUDIT_01.md`・`melos/remaining_issues_01/`)を再利用し、コード位置は現行ファイルをGrepで再照合(行番号は2026-10-13時点)。重複調査はしていない。

### A-1. 既存機構の機能・配線・適用範囲・Melos run_e2e_02での発火(1表)

| # | 既存機構 | コード位置 / 判定順序 | 適用範囲 | Melos run_e2e_02での実際の発火 | 解決できる問題 | 解決できない問題 |
|---|---|---|---|---|---|---|
| 1 | Connected Speech Validator Pattern A/B/C (OPEN-107/110) | `er011_b1_connected_speech_validator_01.py` `classify_connected_speech` L125(Pattern A L151/B L166/C L181)。`er006_preprod_hardening_01_validation.py` `classify_asr_match`から、(1)`non_entity_diffs`あり時 L1076、(2)diff空の最終fallback L1119 で呼ばれる。entity_like差(固有名詞のみ)は先に`entity_only`でUNCERTAINへreturnするため呼ばれない(`_is_benign_plural_pair`で吸収される`Melo`等は例外) | 全clip role(role非依存)。Pattern A=語末`-s/-es`脱落(綴り一致)、B/C=他の連続音 | **発火あり**: attempt_history 528件中CS系7(ACCEPT 5[うちMelos 4])。Std a2 part1_c5 att3(Azure=`Melo said.`)でPattern A ACCEPT | 綴りが`canonical-s`と完全一致する脱落(Melos→Melo、studies→study) | 同音別綴り(`Mello`/`Mellow`/`Mellis`)。Pattern Aの受理が語幹末sにも及ぶ点は承認根拠より広い(**OPEN-330**) |
| 2 | Connected Speech Equivalence Layer (OPEN-122) | `er011_connected_speech_equivalence_layer_production_01.py`、配線 `er006_secondary_asr_01.py` L547-548(`TRUE_CONTENT_MISMATCH`かつprotected_check通過時のみ)・L320-345 | 5 role(FULL_STORY含む)、flag既定False→呼出元がTrue | **Melosで0回**(`ASR_VALIDATION_UNCERTAIN`は入口条件外) | 非固有名詞の音韻環境A〜G(CMU音素既知語) | OOV固有名詞(`word_phones("melos")=None`)。減速後cascadeへflag未配線(OPEN-122(4)、今回の事象には無関係) |
| 3 | ASR Semantic Equivalence Layer (er021) | `er021_en_asr_semantic_equivalence_production_01.py`(telemetry書込 L779 `append_telemetry_log`)。`classify_asr_match`が内部で利用 | EN英語ASR照合全般 | 全clipでtelemetry発火(entity_only等) | 数字/契約形/複数形など | 固有名詞の綴り揺れ |
| 4 | 固有名詞Pronunciation Resolver・Ledger (er025系) | `er006_output/pronunciation_ledger_01/ledger.json`。melos(EN)=`cascade_unresolved_entity`/low/IPA `/ˈmiː.lɑːs/`(辞書推定)。Phrase Listとしてcascade Azureへ供給。CMU Case A(`_step_alternate_pass` `er006_secondary_asr_01.py` L423) | Ledger登録語 | 発火(Phrase List使用。TTS注入は対象外) | Ledgerに高信頼の読みがある語(JA melos=メロス) | EN melosは期待MEE-lahsと実際のTTS読み(MEL-os系)が不一致(OPEN-308)。CMU未収録でCase Aが構造的に常に未解決 |
| 5 | Primary→Secondary ASR Cascade (Tier3 Azure corroboration) | `er006_secondary_asr_01.py` `evaluate_attempt_with_cascade` L347 / detail L464。Tier3 L601-660(Azureがdiff位置でcanonical語を支持→`SECONDARY_ASR_CORROBORATED_MATCH`)、その後Primary#2/Azure#1/#2 | 英語本文clip(`segment_id`伝播が前提) | **発火あり**: 長clip(b1b part3_c3等)で多数PASS。2語clipでは`tier3_attempted_no_corroboration`(Azure=`Mellow`) | 長clipでAzureが`Melos`と綴る場合(10試行中8回) | Azureが綴りを再現しない2語clip |
| 6 | 6%減速後再検証 | `er003_v1_n3_01_tts_generate.py` `apply_a2_slowdown_postprocess` L169、`_post_slowdown_cascade_rescue` L117(是正済み: eb4c6479) | Std(a2)のみ | 是正前は救済なし→STOPPED x3(分類A)。是正後はTier3/cascadeを共有。**[委任_02更新]** part1_c5は、HR承認(ユーザー試聴OK)→attempt4採択→6%減速前の音声のためSlowdown Gate STOP(rc=2、ratio=1.2683、OPEN-331)が現状(Gate回避なし、assemble/pages未実行) | 減速前PASSの音声が減速後に落ちる問題 | 減速前から綴りが再現しない音声 |
| 7 | retry・fallback・Local Rewrite 7 Gates | `er020_tts_retry_local_rewrite_01.py`(role判定 L124-149)、`news_tail_fix.py` L283-296 / `crosslevel` L255-300。TTS上限3、Adv(b1b)はUNCERTAINで即cascade→LR→HR | 全role | Adv part1_c5: LR候補5件が全てGate7(全面書換でない)で不通過→HR。Std: fallback経由でPattern A受理 | 一般的な再生成・短い文言差し替え | 2語clip(LRは全面書換になりGate7不通過)=構造的に救済困難 |

### A-2. 結論(既存対策の限界)

- **解決できる**: 長clip(6語以上)の固有名詞綴り揺れ(Tier3: Azure+Phrase Listが10試行中8回`Melos`)、綴り一致の語末s脱落(Pattern A)、減速後の救済(是正済み)。
- **解決できない**: (1) 固有名詞が**OOV**(CMU未収録)で、Primary/Secondaryが**同音別綴り**(Mello/Mellow/Mellis)を返す2語clip。Equivalence Layerは入口条件(`TRUE_CONTENT_MISMATCH`)とCMU依存の両方で構造的に届かない。(2) Pattern Aは綴り水準で語幹末sを接尾辞と区別せず受理(OPEN-330)。(3) 語末子音の実際の脱落を、ASR文字列だけでは区別できない(安全≠成功原則)。
- **配線漏れ・判定順序の欠落(既存仕様の是正)**: 本Trialで**新規発見なし**。既知分は是正済み(減速後cascade=分類A)または既知Gap(OPEN-122(4)、OPEN-328 観測性)。`entity_only`先行判定は「到達できない受理可能ケース0件」(CS_AUDIT §3-6)で順序問題ではない。
- 本Trialの提案は全て**新仕様提案**であり、既存仕様の是正ではない(Production無変更)。

## B〜D. 実測の要約(数値の出典は付録の生集計表。全ASR呼出の生結果は`results_01.jsonl`)

### 実験の構成(再現可能)
- 音声は**全て既存**(TTS生成0): Melos run_e2e_02の`full_story_part1_c5`(Melos said.)全take(Std a2=6take[att1〜att6]、Adv b1b=1take)と、同run内の前後clip(同一ナレーターAoede、台詞voice Algieba/Charon/Erinome[gemini-2.5-pro-preview-tts])を、clip間300ms無音で結合(`conditions_manifest_01.json`に構成clip・sha256・秒数・target区間)。
- Melos主実験: 7take x 24条件(単独/同一voice前後[3〜27秒]/異voice前後[3〜25秒]/実ストーリー順隣接[c3 c4 T c6 c7、c1〜c7])= 168結合音声。OpenAIは各2回、Azure(PhraseList=Melos、word timestamps)はR00全take x2回+選抜条件、local whisperは全条件。target領域は(1)期待テキストとのdifflib整列、(2)Azure/whisperはword timestampsのtarget区間、の2通りで抽出(両者の一致率: Azure 49/49、whisper-small 92%、medium 100%=領域抽出は妥当)。
- 反例セット: (a)**synthetic**(既存音声のオフライン編集、欠陥の真値が既知): 語末子音切り詰め[70/140/220/300/380/460ms]、語欠落[Melos/said削除]、誤語[Melosをrulerに差し替え]、無改変の対照(intact control)。(b)**natural_ng**: 過去の本番NG take 11件(語末子音脱落/付加、固有名詞誤発音、文脈で推測可能な同音語)。素材は十分(各カテゴリ2件以上)。正解テキストは同segmentの検証済みtake等のproxy(真の発音は未確定)。

### B. ASR評価単位の比較(Melos、詳細は付録 B-1〜B-6)
| 観点 | OpenAI gpt-4o-mini-transcribe | Azure STT+PhraseList | local whisper-small |
|---|---|---|---|
| 単独2語clipで`melos said`と一致 | 0/13 (0%) | 2/14 (14%)[att1のみ2/2] | 0/7 |
| Production判定PASS(領域、Pattern A受理含む) | 0/13 | 6/14 (43%) | 4/7 |
| 文脈付き(298/49/161観測)で`melos said`一致 | 34/298 (11%) | 10/49 (20%) | 26/161 (16%) |
| 同一音声2回でtarget領域転写が一致 | **148/205 (72%)** | **15/15 (100%)** | 決定的(1回) |
| 誤認識の種類(OpenAI、単独) | 綴り変種11 + 語末付加(`meloset`=`Melos set`)2 | take別に固定(Melos/Melo/Mellow/Mallow) | Mello/Melo |
| ASR費用/音声秒 | JPY0.0041 | JPY0.0444 | 0 |
| 処理時間(中央値) | 0.4秒(0-3秒音声)〜0.96秒(16-40秒) | 0.6秒〜7.6秒 | 2.9〜5秒(CPU) |
- 正認識(`melos said`)を文脈量で見ると、OpenAIは Npre3/Npre8/Npre14/Npost3/Npost14/Dpre3/Dpost*=**0%**、Dpre25=31%、Npre27=15%、Rwin7(c1〜c7,28.6秒)=67%。**単調な「何秒以上なら安定」という閾値は存在しない**(文脈量を増やしても綴りは固定されず、文脈clipの内容[Melosという語を含むか]に支配される)。
- OpenAIの文脈付き出力の内訳(base,298観測): `mello said` 148、`melo said`(Pattern A受理)42、`melos said` 33、空(整列不能)13、その他(Mellow/Mellos/malice/mally等)。**[委任_02訂正]** 本文の`melos said` 33件は「領域転写が`melos said`と完全一致(exact_tokens)」、B-5表の34件は「focus語(Melos)の綴り一致(focus_exact)」の定義差(差の1件は a2_att6 Npost8 の領域転写`melos set`[Melos語は一致、sayが`set`])。同一定義ではない。
- 文脈にMelosを含む条件の方が`melos`一致が高い(**[委任_02訂正・数値統一]** OpenAI 25% vs 8%[att6含む旧集計。att6除外では24% (13/55) vs 2% (3/198)]、whisper-small **74% (26/35)** vs 0% (0/126)。旧記述の「78%」は誤記で表の74%に統一) → **att6以外では綴りのプライミングが優勢**。当該clipが本当に`Melos`と発音されているかの確認ではない。ただしatt6は文脈にMelosが無い条件でも`melos said`化しており、プライミングだけでは説明できない(結論(1)(b)、真値は試聴待ち)。

### C. 複数ナレーターの影響(付録 C-2〜C-4)
- 同一ナレーター文脈 vs 異ナレーター(台詞voice)文脈(同秒数、前置): OpenAIの Prod PASS = 3秒 15%/0%、7-8秒 23%/8%、13秒 46%/38%、23-26秒 38%/69%(同一/異)。差は一貫せず、7take(相関あり)x2回のため**ナレーター差は検出できない(文脈内容の差に埋もれる)**。ナレーターの影響を分離するには同一内容・別voiceのTTSが要るが、本Trialでは禁止のため**未分離**。
- Std(6take) vs Adv(1take): 結論は同じ(Advも単独OpenAI 0/1、Azure `mellow`が3/3で固定、文脈で変化なし)。Advはn=1のため統計的差は言えない。

### D. 汎化と安全性(付録 D-3〜D-10)
- **false accept(確定: 真値既知のsynthetic)**: 語欠落/誤語 **0/12**(文脈付きOpenAI)。clip末語の語末子音切り詰め(`said`/`death`、基音声3本から作った12音声)は **42/42が受理**(最終語の綴り一致[`analyze.py`のfocus_exact]基準。Production `classify_asr_match`の判定ではない)。**[委任_02訂正]** 42/42は12音声 x recipeの**非独立観測**(独立な音声は12)。同じ受理基準でProduction判定を使うと、syn_B1_trunc*は`mello said`等になり18観測中PASSは3のみで、42/42とは異なる。70ms切詰が知覚上の欠陥かは真値未確認で、300〜460msは語末子音だけでなく母音まで削っている。→ 結論は「clip末の予測しやすい語の切詰めは単独・文脈付きともASRの綴りでは検出されなかった。語中の語末子音(`Melos`のs、OPEN-330対象)は未検証」に限定する(文脈が誤PASSを増やしたのではなく、ASR自体がこの種の切詰めに対して綴りを補完する)。
- **false accept候補(proxy: 本番NG take)**: 単独NGのtarget 10件のうち、文脈付きOpenAIでPASSに反転したのは **13/41観測**(D-4。**[委任_02追記]** 内訳は nat_feet 4・nat_design 4・nat_bements 3[同音語・文脈推測]=実効標本3 target、+ nat_paused 2[語末子音付加のASR揺れ]。付録D-4b)。固有名詞誤発音3件(Milo/Milos'/Melus')は反転 0。語末子音付加(nat_counts/nat_paused/nat_forced)は ASR自身の揺れ(単独でも100%PASSの回あり)。Melos a2_att6は文脈付き`melos said` **17/45**だが、**[委任_02訂正]** これは「masking主証拠」ではなく真値未確定の候補(15件は文脈にMelosが無い条件で、プライミングでは説明できず、音響に基づく効果の可能性もある。試聴で確定)。→ 「長い音声のASRが正しい表記を返しただけで自動PASS」は、同音語/文脈で一意に決まる語、および名前が文脈に既出の場合には**実際に起き得る**。
- **防止条件の評価(OpenAI文脈付き一次)**: 単独整合(G1)は natural proxy の反転を **13/36→3/36** に抑える(**[委任_02追記]** D-5の36はtarget x recipeのrep1単位で、単独PASSのtargetも含む母集団。D-4の13/41[全rep観測、単独NG targetのみ]とは母集団が異なる)が、**Melosのように単独が常にNGの問題は救えなくなる**(目的矛盾)。2回呼出一致(G2)・logprob閾値(G3)・独立engine(G4)は反転抑止が弱い/部分的(語末切詰には全て無効)。OpenAI領域tokenのmin logprobは good_control(5%点-2.48)と欠陥(-1.0)で分離せず、**確信度は防止条件にならない**。Secondary corroboration必須+HR fallback維持が最低限の安全弁。D-5表頭G0は**[委任_02訂正]**「Prod判定PASS」ではなく実際の受理基準(切詰/対照syntheticは最終語の綴り一致、それ以外はProduction `classify_asr_match` PASS)に修正(`analyze.py`ラベルのみ変更、数値は不変)。
- Azure(deterministic)は文脈有無で結果がほぼ不変 → 文脈結合の追加ASR費(Azure 8秒文脈で約JPY0.36/回)に見合う情報増加が無い(決定的=忠実ではない点は結論(4)のとおり)。

## E. 改善方式の比較(机上+B〜D実測)

| 方式 | 品質(正認識率 / false accept) | コスト(1記事あたり追加) | 開発負担 | 既存Production仕様との整合 | 量産適用性 | A/B/C分類 |
|---|---|---|---|---|---|---|
| **(1) clip分割維持+ASR時のみ前後文脈結合** | Melos綴り改善: **att6以外では名前が文脈にある時のみ上がる**(att6除外: 含まない2%/含む24%=プライミング)。att6は文脈にMelosが無くても`melos said`化(17/45中15件)するが、プライミングか音響効果かは真値(試聴)未確定。false accept候補: 反転13/41(proxy。実効標本は3 target[feet/design/bements]+paused 2)。clip末語の語末子音切詰は単独と同じく綴りでは検出されない(語中は未検証) | OpenAI 8秒文脈で約JPY0.03/回、Azure 約JPY0.36/回(単価は費用節の注記参照、OpenAI音声入力単価は未確認)。短clip(固有名詞のみ)数x cascade最大4step。記事あたり数JPY(Azure使用時) | 中(結合音声生成+target区間抽出+region整列+per-clip判定への写像+retryとの対応) | ASR側のみの変更でclip単位retry/fallback/LR/Master Store再利用/HR Lockは不変。ただし**判定根拠が結合音声になり、ASRが他clipの綴りに引きずられる**=安全≠成功原則に抵触しやすい | 技術的には可。auto-acceptには**非推奨(REJECTED)** | **B**(OPEN-318 C-c として提案済み・未実測。本Trialが初の実測) |
| **(2) TTS clip自体を長くする(原稿/分割ルール)** | **[委任_02訂正]** 既存証跡では、長clipでAzure+PhraseListが`Melos`を8/10(2語clipは0/8)、OpenAIは10語超で10/22(3語以下0/6)。ただし**長さと「s+s融合(`Melos said`)の有無」が交絡**しており(長clip成功例はMelosの後ろがs始まりでない)、**clipを長くすることの効果自体は未検証**。「長clipでは改善」とは言い切れない。false acceptは既存Tier3(Azure corroboration)の範囲 | TTS再生成不要(新規記事の原稿/分割で回避)。既存記事は再生成が要りJPY発生 | 低〜中(規模小〜中。下記「(2)の影響範囲」) | Std/Adv段落対応・分割(`segment_plan`)・clip単位retry/HR Lock/Master Storeと整合(ルールを足すだけ)。台詞voiceとnarrator voiceの境界は維持(attributionを台詞clipへ併合はしない) | 発生源に対処する案としては高いが、効果は交絡のため**未検証**(次Trial候補) | **B**(OPEN-318 代替案③「said Melosの語順、前後clipと結合」として提案済み・未採用) |
| **(3) ASRへ文脈情報を与える(prompt / Phrase List / 前文テキスト)** | OpenAI promptに作品名を与えると単独 36%・3秒文脈付き 75% が`melos said`(base 0%)。**ただしMellis takeも`melos said`化(att4 2/2)、att6も3秒文脈+promptで`melos said` 2/2**(att6は真値未確定のため「masking」とは確定せず。att4[Mellis]は`melos`化で誤認の疑いが強い)。前文テキストpromptは効果弱い(21%)。AzureのPhraseListは効果あり(nophrase 0/7→2/14)だが再現性はtake依存 | ほぼ0(同一ASR呼出) | 低(OpenAI prompt引数。既にKey Phrase経路で`prompt`機構あり) | Azure PhraseListは**既存仕様**。OpenAI body segmentへのprompt拡張は新仕様 | 単独ではmasking懸念、**独立証拠[Azure/音響]と必ず併用**が条件 | Azure PhraseList=**A**(配線済み)、OpenAI promptのbody拡張=**C**(新規) |
| **(4) 既存Connected Speech/Resolver/Secondary ASRの再判定改善** | Pattern A'(stem同音)は効果が限定的(CS_AUDIT 5-2)。作品単位allow-list(人間承認済み綴り群のみ`PASS_WITH_WARNING`)はMelosの綴り揺れを救えるが、**「その名前の語末s脱落リスクを作品内で許容する方針決定」と等価**で、1 takeの人間承認は別takeのs脱落を防がない(下記「(4)の判断3択」)。Equivalence LayerはOOVに届かない | 0〜小(人間の初回承認1回/作品) | 中(allow-list保存場所・参照順・telemetry) | 既存Ledger/work canon(`seed_work_canon_reading`)・Phrase List・HR Lockと整合しやすい。Pattern A範囲(OPEN-330)の確定が前提。OPEN-331(HR承認take→減速後再検証Gate)と一体検討 | 方針決定(下記3択)が前提 | A'拡張=**B**(OPEN-327)、作品単位allow-list=**B**(OPEN-327追記案・OPEN-318 C-a)、OPEN-330範囲確定=**A**(既存仕様の範囲明確化) |

### 推奨候補と誤PASS対策(採用はユーザー判断。以下は全て未実装・未検証)
**[委任_02訂正] 候補: (2)の作品非依存ルール+(4)の方針決定(3択)+既存(3)Azure PhraseList+HR維持+音響証拠の併用。(1)は採用しない(診断用途のみ可)。**
1. **発生源を断つ**(2): 例文`Melos said softly to the ruler.`は`Melos`の直後に`said`ではなく`softly`が来るためs+s融合は避けられるが、旧例の提示は不適切だった(`Melos said ...`と書けばs+s融合を残す)。ルールは**作品非依存の音声的条件**として書く: (i) 固有名詞の語末が歯擦音(s/z/sh等)のとき、直後に歯擦音始まりの語(said/says/saw/softly等s始まり)を連続させない、(ii) 引用間narrator chunk(attribution clip)に最小語数を置く。**長clip化の効果は交絡(結論(1)(c))のため未検証**。OPEN-318旧Opus指摘の代替案「said Melosの語順」(Melosを文末側でなくsaidの後ろへ)は、(i)の「語末歯擦音+s始まり語の連続を避ける」を満たす方法の一つであり整合する(`said Melos.`は`said`語末dと`Melos`語頭mで融合しない。ただし`Melos`語末sがその後ろの語頭と接続するかは文次第)。
   - **(2)の影響範囲(読取確認のみ、コード変更なし)**: `er062_family_z_structure_01.py` `build_flat_chunks`(L535付近)は引用とそれ以外のnarrator chunkを(段落index, voice, 生テキスト)の列にし、引用間の空白のみchunkだけ捨てる。`plan_clips`(L552付近)は`fam_c.plan_story_segments`(`er013_family_c_production_01.py` L306付近、`_build_base_segments` L202付近)をそのまま使い、voice変化は`voice_boundary(分割不可避)`で必ず別clipになる=**narrator chunkの最小語数制約は構造上存在しない**。変更候補は2つ: (a) Z writerの記事生成promptへのattributionルール追加(`er062_family_z_writer_01.py`。記事生成promptの位置は本委任では未特定、attribution LLM判定promptはL208付近で別物)、(b) structure段(`plan_clips`後)の決定論的lint(違反時WARN/retry)。TTS/ASR/retry/Local Rewrite/Master Store/HR Lockは変更不要、既存記事の遡及は不要(新規記事のみ)。規模は小〜中。
2. **作品単位の人間承認allow-list**(4): 初回HRで人が読み・綴りを聴いて承認した綴り群(Mello/Mellow/Melo等)のみ以後自動受理(PASS_WITH_WARNING)する案は、**「その作品内でこの名前の語末s脱落リスクを許容する方針決定」と等価**。1 takeの人間承認は、別takeのs脱落を防げない(承認は音声ではなく綴りに紐付くため)。ユーザー判断3択: **(i) 方針として許容**(OPEN-330(a)の名前単位版)、**(ii) 承認をaudio sha256に紐付ける**(既存のHR Lock/Master Store再利用の範囲=承認した音声そのものだけ自動受理、別takeはHR)、**(iii) 音響的独立証拠の併用を採用条件にする**(語末エネルギー/継続長/音素評価が通った場合のみallow-list適用)。OPEN-331(HR承認take→6%減速後に再検証するGate STOP)は「承認音声が後処理で変わる」問題で(ii)の範囲と直結するため、**一体検討が必要**。
3. **誤PASS対策(共通)**: (i) Azure(決定的)+PhraseListを一次の指標として維持(ただし決定的=忠実ではない)、(ii) 結合ASRや単独OpenAIのPASSは**Secondary corroboration必須**、(iii) HR fallback維持(Gate無効化なし)、(iv) 語末子音欠落には**音響的な独立証拠**(語末エネルギー・継続長、または参照テキスト付き音素評価)が要る(本Trial未検証。OPEN-327 C-2と同種の無料オフライン校正から)。
4. Production採用提案前に**Opus独立技術レビュー(条件A: 新しい構造/条件C: 重要変更)**と、人間の`APPROVED_FOR_PRODUCTION`が必要(本Trialは採用判断をしない)。

## OPEN-330(語末s自動許容範囲)の評価(現行ルールは変更しない)
- 本Trialの観測: Pattern A受理(`melo said`)はOpenAI文脈付きで42回、Azureはtake固定(att3は単独でも文脈付きでも`melo said`)。Azureのtake別結果は、先行調査の摩擦区間長(att1 190ms=`Melos`、att3 120ms=`Melo`)と矛盾しない程度の観測であり、ASRの`Melo`が語末sの実際の短縮と関連している可能性は**否定できないが確定ではない**(真値[耳で確認]は無い。決定的=忠実ではない)。
- **[委任_02訂正]** 一方、clip末の予測しやすい語(said/death、基音声3本)の切詰め(末尾70〜460ms)は、単独・文脈付きとも**ASRの綴りでは検出されなかった**(42/42は12音声x recipeの非独立観測)。これは「語末子音脱落一般はASRで検出不能」の**実証ではない**: 語中の語末子音(`Melos`の語末s、s+s接続含む)の切詰めは本Trialで**未検証**。したがってPattern A(語幹末sも綴り水準で受理)について本Trialが支持するのは、「ASRの綴りだけでは語の切詰めを検出しにくい場面があり、固有名詞の語幹末sについてASR証拠が安全を保証するかは未確認」という限定的な点にとどまる(CS監査の安全≠成功の指摘と矛盾しないが、本Trial単独で実証したとは言わない)。
- 選択肢への示唆(判断はユーザー。**[委任_02追記]**注意): (b)接尾辞限定はHR増(Melos→Meloが受理されなくなる)だが最も保守的。(c)作品単位の人間承認許容語幹リストは、**「その名前の語末s脱落リスクを作品内で許容する方針決定」と等価**で、1 takeの人間承認は別takeのs脱落を防がない(承認が綴りに紐付き、音声に紐付かないため)。(c)を採るなら推奨節の3択((i)方針許容 (ii)audio sha256紐付け (iii)音響的独立証拠併用)から選ぶ必要がある。(a)現状承認は、語幹末s脱落の誤PASSを許容する仕様確認になる。OPEN-331(HR承認take→減速後再検証Gate)と一体検討。

## 既存資産照合(PM_GOVERNANCE 21節 A/B/C)
本Trial自体=**B**(OPEN-318 C-c「前後に既知安全音声を結合してASR(Trial要)」の初の実測。新規Trialではなく既提案の検証)。方式別の分類は上表の最右列。新規OPENは起票しない(既存OPEN-318/327/330へ追記)。

## 限界・注意(正直な記載)
1. 正解(真の発音)は人手試聴でしか確定できない。natural_ngの「反転」はfalse accept**候補**。確定false acceptはsyntheticのみで、そこでは語レベル欠陥0/12、語末切詰は検出不能(文脈無関係)。
2. 語末切詰のsyntheticは「切断」であり、実際のTTSの子音弱化/融合とは異なる。実TTSの弱化子音をASRが検出できるかは別途(本Trialの結論は「予測しやすい語はASRが補完する」ことの実証)。
3. 反例の文脈clipはproxy(検証済みASRテキスト)で、ストーリー上は不連続。実ストーリー順の隣接条件(Rpre/Rpost/Rboth/Rwin5/7)は別に測定済み。
4. 費用制約により Azure は選抜条件のみ(主実験70呼出、反例 R00のみ)、Azureの2回呼出はR00全take+選抜2条件。OpenAIはMelos主実験の最後の一部のrep2が上限JPY14でカットされた(実績311/336呼出)。非決定性の統計はOpenAI中心。
5. 並行agentのMelos run_e2e_02等には一切書き込んでいない(read-only)。`delegation check`は本委任文の抄録で実行(固定ブロックE-1/D-1/G-1/F-1ラベルがFAIL、TTS関連警告はTTS禁止のため非該当)。
6. **[委任_02追記] 一般化の範囲**: Melos側は**1フレーズ(`Melos said.`)・1ナレーター(Aoede)・7 take**のみ。Family Z全体・複数ナレーターへの一般化は未検証。
7. **[委任_02追記] 統計の限界**: 各recipeはn=13程度(7takeのOpenAI 2回呼出)で、take相関があり95%信頼区間は広い(0/13でも真の率の上限は約25%)。「安定閾値は存在しない」ではなく「**試した範囲では見つからなかった**」。
8. **[委任_02追記] Azureの解釈**: 「Azureは音響差を拾う」とは言い切らない。決定的(同一音声で結果が一致)であることは音声に忠実であることを意味せず、Phrase Listも綴りを誘導する。
9. **[委任_02追記] 領域抽出の限界**: OpenAI領域抽出は期待テキストとの文字列整列のみでtimestamp照合は無い(Azure/whisperはtimestamp領域も併用)。`meloset`型の融合出力(`melos`+`said`が1語に融合)は整列で不利になる(領域が空/ずれる可能性)。
10. **[委任_02追記] 費用計算**: OpenAIの音声入力token単価が`pricing_snapshot.json`に別掲されておらず、text単価$1.25/Mで計算した(費用節参照)。

## 費用・処理時間・Production state不変(詳細は`cost_01.json`、`telemetry_guard_01.json`)
- 費用: **JPY39.61 / 40**(OpenAI 19.87[4,816音声秒]、Azure 19.74[443音声秒]、local whisper 0)。単価出典 `er005_output/cost_baseline_01/pricing_snapshot.json`(gpt-4o-mini-transcribe 入力$1.25/M・出力$5.0/M token[OFFICIAL_SOURCE]、Azure STT $1.0/音声時間[Retail Prices API])、USD/JPY=160。呼出984件(smoke test 2件を含む)(うち有料はOpenAI/Azure)。TTS再生成0。Melos累計 約JPY225.0 / 300(185.4[CS監査 委任_02時点、COST_LEDGER最終値]+39.61=225.01)。**[委任_02訂正]** 旧記述の「+39.5」は39.61に統一(累計の最新値はledger確認が必要)。ledgerは並行agentの管理領域のため本Trialから追記しない。
- 当初見積(Azure選抜+OpenAI全条件)よりOpenAI実績が高く(音声入力単価の扱いは未確認、下記)、主実験で上限JPY14に達し一部rep2が未実施(上記限界4)。以降の反例/感度実験(truncation sweep等)は残額の範囲で小規模実施。
- **[委任_02追記・単価確認]** `er005_output/cost_baseline_01/pricing_snapshot.json`(L300-323付近)を確認: gpt-4o-mini-transcribeは`input_tokens` $1.25/M と`output_tokens` $5.0/M の2行のみで、**音声入力tokenの別掲単価は無い**。したがって**音声入力単価は未確認**。text単価$1.25/Mで計算したため**過小評価の可能性あり、OpenAI usage画面との照合が必要**(推定値は出さない)。`cost_01.json`の`recalc`欄に注記(元の値は保持)。OpenAI 549呼出の合計は入力48,030 tokens/出力12,818 tokens(`usage`値)。lib(`er065_..._lib.py` L299)はOpenAI例外時にjpy=0を返す設計だが、本Trialではok=falseの結果は0件・jpy=0の有料呼出も0件。lib側に`input_token_details`(audio/text内訳)の記録を追加する改修は提案のみ(今回は未実施)。
- Production state不変: 全Trial processで実行前後にtelemetry/attempt_history/HR queue/Master Store/ledger/cost_baseline/run_e2e_02 cost_log/COST_LEDGERの行数とsha256を記録。**最初のprocess開始時と最終確認時で全10ファイルが完全一致**(telemetry.jsonl[er021]=9168行、[er025]=185行、attempt_history=12767行、HR queue=75行、Master Store manifest=10297行・reuse_telemetry=1844行、ledger=1200行、cost_summary=135行、run_e2e_02 cost_log=313行、COST_LEDGER=103行)。各process実行中の変化も0。`sys.addaudithook`のwrite guardはtrial dir(+OS temp)外への書込を例外で遮断し、遮断記録は faster-whisperのHugging Faceキャッシュ`refs/main`書込(無害、モデルは既存キャッシュ使用)のみ。Production ASR helper(`er006_secondary_asr_01.get_full_text_via_azure_stt_with_phrase_list`等)は呼ばず、lib内の読取専用実装を使用。`classify_asr_match`は読取呼出しのみ・`semantic_equivalence.append_telemetry_log`はno-op化。
- 外部STOP: `docs/pm/delegation_log/*STOP_NOTICE*`は2026-10-12の別管理ID(run_e2e_01)の通知で本委任(別run・別管理ID・明示許可あり)には非適用と解釈。`<trial dir>/STOP`・`STOP_ALL`は不在(各runnerが呼出ごとに確認)。自分のprocessが外部停止された事象なし、rc≠0の連続なし、再起動はwhisper(無料)の1回のみ[自分のglobal cap判定で停止+write guardのOS temp許可不足を是正して再実行。有料runの再起動0]。

## [委任_02追記] 次Trial候補(未実施・提案のみ)
- **参照テキスト付き音素評価**: Azure Pronunciation Assessment、またはlocal forced alignment/wav2vec2音素CTC(**プロジェクト未使用**)。ASRの綴り出力ではなく、期待テキストの各音素の達成度を見ることで、語末子音・語中語末sの脱落をASRの言語モデル補完に依存せず評価する。
- 条件: 既存wavのみ(TTS生成0)、**ユーザー試聴ラベルを真値に校正**、**語中の語末s(s+s接続含む)の切詰め反例を追加**、実施前に費用見積+Opus条件A(新しい構造/評価方式)。

## [委任_02追記] 残るユーザー判断事項案(推奨付き。採否はユーザー)
- U1: ASR文脈結合(C-c)をauto-accept条件にしない(REJECTED)の確認。推奨=確認(診断用途のみ可)。
- U2: allow-list(4)の方針3択 (i)方針許容 (ii)audio sha256紐付け (iii)音響的独立証拠併用。推奨=(ii)を基本に、(iii)の校正結果が出れば併用。OPEN-331(減速後再検証Gate)と一体で判断。
- U3: 原稿/構造ルール(2)(作品非依存の音声的条件)を新仕様候補としてTrial化するか。推奨=Trial化(効果は未検証のため、長さとs+s融合を分離する実験設計とセット)。
- U4: 音響的独立証拠(音素評価)の次Trial(無料オフライン校正から)を許可するか。推奨=許可(実施前に費用見積+Opus条件A)。
- 任意: a2_att6/att1/att3の人手試聴でattempt6の文脈付き`melos said`が真に`said`か`set`かを確定する(真値、(1)(b)の解消)。推奨=実施(無料)。

## 人手試聴を推奨する音声(Production判定は変更しない。HR queue/HR Lockには触れない)
| 音声(パスはTrial dirへの複製) | 理由 |
|---|---|
| `audio_src/a2_narration/attempts/full_story_part1_c5_attempt6_minimalfallback.wav`(=現行final) | 単独OpenAIは`meloset`で一貫だが、文脈付きでは`melos said` 17/45。語末が`said`か`set`か(語末/d/)を耳で確認 |
| 同 `..._attempt5_minimalfallback.wav` / `..._attempt4_customadfcf33f.wav` | att5=`melloset`系、att4=`Mellis`(prompt付与で`melos said`化) |
| 同 `..._attempt1_customadfcf33f.wav`(Azure=Melos) / `..._attempt3_minimalfallback.wav`(Azure=Melo) | 語末sの有無(摩擦区間190ms vs 120ms)の聴感差 |
| natural反例: `config_natural_ng_01.json`の`nat_feet`/`nat_design`/`nat_bements` | 文脈で正解語に反転(feet→feed等)。真に誤発音かASR誤りか |

## 付録: 生集計表(自動生成 `analysis_tables_01.md`と同一)
## B-1. Melos target take x recipe x engine: 正認識率(target領域がcanonical 'Melos said.' と一致)

### engine=openai (base variant) — exact_tokens(領域=melos said) / focus(Melos)語一致 / Production判定PASS(領域, CS受理含む)

| recipe | n | exact_tokens | focus(Melos)一致 | Prod classify PASS | strict(EXACT/NORMALIZED) | 平均秒 |
|---|---|---|---|---|---|---|
| R00_alone | 13 | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) | 1.4 |
| Npre3 | 13 | 0/13 (0%) | 0/13 (0%) | 2/13 (15%) | 0/13 (0%) | 4.3 |
| Npre8 | 13 | 0/13 (0%) | 0/13 (0%) | 3/13 (23%) | 0/13 (0%) | 8.9 |
| Npre14 | 13 | 0/13 (0%) | 0/13 (0%) | 6/13 (46%) | 0/13 (0%) | 14.8 |
| Npre27 | 13 | 2/13 (15%) | 2/13 (15%) | 5/13 (38%) | 2/13 (15%) | 27.5 |
| Npost3 | 13 | 0/13 (0%) | 0/13 (0%) | 1/13 (8%) | 0/13 (0%) | 4.3 |
| Npost8 | 13 | 5/13 (38%) | 6/13 (46%) | 6/13 (46%) | 5/13 (38%) | 9.3 |
| Npost14 | 13 | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) | 14.8 |
| Nboth | 13 | 0/13 (0%) | 0/13 (0%) | 2/13 (15%) | 0/13 (0%) | 11.8 |
| Dpre3 | 13 | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) | 4.5 |
| Dpre5 | 13 | 1/13 (8%) | 1/13 (8%) | 2/13 (15%) | 1/13 (8%) | 5.9 |
| Dpre6 | 13 | 2/13 (15%) | 2/13 (15%) | 3/13 (23%) | 2/13 (15%) | 7.3 |
| Dpre8 | 13 | 0/13 (0%) | 0/13 (0%) | 1/13 (8%) | 0/13 (0%) | 9.2 |
| Dpre11 | 13 | 2/13 (15%) | 2/13 (15%) | 4/13 (31%) | 2/13 (15%) | 11.8 |
| Dpre14 | 13 | 1/13 (8%) | 1/13 (8%) | 5/13 (38%) | 1/13 (8%) | 15.2 |
| Dpre25 | 13 | 4/13 (31%) | 4/13 (31%) | 9/13 (69%) | 4/13 (31%) | 26.0 |
| Dpost3 | 13 | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) | 4.5 |
| Dpost8 | 13 | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) | 9.2 |
| Dboth | 13 | 2/13 (15%) | 2/13 (15%) | 3/13 (23%) | 2/13 (15%) | 9.1 |
| Rpre | 13 | 2/13 (15%) | 2/13 (15%) | 4/13 (31%) | 2/13 (15%) | 5.9 |
| Rpost | 13 | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) | 4.7 |
| Rboth | 13 | 2/13 (15%) | 2/13 (15%) | 6/13 (46%) | 2/13 (15%) | 9.3 |
| Rwin5 | 13 | 2/13 (15%) | 2/13 (15%) | 5/13 (38%) | 2/13 (15%) | 19.7 |
| Rwin7 | 12 | 8/12 (67%) | 8/12 (67%) | 8/12 (67%) | 8/12 (67%) | 28.6 |

### engine=azure (base variant) — exact_tokens(領域=melos said) / focus(Melos)語一致 / Production判定PASS(領域, CS受理含む)

| recipe | n | exact_tokens | focus(Melos)一致 | Prod classify PASS | strict(EXACT/NORMALIZED) | 平均秒 |
|---|---|---|---|---|---|---|
| R00_alone | 14 | 2/14 (14%) | 2/14 (14%) | 6/14 (43%) | 2/14 (14%) | 1.4 |
| Npre3 | 11 | 2/11 (18%) | 2/11 (18%) | 6/11 (55%) | 2/11 (18%) | 4.3 |
| Npre8 | 4 | 1/4 (25%) | 1/4 (25%) | 2/4 (50%) | 1/4 (25%) | 9.0 |
| Dpre3 | 7 | 1/7 (14%) | 1/7 (14%) | 2/7 (29%) | 1/7 (14%) | 4.5 |
| Dpre8 | 4 | 1/4 (25%) | 1/4 (25%) | 3/4 (75%) | 1/4 (25%) | 8.8 |
| Rpre | 4 | 1/4 (25%) | 1/4 (25%) | 3/4 (75%) | 1/4 (25%) | 5.6 |
| Rpost | 4 | 1/4 (25%) | 1/4 (25%) | 2/4 (50%) | 1/4 (25%) | 5.0 |
| Rboth | 11 | 2/11 (18%) | 2/11 (18%) | 7/11 (64%) | 2/11 (18%) | 9.3 |
| Rwin5 | 4 | 1/4 (25%) | 1/4 (25%) | 2/4 (50%) | 1/4 (25%) | 19.7 |

### engine=whisper-small (base variant) — exact_tokens(領域=melos said) / focus(Melos)語一致 / Production判定PASS(領域, CS受理含む)

| recipe | n | exact_tokens | focus(Melos)一致 | Prod classify PASS | strict(EXACT/NORMALIZED) | 平均秒 |
|---|---|---|---|---|---|---|
| R00_alone | 7 | 0/7 (0%) | 0/7 (0%) | 4/7 (57%) | 0/7 (0%) | 1.4 |
| Npre3 | 7 | 0/7 (0%) | 0/7 (0%) | 3/7 (43%) | 0/7 (0%) | 4.3 |
| Npre8 | 7 | 0/7 (0%) | 0/7 (0%) | 1/7 (14%) | 0/7 (0%) | 8.9 |
| Npre14 | 7 | 4/7 (57%) | 7/7 (100%) | 4/7 (57%) | 4/7 (57%) | 14.9 |
| Npre27 | 7 | 1/7 (14%) | 6/7 (86%) | 1/7 (14%) | 1/7 (14%) | 27.4 |
| Npost3 | 7 | 0/7 (0%) | 0/7 (0%) | 0/7 (0%) | 0/7 (0%) | 4.3 |
| Npost8 | 7 | 7/7 (100%) | 7/7 (100%) | 7/7 (100%) | 7/7 (100%) | 9.3 |
| Npost14 | 7 | 3/7 (43%) | 3/7 (43%) | 3/7 (43%) | 3/7 (43%) | 14.9 |
| Nboth | 7 | 0/7 (0%) | 0/7 (0%) | 1/7 (14%) | 0/7 (0%) | 11.8 |
| Dpre3 | 7 | 0/7 (0%) | 0/7 (0%) | 1/7 (14%) | 0/7 (0%) | 4.5 |
| Dpre5 | 7 | 0/7 (0%) | 0/7 (0%) | 4/7 (57%) | 0/7 (0%) | 5.8 |
| Dpre6 | 7 | 0/7 (0%) | 0/7 (0%) | 6/7 (86%) | 0/7 (0%) | 7.3 |
| Dpre8 | 7 | 0/7 (0%) | 0/7 (0%) | 5/7 (71%) | 0/7 (0%) | 9.0 |
| Dpre11 | 7 | 0/7 (0%) | 0/7 (0%) | 1/7 (14%) | 0/7 (0%) | 11.7 |
| Dpre14 | 7 | 0/7 (0%) | 0/7 (0%) | 0/7 (0%) | 0/7 (0%) | 15.1 |
| Dpre25 | 7 | 0/7 (0%) | 0/7 (0%) | 2/7 (29%) | 0/7 (0%) | 25.8 |
| Dpost3 | 7 | 0/7 (0%) | 0/7 (0%) | 0/7 (0%) | 0/7 (0%) | 4.5 |
| Dpost8 | 7 | 0/7 (0%) | 0/7 (0%) | 0/7 (0%) | 0/7 (0%) | 9.0 |
| Dboth | 7 | 0/7 (0%) | 0/7 (0%) | 0/7 (0%) | 0/7 (0%) | 8.9 |
| Rpre | 7 | 0/7 (0%) | 0/7 (0%) | 4/7 (57%) | 0/7 (0%) | 5.8 |
| Rpost | 7 | 0/7 (0%) | 0/7 (0%) | 1/7 (14%) | 0/7 (0%) | 4.9 |
| Rboth | 7 | 0/7 (0%) | 0/7 (0%) | 1/7 (14%) | 0/7 (0%) | 9.3 |
| Rwin5 | 7 | 0/7 (0%) | 0/7 (0%) | 2/7 (29%) | 0/7 (0%) | 19.7 |
| Rwin7 | 7 | 3/7 (43%) | 3/7 (43%) | 3/7 (43%) | 3/7 (43%) | 28.5 |

## B-2/C. 文脈量・同一/異ナレーター別(Melos main, base)

| engine | 条件群 | 文脈秒(前後合計) | n | exact_tokens | focus一致 | Prod PASS |
|---|---|---|---|---|---|---|
| openai | alone | 0-0.01 | 13 | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) |
| openai | same_voice | 2-4 | 26 | 0/26 (0%) | 0/26 (0%) | 3/26 (12%) |
| openai | same_voice | 7-11 | 39 | 5/39 (13%) | 6/39 (15%) | 11/39 (28%) |
| openai | same_voice | 11-16 | 26 | 0/26 (0%) | 0/26 (0%) | 6/26 (23%) |
| openai | same_voice | 22-30 | 13 | 2/13 (15%) | 2/13 (15%) | 5/13 (38%) |
| openai | diff_voice | 2-4 | 27 | 0/27 (0%) | 0/27 (0%) | 0/27 (0%) |
| openai | diff_voice | 4-7 | 28 | 3/28 (11%) | 3/28 (11%) | 6/28 (21%) |
| openai | diff_voice | 7-11 | 49 | 4/49 (8%) | 4/49 (8%) | 7/49 (14%) |
| openai | diff_voice | 11-16 | 13 | 1/13 (8%) | 1/13 (8%) | 5/13 (38%) |
| openai | diff_voice | 16-22 | 1 | 0/1 (0%) | 0/1 (0%) | 0/1 (0%) |
| openai | diff_voice | 22-30 | 12 | 4/12 (33%) | 4/12 (33%) | 9/12 (75%) |
| openai | mixed_real | 2-4 | 13 | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) |
| openai | mixed_real | 4-7 | 13 | 2/13 (15%) | 2/13 (15%) | 4/13 (31%) |
| openai | mixed_real | 7-11 | 13 | 2/13 (15%) | 2/13 (15%) | 6/13 (46%) |
| openai | mixed_real | 16-22 | 13 | 2/13 (15%) | 2/13 (15%) | 5/13 (38%) |
| openai | mixed_real | 22-30 | 12 | 8/12 (67%) | 8/12 (67%) | 8/12 (67%) |
| azure | alone | 0-0.01 | 14 | 2/14 (14%) | 2/14 (14%) | 6/14 (43%) |
| azure | same_voice | 2-4 | 11 | 2/11 (18%) | 2/11 (18%) | 6/11 (55%) |
| azure | same_voice | 7-11 | 4 | 1/4 (25%) | 1/4 (25%) | 2/4 (50%) |
| azure | diff_voice | 2-4 | 7 | 1/7 (14%) | 1/7 (14%) | 2/7 (29%) |
| azure | diff_voice | 4-7 | 1 | 0/1 (0%) | 0/1 (0%) | 1/1 (100%) |
| azure | diff_voice | 7-11 | 3 | 1/3 (33%) | 1/3 (33%) | 2/3 (67%) |
| azure | mixed_real | 2-4 | 4 | 1/4 (25%) | 1/4 (25%) | 3/4 (75%) |
| azure | mixed_real | 4-7 | 4 | 1/4 (25%) | 1/4 (25%) | 2/4 (50%) |
| azure | mixed_real | 7-11 | 11 | 2/11 (18%) | 2/11 (18%) | 7/11 (64%) |
| azure | mixed_real | 16-22 | 4 | 1/4 (25%) | 1/4 (25%) | 2/4 (50%) |
| whisper-small | alone | 0-0.01 | 7 | 0/7 (0%) | 0/7 (0%) | 4/7 (57%) |
| whisper-small | same_voice | 2-4 | 14 | 0/14 (0%) | 0/14 (0%) | 3/14 (21%) |
| whisper-small | same_voice | 7-11 | 21 | 7/21 (33%) | 7/21 (33%) | 9/21 (43%) |
| whisper-small | same_voice | 11-16 | 14 | 7/14 (50%) | 10/14 (71%) | 7/14 (50%) |
| whisper-small | same_voice | 22-30 | 7 | 1/7 (14%) | 6/7 (86%) | 1/7 (14%) |
| whisper-small | diff_voice | 2-4 | 15 | 0/15 (0%) | 0/15 (0%) | 1/15 (7%) |
| whisper-small | diff_voice | 4-7 | 16 | 0/16 (0%) | 0/16 (0%) | 10/16 (62%) |
| whisper-small | diff_voice | 7-11 | 25 | 0/25 (0%) | 0/25 (0%) | 6/25 (24%) |
| whisper-small | diff_voice | 11-16 | 7 | 0/7 (0%) | 0/7 (0%) | 0/7 (0%) |
| whisper-small | diff_voice | 16-22 | 1 | 0/1 (0%) | 0/1 (0%) | 1/1 (100%) |
| whisper-small | diff_voice | 22-30 | 6 | 0/6 (0%) | 0/6 (0%) | 1/6 (17%) |
| whisper-small | mixed_real | 2-4 | 7 | 0/7 (0%) | 0/7 (0%) | 1/7 (14%) |
| whisper-small | mixed_real | 4-7 | 7 | 0/7 (0%) | 0/7 (0%) | 4/7 (57%) |
| whisper-small | mixed_real | 7-11 | 7 | 0/7 (0%) | 0/7 (0%) | 1/7 (14%) |
| whisper-small | mixed_real | 16-22 | 7 | 0/7 (0%) | 0/7 (0%) | 2/7 (29%) |
| whisper-small | mixed_real | 22-30 | 7 | 3/7 (43%) | 3/7 (43%) | 3/7 (43%) |

## B-3. take別: 単独clip(R00_alone)のASR結果分布(全エンジン・全rep、target領域転写)

| target | Prod判定(本番ログ) | engine | 転写の内訳(回数) |
|---|---|---|---|
| a2_att1 | Std OK take(Prod: Tier3 Azure=Melos said | openai | `mello said` x2 |
| a2_att1 | Std OK take(Prod: Tier3 Azure=Melos said | azure | `melos said` x2; `(nophrase)mellow said` x1 |
| a2_att1 | Std OK take(Prod: Tier3 Azure=Melos said | whisper-small | `mello said` x1 |
| a2_att1 | Std OK take(Prod: Tier3 Azure=Melos said | whisper-medium | `mellow said` x1 |
| a2_att2 | Std NG take(Prod: UNCERTAIN, Azure=Mello | openai | `mello said` x2 |
| a2_att2 | Std NG take(Prod: UNCERTAIN, Azure=Mello | azure | `mellow said` x2; `(nophrase)mellow said` x1 |
| a2_att2 | Std NG take(Prod: UNCERTAIN, Azure=Mello | whisper-small | `mello said` x1 |
| a2_att2 | Std NG take(Prod: UNCERTAIN, Azure=Mello | whisper-medium | `mellow said` x1 |
| a2_att3 | Std fallback take(Prod: Pattern A ACCEPT | openai | `mello said` x2 |
| a2_att3 | Std fallback take(Prod: Pattern A ACCEPT | azure | `melo said` x2; `(nophrase)melo said` x1 |
| a2_att3 | Std fallback take(Prod: Pattern A ACCEPT | whisper-small | `melo said` x1 |
| a2_att3 | Std fallback take(Prod: Pattern A ACCEPT | whisper-medium | `mellow said` x1 |
| a2_att4 | Std NG take(Prod ASR: 'Mellis said') | openai | `mellis said` x2 |
| a2_att4 | Std NG take(Prod ASR: 'Mellis said') | azure | `mallow said` x2; `(nophrase)mallow said` x1 |
| a2_att4 | Std NG take(Prod ASR: 'Mellis said') | whisper-small | `melo said` x1 |
| a2_att4 | Std NG take(Prod ASR: 'Mellis said') | whisper-medium | `mellow said` x1 |
| a2_att5 | Std NG take(Prod ASR: 'melloset' TTS_FAI | openai | `mellowset` x1; `melloset` x1 |
| a2_att5 | Std NG take(Prod ASR: 'melloset' TTS_FAI | azure | `melo said` x2; `(nophrase)melo said` x1 |
| a2_att5 | Std NG take(Prod ASR: 'melloset' TTS_FAI | whisper-small | `melo said` x1 |
| a2_att5 | Std NG take(Prod ASR: 'melloset' TTS_FAI | whisper-medium | `mellow said` x1 |
| a2_att6 | Std NG take(Prod ASR: 'Mellowset' TTS_FA | openai | `meloset` x2 |
| a2_att6 | Std NG take(Prod ASR: 'Mellowset' TTS_FA | azure | `mellow said` x2; `(nophrase)mellow said` x1 |
| a2_att6 | Std NG take(Prod ASR: 'Mellowset' TTS_FA | whisper-small | `melo said` x1 |
| a2_att6 | Std NG take(Prod ASR: 'Mellowset' TTS_FA | whisper-medium | `mellow set` x1 |
| b1b_att1 | Adv take(Prod: UNCERTAIN 'Mello said.';  | openai | `mello said` x1 |
| b1b_att1 | Adv take(Prod: UNCERTAIN 'Mello said.';  | azure | `mellow said` x2; `(nophrase)mellow said` x1 |
| b1b_att1 | Adv take(Prod: UNCERTAIN 'Mello said.';  | whisper-small | `mellow said` x1 |
| b1b_att1 | Adv take(Prod: UNCERTAIN 'Mello said.';  | whisper-medium | `mello said` x1 |

## B-4. 非決定性(同一音声・同一条件で2回呼出した結果の一致)

| engine | variant | 比較ペア数 | target領域転写が2回で一致 | 全文転写が一致 | 領域の判定(exact)が不一致 |
|---|---|---|---|---|---|
| openai | base | 205 | 148/205 (72%) | 114/205 (56%) | 17 |
| openai | prompt_word | 11 | 9/11 (82%) | 8/11 (73%) | 1 |
| openai | prompt_prev | 11 | 5/11 (45%) | 5/11 (45%) | 1 |
| azure | base | 15 | 15/15 (100%) | 15/15 (100%) | 0 |

## B-5. 誤認識の種類(target領域のfocus語トークンの内訳、Melos main、全文脈条件、base)

| engine | recipe群 | exact | spelling_variant | final_char_loss | extra_final_char | other/missing |
|---|---|---|---|---|---|---|
| openai | alone (n=13) | 0 | 11 | 0 | 2 | 0 |
| openai | 文脈あり(全て) (n=298) | 34 | 185 | 42 | 4 | 33 |
| azure | alone (n=14) | 2 | 6 | 4 | 0 | 2 |
| azure | 文脈あり(全て) (n=49) | 10 | 19 | 17 | 0 | 3 |
| whisper-small | alone (n=7) | 0 | 3 | 4 | 0 | 0 |
| whisper-small | 文脈あり(全て) (n=161) | 26 | 101 | 32 | 0 | 2 |

## E-3. ASRへ文脈情報を与える(OpenAI prompt) vs 与えない

| variant | recipe | n | exact_tokens | focus一致 | Prod PASS |
|---|---|---|---|---|---|
| base | R00_alone | 13 | 0/13 (0%) | 0/13 (0%) | 0/13 (0%) |
| base | Npre3 | 7 | 0/7 (0%) | 0/7 (0%) | 0/7 (0%) |
| prompt_word | R00_alone | 14 | 5/14 (36%) | 5/14 (36%) | 7/14 (50%) |
| prompt_word | Npre3 | 8 | 6/8 (75%) | 6/8 (75%) | 6/8 (75%) |
| prompt_prev | R00_alone | 14 | 3/14 (21%) | 3/14 (21%) | 5/14 (36%) |
| prompt_prev | Npre3 | 8 | 0/8 (0%) | 0/8 (0%) | 2/8 (25%) |
| azure base (PhraseList=Melos) | R00_alone | 14 | 2/14 (14%) | 2/14 (14%) | 6/14 (43%) |
| azure nophrase (PhraseList=なし) | R00_alone | 7 | 0/7 (0%) | 0/7 (0%) | 2/7 (29%) |

## D. 反例セット: 単独 vs 文脈結合(誤PASSリスク)

| group | engine | target群 | 条件 | n | 領域=canonical(exact_tokens) | Prod classify PASS(領域) | 全文Prod PASS |
|---|---|---|---|---|---|---|---|
| synthetic | openai | 全 | 単独 | 33 | 20/33 (61%) | 20/33 (61%) | 20/33 (61%) |
| synthetic | openai | 全 | 同一voice文脈 | 48 | 24/48 (50%) | 27/48 (56%) | 18/48 (38%) |
| synthetic | openai | 全 | 異voice文脈 | 44 | 25/44 (57%) | 26/44 (59%) | 26/44 (59%) |
| synthetic | azure | 全 | 単独 | 5 | 0/5 (0%) | 0/5 (0%) | 0/5 (0%) |
| natural_ng | openai | 全 | 単独 | 22 | 5/22 (23%) | 5/22 (23%) | 5/22 (23%) |
| natural_ng | openai | 全 | 同一voice文脈 | 38 | 15/38 (39%) | 15/38 (39%) | 15/38 (39%) |
| natural_ng | openai | 全 | 異voice文脈 | 8 | 2/8 (25%) | 2/8 (25%) | 2/8 (25%) |
| natural_ng | azure | 全 | 単独 | 11 | 6/11 (55%) | 7/11 (64%) | 7/11 (64%) |

### D-2. 反例target別(OpenAI、全rep・全文脈): 領域がcanonical一致した回数

| group | target | category/defect | 単独 PASS | 同voice文脈 PASS | 異voice文脈 PASS | 単独の転写例 |
|---|---|---|---|---|---|---|
| natural_ng | nat_bements | context_guessable_homophone / NG ASR 'Bements to protect.' | 1/2 (50%) | 3/3 (100%) | - | `be meant to protect`x1; `bement to protect`x1 |
| natural_ng | nat_counts | final_consonant_added / NG ASR 'Counts as success.' (+s) | 0/2 (0%) | 0/4 (0%) | - | `counts as success`x2 |
| natural_ng | nat_design | context_guessable_homophone / NG ASR '...fabric and design join forces' | 1/2 (50%) | 3/3 (100%) | 1/1 (100%) | `when fabric and design join forces`x1; `when fabric and drying join forces`x1 |
| natural_ng | nat_feet | context_guessable_homophone / NG ASR '...her feet is closing in' (context 'feed' | 1/2 (50%) | 3/3 (100%) | 1/1 (100%) | `another voice the reader who worries her feed is closing in`x1; `another voice the reader who worries her feet is closing in`x1 |
| natural_ng | nat_forced | final_consonant_added / NG ASR "Forced one's way through." (+d) | 2/2 (100%) | 4/4 (100%) | 0/1 (0%) | `force one's way through`x2 |
| natural_ng | nat_melus_hand | proper_noun_mispronounced / NG ASR "His friends took Melus's hand" | 0/2 (0%) | 0/4 (0%) | 0/1 (0%) | `his friends took melis's hand his fingers were warm and steady`x2 |
| natural_ng | nat_milo | proper_noun_mispronounced / NG ASR 'Milo spoke' | 0/2 (0%) | 0/4 (0%) | 0/1 (0%) | `the guards went still when milo spoke`x2 |
| natural_ng | nat_milos_hand | proper_noun_mispronounced / NG ASR "Milos's hand" (+friends') | 0/2 (0%) | 0/4 (0%) | 0/1 (0%) | `his friend's warm steady fingers closed around milos' hand`x2 |
| natural_ng | nat_paused | final_consonant_added / NG ASR 'Paused the feature.' (+d) | 0/2 (0%) | 2/4 (50%) | - | `paused the feature`x2 |
| natural_ng | nat_reduce | final_consonant_drop / NG ASR 'reduce the feeling of connection.' (-d dro | 0/2 (0%) | 0/4 (0%) | 0/1 (0%) | `reduce the feeling of connection`x2 |
| natural_ng | nat_turnout | content_mispronounced / NG ASR 'Turn out not today.' | 0/2 (0%) | 0/1 (0%) | 0/1 (0%) | `turn out not today`x2 |
| synthetic | ctl_B1_intact | intact_control / none (unmodified base) | 0/1 (0%) | 0/2 (0%) | 0/2 (0%) | `mallow said`x1 |
| synthetic | ctl_B2_intact | intact_control / none (unmodified base) | 1/1 (100%) | 2/2 (100%) | 2/2 (100%) | `the ruler smiled and said`x1 |
| synthetic | ctl_B4_intact | intact_control / none (unmodified base) | 1/1 (100%) | 2/2 (100%) | 2/2 (100%) | `silence came and guards grabbed the young shepherd the ruler ordered his death`x1 |
| synthetic | sweep_B2_trunc300 | synthetic_final_consonant_loss / last 300 ms of speech removed (speech_end=2.57s),  | 2/2 (100%) | 1/1 (100%) | 1/1 (100%) | `the ruler smiled and said`x2 |
| synthetic | sweep_B2_trunc380 | synthetic_final_consonant_loss / last 380 ms of speech removed (speech_end=2.57s),  | 2/2 (100%) | 1/1 (100%) | 1/1 (100%) | `the ruler smiled and said`x2 |
| synthetic | sweep_B2_trunc460 | synthetic_final_consonant_loss / last 460 ms of speech removed (speech_end=2.57s),  | 2/2 (100%) | 1/1 (100%) | 1/1 (100%) | `the ruler smiled and said`x2 |
| synthetic | syn_B1_dropmelos | synthetic_missing_word / word 'Melos' removed (azure word ts: melos 0.35-0. | 0/2 (0%) | 0/3 (0%) | 0/3 (0%) | `said`x2 |
| synthetic | syn_B1_dropsaid | synthetic_missing_word / word 'said' removed (azure word ts: melos 0.35-0.7 | 0/2 (0%) | 0/3 (0%) | 0/3 (0%) | `mellos`x2 |
| synthetic | syn_B1_trunc140 | synthetic_final_consonant_loss / last 140 ms of speech removed (speech_end=1.37s),  | 0/2 (0%) | 0/3 (0%) | 1/3 (33%) | `mello said`x2 |
| synthetic | syn_B1_trunc220 | synthetic_final_consonant_loss / last 220 ms of speech removed (speech_end=1.37s),  | 0/2 (0%) | 1/3 (33%) | 0/3 (0%) | `mello said`x2 |
| synthetic | syn_B1_trunc70 | synthetic_final_consonant_loss / last 70 ms of speech removed (speech_end=1.37s), f | 0/2 (0%) | 1/3 (33%) | 0/3 (0%) | `mello said`x2 |
| synthetic | syn_B2_trunc140 | synthetic_final_consonant_loss / last 140 ms of speech removed (speech_end=2.57s),  | 2/2 (100%) | 3/3 (100%) | 3/3 (100%) | `the ruler smiled and said`x2 |
| synthetic | syn_B2_trunc220 | synthetic_final_consonant_loss / last 220 ms of speech removed (speech_end=2.57s),  | 2/2 (100%) | 3/3 (100%) | 3/3 (100%) | `the ruler smiled and said`x2 |
| synthetic | syn_B2_trunc70 | synthetic_final_consonant_loss / last 70 ms of speech removed (speech_end=2.57s), f | 2/2 (100%) | 3/3 (100%) | 3/3 (100%) | `the ruler smiled and said`x2 |
| synthetic | syn_B4_trunc140 | synthetic_final_consonant_loss / last 140 ms of speech removed (speech_end=7.03s),  | 2/2 (100%) | 3/3 (100%) | 3/3 (100%) | `silence came and guards grabbed the young shepherd the ruler ordered his death`x2 |
| synthetic | syn_B4_trunc220 | synthetic_final_consonant_loss / last 220 ms of speech removed (speech_end=7.03s),  | 2/2 (100%) | 3/3 (100%) | 3/3 (100%) | `silence came and guards grabbed the young shepherd the ruler ordered his death`x2 |
| synthetic | syn_B4_trunc70 | synthetic_final_consonant_loss / last 70 ms of speech removed (speech_end=7.03s), f | 2/2 (100%) | 3/3 (100%) | 3/3 (100%) | `silence came and guards grabbed the young shepherd the ruler ordered his death`x2 |
| synthetic | syn_name_ruler | synthetic_wrong_name / first word replaced by 'ruler' (spliced from anoth | 0/2 (0%) | 0/6 (0%) | 0/2 (0%) | `rulers said`x2 |

### D-3. false accept(既知欠陥を含むsynthetic音声が、文脈付きASRでcanonical一致扱い)と防止条件の評価

| engine | 条件 | n | false accept (領域Prod PASS) | strict一致(EXACT/NORMALIZED) |
|---|---|---|---|---|
| openai | 単独 | 33 | 20/33 (61%) | 20/33 (61%) |
| openai | 文脈あり | 92 | 53/92 (58%) | 49/92 (53%) |
| azure | 単独 | 5 | 0/5 (0%) | 0/5 (0%) |
| whisper-small | 単独 | 18 | 14/18 (78%) | 11/18 (61%) |
| whisper-small | 文脈あり | 80 | 60/80 (75%) | 53/80 (66%) |

### D-4. 単独ではNGなのに文脈付きでPASSに反転した観測(flip = false accept候補)

| label | engine | 単独NGのtarget数 | 文脈付き観測数(単独NG target) | うちPASS反転 | 反転したtarget:recipe |
|---|---|---|---|---|---|
| known_defect_word | openai | 3 | 20 | 0 |  |
| known_defect_word | azure | 2 | 0 | 0 |  |
| known_defect_word | whisper-small | 3 | 14 | 0 |  |
| natural_ng_proxy | openai | 10 | 41 | 13 | nat_bements:SSpost, nat_bements:SSpre, nat_design:SDpre, nat_design:SSpost, nat_design:SSpre, nat_feet:SDpre, nat_feet:SSpost, nat_feet:SSpr |
| natural_ng_proxy | azure | 4 | 0 | 0 |  |
| natural_ng_proxy | whisper-small | 5 | 18 | 0 |  |

### D-4b. (委任_02追加) natural_ng_proxy(OpenAI)のPASS反転観測をtarget別に集計(D-4の単位=全rep観測。D-5のG0=target x recipe単位[rep1のみ]で母集団が異なる)

| target | 単独 | 文脈付き観測数 | 反転(PASS)観測数 |
|---|---|---|---|
| nat_bements | NG | 3 | 3 |
| nat_counts | NG | 4 | 0 |
| nat_design | NG | 4 | 4 |
| nat_feet | NG | 4 | 4 |
| nat_forced | PASS | 5 | 4 |
| nat_melus_hand | NG | 5 | 0 |
| nat_milo | NG | 5 | 0 |
| nat_milos_hand | NG | 5 | 0 |
| nat_paused | NG | 4 | 2 |
| nat_reduce | NG | 5 | 0 |
| nat_turnout | NG | 2 | 0 |

単独NG target合計: 文脈付き観測 41件、反転 13件(D-4と同一母集団)。

### D-5. false accept防止条件の評価(OpenAI文脈付きASRを一次、条件を重ねたときの受理数)

| 条件 | known_defect_word(語欠落/誤語) 受理=false accept | known_defect_trunc(語末切詰) 受理=false accept | good_control 受理=true accept | natural_ng_proxy 受理 |
|---|---|---|---|---|
| G0 文脈付きOpenAI領域が受理(無対策。受理=切詰/対照synthetic[category]は最終語の綴り一致[focus_exact]、それ以外はProduction classify_asr_match PASS) | 0/12 (0%) | 42/42 (100%) | 12/12 (100%) | 13/36 (36%) |
| G1 +単独clipもPASS(単独整合) | 0/12 (0%) | 42/42 (100%) | 12/12 (100%) | 3/36 (8%) |
| G2 +2回呼出し両方PASS | 0/8 (0%) | 18/18 (100%) | - | 4/10 (40%) |
| G3a +領域token min logprob >= -0.5 | 0/12 (0%) | 35/42 (83%) | 11/12 (92%) | 11/36 (31%) |
| G3b +領域token min logprob >= -1.5 | 0/12 (0%) | 42/42 (100%) | 12/12 (100%) | 11/36 (31%) |
| G4 +独立engine(whisper-small, 領域timestamp)もPASS | 0/12 (0%) | 42/42 (100%) | 12/12 (100%) | 12/36 (33%) |
| G5 +単独整合 かつ whisperもPASS | 0/12 (0%) | 42/42 (100%) | 12/12 (100%) | 2/36 (6%) |

### D-6. 語末子音を切り詰めた既知欠陥音声(synthetic)の単独ASR(OpenAI/whisper-small/Azure)

| target | defect | OpenAI単独 | Azure単独 | whisper単独 |
|---|---|---|---|---|
| ctl_B1_intact | none (unmodified base) | `mallow said`(P) | - | `mello said`(P) |
| ctl_B2_intact | none (unmodified base) | `the ruler smiled and said`(P) | - | `the ruler smiled and said`(P) |
| ctl_B4_intact | none (unmodified base) | `silence came and guards grabbed the young shepherd the ruler ordered his death`(P) | - | `silence came and guards grabbed the young shepherd the ruler ordered his death`(P) |
| sweep_B2_trunc300 | last 300 ms of speech removed (speech_end=2.5 | `the ruler smiled and said`(P); `the ruler smiled and said`(P) | - | `the ruler smiled and said`(P) |
| sweep_B2_trunc380 | last 380 ms of speech removed (speech_end=2.5 | `the ruler smiled and said`(P); `the ruler smiled and said`(P) | - | `the ruler smiled and said`(P) |
| sweep_B2_trunc460 | last 460 ms of speech removed (speech_end=2.5 | `the ruler smiled and said`(P); `the ruler smiled and said`(P) | - | `the ruler smiled and said`(P) |
| syn_B1_dropmelos | word 'Melos' removed (azure word ts: melos 0. | `said`(NG); `said`(NG) | `said`(NG) | `said`(NG) |
| syn_B1_dropsaid | word 'said' removed (azure word ts: melos 0.3 | `mellos`(NG); `mellos`(NG) | `mellows`(NG) | `melo's`(NG) |
| syn_B1_trunc140 | last 140 ms of speech removed (speech_end=1.3 | `mello said`(P); `mello said`(P) | `mellow said`(P) | `melo said`(P) |
| syn_B1_trunc220 | last 220 ms of speech removed (speech_end=1.3 | `mello said`(P); `mello said`(P) | `mellow said`(P) | `melo said`(P) |
| syn_B1_trunc70 | last 70 ms of speech removed (speech_end=1.37 | `mello said`(P); `mello said`(P) | `mellow said`(P) | `melo said`(P) |
| syn_B2_trunc140 | last 140 ms of speech removed (speech_end=2.5 | `the ruler smiled and said`(P); `the ruler smiled and said`(P) | - | `the ruler smiled and said`(P) |
| syn_B2_trunc220 | last 220 ms of speech removed (speech_end=2.5 | `the ruler smiled and said`(P); `the ruler smiled and said`(P) | - | `the ruler smiled and said`(P) |
| syn_B2_trunc70 | last 70 ms of speech removed (speech_end=2.57 | `the ruler smiled and said`(P); `the ruler smiled and said`(P) | - | `the ruler smiled and said`(P) |
| syn_B4_trunc140 | last 140 ms of speech removed (speech_end=7.0 | `silence came and guards grabbed the young shepherd the ruler ordered his death`(P); `silence came and guards grabbed the young shepherd the ruler ordered his death`(P) | - | `silence came and guards grabbed the young shepherd the ruler ordered his death`(P) |
| syn_B4_trunc220 | last 220 ms of speech removed (speech_end=7.0 | `silence came and guards grabbed the young shepherd the ruler ordered his death`(P); `silence came and guards grabbed the young shepherd the ruler ordered his death`(P) | - | `silence came and guards grabbed the young shepherd the ruler ordered his death`(P) |
| syn_B4_trunc70 | last 70 ms of speech removed (speech_end=7.03 | `silence came and guards grabbed the young shepherd the ruler ordered his death`(P); `silence came and guards grabbed the young shepherd the ruler ordered his death`(P) | - | `silence came and guards grabbed the young shepherd the ruler ordered his death`(P) |
| syn_name_ruler | first word replaced by 'ruler' (spliced from  | `rulers said`(NG); `rulers said`(NG) | - | `rulers said`(NG) |

### 処理時間(ASR 1呼出あたり秒、中央値)

| engine | 音声長 | 中央値秒 | n |
|---|---|---|---|
| openai | 0-3s | 0.41 | 79 |
| openai | 3-8s | 0.48 | 219 |
| openai | 8-16s | 0.58 | 196 |
| openai | 16-40s | 0.96 | 54 |
| azure | 0-3s | 0.60 | 32 |
| azure | 3-8s | 1.00 | 32 |
| azure | 8-16s | 2.40 | 18 |
| azure | 16-40s | 7.61 | 4 |
| whisper-small | 0-3s | 2.84 | 27 |
| whisper-small | 3-8s | 3.04 | 122 |
| whisper-small | 8-16s | 3.52 | 133 |
| whisper-small | 16-40s | 5.02 | 31 |

### D-7. OpenAI target領域token logprob(min)の分布: 領域PASS観測のうち good_control vs known_defect vs Melos

| label | PASS観測n | min_logprob 中央値 | 5%点 | 最小 |
|---|---|---|---|---|
| good_control | 15 | -0.01 | -2.48 | -2.48 |
| known_defect_trunc | 84 | -0.01 | -1.00 | -1.38 |
| natural_ng_proxy | 22 | -0.07 | -2.53 | -2.82 |

### C-2. 文脈clipに作品固有語(Melos)が含まれるか否かの効果(Melos main, base, 文脈あり条件のみ)

| engine | 文脈にMelos語を含む | n | focus(Melos)一致 | exact_tokens | Prod PASS |
|---|---|---|---|---|---|
| openai | 含まない | 234 | 18/234 (8%) | 18/234 (8%) | 50/234 (21%) |
| openai | 含む | 64 | 16/64 (25%) | 15/64 (23%) | 25/64 (39%) |
| azure | 含まない | 49 | 10/49 (20%) | 10/49 (20%) | 27/49 (55%) |
| whisper-small | 含まない | 126 | 0/126 (0%) | 0/126 (0%) | 32/126 (25%) |
| whisper-small | 含む | 35 | 26/35 (74%) | 18/35 (51%) | 18/35 (51%) |

### B-6. 領域抽出の整合性: timestamp領域(Azure/whisper) と 文字列整列領域の一致率

| engine | 文脈あり観測数 | 領域が一致 |
|---|---|---|
| azure | 49 | 49/49 (100%) |
| whisper-small | 277 | 255/277 (92%) |
| whisper-medium | 28 | 28/28 (100%) |

### D-8. 語末子音を切り詰めた既知欠陥(B2『The ruler smiled and said,』)のASR結果: 切り詰め量別

| 切り詰め(ms) | engine | 条件 | 領域転写 | Prod判定 |
|---|---|---|---|---|
| 0 | openai | R00_alone | `the ruler smiled and said` | P |
| 0 | openai | SSpre | `the ruler smiled and said` | P |
| 0 | openai | SDpre | `the ruler smiled and said` | P |
| 0 | whisper-small | R00_alone | `the ruler smiled and said` | P |
| 0 | whisper-small | SSpre | `the ruler smiled and said` | P |
| 0 | whisper-small | SDpre | `ruler smiled and said` | P |
| 70 | openai | R00_alone | `the ruler smiled and said`; `the ruler smiled and said` | P; P |
| 70 | openai | SSpre | `the ruler smiled and said`; `the rulers smiled and said` | P; P |
| 70 | openai | SDpre | `the ruler smiled and said`; `the ruler smiled and said` | P; P |
| 70 | whisper-small | R00_alone | `the ruler smiled and said` | P |
| 70 | whisper-small | SSpre | `the ruler smiled and said` | P |
| 70 | whisper-small | SDpre | `ruler smiled and said` | P |
| 140 | openai | R00_alone | `the ruler smiled and said`; `the ruler smiled and said` | P; P |
| 140 | openai | SSpre | `the rulers smiled and said`; `the ruler smiled and said` | P; P |
| 140 | openai | SDpre | `the ruler smiled and said`; `the ruler smiled and said` | P; P |
| 140 | whisper-small | R00_alone | `the ruler smiled and said` | P |
| 140 | whisper-small | SSpre | `the ruler smiled and said` | P |
| 140 | whisper-small | SDpre | `ruler smiled and said` | P |
| 220 | openai | R00_alone | `the ruler smiled and said`; `the ruler smiled and said` | P; P |
| 220 | openai | SSpre | `the ruler smiled and said`; `the ruler smiled and said` | P; P |
| 220 | openai | SDpre | `the ruler smiled and said`; `the ruler smiled and said` | P; P |
| 220 | whisper-small | R00_alone | `the ruler smiled and said` | P |
| 220 | whisper-small | SSpre | `the ruler smiled and said` | P |
| 220 | whisper-small | SDpre | `ruler smiled and said` | P |
| 300 | openai | R00_alone | `the ruler smiled and said`; `the ruler smiled and said` | P; P |
| 300 | openai | SSpre | `the rulers smiled and said` | P |
| 300 | openai | SDpre | `the ruler smiled and said` | P |
| 300 | whisper-small | R00_alone | `the ruler smiled and said` | P |
| 300 | whisper-small | SSpre | `the ruler smiled and said` | P |
| 300 | whisper-small | SDpre | `ruler smiled and said` | P |
| 380 | openai | R00_alone | `the ruler smiled and said`; `the ruler smiled and said` | P; P |
| 380 | openai | SSpre | `the ruler smiled and said` | P |
| 380 | openai | SDpre | `the ruler smiled and said` | P |
| 380 | whisper-small | R00_alone | `the ruler smiled and said` | P |
| 380 | whisper-small | SSpre | `the ruler smiled and said` | P |
| 380 | whisper-small | SDpre | `ruler smiled and said` | P |
| 460 | openai | R00_alone | `the ruler smiled and said`; `the ruler smiled and said` | P; P |
| 460 | openai | SSpre | `the ruler smiled and said` | P |
| 460 | openai | SDpre | `the ruler smiled and said` | P |
| 460 | whisper-small | R00_alone | `the ruler smiled and said` | P |
| 460 | whisper-small | SSpre | `the ruler smiled and said` | P |
| 460 | whisper-small | SDpre | `ruler smiled and said` | P |

### D-9. 誤った語(Melos→ruler)に差し替えた既知欠陥: 文脈に正しい名前『Melos』が有る/無いとき

| 条件 | engine | 領域転写 | Prod判定 |
|---|---|---|---|
| R00_alone | openai | `rulers said`; `rulers said` | NG; NG |
| R00_alone | whisper-small | `rulers said` | NG |
| NMpre_name3 | openai | `rulers said`; `rulers said` | NG; NG |
| NMpre_name3 | whisper-small | `rulers said` | NG |
| NMpre_name14 | openai | `rulers said`; `rulers said` | NG; NG |
| NMpre_name14 | whisper-small | `rulers said` | NG |
| NMpre_noname7 | openai | `rulers said`; `rulers said` | NG; NG |
| NMpre_noname7 | whisper-small | `rulers said` | NG |
| NMpre_diffvoice | openai | `rulers said`; `rulers said` | NG; NG |
| NMpre_diffvoice | whisper-small | `rulers said` | NG |

### C-3. 同じ付加秒数での 同一ナレーター文脈 vs 異ナレーター文脈 (前置文脈、Melos main、base)

| 付加秒(約) | 同一voice recipe(秒) | 異voice recipe(秒) | engine | 同一voice: Prod PASS / focus一致 | 異voice: Prod PASS / focus一致 |
|---|---|---|---|---|---|
| 3s | Npre3(2.2) | Dpre3(2.7) | openai | 2/13 (15%) / 0/13 (0%) | 0/13 (0%) / 0/13 (0%) |
| 3s | Npre3(2.2) | Dpre3(2.7) | azure | 6/11 (55%) / 2/11 (18%) | 2/7 (29%) / 1/7 (14%) |
| 3s | Npre3(2.2) | Dpre3(2.7) | whisper-small | 3/7 (43%) / 0/7 (0%) | 1/7 (14%) / 0/7 (0%) |
| 7-8s | Npre8(7.6) | Dpre8(5.5) | openai | 3/13 (23%) / 0/13 (0%) | 1/13 (8%) / 0/13 (0%) |
| 7-8s | Npre8(7.6) | Dpre8(5.5) | azure | 2/4 (50%) / 1/4 (25%) | 3/4 (75%) / 1/4 (25%) |
| 7-8s | Npre8(7.6) | Dpre8(5.5) | whisper-small | 1/7 (14%) / 0/7 (0%) | 5/7 (71%) / 0/7 (0%) |
| 13s | Npre14(14.4) | Dpre14(12.3) | openai | 6/13 (46%) / 0/13 (0%) | 5/13 (38%) / 1/13 (8%) |
| 13s | Npre14(14.4) | Dpre14(12.3) | whisper-small | 4/7 (57%) / 7/7 (100%) | 0/7 (0%) / 0/7 (0%) |
| 23-26s | Npre27(23.8) | Dpre25(20.5) | openai | 5/13 (38%) / 2/13 (15%) | 9/13 (69%) / 4/13 (31%) |
| 23-26s | Npre27(23.8) | Dpre25(20.5) | whisper-small | 1/7 (14%) / 6/7 (86%) | 2/7 (29%) / 0/7 (0%) |

### C-4. Standard(a2) vs Advanced(b1b): 同一recipe・OpenAI/Azure/whisper (base)

| recipe | engine | Std a2(6take) Prod PASS | Adv b1b(1take) Prod PASS |
|---|---|---|---|
| R00_alone | openai | 0/12 (0%) | 0/1 (0%) |
| R00_alone | azure | 6/12 (50%) | 0/2 (0%) |
| R00_alone | whisper-small | 4/6 (67%) | 0/1 (0%) |
| Npre3 | openai | 2/12 (17%) | 0/1 (0%) |
| Npre3 | azure | 4/9 (44%) | 2/2 (100%) |
| Npre3 | whisper-small | 3/6 (50%) | 0/1 (0%) |
| Dpre3 | openai | 0/12 (0%) | 0/1 (0%) |
| Dpre3 | azure | 2/6 (33%) | 0/1 (0%) |
| Dpre3 | whisper-small | 1/6 (17%) | 0/1 (0%) |
| Rboth | openai | 6/12 (50%) | 0/1 (0%) |
| Rboth | azure | 5/9 (56%) | 2/2 (100%) |
| Rboth | whisper-small | 1/6 (17%) | 0/1 (0%) |
| Rwin5 | openai | 5/12 (42%) | 0/1 (0%) |
| Rwin5 | azure | 2/3 (67%) | 0/1 (0%) |
| Rwin5 | whisper-small | 2/6 (33%) | 0/1 (0%) |

### D-10. Melos各take(本番判定つき): 単独ASRと文脈付きASRの比較(OpenAI。単独で『Melos said』にならないtakeが文脈で『Melos said』と書かれる=masking候補)

| target | 本番判定 | OpenAI単独の領域転写 | 文脈付き観測数 | 『melos said』一致 | Prod classify PASS(CS受理含む) | 『melos said』になったrecipe |
|---|---|---|---|---|---|---|
| a2_att1 | Std OK take(Prod: Tier3 Azure=Melo | mello said | 46 | 4 | 6 | Dpre6, Npost8, Rwin7 |
| a2_att2 | Std NG take(Prod: UNCERTAIN, Azure | mello said | 46 | 1 | 23 | Rwin7 |
| a2_att3 | Std fallback take(Prod: Pattern A  | mello said | 46 | 3 | 9 | Dpre25, Rwin7 |
| a2_att4 | Std NG take(Prod ASR: 'Mellis said | mellis said | 46 | 5 | 7 | Npost8, Npre27, Rwin7 |
| a2_att5 | Std NG take(Prod ASR: 'melloset' T | melloset; mellowset | 46 | 3 | 7 | Dpre25, Rwin7 |
| a2_att6 | Std NG take(Prod ASR: 'Mellowset'  | meloset | 45 | 17 | 20 | Dboth, Dpre11, Dpre14, Dpre25, Dpre5, Dpre6, Npost8, Npre27, Rboth, Rpre, Rwin5 |
| b1b_att1 | Adv take(Prod: UNCERTAIN 'Mello sa | mello said | 23 | 0 | 3 |  |

### C-2b. (委任_02追加) C-2をa2_att6除外で再集計(Melos main, base, 文脈あり条件のみ。att6は文脈付き『melos said』の真値が未確定のため分離)

| engine | 文脈にMelos語を含む | n(att6除外) | focus(Melos)一致 | exact_tokens | Prod PASS |
|---|---|---|---|---|---|
| openai | 含まない | 198 | 3/198 (2%) | 3/198 (2%) | 34/198 (17%) |
| openai | 含む | 55 | 13/55 (24%) | 13/55 (24%) | 21/55 (38%) |
| azure | 含まない | 39 | 10/39 (26%) | 10/39 (26%) | 25/39 (64%) |
| whisper-small | 含まない | 108 | 0/108 (0%) | 0/108 (0%) | 25/108 (23%) |
| whisper-small | 含む | 30 | 22/30 (73%) | 15/30 (50%) | 15/30 (50%) |

### C-2c. (委任_02追加) a2_att6のOpenAI文脈付き『melos said』(exact_tokens)観測の内訳: 文脈clipに『Melos』語を含むか / recipe別

- att6 文脈付き観測 45件、うち『melos said』 17件。このうち ctx_has_focus_word=true は 2件、false は 15件。
- 『melos said』になったdistinct recipe 11件: Dboth(ctx_has_focus=F, x2), Dpre11(ctx_has_focus=F, x2), Dpre14(ctx_has_focus=F, x1), Dpre25(ctx_has_focus=F, x2), Dpre5(ctx_has_focus=F, x1), Dpre6(ctx_has_focus=F, x1), Npost8(ctx_has_focus=T, x1), Npre27(ctx_has_focus=T, x1), Rboth(ctx_has_focus=F, x2), Rpre(ctx_has_focus=F, x2), Rwin5(ctx_has_focus=F, x2)
- distinct recipeのうち ctx_has_focus_word=false は 9/11

### C-2d. (委任_02追加) Dpre25(異voice前置25秒)の各take(OpenAI, base)

- a2_att1: n=2, ctx_has_focus=False, 転写=['mello said', 'melo said'], melos said=0
- a2_att2: n=2, ctx_has_focus=False, 転写=['melo said'], melos said=0
- a2_att3: n=2, ctx_has_focus=False, 転写=['melo said', 'melos said'], melos said=1
- a2_att4: n=2, ctx_has_focus=False, 転写=['malice said'], melos said=0
- a2_att5: n=2, ctx_has_focus=False, 転写=['melo said', 'melos said'], melos said=1
- a2_att6: n=2, ctx_has_focus=False, 転写=['melos said'], melos said=2
- b1b_att1: n=1, ctx_has_focus=False, 転写=['mello said'], melos said=0
