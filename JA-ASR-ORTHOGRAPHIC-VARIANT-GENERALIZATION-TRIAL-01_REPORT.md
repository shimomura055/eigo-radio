# JA-ASR-ORTHOGRAPHIC-VARIANT-GENERALIZATION-TRIAL-01

## 要点(5行)
1. 「経つ/たつ」「におい/ニオイ/臭い」個別対応ではなく、日本語ASR表記ゆれの
   構造的要因を7分類に整理し、各分類につき過去ログ外の自作テスト
   (計82件、PASS/MISMATCH両方)+実データ抽出(過去TRUE_CONTENT_MISMATCH
   7件、過去PASS 72件)、計161件で候補を評価した。
2. 最有力候補は**Candidate B(形態素解析ベース読みエンジン、fugashi+
   unidic-lite、¥0・LLM不要)を既存パイプラインへ「追加」する方式**
   (既存のpykakasiベース判定は一切変更せず、Reading Resolver呼び出し
   直前に形態素解析ベースの読み一致チェックをもう1段挟むだけ)。
3. この追加方式は、161件全件で**既存の判定を1件も壊さず**(reasoning上
   構造的に不可能、かつ実測でも確認)、報告事例(経つ/たつ、におい/
   ニオイ/臭い、6/6take)と実データの「あとに/後に」ケースを含む
   計11件を¥0・LLM不要で新たにPASS/自動解決させた。
4. 一方、カタカナ語の長音表記ゆれ(コンピューター/コンピュータ等)は
   Candidate Bでもほぼ解消しない(8件中3件のみ改善)ことが判明した。
   これは読みエンジンの問題ではなく別種の正規化(長音符処理)が必要な、
   本Trialで新たに特定した独立の残存ギャップである。
5. Production採用はユーザー判断(closeout: **USER_DECISION_REQUIRED**、
   詳細は末尾)。API支出は¥0(Reading ResolverのLLM呼び出しは実行せず、
   offline stubで「呼ばれたはずの回数」のみ計測)。

---

## 前提として明示する逸脱: fugashi/unidic-lite/jaconvの環境インストール

Candidate評価のため、`.venv`(プロジェクト仮想環境)へ`fugashi`
`unidic-lite`を新規インストールした(`jaconv`は元々インストール済みだった)。
これは**依存パッケージの追加**であり、コード変更ではないが環境変更では
あるため、ここに明示する。Production配線は一切行っておらず(コード
importは本Trial専用ファイル`er011_ja_asr_variant_trial_01.py`のみ)、
何もimportしなければ既存Productionの動作に影響しない。正式採用の際は
`requirements`等への追加をユーザー判断の上で行う必要がある。

## 前提として明示する逸脱その2: 過去ログ抽出件数が前回報告と一致しない

`FAMILY-A-DISCOVERY-TOWELS-A2-JA-ASR-VARIANT-RECONCILE-01_REPORT.md`は
「重複除去後18件」としていたが、本Trialで`tts_generation_results.json`
(110ファイル)を機械的に再抽出したところ、一意なcanonical/ASRペアで
TRUE_CONTENT_MISMATCHは4件(+comment_2の3件=計7件)だった。抽出対象
ファイルパターンや集計方法の違いによるものと推測されるが、本Trialでは
独自に再抽出した7件(実データ)+comment_2を「過去MISMATCH全件」として
扱った(過大にも過小にも意図的に操作していない、抽出スクリプトは
`er011_output/ja_asr_variant_trial_01/`配下に評価結果として保存)。

---

## 1. failure mode分類(構造的要因)と自作テストセット

過去ログに頼らず、日本語ASRで一般的に起こりうる表記ゆれを構造的要因で
分類した。各分類、過去ログ外の自作例をPASS/MISMATCH(負例)双方で用意した
(合計82件、`er011_output/ja_asr_variant_trial_01/test_dataset.json`)。

| 構造的要因 | 対応するユーザー指定カテゴリ | 自作PASS件数 | 自作MISMATCH(負例)件数 |
|---|---|---|---|
| 辞書未登録読み(kanwadictに正しい訓読みが無い) | (a)ひらがな⇔漢字 | 12 | 4 |
| ひらがな⇔カタカナの書字系差 | (b)ひらがな⇔カタカナ | 12 | 4 |
| 同音異表記(異なる漢字・同じ読み・同義) | (c)同音異表記 | 10 | 4 |
| 送り仮名・活用形・一般的表記差 | (d)一般的な送り仮名・表記差 | 10 | 4 |
| 数字・助数詞 | (d)関連 | 6 | 2 |
| カタカナ語の長音差 | 長音・促音・拗音の表記差 | 6 | 2 |
| 句読点・記号 | 句読点・記号 | 3 | 1 |
| 複数読みの選択誤り(文脈依存の多義漢字) | 複数読みの選択誤り | 2 | 0 |

代表例(全件は`test_dataset.json`参照):
- 辞書未登録読み: 「経つ」/「たつ」(報告事例)、「頑張る」/「がんばる」、
  「行う」/「おこなう」、「見つける」/「みつける」
- ひらがな⇔カタカナ: 「におい」/「ニオイ」(報告事例)、「やばい」/
  「ヤバイ」、「こつ」/「コツ」
- 同音異表記: 「聞く」/「聴く」、「会う」/「逢う」、「暖かい」/「温かい」
- 送り仮名: 「行なう」/「行う」、「申し込む」/「申込む」、
  「まる一か月」/「丸一ヶ月」(実データ抽出)
