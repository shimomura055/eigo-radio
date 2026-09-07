# OPEN-112-THEME2-AUDIO-REVIEW-FIX-02 — サブタスクB(B1 Preview短縮Trial)+ サブタスクC(Numeric Precision整合確認)

**管理ID: OPEN-112-THEME2-AUDIO-REVIEW-FIX-02**
**種別: Trial(B)+ 調査・read-only確認(C)。Production変更なし、Git操作なし。**
**作成日: 2026-09-07**
**対象記事: Theme 2 B1/A2(OPEN-112 Trend Synthesis、Trial-12 `b1b_run01`/`a2_run01` article、`full_audio_trial_13`の実際のProduction Support生成物)**

---

## A. 前提として特定した現行Production経路(read-only)

- B1 PreviewのProduction Prompt本体は `er003_v1_b1_scaffold_01_generate.py::PREVIEW_ROLE`
  に定義されており、`er003_v1_n3_01_scaffold_generate.py`(実際にTheme2で使われている
  Scaffold生成モジュール)が`b1s.PREVIEW_ROLE`をそのままimportして使っている
  (コード確認: `preview_prompt_role = b1s.PREVIEW_ROLE.format(...)`)。
- `er011_output/open112_trend_theme2_b_full_audio_trial_13/b1b/audit/b1_support_generation.json`
  の実際のPrompt文字列が`b1s.PREVIEW_ROLE`と完全一致することを確認し、これが
  Theme2 B1 Previewの実際の生成元であることを実証した。
- 比較対象のA2日本語Previewは`er003_v1_iran01_a2_generate.py::PREVIEW_ROLE`
  (同じく`er003_v1_n3_01_scaffold_generate.py`から`a2gen.PREVIEW_ROLE`として再利用)。

現行B1 PREVIEW_ROLE原文(Production、無変更):
```
あなたはPodcastの冒頭を担当するナビゲーターです。これからリスナーは、
このエピソードのニュース本文(Preview・Key Phrasesに続いてMain Story・Points・
In One Line)を聞きます。エピソードの一番最初に流すPreviewを書いてください。

役割: このニュースの
- theme(何についての話か)
- problem(何が問題・論点か)
- value(なぜ聞く価値があるか)
- question(聞き終える頃に何が分かるようになるか)
を短く提示し、リスナーの関心を引きます。

以下は避けてください:
- 答えを先に言う
- 重要な数字を先出しする
- 結論を先に言う
- turning point(展開の転換点)を先に明かす
- 後で流れるComment 1・Comment 2と内容が重複する

Comment 1・Comment 2は以下の通りです。これらと重複する内容にしないでください。
【Comment 1】{comment_1}
【Comment 2】{comment_2}
```
（分量に関する指示は無し。A2側にのみ「2文程度、80〜110字程度」の目安段落がある。）

---

## B. B1 Preview短縮Trial

### B-1. Trial Prompt(差分)

Production `PREVIEW_ROLE`本体は無変更のまま、以下の1段落だけをTrial専用コピー
(`er011_theme2_b1_preview_shorten_trial_01.py::TRIAL_PREVIEW_ROLE`)へ追加した
(A2 PREVIEW_ROLEの「分量」段落と同じ思想、文言はB1向けに書き換え・重複を避けた):

```
【重要・分量(Trial)】現在のB1 Previewの目安は約1/2〜1/3にしてください
(目安2〜3文)。theme/problem/value/questionの4要素を律儀にすべて別の文で
書き並べる必要はありません。「何を聞く回か」が短く伝わることを優先し、
要素を尽くそうとして冗長にならないよう注意してください。あくまで目安であり、
絶対的なhard limitではありません(記事の内容により多少の増減は許容します)。
```

先出し禁止・Comment1/2重複禁止の既存原則は削除・変更していない。

### B-2. 実行内容とRuntime Evidence

- 呼び出したProduction関数: `er003_v1_b1_scaffold_01_generate.py::run_support_text()`
  (無変更、Trial Promptを渡しただけ)。
- 記事本文: `er011_output/open112_trend_theme2_b_a2_b1_text_trial_12/b1b_run01/article.md`
  (Production `full_audio_trial_13`のPreview生成Promptに埋め込まれた本文と
  diffで完全一致を確認済み)。
