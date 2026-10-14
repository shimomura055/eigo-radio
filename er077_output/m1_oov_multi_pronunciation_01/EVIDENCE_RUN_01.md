# EVIDENCE_RUN_01(M1 runtime evidence + STOP適用範囲規則の正式runner動作証拠、2026-10-14)

管理ID: STOP-NOTICE-SCOPE-RULE-PRODUCTION-01 委任_01(M1側: ASR-M1-OOV-MULTI-PRONUNCIATION-PRODUCTION-01)。使用モデル(最新か): primary ASR=gpt-4o-mini-transcribe、secondary=Azure Speech(phrase list)、TTS=gemini-3.8-flash-lite-tts(Aoede)。いずれも既存Production経路の現行モデルで、評価用に新しい/古いモデルを選んだものではない(本runは配線済みProduction経路の実機確認)。

## 1. 実行条件
- コマンド: `.venv\Scripts\python.exe er077_m1_oov_multi_pronunciation_01_evidence_runner.py --execute --budget-jpy 5`(正式evidence runner、1回のみ、再実行なし、rc=0)。
- 停止確認(helper): 実行前 `evidence_01/stop_check_01.json` = stop=false(STOP_ALL/自run STOPなし。旧Melos NOTICEは`d_legacy_id_match_run_limited`で非適用)。runner自身も実行中にhelperを毎clip前に呼び、`runner_execute.json`の`stop_files_present=[]`、`aborted=null`、`soft_stop=false`。
- 隔離: HR queue/attempt_history/master_audio_store/reuse_telemetry/er021 telemetry/er025 telemetry/cost logは`evidence_01/`配下。Ledgerは`evidence_01/ledger_snapshot.json`(upsert no-op、Tier3 research無効)。Ledger md5: 本番=snapshot=`7ec991722fc7f9087602504a93714d59`(run後も一致)。runnerの共有state 8ファイルのmd5 before/after一致(`shared_state_unchanged=true`)。他agentによる本番state変更はrun中に当該8ファイルでは検出されず。
- 観測数: 36(既存12-take x 2条件[segment_id=full_story_part1相当/None相当=dialogue等]=24観測 + 新規TTS 4文x3take=12観測)。
- 費用: **JPY3.3435**(ASR 2.5988 + TTS 0.7447。OpenAI ASR 42回/Azure 25回)。予算JPY5以内、hard stop 6未達。TTS失敗0。

## 2. M1発火内訳(Melos 12 take)
| 条件 | 観測 | Before(M1なし相当) | After(本run最終) | M1_MULTI_CANDIDATE_ACCEPT |
|---|---|---|---|---|
| segment_id=full_story_part1(Primary/P2/S1/S2=Tier3前の全経路) | 12 | 3/12(Secondary corroborated 3のみ) | **12/12 PASS** | 9(primary_1: 8、secondary_1: 1) |
| segment_id=None(dialogue/point_headings相当、Tier3不発) | 12 | 0/12 | **12/12 PASS** | 12(primary_1: 10、primary_2: 1、secondary_1: 1) |
- 全21件の受理は同一パターン: `C2_ledger_alt`(Ledger IPA `ˈmɛloʊs`由来、confidence=low)の`drop_final_S_or_Z`、F1 Pattern A(`Melos/z/ + said/s/`)で説明される差分のみ。ASR転写の後付け候補・綴り推定(C3)の使用0。
- `secondary_agree`: 19件=`not_provided`(Secondary未取得でPrimary段で完結)、2件=`uncertain_no_agreement`(Azureが同意せず矛盾もなし。仕様どおりSecondary同意は必須化しない)。矛盾(protected fail)による非PASS 0件。
- M1が却下した試行(`MULTI_CANDIDATE_NO_MATCH` 5回): ASRが`Mellis`/`Mella`/`Mallow`(Ledger発音候補に音素一致しない語)を出した試行。これらは後続のP2/S1で別転写がM1受理 or そのまま非M1経路。= M1は音素が合わない転写を受理しない。
- candidate_set_hash凍結: 36観測全てで記録(segment最初の試行前に1回凍結)。HR required 0、全36件が最終PASS。
- Before値: 設計時offline評価は4/12、本runのASRは非決定的で3/12。方向は同じ(Ledger由来のM1が無ければ救えない)。

## 3. 新規TTS 12観測(誤PASS抑止の確認)
| clip | 結果 |
|---|---|
| nonsib_left x3 / nonsib_ran x3 / neg_num x3 | EXACT 1、SECONDARY_ASR_CORROBORATED_MATCH 8(Azureが`Melos left.`等と正しく転写し既存Tier3 corroborationで受理)。**M1受理は0**(M1ではない既存経路。M1は非歯擦音文脈や否定・数値文で発火していない) |
| repeat x3(`Melos said Melos left.`) | 3件とも最終CONNECTED_SPEECH_ACCEPT。ただし**M1は`F1_RESIDUAL_CONTENT`で全6試行却下**(Primary「Mello said, Mello's left.」の2つ目の差分はPattern A/B/Cで説明できない)。受理はAzure secondary_1の転写「Melo said Melos left.」(2つ目が正しい)に対する既存Pattern A受理であり、M1の誤受理ではない |
- M1が非歯擦音文脈・同語反復・否定/数値を**誤って受理した件数 = 0**。(委任_02時点の期待「非PASS維持」はPrimary段について成立。最終PASSは既存の独立機構=Azure正転写に依るもので、M1は無関与。)

## 4. STOP適用範囲規則の正式runner動作証拠
- 旧runnerは`*STOP_NOTICE*`全件でexecuteを拒否していた(ASR-M1 委任_03)。helper切替後、同じ旧Melos NOTICEが存在する状態で`stop_files_present=[]`のまま有料runが完了した = 規則どおり非適用と判定。
- 同NOTICEが適用されるべきケース(対象run=run_e2e_01、Melos自身のID)ではhelperが停止判定することを`tools/stop_scope_check_01_test_01.py::test_13`で確認(21件PASS)。詳細・根拠は`STOP_SCOPE_RULE_01.md`。

## 5. 証跡ファイル(`evidence_01/`)
`stop_check_01.json`、`runner_dry-run.json`、`runner_execute.json`、`clip_results.json`(36観測、M1 audit含む)、`cost_01.json`、`ledger_snapshot.json`。telemetry(`cost_log.jsonl`、`er021_telemetry.jsonl`)・`gen/`(wav)・stdoutはローカルのみ(commit対象外)。
