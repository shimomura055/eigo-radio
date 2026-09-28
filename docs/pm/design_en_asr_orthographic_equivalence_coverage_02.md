# design_en_asr_orthographic_equivalence_coverage_02

管理ID: EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02
Phase: 1(原因分析+coverage再監査+設計案まで)。¥0・API呼び出しなし・
Production code変更なし・SSOT編集なし(本書はすべて記載案)。
日付: 2026-09-28
先行SSOT: `EN-ASR-SEMANTIC-EQUIVALENCE-REVIEW-01_REPORT.md`(22項目レビュー、
Tier 1/3 Phase A+B `APPROVED_FOR_PRODUCTION` 2026-09-27)、
`er021_en_asr_semantic_equivalence_production_01.py`(Production module)、
OPEN-184(CLOSED、本件へ吸収済み)/OPEN-186(WIRING IN PROGRESS)。

## 0. 要旨(先に結論)
canonical "Act One" vs ASR "Act 1" が救済されなかった原因は、**Tier 1の
数値等価判定ロジックそのものが間違っている**からではない。実際に
`tier1_numeric_equivalence("Act One was 20%.", "Act 1 was 20%.")` を
分離して実行すると正しく等価と判定される(検証済み、§1.2)。真因は、
Tier 1が**セグメント全体を1つの atom 列として長さ完全一致を要求する
all-or-nothing設計**になっており、同一セグメント内の**無関係な**別の
表記差(略語 "U.S." のperiod分裂、日付序数 "13th" の接尾辞)が1つでも
あると、セグメント全体の判定が握りつぶされて `None`(非等価)を返す
ためである。この2つの無関係な表記差は、いずれも**既存の旧Validator
(`er006_preprod_hardening_01_validation.py`)側には既に安全な対処が
存在する**(略語は`despaced()`ratio救済、日付序数は`_DATE_ORDINAL_RE`)
にもかかわらず、Tier 1(`er021`)は循環import回避のため独立実装した
自前のtokenizerを使っており、この2つの既存の安全策を継承していない。
したがって本件は「新しい意味等価ルールが必要」という話ではなく、
**Tier 1が自分自身の設計方針(既存Validatorのロジックと結果整合を保つ)
から実装時に逸脱した2つの具体的な穴**である(§5 分類A)。あわせて、
Tier 1の判定方式自体(all-or-nothing)が**構造的に脆い**ことも判明した
(§3)。これは個別のfixture追加では閉じない、設計原則レベルの課題。

## 1. E-1 原因分析

### 1.1 事実確認(コード追跡)
- `er021_en_asr_semantic_equivalence_production_01.py::tier1_numeric_
  equivalence()`(L398-418): `_tier1_atoms(canonical)`/`_tier1_atoms(asr)`
  の2つのatom列を得たあと、`len(ca) != len(aa)` なら即 `None`(L411)。
  その後 `zip(ca, aa)` で位置ごとに完全一致を要求する(L415-417)。
  **diffの位置を特定して部分一致を見る設計ではない**(全体が同じ長さで
  なければ即非等価)。
- `_TOKEN_RE`(L90-102)は数値・通貨・時刻・分数・パーセント・英字語を
  優先的に拾うが、どれにも一致しない1文字(記号)は最後の
  `r"|[^\s]"` で必ず1文字ずつliteral atomにする(コメントに明記された
  意図的安全設計、上付き文字などの黙殺を防ぐため)。この設計の**副作用**
  として、`"."` を含む語(`U.S.`のような打点略語)が `U`+`.`+`S`+`.` の
  4 atomへ分裂する。対して `US`(打点なし)は `[A-Za-z']+` に一致して
  1 atomになる。同じ実体の2つの綴りが**atom数が異なる**ため、
  この語だけでセグメント全体のTier 1判定が握りつぶされる。
- `_preprocess_raw()`(L105-117)はハイフンの吸収(`(?<=[A-Za-z])-
  (?=[A-Za-z])`)とマイナス記号のみを扱い、「数字の直後に付く序数接尾辞
  (`13th`)」を吸収する処理を持たない。`_TOKEN_RE`にも
  `\d+(?:st|nd|rd|th)` 相当の atom 種別が無い。そのため `13` (canonical)
  vs `13th` (ASR) は `[num(13)]` vs `[num(13), literal("th")]` となり、
  やはりatom数が1つずれる。
- 対して**旧Validator側には既にこの2つの安全策が存在する**:
  - 略語: `normalize_text()`(er006 L408-437)は `re.sub(r"[^a-z0-9]+",
    " ", t)` で句読点を空白化するため `U.S.` は `["u","s"]` の2token、
    `US` は `["us"]` の1tokenとなり、依然token数は不一致だが、
    `despaced()`(全空白除去して比較)が `"us"`同士の一致として救済する
    設計になっている(`classify_asr_match`のNORMALIZED_MATCH経路、
    実行確認済み、§1.3)。
  - 日付序数: `_DATE_ORDINAL_RE = r"\b(月名)\s+(\d{1,2})(st|nd|rd|th)\b"`
    (er006 L170)が `normalize_numeric()` 内(L384)で「月名+数字+序数
    接尾辞」を「月名+数字」へ**意図的に狭いスコープで**(月名直後限定)
    正規化する既存の承認済みロジック(`ER-010-DATE-SPOKEN-FORM-POINT-
    FIX-01`由来)。
  - Tier 1(`er021`)はこの2つを**継承していない**(循環import回避の
    ためer006をimportしない設計、L14-24のコメント参照)。しかし
    「継承しない」は「同じロジックを独立に再実装する」ことを意味する
    はずが、実際には再実装されておらず**単純に抜けている**。

