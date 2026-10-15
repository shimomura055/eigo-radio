# 委任文 保存: FAMILY-X-COFFEE-FINAL-SPEC-COMPLETENESS-AUDIT-01 委任_01A (2026-10-15、T-0保存)

## 管理ID

`FAMILY-X-COFFEE-FINAL-SPEC-COMPLETENESS-AUDIT-01`(略称CFSA)委任_01A(**仕様側**: 完成条件の再構成・仕様マトリクス「期待」列・In One Line時系列・原因分析候補)。同時に委任_01B(成果物側: 実artifact観測)が並列で走る。両者の成果物は別ファイル。並行する他管理ID: KGCPW 委任_02(コード・`er071_output/.../gloss_alignment_production_wiring_01/`・OPUS台帳・REPORT_LEDGER・ACTIVE_TASKを編集中)、Day3 委任_E(`docs/research/.../day3/`)。本委任は**Read-only調査**であり、これらに一切触れない。git `index.lock`衝突時は30秒待ち最大3回再試行。

## 性質/到達上限Status/禁止事項

- 性質: Read-only監査(調査・分析・報告)。Production実装・音声再生成・有料API・Trial・SSOT編集・Open Item起票は**禁止**。到達上限Status: `AUDIT_PART_A_COMPLETE`。`PRODUCTION_WIRED`等のStatus変更なし。
- 禁止: 有料API 0(JPY0)。`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/ACTIVE_TASK.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/USER_DECISION_REGISTER_01.md`/コード/Prompt/profile/音声/`user_test/`の編集禁止。git add -A/-f、amend、rebase、force push、stash、clean、reset --hard、checkout -f禁止。新Validator・新管理制度の提案禁止(既存機構での是正案のみ)。
- Opus独立技術レビューGate: 非該当(監査・設計変更なし)。
- 時間見込み: 約2h。並列化: 01A(仕様側)と01B(成果物側)を並列、統合は委任_02。本委任内はSSOT・Trial Report・委任ログの読取が中心で直列。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Readを基本。G-1: git出力は最小化。F-1: transcript退避不要。T-0: 本ファイルへ全文保存+check_delegation_prompt実行。T-2: TTSなし(本委任は該当せず)。T-3: 費用上限JPY0のためGuardrail文不要。

## ユーザー指示(原文)

(2026-10-15、全文、委任文内の転記をそのまま保存)

