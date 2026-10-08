【最初に必ず読む: このファイルの扱い】
- あなたが読んでよいファイルは、この1ファイルだけです。この1回の読み込みが、唯一許される道具(ツール)の使用です。
- このファイル以外のファイルを読まない。Grep・Globで探さない。コマンドを実行しない。Webを使わない。リポジトリ内の他のファイル(過去の注記、評価、仕様の他版など)には一切触れない。
- 読んだ後は、道具を一切使わず、下の「依頼文」の指示どおりに返答の本文だけで答える。ファイルを作らない・保存しない。

--------------------------------------------------------------------------------
【依頼文(ここから)】
あなたは「B3注記」の注記者です。下に貼り付けた3つの文書(注記仕様、元のニュース欄、台帳)だけを使って作業します。

作業の約束:
- ファイルを読む、探す、検索する、Webを使うなど、道具(ツール)を使ってはいけません。貼り付けられた文書以外を参照しません。
- 結果はファイルに保存せず、仕様の「6 出力の形式」のとおりに、この返答の本文で返します。前後に説明文を付けません。
- 判断が分かれる場面は、仕様の既定に従い、仕様のとおりに記録します。仕様に書かれていないことは、印を付けない側にします。
- 注記者は A です。記事の識別名(slug)は meta です。
- サイドカーの `slug` には meta、`annotator` には A、`spec_sha256` には 8d145c3d7cb3953ef2d344056e2e9979698fff7d1f60aec7a6b6d922e7cf1e57、`brief_sha256` には 83c29bc213a7c8bd22000e04446dded2dce4c047b9273ae6575e260339fa22e0 を、そのまま書き写します。
- 仕様の「4 台帳に無い記述」にあるSTOPの条件に当てはまるときだけ、`=== STOP ===` の次の行から理由を返します。

【注記仕様】
# B3注記仕様(注記者用)

あなたの仕事は、ニュース記事の元になる「ニュース欄(brief)」に、事実番号と数字の印を機械的な規則で付け足すことです。与えられた台帳(裏付け済みの事実の一覧)に書かれていることだけを根拠にし、判断が分かれる場面は本書の既定に従います。自分の好みや読みやすさで上書きしません。

## 1 入力と出力
入力(依頼文に貼り付けられている3点だけ): (1) 元のニュース欄(brief)、(2) 台帳、(3) 本書。
出力: 依頼文で指定された形式で、(A) 注記版のニュース欄の全文、(B) サイドカー(JSON)、を返します。ファイルは作りません。

注記版の絶対規則: 元のニュース欄に、次の3種類の印と、定義済みの改行の挿入を**付け足すだけ**です。削除・言い換え・語順の変更・句読点の変更・空白の変更は禁止です。
- 印は `【事実N】` `【中核数値】` `【周辺数値】` の3つだけ。他の【】は使いません。
- 定義済みの改行の挿入は、「`## Selected Facts` 節の中で、文末の `。` の直後に改行と `- ` を入れる」ことと、「節の先頭の行(または `。` と改行の直後)の行頭に `- ` を入れる」ことだけです。どちらも直後に必ず `【事実N】` が続きます。

## 2 【事実N】の付け方
- 単位は、台帳の事実ID(例 ZZ-001)の境界です。ニュース欄の `## Selected Facts` 節の1項目(箇条書き1行、または段落の文のまとまり)を、既定で1つの事実とします。
- 次の2条件を両方満たすときだけ、文の境目(`。`)で分けます。(S1)項目の中に文が2つ以上ある。(S2)別々の文が、台帳の**別々の事実ID**を主な根拠にしている。
- 分けない場合: 同じ1文の中(主体・行為・対象・時期・数量などで1文を割らない)。1つの台帳の事実に載っている複数の要素。限定する文(「ただし〜」「これは〜を意味しない」「〜とは書かない」「〜ではない」など)は、直前の主張の文と同じ事実に入れます(別の事実にしません)。限定する文が別の台帳IDに由来する場合も、別事実にせず、その台帳IDを `ledger_ids` に追加します。
- 1項目で分けられる事実は最大3つです。4つ以上に分けたくなったら、分けない側を選び、迷いとして記録します。
- ニュース欄がすでに同じ台帳の事実を別の項目で繰り返している場合、それぞれに同じ台帳IDを付けて構いません。1つの文が複数の台帳の事実をまとめている場合は、`ledger_ids` に併記します。
- `## Storyline` の文、Selected Facts 節の中の `Storyline：` で始まる重複行、`素材:` で始まる行には、`【事実N】`を付けません(数字の印は後述の規則で付けます)。
- 番号は、ニュース欄の上から順に 1, 2, 3… と連番にします。欠番・重複・飛びは禁止です。`【事実1,事実2】` のような複合の印は禁止です。
- 台帳IDは注記版の本文に書き足しません(サイドカーに書きます)。ニュース欄にもともと台帳ID(例 `ZZ-001：`)が書かれている場合は、そのまま残し、サイドカーの `ledger_ids` と一致させます。