### 1.2 実際に再現・検証した具体例(実データ、コード実行で確認済み)
実際の記事セグメント(`family_x_b3_diversity_trial_01/hormuz`、
`full_story_part1`、Local Rewrite前canonical/実ASR、Flash-Lite Phase 3
`hormuz__run_04_parallel_a/b1b/audit/tts_generation_results.json`の
`local_rewrite_recovery.ng_span`および`er019_output/family_x_audio_
production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_03_
baseline/b1b/narration/attempts/full_story_part1_attempt{1,2}_*.json`)
から抽出した実文を、`er021_en_asr_semantic_equivalence_production_01`を
直接呼び出して検証した(read-only、Production呼び出しは発生させて
いない)。

canonical(Local Rewrite前、実データ):
`"...in 3 acts. Act One was 20%. Act 2 brought an unexpected turn.
Act 3 was...The curtain rose on July 13. ...the cost of US efforts..."`

ASR(実測):
`"...in three acts. Act 1 was 20%. Act 2 brought an unexpected turn.
Act 3 was...The curtain rose on July 13th. ...the cost of U.S.
efforts..."`

検証結果:
1. `tier1_numeric_equivalence(canonical, asr)` → **`None`(非等価判定、
   実際のProduction挙動と一致)**。
2. `_tier1_atoms(canonical)` は148 atom、`_tier1_atoms(asr)` は152 atom
   (`len`不一致で即`return None`、L411)。
3. 両atom列をキー化してdiffすると、非等価な区間は**ちょうど2箇所のみ**:
   - `insert`: ASR側にだけ literal atom `"th"` が1個増える(`13`→
     `13th`)。
   - `replace`: canonical `[lit("us")]` (1 atom) vs ASR `[lit("u"),
     lit("."), lit("s"), lit(".")]` (4 atom)。
   - **"Act One"(atom: number value=1) vs "Act 1"(atom: number
     value=1) の位置は diff に現れない(=既に正しく一致と判定されて
     いる)**。すなわちTier 1の数値語パーサ自体は正常に機能している。
4. `tier1_numeric_equivalence("Act One", "Act 1")` を単独で呼ぶと
   `MATCH` を返す(切り出して単独評価すれば正しく動く)。

### 1.3 telemetryオフライン再分類(母数付き、read-only)
`er021_output/en_asr_semantic_equivalence_production_wiring_01/
telemetry.jsonl`(Phase A/B `PRODUCTION_WIRED`後の実運用ログ、role適用
対象segmentでTier 1 early-exitに入らずbaselineへフォールバックした
記録のみ、2026-09-27以降蓄積)を全件(4,187行)読み込み集計した。

| classification | 件数 |
|---|---|
| TRUE_CONTENT_MISMATCH | 3,487 |
| ASR_VALIDATION_UNCERTAIN | 645 |
| SECONDARY_ASR_CORROBORATED_MATCH | 55 |

| sub_reason | 件数 |
|---|---|
| protected_number | 1,672 |
| content_word | 1,661 |
| plural_only | 367 |
| entity_only | 276 |
| protected_negation | 154 |
| homophone_only | 51 |
| low_ratio | 6 |

`protected_number`(TRUE_CONTENT_MISMATCH、1,672件、多くはunit
test由来の合成fixtureや同一記事の複数attempt/複数run再掲を含む)を
`(canonical, asr)` の完全一致で重複排除すると**distinct 43件**。
この43件それぞれについて、Tier 1のatom列diffを再計算し分類した:

| カテゴリ | 該当distinct件数(43件中) |
|---|---|
| diffの一部が「打点略語のatom分裂」(US/U.S.型) | 9件 |
| diffの一部が「裸digit+序数接尾辞」(13/13th型) | 9件 |
| 上記いずれも含まない(=純粋に値が異なる、正しく保護されている) | 27件(概算、重複除く) |

上記9+9件はほぼ重複しており(同一パターンの併発)、記事文面の重複
(同一記事の複数attempt・複数run・複数フェーズでの再掲)を除去すると
**独立した記事本文は3件**: (1) 本レビュー対象のHormuz「Act One」記事
(`EN-ASR-SEMANTIC-EQUIVALENCE-TRIAL-01`〜`TTS-GEMINI-3.8-FLASH-LITE-
PRODUCTION-WIRING-FAMILY-X-01`のTrial/Phase 2/Phase 3の複数run、raw
telemetry 15行分)、(2) 合成negative fixture1件("The study included 28
articles." vs "28th articles." — これは**値ではなく品詞[基数/序数]が
違う正当な保護対象**であり、本件のような「同じ値の表記違い」ではない。
序数接尾辞を無条件に無視するルールを採用すると、この種の正当な
protected caseがfalse acceptになるため、§4で「日付文脈限定」が必須で
ある根拠として重要)。

残り27件(distinct)は目視・値比較で**すべて実際に異なる数値**(例:
"2 groups"対"3 groups"、"2025"対"2024"、"51 to 49"対別の値等)であり、
Tier 1が現状これらをrescueしていないのは正しい安全側の挙動である。
**Tier 1の値比較ロジック自体にfalse acceptは1件も見つからなかった**
(既存の安全性は毀損されていない)。

結論: 「Act One」型の失敗は**telemetry上でも実際に繰り返し発生している
実データ**であり(1記事が複数run・複数フェーズ・複数attemptで計15回
NG化を記録)、架空probeではない。ただし、この失敗を引き起こす直接
原因(打点略語・裸digit序数接尾辞のatom数不一致)は**この1記事以外の
distinct fixtureでは現時点で確認できていない**(telemetryの母数が
まだ小さいため、頻度自体は今後も観測を継続する必要がある)。

