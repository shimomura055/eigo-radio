## 管理ID

PM-CLOSEOUT-CONSOLIDATION-132(4TYPE補完完成[Trend/Discovery]+Family C Trial-09+Voices OPEN-151 -02結果統合+PM運用方針追記)
並行タスク衝突確認: 並行タスクなし。本タスクがGit・SSOT・ACTIVE_TASK・RESULT_PACKET.mdを扱う唯一のタスク。

## 性質/到達上限Status/禁止事項

- 性質: Git記録・SSOT反映・REPORT作成・比較ページ更新・doc修正のみ。**API呼び出し禁止(費用¥0)**。Production/Trialコードの変更禁止。
- 反映する事実(Fable照合済み、Sonnet自己評価でなく以下の値を使う):
  - **Trend**(`docs/pm/RESULT_PACKET_4T_TREND_COMPLETE.md`): 完成(OK)。A2 503語 Fact Checker=REVIEW_REQUIRED(non-blocking)、Ledger Deviation MAJOR1→Local Rewriteで解消LEDGER_COMPLIANT。B1B 479語 PASS/LEDGER_COMPLIANT(MINOR1)。Ledger追記F008_FIX2(Galaxy XRヘッドセット=Android XR最初のデバイス・既提供中、source: android.com/xr FAQ、blog.google Galaxy XR記事)。Cross-Level矛盾なし。Trend Production 1生成セット総原価=¥174.03(Research¥48.73+run2¥75.25+本run¥50.05)。**要修正**: `er014_output/four_type_observation_01/trend/cross_level_consistency.md`はLocal Rewrite前のA2文(「The camera-and-optional-display version is a separate product tier.」)を引用しており最終A2に存在しない。最終`trend/reader_facing_article.txt`(503語)・`reader_facing_article_b1b.txt`から引用し直して突合表を書き直す(結論「矛盾なし」は最終テキストでも成立: A2はカメラ版に言及しない=省略であり矛盾ではない。語数も503語へ訂正)。
  - **Discovery**(`docs/pm/RESULT_PACKET_4T_DISCOVERY_COMPLETE.md`、`_2.md`、`_3.md`): A2記事OK(final QA PASS/LEDGER_COMPLIANT)、B1B記事OK(PASS/LEDGER_COMPLIANT)、Ledger修正F002(視聴者数を断定しない、Verification AMBIGUOUS)・F009(chosen solitude→Study 4限定)・F011(46名が正、41は別研究)・F014(本文側の一般化修正)、No Jargon 0/0、Cross-Level矛盾なし、Key Phrase A2=OK(lowest-arousal state/feel louder than speech/outside stimulation/thinking for pleasure/nothing to do but think ※`_2.md`8節の「A2=agency/…」はB1B候補との取り違え誤記)、**Key Phrase B1B=未完成**(確定本文へ2回ともKEY_WORDS_STRUCTURE_INVALID、「have agency」の語彙動詞haveを有限助動詞ブロックリストが誤検知する疑い→Validator変更はProduction QA変更でユーザー判断)。Discovery Production 1生成セット総原価=¥463.27。プロセス問題2件(記録のみ): 初回driver `fix_fact_blocks()`が`resolved`未確認でdiff QA不合格rewriteを適用(CONT1でoperator escalation+diff QA PASSにより上書き解消済み)/Key Phrase retryスクリプトが同一dir上書きでcall1詳細を消失(2回再発)。
  - **Voices**(`docs/pm/RESULT_PACKET_VOICES_VAR2.md`、commit `7aefedb2`/`9d9384c0`済み): PARTIAL(15項目中14✓、未充足=項目7 clean 2V evidence: Analytical Leakage Check voice_b/tensionが3attempt上限後も残存。Fact Checker PASS/Ledger COMPLIANT/Comment Contract接続✓/Gate 2V/3V一般化✓)。Voices総原価¥140.39。SSOT・Gitは-02タスクで反映済み → 本タスクでは再編集せず、CONS-132エントリと索引で参照するのみ。
  - **Family C Trial-09**(`docs/pm/RESULT_PACKET_FC9.md`、`EDITORIAL-FUTURE-FAMILY-C-HOME-ROBOTS-EPISODE-SPEC-TRIAL-09_REPORT.md`): VALIDATED(Trial上限)。Audio Validation Gate PASS 38/38、4分18秒、2-voice(narrator=Aoede/robot=Charon)、Preview/Key Phrase5件/Support 2件、費用¥96.30(推定合算、token単位実測不能と明記)、Family C残予算=¥133.99−¥96.30=¥37.69。Open Item候補: Key Phrase選定Validatorが会話文主体記事で高頻度不合格(6回中4回)、短小語TTSのCJKドリフト再現、A2語数429語(ユーザー: 今回は許容、語数は目安・超過は必ず報告)。UDR: A2/B1構成、Validator対応要否、UI読み上げ/人物名ルール恒久化要否。
  - **PM運用方針(ユーザー指示2026-09-14、原文)**: 「既存仕様・既存Gate・許容コスト範囲内なら、発見 → 修正 → QA → 完成まで進める。ユーザー判断が必要なのは、仕様変更・Gate変更・大きなコスト増・最終人間品質判断だけです。」STOP条件: 新Production仕様が必要/既存Gate緩和・変更が必要/Ledger修正だけでは解消できない構造問題/想定を大きく超える追加コスト/最終的に人間判断しかできない品質問題。
  - **Family C運用clarification(ユーザー指示、原文要旨)**: AI固有名はこれらの記事に限り許容、CURRENT_SPECのルールとしては追加しない。語数は目安であってhard capではない、429語は今回限り許容、超過は毎回必ず報告する。→DECISION_LOGのみに記録(CURRENT_SPECへルール追加しない)。
