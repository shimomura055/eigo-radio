# ITEM1_ROOT_CAUSE_02_SPEC_RECONCILIATION_01(FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_05、2026-10-20)

Status: `ITEM1_ROOT_CAUSE_EXPLAINED_PENDING_FABLE`(11-8不具合0件)。コード変更0・新規TTS 0・LLM 0・HR Lock sha不変・`ledger.json` sha不変(script内で前後比較)。
目的: ユーザー2026-10-20指示(原文=`docs/pm/delegation_log/2026-10-20_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_ROOT-CAUSE-WIRING-CLOSEOUT_USER.md`)の「なぜ既存の承認済み音韻同等性判定でこの認識結果が救済されなかったか」への、承認済み仕様文の逐語照合による具体的回答。委任_01の結論を鵜呑みにせず、判定順序を実関数で再実測した(`item1_spec_reconciliation_verify_02.py`/`_result.json`、`melo_asymmetry_clip_census_02.py`/`_result.json`。いずれもread-only・API 0)。

重要な新規事実(委任_01・Opus_Gの記述の訂正を含む):
1. `Melo drank`のPASSは**トークン数50以上の文でのみ**成立する(§2-A)。Opus_Gの「約26文字」は誤り(`OPUS_REVIEW_G_01_VERBATIM.md:20`)。
2. run_e2e_04のMelos含有6文のうち、Melo/Melloの非対称が実在するのは**今回の文(part3_c1、69語)1文だけ**。
3. 過去のMelos PASSは全て「歯擦音が続く文でのM1/F1」か「Azureがcanonical綴りを返したTier3」で、**音素同等性による受理が非歯擦音文脈で働いた実績はない**(§2-C c-4)。

## §1 承認済み「音韻同等性」関連の仕様文(逐語・行番号付き)

水準の凡例: P=Production仕様(`APPROVED_FOR_PRODUCTION`) / D=設計原則(`DESIGN_PRINCIPLE_AGREED`、Production未採用)。

