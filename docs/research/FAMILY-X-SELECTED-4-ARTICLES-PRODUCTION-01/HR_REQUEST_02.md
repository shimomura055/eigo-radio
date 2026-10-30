# HR_REQUEST_02(FAMILY-X-SELECTED-4-ARTICLES-PRODUCTION-01。NUANCE-CORNER-ABOLITION-01 委任_02で2026-10-30再出力: ニュアンス解説欄を除去した版。HR_REQUEST_01とフォームdataの旧版[ニュアンス欄つき]は無効)

## 区分(PM_GOVERNANCE 30-3)
**既存の承認済みProductionルートを正常に通過した結果のHR**(不具合・未実行工程によるHRではない)。4記事とも、正式Production入口の本文生成(Research→Ledger→B3→W-1 Writer→Advanced→Standard)とscaffold stage(Part 2文法候補・KP候補)を通過し、`--stage scaffold`が仕様どおりKP Human Review待機(rc=4、失敗ではない)で停止した。TTS以降は未実施。

## 30-2 必須7項目(共通)
1. 対象: 4記事(下表)のStandard(a2)/Advanced(b1b)。判断対象=学習項目の選定(KP・単語・文法)。音声はまだ無い(TTS前)ので聴取判断はない。
2. 適用ルート: `er019_family_x_entertainment_production_runner_01.py`(本文)→`er019_family_x_audio_production_runner_01.py --stage scaffold`(`kp_backend=fulltext_p2`のKP review、Part 2文法`run_part2_candidates_x`)。CURRENT_SPEC「学習項目選定フォームv3」節。(ニュアンス解説コーナーは2026-10-30に廃止)
3. 通過工程と判定: 各記事のRUNTIME_EVIDENCE_01.md参照(時刻・model・費用)。
4. 救済処理: 本文段のRisk Flaggerは非Blocking(4条件逐次、全件実行)。B3 M1(中核数値)再実行=④のみ1回発動(既存機構、storyline_b3_attempt1へ退避)。KP段のGate除外→補完(backfill)・gloss再整合・canonicalization再判定は②(Std/Adv)等で既存機構が自動発動(依頼書「Gateで除外された候補」欄)。LR/ASR/TTS retryは本段に存在しない(TTS前)。
5. HRに至った直接原因: 仕様上、KP・文法の選定はHuman判断が必須(自動確定は明示の不在宣言のみ)。
6. 残る自動救済: なし(選定はHumanの仕事)。
7. 判断依頼: 下記の各フォームで、Standard/Advancedそれぞれ ①KP(最大3)・単語(最大5、KP含む)・文法(最大1)を選び『選定結果をコピー』またはChatGPT送信で返信。AI推奨のまま良ければ『AI推奨でOK』と書くだけでも可(推奨は各表の`AI推奨`列)。

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

### ② Advanced
- フォーム: https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/?a=untidiness_family_resource__b1b
- KP(フレーズ)候補: apply to every household(すべての家庭に当てはまる)★ / turn into an interrogation(尋問になる)★ / hear it out(言い分を最後まで聞く)★ / the participant's own explanation(参加者本人の説明) / what it helps with(何に役立つのか) / demand its removal(それを取り除くよう要求する) / Now in Session(ただいま開廷中)
- 単語候補: clutter(物が散らかった状態) / verdict(結論) / prosecutor(検察官) / contribution(役立つ働き) / dismiss(退ける)
- 文法候補[1]: 長い主語 — 例: A scorecard that says “the fewer things in sight, the better” could end up taking points away from the ways each home has found to make life work.

---
## ④ AIに勧められた商品、気づかないうちに選ばされている？
- 本文タイトル(JA): 「広告です」と名乗るAI。それでも欲しくなる？ / (EN): An AI That Says “This Is an Ad”—Would You Still Want It?
- 原記事/一次情報: `SOURCE_IDENTIFICATION_01.md`