> # Claude Code／Fableへの指示
> ## Coffee完成版：最新仕様の網羅性・反映状況の全面監査
> **管理ID：FAMILY-X-COFFEE-FINAL-SPEC-COMPLETENESS-AUDIT-01** / **現在Status：AUDIT_REQUIRED** / **今回の到達目標：Coffee Standard／Advanced完成版について、仕様反映状況・未反映事項・原因・必要な是正内容を明確化すること。** / **今回の作業範囲：Read-only調査・分析・報告まで。Production実装・音声再生成・追加Trialは禁止。**
> ## 1. 背景・問題
> ユーザーはCoffee記事について、これまでのTrial成果・承認済み改善を可能な限り織り込んだ完成版を依頼していた。しかし、最新試聴ページを確認したところ、**In One Lineが依然として1文構成**になっている。また、Key Phrase選定や各Voice Promptなど、他の最新仕様がどこまで反映されているかも不明確である。現時点で確認できている事実：最新試聴ページ：`user_test/coffee_m2p0_n01_final_03/index.html`/Standard／Advancedの正式assemble音声は存在する。/`CURRENT_SPEC.md`ではIn One Lineの新2文方針が`OPEN-299`として未仕様化。/M2＋P0、N01、Standardの6%減速、Advanced E1／P3、Standard R2などには反映記録がある。/一方、KP英語K2／日本語M2、Intro等の固定音声については、実際の完成音声と承認Styleの一対一照合が未完了。/一部の固定Master phraseは、通常のAudio Validation Gateの走査対象外。/旧gloss再整合工程を使って生成したCoffee完成版と、その後正式採用された修正版correctedは区別が必要。**完成音声が存在し、技術テストがPASSしただけでは、ユーザー要求を満たしたことにはならない。**
> ## 2. 監査の基本方針
> 最初に、Coffee完成版の本来の完成条件を再構成すること。参照するのは以下。1. ユーザーがCoffee完成版の制作を依頼した際の目的・要求。2. 関連Trialで得られた`VALIDATED`の成果。3. ユーザーがCoffee限定で採用した仕様。4. Family X共通の正式Production仕様。5. 完成版作成時点までのユーザー決定と、作成後の新たな承認事項。6. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS、関連委任ログ、Trial Report、実際の成果物。**重要：`VALIDATED`と`APPROVED_FOR_PRODUCTION`は混同しないこと。** ユーザーの「Trial成果をすべて盛り込んだ完成品」という趣旨を尊重しながら、以下を区別する。正式採用済みで、当然反映すべき仕様/Coffee限定で採用された仕様/TrialでVALIDATEDだが正式採用されていない仕様/ユーザーが今回の完成品への反映を個別に指示した仕様/Trialしたが不採用・保留となった仕様/Coffee完成後に承認されたため、当時の完成版には含まれない仕様。Trialが成功しただけの未承認仕様を、独断でProduction採用してはならない。
> ## 3. 監査対象
> 少なくとも以下をStandard／Advanced別に確認する。
> ### A. 記事構成・原稿
> Intro／Welcome／Preview／Full Story／Comment／Key Phrase／In One Line／Outro/Storyの構成・分割数・記事内容/各Commentの役割と本文との接続/In One Lineの文数・内容・長さ・生成Prompt/Standard／Advancedの難易度と原稿の整合/承認済みのWriter／Entertainment／Fact関連仕様。特に**In One Lineの2文構成**について、どのTrialで提案・検証されたか/VALIDATED／正式承認の有無/Coffee完成版へ適用する指示があったか/なぜ完成版では1文のままなのか/仕様管理・制作指示・Fable受入のどこで漏れたか、を時系列で明らかにする。
> ### B. Key Phrase
> M2候補供給・P0選定/Source span／canonicalization／Rule7/Key Phraseの選定数・難易度・意味整合/英語KPと日本語glossの一致/Standard：英語KP→日本語意味→英語KP/Advanced：英語KP→英語解説→英語KP/日本語gloss再整合工程の実際の適用版/retry／fallback／regeneration／Validation Gate。**現時点で正式採用済みのcorrected gloss再整合工程と、旧Coffee音声で使った処理を混同しないこと。**
> ### C. Voice／TTS Prompt・Style
> 各音声segmentについて、期待されるStyleと実際に生成に使用されたStyleを照合する。特に、Intro／固定Master phrase/Standard日本語Preview／Comment：R2/Advanced Preview：E1/Standard／Advanced KP英語：K2/KP日本語意味：M2/Advanced英英解説：P3/Full Story：N01/Standard Full Story：N01＋既存6%減速/In One Line：既存承認Styleと新しい構成方針/その他の承認済み役割別Style、を確認する。P8／PD8／N01など、過去の採用判断が上書きされた経緯も整理すること。**Style名が設定ファイルに存在するだけで反映済みとは判定しない。** 可能な限り、実際の生成Prompt全文またはhash、生成時のprofile、actual model_id、出力音声、validation記録を照合する。seed音声・cache再利用・fallback takeについても、由来を確認する。
> ### D. 音声品質・完成状態
> WPM、文末ポーズ、長い無音/Standardの6%減速後の品質/ASR検証結果/不自然な日本語読み/Audio Validation GateとM3 Style Gate/再利用音声のValidation継承/完成MP3と試聴ページの内容一致/最新仕様の反映漏れによる品質リスク。参考値と正式合否基準を混同しないこと。
> ## 4. 必須成果物：仕様反映マトリクス
> 各仕様について、少なくとも以下を記録する。| 仕様名・管理ID | Trial／承認／実装の出典 | / | 対象 | Standard／Advanced／両方 | / | Trial結果 | VALIDATED／REJECTED／未検証 | / | ユーザー判断 | 採用／Coffee限定採用／保留／不採用 | / | 完成版への適用要否 | 必須／今回対象／対象外／要判断 | / | 期待動作 | 本来どうあるべきか | / | 実際の完成版 | 原稿・音声・Prompt等の観測結果 | / | 判定 | 反映済み／未反映／部分反映／証拠不足 | / | 原因 | 仕様管理・配線・再利用・受入等 | / | 是正方針 | 必要な最小対応 |。**推測をPASS扱いしないこと。証拠がなければ「未確認」と記録する。**
> ## 5. 原因分析・再発防止
> 反映漏れが見つかった場合、個別修正案だけでは不十分。以下を区別して根本原因を分析する。1. Trial成果が正式な採否判断へつながっていなかった。2. 採用済み仕様がProduction経路に反映されていなかった。3. Production側には存在するが、Coffee完成版では旧artifactやseedを再利用した。4. 完成条件に必要仕様の網羅性確認がなかった。5. Fableが実際の完成物を照合せず受入れた。6. CURRENT_SPEC／Decision Log／Open Itemsの情報が制作時に参照されなかった。今回のDay 2運営モデル刷新と関係する問題は、再発防止の検討事項として報告すること。ただし、進行中の運営モデル実装へ無断介入しないこと。
> ## 6. QDCと作業効率
> 今回は**監査のみ**とする。新しい音声生成や有料API Trialは行わない。既存Repo・ログ・artifact・SSOTを最大限活用する。Standard／Advanced、原稿／TTS／Key Phraseなど、独立調査は可能な限り並列化する。共通ファイルの競合を避ける。新しいValidatorや管理制度を今回作らない。費用・工数・完成速度への影響を簡潔に評価する。監査後の修正で音声再生成が必要な場合は、変更対象segmentを特定し、**全記事を無条件に再生成しない**最小対応案を提示する。
> ## 7. 今回のSTOP条件
> 原因調査・証拠照合までは自律的に進める。新仕様の正式採用、承認済み仕様の意味変更、Production有効化は行わない。既存の明示STOP・安全STOPを厳守。調査中に見つかった欠陥を勝手にProduction修正しない。他の管理IDの進行中作業を変更しない。ユーザー判断が必要な点が出ても、技術的な調査や整理を途中で投げ出さず、可能な限り原因と選択肢を確定してから報告する。
> ## 8. 報告形式
> 最初に、**非エンジニアPM向けの超サマリ**を提示すること。その後、次の順序で報告する。1. **結論：Coffee完成版は当初要求を満たしていたか** 2. Standard／Advanced別の仕様反映一覧 3. 未反映・部分反映・証拠不足の項目 4. In One Lineが1文のままになった根本原因 5. Key Phrase／Voice Prompt等の実際の反映証拠 6. 必要な是正内容と最小限の再生成範囲 7. 今回の反映漏れを引き起こしたPM・制作工程の問題 8. QDC影響・費用見込み 9. 未解決事項・ユーザー判断が本当に必要な事項。FableはSonnetの結果を単純に転送せず、**当初のCoffee完成目的・承認済み仕様・実際の成果物を自ら照合し、独立受入判定と根拠を示すこと。** 今回の最終Statusは監査完了または未完了とし、音声成果物やProduction仕様を`PRODUCTION_WIRED`へ変更しない。**監査結果を提出したところでSTOPし、ユーザーの判断を待つこと。**
> ## 最重要事項
> 今回の本質は、In One Lineの1文だけではない。**ユーザーが求めた「最新の改善成果を網羅したCoffee完成版」が本当に作られていたか、仕様・Prompt・音声・成果物の全体を確認すること。** 仕様が承認されていても完成品に反映されていなければ、完成とはいえない。また、VALIDATEDであっても未承認の仕様は、Production採用と区別して報告すること。根本原因と最小是正案を揃え、ユーザーが次の判断をできる状態で報告してください。

