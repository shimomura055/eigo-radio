# RISK-FLAGGER-PRODUCTION-WIRING-01 委任_03: 設計v2(新Writer配線+RF配線+旧Checker撤去の一括Production Wiring)

- 日付: 2026-10-10 / 性質: 読み取り・設計のみ(Production/CURRENT_SPEC/Prompt変更なし、課金API 0件、Agent起動なし)
- 前提: DESIGN_01(1〜13節+14節Opusレビュー)。DESIGN_01は変更せず、DESIGN_02.mdを新規作成。
- ユーザー方針更新(2026-10-10、正式決定、委任文より要約): 段階案不採用/新Writer(Fact Lock)配線+RF配線+旧Fact Checker撤去を一括/Standard・Advanced両方にRF適用・旧Checker撤去(R2後JA Fact Check含む)/OPEN-233系Checkerは配線しない/技術QA維持/Standard・Advanced非対称棚卸必須/Review Queue=review_queue/post_en/(runnerにgit責務なし)/RF非Blocking/splitter共通module/費用3ギャップ修正承認/git revert+tag/L3最終Evidence(テーマ未指定ならSTOP)/Status=APPROVED_FOR_PRODUCTION(Gate 3全充足時のみPRODUCTION_WIRED)/Opus必須修正8点取込。
- 成果物: docs/pm/design/2026-10-10_RISK-FLAGGER-PRODUCTION-WIRING-01_DESIGN_02.md
- 結果要約: (1)新Writer正式仕様は一意に特定できない(STOP): 承認はコンセプト(OPEN-244)のみ、候補W-1(E2E新腕: Fact Lock R0[Luna]+Astra R1/R2+B1+M1/M3)/W-2(Fact Lock v1全Luna)/W-3(Astra R3まで)/W-4(R0のみ)、R0・R1/R2モデル未決、FACTLOCK-ASTRA-E2E方向判断(a)〜(e)未回答、B3注記のProduction自動化は未設計・未測定。(2)非対称棚卸16行、②=4件(②-a=2、②-b=1、②-c=1[M1(a)])。(3)撤去28行(22+6)、T-17/T-18維持明記。(4)L2は技術的同等と言えない→L3必須、テーマ未指定でSTOP。(5)Phase 2規模 新規+1,700〜2,100行/テスト+1,200/削除−500。(6)STOP候補S2-1〜S2-12(固定条件でPrompt変更・新仕様候補に該当)。
- 注意: 委任文の「ユーザー16条件」原文は本委任文に含まれず、固定STOP条件+委任_01+今回指定で照合(Fableが突合)。委任文の「15項目」は列挙語が16個のため16行で作成。
- T-0(委任文保存検証): 本委任文はテンプレート見出し構成(性質/事前指定Read/実行コマンド全文/固定ブロック)を持たないため委任_01と同様に非準拠(非ブロッキング運用)。
