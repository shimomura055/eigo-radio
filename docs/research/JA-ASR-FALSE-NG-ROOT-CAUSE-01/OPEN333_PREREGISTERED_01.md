# OPEN333_PREREGISTERED_01(しわ↔すわ=N3-07 是正案の事前登録。JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_11、2026-10-25)
評価script実行より前に固定。基準は評価結果を見て緩和しない(厳格化のみ可。変更時は本書に改訂記録を追記して再凍結)。

## 0. 凍結
- proto `proto_open333_fix_01.py` sha256 `dadf1c8cc7ae9e9ff85533e8d87ab20bb3a9ec43cd35e134dd7a9e245e01f91b`、test `proto_open333_fix_01_test_01.py` sha256 `abe586ba09502d77f2b9e7e65c425dd37faa245261f4479898ebad0b3f12186b`(21 passed)、評価 `eval_open333_api0_01.py` sha256 `21a18f174fad887486d651d714881c15528fef454541f9df4da456ec2ef39a87`、trace `open333_trace_01.py` sha256 `307274d0259ba08b6a967d238860d64346ea4289ed952f4a5eaa2b34f99eed6d`。
- 評価データ=(i)`open517_api0_eval_04.out.json`のrows 1,264件(既存771[N1 151・P4 421・P3 107・POS 47・N3 30・MOON 15]+未知493)、(ii)合成負例91(`eval_b_light_api0_02.out.json` `synthetic_negative`のPrimary転写、(canon,primary)重複除去)、(iii)糊付け型の合成sweep(評価script内)。
- 比較基準=07A適用後のProduction HEAD(`er007_*`/`er011_*`/`er078_*`無変更)。proto E1/E2/E3は `er011_ja_asr_variant_layer_01.try_rescue_before_resolver` の戻りを後処理で拒否するのみ(PASS集合は縮む方向のみ)。
- 母集団の注: 委任文の「N3 30 clip・正常143・実履歴43・P-4 562・未知493・合成負例91・保存転写1,098」は B-light評価(Primary×Secondary対)側の集計単位を含む。本委任の対象はPrimary段のCandidate Eであり、P-4 562は重複除去後の421としてrowsに含まれる。実履歴43対・保存転写1,098はSecondary転写との対であり本判定(Primary段)の入力ではないため母集団に含めない(開示)。

## 1. 原因仮説(評価前)
H1(実装不具合): Production `protected_check_ja`(er007:242-326)は数字が左右で異なるopcodeを`number_mismatches`に記録して`continue`し(:259-263)、そのopcodeに糊付けされた非数値差(`しわ8,900`→`巣は八千九百`のしわ→巣は)を`content_diffs`へ入れない。`try_rescue_before_resolver`のCandidate E(er011:~367)は`content_diffs`だけを検査するので、糊付け部分が未検査のまま通る。
H2(仕様どおり): OPEN-333が記述する『漢字候補読み総当たりが過許容』の延長で、し↔す(母音違い)を許す規則が設計に含まれる。
H1とH2は排他的に検証する(trace: 同一文字対を非糊付けにすると不合格か/し↔すの候補読みが共通を持つか)。

## 2. 案
- E1: 数値opcodeの残余監査(protected_checkが飛ばしたopcodeの非数値部分が 一致|読み一致|E候補共通 でなければE拒否)。
- E3: 数値除去後の全文再比較(アラインメント非依存。Productionが非数値差へ課す検査と同じ2段+同じ窓幅)。
- E2(粗い比較案): 数値不一致entryではCandidate Eを使わない。
- (対象外として評価記録のみ)母音違い除外案・固有名詞/重要語限定案: Candidate Eは候補読みの共通を要求し、し↔すは共通読みを持たないため除外対象の規則が存在しない(trace/棚卸しで確認、K7)。

## 3. 合格基準(各案ごとに判定)
- K1 N3-07がPASS以外になる。糊付け型sweepで、base PASSのうち『残余が非説明』のもの(`しば`/`すば`/`しゃわ`等)が全てPASS以外になる。
- K2 単調: 非PASS→PASSが0件(全rows+sweep)。
- K3 正常NG化0: 負例以外(P4・P3・POS・MOON・未知)でPASS→非PASSの変化は0件。変化が出た場合は全件を目視し、(a)真の読み違い/ASR garbleで本来NGが妥当 か (b)正常音声の誤NG化 かに分類する。(b)が1件でもあれば不合格。
- K4 既存負例回帰0: 現行で非PASSの既知負例(N1/N3/合成負例)は全て非PASSのまま。現行PASSの既知負例は、PASS→非PASSは歓迎、PASSのまま残る件数を開示。
- K5 副作用: 判定変化は『Candidate E経由PASS』の行に限る(他の行のstate/reason/labelは完全一致=other_changed 0)。月題(MOON 15)の判定は変化なし、または変化は個別に目視。
- K6 決定性: 2回実行で出力jsonのsha256が一致。
- K7 母音違い仮説の反証/確認: Candidate E経由PASSのうち『かな↔かな』のspan(母音/子音/濁音/長音の置換になり得る型)の件数を開示。0なら『Eは母音違いを同一視する規則を持たない』(H2否定)。
- K8 API 0・費用0円・Production file変更0(`git diff --stat -- er007_*.py er011_*.py er078_*.py`が空)。
- K9 再生成増の見込み: 負例以外の現行PASSに対する(PASS→非PASS)の割合を開示(0なら増加なし)。

