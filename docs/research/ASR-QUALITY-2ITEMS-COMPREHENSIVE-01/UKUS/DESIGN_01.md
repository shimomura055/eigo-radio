# ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 ②英米綴り DESIGN_01
(UKUS 委任_01 / 2026-10-23 / 設計のみ。Production・Prompt・flag・閾値・脚本の変更 0。Trial実装はOpusレビュー後の次委任。API 0円)
前提: ROOT_CAUSE_01.md。承認済み仕様の根拠: er109 v1 は Family X/Z限定でPRODUCTION_WIRED(OPEN-459)、A/B/C凍結(PM_GOVERNANCE 27-3)。

## 1. 目標(原文§4② の翻訳)
正当な英米綴り差(-ise/-ize、-our/-or、-re/-er、-ll-/-l-、-ogue/-og、-ence/-ense、ae/oe、speciality/specialty、aluminium/aluminum、jewellery/jewelry、programme/program、grey/gray、learnt/learned 等、規則対も不規則対も)を、Primary/Secondary双方で同値扱いし、NG・不要retry・LR・HR Lock・脚本変更を起こさない。一方、意味/発音の異なる語(advice/advise、ensure/insure、complement/compliment、principal/principle、stationary/stationery、dependant/dependent の用法差、tire/tyre の語義差 等)を新規にPASSさせない。

## 2. 選択肢の比較(構造の選択理由)
| 案 | 概要 | 評価 |
|---|---|---|
| **A(推奨)** 新層「UKUS」: 英米対応辞書で語unitのkeyをUS正規形へ写像してからer109の既存整列・判定へ渡す(er109の位置・hookをそのまま使う)。辞書外は**制限規則(ise/ize・yse/yze・our/or)**を警告付きで許容 | API 0円。Primary(er006)/Secondary/KP3V(er104)/judge最終gate(er078)/Store guardが**既存のer109 hookを通るため追加配線なし**。「既存全層が不合格のときだけ」評価する既存順序(P1)に乗るため、現在PASSの行は変化しない(PASS→NG 0)。他の差があれば従来どおりNG。 | 推奨 |
| B `BR_AM_SPELLING_PAIRS`(val)を拡張 | 13ペア表に語を足す/辞書化 | **共有Validator(A/B/C含む)の直接編集=A/B/C挙動変化・既存辞書の直接編集で11-7限定例外の対象外・凍結違反**。却下 |
| C er109の音素層を緩和 | 音素距離しきい値で同値化 | `speciality/specialty` 距離0.30、`jewellery`はCMU未登録で判定不能。しきい値を緩めると `ensure/insure` 型の別語まで通る。OPEN-459の厳格化方針と逆行。却下 |
| D 3rd ASR(Whisper)を本文segmentにも導入 | 票を増やす | 3エンジンとも米綴り傾向で救済されない見込み+全segmentにWhisper費用。却下 |
| E ASRにcanonicalをprompt/phrase-listで与える | 綴りを誘導 | **検証の独立性を壊す**(期待文に引かれて実際の誤読を見逃す)。ASRは「何と聞こえたか」の独立計測であるべき。却下 |
| F Writer promptで米綴り固定 | 生成側で統一 | Prompt/承認済み仕様の変更(要ユーザー承認)。Zは原作の英綴りを保つ(原作忠実度)方針と衝突。X/Zで英国記事・引用にUK綴りが入る事実は変わらない。却下 |
| G **TTS直前に脚本を米綴りへ統一する前処理** | canonicalを変換 | **本文変更にあたる**。脚本=ユーザー向けページ表示と一致している必要がある。ページを米綴りにすればZ原作の綴りを変えることになり、ページを英綴りのままTTS入力だけ米綴りにすれば、ページと音声入力が食い違って `audio_text_deviation` が通常運用で恒常化する。ユーザー指示「脚本変更を起こさない」に反する。却下 |
| H LRの手前で綴り差を検出して書換を中止 | 下流の安全網 | 3回NG+10分cooldown(約10.6分、不要費用約1.1円)を消せず、HR Lock経路も残る。Aの**補助**(多層防御)としてのみ有効。Aが働けば不要 |

構造の結論: 「発音が同じ表記差」(er109 v1)とは別の、**「同一語の地域綴り」カテゴリ**を辞書(+制限規則)で明示する層を、er109の**同じ入口**に追加する。音素層(v1)は一切緩めない。

