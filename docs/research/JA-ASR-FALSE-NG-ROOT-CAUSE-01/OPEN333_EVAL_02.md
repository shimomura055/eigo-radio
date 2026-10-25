# OPEN333_EVAL_02(E3 v3[P-1なし]・M-3 sweep・M-2 Secondary全件・E4 のAPI 0評価。JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_12、2026-10-25)
事前登録=`OPEN333_PREREGISTERED_02.md`(評価前に凍結。評価後の開示は§7)。事実と推測を分ける。費用0円・API 0(socket guard、LLM/ASR/TTS呼出0、Production file評価中未変更=flagが存在すればFalse固定の基準)。
再現: `PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/eval_open333_api0_04.py`(出力=`open333_api0_eval_04.out.json`/`.out.txt`)。**決定性(V7): 2回実行でjson sha256 `72f9097d…046e` 同一**。母集団=既存771+未知493+合成負例91=1,327行 + M-3 sweep 40 + 旧v2 sweep 29 + E4行170 + Secondary対(保存103+全Primary転写1,203)。
## 1. 実データ1,327行(現行HEAD vs E3 / E3V[+値ガード要求])
- 棚卸し: 現行PASS 710のうちCandidate E経由 23(N1 6、P4 11、MOON 1、N3 1、legacy 4)。数値entryのE経由PASSは5(N1 2、P4 1、MOON#1、N3-07)。
| 項目 | E3 | E3V |
|---|---|---|
| 変化した行 | 5 | 5(E3と行単位で同一) |
| PASS→非PASS | **2**(N3-07=目的の遮断、MOON#1=下記) | 同左 |
| 非PASS→PASS(広がり) | **0** | 0 |
| NG→NG(reason/label表記のみ変化) | 3(N1-er066b-020『三日目↔3日間』、MOON#2、N3-02。state=NG_PROTECTED不変) | 同左 |
| 負例以外のPASS→非PASS | 1/677=**0.148%**(MOON#1のみ) | 同左 |
| 既知負例PASSの遮断 | 1(N3-07)/現行PASS 33(残る32は従来どおり=OPEN-333本来の同形異音等・本委任の対象外) | 同左 |
- MOON#1: 原稿`月のしわ、8,900本超！…`/転写`月の詩は八千九百本長。…`。HEADでは糊付け未検査でたまたまPASS。E3後`NG_EXCLUDED/p2_exclusion:A4_C2_HOMOGRAPH`。**承認済み仕様どおり**(非糊付けの『詩は』↔『しわ』と同じNG)。同じwavの他の転写はNG(再聴なし=正常と推定は推定)。救済はv2/βの担当。
- N3-07(`月の巣は八千九百本長。`): HEAD PASS→E3後`NG_EXCLUDED`。
- E3とE3Vは実データで差0(値ガード要求は多層防御であり、現行F1が有効な間は追加で拒否する行が無い)。
- 旧v2 sweep(29): 現行PASS 19→E3後PASS 5(`しわ`/`しわ、`+八千九百本長 等=残余なしの対照と、`円`系3)、**非PASS→PASS 0**。N3-07型の糊付け残余PASS(し/す/そ/しば/すば/しゃわ/しわー/しわわ…)は全て遮断。
## 2. M-3 sweep(8クラス、40件。タグ keep=正常・現行と同じ/ block=遮断)
| クラス | 件数(keep/block) | 現行PASS | Eへ到達 | keep維持/現行PASS keep | block遮断/現行PASS block | 関数レベル(audit)違反 |
|---|---|---|---|---|---|---|
| 1 糊付け・片側挿入削除 | 6(1/5) | 3 | 3 | 1/1 | 2/2 | 0 |
| 2 複数数値・1万2,000 | 5(2/3) | 2 | 2 | 2/2 | 0/0 | 0 |
| 3 小数・%・単位・分数 | 6(4/2) | 0 | **0(未検証)** | 0/0 | 0/0 | **2**(3.5℃↔三点五度、10km↔十キロメートル) |
| 4 かな数詞 | 5(4/1) | 1 | 1 | 1/1 | 0/0 | 0 |
| 5 漢数字を含む普通の語 | 6(3/3) | 3 | 3 | 3/3(一緒・千葉・九州保持) | 0/0 | 0 |
| 6 P-1負例+月題#1型 | 4(0/4) | 1 | 1 | — | 1/1(月題#1型) | 0 |
| 7 文頭・文末 | 3(1/2) | 2 | 2 | 1/1 | 1/1 | 0 |
| 8 全角数字・〇/零 | 5(4/1) | 3 | 2 | 3/3 | 0/0 | **2**(２〇〇本超↔二百本長、零点五↔〇点五) |
- 判定: 現行PASSのblock行(計4: しわ脱落・しわ挿入・月題#1型・文頭しわ)は**全て非PASS化**。現行PASSのkeep行(計11)は**全て維持**。非PASS→PASSは**0**。
- **到達の限界**: クラス3は全6件が現行でEに到達せず(現行NGまたは別経路)、E3の実効は未検証。クラス2・4・5・6の多くは現行がEへ到達する前にNG(block行の過半は現行から既にNG)。関数レベル検査(audit_e3単体)でblockは全て拒否・keepは4件(上表)が拒否=**値と認識されない単位(℃・km・〇/零)の表記はE3が非数値残余として拒否する**(現行HEADでは当該行がEに到達しないため判定変化0)。OPEN-522(助数詞表外)に連なる既知の限界。
- クラス6の`はし→わし`/`はな→わな`/`へや→えや`(P-1負例)は現行から既にNG(Eに糊付けで到達しない)。P-1を入れない本案ではこれらを通す経路そのものが無い(P-1を入れると通る恐れ=Opus指摘の再現は不要)。
- 厳格なV5(完全一致)の違反: keep 1件(`２〇〇本超`↔`二百本長`、現行NG→NG、reasonのみ変化。`OPEN333_PREREGISTERED_02.md` §7)。
## 3. 合否(事前登録)
| 基準 | 結果 |
|---|---|
| V1 N3-07遮断・糊付け残余PASS遮断 | **満たす**(N3-07 NG化、旧sweep 糊付け型14件遮断、M-3 block現行PASS 4/4遮断) |
| V2 単調(非PASS→PASS 0) | **満たす**(実データ・sweep40・旧sweep29・E4行170) |
| V3 正常NG化は月題#1のみ | **満たす**(1/677。MOON#1のみ。理由=承認済み仕様どおり) |
| V4 E経由PASS行以外は完全一致 | **厳格には不満足**: 3行がNG→NGのreason/label表記変化(PASS/NG判定は不変)。§7開示 |
| V5 sweep | 40件中、現行PASSのkeep/blockの違反0。クラス3は到達0=未検証。厳格完全一致では1件(reasonのみ) |
| V6 Secondary(M-2) | **満たす**: §5 |
| V7 決定性 | **満たす**(sha同一) |
| V8 API 0・費用0 | **満たす** |
| V9 再生成増 | 0.148%(1/677)。E4を足すと+0.59% |
## 4. E4(便乗PASS)の評価(情報提供。E3単独との差)
負例110(neg)=カタカナ名の母音・子音違い、略語誤読、濁点のみ差 × 乗り物5種 × entry2。cost50=等価表記(ヴェ↔ベ・ヴァ↔バ・NASA→ナサ・IBM→アイビーエム・muse→ミューズ)。ctrl10=名同一(便乗差分なし)。
| entry | kind | 件数 | 現行PASS | E3V | E3V+E4 | E3V+E4E |
|---|---|---|---|---|---|---|
| 非数値(txt) | neg | 55 | **46** | 46 | **0** | 0 |
| 非数値(txt) | cost | 25 | 24 | 24 | 1 | 1 |
| 非数値(txt) | ctrl | 5 | 5 | 5 | 5 | 5 |
| 数値(num) | neg | 55 | **50** | **0** | 0 | 0 |
| 数値(num) | cost | 25 | 25 | **1** | 0 | 0 |
| 数値(num) | ctrl | 5 | 5 | 5 | 5 | 5 |
- **事実**: 便乗PASSは合成負例の87%(96/110)で現行PASSする(`走れメロス→走レメラス`型を含む。実データでも4行)。**数値entryはE3の再検査だけで閉じる**(50→0。カタカナ差もE3の全差分検査が『説明できない』として拒否)。**非数値entry(46件)はE4でないと閉じない**。ctrlは変化0。非PASS→PASS 0。
- **E3の副作用(事実)**: 数値entryの合成等価表記(cost)25件のうち24件がPASS→再生成(TRUE_CONTENT_MISMATCH)になる。E4はこれをCascade(Azure確認)へ送る形に整合化できる(E4-N案)が、本評価では未実装・未評価。実データ1,327行では該当0。
- 実データでE4がE3Vに対して動かす行(4/677=0.59%): P4`走れメロス`↔`走レメラス`(ロ→ラ=本物の読み違い疑い)、P4『ヴェラ』↔『ベラ』(正常等価表記)、P4 comment_3『muse』↔『ミューズ』(正常等価表記)、legacy phase2_ja_evidence_01#s4(`meta→メタ`・`muse…→ミューゼンロを着`=転写が崩れた本物の誤り疑い)。→ (a)本物の読み違い疑い 2、(b)正常音声のCascade送り 2。API 0評価ではCascade(Azure)がstubのため結果は`NG_SECONDARY_UNAVAILABLE`と表示される(実運用ではAzure転写次第でPASS/NG)。
- QCD(推測と区別): 費用=Cascade 1回 約0.267円×0.59%≈0.0016円/セグメント(Cascade結果が一致なら採用=再生成なし、一致しなければ再生成)。品質=固有名詞の読み違い(ユーザーが重視)の便乗PASSを、承認済みの『entity_like/濁点差はCascade』へ戻す。納期=変更小(E分岐に数行)。E4Eとの差は、ひらがなのみの濁点差(phonetic_uncertainのみ)で出るが負例に含めず未検証。
## 5. M-2 Secondary転写
- 保存済みSecondary転写: 103対(月題・N3 30・Melos・履歴43・合成)。canonical不明のattempt json(scg_info.secondary_transcript 63件中、pool外)は除外。補完として**全Primary転写1,203をSecondary転写として同じ受理関数**(classify→voicing upgrade→orth確認)に通した。
| 集合 | 対数 | 受理(SCG_PASS=EXACT/NORMALIZED、orth確認)の変化 | classificationラベルの変化(E3 / E3V / E3V+E4) |
|---|---|---|---|
| 保存Secondary | 103 | **0** | 1 / 1 / 1(`七晩`↔`七番`型。PHONETIC_MATCH→TRUE_CONTENT_MISMATCH。いずれも受理対象外ラベル) |
| 全Primary転写をSecondary扱い | 1,203 | **0** | 5 / 5 / 9 |
- 解釈(事実): `PHONETIC_MATCH`/`ASR_VALIDATION_UNCERTAIN`/`TRUE_CONTENT_MISMATCH`はいずれもSecondaryの自動受理集合(EXACT/NORMALIZED)に含まれず、E3/E4でSecondaryの受理は変化しない。
## 6. 限界(推測と区別)
- 事実: 実Candidate E数値entry残余ありPASSはN3-07とMOON#1の2件のみ。汎化はsweepで補ったが、クラス3は到達0。
- 事実: Cascade(Azure)の実結果・実運用の頻度は未取得(API 0)。適用後の正式run集計(`open333_first_run_tally_01.py`)で確認する。
- 推測: MOON#1が『正常な音声』であるかは再聴していない(同一wavの他の転写がNGであることからの推定)。
