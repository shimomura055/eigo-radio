管理ID: EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02(paperworkのみ: Opus L3所見の逐語保存。**所見の実装・コード変更・SSOT[CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS]編集はしない**。¥0、API呼び出しなし)。一時ファイル `docs/pm/ACTIVE_TASK_ASRO.md` / `docs/pm/RESULT_PACKET_ASRO.md`(commitしない)。E-1/D-1/G-1: 再読なし、Grep→範囲Read、git出力最小化。T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02_03.md` に保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02_03.md --json-out docs/pm/delegation_log/2026-09-28_EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02_03.md_check.json` を実行、結果1行記録。並行: 別Sonnetが `TTS-GEMINI-3.8-FLASH-LITE-*-02_REPORT.md`・`docs/pm/REPORT_LEDGER.md`・`user_test/`・`er003_key_words_*`・`er030_*`・`er035_*` を編集中 → 本タスクは `EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02_REPORT.md` 末尾へ「## Opus L3診断所見(逐語、2026-09-28)」を**追記のみ**。`docs/pm/REPORT_LEDGER.md` は `git status --porcelain docs/pm/REPORT_LEDGER.md` で差分なしを確認できた場合のみ本ID行の「Opus発火」列を「L3 1回(2026-09-28実施、BLOCKER 1件[句読点atom必須条件の未実装=分かち書き/アポストロフィ差の吸収]、SF 5件、N 10件。所見反映はユーザー判断待ち)」へ更新、差分があれば触らず追記案をRESULT_PACKETへ。

以下をREPORT末尾へ**一字一句そのまま**転記する(要約・改変禁止。冒頭に「本節はFableが受領したOpus L3診断の逐語転記(Sonnetによる保存作業のみ、実装は未着手・ユーザー判断待ち)」と注記):

---(逐語ここから)---
# Opus L3診断: EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02(commit 3d9a28be)

前提: read-only。コード編集・テスト実行・API呼び出しは一切行っていない(判定はコード精読による静的追跡。反例は下記のとおり行単位で経路を追跡済みだが、¥0の決定論probeでの機械確認はFable/Sonnet側に委ねる)。

## 総括
- 承認仕様の**中核条件のうち1つが実装されていない**。すなわち「句読点atomを必ず含む差分のみ」という条件が`_closed_punctuation_diff_ok()`に存在せず、結果として**語境界(分かち書き)差とアポストロフィ差が吸収される**。この抜けにより「否定語の欠落」が吸収され得る具体的経路があり、かつDEFERRED扱いの`'s`処理が事実上実装されてしまっている。→ BLOCKER 1件。
- それ以外(数値/時刻atomの保護、op数・比率上限、月名限定序数、ローマ数字安全化、"and"バグ修正、`autojunk=False`、共通化)は設計どおりで、安全方向の締めも含め妥当。修正は**2行程度**で、既存54テスト・evidence(reversal 7件、Hormuz実artifact再判定)を壊さない(下記で個別に検証)。

---

## BLOCKER-1: 「句読点atomを必ず含む差分のみ」が未実装 → 分かち書き差・アポストロフィ差の吸収(否定語欠落・DEFERRED項目の暗黙実装を含む)

根拠(ファイル:行)
- `C:\Users\tensh\eigo-radio\er021_en_asr_semantic_equivalence_production_01.py:537-577` `_closed_punctuation_diff_ok()`。条件は (1) 両側literalのみ (2) `re.sub(r"[^a-z0-9]","",word)`連結の完全一致 (3) 両側非空、の3つだけ。**「差分opに句読点atom(alnumが空のatom)を含むこと」を要求していない**。
- 同関数docstring L550-554 の論拠「alnum内容が一致するならその差は必ずpunctuation由来である」は誤り。差は**空白(トークン境界)由来**でも成立する。alnum連結はatom境界情報を捨てるため、`["not","able"]`と`["notable"]`が等価判定される。
- 早期exitは`C:\Users\tensh\eigo-radio\er006_preprod_hardening_01_validation.py:1210-1222`で`_classify_asr_match_core()`より前に`ProtectedCheckResult(passed=True)`で即PASSするため、`protected_check()`(同ファイル:673-677の否定語チェック)は**実行されない**。つまりこの穴は否定保護を直接すり抜ける。

反例(role適用segment、`classify_asr_match(..., segment_id="full_story_part1")`経路。いずれも atom 17/16、absorbed_ops=1、absorbed_atom_total=3、3/17≈0.176 ≤ 0.2 のため上限では止まらない)