## 既知の手がかり(Fable整理、出発点)

最新完成版=`user_test/coffee_m2p0_n01_final_03/`(FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 委任_04、CHECKLIST_05、REPORT_LEDGER L295、run dir=`er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01/`)。前の完成版=`user_test/coffee_final_v3/`(FAMILY-X-COFFEE-FINAL-AUDIO-ASSEMBLY-01 委任_01+02、OPEN-298/299/300)。Coffee関連Trial(REPORT_LEDGER L256-274)。M2P0/N01配線(L284/286/290-295)。In One Line 2文=OPEN-299。gloss再整合: Coffee完成版は旧(legacy)工程、修正版correctedは2026-10-15正式採用(KGCPW配線中)。

## 事前指定Read一覧 / Grep一覧(要旨)

REPORT_LEDGER L240-302、CHECKLIST_05、FINAL_REPORT_01/02、COFFEE-FINAL-AUDIO-ASSEMBLY-01 委任_01/02、delegation_log(COFFEE/M2P0系)のユーザー指示節、OPEN_ITEMS(OPEN-276/278-281/294-296/298-300/349/350/356)、DECISION_LOG(2026-10-08以降Coffee関連)、CURRENT_SPEC(Family X節)、USER_DECISION_REGISTER、In One Line 2文のTrial出典、PM_GOVERNANCE(Gate 7/Closeout Check)。In One Line時系列・Style採用経緯のrg手順。成果物は`er071_output/m2p0_n01_production_wiring_01/coffee_spec_completeness_audit_01/`(本委任は`A_`接頭辞)。

