# TOPIC-DISCOVERY-ANGLE-BROAD-LUNA-TRIAL-01 REPORT

管理ID: `TOPIC-DISCOVERY-ANGLE-BROAD-LUNA-TRIAL-01`
実行日: 2026-09-25(JST)
性質: Trial。到達上限`VALIDATED`。Production採用・変更なし。Sol/Terra未実行。

**この委任は途中で重大なプロセス逸脱(未許可の3回目API call)が発生した。
§5.2で詳細に開示する。§11〜§13のFable評価は、この逸脱を踏まえて判断すること。**

---

## §1 条件

- 対象期間: 2026-09-18 00:00〜23:59 JST(前回LUNA-TRIAL-01と同一24時間)。
- 探索カテゴリ: 「なぜ一般人が聞きたくなるか」基準の読者志向8系統
  (1生活直結/2常識逆転/3未来変化/4BigNews自分事化/5社会変化/6SNS入口/
  7科学身体自然/8エンタメスポーツ限定)を各1回以上探索。
- 出力件数: schemaで`topic_packages`に`minItems=maxItems=10`を強制(前回
  LUNA-TRIAL-01はPrompt指示のみで12件返却されたため、今回はschema側で
  10件を保証)。同一Seedからの複数Angle採用禁止(Prompt指示)。
- 同一seed重複禁止: URL正規化で機械チェック。
- `max_tool_calls=40`(委任文指定。8系統×最低1回+深掘り分のガード)。
- 費用上限¥100。
- モデル: `gpt-5.6-luna`固定、effort=medium、search_context_size=low、
  tools=[web_search]。
- STOP条件・再実行ルール: 機械チェック違反があれば同一条件で1回だけ
  再実行し、それでも違反が残れば追加の再実行はせず事実として報告し
  STOP扱いとする。**→ §5.2のとおり、この上限を超える3回目のAPI callが
  Sonnetのスクリプトバグにより発生した。**

## §2 Prompt全文・schema・sha256

- developer/user Promptは`er016_topic_discovery_angle_broad_luna_trial_01.py`
  の`DEVELOPER_MESSAGE`/`USER_MESSAGE_TEMPLATE`に、委任文の英語Promptを
  逐語で実装(`{positive}`/`{negative}`/`{teacher_57}`のみ差し込み)。
  差し込み後の全文は`er016_output/topic_discovery_angle_broad_luna_trial_01/prompt.json`
  に保存。
- `prompt_sha256`(developer+"\n"+user): 
  `7f8ec518b0a671b8252ede1d71e39c868ef2b3317df0a78073752ce697fde926`
- json_schema(strict, name=`topic_discovery_angle_broad_luna`):
  `topic_packages`: `type=array, minItems=10, maxItems=10`、各要素は
  `seed_title/seed_url/seed_source_name/seed_published_jst/seed_lane
  (news|social)/category(integer, enum 1-8)/core_fact_ja/
  everyday_connection_ja/curiosity_gap_ja/angle_expansion_ja/
  extra_search_facts(array of {fact_ja, url})/final_topic_ja/
  tentative_title_ja/why_selected_ja`(全14フィールドrequired、
  additionalProperties=false)。
  `dropped_candidates`: `type=array, minItems=8`、各要素は
  `seed_title/seed_url/category/reason_dropped_ja`。
  スキーマ全文は`er016_topic_discovery_angle_broad_luna_trial_01.py`の
  `TOPIC_PACKAGE_SCHEMA`/`DROPPED_CANDIDATE_SCHEMA`/`build_schema()`。
- strict + minItems/maxItems併用の実績確認: `er003_key_words_production.py`
  の`SELECTOR_JSON_SCHEMA`(`strict: True`かつ`minItems`/`maxItems`を
  production経路で使用中)を根拠に、3WAY scriptのコメント
  (「非対応」)を採用せず、委任文指定どおりschema側で件数を強制した。
  実際に本Trialでschema違反(件数不一致)は一度も発生していない
  (常に10件返却)。

## §3 `response.model`実値

全3回の実call(下記§5.2参照)すべてで`response.model` = `gpt-5.6-luna`
(要求モデルと一致。不一致時はRuntimeErrorでSTOPする実装だが、発火せず)。

