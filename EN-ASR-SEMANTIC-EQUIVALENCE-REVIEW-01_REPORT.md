# EN-ASR-SEMANTIC-EQUIVALENCE-REVIEW-01_REPORT

管理ID: EN-ASR-SEMANTIC-EQUIVALENCE-REVIEW-01
日付: 2026-09-26
Status: REVIEW_COMPLETED(Trial deferred、Production採用決定ではない)
レビュー元: `docs/pm/recon_en_asr_semantic_equivalence_01.md`(commit `ba549f05`、read-only)、`docs/pm/recon_en_asr_semantic_equivalence_02_tier2_tier3.md`(commit `76eb3a39`、read-only)

ユーザー指示(逐語):
A-1: レビュー対象はTier 1〜3の3層全面案。ただしProduction採用決定ではなく、まずFableレビュー対象として扱う。A-2: Tier 2も除外せずレビュー対象に含める。安全性・false acceptリスクをFableに確認し、採否はレビュー後。A-3: 今はTrialしない。まずClaude+Fableレビューを完了し、その結果を見てTrial実施要否をユーザー判断する。

本ファイルは、会話ログ
`C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\f1538907-8efe-486d-9790-ef5c6cd789fa.jsonl`
から、assistantレコードで出現する「★★★★報告ここから」ブロックを逐語抽出(要約禁止)したものであり、Part 1(初回Fableレビュー、Tier 1中心・暫定)とPart 2(Fable最終レビュー、3層全面案・Tier 2含む・レビュー完了)の2部構成である。

---

## Part 1 初回Fableレビュー(Tier 1中心、暫定)

### 現在の状態
**Status: USER_DECISION_REQUIRED**(ユーザー指示どおり、レビュー後STOP。実装・Trial・Production変更は一切していない)。事前調査(read-only Recon、commit ba549f05)+Fable批判レビュー完了。

### A-1. Repo上の現行対策(事実)
- 英語ASR照合の主判定は `er006_preprod_hardening_01_validation.py::classify_asr_match`(役割・Family非依存、canonical/ASR文字列のみで判定)。`normalize_numeric()`は cardinal/ordinal語⇔算用数字、桁区切りカンマ、$、小数点、%、日付序数、英米綴り12ペア、住所略語、複合語分かち書き、標準contraction(否定保持、OPEN-123採用分)を既に吸収。
- **実証済みの穴**: `_SCALES`に**billionがない**。**decimal+scale語(2.3 million等)の値を一度も計算しない**ため、canonical「two point three million dollars」vs ASR「$2.3 million」は必ず`TRUE_CONTENT_MISMATCH`→cool-down 600秒→Local Rewrite(Luna 2 call)→再TTSでも不一致→`HUMAN_REVIEW_LOCKED_RETTS_FAILED`(2026-09-26 A2 probe、OPEN-184)。
- 規則的複数形(point/points)は`_is_benign_plural_pair`で内容語差から除外されるが**自動PASSにはならず**`ASR_VALIDATION_UNCERTAIN`×3→cool-down 600秒+Luna 2 callで**canonical文言を書き換えて**解決した実例あり(comment_4)。意味的に無害な差に対し最も高価な回復経路を使っている。
- Local Rewrite(er020)は**NG種別を見ずに**発火する(数字表記差のようにLocal Rewriteで原理的に直らないケースも同じ経路に乗る)。
- want to/wanna等の口語縮約は**2026-09-07ユーザー決定でProduction不採用**(corroboration必須なら救済可能という知見のみ)。drug store/drugstoreは既にNORMALIZED_MATCH。
- Connected Speech Equivalence Layer(OPEN-122、OPEN-121は別件)はCascade層の後段・opt-in・A2/B1本文segmentのみ・Secondary ASR corroboration必須。音韻レベルの差が対象で、今回案(表記・数値レベル)とは層が異なる。
- 回帰基盤: 既存regression 2,112件、OPEN-123の正規化テストセット59通り(POSITIVE 29/AMBIGUOUS 2/NEGATIVE 28、false accept 0)。
- 日本語側の教訓(メタ/メタン): 「一致を広げる」対策は必ずNEGATIVE側(false acceptを増やしていないか)の検証とセット。

