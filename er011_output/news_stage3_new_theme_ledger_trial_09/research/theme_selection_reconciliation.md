# Step 0 テーマ選定(Reconciliation) — FAMILY-A-NEWS-STAGE3-NEW-THEME-LEDGER-TRIAL-09

候補検索(`candidate_search.json`、実Web検索、gpt-5.6-luna、web_search tool)で得られた3件を、
CURRENT_SPEC.md「Editorial Type Routing(2軸判定)」節(軸A=最近性依存/軸B=独立Signal集約依存)と
`FAMILY-A-DAILY-NEWS-FOCUS-LAYER-DESIGN-TRIAL-01_REPORT.md` §2.1 Major/Daily Gate 6項目で評価する。

## 候補一覧と判定

| # | 候補 | 分野 | 軸A(最近性依存) | 軸B(独立Signal集約依存) | 2軸判定 | Gate 6項目 | 採否 |
|---|---|---|---|---|---|---|---|
| 1 | ケイティ・テイラー、現役最後の試合に勝利し引退(2026-09-05、The Guardian) | sports | Yes(この特定の試合・引退表明という日付に依存) | No(単一の試合結果、複数時点の集約ではない) | `MAJOR_DAILY` | 1(PASS、単一試合)・2(PASS)・3(PASS見込み、対戦経緯・記録で2つの異なる意味づけは可能)・4(該当性低)・5(PASS)・6(PASS) | **却下**(理由: Hanshinと構造的に同型[単一試合の勝敗・引退という結果とスコア的記録が中心]で、数値密度もHanshinに近いMEDIUM。題材依存切り分けの目的[Hanshinと構造的に異なる題材で検証する]に合わない) |
| 2 | 体内でCAR-T細胞を作らせる遺伝子治療で多発性硬化症の症状改善を報告(2026-09-03、Nature) | science | Yes(この特定の小規模試験発表という日付・発表に依存) | No(単一の小規模試験。CURRENT_SPEC.md「Health(単一起点研究発表がある場合の扱い)」節の既存判定[単一研究プロジェクト=1つの起点、Trend Synthesis側が要求する複数独立研究の横断集約とは異なる]をそのまま適用できる) | `MAJOR_DAILY` | 1(PASS、「2026年9月3日に、体内でCAR-T細胞を作らせる遺伝子治療の小規模試験で症状改善が報告された」の1文で要点保持)・2(PASS、該当なし)・3(要Ledger確認、Researcher実行後に確定)・4(PASS見込み、"small trial"であることを不確実性として明示しやすい)・5(PASS、新規)・6(PASS、単一小規模試験であり複数独立研究の横断集約ではない) | **採用**(理由: 下記「選定理由」参照) |
| 3 | アテネ動物園で希少なスマトラトラの幼獣が初の健康診断(2026-09-08、Yahoo/AP) | society | Yes(この特定の健康診断という日付に依存) | No(単一の出来事) | `MAJOR_DAILY`(形式上) | 1(PASS、形式的には1文化可能)・**3(懸念、"通常の健康診断"という出来事は「結果を決定づけたmechanism」や「見出し以外の貢献の広がり」を支える確認済み事実が乏しく、Point One/Twoの異なる意味づけをLedgerだけで支えられない可能性が高い) | **却下**(理由: Gate項目3[Ledger充足確認]がリスク。題材の実質的な厚みが薄く、切り分け目的の測定を汚染しかねない[Focus+hintの効果ではなく題材の薄さによるNG率変動と混同するリスク]) |

## 選定理由(候補2: 体内CAR-T免疫療法による多発性硬化症症状改善報告)

1. **Hanshinとの構造的な違いを明確に狙った選定**: Hanshinは単一試合のスコアライン(8-1、
   イニングごとの加点、本塁打数等)という**数値密度の高い**題材だった。候補2は臨床試験の
   「結果を決定づけたmechanism(体内で直接CAR-T細胞を誘導する新方式)」と「限界・不確実性
   (小規模試験、長期安全性は未確認)」という、**語彙がFull Story(mechanism解説)とPoint
   (limitation/unconfirmed)へ自然に分かれやすい**題材である。これはNews Focus Module/Point
   Role hintが想定するPoint役割候補(mechanism、beyond-the-headline factor、limitation/
   unconfirmed)と直接対応するため、「Focus+hintが機能するかどうか」をHanshinより見えやすい
   条件で検証できる。
2. **既存DECIDED判定との整合**: CURRENT_SPEC.md「通常News(Major/Daily News)Reference仕様」節
   「Health(単一起点研究発表がある場合の扱い)」で、単一研究発表はMAJOR_DAILYとして扱う運用方針
   が既にA-UDR-10でDECIDED済み(設計Trial段階)。候補2はこの既存判定パターンへ直接当てはまり、
   新しい判定基準を作らずに済む。
3. **候補1(ボクシング引退)の却下理由**: 単一試合の勝敗という点でHanshinと同型の構造であり、
   「題材依存かどうか」を切り分ける目的には適さない(Hanshinと同じ失敗モードが出ても、それが
   スポーツ題材一般の問題なのか仕組みの問題なのか区別できない)。
4. **候補3(動物園の健康診断)の却下理由**: 数値密度は最も低いが、Ledger充足確認(Gate項目3)の
   リスクが高い。定例的な健康診断というだけでは、記事のPoint One/Twoに要求される「本文とは異なる
   具体的な意味づけ」を支えるだけの確認済みFactが乏しく、Ledgerが薄い場合、NG率の変動が
   「Focus+hintの効果」なのか「そもそも題材が痩せている」のかを区別できなくなる。

## 手動Mode判定結果(run summary記録機構、Trend Gate記録と同型)

- **management_id**: `FAMILY-A-NEWS-STAGE3-NEW-THEME-LEDGER-TRIAL-09`
- **mode_supply_path**: 手動Mode判定+手動Ledger供給(Trend Synthesis/既存News Trialと同じ機構)
- **editorial_mode_determination**: `MAJOR_DAILY`(2軸判定: 軸A=Yes、軸B=No)
- **判定者**: 本Trial実施者(Sonnet委任、Fable指示に基づく手動判定。自動判定は未実装のため実施していない)
- **判定日**: 2026-09-09