## 3. 推奨案Aの仕組み
### 3-1 辞書(オフライン同梱・API 0円)
- 主辞書: **VarCon 2020.12.07**(Kevin Atkinson、SCOWL Copyright=複製・改変・再配布可の寛容許諾、著作権表示を保持。846KB、調査用に取得済み=`work/varcon_2020.12.07.txt`)。A(米)推奨と非A(B/Z/C/D・変異)の対を抽出。用法付き(`| <N>`/`| <V>`/`:1`)は **AMB(語義/用法依存)**として別扱い。
- 補助辞書: **breame 0.1.2**(Apache-2.0、LICENSE表記を同梱=`work/breame_0.1.2_spelling_constants.py`)。VarConに無い対(例: 一部の-ae-/-oe-)を補う。VarConはbreameの95.1%(1,645/1,730)を含み、breame単独は `speciality`・`jewellery`・`practise`・`programme`・`licence` を欠く(確認済み)ため**単独採用は不可**。
- Tier分け(質の管理):
  - **Tier-1**: VarCon SCOWL level ≤ 70(UK形6,750語/6,756対。一般語・辞書語)かつ固有名詞(大文字始まり)でない対。junk候補(`saki/sake`、`arse/ass`、`nite/night`、綴り編集距離>2または短語の約145対)は**初回に全件人手レビュー**して denylist 化(レビューは次委任のTrial準備に含む)。
  - **Tier-2**: level 71〜99(約8,700語)+breame追加分。**採用はPASS_WITH_WARNING**(監査・件数監視用。音声の聴感に影響しない綴り差のため事後試聴は不要。警告の扱いはOpus論点)。
  - **AMB(用法依存、`license/licence`、`practise/practice`、`program/programme`、`tire/tyre`、`curb/kerb`、`check/cheque`、`draft/draught`、`dependant/dependent` 等、約290対)**: **canonical=UK形→ASR=US形の一方向のみ**同値(ASRは米綴りへ寄る傾向がある)。canonical=US形でASRがUK形(逆方向)は同値にしない。
- 辞書外の**制限規則(Tier-2扱い)**: `-isation/-ise(d/s/ing)/-iser`→`-ization/-ize…`、`-yse…`→`-yze…`、`-our(s/ed/ing/ful/ite)`→`-or…` のみ。条件: 語幹≥4字、変換後がwordfreq(zipf≥1.5)に実在。`-ity→-ty`・`-tre→-ter`・`ae/oe→e`・`-ement`等は**採用しない**(`reality→realty`、`shoe→she`、`poet→pet`、`parity→party` 等の誤同値を測定で確認)。測定=`work/ukus_rules_probe_01.py/.json`: 全規則だと60,000語中202件の衝突、制限規則では6件のみで全て同一語の変異(`surprise/surprize`等)=意味差0。
  - 規則はVarCon対の約54%(8,682/16,085)をカバー=**システマティックなクラス(ise/ize・yse/yze・our/or)は規則で再現、不規則クラスは辞書必須**。規則は辞書の再現率補完であり、全規則の汎用化は却下。

### 3-2 適用ルール(安全条件)
1. **語unit・1:1位置対応のみ**(difflibの'replace'で同数・位置対応する語どうし)。語の欠落・付加・語数が違うspanは対象外(従来どおり非同値=OPEN-459のfail-closed原則を維持)。
2. 数・記号・略語・頭字語のunit、および固有名詞(`entity_tokens`=`val.capitalized_flags/loanword_flags`)は**対象外**(`Grey/Gray`人名、`Centre`地名、`Labour/Labor`政党等は①(固有名詞)側のPNAP・再設計に委ねる)。
3. 活用・複数・所有格(`neighbour's`、`colour-blind`のハイフン連結)は語幹ごとに辞書引き。辞書にある対のみ(VarConは活用形も収録)。
4. **他に実差があれば従来どおりNG**(key正規化はUKUS差だけを消すため、同一文中の別の誤読は検出される)。
5. 音素近接の補助検査(tripwire): CMUに両側が登録され、かつ音素正規化距離が0.5超の対は**要レビュー対としてTier-1から外す**(例: `coe/ce`、`crea/cera`、`analyses/analyzes`は辞書誤りの疑い)。ただしCMU両側登録は対の2%(354/16,862)のみで、`speciality/specialty`=0.30は通す。**音素を同値判定には使わない**(本件の根本)。誤辞書検出の補助のみ。
6. 方向性: 通常対は双方向。AMB対は上記一方向。
7. 判定ラベル: er109の既存ラベル `ORTHOGRAPHIC_EQUIVALENT_MATCH` を再利用し、auditに `rules += "ukus_spelling_variant"`、`ukus_pairs=[(c,a,tier,source)]` を記録(新ラベルは作らない。最終ANDゲート `APPROVED_EQUIVALENCE_BASES` へも入れない=OPEN-459のP-06と同じ)。

