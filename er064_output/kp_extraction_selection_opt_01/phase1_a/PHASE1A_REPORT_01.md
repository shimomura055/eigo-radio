# KP-EXTRACTION-SELECTION-OPTIMIZATION-01 委任_01A (Phase 1-A) レポート

日付: 2026-10-13 / 費用: JPY0(LLM/TTS/ASR呼出0。Wiktionary公開API[無料]のみ、既存関数の1回50件・待ち1.5秒を踏襲) / Status: Phase 1-A結果報告(**VALIDATEDではない**。採用判断なし。Production code/Prompt無変更、Trial専用 `er064_kp_opt_01_upstream_*.py`)
使用モデル: LLM不使用(該当なし)。対象記事: Coffee v5 Std/Adv + Family X既存4テーマ(meta run_03 / hormuz run_02 / small_bag run_02 / semiconductor devconfirm)×Std/Adv = 10 article-level。
再現性: 照会結果は `wiktionary_snapshot_01.json`(照会ts付き、4,169+853+unigram)に固定し、再生は全てsnapshot注入(replayではネットワーク禁止をtestで確認)。再生は実関数 `core.run_stage1_and_shortlist` をmonkeypatch(context manager内のみ、終了時復元)で呼ぶ=除外Gate→名詞句判定→重複除去→capまで実コード。現行構成の再生がCoffee v5 Advの保存済みrun(phrase/important候補列)と一致することも確認。

## 1. U1 vs 照会予算拡大 vs 両方(記事別は `u1_vs_budget_expand_01.json`)

「生存hit」=Wiktionary multiword hitが除外Gate・名詞句判定・重複除去を通ったもの。GT(プール全件を照会した場合)= 103件(10 article-level合計)。

| 構成 | 照会件数/記事Lv平均 | 生存hit合計 | 新規(vs現行) | 失う(vs現行) | GT取りこぼし | 推定時間/記事Lv |
|---|---|---|---|---|---|---|
| 現行 (予算60) | 60 | 11 | - | - | 92 | 約10秒(2call) |
| U1 k=10(2語優先、固有名詞込み) | 60 | 11 | +1 (`time lag`) | -1 (`other end`) | 92 | 約10秒 |
| U1np k=10(固有名詞を優先しない) | 60 | 11 | +1 | -1 | 92 | 約10秒 |
| U1np k=20 | 60 | 9 | +1 | -3 | 94 | 約10秒 |
| U1np3 k=10(+3語優先) | 60 | 8 | +1 | -4 | 95 | 約10秒 |
| 現行順 予算120 | 120 | 37 | +26 | 0 | 66 | 約15秒 |
| U1np k=10 予算120(=併用の部分予算) | 120 | 33 | +22 | 0 | 70 | 約15秒 |
| **予算拡大**(2語全件+3語上限100) | 約369 | **95** | **+84** | **0** | 8 | 約43秒(8call) |
| 両方(U1np+拡大) | 約369 | 95 | +84 | 0 | 8 | 約43秒(順序は全件照会では無効) |

- 固有名詞の扱い: U1の優先枠で固有名詞らしいtoken(非文頭の大文字等のヒューリスティック)を含む2語を外す(np)と、込みと同結果。10記事では固有名詞2語が優先枠を食い潰す害は出なかったが、`Brent`/`Strait`等が枠を使うリスクは構造上残る。
- `time lag`型の取りこぼし(「現行shortlistのword候補を含むのに照会窓外で落ちたhit」): Before=3件(Coffee Adv `time lag`、hormuz Std/Adv `strait of hormuz`)→ After(拡大)=2件(`strait of hormuz` x2、3語上限100の外)。`time lag`はU1でも拡大でも回収(76位→優先窓内)。
- 拡大で増えた84hitの内訳: important判定16、demoted(名詞句判定で外れ一般的な短い複数語)68。`time lag`/`shoulder bag`/`stage crew`/`report card`/`mental calculator`は有益寄りだが、`the same`/`at least`/`how long`/`for sale`/`want to`/`close to`/`call it`等の一般語が大半(Wiktionaryのmultiword categoryに載るがtoo_easy Gateを通過する)。
- 実時間・rate limit: 照会は計102 call(2語/3語84call+小文字variant 18call)、累計574秒。**HTTP 429が10回発生**(約10%のcall)。既存関数の5回backoff(Retry-After/指数)で全て回復、失敗0。429待ちを含む1call平均4.07秒(実測、API費用ではなくWiktionary待ち時間)。拡大は記事あたり約43秒(推定=8call×4.07+7×1.5)で、現行の約10秒より約33秒増。
- cache効果: 10 article-levelの拡大照会合計3,694件 vs 重複除去後2,590件(約30%削減)。本番で記事を跨ぐ永続cacheを持てば効果あり(今回はsnapshotがcacheを兼ねる)。
- 小文字variant: 文頭大文字の表記(例 `Even if`)で照会する現行は、小文字表記ならhitする13種を取りこぼす(`even if`/`this time`/`how much`/`in fashion`等。ほぼ一般語で優先度低)。照会前に小文字化する案の効果は小さい。

