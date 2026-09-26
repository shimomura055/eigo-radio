# FICTION-FAMILY-Z-PRODUCTION-E2E-01 -- Phase 0 事前調査(read-only、¥0、API呼び出しなし)

管理ID: `FICTION-FAMILY-Z-PRODUCTION-E2E-01`
種別: Phase 0 recon(実装禁止、コード/Prompt/SSOT変更なし)。本ファイルが今回の唯一の新規成果物。
方法: 既存artifact読込(Read/Grep)+著作権に関する公開資料のHTTP GET直接取得(web_search/API課金なし)。

## 0. 重要な運用上の観察(先に記載)

調査開始直後、`er018_output/fiction_real_story_and_true_crime_trial_01/true_crime/`
配下で、本管理ID(`FICTION-FAMILY-Z-PRODUCTION-E2E-01`)を名乗る**別セッション**が
リアルタイムで作業しており(`naming_rule_diff.md`等が調査中に出現→数分後に
commit済みへ変化)、調査完了時点で以下がcommit済みだった。

- commit `6c0b0e02`(2026-09-26 18:29:21、Author: Keisuke Shimomura、
  `Co-Authored-By: Claude Sonnet 5`): "The Second Skeleton"
  (`true_crime/story.md`)へFiction共通外国人名ルール(本文中はFirst/Last
  どちらか一方のみ)を適用(Daniel Clarke/Eugene Aram/Richard Houseman →
  Clarke/Aram/Houseman、334語→326語、Fact/Storyline/引用は不変)。
  API呼び出し・再生成・音声化なしと明記。

本Phase 0(このsubagent)はこのcommitに一切関与しておらず、対象ファイルの
編集・stageは行っていない(指示範囲外の既存差分を触らない原則を遵守)。
ただし、**同一管理IDの下で複数セッションが並行して動いている**ことを示す
事実であり、Fable側での認識・整理を推奨する(本レポートは事実の記録のみ、
判断はしない)。この並行作業により、本レポートが§5で引用する
"The Second Skeleton"の内容は上記commit後の状態(Last name統一版)である。

---

## 1. 権利の再確認(最優先)

### 1-1. 結論(事実の提示、判断はしない)

太宰治「走れメロス」("The Three-Day Promise"の原典)について、
Trial-02の`candidates_evaluation.md`(44行目)は**日本法のみ**で判定しており
(「Aozora公開・没年1948(著作権切れ)」)、**米国法の判定が欠落している**。
本Phase 0で公開資料を直接HTTP GETし確認した結果、以下の事実が判明した。

- 走れメロスの初出は1940年(日本語版Wikipedia「走れメロス」記事の
  カテゴリタグに「1940年の小説」「新潮掲載の小説」と明記。
  URL: https://ja.wikipedia.org/wiki/走れメロス 、確認2026-09-26、
  HTTP 200)。
- 太宰治の没年は1948-06-13(Aozora Bunko図書カード、
  URL: https://www.aozora.gr.jp/cards/000035/card1567.html 、
  確認2026-09-26、HTTP 200、逐語: 「生年：1909-06-19 没年： 1948-06-13」)。
