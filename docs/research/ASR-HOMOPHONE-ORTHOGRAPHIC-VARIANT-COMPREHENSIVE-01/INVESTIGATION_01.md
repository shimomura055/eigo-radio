# INVESTIGATION_01(ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_01、2026-10-22。調査・設計・未配線プロトタイプのみ。API 0・費用0・Production既存ファイル編集0)

確認済み=実コード読取/実行の観測値、推測=近似を含む見積。再現script(すべて`.venv\Scripts\python.exe`、API 0): `er109_pattern_probe_01.py`(→`pattern_probe_01.json`)、`er109_stored_census_01.py`(→`stored_census_01.json`)、`er109_kp_corpus_eval_01.py`(→`kp_corpus_eval_01.json`)、`er109_machine_pairs_eval_01.py`(→`machine_pairs_eval_01.json`/`..._representative_01.json`)、`er109_gate_exposure_01.py`(→`gate_exposure_01.json`)。ユーザー原文=`docs/pm/delegation_log/2026-10-22_ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01_USER.md`。

## 1. 結論(先に)

1. **同一発音なのに表記差でNGになる原因は『1か所の穴』ではなく、判定が層ごとに別の表記正規化を持っていることにある**(確認済み)。数字<->語はTier1(5 role限定)・`normalize_numeric`(単独`one`は変換しない)・値ガードatom(`one's`をliteral扱い)の3箇所が別々の規則、同音語はCMU 1:1(内容語のみ・stopword除外・1語テキストはratio<0.4で到達不能)、記号/略語は通り種別略語のみ。結果、`one's`<->`1's`のように**どの層も同値化しない**パターン、Key Phrase/Whisper票だけTier1が効かないパターン、承認済み規則でPASSしたのに**非KPの最終ゲートが再否定する**パターンが残っている。
2. 『発音(CMU音素列)の同一性』を共通の判定基準に据えた**1つの共通層**(`er109_asr_orthographic_equivalence_01.py`、未配線プロトタイプ)で、これらを構造的に解消できる見込み。機械生成の正例(KP 1,128・本文2,099)で同値率 **KP 100%・本文99.2%**(既存は KP 90.7%・本文85.4%)、負例(KP 3,049・本文3,749、数の変更・否定の脱落/付加・語置換・音素1つ違い・内容語の脱落/挿入)で**新規誤同値0**。既知の問題音声(take part->Take Tart等21件)も**0件の新規PASS**。
3. 保存ASR記録(英語4,877 attempt、Z含む)の実測: 不合格attempt 914のうち、**発音同値なのに表記差でNG(現行コードでも不合格)だった行が24(distinct pair 13・21 segment)**、うち最終STOPPED/HRに至ったsegmentが3(Z `kp3_en` `seize`<->`sees`のHUMAN_REVIEW_LOCKEDを含む)。Azure(Secondary)転写が表記差のみで同値なのに不合格だった行が6(`Pump 1's fist.`4・`Brace oneself 4.`・`Sees.`)。**KP英語のNG行6**(`third places`<->`Third place is`、`point to`<->`Point 2.`、`seize`<->`sees`/`Seas`等)。
4. 既存承認仕様の**不具合(B)**を3件特定(分類のみ、修正は次委任): (B-1)複合序数`twenty first`<->`21st`が分類はPASSなのに非KPの最終ゲートでNG_PROTECTED、(B-2)承認済み同音救済・多語同音救済が**1語/短文では到達不能**(ratio<0.4のTTS_FAILUREが先、KP英語の12.6%=83/660句が1語)、(B-3)`60 percent`<->`60 %`(空白付き%)が同型の層間不整合(頻度は低い)。
5. 新規救済範囲(C)は『KP/Whisper票へのTier1相当の適用』『`one's`/`1's`型』『記号・略語・stopword同音』など。提案層は**Family別パッチでなく`classify_asr_match`ラッパーの1点**に差し込めば、OpenAI/Azure/Whisper票・Store再利用・X引継ぎ・retry/fallback/resumeが同じ判定原則を通る(§3)。

## 2. 既存機構の地図(file:行。表記差の同等化と、同一発音が不一致になる箇所)

