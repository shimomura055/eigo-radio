# db_survey_key_phrase_sources_01 — Key Phrase DB照合方式向け 外部語彙DB調査

管理ID: KEY-PHRASE-DB-BASED-SELECTION-DESIGN-01
性質: 設計フェーズ調査(**Trial実行なし・API費用¥0・LLM呼び出しなし**)。
取得方法: 各公式サイト/リポジトリへの直接HTTP GET(`curl`/`python requests`
相当)。OpenAI web_search(¥1.6/call)は使用していない。
取得日時: 2026-09-27(JST、本タスク実施日、以下すべて同日)。
注意: 本文書の「逐語引用」は取得したHTML/PDFから抽出した原文そのもの
(タグ除去・空白正規化のみ)。要約・言い換えではない。ライセンス文の
法的解釈はここでは行わず、事実(何が書かれていたか)のみを記録する。
最終的な採否・商用契約締結の判断はユーザーが行う。

---

## 1. Oxford 3000 / Oxford 5000(Oxford Learner's Dictionaries、OUP)

- URL: https://www.oxfordlearnersdictionaries.com/wordlists/oxford3000-5000
  (取得日時2026-09-27、HTTP 200、size 3,621,103 bytes)
- PDF版(同ページからのリンク、取得日時2026-09-27、リンク先確認のみ・
  ダウンロードはしていない):
  - `.../external/pdf/wordlists/oxford-3000-5000/The_Oxford_3000.pdf`
  - `.../external/pdf/wordlists/oxford-3000-5000/The_Oxford_3000_by_CEFR_level.pdf`
  - `.../external/pdf/wordlists/oxford-3000-5000/The_Oxford_5000.pdf`
  - `.../external/pdf/wordlists/oxford-3000-5000/The_Oxford_5000_by_CEFR_level.pdf`
  - American版(`American_Oxford_3000.pdf`等)も同様に存在。
- (1) 収録内容: 単語(word)のみ。ページ内は各語にCEFR band
  (`data-ox3000="b2"`のようなdata属性、例: `copyright`→b2、`licence`→b2、
  `license`→c1)が付与されている。phrase/idiom/phrasal verb/collocation
  ではない(Phrase系は別リスト「Oxford Phrase List」、後述2節)。
- (2) 件数: Oxford 3000(約3,000語)/Oxford 5000(約5,000語、3000を含む
  上位語彙)。
- (3) CEFR level情報: あり(A1〜C1、上記data属性で確認)。
- (4) データ形式: Web page(HTML、data属性埋め込み)+ 公式PDF(語彙リスト、
  CEFR別リストPDFも別途あり)。CSV/JSON配布は確認できず。
- (5) ローカルDB化可否: 技術的にはHTML/PDFからのスクレイピングで可能。
  ただし(6)のライセンス制約により、商用利用のためのローカル取込は
  **不可**(下記条項参照)。
- (6) 商用Production利用可否: **不可(標準利用規約の範囲内では)**。
  Terms and Conditionsページ(URL: https://www.oxfordlearnersdictionaries.com/terms-and-conditions、
  取得日時2026-09-27、HTTP 200)より逐語引用:
  > "make available the Oxford Learner's Dictionaries website and/or the
  > Products for domestic and private use. You agree not to use the
  > Products for any commercial, business or re-sale purposes"
  また、同ページには"Buyer"が"a licence to access a Product"を別途
  取得する枠組みが明記されている(= 商用利用には別途OUPとのライセンス
  契約が必要)。attribution要否・redistribution制限・derivative database
  可否は、標準利用規約の範囲では「そもそも商用利用不可」のため
  **検討対象外(UNRESOLVED、要OUP個別商用ライセンス契約)**。
- (7) 都度Internetアクセス要否: スクレイピングなら初回のみ(以降は
  ローカルキャッシュ可、ただしライセンス上不可のため実施しない)。