### 1.4 なぜTrial-01のcorpusで検出できなかったか
`er021_output/en_asr_semantic_equivalence_trial_01/corpus.jsonl`
(POSITIVE 34/NEGATIVE 34、計68件)を実測すると、canonical文の平均
語数は**6.03語**(最小1語・最大17語)であり、実際の記事本文segment
(`full_story_part1`のような長尺segment、実測148 atom = 100語超相当)
とは1桁以上テキスト長が異なる。さらにcorpus.jsonl全68件を`grep`した
限り、`U.S.`/`US`/`NASA`等の打点略語を含むfixture、および裸digitの
月日+序数接尾辞(`13th`等)を含むfixtureは**0件**だった。

REVIEW-01のFable批判レビュー(A-2項目10)は「acronym: ピリオド除去・
小文字化により U.S./US/NASA は既に吸収済み」と明記しているが、これは
**旧Validator(`normalize_text`/`despaced`)についての正しい事実確認
であり、その後新設されたTier 1(`er021`)の独自atomパーサーについて
再検証されないまま「解決済みの前提」として引き継がれた**。同様に、
日付序数(`13th`)についてはREVIEW-01のA-2項目3・A-3のTier 1閉じた
集合のどちらにも明示的な言及が無く(既存Validatorに`_DATE_ORDINAL_RE`
という対処が既にあることが、レビュー時点で見落とされていた)、Tier 1
の実装対象として意識されなかった。

corpusが「1phenomenon = 1短文」という設計だったため、**2つ以上の
独立した表記差が同一の長尺segmentに同時発生した場合にのみ顕在化する
whole-segment all-or-nothingの脆弱性そのもの**は、そもそも構造的に
テストされ得なかった(§3で後述する設計原則の欠落)。

### 1.5 帰着(仕様漏れ/実装漏れ/corpus不足/coverage設計不足)
複数の原因が複合している:
1. **実装漏れ(Category A、2026-09-28是正: 原因記述を修正)**: 当初
   「(旧Validatorの安全策を)継承し損ねている」と記述したが、これは
   不正確だった。正確には、Tier 1のtokenizer(`_TOKEN_RE`)は上付き
   文字等の情報欠落を防ぐため**意図的にpunctuationを保持したまま
   1文字ずつliteral atom化する設計**(L97-102のER021-SAFETYコメント
   参照)であり、これ自体は正しい安全設計である。一方、旧Validator
   (`normalize_text()`)は逆にpunctuationを**除去**する正規化(かつ
   `despaced()`で空白も除去して救済する)という、Tier 1とは正反対の
   戦略を取っている。問題は「継承し損ねた」ことではなく、**この2つの
   異なる戦略(punctuation保持 vs punctuation除去)の間で、
   punctuation由来の差分をどちらの層が最終的に吸収するかという
   調整が行われていなかった**ことである。Tier 1はpunctuationを
   保持する設計上、略語のatom分裂・日付序数のatom数不一致をそのまま
   全体判定の道連れにしてしまい、旧Validator側の除去戦略の恩恵を
   受けられていなかった(§3のdiff-anchored化は、この未調整を
   Tier 1内部で解消する対策である)。
2. **coverage設計そのものの不足(構造的)**: Tier 1がwhole-segment
   all-or-nothingという設計を採用したこと自体が、「1箇所の対象外
   phenomenonが同一segment内の他の対象内phenomenonの判定まで道連れに
   する」という一般的な脆弱性を生んでいる。これは特定のcategoryの
   抜けではなく、**アーキテクチャ上の脆弱性**であり、今後も新しい
   micro-gapが見つかるたびに同じ失敗パターン(全体巻き込まれ)を
   繰り返す可能性が高い(§3で設計案を提示)。
3. **Trial corpus/fixtureの不足**: 短文・単一事象のfixtureのみで
   検証されており、実運用の長尺segment・複数事象同時発生を代表する
   fixtureが無かったため、上記1・2のどちらも検出されなかった。
4. **どのPhaseに属すべきだったか**: 略語・日付序数はいずれも
   REVIEW-01 A-3の「Tier 1対象(閉じた集合)」の趣旨(閉じた表記差の
   吸収)に明確に含まれる範囲であり、**Phase A(数値/通貨/%/年/時刻/
   分数/ローマ数字/略語の値等価)のスコープ内の実装漏れ**である。
   新しいPhase(C等)や新しい意味論的拡張は不要。

## 2. E-2 coverage matrix(カテゴリ×文脈)
現行判定は実際に`tier1_numeric_equivalence()`を実行して確定させた
(2026-09-28、read-only)。「現行(Tier1単独)」は対象文だけを渡した
場合の結果(他の無関係差分と同居しない、理想的なケース)。実運用の
long segmentでは§1のとおり無関係な差分と同居すると道連れで失敗し
得る点に注意。

