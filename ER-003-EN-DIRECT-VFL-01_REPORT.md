# ER-003-EN-DIRECT-VFL-01 実行報告(Verified Fact Ledger方式 A02再実証)

**管理ID: ER-003-EN-DIRECT-VFL-01**
**実施日: 2026-08-12**
**ステータス: `PROTOTYPE / EXPERIMENT`(A02限定の実験系。Production仕様は変更していない。採否はユーザー判断待ち)**

## A. Executive Summary

VFL方式を**2回とも独立に完走できた**。結果は明確に良好。

- **Run-1 fact status**: `PASS`(矛盾なし、未確認の重要主張なし)
- **Run-2 fact status**: `PASS`(矛盾なし、未確認の重要主張なし)
- **ERROR-1(autoplay/feedのタイミング誤り)再発**: **なし**。両Runとも
  「午前0時〜6時に限定されない、常時の制度項目である」ことを明示的に記述
- **ERROR-2(309 vs 81の混同)再発**: **なし**。両Runとも309=全体・81=夜間
  制限群という区別を明示的に記述(Run-2は「It was not 309 participants
  testing a night curfew」と、旧B版の誤りを先回りして否定するような
  一文まで含む)
- Ledger逸脱チェックも両Runとも `LEDGER_COMPLIANT`(逸脱0件)
- 技術的再試行は**両Runとも0回**

## B. Verified Fact Ledger

Researcherが19件のFactを収集し(Web検索8回)、独立Verificationで
**18件VERIFIED・1件AMBIGUOUS・0件REJECTED**と判定された。

| fact_id | 内容 | 判定 |
|---|---|---|
| POL-02 | 16・17歳、午前0時〜6時のデフォルト夜間制限(通知含む) | VERIFIED |
| POL-03 | 通知ミュートは夜間制限時間帯(6時間)に適用 | VERIFIED |
| POL-04 | autoplay・personalised feedsはデフォルトでオフ | VERIFIED |
| **POL-05** | **autoplay・personalised feedsの制限は「常時」適用され、午前0時〜6時のcurfewには限定されない** | **VERIFIED**(ERROR-1の直接的な解消根拠。Written Ministerial Statementに「at all times」の明記を確認) |
| POL-06 | 保護設定は自動オンだが本人変更可能 | VERIFIED |
| **PILOT-01** | **309は夜間curfew群の人数ではなく、Wave 1全体(4群合計)のインタビュー数** | **VERIFIED**(ERROR-2の直接的な解消根拠) |
| PILOT-02 | 対照群1+介入群3の計4群、希望に基づき配分 | VERIFIED |
| **PILOT-03** | **群別内訳: 15分制限群76、夜間curfew群81、完全削除群74、対照群78(合計309)** | **VERIFIED**(前回監査で「一次資料上未検証」としていた「81」を、今回Researcher+独立Verificationで確定) |
| PILOT-04 | 夜間curfew群81世帯の介入内容(端末設定でブロック) | **AMBIGUOUS**(「81世帯すべてが所定どおり遵守した」と読める場合は不正確。「割り当てられた介入内容」と明示する場合のみ支持) |
| PILOT-07 | 夜間curfew群の遵守: 完全遵守53・軽微な変更23・非遵守5 | VERIFIED |
| OUT-01〜05 | 運用しやすさ・睡眠改善・継続意向・日中利用・適応行動(それぞれcausal_strength=OBSERVED_REPORTEDで因果を強めない指定) | すべてVERIFIED |

## C. Ledger Verification

- **VERIFIED**: 18件
- **AMBIGUOUS**: 1件(PILOT-04。「82世帯全員が所定どおり遵守した」という
  誤読を避けるための限定。writerへは「[AMBIGUOUS - 断定禁止]」のタグ付きで
  渡し、実際に両Runとも遵守状況は「assigned」「reported adherence」等の
  慎重な表現で処理した)
- **REJECTED**: 0件

## D. Run-1