- (8) eigo-radio適合性: 単語のみでphrase/idiom非対応。ライセンス上、
  現行の無償利用枠ではProduction組み込み不可。**Trial/評価参照のみ**
  (人間が目視で参考にする用途に限定)。

## 2. Oxford Phrase List(Oxford Learner's Dictionaries、OUP)

- URL: https://www.oxfordlearnersdictionaries.com/wordlists/oxford-phrase-list
  (取得日時2026-09-27、HTTP 200、size 531,514 bytes)。ページタイトル
  "Oxford Phrase List | OxfordLearnersDictionaries.com"を確認。
- (1) 収録内容: phrase(複数語表現、句動詞・コロケーション等を含む
  学習者向けフレーズ)。
- (2) 件数: 公称約750フレーズ(サイト説明文言、本タスクでは詳細件数の
  逐語確認はしていない=`UNRESOLVED`件数詳細)。
- (3) CEFR level情報: あり(Oxford 3000/5000と同様の枠組みでCEFR band
  付与、本タスクでは各フレーズ個別のband値までは逐一確認していない)。
- (4) データ形式: Web page(HTML)。PDF配布の有無は本タスクでは未確認
  (`UNRESOLVED`)。
- (5) ローカルDB化可否: 技術的には可能。
- (6) 商用Production利用可否: **不可**。同一ドメイン
  (oxfordlearnersdictionaries.com)であり、1節と同じTerms and Conditions
  (商用利用禁止条項)が適用される。
- (7) 都度Internetアクセス要否: スクレイピングなら初回のみ(ライセンス上
  実施しない)。
- (8) eigo-radio適合性: phrase/phrasal verb/collocationを含み観点としては
  最も理想的だが、ライセンス上Production不可。**Trial/評価参照のみ**。

## 3. English Vocabulary Profile(EVP)/ Cambridge English Profile

- URL(EVPポータル): https://www.englishprofile.org/wordlists/evp
  (取得日時2026-09-27、HTTP 404 — ページ構成変更または直リンク切れ)。
- URL(トップページ): https://www.englishprofile.org (取得日時2026-09-27、
  HTTP 200、ただしBubble.io製SPAでJavaScriptレンダリング後にのみ本文が
  表示されるため、静的HTTP GETでは実コンテンツ・利用規約文言を
  取得できなかった)。
- Cambridge Dictionaryのデータライセンスページ(関連法人=Cambridge
  University Press & Assessment、EVPと同じ発行元)から、データ利用の
  一般的な枠組みを確認: URL https://dictionary.cambridge.org/license.html
  (取得日時2026-09-27、HTTP 200)より逐語引用:
  > "License our data Are you interested in using our dictionary data for
  > language processing, or other electronic applications? We're happy to
  > consider all requests, and have a number of data sets available...
  > We're happy to discuss a pricing model that is appropriate for your
  > organisation and how you want to use the data."
  および商用ライセンス申請ページの存在(`dictionary-api.cambridge.org/commercial-agreement`、
  `dev.eim-ciip-cambridge.org/apply`)を確認。
- (1) 収録内容: word/phrase/phrasal verb/idiom等(CEFR各バンドの
  "criterial"語彙・表現、English Grammar Profile等の姉妹プロジェクトも
  存在)。
- (2)〜(5): サイトがJS SPAのため本タスクの直接HTTP GETでは件数・形式の
  逐語確認ができず`UNRESOLVED`(オンライン検索UIでの閲覧は無償だが、
  データセット自体の構造・件数は未確認)。
- (6) 商用Production利用可否: **UNRESOLVED、ただし個別商用ライセンス
  契約が前提である可能性が高い**(上記Cambridge Dictionaryライセンス
  ページの一般的な枠組みから推定。EVP固有の価格・条件は未確認のため
  断定しない)。無償の範囲はオンライン検索(閲覧)のみと考えられる。
