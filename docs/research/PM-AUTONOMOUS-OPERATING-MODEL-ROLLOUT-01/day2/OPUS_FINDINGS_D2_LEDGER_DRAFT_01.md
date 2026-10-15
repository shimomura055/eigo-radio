# OPUS_FINDINGS_D2_LEDGER_DRAFT_01: Opus条件A所見OF-D2-01〜22の台帳行(草案。SSOT未反映)
管理ID: PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 / Day2 Phase A 委任_D / 2026-10-15
性質: `docs/pm/OPUS_FINDINGS_LEDGER.md`(11-5)への追記案。**本委任ではSSOT編集権がないため台帳本体は未編集**。ユーザー設計承認後の委任で、下表を台帳末尾へ追記する。原文は`OPUS_REVIEW_D2_01_VERBATIM.md`(逐語)。形式は台帳ヘッダ10列(ID/日付/Opus#/区分/指摘要旨≤40字/Fable採否/反映(委任#)/Evidence/Closeout確認/Status)に合わせた。
Status「DESIGN_REVISED」は、設計文書(v2)に反映済みで、規則・Agent定義・Production本体は未変更・未承認であることを示す(台帳の既存状態`IMPLEMENTED/TRIALED`には該当しないため、承認後の実装委任で`IMPLEMENTED`へ遷移させる)。

| ID | 日付 | Opus# | 区分 | 指摘要旨(≤40字) | Fable採否 | 反映(委任#) | Evidence | Closeout確認 | Status |
|---|---|---|---|---|---|---|---|---|---|
| OF-D2-01 | 2026-10-15 | ROLLOUT Day2 Phase A Opus条件A | BLOCKER | 判断区分「次だけ」で既存STOP条件が狭まる | 採用 | 委任_D: Charter v2「主に次+正本参照」、旧W5b撤回 | day2/CHARTER_DRAFT_02.md §1・§2 | 未 | FABLE_DECIDED→DESIGN_REVISED |
| OF-D2-02 | 2026-10-15 | 同上 | MAJOR | U2の再計画後の実行回数が未定義 | 採用 | 委任_D: U2案A「追加委任最大2回(数値は承認事項)」 | day2/USER_DECISIONS_02.md U2 | 未 | FABLE_DECIDED→DESIGN_REVISED |
| OF-D2-03 | 2026-10-15 | 同上 | MAJOR | U2の順序が11-3条件Bと逆 | 採用 | 委任_D: 条件B該当はOpus先行→再計画 | day2/USER_DECISIONS_02.md U2 | 未 | FABLE_DECIDED→DESIGN_REVISED |
| OF-D2-04 | 2026-10-15 | 同上 | MAJOR | L3診断後・11-1 STOP(3)の変更が未開示 | 採用 | 委任_D: U2本文に開示、「変えない」案Aを推奨 | day2/USER_DECISIONS_02.md U2 | 未 | FABLE_DECIDED→DESIGN_REVISED |
| OF-D2-05 | 2026-10-15 | 同上 | MAJOR | 既定OFF例外は一般許可への拡大(条件不足) | 採用 | 委任_D: U3'単独項目化+5条件+例外なし案B併記 | day2/USER_DECISIONS_02.md U3' | 未 | FABLE_DECIDED→DESIGN_REVISED |
| OF-D2-06 | 2026-10-15 | 同上 | MAJOR | 11-3再レビュー「のみ」が5条件を狭める | 採用 | 委任_D: 5条件維持+追加型文言(「のみ」削除) | day2/USER_DECISIONS_02.md U4(a)、MINIMUM_CHANGE_PLAN_02.md W5a(d) | 未 | FABLE_DECIDED→DESIGN_REVISED |
| OF-D2-07 | 2026-10-15 | 同上 | MAJOR | 原因究明ループが26-2(a)と衝突 | 採用 | 委任_D: W2に「26節優先・再現のための再実行をしない」 | day2/MINIMUM_CHANGE_PLAN_02.md W2、USER_DECISIONS_02.md U3(b) | 未 | FABLE_DECIDED→DESIGN_REVISED |
| OF-D2-08 | 2026-10-15 | 同上 | MAJOR | 原則4が12-2のblocker即時報告と衝突 | 採用 | 委任_D: 原則4の括弧にblocker・12-2を追記 | day2/CHARTER_DRAFT_02.md §1 | 未 | FABLE_DECIDED→DESIGN_REVISED |
| OF-D2-09 | 2026-10-15 | 同上 | MAJOR | F3が形式的に満たせ独立性を欠く | 採用 | 委任_D: L29は量のみ制限、観測値引用、ユーザー報告掲載 | day2/USER_DECISIONS_02.md U3(a)、MINIMUM_CHANGE_PLAN_02.md W3 | 未 | FABLE_DECIDED→DESIGN_REVISED |
| OF-D2-10 | 2026-10-15 | 同上 | MINOR | 失敗経路確認をGate 3に置いても発火しない | 採用 | 委任_D: Gate 7+W7を主、§6失敗経路版、Gate 3は補助 | day2/MINIMUM_CHANGE_PLAN_02.md W5a(b) | 未 | FABLE_DECIDED→DESIGN_REVISED |
| OF-D2-11 | 2026-10-15 | 同上 | MAJOR | D1とSonnetループ上限の関係が未定義 | 採用 | 委任_D: D1=編集禁止・別カウント・最大2回・git無変化確認 | day2/USER_DECISIONS_02.md U2・U3(a) | 未 | FABLE_DECIDED→DESIGN_REVISED |
| OF-D2-12 | 2026-10-15 | 同上 | MINOR | STOP文言が曖昧(helper実行義務等) | 採用 | 委任_D: helperをBash実行・rc=3停止・fail-closed | day2/USER_DECISIONS_02.md U3(e) | 未 | FABLE_DECIDED→DESIGN_REVISED |
| OF-D2-13 | 2026-10-15 | 同上 | MINOR | §11 L1872がW4対象から漏れ | 採用 | 委任_D: W4の対象に追加 | day2/MINIMUM_CHANGE_PLAN_02.md W4 | 未 | FABLE_DECIDED→DESIGN_REVISED |
| OF-D2-14 | 2026-10-15 | 同上 | MINOR | packet承認状況欄・撤去Grep行が無い | 採用 | 委任_D: W7に2行追加(現行テンプレに欄が無いことを確認) | day2/MINIMUM_CHANGE_PLAN_02.md W7 | 未 | FABLE_DECIDED→DESIGN_REVISED |
| OF-D2-15 | 2026-10-15 | 同上 | MINOR | 観点11注記がpacket側のみだと欠落 | 採用 | 委任_D: U4(c)任意(ブロック本体へ1行、承認要) | day2/USER_DECISIONS_02.md U4(c) | 未 | FABLE_DECIDED→DESIGN_REVISED |
| OF-D2-16 | 2026-10-15 | 同上 | MINOR | haiku B案は承認済み機能の事実上廃止 | 採用 | 委任_D: U3(c)A/B明示、A(tools欄追加)推奨 | day2/USER_DECISIONS_02.md U3(c) | 未 | FABLE_DECIDED→DESIGN_REVISED |
| OF-D2-17 | 2026-10-15 | 同上 | MINOR | 原則4が作業範囲拡大を誘発 | 採用 | 委任_D: 原則4に「委任範囲内で」 | day2/CHARTER_DRAFT_02.md §1 | 未 | FABLE_DECIDED→DESIGN_REVISED |
| OF-D2-18 | 2026-10-15 | 同上 | MINOR | W6欄名「逐語要旨」は矛盾 | 採用 | 委任_D: 「原文引用+DECISION_LOG出典」へ | day2/MINIMUM_CHANGE_PLAN_02.md W6、USER_DECISIONS_02.md T12 | 未 | FABLE_DECIDED→DESIGN_REVISED |
| OF-D2-19 | 2026-10-15 | 同上 | MINOR | リプレイが結論既知で検出力を測れない | 採用 | 委任_D: 盲検リプレイ+陰性対照+事後実測 | day2/MINIMUM_CHANGE_PLAN_02.md §5 | 未 | FABLE_DECIDED→DESIGN_REVISED |
| OF-D2-20 | 2026-10-15 | 同上 | MINOR | W5bの整合リスクが高く原因でもない | 採用 | 委任_D: W5bを後回し(P15)、必須8単位 | day2/MINIMUM_CHANGE_PLAN_02.md §0・§3 | 未 | FABLE_DECIDED→DESIGN_REVISED |
| OF-D2-21 | 2026-10-15 | 同上 | MINOR | 安全文言の変更前後の実文が未提示 | 採用 | 委任_D: Charter判断区分/既定OFF/U2に逐語並記 | day2/USER_DECISIONS_02.md §1参考・U1・U2・U3' | 未 | FABLE_DECIDED→DESIGN_REVISED |
| OF-D2-22 | 2026-10-15 | 同上 | MINOR | 既定ONフラグ約12件の突合が後回し | 採用 | 委任_D: P13をDay5リプレイ試験に含める | day2/MINIMUM_CHANGE_PLAN_02.md §3・§5 | 未 | FABLE_DECIDED→DESIGN_REVISED |
