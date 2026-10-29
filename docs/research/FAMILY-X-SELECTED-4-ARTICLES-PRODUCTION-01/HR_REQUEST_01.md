# HR_REQUEST_01(FAMILY-X-SELECTED-4-ARTICLES-PRODUCTION-01 委任_01、2026-10-29)

## 区分(PM_GOVERNANCE 30-3)
**既存の承認済みProductionルートを正常に通過した結果のHR**(不具合・未実行工程によるHRではない)。4記事とも、正式Production入口の本文生成(Research→Ledger→B3→W-1 Writer→Advanced→Standard)とscaffold stage(Part 2文法候補・KP候補・ニュアンス候補)を通過し、`--stage scaffold`が仕様どおりKP Human Review待機(rc=4、失敗ではない)で停止した。TTS以降は未実施。

## 30-2 必須7項目(共通)
1. 対象: 4記事(下表)のStandard(a2)/Advanced(b1b)。判断対象=学習項目の選定(KP・単語・文法・ニュアンス解説)。音声はまだ無い(TTS前)ので聴取判断はない。
2. 適用ルート: `er019_family_x_entertainment_production_runner_01.py`(本文)→`er019_family_x_audio_production_runner_01.py --stage scaffold`(`kp_backend=fulltext_p2`のKP review、Part 2文法`run_part2_candidates_x`、ニュアンス`run_nuance_candidates_x`)。CURRENT_SPEC「学習項目選定フォームv3」節・「ニュアンス解説」節。
3. 通過工程と判定: 各記事のRUNTIME_EVIDENCE_01.md参照(時刻・model・費用)。
4. 救済処理: 本文段のRisk Flaggerは非Blocking(4条件逐次、全件実行)。B3 M1(中核数値)再実行=④のみ1回発動(既存機構、storyline_b3_attempt1へ退避)。KP段のGate除外→補完(backfill)・gloss再整合・canonicalization再判定は②(Std/Adv)等で既存機構が自動発動(依頼書「Gateで除外された候補」欄)。LR/ASR/TTS retryは本段に存在しない(TTS前)。
5. HRに至った直接原因: 仕様上、KP・文法・ニュアンスの選定はHuman判断が必須(自動確定は明示の不在宣言のみ)。
6. 残る自動救済: なし(選定はHumanの仕事)。
7. 判断依頼: 下記の各フォームで、Standard/Advancedそれぞれ ①KP(最大3)・単語(最大5、KP含む)・文法(最大1)・ニュアンス解説(採用/不採用)を選び『選定結果をコピー』またはChatGPT送信で返信。AI推奨のまま良ければ『AI推奨でOK』と書くだけでも可(推奨は各表の`AI推奨`列)。

## フォームURL(同一フォーム、記事直リンク)

| # | 記事 | Standard | Advanced |
|---|---|---|---|
| ② | 部屋は少し散らかっている方が、家族はうまくいく？ | https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/?a=untidiness_family_resource__a2 | https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/?a=untidiness_family_resource__b1b |
| ④ | AIに勧められた商品、気づかないうちに選ばされている？ | https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/?a=ai_chat_sponsored_persuasion__a2 | https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/?a=ai_chat_sponsored_persuasion__b1b |
| ⑨ | AIペットは、たまごっちの次のブームになる？ | https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/?a=meta_waddle_world__a2 | https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/?a=meta_waddle_world__b1b |
| ⑭ | 地球の外にある天体、光だけでどこまで探せる？ | https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/?a=jwst_mystery_emission_line__a2 | https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/?a=jwst_mystery_emission_line__b1b |


---
## ② 部屋は少し散らかっている方が、家族はうまくいく？
- 本文タイトル(JA): 「出しっぱなし」裁判、開廷します / (EN): The Trial of “Leaving Things Out” Is Now in Session
- 原記事/一次情報: `SOURCE_IDENTIFICATION_01.md`