- Comment 1/2: 既存Production生成物(`full_audio_trial_13/b1b/b1_support_texts.json`)
  をそのまま再利用(再生成していない、比較の土台を固定)。
- 実API呼び出し1回(model=`gpt-5.6-luna`、reasoning=high、Production既定のまま)。
- 出力先: `er011_output/theme2_b1_preview_shorten_trial_01/`
  (`trial_preview_attempts.json`/`trial_prompt_full.txt`/
  `current_production_prompt_full.txt`/`comparison.json`)。

### B-3. Before/After全文と定量比較

**現行Production(before)**:
> This episode looks at how young people in Japan think about travel, including
> freedom, personal interests, and time. But the label "young Japanese travelers"
> may hide important differences between groups. Listen to see what the surveys
> show about these different preferences and what "slow travel" means in this
> story. By the end, you will have a clearer view of what young travelers may
> want from a trip.

統計: 405字・67語・4文。

**Trial(after)**:
> This episode looks at what younger travelers in Japan want from a trip,
> especially how much control they have over their time and activities. We'll
> ask what these changing preferences mean for the future of travel in Japan.

統計: 223字・38語・2文。

**比率**: 語数比0.567、字数比0.551(目安1/2〜1/3のうち、1/2にやや届かず
上振れ。1回生成のためcherry-pickはしていない、目安はhard gateではないため
許容範囲内と判断できるが、より短くしたい場合は「1/3」寄りの表現をPromptへ
追加する等の再Trialが考えられる)。

### B-4. 評価

| 観点 | 結果 |
|---|---|
| 語数・文数の圧縮 | 67語→38語(-43%)、4文→2文。ユーザー希望の「1/2〜1/3」にほぼ収まる(上限寄り) |
| 答え・数字・結論・turning pointの先出し禁止 | 維持。数字・具体的結論の先出しなし |
| Comment1/2との重複回避 | 維持。Comment1(想像する旅行日数と実際の計画日数の差)・Comment2(想像は伸びても実際の計画は短い、変化しているのは態度か行動か)とは異なる文言・情報 |
| 「何を聞く回か」が伝わるか | 伝わる(「日本の若い旅行者が何を求めているか、特に時間の使い方の裁量」という主題は明確) |
| 本編との重複度 | 「control over their time and activities」という表現は、本編Point One見出し「Slow travel is also about control」の角度に近い。ただしA2側の既存Production Preview(承認済み)も「自分らしく過ごしたいという思い」という同系統の主題提示をしており、単独の新しい懸念ではなく、A2の前例と整合する範囲の主題提示と評価できる |
| 情報の取捨選択 | 現行Previewが持っていた「"young Japanese travelers"というラベルが実は違うグループを覆い隠しているかもしれない」というPoint Two寄りのフックは、圧縮の結果Trialでは落ちている(2つのフックのうち1つに絞られた、圧縮の自然なトレードオフ) |
| B1リスナー向けの自然さ | 平易で自然な英語、文法・語彙とも既存Previewと遜色ない |

### B-5. 分類

**`VALIDATED`(Trial as designed)** — Prompt変更のみでProduction関数・既存の
先出し禁止原則を壊さずに、目安の1/2〜1/3にほぼ収まる圧縮を実際に達成できる
ことを1回の実API生成で実証した。ただし字数比0.55は「1/2〜1/3」の1/2端に
やや近い側であり、「1/3」寄りをより確実に狙うなら追加Trial(表現をさらに
強めた分量指示、または複数生成での安定性確認)が必要。**Production採用の
可否・最終文言はユーザー判断**(最大Status VALIDATED、`APPROVED_FOR_PRODUCTION`
はユーザーのみ)。

### B-6. Production採用時に必要な変更一覧(実装はしていない)

1. `er003_v1_b1_scaffold_01_generate.py::PREVIEW_ROLE`へ分量段落を追加
   (本Trialの文言をそのまま、またはユーザー調整後の文言で)。
