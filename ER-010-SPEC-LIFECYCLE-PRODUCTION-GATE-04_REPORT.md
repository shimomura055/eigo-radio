# ER-010-SPEC-LIFECYCLE-PRODUCTION-GATE-04 実行報告

## 1. 結論

品質・Prompt改善提案(Trialを経てProduction Writer Promptへ新原則を追加する類の提案)向けに、
`PROPOSED`→`VALIDATED`→`APPROVED_FOR_PRODUCTION`→`PRODUCTION_WIRED`の4段階Lifecycleと、
「Dangling Reference Check」(後段コードが、前段に存在しない仕様を参照していないかの必須確認)を、
既存のSSOT文書体系(新規文書を作らず)へ正式に組み込んだ。

今回発見・トレース済みのStorytelling First/No Jargonの孤立参照(Dangling Reference)は、
新規`OPEN-95`として正式に追跡可能な形で記録した。個別のWriter仕様(Meaning First/
Storytelling First/No Jargon)を新たに`APPROVED_FOR_PRODUCTION`または`PRODUCTION_WIRED`へ
昇格させる判断は今回行っていない。Production Writerの挙動・コードは一切変更していない。

## 2. Lifecycle定義の反映先

[PROJECT_INDEX.md](PROJECT_INDEX.md)の「状態ラベル(全文書共通)」節に隣接する新設
「仕様Lifecycle」節。理由: PROJECT_INDEXは既に「全文書共通の状態ラベル定義」を持つ
唯一の文書であり(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMSはいずれも個別仕様の記録先で、
プロセスルール自体の置き場所ではない)、新規governance文書を作るより既存構造への
自然な統合と判断した。

## 3. 変更したファイル

- [PROJECT_INDEX.md](PROJECT_INDEX.md)
- [DECISION_LOG.md](DECISION_LOG.md)
- [OPEN_ITEMS.md](OPEN_ITEMS.md)

Production Writer/retry/fallbackのコード(`er003_v1_n3_01_articles_generate.py`、
`er009_diagnostic_full_retry_modules_12.py`等)は一切変更していない。

## 4. 変更内容

- **PROJECT_INDEX.md**: 「状態ラベル(全文書共通)」節の直後に「仕様Lifecycle」節を新設。
  4段階の定義・変更権限・`PRODUCTION_WIRED`の12必須条件・Dangling Reference Checkの
  必須確認項目とFAIL例を記載。参照先マップにも1行追加。
- **DECISION_LOG.md**: 本ルール導入自体を1件のDecisionとして新規記録
  (`ER-010-N1-SPEC-LIFECYCLE-PRODUCTION-GATE-04`)。採用理由・比較した選択肢・
  既存の`PRODUCTION_WIRED`運用実績との関係・Storytelling First/No Jargonの扱いを明記。
- **OPEN_ITEMS.md**: Storytelling First/No JargonのDangling Reference事例を`OPEN-95`
  として新規追加(`USER_DECISION_REQUIRED`)。既存のOPEN-90/91(重複ID問題は別途未解消のまま、
  今回はrenumberしていない)とは独立したIDを採番した。

## 5. Dangling Reference Checkの正式ルール

[PROJECT_INDEX.md](PROJECT_INDEX.md)「仕様Lifecycle」節に記載。要約:
Production code/Promptが新しい仕様名・原則・ruleを参照する場合、(1)ユーザー承認済みか、
(2)Production初回経路に実装されているか、(3)CURRENT_SPECに正式仕様として存在するか、
(4)retry/fallback等の後段だけに孤立していないか、(5)DEV/Trial scriptの定義を暗黙参照
していないか、(6)前段・後段で同じ仕様名が同じ意味を持つか、を確認する。1つでも
満たさなければ`Dangling Reference / Production Wiring FAIL`と判定し、Claude Codeは
勝手に削除・実装・採用せず`USER_DECISION_REQUIRED`としてSTOP・OPEN_ITEMS記録する。

## 6. Production Wiring Checklist

`PRODUCTION_WIRED`と判定するための12条件(詳細はPROJECT_INDEX.md参照): ①ユーザー正式採用済み
②Production初回経路へ実装済み③後続経路と整合④DEV/Trial専用に留まっていない⑤実runtime発火確認
⑥必要な回帰/Validator/integration test PASS⑦実model_id/routing等のruntime evidence確認
⑧CURRENT_SPEC更新済み⑨DECISION_LOG更新済み⑩OPEN_ITEMS close/update済み⑪Git commit/push/merge反映確認
⑫ユーザー承認内容と実際のProduction behaviorが一致。1項目でも未確認なら`PRODUCTION_WIRED`としない。

## 7. 現在確認できた各仕様のStatus一覧(新Lifecycle語彙で整理)