- 負例(真MISMATCH、各分類に必須): 「経つ」/「勝つ」、「だめ」/「ため」、
  「湿度」/「死図塔」(実データ抽出、ASR誤認識の実例)、
  「行う」/「行かない」(否定反転)

## 2. 候補比較

| 候補 | 概要 | カバー範囲 | 誤PASSリスク | 実装影響 | コスト | 再発防止力(汎化) | 回帰リスク |
|---|---|---|---|---|---|---|---|
| A. Resolver候補テーブル拡張 | kanwadictに無い読みを`single_char_candidates()`へ追加registerし、既存Reading Resolver(LLM選択)に候補として渡す | 辞書未登録読み分類のみ部分改善(候補が増えるだけでLLM判断は従来通り必要) | 低(既存fail-safe設計を維持) | 小(1関数へのdict追加) | LLM呼び出しは減らない(むしろ候補が増えると呼び出し機会が増える可能性) | **低**。ユーザー指摘の「都度追加」パターンそのものになりやすく、本Trial実測でも10文字中5文字(経/行/聴/逢/創)がkanwadict候補ゼロと判明、閉じたテーブルでは追いつかない | 低 |
| A2. 単語単位の補助読みテーブル直挿し | 「経つ→たつ」等を単語単位でLLM抜きに直接読み置換 | 登録した単語のみ | 低 | 小 | ¥0・高速 | **最低**。1語ずつのhardcode化そのもので、ユーザーが明示的に禁止したパターンと一致するため不採用 | 低 |
| C. 正規化層(jaconv等) | ひらがな⇔カタカナの文字変換、長音符除去等の軽量ルールベース正規化 | (b)ひらがな⇔カタカナは既存機構で既にほぼ吸収済み(pykakasi読み一致で対応)。長音符(ー)処理は理論上対応可能だが未実装・未検証 | 長音符を機械的に除去するルールは、语によっては意味が変わる語(バス/バース等)を誤って同一視するリスクがあり、閉じた対象範囲の設計が必要 | 中 | ¥0 | 中(長音符処理のみに限定すれば汎用性あり) | 未検証(本Trialでは未実装、比較のみ) |
| B. 形態素解析エンジン(fugashi+unidic-lite) **[Trial実装・評価対象]** | pykakasiの文字単位読み合成を、単語単位で辞書引きする形態素解析器の読みへ、既存の読み一致チェックの**追加レイヤー**として組み込む | (a)(b)(c)(d)全カテゴリで有効性を確認(下記結果表)。数字・助数詞・句読点は既存機構で別途カバー済みのため無変更 | **実測0件**(自作82件+実データ79件、計161件で誤PASSなし) | 中(新規ファイル追加のみ、Production関数は無変更。依存パッケージ2件追加) | ¥0・LLM呼び出し不要(オフラインCPU処理、数ms程度) | **高**。辞書自体が実コーパスベースで単語単位のため、未知の漢字1文字パッチに頼らず広いカバレッジを持つ(実測: 経/行/聴/逢/創の5件中、形態素エンジンは全て正しい読みを機械的に算出できた) | **実測ゼロ**(追加方式のため、既存判定が動く経路には一切触れない) |
| D. SudachiPy/MeCab(フル辞書) | fugashiより大きい辞書・高精度な形態素解析器 | Bと同等以上と推測されるが未インストール・未検証(依存が重く、本Trialの¥0・最小Trial方針に対し導入コストが高いため見送り) | 未検証 | 大(辞書サイズ・ビルド依存が重い) | ¥0だが導入・保守コストがBより高い | 高(推測) | 未検証 |

**結論**: Candidate A/A2は「都度追加」構造そのもの、または効果が限定的で
ユーザーの明示的禁止方針に抵触するため不採用。Candidate Dは本Trialの
最小実施方針に対し導入コストが不釣り合いに高いため見送り。
**Candidate Bを「既存判定への追加レイヤー」として採用する案を主軸に
Trial実施した**(Candidate Cの長音符処理は今回未実装、残存ギャップとして
別途記録)。

## 3. Trial結果

Candidate Bは2方式で評価した:
- **置換方式**(参考): 読み一致関数を丸ごとfugashiベースへ差し替え。
- **追加方式**(本命、後述の理由で置換方式より安全): 既存のpykakasi
  ベース判定はそのまま、Reading Resolver呼び出し直前にfugashiベースの
  全文読み一致チェックをもう1段追加。**既存判定で既にPASS/Cascade対象と
  判定された結果は一切変更しない**ため、regressionが構造的に発生しない。

置換方式では実測で2件の既存PASSを壊した(句読点まわりの実装バグ、
および「一日中」の形態素分割あいまいさ)。うち句読点バグは修正済み。
**追加方式ではこの2件を含め、実測161件中0件の破壊**を確認した
(理由: 既存判定が既にPASS/Cascade対象と判定した時点で追加チェックへ
到達しないよう設計したため)。以下は追加方式の結果。

