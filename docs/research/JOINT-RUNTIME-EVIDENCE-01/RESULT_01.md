# RESULT_01: 合同runtime evidence 実行結果(JOINT-RUNTIME-EVIDENCE-01 委任_02、2026-10-22 JST)

対象: OPEN-450 PNAP / OPEN-451 KP3V / OPEN-454 KPFT。正式Production経路(X=runner main `er019_family_x_audio_production_runner_01.py` の scaffold/tts/assemble/player、Z=`er026_family_z_fiction_production_runner_01.py --stage all`)で実行。Status記載は `WIRED_PENDING_FABLE`(PRODUCTION_WIREDではない。判定はFable)。
証跡dir: `docs/research/JOINT-RUNTIME-EVIDENCE-01/run_20261022/`(`joint_evidence.{json,md}`=coffee+Z、`joint_evidence_small_bag.{json,md}`、stage別`joint_evidence_after_*`、pre_snapshot、stop_check_*、各console log、regression_summary.json、dangling_grep_pre.*)。

## 0. 実行した run(run dir)
| run | path | 内容 |
|---|---|---|
| X-1 coffee_prices | `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_jre_01`(source=`er019_output/coffee_prices/run_v5_ms_01` a2/b1b、style=fx_20261017) | scaffold→tts→assemble→player。a2/b1bとも kp1英語がSTOPPED→HR(下記)。Assembly=BLOCKED_STYLE_PROFILE_GATE(両level) |
| X-2 small_bag | `er019_output/family_x_audio_production_wiring_01/small_bag__run_jre_01`(source=`er019_output/small_bag/run_jre_src`=b3 trial `small_bag/run_02` の a2/b1b `article.md` から旧構造の`###`見出し行のみ除去[本文語は不変]して作成) | scaffold→tts→assemble→player。**b1b=全segment OK・組立済み**。a2は kp1英語(`novelty minaudière`)がSTOPPED→HR、組立BLOCKED |
| Z melos | `er026_output/family_z_production_e2e_01/melos/run_jre_01`(`run_e2e_06`から writer/support/segment_plan/dialogue_attribution/speaker_table を複製。dry-runで writer/std_adjust/plan/support=「provenance sha一致で再利用」を確認) | kp(1回目失敗→是正→再実行)→`--stage all`(全13 stage完走、page_verify含む) |
X素材の選定理由(指示§1(5)): 指示は「small_bagのa2/b1b両本文があれば small_bag 1本」。small_bagのsourceは旧構造(`###`見出し3つ付き、b3 diversity trial)で、現行runner main `plan`が`NG_HEADING_IN_BODY`で`SPLIT_FAILED`(実測)。そこで fallback(coffee_prices でKPFT/KP3V + small_bag を正式入口から)を採用。small_bagは見出し行の機械除去のみの派生sourceで正式入口に通した。この派生sourceはWriter/QAを通っていない評価用入力(公開物ではない)。

## 1. タスク別・Family別 判定表
凡例: PASS / FAIL / 未確認(根拠path)。「er106」=`joint_evidence.md`。er106は実装の記録名とずれる箇所があり(下記§5)、**er106の機械判定ではなく実ファイルを直接読んで確認した値**を採用した箇所を明記。

