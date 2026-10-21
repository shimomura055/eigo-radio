# INVESTIGATION_01: 固有名詞発音供給(#133)＋1語⇔複数語の同音救済 既存仕様・実装・過去Trial調査

管理ID: PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01 委任_01(計画策定のみ。Trial実行・有料API・TTS/ASR・Production変更・SSOT正本変更なし。API 0・JPY 0)
Status管理ラベル: `PLAN_DRAFT_PENDING_FABLE_REVIEW`(VALIDATED/APPROVED_FOR_PRODUCTIONと混同しない)
ユーザー指示原文: `docs/pm/delegation_log/2026-10-21_PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01_USER.md`
コード行番号は作業tree(HEAD=825c22067、対象fileに未commit差分なし)基準。略称: `val`=`er006_preprod_hardening_01_validation.py`、`sec`=`er006_secondary_asr_01.py`、`hp`=`er008_asr_variant_hardening_15_homophone_en.py`、`m1`=`er006_m1_multi_candidate_01.py`、`led`=`er006_pronunciation_ledger_01.py`、`uj`=`er078_asr_unified_judge_01.py`。

本書の「実測」は、既存の保存物(`tts_generation_results.json` 283 files、er021 telemetry)からの**オフライン再適用(API 0)**。再現script・結果は同dir(`collect_pairs_01.py`→`pairs_01.jsonl`[3,493 unique ペア]、`proto_multiword_span_01.py`、`run_offline_replay_01.py`→`replay_result_01*.json`、`demand_oov_01.py`、`rule_domain_enum_01.py`)。これは計画の根拠測定であり、受入Trialではない。Productionコードは未編集。

## 1. Issue #133の正確な内容とStatus

- **リポジトリ内の#133**: `docs/pm/USER_DECISION_REGISTER_01.md:318`「#133(UDR・未回答・非blocking[記事制作を止めない]、2026-10-21登録、PNEP委任_03、OPEN-434) 固有名詞英語発音供給の扱い: (ア)J7を認めて再Trial (イ)現状維持(CMU層+人間承認)で採用見送り(Fable推奨) (ウ)綴りのみPL供給(J2)の限定採用Trial。根拠=Trial結果で必須要件K1未達(英語公式発音なし→安全終了)・効果限定・原価悪化寄り」。対応OPEN=OPEN-434(`OPEN_ITEMS.md:946`、Status `USER_DECISION_REQUIRED`)。結果書=`docs/research/FAMILY-XZ-PROPER-NOUN-EN-PRONUNCIATION-SUPPLY-TRIAL-01/TRIAL_RESULT_01.md`。
- **GitHub Issue #133**: 本環境で確認不能(`gh` CLI未導入、`api.github.com/repos/shimomura055/eigo-radio/issues/133`は404[非公開repoか別repoの可能性]、repo内docs・commit messageにIssue番号との対応記述なし)。**未確認**。ユーザー原文の「GitHub Issue #133『固有名詞の英語発音供給』」は上記UDR #133(題名一致)を指すと推定するが、推定であり、Issue本文にUDR #133に無い要求があれば本計画に反映していない。判断候補: Issue本文の貼付または対応関係の確認(ユーザー/Fable)。
- #133は**発音供給(検出→調査→登録→Phrase List/TTS/M1供給)の採否**であり、「1語⇔複数語の同音救済」(判定基準の拡張)は別問題として、PNEP Trialでは**測定のみ・不実装**(J3、`TRIAL_RESULT_01.md` §9)だった。今回の統合は、この2つが**同じ事象(byUs)から生じた別レイヤーの問題**であることの整理から始まる(§7)。
- 関連未決: #134(Perplexity枠切れ復旧要否、OPEN-434)。Production `research_pronunciations`が動かない可能性があり、発音調査の手段選定に直結(`DESIGN_OPTIONS_01.md`案B)。