### 3-3 適用点(Primary/Secondary/KP/judge すべて同一)
er109 `_units()`(`er109_asr_orthographic_equivalence_01.py:401`)が返す語unitの `key` と `prons` を、canonical側(1回目の呼出)とASR側(2回目)でUKUS層がpost-processする(side判定は呼出順)。`evaluate`(:709)の整列(difflib)以降は無変更。呼出元は既存のまま:
- Primary: `er006_secondary_asr_01.py:1130-1141`(既存全層不合格後)。Secondary: 同 :1205付近(M1後)。KP: `er104_kp_three_asr_vote_01.py:255`。judge: `er078_asr_unified_judge_01.py:360-420`(span解除・記録)。Store guard。すべて `er109_xz_scope_01.is_active_for_run()`(flag∧X/Z scope)内。
- よって**A/B/C・scope外は完全に従来動作**(凍結維持)。X/Zだけで効く。

### 3-4 Trial隔離(承認前はProductionに置かない)
- Trial実装は新module `er110_ukus_spelling_01.py`(純関数)と、Trial専用の評価wrapper(er109 `evaluate` の `_units` に差し込む。**er109本体・val・er006は編集しない**)に限る。Trial wrapperを呼んだ場合のみ有効(Production経路から暗黙参照しない)。
- Production採用はユーザー判断(VALIDATED止まり)。採用時の配線案: er109に `unit_postprocess` 引数(既定None=完全に従来)を追加+X/Z scope内の単一flag読取関数(既定OFF)。これは別委任(11-7限定例外の5条件を満たす形)。

## 4. 撤去・縮小すべき旧規則
- **撤去は提案しない(凍結のため)**: `BR_AM_SPELLING_PAIRS`(val:56-62)は共有Validatorで、A/B/Cへ影響するため触らない。新層はその前段(`NORMALIZED_MATCH`で通る語)には作用しないため衝突しない。
- 旧er003簡易検証の接尾辞規則(`er003_audio_tts_asr_safety.py:253-258`)は旧世代で、現行Productionの判定連鎖に入っていない(Trial時にGrepで参照を再確認)。
- 採用後、X/Z側で「問題になったら個別ペア追加」型の運用(同ファイルの注記)は不要になる旨を運用文書に反映。