## 3 数字の印
対象は、算用数字(全角を含む)を含む表記です。漢数字だけの数量(三千人など)は対象外で、印を付けずに `annotation_notes` に記録します。台帳IDの形(`ZZ-001`、`QQ-AB-006` のような英字-数字)は数字として扱わず、印を付けません。

### 3-1 表記(surface)の取り方
- 数字・単位・ヘッジ語を**1つの表記**として、印は表記の末尾に付けます。例: `約3.4％【中核数値】`、`1リットル180円【中核数値】`、`2,300件超【中核数値】`。
- ヘッジ語は表記に含めます。前に付く語: 約・およそ・ほぼ・最大・最大で・少なくとも・数。後ろに付く語: 超・以上・以下・未満・前後・近く。数字に直接つかない語(「一時」「当面」、「を上回って」)は含めません。
- 範囲(`3〜5％`)は1つの表記(kind=range)。日付と時刻が続くもの(`5月8日午前9時30分`)は1つの表記。「翌14日」は数字の部分 `14日` を表記にします。
- 同じ表記は記事の中のどこでも同じ分類(同じ印)にします。短い表記が長い表記の一部になるとき(`2031年9月` が `2031年9月20日` の中に入るとき)は、その場所では長い方に1回だけ印を付けます。

### 3-2 種類(kind)
- `magnitude`: 割合・金額・件数・個数・価格・倍率・順位などの量。
- `date_time`: 年月日・年月・時刻・期間(月が含まれるもの)。
- `range`: 範囲。
- `year`: 年だけ(`2031年`)。常に周辺です。
- `ordinal`: 識別子としての序数(`第9条`、`第12回会合`)。常に周辺です。
- `name_embedded`: 名称の一部の番号(`Hyperion 12`、`Spring 2031`)。常に周辺です。
番号を変えると別のものを指す表記は識別子(ordinal か name_embedded)で、数量ではありません。番号を変えると量や日付が変わる表記は数量です。量か名称内番号か迷ったら、名称内番号を選びます。

### 3-3 概念(concept)
同じ台帳データを指す表記を1つの「概念」にまとめ、サイドカーの `concept` に同じ名前を書きます(例 `2031年9月20日` と `2031年9月` は同じ概念)。次の場合は必ず同じ概念にします: 台帳IDが共通で短い表記が長い表記に含まれる、台帳IDが共通で主数字(3-5)が同じ。同じ概念の中で、`kind` はそろえます。別の概念の表記同士は、この条件に当てはまりません。

### 3-4 台帳ID
その数字が載っている台帳の事実IDを `ledger_ids` に全て書きます(複数可)。台帳にその数字がない場合は空の配列にし、中核にはできません(周辺にして、`unmapped_claims` に type=`new_number` で記録します)。数字の表記は、ニュース欄の表記のままにします(台帳の表記に直しません)。

