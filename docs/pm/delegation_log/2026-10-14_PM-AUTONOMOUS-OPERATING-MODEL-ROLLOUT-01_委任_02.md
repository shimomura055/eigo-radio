# 委任_02 保存(T-0)
管理ID: PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 / Day 1 委任_02(成果物統合: Day 1報告1文書+Day 2最小設計案+Day 2ユーザー判断事項。commit/push込み。read-only棚卸の範囲を維持、規則・設定・Agent定義・SSOT・Productionは変更禁止。JPY0)

## 0. ユーザー指示の要旨(逐語保存対象)
目的: 「問題が起きるたびにユーザーへ判断を求める」運営から「承認済みの目的・仕様をAIが自律的に完遂する」運営へ7日間で移行。案Dをベースにするが**6〜8週間・18,000字常駐・新規管理機構の一括導入は採用しない(軽量版D)**。基本方針 **Q>D>C≫開発コスト**(C=量産上限70円/記事セット、開発費=有料API日次共有1,000円(JST))。7つの行動原則(1必要十分で止める 2品質を守り最速 3常に量産単価 4不具合は自律解決 5手段に固執せず捉え方から見直す 6Humanには重要Decisionだけ 7Project全体で判断)を棚卸の評価基準に。M1 Day1棚卸→M2 Day2最小設計確定(ユーザー承認Gate)→M3 Day3-4最小実装→M4 Day5-6実案件2〜3件で新旧比較→M5 Day7採用判断。**Day 1の重要な受入条件: Day 3〜4の実装対象を最小化できていること。** 必須成果物8: 1現状棚卸サマリ(問題点と優先度) 2変更候補一覧(維持/修正/統合/廃止、55項目対応) 3読み込み実態(実測/推定区別) 4既存機構との重複表(5機構) 5日次予算・量産単価の既存実装状況 6未完了項目の引継ぎリスト 7Day 2最小設計案(優先順、必須/後回し) 8Day 2で本当にユーザー判断が必要な事項(選択肢・推奨・QDC影響)。最後にM1〜M5進捗・Day 1受入条件・Day 2判断事項を報告。Day 1完了後は必ずSTOP。「目的は調査資料を増やすことではなく、1週間で新しい運営方式を実用化するための、最小限かつ正確な変更範囲を特定すること。」巨大な新台帳・新設計書を作らない。確認できない事項は「未確認」。
追加指示(同日、別回答§8): Day 1棚卸に本日の実例を取り込む: 「判断済み事項が再びUDRとして提示される/技術的不具合をユーザー判断へ転嫁する/既存のTrial指示が次の報告に引き継がれない/Agent間でSTOP_NOTICEの解釈が異なる/未確認の事項を『異議がなければ承認』と扱う」を現在の規則・Agent定義・運用機構と照合。Day 1はread-only維持。

## 本日の実例(T7〜T11、Fableの誤りとして取り込む)
- T7 判断済み事項の再提示(Fragment C1〜C4=ユーザーはC4選択済み、UDR #52=10-13承認済みを未判断として再掲)。
- T8 技術的不具合の転嫁(Coffee Std KP#4 gloss不整合をG1/G2/G3としてユーザーへ)。ユーザー: 「意味的整合は基本品質要件。工程順序・依存関係を調査し原因特定、既存の翻訳・正規化・検証機構で自動整合。人間が訳を決めれば完成できるという理由でHumanに戻さない」。
- T9 Trial指示の引継ぎ失敗(Family Z Std Preview/Comment 1のA/B独立Trial承認済み指示がB′/3択へ変形)。
- T10 Agent間STOP_NOTICE解釈の相違(M1 runnerは旧Melos NOTICEで停止、Coffee側は非適用)。ユーザー案a承認: 自ID宛NOTICE+全体STOP/STOP_ALL+既存安全停止を検出、発行主体・scope・有効性確認、文字列一致の迂回不可、解釈統一、Regression、runtime evidence。
- T11 「異議がなければ承認」(UDR #53, #55を無言承認扱い)。ユーザー: 禁止。承認済み範囲内かを既存仕様と照合して判断。
T8/T9/T11はFableの判断記録自体の欠陥として扱い、「新たな判断事項を出す前の3確認(過去に決まっていないか/技術的に解決できないか/本当に今判断が必要か)」の常駐核入りを検討材料にする。

## 成果物・固定ブロック要点
成果物: `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/DAY1_REPORT_01.md`(§1〜§10、12,000字以内目安)。E-1 Windows/PowerShell/.venv/PYTHONUTF8。D-1 規則・設定・Agent定義・SSOT・台帳・コード・Prompt編集禁止、有料API禁止、他agent出力に触れない。G-1 commit対象はDAY1_*とdelegation_log 01A/01B/02のみ、ファイル名明示add、ACTIVE_TASK*/RESULT_PACKET*はgitignored、secret_scan --staged、trailer Managed-ID。F-1 JPY0。T-2 ACTIVE_TASK_ROLL.md(DAY1_COMPLETE_USER_DECISION_REQUIRED)、T-3 RESULT_PACKET_ROLL.md(30行以内)。
Fable(PM)のDay 2最小設計の叩き台(Charter 1,000〜2,000字/sonnet-worker.md/sandwich-pm.md/stop_check/pre-commit secret scan/budget読取script/マーカーStop hook検証、後回し=state_gate等)と成果物8候補(1〜7)は委任文§3に記載。根拠が反する場合は反論を報告に書く。