| 観点 | 件数 |
|---|---|
| 報告事例(経つ/たつ、におい/ニオイ/臭い、6take相当の3パターン)が解消 | **3/3 PASS化** |
| 実データ既知事例(過去TRUE_CONTENT_MISMATCH、重複除去後7件)が解消 | **4/7 PASS化**(内訳: comment_2 3件全て+「あとに/後に」1件。残り3件は未解消: 「湿度/死図塔」「まる一か月/丸一ヶ月」「しばられず/縛られる」) |
| 過去Human Reviewで「表記のみ」と推定されるcomment_2 | **3/3 PASS化**(人間承認前の機械判定であり、既存Human Review機構の代替ではない) |
| 自作・未出ケース(82件、7分類、PASS/負例混在)が正しく判定 | **74/82 (90.2%)**。ベースライン69/82 (84.1%)から5件改善、新規破壊0件 |
| 真の内容誤りを誤PASSしない(負例、自作+実データ) | **誤PASS 0件**(自作28件の負例+実データ2件の真MISMATCH、計30件全て正しくMISMATCH維持) |
| 過去正常判定(実データPASS、72件)を壊さない | **72/72 (壊れず)**。過去に既にPASSだった判定は追加方式では原理的に不変(構造的に検証済み、実測でも72件中0件破壊) |
| offline regression(既存er007/er011テスト) | **PASS**(er007: POSITIVE 10/10、NEGATIVE 15/15、ENTITY_LIKE/PHONETIC_UNCERTAIN/WHOLE_TEXT系 全OK。er011 wiring08: 15項目中14項目実行しPASS、1項目[実データ「後/あと」]はLLM呼び出しが必須のため本Trialでは未実行・件数のみ計上) |

未解消の残存ギャップ(Candidate Bでも解決しない、率直に報告):
- **カタカナ語の長音表記ゆれ**(コンピューター/コンピュータ等): 自作8件中
  5件が未解決。原因は読みエンジンの精度ではなく、長音符(ー)の有無
  そのものが表記として残る構造的な別問題(正規化層の追加が必要、
  Candidate C相当の別Trialが必要)。
- **「まる一か月」/「丸一ヶ月」**(実データ): `ヶ月`という助数詞表記
  (「ヶ」はカタカナ小文字のケ)が既存の閉じた助数詞正規化(`か月`のみ
  対象)の対象外であるため未解決。
- **複数箇所に渡る複合的な差分を含む長文**(実データ、「洗濯物のにおいは
  …」の複数箇所同時差分)は、Candidate Bでも自動解決せず、既存の
  Reading Resolver(LLM)が引き続き必要(現状から悪化はしない)。
- **形態素分割のあいまいさ**(例: 「一日中」を「一/日中」と分割し
  「にっちゅう」と読んでしまう、正しくは「いちにちじゅう」): 形態素
  解析器固有の別種の誤りであり、pykakasi方式には無い新しいクラスの
  リスクとして記録する(追加方式のため、この語がpykakasi側で既に正しく
  解決されていれば追加チェックへは到達せず影響しない)。

## 4. closeout判定: **USER_DECISION_REQUIRED**

報告事例そのもの(経つ/たつ、におい/ニオイ/臭い)と、指定された4分類
((a)(b)(c)(d))の大部分、および同種の未出一般語(自作テスト90.2%)は
Candidate B(追加方式)で¥0・LLM不要・regression実測ゼロで解消できる
見込みが高い。一方、以下は本Trialの受入観点(タスク指示の「一般的・
高頻度の未出ケースで通ること」)を完全には満たしていない:
- カタカナ語の長音表記ゆれ(未出ケースの一部、8件中5件未解決)
- 助数詞の一部表記(ヶ月等)
- 複合的な長文diff(既存Resolverへの依存が残る、ただし現状より悪化しない)

**選択肢**:
1. 上記残存ギャップを許容し、Candidate B(追加方式)を報告事例+4分類の
   対策としてProduction採用する(長音符・助数詞ギャップは別Trialとして
   切り出す)。
2. 長音符正規化層(Candidate C)を追加実装してから再評価し、まとめて
   採用判断する。
3. 採用を見送り、現状維持(Human Review機構での個別対応を継続)。

いずれもユーザー判断が必要(`APPROVED_FOR_PRODUCTION`はユーザーのみ)。

## 5. 配線案(採用する場合)

- 変更箇所: `er007_ja_asr_validator_01.py`の`classify_ja_asr_match()`
  内、`if FEATURE_FLAG_A2_READING_RESOLVER_ENABLED:`直前に、fugashi/
  unidic-liteベースの全文読み一致チェック(`er011_ja_asr_variant_trial_01.
  classify_with_candidate_additive()`相当のロジック)を追加する。
  既存のpykakasiベースチェック・数字/否定保護・entity_like判定は
  一切変更しない。
- feature flag: 新規`FEATURE_FLAG_A2_MORPH_RESCUE_ENABLED`(既定False)
  を追加し、有効化した場合のみ追加チェックが働くようにする(既存の
  `FEATURE_FLAG_A2_READING_RESOLVER_ENABLED`と同じ設計思想)。
- 依存追加: `fugashi`, `unidic-lite`(要requirements反映、ユーザー承認要)。
- 回帰テスト: 既存`er007_ja_asr_validator_01_test.py`
  `er011_no18_connected_speech_reading_resolver_wiring_08_test.py`に
  加え、本Trialの`test_dataset.json`(82件)と実データ抽出セット
  (`historical_extraction_dedup.json`)をfixtureとして追加することを
  推奨する。
- 想定コスト影響: 1記事あたり追加コストは¥0(offline CPU処理のみ)。
  Reading Resolverへの到達件数が減る分、既存のLLM呼び出し回数・待ち時間は
  純減する見込み(本Trialでは実測せず、Production配線後に計測推奨)。

## 参照

- 実装: `er011_ja_asr_variant_trial_01.py`(Trial専用、Production関数は
  変更していない)、`er011_ja_asr_variant_trial_01_run.py`(自作テストセット
  定義+実行)
