# ROOT_CAUSE_01: 『開いた窓』Bertie→Birdie HR Lock の根本原因(①固有名詞)

管理ID: ASR-QUALITY-2ITEMS-COMPREHENSIVE-01-PN 委任_01 / 2026-10-23 / Status: ROOT_CAUSE_DESIGN_IN_PROGRESS(read-only調査。Production/Prompt/flag/閾値/Ledger変更0、`upsert`/`--apply`/HR Lock解除/run_sf_prod_01 stage実行0、個別登録0)
ユーザー指示原文: docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_USER.md(逐語保存済み、commit faa7c34bc)
数値の根拠scriptと結果JSONは本フォルダ(`quant_*_01.py`/`*_result.json`/`quant_summary_01_output.txt`/`exposure_corpus_01.py`/`article_entity_scan_01.py`/`ner_probe_01.py`/`phonetic_gate_probe_01.py`)。API費用=LLM NER小規模実測のみ 0.5767円(gpt-6-luna、22本文、設計入力。`ner_probe_01_usage.jsonl`)。

## 0. 結論(先に)

**根本原因は「固有名詞を“認識する”仕組みが1つの正本を持たず、HRへ入れる側(緩い)と救済する側(厳しい)で定義が食い違い、救済側の証拠源が『人手/事後のLedger』『CMU辞書に無い語』『文中の大文字』という代理指標に限られていたこと」**である。Bertie は英語の一般的な人名で CMU 辞書に載っており、台帳に無く、本文では歌詞の引用符の直後(1回)と文頭(1回)にしか現れない。そのため、救済側(PNAP)は全ての証拠を満たせず `NO_PROPER_NOUN_EVIDENCE` で不受理になり、通常のASR判定(NG_BOTH)がそのまま HR Lock になった。個別のBertie登録は症状への対処にしかならず、同じ構造(CMU収録の人名/組織名 × 文頭・引用直後)は次の作品・記事で必ず再発する。

「承認済み仕様が機能しなかった」理由は、承認(2026-10-22)の文言ではなく**証拠規則の実装範囲**にある(§4 RC-1〜RC-4)。

## 1. 事象の事実(Bertie、run_sf_prod_01、2026-10-23)

| 項目 | 値(根拠) |
|---|---|
| 停止 clip | a2/b1b 各2: `full_story_part1_c14`(`... sang, 'Bertie, why do you bound?' He always ...`)・`full_story_part3_c2`(`"Bertie, why do you bound?"`)。`er026_output/family_z_production_e2e_01/the_open_window/run_sf_prod_01/{a2,b1b}/audit/tts_generation_results.json`(status=STOPPED) |
| ASR | 全attempt・Primary(gpt-4o-mini-transcribe)/Secondary(Azure)とも `Birdie`(part3_c2: 3attempt中 attempt2/3 が `Birdie, why do you bound?`=差分は Bertie→Birdie の1語のみ、分類=`ASR_VALIDATION_UNCERTAIN`) |
| 台本中の出現 | `writer/std.md:19`・`r2.md:19` の `‘Bertie, why do you bound?’` の1箇所のみ(歌詞)。Seed `source_essentials.key_roles` には Framton/Vera のみで Bertie は無い |
| Ledger | `er006_output/pronunciation_ledger_01/ledger.json` 39 entry に `bertie` なし(BERTIE_LEDGER_CANDIDATE_01.md §1) |
| HR queue | `er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl` の行118・120・121(2026-10-23): いずれも Primary差分 `[('bertie','birdie',entity_like=True)]`、`entity_like_source=["capitalized"]`、`pronunciation_lookups.bertie` は `confidence=unconfirmed / evidence_tier=NO_SOURCE`(調査が結果を返さなかった) |
| PNAP判定 | 同3行を現行 `er103.evaluate_alarm_eligibility` で再評価(`quant_hr_queue_01.py`): `NO_PROPER_NOUN_EVIDENCE`、`detail={'token':'bertie'}`。Ledgerに `bertie` を仮に足せば受理(`_noun_checks` 単体で類似度0.667、BERTIE_LEDGER_CANDIDATE_01.md §4) |
| 調査(Perplexity) | tts_a2 で発音調査17 call が401失敗(PHASE4_RESULT_01.md:43)。**この環境では「事後のLedger登録」経路自体が働かない**(本調査では再現のためのAPI呼出は行っていない) |