| 層 | 場所 | 同等化している表記差 | 同一発音なのに不一致になる箇所(確認済み) |
|---|---|---|---|
| 正規化 `normalize_text` | `er006_preprod_hardening_01_validation.py`(以下val) :410 | 大小・ダイアクリティクス・`’`/引用符・ハイフン/記号(:437 `[^a-z0-9]+`→空白)・英米綴り13組(:56 `BR_AM_SPELLING_PAIRS`)・通り種別略語(:77 street->st、**一方向のみ**) | `&`/`+`/`°`/`vs.`/`Dr.`/`St.`(Saint)/`OK`は未対応。アポストロフィも空白化されるため`one's`->`one s`、`1's`->`1 s` |
| 数詞<->数字 `normalize_numeric` | val:336、`_convert_cardinal_words` :296 | 基数2語以上・100以上・序数・複合序数(:155)・`N percent`/`N%`・`$N`・小数・指数 | **単独`one`は変換しない**(:313 `seq[0]=="one"`、代名詞曖昧)。よって`one`<->`1`は常に不一致。年代`90s`/時刻`5:30`/セント`$5.50`/`2's`は変換対象外 |
| Tier1 数値等価 | val:1301-1303(`classify_asr_match`冒頭)、`er021_en_asr_semantic_equivalence_production_01.py`:635、role gating `er020_tts_retry_local_rewrite_01.py`:125-150 | 数値/通貨/%/年/時刻/分数/ローマ数字/略語の値パース一致(`NUMERIC_EQUIVALENCE_MATCH`)。**適用は5 role(Full Story/Comment/Preview/Topic intro/In One Line)限定**。Key Phrase/Headingは非適用(承認済み。`CURRENT_SPEC.md:2159`) | **Key Phraseとその3票(P/S/Whisper)ではTier1が一切効かない**: `one`<->`1`、`2 million`、`2024`、`1/2`、`1%`、`1 on 1`等がKPで不合格(§3 probe)。時刻`five thirty`<->`5:30`、`$5.50`は本文でも未パース |
| 同音救済 1:1 | val:740-754(`protected_check`内`homophone_en.homophone_arpabet_equivalent` `er008_asr_variant_hardening_15_homophone_en.py`:73) | 内容語1:1置換でCMUいずれかのvariantが一致(wait/weight) | stopword(to/for/by/are/so/there…)は`canon_content`から除外される(val:600 `_STOPWORDS`、:744)ため**`to`<->`tew`/`they're`<->`their`/`by`<->`buy`は対象外**。同音候補は`ASR_VALIDATION_UNCERTAIN`止まり(val:1193)で、PASSは`_step_alternate_pass`(`er006_secondary_asr_01.py`:661)の追加判定 |
| ratioゲート | val:1133 `ratio < tts_failure_threshold(0.4)`->`TTS_FAILURE` | (幻聴検出) | **同音判定(val:1193)より先**。1語テキスト(`wait`/`weight`)は常にTTS_FAILURE。KP英語660句中83句(12.6%)が1語。保存KPの1語homophone swap再現=既存0/12・提案12/12。**実害の保存実例: Z `kp3_en` `seize`<->`sees`がTTS_FAILURE->HUMAN_REVIEW_LOCKED** |
| 多語同音 PNMH-01 | `er094_multiword_homophone_01.py`:71/101/120、val:758 | 1語<->連続2〜3語のCMU一致(ByUs/buy us)。安全条件(単一文字token禁止・canonical3字未満禁止・V8 FW2・entity代表発音) | 同上ratioで短文は到達不能。`all right`<->`alright`、`by us`<->`buy us`(一般語)は不合格 |
| 複合語分かち書き | val:1067-1091(despaced)・:655(span単位) | `well-being`/`wellbeing`/`well being`、冠詞除去後の連結一致 | 発音一致でも綴り連結が違えば不可(oronym) |
| contraction展開 | val:937 `expand_standard_contractions`、:1337-1343(wrapper) | `I'm`<->`I am`等(否定保持・展開後に既存が一致した場合のみ) | `it's`<->`its`はdespacedで救済されるが、**`they're`<->`their`/`you're`<->`your`/`who's`<->`whose`は不合格** |
| 数字ゲート例外(Track B) | val:836 `_try_homophone_number_rescue` | 数詞語<->CMU同音語(two<->to、four<->for) | 数字token<->語のみ。`1's`は対象外(rawが`1`でCMU未登録) |
| 連結音 B1/CS Equivalence/M1/Tier3 | `er011_connected_speech_equivalence_layer_production_01.py`、`er006_m1_multi_candidate_01.py`:258、`er006_secondary_asr_01.py`:992(CS)・:1034(Tier3)・:1107(cascade_eligible) | 子音連続・再分節・複数発音候補・規則複数形(いずれも**同一発音ではなく近似/corroboration必須**) | 本調査の対象外(発音一致の判定ではないため。共通層の後段に残す) |
| 値ガード+否定差(最終ANDゲート) | `er078_asr_unified_judge_01.py`:348 `_protected`・:317 `negation_diff`・:445-454(ゲート)、`er078_asr_value_guard_01.py`:339 `_en_sequence`・:475 `_guard_en`、承認済みbasis除外 :68 `APPROVED_EQUIVALENCE_BASES` | 値atom同値(1==1) | **`one's`はliteral1語、`1's`はnumber atom**→`hyp_drop(b)`=DIFF(AZURE_ITN_IMPACT_01 §2)。**複合序数`twenty first`をatomが20+literalと解釈→`21st`と値DIFF**(実judgeで再現: Primary=NORMALIZED_MATCH->`NG_PROTECTED/final_gate_value_diff`)。`60 percent`<->`60 %`はform_differs |
| KP票 | `er104_kp_three_asr_vote_01.py`:232 `_classify`・:244 `make_voter` | `classify_asr_match`+`_step_alternate_pass`(票は本文一致のみ。値/否定は監査のみ=2026-10-22解除) | **`_classify`は`segment_id`を渡さない**(Whisper/KP票はTier1非適用で一貫)。M1/CS/Tier3は票側に無い(Primaryのみ) |
| 再利用/引継ぎ | `er006_master_audio_store_01.py`:126-130、`er078_reuse_value_guard_01.py`:32 `guard_entry`、`er019_family_x_validation_inheritance_01.py`:305-344、`er104_kp_vote_reuse_01.py`:109/173/192 | 保存転写を現行judge/`classify_asr_match`で再判定(API 0) | 上記すべての穴を**そのまま継承**(非KPは値ガードで再利用禁止になり得る=再生成コスト) |
| A/B/C共有 | `classify_asr_match`呼出ファイル81(Grep。`er003_*`/`er008_*`等の生成・resume・再検証)。27-7で開発停止中 | 同一関数 | 共通Validatorの変更はA/B/Cにも波及(§6) |