### ② Standard
- フォーム: https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/?a=untidiness_family_resource__a2
- KP(フレーズ)候補: hear it out(最後まで話を聞く)★ / take points away from(～から点を差し引く)★ / make life work(暮らしをうまく回す)★ / need another look(改めて見直す必要がある)
- 単語候補: verdict(結論) / clutter(散らかった物) / supplement(サプリメント) / scorecard(採点の基準) / charge(非難)
- 文法候補[1]: the＋比較級の相関構文 — 例: A scorecard might say, “The fewer things you can see, the better.”
- ニュアンス解説(全文): **Not so fast.** — 判断や行動を急がせない、口語的な制止の含み
  - 本文の英文: But the court says, “Not so fast.” This supplement may need a lawyer to speak for it.
  - 日本語訳: しかし裁判所は「ちょっと待った」と言います。このサプリメントには、代わりに弁護してくれる人が必要かもしれません。
  - 解説: “Not so fast.” は文字どおり「速くない」ではなく、「まだそう決めるのは早い」「ちょっと待って」という制止です。ここでは片づける側の要求をすぐに通さず、別の事情も聞こうという反論の合図になっています。単に相手を止める “Wait!” と比べると、判断や結論を急ぐなという含みが出ます。強い怒りというより、会話をいったん止める口語的な言い方です。
  - 重複判定: 暫定選定のKey Phrase・Wordとは学習上の焦点が別と判定しました。

### ② Advanced
- フォーム: https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/?a=untidiness_family_resource__b1b
- KP(フレーズ)候補: apply to every household(すべての家庭に当てはまる)★ / turn into an interrogation(尋問になる)★ / hear it out(言い分を最後まで聞く)★ / the participant's own explanation(参加者本人の説明) / what it helps with(何に役立つのか) / demand its removal(それを取り除くよう要求する) / Now in Session(ただいま開廷中)
- 単語候補: clutter(物が散らかった状態) / verdict(結論) / prosecutor(検察官) / contribution(役立つ働き) / dismiss(退ける)
- 文法候補[1]: 長い主語 — 例: A scorecard that says “the fewer things in sight, the better” could end up taking points away from the ways each home has found to make life work.
- ニュアンス解説(全文): **isn’t always** — 「いつも〜とは限らない」という限定的な否定
  - 本文の英文: The study offers a different way to look at clutter: it isn’t always a personal failure, and it can also support daily life.
  - 日本語訳: この研究は、散らかりを別の見方で捉える方法を示している。散らかりは必ずしも個人の失敗ではなく、日々の暮らしを支えることもある。
  - 解説: “isn’t always a personal failure” は「散らかりは決して失敗ではない」ではなく、「失敗と見なせない場合もある」という限定的な言い方です。たとえば “clutter is never a personal failure” なら全面的な否定になり、本文より強い主張です。ここでは、片づけの価値を否定せず、暮らしを支える場合もあるという見方を加えています。
  - 重複判定: 暫定選定のKey Phrase・Wordとは学習上の焦点が別と判定しました。

---
## ④ AIに勧められた商品、気づかないうちに選ばされている？
- 本文タイトル(JA): そのおすすめ、AIの「お仕事」は何ですか？ / (EN): What Is the AI’s “Job” When It Makes a Recommendation?
- 原記事/一次情報: `SOURCE_IDENTIFICATION_01.md`

### ④ Standard
- フォーム: https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/?a=ai_chat_sponsored_persuasion__a2
- KP(フレーズ)候補: draw attention to(～に注意を向けさせる)★ / apply to real purchases(実際の買い物にも当てはまる)★ / pick at random(無作為に選ぶ)★
- 単語候補: persuade(説得する) / promoted(宣伝対象の) / neutral(偏りのない) / estimate(推定する)
- 文法候補[1]: 比較級とwhen節による比較基準 — 例: This was more often than when the book was only near the top of the search results.
- 文法候補[2]: 比較級とwhen節による比較基準 — 例: It was also more often than when chat-based AI gave a neutral description.
- ニュアンス解説(全文): **too soon to say** — 結論を否定せず、判断するには証拠が足りないと示す
  - 本文の英文: But it is too soon to say, “AI is now the greatest salesperson!” The experiment looked at one limited situation: choosing e-books.
  - 日本語訳: しかし、「AIは今や最高のセールスマンだ」と言うのはまだ早すぎます。この実験が見たのは、電子書籍を選ぶという限られた状況でした。
  - 解説: ここでの too soon to say は、単に「言うタイミングが早い」というより、「今ある証拠だけでは、その結論を出すには不十分」という慎重な姿勢を表します。「AIは最高のセールスマンではない」と否定しているわけではなく、今後そうなる可能性を残しています。たとえば「That is false」と言えば、結論そのものを否定する印象になります。
  - 重複判定: 暫定選定のKey Phrase・Wordとは学習上の焦点が別と判定しました。

