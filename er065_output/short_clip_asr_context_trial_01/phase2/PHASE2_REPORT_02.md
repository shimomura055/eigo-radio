# PHASE2_REPORT_02: FAMILY-Z-SHORT-CLIP-ASR-CONTEXT-GENERALIZATION-TRIAL-01 委任_03

日付 2026-10-13 / 親: EIGO-RADIO-QUALITY-CROSS-FAMILY-FOLLOWUP-01 ④ / 既存Trial(`../TRIAL_REPORT_01.md`)への統合(新Trial新設なし)。
Status: **Production無変更(既存仕様の是正なし)/ 新しい許容条件はTrial(`er065_..._p2_phon.py`)に閉じ、Production未配線 / 自動許容側は独立証拠未校正のため REJECTED(単独gateとして)、HR優先度付けとしての利用は USER_DECISION_REQUIRED**。「VALIDATED」「APPROVED」は使わない。
費用 JPY 8.21 / 20(Melos累計 約233.2 / 300)、TTS生成0、Production state書込0(`state_guard_02.json`)。

評価モデル: OpenAI `gpt-4o-mini-transcribe` / Azure Speech STT(en-US)= **Production同一モデル**(最新モデル原則の例外理由=比較可能性: Productionの実判定条件で評価するため)。local faster-whisper small/medium は無料の第三者参照(Production対象外)。

## 0. 結論(先に要点)

1. **基本原則(子音連続の融合・弱化・脱落を、音韻診断で正常な連結発音と説明できれば許容)は、現行Productionでは「綴り水準の限定3パターン」としてしか実装されていない**(A)。欠けている層は、(a)綴り水準 vs 音韻水準、(b)Equivalence Layerの入口条件(`TRUE_CONTENT_MISMATCH`限定。固有名詞差=`ASR_VALIDATION_UNCERTAIN`には届かない)、(c)OOV固有名詞のG2P欠如(`melos`がCMU未収録)。**配線漏れ・判定順序のバグは新規発見なし**。判定順序(entity gateが先)は「受理可能だったのに遮られた」実例0件(実データ・合成とも)。
2. `Melos said` -> `Mello`/`Mellow`/`Melo said` は、Trial音韻判定で**語末/s/ + 語頭/s/ の融合(/m ɛ l oʊ s s ɛ d/ -> /m ɛ l oʊ s ɛ d/)として説明できる**(PHON_EXPLAINED_FUSION)。`meloset`/`Mellowset`は融合+`said`の/d/無声化(PHON_EXPLAINED_VOICING)。一方 `Mellis`(母音相違)・`Melon`/`Marcus`/`Mel`/`Melos aid`/`Melos.` は説明不能(NOT_EXPLAINED)で、**独立証拠が最大と仮定しても許容にならない**(回帰test固定)。
3. **ただし「ASR文字列だけでは、融合で聞こえにくいだけの正常音声」と「語末sを実際に落とした音声」を区別できない**ことは、今回の全データで変わらない。区別に使える独立証拠として、既存wav 215本・s+s 250境界 vs 単独s 2,007境界から**摩擦区間長を較正したが、AUC=0.74(bootstrap 95% 0.69-0.77)で単独gateには使えない**(同一clip内の差は平均+51ms・78%で融合側が長い=現象は実在するが、絶対閾値は話者・速度・語で揺れる。human承認済み b1b_att1 の測定値は 0ms で、正常音声が閾値を満たさない偽陰性実例)。**よって、音韻説明可の転写は「許容」ではなく「HR候補(説明付き)」に止めるのが現状唯一の安全な運用**。
4. **ASR評価単位(B)**: 短尺2語clipの不安定さの主因は**s+s融合ではなく、短さ+OOV固有名詞**。OpenAIはMelosの後ろがs始まりでない2語cut(called/turned/had/listened/fell)でも exact 0/16・Melos語一致 1/16(6%)で、`Melos said`(0/13)と有意差なし。Azure+PhraseListだけは s+s の影響が検出された(Melos語の綴り一致: `Melos said` 2/14=14% vs Melos+非s 2語cut 6/8=75%、Fisher p=0.008)。一般語でも 2語窓は全型で不安定(融合型 exact 41% vs 対照 52%、有意差なし p=0.37)。
5. **NG時Fallback(C)**: 同条件繰返しはNG take 5本中 **0本**救済(OpenAI 0/9、Azureは決定的で同一)。前後音声付き・別engineは一部take(att6 17/45 等)で exact になるが、真値不明(att6)・プライミング(文脈にMelos含む)が混在し**どの方式も再現性ある救済にならない**。評価条件を変える文脈付き音韻判定は、同条件繰返しで救済できなかった不一致のうち**NG take転写の33〜100%(take・engine別)を「連結発音で説明可」に分類**できるが、これは救済ではなくHR候補の絞り込み/説明付与。
6. **再発防止(D)**: Production実データ(英語2,030対)で語境界の子音連続は 7,412 境界、境界付近に綴り差が出た割合は型別 1.1〜8.9%(上限値)。実データの差分 124 instance のうち「連結発音で説明可」と判定されたのは17(Productionが既に受理6、現行未受理11[Melos関連7、一般語4=`products stores stock`・`some Muse calls`(m+m、2出所)・`pay showed coffee`(d+k)])。**Melos以外の固有名詞の実例はProduction実データに存在しない**(OOV固有名詞への一般化は合成評価のみ)。回帰test 19件を `er065_short_clip_asr_context_trial_01_regression_test_01.py` に固定(全PASS)。

