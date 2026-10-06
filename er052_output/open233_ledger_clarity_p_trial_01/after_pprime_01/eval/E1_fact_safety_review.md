# E1 Fact安全性+原資料照合(判定材料。最終判定=Fable)
原資料(curl取得、¥0): CNA=Reuters転載(取得可) / AOL=Reuters転載(可) / 404 Media(可) / Meta公式about.fb.com・research.meta.ai(可) / marketscreener(403)・investing(403)・Yahoo(JS描画で本文取得不可)。
注意: pprime_provenance.jsonに引用URL3件の記載なし(Before notesのCNA/about.fb.com/research.meta.aiを取得)。After引用元はdraft/verification記載の上記6URLで、うち取得不可3件の本文はCNA/AOL(同一Reuters記事)で代替照合。
## 15 fact照合表(原資料=Reuters CNA転載を主、逐語20語以内)
| fact | claim要旨 | 原資料の該当記述 | 判定 |
|---|---|---|---|
|001|Meta,Muse経由の電話一部を人間請負業者が処理する"human concierge"を試験|"human contractors quietly handle some of the phone calls" (CNA)|一致|
|002|米国事業者へ発信、ヘアカット/在庫/請負業者見積|"booking haircuts, checking whether a store has an item in stock or getting quotes" (CNA)|一致|
|003|9月中旬に従業員半数へ有効化、オプトアウトGあり|"for half of its employees last week"; "opt-out group" (CNA)|一致|
|004|社内告知=Museが依頼を訓練エージェントへ引渡し|"hand requests to a trained agent, who places the call" (CNA)|一致|
|005|一部従業員が機微情報の意図せぬ共有を懸念|"sensitive information being shared unintentionally with contractors" (CNA)|一致|
|006|ケーブル料金交渉の通話記録に人種差別的言及|"transcript showed the human contractor had made a racist reference" (CNA)|一致|
|007|副社長がmissと認め当面ロールバック|"it was a miss"; "rolled back this feature" for now (CNA)|一致(下記所見)|
|008|人間発信の成功率95-98%に達し、AIは低い|"could get their success rate up to the 95 per cent to 98 per cent range" (CNA)|断定強化1件(軽微):"could/some tests indicated"→"達し"(過去の事実断定)|
|009|広報Roberts「overwhelmingly positive」、目的=FB収集|"response from employees had been 'overwhelmingly positive'" (CNA)|一致|
|010|準備完了・適切開示時のみ「一般公開」|"will only roll it out when it's ready and with the proper disclosures"|判定保留1:"roll it out"→「一般公開」と具体化、"potential calling feature"の"potential"脱落(notesで公開済みでない旨は補足)|
|011|8月に従業員テスト→アプリ公開後数日以内に段階展開|"in August ... gradually started rolling it out ... in the days after the app's debut"|一致(「数日以内」は軽微な言い換え)|
|012|保険会社がAIと分かると繰り返し切断(1従業員報告)|"they keep hanging up on Muse when they hear it is AI"|一致|
|013|9/8発表、Muse Secure VM=エージェントとデータを収容する専用VM|"a dedicated, virtual machine (VM) that houses both the agent and a person's data" (Meta公式、日付9/8表記あり)|一致|
|014|接続アプリ/アクセス範囲を選択、変更・切断はいつでも|"People choose which apps ... change access or disconnect a service whenever they want"|一致|
|015|会話・VM内データをMeta広告システムと共有しない|"doesn't share ... conversations or the data in your Virtual Machine with Meta ad systems"(research.meta.ai)|一致。ただし同段落に"how you use Muse can influence the ads you see"の留保あり。claimに含まれず判定保留2(出典URLはabout.fb.com/jaで、原文はresearch.meta.ai側にも存在)|
## 集計(数値)
- 疑義件数(原資料との意味不一致): 0件 / 判定保留件数: 2件(MMHC-010、MMHC-015) / 追加Fact件数(原資料にない新事実): 0件
- 断定強化件数: 1件(MMHC-008、軽微。STOP条件「疑義1件でも」に照らす扱いはFable判断) / 否定反転: 0件 / 数値・日付・固有名の相違: 0件(95-98%・50%・9/8・9/22・Daniel Roberts・Superintelligence Labs全一致)
## 所見
1. MMHC-007: 原資料"it was a miss"/"rolled back this feature"for now。claimは「miss」「ロールバック」(片仮名)のまま。原資料自体が具体的動作(停止/無効化等)を記述しないため、規則3の置換対象となる具体動作が存在せず、置換不能。notes「語義: 原語=rolled back this feature。…「当面」…」で原語と限定は保持。意味一致。Before HC-012の「サービス全体を停止したとは書かない」は消失したが、claim内「human concierge機能を」で範囲は限定済み。
2. M4フラグ: MMHC-005は新規否定「せず」(「意図せず」=原資料"unintentionally"の訳、反転なし、Before HC-010も「意図せず」を含む)。MMHC-015は「ない」(「共有しない」=原資料"doesn't share"、反転なし)。いずれも原資料と同方向で意味不一致なし。新括弧・番号・因果語は0。MMHC-015はBefore側の括弧2→0(URLリンク除去)。
3. 未接地トークン4件: MMHC-001 claim「アシスタント」「パーソナル」(原文"personal AI assistant"、Beforeは「エージェント」と訳出差)、MMHC-012 notes「1」(1人の従業員)、MMHC-013 notes「テスト」。いずれも原資料に根拠あり=実質接地済み(ツールのgrounding源がdraft構造欄中心のため検出)。Before自身は14件。
4. notes短縮(172.2→51.6字): ①残った指針=範囲限定(半数≠全従業員、1従業員報告、懸念≠漏えい、公開方針≠公開済み、数値は一部テスト)。②Writerが読む台帳txtから落ちたもの=成功率の定義/サンプル数/測定方法の不明(HC-008 conditions)、統計的有意性不明、「客観的満足度とは扱わない」(HC-013)、「サービス全体停止と書かない」(HC-012)、「全ての電話を人間が担当とは書かない」(HC-006)。ambiguity欄(draft JSON)には成功の定義・件数不明等が残るが、verified_fact_ledger.txtには出力されないため、Writerには届かない可能性(規則「ambiguity_noteとnotes_for_writerに不確実点を残す」はdraft側では充足、txt側では一部のみ)。
5. 否定語−4: 類似対応(類似度低が多く対応は参考)でBefore合計20→After 16。減少の主因は①Beforeのnotes内の「〜と書かない/断定しない/一般化しない」(Writer向け禁止指示、原資料の否定ではない)の消失(MMHC-001:2→0、004:2→0、007:1→0、008:4→0、011:1→0)。原資料にない否定が新規追加された例なし。原資料の否定そのもの(unintentionally、doesn't share、not made aware等)は保持。「必要な否定が落ちた」=上記4の禁止指示群(特にHC-008の統計的有意性不明、HC-012の停止範囲)。増加側はMMHC-005(+2: 意図せず/できない系)、010(+2)、014(+2)等で、全て原資料の否定・条件("only when"→「のみ」、"disconnect"等)に対応、反転なし。
6. 検索回数7→3: provenance=Research方法は不変(prompt追記のみ、sha記録あり、model_id gpt-5.6-luna)。Before 15 factのうちAfter対応なし: HC-001(Muse 9/8発表・iOS/Android/muse.ai)、HC-002(VMでブラウザ/フォーム/交渉)、HC-003(Sentinel・専用クラウドPC)=3件。After側でBefore対応なし: MMHC-004(社内告知の引渡し、404 Media)、MMHC-015(広告システム非共有)=2件(MMHC-014はHC-015と一部重複)。Meta公式発表のうち製品機能説明が減り、電話実験の事実(Reuters/404)に寄った。Before⇔After未対応合計=5件(意味的対応、自動対応は不確定)。
7. sha相違の原因: checker_after_01/approved_switches_dump_after_p01.json(1545B)とe2e02 dump(1627B)をdiff→switches本体は同一(equal=true)。差分3点のみ: budget_jpy 10.0 vs 20.0、instances(['meta_run03_advanced'] vs 3 instance)、run_cap_jpy(E2E02にのみ存在)。run_checker_after_p01.pyがswitches以外のメタ(budget/instances)も同ファイルへ保存するため。運用差でありswitches相違ではない。補足: provenanceのmodel_idはchecker側gpt-6-luna、Research側gpt-5.6-lunaと表記が異なる(別系統の記録値、本評価では未調査)。
## Fableへの引継ぎ
STOP条件「意味一致に疑義」は、MMHC-008(could→達し)を疑義と扱うかが論点。MMHC-010の「一般公開」、MMHC-015の広告留保欠落は保留。追加Fact・反転・数値相違は0。