### ④ Standard
- フォーム: https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/?a=ai_chat_sponsored_persuasion__a2
- KP(フレーズ)候補: confirm a clear fall(はっきりした減少を確認する)★ / results suggest(結果から～と考えられる)★ / sales pitch(売り込み)★ / favor one product(特定の商品を推す) / blow a whistle(警報を鳴らす) / let the advice through(助言を受け入れる)
- 単語候補: persuasion(説得) / persuade(納得させる) / sponsored(広告主に宣伝されている)
- 文法候補[1]: 疑似分裂文 — 例: What is more interesting is that an ad label and the effect of a conversation may work in different ways.
- 文法候補[2]: 長い動名詞句を主語とする文 — 例: Noticing an ad and stopping yourself from wanting the product seem like two different things.

### ④ Advanced
- フォーム: https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/?a=ai_chat_sponsored_persuasion__b1b
- KP(フレーズ)候補: put the brakes on(抑える)★ / whose interests the conversation serves(会話が誰の利益になるのか)★ / Sales pitch(売り込み文句)★ / confirm a clear drop(明らかな減少を確認する) / rate at which(起こる割合) / or so it seemed(そう見えたのだが)
- 単語候補: persuasion(説得) / biased(偏った) / persuade(説得する) / complications(複雑な要素) / sponsored(スポンサーの支援を受けた)
- 文法候補[1]: What節を用いた疑似分裂文 — 例: What’s more interesting is that the ad label and the effect of the conversation may work in different ways.
- 文法候補[2]: 並列した動名詞句を含む長い主語 — 例: Spotting an ad and putting the brakes on wanting something seem to be two separate things.

---
## ⑨ AIペットは、たまごっちの次のブームになる？
- 本文タイトル(JA): AIペットは無料。でも、飼い主の一日は24時間です / (EN): AI Pets Are Free. But Their Owners Still Have Only 24 Hours a Day
- 原記事/一次情報: `SOURCE_IDENTIFICATION_01.md`

### ⑨ Standard
- フォーム: https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/?a=meta_waddle_world__a2
- KP(フレーズ)候補: At the time of writing(執筆時点で)★ / make room for(～のための時間を作る)★ / side by side(隣り合わせに)★ / early step toward(～への初めの一歩) / gaps in a busy day(忙しい一日の合間にできる空き時間)
- 単語候補: subscription(定額制の契約) / usefulness(役立ち具合) / prediction(予測) / craze(大ブーム) / resident(住人)
- 文法候補[1]: 比較級の比較基準が明示されない表現 — 例: An AI pet may matter less to adults for what it can do.
- 文法候補[2]: 比較級の比較基準が明示されない表現 — 例: It may matter more if they want to make room for one during the gaps in a busy day.

### ⑨ Advanced
- フォーム: https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/?a=meta_waddle_world__b1b
- KP(フレーズ)候補: pore over(じっくり調べる)★ / make room for(～のために時間を作る)★ / by the time of reporting(報道時点までに)★ / on the scale of(～並みの規模で) / an open question(まだ答えが出ていない問題) / in the gaps(ちょっとした空き時間に)
- 単語候補: subscription(定額制の契約) / latter(後者) / craze(大流行) / appeal(魅力) / usefulness(役に立つ度合い)
- 文法候補[1]: 強調構文（it-cleft） — 例: This time, it’s adults who are being asked whether they want to welcome a pet.
- 文法候補[2]: 疑問詞節を主語にする構文 — 例: When it will become available in Japan and other places had not been announced by the time of reporting.

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

### ⑭ Advanced
- フォーム: https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/?a=jwst_mystery_emission_line__b1b
- KP(フレーズ)候補: equivalent width(スペクトル線の強さを示す等価幅)★ / narrow down the source(発生源を絞り込む)★ / set a lower limit(下限を決める)★ / take an unexpected turn(思わぬ展開になる) / point-like object(点のように見える物体)
- 単語候補: wavelength(波長) / celestial(天体の) / absence(見当たらないこと) / investigation(調査) / frustrate(いら立たせる)
- 文法候補[1]: 疑似分裂文 — 例: What they could not confirm was an image showing an object at the line’s position.
- 文法候補[2]: 比較基準が明示されていない比較級 — 例: How much closer will the next observation get us to the source of this voice?

(★=AI推奨KP。文法の解説全文・AI選定理由はフォームに表示)