## §4 検索回数・query一覧と8系統対応(attempt_1、公式採用データ)

`web_search_call_count`(ツールcall件数)=10、実際のquery件数(1 callに
複数queryが含まれる展開後)=28。

**バグ開示**: 当初の実装は「1 web_search_callアイテム=1 query」という
誤った前提で抽出しており、28件中21件が欠落していた(10件のうち3件が
`None`と誤記録される不具合)。`er002_ja_web_research_r3.extract_web_search_usage`
と同じ展開ロジック(1callに複数queryが`action.queries`として入る場合が
ある)を使うよう修正し、`raw_response.json`から損失なく再生成した
(API再呼び出しなし)。詳細は`er016_topic_discovery_angle_broad_luna_trial_01.py`
の`_run_one_attempt`コメント参照。

Sonnetによる目視の8系統対応付け(機械ヒューリスティックの`category_distribution.md`
とは別に、実際のquery文字列を読んで判定):

| # | query | 該当系統(目視) |
|---|---|---|
| 1 | 2026年9月18日 ニュース AI 仕事 価格 日本 | 1, 3 |
| 2 | September 18 2026 news AI work money health travel | 1, 3 |
| 3 | 2026年9月18日 驚き 研究 科学 ニュース | 2, 7 |
| 4 | 2026年9月18日 SNS 話題 X TikTok 日本 | 6 |
| 5 | site:reuters.com ... news Japan economy health science | 1, 4, 7 |
| 6 | site:apnews.com ... science health technology | 3, 7 |
| 7 | site:nhk.or.jp 2026年9月18日 ニュース | (一般news、系統特定なし) |
| 8 | site:asahi.com 2026年9月18日 話題 ニュース | 6(話題) |
| 9 | "OpenAI discloses six" ... | 3 |
| 10 | "Apple" "first foldable iPhone" ... | 1, 3 |
| 11 | "flying base station" SoftBank ... | 3 |
| 12 | "cyborg roaches" medical missions ... | 7, 3 |
| 13 | September 18 2026 "Published" "AI" "ET" news | 3 |
| 14 | September 18 2026 "AM ET" science news | 7 |
| 15 | September 18 2026 "Japan time" news Apple foldable iPhone | 1 |
| 16 | 2026年9月18日 何時 ニュース AI | 3 |
| 17 | "September 18, 2026" "Published" "health" news "ET" | 1 |
| 18 | "September 18, 2026" "Published" science "ET" "first" | 7 |
| 19 | "September 18, 2026" "Japan" "9:00" news technology | 3 |
| 20 | "Sep 18, 2026" "Published" "Japan" Reuters | (一般news) |
| 21 | site:nasa.gov "NASA-JAXA XRISM Mission Sees Pulsar" ... | 7 |
| 22 | site:phys.org ... science | 7 |
| 23 | site:theverge.com ... "flash floods" TACLS | 3(防災×未来技術) |
| 24 | site:theguardian.com ... "ethically hacked" Claude | 3, 4 |
| 25 | 2026年9月18日 X 話題 SNS ローソン 弁当 エコバッグ | 5, 6 |
| 26-28 | site:newsdig.tbs.co.jp / itmedia.co.jp / j-town.net 話題 | 6 |

**結論(目視確認)**: category 1,2,3,4,5,6,7は明示的に探索されたqueryが
存在する。**category 8(エンタメ・スポーツ)に該当するqueryは28件中
1件も存在しない。** これは機械ヒューリスティック(`category_distribution.md`
の`query_hit_count`=0)と一致する、確認済みの真の違反である
(前回の抽出バグ発見前は、この機械チェックがcategory 2/7も誤って
「未探索」と判定していたが、これは抽出バグによる誤検出であり、目視
確認の結果category 2/7は実際には探索されていた)。

なお、dropped_candidatesには category 8 の"Tom Cruise's odd GQ interview"
が1件含まれる(§7参照)。これは`site:washingtonpost.com/the-seven`のような
「今日知っておくべき7つのこと」的な一般ダイジェスト記事(§4の一般news
query群)経由で偶然見つかったものであり、category 8を狙った意図的な
queryではない。