1. 否定の消滅(最重要)
   - canonical: `The findings are not able to explain the 20 percent drop recorded across the region this year.`
   - ASR: `The findings are notable to explain the 20 percent drop recorded across the region this year.`
   - 経路: 差分op = replace `[lit"not", lit"able"]` vs `[lit"notable"]` → 両側literal・alnum `notable` 一致 → 吸収 → `NUMERIC_EQUIVALENCE_MATCH`(`should_pass=True`)。承認仕様「否定の欠落は吸収しない」に反する。
2. 意味反転する分かち書き差
   - canonical: `Officials said the 2 islands remain a part of the territory, and the review will finish in 2027.`
   - ASR: `... remain apart of the territory, ...` → `["a","part"]` vs `["apart"]` を吸収。
   - 同型: `may be`↔`maybe` / `in to`↔`into` / `some time`↔`sometime` / `every one`↔`everyone`。
3. DEFERREDのはずの`'s`処理が発火
   - canonical: `Ottawa's mayor said the 20 percent plan would start in 2027 across the region this year.`
   - ASR: `Ottawa s mayor ...` → replace `[lit"ottawa's"]` vs `[lit"ottawa", lit"s"]` → alnum `ottawas` 一致 → 吸収。
   - REPORT「`'s`はDEFERRED(未実装)」(L338-339)は事実と不一致。
4. アポストロフィ単独差(1atom↔1atom)
   - canonical `We're seeing a 20 percent rise ...` / ASR `Were seeing ...` → alnum `were` 一致で吸収。逆方向(canonical `were` / ASR `we're`)も同様に吸収され、`its`↔`it's`、`he'll`↔`hell`、`she'd`↔`shed` も同じ経路。

緩和事情(重要、severity判断材料)
- 既存baselineの`despaced()`(`er006_...validation.py:986-989`)も**protected_checkより前に**空白除去一致でPASSするため、「分かち書き差だけ」の単独ケースは従来からPASSしていた。したがって本件はend-to-endで完全に新規の穴ではなく、**新規に拡大するのは「分かち書き/アポストロフィ差 × 数値表記差の同居」**(旧`despaced()`では救えなかった組合せ)。
- それでも(i)ユーザー承認仕様の明示条件(句読点atom必須/否定の非吸収)に反する、(ii)DEFERRED項目の暗黙実装、(iii)REPORTの「false accept 0」根拠testにこのクラスのnegativeが1件も無い、の3点から、`PRODUCTION_WIRED`宣言前に是正が必要と判断する。

最小修正案(er021側2行、`_closed_punctuation_diff_ok()`内)
```
punct_present = any(re.sub(r"[^a-z0-9]", "", a["word"]) == "" for a in (*canon_slice, *asr_slice))
if not punct_present:
    return False
```
影響確認(精読ベース、いずれも維持される)
- Hormuz型 `["us"]` vs `["u",".","s","."]`: `.`atomがあるためPASS維持 → 新規25テストのHormuz複合test・長尺punctuation-only test・evidence(b)(absorbed_ops=1)・offline再判定のreversal 7件(うち1件は`safe. But`↔`safe, but`の`.`↔`,` replaceでこれも句読点atomを含む)は**すべて不変**。
- 他のpositive test 8件(序数語/per cent/and/meridiem/hyphenated/COVID-19/月名序数/Section V)は差分opが発生しない(parser・前処理段で吸収)ため無影響。
- negative test 14件は元々rejectなので無影響。
- 副作用: `we're`↔`were`等がTier1で吸収されなくなるが、baseline側の既存正規化経路が従来どおり担うため実害はfalse rejectのみ(安全方向)。

任意の二重防御(推奨、er006側1箇所)
`er006_...validation.py:1211`で`tier1.get("diff_anchored")`がTrueのときのみ、`protected_check(tokenize(canonical_text), tokenize(asr_text)).negation_mismatches`が空であることを追加条件にする。Hormuz実データは両側とも`not`が同位置にあり否定差ゼロなので既存evidenceを壊さない。

残存リスク(修正後も理論上残る、要記録)
句読点atomと語境界ずれが**同一op内に同居**する場合(例: canonical `U.S. not able` vs ASR `US notable`)はalnum一致で吸収され得る。完全に閉じたいなら追加条件「句読点atomを除いた側のatom数の`min`が1(=片側が結合形の1語)」を入れる。Hormuz型は`min(1,2)=1`で通り、上記の混在型は`min(4,2)=2`で落ちる。

---

## SHOULD_FIX

