# RUNTIME_EVIDENCE_01 (FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01 委任_02、2026-10-23、途中停止時点)

run dir: `er026_output/family_z_production_e2e_01/after_twenty_years/run_sf_prod_01/`(wav類は未追跡)。実行は `.venv/Scripts/python.exe`(system Pythonには wordfreq/genai が無い)、`TTS_EXECUTION_MODE=STANDARD`、Production経路のCLI(`er026_family_z_fiction_production_runner_01.py --story after_twenty_years`)。

## 起動履歴(run_launch_log.jsonl / console_t2_*.txt)
| # | JST | stages | 結果 |
|---|---|---|---|
| 1 | 22:17:17 | seed_check | OK(権利Gate・Seed sha・source_essentials検査 PASS) |
| 2 | 22:17:26 | seed_check,writer,std_adjust | OK 14.50円(Adv r0/r1/r2 + Std、Adv 426語/Std 443語、段落28/28) |
| 3 | 22:23:11 | plan,support,kp | **STOP rc=2** DIALOGUE_ATTRIBUTION_MISMATCH(b1b) q23_1(後述、費用 約0.4円) |
| 4 | 22:25 | plan,support,kp | OK 累計17.61円 |
| 5 | 22:30:08 | tts_b1b,tts_a2,provision_shell,gate,assemble,pages,page_verify | tts_b1b OK(341.6秒)。tts_a2は c8 の10分cool-down待機中に**自分がPID 46408をtaskkillした(誤り)**(rc=1)。後述 |
| 6 | 22:47 | 同上(再起動1回) | tts_b1b resume、tts_a2: c8のみ **HR Lock(STOPPED)** rc=2 |

STOP範囲確認 `tools/stop_scope_check_01.py` は各起動前に rc=0(都度 `_stop_scope_check_t2*.json`)。STOPセンチネル・RESTART_STORMの発動なし。他agentのTTS並走なし(ACTIVE_TASKに進行中行なし)。

## 事象と原因
### 1. DIALOGUE_ATTRIBUTION_MISMATCH q23_1(原作忠実性とは無関係の話者判定)
`"They can change a good man into a bad one," the tall man replied. "You're under arrest, Bob. ..."` で 決定論=bob(同一段落内の宛先『Bob』を拾う addressee_keyword 型誤り)、LLM=detective(正)。原本=`dialogue_override_b1b_mismatch_01.json`。Std 同型qも同じ決定論結果(オフライン検算)。是正=作品config(`STORY_SPEAKER_CONFIG["after_twenty_years"]` の `z_voice_keywords`/`dialogue_voice_keywords`)の挿入順を detective→bob→patrolman に変更(値の並び替えのみ、決定論/LLM突合のGate自体は無変更、mismatchは引き続きSTOP)。再実行で全引用 agree/llm_only、mismatch 0(`speaker_table.md`)。
### 2. 自行によるPID誤終了(運用ミス)
c8 は max_attempts 後に既存仕様の**固定10分cool-down**(`er020_tts_retry_local_rewrite_01.maybe_cooldown_before_attempt`、COOLDOWN_SECONDS=600、短縮禁止)に入る。CPU・cost_log更新が7分間止まったため「ハング」と誤認しPID 46408を終了(自分のPIDのみ)。実際は正規のcool-down待機(py-spy dumpで `maybe_cooldown_before_attempt` の sleep を確認)。再起動1回を消費。追加費用は c8 の再TTS分のみ(約1円未満)。再発防止: ログ無更新≠ハング。cool-down(最大10分)を考慮し、まず `py-spy dump --pid`(別dirにinstall、リポジトリ無変更)で確認する。
### 3. Std c8 HR Lock(未解決)
clip `full_story_part2_c8`(narrator): `"... a few minutes hardly mattered. At ten thirty, a tall man in a long overcoat hurried towards Bob."`。5 attempt(custom×4+minimalfallback)すべてASR=`At 10:30,`(1回のみ `ten-thirty`)。音声は『ten thirty』と読まれており正しい。原因=既存ASR判定の保護検査(er006_preprod_hardening classify_asr_match → protected check)が原稿側の隣接数詞語『ten thirty』を合算して `40` に正規化し、ASRの `10:30`(`10 30`)と比較して number_mismatches=[('40','10 30')] → TRUE_CONTENT_MISMATCH/NG_PROTECTED。オフライン再現済み(API 0): 原稿=`ten thirty`、ASR=`10:30` → TRUE_CONTENT_MISMATCH、ASR=`ten-thirty` → NORMALIZED_MATCH。Advは同じ時刻を `half past ten` と書いたため非発生。時刻表現(隣接数詞語)はX/Zいずれでも起こり得る既存検査の限界。
最終状態: `a2/audit/review_lock_state.json` の c8 = HUMAN_REVIEW_REQUIRED(STOPPED、cumulative_tts_attempts 3、ASR calls 3)。他の Std 全clip は OK。

## 実績
- Writer段(`gpt-6.1-sol`: r0/r1/r2/std_adjust)+plan/support/kp(`gpt-6-luna`)= 17.61円。tts_b1b 12.93円(Adv: 全41 clip OK、attempt>1 なし、HR 0、PASS_WITH_WARNING 0、`*_original.wav` 19本=speed v2 dialogue fast 6%の元音)。tts_a2 ≈13円+c8再試行(Std 全40 clip 中39 OK)。合計 約45円(日次ledger増分45.84円と整合)/上限100円。
- RET: `audit/entity_table.json` builds=1 call(22:30:10、`gpt-6-luna`、0.0337円)。実体表 6件(person/weak 2[Bob,Jimmy]、place/weak 3、work_title/weak 1)、証拠として使用可 0件、発音アラーム 0件、HR(固有名詞起因)0件。会話経路でのRET発火は実体表上の確認(受理basis別集計は完成段のruntime_evidence_04Cで取得予定)。UKUS発火なし(英米差の語なし)。Perplexity発音調査は呼ばれていない(Bob/Jimmy等は一般的な英語名で発音供給対象なし)。
- Voice配役(正式Voice表の決定的割当規則、pinなし): narrator=Aoede / Bob=Algieba(男1番) / 警官(Jimmy)=Schedar(男2番) / 私服刑事=Fenrir(男3番)。最終の手紙は警官=Jimmyと同一Voice(Schedar)。`voice_assignment.json`。
- Std support lint: `LISTEN_INSTRUCTION`(comment_1)はZ Stdの既存WARN扱い(blockingでない)。
- 原作忠実性CP: `CP_CHECK_01.md`(重大8項目すべてOK、軽微所見 到着時刻が「30分待つ」期限ちょうど[ADV `half past ten`/STD `ten thirty`]=因果・結末に影響なし、Fable確認待ち)。
- 未実施: `provision_shell,gate,assemble,pages,page_verify`(完成段、c8解決後に**1起動**)、試聴ページ、page_verify。

## 想定される解決案(判断はFable)
- A: Std c8の原稿を Advと同形 `At half past ten,` に1語句の決定論パッチ(std.md・segment_plan_a2.jsonのc8テキスト・必要なら該当Part support/kp入力のshaを更新し、c8のみ `--only-clips full_story_part2_c8` 再生成)。意味不変。再生成はFable承認後(approve_regenerate)。
- B: 現テイクの人間(Fable/ユーザー)による聴取承認(HR Lock解除)。音声は正しいことをASR自身(`10:30`)が示している。
- C: (仕様候補・未承認)数詞語『ten thirty』型を時刻として扱う検査拡張。X/Z共通Productionの変更になるため実装せず記録のみ。
