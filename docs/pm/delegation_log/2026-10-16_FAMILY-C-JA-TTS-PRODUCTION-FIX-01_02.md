## 管理ID

`FAMILY-C-JA-TTS-PRODUCTION-FIX-01` 委任_02(実装+test+0円dry-run+Production正式経路のruntime evidence+SSOT反映+commit/push)。並行: AUW 委任_09(read-only調査、進行中)、DQI 委任_02(文書作成のみ、Git操作なし)。**Git操作(commit/push)は本委任だけが行う。** 他委任が作った未追跡ファイルはaddしない(明示add対象のみ)。

## 前委任(FCJ 委任_01)の受入記録(Gate 7)
- 当初目的(ユーザー原文逐語、`docs/pm/delegation_log/2026-10-16_FAMILY-C-JA-TTS-PRODUCTION-FIX-01_01.md` L19-57): 「到達目標：正式Production経路で日本語音声生成・検証・再利用整合が正常動作すること」「単なる"en"→"ja"の置換だけで安全に解決できるなら、過度な改修はしない。ただし、単一行の修正だけで品質・再利用整合を確認せず完了としない。」
- 最終成果物: `er079_output/family_c_ja_tts_production_fix_01/INVESTIGATION_01.md`(調査・是正設計)。
- 証拠: runner L389-390/L484-500/L641/L807-831(言語経路欠落)、L303/L349-355(reuse_from由来未検査・meta非複製)、06d `cja` debug.json(長さ見積5.50秒=en扱いの1語計算)。
- 一致・不一致: 調査目的には一致。Opus条件Aレビューで由来照合設計にMAJOR 3件(自己参照・コピー手順・偽陰性未測定)が見つかり、設計はそのままでは不十分→本委任で是正。
- 判定: 委任_01=ACCEPTED(計画)。実装は本委任。
- QDC: 目的=Family C JA新規TTS成功+reuse整合/試行=調査1回/原因=言語経路欠落+reuse由来未検査(確定)/費用=JPY0/改善見込み=高/次の一手=本委任。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー承認済み(2026-10-16指示B)の既存Production不具合是正。到達上限Status: `FIX_IMPLEMENTED_EVIDENCE_PENDING_FABLE`(Fable独立照合後に`PRODUCTION_WIRED`相当の判定。本委任は`PRODUCTION_WIRED`と書かない)。
- 禁止: `git add -A`/`-f`、amend、rebase、force push、stash、clean、`reset --hard`、`checkout -f`、STOPセンチネル削除・回避、HR Lock迂回・変更、新Voice採用(Voiceは既存`p9a.VOICE_NAME`=Aoedeのまま)、音声品質基準・Comment内容仕様の変更、tts_safe_ja/cool-down/N1再生成対象拡張の持込み(Legacy Family Cへの新規実装になる)、Family C全体のStatus格上げ、新規コード(コメント・関数名含む)に`asr_verified`/`evaluate_attempt*`/`classify_*asr_match`/`unified_judge`の語を書くこと(`er078_asr_unified_wiring_static_audit_01.py:479-482`の制約)、`er078_reuse_value_guard_01.py`の変更。
- **条件付きSTOP(Fable判断へ戻す。有料実行前に判定)**: (a)0円の記号Gate事前検査でJA文面(Comment1〜3・japanese_title・preview)に禁止記号が見つかり文面修正が必要になる場合(Comment内容仕様に触れる)。(b)reuse plan dry-runで、ユーザーが試聴承認済みのepisode音声が新ルールで再生成対象になる場合(承認済み音声の差替えになる)。いずれもRESULT_PACKETに事実を書きSTOP(Run A/Bを実行しない)。
- Opus独立技術レビューGate(11-3): 条件A **実施済み**(2026-10-16、Fableが採否決定済み。下記「Opus指摘の反映要件」)。原文はjsonlから機械抽出して保存する(後述)。Sonnetは抽出本文を読まなくてよい。
- 時間見込み: 全体2.5〜4時間(実装60〜90・test 30〜45・dry-run 15・evidence 20〜30・SSOT/Git 30)。並列化: Run A/B/C'は独立だがstate共有の確認のため直列(理由: HR queue/attempt_history等の追記先が同一)。
- 費用/日次: 当日(2026-10-16 JST)既使用=AUW 07/07b 約JPY1.3確認済み(他は未確認)/残 約JPY998/本委任見積 期待約JPY4(JA 5 clip+Run B 最大3 clip、根拠=`RUNTIME_EVIDENCE_06.md:113` JPY0.062/clip TTS+`:320` 実測約JPY0.46/attempt、最大3 attempt/clip)/改善見込み 高/承認区分: C(承認済みscope内)。
- T-3定型文: 「上限¥11(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」有料runの再起動は禁止(26節。途中終了したら事実を記録し再実行せずFableへ)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。(定型文は上記「性質」欄に記載)

T-0保存先: `docs/pm/delegation_log/2026-10-16_FAMILY-C-JA-TTS-PRODUCTION-FIX-01_02.md`(全文保存、要旨化禁止)。

## ユーザー指示(原文)

`docs/pm/delegation_log/2026-10-16_FAMILY-C-JA-TTS-PRODUCTION-FIX-01_01.md` L19-57(B-1〜B-4の逐語引用)を正とする。origin/mainには委任_08が保存した全文 `docs/pm/delegation_log/2026-10-16_AUW-FAMILY-C-DQI-USER-INSTRUCTION.md` があり、手順0のffで取得できる。

## Opus指摘の反映要件(Fable採否: 全件採用。実装の必須条件)
- R1(FCJ-01 MAJOR) 由来照合の自己参照排除: `reuse_from`経由の由来証拠として`upgraded_from_legacy_ok:true`のmetaを**使わない**。audit(`tts_generation_results.json`)経由は`reused`が偽(新規生成記録)のentryのみ受け入れる。それ以外は再生成。06d `cja_attempt*`等のバグ期出力dirは汚染資産として一覧化・記録し、reuse_from元として使わない。
- R2(FCJ-02 MAJOR) 受理経路のコピー方法: 照合を通ったら、コピー先のwav/.ok/.ok.meta.jsonを削除してからsrc wavをコピーし、`{tts_text_sha256, wav_sha256(src実測), reuse_from_source, provenance_basis}`を照合関数自身が書き込む。`_copy_with_ok`の「上書きしない」挙動・レガシー分岐に乗せない。
- R3(FCJ-03 MINOR) 新規TTS呼出前にout_pathの`.ok`と`.ok.meta.json`を削除(失敗attempt wav+古い.okの同居による無条件再利用を防ぐ)。
- R4(FCJ-04 MAJOR) 偽陰性の実データ測定: 0円「reuse plan dry-run」=全`article_config.json`の`reuse_from`先についてclipごとに(meta正規/legacy-upgraded/metaなし、audit上`reused`有無、新ルール判定=再利用/再生成)を一覧化。**ユーザー試聴承認済みepisodeの音声が再生成対象なら条件付きSTOP(b)**。
- R5(FCJ-05 MINOR) INVESTIGATION 5-4節の「通算3回目cool-down適用」は誤り(cool-downは`cooldown_total_budget`が渡された場合のみ。Family Cは渡さない)。記述訂正のみ、cool-down追加はしない。
- R6(FCJ-06 MINOR) Run A前に0円の記号Gate事前検査(Layer-4: 括弧`()（）[]`・`/`・`〜`・`…`・`:;：；`)をJA 5文面に実施。違反があれば条件付きSTOP(a)。
- R7(FCJ-07 MINOR) Run Bは文面を編集する場所(reuse_src側/出力dir側)を明記し、成果物を「test fixture(Comment Contract未経由)」と表示(納品物扱いにしない)。`--only-segments comment_N`では原稿再生成判定が真なら3本とも再生成になる点を明記。
- R8(FCJ-08 MINOR) 禁止語を新規コードに書かない(上記)。
- R9(FCJ-09 MINOR) 非en言語ガード(非narrator voiceでen以外→RuntimeError)は関数先頭(`budget.check_before`より前)。`run_simple_narrator_asset`が`language`を渡すことのtest追加。
- R10(FCJ-10 MINOR) `CURRENT_SPEC.md:1119`のFamily C Status(`APPROVED_FOR_PRODUCTION / WIRING_INCOMPLETE`)は格上げしない。`RUNTIME_EVIDENCE_06.md:370`「C runnerから統一ASR判定に到達しない」はDangling更新対象(追記で注記)。
- R11(FCJ-11 MINOR) runner内部予算見積がclip 1回分のみ(実際は最大3 attempt)である点を記録。harness meterを実費の上限管理とし、hard_stop余裕として記録。metaに言語・voice・modelを持たない点はOPEN候補として記録(実装しない)。
- 追加test(β): R1用(legacy-upgraded metaと`reused` auditからは再利用しない)、R2用(既存dstを確実に置き換える)、R3用(TTS失敗後に`.ok`が残らない)。既存静的testの独立項目は不要。
- 追加evidence Run C'(0円): Memory A2を`reuse_from`に指定し空の出力dirで実行、TTS関数を「呼ばれたら例外」に差し替えて走らせ、偽陰性があれば0円で検出。

## KPI provenance欄

- JA新規TTS成功(Run A 5 clip): `production_formal_path`(fresh)。
- 原稿変更時の誤再利用なし(Run B): `production_formal_path`(fresh、test fixture表示)。
- 偽陰性0(Run C'・dry-run): `frozen`(保存データ)+`synthetic`(TTS例外差替え)。
- 英語回帰: `reuse`(既存test)+Run C'(Story/topic_intro_enがAPI 0で再利用される)。
- E2E自己確認「fresh Production初回pathを含むE2E値か」: Run A=Yes、他=No。

## Opus台帳更新

`docs/pm/OPUS_FINDINGS_LEDGER.md`に`OF-FCJ-01`〜`OF-FCJ-11`を追加(RAISED→FABLE_DECIDED(採用)→IMPLEMENTED/EVIDENCEDを本委任の実績で記入)。追記のみ。

## 事前指定Read一覧

- `er079_output/family_c_ja_tts_production_fix_01/INVESTIGATION_01.md` 全文(自分の前委任成果。第5〜7・10節を主に使用)。
- `er013_family_c_production_runner_01.py` L295-430(reuse系・`tts_call_for_voice`・`to_audit_entry`)、L480-505、L585-650、L740-760、L800-835。
- `er003_v1_repro01_main_generate.py` L283-292(記号Gate・length_ok)、L314-335(model/ASR lang/cool-down条件)、L346-390(Validator分岐)。
- `er003_audio_tts_asr_safety.py` L171-203(長さ見積)、L987-995・L1026-1083(記号Gate)。
- `er078_reuse_value_guard_01.py` L1-71(変更しない。前段条件としての関係確認)。
- `er078_asr_unified_wiring_static_audit_01.py` L470-500。
- `er058_output/unified_all_roles_production_wiring_01/RUNTIME_EVIDENCE_06.md` L300-380(06d cja・費用単価)。
- `er013_family_c_production_test_01.py` 全体構造(Grep `def test_`で一覧→影響箇所のみRead)。
- `CURRENT_SPEC.md` L1047-1137・L1553-1560。`OPEN_ITEMS.md` Grep `OPEN-372 `。

## 事前指定Grep一覧+追記位置・更新位置の手順

1. Opus原文の保存: jsonl `C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\tasks\a6309c381506f53d1.output`(**Read toolで開かない**)から、scratchpadの抽出script(`...\scratchpad\extract_opus_fcj.py`: 各行json.loads、`type=="assistant"`のcontent内`type=="text"`で「# FAMILY-C-JA-TTS-PRODUCTION-FIX-01 Opus独立技術レビュー」を含む最後のtext)で `er079_output/family_c_ja_tts_production_fix_01/OPUS_REVIEW_A_01_VERBATIM.md` へ逐語保存(冒頭にsha256・文字数)。`.venv\Scripts\python.exe -I`で実行。
2. `CURRENT_SPEC.md` Family C節(L1047-1137)末尾に追記(既存行不変): 「追記(2026-10-16 `FAMILY-C-JA-TTS-PRODUCTION-FIX-01`): 日本語Section(Comment1〜3・japanese_title・preview_ja)のTTSは`generate_narration_snippet_verified_strict(text,"ja",...)`(Voice=`p9a.VOICE_NAME`、Trial-11/12で試聴OK済みの既存呼出)で生成し、JA ASR Validator経由。reuse_fromは由来照合(text sha256+wav sha256、legacy-upgraded meta・`reused` auditは由来証拠にしない)を通過した場合のみ再利用。Family C全体のStatusは不変(`APPROVED_FOR_PRODUCTION / WIRING_INCOMPLETE`)。本是正はユーザー2026-10-16明示承認によるLegacy Family Cへの例外的是正(Family体系の条件1・3は引き続き有効、tts_safe_ja・cool-down・N1再生成対象拡張は持ち込まない)。証跡=`er079_output/family_c_ja_tts_production_fix_01/`。」
3. `DECISION_LOG.md` 末尾に新節「FAMILY-C-JA-TTS-PRODUCTION-FIX-01(2026-10-16)」: ユーザー承認原文の位置(`docs/pm/delegation_log/2026-10-16_FAMILY-C-JA-TTS-PRODUCTION-FIX-01_01.md:19-57`)、不具合2系統、是正内容、Opus条件A指摘FCJ-01〜11の反映、evidence結果、Status。索引に1行追加。
4. `OPEN_ITEMS.md` OPEN-372行に行内追記: 「【2026-10-16 FCJ 委任_02】是正実装・evidence取得(結果はDECISION_LOG参照)。Status=<結果に応じて 是正済み・Fable判定待ち / 一部残>」。新規OPEN候補(meta言語・voice・model欠如、japanese_title/preview_jaが`--only-segments`非対応、`disfluency_checked`固定、`expected_substring`無意味)は**新規OPEN-381〜として起票**(区分POST_USER_VALIDATION、担当Sonnet→Fable、1行ずつ)。
5. `er058_output/unified_all_roles_production_wiring_01/RUNTIME_EVIDENCE_06.md` L370付近に注記追記「(2026-10-16 FCJ是正後はC runnerからJA Sectionでも統一判定に到達。`er079_output/.../EVIDENCE_02.md`)」。
6. `docs/pm/REPORT_LEDGER.md`に`FAMILY-C-JA-TTS-PRODUCTION-FIX-01`行を追加(初回報告未)。
7. `docs/pm/ACTIVE_TASK.md`(gitignore対象、commitしない)のFCJ Statusを更新。

## 実行コマンド全文

手順0(作業ツリー同期、main dirで): `cd C:\Users\tensh\eigo-radio; git fetch origin; git merge --ff-only origin/main`(現在branch=`feat/auw-unified-asr-01`、b010cb469→fbebfc895へff。失敗なら理由記録して続行) → `git checkout -b work/post-merge-01`(同一commitからの新branch作成。未commit変更があっても通る。失敗時は現branchのまま続行し記録)。`git status --porcelain | Measure-Object -Line`を記録。
手順1(STOP確認): `.venv\Scripts\python.exe tools\stop_scope_check_01.py --managed-id FAMILY-C-JA-TTS-PRODUCTION-FIX-01 --run-dir er079_output\family_c_ja_tts_production_fix_01\evidence_02`(dir未作成なら先に`New-Item -ItemType Directory`)。rc≠0なら有料実行しない。
手順2(実装): `er013_family_c_production_runner_01.py`(言語引数・由来照合関数・R2/R3/R9)、新規test `er079_family_c_ja_tts_fix_02_test_01.py`(β+追加3件)、harness `er079_family_c_ja_evidence_01.py`(INVESTIGATION 第7節案+R4 dry-run+Run C'。費用meter・hard_stop JPY11・STOPセンチネル監視を内蔵)。
手順3(0円検査): `.venv\Scripts\python.exe er079_family_c_ja_evidence_01.py symbol_gate_check --out er079_output\family_c_ja_tts_production_fix_01\evidence_02\symbol_gate_check.json` / `.venv\Scripts\python.exe er079_family_c_ja_evidence_01.py reuse_plan_dryrun --out er079_output\family_c_ja_tts_production_fix_01\evidence_02\reuse_plan_dryrun.json`(全article_config.jsonを走査。ユーザー試聴承認済みepisodeの特定は`CURRENT_SPEC.md`Family C節・`docs/pm/USER_DECISION_REGISTER_01.md` Grep `Family C`/`memory`/`twins`で承認記録を探し、根拠file:lineを出力に含める)。→ 条件付きSTOP(a)(b)判定。
手順4(test、API 0、netguard付き): `.venv\Scripts\python.exe -m pytest -p netguard er079_family_c_ja_tts_fix_02_test_01.py er013_family_c_production_test_01.py -q -p no:cacheprovider`(`PYTHONPATH`にscratchpadのnetguard.pyを含める。委任_08と同じ方法: `$env:PYTHONPATH="C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad"`。無ければ`Get-ChildItem C:\Users\tensh\AppData\Local\Temp\claude -Recurse -Filter netguard.py`で探し、見つからなければ同等のsocket遮断pluginをscratchpadに作成)。続けて静的監査 `.venv\Scripts\python.exe -m pytest -p netguard er078_asr_unified_wiring_static_audit_01.py -q -p no:cacheprovider` と `.venv\Scripts\python.exe er078_asr_unified_wiring_static_audit_01.py`(差分空)。AUW中核のうちFamily C関連 `er078_asr_unified_wiring_06d_test_01.py` も実行。
手順5(Run C'、API 0): `.venv\Scripts\python.exe er079_family_c_ja_evidence_01.py run_c_prime --reuse-from <Memory A2の出力dir実パス> --out er079_output\family_c_ja_tts_production_fix_01\evidence_02\run_c_prime --tts-raise`。
手順6(Run A、有料): `$env:TTS_EXECUTION_MODE="STANDARD"; .venv\Scripts\python.exe er079_family_c_ja_evidence_01.py run_a --out er079_output\family_c_ja_tts_production_fix_01\evidence_02\run_a --budget-jpy 11 --execute`(Production正式entry=`er013_family_c_production_runner_01.py`のmain経路を呼ぶこと。LLM 0 call=comments_ja.mdを再利用。実行前にT-2追記(1)〜(4)を確認し記録)。
手順7(Run B、有料・最大3 clip): `$env:TTS_EXECUTION_MODE="STANDARD"; .venv\Scripts\python.exe er079_family_c_ja_evidence_01.py run_b --out er079_output\family_c_ja_tts_production_fix_01\evidence_02\run_b --budget-jpy 11 --execute`(R7の明記。Run A/Bの合計がJPY11接近時はT-3定型文に従う)。
手順8(証跡文書): `er079_output/family_c_ja_tts_production_fix_01/EVIDENCE_02.md`(各Runの結果表: clipごとの判定state[PASS/PASS_WITH_WARNING/NG_*]・Primary/Secondary呼出回数・Secondary重複0・HR queue追記行数・試聴リスト登録・費用meter実測・model_id/voice実測・shared_state変化・STOPファイル有無、dry-runの偽陰性件数、Run C'結果、Dangling Reference Check、B-4完了条件9項目の充足表)と`IMPLEMENTATION_02.md`(差分説明、R1〜R11対応表)。
手順9(SSOT・Git): Grep手順2〜6。secret scan(`tools\*secret*`の実名で、`--paths`指定で変更ファイルを走査)hits=0 →
`git add er013_family_c_production_runner_01.py er079_family_c_ja_tts_fix_02_test_01.py er079_family_c_ja_evidence_01.py er079_output/family_c_ja_tts_production_fix_01/INVESTIGATION_01.md er079_output/family_c_ja_tts_production_fix_01/OPUS_REVIEW_A_01_VERBATIM.md er079_output/family_c_ja_tts_production_fix_01/IMPLEMENTATION_02.md er079_output/family_c_ja_tts_production_fix_01/EVIDENCE_02.md er079_output/family_c_ja_tts_production_fix_01/evidence_02 CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/REPORT_LEDGER.md docs/pm/OPUS_FINDINGS_LEDGER.md er058_output/unified_all_roles_production_wiring_01/RUNTIME_EVIDENCE_06.md docs/pm/RESULT_PACKET_FCJ1.md docs/pm/RESULT_PACKET_FCJ2.md docs/pm/delegation_log/2026-10-16_FAMILY-C-JA-TTS-PRODUCTION-FIX-01_01.md docs/pm/delegation_log/2026-10-16_FAMILY-C-JA-TTS-PRODUCTION-FIX-01_01.md_check.json docs/pm/delegation_log/2026-10-16_FAMILY-C-JA-TTS-PRODUCTION-FIX-01_02.md docs/pm/delegation_log/2026-10-16_FAMILY-C-JA-TTS-PRODUCTION-FIX-01_02.md_check.json`(存在しないもの・gitignore対象は除外し記録。`evidence_02`配下のwavが大きい場合はwavを除きjson/log/mdのみadd、除外一覧を記録)
`git commit -m "FAMILY-C-JA-TTS-PRODUCTION-FIX-01 委任_02: Family C日本語Section TTS言語経路修正+reuse_from由来照合(Opus FCJ-01〜11反映)+test+runtime evidence(JPY <実費>)"`
mainへの反映: `cd C:\Users\tensh\eigo-radio-crbn; git checkout main; git pull --ff-only origin main; git merge --ff-only work/post-merge-01`(ff不可なら`git merge --no-ff work/post-merge-01 -m "merge work/post-merge-01 (FCJ 委任_02)"`、競合時は中止報告)`; git push origin main`。main dir側: `cd C:\Users\tensh\eigo-radio; git fetch origin; git merge --ff-only origin/main`。
条件付きSTOP(a)(b)に該当した場合: 手順6以降を実行せず、実装・test・dry-run結果まででcommit(メッセージ末尾に「有料evidence未実施・条件付きSTOP(a|b)」)し報告。

## SSOT追記文

上記Grep手順2〜6の文面(実値に置換)。

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: **あり**(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/OPUS_FINDINGS_LEDGER.md`、追記のみ・既存行不変)。`PM_GOVERNANCE.md`は編集しない。
- 他委任の未追跡ファイル(`docs/research/.../dqi/*`、`er058_output/.../U1_U2_SECTION_PLAN_09.md`、`RESULT_PACKET_AUW9.md`/`_DQI*.md`)はaddしない。
- test副作用で変化した本番state file(`er011_output/attempt_history.jsonl`等)はaddしない。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_FCJ2.md`: 1 T-0・Opus原文保存(sha256) / 2 実装差分要約(ファイル:行、R1〜R11対応表) / 3 test結果(新規β件数・既存39・静的監査・06d) / 4 0円検査結果(記号Gate違反件数、dry-run偽陰性件数・汚染資産一覧・承認済みepisode該当有無、条件付きSTOP判定) / 5 Run C'結果 / 6 Run A/B結果(clipごと判定・Secondary重複・HR queue・試聴リスト・model_id/voice・費用meter実測、途中終了の有無) / 7 B-4完了条件9項目の充足表(達成/未達/理由/証拠) / 8 SSOT・OPEN新規起票番号・commit hash・push結果・secret scan / 9 逸脱・新規発見 / 10 費用実測(出典=meter/usage_log)・所要時間 / 11 受入記録5項目(当初目的=B-1/B-2/B-4原文逐語/最終成果物[失敗終了時含む]/証拠/一致・不一致/判定)。`PRODUCTION_WIRED`は宣言しない。
