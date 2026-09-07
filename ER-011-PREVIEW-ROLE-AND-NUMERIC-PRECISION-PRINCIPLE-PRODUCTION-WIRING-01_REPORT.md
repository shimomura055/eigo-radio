# ER-011-PREVIEW-ROLE-AND-NUMERIC-PRECISION-PRINCIPLE-PRODUCTION-WIRING-01 実行報告

## 1. 結論

ユーザーが2026-09-07に`APPROVED_FOR_PRODUCTION`と正式決定した2件(B1 Preview新方針、
Eigo Radio共通Numeric Precision原則)を、Production正式初回経路へ`PRODUCTION_WIRED`
まで配線した。新規・既存単体テストとも全PASS、プロジェクト全体回帰(`run_project_
regression.py`)は変更前後で同一の3件既知failure(無関係)のみ、実API呼び出しによる
Runtime evidence(Theme 2 B1/A2、TTSなし・テキスト工程のみ)を取得済み。

## 2. 何が問題だったか(採用の背景)

- B1のPreview(番組冒頭の導入ナレーション)には分量に関する指示が一切無く、
  4文・67語・405字相当の長いPreviewになっていた(A2側には既に「2文程度、
  80〜110字目安」という分量指示があり、B1だけ抜けていた)。
- 数値の丸め(概数化)ルールは既に存在した(Evidence Compression Editorの
  Listener-Friendly Numeric Precision、Writer共通Promptの項目C)が、「概数が
  既定であること」「精度保持は例外であること」という優先順位が明文で強調
  されておらず、CEFRレベル間で偶然結果が割れて見える(B1は小数を残しやすい、
  A2は整数化しやすい)ことがある実データが以前の調査で確認されていた。

## 3. 何を変更したか

### 3-1. B1 Preview分量原則

`er003_v1_b1_scaffold_01_generate.py::PREVIEW_ROLE`(B1 Previewの実際の生成元、
`er003_v1_n3_01_scaffold_generate.py`が`b1s.PREVIEW_ROLE`としてそのまま再利用する
唯一の経路)へ、以下の1段落を追加した。

```
【重要・分量】Previewは2〜3文程度の短い導入にしてください。要点を先出しし
すぎず、この回で何を聞くのかが自然に伝わる内容を優先してください(記事の
内容により多少の増減は許容します)。
```

旧Preview比の相対指定(「現行の1/2〜1/3」等)・hard word-count gate・「必ず2文」
のような固定文数は含めていない(soft guidance)。既存の「答えを先に言わない」
「重要な数字を先出ししない」「結論を先に言わない」「turning pointを先に明かさない」
「Comment 1・2と重複しない」という既存原則は無変更。A2側`er003_v1_iran01_a2_
generate.py::PREVIEW_ROLE`は別ファイル・別定数のため無変更(影響なし)。

### 3-2. Numeric Precision共通原則(A2/B1/B2共通)

既存のEvidence Compression Editor Numeric Precisionルール(`LISTENER_FRIENDLY_
NUMERIC_PRECISION_BLOCK`、ER-011-NO18-EVIDENCE-COMPRESSION-A-PRODUCTION-WIRING-
AND-FINAL-CANDIDATE-AUDIO-21R由来)の文言はそのまま維持し、これを補強する新規
ブロック`NUMERIC_PRECISION_LEVEL_INDEPENDENT_DEFAULT_BLOCK`を
`er003_v1_n3_01_evidence_compression_editor.py`へ追加した(既存ブロックの直後に
挿入、既存ブロック自体は書き換えない。既存の回帰テストが既存ブロックの
verbatim一致・順序を確認しているため、既存文言は不可侵として扱った)。

```
原則: 聞き取りやすさを優先し、意味を損なわない範囲では概数を基本とする。小数点
以下を保持するのは、その精度自体が記事の意味・比較・判断に必要な場合に限る。
通常は次のように概数化することが既定である: 25.2% → about 25%、44.7% → about
45%、89.6% → about 90%。

小数点以下を保持してよい例: 閾値の前後が論点になっている場合(例えば49.5%と
50.5%のように、僅差自体が意味を持つ場合)、年次変化・比較差を精密に扱う必要が
ある場合、小数を落とすと記事の意味・結論が変わってしまう場合。

This default applies equally regardless of CEFR level (A2/B1/B2). There is no
level-specific numeric precision rule...
```