### 3-5 中核と周辺の決め方(次の手順を機械的に実行)
1. 主数字: 表記の末尾の数字の並びを「主数字」とします(範囲は両端の2つ)。例 `1リットル180円`→180、`約3.4％`→3.4、`3〜5％`→3と5、`2,300件超`→2300。数字は10進数として比べます(`4.00`=`4`=`04`、`1,500`=`1500`)。
2. 適格かどうか(概念の表記のどれか1つが適格なら、その概念が適格):
   - 量(magnitude / range)は、主数字が、紐付く台帳の事実の `numeric_value` 欄の数字に含まれていれば適格です。`(numeric_scope: …)` の中の数字は除いて比べます。台帳に `numeric_value` 欄が1件もない場合に限り、`statement` の中の数字で代わりに比べます。
   - 日付(date_time)は、表記に月があり、台帳の事実の `date_or_period` 欄の**先頭の日付表現**(和文の `2031年9月20日` も、`2031-05-08 09:30 EDT` のような形も)と、表記にある年・月・日(・時刻)が全て一致すれば適格です。表記に無い要素は問いません。年だけ・日だけの表記は不適格です。台帳に `date_or_period` 欄が1件もない場合に限り、`statement` の最初の日付表現で代わりに比べます。Storylineに出るかどうかは条件にしません。
   - year / ordinal / name_embedded は常に不適格です。
3. 数える概念の数 n は、種類が magnitude / date_time / range の概念の総数です。上限は `max(3, min(6, floor(n/2)))` です(n≦7 なら3、n=8〜9 なら4、n=10〜11 なら5、n≧12 なら6)。nが小さいと、適格な概念が全て中核になることもあります(上限は式で決まります)。
4. 適格な概念を次の優先順に並べます: (1)Storylineに出る量(magnitude / range)、(2)それ以外の量、(3)日付。同じ順位の中では、ニュース欄の上から先に出てくる順です。
5. 先頭から上限の数までが中核(`【中核数値】`)、残りの適格な概念と不適格な概念は全て周辺(`【周辺数値】`)です。同じ概念の表記は全て同じ印にします。
6. 上限のために周辺になった適格な概念は、`annotation_notes` に「cap超過で周辺化」と記録します。

## 4 台帳に無い記述
- ニュース欄に書かれているが台帳に無い記述には、印を付けません。サイドカーの `unmapped_claims` に `{"text": "…", "type": "…"}` で記録します。type は次のどれか: `new_fact`(新事実)、`new_number`(新数値)、`new_causal`(新因果)、`generalization`(一般化)、`specification`(具体化)、`qualifier`(限定)。これだけでは作業を止めません。
- 次の2つのときだけは、注記をやめて「STOP」を返します: (i)Storyline(記事の骨格)の主張そのものが台帳に無い。(ii)台帳に無い数字が、中核になりうる量または日付の形でStorylineにある。
- 台帳に書かれていない知識で、事実の根拠や数字の正しさを補ってはいけません。

## 5 迷ったときの既定
迷ったら、必ず `annotation_notes` に `{"where": …, "question": …, "options": […], "chosen": …, "rule": "§番号"}` を記録し、次の既定に従います。
1. 分けるか迷う → 分けない。
2. 中核か周辺か迷う → 周辺(適格であることを台帳で確認できない限り周辺)。
3. 量か名称内番号か迷う → 名称内番号。
4. 紐付く台帳の事実が複数で決められない → 該当するIDを全て `ledger_ids` に書く。
5. ヘッジ語を含めるか迷う → 数字に直接ついていれば含める。
6. 規則に当てはまらない状況 → 記録して、印を付けない側にする。

## 6 出力の形式
次の形式で、そのまま返します(前後に説明文を付けません)。

```
=== ANNOTATED_BRIEF_BEGIN ===
(注記版ニュース欄の全文)
=== ANNOTATED_BRIEF_END ===
=== SIDECAR_JSON_BEGIN ===
(サイドカーJSON)
=== SIDECAR_JSON_END ===
```
STOPの場合は `=== STOP ===` の次の行から理由だけを書きます。

サイドカーJSON:
```
{ "slug": "依頼文で指定された値", "annotator": "A または B(依頼文で指定)",
  "spec_sha256": "依頼文で指定された値をそのまま写す", "brief_sha256": "依頼文で指定された値をそのまま写す",
  "facts":   [ {"n": 1, "ledger_ids": ["ZZ-001"]} ],
  "numbers": [ {"surface": "400円", "kind": "magnitude", "concept": "C1", "ledger_ids": ["ZZ-001"],
                "class": "core または peripheral", "role": "短い説明"} ],
  "unmapped_claims": [ {"text": "…", "type": "new_fact"} ],
  "annotation_notes": [ {"where": "…", "question": "…", "options": ["…"], "chosen": "…", "rule": "§5-2"} ] }
```
本文に出てくる数字の表記は全て `numbers` に1回ずつ載せます(載せない数字は「分類漏れ」になります)。本文に出てこない表記を載せてはいけません。

