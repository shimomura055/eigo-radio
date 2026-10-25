# OPEN333_PREREGISTERED_02(E3 v3[P-1なし]・M-3 sweep・M-2 Secondary全件・E4の事前登録。JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_12、2026-10-25)
評価script実行より前に固定。基準は結果を見て緩和しない(厳格化のみ可。変更時は末尾に改訂記録を追記)。OPEN333_PREREGISTERED_01.md(v1/v2/E4初版)は変更しない。

## 0. 凍結物
- proto v3 `proto_open333_fix_04.py` sha256 `34047670d79935ec63854f2d25d173a890d8001bd88398e76f5569685e668dc8`(mode E3=非数値差の全件再検査のみ / E3V=E3+値ガード要求[R-6])。
- E4 proto `proto_open333_fix_05.py` sha256 `af9f8b60a092a781ab0d9115e16ea3a2e8e9da3444c2352d4138301b856925b8`(E3V_E4 / E3V_E4E)。
- M-3 sweep `sweep_cases_open333_02.py` sha256 `bc2a1e2d2a5fb5b21e41274bfd273159df15c47634c76bb6332da4cb92ce6360`(8クラス、keep/blockタグ付き)。
- E4 負例・対照 `sweep_cases_open333_e4_01.py` sha256 `1b4ea6df48e111cb41c19fbb9875280a03f75073bd20c08f2e5c99783e1b8096`(170件: neg/cost/ctrl)。
- 注: 委任文は『proto_open333_fix_03.py』を指定したが、同名は委任_11で事前登録・凍結済みのE3P+E4 protoのため上書きしない。v3=fix_04、E3v3+E4=fix_05。
- 比較基準=現行HEAD Production(`er011_*`のE3関連flagが存在する場合はFalseに固定して再現)。proto E3/E3Vは `try_rescue_before_resolver` の戻りを後処理で拒否するのみ(PASS集合は縮む方向のみ)。

## 1. R-1(Candidate E承認範囲の確認、評価前に実施)
DECISION_LOG.md:10208-10300(PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01 Phase 2、2026-09-27、APPROVED_FOR_PRODUCTION)を全文照合した。Candidate Eが『数字不一致の経路(er007:366-386のOPEN-145分岐=protected落ち後に追加型チェックを試みる経路)』で動くことを明示した記述は**無い**(記述は固有名詞読み解決core・Ledger・JA-3『Hormuz B1B 海からの封鎖 Candidate E PHONETIC_MATCH再確認』=非数値entry)。数字不一致経路は2026-09-12のOPEN-145承認(er007:366-380のコメント『誤PASSのリスクを生まない』)が前提としていた『全文の読み一致/正規化後一致』のみを許す経路であり、後から同関数にCandidate Eが追加されて数値entryでも到達するようになった。→ 『Eがこの経路で動くこと自体が承認前提外』。ただしE3は『承認時の前提(残差分を全て読みで説明できたときのみ)に戻す最小是正』として説明でき、結論は変わらない(Opus R-1)。

## 2. 比較する案
E3(非数値差の全件再検査。数値span=値ガードがnum/frac/approx/unparsedと認識したspanを両側同一placeholderへ置換、P-1なし)/ E3V(E3+値ガードEQUAL/NO_VALUES/AMBIGUOUSのみ許可[R-6]、判定を広げない方向のみ)/ E3V_E4・E3V_E4E(E4、情報提供)。

## 3. 合格基準(E3、E3V それぞれ)
- V1 N3-07(しわ↔すわ)がPASS以外になる。N3-07と同型の糊付け残余PASS(sweep の block タグ)は、現行PASSなら全てPASS以外になる。
- V2 単調: 非PASS→PASSが0件(全行+sweep+E4行+合成)。
- V3 正常NG化: 負例以外(P4・P3・POS・MOON・未知)のPASS→非PASSは、**MOON attempt3_minimalfallback#1(転写『月の詩は八千九百本長』)のみ許容**(理由=助詞は→わの発音等価を救済するのはv2/βの担当。Opus R-3/Fable判断)。それ以外が1件でも出たら全件を目視し、正常音声の誤NG化なら不合格。
- V4 副作用なし: 『Candidate E経由PASSの数値entry』以外の行のstate/reason/labelは完全一致(other_changed 0)。
- V5 sweep: keep タグの行は現行と完全一致(state/reason/label)。block タグの行は現行がPASSなら非PASS。現行が既にNGの行は対象外として件数を開示する。**Eへ実際に到達した件数をクラス別に開示**(到達0のクラスは『未検証』と明記)。
- V6 Secondary(M-2): 保存済みSecondary転写[usage_log.jsonlのAzure転写、ng_pool_cases_01.jsonのsecondary、attempt jsonの scg_info.secondary_transcript(canonical不明のものは除外し件数開示)]に加え、**全Primary転写をSecondary転写として扱った場合**(同じ受理関数: classify→voicing upgrade→orth)も含め、Secondary受理判定(SCG_PASS_CLASSIFICATIONS=EXACT/NORMALIZED、ORTHOGRAPHIC_VARIANT_CONFIRMED)の現行 vs E3 の変化が0。classificationラベルの変化は全件開示。
- V7 決定性: 2回実行でoutput jsonのsha256が一致。
- V8 API 0・費用0円: socket guardでネットワーク接続を例外化。LLM/ASR/TTS呼出0。評価中、Production fileは未変更(proto評価はHEADに対して行う)。
- V9 再生成増の見込み: 負例以外の現行PASSに対する(PASS→非PASS)の割合を開示。

