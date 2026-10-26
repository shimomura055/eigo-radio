## 管理ID

FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_01(Phase 0: ユーザー正式決定の保存・既存仕様照合・設計・Opus条件A依頼文・費用計画・test計画。実装なし・API 0)。並行Agent: FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01(所有=`docs/research/FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01/**`・`er121_output/family_y_voice_pause_trial_01/**`・`user_test/family_y_voice_pause_trial_01/**`・RESULT_PACKET_YVP1、有料TTS実行中、`er121_*`読取)。本委任の所有=`docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/**`、`docs/pm/delegation_log/2026-10-26_FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01_*`、`docs/pm/RESULT_PACKET_FZCW1.md`、`docs/pm/ACTIVE_TASK.md`、SSOT(`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/USER_DECISION_REGISTER_01.md`のみ。CURRENT_SPEC/REPORT_LEDGER/OPUS台帳は本委任では編集しない)。**本委任がSSOT編集権を持つ唯一のAgent**(8-Y)。

## 性質/到達上限Status/禁止事項

- 性質: Production Wiring案件のPhase 0(設計)。ユーザーが**APPROVED_FOR_PRODUCTION**を正式決定(下記原文)。到達目標はPRODUCTION_WIREDだが、本委任はPhase 0のみ(実装・有料run・Production code変更なし)。
- 到達上限Status(本委任): DESIGN_READY_FOR_OPUS(Opus条件Aレビュー待ち)。Phase 0でSSOTへ記録するStatus=OPEN-528をAPPROVED_FOR_PRODUCTION(ユーザー決定2026-10-26)+PRODUCTION_WIRED未達、と記す。**PRODUCTION_WIREDとは書かない。**
- 禁止: Production code(`er063_family_z_audio_01.py`、`er026_*`、`er011_*`、`er118_*`、ASR/Gate系)の編集禁止(Grep/Readのみ)/有料API 0(`.venv\Scripts\python.exe`起動禁止)/未承認のPrompt改変・感情分類方式変更・品質基準の追加や緩和の提案を「設計既定」にしない(必要なら判断候補として分離)/Family X/Yへの適用・変更を設計に含めない/Git禁止操作(`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・`reset --hard`・`checkout -f`・`git checkout -- <file>`)。共有SSOT(DECISION_LOG/USER_DECISION_REGISTER)はworktreeにCRLF全行差分があるため**HEAD blob+自hunkのみ**でcommit(`git diff --cached --stat`で確認)。
- 修正範囲の線引き(11-8): 本案件は承認済み新仕様の配線(範囲内=ユーザー決定の2節・3節を既存Z経路へ実装すること)。範囲外=ユーザー決定に無い受理面・閾値・方式の新設/拡大(例: 新しい品質基準、感情分類の変更、X/Yへの拡大、試行回数の変更、クールダウン時間の変更)。
- Opus独立技術レビューGate(11-3): **条件A該当**(Z正式経路のretry/fallback構造に新しい処理フロー[ctx→ctx→cooldown→従来方式]を加える。実装前にOpus必須)。本委任はその依頼文(`OPUS_REVIEW_REQUEST_01.md`)を作る。条件C(Production採用提案前)はユーザーが既に採用決定済みのため不要、配線完了判定時に条件Aレビューを再利用。
- 時間見込み: 全体60〜90分(ユーザー原文保存+仕様台帳20、既存経路照合25、設計+test/費用計画+Opus依頼文30、SSOT/commit 10)。並列化: 案件A(Y)と並列。本委任内は照合→設計の直列(設計が照合結果に依存)。
- 費用/日次: 当日(JST 2026-10-26)既使用JPY約123+案件A実費(進行中、Cap 150)/本委任見積JPY0/改善見込み高/承認区分: C(JPY0)。案件全体(Phase 1実装API 0+Phase 2 runtime evidence)の見積はBUDGET_PLAN_01で算定(出典ある単価のみ。Fable仮置きGuardrail=200円、300円超見込みなら事前承認が必要と明記)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし。Phase 2のコマンド案には`TTS_EXECUTION_MODE=STANDARD`を明示して書く)
T-3: 本委任はCapなし(JPY0)。案件全体のGuardrail文言はBUDGET_PLAN_01に次の定型で書く:「上限¥200(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」

委任文保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 634 --out docs\pm\delegation_log\2026-10-26_FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01_DELEGATION_01.md`(先頭が「## 管理ID」+「FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_01」でなければ630〜645を順に試し一致indexを記録)→`py docs/pm/tools/check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-26_FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01_DELEGATION_01.md --json-out docs\pm\delegation_log\2026-10-26_FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01_DELEGATION_01.md_check.json`。
ユーザー原文保存: 下記「ユーザー指示(原文)」節の本文(「# Family Z｜文脈・感情付きTTS＋Fallback 正式Production Wiring」から「…正式Productionの全経路で保証することです。**」まで)を一字も変えず`docs\pm\delegation_log\2026-10-26_FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01_USER.md`へ保存(先頭に`<!-- ユーザー正式決定原文(2026-10-26)。逐語。Fable委任_01同梱の写しから転記 -->`の1行可)。

## ユーザー指示(原文)

# Family Z｜文脈・感情付きTTS＋Fallback 正式Production Wiring

## 1. ユーザー正式決定

Family Zの「文脈・感情付きTTS」を正式採用する。

**Status：APPROVED_FOR_PRODUCTION**
**目標：PRODUCTION_WIRED**

対象はFamily Zのセリフ音声、Standard／Advanced両方。

Family X/Yには適用しない。既存のナレーション、Key Phrase、その他のTTS仕様も変更しない。

## 2. 正式採用するRetry／Fallback仕様

セリフ単位で以下を実行する。

**1回目：文脈・感情付きTTS**
- PASS → 採用
- NG → 即時Retry

**2回目：文脈・感情付きTTS**
- PASS → 採用
- NG → 10分クールダウン

**3回目：従来方式TTSへFallback**
- 文脈・感情情報を付加しない、従来の承認済みTTS指示・Styleを使用
- PASS → 採用
- NG → 既存のLocal Rewrite処理へ

Local Rewriteで解決できなければ、既存のHuman Review／STOP規則に従う。

**TTS総試行回数は初回を含め最大3回。** Fallbackを追加の4回目として扱わない。

Local Rewriteも既存の回数上限・安全条件を維持し、無制限な再生成を発生させない。

## 3. Production実装の必須条件

### ① Trial方式の正確な移植

今回の『猿の手』『走れメロス』全編Trialで使用した文脈・感情情報生成方式とTTS指示を、承認済み仕様として正式Productionへ移植する。

未承認のPrompt改変、感情分類方式の変更、品質基準の追加・緩和は行わない。

Trialの一時コードを単に呼び出すのではなく、正式初回Production経路として機能させる。

### ② Retry／Fallbackの一貫性

以下の経路すべてで同一仕様を保証する。

- 初回Production生成
- retry
- fallback
- regeneration
- resume
- 中断後の再開
- Local Rewrite
- Human Review Lock

失敗が発生した場合も、残りの試行回数・状態・生成方式を正しく引き継ぐこと。

特に、再開によって1〜2回目の文脈・感情付きTTSを不必要に再実行したり、3回の上限を超えたりしないこと。

### ③ 従来方式への正確な復帰

3回目のFallbackでは、今回の文脈・感情情報をTTS指示から完全に除外する。

従来方式のVoice、Style、速度、発音制御、品質検査を維持する。

文脈・感情付き方式の一部設定が残り、従来方式と異なる音声になることを防ぐ。

### ④ 既存の品質・安全仕様

以下を維持する。

- ASR Primary／Secondaryの承認済み判定規則
- 発音・内容一致検査
- ASR表記揺れへの救済
- Local Rewrite／Natural English QA
- Human Review Lock
- STOP条件
- 音声の組立・音量・速度に関する承認済み仕様

特に、ASRの表記違いだけを理由に不要なTTS再生成を行わないこと。

## 4. Trialで判明した問題の扱い

全編Trialでは、次の問題が観測された。

- 一部セリフの不自然な話速
- 長いポーズ
- 地の文とセリフの音量差
- 一部の声の高さの不安定さ
- 『走れメロス』Standardの比較音量条件不一致
- 53件中1件のASR／QA不合格

これらを隠さず、Production品質への影響を確認する。

既存の承認済みValidator・組立・品質条件に反する問題は、承認範囲内で是正する。

ただし、Trial結果を理由に独自の新しい品質基準を設けたり、承認した文脈・感情方式を変更したりしない。

実質的な仕様変更が必要なら、理由とQCD影響を示してUSER_DECISION_REQUIREDで報告する。

## 5. 量産単価・QCD

**Family Z専用のコスト増として管理する。Family X/Yは変更しない。**

全編Trial報告の追加原価推計は＋1.8〜3.3円／記事セットだったが、これは今回のFallback仕様を反映した確定値ではない。

Production実装時に、以下を分けて算定すること。

1. 文脈・感情情報生成の追加費用
2. 文脈・感情付きTTSの費用差
3. Retry／Fallbackの発生率と期待費用
4. Local Rewrite・ASR追加費用
5. Family Zの記事セットあたり総量産単価
6. 制作時間への影響

70円／記事セットの目標を継続する。品質を維持できる範囲で、情報生成の再利用・キャッシュ・不要な再生成防止によって原価を最適化する。

**品質 ＞ Delivery ＞ 量産単価。**

費用削減のために承認済み品質を下げないこと。

## 6. 検証・受入条件

少なくとも次の動作を確認する。

| ケース | 期待動作 |
|---|---|
| 1回目PASS | 文脈・感情付き音声を採用 |
| 1回目NG、2回目PASS | 即時Retry後に採用 |
| 1・2回目NG、3回目PASS | 10分クールダウン後、従来方式で採用 |
| 3回ともNG | Local Rewrite／Human Review／STOPへ正しく移行 |
| retry途中で中断・再開 | 回数・方式を維持 |
| X/Yの通常TTS | 一切変更なし |

Mockテストに加え、正式Production runtimeで文脈・感情付き方式が実際に発火した証拠を取得すること。

Fallbackは3回目まで偶発的に失敗するのを待たず、強制NGによるテストで遷移を検証してよい。ただし、Mockだけで通常経路全体をPRODUCTION_WIREDと判定しないこと。

実際の正常経路・Fallback経路を区別して証拠を記録する。

Fableは独立して設計、コード、正式実行経路、回帰テスト、runtime evidenceを照合する。

## 7. SSOT・Git・Closeout

以下を更新する。

- CURRENT_SPEC
- DECISION_LOG
- OPEN_ITEMS
- 必要な設計・runtime evidence
- Git commit／push

今回の正式採用をFamily Z専用仕様として記録する。

旧方式は3回目のFallbackとして利用できるよう維持し、新方式が後続経路で参照されない等のDangling Referenceを防ぐ。

完了報告では、Family Z Standard／Advancedそれぞれについて、正式初回生成・retry・fallback・resume・QA・実音声・コストを明示すること。

**すべてのGate条件を満たして初めてPRODUCTION_WIREDと判定する。**

未確認事項がある場合は、完了とせず残るOpen Itemと解消条件を報告すること。

## 8. 実行方針・STOP

既存の承認済み作業・日次予算内で、独立作業を並列化して速やかに進める。

不要な追加Trialや磨き込みは行わない。

重大な品質・安全問題、予算超過見込み、承認範囲外の仕様変更が必要な場合はSTOPし、判断事項を整理する。

**今回の最重要目的は、Family Zで文脈・感情付きTTSを標準方式とし、2回失敗した場合だけ、10分クールダウン後の3回目に従来方式へ戻すこと。そして、その動作を正式Productionの全経路で保証することです。**

## KPI provenance欄

該当なし(Phase 0。費用見積の単価はTrial実測=reuse、出典行を明記)。

## Opus台帳更新

関連: `docs/pm/OPUS_FINDINGS_LEDGER.md`のOF-FZFE-M-1〜M-8/R-1〜R-9(全編Trial時のOpus指摘、Grep `OF-FZFE`)。本委任では台帳を編集せず、DESIGN_01の§「Opus既存指摘の引継ぎ」でM-1(NG音声混入遮断)・M-2(_original.wav)・M-4(書込ガード)・M-5(組立後3点assert/headroom)・M-6(グローバル依存排除)・M-8(NG clip方針)がProduction設計でどう扱われるかを1行ずつ記す。

## Fableからの前提・既知事実(鵜呑みにせず照合)

- Trial実装: `er118_fz_full_episode_trial_01.py`(サブコマンド`llm`/`gen`/`assemble`/`analyze`/`page-all`、`use_case`context manager、`generate_with_a2_slowdown_outer_loop`、`redirect_production_sinks`[er113]、`er109_xz_scope_01.family_scope("Z")`、`er078_secondary_run_scope.with_secondary_run`、`run_assembly`/`build_entry`は`er063_family_z_audio_01.py`から)、Round 1/2 module `er118_fz_dialogue_context_tts_trial_01.py`(CONTEXT blockをStyleへ、EMOTION_DEVELOPER rule 1-10、leakage check、ALLOWED_NAMES per work[猿の手で`whites`追加]、`PHASE1_GO.json` cap guard)。感情情報=`er118_output/fz_full_episode_trial_01/<work>/<level>/llm/emotion_review.json`。**Trialでは感情情報53件をFableが目視でaccept/discardした**(Round 2で1件discard、全編で12件がALLOWED_NAMES不足で機械DISCARD→allow-list追加で再実行)。Productionではこの目視レビューは存在しないため、Trial内の決定論チェック(leakage/allow-list/rule 1-10)で自動受理できるか、できない場合の扱い(その文は従来方式で生成する等)を設計し、**新しい品質基準を作らずに**閉じる方法を示す。閉じられない場合は判断候補として分離。
- Trial結果: 53 clip、初回OK 52(厳格51)、NG 1(melos a2 part3_c10)、k_ctx(ctx方式TTS費用比)1.057、Δ+1.80〜+3.26円/set、約9.7秒/clip。観測された問題: 猿Adv part2_c11 話速0.56×、新規長ポーズ(猿Std part2_c8/メロスStd part3_c4)、境界RMS>3 dB 20/98(最大+9.64 dB メロスStd part3_c8)、F0 SD上昇(猿Adv mr_white/mrs_white、メロスAdv melos)、M-5(3) headroom.scalar不一致(24k→48k変換後peak 0.9834/0.998→Production安全弁[閾値0.98]作動。メロスStd=比較条件不成立)。関連文書: `docs/research/FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01/{DESIGN_02,PREREGISTERED_CRITERIA_02,OPUS_REVIEW_01,EVAL_01,TRIAL_RESULT_01,BUDGET_LOG_01}.md`。
- Z正式経路: `er063_family_z_audio_01.py`(セリフclip生成・組立)、runner `er026_*`(正式run例=`er026_output/family_z_production_e2e_01/the_monkeys_paw/run_sf_prod_01`、`…/melos/run_e2e_06`)。retry/Local Rewrite/HR Lock/STOPはER-011 cascade(`er011_*`、`er011_output/attempt_history.jsonl`、`human_review_queue.jsonl`、TTS上限3回→HR Lock→Gate BLOCK)。ASR Primary/Secondary・OPEN-517 F1+F2・E3/E4適用済み。**重要照合点**: 現行cascadeで(a)試行回数の数え方(初回を含め3回か)、(b)Local Rewriteが現在どの試行の後に挟まるか(ユーザー仕様では3回目NGの後)、(c)クールダウンの既存概念の有無、(d)resume時にattempt状態をどこから読むか(attempt_history/`tts_generation_results.json`)、(e)a2減速外側ループ(`generate_with_a2_slowdown_outer_loop`)が試行回数にどう数えられるか。ユーザー仕様と現行cascadeの差分を表にし、「ユーザー仕様どおり実装可能」「既存cascadeの順序変更が必要(=判断候補)」を分ける。
- 費用単価の出典候補: `docs/research/FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01/BUDGET_LOG_01.md`(実費・clip単価)、`er009_n1_routing_governance_10_actual_model_cost.py`(モデル単価)、Z正式run `raw_usage_log.jsonl`。推定値を費用表に使わない(未確認は「未確認」)。

## 事前指定Read一覧

1. `docs/research/FZ-DIALOGUE-CONTEXT-FULL-EPISODE-TRIAL-01/DESIGN_02.md` 全文(Trial設計=移植元)、`OPUS_REVIEW_01.md` M-1〜M-8節、`TRIAL_RESULT_01.md` §結果表・問題一覧、`BUDGET_LOG_01.md` 全文。
2. `er118_fz_full_episode_trial_01.py`: Grep `def |CONTEXT|EMOTION|style|allow|leak|use_case|slowdown|redirect|family_scope`→該当関数(全文Read禁止、ただし`gen`の生成関数と感情情報→Style合成部は全体)。
3. `er118_fz_dialogue_context_tts_trial_01.py`: Grep `EMOTION_DEVELOPER|CONTEXT|ALLOWED_NAMES|leak|build_style|def `→該当範囲。
4. `er063_family_z_audio_01.py`: Grep `def |style|retry|attempt|local_rewrite|human_review|STOP|cooldown|sleep|resume|tts_generation_results|dialogue|speaker`→生成・retry・組立の該当範囲。
5. ER-011 cascade: Glob `er011_*.py`→Grep `attempt|max_attempts|local_rewrite|cooldown|human_review|lock|resume|STOP`→該当範囲(`attempt_history.jsonl`の行schemaも1行Readで把握)。
6. `er026_*`runner: Grep `er063|tts|resume|regenerate|--stage`→呼出箇所±20。
7. `er109_xz_scope_01.py`・`er113_*`(sink redirect)・`er078_secondary_run_scope.py`: 先頭docstring+公開関数のみ。
8. SSOT: `CURRENT_SPEC.md` Grep `Family Z|セリフ|dialogue|ER-011|Local Rewrite|Human Review Lock|a2減速|OPEN-517`→Z音声・retry関連節±20行。`OPEN_ITEMS.md` Grep `OPEN-528|OPEN-516|OPEN-511`。`DECISION_LOG.md` 先頭40行(書式)。`docs/pm/USER_DECISION_REGISTER_01.md` Grep `OPEN-528`。
9. `docs/pm/PM_GOVERNANCE.md` Grep `11-7`(限定例外: 既定OFF flag等)、`11-8`、`15-8`(Production 1生成セット総原価)。
10. `docs/pm/PM_BRIEF.md` Grep `ACTIVE_TASK固定ヘッダ`。

## 事前指定Grep一覧+追記位置・更新位置の手順

- OPEN_ITEMS.md: `OPEN-528`行末尾へ追記「2026-10-26 ユーザー正式決定: APPROVED_FOR_PRODUCTION(Z限定・Std/Adv・ctx→ctx→10分cooldown→従来方式fallback・総3回・以後Local Rewrite→HR/STOP)。原文=docs/pm/delegation_log/2026-10-26_FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01_USER.md。Production Wiring=FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01(Phase 0完了、PRODUCTION_WIRED未達)」。新規OPEN行は作らない(OPEN-528を本案件の追跡に使う)。最大番号はOPEN-530(KP)まで使用済み。
- DECISION_LOG.md: 新規エントリ「2026-10-26 | FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_01(ユーザー正式決定) | Family Z文脈・感情付きTTSをAPPROVED_FOR_PRODUCTION(ユーザー2026-10-26、原文=…USER.md)。仕様=§2/§3逐語要約。目標PRODUCTION_WIRED(未達)。X/Y不変。Opus条件A実施予定。」を既存書式で追加。
- USER_DECISION_REGISTER_01.md: OPEN-528を「UDR」区分から「判断済み(APPROVED_FOR_PRODUCTION、2026-10-26)」区分へ移動/追記。
- ACTIVE_TASK.md: 固定ヘッダで上書き(管理ID=FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_01/並行=FAMILY-Y-VOICE1-PAUSE-CAUSE-TRIAL-01(有料Trial中)/UDR-blocking=OPEN-526(X HR選択+候補数+救済方式OPEN-529)・OPEN-527(Y分割方式・Voice 1)・Chunk監査Std拡張(番号はFable確定)/APPROVED未配線=OPEN-528(Z ctx TTS、Phase 0)/当日費用=2026-10-26 約123+案件A実費/1,000)。

## 実行コマンド全文

- Production不変確認(作業後): `git status --short -- er063_family_z_audio_01.py er118_fz_full_episode_trial_01.py er118_fz_dialogue_context_tts_trial_01.py er026_family_z_production_runner_01.py`(ファイル名はGlobで実在名に置換して実行。新規差分なし)。
- 共有SSOTのhunk限定commit(DECISION_LOG/UDR): `git show HEAD:DECISION_LOG.md > %TEMP%\dl_head.md`→自hunk適用→`git hash-object -w <file>`→`git update-index --cacheinfo 100644,<blob>,DECISION_LOG.md`→`git diff --cached --stat`で自hunkのみ確認。
- secret grep: `git diff --cached | findstr /R /C:"sk-[A-Za-z0-9]" /C:"AIza[A-Za-z0-9_-]" /C:"BEGIN PRIVATE KEY"`(0件。委任文内の検索パターン文面は除外)。

## 成果物(`docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/`)

1. `SPEC_LEDGER_01.md`(+`spec_ledger_01.json`): ユーザー原文§1〜§8を要求項目に分解(ID・原文逐語・実装先候補・検証方法・Status列)。§6の受入表6ケースを必須testとして登録。
2. `EXISTING_SPEC_CHECK_01.md`: 21節A/B/C分類(本件=ユーザー承認済み新仕様の配線)。現行Z経路(初回/retry/fallback/regeneration/resume/Local Rewrite/HR Lock/STOP)の動作をファイル:行で表にし、ユーザー仕様との差分表(「そのまま実装可」/「既存順序の変更が必要=判断候補」/「既存仕様の維持で足りる」)。Trial固有の一時機構(redirect_production_sinks、PHASE1_GO、use_case、Fable目視レビュー、Trial出力dir)のうち**Productionへ持ち込まないもの**と、**正式経路として作り直すもの**の一覧。
3. `DESIGN_01.md`: (a)感情・文脈情報生成の正式経路(入力=Z本文・話者・前後セリフ、Prompt/モデル=Trialと同一[sha固定]、出力の保存先=runディレクトリ、再利用/キャッシュ条件[本文sha・レベル・話者で再利用、再生成しない条件]、決定論チェックによる自動受理と不受理時の扱い) (b)TTS指示合成(Trialと同一のCONTEXT block、従来Styleとの合成順序、fallback時に完全除外されることのコード上の保証[合成関数の引数で`context=None`なら従来とバイト同一のStyle文字列になることをtestで固定]) (c)retry/fallback状態機械(attempt 1 ctx→NG→attempt 2 ctx即時→NG→cooldown 600秒→attempt 3 従来→NG→Local Rewrite→HR/STOP。状態の永続化先・resume時の復元・a2減速外側ループとの関係・HR Lock・STOP sentinelの毎attempt確認・cooldown中のSTOP/中断の扱い) (d)X/Y不変の保証(Z scope限定の入口、X/Y経路のStyle/attemptがバイト同一であるtest) (e)Trial問題(§4の6項目)のProduction上の扱い=既存Validator・組立・品質条件で検出/是正されるか、されないならどの承認済み条件に反するか/反しないか(新基準は作らない。必要なら判断候補) (f)Opus既存指摘M-1/M-2/M-4/M-5/M-6/M-8の引継ぎ (g)Dangling Reference防止(旧方式の参照先・呼出名の維持) (h)段階計画: Phase 1=実装+offline test(API 0)、Phase 2=runtime evidence(正常経路: Z 1作品Std/Adv正式run、fallback経路: 強制NG注入での遷移[本番Gateを迂回しない注入方法=test専用env/flagで1 clipのASR判定を強制NGにする等、実装案を明示]、resume: 中断再開)。
4. `TEST_PLAN_01.md`: §6の6ケース+Style完全除外test+X/Yバイト同一test+cooldown(時間をmock)+resume+上限3回超過禁止+Local Rewrite上限維持。遮断harness下、`py`。
5. `BUDGET_PLAN_01.md`: §5の6区分を分け、出典ある単価のみで見積(未確認は「未確認」)。Phase 2のrun費用(Z 1作品Std/Adv正式run+強制NG fallback+resume)を見積り、Guardrail 200円の定型文。300円超見込みならその旨を先頭に。
6. `OPUS_REVIEW_REQUEST_01.md`: 条件A依頼文(重要論点: 状態機械の網羅性と再開時の整合、fallback時の完全除外保証、X/Y無影響、感情情報の自動受理の歯止め、強制NG注入がGate迂回にならない設計、Trial観測問題の扱い、費用)。
7. `OPEN_TRACKING_01.md`: 残Open Item・判断候補(ユーザー判断が必要なもののみ)。
8. `docs/pm/RESULT_PACKET_FZCW1.md`。

## SSOT追記文

上記Grep節のとおり(OPEN-528追記・DECISION_LOGエントリ・UDR移動)。CURRENT_SPECはPhase 1/2完了時に別委任で更新(文案はDESIGN_01末尾に用意)。

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: あり(OPEN_ITEMS.md/DECISION_LOG.md/docs/pm/USER_DECISION_REGISTER_01.md)。CURRENT_SPEC/REPORT_LEDGER/OPUS台帳=なし。
- 明示add: `docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/**`、`docs/pm/delegation_log/2026-10-26_FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01_{USER,DELEGATION_01}.md`+`_check.json`、SSOT 3ファイル(自hunkのみ)。
- commit: `git commit --only <paths…> -m "FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_01: ユーザー正式決定(APPROVED_FOR_PRODUCTION)の保存・既存Z経路照合・設計/test/費用計画・Opus条件A依頼文(Phase 0、API 0)"`→`git push origin HEAD:main`(non-fast-forwardは`git fetch origin`→`git merge --no-edit origin/main`→再push。競合は両方残してSTOP)。

## 報告(RESULT_PACKET項目)

(0)T-0結果・index (1)結論(ユーザー仕様を既存Z経路へそのまま実装できるか。できない点=判断候補の一覧、それぞれ理由・影響・代替案) (2)差分表の要約(現行cascade vs ユーザー仕様) (3)感情情報の自動受理設計の要点と、新基準を作らずに閉じられるか (4)fallback完全除外の保証方法 (5)強制NG注入の設計(Gate迂回でないことの説明) (6)費用見積(6区分、出典、Phase 2見積、Guardrail、300円判定) (7)Trial観測問題6項目の扱い表 (8)SSOT追記行・自hunk証拠 (9)commit/push・raw URL (10)一覧外Readと理由 (11)Fable向け懸念(Opusに重点確認させたい点3つ以内)。最終行に要約10行以内。