重要な観察: **“Bertie が固有名詞らしい”ことはシステムの別の部分は既に判っていた**。`val.capitalized_flags`(`er006_preprod_hardening_01_validation.py:485-509`)は文頭語も含め大文字始まり語を entity 候補にし、だから Bertie→Birdie は `TRUE_CONTENT_MISMATCH`(再試行)ではなく `ASR_VALIDATION_UNCERTAIN`(HR行き)に分類された。救済側 `proper_noun_evidence`(`er103_proper_noun_alarm_policy_01.py:167-229`)だけが同じ語を「固有名詞の証拠なし」と扱った。

## 2. 判定連鎖と各段の責務(現行)

1. TTS→ASR Primary(OpenAI)→分類 `classify_asr_match`(val)。差分が「大文字始まり語/外来語(+Ledger[既定OFF])」だけなら `entity_like`=True(=緩い定義、`val:485-509,1155`)。
2. 救済層(Case A/homophone/M1/CS等価/er109 orthographic/多語同音)→ Secondary(Azure)→ 統一judge(er078)。全部通ってもNGなら `NG_BOTH/secondary_not_accepted`。
3. **PNAP(er103、最終救済・追加API 0)**: `_pnap_try_accept`(`er006_secondary_asr_01.py:823`、呼出 :1280付近)→`evaluate_for_adapter`→`evaluate_alarm_eligibility`(er103:293-)。G5 の固有名詞根拠 `proper_noun_evidence`(=厳しい定義、er103:167-229)を、Ledger surface 集合(`ledger_surface_tokens` er103:697-712)・CMU・文脈で判定。
4. 受理されなければ最終slotで `human_review_required`→HR queue/HR Lock。HRの表示用に `_resolve_unresolved_entity_for_review`(Stage 1調査→**調査が成功した場合のみ** Ledger upsert、er006_secondary_asr_01.py:347-390、呼出 :1293-1314)が**この時点で初めて**走る。
5. HR Lock後の保存転写再評価(`er109_hr_lock_rejudge_01`・`er019_family_x_validation_inheritance_01.py:349-352`)は、元状態が `PASS_WITH_PRONUNCIATION_ALARM` の音声だけが対象。元が NG_BOTH の clip は Ledger に後から証拠を足しても救えず、**有料の再生成**が必要(BERTIE_LEDGER_CANDIDATE_01.md §4。今回実測 `NOT_CANDIDATE` 2件)。

`proper_noun_evidence` の証拠は 5 つだけ(er103:176-229): ①Ledger登録surface ②CMU未収録語 ③単独ALLCAPS ④文中の大文字始まり(ただし CMU収録語は「文頭・コロン/引用符/括弧の直後・Title Case一般語連なり・role=TOPIC_INTRO」では不可 = OF-PNAP-P-02、er103:200-206) ⑤TTS供給で綴り置換済みの語。**Bertie はCMU収録(zipf 3.08)で台帳なし、出現位置は引用符直後と文頭 → ①〜⑤すべて不成立**。

## 3. 設計時の想定との照合(設計上の前提の欠落)

