# FAMILY-A-DISCOVERY-TOWELS-A2-JA-ASR-VARIANT-RECONCILE-01

## 要点(5行)
1. タオルTrial-11 A2 `comment_2`(6/6take TRUE_CONTENT_MISMATCH)は、既存の日本語ASR表記ゆれ対策(`er007_ja_asr_validator_01.py`の読み一致判定+`er011_a2_reading_resolver_01.py`のReading Resolver)の**対象範囲内**だが、両方が依拠するpykakasi内蔵辞書(kanwadict)に「経」の読み候補として「た」(「経つ」=たつ)が**そもそも存在しない**ため機能しなかった。
2. 「におい」/「ニオイ」表記ゆれは既存の読み一致判定で正しく吸収されており(offline再現で確認)、機構自体は健全。壊れているのは「経」1文字のkanwadict候補不足のみ。
3. Reading Resolver(LLM選択)も候補リスト外を選ばせないfail-safe設計のため、候補に「た」が無い以上、LLMを呼んでも構造的に解決不可能(候補生成部分のみoffline確認、LLM本体は今回呼んでいない)。
4. 過去の日本語A2/B1監査ログ(全リポジトリ、canonical/ASRペア18件、重複除去後)をoffline再分類した結果、同種の「読み一致するはずが辞書候補不足で失敗」パターンは comment_2 の6件(1segment)のみで、残り10件は読みも実際に異なる真正な内容差(現行判定は妥当)。
5. 修正には辞書外読みの補完(新しい正規化ロジック・新依存関係の追加)が必要で、これは新仕様に該当するためSTOP・USER_DECISION_REQUIRED。comment_2自体は内容的に正しい可能性が高く、既存のHuman Review機構(試聴→`record_human_approval()`)で解決可能。

---

## 前提: 作業中に発生した逸脱の開示

調査の途中、`er011_a2_reading_resolver_01.resolve_reading_diff()`を
`FEATURE_FLAG_A2_READING_RESOLVER_ENABLED`を無効化せずに1回だけ呼び出してしまい、
実際にResolver用LLM(`A2_SUPPORT`ルーティング、`reasoning.effort=low`、1呼び出し)への
課金APIコールが発生した(対象語「にお→臭」、`resolver_calls=1`)。本タスクは
「offline関数呼び出しのみ・API支出禁止」だったため、この1件は禁止事項への
違反であることをここに明記する。金額はごく小さい(low-effort・短文1件)と
推測されるが、正式な確認・是正が必要であればユーザー判断を仰ぐ。以降の
全呼び出しは`FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = False`を明示して
LLM呼び出しを避けた。

---

## Family / 現象

- Family: 日本語ASR照合における「表記ゆれ」誤判定(TRUE_CONTENT_MISMATCH)。
- 現象: `er011_output/discovery_generalization_towels_trial_11/a2/human_review/review_package.md`
  記載のとおり、A2 `comment_2`(canonical:
  「洗濯して乾かしても、においが残ることがあります。では、タオルの中には、
  時間がたつと何が残るのでしょうか。」)が、標準2回+fallback1回×2round
  (合計6take)すべてTRUE_CONTENT_MISMATCHとなりHuman Review待ち
  (`review_lock_state.json`=`HUMAN_REVIEW_REQUIRED`)。
- 観測された表記差: 全6takeで「たつ」(ひらがな)→「経つ」(漢字)、
  6take中4takeで「におい」(ひらがな)→「ニオイ」(カタカナ)または
  「臭い」(漢字)。

## 既存対策(該当関数・実装済みSSOT箇所)

`er007_ja_asr_validator_01.py`の`classify_ja_asr_match()`が正式なJA ASR
Validatorであり、以下の階層で表記ゆれを吸収する設計になっている
(コードコメント・CURRENT_SPEC.md「日本語表記ゆれ」項、OPEN-61/OPEN-111で
文書化済み):

1. `normalize_ja()`: NFKC正規化、句読点除去、英字大小文字吸収、閉じた
   助数詞直前の漢数字→算用数字正規化。
2. `protected_check_ja()`: 差分opcode単位で数字・否定を保護した後、
   `_reading_equal()`(pykakasi読み比較、diff箇所の前後4文字を文脈として
   padding)で「読みが同じなら表記(漢字/かな/カタカナ)が違っても許容」
   と判定する。
3. `_reading_equal_allowing_voicing()`: 濁点/半濁点(連濁)差だけの読みゆれ
   はCascade(追加ASR確認)対象。