## 7 出す前の自己点検
- 注記版から3種類の印と定義済みの改行の挿入を取り除くと、元のニュース欄と一字一句同じになるか。
- 【事実N】は上から1,2,3…の連番で、箇条書きの行頭(`- ` の直後)にだけあり、複合の印がないか。
- 本文の算用数字が、全て `numbers` のどれかの表記に含まれているか(台帳IDの形を除く)。
- `numbers` の `class` が、3-5の手順の結果と一致しているか(適格で上限の内側なのに周辺にしていないか、不適格なのに中核にしていないか)。
- 同じ表記が全ての場所で同じ印か。同じ概念の `kind` がそろっているか。
- `spec_sha256`・`brief_sha256`・`annotator` を依頼文の値のとおりに写したか。

## 8 例(架空の記事。実在の記事・過去の注記とは無関係)
台帳:
```ledger
[VERIFIED] ZZ-001: 架空市は2031年4月1日、市営プールの大人料金を400円から500円へ改定した。子ども料金は据え置きで、市営の屋内プール3施設が対象だった。
  scope: 架空市営の屋内プール3施設
  conditions: 子ども料金は据え置き。
  numeric_value: 400円 (旧料金)、500円 (新料金) (numeric_scope: 大人料金。3施設は対象施設数)
  date_or_period: 2031-04-01
  notes_for_writer: 料金改定の理由は一次資料で確認できない。

[VERIFIED] ZZ-002: 市は同じ日、利用者数が前年度比で約12％減ったと説明した。年間の利用者は延べ8万人だった。
  scope: 架空市営プール全体
  conditions: 料金改定の影響かどうかは説明されていない。
  numeric_value: 約12％減、延べ8万人
  date_or_period: 2031年4月1日説明

[VERIFIED] ZZ-003: 市は料金改定とは別に、更衣室を2031年6月に開設する予定だと発表した。
  scope: 架空市営プールの更衣室
  date_or_period: 2031-06（予定）
```
元のニュース欄:
```brief
# Selected Fact Brief

## Storyline
架空市は2031年4月に市営プールの大人料金を400円から500円に改定したが、理由は確認されていない。

## Selected Facts
- 架空市は2031年4月1日、市営プールの大人料金を400円から500円へ改定した。子ども料金は据え置きだった。市営の屋内プール3施設が対象だ。
- 市は同じ日、利用者数が前年度比で約12％減ったと説明した。年間の利用者は延べ8万人だった。ただし、これは料金改定の影響だとは説明していない。市は別に、更衣室を2031年6月に開設する予定だと発表した。
```
注記版(概念は n=7: 400円・500円・約12％・8万人・3施設・2031年4月[1日]・2031年6月 → 上限3。優先順は、Storylineの量[400円, 500円]→他の量[約12％, 8万人]→日付。よって中核は 400円・500円・約12％。8万人は適格だが上限の外、3施設は不適格、日付2つは上限の外):
```annotated
# Selected Fact Brief

## Storyline
架空市は2031年4月【周辺数値】に市営プールの大人料金を400円【中核数値】から500円【中核数値】に改定したが、理由は確認されていない。

## Selected Facts
- 【事実1】架空市は2031年4月1日【周辺数値】、市営プールの大人料金を400円【中核数値】から500円【中核数値】へ改定した。子ども料金は据え置きだった。市営の屋内プール3施設【周辺数値】が対象だ。
- 【事実2】市は同じ日、利用者数が前年度比で約12％【中核数値】減ったと説明した。年間の利用者は延べ8万人【周辺数値】だった。ただし、これは料金改定の影響だとは説明していない。
- 【事実3】市は別に、更衣室を2031年6月【周辺数値】に開設する予定だと発表した。
```
サイドカー:
```sidecar
{
  "slug": "example", "annotator": "A",
  "spec_sha256": "(依頼文の値)", "brief_sha256": "(依頼文の値)",
  "facts": [ {"n": 1, "ledger_ids": ["ZZ-001"]}, {"n": 2, "ledger_ids": ["ZZ-002"]}, {"n": 3, "ledger_ids": ["ZZ-003"]} ],
  "numbers": [
    {"surface": "2031年4月1日", "kind": "date_time", "concept": "C_date", "ledger_ids": ["ZZ-001"], "class": "peripheral", "role": "料金改定日"},
    {"surface": "2031年4月", "kind": "date_time", "concept": "C_date", "ledger_ids": ["ZZ-001"], "class": "peripheral", "role": "料金改定月"},
    {"surface": "400円", "kind": "magnitude", "concept": "C_old", "ledger_ids": ["ZZ-001"], "class": "core", "role": "旧料金"},
    {"surface": "500円", "kind": "magnitude", "concept": "C_new", "ledger_ids": ["ZZ-001"], "class": "core", "role": "新料金"},
    {"surface": "3施設", "kind": "magnitude", "concept": "C_sites", "ledger_ids": ["ZZ-001"], "class": "peripheral", "role": "対象施設数"},
    {"surface": "約12％", "kind": "magnitude", "concept": "C_drop", "ledger_ids": ["ZZ-002"], "class": "core", "role": "利用者減少率"},
    {"surface": "8万人", "kind": "magnitude", "concept": "C_users", "ledger_ids": ["ZZ-002"], "class": "peripheral", "role": "年間利用者"},
    {"surface": "2031年6月", "kind": "date_time", "concept": "C_locker", "ledger_ids": ["ZZ-003"], "class": "peripheral", "role": "更衣室開設予定"}
  ],
  "unmapped_claims": [],
  "annotation_notes": [
    {"where": "概念 C_users", "question": "適格だが上限3の外", "options": ["中核", "周辺"], "chosen": "周辺", "rule": "§3-5-6 cap超過で周辺化"},
    {"where": "概念 C_date / C_locker", "question": "日付は適格だが上限の外", "options": ["中核", "周辺"], "chosen": "周辺", "rule": "§3-5-6 cap超過で周辺化"}
  ]
}
```