| 設計時の記述 | 実際 |
|---|---|
| IMPLEMENTATION_DESIGN_01.md §2-2: 「**文頭の大文字だけ(CMU収録語)は根拠にしない**」、§2-3: 「文頭のCMU収録ブランド(Meta/Apple)はLedger未登録だとHR残(**取りこぼし側=安全**)」 | 取りこぼし側を意図して受容していた。ただし評価対象は「ブランド名(Meta/Apple)」「学者名」で、**英語の一般的な人名(Bertie/Vera)・小説の登場人物**の頻度は見積もられていない(Family Zの本命用途)。Opus条件AレビューのP-02(`OPUS_REVIEW_COND_A_01.md`)も“一般語をTitle Caseで固有名詞扱いする誤受理”の防止観点で、“固有名詞を取りこぼす”側の定量評価は無い |
| 校正データ=HR queue 88イベント(INVESTIGATION_01.md §3、校正受理45件=51%) | 88イベントは**過去にHR化した語**で構成される。HR化した語はStage 1調査により Ledger に反応登録される(`cascade_unresolved_entity` 21 entry)ため、**校正データ自体がLedger証拠を持つ語に偏っている**(後述 §5: Ledger全除外=初見語再現で受理41→36、不受理B類 3→9)。“初めて見る語”を評価に含めない設計だった |
| P-09/ALARM_ACCEPT_MIN_SLOT=1(初回attemptで受理) | Bertie は証拠不足のため slot の問題ではなく入口で不受理 |
| Ledger: 「Stage 1調査で事前/反応的に蓄積される」想定(INVESTIGATION_01.md §2) | 蓄積は**事後・調査成功依存**。今回は調査が401で空振りし、初見語に対しては原理的に間に合わない(PNAPは調査より前に走る) |
| 範囲: Family X/Zへ共通適用 | 証拠源としてZのSeed(`key_roles`、keep_name)もXのResearch Ledger/B3のentityも**一切参照していない**。X側のResearch Ledgerは日本語の fact/subject で英語固有名詞の一覧を持たない(`er019_output/ig_nobel_2026/run_nws_02/research_ledger/fact_ledger_draft.json`)ため、本文から抽出する以外に正本が存在しない |

## 4. 根本原因(RC-1〜RC-4)

**RC-1(定義の分裂)**: 「固有名詞」の判定が、(a)分類器 `capitalized_flags`(緩い: 大文字始まり全部)、(b)PNAP `proper_noun_evidence`(厳しい: 位置・辞書依存)、(c)Ledger(事後登録)の3箇所で別々に実装され、共通の“本文の実体表”が無い。結果として**HRに入れる定義は広く、HRから救う定義は狭い**。Bertie はこの隙間に落ちた。

**RC-2(証拠源の代理指標依存)**: 救済側の証拠は「人名らしさ」そのものではなく代理指標(Ledgerにある/CMUに無い/文中で大文字)。**CMU収録の固有名詞(一般的な人名・国・主要組織・著名ブランド)は、代理指標がその語の“出現位置”に左右される**。実測(§5): 直近X/Z本文から抽出した53の固有名詞(作品名除く)のうち**44(83%)は全tokenがCMU収録**で `cmu_oov` が使えず、Framton/Melos/Khaite のような造語名(CMU未収録)だけが偶然の恩恵を受けている(run内の実アラーム53件の証拠は cmu_oov 52 / ledger 1)。

**RC-3(Z文脈での頻度の過小評価=設計前提の欠落)**: 設計と校正はXのブランド・学者名中心。小説(Z)は英語の一般人名が主で、**歌詞・台詞・呼びかけ(vocative)で引用符直後/文頭に置かれる**ため、P-02 が構造的に不成立にする。実コーパス(§5)でも Vera は15 segmentのうち10で根拠なし(文頭)、Meta・Reuters・Bertie は全segmentで根拠なし。

**RC-4(増幅要因=救済の非対称性)**: 一度 NG_BOTH→HR Lock になると、後から証拠が揃っても保存転写の再評価では救えず(er019:349-352 は ALARM起点のみ)、再生成(有料)か人の承認が必要。小さな証拠欠落が“制作停止”に増幅される。

副次所見(同根): **SECONDARY_NOT_ENTITY_ONLY**(§5のC類)。複数語の名前(`L. Mimoun`→`elle mimon`、`Kristie Tse`→`christie say`、`Altuzarra Toteme`→`altusara totem`)でAzure側の差分が“名前+隣接語”に跨ると、PNAPは「隣接語が変わった」として不受理にする(er103:355-366)。**名前の範囲(span)を表す実体表が無い**ことの別の現れで、同じ対策(実体表)で扱える。

