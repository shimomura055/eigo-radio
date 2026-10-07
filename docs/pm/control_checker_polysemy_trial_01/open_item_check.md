# open_item_check: 新規Open Item候補(i)〜(iv)の21節(Existing Spec / Prior Trial Check Gate)A/B/C分類
管理ID: OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01 委任_05(2026-10-07、¥0、Read/Grepのみ)
確認対象: CURRENT_SPEC.md / DECISION_LOG.md / OPEN_ITEMS.md / 過去REPORT・Trial / Production code(runner switch) / 関連管理ID(`docs/pm/PM_GOVERNANCE.md` 21節)。
分類: A=既存仕様あり(未発火ならwiring/regression問題)、B=過去Trialあり・未採用(結果を再利用)、C=本当に新規。

| 候補 | 分類 | 主な出典 | 扱い |
|---|---|---|---|
| (i) 否定・不在主張型の事実反転をStage2がledger_scope→QUALITYへ格下げして見逃す | **B**(一部ギャップ、下記) | OPEN_ITEMS `OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01`行(方向反転等、系統的読み違えを狙い撃つSafety設計、TRIAL-01〜03、TRIAL-03=REJECTED)、REPORT §81-10/§82/§86、OPEN-233行 negative claim候補16件(委任_04)、`OPEN-233-FLOOR-SELECTIVITY-OPTIMIZATION-01`行(floor誤爆35件のうち否定5件、absence/contra混同が根本原因) | 新規登録せず、DIRECTIONAL-MISREAD行へ追記 |
| (ii) 構造要素(タイトル)のRewrite置換とRecheck非対象 | **A** | DECISION_LOG 2026-10-04 KPI-RECOVERY-REDESIGN-02 委任_07/08(「title単独claimのdeleteは技術是正→構造要素はE1/③で書換え」「構造要素書換えの補強: before/after対をRecheckへ渡す=`STRUCTURAL_PAIRS_TO_RECHECK`」)、REPORT(委任_08実装記録: `STRUCTURAL_ELEMENT_REWRITE`)、runner `STRUCTURAL_PAIRS_TO_RECHECK`(L445 KPI構成ON、L2403既定False)、OPEN-238行(Rewrite新規誤り系) | 新規登録せず、OPEN-238行へ追記(wiring/regression観点) |
| (iii) 過去Trialの`--theme`パス文字列問題 | **C** | 既存SSOT(OPEN_ITEMS/DECISION_LOG/REPORT/docs/pm)のGrep(`topic.txt`/`--theme`/パス文字列)で該当記録なし。事実はSUMMARY_CCP.md plan §2(a)・provenance.json theme_note・delegation_log _03のみ | **新規登録(OPEN-240、POST_USER_VALIDATION、Status=OPEN、ユーザー判断待ち)** |
| (iv) 多義語Noteの供給源(既知多義fact登録方式) | **B** | REPORT §89(POLYSEMY-NOTE-DESIGN-01: 案N/案N+B)、§90(TRIAL-02/03: 自動Note生成が3ループで不成立、推奨=既存notes昇格+B3転記)、§91〜§94/§97、OPEN-237行(関連進捗) | 新規登録せず、OPEN-237行へ追記 |

## 根拠詳細
- (i): 否定・不在主張そのものを対象にした先行検討はある(OPEN-233行のnegative claim候補16件、DIRECTIONAL-MISREAD系のセンサー/blind抽出設計、FLOOR-SELECTIVITYの否定5件)。ただし今回の機序(Stage1がMAJORで候補化→Stage2が`basis=ledger_scope`でQUALITYへ格下げ、2nd opinionも同判断、cycle2は非ブロッキング判定を再利用、RCA_jb9k_qvqc.md RCA-①)を個別に追う既存Open Itemは見つからなかった。機序の特定は新しい事実だが、問題の類型(読者が受ける意味反転がscope評価で埋もれる)はDIRECTIONAL-MISREAD系の守備範囲のため、Bとして既存行へ追記する。Fable/ユーザーが「Stage2格下げ判定の個別是正が別問題」と判断する場合はC扱いへ変更できる(私見の保留事項)。
- (ii): 仕様は既にあり、この実行でも`STRUCTURAL_PAIRS_TO_RECHECK=true`だった(`runs/meta/nb/rep2/checker/approved_switches_dump_after_p01.json`ほか3件で確認)にもかかわらず、cycle2のstage2_resultsにtitle単位が含まれずRecheck対象にならなかった(RCA-②)。よって新規仕様ではなく、既存仕様の未発火/漏れ(wiring・regression問題、原因は未調査)として扱う。actor_guard(AG1-strict)が「Meta」を新規主体と検出しなかった点(`ag1 ok=true new_classes=[]`)も既存`actor_guard`仕様の守備範囲(DECISION_LOG同委任_07/08)。
- (iii): Production入口(runner)は`--theme`文字列をそのまま`{topic}`へ埋め込む仕様で、Production欠陥ではない(Trial運用側の入力ミスに近い)。ただし過去結果(TRIAL-04 Control、E2E_02)との厳密比較に影響し、影響未測定のため管理対象として登録する。
- (iv): TRIAL-03が自動生成3ループ不成立(§90)で、供給源の候補(既存notes昇格等)は既に提示済み・判断待ち。本Trial(旧Note規則abd16d9a固定Note)は供給源を扱っておらず、新しい論点ではない。

## 登録結果
- 新規登録: **OPEN-240**(上記(iii))のみ。(i)(iv)はB、(ii)はAとして既存行追記(OPEN-233行/OPEN-238行/OPEN-237行/DIRECTIONAL-MISREAD行)。Production変更・採用提案なし。