【元のニュース欄(brief)】
# Selected Fact Brief

## Storyline
MetaはMuse経由の一部電話を訓練済み契約スタッフに担わせる人間コンシェルジュを試したが、従業員から機微情報共有への懸念が出るなか、適切な開示なしに始めたことをミスと認め、同機能を当面ロールバックした。

## Selected Facts
MetaはMuse経由の電話の一部で、訓練を受けた人間の契約スタッフに電話をかけさせ、相手とのやり取りを完了させるテストを実施した。従業員は、電話中にユーザーの機微情報が契約スタッフへ意図せず共有される可能性を懸念した。MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを始めたことを「ミス」だったと認め、人間コンシェルジュ機能を当面ロールバックした。これは機能の試験に関する話であり、Muse全体の停止ではない。


【台帳】
[VERIFIED] MUSE-HC-001: Metaは2026年9月8日、個人向けAIエージェント「Muse」を発表した。米国でiOS、Android、muse.ai向けに展開すると説明している。
  scope: 米国のMuse提供地域・対象ユーザー
  conditions: Metaの発表時点の提供範囲
  date_or_period: 2026年9月8日
  notes_for_writer: Meta公式発表に基づく製品仕様。独立検証ではなく、Meta自身の説明として扱う。 ([about.fb.com](https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/))

[VERIFIED] MUSE-HC-002: Metaの説明では、Museは専用のクラウド仮想マシン「Muse Secure VM」上で動作し、ブラウザーを開く、フォームに入力する、ユーザーに代わって交渉するなどの作業を実行できる。
  scope: Museの公式製品設計・機能説明
  conditions: Museに必要な権限が付与され、対象サービスへ接続されている場合
  date_or_period: 2026年9月8日時点
  notes_for_writer: 機能の存在を示す事実。実際の性能や成功率を示す事実ではない。 ([about.fb.com](https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/))