環境所見(別問題・本設計の範囲外、Fableへ報告): Perplexity 発音調査が401(PHASE4_RESULT_01.md:43)。事後Ledger経路が機能していない可能性。

## 5. 定量(保存データ、API 0。LLM NER実測のみ 0.5767円)

### 5-1. HR queue 88イベント(実音声のみ、汚染34行除外。`quant_hr_queue_01.py`/`quant_summary_01.py`)
現行 `evaluate_alarm_eligibility` を「現行Ledger」と「Ledger全除外(=初見語を再現)」の2条件で再評価:

| クラス | 現行Ledger | Ledger全除外(初見) | 内容 |
|---|---|---|---|
| A 受理(ENTITY_ONLY_ACCEPT) | 41 | 36 | 受理 |
| **B 証拠なし(NO_PROPER_NOUN_EVIDENCE)** | **3** | **9** | Bertie×3 / (除外時のみ)Kristie Tse×4・Stephen Reicher×1・Muse×1 |
| **C Secondary span跨ぎ(SECONDARY_NOT_ENTITY_ONLY)** | **16** | **16** | L. Mimoun×10、Kristie Tse×1、Altuzarra Toteme×2、Melos drank×3 |
| C2 Secondary noise上限 | 1 | 1 | Meink→mc |
| D 一般語化ブロック | 6 | 5 | Muse→use×4、Khaite→Kate、mini→many(ブロック維持が正) |
| E 固有名詞以外が原因 | 21 | 21 | 見出しラベル脱落9、P3_ENTRY 7、NO_ENTITY_DIFF 2、Primary非entity 3(本件の対象外) |
| 固有名詞のみ候補の母集合 A+B+C+C2+D | 67 | 67 | |

- **「固有名詞が原因だが救済されなかった」割合**: 現行Ledgerで 26/67=**39%**(B+C+C2+D)、うち**認識(証拠)の欠落が原因のB+C=19/67=28%**。Ledger全除外で B+C=25/67=**37%**(D=5は正しいブロックで除く)。
- **ユニーク本文ベース**(同一segmentの複数attemptを1と数える): 全60本文中、現行でB=2・C=6、初見でB=5・C=6。
- **Ledger依存の受理**: 受理41のうち5(12%)がLedger証拠に依存(Kristie Tse×4、Stephen Reicher×1)= 初見ならHR Lock。受理の証拠ラベル内訳(現行Ledger): ledger 36 / cmu_oov 8 / capitalized_midsentence 4(+1併記)。
- カテゴリ(語の手動ラベル、`quant_summary_01.py`の`CAT`表): person 11(受理)+13(C類)・person(fiction)=Melos/Bertie 8(受理)+3(C)+3(B)・brand_product 15(受理)+…・organization(media)=Bisnow 4。**地名・作品名・組織名は保存HR queueにほぼ現れない**(=この母集団ではカテゴリ別の一般化性能は測れない。Trialで合成データを併用する)。

### 5-2. ON/OFF差分(4,032ペア、`PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01/onoff_differential_02_result.json`)
X英語本文(full_story_part1)のHR→アラーム flip 260件は、全て固有名詞のみ不一致(khaite/toteme/melos/gruen/mimoun/minaudiere/altuzarra/bisnow等=いずれもCMU未収録またはLedger登録済み)。NS/KP/JA差分は0。**flipの母集団に“CMU収録・Ledger未登録・文頭/引用直後”の固有名詞が含まれていない**ことが、Bertieを見逃した理由と整合する。

### 5-3. 配線後の実run(PNAP配線2026-10-22以降の37 tts_generation_results、`quant_alarms_01.py`)
アラーム53件: 証拠は **cmu_oov 52(framton)/ ledger 1(khaite)**。STOPPED 8のうち固有名詞起因は Bertie 4(a2/b1b×2)と minaudière(KP英語1)。**実運用で働いた証拠は「CMUに無い」偶然だけ**。

