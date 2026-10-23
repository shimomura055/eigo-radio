# TRIAL_RESULT_01: ①固有名詞 Run Entity Table(RET) Trial 結果(Fable評価資料)

管理ID: ASR-QUALITY-2ITEMS-COMPREHENSIVE-01-PN 委任_02 / 2026-10-23 / Status: **TRIAL_DONE_PENDING_FABLE**(`VALIDATED`の自己宣言はしない。判定はFable)。Production/Prompt/flag/閾値/Ledger/golden変更0、`upsert`/`--apply`/HR Lock解除/run_sf_prod_01のstage実行・音声変更/TTS実行 0。
設計=`DESIGN_02.md`(Opus条件Aレビュー反映)、反復=`TRIAL_01/ITERATION_LOG_01.md`、実装=`er111_pn_entity_table_trial_01.py`/`er111_pn_trial_evaluate_01.py`(DEV/Trial専用・未配線・承認前・既定OFF相当)、test=`er111_pn_entity_table_trial_01_test_01.py`(40件PASS)。結果json/script=`TRIAL_01/`。
使用モデル: **gpt-6-luna**(reasoning low、Responses API strict JSON)。設計時のNER実測(ner_probe_01)と同一モデルを継続使用(比較条件の同一性を優先。モデル比較はOF-PN2-13の条件[SC-9達成]が条件付きのため未実施)。最新世代かどうかは既存Model Routing登録モデルの範囲で、最新でない場合の例外理由=該当せず(比較検証ではなく実装検証のため新モデル探索は対象外)。

## 0. 結論(先に)
- **Bertie型は検出・受理できる**: 『開いた窓』停止4clipのうち保存転写がある3行(120/121/118)は、現行`NO_PROPER_NOUN_EVIDENCE`→RETで`ENTITY_ONLY_ACCEPT`(アラーム付き受理)。残る1clip(b1b part1_c14)も、保存されたattempt 1・2のPrimary差分は`bertie→birdie`のみで、同条件なら受理される机上推定(§3)。**Bertie usable 5/5回構築**(反復3で自作仲裁規則の不具合を修正後)。
- **HR queue 88実イベント(Ledger全除外=初見語再現)**: アラーム付き受理 36→**56**(現行Ledger条件でも41→**56**)、証拠なし(B)9→**0**、Secondary span跨ぎ(C)16→**3**(残りは意図どおり不受理の`melos drank`×3)。**退行0**。一般語化ブロック(D)5→7は、span跨ぎで止まっていた行が正しく一般語ブロック(productive, muse→use)へ移った分。
- **受理境界は不変**: 類似度≥0.40・一般語ブロック・P-03・G3二重ASR・数値/否定/脱落・KP/JA除外・slotはer103原本の関数/定数をそのまま使用。表が空/無いとき判定はer103とバイト一致。表由来判定は「同一tokenをLedger登録した場合」より緩くならない(2,344ケース不一致0)。新規受理20イベントを全件adjudicate: **意味が変わる受理=0、一般語誤読の受理=0**。
- **未達・開示事項**: SC-9(安定性)は entry単位でtext別最小Jaccardの平均0.953(0.90未満4/27)、token単位平均0.984(同2/27)で、**個別text単位の0.90は未達**(揺れは表記粒度とVogueのカテゴリ揺れ。失敗方向は安全側、和集合の非固有名詞付与0)。費用は平均0.059〜0.067円/記事セットだが、最大0.168円(Z長編58 segment・2 call)が0.1円目標を超える。
- 採用区分: LLM NER(新しい証拠源・新規API call)とRET-3(G3の既存関数の直接変更に当たる)は**新仕様候補**。採用はユーザー判断(VALIDATED止まり)。RET-3は11-7限定例外の対象外の可能性が高い(DESIGN_02 §4)。

## 1. SC-1〜10 結果(基準/実測/判定)
判定欄は私の一次自己点検(**VALIDATED判定ではない**)。「条件付き」は基準文言の一部が未達または解釈を含むもの。

