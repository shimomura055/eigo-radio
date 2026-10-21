# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 委任_03(緊急調査: Std Full Story第2部で発動したFallbackについて、承認済み仕様・承認履歴・実装・今回runの実行証拠の一致を確認する。**調査のみ、API 0・TTS/ASR/LLM呼出0・Fallback音声の採用保留・HR承認操作なし**)。並行agentなし。

## 性質/到達上限Status/禁止事項
- 性質: 調査+事実整理(ユーザー緊急指示2026-10-21)。到達上限=調査報告(分類A/B/Cの材料提示。最終分類はFable)。
- 禁止: 新規TTS/ASR/LLM呼出(既存wavへの追加ASRも禁止)、`record_human_approval`、Lock/state/wav操作、Production code/Prompt/Style変更、新Style採用、CURRENT_SPEC/DECISION_LOG/OPEN_ITEMSの全文読込(Grep→該当行のみ)。既存承認範囲内の明確な実装不具合を見つけた場合は、修正案と無課金testの計画を報告し、**実装はFable判断後**(今回は報告止まり)。
- 費用JPY0。

## 固定ブロック
E-1/D-1/G-1/F-1: 標準。T-0: 本委任文を`docs/pm/delegation_log/2026-10-21_FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01_委任_03.md`へ逐語保存(extract tool、N=「PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 委任_03」を含む最新index)、check結果1行。T-2: TTSなし。

## ユーザー指示(原文・2026-10-21、全文)
`docs/pm/delegation_log/2026-10-21_FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01_FALLBACK-INVESTIGATION_USER.md`へ逐語保存(先頭に`# ユーザー指示原文(2026-10-21)`と`管理ID: FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 委任_03(Fallback調査)`の2行、以降一字一句変えない。文字数・sha256[本文のみ]を報告)。
--- 原文ここから ---
# 緊急：Family X Full Story Fallbackの仕様・承認・Production実動作調査

## 目的

記事A「収入と性格」のStandard Full Story第2部で発動したFallbackについて、承認済み仕様と実装・実行結果が一致しているか確認する。

**調査が完了するまで当該Fallback音声の採用は保留。新たなTTS生成は行わない。**

## 1. 既存仕様と承認履歴

ChatGPTによるRepo確認では、CURRENT_SPECに以下の記載が存在する。

- N01は正式承認されたFull Story通常Style。
- Fallback takeはN01ではない。
- 2026-09-28のFAMILY-X-02では、Fallbackのminimal instructionに関して `FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]` を使う記載がある。

以下を照合する。

1. 当該Fallbackを承認したユーザー判断の日時・内容・適用範囲。
2. N01採用時に旧Fallbackを維持する判断があったか。
3. 現在のCURRENT_SPECとDECISION_LOGで、Fallbackの条件・Style・Human Review要件が整合しているか。
4. 未承認仕様や、廃止すべき旧経路へのDangling Referenceがないか。

## 2. 記事Aの実行証拠

Std Full Story第2部について、実際のログから次を確認する。

- 通常Take 1／2とFallback Takeの使用モデル・Voice・Prompt／Style全文またはSHA
- 各TakeのASR結果と不合格理由
- Fallbackが発動した正確な条件
- Fallbackで合格した検査と、人間承認が必要になった理由
- 減速処理・再検証の結果
- 通常Takeが本当に発音不良だったのか、ASRの誤認識・表記揺れだったのか

コード上の想定ではなく、今回のrunの証拠を提示する。

## 3. Fable独立評価

以下のいずれかに分類する。

**A：承認済み仕様どおり**

Fallbackは適法な既存Production経路であり、今回のHuman Reviewも仕様どおり。

**B：仕様・記録の不整合**

過去に承認された処理だが、CURRENT_SPECやN01との関係が不明確。仕様を勝手に変えず、事実関係と記録上の不足を整理する。

**C：未承認・不正な経路**