## 2. 現行Validatorでの `byUs` 救済失敗の根本原因(既調査の引用+追加確認)

既調査: `docs/research/FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01/BYUS_EQUIVALENCE_INVESTIGATION_01.md`(委任_07)。主要な事実を原文で再確認した(コード行はHEAD):

| # | 事実 | 確認箇所 |
|---|---|---|
| R1 | homophone_candidateは「canon_content・asr_contentがともに**1語**」の置換のみ。`byus→[buy, us]`は1:2で偽→内容語差(`non_entity_diffs`)→`TRUE_CONTENT_MISMATCH` | `val:750-753`、`val:1119` |
| R2 | `TRUE_CONTENT_MISMATCH`では救済層(CMU同音`_step_alternate_pass`、Case A、M1)が入口で除外される(`is_homophone_candidate_mismatch`は`ASR_VALIDATION_UNCERTAIN`限定、M1は`BASE_CLASSIFICATION_NOT_UNCERTAIN`) | `sec:318-327`、`sec:943-952`、`m1:38` |
| R3 | `by`は`_STOPWORDS`で内容語比較から除かれ`by us`→`us`との比較になる。分かち書きのみの差は全文`despaced()`規則(`val:1043`)とHEADで追加されたspan版(`_is_compound_spacing_only_span` `val:654`)で吸収 | `val:599`、`val:1043`、`val:654` |
| R4 | 承認済み仕様は単一語置換差のみ: CURRENT_SPEC.md:1839「canonical/ASRの**単一語置換差**について…ARPAbet完全一致」。固有名詞Case Aも語数一致が前提(`hp:138-148 entity_span_arpabet_match`は語数不一致なら`resolved=False`) | CURRENT_SPEC.md:1837,1839 |
| R5 | `byUs`は小文字始まりでentity_like=False(`capitalized_flags`)。Ledger登録語のentity_like化は`LEDGER_ENTITY_FLAGS_ENABLED_FOR_CLASSIFICATION=False`(2026-09-28ユーザー判断NOT_ADOPTED) | `val:467`,`val:536` |
| R6 | Primary/Secondaryは統合されず独立評価。Secondary転写は原稿と単独で許容集合(should_pass+CMU同音/Case A+M1)に入るかを見る | `sec:993-1010 _secondary_accept`、`uj`(委任_07 §3-5) |
| R7 | EN発音供給が空: ledgerのbyus entryは`ja_reading_katakana`のみ・`pronunciation_hint=""`・`expected_pronunciation_ipa=""`・`sources=[]`。`get_hint_for_text`はhint空entryを返さない(Phrase List空・setWeight(2.0)未実行) | `led:237-282`(特に`led:279`)(特に`if entry.get("pronunciation_hint")`)、ledger.json(`byus`) |

**追加確認(本調査)**:

1. **CMU辞書は`byus`を収録しているが、それはブランドの公式発音ではない**。`pronouncing`で`byus`=`B AY1 AH0 S`=`bias`と同一。したがって現行の`byUs→Bias/Byus/bias`救済は「CMUに姓等として`byus`が収録されていてたまたま`bias`と同音」という**綴りベースの偶然**に依存している(公式発音確認ではない)。この信頼の土台は、**今回の拡張(1語⇔複数語)も同じ**(§7、設計の肝)。
2. **「全文despace一致」の既存規則により`By Us`/`by us`は他に差分が無い場合は既にPASS**する。実例: run_byus_01 `topic_intro` Primary転写`By Us lets you shape stories…`は`NORMALIZED_MATCH`(`tts_generation_results.json` `topic_intro`.attempts_log[0])。新規に必要なのは「**綴りが違うが発音が同じ**」(`buy us`、`Buy Us`)で、綴りが同じで空白だけ違うものではない。
3. **HEADでの再適用**: 保存転写3,493ペアにHEAD判定を適用し、`byus→buy us`を含むペアは**全て非PASS(TRUE_CONTENT_MISMATCH)**。HEADで`story making→storymaking`のspan版が入ったが`buy us`は救われない(区別: `story making`は空白差、`buy us`は綴り差)。
4. **run_byus_01の実害の再整理**: p1/att1のPrimary `Bias`+`storymaking`はHEADで救済済み(委任_07既報)。`Buy Us`はAzure(Secondary)の転写で、Primary NG後にのみ参照される。**HEADに提案ルールを足しても、この実run単体での追加救済は0**(p1/1はHEADのstory-making是正で既にPrimary PASS)。提案ルールの価値は「Primary(OpenAI)が`Buy us`と書く将来のケース」(§5の別runで実在: Primary `Buy us let…`)への予防であり、**この実runの再試行削減は主張しない**。
5. **latent既存問題(今回の対象外、Fableへ報告)**: canonical `AI` vs ASR `Eye`は**現行で`PROPER_NOUN_ENTITY_ARPABET_CONFIRMED`でPASS**(実測: `AI is here.`/`Eye is here.`→`ASR_VALIDATION_UNCERTAIN`→`_step_alternate_pass`=PROPER_NOUN_ENTITY_ARPABET_CONFIRMED)。原因はCMUの`ai`代表発音が`AY1`(=eye)で、略語`AI`の「エー・アイ」(`EY1 AY1`は第2variant)ではないこと。TTSが`AI`を「アイ」(eye)と読む誤りを素通しする可能性。承認済み仕様(固有名詞Case A=代表発音一致)どおりの挙動で、仕様の範囲内の穴。**本計画で新たに広げない**(提案ルールはcanonical側tokenを3字以上に限定して継承しない)が、既存の穴として判断候補。

## 3. 既存機構で再利用できる部分

| 機構 | 再利用可否 | 理由・場所 |
|---|---|---|
| CMU同音(`homophone_arpabet_equivalent` any-variant一致、`_phone_variants`) | **そのまま再利用**(発音辞書・正規化・補完テーブル) | `hp:49-100` |
| `homophone_candidate`フラグ→`ASR_VALIDATION_UNCERTAIN`→`_step_alternate_pass`→`HOMOPHONE_EQUIVALENT`→Primary/Secondary許容集合 | **入口(候補判定)を拡張するだけで下流は無改変** | `val:750-753`、`sec:571-594`、`sec:943-952,993-1010`、`val:1119-1170` |
| span単位のdiff抽出(SequenceMatcher opcode、隣接span限定) | そのまま(「離れた語を結合しない」を構造的に満たす) | `val:691-694` |
| 数値・否定語ガード、`_is_compound_spacing_only_span`(story-making是正) | 共存(適用順は先に空白差span除外、その後に音韻判定) | `val:654`,`val:691-720` |
| M1 C1/C2(CMU全異読+Ledger IPA→ARPA `ipa_to_arpa`)、凍結候補、audit | **Phase 2で再利用**(CMU未収録の固有名詞のn:m) | `m1:91`,`m1:208-251`,CURRENT_SPEC.md:2808 |
| Ledger entry・validator(`entry_invalid_reason`、`ledger_disabled`)、cache(=Ledger自体)、`upsert_*`、`ledger_health_check` | 再利用(新規スキーマ追加なし方針、PNEP V6) | `led:77-98`,`led:194-218`,`led:329` |
| PNEPの検出D1/D2・登録validator V1'-V6・`TrialIsolation` | 再利用候補(Trial専用`er089_*`。Production無配線) | `TRIAL_RESULT_01.md`§7 |
| 統一judge(Primary/Secondary独立評価、`secondary_accept_fn`) | 無改変 | `uj:551`,`sec:993` |
| retry/fallback/Gate/cooldown | 無改変(判定が`HOMOPHONE_EQUIVALENT`になれば再試行を発生させないだけ) | 委任_07 §3-5 |

## 4. story-making / storymaking 既存修正との整合