[VERIFIED] MUSE-HC-003: Metaの公式説明では、Muse Secure VMではユーザーごとに専用のクラウドコンピューターが割り当てられ、接続サービスのデータや認証情報を保存する。Sentinelという別のエージェントが外部通信やコネクター操作の許可を管理する。
  scope: Museの公式セキュリティ設計
  conditions: Metaが公開した製品設計上の説明
  date_or_period: 2026年9月8日時点
  notes_for_writer: Meta自身の設計説明。人間コンシェルジュ実験における請負業者への情報共有範囲を直接説明する資料ではない。 ([research.meta.ai](https://research.meta.ai/blog/security-and-safety-for-ai-agents-our-approach-with-muse))

[VERIFIED] MUSE-HC-004: Museの電話機能では、ユーザーが米国内の企業・店舗へ電話をかけるよう指示し、散髪の予約、在庫確認、業者からの見積もり取得などを依頼できるとReutersが報じた。
  scope: 米国内の企業・店舗への発信
  conditions: Museの電話機能が利用可能なユーザー
  date_or_period: 2026年9月中旬までに公開・展開
  notes_for_writer: Reuters報道の転載。Meta公式発表ページでは電話機能の詳細までは確認できない。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))

[VERIFIED] MUSE-HC-005: MetaはMuseの電話発信機能を、2026年8月から従業員にテストさせ、Museの一般公開後の数日間にユーザー向けへ段階的に展開したと、社内投稿に基づくReuters報道で伝えられた。
  scope: Meta従業員およびMuseユーザー
  conditions: 社内投稿に基づく報道内容
  date_or_period: 2026年8月〜2026年9月中旬
  notes_for_writer: 2026年8月開始という時期は社内投稿に基づく報道。公式の製品発表日と混同しない。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))

[VERIFIED] MUSE-HC-006: MetaはMuse経由の電話の一部について、AIではなく訓練を受けた人間の契約スタッフが電話をかけ、相手とのやり取りを完了させる「human concierge」「human agent calls」のテストを実施した。
  scope: Muse経由で発信された電話の一部
  conditions: Museから人間の訓練済みエージェントへ依頼が引き渡されるテスト条件
  date_or_period: 2026年9月中旬
  notes_for_writer: 全ての電話を人間が担当したとは書かない。「一部の電話」「テスト」と限定する。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))

[VERIFIED] MUSE-HC-007: 人間コンシェルジュ機能は、2026年9月22日のReuters報道時点で、Meta従業員の半数に有効化されていた。利用を望まない従業員向けにオプトアウト用のグループも設けられていた。
  scope: Meta従業員の一部
  conditions: Museの社内テスト参加者に対する機能有効化
  numeric_value: 50%相当（半数） (numeric_scope: Meta従業員に対する有効化範囲)
  date_or_period: 2026年9月中旬〜2026年9月22日
  notes_for_writer: 50%を全Meta従業員の厳密な割合として断定しない。分母の不確定性を保持する。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))

[VERIFIED] MUSE-HC-008: Metaの社内投稿では、人間が電話を担当した一部テストで、成功率が95〜98%に達する可能性が示された。一方、AIだけで電話をかけた場合の成功率は、それより低いとされたが、具体的な数値は示されていない。
  scope: 人間が電話を担当した一部テスト
  conditions: 成功率の定義、サンプル数、比較対象、測定方法は公開されていない
  numeric_value: 95%〜98% (numeric_scope: 人間が電話を担当した一部テストの成功率)
  date_or_period: 2026年9月時点の社内テスト
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 「人間の方が95〜98%で成功した」と一般化しない。「一部テストで95〜98%の範囲が示された」と書く。因果関係や統計的有意性は確認できない。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))

[VERIFIED] MUSE-HC-009: 社内投稿では、MuseがAIだと認識した相手側から電話を切られる事例が報告された。報道では、保険会社がMuseのAI発信だと分かると繰り返し電話を切ったという従業員の報告が紹介された。
  scope: Museが発信した電話の一部
  conditions: 電話の相手が発信者をAIだと認識した場合
  date_or_period: 2026年9月時点
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 「AI電話は一般に切られる」と拡張しない。個別の従業員報告として扱う。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))

[VERIFIED] MUSE-HC-010: Meta従業員は、人間の契約スタッフが電話を担当すると、電話中にユーザーの機微情報がコールセンターの契約スタッフへ意図せず共有される可能性があるとして、社内でプライバシー上の懸念を示した。
  scope: 人間の契約スタッフがMuse経由の電話を担当するテスト
  conditions: 電話の遂行にユーザー情報が必要となる場合
  date_or_period: 2026年9月中旬〜2026年9月22日
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 懸念の存在を示す事実。実際の大規模な情報漏えいが発生したと断定しない。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))