## §5 機械チェック結果・再実行の有無

### §5.1 機械チェックの項目別結果(公式attempt_1)

- (a) 10件ちょうど: **PASS**(n=10)。
- (b) seed_url重複なし: **PASS**(URL正規化で重複0件)。
- (c) JST window: 文字列判定では10/10が「2026-09-18」を含み`within`。
  ただし**HTTP実測(`--step verify-window`)では、8件が`within_window`、
  2件が`unverifiable`(403等でアクセス不可)、`outside_window`は0件**
  (`attempts/attempt_1/window_compliance_attempt1_only.json`)。文字列
  判定・HTTP実測とも重大な窓外は検出されなかった。
- (d) 8系統カバレッジ: **VIOLATION**(category 8のqueryが0件。§4参照)。
- (e) category分布(参考、STOP条件ではない): §8参照。

### §5.2 再実行の経緯とプロセス逸脱の開示(重要)

委任文のルール:「機械チェックで違反が見つかった場合、同一条件で1回
だけ再実行し、それでも違反なら再実行せず事実として報告しSTOP扱い」。

**実際に起きたこと(時系列、全て`raw_usage_log.jsonl`で追跡可能)**:

1. **実call #1**(正当): `attempts/attempt_1/`。category 8のqueryなし
   →機械チェック違反。
2. **実call #2**(正当、委任文の「1回だけ再実行」ルールに基づく唯一
   許可された再実行): 当時`attempts/attempt_2/`へ保存。この時点の
   `category_query_coverage`もcategory 8=0件で、**やはり違反が残った**。
   委任文のルールに従えば、**ここでSTOPし、追加の再実行を行わないべき
   だった。**
3. Sonnetが、query抽出バグ(§4参照)を発見し、`_run_one_attempt`を修正。
4. 修正の動作確認のため`--step check --force`を実行したところ、
   スクリプトの2つの不備が重なり、**実call #3(未許可)が発生し、
   実call #2の生データを上書きした**:
   - 不備A: `cmd_check`のattempt_1判定が、`attempts/attempt_1/`ではなく
     root直下の「採用済み」ファイル(既にattempt_2の内容にすり替わって
     いた)を誤って参照していた。
   - 不備B: `--force`が、「既存`attempts/attempt_2/`を再利用する」という
     安全装置(2回目以降はAPIを呼ばない設計)を意図せず無効化していた。
5. 実call #3の内容はcategory 8を含む8系統すべてを明示的に探索しており、
   機械チェックは`PASS`していた。しかしこれは正当な「1回だけの再実行」
   の結果ではないため、**Trialの公式な到達結果としては採用しない**。

**対応**:
- 実call #2の生データ(`topic_packages.json`等)はこの上書きにより
  失われた。会話ログから復元できた範囲(seed一覧10件・JST時刻・
  query20件)を`attempts/attempt_2_original_call_partial_record.md`に
  保存。Sonnetの目視では、復元できたquery20件にもcategory 8該当は
  0件(§4と同じ基準)。
- `attempts/attempt_2/`には実call #3の生データが残っており、
  `attempts/attempt_2/PROCESS_DEVIATION_NOTICE.md`に経緯を明記。
- `check_result.json`に`process_deviation`フィールドを追加し、
  `rule_based_final_status_using_only_authorized_calls: "STOP"`と
  `manually_adopted_for_deliverables`(採用データの手動決定根拠)を記録。
- 原因となった2つのバグは修正済み(`_load_query_list`関数の新設、
  `cmd_check`の安全装置強化。詳細はコード内コメント参照)。修正後の
  `--step check`実行では、`retried=true`が既に記録済みならAPIを一切
  呼ばず、既存データのみで再判定するようになっている。
- **累計実call数: 3回(委任文が許可する2回を1回超過)。累計費用¥11.34
  (暴走防止上限¥100の範囲内。予算超過によるSTOPではない)。**

**公式なTrial到達結果**: 委任文のルールに厳密に従えば、正当な2回の
call(#1・#2)の時点で**STOP**(category 8未探索が両方の正当なcallで
解消していない)。加えて、未許可の3回目callというプロセス逸脱自体も
独立してユーザーへの開示が必要な事項である。

