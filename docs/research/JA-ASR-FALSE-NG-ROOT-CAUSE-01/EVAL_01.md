# EVAL_01(API 0部分。Phase 3準備、委任_02、2026-10-25)

評価対象=プロトタイプ **v1**(`proto_reading_compare_01.py`、sha256先頭16桁 `8799aa60fed66e2d`、v0=`c3e61412c7adaada`は`proto_reading_compare_01_v0_frozen.py.txt`に退避)。DEV専用・Production file変更0・API呼出0(socket接続を例外にするguard下で実行)。
再現: `PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/eval_api0_v1_01.py`(約15秒)。出力=`eval_api0_v1_01.out.txt`(要約)/`.out.json`(全件)。
方式: Production adapter `evaluate_attempt_ja_with_cascade_detail`(統一judgeの最終ANDゲート込み)をそのまま呼び、Primary層`_numeric_value_equivalence`だけをin-processでv1に差し替え(M7: 評価=配線候補と同一関数、Production関数を直接import)。Secondaryは呼出0のstub。使用LLM/ASR/モデル=なし(保存転写のみ)。

## 1. M5 誤PASS 2本立て(N-1合成テキスト対 150負例+構造的同一1件)
| 区分 | 件数 | 結果 |
|---|---|---|
| **増分誤PASS**(現行NG→v1 PASS)=合否基準 | **0 / 150** | 合格(0件) |
| 構造的同一(`月のしわ`/`月の詩は`) | 1 | 月題のP-1正例と**同じ文字列対**。テキストでは正例と区別できないため負例集合から分離(下記§5)。v1 PASS |
| **既存誤PASS**(現行でも既にPASS=ASRの既存盲点。報告のみ) | 23 / 150 | `三日間/三日目`、`3~5日/35日`、同形異音(今日→こんにち、市場→いちば、一日→ついたち、上手→うわて)、助詞誤読(月は→月ハ・町へ→町ヘ・つきはまるい)、`三分の一/3分の1`、一分→いちふん、三日→さんにち、七晩/七番 等。全件が現行PHONETIC_MATCH/NUMERIC_VALUE_EQUIVALENTで通る。v1で新たに通るものではない |
| v1がM1/M3で止めた件 | 6 | 否定差5(negation)、同形異音+数1(`3人できょう話した`/`三人で今日話した`=C2逆方向) |
| 値ガード不一致で止めた件 | 80 | DIFF/UNKNOWN/AMBIGUOUS/数字差ありNO_VALUES(M3) |
N-1構成=er066既存敵対88(NEGATIVE 35・NEGATIVE_02 39・PRODBUG 9・AMBIGUITY 5)+新規63(M6のテキスト版を含む)。型別内訳は`n1_pairs_01.py`。rule of three=150件0失敗→95%上限2.0%(母集団全体の上限のみ。型ごとの保証ではない)。
**Secondary側(A4)**: N-1を「Azure転写として来た」と見立てた受理 = A4(a)(値のみ一致)4件 / A4(b)(発音一致)0件(構造的同一1件を除く)。A4(a)の4件(`三分の一`/`3分の1`×3、`3人でついたちに会った`/`三人で一日に会った`)は、いずれも**現行のPrimary側`NUMERIC_VALUE_EQUIVALENT_MATCH`が既に通している型**(上表の既存誤PASS)をSecondaryへ同じに拡張した結果で、新しい種類の誤PASSではない。

## 2. 正例対照(er066 POSITIVE 37+POSITIVE_02 10、期待=救済されうる)
現行PASS 37 → v1 PASS 39。回帰(現行PASS→v1 NG)=**0**。増分2件=`20％の人`/`20パーセントの人`(2形)。理由=現行`_numeric_value_equivalence`の「number_mismatches非空」ゲートが、`％`↔`パーセント`のように数字差が検出されない値一致対を落としていた(桁区切り`8,900`と同じ機序、R3)。v1はゲートを外し値ガードEQUAL+残り完全一致で受理。

## 3. 月Std題 attempt別(v1判定。Production adapter+差替え層、Azure stub)
| attempt | Primary転写 | 現行 | v1 | 備考 |
|---|---|---|---|---|
| 1 | 月野詩は**8000句800**本超え | NG_PROTECTED(p1_value_diff) | NG_PROTECTED(p1_value_diff) | 値ガードDIFF=正しい挙動。救済にはB-light(保留)が必要 |
| 2 | 月の死は**八千九百**本超 | NG(Azure→NG_BOTH) | **PASS**(`JA_PRON_VALUE_EQUIVALENT_MATCH`、warning `JA_PRON_EQUIVALENT`) | HR回避。最終ANDゲートapplied=True(test) |
| 3 | 月の氏は**8000900**本超 | NG_PROTECTED(p1_value_diff) | NG_PROTECTED(p1_value_diff) | 同上 |
| 2(Azure転写) | 月の詩は8900本超 | 不受理 | **A4(b)**(発音一致)でのみ受理。A4(a)(値のみ)では不受理 | Primaryが通るためAzure不要。A4(b)=新仕様候補(M4) |
→ **月題は案A(Primary側A3)のみでattempt2が通り、attempt1/3は従来どおりNG**。attempt1/3の誤NGを解消するには(Azure実測=Phase 3 A-1と)B-lightが要るが、B-lightは**保留**(R1)。