### A-2. Fable批判レビュー(22項目)
1. **Tier境界の安全性**: Tier 1は「両側を同一の意味値へ**パース**し、値が完全一致した場合のみ等価」に限定すべき(文字列正規化の拡張ではない)。パース失敗は「等価でない」扱い(best-effort禁止)。日付のスラッシュ形式(4/3)・単一文字単位(m=meter/million/minute)・「a」→1の変換(scale語直前以外)は境界が曖昧なためTier 1から除外。Tier 2は**2026-09-07決定と衝突**するため本案に含めない(再開はcorroboration必須の別判断)。Tier 3は妥当。ただし「規則的複数形の1トークン差」はTier 3の「Secondary ASR救済候補」に明示的に載せるべき(現状は最も高価な経路へ落ちている)。
2. **False accept最大リスク**: Tier 1パーサのバグ(異なる値を同じ値に計算してしまう)。対策: 値比較は`Decimal`の完全一致、片側でも値化できない数はUNKNOWN、NEGATIVE corpus(2.3M vs 2.5M、fifteen vs fifty、15% vs 50%、1999 vs 1990、$あり vs なし、percent vs percentage points、million vs billion、minus vs plus、about 20 vs 20)でfalse accept 0を必須条件にする。
3. **不足カテゴリ**: 年のペア読み(1999=nineteen ninety-nine、2026=twenty twenty-six / two thousand twenty-six)、時刻(3:30=three thirty、am/pm)、分数(one half=1/2のみ、小数への変換はしない)、ローマ数字(World War II vs ASR「World War 2」は実際に起こる)、`No.`/number、`&`/and、複合形容詞の数字(15-minute)、per cent/percent。反対に「the nineties」「half past three」はスタイル差なのでUNKNOWN。
4. **Locale**: 「canonicalは米国英語」を固定ルールとして明記し、多locale実装はしない。£/€は「pounds/euros」への閉じた対応のみ、それ以外の記号はUNKNOWN(現状は記号が黙って消える=情報喪失)。
5. **million/billion**: billion/trillionを追加し、decimal+scaleを`Decimal`で厳密計算(2.3 million=2,300,000、「two million three hundred thousand」も同値→Local Rewrite候補_2のケースも救済できた)。
6. **概数表現(about/nearly/more than/around)**: 現行どおり内容語として**保護**(等価にしない)。概数か正確値かは意味差。
7. **範囲**: 「10–20」「10 to 20」は現行で一致。「between 10 and 20」との等価は**作らない**(TTSが別の語を発話したことになる)。
8. **符号付き**: 「minus」⇔「-」のみ閉じた対応。「negative」は保護、温度単位はTier 1対象外(UNKNOWN)。
9. **電話・住所・ID**: 単独数字語の連続(one two three)を1数値に合成しない(現行の桁単位保護を維持)。7桁以上の数字列は値化せず桁完全一致のみ。
10. **acronym**: ピリオド除去・小文字化により U.S./US/NASA は既に吸収済み。展開(US⇔United States)は**作らない**(TTSが発話した語が異なる)。
11. **所有格・句読点**: アポストロフィ除去後に残る単独「s」が内容語扱いされる残存リスクあり(未検証)。「's」由来のsのみ無視する明示処理を追加。ダッシュ・引用符・カーリークォートは現行除去で十分。
12. **Connected Speech Equivalence Layerとの重複**: カテゴリの重複なし(音韻 vs 表記/数値)。実装場所を分ける: Tier 1は`classify_asr_match`ラッパーの**前段early-exit**、Connected SpeechはCascade後段のまま。Tier 1が既存tokenizeの入力を書き換えない設計にし、3パターンValidatorへの入力を変えない。
13. **Key Phrase Secondary ASRとの重複**: 別問題(ASRの言語誤検出)で重複なし。**Key Phrase役割は本層の対象外**(role gatingはer020の`resolve_narrative_role()`と同じ5役割に揃える)。
14. **現行validatorからの分離**: 新module(例`er021_en_asr_semantic_equivalence_01.py`)に`classify_semantic_equivalence(canonical, asr)`を置き、`classify_asr_match`ラッパー冒頭で呼ぶ(OPEN-123ラッパー方式と同型)。`normalize_numeric()`本体は**Phase 1では無改変**(Key Phrase含む全経路が共有しているため)。
15. **retry/Local Rewriteとの位置関係**: (i) attempt 1の判定時点でTier 1等価→即PASS(retryもcool-downも発生させない)。(ii) Tier 3救済候補(規則的複数形等の1トークン差)は**cool-down前**にSecondary ASR corroboration 1回(限界費用$0.00002)。(iii) diff spanが**数値表記のみ**の場合はLocal Rewriteを**スキップ**してHuman Reviewへ(実証: 600秒+Luna 2 callを消費しても直らない)。
16. **UNKNOWN運用**: 既存`ASR_VALIDATION_UNCERTAIN`(should_retry=False)と同じ扱い=即retryしない(TTSはおそらく正しい)。Secondary ASR corroboration 1回→spanが言い換え可能ならLocal Rewrite→Human Review。UNKNOWN事例は必ずcorpus候補ファイルへ自動追記(下記17)。
17. **Corpus保守**: `regression_corpus.jsonl`(canonical/asr/期待label/証跡パス/日付)。Production runのUNKNOWN・Human Review到達例を候補として自動追記、POSITIVEへの昇格はユーザー/Fable承認、**NEGATIVEをPOSITIVEと同数以上に維持**(メタ/メタン教訓)。unit testで全corpusを¥0実行。
18. **runtime cost/latency**: Tier 1は決定論コードで実質0ms・¥0。Secondary ASR救済は数秒・ほぼ¥0。回避できる損失は1件あたりcool-down 600秒+Luna約¥1+再TTS/ASR約¥2〜3+人手レビュー。純便益はプラス。
19. **決定論コード vs LLM**: 照合経路にLLMは**入れない**(再現性・¥0・テスト可能性)。LLMはcorpus候補の提案など**オフライン補助**に限定(本案では不要)。
20. **既存正常ケースへのリスク**: early-exit(追加的にPASSを増やすだけ)設計なら現在PASSの分布は不変。変わるのは「現在NG→PASS」のみで、そこにfalse acceptが混入しないかをNEGATIVE corpusで担保する。2,112件regression無変化を受入条件にする。
21. **より簡単な代替案(重要)**: 数値false rejectの実証は**架空probe 1件**(canonicalを意図的にspelled-outで書いた)のみ。実記事のcanonicalは通常「$2.3 million」と数字表記で書かれ、ASRも数字で返すため**EXACTで一致する可能性が高い**。よって「大きな3層仕様」を作る前に、`er011_output/attempt_history.jsonl`と`human_review_queue`を機械集計して**実運用で数値/複数形起因のfalse rejectが何件あるか**を確認すべき(¥0)。実件数が少なければ、最小パッチ(billion+decimal×scale値計算/複数形→Secondary救済/数値spanのLocal Rewriteスキップ/corpus)で十分。
22. **追加すべき改善**: (i)証跡先行(21)、(ii)early-exit追加設計、(iii)数値spanのLocal Rewriteスキップ、(iv)cool-down前のSecondary corroboration、(v)`Decimal`厳密比較、(vi)corpus+NEGATIVE同数原則、(vii)どのTierが救済したかのtelemetry label、(viii)Key Phrase非適用、(ix)Tier 2は本案から除外。

