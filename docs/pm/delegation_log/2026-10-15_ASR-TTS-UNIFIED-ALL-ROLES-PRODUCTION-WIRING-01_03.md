# 委任_03: ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 — EN(Primary ASR→統一judge)配線 + PASS_WITH_WARNING registry配線 + 試聴ページ節

管理ID: ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01(以下AUW)。Status: APPROVED_FOR_PRODUCTION(OPEN-356)→目標PRODUCTION_WIRED(本委任では未達。宣言しない)。
作業branch: `feat/auw-unified-asr-01`(origin上に存在、HEAD=59d3f089b)。mainへのmergeは委任_07まで禁止。
予算: 有料API呼出0(unit test・mock・静的解析のみ)。費用JPY0で報告。
Working dir: `C:\Users\tensh\eigo-radio`(branch `feat/auw-unified-asr-01` checkout済み。約750件の未commit変更は過去runの出力であり本委任の対象外。`git add -A`/`-f`/`stash`/`reset --hard`/`checkout -f`/`clean`/`rebase`/`amend`/`force push`禁止。commitは明示ファイル指定のみ)。

## T-0(開始前)
1. 本委任文を `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-15_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_03.md` に全文保存(改変禁止)。`python -I C:\Users\tensh\eigo-radio\tools\check_delegation_prompt.py`(存在するpathをGlobで確認して使う)を実行し、結果JSONを同名`_check.json`へ。FAILでも継続(理由を報告に記載)。
2. `stop_scope_check`(委任_02bで使ったもの)を実行し、rc=0を確認。非0ならSTOPして報告。
3. `git fetch origin` → `git merge --no-edit origin/main` をbranch上で実行(mainにはCRB記録commit 671891010が入っており、対象ファイルはdocs/research・docs/pm・OPEN_ITEMS・DECISION_LOGで、er078/er006とは無関係)。競合が出たら解決せずSTOPし報告。

## 事前指定Grep一覧(読む場所。全文読込禁止のSSOTはGrepのみ)
- `C:\Users\tensh\eigo-radio\er058_output\unified_all_roles_production_wiring_01\DESIGN_01.md` §4-3状態機械(:266–299)/§4-5/§5(配線点J1〜J11)/§6競合(:407–425)/§7 registry・ページ
- `...\DESIGN_02_ADDENDUM_01.md` §1 5値意味論(:33–95)/§2 `_is_number`マーカー付きtoken拡張(配線と同一commit)/§3-2/§4 SecondaryCache・重複呼出防止/§7 技術STOP・circuit breaker/§8 費用計測/OF-AUW-17(新ラベルのallowlist/count集計洗い出し)
- `...\IMPLEMENTATION_02b.md` §2・§6・§7・§8(委任_02bが残した配線注意点: `asr_judgement` additiveキー/`asr_judgement_inherited`/`equivalence_basis`4種/`signals`3種/`secondary_accept_fn`注入/allowlist `phase`切替手順)
- `C:\Users\tensh\eigo-radio\er078_asr_unified_judge_01.py`(公開API: `JudgeResult.audit_record`、`AttemptCtx`、`PrimaryResult`、`SecondaryOutcome`、`SecondaryCache`)
- `C:\Users\tensh\eigo-radio\er078_pass_with_warning_registry_01.py`(derive関数・入出力契約)
- `C:\Users\tensh\eigo-radio\er078_asr_unified_wiring_static_audit_01.py` + `er078_asr_unified_wiring_allowlist_01.json`
- `C:\Users\tensh\eigo-radio\er006_secondary_asr_01.py` `evaluate_attempt_with_cascade_detail`(約L535)とその呼出元(Grep `evaluate_attempt_with_cascade_detail`で全呼出点を列挙)
- `C:\Users\tensh\eigo-radio\er021_*`(EN semantic equivalence: `_tier1_atoms`、`_is_number`、should_pass集合、PRODUCTION_WIRED済みの既存規則)
- `C:\Users\tensh\eigo-radio\OPEN_ITEMS.md` Grep `OPEN-356`のみ(本委任ではSSOT編集しない。読むだけ)
- `C:\Users\tensh\eigo-radio\docs\pm\PM_GOVERNANCE.md` Grep `11-7`(既定OFF一般例外)— 本案件はAPPROVED_FOR_PRODUCTIONのためbranch上での既定ON配線は許容されるが、mainへは委任_07まで入れない。11-7の例外機構(flag)は使わない。

