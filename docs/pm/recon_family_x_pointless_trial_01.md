# recon_family_x_pointless_trial_01.md

管理ID: NEWS-FAMILY-X-POINTLESS-TRIAL-01 / Phase A(read-only 調査、¥0、API呼び出しなし)
作成: 2026-09-26

本文書はPhase A(調査+設計のみ)の成果物。実装・API呼び出しは一切行っていない。
事実(コード引用・行番号)と推測(設計提案)を明示的に分離する。

---

## A-1. 現行Family A構造の実体

### 記事contract(Writer側)
- `er003_v1_n3_01_articles_generate.py:154-166`(COMMON_BLOCK_TEMPLATE内
  「記事構成」節): `# Title` → Main Story(複数段落) → `###`見出し
  ちょうど2つ(Point One相当/Point Two相当) → `## In one line...`。
- `er003_v1_n3_01_advanced_adaptation_generate.py:30,125-127`: Meta記事は
  この「元Ledger駆動Writer」ではなく、JA記事→EN Advanced Adaptation
  (`generate_advanced_adaptation`)経由で生成されているが、**同じcontract
  (`###`ちょうど2つ、"Point One"等のラベル文字列禁止)を`validate_point_
  structure()`でGateしている**(:253「validate_point_structure()による
  contract構造Gate(###見出しちょうど...」)。

### 本文分割(2分割)
- `er003_v1_n3_01_scaffold_generate.py:104-159` `split_article_text()`。
  `###`見出しが**ちょうど2つ**であることをhard要求(:108-110、異なれば
  `RuntimeError`)。Main Story部分(`intro_text`)を`\n\n`段落単位で
  分割し(:137)、累積語数差`abs(running - (total-running))`が最小になる
  境界を選んで2分割する(:140-152、「意味の切れ目・Volume均等」の実装)。
  これがユーザー指示にある「同じ考え方」の実装本体であり、3分割への
  拡張時にそのまま流用できるロジック(境界候補をn-1個に増やすだけ)。

### Comment生成(b1_support_generation/a2_support_generation)
- 呼び出し元: `er003_v1_n3_01_scaffold_generate.py:367-432`
  `run_b1_scaffold()`(英語Comment、`b1s.COMMENT_1_ROLE`等を再利用)、
  `:438-470` `run_a2_scaffold()`(日本語Comment、`a2gen.COMMENT_1_ROLE`等)。
- Roleテキスト本体: `er003_v1_b1_scaffold_01_generate.py:146-191`
  (B1、英語)、`er003_v1_iran01_a2_generate.py:127-172`(A2、日本語)。
  - Comment 1(:146-154 / :127-135): 「本文の前半を聞く直前」向け
    Listening Focus。Point/構造ラベルへの言及なし。**Point前提なし
    →そのまま流用可**。
  - Comment 2(:156-165 / :137-146): 「前半を聞き終え、後半へ」向け
    Mid-story Recovery。Point前提なし→**そのまま流用可**。
  - Comment 3(:167-177 / :148-158): 「本文全体を聞き終え、これから
    Point One・Point Twoを聞く」ことを明示前提とし、役割名自体が
    "Story Meaning + **Bridge to Points**"。「これから聞くPointへの
    橋渡しをします」「Pointの具体的な内容(答え)を先に言っては
    いけません」という文言がある。**Point前提が強く残存
    →コピーして変更が必要**(「Bridge to Points」を「Bridge to
    Full Story Part 3」等へ、"Point"の言及を除去)。
  - Comment 4(:179-191 / :160-172): 「Point One・Point Twoを聞き終え、
    In One Lineへ」向け、役割名"**Point Recovery** + Bridge to In One
    Line"。「2つのPointの意味を軽く回収し」という文言。**Point前提が
    強く残存→コピーして変更が必要**(Part 3の回収+In One Lineへの橋渡し、
    に差し替え)。
  - context組み立て側(呼び出し元)も同様にPoint前提: N3-01 scaffold
    の`run_b1_scaffold`/`run_a2_scaffold`内でComment 3/4のcontextに
    `point_one_heading`/`point_two_heading`/`point_one_body`/
    `point_two_body`を明示的に渡している
    (`er003_v1_n3_01_scaffold_generate.py:384-394,404-411,447-450,454-455`)。
  - A2専用のComment 3 role(`A2_COMMENT_3_ROLE_N3`、:166-179)も
    「これからPoint One・Point Two(補足の視点)を聞きます」「Point Oneの
    見出しが示す視点に軽く触れる程度は許容」と、B1版よりさらに強く
    Point構造前提(N3-01固有の追加仕様、spec 25節由来)。

### Assembly timeline(effect音位置・見出し読み含む)
- B1: `er003_v1_n3_01_assemble.py:677-733` `build_b1_timeline()`。
  実際のsegment列(効果音・pauseを含む正確な順序):
  Intro → Welcome → Topic intro → Notification 1 → Preview intro →
  Preview → Notification 2 → Key phrases intro → Key Phrase 1-5 →
  Notification 3 → Full story intro → **Comment 1 → Full Story Part 1
  → Comment 2 → Full Story Part 2 → Comment 3(Bridge)** →
  **Point Notification(効果音) → Point One heading → Point One →
  Point Notification(効果音) → Point Two heading → Point Two** →
  Comment 4 → In One Line → Outro。
- A2: `:877-937` `build_a2_timeline()`。構造は同型(Japanese title・
  Point explanation segmentが追加される以外はB1と同じ順序)。
- Point Notification効果音(:39 `POINT_NOTIFICATION_MP3_PATH`)は
  Point One/Two導入の直前にのみ挿入される(:716-717,721-722、
  :919-921,925-926)。Comment 1→2、Comment 2→3の間には挿入されない
  (Comment 3→本文3の接続にはこの効果音は使われていない=ユーザー指示
  「新しい効果音を追加しない」と整合、Point Notification自体を
  Family Xで使わなければ良いだけ)。
- pause定数: `AOEDE_TO_CHARON_PAUSE_SECONDS`/`CHARON_TO_AOEDE_PAUSE_
  SECONDS`(:50-51、Comment↔本文間の間)、
  `HEADING_TO_BODY_PAUSE_SECONDS_B1`/`c.POINT_EXPLANATION_PAUSE_SECONDS`
  (見出し→本文間、Point見出し専用)。Family Xは見出しを持たないため、
  この見出し用pauseは不要(Comment↔本文の間だけ既存値を流用すればよい)。

### player.html生成
- `er012_e_family_entertainment_two_level_runner_01.py:404-458`
  `_row_info_b1b()`、:461-516 `_row_info_a2()`: `label.startswith(...)`
  によるsegment名→表示情報のマッピング。Point One/Two関連の分岐
  (:446-455,504-513)はlabel文字列一致で判定しており、汎用部分
  (`player_common.render_timeline_row/table`等、`audio_review_player.py`)
  自体はPoint非依存の汎用ヘルパー。**Family X用には`_row_info_family_x`
  相当の新関数が必要(Point分岐をFull Story Part 3分岐へ差し替え)だが、
  低レベルの`player_common`(:54 import)はそのまま流用可**。

### Audio Validation / retry / regeneration
- Gate本体: `er003_v1_n3_01_assemble.py:469-523`
  `verify_episode_audio_validation_gate()`。`tts_generation_results.json`
  の`segments`/`key_phrases`を読み、status/disfluency QA/A2 slowdown/
  asset hashを検証する汎用関数。**segment名のハードコードはこの関数
  自体には無く**、正本は別辞書(下記)。
- `DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL`(:167-189、キー"B1"/"A2"/
  "B_FAMILY_A2")に`point_one_heading`/`point_two_heading`等がハード
  コードされている。Family Xはここに新しいキー(例"FAMILY_X_B1"/
  "FAMILY_X_A2")を**追加**すれば足りる(既存キーは無変更)。
- `A_FAMILY_B1_REQUIRED_SEGMENTS`/`A_FAMILY_A2_REQUIRED_SEGMENTS`
  (:354-369)+`derive_a_family_required_structure()`(:372-382)が
  OPEN-129構造完全性チェックの正本。Family Xは別関数
  (`derive_family_x_required_structure()`)を新規追加すればよい
  (既存関数は無変更)。
- Point-only regeneration(`er008_point_regenerate_19.regenerate_point_
  only`)はProduction自動経路から既に撤去済み
  (`er003_v1_n3_01_articles_generate.py:710-729`
  `POINT_ONLY_REGENERATION_ENABLED = False`)。**現在は「検出のみ、
  本文は変更しない」状態**であり、Family Xがこれを気にする必要は無い。
- Point overlap QA/Point Value QA/Diagnostic Full Retry
  (`run_point_overlap_qa_and_regenerate()`:732-800、`run_one_pattern()`
  内のretryループ:911-983)は、**元Ledger駆動Writer(`run_one_pattern`)
  経由の記事生成にのみ存在する**。実際に確認したところ、Meta記事が
  使うE-Family runnerの生成関数(`er003_v1_n3_01_advanced_adaptation_
  generate.py`・`er003_v1_n3_01_standard_a2_generate.py`)には
  `overlap_qa`/`point_regen`/`point_planning`への参照が**一切無い**
  (grep確認、0件)。Family Xが「既存Family A記事(Meta)を再利用し
  Point節を除去するだけ」という設計を採る限り、この一群の複雑な
  QA/retry機構には一切触れない。

### E2E runner(er012_e_family_entertainment_two_level_runner_01.py)
- stage構成: ledger→writer→scaffold→tts→assemble→player
  (:629-630 `--stage`選択肢)。各stageは`sc`/`tts_gen`/`asm`モジュールの
  関数を素のままimportして呼ぶ薄いラッパー(:369-398)。
- budget guard: `assert_budget_ok()`(:143-149)が各stage後に
  `raw_usage_log.jsonl`から累計JPYを計算し、`--budget-jpy`超過で
  `RuntimeError`停止。
- TTS mode: 既定`STANDARD`(:632-634、`--tts-mode`引数)、`BATCH`指定時は
  `--batch-reason`必須(:645-647、PM_GOVERNANCE 7-2)。

### 実測segment列(Meta、b1b、`er012_output/e_family_two_level_wiring_01/
meta/b1b/audit/timeline.json`より)
Intro(10.7s)→Welcome(2.1s)→...→Preview(19.9s)→...→Key Phrase 1-5
(各7.5-9.8s)→...→Comment 1(4.3s)→Full Story Part 1(23.0s)→
Comment 2(7.9s)→Full Story Part 2(27.5s)→Comment 3(10.7s)→Point
Notification→Point One heading(3.2s)→Point One(20.1s)→Point
Notification→Point Two heading(3.6s)→Point Two(44.4s)→Comment 4
(13.3s)→In One Line(6.2s)→Outro(6.1s)。総尺320.6s(A2実測、
`meta/a2/run_summary_assemble.json`)。

語数(`meta/b1b/parts.json`実測、正規表現`[A-Za-z']+`ベース):
part1=68語、part2=59語、point_one_body=50語、point_two_body=115語、
in_one_line=17語(Main Story合計=127語)。
比較用(元Ledger駆動THEMES、`er003_output/n3_01/{hanshin,health,
household}/b1b/parts.json`実測): hanshin part1=101/part2=107、
health part1=109/part2=116、household part1=118/part2=100
(Main Story合計はいずれも200-230語程度、Point本文は36-48語程度)。
**Metaの Main Story(127語)は元Ledger駆動記事(200-230語)よりかなり
短い**(JA→EN Advanced Adaptationの性質、`TOTAL_SOFT_LOWER/UPPER`
[280-420語、`er003_v1_n3_01_articles_generate.py:62-63`]はMeta生成
経路には適用されていない)。3分割時の1パートあたり語数に直結する
重要な観察(A-3で詳述)。

---

## A-2. Point前提の残存箇所一覧

| レイヤ | ファイル・関数・行 | Point前提の有無 | Family X対応 |
|---|---|---|---|
| Writer Prompt(Ledger駆動) | `er003_v1_n3_01_articles_generate.py:153-237`COMMON_BLOCK_TEMPLATE | 強(構成必須、役割定義、重複禁止ロジック全体がPoint専用) | **使わない**(Family Xは記事を再生成しないため対象外) |
| Writer Prompt(Advanced Adaptation) | `er003_v1_n3_01_advanced_adaptation_generate.py:125-127`+`validate_point_structure()` | 強(###ちょうど2つのGate) | **使わない**(既存article.md再利用) |
| Comment 1 Role | `er003_v1_b1_scaffold_01_generate.py:146-154`/`er003_v1_iran01_a2_generate.py:127-135` | 無 | そのまま流用可 |
| Comment 2 Role | 同:156-165/137-146 | 無 | そのまま流用可 |
| Comment 3 Role | 同:167-177/148-158 + N3-01専用A2版:166-179(scaffold_generate.py) | 強("Bridge to Points"、Pointへの言及複数) | コピーして変更(文言差し替え) |
| Comment 4 Role | 同:179-191/160-172 | 強("Point Recovery"、"2つのPointの意味を軽く回収") | コピーして変更(文言差し替え) |
| Comment3/4 context組立 | `er003_v1_n3_01_scaffold_generate.py:384-411,447-455` | 強(`point_one_heading`等を直接渡す) | コピーして変更 |
| schema/parser(記事分割) | `er003_v1_n3_01_scaffold_generate.py:104-159`split_article_text | 強(###ちょうど2つhard要求) | コピーして変更(3分割対応の新関数、`###`0個を前提) |
| schema/parser(Point QA用) | `er003_v1_n3_01_articles_generate.py:687-707`split_common_sections_for_point_qa | 強 | 使わない(Family Xは呼ばない) |
| validator(TTS入力Point番号ラベル禁止) | `er003_v1_n3_01_scaffold_generate.py:74-101`assert_no_point_number_label/clean_heading | 中(Point前提だが機能自体は「番号ラベルが万一残っていないか」の安全網) | そのまま流用可(呼ばなくても実害無いが、Comment文言の安全網として呼んでもよい) |
| audio segmentation(timeline) | `er003_v1_n3_01_assemble.py:677-733`build_b1_timeline/:877-937 build_a2_timeline | 強(Point Notification効果音・見出しsegmentが構造に組み込み) | コピーして変更(新規`build_family_x_*_timeline`) |
| audio segmentation(TTS生成) | `er003_v1_n3_01_tts_generate.py:692-809`generate_b1_segments/:815-939 generate_a2_segments | 強(point_one/two/heading専用ループ) | コピーして変更(新規`generate_family_x_*_segments`、低レベルヘルパーはそのまま呼ぶ) |
| retry/regeneration(Point-only) | `er008_point_regenerate_19.py`+`POINT_ONLY_REGENERATION_ENABLED=False`(articles_generate.py:729) | 強だが**現在Production非経路**(検出のみ) | 使わない(Family Xは呼ばない、既にFalseで無効) |
| retry/regeneration(overlap/value QA) | `run_point_overlap_qa_and_regenerate`等(articles_generate.py:732-983) | 強、**ただしE-Family runner(Meta経路)は元々未使用** | 使わない(Family Xは記事非生成のためそもそも該当なし) |
| fallback(Advanced/Standard deviation retry) | `er012_e_family_entertainment_two_level_runner_01.py:278-293,326-338` | 無(Point非依存、記事全体のFact deviationのみ) | 使わない(Family Xは記事非生成) |
| preview page(player.html row info) | `er012_e_family_entertainment_two_level_runner_01.py:404-458,461-516` | 強(label文字列分岐にPoint One/Two heading/bodyの分岐) | コピーして変更(新規`_row_info_family_x_*`) |
| preview page(共通描画ヘルパー) | `audio_review_player.py`(`player_common`、render_timeline_row/table等) | 無 | そのまま流用可 |
| Audio Validation Gate本体 | `er003_v1_n3_01_assemble.py:469-523`verify_episode_audio_validation_gate | 無(segment名は外部辞書経由) | そのまま流用可(関数自体は無変更で呼べる) |
| Audio Validation Gate(必須post-process正本) | `DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL`(:167-189) | 強(point_one_heading等が値として直書き) | **追加のみ**(新キー"FAMILY_X_B1"/"FAMILY_X_A2"を追加、既存キー無変更) |
| Audio Validation Gate(構造完全性正本) | `A_FAMILY_B1/A2_REQUIRED_SEGMENTS`+`derive_a_family_required_structure`(:354-382) | 強 | **追加のみ**(新関数`derive_family_x_required_structure`を追加) |
| E2E orchestration | `er012_e_family_entertainment_two_level_runner_01.py`全体 | 中(stage構成はPoint非依存だが、`run_writer_stage`/`_row_info_*`はPoint前提のFamily A固有関数を直接呼ぶ) | 新規runner(`er019_family_x_pointless_runner_01.py`想定)を書き、writer stageは「既存article.md読み込み」に差し替え、scaffold/tts/assembleは新規Family X版関数を呼ぶ |

### 結論(A-2): Family A側を変更せずにFamily X経路として成立させられるか
**成立する。** Point前提が強く残る箇所(Comment 3/4 Role、記事分割
parser、timeline builder、TTS segment生成、player.html row info、
E2E runner)は、いずれも**呼び出し側(Family X専用の新規モジュール)で
コピーして変更すれば足り**、Family A側の既存関数・定数を書き換える
必要が無い。唯一「追加のみ」で済む箇所が2つある
(`DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL`辞書への新キー追加、
`A_FAMILY_*_REQUIRED_SEGMENTS`と並ぶ新関数の追加)。これらは
`er003_v1_n3_01_assemble.py`という**Family Aと共有のファイル**への
軽微な追記であり、既存キー・既存挙動には触れないが、「ファイルとして
共有」である点はPhase Bの実装方針としてFable/ユーザーに明示すべき
判断ポイント(STOP候補ではないが要確認事項、B節参照)。

**STOP候補は無い**(Parser/schema大規模再設計・Production Family A変更は
不要という結論)。

---

## A-3. Family X設計案(最小差分)

### 新モジュール案
- `er019_family_x_pointless_runner_01.py`(新規、E2E runner本体):
  `er012_e_family_entertainment_two_level_runner_01.py`のstage構成
  (ledger→writer→scaffold→tts→assemble→player)を踏襲するが、
  writer stageは「既存Family A article.mdを読み込み、`### `節を除去
  した本文をそのまま使う」処理に差し替える(下記参照)。
- `er019_family_x_scaffold_01.py`(新規): 3分割ロジック
  (`split_article_text_3way`)、新Comment 3/4 Role文言、Comment生成
  ラッパー(`run_b1_scaffold_x`/`run_a2_scaffold_x`、既存`b1s.run_
  support_text`/`a2gen.run_support_text`をそのまま呼ぶ)、Key Phrase
  選定(`er003_v1_n3_01_scaffold_generate.py`の`run_key_phrases`等を
  そのままimportして再利用、Point節を含まない新しいarticle_textに対し
  再選定する)。
- `er019_family_x_tts_01.py`(新規): `generate_family_x_b1_segments`/
  `generate_family_x_a2_segments`。低レベル生成関数(`voice01.
  generate_charon_english`、`news_tail_fix.generate_news_narration_
  wide_margin`、`generate_a2_segment_with_slowdown`、`generate_a2_
  japanese_with_reading_safety`、`shared_narration.ensure_all_shared_
  narration_*`等)は`er003_v1_n3_01_tts_generate.py`からそのまま
  importして呼ぶ(モジュール自体は無変更)。
- `er019_family_x_assemble_01.py`(新規): `build_family_x_b1_timeline`/
  `build_family_x_a2_timeline`(Point Notification・見出しsegment・
  Point本文を除去し、Full Story Part 3を追加)、`apply_family_x_b1_
  gain`/`apply_family_x_a2_gain`(既存`apply_b1_gain`/`apply_a2_gain`
  とほぼ同型、対象segment名リストのみ変更)。Audio Validation Gate
  呼び出しは`er003_v1_n3_01_assemble.py.verify_episode_audio_
  validation_gate`をそのまま呼ぶ(無変更で呼べる、A-2参照)。

### 記事本文の再利用方針(推奨: 既存記事流用)
ユーザー指示「無駄な再生成を避ける」「元ニュース本文を3分割するだけ」
に従い、**新しいWriter呼び出しは行わず、既存Family A版article.md
(Meta等)からMain Story部分(`### `より前、Title直後〜1つ目の`###`
まで)だけを抽出し、そのまま3分割の入力にする**。Point節
(`### `〜`## In one line`前)は完全に破棄する(内容も転用しない)。
これは`split_article_text()`(scaffold_generate.py:104-159)の
`intro_text`抽出ロジック(:115)と同じ正規表現を使えば機械的に取り出せる
(Writer再呼び出し不要、追加コスト¥0)。

Meta本文がPoint節の存在を前提に書かれているか: Meta article.md
(`er012_output/e_family_two_level_wiring_01/meta/b1b/article.md`)の
Main Story部分を確認したところ、Point節への直接の言及・接続語
("as we'll see next"等)は無く、Main Story単体で意味が完結している
(Point One/Twoは「本文とは別の切り口」という独立した補足という設計
[`COMMON_BLOCK_TEMPLATE`:184-196]のため、本文側がPointに依存する構造
にはそもそもなっていない)。したがってMain Story単独流用は安全。

### 3分割ロジック(拡張案)
`split_article_text()`の2分割ロジック(:140-152)をn分割へ一般化する:
段落境界の累積語数から、3分割点(2つの境界)を「各パートの語数分散が
最小になる組」で選ぶ(動的計画法、または段落数が少ない[実測: Meta
本文は2段落×2ブロック=4段落程度]場合は全境界の組み合わせを総当たりで
評価しても計算量上問題ない)。Volume偏り指標としては、既存の
「隣接差の絶対値最小化」を3パートの標準偏差最小化、または最大パートと
最小パートの語数差最小化、のいずれかに一般化する(実装時に確定、
Phase B)。

**重要な設計上の懸念(観察、A-1参照)**: Metaの現行Main Story本文は
127語しかなく、3分割すると1パートあたり平均42語程度になる
(現行part1/part2は各59-68語)。42語は現行Comment(1〜2文、短い)より
やや長い程度で、音声としては短め(実測比率から概算: 68語=23.0秒
→42語なら約14秒程度)。極端に不自然な短さではないが、現行のFull Story
Part(20-30秒程度)より明確に短くなる。一方、元Ledger駆動記事
(hanshin/health/household、Main Story 200-230語)なら3分割で1パート
70-77語となり、現行part1/part2(59-118語)とほぼ同等の長さを保てる。
**対象記事の選定判断に直結するため、A-3末尾で両論併記する。**

### Comment役割再定義(差し替え文言、逐語案)
Comment 1・2は無変更で流用(role文言・context組み立てとも既存のまま、
「本文の前半/後半」という言い方は2分割/3分割どちらでも意味が通る
汎用表現のため)。

Comment 3(新設、`FAMILY_X_COMMENT_3_ROLE`案、B1版。現行:167-177の
「Bridge to Points」部分のみ書き換え、他の制約[構造ラベル禁止等]は
維持):
> 「あなたはPodcastのナビゲーターです。リスナーは本文の第1部・第2部を
> すでに聞き終わり、これから本文の第3部を聞きます。その間に流す、
> Comment 3(役割: Mid-story Recovery + Bridge to Part 3)を書いて
> ください。役割: ここまでの内容の核心を短く整理し、第3部で何を聞けば
> よいかを示します。第3部の結論を先に言ってはいけません。新しいFactを
> 追加しないでください。2〜3文にしてください。」
(A2版は同内容を日本語出力指示へ差し替え、現行の`A2_COMMENT_3_ROLE_N3`
[scaffold_generate.py:166-179]が持っていた「Point見出しへの先出し許容」
条項は削除する[Point自体が存在しないため])。

Comment 4(新設、`FAMILY_X_COMMENT_4_ROLE`案、現行:179-191の
「Point Recovery」部分を書き換え):
> 「あなたはPodcastのナビゲーターです。リスナーは本文の第3部を含む
> 本文全体をすでに聞き終わり、これからIn One Line(結びのまとめ)を
> 聞きます。その間に流す、Comment 4(役割: Story Recovery + Bridge to
> In One Line)を書いてください。役割: 記事全体の意味を軽く回収し、
> In One Lineへつなぎます。本文を再説明しすぎないでください。2〜3文に
> してください。」
(既存の「sentence数を断定しない」注意書きはそのまま維持)。

Comment数は4のまま(ユーザー指示通り、増減しない)。

### Assembly timeline(新規、Point Notification効果音・見出し無し)
```
...Comment 3(Charon/日本語)
→ pause(既存Comment→Aoede間pauseをそのまま流用)
→ Full Story Part 3(Aoede)
→ pause(既存Aoede→Charon間pauseをそのまま流用)
→ Comment 4(Charon/日本語)
→ pause → In One Line → pause → Outro
```
Point Notification効果音・Point見出しsegment・見出し→本文pauseは
一切挿入しない(新規効果音も追加しない、ユーザー指示通り)。

### Audio Validation/retry/Lock
`verify_episode_audio_validation_gate()`をそのまま呼ぶ(A-2参照)。
`DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL`への新キー追加が必要
(具体的な対象segment案: B1は`("preview","comment_1","comment_2",
"comment_3","comment_4","in_one_line")`、Point見出しが無いため
現行B1キーからpoint_one_heading/point_two_headingを除いたセット。
A2は現行が`("in_one_line","point_one_heading","point_two_heading")`
のみだったため、Family X A2は`("in_one_line",)`のみ、というように
Familyごとに対象が変わる点は実装時に要精査)。`A_FAMILY_*_REQUIRED_
SEGMENTS`と並ぶ新規`FAMILY_X_B1/A2_REQUIRED_SEGMENTS`タプルの追加も
必要。

### player.html
`player_common`の低レベル描画関数(`render_timeline_row`/
`render_timeline_table`/`PLAYER_STANDARD_CSS`/`SEEK_SCRIPT`/
`abs_file_url`/`render_single_audio_html`)はそのまま流用可
(Point非依存の汎用ヘルパー、A-2確認済み)。`_row_info_b1b`/`_row_info_
a2`相当の新関数(`_row_info_family_x_b1b`/`_row_info_family_x_a2`)を
新規作成し、Point One/Two分岐をFull Story Part 3分岐へ差し替える。

### レベル: B1/A2両方 or まず1レベルか
Phase Bはまず**B1(Advanced)1レベルのみ**を推奨する。理由: (1)
ユーザー指示は「1記事のみ」であり構造比較が主目的、B1単体でも
Comment/3分割/Assembly/Gateの新規実装は全て検証できる、(2) A2は
6% slowdown・日本語Comment・Japanese title等B1と異なる後処理が多く、
1レベルで構造が固まってから横展開する方が手戻りが少ない、(3) コストを
半分に抑えられる(下記見積り参照)。ただしユーザー/Fableが両方同時
希望する場合は技術的に問題なく両方実装できる(A2固有の複雑さは
「既存のA2生成関数をそのまま呼ぶ」ことで吸収されるため、Family X固有の
新規実装はB1もA2も同程度の追加工数)。

### コスト見積り(TTS STANDARD)
Meta実績(2レベル、Ledger reuse+Writer×2+Scaffold+TTS+ASR一式)は
`raw_usage_log.jsonl`実測で合計¥72.62(内訳: gemini ¥51.31
[TTS/Comment等]、openai ¥13.92、openai_asr ¥7.38、
`compute_cost_jpy_so_far()`と同一ロジックで実測計算、Writer単体の
cost_usd/cost_jpyは`writer_run_summary.json`実測でadvanced=¥0.305、
standard=¥0.962と無視できる水準)。

Family Xは以下の理由でMeta実績より**segment数が正味減る**
(1レベルあたり): 除去= point_one_heading・point_two_heading・
point_one・point_two(4 segment、Meta実測ではPoint本文だけで
165語相当の音声)、追加= full_story_part3(1 segment、既存記事流用なら
Meta本文で約42語、元Ledger駆動記事なら70-77語)。Comment/Preview/Key
Phrase segment数は変わらない(4 Comment+Preview+KP 5件×2=10)。

- **1レベル(B1のみ)概算**: Ledger再利用(¥0、reuse_ledger_file
  使用)+Writer呼び出し無し(既存article流用、¥0)+Scaffold
  (Comment×4+Preview+KP選定/正規化/冗長性QA、Meta実績の概ね半分弱)+
  TTS(part1/2/3+Comment×4+Preview+KP10件、Point系4segment分のコスト
  減を差し引き)+ASR検証。Meta実績の「1レベル分」を粗く按分すると
  ¥72.62の半分弱(¥25-35程度)からPoint除去分を差し引いた
  **¥20-30程度**を目安とする(実測ではなく按分推定、Phase B実行時に
  `raw_usage_log.jsonl`で確定させる)。
- **2レベル(B1+A2)概算**: 上記の概ね2倍、**¥40-60程度**。
- いずれも`--budget-jpy`引数(新runnerに実装、A-5参照)でPM_GOVERNANCE
  7-5の安全装置として明示的な上限を設定する。想定より大きく外れる
  兆候(異常なASR retry連発等)が出た場合はAPI呼び出し前にSTOPする
  (既存`assert_budget_ok()`と同型の実装を新runnerにも入れる)。

### 対象記事の選定
ユーザー指示は「Meta」を第一候補として提示している。理由(ユーザー
指示通り): 既存Family A版がb1b/a2両方でassemble OK
(`meta/b1b,a2/run_summary_assemble.json`ともにstatus="OK"、実測確認
済み)、JA原文があり由来管理IDも明確(`entry_point.json`)。

比較候補: `er003_output/n3_01/{hanshin,health,household}/{b1b,a2}`
(元Ledger駆動THEMES記事)も同様に両レベルassemble OK
(実測確認済み)。**Main Story語数の観察(A-1参照)により、これらの方が
3分割後の1パートあたり語数(70-77語)がMeta(42語)より現行part1/part2
に近く、3分割の「Volume均等」比較検証としてはより典型的なケースに
なる**。一方、MetaはJA→EN Advanced Adaptation経路(Production採用中の
主力経路)の実例であり、その経路での検証に意味がある。

**推奨**: Fable/ユーザーが「短い本文でも3分割が破綻しないか」を見たい
ならMeta、「現行part1/part2と近い尺での3分割比較」を見たいならhanshin
等元Ledger駆動記事。いずれもデータ上は実行可能で、STOP要因ではない。
Phase Bの実行前にFable/ユーザーの選好を確認することを推奨する
(判断そのものはPhase A範囲外)。

---

## A-4. テスト計画

新runner(`er019_family_x_*`)向けunit test案:
1. **3分割Volumeバランス**: 既知の段落構成を持つfixtureテキストに対し
   `split_article_text_3way()`を実行し、各パートの語数が
   (a) 空でないこと、(b) 最大パートと最小パートの語数差が総語数の
   一定割合(閾値は実装時に確定、既存2分割の実測差から妥当な値を選ぶ)
   以内であることを検証。
2. **Point文言不在チェック**: 生成されたComment 3/4テキスト
   (fixtureまたは実際の生成結果)に"Point One"/"Point Two"/
   "Point 1"/"Point 2"/「第一に」/「第二に」等が含まれないことを、
   既存`_POINT_NUMBER_LABEL_ANYWHERE_RE`
   (`er003_v1_n3_01_scaffold_generate.py:90-91`)を流用して機械検証。
3. **timelineにpoint_*が無いこと**: `build_family_x_b1/a2_timeline()`
   の返り値(part名リスト)に`"Point"`という文字列を含むpartが
   一切無いことをassert(Point Notification効果音・見出し・本文の
   いずれも存在しないことの構造的保証)。
4. **Family Aモジュール未変更であることの検証**: (a) import hashチェック
   ——`er003_v1_n3_01_scaffold_generate.py`/`er003_v1_n3_01_assemble.py`/
   `er003_v1_n3_01_tts_generate.py`/`er012_e_family_entertainment_two_
   level_runner_01.py`の実装開始時点でのsha256を記録し、Phase B完了後に
   再計算して一致を確認(`DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL`
   辞書への新キー追加分だけ差分が生じる想定であれば、diffの内容が
   「新キー追加のみ」であることをgit diffで目視確認するテストとして
   記録)。(b) 既存Family A(Meta)のtimeline/parts.json/player.htmlの
   内容が、Family X実装後に再実行しても既存ファイルと完全一致する
   ことを確認する回帰チェック(Family X追加が既存出力に影響しない
   ことの実測証拠)。

---

## A-5. TTS mode

新runner設計は、`er012_e_family_entertainment_two_level_runner_01.py`
(:632-637,645-647)と同型のCLI引数を持つべきである:
- `--tts-mode STANDARD|BATCH`(既定`STANDARD`、`TTS_EXECUTION_MODE`
  環境変数へ設定)。
- `--tts-mode BATCH`使用時は`--batch-reason`必須(未指定はargparse
  `error`で停止、PM_GOVERNANCE.md 7-2の例外条件該当理由を明記させる)。
- `--budget-jpy`(既定300.0、`assert_budget_ok()`同型のガード関数を
  各stage後に呼ぶ)。
Phase Bではこれら3引数を新runnerにそのまま実装することを設計方針
とする(既存runnerの`build_arg_parser()`パターンを踏襲、コピーして
Family X固有部分[--slug等]だけ調整)。

---

## Phase B実装の変更一覧・見積り(¥)・STOP候補

### 変更一覧(新規作成のみ、既存ファイルへの追記は2箇所に限定)
新規作成:
- `er019_family_x_pointless_runner_01.py`(E2E runner)
- `er019_family_x_scaffold_01.py`(3分割・Comment・KP wrapper)
- `er019_family_x_tts_01.py`(TTS segment生成)
- `er019_family_x_assemble_01.py`(timeline・gain・assemble)
- 各種unit test(`er019_test_family_x_*`)

既存ファイルへの追記(既存キー・既存関数は無変更、新規追加のみ):
- `er003_v1_n3_01_assemble.py`の`DISFLUENCY_QA_MANDATORY_SEGMENTS_
  BY_LEVEL`辞書へ新キー追加(例"FAMILY_X_B1"/"FAMILY_X_A2")
- 同ファイルに`derive_family_x_required_structure()`(または同等の
  新関数)を追加(既存`derive_a_family_required_structure()`と並置)

上記2点は「Family Aと共有のファイルへの追記」であり、Family Aの
既存動作には影響しないと判断するが(理由: 既存キー・既存関数を
一切変更しない、新規キー/新規関数の追加のみ)、共有Productionファイル
である以上、Phase B開始前にFable/ユーザーへ一言確認を推奨する
(代替案: 完全に独立した新モジュールへGateロジック自体を複製し、
共有ファイルへは一切触れない設計も可能。コード重複は増えるが
「Family A用ファイルに一切触れない」を文字通り満たせる。この二択は
Phase B着手前にFable/ユーザーが選択することを推奨)。

### 見積り(¥)
- Phase B実装自体(コード作成・fixtureベースのunit test)は¥0
  (API呼び出しを伴わない)。
- 1記事・B1のみのE2E実行: 概算¥20-30(A-3参照、按分推定であり実測
  ではない)。
- 1記事・B1+A2のE2E実行: 概算¥40-60。
- 実行前に`--budget-jpy`で明示上限を設定し、PM_GOVERNANCE 7-5
  (差分再生成/reuse/想定外全再生成はAPI前STOP)に従う。

### STOP候補
**無し。** 以下を確認済み:
- Production Family Aへの変更は不要(A-2結論、既存キー/関数は
  無変更のまま新規追加のみで足りる)。
- Parser/schema大規模再設計は不要(既存`split_article_text()`の
  ロジックをn分割へ一般化する程度で足り、既存2分割関数自体は
  変更しない[新関数として追加])。
- Point-only regeneration/overlap QA等の複雑な既存retry機構には
  Family Xが一切触れない(Meta経路[Advanced/Standard Writer]が
  元々これらを使っていないことをgrepで確認済み、Family Xは記事を
  再生成しないためさらに非該当)。

唯一の「要確認事項」(STOPではなく、Phase B着手前の確認推奨事項)は
上記の「共有ファイルへの追記2箇所」の是非、および「対象記事(Meta vs
hanshin/health/household)の選好」の2点。