### A-3. 推奨最終仕様(Fable案、ユーザー承認前)
- **名称**: English ASR Numeric/Orthographic Equivalence Layer(Tier 1限定、Tier 2なし)。
- **判定ラベル**: 既存ラベルに2つだけ追加: `NUMERIC_EQUIVALENCE_MATCH`(Tier 1値一致、PASS)/`SECONDARY_ASR_CORROBORATED_MATCH`(Tier 3救済、PASS_WITH_WARNING)。7分類の全面導入はしない(UNKNOWNは既存`ASR_VALIDATION_UNCERTAIN`に写像)。
- **Tier 1対象(閉じた集合)**: cardinal/ordinal語⇔数字、桁区切り、小数、decimal×scale(hundred/thousand/million/billion/trillion)、通貨($/£/€⇔dollars/pounds/euros、通貨の有無は保護)、%⇔percent(percentage pointsは保護)、年のペア読み、時刻(h:mm⇔語、am/pm)、単純分数(1/2⇔one half等)、ローマ数字(I〜X)、`No.`⇔number、`&`⇔and、minus⇔-。対象役割は5役割(Full Story/Comment/Preview/Topic intro/In One Line)、Key Phrase/Heading非適用。
- **Tier 3(保護+救済)**: 時制/否定/概数語/値の相違/通貨有無/percentage pointsは保護。規則的複数形・単独固有名詞の1トークン差のみSecondary ASR corroborationで救済候補。
- **配置**: `classify_asr_match`ラッパー前段のearly-exit(新module)+Local Rewrite呼び出し前に「数値spanのみならスキップ」判定。`normalize_numeric()`本体は無改変。
- **安全条件**: NEGATIVE corpusでfalse accept 0、既存regression不変、`Decimal`厳密比較、パース失敗=非等価。