## やること(EN側のみ。JA(`er007_ja_secondary_asr_01.evaluate_attempt_ja_with_cascade_detail` L383付近)は委任_04で、触らない)
A. **EN配線(adapter置換)**: `er006_secondary_asr_01.evaluate_attempt_with_cascade_detail` の内部を、統一judge(`er078_asr_unified_judge_01`)を呼ぶadapterに置換する。契約:
   - 既存の戻り値型・呼出元のキー(cascade_detail等)は維持(呼出元の全点をGrepで列挙し、1点ずつ互換を確認して報告)。
   - 既存P-chain(Primary分類器)の結果から`PrimaryResult`を組み立て、`equivalence_basis`(HOMOPHONE_MATCH_NUMBER_EXCEPTION / TIER1_DIFF_ANCHORED / TIER1_NUMERIC_EQUIVALENCE / READING_MATCH)と`signals`(c2_homophone_candidate / c1_proper_noun_diff / similarity)を必ず埋める。
   - Secondary許容集合は既存`should_pass`集合を`secondary_accept_fn`で注入(judgeへ再実装しない)。
   - Primary NG→原則Secondary 1回。Secondary PASS→`PASS_WITH_WARNING`として自動採用。Secondary障害(例外・timeout・空転写)はPASS扱いせず`NG_SECONDARY_UNAVAILABLE`。同一wav+engine+lang+phrase_hashのSecondary重複呼出はSecondaryCacheで防止(失敗はcacheしない)。
   - 値ガード: DIFF→`NG_PROTECTED`(Secondary PASSでも採用しない=ユーザー指示「重大内容差を誤採用しないことを優先」)。AMBIGUOUS→P3(Secondary 1回)→同表層のみ`NUMERIC_AMBIGUOUS_SURFACE`警告でPASS_WITH_WARNING。最終ANDゲートは承認済みequivalenceを再否定しない。
   - `_is_number`のマーカー付きtoken認識拡張(追補§2)を同一commitで入れる。既存er021 testが全てPASSすることを確認(PASSしないなら拡張を修正、既存testの期待値は変えない)。
   - Prompt/モデル/Voice/速度/既存QA/HR Lock/予算guardは無変更。COST_GUARD($0.05/segment)は本委任で「統一judgeで等価に適用」か「無効化の根拠」を確定し、`COST_GUARD_IN_UNIFIED_JUDGE`を更新(無効化の場合はDESIGN_01 §6競合との整合をファイル:行で示す)。
   - `tts_generation_results.json`の各segment直下へadditiveキー`asr_judgement`(=`JudgeResult.audit_record`)を書く。既存音声再利用時は`asr_judgement_inherited`。既存キーの意味変更禁止。