## 5. 検証計画(Trial=次委任、API 0円。保存データとローカル計算)
正常系・異常系・境界・一般化・既存回帰・c12再現を**1回のTrialで広く**確認する。
| ID | 内容 | 件数 | 成功基準 |
|---|---|---|---|
| V1 正常系 | 代表英米対(-ise/-ize、-our/-or、-re/-er、-ll-/-l-、-ogue/-og、-ence/-ense、ae/oe、-ity系、不規則[speciality, jewellery, aluminium, grey, programme, licence, practise, mould, plough, pyjamas, sceptic, tyre, kerb, cheque, learnt/dreamt/spelt]、活用・所有・ハイフン複合)をcarrier文で**両方向** | ≥50対(≥100方向、Tier-1/2/AMB含む) | AMB逆方向の意図的非同値を除き**100%同値**。c12を含む |
| V2 異常系 | 意味/語義/発音が異なる対・近似綴りの別語(advice/advise, ensure/insure, complement/compliment, principal/principle, stationary/stationery, affect/effect, dependent/dependant逆方向, tire/tyre逆方向, story/storey, hour/our, four/for, flour/floor, jewellery/jewel, centre/central, practise/practical, specialty/special, colour/collar 等) | ≥30対(両方向) | **新規PASS 0**(ベースライン=現行er109が非同値の対が、新層で同値にならない)。既にer109の音素層で通る同音語(principal/principle, four/for 等)は**本層の責任外**として別表記録 |
| V3 境界 | 固有名詞同形(Grey/Gray、Centre/Center、Labour/Labor、Earl Grey、Rockefeller Center)、文頭大文字、数/記号span、1文中に綴り差+実誤読が同居、語欠落・付加、同音語置換 | ≥25 | 固有名詞は本層で同値にならない/綴り差+実誤読は**NG維持**/欠落・付加NG |
| V4 保存データ再判定 | 保存転写(primary 2,470・azure 172・pairs_02 3,039・HR queue・LR 30件、および`er109_b_fix_before_after_01.py`方式の全保存署名)を新層ON/OFFで比較 | 全件 | **PASS→NG 0**。NG→PASSは**全件目視分類**し、UKUS差のみが原因であることを確認(それ以外の理由でPASSになった件=0) |
| V5 一般化 | VarCon対の20%を辞書から隠し(seed固定)、規則+残り辞書で再現。システマティッククラスは再現、意味差の誤同値0。不規則クラスは辞書外=非同値(fail-closed)を記録。独立辞書(breame 1,730対のうちVarCon未収録85対)を別源の検証に使う | 3,217対 | 規則適用分の**意味差誤同値0**、システマティッククラス再現≥99% |
| V6 c12再現 | 保存転写(Primary/Azure)に対し、判定連鎖(`classify_asr_match`→er109→judge最終ゲート)をOFF/ON | 1(+carrier) | OFF=NG、ON=PASS(rules=`ukus_spelling_variant`)、retry 0・LR 0・HR 0 |
| V7 性能 | 辞書ロード(1回/process)と`evaluate`のp95 | — | ロード≤0.5秒(測定0.24秒)、1判定の追加≤1ms、API 0 |
| V8 既存回帰 | er109の既存test、StaticChecks(AST test)、全回帰(`REGRESSION_BASELINE_01.md`基準: failed 0/errors 0) | 全件 | 新規失敗 0。X/Zのscope外でUKUS層が呼ばれない(DefaultOff/Isolation型test) |

### 5-1 事前確認(本委任で実施済み、API 0・机上シミュレーション)
`work/ukus_sim_01.py`(er109の`_units`にkey正規化をmonkeypatchする研究用スクリプト、Production無変更、結果=`work/ukus_sim_01.json`):
- **c12**: `er109.evaluate(speciality文, specialty文)` 現行=`NOT_EQUIVALENT: phoneme_differs`、UKUS ON=`PASS: surface_equal_after_normalization`。US正規化後の `classify_asr_match`=EXACT_MATCH(census)。
- 正常系 55対×2方向=**110/110同値**(うち55方向は現行er109の音素層が既に通す同音対、**55方向が新規救済**: speciality, jewellery, aluminium, grey…を含む)。
- 異常系 34対×2方向=68方向で、現行非同値から**新規にPASSしたのは3方向**: `surprise/surprize`の2方向(同一語の変異綴り=意味差なし)と `tyre→tire`(AMB一方向、設計どおり)。**意味差のある誤PASSは0**。(`principal/principle`・`four/for`・`storey/story`等12方向は現行er109の音素層が既に同値と判定する既存挙動で、本層の責任外。)
- 暫定の机上値。Trial(V1〜V8)で正式に取り直す。

## 6. 費用・時間
- API費用 0円(辞書・規則・ローカル判定のみ)。量産単価70円への影響: 追加費用0、効果はマイナス要因の除去(c12型の事象1件あたり不要費用≒1.1円+待機約10.6分+脚本改変)。
- 開発: Trial実装(新module約200〜300行+test+評価script)+Opusレビュー反映+V1〜V8実行で半日〜1日。API 0円。並列化: 辞書denylistレビュー、test fixture作成(V1〜V3)、保存データ再判定(V4)、一般化評価(V5)は独立のため並列。
- 実行時: process起動時に辞書を1回ロード(約0.24秒)、以後メモ化。

## 7. 残存リスク
- **辞書の質**(denylistレビューで管理)。VarCon level≥71と規則は警告付き。
- **発音が違う綴り対**(speciality等)は綴りだけで同値にするため、TTSが実際に発音を誤っていても綴り差のみでは検出できない。ただしASRが `specialty` と書いた時点でその語として認識しており、別語の誤読(`specially`等)は従来どおり検出される。残差は英米発音差の範囲で、品質上許容される方言差。
- 固有名詞境界(①との整合)と、AMB対の用法判定(語義ではなくASR転写の綴りだけで判断するため限界あり=一方向・警告で緩和)。
- Z原作が古い英綴り(`to-day`、`connexion`等)を持つ場合の辞書外語: fail-closed(従来どおりNG)。実測はZ次作品で。