- (7) 都度Internetアクセス要否: 現状はオンライン検索UIのみのため、
  ローカルDB化には別途データ提供契約が必要と見込まれる。
- (8) eigo-radio適合性: 内容面では理想的候補(word+phrase+CEFR)だが、
  ライセンス条件がUNRESOLVED。**Trial/評価参照のみ(商用契約なしでは
  ローカル取込不可と推定)**。

## 4. CEFR-J Vocabulary Profile(CEFR-J Wordlist、東京外国語大学 投野由紀夫研究室)

- URL: http://cefr-j.org/download.html (取得日時2026-09-27、HTTP 200、
  size 70,960 bytes)
- (1) 収録内容: word(品詞情報・CEFR level・主要名詞の主題カテゴリ情報
  付き)。「Core Inventory and Threshold Levels」を含む。phrase/idiom
  専用リストではない(word中心)。
- (2) 件数: Version 1.6(2020-03-24更新版)。具体的総語数は本ページ
  逐語では未確認(`UNRESOLVED`詳細件数、ただし数千語規模)。
- (3) CEFR level情報: あり(CEFR-J、A1〜B2寄りの日本の学習指導要領に
  合わせた6段階)。
- (4) データ形式: ダウンロード登録(利用許諾同意)後にExcel形式で配布
  (ページ記述「CEFR-J本体をダウンロード 使用許諾に同意していただいて
  ダウンロードになります」)。
- (5) ローカルDB化可否: **可能**(登録・引用を条件に配布)。
- (6) 商用Production利用可否: **条件付きで可能**。ページより逐語引用
  (日本語原文のまま):
  > "本語彙表の著作権は東京外国語大学投野研究室に帰属するが、適切な
  > 引用を行っていただければ研究教育および商用においても無償で利用
  > できる。"
  引用形式の指定:
  > "『CEFR-J Wordlist Version 1.6』東京外国語大学投野由紀夫研究室.
  > （URL: XXX より◎年◎月ダウンロード）"
  免責事項・追加条件(同ページ逐語):
  > "1)本語彙表は無償で公開する物であり、本語彙表の使用により生じた
  > 一切の損害・不利益・批判などに対して、科研チームおよび投野研究室は
  > 一切の責任を負わない。
  > 2)商用利用に関しては、監修などを行う場合には別途相談の上、必要な
  > 経費を請求する。
  > 3)語彙表は不完全な部分があり、内容的に誤りがある可能性は否定
  > できないので、随時改訂版を作成するものを利用されたい。
  > 4)本語彙表を改変して別の語彙表を作ることはかまわないが、必ず
  > 本語彙表を適切に引用しなければならない。"
  英語版ページの併記(逐語):
  > "The copyright of this wordlist belongs to Tono Laboratory at TUFS,
  > but the list can be used for both research and commercial purposes
  > with a proper acknowledgement of the source."
  解釈整理: 「素の語彙表を商用利用すること」自体は引用表記のみで無償
  可能。ただし「監修等の追加役務」を依頼する場合は別途費用が発生する
  (eigo-radioが単に語彙表データを参照するだけであれば前者に該当する
  と考えられるが、契約解釈の最終確認はユーザー判断とする)。
- (7) 都度Internetアクセス要否: 初回ダウンロードのみ、以降ローカル
  キャッシュ可。
- (8) eigo-radio適合性: word中心・CEFR情報ありでStandard/Advanced語彙
  との対比に有用。ただしphrase/idiom/phrasal verbは収録されていない
  ため、この1つだけでは候補cover範囲が狭い。**Productionへローカル
  取込可能(条件明確)**。

## 5. New General Service List(NGSL)/ NAWL / NGSL-S / BSL(旧称TSL)

- 公式サイト: https://www.newgeneralservicelist.com (取得日時2026-09-27、
  HTTP 200、size 254,302 bytes)。