- 日本の著作権保護期間は、2018年末のTPP11整備法による70年化以前は
  死後50年だった(English Wikipedia "Copyright law of Japan"、
  URL: https://en.wikipedia.org/wiki/Copyright_law_of_Japan 、
  確認2026-09-26、HTTP 200、逐語: "Law changes promulgated in 1970
  extended the duration to 50 years")。太宰没後50年=1998年末で日本の
  保護は満了しており、2018年末の70年化は**遡及しない**(同ページ逐語:
  "This new term was not applied retroactively; works that had entered
  the public domain between 1999 and 29 December 2018 (inclusive) due
  to expiration remained in the public domain.")。太宰の1999年1月1日
  パブリックドメイン化はこの「1999〜2018年に既に切れていた作品」の
  範囲に該当し、日本では現在も確定的にパブリックドメイン。
- 米国では、URAA(Uruguay Round Agreements Act、1996-01-01発効)により、
  「1996年1月1日時点で本国(source country)において著作権が消滅して
  いない外国作品」の米国著作権が回復する(Cornell University Library
  "Copyright Term and the Public Domain in the United States"のチャート、
  URL: https://copyright.cornell.edu/publicdomain (同一内容のミラー
  https://guides.library.cornell.edu/copyright/publicdomain も確認)、
  確認2026-09-26、HTTP 200)。同チャートの該当行(逐語、表内セル抜粋):
  「1931 through 1977 / Solely published abroad, without compliance
  with US formalities or republication in the US, and not in the
  public domain in its home country as of 1 January 1996 (but see
  special cases) / 95 years after publication date」。
- 走れメロスは1996年1月1日時点、日本において**まだ保護期間中**だった
  (没後50年=1998年末まで保護、1996年1月時点で残り約3年)。したがって
  上記表の「1996年1月1日時点で本国で消滅していない」に該当し、
  URAAにより米国著作権が回復し、**発行日(1940年)から95年**=2035年末
  まで米国で保護される、という判定になる可能性が高い(=米国では2036年
  1月1日にパブリックドメイン化する可能性が高い)。
- 日本は1996年より遥か以前(1899年)からベルヌ条約加盟国であり、
  「本国のベルヌ/WTO加盟が1996年より後の場合は加盟日を基準日とする」
  という同チャートの例外規定は適用されない。

**この判定は事実の提示であり、本Phase 0は最終法的判断を行わない**
(著作権法解釈は弁護士確認が望ましい論点であり、Fable/ユーザーの判断が
必要、後述§8のSTOP候補参照)。

### 1-2. 他候補との比較(日米双方の判定表)

Trial-02候補(`fiction_external_seed_selection_criteria_trial_02
/candidates_evaluation.md`)およびTrial-01候補
(`fiction_external_story_seed_trial_01/stories_all.md`)について、
同じ基準(日本: 没後の保護期間経過/米国: 1931年より前の発行は無条件で
米国PD、1931年以降発行の外国作品は1996年時点の本国status次第でURAA
回復+95年)で判定すると、**走れメロスだけが「発行年1940年」で
唯一1931年以降の外国作品であり、米国PD判定に個別のURAA計算を要する
候補である**。他の全候補は1931年より前の発行のため、米国では発行年
基準で無条件にパブリックドメインと判定できる(Cornell表の該当行、
逐語: 「Before 1931 / None / In the public domain」)。

| 候補 | 出典/発行年 | 著者没年 | 日本(または原著国)PD | 米国PD(1931年前発行は無条件PD) | 備考 |
|---|---|---|---|---|---|
| **走れメロス(太宰治)** | 1940年、新潮 | 1948 | PD(1999-01-01〜) | **要URAA判定。1996-01-01時点で日本未PDのため回復、95年=2035年末まで保護の可能性が高い(2036年PD)** | 現行採用候補、唯一の要精査案件 |
| 羅生門(芥川龍之介) | 1915年 | 1927 | PD | 1931年より前発行→**米国PD**(無条件) | Trial-02新規採用 |
| 注文の多い料理店(宮沢賢治) | 1924年 | 1933 | PD | 1931年より前発行→**米国PD**(無条件) | 既生成"Kind Lodge"(ユーザー評価「良い」) |
| The Bet(Chekhov) | 1889年 | 1904 | PD(ロシア/米欧共通) | 1931年より前発行→**米国PD** | Trial-02新規採用 |
| The Signal(Garshin) | 1887年 | 1888 | PD | 1931年より前発行→**米国PD** | 既生成"Red Scarf"(ユーザー評価「悪くない」) |
| Missionary Travels(Livingstone、ライオンの場面) | 1857年 | 1873 | PD | 1931年より前発行→**米国PD** | Trial-02新規採用 |
| Franklin's Autobiography(パンの場面) | 1791年初刊行(米国人著者) | 1790 | PD | 米国内著作かつ1931年より前→**米国PD** | 既生成"Two Plus One"(ユーザー評価「悪くない」) |
| The Story of My Life(Helen Keller、水ポンプの場面) | 1903年、米国発行 | 1968 | - | 米国内著作・米国発行かつ1930年より前発行→**米国PD**(著者没年1968は無関係、発行年基準のpre-1978ルール) | Trial-02新規採用、Gutenberg #2397既に"Public domain in the USA"表記 |
| The Gift of the Magi(O. Henry) | 1905年 | 1910 | - | 米国内著作・1931年より前→**米国PD** | Trial-02、今回非選択(オチが有名) |
| The Necklace(Maupassant) | 1884年 | 1893 | PD | 1931年より前発行→**米国PD** | Trial-02、今回非選択(オチが有名) |
| The Sire de Maletroit's Door(R.L. Stevenson) | 1877年 | 1894 | PD | 1931年より前発行→**米国PD** | Trial-02、今回非選択(圧縮難度) |

結論として、**現行E2E候補("The Three-Day Promise"/走れメロス)は、
Trial-02で評価済みの他候補と比べて唯一、米国著作権が残存している
可能性が高い候補**である。日米双方でPD確定済みの代替候補(表内、
特にユーザー既評価済みの「Kind Lodge」原典=注文の多い料理店[良い]、
「Red Scarf」原典=The Signal[悪くない]、および今回Trial-02で新規に
Gate1-3全通過・未生成のRashomon/The Bet/Livingstoneライオンの場面)が
事実として存在する。

---

## 2. 既存Fiction生成資産の棚卸し

### 2-1. er018系スクリプトの役割
- `er013_family_c_future_*`/`er013_family_c_episode_*`系列(後述2-3)とは別に、
  `er018_output/`配下は**Story調達(Seed化+Story生成)のTrial**であり、
  TTS化・Production配線はしていない(text生成のみ)。
  - `fiction_story_dna_e_axis_redesign_01/`: Story DNA(プロット生成の
    パラメータ空間設計)Trial。
  - `fiction_core_provocation_*`: 内発的Story生成(外部Seedなし)のTrial。
  - `fiction_external_story_seed_trial_01/`: 外部実話/文学Seedの初回Trial
    (4候補採用、うち3件が現在生成済み: The Open Gate[弱い、後にGate3
    FAILと判明・非推奨]/Two Plus One[悪くない]/The Kind Lodge[良い]/
    The Red Scarf[悪くない])。
  - `fiction_external_seed_selection_criteria_trial_02/`: 候補選定基準の
    再設計Trial(一次テキスト実際に読む/tile.loc.gov発見/Gate1-3+ABCD
    基準)。本管理IDの現行候補"The Three-Day Promise"はここで生成
    (`stories/03_japanese_lit_2/`)。
  - `fiction_real_story_and_true_crime_trial_01/`: story_type=real_story/
    true_crime の初回Trial(Nellie Bly実話、Eugene Aram冤罪処刑の
    True Crime、上記§0のnaming_rule_diff.md参照)。

### 2-2. "The Three-Day Promise"の生成物(path+sha256)
`er018_output/fiction_external_seed_selection_criteria_trial_02/stories/03_japanese_lit_2/`
- `seed.json`(sha256: `f4a85f5c...761`): Seed要素6件、conversion_plan、
  rights_status(URL+確認文言+確認日、日本法のみの判定)。
- `story_prompt.txt`(sha256: `9db16dc6...813`): 実際にWriterへ渡された
  Prompt全文(Seed+変換方針+"Common principles"+キャラクター制約
  [主人公のみ固有名詞使用可]+A2レベル/300-350語+listening-friendliness)。
- `story.md`相当の本文(sha256: `2b602da0...2`): "The Three-Day Promise"
  本文(`stories_all.md`156-198行に同一本文を確認転記済み)。
- `primary_text_excerpt.md`(sha256: `cdf8b3dd...8`)、`rights_check.md`
  (日本法のみの確認記録、Aozora URL+没年のみ)。

### 2-3. 既存Production配線の有無(「Future Family」の定義箇所)
`CURRENT_SPEC.md` 974-1076行「Family C(Future Story)Production」節、
`er013_family_c_production_01.py`/`er013_family_c_production_runner_01.py`
(`--level`でA2/B1分岐、Story TTS→ASR→Comment→Assembly→Audio Validation
Gate→player→web_deliveryまでの全体生成経路が存在)。ただし対象は
**"Future Story"**(未来の生活場面、Digital Twins/Memory等の完全創作
シナリオ)であり、Research/Verified Fact Ledgerを使わない点で構造的に
Fictionと共通する(`DECISION_LOG.md` 7910-7913行、逐語: 「Family C
(Future Story、`er013_family_c_production_runner_01.py`)もA2/B1
それぞれ独立の`article_path`を持ち、B1→A2翻案ではない(ただしFamily C
はFictionのためResearch/Ledger自体を使わない構造的特殊例)」)。

`DECISION_LOG.md` 9324行(`PM-USER-VALIDATION-DIRECTION-RECORD-01`)は、
「新News方式・**Future→Fiction再定義**・Key Phrase仕様変更・Learning UI
仕様のいずれも未確定」と明記しており、**「Future Family C」を
「Fiction」として正式に再定義する判断自体、まだユーザー承認された
Production仕様ではない**(`RECORDED`のPM背景記録のみ)。

**結論**: 走れメロス外部Seed文学作品("The Three-Day Promise"のような
"Literature"サブタイプ)向けの専用Production runner/entry pointは
**存在しない**。最も近い既存Production機構はFamily C
(`er013_family_c_production_*`)だが、これは"Future Story"(完全創作の
未来シナリオ)向けに設計されたものであり、外部一次テキストからの
翻案("Literature"/"Real Story"/"True Crime")向けの入口・Seed取込・
権利記録の格納先は未整備。

---

## 3. 既存Family A/X Production機構の再利用可否

### 3-1. Family C(既存の最近傍機構)からの示唆
`CURRENT_SPEC.md` 974-1076行(§2-3で引用)により、以下がFamily C
Production経路で既に実証済み:
- Story本文のTTS segmentation原則(`plan_story_segments()`、Voice境界/
  scene境界で分割、機械的な語数分割はしない)。
- A2 Comment生成(`generate_family_c_a2_comment()`、理解ガイド型Contract、
  「聞いてみましょう」的メタナレーション禁止)。
- Key Phrase選定・Assembly: Family C runnerは既存共有module
  (`p9a.build_key_phrase_block()`)をそのまま再利用しており
  (`er013_family_c_production_runner_01.py` 518-527行)、reuse_from
  必須(content curation自体はスコープ外、既存資産の再利用のみ確認済み)。
  → **Key PhraseのAssembly/TTS/Audio Validation Gateは、既にFiction
  構造(Family C)で動作実績あり**。
- Assembly→Audio Validation Gate→player→web_delivery: Family C runner
  内で既存Production関数を通しで呼ぶ設計(§2-3引用のとおり)。

### 3-2. Family A(News)専用の構造契約で、Fictionにそのまま使えないもの
`er003_v1_n3_01_scaffold_generate.py::split_article_text()`
(104-159行)は、記事本文に**ちょうど2つの`###`見出し(Point One/Point
Two)+`## In one line`見出し**が存在することをハードに要求し
(108-113行、いずれも一致しないとRuntimeErrorで停止)、Main Storyを
段落単位でpart1/part2へ機械的に均等分割する(137-152行)。これは
News/Discovery/Trend共通の「本文+Point 1+Point 2+In One Line」構造
契約であり、**単一の連続した物語(Point構造を持たないFiction本文)には
適合しない**。実際、Family Cは本関数を一切使わず、独自の
`plan_story_segments()`(段落/Voice/scene境界ベースの分割)で代替して
いる。→ Fiction向けにこのscaffold関数を無改変で流用することはできず、
Family C方式(専用segmentation)を継続するのが妥当という既存の実例が
ある(新規重複実装ではなく、Family C機構の再利用)。

`er003_v1_n3_01_scaffold_generate.py` 166-179行の`A2_COMMENT_3_ROLE_N3`
プロンプト文言(「このニュース全体の意味を短く整理し...」)はNews前提の
文言であり、Fiction本文へ流用するとメタファーが破綻する。Family Cは
既にこれを使わず独自のA2 Comment Contract(仕様B、`CURRENT_SPEC.md`
998-1008行)を持っており、Fiction(Family Z)はこのFamily C方式を
継続再利用するのが自然(News用Comment Promptの改造ではなく、Family C
既存Comment機構の適用)。

### 3-3. Fact Checker/Ledger Deviation Check
`CURRENT_SPEC.md` 1105行「Fact Safety(共通)」およびFamily C該当節
(§2-3引用)により、**Ledgerを使わない構造はFamily Cで既に前例化
済み**であり、Fiction(Family Z)がLedger/Fact Checker/Ledger Deviation
Checkの3段構成を経由しないこと自体は新しい問題ではない(Family Cが
同じ構造的特殊例として先行している)。

### 3-4. story_type intro(Preview/Topic intro相当)
Family Cは既に`topic_intro`(固定文言"Today's topic is {topic_title}."、
アセット名`topic_intro_en.wav`)と`preview`(日本語、`preview.txt`から
読み込み、`preview_ja.wav`)を持つ(`er013_family_c_production_runner_01.py`
777-803行)。ただし**「In One Line」に相当する終端要約segmentはFamily C
に存在しない**(同ファイル内`grep -i "in one line"`で該当なし)。→ 依頼
仕様の5要素(Preview/Topic intro/Comment/In One Line/Key Phrase)のうち、
Preview・Topic intro・Comment・Key Phraseの4つはFamily Cに前例があるが、
**In One Lineに相当するFamily C要素は無く新規追加が必要**。

---

## 4. story_type metadata

`er013_output/family_c_production/{memory,home_robots,digital_twins}
/article_config.json`(全件確認)には、story_type相当のフィールド
(`literature`/`real_story`/`true_crime`)は**存在しない**。
`er013_family_c_production_runner_01.py`にも`category`/`content_type`/
`program_type`等の分岐は見つからない(Grep該当なし)。

**結論**: 依頼仕様(story_type metadataによるUI表示+音声冒頭一文の
自動付与、Writer本文には書かせない)を実現する既存の機構・フィールドは
**皆無**。最小追加案(判断はしない、案の提示のみ):
- `article_config.json`へ`"story_type": "literature" | "real_story" |
  "true_crime"`フィールドを追加。
- Production側(runner)がこのフィールドを見て、`real_story`/
  `true_crime`の場合のみ固定文言の音声intro segment("This is a true
  story."/"This is a true crime story.")をFamily Cの`topic_intro`と
  同じ仕組み(固定文言→TTS、Writerには一切書かせない)で自動挿入し、
  `literature`の場合は何も挿入しない。
- player側のUI表示("REAL STORY"/"TRUE CRIME"バッジ)は、既存player/
  web_delivery側にFamily/ジャンル表示の仕組みがあるかどうかは本
  Phase 0では未確認(player側コードの調査は今回のGrep範囲外、追加調査が
  必要な場合は別途)。
- 上記はいずれも**未実装の提案**であり、Prompt文言・コード変更は
  一切行っていない。

---

## 5. 外国人名ルール(First/Lastどちらか一方のみ)

既存コードにこのルールの自動チェックは**存在しない**(`Grep
"naming_rule|First name.*Last name|外国人.*人名"`該当なし)。ただし、
§0で報告した並行作業により、**手動diffベースの前例が既にcommit済み**
(`er018_output/fiction_real_story_and_true_crime_trial_01/true_crime/
naming_rule_diff.md`、commit `6c0b0e02`)。これはコード化されたQAでは
なく、人手(Sonnet)によるBefore/After比較文書であり、今後複数作品へ
スケールする場合は自動化が望ましいという課題が残る。

最小案(判断はしない、案の提示のみ):
- Offline checker案: Story canonical textから固有名詞らしき連続大文字
  始まりトークン列を抽出し、同一人物と推定される複数バリアント
  (例: "Melos"のみ生成された場合は該当なしだが、"John Smith"のように
  First+Last同時出現があれば警告)を機械的に検出するQA関数を追加。
  ただし人物の同定(同一人物判定)自体は簡単ではなく、機械判定の
  信頼性は限定的(過検知/見逃しのリスクあり、あくまで人間レビュー
  補助)。
- Prompt側の恒久対策案: Fiction Story生成Prompt
  (`story_prompt.txt`相当のテンプレート)へ「外国人名は本文中で
  First/Lastどちらか一方のみを一貫して使用すること」という1文を追加。
  ただし**Prompt変更はProduction仕様変更に該当するため、本Phase 0では
  実装しない**(`USER_DECISION_REQUIRED`候補として§8に記載)。

---

## 6. TTS既承認仕様(er020)との接続点

`er020_tts_retry_local_rewrite_01.py`の`resolve_narrative_role()`
(120-140行)は、**segment_idの完全一致文字列**でrole判定を行う
(`"full_story_part1/2/3"`/`"point_one"`/`"point_two"`/`"comment_1〜4"`/
`"preview"`/`"topic_intro"`/`"in_one_line"`のみ、それ以外は`None`)。
`connected_speech_enabled_for()`(157-159行)は上記roleの5種類のみ
`True`を返す。

Family C(既存の最近傍Fiction的機構)の実際のsegment_id命名は、
`er013_family_c_production_01.py` 302行(`s["id"] = f"story_{i:03d}"`
→ `story_001`, `story_002`...)、
`er013_family_c_production_runner_01.py` 779行(`"topic_intro_en.wav"`)、
745行(`"preview_ja.wav"`)であり、**er020の`resolve_narrative_role()`
が期待する文字列("topic_intro"/"preview"等)と一致しない**
(`"topic_intro_en"`≠`"topic_intro"`、`"story_001"`は"FULL_STORY"
パターンにも該当しない)。

**結論**: 現状のFamily C(Future Story)は、er020のConnected Speech
5-role適用対象に**構造的に含まれていない**(segment_id命名の不一致
により`connected_speech_enabled_for()`が常に`False`を返す)。
Family Z(Fiction)を新設する場合も、既存Family C式のsegment_id命名を
そのまま使えばConnected Speechは適用されない。Family Z向けに
Connected Speech(既承認の5 role原則: Full Story/Comment/Preview/
Topic intro/In One Line)を適用したい場合、(a)Family Zのsegment_idを
er020の期待する文字列規約に合わせて命名するか、(b)
`resolve_narrative_role()`へFamily Z固有のsegment_idパターンを追加
するか、のいずれかのコード変更が必要(いずれも本Phase 0では未実施、
新規判断を要する)。

---

## 7. コスト見積(量産、実測値ベースの概算)

実測済みの参考値(既存artifact、円換算):
- Fiction Story生成(Seed化5件+Story生成5件、Trial-02):
  合計$0.010976(約¥1.76)、1本あたり概ね¥0.3〜0.5
  (`er018_output/fiction_external_seed_selection_criteria_trial_02
  /cost.json`)。
- Family C(Future Story)1エピソード実費(累計、複数iterationの合算値
  であり単純な1回生成コストではない点に注意): Home robots episode
  累計¥148.50(`DECISION_LOG.md` 7444行)。
- Discovery(News系、Ledger使用)1記事総原価: ¥606.08
  (`DECISION_LOG.md` 7468-7469行)。
- Voices(B-Family)1記事総原価: ¥354.72
  (`DECISION_LOG.md` 7482-7483行、Fact Safety差し戻し2回込み)。
- TTS単価の参考: comment/preview等の再生成1件あたり概ね¥0.9(TTS)、
  ASR込みで1件あたり数円(`DECISION_LOG.md` 7723行「TTS4件×¥0.90=
  ¥3.60」)。

Family Z特有の増分(既存Familyには無い工程):
- Source確認・権利確認(URAA判定含む): 本Phase 0のような公開資料
  HTTP GET調査はAPI課金なし(¥0)だが、人手/Sonnet作業時間を要する
  (量産時は候補ごとに個別確認が必要、¥0だが時間コスト)。
- Seed処理(一次テキスト取得+Seed化): Trial-02実績で1本¥0.3〜0.5。
- story_type判定: 既存metadata機構がないため実装後は¥0(ロジック
  判定のみ、追加API呼び出し不要)。

概算(既存実測値からのアナロジー、Family Zは新規機構のため実測ではなく
既存Family C/Voices/Discoveryとの類推による概算であることに留意):

| 項目 | 1記事概算 | 根拠 |
|---|---|---|
| Story text生成(Seed+Story) | ¥1〜5 | Trial-02実測¥0.3〜0.5/本+複数候補試行分の余裕 |
| Comment/Preview/Topic intro/In One Line生成 | ¥5〜15 | Family C A2 Comment生成の規模感からの類推(Family C自体の text側個別コストは本Phase 0では未実測、News Comment生成¥数円/件の実績から類推) |
| Key Phrase選定 | ¥5〜15 | 既存Family共通(News/Discovery実績と同水準と仮定) |
| TTS(Full Story分割+Comment+Preview+Topic intro+In One Line+Key Phrase 5件) | ¥15〜40 | ¥0.9/segment×20〜25 segment程度の概算 |
| ASR/QA(cool-down/Local Rewrite/Natural English QA込み) | ¥10〜60 | TTS単価と同水準〜数倍(retry発生時) |
| **1記事合計(概算レンジ)** | **¥40〜135** | 上記合算、Family C累計¥148.50(複数iteration込み)と概ね整合するレンジ |

| 記事数 | 概算合計(下限) | 概算合計(上限) |
|---|---|---|
| 1 | ¥40 | ¥135 |
| 10 | ¥400 | ¥1,350 |
| 30 | ¥1,200 | ¥4,050 |
| 100 | ¥4,000 | ¥13,500 |

**注意**: 上表はFamily A/C/Voicesの実測値からの類推概算であり、Family Z
の実測値ではない(Family Zでの実際のTrial/Production runで再測定が
必要)。retry/Human Review Lock発生率次第で上振れする(Voices実績では
Fact Safety差し戻し2回で¥354まで増加した前例あり)。

---

## 8. 不足一覧・最小実装計画・STOP候補論点

### 8-1. 不足一覧(何が不足しているか/再利用できない理由/最小追加案)

| 領域 | 現状 | 既存機構で再利用できない理由 | 必要最小の追加実装(案、未実装) |
|---|---|---|---|
| Production entry point | 存在しない(er018はtext生成Trialのみ) | Family C runnerは"Future Story"専用設計(article_config.json構造、voice_keywords等がFuture Story文脈) | Family C runnerを土台に、Seed取込+権利記録格納+story_type分岐を追加した新runner(Family C複製ではなく拡張) |
| 本文scaffold(segment化) | Family Aのsplit_article_text()はPoint構造前提で不適合 | ###見出し2つ+In One Line見出しをハード要求、Fiction本文は連続物語で該当構造を持たない | Family C既存の`plan_story_segments()`をそのまま再利用(新規実装不要) |
| Comment/Preview/Topic intro | Family AはNews文脈のPrompt、Family Cは仕様Bで対応済みだがIn One Line相当なし | News用Comment Promptはstory文脈で破綻 | Family C仕様Bを再利用+In One Line相当のみ新規Prompt設計要(USER_DECISION_REQUIRED候補) |
| Key Phrase | 既存共有module(p9a.build_key_phrase_block)がFamily Cで動作実績あり | 再利用できない理由なし(構造非依存) | 追加実装不要、そのまま再利用可能 |
| story_type metadata | 存在しない | - | article_config.jsonへのフィールド追加+固定intro音声の自動挿入ロジック(§4) |
| 人名ルール自動チェック | 存在しない(手動diffの前例のみ) | - | オフラインchecker(補助的、信頼性限定)+Prompt追記(Production仕様変更のためUSER_DECISION_REQUIRED) |
| Connected Speech 5-role適用 | Family C含め現状segment_id命名が不一致で不適用 | er020の`resolve_narrative_role()`が完全一致文字列判定のため | Family Zのsegment_id命名をer020規約に合わせる、またはer020側にFamily Z用パターン追加(いずれもコード変更、要判断) |
| 権利記録の格納先 | Trial単位のrights_check.md/naming_rule_diff.mdのみ、Production正式フィールドなし | Family C article_config.jsonに権利情報フィールドがない | article_config.jsonへ`rights`ブロック(出典URL/日本PD根拠/米国PD根拠[URAA判定結果]/確認日)を追加する案 |

### 8-2. STOP候補(新規仕様判断が必要、判断はしない)

1. **走れメロスの米国著作権status**(§1): 本Phase 0の分析(URAA+95年
   =2035年末保護、2036年PD)が正しければ、現行E2E候補は米国での
   利用に法的懸念がある。続行/差し替え/専門家確認のいずれを取るかは
   ユーザー判断。差し替え候補は日米双方PD確定済みの表(§1-2)に事実
   として複数存在する(羅生門/The Bet/Livingstoneライオンの場面等)。
2. **「Future Family C」→「Fiction」の正式再定義**: `DECISION_LOG.md`
   9324行のとおり未確定。Family Zを新設する場合、Family Cとの関係
   (完全に別Family/Family Cの拡張/統合)をどう位置づけるかは未決定。
3. **story_type metadataの具体的スキーマ・UI文言・音声intro文言**:
   §4の案は未承認の提案であり、正式フィールド名・UI表示文言
   ("REAL STORY"/"TRUE CRIME"の具体的デザイン)はユーザー承認が必要。
4. **外国人名ルールのPrompt組込**: §5の1行追加案はProduction Prompt
   変更に該当し、ユーザー承認が必要。
5. **Connected Speech 5-role適用のsegment_id規約統一方法**: §6の
   (a)/(b)いずれを取るか、Family C自体も同時に是正するかは判断が必要。
6. **In One Line相当segmentの新規Prompt設計**: Family Cに前例がなく、
   Fiction向けのIn One Line生成方針(何を一行に要約するか、結末の
   ネタバレ回避方針等)は新規設計・ユーザー承認が必要。

---

## 参照

- `er018_output/fiction_external_seed_selection_criteria_trial_02/
  candidates_evaluation.md`(1-102行)
- `er018_output/fiction_external_seed_selection_criteria_trial_02/
  stories/03_japanese_lit_2/{seed.json,story_prompt.txt,rights_check.md}`
- `er018_output/fiction_external_story_seed_trial_01/stories_all.md`
- `er018_output/fiction_real_story_and_true_crime_trial_01/true_crime/
  naming_rule_diff.md`(commit `6c0b0e02`)
- `CURRENT_SPEC.md` 974-1076行(Family C Production節)、1080-1109行
  (Cross-level仕様表)
- `DECISION_LOG.md` 7890-7928行(Family横断共通化原則・Family C言及)、
  9319-9327行(Future→Fiction再定義未確定)、7433-7483行(Family C/
  Discovery/Voicesコスト実績)
- `er003_v1_n3_01_scaffold_generate.py` 78-179行(`split_article_text`
  等)
- `er013_family_c_production_01.py`、`er013_family_c_production_runner_01.py`
- `er020_tts_retry_local_rewrite_01.py` 85-165行(role taxonomy)
- 外部公開資料: https://ja.wikipedia.org/wiki/走れメロス 、
  https://www.aozora.gr.jp/cards/000035/card1567.html 、
  https://en.wikipedia.org/wiki/Copyright_law_of_Japan 、
  https://copyright.cornell.edu/publicdomain
  (全件2026-09-26確認、HTTP 200、直接HTTP GET・web_search不使用)