[VERIFIED] MUSE-HC-011: Museにインターネット・ケーブル料金の交渉を依頼した従業員は、電話の記録に人間の契約スタッフによる人種に関する不適切な発言があったと報告した。
  scope: インターネット・ケーブル料金交渉の1件として報道された事例
  conditions: 人間の契約スタッフが電話を担当したケース
  numeric_value: 1件の従業員報告 (numeric_scope: 報道で紹介された個別事例)
  date_or_period: 2026年9月時点
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 従業員の報告として記録する。契約スタッフ全体の行動や実験全体の性質へ一般化しない。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))

[VERIFIED] MUSE-HC-012: MetaのSuperintelligence Labs部門の副社長は、適切な開示なしに契約スタッフが電話をかけるテストを開始したことを「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。
  scope: Meta社内テストの人間コンシェルジュ機能
  conditions: 適切な開示なしで契約スタッフが電話を担当していたテスト
  date_or_period: 2026年9月22日まで
  notes_for_writer: 「サービス全体を停止した」とは書かない。ロールバック対象は人間コンシェルジュ機能として扱う。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))

[VERIFIED] MUSE-HC-013: Metaの広報担当者Daniel Robertsは、従業員の反応は「圧倒的に肯定的」だったと述べ、テストの目的を、安全・プライバシー保護を実装し、公開前に機能を改善するためのフィードバック収集だと説明した。
  scope: Meta従業員を対象とした人間コンシェルジュ機能のテスト
  conditions: Meta広報担当者によるReutersへの説明
  date_or_period: 2026年9月22日
  notes_for_writer: Meta広報担当者の説明として記録する。客観的なユーザー満足度の測定値とは扱わない。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))

[VERIFIED] MUSE-HC-014: Metaは、電話機能について、商業者との改善を続け、準備が整い、適切な開示ができる場合にのみ公開展開すると広報担当者を通じて説明した。
  scope: Museの電話機能および人間コンシェルジュを含む可能性のある運用
  conditions: 準備完了および適切な開示が整うこと
  date_or_period: 2026年9月22日時点
  notes_for_writer: 公開済みの一般機能と、ロールバックされた人間コンシェルジュ実験を区別する。 ([channelnewsasia.com](https://www.channelnewsasia.com/business/exclusive-meta-testing-human-concierge-its-new-personal-ai-agent-muse-6402946))

[VERIFIED] MUSE-HC-015: Metaは公式説明で、Museについて、ユーザーが接続アプリとアクセス権限を選択でき、メール送信や購入などの敏感な操作の前に確認を求め、操作履歴を表示すると説明している。
  scope: Museの公式製品仕様
  conditions: Metaが公開した通常の製品設計
  date_or_period: 2026年9月8日時点
  notes_for_writer: 公式の製品設計上の説明と、実験時の実際の情報共有運用を混同しない。 ([about.fb.com](https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/))


【依頼文の末尾: 運用上の明確化(仕様の規則変更ではなく、未定義の場合の適用方法)】
(a) 台帳の個別記録に `date_or_period` / `numeric_value` 欄が無い場合は、その記録に限り代替規則(statement内の主数字・日付)を適用する(台帳単位の代替規則を記録単位に適用)。該当: byd_recall(date欄なし4記録)、central_bank_mortgage(date欄なし1記録)、各台帳のnumeric_value欄なし記録(数値を持たない記録は対象外)、small_bag(台帳単位でnumeric欄なし)。
(b) B3 brief内の丸め表現(例: hormuz新B3「約25時間後」、台帳HF-007は「約24時間48分後」)は `unmapped_claims` に「新数値(丸め)」として記録する。記事の中心数字が台帳外としてSTOP条件に該当するかは注記統合時に機械判定する。

【返答の受け取り方】
返答の本文は、呼び出し側(あなたではない)が annotation/out/A/meta/ 以下に保存します。あなたは保存しません。返答は仕様の「6 出力の形式」(=== ANNOTATED_BRIEF_BEGIN === 等の区切りを使う形式)のとおりに、本文だけで返します。
【依頼文(ここまで)】