## 4. M-3 sweep の期待(クラス別)
クラス1=糊付け/片側挿入削除、2=複数数値・1万2,000、3=小数・%・単位・分数、4=かな数詞(正常NG化検査)、5=漢数字を含む普通の語(保持/入替)、6=P-1負例(はし→わし/はな→わな/へや→えや)+月題#1型、7=文頭・文末、8=全角数字・〇/零。各行のタグと注記は `sweep_cases_open333_02.py`。
- クラス6の月題#1型(`月のしわ`→`月の詩は`)は block(E3では仕様どおりNG。救済はv2/βの担当。V3の許容に対応)。

## 5. E4(便乗PASS)の事前登録(情報提供。Production適用の合否ではなくFable判断材料)
- 負例=カタカナ固有名詞/語の母音・子音違い、略語の誤読、濁点のみの違い(kind=neg)× 乗り物(Candidateで救済される同音差)。cost=等価表記(ヴェ↔ベ、NASA→ナサ等=正常でE4によりCascade費用がかかる側)。ctrl=名は同一で乗り物のみ(E4で不変であるべき)。
- K-E4-1 neg: 現行HEADでPASS(=便乗が実在する)件数・クラス別と、E4がCascade(ASR_VALIDATION_UNCERTAIN)へ戻す件数。
- K-E4-2 単調(非PASS→PASS 0)。K-E4-3 ctrl: E4で変化0(変化があれば不具合)。K-E4-4 cost: E4でCascade行きになる件数(=Azure確認費用0.2667円/件の見込みの根拠)。
- K-E4-5 実データ(1,327行): E4が動かす行を全件列挙し(a)便乗差分が本物の読み違い疑い/(b)正常音声のCascade送り に区別。E3単独との差を明示。
- E4/E4E(entity_like限定)の差を開示。E4はE3と違い『承認済みの安全条件の機能不全』の是正であり、挙動(Cascade費用)に影響するため、Production適用はFable判断(本委任では適用しない)。

## 6. 開示すべき限界
- 評価データの実Candidate E数値entry残余ありPASSは2件(N3-07、MOON#1)のみで、汎化は sweep と test で補う。
- Secondaryの『保存済み転写』はcanonicalと対になるものが約100件程度で、1,098件ではない(1,098はPrimary側集計。委任文の数値の取り違えを開示)。補完として全Primary転写をSecondary扱いにして受理関数に通す。
- API 0評価のためCascade(Azure)の実結果は不明(E4の送り先UNCERTAINは NG_SECONDARY_UNAVAILABLE と表示される)。

## 7. 改訂記録(評価実行後の開示。基準の緩和にあたる点は隠さない)
- V5『keepタグの行は現行と完全一致(state/reason/label)』を、評価scriptでは『PASS/非PASSが現行と同一』+『NG→NGのreason差は別掲』に実装した(`eval_open333_api0_04.py` の `sw_viol`)。これは**緩和**にあたる。理由: E3でEが拒否されるとNG→NGでもreason/labelが変わる(`final_gate_value_diff`→`p1_value_diff`、PHONETIC_MATCH→TRUE_CONTENT_MISMATCH。判定は同じNG)。該当は40件のsweepのうち1件(`２〇〇本超`↔`二百本長`、現行からNG)。厳格基準(完全一致)での違反数も `OPEN333_EVAL_02.md` §3 に併記した。
- 追加した関数レベル検査(`audit_viol`): 現行がEへ到達しない行も含め、keep=非数値差の拒否が空/block=非空、を直接検査。V5の補強(厳格化)。
- 評価実行後の追加(結果を見た後の追加であり事前登録ではない): proto E3 と E3V(値ガード要求)の比較、`eval_open333_prod_parity_01.py`(proto↔Production一致)、`open333_runtime_fire_01.py`(runtime発火)。
- 評価scriptのsha256: `eval_open333_api0_04.py` `30a69e65b5061a97f481e14ae67d1c5ac7fc9b221a2e903fcf56735eb22e7c48`、出力json `72f9097d7ac95f2ead94398c8437fd4de1b1133dab7ec23c412c8bb277e6046e`(2回実行で同一=V7)。
- V4『Candidate E経由PASSの数値entry以外の行は state/reason/label 完全一致』の厳格判定: 実データ1,327行中**3行がNG→NGでreason/labelだけ変化**(N1-er066b-020『三日目』↔『3日間』、MOON attempt3#2、N3-02。いずれも現行から`NG_PROTECTED`で、E3により`final_gate_value_diff`[PHONETIC_MATCH]→`p1_value_diff`[TRUE_CONTENT_MISMATCH]へ。**state=NG_PROTECTEDは同一、PASS/非PASSの判定変化なし**、Secondary呼出なしも同一)。厳格にはV4不合格(3行)だが、判定結果(PASS/NG・遷移先)は不変なので『理由表記の変化のみ』として開示する。