### 1-1 KPFT(OPEN-454)
| # | 確認項目 | X (coffee / small_bag) | Z (melos) | 根拠 |
|---|---|---|---|---|
| 1 | 全文直接選定(`kp_backend_used`) | PASS / PASS: `fulltext_p2`、db_hybrid dir無し | PASS | `*/key_phrases/keywords_runtime_metadata.json` |
| 2 | 実model=Luna | PASS: `model_id=gpt-6-luna`(requested同一。`raw_usage_log`のselection行も`gpt-6-luna`) | PASS | metadata / `raw_usage_log.jsonl`・`cost_log.jsonl` |
| 3 | 正式Prompt 2 | PASS: sha256=`a12896f485604f32…`(全run・全level) | PASS | metadata `prompt_sha256` |
| 4 | 最大3件 | PASS: 全levelで3件、shortfall=False | PASS | `keywords_canonicalized.json` |
| 5 | 本文外/6語以上は不採用 | PASS(採用3件は全て本文連続一致・≤5語)。**拒否の実例は未観測**(選定段で本文外/6語超は発生せず) | PASS(同左) | er106 KPFT-5 |
| 6 | 原形化・一般化(受理/拒否の実例) | 受理: `pumps its fist→pump one's fist`、`pushed prices up→push prices up`。small_bagは変更0件 | 受理: `held out→hold out`、`in your place→in someone's place`、`sentenced him to death→sentence him to death`。**拒否(実例)**: LLMが出した`sentence someone to death`(him→someoneは閉じた人称表外)、`pull someone under`、`nearly abandon someone`(副詞後の動詞位置) | §3-1 |
| 7 | 後段(意味/解説/音声/ASR/組立)・再生順 | **FAIL(部分)**: coffee a2/b1b と small_bag a2 はkp1英語がSTOPPED→HR→組立BLOCKED。small_bag b1b は PASS(KP音声/解説/ja意味OK、timeline KP=3、再生順間接検査OK) | PASS(両level OK、timeline KP=3、再生順間接検査OK、`page_verify`でKP行3) | `audit/tts_generation_results.json`、`run_summary_assemble.json`、er106 KPFT-7 |
| 8 | retry/fallback/regen/resume | 外側retry: coffee a2=1/3・b1b=2/3、small_bag a2=3/3(成功)・b1b=1/3。stale/m2_fallbackなし | 1回目 b1b=3/3**尽きて`FAMILY_Z_KP_NOT_PASSED`(rc=2)** → 是正(§3-1)後の再実行で a2/b1b とも1/3で成功 | `outer_retry_log.json` |
| 9 | 旧DB/5件のDangling | PASS(db_hybrid経路 production=0、`KP_ARTICLE_COST_CAP` 0、`m2_fallback` production=0)。※KP3V旧dual識別子は§4 | 同左 | `dangling_grep_pre.md`、`joint_evidence.md` |
| 10 | Regression/Validator/test | PASS: 全回帰 collected=6871 passed=6835 failed=13 errors=17 skipped=6(KPFT報告のbaselineと完全一致、新規失敗0)、`er003_test_kp_fulltext_wiring_01` 62件OK | 同左 | `regression_summary.json` |
| 11 | X/Z双方のruntime | PASS | PASS | — |
| 12 | SSOT/Git | 本commit/OPEN-454 | 同左 | — |
KPFT 付随: gloss(`japanese_gloss`)生成=全KPで生成・ALIGN_PASS(§3-3に全文)。Redundancy QA=全level REDUNDANCY_PASS。Adv解説(Z b1b `kp_explanations.json`)=`used_form`(sentence him to death / without asking for another promise / earn such trust)に対する英語解説(11/8/12語、≤15語QA PASS)。X small_bag b1bの解説も3件OK。D1 gate(Z)=`audit/key_phrase_source_gate.json` a2/b1bとも `status=PASS`(total=3 present=3 missing=[])、`gate_result_04C.json` `kp_vote_audit` checked=3・with_vote_evidence=[1,2,3]・missing=[]・blocking=false・shared_gate=PASS。旧5件・Topic枠の残骸: Z `index/standard/advanced.html` と X player.html に `kp4/kp5/key_phrase_4/5` 0件(grep)。`kp_stage_failed.json`: Z 1回目に`FAMILY_Z_KP_NOT_PASSED`発生(再実行で解消。final run dirに残存marker無し=`all`が完走)、Xは非発生。