ユーザー承認のないFallback仕様がProductionで発動。影響範囲・再発防止策を報告し、ユーザー判断前に仕様変更・正式採用しない。

既存承認範囲内の明確な実装不具合は自律的に修正・無課金テストする。ただし、新仕様・新Styleの採用は禁止。

## 4. 報告

最優先で、次の4点を簡潔に報告する。

1. **Fallbackの実際のStyle／モデルは何か。**
2. **誰が、いつ、何を承認したのか。**
3. **なぜN01ではない音声がProduction候補になったのか。**
4. **今回の音声は承認候補として有効か、それとも仕様上の問題があるか。**

調査完了までは、記事AのHuman Review判断を求め直さない。記事B等の独立した完成作業は妨げない。

Fableの独立確認を必須とし、SSOT／Git更新が必要なら適切に反映する。新しい有料Trialは実施しない。
--- 原文ここまで ---

## Fableが事前に確認済みの手がかり(出発点。鵜呑みにせず原文で再確認)
- CURRENT_SPEC.md L1791-1809(FAMILY-X-02、2026-09-28: fallback[minimal instruction]発火時に`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`="natural, clear, conversational"を実配線。「以前は未配線のまま長いlegacy instructionを転用」。修正3回目=Opus L2所見反映、shell固定segmentもFlash-Lite時は同style)。
- CURRENT_SPEC.md L2756(2026-10-13 N01 `APPROVED_FOR_PRODUCTION`: 「fallback takeはN01ではない」「N01は判定緩和を含まない(ASR判定・速度/ポーズ基準・retry/fallback/STOP条件は無変更)」「M3 assembly gate」。Coffee Std full_story_part2がfallback takeで未完=OPEN-343)。L2762(2026-10-14: Coffee part2は**N01標準経路1回目で再生成**して完成=fallback takeを承認せず再生成で解決した前例)。
- test `er019_family_x_style_profile_01_n01_test_01.py:58`(N-8「fallback takeはN01ではない」)、`er019_family_x_variable_role_style_wiring_01_test_01.py:203-204`(FALLBACK定数=["natural, clear, conversational","clear"]不変)。
- DECISION_LOG.md: `FAMILY_X_ROLE_STYLE_EN_FALLBACK` L11285/L11690/L11695/L11958/L12098(2026-09-27〜28前後)。
- M3 Gate: `er019_family_x_style_profile_01.py:628-633(_approved)、658-725`、`record_human_approval`=`er003_v1_n3_01_assemble.py:96-117`。MEY E2E-02(#128、2026-10-21)はStd JA comment_2のHR Lock(標準2回+fallback1回とも不合格→HUMAN_REVIEW_REQUIRED)をユーザー試聴承認で解決した前例(JA、Variant Layer読み不一致)。今回はEN Full Storyのfallback take**合格**→M3 Gate(fallback使用=人間承認必須)で停止。両者の違いを明確に。
- 今回run証拠: `er019_output/family_x_audio_production_wiring_01/paycheck_personality__run_pp_01/a2/audit/tts_generation_results.json`(`segments.full_story_part2.standard_attempts_log[0..1]`、`fallback_attempts_log`、cascade_steps)、`a2/audit/style_profile_gate.json`、`audit/style_profile.json`(profile=既定n01?)、`raw_usage_log.jsonl`(model/voice)、`a2/narration/full_story_part2.wav`、attempt wavが残っていればそのpath、`er011_output/attempt_history.jsonl`該当行、`docs/research/FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01/E2E_PLAN_01.md` §4/§5。

## 調査手順(API 0)
S1. **承認履歴**(ユーザー§1の1〜4): DECISION_LOG/CURRENT_SPEC/USER_DECISION_REGISTER/delegation_log USER原文をGrepし、(a)fallback経路(技術的失敗時のminimal instruction→FALLBACK[0])を承認したユーザー判断の日時・管理ID・原文の該当文・適用範囲(どのsegment/role/backend)、(b)N01採用(2026-10-13)時にfallback維持を明示した判断の有無(「retry/fallback/STOP条件は無変更」の原文と、fallback takeの扱い[M3 Gateで人間承認必須]を誰が決めたか)、(c)fallback takeに対する**正式な解決手順**がSSOTで定義されているか: (i)人間承認(`record_human_approval`)で採用、(ii)N01で再生成(Coffee前例)、(iii)未定義。それぞれの出典行。(d)Dangling Reference: 旧「長いlegacy instruction」経路・P8/PD06/N01の置換関係・`FAMILY_X_ROLE_STYLE_EN`追跡定数とprofile機構の関係で、現行Productionに残る未承認/廃止済み参照がないか(実装Grep: `er003_v1_repro01_main_generate.py:578`、`er003_v1_sing01_voice01_generate.py:189-194`、`er003_v1_sing01_point_headings_aoede.py:99`、runnerのfallback分岐)。
S2. **今回run証拠**(ユーザー§2): tts_generation_results.json等から表にする: attempt番号/経路(standard|fallback)/model/voice/style文言(全文)+sha256/N01 sha(d1956c91…)との一致/temperature等/生成時刻/wav path(存在有無)/減速前後duration/一次ASR(model、転写全文)/二次ASR(Azure、転写全文)/統一judge結果と理由コード/semantic_equivalence結果/採用可否。Fallback発動の正確な条件はコード(`er003_v1_n3_01_tts_generate.py`等のcascade、standard attempt回数上限)と実ログの両方で示す。「fallbackで合格した検査」=一次ASR PASSのみか、二次も含むか、減速後再検証(NORMALIZED_MATCH)の内容。
S3. **発音不良かASR誤認識か**(新規API禁止のため既存証拠のみ): attempt1/2の一次/二次ASR転写とcanonicalの差分語を列挙し、各差分を「同音・活用/縮約(use to/used to, turn/you'd turn)」「句読点・抑揚(!/?)」「固有名詞化誤認識(Ernie Moore)」「その他」に分類。統一judgeがTRUE_CONTENT_MISMATCHとした判定根拠(judgeの出力テキスト)を引用。**音声そのものの良否は未試聴=未確定**と明記し、断定しない。attempt1/2のwavが残っているか(残っていればHRページへの掲載済み有無)。
S4. **分類材料**: ユーザー§3のA/B/Cそれぞれに該当しうる事実を整理(Sonnetは分類を提案してよいが「判断候補」表記、最終はFable)。特に「fallback takeを人間承認で採用する経路」がユーザー承認済み仕様か、それとも実装上存在するだけかを明確に。Coffee前例(再生成で解決)とMEY前例(JA HR Lockを承認)との整合。
S5. **記録**: `docs/research/FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01/FALLBACK_INVESTIGATION_01.md`に全証拠(表・出典行・引用)。SSOTの書換えはしない(Fable判断後)。OPEN-432行末に「委任_03: Fallback調査中(採用保留)」1文、REPORT_LEDGER 1行、ACTIVE_TASK先頭追記。secret scan→明示add→commit(`FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 委任_03: Full Story Fallback仕様・承認・実行証拠調査(API 0、採用保留)`)→`git push origin HEAD:main`。

## 報告(docs/pm/RESULT_PACKET_FXPP3.md 上書き)
先頭にユーザー§4の4点を各2〜4行で(1.Fallbackの実際のStyle全文/sha/model/voice 2.承認の主体・日時・管理ID・適用範囲[原文引用] 3.なぜN01でない音声が候補になったか[cascadeの条件と実ログ] 4.承認候補としての有効性: 仕様上の根拠と不足[判断候補])。続けてS1〜S4の詳細、FALLBACK_INVESTIGATION_01.mdへのpath、commit hash・raw URL、T-0/原文sha256、4行判定。