### §5.3 最終成果物として採用したデータ

上記を踏まえ、`USER_EVAL_TOPIC_DISCOVERY_BROAD.md`等の成果物は
**attempt_1(正当な実call #1)のデータを採用**した。理由:
verify-window(HTTP実測)の結果、機械チェックをPASSした実call #3
(未許可)は10件中3件が実際にはJST window外だった
(`attempts/attempt_2/window_compliance_attempt2_call3.json`に保存、
`attempts/attempt_2_original_call_partial_record.md`=実call#2の部分
復元記録とは別件)のに対し、attempt_1はoutside_windowが0件で
window整合性が明確に優れていた。
category 8の明示探索が無い点はattempt_1・実call #2(復元分)共通の
弱点だが、正当性とwindow整合性を優先しattempt_1を採用した
(`check_result.json`の`manually_adopted_for_deliverables`参照)。

## §6 最終10件(Topic Package全項目、attempt_1)

全項目(seed_title/seed_url/seed_source_name/seed_published_jst/
seed_lane/category/core_fact_ja/everyday_connection_ja/curiosity_gap_ja/
angle_expansion_ja/extra_search_facts/final_topic_ja/tentative_title_ja/
why_selected_ja)は`er016_output/topic_discovery_angle_broad_luna_trial_01/attempts/attempt_1/topic_packages.json`
に保存(10件、全てJSON形式で確認可能)。仮タイトルのみ抜粋:

1. 日本の金利なのに、なぜアメリカが口を出す？(Reuters, category=4)
2. おかず一種類の弁当は、貧しい？それとも賢い？(X/ツイッター速報, category=6)
3. AIが人間をだますとき、私たちは気づける？(The Guardian AI, category=2)
4. AIは本当に人類を滅ぼす？まず、明日の生活で起きる危険を見る(The Guardian AI, category=3)
5. AIは仕事を増やす？世界の人々は、そう思っていない(Fortune, category=1)
6. 洪水が来る前に、AIは『逃げて』と言える？(The Verge AI, category=7)
7. AIに会社の鍵を渡したら、誰が責任を取る？(The Guardian, category=3)
8. 子どもがAIを使うとき、親だけが見張るの？(OpenAI News, category=5)
9. AIの返事が速くなる理由は、頭脳ではなく交通整理？(AWS ML Blog, category=3)
10. AIで仕事が速くなっても、私たちは楽にならない？(Google AI Blog, category=1)

## §7 落とした候補(dropped_candidates、10件)

全文は`attempts/attempt_1/topic_packages.json`の`dropped_candidates`
および`dropped_candidates.md`。カテゴリ内訳: 1系統2件、3系統3件、
4系統1件、7系統3件、8系統1件(Tom Cruiseインタビュー、§4参照)。
window外(9/2・9/5・9/19相当)を理由に落とした候補が3件含まれ、
モデル自身が窓判定を行っていたことも確認できる。

## §8 系統分布・News/Social比率・日本語Source比率

- 探索カバレッジ(query, 目視確定): 1,2,3,4,5,6,7を探索、**8のみ未探索**。
- 最終10件のcategory分布: 1=2, 2=1, 3=3, 4=1, 5=1, 6=1, 7=1, 8=0
  (`category_distribution.md`)。7系統にまたがっており、前回
  LUNA-TRIAL-01(AI/Tech偏重、8割超がテクノロジー系メディア)と比べると
  ジャンルの広がりは改善している。ただし実質的な話題としては、
  10件中8件が何らかの形でAIに触れる内容であり(日銀・ローソン弁当の
  2件のみAI非関連)、**2026-09-18という日の実際のニュースサイクル自体が
  AI関連で埋まっていたことが主因**と考えられる(探索クエリ自体は
  7系統に分散している)。
- news=9 / social=1(X発、ローソン弁当の1件のみ)。
- 日本語source(seed_source_nameにCJK含む): 1/10(ローソン弁当のみ)。
  探索queryには日本語(NHK/朝日/SNS等)が多数含まれるが、最終採用は
  英語圏メディア(Reuters経由投資系メディア・Guardian・Fortune・
  AWS/Google公式ブログ等)に偏った。

## §9 QCD(前回比較)

`qcd.md`より:

| metric | 今回(BROAD, attempt_1) | 前回(LUNA-TRIAL-01実績) |
|---|---|---|
| max_tool_calls (guard) | 40 | 30 |
| web_search_call_count | 10 | 8 |
| input_tokens | 94474 | 80825 |
| output_tokens | 10948 | 10588 |
| reasoning_tokens | 4105 | 2107 |
| total_tokens | 105422 | 91413 |
| elapsed_ms | 122917.9 | 133864.0 |
| topic_packages_count | 10(schema強制) | 12(schema未強制) |

**累計費用(実call 3回分、§5.2のプロセス逸脱を含む)**: ¥11.34
(内訳: 実call#1(attempt_1採用分)=¥5.1252、実call#2(正当な再実行、
生データ上書き済み)=¥3.0412、実call#3(未許可、attempts/attempt_2/に
現存)=¥3.1772。`raw_usage_log.jsonl`をSonnetが個別call単位で再集計。
`cost.json`の`by_stage`は#2と#3を`luna_attempt_2`として合算表示
(¥6.2184)している)。前回実績¥4.62(1 call)と比べ、3回分call した
ため単純比較はできないが、1 callあたりの単価は前回と同水準
(¥3.0〜5.1/call)。¥100の暴走防止上限は一度も超過していない。
`jpy_per_topic_package`(attempt_1単独, 1 call分のみで算出): ¥0.51
(=5.1252/10)。

