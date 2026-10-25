# OPEN333_EVAL_01(しわ↔すわ=N3-07 のAPI 0評価。委任_11、2026-10-25)
事前登録=`OPEN333_PREREGISTERED_01.md`(§0〜§6)。**API 0(socket guard)・LLM/ASR/TTS呼出0・費用0円・Production file無変更**(`git diff --stat -- er007_*.py er011_*.py er078_*.py`が空)。使用モデル: なし(保存済み転写のみ。転写元は既存のOpenAI `gpt-4o-mini-transcribe`/Azure ja-JP。最新モデル原則25節は評価対象外=生成・ASR呼出なし)。
母集団=1,327件(既存771+未知493+合成負例の(canon,Primary転写)重複除去後63)。基準=07A適用後のProduction HEAD。再現: `PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/eval_open333_api0_0{1,2,3}.py`。
証跡: `open333_trace_01.out.txt`(経路trace)、`open333_api0_eval_0{1,2,3}.out.txt/.json`、test=`proto_open333_fix_0{1,2}_test_01.py`(46 passed)。

## 1. 経路(N3-07 `月のしわ、8,900本超` / 転写 `月の巣は八千九百本長。`)
`open333_trace_01.out.txt` §1 の実行trace(Production関数そのまま):
1. `protected_check_ja`(er007:242)のopcode: `replace 'しわ8,900'->'巣は八千九百'` と `replace '超'->'長'`。前者は数字が左右で異なる(`8900` vs なし)ので `number_mismatches=[('8900','')]` に記録して `continue`(er007:258-261)。**このopcodeに糊付けされた非数値差 しわ→巣は は `content_diffs` に入らない**。`content_diffs`=[('超','長')]のみ。
2. `classify_ja_asr_match` は数字不一致のみ(否定なし)なので `try_rescue_before_resolver`(er011:289)へ(er007:381)。Candidate B/C/D-1(全文の読み一致/正規化後一致)は不一致で素通り。
3. Candidate E(er011:363-365)は `remaining_diffs=[超/長]` だけを見る。`超`={ちょう} と `長`={おさ,おさむ,ちょう,なが} に共通読み `ちょう` → 全件説明済みとして **PHONETIC_MATCH(reason=Candidate E)**。
4. Primary段: 07A後の最終Gate(値ガード)は `8,900`=`八千九百` で EQUAL → `state=PASS reason=primary_pass label=PHONETIC_MATCH`(`unified_judge`込み、`equivalence_basis=READING_MATCH`→最終Gate通過)。しわ↔すわは**どの段でも比較されていない**。

反証(trace §2・§3・§4、同一文字対で条件だけ変える):
| 条件 | 現行Production | 読み |
|---|---|---|
| N3-07本体(糊付け+超/長) | PASS | 本件 |
| 超/長の偶然の同音差を外す(`…本超`) | NG(TRUE_CONTENT_MISMATCH) | Eは`remaining_diffs`が空だと不成立。**PASSは同文の別所の同音差(超/長)に依存** |
| 数値を外す(`月のしわ、本超`/`月の巣は本長`) | NG(`p2_exclusion:A4_C2_HOMOGRAPH`) | 糊付けが無ければしわ→巣はは不合格 |
| `月のすわ八千九百本長`(opcodeが し→す と 数値に割れる) | NG | 同じ「す」でも糊付けされないとNG=**し↔すを許す規則は無い**。alignment依存 |
| `月のしば八千九百本長`/`月のす八千九百本長`/`月のそ…`/`月のし…`(わ脱落) | **PASS** | 糊付けされた残余は何でも通る(母音・濁音・文字脱落を問わない) |

## 2. 影響範囲(件数)
**Candidate E経由で現にPASSしている行: 23件 / 現行PASS 710件**(`open333_api0_eval_02.out.txt` 棚卸し)。entry別(数値entry=今回の糊付け経路、非数値entry=従来のOPEN-333本来の過許容):
| 分類 | 数値entry | 非数値entry | 計 | 内訳 |
|---|---|---|---|---|
| 正しく救済(正常音声/対照。残余なし or 説明済み) | 1 | 14 | 15 | P4 `このあと…3人`/`この後…三人`(あと/後)ほか P4 10[あと→後8・関→乾・走れ→走レ等]+未知4 |
| **誤PASS(既知負例=真の読み違い)** | 3 | 4 | 7 | **N3-07(糊付け残余しわ→巣は=本件)**、N1-new-032/033(今日→こんにち/いちば→市場)、N1-new-034/037/039/048(市場→いちば・上手→うわて・月は→つきは)=同形異音/OPEN-333本来 |
| 判定不能→**正常音声と推定** | 1 | 0 | 1 | MOON `attempt3_minimalfallback.wav#1` `月の詩は八千九百本長`(糊付け残余しわ→詩は。助詞はをwaと読めば同音=`B_LIGHT_EVAL_02.md` §3・`EVAL_01.md` §5の構造的同一クラス。同一wavの他転写はNG。音声の再聴は未実施=推定) |
糊付け未検査の残余を持つPASSは**N3-07とMOON#1の2件のみ**(両方とも月題の同一原稿)。