- **SF-1(証拠の衛生): unit testがProductionのtelemetryへ書き込んでいる。** 新規テストは実配線`val.classify_asr_match(..., segment_id=APPLICABLE_SEGMENT_ID)`を使うため、NG時に`er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl`へ追記される(`er006_...validation.py:1263-1271`、書込先は`er021_...production_01.py:50`)。実測でも母数が4,187→4,536件、`protected_number`が1,672→1,813件へ増えており、合成fixtureが実運用ログに混入している。REPORT自身も「cap_limited 1件は本Phaseのtest実行由来」と認めている(REPORT L264-270)。修正案: テスト側で`TELEMETRY_LOG_PATH`を一時ディレクトリへ差し替える(monkeypatch)。既存混入分は「test由来期間」としてOPEN_ITEMSに明記。
- **SF-2(REPORTの過大主張1): 「assertで不変条件を固定」は実質無効。** `er021_...production_01.py:571-577`は`ok = (canon_alnum == asr_alnum)` の直後に`if ok: assert canon_alnum == asr_alnum`で恒真、かつ`python -O`で消える。削除するか、実効のある不変条件(非literal atom不在/句読点atom存在)をassertする。
- **SF-3(REPORTの過大主張2): 「既存合格経路の挙動は完全に同一」は不正確。** 比較アルゴリズム(全体zip)は保存されているが、atom化自体が変更されている(序数語/序数digit token/per cent/meridiem/月名序数/hyphen・minus順序/ローマ数字gate)。特にローマ数字安全化は**従来PASSしていた組合せを落とす**(安全方向だが挙動変化)。SSOT/Gate記述は「既存の比較方式は不変、atom化は分類A修正の範囲で変更」と書き分けるべき。
- **SF-4(test coverageの欠落): 分かち書き差・アポストロフィ差のnegative fixtureが0件。** BLOCKER-1の是非にかかわらず、`not able`/`notable`、`a part`/`apart`、`Ottawa's`/`Ottawa s`、`were`/`we're`をTier1直呼びのnegativeとして固定すべき(将来の再発防止)。
- **SF-5(Gate 3表の表現): 「runtime evidence 完了」は内訳の明示が必要。** 実TTS+実ASR 2 segment(c)は新規則を発火させていない(REPORT L246-250で自認)。新規則の実経路発火は(b)の実Production artifact再判定のみ。Gate表の行に「新規則の実経路発火は(b)の実データ再判定で確認、(c)は発火せず」と明記するのが安全(1記事ずつ完結原則・安全≠成功原則の観点)。

## NOTE

- N-1(論点1a): 数値・時刻atomは`_closed_punctuation_diff_ok()`の条件(1)(L567-568)で確実に非等価へ落ちる。`_atom_key()`(L514-525)がvalue/currency/percent/ordinal/meridiemをキーに含むため、値違いは`equal`になり得ない。ここは仕様等価で問題なし。7桁以上の裸digitのみ`kind="literal"`(L444-447)となり理論上alnum比較の対象になるが、区切りが入ると各片が数値atom化して弾かれるため実害なしと判断。
- N-2(論点2, 月名限定): `_DATE_ORDINAL_RE`(L97)は月名+空白+1〜2桁+接尾辞に限定され、`Act 13th`等の非月名文脈へは漏れない(`Act 13th`は`ordinal=True`のnumber atomとして`13`と非等価、長尺negative testでも固定済み)。残留は英語の`may`/`march`が月名と同綴りである点のみ(er006の既存承認ロジックと同一スコープ、実害は極小)。
- N-3(論点2, ローマ数字): `_ROMAN_AMBIGUOUS_SINGLE`ゲート(L459-461)は直前の生tokenを見るため、`Act: V`のように句読点が挟まると不発(false rejectのみ)。また閉じたラベル語リスト外(`Super Bowl V`、`Series X`等)は従来PASSしていたものが落ちる。いずれも安全方向。POSITIVE corpus 125件無回帰というREPORT主張と矛盾する箇所は精読では見つからなかった。
- N-4(論点2, "and"修正): `_consume_number_word_run()`(L263-283)の先頭/末尾"and"除外は、`one hundred and five`のscale経路(`_words_to_number_scale()`が"and"をskip)を壊さない。逆に従来の「`and five`→num(5)1 atom」による語落ち(false accept方向の副作用)も締まる。設計どおり。
- N-5(論点3): 新規則は`protected_check`より前でPASSを返す(`er006_...validation.py:1210-1222`)。これはPhase A承認済みの既存構造だが、受理集合が広がった分だけ保護層のバイパス範囲も広がっている。BLOCKER-1の修正+任意の否定二重防御でこの範囲を承認仕様の幅に戻せる。
- N-6(論点4, L2対応): 設計書§7-5が明示した「op分割粒度を誤ると意図しない範囲を1つのopとして許容する」という懸念は、**まさに今回の形(alnum連結によるatom境界情報の喪失)で現実化している**。また設計書§5(B)-2「複合語分かち書き吸収をTier1へ複製しない(推奨: 変更しない)」に対し、実装は事実上それを実装している。すなわちL2/設計書レベルの論点は**一部未対応**。既存NEGATIVE corpus回帰(125件)とop数・比率上限は対応済み。
- N-7(論点5の読み方): offline再判定はtelemetry=「過去にNGだった記録」のみを母数とするため、**false rejectの減少量**しか測れず、**false acceptの増加**は構造的に検出できない(従来PASSした記録はログに無い)。reversal 7件が全てHormuz由来という結果は「受理拡大が局所的」を示す弱い証拠にはなるが、「false accept 0」の根拠にはならない。加えて母数に自作test fixtureが混入(SF-1)。`near_match 423件`の目視は有用だが、これも「NG側」だけの視界である点を記録すべき。
- N-8(実務上のカバレッジの狭さ): 条件(3)によりinsert/delete(片側空)は不吸収なので、**ASRが最も頻繁に起こすcomma落ち等の句読点欠落は救われない**(Tier1は非等価→baselineへ)。加えてop上限3のため、打点略語が4箇所以上ある長尺segmentはcap_limitedで落ちる。SSOT側で「構造的耐性」を過大に書かないほうがよい。将来「alnumが空のatomのinsert/deleteのみ許容」へ広げる案は、`12-34`↔`12 34`のような区切り記号の意味差を含むためユーザー判断事項(現時点の据え置きは妥当)。
- N-9(共通化の検証残): `_MONTHS`/`_DATE_ORDINAL_RE`/`_ORDINAL_WORDS`はer021に一本化され、er006(`:124`,`:170-171`)は参照のみ。repo内に重複定義は無い(grep確認、`er003_audio_tts_asr_safety.py`は別目的の`_INTERNAL_LABEL_ORDINAL_WORDS`)。ただし「移設前後で集合が完全同一か」はgit diffでの1行確認を推奨(¥0)。er021の月名は標準12件のみで、旧実装と差異がある兆候は精読では見つからなかった。
- N-10(層間不整合、false rejectのみ): `July thirteenth`↔`July 13`はer006側では序数語→`13th`→月名限定吸収で一致するが、Tier1は`_preprocess_raw()`で序数語→digit変換を行わないため一致しない。安全方向のため対応は任意。