| # | カテゴリ | canonical例 | ASR例 | 現行判定(Tier1単独) | 期待判定 | 根拠 |
|---|---|---|---|---|---|---|
| 1 | cardinal | "two groups" | "2 groups" | MATCH | PASS | 既存Tier1 |
| 2 | ordinal(語→桁+接尾辞) | "the third attempt" | "the 3rd attempt" | 未実測(_ORDINAL_WORDS相当は旧Validator側、Tier1側に同等の変換なし) | PASS | 要追加検証(§6 test design) |
| 3 | 番号ラベル(Act/Part/Chapter/Section/Phase/Version) | "Act One" / "Chapter One" / "Part Two" / "Section IV" | "Act 1" / "Chapter 1" / "Part 2" / "Section 4" | **MATCH**(実測、単独評価時) | PASS | §1.2実測 |
| 4 | year(ペア読み) | "nineteen ninety-nine" | "1999" | 実装あり(`_parse_bare_number_run`のペア読み分岐) | PASS | REVIEW-01 A-3 |
| 5 | date(月+日) | "July 13" | "July 13th" | **NO MATCH**(atom数不一致、序数接尾辞absent) | PASS(月名直後限定) | §1.2実測、旧Validator`_DATE_ORDINAL_RE`は既に対処済みだがTier1未継承 |
| 6 | time | "3:30 pm" | "three thirty pm" | MATCH | PASS | 実測(本書§作成時) |
| 6b | time(略記meridiem) | "10:16 am" | "10:16 a.m." | **NO MATCH**(想定、"a.m."は複数literal atomに分裂しmeridiem判定`words[i+1] in ("am","pm")`に一致しない) | PASS | コード追跡(未実測、§6でtest追加) |
| 7 | decimal | "two point three" | "2.3" | MATCH | PASS | 既存Tier1 |
| 8 | thousand/million/billion | "one point two billion dollars" | "$1.2 billion" | MATCH | PASS | 実測 |
| 9 | currency | "$2.3 million" | "two point three million dollars" | MATCH | PASS | 実測 |
| 10 | percent | "20 percent" | "20%" | MATCH | PASS | 既存Tier1 |
| 11 | fraction | "one half" | "1/2" | MATCH(閉じた語句集合のみ) | PASS | 既存Tier1(`_FRACTION_PHRASES`) |
| 12 | Roman numeral | "World War II" | "World War 2" | MATCH(大文字のみ) | PASS | 実測(§本書実行) |
| 12b | Roman numeral(小文字ASR誤記) | "Section II" | "Section ii" | **未実測/おそらくNO MATCH**(`_ROMAN_SAFE`キーは大文字限定) | UNKNOWN許容(現状維持) | コード追跡(現実のASR出力で小文字ローマ数字は稀、優先度低) |
| 13 | 番号付き固有表現(hyphenated) | "a 15-minute walk" | "a 15 minute walk" | **NO MATCH**(`-`が独立literal atomとして残り atom数不一致) | PASS | 実測(本書) |
| 14 | alphanumeric entity | "the COVID-19 outbreak" | "the COVID 19 outbreak" | **NO MATCH**(同上理由) | PASS | 実測(本書) |
| 15 | capitalization | "NASA" | "Nasa" | MATCH(literal atomは小文字化して保存) | PASS | コード追跡(L370 `lw = w.lower()`) |
| 16 | whitespace/tokenization(複合語分かち書き) | "blitzscaling" | "blitz scaling" | 未実測(Tier1は複合語分かち書きの吸収を持たない、旧Validatorの`despaced()`側の機能) | PASS | 旧Validator側でrescue、Tier1では対象外のままでよい(役割分担、§3) |
| 17 | apostrophe/possessive | "Ottawa's mayor" | "Ottawa is mayor"(誤り例) | N/A(意味の異なる例、負例として不適切、要再設計) | — | REVIEW-01 A-2項目11「未検証」のまま(本Phaseでも未解消、§7) |
| 18 | punctuation/quotes/dash | "“20%”" | "20%" | MATCH(引用符はliteral atomとして両側に無ければ道連れになり得るが、無音声化されるため通常は両側とも欠落し一致) | PASS | 実測(本レビューで使ったLocal Rewrite後canonicalの実データ、引用符付きでも該当segmentは他要因のみで不一致) |
| 19 | abbreviation/acronym(打点あり⇔なし) | "US efforts" | "U.S. efforts" | **旧Validator側はdespaced救済でPASS。Tier1単独ではNO MATCH**(atom数不一致、4 atom vs 1 atom) | PASS | §1.2実測(本件の直接原因) |
| 20 | ASRが数字化しても意味差でない(番号ラベル一般) | "Step One" | "Step 1" | MATCH | PASS | #3と同型 |
| 21 | negative: 概数vs正確値 | "about 20 people" | "20 people" | NO MATCH(正しく保護) | REJECT(現状維持) | 実測(本書) |
| 22 | negative: 値そのものが違う | "1 million copies" | "1 billion copies" | NO MATCH(正しく保護) | REJECT(現状維持) | 実測(本書) |
| 23 | negative: 基数vs序数(品詞違い) | "28 articles" | "28th articles" | NO MATCH(正しく保護) | REJECT(現状維持) | telemetry実例(§1.3)、序数接尾辞を無条件absorbすると壊れる根拠 |

### 2.1 coverage matrix拡張(2026-09-28、Phase 2実装レビュー[Opus指摘]で追加)
「単一カテゴリ単独」ではなく「**同一segment内で複数差分が共存するケース**」
自体を独立した検証観点として追加する(Hormuz実例が示した本質的な脆弱性は
まさにこれであり、§2の各行は単独カテゴリの実測に留まっていたため)。