### 5-4. 露出の見積り(実コーパス)
- 保存segment 372本(X/Z英語ナレーション)の大文字始まり非一般語: 現行 `proper_noun_evidence` が根拠を出せない“全segmentで根拠ゼロ”の語は bertie/meta/reuters/hanshin(+一般語: farther/inventing/muddy/withdrawn=偽候補)、部分的に根拠ゼロ vera(15中10)。(`exposure_corpus_01.py`)
- 本文(X記事22+Z脚本)の「文中大文字が一度も無く、文頭/引用直後/見出しにしか現れない・小文字形が無い非一般語」17語のうち、**実在の固有名詞は bertie/elle/vogue の3語、偽候補は inventing/canceling/fats/roasting/unwanted が5語**(他は縮約・ハイフン語)。→ **決定論的な頻度・大文字規則だけでは精度が約3/8で証拠にできない**(`article_entity_scan_01.py`)。
- LLM NER(gpt-6-luna、1回/本文、22本文、計0.5767円=0.026円/本文): Bertie・Vera・Framton・Melos・ELLE・Vogue・Meta・Reuters 等を検出、**偽候補5語は0件を誤検出**。ただし記事題名(work_title)・一般名詞句(Consumer Price Index、Share the journey, not the noise)を拾うため、後段で一般語/題名フィルタが必要。カテゴリ分布(異なる65名、`ner_probe_01_result.json`): organization 18 / place 15 / brand_product 12 / work_title 9 / other_named 6 / person 5。
- 53名(作品名除く)の語彙性: 全tokenがCMU収録=44(83%)、全tokenが一般語(CMU∧zipf≥4.0)=21(40%、国名など。現行G5で原理的に受理不可=`R_GENERAL_WORD`、er103:269-270)。

## 6. 過去のTrial結論・承認済み仕様との整合

- **Stage 2(判定側方式 REJECTED / TTS入力側供給 Khaite型限定 VALIDATED条件付き)**(`PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02/STAGE2_TRIAL_CLOSEOUT_01.md`): REJECTEDの対象は「取得/推定発音とASR転写の音素照合で**発音の正しさ**を判定して通す」方式(HR削減0〜2件、主因は現行TTSの実誤読)。今回の対策は発音の正しさを判定しない。**既に承認済みのPNAP(“固有名詞の発音不一致だけならアラーム記録のみで受理”)が適用される範囲を、証拠(=その語が固有名詞であること)の側で広げる**だけで、受理条件(類似度・一般語ブロック・P-03・G3二重ASR・数値/否定/脱落ガード)は変えない。したがってREJECTED理由と矛盾しない。同時に“実誤読は直らない”という結論も維持される(実誤読もアラーム記録され、供給はKhaite型のB階層人承認のまま)。
- 承認(2026-10-22 `APPROVED_FOR_PRODUCTION`)の文言は“固有名詞の発音不一致だけが原因のNG/HRをアラーム記録のみで受理”。実装の証拠規則が承認の意図より狭い領域でしか働いていない、という意味では承認済み仕様の**実装不足**の面がある一方、新しい証拠源(LLM NER)とSecondary span規則の変更は**新仕様候補**でもあるため、本件はユーザー指示(2026-10-23、Scope=Trial実装・VALIDATED止まり、Production配線未承認)に従いTrialで検証し、採用はユーザー判断とする。
- 『開いた窓』停止音声は保全(`run_sf_prod_01` の stage 実行0・編集0)。個別登録(upsert/承認CLI)・HR Lock解除はしていない。

## 7. 未確認・限界

- 保存HR queueは固有名詞カテゴリが人名・ブランドに偏り、地名・作品名・組織名は不足。→ Trialで合成データ・別記事で補う。
- 4,032ペアは“Secondary=Primaryと同転写”のmock前提のため、Primary/Secondaryの不一致パターンは表現できない(C類はHR queue 88のみで測定)。
- Perplexity 401は本調査では再現確認していない(PHASE4_RESULT_01の記述に依拠)。
- 保存本文でのLLM NERは“最新run1本/slug”のみ(22本文)。recall の分母(正解集合)は未確定=Trialで人手adjudicationを行う。
