# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01 委任_02b(Opus_J逐語保存+必須修正M-1〜M-5/任意改善S-1〜S-8のFable採否反映[設計v02]+判定注入の是正とgolden replay test+Phase A再注入+追加負例(minimal pair)生成+本番既存takeの再利用集合+Phase B/C Azure実走+評価+Closeout文書+簡易試聴ページ+SSOT)。2026-10-20。
並行タスク衝突確認: 並行委任なし(委任_02a完了 commit 20c1dd54a/a21103942、Opus_J完了)。SSOT編集権: あり(`OPEN_ITEMS.md` OPEN-424行、`DECISION_LOG.md`末尾、`docs/pm/USER_DECISION_REGISTER_01.md` #124行、`docs/pm/REPORT_LEDGER.md`、`docs/pm/OPUS_FINDINGS_LEDGER.md`新規行。Grep→該当行のみ)。`CURRENT_SPEC.md`は編集しない(Production非変更)。

## 性質/到達上限Status/禁止事項
- 性質: Trial(Trial専用経路)。Production module・Prompt・判定・設定は変更しない(`er006_secondary_asr_01.py:288`のコメントも不変)。
- 到達上限Status: `PLW_TRIAL_CLOSEOUT_PENDING_FABLE`(Trial StatusはVALIDATED候補/REJECTED/判断候補/INCONCLUSIVEをevalが機械判定し、最終ラベルはFable。`USER_DECISION_REQUIRED`ラベルはFableのみ)。Production採用はユーザーのみ。
- 禁止: (1)A案/A'案/P1/P2の実装・暗黙採用。(2)重み1.25/1.75等、承認3値(1.0/1.5/2.0)以外の重み条件の実走(S-5: 承認を要約で広げない。必要と判明した場合は判断候補としてRESULT_PACKETへ)。(3)Production成果物(run_e2e_*/HR queue/attempt_history/telemetry/ledger)への書込み。(4)`git add -A/-u/-f`・amend・rebase・force push・stash。(5)wavのcommit。(6)結果を見てから閾値・条件を変える(v02は実走前にcommit、以後の変更は§9に理由付きで記録)。(7)**Phase B実走の機械Gate**: golden replay test(M-1)がPASSし、かつdry-runの見積が上限内でなければAzure実走を開始しない(満たさなければSTOPして報告)。
- 修正範囲の線引き(11-8): Trial harnessの不具合(M-1/M-2)は是正範囲内。Production判定ロジックは呼ぶのみ。
- Opus独立技術レビューGate(11-3): 任意レビューOpus_J済み(GO_WITH_CHANGES)。本委任で設計が変わる点はOpus_Jの修正案に沿うため再レビュー不要。Production採用提案時は条件C(別途)。
- 費用/日次: 当日既使用JPY49.70(出典: RESULT_PACKET_PLW2a.md adopted)/残JPY950.30/本委任見積JPY約150(内訳: Phase B合成42wav×4条件[no_pl/unspec/1.5/2.0]≈JPY37+w1.0・rep2各10%抜き打ち≈5、追加負例minimal pair 27wav[TTS≈3・Primary≈3・Azure×4条件≈19]、本番既存take再利用≤20本×4条件≈85[24秒/本換算]、一般化probe≤JPY15、Primary再現確認含む)/案件合算=20.91+150=約171、C予備を含め上限¥200(案件合算≤300)/改善見込み高/承認区分C(ユーザー承認済みTrial・300円以下・日次内)。
- T-3: 上限¥200(Guardrail、本委任分。案件合算300円以下)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。案件合算が300円を超える見込みになった時点で実走を止めFableへ報告(7-7)。
- 時間見込み: 全体4〜6h(Opus逐語+v02 40分/judge是正+golden test+Phase A再注入 60分/追加負例TTS+Primary 30分/本番take選定 30分/Phase B Azure実走 60〜90分[逐次]/eval・Closeout・試聴ページ 60分/SSOT・報告 30分)。並列化: 追加負例TTSと本番take選定はjudge是正と並列可。Azure実走はwavごとにprocess分割可(SDKログ名分離)。直列化理由: 実走はgolden test PASS後。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。**保存は自分で打ち直さず、`extract_delegation_from_jsonl_01.py`でsession JSONLから抽出する**(委任_02a再開で実績: `--role assistant --tool-use-name Agent --tool-input-field prompt --index <N>`、本文の管理ID行に`委任_02b`を含む最初のものを採用)→`docs/pm/delegation_log/2026-10-20_FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01_委任_02b.md`。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`): TTSを伴う委任は`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する(追加負例TTS)。Batch不使用。T-2追記(7-5)4点: (1)差分生成=追加負例のみ(既存42wavは再利用)、(2)既存音声再利用=42wav+本番既存take(TTS 0)、(3)`--budget-jpy`明示、(4)全再生成ではない。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`): 定型文は上記「性質」欄に記載済み。

## ユーザー指示(原文、該当部抜粋。全文=`docs/pm/delegation_log/2026-10-20_FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01_USER.md`、sha256 7d7b9e16…)
> 重要なのは、**認識してほしい固有名詞を含む正例だけでなく、本来Melosと認識してはいけない負例も設けること。**
> **固有名詞の認識率が上がっても、実際の誤発音を見逃すリスクが増えるなら、単純に成功と判断しない。**
> ASR転写の改善だけでなく、既存のProduction判定ロジックに通した際に、- NGがPASSへ変わるか - PASS_WITH_WARNINGになるか - TTS retryやHuman Reviewを回避できるか - 本来NGとすべき音声を誤PASSしないか を確認する。判定ロジック自体は変更しない。
> - API費用を抑えるため、既存音声・キャッシュ・既存研究成果を優先利用する。 - 独立した比較や分析は並列化する。 - 結果が出なければ同じ条件を機械的に繰り返さず、何が識別できていないかを分析し、別の文脈・音声へ切り替える。 - すでに品質上十分な結論が得られたら、過剰な追加Trialを行わずCloseoutする。
> **Trial StatusはREJECTED／VALIDATED／USER_DECISION_REQUIREDのいずれかでCloseoutする。** VALIDATEDでもProduction採用は自動で行わない。
> 特に、1.0と2.0に差が出なかった場合でも、単に「差がなかった」と報告するのではなく、- 条件が簡単すぎて差が出なかったのか - Phrase Listがほとんど効いていないのか - 既に1.0で十分効いているのか - 文脈・音声品質によって効果が変わるのか - 実用上、重み調整では解決できないのか を、得られた証拠に基づいて整理すること。
> **最終目的は、特定の重みでMelosを一度正しく認識させることではなく、一般的な固有名詞の誤認識を減らし、不必要なTTS再生成・Human Reviewを削減できるか判断すること。**

## Opus台帳更新
`docs/pm/OPUS_FINDINGS_LEDGER.md`へOpus_J(M-1〜M-5、S-1〜S-8)を新規行で登録(ID例`OF-PLW-J-01`〜、委任_07で追加した`OF-FZAQ-G-01`と同じ10列書式)。状態=RAISED→FABLE_DECIDED(下記採否)→本委任でIMPLEMENTED/TRIALED。

## Fableの採否(Opus_J)
- **M-1 採用**: judgeへ本番相当の`segment_id`(合成wavは`full_story_part1_c1`型のFULL_STORY名、本番takeは実segment名)・`enable_connected_speech_equivalence_layer=connected_speech_enabled_for(segment_id)`・本番と同じ`force_secondary`扱いを渡す。**golden replay test**: run_e2e_04 part3_c1 attempt2の記録(Primary`Mello drank`/Azure`Mellows drank`)を注入し、記録どおり`tier3_corroboration_secondary` stepが出てNG_BOTHになること、およびrun_e2e_05 Std part3_c1減速後(Primary`Mellos drank`/Azure`Melos drank`→`SECONDARY_ASR_CORROBORATED_MATCH`)が再現することをassert。PASSするまでPhase B実走禁止。Phase Aの15行をAPI 0で再注入し`PHASE_A_RESULT_01.md`に「v02再注入」節を追記(旧結果は残す)。
- **M-2 採用**: judge内でtelemetry追記関数をno-op化、`is_last_slot=False`固定(HR要否はeval側で換算)、testで次のsize/mtime不変をassert: `er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl`、`er006_output/pronunciation_ledger_01/ledger.json`、`er011_output/attempt_history.jsonl`、`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`、HR log。
- **M-3 採用**: N2(`mellows`)/N4(`Milos`)は「境界例」へ再分類(②の分母から除外し別枠報告)。負例の主軸=正例と同文脈のminimal pair: P1/P3/P4の文脈で`Mello`(s脱落)・`Melon`(別子音)・`Mullos`(許容外母音)の3種×Aoede/Charon=18 TTS take+Aoede減速9=27wav(判定用canonicalは元のMelos文)。有効負例=N1/N3(6)+27=33。誤PASS 0件でもrule of three(95%上限≈3/n)を併記。
- **M-4 採用**: 主要指標=「本番判定のflip」(Primary NGのwavでNG→PASS系の件数とPASS→NGの件数)。Melos正認識率は副指標。VALIDATED候補条件に片側exact符号検定p≤0.05(5:0/7:1/9:2…)と(文,Voice/話速)cluster≥3を追加。R<6→INCONCLUSIVEをREJECTEDより優先。録音2は確認集計から除外し参考値。悪化③に他語揺れによるNG転化を含める。`criteria_thresholds_01.json`をv02へ更新(設計書§3と同期、testで一致検査)。
- **M-5 採用**: (wav,重み)ごとに(i)新規誤り語数[ベースライン差分、Melos位置除く](ii)うち保護対象(数値・否定・固有名詞・内容語)(iii)本番判定flip(iv)Melosからの語距離。判定は2条件(FULL_STORY role=Tier3あり/Tier3なしrole[`segment_id=None`相当、KP型])の両方で集計。
- **S-1 採用(主評価集合)**: `er026_output/family_z_production_e2e_01/melos/run_e2e_0[1-5]/{a2,b1b}/narration/attempts/*.json`から「原稿にMelosを含み、Primaryが`Melos`を正転写していない(=Primary NG系)」takeを抽出(重複wav除外、wav実在確認、1 takeあたり音声秒数記録)。**上限20本**(秒数合計≤500秒を目安。超える場合は文脈多様性[segment違い]を優先して選ぶ。選定規則をv02に事前記録)。各take×{no_pl, pl_unspecified, pl_w1.5, pl_w2.0}+w1.0/rep2の10%抜き打ち。本番Primary転写は記録値を使用。PL=そのsegmentの本番`ledger_phrases`(複数名が入るならそのまま=S-4を兼ねる)。
- **S-2 採用**: `pl_w1.0`は全wavの10%抜き打ち、rep2も10%抜き打ち(決定論の再確認)。
- **S-3 採用**: 主たる重み=1.5を事前宣言(Phase Aはpilot扱い)、2.0は副。
- **S-4 採用**(S-1で自然に含まれる場合はそれで足りる。含まれなければ長文P6の1条件で複数語PL[Melos+Dionysius+Selinuntius]を追加)。
- **S-5 採用**: 1.25/1.75は実走しない。トレードオフが見えた場合は判断候補として報告のみ。
- **S-6 採用(限定)**: Closeout文言は「Melos・Family Z・2 Voice・ナレーター経路限定」。一般化probe=S-1抽出時に「Melos以外の固有名詞(Dionysius/Selinuntius等)でPrimary NG」の本番takeがあれば**最大6本**を{pl_unspecified, pl_w1.5}の2条件で流す(≤JPY15)。それ以上の一般化は条件Cレビュー前の別Trialとして提案に留める。
- **S-7 採用**: 新規wavのPrimaryは本番同一関数・モデル(`gpt-4o-mini-transcribe`、story=prompt無し)で、モデル名を記録(25節)。既に02aで実施済みの42wavは記録確認のみ。
- **S-8 採用**: evalの出力をユーザー§6の5分類(条件が簡単すぎた/PLが効いていない/1.0で既に十分/文脈・音声品質で変わる/重みでは解決できない)に対応付ける。
- 補足採用: M1凍結が現在のLedgerを読む点を設計書に注記。02aの改訂提案3点(Charon経路の制約/閾値jsonの正本化/減速実測5.4〜5.9%)もv02へ。

## 作業
W1. Opus_J逐語保存: `extract_delegation_from_jsonl_01.py --role assistant --tool-use-name SubagentHandback --tool-input-field message --index <N>`で、本文先頭が`## Opus_J レビュー結果: GO_WITH_CHANGES`のものを`docs/research/FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01/OPUS_REVIEW_J_01_VERBATIM.md`へ保存(文字数・sha256記録)。OPUS_FINDINGS_LEDGER登録。
W2. 設計v02: `TRIAL_DESIGN_01.md`を上記採否で改訂(§2-B負例・§2-C・§3指標/基準・§4費用・§9改訂履歴v02[Opus_J反映、日時、理由])、`design_matrix_01.json`/`criteria_thresholds_01.json`を同期。**実走前にcommit**。
W3. judge是正(M-1/M-2)+golden replay test(`er084_azure_phraselist_weight_trial_01_judge_test_02.py`)+Phase A再注入→`PHASE_A_RESULT_01.md`へ「v02再注入」節。
W4. 追加負例27wavのTTS(02aの`_tts.py`を再利用、`TTS_EXECUTION_MODE=STANDARD`、`--budget-jpy 6`)+Primary転写→manifest_02.json(manifest_01は不変、02は追加分+境界例再分類フラグ)。
W5. 本番take選定(S-1/S-6)→`production_takes_manifest_01.json`(run/segment/attempt/wavパス/sha/秒/本番Primary転写/ledger_phrases/選定理由)。
W6. dry-run(全Phase Bの呼出数・秒・見積JPY、上限内確認)→**golden test PASS確認**→Phase B Azure実走(`_run.py --phase B`、raw追記、SDK wire evidenceを各行に保存、逐次またはログ分離並列)→必要ならPhase C(§2-C規則: R<6なら追加take、上限内)。
W7. eval(`_eval.py`+`_eval_ext.py`、M-4/M-5指標、2 role条件、5分類対応、rule of three)→`PHASE_B_RESULT_01.md`+json、候補Status。
W8. 簡易試聴ページ(ユーザー§5): `user_test/plw_trial_01/index.html`(API 0)に、flipしたwav(NG→PASS系)全件と誤PASS(あれば)全件、境界例を、原稿/Primary転写/条件別Azure転写/判定とともに並べる(音声はmp3へ変換し`user_test/plw_trial_01/audio/`へ。本番takeのwavは再エンコードして配置、元は不変)。commit/push後にHTTP 200確認。
W9. Closeout文書 `TRIAL_CLOSEOUT_01.md`: ユーザー§6の報告9項目順(1結論/2条件別認識率/3文脈別効果とばらつき/4副作用/5録音2の改善/6本番判定・HR削減への実効性/7QCD実費/8成果物・Git・SSOT/9推奨案と判断候補)+5分類整理+限定条件(S-6)+Production採用時に必要な追加証拠(条件C)。
W10. SSOT: OPEN-424 Status更新(候補Status・実費・限定条件)、DECISION_LOG末尾(Opus_J採否・v02・結果要約)、REGISTER #124追記、REPORT_LEDGER、OPUS_FINDINGS_LEDGER状態遷移。ACTIVE_TASK先頭ヘッダ。

## 事前指定Read一覧
- `docs/research/FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01/TRIAL_DESIGN_01.md`(全体、改訂対象)、`design_matrix_01.json`、`criteria_thresholds_01.json`、`PHASE_A_RESULT_01.md`
- `docs/pm/RESULT_PACKET_PLW2a.md`(全体)、`docs/pm/RESULT_PACKET_PLW1.md`: Grep `wire_evidence|probe|judge`
- `er084_azure_phraselist_weight_trial_01_{lib,run,eval,eval_ext,judge,tts,test_01,eval_ext_test_01}.py`(Trialファイル、全体)
- `er006_secondary_asr_01.py`:233-237, 795-900, 1030-1045(M1凍結/Tier3/telemetry/HR lookup)、Grep `def evaluate_attempt_with_cascade_detail`→シグネチャ範囲
- `er020_tts_retry_local_rewrite_01.py`:120-150(role解決)
- `er003_v1_n3_01_tts_generate.py`:1105-1155(`connected_speech_enabled_for`の本番呼び方)、Grep `def connected_speech_enabled_for`
- `er021_en_asr_semantic_equivalence_production_01.py`:725-745、Grep `def append_telemetry_log`
- `er026_output/family_z_production_e2e_01/melos/run_e2e_04/a2/narration/attempts/full_story_part3_c1_attempt2_customa3c4625e.json`(golden期待値)
- `er026_output/family_z_production_e2e_01/melos/run_e2e_05/a2/audit/tts_generation_results.json`: Grep `full_story_part3_c1`→該当範囲(golden 2)
- `docs/pm/OPUS_FINDINGS_LEDGER.md`: Grep `OF-FZAQ-G-01`(書式)
- `docs/research/FAMILY-X-B3-BACKGROUND-FACT-COMPLEMENT-TRIAL-01/TRIAL_CLOSEOUT_01.md`:1-40(Closeout書式前例)
- `user_test/middle_east_text_review_01/index.html`:1-40(簡易ページ前例)

## 事前指定Grep一覧+追記位置・更新位置の手順
- Grep `"text"|"asr_text"|ledger_phrases|segment_id` in `er026_output/family_z_production_e2e_01/melos/run_e2e_0*/{a2,b1b}/narration/attempts/*.json`(scriptで走査、Melos含有+Primary非正転写を抽出)→W5。
- Grep `ledger_phrases|get_hint_for_text` in `er006_secondary_asr_01.py`・`er006_pronunciation_ledger_01.py`→本番PLの取得方法を再現。
- `OPEN_ITEMS.md`: Grep `^- OPEN-424`→行末更新。`docs/pm/USER_DECISION_REGISTER_01.md`: Grep `^- #124`→行末追記。`DECISION_LOG.md`: 末尾追加。`docs/pm/REPORT_LEDGER.md`: Grep `FAMILY-Z-AZURE-PHRASELIST`→更新。
- `docs/pm/ACTIVE_TASK.md`先頭ヘッダ5行以内。

## 実行コマンド全文
- 抽出(委任文/Opus): `.venv\Scripts\python.exe docs\pm\tools\extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 0 --out docs\pm\delegation_log\_extract_try_0.md`(indexを増やして照合。Opusは`--tool-use-name SubagentHandback --tool-input-field message`)
- T-0 check: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-20_FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01_委任_02b.md --json-out docs\pm\delegation_log\2026-10-20_FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01_委任_02b.md_check.json`
- test(実走前Gate): `.venv\Scripts\python.exe -m pytest er084_azure_phraselist_weight_trial_01_test_01.py er084_azure_phraselist_weight_trial_01_eval_ext_test_01.py er084_azure_phraselist_weight_trial_01_judge_test_02.py -q`
- Phase A再注入: `.venv\Scripts\python.exe er084_azure_phraselist_weight_trial_01_judge.py --reinject er084_output\azure_phraselist_weight_trial_01\raw\azure_calls.jsonl --out er084_output\azure_phraselist_weight_trial_01\phase_a_reinject_v02.json`(引数名は実装に合わせ、実引数をRESULT_PACKETへ)
- 追加負例TTS: `$env:TTS_EXECUTION_MODE='STANDARD'; .venv\Scripts\python.exe er084_azure_phraselist_weight_trial_01_tts.py --design docs\research\FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01\design_matrix_01.json --only-group negatives_v02 --out er084_output\azure_phraselist_weight_trial_01\wav --budget-jpy 6 --tts-execution-mode STANDARD`(`--only-group`は実装追加、先に`--dry-run`)
- Primary: `.venv\Scripts\python.exe er084_azure_phraselist_weight_trial_01_run.py --manifest er084_output\azure_phraselist_weight_trial_01\wav\manifest_02.json --phase PRIMARY --out er084_output\azure_phraselist_weight_trial_01 --budget-jpy 5`
- Phase B dry-run→実走: `.venv\Scripts\python.exe er084_azure_phraselist_weight_trial_01_run.py --design docs\research\FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01\design_matrix_01.json --manifest er084_output\azure_phraselist_weight_trial_01\wav\manifest_01.json --manifest2 er084_output\azure_phraselist_weight_trial_01\wav\manifest_02.json --production-takes er084_output\azure_phraselist_weight_trial_01\production_takes_manifest_01.json --phase B --out er084_output\azure_phraselist_weight_trial_01 --budget-jpy 170 --dry-run` → 同コマンドから`--dry-run`を外して実走
- eval: `.venv\Scripts\python.exe er084_azure_phraselist_weight_trial_01_eval_ext.py --raw er084_output\azure_phraselist_weight_trial_01\raw\azure_calls.jsonl --primary er084_output\azure_phraselist_weight_trial_01\raw\primary_calls.jsonl --thresholds docs\research\FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01\criteria_thresholds_01.json --out docs\research\FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01\PHASE_B_RESULT_01.md`
- ページ: `curl.exe -I https://shimomura055.github.io/eigo-radio/user_test/plw_trial_01/`
- 費用: `.venv\Scripts\python.exe docs\pm\tools\daily_dev_cost_01.py --date 2026-10-20`
- secret scan: `.venv\Scripts\python.exe tools\secret_scan_01.py --staged`
- Git: `git status --porcelain`→明示add→commit→push(直近commit a21103942と同じ手順、`git log --oneline -3 origin/main`で到達確認)

## SSOT追記文
W10のとおり(実値で埋める。候補StatusはFable最終ラベル前なので「eval機械判定=<X>(Fable判定待ち)」と書く)。

## Git(明示add対象・コミットメッセージ・trailer)
- commit 1(実走前): Opus_J逐語・OPUS台帳・設計v02(3ファイル)・judge是正・golden test・Phase A再注入結果・委任文。msg: `FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01 委任_02b: Opus_J逐語保存+設計v02(M-1〜M-5/S-1〜S-8反映)+judge是正(Tier3/CS層・副作用no-op)+golden replay test+Phase A再注入(API 0)`
- commit 2: 追加負例manifest_02・Primary raw・production_takes_manifest・tts/runの拡張。msg: `… 委任_02b: 追加負例minimal pair <n>wav+本番take再利用集合<n>本(実費JPY<v>)`
- commit 3: Phase B raw/cost/eval結果・Closeout・試聴ページ(mp3含む、前例に倣う)。msg: `… 委任_02b: Phase B実走(<n>呼出、実費JPY<v>)+評価+Closeout(eval判定=<X>)+試聴ページ`
- commit 4: SSOT。msg: `… 委任_02b: SSOT(OPEN-424/DECISION_LOG/REGISTER #124/REPORT_LEDGER/OPUS台帳)`
- trailer: `Delegation: FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01/委任_02b`

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_PLW2b.md`: (1)T-0(抽出成否・文字数・sha・check) (2)Opus_J逐語(文字数・sha)と採否反映箇所 (3)golden replay結果(PASS必須)とPhase A再注入の新旧比較(特にw2.0) (4)v02の要点(負例・指標・基準・費用) (5)本番take選定結果(本数・秒・segment分布・一般化probe本数) (6)Phase B結果: 条件別Melos正認識率/本番判定flip(NG→PASS系・PASS→NG、符号検定p)/負例誤Melos・誤PASS(rule of three)/他語perturbation/2 role条件/ばらつき抜き打ち/5分類対応/候補Status (7)試聴ページURL・収載件数 (8)費用(TTS/OpenAI/Azure別、本委任実費、案件合算、当日累計) (9)Git (10)判断候補(あれば、ラベル無し。1.25/1.75の要否判断材料を含む) (11)Production採用提案時に必要な追加証拠(条件C向け) (12)一覧外Read理由。判定整合行1行。