## 2. shortlist到達の全体再生(`shortlist_replay_01.json`)

- **Coffee Adv**: 現行shortlist=`lag`のみ(32件、`time lag`なし) → U1np(予算60据置)でshortlistに`time lag`が入る(33件)、`lag`は残る(U2なし) → 拡大でも`time lag`入り → **U2 Tier-H(含む側が辞書登録hit、`lag`の全出現が`time lag`内)で`lag`が除外**(`time lag`はimportant判定=名詞句、`lag`はTier-H除外)。Tier-S注釈のみ(U2 tierS)では`lag`は残り`time lag`に`contains`系注釈が付く。Std v5原稿には"time lag"がなく該当しない。
- Tier-Hが10記事で発火したのは2件のみ(`lag`⊂`time lag`、semi Adv `calculator`⊂`mental calculator`)。Tier-S注釈対象(`bean prices`⊂`coffee bean prices`、`tags`⊂`price tag`等)は各記事数件。
- `demoted_to_phrase`のcap切り(`u4_demoted_cap_01.json`): 現行のcap15で切られるdemoted hitは、拡大時にCoffee Adv 11件(`for sale`/`in stock`/`how long`等)、meta Adv 3、semi Adv 3、Coffee Std 2(計19)。cap20で7件(Coffee Advのみ)へ減り、cap20+整列(demotedを`(-db_match_count, canonical)`の通常順へ戻す)で4件。整列のみ(cap15)は計11件、出現順タイブレークは計9件で、いずれもcap20より切り捨てが残り、さらに通常phraseの脱落が増える(removed 18→26/28)。
- shortlist件数・token(候補行+SENTENCE REFERENCE、UTF-8 bytes/4の近似、10 article-level平均、現行=約1,358token):
  現行22.7件 / U1np 22.8件(+3.5token) / 拡大27.4件(+184) / 拡大+U2(H+S)(+199) / 拡大+U3(+183) / 拡大+cap20(28.7件,+235) / **improved=拡大+U2+U3+U4(cap20+整列) 28.6件(+247token、約+18%)** / **precision_guarded_improved 23.3件(+51token、約+4%)**。
- 拡大で増えるhitは、wordの最小枠(word_min=5)に押されて希少単語を押し出す: improvedで外れるword例 `twist`/`explaining`/`inappropriate`/`negotiate`/`curtain`/`crude`/`refuses`/`runway`/`lip`/`proudly`/`vanished`/`clearer`/`luggage`(10記事で計約18件)。precision_guarded(窓外のdemoted hitをphraseへ入れない。important判定hit=`time lag`等は通す)では押し出される希少単語は8件(`inappropriate`/`negotiate`/`crude`x2/`runway`/`lip`/`clearer`/`luggage`)に減り、shortlist増も+0.6件/記事に収まる。

## 3. U3断片検出(`u3_fragment_01.json`)