- 禁止: `git add -A`/`.`/`stash`/`clean`/`amend`/`rebase`/`force push`、API呼び出し、Production/Trialコード変更、`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET*.md`の**gitignore対象**をaddしようとすること(RESULT_PACKET_*.mdが追跡対象かは`git check-ignore -v`で確認し、追跡対象のもののみadd)、SSOT全文Read。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
---

## ユーザー指示(原文)

> 最終REPORTには、Trend: Ledger修正内容/Verification source/regenerated A2/B1/Fact Checker/Ledger Deviation/Cross-Level Consistency/Production 1生成セット総原価/最終Status。Discovery: Ledger修正内容/A2/B1 rewrite差分/Fact Checker/Ledger Deviation/No Jargon確認/Key Phrase A2/B1/Production 1生成セット総原価/最終Status。Voices: Comment wiring結果/Fact Safety Gate 2V/3V対応/Leakage・Fact Checker個別修正結果/2V runtime evidence/3V regression/retry・fallback整合/actual model_id/CURRENT_SPEC・DECISION_LOG・OPEN_ITEMS/Git evidence/Dangling Reference Check/最終Status。未解決事項: Claude側で実施済みの対応/なぜClaudeだけでは完了できないのか/ユーザーが判断すべき具体的選択肢。
> Production 1生成セット総原価を主指標とし50:50配賦なし(PM_GOVERNANCE 15-8)。Claude利用量は9-10形式(週間利用枠換算: 取得不能)。

## 事前指定Read一覧

1. `docs/pm/RESULT_PACKET_4T_TREND_COMPLETE.md` 全文、`docs/pm/RESULT_PACKET_4T_DISCOVERY_COMPLETE.md` 全文、`_2.md` 全文、`_3.md` 全文、`docs/pm/RESULT_PACKET_VOICES_VAR2.md` 全文、`docs/pm/RESULT_PACKET_FC9.md` 全文(REPORT作成の素材)。
2. `er014_output/four_type_observation_01/trend/reader_facing_article.txt`・`reader_facing_article_b1b.txt` 全文(突合表書き直し用)。`trend/cross_level_consistency.md` 全文(書き直し対象)。
3. `EDITORIAL-4TYPE-FOLLOWUP-01_REPORT.md`: Grep `^## |^# ` → 章立てのみ(-02 REPORTの構成を揃える)。
4. `er014_output/four_type_observation_01/index.html`: Grep `<h[1-6]|<tr|href=` → 各記事セル・Key Phrase・費用セルの位置。
5. `OPEN_ITEMS.md`: Grep `^\| OPEN-135|^\| OPEN-150|^\| OPEN-151|^\| OPEN-148` → 該当行のみ。
6. `DECISION_LOG.md`: Grep `PM-CLOSEOUT-CONSOLIDATION-131|EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-02` → 最新エントリ位置と索引行。
7. `CURRENT_SPEC.md`: Grep `Family C|Trial-08|Future` → Family C Trial記述の末尾位置(Trial-09 VALIDATED 1段落追記位置)。Grep `Trend Synthesis|Discovery Focus S2` → 4TYPE完成結果の参照1行を置く位置(既存の「4TYPE観測」参照段落があればそこ)。
8. `docs/pm/PM_GOVERNANCE.md`: Grep `^## 11|^### 11-|^## 15|D-2-補足` → 11節末尾の追記位置(新項「11-x 既存仕様内の個別修正は完成まで進める(2026-09-14ユーザー指示)」)。
9. `docs/pm/PM_BRIEF.md` L133-157(ACTIVE_TASK固定ヘッダ書式)+ Grep `OPEN-151|Family C|4TYPE` → 状態行の更新位置。
10. `docs/pm/tools/measure_delegation_task.py`・`collect_subagent_transcripts.py`: Grep `argparse|add_argument` → 引数のみ。