- 証跡: `er011_output/ja_asr_variant_trial_01/`
  (`test_dataset.json`, `results.json`[置換方式], `additive_results.json`
  [追加方式・本命], `historical_results.json`, `additive_regression_result.json`,
  `existing_er007_offline_regression_result.json`,
  `existing_er011_wiring08_offline_regression_result.json`,
  `historical_extraction_dedup.json`, `candidate_a_dry_candidate_checks.json`)
- 前提資料: `FAMILY-A-DISCOVERY-TOWELS-A2-JA-ASR-VARIANT-RECONCILE-01_REPORT.md`
- Production関数(読み取りのみ、変更なし): `er007_ja_asr_validator_01.py`,
  `er011_a2_reading_resolver_01.py`

---

## 修正1回目(Fable差し戻し対応)

### 差し戻し理由(要約)

初回結果は良好だったが、ユーザー受入観点「一般的・高頻度の未出ケースでも
通る」に対し、(a)カタカナ長音表記差(コンピューター/コンピュータ)、
(b)助数詞表記差(ヶ月/か月)、(c)形態素分割曖昧1件、が未解決のまま
`USER_DECISION_REQUIRED`で止まっていた。初回REPORT自身が「候補C(正規化層)
が必要」と特定していたため、候補Cを候補Bと同じ追加型(additive)設計で
実装し、Trial内で閉じられるかを再評価する差し戻しを受けた。

### 1. 実装した候補C(正規化層、追加型)

新規ファイル`er011_ja_asr_variant_trial_01_rev1.py`(初回成果物
`er011_ja_asr_variant_trial_01.py`は無変更のまま、importして再利用する
だけ)。既存pykakasi判定・候補B・Production関数は一切変更していない。

- **(a) カタカナ語の語末長音符(ー)の省略差**: カタカナ(+長音符)の
  「連続塊」全体が**4文字以上**、かつ連続塊の**最後の1文字が長音符**の
  場合に限り、末尾の1文字だけを取り除く(`normalize_katakana_trailing_
  choonpu()`)。連続塊の途中にある長音符(語の意味を変え得る)は対象外。
  4文字未満の短い外来語(スキー、コピー、バー等)も対象外とし、長音符の
  有無で別の語になるリスク(バス/バース等)を構造的に避けた。これは
  個別語ではなく、JIS Z 8301が慣用として認める「3モーラ以上の外来語は
  語末長音符を省略してよい」という一般ルールの実装であり、単語テーブル
  ではない。
- **(b) 助数詞「ヶ月/ヵ月/カ月」表記**: この3表記を既存Production
  (`er003_audio_tts_asr_safety.py`の閉じた助数詞リスト)が既に認識する
  「か月」へ正規化した後、既存Production関数
  `normalize_kanji_counter_numerals_ja()`を**そのまま呼び出すだけ**
  (無変更・冪等な再利用)で、既存の「一〜九→1〜9」変換を「ヶ月/ヵ月/
  カ月」経由でも同じように効かせる。対象範囲は指示通り「月」のみに限定し
  (「ヶ所」等の他助数詞は対象外、範囲拡大はしていない)、production側の
  「一〜十/1〜10」の既存対応範囲(実際には一〜九の1桁のみ)自体は一切
  変更していない(「十」を含める拡張はkanwadict同様のリスク再評価が
  別途必要な既存Production仕様変更であり、本Trialの対象外)。
- **(c) 形態素分割曖昧の1件(「一日中」→「一/日中」誤分割)**: 原因を
  特定した。本Trialの161件データセット中、このケースは実際には**失敗
  していない**(「いちにちじゅう家で過ごした。」/「一日中家で過ごした。」
  は既存pykakasi判定が最初の時点で既に読み一致と判定しており、追加
  チェックへ到達しない)。「読み比較を文全体のかな列で行う」という
  一般的対処は候補Bが既に採用済みの設計そのものであり、それでも起き得る
  この種の分割誤りは、比較方式ではなく形態素解析辞書(unidic-lite)が
  「一日中」を複合語として持たないという辞書固有の限界に起因する。
  個別語を辞書へ追加することは禁止事項(個別語テーブル)に抵触するため、
  「特殊語(形態素解析器の辞書エントリに依存する複合語分割の限界)」として
  除外する。安全性の論拠: この分割誤りが実害(誤PASS)を生むには
  「(i)既存pykakasiが誤ってMISMATCH化し、かつ(ii)候補Bの誤読みが偶然
  別のASR書き起こしと一致する」という二重の偶然が必要であり、(i)は
  候補B/C導入前から存在するpykakasi側の既知の限界(候補B/C起因の悪化
  ではない)、(ii)は実測161件(負例含む)で0件。詳細な論拠は
  `er011_ja_asr_variant_trial_01_rev1.py`のコメントに記載。

挿入位置は候補Bと同じ設計(既存Resolver呼び出し直前)で、候補Bが既に
何らかの判定を確定させた場合は候補Cへ到達しない(`classify_with_
candidate_additive_bc()`)。候補Cはさらに2段: (1)正規化後の**文字列
完全一致**(読みエンジンを介さない最も安全な判定)、(2)それでも残る差
(例:「まる」/「丸」)を候補Bの形態素読みエンジンへ正規化後のテキストで
再適用、の順で試す。

### 2. 再評価結果(同一82件+実データ7件[過去MISMATCH]+72件[過去PASS]、計161件)