---

## 論点6: `PRODUCTION_WIRED`判定への所見(判定はFable/ユーザー)
- 採用可否は人間ユーザーのみが決定するもので、本診断は判断材料の提示に留める。
- 技術所見としては、**BLOCKER-1(2行の追加条件+SF-4のnegative test)を先に入れてから`PRODUCTION_WIRED`とするのが安全**。理由: (i)承認仕様の明示条件(句読点atom必須/否定非吸収)との不一致、(ii)DEFERRED項目(`'s`)の暗黙実装、(iii)修正コストが極小でevidence再取得も不要(既存evidence・54テストは修正後も成立する見込み)。
- もしユーザーが「分かち書き/アポストロフィ差の吸収も許容する」と判断するなら、それは**承認仕様の拡張**であり、Fable/Claude側で黙示的に確定せず、`USER_DECISION_REQUIRED`として明示の再承認を得る形が整合する。
- SF-1(telemetry汚染)は判定とは独立だが、今後のGate判断の一次データを汚すため早期に是正が望ましい。

参考にした主なファイル
- `C:\Users\tensh\eigo-radio\er021_en_asr_semantic_equivalence_production_01.py`
- `C:\Users\tensh\eigo-radio\er006_preprod_hardening_01_validation.py`
- `C:\Users\tensh\eigo-radio\er021_en_asr_semantic_equivalence_production_wiring_01_test_01.py`(L534-774)
- `C:\Users\tensh\eigo-radio\EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02_REPORT.md`
- `C:\Users\tensh\eigo-radio\docs\pm\design_en_asr_orthographic_equivalence_coverage_02.md`
- `C:\Users\tensh\eigo-radio\er021_output\coverage_review_02\offline_telemetry_reclassify_01_result.json`

入力範囲は十分だった(追加で必要なファイルは無い)。唯一、N-9の集合同一性のみgit diff未確認。
---(逐語ここまで)---

Git: REPORT(+REPORT_LEDGER[条件付き])+delegation_log+_check.json をpath指定add、メッセージ `EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02: Opus L3診断所見(BLOCKER 1/SF 5/N 10)を逐語保存`、trailer `Management-ID: EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02`、push origin main。他Agent差分は巻き込まない(`git add -A`禁止)。RESULT_PACKETに commit hash・raw URL。