## 事前指定Grep一覧+追記位置・更新位置の手順

- (a) Trend `cross_level_consistency.md`を最終テキストで書き直し(冒頭に「Local Rewrite後の最終テキストから引用(CONS-132で訂正)」と明記、A2 503語)。
- (b) 最終REPORT `EDITORIAL-4TYPE-FOLLOWUP-02_REPORT.md`(新規root): 1節概要+PM方針、2節Trend、3節Discovery、4節Voices(-02 REPORT参照+要約)、5節Family C Trial-09(参照+要約、UDR再掲)、6節コスト表(15-8形式: News¥98.32/Trend¥174.03/Discovery¥463.27/Voices¥140.39、各内訳、参考破棄run、50:50配賦なし、Family C Trial¥96.30と残¥37.69は別表)、7節Claude Code usage(9-10形式、下記計測結果、週間利用枠換算: 取得不能)、8節未解決事項(各項目に「実施済み対応/なぜClaudeだけで完了できないか/具体的選択肢」: Discovery KP B1B Validator誤検知、Voices Leakage残存、Family C UDR3件、Open Item候補[driver resolvedバグ・KP retry上書き・手動JSON編集・check_delegation_prompt「同上/TBD」誤検知])、9節Git evidence。
- (c) 比較ページ`index.html`更新: Trend A2/B1B最終、Discovery A2/B1B最終+Key Phrase A2一覧(B1B「未完成」表記)、Voices `run2_clean/b1_2v_new_theme_attempt3/article.md`へ差し替え、各Family総原価セル、Family C Trial-09 player相対リンク(`../../er013_output/family_c_episode_trial_09/home_robots/player.html`)を追加。
- (d) SSOT: `OPEN_ITEMS.md` OPEN-135末尾(Trend完成/Discovery完成[KP B1B未完成]、総原価、commit hash)、OPEN-150末尾(Discovery No Jargon維持0/0)、OPEN-148行は変更なし。`DECISION_LOG.md`: 直近エントリ直後に`## PM-CLOSEOUT-CONSOLIDATION-132`(Trend/Discovery完成、Trial-09 VALIDATED、Voices -02参照、PM方針追記、Family C clarification[AI固有名は当該記事限り・CURRENT_SPECルール化しない/語数目安・429語今回限り許容・超過は必ず報告]、Open Item候補一覧、費用、commit)+索引1行。`CURRENT_SPEC.md`: Family C Trial節末尾にTrial-09 VALIDATED 1段落(完成episode構造・2-voice・Gate PASS・Status VALIDATED・Production未採用)。`docs/pm/PM_GOVERNANCE.md` 11節末尾に新項(ユーザー原文+STOP条件5つ+「Sonnetループ上限・費用上限は従来どおり」)。`docs/pm/PM_BRIEF.md`状態行更新。`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`にTrend/Discovery完成run各1行(gpt-5.6-luna)。
- (e) ACTIVE_TASK固定ヘッダ更新(管理ID=CONS-132、APPROVED未配線=OPEN-151 PARTIAL/OPEN-83/145/146、報告単位Status: 4TYPE=News OK/Trend OK/Discovery OK[KP B1B UDR]/Voices PARTIAL、Family C=Trial-09 VALIDATED 試聴待ち)。
- (f) Claude usage計測: `.venv\Scripts\python.exe docs\pm\tools\measure_delegation_task.py --task-id <id>` を ad89ffd0adfc339c2(Trial-09)/a6ff95d402cea606d(Trend)/a79f94a4d28677526(Discovery初回)/a0b9e8c3143100c0f(Voices)/a115927d191406a8c(Discovery CONT1)/a888b2801bed2c7c6(Discovery CONT2)の6件で実行し、tool_uses/duration/cumulative_usageをREPORT 7節へ。取得不能なら「取得不能」と記載。
- (g) transcript退避: `.venv\Scripts\python.exe docs\pm\tools\collect_subagent_transcripts.py --tasks-dir "C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\tasks" --subagents-dir "C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\subagents" --transcripts-dir docs\pm\transcripts --only-task-ids a9a9a247713c5c080,ad89ffd0adfc339c2,a6ff95d402cea606d,a79f94a4d28677526,a0b9e8c3143100c0f,a115927d191406a8c,a888b2801bed2c7c6 --apply`(subagents-dirが存在しない場合はtasks-dirのみで実行。既存ツールの引数名に合わせる)。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-132.md --json-out docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-132_check.json`
2. (f)(g)のコマンド。
3. `git status --porcelain -- er013_output/family_c_episode_trial_09 er013_family_c_episode_trial_09_run.py er013_family_c_episode_trial_09_test_01.py er014_output/four_type_observation_01 docs/pm CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md` で対象確認 → 明示add → commit → `git push origin main`(classifierブロック時は同一コマンド最大3回再試行、bypass禁止)。
4. push後: `git log --oneline -3`、`git status --porcelain | head -20`(意図しない残差分の確認)。
(回帰不要: コード変更なし。)

## SSOT追記文

上記(d)に従い実値で記載。PARTIAL/未完成の項目をOK/PRODUCTION_WIREDと書かない。VALIDATEDをAPPROVED_FOR_PRODUCTIONと書かない。

## Git(明示add対象・コミットメッセージ・trailer)

- 明示add: `er013_family_c_episode_trial_09_run.py`、`er013_family_c_episode_trial_09_test_01.py`、`er013_output/family_c_episode_trial_09/`(spec/・home_robots/一式。`.ok`marker等の一時ファイルは除外可。wav 48MB+11MBは含める)、`EDITORIAL-FUTURE-FAMILY-C-HOME-ROBOTS-EPISODE-SPEC-TRIAL-09_REPORT.md`、`EDITORIAL-4TYPE-FOLLOWUP-02_REPORT.md`、`er014_output/four_type_observation_01/trend/`・`discovery/`配下の変更・新規、`er014_output/four_type_observation_01/{index.html,progress_log.md}`、`CURRENT_SPEC.md`、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/PM_GOVERNANCE.md`、`docs/pm/PM_BRIEF.md`、`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`、`docs/pm/delegation_log/`の本window新規分(EDITORIAL-4TYPE-FOLLOWUP-02B-TREND-COMPLETE、03B-DISCOVERY-COMPLETE、-CONT1、-CONT2、EDITORIAL-FUTURE-FAMILY-C-HOME-ROBOTS-EPISODE-SPEC-TRIAL-09、PM-CLOSEOUT-CONSOLIDATION-132 各.md+_check.json)、`docs/pm/transcripts/`退避分、追跡対象であれば`docs/pm/RESULT_PACKET_4T_TREND_COMPLETE.md`・`RESULT_PACKET_4T_DISCOVERY_COMPLETE*.md`・`RESULT_PACKET_FC9.md`。無関係な既存差分(er006_output/er011_output/er012_*の未コミット変更等)はaddしない。
- コミットメッセージ: `PM-CLOSEOUT-CONSOLIDATION-132: 4TYPE補完完成(Trend OK/Discovery OK[KP B1B UDR])+Family C Trial-09 VALIDATED+Voices OPEN-151 -02結果参照+PM運用方針(既存仕様内個別修正は完成まで進める)追記` の後に空行、末尾に
  `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`
  `Claude-Session: https://claude.ai/code/session_01THnbjj6FiMbJtrKdFteoE4`

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`(上書き)に: 1) commit hash(full)・push結果・add件数、2) Trend突合表修正内容、3) REPORT/比較ページのパス、4) コスト表(15-8)実値、5) Claude usage 6件の実測値(取得不能は明記)、6) SSOT追記位置(ファイル・行)、7) transcript退避件数、8) T-0結果・事前指定外Read、9) push後`git status --porcelain`の残差分要約、10) Trial-09 player・wav・REPORT・-02 REPORTのraw.githubusercontent.com URL(`https://raw.githubusercontent.com/shimomura055/eigo-radio/main/<path>`)、11) ACTIVE_TASK更新済み。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥0)
- [x] 並行タスク衝突回避あり(単独)