4. 全文読み一致フォールバック(`whole_text_reading_equal`): canonical/ASR
   の script差(例: 漢字混じり vs 全ひらがな)でopcodeが分断された場合の
   救済。
5. `er011_a2_reading_resolver_01.py`のA2 Reading Resolver(2026-09-03
   Production採用、ユーザー正式承認済み、A2専用): 上記1〜4で読み一致と
   確認できない差分箇所について、pykakasi内蔵辞書(kanwadict)から
   「その漢字が持ちうる読み候補」を機械的に取得し、LLMに文脈から
   1つだけ選ばせて(候補外選択は不可、JSON Schema enumで構造的に禁止)
   再比較する。

これらは全て正式にProduction配線済みであり、「そもそも対象外」ではない。

## 今回なぜ効かなかったか(offline再現で特定)

`FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = False`にした状態
(Resolver=LLM呼び出しを介さない、¥0)で、canonical textと6takeの実際の
ASR書き起こし(review_package.md記載のもの)を`classify_ja_asr_match()`に
直接入力し再現した。結果、**6/6takeとも同じ理由**でTRUE_CONTENT_MISMATCHと
なった:

```
content_diffs: [{"type": "replace", "canonical": "た", "asr": "経", ...}]
```

(take6のみ追加で `{"canonical": "にお", "asr": "臭", ...}` も存在)

「におい」→「ニオイ」の差は`_reading_equal()`により正しく吸収され、
content_diffsに一切現れない(機構は健全に動作)。問題は「た」/「経」
1箇所のみ。

原因を特定するため、pykakasiで直接読みを確認した:

```
経つ -> 'へつ'(hetsu)   ← 誤り。正しくは「たつ」
たつ -> 'たつ'(tatsu)
```

pykakasiは「経つ」を「へつ」(経=へ、つ=つ、の機械的合成)と読んでしまい、
canonical側の「たつ」と一致しない。さらにA2 Reading Resolverの候補生成
部分(`single_char_candidates('経')`、LLMを呼ばないoffline部分)を直接
確認したところ:

```
候補一覧: ['けい', 'きょう', 'へ', 'つね']
```

候補に「た」が**含まれていない**。Resolverは「与えられた候補からLLMが
1つ選ぶ」設計(候補外は選ばせないfail-safe、ユーザー正式決定§2)のため、
候補に正解が無い場合はLLMをどう呼んでも構造的に解決不可能である。これは
実際にLLMを呼ぶまでもなく、候補生成部分(offline、pykakasi辞書引き)だけで
確認できた。

参考: 「経つ」を「たつ」と読むのは常用漢字表に載る公式な訓読みではなく
(表内訓は「経る」=へる のみ)、実務上よく使われるが辞書によっては
収録されない読みである。したがって今回のkanwadict欠落は単純な実装漏れ
というより、**採用している読み辞書(pykakasi内蔵kanwadict)が常用漢字表
ベースであることに起因する既知種類のカバレッジ限界**に近い。

なお、OPEN-61/CURRENT_SPEC.md記載の既存の「既知の残存限界」(「頃」の
ころ/ごろ、「後」のあと/のち等)は、**辞書上は複数の読み候補が存在し、
どれが正しいか文脈依存で決めきれない**という曖昧性の問題だった
(Reading Resolverはこの種類を解決するために作られ、実際に「後」で
成功実績がある、OPEN-111参照)。今回の「経」は候補自体が**存在しない**
ケースであり、これまで文書化されていた限界とは微妙に異なる派生パターン
である。

## 追加Trial(offline再現、実施したもの)

1. 6take全件をclassify_ja_asr_match()へ直接入力(Resolver無効、コード
   変更なし)→ 全件同一原因(「た」/「経」)を確認(上記)。
2. `single_char_candidates('経')`を直接呼び出し、候補一覧に「た」が
   無いことを確認(offline、pykakasi辞書引きのみ)。