### A-4. リスク・未解決点
1. 実運用での発生頻度が未確認(架空probe 1件のみが証跡)。
2. 年・時刻のペア読みは実装ミスがfalse acceptに直結(NEGATIVE corpusで担保)。
3. Tier 2(wanna等)を含めない判断は2026-09-07決定の維持であり、必要なら別途再判断。
4. `normalize_numeric()`にbillionを直接追加すると全経路(Key Phrase含む)へ影響するため、Phase 1では新module側で計算する設計にしている(将来の一本化は別判断)。

### A-5. Trial設計案(承認前・未実施)
**EN-ASR-NUMERIC-EQUIVALENCE-TRIAL-01**(Production変更なし)
- Phase 0(¥0): `attempt_history.jsonl`/`human_review_queue.jsonl`/`review_lock_state.json`群を機械集計し、NG分類×diff種別(数値/複数形/その他)の件数表を作る。
- Phase 1(¥0): 新moduleとcorpus(POSITIVE≥30: $2.3M probe・年・時刻・通貨・%・billion等、NEGATIVE≥30)、unit test、既存2,112件regression不変確認。
- Phase 2(¥5〜10): 実TTS/ASR probe 5〜10文(数値・年・複数形を含む、`TTS_EXECUTION_MODE=STANDARD`、専用out-dir、既存記事無変更)で、false accept 0・救済率・cool-down/Local Rewrite不発火を確認。既存probe JSON(comment_test2)は再生成せず再判定(¥0)。
- 受入: NEGATIVE false accept 0、POSITIVE救済≥90%、regression不変、cost実測記録。
- **想定cost: 合計¥5〜10、Guardrail ¥30**。Production配線は別管理ID・ユーザー承認後。

### 未解決問題
1. 仕様の範囲(最小Tier 1+救済 vs 3層7分類の全面導入)。
2. Tier 2(口語縮約)を本案から除外する扱いの確認。
3. Trial実施可否(T-2「OPEN-184小Trial」は本Trialに吸収)。

### 次にやること(ユーザー判断後)
1. A-1判断に沿ってTrial設計を確定(仕様変更なしなら上記A-5のまま)。
2. A-3承認後、Phase 0→1→2の順にsonnet-workerへ委任(¥5〜10)。

### ユーザー判断
- **A-1(範囲)**: (a) 最小Tier 1(数値/表記の閉じた集合)+Tier 3救済+数値spanのLocal Rewriteスキップ / (b) 3層7分類の全面導入。**Fable推奨: (a)。** 理由: 実証済みの穴は数値系に集中し、(a)はearly-exit追加設計で既存PASS分布を変えない。(b)は実証のない範囲を広げfalse acceptリスクを増やす。
- **A-2(Tier 2)**: (a) 2026-09-07決定(wanna等不採用)を維持し本案から除外 / (b) corroboration必須条件で再開。**Fable推奨: (a)。** 理由: 既に一度検証・却下済み、証跡1件のみ。
- **A-3(Trial)**: 上記A-5 Trial(¥5〜10、Guardrail ¥30)を実施するか。**Fable推奨: 実施。ただしPhase 0(実頻度集計、¥0)の結果が「実運用0件」ならPhase 2前に再報告してSTOP。**(T-2はこれに吸収)

### 補足・技術詳細
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/recon_en_asr_semantic_equivalence_01.md(Recon全文: 分類フロー13分岐、過去false rejection証跡(a)〜(h)、設計論点表、Regression Corpus候補表)
- 本レビューのREPORT化(`EN-ASR-SEMANTIC-EQUIVALENCE-REVIEW-01_REPORT.md`)とREPORT_LEDGER行追加は、B完了後のcloseout委任でまとめて実施(¥0)。

---

## Part 2 Fable最終レビュー(3層全面案、Tier 2含む)

★★★★報告ここから★★★★

# EN-ASR-SEMANTIC-EQUIVALENCE-REVIEW-01 — Fable最終レビュー(3層全面案、Tier 2含む)。Status: REVIEW_COMPLETED / Trial deferred