- 重要な注記: 旧知られていたドメイン`newgeneralservicelist.org`は
  2026-09-27時点でNGSLと無関係な第三者コンテンツ(オンラインカジノ
  ゲーム紹介記事、"Chicken Road"等)が表示される状態になっており
  (取得日時2026-09-27、HTTP 200、本文中に"Copyright © 2026 Chicken Road
  Game Gambling"等を確認)、**NGSL公式サイトとして参照してはならない**。
  `.com`ドメインのFAQページ内に逐語で明記あり(取得日時2026-09-27、
  URL https://www.newgeneralservicelist.com/faqs-4):
  > "The only official site of the NGSL Project is
  > newgeneralservicelist.com ... students, publishers, and institutions
  > should use only newgeneralservicelist.com for official NGSL
  > resources, citations, downloads, and project information."
- (1) 収録内容: NGSL=一般語彙(word)。NAWL=Academic Word相当。
  NGSL-S=口語(spoken)頻出語。BSL(Business Service List、旧TSL表記も
  サイト内に残存)=ビジネス語彙。いずれもword中心、phrase/idiom専用
  リストではない。
- (2) 件数: NGSL約2,800語、NAWL約960語等(公式サイト一般記述、本タスク
  では各リストの正確な件数逐語は未取得=`UNRESOLVED`詳細件数)。
- (3) CEFR level情報: 明示的なCEFR対応表は公式サイト内で確認できず
  (頻度順リストが基本、`UNRESOLVED`詳細)。
- (4) データ形式: 公式サイトの説明によれば無償配布(ダウンロード導線は
  JavaScript経由のため本タスクの静的HTTP GETでは実ファイルURLを
  直接確認できず、`UNRESOLVED`詳細フォーマット。一般に知られている
  形式はExcel/CSV)。
- (5) ローカルDB化可否: **可能**(下記ライセンスにより明示的に許可)。
- (6) 商用Production利用可否: **可能**。公式サイトトップページより
  逐語引用(取得日時2026-09-27):
  > "Open since 2013 Free under Creative Commons, including commercial
  > use. No accounts, no paywalls, no ads."
  および:
  > "© 2026 Dr. Charles Browne. Word lists released under Creative
  > Commons."
  FAQページより逐語引用:
  > "Like all of our other public lists, these new lists will be made
  > available for free via the least restrictive Creative Commons
  > License along with our many free learning tools."
  注記: 具体的なCC変種(BY / BY-SA等)の明示的なバージョン番号・条項名
  までは本タスクの直接HTTP GETでは確認できなかった(`UNRESOLVED`詳細
  ライセンス条項番号。ただし「商用利用を含め無償」という方針自体は
  上記2箇所で明確に確認済み)。attribution(引用)は前提として推奨されて
  いると解釈するのが妥当。
- (7) 都度Internetアクセス要否: 初回ダウンロードのみ。
- (8) eigo-radio適合性: word中心のため、Key Phrase(1〜5語、phrase/idiom
  含む)の主要DBそのものにはならないが、単語候補の頻度・基礎語彙判定
  (除外Gateの「簡単すぎる」判定の補助データ)として有用。
  **Productionへローカル取込可能(商用可・具体的CC条項番号のみ
  UNRESOLVED)**。

## 6. PHRASE List(Martinez & Schmitt, 2012, "A Phrasal Expressions List", Applied Linguistics 33(3))

- 著者公式ページ: https://www.norbertschmitt.co.uk/vocabulary-resources
  (取得日時2026-09-27、HTTP 200、size 446,441 bytes)より逐語引用(抜粋):
  > "There is little dispute that formulaic language forms an important
  > part of the lexicon, but to date there has been no principled way to
  > prioritize the inclusion of formulaic items in pedagogic materials...
  > I have tried to address this deficiency by presenting the PHRASal
  > Expressions List (PHRASE List). The list consists of the 505 most
  > frequent non-transparent multiword expressions in English...
  > The actual PHRASE List is provided below in a Word document."
- (1) 収録内容: non-transparent multiword expression(idiom寄りの
  複数語表現、receptive use想定)。
- (2) 件数: 505件(上記引用より確認)。
- (3) CEFR level情報: なし(頻度ベースのリストであり、CEFR band付与は
  確認できず)。
- (4) データ形式: Word文書(著者サイトから直接配布、CSV/JSON化はされて
  いない)。学術論文本体はOxford University Press刊行の購読誌
  (Applied Linguistics)にあり、academic.oup.comの該当ページは
  本タスクのHTTP GETでは403(bot対策と推測)で本文取得不可。
- (5) ローカルDB化可否: 技術的にはWord文書からの抽出で可能。
- (6) 商用Production利用可否: **UNRESOLVED(明示的な商用ライセンス文言
  を著者ページ上に発見できず)**。著者個人サイトでの無償配布は「研究・
  教育目的の利用」を想定した記述にとどまり、eigo-radioのような商用
  Productionでの再配布・組み込みを明示的に許可/禁止する文言は確認
  できなかった。推測で「可」「不可」と判定しない。
- (7) 都度Internetアクセス要否: 初回ダウンロードのみ。
- (8) eigo-radio適合性: idiom/phraseの複数DB一致判定の一角として内容面
  では有用だが、商用可否がUNRESOLVEDのため**Trial/評価参照のみ
  (Production投入は著者への直接確認後)**。

## 7. PHaVE List(Garnier & Schmitt, 2015, "The PHaVE List", Language Teaching Research)

- 著者公式ページ: 同上 https://www.norbertschmitt.co.uk/vocabulary-resources
  (取得日時2026-09-27)より逐語引用:
  > "my student Melodie Garnier developed the PHrasal VErb Pedagogical
  > List (PHaVE List). It lists the 150 most frequent phrasal verbs, and
  > provides information on their key meaning senses, which cover 75%+
  > of the occurrences in the Corpus of Contemporary American English."
- (1) 収録内容: phrasal verb(150件)+ 主要義(meaning sense)+ 出現割合+
  定義+学習者向け例文。
- (2) 件数: 150 phrasal verbs(上記引用より確認)。
- (3) CEFR level情報: なし(頻度・意味カバー率ベース)。
- (4) データ形式: 論文PDF・User's Manual PDF・Alphabetical
  Index/Frequency Ranking(著者ページのリンク名から、PDF/文書形式と
  推定。CSV/JSON配布は確認できず)。
- (5) ローカルDB化可否: 技術的にはPDF/文書からの抽出で可能。
- (6) 商用Production利用可否: **UNRESOLVED**(6節のPHRASE Listと同様、
  著者ページ上に商用利用可否を明示する文言は確認できなかった)。
- (7) 都度Internetアクセス要否: 初回ダウンロードのみ。
- (8) eigo-radio適合性: **discontinuous phrasal verb(pick it up⇄pick
  up)を含む口語頻出phrasal verbのcanonical化・意味センス確認に有用**
  だが、商用可否UNRESOLVEDのため**Trial/評価参照のみ**。

## 8. Academic Collocation List(ACL, Ackermann & Chen, 2013、Pearson)

- 公式PDF: https://www.pearsonpte.com/content/dam/ELL/pte/pearsonpte/pdfs/the-academic-collocation-list.pdf
  (取得日時2026-09-27、HTTP 200、size 1,290,998 bytes、40ページ、
  "VERSION 2/2025"と明記)より逐語引用(1ページ目):
  > "Created by Pearson, the Academic Collocation List contains the most
  > frequent and pedagogically relevant lexical collocations in written
  > academic English... Number of collocations: 2,469. Source: Pearson
  > International Corpus of Academic English (25 mill words). Purpose:
  > to support PTE preparation."
- (1) 収録内容: lexical collocation(verb+noun/adjective+noun/noun+noun
  等)、Component I・IIの品詞情報付き。
- (2) 件数: 2,469件(PDF本文より確認)。
- (3) CEFR level情報: なし。
- (4) データ形式: PDF(番号付きリスト、Word文書相当のレイアウト)。
  CSV/JSON配布は確認できず。
- (5) ローカルDB化可否: 技術的にはPDF抽出で可能(本タスクでpypdfにより
  実際に全40ページ中の該当リストをテキスト抽出できることを確認済み)。
- (6) 商用Production利用可否: **UNRESOLVED**。PDF全体(表紙〜末尾)を
  確認したが、明示的なライセンス条項・著作権表示文は本タスクで抽出
  した範囲では見当たらなかった(Pearsonという商用試験会社の
  マーケティング資料としての性質上、既定は「全著作権留保」である
  可能性が高いが、明文未確認のため断定しない)。
- (7) 都度Internetアクセス要否: 初回ダウンロードのみ。
- (8) eigo-radio適合性: collocationのchunk価値評価に有用(2軸のうち
  「chunk価値」側の外部根拠として使える)が、商用可否UNRESOLVEDのため
  **Trial/評価参照のみ**。

## 9. Wiktionary(英語版、派生ソースとして)

- URL: https://en.wiktionary.org/wiki/Wiktionary:Copyrights (取得日時
  2026-09-27、HTTP 200、size 86,151 bytes)より逐語引用:
  > "The original texts of Wiktionary entries are dual-licensed to the
  > public under both the Creative Commons Attribution-ShareAlike 4.0
  > International License (CC-BY-SA) and the GNU Free Documentation
  > License (GFDL)... Permission is granted to copy, distribute and/or
  > modify the text of all Wiktionary entries under the terms of the
  > Creative Commons Attribution-ShareAlike 4.0 International License..."
- (1) 収録内容: word/phrase/idiom/phrasal verb/collocation等を含む
  (エントリごとに"Idiom"/"Phrase"/"Proverb"等の品詞相当カテゴリが
  付与される)。CEFR情報はなし。
- (2) 件数: 英語エントリ数十万件規模(idiom/phraseカテゴリはその一部)。
- (3) CEFR level情報: なし。
- (4) データ形式: MediaWikiダンプ(XML)またはWiktextract等のサードパーティ
  パーサ出力(JSON)。API経由アクセスも可能。
- (5) ローカルDB化可否: **可能**(ダンプ配布あり)。
- (6) 商用Production利用可否: **可能、ただしShareAlike条件に注意**。
  CC BY-SA 4.0は商用利用を許可するが、「同じライセンスでの再配布」を
  要求するShareAlike条項を含む。eigo-radioが内部照合用DBとして
  ローカルに保持し外部へ再配布しない場合は実務上の抵触は小さいと
  考えられるが、**将来Wiktionary由来データを含む成果物(例:
  加工済み複合DB)を外部公開・販売する場合は法務確認が必要**
  (本タスクでは断定せず、リスクとして記録するにとどめる)。
- (7) 都度Internetアクセス要否: 初回ダンプ取得のみ(定期更新を追う
  場合は再取得)。
- (8) eigo-radio適合性: idiom/phrase判定の補助DB(他の専門DBに無い
  口語表現・discourse expressionの一致確認)として有用。
  **Productionへローカル取込可能(商用可・ShareAlike注意点あり)**。

---

## 横断メモ: 「複数DB一致」を成立させるための組み合わせ

上記のうち商用ローカル取込が明確な(4) CEFR-J・(5) NGSL系・(9)
Wiktionaryの3系統だけでも、word中心2系統(CEFR-J・NGSL系)+
phrase/idiom系1系統(Wiktionary)という異なる性質のDBの組み合わせが
確保できる。Oxford系・EVP・PHRASE/PHaVE/ACLは「複数DB一致」の追加
根拠としては現時点でTrial/参考データにとどめ、Production判定の
必須条件には含めない設計とする(詳細は設計doc側)。