3. 一般化のための集計: リポジトリ全体の`tts_generation_results.json`
   相当の監査ファイル(110ファイル走査)+`human_review_resume*_results.json`
   から、canonical_textとASR書き起こしがペアで残っている日本語segmentの
   TRUE_CONTENT_MISMATCH攻撃結果を抽出し、重複除去後18件のcanonical/ASR
   ペアを得た。これを現行コード(Resolver無効、¥0)で再分類した結果:
   - 2件: 現行コードでは既にNORMALIZED_MATCH/PHONETIC_MATCHに変わって
     いた(生成当時より後のコード改善で解消済みの古い記録、
     `open112_trend_theme2_b_full_audio_trial_13`の「2泊」/「二泊」等)。
   - 16件が依然TRUE_CONTENT_MISMATCH。うち**6件(=1segment、comment_2の
     6take)のみ**が今回と同じ「読みは本来同じはずだが辞書候補不足で
     機械的に読み一致と判定できない」パターン。
   - 残り10件(「帰属意識」系5件、「活動し続ける」系3件、「名所を中心
     にした旅程」系2件)は、実際に読みも異なる(例: 帰属=きぞく/記憶=
     きおく等)真正な内容差であり、現行のTRUE_CONTENT_MISMATCH判定は
     妥当(表記ゆれ問題ではない)。
   - 副次的な追加観測: 「名所を中心にした旅程」vs「名勝を中心にした
     旅亭」の`程`/`亭`の部分だけを見ると、pykakasiは「旅亭」全体を
     `tabitei`(訓読み優先の誤読み、正しくは`ryotei`)と読んでおり、
     comment_2と同種のkanwadict由来の誤読みが別の語でも起きうることを
     示す一例。ただしこのケースは`所`/`勝`側が既に真正な内容差のため、
     最終分類には影響しなかった。

## 結果

- comment_2の6/6 TRUE_CONTENT_MISMATCHは、既存対策の「対象外」ではなく
  「対象内だが、依拠する外部辞書(pykakasi kanwadict)に該当読みが
  存在しないため機能しなかった」個別の限界と特定した。
- 全体としては、日本語ASR表記ゆれ対策は概ね機能している(におい/ニオイ、
  過去の数字表記ゆれ等は正しく吸収)。今回のような「辞書に正解候補が
  無い」パターンは、抽出できた過去データの範囲(18ペア中)では comment_2
  の1segmentに限定的に観測された。

## Production判断が必要か

**新仕様が必要(STOP・USER_DECISION_REQUIRED)。** 以下はいずれも
「新しい正規化ルールの発明・新依存関係の追加」に該当し、Sonnetの判断で
実装してはならない範囲のため、是正候補の提示のみに留める(コード変更は
一切行っていない):

- 候補A: kanwadictに無い読みのための小さな閉じた補完テーブルを追加する
  (英語Validator側で既に前例のある設計思想、CURRENT_SPEC.md 864行目
  「辞書に無い語向けの小さな閉じた補完テーブル」)。
  - 変更箇所: `er011_a2_reading_resolver_01.single_char_candidates()`
    または`er007_ja_asr_validator_01._reading_equal()`に、追加候補
    テーブルを挟む。
  - 影響範囲: A2(日本語)ASR判定全体(過去A2セグメント含む再評価が必要)。
  - 回帰リスク: 補完テーブルの追加語が誤った早期PASSを招く可能性
    (新しい許容基準のため、fixtureでの検証が別途必要)。
  - 費用: 実装+regression再実行(TTS/ASR再実行は伴わない、offlineの
    fixtureテストのみなら低コスト)。
- 候補B: pykakasi(kanwadict)から形態素解析ベースの辞書(fugashi/
  sudachipy等)へ切替・併用する(OPEN-61に将来検討事項として既に記録
  済み、現環境未インストール)。
  - 変更箇所: 読み比較エンジン自体の置換、影響範囲が広い(A2全体、
    将来のB1拡張時にも影響しうる)。
  - 影響範囲・回帰リスク: 大(既存のfixture・regression全体の再検証、
    新規依存パッケージの追加要)。
  - 費用: 実装・検証コストが候補Aより高い。
- 候補C(コード変更なしで今回解決可能): comment_2自体は、6takeいずれも
  「同じ意味・同じ発音の表記ゆれ」である可能性が高く、既存のHuman Review
  機構(試聴→ユーザー判断→`record_human_approval()`)で解決できる。
  これは新仕様ではなく、既存機構の正しい用途内の対応であり、ユーザーの
  試聴判断のみで前進可能(review_package.mdの選択肢(a)(b)(c)参照)。

## 参照した既存SSOT

- `er007_ja_asr_validator_01.py`(JA ASR Validator本体)
- `er011_a2_reading_resolver_01.py`(A2 Reading Resolver)
- `er011_output/discovery_generalization_towels_trial_11/a2/audit/
  tts_generation_results.json`
- `er011_output/discovery_generalization_towels_trial_11/a2/human_review/
  review_package.md`
- `OPEN_ITEMS.md` OPEN-61(JA Validator再設計・既知の残存限界)、
  OPEN-111(A2 Reading Resolver Production採用・「後」での成功実績)
- `CURRENT_SPEC.md`「日本語表記ゆれ(漢字/かな)のCascade内自動PASS条件」
  行(既知の限界の正式記載箇所)
