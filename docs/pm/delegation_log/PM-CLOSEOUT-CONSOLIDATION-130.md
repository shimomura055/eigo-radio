## 管理ID

PM-CLOSEOUT-CONSOLIDATION-130(4TYPE FOLLOWUP: Open Item 2件登録+コスト/Claude usage報告方式の恒久反映+Voices 2/3可変Writer APPROVED記録)
並行タスク衝突確認: 並行して News B1追加・Trend再生成・Discovery修正(いずれも`er014_output/`配下のみ、Git操作なし)が走る。本タスクはSSOT(`OPEN_ITEMS.md`/`DECISION_LOG.md`/`CURRENT_SPEC.md`/`docs/pm/PM_GOVERNANCE.md`/`docs/pm/PM_BRIEF.md`)+docs/pmのみを扱い、`er014_output/`はaddしない・触らない。Git操作は本タスクのみ。RESULT_PACKETは`docs/pm/RESULT_PACKET.md`へ上書き。`docs/pm/ACTIVE_TASK.md`は固定ヘッダ付きで上書き可。

## 性質/到達上限Status/禁止事項

- 性質: SSOT反映(¥0)。ユーザー正式決定4件を反映: (A)Open Item「A-Family Research / Verification / Final Web Fact Check cost optimization」=Priority MEDIUM/DEFERRED、(B)Open Item「No Jargon Writer compliance instability」=Priority LOW/DEFERRED、(C)コスト報告形式の恒久統一(「Production 1生成セット総原価」を主指標、50:50配賦禁止)、(D)Claude Code usage報告形式(Production pipeline API usageとClaude Code development/audit usageを別項目、cumulative_usageを「量産1記事のClaude token」と表現しない、週間利用枠のbefore/afterが取得可能な場合のみ「xx%→yy%(+z pp)」、取得不能なら「週間利用枠換算: 取得不能」、推定で%を作らない)。加えて(E)Voices Production Writerの2/3 Voices可変一般化=ユーザー正式決定`APPROVED_FOR_PRODUCTION`(未配線、Gate 3追跡対象)をOPEN_ITEMS/DECISION_LOGに記録。
- 禁止: コード変更/API呼び出し/`git add -A`・`.`・`stash`・`clean`・`amend`・`rebase`・`force push`/`er014_output/`のadd/ユーザー決定文言の意味変更/Production変更。
- STOP条件: push失敗3回→報告。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
---

## ユーザー指示(原文)