同じ原則の1文を、Writer共通Prompt(`er003_v1_n3_01_articles_generate.py::
COMMON_BLOCK_TEMPLATE`「Spoken-first原則(数字の扱い)」C項)にも追加した
(A2/B2いずれのWriter初回呼び出しにも共通で使われる箇所、レベル分岐は追加して
いない)。

## 4. 何が改善されるか(Runtime evidence)

出力先: `er011_output/preview_role_numeric_precision_wiring_01/`
(`preview_evidence.json`/`numeric_precision_evidence.json`/
`ledger_deviation_after_{a2,b1}.json`)。すべてProduction正式関数を無変更のまま
呼び出す実API呼び出し(TTSなし)。

### Preview(Theme 2 B1、実記事)

| | 旧Preview(以前の実測記録) | 新Preview(本タスクで実際に生成) |
|---|---|---|
| 文数 | 4文 | 2文 |
| 語数 | 67語 | 46語 |
| 字数 | 405字 | 253字 |

新Preview全文: "This episode looks at what younger people in Japan want from
travel, including how much freedom they want during a trip. We will ask whether
young travelers can be treated as one group, and what the surveys can really
tell us about the future of travel."

先出し禁止・Comment1/2非重複は維持(Comment1/2は既存Production生成物を再利用し
比較の土台を固定)。A2 Previewは同一記事で1件再生成し、2文・85字(従来の
80〜110字目安の範囲内)で従来どおりであることを確認した。

### Numeric Precision(Theme 2 B1/A2、Ledgerに25.2%/44.7%等の小数を含む実記事)

| Fact | Before(旧Editor、実際の過去Production出力) | After(新Editor、本タスクで実際に生成) |
|---|---|---|
| 男性ソロ旅行 | B1: 25.2%のまま保持 / A2: about 25% | B1: about 25% / A2: about 25% |
| 女性有名観光地 | B1: 44.7%のまま保持 / A2: about 45% | B1: about 45% / A2: about 45% |
| 男性趣味旅行 | B1: 24.3%→trend表現 / A2: about 24% | B1: about one quarter(trend表現) / A2: about 24% |
| Jalan一週間回答 | A2: 24.1%のまま未丸め | A2: about 24% |
| 観光庁「自由時間」約90%/約80% | 変更なし(Ledger原本が既に近似値) | 変更なし |

Ledger Deviation Checker(Production正式`hook_aware=True`)を編集後テキストへ
実行し、B1=`LEDGER_COMPLIANT`(0件)、A2=`LEDGER_COMPLIANT`(MINOR1件、
`changed_number: false`、丸めとは無関係な確信度ニュアンスの指摘)を確認した。
丸め自体がchanged_numberとして誤検知されないことを実データで確認できた。
精度保持側(既存ブロックが変更されていないことの確認)は新規API呼び出しを
せず、Trial-20の既存fixture(`article_pattern_b_precision_01.md`、99.71/108.95
が丸めず保持された実例)で確認した。

## 5. リスクや注意点

- B1 Preview 2文・46語は「2〜3文程度」の下限寄り(3文の実例は今回未取得、
  1回の生成のためcherry-pickではないが、記事により3文になる場合の再現性は
  monitoring対象)。
- Evidence Compression Editorは"judgment rule"(非決定的LLM判断)であるため、
  同じ原則でも記事ごとに丸め方の細部は変動しうる(既存仕様どおりの想定内)。
- OPEN_ITEMS.mdには本件専用の既存行が無く(過去Trial Reportは登録案を提示した
  のみで実際には未登録)、該当行が無いため変更していない。
- git add/commit/pushは本タスクでは実施していない(Fableが後続タスクで統合)。
  変更ファイル一覧は最終メッセージ参照。

## 6. 回帰・テスト

- `er011_no18_evidence_compression_a_precision_21r_test_01.py`: 9件PASS
  (既存ブロックのverbatim一致・順序を維持)。
- `er010_n9_production_integration_09_test_01.py`: 33件PASS。
- `er008_n8_point_prompt_strengthen_24_test_01.py`: 8件PASS。
- `run_project_regression.py`: collected=2110、passed=2107、failed=3。
  git stash(変更3ファイルのみ)で変更前後を比較し、失敗3件
  (`er003_test_bad.FixtureTests.test_case_0`、`er003_test_p2j_investigate`の
  count reconciliation系2件)が変更前後で完全に同一(既知の無関係failure)
  であることを実証した。