- 是正=FAMILY-XZ-ASR-MULTI-DIFF-JUDGE-FIX-01(PRODUCTION_WIRED、commit 01fdd3a2c、CURRENT_SPEC.md:452): `_is_compound_spacing_only_span()`がdiff span単位で空白除去一致・冠詞のみ除外一致なら内容語差から外す(`val:654`、呼出`val:713`、`continue`)。
- 提案ルールは**その`continue`の後**で評価される(`homophone_candidate`算出箇所`val:750-753`)ため、**適用順は 空白差span除外→benign複数形→(既存1:1同音)→(提案)n:m音韻一致**。衝突しない。
- 実測: 保存転写3,493ペアの`story making→storymaking`(5 span)・`well being→wellbeing`等の**判定結果は提案前後で不変**(`replay_result_01.json`: 変化ペアは`byus→buy us`の4ペアのみ)。
- ratio問題(委任_07 §7案(d)): span吸収後も`SequenceMatcher.ratio()`は生token列で計算されるため、`by us→byUs`置換でratioが0.9718→0.9811に上がる(分かち書き差の分だけ損なわれる)。`HOMOPHONE_EQUIVALENT`経路では`ratio < tts_failure_threshold`のときのみ`TTS_FAILURE`(`val:1109`)で、救済の可否を左右しない。**案(d)は本計画の対象外**(別の不具合判定=Fable11-8)。

## 5. 実データ上の発生頻度(オフライン実測、`replay_result_01.json`)

保存物3,493 unique ペア(実run転写2,656+telemetry由来837。canonical本文2,425種)に現行判定とプロトタイプ判定を適用:
- 1語⇔連続n語(片側が単語1つ)のspan: 246種(長文の欠落等を含む)。うち音韻列(ストレス無視・CMU全variant)が一致するspanは15種(`byus→buy us`/`byus→by us`/`onto→on to`/…。大半は空白差で既に救済済み)。
- 提案ルールで**判定が変わるペアは4件のみ**(全て`byus→buy us`、Primary 1・Secondary 1・telemetry 2。`非PASS→PASS:HOMOPHONE_EQUIVALENT`)。**PASS→NGは0件、想定外のNG→PASSは0件**。
- ガード無効化のablation(`PNMH_NO_GUARDS=1`、`replay_result_01_noguard.json`と、空白差spanを除いた再集計): 音韻列一致のspanは全体で15→25種に増えるが、増えた7種(`us→u s`[257回]、`a m→am`[13]、`am→a m`[31]等)は**全て空白除去で綴りが一致する**ため、提案ルールに到達する前に既存の空白差規則(全文`despaced()`と`_is_compound_spacing_only_span`)が吸収する(=提案の有無と無関係。ガードの効果ではない)。**提案ルールに実際に到達するspanに限ると、ガードの限界効果は G5(canonical側token 3字以上)による`ai phone→iphone`の1件のみ**、G4(複数語側の1文字token禁止)の限界効果は保存データ上0件(`a count→account`はG5でも防がれる)。→ G4は『効果の実証がない防御』として任意(Opus/Fableが過剰と判断すれば削除可)。
- **既存の穴(今回の対象外、判断候補)**: 上記の吸収により、canonical `us`(代名詞)をTTSが文字読み`U S`した誤りは、**現行でも**全文despace規則でPASSする(`He told us the plan.`/`He told u s the plan.`→`NORMALIZED_MATCH`、`am`→`a m`も同様)。国名`US`・時刻`a.m.`では正読なので承認済みの空白差吸収の副作用として許容されてきた可能性が高いが、略語/代名詞の区別はしていない。AI→eye(§2-追加5)と同種の『期待発音を綴りだけで決める限界』であり、L2(期待発音源)の改善で扱う対象。
- **ラベル付きデータでの副作用確認**: ASR-THREE-WAY-COMPARISON-TRIAL-01の保存転写(`er091_output/asr_three_way_trial_01/results/asr_raw.jsonl`、**読み取り専用**・そのTrialの設定/出力は無変更)544転写・91音声(正常/HR承認難例/既知問題[take part]/構成問題[TTS文面変更・splice]、Whisper small/medium・Azure・OpenAI)に現行/提案を再適用(`replay_asr3way_cache_01.py`→`replay_asr3way_cache_result_01.json`): **判定変化 0件、問題ラベル音声の新規PASS 0件**。この集合に1語⇔複数語の正例は含まれない(救済力ではなく『副作用なし・誤PASSなし』の確認)。
- 発生頻度は低い(判定が変わるペア4/3,493=0.11%[v2: pairs_02で4/4,032=0.10%]。多語化した実転写6ペアは全てrun_byus_01の1記事由来で、一般化の根拠は薄い)。**この拡張の主な価値は予防(Family Yを含む将来の造語・ブランド名)であり、既存runの再試行削減は小さい**。
- 適用域(`rule_domain_result_01.json`): 保存原稿の語彙3,725語(CMU収録)について「canonical単語X＝連続2語(w1 w2)」で綴りが異なる音韻一致は461組[v2訂正: distinctは456組、§8-2](`already=all ready`、`also=all so`、`bias=buy us`、`changes=change is`等)。通常語にも**理論上は**広く及ぶ(音が同じなら期待どおりPASSだが、適用域が「固有名詞に限らない」ことの定量根拠)。実運用では通常語がASRで2語に割れることは稀(実ペアでの発火はbyusのみ)。スコープを固有名詞/造語に絞る案は`DESIGN_OPTIONS_01.md`で比較。