2. 影響範囲確認: `PREVIEW_ROLE`は`er003_v1_n3_01_scaffold_generate.py`からも
   再利用されるため、この1箇所の変更で新規記事生成すべてに反映される
   (過去に生成済みの完成音声・article/support_textsは遡及的に変わらない、
   既存方針どおり新規生成のみ対象)。
3. 既存回帰確認(B1 Preview関連のunit testがあれば実行、本Trialでは既存
   Production testの改変は行っていない)。
4. 採用後、目安が実運用で1/2〜1/3レンジに安定して収まるか複数記事で
   monitoring(hard gateにしない前提を維持)。

### B-7. Cost

実API呼び出し1回(`gpt-5.6-luna`、reasoning=high)。`run_support_text()`は
usageトークン数を記録しない実装のため、正確な円換算コストは本Reportでは
提示しない(Production既存の同種呼び出し[Comment/Preview単体生成]と同程度、
入力コンテキストは記事全文[約2.3千字]+Comment1/2、出力は短文のみのため、
既存の同種呼び出し実績[数円〜十数円程度]と同オーダーと推定)。

---

## C. Numeric Precision / Rounding整合確認(read-only)

### C-1. 参照した既存仕様(原文引用・箇所)

1. **CURRENT_SPEC.md 110行目**(A2/B1/B2比較表、「数字・金額・日付・%」行):
   > 原則1文1数字。年齢範囲・スコア・時間帯・日付(月+日+年)は1つの意味単位
   > として例外扱い | CEFR別の簡略化ルールなし(音声制作段階のMFA/ASR対応のみ)

2. **CURRENT_SPEC.md 222行目**(「Spoken-first Number Treatment」、`DECIDED`、
   ER-003-A2-B1-N3-01 §14、A2/B1双方へ適用・3ジャンルで運用確認済み):
   > Verified Fact Ledgerは常にexact factを保持する。spoken narrative側は、
   > 精度自体に意味がない数字を、丸め(round)・概数化(approximate)・
   > 方向化(directionalize)してListening easeを優先してよい。分類は2軸:
   > Importance(ANCHOR/SUPPORTING/DISPENSABLE)、Exactness(EXACT_REQUIRED/
   > APPROXIMATE_OK/DIRECTION_ONLY)。…精度そのものが意味を持つ数字は
   > EXACT_REQUIREDのまま維持する

3. **CURRENT_SPEC.md 352行目**(Evidence Compression Editor追加ルール:
   Pattern A + Listener-Friendly Numeric Precision、`DECIDED`/`PRODUCTION_WIRED`、
   ER-011-NO18-EVIDENCE-COMPRESSION-A-PRODUCTION-WIRING-AND-FINAL-CANDIDATE-
   AUDIO-21R):
   > 残す価値があると判断した数値について、意味(比較方向・story上の大きさ・
   > 閾値・解釈・値同士の区別)が変わらない場合のみ、より単純な概数を優先
   > してよい。小数の機械的削除は禁止、丸めが意味のある差・閾値・小規模測定・
   > 解釈・区別を損なう場合は小数を保持する。最重要制約: 丸めは異なるFact・
   > 指標・group・time point・survey質問・実験結果の統合を許可しない
   （実際のPrompt本文には"This is a judgment rule, not a mechanical one."
   と明記されている、`er003_v1_n3_01_evidence_compression_editor.py`経由で
   A2/B2いずれのWriter出力にも**同一文言**が適用される、コード実行時の
   実際のPrompt全文で確認済み）。

4. **`er003_v1_n3_01_articles_generate.py` COMMON_BLOCK_TEMPLATE
   「Spoken-first原則(数字の扱い)」節**(A2/B2いずれのWriter呼び出しにも
   共通で使われる、全テーマ共通のテンプレート):
   > C. Exactnessが不要な場合は丸めてよい。ただし丸めによって意味が
   > 変わらないこと … G. exactness_requirement: EXACT_REQUIREDと印のある
   > 数値(スコア・日付・記録・研究結果の主要数値・安全性に関わる閾値等)は、
   > 精度自体が意味を持つため、正確な値を保持する

5. **Ledger Deviation Check**: `er011_output/…/b1b_run01/ledger_deviation.json`
   ・`a2_run01/ledger_deviation.json`とも`"overall_status": "LEDGER_COMPLIANT"`
   (deviations 0件)。丸め版(A2)・精密版(B1)いずれもLedger整合と判定されている。