---

## A. 既存連結発音対策の徹底監査(¥0)
詳細表(5機構 x 8点)と「Melos said -> ASR別綴り」の音韻説明表: `A_AUDIT_02.md`。要約は上記結論1・2。
- 「接尾辞s vs 語幹末s」(点6): Pattern A・Semantic Equivalence とも**区別しない**(`bus stops`<-`bu stops` もACCEPT。OPEN-330)。Trialの音韻判定は形態素ではなく音素列で判定する。ただし D-2b のとおり、`The studies suggest -> The study suggests` のような**複数形/三単現の付替え**(ProductionはPattern Aで受理)は、語境界の子音融合では説明されない形態素差であり、Trial音韻判定では NOT_EXPLAINED になる(両者は別の規則=Trialは現行Pattern Aを置換しない、拡張の候補としてのみ位置づける)。
- 配線漏れ候補(是正候補。**いずれも実施していない**): (1) OPEN-122(4) 減速後cascade(`_post_slowdown_cascade_rescue`)へ Equivalence Layer flag 未配線 - 今回の事象(UNCERTAIN)ではEq Layerは入口条件で発火しないため、配線しても効果を確認できない。(2) OPEN-322 Dialogue本文が `segment_id` を渡さずTier3/role gatingが効かない - 本件(narrator clip)に無関係。(3) OPEN-328 観測性(各層の `connected_speech_enabled` 実値・`layer_invoked` 未記録)。これらは既に追跡中のOPENで、新規バグではない。

## B. ASR評価単位(オフライン既存音声の切出し・結合、ASR上限内)
全表: `analysis_b_02.md`、生データ `b_records_02.json`、`results_01_*_02.jsonl`。cutの再現: `er065_..._p2_make_config_b.py`(`b_cuts_*`、v1は終端が語末+0.06秒で`-ed`が欠け得たため参考、v2が主)。