### 5-2. 発音供給(#133)の需要(`demand_oov_result_01.json`)
非PASSペア1,048件の内容語差のうち、canonicalがCMU辞書外(OOV)の語: 実run由来はTriangeln(10)・Ottoni(10)・AKB48(9)・Seishiro(7)・Sukisshu(7)・Torai(5)等、**外国語・日本語由来の人名/地名が中心**(telemetryのmelos 132、khaite 56、mimoun 43、toteme 34等はTrial/合成由来を含む)。byUs型(辞書収録の英語造語)は別分類(CMUに収録されているため供給不要)。つまり#133の供給は「**CMU辞書外の外国由来名**」に効く機能であり、byUsの多語化問題(L1)とは対象が異なる。

## 6. Family X/Z/Y 共通仕様か

- 結論: **共通仕様として扱える(単一のProduction関数に収まる)**。Family X(`er003_v1_repro01_main_generate.py`/`er019`系runner)とFamily Z(er063→er012)は、いずれも`er006_secondary_asr_01.evaluate_attempt_with_cascade[_detail]`→`val.classify_asr_match`を通る(CURRENT_SPEC.md:452記載、`grep evaluate_attempt_with_cascade`で呼出元を確認)。将来のFamily Yも同関数を呼ぶ前提で、**判定拡張を1箇所(`protected_check`)に置けば全Familyに自動で効く**(Family別の分岐は不要)。
- 適用外: JA判定(`er007_ja_secondary_asr_01`、読み/かな漢字の別判定)・数値/否定語(既存ガードが先に判定)。Key Phrase(KP)のEN ASRも同関数を使うが、KPは短文で1語の置換が支配的なので提案ルールの発火は稀(測定ではKPペアの変化0)。
- 注意: **Ledger供給**(Phrase List重み2.0)はASR方式に依存(Azure固有機能)。3方式ASR比較Trialの結果次第で供給の入口が変わる(依存管理は`DESIGN_OPTIONS_01.md`§6)。

## 7. 設計の肝(次書への入力)

