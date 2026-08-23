# ER-006-GATE-EVIDENCE-REVIEW-CASCADE-ON-MATH-ADOPT-01 完了報告

## 1. 何が問題だったか

前タスクで3つの改善(取材チェックの較正、数式表記チェックの実装、
固有名詞ASR再検証の修正)を行ったが、いずれも「検証済みだが未確定」の
状態でした。具体的には: ①取材チェックがNo.1・No.2を「取材不足」と
判定した理由が本当に正しいか未検証、②数式表記チェックの改善が正式な
仕様として採用されていない、③固有名詞のASR再検証の仕組み(Cascade)は
実装済みなのに、本番設定でOFFのままだった。

## 2. 何を変更したか・分かったこと

### Part A: 取材チェック(Research Coverage Gate)のNo.1/No.2判定を検証

既存のResearch・Ledger・完成記事・事実確認(Fact Check)・Ledger整合性
チェックだけを使い、新規取材はせずに検証しました。

**結論: No.1・No.2の判定は、実質的にすべて誤検知(FALSE_POSITIVE)でした。**

Gateが指摘した8件の不足項目のうち、TRUE_COVERAGE_GAP(本当の不足)は
0件、FALSE_POSITIVE(誤検知)7件、BORDERLINE(境界的)1件でした。
両Topicとも、完成記事は事実確認PASS、Ledger整合性チェックもA2版は
両方とも「完全準拠」であり、Writerは実際にはLedgerの範囲内で適切に
慎重な記事を書けていました。