### B-1. 評価単位別(Melos main + 一般語。exact=target領域が canonical と綴り全一致)
| 評価単位 | OpenAI exact | Azure+PL exact | Azure Melos語一致 | 備考 |
|---|---|---|---|---|
| `Melos said.` 単独2語 (7 take) [委任_01] | 0/13 | 2/14 (14%) | 2/14 (14%) | s+s融合あり |
| `Melos said.` +直前台詞 (1文単位, gap300) [委任_01] | 2/13 (15%) | 1/4 | 1/4 | att6のみ OpenAI 2/2 |
| `Melos said.` +直前台詞 (1文単位, gap80) [新規] | **0/14** | **0/7** | 0/7 | gapを詰めても改善せず(現実の文に近い条件) |
| `Melos said.` +直後台詞 gap80 / 前後 gap80 [新規] | 0/14 / 0/14 | - | - | |
| `Melos said.` 前後2-3clip (28秒) [委任_01] | 10/25 (40%) | 1/4 | 1/4 | 文脈にMelos語を含む条件に偏る(プライミング) |
| **Melos + 非s始まり 2語cut v2** (0.75-1.2秒) [新規] | **0/16** (Melos語一致 1/16) | 2/8 (Melos語 6/8) | 6/8 (75%) | 長さ=`Melos said`と同程度、s+s融合なし |
| Melos + 非s始まり 元clip全体 (2.7-4.6秒) [新規] | 2/8 (25%) | 4/4 (100%) | 3/4 | 長さ+約2倍 |
- **長さ vs s+s融合の分離**: OpenAIは「s+s融合なし・2語」でも0/16 = 短さ+OOV固有名詞が主因(s+s融合の寄与は検出不能: floor effect)。Azure+PLでは s+s の寄与が有意(p=0.008)。→ **短尺不安定は「長さ」と「s+s融合」の両方が絡み、engineで寄与が異なる**(委任_01の交絡指摘に対する実測回答)。
- OpenAIの出力例(非s文脈でも): `Mellow's turn` / `Maloz listen` / `My los listen` / `Mallows turn`(語末sは**聞こえて**`'s`/`z`として書かれる = 融合していない文脈では語末sは保たれ、綴りだけがOOV名として揺れる)。
- **一般語**(Production採用済み正常音声の実境界、0.5-1.6秒の2語窓、`analysis_b_02.md` B-P2-4): 融合型6種(SS/TT/DD/NN/YOD/SHS) OpenAI exact 57/144 (40%)、対照(CTRL: 融合しない境界) 12/24 (50%)、Fisher p=0.37。2語窓は**一般語でも不安定**(余計な前後語を足す/語尾を落とす: `by this small`, `top users state`, `meant to be`, `sunlight touch` 等。これらは連結発音で説明できない**ASR側の別語化**)で、融合型固有のペナルティは検出できなかった。注意: 連続音声から切り出した窓であり、TTS生成の2語clipとは境界の自然さが異なる(proxy)。
- 編集音声実験(`B-P2-5`): 融合長の摩擦区間を単独s相当(80ms)まで短縮した Melos said(5 take)でも、OpenAIの出力は多くの take で元と変わらず(att1/3/4: `mello said`)、**ASR文字列は融合と単独sを区別しない**。Azure+PL は att1 のみ `Melos said`->`Mello said` に変化(att1 が実際に融合長だった可能性と整合)。

### B-2. 「最初から長い範囲(1文または段落)でASR評価する方式」の設計案(clip分割は維持、ASR単位だけ変更)
実測からの評価: 1文単位(直前台詞+attribution)は gap300/gap80 とも OpenAI 0〜15%、28秒窓でも40%(プライミング混在)で**正認識率の改善が不安定**。Azure+PLは非s文脈の長clipで良好(4/4)だが `Melos said` を含む窓では 25% 程度。→ **推奨しない**(下記整合・費用・masking)。検討する場合の設計:
- 窓の作り方: 同一ナレーター連続clipを結合(現行の `concat_parts` 相当を ASR 前処理に置く)。対象clipのspan(`target_span`)を結合時に記録し、ASR結果は `region_by_words`(Azure/whisper word timestamp)または difflib整列でclip単位に割り当て(既存実装あり)。
- **retry/fallback/LR**: 窓NGでも責任clipの特定が必要(窓内の差分位置->clip span)。TTS retry上限3・cooldownはclip単位のまま。窓評価は「隣接clipが再生成されるたびに再評価」が必要=連鎖再評価。Local Rewrite の7 Gate・QAは clip 単位のまま変更不要だが、LR後の再ASRも窓単位になり費用増。
- **Master Store**: 再利用キーはclip単位(sha256)。窓合否は隣接clip次第で変わるため、「clip単独PASS」を再利用判定に使えなくなる(窓合否の履歴をclip単位に紐付けるキー設計が必要)。**HR Lock**: 対象は責任clip。人間承認(attempt採択)はclip音声のsha256に紐付くが、窓が変わると再評価対象になり承認が無効化される恐れ(OPEN-331と同型の問題)。
- **費用**: OpenAI ¥0.004/秒、Azure ¥0.044/秒(実測回帰)。2秒clip -> 28秒窓で ASR呼出あたり OpenAI ¥0.008 -> 約¥0.11、Azure ¥0.09 -> 約¥1.2(いずれも約14倍)。窓が重なるclip数だけ再評価が増えるため、1記事あたり数十clipで ASR費用は一桁増。処理時間も比例(OpenAI/Azure とも音声長に概ね比例、窓28秒で数秒〜十数秒)。
- masking: 文脈にMelosを含む窓は OpenAI が前出の綴りへ引きずられる(委任_01: 含む 24% vs 含まない 2%、att6除外)。**窓ASRの合格は当該clipの発音確認にならない**ため auto-accept 根拠にしない(委任_01 REJECTED を維持)。