## 4. P-3/P-4 flip(保存転写の再判定)・原因別集計(R4)
| データ | 件数 | 結果 |
|---|---|---|
| P-3 NG pool(`ng_pool_cases_01.json` 150転写) | 150 | flip 8転写(ユニーク4)。Primary 2 / Secondary 6 |
| P-4 全JA attempt(canonical復元可能562→ユニーク(canon,primary)421) | 421 | 現行PASS 334。**回帰=0**(PASS→NG/ラベル変化なし)。NG→PASS flip=2(下表の1と4) |
※P-4はPhase 2予告の「全1,027 attempt」ではなく、`audit/tts_generation_results.json`からcanonicalを復元できた562 attempt(他は復元手段なし=記録上の制約)。
flip個別審査:
| # | where | 内容 | 原因分類 | warning | 所見 |
|---|---|---|---|---|---|
| 1 | Primary | 月題attempt2 `月のしわ`/`月の死は八千九百本超` | A3_value+A2_particle | JA_PRON_EQUIVALENT | **正当救済**(ユーザー試聴で月題3音声すべて問題なし) |
| 2 | Secondary(A4b) | 同wavのAzure転写 `月の詩は8900本超` | A3_value+A2_particle | JA_PRON_EQUIVALENT | 同上。ただしA4(b)=新仕様候補。Primary PASSで不要 |
| 3 | Secondary(A4a)×5 | Melos comment_2 `三人`/Azure`3人` | A1_value_notation | なし | **正当救済**(仕様L2865が明記する値等価。mock再現と同型。同一転写が5 attemptに重複) |
| 4 | Primary | Melos preview attempt2 `三日目…道をふさぐ`/`3日目…道を塞ぐ` | A3_value+pron(`ふさ`↔`塞`) | JA_NUMERIC_IRREGULAR_READING+JA_PRON_EQUIVALENT | **推定正例**(読みは同じ。三日目=みっかめ系の不規則読み警告が付き事後試聴リスト対象)。実音声の試聴確認をPhase 3で依頼 |
原因別: A1_value_notation 5(Secondary)/ A3_value+A2_particle 2 / A3_value+pron 1 / A2_particle 0 / ENGINE_reading_difference **0**(エンジン差による通過なし=R4の個別正当化は不要)。
**Phase 2の推定正例のうちMelos 4転写(comment_1 attempt1=`あと→後`、attempt2/3=`つ→付`、kgcpw comment_1=`支配者→し|敗者`)は、v1が止めた**(`あと/後`・`つ/付`=C2逆方向: ASRが書いた漢字spanが複数読みを持ち原稿の読みがその1つ、`支配/し敗`=C2順方向)。M1により救済件数は減った(Melos preview attempt2のみ残る)。品質優先の想定どおりの動作。Phase 2の5転写→v1で1転写。

## 5. 構造的同一クラス(要Fable確認の論点)
`月のしわ`(原稿の`わ`は非助詞)と`月の詩は`(ASR出力の`は`は助詞)は、**テキストだけでは「正しく`しわ`と読まれた音声」と「`しは(ha)`と読まれた音声」を区別できない**。月題の正例救済そのものがこのクラス。現実にはTTSは入力`わ`を`wa`と読むので「原稿=わ、音声=ha」は生じにくい(逆方向=原稿が助詞`は`でTTSが`ha`と読む場合は現行PHONETICも案Aも検出不能な既存盲点=O3)。従って**M5の「増分誤PASS 0」はこのクラスを数えると構造的に0にできない**。事前登録`_02`では、このクラスを増分誤PASSの母数から外す理由(正例と同一入力であること)と、代わりにN-3の実音声(`つきのしはがおおい`→haと読まれるか等)で物理的前提を確認する規則を明記した。この扱いはFable確認事項(分類B=承認範囲内で自己解決した判断、ただし採否提示で開示)。

## 6. 注意(正直な限界)
- ASRの実際の書き方を再現しているのは保存転写(P-3/P-4)のみ。N-1は「ASRがこう書きうる」の想定文で、実ASRの分布を代表しない。実測はPhase 3 N-3。
- 現行盲点(既存誤PASS 23件)はv1の対象外。うち`三日間/三日目`のPHONETIC_MATCH PASSと、READING_MATCHが最終値ゲートをskipする点は別OPEN(R5)で登録。
- `超え`↔`超`(ちょう/こえ)はv1でも救えない(正しい挙動=事前登録)。月題attempt1の`超え`は実音声が`こえ`の可能性がある。
