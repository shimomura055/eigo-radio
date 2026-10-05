# 委任_03 全文(OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01、2026-10-05、Fable→Sonnet)

## 管理ID

`OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01`(委任_03、改善ループ1/3の「設計」段)。**並行タスクあり**: 委任_04(PM_GOVERNANCE/DECISION_LOG/CURRENT_SPEC/OPEN_ITEMS/REPORT/REPORT_LEDGER/toolsを編集・commit)。**本委任はそれらを編集せず、git操作もしない**(新規文書・スクリプト・出力のみ作成。次委任でadd)。報告はhandback本文。

## 性質/到達Status/禁止事項

- 性質: ¥0。RCA(`docs/pm/rca_open233_stage1_checker_01.md`)の結論(非決定性は存在するが主因は設計: 網羅を要求しない1 call集約・非検出時に決定論層が走らないF3・候補生成をLLMに委ねる)を受け、**Stage 1の役割・構造・判定方式の設計案を比較**し、既存データで¥0事前評価を行い、Opus#16(必須独立レビュー)向けpacketを作る。実装・有料API・Prompt修正は本委任で行わない。
- KPI(不変): Human Review 0 / 重大Fact見逃し0 / 平均追加+¥2/記事。E2E(fresh Stage 1)で判定。重大に対して甘くするのは禁止、過剰検出の抑制は可。Safety-critical定義・gold・母数は変更禁止。
- 到達Status: Trial、最大`VALIDATED`。後段`APPROVED_FOR_PRODUCTION`と混同しない。
- 禁止: コード変更(runner/er051/er003/Production)禁止。有料API禁止。「LLMは揺れるから仕方ない」禁止。単なるPrompt文言変更案のみで終わること禁止(根本が構造なら構造案を主軸に)。`git add`/commit禁止。1回の書き込み2,500文字以下。
- 費用枠(参考): Phase残約¥138+本管理ID追加+¥100(ユーザー決定2026-10-05)。設計案ごとに¥0→小規模→E2Eの費用見込みを出す。
- T-0: 委任ログ(本ファイル)に全文保存(分割)、check実行・結果をhandbackに1行。
- 固定ブロックE-1/D-1/G-1/F-1/T-2/T-3は従来どおり。

## ユーザー指示(原文、該当部分。全文はDECISION_LOG 2026-10-05エントリ)

````
4. 根本設計も検討対象
…例として、
- deterministicな候補抽出との役割分担
- 重大カテゴリごとの機械的pre-check
- 複数候補を漏れなくStage 2へ渡す構造
- Stage 1の複数回実行・和集合
- 最終PASS前の安全確認
- 既存Checkerと補完層の役割分担
等は検討対象になり得る。ただし上記をそのまま採用せよという意味ではない。
QCD・単純性・既存資産再利用・非決定性・Production運用性を比較して、最も合理的な構造を設計すること。
5. Opusレビュー
…Opusには追認させず、最低限以下を問うこと。
- 単一Checker方式を維持する必要があるか
- より単純で堅牢な方法はないか
- 重大見逃し0に対して構造的な穴がないか
- 過剰検出・Rewrite・Human Review・費用を増やしすぎないか
- deterministic / LLMの責務分担は適切か
- retry / fallback / regenerationを含めProductionで成立するか
- Stage 1だけでなくE2E KPIとして成立するか
````

## 作業1: 設計案比較(新規`docs/pm/design_open233_stage1_redesign_01.md`)

RCA §5の案A〜Fを起点に、少なくとも次を比較(各案: 構造図[文章]/LLM call数と費用/非決定性への耐性/重大見逃し0への構造的根拠/過剰検出・Stage 2発動率・Rewrite率・Human Reviewへの影響/既存資産再利用(runner決定論floor・`causal_strength`・`SAFETY_CRITICAL_CLAIM_DEFS`・Ledger構造・`expand_same_fact_id_locations`・Stage 2 batch・S1・S1-U)/Production運用性(retry/fallback/regeneration、Routing)/単純性/残る穴):
- 案1 現行V4A単発+Prompt改善(網羅要求・「迷えば許容」バイアスの除去)— 比較の基準線として(ユーザー§2「小修正ありき禁止」なので主軸にしない)。
- 案2 Stage 1複数回実行∪(n=2/3)— ¥0 replayでneg5/HF-011を拾えないことが示唆されているため、単独では不十分と明記。
- 案3 **決定論候補抽出+LLM分類**: Ledger fact(日本語本文・数値・主体・否定・時期・因果語)と英語本文の文単位alignmentで「fact対応文」を機械的に全列挙→各文×factの対を候補としてLLMに「逸脱か/フラグ/重大度」を判定させる(Stage 1を再現率優先の列挙専用にせず、候補を機械で作り分類だけLLM)。候補数と費用、alignment精度のリスク。
- 案4 **カテゴリ別決定論pre-check(非検出時も走る)**: 主体/数値/否定/比較・方向/時期/因果の6カテゴリで、Ledgerと本文の機械照合により「不一致候補文」を生成し、Stage 1非検出でもStage 2へ渡す(F3の穴を閉じる)。HF-011型(意味的scope変化)は対象外→他の層で担う。
- 案5 **Stage 1を「fact単位の網羅問い合わせ」に分解**: 1 callで全列挙させず、fact(または fact群)ごとに「この事実に対応する本文の文を全て引用し、各々の一致/逸脱を判定」と問う(batch化で費用抑制)。網羅性を構造で担保。
- 案6 **最終PASS前の安全確認(独立call)**: 後段PASS直前に、Safety-criticalカテゴリ限定の第2 Checker(別prompt、同モデル)を1回。見逃しの二重化。費用+1 call。
- 案7 組合せ(例: 案4+案5(または案3)+案6、Stage 2/S1は現行)。
各案の「neg5 B3-same(兄弟箇所で同一文)」「HF-011(意味的scope変化)」「A4-0(非決定性)」「B4非SC 4件」をどう拾うかを個別に書く。推奨組合せを1つ提示し、ループ1で検証する最小構成を定義。