- **word count**: 409語(soft target 355〜481語の範囲内)
- **fact status**: `PASS`(独立fact checker、Web検索6回、矛盾・未確認主張ともに0件)
- **Ledger deviation**: `LEDGER_COMPLIANT`(逸脱0件)
- **9観点QA**: F・G節および比較Artifact参照。Fact accuracy・Meaning
  precisionはOriginal Bから明確に改善。Editorial engagement・
  Master-style transferはOriginal Bと同水準を維持("Midnight arrives. A
  phone lights up."という開幕の短文リズムはOriginal Bの"It is 11:59
  p.m."と同種の演出技法だが、今回は具体的Fact claimと接続していない)

## E. Run-2

- **word count**: 393語(soft target範囲内)
- **fact status**: `PASS`(独立fact checker、Web検索10回、矛盾・未確認主張ともに0件)
- **Ledger deviation**: `LEDGER_COMPLIANT`(逸脱0件)
- **9観点QA**: Run-1と同様にFact accuracy良好。Point Oneで
  「Nighttime quiet is only one layer」という、curfewとautoplay/feed
  制限を明確に別項目として提示する切り口を採用しており、これはLedgerの
  POL-05が時間的scopeを明示していたことで初めて可能になった、Original
  Bにはなかった新しい編集上の強みと言える。

## F. ERROR再発確認

| | ERROR-1(autoplay/feedのタイミング) | ERROR-2(309 vs 81) |
|---|---|---|
| Original B | 発生(午前0時起点として誤統合) | 発生(309を夜間群人数と誤記) |
| Run-1 | **再発なし**(「throughout the day—not only between midnight and 6 a.m.」と明記) | **再発なし**(309=全体、81=夜間curfew群と明記) |
| Run-2 | **再発なし**(「not merely between midnight and 6 a.m....regardless of the hour」と明記) | **再発なし**(「It was not 309 participants testing a night curfew」と明示的に否定した上で81を提示) |

2件とも、2回の独立試行で一貫して再発しなかった。

## G. Style Preservation

Original Bと比較して、以下を確認した。

- **Hook**: Run-1はOriginal Bとほぼ同種の開幕演出(短い断定文の連打)を
  維持。Run-2はより直接的な書き出しだが、フックとして機能する
  見出し引用形式は維持されている
- **Rhythm**: 両Runとも短いセンテンスを積み重ねる構成を維持しており、
  「Fact accuracyのために無味乾燥な文章にする」という禁止事項には
  抵触していないと判断する
- **Editorial engagement**: 両Runとも「聞き手が続きを聞きたくなる」
  構成(結論を急がず、Point二つで異なる角度を示し、一言まとめで締める)
  を維持
- **Master-style transfer**: 「概要→2ポイント(それぞれ別の切り口)→
  一言まとめ」という阪神マスターの構成は両Runとも明確に維持されている

**結論**: 今回の1セット(2回試行)の範囲では、Fact accuracyの改善と
文体上の長所の維持は**両立できた**。

## H. 比較Artifact

Original B・VFL Run-1・VFL Run-2の全文、fact QA結果、9観点QA表をまとめた
比較ページを作成した。本文は各版とも先頭から全文を読める配置とし、QA結果・
勝敗に関する記述は本文の後にのみ置いている。

**URL**: https://claude.ai/code/artifact/b8382b8c-40dd-451d-b66c-0d1723d20d12

リポジトリ内の原本: `er003_output/en_direct_vfl_01/A02/comparison.html`

## I. Production非変更確認

- **CURRENT_SPEC.md**: 無変更
- **R4 Production prompt**(`er002_ja_article_generation.py`・
  `er002_ja_web_research_r3.py`等): 無変更。今回のVFLパイプラインは
  新規の独立スクリプト`er003_v1_en_direct_vfl_01_generate.py`から、
  これらのモジュールおよび前回実験の`er003_v1_en_direct_ab_01_generate.py`
  の関数を読み取り専用でimportして使用した
- **ER-003-P1B**: 無変更
- **A方式・B方式の正式採用状態**: 変更なし(いずれも正式採用されていない)
- **B1/A2 Production生成・TTS/audio**: 実施していない
- **OPEN-35**: 変更・CLOSEしていない。A01/A02/ADD03の音声更新は今回も
  実行していない(夜間まとめ処理のため意図的保留のまま)

## J. 次のDecision(3択、ユーザー判断待ち)

1. ADD03へVFL方式を展開してstress test
2. A02でVFL方式を調整して再テストする
3. 現行A方式(日本語経由の2段階方式)へ戻る

今回の1セットの実証結果(2/2回でERROR-1・ERROR-2とも再発なし、9観点QAで
文体上の長所も維持)は、選択肢1(他記事でのstress test)を支持する材料と
なり得るが、あくまで**A02・2回試行のみ**の結果であることに留意されたい
(次回実証時にも複数回試行を推奨する、前回report ER-003-EN-DIRECT-FACT-01
I節と同じ理由による)。最終判断はユーザーに委ねる。

## 対象ファイル・新規Artifact一覧

| ファイル | 内容 |
|---|---|
| `er003_v1_en_direct_vfl_01_generate.py`(新規) | VFLパイプライン全体(Researcher→Verification→Writer×2→Fact Checker×2→Ledger逸脱チェック×2)の独立実験スクリプト。Production関数を読み取り専用でimportするのみ |
| `er003_output/en_direct_vfl_01/A02/fact_ledger_draft.json`(新規) | Researcherが生成したFact Ledger下書き(19件) |
| `er003_output/en_direct_vfl_01/A02/fact_ledger_verification.json`(新規) | 独立Verification結果(18 VERIFIED/1 AMBIGUOUS/0 REJECTED) |
| `er003_output/en_direct_vfl_01/A02/verified_fact_ledger.txt`(新規) | writerへ渡した最終Verified Fact Ledgerのテキスト形式 |
| `er003_output/en_direct_vfl_01/A02/verified_fact_ledger_structured.json`(新規) | 同上の構造化データ |
| `er003_output/en_direct_vfl_01/A02/run1_article.md` / `run2_article.md`(新規) | Run-1・Run-2の生成本文 |
| `er003_output/en_direct_vfl_01/A02/run1_diagnostics.json` / `run2_diagnostics.json`(新規) | 構造・語数診断 |
| `er003_output/en_direct_vfl_01/A02/run1_fact_qa.json` / `run2_fact_qa.json`(新規) | 独立fact checker結果 |
| `er003_output/en_direct_vfl_01/A02/run1_ledger_deviation.json` / `run2_ledger_deviation.json`(新規) | Ledger逸脱チェック結果 |
| `er003_output/en_direct_vfl_01/A02/comparison.html`(新規) | 比較Artifact原本 |
| `er003_output/en_direct_vfl_01/A02/audit/`(新規) | 各API呼び出しのprompt全文・応答詳細等の監査証跡 |

## 受入条件30項目

| # | 条件 | 結果 |
|---|---|---|
| 1 | A02限定の実験である | PASS |
| 2 | Verified Fact Ledger工程をwriter前段に追加している | PASS(B節) |
| 3 | Fact Ledgerが構造化されている | PASS(fact_id等15項目のスキーマ) |
| 4 | 数字のscopeを保持できる構造になっている | PASS(numeric_value/numeric_scope) |
| 5 | 制度の時間・対象範囲を保持できる構造になっている | PASS(date_or_period/scope/conditions) |
| 6 | Fact Ledgerを独立verificationしている | PASS(C節、別API呼び出し) |
| 7 | VERIFIED/AMBIGUOUS/REJECTEDを区別している | PASS(C節) |
| 8 | writerへ原則VERIFIEDのみ渡している | PASS(AMBIGUOUSは断定禁止タグ付きで渡し、REJECTEDは0件) |
| 9 | writerは日本語阪神master全文を使用している | PASS |
| 10 | writerは英語を直接生成している | PASS |
| 11 | writerは原則Web検索を使用していない | PASS(tools引数を省略、技術的障害なし) |
| 12 | writerはLedger外Fact追加禁止を指示されている | PASS(writer prompt制約節) |
| 13 | 2回独立生成している | PASS(Run-1/Run-2) |
| 14 | 2回とも同一Ledger・同一条件を使用している | PASS |
| 15 | Run-1/Run-2それぞれ独立Fact Checkしている | PASS(D・E節) |
| 16 | ERROR-1型を個別確認している | PASS(F節) |
| 17 | ERROR-2型を個別確認している | PASS(F節) |
| 18 | Ledger逸脱チェックを行っている | PASS(両Run LEDGER_COMPLIANT) |
| 19 | 9観点QAを行っている | PASS(比較Artifact) |
| 20 | 前回B/Run-1/Run-2比較Artifactを作成している | PASS(H節) |
| 21 | Production仕様を変更していない | PASS(I節) |
| 22 | B1/A2/TTS/audioを生成していない | PASS(I節) |
| 23 | OPEN-35を変更・CLOSEしていない | PASS(I節) |
| 24 | APIモデル・reasoning・Web search回数を記録している | PASS(H節下部、各jsonファイル) |
| 25 | Fact Ledgerの全Sourceを記録している | PASS(fact_ledger_draft.json、各factにsource_title/source_url) |
| 26 | Fact Ledger verification結果を保存している | PASS(fact_ledger_verification.json) |
| 27 | Writerの再試行有無を記録している | PASS(両Run 0回、diagnostics.json) |
| 28 | Fact checkerの再試行有無を記録している | PASS(両Run 1 attempt、fact_qa.json) |
| 29 | 新規・変更ファイル一覧を報告している | PASS(上表) |
| 30 | Git操作を行った場合はcommit/push状態を報告している | 本報告の末尾を参照 |