| SC | 基準(DESIGN_02 §3) | 実測(出典) | 一次判定 |
|---|---|---|---|
| SC-1 同値性 | 表なし/空/無関係表でer103とバイト一致、drift guard一致 | D1 88事象×(現行Ledger/Ledger全除外)×3表 = 528判定 不一致0、D2 保存EN 3,041pair(判定対象1,309)×3表 不一致0、drift guard一致、unit 40件PASS(`sc1_equivalence_01_result.json`) | PASS |
| SC-2 検出 | gold出現≥150、必要層recall≥0.90、カテゴリ別≥0.85、Bertie型n≥10で100% | gold出現 **266**(実本文156+合成110)。eligible gold 79中 usable **79(100%)**、表が必要な層(既存証拠が成立しない出現)**42/42**、カテゴリ別 person 36/36・organization 14/14・place 11/11・brand_product 16/16・work_title 1/1・other_named 1/1。Bertie型(CMU収録の人名、既存証拠が成立しない出現あり) **n=21で21/21**。検出(grade不問)95/97=残2は5語超の題名/スローガン(`The Crimson Petal and the White`/`Share the journey, not the noise`)を**意図的に除外**。実本文のrecall分母はLLM列挙+独立の大文字語点検(未列挙の大文字語は一般語/略語のみ)で、取りこぼしの実体は複数形`Typhoons`のみ(`sc2_sc3_detection_01_result.json`) | PASS(実本文の分母はSonnet一次) |
| SC-3 精度 | 非固有名詞率≤2%、偽候補の証拠化0、題名中の低頻度一般語の証拠化0 | D3(21本文)usable 40 entry中の非固有名詞 **0**、D4 usable全件がgold内、HR群30表の usable 68 entry(人手点検)に非固有名詞 **0**。**全segment全tokenの総当たり**で表が証拠を付けたtokenは全て実体内(D3/D4: 非gold付与0、HR群: 68 token全て実体内の語)。偽候補(inventing/canceling/fats/roasting/unwanted/farther/muddy/withdrawn、見出し語、Title Case一般語、`petal`/`crimson`/`pedal`)の証拠化 **0**。brand_productは別集計(D3 usable 12・D4 16、全て実在ブランド)(`sc2_sc3_detection_01_result.json`/`sc3_hr_token_precision_01_result.json`) | PASS(残存リスクR4参照) |
| SC-4 受理(初見語) | B類9中≥8(Bertie 3/3)、C類entity-only 13中≥12、Melos drank×3不受理維持、A類41維持、D/E維持、LOO≥90% | Ledger全除外: B類 **8/9**(Bertie 3/3、Kristie Tse 4/4、Stephen Reicher 1/1、残1=`Muse→use`は両ASRが一般語でP-03により**正しく不受理**)、C類entity-only **12/13**(L. Mimoun 9/10[残1は`productive`の一般語誤読で正しくD類ブロック]、Kristie Tse 1/1、Altuzarra Toteme 2/2)、`melos drank`×3 不受理維持、A類 **退行0**(現行Ledger条件41→56)。ユニーク(text,名前)単位 受理 31→39。LOO(25 Ledger entry): 依存受理5中 **5(100%)** を表で維持(`sc4_hr_replay_01_result.json`/`sc4b_followups_01_result.json`) | PASS |
| SC-5 実装同値 | 表由来判定=Ledger登録判定が100%一致 | 118 entry×10種ASR変種×2 Secondary条件=2,344ケース **不一致0・表が緩い側の差0**。※tautologyであることを明記(誤PASS不在の証明ではない) | PASS(実装同値のみ) |
| SC-5b 誤PASS adjudication | 新規受理全件を人手判定、意味変更0・一般語誤読受理0、負例受理0 | 新規受理20イベント(29 diff)全件を§4で判定: **意味が変わる受理0・一般語誤読の受理0**(最終目視=Fable)。合成負例(一般語/数値/否定/脱落、Primary=Secondary同一別語)の受理 **0**(`sc5_variants_01_result.json`) | PASS(最終はFable目視) |
| SC-6 フェイルセーフ | 全注入で例外0・表由来受理0・現行同一・operator reportに未構築明記 | 8注入(RuntimeError/TimeoutError/ValueError[不正JSON相当]/空応答/`entities=None`[refusal相当]/不正item/幻覚のみ/**実APIクライアントの超短timeout[0.001秒、費用0]**)で例外0・不一致0・表由来受理0。LLM失敗系はstatus=`LLM_UNAVAILABLE`でoperator reportに「実体表: 未構築または縮退」を出力(`sc6_failsafe_01_result.json`) | PASS |
| SC-7 費用・時間 | NER≤0.1円/記事セット、p95遅延 | 実測 **222 call・5.30円**(平均0.0239円/call、最大0.0857円)。記事セット(Std+Adv和集合の1表)あたり:平均 **0.059円**(監査ありの25群は平均0.067円)・call数平均1.33(call Bは独立裏付けが無いentryがあるときだけ)。**最大0.168円**(Z長編・2call)は0.1円目標超。構築時間 平均5.2秒/最大13.7秒、call遅延 p50 2.6秒/p95 5.1秒/max 23秒(TTS前に独立処理・TTSの分単位に隠れる)(`sc7_sc8_summary_01_result.json`、出典=`usage_log.jsonl`) | 条件付き(平均は達成、最大1群が超過) |
| SC-8 横断 | Z2作品+X≥6記事で構築・分布・weak/dropped | Z2作品(『走れメロス』『開いた窓』)+X記事19本の計21表+HR群30表で構築成功(status OK 21/21)。D3カテゴリ分布(usable/not_usable): organization 18/8・brand_product 12/3・place 4/23・person 5/0・other_named 1/6。place/orgの not_usable の大半は全tokenが一般語(Brazil/Japan/United States等=`R_GENERAL_WORD`維持、`blocked_general_person_place` 40件を記録)。dropped=長句1(`sc7_sc8_summary_01_result.json`) | PASS |
| SC-9 安定性 | Jaccard≥0.90、和集合の非固有名詞付与0 | 27 text×3回構築。entry単位: text別最小Jaccardの平均 **0.953**(0.90未満 **4/27**、最小0.5=`Meta’s Superintelligence Labs`⇔`Superintelligence Labs`の表記粒度)、token単位(証拠が付くtoken集合): 平均 **0.984**(0.90未満 **2/27**、最小0.80)。**3回の和集合でも非固有名詞への付与0**。Bertie再構築 5/5(`sc9_stability_01_result.json`/`bertie_stability_01_result.json`) | **条件付き**(平均は達成・個別text単位は未達。失敗方向=証拠が減るだけ[安全側]) |
| SC-10 継承/LR | 保存entry再判定の一致、LRで表が減らない | 受理92判定(現行Ledger/全除外)で、受理に使った実体entryのみから復元した表(LLM 0 call・表sha不一致78件含む)による再判定が**92/92一致**。Local Rewrite相当(4 segment書換え)で表entry 4→4(減らない)、Bertie行の判定不変、NER失敗でも既存entry維持(`sc10_rejudge_lr_01_result.json`) | PASS |

## 2. 改善前後(HR queue 88実イベント再評価、現行`evaluate_alarm_eligibility`=改善前 vs RET=改善後)
表は各イベントの記事のTTS canonical和集合(Std+Adv、`audit/tts_generation_results.json`)から構築(83行は実audit、5行のみHR行のcanonical和集合)。

| 原因クラス | Ledger全除外(初見語): 前 | 後 | 現行Ledger: 前 | 後 |
|---|---|---|---|---|
| A 受理(アラーム付き) | 36 | **56** | 41 | **56** |
| B 証拠なし(NO_PROPER_NOUN_EVIDENCE) | 9 | **0** | 3 | **0** |
| C Secondary span跨ぎ | 16 | **3**(`melos drank`×3=意図どおり) | 16 | **3** |
| C2 Secondary noise上限 | 1 | 1 | 1 | 1 |
| D 一般語化ブロック | 5 | 7(span跨ぎで止まっていた行が正しいブロックへ移動) | 6 | 7 |
| E 固有名詞以外が原因 | 21 | 21 | 21 | 21 |
| 固有名詞のみ候補の母集団 A..D | 67 | 67 | 67 | 67 |

アブレーション(`ablation_01_result.json`、Ledger全除外):原本 36 → RET-2(証拠源のみ) 44 → RET-2+RET-3 **56**(+8は表の証拠: Bertie3・Kristie Tse4・Reicher1、+12はSecondary span規則: L. Mimoun×9・Altuzarra Toteme×2・Kristie×1)。`general_in_phrase`(一般語tokenへの位置紐づけ付与)はV1=V2=56で差なし。
**「固有名詞が原因だが救済されなかった」割合(DESIGN_01の指標)**: 認識欠落(B+C)の 25/67=**37%**(初見) → **3/67=4.5%**(残りは意図どおり不受理の`melos drank`)。

## 3. 『開いた窓』停止4clipの机上再判定(状態変更なし、`openwindow_4clip_01_result.json`)
表=当該runのStd+Adv TTS canonical和集合(74 segment)から構築: Framton/Vera/**Bertie**=confirmed(Bertieは独立call Bが一致)、Indiaは全token一般語でweak。Z Seed `key_roles`の宣言(Framton・Vera)のみでは**Bertieは救えない**(宣言外)ことも確認(「宣言のみ」列)。

| clip | 保存HR行 | 現行 | RET(LLM表) | 宣言のみ |
|---|---|---|---|---|
| a2 full_story_part1_c14 | 行120(Primary/Secondary保存あり) | NO_PROPER_NOUN_EVIDENCE | **ENTITY_ONLY_ACCEPT** | NO_PROPER_NOUN_EVIDENCE |
| a2 full_story_part3_c2 | 行121 | NO_PROPER_NOUN_EVIDENCE | **ENTITY_ONLY_ACCEPT** | NO_PROPER_NOUN_EVIDENCE |
| b1b full_story_part3_c2 | 行118 | NO_PROPER_NOUN_EVIDENCE | **ENTITY_ONLY_ACCEPT** | NO_PROPER_NOUN_EVIDENCE |
| b1b full_story_part1_c14 | 行117(attempt 3: Primaryに`sang→sing`の非固有名詞差が混入=TRUE_CONTENT_MISMATCH) | PRIMARY_NOT_ENTITY_ONLY(対象外) | 同左(対象外) | 同左 |

b1b part1_c14は保存HR行(最終attempt)が固有名詞以外の差を含むためPNAP対象外だが、`tts_generation_results.json`のattempt 1・2のPrimary差分は`bertie→birdie`のみ(ASR_VALIDATION_UNCERTAIN)で、**机上推定(Secondary=Primary mock、onoff_differentialと同じ前提)ではRETで受理**。attempt 1・2のSecondary転写は保存されていないため推定である点を明記する。他3clipの全attemptでも、Primary差分が`bertie→birdie`のみのattemptはすべて受理推定。**採用後の再開は、Primary差分が固有名詞のみになるattemptで受理される見込み**(再生成が必要な場合の費用は設計時見積約2〜5円)。

## 4. 新規受理(RETで初めて受理となった全件)の adjudication(OF-PN2-07、一次=Sonnet・最終目視=Fable)
Ledger全除外で現行→不受理、RET→受理の **20イベント(29 diff)**。分類は (a)名前の聞き違い/表記ゆれ(意味不変) (b)実誤読型(PrimaryとSecondaryが同じ別語=Stage 2の「複数ASRが揃って別語」)でアラーム付き受理=承認済み方針の範囲 (c)意味が変わる受理 (d)一般語誤読の受理。**(c)=0・(d)=0**。ラベル(OF-PN2-08)は試聴優先度用。

| HR行 | canonical(対象語) | Primary ASR | Secondary ASR | カテゴリ/経路 | ラベル | 一次分類(Sonnet) | 根拠 |
|---|---|---|---|---|---|---|---|
| 7 | mimoun | mamone | (Secondaryはcanonical一致) | person / RET-3+表 | mid | 名前の聞き違い/表記ゆれ(意味不変) | 固有名詞のみの差。ASR語は一般語でない(P-03通過)。数値/否定/脱落なし。 |
| 8 | mimoun | mimmen | (Secondaryはcanonical一致) | person / RET-3+表 | mid | 名前の聞き違い/表記ゆれ(意味不変) | 固有名詞のみの差。ASR語は一般語でない(P-03通過)。数値/否定/脱落なし。 |
| 8 | gruen | groen | grune | person / RET-3+表 | high | 名前の聞き違い/表記ゆれ(意味不変) | 固有名詞のみの差。ASR語は一般語でない(P-03通過)。数値/否定/脱落なし。 |
| 9 | mimoun | memon | (Secondaryはcanonical一致) | person / RET-3+表 | high | 名前の聞き違い/表記ゆれ(意味不変) | 固有名詞のみの差。ASR語は一般語でない(P-03通過)。数値/否定/脱落なし。 |
| 9 | gruen | grun | groon | person / RET-3+表 | high | 名前の聞き違い/表記ゆれ(意味不変) | 固有名詞のみの差。ASR語は一般語でない(P-03通過)。数値/否定/脱落なし。 |
| 12 | mimoun | mamon | (Secondaryはcanonical一致) | person / RET-3+表 | high | 名前の聞き違い/表記ゆれ(意味不変) | 固有名詞のみの差。ASR語は一般語でない(P-03通過)。数値/否定/脱落なし。 |
| 12 | gruen | gruhn | grown | person / RET-3+表 | high | 名前の聞き違い/表記ゆれ(意味不変) | 固有名詞のみの差。ASR語は一般語でない(P-03通過)。数値/否定/脱落なし。 |
| 13 | mimoun | memoun | (Secondaryはcanonical一致) | person / RET-3+表 | high | 名前の聞き違い/表記ゆれ(意味不変) | 固有名詞のみの差。ASR語は一般語でない(P-03通過)。数値/否定/脱落なし。 |
| 16 | mimoun | mimon | (Secondaryはcanonical一致) | person / RET-3+表 | high | 名前の聞き違い/表記ゆれ(意味不変) | 固有名詞のみの差。ASR語は一般語でない(P-03通過)。数値/否定/脱落なし。 |
| 16 | gruen | groen | grune | person / RET-3+表 | high | 名前の聞き違い/表記ゆれ(意味不変) | 固有名詞のみの差。ASR語は一般語でない(P-03通過)。数値/否定/脱落なし。 |
| 17 | mimoun | mamoun | (Secondaryはcanonical一致) | person / RET-3+表 | high | 名前の聞き違い/表記ゆれ(意味不変) | 固有名詞のみの差。ASR語は一般語でない(P-03通過)。数値/否定/脱落なし。 |
| 17 | gruen | groen | grune | person / RET-3+表 | high | 名前の聞き違い/表記ゆれ(意味不変) | 固有名詞のみの差。ASR語は一般語でない(P-03通過)。数値/否定/脱落なし。 |
| 18 | mimoun | miman | (Secondaryはcanonical一致) | person / RET-3+表 | high | 名前の聞き違い/表記ゆれ(意味不変) | 固有名詞のみの差。ASR語は一般語でない(P-03通過)。数値/否定/脱落なし。 |
| 18 | gruen | groon | grun | person / RET-3+表 | mid | 名前の聞き違い/表記ゆれ(意味不変) | 固有名詞のみの差。ASR語は一般語でない(P-03通過)。数値/否定/脱落なし。 |
| 20 | mimoun | mimuun | (Secondaryはcanonical一致) | person / RET-3+表 | high | 名前の聞き違い/表記ゆれ(意味不変) | 固有名詞のみの差。ASR語は一般語でない(P-03通過)。数値/否定/脱落なし。 |
| 20 | gruen | groon | grune | person / RET-3+表 | mid | 名前の聞き違い/表記ゆれ(意味不変) | 固有名詞のみの差。ASR語は一般語でない(P-03通過)。数値/否定/脱落なし。 |
| 21 | kristie tse | christy c | christy c | person / 表(RET-2) | low, P=S同一別語 | 実誤読型(両ASR一致)→アラーム付き受理・承認方針内 | 固有名詞のみの差。ASR語は一般語でない(P-03通過)。数値/否定/脱落なし。 類似度が下限0.40に近い=試聴優先度:高。 |
| 22 | kristie tse | christy tay | christy tay | person / 表(RET-2) | mid, P=S同一別語 | 実誤読型(両ASR一致)→アラーム付き受理・承認方針内 | 固有名詞のみの差。ASR語は一般語でない(P-03通過)。数値/否定/脱落なし。 |
| 23 | kristie tse | christy c | christy c | person / 表(RET-2) | low, P=S同一別語 | 実誤読型(両ASR一致)→アラーム付き受理・承認方針内 | 固有名詞のみの差。ASR語は一般語でない(P-03通過)。数値/否定/脱落なし。 類似度が下限0.40に近い=試聴優先度:高。 |
| 24 | kristie tse | christy sea | christy c | person / 表(RET-2) | mid | 名前の聞き違い/表記ゆれ(意味不変) | 固有名詞のみの差。ASR語は一般語でない(P-03通過)。数値/否定/脱落なし。 |
| 25 | kristie | christie | (Secondaryはcanonical一致) | person / RET-3+表 | high, zipf境界付近 | 名前の聞き違い/表記ゆれ(意味不変) | 固有名詞のみの差。ASR語は一般語でない(P-03通過)。数値/否定/脱落なし。 |
| 26 | stephen reicher | steven reichert | steven reichert | person / 表(RET-2) | high, P=S同一別語 | 実誤読型(両ASR一致)→アラーム付き受理・承認方針内 | 固有名詞のみの差。ASR語は一般語でない(P-03通過)。数値/否定/脱落なし。 |
| 37 | toteme | totem | (Secondaryはcanonical一致) | brand_product / RET-3+表 | high | 名前の聞き違い/表記ゆれ(意味不変) | 固有名詞のみの差。ASR語は一般語でない(P-03通過)。数値/否定/脱落なし。 |
| 37 | kallmeyer | kalmeyer | (Secondaryはcanonical一致) | brand_product / RET-3+表 | high | 名前の聞き違い/表記ゆれ(意味不変) | 固有名詞のみの差。ASR語は一般語でない(P-03通過)。数値/否定/脱落なし。 |
| 44 | toteme | totem | (Secondaryはcanonical一致) | brand_product / RET-3+表 | high | 名前の聞き違い/表記ゆれ(意味不変) | 固有名詞のみの差。ASR語は一般語でない(P-03通過)。数値/否定/脱落なし。 |
| 44 | kallmeyer | kaal eeram | kalmire | brand_product / RET-3+表 | mid | 名前の聞き違い/表記ゆれ(意味不変) | 固有名詞のみの差。ASR語は一般語でない(P-03通過)。数値/否定/脱落なし。 |
| 118 | bertie | birdie | birdie | person / 表(RET-2) | mid, P=S同一別語 | 実誤読型(両ASR一致)→アラーム付き受理・承認方針内 | 固有名詞のみの差。ASR語は一般語でない(P-03通過)。数値/否定/脱落なし。 |
| 120 | bertie | birdie | (Secondaryはcanonical一致) | person / 表(RET-2) | mid | 名前の聞き違い/表記ゆれ(意味不変) | 固有名詞のみの差。ASR語は一般語でない(P-03通過)。数値/否定/脱落なし。 |
| 121 | bertie | birdie | birdie | person / 表(RET-2) | mid, P=S同一別語 | 実誤読型(両ASR一致)→アラーム付き受理・承認方針内 | 固有名詞のみの差。ASR語は一般語でない(P-03通過)。数値/否定/脱落なし。 |

要約: 実誤読型(b) は 6事象(Kristie Tse×3[行21/22/23]・Stephen Reicher[行26]・Bertie×2[行118/121])。類似度帯 low(0.40〜0.50) は行21/23(`kristie tse→christy c`)で試聴優先度が最も高い。zipf境界付近の語を含むのは行25(`christie`)のみ。Stage 2で実誤読と確認済みの語(Khaite→kate、Muse→use、Meink→mc等)は**一般語化ブロックのまま不受理**(D類)で、本案で受理に変わっていない。

## 5. 承認済み方針との整合(OF-PN2-12)
新規受理の多くは「実際にTTSが誤読している(両ASRが別語を転写)固有名詞」である。これは**2026-10-22承認済みの方針(固有名詞の発音不一致だけが原因のNG/HRは、アラーム記録のみで受理し制作を止めない)の範囲内**。Stage 2 REJECTED(取得/推定発音とASR転写の音素照合で発音の**正否を判定**して通す方式)とは別物で、本案は発音の正否を判定せず、「その語が固有名詞である」という**証拠を本文側から供給する**だけ。受理条件(類似度・一般語ブロック・P-03・G3・数値/否定/脱落)は不変。実誤読はoperator reportのアラームとして記録され、供給(Khaite型のB階層人承認)は変わらない。

## 6. 残存リスク(誤PASS・見逃し)
| ID | リスク | 評価・緩和 |
|---|---|---|
| R1 | zipf境界(3.5〜4.0)依存: 一般語判定(CMU∧zipf≥4.0)の境界付近の語(`barn` 3.99、`translate` 3.93等)の eligible/一般語がwordfreqのversionに依存 | wordfreq 3.1.1を記録。アラームラベル`asr_zipf_near_general_boundary`で試聴優先度化(新規受理29 diff中1件)。境界は動かさない |
| R2 | 実誤読のアラーム付き受理(§5)。ASR語が非一般語で類似度≥0.40なら、実際の誤読でも受理される(承認済み方針の範囲) | operator reportで記録・ラベル付き。Ledger登録済みの語と同一境界(SC-5) |
| R3 | pron_differs相当: Birdie⇔Bertie のように綴りが違うだけで実音が近いのか違うのかを判定しない | 判定しない設計(音素距離は分離不能と実測済み、DESIGN_01 §4)。ラベルのみ |
| R4 | 通常語を含む名前の通常語token: `Pier`(Terminal C Pier Expansion)・`Translate`(Google Translate)・`Labs`・`Barn`・`Pixel`・`Pentagon`・`Muse`・`Maxi`・`Gemini` は eligible(非一般語zipf<4)。HR群で証拠が付いた68 tokenのうち約9(約13%) | **実体出現範囲に全出現が含まれる場合のみ**(位置紐づけ)で、実体外の同形語には付与されない(unit test)。その名前内の誤読はアラーム付き受理。OF-PN2-04は work_title/other_named のみ制限するので、person/place/org/brandの低頻度一般語は対象。必要なら将来、名前内の通常語tokenを弾くカテゴリ別規則を検討(Fable判断) |
| R5 | LLM依存: 安定性(SC-9個別text単位未達)・分類揺れ(Vogue→work_title)・列挙漏れ | 失敗方向=証拠が減る(HRのまま)で安全側。call Bで独立裏付け。和集合でも非固有名詞付与0。多数決は費用3倍で保留 |
| R6 | 偽陰性: 一般語と同形の名前(Iran/Mark/Will/Rose/Japan/France)は全token一般語なので救済されない(Iran/Mark型ブロック維持=設計どおり)。小文字始まりブランド(iPhone/eBay)・複数形(Typhoons)・5語超の題名は対象外 | 受け入れ。HRのまま |
| R7 | RET-3の「語を含まない句読点の連結許容」は私の解釈(Opus原文は「区切り語なし隣接複数実体」) | Fable確認事項。`Celine, Altuzarra, Toteme`の2事象のみに作用 |
| R8 | 実本文のrecall分母は『LLM列挙+Sonnetの独立点検』。合成D4は構成上確定 | Fableが§4・`d3_gold_01.json`を目視 |
| R9 | 表入力が部分: HR群のうち5行はaudit不在で当該HR行のcanonicalのみから構築(文脈が小さい) | 結論に影響する行はなし(Bertie含む83行は実audit) |
| R10 | RET-3は既存G3の直接変更に当たる(複製で隔離したのみ)。Production配線はユーザー採用判断+VALIDATED後 | DESIGN_02 §4 |
| R11 | 最大費用0.168円/記事セット(長編2call)が0.1円目標超 | 平均0.059〜0.067円。長編でcall Bを省く/Seed宣言を優先する等で圧縮可能(未実施) |
| R12 | Perplexity 401(Ledger事後登録が機能しない環境不全)はRETでは解消しない(RETはLedgerに依存しないがA/B階層の発音供給は別問題) | OPEN-473で別追跡 |

## 7. Family X/Z への適用範囲
- **共通部品**: 表の構築・判定wrapperは入力が`Seg(text, role)`列なので、Z(`er063_family_z_audio_01.run_tts_stage`が`article_text`を受ける位置)とX(`@pnap_hooks.family_scope`)の双方から同じ関数で呼べる(配線は未承認のため今回は配線しない)。
- **Z**: Seed `key_roles` の名前を宣言として使えるが、**Bertieのような宣言外の固有名詞はLLM NERでしか拾えない**(実証済み)。
- **X**: 英語の宣言済み実体表が存在しない(Research Ledgerは日本語fact/subject)ためLLM NER+決定論のみ。X記事19本で構築成功。
- Family A/B/C: PNAPのrun scope(X/Z)外のため無影響。Trialは`er111_pn_*`のみで正式経路に未参照(AST test)。
- ②UKUS: 別モジュール(`er111_ukus_*`)で非干渉。表は読取のみ共有の想定。

## 8. 費用・時間・単価
- API: 222 call・5.30円(上限30円、gpt-6-luna、単価の出典=`er006_model_routing_pricing_coverage_test_01.py:50-52`[入力0.10/出力0.50 USD per 1M token]×160円/USD、`usage_log.jsonl`)。
- 1記事セットあたり 平均0.059円・最大0.168円。70円/記事セットに対し 0.1%未満(平均)。TTS前の独立処理で、構築時間は平均5.2秒/最大13.7秒。

## 9. 撤去・残置・隔離の確認
- 撤去0・縮小0。`er103`(P-02/`proper_noun_evidence`/`R_GENERAL_WORD`/G3)・`er006_secondary_asr_01`・`er019`・`val`・runner は**無変更**(`git diff --stat`に含まれない)。
- 残存Grep: `er111_pn_`を参照する正式module=0(`IsolationTest.test_no_production_module_imports_trial`)。11-7 flag(`*_ENABLED =`)の新設=0、`os.environ`参照=0、`upsert`=0。
- drift guard: 複製元5関数のsha256固定(`test_drift_guard`)。

## 10. 判定整合・次の一手
- VALIDATED基準に対する私の一次自己点検: SC-1・2・3・4・5・5b・6・8・10 PASS、SC-7・SC-9 は条件付き(§1)。**判定はFable**。
- 次の一手の候補(改善見込みの自己評価): (a)SC-9を詰める=「det裏付けのあるentryはA/Bの和集合」(費用+0.05円、見込み中) (b)長編のcall B省略/宣言優先で最大費用を0.1円内へ(見込み中〜高) (c)RET-3のカンマ連結解釈の確認(Fable、即) (d)R4のカテゴリ別規則(person/brand名の通常語token)は採用前に再検討(見込み低〜中)。