REPORT_LEDGER確認: 本件は`REVIEW_PENDING`→本報告でレビュー完了。未回答はR-1/R-2/SE-1(直前のcloseout報告)のみで、決定済み項目は再掲しません。補完Recon: `docs/pm/recon_en_asr_semantic_equivalence_02_tier2_tier3.md`(commit 76eb3a39、全件オフライン実測、¥0)。

## 現在の状態
Claude側(Tier 1中心recon_01+Tier 2/3実測recon_02)+Fableレビューが完了。実装・Trial・Production変更なし。

## レビュー結論(Tier別)

### Tier 1(決定論的等価: 数値・通貨・%・日付・時刻・単位・略語・句読点)
- 前回レビューどおり有効。実証済みの穴はdecimal×scale語(2.3 million)・billion不在・年/時刻のペア読み。
- 実測で判明した実装上の注意: 値の差は2経路で検出される(素の数字=`number_mismatches`、$/%マーカー付き=`content_word_diffs`)。Tier 1は**tokenize前の値パースによるearly-exit**として実装し、既存2経路には触れない。
- ラベル: 7分類のうち新規が必要なのは`NUMERIC_EQUIVALENCE`のみ。呼び出し元の大多数は`should_pass`/`should_retry`(bool)で分岐しており、新ラベルが`should_pass=True`を正しく持てば制御フローは不変。文字列直接比較は`er006_secondary_asr_01.py`内5箇所+`should_stop_retrying()`のみ(個別確認が必要)。er020 Local Rewrite・telemetryはラベル非依存。

### Tier 2(transcript style: contraction/wanna/gonna等)— 安全性・false acceptの確認結果
1. **既存Production機構に実在する穴(新発見、Tier 2導入とは独立)**: OPEN-123で採用済みの標準contraction展開は`'d`を常に`would`、`'s`を常に`is`へ展開する。実測(T2-2-1c): canonical "By the time she called, I'd finished the entire report."(I had)vs ASR "…I would finished…" → **PASS**(`TRANSCRIPT_STYLE_NORMALIZED_MATCH`)。ASRが非文法的な"would finished"を出す確率は低いが、時制解釈が食い違ってもPASSし得る構造は事実。逆方向(ASRが正しく"had")はfalse rejectのまま。
2. **未対応の口語縮約10種(gotta/kinda/sorta/'cause/lemme/gimme/dunno/ya/outta/ain't)**: 現行はすべて`TRUE_CONTENT_MISMATCH`(false accept 0、既知のfalse reject)。個別リスク: `'cause`は名詞"cause"と衝突/`ya`は間投詞用法/`ain't`は5通りに曖昧(単一展開では取りこぼしと誤一致の両方)/`dunno`は否定を内包し`_NEGATION_WORDS`未登録のまま追加すると否定保護をすり抜ける/`kinda`・`sorta`は"of"がstopwordのため"kind of"→"kind"が既に`ASR_VALIDATION_UNCERTAIN`まで来ており、Tier 2でratio閾値やトークン数差を緩めるとそのままPASSに変わる圧力がある/`wanna`は"want to"と"want a"の二義(T2-2-15、現行の「展開後完全一致のみ採用」で安全)。
3. **corroboration条件(mode_c)**: NEGATIVE対照54件で誤一致0、実例1件を正しく救済。ただしSecondary/Localも同じ縮約を返すと救済されない(3経路が独立に誤らない場合のみ有効)。OPEN-122の`_word_at_diff_matches_canonical`/`corroboration_count`と同型ロジックだが未統合(独立実装2つが並存)。
4. **Fable判定**: Tier 2は「閉じたリスト+展開後完全一致+否定・法助動詞に触れない+口語縮約はcorroboration必須+ratio/トークン数の許容を緩めない」の5条件を満たす範囲でのみ安全。この条件下で採用候補は`wanna⇔want to`/`gonna⇔going to`(片方向: canonical完全形・ASR縮約形)に限定。`'cause`/`ya`/`ain't`/`dunno`/`kinda`/`sorta`/`gotta`は**除外**。併せて既存`'d`/`'s`展開の曖昧性は、展開先が一意でないcontractionにcorroborationを要求する形で同じTierで是正すべき。