- U3(i) 閉じた語類のみの一致の除外: 10 article-levelで発火3件(Coffee Adv `at that`/`of a`、meta Std `of a`)、**全て断片で正当な成句の誤除外は0**。`as well`/`at all`/`in fact`/`of course`/`so far`/`on a regular basis`は既存の閉じた語類集合では対象外(testで確認)。
- ただし理論上の影響範囲: Wiktionary見出し16,317中、閉じた語類のみの2〜5語見出しは67件で、正当な定着表現を含む(`as if`/`as is`/`and so on`/`so be it`/`at will`/`as yet`/`about to`/`have to`/`there you are`等)。記事内にゲート前で出現するのは semi Std(`as if`,`have to`)、semi Adv(`have to`)、hormuz Adv(`or what`)だが、いずれも既存のtoo_easy Gateで先に落ちており生存候補にはならない=10記事での誤除外0。集合を`all/well/up/out/...`に広げると見出し169件になり`as well`/`at all`/`so far`/`by far`等が巻き込まれるため**拡張しない**(Step2の判断材料)。
- U3(ii) `fragment_risk`注釈(辞書未登録かつ先頭が冠詞/前置詞/助動詞等。置換なし): LLM抽出span 43種(Phase C/D extractor_raw全36 run)のうち6種に注釈: `in the ring`/`the two numbers in the ring`/`an unseen clock of its own`(真の断片寄り3)+`been behind price increases`/`had been behind price increases`/`has read the clock`(助動詞始まりで断片ではない3=ノイズ)。助動詞始まりを外せば注釈は3種で精度が上がる。登録済みの`in stock`は対象外。注意: これはLLM抽出span(Pkg E)に対するものでPkg U単独では`in the ring`型は回避できない(設計書どおり)。

## 4. Rule7 予測INVALIDリスト(`rule7_predicted_invalid_01.json`、修正なし)

`_PERSON_DEPENDENT_TO_GENERIC`(my/our/its/yours/theirs→`one's`のみ、目的格なし、myself/itself/ourselves/yourselves→なし)とcanonicalization Prompt(`one's/someone's/somebody's`、`someone/somebody/one`、`oneself`)を実validatorで総当たり(70組): **35組がINVALID予測**。主なもの:
- 所有格: `my/our/its/yours/theirs → someone's / somebody's`(Promptは許可、validatorは不許可)
- 目的格(表に無い): `me/him/her/them/us/it → someone/somebody`
- 主格: `i/we/it → someone/somebody/one`
- 再帰: `myself/itself/ourselves/yourselves → oneself`
- 活用+人称の同時変更: `holding its breath→hold one's breath`、`pulling my leg→pull one's leg`、`pumps its fist→pump one's fist`(語数同一・他token不変の条件に抵触)=3 span
- 実記事の候補(improved/current shortlist)で該当しうる: `calls it`/`call it`/`that's it`(目的格/it)と`your head`(語1件)。LLM抽出spanで該当しうる10種(`its own hidden clock`/`clock of its own`/`pumps its fist`/`holding its breath`/`pulling my leg`等)は`someone's`系の提案でINVALID予測。
- 人称表と無関係の既知INVALID: 活用形戻し(`been→be`)、辞書形の語追加(`loan against the future`)、過剰一般化(`one's own hidden clock`)。
- 是正候補(未適用、判断はユーザー/Fable): (i)表をPromptに合わせ拡張 / (ii)Promptを表に合わせ縮小(`its/my/our/yours/theirs`は`one's`のみ、目的格・再帰は対象外) / (iii)折衷(`my/our`のみ`someone's`許可、`its→someone's`は不許可)。Phase 2でINVALIDが出た場合は、まずこの予測リストと照合して選定能力の失敗と切り分ける。

## 5. コスト・時間影響(10 article-level平均)

| 構成 | shortlist件数 | 候補行token(現行比) | Wiktionary照会(推定) | LLM費用への影響 |
|---|---|---|---|---|
| 現行 | 22.7 | 約1,358 | 2call/約10秒 | 基準 |
| U1np | 22.8 | +3.5 | 同上 | 無視可 |
| 拡大 | 27.4 | +184(+14%) | 8call/約43秒(429待ち込み) | 候補行token増のみ(選定1job。他は同一) |
| improved | 28.6 | +247(+18%) | 同上 | 同上 |
| precision_guarded_improved | 23.3 | +51(+4%) | 同上 | ほぼ無視可 |

