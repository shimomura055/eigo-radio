# FINAL_SUMMARY_01: ASR発音同等性の一般化(ASR-PHONETIC-EQUIVALENCE-GENERALIZATION-01 委任_01+_02)

非エンジニア向けのまとめ。Production無変更・Production採用なし・費用JPY0。数値の出典は括弧内。

## 1. 一般化した判定原則とRepo記録内容
- 原則(上位原則書 `docs/pm/design_principles/connected_speech_proper_noun_phonetic_equivalence_2026-10-13.md`): 「同じ音の並びには同じ判定を」「単語単体の読みと、つなげて話したときの読みを混同しない」「音が実質的に違うものは許容しない」「安全が確認できない方式は採用しない」。
- Repo記録: 設計草案 `DESIGN_DRAFT_01.md`→改訂版 `DESIGN_DRAFT_02.md`(Opus必須修正1〜4反映)、既存機構との対応表 `GAP_MAP_01.md`、読み取り専用の評価 `OFFLINE_EVAL_01.md`/`OFFLINE_EVAL_02.md`、試作 `er068_asr_phonetic_equivalence_generalization_01_offline.py`、テスト 32件。

## 2. 既存機構で対応できる範囲/できない範囲
- できる: 「語末のsが次のs始まりの語に溶ける」型(Pattern A)で、ASRが語幹の綴りを書く場合(例 `Melo said`)。
- できない: 同じ音を別の綴りで書く場合(`Mello`/`Mellow`)は、Pattern Aが受理しない=`Melo`はPASS・`Mello`はHRという不揃い(GAP_MAP_01)。
- 別機構(Equivalence Layer)は独立した2つ目のASRの裏付けが必須で、Melos型は2つ目も同じ綴りを書くため救済0件(CS_AUDIT)。

## 3. 推奨する判定ロジックと理由(Opus修正後)
- 方式M1: ASRが書いた綴りを「同じ音素列を持ち、承認済みの連結発音規則が期待する綴り」へ置き換え、既存の判定へそのまま流す(新しい受理基準は作らない)。
- Opus修正後の4点: (1)基準を綴りから**音素**へ(Moses/moss・Giles/guileなど音が違う語は受理しない)、(2)受理理由を「同音一致/Pattern A・B・C」に限定(類似度・数値同値の理由で通る道は塞ぐ)、(3)配置はPrimary判定の直後・Tier3の前、fallbackはSecondary同意またはHR、(4)末尾確認は「暫定の保守ゲート」。
- 推奨の優先順位(Opus): R1(原稿側の上流対策) > F1是正 > 修正版M1(優先度低)。採否はユーザー。

## 4. 正常音声の救済効果と誤PASSリスク(`OFFLINE_EVAL_02.md` §1)
| | V1'(テキストのみ) | V2'(+末尾暫定ゲート) |
|---|---|---|
| 正常音声の新規救済(実データ系n=1030、既存PASS 213) | 64件 | 41件 |
| 誤PASSの増分(欠陥363件、Pattern A比) | **28件**(末尾切詰を区別できない) | **0件**(合成データのみ) |
| Status | **REJECTED** | **USER_DECISION_REQUIRED** |
- 救済はすべて**Melosのみ**(Melos以外0件)かつ、Melosは辞書に無い名前のため「綴り基準へのfallback」経由。つまり実データ上の効果は小さい。
- 旧11件(類似度8・数値3)は受理理由の限定で不受理へ(`OFFLINE_EVAL_02.md` §3)。真値はHR待ちで不明(OPEN-335)。
- 受理面の広がり(54語プローブ): 旧17語/38綴り→新10語/21綴り。残るのは音素列が真に同一の別語(Jones<-Joan、Hayes<-Hey 等)。

## 5. Std減速後を含めた適用・検証範囲
- 判定は「文章と転写の関数」で、減速・経路を入力に持たない。減速前後で転写が同じ15対は判定15/15一致。全34対の群一致は26/34(不一致は減速でASRの転写が変わるため)。
- 適用: 全6経路が共有するcascadeに同時に効く設計(設計のみ。未実装)。対象はen-US narration/dialogue(Key Phrase・日本語は除外)。

## 6. 英文・音声分割Trialの結果(別ID: FAMILY-Z-ATTRIBUTION-CLIP-SPLIT-IMPROVEMENT-TRIAL-01、`er069_output/attribution_clip_split_trial_01/trial_conclusion_02.md`)
- 委任_01〜_02: 語末sの固有名詞の直後に「said/says/sighed」(s始まり)が来ると通過率が低い(Melos 10/36 vs replied/answered/asked 35/36)。**s+s融合が主因で`said`固有ではない**。最小語数ルール(R2)は効果未検出。
- R1(原稿ルール)案: 「語末歯擦音の固有名詞の直後に歯擦音始まりの語を置かない」。効果はMelos型の名前のみ(Brontes型は変わらない)。Status=USER_DECISION_REQUIRED(採否はユーザー、Production無変更)。費用 累計JPY53.76/100(commit a4c0af16/832ccbce)。

## 7. 費用・QCD・回帰結果
- 費用: 本件(ASR-PHONETIC)は委任_01・_02とも**JPY0**(有料API 0)。
- 回帰: er068 32件、er065 32件、er026 CS監査12件、Eq Layer wiring ALL PASS。Production state 9ファイルのsha256不変。
- 限界: 委任_01の回帰でtelemetry/attempt_historyに副作用が出た教訓(OPEN-328)から、本委任は共有ファイルへ書く回帰を実行していない。

## 8. 未解決事項とユーザー判断
- Opus後の4件: (1)優先順位 R1/F1/M1、(2)暫定の非対称(`Melo`=PASS/`Mello`=HR)の許容か末尾確認の全経路化(OPEN-341)、(3)F1是正(OPEN-340。既存成果物の判定がPASS→NGに変わり得る)、(4)辞書に無い名前(Melos)で綴り基準へ戻すことの許容+初出時1回HRの要否。
- R1の採否(A/B/C): A=Writer promptへの指針+決定論WARN lintをProduction化、B=追加確認(別名前タイプ・ledger未登録名のPLなし通過率)を先に、C=見送り。(選択肢の整理のみ。決定はユーザー。)
- 新規OPEN: OPEN-340(F1)、OPEN-341(末尾欠損の検出)、OPEN-342(F2)。

## 9. SSOT反映状況
`OPEN_ITEMS.md`(OPEN-339更新・OPEN-318/328追記・OPEN-340〜342新規)、`DECISION_LOG.md`(委任_02・分割Trial結果)、`docs/pm/OPUS_FINDINGS_LEDGER.md`、`docs/pm/USER_DECISION_REGISTER_01.md`、`docs/pm/REPORT_LEDGER.md`。`CURRENT_SPEC.md`/`PM_GOVERNANCE.md`は無編集。

## 10. APPROVED未配線・Dangling Reference
- 本委任での新規APPROVED未配線: 0(既存=OPEN-322/OPEN-320)。
- Dangling Reference: 新規参照は`er068_output/.../`(DESIGN_DRAFT_02/OFFLINE_EVAL_02/FINAL_SUMMARY_01/offline_eval_02.json/analysis_02.json/state_guard_02.json)・`er069_output/.../trial_conclusion_02.md`のみ。いずれも実在。既存SSOTの参照先変更なし。