1. **byUs救済の失敗は2つの別レイヤーが重なっている**: (L1) **判定レイヤー**: 「1語⇔複数語・綴り違い・同音」が候補判定に入らない(R1-R2)。(L2) **供給レイヤー**: 「そもそも正しい発音をシステムが知らない」(R7)。L1はCMUの綴りベース発音で閉じて解ける(L2を待たない)。L2は「正解発音の確定」の問題。
2. 提案するL1拡張の**信頼の土台(期待発音=CMU収録綴りの発音)は既存の1語⇔1語同音(Bias/Byus/wait-weight)と同じ**(ただしストレスの扱いは同一でない・v2 §8-4)(canonical側の期待発音=CMU収録綴りの発音)。これ以上の確認(公式発音)を要求するのはL2。したがって「ByUsの公式発音が未確認でも、CMU上の期待発音を土台にしている現行の1:1救済と同水準でn:mを救う」は**新しい信頼リスクを持ち込まない**が、「現行の土台自体が偶然」という既存リスクは**そのまま残る**(§2-追加確認1)。この区別を計画の前提として明記し、公式発音の確定(L2)は別建てで管理する。
3. **特定のASR構成(Primary/Secondary)に依存しない**: L1は転写テキスト→判定の純関数であり、Primary/Secondaryの組合せが変わっても成立する(ただし「どのエンジンが多語化しやすいか」で効果の大きさは変わる=再評価対象)。

## 8. v2追補(委任_02、Opus OF-PNMH-R-01〜13の調査項目。API 0・JPY 0)

