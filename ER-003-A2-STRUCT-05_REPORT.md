# ER-003-A2-STRUCT-05 実行報告(In One Lineセクション補足復元)

**管理ID: ER-003-A2-STRUCT-05**
**実施日: 2026-08-09**
**ステータス: `PROTOTYPE / UNDER_EVALUATION`(A2全体はPROTOTYPEのまま、CURRENT_SPECへ未反映)**

## 1. 目的・修正内容

A2構造支援プロトタイプ3記事(A01・A02・ADD03)の`In One Line`セクションが
中心1文のみで終わっており、B1(中心1文+補足2文程度)よりセクションが
薄くなっていた。「In One Line」という見出しは中心1文そのものを指す語で
あり、セクション全体を1文に限定する必要はないという考え方に基づき、
各記事の中心1文はそのまま維持し、その後にA2言語仕様を満たす英語補足を
2文追加した。**変更したのはIn One Lineセクションのみ**で、Preview・
Key Phrases位置・Comment1〜4・Full Story Part1/2・Point One/Two・
Full Story分割位置は一切変更していない。

## 2. 各記事の修正結果

### A01

中心1文(無変更): "Argentina turned the game around in seven minutes and ended England's dream."

補足:
1. "Messi did not score, but he made both late goals happen."(11語)
2. "The two teams chose different paths, and this decided the game."(11語)

### A02

中心1文(無変更): "The UK hopes more teenagers will keep the night setting and simply go to sleep."

補足:
1. "This is not a full ban; teenagers can still turn it off."(12語)
2. "But even a simple first setting can change what people do."(11語)

### ADD03

中心1文(無変更): "Trump dropped the toll, but oil traders will not relax until ships can pass safely."

補足:
1. "The toll is gone, but real danger remains in the strait."(11語)
2. "Traders still worry more about safety than about cost."(9語)

全文は各記事の統合台本([A01](ER-003-A2-STRUCT-04_A01_INTEGRATED_SCRIPT.md)、
[A02](ER-003-A2-STRUCT-03_A02_INTEGRATED_SCRIPT.md)、
[ADD03](ER-003-A2-STRUCT-04_ADD03_INTEGRATED_SCRIPT.md))の
`In One Line`パートに反映済み。

## 3. QA結果

| 確認項目 | 結果 |
|---|---|
| 中心1文を既存A2版から変更していない | 3記事とも該当箇所の文字列を変更していないことを確認(コピー&ペーストのみ) |
| 補足は2文程度 | 3記事とも各2文 |
| 新規factなし | 下記4節参照 |
| A2文長条件(平均11語以下・最長18語以下) | 補足文個別では9〜12語、いずれも18語以下。中心1文を含めた3文単位の平均は、A01=11.7語・A02=12.7語・ADD03=11.7語(中心1文自体が15語のため平均はやや上振れするが、既存の中心1文は変更対象外) |
| spoken-first | 全補足文で主語が文頭付近に出る構成を確認(下記5節) |
| Comment 4との過度な重複がないこと | 下記6節参照 |
| Point One/Twoの既出内容と整合 | 下記4節参照 |
| セクション全体が自然な締めになっている | 目視確認済み(1文目=中心要約、2文目=理由/残る論点、3文目=締めの一言、という自然な流れ) |

## 4. 新規fact非追加の確認

| 記事 | 補足文 | 出典(既出箇所) |
|---|---|---|
| A01 | "Messi did not score, but he made both late goals happen." | Point One("He did not take the final shot for either goal."他) |
| A01 | "The two teams chose different paths, and this decided the game." | Point Two(結論部"England made changes to defend. Argentina made changes to score.") |
| A02 | "This is not a full ban; teenagers can still turn it off." | Full Story Part 2("it would not be a full ban. Teenagers could change the setting.") |
| A02 | "But even a simple first setting can change what people do." | Point Two("the first setting changed what many children did.") |
| ADD03 | "The toll is gone, but real danger remains in the strait." | Full Story Part 2("The fee was gone, but the danger was not.") |
| ADD03 | "Traders still worry more about safety than about cost." | Full Story Part 2("Traders asked a more important question: Could ships pass through safely?") |

いずれも新規の数値・固有名詞・事実は追加していない。

## 5. Spoken-first確認

全6文とも、主語(Messi/The two teams/This/even a simple first
setting/The toll/Traders)が文頭または文頭に近い位置に出ており、長い
前置詞句・名詞句を文頭に置く構成にはなっていない。

## 6. Comment 4との重複確認

各記事のComment4(日本語)と対応する英語補足は、同じ論点を扱っている
箇所があるが、これは意図的な設計(日本語で先に理解を促し、英語で最後に
定着させる)であり、**文言としては重複していない**(日本語からの
逐語訳ではなく、英語として独立に書いた文)。3記事とも、Comment4は
Points全体を対象にした要約であるのに対し、In One Line補足は中心1文
(記事全体のテーマ)により直結した2文としている。

## 7. 機械検証

`er003_a2_article.py`の既存関数(`compute_a2_grammar_vocab_heuristics`、
`compute_number_per_sentence_report`)を用いて、6件の補足文すべてを
検証した。

- 関係詞候補・受動態候補・完了形候補・分詞構文候補: **全て0件**
  (A01補足文で当初「that difference」が関係詞ヒューリスティックに
  誤検出されたため、"this decided the game"へ言い換えて解消。指示詞の
  "that"を関係詞と誤認する既知のヒューリスティック限界であり、目視で
  誤検出と確認した上で自然な表現へ調整した)
- 1文複数数字: 0件(補足文はいずれも数字を含まない)

## 8. A2_PROTOTYPE_SPEC更新内容

「維持する項目」に新規行を追加し、「In One Line」という見出しは中心
1文要約を指す語であり、セクション全体を1文に限定しないこと、中心1文
の後にA2言語仕様を満たす短い補足を2文程度置くことを明記した
([A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md))。A2全体は引き続き
`PROTOTYPE`のまま、CURRENT_SPECへは昇格していない。

## 9. 作成・変更ファイル

- 更新: [ER-003-A2-STRUCT-04_A01_INTEGRATED_SCRIPT.md](ER-003-A2-STRUCT-04_A01_INTEGRATED_SCRIPT.md)(In One Lineに補足2文追加)
- 更新: [ER-003-A2-STRUCT-03_A02_INTEGRATED_SCRIPT.md](ER-003-A2-STRUCT-03_A02_INTEGRATED_SCRIPT.md)(同上)
- 更新: [ER-003-A2-STRUCT-04_ADD03_INTEGRATED_SCRIPT.md](ER-003-A2-STRUCT-04_ADD03_INTEGRATED_SCRIPT.md)(同上)
- 更新: [A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)(In One Line原則を追加)
- 新規: 本レポート
- 他のセクション(Preview/Key Phrases/Comment1〜4/Full Story/Points)は変更していない
- コード変更: なし(検証は既存関数のみ使用)

## 10. テスト結果

コード変更がないため、プロジェクト全体回帰テストの再実行は不要と判断した
(直近の実行結果1660件全合格が引き続き有効)。7節の機械検証は既存関数
のみを用いた一時的な確認スクリプトで実施し、リポジトリへは追加していない。

## 11. Git status / commit / push未実行確認

commit済み(pushなし)。**pushは実行していません。**

## 参照元

[PROJECT_INDEX.md](PROJECT_INDEX.md)、[OPEN_ITEMS.md](OPEN_ITEMS.md)、
[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)、
[ER-003-A2-STRUCT-04_REPORT.md](ER-003-A2-STRUCT-04_REPORT.md)
