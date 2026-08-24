# ER-007-EVIDENCE-WORDCOUNT-JA-ASR-EFFECTIVENESS-AUDIT-01 完了報告

**本タスクはAudit専用であり、実装変更は一切行っていない。新規API呼び出しも0件
(既存ログ・既存テキストの再解析、および検証ロジックへ仮想テキストを直接通す
シミュレーションのみ)。**

## Part A: Evidence Compression版の語数確認

### A-1. SSOT確認(正式なtarget)

CURRENT_SPEC.mdを確認した結果、以下が正式に文書化されている。

| 項目 | 正式値 | 状態 |
|---|---|---|
| Point One/Two 個別の目標語数 | 目標30〜60語、許容25〜70語 | `VALIDATED`、**診断的な目安、hard capではない**(CURRENT_SPEC「Point Balance」行) |
| 記事全体の語数 | **「上限なし」と明記**(CEFR比較表「全体語数」行、A2・B1とも) | `DECIDED` |

**重要な発見(SSOT不整合)**: 実装コード(`er003_v1_n3_01_articles_generate.py`)には
`TOTAL_SOFT_LOWER=280`/`TOTAL_SOFT_UPPER=420`という記事全体の「soft range」定数が
存在し、実際にNo.4〜6のA版生成時にも`length_report.json`へ記録されていた。しかし
この280〜420という具体的な数値は、**CURRENT_SPEC.mdのどこにも文書化されていない**
(CEFR表は逆に「上限なし」と明記している)。したがって「280〜420語」は正式な
SSOT記載事項ではなく、コード内部の未文書化diagnostic定数である。本Auditでは
「推測で新しい基準を作らない」という指示に従い、この数値を**参考値**として使い
つつ、正式扱いしていないことを明記する。

### A-2. No.4〜6 B版確認(全6本)

Production Writerが実際に使っている計測関数(`compute_word_count`/`compute_metrics`)
でそのまま再計測した。

| Topic | Level | 全体target(参考値) | A版実測 | B版実測 | 判定(B版) |
|---|---|---|---|---|---|
| No.4 | B1 | 280〜420 | 408 | 351 | PASS |
| No.4 | A2 | 280〜420 | 357 | 333 | PASS |
| No.5 | B1 | 280〜420 | 414 | 382 | PASS |
| No.5 | A2 | 280〜420 | 404 | 384 | PASS |
| No.6 | B1 | 280〜420 | 350 | 355 | PASS |
| No.6 | A2 | 280〜420 | 389 | 367 | PASS |

**全体語数は6本すべてPASS。下限割れは1件も発生していない。**

Point単位(目標30〜60語、許容25〜70語)も確認した。

| Topic | Level | Point One(A→B) | 判定 | Point Two(A→B) | 判定 |
|---|---|---|---|---|---|
| No.4 | B1 | 45→46 | PASS | 65→49 | PASS |
| No.4 | A2 | 46→46 | PASS | 52→50 | PASS |
| No.5 | B1 | 41→41 | PASS | 42→42 | PASS |
| No.5 | A2 | 41→41 | PASS | 39→39 | PASS |
| No.6 | B1 | 46→46 | PASS | 44→66 | **目標超過(許容内)** |
| No.6 | A2 | 78→68 | 目標超過(許容内、A版も既に超過) | 72→72 | **許容も超過(A版から変化なし)** |

### A-3. 下限割れの有無

**下限割れは全体・Point単位とも1件も発生しなかった。** タスク仕様が想定していた
リスク方向(圧縮しすぎて短くなりすぎる)は実際には発生せず、代わりに**上限側の
超過が2件**見つかった。

