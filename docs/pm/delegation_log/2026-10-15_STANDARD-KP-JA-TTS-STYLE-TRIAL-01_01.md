# STANDARD-KP-JA-TTS-STYLE-TRIAL-01 委任_01 (受領委任文の保存、2026-10-15)

## 管理ID
`STANDARD-KP-JA-TTS-STYLE-TRIAL-01`(略称SKJT)委任_01(初回: 6 Style x 5 Phrase比較Trial+試聴ページ)。並行タスク: KGCPW 委任_03(正式runnerで有料evidence/Regression実行中、SSOT6本・ACTIVE_TASK.md・REPORT_LEDGER.md編集中)、Day3 委任_F2(PM_GOVERNANCE.md/CLAUDE.md/PM_BRIEF.md/docs/research/.../day3/)、CFSA 委任_02(er071_output/.../coffee_spec_completeness_audit_01/)。本委任はこれらに触れず、共有stateへ書き込まない隔離Trialとして実装。git index.lock衝突時は30秒待ち最大3回再試行。

## 性質/到達上限Status/禁止事項
- 性質: 有料Trial(TTS)。現在Status USER_APPROVED_FOR_TRIAL。到達してよいStatus: REJECTED/VALIDATED/USER_DECISION_REQUIRED(Sonnet提案、最終分類はFable)。Production採用・実装禁止(APPROVED_FOR_PRODUCTIONへ変更しない。良好候補があっても試聴ページ提示でSTOP)。
- 到達上限: Trial完了+試聴ページ公開URL+比較結果+推奨候補案。
- Opus独立技術レビューGate: 非該当。
- 費用上限: JPY50(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的/QCD上の便益が明らか、であれば超過を記録して継続。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告。見積の出典: Coffee F5再生成7 call約JPY6.50(REPORT_LEDGER L258)->約0.93円/call x25=約JPY23(TTS)。ASR QAを行う場合は単価を出典付きで加算し、実行前にRESULT_PACKETへ見積を記録。当日(2026-10-15 JST)既使用約JPY7+KGCPW委任_03(上限60)、日次1,000円のソフト上限内。
- 禁止: 6 Promptの文言変更(逐語使用。全角/半角・句読点も変えない)。日本語意味の文言変更(現行canonical text逐語)。英語KP・他segment・Preview/Comment・Advanced・正式J3定義(er019_family_x_style_profile_01.py等)・KP選定・gloss・canonicalization・再整合工程・Production runner・retry/fallback・Coffee完成版MP3/run dir/user_test/coffee_m2p0_n01_final_03/の変更禁止。共有stateへの書込禁止: er006_output/master_audio_store_01/manifest.json・reuse_telemetry.jsonl、er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl、er006_output/pronunciation_ledger_01/ledger.json、er011_output/attempt_history.jsonl、er021_output/**/telemetry.jsonl、er025_output/**/telemetry.jsonl、er030_output/**/telemetry.jsonl、er005_output/cost_baseline_01/cost_summary.json、er011_output/local_rewrite_recovery/(Trial前後でsha256比較し不変を証明)。Batch TTS不使用。git add -A/-f、amend、rebase、force push、stash、clean、reset --hard、checkout -f禁止。SSOT(CURRENT_SPEC.md/DECISION_LOG.md/OPEN_ITEMS.md/REPORT_LEDGER.md/USER_DECISION_REGISTER_01.md)・ACTIVE_TASK.mdの編集禁止(文案のみ)。
- 時間見込み: 約2h。並列化: Style P1〜P5の生成は同時2〜3 process以内。QA・mp3変換・ページ生成は生成完了後に並列可。

## 固定ブロック
E-1: 同一task内で同一ファイルを再読しない。D-1: Grep->該当行範囲Read。G-1: git出力は最小化。F-1: transcript退避不要。
T-0: 受領委任文を本ファイルへ保存し check_delegation_prompt.py を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。
T-2: TTSを伴う委任は TTS_EXECUTION_MODE=STANDARD を明示。Batchは7-2例外理由の明示時のみ。T-2追記: 実行前に(1)差分再生成可否(2)既存音声再利用キャッシュ有無(3)--budget-jpy明示(4)想定外の全再生成ならAPI実行前STOP。
T-3: 費用上限はGuardrailであり到達=自動STOPではない。

## ユーザー指示(原文要旨、Prompt本文は逐語)
Standard Key Phrase日本語TTS Style改善Trial。管理ID STANDARD-KP-JA-TTS-STYLE-TRIAL-01 / USER_APPROVED_FOR_TRIAL / 到達可Status REJECTED・VALIDATED・USER_DECISION_REQUIRED / Production採用・実装禁止。
1. 目的: Coffee記事Std KP「right away」の日本語意味「すぐに」が不必要に感情的・演技的。現行J3の「意味の流れ・強調点・転換に応じて表情豊かに抑揚をつけてください」が短い訳に過剰作用している可能性。改善目標: 過剰な感情表現を取り除き、自然さ・明瞭さ・親しみやすさは維持。不要な変更は避ける。
2. 対象: Coffee完成版Std KP日本語意味5件(1 pump one's fist=大喜びする / 2 raw bean=生豆 / 3 right away=すぐに / 4 based on interviews=インタビューをもとにした / 5 take time=時間がかかる)。現行canonical text使用、文言変更なし。日本語意味のTTS Styleのみ変更。英語KP・他segment変更なし。
3. 6 Prompt(逐語):
 - J3 現行Baseline: 落ち着いた、自然な話し言葉で。意味の流れ・強調点・転換に応じて表情豊かに抑揚をつけてください。演技がかった話し方は避けてください。
 - P1 最小修正版: 落ち着いた、自然な話し言葉で。意味の流れに応じて自然な抑揚をつけてください。感情を込めすぎず、演技がかった話し方は避けてください。
 - P2 意味伝達重視: 落ち着いた、自然な話し言葉で。日本語の意味が明瞭に伝わるよう、自然で控えめな抑揚で読み上げてください。感情的な強調や演技がかった話し方は避けてください。
 - P3 ニュートラル重視: 穏やかで自然な話し言葉で。声の調子をニュートラルに保ち、必要最小限の自然な抑揚で読み上げてください。特定の単語を感情的に強調せず、演技がかった話し方は避けてください。
 - P4 自然な会話調: 落ち着いた、親しみやすい自然な話し言葉で。普通の会話で短い言葉の意味を伝えるように、軽やかで無理のない抑揚をつけてください。大げさな感情表現や演技は避けてください。
 - P5 簡潔・淡々: 落ち着いた、明瞭で自然な話し方で。短い言葉の意味を簡潔に、控えめな抑揚で読み上げてください。感情を強く込めたり、語尾を不必要に強調したりしないでください。
 Promptは逐語使用。Fable/Sonnetが独断で修正しない。
4. 設計: 6 Style x 5 Phrase=30音声。J3はCoffee完成版既存音声をBaseline再利用可。P1〜P5は5 Phraseずつ生成=新規TTS原則25回。Voice・モデル・backend・生成設定をJ3と揃える。同じcanonical text。設定差は明記。Seed/既存結果が利用できれば再利用。必要なQAは行うが無関係なTrialはしない。実行前に費用見積、Trial予算規定と日次1,000円管理を守る。並列化: 独立作業は並列、同一成果物への競合書込・過剰同時API呼出は避ける。
5. 試聴ページ: 6 Styleを横並び比較できるシンプルなページ。J3/P1-P5比較可、日本語意味5件すべて掲載、個別再生、Phrase単位で6候補を並べる、Prompt全文確認可、完成版J3既存音声をBaselineとして区別、PC/スマホ再生可、実際のURLを報告。凝ったUI不要、ユーザー自身が比較・採否判断しやすいこと優先。
6. 品質評価: (1)感情表現の適切さ(2)自然さ(棒読みでないか)(3)明瞭さ(4)安定性(5 Phrase全体)。技術QAに加え可能な範囲でFableが相対比較。自動評価でユーザー聴感評価を代替しない。
7. 非対象: 正式J3(Family X)変更なし、Std Preview/Comment Style変更なし、Advanced音声変更なし、KP選定・gloss本文・canonicalization・再整合工程に触れない、Production runner・retry・fallback・regeneration変更なし、Coffee完成版MP3上書きなし、他進行中タスク/Day3-4と競合させない、隔離された新規artifact。
8. STOP/Status: 有料Trial予算上限・既存STOP規則厳守。予算超過・仕様変更・新たなユーザー判断が必要ならSTOP。分類はREJECTED/VALIDATED/USER_DECISION_REQUIRED。音声が生成できただけでVALIDATEDとしない。良好候補があってもユーザー試聴と正式採用判断なしにAPPROVED_FOR_PRODUCTIONへ変更しない。
9. 報告: 非エンジニア向け超サマリ先頭に、(1)完了状況・新規TTS数・実費 (2)試聴ページURL (3)6x5比較結果 (4)「すぐに」の改善状況 (5)自然さ・聞きやすさ (6)Fable推奨候補と理由 (7)未解決・ユーザー判断事項 (8)SSOT/Decision Log/Open Itemsへの記録。推奨が見つかってもProduction採用せず試聴ページ提示でSTOP。

## KPI provenance
J3 Baseline=reuse(Coffee完成版a2のmeaning_1〜5.wav)。P1〜P5=fresh(synthetic条件: Trial script経由)。客観指標=fresh(参考値)。E2E自己確認=No。

## 重要な前提確認
CFSA 01B観測: Std KP日本語意味5件の実使用Styleは FAMILY_X_ROLE_STYLE_JA(65字、sha ae68e3e6...)。ユーザーのJ3本文と実使用Prompt本文が逐語一致するか最初に確認。不一致なら差分を明記し(a)Baselineは実使用Prompt音声(b)ユーザー提示J3での新規生成が必要か(+5 call)をFable判断材料として報告(自分で決めずJ3新規生成は行わず、事実をRESULT_PACKETに記録して継続。P1〜P5は生成)。

## 事前指定Read一覧(要旨)
tts_generation_results.json(Baseline設定の正本) / keywords_canonicalized.json / B_ARTIFACT_OBSERVATION_01.md §3,§5 / er057既存Trialの生成・ページ実装 / user_test/coffee_pace_trial_02/index.html / er006_model_routing_contract_01.py / PM_GOVERNANCE.md 7-7,7-8 / REPORT_LEDGER.md 256-275。

## 出力先・手順
- 共有state不変の証明: Trial前後で禁止リスト各ファイルsha256を記録(evidence/shared_state_sha_before.json/_after.json)。
- 出力先: er057_output/std_kp_ja_style_trial_01/、試聴ページ user_test/coffee_std_kp_ja_style_trial_01/index.html(+mp3。J3 Baselineは完成版wavをcopyしてmp3化、原本不変)。
- 客観指標(参考値、合否基準にしない): 長さ、RMS dynamic range、F0 std/range(librosa/pyworld無ければ未測定)、無音比率。Style別に5 Phrase平均と分散。
- QA: 既存Trialで使った日本語ASR照合があれば同条件で実施(費用を見積に含める)。TTS失敗時retryは既存Trial script既定(最大2回)まで。

## 実行コマンド
- T-0: .venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-15_STANDARD-KP-JA-TTS-STYLE-TRIAL-01_01.md --json-out docs/pm/delegation_log/2026-10-15_STANDARD-KP-JA-TTS-STYLE-TRIAL-01_01_check.json
- STOP確認: .venv\Scripts\python.exe tools/stop_scope_check_01.py --managed-id STANDARD-KP-JA-TTS-STYLE-TRIAL-01 --run-dir er057_output/std_kp_ja_style_trial_01 --out er057_output/std_kp_ja_style_trial_01/stop_scope_check_01.json
- 生成: TTS_EXECUTION_MODE=STANDARD .venv\Scripts\python.exe er057_std_kp_ja_style_trial_01.py --style P1 --out-dir er057_output/std_kp_ja_style_trial_01 --budget-jpy 10 (P2〜P5同様、同時<=3。Baselineと同一model/voice/backend/speed/設定をtts_generation_resultsから読み取り固定、Prompt本文は逐語を定数に。生成前に--dry-runで設定と見積を出力しRESULT_PACKETへ記録)
- 客観指標・ページ: er057_std_kp_ja_style_trial_01.py --analyze --build-page --out-dir er057_output/std_kp_ja_style_trial_01 --page-dir user_test/coffee_std_kp_ja_style_trial_01
- 公開確認: curl -s -o NUL -w "%{http_code}" https://shimomura055.github.io/eigo-radio/user_test/coffee_std_kp_ja_style_trial_01/index.html (200でなければ再確認1回、だめなら「反映待ち」)

## 成果物
- er057_output/std_kp_ja_style_trial_01/TRIAL_REPORT_01.md: §0超サマリ/§1 Baseline設定とJ3一致確認/§2 生成結果/§3 6x5比較表/§4 「すぐに」客観指標変化/§5 Sonnet所見(聴感未実施明記)/§6 推奨候補案/§7 Status分類案/§8 SSOT文案/§9 共有state不変証明/§10 確認できなかった事項。
- user_test/coffee_std_kp_ja_style_trial_01/index.html。

## SSOT/Git
SSOT編集権なし(文案のみ)。明示add: er057_std_kp_ja_style_trial_01.py、er057_output/std_kp_ja_style_trial_01/、user_test/coffee_std_kp_ja_style_trial_01/、本ファイル(+_check.json)。RESULT_PACKET_SKJT1.mdはgitignore対象なら強制addしない。コミットメッセージ: 「STANDARD-KP-JA-TTS-STYLE-TRIAL-01 委任_01: Std KP日本語意味 6 Style x 5 Phrase比較Trial(J3 Baseline再利用+P1〜P5新規25 call、実費JPY<実測>)+試聴ページ user_test/coffee_std_kp_ja_style_trial_01。Production/正式J3/SSOT無変更、採用なし」。push to origin/main。

## 報告(RESULT_PACKET_SKJT1.md)
(1)T-0/STOP確認 (2)J3一致/不一致 (3)見積と実費・call数・失敗/retry・model_id/voice/backend (4)試聴ページURL(HTTP status) (5)6x5比較表要約と客観指標 (6)「すぐに」の変化 (7)推奨候補案・Status分類案 (8)共有state不変の証明 (9)SSOT文案 (10)commit hash・push・raw URL (11)確認できなかった事項 (12)逸脱。Fableは(2)(3)(4)(7)(8)を照合する。