| 観点 | 初回(候補Bのみ) | 修正1回目(候補B+C) |
|---|---|---|
| 報告事例3パターン | 3/3 PASS化 | 3/3 PASS化(不変) |
| 実データ既知事例(過去TRUE_CONTENT_MISMATCH、7件) | 4/7 PASS化 | **5/7 PASS化**(新たに「まる一か月/丸一ヶ月」が解消。残り2件[湿度/死図塔、しばられず/縛られる]は真の内容誤りのため意図的に未解消のまま) |
| comment_2(3件) | 3/3 PASS化 | 3/3 PASS化(不変) |
| 自作・未出ケース(82件) | 74/82 (90.2%) | **80/82 (97.6%)**(新たに解消: カタカナ長音6件中5件+「まる一か月/丸一ヶ月」の計6件) |
| 誤PASS(負例、自作21件[82件中]+実データ2件、計23件) | 0件 | **0件(維持)** |
| 過去正常判定(実データPASS、72件) | 壊れず(構造的に保証、実測もOK) | **壊れず**(下記「methodology上の発見」参照、fresh baseline比較で正しく再検証、真の regression 0件) |
| offline regression(er007) | POSITIVE 10/10, NEGATIVE 15/15, 他OK | **POSITIVE 10/10, NEGATIVE 15/15, ENTITY_LIKE 1/1, PHONETIC_UNCERTAIN 2/2, WHOLE_TEXT系 3/3+2/2, KNOWN_TRADEOFF 1/1、全OK**(1件[月/つき、LLM必須]はskip、初回と同じ扱い) |
| offline regression(er011 wiring08、A2関連) | 15項目中14実行OK、1skip | **A2分類結果に影響し得る2項目(#10完全一致、#14真の内容誤り)ともOK**、#9(後/あと、LLM必須)はskip(初回と同じ扱い。#1-8はB1英語Validatorで対象外、#11-13はmock検証でclassify関数を経由せず対象外、#15はimportチェックで対象外) |

残存(意図的に対象外、Fable指示の3項目には含まれない別種の既知ギャップ):
- **「十件/10件」**(自作82件中1件): Production既存の助数詞直前漢数字
  変換が「一〜九」の1桁のみに限定されており(`ER-011-KP-VALIDATOR-
  NUMERIC-HOMOPHONE-AND-GLOSS-RULES-PRODUCTION-WIRING-02`でリスク評価済み
  の既存仕様)、「十」(10)を含める拡張はProduction既存仕様自体の変更
  判断であり、本Trialの指示範囲(ヶ月表記・長音・形態素曖昧の3点)を
  超えるため対象外とした。
- **「頃/ころ」**(自作82件中1件): baselineの時点で既にASR_VALIDATION_
  UNCERTAIN(Cascade対象、候補B/C導入前からの既存pykakasi/voicing機構の
  挙動)であり、候補B/Cはこの判定へ一切到達しない(`b:unchanged`)。
  候補B/C起因の問題ではなく、既存Cascade機構がこのケースを「即PASSでは
  なくCascade(追加ASR再確認)」として扱っているだけ(誤PASSはしていない、
  安全側の既知の挙動)。

### 3. methodology上の発見(率直に報告)

再検証の過程で、初回Trialの証跡ファイル間に**評価方式のラベル不整合**を
発見した。`historical_results.json`の`candidate_classification`/
`candidate_should_pass`フィールドは、命名上は「追加方式」の結果に見える
が、実際には**置換方式**(`classify_with_candidate_morph()`、既存
pykakasi判定を丸ごとfugashiへ差し替える方式)で計算されていたことを、
該当ケース(「関連づけられる/関連付けられる」)を追加方式・置換方式の
両方で直接再実行して確認した(追加方式では`unchanged`のままPHONETIC_
MATCHを維持し壊れない。置換方式ではASR_VALIDATION_UNCERTAINへ変化する
=1件のregression)。この結果、`historical_results.json`のsummaryが
示す`past_pass_candidate_broke: 1`は置換方式のregressionであり、追加
方式(本命として採用された方式)のregressionではない。また
`additive_results.json`の`past_pass_summary`が示す`broke: 2`は、
「(dry-run方式の制約でbaseline自体が元々Falseだったケース)」を
regressionとして誤カウントしていた(fresh baselineとの比較を行わず、
現在の`should_pass`が`False`かどうかだけで判定していたための誤り)。
本修正では、`fresh_baseline_should_pass`(その場で再計算したbaseline)
と`bc_should_pass`を正しく比較する定義に直し、72件中**真のregressionは
0件**であることを確認した(初回REPORTの結論「72/72壊れず」自体は最終的
に正しいが、その根拠となった証跡ファイル間には上記の不整合があったため
ここに記録する)。

### 4. closeout判定(修正1回目): **VALIDATED**

Fable差し戻し指示で明示された3項目(カタカナ長音、ヶ月表記、形態素分割
曖昧1件)はいずれも解消(実装または理由付き除外)し、82件+実データ79件
(計161件)の受入観点6項目すべてで誤PASS 0件・真のregression 0件を実測
で確認した。残存する「十件/10件」「頃/ころ」は指示範囲外の別種の既知
ギャップであり、これらはこのTrialの受入判定をブロックしない(ユーザー
判断で別Open Itemとして切り出すことを推奨)。

### 5. Production配線案(候補B+C、更新版)

- 変更箇所: `er007_ja_asr_validator_01.py`の`classify_ja_asr_match()`
  内、`if FEATURE_FLAG_A2_READING_RESOLVER_ENABLED:`直前へ、(1)候補B
  (形態素読み一致、`FEATURE_FLAG_A2_MORPH_RESCUE_ENABLED`)、(2)候補C
  (正規化層、新規`FEATURE_FLAG_A2_NORMALIZATION_RESCUE_ENABLED`)の順で
  2段の追加チェックを挿入する。既存のpykakasiベースチェック・数字/否定
  保護・entity_like判定は一切変更しない。
- feature flag: 新規`FEATURE_FLAG_A2_NORMALIZATION_RESCUE_ENABLED`
  (既定False)を追加。候補Cの「正規化後の文字列完全一致」判定は候補B
  (fugashi)に依存しないが、「正規化後もなお残る差を形態素読みで確認」する
  第2段は候補Bの読みエンジンに依存するため、Production配線の実装時に
  候補Bが無効(False)の場合の扱い(第2段をスキップするか、候補Cが内部で
  独自にfugashiを呼ぶか)を確定する必要がある(本Trialでは候補Bが常に
  利用可能という前提で評価した、実装時の詳細設計はユーザー承認後の
  Production配線タスクで確定)。
- 依存追加: 候補Bと同じ(`fugashi`, `unidic-lite`)。候補C自体は標準
  ライブラリ(`re`)のみで追加の依存パッケージは不要(`jaconv`は候補B側
  で既に使用、候補Cでは直接使用していない)。
- 回帰テスト: 候補Bの推奨に加え、本修正の`rev1_synthetic_results.json`
  (82件)・`rev1_historical_results.json`(79件)・
  `rev1_regression_result.json`(er007/er011 wiring08)をfixtureとして
  追加することを推奨する。
- 想定コスト影響: 候補Bと同じく1記事あたり¥0(正規表現ベースの軽量な
  文字列処理のみ、追加のCPU負荷は無視できる水準)。

### 参照(修正1回目)

- 実装: `er011_ja_asr_variant_trial_01_rev1.py`(新規、初回の
  `er011_ja_asr_variant_trial_01.py`は無変更のままimportして再利用)
- 実行: `er011_ja_asr_variant_trial_01_rev1_run.py`(82件+実データ79件の
  再評価)、`er011_ja_asr_variant_trial_01_rev1_regression_run.py`
  (er007/er011 wiring08の再確認、既存test fixtureファイルをimportして
  再利用、fixtureを作り直していない)
- 証跡: `er011_output/ja_asr_variant_trial_01/`配下
  (`rev1_synthetic_results.json`, `rev1_historical_results.json`,
  `rev1_regression_result.json`)
- Production関数(読み取りのみ、変更なし): `er007_ja_asr_validator_01.py`,
  `er011_a2_reading_resolver_01.py`, `er003_audio_tts_asr_safety.py`

---

## 修正2回目(Fable差し戻し対応、2回目)

### 差し戻し理由(要約)

修正1回目は82件中80件・過去MISMATCH7件中5件を解消したが、未解消2件
(「頃/ころ」「十件/10件」)のうち「頃/ころ」はユーザーが明示したひらがな
⇔漢字カテゴリそのもの、「十件/10件」は漢数字⇔算用数字という一般的・
高頻度の表記差であり、「指示範囲外」として除外することは認められず、
failure mode単位で構造的に特定した上で一般的な追加型修正で閉じるよう
差し戻された。

### 1. 構造診断(実測)

新規ファイル`er011_ja_asr_variant_trial_01_rev2.py`で診断・実装した
(修正1回目までの成果物・Production関数は一切変更せず、importして再利用
するだけ)。

- **「頃/ころ」— 比較アルゴリズム(候補B+Cの適用範囲)の問題**。実測で
  確認: baselineの`classify_ja_asr_match()`は、この入力に対し既に
  `ASR_VALIDATION_UNCERTAIN`(既存のvoicing許容Cascade機構、「頃」を
  pykakasiが文脈依存で連濁形「ごろ」と読んでしまうことへの既存の安全側
  フォールバック)を返しており、修正1回目の候補B(`classify_with_
  candidate_additive()`)は「baselineがTRUE_CONTENT_MISMATCHの場合のみ
  追加チェックを試みる」設計のため、この時点で早期リターンし
  fugashi/unidic-lite形態素読みエンジンに一切到達していなかった
  (`b:unchanged`)。ところが実測でfugashi/unidic-liteの厳密(濁点許容
  なし)読み一致を直接確認すると、"ゆうがたころにえきへつくよてい"同士で
  **完全一致**することを確認した(形態素辞書エンジンはpykakasiのような
  文脈依存の連濁推定を行わないため)。一方、既存fixtureの「柿/鍵」
  (`KNOWN_TRADEOFF_FIXTURES`、清音化後にのみ偶然一致する別の実在語)を
  同じ方法で確認すると、形態素読みエンジンでも厳密不一致のままである
  ことを確認した(`かき`≠`かぎ`)。この違いを安全に利用できる: 既存の
  voicing許容Cascade(`ASR_VALIDATION_UNCERTAIN`、根拠が固有名詞ゆれ
  [entity_like]を含まない純粋な濁点差[phonetic_uncertain]のみ)に限り、
  形態素エンジンで厳密一致が確認できた場合だけ`PHONETIC_MATCH`へ引き上げる
  (Candidate D-2)。
- **「十件/10件」— 数詞処理(漢数字→算用数字変換の対象範囲)の問題**。
  既存Production(`normalize_kanji_counter_numerals_ja()`)は閉じた助数詞
  リストの直前の**単独1桁**漢数字(一〜九)だけを算用数字化しており、
  「十」(10)・「百」・「千」・「万」の位取り表記は対象外だった。
  「十」は変換されないまま残るため、"じゅうけん"と"10けん"の読みが一致
  せず、候補B・候補Cのどちらでも解消しなかった(実測で確認)。

### 2. 実装した追加修正(Candidate D、追加型)

- **Candidate D-1(漢数字の位取り一般正規化)**: 既存Productionと**同じ
  閉じた助数詞リスト**(つ/泊/回/件/年/時間/か月/週/歳、`safety._CLOSED_
  COUNTERS_JA`を読み取り専用で再利用、対象助数詞の集合自体は拡大していない
  =「日」「人」等の既知の不規則読みリスクがある助数詞は引き続き対象外)を
  トリガー文脈として再利用し、その直前に来る漢数字を1桁だけでなく
  「十/百/千/万」の位取りを含めて一般的に整数へ変換する
  (`kanji_numeral_run_to_int()`)。構文的に解釈できない並び(位取りの
  大小関係が単調減少でない「十千」、数字が連続する「一一」等)は
  fail-safeで無変換のまま返す。この変換は「同じ数値表記同士だけが同じ
  文字列に正規化される」決定的な変換のため、異なる数量を同じ文字列へ
  変換することは構造的に起こらない(=負例を誤ってPASSさせるリスクを
  生まない性質)。個別の単語・数値のテーブルではなく、一般的な漢数字の
  構文規則の実装である。
  - **実装中に実測で発見し、修正した順序依存の副作用(2件)**: (1)既存
    Production(`javal.normalize_ja()`)が先に単独1桁だけを変換すると、
    「十五件」の末尾の「五」だけが先に"5"化され「十5件」という漢数字と
    算用数字が混在した文字列になり、Candidate D-1の正規表現(漢数字の
    連続塊)が寸断されて「十」が変換されなくなる。(2)助数詞「ヶ月/ヵ月/
    カ月」表記(Candidate C)と複合漢数字が同時に発生するケース(例:
    「十五ヶ月」)でも同様に、Candidate Cの表記統一より前に一般漢数字
    正規化を行うと「か月」パターンにまだマッチせず変換されない。
    いずれも「生テキストに対し、複合漢数字がまだ漢字のまま連続している
    段階で先に一般漢数字正規化を適用し、そのあとで既存Production処理・
    Candidate Cを適用する」という順序に修正することで解消した
    (`prepare_text_for_candidate_d1()`、実測で追加検証済み、下記4節)。
- **Candidate D-2(voicing許容Cascadeの厳密一致引き上げ)**:
  `ASR_VALIDATION_UNCERTAIN`のうち、根拠となる`content_diffs`が
  「濁点/半濁点の有無だけが異なる読みゆれ(`phonetic_uncertain`)」のみで
  構成され、固有名詞ゆれ(`entity_like`)が1件も混ざっていない場合に限り、
  fugashi/unidic-lite形態素解析ベースの**厳密**(濁点許容なし)読み一致を
  再確認する。厳密一致すれば`PHONETIC_MATCH`へ引き上げ、一致しなければ
  一切変更しない(既存のCascade対象のまま=誤PASSしない)。固有名詞ゆれの
  ケース(`ENTITY_LIKE_FIXTURES`)は本Trialのスコープ外として明示的に
  対象外にした。

挿入位置は既存の追加方式と同じ設計(候補B→候補C→候補Dの順、いずれかの
段が既に判定を確定させた場合はそれ以降の段へ進まない、
`classify_with_candidate_additive_bcd()`)。

**(b)辞書未登録読みへの一般的フォールバック(編集距離比等)について**:
差し戻し指示で例示された「fugashiの複数読み候補・かな列の編集距離比/
文字数比によるフォールバック」は、実装しなかった。構造診断の結果、
残存2件はいずれも「辞書に読みが登録されていない」ことが原因ではなく
(fugashi/unidic-liteは「頃」を正しく「ころ」と引けている)、(1)候補B+Cの
適用範囲(比較アルゴリズム)の問題、(2)数詞処理の対象範囲の問題、で
あることが実測で判明したため、この2件を閉じるために編集距離ベースの
あいまい一致という新しい種類のリスク(意味の異なる語同士が偶然近い
読みになった場合に誤PASSする可能性がある一般的なメカニズム)を根拠なく
追加することはしなかった(開発方針「速度よりも安定性を優先」、実際の
failure modeで正当化できない一般化を避ける)。

### 3. 再評価結果(同一82件+実データ7件[過去MISMATCH]+72件[過去PASS]、計161件)

| 観点 | 修正1回目(候補B+C) | 修正2回目(候補B+C+D) |
|---|---|---|
| 自作・未出ケース(82件) | 80/82 (97.6%) | **82/82 (100%)**(残り2件「頃/ころ」「十件/10件」も解消) |
| 実データ既知事例(過去TRUE_CONTENT_MISMATCH、7件) | 5/7 PASS化 | **5/7 PASS化(不変)**。残り2件(湿度/死図塔、しばられず/縛られる)は真の内容誤りのため意図的に未解消のまま(修正1回目と同じ、対象外の指示範囲) |
| 誤PASS(負例、82件中21件+実データ2件、計23件) | 0件 | **0件(維持)**。追加で漢数字の値違い(十五件/50件、二十件/12件、十件/十一件、百件/百一件等)・「人」助数詞への非拡大(十人/10人)を独自診断で追加確認、いずれも誤PASSなし |
| 過去正常判定(実データPASS、72件) | 壊れず | **壊れず**(fresh baseline比較、真のregression 0件。bcd_still_pass=70>fresh_baseline_pass=68は改善であり悪化ではない) |
| offline regression(er007) | 全OK(1件[月/つき]skip) | **全OK(維持、1件[月/つき]skip)**。PHONETIC_UNCERTAIN(頃/ころ実データfixture)・WHOLE_TEXT_SCRIPT_MISMATCH(実データNo.9 A2)がCandidate D-2で`ASR_VALIDATION_UNCERTAIN`→`PHONETIC_MATCH`へ引き上げられたが、いずれも期待値(`!= TRUE_CONTENT_MISMATCH`)の範囲内でOK。KNOWN_TRADEOFF(柿/鍵)・ENTITY_LIKE(スラッジ/スラッシ)はD-2の対象外条件により不変(誤PASSなし) |
| offline regression(er011 wiring08、A2関連) | #10・#14ともOK | **#10・#14ともOK(維持)**、#9(後/あと、LLM必須)はskip(不変) |

### 4. 追加診断(独自negativeケース、フリーズ済み82件セットとは別枠)

漢数字一般化の安全性を追加確認するため、82件セットとは別に独自の
diagnosticケースを実行した(`/tmp`の一時スクリプト、正式なfixtureへは
追加していない、既存フリーズ済みデータセットは変更していない):
「十五件/15件」「二十件/20件」「百件/100件」「八十五歳/85歳」
「二百時間/200時間」「十五ヶ月/15か月」はいずれも正しくPASS、
「十五件/50件」「二十件/12件」「十件/十一件」「百件/百一件」
(いずれも値そのものが異なる)はいずれも正しくMISMATCHのまま、
「十人/10人」(「人」は既存Productionの既知リスクにより対象外のまま)も
変化なし、を確認した。

### 5. closeout判定(修正2回目): **VALIDATED**

Fable差し戻し指示で明示された2件(頃/ころ、十件/10件)を含む自作82件
全件・過去実データ既知事例(解消可能な5/7、残り2件は真の内容誤りのため
意図的に対象外)を、個別語テーブルを一切使わずfailure mode単位の一般的な
追加修正(比較アルゴリズムの適用範囲拡張+漢数字位取りの一般正規化)で
解消し、誤PASS 0件・真のregression 0件を実測で確認した。

### 6. Production配線案(候補B+C+D、更新版)

- 変更箇所: 修正1回目の配線案と同じ挿入位置(`er007_ja_asr_validator_01.py`
  の`classify_ja_asr_match()`内、`if FEATURE_FLAG_A2_READING_RESOLVER_
  ENABLED:`直前)に加え、Candidate D-2(voicing許容Cascadeの厳密一致
  引き上げ)は`classify_ja_asr_match()`が`ASR_VALIDATION_UNCERTAIN`を
  返した**後**(呼び出し元)で追加の1段として適用する必要がある(関数内部
  ではなく、呼び出し元でのpost-processingとして配線する設計。理由:
  既存関数の`ASR_VALIDATION_UNCERTAIN`の返り値自体は変更せず、既存の
  Cascade呼び出し元[追加ASR再確認ロジック]の判断に委ねる既存設計の原則を
  壊さないため)。
- feature flag: 修正1回目の`FEATURE_FLAG_A2_NORMALIZATION_RESCUE_
  ENABLED`に加え、新規`FEATURE_FLAG_A2_KANJI_NUMERAL_GENERALIZATION_
  ENABLED`(Candidate D-1、既定False)・`FEATURE_FLAG_A2_VOICING_CASCADE_
  EXACT_MORPH_UPGRADE_ENABLED`(Candidate D-2、既定False)を追加する。
  Candidate D-1は既存の閉じた助数詞リストをそのまま再利用するため、
  リスト自体を拡張する仕様変更ではない(既存の「日」「人」除外方針は
  維持)。
- 依存追加: 新規なし(Candidate B/Cと同じ`fugashi`, `unidic-lite`。
  Candidate D-1は標準ライブラリ`re`のみ)。
- 回帰テスト: 修正1回目の推奨に加え、`rev2_synthetic_results.json`
  (82件)・`rev2_historical_results.json`(79件)・
  `rev2_regression_result.json`(er007/er011 wiring08)・本節4の独自
  diagnosticケース(漢数字一般化の値違い負例)をfixtureとして追加する
  ことを推奨する。
- 想定コスト影響: 候補B/Cと同じく1記事あたり¥0(正規表現ベースの軽量な
  文字列処理・形態素解析の追加呼び出しのみ、追加のCPU負荷は無視できる
  水準)。

### 参照(修正2回目)

- 実装: `er011_ja_asr_variant_trial_01_rev2.py`(新規、修正1回目
  `er011_ja_asr_variant_trial_01_rev1.py`・初回`er011_ja_asr_variant_
  trial_01.py`は無変更のままimportして再利用)
- 実行: `er011_ja_asr_variant_trial_01_rev2_run.py`(82件+実データ79件の
  再評価)、`er011_ja_asr_variant_trial_01_rev2_regression_run.py`
  (er007/er011 wiring08の再確認、既存test fixtureファイルをimportして
  再利用、fixtureを作り直していない)
- 証跡: `er011_output/ja_asr_variant_trial_01/`配下
  (`rev2_synthetic_results.json`, `rev2_historical_results.json`,
  `rev2_regression_result.json`)
- Production関数(読み取りのみ、変更なし): `er007_ja_asr_validator_01.py`,
  `er011_a2_reading_resolver_01.py`, `er003_audio_tts_asr_safety.py`