## 作業2: ¥0事前評価(スクリプト`er052_output/open233_kpi_recovery_02_offline_01/stage1_redesign_offline_eval_01.py`+json/md)

既存データのみ: A構成fresh 32 run(`a_frozen_fresh_01/`)、frozen記録、V0記録、fixture本文・Ledger(`SAFETY_CRITICAL_CLAIM_DEFS`、er009合成fixture、A2A3/A4/A5/B3/B4/neg1〜5/B2_hormuz/hormuz_run01/02)。計算: (a)案4の決定論pre-checkを**設計レベルで模擬**(fixtureごとに、Ledger factの数値・固有名・否定語・時期語・因果語と本文文の機械照合で候補文が立つか。実装はせずスクリプト内の簡易照合でよい。Safety-critical各claimが候補に入るか、負例/NORMALで候補が何文立つか)。(b)案5の候補数(fact数×対応文数)と費用見込み(fact単位batch)。(c)案2の∪(既存n=2)の検出・誤検出(RCA既出の再掲)。(d)各案の1記事あたりStage 1費用見込み(A 1 call実測¥0.357基準)と、Stage 2発動件数の増加見込み(候補が全てStage 2へ行く場合のbatch費用はrep30のStage 2実測から比例推定)。限界(推測)を明記。

## 作業3: Opus#16 packet(新規`docs/pm/opus_packet_open233_stage1_redesign_01.md`)

雛形(a)〜(g): (a)管理ID・性質・KPI・禁止事項・予算枠、(b)ユーザー指示原文(§2〜§9、DECISION_LOG参照+上記引用)、(c)RCA要点(非決定性/設計問題の分離表、F3、過適合の疑い、HF-011系統的miss疑い)とパス、(d)設計案比較と推奨組合せ、¥0事前評価の結果、(e)Opusへの必須の問い(ユーザー§5の7点)+Fable追加: ①neg5型(兄弟箇所)・HF-011型(意味的scope)を構造的に拾う最も単純な方法 ②候補を全てStage 2へ渡すことの過剰検出・費用・Human Review影響と、Stage 2(V7b+S1+floor)がそれを吸収できるか ③決定論alignment(日英)の精度リスクと失敗時のfail-closed設計 ④retry/regeneration時の再実行コスト ⑤ループ1で最小限何を検証すればKPI見込みが立つか(E2E run数・費用) ⑥後段`APPROVED_FOR_PRODUCTION`設計(Opus#15)との接続点、(f)出力形式(結論→案別判定[採用/不採用/修正採用]→Safety hole→残る穴→STOP条件該当有無→追加Read→答えられなかった点)、(g)`docs/pm/templates/OPUS_INDEPENDENT_REVIEW_BLOCK.md`逐語貼付(スクリプトコピー可)。

## 事前指定Read一覧

RCA文書(自作、全文可)。runner: Grep `causal_floor_guard|CAUSAL_CONNECTIVES_EN|HEDGE_MARKERS_EN|issue_actor_guard|precheck|SAFETY_CRITICAL_CLAIM_DEFS|expand_same_fact_id_locations|enable_s1u|apply_stage2_second_opinion` → 範囲。er003 `causal_strength`(88〜107)。fixture(Pythonで一括読込)。`a_frozen_fresh_01/*.json`、`agg_stage1_variance_impact_01.md`。Opus packet雛形`docs/pm/opus_packet_open233_production_wiring_01.md`(構成のみ)。

## 実行コマンド全文

T-0 check: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_03.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_03.md_check.json
事前評価: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_output\open233_kpi_recovery_02_offline_01\stage1_redesign_offline_eval_01.py
Git: なし。

## 報告(handback、短く)

(1)結論10行以内(推奨組合せ、¥0事前評価の要点: 各案がneg5/HF-011/A4-0/B4をどう拾うか、費用見込み)、(2)比較表の要点、(3)packetパス(Fable追加編集なしで渡せるか)、(4)T-0・作成ファイル一覧(未commit)・一覧外Read・確認/推測、(5)Fableへの論点。

## 実行側補記(Sonnet、原文ではない。checkの必須節を満たすための注記)

- 事前指定Grep一覧+追記位置・更新位置の手順: Grepは上記「事前指定Read一覧」記載のrunner Grepのみ。追記位置=新規ファイル3点(design/packet/offline eval)のみ。既存ファイルの更新位置なし。
- SSOT追記先: なし(本委任はSSOT・PM_GOVERNANCE・REPORT等を編集しない。次委任でFableが追記)。
- 初回check結果(補記前): FAIL(上記2節の欠落のみ)。補記後に再実行。