> 3. Trend: Research / Verification / Final Web Fact Checkの重複問題。今回はProduction構造を変更しない。最終Fact Checkerが上流Researchの取りこぼしを実際に検出したため、単純削除はしない。一方、Web検索を複数段階で繰り返しており、量産コスト上の最適化余地が大きい。Open Item化: Priority MEDIUM / DEFERRED として登録。「A-Family Research / Verification / Final Web Fact Check cost optimization」論点: 上流Research / Verificationの精度を高める/Final Web Fact Checkを全件検索ではなく必要時のみ検索する可能性/Fact Safetyを落とさずWeb Search重複を減らせるか/News / Trend / Discovery共通基盤への影響/単純なFact Checker削除は禁止/今回はProduction変更しない。ユーザー判断により、今回これ以上のTrial・最適化は行わない。
> 7. No Jargon再発問題はLOW Open Item。Priority LOW / DEFERRED として登録。「No Jargon Writer compliance instability」内容: No Jargonは既にPRODUCTION_WIRED/Discovery実記事で高度専門語がReader-facing本文へ流出/Writerが指示を守らなかった、または当該語を高度専門語と判定しなかった可能性/No Jargon専用Blocking Validatorは現在存在しない/現時点では新Checkerを追加しない/理由: APIコスト増、False Positive、副作用、新たな検証コストを避ける/今回は個別修正/今後のProduction記事で再発頻度を観測/再発が継続する場合のみPrompt/軽量対策を再検討。
> 8. コスト報告形式を恒久統一。ユーザー正式決定。今後のProduction記事生成コストは、「量産時1記事単価」だけを主見出しにしない。Familyごとにまず、Production 1生成セット総原価を主指標として報告する。標準表: | Family | Production 1生成セット | 総原価 | News | 共通Research/Ledger + A2+B1 | ¥xx | Trend | 共通Research/Ledger + A2+B1 | ¥xx | Discovery | 共通Research/Ledger + A2+B1 | ¥xx | Voices | そのFamilyの正式1生成セット | ¥xx |。その下に可能な範囲で、Research / Ledger、A2 Writer、B1 Writer、QA、retry、rewrite、その他を示す。重要: 共通Research / Ledger等を恣意的にA2/B1へ50:50配賦して「A2 ¥xx / B1 ¥yy」のような擬似的記事単価を作らない。正確に機械分離できる直接費だけを参考内訳として示す。TrendのようにA2+B1を1runで生成するものは、「Trend Production 1生成セット(A2+B1)= ¥xx」と表示する。この報告方式をPM報告標準・関連SSOTへ恒久反映すること。Statusはユーザー正式決定に基づく運用仕様として追跡し、必要なCURRENT_SPEC / PM_GOVERNANCE / DECISION_LOGへの反映を行う。
> 9. Claude Code usageの報告形式。記事生成API tokenとClaude Code作業量を混同しない。今後、「Production pipeline API usage」と「Claude Code development / audit usage」を別項目にする。Claude Codeのcumulative_usageにcache_readを含む巨大値を、「量産1記事で消費するClaude token」とは表現しない。weekly / 5-hour utilizationのbefore/afterが取得可能な場合のみ、「週間利用枠: xx% → yy%(+z percentage points)」を最も分かりやすい指標として報告。取得不能なら、「週間利用枠換算: 取得不能」と明記する。推定で%を作らない。
> 10. Voices 2/3可変Writer — 既存APPROVED項目。別途ユーザーが正式決定済み: Production Writerを2/3 Voices可変へ一般化する。Status: APPROVED_FOR_PRODUCTION。これは未配線のまま忘れないこと。

## 事前指定Read一覧