## C. NG時Fallback(同じNG take群で比較。全表 `analysis_c_02.md`)
| 方式 | NG take 5本の救済(exact or 現行PASS) | 備考 |
|---|---|---|
| F1 同条件繰返し(OpenAI rep) | **0/5 take**(観測 0/9) | Azureは決定的(15/15一致)で繰返しても同じ |
| F2 前後音声追加再評価(OpenAI) | exact 率 att2 1/46, att4 5/46, att5 3/46, att6 17/45, b1b 0/23 | att6の17/45は文脈にMelos無しでも発生(真値未確定)。他takeは文脈にMelosを含む条件に偏る(プライミング) |
| F3 別engine再評価 | Azure exact 0/5 take(att1のみ exact だがProduction OK take)。whisper-small が `melo said` を返し Pattern A で受理 3/5 観測 | 第二engineの一致は『同音の別綴り』で割れる |
| F4 文脈付き音韻判定(Trial) | **音韻説明可(FUSION)**: OpenAI単独 3/9、Azure 8/10、whisper-small 5/5、whisper-medium 4/5。VOICING弱説明 OpenAI 4/9。説明不能(Mellis, mallow, 他)OpenAI 2/9 | 救済ではなくHR候補への分類。許容は独立証拠が必要 |
| F5 F4 + 音響独立証拠(Trial) | **単独gateとして不可**(AUC 0.74)。Melos 7 takeの測定: att1 195ms, att2 0, att3 120, att4 180(**人間HR承認済み**), att5 100, att6 145, b1b_att1 0(**人間HR承認済み**) | 人間承認済み2本が 180ms と 0ms に分かれ、正常音声が閾値を満たさない |
- **評価条件を変えるFallback(F4)は、同条件繰返し(F1)で救済できない不一致に対し、「別の質問(融合で説明できるか)」へ変えることで分類可能にする**が、自動許容にはできない(独立証拠が未校正)。数値: F1で救済できなかったNG take観測のうち、F4がHR候補にできたのは OpenAI 7/9(FUSION+VOICING)、Azure 8/10。
- 人間確認の実例: a2_att4 は OpenAI `Mellis`/Azure `mallow` で Trial音韻判定でも **説明不能(NG扱い)** だが、ユーザーHR試聴では**承認**された。Trialの音韻判定は「Mellis」型(unstressed vowelの母音差)を取りこぼす=偽陰性の実例(安全側だが、HR依存は残る)。

## D. 再発防止(Melos以外の一般例+反例。全表 `analysis_d_02.md`)
- **D-1 実データ base rate**: 英語2,030対(Production tts_generation_results)で、同一子音の重なり 1,841境界(境界付近に綴り差 8.9%上限)、歯擦音連続 476(7.4%)、歯擦音+口蓋歯擦音 509(4.3%)、同位置破裂音 877(2.7%)、yod 366(1.1%)、その他破裂音連続 3,343(1.6%)。融合しやすい境界でも**Productionの実運用ではほぼ綴り一致で通っている**。
- **D-2 実データ差分124 instance**(窓=差分語+前後1語): Trial音韻判定 FUSION 15 + VOICING 2、HOMOPHONE_ONLY 26(多くは既存のNORMALIZED_MATCH等で受理済み)、NO_PHONOLOGICAL_EVIDENCE 11、NOT_EXPLAINED 70(実際の別語化・数値・語脱落)。FUSION/VOICING 17件の内訳: **Productionが既に受理(Pattern A) 6件**、**現行未受理 11件(Melos関連7件、一般語4 instance=`the products stores stock->the products' store stock`[s+s]、`some Muse calls->some use calls`[m+m、2出所]、`pay showed coffee->pay show coffee`[d+k])**。**Melos以外の固有名詞の実データは0件**。
- **D-3 一般語2語窓の3分類**(正常音声 = 真値「正常な連結発音」): 融合型 n=288: 現行Production PASS 45% / Trial許容(綴り一致のみ) 41% / HR 2% / NG(説明不能) 57%。対照 n=48: 69% / 52% / 6% / 42%。**Trialは一般語の正常音声でほぼ新たな許容を生まない**(失敗の大半は連結発音で説明できないASRの別語化で、HRに載るのは6/288)。
- **D-4 反例(真値既知)**: 欠落語(synthetic_missing_word 0/26 許容)・誤名(synthetic_wrong_name `ruler` 0/15)・固有名詞誤読proxy(0/39)は、独立証拠最大でも許容0。**増分誤許容 19件(すべて `syn_B1_trunc*`)**: `said`語末を70〜220ms切詰めたMelos said音声で、`Melos`のs+s領域には欠陥がなくASR転写がintactと同一(`mello said`/`mellow said`)のため、証拠最大の仮定下では許容側に倒れる。これは「ASR文字列は語末切詰を検出しない」(委任_01)が、現行ではたまたま`Mello`綴りで止まっていた事象をTrial規則が通すことを意味する。→ Trial規則を導入する場合、**clip末尾の完全性の独立確認(末尾エネルギー/継続長等)を併用する必要がある**(残余リスク)。
- 真の誤発音・語尾欠落の「過去HRで人間がNGとした音声」: HR queue(75件)は人手verdictを保持しない(`final_status`のみ)ため、**NG判定の実音声は取り出せなかった**。代わりに真値既知の編集音声(委任_01 synthetic、本委任の編集音声)を使用。人間verdictの蓄積(HR承認/却下を `record_human_approval` 系に残す運用)がないと再発防止の実データ評価に限界がある。
- 一般化可能な方式: 「canonical語末音素 + 次語頭音素」の境界型(`boundary_type`)で融合変種を列挙し、ASR転写の音素列が変種と一致するかを見る(辞書語+OOVの`-s`派生)。残余リスク型: (R1) 融合と脱落のASR文字列上の不可分(音響証拠未校正)、(R2) OOV名のG2P欠如(stem+s派生は`melo`がCMU収録だったため成立。一般にはg2p_en等が必要)、(R3) unstressed母音差(`Mellis`型)の取りこぼし、(R4) clip末切詰の併発(D-4)、(R5) 一般語でも2語窓のASR別語化(連結発音以外の失敗)は説明不能のまま。