- **No.6 B1 Point Two(44→66語、目標超過だが許容範囲内)**: 圧縮の過程で、
  `b = 0.90, P < 2 × 10⁻¹⁶`という統計記号表記を、自然な話し言葉("The link
  between uncertainty and checking was strong.")へ置き換えた結果、記号としては
  短くても語数としては増加した。**Evidence Compressionは常に語数を減らすとは
  限らない**(専門記号の圧縮が、自然な説明文への展開によって語数増加につながる
  ケースがあることを示す実例)
- **No.6 A2 Point Two(72語、許容範囲[70語]も超過)**: これはB版で変更していない
  segment(圧縮対象外のまま)であり、**A版の時点で既に許容範囲を超えていた
  既存の状態**。Evidence Compressionが原因ではない

いずれも「hard capではない診断的な目安」への抵触であり、Production的にブロック
される性質のものではない。**今回はEvidence detailを戻す必要のある下限割れが
存在しないため、A-3で想定されていた「補完提案」は不要と判断する。** 上記2件の
上限超過について、ユーザー判断が必要であれば別途対応を検討されたい(本タスクでは
Production script変更は行っていない)。

## Part B: Japanese ASR Validator実効性Audit

### B-1. Segment構造

**「日本語はすべて1 segmentなのか？」→ いいえ。** 1エピソードあたり、B1は
**5 segment**、A2は**11 segment**が日本語で生成されている(実データで確認、
全topic共通)。

| Level | 日本語segment | 件数/episode |
|---|---|---|
| B1 | Key Phrase日本語訳(`kp{1-5}_ja_charon`)のみ | 5 |
| A2 | `japanese_title`、`preview`、`comment_1〜4`、Key Phrase日本語訳(`meaning_1〜5`) | 11 |

B1は**「原則Key Phraseの日本語訳のみ日本語を使用する」**という既存仕様
(CURRENT_SPEC「B1日本語使用範囲」)通り、Preview/Comment/Full Story/Point/
In One Lineはすべて英語(Charon/Aoede)。日本語はKey Phrase glossという
短いsegmentのみに限定されている。

A2は逆に、`japanese_title`/`preview`/`comment_1〜4`という**長めの説明文**が
日本語であり(News本文=Full Story/Point/In One Lineは英語のまま)、これに
加えてKey Phrase日本語訳5件が日本語。

### B-2. 英語と日本語の違い

| 項目 | English | Japanese |
|---|---|---|
| TTS segment単位 | Full Story Part1/2・Point One/Two・In One Line・Key Phrase English Component(News Content、Aoede) | B1: Key Phrase gloss(5件)のみ。A2: japanese_title/preview/comment_1-4/Key Phrase gloss(11件) |
| 平均文字/語数 | 記事本文相当(Part A参照、全体280〜420語目安) | 短いもの(Key Phrase gloss)は数〜20文字、長いもの(A2のpreview/comment)は40〜160文字程度 |
| ASR engine | OpenAI `gpt-4o-mini-transcribe`(Primary) | Azure Speech STT |
| Validator | `er006_preprod_hardening_01_validation.classify_asr_match()`(6分類、数字/否定/内容語のProtected Check、ASR-first Secondary Cascade対応) | `expected_substring_ja()`によるprefix一致 + 文字数許容範囲チェック(第一段階)、失敗時のみ`validate_japanese_short_segment_match()`(第二段階、フォールバック) |
| short/long判定閾値 | 該当なし(全segmentへ同一Validatorを適用) | `JAPANESE_SHORT_SEGMENT_MAX_CHARS = 30`文字。ただし閾値は**第二段階(フォールバック)にのみ適用**され、第一段階はsegment長によらず全件同じ弱い判定 |
| short時の検証 | (該当なし) | 第一段階(prefix+length)が失敗した場合のみ、数字集合一致・否定表現一致・完全一致・読み(ローマ字)完全一致・読み類似度(0.85閾値)による`EXACT_MATCH`/`NORMALIZED_MATCH`/`PHONETIC_MATCH`/`ASR_UNCERTAIN`/`TRUE_CONTENT_MISMATCH`の判定が機能する |
| long時の検証 | (該当なし) | 第一段階が失敗すると第二段階へ進むが、30文字を超える場合`validate_japanese_short_segment_match()`は中身を見ずに即座に`ASR_UNCERTAIN`(不合格)を返す設計。**実質的な追加検証は一切ない** |

**重要な構造的事実**: 第一段階(prefix substring + 文字数許容)は、**segment長に
関わらず全ての日本語segmentに最初に適用される**。第二段階(意味のある検証)は、
第一段階が「たまたま失敗した場合」にのみ発動するフォールバックであり、無条件の
検証ではない。したがって、たとえ30文字以下の短いsegmentであっても、第一段階が
誤って通過してしまえば、第二段階の意味検証は一度も実行されない。

### B-3. No.1〜6 日本語segment長分布

既存の`tts_generation_results.json`を再解析(新規TTSなし)。No.1〜6合計で
**96 segment**の日本語canonical textを収集した(各topic 16件、B1=5+A2=11で一致)。

| 文字数帯 | 件数 | 比率 |
|---|---|---|
| ≤30文字 | 67 | 69.8% |
| 31〜60文字 | 5 | 5.2% |
| 61〜90文字 | 5 | 5.2% |
| 91〜120文字 | 10 | 10.4% |
| >120文字 | 9 | 9.4% |

**≤30文字segment比率: 69.8%。>30文字segment比率: 30.2%**。

>30文字(30.2%)は、B-2で確認した通り「第二段階のフォールバックが構造的に
no-opになる」segment群である。これはA2の`preview`/`comment_1〜4`
(実測40〜160文字程度)にほぼ集中している。

### B-4. 実際のValidator Coverage

B-2/B-3を踏まえ、日本語segmentが実際に受けている検証を分類する。

| 分類 | 該当segment | 実態 |
|---|---|---|
| 実質的にcontent validationなし | >30文字segment(30.2%、主にA2 preview/comment) | 第一段階(prefix 2文字+文字数許容)のみ。中間・末尾の内容変化は検知不能。第一段階が失敗しても第二段階は無条件ASR_UNCERTAINで終わり、追加の意味検証は発生しない |
| partial validation(条件付き) | ≤30文字segment(69.8%、主にKey Phrase gloss) | 第一段階が**先に**適用される(prefix+length)。これがたまたま通過すれば、それ以降の意味検証(数字・否定・読み一致)は一度も実行されない。第一段階が失敗した場合のみ、第二段階の実質的な検証が機能する |

「ASR APIを呼んでいるか」という観点では全segment100%呼んでいるが、「ASR結果を
使って実際にどの程度誤りを検知できているか」という観点では、**全segmentが
第一段階という共通の弱いgateを最初に通過してしまえば、それ以上の意味検証を
一切受けない**という設計になっている。

### B-5. Blind Spot検証(実証)

comment_2(A2/Subscriptions実データ、66文字)を土台に、6カテゴリの誤りを
構成し、実際の第一段階判定ロジック(`expected_substring_ja()` + prefix一致 +
文字数許容)へ直接通した。新規TTS/ASRは呼んでいない。

| カテゴリ | 変更内容 | 検知可否 |
|---|---|---|
| 1文字/1音の誤り | 「スラッジ」→「スラッシ」 | **見逃す(誤ってPASS)** |
| 語の置換 | 「FTC」→「FCC」 | **見逃す(誤ってPASS)** |
| 数字の誤り | 実データ(No.4 comment_2)で「Part 1」→「Part 2」 | **見逃す(誤ってPASS)** |
| 否定の脱落/反転 | 「変えるために」→「変えないために」(意味が反転) | **見逃す(誤ってPASS)** |
| 文中フレーズの脱落 | 文末の問いかけ部分を削除 | **見逃す(誤ってPASS)** |
| 文中フレーズの追加 | 無関係な一文を挿入 | **見逃す(誤ってPASS)** |

**6カテゴリすべてが検知されずPASSしてしまうことを実証した。**

理由はB-2で述べた通り単純である: `expected_substring_ja()`は文頭の安全な2文字
だけを見ており、`length_ok`は元の文字数+40文字という広い許容幅で判定するため、
文中の内容がどれだけ変わっても、文頭と全体の文字数さえ大きく崩れなければ
`substring_ok=True`かつ`length_ok=True`となり、後段の意味検証(第二段階)へは
到達しない。

**「やめにくくする」→「やめにくかする」問題を、なぜ現Validatorが見逃したか**:
実際のcomment_3(118文字)canonical textと、本番で実際に記録されていたASR
書き起こし文字列を、この検証ロジックへ通して再確認した。

```
expected_substring: 'この'  substring_ok=True
length_ok: True(asr_len=117 vs max_len=158)
=> 見逃す(誤ってPASS)
```

文頭の「この」は変化していないため`substring_ok`が通過し、全体の文字数も
許容範囲内(117文字 ≤ 158文字)のため`length_ok`も通過する。したがって
`verified=True`となり、第二段階の意味検証(30文字を超えるため、そもそも
no-opで即不合格になる設計)には到達すらしない。**この文は118文字であり、
たとえ第二段階へ到達していたとしても、無条件にASR_UNCERTAINとして扱われ、
「くく」→「くか」の違いを検知することはできなかった。**

### B-6. 評価: **MATERIAL_VALIDATION_GAP**

以下の理由により`MATERIAL_VALIDATION_GAP`と判定する。

1. 日本語segmentの30.2%が31文字以上(long segment)であり、これらは構造的に
   意味検証を一切受けられない
2. 残る69.8%(short segment)も、**無条件に**意味検証を受けるわけではなく、
   同じ弱い第一段階を先に通過してしまえば意味検証は発動しない
3. B-5の実証テストで、1文字誤り・語の置換・数字の誤り・否定の反転・フレーズ
   脱落・フレーズ追加という代表的な6カテゴリすべてが、現在の検証ロジックを
   すり抜けることを、実際の本番コードのロジックへ実データを通して確認した
4. 実際に本番で発生した「やめにくくする」→「やめにくかする」という実例も、
   この構造的な弱点がそのまま顕在化したものであることを確認した

### 改善案(次タスク向け、今回は実装しない)

1. **long segmentでも全文ASR比較する**: 英語Validator(`classify_asr_match`)
   と同様の正規化+内容語比較を日本語にも導入する(形態素解析や読み変換を
   活用した日本語版Protected Check)
2. **文/句単位で内部chunk比較する**: 長いComment/Previewを句読点で分割し、
   各chunkごとにASR結果と突き合わせる(現在のprefix依存を解消)
3. **semantic-critical tokenを別検証する**: 数字・固有名詞・否定語など、
   意味を大きく左右するトークンだけを抽出して個別に一致確認する(英語
   Validatorの数字/否定Protected Checkと同じ発想を日本語へ移植)
4. **日本語TTS segment自体を細分化する**: A2のpreview/comment_1〜4を、現在の
   1文相当より細かい単位で生成・検証する(ただし音声の自然さ・生成コストとの
   トレードオフを要検討)

## 受入条件チェックリスト

1. **正式A2/B1 target word count**: 全体は「上限なし」(CURRENT_SPEC明記)。
   Point単位は目標30-60語/許容25-70語(診断的目安、非gating)。コード内の
   280-420(全体soft range)はSSOT未文書化の参考値(A-1参照)
2. **No.4〜6 B版6本のtarget適合表**: A-2参照、全6本PASS
3. **下限割れ有無**: なし。逆に上限超過が2件(No.6 B1/A2 Point Two、A-3参照)
4. **日本語segment定義**: B1=Key Phrase gloss 5件のみ、A2=japanese_title/preview/comment_1-4/Key Phrase gloss 11件(B-1)
5. **英語segment定義**: Full Story Part1/2・Point One/Two・In One Line・Key Phrase English Component(B-2)
6. **英日segment方式の差**: B-2表参照。日本語は2段階(prefix+length→条件付き意味検証)、英語は正規化+6分類Validator
7. **No.1〜6日本語segment長分布**: B-3参照(≤30: 67件、31-60: 5件、61-90: 5件、91-120: 10件、>120: 9件、計96件)
8. **≤30文字segment比率**: 69.8%
9. **>30文字segment比率**: 30.2%
10. **short segment Validator内容**: 第一段階(prefix+length)+条件付き第二段階(数字/否定/完全一致/読み一致、`validate_japanese_short_segment_match`)
11. **long segment Validator内容**: 第一段階(prefix+length)のみ。第二段階は構造的に無条件ASR_UNCERTAIN(no-op)
12. **「やめにくくする」誤発音をなぜ見逃したか**: B-5参照。文頭2文字と全体文字数のみの判定のため、文中の1文字誤りは検知対象外
13. **long segmentで検知可能/不可能な誤りの実証**: B-5参照。6カテゴリ全て見逃す(誤ってPASS)ことを実データで実証
14. **Japanese ASRの実効性判定**: `MATERIAL_VALIDATION_GAP`
15. **改善が必要な場合の選択肢**: 上記「改善案」4点(全文ASR比較/chunk比較/semantic-critical token検証/segment細分化)
16. **Productionコード変更有無**: なし(Audit専用、非対象事項の通り)
17. **新規API Cost**: $0(新規TTS/ASR/LLM呼び出しは0件。既存ログ再解析と検証ロジックへの直接シミュレーションのみ)
18. **残存Open Item**: 本報告のPart B結果を踏まえた日本語Validator改善の要否判断(ユーザー判断待ち、OPEN-59として記録)、No.6 Point Two上限超過2件の扱い(OPEN-59に含める)

## 非対象

Evidence Compression方針の撤回、No.7生成、日本語Validatorの大規模変更、
Japanese segment分割変更、TTS model変更、ASR provider変更、いずれも実施していない。

Audit完了につきSTOPする。
