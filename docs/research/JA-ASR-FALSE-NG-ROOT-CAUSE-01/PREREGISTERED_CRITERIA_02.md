# PREREGISTERED_CRITERIA_02(Phase 3 事前登録 改訂版。Opus条件A必須M1〜M7反映。01は残置、本書が優先)

## 0. 凍結
- 凍結対象=**v1** `docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/proto_reading_compare_01.py` sha256(全体)= `8799aa60fed66e2d78eea00bb263e99ebf069db83c6fe1d3191d1d96870c1733`(先頭16桁 `8799aa60fed66e2d`)。v0(`c3e61412c7adaada`、`proto_reading_compare_01_v0_frozen.py.txt`)からの差分:
  - M1: A7(登録読み`expected_readings`不一致)とC2同形異音(順方向=Production`_scg_c2_candidate`+span別`_scg_heterophone_candidate`、逆方向=ASR側漢字spanが複数読みを持ち原稿読みがその1つ)があれば救済しない。Primary・Secondary共通。
  - M2: 新分類名`JA_PRON_VALUE_EQUIVALENT_MATCH`(`_READING_MATCH_CLASSIFICATIONS`・`APPROVED_EQUIVALENCE_BASES`・`SCG_PASS_CLASSIFICATIONS`に入れない=最終ANDゲートが走る)。値のみ一致は既存`NUMERIC_VALUE_EQUIVALENT_MATCH`。
  - M3: `number_mismatches`が空でなければ値ガードEQUALのみ。NO_VALUESは数字差が無いTCMのときだけ。UNKNOWN/DIFF/AMBIGUOUS不可。否定差・否定マーカー差も救済しない(P1保護差を迂回しない)。
  - M7: Production関数(`_ja_value_form`等)を直接import(複製なし。AST testで固定)。Production`_numeric_value_equivalence`の受理集合⊂v1の受理集合をparity testで固定。
  - R3: A1(桁区切りstrip)は廃止(`extract_atoms_ja`が桁区切りを1 atomにする)。Productionが`8,900`/`8900`を落とす原因は「number_mismatches非空」ゲート(桁区切り`,`はcontent_diff)であり、v1はそのゲートを外し値atom化後の残りで比較する(副次効果: `20％`↔`20パーセント`も受理)。
  - 評価のadapter差替え方式=Production adapterをそのまま呼び、Primary層`_numeric_value_equivalence`のみin-processで差替え(Production file変更0)。
- Phase 3での変更は「逸脱」として理由・影響を全て記録する。凍結は評価開始前・N-3作成前(v0の欠落をv1で是正するのは逸脱ではない、Opus確認済)。評価データ(N-1/N-3文)はv1の凍結後に確定済み(N-1は`n1_pairs_01.py`、N-3は`n3_clips_01.json`)。

## 1. 誤PASS基準(M5。2本立て)
| 指標 | 定義 | 基準 |
|---|---|---|
| **増分誤PASS**(合否) | 負例のうち「現行=NG かつ v1(Primary層差替え後の最終判定)=PASS/PASS_WITH_WARNING」。Secondary側は別表(A4(a)/(b))で同定義 | **0件**。1件でも出たら不合格=原因修正→v2として再凍結→再評価 |
| **既存誤PASS**(報告のみ) | 負例のうち現行でも既にPASS(ASRの既存盲点) | 件数・型を報告。必要なら別OPEN(合否に使わない) |
- 構造的同一クラス(例外の明示): `月のしわ`/`月の詩は`型(原稿の`わ`/`え`が非助詞、ASR出力が助詞`は`/`へ`)は、**月題の正例(P-1 attempt2)と同一入力でありテキストから区別できない**ため、N-1の増分誤PASS母数から外して別記する(EVAL_01 §5)。代わりにN-3で物理的前提を実音声で確認する: `N3-26`(`つきのしはがおおい`)・`N3-27`(`ヘをかく`)がhe/haと読まれ、かつv1がPASSさせた場合は**増分誤PASSとして数える**(=基準違反)。また原稿`わ`をTTSがwaと読む通常ケースはP-1で確認済み。この例外の扱いを緩和と見なす場合はFableが指摘すること(厳格化は可、緩和は禁止の原則)。
- rule of three: 母集団全体に対する上限のみ(N-1 150件で95%上限2.0%、N-1+N-3 180件で1.7%)。N-3は**型ごとの機構test**であり、型ごとの誤PASS率は推定しない。