| # | 出所 | 逐語引用(抜粋) | 水準・備考 |
|---|---|---|---|
| S-1 | `CURRENT_SPEC.md:2136`(Validator、2026-08-24 `ER-006-GATE-CALIBRATION-ASR-CASCADE-MATH-VALIDATOR-01`、採用=`DECISION_LOG_HISTORY.md:4365-4373` Decision 1) | 「安全に吸収してよい表記ゆれ: …規則的な単数形/複数形の語尾差(result/results等、閉じた語尾パターン[-s/-es]のみ、無関係語の誤同一視を避けるため長さ・語尾形状を厳格に限定)」「絶対にPASSさせてはならない差…無関係な複数形の誤同一視(cats≠dogs)」「記事個別のwhitelist(固有名詞の1対1ハードコード等)は使わない。」 | P。綴り水準。固有名詞への適用を明記も除外もしていない。`HIGH_SIMILARITY_SAFE`・閾値0.98は**本文に記載なし**(コード既定`er006_preprod_hardening_01_validation.py:1201`のみ) |
| S-2 | `CURRENT_SPEC.md:2144`(English ASR Semantic Equivalence Layer、OPEN-186、2026-09-27) | 「Tier3(規則的複数形・固有名詞のみの1トークン差、Secondary ASR corroboration必須)…`SECONDARY_ASR_CORROBORATED_MATCH`、warning付き」 | P。音素比較でなく**Secondaryがcanonical語そのものを返す**ことを要求(`er021_en_asr_semantic_equivalence_production_01.py:731 corroboration_supports`=`other_tokens[idx]==canon_tokens[idx]`) |
| S-3 | `CURRENT_SPEC.md:2150`(B1 Connected Speech Validator、OPEN-107/110) | 「判定パターン(3種、ユーザー承認範囲に限定、拡張しない)」「Pattern A(歯擦音連続、例: studies/z/+suggest/s/)…いずれの判定にも該当しない場合は既存のTRUE_CONTENT_MISMATCH等をそのまま維持する(…新しい音韻パターンの追加は行わない)」 | P。Pattern A=canonical語から-s/-esを除いた綴り==ASR語**かつ次語頭が歯擦音**(`er011_b1_connected_speech_validator_01.py:153-159`) |
| S-4 | `CURRENT_SPEC.md:2151`(Connected Speech Equivalence Layer、OPEN-122) | 「音韻環境カテゴリA〜G+独立ASR corroborationで判定する拡張レイヤー、**A2/B1英語本文segment限定**」「`classify_asr_match()`がTRUE_CONTENT_MISMATCHかつ`protected_check()`通過済み…の場合のみ」「単一証拠のみでは絶対にacceptしない安全設計」 | P。入口はTRUE_CONTENT_MISMATCH限定。カテゴリA〜Gに**語末S/Zの有声性差は無い**(`er011_connected_speech_equivalence_layer_production_01.py:80-137`)。`phoneme_final_place_substitution`は「manner/voicingが変わる場合は語幹自体の置換とみなし対象外」(同L163-168。assimilation検出関数内の安全側設計) |
| S-5 | `CURRENT_SPEC.md:1829`(固有名詞ASR不一致の自動PASS条件) | 「(A) canonical綴り・ASR候補の両方がCMU Pronouncing Dictionaryに存在し、代表(先頭)発音が完全一致する場合のみ自動PASS…(B) CMU辞書に無い外国由来固有名詞は…自動PASSの根拠にはせず、Human Reviewパッケージ…を充実させるためだけに使う。IPA→ARPAbet変換による近似自動PASSは行わない…(B)は引き続きHuman Review行きのまま。」 | P(2026-08-28)。**OOVはHR行き**。後にM1(S-7)が「Ledger候補が揃う場合」に限り限定的に置換(L2799 D-2') |
| S-6 | `CURRENT_SPEC.md:1831`(英語homophone) | 「`HOMOPHONE_EQUIVALENT`: …CMU Pronouncing DictionaryのARPAbet音素列が完全一致する場合のみcascade対象…辞書に無い語向けの小さな閉じた補完テーブルを併設(2026-08-28時点で空…)」 | P。**「音韻的に同等」のProduction上の定義=CMU音素列の完全一致(両語収録)**。一般語・固有名詞とも |
| S-7 | `CURRENT_SPEC.md:2796-2801`(M1、2026-10-13ユーザー承認、OF-178等) | L2796「複数の合理的な発音候補のいずれか1つで音韻整合すればPASS可。**綴りだけを根拠に任意の発音を許容してはならない**」/L2797「C3(綴り規則推定)・ASR転写からの後付け候補は存在しない」/L2798「受理: 置換後文のF1残差0、かつexact以外の置換位置が全て`f1_explained`(Pattern A/B/C)に含まれること(benign吸収は不受理)」/L2801「未充足(PRODUCTION_WIRED未宣言): 自然発生Production runでのM1発火evidence未取得…」 | P(`APPROVED_FOR_PRODUCTION`・配線済み・`PRODUCTION_WIRED`**未宣言**)。対象=OOVのcanonical側(Ledger IPA→ARPAbet)。ASR側の音素はCMUのみ |
| S-8 | `er077_output/m1_oov_multi_pronunciation_01/SSOT_DRAFT_01.md:4`(M1承認時の設計文)、`docs/pm/USER_DECISION_REGISTER_01.md:71`(#52)、`docs/pm/OPUS_FINDINGS_LEDGER.md:211`(OF-184) | 「C3(規則G2P)とASR側綴りの近似は不採用。」/#52「判断済み…**綴りだけを根拠に任意の発音を許容してよいわけではない**=許容不可を併記」/OF-184「直接音素置換への拡張は今回範囲外。no_match理由別telemetryで需要測定」 | M1承認時に**意図的に対象外**とした領域(ASR側OOV語・G2P) |
| S-9 | `CURRENT_SPEC.md:2814` | 「**Primary#2(同一音声のOpenAI再転写)とSecondary#2は廃止**…Secondary 1回+cache」(2026-10-15) | P。再転写による救済は不可 |
| S-10 | `DECISION_LOG.md:20918`(ユーザー決定2026-10-13)+`docs/pm/design_principles/connected_speech_proper_noun_phonetic_equivalence_2026-10-13.md` §1・§2-1〜2-7・§3・§6・§7 | DECISION_LOG:「原文とASR結果の文字列差分を、発音上の同等性と自然な音声変化に基づいて評価し、同じ音韻現象には同じ判定を適用する。ただし、実質的な発音・内容の誤りを許容しないための安全条件を維持する。」「今回の承認は設計方針の承認であり、新ValidatorのProduction採用承認ではない」。設計原則文書冒頭:「**Production仕様ではない。** Status: `DESIGN_PRINCIPLE_AGREED`…Production採用 = 未承認」。§2-1「綴りの違い自体は音声の誤りを意味しない」「音素列として同等か、自然な音声変化(連結発音)で説明できるか」、§2-6「母音や他の子音が実質的に異なる転写…音素が実質的に異なるケースまで許容しない」、§3「確認済み発音: CMU辞書(代表発音)、Pronunciation Ledger、ユーザー確認済みの読み。**推定(OOVのstem+規則的-s等)は『確認済み』に含めない**」、§6「最終選択は設計草案の範囲外(…ユーザー判断。OPEN-330/339)」、§7「本原則は`CURRENT_SPEC.md`へ**記載しない**(未検証ロジックはProduction仕様ではない)」 | **D(設計原則・ユーザー合意)。Production仕様ではない** |

### 1-1 ユーザー前提文に最も近い承認済み文
ユーザー文:「既存の承認済み仕様では、単なる綴りの違いによって音韻的に同等な発音を不合格にしない」。
**文言として最も近い**のはS-10(DECISION_LOG:20918 / 設計原則§2-1・§2-3)。**Production仕様として最も近い**のはS-6(CMU完全一致)+S-7(M1)+S-1(単複)の3つの合成。
- (i) 水準: S-10は`DESIGN_PRINCIPLE_AGREED`でProduction仕様**ではない**。Productionに入っているのはS-1〜S-9の個別機構のみで、これらを束ねる一般規則「音韻的に同等ならPASS」はProductionには存在しない。
- (ii) 「音韻的に同等」の定義: 設計原則§3は音素水準(同音異綴り=音素列が同一で綴りが異なる語)。ただし比較対象は**確認済み発音**(CMU/Ledger/ユーザー確認済み)に限り推定は含めない。Production(S-6)は「CMU音素列の完全一致」、S-7は「canonical側Ledger候補音素列に対する、exact/語末S・Z脱落(F1で説明できる場合のみ)/-s付加」。**綴り水準の等価はS-1(単複)とS-3(Pattern A、次語頭が歯擦音)のみ**。
- (iii) 固有名詞・OOVへの適用条件: S-5(OOV固有名詞はHR行き)→S-7(OOVのcanonicalはLedger候補で救済、ASR側OOV語は救済しない=S-8)。S-1は固有名詞を明示的に対象とも対象外ともしていない(§2-A)。
→ ユーザーの前提文は**設計原則(合意済み・未Production化)の理想**であり、Productionの現行仕様は「CMU完全一致(S-6)+Ledger候補×連結発音(S-7/S-3)+単複の表記ゆれ(S-1)+Azureが正綴りを返すTier3(S-2)」という個別許容の集合である。これが「期待したのに救済されない」という感覚の一因。

## §2 A / B / C の具体解明

### 共通: canonical側の発音(Ledger)
`ledger.json` key `ec716e185835dba3`(surface=melos、`cascade_unresolved_entity`、confidence=**low**、updated_at 2026-10-12T13:17:58、sources 10件): expected `/ˈmiː.lɑːs/`(米)・`/ˈmiː.lɒs/`(英)、alt `/ˈmɪlɒs/`・`/ˈmɛlɒs/ または /ˈmɛloʊs/`。M1凍結C2候補=4件: `M IY L AA S`/`M IH L AA S`/`M EH L AA S`/**`M EH L OW S`**(candidate_set_hash `fccea39f81125d79`)。**全候補の語末は無声S**。CMU(`pronouncing`)に`melos`・`mellows`・`mellos`は無い(実測 `cmu`欄: `[]`)。`melo`/`mello`/`mellow`は同一音素列`M EH L OW`。

### A: `Melos → Melo`(PASSの正確な根拠)
実測(`item1_spec_reconciliation_verify_02_result.json`、canonical=part3_c1全文69語):
1. `protected_check`(`er006_preprod_hardening_01_validation.py:691`): `_is_benign_plural_pair('melos','melo')`=True(`_singularize_simple('melos')=='melo'`: `len('melos')=5>4`かつ`s`終わりかつ`ss`でない、L634-642)→ **`content_word_diffs`へ追加されない**(L692-696のコメント「規則的な単数形/複数形の揺れのみ…後段のcascade判定を無関係な複数形差でブロックしない」)。
2. 内容語差が無いので`entity_only_diffs`・`non_entity_diffs`は空 → L1148 `ratio >= 0.98`(トークン列の`difflib` ratio、L1006)=0.9855 → **`HIGH_SIMILARITY_SAFE`**(should_pass=True、警告なし、reason「内容語の差は無く、表記のみの軽微な揺れ」)。
3. **Pattern A(音連結)とは別経路**: `classify_connected_speech`は`Melo drank`で`UNCLASSIFIED_FALLS_THROUGH_TO_EXISTING`(実測)。`s_suffix_label_if_match('Melos','Melo')=='s'`は成立するが、`initial_sound('drank')=='/d/'`が`SIBILANTS={'/s/','/z/'}`に入らない(`er011_b1…:84,153-159`)。`drank`は歯擦音でない。
4. **文長依存(新規事実)**: ratioはトークン列で計算されるため、1語差で0.98に達するのは**50語以上**(実測: 49語=0.9796=UNCERTAIN、50語=0.98=HIGH_SIMILARITY_SAFE。10語=0.90/20語=0.95/30語=0.9667/40語=0.975は全てUNCERTAIN)。`Melo drank.`(2語)=0.5=UNCERTAIN。
5. 実データ(run_e2e_04のMelos含有6文、`melo_asymmetry_clip_census_02_result.json`): 69語のpart3_c1だけが`Melo`=PASS。他5文(2/5/9/18/30語)は`Melo`もUNCERTAIN(2語の`Melos said.`は`Melo said.`がPattern AでACCEPT、`Mello said.`もM1でACCEPT=対称)。

**承認範囲内か**: S-1の字義(語尾形状・長さ条件を満たす規則単数/複数)の範囲内。ただし(a)固有名詞への適用はS-1に**明文なし**(Opus_Gは「普通名詞の単複の揺れを想定した規則が、固有名詞の語幹末sにも当たっている副作用」と評価、`OPUS_REVIEW_G_01_VERBATIM.md:17`)、(b)「吸収」はretry回避(TRUE_CONTENT_MISMATCHにしない)が目的でPASS保証ではない(コメントL692-696、およびPOSITIVE fixtureの合否基準が`should_pass or not should_retry`=`er006_preprod_hardening_01_validation_test.py:267`。`result/results`の短文fixtureは実測でUNCERTAIN)。判定=**承認文の字義の範囲内・固有名詞適用と文長依存は明文化なし(UDR #120の論点)**。厳格化はしない(委任禁止事項(3))。

### B: `Melos → Mello`
- 音韻関係: `mello`=`M EH L OW`(CMU)。Ledger候補`M EH L OW S`から**語末無声Sを除いた形**(他は同一、音節数同一)=「語末S脱落」。
- 発動する判定条件の順序と棄却(Primary、`er006_secondary_asr_01.py`の実順序。実測値は`item1_spec_reconciliation_verify_02_result.json` LONG/Mello):

| 段 | 関数:行 | 条件 | 実測 | 結果 |
|---|---|---|---|---|
| 1 classify | validation.py:691(benign)→1137(entity_only) | `_is_benign_plural_pair('melos','mello')`=False(`_singularize_simple('melos')=='melo'`≠`mello`、単複補正は綴り一致のみ)→`content_word_diffs=[('melos','mello',entity_like=True)]` | `ASR_VALIDATION_UNCERTAIN`、ratio 0.9855(L1137の`entity_only_diffs`がL1148より先のため`HIGH_SIMILARITY_SAFE`には**届かない**) | 棄却 |
| 2 Eq Layer | secondary:799 | 入口=`TRUE_CONTENT_MISMATCH`限定。本件=UNCERTAIN | 不呼出(呼んでも`word_phones('melos')=None`) | 対象外 |
| 3 Tier3 | secondary:855-870、er021:731 | Azureが同位置にcanonical語`melos`を返す | Azure=`Mellows`→`corroboration_supports`=False(E21行9614 `corroborated_by=[]`) | 棄却 |
| 4 Case A/homophone | secondary:557 `_step_alternate_pass` | 両語CMU収録かつ代表発音一致 | `melos`未収録→unresolved | 棄却 |
| 5 M1 | secondary:937→m1:443 `_judge_core` | 入口通過。置換案`mello→melo`(`drop_final_S_or_Z`、C2_ledger_alt `M EH L OW S`)→`_post_check`(m1:407-421) | 置換後`Melo drank`のF1=`UNCLASSIFIED`(`drank`=/d/)→**`SUBSTITUTION_NOT_F1_EXPLAINED`** | 棄却 |

- **M1/F1/単複補正の関係**: M1は「綴りが違う同音語」を一度`Melo`へ正規化し、その上でF1(Pattern A/B/C)に説明させる。`Melo`の「benign単複+ratio」経路はM1が**意図的に使わない**(S-7 L2798「benign吸収は不受理」、OF-178=`OPUS_FINDINGS_LEDGER.md:205`)。根拠の逐語=`DECISION_LOG.md:20938`「受理理由はEXACT/NORMALIZED_MATCH…とPattern A/B/C…に限る。HIGH_SIMILARITY_SAFE…を理由とする受理は除外(歯擦音が続かない文脈[`Mello called`型]の真の/z/欠落を受理し得て原則2-4に反する)」。つまり**`drank`のように歯擦音が続かない文脈では、語末Sの脱落は『連結発音で説明できない=真の発音欠落かもしれない』とみなす**のがM1承認時にOpus BLOCKERとして採用された設計。
- 「語末s/zの差と綴りの違いが重なった場合」: `Melos→Mello`では綴り違い(os→o)と音素差(語末S脱落)が同一事象で、重なる別条件は発動しない。発動する条件は上表の5段のみ。

### C: `Melos → Mellows`【最重要】
**(c-1) 音韻同等性**: 音素列比較(`phoneme_compare_melos_01_result.json` `phoneme_diff_table`): `Mellows`(CMU未収録。分析専用に`mellow`+規則-s→`M EH L OW Z`を導出)と、Ledger候補4件のうち`M EH L OW S`との差=**語末S→Zの有声性のみ**(manner=fricative・place=alveolar同一、母音差0・音節数差0)。他3候補とは母音も異なる。
- **承認済み定義のどれにも該当しない**: (S-6)CMU完全一致→`mellows`未収録で不成立。(S-7)exactでない/`drop_final_S_or_Z`でない(Zが残る)/`add_s`でもない(`…OW S`+S/Z/IH Zの形でもない)。(S-4)Eq Layerは入口がUNCERTAINで不呼出、かつカテゴリA〜Gに有声性差は無い。(S-3)Pattern Aは綴り==`melo`の場合のみ。
- 「同等か」の判定: **ARPAbet上SとZは別音素**(bus/buzz)。実音声にも無声歯擦音が約105〜125msある(`acoustic_tail_part3c1_01_result.json`: 録音2は低域-54.3dB・自己相関0.19・高域-22.0dB=無声/s/様。/z/なら低域に有声バーが出る)。したがって**音声は`…OW S`型(Ledger候補と整合)で、`Mellows`(…OW Z)はAzureの語彙推定(自然な英単語`mellows`への寄せ)**。設計原則§2-4は例として`Melos`を`M EH L OW Z`(推定)と書くが、§3は推定を「確認済み発音」から除外しており、Ledgerの確認済み候補はSのみ。F1の`final_s_sound('Melos')=='/z/'`(`er011_b1…:35-48`、綴り規則)はSとZを区別せず歯擦音として扱うための実装で、発音の主張ではない。

**(c-2) 判定順序と棄却(Secondary `Mellows drank`、`_secondary_accept` secondary:977-991)**:

| 段 | 関数:行 | 実測 | 結果 |
|---|---|---|---|
| classify | validation.py:1137 | `_is_benign_plural_pair('melos','mellows')`=False(`_singularize_simple('mellows')=='mellow'`)。entity_only→`ASR_VALIDATION_UNCERTAIN` | 棄却(R6) |
| Case A | secondary:557 | `melos`・`mellows`ともCMU未収録 | 棄却(R7) |
| M1 | m1:371 `_enumerate_subs` | `avs=_variants(cmu,'mellows')=[]`→`asr_word_not_in_cmu`→`MULTI_CANDIDATE_NO_MATCH` | 棄却(R8) |
| Eq Layer・Tier3 | 呼出なし | `_secondary_accept`の許容集合はclassify/Case A/M1のみ(secondary:977-991) | - |

- **M1で`Mellows`が音素比較に入れない点は「承認時に意図的に対象外とした領域」であり見落としではない**: S-8(`SSOT_DRAFT_01.md:4`「C3(規則G2P)とASR側綴りの近似は不採用」)、S-7 L2797(「ASR転写からの後付け候補は存在しない」)、UDR #52、OF-184。M1承認の発動実績(Melos 12/12)も全て歯擦音が続く文脈で、ASR側OOVの救済は検証対象外だった。
- さらに、仮に音素が得られても語末S↔Zを同等とする規則は存在しない: `forms_from`(m1:293-309)は`exact`/`drop_final_S_or_Z`/`drop_ed`/`add_s`のみ。設計草案も「voicingを診断(自動許容しない)」(`er068_output/asr_phonetic_equivalence_generalization_01/DESIGN_DRAFT_01.md:60`)、ASR文字列に対する自動許容は「独立証拠未校正でREJECTED」(`DECISION_LOG.md:20795`、AUC0.74)。→ **仕様の空白だが、「許容と決めた」ことも「見落とした」ことも示す文はなく、検討時点で自動許容しない方針**。

**(c-3) 切り分け(既存結果の再掲、追加API 0)**: 録音2の同一wavをAzure(PhraseListあり/なし)で再転写→両方`Mellows drank`(Production記録と同一=再現)。OpenAI再転写は`Melo drank`(PASS側)。run_03 PASS版wavはAzure `Melos drank`、録音3は`Mellow strength`(takeごとに別綴りを決定的に返す)。音声に/s/あり(c-1)。PhraseList(`["Melos"]`、`phrase_list_used:true`、SDK `PhraseListGrammar`、`er006_secondary_asr_01.py:99-101`)は重み付けのみでper-phrase重み設定は無い(`CASCADE_CONFIG["phrase_list_weight"]=None`、同L288)。→ **原因は音声ではなくASRの語彙推定(PhraseList無効)**(出典`ITEM1_PHONETIC_EQUIVALENCE_ROOT_CAUSE_01.md` §4、`asr_consistency_part3c1_01_result.json`)。

**(c-4) 過去Melos Trial/runのPASSと今回NGの比較**

| 観測 | 文脈(次語) | OpenAI | Azure | 受理経路 | 出典 |
|---|---|---|---|---|---|
| M1隔離run Melos 12 take(2026-10-14) | `said`(/s/、歯擦音) | `Mello/Mellow/Mellos`等 | 多くは未取得 | **M1 `drop_final_S_or_Z`+F1 Pattern A** 21/21(全て`said`) | `er077_output/m1_oov_multi_pronunciation_01/EVIDENCE_RUN_01.md:12-17` |
| 同 nonsib `left`/`ran`/否定数値 ×9 | `left`/`ran`(非歯擦音) | 揺れ | **Azureがcanonical`Melos left.`等を返した8件**+EXACT 1 | **Tier3 `SECONDARY_ASR_CORROBORATED_MATCH`**。**M1受理0** | 同:26 |
| 同 repeat ×3 | `said`+`left` | `Mello said, Mello's left.` | `Melo said Melos left.` | M1は`F1_RESIDUAL_CONTENT`で却下、Azure正転写のPattern A | 同:27 |
| run_e2e_02 part3_c1(**同一文**`Melos drank`、2026-10-12) | `drank` | `Mellos drank` | (Tier3成立の含意としてcanonical`melos`) | `SECONDARY_ASR_CORROBORATED_MATCH` | `er026_output/family_z_production_e2e_01/melos/run_e2e_02/a2/audit/review_lock_state.json` |
| run_e2e_03 part3_c1(同一文、2026-10-17) | `drank` | `Mello drank` | **`Melos drank`** | Tier3 `SECONDARY_ASR_CORROBORATED_MATCH` | `run_e2e_03/a2/audit/review_lock_state.json`、`HR_LOCK_PART3C1_ROOT_CAUSE_01.md:44` |
| **run_e2e_04 att2(今回NG)** | `drank` | `Mello drank` | **`Mellows drank`** | なし(B/C全段で棄却) | E21行9613-9615、`HR_LOCK_PART3C1_ROOT_CAUSE_01.md:18-19` |
| run_e2e_04 att1 / att3 | `drank`(別内容語に誤認) | `Melo strained`/`Mello drank` | `Mellow Strength`/`Mellow strength` | 内容語不一致等で入口外 | 同:15 |

→ **過去のMelos PASSは(i)歯擦音`said`が続く文でM1/F1が働いたか、(ii)Azureがcanonical綴りを返してTier3が働いたか、のどちらか**。`drank`/`left`のような非歯擦音文脈で、OpenAI/Azureの両方が別綴りを返したケースを音素同等性で救った実績は**一度もない**(M1は設計上その文脈で働かない=OF-178)。今回の違いは仕様や配線ではなく「Azureが`Mellows`を返した」という確率的結果のみ(run_03/04は同一コード・同一Ledger、10-17以降のASR判定moduleは無変更=`HR_LOCK_PART3C1_ROOT_CAUSE_01.md:42`)。参考(n小): 同一文のPASS=run_02・run_03で各1take、run_04は3take全NG=2/5take。

**(c-5) 検証・承認した仕組みはProductionで意図どおり動いていたか**

| 機構 | 有効設定・実行時証拠 | 判定 |
|---|---|---|
| 統一ASR判定(Primary→Secondary 1回+cache) | steps `primary_1`/`secondary_1`、Azure `cached:true`、NG_BOTH(`review_lock_state.json`、`attempt_history`行15172-15176) | 設計どおり |
| Tier3 | E21行9613(Primary Mello、entity_only)→行9614 `tier3_corroboration`・`corroborated_by=[]`(再測: `corroboration_supports(Azure=Mellows)=False`、`(Azure=Melos)=True`) | 設計どおり(Azureがcanonicalを返さず不成立) |
| M1 | `m1_enabled`既定True(`er006_secondary_asr_01.py:488,727`)、`m1_enabled=False`を渡すProduction呼出元0件(リポ全Grep)、起動flag・`.env`非依存。凍結候補4件。Primary: 入口通過・置換案生成・`_post_check`で棄却(`m1_offline_replay_part3c1_10_result.json`)、Secondary: `asr_word_not_in_cmu` | 設計どおり(動いて棄却) |
| Case A/homophone | `melos`未収録でunresolved | 設計どおり |
| Eq Layer | 入口条件不成立で不呼出。Z経路の`enable_connected_speech_equivalence_layer`の値は本件結論に影響しないため未確認 | 不発(設計どおり) |
| PhraseList | `phrase_list_used:true`、SDK `PhraseListGrammar`に`Melos`投入(secondary:99-101)。Azureは効果なし(あり/なし同一) | 動作したが効果なし(重み付けのみ仕様) |
| Pronunciation Resolution Core(TTS側ヒント) | confidence=low・`min_confidence="medium"`で`hints_applied=False` | 仕様どおり不発(OPEN-318「TTS注入は別Phase」) |

→ **「設計どおり動かなかった機構」は0**。配線漏れ・設定OFF・順序バグは確認されない。

## §3 11-8不具合判定テスト表(R1〜R12)
水準: P=Production仕様 / D=設計原則(Production未採用) / T=Opus採用済み指摘。

| R | 棄却点 | ①承認済み仕様文(行) | ②実装挙動(関数:行) | ③矛盾 | ④判定 | ⑤是正に受理面/閾値/方式の新設・拡大を伴うか |
|---|---|---|---|---|---|---|
| R1 | Primary `Mello` classify | S-1(L2136): 単複の語尾差のみ吸収 | validation.py:691(`_is_benign_plural_pair`=False)→1137 entity_only→UNCERTAIN | なし | 仕様どおり | 吸収対象の拡大=新設 |
| R2 | Primary Case A | S-5(L1829)、S-6(L1831) | secondary:557→homophone_en.py:138: `melos`未収録でunresolved | なし | 仕様どおり | G2P/補完=新設(S-8で不採用) |
| R3 | Primary F1 | S-3(L2150): Pattern Aは次語頭が歯擦音 | er011_b1:153-159: `initial_sound('drank')='/d/'` | なし | 仕様どおり | Pattern A拡張=「新しい音韻パターンの追加は行わない」に反する拡大 |
| R4 | Primary M1 `_post_check` | S-7 L2798、OF-178、DECISION_LOG:20938 | m1:407-421 `R_NOT_EXPLAINED` | **P/Tとは矛盾なし。D(設計原則§2-3「Melo said:PASS/Mello said:UNCERTAINの非対称を作らない」)とは乖離** | 仕様どおり(P水準)。D水準との乖離=UDR #120(価値判断) | 受理拡張=A/A'(REJECTED) |
| R5 | Primary Tier3 | S-2(L2144) | er021:731(位置一致の完全一致)、Azure=`Mellows` | なし | 仕様どおり | 音素比較化=新方式 |
| R6 | Secondary `Mellows` classify | S-1 | validation.py:691/1137 | なし | 仕様どおり | 同R1 |
| R7 | Secondary Case A | S-5/S-6 | 両語CMU未収録 | なし | 仕様どおり | 同R2 |
| R8 | Secondary M1(ASR側OOV) | S-7 L2797、S-8、UDR #52、OF-184 | m1:371 `asr_word_not_in_cmu` | なし(承認時の明示的不採用) | **承認時に意図的に対象外** | G2P=P2(REJECTED) |
| R9 | S↔Z有声性差 | S-4(voicing除外はassimilation関数内のみ明記)、DESIGN_DRAFT_01:60「自動許容しない」、DECISION_LOG:20795 | m1:293-309 `forms_from`にvoicing形なし | 許容も禁止もProduction本文に明文なし | **仕様の空白**(検討時は自動許容しない方針) | 許容基準新設=P2(REJECTED) |
| R10 | Secondary Eq Layer | S-4(L2151): 入口TRUE_CONTENT_MISMATCH限定 | secondary:799、eq:163-168、`word_phones('melos')=None` | なし | 仕様どおり | 入口拡大=新設 |
| R11 | 統一judge NG_BOTH | S-9(L2814) | er078:352/523 | なし | 仕様どおり | Primary#2復活=廃止決定の覆し |
| R12 | Resolver/TTS hint | OPEN-318(TTS注入は別Phase) | er025:462 `min_confidence="medium"`、Melos=low | なし | 仕様どおり | 注入の新設=別Phase |
| 補S1 | `Melo`のbenign PASS(対比) | S-1 | validation.py:691→1148、ratio≥0.98(50語以上) | S-1の字義の範囲内。固有名詞適用・文長依存は本文に記載なし | 仕様どおり(適用範囲の明文化なし=UDR #120の論点)。厳格化しない | 厳格化=承認済み許容の独断変更(禁止) |

集計: **不具合0 / 仕様どおり10(R1〜R7,R10〜R12) / 承認時に意図的に対象外1(R8) / 仕様の空白1(R9)**。Melo PASS/Mello NGの非対称(OPEN-330)は、**Production仕様文(S-1・S-7 L2798・OF-178)とは矛盾せず、設計原則(S-10 §2-3)とは乖離する**。乖離の水準はP(Production)ではなくD。

## §4 是正
11-8不具合(承認済み仕様文・設計原則との矛盾のうちProduction仕様水準のもの)=**0件**。修正・Regression・offline再判定は実施しない(コード差分0)。根拠=§3表。「仕様の空白・D水準の乖離」をコードで埋めることは受理面・方式の新設/拡大(11-8範囲外)にあたり、A/A'/P2としてユーザーがREJECTED済み。

## §5 ユーザー判断候補
**該当なし。** 理由:
1. 不具合0件で、Production仕様内で救済できなかった理由は§2・§6で説明できる。
2. A/A'/P2が「根本原因の解決に必要」とは証明されていない。録音2の直接原因は「Azureがcanonical綴りを返さない確率事象」と「非歯擦音文脈でM1が働かない承認済み設計」であり、承認済みフロー(NG→最大2回再TTS→Rewrite)と②③の是正が機能すればHR Lockには至らない。
3. Melo/Mello非対称(UDR #120)は実データ上、69語のpart3_c1の1文のみ(§2-A 5)。短い文では`Melo`も`Mello`も同じくUNCERTAIN。再提案する場合は、この実測(影響範囲が狭いこと、P1が効くのもPrimary側かつ50語以上の文のみ)を材料に「必要性」を再評価し、原因・既存仕様との関係・他案比較・QCDを揃えること(A/A'の別名での推奨はしない)。

## §6 ①の結論(ユーザー向け)
録音2で救済されなかったのは、承認済みのルールが壊れていたからではなく、承認済みのルールが元々その場面をカバーしていなかったからです。Primary側の`Mello drank`は「語末のSが落ちた」形で、M1は承認時のOpus指摘(OF-178、`CURRENT_SPEC.md:2798`「benign吸収は不受理」)により、歯擦音が続く文(`Melos said`型)でのみ連結発音として許容し、`drank`のように歯擦音が続かない文では「真の発音欠落かもしれない」として許容しない設計です。Secondary側の`Mellows drank`は、(a)`Mellows`がCMU辞書になく、M1は「ASR側綴りの近似・G2Pは不採用」(`SSOT_DRAFT_01.md:4`、UDR #52)と承認時に決めていたため音素比較に入れず、(b)音素で比べても`Melos`のLedger候補(語末は無声S)と`Mellows`(語末は有声Z)は別音素で、Sの有声性違いを同等とする承認済み規則がなく(「同じ音韻現象には同じ判定」は設計原則=`DESIGN_PRINCIPLE_AGREED`でProduction仕様ではない)、(c)実際の音声には無声の/s/があるためAzureの語彙推定の誤りと判断でき、PhraseListも効きませんでした。過去の同一文のPASS(run_02・run_03)は、どちらも音素同等性ではなく「Azureがcanonical綴り`Melos`を返したTier3」による合格で、今回はAzureが`Mellows`を返したためその救済経路が成立しませんでした。救済の仕組み(Tier3・M1・Case A・PhraseList)は全て設計どおり動作しており、動かなかった・配線漏れの機構は0件です。なお`Melo drank`が通り`Mello drank`が通らない非対称は、普通名詞の単複の揺れ用の規則(`CURRENT_SPEC.md:2136`)が50語以上の長い文で固有名詞にも当たる副作用で、Melos含有6文のうち今回の1文でのみ顕在化しています。また、却下済みのP1(A案)で救済され得るのは録音2のPrimary側(`Mello`)だけで、Secondary(`Mellows`)はP1では救済されず、P2(REJECTED)の領域でした。
