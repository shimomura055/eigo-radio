# comparison_meta_b1.md
管理ID: NEWS-FAMILY-X-POINTLESS-TRIAL-01 / Phase B
対象: Meta記事、B1(Advanced)レベルのみ。Family A(既存Point構造)と
Family X(本Trial、Point構造廃止・3分割)の構造比較。

Family Xの`comment_4`はASR Validation 3回とも「main point together」が
「main points together」(単数/複数の揺れ)としてASR書き起こされ、
Human Review Lock(ER-011-HUMAN-REVIEW-COST-GUARD-01)により
HUMAN_REVIEW_LOCKEDで終端した。既存の安全装置(Human Review Lock)を
Sonnet判断で回避・上書きしていないため、full episode assembly(1本の
wavファイル)は未完成(GATE_BLOCKED)。個別segment(10件中9件VALIDATED、
1件HUMAN_REVIEW_LOCKED)は全てplayer.html経由で試聴可能。

---

## 1. segment列比較(非pause行のみ)

### Family A(既存、meta/b1b、`timeline.json`実測)
| # | segment | 開始(s) | 長さ(s) |
|---|---|---|---|
| 1 | Intro | 0.00 | 10.74 |
| 2 | Welcome (Charon) | 10.74 | 2.05 |
| 3 | Topic intro (Charon) | 13.29 | 6.89 |
| 4 | Notification 1 | 20.83 | 2.04 |
| 5 | Preview intro (Charon) | 23.27 | 1.48 |
| 6 | Preview (Charon) | 25.40 | 19.94 |
| 7 | Notification 2 | 45.84 | 2.04 |
| 8 | Key phrases intro (Charon) | 48.28 | 2.69 |
| 9 | Key Phrase 1 | 51.47 | 9.36 |
| 10 | Key Phrase 2 | 60.83 | 7.78 |
| 11 | Key Phrase 3 | 68.62 | 9.75 |
| 12 | Key Phrase 4 | 78.37 | 7.49 |
| 13 | Key Phrase 5 | 85.86 | 8.79 |
| 14 | Notification 3 | 94.66 | 2.04 |
| 15 | Full story intro (Charon) | 97.10 | 2.17 |
| 16 | Comment 1 (Charon) | 100.07 | 4.33 |
| 17 | Full Story Part 1 (Aoede) | 105.20 | 23.02 |
| 18 | Comment 2 (Charon) | 129.02 | 7.93 |
| 19 | Full Story Part 2 (Aoede) | 137.75 | 27.49 |
| 20 | Comment 3 (Charon, Bridge) | 166.04 | 10.72 |
| 21 | Point Notification (One cue) | 177.26 | 1.78 |
| 22 | Point One semantic heading | 179.04 | 3.21 |
| 23 | Point One (Aoede) | 182.95 | 20.06 |
| 24 | Point Notification (Two cue) | 203.51 | 1.78 |
| 25 | Point Two semantic heading | 205.29 | 3.57 |
| 26 | Point Two (Aoede) | 209.56 | 44.36 |
| 27 | Comment 4 (Charon) | 254.72 | 13.30 |
| 28 | In One Line (Aoede) | 268.82 | 6.17 |
| 29 | Outro (Charon) | 275.79 | 6.14 |

**segment数(非pause)=29、総尺=281.93秒(約4分42秒)**

### Family X(本Trial、meta/b1b、個別segment実測+pause定数からの推定合計)
| # | segment | 長さ(s) | 備考 |
|---|---|---|---|
| 1 | Intro | 10.74 | Family Aと同一固定音源 |
| 2 | Welcome (Charon) | 2.051 | Master Audio Store cache hit(Family Aと同一音声、追加コスト¥0) |
| 3 | Topic intro (Charon) | 8.121 | 新規生成(テキストはFamily Aと同文、TTS結果の揺れで秒数は別) |
| 4 | Notification 1 | 2.04 | Family Aと同一固定音源 |
| 5 | Preview intro (Charon) | 1.481 | Master Audio Store cache hit |
| 6 | Preview (Charon) | 17.411 | 新規生成(Point節を含まないarticle_textを参考context化) |
| 7 | Full story intro (Charon) | 2.171 | Master Audio Store cache hit |
| 8 | Comment 1 (Charon) | 3.611 | 既存b1s.COMMENT_1_ROLEをそのまま流用 |
| 9 | Full Story Part 1 (Aoede) | 12.371 | 3分割part1(39語) |
| 10 | Comment 2 (Charon) | 7.441 | 既存b1s.COMMENT_2_ROLEをそのまま流用 |
| 11 | Full Story Part 2 (Aoede) | 15.701 | 3分割part2(40語) |
| 12 | Comment 3 (Charon, Bridge to Part 3) | 11.561 | 新role(FAMILY_X_COMMENT_3_ROLE) |
| 13 | Full Story Part 3 (Aoede) | 20.251 | 3分割part3(48語)★新規segment |
| 14 | Comment 4 (Charon) | 10.331 | 新role(FAMILY_X_COMMENT_4_ROLE)。**HUMAN_REVIEW_LOCKED(下記2節参照)** |
| 15 | In One Line (Aoede) | 6.331 | Family A版と同一テキスト |
| 16 | Outro | 6.14 | Family Aと同一固定音源(推定、Intro/Outroは共通mp3) |

**segment数(非pause)=16(Family A比 -13: Notification2/Key phrases intro/
Key Phrase1-5/Notification3/Point Notification×2/Point見出し×2/
Point本文×2 を削除、Full Story Part 3を追加)。
pause定数(AOEDE_TO_CHARON=CHARON_TO_AOEDE=IN_ONE_LINE_TO_OUTRO=0.8秒)を
含めた推定総尺=約147.7秒(約2分28秒)、Family A比 約52%(-134秒、
主にKey Phrase block約38秒とPoint block約74秒の削除による)。**

