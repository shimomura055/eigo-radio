# 委任_01: 報告・表示運用ルール(ユーザー正式決定2026-10-28)の正本反映(PM_GOVERNANCE 12節・CLAUDE.md・sandwich-pm/sonnet-worker agent定義・SSOT)、旧ルール整理、Claude Code表示抑制の可否確認(API 0)

管理ID: PM-REPORTING-RULES-01(Fable→sonnet-worker、2026-10-28)。ユーザー原文(全文必読)=`docs/pm/delegation_log/2026-10-28_FZ-TELL-TALE-HEART-NARRATOR-VOICE-01_USER_02.md` **§2・§3のみ**(§1はVoice案件、本委任の対象外)。共通Charter=`CLAUDE.md`冒頭。成果物=`docs/research/PM-REPORTING-RULES-01/REPORTING_RULES_REFLECTION_01.md`、報告=`docs/pm/RESULT_PACKET_PMRR1.md`。

## 決定内容(転記対象、要約しない=逐語で正本へ)
①作業中の詳細ログ(ツール実行内容・ファイル編集の逐次表示・委任文・Worker起動状況/経過・テスト詳細ログ)をユーザー向けメッセージに出さない(内部記録は従来どおり)。②中間報告(開始・進捗・委任完了)は不要。③タスク単位で完了報告1件(混在・他タスク進捗付記・別タスク待ちのまとめ禁止、並列化は可)。④例外=重大品質/安全・予算超過見込み・仕様/Scope変更等のユーザー判断・明示STOP・自律解決不能なBlockerは即時報告。⑤内部証拠・品質管理(test/Regression・runtime evidence・Fable受入・SSOT・Git・PM Gate/STOP)は省略しない。最終報告=結論・品質結果・Production Wiring Status・QCD・必要なユーザー判断を簡潔に。既存の重要なSTOP・承認・品質Gate・即時報告義務は弱めない。

## 作業
1. **正本の特定と反映**: `docs/pm/PM_GOVERNANCE.md` 12節(報告単位管理ルール: 即時報告・未回答フル再掲・Next Action提示)・9-8(★★★★マーカー)・11-6・29節をGrepで読み、矛盾箇所(例: 「委任完了ごとの報告」「中間報告」「未回答事項のフル再掲」「Next Action提示」等の旧記載)を列挙。**新ルールを12節へ追記**(既存行は書き換えず「2026-10-28改定」として追記し、矛盾する旧記載には「→2026-10-28以降は本改定が優先」を付す)。④の即時報告義務は既存の即時報告規定(重大品質・予算・STOP等)と統合し弱めない。「未回答事項の再掲」は**完了報告内の『必要なユーザー判断』欄に限定**(フル再掲は廃止)と整理(Fable判断、原文③④に基づく)。
2. `CLAUDE.md`: 「Fableサンドイッチ運用(PM層)」のcompact後復帰手順(8)の報告マーカー項の直後へ1行追記「報告運用=PM_GOVERNANCE 12節(2026-10-28改定: 中間報告なし・タスク単位完了報告・例外のみ即時)」。長文化しない。
3. `.claude/agents/sandwich-pm.md`・`.claude/agents/sonnet-worker.md`: ユーザー向け出力に関する記述があれば新ルールへ整合(workerの最終応答はFable向けであり、ユーザー向けではない旨を明確化)。
4. **Claude Code表示抑制の確認**: `~/.claude/settings.json`/プロジェクト`.claude/settings.json`/CLI optionsで、ツール実行表示・verbose・出力省略に関する設定の有無を調べる(公式docs参照可、WebFetch不可ならローカルdocs/既知設定のみ)。結論: 抑制可能な設定があれば適用案(設定変更は**提案のみ**、本委任では変更しない)。不可能なら「ツール呼出表示はClaude Code実行環境の仕様でClaude側から抑制不可」と簡潔に記録。
5. SSOT: `DECISION_LOG.md`末尾へ1エントリ(PM-REPORTING-RULES-01、原文path、決定①〜⑤、正本=PM_GOVERNANCE 12節改定)、`docs/pm/USER_DECISION_REGISTER_01.md`へ判断済み1件、`OPEN_ITEMS.md`へ新規OPEN(次番号)「PM-REPORTING-RULES-01 報告・表示運用ルール」Status=反映済み(本commit)・表示抑制可否の結論。
6. `docs/pm/ACTIVE_TASK.md`の固定ヘッダ「報告運用」欄(無ければStatus行末尾)に「2026-10-28以降: 中間報告なし・タスク単位完了報告・例外のみ即時(PM_GOVERNANCE 12節)」を1行追記。
7. Git: 変更ファイルのみ`git add`、commit「PM-REPORTING-RULES-01: 報告・表示運用ルール(中間報告なし・タスク単位完了報告・例外のみ即時)を正本へ反映(API 0)」+`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`、`git push origin HEAD:main`(競合時`git pull --no-rebase origin main`)。同時進行の他worker(er129〜er132・Z run)のファイルには触れない。
8. 最終応答(Fable向け): 変更ファイル・矛盾整理一覧・表示抑制の結論・commit・raw URL。