1. `docs/pm/PM_GOVERNANCE.md`: Grep `^## 15|15-5|5区分|^## 9|9-8` → 15節(コスト報告)と9節(ユーザー向け報告)の該当範囲のみRead(追記位置決定用)。
2. `OPEN_ITEMS.md`: Grep `^\| OPEN-14[5-9] ` → 直近行の書式確認(新規行の列構成を揃える)。Grep `^\| OPEN-83 |^\| OPEN-120 |^\| OPEN-135 ` → 各行の先頭200文字のみ(既存参照用、全文不要)。
3. `DECISION_LOG.md`: Grep `PM-CLOSEOUT-CONSOLIDATION-129` → 直近エントリ位置・索引書式。
4. `CURRENT_SPEC.md`: Grep `コスト報告|15-5|Production 1生成セット|量産単価` → 既存のコスト報告関連記述があれば該当範囲のみ(無ければ「該当なし」)。Grep `3V|3 Voices|可変|voice_cards` → Voices 3V未配線の記述(L657-659付近)のみRead。
5. `docs/pm/PM_BRIEF.md` L59-116(PM運用Gate・Closeout原則の段落、15節参照文の更新位置)とL133-157(ACTIVE_TASK固定ヘッダ書式)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- `OPEN_ITEMS.md`: Grep `^\| OPEN-148 ` → その直後に新規行OPEN-149(下記①)、OPEN-150(②)、OPEN-151(③)を既存表書式で追加。
- `DECISION_LOG.md`: 直近エントリ直後に新エントリ「PM-CLOSEOUT-CONSOLIDATION-130」(④)+索引1行。
- `docs/pm/PM_GOVERNANCE.md`: 15節末尾に「15-6. Production 1生成セット総原価(2026-09-14ユーザー正式決定)」(⑤)を追加。9節末尾に「9-10. Claude Code usage報告形式(2026-09-14ユーザー正式決定)」(⑥)を追加。
- `CURRENT_SPEC.md`: Grep `## .*報告|## .*コスト` で該当節があればその末尾、無ければ`docs/pm/PM_GOVERNANCE.md`参照の1段落(「Production記事生成コストの報告方式はPM_GOVERNANCE 15-6(Production 1生成セット総原価主指標、50:50配賦禁止)に従う。2026-09-14ユーザー正式決定、運用仕様として追跡」)を、Grep `## Discovery Focus S2` の直前(または適切な運用節)に追加。Voices 3V未配線記述の末尾に「(2026-09-14ユーザー正式決定) Production Writerを2/3 Voices可変へ一般化: `APPROVED_FOR_PRODUCTION`(未配線、OPEN-151でGate 3追跡)」を追記。
- `docs/pm/PM_BRIEF.md`: L59-116段落内の「記事制作Trial/Production runのコスト報告は同15節…5区分」の直後に「Production記事生成コストは15-6『Production 1生成セット総原価』を主指標(50:50配賦禁止)、Claude Code usageは9-10の形式(2026-09-14)」を1文追記。
- `docs/pm/ACTIVE_TASK.md`: 固定ヘッダで上書き(管理ID=本タスク、UDR-blocking=なし、UDR-deferred=OPEN-148(HIGH)/OPEN-149(MEDIUM)/OPEN-150(LOW)/OPEN-134等、APPROVED未配線=OPEN-151(Voices 2/3可変Writer、Gate 3進行予定)/OPEN-83/145/146(+OPEN-120)、STOP条件=なし、次アクション=4TYPE補完A/B/C完了待ち→Voices Gate 3、報告単位Status: 4TYPE補完=進行中 / Family C=Trial-08 VALIDATED評価待ち)。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-130.md --json-out docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-130_check.json`
2. `git status --porcelain` → `git add OPEN_ITEMS.md DECISION_LOG.md CURRENT_SPEC.md docs/pm/PM_GOVERNANCE.md docs/pm/PM_BRIEF.md docs/pm/delegation_log/PM-CLOSEOUT-CONSOLIDATION-130.md docs/pm/delegation_log/PM-CLOSEOUT-CONSOLIDATION-130_check.json` → commit → `git push origin main`(classifierブロック時は同一コマンド最大3回再試行)。
(回帰不要: コード変更なし。)

## SSOT追記文

① OPEN-149: 「| OPEN-149 | **A-Family Research / Verification / Final Web Fact Check cost optimization(Priority: MEDIUM、Status: DEFERRED、2026-09-14ユーザー判断)**: 現状A-Family(News/Trend/Discovery)はResearch/Verification→Verified Fact Ledger→Writer→Ledger Deviation→独立Web Fact Checkerの構成で、Web検索を複数段階で繰り返しており量産コスト上の最適化余地が大きい(4TYPE観測: Research/Ledgerがセット原価の50〜60%、Final Fact Checkerも毎回web_search)。一方、EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01のTrend A2では最終Fact Checkerが上流Researchの取りこぼし(Google XRメガネ発売発表2026-05-19)を実際に検出したため**単純削除は禁止**。論点: 上流Research/Verificationの精度向上/Final Web Fact Checkを全件検索ではなく必要時のみ検索する可能性/Fact Safetyを落とさずWeb Search重複を減らせるか/News・Trend・Discovery共通基盤への影響。今回はProduction変更・追加Trial・最適化を行わない(ユーザー判断)。 |」
② OPEN-150: 「| OPEN-150 | **No Jargon Writer compliance instability(Priority: LOW、Status: DEFERRED、2026-09-14ユーザー判断)**: No JargonはProduction Writer正式原則(PRODUCTION_WIRED)だが、Discovery実記事『Why can silence feel uncomfortable?』(4TYPE観測)のReader-facing本文に"parasympathetic activity"/"sympathetic activity"/"fMRI acoustic noise"等の高度専門語が流出。Writerが指示を守らなかった、または当該語を高度専門語と判定しなかった可能性。No Jargon専用Blocking Validatorは現在存在しない。現時点では新Checkerを追加しない(理由: APIコスト増、False Positive、副作用、新たな検証コストの回避)。今回は個別修正(EDITORIAL-4TYPE-FOLLOWUP-03)で対応し、今後のProduction記事で再発頻度を観測。再発が継続する場合のみPrompt/軽量対策を再検討。 |」
③ OPEN-151: 「| OPEN-151 | **Voices Production Writerの2/3 Voices可変一般化(Status: `APPROVED_FOR_PRODUCTION`、未配線、2026-09-14ユーザー正式決定)**: 4TYPE観測で、2 Voicesで新規Topicを書き起こす正式Production pathが存在しない(a2/b1 runnerは承認済み固定記事の音声再配線専用、新規Writer`write_new_theme`は3V専用で`voice_cards==3`を強制)と判明。ユーザー決定: Production Writerを2/3 Voices可変へ一般化する。Gate 3で最低限確認: 2V新規topic正式Production path/3V既存挙動のRegressionなし/registry可変voice数/retry・fallback整合/Fact attribution・Comment Contract・Gate辞書整合/2V runtime evidence/3V regression evidence/CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/Git反映。実装途中ではPRODUCTION_WIREDとしない。関連: CURRENT_SPEC L657-659の3V未配線5項目、OPEN-120(3Vゲートruntime evidence)。 |」
④ DECISION_LOG: 「2026-09-14: PM-CLOSEOUT-CONSOLIDATION-130。ユーザー正式決定4件をSSOT反映: (1)OPEN-149 A-Family Research/Verification/Final Web Fact Check cost optimization=MEDIUM/DEFERRED(単純削除禁止、今回Production変更なし)。(2)OPEN-150 No Jargon Writer compliance instability=LOW/DEFERRED(新Checker追加せず、個別修正+再発観測)。(3)コスト報告形式の恒久統一: Familyごとに『Production 1生成セット総原価』を主指標、共通Research/Ledgerの50:50配賦による擬似記事単価は禁止、機械分離できる直接費のみ参考内訳(PM_GOVERNANCE 15-6、CURRENT_SPEC参照段落、PM_BRIEF)。(4)Claude Code usage報告形式: Production pipeline API usageとClaude Code development/audit usageを別項目、cumulative_usageを『量産1記事のClaude token』と表現しない、週間利用枠before/afterが取得可能な場合のみ『xx%→yy%(+z pp)』、取得不能なら『週間利用枠換算: 取得不能』、推定%禁止(PM_GOVERNANCE 9-10)。(5)OPEN-151 Voices 2/3可変Writer=APPROVED_FOR_PRODUCTION(未配線、Gate 3追跡)。」
⑤ PM_GOVERNANCE 15-6(ユーザー指示原文8の内容を規範文として記載。標準表の書式をそのまま含める。「量産時1記事単価」は主見出しにしない、50:30配賦禁止、Trendのような1run A2+B1は「Production 1生成セット(A2+B1)=¥xx」表示、直接費内訳はResearch/Ledger・A2 Writer・B1 Writer・QA・retry・rewrite・その他、を明記)。
⑥ PM_GOVERNANCE 9-10(ユーザー指示原文9の内容を規範文として記載: 別項目化、cumulative_usageの表現禁止、週間利用枠の表記形式、取得不能時の明記、推定%禁止。代替指標としてtool uses・委任数・transcript実測cumulative_usageを「Claude Code development/audit usage(参考)」欄に限って記載可)。

## Git(明示add対象・コミットメッセージ・trailer)

- 明示add: 上記コマンド2の7ファイルのみ。
- コミットメッセージ: `PM-CLOSEOUT-CONSOLIDATION-130: OPEN-149/150/151起票(Fact Check最適化MEDIUM・No Jargon LOW・Voices 2/3可変Writer APPROVED)+コスト報告『Production 1生成セット総原価』とClaude usage報告形式の恒久反映` の後に空行、末尾に
  `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`
  `Claude-Session: https://claude.ai/code/session_01THnbjj6FiMbJtrKdFteoE4`

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`へ: 1) commit hash(full)・push結果、2) 追記位置(ファイル・行)一覧、3) OPEN-149/150/151の行番号、4) T-0・事前指定外Read、5) ACTIVE_TASK更新済み、6) STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥0)
- [x] 並行タスク衝突回避あり(er014不可・並行側Git操作なし)