JPY換算の単価は未確認のため算出せず(候補行tokenの相対増のみ。選定Promptの固定部[数千token]に対する比率は小さいが厳密値は未測定)。照会時間はAPI費用でなくWiktionary待ち時間。

## 6. 受入条件のPhase 1時点判定

| 条件 | 判定 | 根拠 |
|---|---|---|
| 1 `time lag`が候補へ届く | ○ | Coffee AdvでU1/拡大とも照会に入り、shortlistへ到達、U2 Tier-Hで`lag`除外。ただしLLMが実際に選ぶかは未検証(Phase 2) |
| 2 有益複数語が不必要に短縮されない(U3は注釈のみ) | ○ | U3は除外(断片のみ3件)+`fragment_risk`注釈で、置換・左拡張なし。正当な成句の誤除外0。理論上の影響範囲67見出しは既存Gateで記事内ではほぼ先に落ちる |
| 6 Coffee以外で誤除外・品質悪化なし | △ | 誤除外0(U2は2件、U3は3件)。ただし拡大は一般的な短い複数語68件を流入させ、希少単語約18件を押し出す=品質悪化の恐れ。precision_guardedで緩和されるが、効果は選定LLMの出力(Phase 2)で要確認 |
| 7 5件構成・canonicalization・Redundancy QAとの整合 | △ | 候補行の書式・ID・5件構成は無変更。U2 Tier-Hが`lag`/`time lag`の重複選択(Redundancy QA NG)を事前に避ける。ただし`contains:`/`contained_in:`/`fragment_risk`注釈の読み方を選定Promptへ書く必要あり(Pkg P、未実装)、Rule7 INVALIDの予測(35組)は別論点として残る |

## 7. Phase 2へ渡す固定shortlist

- `er064_output/kp_extraction_selection_opt_01/phase1_a/shortlists_improved_01.json`、sha256 = `04b41555252f72e7e13dd90959cae392f83859694dde8fd003f4f286fb01bac9`(sidecar `shortlists_improved_01.sha256.txt`、snapshot sha256はファイル内`snapshot_sha256`、10 article-levelの各`rows_text_sha256`付き)。
- 各記事に `current` / `improved`(拡大+U2 H+S+U3+U4c) / `alt_u2_tierS_only` / `alt_precision_guarded`(improved+窓外demoted hit除外)を収録。Phase 2対象(Coffee/meta/hormuz)は6 article-level。**どれをPhase 2の主対照にするかはFable判断**(私見: 拡大単独は一般語の流入が大きいため、improvedとalt_precision_guardedの2つを比較する価値あり。採用推奨ではない)。

## 8. 新たに発見した事項(実装していない・報告のみ)

1. 既存`refine_multiword_hits_noun_phrase_flag`のimportant判定が緩く、`want to`/`close to`/`call it`/`be wrong`/`take care`のような動詞・機能語連語もimportant(noun_phrase)扱いになる(現行60窓でも`feature back`が該当)。拡大で顕在化。名詞句判定の見直しは別論点。
2. 拡大のもう一つのコスト: 3語上限100の外にある`strait of hormuz`型(大文字表記3語)の取りこぼしが残る。
3. 小文字化(照会正規化)は取りこぼし13種に効くが優先度低。
4. `surface_echo`が候補`span`より広いケースの過去run走査(設計書Step1(v))は本委任の範囲外のため未実施。

## 9. 証跡
`wiktionary_snapshot_01.json` / `u1_vs_budget_expand_01.json` / `shortlist_replay_01.json` / `u4_demoted_cap_01.json` / `u3_fragment_01.json` / `rule7_predicted_invalid_01.json` / `shortlists_improved_01.json`(+.sha256.txt) / `prefetch_log_01.txt` / `run_01_log.txt`(Windowsコンソールの文字化けあり、集計は各JSONが正)。コード: `er064_kp_opt_01_upstream_core.py` `_prefetch_01.py` `_run_01.py` `_rule7_predict_01.py` `_test_01.py`(34/34 PASS: rate limit定数、Production無改変[git diff空]、patch復元、順序、U2/U3、後方互換、固定shortlist整合、Rule7)。