B. **registry配線**: 生成完了時(ENのTTS結果確定後の既存hook地点を特定して報告)に `er078_pass_with_warning_registry_01` のderiveを呼び、`audit/pass_with_warning_listening_list.json`を出力する。derive失敗は生成を失敗させない(warningログ+レポート)。
C. **試聴ページ節**: `user_test/<run>/index.html`生成器(Grepで特定)に「事後試聴リスト(PASS_WITH_WARNING)」節を追加(segment id・警告ラベル・Primary/Secondary転写・値ガードkind・mp3リンク)。legacy standalone(既存の単独ページ形式)にも同節。0件のときは「0件」と明記した節を出す(節自体を省略しない)。
D. **新ラベル下流洗い出し(OF-AUW-17)**: `NUMERIC_AMBIGUOUS_SURFACE`/`LR_REWRITTEN`/`JA_NUMERIC_IRREGULAR_READING`/`NG_PROTECTED`/`NG_SECONDARY_UNAVAILABLE`/`PASS_WITH_WARNING`等の新ラベルについて、既存のallowlist・count集計・summary・HR queue投入条件をGrepで洗い出し、未知ラベルで例外・取りこぼしが起きないよう更新。更新点を表(ファイル:行/旧/新)で報告。
E. **静的監査**: allowlistを「EN配線済み・JA未配線」の状態に更新(`phase`の設計は委任_02bのtestコメント手順に従う。必要なら`post_wiring_en`等の中間phaseを追加し、ENのentrypointから統一judgeへ到達すること・JA経路が未到達であること・judge/adapter以外のASR呼出が0であることをtestでassert)。
F. **test**: 新規/更新adapter test(Primary PASS/Primary NG→Secondary PASS→PASS_WITH_WARNING/Secondary障害→NG_SECONDARY_UNAVAILABLE/値ガードDIFF→NG_PROTECTED(Secondary PASSでも)/AMBIGUOUS→P3/重複呼出防止/`asr_judgement`書込/registry出力/ページ節0件・N件)。全てmockでAPI呼出0。既存影響: `er021*test*.py er007*test*.py er006*test*.py er078*test*.py` を実行し結果を数値で報告。
G. **既存14 FAILの前提確認**: 委任_02bが「既存FAIL」と報告した14件(er007_ja_secondary_asr_01_test 2/er006_asr_provider_routing_01_test 2/er006_kp5_canonical_bug_01_test 4/er006_model_routing_pricing_coverage_test_01 1/er006_secondary_asr_01_m1_wiring_test_01 1/er006_secondary_asr_01_test 4)を、**mainのworktree `C:\Users\tensh\eigo-radio-crbn`(er078未導入)**で同じtestを実行して同じ14件がFAILすることを確認(clean HEAD突合の代替)。一致しなければ差分を報告し、本委任の変更が原因か切り分ける。`er006_secondary_asr_01_test`の4件は本委任で同ファイルを改変するため、改変前後で同一の4件であることも確認。
H. **IMPLEMENTATION_03.md**(`er058_output/unified_all_roles_production_wiring_01/`)に: 配線点一覧(ファイル:行)/呼出元互換表/状態→戻り値マッピング/COST_GUARD結論/新ラベル下流更新表/registry hook地点/ページ節のscreenshot代替(生成HTMLのpath+該当節抜粋)/test結果/静的監査snapshot/未実装(JA=委任_04、A2減速・Dialogue・KP 3回=委任_05)/逸脱。

## 禁止・境界
- JA配線・A2減速・Dialogue・KP max_attempts変更には触らない(委任_04/05)。
- Prompt・モデル・Voice・速度・閾値・既存Gate・HR Lock・予算guardの変更禁止。新しいSection固有例外の追加禁止。
- 有料API呼出0。runtime evidence(Melos regression等)は委任_06。
- SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)編集禁止(委任_07)。
- U1(`U1_KEEP_C1_SIMILARITY_EXCLUSIONS=True`)/U2(`A2_ONLY`)は現状維持。変更禁止。
- 設計上「新仕様判断が必要」「重大競合」「既存testの期待値を変えないと通らない」事態が出たら、その箇所を実装せずSTOPし、事実(ファイル:行・観測値)と選択肢を報告。
- 「技術的には仕様どおり」だけでACCEPTEDにしない。EN配線後に、Primary NG・Secondary PASSの音声が最終成果物で`PASS_WITH_WARNING`として採用され、かつ試聴リストに載ることをtestのend-to-end(mock)で示す。

## commit/push
明示ファイル指定で`git add`→`secret_scan --staged` hits=0→commit(message: `ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 委任_03: EN統一judge配線(adapter)+_is_numberマーカー拡張+PASS_WITH_WARNING registry+試聴ページ節+静的監査EN配線済み。JA未配線、main無変更、JPY0`)→`git push origin feat/auw-unified-asr-01`。mainへpushしない。`docs/pm/RESULT_PACKET_AUW3.md`(gitignore対象)へ詳細。

## 報告様式(受入記録5項目を含む)
(1)当初目的・要求された最終状態 (2)実際に生成・残存した最終成果物(成功/失敗双方) (3)証拠(ファイル:行・観測値) (4)目的要件との一致/不一致(A〜H項目ごと) (5)最終判定と理由。加えて: T-0結果/merge結果/test数値(新規・既存・14件突合)/COST_GUARD結論/新ラベル下流表/静的監査snapshot/逸脱・未確認・判断した箇所/委任_04への注意点/commit hash/費用。