原因を2つ特定しました。
- **No.1固有の原因**: Gateへ渡していたタイトルが、企画段階の仮タイトル
  ("Why Are More Cities Rethinking Public Benches?")であり、Writerが
  実際に採用した最終タイトル("A Place to Pause—or a Signal to Move
  On?")とは別物でした。仮タイトルの「より多くの都市が」という頻度の
  主張は、実際の記事には一切登場しません。実際の最終タイトルでGateを
  再実行すると、同じLedgerのまま`COVERAGE_PASS`へ反転することを確認
  しました(新規取材なし)。
- **No.2でも判明したより一般的な原因**: 実際の最終タイトルで再実行して
  も`MORE_RESEARCH_REQUIRED`のままでした。Gateは「なぜ〜なのか」という
  因果的な問いを自動的に想定し、行動実験のようなEvidenceを要求し続ける
  一方、実際に採用された記事は「概念の説明+制度の歴史」に留め、因果の
  断定を一切していません。これは番組の正当な編集パターンであり、前回の
  較正(類推適用の許容)では、この「因果を問う体裁でも、記事は概念的な
  説明に留まる」パターンへの対応が不足していたことが分かりました。

### Part B: 数式Validatorの正式採用

前タスクで実装した数式表記の正規化(等号・不等号・掛け算記号・上付き
指数・単数複数の揺れ吸収)を、Production標準Validatorの正式仕様として
確定しました。安全条件(`10⁻¹⁶≠10⁻⁶`等)を含む55件のfixtureが全てPASS
することを再確認しました。

### Part C: ASR Cascade(固有名詞の音声再検証)を本番で有効化

`FEATURE_FLAG_SECONDARY_ASR_ENABLED`を`False`→`True`へ変更しました。
本番の呼び出し箇所6箇所は全て、呼び出す瞬間にこの設定値を読みに行く
実装だったため、この1箇所の変更だけで全箇所へ反映されます。

実際のNo.6音声(2件)で、TTS再生成なしにASRだけを4回再検証して人間
レビューへ回る、という設計通りの動きを確認しました。また、Ottoni・
Boavida型の模擬テスト(9件)・数値/内容誤りfixture(55件)・実際の
No.4/No.5/No.6の音声ログの再解析のいずれでも、「本当に内容が違う音声」
を誤って合格にしてしまうケースは1件も見つかりませんでした。プロジェクト
全体の回帰テストも1753件中1753件成功のままです。

## 3. 何が改善されるか

既存ログを使ったcounterfactual計算(新規TTS生成なし)によると、
No.4・No.5・No.6だけで、Cascade有効化により合計$0.358883(¥57.42)の
TTS費用が本来不要だったことを確認しました(追加のASR費用は無視できる
水準)。No.1(Boavida)でも1回分のTTS再生成が回避できたはずですが、
その時期はコスト計測の対象外だったため金額化はできていません。No.2・
No.3の既存ログには、この種のミスマッチ自体が発生していませんでした。

## 4. リスクや注意点

- 取材チェック(Gate)は**引き続きProduction未配線**です。今回の
  検証で、Gateへ渡すタイトルの選び方と、因果的なタイトルでも概念的な
  記事は許容すべきという較正がまだ不足していることが分かったため、
  ユーザーの指示なしに配線はしていません。
- Cascade有効化は、既存6箇所の呼び出しコードの実装パターンを確認した
  上で行いましたが、今後新しい呼び出し箇所を追加する際は、同じ「呼び
  出し時にモジュール変数を参照する」パターンを維持する必要があります。

## 5. 受入条件チェックリスト(20項目)

1. **No.1 Gate判定妥当性**: FALSE_POSITIVE(pre-Writer仮タイトルと実際の
   最終タイトルの不一致が主因、実タイトルで再実行するとCOVERAGE_PASS)
2. **No.2 Gate判定妥当性**: FALSE_POSITIVE(実タイトルで再実行してもGateは
   因果Evidenceを要求し続けるが、実際の記事は概念説明に留め因果断定を
   していない。Fact Check PASS、A2はLedger完全準拠)
3. **分類**: TRUE_COVERAGE_GAP 0件、FALSE_POSITIVE 7件、BORDERLINE 1件
   (計8 missing_items、詳細はOPEN-54参照)
4. **Gate最終判定**: `PROMISING_BUT_MORE_DATA_NEEDED`(No.4/5/6の必須flip
   は成功したが、No.1/2で新たな較正課題[タイトル入力契約・因果的タイトル
   への過剰反応]が見つかったため)
5. **Gate Production導入推奨可否**: 現時点では非推奨。追加較正
   (①Gateへ渡すtitleの入力契約見直し、②因果的タイトルでも概念説明で
   十分なパターンの明示的許容)を経てから再判断を推奨。**Production配線は
   実施していない**
6. **数式Validator正式採用内容**: `=`/`<`/`>`/`×`/数字間`x`/Unicode上付き
   指数/ASCIIキャレット指数/Markdown italic/規則的単数複数吸収を
   CURRENT_SPEC.mdへ正式反映(詳細は同ファイルValidator項)
7. **55 fixture結果**: 全55件PASS(既存32件+新規23件、再確認済み)
8. **CURRENT_SPEC反映内容**: Validator項(55件・数式表記詳細を追記)、
   ASR-first Retry Policy項(`FEATURE_FLAG_SECONDARY_ASR_ENABLED=True`へ
   更新)
9. **DECISION_LOG反映内容**: 新規エントリ`ER-006-GATE-EVIDENCE-REVIEW-
   CASCADE-ON-MATH-ADOPT-01`(Decision 1〜3、Validator正式採用・
   Cascade ON化・Gate Production配線見送りの3点)
10. **OPEN_ITEMS更新内容**: OPEN-48を`RESOLVED(feature flag ON化)`へ
    更新、新規OPEN-54(Gate較正の残課題)・OPEN-55(Cost counterfactual
    記録)を追加
11. **Cascade Production ONの実装箇所**: `er006_secondary_asr_01.py`
    118行目の`FEATURE_FLAG_SECONDARY_ASR_ENABLED`定数
12. **feature flag変更内容**: `False`→`True`(1箇所、全6 call siteへ
    自動反映)
13. **SweenyでASR-only Cascadeになる証拠**: `verify_cascade_production_on.py`
    実行結果(B1/A2ともcascade_invoked=True、Primary#1→#2→Secondary#1→#2
    の4-step)
14. **SweenyでTTS retry 0になる証拠**: 同スクリプトで新規TTS呼び出し0回、
    既存音声のみでの再検証を確認
15. **Ottoni/Boavida等の回帰結果**: `er006_secondary_asr_01_test.py`
    9件全PASS、実Boavida/Vogel/Mimoun-Gruenログの再解析でも選択的に
    正しく動作(内容差を伴うケースはCascade対象外のまま)
16. **true content mismatch誤PASS 0件の証拠**: Validator 55 fixture・
    Secondary ASR 9 fixture・実音声ログ再解析のいずれでも誤PASS 0件
17. **Cascade ONによる追加ASR Cost**: 1 segmentあたり約$0.000022
    (無視できる水準)
18. **回避可能TTS Cost**: No.4/5/6で合計$0.358883(¥57.42、実測ログ
    ベース)。No.1 Boavidaは1回分回避(金額データなし)
19. **Net Saving**: 実質$0.358883(¥57.42)相当(追加ASR費用は無視できる
    水準のため実質全額が純節約)
20. **regression test結果**: プロジェクト全体1753/1753件PASS、Validator
    55/55件PASS、Secondary ASR 9/9件PASS
21. **新規API Cost**: 本タスクの検証作業自体で発生したAPI呼び出しは、
    Gate再実行(No.1/No.2 real-title確認、2件)・Cascade検証用ASR呼び出し
    (No.6実音声、Primary/Secondary計8回程度)のみ。いずれも数十円未満の
    軽微な支出
22. **残存Open Item**: OPEN-54(Gate較正: title入力契約の見直し・因果的
    タイトルへの較正追加)、OPEN-48残る3点(Azure時刻誤認識・Cascade
    実効性の継続監視・固有名詞認識精度の独立測定)

## 6. 非対象・STOP条件

タスク仕様の非対象事項(No.7以降の記事生成、Gate Production配線、
第三ASR、固有名詞whitelist等)はいずれも実施していません。STOP条件
(Cascade誤PASS、Production回帰、Validator negative fixture FAIL、
No.1/2評価不能)はいずれも発生しませんでした。