### 8-1. R-10: CURRENT_SPEC:1839とコードの不一致(Primary単独PASS)の事実確認
- **仕様の文言**: CURRENT_SPEC.md:1839「英語homophone(同音異義語)のCascade内自動PASS条件」=「単一語置換差について、…ARPAbet音素列が完全一致する場合のみ**cascade対象**とする(即blind TTS retryしない)。**Secondary(または2回目のASR)側の結果が**、(a)canonical文字一致、または(b)同じくARPAbet完全一致のいずれかを満たした場合のみPASSする」。同タスクのDECISION_LOG記録(`DECISION_LOG_HISTORY.md:5736`、ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15)も「Secondary側は…ARPAbet完全一致を要求し、消極的PASSは禁止」とだけ書き、Primary単独PASSの可否は書いていない。一方、固有名詞Case Aは同じ記録(`:5734`)とCURRENT_SPEC.md:1837(A)に「代表発音が完全一致する場合のみ自動PASS(…コストゼロ)」とあり、Primary単独のPASSが明記されている。
- **コード**: `sec:937-951`(`evaluate_attempt_with_cascade_detail`)は、Primaryが`should_pass`でなくても`is_entity_like_mismatch||is_homophone_candidate_mismatch`なら`_step_alternate_pass`(CMU Case A/homophone)が成立した時点で**追加ASRなしに即PASS**(`layers=["cmu_alternate"]`)。この挙動は**同一タスクの実装commit `2b40165dc`(2026-08-28)で既に存在**(当時のコメント「Primary#1の時点で既にhomophone/固有名詞Case Aが判定できる場合、追加のASR呼び出し無しでPASSする…コストゼロ」)。EN統一judge配線(`cc01cd8f3`、2026-10-15)後も同じ位置。
- **後続の置換決定**: `CURRENT_SPEC.md`/`DECISION_LOG.md`/`DECISION_LOG_HISTORY.md`を`cmu_alternate|HOMOPHONE_EQUIVALENT|Primary単独|追加ASR無し|このステップ単独`でGrepし、1839を置換した決定は**見つからなかった**。一方でPRODUCTION_WIRED記録CURRENT_SPEC.md:453(FAMILY-XZ-ASR-MULTI-DIFF-JUDGE-FIX-01)は「保存済み**Primary転写**が`HOMOPHONE_EQUIVALENT`でPASS」を期待成果として記載しており、運用上はPrimary単独PASSが前提になっている。
- **結論: (ii) 仕様文言とコードの不一致(PM_GOVERNANCE 11-8の不具合/整合性候補)**。(i)「後続決定で置換済み」は出典を特定できず、(iii)の要素(ユーザーが承認した意図がPrimary単独を含むかは文言から断定できない)もある。**判定はFable**。コードは変更しない。**新ルールの方針**: Primary単独PASSの是非は本計画で決めず、新ルールで救済した判定も既存1:1と同じ`_step_alternate_pass`経路に載せるだけで、既存のズレを拡大も是正もしない。

### 8-2. R-05: 再適用対象の拡張結果(pairs_02、`collect_pairs_02.py`/`measure_v2_01.py`)
- 対象: pairs_01(3,493)＋MDJF golden 193行(191ユニーク、`golden_rejudge.py`と同じ走査)＋`human_review_queue.jsonl`全件の`steps[*].text`(235ペア)＋`runtime_evidence_{x,z}.json`/fixtures(7ペア)＋tts_results追加形式 → **計4,032ペア**(origin別延べ: pairs_01 3,493 / tts_results_ext 3,212 / human_review_queue 235 / golden 191 / runtime_fixture 7、重複あり)。
- **`Bi-us`を含むペアが対象に含まれることを確認**(runtime_evidence_x.json、Primary転写`BAUS`と`"Bi-us."`)。そのペアは現行・V1とも`TRUE_CONTENT_MISMATCH`のまま(`byus→baus`のOOV diffが残るため)。`bias→bi us`のdiffだけはV1で`homophone_candidate`=Trueになる(V8でFalse)。
- 変化したペア: V1で**4ペア**(全て`byus→buy us`、run_byus_01由来、NG→`PASS:HOMOPHONE_EQUIVALENT`)、PASS→NG **0**、新規誤PASS **0**(ガード無しの最も緩い構成でも追加は`AI Phone→iPhone`の1件のみで、G5が防ぐ)。human_review_queueの235ペアでは変化0。V2(ストレス込み)・V5(2字以下禁止)は4ペアとも救済不能(変化0)、V3/V4/V6/V8は4/4維持。
- 理論域の数字訂正: 委任_01の「461組」は`rule_domain_enum_01.py`が(X,w1,w2,only_primary)の4タプルを集合化していたため、primary/非primaryの両方で成立する組を2回数えていた。distinctは**456組**(同一語彙、`measure_v2_result_01_vocab01.json`)。pairs_02の語彙では473組。

### 8-3. R-03: 既存の穴 `Tse`→`sea`の実測(是正しない)
現行コードで`Kristie Tse spoke first.`→`Kristie Sea spoke first.`(`Sea`/`See`/`C`とも)は`ASR_VALIDATION_UNCERTAIN`→`PASS:HOMOPHONE_EQUIVALENT`。原因: `Tse`はentity_likeかつ`homophone_candidate`(any-variant一致、`S IY1`)=Trueで、`_step_alternate_pass`の1番目の分岐(Case A=代表発音のみ)は不成立だが2番目(homophone)が成立するため。固有名詞に「代表発音のみ」としたD-2'(`DECISION_LOG_HISTORY.md:5728-`の『実装中に発見した事実』、Tse/Sea)の意図は、多語span・1:1のhomophone経路でも貫かれていない。規模: 保存canonical中の文中大文字語621語のうちCMUに複数variantを持つ116語、**非代表variantでのみ他語と同音になる組は5組(4語)**: `loewe→low`(46回)、`tse→sea/see`(12回)、`are→or`(6回)、`when→win`(7回)。是正は本計画の範囲外(判断候補U5・R-13)。

### 8-4. v1記述の訂正
- 本書§2「追加確認1」・§3表(CMU同音の再利用)・末尾の結論2にある『既存の1語⇔1語同音と同一』は、**信頼の土台(期待発音=CMU収録綴りの発音)が同じ**という意味に限る。ストレスの扱いは同一でない(既存1:1はストレス込みの完全一致、連結比較はストレス無視。DESIGN_OPTIONS_01.md §4-1 G7)。
