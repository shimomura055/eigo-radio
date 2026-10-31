# DESIGN_01 — 学習項目選定UI: Phrase/Word 出現回数の集計仕様と表示(設計。未実装・Production未変更)

管理ID: SELECTION-UI-OCCURRENCE-COUNT-01 / OPEN-632 / 委任_01 / 状態: 設計中(Opus条件Aレビュー前)
**【委任_02(2026-10-31)で実装済み。本書は設計原本として残す。差分】** (1)最終規則表=`RULES_01.md`(Opus必須M1-M6+推奨を反映。本書§2との差=1語項目の除外表該当形・前置詞兼用の不変化詞の分離形・人名スロットを保留へ、先頭be/have/doを確定へ、縮約'sを除外、sb/sth別名、S/U和集合)。(2)**exporterは既定ON**(Fable判断=表示方針は承認済み)。本書§7・§8-10の「`--with-occurrence`明示のみ」は撤回済みで、`--with-occurrence`は存在しない(止めるのは`--without-occurrence`のみ。手順書では使わない)。(3)集計関数=`er140_selection_occurrence_count_01.py`(提案名`er_selection_occurrence_count_01.py`から変更、既存`erNNN_*`命名に合わせた)。(4)実装・検証=`EVIDENCE_01.md`。
ユーザー原文: `docs/pm/delegation_log/2026-10-31_LEARNING-ITEM-QUALITY-TRIO-01_USER.md` §4。現状調査: `CURRENT_STATE_01.md`。精度検証: `PRECISION_01.md`(試作 `tools/occurrence_count_01.py` の実測)。

## 0. 結論(1段落)

回数は、**選定フォーム生成時に、記事×水準ごとの4区分(+タイトル)の英語本文へ決定論的に照合して数え、各候補entryの追加キー `occurrence` としてdata JSONに持たせる**(AI API 0円・難易度表示と同型の参考情報)。照合は **語(トークン)単位・大小無視・活用形は承認済みer105の活用表で前方生成・人称スロットは閉じた代名詞集合・句動詞の分離は間が代名詞1語まで**を「確定」、**それ以外で構造的に同じに見えるもの(名詞句が間/スロットに入る、前置詞かもしれない分離、活用済み語の他活用形)は「判定保留」として加算せず別枠で件数だけ記録**する(ユーザー原文§4-8「推測で加算しない」)。意味・用法(多義)の機械判別は行わない(原文「過剰な仕組みを作らない」)。既存データ(batch実member 27件・253項目)の実測では、確定ヒット335件のうち複数回出現する41項目の全ヒット(123件)と活用形等の非exact全件(7件)を全文確認して誤カウント0、緩い基準のoracle(45件)を人手分類して取りこぼし(確定すべきもの)0・境界1件、既存`occurrence_count`との不変条件は251/253一致(不一致2件は旧記録が古い実例)(`PRECISION_01.md`)。表示は各候補の日本語訳の下に1行(`出現 3回｜本文2・Comment1`)。選定条件・並び順・Done・コメント・入力保持・一括コピー・Claude受領形式は変更しない。

## 1. 設計判断(要約表)

| 論点 | 決定 | 根拠 |
|---|---|---|
| どこで数えるか | exportツール(`export_form_data_01.py convert()`)の中、候補→data JSON変換時 | support(Preview/Comment)はKP候補生成より前に存在(CURRENT_STATE §2)。AI呼出なし。data JSONに焼き込むので再表示・再開でも失われない(受入8) |
| 保存先 | 各member data JSONのentryごとに `occurrence`、記事ごとに `occurrence_meta`。**batch JSON(`data/batches/<id>.json`)は無変更**(members+member_sha256が既にデータ変更を封印) | 回数は記事×水準の情報。batchはmember列挙 |
| 付加方式 | 既存の `difficulty`(参考情報・照合コードに含めない)と同型 | `export_form_data_01.py:172`、`form_logic.js:102`。validateArticleは未知キーを許す(:321) |
| 数え方の単位 | 非重複の出現。1文に2回あれば2回 | |
| 同形異義・多義 | **判別しない**。字面・形が同一の用法を数え、構造が曖昧なものは保留 | 原文「完全に機械判定するために過剰な仕組みを作らない」。実測: 品詞割れ=1項目(shriek/shrieked=同一語彙素)のみ、誤カウント0 |
| lemmatize | 承認済み前方生成表(er105 `forms`/`IRR`/`_PLURAL_EXCLUDE`/`_PARTICIPIAL_ADJ_EXCLUDE`)を再利用。新依存なし | §2-4 |
| 数えない領域 | 日本語訳・説明文・KP解説・固定文・コメント欄(UI)・文境界/句読点/改行をまたぐ一致 | 原文§4-7 |

## 2. 集計規則 occ-v1

### 2-1. 入力(区分)
`story / comment / preview / oneline`(原文の4区分)+ `title`(別枠)。所在はCURRENT_STATE §2の表。**取得できない区分は `None`(未取得)**とし、0と区別する(`occurrence.unavailable`)。
- **title**: KP選定の入力本文にはタイトル行が含まれ、タイトル内の語句が候補になり得る(実データ253件中2件がタイトルのみ: `Now in Session`、`Putting on an Unwanted Show`)。原文の4区分には無いため、**合計(`total`)には含めず**、`counts.title` に別記録し、表示では0でないときだけ「タイトル」を添える(§4)。[判断: 承認範囲内の表示最適化(原文「見やすさを優先して最適化してよい」)。Opus観点7]
- Standard(a2)のPreview/Commentは日本語本文。英語トークンを含まず自然に0(別処理しない)。
- 日本語訳(`ja_gloss`/`meaning_ja`)・理由・文法解説・KP英文解説は**入力に渡さない**(関数の引数に含まれない=構造的に混入不能)。

### 2-2. トークン化と一致の基本
- NFKC正規化、曲線引用符→直線、`[A-Za-z0-9]+(-[A-Za-z0-9]+)*('[a-z]+)?` を1トークン(ハイフン連結語・`isn't` 等は1語、en/em dashは区切り)。小文字比較。
- 連続トークンの間の空白は**半角空白/タブのみ**許容(句読点・改行・文末・引用符・ダッシュをはさむ一致は不成立=文境界をまたがない)。
- 部分文字列一致は構造的に起きない(`in sight` が `insight` に、`put away` が `input away`/`put-away` に一致しない)。
- 所有格 `'s` は**パターン末尾の語にだけ**付いていてもよい(`campaign` が `campaign's` に一致。`er105 _phrase_pattern` が語境界で `'s` 前を許していた旧挙動と整合し、旧`occurrence_count`との不変条件を保つ)。

### 2-3. 一致の種類(確定 / 保留)

| rule | 内容 | 例(term <- 本文) | 扱い |
|---|---|---|---|
| exact | 本文実表現 `selection_phrase`(S)または表示形 `term`(U)とトークン完全一致 | `put away` <- `put away` | **確定** |
| lemma | Uの先頭の動詞位置・末尾の名詞位置・Sとの対応で差がある位置を活用形に展開 | `leave out` <- `left out`/`leaving out` ; `supplement` <- `supplements` | **確定** |
| slot_pron | 人称/目的語スロット語を閉じた代名詞集合で充足(下表) | `pull someone under` <- `pulled him under` ; `lose one's trust in someone` <- `lost her trust in him` | **確定** |
| sep_pron | 句動詞の動詞と不変化詞の間に**代名詞1語** | `put away` <- `put it away` / `putting something away` | **確定**(ただし不変化詞の直後が限定詞=前置詞の可能性 `put it on the table` は保留) |
| slot_np | スロットが名詞句(限定詞+1〜2語)で埋まる | `hold someone back` <- `hold the whole team back` | **保留(加算しない)** |
| sep_np | 句動詞の間に名詞句/他の語(1〜3語) | `leave out` <- `leaving things out`/`put the books away` | **保留(加算しない)** |
| revlemma | N5が基本形化していない活用済み語の**他の活用形** | `bothered` <- `bother`/`bothers`、`veiled` <- `veil` | **保留(加算しない)** |
| (不成立) | 間が4語以上、句読点/文境界をまたぐ、`the` への置換 (`draw a line` <-> `draw the line`)、派生語(`persuade`<->`persuasion`、`shrinkage`<->`shrinking`)、語の挿入(`make life work` <-> `make daily life work`) | | 数えない・保留にもしない |

人称/目的語スロットの閉じた集合(`er003 _PERSON_DEPENDENT_TO_GENERIC` と `er105 reference_pair_ok` の逆向きの展開。語の追加は承認事項):
- `someone/somebody` <- me, you, him, her, us, them, someone, somebody, one, I, he, she, we, they
- `one's/someone's/somebody's` <- my, your, his, her, its, our, their, one's, someone's, somebody's
- `oneself` <- myself, yourself, himself, herself, itself, ourselves, themselves, oneself, yourselves
- `something` <- it, this, that, them, these, those, everything, something, anything
- `a/an`(先頭以外の位置) <-> this, that, a, an。**`the` は含めない**(`er105 reference_pair_ok` と同じ)

N5連動(原文§4-5)の下限保証: **本文実表現 `selection_phrase` の完全一致は常に確定**で数える。N5形(`hear someone out`)が実表現(`hear it out`)と違っても、実表現の件数が下限になる。他の出現はN5形の位置展開(スロット/活用)で追加するだけ。

### 2-4. lemmatize方式の選択と根拠

| 案 | 判定 | 理由 |
|---|---|---|
| A. 承認済み前方生成表(er105 `forms`/`IRR`/`regular_forms`/`_IRREGULAR_PLURAL`)を再利用 | **採用** | 決定論・新規依存なし・KP正規化validatorとして既にProductionで承認済み・誤りの向きは「取りこぼし」側で、取りこぼしは保留枠に出せる |
| B. NLTK WordNet lemmatizer | 不採用 | wordnetコーパスがローカルに無く新規アセット依存。語形->基本形は得られるが品詞/語義は決まらない |
| C. spaCy等のモデル | 不採用 | 未導入・重い・モデル更新で出力が変わる(再現性) |
| D. NLTK品詞タガー(perceptron) | **集計には使わない**(評価oracleのみ) | MLで版により結果が変わる。Production依存を増やさない。誤カウント監査にだけ使用(`PRECISION_01.md` §4) |

展開を許す位置(過剰生成の抑制): ①先頭の内容語(動詞)・`to`/副詞(never,just...)の直後 ②末尾の内容語(名詞の複数/動詞) ③SとUの語が対応して異なる位置。**中間語・機能語(冠詞/前置詞/代名詞/助動詞/接続詞/疑問詞)は活用させない**。逆引き(活用済み->基本形)は `_verb_base_candidates`/`_plural_base_candidates`/`IRR` の候補を**前方生成で再現できたものだけ**採用し、`_PLURAL_EXCLUDE`(news->new等)・`_PARTICIPIAL_ADJ_EXCLUDE`(puzzling->puzzle等)は対象外。逆引きで得た他活用形は**保留**。

### 2-5. 分離句動詞(`put it away`)
- 対象: Uが「動詞(先頭) + 不変化詞(2語目、閉じた集合 away/out/up/down/off/on/in/over/back/around/apart/through/aside/along/together/forward)」で始まる表現。
- 間に入る語数: **1〜3語まで探索**(4語以上離れたものは別の構文として不成立)。**確定は代名詞1語のみ**(it/them/him/her/me/you/us/this/that/these/those/everything/something/anything/one)。それ以外(名詞句)は保留。
- 間なし(`put away your phones`)は通常のexactとして確定。
- 前置詞との曖昧さ: 代名詞が入っても不変化詞の直後が限定詞なら(`put it on the table`)保留。

### 2-6. 同形異義・判定不能の具体化(原文§4-4,8)
1. 判別**しない**もの(実害の見積り): 同綴りの多義(`in the way` の「邪魔」/「…する様子」、`put out`)、品詞違いの同綴(`bar`名詞/動詞)。実測(`PRECISION_01`): 複数回出現する41項目の全ヒットと非exact全件の人手確認で誤カウント0、品詞が割れた項目は1(`shriek`名詞/`shrieked`動詞=同一語彙素)。表示には「意味の違いまでは判別していません」を常設注記し、`forms`(数えた表層形)を確認できるようにする。
2. 判別**する**もの(構造が決める範囲): 語境界(部分文字列)、語形(活用表)、`a/an`<->`this/that`は可・`the`は不可、分離の間の語数と品詞(代名詞のみ確定)、前置詞/不変化詞の曖昧さ、名詞句スロット。
3. **判定できない = 加算しない**: 上記のslot_np/sep_np/revlemma/前置詞かもしれない分離は `uncertain` に件数だけ記録し、合計に入れない。UIは「＋判定保留N」を小さく併記(0なら非表示)。
4. 未取得区分: 回数に含めず `unavailable` に区分名を記録し、UIで「Comment・Preview未集計」と明示(0と偽らない)。

### 2-7. 区分別・合計
`total = story + comment + preview + oneline`(確定のみ。titleは含めない)。`counts` は4区分+title の確定件数。`forms` は確定ヒットの表層形別件数(表示の根拠・検証用)。

## 3. データ仕様(後方互換)

member data JSON(`user_test/selection_form_v3/data/<stem>.json`)への**追加のみ**:
```json
// phrases[i] / words[i] / overflow[i] の各entryに
"occurrence": {
  "v": "occ-v1",
  "counts": {"story": 2, "comment": 1, "preview": 1, "oneline": 1, "title": 0},
  "total": 5,
  "forms": {"clutter": 5},
  "uncertain": {"story": 1},          // 任意: 保留があるときだけ
  "unavailable": ["comment","preview"] // 任意: 区分の本文が取れなかったときだけ(countsにはキーを出さない=0と区別)
}
// 記事(トップ階層)に
"occurrence_meta": {"v": "occ-v1", "sections": {"story": {"sha256": "...", "paragraphs": 9, "source": "<run相対path>"}, "comment": {...}, ...}, "unavailable": []}
```
- 実測例(`untidiness_family_resource__b1b`): `clutter` -> `{"counts":{"story":2,"comment":1,"preview":1,"oneline":1,"title":0},"total":5,"forms":{"clutter":5}}`、`Now in Session` -> `{"counts":{...,"title":1},"total":0}`。
- 後方互換: キー無し(既存data)は何も表示しない。validateArticleは未知キーを許す。`buildText/buildReadable/buildStructured`・照合コード・Done署名の入力に含めない(難易度と同じ)=Claude受領形式・復元ツール(er128)は無変更。
- 生成: `convert(..., occurrence_sections=<dict|None>)` を追加。`None`なら従来とバイト同一。`export_form_data_01.py` のCLIは `family/level/source_kp_candidates_path` からrun dirを導出して区分本文を読む loader（試作 `tools/section_loaders_01.py`）を呼ぶ。読めない区分は `unavailable`、記事全体で全く読めない場合は `occurrence` を出さず `data_warnings[{code:"occurrence_unavailable"}]`(フォーム自体は従来どおり動く=fail-open。回数は選定条件ではない)。
- 集計関数は新規の共有moduleとして配置(提案名 `er_selection_occurrence_count_01.py`、純関数・API 0・環境変数/flagを読まない)。exporterは単一入口でこれだけ呼ぶ。
- サイズ: 1 entryあたり約150B、1 memberあたり+2KB前後(現状13〜17KB)。集計時間は1 memberで約30ms。
- 再現性と陳腐化: `occurrence_meta.sections.*.sha256` に数えた本文のsha256を記録。選定後にLocal Rewrite/intro patch等で本文が変わる場合（`surname_choice` で `adopted` の旧occurrence_count=4 に対し現本文=3 の実例あり）は、**回数は選定時点の本文**を表す。後工程で本文が変わった際は同じ集計で再計算して差分を検査できる(委任_02の任意検査 `verify_occurrence`、警告のみ)。
- 公開済みbatchへの後付けは**しない**(data JSONのバイトが変わるとDone署名・照合コードが変わる: CURRENT_STATE §4-2)。新規export+新batch idで公開。

## 4. 表示案

各候補の日本語訳(`.ja`)の下に1行(AI理由detailsの上)。選定条件・並び順・①②③は変更しない。
```
put away
  [日本語訳 ...]
  出現 6回｜本文4・Comment1・In One Line1          ← 内訳は0でない区分だけ
clutter
  出現 5回｜本文2・Comment1・Preview1・In One Line1
Now in Session
  出現 0回（タイトルに1回）
leave out
  出現 5回｜本文3・Comment1・Preview1  ＋判定保留1   ← 保留がある時だけ小さく
redelivery系(評価runでPreview/Commentが無い場合)
  出現 3回｜本文3  ※Comment・Preview未集計
```
- ラベルは原文の語(本文 / Comment / Preview / In One Line)。区切りは `・`、合計の太字は回数のみ。0区分は省略(原文「0を並べる必要はない」)。
- PC: `.lab` 内の1行(12px、`.diff` と同系統の控えめな色)。モバイル(<=520px): 同じ行が折り返す(ピック列42px固定のため文字量が増えても列は崩れない)。
- `title`属性(タップ/ホバー): 「同じ綴り・活用形・分離形(例 put it away)の出現を数えています。意味の違いまでは判別していません。数えた形: put away×3, put it away×1」。常設の説明は1行(`.hint`)でフォーム上部に1回。
- 回数0・未取得・保留だけの区分もあるため、`occurrenceOf(it)` は `{has, total, parts[], title, unc, unavail}` を返す純関数にする(UIはこれだけ読む。node単体testで固定)。
- 確定済みKP/KW(`lockHtml`)・文法欄には出さない(Phrase/Wordの候補選定が対象)。

## 5. UI変更範囲(最小)

| ファイル | 変更 |
|---|---|
| `user_test/selection_form_v3/form_logic.js` | `occurrenceOf(it)` 追加・export、`ASSET_VERSION` を+1(他委任と同時の場合は最新値にrebase) |
| `user_test/selection_form_v3/index.html` | `groupHtml()`(:151-170)の`.ja`直後に1行追加、CSS `.occ` を数行、フォーム上部の注記1行 |
| `docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/selection_form_logic_test_01.js` | `occurrenceOf` のtest追加(旧data=非表示、保留/未取得/titleのみ/0) |
| `docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py` | `convert()`に`occurrence_sections`引数、CLIにloader呼出、`data_warnings` |
| 新規 `er_selection_occurrence_count_01.py`(+test) | 集計(試作 `tools/occurrence_count_01.py` を昇格) |
| 触らない | `buildText/buildReadable/buildStructured`、`doneSig`/`makeCode`、localStorage state、`selectRemaining`、batch JSON/`publish_selection_batch_01.py`、`er128_form_readable_restore_01.py`、N5/KP候補抽出・Prompt・Gate・閾値 |

2階層化(SELECTION-UI-TWO-TIER-01 rev05-a)との切り分け: 個別ページ(`MODE==='set'`)が`render()`->`groupHtml`を共有するので、回数表示は`groupHtml`だけで両階層に効く。トップは候補単位描画が無く変更不要。共通データ仕様(§3)が先に固まっているため、データ側(exporter)とUI側は並列実装できる。

## 6. 受入条件1〜10の対応

| # | 条件 | 本設計での担保 | 検証方法(実装委任) |
|---|---|---|---|
| 1 | Phrase・Word両方に回数表示 | `phrases`/`words`/`overflow`の全entryに`occurrence`、`groupHtml`は両方 | node test + 公開URLの実画面 |
| 2 | X/Y/Z x Standard/Advanced | loaderがX/Y/Z、a2/b1bを同一入口で処理。27 member実測で6水準全てを確認(`PRECISION_01` §2) | 6水準のmemberを新batchに含め公開で確認 |
| 3 | 4区分の区分が正しい | loader表(CURRENT_STATE §2)+公開enduser pageとの突合: 20ページ195項目でStory/In One Line一致100%、Comment/Preview一致(evidence-onlyの35項目を除く160/160) | 突合ツール再実行 |
| 4 | 活用形・分離形が承認した規則どおり | 本書§2が規則。ユーザー承認後に固定(判断候補) | 単体test 30件 + 5表現実例 |
| 5 | 誤カウントを防ぐ検証がPASS | 部分文字列/ハイフン語/`in a way`/句読点/newline/`the`置換/派生語/news->new/puzzling->puzzle 等の否定test | `occurrence_count_01_test_01.py` 30件PASS |
| 6 | 既存機能維持 | §5「触らない」。Done/コメント/入力保持/一括コピー/受領形式に回数を入れない | 既存node/pytest回帰 + 公開URL実操作 |
| 7 | 公開URL PC/スマホ実操作 | 新batch公開+live smoke | Playwright(PC/mobile)+スクショ |
| 8 | batchデータ供給・再表示・再開 | 回数はdata JSON内の静的データ。localStorage stateに入れない | 再読込/別タブ/再開のE2E |
| 9 | 追加AI費用0円 | 決定論。API呼出なし(テストで`client`引数を持たない) | 実行ログにAPI呼出0、`costs`不変 |
| 10 | SSOT/Git | OPEN-632、CURRENT_SPEC、DECISION_LOG、ACTIVE_TASK | Closeoutで更新 |

## 7. 実装計画(委任_02以降。本委任では未実施)

1. (並列A) 集計moduleの昇格+test+exporter統合(`convert(occurrence_sections=)`、CLI)。
2. (並列B) `form_logic.js occurrenceOf`+`index.html`表示+node test(固定のdata fixtureで先行可能)。
3. 全27 memberを再export(API 0)->新batch id(テスト明記)でpublish->live smoke->PC/スマホ実操作(Playwright)->Fable独立受入。
4. ユーザー承認(集計規則)後にexporterの既定をONにし、以降の報告から全Family・全水準へ供給(= PRODUCTION_WIRED)。承認前は`--with-occurrence`の明示指定のみ・テストbatchのみ。
所要見込み(Sonnet): A 1.5h || B 1.5h -> 統合・公開・実操作 1.5h = 約3〜3.5h(直列5h比で約30%短縮)。API費用0円・量産単価への加算0円(CPU約30ms/記事)。

## 8. Opus条件Aレビュー論点(新しい構造・処理フローの設計)

1. **意味の水準**: 「同綴り・同形の出現」を数え多義は判別しないという線引きは、ユーザー原文§4-4/§4-8と過剰設計回避の両立として妥当か。表示の注記文言は十分か。
2. **保留枠(uncertain)**: 「加算しない+件数を別表示」は§4-8に対し十分か、過剰な情報か。保留を表示しない選択（データには残す）の方がよいか。
3. **確定集合の大きさ**: slot_pron/sep_pronを確定にするのは妥当か（実データではslot_pron 2件・sep 0件、ユーザー指定5表現の実例では分離形4件を確定）。確定を「完全一致+活用形のみ」に絞り、他を全て保留にする案との比較。
4. **品詞割れの同綴(bar等)**: 語彙素単位で数える現案 vs 「選定表層と同じ活用クラスのみ確定」案。実データの差は確定ヒット2%未満。
5. **N5(2026-10-30配線)との結合**: 既存の候補docに`n5_generalization`が無く、N5形でのtestは単体test(スロット)のみ。N5形が想定外の語を含む場合も「実表現の完全一致=下限」で破綻しないか。
6. **データ配置**: member data JSONへの焼き込み(推奨)と、サイドカー(`<stem>.occurrence.json`)の比較。焼き込みは1ファイルで原子的・公開sha封印・難易度と同型だが、後付けすると`__file_sha256`が変わりDone/照合コードが無効になる。サイドカーは後付け可能だがfetch・整合管理が増える。
7. **title 5番目ラベル**: 原文4区分に`タイトル`を条件付きで追加する表示が許容範囲か（代替: titleのみの項目は「0回」とだけ表示）。
8. **陳腐化**: 選定後の本文変更(LR/intro patch)でズレた場合の扱い（選定時点の本文を表す・差分検査は警告のみ）。
9. **er105の再利用結合**: Production module（`er105`）の内部表(`_PLURAL_EXCLUDE`等アンダースコア名)を読む結合の許容。公開関数に昇格してもらうか、コピー禁止の方針でよいか。
10. **既定ON/OFF**: 集計規則のユーザー承認前は`--with-occurrence`明示のみ・テストbatchのみとする段階導入（11-7の限定例外に準拠した隔離）で足りるか。

## 9. リスクと注意

- 表示の信頼は「何を同じと数えるか」の説明に依存する。注記は短く常設し、詳細(数えた形)はタップで確認できる形にする。
- 回数は参考情報であり、AIの候補順位・品質判定・選定条件には使わない（並び替え・フィルタに使わない）。
- 本設計は現在の候補doc(N5配線前)で検証している。N5配線後の新規runでの再実測を委任_02の最初に行う。