| 仕様 | 現在Status | 根拠 |
|---|---|---|
| Meaning First | `VALIDATED` / `USER_DECISION_REQUIRED` | Trial-03で検証済み、OPEN-91に正式記録済み。Production Writer Promptへは未実装 |
| Storytelling First | 実質`VALIDATED`(ただし非公式Trialのみ、正式報告なし) / **Dangling Reference状態**でProduction配線に孤立参照が存在 | ER-010-03監査、OPEN-95新規記録 |
| No Jargon(学習者向け全文レベル) | Storytelling Firstと同一チェーンで同一状態 | 同上 |
| Diagnostic Full Retry機構自体 | `PRODUCTION_WIRED` | CURRENT_SPEC/DECISION_LOG既存記録(ER-009-N1-DIAGNOSTIC-FULL-RETRY-CLOSEOUT-14) |
| Point Overlap Writer full retry | `PRODUCTION_WIRED`(OPEN-88 CLOSE) | 既存記録 |
| 固有名詞発音判定基準の変更(ER-16) | `APPROVED_FOR_PRODUCTION`→同エントリ内で`PRODUCTION_WIRED`まで到達済み | CURRENT_SPEC 194行目、新Lifecycle語彙導入前からの実運用例 |

Key Phrase専門語回避(OPEN-90)は本タスクの直接対象外だが、同じく`USER_DECISION_REQUIRED`である
ことを確認済み(第9節参照)。

## 8. APPROVED_FOR_PRODUCTIONだが未配線の項目

該当なし。既存文書を横断確認したが、`APPROVED_FOR_PRODUCTION`のまま`PRODUCTION_WIRED`に
到達していない項目は見つからなかった。唯一の既存`APPROVED_FOR_PRODUCTION`実例(固有名詞発音
判定基準、CURRENT_SPEC 194行目)は同一記録内で`PRODUCTION_WIRED`まで完了済みだった。

## 9. USER_DECISION_REQUIRED項目

- OPEN-90(重複IDのうち、Key Phrase専門語回避の方): `USER_DECISION_REQUIRED`
- OPEN-91(重複IDのうち、Meaning First Production採用の方): `USER_DECISION_REQUIRED`
- OPEN-95(新規、本タスクで追加): Storytelling First/No JargonのDangling Reference: `USER_DECISION_REQUIRED`

いずれも今回ユーザー判断なしに自動でcloseしていない。

## 10. 明示defer済みOpen Item

- OPEN-72: 構造化comparator等による方向反転チェックの本格対策。`DEFERRED / AFTER USER VALIDATION`のまま維持
- OPEN-78: 重要な日付・数字のTTS入力前チェック。`DEFERRED`(不採用、Open Item化のみ)

いずれも本タスクでは変更していない。

## 11. 新たに発見したDangling Reference

今回のDangling Reference Check導入に伴い横断確認した範囲では、Storytelling First/No Jargon
以外の新規Dangling Referenceは発見しなかった。Diagnostic Full Retryモジュール
(`er009_diagnostic_full_retry_modules_12.py::DIAGNOSTIC_SECTION_TEMPLATE`)の他の記述
(Evidence Pack/VFL固定での全文再生成指示等)は、初回Production Writerに存在する原則の
言い換えであり、孤立参照ではないことを確認した。

## 12. Git変更内容

- 変更ファイル: `PROJECT_INDEX.md`(+62/-1)、`DECISION_LOG.md`(+16/-1)、`OPEN_ITEMS.md`(+3/-1)
  ※行数は末尾ドキュメントへの追記であり、既存記述は削除していない(改行コード警告のみ、内容欠落なし)
- コミット: 本レポートと合わせて1件のコミットとして作成予定(下記チャット報告で最終commit hashを報告)
- **Push**: 今回も実施しない。理由は第13節・チャット報告を参照

## 13. 残課題

- OPEN-90/OPEN-91のID重複問題(ER-010-03で発見済み)は今回も未解消(スコープ外、別タスクで対応)
- OPEN-95(Storytelling First/No Jargon Dangling Reference)自体の解消(採用するか、参照を削除するか)は
  ユーザー判断待ちのまま
- 本Lifecycle導入以前に`PRODUCTION_WIRED`と記録済みの全項目を、新12条件チェックリストで
  遡及的に再監査することは今回のスコープ外(今回はルール導入のみ)

---

- **Production behavior変更の有無**: なし。コード変更ゼロ、ドキュメントのみ変更
- **未処理USER_DECISION_REQUIREDの有無**: あり(OPEN-90、OPEN-91、OPEN-95の3件)
- **APPROVED_FOR_PRODUCTION未配線項目の有無**: なし

Status: GOVERNANCE WIRED / PRODUCTION BEHAVIOR UNCHANGED