## 3. 票ごとの判定原則の差(確認済み)

- **Primary(OpenAI)**: Tier1(5 role)+baseline+contraction+B1連結音→CS Equivalence層→Tier3→非ラテンKP→CMU同音(`_step_alternate_pass`)→M1(`er006_secondary_asr_01.py`:870〜)。
- **Secondary(Azure)**: `_secondary_accept`(:1172)=`classify_asr_match(segment_id付き)`+`_step_alternate_pass`+M1。**Primaryと同じ分類器だがsegment_idの有無でTier1が変わる**(本文はあり、KPは非適用)。
- **Whisper(local、KPのみ)**: `er104._classify`(:232)=`classify_asr_match(segment_idなし)`+`_step_alternate_pass`。**M1/CS/Tier3/Tier1なし**。
- 結論: **3票とも`val.classify_asr_match`を通る**。従って`classify_asr_match`ラッパーに1層足せば全票・再利用・引継ぎ(§2最下段)に同一原則が掛かる(Family別パッチ不要)。個別に差があるのは前置の層(Tier1のsegment_id、M1/CS/Tier3のPrimary専用)であり、共通層はそれらの**後ろ(不合格時のみ)**に置けば既存の合格を減らさない(構造的に、PASS->NGへ変える経路が存在しない)。

## 4. ASR各社の表記整形(ITN)の傾向(保存ログ、`stored_census_01.json` summary.itn_profile_by_provider)