---

## 2. Comment 3・4の全文(新旧比較)

### Comment 3
- Family A(既存、"Bridge to Points"役割、実測生成テキスト):
  > "This story shows a gap between how the phone service appeared
  > and how it worked in testing. Now, let's look more closely at
  > that gap and the concerns it brought up."
- Family X(本Trial、"Bridge to Part 3"役割、実測生成テキスト):
  > "Meta was preparing a service that would let its AI make phone
  > calls for users. The AI was called Muse. Now listen for what
  > people found when they looked more closely."

### Comment 4
- Family A(既存、"Point Recovery"役割、実測生成テキスト):
  > "So far, this story has raised two connected questions: how much
  > human help may be involved, and how much people know about it.
  > Now, let's bring these ideas together and hear the main point."
- Family X(本Trial、"Story Recovery"役割、実測生成テキスト):
  > "The service looked like AI, but the work behind it was not
  > always done by AI alone. Now, let's bring the main point
  > together."
  (注: 上記canonical textの"point"は一般的な英語表現"bring the main
  point together"であり、"Point One/Two"という構造ラベルではない。
  ただし3回のTTS/ASR試行すべてで、ASRが一貫して"points"[複数形]と
  書き起こし、既存のASR Validation/Human Review Lockが正しく作動し
  HUMAN_REVIEW_LOCKEDへ終端した。音声自体を実際に聴取して人間が判断
  する必要がある[3回分のattempt音声は`narration/attempts/comment_4_
  attempt{1,2,3}_englishstyleprefix.wav`に保存済み]。)

その他生成テキスト(Comment 1・2・Preview、既存role文言を無変更のまま
流用): `er019_output/family_x_pointless_trial_01/meta/b1b/b1_support_
texts.json`参照。

---

## 3. In One Line
Family A・Family Xとも同一テキスト(既存article.mdからそのまま流用、
新規生成なし): "AI may make the call, but people also need to know
who is really behind the voice."

---

## 4. Point解説の情報が失われたか(文単位の対照)

Family AのPoint One/Two本文(`parts.json`実測)とMain Story(part1〜3)を
文単位で照合した結果:

**Point One body**(「もう一人の演者がピアノの中に隠れていた」の比喩・
「人間の助けは必ずしも悪いことではない」という解説): **Main Storyには
一切含まれていない**。Main Story側にあるのは「AIだけが演じているように
見えた(The AI only appeared to be performing alone)」という一文のみで、
Point Oneはこれを「ピアノの中の演者」という比喩で敷衍し、「人間が
補助すること自体は問題ではない」という評価的解説を加えている。
**→ Family Xでは、この比喩と評価的解説は完全に失われる。**

**Point Two body**(プライバシー懸念・Meta従業員の懸念・機能一時停止の
事実・「誰が舞台裏にいるか」という結び): **Main Storyには一切含まれて
いない**。特に「Metaが機能を一時停止した」という事実は、この記事の
ニュース価値の核心部分の一つだが、Main Story(part1〜3)のどの文にも
現れない。
**→ Family Xでは、プライバシー懸念とMetaによる機能一時停止という
事実そのものが失われる(比喩表現だけでなく、ニュースFactの欠落)。**

**結論**: この記事(Meta)に関しては、Point One/Twoは「本文の言い換え・
重複」ではなく、本文が述べていない独自の情報(特にPoint Twoの
「機能一時停止」という事実)を担っていた。ユーザー指示「Point節は
内容ごと破棄する」に厳密に従って実装したため、本Trialの音声からは
この情報が失われている。これは実装ミスではなく、指示どおりの結果で
あることを明示的に報告する(§6でも改めて記載)。

---

## 5. 重複の減少
Family AのComment 3(Bridge to Points)は「これからPointを聞く」ことを
前提とした橋渡し文言、Comment 4(Point Recovery)は「2つのPointの内容を
軽く回収する」文言だった。Family XのComment 3/4はPoint前提を持たず、
「本文の第1部・第2部の核心を整理し第3部へ」「本文全体を回収しIn One
Lineへ」という素直な役割になっており、Point One/Two本文との重複や
橋渡し専用の言い回し("Bridge to Points"等)は生じていない。

---

## 6. 旧Point誘導表現の残存grep結果
`grep -rniE "point one|point two|point 1|point 2|第一に|第二に"` を
`er019_output/family_x_pointless_trial_01/meta/b1b/{parts.json,
b1_support_texts.json}` に対して実行: **0件ヒット**(構造ラベルとしての
"Point One/Two"は一切残存していない)。Comment 4のcanonical textに
一般的な英語表現"point"(小文字、"bring the main point together")が
1件あるが、これは構造ラベルではなく通常の英語語彙(詳細は2節)。

---

## 7. 音声テンポ(合計秒数・segment数)
| | Family A | Family X |
|---|---|---|
| segment数(非pause) | 29 | 16 |
| 総尺(推定含む) | 281.93秒 | 約147.7秒(推定、comment_4は最終attempt音声の秒数を使用) |
| Key Phrase block | あり(5件、約38秒) | なし |
| Point block | あり(Notification×2+見出し×2+本文×2、約74秒) | なし |
| Full Story分割数 | 2(Part1/Part2) | 3(Part1/Part2/Part3) |

Family Xは音声テンポとしてはKey Phrase/Point blockの削除により
テンポが大幅に速まる(約52%の長さ)。一方、3分割後の1パートあたりの
長さ(12.4秒/15.7秒/20.3秒)はFamily AのPart1/2(23.0秒/27.5秒)より
短く、design書(A-3)で事前に指摘されていた「短くなる」懸念が実測でも
確認された(ただし極端に不自然な短さではない)。