## 回帰test
`er065_short_clip_asr_context_trial_01_regression_test_01.py`: 19件 PASS(ASR呼出なし、既存転写入力、telemetry追記無効化)。構成: Production現行挙動の固定(Pattern A受理、同音別綴り=現行未受理[OPEN-327の記録]、反例の誤PASS 0、Eq Layer のOOV到達不能・corroboration必須)、Trial音韻判定(Melos said系・一般語の実データ、説明不能、OOV証拠なし)、3分類ポリシー(ASR推測のみでは許容にならない、反例は証拠最大でも許容にならない、VOICING/HOMOPHONEはHR止まり)。
実行: `.venv\Scripts\python.exe er065_short_clip_asr_context_trial_01_regression_test_01.py`

## 限界・注意(正直な記載)
- Trial音韻判定は CMU辞書+限定的OOV派生に依存し、`Mellis`型(unstressed母音差)・`mallow`(別語に一致)は取りこぼす。
- 音響測定は「4kHz以上の高域比>0.5、5msフレーム、境界±40msに重なる連続区間」の単純指標。有声Z+Sでは高域比が低く0msになりやすい(A群の10%以上が0ms)。forced alignment/Pronunciation Assessment等の別指標は未検証(新規依存/費用が必要)。
- 一般語2語窓は連続音声からの切出しで、TTS生成の2語clipとは境界の自然さが異なる(proxy)。切出し位置はlocal whisper small の word timestamp に依存。
- Melos以外の固有名詞(OOV)の実音声は存在せず、固有名詞一般化は合成評価のみ(`CS_AUDIT_01.md` §5-2)。
- 費用: OpenAI音声入力tokenの単価は`pricing_snapshot.json`に別掲が無く(委任_01から継続)、実費は過小評価の可能性。
- 並行実行中の他agent(③JA ASR / ⑤Coffee v5 / ⑥KP Idiom)の出力・stateには触れていない。共有telemetryの before/after 差は無し(`state_guard_02.json`)。

## 成果物
- `A_AUDIT_02.md`(A)、`analysis_b_02.md`(B)、`analysis_c_02.md`(C)、`analysis_d_02.md`(D)、`acoustic_stats_02b.json`、`melos_take_acoustic_02.json`、`a7_table_02.json`、`d_instances_02.json`、`d_base_rate_02.json`
- 生ASR結果 `results_01_*_02.jsonl`、費用 `cost_02.json`(`cost_01_*_02.jsonl`)、state不変 `state_guard_02.json`(`telemetry_guard_*_02.json`)
- コード: `er065_short_clip_asr_context_trial_01_p2_{phon,corpus,acoustic,acoustic_stats,make_config_b,make_general_cuts,melos_edit,a7_table,analyze_b,analyze_c,analyze_d}.py`、`er065_short_clip_asr_context_trial_01_regression_test_01.py`