『期待文に無い特徴が転写にだけ現れた件数』(母数=転写数):
| 提供 | 母数 | 数字 | % | 通貨記号 | 時刻`h:mm` | em dash | ハイフン |
|---|---|---|---|---|---|---|---|
| OpenAI Primary(全保存attempt) | 4,800 | 145 | 20 | 2 | 6 | 11 | 73 |
| Azure Secondary(全保存) | 225 | 7 | 1 | 0 | 0 | 0 | 0 |
| KP保存コーパス OpenAI | 96 | 0 | 0 | 0 | 0 | 0 | 2 |
| KP保存コーパス Azure | 96 | **8**(すべて`Pump 1's fist.`型) | 0 | 0 | 0 | 0 | 0 |
| KP保存コーパス Whisper small | 11 | 0 | 0 | 0 | 0 | 0 | 0 |
解釈: OpenAIは本文で約3%に数字化(Tier1が5 roleで受ける)、AzureはKP短句で数字化(`1's`)、Whisper smallは小標本(11)でITNなし(Title Case出力。標本が小さく**推測**)。Azureのlexical形取得(C1)は本方式に**包含されない補完策**(同一Azure呼出のoutput設定変更。表記ではなく入力側を直す案)。ユーザー決定済みの③『Azure整形前テキスト併用』はREJECTED(DECISION_LOG末尾・UDR #155)であり、本方式は**転写の表記差を発音で吸収する側**に立つ(別案)。

## 5. 保存データの実測(§3、API 0。`stored_census_01.json`)

母集団: `**/*tts_generation_results*.json` 370ファイル(本文segment+KP英語のattempts_log、canonical=`text`/`canonical_text`、転写=`asr_text`。Z等でattempts_logが無いKP英語は`narration/attempts/<seg>_attempt*.json`で補完)と各runの`narration/attempts/*.json`の`cascade_steps`(Azure)。英語attempt行 **4,877**(distinct pair 2,191、KP行1,003)。Family A/B/C/X/Zを区別せず保存分すべて(トップdir別: er011 1,203・er019(X) 1,023・er026(Z) 939・er006 471等、内訳はjsonに記録)。Zの本文segmentは日本語canonicalのため英語行はKP英語が中心。

| 指標 | 件数 | 備考 |
|---|---|---|
| 保存分類が不合格/未verifiedのattempt | 914 | うち現行コードでも不合格 829(85件は旧コード由来で現行は合格) |
| 上記のうち**提案層が発音同値**と判定 | 90 | うち**現行コードでも不合格=偽NG候補 24**(distinct pair 13、distinct segment 21)。残り66は現行コードでは既に合格 |
| 偽NG候補のルール別 | number_spoken_form 14 / cmu_homophone 7 / compound_spacing 3 / multiword_homophone_er094 2 / abbreviation 1 | 例: `fifth`<->`5th`、`One`<->`1`、`to`<->`2`(`point to`<->`Point 2.`)、`study's`<->`studies`、`places`<->`place is`、`fruit-versus-vegetable`<->`fruit vs vegetable`、`seize`<->`sees`/`Seas` |
| そのうち最終STOPPED/HRに至ったsegment | 3(行5) | full_story_part2 x2(er003 `fifth`->`5th`・`1`<->`one` / er005 `study's`<->`studies`+`parent-child`)、**Z `kp3_en` `seize`<->`sees`(TTS_FAILURE、HUMAN_REVIEW_LOCKED)** |
| KP英語の偽NG行 | 6 | `third places`<->`Third place is`(2)、`point to`<->`Point 2.`(kp5)、`seize`<->`Seas`/`sees`(Z、1語テキスト=ratio<0.4でTTS_FAILURE) |
| 保存の救済行(Secondary/連結音等で救済) | 167 | 提案層で同値かつ現行不合格 0(救済は既に現行で効いている) |
| Azure(Secondary)転写が表記差のみで同値なのに現行不合格(自明な完全一致を除く) | 6 / 225 | `Pump 1's fist.`x4(coffee NG3)・`Brace oneself 4.`(X nws kp2、`for`<->`4`)・`Sees.`(`seize`) |

KPコーパス(`noguard_reeval_01.json`、P/S/Whisper転写203件): 提案層で**新規にPASSになるのはNG3 coffee `Pump 1's fist.`の7件のみ(`ng3_case`)**。**問題音声21件由来の転写45件は新規PASS 0**(同値と判定された3件は既存でも合格しているASR非検出例)。

偽NGの絶対頻度は小さい(全attemptの約0.5%)が、1件が**regenerate、時にSTOPPED/HR**を呼ぶ(上表の3 segment、およびコーヒーNG3のHR 2 segment=本表の「Azure同値」と同件)。提案層は追加API 0で、Secondary(Azure)呼出が不要になる側に働く(増えない)。

## 6. A/B/C共有Validatorの互換性(確認のみ、開発は開始しない)

- 提案層は`classify_asr_match`の**不合格時のみ**呼ばれ、合格へ変える方向にしか作用しない(構造保証: 既存合格の返り値は無変更)。従ってA/B/Cの既存合格がNGに変わる経路は無い(挙動差分は『NG->PASS』のみ)。
- 保存データ上のA/B/C該当行の偽NG候補: トップdir別 er003 3・er005 3・er006 2・er011 10(いずれも旧A/B/C系=18)、er019(X) 3、er026(Z) 2、er071 1(系統未確認)。A/B/Cが『同じ改善を受ける』か『挙動差分0を維持するか』は**Fable/ユーザー判断事項**(27-7: A/B/Cは最新仕様へ追従させない方針との整合)。挙動差分0を要件にするなら、配線時にsegment_id/family由来のopt-in(呼出点plumbing)が必要=Family別パッチに近くなる点がトレードオフ。

## 7. 制約・未再現範囲

- 既存経路の再現は`classify_asr_match`+`_step_alternate_pass`(+非KPの最終ANDゲート)まで。M1(凍結候補要)・CS Equivalence/Tier3(wav/Secondary要)は再現していない(それらは発音同一ではなく近似/corroboration層で、提案層の後段に残す前提)。
- Whisper票はKP保存コーパスの11件のみ(`A_whisper`)。Whisper small全般のITN傾向の統計は**未確認**。次委任で保存wav(KP数値/所有格)に対するローカルwhisper実行(API 0・費用0)を検討可。
- 保存分類(`audio_classification`)は旧コード由来を含むため、偽NG候補は『現行コードでも不合格』に絞って計上した。census実行時点(2026-10-22)の保存ファイル数に依存する(並行タスクが追加するresultsで母数は増える)。
- 同一ファイルを並行タスク(OPEN-458 KPQ 委任_02)が編集中のため、Production既存ファイルは**読取のみ**(testで『er109をimportするProduction fileが0』を固定)。
