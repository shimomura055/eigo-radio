# 委任_03 全文保存(FACTLOCK-WRITER-REDESIGN-TRIAL-01、2026-10-08、T-0)

## 管理ID

FACTLOCK-WRITER-REDESIGN-TRIAL-01(委任_03: 面白さ低下の原因診断+Fact Lock v2 prompt設計。**¥0・API課金なし・git操作なし**)。並行タスクあり: (1)同管理IDの委任_02b agent(盲検採点・集計中。書込先`er052_output/factlock_writer_trial_01/eval/`・`RESULT.md`・`MANIFEST.json`・`docs/pm/RESULT_PACKET_FACTLOCK.md`)、(2)`PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01`委任_03 agent(Production配線・git commit中)。本委任は両者のファイルに書き込まない。

## 性質/到達上限Status/禁止事項

- 性質: 診断+設計(Trial準備)。到達上限Status: `V2_DESIGN_READY_FOR_OPUS`。
- 隔離規則(必須): 書込は `er052_output/factlock_writer_trial_01/v2_design/` 配下、`docs/pm/RESULT_PACKET_FACTLOCK_V2.md`(新規)、`docs/pm/delegation_log/2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_03.md`(+`_check.json`)のみ。harness(`er052_factlock_writer_trial_01_run.py`)は**編集しない**(v2のprompt文言は設計書内に書き、実装は委任_04)。SSOT・`RESULT_PACKET.md`・`RESULT_PACKET_FACTLOCK.md`・`ACTIVE_TASK.md`編集禁止。git add/commit/push禁止。有料API禁止。Production code編集禁止。
- 費用: ¥0。
- Opus独立技術レビューGate: 条件A(内容変更に伴う再レビュー)に該当。本委任はそのレビュー対象(v2設計書)を作る。
- 時間見込み: ≈60分(診断30分/v2設計25分/事前登録案5分)。並列不要。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は使わない(本委任ではgit操作禁止)。
F-1: 自タスクのtranscript退避は不要。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ**全文**保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`): 本委任はTTSを伴わない。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`): 本委任は課金なし。

## ユーザー指示(原文)

「指摘の通りエンターテイメント性については全くNGです。これでは話になりません。一つはR0>R1>R2のPromptを変更して改善できないか、もう1つはそもそもWriterへのPromptを現状の品質重視をキープしながら、工夫できないか、変更して検討してください」(2026-10-08)。前提: 事実固定(台帳から外れない)は維持。面白さは現行prompt版(6×現行)と同等以上に戻すことが目標。

## KPI provenance欄

該当なし(本委任は測定なし。診断は既存artifactのreuse)。委任_04の指標provenanceは事前登録案に記載。

## Opus台帳更新

該当なし(レビューは本委任後にFableが起動)。

## 事前指定Read一覧

- `er052_output/factlock_writer_trial_01/eval/SUMMARY_FL.md` §3(面白さpairwise結果と理由抜粋)
- `er052_output/factlock_writer_trial_01/eval/FACTLOCK_CHECK_SUMMARY.md` 全文(照合指標。R0→R2で不整合が増幅していないこと等、v2で維持すべき挙動の基準)
- pairwise判定の生ログ(Glob `er052_output/factlock_writer_trial_01/eval/**/pairwise*` または `**/*pairwise*.json` で特定→全48判定の理由文を読む。読み取りのみ)
- 同brief対の本文比較(読み取りのみ、各R0/R1/R2): Fact Lock版 `er052_output/factlock_writer_trial_01/runs/<slug>/control/b<i>__factlock__r<j>/ja_writer/{original,revision1,revision2}.md` と 現行版 `er052_output/all6_writer_redesign_necessity_01/runs/<slug>/control/b<i>__all6__r<j>/ja_writer/{original,revision1,revision2}.md`。対象: meta b2 r1、hormuz b1 r2、hormuz b4 r1、space_weapons b3 r2(照合不整合の外れ値)、+一貫してFact Lockが勝った3対(pairwiseログから特定)。
- 現行promptの原文: `er019_family_x_ja_writer_o_r1_r2_01.py` Grep `R0_PROMPT|REVISION_INSTRUCTIONS|CONCRETENESS_CONTROL_AN3_BLOCK` →該当範囲Read(R0本文L40-120、R1/R2指示L70-80)
- Fact Lock v1のprompt追記ブロック: `er052_factlock_writer_trial_01_run.py` Grep `FACTLOCK_R0|FACTLOCK_REV|BLOCK` →該当範囲Read(逐語)
- `er052_output/factlock_writer_trial_01/DESIGN_01.md` §1〜§2(v1規則の正本)
- `docs/pm/opus_l2_review_factlock_writer_trial_01.md` 論点3(R1/R2規則と面白さに関するOpus指摘)

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep `比喩|作り込|窮屈|硬い|不自然|繰り返し|説明|流れ|具体|暮らし|問いかけ` in pairwise理由文 → 負け理由の分類表(カテゴリ×件数)を作る。
- Grep `ではありません|わけではありません|分かっていない|かもしれません|もし` in Fact Lock版R2本文24本 と 現行版R2本文24本 → 「否定・留保表現の密度」「推量形の密度」を記事あたり件数で比較(v1規則の副作用の定量化)。
- 比喩語の重なり: Fact Lock版/現行版R2で、同一記事内の比喩系語(舞台・幕・探偵・衣装・主役・配役・ドラマ・映画・ショー等。本文から抽出した上位語で定義)の異なり数と出現回数を比較。
- 追記位置: 新規 `er052_output/factlock_writer_trial_01/v2_design/DIAGNOSIS_01.md`、`DESIGN_02.md`、`PREREGISTRATION_V2.md`。