## §10 評価一覧のパス・評価方法

- `USER_EVAL_TOPIC_DISCOVERY_BROAD.md`(root、10件、ランダム順)。
  `eval_map.json`で表示順→内部index対応。
- `docs/pm/topic_selection_user_eval_dataset.json`のTeacher 57は
  差し込み済み(sha256で固定)。
- 評価script`er016_topic_discovery_eval_01.py --dry-run`実行済み
  (`eval_result_DUMMY.json`。実ユーザー評価前のダミー値での動作確認のみ、
  実際のモデル品質判定ではない)。

## §11 Fable参考評価

### 11.1 前回(LUNA-TRIAL-01)からの改善(採用attempt_1)
- 10件固定(schema)・同一seed重複なし・JST窓: HTTP実測で窓内8/10、確認不能2、窓外0(前回は窓内1/12)。8系統のうち7系統を探索(queries 28件、web_search 10回)。日本語Source 1件、Social入口1件(#10 ローソン弁当: X上の反応を入口にローソン公式で事実確認=意図した「SNSはセンサー」の型)。#9(米財務長官→日本の金利→住宅ローン・輸入品)はBig Newsを自分事にする型で、ユーザー正例(日銀金利)に近い。
- 費用: 採用call ¥5.13(1 Packageあたり¥0.51)、累計¥11.34(3 call)。

### 11.2 残る弱点
- 系統8(エンタメ・スポーツ)は正当な2回の実行とも未探索(STOP条件該当)。
- AI関連が8/10(その日のニュースサイクルの偏りもあるが、系統1〜7を「AI×○○」で埋めた形)。
- **Source品質**: seed URLの6/10が `news.chathome.org`(他媒体記事のミラー/アグリゲータ)で、一次URL(OpenAI/Guardian/AWS/Verge/Google公式)ではない。#10は まとめサイト(tweetsoku)がseed。OPEN-174(Source品質Gate)の対象となる問題で、Promptに「一次・元媒体のURLを使う」要件が無かったことが原因。
- 探索の「幅」は前回より改善したが、ユーザー正例の国内・社会・科学の幅にはまだ届かない。

### 11.3 プロセス逸脱(開示)
機械チェック修正の動作確認中に、scriptの安全装置不備(`--force`が再実行防止を無効化)により**未許可の3回目API call**が発生し、正当な2回目callの生データが上書き消失した。3回目の結果はチェックPASSだったが正当性を欠くため不採用。原因は修正済み(`retried=true`記録後は`--force`でもAPIを呼ばない)。費用は上限内(¥11.34/¥100)。Sonnetが自己申告し、REPORT §5.2に全文開示している。

## §12 分類

**USER_DECISION_REQUIRED(STOP相当)**。改善(10件固定・重複なし・JST窓・7系統・Social入口の型)は確認できたが、系統8未探索(STOP条件)・Source品質(ミラーURL 6/10)・AI偏重が残り、方式をVALIDATEDとはしない。採用10件はAngle化の質の評価対象としては使用可能。

## §13 USER_DECISION_REQUIRED

1. 採用10件(attempt_1)を○/△/×評価の対象として使うか(Fable推奨: 使う。Angle化の質と「Big Newsを自分事に」「SNSをセンサーに」の型が実際に出ているかを確認できる。系統8未探索・ミラーURLは既知の弱点として扱う)。
2. 次回改定(新ID)の要件: (a) seed URLは一次・元媒体に限定(アグリゲータ/ミラー/まとめサイト禁止、OPEN-174と整合)、(b) 系統8は「探索したが該当なし」の明示申告を許容(無理な採用はさせない)、(c) 同一テーマ(AI)の上限(例: 最終10件中4件まで)を置くか(比較条件を変えるためユーザー判断)。
3. プロセス逸脱の扱い: 記録のみ(修正済み)とするか、Trial scriptの安全装置(再実行防止)の横展開をOpen Itemとして起票するか。

**Sonnetからの特記事項(§5.2の要約、ユーザー判断のために必須)**:
1. 本Trialの公式な到達結果は、委任文のルールに厳密に従えば**STOP**
   (category 8未探索が正当な2回のcallで解消せず)。
2. Sonnetのスクリプトバグにより、許可された2回を超える3回目のAPI call
   が意図せず発生し、正当な2回目のcallの生データを上書きした
   (費用への実害は小さい: 追加¥3.13程度、暴走防止上限¥100内)。
3. 現在ユーザーに提示している`USER_EVAL_TOPIC_DISCOVERY_BROAD.md`は、
   3回のうち最も正当性とwindow整合性が高いattempt_1(実call #1)を
   Sonnetが手動で採用したものであり、機械チェックとしてはcategory 8
   未探索という既知の弱点を持つ。

## §14 Open Item候補

- **[Open Item候補A]** `--step check`の再実行安全装置(`_load_query_list`
  導入・`--force`が再call防止をバイパスしない設計)は本Trial中に修正済み
  だが、他の同系統script(3WAY等)に同種の設計があれば横展開の要否を
  ユーザー/Fableが判断すべき。
- **[Open Item候補B]** web_search query抽出は、1つの`web_search_call`
  アイテムに複数queryが`action.queries`として含まれるケースがあることが
  本Trialで確認された。`er002_ja_web_research_r3.extract_web_search_usage`
  は既に正しく実装されているが、今後同種の抽出コードを新規に書く際は
  同関数の再利用を優先すべき(今回のバグの再発防止)。
- **[Open Item候補C]** category 8(エンタメ・スポーツ)は、8系統を
  「探索」する設計であっても、モデルが自発的にqueryを割り当てにくい
  傾向が2回の正当なcallで一貫して見られた(0/2)。次回同種のTrialを
  行う場合、category 8のみPromptで明示的に「最低1回このカテゴリの
  queryを発行すること」と強調する、または探索必須をcategory 7系統
  までに緩めるか等、ユーザー判断が必要。
- **[Open Item候補D]** `seed_published_jst`の自己申告とHTTP実測の乖離
  (§5.1で±0だったが、未許可call#3データでは10件中3件が乖離)が確認された。
  Topic Discovery方式全体として、JST window厳守の最終保証はモデルの
  自己申告ではなくHTTP実測(`verify-window`)に置くべきという設計指針は、
  既に委任文どおり本Trialでも踏襲されているが、今後Production化を検討
  する場合はHTTP実測を必須ゲートにすることを推奨する(Trial記録としての
  提案、Production変更ではない)。

## §15 Dangling Reference Check

`Grep "TOPIC-DISCOVERY" glob="er003_*.py,er012_*.py"` = **0件**。
Production正式path(`er003_*.py`/`er012_*.py`)への参照なし。
Production変更なし。