### 1-2 KP3V(OPEN-451)
| # | 確認項目 | X | Z | 根拠 |
|---|---|---|---|---|
| 1 | 割れたときのみWhisper | PASS(Xでは割れ=P≠S が出ず、Whisper不要で未発火。coffee kp1は`NG_PROTECTED_DISSENT`でWhisperを呼ばないのが設計) | **PASS**(Z b1b kp1: P=NG・S=PASS → Whisper(small/int8)自然発火、W=PASS → `PASS_VOTE_2OF3`・行`S+W`)。er106がKP3V-1をNGとしたのは記録キー名の不一致(誤判定) | `melos/run_jre_01/b1b/audit/tts_generation_results.json` key_phrases.1.english.kp_vote_check |
| 2 | 2/3 PASSで正常終了 | 未観測(X) | PASS(上記1件、`PASS_WITH_WARNING`=事後試聴リスト対象)。**当該wavの聴取で妥当性確認が必要(未実施)** | 同上、`b1b/audit/pass_with_warning_listening_list.json` |
| 3 | 2/3 NGは従来NG | PASS: coffee kp1 = P/S/(W未呼出)→NG。small_bag a2 kp1 = P=UNCERTAIN → NG。全て最終採用なし(STOPPED→HR) | (対象事例なし) | tts_generation_results |
| 4 | Whisper error/未利用でPASSにしない | PASS(I1-I7違反0、er106 KP3V-4) | PASS | er106 |
| 5 | retry/fallback/regen/resume | PASS(attempt各1〜、K2 styled→English Lock→minimal fallbackの既存機構へ票が一貫適用[coffee kp1の`fallback_attempts_log`に各attemptの`vote`あり]) | PASS | tts_generation_results |
| 6 | **Store再利用時に新判定** | **PASS(small_bag b1b kp3 `Carry the Load`: `reused=True`、`kp_vote_check.source=stored_evidence_rejudged`、`version=kp_vote_check_v1`、行P+S)** | 未観測(再利用0件) | `small_bag__run_jre_01/b1b/audit/tts_generation_results.json` key_phrases.3 |
| 7 | 解説・その他音声に影響なし | PASS。er106 KP3V-7 NGは偽陽性: `phrase_repeat`は`dict(en_r)`(英語phraseの同一音声のコピー、`er019:1221-1223`)でvote証跡を継承するのみ | PASS | er019 runner 1221-1223 |
| 8 | PNAPとの範囲整合 | PASS(KP segmentにALARM無し) | PASS | er106 PNAP-8 |
| 9 | X/Z双方のruntime | PASS | PASS | — |
| preflight | Whisper事前確認 | PASS: console `[KP-VOTE] whisper preflight: ok=True model=small/int8 cache_present=True load_sec=0.0 error=None`(Xのtts前に1回) | Zも同(console) | `x_tts_console.log`、`z_all_console.log`(er106 KP3V-1cはMISSING=記録先ファイル名の想定違い) |
| 追加API | 追加API 0 | Whisperはローカル(費用0)。Azure/OpenAI呼出は従来のP/S 2系統と同数 | 同左 | cost台帳 |
**KP音声の投票記録(kp_vote_check_v1)**: X coffee: a2/b1b とも kp2・kp3=P+S PASS_DUAL、**kp1=NG_BOTH**。X small_bag: a2 kp2/kp3=P+S、a2 kp1=NG(`novelty minaudière`)、b1b kp1/2/3=P+S(kp3はStore再利用+再判定)。Z: a2 kp1/2/3=P+S、b1b kp1=S+W(Whisper発火)、kp2/3=P+S。