### C-2. 実データでの確認(a)〜(f)

事前に、この記事のVerified Fact Ledger原本
(`er011_output/open112_trend_theme2_b_a2_b1_text_trial_12/research/
theme2_verified_fact_ledger_CORRECTED_trial12.txt`)を確認した。重要な発見:
Ledger自体が、Fact源によって**元から異なる精度**で記録されている。
- F-202(日本交通公社調査): 「ひとり旅25.2%・趣味を深める旅行24.3%…
  グルメ旅行52.4%・有名観光地巡り44.7%」— 調査報告そのものが小数第1位
  まで開示
- F-203(観光庁調査): 「約90%…うち約80%」— **調査報告そのものが
  「約」付きの概数**(Ledger原文コメントに「観光庁公式プレスリリースPDF」
  を根拠に約90%/約80%とLedgerへ明記されている、Editorが丸めたものではない)

`evidence_compression_editor_raw.json`(A2/B1とも実行済み、実Prompt・実出力
を直接確認)で以下を実証:
- B1(B2)側: 編集前ドラフトに「solo travel at 25.2%, hobby-focused travel
  at 24.3%」→ Editorは25.2%を保持し24.3%は"similar pattern"へ圧縮
  (Pattern A適用)。44.7%はそのまま保持(比較対象のgourmet travel 52.4%は
  このドラフトに元々含まれていなかった)。
- A2側: 編集前ドラフトに「solo travel was 25.2%, hobby-focused travel was
  24.3%」「44.7%」「52.4%」→ Editorはいずれも整数へ丸め(about 25%/about
  24%/about 45%/about 52%)。

(a) **B1で25.2%/44.7%を残すのは現行仕様どおりか** — Yes。上記3の
Numeric Precision ruleは「丸めが意味のある差・区別を損なう場合は小数を
保持する」という**判断ルール**(mechanicalではない)であり、Editorが
「保持する」と判断すること自体は仕様の範囲内の挙動。仕様違反ではない。

(b) **A2で整数丸めは現行仕様どおりか** — Yes。同じ規則が「精度が
意味に影響しない場合は簡潔な概数を優先してよい」とも明記しており、
Editorが「丸める」と判断することも同様に仕様の範囲内。

(c) **レベル差として意図されたものか(仕様上の根拠)** — **明確な意図は
確認できなかった(仕様の穴)**。CURRENT_SPEC 110行目が明示するとおり、
記事本文の数字取り扱いには「CEFR別の簡略化ルールなし」であり、Numeric
Precision rule・COMMON_BLOCK_TEMPLATEのSpoken-first数字原則もA2/B2で
**完全に同一の文言**が使われている(コード上、レベル分岐は存在しない)。
実際に観測された差は、(i)A2とB2が独立した別のWriter生成物であること、
(ii)Editor自体が"judgment rule, not mechanical"な非決定的LLM判断である
こと、の組み合わせによる**偶発的な結果**であり、「B1は精密・A2は概数」
という方針がSSOTのどこかに明文で決定されているわけではない。実務上は
「A2は認知負荷を下げるため数字を単純化する方が自然」という考え方に
合致する結果ではあるが、これは今回の調査で見えた**現状追認的な観察**
であり、正式な採用決定ではない。

(d) **同一記事内の丸め規則に不整合がないか(B1内で25.2%と"about 90%"
混在)** — **不整合ではない**。上記Ledger確認のとおり、"about 90%"/
"about 80%"はEditorによる丸めではなく、**Ledgerに記録された時点で
既に近似値として報告されている別のFact(観光庁調査)** である。異なる
一次資料が異なるネイティブ精度で報告している以上、それぞれの精度を
そのまま保持することはむしろFact fidelity(Ledger整合)の観点で正しい。
25.2%(JTBF調査)と約90%(観光庁調査)は「同じ記事内で丸め方針が
ぶれている」のではなく「別々のFactが別々の精度で正しく記録されている」。