## 成果物

`A_COMPLETION_CRITERIA_RECONSTRUCTION_01.md`(§0超サマリ10行/§1ユーザー要求原文+出典行/§2仕様側マトリクス全列挙[6区分、実際・判定・原因は空欄]/§3 Gate 7・Closeout観点でCHECKLIST_05の網羅性確認有無)、`A_IN_ONE_LINE_TIMELINE_01.md`(時系列表)、`A_ROOT_CAUSE_CANDIDATES_01.md`(ユーザー§5の6分類+Day2運営モデルとの関係1段落)。

## SSOT追記文 / Git

SSOT追記なし(編集権なし)。明示add対象=上記A_3ファイル+本ファイル+`_check.json`。コミットメッセージ「FAMILY-X-COFFEE-FINAL-SPEC-COMPLETENESS-AUDIT-01 委任_01A: Coffee完成条件の再構成(ユーザー要求原文・仕様側マトリクス・6区分)+In One Line 2文構成の時系列+根本原因候補。Read-only、SSOT/Production無変更、JPY0」、push to origin/main。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_CFSA1A.md`へ(1)T-0 (2)§0超サマリ転記 (3)ユーザー要求原文の所在と要点 (4)マトリクス件数(区分別) (5)IOL時系列の結論 (6)final_03完成宣言時の網羅性確認の有無(逐語) (7)01B/委任_02で確認が必要な点 (8)commit hash・push・raw URL (9)確認できなかった事項 (10)逸脱。

## 事前指定Grep一覧+追記位置・更新位置の手順

- In One Line時系列: `rg -n "in_one_line|In One Line|IN_ONE_LINE" DECISION_LOG.md DECISION_LOG_HISTORY.md OPEN_ITEMS.md OPEN_ITEMS_HISTORY.md CURRENT_SPEC.md docs/pm/delegation_log docs/pm/*.md --glob "!docs/pm/RESULT_PACKET*"` → 日付順に並べ、提案→Trial→VALIDATED/承認→Coffee適用指示の有無→完成版作成→受入の各段で記録/見落としを特定。
- Style採用経緯: `rg -n "PD8|P8\b|N01|\bR2\b|\bE1\b|\bK2\b|\bM2\b|\bP3\b" DECISION_LOG.md docs/pm/USER_DECISION_REGISTER_01.md`。
- 成果物は新規ディレクトリ`er071_output/m2p0_n01_production_wiring_01/coffee_spec_completeness_audit_01/`(本委任は`A_`接頭辞)。追記位置・更新位置: SSOT追記なし。

## 実行コマンド全文

- T-0: `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-15_FAMILY-X-COFFEE-FINAL-SPEC-COMPLETENESS-AUDIT-01_01A.md --json-out docs/pm/delegation_log/2026-10-15_FAMILY-X-COFFEE-FINAL-SPEC-COMPLETENESS-AUDIT-01_01A_check.json`
- 一覧: `ls docs/pm/delegation_log | rg "COFFEE|M2P0"`
- git: `git status --porcelain -- er071_output/m2p0_n01_production_wiring_01/coffee_spec_completeness_audit_01 docs/pm/delegation_log`、`git log --oneline -3`
有料API・runner・TTS・音声処理の実行は一切しない。

## KPI provenance欄 / Opus台帳更新

KPI provenance: 該当なし(監査。数値は既存証跡の`reuse`と明記)。Opus台帳更新: 該当なし(台帳は編集しない)。