## 実行コマンド全文

cwd=`C:\Users\tensh\eigo-radio`、python=`.venv\Scripts\python.exe -X utf8`。

0. 委任文全文保存+検証: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_03.md --json-out docs\pm\delegation_log\2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_03.md_check.json`
1. 診断 `v2_design/DIAGNOSIS_01.md`: (a)pairwise負け理由の分類(件数)、(b)否定・留保・推量形の密度比較、(c)比喩重なりの比較、(d)同brief対の本文比較から「現行版にあってFact Lock版で失われた要素」(暮らしとのつながり・具体場面・語りの緩急・結びの余韻等)と「Fact Lock版で増えた要素」(否定の明示・タグ由来の文の硬さ・事実文の短文化等)を各3〜5例、(e)Fact Lockが勝った3対の共通点、(f)外れ値space_weapons b3 r2の不整合5文の中身(誤りか照合側の誤判定か)。(g)R0/R1/R2のどの段で面白さが落ちたかの推定(R0時点で既に硬いのか、R1/R2が伸ばせていないのか。段別の文体所見)。
2. v2設計 `v2_design/DESIGN_02.md`: 2案を**両方**設計し、それぞれR0/R1/R2の追記ブロック全文(日本語、逐語)を書く。共通の不変条件: 出典タグ・台帳外禁止・数値規則(c)・タグ照合・タグ除去・事実確認最優先条項(Opus M2)は維持。
   - **案A(方向1: Revise規則の調整)**: v1の5則は維持しつつ、(i)比喩は記事全体で1系統・重ねない、(ii)「暮らしとのつながり」は仮定(もし〜なら)・問いかけ・たとえ話の形で**必ず1箇所以上**入れる(禁止→推奨へ反転。断定しない条件は維持)、(iii)「〜ではありません」型の否定の明示はR0に留め、R1/R2では語り口に溶かす(残すのは誤解防止に必要な1箇所まで)、(iv)硬い転記調(「投稿された日」「清算されました」等)は話し言葉へ言い換えてよい(事実不変)、(v)結びは問いかけか余韻で終える。
   - **案B(方向2: Writer prompt構成の見直し・制約最小化)**: R1/R2の制約を**2則に圧縮**(「タグ付き文の事実は変えない・新しい事実文を足さない」のみ。削除自由・タグ継承・空白を埋めないは短い注記に)、代わりに現行のEntertainment Revision指示文(「友人に『これ、ちょっと面白くない?』と話すような読み物に」等)を**そのまま前面**に置き、面白さの手段リスト(具体的な生活場面の仮定/対比/一本の比喩/テンポの緩急/問いかけ/意外性のある導入)を提示。R0は事実の骨格に専念(短め・面白さを求めない)、R1=構成とフック、R2=ラジオで聞く語り口、と段ごとの役割を明記。
   - 各案について、Fact Lock v1の照合指標(不整合率≈7%で増幅なし、数値一致98%、残存タグ0)を**悪化させない**見込みの根拠と、面白さが戻る見込みの根拠(診断(d)(e)との対応)を書く。
   - §Opusレビュー論点(3〜5点): 案A/Bの規則が事実固定を緩めていないか、「推奨」へ反転した暮らしとのつながりが`asserts_unstated`の再発経路にならないか、比喩1系統の指定が逆に窮屈にならないか、R0を骨格化する案BでR0のJA Fact Checkが機能するか、比較設計。
3. 事前登録案 `v2_design/PREREGISTRATION_V2.md`(委任_04用): セル=6×案A、6×案B(各6 brief: meta b2/b3、hormuz b1/b4、space_weapons b1/b3 × 1反復=6本/案、計12本)。比較対象=6×現行(既存24本から同brief)と6×Fact Lock v1(既存)。指標=面白さpairwise(対6×現行、順序入替2回)、照合指標(不整合率・unsupported・数値一致・残存タグ)、JA FC must-fix/EN再生成/STOP、盲検rubric(重大/軽微)は同一パック再採点が可能なら実施。しきい値なし(数値化)。費用見積(12本×≈¥5+pairwise+照合≈¥80、上限¥100のT-3定型文)。開始条件=委任_02bの採点完了(`er052_output/factlock_writer_trial_01/RESULT.md`存在)。

## SSOT追記文

本委任ではSSOT編集なし。RESULT_PACKET_FACTLOCK_V2にDECISION_LOG追記文案(ユーザー指示: 面白さNG・2方向で再設計・事実固定維持)を記載。

## Git(明示add対象・コミットメッセージ・trailer)

**本委任ではgit操作禁止**。commit候補一覧(後続委任でFableが指示): `er052_output/factlock_writer_trial_01/v2_design/**`、`docs/pm/RESULT_PACKET_FACTLOCK_V2.md`、`docs/pm/delegation_log/2026-10-08_FACTLOCK-WRITER-REDESIGN-TRIAL-01_03.md`(+`_check.json`)。SSOT編集権なし。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_FACTLOCK_V2.md`を新規作成(ヘッダ: 管理ID・Status=V2_DESIGN_READY_FOR_OPUS・¥0・Production変更なし・git未操作)。本文: 1. 診断の要点(負け理由分類表、否定/推量/比喩密度の比較値、失われた要素・増えた要素の例、段別の推定)。2. 案A/案Bの要点と追記ブロック全文(逐語)。3. 各案の事実固定への影響見込み。4. Opusへの論点。5. 委任_04の開始条件・費用・時間。6. 問題・残作業(blockingか明示)。7. check_delegation_prompt結果1行、一覧外Readの理由。推奨は書かず事実のみ(どちらの案が有望かの判断はFable)。