| # | カテゴリ | canonical例 | ASR例 | 実装後の判定 | 根拠 |
|---|---|---|---|---|---|
| 24 | 番号ラベル+略語+日付序数の3種同時共存(Hormuz実例そのもの) | "Act One...US efforts...July 13" | "Act 1...U.S. efforts...July 13th" | PASS(diff-anchored、absorbed_ops=1、日付序数は前処理で無差分化) | 実装後実測(本Phase、runtime evidence) |
| 25 | 序数語("third")+per cent+meridiem略記が同一segmentに共存 | "the third attempt...20 per cent...10:16 am" | "the 3rd attempt...20%...10:16 a.m." | PASS(各差分が個別にTier1既存判定/strict合成規則へ帰着) | 実装後実測(本Phase) |
| 26 | punctuation差+文の丸ごと欠落が同一segmentに共存(合成negative) | 長尺segment(略語差含む) | 同上+末尾1文が欠落 | REJECT(欠落文の英数字内容がalnum不一致のため即座に全体非等価) | 実装後実測(本Phase、long-segment negative test) |
| 27 | punctuation差+数値1桁違いが同一segmentに共存(合成negative) | 長尺segment(略語差含む) | 同上+数値が1桁違う | REJECT(値の異なるnumber atomはkindは同じでもkeyが異なりequalにならず、opは非literal混入でabsorb対象外) | 実装後実測(本Phase、long-segment negative test) |

## 3. E-3 設計原則・設計案比較

### 3.1 設計原則(Fable最終レビュー2026-09-26を継承、本書で明確化する点を追加)
- 両側を安全な共通意味表現へparseし、値が完全一致する場合のみ等価
  (既存方針、変更なし)。
- **(本書で追加提案)判定は「セグメント全体のall-or-nothing」ではなく、
  「diffを局所化し、非一致箇所それぞれが個別に許容パターンへ帰着する
  場合のみ全体PASS」という設計に変えるべきである**。理由は§1.5-2の
  構造的脆弱性(1箇所の対象外差分が他の対象内差分の判定を道連れにする)
  を解消するため。これは新しい意味論(false acceptの境界)を追加する
  ものではなく、**同じ既存atom比較を「位置固定zip」から「diff-anchored
  比較」へ変えるだけ**であり、個々のatomの等価判定基準そのものは一切
  変更しない(§5で分類Aとする根拠)。

### 3.2 設計案比較

| 観点 | 案1: 現状維持+個別pre-processing追加のみ | 案2: diff-anchored比較への変更(pre-processing追加込み) | 案3: 意味parse層を新設(全面刷新) |
|---|---|---|---|
| 説明 | `_tier1_atoms`の前処理へ「打点略語をatomへ結合」「月名直後の裸digit+序数接尾辞を吸収」の2パッチのみ追加、all-or-nothingのzip比較はそのまま | 上記2パッチに加え、`len(ca)!=len(aa)`即NGを廃し、`difflib.SequenceMatcher`でatom列をalignし、非equalな各opが「許容済みパターン(既存atom種別+新設2種)」に帰着する場合のみ全体PASSとする | Tier1を破棄し、canonical/ASR両方を文単位で構造化パース(数値・日付・固有表現等をラベル付きノードに)する新層を作る |
| false reject耐性 | 中(今回のAct One実例[打点略語+日付序数の2要因]は2パッチで解消できるが、**3つ目以降**の未知の別要因が同一segmentに出た場合はまだ道連れになる) | 高(無関係要因が何個同居しても、各要因が個別に許容パターンなら全体PASS。今回の実例はもちろん、将来の未知のpunctuation差にも構造的に耐性がある) | 高(理論上は最も柔軟) |
| false acceptリスク | 低(既存の閉じた判定基準のまま) | 低〜中(SequenceMatcherのalignmentが複数の連続した差分を1つのopとして誤って大きく括る可能性があるため、**opごとに厳密な許容パターン一致**を要求する実装規律が必須。既存のTier3 `locate_single_token_diff`と同様、op自体が「1箇所の閉じた許容パターン」に完全一致しない場合は非等価のまま[best-effort禁止]とする設計にすれば旧来同様に低リスク) | 不明(新規実装のため要ゼロベース検証、実装・レビューコスト大) |
| 変更範囲 | `er021`内のみ、小さい | `er021`内のみ、中程度(比較アルゴリズムの置き換え) | 新モジュール、全呼び出し経路への再配線が必要、大きい |
| 全経路一貫性 | 保たれる(既存wrapper無変更) | 保たれる(既存wrapper無変更、`tier1_numeric_equivalence()`の内部実装のみ変更、シグネチャ不変) | 要再設計、既存の5role wrapper・telemetry・Tier3との統合をやり直す必要 |
| コスト | ¥0、決定論コード | ¥0、決定論コード | ¥0のはずだが実装・レビュー工数が最大 |
| 今回のAct One実例を解消するか | **する**(2026-09-28実装レビューで是正: 打点略語を1atomへ結合するpre-processingと月名限定の序数吸収pre-processingの**2パッチだけでも**、両方を適用すれば残る差は無くなり`len(ca)==len(aa)`のall-or-nothing判定のままでも今回の実例そのものは解消できることを実装時に確認した。先の記述「しない」は誤りだったため訂正する) | **する**(2パッチと同じ範囲を解消しつつ、**未知の3つ目以降の想定外punctuation差**が将来同一segmentに同居した場合にも道連れにしない、という構造的な耐性が2パッチのみとの真の差分である) | する(が過剰) |

**推奨: 案2(diff-anchored比較+2つの具体的pre-processing修正)**。
理由: (a) 今回の実例を確実に解消する、(b) 変更範囲が最小(`er021`
内部のみ、呼び出し側シグネチャ不変、既存の5role wiring・telemetry・
Tier3救済ロジックに一切触れない)、(c) 「1箇所の未知の微小差分が他の
既知の正しい等価判定を握りつぶす」という**同種の再発**を構造的に防ぐ
(ユーザー要求「同種の誤判定を量産時に繰り返さない」に直接対応する)、
(d) 新しい等価判定基準(false acceptの境界)を一切追加しないため、
既存のNEGATIVE corpus・回帰(2,112件+corpus 68件)に対して安全側で
あることが機械的に保証しやすい(各opの許容判定は既存atom比較そのもの
を使い回すだけであり、新しい許容ルールを1つも作らない)。