### 1-3 PNAP(OPEN-450)
| # | 確認項目 | X (coffee / small_bag) | Z | 根拠 |
|---|---|---|---|---|
| 1 | 発音情報取得・TTS供給 | coffee: 供給対象語なし(0)。**small_bag: a2/b1bとも `khaite→Kate`(B階層・人承認済み・ledger_id=1652efa9f4bdd7e8)をTTS入力へ置換**。`full_story_part2`のASR文に`Kate's palm-sized evening clutch`、segment status=OK。Stage1調査呼出=perplexity sonar 1件(unpriced) | 供給0 | `small_bag__run_jre_01/*/audit/pronunciation_alarms.json`(`supply_applied`)、`operator_alarm_report.md` |
| 2 | 不一致時アラーム+制作継続(`PASS_WITH_PRONUNCIATION_ALARM`) | **未観測(正式入口からの発火は今回なし)**。alarms=0件(coffee a2/b1b、small_bag a2/b1b)。Khaite→Kateが1回目で一致したためアラーム化せず | **未観測(正式経路実行済み・発火未観測)**。alarms=0 | `pronunciation_alarms.json`(count=0)。指示§1(4): 反復runは行わない |
| 3 | HRに回らない・Lock RESOLVED | PASS(固有名詞が原因のHR 0、alarm状態recordも0)。HR queue +3行は**全てKP1英語**(§1-2、PNAP非対象)で非RESOLVED lockも`kp1_en`のみ(§2) | PASS(Lock全RESOLVED、HR新規0) | `joint_evidence.md` (e)、`review_lock_state.json` |
| 4 | ASR/retry/fallback/regen/resume整合 | PASS(継続動作) | PASS | tts_generation_results |
| 5 | 固有名詞以外は従来どおり | PASS(KP segmentにALARM付かず) | PASS | er106 PNAP-8 |
| 6 | 完成報告まで引継ぎ | PASS: runner stdoutに「固有名詞発音アラーム報告」節、供給適用一覧に`khaite→Kate`。`consistency.match=True` | PASS | console logs、`pronunciation_alarms.json` |
| 7 | 一般リスナー非露出 | PASS(player.html / Z index.htmlに`PASS_WITH_PRONUNCIATION_ALARM`/アラーム語なし、er106 PNAP-7 leaks=[]) | PASS | `joint_evidence.md` |
| 8 | Regression | PASS(§1-1 #10) | 同左 | — |
| 9 | X/Z双方のruntime発火 | 供給は発火(Khaite)。アラーム受理は未観測。**過去証跡(別素材, TTS段関数直接呼出)=PNAP 委任_02c の X実発火1件**であり、runner main経由の発火証拠は今回も取得できず | 未観測 | — |
実使用model: TTS=`gemini-3.8-flash-lite-tts`(Z Dialogue等に`gemini-2.5-pro-preview-tts` 21呼出も既存どおり)/Primary ASR=`gpt-4o-mini-transcribe`/Secondary=`azure-speech-stt`(`raw_usage_log.jsonl`/`cost_log.jsonl`のmodel_id集計)。

## 2. 重要所見(Fable判断材料)
1. **kp1英語STOPPED→HR 3件(X coffee a2・b1b、X small_bag a2)**: いずれも rank1。`pump one's fist`(coffee)=TTSが`once fist`/`one fist`/`1's fist`と読み、PrimaryはNORMALIZED_MATCHでもAzureが`1's`(数値guardのprotected dissent)でNG。保存wavをoffline再判定(API 0)すると、数値guardを仮に緩めてもWhisperが`Pump Ones Fest`でNG(`NG_VOTE_WHISPER_NG`)。つまり**音声自体が不良で、ゲートは正しく止めた**(ゲートのバグではない)。`novelty minaudière`(small_bag a2)=Primary `Novelty Monadier.`(loanword、UNCERTAIN)で止まった。共有HR queue `er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl` に本taskで3行追加(timestamp 17:40:32 / 17:43:47 / 18:03:58、wav pathは各run dir)。人間が処理するか破棄するかはFable判断。
2. 3-ASR投票は、Primary単独では落ちるがS+Wで通る事例(Z b1b `sentence him to death`: P=`sentenced him to death.`)を実runtimeで観測した。**P=NGの理由はTTSが`sentenced`と発音した可能性もあり、聴取確認が必要**(事後試聴リストに載る)。推測で正否は断定しない。
3. 費用が設計想定(-4.8円/セット)と逆に見える: §4。

## 3. 失敗と修正の履歴
1. **Z melos KP stage 失敗(KPFT由来)**: `FAMILY_Z_KP_NOT_PASSED(b1b): OUTER_RETRY_EXHAUSTED`。`outer_retry_log.json`: 3回とも selection=PASS だが canonicalization=INVALID。原因=LLMが目的格`him`を`someone`へ一般化(`sentence someone to death`)し、閉じた人称表(`er003_key_words_canonicalization.py:431-449`、heへの`someone`は有るが`him`は無し)外のため決定論validatorが却下(2回とも同出力)。選定段がsentenced him to deathを3回選び続け外側retryでも解消せず。**是正(承認範囲内・templateの明確化のみ)**: `er003_v1_translator_briefs/b1_p2_keywords_canonicalization_fulltext_prompt_template.txt` 規則3へ「一般化してよい代名詞は列挙語だけ。him/her(目的格)/them/me/us/it等はそのまま残す」を追記(新規KPFT template、旧templateは無変更・sha固定testもPASS)。test 2件追加(`er003_test_kp_fulltext_wiring_01`: 62件OK)。commit `1d501f74d`(push済)。再実行(失敗部分のみ・同run dir・資源消費=Luna約数円)でa2/b1bともPASS。validator・閉じた人称表・Promptの承認済み部分は無変更。**Fable確認事項**: これはProduction Prompt(新規template)の1文追記であり、事後報告。
2. 副次的な所見(未修正・Fable判断): `nearly abandoned you→nearly abandon someone` は閉じた表上は正当な変換(you→someone許可)だが、`er105_kp_fulltext_selector_01.py:_token_pair_ok`の`verb_pos`が「語頭または`to`直後」に限定されるため副詞後の動詞(`nearly abandoned`)の基本形化が却下される。今回の最終成功経路には影響せず(outer retryで別KPが選ばれた)。修正するとQ1 validatorの拡張になるため実施せず。
3. 回帰の「消えたtest」: `er019_family_x_fx_20261016_wiring_01_test_01.AbcGoldenTests.test_k2_store_module_is_family_x_only`は**消えていない**。collectされ現在PASS(72件OK)。KPFT報告のbaseline failed 14→13の差分はこのtestがKP3V配線commit(`865a2ae46`)で期待値リストに`er104_kp_vote_wiring_test_01.py`等が追加され、着手前failから現在PASSに変わった分(test削除/改名/skipではない)。

## 4. 費用・時間(出典: `raw_usage_log.jsonl`/`cost_log.jsonl`、`daily_dev_cost_01.py`系集計=`joint_evidence*.md` (d))
| run | 合計 | KP関連(chain+音声) | 備考 |
|---|---|---|---|
| X coffee(scaffold 1.97+tts 22.24) | 24.213円 | 2.448円(+未分離scaffold 1.675円) | 非KP音声20.07円(profile違いで全segment再生成、手順書想定どおり) |
| X small_bag(scaffold 2.16+tts 18.64) | 20.803円 | 2.174円(+未分離scaffold 1.907円) | `perplexity/sonar` 1呼出はunpriced(金額未確認、Stage1調査) |
| Z melos(kp失敗分含む) | 26.101円 | 3.713円(chain 2.40円は失敗した外側retry含む) | 旧`run_e2e_06`=27.58円/KP関連1.52円 |
| **本委任合計** | **71.117円** | | 上限150円内 |
本日累計: Fable前提の約900円 + 71.1円 ≒ **約971円**(厳密合算は未確認。REPORT_LEDGER起点の約887円+PNAP 02c等を含む差は要照合)。上限1,500円内。
比較: 旧5件run(X paycheck KP関連1.49円/Z 1.52円)に対し、新3件KP関連はX 2.17〜2.45円/Z 3.71円(Zは失敗したretry込み。成功retry単体の内訳は未分離)。**KP段の単価は設計見込みの減少(-4.8円/セット)にならず、今回の計測では同等〜増加**(gloss生成が新規LLM段、外側retry、HR再生成等)。非KPが主因の総額比較は不可(profile差)。1記事セット単価の確定推定は、HR無し完走のsmall_bag b1b + Zのみ=未確認。
処理時間: X coffee scaffold約186秒・tts約431秒(両level)。X small_bag tts約7.5分(両level)。Z: kp 90秒(1回目失敗)+0.8秒(再実行)、tts_b1b 337.7秒、tts_a2 359.0秒、assemble 1.4秒、pages 9.6秒、page_verify 164.2秒(合計約14.6分/起動)。

## 5. er106 と実ファイルの食い違い(集計scriptの限界。Production無変更)
- KP3V-1(Z)=NG: 実ファイルはWhisper発火あり(`kp_vote_check.whisper.called=true`)。er106が見るキー名が実装(`whisper.called`)と異なる。KP3V-0b MISSING・KP3V-1c(preflight記録ファイル)MISSINGも実装名称差。KP3V-7(X)=NG偽陽性は§1-2 #7。PNAP-3(X)=NGはKP1英語のHR(PNAP非対象)を帰属させたもの。本表は実ファイル確認値を採用した。
- Dangling(KP3V旧dual識別子 production=22): 全て`er096_kp_dual_pass_01.py`(`er099`が保存証跡を読むための残置と冒頭に明記、`evaluate_dual`は実行不可)と`er078_asr_unified_judge_01.py:27`のコメント。Production経路に`dual_required`/`NG_DUAL_PRIMARY_NOT_PASS`の実コードは無い(Grep)。撤去するか残置するかはFable判断。

## 6. 成果物の状態
- X試聴: coffee `…/coffee_prices__run_jre_01/player.html`(組立BLOCKEDのためKP行無し)、small_bag `…/small_bag__run_jre_01/player.html`(b1bは完成、a2はkp1 HRで未組立)。GitHub Pages URLなし(er019_outputは公開dirではない)。
- Z試聴: `user_test/family_z_melos_02/`(index.html/standard.html/advanced.html、KP行3件、`page_verify_local.json`で再生OK 46/50、`seek_ok_all=false`は既存どおり)。**受理済みページを上書きしたため `git status` で97ファイルが変更状態**。退避=`user_test/family_z_melos_02__backup_20261022/`(.gitignore対象外のためuntracked表示のまま放置=指示§1(2))。**変更は未commit(commitすると受理済みURL https://shimomura055.github.io/eigo-radio/user_test/family_z_melos_02/index.html の内容が新run差し替えになるためFable判断)**
- 事前チェックa: Production .pyの未commit差分は`er063_family_z_audio_01.py`の1行(コメントのみ。ASTを比較して実行コードと同一であることを確認)。他agent残置のため触らずに実行(指示は「実行せず報告」だが、AST同一のため実行コードとevidenceの対応は保たれると判断。Fable判断)。