(e) **TTS自然さとの兼ね合い(小数点読み上げ)** — 既存のASR/canonical
text正規化コード(`er006_preprod_hardening_01_validation.py`)が
`\d+\s+point\s+\d+`(例: "twenty-five point two")のパターンを明示的に
正規化対象として扱っており、小数読み上げは既存パイプラインで想定内・
handling済みの表現である(未知の技術的困難ではない)。ただし「技術的に
発話・照合できる」ことと「聴取負荷が低い」ことは別軸であり、"twenty-five
point two percent"は"about twenty-five percent"より音節数・認知負荷が
高いのは事実。この聴取負荷トレードオフの判断こそが、Numeric Precision
ruleが"judgment rule"としてLLMに委ねている部分であり、既存仕様の設計
思想と矛盾しない。

(f) **Ledger/Fact Safety上の許容** — 両レベルとも`ledger_deviation.json`
で`LEDGER_COMPLIANT`(0件)を実データで確認。Ledger Deviation Checkerは
精密表現(25.2%)・概数表現(about 25%)のいずれも許容しており、丸めの
有無自体をFact違反として検出する設計にはなっていない(意図通り)。

### C-3. 結論

**(a)(b)(d)(f)は既存仕様どおりで問題なし**。B1の精密表記・A2の概数化
双方とも、既存のNumeric Precision judgment ruleとLedger fidelityの
両方に照らして正当な結果であり、新ルールを作る必要はない。

**(c)は仕様の穴(未決)として提示する**: 「レベル間で数字の粒度が異なる
結果になり得る」こと自体は、SSOTのどこにも明文で承認されていない
(CEFR別ルールは意図的に「なし」とされている)。これは今回たまたま
「A2=概数・B1=精密」という直感的に自然な組み合わせになったが、Editorの
非決定性ゆえに**将来別の記事では逆転する可能性がある**(例: A2が精密な
小数を残し、B1が丸めてしまう回が理論上あり得る)。`USER_DECISION_REQUIRED`
として以下の選択肢を提示する(いずれも未実装、SSOT変更なし):

- **選択肢1(現状維持)**: 新ルールを作らず、Editorの判断に委ねたまま
  monitoring対象とする(今回のように結果整合していれば良しとする)。
- **選択肢2(レベル別ガイダンス明文化)**: Numeric Precision ruleへ
  「A2は一般に概数化を優先し、B1はより高い精度を許容してよい」という
  レベル別の目安(hard ruleにはしない)を追記し、非決定性による逆転リスクを
  減らす。
- **選択肢3(記事内一貫性ルール)**: レベル間の一致は求めず、代わりに
  「同一Fact源内での丸め一貫性」(今回のようにLedgerの元精度に忠実である
  こと)だけを明文化する最小限のルールを追加する。

いずれもProductionコード・Prompt変更は今回実装していない
(`APPROVED_FOR_PRODUCTION`はユーザーのみ判断可能)。

---

## D. SSOT登録案(未実装、ユーザー判断待ち)

- `OPEN_ITEMS.md`へ新規行として「OPEN-11X: Theme2 Numeric Precisionレベル間
  一貫性(CEFR別ルール不在によるEditor非決定性)」を追加する案(上記選択肢
  1〜3を選択肢として記載)。
- B1 Preview短縮Trialの結果(`VALIDATED`、字数比0.55)を、ユーザーが
  Production採用と判断した場合、DECISION_LOG.mdへ
  `OPEN-112-THEME2-B1-PREVIEW-SHORTEN-XX`のようなID(タスク完了後に
  Fable/ユーザーが正式ID採番)で記録する案。

---

## E. 使用ファイル一覧

- `er011_theme2_b1_preview_shorten_trial_01.py`(新規、Trial script)
- `er011_output/theme2_b1_preview_shorten_trial_01/`(新規、Trial出力一式)
- 変更なし(read-onlyでimportのみ): `er003_v1_b1_scaffold_01_generate.py`、
  `er003_v1_iran01_a2_generate.py`、`er003_v1_n3_01_scaffold_generate.py`、
  `er003_v1_n3_01_articles_generate.py`、`er003_v1_n3_01_evidence_compression_editor.py`
- git操作: 未実施(コミット・push・ACTIVE_TASK.md/RESULT_PACKET.md編集なし、
  本タスク指示どおり)