### 3.3 案2に含める具体的パッチ(実装時の詳細、本Phaseでは未実装)
1. **打点略語の前処理**: `_preprocess_raw()`または新規ステップで、
   `\b[A-Za-z](?:\.[A-Za-z])+\.?\b` にマッチする範囲(例: `U.S.`、
   `U.K.`、`e.g.`)を検出し、ピリオドを除去して1つのliteral atomへ
   結合する(`U.S.` → 1 atom `"us"`)。これは**旧Validatorの
   `normalize_text()`が既にやっている正規化の考え方の再利用**であり、
   新しい許容ルールではない(Category A)。
2. **日付文脈限定の裸digit序数接尾辞吸収**: 旧Validatorの
   `_DATE_ORDINAL_RE`(月名直後限定)と**同一の正規表現・同一のスコープ
   条件**をTier1側にもそのまま複製する(ロジックの新規発明ではなく
   既存承認済みロジックの移植、Category A)。月名に隣接しない裸digitの
   序数接尾辞(例: "28th"単独)は**これまでどおり吸収しない**(§2の
   negative #23の保護を壊さないため)。
3. **diff-anchored比較**: `tier1_numeric_equivalence()`内部を
   `SequenceMatcher(None, ca_keys, aa_keys).get_opcodes()`で回し、
   `equal`以外の各opについて「削除/挿入側が空、または両側1atomの
   `_atoms_equal`」という**既存の判定基準をそのまま**適用する。opが
   この基準に該当しない場合は全体を非等価とする(best-effort禁止、
   既存原則を維持)。

## 4. E-4 全経路確認(呼び出しチェーン)
`classify_asr_match()`(er006 L1158)が英語ASR照合の唯一のwrapperで
あり、Tier 1 early-exit(role gate付き)はこの関数の冒頭1箇所にのみ
実装されている(L1207-1221)。実コード追跡の結果、以下の全呼び出し元が
**同じ1つの関数**を経由することを確認した(重複実装は無い):

| 経路 | 呼び出し箇所 | segment_id/role渡し | Tier1適用 |
|---|---|---|---|
| 初回attempt(B1 Full Story等) | `er003_v1_n3_01_tts_generate.py:144` | `segment_id=name` | ○(role該当時) |
| A2標準+fallback | `er003_v1_crosslevel_audio_02_common.py`→内部で上記er003_v1_n3_01の共通生成コアを呼ぶ(直接呼び出しなし、同一関数を再利用) | 同上 | ○ |
| retry(同一関数内ループ) | 同上(初回と同一コード経路) | 同上 | ○ |
| Local Rewrite回復(er020) | 再TTS後の再検証は同一生成コアの再呼び出し(`er003_v1_n3_01_tts_generate.py:144`と同一箇所)を通る、独立実装なし | 同上 | ○ |
| Secondary ASR cascade | `er006_secondary_asr_01.py`(直接呼び出し5箇所、L682/706/747/777/808、+間接2箇所[L395: `evaluate_attempt_with_cascade`→内部で`evaluate_attempt_with_cascade_detail`を同じsegment_idで再呼び出し、L526: `evaluate_attempt_with_cascade_detail`→`val.evaluate_attempt`経由でclassify_asr_matchへ到達]、2026-09-28追加確認) | `segment_id=segment_id` | ○(role該当時) |
| Human Review Lock直前 | cascade結果(上記)をそのまま使用、独立再判定なし | — | ○(cascade経由) |
| Key Phrase英語経路 | `classify_asr_match()`は呼ばれるが`segment_id`/`role`いずれも渡していない箇所が大多数(約50ファイル中の非該当segment) | 渡さない | ×(role非該当、既存仕様どおり対象外) |

**結論**: 経路の配線自体に矛盾・欠落は無い(初回・retry・fallback・
Local Rewrite前後・Secondary ASR・Human Review Lock直前のいずれも
単一wrapper・単一role gate関数を経由しており、「表記差だけでretry→
cooldown→Local Rewrite→Human Reviewへ落ちる構造」は**wiringの不整合
ではなく、Tier1自体の判定精度[§1-3]に起因する**)。したがって
Tier1本体の判定ロジックを修正すれば、追加の配線作業なしに全経路へ
同時に効果が及ぶ。

## 5. 分類(Existing Spec Check、A/B)

### (A) 既承認範囲内の明白な実装漏れ修正(Production採用は別途、本Phaseでは未実装)
1. 打点略語のatom結合前処理(§3.3-1)。旧Validatorの既存動作を
   Tier1側へ再現するのみ、新しい許容ルールではない。
2. 日付文脈限定(月名直後)の裸digit序数接尾辞吸収(§3.3-2)。旧
   Validatorの`_DATE_ORDINAL_RE`と同一スコープの移植のみ。
3. Tier1内部比較をdiff-anchoredへ変更(§3.3-3)。個々のatom等価判定
   基準は無変更、all-or-nothingのzip比較というアルゴリズムのみ変更。
4. hyphenated numeric(`15-minute`)・alphanumeric entity(`COVID-19`)の
   ハイフン吸収(§2 #13/#14)。既存`_preprocess_raw()`の
   「文字-文字」ハイフン吸収ルールを「数字-文字」「文字-数字」の
   組へ拡張するのみ(閉じた表記差の吸収、新しい数値の意味等価では
   ない)。
5. meridiem略記("a.m."/"p.m.")のatom結合(§2 #6b)。#1と同型の打点
   吸収パターン。
6. Trial corpusへの長尺・複数事象同時発生fixtureの追加(§1.4の再発
   防止、corpus拡充自体はコード変更を伴わない)。
7. 「's」由来の単独"s"の無視処理(REVIEW-01 A-2項目11、未検証のまま
   残っている件、§7で改めてOpusへ申し送り)。

上記(A)はいずれも**新しい意味等価カテゴリを追加するものではなく、
既存Phase A(数値/通貨/%/年/時刻/分数/ローマ数字/略語の値等価、
`APPROVED_FOR_PRODUCTION`2026-09-27)のスコープ内の実装是正**であり、
本設計書はこれを実装候補として提案するに留める(Production変更は
別途ユーザー承認・Trial・Fable Gateを経る)。

### (B) 新しい意味等価ルール・false accept境界拡張(USER_DECISION_REQUIRED、本書では採用しない)
1. **日付文脈以外での裸digit序数接尾辞の一般的吸収**(例:
   `"the 28th"` ⇔ `"the 28"` を月名の隣接なしに常に等価とする)。
   §2 negative #23("28 articles" vs "28th articles")が示すとおり、
   基数と序数は品詞として意味が異なり得るため、**日付文脈限定という
   閉じたスコープを外すことは新しい false accept 境界の拡張**にあたる。
   採用しない。追加コスト見積り: 実装自体は¥0だが、false accept
   リスク低減のための追加negative corpus設計・Fableレビューが必要。
2. **複合語分かち書き吸収をTier1へ複製する**(現在は旧Validator側の
   `despaced()`が担っている役割分担、§2 #16)。Tier1へ機能を移すこと
   自体に技術的合理性は乏しく(役割分担のまま据え置きが望ましい)、
   あえて行うなら「新しい層を追加する」ことになるため(B)寄りだが、
   現時点で不要と判断する(推奨: 変更しない)。
3. **ローマ数字の小文字許容**(§2 #12b)。実運用頻度が未確認(ASRが
   ローマ数字を小文字で書き起こす例が実際に観測されていない)。
   採用の是非はユーザー判断、優先度は低いと考える。

(B)は本Phaseでは一切実装しない。Trial実施要否を含め、ユーザー判断が
必要な場合は別管理IDで改めて起票する。

## 6. Positive/Negative test設計(実装フェーズ向け、本Phaseでは未実施)
Positiveに追加すべき最小セット(§2の実測結果に基づく):
- 番号ラベル+略語+日付序数が**同一の長尺文**に同居するfixture(今回の
  Hormuz実例を最小化した再現ケース、単一文ではなく100語超の
  多段落セグメントで検証すること。既存corpus.jsonlの平均6語という
  短さを是正する)。
- 打点略語(`U.S.`/`U.K.`/`e.g.`)単独のfixture(現状0件)。
- 月名直後の裸digit序数接尾辞(`July 13`/`July 13th`)単独のfixture。
- meridiem略記(`10:16 am`/`10:16 a.m.`)。
- hyphenated numeric(`15-minute`/`15 minute`)、alphanumeric entity
  (`COVID-19`/`COVID 19`)。

Negativeに追加すべき最小セット(false accept再確認、§2実測はすべて
正しく保護されていたが、diff-anchored化後に**回帰していないことを
再確認する**必要がある):
- 基数vs序数(`"28 articles"` vs `"28th articles"`、月名に隣接しない
  文脈)。
- 略語の見た目が似ているが**別の実体**(例: `U.S.`と`U.K.`)。
- 概数vs正確値、値そのものの相違(§2 #21/#22)。
- 略語のatom結合パッチが**無関係な別の略語違い**を隠さないこと(例:
  `U.S.`側の結合ロジックが`N.A.S.A.`のような別の打点略語と混同しない
  かの確認)。

## 7. Opus L2申し送り
1. **単発か構造的か**: 実データ上は現時点で1記事(Hormuz Act One)に
   由来する再発(15 raw telemetry行、複数run/複数phase)のみが確認
   されているが、原因自体(whole-segment all-or-nothingという設計)
   は**構造的**であり、略語・日付序数以外の未知のtokenization差
   (例えば将来別のUnicode文字・別の略語パターン)が今後も同種の
   道連れ失敗を起こし得る。案2(diff-anchored化)はこの構造的リスクを
   解消する提案である。
2. **他の同系統の抜け**: §2 negative #17(apostrophe/possessive、
   REVIEW-01 A-2項目11)は本Phaseでも実質未検証のまま残っている
   (良い負例を設計できず保留)。§2 #12b(ローマ数字小文字)も未検証。
3. **包括対策と呼べるか**: 案2(diff-anchored+2パッチ)は「今回見つかった
   2つの具体的穴」を塞ぐと同時に、「未知の3つ目の穴が見つかっても
   全体を道連れにしない」という構造的解決を提供する点で、単なる
   fixture追加より一段階上の包括対策と考えられる。ただし「意味parse
   層への全面刷新」(案3)ほどの汎用性は無く、Tier1の対象カテゴリ自体
   (§2の閉じた集合)を拡張するものではない。
4. **量産false reject耐性**: telemetry実測(§1.3)により、
   `protected_number`の大多数(43件中27件)は正しく保護されている
   ことを確認済み。diff-anchored化によりfalse rejectが減る対象は
   今回確認した2パターン(略語・日付序数)に限定される想定。
5. **false accept**: 案2はop単位で既存の閉じた許容パターンを流用する
   設計であり、新しい許容ルールを追加しない限りfalse acceptの境界は
   拡張されない(§3.2)。ただし実装時にop分割の粒度(SequenceMatcherの
   opcode境界の取り方)を誤ると、意図しない範囲を1つのopとして許容
   してしまうリスクがあるため、実装レビュー時に重点確認が必要。
6. **retry・fallback・Local Rewrite整合**: §4のとおり全経路が単一
   wrapperを経由しており、Tier1修正は追加配線なしに全経路へ反映される
   (整合性は担保されている)。
7. **Phase A+Bとの重複・矛盾**: 本書の(A)候補はいずれもPhase Aの
   スコープ内の実装是正であり、Phase B(規則的複数形・固有名詞
   corroboration)とは無関係(重複・矛盾なし)。
8. **Dangling Reference**: OPEN-184は本件(EN-ASR-SEMANTIC-EQUIVALENCE-
   REVIEW-01)へ吸収済み(`CLOSED`)、OPEN-186は`WIRING IN PROGRESS
   (telemetry待ち)`のまま。本Phase(COVERAGE-REVIEW-02)の結果は
   OPEN-186のPhase B live telemetry判定とは独立した論点(Tier1自体の
   実装是正)であり、OPEN-186の記載へ追記が必要(§8 SSOT記載案)。

## 8. SSOT記載案(記載のみ、本Phaseでは編集しない)
- `EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02_REPORT.md`(新設、
  本設計のREPORT化)。
- OPEN-186への追記案: 「追記5(2026-09-28、
  `EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02`、Phase 1原因分析
  完了): 実運用でcanonical "Act One" vs ASR "Act 1"がPhase A Tier1で
  救済されなかった実例(Hormuz記事、telemetry上15回のNG再掲)を調査。
  Tier1の数値語パーサ自体は正しく機能しているが、同一segment内の
  無関係な打点略語(U.S./US)・日付序数接尾辞(13/13th)のatom数不一致
  により、whole-segment all-or-nothing判定が全体を道連れに非等価と
  判定していたことをコード実行で特定した。実装是正案(Category A、
  diff-anchored比較への変更含む)を設計、Mandatory Opus L2レビュー待ち。
  Production変更は未実施。」
- Statusの候補: `EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02`は
  `DESIGN_COMPLETED / Opus L2 REVIEW PENDING`(Trial・実装は未着手)。

## 9. 参照
- `EN-ASR-SEMANTIC-EQUIVALENCE-REVIEW-01_REPORT.md`
- `EN-ASR-SEMANTIC-EQUIVALENCE-TRIAL-01_REPORT.md`
- `EN-ASR-SEMANTIC-EQUIVALENCE-PRODUCTION-WIRING-01_REPORT.md`
- `er021_en_asr_semantic_equivalence_production_01.py`
- `er006_preprod_hardening_01_validation.py`
- `TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01_REPORT.md`
  (Phase 3、Gate項目14、Act One digit読み再現の実測記録)
- `er021_output/en_asr_semantic_equivalence_production_wiring_01/
  telemetry.jsonl`(read-only、本書の母数集計の一次データ)
- `er019_output/family_x_audio_production_wiring_01/family_x_b3_
  diversity_trial_01/hormuz__run_04_parallel_a/b1b/audit/
  tts_generation_results.json`(`local_rewrite_recovery.ng_span`の
  実データ)
- `er021_output/en_asr_semantic_equivalence_trial_01/corpus.jsonl`
  (Trial-01 fixture一覧、§1.4の語数分析対象)

## 10. 修正1回目(Opus L3 BLOCKER-1、2026-09-28追記)との対応(N-6)

Opus L3診断(`EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02_REPORT.md`
末尾「Opus L3診断所見」)がBLOCKER-1として指摘した「句読点atom必須条件の
未実装による分かち書き差・アポストロフィ差の吸収」は、本設計書の以下2点と
以下のとおり対応する。

- **§5(B)-2「複合語分かち書き吸収をTier1へ複製する」(推奨: 変更しない)**:
  実装(Phase 2)は、この(B)-2を意図して実装したものではなく、
  `_closed_punctuation_diff_ok()`の条件(2)(英数字内容完全一致)が
  atom境界情報を捨てる副作用として、事実上(B)-2相当の挙動を実装して
  しまっていた(意図的な機能追加ではなく、実装漏れによる意図しない
  拡張)。修正1回目では、(B)-2の「変更しない」という推奨どおりの状態
  (Tier1は分かち書き差を吸収しない)へ是正した(条件(4)(5)追加)。
  (B)-2の推奨自体は維持されたままであり、本書の分類・判断を変更する
  必要はない。
- **§7-5「実装時にop分割の粒度[SequenceMatcherのopcode境界の取り方]を
  誤ると、意図しない範囲を1つのopとして許容してしまうリスクがあるため、
  実装レビュー時に重点確認が必要」**: この懸念はまさに今回の形
  (alnum連結によるatom境界情報の喪失で、"not able"と"notable"が同一
  opとして誤って許容される)で現実化した。実装時の「重点確認」の一部が
  Phase 2完了時点では抜けており、Opus L3診断でのみ検出された(Mandatory
  Opus L3診断の必要性を裏付ける実例)。修正1回目で該当箇所を是正した。

上記2点はいずれも本設計書レベルでの新しい判断変更を要さない(§5(B)の
分類・「採用しない」判断は維持したまま、Phase 2実装時の実装漏れを
Phase 2修正1回目で是正したもの)。