### ④ Advanced
- フォーム: https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/?a=ai_chat_sponsored_persuasion__b1b
- KP(フレーズ)候補: play favorites(えこひいきする)★ / capture all that complexity(複雑な事情をすべて捉える)★ / a different script(別の指示)★ / choose at random(無作為に選ぶ) / what stands out(際立っている点) / in a news flash(ニュース速報で) / a prominent spot(人目につく位置)
- 単語候補: persuasive(説得を目的とした) / motive(行動の理由) / placement(掲載される位置) / estimate(およその値を出す) / sponsored(スポンサー付きの)
- 文法候補[1]: 疑似分裂文 — 例: But what stands out in this experiment is the guide’s task, not just its seat.
- 文法候補[2]: 従属節内の疑似分裂文 — 例: It is as if we were looking at a map of a store’s layout, then realized that what we should be looking at was the work instructions given to the staff.
- ニュアンス解説(全文): **may want to** — 希望の推測ではなく、控えめな助言を表す用法
  - 本文の英文: When you ask for help choosing your next book, you may want to pay a little attention not only to the book’s summary, but also to what the guide has been asked to do.
  - 日本語訳: 次に読む本選びを手伝ってもらうときは、本のあらすじだけでなく、案内役が何をするよう求められているかにも少し注意を向けてみるとよいかもしれません。
  - 解説: ここでの may want to は、相手がそう望んでいるかを推測するというより、提案を控えめに伝える言い方です。たとえば You should pay attention なら「注意すべきだ」と比較的強く促しますが、本文の you may want to pay a little attention は、読者に選択の余地を残します。直訳して「注意したいかもしれない」と受け取らないのがポイントです。
  - 重複判定: 暫定選定のKey Phrase・Wordとは学習上の焦点が別と判定しました。

---
## ⑨ AIペットは、たまごっちの次のブームになる？
- 本文タイトル(JA): 今日の日記、執筆担当はペットです / (EN): Today's Diary Is Written by a Pet
- 原記事/一次情報: `SOURCE_IDENTIFICATION_01.md`

### ⑨ Standard
- フォーム: https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/?a=meta_waddle_world__a2
- KP(フレーズ)候補: reach a dead end(行き詰まる)★ / write it up(文章にまとめる)★ / point of view(視点)★
- 単語候補: account(話) / ordinary(ありふれた) / description(説明文) / storyteller(語り手) / doodle(気軽に描いた絵)
- 文法候補: 0件(Part 2抽出が該当構文なしと判定=`no_feature_paras`全段落。既存仕様の『候補0件』経路。フォーム上は文法欄が出ません)
- ニュアンス解説: 候補なし(モデルが『該当なし』を返却=NO_CANDIDATE。既存仕様どおり提示0件・待機なし)

### ⑨ Advanced
- フォーム: https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/?a=meta_waddle_world__b1b
- KP(フレーズ)候補: hit a dead end(行き詰まる)★ / take the storyteller's seat(語り手になる)★ / write it up properly(きちんと文章にまとめる)★
- 単語候補: editorial(編集に関する) / doodle(気軽に描いた絵) / alongside(〜に添えて)
- 文法候補[1]: What節を主語にした疑似分裂文 — 例: What makes it interesting isn’t a promise that each result will be good, but the idea of changing who tells the diary.
- 文法候補[2]: 不定代名詞を修飾する後置形容詞句 — 例: Did anything even happen worth writing about?
- ニュアンス解説(全文): **for now** — 現時点の役割を暫定的なものとして示す
  - 本文の英文: For now, the human’s job is simply to bring in the story of the day.
  - 日本語訳: 今のところ、人間の役目はその日の出来事を持ち込むことだけです。
  - 解説: 「for now」は単なる「今」より、現時点での暫定的な状態や方針という含みを持ちます。ここでは、人間の役割をこの段階では素材を持ち込むことに限って述べ、今後もずっとそうだとは断定していません。ただし、必ず変更されるという予告でもありません。たとえば “The human’s job is...” だけなら、一般的・恒常的な説明に聞こえやすくなります。
  - 重複判定: 暫定選定のKey Phrase・Wordとは学習上の焦点が別と判定しました。