## 2. 評価セット
| ID | 内容 | 件数 | 期待 |
|---|---|---|---|
| P-1 | 月Std題3音声(ユーザー試聴「問題なし」) | 3 | attempt2=PASS。attempt1/3=値ガードDIFFで従来どおりNG(**正しい挙動**。誤NGの残りとして記録、B-light保留)。attempt1の`超え`は実音声が`こえ`の可能性があり、発音一致層で救えないのは正しい挙動 |
| P-2 | 設計で見つけた救済候補の元音声(Melos preview attempt2=v1 flip。ユーザー試聴を依頼) | 1〜2 | flipは試聴確認 |
| P-3 | NG pool(`ng_pool_cases_01.json`150転写)のflip全件を個別審査(EVAL_01 §4) | 全flip | 各件の最終所見(正当/要試聴/不当) |
| P-4 | 非回帰: canonical復元可能なJA attempt 562(ユニーク421)で、現行PASSの判定・ラベルがv1で不変 | 421(現行PASS 334) | 回帰0 |
| N-1 | 合成テキスト対150(er066既存88+新規63の内、構造的同一1を除く)。M6のテキスト版(同形異音/数+同形異音/連濁・音便/不規則/助詞誤読)を含む | 150 | 増分誤PASS 0 |
| N-2 | 保存NG音声のうち複数エンジンが原稿と異なる語で一致したもの(台風機/風師波、疲れきって、渋滞→中断、七晩、`42何46`等) | 10〜14 | v1 flipが出たら自動判定せず試聴確認(現状flipなし) |
| N-3 | 新規生成の誤読音声30 clip(`n3_clips_01.json`、型別内訳は§3) | 30 | 増分誤PASS 0(構造的同一2 clipは§1の規則) |
- A-1: 月attempt1/3のwavにAzure各1回(**情報取得のみ**。B-lightは保留で提示判断もしない)。A-2: 月3 wavをOpenAIで各3回再転写(数詞崩れの再現性)。A-3: v1 flipのうちAzure未呼出のwav。O1(任意、約1円): 汎用書式prompt(原稿内容を含まない「数字は算用数字で書いてください」)と`gpt-4o-transcribe`の月題3 wav並置。使用モデル=`gpt-4o-mini-transcribe`(Production Primary)/`gpt-4o-transcribe`(最新世代の同系比較)、旧/下位を使う理由=Productionとの比較基準。採用判断は別(ユーザー)。O2: Azure単独判定を副次データとして記録(採用提案はしない、UDR #136)。O3: 現行PHONETIC経路の助詞`は`=ha読み盲点を既知の制約として記録(月は→つきハ型の既存誤PASSは本層の対象外)。

## 3. N-3 構成(確定。生成は未実施)
30 clip=既存16→**8に縮小**+M6追加22。TTS入力文(かな/誤読表記)・原稿(正しい漢字)・「NGになるべき理由」は`n3_clips_01.json`(id N3-01〜30)に確定。型別件数:
| 型 | 件数 | NGになるべき理由(要約) |
|---|---|---|
| 既存縮小: 値違い/桁違い | 2 | 音声の値が違う。値ガードDIFF |
| 既存縮小: わ脱落/近音(しわ→すわ・しば)/へ→に/本→冊/否定反転 | 6 | 発音不一致・助数詞違い・否定差 |
| M6 同形異音(今日→こんにち、市場→しじょう、行った→おこなった、一日→いちにち/ついたち、人気→にんき) | 6 | 原稿と別の正当読み。C2(順/逆)で救済しない。一部(ついたち)は値atom化で現行盲点=既存誤PASS側として別記 |
| M6 数値+同形異音(`3人できょう話した`型) | 3 | M1検証(数値を含む文でC2が効くか) |
| M6 助数詞の連濁・音便(三本→さんほん、一分→いちふん、六百→ろくひゃく) | 3 | 正しい読みと違う。ASRがかなで書けば値atomが消える→M3で止まる |
| M6 不規則読み(三日→さんにち、二十歳→にじゅっさい) | 2 | 同上+不規則読み警告(R2) |
| M6 助詞の誤読(月は→つきハ、町へ→まちヘ、私は→わたしハ) | 3 | ASRは助詞表記を書く→現行も案Aも検出不能の可能性。**既知の盲点O3として結果を記録**(増分でなければ基準に影響しない) |
| M6 非助詞わ/え語×助詞読み(`つきのしはがおおい`、`ヘをかく`) | 2 | §1の物理的前提確認。haと読まれv1がPASSなら増分誤PASS |
| M6 否定反転+数 / 助数詞違い / 長音差(超→こえ) | 3 | 否定差ガード/値ガード/発音不一致(`超え`問題の対照) |
各clipは原稿(canonical)に対してOpenAI(Primary)・Azure(Secondary)の実転写を取り、現行判定とv1判定を比較する。

## 4. flipの原因別分類(R4。定義)
`A1_value_notation`(値atom化後の残りが表層完全一致=桁区切り・漢数字/算用数字・`％`/`パーセント`)/`A2_particle`(助詞は→わ・へ→えの読みだけで一致)/`A3_value+A2_particle`(値atom化と助詞読みの両方が必要)/`A3_value+pron`(値atom化+かな漢字等の読み一致)/`ENGINE_reading_difference`(値も助詞も不要で、判定エンジン(pykakasi対unidic)の差だけで通る=個別に正当化が必要、無ければ不合格)。

## 5. A4(a)/(b)の指標分離(M4)
- A4(a)=Secondary転写への**値等価のみ**(仕様L2865が明記=不具合是正)。指標: Secondary側増分誤PASS、flip件数。
- A4(b)=Secondary転写への**発音一致**(助詞読みを含む)。承認済み安全条件(L2179「PHONETIC_MATCH自動PASS未採用」・L2856「読みでの受理禁止」)に触れるため**新仕様候補(ユーザー判断)**。Phase 3ではDEV評価のみ・指標はA4(a)と別表。ユーザー提示は(a)=不具合是正、(b)=新仕様候補として分けて行う。
- Primary側A3は「承認済み2機構(値等価+発音)の組合せ」だが、2026-10-11に未採用とされた「助詞差」リストに関連するため、採否提示で明示開示する。
- B-light: 保留(Opus重大)。A-1は情報取得のみ。再検討時はKP3Vと同等の強度で設計し直す(Whisper第3票はUDR #136に触れユーザー判断)。

## 6. 合格基準(全て満たすこと)
1. 増分誤PASS=0(N-1 150+N-3 30。§1の構造的同一の扱いを含む)。既存誤PASSは報告のみ。
2. 非回帰: P-4で回帰0、既存PASSの判定・ラベル不変。**済み(API 0): 421ユニーク/現行PASS334/回帰0**。
3. 誤NG削減: P-1 attempt2=PASS(**済み**)。attempt1/3はNG維持が正しい。P-3 flip全件を表にし、「不当」=0、「要試聴」はユーザー試聴で正常音声と確認。ENGINE_reading_difference=0または個別正当化。
4. 最終ANDゲート/警告継承: 最終ANDゲートapplied=True test(**済み**)、`JA_PRON_EQUIVALENT`・`JA_NUMERIC_IRREGULAR_READING`警告がv1経路でも残るtest(**済み**)。
5. HR発生率: 保存attempt列の再判定で増加0(P-4回帰0で担保)。
6. 費用: Phase 3全体で`BUDGET_PLAN_02`のCap ¥60以内、量産単価影響±0.01円/セット未満。
7. 到達上限=**VALIDATED**。Production無変更(`proto_*`をProductionがimportしないtest済み)。配線はユーザー正式採用後。配線時testはR6(HR Lock済みsegmentの自動解除なし/reuse・resume・継承で新ラベル可読・旧reader不破壊/試聴リスト再導出で新warning拾得/flag OFFで従来挙動)。配線形=`er109_xz_scope_01.is_active_for_run()`再利用+単一flag読取関数(既定OFF)。

## 7. 逸脱の扱い
アルゴリズム変更・基準変更は理由・影響・変更前後差を`PHASE3_RESULT`に記録。緩和は禁止(厳格化は可)。