## 4. 写像
- E1/E3が K1〜K9 を満たす → 『VALIDATED(限定: API 0・DEV/proto。Production未適用)候補』。採用語は使わない。
- E1とE3で差が出る場合は差の全件を提示し、アラインメント非依存のE3を推奨するかを根拠付きで述べる。
- E2はK3で正常NG化が出る場合は不採用(比較のみ)。
- 到達上限=DEV/proto検証。Production適用の可否・ユーザー承認要否は別途(OPEN333_DESIGN_01.md)。

## 5. 改訂記録(v1評価結果を見た後の改訂。透明性のため経緯を残す)
- 経緯: §0凍結のv1(E1/E2/E3)を `eval_open333_api0_01.py` で実行(結果=`open333_api0_eval_01.out.txt/.json`、sha `aa57ddca…`)。K1・K2・K6は満たしたが、**K3(正常NG化0)がE1/E3で不合格**: 月題の実転写 `MOON japanese_title_attempt3_minimalfallback.wav#1`(原稿`月のしわ…`/転写`月の詩は八千九百本長。…`)が、現行Productionでは糊付け未検査のため『たまたま』PASSしていて、E1/E3は糊付け残余`しわ`↔`詩は`を未説明としてNG化する。助詞`は`をwaと読めば`詩は`=`しわ`(同一wavの別転写の再掲、`B_LIGHT_EVAL_02.md` §3・`EVAL_01.md` §5の構造的同一クラス)であり、E1/E3は既存の正しいPASSを壊す。E2はさらにP4正常行`このあと…3人`↔`この後…三人`をNG化(K3不合格)。→ **E2は不採用確定、E1/E3単独は不採用**。
- 改訂(v1のsha・結果は変更しない。新ファイルv2として追加): `proto_open333_fix_02.py` sha256 `f0f333f6a5a20ca800bac29e811321c877d52cd3f6983a6f4e7cfb0fcde4e65a`、`eval_open333_api0_02.py` sha256 `3a733d506332d6e0383186fac96a3b311e9c33026abc923b2c922a1737ab3b84`。差分=P-1(助詞は→わ・へ→えのみ発音形にした読み一致を、糊付け残余の『説明済み』に加える免除)。方向は『現行PASSを保つ』のみ(新規受理なし)。案=E1P/E3P。
- 追加基準:
  - K10 P-1免除は新規受理を作らない(非PASS→PASSが0件、全rows+sweep)。免除が働く行(現行PASSのまま残るCandidate E・数値entry・残余ありの行)を全件列挙し目視する。
  - K11 K1〜K9をE1P/E3Pで再判定する。K3は『負例以外のPASS→非PASSが0件』に厳格化(v1のような目視区分の余地を残さない)。
  - K12 E1PとE3Pの差分は全件提示。差が出たらアラインメント非依存のE3Pを推奨するか根拠を述べる。
- 開示: P-1の動機はv1の評価結果(MOON#1)であり、v1→v2は同一コーパスを見て設計を変えた履歴(OPEN517_PREREGISTERED_02 §2 注記10(iii)と同じ限界)。母集団でCandidate E数値entry残余ありのPASSはN3-07とMOON#1の2件のみで、汎化はsweep(助詞等価の実例・非等価の実例)で補う。

## 6. 追記(評価v2の棚卸しで見つかった第2の漏れの評価。N3-07の是正とは別枠。基準の緩和なし)
- 事実(v2棚卸し・scratch確認): Candidate Eは `remaining_diffs`=non-cascade差分だけを検査する。cascade_eligible差分(entity_like=カタカナ/略語同士の差[ロ→ラ・ヴェ→ベ]、phonetic_uncertain=濁点/半濁点のみの差)は未検査で、他の差分がEで救済されると便乗してPASSになる(現行Production、Candidate E経由PASS 23件中4件: P4 3[走れメロス→走レメラス、ヴェラ→ベラ、muse→ミューズ]+未知1)。元来これらはASR_VALIDATION_UNCERTAIN(Cascade=Azure再確認)へ回る差分。
- 本節の評価は **情報提供**であり、N3-07の是正(E3P)の合否には含めない。案: E4=Candidate E救済時にcascade_eligible差分が残るなら ASR_VALIDATION_UNCERTAIN(Cascade対象)を返す / E3P4=E3P+E4。`proto_open333_fix_03.py` sha256 `444bbe240ed6d06bda199e851c0509294935b44b3b359a023685641c406b07c7`、`eval_open333_api0_03.py` sha256 `82e31ae3e1b5dcaec33f150c504fd2164b7104c80e0f8fe33a6865ecf4300c6c`。
- K13 E4/E3P4は非PASS→PASS 0件(単調)。K14 E4が動かす行を全件列挙し、各行を(a)便乗差分が本物の読み違い疑い か (b)正常音声のCascade送り(Azure再確認費用+再生成リスク) かに区別して目視する。API 0評価ではSecondaryがstubのためUNCERTAINは `NG_SECONDARY_UNAVAILABLE` と表示される(実運用ではAzure転写次第でPASS/NG)。
- 推奨の扱い: E4はE3Pより動かす範囲が広く、正常音声に実害(Cascade費用・NG化)が出うるため、**自律適用の対象にせず**、Opusレビューの論点とFable判断に渡す。