---
## ⑭ 地球の外にある天体、光だけでどこまで探せる？
- 本文タイトル(JA): 写真にはいない。でも光は届く！ JWSTの「宇宙捜査ファイル」 / (EN): Not in the Picture, but Its Light Reaches Us! JWST’s “Cosmic Case File”
- 原記事/一次情報: `SOURCE_IDENTIFICATION_01.md`

### ⑭ Standard
- フォーム: https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/?a=jwst_mystery_emission_line__a2
- KP(フレーズ)候補: equivalent width(光の線の特徴を表す幅)★ / a lower limit(下限)★ / narrow down the source(発生源を絞り込む)★ / turn the usual steps around(いつもの手順を逆にする) / line's absence from images(画像に光の線が写っていないこと) / show up(現れる)
- 単語候補: wavelength(波長) / estimate(およその値を出す) / investigation(調査) / frustrate(いら立たせる) / overlap(一部が重なる)
- 文法候補[1]: 比較基準が省略された比較級 — 例: How much closer will the next observation bring us to the source of this voice?
- 文法候補[2]: 長い動名詞句主語 — 例: Not seeing something in an image does not mean it does not exist.
- ニュアンス解説(全文): **could not confirm** — 「確認できない」と「存在しないと確認した」の区別
  - 本文の英文: They could not confirm that an image showed an object where the line was.
  - 日本語訳: 画像が、光の線があった場所に天体を示しているとは確認できませんでした。
  - 解説: could not confirm that ... は「…ではないと確認した」ではなく、「…だと確かめられなかった」という意味です。否定されているのは確認できたということ自体で、対象が存在しないとは断定していません。たとえば They confirmed that no object was there. なら「そこに天体がないと確認した」です。本文では、画像で確認できないことと、存在しないことを慎重に区別しています。
  - 重複判定: 暫定選定のKey Phrase・Wordとは学習上の焦点が別と判定しました。

### ⑭ Advanced
- フォーム: https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/?a=jwst_mystery_emission_line__b1b
- KP(フレーズ)候補: equivalent width(スペクトル線の強さを示す等価幅)★ / narrow down the source(発生源を絞り込む)★ / set a lower limit(下限を決める)★ / take an unexpected turn(思わぬ展開になる) / point-like object(点のように見える物体)
- 単語候補: wavelength(波長) / celestial(天体の) / absence(見当たらないこと) / investigation(調査) / frustrate(いら立たせる)
- 文法候補[1]: 疑似分裂文 — 例: What they could not confirm was an image showing an object at the line’s position.
- 文法候補[2]: 比較基準が明示されていない比較級 — 例: How much closer will the next observation get us to the source of this voice?
- ニュアンス解説(全文): **too soon to announce** — 「時期尚早」が、現時点での証拠への慎重さを示す
  - 本文の英文: Even so, it was too soon to announce, “A celestial object with no visible form has been found!”
  - 日本語訳: それでも、「目に見える形のない天体が見つかった」と発表するには時期尚早だった。
  - 解説: ここでの too soon は、発表する能力がないという意味ではなく、今ある証拠だけで結論を公表するのは早すぎる、という慎重な判断を示します。たとえば could not announce なら「発表できなかった」と、能力や事情による不可能さにも聞こえます。too soon は「今はまだ早いが、今後なら発表できるかもしれない」という余地を残します。
  - 重複判定: 暫定選定のKey Phrase・Wordとは学習上の焦点が別と判定しました。

(★=AI推奨KP。文法の解説全文・AI選定理由はフォームに表示)

## 公開確認
フォーム(index.html)と8データJSON+articles.jsonをpush(47141553c)。GitHub Pages deploy完了後 2026-10-29 22:06 に9URL(上記フォーム直リンク+data/*.json 8件+articles.json)すべてHTTP 200を確認(curl)。