### Tier 3(保護: 時制・否定・値)と救済候補
- 保護の実効性: 時制3件・否定3件・値3件すべて`TRUE_CONTENT_MISMATCH`を実測(9/9)。接頭辞否定(safe/unsafe)も内容語差として検出。
- 救済候補(Secondary corroboration前提): 規則的複数形(point/points、dollar/dollars)・固有名詞の音訳差(Ottoni/Otani、Triangeln/Triangle)は現行`ASR_VALIDATION_UNCERTAIN`。意味への影響は原則なしだが、多義語"point"(得点)や別実体を指し得る地名は理論上のfalse acceptが残るため、救済は`PASS_WITH_WARNING`+telemetry記録に限定するのが妥当。
- 同音語救済(wait/weight)は本Reconの例文がCMU辞書上同音と判定されず実測不能(既存コードコメントとの齟齬の可能性あり、別件として記録)。
- `ASR_VALIDATION_UNCERTAIN`は3つの異なる原因(固有名詞差/同音語差/一致率不足)を1ラベルに集約している。UNKNOWN運用にはラベル追加ではなく**sub-reasonフィールド**を持たせ、corpus候補の自動追記に使う。

### 実運用頻度(観測性のギャップ)
英語attempt 4,069件(OK 2,233/STOPPED 1,411/UNCERTAIN 425)だが、`attempt_history.jsonl`はcanonical/ASR本文をsha256しか保存しておらず、**NGの内訳(数値/複数形/縮約/その他)は判別不能**。review_lock_state/tts_generation_resultsから縮約救済の発火が11件確認できたのみ。→ どのTierに実効があるかを測る前提として、**NG時のcanonical/ASR/diff spanをログへ保存する観測性修正**(挙動変更なし、¥0)が先。

### Cost/latency
Tier 1: ¥0・0ms。Tier 3救済/Tier 2 corroboration: Cascadeが既に発火している経路では追加¥0、未発火経路で新規にSecondaryを呼ぶ設計なら1回あたり限界費用は無視できる水準(Azure単発は音声長按分で約¥13.8相当という別見積もりもあり、設計で「Cascade結果の再利用のみ」に限定すべき)。回避できる損失は1件あたりcool-down 600秒+Luna 2 call+再TTS。

## 推奨最終仕様(段階導入、いずれもTrial gate付き・Production採用は別途ユーザー承認)
- **Phase A**: 観測性修正(NG時のcanonical/ASR/diff span保存)+Tier 1数値early-exit(`NUMERIC_EQUIVALENCE`、`Decimal`厳密比較、パース失敗=非等価)+数値のみspanのLocal Rewriteスキップ。
- **Phase B**: Tier 3救済(規則的複数形・固有名詞差)をcorroboration付き`PASS_WITH_WARNING`でcool-down前に判定。`ASR_VALIDATION_UNCERTAIN`にsub-reason付与、corpus自動追記。
- **Phase C**: Tier 2口語縮約(`wanna`/`gonna`のみ、片方向、corroboration必須)+既存`'d`/`'s`曖昧展開の是正。OPEN-122のcorroboration関数へ統合(独立実装の解消)。
- 全Phase共通: NEGATIVE corpusをPOSITIVEと同数以上に維持、既存regression不変、Key Phrase役割は対象外。

## リスク・未解決点
1. 既存Production(`'d`/`'s`展開)の穴は実運用での発生確率が不明(観測性修正後に判断)。
2. Phase Cの救済率は「3経路が独立に誤らない」ことに依存し、限定的。
3. 同音語救済ロジックの実測不能(コードコメントとの齟齬要確認)。

## ユーザー判断(必要な1件のみ)
- **A-T**: Trialを起票するか。(a) Phase A(観測性+Tier 1)のみ先行(¥5〜10)/(b) Phase A+B(¥10〜15)/(c) 起票せず保留。**Fable推奨: (b)。** 理由: Phase Aは実証済みの穴(数値)に直接対応し、Phase Bは実本番で600秒+Luna 2 callを消費した複数形ケースを安価に解消できる。Phase Cは観測性データが溜まってから別判断。
- (参考)未回答: R-1/R-2(Family X Retry対策)、SE-1(効果音)。

## 補足・技術詳細
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/recon_en_asr_semantic_equivalence_02_tier2_tier3.md
- https://raw.githubusercontent.com/shimomura055/eigo-radio/main/docs/pm/recon_en_asr_semantic_equivalence_01.md
- 本レビューの`EN-ASR-SEMANTIC-EQUIVALENCE-REVIEW-01_REPORT.md`への転記・OPEN-186 Status更新(`REVIEW_COMPLETED`/Trial deferred)・LEDGER更新は、実行中のSSOT追従修正が完了次第委任します(¥0)。

★★★★報告ここまで