規則種別(Eが救済したspanののべ33件):
| 型 | span数 | 備考 |
|---|---|---|
| 漢字↔かな(読み一致) | 23 | あと/後 等。正当な救済が大半 |
| 漢字↔漢字(共通読み) | 4 | 超/長・関/乾 等 |
| かな↔かな(正規化差 れ→レ) | 1 | |
| **共通読みなし(Eが検査しない便乗差分)** | 5 | entity_like(カタカナ/略語同士)の ロ→ラ・ヴェ→ベ・muse→ミューズ・meta→メタ・museで起き→ミューゼンロを着。**4行**(P4 3+未知1)。**第2の漏れ**(§4) |
- **母音違い(し↔す型)をEが同一視する規則: 0件**(trace §4 `すわ`NG・`sweep`)。仮説H2(仕様どおり)は否定。
- 濁音違い: Eの救済span内0件(濁点のみ差は`phonetic_uncertain`=cascade_eligibleでCascade行き)。長音違い: 0件(`コーヒー/コヒ`はNG)。
- 非PASS→PASSへ動いた行: 全案で0件。

## 3. 案の評価(事前登録K1〜K12、E1/E2/E3=v1、E1P/E3P=v2)
| 案 | K1 N3-07遮断+糊付けsweep | K2 単調 | K3 正常NG化0 | K4 既知負例回帰 | K5 副作用(state変化) | K9 再生成増 | 判定 |
|---|---|---|---|---|---|---|---|
| E2 数値entryでE不使用 | 遮断(ただし正例の`…円長です`等も巻き込む) | 0 | **不合格**: P4正常行(あと/後+3人/三人)をNG化、MOON#1もNG化 | NG化したN1 032/033は歓迎 | 5件PASS→非PASS | 2/677=0.30% | 不採用 |
| E1 残余監査 | 遮断 | 0 | **不合格**: MOON#1(正常音声)をNG化 | — | PASS→非PASS 2、NG→NGの理由変更2 | 1/677=0.15% | 単独不採用 |
| E3 全文再比較 | 遮断 | 0 | **不合格**: 同上 | — | PASS→非PASS 2、理由変更1 | 1/677=0.15% | 単独不採用 |
| **E1P** E1+助詞発音等価の免除 | 遮断 | 0 | **合格(0件)** | — | PASS→非PASS 1(N3-07)、NG→NGの理由変更1(MOON#2、state不変) | 0/677=0.0% | 可(E3Pより劣る) |
| **E3P** E3+助詞発音等価の免除 | **遮断**(N3-07、sweep: し/す/そ/しば/すば/しわー/しわわ…の糊付け残余PASS 14件全て。正例`しわ`+超長・`円長です`は維持) | **0** | **合格(0件)** | — | **PASS→非PASS 1(N3-07)のみ・他に変化0**(state/reason/label完全一致) | **0/677=0.0%** | **推奨(限定VALIDATED候補)** |
- K6 決定性: eval_01/02/03 いずれも2回実行で出力json・標準出力が完全一致(sha `aa57ddca…`/`e0e867a5…`/`e3f8fa0f…`)。K8: API 0、費用0円、Production無変更。
- K7: Eは母音違い等を同一視する規則を持たない(上記)。H2否定。
- K10: 免除(助詞は→わ・へ→えのみ発音形)が働く行=MOON#1の1件のみ(現行PASSを維持。新規受理0)。K12: E1PとE3Pの差=MOON#2のreason/label(`final_gate_value_diff/PHONETIC_MATCH`→`p1_value_diff/TRUE_CONTENT_MISMATCH`、NG_PROTECTED不変)の1行のみ。E1Pはopcodeの切れ方に依存するため、alignment非依存のE3Pを推奨。
- parity開示: 現行Production再計算とeval_04保存(proto)の不一致1件(`N1-er066b-021` `NG_PROTECTED` vs `NG_SECONDARY_UNAVAILABLE`、いずれも非PASS、07A前後のstub表示差)。
- v1→v2は同一コーパスの結果(MOON#1)を見て設計を変えた履歴(開示済み、準備書§5)。糊付け残余を持つ実データPASSは2件のみで汎化はsweepで補った。

## 4. 第2の漏れ(便乗PASS。E4/E3P4。情報提供)
Candidate Eの `remaining_diffs` は non-cascade 差分のみで、cascade_eligible差分(entity_like/phonetic_uncertain)は未検査のまま、他の差分のE救済に便乗してPASSする(現行Production)。実データ4行: P4 `走れメロス→走レメラス`(ロ→ラ=母音違い)・`ヴェラ→ベラ`・`muse→ミューズ`、未知1(`museで起き→ミューゼンロを着`)。凍結負例で遮断される行は**0**(neg_pass_blocked 0)、正常と推定される4行(4/677=0.59%)を `ASR_VALIDATION_UNCERTAIN`(Cascade=Azure再確認)へ回す(API 0ではstubのため`NG_SECONDARY_UNAVAILABLE`表示、実運用ではAzure転写次第)。単調(非PASS→PASS 0)。E3P4=E3P+E4: PASS→非PASS 5(N3-07+上記4)。
**所見**: 実害(誤PASSが実際に起きた証拠)は凍結データ内に無く、変更は正常音声のCascade費用・再生成を増やす側。N3-07の是正とは独立のため、本委任の推奨には含めない(Opus/Fable判断)。
